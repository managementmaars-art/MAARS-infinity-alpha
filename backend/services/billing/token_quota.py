"""Token Quota — the UNIFIED per-client credit pool.

Replaces the 7-bucket complexity from the end-user's perspective.
Every client sees ONE number: "4,326,781 / 5,000,000 tokens this period."

The client can spend that pool however they want — all on OpenAI,
all on Anthropic, mix across 33 providers. The smart router still
picks the cheapest capable provider per call; the client sees only
their token counter decrement.

Architecture:

  1 credit = TOKENS_PER_CREDIT tokens   (default 100,000; configurable)

  Plan quota (monthly):
    Free       10   credits =   1,000,000 tokens
    Creator    50   credits =   5,000,000 tokens
    Studio     200  credits =  20,000,000 tokens
    Scale      750  credits =  75,000,000 tokens
    Infinity   5000 credits = 500,000,000 tokens

  Reserve/settle (every LLM + media call):
    1. Gateway estimates input+output tokens (for media: convert cost_usd → tokens)
    2. reserve_tokens(user_id, est_tokens, ref_id)   — atomic, fails if quota hit
    3. Provider call runs
    4. settle_tokens(user_id, reserved, actual_tokens, ref_id)
         actual_tokens < reserved → release unused
         actual_tokens > reserved → debit overage from quota (clamped to 0)

  Hard cap: reserve fails with HTTP 402 when the user has no tokens left.
  Client-isolated: each user has their own quota row; zero cross-client leakage.

The existing 7-bucket wallet stays in the DB as OPERATOR-ONLY analytics
(admin can see "of 4.3M tokens, 2M were chat, 1.5M were images"). Users
never see buckets.
"""
from __future__ import annotations
import datetime as _dt
import logging
from typing import Any, Optional
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)

# ── Tunables ─────────────────────────────────────────────────────────

# How many tokens one MAARS credit represents. This is the single lever
# the operator uses to adjust margins across all plans. Default 100k
# matches the user's stated model.
TOKENS_PER_CREDIT = 100_000

# Blended USD cost per token for converting media/audio/video $-cost
# into token-equivalent debits. Tuned to the real blended router cost
# (Gemini Flash / Groq / Cerebras dominate), roughly $0.05/M = $5/100M.
COST_USD_PER_TOKEN = 0.00000005   # $0.05 per million tokens

# Monthly period length; can be overridden per plan/user later.
DEFAULT_PERIOD_DAYS = 30

QUOTA_COLLECTION = "token_quotas"
QUOTA_LEDGER     = "token_quota_ledger"


# ── Conversions ──────────────────────────────────────────────────────

def credits_to_tokens(credits: int, tokens_per_credit: int = TOKENS_PER_CREDIT) -> int:
    """Convert a plan's headline credits into tokens for the quota."""
    return max(0, int(credits)) * max(1, int(tokens_per_credit))


def tokens_to_credits(tokens: int, tokens_per_credit: int = TOKENS_PER_CREDIT) -> float:
    """Inverse of credits_to_tokens — for admin display."""
    return float(max(0, int(tokens))) / max(1, int(tokens_per_credit))


def cost_usd_to_tokens(cost_usd: float,
                       cost_per_token: float = COST_USD_PER_TOKEN) -> int:
    """For media/audio calls the provider charges $, not tokens. Convert
    cost_usd → equivalent tokens so the single-pool accounting holds.
    Example: $0.02 Fal LTX video @ $0.00000005/token = 400,000 tokens.
    """
    if cost_usd <= 0:
        return 0
    return max(1, int(round(cost_usd / max(cost_per_token, 1e-12))))


# ── Quota state ──────────────────────────────────────────────────────

async def _ensure_quota(user_id: str, initial_tokens: int = 0) -> dict:
    """Create the user's token-quota row if absent. Returns current doc.

    Period start/end default to now → +30 days. Refresh on monthly
    renewal via `grant_tokens(..., reset_period=True)`.
    """
    from db import db
    existing = await db[QUOTA_COLLECTION].find_one({"user_id": user_id}, {"_id": 0})
    if existing:
        return existing
    now = _dt.datetime.now(_dt.timezone.utc)
    doc = {
        "user_id":            user_id,
        "tokens_quota":       int(initial_tokens),
        "tokens_used":        0,
        "tokens_reserved":    0,
        "period_start":       now.isoformat(),
        "period_end":         (now + _dt.timedelta(days=DEFAULT_PERIOD_DAYS)).isoformat(),
        "tokens_per_credit":  TOKENS_PER_CREDIT,
        "total_calls":        0,
        "created_at":         now.isoformat(),
        "updated_at":         now.isoformat(),
    }
    try:
        await db[QUOTA_COLLECTION].insert_one(doc)
    except Exception:
        doc = await db[QUOTA_COLLECTION].find_one({"user_id": user_id}, {"_id": 0}) or doc
    return doc


async def get_quota(user_id: str) -> dict[str, Any]:
    """User-visible single-number view. Everything the wallet UI needs."""
    q = await _ensure_quota(user_id, initial_tokens=0)
    quota = int(q.get("tokens_quota") or 0)
    used  = int(q.get("tokens_used") or 0)
    reserved = int(q.get("tokens_reserved") or 0)
    remaining = max(0, quota - used - reserved)
    pct_used = (100.0 * used / quota) if quota > 0 else 0.0
    return {
        "user_id":           user_id,
        "tokens_quota":      quota,
        "tokens_used":       used,
        "tokens_reserved":   reserved,
        "tokens_remaining":  remaining,
        "pct_used":          round(pct_used, 2),
        "period_start":      q.get("period_start"),
        "period_end":        q.get("period_end"),
        "tokens_per_credit": int(q.get("tokens_per_credit") or TOKENS_PER_CREDIT),
        "credits_remaining": round(tokens_to_credits(remaining, q.get("tokens_per_credit") or TOKENS_PER_CREDIT), 2),
        "credits_quota":     round(tokens_to_credits(quota, q.get("tokens_per_credit") or TOKENS_PER_CREDIT), 2),
        "total_calls":       int(q.get("total_calls") or 0),
    }


# ── Grant (plan renewal / top-up) ────────────────────────────────────

async def grant_tokens(
    user_id: str,
    tokens: int,
    *,
    reference_id: str,
    description: str = "",
    plan_id: Optional[str] = None,
    reset_period: bool = False,
) -> dict:
    """Add tokens to the user's quota. Use reset_period=True on monthly
    renewal to zero out tokens_used and restart the period clock.
    Idempotent on reference_id via the ledger unique key.
    """
    from db import db
    if tokens <= 0 and not reset_period:
        return await get_quota(user_id)

    await _ensure_quota(user_id, initial_tokens=0)
    now = _dt.datetime.now(_dt.timezone.utc)

    # Idempotency: check ledger first
    existing = await db[QUOTA_LEDGER].find_one(
        {"user_id": user_id, "reference_id": reference_id, "kind": "grant"},
        {"_id": 1},
    )
    if existing:
        return await get_quota(user_id)

    set_payload: dict[str, Any] = {"updated_at": now.isoformat()}
    inc_payload: dict[str, int] = {}
    if reset_period:
        set_payload["tokens_used"]     = 0
        set_payload["tokens_reserved"] = 0
        set_payload["tokens_quota"]    = int(tokens)
        set_payload["period_start"]    = now.isoformat()
        set_payload["period_end"]      = (now + _dt.timedelta(days=DEFAULT_PERIOD_DAYS)).isoformat()
    else:
        inc_payload["tokens_quota"] = int(tokens)
    if plan_id:
        set_payload["plan_id"] = plan_id

    op: dict[str, Any] = {"$set": set_payload}
    if inc_payload:
        op["$inc"] = inc_payload
    await db[QUOTA_COLLECTION].update_one({"user_id": user_id}, op)

    await db[QUOTA_LEDGER].insert_one({
        "user_id":      user_id,
        "kind":         "grant",
        "tokens":       int(tokens),
        "reference_id": reference_id,
        "description":  description,
        "plan_id":      plan_id,
        "reset_period": bool(reset_period),
        "ts":           now.isoformat(),
    })
    return await get_quota(user_id)


# ── Reserve / settle / refund ────────────────────────────────────────

async def reserve_tokens(
    user_id: str,
    tokens: int,
    *,
    reference_id: str,
    source: Optional[str] = None,
) -> Optional[dict]:
    """Atomic hold on `tokens` from the quota. Returns the updated quota
    row, or None if the user would go over cap.

    Hard cap enforcement: the CAS filter requires
        tokens_quota - tokens_used - tokens_reserved >= tokens
    """
    from db import db
    if tokens <= 0:
        return await get_quota(user_id)

    await _ensure_quota(user_id, initial_tokens=0)
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()

    updated = await db[QUOTA_COLLECTION].find_one_and_update(
        {
            "user_id": user_id,
            "$expr": {
                "$gte": [
                    {"$subtract": [
                        {"$ifNull": ["$tokens_quota", 0]},
                        {"$add": [
                            {"$ifNull": ["$tokens_used", 0]},
                            {"$ifNull": ["$tokens_reserved", 0]},
                        ]},
                    ]},
                    int(tokens),
                ]
            }
        },
        {
            "$inc": {"tokens_reserved": int(tokens)},
            "$set": {"updated_at": now},
        },
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )
    if updated is None:
        return None

    try:
        await db[QUOTA_LEDGER].insert_one({
            "user_id":      user_id,
            "kind":         "reserve",
            "tokens":       int(tokens),
            "reference_id": reference_id,
            "source":       source,
            "ts":           now,
        })
    except Exception as exc:
        logger.info("ledger reserve insert skipped: %s", exc)

    return await get_quota(user_id)


async def settle_tokens(
    user_id: str,
    *,
    reserved_tokens: int,
    actual_tokens: int,
    reference_id: str,
    source: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    cost_usd: Optional[float] = None,
) -> dict:
    """Close out a reserve.
      actual < reserved → excess returns to the pool
      actual > reserved → overage is debited (clamped to not go negative)
    Always increments `total_calls`.
    """
    from db import db
    if reserved_tokens < 0 or actual_tokens < 0:
        raise ValueError("amounts must be non-negative")

    await _ensure_quota(user_id, initial_tokens=0)
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    actual = int(actual_tokens)
    reserved = int(reserved_tokens)

    # Clamp actual to quota-available so we never drive used beyond quota.
    # (Over-budget overflow is logged but clamped for accounting integrity.)
    if actual > reserved:
        overage = actual - reserved
        q = await _ensure_quota(user_id)
        headroom = max(0, int(q.get("tokens_quota", 0)) - int(q.get("tokens_used", 0)) - reserved)
        debit_overage = min(overage, headroom)
        if debit_overage < overage:
            logger.warning("token overage clamped for %s: wanted +%d, allowed +%d",
                           user_id, overage, debit_overage)
        effective_debit = reserved + debit_overage
    else:
        effective_debit = actual

    release = reserved - min(reserved, actual)  # never negative

    await db[QUOTA_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "tokens_used":     int(effective_debit),
                "tokens_reserved": -int(reserved),
                "total_calls":     1,
            },
            "$set": {"updated_at": now},
        },
    )

    try:
        await db[QUOTA_LEDGER].insert_one({
            "user_id":      user_id,
            "kind":         "settle",
            "tokens":       int(effective_debit),
            "reserved":     int(reserved),
            "actual":       int(actual),
            "released":     int(release),
            "reference_id": reference_id,
            "source":       source,
            "provider":     provider,
            "model":        model,
            "cost_usd":     cost_usd,
            "ts":           now,
        })
    except Exception as exc:
        logger.info("ledger settle insert skipped: %s", exc)

    return await get_quota(user_id)


async def refund_tokens(
    user_id: str,
    *,
    reserved_tokens: int,
    reference_id: str,
    source: Optional[str] = None,
) -> dict:
    """Full release — used when the provider call failed and no tokens
    were actually consumed."""
    from db import db
    if reserved_tokens <= 0:
        return await get_quota(user_id)
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    await db[QUOTA_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$inc": {"tokens_reserved": -int(reserved_tokens)},
            "$set": {"updated_at": now},
        },
    )
    try:
        await db[QUOTA_LEDGER].insert_one({
            "user_id":      user_id,
            "kind":         "refund",
            "tokens":       int(reserved_tokens),
            "reference_id": reference_id,
            "source":       source,
            "ts":           now,
        })
    except Exception:
        pass
    return await get_quota(user_id)


# ── Monthly renewal (scheduler hook) ─────────────────────────────────

async def renew_expired_periods() -> dict[str, int]:
    """Scheduler tick: for every user whose period_end has passed, reset
    their period. Grants a fresh quota based on their current plan.
    Safe to run every hour — only users with expired periods get touched.
    """
    from db import db
    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    cursor = db[QUOTA_COLLECTION].find(
        {"period_end": {"$lt": now}},
        {"user_id": 1, "plan_id": 1, "_id": 0},
    )
    renewed = 0
    async for row in cursor:
        uid = row.get("user_id")
        pid = row.get("plan_id") or "free"
        # Resolve plan → credits → tokens
        try:
            from services.billing.plan_deliverables import total_credits_for
            credits = total_credits_for(pid)
        except Exception:
            credits = 0
        tokens = credits_to_tokens(credits)
        if tokens <= 0:
            continue
        ref = f"renewal_{uid}_{now[:10]}"
        try:
            await grant_tokens(
                uid, tokens,
                reference_id=ref,
                description=f"Period renewal: {pid}",
                plan_id=pid, reset_period=True,
            )
            renewed += 1
        except Exception as exc:
            logger.warning("renewal failed for %s: %s", uid, exc)
    return {"renewed": renewed}


async def recent_ledger(user_id: Optional[str] = None, limit: int = 100) -> list[dict]:
    """Audit trail — used by admin + optionally user usage-history view."""
    from db import db
    q: dict[str, Any] = {}
    if user_id:
        q["user_id"] = user_id
    cur = db[QUOTA_LEDGER].find(q, {"_id": 0}).sort("ts", -1).limit(max(1, min(limit, 1000)))
    return await cur.to_list(limit)
