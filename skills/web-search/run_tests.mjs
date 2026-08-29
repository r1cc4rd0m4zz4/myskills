#!/usr/bin/env node
/**
 * Test Suite for web-search skill.
 * Zero-dependency unit tests using native Node.js test runner & assert (Node 18+).
 */

import assert from "node:assert";

// Import helper functions from exa_tool.mjs (or recreate deterministic mocks)
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

// ── Test Runner ─────────────────────────────────────────────────────────────
let passed = 0;
let failed = 0;

function runTest(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
    failed++;
  }
}

console.log("======================================================================");
console.log("  web-search — Test Suite (Node.js native assert)");
console.log("======================================================================");

// 1. URL Normalization Tests
runTest("URL Normalization: strips utm tracking params", () => {
  const input = "https://example.com/blog/article?utm_source=twitter&utm_medium=social&utm_campaign=launch";
  const expected = "https://example.com/blog/article";
  assert.strictEqual(normalizeUrl(input), expected);
});

runTest("URL Normalization: strips click tracking IDs (gclid, fbclid, ref)", () => {
  const input = "https://example.com/product?gclid=12345&fbclid=abcde&ref=ad_campaign&valid_param=keep_me";
  const expected = "https://example.com/product?valid_param=keep_me";
  assert.strictEqual(normalizeUrl(input), expected);
});

runTest("URL Normalization: normalizes trailing slash on pathnames", () => {
  const input = "https://example.com/docs/api/";
  const expected = "https://example.com/docs/api";
  assert.strictEqual(normalizeUrl(input), expected);
});

runTest("URL Normalization: preserves root trailing slash", () => {
  const input = "https://example.com/";
  const expected = "https://example.com/";
  assert.strictEqual(normalizeUrl(input), expected);
});

runTest("URL Normalization: lowercases protocol and domain", () => {
  const input = "HTTPS://WWW.Example.COM/Path";
  const expected = "https://www.example.com/Path";
  assert.strictEqual(normalizeUrl(input), expected);
});

// 2. Parsing Multi-Result Stream Blocks
runTest("Parsing: parses multi-item text blocks separated by '---'", () => {
  const block = `Title: First Search Result
URL: https://example.com/item1
Published: 2026-08-01
Highlights:
Key point 1
...
Key point 2

---

Title: Second Search Result
URL: https://example.com/item2
Published: N/A
Highlights:
Important excerpt`;

  const parsed = parseSearchBlocks([block], 3);
  assert.strictEqual(parsed.length, 2);
  assert.strictEqual(parsed[0].title, "First Search Result");
  assert.strictEqual(parsed[0].url, "https://example.com/item1");
  assert.strictEqual(parsed[0].published, "2026-08-01");
  assert.strictEqual(parsed[0].highlights.length, 2);
  assert.strictEqual(parsed[1].title, "Second Search Result");
});

// 3. Deduplication and Merge Logic
runTest("Deduplication: merges items with identical normalized URL", () => {
  const raw = [
    {
      title: "Short Title",
      url: "https://example.com/item?utm_source=twitter",
      published: "N/A",
      highlights: ["Highlight A"]
    },
    {
      title: "More Descriptive Longer Title",
      url: "https://example.com/item",
      published: "2026-08-20",
      highlights: ["Highlight B"]
    }
  ];

  const merged = deduplicateAndMergeResults(raw, 3);
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(merged[0].url, "https://example.com/item");
  assert.strictEqual(merged[0].title, "More Descriptive Longer Title");
  assert.strictEqual(merged[0].published, "2026-08-20");
  assert.deepStrictEqual(merged[0].highlights, ["Highlight A", "Highlight B"]);
});

// 4. Token Truncation & Constraints
runTest("Compaction: enforces title max length 100 and highlight max length 200", () => {
  const longTitle = "A".repeat(150);
  const longHl = "B".repeat(250);
  const raw = [{ title: longTitle, url: "https://example.com", highlights: [longHl] }];
  const res = deduplicateAndMergeResults(raw, 3);
  assert.strictEqual(res[0].title.length, 100);
  assert.strictEqual(res[0].highlights[0].length, 200);
});

console.log("======================================================================");
if (failed > 0) {
  console.error(`  ❌ ${failed} test falliti (${passed} passati)`);
  process.exit(1);
} else {
  console.log(`  ✅ ${passed} test passati con successo (100%)`);
}
