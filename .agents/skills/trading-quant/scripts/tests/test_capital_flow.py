"""Unit tests for capital flow analysis module."""
import pytest
from data_sources.base import QuoteData
from analysis.capital_flow import compute_capital, CapitalSignal


class TestComputeCapital:
    def _make_quote(self, **kwargs):
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

    def test_capital_flow_basic_structure(self):
        """capital_flow 返回基本结构."""
        q = self._make_quote()
        result = compute_capital(q)
        assert isinstance(result, CapitalSignal)
        assert hasattr(result, "score")
        assert hasattr(result, "signals")
        assert hasattr(result, "metrics")
        assert 0 <= result.score <= 100

    def test_change_pct_none_handling(self):
        """quote.change_pct 为 None 时防空处理."""
        q = self._make_quote(change_pct=None)
        result = compute_capital(q)
        assert 0 <= result.score <= 100

    def test_volume_turnover_zero_no_divide(self):
        """volume/amount 为 0 时不除零."""
        q = self._make_quote(volume=0, amount=0, volume_ratio=0, turnover_rate=0)
        result = compute_capital(q, avg_volume=0, avg_amount=0)
        assert 0 <= result.score <= 100
