"""
metrics-config-template.py -- Prometheus metrics setup for FastAPI applications.

Configures Prometheus client metrics with RED method (Rate, Errors, Duration)
and USE method (Utilization, Saturation, Errors) metrics. Includes middleware
for automatic HTTP request instrumentation.

Usage:
    from metrics_config import setup_metrics
    setup_metrics(app)
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# ---------------------------------------------------------------------------
# RED Metrics (Request-driven)
# ---------------------------------------------------------------------------

# Rate: Total number of requests
HTTP_REQUEST_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    labelnames=["method", "endpoint", "status_code"],
)

# Duration: Request latency distribution
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Errors: Specifically track 5xx errors
HTTP_SERVER_ERRORS = Counter(
    "http_server_errors_total",
    "Total number of HTTP 5xx server errors",
    labelnames=["method", "endpoint", "status_code"],
)

# Request size
HTTP_REQUEST_SIZE = Histogram(
    "http_request_size_bytes",
    "HTTP request body size in bytes",
    labelnames=["method", "endpoint"],
    buckets=[100, 1000, 10000, 100000, 1000000],
)

# Response size
HTTP_RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response body size in bytes",
    labelnames=["method", "endpoint"],
    buckets=[100, 1000, 10000, 100000, 1000000],
)

# Requests in progress
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    labelnames=["method"],
)

# ---------------------------------------------------------------------------
# USE Metrics (Resource-driven)
# ---------------------------------------------------------------------------

# Database connection pool
DB_POOL_SIZE = Gauge(
    "db_connection_pool_size",
    "Maximum size of the database connection pool",
    labelnames=["pool_name"],
)

DB_POOL_CHECKED_IN = Gauge(
    "db_connection_pool_checked_in",
    "Number of connections currently available in the pool",
    labelnames=["pool_name"],
)

DB_POOL_CHECKED_OUT = Gauge(
    "db_connection_pool_checked_out",
    "Number of connections currently in use from the pool",
    labelnames=["pool_name"],
)

DB_POOL_OVERFLOW = Gauge(
    "db_connection_pool_overflow",
    "Number of connections in overflow beyond pool size",
    labelnames=["pool_name"],
)

# Redis connections
REDIS_CONNECTIONS_ACTIVE = Gauge(
    "redis_connections_active",
    "Number of active Redis connections",
)

# Cache metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    labelnames=["cache_name"],
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    labelnames=["cache_name"],
)

# ---------------------------------------------------------------------------
# Business Metrics
# ---------------------------------------------------------------------------

ACTIVE_USERS = Gauge(
    "active_users_total",
    "Number of currently active users",
)

BACKGROUND_TASKS_QUEUED = Gauge(
    "background_tasks_queued",
    "Number of background tasks waiting to be processed",
    labelnames=["task_type"],
)

BACKGROUND_TASKS_PROCESSED = Counter(
    "background_tasks_processed_total",
    "Total number of background tasks processed",
    labelnames=["task_type", "status"],
)

# Application info
APP_INFO = Info(
    "app",
    "Application metadata",
)


# ---------------------------------------------------------------------------
# Prometheus Middleware
# ---------------------------------------------------------------------------

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically instruments HTTP requests with Prometheus metrics.

    Records request count, duration, errors, and in-progress gauges for every
    HTTP request.
    """

    # Endpoints to exclude from metrics (avoid noise from internal endpoints)
    EXCLUDED_PATHS = {"/metrics", "/health", "/health/ready"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path

        # Skip metrics for excluded paths
        if path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Normalize path to avoid high-cardinality labels
        # e.g., /users/123 -> /users/{id}
        endpoint = self._normalize_path(path)

        # Track in-progress requests
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method).inc()

        # Record request size
        content_length = request.headers.get("content-length")
        if content_length:
            HTTP_REQUEST_SIZE.labels(
                method=method, endpoint=endpoint
            ).observe(int(content_length))

        # Time the request
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            # Record unhandled exception as 500
            HTTP_REQUEST_TOTAL.labels(
                method=method, endpoint=endpoint, status_code="500"
            ).inc()
            HTTP_SERVER_ERRORS.labels(
                method=method, endpoint=endpoint, status_code="500"
            ).inc()
            raise
        finally:
            duration = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method).dec()

        status_code = str(response.status_code)

        # Record request count
        HTTP_REQUEST_TOTAL.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        # Record server errors
        if response.status_code >= 500:
            HTTP_SERVER_ERRORS.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

        # Record response size
        response_size = response.headers.get("content-length")
        if response_size:
            HTTP_RESPONSE_SIZE.labels(
                method=method, endpoint=endpoint
            ).observe(int(response_size))

        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize URL path to reduce label cardinality.

        Replaces numeric path segments with {id} placeholder.
        /users/123/posts/456 -> /users/{id}/posts/{id}
        """
        parts = path.strip("/").split("/")
        normalized = []
        for part in parts:
            if part.isdigit():
                normalized.append("{id}")
            else:
                try:
                    # Check for UUID-like segments
                    if len(part) == 36 and part.count("-") == 4:
                        normalized.append("{id}")
                    else:
                        normalized.append(part)
                except (ValueError, AttributeError):
                    normalized.append(part)
        return "/" + "/".join(normalized)


# ---------------------------------------------------------------------------
# Setup Function
# ---------------------------------------------------------------------------

def setup_metrics(
    app: FastAPI,
    app_version: str = "unknown",
    app_env: str = "development",
) -> None:
    """
    Set up Prometheus metrics for a FastAPI application.

    Adds the PrometheusMiddleware and creates the /metrics endpoint.

    Args:
        app: The FastAPI application instance.
        app_version: Application version string.
        app_env: Application environment (development, staging, production).
    """
    # Set application info
    APP_INFO.info({
        "version": app_version,
        "environment": app_env,
    })

    # Add metrics middleware
    app.add_middleware(PrometheusMiddleware)

    # Add /metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint."""
        return StarletteResponse(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )


# ---------------------------------------------------------------------------
# Database Pool Metrics Collector
# ---------------------------------------------------------------------------

def update_db_pool_metrics(engine, pool_name: str = "default") -> None:
    """
    Update database connection pool metrics from SQLAlchemy engine.

    Call this periodically or in a middleware to keep metrics current.

    Args:
        engine: SQLAlchemy engine instance.
        pool_name: Label for the connection pool.
    """
    pool = engine.pool
    DB_POOL_SIZE.labels(pool_name=pool_name).set(pool.size())
    DB_POOL_CHECKED_IN.labels(pool_name=pool_name).set(pool.checkedin())
    DB_POOL_CHECKED_OUT.labels(pool_name=pool_name).set(pool.checkedout())
    DB_POOL_OVERFLOW.labels(pool_name=pool_name).set(pool.overflow())


# ---------------------------------------------------------------------------
# Usage example (in main.py):
# ---------------------------------------------------------------------------
#
# from fastapi import FastAPI
# from metrics_config import setup_metrics
#
# app = FastAPI()
# setup_metrics(app, app_version="1.2.3", app_env="production")
#
# # Use metrics in your code:
# from metrics_config import CACHE_HITS, CACHE_MISSES
#
# async def get_cached_data(key: str):
#     value = await redis.get(key)
#     if value:
#         CACHE_HITS.labels(cache_name="user_cache").inc()
#         return value
#     CACHE_MISSES.labels(cache_name="user_cache").inc()
#     value = await fetch_from_db(key)
#     await redis.set(key, value, ex=300)
#     return value
