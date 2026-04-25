"""Per-agent monthly credit budget enforcement.

Problem this solves: MAARS has 499 auto-routed client agents. Budgeting lives
at the wallet/plan level, so a runaway agent (bad prompt loop, tool misuse)
can drain the whole user wallet before a human notices. This adds an
agent-level budget gate on top of the wallet CAS — each agent gets its own
monthly allowance, checked before `wallet_service.reserve()` in
`services.llm_gateway.complete()`.

Shape on the agent doc (set via admin UI):
    monthly_budget_credits: int | None   # None = no cap (legacy/admin agents)
    throttle_at_pct: float | None        # e.g. 0.80 → slow-warn at 80%; 1.00 enforced hard cap

Aggregation source: `db.gateway_usage_logs` filtered by `agent_id` +
timestamp within the current calendar month (UTC). No separate counter
collection — the log is already the source of truth for billing.

Public surface:
    check(agent_id) -> dict   # hard-cap + throttle signal
    record_usage(...)         # not needed; the log itself is the counter
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def _agent_doc(agent_id: str) -> Optional[dict]:
    if not agent_id:
        return None
    from db import db
    return await db.agents.find_one({"agent_id": agent_id}, {
        "monthly_budget_credits": 1, "throttle_at_pct": 1, "agent_id": 1, "name": 1,
    })


async def _month_to_date_credits(agent_id: str) -> int:
    """Sum credits_charged from gateway_usage_logs for this agent since
    start-of-month UTC."""
    from db import db
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cursor = db.gateway_usage_logs.aggregate([
        {"$match": {
            "agent_id": agent_id,
            "timestamp": {"$gte": month_start.isoformat()},
        }},
        {"$group": {"_id": None, "total": {"$sum": "$credits_charged"}}},
    ])
    docs = await cursor.to_list(length=1)
    if not docs:
        return 0
    return int(docs[0].get("total") or 0)


async def check(agent_id: Optional[str]) -> dict[str, Any]:
    """Decide whether the caller should proceed, throttle, or reject.

    Returns:
      {
        allow:          bool,         # proceed with call
        throttled:      bool,         # proceed but warn / degrade
        reason:         str,          # human-readable
        month_to_date:  int,          # credits spent so far this month
        budget:         int | None,   # cap or None if no budget set
        pct_used:       float,        # 0..1+
      }
    """
    if not agent_id:
        return {"allow": True, "throttled": False, "reason": "no_agent_id",
                "month_to_date": 0, "budget": None, "pct_used": 0.0}
    doc = await _agent_doc(agent_id)
    if not doc:
        return {"allow": True, "throttled": False, "reason": "agent_not_found",
                "month_to_date": 0, "budget": None, "pct_used": 0.0}
    budget = doc.get("monthly_budget_credits")
    if not budget or int(budget) <= 0:
        return {"allow": True, "throttled": False, "reason": "no_budget_set",
                "month_to_date": 0, "budget": None, "pct_used": 0.0}
    try:
        mtd = await _month_to_date_credits(agent_id)
    except Exception as exc:
        logger.warning("agent_budget aggregation failed for %s: %s", agent_id, exc)
        return {"allow": True, "throttled": False, "reason": "aggregation_failed",
                "month_to_date": 0, "budget": int(budget), "pct_used": 0.0}
    budget_i = int(budget)
    pct = mtd / budget_i if budget_i > 0 else 0.0
    throttle_at = float(doc.get("throttle_at_pct") or 1.0)
    if mtd >= budget_i:
        return {"allow": False, "throttled": True,
                "reason": f"agent_budget_exceeded: {mtd}/{budget_i} credits this month",
                "month_to_date": mtd, "budget": budget_i, "pct_used": pct}
    if pct >= throttle_at:
        return {"allow": True, "throttled": True,
                "reason": f"agent_budget_throttle: {mtd}/{budget_i} ({pct:.0%})",
                "month_to_date": mtd, "budget": budget_i, "pct_used": pct}
    return {"allow": True, "throttled": False, "reason": "within_budget",
            "month_to_date": mtd, "budget": budget_i, "pct_used": pct}


async def status_for(agent_ids: list[str]) -> list[dict[str, Any]]:
    """Batch status read for the admin UI — one call, all agents."""
    return [dict(await check(aid), agent_id=aid) for aid in agent_ids]
