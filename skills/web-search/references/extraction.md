# Estrazione Dati Strutturati

Estrai campi specifici dai risultati di Exa in uno schema definito.

## 1. Schema Base Ricerca (`web_search_exa`)

```json
{
  "title": "Titolo articolo (max 100 char)",
  "url": "https://example.com/clean-url",
  "published": "2026-08-16T00:00:00.000Z",
  "highlights": ["Frammento chiave 1 (max 200 char)", "Frammento 2"]
}
```

## 2. Schema Pagina Estratta (`web_fetch_exa`)

```json
{
  "url": "https://example.com/clean-url",
  "content": "# Testo o Markdown estratto...\n\nContenuto ripulito da header, cookie e script.",
  "truncated": false,
  "total_chars": 2840
}
```

## 3. Schema Deep Search (`deep_search_exa`)

```json
{
  "mode": "api_deep_search | mcp_multi_search_fallback",
  "query": "Domanda di ricerca",
  "results": [
    {
      "title": "Titolo",
      "url": "https://...",
      "published": "2026-08-16",
      "highlights": ["..."]
    }
  ]
}
```

## Campi Opzionali per Sintesi Specializzate

### Per Notizie
- `location`: Luogo dell'evento
- `entities`: Persone/organizzazioni menzionate
- `impact`: Alto/Medio/Basso

### Per Tecnologia
- `technology`: Nome tecnologia/tool
- `version`: Versione
- `use_case`: Caso d'uso principale

### Per Business / Competitor
- `company`: Nome azienda
- `market_segment`: Segmento di mercato
- `competitors`: Competitori diretti
