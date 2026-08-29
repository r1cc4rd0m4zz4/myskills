---
name: secure-url-fetcher
description: Security-hardened HTTP/HTTPS fetcher with pre-resolution IP blacklisting and socket pinning to eliminate SSRF and DNS rebinding.
---

# Secure URL Fetcher

Safely fetch external web resources while blocking Server-Side Request Forgery (SSRF) and DNS Rebinding.

## Protocol

Invoke whenever fetching user-provided or external URLs (RSS, JSON APIs, remote files, webhooks) to ensure requests cannot target private networks, localhost, or cloud metadata endpoints.

## Execution

```bash
uv run <skill_dir>/secure-fetcher.py "<URL>"
```

## Security Pipeline

1. **Schema Check**: Strictly permits `http://` and `https://`. Rejects `file://`, `gopher://`, `dict://`.
2. **Pre-Resolution DNS**: Resolves hostname to IPv4/IPv6 address prior to opening connection.
3. **Anti-SSRF IP Validation**: Blocks private, loopback, link-local, multicast, reserved ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, `::1`, `fe80::/10`, `fc00::/7`, Alibaba metadata `100.100.100.200`).
4. **Socket Pinning**: Connects directly to verified IP literal with original `Host` header and TLS SNI.
5. **Redirect Defense**: Prohibits HTTP redirects (301/302/307/308) to prevent indirect SSRF escalation.
6. **Payload Guard**: Enforces strict maximum response limit (5 MB) against denial-of-service.
