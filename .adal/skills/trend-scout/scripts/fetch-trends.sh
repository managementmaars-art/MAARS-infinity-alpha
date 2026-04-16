#!/bin/bash
# fetch-trends.sh — Reddit + Hacker News 인기글 수집
# Usage: bash fetch-trends.sh [day|week] [limit]
# Output: JSON to stdout

PERIOD="${1:-day}"
LIMIT="${2:-10}"
UA="TrendScout/1.0"
OUTDIR="/tmp/trend-scout"
mkdir -p "$OUTDIR"

# ── Reddit ──────────────────────────────────────────
SUBREDDITS="Solopreneur,indiehackers,SaaS,Entrepreneur,ClaudeAI,ChatGPT,nextjs,GeminiAI"

echo "=== Reddit Top Posts (t=$PERIOD, limit=$LIMIT) ===" >&2

IFS=',' read -ra SUBS <<< "$SUBREDDITS"
for SUB in "${SUBS[@]}"; do
  echo "Fetching r/$SUB..." >&2
  curl -sA "$UA" "https://www.reddit.com/r/${SUB}/top.json?t=${PERIOD}&limit=${LIMIT}" \
    > "$OUTDIR/reddit-${SUB}.json" 2>/dev/null
  sleep 1  # rate limit 준수
done

# ── Hacker News ─────────────────────────────────────
echo "=== Hacker News Top Stories ===" >&2
# HN API: top story IDs → 개별 item fetch
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" \
  | python3 -c "import sys,json; ids=json.load(sys.stdin)[:${LIMIT}]; print(json.dumps(ids))" \
  > "$OUTDIR/hn-top-ids.json" 2>/dev/null

# Fetch each story
python3 -c "
import json, urllib.request, sys

with open('$OUTDIR/hn-top-ids.json') as f:
    ids = json.load(f)

stories = []
for sid in ids:
    try:
        url = f'https://hacker-news.firebaseio.com/v0/item/{sid}.json'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            item = json.loads(resp.read())
            if item and item.get('type') == 'story':
                stories.append({
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'url': item.get('url', f'https://news.ycombinator.com/item?id={sid}'),
                    'score': item.get('score', 0),
                    'comments': item.get('descendants', 0),
                    'by': item.get('by', ''),
                    'hn_url': f'https://news.ycombinator.com/item?id={sid}'
                })
    except Exception as e:
        print(f'Error fetching {sid}: {e}', file=sys.stderr)

with open('$OUTDIR/hn-stories.json', 'w') as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)
print(f'Fetched {len(stories)} HN stories', file=sys.stderr)
"

# ── 통합 요약 ───────────────────────────────────────
python3 -c "
import json, glob, os

outdir = '$OUTDIR'
results = {'reddit': {}, 'hackernews': []}

# Parse Reddit
for f in sorted(glob.glob(f'{outdir}/reddit-*.json')):
    sub = os.path.basename(f).replace('reddit-','').replace('.json','')
    try:
        with open(f) as fh:
            data = json.load(fh)
        posts = []
        for child in data.get('data',{}).get('children',[]):
            d = child.get('data',{})
            posts.append({
                'title': d.get('title',''),
                'score': d.get('score',0),
                'comments': d.get('num_comments',0),
                'url': f\"https://reddit.com{d.get('permalink','')}\",
                'author': d.get('author',''),
                'created_utc': d.get('created_utc',0),
                'selftext': (d.get('selftext','') or '')[:300]
            })
        results['reddit'][sub] = posts
    except Exception as e:
        results['reddit'][sub] = {'error': str(e)}

# Parse HN
try:
    with open(f'{outdir}/hn-stories.json') as fh:
        results['hackernews'] = json.load(fh)
except:
    pass

print(json.dumps(results, ensure_ascii=False, indent=2))
"
