#!/bin/bash
# Fetch REAL-TIME XAUUSD data from TradingView scanner API
# Usage: ./fetch_price.sh
# No API key needed. Returns live price + 5m/15m/1h indicators. ALL REAL-TIME.

curl -s "https://scanner.tradingview.com/cfd/scan" \
  -H "Content-Type: application/json" \
  -d '{"symbols":{"tickers":["TVC:GOLD"],"query":{"types":[]}},"columns":["close","open","high","low","change","change_abs","Recommend.All","close|5","open|5","high|5","low|5","RSI|5","EMA5|5","EMA10|5","EMA20|5","MACD.macd|5","MACD.signal|5","MACD.hist|5","Stoch.K|5","Stoch.D|5","BB.upper|5","BB.lower|5","ATR|5","ADX|5","ADX-DI|5","ADX+DI|5","CCI20|5","Mom|5","close|15","open|15","high|15","low|15","RSI|15","EMA5|15","EMA10|15","EMA20|15","MACD.macd|15","MACD.signal|15","MACD.hist|15","Stoch.K|15","Stoch.D|15","BB.upper|15","BB.lower|15","ATR|15","ADX|15","ADX-DI|15","ADX+DI|15","CCI20|15","close|60","open|60","high|60","low|60","RSI|60","EMA5|60","EMA10|60","EMA20|60","MACD.macd|60","MACD.signal|60","MACD.hist|60","BB.upper|60","BB.lower|60","ATR|60"]}' \
  2>/dev/null | python3 -c "
import sys, json
from datetime import datetime

def f(v):
    return f'{v:.2f}' if v is not None else 'N/A'
def f1(v):
    return f'{v:.1f}' if v is not None else 'N/A'

try:
    data = json.load(sys.stdin)
    if not data.get('data'):
        print('ERROR: No data returned. Market may be closed.')
        sys.exit(1)
    
    r = data['data'][0]['d']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Daily
    close, opn, high, low = r[0], r[1], r[2], r[3]
    change_pct, change_abs = r[4], r[5]
    rec = r[6]
    
    print('=' * 60)
    print(f'  XAUUSD LIVE | {now}')
    print('=' * 60)
    print(f'  Price:  \${f(close)}   Change: {f1(change_pct)}% (\${f(change_abs)})')
    print(f'  Day:    O={f(opn)} H={f(high)} L={f(low)}')
    
    if rec is not None:
        if rec >= 0.5: tag = 'STRONG BUY'
        elif rec >= 0.1: tag = 'BUY'
        elif rec > -0.1: tag = 'NEUTRAL'
        elif rec > -0.5: tag = 'SELL'
        else: tag = 'STRONG SELL'
        print(f'  TV Rec: {tag} ({rec:+.2f})')
    
    # 5-MINUTE
    print()
    print('-' * 60)
    print('  5-MINUTE (real-time)')
    print('-' * 60)
    print(f'  Candle: O={f(r[8])} H={f(r[9])} L={f(r[10])} C={f(r[7])}')
    print(f'  RSI:    {f1(r[11])}')
    print(f'  EMA:    5={f(r[12])} 10={f(r[13])} 20={f(r[14])}')
    print(f'  MACD:   {f(r[15])} Sig={f(r[16])} Hist={f(r[17])}')
    print(f'  Stoch:  K={f1(r[18])} D={f1(r[19])}')
    print(f'  BB:     Up={f(r[20])} Low={f(r[21])}')
    print(f'  ATR:    {f(r[22])}   ADX: {f1(r[23])} (-DI:{f1(r[24])} +DI:{f1(r[25])})')
    print(f'  CCI:    {f1(r[26])}   Mom: {f(r[27])}')
    
    # 15-MINUTE
    print()
    print('-' * 60)
    print('  15-MINUTE (real-time)')
    print('-' * 60)
    print(f'  Candle: O={f(r[29])} H={f(r[30])} L={f(r[31])} C={f(r[28])}')
    print(f'  RSI:    {f1(r[32])}')
    print(f'  EMA:    5={f(r[33])} 10={f(r[34])} 20={f(r[35])}')
    print(f'  MACD:   {f(r[36])} Sig={f(r[37])} Hist={f(r[38])}')
    print(f'  Stoch:  K={f1(r[39])} D={f1(r[40])}')
    print(f'  BB:     Up={f(r[41])} Low={f(r[42])}')
    print(f'  ATR:    {f(r[43])}   ADX: {f1(r[44])} (-DI:{f1(r[45])} +DI:{f1(r[46])})')
    print(f'  CCI:    {f1(r[47])}')
    
    # 1-HOUR
    print()
    print('-' * 60)
    print('  1-HOUR (real-time)')
    print('-' * 60)
    print(f'  Candle: O={f(r[49])} H={f(r[50])} L={f(r[51])} C={f(r[48])}')
    print(f'  RSI:    {f1(r[52])}')
    print(f'  EMA:    5={f(r[53])} 10={f(r[54])} 20={f(r[55])}')
    print(f'  MACD:   {f(r[56])} Sig={f(r[57])} Hist={f(r[58])}')
    print(f'  BB:     Up={f(r[59])} Low={f(r[60])}')
    print(f'  ATR:    {f(r[61])}')
    
    print('=' * 60)

except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
