"""Collaboration Engine, KPI Framework, Cost Governance, and System Controls API."""
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone
import uuid
from db import db
from auth import get_current_user
from models.schemas import User

router = APIRouter()
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


# ============== COLLABORATION ENGINE ==============

@router.post("/collaborations")
async def create_collaboration(request: Request, current_user: User = Depends(get_current_user)):
    """Create an inter-agent collaboration message."""
    data = await request.json()
    collab = {
        "collab_id": f"collab_{uuid.uuid4().hex[:12]}",
        "user_id": current_user.user_id,
        "task_id": data.get("task_id", ""),
        "project_id": data.get("project_id", ""),
        "sender": data.get("sender", ""),
        "receivers": data.get("receivers", []),
        "objective": data.get("objective", ""),
        "context": data.get("context", ""),
        "required_output": data.get("required_output", ""),
        "deadline": data.get("deadline", ""),
        "risk_level": data.get("risk_level", "low"),
        "dependencies": data.get("dependencies", []),
        "approval_required": data.get("approval_required", False),
        "status": "pending",
        "response": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.collaborations.insert_one(collab)
    collab.pop("_id", None)
    return collab


@router.get("/collaborations")
async def list_collaborations(
    project_id: str = None, status: str = None,
    page: int = 1, limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """List collaboration messages with optional filters."""
    query = {"user_id": current_user.user_id}
    if project_id:
        query["project_id"] = project_id
    if status:
        query["status"] = status

    total = await db.collaborations.count_documents(query)
    items = await db.collaborations.find(query, {"_id": 0}).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(limit)
    return {"items": items, "total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)}


@router.put("/collaborations/{collab_id}")
async def update_collaboration(collab_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Update a collaboration status or response."""
    data = await request.json()
    update = {"updated_at": datetime.now(timezone.utc).isoformat()}
    for field in ["status", "response", "risk_level"]:
        if field in data:
            update[field] = data[field]

    result = await db.collaborations.find_one_and_update(
        {"collab_id": collab_id, "user_id": current_user.user_id},
        {"$set": update}, return_document=True, projection={"_id": 0}
    )
    if not result:
        raise HTTPException(404, "Collaboration not found")
    return result


# ============== KPI FRAMEWORK ==============

@router.get("/kpis")
async def get_kpis(current_user: User = Depends(get_current_user)):
    """Get the KPI dashboard for the current user."""
    user_id = current_user.user_id

    # Aggregate KPIs from various sources
    total_projects = await db.projects.count_documents({"user_id": user_id})
    completed_projects = await db.projects.count_documents({"user_id": user_id, "status": "completed"})
    total_tasks = await db.tasks.count_documents({"user_id": user_id})
    completed_tasks = await db.tasks.count_documents({"user_id": user_id, "status": "completed"})
    total_chats = await db.chats.count_documents({"user_id": user_id})
    total_collabs = await db.collaborations.count_documents({"user_id": user_id})
    total_approvals = await db.approvals.count_documents({"user_id": user_id})
    pending_approvals = await db.approvals.count_documents({"user_id": user_id, "status": "pending"})
    total_tool_calls = await db.tool_calls.count_documents({"user_id": user_id})

    # Usage/cost from transactions
    pipeline = [
        {"$match": {"user_id": user_id, "type": "usage"}},
        {"$group": {"_id": None, "total_cost": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    usage_agg = await db.transactions.aggregate(pipeline).to_list(1)
    total_ai_cost = abs(usage_agg[0]["total_cost"]) if usage_agg else 0
    total_ai_calls = usage_agg[0]["count"] if usage_agg else 0

    # Risk incidents (from tool_calls with errors)
    risk_incidents = await db.tool_calls.count_documents({"user_id": user_id, "status": "error"})

    # Custom KPIs stored by user
    custom_kpis = await db.kpi_store.find({"user_id": user_id}, {"_id": 0}).to_list(50)

    return {
        "operational": {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "project_completion_rate": round(completed_projects / max(total_projects, 1) * 100, 1),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "task_completion_rate": round(completed_tasks / max(total_tasks, 1) * 100, 1),
            "total_chats": total_chats,
            "total_collaborations": total_collabs,
        },
        "governance": {
            "total_approvals": total_approvals,
            "pending_approvals": pending_approvals,
            "total_tool_calls": total_tool_calls,
            "risk_incidents": risk_incidents,
        },
        "cost": {
            "total_ai_cost": round(total_ai_cost, 2),
            "total_ai_calls": total_ai_calls,
            "avg_cost_per_call": round(total_ai_cost / max(total_ai_calls, 1), 4),
        },
        "custom_kpis": custom_kpis,
    }


@router.post("/kpis/custom")
async def add_custom_kpi(request: Request, current_user: User = Depends(get_current_user)):
    """Add a custom KPI metric."""
    data = await request.json()
    kpi = {
        "kpi_id": f"kpi_{uuid.uuid4().hex[:8]}",
        "user_id": current_user.user_id,
        "name": data.get("name", ""),
        "value": data.get("value", 0),
        "target": data.get("target", 0),
        "unit": data.get("unit", ""),
        "category": data.get("category", "business"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.kpi_store.insert_one(kpi)
    kpi.pop("_id", None)
    return kpi


@router.put("/kpis/custom/{kpi_id}")
async def update_custom_kpi(kpi_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Update a custom KPI."""
    data = await request.json()
    update = {"updated_at": datetime.now(timezone.utc).isoformat()}
    for field in ["name", "value", "target", "unit", "category"]:
        if field in data:
            update[field] = data[field]
    result = await db.kpi_store.find_one_and_update(
        {"kpi_id": kpi_id, "user_id": current_user.user_id},
        {"$set": update}, return_document=True, projection={"_id": 0}
    )
    if not result:
        raise HTTPException(404, "KPI not found")
    return result


# ============== SYSTEM MODE (Simulation vs Execution) ==============

@router.get("/system/mode")
async def get_system_mode(current_user: User = Depends(get_current_user)):
    """Get the current system mode (simulation or execution)."""
    config = await db.system_config.find_one(
        {"user_id": current_user.user_id}, {"_id": 0}
    )
    if not config:
        return {"mode": "simulation", "description": "Simulation mode — no real API calls"}
    return {"mode": config.get("mode", "simulation"), "description": config.get("description", "")}


@router.put("/system/mode")
async def set_system_mode(request: Request, current_user: User = Depends(get_current_user)):
    """Toggle between simulation and execution mode."""
    data = await request.json()
    mode = data.get("mode", "simulation")
    if mode not in ("simulation", "execution"):
        raise HTTPException(400, "Mode must be 'simulation' or 'execution'")

    descriptions = {
        "simulation": "Simulation mode — no real API calls, safe for testing",
        "execution": "Execution mode — live API calls, real-world actions enabled"
    }
    await db.system_config.update_one(
        {"user_id": current_user.user_id},
        {"$set": {
            "user_id": current_user.user_id,
            "mode": mode,
            "description": descriptions[mode],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"mode": mode, "description": descriptions[mode]}


# ============== QUALITY CONTROL ==============

@router.post("/quality-review")
async def create_quality_review(request: Request, current_user: User = Depends(get_current_user)):
    """Submit an output for quality review (self-check + peer review)."""
    data = await request.json()
    review = {
        "review_id": f"qc_{uuid.uuid4().hex[:10]}",
        "user_id": current_user.user_id,
        "project_id": data.get("project_id", ""),
        "task_id": data.get("task_id", ""),
        "agent_id": data.get("agent_id", ""),
        "content": data.get("content", ""),
        "review_type": data.get("review_type", "self_check"),
        "reviewer_agent": data.get("reviewer_agent", ""),
        "score": None,
        "feedback": None,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.quality_reviews.insert_one(review)
    review.pop("_id", None)
    return review


@router.get("/quality-reviews")
async def list_quality_reviews(
    project_id: str = None, status: str = None,
    page: int = 1, limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """List quality reviews."""
    query = {"user_id": current_user.user_id}
    if project_id:
        query["project_id"] = project_id
    if status:
        query["status"] = status
    total = await db.quality_reviews.count_documents(query)
    items = await db.quality_reviews.find(query, {"_id": 0}).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(limit)
    return {"items": items, "total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)}


# ============== COST GOVERNANCE ==============

@router.get("/cost-governance")
async def get_cost_governance(current_user: User = Depends(get_current_user)):
    """Get cost governance dashboard with per-agent cost breakdowns."""
    user_id = current_user.user_id

    # Per-agent cost breakdown
    pipeline = [
        {"$match": {"user_id": user_id, "type": "usage"}},
        {"$group": {"_id": "$agent_name", "total_cost": {"$sum": {"$abs": "$amount"}}, "call_count": {"$sum": 1}}},
        {"$sort": {"total_cost": -1}}
    ]
    agent_costs = await db.transactions.aggregate(pipeline).to_list(50)

    # Budget config
    budget = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "budget"}, {"_id": 0}
    )

    return {
        "agent_costs": [{"agent": c["_id"] or "Unknown", "total_cost": round(c["total_cost"], 2), "call_count": c["call_count"]} for c in agent_costs],
        "budget": budget or {"monthly_cap": None, "alert_threshold": None},
    }


@router.put("/cost-governance/budget")
async def set_budget(request: Request, current_user: User = Depends(get_current_user)):
    """Set cost governance budget caps."""
    data = await request.json()
    await db.system_config.update_one(
        {"user_id": current_user.user_id, "config_type": "budget"},
        {"$set": {
            "user_id": current_user.user_id,
            "config_type": "budget",
            "monthly_cap": data.get("monthly_cap"),
            "alert_threshold": data.get("alert_threshold"),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"success": True}



# ============== AGENT ACTIVITY MONITOR ==============

@router.get("/activity/live")
async def get_live_activity(current_user: User = Depends(get_current_user)):
    """Get real-time agent activity data for the activity monitor."""
    user_id = current_user.user_id

    # Active projects (in_progress)
    active_projects = await db.projects.find(
        {"user_id": user_id, "status": "in_progress"}, {"_id": 0, "project_id": 1, "title": 1, "goal": 1, "status": 1}
    ).to_list(10)

    # Recent tasks (last 50)
    recent_tasks = await db.tasks.find(
        {"user_id": user_id}, {"_id": 0, "task_id": 1, "title": 1, "status": 1, "agent_name": 1, "agent_role": 1, "project_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).limit(50).to_list(50)

    # Recent collaborations (last 30)
    recent_collabs = await db.collaborations.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(30)

    # Recent tool calls (last 30)
    recent_tools = await db.tool_calls.find(
        {"user_id": user_id}, {"_id": 0, "tool_name": 1, "agent_name": 1, "status": 1, "timestamp": 1, "parameters": 1}
    ).sort("timestamp", -1).limit(30).to_list(30)

    # Agent activity summary
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$agent_name", "task_count": {"$sum": 1}, "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}, "latest": {"$max": "$updated_at"}}},
        {"$sort": {"task_count": -1}}
    ]
    agent_activity = await db.tasks.aggregate(pipeline).to_list(50)

    # Build communication flow data (edges between agents)
    comm_flows = []
    seen_flows = set()
    for c in recent_collabs:
        sender = c.get("sender", "")
        for r in c.get("receivers", []):
            key = f"{sender}->{r}"
            if key not in seen_flows:
                seen_flows.add(key)
                comm_flows.append({"from": sender, "to": r, "objective": c.get("objective", "")[:80], "status": c.get("status", "pending")})

    # Build task dependency graph
    dependencies = []
    for t in recent_tasks:
        if t.get("project_id"):
            dependencies.append({
                "task_id": t.get("task_id", ""),
                "title": t.get("title", "")[:60],
                "agent": t.get("agent_name", ""),
                "status": t.get("status", ""),
                "project_id": t.get("project_id", ""),
            })

    return {
        "active_projects": active_projects,
        "agent_activity": [{"agent": a["_id"] or "Unknown", "task_count": a["task_count"], "completed": a["completed"], "latest": a.get("latest", "")} for a in agent_activity],
        "communication_flows": comm_flows,
        "task_graph": dependencies[:30],
        "recent_tool_calls": recent_tools[:15],
        "recent_collabs": recent_collabs[:10],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============== UNIVERSAL REFERENCE INTELLIGENCE ==============

async def _get_user_llm_config(user_id: str):
    """Get user's preferred LLM provider and model, with fallback to defaults."""
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )
    if config:
        return config.get("provider", "openai"), config.get("model", "gpt-5.2")
    return "openai", "gpt-5.2"


@router.get("/llm/config")
async def get_llm_config(current_user: User = Depends(get_current_user)):
    """Get the user's LLM provider/model preference."""
    provider, model = await _get_user_llm_config(current_user.user_id)
    return {
        "provider": provider,
        "model": model,
        "available_providers": [
            {"id": "openai", "name": "OpenAI", "models": ["gpt-5.2", "gpt-5.1", "gpt-4.1", "gpt-4o", "o3", "o4-mini"]},
            {"id": "anthropic", "name": "Anthropic", "models": ["claude-sonnet-4-5-20250929", "claude-4-sonnet-20250514", "claude-haiku-4-5-20251001"]},
            {"id": "gemini", "name": "Google Gemini", "models": ["gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash"]},
            {"id": "xai", "name": "xAI (Grok)", "models": ["grok-3", "grok-3-mini", "grok-2"]},
            {"id": "deepseek", "name": "DeepSeek", "models": ["deepseek-chat", "deepseek-reasoner"]},
            {"id": "mistral", "name": "Mistral AI", "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]},
            {"id": "perplexity", "name": "Perplexity", "models": ["sonar-pro", "sonar"]},
            {"id": "cohere", "name": "Cohere", "models": ["command-r-plus", "command-r"]},
            {"id": "groq", "name": "Groq (Llama 4)", "models": ["llama-4-scout-17b-16e-instruct", "llama-4-maverick-17b-128e-instruct", "llama-3.3-70b-versatile"]},
            {"id": "together", "name": "Together AI", "models": ["meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1"]},
            {"id": "fireworks", "name": "Fireworks AI", "models": ["accounts/fireworks/models/llama4-scout-instruct-basic", "accounts/fireworks/models/llama4-maverick-instruct-basic", "accounts/fireworks/models/deepseek-v3"]},
            {"id": "ai21", "name": "AI21 (Jamba)", "models": ["jamba-large-1.7", "jamba-mini-1.7"]},
        ]
    }


@router.put("/llm/config")
async def set_llm_config(request: Request, current_user: User = Depends(get_current_user)):
    """Set the user's preferred LLM provider/model."""
    data = await request.json()
    provider = data.get("provider", "openai")
    model = data.get("model", "gpt-5.2")
    await db.system_config.update_one(
        {"user_id": current_user.user_id, "config_type": "llm_preference"},
        {"$set": {
            "user_id": current_user.user_id,
            "config_type": "llm_preference",
            "provider": provider,
            "model": model,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    return {"provider": provider, "model": model}


@router.post("/reference/analyze")
async def analyze_reference(request: Request, current_user: User = Depends(get_current_user)):
    """Analyze an image or text reference to extract style, tone, brand elements."""
    import os
    data = await request.json()
    ref_type = data.get("type", "text")
    content = data.get("content", "")
    image_url = data.get("image_url", "")

    EMERGENT_KEY_VAL = os.environ.get("EMERGENT_LLM_KEY", "") or EMERGENT_KEY
    provider, model = await _get_user_llm_config(current_user.user_id)

    if ref_type == "image" and image_url:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_KEY_VAL,
                session_id=f"ref_analyze_{uuid.uuid4().hex[:8]}",
                system_message="You are a brand and visual intelligence analyst. Analyze the image and extract: 1) Brand/product identification (if recognizable), 2) Visual style elements (colors, typography, composition), 3) Emotional tone and mood, 4) Target audience impression, 5) Key design patterns. Return structured JSON."
            ).with_model(provider, model)

            analysis = await chat.send_message(UserMessage(text=f"Analyze this image: {image_url}\n\nProvide a structured analysis including brand detection, visual style, tone, and key elements. Return as clear sections."))

            result = {
                "ref_id": f"ref_{uuid.uuid4().hex[:8]}",
                "type": "image",
                "source": image_url,
                "analysis": analysis,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.reference_analyses.insert_one({**result, "user_id": current_user.user_id})
            result.pop("_id", None)
            return result
        except Exception as e:
            raise HTTPException(500, f"Image analysis failed: {str(e)[:200]}")

    elif ref_type == "text" and content:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_KEY_VAL,
                session_id=f"ref_text_{uuid.uuid4().hex[:8]}",
                system_message="You are a brand and content intelligence analyst. Analyze the text reference to extract: 1) Writing style and tone, 2) Target audience, 3) Key messaging patterns, 4) Brand voice characteristics, 5) Structural elements. Create a Style Blueprint that can guide content creation."
            ).with_model(provider, model)

            analysis = await chat.send_message(UserMessage(text=f"Analyze this reference content and create a Style Blueprint:\n\n{content[:3000]}"))

            result = {
                "ref_id": f"ref_{uuid.uuid4().hex[:8]}",
                "type": "text",
                "source": content[:500],
                "analysis": analysis,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.reference_analyses.insert_one({**result, "user_id": current_user.user_id})
            result.pop("_id", None)
            return result
        except Exception as e:
            raise HTTPException(500, f"Text analysis failed: {str(e)[:200]}")
    else:
        raise HTTPException(400, "Provide image_url (for image type) or content (for text type)")


@router.get("/reference/history")
async def get_reference_history(current_user: User = Depends(get_current_user)):
    """Get history of reference analyses."""
    items = await db.reference_analyses.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    return {"items": items}


# ============== QUALITY CONTROL & FAILURE RECOVERY ==============

@router.get("/quality/dashboard")
async def quality_dashboard(current_user: User = Depends(get_current_user)):
    """Get quality metrics: pass rates, scores, escalations, recovery stats."""
    from services.quality_service import get_quality_dashboard
    return await get_quality_dashboard(current_user.user_id)


@router.post("/quality/review")
async def trigger_quality_review(request: Request, current_user: User = Depends(get_current_user)):
    """Trigger a quality review on a specific task."""
    data = await request.json()
    task_id = data.get("task_id", "")
    if not task_id:
        raise HTTPException(400, "task_id is required")

    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(404, "Task not found")
    if not task.get("result"):
        raise HTTPException(400, "Task has no result to review")

    from services.quality_service import critic_review
    review = await critic_review(
        task_result=task["result"],
        task_description=task.get("description", ""),
        agent_name=task.get("agent_name", "Agent"),
        user_id=current_user.user_id,
        project_id=task.get("project_id", ""),
        task_id=task_id,
        api_keys={"emergent": EMERGENT_KEY},
    )
    return review


@router.post("/quality/retry")
async def retry_failed_task(request: Request, current_user: User = Depends(get_current_user)):
    """Retry a failed task with fallback model chain."""
    data = await request.json()
    task_id = data.get("task_id", "")
    if not task_id:
        raise HTTPException(400, "task_id is required")

    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(404, "Task not found")

    from services.quality_service import retry_with_fallback
    result = await retry_with_fallback(
        task_id=task_id,
        user_id=current_user.user_id,
        project_id=task.get("project_id", ""),
        original_error=task.get("result", "Unknown error"),
        api_keys={"emergent": EMERGENT_KEY},
    )
    return result


# ============== LLM ROUTER ==============

@router.get("/router/stats")
async def get_router_stats(current_user: User = Depends(get_current_user)):
    """Get LLM routing statistics: model usage, complexity distribution, cost."""
    from services.llm_router import get_routing_stats
    return await get_routing_stats(current_user.user_id)


@router.post("/router/analyze")
async def analyze_task_routing(request: Request, current_user: User = Depends(get_current_user)):
    """Analyze what model would be selected for a given task (dry run)."""
    data = await request.json()
    content = data.get("content", "")
    agent_role = data.get("agent_role", "")
    if not content:
        raise HTTPException(400, "content is required")

    from services.llm_router import route_to_model, classify_task_complexity
    routing = await route_to_model(content, agent_role, current_user.user_id)
    classification = classify_task_complexity(content, agent_role)
    return {**routing, "classification": classification}
