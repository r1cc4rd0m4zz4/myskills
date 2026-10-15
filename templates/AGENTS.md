# Global Guardrails: Code Is Law (Anti-Bloat Mode)

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."* — Antoine de Saint-Exupéry  
> Every superfluous line is an uninspected law, a hidden failure state, and an expanded attack surface.

- **Code Is Law (Zero Trust):** Code is law, not promises or reputation. Audit actual implementation, privileges, and blast radius directly from verbatim source—never trust documentation or claimed intent.
- **Git Workflow:** NEVER push autonomously. Wait for the explicit order ("push", "fai il push", "pusha"). Before editing in a repo, read its own `AGENTS.md`/`CONTRIBUTING.md`. Before proposing any commit or push, run `git fetch` + `git status -sb`, report the exact divergence, and run the repo's verification gate.
- **Notes & Runbooks:** ONLY save personal notes and guides outside the repository in local private storage. Keep repos clean.
- **The Ladder (Anti-Bloat & Minimalist Engineering):** Solve the problem with the least new code.
  1. *Does it need to exist?* Reject unrequested options, speculative configuration, and flexibility.
  2. *Already in codebase:* Reuse existing helpers, components, and conventions before writing new code.
  3. *Native & stdlib first:* OS primitives, runtime built-ins, and standard libraries before any custom code. Never trade 1 native command (`pmset`, `systemd-inhibit`) for daemons, Accessibility hooks, or `sudoers NOPASSWD` hacks.
  4. *Dependencies policy:* Strictly lockfile-only. **NEVER** add an external dependency without explicit pushback and user approval.
  5. *Shortest working diff:* No speculative abstractions, wrappers, or "for later" code. Deletion beats addition.
- **Pushback Policy:** Direct minimal execution by default. Mandatory proactive pushback before acting ONLY when a request introduces new external dependencies or an architecture grossly oversized relative to platform standards.
- **Verification of Compact Code:** Compact code without checks is unverified debt. Non-trivial logic (branches, parsers, security flows) must include a minimal assertion or unit test covering negative branches.
- **Defensive Scripting:** Whitelist inputs with strict regex (`^[0-9]+$`). Always atomic `trap` cleanup on `INT TERM EXIT`. No security theater: run tools matching the actual stack (ShellCheck + Gitleaks for shell; zero SCA on zero-dependency code).
- **Dual-Mode Installers:** Installers must work both locally from any folder (`BASH_SOURCE[0]`) and remotely via pipe (`curl | bash`). Never assume a repo is public.
- **Verification & CI:** Test negative branches and edge cases first. When CI exists, actively query remote jobs until green (`success`) before calling it done. Local pass != remote verification.
- **Sanitization:** Zero personal paths (`/Users/...`), usernames, or chat jargon ("Fix A/B", internal labels) in commits, code, or docs. Strictly production-grade.
