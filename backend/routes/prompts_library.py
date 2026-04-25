"""Prompt library — users save, reuse, and optionally share prompts.

Retention lever: once a user has 3+ saved prompts they stop thinking
about switching. Team-plan upsell: shared prompts across a workspace.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


class PromptCreate(BaseModel):
    title: str
    body: str
    modality: str = "text"   # text | image | video | campaign | social
    tags: list[str] = []
    shared_with_workspace: bool = False


class PromptUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    tags: list[str] | None = None
    shared_with_workspace: bool | None = None


@router.get("/prompts")
async def list_prompts(
    modality: str | None = None,
    q: str | None = None,
    current_user: User = Depends(get_current_user),
):
    from db import db
    query: dict = {"$or": [
        {"owner_user_id": current_user.user_id},
        {"workspace_id": current_user.user_id, "shared_with_workspace": True},
    ]}
    if modality:
        query["modality"] = modality
    if q:
        # Best-effort text search — Mongo $text requires an index, so
        # fall back to regex over title for zero-config operation.
        query["title"] = {"$regex": q, "$options": "i"}
    docs = await db.prompts_library.find(query, {"_id": 0}).sort("updated_at", -1).to_list(500)
    return {"object": "list", "data": docs, "count": len(docs)}


@router.post("/prompts")
async def create_prompt(body: PromptCreate, current_user: User = Depends(get_current_user)):
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "prompt_id": f"prompt_{uuid.uuid4().hex[:12]}",
        "owner_user_id": current_user.user_id,
        "workspace_id": current_user.user_id,  # TODO: real workspace when multi-ws lands
        "title": body.title.strip(),
        "body": body.body,
        "modality": body.modality,
        "tags": body.tags,
        "shared_with_workspace": body.shared_with_workspace,
        "created_at": now,
        "updated_at": now,
        "use_count": 0,
    }
    await db.prompts_library.insert_one({**doc, "_id": None})
    return doc


@router.patch("/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    body: PromptUpdate,
    current_user: User = Depends(get_current_user),
):
    from db import db
    update = {k: v for k, v in body.model_dump(exclude_none=True).items()}
    if not update:
        raise HTTPException(400, "no changes")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    res = await db.prompts_library.update_one(
        {"prompt_id": prompt_id, "owner_user_id": current_user.user_id},
        {"$set": update},
    )
    if not res.matched_count:
        raise HTTPException(404, "not found")
    return {"ok": True}


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str, current_user: User = Depends(get_current_user)):
    from db import db
    res = await db.prompts_library.delete_one({
        "prompt_id": prompt_id, "owner_user_id": current_user.user_id,
    })
    return {"ok": bool(res.deleted_count)}


@router.post("/prompts/{prompt_id}/use")
async def record_usage(prompt_id: str, current_user: User = Depends(get_current_user)):
    """Bump the use_count so popular prompts bubble up in list views."""
    from db import db
    await db.prompts_library.update_one(
        {"prompt_id": prompt_id},
        {"$inc": {"use_count": 1},
         "$set": {"last_used_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"ok": True}
