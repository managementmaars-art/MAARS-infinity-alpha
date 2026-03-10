"""Agent Team Builder API routes."""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent-teams", tags=["agent-teams"])


class AgentTeamCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    purpose: Optional[str] = ""
    agent_ids: List[str] = []


class AgentTeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    agent_ids: Optional[List[str]] = None


@router.post("")
async def create_agent_team(data: AgentTeamCreate, current_user: User = Depends(get_current_user)):
    team_id = f"ateam_{uuid.uuid4().hex[:12]}"
    team = {
        "team_id": team_id,
        "name": data.name,
        "description": data.description,
        "purpose": data.purpose,
        "agent_ids": data.agent_ids,
        "created_by": current_user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_teams.insert_one(team)
    team.pop("_id", None)
    return team


@router.get("")
async def list_agent_teams(current_user: User = Depends(get_current_user)):
    teams = await db.agent_teams.find(
        {"created_by": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return teams


@router.get("/{team_id}")
async def get_agent_team(team_id: str, current_user: User = Depends(get_current_user)):
    team = await db.agent_teams.find_one(
        {"team_id": team_id, "created_by": current_user.user_id}, {"_id": 0}
    )
    if not team:
        raise HTTPException(404, "Team not found")
    return team


@router.put("/{team_id}")
async def update_agent_team(team_id: str, data: AgentTeamUpdate, current_user: User = Depends(get_current_user)):
    team = await db.agent_teams.find_one({"team_id": team_id, "created_by": current_user.user_id})
    if not team:
        raise HTTPException(404, "Team not found")
    updates = {k: v for k, v in data.dict().items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.agent_teams.update_one({"team_id": team_id}, {"$set": updates})
    updated = await db.agent_teams.find_one({"team_id": team_id}, {"_id": 0})
    return updated


@router.delete("/{team_id}")
async def delete_agent_team(team_id: str, current_user: User = Depends(get_current_user)):
    result = await db.agent_teams.delete_one({"team_id": team_id, "created_by": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Team not found")
    return {"status": "deleted", "team_id": team_id}
