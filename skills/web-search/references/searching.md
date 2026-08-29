# Effective Exa Search Queries

Exa relies on semantic embeddings rather than literal keyword matching. Natural, context-rich questions outperform short keywords.

## Effective vs Ineffective Queries
- ✅ `"Best LLM inference engines with vLLM and TensorRT-LLM benchmarks in 2026"`
- ❌ `"LLM inference"`
- ✅ `"PostgreSQL 17 performance improvements and migration gotchas"`
- ❌ `"postgres new features"`

## Best Practices
1. **Specific Context**: State constraints directly (e.g. `production`, `open-source`, `benchmark`).
2. **Angle Diversity**: For multi-query searches, vary perspective rather than substituting synonyms (e.g. `latency benchmark` vs `memory footprint` vs `production failure stories`).
3. **Temporal Anchors**: Include explicit year or month when looking for latest releases.
