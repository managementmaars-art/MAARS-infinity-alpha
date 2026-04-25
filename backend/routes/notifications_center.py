"""In-app notification center — bell icon, unread count, mark-read.

Used by the frontend NotificationBell component. Backing collection
has indexes on (user_id, created_at DESC) and (user_id, read) for
the hot queries.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


class NotifyInternal(BaseModel):
    """Shape for programmatic notification creation by other services."""
    user_id: str
    title: str
    body: str | None = None
    kind: str = "info"          # info | success | warn | danger
    link: str | None = None     # in-app link to jump to
    icon: str | None = None     # lucide icon name


async def notify(user_id: str, title: str, *, body: str | None = None,
                 kind: str = "info", link: str | None = None,
                 icon: str | None = None) -> dict:
    """Fire a notification to one user. Called by services (e.g. when
    a campaign completes, a referral converts, credits run low)."""
    from db import db
    doc = {
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "title": title,
        "body": body,
        "kind": kind,
        "link": link,
        "icon": icon,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.notifications.insert_one({**doc, "_id": None})
    return doc


@router.get("/notifications")
async def list_notifications(
    limit: int = 50, unread_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    from db import db
    q: dict = {"user_id": current_user.user_id}
    if unread_only:
        q["read"] = False
    docs = await db.notifications.find(q, {"_id": 0}).sort("created_at", -1).limit(max(1, min(limit, 100))).to_list(limit)
    unread = await db.notifications.count_documents({"user_id": current_user.user_id, "read": False})
    return {"object": "list", "data": docs, "unread_count": unread}


@router.post("/notifications/{notification_id}/read")
async def mark_read(notification_id: str, current_user: User = Depends(get_current_user)):
    from db import db
    res = await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user.user_id},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"ok": bool(res.modified_count)}


@router.post("/notifications/mark-all-read")
@router.post("/notifications/read-all")     # legacy path kept for NotificationCenter.jsx
async def mark_all_read(current_user: User = Depends(get_current_user)):
    from db import db
    res = await db.notifications.update_many(
        {"user_id": current_user.user_id, "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"ok": True, "updated_count": res.modified_count}


@router.delete("/notifications/clear")
async def clear_read_notifications(current_user: User = Depends(get_current_user)):
    """Delete all already-read notifications for this user."""
    from db import db
    res = await db.notifications.delete_many(
        {"user_id": current_user.user_id, "read": True},
    )
    return {"ok": True, "deleted": int(getattr(res, "deleted_count", 0) or 0)}
