"""Per-user daily cost cap — hard ceiling on runaway spend.

Even with wallet credits, a misbehaving integration (loop bug, looping
agent) can burn through a top-up in hours. This module enforces a
per-user, per-day USD ceiling INDEPENDENT of wallet balance. When a
user crosses it, the gateway returns 429 until midnight UTC.

Configurable per user (admin can raise caps for power users) with
a global default fallback (env `MAARS_DAILY_USD_CAP`, default 50).

How it integrates:
  - `check(user_id)` runs BEFORE reserve; returns (ok, spent_today, cap).
  - After settle, `record(user_id, cost_usd)` updates the counter.
  - State lives in `daily_budget` Mongo collection keyed by
    (user_id, yyyy-mm-dd); Mongo TTL index drops entries after 7 days.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CAP_USD = float(os.environ.get("MAARS_DAILY_USD_CAP", "50"))
_INDEX_READY = False


async def _ensure_index() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return
    try:
        from db import db
        await db.daily_budget.create_index([("user_id", 1), ("day", 1)], unique=True)
        # 7-day TTL on created_at_epoch
        await db.daily_budget.create_index("created_at_epoch", expireAfterSeconds=7 * 86400)
        _INDEX_READY = True
    except Exception as exc:
        logger.info("daily_budget index deferred: %s", exc)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def get_cap(user_id: str) -> float:
    """Per-user override lives on `users.daily_cap_usd`; else default."""
    try:
        from db import db
        u = await db.users.find_one({"_id": user_id}, {"daily_cap_usd": 1, "_id": 0})
        if u and isinstance(u.get("daily_cap_usd"), (int, float)) and u["daily_cap_usd"] > 0:
            return float(u["daily_cap_usd"])
    except Exception:
        pass
    return DEFAULT_CAP_USD


async def _org_cap(org_id: str) -> float | None:
    """Per-org cap from `orgs.daily_cap_usd`, if the org doc exists."""
    try:
        from db import db
        o = await db.orgs.find_one({"_id": org_id}, {"daily_cap_usd": 1, "_id": 0})
        if o and isinstance(o.get("daily_cap_usd"), (int, float)) and o["daily_cap_usd"] > 0:
            return float(o["daily_cap_usd"])
    except Exception:
        pass
    return None


async def _user_org(user_id: str) -> str | None:
    try:
        from db import db
        u = await db.users.find_one({"_id": user_id}, {"org_id": 1, "_id": 0})
        return (u or {}).get("org_id")
    except Exception:
        return None


async def check(
    user_id: str, *,
    expected_cost_usd: float = 0.0,
    org_id: str | None = None,
) -> tuple[bool, float, float]:
    """Return (ok_to_proceed, spent_today_usd, cap_usd).

    If the user belongs to an org AND the org has its own cap, the
    stricter of (user_cap, org_cap) wins — org spend is the sum across
    every user in the org, not just this caller."""
    await _ensure_index()
    from db import db
    user_cap = await get_cap(user_id)

    try:
        udoc = await db.daily_budget.find_one({"user_id": user_id, "day": _today()})
    except Exception:
        udoc = None
    user_spent = float((udoc or {}).get("spent_usd", 0.0))

    # Org layer
    if org_id is None:
        org_id = await _user_org(user_id)
    if org_id:
        org_cap = await _org_cap(org_id)
        if org_cap is not None:
            try:
                org_agg = await db.daily_budget.aggregate([
                    {"$match": {"org_id": org_id, "day": _today()}},
                    {"$group": {"_id": None, "total": {"$sum": "$spent_usd"}}},
                ]).to_list(1)
            except Exception:
                org_agg = []
            org_spent = float((org_agg[0]["total"] if org_agg else 0.0))
            if org_spent + expected_cost_usd > org_cap:
                return False, org_spent, org_cap

    if user_spent + expected_cost_usd > user_cap:
        return False, user_spent, user_cap
    return True, user_spent, user_cap


async def record(user_id: str, cost_usd: float, *, org_id: str | None = None) -> None:
    """Increment today's counter. Upserts if today's row doesn't exist.
    Populates org_id on the row so org-level aggregations work."""
    if cost_usd <= 0:
        return
    await _ensure_index()
    from db import db
    import time as _t
    if org_id is None:
        org_id = await _user_org(user_id)
    try:
        await db.daily_budget.update_one(
            {"user_id": user_id, "day": _today()},
            {
                "$inc": {"spent_usd": cost_usd, "calls": 1},
                "$setOnInsert": {"created_at_epoch": _t.time()},
                "$set": {"org_id": org_id} if org_id else {},
            },
            upsert=True,
        )
    except Exception as exc:
        logger.info("daily_budget record failed: %s", exc)


async def snapshot(user_id: str) -> dict[str, Any]:
    """Admin view: today + last 7 days."""
    from db import db
    cap = await get_cap(user_id)
    try:
        rows = await db.daily_budget.find({"user_id": user_id}).sort("day", -1).limit(7).to_list(7)
    except Exception:
        rows = []
    return {
        "cap_usd": cap,
        "today_spent_usd": float(next((r["spent_usd"] for r in rows if r["day"] == _today()), 0.0)),
        "last_7_days": [{"day": r["day"], "spent_usd": r["spent_usd"], "calls": r.get("calls", 0)} for r in rows],
    }
