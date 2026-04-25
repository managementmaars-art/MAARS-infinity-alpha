"""Per-provider command-center dashboard data.

For each integration the operator has connected, this service rolls up:
  • Connection status (API + browser)
  • Recent agent actions on that platform (from integration_action_log)
  • Pollable activity (DMs / mentions / comments — see integration_activity.py)
  • Which agents currently have authority
  • Provider-specific capabilities the agents can invoke

Used by /apps/{provider} command-center pages so each integration has
its own dedicated section in the UI.
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)


async def dashboard(provider: str, user_id: str) -> dict[str, Any]:
    """Single call returning everything needed to paint a provider page."""
    from services import integration_driver
    from db import db

    # 1. Status (API/browser readiness)
    status = await integration_driver.status(provider, user_id)
    if not status.get("known"):
        # status() returns just {provider, known: False} for unknown providers
        # but actually returns the full dict for known ones. Let's check
        # the modes_available key as a sanity signal.
        if not status.get("modes_available"):
            return {"ok": False, "error": f"unknown_provider: {provider}"}

    # 2. Recent actions (filtered to this provider)
    cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    cursor = db.integration_action_log.find(
        {"user_id": user_id, "provider": provider, "at": {"$gte": cutoff_24h}},
        {"_id": 0},
    ).sort("at", -1).limit(20)
    recent_actions = await cursor.to_list(length=20)

    # 3. Action volume (24h totals)
    total_24h = await db.integration_action_log.count_documents({
        "user_id": user_id, "provider": provider, "at": {"$gte": cutoff_24h},
    })
    failed_24h = await db.integration_action_log.count_documents({
        "user_id": user_id, "provider": provider,
        "at": {"$gte": cutoff_24h}, "ok": False,
    })

    # 4. Agents with authority on this provider
    grants = await db.integration_authority.find(
        {"user_id": user_id, "providers": provider},
        {"_id": 0, "agent_id": 1, "actions": 1, "expires_at": 1},
    ).to_list(length=50)
    granted_agents: list[dict[str, Any]] = []
    for g in grants:
        if not g.get("agent_id"):
            continue
        agent = await db.agents.find_one(
            {"agent_id": g["agent_id"]},
            {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "avatar": 1},
        )
        if agent:
            granted_agents.append({
                **agent,
                "actions_allowed": g.get("actions"),
                "expires_at":      g.get("expires_at"),
            })

    # 5. Last poll marker + unseen count (from integration_activity_meta / _activity)
    meta = await db.integration_activity_meta.find_one(
        {"user_id": user_id, "provider": provider},
        {"_id": 0, "polled_at": 1, "last_count": 1},
    )
    unseen_count = await db.integration_activity.count_documents(
        {"user_id": user_id, "provider": provider, "seen": False},
    )

    return {
        "ok":            True,
        "provider":      provider,
        "display_name":  status.get("display_name") or provider,
        "category":      status.get("category"),
        "status":        status,
        "totals_24h": {
            "actions": total_24h,
            "failed":  failed_24h,
            "error_rate_pct": round((failed_24h / total_24h) * 100, 1) if total_24h else 0.0,
        },
        "recent_actions":    recent_actions,
        "granted_agents":    granted_agents,
        "last_polled_at":    (meta or {}).get("polled_at"),
        "unseen_count":      unseen_count,
        "actions_available": (status.get("api_actions") or []) + (status.get("browser_actions") or []),
    }
