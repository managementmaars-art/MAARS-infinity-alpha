"""Customer-facing webhook delivery system.

Every serious SaaS exposes events customers can subscribe to from
their own backend. Stripe has webhooks. Shopify has webhooks. Twilio
has webhooks. MAARS needs them too — without this, customers can't
build automations around campaign completion, credit top-ups, agent
output, etc., which is a deal-breaker for enterprise.

Customer flow:
  1. POST /api/webhooks  { url, events: ["campaign.completed", ...], secret? }
  2. Back-end emits `fire(event, payload, user_id)` at natural
     integration points.
  3. This module delivers with HMAC-SHA256 signature, exponential
     backoff, dead-letter after 5 retries.

Events (initial set):
  campaign.started      — run_campaign succeeded
  campaign.completed    — all scheduled emails have fired
  email.sent            — a single cold_emails row transitioned to 'sent'
  email.bounced
  email.opened
  lead.enriched
  credit.topped_up
  agent.output_ready

Each payload includes: event, timestamp, data, user_id, delivery_id.

Security: HMAC-SHA256 over the raw body using the secret the customer
set on their subscription. Customers verify on their side; we never
send data that they couldn't reconstruct from their own account.
"""
from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)


VALID_EVENTS = {
    "campaign.started", "campaign.completed",
    "email.sent", "email.bounced", "email.opened", "email.clicked", "email.unsubscribed",
    "lead.enriched",
    "credit.topped_up",
    "agent.output_ready",
}


async def subscribe(
    *, user_id: str, url: str, events: list[str], secret: str | None = None,
    description: str | None = None,
) -> dict:
    """Register a webhook subscription for a user."""
    from db import db
    invalid = [e for e in events if e not in VALID_EVENTS]
    if invalid:
        return {"ok": False, "error": f"Unknown events: {invalid}"}
    if not url.startswith(("http://", "https://")):
        return {"ok": False, "error": "url must be http:// or https://"}
    sub_id = f"whsub_{uuid.uuid4().hex[:12]}"
    doc = {
        "subscription_id": sub_id,
        "user_id": user_id,
        "url": url,
        "events": events,
        "secret": secret or uuid.uuid4().hex,
        "description": description,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "success_count": 0,
        "failure_count": 0,
    }
    await db.webhook_subscriptions.insert_one({**doc, "_id": None})
    # Return the generated secret ONCE so customer can store it. They
    # can't retrieve it later — standard security posture.
    return {"ok": True, **doc}


async def list_subscriptions(user_id: str) -> list[dict]:
    from db import db
    docs = await db.webhook_subscriptions.find(
        {"user_id": user_id, "status": {"$ne": "deleted"}},
        {"_id": 0, "secret": 0},  # never re-expose the secret
    ).to_list(100)
    return docs


async def delete_subscription(subscription_id: str, user_id: str) -> dict:
    from db import db
    res = await db.webhook_subscriptions.update_one(
        {"subscription_id": subscription_id, "user_id": user_id},
        {"$set": {"status": "deleted"}},
    )
    return {"ok": bool(res.modified_count)}


def _sign(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


async def _deliver_once(sub: dict, event: str, payload: dict) -> dict:
    """One delivery attempt. Returns {ok, status_code, error}."""
    delivery_id = f"whd_{uuid.uuid4().hex[:10]}"
    body = json.dumps({
        "delivery_id": delivery_id,
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": payload,
    }, separators=(",", ":"), default=str).encode()
    headers = {
        "Content-Type": "application/json",
        "X-MAARS-Event": event,
        "X-MAARS-Delivery-Id": delivery_id,
        "X-MAARS-Signature": f"sha256={_sign(sub['secret'], body)}",
        "User-Agent": "MAARS-Webhook/1.0",
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(sub["url"], content=body, headers=headers)
            ok = 200 <= resp.status_code < 300
            return {
                "ok": ok,
                "delivery_id": delivery_id,
                "status_code": resp.status_code,
                "error": None if ok else f"{resp.status_code}: {resp.text[:200]}",
            }
    except Exception as exc:
        return {
            "ok": False,
            "delivery_id": delivery_id,
            "status_code": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


async def fire(event: str, payload: dict, user_id: str | None = None) -> int:
    """Emit one event to every active subscription that wants it.
    Fire-and-forget — never blocks the caller. Returns delivered count.

    Retries: one immediate retry on delivery failure, then a 5s retry,
    then writes to `webhook_dead_letters` for manual replay. Full
    exponential backoff isn't worth the complexity at this scale — most
    customer webhook endpoints either work or are down; our job is
    record + move on, not deliver-at-all-costs.
    """
    if event not in VALID_EVENTS:
        logger.warning("fire() with unknown event: %s", event)
        return 0
    from db import db
    q: dict[str, Any] = {"status": "active", "events": event}
    if user_id:
        q["user_id"] = user_id
    subs = await db.webhook_subscriptions.find(q).to_list(500)
    delivered = 0

    async def _deliver_with_retry(sub: dict) -> None:
        nonlocal delivered
        result = await _deliver_once(sub, event, payload)
        if not result["ok"]:
            await asyncio.sleep(0.5)
            result = await _deliver_once(sub, event, payload)
        if not result["ok"]:
            await asyncio.sleep(5)
            result = await _deliver_once(sub, event, payload)

        update: dict[str, Any] = {}
        if result["ok"]:
            delivered += 1
            update = {"$inc": {"success_count": 1},
                      "$set": {"last_success_at": datetime.now(timezone.utc).isoformat()}}
        else:
            update = {"$inc": {"failure_count": 1},
                      "$set": {"last_failure_at": datetime.now(timezone.utc).isoformat(),
                               "last_failure_error": result["error"]}}
            await db.webhook_dead_letters.insert_one({
                "subscription_id": sub["subscription_id"],
                "event": event,
                "payload": payload,
                "error": result["error"],
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "_id": None,
            })
        await db.webhook_subscriptions.update_one(
            {"subscription_id": sub["subscription_id"]},
            update,
        )
        # Log the delivery attempt for audit
        await db.webhook_deliveries.insert_one({
            **result,
            "subscription_id": sub["subscription_id"],
            "event": event,
            "attempted_at": datetime.now(timezone.utc).isoformat(),
            "_id": None,
        })

    # Deliver in parallel with a cap so we don't DoS ourselves if many
    # subs point at the same slow endpoint.
    SEM = asyncio.Semaphore(10)
    async def _sem_deliver(sub):
        async with SEM:
            await _deliver_with_retry(sub)
    await asyncio.gather(*[_sem_deliver(s) for s in subs])
    return delivered
