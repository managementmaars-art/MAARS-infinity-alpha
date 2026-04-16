---
name: sentiment-shift
description: Identify stocks where blogger sentiment has changed significantly. Use when users want to find who changed their mind or detect sentiment reversals.
---

# Sentiment Shift Detector

Identify stocks where blogger sentiment has changed significantly.

## Triggers

- "情绪变化最大的股票"
- "谁转向了"
- "sentiment shift"
- "who changed their mind"
- "态度转变"
- `/sentiment-shift`

## Instructions

When the user wants to find sentiment shifts, follow these steps:

1. **Get Multi-Day Summaries**
   Call `get_daily_summary` for recent dates (today, yesterday, a few days ago) to compare sentiment over time.

2. **Identify Changed Tickers**
   Compare the summaries to find:
   - Stocks that moved from bullish to bearish
   - Stocks that moved from bearish to bullish
   - Stocks with increased/decreased mentions

3. **Get Detailed Sentiment**
   For tickers with notable changes, call `get_ticker_sentiment` to understand who changed their view.

4. **Search for Explanations**
   Call `search_viewpoints` for changed tickers to find the reasoning behind sentiment shifts.

5. **Present Results**
   Format the output as:

   ```
   ## 情绪转变追踪 🔄

   ### 转向看涨 📈

   #### TICKER1
   - **变化**: 看跌 → 看涨
   - **时间**: X天前开始转变
   - **关键转变博主**: 博主A, 博主B
   - **转变原因**: [摘要为什么改变看法]
   - **代表观点**: "[具体观点]" — 博主A

   ### 转向看跌 📉

   #### TICKER2
   - **变化**: 看涨 → 看跌
   - **时间**: X天前开始转变
   - **关键转变博主**: 博主C
   - **转变原因**: [摘要为什么改变看法]
   - **代表观点**: "[具体观点]" — 博主C

   ### 热度变化 🌡️

   | 股票 | 之前提及 | 现在提及 | 变化 |
   |------|----------|----------|------|
   | XXX | 5 | 25 | ⬆️ +400% |
   | YYY | 20 | 3 | ⬇️ -85% |

   ### 分析
   [总结市场情绪变化的整体趋势]
   ```

## Tool Sequence

1. `get_daily_summary(date=today)` + `get_daily_summary(date=yesterday)` + `get_daily_summary(date=3_days_ago)` → Compare over time
2. Identify tickers with changed sentiment
3. `get_ticker_sentiment(changed_ticker)` → For each changed ticker
4. `search_viewpoints(changed_ticker)` → Find reasoning
5. Compile shift analysis

## Notes

- Sentiment shifts can be leading indicators
- A blogger changing their view is often more significant than new bloggers joining
- Track both direction changes and intensity changes
- Include context for why shifts happened (news, earnings, etc.)
