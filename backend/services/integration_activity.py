"""Polled inbound activity per connected integration.

For each provider, a thin poller pulls recent inbound items (DMs,
mentions, comments, messages) and persists them to
`db.integration_activity`. The per-app command-center UI reads this
collection for the live feed, and the action log reads `integration_action_log`
for outbound activity — together those give the operator a full
inbox/outbox view per app.

Pollers are intentionally small and API-only. Browser-mode scraping is
fragile and gets blocked (esp. on Instagram/TikTok), so if the user
only has a browser session (no API key) we record a "connected but
no_api" placeholder rather than scraping HTML. The operator can still
read content by opening the in-app browser viewer.

Each poller is idempotent — we store `external_id` per item and upsert
so re-polling the same window does not duplicate rows.

Called by:
  • `scheduler.activity_poll_loop` (every ~5 min, for every connected user)
  • `integration_dashboard.dashboard()` does NOT trigger a poll — it
    just reads the last-polled snapshot so the page loads fast.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


# ── Registry of per-provider pollers ─────────────────────────────────

_POLLERS: dict[str, Callable[[str], Awaitable[list[dict[str, Any]]]]] = {}


def register_poller(provider: str, fn: Callable[[str], Awaitable[list[dict[str, Any]]]]) -> None:
    _POLLERS[provider] = fn


def pollable_providers() -> list[str]:
    return sorted(_POLLERS.keys())


# ── Storage helpers ──────────────────────────────────────────────────

async def _upsert_items(provider: str, user_id: str, items: list[dict[str, Any]]) -> int:
    """Bulk upsert polled items keyed by (user_id, provider, external_id)."""
    if not items:
        return 0
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    n_new = 0
    for it in items:
        ext_id = str(it.get("external_id") or it.get("id") or it.get("timestamp") or "")
        if not ext_id:
            continue
        doc = {
            "user_id":    user_id,
            "provider":   provider,
            "external_id": ext_id,
            "kind":       it.get("kind") or "item",          # "dm" | "mention" | "comment" | "message"
            "from":       it.get("from"),                    # sender name/handle
            "preview":    (it.get("preview") or "")[:500],   # text snippet
            "url":        it.get("url"),                     # deep link back to the app
            "occurred_at": it.get("occurred_at") or now,
            "raw":        it.get("raw"),                     # optional provider payload
            "polled_at":  now,
            "seen":       False,                             # operator marks read
        }
        res = await db.integration_activity.update_one(
            {"user_id": user_id, "provider": provider, "external_id": ext_id},
            {"$setOnInsert": {"first_seen_at": now}, "$set": doc},
            upsert=True,
        )
        if getattr(res, "upserted_id", None):
            n_new += 1
    # Remember last-poll marker so the dashboard can show "updated 2m ago"
    await db.integration_activity_meta.update_one(
        {"user_id": user_id, "provider": provider},
        {"$set": {"polled_at": now, "last_count": len(items), "user_id": user_id, "provider": provider}},
        upsert=True,
    )
    return n_new


async def get_feed(
    provider: str, user_id: str, limit: int = 50, unseen_only: bool = False,
) -> list[dict[str, Any]]:
    from db import db
    q: dict[str, Any] = {"user_id": user_id, "provider": provider}
    if unseen_only:
        q["seen"] = False
    cursor = db.integration_activity.find(q, {"_id": 0}).sort("occurred_at", -1).limit(
        max(1, min(int(limit), 200))
    )
    return await cursor.to_list(length=limit)


async def mark_seen(provider: str, user_id: str, external_ids: list[str]) -> int:
    from db import db
    if not external_ids:
        return 0
    res = await db.integration_activity.update_many(
        {"user_id": user_id, "provider": provider, "external_id": {"$in": external_ids}},
        {"$set": {"seen": True, "seen_at": datetime.now(timezone.utc).isoformat()}},
    )
    return int(getattr(res, "modified_count", 0) or 0)


async def poll_provider(provider: str, user_id: str) -> dict[str, Any]:
    """Poll one provider for one user. Safe to call often; no-op if no creds."""
    fn = _POLLERS.get(provider)
    if not fn:
        return {"ok": False, "provider": provider, "error": "no_poller_registered"}
    try:
        items = await fn(user_id)
    except Exception as exc:
        logger.warning("poll %s/%s failed: %s", provider, user_id, exc)
        return {"ok": False, "provider": provider, "error": f"{type(exc).__name__}: {exc}"}
    n_new = await _upsert_items(provider, user_id, items or [])
    return {"ok": True, "provider": provider, "polled": len(items or []), "new": n_new}


async def poll_all_connected(user_id: str) -> dict[str, Any]:
    """Poll every provider the user has credentials for. Returns a summary."""
    from services import integration_driver
    results: list[dict[str, Any]] = []
    for d in integration_driver.list_drivers():
        provider = d["provider"]
        if provider not in _POLLERS:
            continue
        status = await integration_driver.status(provider, user_id)
        # Only poll if the user actually has an API credential
        if not status.get("has_api_credential"):
            continue
        results.append(await poll_provider(provider, user_id))
    return {"ok": True, "results": results,
            "total_new": sum(r.get("new", 0) for r in results if r.get("ok"))}


# ═══ Per-provider pollers ════════════════════════════════════════════

async def _poll_x(user_id: str) -> list[dict[str, Any]]:
    """X / Twitter — pull mentions timeline for the authenticated user."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "x") or await _from_vault(user_id, "twitter")
    if not token:
        return []
    # 1) Who am I — need user_id for /users/:id/mentions
    s, me, _ = await _http("GET", "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {token}"})
    if s != 200 or not me:
        return []
    me_id = (me.get("data") or {}).get("id")
    if not me_id:
        return []
    s, body, _ = await _http("GET", f"https://api.twitter.com/2/users/{me_id}/mentions",
        headers={"Authorization": f"Bearer {token}"},
        params={"max_results": 25,
                "tweet.fields": "created_at,author_id",
                "expansions":   "author_id",
                "user.fields":  "username,name"})
    if s != 200 or not body:
        return []
    users = {u["id"]: u for u in (body.get("includes") or {}).get("users", [])}
    out = []
    for t in body.get("data") or []:
        author = users.get(t.get("author_id")) or {}
        out.append({
            "external_id": t.get("id"),
            "kind":        "mention",
            "from":        f"@{author.get('username')}" if author else None,
            "preview":     t.get("text") or "",
            "url":         f"https://x.com/i/web/status/{t.get('id')}",
            "occurred_at": t.get("created_at"),
        })
    return out


async def _poll_slack(user_id: str) -> list[dict[str, Any]]:
    """Slack — recent DMs from conversations.list + conversations.history."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "slack")
    if not token:
        return []
    s, convs, _ = await _http("GET", "https://slack.com/api/conversations.list",
        headers={"Authorization": f"Bearer {token}"},
        params={"types": "im", "limit": 10})
    if s != 200 or not convs or not convs.get("ok"):
        return []
    out = []
    for ch in convs.get("channels") or []:
        ch_id = ch.get("id")
        if not ch_id:
            continue
        s2, hist, _ = await _http("GET", "https://slack.com/api/conversations.history",
            headers={"Authorization": f"Bearer {token}"},
            params={"channel": ch_id, "limit": 10})
        if s2 != 200 or not hist or not hist.get("ok"):
            continue
        for m in hist.get("messages") or []:
            if m.get("bot_id"):   # skip bot echoes
                continue
            ts = m.get("ts")
            out.append({
                "external_id": f"{ch_id}:{ts}",
                "kind":        "dm",
                "from":        m.get("user"),
                "preview":     m.get("text") or "",
                "url":         None,
                "occurred_at": datetime.fromtimestamp(
                    float(ts or 0), tz=timezone.utc).isoformat() if ts else None,
            })
    return out


async def _poll_discord(user_id: str) -> list[dict[str, Any]]:
    """Discord — DMs via /users/@me/channels + /channels/:id/messages.
    Bot tokens can't receive DMs, so this works with a user/OAuth token."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "discord")
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    s, dms, _ = await _http("GET", "https://discord.com/api/v10/users/@me/channels",
        headers=headers)
    if s != 200 or not dms:
        return []
    out = []
    for ch in (dms if isinstance(dms, list) else [])[:10]:
        ch_id = ch.get("id")
        if not ch_id:
            continue
        s2, msgs, _ = await _http("GET",
            f"https://discord.com/api/v10/channels/{ch_id}/messages",
            headers=headers, params={"limit": 10})
        if s2 != 200 or not isinstance(msgs, list):
            continue
        for m in msgs:
            author = (m.get("author") or {}).get("username")
            out.append({
                "external_id": m.get("id"),
                "kind":        "dm",
                "from":        author,
                "preview":     m.get("content") or "",
                "url":         None,
                "occurred_at": m.get("timestamp"),
            })
    return out


async def _poll_telegram(user_id: str) -> list[dict[str, Any]]:
    """Telegram Bot API — getUpdates long-poll with offset."""
    from services.workflows.workflow_services import _from_vault, _http
    from db import db
    token = await _from_vault(user_id, "telegram")
    if not token:
        return []
    # Persist update_id offset so repeated polls don't replay the same chats
    meta = await db.integration_activity_meta.find_one(
        {"user_id": user_id, "provider": "telegram"}, {"_id": 0, "offset": 1})
    offset = int((meta or {}).get("offset") or 0)
    s, body, _ = await _http("GET", f"https://api.telegram.org/bot{token}/getUpdates",
        params={"offset": offset, "timeout": 0, "limit": 50})
    if s != 200 or not body or not body.get("ok"):
        return []
    out = []
    max_seen = offset
    for u in body.get("result") or []:
        up_id = int(u.get("update_id") or 0)
        max_seen = max(max_seen, up_id + 1)
        msg = u.get("message") or u.get("channel_post") or {}
        if not msg:
            continue
        frm = msg.get("from") or {}
        out.append({
            "external_id": str(u.get("update_id")),
            "kind":        "message",
            "from":        frm.get("username") or frm.get("first_name"),
            "preview":     msg.get("text") or msg.get("caption") or "",
            "url":         None,
            "occurred_at": datetime.fromtimestamp(
                int(msg.get("date") or 0), tz=timezone.utc).isoformat(),
        })
    if max_seen > offset:
        await db.integration_activity_meta.update_one(
            {"user_id": user_id, "provider": "telegram"},
            {"$set": {"offset": max_seen}},
            upsert=True,
        )
    return out


async def _poll_whatsapp(user_id: str) -> list[dict[str, Any]]:
    """WhatsApp Cloud API delivers inbound via webhook, not polling.
    Read whatever the webhook already stashed into integration_activity_inbox."""
    from db import db
    cursor = db.integration_activity_inbox.find(
        {"user_id": user_id, "provider": "whatsapp", "consumed": {"$ne": True}},
        {"_id": 0},
    ).sort("occurred_at", -1).limit(50)
    rows = await cursor.to_list(length=50)
    if rows:
        ids = [r.get("external_id") for r in rows if r.get("external_id")]
        if ids:
            await db.integration_activity_inbox.update_many(
                {"user_id": user_id, "provider": "whatsapp", "external_id": {"$in": ids}},
                {"$set": {"consumed": True}},
            )
    return rows


async def _poll_linkedin(user_id: str) -> list[dict[str, Any]]:
    """LinkedIn restricts inbound messaging/comments to partner tier.
    Return the last-updated timestamp on the profile so we can show a
    heartbeat, nothing else."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "linkedin")
    if not token:
        return []
    s, body, _ = await _http("GET", "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"})
    if s != 200 or not body:
        return []
    now = datetime.now(timezone.utc).isoformat()
    return [{
        "external_id": f"heartbeat:{now[:10]}",
        "kind":        "heartbeat",
        "from":        body.get("name"),
        "preview":     f"Connection healthy ({body.get('email') or body.get('sub')})",
        "url":         "https://www.linkedin.com/feed/",
        "occurred_at": now,
    }]


async def _poll_youtube(user_id: str) -> list[dict[str, Any]]:
    """YouTube — recent comments on your uploads via commentThreads."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "youtube") or await _from_vault(user_id, "google_oauth")
    if not token:
        return []
    s, body, _ = await _http("GET", "https://www.googleapis.com/youtube/v3/commentThreads",
        headers={"Authorization": f"Bearer {token}"},
        params={"part": "snippet", "allThreadsRelatedToChannelId": "mine", "maxResults": 25})
    if s != 200 or not body:
        return []
    out = []
    for t in body.get("items") or []:
        top = ((t.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {}
        out.append({
            "external_id": t.get("id"),
            "kind":        "comment",
            "from":        top.get("authorDisplayName"),
            "preview":     top.get("textDisplay") or "",
            "url":         top.get("authorChannelUrl"),
            "occurred_at": top.get("publishedAt"),
        })
    return out


async def _poll_facebook(user_id: str) -> list[dict[str, Any]]:
    """Facebook — recent page posts with new comments."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "facebook") or await _from_vault(user_id, "meta")
    if not token:
        return []
    # The user needs at least one managed page; grab the first
    s, pages, _ = await _http("GET", "https://graph.facebook.com/v20.0/me/accounts",
        params={"access_token": token})
    if s != 200 or not pages:
        return []
    page = next(iter(pages.get("data") or []), None)
    if not page:
        return []
    page_id = page.get("id")
    page_token = page.get("access_token") or token
    s2, feed, _ = await _http("GET", f"https://graph.facebook.com/v20.0/{page_id}/feed",
        params={"access_token": page_token,
                "fields": "message,created_time,comments.limit(3){message,from}",
                "limit":  10})
    if s2 != 200 or not feed:
        return []
    out = []
    for post in feed.get("data") or []:
        for c in ((post.get("comments") or {}).get("data") or []):
            out.append({
                "external_id": c.get("id"),
                "kind":        "comment",
                "from":        (c.get("from") or {}).get("name"),
                "preview":     c.get("message") or "",
                "url":         f"https://facebook.com/{post.get('id')}",
                "occurred_at": post.get("created_time"),
            })
    return out


async def _poll_instagram(user_id: str) -> list[dict[str, Any]]:
    """Instagram Graph API — recent comments on your IG Business media."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "instagram") or await _from_vault(user_id, "meta")
    if not token:
        return []
    # Needs ig_user_id from the Facebook page; cached on profile if wired
    from db import db
    prof = await db.users.find_one({"user_id": user_id}, {"_id": 0, "ig_user_id": 1})
    ig = (prof or {}).get("ig_user_id")
    if not ig:
        return []
    s, media, _ = await _http("GET", f"https://graph.facebook.com/v20.0/{ig}/media",
        params={"access_token": token, "fields": "id,caption,timestamp", "limit": 10})
    if s != 200 or not media:
        return []
    out = []
    for m in media.get("data") or []:
        s2, cm, _ = await _http("GET", f"https://graph.facebook.com/v20.0/{m.get('id')}/comments",
            params={"access_token": token, "fields": "id,text,username,timestamp", "limit": 10})
        if s2 != 200 or not cm:
            continue
        for c in cm.get("data") or []:
            out.append({
                "external_id": c.get("id"),
                "kind":        "comment",
                "from":        f"@{c.get('username')}" if c.get("username") else None,
                "preview":     c.get("text") or "",
                "url":         None,
                "occurred_at": c.get("timestamp"),
            })
    return out


async def _poll_tiktok(user_id: str) -> list[dict[str, Any]]:
    """TikTok — only sandbox-approved apps can read comments; return empty
    gracefully if the token isn't scoped."""
    from services.workflows.workflow_services import _from_vault, _http
    token = await _from_vault(user_id, "tiktok")
    if not token:
        return []
    s, body, _ = await _http("GET",
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {token}"})
    if s != 200 or not body:
        return []
    now = datetime.now(timezone.utc).isoformat()
    u = ((body.get("data") or {}).get("user") or {})
    return [{
        "external_id": f"heartbeat:{now[:10]}",
        "kind":        "heartbeat",
        "from":        u.get("display_name"),
        "preview":     f"Followers: {u.get('follower_count', 0)}",
        "url":         "https://www.tiktok.com/",
        "occurred_at": now,
    }]


register_poller("x",         _poll_x)
register_poller("slack",     _poll_slack)
register_poller("discord",   _poll_discord)
register_poller("telegram",  _poll_telegram)
register_poller("whatsapp",  _poll_whatsapp)
register_poller("linkedin",  _poll_linkedin)
register_poller("youtube",   _poll_youtube)
register_poller("facebook",  _poll_facebook)
register_poller("instagram", _poll_instagram)
register_poller("tiktok",    _poll_tiktok)
