"""
Operator/admin control surface over user wallets and ledger.

Closes the Phase-7 admin-wallet gaps flagged in audit 010:
    GET  /admin/users/{user_id}/wallet
    GET  /admin/users/{user_id}/ledger
    POST /admin/wallets/{user_id}/adjust
    GET  /admin/ledger/recent
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth import require_admin
from db import db
from models.schemas import User
from services.billing import ledger_service, wallet_service
from services.billing.ledger_service import LedgerEntryType

router = APIRouter()


@router.get("/admin/users/{user_id}/wallet")
async def admin_get_wallet(user_id: str, _: User = Depends(require_admin)):
    """Full operator view of a user's wallet state."""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(404, "User not found")
    summary = await wallet_service.get_summary(user_id)
    sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    return {
        "user": user,
        "wallet": summary,
        "subscription": sub,
    }


@router.get("/admin/users/{user_id}/ledger")
async def admin_get_ledger(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    entry_type: Optional[str] = Query(None),
    _: User = Depends(require_admin),
):
    kind: Optional[LedgerEntryType] = None
    if entry_type:
        try:
            kind = LedgerEntryType(entry_type.upper())
        except ValueError:
            raise HTTPException(400, f"Invalid entry_type: {entry_type}")

    entries = await ledger_service.list_entries(
        user_id=user_id, limit=limit, skip=skip, entry_type=kind,
    )
    total = await ledger_service.count_entries(user_id=user_id, entry_type=kind)
    return {"object": "list", "data": entries, "total": total}


class WalletAdjustRequest(BaseModel):
    delta: int = Field(..., description="Positive = grant, negative = claw-back")
    reason: str = Field(..., min_length=1, max_length=500)
    reference_id: Optional[str] = None


@router.post("/admin/wallets/{user_id}/adjust")
async def admin_adjust_wallet(
    user_id: str,
    payload: WalletAdjustRequest,
    admin_user: User = Depends(require_admin),
):
    """Operator-initiated wallet adjustment. Logged with actor_id for audit."""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(404, "User not found")

    summary = await wallet_service.adjust(
        user_id,
        payload.delta,
        actor_id=admin_user.user_id,
        reason=payload.reason,
        reference_id=payload.reference_id,
    )
    return {"object": "wallet.adjusted", "wallet": summary, "delta_applied": payload.delta}


@router.get("/admin/ledger/recent")
async def admin_recent_ledger(
    limit: int = Query(100, ge=1, le=500),
    entry_type: Optional[str] = Query(None),
    _: User = Depends(require_admin),
):
    """Global recent ledger activity — operator view."""
    query: dict = {}
    if entry_type:
        try:
            query["type"] = LedgerEntryType(entry_type.upper()).value
        except ValueError:
            raise HTTPException(400, f"Invalid entry_type: {entry_type}")

    cursor = db[ledger_service.LEDGER_COLLECTION].find(query, {"_id": 0}) \
        .sort("created_at", -1).limit(limit)
    data = [doc async for doc in cursor]
    return {"object": "list", "data": data}
