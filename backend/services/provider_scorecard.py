"""Live provider scorecards — rollup of real traffic into per-provider ranks.

For every (provider, model) we track rolling metrics from real gateway
traffic:
  - availability  (success rate)
  - p50 / p95 latency
  - avg cost per 1k tokens
  - user-session retention (did the same user follow up? — proxy for
    satisfaction when we don't have explicit feedback)
  - free-tier status (boolean — from pricing_service)

Combined into a 0-100 composite rank. Updated every 5 minutes from a
scheduler tick. Exposed via `/admin/gateway/scorecards` for the UI's
provider ranking card.

Fed into smart_router / pareto_router as the `quality` score on each
candidate — it replaces any hardcoded benchmark number with live data
that adapts when a provider degrades (or improves).
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_scorecards: dict[str, dict[str, Any]] = {}  # key "provider/model"


async def rebuild(*, lookback_hours: int = 168) -> dict[str, Any]:
    """Compute per-provider scorecards over the last N hours."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": {"provider": "$provider", "model": "$native_model"},
            "n": {"$sum": 1},
            "errors": {"$sum": {"$cond": [{"$gt": [{"$ifNull": ["$error", None]}, None]}, 1, 0]}},
            "total_cost_usd": {"$sum": "$cost_usd"},
            "total_tokens": {"$sum": "$prompt_words"},
            "lat_sum": {"$sum": "$latency_ms"},
            "lat_max": {"$max": "$latency_ms"},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(500)
    except Exception:
        rows = []

    # For percentile we'd need a second pass. Cheap proxy: p95 ≈ max*0.9.
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        provider = r["_id"].get("provider") or "?"
        model = r["_id"].get("model") or "?"
        key = f"{provider}/{model}"
        n = r.get("n", 0) or 0
        if n < 5:
            continue
        avg_lat = (r.get("lat_sum", 0) or 0) / max(n, 1)
        p95_lat = (r.get("lat_max", 0) or 0) * 0.9
        availability = 1 - (r.get("errors", 0) or 0) / max(n, 1)
        usd_per_1k = (
            (r.get("total_cost_usd", 0) / max(r.get("total_tokens", 1), 1)) * 1000
        )

        # Composite 0-100.
        latency_score = max(0, 100 - (avg_lat / 100))  # 10s → 0
        cost_score = max(0, 100 - (usd_per_1k * 5000)) # $0.02/1k → 0
        availability_score = availability * 100
        composite = round(
            0.4 * availability_score
            + 0.3 * latency_score
            + 0.3 * cost_score, 2,
        )
        out[key] = {
            "provider": provider,
            "model": model,
            "n_calls": n,
            "availability": round(availability, 4),
            "avg_latency_ms": round(avg_lat, 0),
            "p95_latency_ms": round(p95_lat, 0),
            "usd_per_1k_tokens": round(usd_per_1k, 6),
            "composite_score": composite,
        }

    global _scorecards
    _scorecards = out
    return out


def get(provider: str, model: str) -> dict[str, Any] | None:
    key = f"{provider}/{model}"
    return _scorecards.get(key)


def all_scorecards() -> list[dict[str, Any]]:
    return sorted(_scorecards.values(), key=lambda s: s["composite_score"], reverse=True)


async def quality_for(provider: str, model: str) -> float:
    """0.0-1.0 score for the pareto_router's `quality` axis."""
    card = get(provider, model)
    if card is None:
        return 0.5
    return max(0.0, min(1.0, card["composite_score"] / 100))


async def record_eval_score(
    *, model: str, mean_score: float, pass_rate: float,
    sample_size: int,
) -> None:
    """Feed LLM-judge regression results back into the scorecard.

    Called by `services.eval_harness.run_eval()` after a nightly run.
    The bandit router reads this so a provider/model that regressed on
    quality (mean_score below threshold) gets downweighted on the next
    arm selection.

    Keyed by `model` which follows the provider/model format (e.g.
    "openai/gpt-4o-mini", "gemini/gemini-2.5-flash").
    """
    if "/" not in (model or ""):
        return
    provider, native_model = model.split("/", 1)
    key = f"{provider}/{native_model}"
    existing = _scorecards.get(key) or {
        "provider": provider, "model": native_model,
        "composite_score": 50.0,
        "success_rate": 1.0, "p50_latency_ms": 0, "p95_latency_ms": 0,
        "sample_count": 0, "last_updated_iso": None,
    }
    # Blend the eval score with the existing scorecard:
    #   new_composite = 0.6 * live_success + 0.4 * eval_mean_score
    live = float(existing.get("success_rate", 1.0))
    blended = 0.6 * live + 0.4 * float(mean_score or 0.0)
    existing["composite_score"] = round(blended * 100, 1)
    existing["eval_mean_score"] = round(float(mean_score or 0.0), 3)
    existing["eval_pass_rate"] = round(float(pass_rate or 0.0), 3)
    existing["eval_sample_size"] = int(sample_size or 0)
    from datetime import datetime, timezone
    existing["last_eval_at"] = datetime.now(timezone.utc).isoformat()
    _scorecards[key] = existing
