"""Integration Driver — one unified surface for every connected app.

Gives agents / workflows a single call shape:

    await integration_driver.act(
        provider="linkedin",
        action="post",
        params={"content": "Launching MAARS!"},
        user_id=uid,
    )
    → {"ok": True, "mode": "browser", "output": {...}}

Under the hood the driver picks the best available mode per provider:

  • `api`      — provider has a real API adapter (already in workflow_services)
  • `browser`  — no API (or API-gated); drive the live web app via the
                 existing BrowserAgent session pool using saved cookies
  • `unavailable` — neither API nor browser session wired for this user

`act()` does no provider logic itself — it delegates to per-provider
handlers registered via `register_driver()`. That keeps each provider's
quirks contained and makes this file tiny.

Authority model: the caller (agent/workflow) must pass a `user_id` and
the driver uses only credentials + browser sessions scoped to that
user. No cross-user access.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Optional

logger = logging.getLogger(__name__)


# ── Driver registration ──────────────────────────────────────────────

@dataclass
class DriverSpec:
    provider:   str
    display_name: str
    category:   str                      # "social" | "crm" | "ecom" | etc.
    api_actions: list[str] = field(default_factory=list)
    browser_actions: list[str] = field(default_factory=list)
    api_handler:     Optional[Callable[..., Awaitable[dict]]] = None
    browser_handler: Optional[Callable[..., Awaitable[dict]]] = None
    login_url:       Optional[str] = None   # where user signs in (for browser mode)
    docs_url:        Optional[str] = None


_DRIVERS: dict[str, DriverSpec] = {}


def register_driver(spec: DriverSpec) -> None:
    _DRIVERS[spec.provider] = spec


def list_drivers() -> list[dict[str, Any]]:
    out = []
    for d in _DRIVERS.values():
        out.append({
            "provider":       d.provider,
            "display_name":   d.display_name,
            "category":       d.category,
            "api_actions":    d.api_actions,
            "browser_actions": d.browser_actions,
            "login_url":      d.login_url,
            "docs_url":       d.docs_url,
            "modes_available": _modes_for(d),
        })
    return out


def _modes_for(d: DriverSpec) -> list[str]:
    m: list[str] = []
    if d.api_handler:     m.append("api")
    if d.browser_handler: m.append("browser")
    return m


# ── Status (does this user have creds / session for this provider) ──

async def status(provider: str, user_id: str) -> dict[str, Any]:
    d = _DRIVERS.get(provider)
    if not d:
        return {"provider": provider, "known": False}
    from services import credential_vault
    has_api_cred = False
    try:
        cred = await credential_vault.get(provider, user_id=user_id)
        has_api_cred = bool(cred and cred.secret)
    except Exception:
        pass
    # Browser session = any persisted profile cookies
    from pathlib import Path
    browser_has_session = False
    try:
        storage = Path("browser_data/storage_states") / f"{user_id}.json"
        browser_has_session = storage.exists() and storage.stat().st_size > 50
    except Exception:
        pass
    return {
        "provider":             provider,
        "display_name":         d.display_name,
        "category":             d.category,
        "modes_available":      _modes_for(d),
        "has_api_credential":   has_api_cred,
        "browser_has_session":  browser_has_session,
        "ready_modes": (
            (["api"] if has_api_cred and d.api_handler else [])
            + (["browser"] if browser_has_session and d.browser_handler else [])
        ),
        "api_actions":          d.api_actions,
        "browser_actions":      d.browser_actions,
    }


# ── Main dispatch ───────────────────────────────────────────────────

async def act(
    *,
    provider: str,
    action: str,
    params: dict | None = None,
    user_id: str,
    prefer_mode: str | None = None,   # "api" | "browser" | None (auto)
) -> dict[str, Any]:
    """Execute a provider action. Picks the best available mode unless
    the caller pinned one. Returns:

        {ok, mode, provider, action, output, latency_ms}
    """
    d = _DRIVERS.get(provider)
    if not d:
        return {"ok": False, "error": f"unknown_provider: {provider}"}
    start = time.time()
    # Resolve mode
    s = await status(provider, user_id)
    ready = s.get("ready_modes") or []
    if prefer_mode and prefer_mode in ready:
        mode = prefer_mode
    elif ready:
        # Prefer API when available — faster, less fragile
        mode = "api" if "api" in ready else ready[0]
    else:
        return {
            "ok": False,
            "error": f"no_mode_ready: connect {provider} (API credential or browser session)",
            "modes_available": s.get("modes_available"),
        }
    handler = d.api_handler if mode == "api" else d.browser_handler
    if not handler:
        return {"ok": False, "error": f"no_handler_for_mode: {mode}"}
    # Validate action
    allowed = d.api_actions if mode == "api" else d.browser_actions
    if allowed and action not in allowed:
        return {
            "ok": False,
            "error": f"unsupported_action '{action}' in mode '{mode}'",
            "supported": allowed,
        }
    try:
        output = await handler(user_id=user_id, action=action, params=params or {})
    except Exception as exc:
        logger.warning("integration_driver %s/%s/%s failed: %s",
                       provider, mode, action, exc)
        return {
            "ok": False, "mode": mode, "provider": provider, "action": action,
            "error": f"{type(exc).__name__}: {exc}",
            "latency_ms": int((time.time() - start) * 1000),
        }
    latency_ms = int((time.time() - start) * 1000)
    # Audit log — every integration action lands in Mongo for traceability
    try:
        from db import db
        from datetime import datetime, timezone
        await db.integration_action_log.insert_one({
            "user_id":   user_id,
            "provider":  provider,
            "action":    action,
            "mode":      mode,
            "ok":        bool((output or {}).get("ok", True)),
            "latency_ms": latency_ms,
            "params_keys": list((params or {}).keys()),
            "at":        datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass
    return {
        "ok":         bool((output or {}).get("ok", True)),
        "mode":       mode,
        "provider":   provider,
        "action":     action,
        "output":     output,
        "latency_ms": latency_ms,
    }


# ── Browser helpers shared across drivers ───────────────────────────

async def _open_session(user_id: str, start_url: str | None = None):
    """Open (or reuse) the user's browser session. All browser drivers
    go through this so 2FA handoff + screenshot streaming are consistent."""
    from services.browser_service import get_browser_pool
    pool = get_browser_pool()
    return await pool.open(user_id=user_id, agent_id="integration_driver",
                            start_url=start_url)


async def _goto(session, url: str) -> None:
    await session.navigate(url, caller="system")


async def _find_and_click(session, selector: str) -> dict:
    try:
        return await session.click(selector, caller="system")
    except Exception as exc:
        return {"ok": False, "error": f"click_failed: {exc}"}


async def _extract_text_contains(session, text_fragment: str) -> bool:
    try:
        body = await session.extract_text("body")
        return text_fragment.lower() in (body or "").lower()
    except Exception:
        return False


# ── Built-in driver registrations ────────────────────────────────────
# Kept in a separate module so this file stays orchestration-only.
# Imported for side-effect at module load.
try:
    from services import integration_handlers  # noqa: F401
except Exception as exc:
    logger.info("integration_handlers package load deferred: %s", exc)
