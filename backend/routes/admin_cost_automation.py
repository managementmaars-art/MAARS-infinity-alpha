"""Admin endpoints for cost automation.

Paired with services/billing/cost_automation.py. Frontend pulls:
  - /admin/cost-automation/pnl           — daily revenue / COGS / margin
  - /admin/cost-automation/providers     — per-provider COGS + balance
  - /admin/cost-automation/alerts        — low-balance alerts
  - /admin/cost-automation/setup-guide   — native auto-recharge per provider
  - /admin/cost-automation/run           — force a tick (trigger snapshot)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query

from auth import require_admin, User
from services.billing import cost_automation
from services import provider_balance

router = APIRouter()


@router.get("/admin/cost-automation/pnl")
async def get_pnl(days: int = Query(30, ge=1, le=365),
                  _admin: User = Depends(require_admin)):
    rows = await cost_automation.build_daily_pnl(days=days)
    snapshot = await cost_automation.latest_snapshot()
    return {
        "window_days":   days,
        "days":          rows,
        "latest":        snapshot,
    }


@router.get("/admin/cost-automation/providers")
async def get_providers(days: int = Query(30, ge=1, le=365),
                        _admin: User = Depends(require_admin)):
    # Per-provider COGS + latest balance snapshot side-by-side
    cogs = await cost_automation.cogs_by_provider(days=days)
    try:
        balances = await provider_balance.fetch_all()
    except Exception:
        balances = {}
    # Merge: each cogs row gets a balance_usd + tier if available
    for row in cogs:
        b = balances.get(row["provider"])
        if isinstance(b, dict):
            row["balance_usd"] = b.get("balance_usd")
            row["balance_source"] = b.get("source")
            row["tier"] = b.get("tier")
    return {
        "window_days":  days,
        "providers":    cogs,
        "raw_balances": balances,
    }


@router.get("/admin/cost-automation/alerts")
async def get_alerts(_admin: User = Depends(require_admin)):
    alerts = await cost_automation.provider_balance_alerts()
    return {"count": len(alerts), "alerts": alerts}


@router.get("/admin/cost-automation/setup-guide")
async def get_setup_guide(_admin: User = Depends(require_admin)):
    return {"providers": cost_automation.setup_guide()}


@router.post("/admin/cost-automation/run")
async def force_tick(_admin: User = Depends(require_admin)):
    snapshot = await cost_automation.cost_automation_tick()
    return {"ok": True, "snapshot": snapshot}


# ── Treasury endpoints ───────────────────────────────────────────────
# Revenue / COGS-reserve / Profit — the unified operator money view.
# Paired with services/billing/treasury.py which books the 3-way split
# at every Stripe webhook + debits real COGS on every API settle.

@router.get("/admin/treasury")
async def get_treasury(_admin: User = Depends(require_admin)):
    from services.billing import treasury
    snap = await treasury.get_snapshot()
    return {"object": "treasury", **snap}


@router.get("/admin/treasury/log")
async def treasury_log(limit: int = 100,
                       _admin: User = Depends(require_admin)):
    from services.billing import treasury
    entries = await treasury.recent_log(limit=max(1, min(limit, 500)))
    return {"object": "list", "data": entries}


@router.post("/admin/treasury/reconcile")
async def treasury_reconcile(_admin: User = Depends(require_admin)):
    """Close the month — move COGS surplus to profit, alert on deficit."""
    from services.billing import treasury
    return await treasury.monthly_reconcile()
