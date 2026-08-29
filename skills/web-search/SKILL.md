---
name: web-search
description: Semantic web search, reader-mode page extraction, and multi-query deep research via Exa with ~80% token reduction and automatic tracking removal.
---

# Web Search

Harness-agnostic web retrieval via standalone zero-dependency Node.js ESM tool.

## Tool Invocation

```bash
# 1. Fast Semantic Search (Default: 10 results)
node <skill_dir>/exa_tool.mjs search "<query>" [numResults] [category]

# 2. Reader-Mode Content Extraction
node <skill_dir>/exa_tool.mjs fetch "<url>" [maxChars]

# 3. Deep Multi-Angle Research
node <skill_dir>/exa_tool.mjs deep "<query>" [numResults] [type: deep|deep-lite|deep-reasoning] "[subquery1;subquery2]"
```

## Decision Protocol

- **Fact checks, quick links, news**: `search "<query>" 5`
- **Read specific URL / documentation**: `fetch "<url>" 4000`
- **Broad landscape / multi-angle investigation**: `deep "<query>" 10 deep "[subquery1;subquery2]"`

## Compaction & Signal Guarantees

- **Context Savings**: Prunes boilerplate, navigation chrome, and metadata (~80% token reduction vs raw web/HTML payloads).
- **URL Normalization**: Strips tracking parameters (`utm_*`, `gclid`, `fbclid`, `ref`, etc.) and canonicalizes paths.
- **Deduplication**: Merges overlapping URLs preserving richest titles, dates, and non-duplicate highlights.

## Source Quality Tiering

1. **Tier 5 (Primary)**: Official documentation, GitHub repos, arXiv papers, engineering benchmark posts.
2. **Tier 4 (Specialist Media)**: TechCrunch, Ars Technica, The Verge, Reuters.
3. **Tier 3 (General Media)**: Wire services, mainstream news.
4. **Tier 2 (Commentary)**: Personal blogs, social media threads.
5. **Tier 1 (Low Signal)**: SEO content farms, AI slop aggregators (discard immediately).
