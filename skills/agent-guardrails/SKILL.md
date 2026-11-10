---
name: agent-guardrails
description: Enforces production-grade defensive engineering guardrails, anti-bloat ladder, code-is-law zero trust, and strict privacy/sanitization across all agent coding tasks.
---

# Agent Guardrails

Production-grade engineering guardrails, zero-bloat architecture, and defensive security protocols for AI coding agents.

## Core Protocol

When executing coding, refactoring, architecture, or shell tasks, strictly enforce the following rules:

### 1. Code Is Law (Zero Trust)

* Never rely on documentation, comments, or claimed intent. Audit verbatim implementation code, permissions, and blast radius directly—never trust opaque AI output. Zero black-box diffs: if you cannot explain every line at the runtime layer, delete it.
* Inspect callers before patching functions. Fix root causes at shared junctions rather than patching symptoms across callers.

### 2. The Ladder (Anti-Bloat & Minimalist Engineering)

Solve the problem with the least new code. Stop at the first rung that satisfies the requirement:

1. **Does it need to exist?** Reject unrequested options, speculative configuration, and flexibility.
2. **Already in codebase:** Reuse existing helpers, components, and conventions before writing new code.
3. **Native & stdlib first:** OS primitives, runtime built-ins, and standard libraries before any custom code. Never trade 1 native command (`pmset`, `systemd-inhibit`) for daemons, Accessibility hooks, or `sudoers NOPASSWD` hacks. Probe flags and APIs against the live target (`--help`, `man`) before use—never assume phantom options exist.
4. **Dependencies policy:** Strictly lockfile-only. **NEVER** add an external dependency without explicit pushback and user approval.
5. **Shortest working diff:** No speculative abstractions, wrappers, or "for later" code. Deletion beats addition.

### 3. Pushback Policy

Direct minimal execution by default. Mandatory proactive pushback before acting ONLY when a request introduces new external dependencies or an architecture grossly oversized relative to platform standards.

### 4. Devil's Advocate Grilling

In any interview, planning, or grilling phase (via `/grill-me`, `/grill-with-docs`, `grilling`, plan, /plan or custom skills), every question round MUST include an explicit Devil's Advocate counter-option. Challenge the proposed design against minimal-code alternatives (The Ladder, Level 1–5), exposing speculative assumptions, blast-radius risks, and cognitive blind spots before accepting any decision.

### 5. Git Workflow & Safety

* **NEVER push autonomously.** Wait for explicit user authorization ("push", "fai il push", "pusha").
* Before editing in any repo, read its own `AGENTS.md`/`CONTRIBUTING.md`.
* Before proposing any commit or push, run `git fetch` + `git status -sb`, report the exact divergence, and run the repo's verification gate.
* Keep commits focused, production-grade, and strictly free of personal paths or jargon.

### 6. Verification of Compact Code & Verification Gate

* Compact code without checks is unverified debt. Non-trivial logic (branches, parsers, security flows) must include a minimal assertion or unit test covering negative branches.
* Run the repo's verification suite (`./scripts/verify.sh`) before any commit.

### 7. Defensive Scripting & Shell Safety

* Whitelist inputs with strict regex (`^[0-9]+$`).
* Always attach atomic `trap` cleanup on `INT TERM EXIT` for temporary resources.
* Shell scripts must work both locally (`BASH_SOURCE[0]`) and via pipe (`curl | bash`).
* No security theater: run tools matching the actual stack; no PoC on a reachable path = no bug (reject speculative patches for static noise).

### 8. Absolute Privacy & Sanitization

* Zero personal paths (`/Users/...`, `/home/...`), usernames, or host machine details in code, commits, or documentation.
* Use generic placeholders (`<project_dir>`, `https://example.com`).
* **Grill-Me Protocol:** On any ambiguity regarding private data, credentials, or sensitive host configs, stop and interrogate the user for clarification.

### 9. Zero-Cost CI & Workflows (Code Is Law)

Workflows must never incur billing or drain account quotas. Always use standard Linux (`runs-on: ubuntu-latest`); strictly ban `macos-latest`, `windows-latest` (10x/2x billing meters), and Larger Runners. Enforce `timeout-minutes: 10`, `concurrency` cancellation, `retention-days: 1`, and an account spending limit of $0.00.

---

## Discovery & Configuration Paths

Different AI agent harnesses discover rules from distinct filesystem locations. Ensure guardrails are deployed to the correct path:

### 1. Antigravity CLI (`agy`)
* **Hierarchical (Local):** Scans upwards from the current working directory (`$CWD`) to the root of the Git repository (`.git/`) for `AGENTS.md`.
* **Global (User-Wide):** Scans exclusively in `~/.gemini/config/AGENTS.md` (or `~/.gemini/AGENTS.md`).
* **Warning:** Antigravity CLI does **not** scan `~/.agents/AGENTS.md`. Placing rules solely in `~/.agents/` will cause `agy` to ignore them entirely.

### 2. Generic Agents (Pi, OpenCode, Claude Code, Cursor, Codex, Windsurf)
* **Local:** Reads `./AGENTS.md` located in the repository root.
* **Global:** Reads `~/.agents/AGENTS.md`.

### 3. Dual-Environment Symlink Setup
To maintain a single source of truth across both Antigravity CLI and generic agents, establish `~/.gemini/config/AGENTS.md` as canonical and symlink `~/.agents/AGENTS.md` to it:

```bash
mkdir -p ~/.gemini/config ~/.agents
ln -sf ~/.gemini/config/AGENTS.md ~/.agents/AGENTS.md
```

Or deploy automatically via the dual-mode installer:

```bash
# Via pipe:
curl -fsSL https://raw.githubusercontent.com/r1cc4rd0m4zz4/myskills/main/scripts/install-guardrails.sh | bash -s -- --symlink

# Or locally:
./scripts/install-guardrails.sh --symlink
```
