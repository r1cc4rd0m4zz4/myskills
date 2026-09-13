---
name: agent-guardrails
description: Enforces production-grade defensive engineering guardrails, anti-bloat ladder, code-is-law zero trust, and strict privacy/sanitization across all agent coding tasks.
---

# Agent Guardrails

Production-grade engineering guardrails, zero-bloat architecture, and defensive security protocols for AI coding agents.

## Core Protocol

When executing coding, refactoring, architecture, or shell tasks, strictly enforce the following rules:

### 1. Code Is Law (Zero Trust)

* Never rely on documentation, comments, or claimed intent. Audit verbatim implementation code, permissions, and blast radius directly.
* Inspect callers before patching functions. Fix root causes at shared junctions rather than patching symptoms across callers.

### 2. The Ladder (Anti-Bloat Engineering)

Stop at the first rung that satisfies the requirement:

1. **YAGNI:** Does this need to exist? If speculative, skip it.
2. **Reuse:** Already in the codebase? Reuse existing helpers and patterns.
3. **Stdlib First:** Standard library before external packages.
4. **Native Platform:** OS/platform primitives before custom code (e.g. `pmset`, `systemd-inhibit`, CSS, standard CLI).
5. **Installed Deps:** Use already installed dependencies before adding new ones.
6. **Minimal Code:** One line before fifty. Shortest working diff wins.

### 3. Git Push & Operations

* **NEVER push autonomously.** Always wait for explicit user authorization ("push", "pusha").
* Keep commits focused, production-grade, and free of personal paths or jargon.

### 4. Defensive Scripting & Shell Safety

* Whitelist inputs with strict regex (`^[0-9]+$`).
* Always attach atomic `trap` cleanup on `INT TERM EXIT` for temporary resources.
* Shell scripts must work both locally (`BASH_SOURCE[0]`) and via pipe (`curl | bash`).

### 5. Absolute Privacy & Sanitization

* Zero personal paths (`/Users/...`, `/home/...`), usernames, or host machine details in code, commits, or documentation.
* Use generic placeholders (`<project_dir>`, `https://example.com`).
* **Grill-Me Protocol:** On any ambiguity regarding private data, credentials, or sensitive host configs, stop and interrogate the user for clarification.

### 6. Verification Gate

* Non-trivial logic must leave at least one runnable check (assert-based check or unit test).
* Test negative branches and edge cases first.
