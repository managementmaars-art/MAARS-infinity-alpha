"""Meta adapter — Instagram + Facebook via the Graph API.

Reference:
  - https://developers.facebook.com/docs/facebook-login/
  - https://developers.facebook.com/docs/graph-api/
  - https://developers.facebook.com/docs/instagram-api/guides/content-publishing

OAuth:
  Authorize: https://www.facebook.com/v21.0/dialog/oauth
  Token:     https://graph.facebook.com/v21.0/oauth/access_token
  Scopes:
    Facebook page posting: pages_manage_posts, pages_read_engagement
    Instagram publishing:  instagram_basic, instagram_content_publish,
                           pages_show_list, business_management

IG Business accounts post THROUGH a connected Facebook Page. The flow:
  1. Exchange short-lived user token → long-lived user token (60d).
  2. List user's pages: GET /me/accounts → get page_id + page_access_token.
  3. For IG: get instagram_business_account.id via
     GET /{page_id}?fields=instagram_business_account.
  4. Post to IG: TWO steps —
     a) Create container: POST /{ig_account_id}/media
        body: {image_url, caption, access_token}
     b) Publish: POST /{ig_account_id}/media_publish
        body: {creation_id: <container_id>}
  5. Post to FB page: POST /{page_id}/feed {message, access_token}.

This adapter keeps one class with `target` = "instagram" | "facebook".
The registry exposes both as separate platform slugs, but both share
the same Meta OAuth flow.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from urllib.parse import urlencode

from .base import BasePlatformAdapter, PlatformError

logger = logging.getLogger(__name__)

GRAPH_VERSION  = "v21.0"
AUTHORIZE_URL  = f"https://www.facebook.com/{GRAPH_VERSION}/dialog/oauth"
TOKEN_URL      = f"https://graph.facebook.com/{GRAPH_VERSION}/oauth/access_token"
GRAPH_BASE     = f"https://graph.facebook.com/{GRAPH_VERSION}"


class MetaAdapter(BasePlatformAdapter):
    platform = "meta"
    supports_scheduling = True   # Meta supports scheduled_publish_time on page posts

    def __init__(self, target: str = "facebook"):
        # "facebook" or "instagram" — publish() dispatches on this.
        self.target = target
        # Override the default platform slug so credential_vault sees
        # the concrete target. But OAuth flow is shared.
        self.platform = target

    def client_id(self) -> str | None:
        return self._env("META_APP_ID", "FACEBOOK_APP_ID")

    def client_secret(self) -> str | None:
        return self._env("META_APP_SECRET", "FACEBOOK_APP_SECRET")

    def oauth_authorize_url(
        self, *, state: str, redirect_uri: str, scopes: list[str] | None = None,
    ) -> str:
        cid = self.client_id()
        if not cid:
            raise PlatformError("META_APP_ID not set", platform=self.platform)
        params = {
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "scope": ",".join(scopes or [
                "pages_manage_posts", "pages_read_engagement", "pages_show_list",
                "instagram_basic", "instagram_content_publish", "business_management",
                "public_profile",
            ]),
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def oauth_exchange(
        self, *, code: str, redirect_uri: str, verifier: str | None = None,
    ) -> dict[str, Any]:
        cid = self.client_id()
        secret = self.client_secret()
        if not (cid and secret):
            raise PlatformError("META_APP_ID/SECRET missing", platform=self.platform)

        from services.http_client import get_client
        client = await get_client()

        # Step 1: short-lived user token
        r = await client.get(TOKEN_URL, params={
            "client_id": cid,
            "redirect_uri": redirect_uri,
            "client_secret": secret,
            "code": code,
        })
        if r.status_code >= 400:
            raise PlatformError(f"token exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        short = r.json()
        short_token = short.get("access_token")

        # Step 2: exchange for long-lived user token
        r = await client.get(TOKEN_URL, params={
            "grant_type": "fb_exchange_token",
            "client_id": cid,
            "client_secret": secret,
            "fb_exchange_token": short_token,
        })
        if r.status_code >= 400:
            raise PlatformError(f"long-lived exchange failed: {r.text[:300]}", status=r.status_code, platform=self.platform)
        ll = r.json()
        user_token = ll.get("access_token", short_token)

        # Step 3: list pages + pick first by default. Caller can reassign.
        pages_r = await client.get(
            f"{GRAPH_BASE}/me/accounts",
            params={"access_token": user_token, "fields": "id,name,access_token,instagram_business_account"},
        )
        pages = pages_r.json().get("data", []) if pages_r.status_code < 400 else []
        default_page = pages[0] if pages else {}

        return {
            "secret": user_token,
            "refresh_secret": None,   # Meta long-lived tokens don't refresh; re-auth at ~60d
            "expires_at": time.time() + int(ll.get("expires_in", 60 * 86400)),
            "public": {
                "default_page_id": default_page.get("id"),
                "default_page_access_token": default_page.get("access_token"),
                "default_ig_account_id": (default_page.get("instagram_business_account") or {}).get("id"),
                "pages": [{"id": p.get("id"), "name": p.get("name")} for p in pages],
            },
            "metadata": {"token_type": ll.get("token_type", "bearer")},
        }

    # ── Publishing ───────────────────────────────────────────────────
    async def publish(
        self, *, user_id: str, text: str,
        media_urls: list[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        public = cred.public or {}
        params = params or {}

        if self.target == "instagram":
            ig_id = params.get("ig_account_id") or public.get("default_ig_account_id")
            page_token = params.get("page_access_token") or public.get("default_page_access_token")
            if not (ig_id and page_token):
                return {"ok": False, "platform": "instagram",
                        "error": "missing ig_account_id or page_access_token — user must connect an IG Business account"}
            if not media_urls:
                return {"ok": False, "platform": "instagram",
                        "error": "Instagram posts require at least one media URL (image or video)"}
            return await self._publish_instagram(ig_id, page_token, text, media_urls[0], params)

        # Facebook page post
        page_id = params.get("page_id") or public.get("default_page_id")
        page_token = params.get("page_access_token") or public.get("default_page_access_token")
        if not (page_id and page_token):
            return {"ok": False, "platform": "facebook",
                    "error": "no connected Facebook page"}
        return await self._publish_facebook(page_id, page_token, text, media_urls or [], params)

    async def _publish_facebook(
        self, page_id: str, page_token: str, text: str,
        media_urls: list[str], params: dict[str, Any],
    ) -> dict[str, Any]:
        from services.http_client import get_client
        client = await get_client()
        body: dict[str, Any] = {"message": text, "access_token": page_token}
        if media_urls:
            body["link"] = media_urls[0]   # simple preview-card path
        if params.get("scheduled_publish_time"):
            body["published"] = False
            body["scheduled_publish_time"] = int(params["scheduled_publish_time"])
        r = await client.post(f"{GRAPH_BASE}/{page_id}/feed", data=body)
        if r.status_code >= 400:
            return {"ok": False, "platform": "facebook",
                    "status": r.status_code, "error": r.text[:400]}
        data = r.json()
        post_id = data.get("id")
        return {"ok": True, "platform": "facebook",
                "post_id": post_id,
                "url": f"https://www.facebook.com/{post_id}" if post_id else None,
                "raw": data}

    async def _publish_instagram(
        self, ig_id: str, page_token: str, caption: str,
        media_url: str, params: dict[str, Any],
    ) -> dict[str, Any]:
        from services.http_client import get_client
        client = await get_client()
        is_video = any(media_url.lower().endswith(ext) for ext in (".mp4", ".mov", ".webm"))

        # 1) Create media container.
        container_body = {
            "caption": caption, "access_token": page_token,
        }
        if is_video:
            container_body["media_type"] = "REELS"
            container_body["video_url"] = media_url
        else:
            container_body["image_url"] = media_url
        r = await client.post(f"{GRAPH_BASE}/{ig_id}/media", data=container_body)
        if r.status_code >= 400:
            return {"ok": False, "platform": "instagram",
                    "status": r.status_code, "error": r.text[:400], "stage": "create_container"}
        creation_id = (r.json() or {}).get("id")

        # For video we should poll /status until FINISHED. Scaffold:
        # GET /{creation_id}?fields=status_code — repeat until "FINISHED".

        # 2) Publish.
        pr = await client.post(
            f"{GRAPH_BASE}/{ig_id}/media_publish",
            data={"creation_id": creation_id, "access_token": page_token},
        )
        if pr.status_code >= 400:
            return {"ok": False, "platform": "instagram",
                    "status": pr.status_code, "error": pr.text[:400], "stage": "publish"}
        data = pr.json()
        return {"ok": True, "platform": "instagram",
                "post_id": data.get("id"),
                "url": f"https://www.instagram.com/p/{data.get('id')}" if data.get('id') else None,
                "raw": data}

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        page_token = (cred.public or {}).get("default_page_access_token", cred.secret)
        from services.http_client import get_client
        client = await get_client()
        r = await client.get(
            f"{GRAPH_BASE}/{post_id}/insights",
            params={"metric": "impressions,reach,engaged_users", "access_token": page_token},
        )
        if r.status_code >= 400:
            return {"ok": False, "error": r.text[:300]}
        return {"ok": True, **(r.json() or {})}

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        cred = await self._require_creds(user_id)
        page_token = (cred.public or {}).get("default_page_access_token", cred.secret)
        from services.http_client import get_client
        client = await get_client()
        r = await client.delete(f"{GRAPH_BASE}/{post_id}", params={"access_token": page_token})
        return {"ok": r.status_code < 400, "status": r.status_code}
