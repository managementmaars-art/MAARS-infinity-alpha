"""Hedged requests — Google's 'Tail at Scale' trick for p99 latency.

If a request hasn't finished within p90 of observed latency, fire a
duplicate to a second provider and take whichever responds first. Costs
up to 2× the money on ~10% of calls; saves seconds on the slow tail
where a stuck provider would otherwise hang the user.

Published impact (Google, 2013 paper): 44% reduction in p99 latency
with a 5% increase in mean load. For us, that means agent-chat feels
fast even when OpenAI's us-east-1 briefly melts.

We hedge only when:
  - max_hedges > 0 AND a second-choice provider exists
  - caller is interactive (source startswith 'chat', 'vibe', 'agent')
  - not cached / not batch / not streaming (stream hedging is hairy —
    which stream wins?)

We track rolling p90 latency per (provider, model) in-process. After
50 observations the p90 estimate is stable enough to trigger hedging.
"""
from __future__ import annotations
import asyncio
import bisect
import logging
import time
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

_WINDOW = 200          # latency samples per bucket
_MIN_SAMPLES = 50      # need this many before hedging kicks in
_FLOOR_P90_MS = 2000   # don't hedge anything faster than 2s p90 — too noisy

_latencies: dict[str, list[float]] = {}


def record_latency(bucket_key: str, latency_ms: float) -> None:
    """Append a latency sample; bounded list acts as a crude ring buffer."""
    samples = _latencies.setdefault(bucket_key, [])
    samples.append(latency_ms)
    if len(samples) > _WINDOW:
        del samples[0]


def p90(bucket_key: str) -> float | None:
    """Return p90 of the last N samples, or None if too few."""
    samples = _latencies.get(bucket_key, [])
    if len(samples) < _MIN_SAMPLES:
        return None
    s = sorted(samples)
    idx = int(0.90 * (len(s) - 1))
    return s[idx]


def hedge_delay_ms(bucket_key: str) -> float | None:
    """How long to wait before firing the hedge. None means don't hedge."""
    v = p90(bucket_key)
    if v is None:
        return None
    if v < _FLOOR_P90_MS:
        return None
    # Fire the hedge at 80% of p90 — aggressive enough to save on the slow
    # tail, conservative enough that we don't hedge on merely-average calls.
    return v * 0.8


async def run_with_hedge(
    *,
    primary: Callable[[], Awaitable[Any]],
    secondary: Callable[[], Awaitable[Any]] | None,
    bucket_key: str,
    max_wait_ms: float | None = None,
) -> tuple[Any, str]:
    """Race the primary + a delayed-start secondary. Returns (result, winner)
    where winner is 'primary' or 'hedge'. Secondary task is cancelled if
    primary wins, and vice-versa. If secondary is None, just awaits primary.
    """
    start = time.time()
    if secondary is None:
        result = await primary()
        record_latency(bucket_key, (time.time() - start) * 1000)
        return result, "primary"

    delay_ms = max_wait_ms if max_wait_ms is not None else hedge_delay_ms(bucket_key)
    if delay_ms is None:
        result = await primary()
        record_latency(bucket_key, (time.time() - start) * 1000)
        return result, "primary"

    primary_task = asyncio.create_task(primary())
    try:
        result = await asyncio.wait_for(asyncio.shield(primary_task), timeout=delay_ms / 1000)
        record_latency(bucket_key, (time.time() - start) * 1000)
        return result, "primary"
    except asyncio.TimeoutError:
        pass

    # Primary is slow. Fire hedge.
    hedge_task = asyncio.create_task(secondary())
    done, pending = await asyncio.wait(
        {primary_task, hedge_task}, return_when=asyncio.FIRST_COMPLETED
    )
    winner = next(iter(done))
    for p in pending:
        p.cancel()
    try:
        result = winner.result()
    except Exception:
        # Winner errored — try the other if it's still alive.
        if pending:
            alt = next(iter(pending))
            try:
                result = await alt
                record_latency(bucket_key, (time.time() - start) * 1000)
                return result, "hedge" if alt is hedge_task else "primary"
            except Exception:
                raise
        raise
    record_latency(bucket_key, (time.time() - start) * 1000)
    return result, "hedge" if winner is hedge_task else "primary"
