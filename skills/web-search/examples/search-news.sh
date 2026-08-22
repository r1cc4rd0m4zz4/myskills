#!/usr/bin/env bash
# examples/search-news.sh
# Ricerca notizie con Exa (accesso anonimo) — output compattato per minimizzare token

set -e

QUERY="${1:-top news today}"
NUM_RESULTS="${2:-10}"
ID="${3:-1}"

curl -s -X POST "https://mcp.exa.ai/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": $ID,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"web_search_exa\",
      \"arguments\": {
        \"query\": \"$QUERY\",
        \"numResults\": $NUM_RESULTS
      }
    }
  }" | python3 -c "
import sys, json, re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

data = sys.stdin.read()
results = []
block = []

def strip_tracking(url):
    \"\"\"Rimuove solo i parametri di tracking/telemetria, mantiene URL intatto.\"\"\"
    try:
        parsed = urlparse(url)
        # Parametri di tracking comuni da rimuovere
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                          'ref', 'refid', 'referral', 'source', 'srccid', 'gclid', 'fbclid',
                          'igshid', 'twclid', 'msclkid', 'yclid', 'wa_id', 'wbraid'}
        query = parse_qs(parsed.query, keep_blank_values=True)
        # Filtra solo i parametri di tracking
        clean_query = {k: v for k, v in query.items() if k.lower() not in tracking_params}
        clean_url = urlunparse(parsed._replace(query=urlencode(clean_query, doseq=True)))
        return clean_url
    except:
        return url

def process_block(text):
    if not text.startswith('Title:'):
        return
    lines = text.split('\\n')
    title = lines[0].replace('Title: ', '').strip()[:100]
    url = ''
    pub = ''
    highlights = []
    in_highlights = False
    for l in lines:
        if l.startswith('URL:'):
            raw_url = l.replace('URL: ', '').strip()
            url = strip_tracking(raw_url)  # Pulisci solo tracking params
        elif l.startswith('Published:') and not pub:
            pub = l.replace('Published: ', '').strip()
        elif l.startswith('Highlights:') and not in_highlights:
            in_highlights = True
            hl = l.replace('Highlights:', '').strip()
            if hl and len(highlights) < 3:
                highlights.append(hl[:200])
        elif in_highlights and l.startswith('...'):
            continue
        elif in_highlights and l.strip():
            if len(highlights) < 3:
                highlights.append(l.strip()[:200])
            if len(highlights) >= 3:
                break
    if title and url:
        results.append({
            'title': title,
            'url': url,
            'published': pub,
            'highlights': highlights[:3]
        })

for line in data.split('\\n'):
    if line.startswith('data: '):
        try:
            obj = json.loads(line[6:])
            if 'result' in obj:
                content = obj['result']['content']
                for c in content:
                    if c.get('type') == 'text':
                        block.append(c['text'])
        except:
            pass

for b in block:
    process_block(b)

# Output: JSON minimale, no indent, no campi vuoti
compact = [r for r in results if r['title'] and r['url']]
print(json.dumps(compact, separators=(',', ':')))
"
