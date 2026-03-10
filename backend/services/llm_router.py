"""Model-Agnostic LLM Router.

Intelligently routes tasks to optimal LLM models based on:
- Task complexity analysis
- Cost optimization
- Latency requirements
- User preferences
"""
import logging
from datetime import datetime, timezone

from db import db
from services.llm_service import MODEL_COSTS_MAP, MODEL_CREDIT_COSTS, auto_select_model

logger = logging.getLogger(__name__)

# Model capability tiers
TIER_PREMIUM = [
    {"provider": "openai", "model": "gpt-5.2", "strengths": ["coding", "reasoning", "creative", "long_form"], "cost_tier": "high", "speed": "medium"},
    {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "strengths": ["reasoning", "creative", "legal", "long_form"], "cost_tier": "high", "speed": "medium"},
    {"provider": "gemini", "model": "gemini-2.5-pro", "strengths": ["reasoning", "data", "coding"], "cost_tier": "medium", "speed": "fast"},
    {"provider": "ai21", "model": "jamba-large-1.7", "strengths": ["reasoning", "long_form", "data"], "cost_tier": "medium", "speed": "medium"},
    {"provider": "together", "model": "deepseek-ai/DeepSeek-R1", "strengths": ["reasoning", "coding"], "cost_tier": "medium", "speed": "medium"},
]

TIER_STANDARD = [
    {"provider": "openai", "model": "gpt-4o", "strengths": ["data", "coding", "multimodal"], "cost_tier": "medium", "speed": "fast"},
    {"provider": "openai", "model": "gpt-4.1", "strengths": ["coding", "reasoning"], "cost_tier": "medium", "speed": "fast"},
    {"provider": "gemini", "model": "gemini-3-flash-preview", "strengths": ["quick", "creative", "data"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "together", "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "strengths": ["coding", "reasoning"], "cost_tier": "low", "speed": "fast"},
    {"provider": "fireworks", "model": "accounts/fireworks/models/llama4-maverick-instruct-basic", "strengths": ["coding", "reasoning", "creative"], "cost_tier": "low", "speed": "very_fast"},
]

TIER_ECONOMY = [
    {"provider": "openai", "model": "gpt-4o-mini", "strengths": ["quick", "simple"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "gemini", "model": "gemini-2.5-flash", "strengths": ["quick", "simple", "data"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "strengths": ["quick", "simple", "creative"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "groq", "model": "llama-4-scout-17b-16e-instruct", "strengths": ["quick", "coding", "creative"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "ai21", "model": "jamba-mini-1.7", "strengths": ["quick", "simple", "data"], "cost_tier": "low", "speed": "fast"},
]


def classify_task_complexity(content: str, agent_role: str = "") -> dict:
    """Classify a task into complexity tiers with detailed analysis."""
    content_lower = content.lower()
    content_len = len(content)

    # Complexity signals
    signals = {
        "coding": sum(1 for kw in ["code", "function", "api", "debug", "python", "javascript", "react", "database", "algorithm", "implement", "refactor", "deploy"] if kw in content_lower),
        "reasoning": sum(1 for kw in ["analyze", "compare", "evaluate", "strategy", "decision", "complex", "calculate", "problem", "solve", "why", "how does"] if kw in content_lower),
        "creative": sum(1 for kw in ["write", "story", "creative", "blog", "article", "copy", "campaign", "brand", "engaging", "compelling", "narrative"] if kw in content_lower),
        "data": sum(1 for kw in ["data", "analytics", "metrics", "chart", "statistics", "forecast", "visualization", "spreadsheet"] if kw in content_lower),
        "legal": sum(1 for kw in ["contract", "legal", "compliance", "regulation", "policy", "clause", "liability"] if kw in content_lower),
        "quick": sum(1 for kw in ["quick", "simple", "brief", "summarize", "list", "yes or no", "define", "translate", "hello", "hi"] if kw in content_lower),
    }

    # Agent role boost
    role_lower = agent_role.lower()
    if any(r in role_lower for r in ["developer", "engineer", "technical"]):
        signals["coding"] += 3
    if any(r in role_lower for r in ["copywriter", "marketing", "social media", "content"]):
        signals["creative"] += 3
    if any(r in role_lower for r in ["analyst", "strategist", "research", "financial"]):
        signals["reasoning"] += 2
    if any(r in role_lower for r in ["legal", "compliance"]):
        signals["legal"] += 3

    primary_type = max(signals, key=signals.get)
    max_score = signals[primary_type]

    # Determine complexity tier
    if max_score <= 1 or content_len < 80:
        tier = "economy"
        complexity = "simple"
    elif max_score <= 3 or content_len < 300:
        tier = "standard"
        complexity = "moderate"
    else:
        tier = "premium"
        complexity = "complex"

    # Override for specific high-stakes tasks
    if signals["legal"] >= 2 or signals["coding"] >= 4:
        tier = "premium"
        complexity = "complex"

    return {
        "tier": tier,
        "complexity": complexity,
        "primary_type": primary_type,
        "signals": signals,
        "content_length": content_len,
    }


async def route_to_model(content: str, agent_role: str, user_id: str) -> dict:
    """Route a task to the optimal LLM model.
    Checks user preference first, then auto-selects if set to 'auto'."""

    # Check user preference
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )

    user_routing = "auto"
    user_provider = None
    user_model = None
    if config:
        user_routing = config.get("routing", "auto")
        user_provider = config.get("provider")
        user_model = config.get("model")

    # If user has a fixed preference and routing is not auto, use it
    if user_routing != "auto" and user_provider and user_model:
        return {
            "provider": user_provider,
            "model": user_model,
            "routing_method": "user_preference",
            "reason": f"User-selected: {user_provider}/{user_model}",
            "complexity": None,
        }

    # Auto-routing
    classification = classify_task_complexity(content, agent_role)
    tier = classification["tier"]
    primary_type = classification["primary_type"]

    # Select best model for the task type from the appropriate tier
    if tier == "premium":
        candidates = TIER_PREMIUM
    elif tier == "standard":
        candidates = TIER_STANDARD
    else:
        candidates = TIER_ECONOMY

    # Score candidates by how well they match the task type
    best = candidates[0]
    best_score = 0
    for c in candidates:
        score = 1 if primary_type in c["strengths"] else 0
        if score > best_score:
            best = c
            best_score = score

    cost_info = MODEL_COSTS_MAP.get(best["model"], {})
    credit_cost = MODEL_CREDIT_COSTS.get(best["model"], 2)

    # Log routing decision
    try:
        await db.routing_logs.insert_one({
            "user_id": user_id,
            "provider": best["provider"],
            "model": best["model"],
            "tier": tier,
            "primary_type": primary_type,
            "complexity": classification["complexity"],
            "credit_cost": credit_cost,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass

    return {
        "provider": best["provider"],
        "model": best["model"],
        "routing_method": "auto_router",
        "reason": f"{best['model']} selected - optimal for {primary_type} tasks ({classification['complexity']} complexity)",
        "complexity": classification,
        "cost_per_million_input": cost_info.get("input", 0),
        "credit_cost": credit_cost,
    }


async def get_routing_stats(user_id: str) -> dict:
    """Get model routing statistics for a user."""
    # Model usage distribution
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$model", "count": {"$sum": 1}, "provider": {"$first": "$provider"}}},
        {"$sort": {"count": -1}}
    ]
    model_usage = await db.routing_logs.aggregate(pipeline).to_list(20)

    # Complexity distribution
    complexity_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$tier", "count": {"$sum": 1}}},
    ]
    complexity_dist = await db.routing_logs.aggregate(complexity_pipeline).to_list(10)

    # Task type distribution
    type_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$primary_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    type_dist = await db.routing_logs.aggregate(type_pipeline).to_list(10)

    # Total cost estimate
    cost_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total_credits": {"$sum": "$credit_cost"}, "total_calls": {"$sum": 1}}}
    ]
    cost_agg = await db.routing_logs.aggregate(cost_pipeline).to_list(1)

    return {
        "model_usage": [{"model": m["_id"], "provider": m.get("provider", ""), "count": m["count"]} for m in model_usage],
        "complexity_distribution": {c["_id"]: c["count"] for c in complexity_dist},
        "task_type_distribution": {t["_id"]: t["count"] for t in type_dist},
        "total_routed_calls": cost_agg[0]["total_calls"] if cost_agg else 0,
        "total_credits_used": cost_agg[0]["total_credits"] if cost_agg else 0,
    }
