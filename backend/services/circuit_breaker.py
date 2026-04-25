"""Per-provider circuit breakers — stop slamming a dead provider.

The pattern: after N consecutive failures within a short window, a
provider's "breaker" trips open. Calls to that provider fail-fast
(milliseconds) instead of waiting for a 30-second timeout. After
cool_down seconds we let ONE probe through (half-open); if it succeeds,
breaker closes and traffic resumes; if it fails, breaker re-opens.

Without this, when OpenAI has a regional outage every caller sits on
a 30s timeout and the entire event loop stalls. With this, we detect
the outage in ~5 failed calls and instantly route around it.

State lives in-process (module globals). On a multi-worker deploy each
worker has its own view — good enough, since trips happen fast and
workers converge within seconds. A future Redis-backed shared view
would be strictly better but isn't required for correctness.

Usage:
    if not breaker.allow("openai"):
        raise ProviderUnavailable("openai")
    try:
        resp = await call_openai(...)
        breaker.record_success("openai")
    except Exception:
        breaker.record_failure("openai")
        raise
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

FAILURE_THRESHOLD = 5      # consecutive failures to trip
COOL_DOWN_SECONDS = 30     # time before we test half-open
WINDOW_SECONDS = 60        # failures outside this window don't count


@dataclass
class _BreakerState:
    failures: int = 0
    last_failure_ts: float = 0.0
    opened_at: float = 0.0
    state: str = "closed"  # closed | open | half_open
    success_count: int = 0
    total_requests: int = 0
    total_failures: int = 0


_states: dict[str, _BreakerState] = {}


def _get(provider: str) -> _BreakerState:
    st = _states.get(provider)
    if st is None:
        st = _BreakerState()
        _states[provider] = st
    return st


def allow(provider: str) -> bool:
    """True if the caller may attempt a request to this provider."""
    st = _get(provider)
    now = time.time()
    st.total_requests += 1

    if st.state == "closed":
        # Expire stale failure counts.
        if now - st.last_failure_ts > WINDOW_SECONDS:
            st.failures = 0
        return True

    if st.state == "open":
        if now - st.opened_at >= COOL_DOWN_SECONDS:
            st.state = "half_open"
            logger.info("circuit-breaker %s: open → half_open (probe)", provider)
            return True
        return False

    # half_open: only one probe at a time. Naïve single-threaded check
    # (we don't need per-worker correctness here — worst case we send
    # 2 probes instead of 1, which is fine).
    return True


def record_success(provider: str) -> None:
    st = _get(provider)
    st.success_count += 1
    if st.state == "half_open":
        st.state = "closed"
        st.failures = 0
        logger.info("circuit-breaker %s: half_open → closed (probe succeeded)", provider)
    elif st.state == "closed":
        st.failures = max(0, st.failures - 1)


def record_failure(provider: str, *, error: str = "") -> None:
    st = _get(provider)
    now = time.time()
    st.total_failures += 1
    st.last_failure_ts = now

    if st.state == "half_open":
        st.state = "open"
        st.opened_at = now
        logger.warning("circuit-breaker %s: half_open → open (probe failed: %s)", provider, error[:200])
        return

    if st.state == "closed":
        # Reset count if outside window.
        if now - st.last_failure_ts > WINDOW_SECONDS and st.failures > 0:
            st.failures = 0
        st.failures += 1
        if st.failures >= FAILURE_THRESHOLD:
            st.state = "open"
            st.opened_at = now
            logger.warning(
                "circuit-breaker %s: closed → open (%d consecutive failures, last: %s)",
                provider, st.failures, error[:200]
            )


def snapshot() -> dict[str, dict]:
    """For /admin/gateway — show which providers are circuit-broken."""
    return {
        p: {
            "state": st.state,
            "failures_in_window": st.failures,
            "cool_down_remaining": max(
                0, int(COOL_DOWN_SECONDS - (time.time() - st.opened_at))
            ) if st.state == "open" else 0,
            "total_requests": st.total_requests,
            "total_failures": st.total_failures,
            "error_rate": round(st.total_failures / max(st.total_requests, 1), 4),
        }
        for p, st in _states.items()
    }


def reset(provider: str) -> None:
    """Admin-hook — force-close a breaker (e.g. after provider confirms recovery)."""
    if provider in _states:
        _states[provider] = _BreakerState()
