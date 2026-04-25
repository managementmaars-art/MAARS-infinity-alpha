"""
Setup wizard routes — /api/setup/*

Auth model:
    * If no users exist yet → unauthenticated access is allowed (first-run mode).
    * Otherwise → admin only.

After the wizard calls `POST /launch`, mutating endpoints become admin-only
even if the users collection is empty (defense in depth).
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from auth import get_current_user, security as _bearer_security
from db import db
from models.schemas import User
from services import setup_orchestrator as orch

router = APIRouter()


# ────────────────────────────────────────────────── auth dependency

async def setup_access(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_security),
) -> Optional[User]:
    """
    Allow if:
      (a) no users exist yet (first-run installer), OR
      (b) the caller is an authenticated admin.

    We resolve credentials via FastAPI's DI so the Authorization header (and
    cookie session) are properly parsed; a silent failure here would make the
    wizard 403 every admin post-launch.
    """
    first_run = await orch.is_first_run()
    state = await orch.get_state()
    finished = bool(state.get("finished_at"))

    user: Optional[User] = None
    try:
        user = await get_current_user(request, credentials=credentials)
    except HTTPException:
        user = None

    if user and getattr(user, "is_admin", False):
        return user
    if first_run and not finished:
        return None
    raise HTTPException(
        status_code=403,
        detail={"error": {"type": "setup_locked",
                          "message": "Setup is locked — sign in as admin to make changes."}},
    )


# ────────────────────────────────────────────────── reads

@router.get("/setup/status")
async def setup_status(_: Optional[User] = Depends(setup_access)):
    return await orch.get_state()


@router.get("/setup/report")
async def setup_report(_: Optional[User] = Depends(setup_access)):
    return await orch.build_report()


# ────────────────────────────────────────────────── system check

@router.post("/setup/check")
async def setup_check(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("system_check", status="running")
    ok, detail, meta = await orch.step_system_check()
    await orch.set_step("system_check", status="success" if ok else "failed", detail=detail, metadata=meta)
    return await orch.get_state()


# ────────────────────────────────────────────────── providers

class ProviderLinkRequest(BaseModel):
    provider: str = Field(..., description="openai | anthropic | groq | deepseek")


@router.post("/setup/providers/open-link")
async def providers_open_link(body: ProviderLinkRequest, _: Optional[User] = Depends(setup_access)):
    from services import provider_catalog
    entry = provider_catalog.get(body.provider)
    if entry is None:
        raise HTTPException(404, f"Unknown provider: {body.provider}")
    return {"provider": entry.slug, "name": entry.display_name, "url": entry.dashboard_url, "env_var": entry.env_var}


@router.get("/setup/providers/catalog")
async def providers_catalog(_: Optional[User] = Depends(setup_access)):
    """
    Full provider catalog with live detection state. The wizard renders Quick
    Setup from `quick=true` entries and Advanced Setup from the rest.
    """
    from services import provider_catalog
    state = await orch.get_state()
    detected = orch.detect_configured_providers()
    detected = orch.overlay_step_status(detected, state.get("steps", {}))
    quick    = [detected[p.slug] for p in provider_catalog.QUICK_PROVIDERS]
    advanced = [detected[p.slug] for p in provider_catalog.ADVANCED_PROVIDERS]
    return {
        "quick": quick,
        "advanced": advanced,
        "validation_strategies": list(provider_catalog.VALIDATION_STRATEGIES),
        "categories": list(provider_catalog.CATEGORIES),
        "totals": {"quick": len(quick), "advanced": len(advanced),
                   "configured": sum(1 for d in detected.values() if d["configured"])},
    }


class ProviderSaveRequest(BaseModel):
    provider: str
    api_key: str = Field(..., min_length=8, max_length=300)


@router.post("/setup/providers/save")
async def providers_save(body: ProviderSaveRequest, _: Optional[User] = Depends(setup_access)):
    step_id = f"provider_{body.provider}"
    await orch.set_step(step_id, status="running")
    ok, detail, meta = await orch.step_provider_save_and_test(body.provider, body.api_key)
    await orch.set_step(step_id, status="success" if ok else "failed", detail=detail, metadata=meta)
    state = await orch.get_state()
    return {"saved": ok, "detail": detail, "metadata": meta, "state": state}


class ProviderTestRequest(BaseModel):
    provider: str


@router.post("/setup/providers/test")
async def providers_test(body: ProviderTestRequest, _: Optional[User] = Depends(setup_access)):
    step_id = f"provider_{body.provider}"
    await orch.set_step(step_id, status="running")
    ok, detail, meta = await orch.step_provider_test_existing(body.provider)
    await orch.set_step(step_id, status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


# ────────────────────────────────────────────────── stripe

@router.post("/setup/stripe/open-link")
async def stripe_open_link(_: Optional[User] = Depends(setup_access)):
    return orch.STRIPE_LINK


class StripeSaveRequest(BaseModel):
    secret_key: str = Field(..., min_length=8, max_length=300)
    webhook_secret: str = Field("", max_length=300)


@router.post("/setup/stripe/save")
async def stripe_save(body: StripeSaveRequest, _: Optional[User] = Depends(setup_access)):
    await orch.set_step("stripe_keys", status="running")
    ok, detail, meta = await orch.step_stripe_save(body.secret_key, body.webhook_secret)
    await orch.set_step("stripe_keys", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"saved": ok, "detail": detail, "metadata": meta}


@router.post("/setup/stripe/test")
async def stripe_test(_: Optional[User] = Depends(setup_access)):
    """Re-validate whatever STRIPE_SECRET_KEY is currently in env."""
    import os
    sk = os.environ.get("STRIPE_SECRET_KEY", "")
    if not sk:
        await orch.set_step("stripe_keys", status="failed", detail="STRIPE_SECRET_KEY not set.")
        return {"ok": False, "detail": "STRIPE_SECRET_KEY not set."}
    ok, detail, meta = await orch.step_stripe_save(sk, os.environ.get("STRIPE_WEBHOOK_SECRET", ""))
    await orch.set_step("stripe_keys", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


# ────────────────────────────────────────────────── migrate / seed

@router.post("/setup/migrate")
async def migrate(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("migrate", status="running")
    ok, detail, meta = await orch.step_migrate()
    await orch.set_step("migrate", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


@router.post("/setup/seed")
async def seed(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("seed", status="running")
    ok, detail, meta = await orch.step_seed()
    await orch.set_step("seed", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


# ────────────────────────────────────────────────── tests

@router.post("/setup/test-routing")
async def test_routing(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("test_routing", status="running")
    ok, detail, meta = await orch.step_test_routing()
    await orch.set_step("test_routing", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


@router.post("/setup/test-wallet")
async def test_wallet(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("test_wallet", status="running")
    ok, detail, meta = await orch.step_test_wallet()
    await orch.set_step("test_wallet", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


@router.post("/setup/test-completion")
async def test_completion(_: Optional[User] = Depends(setup_access)):
    await orch.set_step("test_completion", status="running")
    ok, detail, meta = await orch.step_test_completion()
    await orch.set_step("test_completion", status="success" if ok else "failed", detail=detail, metadata=meta)
    return {"ok": ok, "detail": detail, "metadata": meta}


# ────────────────────────────────────────────────── launch

@router.post("/setup/launch")
async def launch(_: Optional[User] = Depends(setup_access)):
    report = await orch.build_report()
    if not report["launch_ready"]:
        raise HTTPException(
            status_code=409,
            detail={"error": {"type": "not_ready",
                              "message": "Setup is not yet launch-ready.",
                              "report": report}},
        )
    await orch.mark_finished()
    return {"launched": True, "report": await orch.build_report()}
