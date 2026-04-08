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
from config import AGENT_TOOL_MAP, AGENT_TOOLS, DEFAULT_BRAIN_PROFILES
from services.cache_service import cache
from infinity_catalog import generate_rich_svg_avatar

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/agents/public")
async def get_agents_public():
    """Public endpoint: return default agents (no auth required)"""
    cached = cache.get("agents_public")
    if cached:
        return cached
    agents = await db.agents.find(
        {"is_custom": False, "is_active": {"$ne": False}},
        {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1, "description": 1, "capabilities": 1, "is_commander": 1}
    ).to_list(50)
    for agent in agents:
        agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
        if not agent.get("name"):
            agent["name"] = agent.get("role", "Agent").split()[0] + " Agent"
        if not agent.get("avatar"):
            agent["avatar"] = generate_rich_svg_avatar(agent.get("name", "Agent"), "", 0)
    agents.sort(key=lambda a: (0 if a.get("agent_id") == "agent_commander" else 1, a.get("name", "")))
    cache.set("agents_public", agents, ttl=120)
    return agents

@router.get("/agents/tools")
async def get_available_tools():
    """Get all available tools and their descriptions"""
    return {
        "tools": {name: {"name": t["name"], "description": t["description"]} for name, t in AGENT_TOOLS.items()},
        "agent_tools": AGENT_TOOL_MAP
    }

@router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user), network: str = None):
    # Get default agents and user's custom agents, filter out deactivated ones
    query = {"$or": [{"is_custom": False}, {"creator_id": current_user.user_id}], "is_active": {"$ne": False}}
    if network:
        query["network"] = network
    agents = await db.agents.find(query, {"_id": 0}).to_list(500)
    
    needs_avatar_patch = []
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
        # Inject tools info from AGENT_TOOL_MAP or infinity tools
        if not agent.get("tools"):
            agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
        # Ensure every agent has a name and avatar — patch on the fly if missing
        if not agent.get("name"):
            agent["name"] = agent.get("role", "Agent").split()[0] + " Agent"
        if not agent.get("avatar"):
            svg = generate_rich_svg_avatar(
                agent.get("name", "Agent"),
                agent.get("network", ""),
                0
            )
            agent["avatar"] = svg
            needs_avatar_patch.append({"agent_id": agent["agent_id"], "avatar": svg, "name": agent["name"]})

    # Persist any patched avatars/names back to DB asynchronously (fire-and-forget)
    if needs_avatar_patch:
        import asyncio
        async def _patch():
            for p in needs_avatar_patch:
                await db.agents.update_one(
                    {"agent_id": p["agent_id"]},
                    {"$set": {"avatar": p["avatar"], "name": p["name"]}}
                )
        asyncio.create_task(_patch())

    # Sort: Commander first, then original agents, then infinity agents
    agents.sort(key=lambda a: (
        0 if a.get("agent_id") == "agent_commander" else
        1 if not a.get("is_infinity") else 2,
        a.get("name", "")
    ))

    return agents

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if isinstance(agent.get('created_at'), str):
        agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    if not agent.get("name"):
        agent["name"] = agent.get("role", "Agent").split()[0] + " Agent"
    if not agent.get("avatar"):
        agent["avatar"] = generate_rich_svg_avatar(
            agent.get("name", "Agent"), agent.get("network", ""), 0
        )

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

    # Ingest skills + provider knowledge for the new agent (fire-and-forget)
    import asyncio
    async def _ingest_new_agent():
        try:
            from pathlib import Path
            from services.skills_service import ensure_agent_skills, ensure_provider_skills
            skills_root = Path(__file__).parent.parent.parent / ".claude" / "skills"
            await ensure_agent_skills(agent_doc, db, skills_root)
            await ensure_provider_skills(agent_doc, db)
        except Exception as e:
            logger.warning(f"Skill ingestion for new agent {agent_id}: {e}")
    asyncio.create_task(_ingest_new_agent())

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


# ============== CUSTOM BRAIN PROFILES ==============

@router.get("/agents/{agent_id}/brain")
async def get_agent_brain(agent_id: str, current_user: User = Depends(get_current_user)):
    """Get an agent's Custom Brain Profile."""
    # Check user-specific override first
    user_brain = await db.agent_brains.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    if user_brain:
        user_brain["is_custom"] = True
        return user_brain

    # Fall back to default brain profile
    default = DEFAULT_BRAIN_PROFILES.get(agent_id, {})
    if not default:
        # Generate a generic default for agents without predefined profiles
        default = {
            "primary_model": {"provider": "openai", "model": "gpt-5.2"},
            "fallback_models": [{"provider": "openai", "model": "gpt-4o"}],
            "memory_scopes": ["working", "shared"],
            "autonomy_level": 3,
            "approval_required": False,
            "output_templates": [],
            "kpis": [],
            "escalation_rules": [],
            "communication_style": "Professional and helpful",
            "risk_boundaries": {"max_budget_authority": 0, "can_approve_external_comms": False},
        }
    return {"agent_id": agent_id, "is_custom": False, **default}


@router.put("/agents/{agent_id}/brain")
async def update_agent_brain(agent_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Update an agent's Custom Brain Profile for the current user."""
    data = await request.json()
    allowed_fields = {
        "primary_model", "fallback_models", "memory_scopes", "autonomy_level",
        "approval_required", "output_templates", "kpis", "escalation_rules",
        "communication_style", "risk_boundaries"
    }
    update = {k: v for k, v in data.items() if k in allowed_fields}
    if not update:
        raise HTTPException(400, "No valid fields to update")

    # Validate autonomy_level
    if "autonomy_level" in update:
        update["autonomy_level"] = max(0, min(5, int(update["autonomy_level"])))

    await db.agent_brains.update_one(
        {"user_id": current_user.user_id, "agent_id": agent_id},
        {"$set": {
            **update,
            "user_id": current_user.user_id,
            "agent_id": agent_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    result = await db.agent_brains.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    result["is_custom"] = True
    return result


@router.delete("/agents/{agent_id}/brain")
async def reset_agent_brain(agent_id: str, current_user: User = Depends(get_current_user)):
    """Reset an agent's brain profile to defaults."""
    await db.agent_brains.delete_one({"user_id": current_user.user_id, "agent_id": agent_id})
    return {"success": True, "agent_id": agent_id}


@router.put("/agents/{agent_id}/visibility")
async def toggle_agent_visibility(agent_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Toggle agent visibility (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")
    data = await request.json()
    hidden = data.get("hidden", False)
    result = await db.agents.update_one(
        {"agent_id": agent_id},
        {"$set": {"hidden": hidden}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Agent not found")
    return {"agent_id": agent_id, "hidden": hidden}



@router.get("/brain-profiles")
async def list_brain_profiles(current_user: User = Depends(get_current_user)):
    """Get all brain profiles (defaults + user customizations)."""
    user_brains = await db.agent_brains.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).to_list(100)
    user_brain_map = {b["agent_id"]: b for b in user_brains}

    all_agents = await db.agents.find(
        {"$or": [{"is_custom": False}, {"creator_id": current_user.user_id}], "is_active": {"$ne": False}},
        {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1}
    ).to_list(100)

    profiles = []
    for agent in all_agents:
        aid = agent["agent_id"]
        brain = user_brain_map.get(aid, DEFAULT_BRAIN_PROFILES.get(aid, {}))
        profiles.append({
            "agent_id": aid,
            "agent_name": agent.get("name", ""),
            "agent_avatar": agent.get("avatar", ""),
            "agent_role": agent.get("role", ""),
            "is_custom": aid in user_brain_map,
            "autonomy_level": brain.get("autonomy_level", 3),
            "primary_model": brain.get("primary_model", {"provider": "openai", "model": "gpt-5.2"}),
            "memory_scopes": brain.get("memory_scopes", ["working"]),
            "approval_required": brain.get("approval_required", False),
            "communication_style": brain.get("communication_style", "Professional"),
            "kpis": brain.get("kpis", []),
        })
    return {"profiles": profiles}
