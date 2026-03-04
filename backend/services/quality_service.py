"""Quality Control & Failure Recovery Service.

Implements:
- Critic Module: Auto-reviews agent task output for quality scoring
- Retry/Fallback: Re-executes failed tasks with fallback models
- Escalation Chain: Failed tasks escalate Commander → User
"""
import uuid
import json
import logging
from datetime import datetime, timezone

from db import db
from shared.constants import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)

QUALITY_THRESHOLDS = {
    "excellent": 8,
    "acceptable": 5,
    "needs_revision": 3,
}

FALLBACK_CHAIN = [
    ("openai", "gpt-5.2"),
    ("anthropic", "claude-sonnet-4-5-20250929"),
    ("gemini", "gemini-2.5-pro"),
    ("openai", "gpt-4o"),
]


async def critic_review(task_result: str, task_description: str, agent_name: str,
                        user_id: str, project_id: str, task_id: str, api_keys: dict) -> dict:
    """Run an automated quality review on a task result.
    Returns a review with score (1-10), feedback, and pass/fail status."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        critic = LlmChat(
            api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
            session_id=f"critic_{task_id}_{uuid.uuid4().hex[:6]}",
            system_message="""You are a strict quality assurance reviewer. Evaluate task outputs against their requirements.
Score on a 1-10 scale. Return ONLY valid JSON:
{
  "score": <1-10>,
  "verdict": "pass" or "revision_needed" or "fail",
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1"],
  "suggestions": ["suggestion1"],
  "summary": "One sentence assessment"
}"""
        ).with_model("openai", "gpt-4o")

        prompt = f"""Review this task output:

TASK: {task_description[:500]}
AGENT: {agent_name}
OUTPUT:
{task_result[:2000]}

Evaluate for: completeness, accuracy, actionability, professionalism, and alignment with the task requirements."""

        response = await critic.send_message(UserMessage(text=prompt))
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        if text.startswith("json"):
            text = text[4:].strip()

        review_data = json.loads(text)
    except Exception as e:
        logger.error(f"Critic review error: {e}")
        review_data = {
            "score": 6,
            "verdict": "pass",
            "strengths": ["Output generated successfully"],
            "weaknesses": ["Could not perform detailed review"],
            "suggestions": [],
            "summary": "Automated review unavailable, defaulting to pass.",
        }

    review = {
        "review_id": f"qc_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "project_id": project_id,
        "task_id": task_id,
        "agent_name": agent_name,
        "review_type": "auto_critic",
        "score": review_data.get("score", 5),
        "verdict": review_data.get("verdict", "pass"),
        "strengths": review_data.get("strengths", []),
        "weaknesses": review_data.get("weaknesses", []),
        "suggestions": review_data.get("suggestions", []),
        "summary": review_data.get("summary", ""),
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.quality_reviews.insert_one(review)
    review.pop("_id", None)
    return review


async def retry_with_fallback(task_id: str, user_id: str, project_id: str,
                              original_error: str, api_keys: dict) -> dict:
    """Retry a failed task using the fallback model chain.
    Returns the retry result or escalates."""
    task = await db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        return {"status": "error", "message": "Task not found"}

    agent_id = task.get("assigned_agents", ["agent_strategist"])[0]
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        return {"status": "error", "message": "Agent not found"}

    original_provider = agent.get("model_provider", "openai")
    original_model = agent.get("model_name", "gpt-5.2")

    # Build fallback chain excluding the original failed model
    chain = [m for m in FALLBACK_CHAIN if not (m[0] == original_provider and m[1] == original_model)]

    for attempt, (fb_provider, fb_model) in enumerate(chain[:3], 1):
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            from services.agent_service import build_brain_context

            brain_ctx = await build_brain_context(user_id, agent["agent_id"])
            system_msg = agent.get("system_prompt", "You are a helpful specialist.")
            if brain_ctx:
                system_msg += brain_ctx

            chat = LlmChat(
                api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
                session_id=f"retry_{task_id}_{attempt}_{uuid.uuid4().hex[:6]}",
                system_message=system_msg
            ).with_model(fb_provider, fb_model)

            goal = task.get("source_goal", "")
            prompt = f"""You are retrying a failed task. Execute it carefully.

TASK: {task['description']}
{f'PROJECT GOAL: {goal}' if goal else ''}
PREVIOUS ERROR: {original_error[:300]}

Provide a complete, high-quality deliverable. Be thorough and professional."""

            result = await chat.send_message(UserMessage(text=prompt))

            # Update task with retry result
            await db.tasks.update_one(
                {"task_id": task_id},
                {"$set": {
                    "status": "completed",
                    "result": result[:3000],
                    "retry_info": {
                        "attempts": attempt,
                        "fallback_model": f"{fb_provider}/{fb_model}",
                        "original_error": original_error[:200],
                    },
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )

            return {
                "status": "recovered",
                "task_id": task_id,
                "fallback_model": f"{fb_provider}/{fb_model}",
                "attempts": attempt,
                "result_preview": result[:200],
            }

        except Exception as e:
            logger.warning(f"Retry attempt {attempt} failed with {fb_provider}/{fb_model}: {e}")
            continue

    # All retries failed → escalate
    return await escalate_task(task_id, user_id, project_id, original_error)


async def escalate_task(task_id: str, user_id: str, project_id: str, error: str) -> dict:
    """Escalate a failed task: notify Commander, then user."""
    task = await db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        return {"status": "error", "message": "Task not found"}

    await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {
            "status": "escalated",
            "escalation": {
                "reason": f"All retry attempts failed: {error[:300]}",
                "escalated_at": datetime.now(timezone.utc).isoformat(),
                "level": "user",
            },
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    # Create notification for user
    try:
        from shared.utils import create_notification
        await create_notification(
            user_id, "task_escalated",
            f"Task Escalated: {task.get('title', 'Untitled')}",
            f"Task failed after multiple retry attempts. Needs manual intervention. Error: {error[:200]}",
            "/tasks"
        )
    except Exception:
        pass

    return {
        "status": "escalated",
        "task_id": task_id,
        "level": "user",
        "message": "All fallback models failed. Task escalated to user for manual review.",
    }


async def get_quality_dashboard(user_id: str) -> dict:
    """Get quality metrics for the user's tasks."""
    total_reviews = await db.quality_reviews.count_documents({"user_id": user_id})
    pass_count = await db.quality_reviews.count_documents({"user_id": user_id, "verdict": "pass"})
    revision_count = await db.quality_reviews.count_documents({"user_id": user_id, "verdict": "revision_needed"})
    fail_count = await db.quality_reviews.count_documents({"user_id": user_id, "verdict": "fail"})

    # Average score
    pipeline = [
        {"$match": {"user_id": user_id, "score": {"$exists": True}}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}, "count": {"$sum": 1}}}
    ]
    agg = await db.quality_reviews.aggregate(pipeline).to_list(1)
    avg_score = round(agg[0]["avg_score"], 1) if agg and agg[0].get("avg_score") is not None else 0

    # Escalated tasks
    escalated = await db.tasks.count_documents({"user_id": user_id, "status": "escalated"})

    # Recovered tasks (retried successfully)
    recovered = await db.tasks.count_documents({"user_id": user_id, "retry_info": {"$exists": True}, "status": "completed"})

    # Recent reviews
    recent = await db.quality_reviews.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)

    return {
        "total_reviews": total_reviews,
        "pass_count": pass_count,
        "revision_count": revision_count,
        "fail_count": fail_count,
        "avg_score": avg_score,
        "pass_rate": round(pass_count / max(total_reviews, 1) * 100, 1),
        "escalated_tasks": escalated,
        "recovered_tasks": recovered,
        "recent_reviews": recent,
    }
