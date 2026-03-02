"""Agent CRUD and user customization endpoints."""
import uuid
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from db import db
from auth import get_current_user, require_admin, User, ADMIN_EMAIL
from models.schemas import Agent, AgentCreate
from shared.constants import SUBSCRIPTION_PLANS, CUSTOM_AGENT_CREDIT_COST
from config import AGENT_TOOL_MAP, AGENT_TOOLS

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/agents/public")
async def get_agents_public():
    """Public endpoint: return default agents (no auth required)"""
    agents = await db.agents.find(
        {"is_custom": False, "is_active": {"$ne": False}},
        {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1, "description": 1, "capabilities": 1, "is_commander": 1}
    ).to_list(50)
    # Inject tools info
    for agent in agents:
        agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    agents.sort(key=lambda a: (0 if a.get("agent_id") == "agent_commander" else 1, a.get("name", "")))
    return agents

@router.get("/agents/tools")
async def get_available_tools():
    """Get all available tools and their descriptions"""
    return {
        "tools": {name: {"name": t["name"], "description": t["description"]} for name, t in AGENT_TOOLS.items()},
        "agent_tools": AGENT_TOOL_MAP
    }

@router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user)):
    # Get default agents and user's custom agents, filter out deactivated ones
    agents = await db.agents.find(
        {"$or": [{"is_custom": False}, {"creator_id": current_user.user_id}], "is_active": {"$ne": False}},
        {"_id": 0}
    ).to_list(100)
    
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
        # Inject tools info from AGENT_TOOL_MAP
        if not agent.get("tools"):
            agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    
    # Sort: Commander first, then others
    agents.sort(key=lambda a: (0 if a.get("agent_id") == "agent_commander" else 1, a.get("name", "")))
    
    return agents

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if isinstance(agent.get('created_at'), str):
        agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    
    return agent

@router.post("/agents", response_model=Agent)
async def create_agent(agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    is_admin = current_user.email == ADMIN_EMAIL
    
    # Get user subscription
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not user_sub:
        user_sub = {
            "user_id": current_user.user_id,
            "plan_id": "free",
            "credits": 50,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(user_sub)
    
    plan_id = user_sub.get("plan_id", "free")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_custom = plan.get("max_custom_agents", 0)
    
    if not is_admin:
        # Check plan limit (-1 means unlimited)
        if max_custom != -1:
            current_custom_count = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
            if current_custom_count >= max_custom:
                if max_custom == 0:
                    raise HTTPException(status_code=403, detail="Custom agent creation is not available on the Free plan. Please upgrade to Starter or higher.")
                raise HTTPException(status_code=403, detail=f"You've reached the custom agent limit ({max_custom}) for your {plan['name']} plan. Upgrade to create more.")
        
        # Check credits
        credits_remaining = user_sub.get("credits", 0)
        if credits_remaining < CUSTOM_AGENT_CREDIT_COST:
            raise HTTPException(status_code=402, detail=f"Creating a custom agent costs {CUSTOM_AGENT_CREDIT_COST} credits. You have {credits_remaining} credits remaining.")
    
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    
    agent_doc = {
        "agent_id": agent_id,
        "name": agent_data.name,
        "description": agent_data.description,
        "avatar": agent_data.avatar or "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/43ae7e2a837703cb3a5da4fdd616bc12c825f9f0f15b7e9304e61a3dab0bd257.png",
        "role": agent_data.role,
        "system_prompt": agent_data.system_prompt,
        "model_provider": agent_data.model_provider,
        "model_name": agent_data.model_name,
        "is_custom": True,
        "creator_id": current_user.user_id,
        "capabilities": agent_data.capabilities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.agents.insert_one(agent_doc)
    
    # Deduct credits for non-admin users
    if not is_admin:
        await db.subscriptions.update_one(
            {"user_id": current_user.user_id},
            {"$inc": {"credits": -CUSTOM_AGENT_CREDIT_COST, "credits_used": CUSTOM_AGENT_CREDIT_COST}}
        )
    
    agent_doc.pop("_id", None)
    agent_doc['created_at'] = datetime.fromisoformat(agent_doc['created_at'])
    return Agent(**agent_doc)

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if not agent.get("is_custom") or agent.get("creator_id") != current_user.user_id:
        raise HTTPException(status_code=403, detail="Cannot delete this agent")
    
    await db.agents.delete_one({"agent_id": agent_id})
    return {"message": "Agent deleted"}

@router.get("/agents/create/info")
async def get_create_agent_info(current_user: User = Depends(get_current_user)):
    """Get info about custom agent creation limits and cost for current user"""
    is_admin = current_user.email == ADMIN_EMAIL
    
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    plan_id = user_sub.get("plan_id", "free") if user_sub else "free"
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_custom = plan.get("max_custom_agents", 0)
    credits = user_sub.get("credits", 0) if user_sub else 0
    
    current_custom_count = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
    
    return {
        "credit_cost": CUSTOM_AGENT_CREDIT_COST,
        "credits_remaining": credits,
        "can_afford": credits >= CUSTOM_AGENT_CREDIT_COST or is_admin,
        "max_custom_agents": max_custom if not is_admin else -1,
        "current_custom_count": current_custom_count,
        "can_create": is_admin or (max_custom == -1 or current_custom_count < max_custom) and credits >= CUSTOM_AGENT_CREDIT_COST,
        "plan_name": plan["name"],
        "is_admin": is_admin
    }




# ============== USER AGENT CUSTOMIZATION ==============

@router.get("/agents/{agent_id}/my-settings")
async def get_user_agent_settings(agent_id: str, current_user: User = Depends(get_current_user)):
    """Get user's personal customization for an agent."""
    override = await db.user_agent_overrides.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    if not override:
        return {"agent_id": agent_id, "has_override": False}
    override["has_override"] = True
    return override

@router.put("/agents/{agent_id}/my-settings")
async def update_user_agent_settings(agent_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Save user's personal agent customization (temperature, max_tokens, personality_tone, custom_instructions)."""
    data = await request.json()
    allowed = {"temperature", "max_tokens", "personality_tone", "custom_instructions"}
    update = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not update:
        raise HTTPException(400, "No valid fields to update")
    
    # Validate ranges
    if "temperature" in update:
        update["temperature"] = max(0, min(2, float(update["temperature"])))
    if "max_tokens" in update:
        update["max_tokens"] = max(256, min(16384, int(update["max_tokens"])))
    
    await db.user_agent_overrides.update_one(
        {"user_id": current_user.user_id, "agent_id": agent_id},
        {"$set": {**update, "user_id": current_user.user_id, "agent_id": agent_id, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    result = await db.user_agent_overrides.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    result["has_override"] = True
    return result

@router.delete("/agents/{agent_id}/my-settings")
async def reset_user_agent_settings(agent_id: str, current_user: User = Depends(get_current_user)):
    """Reset user's agent customization back to defaults."""
    await db.user_agent_overrides.delete_one({"user_id": current_user.user_id, "agent_id": agent_id})
    return {"success": True, "agent_id": agent_id}
