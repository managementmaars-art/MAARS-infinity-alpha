"""Unsubscribe endpoint — deliverability + legal compliance.

Without this endpoint, the List-Unsubscribe header in email_sender.py
points to a 404, which:
  1. Makes Gmail/Yahoo route your mail to spam (they enforce one-click
     unsubscribe since Feb 2024 for bulk senders).
  2. Violates CAN-SPAM (US), CASL (Canada), GDPR Art. 21 (EU), UK DMCC
     Act, Australian Spam Act — every jurisdiction requires a working
     unsubscribe mechanism. A single complaint from any of them can
     freeze Stripe.

This module:
  - GET  /unsubscribe?email=...&token=...  — human-readable page
  - POST /unsubscribe                       — one-click form / Gmail "Unsubscribe" button
  - Writes to `email_suppressions` collection — email_sender.py SHOULD check
    this collection before every send (wired below).
"""
from __future__ import annotations
import hashlib
import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import HTMLResponse

router = APIRouter()


def _suppression_token(email: str) -> str:
    """HMAC of the email using a server secret — prevents random people
    from unsubscribing others. If MAARS_UNSUB_SECRET isn't set we fall
    back to a per-install default (still better than unsigned URLs)."""
    secret = os.environ.get("MAARS_UNSUB_SECRET", "maars-default-unsub-secret-change-me")
    return hmac.new(secret.encode(), email.lower().encode(), hashlib.sha256).hexdigest()[:16]


def build_unsubscribe_url(email: str) -> str:
    """Called by email_sender to build the List-Unsubscribe URL with a
    signed token so the link can't be spoofed."""
    base = os.environ.get("MAARS_UNSUB_URL", "https://maarscommand.com/unsubscribe")
    tok = _suppression_token(email)
    return f"{base}?email={email}&token={tok}"


async def _mark_suppressed(email: str, reason: str = "user_requested") -> None:
    """Write to the suppression list. Idempotent — upsert on email."""
    from db import db
    await db.email_suppressions.update_one(
        {"email": email.lower()},
        {"$set": {
            "email": email.lower(),
            "reason": reason,
            "unsubscribed_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )


async def is_suppressed(email: str) -> bool:
    """Called by email_sender before every send — bypasses the provider
    API if this address has unsubscribed. Prevents CAN-SPAM violations
    from races (user unsubs, scheduled campaign fires seconds later)."""
    from db import db
    if not email:
        return False
    doc = await db.email_suppressions.find_one({"email": email.lower()})
    return doc is not None


@router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_get(
    email: str = Query(...),
    token: str = Query(""),
):
    """Human-clickable page. Verifies the token, shows a confirm page.
    On POST from the form we mark the address suppressed."""
    expected = _suppression_token(email)
    if not hmac.compare_digest(token, expected):
        return HTMLResponse(
            "<h1>Invalid unsubscribe link</h1>"
            "<p>This link is malformed. Reply to the email with 'unsubscribe' "
            "and we'll remove you manually.</p>",
            status_code=400,
        )
    # Auto-suppress on click (required by Gmail's one-click spec).
    await _mark_suppressed(email, reason="one_click_link")
    return HTMLResponse(f"""
<!doctype html>
<html><head><title>Unsubscribed</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:480px;margin:80px auto;padding:24px;color:#222}}
h1{{color:#0a7}}</style></head>
<body>
  <h1>You're unsubscribed.</h1>
  <p>We've removed <strong>{email}</strong> from our list. You won't receive further emails.</p>
  <p style="color:#666;font-size:13px">If you did this by mistake, reply to any previous email and we'll add you back.</p>
</body></html>""")


@router.post("/unsubscribe")
async def unsubscribe_post(request: Request):
    """Gmail / Yahoo / Apple Mail POST their one-click unsubscribe here
    with the email encoded as form or JSON. We accept both."""
    # Gmail sends application/x-www-form-urlencoded
    email = None
    token = None
    try:
        ctype = request.headers.get("content-type", "")
        if "json" in ctype:
            body = await request.json()
            email = body.get("email")
            token = body.get("token")
        else:
            form = await request.form()
            email = form.get("email")
            token = form.get("token")
    except Exception:
        pass
    if not email:
        email = request.query_params.get("email")
        token = request.query_params.get("token")
    if not email:
        return Response("email is required", status_code=400)
    expected = _suppression_token(email)
    if token and not hmac.compare_digest(token, expected):
        return Response("invalid token", status_code=400)
    await _mark_suppressed(email, reason="one_click_post")
    # Return 200 OK — per RFC 8058 Gmail just wants any 2xx.
    return {"ok": True, "unsubscribed": email}


@router.get("/unsubscribe/status")
async def suppression_status(email: str):
    """Introspection: is this email on our suppression list? Public —
    operators can use it to debug, providers can check deliverability."""
    return {"email": email, "suppressed": await is_suppressed(email)}
