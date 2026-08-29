# Search Result Filtering

## Hard Filters (Mandatory)
- **Recency**: Limit to last 24–48 hours for breaking news or specified ranges for historical analysis.
- **Geography/Language**: Filter by required regional context or language.
- **Source Trust**: Discard clickbait, SEO farms, and AI-generated aggregators immediately.

## Soft Filters (Contextual Scoring)
- **Relevance**: Does the highlight directly answer the target query?
- **Data Density**: Favor results containing concrete numbers, benchmarks, dates, or code.
- **Recency & Supersession**: Prefer newest revisions when articles are updated.

## Output Compaction Standard
Return strictly minimal structured keys:
- `url`: Canonical cleaned URL
- `title`: Clean title (truncated to 100 chars)
- `published`: ISO date or `N/A`
- `highlights`: Max 3 high-signal excerpts (truncated to 200 chars each)
