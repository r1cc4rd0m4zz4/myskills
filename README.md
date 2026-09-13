# myskills ⚡

```text
                     _     _ _ _     
 _ __ ___  _   _ ___| | __(_) | |___ 
| '_ ` _ \| | | / __| |/ /| | | / __|
| | | | | | |_| \__ \   < | | | \__ \
|_| |_| |_|\__, |___/_|\_\|_|_|_|___/
           |___/                     
```

> Curated, production-grade, zero-bloat AI agent skills with deterministic token economy and zero ambient dependencies.

[![skills.sh](https://skills.sh/b/r1cc4rd0m4zz4/myskills)](https://skills.sh/r1cc4rd0m4zz4/myskills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node Dependencies: 0](https://img.shields.io/badge/Node%20Dependencies-0-brightgreen.svg)](#security--quality-gates)
[![Token Compaction: ~80%](https://img.shields.io/badge/Token%20Compaction-~80%25-blueviolet.svg)](#why-myskills)
[![Harness: Universal](https://img.shields.io/badge/Harness-Universal-orange.svg)](#universal-installation)
[![Security: Anti--SSRF](https://img.shields.io/badge/Security-Anti--SSRF%20Pinning-red.svg)](#security--quality-gates)

`myskills` is a transparent, lightweight suite of harness-agnostic agent tools built for real software engineering. It prioritizes strict token economy, native runtime features, and defense-in-depth security without framework bloat, background daemons, or unpinned dependencies.

---

## Why myskills?

Many agent skill toolkits and MCP wrappers introduce:

* ⚠️ **Massive token exhaustion:** dumping raw HTML, full DOM trees, and unpruned JSON payloads directly into finite context windows.
* ⚠️ **Dependency creep:** requiring hundreds of `node_modules` packages, transpile steps, or brittle ambient environments.
* ⚠️ **Critical security blindspots:** exposing local machines and cloud metadata endpoints (`169.254.169.254`) to SSRF and DNS rebinding attacks.
* ⚠️ **Vendor lock-in:** coupling tool definitions to proprietary agent frameworks.

`myskills` takes the native, zero-bloat approach:

* ✅ **Deterministic Token Compaction:** ~80% context reduction through aggressive highlight extraction, metadata pruning, and cross-result deduplication.
* ✅ **Zero Ambient Assumptions:** Node.js tools run as zero-dependency standalone ESM (`.mjs`); Python tools declare exact pinned versions via inline PEP 723 metadata.
* ✅ **Anti-SSRF & DNS Rebinding Immunity:** Pre-execution DNS dual-stack resolution, private IP blacklisting, and direct socket IP pinning.
* ✅ **Universal Compatibility:** Conforms strictly to the open Agent Skills standard (`skills.sh`), working seamlessly across Pi Coding Agent, Claude Code, Cursor, Codex, OpenCode, and Windsurf.
* ✅ **Absolute Privacy:** Zero host leaks, zero PII, and zero machine details in commits, documentation, or tool outputs.

---

## The Philosophy

1. **The Ladder of Restraint (Anti-Bloat Engineering):**  
   If native platform features or runtime standard libraries can solve the problem, writing boilerplate wrappers or installing dependencies is technical debt. One line before fifty.
2. **Code You Know, Not Code You Trust (Digital Sovereignty):**  
   Security is not blind trust in an opaque library or remote service. It is clean, auditable code that an engineer can read and verify in two minutes.
3. **Finite Context Window Ethics:**  
   LLM context tokens are expensive and finite. Feeding raw web garbage to an agent degrades its reasoning. Every byte returned to an agent must earn its place.

---

## Skills Catalog

| Skill | Description | Runtime | Security & Optimization |
| :--- | :--- | :--- | :--- |
| [`agent-guardrails`](skills/agent-guardrails/SKILL.md) | Universal defensive engineering guardrails: anti-bloat ladder, zero trust code auditing, and strict sanitization. | Universal Markdown | Prevents autonomous pushes, enforces input whitelisting, and bans PII/host leaks. |
| [`web-search`](skills/web-search/SKILL.md) | High-signal web search, page extraction, and deep reasoning via Exa with ~80% token compaction and tracking deduplication. | Node.js 18+ (ESM, 0 deps) | Tracking parameter stripping (`utm_*`, `gclid`), URL normalization, multi-block parsing. |
| [`secure-url-fetcher`](skills/secure-url-fetcher/SKILL.md) | Security-hardened HTTP/HTTPS fetcher with pre-resolution IP blacklisting and socket pinning. | Python (`uv`, `urllib3==2.2.3`) | Eliminates SSRF, DNS Rebinding, IPv6 bypass, and indirect HTTP redirect attacks. |

---

## Universal Installation

### Option 1: Interactive Agent Installer (`skills.sh`)

Install the full suite or individual skills into any agent environment using `npx`, `pnpx`, or `bunx`:

```bash
# Install the full suite
npx skills add r1cc4rd0m4zz4/myskills

# Or install individual skills directly
npx skills add r1cc4rd0m4zz4/myskills/skills/agent-guardrails
npx skills add r1cc4rd0m4zz4/myskills/skills/web-search
npx skills add r1cc4rd0m4zz4/myskills/skills/secure-url-fetcher
```

### Option 2: Pi Coding Agent

Install directly via Pi's package manager:

```bash
pi install git:github.com/r1cc4rd0m4zz4/myskills
```

### Option 3: Universal `AGENTS.md` (Project or Global)

Download the universal guardrails directly into any project or your agent's global profile:

```bash
# Into any local project root:
curl -fsSL https://raw.githubusercontent.com/r1cc4rd0m4zz4/myskills/main/templates/AGENTS.md -o AGENTS.md

# Or into Pi Coding Agent global config:
curl -fsSL https://raw.githubusercontent.com/r1cc4rd0m4zz4/myskills/main/templates/AGENTS.md -o ~/.pi/agent/AGENTS.md
```

### Option 4: Local Clone for Development

Clone the repository and symlink skills into your agent directory (`~/.agents/skills/`):

```bash
git clone https://github.com/r1cc4rd0m4zz4/myskills.git
cd myskills
./scripts/link-skills.sh
```

---

## Usage Examples

### 1. Web Search & Page Fetching

```bash
# Fast semantic search with tracking removal & deduplication
node skills/web-search/exa_tool.mjs search "Node.js 22 LTS features" 5

# Reader-mode extraction (HTML & cookie banners stripped)
node skills/web-search/exa_tool.mjs fetch "https://example.com/article" 3000

# Multi-angle deep research
node skills/web-search/exa_tool.mjs deep "WebAssembly 2026" 10 deep "Wasm GC;Wasm edge"
```

### 2. Secure URL Fetching (Anti-SSRF)

```bash
# Safely fetch an external feed (DNS resolved & IP pinned)
uv run skills/secure-url-fetcher/secure-fetcher.py "https://example.com/feed.xml"

# Malicious localhost or cloud metadata attempts are aborted instantly
uv run skills/secure-url-fetcher/secure-fetcher.py "http://169.254.169.254/latest/meta-data/"
# -> PermissionError: Access Denied (Private / Local IP range)
```

---

## Scope & Non-Goals

To maintain zero-bloat integrity and maximum reliability:

* ❌ **No Heavy Frameworks:** No LangChain, LlamaIndex, or multi-megabyte SDK abstractions.
* ❌ **No Resident Daemons:** Tools execute statelessly, return compacted structured outputs, and exit immediately.
* ❌ **No Telemetry or Tracking:** Zero user profiling, zero external logging, zero ambient network calls.

---

## Security & Quality Gates

Every change in this repository must satisfy strict defensive verification:

* **Zero Ambient Dependencies:** Node tools require zero npm packages; Python dependencies are exact-pinned.
* **Privacy & PII Audit:** Automated scan on every run to prevent local paths (`/Users/...`, `/home/...`) or secrets from entering code or docs.
* **Deterministic Test Suite:** Complete offline test suite executing in under 10ms:

```bash
./scripts/verify.sh
```

* 8/8 tests passing for `web-search` (URL normalization, tracking removal, compaction).
* 30/30 tests passing for `secure-url-fetcher` (SSRF, IPv6 link-local, cloud metadata, redirects).

---

## Contributors & Authors

[![r1cc4rd0m4zz4](https://github.com/r1cc4rd0m4zz4.png)](https://github.com/r1cc4rd0m4zz4)

* **r1cc4rd0m4zz4** ([@r1cc4rd0m4zz4](https://github.com/r1cc4rd0m4zz4))  
  *Cybersecurity Specialist & Anti-Bloat Architect.*

See also [CONTRIBUTORS.md](CONTRIBUTORS.md) for contribution guidelines.

---

## License

[MIT](LICENSE) © Riccardo Mazza
