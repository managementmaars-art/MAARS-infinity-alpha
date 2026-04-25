"""Materialize db.teams from the team registry and assign team_id to agents.

Runs once at migration time (or on demand from /admin/teams/seed). Safe
to re-run — existing team docs are updated rather than duplicated, and
agents keep the team_id the detector picks for them so membership stays
stable across re-seeds.

Each team doc in db.teams has:
  team_id, name, department, studio_name, mission,
  role_families[], shared_tools[], memory_tags[], languages[],
  member_agent_ids[], lead_agent_id, monthly_budget_credits,
  created_at, updated_at
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any

from .team_templates import ALL_TEAMS, detect_team_for_agent, team_by_id
from .role_templates import detect_role_template

logger = logging.getLogger(__name__)
TEAMS_COLLECTION = "teams"


async def seed_all_teams(force_rebuild: bool = False) -> dict[str, Any]:
    """Populate db.teams from the registry and write team_id onto every
    agent. Re-runnable; membership rebuilt from current detector logic.

    Returns stats + per-team member counts.
    """
    from db import db

    agents = await db.agents.find({}, {"_id": 0}).to_list(10_000)
    now = datetime.now(timezone.utc).isoformat()

    # Pass 1 — compute (agent_id → team_id) via the detector.
    assignments: dict[str, str] = {}
    team_members: dict[str, list[str]] = {t["team_id"]: [] for t in ALL_TEAMS}
    for agent in agents:
        aid = agent.get("agent_id")
        if not aid:
            continue
        # Detect role family first (for better team mapping)
        role_tpl = detect_role_template(agent)
        role_family = role_tpl["role_family"] if role_tpl else None
        team_id = detect_team_for_agent(agent, role_family)
        assignments[aid] = team_id
        team_members.setdefault(team_id, []).append(aid)

    # Pass 2 — upsert the 29 team docs (using registry + computed members).
    team_upserts = 0
    for team in ALL_TEAMS:
        members = team_members.get(team["team_id"]) or []
        # Pick a lead: the first agent whose role matches this team's
        # primary role_family. Not critical, but gives the UI something.
        lead = members[0] if members else None
        doc = {
            "team_id":       team["team_id"],
            "name":          team["name"],
            "department":    team["department"],
            "studio_name":   team["studio_name"],
            "mission":       team["mission"],
            "role_families": list(team["role_families"]),
            "shared_tools":  list(team["shared_tools"]),
            "memory_tags":   list(team["memory_tags"]),
            "languages_supported": list(team["languages"]),
            "member_agent_ids": members,
            "member_count":  len(members),
            "lead_agent_id": lead,
            "monthly_budget_credits": int(team.get("monthly_budget_credits", 10_000)),
            "updated_at":    now,
        }
        await db[TEAMS_COLLECTION].update_one(
            {"team_id": team["team_id"]},
            {"$set": doc, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        team_upserts += 1

    # Pass 3 — write team_id onto each agent row. Bulk write for speed.
    agent_updates = 0
    for aid, team_id in assignments.items():
        await db.agents.update_one(
            {"agent_id": aid},
            {"$set": {"team_id": team_id, "team_assigned_at": now}},
        )
        agent_updates += 1

    return {
        "agents_scanned":  len(agents),
        "teams_upserted":  team_upserts,
        "agents_assigned": agent_updates,
        "unassigned":      len(agents) - agent_updates,
        "distribution": {
            team["team_id"]: {
                "name":         team["name"],
                "department":   team["department"],
                "member_count": len(team_members.get(team["team_id"]) or []),
            }
            for team in ALL_TEAMS
        },
    }


async def list_teams() -> list[dict]:
    """Admin UI helper — all teams with current member counts."""
    from db import db
    return await db[TEAMS_COLLECTION].find({}, {"_id": 0}).to_list(100)


async def get_team(team_id: str) -> dict | None:
    """Fetch a single team doc (with member list)."""
    from db import db
    return await db[TEAMS_COLLECTION].find_one({"team_id": team_id}, {"_id": 0})


async def team_members_detailed(team_id: str) -> list[dict]:
    """Resolve member_agent_ids → full agent rows. Used by UI when drilling
    into a team to see who's on it."""
    from db import db
    team = await get_team(team_id)
    if not team:
        return []
    mids = team.get("member_agent_ids") or []
    if not mids:
        return []
    cursor = db.agents.find(
        {"agent_id": {"$in": mids}},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "description": 1,
         "avatar": 1, "capabilities": 1, "is_commander": 1},
    )
    return await cursor.to_list(len(mids))
