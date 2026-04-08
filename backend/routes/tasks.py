"""Task management endpoints."""
import uuid
import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from db import db
from auth import get_current_user, User
from models.schemas import Task, TaskCreate, TaskUpdate
from shared.constants import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await db.tasks.find({"user_id": current_user.user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for task in tasks:
        if isinstance(task.get('created_at'), str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if isinstance(task.get('updated_at'), str):
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
    
    return tasks

@router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    task_doc = {
        "task_id": task_id,
        "user_id": current_user.user_id,
        "title": task_data.title,
        "description": task_data.description,
        "status": "pending",
        "priority": task_data.priority,
        "assigned_agents": task_data.assigned_agents,
        "result": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.tasks.insert_one(task_doc)
    task_doc['created_at'] = now
    task_doc['updated_at'] = now
    return Task(**task_doc)

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.tasks.update_one({"task_id": task_id}, {"$set": update_data})
    
    updated_task = await db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if isinstance(updated_task.get('created_at'), str):
        updated_task['created_at'] = datetime.fromisoformat(updated_task['created_at'])
    if isinstance(updated_task.get('updated_at'), str):
        updated_task['updated_at'] = datetime.fromisoformat(updated_task['updated_at'])
    
    return Task(**updated_task)

@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.get("assigned_agents"):
        raise HTTPException(status_code=400, detail="No agents assigned to task")
    
    # Block double-execution
    if task.get("status") == "in_progress":
        raise HTTPException(status_code=409, detail="Task is already executing")

    priority = task.get("priority", "medium")
    priority_directive = {
        "critical": "⚡ CRITICAL PRIORITY — respond with maximum urgency, depth, and precision.",
        "high":     "🔴 HIGH PRIORITY — deliver a comprehensive, thorough response.",
        "medium":   "Deliver a complete, well-structured response.",
        "low":      "Provide a concise but complete response.",
    }.get(priority, "Deliver a complete, well-structured response.")

    # Update status to in_progress
    await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    start_ts = time.monotonic()
    results = []
    errors = []

    async def _run_agent(agent_id: str) -> str:
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        if not agent:
            return f"**{agent_id}:** Agent not found"
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            llm_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"{task_id}_{agent_id}",
                system_message=agent["system_prompt"]
            ).with_model(agent["model_provider"], agent["model_name"])
            prompt = (
                f"{priority_directive}\n\n"
                f"**Task:** {task['title']}\n\n"
                f"**Description:**\n{task['description']}\n\n"
                f"Please complete this task thoroughly and provide structured output with clear sections."
            )
            response = await llm_chat.send_message(UserMessage(text=prompt))
            return f"**{agent['name']} ({agent.get('role', 'Agent')}):**\n{response}"
        except Exception as e:
            logger.error(f"Task execution error for agent {agent_id}: {e}")
            errors.append(agent_id)
            return f"**{agent.get('name', agent_id)}:** ⚠️ Execution error — {str(e)}"

    # Run all agents concurrently
    agent_results = await asyncio.gather(*[_run_agent(aid) for aid in task["assigned_agents"]])
    results = list(agent_results)

    elapsed_ms = int((time.monotonic() - start_ts) * 1000)
    combined_result = "\n\n---\n\n".join(results)

    # Add execution metadata footer
    combined_result += (
        f"\n\n---\n*Executed {len(task['assigned_agents'])} agent(s) in {elapsed_ms}ms"
        f" · Priority: {priority.upper()}"
        + (f" · {len(errors)} error(s)" if errors else "")
        + "*"
    )

    final_status = "failed" if len(errors) == len(task["assigned_agents"]) else "completed"

    await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {
            "status": final_status,
            "result": combined_result,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    return {"status": final_status, "result": combined_result, "elapsed_ms": elapsed_ms}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    result = await db.tasks.delete_one({"task_id": task_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

