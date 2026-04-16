"""Unit tests for cache module."""
import pytest
import json
import os
from unittest.mock import patch
from utils.cache import cache_set, cache_get


class TestKVCache:
    def test_cache_set_get(self, tmp_path):
        """基础缓存读写."""
        with patch("utils.cache.CACHE_DIR", str(tmp_path)):
            cache_set("test_key", {"value": 42}, ttl_seconds=3600)
            result = cache_get("test_key")
            assert result == {"value": 42}

    def test_cache_expired(self, tmp_path):
        """过期缓存返回 None."""
        import time
        with patch("utils.cache.CACHE_DIR", str(tmp_path)):
            cache_set("test_key", {"value": 42}, ttl_seconds=0)
            time.sleep(0.1)
            result = cache_get("test_key")
            assert result is None


class TestKVCacheBoundary:
    def test_corrupted_json_defense(self, tmp_path):
        """缓存文件损坏（非法 JSON）时返回 None."""
        from utils.cache import cache_get
        from unittest.mock import patch
        key = "corrupt_key"
        path = tmp_path / (key + ".json")
        path.write_text("not valid json")
        with patch("utils.cache.CACHE_DIR", str(tmp_path)):
            result = cache_get(key)
            assert result is None

    def test_concurrent_read_write(self, tmp_path):
        """并发读写不同 key 不崩溃."""
        import threading
        from utils.cache import cache_set, cache_get
        from unittest.mock import patch
        results = []
        def writer(k, v):
            with patch("utils.cache.CACHE_DIR", str(tmp_path)):
                cache_set(k, v, ttl_seconds=3600)
        def reader(k):
            with patch("utils.cache.CACHE_DIR", str(tmp_path)):
                r = cache_get(k)
                results.append(r)
        with patch("utils.cache.CACHE_DIR", str(tmp_path)):
            cache_set("a", {"x": 1}, ttl_seconds=3600)
            cache_set("b", {"y": 2}, ttl_seconds=3600)
        t1 = threading.Thread(target=reader, args=("a",))
        t2 = threading.Thread(target=reader, args=("b",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert {"x": 1} in results
        assert {"y": 2} in results
    @pytest.mark.asyncio
    async def test_calc_consecutive_date_gap_handling(self):
        """calc_consecutive_from_klines 日期间隔>3天时记录警告但不崩溃."""
        from unittest.mock import patch, MagicMock, AsyncMock
        from utils.cache import calc_consecutive_from_klines
        import utils.cache as cache
        cache._kline_consecutive_cache = {"data": None, "ts": 0, "ttl": 600}
        mock_resp = MagicMock()
        mock_resp.text = "[{\"day\":\"2026-01-02\",\"close\":\"100\"},{\"day\":\"2026-01-09\",\"close\":\"101\"}]"
        with patch("httpx.AsyncClient") as mock_client:
            instance = MagicMock()
            instance.get = AsyncMock(return_value=mock_resp)
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = instance
            result = await calc_consecutive_from_klines()
        assert "consecutive_up_days" in result
        assert "consecutive_down_days" in result
