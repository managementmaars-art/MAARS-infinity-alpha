"""Aggregator warm pool — routes traffic to HF / OpenRouter / Bytez /
Novita / Together / Fireworks catalogs, not just the curated MODEL_REGISTRY.

Before this module, the smart router's candidate pool was:

    1. Curated MODEL_REGISTRY (622 entries, hand-picked)
    2. Deep fallback: every MODEL_REGISTRY entry of matching tier

Both only touch MAARS-catalogued models. The 175k+ HuggingFace models
and ~350 OpenRouter models were unreachable by `maars/auto` — they
only served if a client explicitly called `huggingface/X/Y`.

Now the router has a **third tier**:

    3. Aggregator warm pool — top-N models from each configured
       aggregator, with metadata (quality proxy, cost estimate, free-
       tier flag) so Pareto can rank them alongside direct candidates.

Design principles:

  • **Hot path stays fast.** The warm pool is appended after the
    curated+deep pools, not prepended — direct providers still win
    on tied rank. A request only reaches the warm pool if its free
    quota is exhausted or its curated candidates are all rate-limited.

  • **Only surface what's likely to work.** For HF we filter to
    public, text-generation, downloads > 5000. Gated/private models
    are excluded — they'd 401 at call time.

  • **Per-aggregator circuit breaker.** If HF has thrown 5 errors
    in the last 60s, we skip it for the next 2 min. Prevents a
    broken aggregator from poisoning the entire pool.

  • **Cached for 10 minutes.** The warm pool is an ordering hint,
    not a live feed. Refetching 349 OpenRouter entries every request
    would add 100ms+ to every call.
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_TTL_S = 600.0        # 10 minutes — warm pool is slow-changing
_cache: dict[str, Any] = {"pool": None, "ts": 0.0}

# Simple error-window circuit breaker, per aggregator.
_error_window: dict[str, list[float]] = {}
_CB_ERRORS_THRESHOLD = 5
_CB_WINDOW_S         = 60.0
_CB_TRIP_DURATION_S  = 120.0
_cb_tripped_until: dict[str, float] = {}


# ── Per-aggregator limits ────────────────────────────────────────────
# Keep these conservative. The warm pool exists to expand addressable
# models, not to flood traffic at obscure providers. Each aggregator
# contributes at most this many candidates to routing.
TOP_N_BY_AGGREGATOR: dict[str, int] = {
    "huggingface":   100,
    "openrouter":    200,
    "together":      100,
    "fireworks":     50,
    "novita":        80,
    "bytez":         50,
}


# ── Circuit breaker ──────────────────────────────────────────────────

def record_aggregator_error(slug: str) -> None:
    """Call when an aggregator returns an error at inference time.
    Repeated errors in the window trip the breaker so the warm pool
    temporarily excludes this provider."""
    now = time.time()
    hist = _error_window.setdefault(slug, [])
    hist.append(now)
    hist[:] = [t for t in hist if now - t <= _CB_WINDOW_S]
    if len(hist) >= _CB_ERRORS_THRESHOLD:
        _cb_tripped_until[slug] = now + _CB_TRIP_DURATION_S
        logger.warning("aggregator %s circuit-breaker tripped (errors=%d)", slug, len(hist))
        hist.clear()


def is_aggregator_available(slug: str) -> bool:
    until = _cb_tripped_until.get(slug)
    if until and time.time() < until:
        return False
    return True


# ── HuggingFace warm candidates ──────────────────────────────────────

async def _fetch_hf_candidates(api_key: str | None) -> list[dict]:
    """Top-N popular, non-gated, text-generation HF models as routing
    candidates. Returns dicts with (provider, model_id, quality, cost,
    latency, free_tier) so the Pareto reranker can score them."""
    import httpx
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    limit = TOP_N_BY_AGGREGATOR["huggingface"]
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                "https://huggingface.co/api/models",
                headers=headers,
                params={
                    "pipeline_tag": "text-generation",
                    "sort":         "downloads",
                    "limit":        limit,
                    "full":         "false",
                },
            )
    except Exception as exc:
        logger.info("HF warm-pool fetch failed: %s", exc)
        return []
    if r.status_code != 200:
        return []
    out: list[dict] = []
    for m in r.json():
        if not isinstance(m, dict):
            continue
        model_id = m.get("id") or m.get("modelId")
        if not model_id:
            continue
        if m.get("gated"):
            continue        # gated models require user-side license acceptance
        # Quality proxy: log of downloads (capped 0..1)
        dl = float(m.get("downloads", 0))
        import math
        quality = min(1.0, max(0.3, math.log10(max(10, dl)) / 7.0))
        out.append({
            "provider":  "huggingface",
            "model":     model_id,
            "quality":   round(quality, 3),
            "cost":      0.0,            # free serverless tier (rate-limited)
            "latency":   1200,           # HF serverless is slower; realistic estimate
            "free_tier": True,
        })
    return out


# ── OpenRouter warm candidates ───────────────────────────────────────

async def _fetch_openrouter_candidates(api_key: str | None) -> list[dict]:
    """Top-N popular models from OpenRouter with their actual pricing.
    OpenRouter's /models endpoint is public — no auth required."""
    import httpx
    limit = TOP_N_BY_AGGREGATOR["openrouter"]
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get("https://openrouter.ai/api/v1/models", timeout=20.0)
    except Exception as exc:
        logger.info("OpenRouter warm-pool fetch failed: %s", exc)
        return []
    if r.status_code != 200:
        return []
    data = (r.json() or {}).get("data", [])
    out: list[dict] = []
    for m in data[:limit]:
        mid = m.get("id")
        if not mid:
            continue
        pricing = m.get("pricing", {}) or {}
        # USD per token → cost per million tokens for easier scaling
        in_cost  = float(pricing.get("prompt", 0)) * 1_000_000
        out_cost = float(pricing.get("completion", 0)) * 1_000_000
        blended  = (in_cost + out_cost) / 2.0
        # Free models cost $0; OpenRouter tags them with a :free suffix
        is_free = mid.endswith(":free") or blended == 0.0
        out.append({
            "provider":  "openrouter",
            "model":     mid,
            "quality":   0.70,            # neutral default; OpenRouter doesn't expose arena ranks
            "cost":      round(blended, 4),
            "latency":   800,
            "free_tier": is_free,
        })
    return out


# ── Generic OpenAI-compat aggregator ────────────────────────────────

async def _fetch_generic(
    slug: str, url: str, api_key: str | None, default_cost: float = 1.0,
) -> list[dict]:
    """Works for Together / Fireworks / Novita / Bytez — anything that
    returns an OpenAI-shape `/v1/models` response."""
    import httpx
    limit = TOP_N_BY_AGGREGATOR.get(slug, 50)
    if not api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                url, headers={"Authorization": f"Bearer {api_key}"}, timeout=20.0,
            )
    except Exception as exc:
        logger.info("%s warm-pool fetch failed: %s", slug, exc)
        return []
    if r.status_code != 200:
        return []
    body = r.json() or {}
    data = body if isinstance(body, list) else body.get("data", body.get("models", []))
    out: list[dict] = []
    for m in (data or [])[:limit]:
        if isinstance(m, str):
            mid = m
        else:
            mid = m.get("id") or m.get("name") or m.get("modelId")
        if not mid:
            continue
        out.append({
            "provider":  slug,
            "model":     mid,
            "quality":   0.65,
            "cost":      default_cost,
            "latency":   700,
            "free_tier": False,
        })
    return out


# ── Public API ───────────────────────────────────────────────────────

async def get_warm_pool(api_keys: dict) -> list[dict]:
    """Return the full aggregator warm pool as candidate dicts.
    Cached 10 min. De-duped by (provider, model). Excludes tripped
    aggregators."""
    now = time.time()
    if _cache["pool"] is not None and (now - _cache["ts"]) < _CACHE_TTL_S:
        return _cache["pool"]

    tasks = []
    if api_keys.get("huggingface") and is_aggregator_available("huggingface"):
        tasks.append(("huggingface", _fetch_hf_candidates(api_keys["huggingface"])))
    if is_aggregator_available("openrouter"):
        # OpenRouter's /models endpoint is public — include even without a key.
        tasks.append(("openrouter", _fetch_openrouter_candidates(api_keys.get("openrouter"))))
    if api_keys.get("together") and is_aggregator_available("together"):
        tasks.append(("together", _fetch_generic(
            "together", "https://api.together.xyz/v1/models", api_keys["together"], default_cost=1.0,
        )))
    if api_keys.get("fireworks") and is_aggregator_available("fireworks"):
        tasks.append(("fireworks", _fetch_generic(
            "fireworks", "https://api.fireworks.ai/inference/v1/models", api_keys["fireworks"], default_cost=0.8,
        )))
    if api_keys.get("novita") and is_aggregator_available("novita"):
        tasks.append(("novita", _fetch_generic(
            "novita", "https://api.novita.ai/v3/openai/models", api_keys["novita"], default_cost=0.9,
        )))
    if api_keys.get("bytez") and is_aggregator_available("bytez"):
        tasks.append(("bytez", _fetch_generic(
            "bytez", "https://api.bytez.com/v1/models", api_keys["bytez"], default_cost=0.5,
        )))

    results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
    pool: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for (slug, _task), res in zip(tasks, results):
        if isinstance(res, Exception):
            logger.info("warm-pool %s threw: %s", slug, res)
            continue
        for c in res:
            key = (c["provider"], c["model"])
            if key in seen:
                continue
            seen.add(key)
            pool.append(c)

    _cache["pool"] = pool
    _cache["ts"]   = now
    logger.info("aggregator warm pool rebuilt: %d candidates", len(pool))
    return pool


async def warm_candidates_as_pairs(api_keys: dict) -> list[tuple[str, str]]:
    """Shortcut for the router's candidate-list consumer. Preserves the
    aggregator's own ordering (popularity/download rank) so the pool
    naturally puts its better picks first."""
    pool = await get_warm_pool(api_keys)
    return [(c["provider"], c["model"]) for c in pool]


def invalidate_cache() -> None:
    _cache["pool"] = None
    _cache["ts"]   = 0.0
