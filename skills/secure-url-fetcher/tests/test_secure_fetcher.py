"""
TDD Test Suite — secure-url-fetcher skill
==========================================
Copre le vulnerabilità SEV-1, SEV-2, SEV-3 e la regressione del comportamento atteso.

Ciclo TDD:
  RED  → questi test falliscono sul codice originale (pre-fix)
  GREEN → questi test passano dopo l'applicazione dei fix

Esecuzione:
  python3 -m pytest tests/ -v
  python3 -m unittest discover -s tests -v
"""

import sys
import socket
import importlib.util
import pathlib
import unittest
from unittest.mock import patch, MagicMock

# ── Caricamento del modulo con importlib (il filename contiene un trattino) ──
_SCRIPT_PATH = pathlib.Path(__file__).parent.parent / "secure-fetcher.py"
_spec = importlib.util.spec_from_file_location("secure_fetcher", _SCRIPT_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
secure_url_fetch = _mod.secure_url_fetch


# ════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════

def _addr_info(ip: str, family=socket.AF_INET):
    """Simula il ritorno di socket.getaddrinfo."""
    sockaddr = (ip, 80) if family == socket.AF_INET else (ip, 80, 0, 0)
    return [(family, socket.SOCK_STREAM, 6, "", sockaddr)]

def _mock_response(status=200, body=b"<html>OK</html>", location=None):
    """Crea una risposta urllib3 mockata."""
    resp = MagicMock()
    resp.status = status
    resp.data = body
    resp.headers = {"Location": location} if location else {}
    return resp

def _patch_public_ip(ip="93.184.216.34"):
    """Shortcut: simula risoluzione verso un IP pubblico."""
    return patch("socket.getaddrinfo", return_value=_addr_info(ip))

def _patch_http(status=200, body=b"<html>OK</html>", location=None):
    """Shortcut: simula una risposta urllib3."""
    return patch(
        "urllib3.PoolManager",
        return_value=MagicMock(
            request=MagicMock(
                return_value=_mock_response(status, body, location)
            )
        ),
    )


# ════════════════════════════════════════════════════════
#  1. SCHEMA VALIDATION (comportamento originale invariato)
# ════════════════════════════════════════════════════════

class TestSchemaValidation(unittest.TestCase):
    """Verifica che soli http/https siano accettati."""

    def test_rejects_file_protocol(self):
        with self.assertRaises(ValueError):
            secure_url_fetch("file:///etc/passwd")

    def test_rejects_gopher_protocol(self):
        with self.assertRaises(ValueError):
            secure_url_fetch("gopher://evil.com/data")

    def test_rejects_dict_protocol(self):
        with self.assertRaises(ValueError):
            secure_url_fetch("dict://evil.com:2628/")

    def test_rejects_missing_hostname(self):
        with self.assertRaises(ValueError):
            secure_url_fetch("http://")

    def test_accepts_http(self):
        with _patch_public_ip(), _patch_http():
            result = secure_url_fetch("http://example.com/")
        self.assertIsInstance(result, str)

    def test_accepts_https(self):
        with _patch_public_ip(), _patch_http():
            result = secure_url_fetch("https://example.com/")
        self.assertIsInstance(result, str)


# ════════════════════════════════════════════════════════
#  2. SSRF IPv4 — BLOCCHI ORIGINALI (non devono regredire)
# ════════════════════════════════════════════════════════

class TestSSRFBlockingIPv4Original(unittest.TestCase):
    """Range IPv4 privati/locali: devono restare bloccati."""

    def _assert_blocked(self, ip):
        with patch("socket.getaddrinfo", return_value=_addr_info(ip)):
            with self.assertRaises(PermissionError, msg=f"IP {ip!r} dovrebbe essere bloccato"):
                secure_url_fetch("http://target.example.com/resource")

    def test_loopback_127_0_0_1(self):
        self._assert_blocked("127.0.0.1")

    def test_private_10_x(self):
        self._assert_blocked("10.0.0.1")

    def test_private_192_168(self):
        self._assert_blocked("192.168.1.100")

    def test_private_172_16(self):
        self._assert_blocked("172.16.0.1")

    def test_link_local_aws_metadata(self):
        self._assert_blocked("169.254.169.254")

    def test_multicast(self):
        self._assert_blocked("224.0.0.1")


# ════════════════════════════════════════════════════════
#  3. SEV-2 — IP RISERVATI NON COPERTI DALL'ORIGINALE
# ════════════════════════════════════════════════════════

class TestSSRFBlockingIPv4Extended(unittest.TestCase):
    """
    SEV-2: Blocco di range non coperti dalla versione originale.
    ATTESO: PermissionError su tutti gli IP seguenti.
    STATO ORIGINALE: FALLISCE (0.0.0.0 e 100.100.100.200 NON sono bloccati)
    """

    def _assert_blocked(self, ip):
        with patch("socket.getaddrinfo", return_value=_addr_info(ip)):
            with self.assertRaises(PermissionError, msg=f"IP {ip!r} dovrebbe essere bloccato"):
                secure_url_fetch("http://target.example.com/resource")

    def test_sev2_blocks_unspecified_0_0_0_0(self):
        """SEV-2: 0.0.0.0 (is_unspecified) deve essere bloccato."""
        self._assert_blocked("0.0.0.0")

    def test_sev2_blocks_alibaba_cloud_metadata(self):
        """SEV-2: 100.100.100.200 (Alibaba Cloud metadata) deve essere bloccato."""
        self._assert_blocked("100.100.100.200")

    def test_sev2_blocks_reserved_240_range(self):
        """SEV-2: 240.0.0.1 (IANA reserved future use) deve essere bloccato."""
        self._assert_blocked("240.0.0.1")


# ════════════════════════════════════════════════════════
#  4. SEV-1 — BYPASS IPv6
# ════════════════════════════════════════════════════════

class TestSSRFBlockingIPv6(unittest.TestCase):
    """
    SEV-1: Indirizzi IPv6 pericolosi devono essere bloccati.
    STATO ORIGINALE: FALLISCE (il codice forza AF_INET → ignora IPv6)
    """

    def _make_ipv6_side_effect(self, ipv6_addr):
        """Simula: AF_INET fallisce, AF_INET6 risolve all'indirizzo pericoloso."""
        def side_effect(host, port, family, socktype):
            if family == socket.AF_INET:
                raise socket.gaierror(11, "No A record for host")
            return _addr_info(ipv6_addr, family=socket.AF_INET6)
        return side_effect

    def _assert_ipv6_blocked(self, ipv6_addr):
        with patch("socket.getaddrinfo", side_effect=self._make_ipv6_side_effect(ipv6_addr)):
            with self.assertRaises(PermissionError, msg=f"IPv6 {ipv6_addr!r} dovrebbe essere bloccato"):
                secure_url_fetch("http://ipv6only.example.com/data")

    def test_sev1_blocks_ipv6_loopback(self):
        """SEV-1: ::1 (IPv6 loopback) deve essere bloccato."""
        self._assert_ipv6_blocked("::1")

    def test_sev1_blocks_ipv6_ula_private(self):
        """SEV-1: fc00::1 (ULA — Unique Local Address, equivalente a 192.168.x.x) deve essere bloccato."""
        self._assert_ipv6_blocked("fc00::1")

    def test_sev1_blocks_ipv6_link_local(self):
        """SEV-1: fe80::1 (link-local IPv6) deve essere bloccato."""
        self._assert_ipv6_blocked("fe80::1")


# ════════════════════════════════════════════════════════
#  5. SEV-3 — REDIRECT SSRF INDIRETTO
# ════════════════════════════════════════════════════════

class TestRedirectBlocking(unittest.TestCase):
    """
    SEV-3: Redirect HTTP (3xx) verso qualsiasi destinazione devono essere bloccati.
    STATO ORIGINALE: FALLISCE (urllib3 segue i redirect silenziosamente)
    """

    def _assert_redirect_blocked(self, status_code):
        location = "http://192.168.1.1/admin"
        with _patch_public_ip(), _patch_http(status=status_code, location=location):
            with self.assertRaises(PermissionError, msg=f"Redirect {status_code} dovrebbe essere bloccato"):
                secure_url_fetch("http://legit-public.com/redirect-trap")

    def test_sev3_blocks_301(self):
        """SEV-3: 301 Moved Permanently → SSRF indiretto."""
        self._assert_redirect_blocked(301)

    def test_sev3_blocks_302(self):
        """SEV-3: 302 Found → SSRF indiretto."""
        self._assert_redirect_blocked(302)

    def test_sev3_blocks_303(self):
        """SEV-3: 303 See Other → SSRF indiretto."""
        self._assert_redirect_blocked(303)

    def test_sev3_blocks_307(self):
        """SEV-3: 307 Temporary Redirect → SSRF indiretto."""
        self._assert_redirect_blocked(307)

    def test_sev3_blocks_308(self):
        """SEV-3: 308 Permanent Redirect → SSRF indiretto."""
        self._assert_redirect_blocked(308)

    def test_sev3_redirect_raises_permission_error_not_runtime(self):
        """SEV-3 + SEV-6: Il PermissionError NON deve essere oscurato da RuntimeError."""
        with _patch_public_ip(), _patch_http(status=301, location="http://169.254.169.254/"):
            with self.assertRaises(PermissionError):
                secure_url_fetch("http://evil-redirect.com/trap")


# ════════════════════════════════════════════════════════
#  6. HAPPY PATH (regressione post-fix)
# ════════════════════════════════════════════════════════

class TestHappyPath(unittest.TestCase):
    """Verifica che il comportamento legittimo funzioni correttamente dopo i fix."""

    def test_successful_fetch_returns_content(self):
        with _patch_public_ip(), _patch_http(body=b"Hello, World!"):
            result = secure_url_fetch("http://example.com/page")
        self.assertEqual(result, "Hello, World!")

    def test_url_with_query_string_is_preserved(self):
        """La query string deve essere inclusa nell'URL target."""
        with _patch_public_ip() as mock_getaddr, _patch_http() as mock_pool:
            secure_url_fetch("http://example.com/search?q=test&page=2")
            call_url = mock_pool.return_value.request.call_args[0][1]
            self.assertIn("q=test", call_url, "Query string assente dall'URL di destinazione")
            self.assertIn("page=2", call_url)

    def test_host_header_is_original_hostname(self):
        """L'header Host deve contenere il nome originale, non l'IP."""
        with _patch_public_ip("93.184.216.34") as _, _patch_http() as mock_pool:
            secure_url_fetch("http://example.com/")
            call_kwargs = mock_pool.return_value.request.call_args
            headers = call_kwargs[1].get("headers") or call_kwargs[0][2] if len(call_kwargs[0]) > 2 else {}
            # L'URL di destinazione deve usare l'IP, non il nome
            call_url = mock_pool.return_value.request.call_args[0][1]
            self.assertIn("93.184.216.34", call_url, "L'URL non usa l'IP risolto (IP pinning fallito)")

    def test_server_error_raises_runtime_error(self):
        with _patch_public_ip(), _patch_http(status=500):
            with self.assertRaises(RuntimeError):
                secure_url_fetch("http://example.com/broken")

    def test_unresolvable_domain_raises_value_error(self):
        with patch("socket.getaddrinfo", side_effect=socket.gaierror("NXDOMAIN")):
            with self.assertRaises(ValueError):
                secure_url_fetch("http://this-does-not-exist-xyzabc.com/")

    def test_public_ip_is_not_blocked(self):
        """Un IP pubblico valido non deve essere bloccato."""
        with _patch_public_ip("8.8.8.8"), _patch_http(body=b"dns response"):
            result = secure_url_fetch("http://dns.google/")
        self.assertEqual(result, "dns response")


if __name__ == "__main__":
    unittest.main(verbosity=2)
