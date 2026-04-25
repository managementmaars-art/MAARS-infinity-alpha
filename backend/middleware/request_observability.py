"""
ASGI middleware: per-request correlation ID + per-IP rate limit + access log.

Pipeline on every /api/* request:
    1. Read or mint an `X-Request-ID` — bind it to request_context contextvars.
    2. Per-IP rate limit check (pre-auth).
    3. Time the response, attach `X-Request-ID` + `X-Response-Time-Ms` headers.
    4. Emit one structured INFO log line with method, path, status, latency.

Auth-level user_id is bound later, by v1_gateway / auth helpers, via
`request_context.set_user_id`.
"""
from __future__ import annotations

import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services import rate_limit_ip
from services.request_context import get_request_id, get_user_id, new_request_id, set_context

logger = logging.getLogger("maars.request")


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if fwd:
        return fwd
    return (request.client.host if request.client else "") or ""


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Correlation ID + per-IP rate limit + access log."""

    def __init__(self, app, *, rpm_per_ip: int = 300, protected_prefix: str = "/api/"):
        super().__init__(app)
        self.rpm_per_ip = int(rpm_per_ip)
        self.protected_prefix = protected_prefix

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        req_id = request.headers.get("x-request-id") or new_request_id()
        set_context(request_id=req_id)

        # Per-IP rate limit — protects ALL API surfaces, including auth endpoints.
        if request.url.path.startswith(self.protected_prefix):
            allowed, count, retry = rate_limit_ip.check(_client_ip(request), rpm=self.rpm_per_ip)
            if not allowed:
                logger.warning(
                    "ip_rate_limited ip=%s path=%s count=%d retry_in=%ds",
                    _client_ip(request), request.url.path, count, retry,
                )
                resp = JSONResponse(
                    status_code=429,
                    content={"error": {
                        "type": "ip_rate_limited",
                        "message": f"Too many requests from this IP. Retry in {retry}s.",
                        "retry_after_seconds": retry,
                    }},
                    headers={
                        "Retry-After": str(retry),
                        "X-RateLimit-Scope": "ip",
                        "X-Request-ID": req_id,
                    },
                )
                return resp

        t0 = time.time()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = int((time.time() - t0) * 1000)
            logger.exception(
                "request_crashed method=%s path=%s latency_ms=%d request_id=%s",
                request.method, request.url.path, elapsed_ms, req_id,
            )
            raise

        elapsed_ms = int((time.time() - t0) * 1000)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)

        logger.info(
            "request method=%s path=%s status=%s latency_ms=%d user_id=%s request_id=%s",
            request.method, request.url.path, response.status_code,
            elapsed_ms, get_user_id() or "-", get_request_id() or req_id,
        )
        return response
