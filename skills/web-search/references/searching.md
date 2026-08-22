# Guida per Query Exa Efficaci

Exa usa embeddings semantici, non keyword matching. Query lunghe e specifiche funzionano meglio di brevi e generiche.

## Formati di Query che Funzionano

### ✅ Buoni (specifici, contestuali)
- "What are the best LLM fine-tuning frameworks for production use in 2026?"
- "Latest news about OpenAI GPT-5 release date and features"
- "Competitors to Stripe in payment processing for startups"
- "What do engineers say about WebGPU browser support in 2026?"

### ❌ Cattivi (troppo generici)
- "LLM frameworks"
- "News"
- "Stripe"
- "WebGPU"

## Pattern di Query per Tipo di Ricerca

### News quotidiane
```
"top news today [date]"
"breaking news [topic] [month] [year]"
"world news headlines today"
```

### Analisi tecnologiche
```
"latest developments in [technology] [year]"
"[Company] news releases [date range]"
"open source [category] tools comparison"
```

### Deep dive tematici
```
"What do [practitioners/experts] say about [topic]?"
"Common complaints about [tool/platform]"
"Migration stories from [old] to [new]"
```

## Consigli Pratici

1. **Includi date** quando relevantes (es. "August 2026")
2. **Specifica il contesto** (es. "for production use", "in 2026")
3. **Usa nomi propri** quando li conosci (es. "Stripe", "WebGPU")
4. **Diversifica per angolo**, non per sinonimi (es. "best" vs "most reliable" vs "cheapest")

## Errori da Evitare

- **Synonym queries**: "overrated AI" e "overhyped AI" vanno nello stesso embedding → diversifica per angolo, non per parole simili.
- **Query troppo brevi**: "AI tools" → risultati troppo generici.
- **Ripetere la stessa query**: Se un search fallisce, riprova con angolazioni diverse, non parafrasi.
