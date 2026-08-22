# Contributing to Curated Agent Skills

We welcome contributions from both human developers and AI agents! This repository adheres strictly to the open **Agent Skills standard** (`skills.sh`).

---

## Guiding Principles

1. **Harness-Agnostic**: Skills must never assume a specific AI client (Claude Code, Pi, Cursor, Codex, OpenCode, etc.). They must work universally.
2. **Zero Bloat & Token Economy**: Prune metadata, tracking parameters, and raw boilerplate before returning results to LLM context windows (~80% token compaction target).
3. **Defense in Depth**: All network/shell tools must safely handle input boundaries (no raw shell string interpolations, strict IP resolution & pinning for network requests).
4. **Self-Contained Runtimes**: Use zero-dependency Node.js ESM (`.mjs`) or Python with inline PEP 723 metadata (`uv`).

---

## Directory Structure

All skills must reside directly under the `skills/` folder (flat structure):

```text
skills/
└── your-skill-name/
    ├── SKILL.md          # Standard frontmatter + instructions + prompt
    ├── tool_script.mjs   # (Optional) Node.js executable
    └── references/       # (Optional) Domain references, schemas, and scoring rules
```

---

## `SKILL.md` Requirements

Every skill requires a valid YAML frontmatter block at the very top:

```markdown
---
name: your-skill-name
description: A concise, one-sentence description of what this skill does and when an agent should invoke it.
---

# Title

Detailed instructions, tool execution commands, and edge-case guidance.
```

- **`name`**: Lowercase, kebab-case matching the directory name.
- **`description`**: Clear, high-signal summary describing trigger conditions and capabilities.
- **Language**: All documentation, comments, and instructions must be in **English**.

---

## Development & Verification Workflow

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/r1cc4rd0m4zz4/myskills.git
   cd myskills
   ```

2. **Link for Local Testing**:
   ```bash
   ./scripts/link-skills.sh
   ```

3. **Verify Functionality**:
   - For Node scripts: Ensure they run with `node script.mjs` on Node 18+ without `npm install`.
   - For Python scripts: Ensure unit tests pass using `uv run run_tests.py` or `pytest`.

4. **Submit a Pull Request**:
   - Ensure `README.md` catalog table is updated with your new skill.
   - Describe the security model, token impact, and verification steps in the PR description.
