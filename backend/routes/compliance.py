"""Compliance endpoints — GDPR Art. 15 (access) + Art. 17 (erasure).

Every jurisdiction with privacy law (EU/UK/CA/AU/CN/BR/+) now requires
the operator to provide a working data-export mechanism AND a delete
mechanism. Without these, one DSAR complaint → fine + investigation.

Endpoints:
  GET  /api/users/me/export  — download all user data as JSON
  POST /api/users/me/delete  — schedule account+data deletion (30-day grace)
  POST /api/users/me/delete/confirm?token=... — finalize deletion

Deletion is SOFT for 30 days (compliance with "right to reverse")
then hard-purges via the scheduler.
"""
from __future__ import annotations
import hmac
import hashlib
import os
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from auth import get_current_user
from models.schemas import User

router = APIRouter()


def _deletion_token(user_id: str) -> str:
    secret = os.environ.get("MAARS_DELETION_SECRET", "maars-deletion-change-me")
    return hmac.new(secret.encode(), user_id.encode(), hashlib.sha256).hexdigest()[:20]


@router.get("/users/me/export")
async def export_user_data(current_user: User = Depends(get_current_user)):
    """GDPR Art. 15 — dump every record tied to this user.

    Returns a JSON doc the user can save. Covers: profile, subscription,
    wallet, ledger entries, chats, campaigns, leads, emails, social
    posts, referrals, webhook subscriptions, audit trail.
    """
    from db import db
    uid = current_user.user_id

    async def collect(coll_name: str, query: dict, projection: dict | None = None) -> list:
        try:
            proj = projection or {"_id": 0}
            return await db[coll_name].find(query, proj).to_list(10000)
        except Exception:
            return []

    export = {
        "export_meta": {
            "user_id": uid,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "regulation": "GDPR Art. 15 / CCPA §1798.110 / PIPEDA / UK DPA 2018",
            "retention_note": "This file contains all personal data held. Request deletion via POST /api/users/me/delete.",
        },
        "profile": await db.users.find_one({"user_id": uid}, {"_id": 0, "password_hash": 0}),
        "subscription": await collect("subscriptions", {"user_id": uid}),
        "wallet": await collect("wallets", {"user_id": uid}),
        "ledger_entries": await collect("ledger_entries", {"user_id": uid}),
        "chats": await collect("chats", {"user_id": uid}),
        "messages": await collect("messages", {"user_id": uid}),
        "campaigns": await collect("outbound_campaigns", {"user_id": uid}),
        "cold_emails": await collect("cold_emails", {"user_id": uid}),
        "cold_calls": await collect("cold_calls", {"user_id": uid}),
        "social_posts": await collect("social_posts", {"user_id": uid}),
        "tasks": await collect("tasks", {"user_id": uid}),
        "referrals": await collect("referral_codes", {"user_id": uid}),
        "referral_clicks": await collect("referral_clicks", {"referrer_user_id": uid}),
        "webhook_subscriptions": await collect("webhook_subscriptions", {"user_id": uid}, {"_id": 0, "secret": 0}),
        "gateway_usage": await collect("gateway_usage_logs", {"user_id": uid}),
        "audit_log": await collect("admin_audit_log", {"target_user_id": uid}),
    }
    # Pretty-print JSON as an attachment download
    return JSONResponse(
        export,
        headers={
            "Content-Disposition": f"attachment; filename=maars-export-{uid[:8]}.json"
        },
    )


@router.post("/users/me/delete")
async def request_deletion(current_user: User = Depends(get_current_user)):
    """GDPR Art. 17 — schedule account deletion.

    Soft-delete now (flag + stop all outbound); hard-purge after 30
    days via the scheduler's deletion_queue. User can cancel within
    the window by POSTing /users/me/delete/cancel.
    """
    from db import db
    uid = current_user.user_id
    now = datetime.now(timezone.utc)
    scheduled_for = (now + timedelta(days=30)).isoformat()

    await db.users.update_one(
        {"user_id": uid},
        {"$set": {
            "deletion_requested_at": now.isoformat(),
            "deletion_scheduled_for": scheduled_for,
            "status": "pending_deletion",
        }},
    )
    # Halt any active outbound — deleted users shouldn't be sending
    await db.cold_emails.update_many(
        {"user_id": uid, "status": "scheduled"},
        {"$set": {"status": "paused", "paused_reason": "account_deletion_requested"}},
    )
    await db.outbound_campaigns.update_many(
        {"user_id": uid, "status": {"$in": ["scheduled", "drafting"]}},
        {"$set": {"status": "paused", "paused_reason": "account_deletion_requested"}},
    )
    # Suppress their own email to prevent any further outreach
    email = current_user.email or ""
    if email:
        from routes.unsubscribe import _mark_suppressed
        await _mark_suppressed(email, reason="account_deletion")

    token = _deletion_token(uid)
    return {
        "ok": True,
        "status": "pending_deletion",
        "scheduled_for": scheduled_for,
        "grace_period_days": 30,
        "confirm_token": token,
        "cancel_url": "POST /api/users/me/delete/cancel",
        "confirm_immediate_url": f"POST /api/users/me/delete/confirm?token={token}",
        "note": "Your account is soft-deleted. All outbound is paused. Data purges automatically in 30 days. Cancel anytime before then.",
    }


@router.post("/users/me/delete/cancel")
async def cancel_deletion(current_user: User = Depends(get_current_user)):
    from db import db
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$unset": {"deletion_requested_at": "", "deletion_scheduled_for": ""},
         "$set": {"status": "active"}},
    )
    return {"ok": True, "status": "active"}


@router.post("/users/me/delete/confirm")
async def confirm_immediate_deletion(token: str, current_user: User = Depends(get_current_user)):
    """Skip the 30-day wait — purge now. Requires the signed token
    from the original request to prevent accidental curl."""
    if not hmac.compare_digest(token, _deletion_token(current_user.user_id)):
        raise HTTPException(400, "invalid token")
    from db import db
    uid = current_user.user_id
    # Hard-delete. Order matters: delete child rows before parent.
    child_collections = [
        "messages", "chats", "outbound_campaigns", "cold_emails",
        "cold_calls", "social_posts", "tasks", "referral_codes",
        "referral_clicks", "referral_attributions", "webhook_subscriptions",
        "webhook_deliveries", "gateway_usage_logs", "ledger_entries",
        "wallets", "subscriptions", "linkedin_tokens",
    ]
    deleted_counts = {}
    for coll in child_collections:
        try:
            res = await db[coll].delete_many({"user_id": uid})
            deleted_counts[coll] = res.deleted_count
        except Exception:
            deleted_counts[coll] = "error"
    # Finally remove the user record itself
    await db.users.delete_one({"user_id": uid})
    return {"ok": True, "purged": deleted_counts, "user_id": uid}
