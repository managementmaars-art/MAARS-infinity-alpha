"""LinkedIn adapter — OAuth 2.0 + UGC Posts API.

Reference:
  - https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/posts-api
  - Authorize: https://www.linkedin.com/oauth/v2/authorization
  - Token:     https://www.linkedin.com/oauth/v2/accessToken

Scopes needed for posting:
  - w_member_social   (post on authenticated user's behalf)
  - r_liteprofile     (fetch user's URN)
  - r_emailaddress    (optional)

Publishing a text-only share:
  POST https://api.linkedin.com/v2/ugcPosts
  Headers: Authorization: Bearer <token>, X-Restli-Protocol-Version: 2.0.0
  Body: {
    "author": "urn:li:person:<id>",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": {"text": "..."},
        "shareMediaCategory": "NONE"
      }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
  }

Media (image/video) requires register-upload → PUT bytes → reference asset URN.
This adapter ships the text flow; media flow scaffolded for later.

LinkedIn tokens don't refresh via refresh_token unless you have the
`r_member_social` scope approved by LinkedIn review (Marketing Developer
Platform tier). Default tokens last 60 days.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from urllib.parse import urlencode

from .base import BasePlatformAdapter, PlatformError

logger = logging.getLogger(__name__)

AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL     = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE      = "https://api.linkedin.com/v2"


class LinkedInAdapter(BasePlatformAdapter):
    platform = "linkedin"
    supports_scheduling = False   # LinkedIn has native scheduling but requires Marketing API

    def client_id(self) -> str | None:
        return self._env("LINKEDIN_CLIENT_ID")

    def client_secret(self) -> str | None:
        return self._env("LINKEDIN_CLIENT_SECRET")

    def oauth_authorize_url(
        self, *, state: str, redirect_uri: str, scopes: list[str] | None = None,
    ) -> str:
        cid = self.client_id()
        if not cid:
            raise PlatformError("LINKEDIN_CLIENT_ID not set", platform=self.platform)
        params = {
            "response_type": "code",
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes or ["openid", "profile", "w_member_social", "email"]),
            "state": state,
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def oauth_exchange(
        self, *, code: str, redirect_uri: str, verifier: str | None = None,
    ) -> dict[str, Any]:
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            raise PlatformError("LINKEDIN_CLIENT_ID/SECRET missing", platform=self.platform)
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": cid,
                "client_secret": secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code >= 400:
            raise PlatformError(f"token exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        tok = r.json()

        # LinkedIn /userinfo to get the author URN.
        ui = await client.get(
            f"{API_BASE}/userinfo",
            headers={"Authorization": f"Bearer {tok['access_token']}"},
        )
        profile = ui.json() if ui.status_code < 400 else {}
        sub = profile.get("sub")  # LinkedIn OIDC sub is the member ID

        return {
            "secret": tok["access_token"],
            "refresh_secret": tok.get("refresh_token"),
            "expires_at": time.time() + int(tok.get("expires_in", 60 * 86400)),
            "public": {
                "member_id": sub,
                "author_urn": f"urn:li:person:{sub}" if sub else None,
                "name": profile.get("name"),
                "email": profile.get("email"),
            },
            "metadata": {"scope": tok.get("scope")},
        }

    async def publish(
        self, *, user_id: str, text: str,
        media_urls: list[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        author = (cred.public or {}).get("author_urn")
        if not author:
            return {"ok": False, "platform": self.platform, "error": "no author_urn on credential"}

        visibility = (params or {}).get("visibility", "PUBLIC")   # PUBLIC | CONNECTIONS
        image_urls = (params or {}).get("image_urls") or []
        share_content: dict = {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "NONE",
        }

        # Media upload path: register → PUT bytes → attach as media asset
        if image_urls:
            media_assets = await _upload_linkedin_images(
                access_token=cred.secret, author=author, image_urls=image_urls,
            )
            if media_assets:
                share_content["shareMediaCategory"] = "IMAGE"
                share_content["media"] = [
                    {
                        "status": "READY",
                        "description": {"text": text[:200]},
                        "media": urn,
                        "title": {"text": (params or {}).get("title", "")[:200]},
                    }
                    for urn in media_assets
                ]

        body = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
        }

        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            f"{API_BASE}/ugcPosts",
            headers={
                "Authorization": f"Bearer {cred.secret}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json=body,
        )
        if r.status_code >= 400:
            return {"ok": False, "platform": self.platform,
                    "status": r.status_code, "error": r.text[:400]}
        data = r.json() if r.text else {}
        post_urn = data.get("id") or r.headers.get("x-restli-id")
        post_id = (post_urn or "").split(":")[-1] if post_urn else None
        return {
            "ok": True, "platform": self.platform,
            "post_id": post_urn,
            "url": f"https://www.linkedin.com/feed/update/{post_urn}" if post_urn else None,
            "raw": data,
        }

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.get(
            f"{API_BASE}/socialActions/{post_id}",
            headers={"Authorization": f"Bearer {cred.secret}"},
        )
        if r.status_code >= 400:
            return {"ok": False, "error": r.text[:300]}
        return {"ok": True, **(r.json() or {})}

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        from services.http_client import get_client
        client = await get_client()
        r = await client.delete(
            f"{API_BASE}/ugcPosts/{post_id}",
            headers={"Authorization": f"Bearer {cred.secret}",
                     "X-Restli-Protocol-Version": "2.0.0"},
        )
        return {"ok": r.status_code < 400, "status": r.status_code}


async def _upload_linkedin_images(
    *, access_token: str, author: str, image_urls: list[str],
) -> list[str]:
    """Register → fetch bytes → PUT to LinkedIn's upload URL.
    Returns list of asset URNs ready for attachment to a UGC post.
    Silently skips any that fail so a single bad URL doesn't lose the post."""
    from services.http_client import get_client
    client = await get_client()
    urns: list[str] = []
    for src_url in image_urls[:9]:   # LinkedIn allows up to 9 images per post
        try:
            # 1. Register the upload
            reg = await client.post(
                f"{API_BASE}/assets?action=registerUpload",
                headers={"Authorization": f"Bearer {access_token}",
                         "Content-Type": "application/json",
                         "X-Restli-Protocol-Version": "2.0.0"},
                json={
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner":   author,
                        "serviceRelationships": [{
                            "relationshipType": "OWNER",
                            "identifier":       "urn:li:userGeneratedContent",
                        }],
                    }
                },
            )
            if reg.status_code >= 400:
                continue
            d = reg.json().get("value") or {}
            upload_url = ((d.get("uploadMechanism") or {})
                          .get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest") or {}
                          ).get("uploadUrl")
            asset_urn = d.get("asset")
            if not (upload_url and asset_urn):
                continue
            # 2. Fetch source bytes
            src = await client.get(src_url, timeout=30)
            if src.status_code >= 400:
                continue
            # 3. PUT to the LI upload endpoint
            put = await client.put(
                upload_url,
                headers={"Authorization": f"Bearer {access_token}"},
                content=src.content,
            )
            if put.status_code < 400:
                urns.append(asset_urn)
        except Exception:
            # Per-image failure is non-fatal — skip and continue
            continue
    return urns
