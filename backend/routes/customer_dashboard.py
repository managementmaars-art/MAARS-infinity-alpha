"""Customer-facing dashboard endpoints.

Unlike /admin/* which shows operator truth, these return ONLY the
caller's own data — usage, campaigns, savings estimate — scrubbed of
backend identities so nothing leaks.

This is the #1 retention lever: when users log in tomorrow and see
"You saved $847 this month vs building this yourself", churn drops.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends

from auth import get_current_user
from models.schemas import User

router = APIRouter()


@router.get("/me/usage")
async def my_usage(current_user: User = Depends(get_current_user)):
    """Current billing cycle snapshot + 30-day rollup. Safe for clients
    (no provider names, no USD cost basis)."""
    from db import db
    uid = current_user.user_id
    now = datetime.now(timezone.utc)
    cycle_start = (now - timedelta(days=30)).isoformat()

    # Parallel-ish aggregations
    wallet = await db.wallets.find_one({"user_id": uid}, {"_id": 0}) or {}
    credits_used = await db.gateway_usage_logs.count_documents({
        "user_id": uid, "created_at": {"$gte": cycle_start},
    })

    # Campaign & outreach activity
    campaigns_all = await db.outbound_campaigns.count_documents({"user_id": uid})
    campaigns_active = await db.outbound_campaigns.count_documents({
        "user_id": uid, "status": {"$in": ["scheduled", "drafting", "running"]},
    })
    emails_sent = await db.cold_emails.count_documents({
        "user_id": uid, "status": {"$in": ["sent", "published"]},
    })
    emails_scheduled = await db.cold_emails.count_documents({
        "user_id": uid, "status": "scheduled",
    })
    # Deliverability aggregates via email_events
    event_agg = [
        {"$lookup": {
            "from": "cold_emails",
            "localField": "email",
            "foreignField": "to_email",
            "as": "owner",
        }},
        {"$match": {"owner.user_id": uid}},
        {"$group": {"_id": "$event_type", "n": {"$sum": 1}}},
    ]
    try:
        event_rows = await db.email_events.aggregate(event_agg).to_list(50)
    except Exception:
        event_rows = []
    events = {r["_id"]: r["n"] for r in event_rows}

    # Media generations (images, videos, TTS)
    images_made = await db.gateway_usage_logs.count_documents({
        "user_id": uid, "source": {"$regex": "image", "$options": "i"},
    })
    videos_made = await db.gateway_usage_logs.count_documents({
        "user_id": uid, "source": {"$regex": "video", "$options": "i"},
    })

    # Leads found
    try:
        leads_found = sum(1 for _ in [])  # scaffold — if you persist lead searches, count here
    except Exception:
        leads_found = 0

    # ROI estimate — conservative floor pricing operators would pay
    # DIY ($0.10/image industry avg, $0.40/video Sora, $0.02/lead Apollo).
    # We retail credits at $0.001 so the "savings" is intentionally
    # understated to avoid looking like we're inflating. Still shows
    # meaningful delta.
    diy_cost_usd = (
        images_made * 0.10 +
        videos_made * 0.40 +
        leads_found * 0.02 +
        emails_sent * 0.008  # SendGrid essentials ~$8/1K
    )
    # What the user actually paid us for this activity (credits × retail):
    credits_this_cycle = credits_used
    paid_cost_usd = credits_this_cycle * 0.001  # retail $/credit

    return {
        "cycle_start": cycle_start,
        "as_of": now.isoformat(),
        "credits": {
            "remaining": int(wallet.get("balance_credits", 0) or 0),
            "reserved": int(wallet.get("reserved_credits", 0) or 0),
            "used_this_cycle": credits_this_cycle,
        },
        "campaigns": {
            "total": campaigns_all,
            "active": campaigns_active,
        },
        "emails": {
            "sent": emails_sent,
            "scheduled": emails_scheduled,
            "opened": events.get("open") or events.get("opened") or 0,
            "clicked": events.get("click") or events.get("clicked") or 0,
            "bounced": events.get("bounce") or events.get("bounced") or 0,
        },
        "media": {
            "images_generated": images_made,
            "videos_generated": videos_made,
        },
        "leads": {
            "found": leads_found,
        },
        "savings_estimate": {
            "what_you_paid_usd": round(paid_cost_usd, 2),
            "what_diy_would_cost_usd": round(diy_cost_usd, 2),
            "savings_usd": round(max(0, diy_cost_usd - paid_cost_usd), 2),
            "multiplier": round(diy_cost_usd / paid_cost_usd, 1) if paid_cost_usd > 0 else None,
            "note": "Estimated at industry-standard per-unit prices vs MAARS credits.",
        },
    }


@router.get("/me/recent-activity")
async def my_recent_activity(current_user: User = Depends(get_current_user)):
    """Last 20 actions across all surfaces — for the dashboard activity
    feed."""
    from db import db
    uid = current_user.user_id
    activity: list[dict] = []

    try:
        for c in await db.outbound_campaigns.find({"user_id": uid}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5):
            activity.append({
                "type": "campaign",
                "at": c.get("created_at"),
                "label": f"Campaign: {c.get('name')}",
                "status": c.get("status"),
            })
    except Exception:
        pass

    try:
        for m in await db.messages.find({"user_id": uid}, {"_id": 0, "content": 0}).sort("created_at", -1).limit(10).to_list(10):
            activity.append({
                "type": "chat",
                "at": m.get("created_at"),
                "label": f"Chat with {m.get('agent_id', 'agent')}",
            })
    except Exception:
        pass

    activity.sort(key=lambda x: x.get("at") or "", reverse=True)
    return {"object": "list", "data": activity[:20]}
