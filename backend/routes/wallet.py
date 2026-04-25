"""
User-facing wallet surface: /v1/credits, /v1/usage, /v1/api-keys.

These endpoints sit alongside the OpenAI-compatible gateway (routes/v1_gateway.py)
and expose the credits/wallet/usage state that the gateway already tracks.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth import get_current_user
from db import db
from models.schemas import User
from services import api_key_service
from services.billing import ledger_service, wallet_service
from services.billing.ledger_service import LedgerEntryType

router = APIRouter()


# --------------------------------------------------------------------------
# Credits — balance + reserved snapshot
# --------------------------------------------------------------------------

@router.get("/v1/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """Client-visible wallet summary.

    The UNIFIED client view is credits-based (see token_quota.py):
      credits_quota     — plan's period allowance (e.g. Creator = 50)
      credits_used      — credits consumed this period
      credits_remaining — what the client can still spend
      pct_used          — progress bar % for UI

    Internally MAARS tracks tokens (1 credit = 100k tokens by default)
    and per-modality buckets for operator analytics — those are NOT
    returned to the client. Admin/legacy buckets live on /admin/...

    The smart router picks the cheapest capable provider per call;
    the client spends from ONE pool regardless of which provider served.
    """
    summary = await wallet_service.get_summary(current_user.user_id)

    # Resolve plan for context (name, renewal date)
    sub = await db.subscriptions.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "plan_id": 1},
    ) or {}
    plan_id = sub.get("plan_id") or "free"

    # Primary: unified credit quota (single number for the UI)
    credits_view = {}
    try:
        from services.billing import token_quota
        from services.billing.plan_deliverables import LEGACY_TO_UNIFIED, PLAN_CATALOG
        q = await token_quota.get_quota(current_user.user_id)
        # Unified plan display name
        unified_id = LEGACY_TO_UNIFIED.get(plan_id, plan_id)
        plan_entry = next((p for p in PLAN_CATALOG if p["plan_id"] == unified_id), None)
        plan_name = (plan_entry or {}).get("name") or plan_id.title()
        credits_view = {
            "plan_id":            plan_id,
            "unified_plan_id":    unified_id,
            "plan_name":          plan_name,
            "credits_quota":      q["credits_quota"],
            "credits_used":       round(q["credits_quota"] - q["credits_remaining"], 2),
            "credits_remaining":  q["credits_remaining"],
            "pct_used":           q["pct_used"],
            "period_start":       q["period_start"],
            "period_end":         q["period_end"],
            "total_calls":        q["total_calls"],
        }
    except Exception as exc:
        logger.info("token_quota view skipped: %s", exc)

    # Legacy deliverables (optional, for gradual migration of older UI)
    try:
        from services.billing.plan_deliverables import user_plan_summary
        legacy_plan_view = user_plan_summary(
            plan_id, price_usd=0.0,
            wallet_buckets=summary.get("buckets") or {},
        )
    except Exception:
        legacy_plan_view = {"plan_id": plan_id, "deliverables": []}

    return {
        "object":   "credits",
        # PRIMARY client-visible fields
        "credits":  credits_view,
        # Legacy: full bucket summary + deliverables (admin/back-compat)
        "legacy": {
            "bucket_summary": summary,
            "plan":           legacy_plan_view,
        },
    }


# --------------------------------------------------------------------------
# Usage — recent ledger, newest first
# --------------------------------------------------------------------------

@router.get("/v1/usage/ledger")
async def get_usage_ledger(
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    entry_type: Optional[str] = Query(None, description="Filter: CREDIT|RESERVE|RELEASE|DEBIT|REFUND|ADJUSTMENT"),
    current_user: User = Depends(get_current_user),
):
    """Recent wallet/ledger activity for the authenticated user (complements /v1/usage, which is the gateway-spend summary keyed by API key)."""
    kind: Optional[LedgerEntryType] = None
    if entry_type:
        try:
            kind = LedgerEntryType(entry_type.upper())
        except ValueError:
            raise HTTPException(400, f"Invalid entry_type: {entry_type}")

    entries = await ledger_service.list_entries(
        user_id=current_user.user_id, limit=limit, skip=skip, entry_type=kind,
    )
    total = await ledger_service.count_entries(user_id=current_user.user_id, entry_type=kind)
    return {"object": "list", "data": entries, "total": total}


# --------------------------------------------------------------------------
# API keys — create / list / revoke
# --------------------------------------------------------------------------

class CreateApiKeyRequest(BaseModel):
    name: str = Field(default="default", max_length=80)


@router.post("/v1/api-keys")
async def create_api_key(
    payload: CreateApiKeyRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new MAARS API key for the caller. The raw key is returned ONCE;
    subsequent list calls expose only last4.
    """
    plan_id = "free"
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if sub:
        plan_id = sub.get("plan_id", "free")

    result = await api_key_service.create_key(
        current_user.user_id, name=payload.name, plan_id=plan_id,
    )
    # Expose the raw key separately so the caller is forced to acknowledge it.
    raw_key = result.pop("raw_key")
    return {"object": "api_key.created", "key": raw_key, "key_info": result}


@router.get("/v1/api-keys")
async def list_api_keys(current_user: User = Depends(get_current_user)):
    keys = await api_key_service.list_keys(current_user.user_id)
    return {"object": "list", "data": keys}


@router.delete("/v1/api-keys/{api_key_id}")
async def revoke_api_key(api_key_id: str, current_user: User = Depends(get_current_user)):
    ok = await api_key_service.revoke(api_key_id, current_user.user_id)
    if not ok:
        raise HTTPException(404, "API key not found or already revoked")
    return {"object": "api_key.revoked", "api_key_id": api_key_id, "revoked_at": datetime.now(timezone.utc).isoformat()}
