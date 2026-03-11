"""MAARS — Governance: Autonomy Tier Enforcement."""

from db import db

TIERS = {
    0: {"name": "Advisory Only", "allowed_actions": ["analyze", "recommend"], "requires_approval": True, "max_spend": 0},
    1: {"name": "Research & Draft", "allowed_actions": ["analyze", "recommend", "research", "draft", "simulate"], "requires_approval": True, "max_spend": 1.0},
    2: {"name": "Sandbox Execution", "allowed_actions": ["analyze", "recommend", "research", "draft", "simulate", "execute_sandbox"], "requires_approval": False, "max_spend": 5.0},
    3: {"name": "Production (Narrow)", "allowed_actions": ["analyze", "recommend", "research", "draft", "simulate", "execute_sandbox", "execute_production"], "requires_approval": False, "max_spend": 20.0},
    4: {"name": "Multi-step Workflows", "allowed_actions": ["analyze", "recommend", "research", "draft", "simulate", "execute_sandbox", "execute_production", "coordinate_workflow"], "requires_approval": True, "max_spend": 50.0},
    5: {"name": "System Changes (Propose)", "allowed_actions": ["analyze", "recommend", "research", "draft", "simulate", "execute_sandbox", "execute_production", "coordinate_workflow", "propose_system_change"], "requires_approval": True, "max_spend": 100.0},
}


def get_tier_info(tier: int):
    """Get tier details."""
    return TIERS.get(tier, TIERS[0])


def check_action_allowed(tier: int, action: str):
    """Check if an action is allowed at a given autonomy tier."""
    info = get_tier_info(tier)
    allowed = action in info["allowed_actions"]
    return {
        "allowed": allowed,
        "tier": tier,
        "tier_name": info["name"],
        "action": action,
        "requires_approval": info["requires_approval"],
        "reason": f"Action '{action}' {'is' if allowed else 'is NOT'} permitted at tier {tier} ({info['name']})",
    }


async def get_agent_autonomy(agent_id: str):
    """Get an agent's current autonomy tier and permissions."""
    agent = await db["agents"].find_one({"agent_id": agent_id}, {"_id": 0, "agent_id": 1, "name": 1, "autonomy_tier": 1})
    if not agent:
        return {"error": "agent_not_found"}
    tier = agent.get("autonomy_tier", 0)
    info = get_tier_info(tier)
    return {**agent, "tier_info": info}


async def set_agent_autonomy(agent_id: str, tier: int):
    """Set an agent's autonomy tier."""
    if tier not in TIERS:
        return {"error": f"Invalid tier. Must be 0-5"}
    await db["agents"].update_one({"agent_id": agent_id}, {"$set": {"autonomy_tier": tier}})
    return {"agent_id": agent_id, "autonomy_tier": tier, "tier_info": get_tier_info(tier)}


def get_all_tiers():
    """Get all tier definitions."""
    return {k: v for k, v in TIERS.items()}
