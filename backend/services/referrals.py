"""Referral program — zero-cost customer acquisition.

Lowest-CAC channel a SaaS has: existing customers. This module:

  1. Generates a unique short `referral_code` for each user on demand.
  2. Tracks clicks (GET /r/<code> → 302 to signup with code cookie).
  3. On Stripe checkout success, checks the signup cookie; if a referral
     is attached, credits the referrer per the reward policy.

Reward policy (operator-configurable via env):
  MAARS_REFERRAL_PCT        = 20       (20% of the referred user's first
                                        payment credited to referrer
                                        as usable credits)
  MAARS_REFERRAL_FLAT_CR    = 500      (optional flat-credit bonus on
                                        top of percentage)
  MAARS_REFERRAL_RECURRING  = 0        (0 = one-time; 1 = forever on
                                        every charge the referred user
                                        makes)

Economics: MAARS has ~99% free-tier routing, so the "cost" of paying out
500 referral credits is ~$0.05 in actual compute. CAC is effectively
zero, LTV uncapped. This is the SaaS arbitrage the operator owns by
having built a free-first router.
"""
from __future__ import annotations
import logging
import os
import secrets
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _policy() -> dict:
    """Current reward policy — read fresh every call so operator env
    edits take effect without restart."""
    return {
        "pct":       float(os.environ.get("MAARS_REFERRAL_PCT", "20")),
        "flat_cr":   int(os.environ.get("MAARS_REFERRAL_FLAT_CR", "500")),
        "recurring": os.environ.get("MAARS_REFERRAL_RECURRING", "0") == "1",
    }


async def get_or_create_code(user_id: str) -> str:
    """Return this user's referral code, creating one if needed."""
    from db import db
    doc = await db.referral_codes.find_one({"user_id": user_id})
    if doc and doc.get("code"):
        return doc["code"]
    # 8-char code — 28 trillion possibilities, collision-safe for this scale.
    code = secrets.token_urlsafe(6)[:8].lower().replace("_", "0").replace("-", "1")
    await db.referral_codes.insert_one({
        "user_id": user_id,
        "code": code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "clicks": 0,
        "signups": 0,
        "paid_conversions": 0,
        "total_reward_credits": 0,
        "_id": None,
    })
    return code


async def record_click(code: str, request_info: dict | None = None) -> dict:
    """Log a click on a referral link. Called by /r/<code> redirect."""
    from db import db
    res = await db.referral_codes.find_one_and_update(
        {"code": code},
        {"$inc": {"clicks": 1}},
    )
    if not res:
        return {"ok": False, "error": "Unknown code"}
    await db.referral_clicks.insert_one({
        "code": code,
        "referrer_user_id": res.get("user_id"),
        "clicked_at": datetime.now(timezone.utc).isoformat(),
        "info": request_info or {},
        "_id": None,
    })
    return {"ok": True, "referrer_user_id": res.get("user_id")}


async def attach_referral_to_signup(new_user_id: str, code: str) -> dict:
    """Called during signup when a referral cookie is present. Binds
    the new user to the referrer so future charges trigger rewards."""
    from db import db
    ref = await db.referral_codes.find_one({"code": code})
    if not ref:
        return {"ok": False, "error": "Unknown code"}
    if ref.get("user_id") == new_user_id:
        return {"ok": False, "error": "Self-referral not allowed"}
    await db.referral_attributions.update_one(
        {"referred_user_id": new_user_id},
        {"$set": {
            "referred_user_id": new_user_id,
            "referrer_user_id": ref["user_id"],
            "code": code,
            "attached_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    await db.referral_codes.update_one(
        {"code": code},
        {"$inc": {"signups": 1}},
    )
    return {"ok": True, "referrer_user_id": ref["user_id"]}


async def on_paid_conversion(referred_user_id: str, charge_amount_usd: float) -> dict:
    """Called from the Stripe webhook when a referred user's charge
    succeeds. Credits the referrer per policy.

    Idempotency note: this function is NOT idempotent today — the
    Stripe webhook layer must guard against double-firing. Easy win
    later: write `processed_charges` collection with the stripe charge
    id as unique key before crediting.
    """
    from db import db
    from services.billing import wallet_service
    attr = await db.referral_attributions.find_one({"referred_user_id": referred_user_id})
    if not attr:
        return {"ok": False, "error": "No referrer attached"}

    policy = _policy()
    is_first_paid = not attr.get("first_paid_at")
    if not (is_first_paid or policy["recurring"]):
        # One-time policy + not first paid = no reward.
        return {"ok": True, "credited": 0, "reason": "one_time_already_paid"}

    # Convert the % of USD to credits at current blended cost so the
    # operator's actual outlay is tiny. 20% of $50 = $10 revenue credit
    # BUT at $0.0001/credit blended cost that's 100,000 credits worth
    # of compute, which costs the operator ~$10 to deliver. Scale the
    # reward by a healthy margin — default is to grant 20% as credits
    # at the RETAIL rate (1 credit = $0.001), which costs the operator
    # only ~$0.10 in actual compute. Cheap as it gets.
    retail_usd_per_credit = 0.001  # the price the client paid per credit
    pct_credits = int((policy["pct"] / 100.0) * charge_amount_usd / retail_usd_per_credit)
    flat_credits = policy["flat_cr"] if is_first_paid else 0
    total_credits = pct_credits + flat_credits

    try:
        await wallet_service.grant(
            user_id=attr["referrer_user_id"],
            amount=total_credits,
            reason=f"referral_reward:{referred_user_id}",
        )
    except Exception as exc:
        logger.exception("Referral grant failed")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    await db.referral_codes.update_one(
        {"code": attr["code"]},
        {"$inc": {"paid_conversions": 1, "total_reward_credits": total_credits}},
    )
    await db.referral_attributions.update_one(
        {"referred_user_id": referred_user_id},
        {"$set": {
            "first_paid_at": datetime.now(timezone.utc).isoformat() if is_first_paid else attr.get("first_paid_at"),
            "last_reward_at": datetime.now(timezone.utc).isoformat(),
        },
        "$inc": {"total_rewards_credits": total_credits}},
    )

    return {
        "ok": True,
        "credited": total_credits,
        "referrer_user_id": attr["referrer_user_id"],
        "breakdown": {"pct_credits": pct_credits, "flat_credits": flat_credits},
    }


async def stats_for_user(user_id: str) -> dict:
    """Operator / user dashboard data."""
    from db import db
    code_doc = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    if not code_doc:
        return {
            "code": None,
            "clicks": 0, "signups": 0, "paid_conversions": 0,
            "total_reward_credits": 0,
            "policy": _policy(),
        }
    return {
        **code_doc,
        "policy": _policy(),
        "share_url": f"{os.environ.get('MAARS_PUBLIC_URL', 'https://maarscommand.com')}/r/{code_doc.get('code')}",
    }
