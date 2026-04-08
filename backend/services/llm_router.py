"""Model-Agnostic LLM Router — full 19-provider coverage.

Routes tasks to the optimal model based on:
- Task type & complexity classification (11 task types)
- Credit-budget awareness (micro / tight / normal / generous)
- Per-task preferred model tables (best model per task type)
- Cheapest-first fallback within each quality tier

Delegates to universal gateway's _smart_candidates() to avoid duplication.
"""
import logging
from datetime import datetime, timezone

from db import db
from services.llm_service import MODEL_COSTS_MAP, MODEL_CREDIT_COSTS

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# FULL 19-PROVIDER MODEL CAPABILITY TIERS
# ─────────────────────────────────────────────────────────────────────────────
# Ordered best-first within each tier. Every provider represented.

TIER_PREMIUM = [
    # ── Reasoning & depth ────────────────────────────────────────────────────
    {"provider": "openai",     "model": "gpt-5.2",                        "strengths": ["coding", "reasoning", "creative", "legal", "long_form"], "cost_tier": "high",   "speed": "medium"},
    {"provider": "anthropic",  "model": "claude-opus-4-6",                "strengths": ["reasoning", "creative", "legal", "long_form"],           "cost_tier": "high",   "speed": "medium"},
    {"provider": "anthropic",  "model": "claude-sonnet-4-6",              "strengths": ["reasoning", "creative", "legal", "coding"],               "cost_tier": "high",   "speed": "fast"},
    {"provider": "openai",     "model": "o4",                             "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "high",   "speed": "slow"},
    {"provider": "openai",     "model": "o3",                             "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "high",   "speed": "slow"},
    {"provider": "openai",     "model": "o4-mini",                        "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "medium", "speed": "medium"},
    {"provider": "openai",     "model": "o3-mini",                        "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "medium", "speed": "medium"},
    {"provider": "xai",        "model": "grok-3",                         "strengths": ["reasoning", "creative", "research"],                      "cost_tier": "high",   "speed": "medium"},
    {"provider": "perplexity", "model": "sonar-deep-research",            "strengths": ["research", "factual", "long_form"],                       "cost_tier": "medium", "speed": "slow"},
    {"provider": "perplexity", "model": "sonar-reasoning-pro",            "strengths": ["research", "reasoning"],                                  "cost_tier": "medium", "speed": "medium"},
    {"provider": "perplexity", "model": "sonar-pro",                      "strengths": ["research", "factual"],                                    "cost_tier": "medium", "speed": "fast"},
    {"provider": "nvidia",     "model": "nvidia/llama-3.1-nemotron-ultra-253b-v1", "strengths": ["reasoning", "coding", "long_form"],              "cost_tier": "medium", "speed": "medium"},
    {"provider": "together",   "model": "deepseek-ai/DeepSeek-R1",        "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "medium", "speed": "medium"},
    {"provider": "arcee",      "model": "arcee-maestro",                  "strengths": ["reasoning", "creative", "legal"],                         "cost_tier": "high",   "speed": "fast"},
]

TIER_STANDARD = [
    # ── Capable & balanced ───────────────────────────────────────────────────
    {"provider": "openai",     "model": "gpt-4.1",                        "strengths": ["coding", "reasoning", "data"],                            "cost_tier": "medium", "speed": "fast"},
    {"provider": "openai",     "model": "gpt-4o",                         "strengths": ["data", "coding", "multimodal", "vision"],                 "cost_tier": "medium", "speed": "fast"},
    {"provider": "anthropic",  "model": "claude-sonnet-4-5-20250929",     "strengths": ["reasoning", "creative", "legal"],                         "cost_tier": "medium", "speed": "fast"},
    {"provider": "gemini",     "model": "gemini-2.5-pro",                 "strengths": ["reasoning", "data", "coding", "vision"],                  "cost_tier": "medium", "speed": "fast"},
    {"provider": "gemini",     "model": "gemini-3-pro-preview",           "strengths": ["reasoning", "data", "creative"],                          "cost_tier": "medium", "speed": "fast"},
    {"provider": "deepseek",   "model": "deepseek-r1-0528",               "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "low",    "speed": "medium"},
    {"provider": "deepseek",   "model": "deepseek-reasoner",              "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "low",    "speed": "medium"},
    {"provider": "deepseek",   "model": "deepseek-v3-0324",               "strengths": ["coding", "data", "translation"],                          "cost_tier": "low",    "speed": "fast"},
    {"provider": "xai",        "model": "grok-2",                         "strengths": ["reasoning", "creative", "research"],                      "cost_tier": "medium", "speed": "fast"},
    {"provider": "mistral",    "model": "mistral-large-latest",           "strengths": ["creative", "reasoning", "legal"],                         "cost_tier": "medium", "speed": "fast"},
    {"provider": "mistral",    "model": "pixtral-large-latest",           "strengths": ["vision", "creative", "multimodal"],                       "cost_tier": "medium", "speed": "medium"},
    {"provider": "cohere",     "model": "command-a-03-2025",              "strengths": ["reasoning", "legal", "long_form"],                        "cost_tier": "medium", "speed": "medium"},
    {"provider": "cohere",     "model": "command-r-plus",                 "strengths": ["reasoning", "creative", "data"],                          "cost_tier": "medium", "speed": "fast"},
    {"provider": "perplexity", "model": "sonar-reasoning",                "strengths": ["research", "reasoning", "factual"],                       "cost_tier": "low",    "speed": "fast"},
    {"provider": "perplexity", "model": "sonar",                          "strengths": ["research", "factual", "quick"],                           "cost_tier": "low",    "speed": "fast"},
    {"provider": "ai21",       "model": "jamba-large-1.7",                "strengths": ["reasoning", "long_form", "data"],                         "cost_tier": "medium", "speed": "medium"},
    {"provider": "qwen",       "model": "qwen-max",                       "strengths": ["data", "reasoning", "translation", "coding"],             "cost_tier": "medium", "speed": "fast"},
    {"provider": "qwen",       "model": "qwen3-235b-a22b",                "strengths": ["reasoning", "coding", "translation"],                     "cost_tier": "low",    "speed": "fast"},
    {"provider": "moonshot",   "model": "moonshot-v1-128k",               "strengths": ["long_form", "research", "creative"],                      "cost_tier": "low",    "speed": "medium"},
    {"provider": "together",   "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "strengths": ["coding", "reasoning", "creative"],     "cost_tier": "low",    "speed": "fast"},
    {"provider": "together",   "model": "Qwen/Qwen3-235B-A22B-Instruct-FP8", "strengths": ["reasoning", "coding", "data"],                        "cost_tier": "low",    "speed": "fast"},
    {"provider": "sambanova",  "model": "DeepSeek-R1-0528",               "strengths": ["math", "reasoning", "coding"],                            "cost_tier": "low",    "speed": "fast"},
    {"provider": "fireworks",  "model": "accounts/fireworks/models/llama4-maverick-instruct-basic", "strengths": ["coding", "reasoning", "creative"], "cost_tier": "low", "speed": "very_fast"},
    {"provider": "fireworks",  "model": "accounts/fireworks/models/deepseek-v3", "strengths": ["coding", "data"],                                  "cost_tier": "low",    "speed": "fast"},
    {"provider": "novita",     "model": "qwen/qwen3-235b-a22b",           "strengths": ["coding", "reasoning", "data"],                            "cost_tier": "medium", "speed": "fast"},
    {"provider": "nvidia",     "model": "nvidia/llama-3.1-nemotron-70b-instruct", "strengths": ["reasoning", "coding"],                           "cost_tier": "low",    "speed": "fast"},
]

TIER_ECONOMY = [
    # ── Fast & cheap ─────────────────────────────────────────────────────────
    {"provider": "groq",       "model": "llama-3.1-8b-instant",           "strengths": ["quick", "simple", "translation"],                         "cost_tier": "low",    "speed": "ultra_fast"},
    {"provider": "cerebras",   "model": "llama3.1-8b",                    "strengths": ["quick", "simple", "chat"],                                "cost_tier": "low",    "speed": "ultra_fast"},
    {"provider": "gemini",     "model": "gemini-2.5-flash-lite",          "strengths": ["quick", "simple", "translation"],                         "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "gemini",     "model": "gemini-2.5-flash",               "strengths": ["quick", "data", "translation", "summary"],                "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "gemini",     "model": "gemini-3-flash-preview",         "strengths": ["quick", "creative", "data"],                              "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "groq",       "model": "gemma2-9b-it",                   "strengths": ["quick", "creative", "translation"],                       "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "mistral",    "model": "mistral-nemo",                   "strengths": ["quick", "translation", "creative"],                       "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "mistral",    "model": "mistral-small-latest",           "strengths": ["quick", "creative", "translation"],                       "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "mistral",    "model": "codestral-latest",               "strengths": ["coding", "quick"],                                        "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "deepseek",   "model": "deepseek-chat",                  "strengths": ["quick", "coding", "translation"],                         "cost_tier": "low",    "speed": "fast"},
    {"provider": "groq",       "model": "llama-4-scout-17b-16e-instruct", "strengths": ["quick", "coding", "chat"],                               "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "groq",       "model": "llama-4-maverick-17b-128e-instruct", "strengths": ["coding", "reasoning", "quick"],                      "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "groq",       "model": "qwen-qwq-32b",                   "strengths": ["math", "reasoning", "quick"],                             "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "openai",     "model": "gpt-4.1-nano",                   "strengths": ["quick", "summary", "translation"],                        "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "openai",     "model": "gpt-4o-mini",                    "strengths": ["quick", "simple", "chat"],                                "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "openai",     "model": "gpt-4.1-mini",                   "strengths": ["quick", "coding", "chat"],                                "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "anthropic",  "model": "claude-haiku-4-5-20251001",      "strengths": ["quick", "simple", "creative", "translation"],             "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "xai",        "model": "grok-3-mini",                    "strengths": ["quick", "chat", "summary"],                               "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "cohere",     "model": "command-r",                      "strengths": ["quick", "simple", "data"],                                "cost_tier": "low",    "speed": "fast"},
    {"provider": "ai21",       "model": "jamba-mini-1.7",                 "strengths": ["quick", "simple", "data"],                                "cost_tier": "low",    "speed": "fast"},
    {"provider": "cerebras",   "model": "llama-3.3-70b",                  "strengths": ["coding", "reasoning", "quick"],                           "cost_tier": "low",    "speed": "ultra_fast"},
    {"provider": "cerebras",   "model": "qwen-3-32b",                     "strengths": ["coding", "translation", "quick"],                         "cost_tier": "low",    "speed": "ultra_fast"},
    {"provider": "together",   "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "strengths": ["coding", "reasoning", "quick"],                 "cost_tier": "low",    "speed": "fast"},
    {"provider": "together",   "model": "Qwen/Qwen2.5-72B-Instruct-Turbo", "strengths": ["translation", "coding", "quick"],                       "cost_tier": "low",    "speed": "fast"},
    {"provider": "fireworks",  "model": "accounts/fireworks/models/llama4-scout-instruct-basic", "strengths": ["quick", "coding", "chat"],         "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "fireworks",  "model": "accounts/fireworks/models/qwen3-30b-a3b-instruct", "strengths": ["coding", "translation", "quick"],       "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "fireworks",  "model": "accounts/fireworks/models/phi-4", "strengths": ["coding", "reasoning", "quick"],                          "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "sambanova",  "model": "Meta-Llama-3.3-70B-Instruct",    "strengths": ["coding", "reasoning", "quick"],                           "cost_tier": "low",    "speed": "fast"},
    {"provider": "sambanova",  "model": "Qwen2.5-72B-Instruct",           "strengths": ["translation", "coding", "data"],                          "cost_tier": "low",    "speed": "fast"},
    {"provider": "nvidia",     "model": "meta/llama-3.3-70b-instruct",    "strengths": ["coding", "reasoning", "quick"],                           "cost_tier": "low",    "speed": "fast"},
    {"provider": "nvidia",     "model": "meta/llama-3.1-8b-instruct",     "strengths": ["quick", "simple", "chat"],                                "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "moonshot",   "model": "moonshot-v1-8k",                 "strengths": ["quick", "translation", "creative"],                       "cost_tier": "low",    "speed": "fast"},
    {"provider": "moonshot",   "model": "moonshot-v1-32k",                "strengths": ["creative", "research", "quick"],                          "cost_tier": "low",    "speed": "fast"},
    {"provider": "qwen",       "model": "qwen-turbo",                     "strengths": ["quick", "translation", "chat"],                           "cost_tier": "low",    "speed": "very_fast"},
    {"provider": "qwen",       "model": "qwen-plus",                      "strengths": ["translation", "coding", "quick"],                         "cost_tier": "low",    "speed": "fast"},
    {"provider": "qwen",       "model": "qwen2.5-72b-instruct",           "strengths": ["translation", "coding", "data"],                          "cost_tier": "low",    "speed": "fast"},
    {"provider": "novita",     "model": "meta-llama/llama-4-maverick",    "strengths": ["coding", "reasoning", "quick"],                           "cost_tier": "low",    "speed": "fast"},
    {"provider": "lambda",     "model": "hermes-3-405b",                   "strengths": ["coding", "reasoning", "quick"],                           "cost_tier": "low",    "speed": "fast"},
]

ALL_ROUTER_TIERS = {
    "premium":  TIER_PREMIUM,
    "standard": TIER_STANDARD,
    "economy":  TIER_ECONOMY,
}


def classify_task_complexity(content: str, agent_role: str = "") -> dict:
    """Classify a task into complexity tiers with full 11-type signal detection."""
    content_lower = content.lower()
    content_len = len(content)

    signals = {
        "coding":      sum(1 for kw in ["code", "function", "api", "debug", "python", "javascript", "typescript", "react", "database", "algorithm", "implement", "refactor", "deploy", "docker", "sql", "git", "script", "regex", "backend", "frontend"] if kw in content_lower),
        "math":        sum(1 for kw in ["calculate", "equation", "formula", "solve", "math", "integral", "derivative", "proof", "algebra", "matrix", "statistics", "probability", "factorial", "prime", "regression"] if kw in content_lower),
        "reasoning":   sum(1 for kw in ["analyze", "compare", "evaluate", "strategy", "decision", "complex", "why", "how does", "explain", "trade-off", "pros and cons", "because", "therefore", "hypothesis", "infer", "cause"] if kw in content_lower),
        "creative":    sum(1 for kw in ["write", "story", "creative", "blog", "article", "copy", "campaign", "brand", "engaging", "compelling", "narrative", "poem", "script", "headline", "tagline", "slogan", "marketing"] if kw in content_lower),
        "data":        sum(1 for kw in ["data", "analytics", "metrics", "chart", "statistics", "forecast", "visualization", "spreadsheet", "csv", "excel", "pandas", "dataframe", "pivot", "aggregate", "kpi"] if kw in content_lower),
        "legal":       sum(1 for kw in ["contract", "legal", "compliance", "regulation", "policy", "clause", "liability", "gdpr", "hipaa", "jurisdiction", "statute", "trademark", "copyright", "nda", "indemnify"] if kw in content_lower),
        "research":    sum(1 for kw in ["research", "comprehensive", "in-depth", "find information", "latest", "recent", "news", "fact check", "sources", "citations", "search for", "look up"] if kw in content_lower),
        "translation": sum(1 for kw in ["translate", "translation", "in french", "in spanish", "in german", "in arabic", "in chinese", "in japanese", "in hindi", "localize", "multilingual"] if kw in content_lower),
        "summary":     sum(1 for kw in ["summarize", "summary", "tldr", "brief", "key points", "condense", "highlights", "recap", "overview", "bullet points"] if kw in content_lower),
        "vision":      sum(1 for kw in ["image", "photo", "picture", "visual", "describe this", "identify", "recognize", "ocr", "diagram", "screenshot", "in the picture"] if kw in content_lower),
        "quick":       sum(1 for kw in ["quick", "simple", "brief", "yes or no", "define", "hello", "hi ", "hey ", "thanks", "how are you", "one sentence"] if kw in content_lower),
    }

    # Agent role boosts
    role_lower = agent_role.lower()
    if any(r in role_lower for r in ["developer", "engineer", "technical"]):
        signals["coding"] += 3
    if any(r in role_lower for r in ["copywriter", "marketing", "social media", "content"]):
        signals["creative"] += 3
    if any(r in role_lower for r in ["analyst", "strategist", "research", "financial"]):
        signals["reasoning"] += 2; signals["data"] += 2
    if any(r in role_lower for r in ["legal", "compliance"]):
        signals["legal"] += 3; signals["reasoning"] += 1
    if any(r in role_lower for r in ["translator", "localiz"]):
        signals["translation"] += 3
    if any(r in role_lower for r in ["designer", "illustrator", "visual"]):
        signals["vision"] += 3

    primary_type = max(signals, key=signals.get) if max(signals.values()) > 0 else "quick"
    max_score = signals[primary_type]
    words = len(content.split())

    # Tier determination
    if max_score <= 1 or words < 10:
        tier = "economy"; complexity = "simple"
    elif max_score <= 3 or words < 100:
        tier = "standard"; complexity = "moderate"
    else:
        tier = "premium"; complexity = "complex"

    # Hard overrides for high-stakes
    if signals["legal"] >= 2 or signals["coding"] >= 4 or signals["math"] >= 3:
        tier = "premium"; complexity = "complex"
    if signals["research"] >= 2 or signals["vision"] >= 2:
        tier = "premium"; complexity = "complex"

    return {
        "tier": tier, "complexity": complexity,
        "primary_type": primary_type, "signals": signals,
        "content_length": content_len,
    }


async def route_to_model(content: str, agent_role: str, user_id: str) -> dict:
    """Route a task to the optimal model across all 33 providers.
    Respects user-saved quality_tier and task_hint preferences.
    Delegates candidate selection to universal gateway's smart router."""
    from routes.universal import _smart_candidates, _credit_budget

    # Load user preference
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )

    if config:
        saved_q = config.get("quality_tier", "auto")
        quality_override = saved_q if saved_q not in ("", "auto") else None
        if config.get("routing") not in ("auto", None, "") and config.get("provider") and config.get("model"):
            return {
                "provider": config["provider"],
                "model": config["model"],
                "routing_method": "user_preference",
                "reason": f"User-selected: {config['provider']}/{config['model']}",
                "complexity": None,
            }
    else:
        quality_override = None

    # Get user credit balance for budget-aware routing
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0, "credits": 1})
    credits = (user_doc or {}).get("credits", 50)

    candidates, task_info = _smart_candidates(content, credits, quality_override)
    best_provider, best_model = candidates[0] if candidates else ("openai", "gpt-5.2")

    cost_info = MODEL_COSTS_MAP.get(best_model, {})
    credit_cost = MODEL_CREDIT_COSTS.get(best_model.split("/")[-1], 2)

    try:
        await db.routing_logs.insert_one({
            "user_id": user_id,
            "provider": best_provider,
            "model": best_model,
            "tier": task_info["type"],
            "primary_type": task_info["type"],
            "complexity": task_info["complexity"],
            "credit_cost": credit_cost,
            "routing_method": "smart_universal",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass

    return {
        "provider": best_provider,
        "model": best_model,
        "routing_method": "smart_universal",
        "reason": f"{best_model} selected — {task_info['type']} task ({task_info['complexity']} complexity)",
        "complexity": task_info,
        "credit_cost": credit_cost,
    }


async def get_routing_stats(user_id: str) -> dict:
    """Get model routing statistics for a user."""
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$model", "count": {"$sum": 1}, "provider": {"$first": "$provider"}}},
        {"$sort": {"count": -1}},
    ]
    model_usage = await db.routing_logs.aggregate(pipeline).to_list(20)

    complexity_dist = {
        c["_id"]: c["count"]
        for c in await db.routing_logs.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$tier", "count": {"$sum": 1}}},
        ]).to_list(10)
    }
    type_dist = {
        t["_id"]: t["count"]
        for t in await db.routing_logs.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$primary_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(10)
    }
    cost_agg = await db.routing_logs.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total_credits": {"$sum": "$credit_cost"}, "total_calls": {"$sum": 1}}},
    ]).to_list(1)

    return {
        "model_usage": [{"model": m["_id"], "provider": m.get("provider", ""), "count": m["count"]} for m in model_usage],
        "complexity_distribution": complexity_dist,
        "task_type_distribution": type_dist,
        "total_routed_calls": cost_agg[0]["total_calls"] if cost_agg else 0,
        "total_credits_used": cost_agg[0]["total_credits"] if cost_agg else 0,
    }
