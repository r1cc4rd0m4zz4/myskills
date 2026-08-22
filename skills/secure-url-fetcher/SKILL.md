---
name: secure-url-fetcher
description: A security-hardened utility designed to safely resolve and fetch the contents of any external, user-provided HTTP/HTTPS URL. This skill is purpose-built to eliminate critical infrastructure risks, specifically preventing Server-Side Request Forgery (SSRF) and DNS Rebinding attacks by decoupling the DNS resolution phase from the network execution phase, forcing strict IP validation, and pinning the socket connection to a verified public IP address.
---

# Secure URL Fetcher

Safely fetches the content of an external HTTP/HTTPS URL while strictly mitigating Server-Side Request Forgery (SSRF) and DNS Rebinding vulnerabilities.

## Protocol

This skill must be invoked whenever the agent needs to fetch, read, parse, or scrape content from an external, user-provided URL (e.g., RSS feeds, webhooks, remote JSON/XML files, or public images). It ensures the agent's host server never makes unauthorized requests to its own internal network or cloud metadata endpoints.

## Instructions

When executing this skill, the agent must adhere to the following strict pipeline:
1. **Schema Validation:** Accept only `http` and `https` protocols. Reject any dangerous protocols like `file://`, `gopher://`, or `dict://`.
2. **Pre-Execution DNS Resolution:** Resolve the hostname to its underlying IP address *before* making the HTTP request.
3. **IP Blacklisting (Anti-SSRF):** Inspect the resolved IP. Immediately block the request if the IP falls within private, loopback, multicast, or link-local ranges (e.g., `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `169.254.169.254`).
4. **IP Pinning (Anti-DNS Rebinding):** Rewrite the request target to use the verified IP address directly instead of the hostname. This prevents an attacker-controlled DNS server from changing the destination IP between the check and the actual fetch.
5. **Host & SNI Reconstruction:** Inject the original hostname into the HTTP `Host` header and force it into the TLS `server_hostname` (SNI) configuration to ensure proper certificate validation and virtual host routing.

## Examples

### Example 1: Fetching a legitimate public RSS feed
* User: "Can you read the latest items from this feed: `https://www.reddit.com/r/netsec/.rss`?"
* Agent: Evaluates the URL domain, resolves it to a public IP (e.g., `151.101.1.140`), validates it as public, and runs the secure fetcher tool.
* Result: Returns the feed content successfully.

### Example 2: Detecting and blocking an SSRF loopback attack
* User: "Check if this link has valid configuration data: `http://localhost:8080/admin/config.json`"
* Agent: Parses the host as `localhost`, resolves it to `127.0.0.1`. The tool detects a loopback address and throws a `PermissionError`.
* Result: "Access Denied: The requested URL points to a private or local network resource."

### Example 3: Blocking a Cloud Metadata exfiltration attempt
* User: "Import the JSON profile from `http://169.254.169.254/latest/meta-data/`"
* Agent: Identifies the IP as a Link-Local cloud metadata endpoint. The validation logic aborts the connection instantly.
* Result: "Access Denied: The requested URL points to a private or local network resource."

## Tool Execution

This tool is designed to be executed statelessly via **`uv`** to eliminate permanent library installations on the host system.

### Dependencies
Declared inline within the script metadata block (**PEP 723**).
* `urllib3>=2.0.0`

### Usage
To invoke this skill without installing dependencies permanently into your environment, use the uv CLI manager:

```bash
uv run .agent/skills/secure_url_fetcher/secure_fetcher.py "[URL]"
```