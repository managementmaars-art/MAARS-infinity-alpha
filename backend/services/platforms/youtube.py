"""YouTube adapter — Data API v3 via OAuth 2.0 (Google).

Reference:
  - https://developers.google.com/youtube/v3/docs/videos/insert
  - Authorize: https://accounts.google.com/o/oauth2/v2/auth
  - Token:     https://oauth2.googleapis.com/token
  - Upload:    https://www.googleapis.com/upload/youtube/v3/videos (resumable)

Scopes:
  - https://www.googleapis.com/auth/youtube.upload   (upload videos)
  - https://www.googleapis.com/auth/youtube          (manage account)
  - https://www.googleapis.com/auth/youtube.readonly (stats)

Publish flow for videos (resumable upload):
  1. POST /upload/youtube/v3/videos?uploadType=resumable with metadata
     (snippet, status) in body + Content-Type: application/json; charset=UTF-8.
     Response includes Location header = upload URL.
  2. PUT video bytes to Location URL in one or more chunks.
  3. Final response is the created Video resource with id.

This adapter handles a simple PULL_FROM_URL helper: we download the
video from media_url, stream it to YouTube. For hosted files (S3, etc)
that works fine. Large files are chunked automatically by httpx.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from urllib.parse import urlencode

from .base import BasePlatformAdapter, PlatformError

logger = logging.getLogger(__name__)

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL     = "https://oauth2.googleapis.com/token"
API_BASE      = "https://www.googleapis.com/youtube/v3"
UPLOAD_BASE   = "https://www.googleapis.com/upload/youtube/v3"


class YouTubeAdapter(BasePlatformAdapter):
    platform = "youtube"

    def client_id(self) -> str | None:
        return self._env("YOUTUBE_CLIENT_ID", "GOOGLE_CLIENT_ID")

    def client_secret(self) -> str | None:
        return self._env("YOUTUBE_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET")

    def oauth_authorize_url(
        self, *, state: str, redirect_uri: str, scopes: list[str] | None = None,
    ) -> str:
        cid = self.client_id()
        if not cid:
            raise PlatformError("YOUTUBE_CLIENT_ID not set", platform=self.platform)
        params = {
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "access_type": "offline",     # required for refresh_token
            "prompt": "consent",          # forces consent so refresh_token is returned
            "include_granted_scopes": "true",
            "state": state,
            "scope": " ".join(scopes or [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly",
            ]),
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def oauth_exchange(
        self, *, code: str, redirect_uri: str, verifier: str | None = None,
    ) -> dict[str, Any]:
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            raise PlatformError("YOUTUBE_CLIENT_ID/SECRET missing", platform=self.platform)
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(TOKEN_URL, data={
            "code": code,
            "client_id": cid,
            "client_secret": secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        if r.status_code >= 400:
            raise PlatformError(f"token exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        tok = r.json()

        # Fetch channel info for the public handle.
        ch = await client.get(
            f"{API_BASE}/channels",
            params={"part": "id,snippet", "mine": "true"},
            headers={"Authorization": f"Bearer {tok['access_token']}"},
        )
        channel_data = (ch.json() or {}).get("items", []) if ch.status_code < 400 else []
        channel = channel_data[0] if channel_data else {}

        return {
            "secret": tok["access_token"],
            "refresh_secret": tok.get("refresh_token"),
            "expires_at": time.time() + int(tok.get("expires_in", 3600)),
            "public": {
                "channel_id": channel.get("id"),
                "channel_title": (channel.get("snippet") or {}).get("title"),
            },
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
        r = await client.post(TOKEN_URL, data={
            "client_id": cid,
            "client_secret": secret,
            "refresh_token": cred.refresh_secret,
            "grant_type": "refresh_token",
        })
        if r.status_code >= 400:
            return None
        tok = r.json()
        from services.credential_vault import Credential
        return Credential(
            scope=cred.scope, scope_id=cred.scope_id,
            provider=self.platform, kind=cred.kind,
            secret=tok["access_token"],
            refresh_secret=cred.refresh_secret,  # Google refresh token stays stable
            expires_at=time.time() + int(tok.get("expires_in", 3600)),
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
            return {"ok": False, "platform": "youtube",
                    "error": "YouTube publish requires a video URL in media_urls"}
        params = params or {}
        video_url = media_urls[0]
        title = (params.get("title") or text[:100] or "Untitled video")[:100]
        description = params.get("description") or text[:5000]
        tags = params.get("tags") or []
        privacy = params.get("privacy_status", "private")   # public | unlisted | private

        # Step 1: initiate resumable upload
        metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": params.get("category_id", "22"),   # 22 = People & Blogs
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": bool(params.get("made_for_kids", False)),
            },
        }

        from services.http_client import get_client
        client = await get_client()

        init = await client.post(
            f"{UPLOAD_BASE}/videos",
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers={
                "Authorization": f"Bearer {cred.secret}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/*",
            },
            json=metadata,
        )
        if init.status_code >= 400:
            return {"ok": False, "platform": "youtube",
                    "status": init.status_code, "error": init.text[:400], "stage": "init"}
        upload_url = init.headers.get("location") or init.headers.get("Location")
        if not upload_url:
            return {"ok": False, "platform": "youtube", "error": "no upload URL returned"}

        # Step 2: stream the video bytes from media_url directly to YouTube.
        async with client.stream("GET", video_url) as src:
            if src.status_code >= 400:
                return {"ok": False, "platform": "youtube",
                        "error": f"source fetch failed: {src.status_code}"}
            total_len = src.headers.get("content-length")

            async def _iter_bytes():
                async for chunk in src.aiter_bytes(chunk_size=8 * 1024 * 1024):
                    yield chunk

            hdrs = {"Authorization": f"Bearer {cred.secret}", "Content-Type": "video/*"}
            if total_len:
                hdrs["Content-Length"] = total_len
            up = await client.put(upload_url, headers=hdrs, content=_iter_bytes())

        if up.status_code >= 400:
            return {"ok": False, "platform": "youtube",
                    "status": up.status_code, "error": up.text[:400], "stage": "upload"}
        video = up.json()
        video_id = video.get("id")
        return {"ok": True, "platform": "youtube",
                "post_id": video_id,
                "url": f"https://youtu.be/{video_id}" if video_id else None,
                "raw": video}

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.get(
            f"{API_BASE}/videos",
            params={"id": post_id, "part": "statistics,snippet,status"},
            headers={"Authorization": f"Bearer {cred.secret}"},
        )
        if r.status_code >= 400:
            return {"ok": False, "error": r.text[:300]}
        items = (r.json() or {}).get("items", [])
        return {"ok": True, **(items[0] if items else {})}

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.delete(
            f"{API_BASE}/videos",
            params={"id": post_id},
            headers={"Authorization": f"Bearer {cred.secret}"},
        )
        return {"ok": r.status_code < 400, "status": r.status_code}
