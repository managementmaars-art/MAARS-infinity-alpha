"""TikTok adapter — Content Posting API.

Reference:
  - https://developers.tiktok.com/doc/content-posting-api-get-started/
  - Auth: OAuth 2.0 at https://www.tiktok.com/v2/auth/authorize/
  - Token exchange: https://open.tiktokapis.com/v2/oauth/token/

Scopes required:
  - user.info.basic
  - video.publish          (direct-post videos)
  - video.upload           (draft/inbox uploads)

Posting flow (video):
  1. Init upload: POST https://open.tiktokapis.com/v2/post/publish/video/init/
     body describes video source (FILE_UPLOAD with upload_id OR PULL_FROM_URL).
     Response gives a publish_id.
  2. For FILE_UPLOAD, chunk-upload the bytes to the returned upload_url.
     For PULL_FROM_URL, TikTok fetches the URL itself.
  3. Poll status: POST /v2/post/publish/status/fetch/ with publish_id
     until status == "PUBLISH_COMPLETE" or "FAILED".

App review gate:
  The Content Posting API requires app-review approval. Without it,
  posts go to the user's TikTok inbox as a draft — not directly to feed.
  The `direct_post` flag in init requires approved scope.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from urllib.parse import urlencode

from .base import BasePlatformAdapter, PlatformError

logger = logging.getLogger(__name__)

AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL     = "https://open.tiktokapis.com/v2/oauth/token/"
API_BASE      = "https://open.tiktokapis.com/v2"


class TikTokAdapter(BasePlatformAdapter):
    platform = "tiktok"

    def client_id(self) -> str | None:
        return self._env("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_ID")

    def client_secret(self) -> str | None:
        return self._env("TIKTOK_CLIENT_SECRET")

    def oauth_authorize_url(
        self, *, state: str, redirect_uri: str, scopes: list[str] | None = None,
    ) -> str:
        cid = self.client_id()
        if not cid:
            raise PlatformError("TIKTOK_CLIENT_KEY not set", platform=self.platform)
        params = {
            "client_key": cid,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": ",".join(scopes or ["user.info.basic", "video.publish", "video.upload"]),
            "state": state,
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def oauth_exchange(
        self, *, code: str, redirect_uri: str, verifier: str | None = None,
    ) -> dict[str, Any]:
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            raise PlatformError("TIKTOK_CLIENT_KEY/SECRET missing", platform=self.platform)
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            TOKEN_URL,
            data={
                "client_key": cid,
                "client_secret": secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code >= 400:
            raise PlatformError(f"token exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        tok = r.json().get("data", r.json())

        # Fetch user info for the public handle.
        me = await client.get(
            f"{API_BASE}/user/info/",
            params={"fields": "open_id,union_id,display_name,username"},
            headers={"Authorization": f"Bearer {tok['access_token']}"},
        )
        me_data = (me.json() or {}).get("data", {}).get("user", {}) if me.status_code < 400 else {}

        return {
            "secret": tok["access_token"],
            "refresh_secret": tok.get("refresh_token"),
            "expires_at": time.time() + int(tok.get("expires_in", 86400)),
            "public": {
                "open_id": tok.get("open_id") or me_data.get("open_id"),
                "display_name": me_data.get("display_name"),
                "username": me_data.get("username"),
            },
            "metadata": {"scope": tok.get("scope")},
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
        r = await client.post(TOKEN_URL, data={
            "client_key": cid,
            "client_secret": secret,
            "refresh_token": cred.refresh_secret,
            "grant_type": "refresh_token",
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code >= 400:
            return None
        tok = r.json().get("data", r.json())
        from services.credential_vault import Credential
        return Credential(
            scope=cred.scope, scope_id=cred.scope_id,
            provider=self.platform, kind=cred.kind,
            secret=tok["access_token"],
            refresh_secret=tok.get("refresh_token", cred.refresh_secret),
            expires_at=time.time() + int(tok.get("expires_in", 86400)),
            public=cred.public, metadata=cred.metadata,
        )

    # ── Publishing ───────────────────────────────────────────────────
    async def publish(
        self, *, user_id: str, text: str,
        media_urls: list[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        if not media_urls:
            return {"ok": False, "platform": "tiktok",
                    "error": "TikTok posts require a video URL"}
        params = params or {}
        direct_post = bool(params.get("direct_post", False))
        video_url = media_urls[0]

        body = {
            "post_info": {
                "title": text[:150],
                "privacy_level": params.get("privacy_level", "SELF_ONLY"),
                "disable_duet": params.get("disable_duet", False),
                "disable_comment": params.get("disable_comment", False),
                "disable_stitch": params.get("disable_stitch", False),
                "video_cover_timestamp_ms": params.get("cover_ms", 1000),
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        }
        endpoint = "/post/publish/video/init/" if direct_post else "/post/publish/inbox/video/init/"

        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            f"{API_BASE}{endpoint}",
            headers={"Authorization": f"Bearer {cred.secret}",
                     "Content-Type": "application/json; charset=UTF-8"},
            json=body,
        )
        if r.status_code >= 400:
            return {"ok": False, "platform": "tiktok",
                    "status": r.status_code, "error": r.text[:400]}
        data = r.json().get("data", {})
        publish_id = data.get("publish_id")
        return {
            "ok": True, "platform": "tiktok",
            "post_id": publish_id,
            "url": None,   # TikTok doesn't return a URL until publish completes; caller polls stats
            "raw": data,
            "status_hint": "Poll stats(publish_id) until PUBLISH_COMPLETE",
        }

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        """For TikTok, `post_id` = publish_id during in-flight;
        after completion it becomes the video_id."""
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            f"{API_BASE}/post/publish/status/fetch/",
            headers={"Authorization": f"Bearer {cred.secret}",
                     "Content-Type": "application/json; charset=UTF-8"},
            json={"publish_id": post_id},
        )
        if r.status_code >= 400:
            return {"ok": False, "error": r.text[:300]}
        return {"ok": True, **(r.json() or {}).get("data", {})}

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        # TikTok Content Posting API does not expose a delete endpoint
        # for individual videos (as of 2025). Users must delete in-app.
        return {"ok": False, "platform": "tiktok",
                "error": "delete not supported — user must remove in TikTok app"}
