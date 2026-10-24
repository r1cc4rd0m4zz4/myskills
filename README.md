# myskills

```text
                     _     _ _ _     
 _ __ ___  _   _ ___| | __(_) | |___ 
| '_ ` _ \| | | / __| |/ /| | | / __|
| | | | | | |_| \__ \   < | | | \__ \
|_| |_| |_|\__, |___/_|\_\|_|_|_|___/
           |___/                     
```

> Zero-dependency, auditable skills for AI coding agents (Antigravity, OpenCode, Pi, Claude Code, Cursor, Codex).

[![skills.sh](https://skills.sh/b/r1cc4rd0m4zz4/myskills)](https://skills.sh/r1cc4rd0m4zz4/myskills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node Dependencies: 0](https://img.shields.io/badge/Node%20deps-0-brightgreen.svg)](#)

---

## Skills

| Skill | What it does | Runtime | Quick Run |
|---|---|---|---|
| [`agent-guardrails`](skills/agent-guardrails/SKILL.md) | Anti-bloat ladder, zero-trust auditing, no autonomous push | Universal Markdown | Copy template to `AGENTS.md` |
| [`web-search`](skills/web-search/SKILL.md) | Web search & page extraction via Exa, stripped of tracking params | Node 18+ (0 deps) | `node skills/web-search/exa_tool.mjs search "<query>"` |
| [`secure-url-fetcher`](skills/secure-url-fetcher/SKILL.md) | HTTP fetcher with pre-resolution DNS pinning (blocks SSRF & metadata) | Python (`uv`, `urllib3==2.8.0`) | `uv run skills/secure-url-fetcher/secure-fetcher.py "<url>"` |
| [`pdf-security-scanner`](skills/pdf-security-scanner/SKILL.md) | Static PDF malware audit, in-memory CMap text preview & XREF-safe CDR | Python 3.8+ (0 deps) | `uv run skills/pdf-security-scanner/pdf_scanner.py scan "<path>"` |

---

## Quick Start

Install into your agent environment via [skills.sh](https://skills.sh):

```bash
# Install full suite (Antigravity, OpenCode, Claude Code, Cursor, Codex)
npx skills add r1cc4rd0m4zz4/myskills

# Or install in Pi Coding Agent
pi install git:github.com/r1cc4rd0m4zz4/myskills

# Or grab just the universal AGENTS.md guardrails
curl -fsSL https://raw.githubusercontent.com/r1cc4rd0m4zz4/myskills/main/templates/AGENTS.md -o AGENTS.md
```

---

## CLI Examples

```bash
# 1. Search without tracker bloat
node skills/web-search/exa_tool.mjs search "Node.js 22 LTS features" 5

# 2. Extract clean article markdown (cookie banners & HTML stripped)
node skills/web-search/exa_tool.mjs fetch "https://example.com/article" 3000

# 3. Secure fetch with anti-SSRF & DNS pinning
uv run skills/secure-url-fetcher/secure-fetcher.py "https://example.com/feed.xml"

# Malicious attempts to probe cloud metadata or internal subnets fail immediately:
uv run skills/secure-url-fetcher/secure-fetcher.py "http://169.254.169.254/latest/meta-data/"
# -> PermissionError: Access Denied (Private / Local IP range)

# 4. Static PDF malware audit, in-memory text preview, or XREF-preserving disarm
uv run skills/pdf-security-scanner/pdf_scanner.py scan "path/to/document.pdf"
```

---

## Verification

Offline test suite with zero network dependencies:

```bash
./scripts/verify.sh
```

- **Privacy audit:** Scans diffs for local user paths (`/Users/...`, `/home/...`) or secrets.
- **Node.js suite:** 9 tests for tracking parameter stripping and compaction.
- **Python suite:** 41 tests for SSRF, DNS rebinding, IPv6 link-local, redirect attacks, and static PDF malware/CDR analysis.

---

## License

[MIT](LICENSE) © Riccardo Mazza
