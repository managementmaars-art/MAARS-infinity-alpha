"""X / Twitter adapter — API v2 OAuth 2.0 + PKCE + tweet publishing.

Reference: https://docs.x.com/x-api/posts/creation-of-a-post

OAuth 2.0 user context required for posting:
  - Authorize URL: https://twitter.com/i/oauth2/authorize
  - Token URL:     https://api.twitter.com/2/oauth2/token
  - Scopes needed: tweet.read tweet.write users.read offline.access
  - PKCE required (code_challenge + code_verifier)

Publishing:
  POST https://api.x.com/2/tweets
  body: {"text": "...", "media": {"media_ids": [...]}}

Media upload is a separate v1.1 API flow (media/upload.json), which we
stub here — most publishes are text-only for now. The flow is:
  1) Init: POST /1.1/media/upload.json?command=INIT
  2) Append: POST /1.1/media/upload.json?command=APPEND (chunked)
  3) Finalize: POST /1.1/media/upload.json?command=FINALIZE
  4) Attach media_id to tweet

Rate limits (app + user, 15-min window):
  POST /2/tweets: 200/user, 300/app (as of Dec 2025).
"""
from __future__ import annotations
import base64
import hashlib
import logging
import os
import secrets
import time
from typing import Any
from urllib.parse import urlencode

from .base import BasePlatformAdapter, PlatformError

logger = logging.getLogger(__name__)

AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL     = "https://api.twitter.com/2/oauth2/token"
API_BASE      = "https://api.x.com/2"


class TwitterAdapter(BasePlatformAdapter):
    platform = "x"
    supports_scheduling = False   # use our own scheduler; X paid "Scheduled Tweets" not in v2

    def client_id(self) -> str | None:
        return self._env("TWITTER_CLIENT_ID", "X_CLIENT_ID")

    def client_secret(self) -> str | None:
        return self._env("TWITTER_CLIENT_SECRET", "X_CLIENT_SECRET")

    # ── PKCE helpers ─────────────────────────────────────────────────
    def _pkce_pair(self) -> tuple[str, str]:
        verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        return verifier, challenge

    def oauth_authorize_url(
        self, *, state: str, redirect_uri: str, scopes: list[str] | None = None,
    ) -> tuple[str, str]:
        """Returns (url, code_verifier). The caller MUST persist
        code_verifier against `state` so we can pass it to oauth_exchange."""
        cid = self.client_id()
        if not cid:
            raise PlatformError("TWITTER_CLIENT_ID not set", platform=self.platform)
        verifier, challenge = self._pkce_pair()
        params = {
            "response_type": "code",
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes or [
                "tweet.read", "tweet.write", "users.read", "offline.access",
            ]),
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}", verifier

    async def oauth_exchange(
        self, *, code: str, redirect_uri: str, verifier: str | None = None,
    ) -> dict[str, Any]:
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            raise PlatformError("TWITTER_CLIENT_ID/SECRET missing", platform=self.platform)
        if not verifier:
            raise PlatformError("PKCE verifier missing", platform=self.platform)

        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": cid,
                "redirect_uri": redirect_uri,
                "code_verifier": verifier,
            },
            auth=(cid, secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code >= 400:
            raise PlatformError(f"token exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        tok = r.json()
        # Fetch the authenticated user's handle + id for public metadata.
        me = await client.get(
            f"{API_BASE}/users/me",
            headers={"Authorization": f"Bearer {tok['access_token']}"},
        )
        me_data = me.json().get("data", {}) if me.status_code < 400 else {}
        return {
            "secret": tok["access_token"],
            "refresh_secret": tok.get("refresh_token"),
            "expires_at": time.time() + int(tok.get("expires_in", 7200)),
            "public": {"user_id": me_data.get("id"), "username": me_data.get("username")},
            "metadata": {"scope": tok.get("scope"), "token_type": tok.get("token_type")},
        }

    async def refresh(self, cred):
        if not cred.refresh_secret:
            return None
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            return None
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": cred.refresh_secret,
                "client_id": cid,
            },
            auth=(cid, secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code >= 400:
            logger.info("twitter refresh failed: %s", r.text[:200])
            return None
        tok = r.json()
        from services.credential_vault import Credential
        return Credential(
            scope=cred.scope, scope_id=cred.scope_id,
            provider=self.platform, kind=cred.kind,
            secret=tok["access_token"],
            refresh_secret=tok.get("refresh_token") or cred.refresh_secret,
            expires_at=time.time() + int(tok.get("expires_in", 7200)),
            public=cred.public,
            metadata=cred.metadata,
        )

    # ── Publishing ───────────────────────────────────────────────────
    async def publish(
        self, *, user_id: str, text: str,
        media_urls: list[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        body: dict[str, Any] = {"text": text[:280]}
        # v1.1 media/upload → media_id(s) → attach to v2 tweet body.
        # Requires OAuth 1.0a user-context credentials on the same account
        # (v1.1 endpoints reject bearer tokens). Caller should store
        # oauth1 creds in cred.metadata["oauth1"]={consumer_key, consumer_secret,
        # access_token, access_token_secret}.
        if media_urls:
            media_ids = await _upload_twitter_media(
                cred=cred, media_urls=media_urls,
            )
            if media_ids:
                body["media"] = {"media_ids": media_ids}
        r = await client.post(
            f"{API_BASE}/tweets",
            headers={
                "Authorization": f"Bearer {cred.secret}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        if r.status_code >= 400:
            return {"ok": False, "platform": self.platform,
                    "status": r.status_code, "error": r.text[:400]}
        data = (r.json() or {}).get("data", {})
        tweet_id = data.get("id")
        username = (cred.public or {}).get("username", "i")
        return {
            "ok": True, "platform": self.platform,
            "post_id": tweet_id,
            "url": f"https://x.com/{username}/status/{tweet_id}" if tweet_id else None,
            "raw": data,
        }

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.get(
            f"{API_BASE}/tweets/{post_id}",
            params={"tweet.fields": "public_metrics,created_at"},
            headers={"Authorization": f"Bearer {cred.secret}"},
        )
        if r.status_code >= 400:
            return {"ok": False, "error": r.text[:300]}
        return {"ok": True, **(r.json().get("data") or {})}

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.delete(
            f"{API_BASE}/tweets/{post_id}",
            headers={"Authorization": f"Bearer {cred.secret}"},
        )
        return {"ok": r.status_code < 400, "status": r.status_code}


async def _upload_twitter_media(*, cred, media_urls: list[str]) -> list[str]:
    """Upload images/videos via v1.1 media/upload (user-context OAuth 1.0a).
    Returns v2-compatible media_id strings to attach to a tweet.

    Credentials: cred.metadata["oauth1"] must contain the 4 tokens. If
    they're missing this silently returns [] — the tweet still posts
    without media rather than failing outright."""
    from services.http_client import get_client
    oauth1 = (cred.metadata or {}).get("oauth1") or {}
    ck = oauth1.get("consumer_key")
    cs = oauth1.get("consumer_secret")
    at = oauth1.get("access_token")
    ats = oauth1.get("access_token_secret")
    if not (ck and cs and at and ats):
        return []
    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        return []
    oauth = OAuth1(ck, cs, at, ats)
    client = await get_client()
    ids: list[str] = []
    for src_url in media_urls[:4]:
        try:
            src = await client.get(src_url, timeout=30)
            if src.status_code >= 400:
                continue
            content = src.content
            # Simple single-request upload (works for <=5MB images)
            # Use httpx without auth + sign by converting OAuth1 to header
            import httpx, io
            with httpx.Client(timeout=60) as sync_client:
                resp = sync_client.post(
                    "https://upload.twitter.com/1.1/media/upload.json",
                    auth=oauth,
                    files={"media": ("file", io.BytesIO(content))},
                )
            if resp.status_code < 400:
                data = resp.json()
                mid = data.get("media_id_string") or str(data.get("media_id", ""))
                if mid:
                    ids.append(mid)
        except Exception:
            continue
    return ids
