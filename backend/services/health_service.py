"""Health and readiness helpers for backend runtime checks."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

REQUIRED_ENV_VARS = {
    "MONGO_URL": "MongoDB connection string (for example mongodb://localhost:27017)",
    "DB_NAME": "Database name (for example maars_infinity)",
    "JWT_SECRET": "JWT signing secret used for authentication",
}

OPTIONAL_INTEGRATION_GROUPS = {
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "google_ai": ("GOOGLE_API_KEY",),
    "google_oauth": ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
    "stripe": ("STRIPE_SECRET_KEY",),
    "email_smtp": ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"),
    "email_resend": ("RESEND_API_KEY",),
    "twilio": ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"),
}

SERVICE_START_TIME = time.time()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_environment_configuration() -> dict[str, Any]:
    required = {
        name: {"configured": bool(os.environ.get(name)), "description": description}
        for name, description in REQUIRED_ENV_VARS.items()
    }

    optional_integrations: dict[str, Any] = {}
    for group_name, variables in OPTIONAL_INTEGRATION_GROUPS.items():
        configured_map = {var_name: bool(os.environ.get(var_name)) for var_name in variables}
        configured_count = sum(1 for value in configured_map.values() if value)
        optional_integrations[group_name] = {
            "configured": configured_count == len(variables),
            "partial": 0 < configured_count < len(variables),
            "configured_variables": configured_map,
        }

    missing_required = [name for name, meta in required.items() if not meta["configured"]]
    integrations_configured = sum(
        1 for meta in optional_integrations.values() if meta["configured"]
    )
    partial_integrations = sum(
        1 for meta in optional_integrations.values() if meta["partial"]
    )

    return {
        "required": required,
        "missing_required": missing_required,
        "optional_integrations": optional_integrations,
        "summary": {
            "required_configured": len(required) - len(missing_required),
            "required_total": len(required),
            "integrations_configured": integrations_configured,
            "integrations_total": len(optional_integrations),
            "partial_integrations": partial_integrations,
        },
    }


def get_startup_summary(startup_state: dict[str, Any] | None) -> dict[str, Any]:
    state = startup_state or {}
    tasks = state.get("tasks", {})
    completed_tasks = sum(1 for done in tasks.values() if done)
    return {
        "ready": bool(state.get("ready")),
        "completed_tasks": completed_tasks,
        "total_tasks": len(tasks),
        "tasks": tasks,
        "started_at": state.get("started_at"),
        "completed_at": state.get("completed_at"),
        "last_error": state.get("last_error"),
    }


def build_root_health_response(service_name: str, startup_state: dict[str, Any] | None) -> dict[str, Any]:
    startup = get_startup_summary(startup_state)
    return {
        "status": "healthy",
        "service": service_name,
        "timestamp": utcnow_iso(),
        "ready": startup["ready"],
    }


def build_api_health_response(service_name: str, startup_state: dict[str, Any] | None) -> dict[str, Any]:
    startup = get_startup_summary(startup_state)
    configuration = get_environment_configuration()
    return {
        "status": "ok",
        "service": service_name,
        "timestamp": utcnow_iso(),
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "ready": startup["ready"],
        "uptime_seconds": round(max(time.time() - SERVICE_START_TIME, 0), 2),
        "startup": startup,
        "configuration": {
            "missing_required": configuration["missing_required"],
            **configuration["summary"],
        },
    }


def build_liveness_response(service_name: str) -> dict[str, Any]:
    return {
        "alive": True,
        "service": service_name,
        "timestamp": utcnow_iso(),
        "uptime_seconds": round(max(time.time() - SERVICE_START_TIME, 0), 2),
    }


async def default_database_ping() -> None:
    from db import db

    await db.command("ping")


async def run_database_check(
    db_ping_fn: Callable[[], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    ping_fn = db_ping_fn or default_database_ping
    started = time.perf_counter()
    try:
        await ping_fn()
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "status": "pass",
            "connected": True,
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        return {
            "status": "fail",
            "connected": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


async def build_readiness_response(
    service_name: str,
    startup_state: dict[str, Any] | None,
    db_ping_fn: Callable[[], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    startup = get_startup_summary(startup_state)
    configuration = get_environment_configuration()
    database = await run_database_check(db_ping_fn=db_ping_fn)

    checks = {
        "startup": {
            "status": "pass" if startup["ready"] else "fail",
            "ready": startup["ready"],
            "completed_tasks": startup["completed_tasks"],
            "total_tasks": startup["total_tasks"],
            "last_error": startup["last_error"],
        },
        "environment": {
            "status": "pass" if not configuration["missing_required"] else "fail",
            "missing_required": configuration["missing_required"],
            **configuration["summary"],
        },
        "database": database,
    }

    ready = all(check["status"] == "pass" for check in checks.values())
    passed_checks = sum(1 for check in checks.values() if check["status"] == "pass")

    return {
        "service": service_name,
        "ready": ready,
        "timestamp": utcnow_iso(),
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "checks": checks,
        "summary": {
            "passed": passed_checks,
            "total": len(checks),
        },
    }
