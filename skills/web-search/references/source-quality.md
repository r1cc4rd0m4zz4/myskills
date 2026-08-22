# Valutazione Qualità Fonti

Score da 1-5 per ogni fonte, basato su credibilità e rilevanza.

## Score di Qualità

### 5 — Practitioner + Data
**Cosa cercare**:
- Engineer blog con benchmark reali
- Documentation ufficiale (docs, API reference)
- Code examples funzionanti
- Dati quantitativi (numeri, metriche)

**Esempi**:
- Blog di sviluppatori con codice sorgente
- Documentation di framework/librerie
- Paper tecnici con esperimenti riproducibili

### 4 — Specialist Media
**Cosa cercare**:
- Testata di settore con redazione tecnica
- Giornalisti specializzati in tecnologia
- Articolii con interviste a practitioners

**Esempi**:
- TechCrunch, The Verge, Ars Technica
- Hacker News (top comments, non link)
- Reddit r/MachineLearning, r/programming (con moderazione)

### 3 — General Media
**Cosa cercare**:
- Testate generaliste con sezione tech
- AGI, AP, Reuters, BBC

**Limiti**:
- Spesso superficiali
- Possono fraintendere dettagli tecnici
- Buoni per headline, cattivi per deep dive

### 2 — Commentary/Opinion
**Cosa cercare**:
- Blog personali
- Opinion pieces
- Thread Twitter/X di influencer

**Limiti**:
- Spesso sensazionalistici
- Mancano dati concreti
- Possono avere bias evidenti

### 1 — Low Signal
**Cosa cercare**:
- SEO spam blogs
- Clickbait sites
- Fonti con bias commerciale evidente
- AI-generated content non verificato

## Regole di Valutazione

1. **Convergenza > Isolamento**: 3 fonti low-signal che dicono la stessa cosa = rumore. 2+ high-signal che convergono = segnale.

2. **Practitioner > Commentator**: Chi fa il lavoro vale più di chi lo commenta.

3. **Via negativa**: Prima di sintetizzare, definisci chi ESCLUDERE (fonti con incentivi disallineati, senza "skin in the game", claim infalsificabili).

4. **Red-team**: Che prospettive mancano? Quali bias potrebbero distorcere il risultato?

5. **Ideas over entities**: Per expert-finding e best-practices, l'output primario sono verità convergenti, non liste di nomi.

## Processo di Tagging

Per ogni fonte, assegna:
- `quality_score`: 1-5
- `source_type`: "practitioner", "specialist_media", "general_media", "commentary", "low_signal"
- `bias_flags`: Lista di potenziali bias (es. "commercial interest", "political agenda")
- `data_present`: boolean — Il contenuto contiene dati concreti?

## Output

Includi il quality score in ogni risultato restituito, così il compilatore può pesare i risultati in base alla qualità.
