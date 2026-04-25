"""Inbound webhook triggers for workflows — replaces "Zapier Catch Hook".

A workflow with `trigger.type == "webhook"` can be fired by any external
system that POSTs JSON to:

    POST https://YOUR_DOMAIN/api/webhooks/workflow/{workflow_id}

If the workflow's trigger defines a `signing_secret`, callers must
include header `X-MAARS-Signature: <hex_hmac_sha256>` where the HMAC
is computed over the raw request body. Without a signing_secret the
endpoint is open (publicly triggerable by workflow_id alone).

Each hit enqueues one run. Scheduler's `_workflow_tick` picks it up
within ~20s. The payload is passed to the first node's `input` as
`overrides.webhook_payload`.

Why this exists:
  Zapier's "Catch Hook" let other services trigger Zaps with a POST.
  We replaced Zapier; this endpoint covers the same role natively.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter()


def _verify_signature(secret: str, raw: bytes, provided: str | None) -> bool:
    if not secret:
        return True   # no secret set = no verification
    if not provided:
        return False
    mac = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, provided)


@router.post("/webhooks/workflow/{workflow_id}")
async def trigger_workflow_webhook(workflow_id: str, request: Request):
    """Fire an active workflow via inbound webhook.

    Returns {ok, run_id} on success, 401/403 on signature fail, 404 on
    bad id, 400 on malformed body.
    """
    raw = await request.body()
    try:
        payload: dict[str, Any] = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        raise HTTPException(400, "invalid JSON body")

    from db import db
    from services.workflows import workflow_executor
    wf = await db.workflows.find_one({"workflow_id": workflow_id, "active": True})
    if not wf:
        raise HTTPException(404, "workflow not found or inactive")

    trig = wf.get("trigger") or {}
    if trig.get("type") != "webhook":
        raise HTTPException(400, "workflow trigger type is not 'webhook'")

    # Signature check
    provided_sig = request.headers.get("x-maars-signature") or request.headers.get("X-MAARS-Signature")
    secret = str(trig.get("signing_secret") or "")
    if secret and not _verify_signature(secret, raw, provided_sig):
        raise HTTPException(401, "signature mismatch")

    result = await workflow_executor.trigger_webhook(
        workflow_id, payload=payload, signing_ok=True,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "trigger failed"))
    return {"ok": True, "run_id": result["run_id"]}


@router.api_route("/webhooks/resume/{token}", methods=["GET", "POST"])
async def resume_wait_token(token: str, request: Request):
    """Resume a paused workflow: fires when a wait_for_webhook or
    approval node receives its trigger.

    Query params or JSON body become the resume payload. The special
    query param `decision=approved|rejected` drives approval nodes.
    """
    from db import db
    doc = await db.workflow_wait_tokens.find_one({"token": token})
    if not doc:
        raise HTTPException(404, "token not found")
    if doc.get("resolved"):
        return {"ok": False, "error": "already resolved"}
    if doc.get("expires_at") and doc["expires_at"] < time.time():
        await db.workflow_wait_tokens.update_one({"token": token}, {"$set": {"expired": True, "resolved": True}})
        raise HTTPException(410, "token expired")

    payload: dict[str, Any] = dict(request.query_params)
    if request.method == "POST":
        try:
            body = await request.json()
            if isinstance(body, dict):
                payload.update(body)
        except Exception:
            pass

    await db.workflow_wait_tokens.update_one(
        {"token": token},
        {"$set": {"resolved": True, "resolved_at": time.time(), "payload": payload}},
    )
    kind = doc.get("kind", "wait")
    decision = payload.get("decision", "approved") if kind == "approval" else None
    return {"ok": True, "kind": kind, "decision": decision, "resumed": True}


@router.get("/webhooks/workflow/{workflow_id}")
async def inbound_webhook_info(workflow_id: str):
    """Returns the inbound webhook URL + signature requirement so the UI
    can show users where to point their external system."""
    from db import db
    wf = await db.workflows.find_one(
        {"workflow_id": workflow_id},
        {"_id": 0, "workflow_id": 1, "name": 1, "trigger": 1, "active": 1},
    )
    if not wf:
        raise HTTPException(404, "workflow not found")
    trig = wf.get("trigger") or {}
    return {
        "workflow_id": workflow_id,
        "active": wf.get("active"),
        "trigger_type": trig.get("type"),
        "url_hint": f"/api/webhooks/workflow/{workflow_id}",
        "requires_signature": bool(trig.get("signing_secret")),
        "signature_header": "X-MAARS-Signature" if trig.get("signing_secret") else None,
        "signature_algorithm": "HMAC-SHA256 over raw request body" if trig.get("signing_secret") else None,
    }
