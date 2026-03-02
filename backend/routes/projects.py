"""Projects / Workflow endpoints — Strategic goal execution."""
import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends

from db import db
from auth import get_current_user, User
from models.schemas import ProjectCreate, ProjectUpdate, AutonomySettings
from shared.constants import EMERGENT_LLM_KEY
from services.orchestration_service import create_project, execute_project

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/projects")
async def list_projects(status: str = "", current_user: User = Depends(get_current_user)):
    """List all projects for the current user."""
    query = {"user_id": current_user.user_id}
    if status:
        query["status"] = status
    projects = await db.projects.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"projects": projects}


@router.get("/projects/active-summary")
async def active_summary(current_user: User = Depends(get_current_user)):
    """Quick summary for executive dashboard."""
    projects = await db.projects.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "project_id": 1, "title": 1, "goal": 1, "status": 1, "scores": 1,
         "milestones": 1, "total_tasks": 1, "completed_tasks": 1, "execution_mode": 1,
         "priority": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(20)

    active = [p for p in projects if p.get("status") in ("active", "executing", "planning")]
    completed = [p for p in projects if p.get("status") in ("completed", "completed_with_issues")]

    # Active agent count
    in_progress_tasks = await db.tasks.count_documents({
        "user_id": current_user.user_id, "project_id": {"$exists": True}, "status": "in_progress"
    })

    return {
        "projects": projects,
        "active_count": len(active),
        "completed_count": len(completed),
        "total_count": len(projects),
        "agents_working": in_progress_tasks,
    }


@router.post("/projects")
async def create_new_project(data: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Create a new project from a business goal."""
    # Get user's API keys
    user = await db.users.find_one({"user_id": current_user.user_id}, {"_id": 0})
    api_keys = user.get("api_keys", {}) if user else {}
    if not api_keys.get("emergent"):
        api_keys["emergent"] = EMERGENT_LLM_KEY

    project = await create_project(
        goal=data.goal,
        user_id=current_user.user_id,
        execution_mode=data.execution_mode,
        priority=data.priority,
        api_keys=api_keys,
    )

    return project


@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get full project details with task results."""
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(404, "Project not found")

    # Enrich with full task data
    tasks = await db.tasks.find(
        {"project_id": project_id}, {"_id": 0}
    ).to_list(100)
    project["tasks_detail"] = tasks

    return project


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate, current_user: User = Depends(get_current_user)):
    """Update project settings."""
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": current_user.user_id}
    )
    if not project:
        raise HTTPException(404, "Project not found")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.projects.update_one({"project_id": project_id}, {"$set": updates})
    return {"success": True}


@router.post("/projects/{project_id}/execute")
async def execute_project_endpoint(project_id: str, current_user: User = Depends(get_current_user)):
    """Trigger execution of a project (for draft/approval mode)."""
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(404, "Project not found")
    if project.get("status") in ("completed", "completed_with_issues"):
        raise HTTPException(400, "Project already completed")

    user = await db.users.find_one({"user_id": current_user.user_id}, {"_id": 0})
    api_keys = user.get("api_keys", {}) if user else {}
    if not api_keys.get("emergent"):
        api_keys["emergent"] = EMERGENT_LLM_KEY

    await db.projects.update_one(
        {"project_id": project_id},
        {"$set": {"status": "active", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    asyncio.create_task(execute_project(project_id, current_user.user_id, api_keys))
    return {"success": True, "message": "Project execution started"}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Delete a project and its tasks."""
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": current_user.user_id}
    )
    if not project:
        raise HTTPException(404, "Project not found")

    await db.tasks.delete_many({"project_id": project_id})
    await db.projects.delete_one({"project_id": project_id})
    return {"success": True}


@router.get("/user/autonomy")
async def get_autonomy(current_user: User = Depends(get_current_user)):
    """Get user's autonomy settings."""
    user = await db.users.find_one({"user_id": current_user.user_id}, {"_id": 0, "autonomy_level": 1})
    return {"autonomy_level": user.get("autonomy_level", "approval") if user else "approval"}


@router.put("/user/autonomy")
async def set_autonomy(data: AutonomySettings, current_user: User = Depends(get_current_user)):
    """Set user's default autonomy level."""
    if data.autonomy_level not in ("manual", "approval", "autonomous"):
        raise HTTPException(400, "Invalid autonomy level")
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"autonomy_level": data.autonomy_level}}
    )
    return {"success": True, "autonomy_level": data.autonomy_level}
