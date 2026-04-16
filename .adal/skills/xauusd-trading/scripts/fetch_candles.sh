#!/bin/bash
# Fetch XAUUSD candle history from Twelve Data API (REAL-TIME, no delay)
# Usage: ./fetch_candles.sh [interval] [count] [api_key]
# Example: ./fetch_candles.sh 5min 30
#
# Requires: Free API key from https://twelvedata.com (800 requests/day)
# Set via: export TWELVE_DATA_API_KEY="your_key"

INTERVAL="${1:-5min}"
COUNT="${2:-30}"
API_KEY="${3:-$TWELVE_DATA_API_KEY}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: No API key. Set TWELVE_DATA_API_KEY or pass as 3rd argument."
  echo "Get free key: https://twelvedata.com/pricing (800 req/day, free forever)"
  exit 1
fi

curl -s "https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=${INTERVAL}&outputsize=${COUNT}&apikey=${API_KEY}" \
  2>/dev/null | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
    
    if data.get('code') == 401 or data.get('status') == 'error':
        print(f'API Error: {data.get(\"message\", \"Unknown error\")}')
        sys.exit(1)
    
    if 'values' not in data:
        print(f'No data returned: {json.dumps(data)[:200]}')
        sys.exit(1)
    
    values = data['values']
    meta = data.get('meta', {})
    
    print('=' * 70)
    print(f'XAU/USD {meta.get(\"interval\",\"?\")} - Last {len(values)} Candles (REAL-TIME)')
    print('=' * 70)
    print(f'{\"Datetime\":<20} {\"Open\":>10} {\"High\":>10} {\"Low\":>10} {\"Close\":>10}')
    print('-' * 70)
    
    for v in reversed(values):
        dt = v['datetime']
        o, h, l, c = float(v['open']), float(v['high']), float(v['low']), float(v['close'])
        print(f'{dt:<20} {o:>10.2f} {h:>10.2f} {l:>10.2f} {c:>10.2f}')
    
    latest = values[0]
    oldest = values[-1]
    all_highs = [float(v['high']) for v in values]
    all_lows = [float(v['low']) for v in values]
    all_closes = [float(v['close']) for v in values]
    
    current = float(latest['close'])
    prev = float(values[1]['close']) if len(values) > 1 else current
    change = current - prev
    change_pct = (change / prev) * 100
    
    print('-' * 70)
    print(f'Current: \${current:.2f}  Change: \${change:+.2f} ({change_pct:+.2f}%)')
    print(f'Period High: \${max(all_highs):.2f}  Period Low: \${min(all_lows):.2f}')
    print('=' * 70)

except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
