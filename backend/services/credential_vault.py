"""Unified credential vault — one store for every OAuth + API key.

Before: creds lived in three places:
  - `db.social_connections` (platform OAuth dicts, no refresh)
  - `db.integrations`       (system-wide provider keys)
  - `users.api_keys`        (user-scoped keys)

Tokens never refreshed. Same platform often stored twice with slight
shape drift. Secrets written in the clear.

After: every credential lives in one collection (`credentials`) with:
  - Envelope encryption via Fernet (key from MAARS_VAULT_KEY env).
  - Uniform shape: `{scope, scope_id, provider, kind, secret_enc,
    public, expires_at, refresh_secret_enc, metadata}`.
  - Scope layers: "system" | "user" | "org".  Resolution precedence:
    user > org > system.
  - Per-provider refresh adapter → get() transparently refreshes if
    expires_at within _REFRESH_LEEWAY_SECONDS.

This module stays simple: the full OAuth login handshake lives in
routes/oauth.py; this module just stores and returns the creds, plus
refreshes them when asked.

If MAARS_VAULT_KEY isn't set we fall back to a deterministic dev key
with a loud log line — prod deployments MUST set it.
"""
from __future__ import annotations
import base64
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

_REFRESH_LEEWAY_SECONDS = 300   # refresh 5 min before actual expiry
_INDEX_READY = False


def _key() -> bytes:
    """Derive the Fernet key from MAARS_VAULT_KEY. Accepts any length
    string; we hash to 32 bytes and base64-urlsafe encode to match
    Fernet's expected format."""
    raw = os.environ.get("MAARS_VAULT_KEY")
    if not raw:
        logger.warning(
            "MAARS_VAULT_KEY not set — using default dev key. "
            "DO NOT deploy to production without setting this env var."
        )
        raw = "maars-default-dev-vault-key-change-me"
    h = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(h)


def _cipher():
    try:
        from cryptography.fernet import Fernet
        return Fernet(_key())
    except ImportError as exc:
        raise RuntimeError(
            "credential_vault requires the `cryptography` package. "
            "pip install cryptography"
        ) from exc


def _encrypt(plain: str) -> bytes:
    if plain is None:
        return b""
    return _cipher().encrypt(plain.encode())


def _decrypt(blob: bytes | None) -> str:
    if not blob:
        return ""
    try:
        return _cipher().decrypt(blob).decode()
    except Exception as exc:
        logger.warning("vault decrypt failed: %s", exc)
        return ""


async def _ensure_indexes() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return
    try:
        from db import db
        await db.credentials.create_index(
            [("scope", 1), ("scope_id", 1), ("provider", 1), ("kind", 1)],
            unique=True,
        )
        await db.credentials.create_index("expires_at")
        _INDEX_READY = True
    except Exception as exc:
        logger.info("credential_vault index deferred: %s", exc)


@dataclass
class Credential:
    scope: str          # "system" | "user" | "org"
    scope_id: str       # user_id / org_id / "global" for system
    provider: str       # "twitter" | "linkedin" | "meta" | "tiktok" | "youtube" | "openai" | ...
    kind: str           # "oauth" | "api_key" | "webhook_secret" | "refresh"
    secret: str         # the actual token/key (stored encrypted)
    refresh_secret: Optional[str] = None
    expires_at: Optional[float] = None   # epoch seconds, None = no expiry
    public: dict[str, Any] = field(default_factory=dict)  # non-secret metadata (account_id, username, etc.)
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Public API ───────────────────────────────────────────────────────

async def put(cred: Credential) -> None:
    """Store or overwrite a credential. Encrypts secret + refresh_secret."""
    await _ensure_indexes()
    from db import db
    now = time.time()
    doc = {
        "scope":      cred.scope,
        "scope_id":   cred.scope_id,
        "provider":   cred.provider,
        "kind":       cred.kind,
        "secret_enc": _encrypt(cred.secret),
        "refresh_secret_enc": _encrypt(cred.refresh_secret) if cred.refresh_secret else None,
        "expires_at": cred.expires_at,
        "public":     cred.public,
        "metadata":   cred.metadata,
        "updated_at": now,
    }
    await db.credentials.update_one(
        {"scope": cred.scope, "scope_id": cred.scope_id,
         "provider": cred.provider, "kind": cred.kind},
        {"$set": doc, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )


async def _load(scope: str, scope_id: str, provider: str, kind: str) -> Credential | None:
    from db import db
    doc = await db.credentials.find_one({
        "scope": scope, "scope_id": scope_id,
        "provider": provider, "kind": kind,
    })
    if not doc:
        return None
    return Credential(
        scope=doc["scope"], scope_id=doc["scope_id"],
        provider=doc["provider"], kind=doc["kind"],
        secret=_decrypt(doc.get("secret_enc")),
        refresh_secret=_decrypt(doc.get("refresh_secret_enc")) or None,
        expires_at=doc.get("expires_at"),
        public=doc.get("public") or {},
        metadata=doc.get("metadata") or {},
    )


async def get(
    provider: str,
    *,
    user_id: str | None = None,
    org_id: str | None = None,
    kind: str = "oauth",
    auto_refresh: bool = True,
) -> Credential | None:
    """Resolve a credential. Precedence: user → org → system.

    If auto_refresh, a credential within the refresh leeway is refreshed
    via the provider's registered refresh function (if any)."""
    await _ensure_indexes()
    cred: Credential | None = None
    if user_id:
        cred = await _load("user", user_id, provider, kind)
    if cred is None and org_id:
        cred = await _load("org", org_id, provider, kind)
    if cred is None:
        cred = await _load("system", "global", provider, kind)
    if cred is None:
        return None

    if auto_refresh and cred.expires_at and cred.refresh_secret:
        if cred.expires_at - time.time() < _REFRESH_LEEWAY_SECONDS:
            try:
                fresh = await _refresh(cred)
                if fresh is not None:
                    await put(fresh)
                    cred = fresh
            except Exception as exc:
                logger.info("vault refresh failed for %s: %s", provider, exc)
    return cred


async def delete(provider: str, *, user_id: str | None = None,
                 org_id: str | None = None, kind: str = "oauth") -> bool:
    from db import db
    scope, scope_id = ("system", "global")
    if user_id:
        scope, scope_id = "user", user_id
    elif org_id:
        scope, scope_id = "org", org_id
    res = await db.credentials.delete_one({
        "scope": scope, "scope_id": scope_id,
        "provider": provider, "kind": kind,
    })
    return bool(res.deleted_count)


async def list_for(
    *, user_id: str | None = None, org_id: str | None = None,
) -> list[dict[str, Any]]:
    """Admin-facing: list credentials (PUBLIC fields only) for a scope."""
    from db import db
    scopes: list[tuple[str, str]] = [("system", "global")]
    if user_id:
        scopes.append(("user", user_id))
    if org_id:
        scopes.append(("org", org_id))
    out: list[dict[str, Any]] = []
    for scope, scope_id in scopes:
        async for doc in db.credentials.find({"scope": scope, "scope_id": scope_id}):
            out.append({
                "scope":      doc["scope"],
                "scope_id":   doc["scope_id"],
                "provider":   doc["provider"],
                "kind":       doc["kind"],
                "public":     doc.get("public") or {},
                "expires_at": doc.get("expires_at"),
                "has_refresh": bool(doc.get("refresh_secret_enc")),
                "updated_at": doc.get("updated_at"),
            })
    return out


# ── Refresh dispatch ─────────────────────────────────────────────────
# Each provider registers a refresh callback. Callback signature:
#   async def refresh(cred) -> Credential | None
# Returns a new Credential (with updated secret/expires_at) or None
# to abort.

_REFRESH_HANDLERS: dict[str, Any] = {}


def register_refresh_handler(provider: str, fn) -> None:
    _REFRESH_HANDLERS[provider] = fn


async def _refresh(cred: Credential) -> Credential | None:
    fn = _REFRESH_HANDLERS.get(cred.provider)
    if fn is None:
        return None
    return await fn(cred)


# ── Convenience: map legacy `db.integrations` entries into the vault ─

async def import_legacy_integrations() -> int:
    """One-shot migration: read `db.integrations` into the vault at
    system scope. Safe to re-run; upserts by key."""
    from db import db
    count = 0
    try:
        async for doc in db.integrations.find({}):
            provider = doc.get("provider") or doc.get("name")
            secret = doc.get("api_key") or doc.get("secret") or doc.get("token")
            if not provider or not secret:
                continue
            await put(Credential(
                scope="system", scope_id="global",
                provider=str(provider).lower(), kind="api_key",
                secret=str(secret),
                public={"imported_from": "legacy_integrations"},
            ))
            count += 1
    except Exception as exc:
        logger.info("legacy import failed: %s", exc)
    return count
