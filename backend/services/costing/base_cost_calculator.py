"""Real base-cost calculator — the single source of truth for
"what does a credit actually cost MAARS."

Before this module, `pricing_math.ai_cost_usd` used a hardcoded
fallback of $0.00003/credit (the `DEFAULT_AI_COST_PER_CREDIT`). That
number came from chat-only free-tier traffic and ignored media, voice,
email, lead research. Real mixed traffic is ~30-100x more expensive.
Result: every plan's `monthly_cap_usd` was understated by 30-100x and
every operator margin figure was fictional.

This module reads actual `gateway_usage_logs` over a trailing window
and produces:
  - global_blended_cost()           $/credit across all users
  - blended_cost_for_user(user_id)  $/credit for ONE user (captures
                                    their workload shape — chat-heavy
                                    vs. media-heavy)
  - blended_cost_for_plan(plan_id)  $/credit averaged across users on
                                    that plan
  - modality_cost_per_credit()      {chat, image, video, tts, stt}
                                    per-modality averages for capacity
                                    math in the plan validator

Numbers are cached for 5 minutes so the hot path (reserve / settle)
doesn't hit Mongo every call.

All functions are async; all return either a float (USD per credit)
or a dict of breakdowns.
"""
from __future__ import annotations
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_TTL = 300   # seconds
_cache: dict[str, tuple[Any, float]] = {}

# Minimum credits needed for a statistical signal. Below this we return
# a conservative default rather than a noisy number from 2 log rows.
_MIN_CREDITS_FOR_SIGNAL = 500

# Conservative fallback when we have no data yet. Picked from:
#   chat-only measured:   $0.00004/credit
#   mixed measured:       $0.001/credit
#   media-heavy worst:    $0.003/credit
# We default to $0.001 (mixed) for a cold install so plan economics
# aren't wildly off on day 1.
FALLBACK_BLENDED_USD_PER_CREDIT = 0.001


# ── Cache helpers ────────────────────────────────────────────────────

def _cached(key: str) -> Any | None:
    hit = _cache.get(key)
    if hit and time.time() - hit[1] < _CACHE_TTL:
        return hit[0]
    return None


def _put(key: str, value: Any) -> Any:
    _cache[key] = (value, time.time())
    # bound the cache so long-lived processes don't leak
    if len(_cache) > 5000:
        _cache.pop(next(iter(_cache)))
    return value


def invalidate_all() -> None:
    _cache.clear()


# ── Core queries ─────────────────────────────────────────────────────

async def _aggregate(match: dict, *, lookback_days: int = 30) -> dict[str, Any]:
    """Shared aggregation helper: returns total cost_usd + credits charged
    over the match filter + lookback. None if there's no data."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    m = {**match, "timestamp": {"$gte": since}}
    pipeline = [
        {"$match": m},
        {"$group": {
            "_id": None,
            "total_cost_usd":       {"$sum": "$cost_usd"},
            "total_credits":        {"$sum": "$credits_charged"},
            "total_calls":          {"$sum": 1},
            "total_prompt_tokens":  {"$sum": "$prompt_tokens"},
            "total_completion_tokens": {"$sum": "$completion_tokens"},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1)
    except Exception as exc:
        logger.info("base_cost aggregate failed: %s", exc)
        return {}
    return rows[0] if rows else {}


async def global_blended_cost(*, lookback_days: int = 30) -> dict[str, Any]:
    """$/credit across all MAARS traffic — the headline blended figure
    the Pricing Command Center should display and `pricing_math` should
    consume."""
    key = f"global:{lookback_days}"
    cached = _cached(key)
    if cached is not None:
        return cached

    r = await _aggregate({}, lookback_days=lookback_days)
    total_cost  = float(r.get("total_cost_usd") or 0.0)
    total_cred  = float(r.get("total_credits") or 0.0)
    n_calls     = int(r.get("total_calls") or 0)

    if total_cred < _MIN_CREDITS_FOR_SIGNAL:
        out = {
            "usd_per_credit":  FALLBACK_BLENDED_USD_PER_CREDIT,
            "source":          "fallback",
            "lookback_days":   lookback_days,
            "n_calls":         n_calls,
            "total_cost_usd":  round(total_cost, 6),
            "total_credits":   int(total_cred),
            "confidence":      "low",
        }
        return _put(key, out)

    usd_per_credit = total_cost / total_cred
    out = {
        "usd_per_credit":  round(usd_per_credit, 8),
        "source":          "measured",
        "lookback_days":   lookback_days,
        "n_calls":         n_calls,
        "total_cost_usd":  round(total_cost, 4),
        "total_credits":   int(total_cred),
        "confidence":      "high" if n_calls > 1000 else "medium",
    }
    return _put(key, out)


async def blended_cost_for_user(user_id: str, *, lookback_days: int = 30) -> dict[str, Any]:
    """Per-user blended $/credit. Shows operators which clients are
    expensive to serve — critical for the cost-allocation dashboard."""
    key = f"user:{user_id}:{lookback_days}"
    cached = _cached(key)
    if cached is not None:
        return cached

    r = await _aggregate({"user_id": user_id}, lookback_days=lookback_days)
    total_cost = float(r.get("total_cost_usd") or 0.0)
    total_cred = float(r.get("total_credits") or 0.0)
    calls      = int(r.get("total_calls") or 0)

    if total_cred < _MIN_CREDITS_FOR_SIGNAL:
        # Fallback: use the user's plan blended if assigned, else global.
        global_r = await global_blended_cost(lookback_days=lookback_days)
        out = {
            "user_id":        user_id,
            "usd_per_credit": global_r["usd_per_credit"],
            "source":         "fallback_global",
            "n_calls":        calls,
            "total_cost_usd": round(total_cost, 6),
            "total_credits":  int(total_cred),
            "confidence":     "low",
        }
        return _put(key, out)

    out = {
        "user_id":        user_id,
        "usd_per_credit": round(total_cost / total_cred, 8),
        "source":         "measured",
        "n_calls":        calls,
        "total_cost_usd": round(total_cost, 4),
        "total_credits":  int(total_cred),
        "confidence":     "high" if calls > 200 else "medium",
    }
    return _put(key, out)


async def blended_cost_for_plan(plan_id: str, *, lookback_days: int = 30) -> dict[str, Any]:
    """$/credit averaged across every active user currently on this plan.
    The Pricing Command Center uses this to decide if a plan is bleeding
    money (real cost > published monthly_cap_usd)."""
    key = f"plan:{plan_id}:{lookback_days}"
    cached = _cached(key)
    if cached is not None:
        return cached

    from db import db
    try:
        owned = await db.subscriptions.find(
            {"plan_id": plan_id, "status": {"$in": ["active", "trialing", None]}},
            {"user_id": 1, "_id": 0},
        ).to_list(10000)
    except Exception:
        owned = []
    user_ids = [d.get("user_id") for d in owned if d.get("user_id")]

    if not user_ids:
        global_r = await global_blended_cost(lookback_days=lookback_days)
        out = {
            "plan_id":        plan_id,
            "usd_per_credit": global_r["usd_per_credit"],
            "source":         "fallback_global_no_users",
            "active_users":   0,
            "n_calls":        0,
            "total_cost_usd": 0,
            "total_credits":  0,
            "confidence":     "low",
        }
        return _put(key, out)

    r = await _aggregate({"user_id": {"$in": user_ids}}, lookback_days=lookback_days)
    total_cost = float(r.get("total_cost_usd") or 0.0)
    total_cred = float(r.get("total_credits") or 0.0)
    calls      = int(r.get("total_calls") or 0)

    if total_cred < _MIN_CREDITS_FOR_SIGNAL:
        global_r = await global_blended_cost(lookback_days=lookback_days)
        out = {
            "plan_id":        plan_id,
            "usd_per_credit": global_r["usd_per_credit"],
            "source":         "fallback_global_low_signal",
            "active_users":   len(user_ids),
            "n_calls":        calls,
            "total_cost_usd": round(total_cost, 6),
            "total_credits":  int(total_cred),
            "confidence":     "low",
        }
        return _put(key, out)

    out = {
        "plan_id":        plan_id,
        "usd_per_credit": round(total_cost / total_cred, 8),
        "source":         "measured",
        "active_users":   len(user_ids),
        "n_calls":        calls,
        "total_cost_usd": round(total_cost, 4),
        "total_credits":  int(total_cred),
        "confidence":     "high" if calls > 500 else "medium",
    }
    return _put(key, out)


async def modality_cost_per_credit(*, lookback_days: int = 30) -> dict[str, float]:
    """Per-modality $/credit. Plan validator uses these to say
    'Starter (500 cr) can afford ~12 Sora videos' accurately."""
    key = f"mod:{lookback_days}"
    cached = _cached(key)
    if cached is not None:
        return cached

    from db import db
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$source",
            "total_cost":    {"$sum": "$cost_usd"},
            "total_credits": {"$sum": "$credits_charged"},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(200)
    except Exception:
        rows = []

    # Heuristic bucketing by source tag — sources we know map to modality.
    buckets: dict[str, tuple[float, float]] = {
        "chat": (0.0, 0.0), "image": (0.0, 0.0), "video": (0.0, 0.0),
        "tts": (0.0, 0.0), "stt": (0.0, 0.0), "other": (0.0, 0.0),
    }
    for row in rows:
        s = (row.get("_id") or "").lower()
        cost = float(row.get("total_cost") or 0)
        cred = float(row.get("total_credits") or 0)
        if any(k in s for k in ("chat", "content", "vibe", "agent", "classify", "summarize", "rag")):
            bucket = "chat"
        elif "image" in s or "pollination" in s:
            bucket = "image"
        elif "video" in s or "sora" in s:
            bucket = "video"
        elif "tts" in s or "voiceover" in s:
            bucket = "tts"
        elif "stt" in s or "transcrib" in s:
            bucket = "stt"
        else:
            bucket = "other"
        c_sum, cr_sum = buckets[bucket]
        buckets[bucket] = (c_sum + cost, cr_sum + cred)

    out: dict[str, float] = {}
    for b, (c, cr) in buckets.items():
        if cr >= 100:
            out[b] = round(c / cr, 8)
        else:
            out[b] = FALLBACK_BLENDED_USD_PER_CREDIT
    return _put(key, out)


# ── Consumption helpers used by pricing_math ─────────────────────────

async def effective_cost_per_credit(
    *, user_id: str | None = None, plan_id: str | None = None,
) -> float:
    """The number pricing_math.ai_cost_usd should actually use.

    Resolution:
      - if user_id: per-user measured (if signal)
      - elif plan_id: per-plan measured (if signal)
      - else: global measured
      - fallback to $0.001/credit (mixed-workload default)
    """
    if user_id:
        r = await blended_cost_for_user(user_id)
        if r["confidence"] != "low":
            return float(r["usd_per_credit"])
    if plan_id:
        r = await blended_cost_for_plan(plan_id)
        if r["confidence"] != "low":
            return float(r["usd_per_credit"])
    g = await global_blended_cost()
    return float(g["usd_per_credit"])


async def monthly_spend_usd(user_id: str) -> float:
    """What has this user cost MAARS this calendar month (provider side)?
    Used by the advisory cap enforcement + cost-allocation dashboard."""
    from db import db
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    pipeline = [
        {"$match": {"user_id": user_id, "timestamp": {"$gte": month_start}}},
        {"$group": {"_id": None, "cost": {"$sum": "$cost_usd"}}},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1)
    except Exception:
        return 0.0
    return round(float((rows[0]["cost"] if rows else 0.0) or 0.0), 4)
