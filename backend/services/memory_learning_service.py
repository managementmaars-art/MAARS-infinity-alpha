"""Memory Auto-Learning Service — extracts key learnings from completed agent tasks."""
import uuid
import logging
from datetime import datetime, timezone

from db import db
from shared.constants import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)

MAX_MEMORY_PER_USER = 500


async def extract_learnings_from_task(
    task_result: str,
    task_description: str,
    task_title: str,
    agent_name: str,
    agent_id: str,
    user_id: str,
    project_id: str = "",
    quality_score: float = None,
    api_keys: dict = None,
):
    """Extract key learnings from a completed task and store as memory entries."""
    if not task_result or len(task_result.strip()) < 50:
        return []

    # Check memory limit
    count = await db.memory_entries.count_documents({"user_id": user_id})
    if count >= MAX_MEMORY_PER_USER:
        logger.info(f"Memory limit reached for user {user_id}, skipping auto-learn")
        return []

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        extractor = LlmChat(
            api_key=(api_keys or {}).get("emergent", EMERGENT_LLM_KEY),
            session_id=f"memory_learn_{uuid.uuid4().hex[:8]}",
            system_message="You extract key learnings from task results. Return ONLY valid JSON."
        ).with_model("openai", "gpt-4o-mini")

        prompt = f"""Analyze this completed task and extract 1-3 key learnings worth remembering for future work.

TASK: {task_title}
DESCRIPTION: {task_description[:500]}
AGENT: {agent_name}
RESULT (excerpt): {task_result[:1500]}
{f'QUALITY SCORE: {quality_score}/10' if quality_score else ''}

Return ONLY a JSON array of learnings. Each learning should be a concise, actionable insight:
[
  {{
    "content": "The specific learning or insight (1-2 sentences max)",
    "category": "one of: fact, preference, instruction, context, decision",
    "importance": 0.0 to 1.0 (how important is this for future work),
    "summary": "3-5 word summary",
    "tags": ["tag1", "tag2"]
  }}
]

Rules:
- Only extract genuinely useful learnings, not generic observations
- Skip if the task result is too generic or has no actionable insights
- Return an empty array [] if nothing worth remembering
- Max 3 learnings per task"""

        response = await extractor.send_message(UserMessage(text=prompt))
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]

        import json
        learnings = json.loads(text.strip())
        if not isinstance(learnings, list):
            return []

        created = []
        now = datetime.now(timezone.utc).isoformat()

        for learning in learnings[:3]:
            content = learning.get("content", "").strip()
            if not content or len(content) < 10:
                continue

            # Check for near-duplicate
            existing = await db.memory_entries.find_one({
                "user_id": user_id,
                "content": {"$regex": content[:40], "$options": "i"},
            })
            if existing:
                continue

            entry = {
                "memory_id": f"mem_{uuid.uuid4().hex[:12]}",
                "user_id": user_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "category": learning.get("category", "context"),
                "content": content,
                "summary": learning.get("summary", content[:40]),
                "importance": min(max(float(learning.get("importance", 0.5)), 0.1), 1.0),
                "access_count": 0,
                "version": 1,
                "versions": [{
                    "version": 1,
                    "content": content,
                    "updated_at": now,
                    "reason": "Auto-learned from task completion",
                }],
                "tags": learning.get("tags", []),
                "source": "auto_learn",
                "source_task_title": task_title[:100],
                "source_project_id": project_id,
                "quality_score": quality_score,
                "created_at": now,
                "updated_at": now,
            }

            await db.memory_entries.insert_one(entry)
            entry.pop("_id", None)
            created.append(entry)

        if created:
            logger.info(f"Auto-learned {len(created)} memories from task '{task_title}' by {agent_name}")

        return created

    except Exception as e:
        logger.error(f"Memory auto-learning error: {e}")
        return []
