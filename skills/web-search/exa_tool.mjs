#!/usr/bin/env node
/**
 * Exa Tool Runner for web-search skill.
 * Zero-dependency standalone ES Module (Node 18+).
 */

const MCP_URL = "https://mcp.exa.ai/mcp";
const REST_SEARCH_URL = "https://api.exa.ai/search";
const USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)";
const TRACKING_PARAMS = new Set([
  "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
  "ref", "refid", "referral", "source", "srccid", "gclid", "fbclid",
  "igshid", "twclid", "msclkid", "yclid", "wa_id", "wbraid"
]);

function normalizeUrl(urlStr) {
  if (!urlStr) return "";
  try {
    const u = new URL(urlStr.trim());
    u.protocol = u.protocol.toLowerCase();
    u.hostname = u.hostname.toLowerCase();
    u.hash = "";

    for (const key of [...u.searchParams.keys()]) {
      if (TRACKING_PARAMS.has(key.toLowerCase())) {
        u.searchParams.delete(key);
      }
    }

    if (u.pathname.length > 1 && u.pathname.endsWith("/")) {
      u.pathname = u.pathname.slice(0, -1);
    }

    return u.toString();
  } catch {
    return urlStr.trim();
  }
}

function deduplicateAndMergeResults(rawResults, maxHighlights = 3) {
  const map = new Map();

  for (const item of rawResults) {
    if (!item.title || !item.url) continue;

    const normalizedKey = normalizeUrl(item.url);
    if (!normalizedKey) continue;

    if (!map.has(normalizedKey)) {
      map.set(normalizedKey, {
        title: item.title.slice(0, 100),
        url: normalizedKey,
        published: item.published || "N/A",
        highlights: (item.highlights || []).slice(0, maxHighlights).map(h => typeof h === "string" ? h.slice(0, 200) : h)
      });
    } else {
      const existing = map.get(normalizedKey);

      if ((existing.published === "N/A" || !existing.published) && item.published && item.published !== "N/A") {
        existing.published = item.published;
      }

      if (existing.title.length < item.title.length && item.title.length <= 100) {
        existing.title = item.title;
      }

      const currentHls = new Set(existing.highlights.map(h => h.trim().toLowerCase()));
      for (const hl of item.highlights || []) {
        const trimmed = hl.trim();
        if (trimmed && !currentHls.has(trimmed.toLowerCase()) && existing.highlights.length < maxHighlights) {
          existing.highlights.push(trimmed.slice(0, 200));
          currentHls.add(trimmed.toLowerCase());
        }
      }
    }
  }

  return Array.from(map.values());
}

async function callMcpTool(toolName, args, apiKey) {
  let url = MCP_URL;
  if (apiKey) {
    url += `?exaApiKey=${encodeURIComponent(apiKey)}`;
  }

  const payload = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: toolName,
      arguments: args
    }
  };

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream",
      "User-Agent": USER_AGENT
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`MCP request failed with status ${res.status}: ${res.statusText}`);
  }

  const text = await res.text();
  const textBlocks = [];

  for (const line of text.split("\n")) {
    if (line.startsWith("data: ")) {
      try {
        const obj = JSON.parse(line.slice(6));
        if (obj.error) {
          throw new Error(obj.error.message || "MCP RPC Error");
        }
        if (obj.result) {
          if (obj.result.isError) {
            const errDetail = Array.isArray(obj.result.content)
              ? obj.result.content.map(c => c.text).filter(Boolean).join(" ")
              : "MCP execution returned error";
            throw new Error(errDetail);
          }
          if (Array.isArray(obj.result.content)) {
            for (const item of obj.result.content) {
              if (item.type === "text" && item.text) {
                textBlocks.push(item.text);
              }
            }
          }
        }
      } catch (err) {
        if (err.message && (err.message.includes("rate limit") || err.message.includes("MCP"))) {
          throw err;
        }
      }
    }
  }

  return textBlocks;
}

function parseSearchBlocks(textBlocks, maxHighlights = 3) {
  const rawResults = [];
  const fullText = textBlocks.join("\n\n");
  const blocks = fullText
    .split(/(?:\n\s*---\s*\n|(?=(?:\n|^)Title:\s*))/)
    .map(b => b.trim())
    .filter(b => b.startsWith("Title:"));

  for (const block of blocks) {
    const lines = block.split("\n");
    let title = "";
    let url = "";
    let pub = "";
    const highlights = [];
    let inHighlights = false;

    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith("Title:")) {
        title = trimmedLine.replace(/^Title:\s*/, "").trim().slice(0, 100);
      } else if (trimmedLine.startsWith("URL:")) {
        url = normalizeUrl(trimmedLine.replace(/^URL:\s*/, "").trim());
      } else if (trimmedLine.startsWith("Published:")) {
        const val = trimmedLine.replace(/^Published:\s*/, "").trim();
        if (val && val !== "N/A") pub = val;
      } else if (trimmedLine.startsWith("Author:")) {
        continue;
      } else if (trimmedLine.startsWith("Highlights:")) {
        inHighlights = true;
        const hl = trimmedLine.replace(/^Highlights:\s*/, "").trim();
        if (hl && highlights.length < maxHighlights) {
          highlights.push(hl.slice(0, 200));
        }
      } else if (inHighlights) {
        if (trimmedLine.startsWith("...") || trimmedLine === "---") continue;
        if (trimmedLine.length > 0 && highlights.length < maxHighlights) {
          highlights.push(trimmedLine.slice(0, 200));
        }
      }
    }

    if (title && url) {
      rawResults.push({
        title,
        url,
        published: pub || "N/A",
        highlights: highlights.slice(0, maxHighlights)
      });
    }
  }

  return deduplicateAndMergeResults(rawResults, maxHighlights);
}

export async function webSearch(query, numResults = 10, category = null) {
  const apiKey = process.env.EXA_API_KEY;
  const args = { query, objective: query, numResults };
  if (category) args.category = category;

  const blocks = await callMcpTool("web_search_exa", args, apiKey);
  return parseSearchBlocks(blocks);
}

export async function webFetch(url, maxChars = 4000) {
  const apiKey = process.env.EXA_API_KEY;
  const cleanedUrl = normalizeUrl(url);
  const blocks = await callMcpTool("web_fetch_exa", { urls: [cleanedUrl] }, apiKey);
  const content = blocks.join("\n\n").trim();

  return {
    url: cleanedUrl,
    content: content.slice(0, maxChars),
    truncated: content.length > maxChars,
    total_chars: content.length
  };
}

export async function deepSearch(query, numResults = 10, searchType = "deep", category = null, additionalQueries = []) {
  const apiKey = process.env.EXA_API_KEY;

  if (apiKey) {
    const payload = {
      query,
      type: searchType,
      numResults,
      contents: { highlights: true }
    };
    if (category) payload.category = category;
    if (additionalQueries && additionalQueries.length > 0) {
      payload.additionalQueries = additionalQueries.slice(0, 5);
    }

    try {
      const res = await fetch(REST_SEARCH_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
          "User-Agent": USER_AGENT
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        const rawResults = (data.results || []).map((item) => ({
          title: (item.title || "").slice(0, 100),
          url: normalizeUrl(item.url || ""),
          published: item.publishedDate || "N/A",
          highlights: (item.highlights || []).slice(0, 3).map((h) => h.slice(0, 200))
        }));

        return {
          mode: "api_deep_search",
          query,
          results: deduplicateAndMergeResults(rawResults)
        };
      }
    } catch (e) {
      process.stderr.write(`Deep search API error: ${e.message}, falling back to multi-search MCP\n`);
    }
  }

  const queries = [query, ...additionalQueries].slice(0, 4);
  const rawResults = [];

  for (const q of queries) {
    const res = await webSearch(q, Math.max(3, Math.floor(numResults / queries.length)), category);
    rawResults.push(...res);
  }

  const merged = deduplicateAndMergeResults(rawResults);

  return {
    mode: "mcp_multi_search_fallback",
    queries,
    results: merged.slice(0, numResults)
  };
}

// CLI Execution Entrypoint
const [, , cmd, ...args] = process.argv;

if (cmd) {
  try {
    if (cmd === "search" || cmd === "web_search_exa") {
      const query = args[0] || "top news today";
      const num = parseInt(args[1], 10) || 10;
      const cat = args[2] || null;
      const res = await webSearch(query, num, cat);
      console.log(JSON.stringify(res));
    } else if (cmd === "fetch" || cmd === "web_fetch_exa") {
      const url = args[0];
      if (!url) {
        process.stderr.write("Error: URL required for fetch\n");
        process.exit(1);
      }
      const maxChars = parseInt(args[1], 10) || 4000;
      const res = await webFetch(url, maxChars);
      console.log(JSON.stringify(res));
    } else if (cmd === "deep" || cmd === "deep_search_exa") {
      const query = args[0] || "technology trends";
      const num = parseInt(args[1], 10) || 10;
      const searchType = args[2] || "deep";
      const extra = args[3] ? args[3].split(";") : [];
      const res = await deepSearch(query, num, searchType, null, extra);
      console.log(JSON.stringify(res));
    } else {
      process.stderr.write(`Unknown command: ${cmd}\n`);
      process.exit(1);
    }
  } catch (err) {
    process.stderr.write(`Error: ${err.message}\n`);
    process.exit(1);
  }
}
