"""Admin routes for the Provider Onboarding flow.

Surfaces the unconfigured-provider list, opens signup browser sessions,
triggers DOM-based key extraction, and supports a paste-in fallback when
the extraction doesn't match the provider's dashboard layout.

All routes require admin auth.
"""
from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import require_admin
from models.schemas import User

router = APIRouter()


@router.get("/admin/providers/onboarding")
async def list_unconfigured(
    all: bool = False,
    _: User = Depends(require_admin),
):
    """List providers needing API keys (default) or every registered
    onboardable provider when `all=true`."""
    from services import provider_onboarding
    return {
        "providers": provider_onboarding.list_providers(unconfigured_only=not all),
        "count":     len(provider_onboarding.list_providers(unconfigured_only=not all)),
    }


class _StartBody(BaseModel):
    provider: str


@router.post("/admin/providers/onboarding/start")
async def start_onboarding(body: _StartBody, current_user: User = Depends(require_admin)):
    """Open the provider's signup page in the in-app BrowserPanel.
    Returns a session_id the frontend redirects to /browser?session=X."""
    from services import provider_onboarding
    res = await provider_onboarding.start_session(body.provider, current_user.user_id)
    if not res.get("ok"):
        raise HTTPException(400, res.get("error") or "start_failed")
    return res


class _GrabBody(BaseModel):
    provider: str
    session_id: str


@router.post("/admin/providers/onboarding/grab-key")
async def grab_key(body: _GrabBody, current_user: User = Depends(require_admin)):
    """After operator is signed in, DOM-scrape the API key from the
    provider's keys page and persist to vault + .env."""
    from services import provider_onboarding
    res = await provider_onboarding.grab_key(body.provider, current_user.user_id, body.session_id)
    if not res.get("ok"):
        raise HTTPException(400, res.get("error") or "grab_failed")
    return res


class _PasteBody(BaseModel):
    provider: str
    api_key: str


@router.post("/admin/providers/onboarding/paste")
async def paste_key(body: _PasteBody, current_user: User = Depends(require_admin)):
    """Manual fallback: operator pastes the key from the provider
    dashboard. Same persistence as grab-key."""
    from services import provider_onboarding
    res = await provider_onboarding.save_key(body.provider, current_user.user_id, body.api_key)
    if not res.get("ok"):
        raise HTTPException(400, res.get("error") or "paste_failed")
    return res
