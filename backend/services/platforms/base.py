"""Base platform adapter — the uniform contract every social platform
implements. Lets the workflow executor, content publisher, and social
routes address any platform with one API.

Every method returns a plain dict so it's JSON-serializable for the
workflow executor and the SSE progress stream.
"""
from __future__ import annotations
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class PlatformError(Exception):
    def __init__(self, message: str, *, status: int | None = None, platform: str = ""):
        super().__init__(message)
        self.status = status
        self.platform = platform


@dataclass
class PublishResult:
    ok: bool
    platform: str
    post_id: str | None = None
    url: str | None = None
    error: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "platform": self.platform,
            "post_id": self.post_id, "url": self.url,
            "error": self.error, "raw": self.raw,
        }


class BasePlatformAdapter:
    """Subclass this. Leave methods raising NotImplementedError for
    features the platform doesn't support — callers check with
    `.supports(feature)` before assuming."""

    platform: str = "base"
    supports_posting: bool = True
    supports_media: bool = True
    supports_video: bool = True
    supports_scheduling: bool = False
    supports_stats: bool = True
    supports_delete: bool = True

    # ── OAuth ────────────────────────────────────────────────────────

    def client_id(self) -> str | None:
        """Read the platform's developer app client_id from env.
        Each adapter overrides with its specific env var name."""
        return None

    def client_secret(self) -> str | None:
        return None

    def oauth_authorize_url(self, *, state: str, redirect_uri: str,
                            scopes: list[str] | None = None) -> str:
        raise NotImplementedError

    async def oauth_exchange(self, *, code: str, redirect_uri: str,
                             verifier: str | None = None) -> dict[str, Any]:
        """Exchange an authorization code for access/refresh tokens.
        Returns a dict suitable for credential_vault.Credential."""
        raise NotImplementedError

    async def refresh(self, cred) -> Any | None:
        """Providers that use refresh tokens override this. Default: no-op."""
        return None

    # ── Posting ──────────────────────────────────────────────────────

    async def publish(
        self, *,
        user_id: str,
        text: str,
        media_urls: list[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    async def stats(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        raise NotImplementedError

    async def delete(self, *, user_id: str, post_id: str) -> dict[str, Any]:
        raise NotImplementedError

    # ── Shared helpers ───────────────────────────────────────────────

    def supports(self, feature: str) -> bool:
        return bool(getattr(self, f"supports_{feature}", False))

    async def _get_creds(self, user_id: str):
        from services import credential_vault
        return await credential_vault.get(self.platform, user_id=user_id, kind="oauth")

    async def _require_creds(self, user_id: str):
        cred = await self._get_creds(user_id)
        if cred is None or not cred.secret:
            raise PlatformError(
                f"No {self.platform} credentials for user {user_id}. "
                f"User needs to complete OAuth flow.",
                status=401, platform=self.platform,
            )
        return cred

    def _env(self, name: str, *fallbacks: str) -> str | None:
        for n in (name, *fallbacks):
            v = os.environ.get(n)
            if v:
                return v
        return None
