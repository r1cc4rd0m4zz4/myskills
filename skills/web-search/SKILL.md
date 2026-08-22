---
name: web-search
description: "Cerca e naviga su internet con Exa (web_search_exa, web_fetch_exa, deep_search_exa). Per news, analisi tech, estrazione pagine e deep dive."
---

# Web Search (Exa Suite Nativa)

Skill autonoma per ricerca, estrazione e deep investigation via Exa, **senza dipendenza da estensioni terze o pacchetti npm**.

Supporta le 3 modalità native Exa:
1. **`web_search_exa`** — Ricerca semantica rapida e snippet essenziali.
2. **`web_fetch_exa`** — Estrazione diretta del testo pulito da URL specifici.
3. **`deep_search_exa`** — Ricerca multi-angolo approfondita e sintesi multi-fonte.

---

## Strumenti Nativi Disponibili

Tutti i tool sono eseguiti tramite l'helper standard ES Module `exa_tool.mjs` (compatibile al 100% con Node 18+ su macOS, Ubuntu e WSL2):

```bash
# 1. Ricerca Semantica
node <skill_dir>/exa_tool.mjs search "<query>" [numResults] [category]

# 2. Estrazione Pagina da URL (Web Fetch)
node <skill_dir>/exa_tool.mjs fetch "<url>" [maxChars]

# 3. Deep Research & Ragionamento
node <skill_dir>/exa_tool.mjs deep "<query>" [numResults] [type: deep|deep-lite|deep-reasoning] "[query1;query2]"
```

---

## Matrice di Scelta Tool

| Esigenza | Tool Raccomandato | Esempio di Utilizzo | Output Atteso |
| :--- | :--- | :--- | :--- |
| **Fatti, news, entità, link veloci** | `web_search_exa` | `search "Gemini 2.0 Flash release" 5` | JSON compatto (~50-100 tok/item) |
| **Leggere documentazione / pagina specifica** | `web_fetch_exa` | `fetch "https://arxiv.org/abs/2403.05530" 3000` | Testo/Markdown pulito senza HTML |
| **Analisi complessa, competitor, trend** | `deep_search_exa` | `deep "WebAssembly browser runtime 2026" 10 deep-reasoning "Wasm GC performance;Wasm edge computing"` | Multi-query & sintesi multi-fonte |

---

## Ottimizzazione Token e Contesto

**Obiettivo**: Massimizzare il segnale riducendo fino all'80% i token sprecati.

1. **`web_search_exa`**: Titoli troncati a 100 char, max 3 highlights da 200 char, rimozione metadati e stripping parametri di tracciamento (`utm_*`, `gclid`, `ref`).
2. **`web_fetch_exa`**: Estrazione del solo testo utile / Markdown (eliminazione cookie banner, navigazione, script) con budget di caratteri configurabile (default: 4000 char).
3. **`deep_search_exa`**: Deduplicazione cross-query automatica prima di restituire il risultato al contesto.

---

## Configurazione Credenziali

```bash
# Opzionale: Se impostata, sblocca Deep Search API e rimuove rate limiting
export EXA_API_KEY="sk-..."

# Se non impostata: usa automaticamente l'accesso MCP anonimo e fallback multi-query
```

---

## Pattern di Esecuzione

### 1. Ricerca Semplice (Single-Turn)
Per domande puntuali, esegui direttamente `search` e sintetizza subito:
```bash
node /Users/mazric/.agents/skills/web-search/exa_tool.mjs search "notizie geopolitiche oggi" 5
```

### 2. Ispezione Dettagliata (Search + Fetch)
Trova prima l'URL rilevante, poi estrai la pagina mirata per evitare di inquinare il contesto:
```bash
# Step 1: Trova l'URL
node /Users/mazric/.agents/skills/web-search/exa_tool.mjs search "DeepMind Flamingo paper" 2
# Step 2: Estrai solo la sezione rilevante
node /Users/mazric/.agents/skills/web-search/exa_tool.mjs fetch "https://arxiv.org/abs/..." 3500
```

### 3. Ricerca Complessa con Subagent
Per deep dive con subagent (es. `scout` o `worker`), fornisci il template con query diversificate:

```
Usa node /Users/mazric/.agents/skills/web-search/exa_tool.mjs per eseguire:
1. deep_search sulla domanda primaria
2. fetch su 1-2 fonti tier-5 identificate
Restituisci solo dati strutturati e sintetizzati.
```

---

## Valutazione Qualità Fonti (Tier 1-5)

- **Tier 5 (Practitioner / Primary)**: Repository GitHub, paper ArXiv, blog tecnici di ingegneri con benchmark, documentazione ufficiale.
- **Tier 4 (Specialist Media)**: TechCrunch, Ars Technica, The Verge, Reuters.
- **Tier 3 (General Media)**: Giornali generici, agenzie di stampa.
- **Tier 2 (Commentary)**: Opinioni su Medium, post personali non verificati.
- **Tier 1 (Low Signal)**: Siti SEO spam, aggregatori automatici (scartare immediatamente).

---

## Formato di Sintesi Finale

Per ricerche complesse:
1. **Risposta Diretta**: 2-4 frasi con la risposta chiave.
2. **Evidenze & Dati**: Bullet points con hyperlink puliti alle fonti.
3. **Punti di Convergenza / Divergenza**: Se più fonti non concordano.
