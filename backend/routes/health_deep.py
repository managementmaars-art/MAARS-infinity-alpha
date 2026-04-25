"""Deep health check — answers 'is everything actually working' not
just 'is the process alive'.

Used by uptime monitors, status page, and load balancers. Returns 503
when any critical subsystem is down so orchestrators route traffic
away from a broken instance.
"""
from __future__ import annotations
import asyncio
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/health/deep")
async def deep_health(response: Response):
    checks = await asyncio.gather(
        _check_db(),
        _check_scheduler(),
        _check_stripe(),
        _check_email_provider(),
        _check_lead_provider(),
        return_exceptions=True,
    )
    results = {
        "db":           checks[0] if not isinstance(checks[0], Exception) else {"ok": False, "error": str(checks[0])},
        "scheduler":    checks[1] if not isinstance(checks[1], Exception) else {"ok": False, "error": str(checks[1])},
        "stripe":       checks[2] if not isinstance(checks[2], Exception) else {"ok": False, "error": str(checks[2])},
        "email":        checks[3] if not isinstance(checks[3], Exception) else {"ok": False, "error": str(checks[3])},
        "leads":        checks[4] if not isinstance(checks[4], Exception) else {"ok": False, "error": str(checks[4])},
    }
    all_critical_ok = results["db"]["ok"] and results["scheduler"]["ok"]
    if not all_critical_ok:
        response.status_code = 503
    return {
        "status": "ok" if all_critical_ok else "degraded",
        "as_of": datetime.now(timezone.utc).isoformat(),
        "checks": results,
    }


async def _check_db() -> dict:
    from db import db
    try:
        await asyncio.wait_for(db.command("ping"), timeout=3)
        return {"ok": True, "critical": True}
    except Exception as exc:
        return {"ok": False, "critical": True, "error": f"{type(exc).__name__}: {exc}"}


async def _check_scheduler() -> dict:
    try:
        from services.scheduler import scheduler_status
        s = scheduler_status()
        return {"ok": bool(s.get("running")), "critical": True, "jobs": len(s.get("jobs") or [])}
    except Exception as exc:
        return {"ok": False, "critical": True, "error": f"{type(exc).__name__}: {exc}"}


async def _check_stripe() -> dict:
    key = os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_RESTRICTED_KEY")
    if not key:
        return {"ok": False, "critical": False, "error": "not configured"}
    try:
        import stripe
        stripe.api_key = key
        # Retrieving account is a cheap read operation
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, stripe.Balance.retrieve)
        return {"ok": True, "critical": False}
    except Exception as exc:
        return {"ok": False, "critical": False, "error": f"{type(exc).__name__}"}


async def _check_email_provider() -> dict:
    try:
        from services.email_sender import _get_integration_keys
        keys = await _get_integration_keys()
        has_sg = bool((keys.get("sendgrid") or {}).get("api_key"))
        has_rs = bool((keys.get("resend") or {}).get("api_key"))
        return {
            "ok": has_sg or has_rs,
            "critical": False,
            "providers_configured": sum([has_sg, has_rs]),
        }
    except Exception as exc:
        return {"ok": False, "critical": False, "error": f"{type(exc).__name__}"}


async def _check_lead_provider() -> dict:
    try:
        from services.lead_research import apollo, hunter
        return {
            "ok": apollo.is_configured() or hunter.is_configured(),
            "critical": False,
            "apollo": apollo.is_configured(),
            "hunter": hunter.is_configured(),
        }
    except Exception as exc:
        return {"ok": False, "critical": False, "error": f"{type(exc).__name__}"}
