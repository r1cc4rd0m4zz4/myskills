# MySkills

Raccolta di agent skills per agenti di codifica AI (Pi, Claude Code, Cursor, Codex, OpenCode).

## Skills Incluse

- **`web-search`**: Suite di ricerca web autonoma basata su Exa (`web_search_exa`, `web_fetch_exa`, `deep_search_exa`), con compattazione automatica dei token, filtraggio anti-tracking e zero dipendenze npm (Node.js ES Module nativo).
- **`secure-url-fetcher`**: Utility hardened per scaricare contenuti da URL esterni mitigando attacchi SSRF e DNS Rebinding tramite validazione IP stretta e IP pinning.

---

## Installazione

### 1. Tramite `npx skills` (Standard skills.sh per tutti gli agenti)

Puoi installare le skill in modo interattivo scegliendo quali aggiungere e per quali agenti:

```bash
npx skills add r1cc4rd0m4zz4/myskills
```

### 2. Tramite Pi Coding Agent (`pi install`)

Per installare l'intero pacchetto come estensione/skill globale per Pi:

```bash
# Installazione globale
pi install git:github.com/r1cc4rd0m4zz4/myskills

# Oppure installazione limitata al progetto corrente (-l)
pi install -l git:github.com/r1cc4rd0m4zz4/myskills
```

---

## Struttura Repository

```text
myskills/
├── README.md
├── package.json
├── .gitignore
└── skills/
    ├── web-search/
    │   ├── SKILL.md
    │   ├── exa_tool.mjs
    │   ├── references/
    │   └── examples/
    └── secure-url-fetcher/
        ├── SKILL.md
        ├── secure-fetcher.py
        └── pyproject.toml
```

---

## Licenza

[MIT](LICENSE)
