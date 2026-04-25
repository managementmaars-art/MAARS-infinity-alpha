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
from services.agent_service import AGENT_ROLE_MAP

logger = logging.getLogger(__name__)


async def score_goal(goal: str, api_keys: dict, user_id: str = "system") -> dict:
    """Score a goal for clarity, complexity, and strategic alignment."""
    try:
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
        from services.llm_gateway import complete_text
        response = await complete_text(
            user_id=user_id,
            system_prompt="You score business goals. Return ONLY valid JSON.",
            user_prompt=prompt,
            model="maars/auto",
            source="orchestration.score_goal",
        )
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


async def create_strategic_plan(goal: str, scores: dict, api_keys: dict, user_id: str = "system") -> dict:
    """Create a strategic plan with milestones and task assignments."""
    try:
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

        from services.llm_gateway import complete_text
        response = await complete_text(
            user_id=user_id,
            system_prompt="You are a world-class strategic planner. Output ONLY valid JSON.",
            user_prompt=prompt,
            model="maars/auto",
            source="orchestration.strategic_plan",
        )
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
    scores = await score_goal(goal, api_keys, user_id=user_id)

    # Step 2: Create strategic plan
    plan = await create_strategic_plan(goal, scores, api_keys, user_id=user_id)

    # Step 3: Build project document
    milestones = []
    all_tasks = []
    for ms in plan.get("milestones", []):
        from services.agents import agent_router_map
        ms_id = f"ms_{uuid.uuid4().hex[:8]}"
        ms_tasks = []
        for t in ms.get("tasks", []):
            agent_role = t.get("agent_role", "strategy").lower()
            try:
                agent_id = await agent_router_map.resolve(agent_role)
            except Exception:
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

        # Fetch all project tasks for collaboration detection
        all_project_tasks = await db.tasks.find(
            {"project_id": project_id}, {"_id": 0}
        ).to_list(100)

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

                    # Quality Control: Auto-review task result
                    quality_review = None
                    try:
                        from services.quality_service import critic_review
                        quality_review = await critic_review(
                            task_result=result[:2000],
                            task_description=task["description"],
                            agent_name=agent.get("name", "Agent"),
                            agent_id=agent.get("agent_id"),
                            user_id=user_id,
                            project_id=project_id,
                            task_id=task_id,
                            api_keys=api_keys,
                        )
                    except Exception as qc_err:
                        logger.error(f"Quality review error: {qc_err}")

                    await db.tasks.update_one(
                        {"task_id": task_id},
                        {"$set": {
                            "status": "completed",
                            "result": result[:3000],
                            "quality_score": quality_review.get("score") if quality_review else None,
                            "quality_verdict": quality_review.get("verdict") if quality_review else None,
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }}
                    )
                    completed += 1

                    # Memory Auto-Learning: Extract learnings from completed task
                    try:
                        from services.memory_learning_service import extract_learnings_from_task
                        asyncio.create_task(extract_learnings_from_task(
                            task_result=result[:2000],
                            task_description=task["description"],
                            task_title=task.get("title", "Untitled"),
                            agent_name=agent.get("name", "Agent"),
                            agent_id=agent.get("agent_id", ""),
                            user_id=user_id,
                            project_id=project_id,
                            quality_score=quality_review.get("score") if quality_review else None,
                            api_keys=api_keys,
                        ))
                    except Exception as learn_err:
                        logger.error(f"Auto-learn error: {learn_err}")

                    # Autonomous Collaboration: Detect cross-domain dependencies
                    await _detect_and_create_collaborations(
                        task=task, agent=agent, result=result,
                        project=project, user_id=user_id, all_tasks=all_project_tasks
                    )
                except Exception as e:
                    logger.error(f"Task execution failed {task_id}: {e}")
                    # Failure Recovery: Retry with fallback models
                    try:
                        from services.quality_service import retry_with_fallback
                        recovery = await retry_with_fallback(
                            task_id=task_id,
                            user_id=user_id,
                            project_id=project_id,
                            original_error=str(e)[:500],
                            api_keys=api_keys,
                        )
                        if recovery.get("status") == "recovered":
                            completed += 1
                            logger.info(f"Task {task_id} recovered via {recovery.get('fallback_model')}")
                        else:
                            logger.warning(f"Task {task_id} escalated: {recovery.get('message', '')}")
                    except Exception as retry_err:
                        logger.error(f"Retry failed for {task_id}: {retry_err}")
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

        # Commander → Personal Secretary Handoff
        # Auto-create a task for the secretary to execute real-world actions
        try:
            completed_results = []
            all_tasks = await db.tasks.find(
                {"project_id": project_id, "status": "completed"}, {"_id": 0, "title": 1, "result": 1, "agent_role": 1}
            ).to_list(50)
            for t in all_tasks:
                if t.get("result"):
                    completed_results.append(f"- {t['title']}: {t['result'][:500]}")

            if completed_results:
                secretary_task = {
                    "task_id": f"task_{uuid.uuid4().hex[:12]}",
                    "user_id": user_id,
                    "project_id": project_id,
                    "title": f"Execute deliverables for: {project.get('title', 'Project')}",
                    "description": f"The Commander has completed project '{project.get('title')}'. Review the following deliverables and identify any real-world actions needed (emails to send, meetings to schedule, content to post, messages to deliver):\n\n" + "\n".join(completed_results[:10]),
                    "status": "pending",
                    "priority": "high",
                    "assigned_agents": ["agent_secretary"],
                    "agent_name": "Nadia Kessler",
                    "agent_role": "Personal Secretary",
                    "result": None,
                    "source": "commander_handoff",
                    "source_goal": project.get("goal", "")[:200],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                await db.tasks.insert_one(secretary_task)
                logger.info(f"Commander→Secretary handoff created for project {project_id}")
        except Exception as handoff_err:
            logger.error(f"Secretary handoff failed: {handoff_err}")

    except Exception as e:
        logger.error(f"Project execution failed {project_id}: {e}")
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {"status": "error", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )


async def execute_agent_task(agent: dict, task_description: str, goal: str, api_keys: dict, user_id: str, project_id: str) -> str:
    """Execute a single task using the assigned agent. Supports media generation for image/video tasks."""
    try:
        from services.agent_service import build_brain_context

        brain_ctx = await build_brain_context(user_id, agent["agent_id"])
        system_msg = agent.get("system_prompt", "You are a helpful specialist.")
        if brain_ctx:
            system_msg += brain_ctx

        # LLM Router: Select optimal model
        model_provider = agent.get("model_provider", "openai")
        model_name = agent.get("model_name", "gpt-5.2")
        try:
            from services.routing.llm_router import route_to_model
            routing = await route_to_model(task_description, agent.get("role", ""), user_id)
            model_provider = routing["provider"]
            model_name = routing["model"]
            logger.info(f"Router selected {model_provider}/{model_name}: {routing.get('reason', '')}")
        except Exception as route_err:
            logger.warning(f"Router fallback to default: {route_err}")

        # Check if this is a media generation task
        agent_id = agent.get("agent_id", "")
        is_graphics_agent = agent_id == "agent_graphics"
        is_video_agent = agent_id == "agent_video"

        if is_graphics_agent:
            system_msg += "\n\nIMPORTANT: When creating visual content, describe your creative concept in detail (style, colors, composition). The system will automatically generate the image."

        if is_video_agent:
            system_msg += "\n\nIMPORTANT: When creating video content, describe your creative vision in detail (scenes, camera angles, mood, pacing). The system will automatically generate the video."

        prompt = f"""You are executing a task as part of an autonomous project.

PROJECT GOAL: {goal}
YOUR TASK: {task_description}

Execute this task NOW. Provide a complete, actionable deliverable. Do NOT ask questions — use your professional judgment. Be concise, specific, and deliver real value. Write in clean paragraphs, avoid excessive formatting."""

        from services.llm_gateway import complete_text
        gw_model = "maars/auto" if model_provider in ("auto", None) else f"{model_provider}/{model_name}"
        response = await complete_text(
            user_id=user_id,
            system_prompt=system_msg,
            user_prompt=prompt,
            model=gw_model,
            source=f"orchestration.execute_agent_task:{agent.get('agent_id','?')}",
        )

        # For graphics agent, attempt to generate an image based on the response
        if is_graphics_agent and response:
            try:
                image_result = await _generate_project_image(response, api_keys, project_id, agent_id, user_id=user_id)
                if image_result:
                    response += f"\n\n[GENERATED_IMAGE]{image_result}[/GENERATED_IMAGE]"
            except Exception as img_err:
                logger.error(f"Project image generation error: {img_err}")

        # For video agent, attempt to generate a video
        if is_video_agent and response:
            try:
                video_result = await _generate_project_video(response, api_keys, project_id, agent_id, user_id=user_id)
                if video_result:
                    response += f"\n\n[GENERATED_VIDEO]{video_result}[/GENERATED_VIDEO]"
            except Exception as vid_err:
                logger.error(f"Project video generation error: {vid_err}")

        return response
    except Exception as e:
        raise Exception(f"Agent {agent.get('name', 'Unknown')} execution failed: {str(e)[:200]}")


async def _generate_project_image(agent_response: str, api_keys: dict, project_id: str, agent_id: str, user_id: str = "system") -> str:
    """Generate an image based on the agent's creative description, through the MAARS media router."""
    try:
        from services.llm_gateway import complete_text
        img_prompt = (await complete_text(
            user_id=user_id,
            system_prompt="Extract a concise image generation prompt from the creative description. Return ONLY the prompt text, nothing else. Max 200 characters.",
            user_prompt=f"Extract image prompt from:\n{agent_response[:1500]}",
            model="maars/economy",
            source="orchestration.image_prompt_extract",
        )).strip()[:200]
        if not img_prompt:
            return ""

        from services.media_router import route_image
        from shared.constants import UPLOAD_DIR
        image_bytes, meta = await route_image(prompt=img_prompt, quality="standard")
        filename = f"proj_{project_id}_{uuid.uuid4().hex[:8]}.png"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        return f"/files/{filename}"
    except Exception as e:
        logger.error(f"Image generation in project failed: {e}")
        return ""


async def _generate_project_video(agent_response: str, api_keys: dict, project_id: str, agent_id: str, user_id: str = "system") -> str:
    """Generate a video based on the agent's creative description, through the MAARS media router."""
    try:
        from services.llm_gateway import complete_text
        vid_prompt = (await complete_text(
            user_id=user_id,
            system_prompt="Extract a concise video generation prompt from the creative description. Return ONLY the prompt text, nothing else. Max 200 characters.",
            user_prompt=f"Extract video prompt from:\n{agent_response[:1500]}",
            model="maars/economy",
            source="orchestration.video_prompt_extract",
        )).strip()[:200]
        if not vid_prompt:
            return ""

        from services.media_router import route_video
        from shared.constants import UPLOAD_DIR
        video_bytes, meta = await route_video(prompt=vid_prompt, duration=4, size="1280x720")
        filename = f"proj_{project_id}_{uuid.uuid4().hex[:8]}.mp4"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(video_bytes)
        return f"/files/{filename}"
    except Exception as e:
        logger.error(f"Video generation in project failed: {e}")
        return ""


# Domain mapping for autonomous collaboration detection
AGENT_DOMAIN_MAP = {
    "agent_commander": "executive", "agent_strategist": "executive",
    "agent_revenue": "executive", "agent_investor": "executive",
    "agent_pm": "product", "agent_developer": "technical",
    "agent_automation": "technical", "agent_ai_optimizer": "technical",
    "agent_data_engineer": "technical", "agent_cybersecurity": "technical",
    "agent_brand_architect": "creative", "agent_graphics": "creative",
    "agent_video": "creative", "agent_copywriter": "creative",
    "agent_web_designer": "creative", "agent_ux_researcher": "creative",
    "agent_3d_specialist": "creative",
    "agent_marketing": "marketing", "agent_growth_hacker": "marketing",
    "agent_seo": "marketing", "agent_social_media": "marketing",
    "agent_email_marketing": "marketing", "agent_sales": "marketing",
    "agent_pr_manager": "marketing",
    "agent_ops": "operations", "agent_inventory": "operations",
    "agent_procurement": "operations", "agent_hr": "operations",
    "agent_customer_service": "operations", "agent_cx_architect": "operations",
    "agent_finance": "finance", "agent_data_analyst": "finance",
    "agent_legal": "governance", "agent_compliance": "governance", "agent_ethics": "governance",
    "agent_research": "intelligence", "agent_knowledge": "intelligence",
    "agent_localization": "intelligence", "agent_secretary": "operations",
}

CROSS_DOMAIN_TRIGGERS = {
    "marketing": {"creative", "technical"},
    "creative": {"marketing", "product"},
    "technical": {"product", "operations"},
    "product": {"technical", "creative", "marketing"},
    "finance": {"executive", "operations"},
    "executive": {"finance", "product", "marketing"},
    "governance": {"executive", "operations"},
    "operations": {"technical", "finance"},
    "intelligence": {"marketing", "product", "executive"},
}


async def _detect_and_create_collaborations(task: dict, agent: dict, result: str,
                                            project: dict, user_id: str, all_tasks: list):
    """Detect cross-domain dependencies and auto-create collaboration entries."""
    try:
        agent_id = agent.get("agent_id", "")
        agent_domain = AGENT_DOMAIN_MAP.get(agent_id, "general")
        task_desc_lower = task.get("description", "").lower()

        # Find other agents in this project from different domains
        collaborators = []
        for t in all_tasks:
            other_agent_id = (t.get("assigned_agents") or [""])[0]
            if other_agent_id == agent_id:
                continue
            other_domain = AGENT_DOMAIN_MAP.get(other_agent_id, "general")

            # Create collaboration if domains trigger each other
            related_domains = CROSS_DOMAIN_TRIGGERS.get(agent_domain, set())
            if other_domain in related_domains:
                collaborators.append({
                    "agent_id": other_agent_id,
                    "name": t.get("agent_name", "Agent"),
                    "domain": other_domain,
                    "task_title": t.get("title", ""),
                })

        if not collaborators:
            return

        # Determine collaboration type based on content
        collab_type = "information_sharing"
        if any(kw in task_desc_lower for kw in ["review", "approve", "validate", "check"]):
            collab_type = "review_request"
        elif any(kw in task_desc_lower for kw in ["data", "input", "provide", "send", "share"]):
            collab_type = "data_handoff"
        elif any(kw in task_desc_lower for kw in ["coordinate", "align", "sync", "together"]):
            collab_type = "coordination"

        # Create collaboration entries (max 3 per task to avoid spam)
        for collab_agent in collaborators[:3]:
            collab_doc = {
                "collab_id": f"collab_{uuid.uuid4().hex[:12]}",
                "user_id": user_id,
                "task_id": task.get("task_id", ""),
                "project_id": project.get("project_id", ""),
                "sender": agent.get("name", "Agent"),
                "sender_domain": agent_domain,
                "receivers": [collab_agent["name"]],
                "receiver_domain": collab_agent["domain"],
                "objective": f"Cross-domain collaboration: {task.get('title', '')}",
                "context": f"Agent '{agent.get('name')}' ({agent_domain}) completed '{task.get('title')}' which impacts {collab_agent['name']} ({collab_agent['domain']}) working on '{collab_agent['task_title']}'.",
                "collaboration_type": collab_type,
                "required_output": f"Review and integrate output from {agent.get('name')}",
                "auto_generated": True,
                "risk_level": task.get("priority", "medium"),
                "dependencies": [task.get("task_id", "")],
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.collaborations.insert_one(collab_doc)

        logger.info(f"Auto-created {len(collaborators[:3])} collaborations for task {task.get('task_id')}")

    except Exception as e:
        logger.error(f"Auto-collaboration detection error: {e}")
