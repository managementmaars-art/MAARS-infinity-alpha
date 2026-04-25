"""Public status + changelog endpoints.

Both are unauthenticated by design — they're trust signals, not
secrets. Status feeds a /status page (green/yellow/red); changelog
feeds /changelog for product-update SEO + retention.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def public_status():
    """Live system status — green if every subsystem is healthy.

    Checks:
      - DB reachable
      - Scheduler running
      - At least 1 LLM provider reachable (smoke-test cached)
      - No email-provider outage in last hour
    """
    from db import db
    components = []
    overall = "operational"

    # DB
    try:
        await db.command("ping")
        components.append({"name": "Database", "status": "operational"})
    except Exception:
        components.append({"name": "Database", "status": "major_outage"})
        overall = "major_outage"

    # Scheduler
    try:
        from services.scheduler import scheduler_status
        sch = scheduler_status()
        components.append({
            "name": "Automation Engine",
            "status": "operational" if sch.get("running") else "degraded",
        })
        if not sch.get("running") and overall == "operational":
            overall = "degraded"
    except Exception:
        components.append({"name": "Automation Engine", "status": "unknown"})

    # AI providers (cached from smoke-test runs)
    try:
        smoke = await db.provider_smoke_results.find(
            {},
            {"_id": 0, "slug": 1, "ok": 1, "last_run": 1},
        ).to_list(50)
        if smoke:
            ok_count = sum(1 for s in smoke if s.get("ok"))
            total = len(smoke)
            if ok_count >= max(1, total // 2):
                components.append({
                    "name": "AI Inference",
                    "status": "operational" if ok_count == total else "degraded",
                    "detail": f"{ok_count}/{total} providers healthy",
                })
                if ok_count < total and overall == "operational":
                    overall = "degraded"
            else:
                components.append({
                    "name": "AI Inference",
                    "status": "major_outage",
                    "detail": f"Only {ok_count}/{total} providers reachable",
                })
                overall = "major_outage"
        else:
            components.append({"name": "AI Inference", "status": "unknown"})
    except Exception:
        components.append({"name": "AI Inference", "status": "unknown"})

    # Email transport
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        recent_failures = await db.cold_emails.count_documents({
            "status": "failed", "executed_at": {"$gte": cutoff},
        })
        recent_sent = await db.cold_emails.count_documents({
            "status": "sent", "executed_at": {"$gte": cutoff},
        })
        if recent_failures > 0 and recent_failures > recent_sent * 0.3:
            components.append({
                "name": "Email Delivery",
                "status": "degraded",
                "detail": f"{recent_failures} failures in last hour",
            })
            if overall == "operational":
                overall = "degraded"
        else:
            components.append({"name": "Email Delivery", "status": "operational"})
    except Exception:
        components.append({"name": "Email Delivery", "status": "unknown"})

    return {
        "status": overall,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "components": components,
    }


# ── Changelog — curated release notes fed from the changelog collection.
# Populate via seed script or admin endpoint. Client-readable only.
@router.get("/changelog")
async def public_changelog(limit: int = 20):
    from db import db
    entries = await db.changelog_entries.find(
        {"published": True},
        {"_id": 0},
    ).sort("published_at", -1).to_list(max(1, min(limit, 50)))
    return {"object": "list", "data": entries}
