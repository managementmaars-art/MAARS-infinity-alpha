"""
Owner-only package configuration — read + edit subscription splits in-app.

Endpoints:
    GET   /admin/packages           current view (with overrides applied)
    POST  /admin/packages           upsert one or more package edits
    POST  /admin/packages/reset     wipe overrides; revert to code defaults

Editable fields per package:
    name, price_usd, credits, operator_share_pct (0.0 - 1.0)

Persisted in the existing `platform_config` collection so a backend restart
keeps your changes.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator

from auth import require_admin
from models.schemas import User
from services import customer_pricing_service
from services.billing import stripe_service

router = APIRouter()


class PackageEdit(BaseModel):
    name: Optional[str] = Field(None, max_length=80)
    price_usd: Optional[float] = Field(None, ge=0.0, le=100_000.0)
    credits: Optional[int] = Field(None, ge=0, le=10_000_000)
    operator_share_pct: Optional[float] = Field(None, ge=0.0, le=1.0)


class PackagesUpdate(BaseModel):
    updates: dict[str, PackageEdit] = Field(..., description="{ pkg_id: {field: value} }")

    @validator("updates")
    def at_least_one(cls, v):
        if not v:
            raise ValueError("updates must contain at least one package")
        return v


class CustomerOverride(BaseModel):
    package_id: str = Field(..., min_length=1, max_length=80)
    operator_share_pct: Optional[float] = Field(None, ge=0.0, le=1.0)
    price_usd: Optional[float] = Field(None, ge=0.0, le=100_000.0)
    credits_bonus: Optional[int] = Field(None, ge=0, le=10_000_000)
    notes: Optional[str] = Field("", max_length=500)
    expires_at: Optional[str] = Field(None, description="ISO timestamp; override stops applying after this")


@router.get("/admin/packages")
async def list_packages(_: User = Depends(require_admin)):
    """Current packages — defaults overlaid with any persisted overrides."""
    return {
        "object": "list",
        "data": stripe_service.list_packages(),
    }


@router.post("/admin/packages")
async def update_packages(body: PackagesUpdate, current: User = Depends(require_admin)):
    """
    Upsert package fields. Unknown fields are dropped; out-of-range values
    are rejected by Pydantic (operator_share_pct must be 0.0-1.0).

    New custom packages (any pkg_id not in defaults) require name + price_usd
    + credits the first time — additional fields can be added later.
    """
    updates_dict: dict[str, dict[str, Any]] = {}
    for pkg_id, edit in body.updates.items():
        clean = {k: v for k, v in edit.dict().items() if v is not None}
        if clean:
            updates_dict[pkg_id] = clean
    if not updates_dict:
        raise HTTPException(status_code=400, detail="No edits supplied (every field was None).")

    try:
        result = await stripe_service.apply_overrides(updates_dict, actor_id=current.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"object": "list", "data": result, "applied_to": list(updates_dict.keys())}


@router.delete("/admin/packages/{pkg_id}")
async def delete_package(pkg_id: str, current: User = Depends(require_admin)):
    """Remove a custom package. Default packages can't be deleted (use /reset)."""
    try:
        ok = await stripe_service.delete_package(pkg_id, actor_id=current.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=404, detail=f"Package '{pkg_id}' not found in overrides.")
    return {"deleted": pkg_id, "data": stripe_service.list_packages()}


@router.post("/admin/packages/reset")
async def reset_packages(current: User = Depends(require_admin)):
    result = await stripe_service.reset_overrides(actor_id=current.user_id)
    return {"object": "list", "data": result, "reset": True}


# ────────────────────────────────────────────── per-customer pricing

@router.get("/admin/customers/{user_id}/pricing")
async def get_customer_pricing(user_id: str, _: User = Depends(require_admin)):
    overrides = await customer_pricing_service.list_for_user(user_id)
    return {"object": "list", "user_id": user_id, "data": overrides}


@router.post("/admin/customers/{user_id}/pricing")
async def upsert_customer_pricing(
    user_id: str, body: CustomerOverride, current: User = Depends(require_admin),
):
    """Create or update a per-customer pricing override for a single package."""
    if not any([body.operator_share_pct is not None, body.price_usd is not None,
                body.credits_bonus is not None]):
        raise HTTPException(status_code=400, detail="At least one of operator_share_pct, price_usd, credits_bonus is required.")

    try:
        rec = await customer_pricing_service.upsert(
            user_id=user_id,
            package_id=body.package_id,
            operator_share_pct=body.operator_share_pct,
            price_usd=body.price_usd,
            credits_bonus=body.credits_bonus,
            notes=body.notes or "",
            expires_at=body.expires_at,
            actor_id=current.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Audit hook
    try:
        from governance.audit import log_action
        await log_action(
            action="customer_pricing_upsert",
            actor_type="admin",
            actor_id=current.user_id,
            target_type="user",
            target_id=user_id,
            details={"package_id": body.package_id, "fields": rec},
        )
    except Exception:
        pass

    return {"object": "customer_pricing_override", "user_id": user_id, "record": rec}


@router.delete("/admin/customers/{user_id}/pricing/{package_id}")
async def delete_customer_pricing(
    user_id: str, package_id: str, current: User = Depends(require_admin),
):
    ok = await customer_pricing_service.delete(user_id=user_id, package_id=package_id)
    if not ok:
        raise HTTPException(status_code=404, detail="No matching override.")
    try:
        from governance.audit import log_action
        await log_action(
            action="customer_pricing_delete", actor_type="admin", actor_id=current.user_id,
            target_type="user", target_id=user_id, details={"package_id": package_id},
        )
    except Exception:
        pass
    return {"deleted": True, "user_id": user_id, "package_id": package_id}


@router.get("/admin/customers/pricing")
async def list_all_customer_pricing(_: User = Depends(require_admin)):
    """Global view across every customer with an override (limit 200, newest first)."""
    return {"object": "list", "data": await customer_pricing_service.list_all(limit=200)}


# ────────────────────────────────────────────── audit trail (slice)

@router.get("/admin/packages/audit")
async def package_audit_trail(limit: int = 50, _: User = Depends(require_admin)):
    """Slice of audit_log filtered to package + customer pricing actions.
    Wrapped in defensive try/except — on an empty audit_log collection the
    underlying Mongo query can throw, which surfaces as a misleading
    'Load failed: Failed to execute text on Response' toast on the pricing
    manager page. Always return a well-formed list envelope."""
    from governance.audit import query_audit_log
    import logging
    _logger = logging.getLogger(__name__)
    combined = []
    for f in (
        {"target_type": "stripe_package"},
        {"action": "customer_pricing_upsert"},
        {"action": "customer_pricing_delete"},
    ):
        try:
            out = await query_audit_log(filters=f, limit=int(limit))
            combined.extend(out or [])
        except Exception as exc:
            _logger.warning("packages/audit query %s failed: %s", f, exc)
    combined.sort(key=lambda e: (e or {}).get("timestamp", ""), reverse=True)
    return {"object": "list", "data": combined[: int(limit)]}
