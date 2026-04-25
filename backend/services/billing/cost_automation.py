"""Cost automation — daily P&L rollup + provider-balance monitoring +
native auto-recharge setup guidance.

What this does (and does NOT do):

  DOES:
    * Roll up gateway_usage_logs into daily per-provider COGS
    * Roll up operator_revenue_entries into daily revenue
    * Join the two into a P&L row per day: revenue, cogs, margin, margin_pct
    * Pull current provider balances via provider_balance.py (Tier 1 APIs)
    * Emit alerts when any provider's balance drops below configurable threshold
    * Surface a "setup guide" — URL per provider where the operator enables
      native auto-recharge (OpenAI/Anthropic/Fal/etc. all support it)

  DOES NOT:
    * Programmatically top up provider balances (each provider requires
      the operator to enable their own native auto-recharge against the
      operator's payment method — MAARS has no credential to charge on
      their behalf). This is by design; providers reject revenue-split
      payments and only accept direct card/invoice billing.

Tick cadence: scheduled every 30 min. Writes a snapshot to
`cost_automation_snapshots` so the admin UI can graph burn rate
over time. Scheduler integration lives in services/scheduler.py.
"""
from __future__ import annotations
import asyncio
import datetime as _dt
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Tunables ─────────────────────────────────────────────────────────

# Alert if any provider's balance drops below this USD amount. Operators
# can override per-provider via platform_config.cost_automation.thresholds.
DEFAULT_LOW_BALANCE_USD = 5.0

# Margin floor — if daily margin % drops below this, emit a warning.
# Realistic target after provider mix is 75-95%; 60% is the "something
# is bleeding" threshold.
DEFAULT_MIN_MARGIN_PCT = 60.0

# How many days of history the P&L rollup covers by default.
DEFAULT_PNL_WINDOW_DAYS = 30


# ── Native auto-recharge setup guide ────────────────────────────────
# Each provider supports native auto-recharge in their own billing
# dashboard. Operator enables once; provider charges the saved payment
# method when balance runs low. No MAARS credentials needed.

AUTO_RECHARGE_PROVIDERS = [
    {
        "provider": "openai",
        "display":  "OpenAI",
        "url":      "https://platform.openai.com/settings/organization/billing/overview",
        "howto":    "Billing → Auto recharge → Set when balance falls below $X, "
                    "add $Y. Funded from your default payment method.",
        "recommended_threshold_usd": 20,
        "recommended_topup_usd":     50,
    },
    {
        "provider": "anthropic",
        "display":  "Anthropic",
        "url":      "https://console.anthropic.com/settings/billing",
        "howto":    "Billing → Auto-reload → Enable. Charges once usage hits threshold.",
        "recommended_threshold_usd": 20,
        "recommended_topup_usd":     100,
    },
    {
        "provider": "fal",
        "display":  "Fal.ai",
        "url":      "https://fal.ai/dashboard/usage-billing/billing",
        "howto":    "Billing → Auto-recharge — set low-balance trigger + refill amount.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     25,
    },
    {
        "provider": "elevenlabs",
        "display":  "ElevenLabs",
        "url":      "https://elevenlabs.io/app/subscription",
        "howto":    "Subscription → Enable auto-recharge when credits hit floor.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     25,
    },
    {
        "provider": "deepgram",
        "display":  "Deepgram",
        "url":      "https://console.deepgram.com/usage",
        "howto":    "Usage → Auto-refill — or stay on the 45k-free-min/mo tier (usually enough).",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     20,
    },
    {
        "provider": "groq",
        "display":  "Groq",
        "url":      "https://console.groq.com/settings/billing",
        "howto":    "Free tier covers most SaaS loads. Upgrade + set auto-refill only if needed.",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     20,
    },
    {
        "provider": "together",
        "display":  "Together.ai",
        "url":      "https://api.together.xyz/settings/billing",
        "howto":    "Billing → Auto top-up. Together will charge when balance hits threshold.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     25,
    },
    {
        "provider": "fireworks",
        "display":  "Fireworks",
        "url":      "https://fireworks.ai/account/billing",
        "howto":    "Account → Billing → Auto-recharge.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     25,
    },
    {
        "provider": "hyperbolic",
        "display":  "Hyperbolic",
        "url":      "https://app.hyperbolic.xyz/settings",
        "howto":    "Settings → Billing — manual top-ups; set a calendar reminder.",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     10,
    },
    {
        "provider": "novita",
        "display":  "Novita",
        "url":      "https://novita.ai/console/billing",
        "howto":    "Billing → Auto-recharge toggle.",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     10,
    },
    {
        "provider": "mistral",
        "display":  "Mistral",
        "url":      "https://console.mistral.ai/billing",
        "howto":    "Billing → Top up — manual + alerts when balance low.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     20,
    },
    {
        "provider": "cohere",
        "display":  "Cohere",
        "url":      "https://dashboard.cohere.com/billing",
        "howto":    "Billing → Auto-recharge.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     20,
    },
    {
        "provider": "perplexity",
        "display":  "Perplexity",
        "url":      "https://www.perplexity.ai/settings/api",
        "howto":    "API tab → Billing section.",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     10,
    },
    {
        "provider": "xai",
        "display":  "xAI (Grok)",
        "url":      "https://console.x.ai/team/default/billing",
        "howto":    "Billing → Auto-recharge.",
        "recommended_threshold_usd": 10,
        "recommended_topup_usd":     25,
    },
    {
        "provider": "deepseek",
        "display":  "DeepSeek",
        "url":      "https://platform.deepseek.com/usage",
        "howto":    "Usage → Top up — manual with balance API we can poll.",
        "recommended_threshold_usd": 5,
        "recommended_topup_usd":     10,
    },
]


def setup_guide() -> list[dict]:
    """Return the provider setup list for the UI. Adds `has_key` flag
    for each so the operator sees which ones are actually configured."""
    import os
    out: list[dict] = []
    for p in AUTO_RECHARGE_PROVIDERS:
        slug = p["provider"]
        env_candidates = [
            f"{slug.upper()}_API_KEY",
            f"{slug.upper()}_KEY",
            f"{slug.upper()}_TOKEN",
        ]
        has_key = any(bool(os.environ.get(e, "").strip()) for e in env_candidates)
        out.append({**p, "has_key": has_key})
    return out


# ── Daily P&L rollup ─────────────────────────────────────────────────

async def build_daily_pnl(days: int = DEFAULT_PNL_WINDOW_DAYS) -> list[dict]:
    """Aggregate revenue (operator_revenue_entries) + COGS (gateway_usage_logs +
    media costs) into a per-day table for the last N days.

    Returns a list ordered oldest→newest, one row per day:
      {date, revenue_usd, cogs_usd, margin_usd, margin_pct, call_count, providers_hit[]}
    """
    from db import db
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)

    # Revenue: operator_revenue_entries
    rev_pipe = [
        {"$match": {"created_at": {"$gte": cutoff.isoformat()}}},
        {"$project": {
            "day": {"$substr": ["$created_at", 0, 10]},
            "amount_usd": 1,
        }},
        {"$group": {"_id": "$day", "revenue_usd": {"$sum": "$amount_usd"}}},
    ]
    try:
        rev_rows = await db.operator_revenue_entries.aggregate(rev_pipe).to_list(days + 10)
    except Exception as exc:
        logger.info("revenue rollup skipped: %s", exc)
        rev_rows = []
    rev_by_day = {r["_id"]: float(r.get("revenue_usd") or 0) for r in rev_rows}

    # COGS: gateway_usage_logs
    cogs_pipe = [
        {"$match": {"created_at": {"$gte": cutoff.isoformat()}}},
        {"$project": {
            "day": {"$substr": ["$created_at", 0, 10]},
            "cost_usd": {"$ifNull": ["$cost_usd", 0]},
            "provider": 1,
        }},
        {"$group": {
            "_id": "$day",
            "cogs_usd": {"$sum": "$cost_usd"},
            "call_count": {"$sum": 1},
            "providers":  {"$addToSet": "$provider"},
        }},
    ]
    try:
        cogs_rows = await db.gateway_usage_logs.aggregate(cogs_pipe).to_list(days + 10)
    except Exception as exc:
        logger.info("cogs rollup skipped: %s", exc)
        cogs_rows = []

    cogs_by_day: dict[str, dict] = {}
    for r in cogs_rows:
        cogs_by_day[r["_id"]] = {
            "cogs_usd":  float(r.get("cogs_usd") or 0),
            "call_count": int(r.get("call_count") or 0),
            "providers": [p for p in (r.get("providers") or []) if p],
        }

    # Union of days seen in either stream
    all_days = sorted(set(list(rev_by_day.keys()) + list(cogs_by_day.keys())))
    rows: list[dict] = []
    for day in all_days:
        rev  = rev_by_day.get(day, 0.0)
        cgs  = (cogs_by_day.get(day) or {}).get("cogs_usd", 0.0)
        margin = rev - cgs
        margin_pct = (margin / rev * 100) if rev > 0 else (100.0 if cgs == 0 else 0.0)
        rows.append({
            "date":         day,
            "revenue_usd":  round(rev, 4),
            "cogs_usd":     round(cgs, 4),
            "margin_usd":   round(margin, 4),
            "margin_pct":   round(margin_pct, 2),
            "call_count":   (cogs_by_day.get(day) or {}).get("call_count", 0),
            "providers":    (cogs_by_day.get(day) or {}).get("providers", []),
        })
    return rows


async def cogs_by_provider(days: int = DEFAULT_PNL_WINDOW_DAYS) -> list[dict]:
    """Per-provider COGS + call count over the last N days."""
    from db import db
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)
    pipe = [
        {"$match": {"created_at": {"$gte": cutoff.isoformat()}}},
        {"$group": {
            "_id": {"$ifNull": ["$provider", "?"]},
            "cogs_usd":   {"$sum": {"$ifNull": ["$cost_usd", 0]}},
            "call_count": {"$sum": 1},
            "avg_usd":    {"$avg": {"$ifNull": ["$cost_usd", 0]}},
        }},
        {"$sort": {"cogs_usd": -1}},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipe).to_list(200)
    except Exception:
        rows = []
    return [{
        "provider":   r["_id"],
        "cogs_usd":   round(float(r.get("cogs_usd") or 0), 6),
        "call_count": int(r.get("call_count") or 0),
        "avg_usd":    round(float(r.get("avg_usd") or 0), 6),
    } for r in rows]


# ── Provider balance alerts ──────────────────────────────────────────

async def provider_balance_alerts(threshold_usd: float = DEFAULT_LOW_BALANCE_USD) -> list[dict]:
    """Scan every configured provider's current balance; return an alert
    for every provider whose balance is below `threshold_usd` (from DB
    override if set). Relies on `provider_balance.fetch_all()`."""
    from services import provider_balance
    alerts: list[dict] = []
    try:
        balances = await provider_balance.fetch_all()
    except Exception as exc:
        logger.warning("fetch_all balances failed: %s", exc)
        return []

    # Per-provider threshold overrides from DB
    from db import db
    cfg = await db.platform_config.find_one({"config_type": "cost_automation"}, {"_id": 0}) or {}
    overrides = (cfg.get("thresholds_usd") or {}) if isinstance(cfg, dict) else {}

    for slug, data in balances.items():
        if not isinstance(data, dict):
            continue
        # Skip tier-3 (free/unlimited) providers
        if data.get("tier") == 3 or data.get("source") == "free_tier":
            continue
        bal = data.get("balance_usd")
        if bal is None:
            continue
        thresh = float(overrides.get(slug, threshold_usd))
        if bal < thresh:
            alerts.append({
                "provider":      slug,
                "balance_usd":   round(float(bal), 4),
                "threshold_usd": thresh,
                "deficit_usd":   round(thresh - float(bal), 4),
                "source":        data.get("source", "?"),
            })
    return alerts


# ── Scheduler tick ───────────────────────────────────────────────────

async def cost_automation_tick() -> dict[str, Any]:
    """Called by the scheduler every 30 min.

    1. Snapshot today's P&L + per-provider COGS into cost_automation_snapshots
    2. Check for low-balance providers; if any, write an alert doc to
       cost_automation_alerts (idempotent per day per provider) and log.
    """
    from db import db
    now = _dt.datetime.now(_dt.timezone.utc)
    today = now.strftime("%Y-%m-%d")

    pnl_rows = await build_daily_pnl(days=1)
    today_row = next((r for r in pnl_rows if r["date"] == today),
                     {"date": today, "revenue_usd": 0, "cogs_usd": 0,
                      "margin_usd": 0, "margin_pct": 100})

    providers = await cogs_by_provider(days=1)
    alerts = await provider_balance_alerts()

    snapshot = {
        "date":        today,
        "captured_at": now.isoformat(),
        "revenue_usd": today_row.get("revenue_usd", 0),
        "cogs_usd":    today_row.get("cogs_usd", 0),
        "margin_usd":  today_row.get("margin_usd", 0),
        "margin_pct":  today_row.get("margin_pct", 0),
        "call_count":  today_row.get("call_count", 0),
        "providers":   providers,
        "low_balance_alerts": alerts,
    }
    try:
        await db.cost_automation_snapshots.update_one(
            {"date": today},
            {"$set": snapshot},
            upsert=True,
        )
    except Exception as exc:
        logger.warning("snapshot write failed: %s", exc)

    # Write alert docs once per day per provider (idempotent).
    for a in alerts:
        try:
            await db.cost_automation_alerts.update_one(
                {"date": today, "provider": a["provider"]},
                {"$set": {**a, "date": today, "captured_at": now.isoformat()}},
                upsert=True,
            )
        except Exception as exc:
            logger.info("alert write skipped for %s: %s", a.get("provider"), exc)

    if alerts:
        names = ", ".join(a["provider"] for a in alerts)
        logger.warning("cost_automation: %d provider(s) below threshold — %s",
                       len(alerts), names)

    return snapshot


async def latest_snapshot() -> dict | None:
    """Fetch the most recent daily snapshot."""
    from db import db
    return await db.cost_automation_snapshots.find_one(
        {}, {"_id": 0}, sort=[("date", -1)],
    )


async def recent_snapshots(days: int = 30) -> list[dict]:
    """Snapshot history — for the UI burn-rate chart."""
    from db import db
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)
    cur = db.cost_automation_snapshots.find(
        {"date": {"$gte": cutoff.strftime("%Y-%m-%d")}},
        {"_id": 0},
    ).sort("date", 1)
    return await cur.to_list(days + 5)
