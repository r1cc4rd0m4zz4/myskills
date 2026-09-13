# Global Guardrails: Code Is Law (Zero-Bloat Mode)

Universal, production-grade guardrails for autonomous AI coding agents and developers.

---

## 1. Core Mandates

- **Code Is Law (Zero Trust):** Code is law, not promises or reputation. Audit actual implementation, privileges, and blast radius directly from verbatim source—never trust documentation, comments, or claimed intent.
- **Git Push Protection:** NEVER push autonomously. Always wait for explicit user authorization ("push", "fai il push", "pusha").
- **Clean Repositories:** Keep repositories strictly clean. Never commit scratchpads, notes, or temporary exploration files.
- **The Ladder (Anti-Bloat Engineering):**
  1. Native OS or platform feature before custom code.
  2. Standard library before external dependencies.
  3. One line before fifty.
  Never trade one native command (`pmset`, `systemd-inhibit`) for background daemons, accessibility hooks, or `sudoers` hacks.
- **Defensive Scripting:** Whitelist inputs with strict regex (`^[0-9]+$`). Always attach atomic `trap` cleanup on `INT TERM EXIT`. No security theater: match validation tools to the actual stack (ShellCheck + Gitleaks for shell; zero SCA on zero-dependency code).
- **Dual-Mode Installers:** Installers and scripts must work both locally from any directory (`BASH_SOURCE[0]`) and remotely via pipe (`curl | bash`). Never assume a repository is public or cloned in a standard path.
- **Verification First:** Test negative branches and security edge cases first. Local pass != remote verification. Non-trivial logic must leave runnable checks behind.
- **Strict Sanitization & Zero PII:** Zero personal paths (`/Users/...`, `/home/...`), host usernames, machine configurations, internal IP addresses, credentials, or internal chat jargon in commits, code, or documentation. Strictly production-grade.

---

## 2. Absolute Privacy & Zero Data Exfiltration

- **Zero Host Leaks:** Never hardcode, commit, or log local system details, home directories, environment secrets, or private tokens.
- **Generic Placeholders Only:** All examples, tests, documentation, and error messages MUST use generic placeholders (`<project_dir>`, `https://example.com`, `sk-...`, `0.0.0.0`).
- **Grill-Me Protocol on Ambiguity:** If there is the slightest doubt about whether a detail, path, identifier, or value constitutes personal, confidential, or internal host configuration information, **NEVER assume or proceed silently**. Interrogate and grill the maintainer directly for explicit clarification.

---

## 3. Token & Context Economy

- **Context Preservation:** LLM context windows are finite and expensive. Raw payload dumping (HTML, unpruned JSON, huge logs) is prohibited.
- **Aggressive Compaction:** Filter, prune, deduplicate, and compact outputs before injecting them into the agent's context window (~80% token reduction target).
