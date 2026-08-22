#!/usr/bin/env node
/**
 * Exa Tool Runner for web-search skill.
 * Zero-dependency standalone ES Module (Node 18+).
 * Works across macOS, Ubuntu, WSL2 without package.json or npm install.
 */

const MCP_URL = "https://mcp.exa.ai/mcp";
const REST_SEARCH_URL = "https://api.exa.ai/search";
const USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)";
const TRACKING_PARAMS = new Set([
  "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
  "ref", "refid", "referral", "source", "srccid", "gclid", "fbclid",
  "igshid", "twclid", "msclkid", "yclid", "wa_id", "wbraid"
]);

function cleanUrl(urlStr) {
  if (!urlStr) return "";
  try {
    const u = new URL(urlStr);
    for (const key of [...u.searchParams.keys()]) {
      if (TRACKING_PARAMS.has(key.toLowerCase())) {
        u.searchParams.delete(key);
      }
    }
    return u.toString();
  } catch {
    return urlStr;
  }
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
        if (obj.result && Array.isArray(obj.result.content)) {
          for (const item of obj.result.content) {
            if (item.type === "text" && item.text) {
              textBlocks.push(item.text);
            }
          }
        }
      } catch {}
    }
  }

  return textBlocks;
}

function parseSearchBlocks(textBlocks, maxHighlights = 3) {
  const results = [];

  for (const block of textBlocks) {
    if (!block.startsWith("Title:")) continue;

    const lines = block.split("\n");
    const title = (lines[0] || "").replace("Title: ", "").trim().slice(0, 100);
    let url = "";
    let pub = "";
    const highlights = [];
    let inHighlights = false;

    for (const line of lines) {
      if (line.startsWith("URL:")) {
        url = cleanUrl(line.replace("URL: ", "").trim());
      } else if (line.startsWith("Published:") && !pub) {
        pub = line.replace("Published: ", "").trim();
      } else if (line.startsWith("Highlights:") && !inHighlights) {
        inHighlights = true;
        const hl = line.replace("Highlights:", "").trim();
        if (hl && highlights.length < maxHighlights) {
          highlights.push(hl.slice(0, 200));
        }
      } else if (inHighlights && line.startsWith("...")) {
        continue;
      } else if (inHighlights && line.trim()) {
        if (highlights.length < maxHighlights) {
          highlights.push(line.trim().slice(0, 200));
        }
        if (highlights.length >= maxHighlights) {
          break;
        }
      }
    }

    if (title && url) {
      results.push({
        title,
        url,
        published: pub || "N/A",
        highlights: highlights.slice(0, maxHighlights)
      });
    }
  }

  return results;
}

export async function webSearch(query, numResults = 10, category = null) {
  const apiKey = process.env.EXA_API_KEY;
  const args = { query, numResults };
  if (category) args.category = category;

  const blocks = await callMcpTool("web_search_exa", args, apiKey);
  return parseSearchBlocks(blocks);
}

export async function webFetch(url, maxChars = 4000) {
  const apiKey = process.env.EXA_API_KEY;
  const cleanedUrl = cleanUrl(url);
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
        const results = (data.results || []).map((item) => ({
          title: (item.title || "").slice(0, 100),
          url: cleanUrl(item.url || ""),
          published: item.publishedDate || "N/A",
          highlights: (item.highlights || []).slice(0, 3).map((h) => h.slice(0, 200))
        }));

        return {
          mode: "api_deep_search",
          query,
          results
        };
      }
    } catch (e) {
      process.stderr.write(`Deep search API error: ${e.message}, falling back to multi-search MCP\n`);
    }
  }

  // Fallback se anonimo o API error: parallel multi-query
  const queries = [query, ...additionalQueries].slice(0, 4);
  const seenUrls = new Set();
  const combinedResults = [];

  for (const q of queries) {
    const res = await webSearch(q, Math.max(3, Math.floor(numResults / queries.length)), category);
    for (const r of res) {
      if (!seenUrls.has(r.url)) {
        seenUrls.add(r.url);
        combinedResults.push(r);
      }
    }
  }

  return {
    mode: "mcp_multi_search_fallback",
    queries,
    results: combinedResults.slice(0, numResults)
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
