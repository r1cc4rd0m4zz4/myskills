# Domain Glossary & Ubiquitous Language (`CONTEXT.md`)

This document establishes the common vocabulary and domain concepts across the skills in this repository.

---

## 1. Web Search & Retrieval (`web-search`)

- **Exa MCP (`https://mcp.exa.ai/mcp`)**: Server-Sent Events (SSE) JSON-RPC endpoint providing access to Exa's search index without requiring an API key (subject to public rate limits).
- **Exa REST API (`https://api.exa.ai/search`)**: Authenticated endpoint enabling deep search modes (`deep-lite`, `deep`, `deep-reasoning`) and parallel multi-query generation.
- **`web_search_exa`**: Semantic web search returning clean snippets and highlights.
- **`web_fetch_exa`**: Web page reader returning extracted, reader-mode Markdown content stripped of HTML boilerplate, cookie notices, and navigation chrome.
- **`deep_search_exa`**: Multi-query, multi-angle search mode for complex research, syntheses, and technical investigations.
- **Token Compactor**: Parsing and filtering pipeline that extracts only canonical URLs, titles, published dates, and top highlights (<3 highlights, <200 chars each), shrinking token consumption by ~80%.
- **URL Normalization**: Canonicalization process that lowercases hostname/protocol, removes trailing slashes, drops anchor fragments, and strips tracking parameters (`utm_*`, `gclid`, `fbclid`, `ref`, `srccid`, `yclid`, etc.).

---

## 2. Source Evaluation Rubric (Tier 1–5)

- **Tier 5 (Primary / Practitioner)**: Official documentation, engineering blogs with benchmarks, source repositories (GitHub), peer-reviewed papers (arXiv).
- **Tier 4 (Specialist Media)**: High-quality domain publications (e.g., TechCrunch, Ars Technica, The Verge, Reuters).
- **Tier 3 (General Media)**: General news outlets and wire services. Useful for event timelines, but secondary for deep technical truth.
- **Tier 2 (Commentary)**: Personal blogs, subjective opinion pieces, unverified social commentary.
- **Tier 1 (Low Signal)**: SEO spam, AI-generated content farms, aggregator spam. Must be discarded immediately.

---

## 3. Web Security & Anti-SSRF (`secure-url-fetcher`)

- **SSRF (Server-Side Request Forgery)**: An attack vector where an agent or server is coerced into sending unauthorized HTTP requests to internal networks, loopback addresses (`127.0.0.1`), or cloud metadata endpoints (`169.254.169.254`).
- **DNS Rebinding**: A time-of-check to time-of-use (TOCTOU) vulnerability where an attacker's DNS server responds with a public IP on initial resolution, but quickly changes to a private IP on the subsequent socket connection.
- **Pre-Execution DNS Resolution**: Resolving domain names to exact IP addresses *prior* to opening any socket connection.
- **IP Pinning**: Forcing the network transport to connect directly to the verified, resolved IP address rather than re-resolving the hostname during the HTTP handshake.
- **SNI / Host Header Reconstruction**: Re-injecting the original hostname into the HTTP `Host` header and TLS Server Name Indication (SNI) so that virtual hosting and TLS certificate verification succeed against the pinned IP.
