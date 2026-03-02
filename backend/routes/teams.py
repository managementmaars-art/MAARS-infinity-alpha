"""Team collaboration endpoints."""
import os
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from db import db
from auth import get_current_user, User
from models.schemas import TeamCreate, TeamInvite, TeamMemberUpdate
from shared.constants import SUBSCRIPTION_PLANS
from shared.utils import send_email_notification, create_notification

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/teams")
async def create_team(data: TeamCreate, current_user: User = Depends(get_current_user)):
    """Create a new team. Owner is the creator."""
    existing = await db.teams.find_one({"owner_id": current_user.user_id})
    if existing:
        raise HTTPException(400, "You already own a team. Delete it first to create a new one.")
    
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    team = {
        "team_id": team_id,
        "name": data.name,
        "owner_id": current_user.user_id,
        "members": [
            {"user_id": current_user.user_id, "role": "owner", "email": current_user.email, "name": current_user.name, "joined_at": datetime.now(timezone.utc).isoformat()}
        ],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.insert_one(team)
    team.pop("_id", None)
    return team

@router.get("/teams")
async def get_my_teams(current_user: User = Depends(get_current_user)):
    """Get all teams the user belongs to (as owner or member)."""
    teams = await db.teams.find(
        {"members.user_id": current_user.user_id}, {"_id": 0}
    ).to_list(20)
    return teams

@router.get("/teams/{team_id}")
async def get_team(team_id: str, current_user: User = Depends(get_current_user)):
    """Get a single team's details."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id}, {"_id": 0})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    return team

@router.post("/teams/{team_id}/invite")
async def invite_to_team(team_id: str, data: TeamInvite, current_user: User = Depends(get_current_user)):
    """Invite a user by email. Only owner and admins can invite."""
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not team:
        raise HTTPException(404, "Team not found")
    
    # Check permissions
    member = next((m for m in team["members"] if m["user_id"] == current_user.user_id), None)
    if not member or member["role"] not in ("owner", "admin"):
        raise HTTPException(403, "Only team owners and admins can invite members")
    
    # Check team size limit
    user_sub = await db.subscriptions.find_one({"user_id": team["owner_id"]}, {"_id": 0})
    plan_id = user_sub.get("plan_id", "free") if user_sub else "free"
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_members = plan.get("max_team_members", 1)
    if max_members != -1 and len(team["members"]) >= max_members:
        raise HTTPException(400, f"Team size limit reached ({max_members} members on {plan['name']} plan). Upgrade to add more members.")
    
    # Check if already a member
    if any(m.get("email") == data.email for m in team["members"]):
        raise HTTPException(400, "This user is already a team member")
    
    # Check for existing pending invite
    existing_invite = await db.team_invites.find_one({"team_id": team_id, "email": data.email, "status": "pending"})
    if existing_invite:
        raise HTTPException(400, "An invite is already pending for this email")
    
    invite_token = uuid.uuid4().hex
    invite = {
        "invite_id": f"inv_{uuid.uuid4().hex[:12]}",
        "team_id": team_id,
        "team_name": team["name"],
        "email": data.email,
        "role": data.role if data.role in ("admin", "member") else "member",
        "invited_by": current_user.user_id,
        "invited_by_name": current_user.name,
        "status": "pending",
        "token": invite_token,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.team_invites.insert_one(invite)
    invite.pop("_id", None)
    
    # Notify the invited user if they already have an account
    invited_user = await db.users.find_one({"email": data.email}, {"_id": 0, "user_id": 1})
    if invited_user:
        await create_notification(invited_user["user_id"], "team_invite", f"Team Invite: {team['name']}", f"{current_user.name} invited you to join {team['name']}. Check your pending invites.", "/team")
    
    # Send email notification (non-blocking, skips if SMTP not configured)
    asyncio.create_task(send_email_notification(
        to_email=data.email,
        subject=f"You've been invited to {team['name']} on MAARS Command",
        html_body=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#111;color:#fff;border-radius:12px;">
            <h2 style="color:#818cf8;">You're Invited!</h2>
            <p>{current_user.name} has invited you to join <strong>{team['name']}</strong> on MAARS Command as a <strong>{data.role}</strong>.</p>
            <p>Log in to your MAARS Command account to accept the invitation and start collaborating with your team.</p>
            <p style="margin-top:20px;"><a href="{os.environ.get('FRONTEND_URL', 'https://maarscommand.com')}/team" style="display:inline-block;padding:12px 24px;background:linear-gradient(to right,#6366f1,#8b5cf6);color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;">Accept Invitation</a></p>
            <p style="color:#888;font-size:12px;margin-top:30px;">MAARS Command by MAARS Global Corporation</p>
        </div>"""
    ))
    
    return invite

@router.get("/teams/invites/pending")
async def get_my_pending_invites(current_user: User = Depends(get_current_user)):
    """Get all pending invites for the current user."""
    invites = await db.team_invites.find(
        {"email": current_user.email, "status": "pending"}, {"_id": 0}
    ).to_list(50)
    return invites

@router.post("/teams/invites/{invite_id}/accept")
async def accept_invite(invite_id: str, current_user: User = Depends(get_current_user)):
    """Accept a team invite."""
    invite = await db.team_invites.find_one({"invite_id": invite_id, "email": current_user.email, "status": "pending"})
    if not invite:
        raise HTTPException(404, "Invite not found or already responded")
    
    team = await db.teams.find_one({"team_id": invite["team_id"]})
    if not team:
        raise HTTPException(404, "Team no longer exists")
    
    # Add member
    new_member = {
        "user_id": current_user.user_id,
        "role": invite["role"],
        "email": current_user.email,
        "name": current_user.name,
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.update_one(
        {"team_id": invite["team_id"]},
        {"$push": {"members": new_member}}
    )
    await db.team_invites.update_one({"invite_id": invite_id}, {"$set": {"status": "accepted"}})
    
    # Notify team owner
    owner_id = team.get("owner_id")
    if owner_id:
        await create_notification(owner_id, "team_join", f"{current_user.name} joined your team", f"{current_user.name} accepted the invite to {team.get('name', 'your team')}.", "/team")
    
    return {"success": True, "team_id": invite["team_id"], "team_name": invite["team_name"]}

@router.post("/teams/invites/{invite_id}/decline")
async def decline_invite(invite_id: str, current_user: User = Depends(get_current_user)):
    """Decline a team invite."""
    invite = await db.team_invites.find_one({"invite_id": invite_id, "email": current_user.email, "status": "pending"})
    if not invite:
        raise HTTPException(404, "Invite not found or already responded")
    await db.team_invites.update_one({"invite_id": invite_id}, {"$set": {"status": "declined"}})
    return {"success": True}

@router.put("/teams/{team_id}/members/{user_id}")
async def update_member_role(team_id: str, user_id: str, data: TeamMemberUpdate, current_user: User = Depends(get_current_user)):
    """Update a team member's role. Only owner can change roles."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    if team["owner_id"] != current_user.user_id:
        raise HTTPException(403, "Only the team owner can change roles")
    if user_id == current_user.user_id:
        raise HTTPException(400, "Cannot change your own role")
    if data.role not in ("admin", "member"):
        raise HTTPException(400, "Role must be 'admin' or 'member'")
    
    result = await db.teams.update_one(
        {"team_id": team_id, "members.user_id": user_id},
        {"$set": {"members.$.role": data.role}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Member not found in team")
    return {"success": True}

@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_member(team_id: str, user_id: str, current_user: User = Depends(get_current_user)):
    """Remove a member from team. Owner/admins can remove, or members can leave."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    
    member = next((m for m in team["members"] if m["user_id"] == current_user.user_id), None)
    if not member:
        raise HTTPException(403, "You are not a member of this team")
    
    # Owners can't be removed
    if user_id == team["owner_id"]:
        raise HTTPException(400, "Cannot remove the team owner")
    
    # Self-removal (leaving) is always allowed
    is_self = user_id == current_user.user_id
    if not is_self and member["role"] not in ("owner", "admin"):
        raise HTTPException(403, "Only owners and admins can remove members")
    
    await db.teams.update_one(
        {"team_id": team_id},
        {"$pull": {"members": {"user_id": user_id}}}
    )
    return {"success": True}

@router.delete("/teams/{team_id}")
async def delete_team(team_id: str, current_user: User = Depends(get_current_user)):
    """Delete a team. Only the owner can delete."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    if team["owner_id"] != current_user.user_id:
        raise HTTPException(403, "Only the team owner can delete the team")
    
    await db.teams.delete_one({"team_id": team_id})
    await db.team_invites.delete_many({"team_id": team_id})
    # Unshare all team chats
    await db.chats.update_many(
        {"shared_with_team": team_id},
        {"$unset": {"shared_with_team": ""}}
    )
    return {"success": True}

@router.post("/chats/{chat_id}/share")
async def share_chat_with_team(chat_id: str, current_user: User = Depends(get_current_user)):
    """Toggle sharing a chat with the user's team."""
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id})
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    team = await db.teams.find_one({"members.user_id": current_user.user_id}, {"_id": 0, "team_id": 1})
    if not team:
        raise HTTPException(400, "You are not part of any team")
    
    is_shared = chat.get("shared_with_team") == team["team_id"]
    if is_shared:
        await db.chats.update_one({"chat_id": chat_id}, {"$unset": {"shared_with_team": ""}})
        return {"shared": False}
    else:
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"shared_with_team": team["team_id"]}})
        # Notify team members
        full_team = await db.teams.find_one({"team_id": team["team_id"]})
        if full_team:
            for m in full_team.get("members", []):
                if m["user_id"] != current_user.user_id:
                    await create_notification(m["user_id"], "team_share", f"Chat shared in {full_team.get('name', 'your team')}", f"{current_user.name} shared a chat: {chat.get('title', 'Untitled')}", "/team")
        return {"shared": True, "team_id": team["team_id"]}

@router.get("/teams/{team_id}/shared-chats")
async def get_shared_chats(team_id: str, current_user: User = Depends(get_current_user)):
    """Get all chats shared with this team."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    
    chats = await db.chats.find(
        {"shared_with_team": team_id},
        {"_id": 0, "chat_id": 1, "title": 1, "agent_id": 1, "user_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(100)
    
    # Add owner info
    for chat in chats:
        owner = await db.users.find_one({"user_id": chat["user_id"]}, {"_id": 0, "name": 1, "email": 1})
        chat["owner_name"] = owner.get("name", "Unknown") if owner else "Unknown"
    
    return chats


@router.get("/teams/{team_id}/activity")
async def get_team_activity(team_id: str, limit: int = 30, current_user: User = Depends(get_current_user)):
    """Get recent activity for a team - chats, messages, member actions."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    
    member_ids = [m["user_id"] for m in team.get("members", [])]
    member_map = {m["user_id"]: m.get("name", m.get("email", "Unknown")) for m in team["members"]}
    
    activity = []
    
    # Recent shared chats
    shared_chats = await db.chats.find(
        {"shared_with_team": team_id},
        {"_id": 0, "chat_id": 1, "title": 1, "user_id": 1, "updated_at": 1, "agent_id": 1}
    ).sort("updated_at", -1).to_list(10)
    
    for chat in shared_chats:
        activity.append({
            "type": "shared_chat",
            "user_name": member_map.get(chat["user_id"], "Unknown"),
            "title": f"Shared: {chat.get('title', 'Untitled chat')}",
            "timestamp": chat.get("updated_at", ""),
            "chat_id": chat["chat_id"],
            "agent_id": chat.get("agent_id", ""),
        })
    
    # Recent messages from team members (last N messages)
    recent_chats = await db.chats.find(
        {"user_id": {"$in": member_ids}},
        {"_id": 0, "chat_id": 1, "title": 1, "user_id": 1, "agent_id": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(15)
    
    for chat in recent_chats:
        if chat["chat_id"] not in [a.get("chat_id") for a in activity]:
            activity.append({
                "type": "member_chat",
                "user_name": member_map.get(chat["user_id"], "Unknown"),
                "title": chat.get("title", "Untitled chat"),
                "timestamp": chat.get("updated_at", ""),
                "chat_id": chat["chat_id"],
                "agent_id": chat.get("agent_id", ""),
            })
    
    # Sort by timestamp
    activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return activity[:limit]


@router.get("/teams/{team_id}/stats")
async def get_team_stats(team_id: str, current_user: User = Depends(get_current_user)):
    """Get team usage statistics."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    
    member_ids = [m["user_id"] for m in team.get("members", [])]
    
    total_chats = await db.chats.count_documents({"user_id": {"$in": member_ids}})
    shared_chats = await db.chats.count_documents({"shared_with_team": team_id})
    
    # Per-member stats
    member_stats = []
    for member in team.get("members", []):
        uid = member["user_id"]
        chat_count = await db.chats.count_documents({"user_id": uid})
        member_stats.append({
            "user_id": uid,
            "name": member.get("name", "Unknown"),
            "email": member.get("email", ""),
            "role": member.get("role", "member"),
            "chats": chat_count,
            "joined_at": member.get("joined_at", ""),
        })
    
    return {
        "team_id": team_id,
        "team_name": team.get("name", ""),
        "member_count": len(member_ids),
        "total_chats": total_chats,
        "shared_chats": shared_chats,
        "members": member_stats,
    }

