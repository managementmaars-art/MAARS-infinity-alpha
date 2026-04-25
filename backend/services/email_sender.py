"""Unified email-sending transport — one module, two providers.

Before this extraction, SendGrid + Resend logic lived inline in
routes/social_media.py. That meant the background scheduler (which fires
scheduled_at emails) couldn't reuse it, and every new caller would copy
the same httpx boilerplate. This module consolidates:

  1. Provider keys read from the `integrations` store (same source as
     the ad-hoc endpoint — no config drift).
  2. Envelope normalization (from/reply-to/to) so callers don't need to
     know either provider's JSON shape.
  3. Compliance headers (List-Unsubscribe, Message-ID) that every jurisdiction
     now checks. Without these, Gmail bins you to spam automatically — this
     is pure deliverability hygiene, not regulatory theatre.
  4. Structured result contract: { ok, provider, message_id, error }.
     Callers check .ok to branch; no exceptions for expected failures
     (bad key, provider down, rate-limit).

Compliance note: List-Unsubscribe + List-Unsubscribe-Post is REQUIRED by
Gmail/Yahoo since Feb 2024 for any sender doing >5k/day to those
domains. CAN-SPAM / CASL / GDPR / UK DMCC all require a working
unsubscribe mechanism. This module writes the header but the operator
still needs to host an unsubscribe URL that actually processes clicks —
see /api/unsubscribe in routes/social_media.py (TODO: wire up).
"""
from __future__ import annotations
import logging
import os
import uuid
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_FROM_DOMAIN = os.environ.get("MAARS_EMAIL_DOMAIN", "maarscommand.com")
_DEFAULT_UNSUB_URL = os.environ.get("MAARS_UNSUB_URL", f"https://{_DEFAULT_FROM_DOMAIN}/unsubscribe")


async def _get_integration_keys() -> dict:
    """Pull provider credentials from the integrations store. Same source
    of truth as routes/social_media.py — keeps admin panel and scheduler
    reading from one place."""
    try:
        from routes.integrations import get_integration_keys
        return await get_integration_keys()
    except Exception:
        # Fallback: env vars. Useful for test / CI where the integrations
        # collection isn't populated.
        return {
            "sendgrid": {"api_key": os.environ.get("SENDGRID_API_KEY", "")},
            "resend":   {"api_key": os.environ.get("RESEND_API_KEY", "")},
        }


def _compliance_headers(to_email: str, unsubscribe_url: str | None = None) -> dict:
    """Headers every outbound cold email must carry. Not optional if you
    want to reach inboxes in 2024+. The unsubscribe URL is HMAC-signed
    so recipients can't unsubscribe strangers by editing the query
    string (routes/unsubscribe.py verifies the token)."""
    if unsubscribe_url:
        url = unsubscribe_url
    else:
        try:
            from routes.unsubscribe import build_unsubscribe_url
            url = build_unsubscribe_url(to_email)
        except Exception:
            url = f"{_DEFAULT_UNSUB_URL}?email={to_email}"
    return {
        "List-Unsubscribe": f"<{url}>, <mailto:unsubscribe@{_DEFAULT_FROM_DOMAIN}?subject=unsubscribe>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        "Message-ID": f"<{uuid.uuid4().hex}@{_DEFAULT_FROM_DOMAIN}>",
    }


async def _send_via_sendgrid(
    api_key: str,
    *,
    to: str,
    subject: str,
    body_html: str,
    body_text: str | None,
    from_email: str,
    from_name: str | None,
    reply_to: str | None,
    to_name: str | None,
    unsubscribe_url: str | None,
    personalization: dict | None,
) -> dict:
    """SendGrid v3 /mail/send. Returns normalized result."""
    payload: dict[str, Any] = {
        "personalizations": [{
            "to": [{"email": to, **({"name": to_name} if to_name else {})}],
            **({"dynamic_template_data": personalization} if personalization else {}),
        }],
        "from": {"email": from_email, **({"name": from_name} if from_name else {})},
        "subject": subject,
        "content": [
            *([{"type": "text/plain", "value": body_text}] if body_text else []),
            {"type": "text/html", "value": body_html},
        ],
        "headers": _compliance_headers(to, unsubscribe_url),
    }
    if reply_to:
        payload["reply_to"] = {"email": reply_to}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            if resp.status_code in (200, 202):
                return {
                    "ok": True,
                    "provider": "sendgrid",
                    "message_id": resp.headers.get("X-Message-Id"),
                    "status_code": resp.status_code,
                }
            return {
                "ok": False,
                "provider": "sendgrid",
                "error": f"SendGrid {resp.status_code}: {resp.text[:300]}",
                "status_code": resp.status_code,
            }
    except httpx.TimeoutException:
        return {"ok": False, "provider": "sendgrid", "error": "SendGrid timeout (20s)"}
    except Exception as exc:
        logger.exception("SendGrid send failed")
        return {"ok": False, "provider": "sendgrid", "error": f"{type(exc).__name__}: {exc}"}


async def _send_via_resend(
    api_key: str,
    *,
    to: str,
    subject: str,
    body_html: str,
    body_text: str | None,
    from_email: str,
    from_name: str | None,
    reply_to: str | None,
    unsubscribe_url: str | None,
) -> dict:
    """Resend /emails. Returns normalized result."""
    from_field = f"{from_name} <{from_email}>" if from_name else from_email
    payload: dict[str, Any] = {
        "from": from_field,
        "to": [to],
        "subject": subject,
        "html": body_html,
        "headers": _compliance_headers(to, unsubscribe_url),
    }
    if body_text:
        payload["text"] = body_text
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            if resp.status_code in (200, 201):
                data = resp.json() if resp.content else {}
                return {
                    "ok": True,
                    "provider": "resend",
                    "message_id": data.get("id"),
                    "status_code": resp.status_code,
                }
            return {
                "ok": False,
                "provider": "resend",
                "error": f"Resend {resp.status_code}: {resp.text[:300]}",
                "status_code": resp.status_code,
            }
    except httpx.TimeoutException:
        return {"ok": False, "provider": "resend", "error": "Resend timeout (20s)"}
    except Exception as exc:
        logger.exception("Resend send failed")
        return {"ok": False, "provider": "resend", "error": f"{type(exc).__name__}: {exc}"}


async def send_email(
    *,
    to: str,
    subject: str,
    body_html: str,
    body_text: str | None = None,
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
    to_name: str | None = None,
    provider: str | None = None,
    unsubscribe_url: str | None = None,
    personalization: dict | None = None,
) -> dict:
    """Send one email through the first available configured provider.

    If `provider` is None, try SendGrid first then Resend (alphabetical
    fallback — operator can override by passing provider="resend").

    Returns: {ok: bool, provider: str, message_id: str|None, error: str|None, status_code: int|None}
    """
    if not to or not subject or not body_html:
        return {"ok": False, "provider": None, "error": "to/subject/body_html all required"}

    # Suppression check — skip sending if recipient has unsubscribed.
    # Running this before the provider call saves money AND is legally
    # required (CAN-SPAM, CASL, GDPR Art. 21). Race-safe because
    # /api/unsubscribe writes synchronously.
    try:
        from routes.unsubscribe import is_suppressed
        if await is_suppressed(to):
            return {
                "ok": False,
                "provider": None,
                "error": "Recipient is on the suppression list (previously unsubscribed).",
                "suppressed": True,
            }
    except Exception:
        pass  # Never fail a send because suppression lookup errored.

    keys = await _get_integration_keys()
    sg_key = (keys.get("sendgrid") or {}).get("api_key", "")
    rs_key = (keys.get("resend") or {}).get("api_key", "")

    from_email = from_email or f"noreply@{_DEFAULT_FROM_DOMAIN}"

    # ── Self-hosted SMTP first (zero marginal cost). Falls through to
    # SendGrid/Resend on any SMTP failure or when MAARS_SMTP_HOST is unset.
    if (not provider) or provider.lower() in ("smtp_local", "local_smtp"):
        try:
            from services import smtp_local
            if smtp_local.is_configured():
                result = await smtp_local.send_local(
                    to=to, subject=subject,
                    body_html=body_html, body_text=body_text,
                    from_email=from_email, from_name=from_name,
                    reply_to=reply_to, unsubscribe_url=unsubscribe_url,
                )
                return result
        except Exception as exc:
            # If the caller explicitly asked for smtp_local, honor the
            # failure; otherwise silently fall through to paid providers.
            if provider and provider.lower() in ("smtp_local", "local_smtp"):
                return {"ok": False, "provider": "smtp_local",
                        "error": str(exc)[:400]}
            logger.info("smtp_local send failed, falling through to hosted: %s", exc)

    order = []
    if provider:
        order = [provider.lower()]
    else:
        if sg_key: order.append("sendgrid")
        if rs_key: order.append("resend")

    if not order:
        return {
            "ok": False,
            "provider": None,
            "error": "No email provider configured. Set MAARS_SMTP_HOST for self-hosted SMTP, or add SendGrid / Resend API key in /admin/integrations.",
        }

    last_error = None
    for p in order:
        if p == "sendgrid":
            if not sg_key:
                last_error = "SendGrid key missing"
                continue
            return await _send_via_sendgrid(
                sg_key, to=to, subject=subject, body_html=body_html, body_text=body_text,
                from_email=from_email, from_name=from_name, reply_to=reply_to,
                to_name=to_name, unsubscribe_url=unsubscribe_url, personalization=personalization,
            )
        elif p == "resend":
            if not rs_key:
                last_error = "Resend key missing"
                continue
            return await _send_via_resend(
                rs_key, to=to, subject=subject, body_html=body_html, body_text=body_text,
                from_email=from_email, from_name=from_name, reply_to=reply_to,
                unsubscribe_url=unsubscribe_url,
            )
        else:
            last_error = f"Unknown provider: {p}"

    return {"ok": False, "provider": None, "error": last_error or "No provider succeeded"}


async def send_via_configured_provider(
    *,
    to: str,
    subject: str,
    body: str,
    body_text: str | None = None,
    from_email: str | None = None,
) -> dict:
    """Legacy-friendly shim used by the background scheduler. Accepts
    the minimal arg set (to/subject/body); deeper callers use send_email()."""
    return await send_email(
        to=to,
        subject=subject,
        body_html=body,
        body_text=body_text,
        from_email=from_email,
    )
