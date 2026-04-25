"""LinkedIn posting adapter — Community Management API.

To activate:
  1. Register an app at https://www.linkedin.com/developers/apps
     - Product: "Community Management API" (requires approval for posting
       as a company page) OR "Share on LinkedIn" (personal posts,
       no approval needed for individual members).
     - OAuth redirect URL: your backend `/auth/linkedin/callback`.
  2. Capture CLIENT_ID + CLIENT_SECRET in env:
        LINKEDIN_CLIENT_ID=...
        LINKEDIN_CLIENT_SECRET=...
        LINKEDIN_REDIRECT_URI=https://.../auth/linkedin/callback
  3. Each user that wants to post runs through OAuth and the access
     token lands in `linkedin_tokens` collection keyed by user_id.

Until step 1 is done, `post_text()` returns {"ok": False, "error":
"LinkedIn not configured — register app at ..."} so the scheduler
records a clear failure instead of sitting in eternal "scheduled".

LinkedIn API docs: https://learn.microsoft.com/en-us/linkedin/marketing/
"""
from __future__ import annotations
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_LI_API_BASE = "https://api.linkedin.com"
_LI_AUTH_BASE = "https://www.linkedin.com/oauth/v2"


def is_configured() -> bool:
    return bool(os.environ.get("LINKEDIN_CLIENT_ID") and os.environ.get("LINKEDIN_CLIENT_SECRET"))


async def _get_user_token(user_id: str) -> str | None:
    """Load the stored OAuth access token for this MAARS user. Returns
    None if the user hasn't completed LinkedIn OAuth yet. Auto-refreshes
    when the stored token is within 7 days of expiry (LI access tokens
    last 60 days; refresh tokens last a year)."""
    try:
        from db import db
        doc = await db.linkedin_tokens.find_one({"user_id": user_id})
        if not doc:
            return None
        tok = doc.get("access_token")
        # Auto-refresh if expires_at is set and within 7 days
        import time as _t
        exp = doc.get("expires_at")
        if exp and isinstance(exp, (int, float)) and (exp - _t.time()) < 7 * 86400:
            refresh_tok = doc.get("refresh_token")
            if refresh_tok:
                refreshed = await _refresh_access_token(refresh_tok)
                if refreshed.get("ok"):
                    new_token = refreshed.get("access_token")
                    new_exp = _t.time() + int(refreshed.get("expires_in", 5_184_000))
                    await db.linkedin_tokens.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "access_token": new_token,
                            "expires_at":   new_exp,
                            "refresh_token": refreshed.get("refresh_token") or refresh_tok,
                            "refreshed_at": _t.time(),
                        }},
                    )
                    logger.info("linkedin token refreshed for user %s", user_id[:8])
                    return new_token
                logger.warning("linkedin refresh failed: %s", refreshed.get("error"))
        return tok
    except Exception:
        logger.exception("linkedin token lookup failed")
        return None


async def _refresh_access_token(refresh_token: str) -> dict:
    """Trade refresh_token for a new access_token. Called proactively
    when the existing token is within 7 days of expiry, or reactively
    after a 401."""
    data = {
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
        "client_id":     os.environ.get("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{_LI_AUTH_BASE}/accessToken", data=data)
        if resp.status_code == 200:
            return {"ok": True, **resp.json()}
        return {"ok": False, "error": f"{resp.status_code}: {resp.text[:300]}"}


def authorize_url(state: str) -> str:
    """Build the LinkedIn consent URL. Frontend redirects the user here
    to start OAuth. `state` is an opaque token to prevent CSRF."""
    cid = os.environ.get("LINKEDIN_CLIENT_ID", "")
    redirect = os.environ.get("LINKEDIN_REDIRECT_URI", "")
    scope = "r_liteprofile w_member_social"  # post + read profile
    return (
        f"{_LI_AUTH_BASE}/authorization"
        f"?response_type=code&client_id={cid}"
        f"&redirect_uri={redirect}&state={state}&scope={scope}"
    )


async def exchange_code_for_token(code: str) -> dict:
    """Trade the OAuth `code` from the callback for an access_token.
    Store the result in `linkedin_tokens` keyed by user_id (caller does
    that — this function just returns the token dict).

    Adds `expires_at` (epoch seconds) to the returned dict so callers
    can persist it for the refresh path in `get_access_token()`."""
    import time as _t
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ.get("LINKEDIN_REDIRECT_URI", ""),
        "client_id": os.environ.get("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{_LI_AUTH_BASE}/accessToken", data=data)
        if resp.status_code == 200:
            payload = resp.json()
            # LinkedIn returns expires_in in seconds (typically 5184000 = 60d)
            expires_in = int(payload.get("expires_in", 5_184_000))
            payload["expires_at"] = _t.time() + expires_in
            return {"ok": True, **payload}
        return {"ok": False, "error": f"{resp.status_code}: {resp.text[:300]}"}


async def persist_linkedin_tokens(
    *, user_id: str, token_payload: dict,
) -> None:
    """Helper used by the OAuth callback route — stores tokens + expiry
    in the shape `get_access_token()` expects for auto-refresh."""
    from db import db
    import time as _t
    await db.linkedin_tokens.update_one(
        {"user_id": user_id},
        {"$set": {
            "access_token":  token_payload.get("access_token"),
            "refresh_token": token_payload.get("refresh_token"),
            "expires_at":    token_payload.get("expires_at") or (_t.time() + 5_184_000),
            "scope":         token_payload.get("scope"),
            "updated_at":    _t.time(),
        }},
        upsert=True,
    )


async def _get_person_urn(access_token: str) -> str | None:
    """LinkedIn's post API requires the author as a URN like
    `urn:li:person:<id>`. Fetch the current user's id via /me."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{_LI_API_BASE}/v2/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code == 200:
            return f"urn:li:person:{resp.json().get('id')}"
        return None


async def post_text(user_id: str, text: str, visibility: str = "PUBLIC") -> dict:
    """Publish a plain-text post as the authenticated user.

    Returns normalized result: {ok, post_id, error}.
    """
    if not is_configured():
        return {
            "ok": False,
            "error": "LinkedIn app not configured. Set LINKEDIN_CLIENT_ID + LINKEDIN_CLIENT_SECRET in .env and register app at developer.linkedin.com.",
        }
    tok = await _get_user_token(user_id)
    if not tok:
        return {
            "ok": False,
            "error": "This user has not completed LinkedIn OAuth. Send them through /auth/linkedin.",
        }
    urn = await _get_person_urn(tok)
    if not urn:
        return {"ok": False, "error": "Could not resolve LinkedIn person URN (token expired or revoked)."}

    body: dict[str, Any] = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{_LI_API_BASE}/v2/ugcPosts",
            headers={
                "Authorization": f"Bearer {tok}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
            },
            json=body,
        )
        if resp.status_code in (200, 201):
            # LinkedIn returns the post URN in `x-restli-id` header
            return {
                "ok": True,
                "post_id": resp.headers.get("x-restli-id") or resp.json().get("id"),
                "status_code": resp.status_code,
            }
        return {
            "ok": False,
            "error": f"LinkedIn {resp.status_code}: {resp.text[:300]}",
            "status_code": resp.status_code,
        }
