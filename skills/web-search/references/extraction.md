# Structured Extraction Schema

## 1. Search Schema (`web_search_exa`)
```json
{
  "title": "Article Title (<=100 chars)",
  "url": "https://example.com/canonical-path",
  "published": "2026-08-16T00:00:00.000Z",
  "highlights": ["Top highlight excerpt (<=200 chars)"]
}
```

## 2. Page Extraction Schema (`web_fetch_exa`)
```json
{
  "url": "https://example.com/canonical-path",
  "content": "Extracted Markdown/clean text stripped of ads, cookies, and navigation.",
  "truncated": false,
  "total_chars": 2840
}
```

## 3. Deep Search Schema (`deep_search_exa`)
```json
{
  "mode": "api_deep_search | mcp_multi_search_fallback",
  "query": "Main research question",
  "results": [
    {
      "title": "Title",
      "url": "https://...",
      "published": "2026-08-16",
      "highlights": ["..."]
    }
  ]
}
```
