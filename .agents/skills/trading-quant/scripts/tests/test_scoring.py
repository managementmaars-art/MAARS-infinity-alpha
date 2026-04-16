"""Unit tests for scoring module."""
import pytest
from analysis.scoring import compute_stock_score, _detect_risks
from data_sources.base import QuoteData


class TestComputeStockScore:
    def _make_quote(self, **kwargs):
        """Helper: 创建模拟 QuoteData."""
        defaults = {
            "code": "000001", "name": "测试股", "price": 10.0,
            "change_pct": 1.0, "volume": 1000000, "amount": 50000000,
            "volume_ratio": 1.0, "turnover_rate": 3.0,
            "pe": 20.0, "pb": 2.0, "market_cap": 100e8,
            "bid1": 9.99, "ask1": 10.01,
            "open": 9.90, "high": 10.10, "low": 9.85, "pre_close": 9.90,
            "timestamp": "2026-03-04 15:00:00", "source": "test",
            "outer_vol": 0.0, "inner_vol": 0.0,
        }
        defaults.update(kwargs)
        return QuoteData(**{k: v for k, v in defaults.items() if k in QuoteData.__dataclass_fields__})


    def test_change_pct_none_handling(self):
        """change_pct 为 None 时不应崩溃."""
        import pandas as pd
        q = self._make_quote(change_pct=None)
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        try:
            result = compute_stock_score(q, df)
            assert 10 <= result.total_score <= 90
        except (TypeError, AttributeError) as e:
            pytest.fail(f"change_pct=None should be handled gracefully: {e}")

    def test_score_range(self):
        """评分在 [10, 90] 范围内（scoring.py 有 clamp）."""
        import pandas as pd
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        q = self._make_quote()
        result = compute_stock_score(q, df)
        assert 10 <= result.total_score <= 90

    def test_limit_up_momentum_penalty(self):
        """涨停时应有追涨惩罚."""
        import pandas as pd
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        q_normal = self._make_quote(change_pct=1.0)
        q_limit_up = self._make_quote(change_pct=10.0)
        s_normal = compute_stock_score(q_normal, df)
        s_limit_up = compute_stock_score(q_limit_up, df)
        assert s_limit_up.total_score < s_normal.total_score + 5


class TestComputeStockScoreBoundary:
    """边界条件测试."""

    def _make_quote(self, **kwargs):
        from data_sources.base import QuoteData
        defaults = {
            "code": "000001", "name": "测试股", "price": 10.0,
            "change_pct": 1.0, "volume": 1000000, "amount": 50000000,
            "volume_ratio": 1.0, "turnover_rate": 3.0,
            "pe": 20.0, "pb": 2.0, "market_cap": 100e8,
            "bid1": 9.99, "ask1": 10.01,
            "open": 9.90, "high": 10.10, "low": 9.85, "pre_close": 9.90,
            "timestamp": "2026-03-04 15:00:00", "source": "test",
            "outer_vol": 0.0, "inner_vol": 0.0,
        }
        defaults.update(kwargs)
        return QuoteData(**{k: v for k, v in defaults.items() if k in QuoteData.__dataclass_fields__})

    def test_quote_all_none_extreme(self):
        """quote 可选字段为 None 时不应崩溃."""
        import pandas as pd
        q = self._make_quote(change_pct=None, volume_ratio=None, turnover_rate=None, pe=None, pb=None)
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        result = compute_stock_score(q, df)
        assert 10 <= result.total_score <= 90

    def test_change_pct_extreme_limit_up_down(self):
        """change_pct 极端值 +20/-20（涨跌停）应有相应惩罚/加分."""
        import pandas as pd
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        q_up = self._make_quote(change_pct=20.0)
        q_down = self._make_quote(change_pct=-20.0)
        s_up = compute_stock_score(q_up, df)
        s_down = compute_stock_score(q_down, df)
        assert s_up.total_score < 70
        assert s_down.total_score > 15

    def test_volume_ratio_zero_and_extreme(self):
        """volume_ratio 为 0 或极大值(>100) 应不崩溃."""
        import pandas as pd
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=30, freq="B").strftime("%Y-%m-%d"),
            "open": [10] * 30, "high": [11] * 30, "low": [9] * 30,
            "close": [10.5] * 30, "volume": [1000000] * 30,
        })
        q_zero = self._make_quote(volume_ratio=0)
        q_extreme = self._make_quote(volume_ratio=150)
        s_zero = compute_stock_score(q_zero, df)
        s_extreme = compute_stock_score(q_extreme, df)
        assert 10 <= s_zero.total_score <= 90
        assert 10 <= s_extreme.total_score <= 90

    def test_empty_df_technical_neutral_fallback(self):
        """daily_df 为空时 technical 降级为中性，总分仍有效."""
        import pandas as pd
        q = self._make_quote()
        df_empty = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        result = compute_stock_score(q, df_empty)
        assert 10 <= result.total_score <= 90
