"""MAARS — Model Router.
Classifies tasks, selects optimal models based on task type, difficulty,
risk, speed, cost sensitivity, and tracks performance for learning."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

ROUTING_LOG = "model_routing_log"
MODEL_PERF = "model_performance"

# Provider catalog with model capabilities and pricing tiers
PROVIDER_CATALOG = {
    "openai": {
        "gpt-5.2": {"tier": "flagship", "strengths": ["reasoning", "coding", "analysis"], "cost_per_1k_in": 0.01, "cost_per_1k_out": 0.03, "latency": "medium"},
        "gpt-4o": {"tier": "balanced", "strengths": ["general", "multimodal", "speed"], "cost_per_1k_in": 0.005, "cost_per_1k_out": 0.015, "latency": "fast"},
        "gpt-4o-mini": {"tier": "economy", "strengths": ["general", "speed"], "cost_per_1k_in": 0.00015, "cost_per_1k_out": 0.0006, "latency": "fast"},
        "o3": {"tier": "reasoning", "strengths": ["deep_reasoning", "math", "logic"], "cost_per_1k_in": 0.01, "cost_per_1k_out": 0.04, "latency": "slow"},
    },
    "anthropic": {
        "claude-sonnet-4.5": {"tier": "flagship", "strengths": ["safety", "reasoning", "coding", "analysis"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
        "claude-opus-4.5": {"tier": "premium", "strengths": ["deep_reasoning", "safety", "nuance"], "cost_per_1k_in": 0.015, "cost_per_1k_out": 0.075, "latency": "slow"},
        "claude-haiku-4.5": {"tier": "economy", "strengths": ["speed", "general"], "cost_per_1k_in": 0.0008, "cost_per_1k_out": 0.004, "latency": "fast"},
    },
    "google": {
        "gemini-3-flash": {"tier": "economy", "strengths": ["speed", "general", "multimodal"], "cost_per_1k_in": 0.0001, "cost_per_1k_out": 0.0004, "latency": "fast"},
        "gemini-3-pro": {"tier": "balanced", "strengths": ["reasoning", "multimodal", "analysis"], "cost_per_1k_in": 0.00125, "cost_per_1k_out": 0.005, "latency": "medium"},
    },
    "groq": {
        "llama-4-scout": {"tier": "economy", "strengths": ["speed", "general"], "cost_per_1k_in": 0.00011, "cost_per_1k_out": 0.00034, "latency": "ultra_fast"},
    },
    "deepseek": {
        "deepseek-v3": {"tier": "economy", "strengths": ["coding", "reasoning"], "cost_per_1k_in": 0.00027, "cost_per_1k_out": 0.0011, "latency": "fast"},
    },
    "xai": {
        "grok-3": {"tier": "flagship", "strengths": ["reasoning", "long_context", "analysis"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
    },
    "perplexity": {
        "sonar-pro": {"tier": "balanced", "strengths": ["search", "grounded_answers", "citations"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
    },
}

# Task class → model preference mapping
TASK_ROUTING_RULES = {
    "coding": {"preferred_strengths": ["coding", "reasoning"], "preferred_tier": "flagship", "fallback_tier": "balanced"},
    "architecture": {"preferred_strengths": ["deep_reasoning", "coding"], "preferred_tier": "flagship", "fallback_tier": "balanced"},
    "research": {"preferred_strengths": ["search", "grounded_answers", "analysis"], "preferred_tier": "balanced", "fallback_tier": "economy"},
    "legal_compliance": {"preferred_strengths": ["safety", "reasoning", "nuance"], "preferred_tier": "flagship", "fallback_tier": "balanced"},
    "math_forecasting": {"preferred_strengths": ["deep_reasoning", "math", "logic"], "preferred_tier": "reasoning", "fallback_tier": "flagship"},
    "summary": {"preferred_strengths": ["speed", "general"], "preferred_tier": "economy", "fallback_tier": "economy"},
    "creative": {"preferred_strengths": ["general", "nuance"], "preferred_tier": "balanced", "fallback_tier": "economy"},
    "real_time": {"preferred_strengths": ["speed"], "preferred_tier": "economy", "fallback_tier": "economy"},
    "general": {"preferred_strengths": ["general", "reasoning"], "preferred_tier": "balanced", "fallback_tier": "economy"},
}


def classify_task(task_description: str, metadata: dict = None):
    """Classify a task into type, difficulty, risk level, and requirements."""
    metadata = metadata or {}
    desc_lower = task_description.lower()

    # Task type detection
    task_type = "general"
    if any(w in desc_lower for w in ["code", "implement", "debug", "program", "function", "api", "deploy"]):
        task_type = "coding"
    elif any(w in desc_lower for w in ["architect", "design system", "infrastructure"]):
        task_type = "architecture"
    elif any(w in desc_lower for w in ["research", "analyze", "investigate", "market", "competitor"]):
        task_type = "research"
    elif any(w in desc_lower for w in ["legal", "compliance", "regulation", "policy", "contract"]):
        task_type = "legal_compliance"
    elif any(w in desc_lower for w in ["forecast", "calculate", "financial", "math", "quantitative"]):
        task_type = "math_forecasting"
    elif any(w in desc_lower for w in ["summarize", "brief", "tldr", "overview"]):
        task_type = "summary"
    elif any(w in desc_lower for w in ["creative", "write", "story", "brand", "campaign", "content"]):
        task_type = "creative"

    # Override with explicit metadata
    task_type = metadata.get("task_type", task_type)
    difficulty = metadata.get("difficulty", "medium")
    risk_level = metadata.get("risk_level", "medium")
    speed_req = metadata.get("speed_requirement", "normal")
    cost_sensitivity = metadata.get("cost_sensitivity", "moderate")

    return {
        "task_type": task_type,
        "difficulty": difficulty,
        "risk_level": risk_level,
        "speed_requirement": speed_req,
        "cost_sensitivity": cost_sensitivity,
    }


def select_model(classification: dict):
    """Select the best model based on task classification. Returns {provider, model, reason, expected_cost}."""
    task_type = classification.get("task_type", "general")
    cost_sensitivity = classification.get("cost_sensitivity", "moderate")
    speed_req = classification.get("speed_requirement", "normal")

    rules = TASK_ROUTING_RULES.get(task_type, TASK_ROUTING_RULES["general"])
    preferred_strengths = set(rules["preferred_strengths"])
    preferred_tier = rules["preferred_tier"]

    # If cost-sensitive, downgrade tier
    if cost_sensitivity == "high":
        preferred_tier = "economy"
    # If speed is critical, prefer fast models
    speed_filter = None
    if speed_req == "critical":
        speed_filter = {"ultra_fast", "fast"}

    best = None
    best_score = -1

    for provider, models in PROVIDER_CATALOG.items():
        for model_name, info in models.items():
            score = 0
            model_strengths = set(info["strengths"])
            overlap = len(preferred_strengths & model_strengths)
            score += overlap * 10

            if info["tier"] == preferred_tier:
                score += 5
            elif info["tier"] == rules.get("fallback_tier"):
                score += 2

            if speed_filter and info["latency"] not in speed_filter:
                score -= 10

            if cost_sensitivity == "high":
                score -= int(info["cost_per_1k_out"] * 1000)

            if score > best_score:
                best_score = score
                best = {
                    "provider": provider,
                    "model": model_name,
                    "tier": info["tier"],
                    "reason": f"Best match for {task_type}: {', '.join(preferred_strengths & model_strengths)} (tier={info['tier']})",
                    "expected_cost_per_1k_in": info["cost_per_1k_in"],
                    "expected_cost_per_1k_out": info["cost_per_1k_out"],
                    "latency_class": info["latency"],
                }

    return best


async def route_task(task_description: str, metadata: dict = None):
    """Full routing pipeline: classify → select → log → return."""
    classification = classify_task(task_description, metadata)
    selection = select_model(classification)

    log_entry = {
        "task_description": task_description[:200],
        "classification": classification,
        "selection": selection,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[ROUTING_LOG].insert_one(log_entry)
    await log_action(
        "model_routed", "system", "model_router",
        details={"task_type": classification["task_type"], "model": selection["model"], "provider": selection["provider"]},
    )

    return {"classification": classification, "selection": selection}


async def log_model_result(
    provider: str, model: str, task_type: str,
    success: bool, cost: float, latency_ms: int,
    verification_passed: bool = None, hallucination: bool = False,
):
    """Log model execution result for performance tracking."""
    await db[MODEL_PERF].update_one(
        {"provider": provider, "model_name": model, "task_class": task_type},
        {
            "$inc": {
                "total_calls": 1,
                "success_count": 1 if success else 0,
                "total_cost": cost,
                "total_latency": latency_ms,
                **({"verification_passes": 1} if verification_passed else {}),
                **({"hallucination_count": 1} if hallucination else {}),
            },
            "$set": {"last_updated": datetime.now(timezone.utc).isoformat()},
        },
        upsert=True,
    )


async def get_model_performance(provider: str = None):
    """Get model performance stats."""
    query = {}
    if provider:
        query["provider"] = provider
    cursor = db[MODEL_PERF].find(query, {"_id": 0})
    results = await cursor.to_list(length=100)
    for r in results:
        calls = r.get("total_calls", 1)
        r["avg_cost"] = round(r.get("total_cost", 0) / max(calls, 1), 4)
        r["avg_latency"] = round(r.get("total_latency", 0) / max(calls, 1))
        r["success_rate"] = round(r.get("success_count", 0) / max(calls, 1), 3)
        r["verification_pass_rate"] = round(r.get("verification_passes", 0) / max(calls, 1), 3)
    return results
