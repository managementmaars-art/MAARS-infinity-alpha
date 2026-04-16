"""Unit tests for technical analysis module."""
import pytest
import pandas as pd
import numpy as np
from analysis.technical import compute_technical


class TestComputeTechnical:
    def _make_kline_df(self, rows=30, start_price=10.0, daily_return=0.01):
        """Helper: 生成模拟K线数据."""
        dates = pd.date_range("2026-01-01", periods=rows, freq="B")
        prices = [start_price]
        for i in range(1, rows):
            prices.append(prices[-1] * (1 + daily_return + np.random.uniform(-0.02, 0.02)))
        df = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "open": [p * 0.99 for p in prices],
            "high": [p * 1.02 for p in prices],
            "low": [p * 0.98 for p in prices],
            "close": prices,
            "volume": [1000000 + np.random.randint(-200000, 200000) for _ in range(rows)],
        })
        return df

    def test_basic_output_structure(self):
        """基础输出结构验证."""
        df = self._make_kline_df()
        result = compute_technical(df)
        assert hasattr(result, "score")
        assert hasattr(result, "signals")
        assert hasattr(result, "indicators")
        assert 0 <= result.score <= 100

    def test_insufficient_data(self):
        """数据不足时返回中性评分."""
        df = self._make_kline_df(rows=5)
        result = compute_technical(df)
        assert result.score == 50.0
        assert "数据不足" in result.signals[0]

    def test_none_input(self):
        """None 输入返回中性评分."""
        result = compute_technical(None)
        assert result.score == 50.0

    def test_duplicate_dates_handled(self):
        """重复日期的数据应被去重，不影响指标计算."""
        df = self._make_kline_df(rows=30)
        dup = df.tail(5).copy()
        dup["close"] = dup["close"] * 1.001
        df_with_dups = pd.concat([df, dup], ignore_index=True)

        result_clean = compute_technical(df)
        result_dup = compute_technical(df_with_dups)

        assert abs(result_clean.score - result_dup.score) < 15

    def test_consecutive_candles_with_duplicates(self):
        """连阳计算：重复日期不应重复计数."""
        df = self._make_kline_df(rows=30)
        for i in range(-5, 0):
            df.loc[df.index[i], "close"] = df.loc[df.index[i], "open"] * 1.05

        result = compute_technical(df)
        up_candles = result.indicators.get("consecutive_up_candles_5d", 0)
        assert up_candles == 5

        dup = df.tail(3).copy()
        df_dup = pd.concat([df, dup], ignore_index=True)
        result_dup = compute_technical(df_dup)
        up_candles_dup = result_dup.indicators.get("consecutive_up_candles_5d", 0)
        assert up_candles_dup == 5

    def test_score_bounds(self):
        """评分始终在 [0, 100] 范围内."""
        for _ in range(10):
            df = self._make_kline_df(rows=50, daily_return=np.random.uniform(-0.05, 0.05))
            result = compute_technical(df)
            assert 0 <= result.score <= 100

    def test_empty_dataframe(self):
        """空 DataFrame (len=0) 应返回中性评分."""
        df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        result = compute_technical(df)
        assert result.score == 50.0
        assert "数据不足" in result.signals[0]

    def test_minimum_dataset_20_rows(self):
        """刚好 20 行 (len>=20) 应能正常计算."""
        df = self._make_kline_df(rows=20)
        result = compute_technical(df)
        assert hasattr(result, "score")
        assert hasattr(result, "indicators")
        assert 0 <= result.score <= 100

    def test_non_continuous_trading_dates(self):
        """date 列包含非连续交易日（周末/假期间隔）应能处理."""
        dates = ["2026-01-02", "2026-01-03", "2026-01-06", "2026-01-07", "2026-01-08",
                 "2026-01-09", "2026-01-10", "2026-01-13", "2026-01-14", "2026-01-15",
                 "2026-01-16", "2026-01-17", "2026-01-20", "2026-01-21", "2026-01-22",
                 "2026-01-23", "2026-01-24", "2026-01-27", "2026-01-28", "2026-01-29"]
        prices = [10.0 + i * 0.01 for i in range(20)]
        df = pd.DataFrame({
            "date": dates,
            "open": [p * 0.99 for p in prices],
            "high": [p * 1.02 for p in prices],
            "low": [p * 0.98 for p in prices],
            "close": prices,
            "volume": [1000000] * 20,
        })
        result = compute_technical(df)
        assert 0 <= result.score <= 100

    def test_flat_close_rsi_50(self):
        """close 全部相同时 RSI 应接近 50."""
        df = self._make_kline_df(rows=30, daily_return=0)
        df["close"] = 10.0
        df["open"] = 10.0
        df["high"] = 10.0
        df["low"] = 10.0
        result = compute_technical(df)
        rsi = result.indicators.get("rsi", 50)
        import math
        assert 0 <= result.score <= 100
        assert math.isnan(rsi) or (45 <= rsi <= 55)

    def test_negative_volume_defense(self):
        """负数 volume（异常数据）应不崩溃."""
        df = self._make_kline_df(rows=25)
        df.loc[df.index[-5:], "volume"] = -1000
        result = compute_technical(df)
        assert 0 <= result.score <= 100
