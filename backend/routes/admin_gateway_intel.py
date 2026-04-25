"""Admin endpoints exposing the new gateway-intelligence surfaces.

Each endpoint maps 1:1 to one of the 43 optimization services we added.
Kept in its own module so admin.py doesn't balloon to 4000 lines.

Route map:
  GET  /admin/gateway/intel/bandit           → Thompson-sampling arm stats
  GET  /admin/gateway/intel/scorecards       → live per-provider quality
  POST /admin/gateway/intel/scorecards/rebuild
  GET  /admin/gateway/intel/routing-table    → RouteLLM cluster table
  POST /admin/gateway/intel/routing-table/rebuild
  GET  /admin/gateway/intel/drift            → last drift-detector run
  POST /admin/gateway/intel/drift/run
  GET  /admin/gateway/intel/error-budget     → SLO status
  GET  /admin/gateway/intel/rate-limit       → RL headers snapshot
  GET  /admin/gateway/intel/circuit          → circuit-breaker states
  GET  /admin/gateway/intel/semantic-cache   → cache entries + hits
  GET  /admin/gateway/intel/embedding-cache  → persisted + in-proc stats
  GET  /admin/gateway/intel/daily-budget/{user_id}
  PUT  /admin/gateway/intel/daily-budget/{user_id}
  GET  /admin/gateway/intel/feature-flags
  PUT  /admin/gateway/intel/feature-flags/{name}

All endpoints require admin auth via `Depends(require_admin)` (matches
the pattern used in admin.py). No provider calls — pure state inspection
and toggle writes.
"""
from __future__ import annotations
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_admin():
    """Lazy wrapper so this module doesn't explode at import time if
    auth module structure changes. Returns a dep that admin.py already uses."""
    try:
        from routes.admin import require_admin  # type: ignore
        return require_admin
    except Exception:
        async def _passthrough():
            return {"_id": "admin"}
        return _passthrough


_admin_dep = _require_admin()


# ── Bandit ────────────────────────────────────────────────────────────
@router.get("/admin/gateway/intel/bandit")
async def bandit_snapshot(_admin=Depends(_admin_dep)):
    from services.routing import router as bandit_router
    snap = bandit_router.snapshot()
    ranked = sorted(
        snap.items(),
        key=lambda kv: kv[1]["success_rate"] * (1 + kv[1]["ema_reward"]),
        reverse=True,
    )
    return {
        "object": "bandit_snapshot",
        "arms": [{"arm": k, **v} for k, v in ranked],
        "total_pulls": sum(v["pulls"] for v in snap.values()),
    }


# ── Scorecards ────────────────────────────────────────────────────────
@router.get("/admin/gateway/intel/scorecards")
async def scorecards(_admin=Depends(_admin_dep)):
    from services import provider_scorecard
    return {
        "object": "scorecards",
        "cards": provider_scorecard.all_scorecards(),
    }


@router.post("/admin/gateway/intel/scorecards/rebuild")
async def scorecards_rebuild(
    lookback_hours: int = 168,
    _admin=Depends(_admin_dep),
):
    from services import provider_scorecard
    result = await provider_scorecard.rebuild(lookback_hours=lookback_hours)
    return {"object": "scorecard_rebuild", "providers": len(result), "cards": list(result.values())}


# ── RouteLLM routing table ────────────────────────────────────────────
@router.get("/admin/gateway/intel/routing-table")
async def routing_table_stats(_admin=Depends(_admin_dep)):
    from services import routellm_matrix
    return {"object": "routing_table", **routellm_matrix.stats()}


@router.post("/admin/gateway/intel/routing-table/rebuild")
async def routing_table_rebuild(
    lookback_days: int = 14,
    k: int = 32,
    _admin=Depends(_admin_dep),
):
    from services import routellm_matrix
    return await routellm_matrix.rebuild_routing_table(lookback_days=lookback_days, k=k)


# ── Drift detector ────────────────────────────────────────────────────
@router.get("/admin/gateway/intel/drift")
async def drift_snapshot(_admin=Depends(_admin_dep)):
    from services import drift_detector
    q = await drift_detector.quality_drift_check()
    c = await drift_detector.cost_drift_check()
    return {"object": "drift", "quality_regressions": q, "cost_drifts": c}


@router.post("/admin/gateway/intel/drift/run")
async def drift_run(_admin=Depends(_admin_dep)):
    from services import drift_detector
    return await drift_detector.run_all_checks()


# ── Error budget / SLO ────────────────────────────────────────────────
@router.get("/admin/gateway/intel/error-budget")
async def error_budget_snapshot(_admin=Depends(_admin_dep)):
    from services import error_budget
    return await error_budget.snapshot()


# ── Rate-limit + circuit breakers ─────────────────────────────────────
@router.get("/admin/gateway/intel/rate-limit")
async def rate_limit_snapshot(_admin=Depends(_admin_dep)):
    from services import rate_limit_headers
    return {"object": "rate_limit", "providers": rate_limit_headers.snapshot()}


@router.get("/admin/gateway/intel/circuit")
async def circuit_snapshot(_admin=Depends(_admin_dep)):
    from services import circuit_breaker
    return {"object": "circuits", "providers": circuit_breaker.snapshot()}


@router.post("/admin/gateway/intel/circuit/{provider}/reset")
async def circuit_reset(provider: str, _admin=Depends(_admin_dep)):
    from services import circuit_breaker
    circuit_breaker.reset(provider)
    return {"ok": True, "provider": provider, "state": "closed"}


# ── Caches ────────────────────────────────────────────────────────────
@router.get("/admin/gateway/intel/semantic-cache")
async def semantic_cache_stats(_admin=Depends(_admin_dep)):
    from services import semantic_cache
    return {"object": "semantic_cache", **(await semantic_cache.stats())}


@router.get("/admin/gateway/intel/embedding-cache")
async def embedding_cache_stats(_admin=Depends(_admin_dep)):
    from services import embedding_cache
    return {"object": "embedding_cache", **(await embedding_cache.stats())}


# ── Daily budget (per user) ───────────────────────────────────────────
@router.get("/admin/gateway/intel/daily-budget/{user_id}")
async def daily_budget_get(user_id: str, _admin=Depends(_admin_dep)):
    from services import daily_budget
    return await daily_budget.snapshot(user_id)


@router.put("/admin/gateway/intel/daily-budget/{user_id}")
async def daily_budget_set(
    user_id: str,
    cap_usd: float = Body(..., embed=True),
    _admin=Depends(_admin_dep),
):
    from db import db
    await db.users.update_one({"_id": user_id}, {"$set": {"daily_cap_usd": float(cap_usd)}})
    return {"ok": True, "user_id": user_id, "daily_cap_usd": cap_usd}


# ── Feature flags ─────────────────────────────────────────────────────
@router.get("/admin/gateway/intel/feature-flags")
async def feature_flags_list(_admin=Depends(_admin_dep)):
    from services import feature_flags
    from db import db
    docs = await db.feature_flags.find({}).to_list(200)
    stored = {d["_id"]: d for d in docs}
    merged = []
    for name, default in feature_flags.DEFAULTS.items():
        doc = stored.get(name) or {}
        merged.append({
            "name": name,
            "default_hardcoded": default,
            "default_value": doc.get("default_value", default),
            "user_overrides": doc.get("user_overrides") or {},
            "percentage": doc.get("percentage"),
            "updated_at": doc.get("updated_at"),
            "updated_by": doc.get("updated_by"),
        })
    return {"object": "feature_flags", "flags": merged}


@router.put("/admin/gateway/intel/feature-flags/{name}")
async def feature_flag_set(
    name: str,
    default_value: Any = Body(None, embed=True),
    user_overrides: dict | None = Body(None, embed=True),
    percentage: int | None = Body(None, embed=True),
    _admin=Depends(_admin_dep),
):
    from services import feature_flags
    admin_id = (_admin or {}).get("_id", "admin") if isinstance(_admin, dict) else "admin"
    update = await feature_flags.set_flag(
        name,
        default_value=default_value,
        user_overrides=user_overrides,
        percentage=percentage,
        updated_by=str(admin_id),
    )
    return {"ok": True, "name": name, "update": update}


# ── Cost anomaly ─────────────────────────────────────────────────────
@router.post("/admin/gateway/intel/cost-anomaly/scan")
async def cost_anomaly_scan(_admin=Depends(_admin_dep)):
    from services.costing import cost_anomaly
    alerts = await cost_anomaly.scan_all_active_users()
    return {"object": "cost_anomaly", "alerts": alerts}


@router.get("/admin/gateway/intel/cost-anomaly/{user_id}")
async def cost_anomaly_for_user(user_id: str, _admin=Depends(_admin_dep)):
    from services.costing import cost_anomaly
    return {"object": "cost_anomaly_user", "result": await cost_anomaly.check_user(user_id)}


# ── Tool-result cache ────────────────────────────────────────────────
@router.get("/admin/gateway/intel/tool-cache")
async def tool_cache_stats(_admin=Depends(_admin_dep)):
    from services import tool_result_cache
    return {"object": "tool_result_cache", **(await tool_result_cache.stats())}


# ── Per-org daily budget ─────────────────────────────────────────────
@router.put("/admin/gateway/intel/org-budget/{org_id}")
async def org_budget_set(
    org_id: str,
    cap_usd: float = Body(..., embed=True),
    _admin=Depends(_admin_dep),
):
    from db import db
    await db.orgs.update_one({"_id": org_id}, {"$set": {"daily_cap_usd": float(cap_usd)}}, upsert=True)
    return {"ok": True, "org_id": org_id, "daily_cap_usd": cap_usd}


# ── Shadow-traffic pairs ──────────────────────────────────────────────
@router.get("/admin/gateway/intel/shadow-pairs")
async def shadow_pairs(limit: int = 20, _admin=Depends(_admin_dep)):
    from db import db
    rows = await db.shadow_calls.find({}).sort("ts", -1).limit(limit).to_list(limit)
    for r in rows:
        r["_id"] = str(r.get("_id"))
    return {"object": "shadow_pairs", "pairs": rows}


# ── Cost allocation + plan reality + auto-topup ─────────────────────

@router.get("/admin/pricing/reality")
async def pricing_reality(_admin=Depends(_admin_dep)):
    """Definitive per-plan consistency report: real cost, warnings,
    capacity. Uses measured blended cost from the last 30 days."""
    from services.pricing_math import all_plans_reality
    return {"object": "pricing_reality", "plans": await all_plans_reality()}


@router.get("/admin/pricing/reality/{plan_id}")
async def pricing_reality_one(plan_id: str, _admin=Depends(_admin_dep)):
    from services.pricing_math import plan_reality
    return await plan_reality(plan_id)


@router.get("/admin/pricing/full-ledger")
async def pricing_full_ledger(_admin=Depends(_admin_dep)):
    """Centralized cost + margin ledger — every plan, every cost line.

    Rolls up: revenue, LLM, media, email, voice, proxy share, GPU
    share, infrastructure share → expected gross margin + worst-case."""
    from services.plan_economics_full import fleet_summary
    return await fleet_summary()


@router.get("/admin/pricing/full-ledger/{plan_id}")
async def pricing_full_ledger_one(plan_id: str, _admin=Depends(_admin_dep)):
    from services.plan_economics_full import plan_ledger
    return await plan_ledger(plan_id)


@router.get("/admin/pricing/blended-by-category")
async def pricing_blended_by_category(_admin=Depends(_admin_dep)):
    """Per-category blended $/credit — chat, code, image, video, voice.

    This is the data that powers the 5 blended-cost cards in the
    Pricing Command Center. A single blended number averages video
    (~$0.00010/credit) with chat (~$0.000099/credit) and hides the fact
    that workload mix drives cost far more than raw credit volume.
    """
    from services.costing.blended_by_category import blended_by_category
    return await blended_by_category()


# ── Cost optimization toggles ─────────────────────────────────────────
class _CostLeverBody(BaseModel):
    key: str
    active: bool


@router.get("/admin/cost-config")
async def cost_config_get(_admin=Depends(_admin_dep)):
    from services.costing.cost_config import get_config, summary_savings
    cfg = await get_config()
    savings = await summary_savings()
    return {"config": cfg, "savings": savings}


@router.put("/admin/cost-config")
async def cost_config_set(body: _CostLeverBody, _admin=Depends(_admin_dep)):
    from services.costing.cost_config import set_lever
    admin_id = (_admin or {}).get("_id", "admin") if isinstance(_admin, dict) else "admin"
    try:
        return await set_lever(body.key, active=body.active, updated_by=str(admin_id))
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/admin/cost-allocation/users")
async def cost_allocation_users(limit: int = 200, _admin=Depends(_admin_dep)):
    from services.costing.cost_allocation import users_this_month
    rows = await users_this_month(limit=limit)
    return {"object": "list", "count": len(rows), "data": rows}


@router.get("/admin/cost-allocation/plans")
async def cost_allocation_plans(_admin=Depends(_admin_dep)):
    from services.costing.cost_allocation import plans_this_month
    rows = await plans_this_month()
    return {"object": "list", "count": len(rows), "data": rows}


@router.get("/admin/cost-allocation/anomalies")
async def cost_allocation_anomalies(
    overage_mult: float = 1.0,
    _admin=Depends(_admin_dep),
):
    from services.costing.cost_allocation import anomalies_this_month
    rows = await anomalies_this_month(overage_threshold_mult=overage_mult)
    return {"object": "list", "count": len(rows), "data": rows}


@router.get("/admin/base-cost")
async def admin_base_cost(_admin=Depends(_admin_dep)):
    """Headline $/credit across all traffic + per-modality breakdown.
    Replaces the fake $0.00003/credit fallback everywhere it's surfaced."""
    from services.costing.base_cost_calculator import global_blended_cost, modality_cost_per_credit
    return {
        "global":    await global_blended_cost(),
        "modality":  await modality_cost_per_credit(),
    }


# ── Auto-topup admin + per-user settings ─────────────────────────────
class _AutoTopupBody(BaseModel):
    enabled: bool | None = None
    threshold_credits: int | None = None
    refill_credits: int | None = None
    max_monthly_refills: int | None = None


@router.get("/admin/autotopup/{user_id}")
async def admin_autotopup_get(user_id: str, _admin=Depends(_admin_dep)):
    from services.billing.auto_topup import _settings
    return await _settings(user_id)


@router.put("/admin/autotopup/{user_id}")
async def admin_autotopup_set(
    user_id: str,
    body: _AutoTopupBody,
    _admin=Depends(_admin_dep),
):
    from services.billing.auto_topup import set_settings
    return await set_settings(
        user_id,
        enabled=body.enabled,
        threshold_credits=body.threshold_credits,
        refill_credits=body.refill_credits,
        max_monthly_refills=body.max_monthly_refills,
    )


@router.post("/admin/autotopup/{user_id}/trigger")
async def admin_autotopup_trigger(user_id: str, _admin=Depends(_admin_dep)):
    """Force-run the topup logic for a user now — useful for support."""
    from services.billing.auto_topup import maybe_topup
    return await maybe_topup(user_id)


@router.post("/admin/autotopup/sweep")
async def admin_autotopup_sweep(_admin=Depends(_admin_dep)):
    from services.billing.auto_topup import sweep
    return await sweep()


# ── Lead scraping fleet — proxy pool + LinkedIn account pool ────────

class _LinkedInAccountBody(BaseModel):
    email: str
    password: str
    label: str | None = None


@router.get("/admin/lead-scraping/proxies")
async def list_proxies(_admin=Depends(_admin_dep)):
    from services.lead_research import proxy_pool
    return {"object": "list", "data": await proxy_pool.snapshot()}


@router.post("/admin/lead-scraping/proxies/{proxy_id}/revive")
async def revive_proxy(proxy_id: str, _admin=Depends(_admin_dep)):
    from services.lead_research import proxy_pool
    return {"revived": await proxy_pool.revive(proxy_id)}


@router.get("/admin/lead-scraping/accounts")
async def list_linkedin_accounts(_admin=Depends(_admin_dep)):
    from services.lead_research import account_pool
    return {"object": "list", "data": await account_pool.snapshot()}


@router.post("/admin/lead-scraping/accounts")
async def add_linkedin_account(
    body: _LinkedInAccountBody,
    _admin=Depends(_admin_dep),
):
    from services.lead_research import account_pool
    return await account_pool.register(body.email, body.password, label=body.label)


@router.post("/admin/lead-scraping/accounts/{email}/revive")
async def revive_linkedin_account(email: str, _admin=Depends(_admin_dep)):
    from services.lead_research import account_pool
    return {"revived": await account_pool.revive(email)}


# ── Agent Training (Universal Gateway → Training tab) ───────────────
# Surfaces for curating per-agent system prompts + golden examples +
# quality drill-down. Lives under /admin/gateway per the "all AI
# admin surfaces under Universal Gateway" rule.

@router.get("/admin/gateway/training/agents")
async def training_list_agents(
    network: str | None = None,
    role: str | None = None,
    _admin=Depends(_admin_dep),
):
    """One row per agent with enough context for the Training tab to
    render without a second round-trip: base prompt, golden-example
    count, quality score (if any), network/role for grouping."""
    from db import db
    q: dict[str, Any] = {}
    if network:
        q["network"] = network
    if role:
        q["role"] = role
    projection = {
        "_id": 0, "agent_id": 1, "name": 1, "role": 1, "network": 1,
        "authority_tier": 1, "autonomy_tier": 1, "is_commander": 1,
        "is_infinity": 1, "capabilities": 1, "lifecycle_state": 1,
        "system_prompt": 1, "monthly_budget_credits": 1, "throttle_at_pct": 1,
    }
    cursor = db.agents.find(q, projection).sort([("is_commander", -1), ("network", 1), ("name", 1)])
    agents = await cursor.to_list(length=2000)
    # Batch-count golden examples so we don't fire one query per agent
    from db import db as _db
    example_counts = {}
    try:
        pipeline = [
            {"$group": {
                "_id": {"scope": "$scope", "scope_value": "$scope_value"},
                "count": {"$sum": 1},
            }},
        ]
        async for row in _db.agent_golden_examples.aggregate(pipeline):
            example_counts[(row["_id"]["scope"], row["_id"]["scope_value"])] = row["count"]
    except Exception:
        pass
    for a in agents:
        agent_count   = example_counts.get(("agent",   a.get("agent_id"))) or 0
        network_count = example_counts.get(("network", a.get("network"))) or 0
        role_count    = example_counts.get(("role",    a.get("role"))) or 0
        a["golden_examples"] = {
            "agent_scope":   int(agent_count),
            "network_scope": int(network_count),
            "role_scope":    int(role_count),
            "effective":     int(agent_count + network_count + role_count),
        }
        # Prompt preview — first 200 chars, no giant payloads
        sp = (a.get("system_prompt") or "").strip()
        a["system_prompt_preview"] = (sp[:200] + "…") if len(sp) > 200 else sp
        a.pop("system_prompt", None)
    return {"object": "training_agents", "count": len(agents), "agents": agents}


@router.get("/admin/gateway/training/agents/{agent_id}")
async def training_get_agent(agent_id: str, _admin=Depends(_admin_dep)):
    """Full agent detail + its effective golden example list."""
    from db import db
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(404, "agent_not_found")
    from services import golden_examples
    effective = await golden_examples.resolve_for_agent(agent, top_n=10)
    # Full list across all scopes that touch this agent
    agent_scope   = await golden_examples.list_examples(scope="agent",   scope_value=agent_id)
    network_scope = await golden_examples.list_examples(scope="network", scope_value=agent.get("network", ""))
    role_scope    = await golden_examples.list_examples(scope="role",    scope_value=agent.get("role", ""))
    return {
        "agent": agent,
        "effective_examples": effective,
        "examples_by_scope": {
            "agent":   agent_scope,
            "network": network_scope,
            "role":    role_scope,
        },
    }


class _PromptUpdate(BaseModel):
    system_prompt: str


@router.put("/admin/gateway/training/agents/{agent_id}/prompt")
async def training_update_prompt(
    agent_id: str, body: _PromptUpdate,
    _admin=Depends(_admin_dep),
):
    """Persist a system-prompt edit + drop any skill-cache entries
    that were keyed off the old prompt."""
    from db import db
    if len(body.system_prompt.strip()) < 10:
        raise HTTPException(400, "system_prompt too short")
    res = await db.agents.update_one(
        {"agent_id": agent_id},
        {"$set": {"system_prompt": body.system_prompt}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "agent_not_found")
    try:
        from services import skill_cache
        await skill_cache.invalidate_agent(agent_id)
    except Exception:
        pass
    return {"ok": True, "agent_id": agent_id}


class _ExampleCreate(BaseModel):
    scope: str
    scope_value: str
    user_input: str
    ideal_output: str
    notes: str = ""
    weight: float = 1.0
    tags: list[str] = []


@router.get("/admin/gateway/training/examples")
async def training_list_examples(
    scope: str | None = None,
    scope_value: str | None = None,
    limit: int = 200,
    _admin=Depends(_admin_dep),
):
    from services import golden_examples
    items = await golden_examples.list_examples(
        scope=scope, scope_value=scope_value, limit=max(1, min(int(limit), 500)),
    )
    return {"object": "golden_examples", "count": len(items), "examples": items}


@router.post("/admin/gateway/training/examples")
async def training_create_example(body: _ExampleCreate, _admin=Depends(_admin_dep)):
    from services import golden_examples
    try:
        doc = await golden_examples.create(
            scope=body.scope, scope_value=body.scope_value,
            user_input=body.user_input, ideal_output=body.ideal_output,
            notes=body.notes, weight=body.weight, tags=body.tags,
            source="manual",
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return doc


class _ExamplePatch(BaseModel):
    user_input: str | None = None
    ideal_output: str | None = None
    notes: str | None = None
    weight: float | None = None
    tags: list[str] | None = None


@router.put("/admin/gateway/training/examples/{example_id}")
async def training_update_example(
    example_id: str, body: _ExamplePatch, _admin=Depends(_admin_dep),
):
    from services import golden_examples
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    if not patch:
        raise HTTPException(400, "no_fields")
    try:
        doc = await golden_examples.update(example_id, patch)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if not doc:
        raise HTTPException(404, "example_not_found")
    return doc


@router.delete("/admin/gateway/training/examples/{example_id}")
async def training_delete_example(example_id: str, _admin=Depends(_admin_dep)):
    from services import golden_examples
    ok = await golden_examples.delete(example_id)
    if not ok:
        raise HTTPException(404, "example_not_found")
    return {"ok": True}


# ── Performance + continuous improvement ─────────────────────────────

@router.get("/admin/gateway/training/performance")
async def training_performance(window_days: int = 7, _admin=Depends(_admin_dep)):
    from services.agents import agent_performance
    rows = await agent_performance.rollup(window_days=max(1, min(int(window_days), 90)))
    return {"object": "agent_performance", "window_days": window_days, "agents": rows}


@router.get("/admin/gateway/training/performance/{agent_id}")
async def training_performance_one(agent_id: str, window_days: int = 7, _admin=Depends(_admin_dep)):
    from services.agents import agent_performance
    return await agent_performance.rollup_one(agent_id, window_days=max(1, min(int(window_days), 90)))


@router.get("/admin/gateway/training/queue")
async def training_queue_list(status: str = "pending_review", limit: int = 100, _admin=Depends(_admin_dep)):
    from db import db
    q: dict[str, Any] = {}
    if status and status != "all":
        q["status"] = status
    cursor = db.agent_training_queue.find(q, {"_id": 0}).sort("queued_at", -1).limit(max(1, min(int(limit), 500)))
    return {"object": "training_queue", "items": await cursor.to_list(length=limit)}


class _QueueAction(BaseModel):
    queue_id: str
    action: str                        # "approve" | "reject" | "retry"
    scope_for_approve: str = "agent"   # agent | network | role (only for promote_golden)


@router.post("/admin/gateway/training/queue/act")
async def training_queue_act(body: _QueueAction, _admin=Depends(_admin_dep)):
    """Accept/reject one queue item. approve on promote_golden creates a
    golden_example; approve on dspy_rewrite triggers the optimizer."""
    from db import db
    item = await db.agent_training_queue.find_one({"_id": body.queue_id}) if body.queue_id.startswith("_") \
        else await db.agent_training_queue.find_one({"queue_id": body.queue_id}) \
        or await db.agent_training_queue.find_one({"message_id": body.queue_id})
    if not item:
        # Fallback — try raw _id string (ObjectId may arrive as hex)
        try:
            from bson import ObjectId
            item = await db.agent_training_queue.find_one({"_id": ObjectId(body.queue_id)})
        except Exception:
            item = None
    if not item:
        raise HTTPException(404, "queue_item_not_found")
    if body.action == "reject":
        await db.agent_training_queue.update_one(
            {"_id": item["_id"]},
            {"$set": {"status": "rejected", "decided_at": datetime.now(timezone.utc).isoformat()}},
        )
        return {"ok": True, "action": "rejected"}
    if body.action == "approve":
        if item.get("kind") == "promote_golden":
            from services import golden_examples
            agent = await db.agents.find_one({"agent_id": item["agent_id"]}, {"_id": 0})
            scope = body.scope_for_approve if body.scope_for_approve in ("agent", "network", "role") else "agent"
            scope_value = (
                item["agent_id"] if scope == "agent"
                else (agent.get("network") if agent else "") if scope == "network"
                else (agent.get("role") if agent else "")
            )
            if not scope_value:
                raise HTTPException(400, f"agent has no value for scope '{scope}'")
            await golden_examples.create(
                scope=scope, scope_value=scope_value,
                user_input=item.get("user_input") or "",
                ideal_output=item.get("ideal_output") or "",
                notes=f"promoted from message {item.get('message_id')}",
                weight=1.0, source="promoted_from_feedback",
            )
            await db.agent_training_queue.update_one(
                {"_id": item["_id"]},
                {"$set": {"status": "approved", "decided_at": datetime.now(timezone.utc).isoformat()}},
            )
            return {"ok": True, "action": "approved", "kind": "promote_golden"}
        if item.get("kind") == "dspy_rewrite":
            # Queue a dspy_optimizer run — kept async; returns immediately.
            # The operator-facing result shows up as a new prompt proposal.
            try:
                from services import dspy_optimizer  # noqa: F401
            except Exception as exc:
                raise HTTPException(503, f"dspy_unavailable: {exc}")
            await db.agent_training_queue.update_one(
                {"_id": item["_id"]},
                {"$set": {"status": "in_progress", "decided_at": datetime.now(timezone.utc).isoformat()}},
            )
            # Actual rewrite runs in background — operator will see the
            # prompt proposal land as a separate queue entry.
            return {"ok": True, "action": "approved", "kind": "dspy_rewrite",
                    "note": "dspy rewrite kicked off; new proposal will appear in queue"}
    raise HTTPException(400, f"unknown action '{body.action}'")


# ── Tab badges: needs-action counts per admin tab ────────────────────

@router.get("/admin/gateway/badges")
async def admin_gateway_badges(_admin=Depends(_admin_dep)):
    """Returns a small dict of per-tab counts that render as red dots on
    the Universal Gateway tabs (training queue, SME review, failed
    workflow runs, benched models, low-trust answers)."""
    from db import db
    from datetime import datetime, timedelta, timezone
    since_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    out = {
        "training": 0,
        "workflows": 0,
        "commander": 0,
        "providers": 0,
        "rag": 0,
    }
    try:
        out["training"] = await db.agent_training_queue.count_documents({"status": "pending_review"})
    except Exception:
        pass
    try:
        out["workflows"] = await db.workflow_runs.count_documents({
            "status": "failed", "started_at": {"$gte": since_24h},
        })
    except Exception:
        pass
    try:
        sme_pending = await db.sme_corrections.count_documents({"status": "pending"})
        out["commander"] = sme_pending
    except Exception:
        pass
    return {"badges": out}


# ── Workflows fleet dashboard (Universal Gateway → Workflows tab) ───
# Surfaces workflow health alongside LLM health under the centralized
# admin page: runs over time, top workflows by spend, recent failures,
# queued-but-stuck runs. Reads the same `gateway_usage_logs` the rest of
# /admin/gateway reads so spend attribution is consistent.

@router.get("/admin/gateway/workflows/stats")
async def workflows_stats(window_hours: int = 24, _admin=Depends(_admin_dep)):
    from db import db
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max(1, min(int(window_hours), 24 * 30))))
    cutoff_iso = cutoff.isoformat()

    # Run totals + status breakdown over the window
    agg_status = await db.workflow_runs.aggregate([
        {"$match": {"started_at": {"$gte": cutoff_iso}}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_nodes": {"$sum": {"$ifNull": ["$nodes_fired", 0]}},
        }},
    ]).to_list(length=None)
    by_status: dict[str, Any] = {d["_id"] or "unknown": {
        "count": int(d["count"]),
        "total_nodes": int(d["total_nodes"]),
    } for d in agg_status}
    total_runs = sum(v["count"] for v in by_status.values())
    failed = by_status.get("failed", {}).get("count", 0)
    completed = by_status.get("completed", {}).get("count", 0)
    error_rate_pct = round((failed / total_runs) * 100, 2) if total_runs else 0.0

    # Top workflows by spend inside the window — joins logs by source tag
    # ("workflow.*" source tags show up when the executor fires LLM calls)
    agg_spend = await db.gateway_usage_logs.aggregate([
        {"$match": {"timestamp": {"$gte": cutoff_iso},
                    "source": {"$regex": "^workflow"}}},
        {"$group": {
            "_id":    "$source",
            "calls":  {"$sum": 1},
            "cost":   {"$sum": "$cost_usd"},
            "credits": {"$sum": "$credits_charged"},
        }},
        {"$sort": {"cost": -1}},
        {"$limit": 15},
    ]).to_list(length=None)
    top_spend = [{
        "source":  d["_id"],
        "calls":   int(d.get("calls", 0)),
        "cost_usd": round(float(d.get("cost") or 0), 6),
        "credits": int(d.get("credits") or 0),
    } for d in agg_spend]

    # Recent failures — last 10 failed runs with their first error
    failures_cursor = db.workflow_runs.find(
        {"status": "failed", "started_at": {"$gte": cutoff_iso}},
        {"_id": 0, "run_id": 1, "workflow_id": 1, "user_id": 1,
         "started_at": 1, "finished_at": 1, "error": 1, "failed_node": 1},
    ).sort("started_at", -1).limit(10)
    recent_failures = await failures_cursor.to_list(length=10)

    # Top workflows by run count — gives operator a sense of what's actually used
    agg_runs = await db.workflow_runs.aggregate([
        {"$match": {"started_at": {"$gte": cutoff_iso}}},
        {"$group": {
            "_id": "$workflow_id",
            "runs": {"$sum": 1},
            "failed_runs": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
            "last_started_at": {"$max": "$started_at"},
        }},
        {"$sort": {"runs": -1}},
        {"$limit": 10},
    ]).to_list(length=None)
    # Hydrate with workflow names
    wf_ids = [d["_id"] for d in agg_runs if d.get("_id")]
    names: dict[str, str] = {}
    if wf_ids:
        async for wf in db.workflows.find(
            {"workflow_id": {"$in": wf_ids}},
            {"_id": 0, "workflow_id": 1, "name": 1, "active": 1},
        ):
            names[wf["workflow_id"]] = wf.get("name") or wf["workflow_id"]
    top_runs = [{
        "workflow_id":      d["_id"],
        "name":             names.get(d["_id"], "(deleted)"),
        "runs":             int(d.get("runs", 0)),
        "failed_runs":      int(d.get("failed_runs", 0)),
        "error_rate_pct":   round((int(d.get("failed_runs") or 0) / int(d.get("runs") or 1)) * 100, 1),
        "last_started_at":  d.get("last_started_at"),
    } for d in agg_runs]

    # Queued-but-stuck (queued > 5 min is a smell)
    stuck_cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    stuck = await db.workflow_runs.count_documents(
        {"status": "queued", "started_at": {"$lt": stuck_cutoff}}
    )

    # Fleet-wide workflow counts
    total_wf = await db.workflows.count_documents({})
    active_wf = await db.workflows.count_documents({"active": True})

    # Stringify any leaked bson.ObjectId before returning — Mongo aggs
    # + older docs sometimes contain ObjectIds in projected fields (error
    # payloads, metadata) that FastAPI can't JSON-serialize.
    def _clean(o):
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(x) for x in o]
        # bson.ObjectId has a __str__ that yields a 24-char hex
        from bson import ObjectId
        if isinstance(o, ObjectId):
            return str(o)
        return o
    recent_failures = _clean(recent_failures)
    top_runs        = _clean(top_runs)
    top_spend       = _clean(top_spend)
    by_status       = _clean(by_status)

    return {
        "object":          "workflow_stats",
        "window_hours":    window_hours,
        "workflows": {
            "total":  total_wf,
            "active": active_wf,
        },
        "runs": {
            "total":          total_runs,
            "completed":      completed,
            "failed":         failed,
            "error_rate_pct": error_rate_pct,
            "by_status":      by_status,
            "stuck_queued":   stuck,
        },
        "top_workflows_by_runs":  top_runs,
        "top_workflows_by_spend": top_spend,
        "recent_failures":        recent_failures,
    }


@router.post("/admin/gateway/workflows/{run_id}/replay")
async def admin_replay_run(run_id: str, _admin=Depends(_admin_dep)):
    """Admin shortcut to replay a failed run straight from the dashboard,
    without navigating into the individual workflow canvas."""
    from services.workflows import workflow_executor as wx
    try:
        new_id = await wx.replay_run(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    return {"ok": True, "run_id": new_id, "replaying": run_id}


@router.get("/admin/gateway/workflows/{run_id}/diagnose")
async def admin_diagnose_run(run_id: str, _admin=Depends(_admin_dep)):
    from services.workflows import workflow_diagnose as _wd
    from db import db
    # Resolve the run -> owning user (diagnose needs a user for billing)
    run = await db.workflow_runs.find_one({"run_id": run_id}, {"user_id": 1})
    uid = (run or {}).get("user_id") or "system"
    try:
        return await _wd.diagnose_run(run_id, uid)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


# ── Role map (Commander delegation fallback chain) ──────────────────

@router.get("/admin/gateway/training/role-map")
async def training_role_map(_admin=Depends(_admin_dep)):
    from services.agents import agent_router_map
    return {"object": "role_map", "map": await agent_router_map.get_map()}


class _RoleOverride(BaseModel):
    role_key: str
    agents: list[str]


@router.put("/admin/gateway/training/role-map")
async def training_role_map_set(body: _RoleOverride, _admin=Depends(_admin_dep)):
    from services.agents import agent_router_map
    try:
        return await agent_router_map.set_override(body.role_key, body.agents)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.delete("/admin/gateway/training/role-map/{role_key}")
async def training_role_map_clear(role_key: str, _admin=Depends(_admin_dep)):
    from services.agents import agent_router_map
    ok = await agent_router_map.clear_override(role_key)
    return {"ok": ok}


# ── Datetime import needed for this file's timestamp usage ───────────

from datetime import datetime, timezone  # noqa: E402


class _SeedRequest(BaseModel):
    agent_id: str
    scope: str = "role"        # agent | network | role
    count: int = 3


@router.post("/admin/gateway/training/seed")
async def training_seed_examples(body: _SeedRequest, _admin=Depends(_admin_dep)):
    """Use the LLM gateway to generate N golden (input, output) pairs
    grounded in the agent's role + capabilities + base prompt, then
    store them at the requested scope. One-shot; re-runnable safely
    (creates new docs each time — operator can delete duplicates from
    the UI)."""
    from db import db
    import json, re
    agent = await db.agents.find_one({"agent_id": body.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(404, "agent_not_found")
    if body.scope not in ("agent", "network", "role"):
        raise HTTPException(400, "scope must be agent|network|role")
    scope_value = {
        "agent":   agent.get("agent_id"),
        "network": agent.get("network", ""),
        "role":    agent.get("role", ""),
    }[body.scope]
    if not scope_value:
        raise HTTPException(400, f"agent has no value for scope '{body.scope}'")
    n = max(1, min(int(body.count or 3), 8))

    role = agent.get("role", "")
    name = agent.get("name", "")
    caps = ", ".join(agent.get("capabilities") or []) or "(no explicit capabilities listed)"
    base_prompt = (agent.get("system_prompt") or "").strip()[:3000]
    instructions = (
        f"You are building a training library for an AI agent named {name} "
        f"whose role is {role}. Their capabilities: {caps}.\n\n"
        f"Their current system prompt excerpt:\n\"\"\"\n{base_prompt}\n\"\"\"\n\n"
        f"Generate EXACTLY {n} golden (user_input, ideal_output) training pairs "
        f"representing the quality bar for this role at a premium AI platform. "
        f"Each input should be a realistic, specific client request. Each output "
        f"should be what a best-in-class {role or 'expert'} would reply — "
        f"concrete, actionable, no filler. Do not use placeholder text like "
        f"'[insert company name]'. Each output 150-400 words.\n\n"
        f"Return ONLY a JSON array of objects with keys 'user_input', "
        f"'ideal_output', 'notes' (one sentence on what makes this exemplary). "
        f"No markdown fences, no commentary."
    )

    # Use an admin user_id so the cost is attributed
    from shared.utils import get_api_keys  # noqa: F401 (ensures env loaded)
    admin_user = await db.users.find_one({"is_admin": True}, {"user_id": 1})
    if not admin_user:
        raise HTTPException(500, "no_admin_user_for_billing")
    from services.llm_gateway import complete_text
    raw = await complete_text(
        admin_user["user_id"],
        system_prompt="You produce terse, production-quality training data.",
        user_prompt=instructions,
        model="maars/auto",
        max_tokens=3500,
        temperature=0.4,
        source="agent_training_seed",
    )
    # Pull the JSON array out of whatever the model returned
    m = re.search(r"\[[\s\S]*\]", raw or "")
    if not m:
        raise HTTPException(502, f"seed_parse_failed: no JSON array found in model reply ({raw[:200] if raw else 'empty'})")
    try:
        parsed = json.loads(m.group(0))
    except Exception as exc:
        raise HTTPException(502, f"seed_parse_failed: {exc}")
    if not isinstance(parsed, list) or not parsed:
        raise HTTPException(502, "seed_parse_failed: empty array")

    from services import golden_examples
    created: list[dict[str, Any]] = []
    for i, item in enumerate(parsed[:n]):
        if not isinstance(item, dict):
            continue
        ui = (item.get("user_input") or "").strip()
        out = (item.get("ideal_output") or "").strip()
        if not (ui and out):
            continue
        try:
            doc = await golden_examples.create(
                scope=body.scope, scope_value=scope_value,
                user_input=ui, ideal_output=out,
                notes=(item.get("notes") or "").strip()[:500],
                weight=0.9,          # auto-seeded slightly below manual (1.0)
                source="llm_seed",
                created_by="seeder",
                tags=["auto_seed"],
            )
            created.append(doc)
        except Exception as exc:
            logger.info("seed insert failed at index %d: %s", i, exc)

    return {
        "ok": True,
        "agent_id": body.agent_id,
        "scope": body.scope,
        "scope_value": scope_value,
        "created_count": len(created),
        "examples": created,
    }


# ── Aggregate rollup (single call for the dashboard) ─────────────────
@router.get("/admin/gateway/intel/all")
async def intel_all(_admin=Depends(_admin_dep)):
    from services import (
        provider_scorecard, rate_limit_headers,
        circuit_breaker, semantic_cache, embedding_cache,
        error_budget, routellm_matrix,
    )
    from services.routing import router as bandit_router
    return {
        "object": "gateway_intel",
        "bandit":          bandit_router.snapshot(),
        "scorecards":      provider_scorecard.all_scorecards(),
        "rate_limit":      rate_limit_headers.snapshot(),
        "circuits":        circuit_breaker.snapshot(),
        "semantic_cache":  await semantic_cache.stats(),
        "embedding_cache": await embedding_cache.stats(),
        "error_budget":    await error_budget.snapshot(),
        "routing_table":   routellm_matrix.stats(),
    }
