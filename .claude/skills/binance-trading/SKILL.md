---
name: binance-trading
description: Binance API for spot trading, market data, WebSocket streams, order management, and account monitoring.
---

# Binance Trading API

## Overview

Binance provides REST and WebSocket APIs for spot trading, futures, market data, and account management. Always test with the testnet before live trading.

## Installation & Setup

```bash
pip install python-binance
npm install @binance/connector
```

```python
from binance.client import Client
from binance.enums import *
import os

# Testnet for development
client = Client(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
    testnet=True,   # Use testnet! Remove for production
)

# Production
client = Client(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
)
```

## Market Data

```python
# Get current price
price = client.get_symbol_ticker(symbol="BTCUSDT")
print(f"BTC Price: ${price['price']}")

# Get order book (depth)
depth = client.get_order_book(symbol="BTCUSDT", limit=20)
bids = depth["bids"]   # [[price, quantity], ...]
asks = depth["asks"]

best_bid = float(bids[0][0])
best_ask = float(asks[0][0])
spread = best_ask - best_bid

# Get recent trades
trades = client.get_recent_trades(symbol="BTCUSDT", limit=100)

# Get klines (candlestick data)
klines = client.get_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1HOUR,
    limit=500,
)

# Parse klines into usable format
import pandas as pd

def klines_to_df(klines) -> pd.DataFrame:
    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore",
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df.set_index("open_time", inplace=True)
    return df

df = klines_to_df(klines)
df["sma_20"] = df["close"].rolling(20).mean()
df["rsi"] = compute_rsi(df["close"])

# Get 24hr ticker stats
ticker = client.get_ticker(symbol="BTCUSDT")
print(f"24h change: {ticker['priceChangePercent']}%")
print(f"24h volume: {ticker['quoteVolume']}")
print(f"24h high: {ticker['highPrice']}, low: {ticker['lowPrice']}")

# Get all tickers (for screener)
all_tickers = client.get_all_tickers()
usdt_pairs = [t for t in all_tickers if t["symbol"].endswith("USDT")]
```

## Order Management

```python
from decimal import Decimal
import math

def get_lot_size_info(symbol: str) -> dict:
    """Get precision requirements for a symbol."""
    info = client.get_symbol_info(symbol)
    filters = {f["filterType"]: f for f in info["filters"]}

    lot_size = filters.get("LOT_SIZE", {})
    price_filter = filters.get("PRICE_FILTER", {})

    return {
        "min_qty": float(lot_size.get("minQty", 0)),
        "max_qty": float(lot_size.get("maxQty", 0)),
        "step_size": float(lot_size.get("stepSize", 0)),
        "min_price": float(price_filter.get("minPrice", 0)),
        "tick_size": float(price_filter.get("tickSize", 0)),
    }

def round_step_size(quantity: float, step_size: float) -> float:
    """Round quantity to valid step size."""
    precision = int(round(-math.log(step_size, 10), 0))
    return round(quantity, precision)

# Market order (buy immediately at market price)
def market_buy(symbol: str, usdt_amount: float) -> dict:
    return client.order_market_buy(
        symbol=symbol,
        quoteOrderQty=usdt_amount,   # Spend exactly this much USDT
    )

def market_sell(symbol: str, quantity: float) -> dict:
    info = get_lot_size_info(symbol)
    qty = round_step_size(quantity, info["step_size"])
    return client.order_market_sell(symbol=symbol, quantity=qty)

# Limit order
def limit_buy(symbol: str, quantity: float, price: float) -> dict:
    info = get_lot_size_info(symbol)
    qty = round_step_size(quantity, info["step_size"])

    return client.order_limit_buy(
        symbol=symbol,
        quantity=qty,
        price=str(round(price, 2)),
    )

# Stop-loss limit order
def stop_loss_limit(symbol: str, quantity: float, stop_price: float, limit_price: float) -> dict:
    return client.create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=ORDER_TYPE_STOP_LOSS_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        stopPrice=str(stop_price),
        price=str(limit_price),
    )

# OCO order (One-Cancels-the-Other: take profit + stop loss)
def oco_sell(symbol: str, quantity: float, take_profit: float, stop_price: float, stop_limit: float) -> dict:
    return client.create_oco_order(
        symbol=symbol,
        side=SIDE_SELL,
        quantity=quantity,
        price=str(take_profit),     # Take profit limit
        stopPrice=str(stop_price),  # Stop trigger
        stopLimitPrice=str(stop_limit),
        stopLimitTimeInForce=TIME_IN_FORCE_GTC,
    )

# Cancel order
client.cancel_order(symbol="BTCUSDT", orderId=12345678)

# Get all open orders
open_orders = client.get_open_orders(symbol="BTCUSDT")

# Get order history
orders = client.get_all_orders(symbol="BTCUSDT", limit=100)
```

## Account Management

```python
# Get account balances
def get_balances() -> dict:
    account = client.get_account()
    return {
        asset["asset"]: {
            "free": float(asset["free"]),
            "locked": float(asset["locked"]),
        }
        for asset in account["balances"]
        if float(asset["free"]) > 0 or float(asset["locked"]) > 0
    }

# Get trade history
trades = client.get_my_trades(symbol="BTCUSDT", limit=100)
for trade in trades:
    pnl = float(trade["price"]) * float(trade["qty"]) * (1 if trade["isBuyer"] else -1)
    print(f"{'Buy' if trade['isBuyer'] else 'Sell'} {trade['qty']} BTC @ {trade['price']}")
```

## WebSocket Streams

```python
from binance import ThreadedWebsocketManager

twm = ThreadedWebsocketManager(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_API_SECRET"),
)
twm.start()

# Real-time price ticker
def handle_ticker(msg):
    if msg["e"] == "error":
        print(f"Error: {msg['m']}")
        return
    print(f"BTC: ${msg['c']} | 24h: {msg['P']}%")

twm.start_symbol_ticker_socket(callback=handle_ticker, symbol="BTCUSDT")

# Real-time kline updates
def handle_kline(msg):
    k = msg["k"]
    if k["x"]:  # Candle is closed
        print(f"Closed candle: O={k['o']} H={k['h']} L={k['l']} C={k['c']} V={k['v']}")

twm.start_kline_socket(callback=handle_kline, symbol="BTCUSDT", interval="1m")

# Order book depth stream
def handle_depth(msg):
    bids = msg["bids"][:5]
    asks = msg["asks"][:5]
    # Update local order book

twm.start_depth_socket(callback=handle_depth, symbol="BTCUSDT", depth=20)

# User data stream (orders, trades, balance updates)
def handle_user_data(msg):
    if msg["e"] == "executionReport":
        order_id = msg["i"]
        status = msg["X"]   # NEW, PARTIALLY_FILLED, FILLED, CANCELED
        symbol = msg["s"]
        side = msg["S"]
        price = msg["p"]
        qty = msg["q"]
        print(f"Order {order_id}: {side} {qty} {symbol} @ {price} -> {status}")

    elif msg["e"] == "outboundAccountPosition":
        balances = msg["B"]
        for b in balances:
            print(f"{b['a']}: {b['f']} free, {b['l']} locked")

twm.start_user_socket(callback=handle_user_data)

# Cleanup
import time
time.sleep(60)
twm.stop()
```

## Simple Trading Bot Pattern

```python
import time
from dataclasses import dataclass

@dataclass
class TradingConfig:
    symbol: str = "BTCUSDT"
    trade_amount_usdt: float = 100.0
    sma_fast: int = 10
    sma_slow: int = 30
    stop_loss_pct: float = 0.02    # 2%
    take_profit_pct: float = 0.04  # 4%

class SimpleBot:
    def __init__(self, config: TradingConfig):
        self.config = config
        self.client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_API_SECRET"), testnet=True)
        self.position = None

    def get_signal(self) -> str:
        klines = self.client.get_klines(symbol=self.config.symbol, interval="1h", limit=50)
        df = klines_to_df(klines)
        df["sma_fast"] = df["close"].rolling(self.config.sma_fast).mean()
        df["sma_slow"] = df["close"].rolling(self.config.sma_slow).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Golden cross = buy, death cross = sell
        if prev["sma_fast"] <= prev["sma_slow"] and latest["sma_fast"] > latest["sma_slow"]:
            return "BUY"
        elif prev["sma_fast"] >= prev["sma_slow"] and latest["sma_fast"] < latest["sma_slow"]:
            return "SELL"
        return "HOLD"

    def run(self):
        while True:
            signal = self.get_signal()
            if signal == "BUY" and not self.position:
                order = market_buy(self.config.symbol, self.config.trade_amount_usdt)
                self.position = order
                print(f"Bought: {order}")
            elif signal == "SELL" and self.position:
                order = market_sell(self.config.symbol, float(self.position["executedQty"]))
                self.position = None
                print(f"Sold: {order}")
            time.sleep(60)
```

## Key Patterns

- **Always use testnet** for development and paper trading before going live
- **Handle lot size precision** — Binance will reject orders with incorrect quantity precision
- **OCO orders** automate both take-profit and stop-loss in a single API call
- **WebSocket for real-time** — polling REST for prices adds latency and hits rate limits
- **User data stream** is essential for tracking order fills without polling
- **Rate limits**: 1200 weight/min for REST; WebSocket streams have lower overhead

## Models to Use

- **claude-opus-4-5**: Complex trading strategies, risk management systems, backtesting frameworks
- **claude-sonnet-4-5**: Order management, WebSocket bots, indicator implementation
- **claude-haiku-3-5**: Simple price checks, balance queries, order status
