# Global Guardrails: Code Is Law (Anti-Bloat Mode)

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."* — Antoine de Saint-Exupéry  
> Every superfluous line is an uninspected law, a hidden failure state, and an expanded attack surface.

- **Code Is Law (Zero Trust):** Code is law, not promises or reputation. Audit actual implementation, privileges, and blast radius directly from verbatim source—never trust documentation or claimed intent.
- **Git Push:** NEVER push autonomously. Wait for the explicit order ("push", "fai il push", "pusha").
- **Notes & Runbooks:** ONLY save personal notes and guides outside the repository in local private storage. Keep repos clean.
- **The Ladder (Anti-Bloat):** Native OS feature before code; stdlib before dependencies; one line before fifty. Never trade 1 native command (`pmset`, `systemd-inhibit`) for daemons, Accessibility hooks, or `sudoers NOPASSWD` hacks.
- **Defensive Scripting:** Whitelist inputs with strict regex (`^[0-9]+$`). Always atomic `trap` cleanup on `INT TERM EXIT`. No security theater: run tools matching the actual stack (ShellCheck + Gitleaks for shell; zero SCA on zero-dependency code).
- **Dual-Mode Installers:** Installers must work both locally from any folder (`BASH_SOURCE[0]`) and remotely via pipe (`curl | bash`). Never assume a repo is public.
- **Verification & CI:** Test negative branches and edge cases first. When CI exists, actively query remote jobs until green (`success`) before calling it done. Local pass != remote verification.
- **Sanitization:** Zero personal paths (`/Users/...`), usernames, or chat jargon ("Fix A/B", internal labels) in commits, code, or docs. Strictly production-grade.
