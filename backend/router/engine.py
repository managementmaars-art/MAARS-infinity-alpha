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
        "gpt-5.2": {"tier": "flagship", "strengths": ["reasoning", "coding", "analysis", "search"], "cost_per_1k_in": 0.01, "cost_per_1k_out": 0.03, "latency": "medium"},
        "gpt-4o": {"tier": "balanced", "strengths": ["general", "multimodal", "speed"], "cost_per_1k_in": 0.005, "cost_per_1k_out": 0.015, "latency": "fast"},
        "gpt-4o-mini": {"tier": "economy", "strengths": ["general", "speed"], "cost_per_1k_in": 0.00015, "cost_per_1k_out": 0.0006, "latency": "fast"},
        "o3": {"tier": "reasoning", "strengths": ["deep_reasoning", "math", "logic"], "cost_per_1k_in": 0.01, "cost_per_1k_out": 0.04, "latency": "slow"},
        "o4-mini": {"tier": "reasoning_economy", "strengths": ["deep_reasoning", "math", "speed"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.012, "latency": "medium"},
    },
    "anthropic": {
        "claude-sonnet-4-6": {"tier": "flagship", "strengths": ["safety", "reasoning", "coding", "analysis", "nuance"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
        "claude-opus-4-6": {"tier": "premium", "strengths": ["deep_reasoning", "safety", "nuance", "long_context"], "cost_per_1k_in": 0.015, "cost_per_1k_out": 0.075, "latency": "slow"},
        "claude-haiku-4-5": {"tier": "economy", "strengths": ["speed", "general", "summarization"], "cost_per_1k_in": 0.0008, "cost_per_1k_out": 0.004, "latency": "ultra_fast"},
    },
    "google": {
        "gemini-2.5-flash": {"tier": "economy", "strengths": ["speed", "general", "multimodal", "search"], "cost_per_1k_in": 0.0001, "cost_per_1k_out": 0.0004, "latency": "ultra_fast"},
        "gemini-2.5-pro": {"tier": "balanced", "strengths": ["reasoning", "multimodal", "analysis", "grounded_answers", "long_context"], "cost_per_1k_in": 0.00125, "cost_per_1k_out": 0.005, "latency": "medium"},
    },
    "deepseek": {
        "deepseek-r1": {"tier": "reasoning", "strengths": ["deep_reasoning", "math", "coding", "logic"], "cost_per_1k_in": 0.00055, "cost_per_1k_out": 0.00219, "latency": "medium"},
        "deepseek-v3": {"tier": "flagship", "strengths": ["coding", "analysis", "reasoning", "general"], "cost_per_1k_in": 0.00027, "cost_per_1k_out": 0.0011, "latency": "fast"},
        "deepseek-chat": {"tier": "economy", "strengths": ["general", "speed"], "cost_per_1k_in": 0.00014, "cost_per_1k_out": 0.00028, "latency": "fast"},
    },
    "mistral": {
        "mistral-large": {"tier": "balanced", "strengths": ["reasoning", "coding", "multilingual", "analysis"], "cost_per_1k_in": 0.002, "cost_per_1k_out": 0.006, "latency": "fast"},
        "mistral-medium": {"tier": "economy", "strengths": ["general", "speed", "multilingual"], "cost_per_1k_in": 0.0027, "cost_per_1k_out": 0.0081, "latency": "fast"},
        "codestral": {"tier": "balanced", "strengths": ["coding", "code_completion", "technical"], "cost_per_1k_in": 0.001, "cost_per_1k_out": 0.003, "latency": "fast"},
    },
    "groq": {
        "llama-4-maverick": {"tier": "balanced", "strengths": ["speed", "general", "reasoning"], "cost_per_1k_in": 0.0002, "cost_per_1k_out": 0.0006, "latency": "ultra_fast"},
        "llama-4-scout": {"tier": "economy", "strengths": ["speed", "general"], "cost_per_1k_in": 0.00011, "cost_per_1k_out": 0.00034, "latency": "ultra_fast"},
        "mixtral-8x7b": {"tier": "balanced", "strengths": ["general", "speed", "multilingual"], "cost_per_1k_in": 0.00024, "cost_per_1k_out": 0.00024, "latency": "ultra_fast"},
    },
    "xai": {
        "grok-3": {"tier": "flagship", "strengths": ["reasoning", "analysis", "real_time", "humor"], "cost_per_1k_in": 0.005, "cost_per_1k_out": 0.015, "latency": "medium"},
        "grok-3-mini": {"tier": "economy", "strengths": ["speed", "general", "real_time"], "cost_per_1k_in": 0.0003, "cost_per_1k_out": 0.0005, "latency": "fast"},
    },
    "perplexity": {
        "sonar-pro": {"tier": "balanced", "strengths": ["search", "real_time", "grounded_answers", "research"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
        "sonar": {"tier": "economy", "strengths": ["search", "real_time", "grounded_answers"], "cost_per_1k_in": 0.001, "cost_per_1k_out": 0.001, "latency": "fast"},
    },
    "cohere": {
        "command-r-plus": {"tier": "balanced", "strengths": ["rag", "analysis", "business", "multilingual"], "cost_per_1k_in": 0.003, "cost_per_1k_out": 0.015, "latency": "medium"},
        "command-r": {"tier": "economy", "strengths": ["rag", "general", "speed"], "cost_per_1k_in": 0.00015, "cost_per_1k_out": 0.0006, "latency": "fast"},
    },
    "together": {
        "qwen2.5-72b-instruct": {"tier": "balanced", "strengths": ["coding", "multilingual", "general", "reasoning"], "cost_per_1k_in": 0.0012, "cost_per_1k_out": 0.0012, "latency": "fast"},
        "meta-llama-3.1-405b": {"tier": "premium", "strengths": ["reasoning", "coding", "general", "long_context"], "cost_per_1k_in": 0.0035, "cost_per_1k_out": 0.0035, "latency": "medium"},
    },
}

# Providers available via Emergent LLM key
AVAILABLE_PROVIDERS = {"openai", "anthropic", "google", "deepseek", "mistral", "groq", "xai", "perplexity", "cohere", "together"}

# Task class → model preference mapping
TASK_ROUTING_RULES = {
    "coding":           {"preferred_strengths": ["coding", "reasoning"],                        "preferred_tier": "flagship",          "fallback_tier": "balanced"},
    "architecture":     {"preferred_strengths": ["deep_reasoning", "coding"],                   "preferred_tier": "flagship",          "fallback_tier": "balanced"},
    "research":         {"preferred_strengths": ["search", "grounded_answers", "analysis"],     "preferred_tier": "balanced",          "fallback_tier": "economy"},
    "legal_compliance": {"preferred_strengths": ["safety", "reasoning", "nuance"],              "preferred_tier": "flagship",          "fallback_tier": "balanced"},
    "math_forecasting": {"preferred_strengths": ["deep_reasoning", "math", "logic"],            "preferred_tier": "reasoning",         "fallback_tier": "flagship"},
    "summary":          {"preferred_strengths": ["summarization", "speed", "general"],          "preferred_tier": "economy",           "fallback_tier": "economy"},
    "creative":         {"preferred_strengths": ["general", "nuance"],                          "preferred_tier": "balanced",          "fallback_tier": "economy"},
    "real_time":        {"preferred_strengths": ["real_time", "search", "speed"],               "preferred_tier": "economy",           "fallback_tier": "economy"},
    "general":          {"preferred_strengths": ["general", "reasoning"],                       "preferred_tier": "balanced",          "fallback_tier": "economy"},
    "data_analysis":    {"preferred_strengths": ["analysis", "reasoning", "coding"],            "preferred_tier": "balanced",          "fallback_tier": "flagship"},
    "translation":      {"preferred_strengths": ["multilingual", "general"],                    "preferred_tier": "economy",           "fallback_tier": "balanced"},
    "long_context":     {"preferred_strengths": ["long_context", "analysis"],                   "preferred_tier": "premium",           "fallback_tier": "flagship"},
    "rag_retrieval":    {"preferred_strengths": ["rag", "analysis", "grounded_answers"],        "preferred_tier": "balanced",          "fallback_tier": "economy"},
    "sales_marketing":  {"preferred_strengths": ["general", "nuance", "reasoning"],             "preferred_tier": "balanced",          "fallback_tier": "economy"},
    "security":         {"preferred_strengths": ["safety", "reasoning", "coding"],              "preferred_tier": "flagship",          "fallback_tier": "balanced"},
    "ultra_fast":       {"preferred_strengths": ["speed", "general"],                           "preferred_tier": "economy",           "fallback_tier": "economy"},
}


def classify_task(task_description: str, metadata: dict = None):
    """Classify a task into type, difficulty, risk level, and requirements."""
    metadata = metadata or {}
    desc_lower = task_description.lower()

    # Task type detection (ordered by specificity — most specific first)
    task_type = "general"
    if any(w in desc_lower for w in ["translate", "translation", "localiz", "multilingual", "language"]):
        task_type = "translation"
    elif any(w in desc_lower for w in ["security", "vulnerability", "pentest", "exploit", "audit security", "threat"]):
        task_type = "security"
    elif any(w in desc_lower for w in ["architect", "design system", "infrastructure", "microservice", "scalab"]):
        task_type = "architecture"
    elif any(w in desc_lower for w in ["code", "implement", "debug", "program", "function", "api", "deploy", "refactor"]):
        task_type = "coding"
    elif any(w in desc_lower for w in ["sql", "pandas", "data pipeline", "etl", "dashboard", "csv", "dataset", "analytics"]):
        task_type = "data_analysis"
    elif any(w in desc_lower for w in ["legal", "compliance", "regulation", "policy", "contract", "gdpr", "privacy law"]):
        task_type = "legal_compliance"
    elif any(w in desc_lower for w in ["forecast", "calculate", "financial model", "math", "quantitative", "statistical", "regression"]):
        task_type = "math_forecasting"
    elif any(w in desc_lower for w in ["research", "analyze", "investigate", "market research", "competitor", "industry report"]):
        task_type = "research"
    elif any(w in desc_lower for w in ["real-time", "latest news", "current", "today", "live data", "stock price"]):
        task_type = "real_time"
    elif any(w in desc_lower for w in ["summarize", "brief", "tldr", "overview", "condense"]):
        task_type = "summary"
    elif any(w in desc_lower for w in ["long document", "full book", "entire codebase", "extensive context"]):
        task_type = "long_context"
    elif any(w in desc_lower for w in ["marketing", "sales pitch", "campaign", "ad copy", "brand voice", "copywrite"]):
        task_type = "sales_marketing"
    elif any(w in desc_lower for w in ["creative", "write story", "fiction", "poem", "narrative"]):
        task_type = "creative"
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
        if provider not in AVAILABLE_PROVIDERS:
            continue
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



async def execute_routed_task(task_description: str, context: str = "", metadata: dict = None):
    """Full pipeline: route → call LLM → log result → return output."""
    import time as _time
    from services.infinity_llm import call

    routing = await route_task(task_description, metadata)
    model_name = routing["selection"]["model"]
    provider = routing["selection"]["provider"]
    task_type = routing["classification"]["task_type"]

    system_msg = f"You are an expert AI agent specialized in {task_type} tasks. Execute the task precisely and provide a thorough response."

    prompt = task_description
    if context:
        prompt = f"Context:\n{context}\n\nTask:\n{task_description}"

    start = _time.time()
    try:
        llm_result = await call(prompt, system_msg, model_name)
        latency_ms = int((_time.time() - start) * 1000)
        cost_info = routing["selection"]
        estimated_cost = cost_info.get("expected_cost_per_1k_out", 0) * 2

        await log_model_result(
            llm_result["provider"], llm_result["model"], task_type,
            success=True, cost=estimated_cost, latency_ms=latency_ms,
        )

        return {
            "output": llm_result["response"],
            "routing": routing,
            "execution": {
                "provider": llm_result["provider"],
                "model": llm_result["model"],
                "latency_ms": latency_ms,
                "estimated_cost": estimated_cost,
                "attempt": llm_result.get("attempt", 1),
            },
        }
    except Exception as e:
        latency_ms = int((_time.time() - start) * 1000)
        await log_model_result(provider, model_name, task_type, success=False, cost=0, latency_ms=latency_ms)
        raise RuntimeError(f"Task execution failed: {e}")
