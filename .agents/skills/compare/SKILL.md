---
name: compare
description: Compare sentiment and blogger opinions between two stocks. Use when users want to analyze NVDA vs AMD, or any two tickers side by side.
---

# Stock Comparison

Compare sentiment and blogger opinions between two stocks.

## Triggers

- "对比 NVDA 和 AMD"
- "比较这两只股票"
- "compare NVDA vs AMD"
- "NVDA 和 AMD 哪个好"
- `/compare NVDA AMD`
- `/compare {ticker1} {ticker2}`

## Arguments

- `ticker1` - First stock ticker (required)
- `ticker2` - Second stock ticker (required)

## Instructions

When the user wants to compare two stocks, follow these steps:

1. **Get Sentiment for Both Stocks**
   Call `get_ticker_sentiment` for both tickers in parallel to get sentiment data.

2. **Search for Related Viewpoints**
   Call `search_viewpoints` with each ticker to find detailed blogger opinions.

3. **Analyze and Compare**
   Create a side-by-side comparison covering:
   - Overall sentiment score
   - Number of bullish vs bearish bloggers
   - Key arguments for each side
   - Common themes in viewpoints

4. **Present Results**
   Format the output as:

   ```
   ## 股票对比: TICKER1 vs TICKER2

   | 指标 | TICKER1 | TICKER2 |
   |------|---------|---------|
   | 整体情绪 | 🟢 看涨 | 🟡 中性 |
   | 看涨博主 | X 位 | Y 位 |
   | 看跌博主 | X 位 | Y 位 |
   | 提及次数 | XX | YY |

   ### TICKER1 关键观点
   **看涨理由:**
   - [观点1] — 博主A
   - [观点2] — 博主B

   **风险提示:**
   - [风险1] — 博主C

   ### TICKER2 关键观点
   **看涨理由:**
   - [观点1] — 博主D

   **风险提示:**
   - [风险1] — 博主E

   ### 综合分析
   [基于数据的客观分析，指出两者的优劣势]
   ```

## Tool Sequence

1. `get_ticker_sentiment(ticker1)` + `get_ticker_sentiment(ticker2)` → In parallel
2. `search_viewpoints(ticker1)` + `search_viewpoints(ticker2)` → In parallel
3. Compile comparison table and analysis

## Notes

- Always present data objectively, let users make their own decisions
- Highlight where bloggers disagree
- If one ticker has significantly more coverage, note this caveat
- Do NOT give buy/sell recommendations
