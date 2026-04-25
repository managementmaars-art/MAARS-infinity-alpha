"""
Operator metrics — the unit-economics view.

These endpoints read from existing collections (`usage_logs`, `ledger_entries`,
`provider_health_events`, `inference_requests`) and aggregate them into the
four operator lenses demanded by the product spec:

    /admin/metrics/routing         — task-type × model × mode distribution
    /admin/metrics/provider-spend  — internal $ cost per provider / model
    /admin/metrics/profitability   — credits charged − internal cost, rolled up
    /admin/metrics/health          — provider health + fallback rate

Where a collection doesn't yet exist, the endpoint returns an empty-but-shaped
result rather than 500 — this keeps the operator dashboard consuming them
before the gateway is wired through.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query

from auth import require_admin
from db import db
from models.schemas import User

router = APIRouter()


def _window_start(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


async def _collection_exists(name: str) -> bool:
    return name in await db.list_collection_names()


# ---------------------------------------------------------------------------
# Routing decisions
# ---------------------------------------------------------------------------

@router.get("/admin/metrics/routing")
async def routing_metrics(
    days: int = Query(7, ge=1, le=90),
    _: User = Depends(require_admin),
):
    """Distribution of routing decisions: source (task-tag) × model × mode.

    Reads db.gateway_usage_logs — the canonical single collection every LLM
    call writes to since Audit 015. Task-type proxy uses the `source` tag
    that every gateway.complete() call emits (e.g. "chats.send_message",
    "vibe.create", "orchestration.execute_agent_task:*").
    """
    since = _window_start(days)

    by_task: dict[str, int] = {}
    by_model: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    total = 0

    if await _collection_exists("gateway_usage_logs"):
        cursor = db.gateway_usage_logs.find(
            {"timestamp": {"$gte": since}},
            {"_id": 0, "source": 1, "maars_model": 1, "native_model": 1, "provider": 1},
        )
        async for doc in cursor:
            total += 1
            # Source tag = task type (chats.send_message, vibe.create, orchestration.*, v1_gateway).
            src = doc.get("source") or "v1_gateway"
            # Strip the ":{id}:iter_*" suffix so agent.tool_loop:agent_copywriter:iter_0
            # rolls up to "agent.tool_loop" for cleaner aggregation.
            bucket_key = src.split(":", 1)[0] if ":" in src else src
            by_task[bucket_key] = by_task.get(bucket_key, 0) + 1
            model = doc.get("native_model") or doc.get("maars_model") or "unknown"
            by_model[model] = by_model.get(model, 0) + 1
            # Routing mode: alias (maars/*) vs manual (provider/model literal).
            mmodel = doc.get("maars_model") or ""
            mode = "alias" if mmodel.startswith("maars/") else "manual"
            by_mode[mode] = by_mode.get(mode, 0) + 1

    return {
        "window_days": days,
        "total_requests": total,
        "by_task_type": dict(sorted(by_task.items(), key=lambda kv: -kv[1])),
        "by_model": dict(sorted(by_model.items(), key=lambda kv: -kv[1])[:25]),
        "by_routing_mode": by_mode,
    }


# ---------------------------------------------------------------------------
# Provider spend (internal cost, not user-facing credits)
# ---------------------------------------------------------------------------

@router.get("/admin/metrics/provider-spend")
async def provider_spend(
    days: int = Query(30, ge=1, le=365),
    _: User = Depends(require_admin),
):
    since = _window_start(days)
    by_provider: dict[str, dict[str, Any]] = {}
    total_cost = 0.0

    if await _collection_exists("gateway_usage_logs"):
        cursor = db.gateway_usage_logs.find(
            {"timestamp": {"$gte": since}},
            {"_id": 0, "provider": 1, "native_model": 1, "cost_usd": 1, "prompt_words": 1},
        )
        async for doc in cursor:
            provider = doc.get("provider") or "unknown"
            cost = float(doc.get("cost_usd") or 0.0)
            bucket = by_provider.setdefault(provider, {
                "provider": provider, "calls": 0, "cost_usd": 0.0,
                "input_tokens": 0, "output_tokens": 0,
            })
            bucket["calls"] += 1
            bucket["cost_usd"] = round(bucket["cost_usd"] + cost, 6)
            # gateway logs store prompt_words; approximate tokens as words × 1.3.
            bucket["input_tokens"] += int((doc.get("prompt_words") or 0) * 1.3)
            total_cost += cost

    return {
        "window_days": days,
        "total_cost_usd": round(total_cost, 4),
        "providers": sorted(by_provider.values(), key=lambda b: -b["cost_usd"]),
    }


# ---------------------------------------------------------------------------
# Profitability = credits charged (DEBIT) - internal cost
# ---------------------------------------------------------------------------

@router.get("/admin/metrics/profitability")
async def profitability(
    days: int = Query(30, ge=1, le=365),
    credits_per_usd: float = Query(1000.0, gt=0, description="Conversion: credits per 1 USD of value"),
    _: User = Depends(require_admin),
):
    """
    Gross profitability window.

    Revenue proxy: sum of DEBIT ledger entries in the window, converted to USD
    at `credits_per_usd`. Cost: sum of `estimated_cost_usd` from usage_logs.
    Margin = revenue - cost.
    """
    since = _window_start(days)

    revenue_credits = 0
    revenue_usd = 0.0
    if await _collection_exists("ledger_entries"):
        pipeline = [
            {"$match": {"type": "DEBIT", "created_at": {"$gte": since}}},
            {"$group": {"_id": None, "sum_credits": {"$sum": "$amount_credits"}}},
        ]
        async for row in db.ledger_entries.aggregate(pipeline):
            revenue_credits = int(row.get("sum_credits") or 0)
        revenue_usd = revenue_credits / credits_per_usd if credits_per_usd else 0.0

    cost_usd = 0.0
    if await _collection_exists("gateway_usage_logs"):
        pipeline = [
            {"$match": {"timestamp": {"$gte": since}}},
            {"$group": {"_id": None, "sum_cost": {"$sum": "$cost_usd"}}},
        ]
        async for row in db.gateway_usage_logs.aggregate(pipeline):
            cost_usd = float(row.get("sum_cost") or 0.0)

    net = revenue_usd - cost_usd
    margin_pct = (net / revenue_usd * 100.0) if revenue_usd > 0 else 0.0
    return {
        "window_days": days,
        "revenue_credits": revenue_credits,
        "revenue_usd": round(revenue_usd, 4),
        "cost_usd": round(cost_usd, 4),
        "net_usd": round(net, 4),
        "margin_pct": round(margin_pct, 2),
        "credits_per_usd": credits_per_usd,
    }


# ---------------------------------------------------------------------------
# Provider health + fallback
# ---------------------------------------------------------------------------

@router.get("/admin/treasury/auto-pilot")
async def treasury_auto_pilot(
    days: int = Query(30, ge=1, le=365),
    _: User = Depends(require_admin),
):
    """One-page operator profit view — every cost automated, attribution
    rolled up by client × subscription × top-up × category × model.

    Operator-stated goal: "I don't want to worry about my costs at all.
    I only see profits." This endpoint consolidates everything into a
    single payload so a single dashboard render answers:

      - Bottom line: net profit this period (one number)
      - Three-way split: revenue / COGS reserve / operator profit
      - Per-category P&L: revenue from each track minus actual cost
      - Per-client P&L: top buyers + their cost-to-serve + margin
      - Per-model spend: where the money is going by provider/model
      - Auto-rules health: which cost levers are flipped + their savings
      - Alert if any provider needs top-up (operator card on file
        auto-handles this; only surfaces here as a safety check)
    """
    from datetime import datetime, timezone, timedelta
    from db import db
    from services.billing import treasury

    snapshot = await treasury.get_snapshot()

    # ── Per-category revenue + COGS + margin (last `days` days) ──
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    pipeline_topups = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {"_id": "$category", "revenue": {"$sum": "$amount_usd"},
                    "credits": {"$sum": "$credits"}, "count": {"$sum": 1}}},
    ]
    cat_rev_rows = await db.category_topups.aggregate(pipeline_topups).to_list(20)
    from services.costing.blended_by_category import blended_by_category, CATEGORY_KEYS
    rates = await blended_by_category()
    def _rate(cat):
        return float((rates.get(cat) or {}).get("value") or 0.0)
    per_category = []
    obs = {r.get("_id"): r for r in cat_rev_rows}
    for cat in CATEGORY_KEYS + ["general"]:
        row = obs.get(cat, {})
        rev  = float(row.get("revenue") or 0)
        crs  = int(row.get("credits") or 0)
        cnt  = int(row.get("count") or 0)
        cost = crs * _rate(cat if cat in CATEGORY_KEYS else "chat")
        prof = rev - cost
        per_category.append({
            "category":     cat,
            "revenue_usd":  round(rev, 2),
            "cost_usd":     round(cost, 4),
            "profit_usd":   round(prof, 2),
            "margin_pct":   round((prof / rev * 100), 1) if rev > 0 else None,
            "topups_count": cnt,
        })

    # ── Per-client P&L (top 20 by revenue in window) ──
    # Revenue from category_topups + recurring subscriptions.
    # Cost from gateway_usage_logs grouped by user_id.
    since_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    cost_pipeline = [
        {"$match": {"timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()}}},
        {"$group": {"_id": "$user_id", "cost": {"$sum": "$cost_usd"}, "calls": {"$sum": 1}}},
    ]
    user_costs = {r["_id"]: r for r in await db.gateway_usage_logs.aggregate(cost_pipeline).to_list(500)}
    user_revs_pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {"_id": "$user_id", "revenue": {"$sum": "$amount_usd"}}},
    ]
    user_revs = {r["_id"]: r for r in await db.category_topups.aggregate(user_revs_pipeline).to_list(500)}
    all_users = set(user_costs.keys()) | set(user_revs.keys())
    per_client = []
    for uid in all_users:
        if not uid:
            continue
        rev = float((user_revs.get(uid, {}) or {}).get("revenue") or 0)
        cost = float((user_costs.get(uid, {}) or {}).get("cost") or 0)
        calls = int((user_costs.get(uid, {}) or {}).get("calls") or 0)
        per_client.append({
            "user_id":     uid,
            "revenue_usd": round(rev, 2),
            "cost_usd":    round(cost, 4),
            "profit_usd":  round(rev - cost, 2),
            "margin_pct":  round((rev - cost) / rev * 100, 1) if rev > 0 else None,
            "api_calls":   calls,
        })
    per_client.sort(key=lambda r: r["revenue_usd"] - r["cost_usd"], reverse=True)
    per_client = per_client[:20]

    # ── Per-model spend (top 20 by cost in window) ──
    model_pipeline = [
        {"$match": {"timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()}}},
        {"$group": {"_id": {"provider": "$provider", "model": "$native_model"},
                    "cost": {"$sum": "$cost_usd"}, "calls": {"$sum": 1}}},
        {"$sort": {"cost": -1}},
        {"$limit": 20},
    ]
    per_model = [
        {
            "provider": (r.get("_id") or {}).get("provider") or "—",
            "model":    (r.get("_id") or {}).get("model") or "—",
            "cost_usd": round(float(r.get("cost") or 0), 4),
            "calls":    int(r.get("calls") or 0),
        }
        for r in await db.gateway_usage_logs.aggregate(model_pipeline).to_list(20)
    ]
    total_provider_cost = round(sum(m["cost_usd"] for m in per_model), 4)

    # ── Cost Optimization Levers — current ON/OFF + estimated savings ──
    try:
        from services.costing.cost_config import get_config as _cc
        cost_cfg = await _cc()
        levers = cost_cfg.get("levers") or {}
    except Exception:
        levers = {}
    import os as _os
    def _env(k):
        return bool(_os.environ.get(k))
    lever_status = [
        {"key": "local_media",   "label": "Local media GPU",     "active_claim": bool(levers.get("local_media",   {}).get("active_claim")), "env_detected": _env("MAARS_LOCAL_IMAGE_URL"), "savings_per_heavy_client": 18.00},
        {"key": "self_smtp",     "label": "Self-hosted SMTP",     "active_claim": bool(levers.get("self_smtp",     {}).get("active_claim")), "env_detected": _env("MAARS_SMTP_HOST"),       "savings_per_heavy_client": 0.40},
        {"key": "telnyx_voice",  "label": "Telnyx (vs Twilio)",   "active_claim": bool(levers.get("telnyx_voice",  {}).get("active_claim")), "env_detected": _env("TELNYX_API_KEY"),        "savings_per_heavy_client": 5.00},
        {"key": "native_leads",  "label": "Native lead research", "active_claim": True, "env_detected": True, "savings_per_heavy_client": 15.00},
    ]
    untapped = sum(l["savings_per_heavy_client"] for l in lever_status if not l["active_claim"])

    # ── Provider balances — surface only LOW alerts. Provider native
    # auto-recharge (operator card on file) handles top-ups; this is a
    # safety check so operator gets a heads-up before an outage.
    try:
        balances = await db.provider_balance_snapshots.find(
            {}, {"_id": 0}
        ).sort("captured_at", -1).limit(60).to_list(60)
    except Exception:
        balances = []
    seen_slugs = set()
    low_alerts = []
    for b in balances:
        slug = b.get("slug")
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        bal = float(b.get("balance_usd") or 0)
        thr = float(b.get("threshold_usd") or 5)
        if bal > 0 and bal < thr:
            low_alerts.append({"slug": slug, "balance_usd": bal, "threshold_usd": thr})

    return {
        "window_days":          days,
        # Headline — the one number operator cares about
        "net_profit_usd":       snapshot["net_profit_usd"],
        "gross_margin_pct":     snapshot["gross_margin_pct"],
        # Three-way split (lifetime)
        "treasury": {
            "revenue_usd":         snapshot["revenue_usd"],
            "cogs_reserve_usd":    snapshot["cogs_reserve_usd"],
            "cogs_actual_usd":     snapshot["cogs_actual_usd"],
            "operator_profit_usd": snapshot["operator_profit_usd"],
            "surplus_rolled_usd":  snapshot.get("surplus_rolled_usd", 0),
            "deficit_alerts":      snapshot.get("deficit_alerts", 0),
        },
        # Per-attribution rollups for the window
        "per_category":         per_category,
        "per_client":           per_client,
        "per_model":            per_model,
        "total_provider_cost":  total_provider_cost,
        # Cost levers + tap headroom
        "cost_levers":          lever_status,
        "untapped_monthly_usd_per_heavy_client": round(untapped, 2),
        # Safety alerts (provider auto-recharge is what actually pays them)
        "provider_low_alerts":  low_alerts,
        "generated_at":         datetime.now(timezone.utc).isoformat(),
    }


@router.get("/admin/metrics/quality-gate")
async def quality_gate_metrics(
    hours: int = Query(24, ge=1, le=720),
    _: User = Depends(require_admin),
):
    """Quality-gate telemetry from llm_gateway.complete().

    Every cheap-tier call is assessed for confidence (logprobs when
    available, hedge-phrase heuristics otherwise). This endpoint rolls
    up the last `hours` of assessments so the operator can see:

      total_assessed      — how many cheap-tier calls got scored
      escalated_count     — how many got silently retried on premium
      escalation_rate_pct — what % of cheap calls needed escalation
      avg_score           — mean confidence score across all assessments
      by_method           — breakdown by logprobs vs heuristic
      by_tier             — breakdown by economy vs standard

    Healthy range: escalation_rate_pct around 10-20%. Higher = cheap
    models aren't carrying their weight for your traffic; lower = gate
    threshold may be too lax (passing through weak responses)."""
    from datetime import datetime, timezone, timedelta
    import time as _time
    from db import db
    since_ts = _time.time() - hours * 3600
    cursor = db.quality_gate_events.find({"ts": {"$gte": since_ts}}, {"_id": 0})
    rows = await cursor.to_list(50_000)
    if not rows:
        return {
            "hours_window":        hours,
            "total_assessed":      0,
            "escalated_count":     0,
            "escalation_rate_pct": 0.0,
            "avg_score":           None,
            "by_method":           {},
            "by_tier":             {},
            "generated_at":        datetime.now(timezone.utc).isoformat(),
        }
    total = len(rows)
    esc = sum(1 for r in rows if r.get("should_escalate"))
    avg_score = sum(r.get("score") or 0 for r in rows) / total if total else None
    by_method: dict[str, dict] = {}
    for r in rows:
        m = r.get("method") or "unknown"
        slot = by_method.setdefault(m, {"count": 0, "escalated": 0})
        slot["count"] += 1
        if r.get("should_escalate"):
            slot["escalated"] += 1
    by_tier: dict[str, dict] = {}
    for r in rows:
        t = r.get("tier") or "unknown"
        slot = by_tier.setdefault(t, {"count": 0, "escalated": 0, "avg_score": 0})
        slot["count"] += 1
        slot["avg_score"] += (r.get("score") or 0)
        if r.get("should_escalate"):
            slot["escalated"] += 1
    for t, slot in by_tier.items():
        slot["avg_score"] = round(slot["avg_score"] / max(slot["count"], 1), 3)
    return {
        "hours_window":        hours,
        "total_assessed":      total,
        "escalated_count":     esc,
        "escalation_rate_pct": round((esc / total) * 100, 1) if total else 0.0,
        "avg_score":           round(avg_score, 3) if avg_score is not None else None,
        "by_method":           by_method,
        "by_tier":             by_tier,
        "generated_at":        datetime.now(timezone.utc).isoformat(),
    }


@router.get("/admin/metrics/revenue-by-category")
async def revenue_by_category(
    days: int = Query(30, ge=1, le=365),
    _: User = Depends(require_admin),
):
    """Per-category revenue + COGS + margin from tagged credit top-ups.

    Reads `category_topups` (populated when a client buys a category-tagged
    credit package, see routes/subscriptions.py webhook). For each of the 8
    tracks, reports:
      revenue_usd         — sum of top-up prices in the window
      topups_count        — how many purchases
      credits_sold        — total credits in those top-ups
      cost_estimated_usd  — credits × per-category blended rate
      profit_usd          — revenue − cost
      margin_pct          — profit ÷ revenue × 100
      share_of_revenue    — this category's fraction of total revenue

    This is the "so which category actually makes me money" panel.
    """
    from datetime import datetime, timezone, timedelta
    from db import db
    from services.costing.blended_by_category import blended_by_category, CATEGORY_KEYS

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id":        "$category",
            "revenue":    {"$sum": "$amount_usd"},
            "count":      {"$sum": 1},
            "credits":    {"$sum": "$credits"},
        }},
    ]
    rows = await db.category_topups.aggregate(pipeline).to_list(100)
    rates = await blended_by_category()
    def rate(cat):
        return (rates.get(cat, {}) or {}).get("value") or 0.0

    total_rev = sum(r.get("revenue", 0) or 0 for r in rows) or 0.0
    # Render per-track (even if zero revenue) so UI can show all 8 slots.
    per_cat = []
    observed = {r.get("_id"): r for r in rows}
    for cat in CATEGORY_KEYS + ["general"]:
        row = observed.get(cat, {})
        rev  = float(row.get("revenue")  or 0)
        crs  = int(row.get("credits") or 0)
        cnt  = int(row.get("count")   or 0)
        cost = crs * rate(cat if cat in CATEGORY_KEYS else "chat")
        profit = rev - cost
        margin = (profit / rev * 100) if rev > 0 else None
        per_cat.append({
            "category":          cat,
            "revenue_usd":       round(rev, 2),
            "topups_count":      cnt,
            "credits_sold":      crs,
            "cost_estimated_usd": round(cost, 4),
            "profit_usd":        round(profit, 2),
            "margin_pct":        round(margin, 1) if margin is not None else None,
            "share_of_revenue":  round((rev / total_rev * 100), 1) if total_rev > 0 else 0.0,
        })
    # Stable order: highest revenue first within category set, "general" last.
    ordered_known = sorted([r for r in per_cat if r["category"] != "general"],
                           key=lambda r: r["revenue_usd"], reverse=True)
    general_row = [r for r in per_cat if r["category"] == "general"]
    return {
        "days_window":    days,
        "total_revenue_usd": round(total_rev, 2),
        "total_topups":   sum(r["topups_count"] for r in per_cat),
        "per_category":   ordered_known + general_row,
        "generated_at":   datetime.now(timezone.utc).isoformat(),
    }


@router.get("/admin/metrics/revenue")
async def revenue_metrics(
    days: int = Query(30, ge=1, le=365),
    top_users: int = Query(10, ge=1, le=100),
    _: User = Depends(require_admin),
):
    """
    Operator profit-pool view (Stripe-backed subscription split).

    `total_revenue_usd` is the sum of operator-share entries in the window —
    this is what MAARS *retains* as profit on cash collected, distinct from
    `/admin/metrics/profitability` which reasons about credit-debits vs
    provider cost.
    """
    from services import revenue_service, stripe_service

    total = await revenue_service.total_revenue(days=days)
    by_pkg = await revenue_service.revenue_by_package(days=days)
    by_user = await revenue_service.revenue_by_user(days=days, limit=top_users)
    recent = await revenue_service.recent_entries(limit=20)

    # Annotate package rows with their configured split % for context.
    for row in by_pkg:
        pkg = stripe_service.PACKAGES.get(row["package_id"])
        row["operator_share_pct"] = pkg.operator_share_pct if pkg else None

    return {
        "window_days": days,
        "total_revenue_usd": round(total, 4),
        "by_package": by_pkg,
        "top_users": by_user,
        "recent": recent,
        "packages_configured": stripe_service.list_packages(),
    }


@router.post("/admin/metrics/router/train")
async def train_smart_router(_: User = Depends(require_admin)):
    """Train the ML-based smart router from gateway_usage_logs. Requires >=50 samples."""
    from services.routing import smart_router
    result = await smart_router.train_from_logs()
    return result


@router.post("/admin/metrics/router/explain")
async def explain_routing(
    request_body: dict,
    _: User = Depends(require_admin),
):
    """Diagnostic: show what the smart router would do with a given prompt."""
    from services.routing import smart_router
    prompt = request_body.get("prompt", "hello")
    return smart_router.explain(prompt)


@router.post("/admin/metrics/router/evolve")
async def evolve_router(
    request_body: dict = {},
    _: User = Depends(require_admin),
):
    """
    Run one Proposer -> Solver -> Judge evolution cycle.

    Generates test prompts, routes them to multiple models, judges each response,
    and feeds the quality scores back into the smart router's learned quality map.
    The router gets smarter with every cycle -- no human labels needed.

    Based on Multi-agent-evolve (UIUC) + LLMRouter scoring integration.

    Optional body fields:
        max_prompts:       how many test prompts to generate (default 10)
        models_per_prompt: how many models to evaluate per prompt (default 4)
        judge_provider:    provider for the Judge agent (default groq)
        judge_model:       model for the Judge (default llama-3.3-70b-versatile)
    """
    from services.routing import router_evolution
    result = await router_evolution.run_evolution_cycle(
        max_prompts=int(request_body.get("max_prompts", 10)),
        models_per_prompt=int(request_body.get("models_per_prompt", 4)),
        judge_provider=str(request_body.get("judge_provider", "groq")),
        judge_model=str(request_body.get("judge_model", "llama-3.3-70b-versatile")),
    )
    return result


@router.get("/admin/metrics/router/evolution-history")
async def evolution_history(
    limit: int = Query(20, ge=1, le=100),
    _: User = Depends(require_admin),
):
    """Recent evolution run summaries."""
    from services.routing import router_evolution
    return {"object": "list", "data": await router_evolution.get_evolution_history(limit)}


@router.get("/admin/metrics/router/quality-map")
async def quality_map(_: User = Depends(require_admin)):
    """The live learned quality scores the router is using right now."""
    from services.routing import router_evolution
    qm = await router_evolution.get_current_quality_map()
    return {"object": "quality_map", "models": len(qm), "data": qm}


@router.get("/admin/metrics/health")
async def health_metrics(
    days: int = Query(7, ge=1, le=90),
    _: User = Depends(require_admin),
):
    since = _window_start(days)
    events = []
    fallback_count = 0
    total_calls = 0

    if await _collection_exists("provider_health_events"):
        cursor = db.provider_health_events.find(
            {"created_at": {"$gte": since}}, {"_id": 0},
        ).sort("created_at", -1).limit(200)
        events = [doc async for doc in cursor]

    if await _collection_exists("gateway_usage_logs"):
        total_calls = await db.gateway_usage_logs.count_documents({"timestamp": {"$gte": since}})
        fallback_count = await db.gateway_usage_logs.count_documents(
            {"timestamp": {"$gte": since}, "fallback_used": True},
        )

    fallback_rate = (fallback_count / total_calls * 100.0) if total_calls else 0.0
    return {
        "window_days": days,
        "total_calls": total_calls,
        "fallback_count": fallback_count,
        "fallback_rate_pct": round(fallback_rate, 2),
        "recent_events": events,
    }


# ---------------------------------------------------------------------------
# Provider external balance monitoring
# ---------------------------------------------------------------------------

@router.get("/admin/metrics/provider-balances")
async def provider_balances(_: User = Depends(require_admin)):
    """
    Current balance/quota for every configured provider.

    Tier 1: Real API call (DeepSeek, OpenRouter, ElevenLabs, Together)
    Tier 2: Estimated from MAARS usage_logs minus operator-set starting balance
    Tier 3: Free tier providers (no balance tracking)
    """
    from services import provider_balance
    balances = await provider_balance.fetch_all_balances()
    burn_rates = await provider_balance.get_burn_rates()
    alerts = await provider_balance.get_alerts()
    configs = await provider_balance.get_all_configs()

    # Merge burn rate into balance entries
    for b in balances:
        rate = burn_rates.get(b["slug"])
        if rate:
            b["daily_burn_usd"] = rate.get("daily_burn_usd")
            b["days_until_empty"] = rate.get("days_until_empty")

    configured = [b for b in balances if b.get("tier") != "unconfigured"]
    return {
        "object": "provider_balances",
        "total_providers": len(balances),
        "configured_providers": len(configured),
        "alerts": alerts,
        "configs": configs,
        "providers": balances,
    }


@router.get("/admin/metrics/provider-balances/history")
async def provider_balance_history(
    slug: str = Query(..., description="Provider slug"),
    days: int = Query(30, ge=1, le=365),
    _: User = Depends(require_admin),
):
    """Balance snapshots over time for burn-rate charts."""
    from services import provider_balance
    history = await provider_balance.get_balance_history(slug, days)
    return {"object": "balance_history", "slug": slug, "days": days, "data": history}


@router.post("/admin/metrics/provider-balances/refresh")
async def refresh_provider_balances(_: User = Depends(require_admin)):
    """Force refresh all provider balances (clears cache) and take a snapshot."""
    from services import provider_balance
    provider_balance.clear_cache()
    count = await provider_balance.snapshot_balances()
    balances = await provider_balance.fetch_all_balances()
    alerts = await provider_balance.get_alerts()
    return {
        "status": "refreshed",
        "snapshot_count": count,
        "alerts": alerts,
        "providers": balances,
    }


@router.get("/admin/metrics/provider-balances/alerts")
async def provider_balance_alerts(_: User = Depends(require_admin)):
    """Providers whose balance is below their configured threshold."""
    from services import provider_balance
    alerts = await provider_balance.get_alerts()
    return {"object": "balance_alerts", "count": len(alerts), "alerts": alerts}


@router.post("/admin/metrics/provider-balances/config")
async def set_provider_balance_config(
    request_body: dict,
    _: User = Depends(require_admin),
):
    """
    Set starting balance and/or alert threshold for a provider.

    Body: { "slug": "openai", "starting_balance_usd": 20.0, "alert_threshold_usd": 5.0 }
    """
    from services import provider_balance
    slug = request_body.get("slug", "")
    if not slug:
        return {"error": "slug is required"}
    result = await provider_balance.set_provider_config(
        slug=slug,
        starting_balance_usd=request_body.get("starting_balance_usd"),
        alert_threshold_usd=request_body.get("alert_threshold_usd"),
    )
    return {"status": "updated", "config": result}


# ---------------------------------------------------------------------------
# Unified Cash Position — operator-facing "what's my money doing right now"
# ---------------------------------------------------------------------------

@router.get("/admin/cash-position")
async def admin_cash_position(_: User = Depends(require_admin)):
    """Unified view of operator cash flow in a single response:

      - liquid_stripe: live Stripe available + pending balances
                       (requires STRIPE_SECRET_KEY or STRIPE_RESTRICTED_KEY
                        with balance:read scope)
      - committed_providers: USD topped up but not yet spent across every
                             Tier-1/Tier-2 provider
      - client_liabilities: unused credits held in client wallets —
                            money the operator OWES back as service
      - revenue_30d: operator-share of Stripe charges in last 30d
      - spend_30d: gateway cost (what the router actually paid providers)
      - runway_days: (committed_providers / daily_burn) — how long current
                     topups last at current burn

    This is the "one screen" view — before it existed, the operator had
    to hop between /admin/metrics/revenue, /admin/metrics/provider-balances,
    /admin/gateway/payg-overview to stitch together cash position.
    """
    import os
    from datetime import datetime, timezone, timedelta

    # ── Liquid: Stripe balance ────────────────────────────────────────
    # Uses STRIPE_RESTRICTED_KEY if present (safer — balance:read scope
    # only); falls back to STRIPE_SECRET_KEY which usually exists from
    # the checkout wiring. If neither works, returns null + a reason so
    # the UI can prompt the operator to add the restricted key.
    stripe_balance: dict[str, Any] = {
        "available_usd": None,
        "pending_usd": None,
        "currency": "usd",
        "configured": False,
        "error": None,
    }
    key = os.environ.get("STRIPE_RESTRICTED_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        stripe_balance["error"] = "No STRIPE_RESTRICTED_KEY or STRIPE_SECRET_KEY in .env"
    else:
        try:
            import stripe
            stripe.api_key = key
            bal = await _run_sync(stripe.Balance.retrieve)
            # Sum each currency bucket; report primary = usd if present.
            def _pick(entries):
                usd_total = 0
                other = {}
                for e in entries:
                    amt = e.get("amount", 0) / 100.0
                    cur = e.get("currency", "usd")
                    if cur == "usd":
                        usd_total += amt
                    else:
                        other[cur] = round(other.get(cur, 0) + amt, 2)
                return round(usd_total, 2), other
            avail_usd, avail_other = _pick(bal.get("available", []))
            pend_usd,  pend_other  = _pick(bal.get("pending", []))
            stripe_balance.update({
                "available_usd": avail_usd,
                "pending_usd": pend_usd,
                "available_other": avail_other or None,
                "pending_other": pend_other or None,
                "configured": True,
            })
        except Exception as exc:
            stripe_balance["error"] = f"{type(exc).__name__}: {exc}"

    # ── Committed: provider topups remaining ──────────────────────────
    from services import provider_balance
    try:
        provider_rows = await provider_balance.fetch_all_balances()
    except Exception:
        provider_rows = []
    committed_total = 0.0
    committed_breakdown = []
    for b in provider_rows:
        # Only count providers with a real USD balance (skip free-tier
        # and unconfigured ones — they don't tie up cash).
        if b.get("tier") in ("free", "unconfigured"):
            continue
        bal = b.get("balance_usd")
        if bal is None:
            bal = b.get("total_balance")
        if bal is None:
            continue
        try:
            bal = float(bal)
        except (TypeError, ValueError):
            continue
        committed_total += bal
        committed_breakdown.append({
            "slug": b.get("slug"),
            "name": b.get("display_name") or b.get("slug"),
            "balance_usd": round(bal, 2),
            "tier": b.get("tier"),
            "daily_burn_usd": b.get("daily_burn_usd"),
            "days_until_empty": b.get("days_until_empty"),
        })

    # ── Client liabilities: credits held in client wallets ────────────
    # Credits × blended cost = USD the operator owes as compute.
    from services.costing.blended_cost import get_blended_cost_per_credit
    _bc = await get_blended_cost_per_credit()
    blended = _bc["value"]
    wallet_pipeline = [
        {"$group": {
            "_id": None,
            "total_credits": {"$sum": "$balance_credits"},
            "reserved_credits": {"$sum": "$reserved_credits"},
            "users": {"$sum": 1},
        }}
    ]
    try:
        wrows = await db.wallets.aggregate(wallet_pipeline).to_list(1)
    except Exception:
        wrows = []
    w = wrows[0] if wrows else {}
    total_credits = float(w.get("total_credits", 0) or 0)
    reserved_credits = float(w.get("reserved_credits", 0) or 0)
    client_liability_usd = round(total_credits * blended, 4)

    # ── Revenue + spend last 30 days ──────────────────────────────────
    from services import revenue_service
    try:
        rev_30d = await revenue_service.total_revenue(days=30)
    except Exception:
        rev_30d = 0.0

    # Spend: sum cost_usd across both log collections for last 30d
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    spend_pipeline = [
        {"$match": {"$or": [
            {"created_at": {"$gte": cutoff}},
            {"timestamp":  {"$gte": cutoff}},
        ]}},
        {"$group": {
            "_id": None,
            "cost": {"$sum": {"$ifNull": ["$cost_usd", "$estimated_cost_usd"]}},
            "calls": {"$sum": 1},
        }},
    ]
    try:
        legacy_spend = await db.usage_logs.aggregate(spend_pipeline).to_list(1)
        gw_spend     = await db.gateway_usage_logs.aggregate(spend_pipeline).to_list(1)
    except Exception:
        legacy_spend, gw_spend = [], []
    spend_30d = sum(
        (rows[0].get("cost", 0) or 0) for rows in (legacy_spend, gw_spend) if rows
    )
    calls_30d = sum(
        (rows[0].get("calls", 0) or 0) for rows in (legacy_spend, gw_spend) if rows
    )

    # ── Runway: how many days of burn the committed balance covers ────
    daily_burn = sum(
        (b.get("daily_burn_usd") or 0) for b in committed_breakdown
    )
    if daily_burn > 0 and committed_total > 0:
        runway_days = round(committed_total / daily_burn, 1)
    else:
        runway_days = None

    # ── Net position: liquid + committed − liabilities ────────────────
    liquid = (stripe_balance.get("available_usd") or 0) + (stripe_balance.get("pending_usd") or 0)
    net_position_usd = round(liquid + committed_total - client_liability_usd, 2)

    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "liquid_stripe": stripe_balance,
        "committed_providers": {
            "total_usd": round(committed_total, 2),
            "providers": committed_breakdown,
            "daily_burn_usd": round(daily_burn, 4),
            "runway_days": runway_days,
        },
        "client_liabilities": {
            "total_credits": int(total_credits),
            "reserved_credits": int(reserved_credits),
            "blended_cost_per_credit": blended,
            "usd_value": client_liability_usd,
            "note": "USD worth of compute owed to clients at current blended cost.",
        },
        "last_30_days": {
            "revenue_usd": round(rev_30d, 2),
            "spend_usd": round(spend_30d, 4),
            "calls": calls_30d,
            "gross_margin_usd": round(rev_30d - spend_30d, 2),
            "gross_margin_pct": round(((rev_30d - spend_30d) / rev_30d * 100), 2) if rev_30d > 0 else None,
        },
        "net_position_usd": net_position_usd,
        "net_position_formula": "liquid_stripe + committed_providers − client_liabilities",
    }


async def _run_sync(fn, *args, **kwargs):
    """Run a sync function in a thread pool — used for Stripe SDK calls
    which are sync but need to be awaited without blocking the event loop."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))


# ---------------------------------------------------------------------------
# Product Readiness — "what can I sell today, what needs configuration"
# ---------------------------------------------------------------------------

@router.get("/admin/product-readiness")
async def admin_product_readiness(_: User = Depends(require_admin)):
    """Single view of every product surface: what's live, what's
    partial, what needs credentials. Before shipping marketing copy
    that promises a feature, check this endpoint.

    Each entry carries:
      - status: 'live' | 'needs_config' | 'partial' | 'vapor'
      - requires: list of env vars / accounts needed
      - setup_url: where to register / get the key
      - notes: anything the operator should know
    """
    import os

    def has_env(*keys: str) -> bool:
        return all(os.environ.get(k) for k in keys)

    async def _integration(name: str) -> bool:
        try:
            from routes.integrations import get_integration_keys
            keys = await get_integration_keys()
            return bool((keys.get(name) or {}).get("api_key"))
        except Exception:
            return False

    # Check each capability
    sendgrid_ok = (await _integration("sendgrid")) or has_env("SENDGRID_API_KEY")
    resend_ok   = (await _integration("resend"))   or has_env("RESEND_API_KEY")
    email_ok = sendgrid_ok or resend_ok

    features = [
        {
            "capability": "Chat + 50+ Agents",
            "status": "live",
            "notes": "Core chat with specialist agents (marketing, sales, socialmedia, email, growthhacker, etc.). Fully billed through Gateway credits.",
        },
        {
            "capability": "Image Generation (free-first + enhanced)",
            "status": "live",
            "notes": "Pollinations.ai (free, unlimited Flux) → Gemini → gpt-image-1 → DALL-E 3 fallback chain. Prompt enhancer auto-upgrades briefs via free-tier LLM. 99%+ of images can route free.",
        },
        {
            "capability": "Video Generation",
            "status": "live",
            "requires": ["OPENAI_API_KEY"],
            "notes": "Sora-2 only for now. $0.40/4s. Gates to Basic+ plans. Add Runway/Pika to lower the floor.",
        },
        {
            "capability": "Content Generation + Style Blueprints",
            "status": "live",
            "notes": "8 content types through the Gateway.",
        },
        {
            "capability": "TTS / Voice-over (free premium)",
            "status": "live",
            "notes": "Edge TTS (Microsoft, 400+ neural voices, $0) → OpenAI tts-1 → ElevenLabs. Edge quality matches ElevenLabs for 95% of use cases.",
        },
        {
            "capability": "Lead Research (free + paid)",
            "status": "live" if (has_env("APOLLO_API_KEY") or has_env("HUNTER_API_KEY")) else "needs_config",
            "requires": ["Either APOLLO_API_KEY ($49/mo) OR HUNTER_API_KEY (free tier 25/mo)"],
            "setup_url": "https://hunter.io/api-keys (free) or https://app.apollo.io (paid)",
            "notes": "Auto-selects: Apollo if key present, else Hunter. Campaign orchestrator works with either.",
        },
        {
            "capability": "Email Event Webhooks (bounce/open/click/complaint)",
            "status": "live",
            "notes": "Auto-suppresses hard bounces + spam complaints → protects domain reputation. POST /api/email-events/sendgrid and /resend.",
        },
        {
            "capability": "Referral Program (zero-CAC acquisition)",
            "status": "live",
            "notes": "Operator-configurable reward policy via MAARS_REFERRAL_PCT + MAARS_REFERRAL_FLAT_CR. Public link: /r/<code>. User dashboard: /api/referrals/me.",
        },
        {
            "capability": "Customer Webhooks (SaaS integration)",
            "status": "live",
            "notes": "Customers subscribe via POST /api/webhooks. HMAC-SHA256 signed delivery with 3 retries + dead-letter. 8 event types.",
        },
        {
            "capability": "Background Scheduler (24/7 auto-fire)",
            "status": "live",
            "notes": "30s tick, 4 dispatchers. /admin/scheduler/status shows queue counts.",
        },
        {
            "capability": "Cold Email (transport + compliance)",
            "status": "live" if email_ok else "needs_config",
            "requires": ["SENDGRID_API_KEY or RESEND_API_KEY", "Domain SPF + DKIM records"],
            "setup_url": "https://app.sendgrid.com / https://resend.com",
            "notes": "List-Unsubscribe + Message-ID stamped. Suppression list enforced pre-send.",
        },
        {
            "capability": "Unsubscribe endpoint",
            "status": "live",
            "notes": "/api/unsubscribe with HMAC-signed tokens. Gmail one-click compliant.",
        },
        {
            "capability": "Campaign Orchestrator (leads → drafts → scheduled sends)",
            "status": "live" if ((has_env("APOLLO_API_KEY") or has_env("HUNTER_API_KEY")) and email_ok) else "needs_config",
            "requires": ["Any lead provider (Apollo or Hunter) + any email provider (SendGrid or Resend)"],
            "notes": "run_campaign tool available to all outbound agents. Pause/resume + customer-webhook events supported.",
        },
        {
            "capability": "LinkedIn Posting",
            "status": "live" if has_env("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET") else "needs_config",
            "requires": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_REDIRECT_URI", "Each user completes OAuth"],
            "setup_url": "https://www.linkedin.com/developers/apps",
            "notes": "Approval can take 3-14 days for Community Management API.",
        },
        {
            "capability": "X (Twitter) Posting",
            "status": "vapor",
            "requires": ["X Developer Basic tier ($200/mo)"],
            "setup_url": "https://developer.twitter.com/en/portal",
            "notes": "Adapter not yet wired. Free tier can no longer post.",
        },
        {
            "capability": "Meta (Facebook/Instagram) Posting",
            "status": "vapor",
            "requires": ["Meta Business verification", "App Review approval"],
            "setup_url": "https://developers.facebook.com/apps",
            "notes": "Adapter not yet wired. ~1 week approval if business is verified.",
        },
        {
            "capability": "Cold Calling (Twilio)",
            "status": "partial" if has_env("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER") else "needs_config",
            "requires": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "A2P 10DLC registration for US"],
            "setup_url": "https://console.twilio.com",
            "notes": "Outbound initiate works. No inbound webhook handler for responses yet.",
        },
        {
            "capability": "Stripe Checkout → Wallet",
            "status": "live" if has_env("STRIPE_SECRET_KEY") else "needs_config",
            "requires": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
            "notes": "Plan subscriptions + credit packages → wallet.grant() on webhook.",
        },
        {
            "capability": "Live Stripe Balance",
            "status": "live" if (has_env("STRIPE_RESTRICTED_KEY") or has_env("STRIPE_SECRET_KEY")) else "needs_config",
            "requires": ["STRIPE_RESTRICTED_KEY (balance:read) or STRIPE_SECRET_KEY"],
            "notes": "Visible in /admin/cash-position.",
        },
    ]

    summary = {
        "live":         sum(1 for f in features if f["status"] == "live"),
        "needs_config": sum(1 for f in features if f["status"] == "needs_config"),
        "partial":      sum(1 for f in features if f["status"] == "partial"),
        "vapor":        sum(1 for f in features if f["status"] == "vapor"),
        "total":        len(features),
    }

    # Ordered by "unblock-me first": live-count boost > revenue risk
    fastest_unlocks = [
        f for f in features
        if f["status"] == "needs_config"
    ][:3]

    return {
        "summary": summary,
        "features": features,
        "fastest_unlocks": fastest_unlocks,
        "as_of": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Cost health — the six metrics that tell you where money leaks
# ---------------------------------------------------------------------------

@router.get("/admin/gateway/cost-health")
async def cost_health(
    days: int = Query(7, ge=1, le=90),
    _: User = Depends(require_admin),
):
    """The 6-metric cost-optimization dashboard.

    Designed to answer "where is money leaking?" at a glance:
      1. cost_per_credit     — operator cost per credit delivered (lower = better)
      2. free_absorption_pct — share of calls absorbed by free-tier providers
      3. cache_hit_pct       — semantic-cache hit rate
      4. escalation_pct      — how often the cheap-first cascade escalates to a paid model
      5. retry_multiplier    — total provider calls / total user requests (>1 = retries)
      6. free_quota_util     — per-provider free-tier utilisation

    Each metric carries a `target` the operator should aim for. Anything
    red below target is a concrete fix to execute.
    """
    since = _window_start(days)

    if not await _collection_exists("gateway_usage_logs"):
        return {"ok": True, "empty": True, "as_of": datetime.now(timezone.utc).isoformat()}

    # Top-level totals. Field names track the actual columns written by
    # llm_gateway.complete() + v1_gateway so the dashboard lights up
    # without requiring log-schema migrations.
    pipeline_totals = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": None,
            "calls":         {"$sum": 1},
            "cost_usd":      {"$sum": {"$ifNull": ["$cost_usd", 0]}},
            "billed_usd":    {"$sum": {"$ifNull": ["$billed_usd", 0]}},
            "credits":       {"$sum": {"$ifNull": ["$credits_charged", 0]}},
            # cache-hit flag is stored as `from_cache` (bool); some older
            # rows use `was_cached` — accept either.
            "cache_hits":    {"$sum": {"$cond": [
                {"$or": [
                    {"$eq": ["$from_cache", True]},
                    {"$eq": ["$was_cached", True]},
                ]}, 1, 0]}},
            "escalations":   {"$sum": {"$cond": [{"$eq": ["$cascade_escalated", True]}, 1, 0]}},
            "cheap_tries":   {"$sum": {"$cond": [{"$ne": ["$cascade_outcome", None]}, 1, 0]}},
            "retries":       {"$sum": {"$ifNull": ["$retry_count", 0]}},
            "quality_retries": {"$sum": {"$cond": [
                {"$gt": [{"$ifNull": ["$quality_retry_depth", 0]}, 0]}, 1, 0]}},
        }},
    ]
    tot_docs = await db.gateway_usage_logs.aggregate(pipeline_totals).to_list(1)
    tot = tot_docs[0] if tot_docs else {}
    calls = int(tot.get("calls") or 0)
    credits = float(tot.get("credits") or 0)
    cost_usd = float(tot.get("cost_usd") or 0)

    # Per-provider breakdown for free-tier absorption + free-quota util.
    # Uses the shared free-provider set so this endpoint and the Pricing
    # Manager tab agree on what counts as "free".
    from shared.free_providers import FREE_PROVIDERS as FREE_TIER_PROVIDERS
    by_provider = await db.gateway_usage_logs.aggregate([
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": {"provider": "$provider"},
            "calls":     {"$sum": 1},
            "cost_usd":  {"$sum": {"$ifNull": ["$cost_usd", 0]}},
        }},
        {"$sort": {"calls": -1}},
    ]).to_list(100)
    free_calls = sum(r["calls"] for r in by_provider
                     if (r["_id"].get("provider") or "").lower() in FREE_TIER_PROVIDERS)

    # Aggregator warm-pool hit count — calls that reached HF / OpenRouter /
    # Bytez / Novita / Together / Fireworks via routing (not explicit
    # passthrough). This tells the operator whether the expanded 176k+
    # catalog is actually pulling its weight.
    AGGREGATORS = {"huggingface", "openrouter", "bytez", "novita", "together", "fireworks"}
    aggregator_calls = sum(r["calls"] for r in by_provider
                           if (r["_id"].get("provider") or "").lower() in AGGREGATORS)
    aggregator_hit_pct = round(100.0 * aggregator_calls / calls, 2) if calls else 0.0

    # Metric 1: cost per credit
    cost_per_credit = round(cost_usd / credits, 6) if credits > 0 else 0.0

    # Metric 2: free-provider absorption
    free_abs_pct = round(100.0 * free_calls / calls, 2) if calls else 0.0

    # Metric 3: cache hit rate
    cache_hit_pct = round(100.0 * int(tot.get("cache_hits") or 0) / calls, 2) if calls else 0.0

    # Metric 4: cascade escalation rate
    cheap_tries = int(tot.get("cheap_tries") or 0)
    escalations = int(tot.get("escalations") or 0)
    escalation_pct = round(100.0 * escalations / cheap_tries, 2) if cheap_tries else None

    # Metric 5: retry multiplier — total provider calls / (calls - retries).
    # When retry_count is 0 on every row, multiplier = 1.0. As retries happen,
    # the denominator shrinks and the ratio grows.
    retries = int(tot.get("retries") or 0)
    unique_req = max(1, calls - retries)
    retry_mult = round(calls / unique_req, 3)

    # Metric 6: free-quota util — how deep into each free provider's daily
    # allotment we are. Pulled from free_quota_tracker if available, else
    # best-effort approximation from call count.
    try:
        from services import free_quota_tracker as fqt
        quota_util = await fqt.utilisation_snapshot()
    except Exception:
        quota_util = {
            r["_id"].get("provider"): {"calls_today": r["calls"], "cap": None, "util_pct": None}
            for r in by_provider
            if (r["_id"].get("provider") or "").lower() in FREE_TIER_PROVIDERS
        }

    targets = {
        "cost_per_credit":     {"target": 0.0002, "unit": "USD/credit", "direction": "low"},
        "free_absorption_pct": {"target": 85.0,   "unit": "%", "direction": "high"},
        "cache_hit_pct":       {"target": 40.0,   "unit": "%", "direction": "high"},
        "escalation_pct":      {"target": 15.0,   "unit": "%", "direction": "low"},
        "retry_multiplier":    {"target": 1.05,   "unit": "x", "direction": "low"},
    }

    return {
        "ok":           True,
        "as_of":        datetime.now(timezone.utc).isoformat(),
        "window_days":  days,
        "totals": {
            "calls":     calls,
            "credits":   round(credits, 2),
            "cost_usd":  round(cost_usd, 4),
            "billed_usd": round(float(tot.get("billed_usd") or 0), 4),
        },
        "metrics": {
            "cost_per_credit":     cost_per_credit,
            "free_absorption_pct": free_abs_pct,
            "cache_hit_pct":       cache_hit_pct,
            "escalation_pct":      escalation_pct,
            "retry_multiplier":    retry_mult,
            "aggregator_hit_pct":  aggregator_hit_pct,  # % of calls served by warm pool (HF/OpenRouter/etc.)
            "aggregator_calls":    aggregator_calls,
            # Quality-gate retry rate: how often a cheap-model call's output
            # scored too low and was silently retried on a premium model.
            # Target: 3-8% (high enough that the gate is doing work; low
            # enough that cheap models usually suffice).
            "quality_retry_pct":   round(100.0 * int(tot.get("quality_retries") or 0) / calls, 2) if calls else 0.0,
            "quality_retries":     int(tot.get("quality_retries") or 0),
            "free_quota_util":     quota_util,
        },
        "targets":   targets,
        "providers": [
            {"provider": r["_id"].get("provider") or "unknown",
             "calls":     r["calls"],
             "cost_usd":  round(r["cost_usd"], 4),
             "free_tier": (r["_id"].get("provider") or "").lower() in FREE_TIER_PROVIDERS}
            for r in by_provider
        ],
    }


@router.get("/admin/gateway/model-activation")
async def model_activation(_: User = Depends(require_admin)):
    """Report on model reachability — how many of the 612 registered
    models are live (configured + routable) vs dormant. Also exposes
    the meta-aggregator passthroughs (HuggingFace 175k+, OpenRouter,
    Bytez, Novita, Together, Fireworks) that expand the universe
    beyond the catalogued registry."""
    from services.routing import model_activator
    report = await model_activator.activation_report()

    # Cross-check against actual 30-day traffic so we can flag any model
    # that's CLASSIFIED live but hasn't seen a single call yet.
    since = _window_start(30)
    if await _collection_exists("gateway_usage_logs"):
        active_pairs = set()
        async for row in db.gateway_usage_logs.aggregate([
            {"$match": {"timestamp": {"$gte": since}}},
            {"$group": {"_id": {"p": "$provider", "m": "$native_model"}}},
        ]):
            p = (row["_id"].get("p") or "").lower()
            m = row["_id"].get("m") or ""
            if p and m:
                active_pairs.add((p, m))
        report["active_in_last_30_days"] = len(active_pairs)
    else:
        report["active_in_last_30_days"] = 0

    return report
