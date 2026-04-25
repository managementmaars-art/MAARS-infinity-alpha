"""Per-provider integration drivers.

Each provider registers a DriverSpec with the integration_driver module.
The `api_handler` wraps existing workflow_services adapters; the
`browser_handler` drives the live web app via the BrowserAgent session
pool when the API is gated or unavailable.

Browser handlers are deliberately small — they start the user's session
at the right URL and click/type to perform the action. The user's cookies
(loaded from `backend/browser_data/storage_states/{user_id}.json`) keep
them signed in. When a 2FA/CAPTCHA page blocks progress, the BrowserAgent
pauses and yields control back to the operator automatically.

NOT PRODUCTION-HARDENED — web UIs change and selectors drift. These are
scaffold implementations that prove the authority path works end-to-end;
real selectors + reliability hardening is per-provider engineering.
"""
from __future__ import annotations
import logging
from typing import Any

from services.integration_driver import (
    DriverSpec,
    register_driver,
    _open_session,
    _goto,
)

logger = logging.getLogger(__name__)


# ═══ LinkedIn ═══════════════════════════════════════════════════════

async def _linkedin_api(user_id: str, action: str, params: dict) -> dict:
    """LinkedIn UGC API via workflow_services (post via bearer token)."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "linkedin")
    if not token:
        return {"ok": False, "error": "no_linkedin_oauth_token"}
    if action == "post":
        text = (params.get("content") or "").strip()[:3000]
        if not text: return {"ok": False, "error": "content_required"}
        s, b, _ = await _http("POST", "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": f"Bearer {token}",
                     "X-Restli-Protocol-Version": "2.0.0",
                     "Content-Type": "application/json"},
            json={
                "author": f"urn:li:person:{params.get('author_urn','~')}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {"com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }},
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            })
        return {"ok": 200 <= s < 300, "status": s, "body": b}
    return {"ok": False, "error": f"unsupported_action: {action}"}


async def _linkedin_browser(user_id: str, action: str, params: dict) -> dict:
    sess = await _open_session(user_id, start_url="https://www.linkedin.com/feed/")
    if action == "post":
        content = params.get("content", "")[:3000]
        # Click the start-a-post trigger + type
        await _goto(sess, "https://www.linkedin.com/feed/")
        try:
            await sess.click('button[aria-label="Start a post"]', caller="system")
            await sess.fill('div.ql-editor[role="textbox"]', content, caller="system")
            await sess.click('button.share-actions__primary-action', caller="system")
            return {"ok": True, "posted_via": "browser", "preview": content[:80]}
        except Exception as exc:
            return {"ok": False, "error": f"browser_post_failed: {exc}",
                    "hint": "UI may have changed; check session + selectors"}
    if action == "read_feed":
        await _goto(sess, "https://www.linkedin.com/feed/")
        text = await sess.extract_text("main")
        return {"ok": True, "feed_preview": (text or "")[:2000]}
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="linkedin", display_name="LinkedIn", category="social",
    api_actions=["post"],
    browser_actions=["post", "read_feed", "send_message"],
    api_handler=_linkedin_api, browser_handler=_linkedin_browser,
    login_url="https://www.linkedin.com/login",
    docs_url="https://learn.microsoft.com/en-us/linkedin/marketing/",
))


# ═══ X / Twitter ════════════════════════════════════════════════════

async def _x_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "x") or await _from_vault(user_id, "twitter")
    if not token:
        return {"ok": False, "error": "no_x_bearer_token"}
    if action == "post":
        text = (params.get("content") or "")[:280]
        s, b, _ = await _http("POST", "https://api.twitter.com/2/tweets",
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
            json={"text": text})
        return {"ok": 200 <= s < 300, "status": s, "body": b}
    return {"ok": False, "error": f"unsupported_action: {action}"}


async def _x_browser(user_id: str, action: str, params: dict) -> dict:
    sess = await _open_session(user_id, start_url="https://x.com/home")
    if action == "post":
        content = (params.get("content") or "")[:280]
        try:
            await sess.click('a[data-testid="SideNav_NewTweet_Button"]', caller="system")
            await sess.fill('div[data-testid="tweetTextarea_0"]', content, caller="system")
            await sess.click('button[data-testid="tweetButton"]', caller="system")
            return {"ok": True, "posted_via": "browser"}
        except Exception as exc:
            return {"ok": False, "error": f"browser_post_failed: {exc}"}
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="x", display_name="X / Twitter", category="social",
    api_actions=["post"],
    browser_actions=["post", "read_feed", "send_dm"],
    api_handler=_x_api, browser_handler=_x_browser,
    login_url="https://x.com/login",
    docs_url="https://docs.x.com/",
))


# ═══ Instagram ══════════════════════════════════════════════════════

async def _instagram_api(user_id: str, action: str, params: dict) -> dict:
    """Instagram Graph API via Meta. Needs a connected Facebook Page +
    Instagram Business account."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "instagram") or await _from_vault(user_id, "meta")
    if not token:
        return {"ok": False, "error": "no_instagram_graph_token"}
    ig_user_id = params.get("ig_user_id")
    if not ig_user_id:
        return {"ok": False, "error": "ig_user_id_required"}
    if action == "post":
        image_url = params.get("image_url")
        caption = params.get("content", "")
        if not image_url: return {"ok": False, "error": "image_url_required"}
        # Two-step: create container → publish
        s1, b1, _ = await _http("POST", f"https://graph.facebook.com/v20.0/{ig_user_id}/media",
            params={"image_url": image_url, "caption": caption, "access_token": token})
        if s1 >= 300: return {"ok": False, "status": s1, "body": b1}
        container_id = (b1 or {}).get("id")
        s2, b2, _ = await _http("POST", f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish",
            params={"creation_id": container_id, "access_token": token})
        return {"ok": 200 <= s2 < 300, "status": s2, "body": b2}
    return {"ok": False, "error": f"unsupported_action: {action}"}


async def _instagram_browser(user_id: str, action: str, params: dict) -> dict:
    sess = await _open_session(user_id, start_url="https://www.instagram.com/")
    if action == "read_inbox":
        await _goto(sess, "https://www.instagram.com/direct/inbox/")
        text = await sess.extract_text("main")
        return {"ok": True, "inbox_preview": (text or "")[:2000]}
    # Instagram web blocks most posting flows — mark as unsupported for now
    return {"ok": False,
            "error": f"action '{action}' requires Instagram Graph API (posting is blocked on web). "
                     "Connect a Facebook Page + IG Business account and use api mode."}


register_driver(DriverSpec(
    provider="instagram", display_name="Instagram", category="social",
    api_actions=["post"],
    browser_actions=["read_inbox", "read_profile"],
    api_handler=_instagram_api, browser_handler=_instagram_browser,
    login_url="https://www.instagram.com/accounts/login/",
    docs_url="https://developers.facebook.com/docs/instagram-api",
))


# ═══ TikTok ═════════════════════════════════════════════════════════

async def _tiktok_api(user_id: str, action: str, params: dict) -> dict:
    """TikTok Content Posting API — requires a sandbox-approved app."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "tiktok")
    if not token:
        return {"ok": False, "error": "no_tiktok_token"}
    if action == "post_video":
        # Simplified — real flow is multi-step with upload-init + video-upload + publish
        s, b, _ = await _http("POST", "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "post_info": {"title": params.get("content", "")[:150],
                              "privacy_level": params.get("privacy", "SELF_ONLY")},
                "source_info": {"source": "PULL_FROM_URL",
                                "video_url": params.get("video_url")},
            })
        return {"ok": 200 <= s < 300, "status": s, "body": b}
    return {"ok": False, "error": f"unsupported_action: {action}"}


async def _tiktok_browser(user_id: str, action: str, params: dict) -> dict:
    sess = await _open_session(user_id, start_url="https://www.tiktok.com/")
    if action == "read_profile":
        try:
            await _goto(sess, "https://www.tiktok.com/foryou")
            text = await sess.extract_text("main")
            return {"ok": True, "feed_preview": (text or "")[:2000]}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": f"unsupported_action: {action}",
            "hint": "TikTok blocks most automated posting. Use approved API."}


register_driver(DriverSpec(
    provider="tiktok", display_name="TikTok", category="social",
    api_actions=["post_video"],
    browser_actions=["read_profile", "read_inbox"],
    api_handler=_tiktok_api, browser_handler=_tiktok_browser,
    login_url="https://www.tiktok.com/login",
    docs_url="https://developers.tiktok.com/",
))


# ═══ YouTube ════════════════════════════════════════════════════════

async def _youtube_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "youtube") or await _from_vault(user_id, "google_oauth")
    if not token:
        return {"ok": False, "error": "no_youtube_oauth_token"}
    if action == "upload":
        # Resumable upload; simplified here to init step
        s, b, _ = await _http("POST",
            "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json",
                     "X-Upload-Content-Type": "video/*"},
            json={
                "snippet":  {"title": params.get("title") or "Untitled",
                             "description": params.get("content", "")},
                "status":   {"privacyStatus": params.get("privacy", "private")},
            })
        return {"ok": 200 <= s < 300, "status": s, "body": b,
                "note": "returned upload URL — stream video bytes there to complete"}
    return {"ok": False, "error": f"unsupported_action: {action}"}


async def _youtube_browser(user_id: str, action: str, params: dict) -> dict:
    sess = await _open_session(user_id, start_url="https://studio.youtube.com/")
    if action == "read_dashboard":
        text = await sess.extract_text("body")
        return {"ok": True, "dashboard_preview": (text or "")[:2000]}
    return {"ok": False, "error": f"unsupported_action: {action}",
            "hint": "YouTube upload requires Data API v3 — use api mode."}


register_driver(DriverSpec(
    provider="youtube", display_name="YouTube", category="social",
    api_actions=["upload"],
    browser_actions=["read_dashboard"],
    api_handler=_youtube_api, browser_handler=_youtube_browser,
    login_url="https://accounts.google.com/signin",
    docs_url="https://developers.google.com/youtube/v3",
))


# ═══ Facebook ═══════════════════════════════════════════════════════

async def _facebook_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "facebook") or await _from_vault(user_id, "meta")
    if not token:
        return {"ok": False, "error": "no_facebook_token"}
    page_id = params.get("page_id")
    if not page_id: return {"ok": False, "error": "page_id_required"}
    if action == "post":
        s, b, _ = await _http("POST", f"https://graph.facebook.com/v20.0/{page_id}/feed",
            params={"message": params.get("content", ""), "access_token": token})
        return {"ok": 200 <= s < 300, "status": s, "body": b}
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="facebook", display_name="Facebook", category="social",
    api_actions=["post"], browser_actions=[],
    api_handler=_facebook_api, browser_handler=None,
    login_url="https://www.facebook.com/login",
    docs_url="https://developers.facebook.com/docs/graph-api",
))


# ═══ WhatsApp Business ══════════════════════════════════════════════

async def _whatsapp_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "whatsapp")
    if not token:
        return {"ok": False, "error": "no_whatsapp_token"}
    phone_id = params.get("phone_number_id")
    to = params.get("to")
    if not (phone_id and to):
        return {"ok": False, "error": "phone_number_id + to required"}
    if action == "send_message":
        s, b, _ = await _http("POST",
            f"https://graph.facebook.com/v20.0/{phone_id}/messages",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": params.get("content", "")},
            })
        return {"ok": 200 <= s < 300, "status": s, "body": b}
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="whatsapp", display_name="WhatsApp Business", category="messaging",
    api_actions=["send_message"], browser_actions=[],
    api_handler=_whatsapp_api, browser_handler=None,
    login_url="https://business.whatsapp.com/",
    docs_url="https://developers.facebook.com/docs/whatsapp",
))


# ═══ Slack ══════════════════════════════════════════════════════════

async def _slack_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import t_slack_send
    if action == "send":
        return await t_slack_send(user_id, params, {}, {})
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="slack", display_name="Slack", category="messaging",
    api_actions=["send"], browser_actions=[],
    api_handler=_slack_api, browser_handler=None,
    login_url="https://slack.com/signin",
    docs_url="https://api.slack.com/",
))


# ═══ Discord ════════════════════════════════════════════════════════

async def _discord_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import t_discord_send
    if action == "send":
        return await t_discord_send(user_id, params, {}, {})
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="discord", display_name="Discord", category="messaging",
    api_actions=["send"], browser_actions=[],
    api_handler=_discord_api, browser_handler=None,
    login_url="https://discord.com/login",
    docs_url="https://discord.com/developers/docs",
))


# ═══ Telegram ═══════════════════════════════════════════════════════

async def _telegram_api(user_id: str, action: str, params: dict) -> dict:
    from services.workflows.workflow_services import t_telegram_send
    if action == "send":
        return await t_telegram_send(user_id, params, {}, {})
    return {"ok": False, "error": f"unsupported_action: {action}"}


register_driver(DriverSpec(
    provider="telegram", display_name="Telegram", category="messaging",
    api_actions=["send"], browser_actions=[],
    api_handler=_telegram_api, browser_handler=None,
    login_url="https://web.telegram.org/",
    docs_url="https://core.telegram.org/bots/api",
))
