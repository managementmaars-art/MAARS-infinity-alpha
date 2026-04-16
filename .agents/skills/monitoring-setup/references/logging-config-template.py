"""
logging-config-template.py -- structlog setup for FastAPI applications.

Configures structured JSON logging with request context, correlation IDs,
and proper log level handling. Drop this into your FastAPI project and call
setup_logging() during application startup.

Usage:
    from logging_config import setup_logging
    setup_logging(log_level="INFO", json_format=True)
"""

import logging
import sys
import uuid
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def setup_logging(
    log_level: str = "INFO",
    json_format: bool = True,
    service_name: str = "backend",
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: If True, output JSON logs. If False, output colored console logs.
        service_name: Name of the service (included in every log entry).
    """
    # Choose renderer based on format preference
    if json_format:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Shared processors for both structlog and stdlib loggers
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_service_name(service_name),
    ]

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog formatting
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _add_service_name(service_name: str):
    """Create a processor that adds the service name to every log entry."""

    def processor(logger, method_name, event_dict):
        event_dict["service"] = service_name
        return event_dict

    return processor


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds request context to all log entries.

    Binds request_id, method, path, and client_ip to structlog context
    variables so they appear in every log entry during the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get or generate request ID
        request_id = request.headers.get(
            "X-Request-ID", str(uuid.uuid4())
        )

        # Clear and bind context variables for this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        logger = structlog.get_logger()

        # Log request start
        logger.info(
            "request_started",
            query_params=str(request.query_params) if request.query_params else None,
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            raise

        # Add request ID to response headers for correlation
        response.headers["X-Request-ID"] = request_id

        # Log request completion
        logger.info(
            "request_completed",
            status_code=response.status_code,
        )

        return response


# ---------------------------------------------------------------------------
# Usage example (in main.py):
# ---------------------------------------------------------------------------
#
# from fastapi import FastAPI
# from logging_config import setup_logging, LoggingContextMiddleware
#
# app = FastAPI()
#
# # Initialize logging
# setup_logging(
#     log_level=os.getenv("LOG_LEVEL", "INFO"),
#     json_format=os.getenv("APP_ENV") != "development",
#     service_name="my-backend",
# )
#
# # Add logging context middleware
# app.add_middleware(LoggingContextMiddleware)
#
# # Use structlog throughout the application
# import structlog
# logger = structlog.get_logger()
#
# @app.get("/users/{user_id}")
# async def get_user(user_id: int):
#     logger.info("fetching_user", user_id=user_id)
#     user = await user_service.get(user_id)
#     if not user:
#         logger.warning("user_not_found", user_id=user_id)
#         raise HTTPException(404, "User not found")
#     return user
#
# ---------------------------------------------------------------------------
# Example log output (JSON format):
# ---------------------------------------------------------------------------
#
# {
#   "request_id": "abc-123-def",
#   "method": "GET",
#   "path": "/users/42",
#   "client_ip": "10.0.0.1",
#   "service": "my-backend",
#   "event": "fetching_user",
#   "user_id": 42,
#   "level": "info",
#   "timestamp": "2024-01-15T14:30:00.123456Z",
#   "logger": "my_module"
# }
