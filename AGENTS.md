# Global Guardrails: Code Is Law (Zero-Bloat Mode)

- **Code Is Law (Zero Trust):** Code is law, not promises or reputation. Audit actual implementation, privileges, and blast radius directly from verbatim source—never trust documentation, claimed intent, or opaque AI output. Zero black-box diffs: if you cannot explain every line at the runtime layer, delete it.
- **Git Workflow:** NEVER push autonomously. Wait for the explicit order ("push", "fai il push", "pusha"). Before editing in a repo, read its own `AGENTS.md`/`CONTRIBUTING.md`. Before proposing any commit or push, run `git fetch` + `git status -sb`, report the exact divergence, and run the repo's verification gate.
- **Notes & Runbooks:** ONLY save personal notes and guides outside the repository in local private storage. Keep repos strictly clean.
- **The Ladder (Anti-Bloat & Minimalist Engineering):** Solve the problem with the least new code.
  1. *Does it need to exist?* Reject unrequested options, speculative configuration, and flexibility.
  2. *Already in codebase:* Reuse existing helpers, components, and conventions before writing new code.
  3. *Native & stdlib first:* OS primitives, runtime built-ins, and standard libraries before any custom code. Never trade 1 native command (`pmset`, `systemd-inhibit`) for daemons, Accessibility hooks, or `sudoers NOPASSWD` hacks. Probe flags and APIs against the live target (`--help`, `man`) before use—never assume phantom options exist.
  4. *Dependencies policy:* Strictly lockfile-only. **NEVER** add an external dependency without explicit pushback and user approval.
  5. *Shortest working diff:* No speculative abstractions, wrappers, or "for later" code. Deletion beats addition.
- **Pushback Policy:** Direct minimal execution by default. Mandatory proactive pushback before acting ONLY when a request introduces new external dependencies or an architecture grossly oversized relative to platform standards.
- **Verification of Compact Code:** Compact code without checks is unverified debt. Non-trivial logic (branches, parsers, security flows) must include a minimal assertion or unit test covering negative branches.
- **Defensive Scripting:** Whitelist inputs with strict regex (`^[0-9]+$`). Always atomic `trap` cleanup on `INT TERM EXIT`. No security theater: run tools matching the actual stack (ShellCheck + Gitleaks for shell; zero SCA on zero-dependency code); no PoC on a reachable path = no bug (reject speculative patches for static noise).
- **Dual-Mode Installers:** Installers must work both locally from any folder (`BASH_SOURCE[0]`) and remotely via pipe (`curl | bash`). Never assume a repo is public.
- **Verification & CI:** Test negative branches and edge cases first. Local pass != remote verification. Non-trivial logic must leave runnable checks.
- **Sanitization:** Zero personal paths (`/Users/...`, `/home/...`), usernames, machine configurations, or chat jargon in commits, code, or docs. Strictly production-grade.

---

## Agent Guidelines (`AGENTS.md`)

This repository hosts a curated collection of agent-agnostic skills. Any autonomous AI agent contributing to or executing from this repository must adhere to the conventions outlined below.

---

## 1. Principles

1. **Harness-Agnostic Design**: Never build skills tied to a specific proprietary agent framework. Skills must adhere to the open Agent Skills standard (`SKILL.md` with standard YAML frontmatter) and execute on any host runtime (Pi, Claude Code, Cursor, Codex, OpenCode, Windsurf).
2. **Zero Ambient Assumptions**: Rely exclusively on standard runtime environments:
   - **Node.js (ESM `.mjs`)**: For HTTP, JSON-RPC, stream parsing, and cross-platform I/O. Use Node 18+ native `fetch` and standard globals. Zero required `node_modules` or `npm install` steps for skill scripts.
   - **Python (PEP 723)**: If Python is required, declare dependencies inline via PEP 723 metadata blocks and run via `uv run`. Exact dependency pinning (`==`) is required.
3. **Strict Token Economy (Anti-Bloat Rule)**: LLM context windows are finite. Raw API, HTML, or JSON dumping is prohibited. Skills must filter, prune, deduplicate, and compact outputs (~50–100 tokens per record, ~80% reduction vs raw payloads).
4. **Absolute Privacy & Zero Data Exfiltration**:
   - **Zero PII / Host Leaks**: Never hardcode, commit, or log non-public personal information, local OS usernames, user home directories, internal IP addresses/hostnames, credentials, or machine configuration details.
   - **Generic Placeholders Only**: All examples, tests, scripts, and documentation MUST use generic placeholders (`<skill_dir>`, `~/.agents/skills`, `https://example.com`, `sk-...`).
   - **Grill-Me on Ambiguity**: If there is the slightest doubt about whether a detail, path, identifier, or value constitutes personal, confidential, or internal host configuration information, **NEVER assume or proceed silently**. Interrogate and grill the maintainer directly for explicit clarification.
5. **Security by Default**:
   - URL inputs must undergo SSRF validation and DNS pinning before fetching (`secure-url-fetcher`).
   - Query inputs must use safe JSON serialization (`JSON.stringify` / `json.dumps`), avoiding shell string interpolations.
   - Tracking parameters (`utm_*`, `gclid`, `fbclid`, `ref`, etc.) must be stripped during URL normalization.

---

## 2. Skill Directory Structure

Every skill lives inside a flat directory under `skills/<skill-name>/`:

```text
skills/<skill-name>/
├── SKILL.md                 # Primary definition and model instructions
├── <tool_runner>.mjs        # Standalone executable tool runner (zero-dependency ESM)
└── references/              # Optional detailed schemas, quality rubrics, or docs
    └── *.md
```

---

## 3. `SKILL.md` Specification

Every `SKILL.md` must start with valid YAML frontmatter:

```markdown
---
name: skill-name
description: Clear, action-oriented description of what this skill does and when an agent should invoke it.
---

# Skill Title

Overview and primary capabilities.

## Tools & Execution

Direct CLI invocation patterns.

## Protocol & Decision Matrix

When to use which mode or tool.

## Context & Token Optimization

Compaction guarantees and formatting rules.
```

---

## 4. Verification & Testing Gate

Before committing any change to this repository:

1. **Privacy & PII Audit**: Scan diffs for any accidental leaks of local paths, usernames, machine configurations, or confidential tokens (`./scripts/verify.sh`).
2. **Self-Check**: Run the skill's tool runner directly from the terminal with a real or mocked invocation.
3. **Automated Tests**: All tests must pass with 100% success rate.
4. **No Unused Scaffolding**: Keep diffs minimal and delete dead code immediately.
