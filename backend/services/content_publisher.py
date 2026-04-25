"""Content → multi-platform publisher — the missing chain.

Before: `content.generate` produced text; `social_media.post` accepted
text. No single call went from "write me a post about X" to
"it's live on LinkedIn + X + Facebook."

This module does that. One call:

    await publish_content(
        user_id, content_id,
        platforms=["x", "linkedin", "facebook"],
        extras={"x": {"hashtags": ["#ai"]}, "linkedin": {"visibility": "PUBLIC"}},
    )

Returns a per-platform result map. Parallel fan-out, one PublishResult
per platform. Failures on one platform never block others.

Works for already-generated content (looked up by content_id) OR
ad-hoc content passed as a `text` override.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def publish_content(
    *,
    user_id: str,
    content_id: str | None = None,
    text: str | None = None,
    media_urls: list[str] | None = None,
    platforms: list[str],
    extras: dict[str, dict[str, Any]] | None = None,
    schedule_at: float | None = None,
) -> dict[str, Any]:
    """Publish one piece of content to N platforms in parallel.

    content_id : optional — pulls the text from `generated_content` collection.
    text       : optional — direct text override. One of content_id or text required.
    platforms  : list of platform slugs (x, linkedin, instagram, facebook, tiktok, youtube).
    extras     : per-platform param overrides, e.g. {"facebook": {"page_id": "..."}}.
    schedule_at: if set (epoch seconds), schedule the post via our scheduler
                 rather than firing immediately (for platforms that don't
                 support native scheduling).
    """
    from services.platforms import get_adapter
    from db import db
    extras = extras or {}

    if not text and content_id:
        doc = await db.generated_content.find_one(
            {"content_id": content_id, "user_id": user_id},
            {"content": 1, "text": 1, "output": 1, "_id": 0},
        )
        if not doc:
            return {"ok": False, "error": f"content {content_id} not found"}
        text = doc.get("content") or doc.get("text") or doc.get("output", "")
    if not text:
        return {"ok": False, "error": "no text to publish"}

    # If schedule_at is set, persist to `scheduled_posts` collection —
    # the scheduler picks it up at the right time. For immediate sends
    # we fire now.
    if schedule_at:
        import time as _t
        from datetime import datetime, timezone
        docs = []
        for p in platforms:
            docs.append({
                "user_id": user_id,
                "platform": p,
                "text": text,
                "media_urls": media_urls or [],
                "params": extras.get(p) or {},
                "scheduled_at": schedule_at,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "scheduled",
                "_id": None,
            })
        if docs:
            await db.scheduled_posts.insert_many(docs)
        return {"ok": True, "scheduled": len(docs), "scheduled_at": schedule_at}

    async def _publish_one(p: str) -> tuple[str, dict[str, Any]]:
        adapter = get_adapter(p)
        if adapter is None:
            return p, {"ok": False, "platform": p, "error": "unknown platform"}
        try:
            r = await adapter.publish(
                user_id=user_id, text=text,
                media_urls=media_urls or [],
                params=extras.get(p) or {},
            )
            return p, r
        except Exception as exc:
            logger.warning("publish %s crashed: %s", p, exc)
            return p, {"ok": False, "platform": p, "error": str(exc)[:300]}

    results = await asyncio.gather(*(_publish_one(p) for p in platforms))
    per_platform = dict(results)
    ok_count = sum(1 for _, r in results if r.get("ok"))

    # Record aggregate for audit + UI history.
    try:
        from datetime import datetime, timezone
        await db.published_content.insert_one({
            "user_id": user_id,
            "content_id": content_id,
            "text": text[:2000],
            "media_urls": media_urls or [],
            "platforms": platforms,
            "results": per_platform,
            "ok_count": ok_count,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "_id": None,
        })
    except Exception as exc:
        logger.info("published_content log failed: %s", exc)

    return {
        "ok": ok_count > 0,
        "published": ok_count,
        "failed": len(platforms) - ok_count,
        "per_platform": per_platform,
    }
