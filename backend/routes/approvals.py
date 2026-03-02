"""Approval workflows for social media posts, email campaigns, and other publishable content."""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Body

from db import db
from auth import get_current_user, User
from shared.utils import create_notification

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/approvals")
async def create_approval(body: dict = Body(...), current_user: User = Depends(get_current_user)):
    """Create a new approval request (draft state)."""
    approval_id = f"appr_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "approval_id": approval_id,
        "user_id": current_user.user_id,
        "type": body.get("type", "general"),
        "title": body.get("title", "Untitled"),
        "content": body.get("content", ""),
        "metadata": body.get("metadata", {}),
        "agent_id": body.get("agent_id", ""),
        "agent_name": body.get("agent_name", ""),
        "chat_id": body.get("chat_id", ""),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.approvals.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/approvals")
async def list_approvals(
    status: str = "",
    approval_type: str = "",
    current_user: User = Depends(get_current_user)
):
    """List approval requests for the current user."""
    query = {"user_id": current_user.user_id}
    if status:
        query["status"] = status
    if approval_type:
        query["type"] = approval_type
    items = await db.approvals.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    pending_count = await db.approvals.count_documents({"user_id": current_user.user_id, "status": "draft"})
    return {"approvals": items, "pending_count": pending_count}


@router.get("/approvals/{approval_id}")
async def get_approval(approval_id: str, current_user: User = Depends(get_current_user)):
    """Get a single approval request."""
    doc = await db.approvals.find_one(
        {"approval_id": approval_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(404, "Approval not found")
    return doc


@router.post("/approvals/{approval_id}/approve")
async def approve_item(approval_id: str, current_user: User = Depends(get_current_user)):
    """Approve the content for publishing."""
    doc = await db.approvals.find_one(
        {"approval_id": approval_id, "user_id": current_user.user_id}
    )
    if not doc:
        raise HTTPException(404, "Approval not found")
    if doc["status"] not in ("draft", "revision_requested"):
        raise HTTPException(400, f"Cannot approve from status: {doc['status']}")

    now = datetime.now(timezone.utc).isoformat()
    await db.approvals.update_one(
        {"approval_id": approval_id},
        {"$set": {"status": "approved", "approved_at": now, "updated_at": now}}
    )
    await create_notification(
        current_user.user_id, "approval",
        f"Approved: {doc.get('title', 'Content')}",
        f"Your {doc.get('type', 'content')} has been approved and is ready to publish.",
        "/approvals"
    )
    return {"success": True, "status": "approved"}


@router.post("/approvals/{approval_id}/reject")
async def reject_item(
    approval_id: str,
    body: dict = Body(default={}),
    current_user: User = Depends(get_current_user)
):
    """Reject or request revision."""
    doc = await db.approvals.find_one(
        {"approval_id": approval_id, "user_id": current_user.user_id}
    )
    if not doc:
        raise HTTPException(404, "Approval not found")

    now = datetime.now(timezone.utc).isoformat()
    await db.approvals.update_one(
        {"approval_id": approval_id},
        {"$set": {
            "status": "revision_requested",
            "rejection_reason": body.get("reason", ""),
            "updated_at": now
        }}
    )
    return {"success": True, "status": "revision_requested"}


@router.post("/approvals/{approval_id}/publish")
async def publish_item(approval_id: str, current_user: User = Depends(get_current_user)):
    """Publish approved content (execute the action)."""
    doc = await db.approvals.find_one(
        {"approval_id": approval_id, "user_id": current_user.user_id}
    )
    if not doc:
        raise HTTPException(404, "Approval not found")
    if doc["status"] != "approved":
        raise HTTPException(400, "Content must be approved before publishing")

    now = datetime.now(timezone.utc).isoformat()
    await db.approvals.update_one(
        {"approval_id": approval_id},
        {"$set": {"status": "published", "published_at": now, "updated_at": now}}
    )
    await create_notification(
        current_user.user_id, "approval",
        f"Published: {doc.get('title', 'Content')}",
        f"Your {doc.get('type', 'content')} has been published successfully.",
        "/approvals"
    )
    return {"success": True, "status": "published"}


@router.delete("/approvals/{approval_id}")
async def delete_approval(approval_id: str, current_user: User = Depends(get_current_user)):
    """Delete an approval request."""
    result = await db.approvals.delete_one(
        {"approval_id": approval_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(404, "Approval not found")
    return {"success": True}
