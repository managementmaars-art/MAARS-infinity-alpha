"""User stats and insights endpoints."""
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    chats_count = await db.chats.count_documents({"user_id": current_user.user_id})
    tasks_count = await db.tasks.count_documents({"user_id": current_user.user_id})
    completed_tasks = await db.tasks.count_documents({"user_id": current_user.user_id, "status": "completed"})
    custom_agents = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
    
    # Count total messages
    pipeline = [
        {"$match": {"user_id": current_user.user_id}},
        {"$project": {"message_count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$message_count"}}}
    ]
    messages_result = await db.chats.aggregate(pipeline).to_list(1)
    total_messages = messages_result[0]["total"] if messages_result else 0
    
    # Get user subscription info
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    credits_remaining = user_sub.get("credits", 50) if user_sub else 50
    plan = user_sub.get("plan_id", "free") if user_sub else "free"
    
    return {
        "total_chats": chats_count,
        "total_tasks": tasks_count,
        "completed_tasks": completed_tasks,
        "custom_agents": custom_agents,
        "total_messages": total_messages,
        "credits_remaining": credits_remaining,
        "plan": plan
    }

# ============== USER INSIGHTS DASHBOARD ==============

@router.get("/user/insights")
async def get_user_insights(current_user: User = Depends(get_current_user)):
    """Comprehensive usage insights for the current user."""
    uid = current_user.user_id
    now = datetime.now(timezone.utc)
    thirty_days_ago = (now - timedelta(days=30)).isoformat()

    # --- Basic stats ---
    user_chats = await db.chats.find({"user_id": uid}, {"_id": 0, "chat_id": 1, "agent_id": 1, "messages": 1, "created_at": 1}).to_list(1000)
    total_chats = len(user_chats)
    total_messages = sum(len(c.get("messages", [])) for c in user_chats)
    user_messages = sum(1 for c in user_chats for m in c.get("messages", []) if m.get("role") == "user")
    ai_messages = sum(1 for c in user_chats for m in c.get("messages", []) if m.get("role") == "assistant")

    # --- Credits ---
    user_sub = await db.subscriptions.find_one({"user_id": uid}, {"_id": 0})
    credits_remaining = user_sub.get("credits", 50) if user_sub else 50
    credits_used = user_sub.get("credits_used", 0) if user_sub else 0
    plan = user_sub.get("plan_id", "free") if user_sub else "free"

    # --- Favorite agents (most used) ---
    agent_count = {}
    for c in user_chats:
        aid = c.get("agent_id", "unknown")
        msg_count = len([m for m in c.get("messages", []) if m.get("role") == "assistant"])
        agent_count[aid] = agent_count.get(aid, 0) + msg_count

    all_agents = await db.agents.find({"is_active": {"$ne": False}}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1, "description": 1}).to_list(200)
    agent_map = {a["agent_id"]: a for a in all_agents}

    favorite_agents = sorted(agent_count.items(), key=lambda x: x[1], reverse=True)[:5]
    favorites = []
    for aid, count in favorite_agents:
        info = agent_map.get(aid, {})
        favorites.append({
            "agent_id": aid,
            "name": info.get("name", aid),
            "avatar": info.get("avatar", ""),
            "role": info.get("role", ""),
            "messages": count
        })

    # --- Agents not yet used (recommendations) ---
    used_agents = set(agent_count.keys())
    recommendations = []
    for a in all_agents:
        if a["agent_id"] not in used_agents and not a.get("is_commander"):
            recommendations.append({
                "agent_id": a["agent_id"],
                "name": a["name"],
                "avatar": a.get("avatar", ""),
                "role": a.get("role", ""),
                "description": a.get("description", ""),
            })
    # Limit recommendations
    recommendations = recommendations[:6]

    # --- Daily activity (last 30 days) ---
    daily_activity = {}
    for c in user_chats:
        for m in c.get("messages", []):
            ca = m.get("created_at", "")
            if ca and ca >= thirty_days_ago:
                day = ca[:10]
                daily_activity[day] = daily_activity.get(day, 0) + 1

    activity_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        activity_series.append({"date": d, "messages": daily_activity.get(d, 0)})

    # --- Feedback given ---
    feedback_up = 0
    feedback_down = 0
    for c in user_chats:
        for m in c.get("messages", []):
            fb = m.get("feedback")
            if fb == "up":
                feedback_up += 1
            elif fb == "down":
                feedback_down += 1

    # --- Streak (consecutive days with activity) ---
    streak = 0
    for i in range(30):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        if daily_activity.get(d, 0) > 0:
            streak += 1
        else:
            break

    return {
        "stats": {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "credits_remaining": credits_remaining,
            "credits_used": credits_used,
            "plan": plan,
            "feedback_up": feedback_up,
            "feedback_down": feedback_down,
            "streak": streak,
        },
        "favorite_agents": favorites,
        "recommendations": recommendations,
        "daily_activity": activity_series,
    }

