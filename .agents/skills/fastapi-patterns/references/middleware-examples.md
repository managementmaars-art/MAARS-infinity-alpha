# Middleware Examples

Complete middleware implementations for FastAPI applications.

---

## 1. Request Logging Middleware

Logs every request with method, path, status code, and duration.

```python
import time
import logging
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500  # Default if response fails

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start
            method = scope.get("method", "?")
            path = scope.get("path", "?")
            logger.info(
                "request completed",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
```

---

## 2. Request ID Middleware

Assigns a unique ID to each request for tracing.

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

---

## 3. Rate Limiting Middleware

Token bucket rate limiter with per-IP tracking.

```python
import time
from collections import defaultdict
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse


class RateLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        requests_per_minute: int = 60,
    ) -> None:
        self.app = app
        self.rate = requests_per_minute
        self.window = 60.0
        self.buckets: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, scope: Scope) -> str:
        # Check for proxy headers
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)
        now = time.time()

        # Clean old entries
        self.buckets[client_ip] = [
            t for t in self.buckets[client_ip] if now - t < self.window
        ]

        if len(self.buckets[client_ip]) >= self.rate:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "code": "RATE_LIMITED"},
                headers={
                    "Retry-After": str(int(self.window)),
                    "X-RateLimit-Limit": str(self.rate),
                    "X-RateLimit-Remaining": "0",
                },
            )
            await response(scope, receive, send)
            return

        self.buckets[client_ip].append(now)
        await self.app(scope, receive, send)
```

---

## 4. Error Handling Middleware

Catches unhandled exceptions and returns consistent error responses.

```python
import logging
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("api.errors")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                "Unhandled exception",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "code": "INTERNAL_ERROR",
                },
            )
```

---

## 5. CORS Configuration Examples

### Development (Permissive)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production (Restrictive)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://admin.example.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

---

## Recommended Middleware Order

Add middleware in this order (last added = outermost = executes first):

```python
# 5. Error handling (outermost — catches everything)
app.add_middleware(ErrorHandlingMiddleware)

# 4. Request timing/logging
app.add_middleware(RequestLoggingMiddleware)

# 3. Request ID assignment
app.add_middleware(RequestIdMiddleware)

# 2. Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 1. CORS (innermost — closest to routes)
app.add_middleware(CORSMiddleware, ...)
```

This ensures:
- CORS headers are always included (even on errors)
- Rate limiting runs before route processing
- Every request gets an ID before logging
- All requests are logged with timing
- Unhandled exceptions are caught and formatted
