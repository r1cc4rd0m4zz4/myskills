# Sintesi Narrativa

Trasforma risultati di ricerca in narrativa coerente con contesto e citazioni.

## Quando Usare la Sintesi Narrativa

- Query complesse con multiple angolazioni
- Deep dive tematici
- Analisi comparative
- Ricerca di "best of" o "top X"

## Struttura della Sintesi

### 1. Riassunto Esecutivo (3-5 bullet)
- I punti chiave emersi dalla ricerca
- Convergenze tra fonti high-signal
- Cosa sappiamo con certezza vs cosa è speculazione

### 2. Dettagli per Tema
- Organizza per tema/sottotema, non per fonte
- Includi hyperlink alle fonti originali
- Cita dati specifici (numeri, date, nomi)

### 3. Pattern Non Ovvî
- Tendenze emergenti non menzionate esplicitamente
- Correlazioni tra fonti indipendenti
- Gap nella copertura attuale

### 4. Fonti Scartate (trasparenza)
- Quali risultati sono stati esclusi e perché
- Bias potenziali nelle fonti incluse
- Cosa manca nella copertura attuale

## Regole di Scrittura

- **Practitioner > Commentator**: Priorità a chi fa il lavoro vs chi lo commenta
- **Dati > Opinioni**: Citare numeri, non solo affermazioni
- **Cita le fonti**: Hyperlink inline dove utile
- **Ammetti incertezze**: Segnala dove le fonti divergono

## Output Format

```markdown
## Riassunto Esecutivo

- Punto 1
- Punto 2
- Punto 3

## Dettagli per Tema

### Tema 1
- Dettaglio con [fonte](url)

### Tema 2
- Dettaglio con [fonte](url)

## Pattern Non Ovvî

- Osservazione 1
- Osservazione 2

## Fonti Scartate

- Fonte X: motivo esclusione
- Fonte Y: motivo esclusione
```

## Esempio

**Query**: "Cosa dicono gli ingegneri su WebGPU?"

**Sintesi**:
```markdown
## Riassunto Esecutivo

- WebGPU supportato in Chrome 113+, Firefox 113+, Safari Technology Preview
- GPU computing browser-side ancora limitato a casi d'uso specifici
- Community divide: entusiasti per potenzialità vs scettici su adoption

## Dettagli per Tema

### Browser Support
- Chrome e Firefox hanno implementazione stabile
- Safari solo in Technology Preview (non production)
- [Chrome Status](https://chromestatus.com) conferma feature flags

### Use Cases
- Rendering 3D pesante (Three.js, Babylon.js)
- ML inference browser-side (TensorFlow.js, ONNX)
- Video processing (limitato)

## Fonti Scartate

- Blog "WebGPU will replace WebGL" (SEO spam, nessuna证据 tecnica)
- Tweet di influencer senza background tecnico
```
