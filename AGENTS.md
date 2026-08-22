# Agent Guidelines (`AGENTS.md`)

This repository hosts a curated collection of agent-agnostic skills. Any autonomous AI agent or developer contributing to or executing from this repository must adhere to the conventions outlined below.

---

## 1. Principles

1. **Harness-Agnostic Design**: Never build skills tied to a specific proprietary agent framework. Skills must adhere to the open Agent Skills standard (`SKILL.md` with standard YAML frontmatter) and execute on any host runtime.
2. **Zero Ambient Assumptions**: Rely exclusively on standard runtime environments:
   - **Node.js (ESM `.mjs`)**: For HTTP, JSON-RPC, stream parsing, and cross-platform I/O. Use Node 18+ native `fetch` and standard globals. No required `node_modules` or `npm install` steps for skill scripts.
   - **Python (PEP 723)**: If Python is required, declare dependencies inline via PEP 723 metadata blocks and run via `uv run`.
3. **Strict Token Economy**: LLM context windows are finite. Raw API or HTML dumping is prohibited. Skills must filter, prune, deduplicate, and compact outputs (~50–100 tokens per record, ~80% reduction vs raw payloads).
4. **Security by Default**:
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
1. **Self-Check**: Run the skill's tool runner directly from the terminal with a real or mocked invocation.
2. **Automated Tests**: If test suites exist (e.g. `run_tests.py`), all tests must pass with 100% success rate.
3. **No Unused Scaffolding**: Keep diffs minimal and delete dead code immediately.
