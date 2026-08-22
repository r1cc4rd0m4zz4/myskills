---
name: web-search
description: Search the web, fetch clean reader-mode pages, and execute deep multi-query research with Exa. Optimized for low token consumption (~80% compaction) and automatic tracking deduplication.
---

# Web Search (Standalone Exa Suite)

Self-contained skill for semantic search, reader-mode page extraction, and deep multi-source research powered by Exa. Fully harness-agnostic with zero external package dependencies.

---

## Capabilities

1. **`web_search_exa`**: Fast semantic search returning clean titles, canonical URLs, and extracted highlights.
2. **`web_fetch_exa`**: Reader-mode page extractor returning structured text/Markdown from target URLs without HTML clutter or cookie banners.
3. **`deep_search_exa`**: Multi-query parallel search and reasoning mode for comprehensive investigations and cross-source synthesis.

---

## Tool Execution

All operations run through the standalone ES Module `exa_tool.mjs` (compatible with Node 18+ on macOS, Linux, and WSL2):

```bash
# 1. Semantic Web Search
node <skill_dir>/exa_tool.mjs search "<query>" [numResults] [category]

# 2. Web Page Content Extraction (Fetch)
node <skill_dir>/exa_tool.mjs fetch "<url>" [maxChars]

# 3. Deep Research & Multi-Query Reasoning
node <skill_dir>/exa_tool.mjs deep "<query>" [numResults] [type: deep|deep-lite|deep-reasoning] "[query1;query2;...]"
```

---

## Tool Selection Matrix

| Objective | Recommended Tool | Invocation Example | Expected Output |
| :--- | :--- | :--- | :--- |
| **Facts, news, entities, quick links** | `web_search_exa` | `search "Gemini 2.0 Flash release" 5` | Compact JSON (~50–100 tokens/item) |
| **Read docs / full article content** | `web_fetch_exa` | `fetch "https://arxiv.org/abs/2403.05530" 3000` | Clean Markdown text (no HTML) |
| **Complex comparisons, deep investigations** | `deep_search_exa` | `deep "WebAssembly runtime 2026" 10 deep-reasoning "Wasm GC performance;Wasm edge computing"` | Multi-angle synthesized results |

---

## Token & Context Window Optimization

- **Payload Compaction**: Titles truncated to 100 chars; max 3 highlights of 200 chars per result; metadata stripped. Reduces context overhead by **~80%** compared to raw web responses.
- **URL Normalization**: Strips tracking parameters (`utm_*`, `gclid`, `fbclid`, `ref`, `srccid`, etc.), canonicalizes lowercase hosts, and normalizes trailing slashes.
- **Intelligent Deduplication**: Merges duplicate records by canonical URL, preserving the most complete title, valid publication dates, and non-duplicate highlights.

---

## Credentials & Rate Limits

```bash
# Optional: unlocks authenticated Exa Deep Search REST API and removes rate limits
export EXA_API_KEY="sk-..."

# If not set: automatically uses public anonymous Exa MCP access with parallel multi-query fallback
```

---

## Execution Patterns

### 1. Direct Search (Single-Turn)
For factual lookups, execute `search` and synthesize immediately:
```bash
node <skill_dir>/exa_tool.mjs search "latest OpenAI model release" 5
```

### 2. Two-Stage Inspect (Search → Fetch)
To inspect specific documentation without polluting context:
```bash
# Step 1: Find the relevant canonical URL
node <skill_dir>/exa_tool.mjs search "DeepMind Gemini 1.5 paper arXiv" 1
# Step 2: Fetch only the necessary content section
node <skill_dir>/exa_tool.mjs fetch "https://arxiv.org/abs/2403.05530" 3000
```

### 3. Deep Research with Subagents
For complex multi-stage tasks, dispatch a subagent with distinct research angles:
```text
Run `node <skill_dir>/exa_tool.mjs deep "<main_query>" 10 deep "[angle1;angle2]"`
Then `fetch` the top 1-2 Tier-5 primary sources.
Return only verified facts with markdown citations.
```

---

## Source Quality Rubric (Tier 1–5)

- **Tier 5 (Primary / Practitioner)**: Official documentation, GitHub repositories, engineering blogs with benchmarks, arXiv papers.
- **Tier 4 (Specialist Media)**: TechCrunch, Ars Technica, The Verge, Reuters.
- **Tier 3 (General Media)**: General news outlets and wire services.
- **Tier 2 (Commentary)**: Personal opinion blogs, unverified social posts.
- **Tier 1 (Low Signal)**: SEO content farms, AI slop aggregators (discard immediately).

---

## Output Format

For complex inquiries:
1. **Executive Summary**: 2–4 concise sentences answering the core question.
2. **Key Findings**: Structured bullet points with clean markdown hyperlinks to sources.
3. **Synthesis & Trade-offs**: Divergences, consensus, or technical nuances across sources.
