"""Orchestration service — Strategic Cognition + Autonomous Execution Engine.

Transforms high-level business goals into structured projects with milestones,
delegates to specialist agents, monitors execution, and self-corrects.
"""
import uuid
import json
import logging
import asyncio
from datetime import datetime, timezone

from db import db
from config import DEFAULT_AGENTS
from shared.constants import EMERGENT_LLM_KEY
from services.agent_service import AGENT_ROLE_MAP

logger = logging.getLogger(__name__)


async def score_goal(goal: str, api_keys: dict) -> dict:
    """Score a goal for clarity, complexity, and strategic alignment."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        scorer = LlmChat(
            api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
            session_id=f"goal_score_{uuid.uuid4().hex[:8]}",
            system_message="You score business goals. Return ONLY valid JSON."
        ).with_model("openai", "gpt-4o-mini")

        prompt = f"""Score this business goal on a 1-10 scale for each metric. Return ONLY a JSON object:

Goal: "{goal}"

{{
  "clarity": <1-10 how clear and specific the goal is>,
  "complexity": <1-10 how complex to execute>,
  "estimated_agents": <number of specialist agents needed>,
  "estimated_hours": <rough hours to complete>,
  "risk_level": "low" or "medium" or "high",
  "confidence": <1-10 system confidence in achieving this>,
  "refined_title": "<clean 5-8 word title for this project>",
  "strategic_summary": "<1-2 sentence strategic assessment>"
}}"""
        response = await scorer.send_message(UserMessage(text=prompt))
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Goal scoring error: {e}")
        return {
            "clarity": 5, "complexity": 5, "estimated_agents": 3,
            "estimated_hours": 8, "risk_level": "medium", "confidence": 6,
            "refined_title": goal[:60], "strategic_summary": "Goal accepted for processing."
        }


async def create_strategic_plan(goal: str, scores: dict, api_keys: dict) -> dict:
    """Create a strategic plan with milestones and task assignments."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        planner = LlmChat(
            api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
            session_id=f"strategic_plan_{uuid.uuid4().hex[:8]}",
            system_message="You are a world-class strategic planner. Output ONLY valid JSON."
        ).with_model("openai", "gpt-5.2")

        available_roles = list(AGENT_ROLE_MAP.keys())
        prompt = f"""Create an execution plan for this business goal. Return ONLY valid JSON.

Goal: "{goal}"
Complexity: {scores.get('complexity', 5)}/10
Estimated agents needed: {scores.get('estimated_agents', 3)}

Available specialist roles: {', '.join(available_roles)}

Return this exact JSON structure:
{{
  "milestones": [
    {{
      "title": "Milestone name",
      "description": "What this milestone achieves",
      "phase": 1,
      "tasks": [
        {{
          "title": "Task title",
          "description": "Detailed task description with specific deliverables",
          "agent_role": "one of the available roles above",
          "priority": "high/medium/low",
          "estimated_minutes": 15
        }}
      ]
    }}
  ],
  "execution_strategy": "Brief 2-3 sentence strategy for achieving this goal",
  "success_criteria": ["Measurable criterion 1", "Criterion 2", "Criterion 3"],
  "risks": ["Risk 1", "Risk 2"]
}}

Create 2-4 milestones with 1-3 tasks each. Be specific and actionable."""

        response = await planner.send_message(UserMessage(text=prompt))
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Strategic planning error: {e}")
        return {
            "milestones": [{
                "title": "Execute Goal",
                "description": goal,
                "phase": 1,
                "tasks": [{"title": "Analyze and execute", "description": goal, "agent_role": "strategy", "priority": "high", "estimated_minutes": 30}]
            }],
            "execution_strategy": "Direct execution approach.",
            "success_criteria": ["Goal completed successfully"],
            "risks": ["Unclear requirements"]
        }


async def create_project(goal: str, user_id: str, execution_mode: str, priority: str, api_keys: dict) -> dict:
    """Full project creation pipeline: Score → Plan → Create → (optionally) Execute."""
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Score the goal
    scores = await score_goal(goal, api_keys)

    # Step 2: Create strategic plan
    plan = await create_strategic_plan(goal, scores, api_keys)

    # Step 3: Build project document
    milestones = []
    all_tasks = []
    for ms in plan.get("milestones", []):
        ms_id = f"ms_{uuid.uuid4().hex[:8]}"
        ms_tasks = []
        for t in ms.get("tasks", []):
            agent_role = t.get("agent_role", "strategy").lower()
            agent_id = AGENT_ROLE_MAP.get(agent_role, "agent_strategist")
            agent_doc = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "name": 1, "avatar": 1, "role": 1})

            task_id = f"task_{uuid.uuid4().hex[:12]}"
            task_doc = {
                "task_id": task_id,
                "user_id": user_id,
                "project_id": project_id,
                "milestone_id": ms_id,
                "title": t.get("title", "Untitled"),
                "description": t.get("description", ""),
                "status": "pending",
                "priority": t.get("priority", "medium"),
                "assigned_agents": [agent_id],
                "agent_name": agent_doc.get("name", "Agent") if agent_doc else "Agent",
                "agent_avatar": agent_doc.get("avatar", "") if agent_doc else "",
                "agent_role": agent_doc.get("role", "Specialist") if agent_doc else "Specialist",
                "result": None,
                "source": "orchestrator",
                "source_goal": goal[:200],
                "estimated_minutes": t.get("estimated_minutes", 15),
                "created_at": now,
                "updated_at": now,
            }
            await db.tasks.insert_one(task_doc)
            ms_tasks.append(task_id)
            all_tasks.append(task_doc)

        milestones.append({
            "milestone_id": ms_id,
            "title": ms.get("title", "Milestone"),
            "description": ms.get("description", ""),
            "phase": ms.get("phase", 1),
            "status": "pending",
            "task_ids": ms_tasks,
        })

    project_doc = {
        "project_id": project_id,
        "user_id": user_id,
        "goal": goal,
        "title": scores.get("refined_title", goal[:60]),
        "status": "planning" if execution_mode == "draft" else "active",
        "execution_mode": execution_mode,
        "priority": priority,
        "scores": {
            "clarity": scores.get("clarity", 5),
            "complexity": scores.get("complexity", 5),
            "confidence": scores.get("confidence", 6),
            "risk_level": scores.get("risk_level", "medium"),
            "estimated_agents": scores.get("estimated_agents", 3),
            "estimated_hours": scores.get("estimated_hours", 8),
        },
        "strategic_summary": scores.get("strategic_summary", ""),
        "execution_strategy": plan.get("execution_strategy", ""),
        "success_criteria": plan.get("success_criteria", []),
        "risks": plan.get("risks", []),
        "milestones": milestones,
        "task_ids": [t["task_id"] for t in all_tasks],
        "total_tasks": len(all_tasks),
        "completed_tasks": 0,
        "created_at": now,
        "updated_at": now,
    }

    await db.projects.insert_one(project_doc)
    project_doc.pop("_id", None)

    # Step 4: If autonomous, start execution immediately
    if execution_mode == "autonomous":
        asyncio.create_task(execute_project(project_id, user_id, api_keys))

    return project_doc


async def execute_project(project_id: str, user_id: str, api_keys: dict):
    """Execute all pending tasks in a project, milestone by milestone."""
    try:
        project = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
        if not project:
            return

        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {"status": "executing", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )

        completed = 0
        for ms in project.get("milestones", []):
            ms_id = ms["milestone_id"]
            await db.projects.update_one(
                {"project_id": project_id, "milestones.milestone_id": ms_id},
                {"$set": {"milestones.$.status": "in_progress"}}
            )

            for task_id in ms.get("task_ids", []):
                task = await db.tasks.find_one({"task_id": task_id}, {"_id": 0})
                if not task or task.get("status") == "completed":
                    if task and task.get("status") == "completed":
                        completed += 1
                    continue

                await db.tasks.update_one(
                    {"task_id": task_id},
                    {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
                )

                agent_id = task.get("assigned_agents", ["agent_strategist"])[0]
                agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
                if not agent:
                    continue

                try:
                    result = await execute_agent_task(
                        agent=agent,
                        task_description=task["description"],
                        goal=project["goal"],
                        api_keys=api_keys,
                        user_id=user_id,
                        project_id=project_id,
                    )
                    await db.tasks.update_one(
                        {"task_id": task_id},
                        {"$set": {
                            "status": "completed",
                            "result": result[:3000],
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }}
                    )
                    completed += 1
                except Exception as e:
                    logger.error(f"Task execution failed {task_id}: {e}")
                    await db.tasks.update_one(
                        {"task_id": task_id},
                        {"$set": {"status": "failed", "result": str(e)[:500], "updated_at": datetime.now(timezone.utc).isoformat()}}
                    )

                # Update project progress
                await db.projects.update_one(
                    {"project_id": project_id},
                    {"$set": {"completed_tasks": completed, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )

            # Mark milestone complete if all tasks done
            ms_tasks = await db.tasks.find({"task_id": {"$in": ms.get("task_ids", [])}}, {"_id": 0, "status": 1}).to_list(50)
            if all(t.get("status") in ("completed", "failed") for t in ms_tasks):
                await db.projects.update_one(
                    {"project_id": project_id, "milestones.milestone_id": ms_id},
                    {"$set": {"milestones.$.status": "completed"}}
                )

        # Finalize project
        final_status = "completed"
        failed_count = await db.tasks.count_documents({"project_id": project_id, "status": "failed"})
        if failed_count > 0:
            final_status = "completed_with_issues"

        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {"status": final_status, "completed_tasks": completed, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )

        # Notify user
        from shared.utils import create_notification
        await create_notification(
            user_id, "project_complete",
            f"Project Complete: {project.get('title', 'Untitled')}",
            f"Your project has finished with {completed}/{project.get('total_tasks', 0)} tasks completed.",
            "/projects"
        )

    except Exception as e:
        logger.error(f"Project execution failed {project_id}: {e}")
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {"status": "error", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )


async def execute_agent_task(agent: dict, task_description: str, goal: str, api_keys: dict, user_id: str, project_id: str) -> str:
    """Execute a single task using the assigned agent."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
            session_id=f"project_{project_id}_{agent['agent_id']}_{uuid.uuid4().hex[:6]}",
            system_message=agent.get("system_prompt", "You are a helpful specialist.")
        ).with_model(agent.get("model_provider", "openai"), agent.get("model_name", "gpt-5.2"))

        prompt = f"""You are executing a task as part of an autonomous project.

PROJECT GOAL: {goal}
YOUR TASK: {task_description}

Execute this task NOW. Provide a complete, actionable deliverable. Do NOT ask questions — use your professional judgment. Be concise, specific, and deliver real value. Write in clean paragraphs, avoid excessive formatting."""

        response = await chat.send_message(UserMessage(text=prompt))
        return response
    except Exception as e:
        raise Exception(f"Agent {agent.get('name', 'Unknown')} execution failed: {str(e)[:200]}")
