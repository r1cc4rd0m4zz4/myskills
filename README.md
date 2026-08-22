# Curated Agent Skills

[![skills.sh](https://skills.sh/b/r1cc4rd0m4zz4/myskills)](https://skills.sh/r1cc4rd0m4zz4/myskills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A curated collection of production-grade, harness-agnostic AI agent skills. Built for real engineering workflows with a strict focus on **security**, **token economy**, and **universal compatibility** across all AI coding assistants (Pi, Claude Code, Cursor, Codex, OpenCode, Windsurf, and custom harnesses).

---

## Skills Catalog

| Skill | Description | Runtime | Prerequisites |
| :--- | :--- | :--- | :--- |
| [`web-search`](skills/web-search/SKILL.md) | High-signal web search, page extraction, and deep reasoning via Exa with ~80% token compaction and automatic tracking deduplication. | Node.js 18+ (ESM) | None (`EXA_API_KEY` optional for Deep API) |
| [`secure-url-fetcher`](skills/secure-url-fetcher/SKILL.md) | Security-hardened HTTP/HTTPS fetcher with pre-resolution IP blacklisting and socket pinning to eliminate SSRF and DNS rebinding risks. | Python (`uv`) | [`uv`](https://docs.astral.sh/uv/) |

---

## Universal Installation

### Option 1: Interactive Agent Installer (`npx skills`)
Install any skill into any configured agent environment using the open [skills.sh](https://skills.sh) standard:

```bash
npx skills add r1cc4rd0m4zz4/myskills
```

### Option 2: Pi Coding Agent
Install directly via Pi's native package manager:

```bash
pi install git:github.com/r1cc4rd0m4zz4/myskills
```

### Option 3: Local Symlink for Development
Clone the repository and link all skills into your local agent directories (`~/.agents/skills/`):

```bash
git clone https://github.com/r1cc4rd0m4zz4/myskills.git myskills
cd myskills
./scripts/link-skills.sh
```

---

## Design Principles

1. **Zero Vendor Lock-In**: Compliant with the open Agent Skills standard. Every skill is defined in a standard `SKILL.md` with YAML frontmatter.
2. **Deterministic Token Economy**: Raw JSON/HTML payloads are pruned and compressed before reaching the LLM context window.
3. **Defense in Depth**: Zero unvalidated string interpolation in shell calls; strictly validated network I/O with IP pinning.
4. **Self-Contained Execution**: No bloat. Node tools run as zero-dependency standalone `.mjs` modules; Python tools use inline PEP 723 metadata with `uv`.

---

## Contributing

See [`AGENTS.md`](AGENTS.md) for architectural guidelines, test requirements, and contribution rules.
See [`CONTEXT.md`](CONTEXT.md) for domain terminology and source quality scoring standards.

---

## License

[MIT](LICENSE) © Riccardo Mazza
