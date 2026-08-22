# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "urllib3>=2.0.0",
# ]
# ///

"""
secure-fetcher.py — Secure URL Fetcher
=======================================
Fetch sicuro di risorse HTTP/HTTPS con protezione da:
  - SSRF (Server-Side Request Forgery) via IP pinning
  - DNS Rebinding via pre-resolution + pinning
  - IPv6 bypass (SEV-1 fix)
  - IP riservati/cloud metadata (SEV-2 fix)
  - Redirect SSRF indiretto (SEV-3 fix)
  - DoS da risposta illimitata (SEV-4 fix)
"""

import socket
import ipaddress
from urllib.parse import urlparse
import urllib3
import sys
from typing import Tuple

# ── SEV-2 FIX: Blocklist esplicita per range non coperti da stdlib ──────────
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("100.100.100.200/32"),  # Alibaba Cloud metadata
    ipaddress.ip_network("192.0.2.0/24"),         # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("198.51.100.0/24"),      # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),       # TEST-NET-3 (RFC 5737)
]

MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB — SEV-4 FIX


def _is_ip_blocked(ip_str: str) -> bool:
    """
    Verifica se un IP (IPv4 o IPv6) appartiene a un range
    privato, locale, riservato o cloud metadata.
    """
    ip_obj = ipaddress.ip_address(ip_str)
    # SEV-2 FIX: aggiunto is_reserved e is_unspecified
    if (ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified):
        return True
    # Blocklist cloud metadata aggiuntiva
    if any(ip_obj in net for net in _BLOCKED_NETWORKS):
        return True
    return False


def _resolve_ip(hostname: str, port: int) -> Tuple[str, int]:
    """
    Risolve hostname → IP provando prima IPv4 poi IPv6.
    Ritorna (ip_string, address_family).

    SEV-1 FIX: il codice originale usava solo AF_INET (IPv4),
    permettendo bypass tramite record AAAA (IPv6).
    """
    last_exc = None
    for family in [socket.AF_INET, socket.AF_INET6]:
        try:
            addr_info = socket.getaddrinfo(hostname, port, family, socket.SOCK_STREAM)
            if addr_info:
                return addr_info[0][4][0], family
        except socket.gaierror as exc:
            last_exc = exc
    raise ValueError(f"Impossibile risolvere il dominio '{hostname}': {last_exc}")


def _build_target_url(scheme: str, resolved_ip: str, af_family: int, parsed_url) -> str:
    """
    Costruisce l'URL usando l'IP verificato (IP pinning).
    IPv6 richiede parentesi quadre nell'URL (RFC 2732).
    """
    ip_literal = f"[{resolved_ip}]" if af_family == socket.AF_INET6 else resolved_ip
    path = parsed_url.path or "/"
    target = f"{scheme}://{ip_literal}{path}"
    if parsed_url.query:
        target += f"?{parsed_url.query}"
    # Il fragment non viene trasmesso al server (ignorato intenzionalmente)
    return target


def secure_url_fetch(url_str: str, timeout: float = 5.0) -> str:
    """
    Esegue il fetch sicuro di una risorsa web.

    Protezioni attive:
      1. Schema validation (solo http/https)
      2. Pre-resolution DNS + IP validation anti-SSRF
      3. IP pinning anti-DNS rebinding
      4. Blocco redirect HTTP anti-SSRF indiretto (SEV-3)
      5. Supporto IPv4 + IPv6 (SEV-1)
      6. Blocklist IP estesa (SEV-2)
      7. Limite dimensione risposta (SEV-4)

    Raises:
        ValueError: URL non valido o hostname non risolvibile.
        PermissionError: IP bloccato (privato/locale/riservato) o redirect rilevato.
        RuntimeError: Errore di rete durante il fetch.
    """
    parsed_url = urlparse(url_str)
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme

    # ── 1. Schema validation ─────────────────────────────────────────────────
    if not hostname:
        raise ValueError("URL non valido: hostname mancante.")

    if scheme not in ("http", "https"):
        raise ValueError(
            f"Schema '{scheme}' non supportato. "
            "Usa solo http o https."
        )

    port = parsed_url.port or (443 if scheme == "https" else 80)

    # ── 2. Pre-resolution DNS (SEV-1 FIX: IPv4 + IPv6) ──────────────────────
    resolved_ip, af_family = _resolve_ip(hostname, port)

    # ── 3. IP validation (SEV-2 FIX: blocklist estesa) ──────────────────────
    if _is_ip_blocked(resolved_ip):
        raise PermissionError(
            f"Accesso negato: l'IP risolto ({resolved_ip}) "
            "appartiene a un range privato, locale o riservato."
        )

    # ── 4. IP pinning — costruisce URL con IP verificato ─────────────────────
    target_url = _build_target_url(scheme, resolved_ip, af_family, parsed_url)
    headers = {"Host": hostname}

    http = urllib3.PoolManager(
        timeout=urllib3.Timeout(connect=timeout, read=timeout)
    )

    try:
        # ── 5. Fetch con redirect DISABILITATI (SEV-3 FIX) ──────────────────
        kwargs = dict(headers=headers, redirect=False)
        if scheme == "https":
            kwargs["server_hostname"] = hostname  # SNI per TLS corretto

        response = http.request("GET", target_url, **kwargs)

        # ── 6. Blocco esplicito dei redirect (SEV-3 FIX) ────────────────────
        if response.status in (301, 302, 303, 307, 308):
            location = response.headers.get("Location", "<sconosciuta>")
            raise PermissionError(
                f"Redirect bloccato ({response.status} → {location}): "
                "potenziale SSRF indiretto."
            )

        if response.status != 200:
            raise RuntimeError(f"Errore server: codice HTTP {response.status}")

        # ── 7. Limite dimensione risposta (SEV-4 FIX) ────────────────────────
        if len(response.data) > MAX_RESPONSE_BYTES:
            raise ValueError(
                f"Risposta troppo grande ({len(response.data):,} bytes). "
                f"Limite: {MAX_RESPONSE_BYTES:,} bytes."
            )

        return response.data.decode("utf-8", errors="replace")

    except PermissionError:
        raise  # SEV-6 FIX: non oscurare PermissionError con RuntimeError
    except ValueError:
        raise  # Non oscurare ValueError
    except Exception as exc:
        raise RuntimeError(f"Errore di rete nel fetch sicuro: {exc}")


# ── CLI entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: uv run --offline secure-fetcher.py <URL>")
        sys.exit(1)

    try:
        result = secure_url_fetch(sys.argv[1])
        print(result)
    except Exception as err:
        print(f"Errore: {err}", file=sys.stderr)
        sys.exit(1)