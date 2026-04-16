#!/bin/bash
# Fetch XAUUSD (Gold) price data from Yahoo Finance
# Usage: ./fetch_gold.sh [interval] [range] [count]
# Example: ./fetch_gold.sh 1h 5d 30

INTERVAL="${1:-1h}"    # 1m, 5m, 15m, 1h, 1d
RANGE="${2:-5d}"       # 1d, 5d, 1mo, 3mo, 6mo, 1y
COUNT="${3:-30}"       # Number of candles to show

# GC=F is Gold Futures on Yahoo Finance
SYMBOL="GC=F"

curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${SYMBOL}?interval=${INTERVAL}&range=${RANGE}" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  2>/dev/null | python3 -c "
import sys
import json
from datetime import datetime

count = ${COUNT}

try:
    data = json.load(sys.stdin)
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    quote = result['indicators']['quote'][0]
    
    opens = quote['open']
    highs = quote['high']
    lows = quote['low']
    closes = quote['close']
    
    print('=' * 70)
    print(f'GOLD FUTURES (GC=F) - Last {min(count, len(timestamps))} Candles')
    print('=' * 70)
    print(f\"{'Datetime':<20} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10}\")
    print('-' * 70)
    
    for i in range(-min(count, len(timestamps)), 0):
        ts = timestamps[i]
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        
        # Skip if any value is None
        if None in (o, h, l, c):
            continue
            
        dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        print(f'{dt:<20} {o:>10.2f} {h:>10.2f} {l:>10.2f} {c:>10.2f}')
    
    # Summary
    valid_closes = [c for c in closes if c is not None]
    valid_highs = [h for h in highs[-count:] if h is not None]
    valid_lows = [l for l in lows[-count:] if l is not None]
    
    if len(valid_closes) >= 2:
        current = valid_closes[-1]
        prev = valid_closes[-2]
        change = current - prev
        change_pct = (change / prev) * 100
        
        print('-' * 70)
        print(f'Current Price: \${current:.2f}')
        print(f'Change: \${change:+.2f} ({change_pct:+.2f}%)')
        print(f'Period High: \${max(valid_highs):.2f}')
        print(f'Period Low: \${min(valid_lows):.2f}')
        
except Exception as e:
    print(f'Error fetching data: {e}', file=sys.stderr)
    sys.exit(1)
"
