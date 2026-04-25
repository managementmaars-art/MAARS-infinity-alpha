"""Email event webhooks — bounce / open / click / spam-complaint ingestion.

SendGrid + Resend both post events to your backend URL in batches.
Without a handler, every hard bounce silently erodes your domain
reputation; by Day 30 Gmail routes everything to spam. This module:

  1. Accepts the provider's webhook payload (batched event array).
  2. Writes each event to `email_events` for analytics.
  3. Auto-suppresses email addresses on:
       - hard bounce (550, 5.x.x codes)
       - spam complaint (user clicked "mark as spam")
       - unsubscribe event
  4. Updates the originating cold_emails row so the UI shows "opened
     12 seconds after send" / "bounced" / "complained".

Setup (once per provider):
  SendGrid:  Settings → Mail Settings → Event Webhook → POST to
             https://YOUR_DOMAIN/api/email-events/sendgrid
             Enable: Delivered, Bounced, Blocked, Dropped, Spam Report,
             Unsubscribe, Open, Click.
  Resend:    Webhooks → Add Endpoint → POST to
             https://YOUR_DOMAIN/api/email-events/resend
             Events: email.delivered, email.bounced, email.complained,
             email.opened, email.clicked.

Signature verification is enforced when the corresponding signing-secret
env var is set:
  SendGrid   → SENDGRID_VERIFICATION_KEY (Ed25519 base64)
  Resend     → RESEND_WEBHOOK_SECRET     (HMAC-SHA256 hex)
When the env var is missing, the webhook falls open so dev can exercise
the pipeline without DNS tricks; prod deploys should always set these.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Signature verification helpers ──────────────────────────────────

def _verify_sendgrid_signature(public_key_b64: str, body: bytes, sig_b64: str, ts: str) -> bool:
    """Verify SendGrid's X-Twilio-Email-Event-Webhook-Signature.
    Uses Ed25519 over (timestamp + body). Returns False if cryptography
    isn't installed — caller decides what to do on missing dep."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        logger.warning("cryptography not installed — cannot verify SendGrid signature")
        return False
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        key.verify(base64.b64decode(sig_b64), (ts.encode() + body))
        return True
    except Exception as exc:
        logger.warning("sendgrid signature verify failed: %s", exc)
        return False


def _verify_resend_signature(secret: str, body: bytes, sig_hex: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, (sig_hex or "").strip())


async def _record_event(
    *,
    provider: str,
    event_type: str,
    email: str,
    raw: dict[str, Any],
    message_id: str | None = None,
) -> None:
    """Append to email_events + update originating cold_emails row."""
    from db import db
    from routes.unsubscribe import _mark_suppressed

    now = datetime.now(timezone.utc).isoformat()
    await db.email_events.insert_one({
        "provider": provider,
        "event_type": event_type,
        "email": email.lower() if email else None,
        "message_id": message_id,
        "received_at": now,
        "raw": raw,
    })

    # Update the cold_email row if we can find it by message_id or email
    if message_id:
        await db.cold_emails.update_one(
            {"provider_message_id": message_id},
            {"$push": {"events": {"type": event_type, "at": now}}},
        )
    elif email:
        # best-effort — find the most recent scheduled/sent row to this address.
        # Motor's update_one has no `sort` kwarg; do find_one → update_one by _id.
        recent = await db.cold_emails.find_one(
            {"to_email": email.lower(), "status": {"$in": ["sent", "scheduled"]}},
            sort=[("created_at", -1)],
            projection={"_id": 1},
        )
        if recent:
            await db.cold_emails.update_one(
                {"_id": recent["_id"]},
                {"$push": {"events": {"type": event_type, "at": now}}},
            )

    # Auto-suppress on events that mean "do not send to this address
    # again". This is how we avoid Stripe-killing complaints: one user
    # clicks 'mark as spam' → we never email them again, period.
    AUTO_SUPPRESS = {
        "bounce", "bounced", "hard_bounce",
        "dropped",
        "spam_report", "complained", "complaint",
        "unsubscribe", "unsubscribed",
        "blocked",
    }
    if email and event_type.lower() in AUTO_SUPPRESS:
        await _mark_suppressed(email, reason=f"webhook_{event_type}")

    # Bridge: fire our customer-webhook for common events so subscribed
    # customer backends can react in real time. Maps provider-specific
    # event names to our canonical event set.
    WEBHOOK_MAP = {
        "delivered": "email.sent",
        "open": "email.opened", "opened": "email.opened",
        "click": "email.clicked", "clicked": "email.clicked",
        "bounce": "email.bounced", "bounced": "email.bounced", "hard_bounce": "email.bounced",
        "unsubscribe": "email.unsubscribed", "unsubscribed": "email.unsubscribed",
    }
    canonical = WEBHOOK_MAP.get(event_type.lower())
    if canonical and email:
        try:
            from services.customer_webhooks import fire
            # Look up the user_id that owns this email via cold_emails
            owner = await db.cold_emails.find_one(
                {"to_email": email.lower()}, {"user_id": 1, "_id": 0},
            )
            await fire(canonical, {
                "to": email,
                "event": event_type,
                "provider": provider,
                "message_id": message_id,
            }, user_id=(owner or {}).get("user_id"))
        except Exception:
            pass

    # Notify the sending user on bounce or complaint — deliverability-
    # protective signal they can't afford to miss.
    if event_type.lower() in ("bounce", "hard_bounce", "complained", "complaint", "spam_report"):
        try:
            from routes.notifications_center import notify
            owner = await db.cold_emails.find_one(
                {"to_email": email.lower()}, {"user_id": 1, "_id": 0},
            )
            if owner and owner.get("user_id"):
                await notify(
                    owner["user_id"],
                    f"Email delivery issue: {event_type}",
                    body=f"{email} — {event_type}. We've added them to your suppression list automatically.",
                    kind="warn",
                    link="/admin/operations",
                )
        except Exception:
            pass


@router.post("/email-events/sendgrid")
async def sendgrid_events(request: Request):
    """SendGrid posts an array of events per delivery.
    https://docs.sendgrid.com/for-developers/tracking-events/event"""
    body_bytes = await request.body()
    pub_key = os.environ.get("SENDGRID_VERIFICATION_KEY")
    if pub_key:
        sig = request.headers.get("X-Twilio-Email-Event-Webhook-Signature", "")
        ts  = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp", "")
        if not _verify_sendgrid_signature(pub_key, body_bytes, sig, ts):
            raise HTTPException(401, "invalid_signature")
    try:
        import json as _json
        events = _json.loads(body_bytes or b"[]")
    except Exception:
        return {"ok": False, "error": "invalid json"}
    if not isinstance(events, list):
        events = [events]
    for ev in events:
        await _record_event(
            provider="sendgrid",
            event_type=ev.get("event", "unknown"),
            email=ev.get("email", ""),
            message_id=ev.get("sg_message_id") or ev.get("smtp-id"),
            raw=ev,
        )
    return {"ok": True, "processed": len(events)}


@router.post("/email-events/resend")
async def resend_events(request: Request):
    """Resend posts one event per request. Types include email.delivered,
    email.bounced, email.complained, email.opened, email.clicked.
    https://resend.com/docs/dashboard/webhooks/introduction"""
    body_bytes = await request.body()
    secret = os.environ.get("RESEND_WEBHOOK_SECRET")
    if secret:
        sig = request.headers.get("svix-signature") or request.headers.get("resend-signature") or ""
        if not _verify_resend_signature(secret, body_bytes, sig):
            raise HTTPException(401, "invalid_signature")
    try:
        import json as _json
        body = _json.loads(body_bytes or b"{}")
    except Exception:
        return {"ok": False, "error": "invalid json"}
    # Resend nests: { type: "email.bounced", data: { email_id, to, ... } }
    event_type = (body.get("type") or "").replace("email.", "")
    data = body.get("data", {})
    to = data.get("to")
    if isinstance(to, list):
        to = to[0] if to else ""
    await _record_event(
        provider="resend",
        event_type=event_type or "unknown",
        email=to or "",
        message_id=data.get("email_id"),
        raw=body,
    )
    return {"ok": True}


@router.post("/email-events/inbound")
async def inbound_email(request: Request):
    """Inbound-email endpoint — point SendGrid Inbound Parse, Resend
    Inbound, or Mailgun Route here.

    Fires any active workflow with `trigger.type == "email_reply"` whose
    filters match this reply. Ownership is resolved by finding the
    `cold_emails` row we originally sent to this address.

    Accepts multiple provider payload shapes — we normalize the three
    common fields (from, subject, body) and pass the rest through to
    the workflow as context.

    SendGrid Inbound Parse body is multipart/form-data with `from`,
    `subject`, `text`, `html`, `envelope`, `headers`, `dkim`, `SPF`.
    Resend inbound: { type: "email.received", data: { from, subject, text, ... } }.
    Mailgun: similar form-data to SendGrid.
    """
    content_type = (request.headers.get("content-type") or "").lower()
    from_email = ""
    subject = ""
    body_text = ""
    message_id = None
    raw_record: Any = {}

    try:
        if "application/json" in content_type:
            j = await request.json()
            raw_record = j
            # Resend shape
            data = j.get("data") if isinstance(j, dict) else None
            if data and (j.get("type") or "").lower() == "email.received":
                from_email = data.get("from", "") or ""
                subject = data.get("subject", "") or ""
                body_text = data.get("text") or data.get("html", "") or ""
                message_id = data.get("email_id")
            else:
                from_email = j.get("from", "") or j.get("sender", "") or ""
                subject = j.get("subject", "") or ""
                body_text = j.get("text", "") or j.get("body", "") or ""
                message_id = j.get("message_id") or j.get("Message-Id")
        else:
            form = await request.form()
            raw_record = {k: (str(v)[:2000] if v is not None else None) for k, v in form.items()}
            from_email = (form.get("from") or form.get("sender") or "") or ""
            subject = form.get("subject", "") or ""
            body_text = form.get("text") or form.get("html") or form.get("body-plain") or ""
            message_id = form.get("Message-Id") or form.get("message-id")
    except Exception as exc:
        logger.info("inbound_email parse failed: %s", exc)

    # Extract bare address if "Name <addr>" form.
    if "<" in from_email and ">" in from_email:
        try:
            from_email = from_email.split("<", 1)[1].split(">", 1)[0]
        except Exception:
            pass
    from_email = (from_email or "").strip().lower()

    # Persist as a generic email_event for auditability.
    await _record_event(
        provider="inbound",
        event_type="reply",
        email=from_email,
        message_id=message_id,
        raw=raw_record,
    )

    if not from_email:
        return {"ok": False, "error": "no from address"}

    # Resolve ownership: most recent cold_emails row whose to_email matches.
    from db import db
    owner = await db.cold_emails.find_one(
        {"to_email": from_email},
        sort=[("created_at", -1)],
        projection={"user_id": 1, "_id": 0},
    )
    if not owner or not owner.get("user_id"):
        return {"ok": True, "processed": False, "reason": "no matching outbound thread"}

    # Fire matching email_reply workflows.
    try:
        from services.workflows import workflow_executor
        run_ids = await workflow_executor.trigger_email_reply(
            user_id=owner["user_id"],
            from_email=from_email,
            subject=subject,
            body=body_text,
            message_id=message_id,
        )
    except Exception as exc:
        logger.warning("inbound email trigger failed: %s", exc)
        run_ids = []

    return {"ok": True, "processed": True, "run_ids": run_ids}


@router.get("/email-events/stats")
async def email_stats(user_id: str | None = None):
    """Quick deliverability view: last 30d counts per event type.
    Gives the operator an at-a-glance 'is my reputation OK?' signal."""
    from db import db
    match: dict[str, Any] = {}
    if user_id:
        # join through cold_emails → filter events by originating user
        owned = await db.cold_emails.find(
            {"user_id": user_id}, {"to_email": 1, "_id": 0}
        ).to_list(10000)
        emails_owned = [d["to_email"] for d in owned if d.get("to_email")]
        if emails_owned:
            match["email"] = {"$in": emails_owned}
    pipeline = [
        *([{"$match": match}] if match else []),
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    rows = await db.email_events.aggregate(pipeline).to_list(50)
    return {
        "object": "email_event_stats",
        "counts": {r["_id"]: r["count"] for r in rows},
    }
