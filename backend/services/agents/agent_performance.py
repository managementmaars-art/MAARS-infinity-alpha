"""Per-agent performance aggregation — closes the orphaned-signal gap.

Signals already captured but never aggregated:
  • `db.quality_reviews`     — critic_review scores (1-10), verdicts
  • `db.messages.feedback`   — user thumbs up/down per chat message
  • `db.gateway_usage_logs`  — cost + latency per call (now with agent_id)

This module rolls those into one per-agent record so the Training tab
can rank agents by (quality / cost), flag regressions, and feed the
continuous-improvement loop.

Public surface:
    async rollup(window_days=7) -> list[dict]       # one row per agent
    async rollup_one(agent_id, window_days=7) -> dict
    async top_promote_candidates(n=5) -> list       # agents with great
                                                     # messages to add as
                                                     # golden examples
    async retrain_candidates(score_floor=5.0) -> list  # agents whose prompt
                                                         # needs dspy rewrite
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _window_start(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


async def _quality_by_agent(window_days: int) -> dict[str, dict[str, Any]]:
    from db import db
    start = _window_start(window_days)
    pipeline = [
        {"$match": {"created_at": {"$gte": start}, "agent_id": {"$ne": None}}},
        {"$group": {
            "_id": "$agent_id",
            "review_count": {"$sum": 1},
            "avg_score":    {"$avg": "$score"},
            "pass_count":   {"$sum": {"$cond": [{"$eq": ["$verdict", "pass"]}, 1, 0]}},
            "revision_count": {"$sum": {"$cond": [{"$eq": ["$verdict", "revision_needed"]}, 1, 0]}},
            "fail_count":   {"$sum": {"$cond": [{"$eq": ["$verdict", "fail"]}, 1, 0]}},
        }},
    ]
    out: dict[str, dict] = {}
    async for doc in db.quality_reviews.aggregate(pipeline):
        out[doc["_id"]] = {
            "review_count":   int(doc.get("review_count", 0)),
            "avg_score":      round(float(doc.get("avg_score") or 0), 2),
            "pass_count":     int(doc.get("pass_count", 0)),
            "revision_count": int(doc.get("revision_count", 0)),
            "fail_count":     int(doc.get("fail_count", 0)),
        }
    return out


async def _feedback_by_agent(window_days: int) -> dict[str, dict[str, Any]]:
    """Chat-message thumbs up/down. Messages don't carry agent_id directly
    — they live in `db.messages` keyed by chat_id. Resolve via the chat's
    agent_id. The $lookup keeps this one round-trip."""
    from db import db
    start = _window_start(window_days)
    pipeline = [
        {"$match": {
            "feedback": {"$in": ["up", "down"]},
            "feedback_at": {"$gte": start},
            "role": "assistant",
        }},
        {"$lookup": {
            "from": "chats", "localField": "chat_id", "foreignField": "chat_id",
            "as": "_chat",
        }},
        {"$unwind": {"path": "$_chat", "preserveNullAndEmptyArrays": False}},
        {"$group": {
            "_id": "$_chat.agent_id",
            "up":   {"$sum": {"$cond": [{"$eq": ["$feedback", "up"]}, 1, 0]}},
            "down": {"$sum": {"$cond": [{"$eq": ["$feedback", "down"]}, 1, 0]}},
        }},
    ]
    out: dict[str, dict] = {}
    try:
        async for doc in db.messages.aggregate(pipeline):
            aid = doc.get("_id")
            if not aid:
                continue
            u, d = int(doc.get("up", 0)), int(doc.get("down", 0))
            total = u + d
            out[aid] = {
                "up": u, "down": d, "total": total,
                "net_sentiment": round((u - d) / total, 3) if total > 0 else 0.0,
            }
    except Exception as exc:
        logger.info("feedback aggregation soft-fail: %s", exc)
    return out


async def _cost_by_agent(window_days: int) -> dict[str, dict[str, Any]]:
    from db import db
    start = _window_start(window_days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": start}, "agent_id": {"$ne": None}}},
        {"$group": {
            "_id": "$agent_id",
            "calls":      {"$sum": 1},
            "credits":    {"$sum": "$credits_charged"},
            "cost_usd":   {"$sum": "$cost_usd"},
            "cache_hits": {"$sum": {"$cond": [{"$eq": ["$from_cache", True]}, 1, 0]}},
            "p95_latency_ms": {"$avg": "$latency_ms"},  # approx: real p95 needs $percentile (Mongo 7+)
        }},
    ]
    out: dict[str, dict] = {}
    async for doc in db.gateway_usage_logs.aggregate(pipeline):
        out[doc["_id"]] = {
            "calls":      int(doc.get("calls", 0)),
            "credits":    int(doc.get("credits", 0)),
            "cost_usd":   round(float(doc.get("cost_usd") or 0), 6),
            "cache_hits": int(doc.get("cache_hits", 0)),
            "avg_latency_ms": int(doc.get("p95_latency_ms") or 0),
        }
    return out


def _compute_score(quality: dict, feedback: dict, cost: dict) -> dict[str, float]:
    """Blend quality + feedback + efficiency into one number.

    - quality (0-10 → normalize to 0-1)       weight 0.55
    - user sentiment (-1..1 → normalize to 0-1) weight 0.30
    - efficiency (credits/call, inverted)     weight 0.15

    Agents with no signal get None (not 0) so they don't rank below
    measurably-bad agents.
    """
    has_quality = bool(quality.get("review_count"))
    has_feedback = bool(feedback.get("total"))
    if not (has_quality or has_feedback):
        return {"score": None, "confidence": 0.0}
    q = (quality.get("avg_score") or 0) / 10.0 if has_quality else 0.5
    s = ((feedback.get("net_sentiment") or 0) + 1) / 2.0 if has_feedback else 0.5
    calls = cost.get("calls") or 0
    credits = cost.get("credits") or 0
    efficiency = 1.0
    if calls > 0 and credits > 0:
        # Normalize against a nominal 5 credits/call baseline. 1 credit/call → 1.0, 10+ credits/call → 0.0
        ratio = credits / calls
        efficiency = max(0.0, min(1.0, (10.0 - ratio) / 9.0))
    score = 0.55 * q + 0.30 * s + 0.15 * efficiency
    # Confidence rises with sample size, capped at 1.0 around 50 reviews/feedbacks
    samples = (quality.get("review_count") or 0) + (feedback.get("total") or 0)
    confidence = min(1.0, samples / 50.0)
    return {"score": round(score, 3), "confidence": round(confidence, 2)}


async def rollup(window_days: int = 7) -> list[dict[str, Any]]:
    from db import db
    quality = await _quality_by_agent(window_days)
    feedback = await _feedback_by_agent(window_days)
    cost = await _cost_by_agent(window_days)
    agent_ids = set(quality) | set(feedback) | set(cost)
    if not agent_ids:
        return []
    agents = await db.agents.find(
        {"agent_id": {"$in": list(agent_ids)}},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "network": 1},
    ).to_list(length=len(agent_ids))
    agent_by_id = {a["agent_id"]: a for a in agents}
    rows: list[dict[str, Any]] = []
    for aid in agent_ids:
        q = quality.get(aid) or {}
        f = feedback.get(aid) or {}
        c = cost.get(aid) or {}
        scored = _compute_score(q, f, c)
        meta = agent_by_id.get(aid) or {"agent_id": aid}
        rows.append({
            **meta,
            "window_days": window_days,
            "quality":  q,
            "feedback": f,
            "cost":     c,
            **scored,
        })
    # Rank — None scores fall to the end; within None bucket, alphabetical
    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))
    return rows


async def rollup_one(agent_id: str, window_days: int = 7) -> dict[str, Any]:
    all_rows = await rollup(window_days=window_days)
    for r in all_rows:
        if r.get("agent_id") == agent_id:
            return r
    # No signal — return empty shape rather than 404
    from db import db
    agent = await db.agents.find_one(
        {"agent_id": agent_id},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "network": 1},
    ) or {"agent_id": agent_id}
    return {**agent, "window_days": window_days, "quality": {}, "feedback": {},
            "cost": {}, "score": None, "confidence": 0.0}


async def top_promote_candidates(
    n: int = 5, window_days: int = 7, min_feedback: int = 3,
) -> list[dict[str, Any]]:
    """Find individual assistant messages that got thumbs-up — these are
    candidates to promote into the golden-examples library.
    Returns {message_id, chat_id, agent_id, user_input, assistant_output, feedback_at}."""
    from db import db
    start = _window_start(window_days)
    pipeline = [
        {"$match": {"feedback": "up", "role": "assistant", "feedback_at": {"$gte": start}}},
        {"$lookup": {"from": "chats", "localField": "chat_id", "foreignField": "chat_id", "as": "_chat"}},
        {"$unwind": {"path": "$_chat", "preserveNullAndEmptyArrays": False}},
        {"$sort": {"feedback_at": -1}},
        {"$limit": int(n) * 3},  # overfetch; we filter below
    ]
    out: list[dict] = []
    async for msg in db.messages.aggregate(pipeline):
        aid = msg["_chat"].get("agent_id")
        if not aid:
            continue
        # Find the preceding user message in the same chat
        prior = await db.messages.find({
            "chat_id": msg["chat_id"],
            "role": "user",
            "created_at": {"$lt": msg.get("created_at")},
        }, {"_id": 0, "content": 1, "created_at": 1}).sort("created_at", -1).limit(1).to_list(length=1)
        user_input = (prior[0]["content"] if prior else "").strip()
        if not user_input:
            continue
        out.append({
            "message_id": msg.get("message_id"),
            "chat_id":    msg.get("chat_id"),
            "agent_id":   aid,
            "user_input": user_input[:500],
            "assistant_output": (msg.get("content") or "")[:2000],
            "feedback_at": msg.get("feedback_at"),
        })
        if len(out) >= n:
            break
    return out


async def retrain_candidates(
    score_floor: float = 5.0, window_days: int = 7, min_reviews: int = 5,
) -> list[dict[str, Any]]:
    """Agents with enough volume that also score below the floor — these
    are candidates to auto-rewrite via dspy_optimizer."""
    rows = await rollup(window_days=window_days)
    losers = []
    for r in rows:
        q = r.get("quality") or {}
        if int(q.get("review_count") or 0) < min_reviews:
            continue
        if (q.get("avg_score") or 0) >= score_floor:
            continue
        losers.append(r)
    return losers
