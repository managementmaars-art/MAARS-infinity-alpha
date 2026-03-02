"""Notification center endpoints."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Get user's notifications (newest first, last 50)."""
    notifs = await db.notifications.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    unread = sum(1 for n in notifs if not n.get("read"))
    return {"notifications": notifs, "unread_count": unread}

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user.user_id},
        {"$set": {"read": True}}
    )
    return {"success": result.modified_count > 0}

@router.post("/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user.user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

@router.delete("/notifications/clear")
async def clear_notifications(current_user: User = Depends(get_current_user)):
    await db.notifications.delete_many({"user_id": current_user.user_id, "read": True})
    return {"success": True}
