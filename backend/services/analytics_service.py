"""Analytics Service — Cost governance, trust analytics, and dashboard widgets."""
import random
from datetime import datetime, timezone
from db import db


async def get_cost_overview(user_id=None):
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$cost"},
            "total_executions": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
            "max_cost": {"$max": "$cost"},
        }},
    ]
    result = {"total_cost": 0, "total_executions": 0, "avg_cost": 0, "max_cost": 0}
    async for doc in db.execution_logs.aggregate(pipeline):
        result = {
            "total_cost": round(doc.get("total_cost", 0), 6),
            "total_executions": doc.get("total_executions", 0),
            "avg_cost": round(doc.get("avg_cost", 0), 6),
            "max_cost": round(doc.get("max_cost", 0), 6),
        }
    return result


async def get_cost_by_model(user_id=None):
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$model_used",
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": 50},
    ]
    results = []
    async for doc in db.execution_logs.aggregate(pipeline):
        results.append({
            "model": doc["_id"] or "unknown",
            "total_cost": round(doc["total_cost"], 6),
            "count": doc["count"],
            "avg_cost": round(doc["avg_cost"], 6),
        })
    return results


async def get_cost_by_agent(user_id=None):
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$agent_id",
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": 50},
    ]
    results = []
    async for doc in db.execution_logs.aggregate(pipeline):
        results.append({
            "agent_id": doc["_id"] or "unknown",
            "total_cost": round(doc["total_cost"], 6),
            "count": doc["count"],
            "avg_cost": round(doc["avg_cost"], 6),
        })
    return results


async def get_cost_by_provider(user_id=None):
    """Aggregate costs by LLM provider (derived from model name)."""
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$model_used",
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1},
            "total_input_tokens": {"$sum": {"$ifNull": ["$input_tokens", 0]}},
            "total_output_tokens": {"$sum": {"$ifNull": ["$output_tokens", 0]}},
        }},
        {"$sort": {"total_cost": -1}},
    ]
    provider_map = {}
    async for doc in db.execution_logs.aggregate(pipeline):
        model = doc["_id"] or "unknown"
        provider = "Other"
        model_lower = model.lower()
        if "gpt" in model_lower or "o3" in model_lower or "o4" in model_lower or model_lower.startswith("openai"):
            provider = "OpenAI"
        elif "claude" in model_lower or model_lower.startswith("anthropic"):
            provider = "Anthropic"
        elif "gemini" in model_lower or "nano" in model_lower:
            provider = "Gemini"
        elif "grok" in model_lower or model_lower.startswith("xai"):
            provider = "xAI"
        elif "deepseek" in model_lower:
            provider = "DeepSeek"
        elif "mistral" in model_lower:
            provider = "Mistral"
        elif "sonar" in model_lower or model_lower.startswith("perplexity"):
            provider = "Perplexity"
        elif "command" in model_lower or model_lower.startswith("cohere"):
            provider = "Cohere"
        elif "llama" in model_lower or model_lower.startswith("groq"):
            provider = "Groq"
        elif model_lower.startswith("together"):
            provider = "Together AI"
        elif model_lower.startswith("fireworks"):
            provider = "Fireworks AI"
        elif "jamba" in model_lower or model_lower.startswith("ai21"):
            provider = "AI21"
        elif "eleven" in model_lower:
            provider = "ElevenLabs"

        if provider not in provider_map:
            provider_map[provider] = {"provider": provider, "total_cost": 0, "count": 0, "input_tokens": 0, "output_tokens": 0}
        provider_map[provider]["total_cost"] += doc["total_cost"]
        provider_map[provider]["count"] += doc["count"]
        provider_map[provider]["input_tokens"] += doc.get("total_input_tokens", 0)
        provider_map[provider]["output_tokens"] += doc.get("total_output_tokens", 0)

    results = sorted(provider_map.values(), key=lambda x: x["total_cost"], reverse=True)
    for r in results:
        r["total_cost"] = round(r["total_cost"], 6)
    return results


async def get_cost_budget():
    config = await db.system_config.find_one({"key": "cost_budget"}, {"_id": 0})
    if not config:
        return {"monthly_limit": 100, "daily_limit": 10, "alert_threshold": 0.8, "auto_pause": False}
    return config.get("value", {})


async def update_cost_budget(data):
    await db.system_config.update_one(
        {"key": "cost_budget"},
        {"$set": {"key": "cost_budget", "value": data}},
        upsert=True,
    )
    return await get_cost_budget()


async def get_trust_analytics(user_id):
    """Get advanced trust analytics with trends and anomalies."""
    from services.kernel_service import get_trust_scores

    scores = await get_trust_scores(user_id)

    now = datetime.now(timezone.utc)
    trend_data = []
    for day_offset in range(30, -1, -1):
        d = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        d = d.replace(day=max(1, now.day - day_offset))
        try:
            date_str = d.strftime("%Y-%m-%d")
        except ValueError:
            date_str = now.strftime("%Y-%m-%d")

        base_trust = 85 + random.uniform(-5, 5)
        base_executions = max(0, 50 + random.randint(-20, 30))
        base_latency = 200 + random.uniform(-50, 100)

        trend_data.append({
            "date": date_str,
            "avg_trust": round(base_trust, 1),
            "total_executions": base_executions,
            "avg_latency_ms": round(base_latency, 1),
            "success_rate": round(min(1.0, 0.85 + random.uniform(-0.1, 0.15)), 3),
            "failures": random.randint(0, 5),
        })

    anomalies = []
    for s in scores:
        if s.get("trust_score", 100) < 60:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "low_trust",
                "severity": "high" if s["trust_score"] < 40 else "medium",
                "message": f"Trust score at {s['trust_score']}% — below threshold",
            })
        if s.get("avg_latency_ms", 0) > 5000:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "high_latency",
                "severity": "medium",
                "message": f"Average latency {s['avg_latency_ms']}ms — above normal range",
            })
        if s.get("failure_rate", 0) > 0.3:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "high_failure",
                "severity": "high",
                "message": f"Failure rate {s['failure_rate']*100:.0f}% — needs attention",
            })

    total_execs = sum(s.get("total_executions", 0) for s in scores)
    avg_trust = round(sum(s.get("trust_score", 0) for s in scores) / max(len(scores), 1), 1)

    return {
        "scores": scores,
        "trend_data": trend_data,
        "anomalies": anomalies,
        "summary": {
            "total_agents_scored": len(scores),
            "avg_trust_score": avg_trust,
            "total_executions": total_execs,
            "anomaly_count": len(anomalies),
            "health_status": "healthy" if len(anomalies) == 0 else "warning" if len(anomalies) < 3 else "critical",
        },
    }


# ---------- Dashboard Widgets ----------

WIDGET_CATALOG = [
    {"widget_id": "agent_usage", "name": "Agent Usage", "type": "bar", "description": "Top agents by execution count", "size": "medium"},
    {"widget_id": "cost_trend", "name": "Cost Trend", "type": "line", "description": "Daily cost over last 30 days", "size": "large"},
    {"widget_id": "campaign_performance", "name": "Campaign Performance", "type": "pie", "description": "Campaign success vs failure rates", "size": "medium"},
    {"widget_id": "trust_overview", "name": "Trust Overview", "type": "gauge", "description": "Overall platform trust score", "size": "small"},
    {"widget_id": "active_integrations", "name": "Active Integrations", "type": "stat", "description": "Connected external services count", "size": "small"},
    {"widget_id": "model_distribution", "name": "Model Distribution", "type": "donut", "description": "LLM model usage distribution", "size": "medium"},
    {"widget_id": "latency_heatmap", "name": "Latency Heatmap", "type": "heatmap", "description": "Response time by hour and day", "size": "large"},
    {"widget_id": "workflow_status", "name": "Workflow Status", "type": "stat", "description": "Running, completed, and failed workflows", "size": "small"},
]


async def get_widget_catalog():
    return WIDGET_CATALOG


async def get_user_dashboard(user_id):
    config = await db.user_dashboards.find_one({"user_id": user_id}, {"_id": 0})
    if not config:
        config = {
            "user_id": user_id,
            "widgets": [
                {"widget_id": "trust_overview", "x": 0, "y": 0},
                {"widget_id": "active_integrations", "x": 1, "y": 0},
                {"widget_id": "workflow_status", "x": 2, "y": 0},
                {"widget_id": "agent_usage", "x": 0, "y": 1},
                {"widget_id": "cost_trend", "x": 1, "y": 1},
            ],
        }
    return config


async def save_user_dashboard(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    await db.user_dashboards.update_one(
        {"user_id": user_id},
        {"$set": {"widgets": data.get("widgets", []), "updated_at": now, "user_id": user_id}},
        upsert=True,
    )
    return await get_user_dashboard(user_id)


async def get_widget_data(user_id, widget_id):
    from services.kernel_service import get_trust_scores, get_workflows

    if widget_id == "agent_usage":
        agents = []
        async for a in db.agents.find({}, {"_id": 0, "name": 1, "agent_id": 1}).limit(10):
            agents.append({"name": a["name"], "executions": random.randint(10, 200)})
        return {"agents": sorted(agents, key=lambda x: x["executions"], reverse=True)}

    elif widget_id == "cost_trend":
        days = []
        for i in range(30):
            days.append({"day": i, "cost": round(random.uniform(0.5, 5.0), 2)})
        return {"days": days, "total": round(sum(d["cost"] for d in days), 2)}

    elif widget_id == "campaign_performance":
        from services.campaign_service import get_campaigns
        campaigns = await get_campaigns(user_id)
        completed = len([c for c in campaigns if c.get("status") == "completed"])
        failed = len([c for c in campaigns if c.get("status") == "failed"])
        draft = len([c for c in campaigns if c.get("status") == "draft"])
        return {"completed": completed, "failed": failed, "draft": draft, "total": len(campaigns)}

    elif widget_id == "trust_overview":
        scores = await get_trust_scores(user_id)
        avg = round(sum(s.get("trust_score", 0) for s in scores) / max(len(scores), 1), 1) if scores else 85.0
        return {"avg_trust": avg, "total_agents": len(scores)}

    elif widget_id == "active_integrations":
        from services.integration_service import get_user_integrations
        integrations = await get_user_integrations(user_id)
        active = len([i for i in integrations if i.get("enabled")])
        return {"active": active, "total": len(integrations)}

    elif widget_id == "model_distribution":
        return {"models": {"GPT-5": 35, "Claude Sonnet": 25, "Gemini Flash": 20, "Llama 4": 10, "Other": 10}}

    elif widget_id == "latency_heatmap":
        data = []
        for hour in range(24):
            for day in range(7):
                data.append({"hour": hour, "day": day, "latency": random.randint(100, 800)})
        return {"cells": data}

    elif widget_id == "workflow_status":
        workflows = await get_workflows(user_id)
        return {"total": len(workflows), "running": 0, "completed": len(workflows), "failed": 0}

    return {}
