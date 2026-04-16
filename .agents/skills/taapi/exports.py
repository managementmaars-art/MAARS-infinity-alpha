"""
TaAPI skill exports — tool names match SKILL.md frontmatter.

Usage in task scripts:
    from core.skill_tools import taapi
    rsi = taapi.indicator(name="rsi", exchange="binance", symbol="BTC/USDT", interval="1h")
    sr = taapi.support_resistance(exchange="binance", symbol="BTC/USDT", interval="1d")
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

from indicators import get_indicator
from support_resistance import get_support_resistance


def indicator(name, symbol, interval, exchange="binance", backtrack=0, backtracks=None):
    """Get technical analysis indicator (RSI, MACD, Bollinger Bands, etc.)."""
    return get_indicator(
        indicator=name,
        exchange=exchange,
        symbol=symbol,
        interval=interval,
        backtrack=backtrack,
        backtracks=backtracks,
    )


def support_resistance(symbol, interval, exchange="binance", indicator_type="pivots"):
    """Get support and resistance levels."""
    return get_support_resistance(
        exchange=exchange,
        symbol=symbol,
        interval=interval,
        indicator=indicator_type,
    )
