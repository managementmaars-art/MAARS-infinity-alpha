"""Outcomes service — the buyer-facing dashboard in one API call.

A client paying $10K/month wants to see RESULTS, not internals.
Specifically (in buyer priority order):

  1. Pipeline — leads sourced, emails sent, replies, meetings
  2. Content — posts published, images generated, videos rendered
  3. Campaigns — active, paused, completed (revenue-attributed when available)
  4. Workflows — active trigger sources + recent run success rate
  5. Team — agents working right now + their current task
  6. Usage — this-month capacity vs. plan (one friendly bar,
             NOT a credit number)

Every line maps to ONE Mongo query scoped by user_id. No router
internals leak out — this is strictly outcomes. Caching is 60 seconds
so the dashboard feels live without hammering Mongo.
"""
from __future__ import annotations
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_TTL = 60
_cache: dict[str, tuple[Any, float]] = {}


def _cached(key):
    hit = _cache.get(key)
    if hit and time.time() - hit[1] < _CACHE_TTL:
        return hit[0]
    return None

def _put(key, val):
    _cache[key] = (val, time.time())
    return val


def _month_start() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


async def _count(coll: str, match: dict) -> int:
    from db import db
    try:
        return await db[coll].count_documents(match)
    except Exception:
        return 0


async def _sum_field(coll: str, match: dict, field: str) -> float:
    from db import db
    try:
        rows = await db[coll].aggregate([
            {"$match": match},
            {"$group": {"_id": None, "s": {"$sum": f"${field}"}}},
        ]).to_list(1)
    except Exception:
        return 0.0
    return float((rows[0]["s"] if rows else 0.0) or 0.0)


async def pipeline_block(user_id: str) -> dict[str, Any]:
    """Lead → email → reply → meeting funnel. Counts this month."""
    since = _month_start()
    from db import db
    # Leads sourced (from lead_research output we persist)
    leads_sourced = await _count("cold_emails", {"user_id": user_id,
                                                  "created_at": {"$gte": since}})
    # Emails sent
    emails_sent = await _count("cold_emails", {"user_id": user_id,
                                                "status": {"$in": ["sent", "delivered"]},
                                                "created_at": {"$gte": since}})
    # Replies — email_events reply
    replies = 0
    try:
        # email_events doesn't carry user_id; resolve via cold_emails.
        owned = await db.cold_emails.find(
            {"user_id": user_id, "created_at": {"$gte": since}},
            {"to_email": 1, "_id": 0},
        ).to_list(10000)
        addrs = [d.get("to_email") for d in owned if d.get("to_email")]
        if addrs:
            replies = await _count("email_events", {
                "event_type": {"$in": ["reply", "replied"]},
                "email": {"$in": [a.lower() for a in addrs]},
            })
    except Exception:
        pass
    meetings = await _count("bookings", {"user_id": user_id, "created_at": {"$gte": since}})

    return {
        "leads_sourced":  leads_sourced,
        "emails_sent":    emails_sent,
        "replies":        replies,
        "meetings":       meetings,
        "reply_rate_pct": round((replies / emails_sent) * 100, 2) if emails_sent else 0.0,
    }


async def content_block(user_id: str) -> dict[str, Any]:
    since = _month_start()
    posts_published = await _count("published_content", {
        "user_id": user_id, "published_at": {"$gte": since},
    })
    posts_scheduled = await _count("scheduled_posts", {
        "user_id": user_id, "status": "scheduled",
    })
    generated_text = await _count("generated_content", {
        "user_id": user_id, "created_at": {"$gte": since},
    })
    images = await _count("gateway_usage_logs", {
        "user_id": user_id, "source": {"$regex": "image", "$options": "i"},
        "timestamp": {"$gte": since},
    })
    videos = await _count("gateway_usage_logs", {
        "user_id": user_id, "source": {"$regex": "video|sora", "$options": "i"},
        "timestamp": {"$gte": since},
    })
    return {
        "text_pieces":      generated_text,
        "posts_published":  posts_published,
        "posts_scheduled":  posts_scheduled,
        "images_created":   images,
        "videos_created":   videos,
    }


async def campaigns_block(user_id: str) -> dict[str, Any]:
    from db import db
    active = await _count("outbound_campaigns", {"user_id": user_id, "status": {"$in": ["running", "active"]}})
    paused = await _count("outbound_campaigns", {"user_id": user_id, "status": "paused"})
    completed = await _count("outbound_campaigns", {"user_id": user_id, "status": "completed"})
    social_campaigns_active = await _count("social_campaigns", {
        "user_id": user_id, "status": {"$in": ["running", "active", "scheduled"]},
    })
    return {
        "email_campaigns_active": active,
        "email_campaigns_paused": paused,
        "email_campaigns_completed": completed,
        "social_campaigns_active": social_campaigns_active,
    }


async def workflows_block(user_id: str) -> dict[str, Any]:
    from db import db
    since = _month_start()
    active_total = await _count("workflows", {"user_id": user_id, "active": True})
    runs_this_month = await _count("workflow_runs", {"user_id": user_id, "started_at": {"$gte": since}})
    successes = await _count("workflow_runs", {"user_id": user_id,
                                                "status": "completed",
                                                "started_at": {"$gte": since}})
    success_rate = round((successes / runs_this_month) * 100, 2) if runs_this_month else 100.0
    return {
        "workflows_active":   active_total,
        "runs_this_month":    runs_this_month,
        "successful_runs":    successes,
        "success_rate_pct":   success_rate,
    }


async def team_block(user_id: str) -> dict[str, Any]:
    """Agents + right-now activity."""
    from db import db
    try:
        agent_count = await _count("agents", {"user_id": user_id})
        running = await db.agent_tasks.count_documents({
            "user_id": user_id, "status": {"$in": ["running", "executing"]},
        }) if db is not None else 0
    except Exception:
        running = 0
    return {"agents_configured": agent_count, "agents_working_now": running}


async def usage_block(user_id: str) -> dict[str, Any]:
    """Capacity consumed vs. plan ceiling — single friendly percent.
    We deliberately AVOID exposing credit numbers to the buyer."""
    from db import db
    from shared.constants import SUBSCRIPTION_PLANS
    try:
        sub = await db.subscriptions.find_one({"user_id": user_id},
                                              {"plan_id": 1, "_id": 0})
    except Exception:
        sub = None
    plan_id = (sub or {}).get("plan_id") or "free"
    plan = SUBSCRIPTION_PLANS.get(plan_id) or {}
    monthly_cap = float(plan.get("monthly_cap_usd") or 0)

    try:
        from services.costing.base_cost_calculator import monthly_spend_usd
        spent = await monthly_spend_usd(user_id)
    except Exception:
        spent = 0.0

    used_pct = 0.0
    if monthly_cap > 0:
        used_pct = round(min(100.0, (spent / monthly_cap) * 100), 2)

    return {
        "plan_id":        plan_id,
        "plan_name":      plan.get("name", plan_id.title()),
        "cycle_start":    _month_start(),
        "used_pct":       used_pct,
        "near_limit":     used_pct >= 80,
    }


async def overview(user_id: str) -> dict[str, Any]:
    """The one call the client dashboard hits. Parallelizes the blocks
    so the whole page renders in ~one DB roundtrip's worth of time."""
    key = f"overview:{user_id}"
    c = _cached(key)
    if c: return c

    import asyncio
    pipeline, content, camp, wf, team, usage = await asyncio.gather(
        pipeline_block(user_id),
        content_block(user_id),
        campaigns_block(user_id),
        workflows_block(user_id),
        team_block(user_id),
        usage_block(user_id),
        return_exceptions=True,
    )
    def _safe(x, default):
        return default if isinstance(x, Exception) else x
    payload = {
        "object":     "outcomes_overview",
        "user_id":    user_id,
        "pipeline":   _safe(pipeline, {}),
        "content":    _safe(content, {}),
        "campaigns":  _safe(camp, {}),
        "workflows":  _safe(wf, {}),
        "team":       _safe(team, {}),
        "usage":      _safe(usage, {}),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return _put(key, payload)


async def recent_activity(user_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    """Recent done-things stream — "we just sent 3 emails, published 1
    post, closed 2 workflow runs." No model internals. Used by the
    dashboard activity ticker."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    items: list[dict[str, Any]] = []

    # Emails sent
    try:
        async for d in db.cold_emails.find(
            {"user_id": user_id, "created_at": {"$gte": since}},
            {"to_email": 1, "subject": 1, "status": 1, "created_at": 1, "_id": 0},
        ).sort("created_at", -1).limit(limit):
            items.append({"kind": "email_sent", "ts": d.get("created_at"),
                          "subject": d.get("subject"), "to": d.get("to_email"),
                          "status": d.get("status")})
    except Exception:
        pass

    # Posts published
    try:
        async for d in db.published_content.find(
            {"user_id": user_id, "published_at": {"$gte": since}},
            {"platforms": 1, "ok_count": 1, "published_at": 1, "text": 1, "_id": 0},
        ).sort("published_at", -1).limit(limit):
            items.append({"kind": "post_published", "ts": d.get("published_at"),
                          "platforms": d.get("platforms", []),
                          "ok_count": d.get("ok_count", 0),
                          "preview": (d.get("text") or "")[:120]})
    except Exception:
        pass

    # Workflow runs completed
    try:
        async for d in db.workflow_runs.find(
            {"user_id": user_id, "started_at": {"$gte": since},
             "status": {"$in": ["completed", "failed"]}},
            {"workflow_id": 1, "status": 1, "started_at": 1,
             "nodes_fired": 1, "_id": 0},
        ).sort("started_at", -1).limit(limit):
            items.append({"kind": "workflow_run", "ts": d.get("started_at"),
                          "workflow_id": d.get("workflow_id"),
                          "status": d.get("status"),
                          "nodes_fired": d.get("nodes_fired", 0)})
    except Exception:
        pass

    items.sort(key=lambda x: x.get("ts") or "", reverse=True)
    return items[:limit]
