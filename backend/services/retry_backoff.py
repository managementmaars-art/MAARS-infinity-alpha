"""Exponential backoff with full jitter — the AWS-recommended retry policy.

Two things most naive retry loops get wrong:
  1. They retry on 4xx errors that will never succeed (401 Unauthorized,
     422 Validation) — wasting latency + provider quota.
  2. They use fixed backoff (1s, 2s, 4s) with no jitter, so a thundering
     herd of clients all retry at the same instant after a provider
     hiccup and re-DDoS the provider.

This module:
  - Classifies errors into retryable (429, 500-series, network timeouts)
    vs terminal (4xx except 408/425/429).
  - Uses AWS "full jitter": sleep = random(0, min(cap, base * 2^attempt))
  - Honors Retry-After headers when the provider sends them (always
    preferable to our own schedule — the provider knows when to try again).

Use as a decorator:
    @retry_on_provider_error(max_attempts=3, provider="openai")
    async def call_provider(...):
        ...

Or inline:
    async for sleep_before_attempt in backoff_iter(max_attempts=3):
        await sleep_before_attempt()
        try: ...
"""
from __future__ import annotations
import asyncio
import functools
import logging
import random
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

BASE_DELAY = 0.25   # seconds
MAX_DELAY = 20.0
MAX_ATTEMPTS_DEFAULT = 3

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504, 520, 521, 522, 524}


def _is_retryable(exc: Exception) -> bool:
    # httpx.HTTPStatusError
    response = getattr(exc, "response", None)
    if response is not None:
        status = getattr(response, "status_code", None)
        if isinstance(status, int):
            return status in RETRYABLE_STATUS
    # httpx network / timeout
    name = type(exc).__name__
    if name in ("TimeoutException", "ConnectTimeout", "ReadTimeout", "NetworkError", "ConnectError", "RemoteProtocolError"):
        return True
    return False


def _retry_after_from_exc(exc: Exception) -> float | None:
    response = getattr(exc, "response", None)
    if response is None:
        return None
    try:
        ra = response.headers.get("retry-after") or response.headers.get("Retry-After")
        if not ra:
            return None
        # integer-seconds form
        return max(0.0, float(ra))
    except Exception:
        return None


def _sleep_for_attempt(attempt: int) -> float:
    cap = min(MAX_DELAY, BASE_DELAY * (2 ** attempt))
    return random.uniform(0.0, cap)


def retry_on_provider_error(
    *,
    max_attempts: int = MAX_ATTEMPTS_DEFAULT,
    provider: str = "unknown",
    on_retry: Callable[[int, Exception, float], None] | None = None,
):
    """Decorator — retry the wrapped coroutine on retryable errors."""
    def decorator(fn: Callable[..., Awaitable[Any]]):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    if not _is_retryable(exc) or attempt == max_attempts - 1:
                        raise
                    sleep = _retry_after_from_exc(exc)
                    if sleep is None:
                        sleep = _sleep_for_attempt(attempt)
                    logger.info(
                        "retry %s attempt=%d sleep=%.2fs error=%s",
                        provider, attempt + 1, sleep, type(exc).__name__,
                    )
                    if on_retry:
                        try:
                            on_retry(attempt, exc, sleep)
                        except Exception:
                            pass
                    await asyncio.sleep(sleep)
                    last_exc = exc
            assert last_exc is not None
            raise last_exc
        return wrapper
    return decorator


async def with_retry(
    fn: Callable[[], Awaitable[Any]],
    *,
    max_attempts: int = MAX_ATTEMPTS_DEFAULT,
    provider: str = "unknown",
) -> Any:
    """Inline wrapper — same semantics as the decorator, for one-off calls."""
    @retry_on_provider_error(max_attempts=max_attempts, provider=provider)
    async def _run():
        return await fn()
    return await _run()
