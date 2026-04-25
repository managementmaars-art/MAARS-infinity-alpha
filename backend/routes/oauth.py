"""Unified OAuth routes — one callback URL for every platform.

Flow:
  1. Client calls GET /oauth/{platform}/start → we generate a signed
     `state` token, stash any per-flow data (PKCE verifier for X/Twitter)
     in `db.oauth_states`, return an authorize URL for the user to visit.
  2. Platform redirects user back to GET /oauth/callback with `state`
     + `code`. We look up the platform from the state, exchange the
     code for tokens via the adapter, store the result in
     credential_vault, then redirect the user back to the frontend.

Callback URL registered with every provider:
    https://YOUR_DOMAIN/api/oauth/callback

Per-provider env vars:
    TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
    LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
    META_APP_ID, META_APP_SECRET
    TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET (or GOOGLE_CLIENT_ID/SECRET)

MAARS_OAUTH_REDIRECT_URI controls the callback; defaults to
`{MAARS_BASE_URL}/api/oauth/callback`.
MAARS_OAUTH_FRONTEND_RETURN controls where we send the user after a
successful exchange (default `/settings/integrations`).
"""
from __future__ import annotations
import logging
import os
import secrets
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse

from auth import get_current_user
from models.schemas import User

logger = logging.getLogger(__name__)
router = APIRouter()


def _callback_url() -> str:
    explicit = os.environ.get("MAARS_OAUTH_REDIRECT_URI")
    if explicit:
        return explicit
    base = os.environ.get("MAARS_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    return f"{base}/api/oauth/callback"


def _frontend_return() -> str:
    return os.environ.get("MAARS_OAUTH_FRONTEND_RETURN", "/settings/integrations")


@router.get("/oauth/{platform}/start")
async def oauth_start(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Begin an OAuth flow. Returns `{authorize_url, state}` — frontend
    navigates the user there."""
    from services.platforms import get_adapter
    from db import db
    adapter = get_adapter(platform)
    if adapter is None:
        raise HTTPException(404, f"unknown platform: {platform}")

    state = secrets.token_urlsafe(32)
    redirect_uri = _callback_url()

    verifier = None
    result = adapter.oauth_authorize_url(state=state, redirect_uri=redirect_uri)
    if isinstance(result, tuple):   # PKCE providers (X) return (url, verifier)
        url, verifier = result
    else:
        url = result

    await db.oauth_states.insert_one({
        "state": state,
        "platform": platform,
        "user_id": current_user.user_id,
        "verifier": verifier,
        "redirect_uri": redirect_uri,
        "created_at_epoch": time.time(),
        "_id": None,
    })
    return {"ok": True, "authorize_url": url, "state": state}


@router.get("/oauth/callback")
async def oauth_callback(
    state: str = Query(...),
    code: str | None = Query(None),
    error: str | None = Query(None),
    error_description: str | None = Query(None),
):
    """Single callback for every platform. State lookup tells us which
    adapter handles this exchange."""
    from db import db
    from services.platforms import get_adapter
    from services import credential_vault

    row = await db.oauth_states.find_one({"state": state})
    if not row:
        raise HTTPException(400, "invalid or expired state")
    # one-time use
    await db.oauth_states.delete_one({"state": state})

    if time.time() - row.get("created_at_epoch", 0) > 900:   # 15 min
        raise HTTPException(400, "state expired — restart OAuth")

    if error:
        return RedirectResponse(
            f"{_frontend_return()}?oauth_error={error}&desc={error_description or ''}"
        )
    if not code:
        raise HTTPException(400, "missing code")

    platform = row["platform"]
    adapter = get_adapter(platform)
    if adapter is None:
        raise HTTPException(404, f"unknown platform: {platform}")

    try:
        tok = await adapter.oauth_exchange(
            code=code,
            redirect_uri=row["redirect_uri"],
            verifier=row.get("verifier"),
        )
    except Exception as exc:
        logger.warning("oauth exchange failed for %s: %s", platform, exc)
        return RedirectResponse(
            f"{_frontend_return()}?oauth_error=exchange_failed&platform={platform}"
        )

    await credential_vault.put(credential_vault.Credential(
        scope="user",
        scope_id=row["user_id"],
        provider=platform,
        kind="oauth",
        secret=tok["secret"],
        refresh_secret=tok.get("refresh_secret"),
        expires_at=tok.get("expires_at"),
        public=tok.get("public") or {},
        metadata=tok.get("metadata") or {},
    ))

    return RedirectResponse(
        f"{_frontend_return()}?oauth_ok=1&platform={platform}"
    )


@router.get("/oauth/{platform}/status")
async def oauth_status(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Is this user currently connected to this platform?"""
    from services import credential_vault
    cred = await credential_vault.get(
        platform, user_id=current_user.user_id, kind="oauth",
        auto_refresh=False,
    )
    if cred is None:
        return {"connected": False}
    return {
        "connected": True,
        "platform": platform,
        "public": cred.public,
        "expires_at": cred.expires_at,
        "expires_in_s": int((cred.expires_at or 0) - time.time()) if cred.expires_at else None,
    }


@router.delete("/oauth/{platform}")
async def oauth_disconnect(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    from services import credential_vault
    ok = await credential_vault.delete(
        platform, user_id=current_user.user_id, kind="oauth",
    )
    return {"ok": ok, "platform": platform}


@router.get("/oauth/connections")
async def oauth_connections(current_user: User = Depends(get_current_user)):
    """List every platform the current user is connected to."""
    from services import credential_vault
    rows = await credential_vault.list_for(user_id=current_user.user_id)
    return {"object": "list", "data": [r for r in rows if r["kind"] == "oauth"]}
