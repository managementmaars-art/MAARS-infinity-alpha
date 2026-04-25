"""Social platform adapters — one file per platform, uniform contract.

Every adapter implements:
    class Adapter(BasePlatformAdapter):
        platform: str
        oauth_authorize_url(state, redirect_uri) -> str
        oauth_exchange(code, redirect_uri) -> Credential
        refresh(cred) -> Credential | None
        publish(user_id, text, media_urls, params) -> dict
        stats(user_id, post_id) -> dict
        delete(user_id, post_id) -> dict

The registry below maps a platform slug to its adapter instance. All
subsystems (workflow_executor, content_publisher, social_media routes)
fetch adapters from here instead of hard-coding per-platform logic.
"""
from __future__ import annotations
from typing import Any

from .base import BasePlatformAdapter, PlatformError, PublishResult
from .twitter import TwitterAdapter
from .linkedin import LinkedInAdapter
from .meta import MetaAdapter
from .tiktok import TikTokAdapter
from .youtube import YouTubeAdapter


_REGISTRY: dict[str, BasePlatformAdapter] = {
    "x":         TwitterAdapter(),
    "twitter":   TwitterAdapter(),
    "linkedin":  LinkedInAdapter(),
    "meta":      MetaAdapter(),
    "instagram": MetaAdapter(target="instagram"),
    "facebook":  MetaAdapter(target="facebook"),
    "tiktok":    TikTokAdapter(),
    "youtube":   YouTubeAdapter(),
}


def get_adapter(platform: str) -> BasePlatformAdapter | None:
    return _REGISTRY.get((platform or "").lower())


def all_adapters() -> dict[str, BasePlatformAdapter]:
    return dict(_REGISTRY)


__all__ = [
    "BasePlatformAdapter", "PlatformError", "PublishResult",
    "get_adapter", "all_adapters",
    "TwitterAdapter", "LinkedInAdapter", "MetaAdapter",
    "TikTokAdapter", "YouTubeAdapter",
]
