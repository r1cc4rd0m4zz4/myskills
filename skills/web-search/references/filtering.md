# Filtraggio Risultati Exa

Applica filtri hard e soft per selezionare risultati rilevanti.

## Filtri Hard (obbligatori)

### Data
- **Recenti**: Ultime 24-48 ore per news
- **Periodo definito**: Range specifico per analisi storiche
- **Escludi**: Risultati vecchi di X giorni (configurabile)

### Geografia
- **Includi regioni**: "EU", "US", "Asia-Pacific"
- **Escludi regioni**: "North Korea", "Iran" (se rilevante)
- **Lingua**: Filtra per lingua del contenuto (es. solo inglese, o multilingue)

### Tipo di fonte
- **Includi**: "TechCrunch", "Reuters", "ArXiv", "GitHub"
- **Escludi**: "clickbait", "SEO spam", "blog personali non verificati"

## Filtri Soft (giudizio contestuale)

### Rilevanza semantica
- Il risultato parla direttamente della query?
- Aggiunge contesto o è solo menzionato?

### Completezza
- Il risultato contiene dati specifici (numeri, date, nomi)?
- O è solo un titolo/snellato?

### Aggiornamento
- La data di pubblicazione è recente?
- Ci sono versioni più recenti della stessa notizia?

## Processo di Filtraggio

1. **Applica filtri hard** → Scarta risultati che non passano
2. **Valuta filtri soft** → Score 1-5 per ogni risultato rimanente
3. **Tieni top N** → Basato sul tuo budget di risultati
4. **Deduplica** → Stesso URL = tieni il più recente/ricco

## Output di Filtraggio (Compattato)

Per ottimizzare l'uso di token, restituisci SOLO:
- `url`: Link originale (tronco a 150 char se necessario)
- `title`: Titolo articolo (tronco a 100 char)
- `published`: Data pubblicazione (ISO 8601, o vuota se non disponibile)
- `highlights`: Array di max 3 highlight (troncati a 200 char ciascuno)
- `relevance_score`: 1-5 (opzionale, solo se utile per ranking)

**Escludi**:
- `author` (raro utile per sintesi)
- `full snippet` (usa solo highlights)
- `metadata` extra (tranne data)

Esempio output compattato:
```json
{"url":"https://...","title":"Ukraine launches 600 drones","published":"2026-08-16","highlights":["822 drones shot down","6 killed in Russia"]}
```
