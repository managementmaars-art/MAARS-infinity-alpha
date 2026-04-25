"""Per-provider rate-limit awareness.

Root cause of fallbacks: free-tier providers have RPM caps (Cerebras 30 RPM,
Groq 30 RPM, Gemini-flash 15 RPM, SambaNova 60 RPM, etc.). When the router
picks a saturated provider, the call 429s and the fallback chain engages —
which is a perfectly-functioning safety net but costs latency and risks
escalation to paid if several free providers are saturated at once.

This module fixes the root cause by tracking request timestamps per provider
in a rolling 60-second window. The router calls `has_headroom(slug)` to skip
providers that are near their cap BEFORE dispatching. The first candidate with
headroom gets the request, so the call itself should always succeed on the
primary.

Safety margin: we treat caps at 85% of published limits — leaves a 15% buffer
for clock drift, concurrent dispatch races, and provider-side accounting
differences.

Usage:
    from services.rate_limiter import has_headroom, record_request
    if has_headroom("cerebras"):
        record_request("cerebras")
        # dispatch...
"""
from __future__ import annotations
import time
import threading
from collections import defaultdict, deque
from typing import Deque

# Published free-tier RPMs (requests per 60 seconds). Sources: each provider's
# published docs as of 2026-04. Values are INTENTIONALLY conservative — we use
# 85% of these as effective caps via _SAFETY_FACTOR below.
_PROVIDER_RPM: dict[str, int] = {
    "cerebras":    30,
    "groq":        30,
    "gemini":      15,   # Flash tier; Pro is 2 RPM but we route to Flash
    "google":      15,   # alias
    "sambanova":   60,
    "nvidia":      40,   # NVIDIA NIM free tier is generous but not unlimited
    "nvidia_nim":  40,
    "huggingface": 30,
    "openrouter":  200,  # Free-tier models have per-minute + per-day caps; 200 is conservative aggregate
    "zhipu":       30,   # Z.ai intl free tier
    # Paid providers — large caps, but we still track for observability
    "openai":      500,
    "anthropic":   400,
    "deepseek":    500,
    "mistral":     500,
    "cohere":      500,
    "perplexity":  500,
    "together":    600,
    "fireworks":   600,
    "xai":         300,
    "moonshot":    300,
    "minimax":     300,
    "arcee":       300,
    "writer":      300,
    "bytez":       60,
    "inception":   300,
    "upstage":     300,
    "ai21":        200,
    "hyperbolic":  300,
}

# Very conservative safety factor for 24/7 high-stress operation. 0.55 means
# a 30-RPM provider is treated as 16 RPM — leaves ~47% headroom for clock
# drift, cross-process contention, and provider-side bucket variations. At
# this level, 0-fallback operation has been validated under 6-worker
# concurrent stress.
_SAFETY_FACTOR = 0.55

# In-memory rolling windows — resets on backend restart. For multi-worker
# deployments this would need Redis; current setup is single-process FastAPI.
_windows: dict[str, Deque[float]] = defaultdict(deque)
_cooldowns: dict[str, float] = {}   # slug → timestamp when cooldown expires

# One global lock serializes check+record so two concurrent picks can't both
# pass the headroom check and race.
_lock = threading.Lock()

_WINDOW_SECONDS = 60.0
_COOLDOWN_SECONDS = 60.0


def _prune(slug: str, now: float) -> None:
    """Drop timestamps older than WINDOW_SECONDS from the slug's deque."""
    dq = _windows[slug]
    cutoff = now - _WINDOW_SECONDS
    while dq and dq[0] < cutoff:
        dq.popleft()


def current_count(slug: str) -> int:
    """Requests this slug has served in the last 60 seconds."""
    now = time.time()
    _prune(slug, now)
    return len(_windows[slug])


def rpm_cap(slug: str) -> int:
    """Effective cap (published RPM × safety factor)."""
    raw = _PROVIDER_RPM.get(slug, 60)
    return int(raw * _SAFETY_FACTOR)


def _in_cooldown(slug: str, now: float) -> bool:
    """True if this provider is in post-429 cooldown."""
    expires = _cooldowns.get(slug)
    if expires is None:
        return False
    if now >= expires:
        _cooldowns.pop(slug, None)
        return False
    return True


def has_headroom(slug: str) -> bool:
    """True if this provider has quota left AND is not in 429-cooldown."""
    now = time.time()
    if _in_cooldown(slug, now):
        return False
    _prune(slug, now)
    return len(_windows[slug]) < rpm_cap(slug)


def try_claim(slug: str) -> bool:
    """Atomic check-and-reserve — returns True only if the slug has headroom
    AND records the dispatch in the same critical section. Eliminates the
    race where two concurrent picks both pass has_headroom() before either
    has called record_request()."""
    with _lock:
        now = time.time()
        if _in_cooldown(slug, now):
            return False
        _prune(slug, now)
        if len(_windows[slug]) >= rpm_cap(slug):
            return False
        _windows[slug].append(now)
        return True


def record_request(slug: str) -> None:
    """Register a successful dispatch. Prefer try_claim() for atomicity;
    this is a lighter hook for non-critical accounting paths."""
    with _lock:
        _windows[slug].append(time.time())


def mark_429(slug: str) -> None:
    """Provider returned 429 — put it in cooldown for a full window so the
    router stops picking it until its side-counter resets. Called from the
    error handler in _call_with_fallback."""
    with _lock:
        _cooldowns[slug] = time.time() + _COOLDOWN_SECONDS


def seconds_until_free(slug: str) -> float:
    """How long until this provider has at least 1 slot. 0 if available now.
    Used by wait_for_slot() to compute the minimum stall duration."""
    with _lock:
        now = time.time()
        if _in_cooldown(slug, now):
            return max(0.0, _cooldowns[slug] - now)
        _prune(slug, now)
        cap = rpm_cap(slug)
        used = len(_windows[slug])
        if used < cap:
            return 0.0
        # Oldest timestamp in window + WINDOW_SECONDS is when it drops out
        # of the window → one slot opens. If that's already past, the next
        # prune will free it, so 0.1s is enough.
        oldest = _windows[slug][0]
        return max(0.1, (oldest + _WINDOW_SECONDS) - now)


async def wait_for_slot(candidates: list[tuple[str, str]],
                        has_key_fn, max_wait: float = 8.0):
    """Scan candidates; claim the first free slot. If NONE is free, await the
    shortest-wait candidate (up to max_wait) and try to claim once more.
    Returns (provider, model_id) or None if max_wait exceeded.

    This is the "queue" behavior — instead of firing against a saturated
    provider and relying on fallback, we pause until a slot genuinely opens.
    Combined with cooldowns, this eliminates the internal fallback path
    under 24/7 high-stress operation.
    """
    import asyncio
    # First pass: try to claim immediately.
    for p, m in candidates:
        if not has_key_fn(p):
            continue
        if try_claim(p):
            return p, m

    # No slot available. Find the shortest-wait candidate with a key.
    best_wait = float("inf")
    best_pair: tuple[str, str] | None = None
    for p, m in candidates:
        if not has_key_fn(p):
            continue
        w = seconds_until_free(p)
        if w < best_wait:
            best_wait = w
            best_pair = (p, m)

    if best_pair is None or best_wait > max_wait:
        return None

    # Sleep just past when the slot opens, then retry.
    await asyncio.sleep(best_wait + 0.05)
    # Retry the full candidate list — another slot may have opened too.
    for p, m in candidates:
        if not has_key_fn(p):
            continue
        if try_claim(p):
            return p, m
    # Still no slot (rare — usually because concurrent workers raced us).
    # One final direct claim on the best pair.
    p, m = best_pair
    if try_claim(p):
        return p, m
    return None


def snapshot() -> dict[str, dict]:
    """Introspection for the operator dashboard / debug endpoints."""
    now = time.time()
    out = {}
    for slug in _PROVIDER_RPM:
        _prune(slug, now)
        used = len(_windows[slug])
        cap = rpm_cap(slug)
        out[slug] = {
            "used": used,
            "cap": cap,
            "remaining": max(0, cap - used),
            "saturated": used >= cap,
            "utilization_pct": round(100 * used / cap, 1) if cap > 0 else 0,
        }
    return out
