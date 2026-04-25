"""Per-user rate limiting — protects against abuse.

A single free-tier user hammering /api/generate/image could exhaust
your free-tier provider quotas in minutes. This middleware enforces a
rolling 60-second window per (user_id, endpoint_group) pair.

Default limits (generous; tighten via env):
  MAARS_RATE_LIMIT_CHAT=60       — chat completions per minute
  MAARS_RATE_LIMIT_GENERATION=30 — image/video/tts/stt per minute
  MAARS_RATE_LIMIT_CAMPAIGN=5    — new campaign launches per minute

Applies to authenticated requests. Anonymous requests are rate-limited
by IP using the same logic.
"""
from __future__ import annotations
import os
import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import Request
from fastapi.responses import JSONResponse


_WINDOW_SECONDS = 60.0

_LIMITS = {
    "chat":       int(os.environ.get("MAARS_RATE_LIMIT_CHAT", "60")),
    "generation": int(os.environ.get("MAARS_RATE_LIMIT_GENERATION", "30")),
    "campaign":   int(os.environ.get("MAARS_RATE_LIMIT_CAMPAIGN", "5")),
    "leads":      int(os.environ.get("MAARS_RATE_LIMIT_LEADS", "20")),
    "default":    int(os.environ.get("MAARS_RATE_LIMIT_DEFAULT", "120")),
}


# (user_id/ip, group) → deque of timestamps
_windows: dict[tuple[str, str], Deque[float]] = defaultdict(deque)


def _classify(path: str) -> str:
    """Map URL path → rate-limit group."""
    if "/chat" in path or "/v1/chat/completions" in path:
        return "chat"
    if "/generate/" in path or "/tts/" in path or "/audio/" in path:
        return "generation"
    if "/campaigns/run" in path:
        return "campaign"
    if "/leads/" in path:
        return "leads"
    return "default"


def _prune(key: tuple[str, str], now: float) -> None:
    dq = _windows[key]
    cutoff = now - _WINDOW_SECONDS
    while dq and dq[0] < cutoff:
        dq.popleft()


async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware. Registered via app.middleware('http')."""
    path = request.url.path
    # Skip non-API + admin + health paths
    if not path.startswith("/api") or path.startswith(("/api/admin", "/api/health")):
        return await call_next(request)

    group = _classify(path)
    limit = _LIMITS.get(group, _LIMITS["default"])

    # Identify caller: user_id if Authorization header, else client IP
    caller_id = ""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        caller_id = "user:" + auth[:32]  # token prefix as identity (prevents decode cost)
    else:
        caller_id = "ip:" + (request.client.host if request.client else "unknown")

    key = (caller_id, group)
    now = time.time()
    _prune(key, now)
    dq = _windows[key]

    if len(dq) >= limit:
        retry_after = int(_WINDOW_SECONDS - (now - dq[0])) + 1
        return JSONResponse(
            {
                "error": "rate_limited",
                "detail": f"Too many requests in the {group} group. Limit is {limit}/min.",
                "retry_after_seconds": retry_after,
            },
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )

    dq.append(now)
    resp = await call_next(request)
    resp.headers["X-RateLimit-Group"] = group
    resp.headers["X-RateLimit-Limit"] = str(limit)
    resp.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(dq)))
    return resp
