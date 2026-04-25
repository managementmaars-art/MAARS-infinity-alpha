"""Admin team-management endpoints.

Lives alongside routes/agent_offices.py. The team model is the collaborative
workspace layer on top of individual agent offices.

Routes:
  POST /admin/teams/seed            — materialize all teams + assign agents
  GET  /admin/teams                 — list all teams with member counts
  GET  /admin/teams/{team_id}       — single team with full details
  GET  /admin/teams/{team_id}/members — resolved member agent rows
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from auth import require_admin, User
from services.agents import team_seeder

router = APIRouter()


@router.post("/admin/teams/seed")
async def seed_teams(
    force_rebuild: bool = False,
    _admin: User = Depends(require_admin),
):
    """Populate db.teams from the registry + assign each agent a team_id.

    Safe to re-run. `force_rebuild=True` currently behaves the same as
    default — always upserts fresh team state from current detector
    logic. Reserved for future "wipe + rebuild" semantics."""
    result = await team_seeder.seed_all_teams(force_rebuild=force_rebuild)
    return result


@router.get("/admin/teams")
async def list_teams(_admin: User = Depends(require_admin)):
    """List every team with its current member count + department."""
    teams = await team_seeder.list_teams()
    teams.sort(key=lambda t: (-(t.get("member_count") or 0), t.get("team_id", "")))
    return {"count": len(teams), "teams": teams}


@router.get("/admin/teams/{team_id}")
async def get_team(team_id: str, _admin: User = Depends(require_admin)):
    team = await team_seeder.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"team '{team_id}' not found")
    return team


@router.get("/admin/teams/{team_id}/members")
async def get_team_members(team_id: str, _admin: User = Depends(require_admin)):
    team = await team_seeder.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"team '{team_id}' not found")
    members = await team_seeder.team_members_detailed(team_id)
    return {
        "team_id":      team_id,
        "team_name":    team.get("name"),
        "studio_name":  team.get("studio_name"),
        "member_count": len(members),
        "members":      members,
    }
