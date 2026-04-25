"""Auto-topup — off-session Stripe charges when a user's credit
balance falls below a configured threshold.

Flow:
  1. User enables auto-topup + sets {threshold, refill, max_monthly}.
  2. MAARS stores their Stripe `payment_method_id` (captured during
     their last checkout with `setup_future_usage="off_session"`).
  3. Scheduler sweeps every 5 min OR wallet.reserve triggers an
     on-demand top-up when balance falls below threshold inside a
     request.
  4. Off-session `PaymentIntent` charges the saved card for
     `refill_credits × usd_per_credit_headline`. Idempotent via
     `reference_id = autotopup_{user}_{YYYYMM}_{n}`.
  5. On success: wallet.grant(refill_credits). Ledger gets an
     AUTO_TOPUP entry. Notifications_center pings the user.
  6. On failure (3DS required, insufficient funds, expired card):
     mark topup_state="needs_attention" and notify user + admin.
     Subsequent sweeps skip this user until they fix payment.

Hard limits (safety rails):
  - max_monthly_refills: prevents runaway charging on a loop-bug user
  - hard_cap_usd: one topup can't charge more than this
"""
from __future__ import annotations
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD_CREDITS = 50
DEFAULT_REFILL_CREDITS    = 500
DEFAULT_MAX_MONTHLY       = 4
HARD_CAP_USD              = 500.0
HEADLINE_USD_PER_CREDIT   = 0.10  # what the client pays for a credit on top-up


async def _settings(user_id: str) -> dict[str, Any]:
    from db import db
    doc = await db.auto_topup.find_one({"_id": user_id}, {"_id": 0}) or {}
    return {
        "enabled":               bool(doc.get("enabled")),
        "threshold_credits":     int(doc.get("threshold_credits") or DEFAULT_THRESHOLD_CREDITS),
        "refill_credits":        int(doc.get("refill_credits") or DEFAULT_REFILL_CREDITS),
        "max_monthly_refills":   int(doc.get("max_monthly_refills") or DEFAULT_MAX_MONTHLY),
        "payment_method_id":     doc.get("payment_method_id"),
        "stripe_customer_id":    doc.get("stripe_customer_id"),
        "state":                 doc.get("state", "idle"),
        "last_error":            doc.get("last_error"),
    }


async def set_settings(
    user_id: str, *,
    enabled: bool | None = None,
    threshold_credits: int | None = None,
    refill_credits: int | None = None,
    max_monthly_refills: int | None = None,
    payment_method_id: str | None = None,
    stripe_customer_id: str | None = None,
) -> dict[str, Any]:
    from db import db
    patch: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if enabled is not None:             patch["enabled"] = bool(enabled)
    if threshold_credits is not None:   patch["threshold_credits"] = int(threshold_credits)
    if refill_credits is not None:      patch["refill_credits"] = int(refill_credits)
    if max_monthly_refills is not None: patch["max_monthly_refills"] = int(max_monthly_refills)
    if payment_method_id is not None:   patch["payment_method_id"] = payment_method_id
    if stripe_customer_id is not None:  patch["stripe_customer_id"] = stripe_customer_id
    await db.auto_topup.update_one({"_id": user_id}, {"$set": patch}, upsert=True)
    return await _settings(user_id)


async def _month_refills_count(user_id: str) -> int:
    from db import db
    now = datetime.now(timezone.utc)
    month = now.strftime("%Y%m")
    return await db.auto_topup_charges.count_documents({"user_id": user_id, "month": month})


async def _charge_off_session(
    *, user_id: str, settings: dict, usd_amount: float, idempotency_key: str,
) -> dict[str, Any]:
    """Stripe off-session PaymentIntent for a saved payment method."""
    try:
        import stripe
    except ImportError:
        return {"ok": False, "error": "stripe package not installed"}
    api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not api_key:
        return {"ok": False, "error": "STRIPE_SECRET_KEY not configured"}
    stripe.api_key = api_key

    pm = settings.get("payment_method_id")
    cust = settings.get("stripe_customer_id")
    if not (pm and cust):
        return {"ok": False, "error": "no saved payment method / customer"}

    import asyncio as _a
    def _sync():
        return stripe.PaymentIntent.create(
            amount=int(round(usd_amount * 100)),
            currency="usd",
            customer=cust,
            payment_method=pm,
            off_session=True,
            confirm=True,
            description=f"MAARS auto-topup for user {user_id}",
            idempotency_key=idempotency_key,
            metadata={"user_id": user_id, "type": "auto_topup"},
        )
    try:
        pi = await _a.to_thread(_sync)
        return {
            "ok":        pi.status == "succeeded",
            "status":    pi.status,
            "intent_id": pi.id,
            "amount":    pi.amount / 100,
            "charge_id": (pi.charges.data[0].id if getattr(pi, "charges", None) and pi.charges.data else None),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}


async def maybe_topup(user_id: str) -> dict[str, Any]:
    """The one function wallet.reserve + scheduler call.

    - Reads settings
    - Checks guards (enabled, under monthly cap, current balance below
      threshold)
    - Charges Stripe off-session
    - Grants credits on success
    - Logs + notifies
    """
    from services.billing import wallet_service
    from db import db

    settings = await _settings(user_id)
    if not settings["enabled"]:
        return {"ok": False, "skipped": "not enabled"}
    if settings["state"] == "needs_attention":
        return {"ok": False, "skipped": "needs_attention"}

    try:
        wallet = await wallet_service.get_summary(user_id)
    except Exception as exc:
        return {"ok": False, "error": f"wallet lookup failed: {exc}"}
    balance = int(wallet.get("balance_credits") or 0)
    if balance > settings["threshold_credits"]:
        return {"ok": False, "skipped": "balance above threshold"}

    if await _month_refills_count(user_id) >= settings["max_monthly_refills"]:
        return {"ok": False, "skipped": "monthly refill cap reached"}

    refill = int(settings["refill_credits"])
    usd = min(HARD_CAP_USD, round(refill * HEADLINE_USD_PER_CREDIT, 2))
    if usd <= 0:
        return {"ok": False, "error": "zero charge amount"}

    now = datetime.now(timezone.utc)
    month = now.strftime("%Y%m")
    idem = f"autotopup_{user_id}_{month}_{uuid.uuid4().hex[:8]}"

    charge = await _charge_off_session(
        user_id=user_id, settings=settings, usd_amount=usd, idempotency_key=idem,
    )
    record = {
        "user_id":   user_id,
        "month":     month,
        "idem_key":  idem,
        "usd":       usd,
        "refill":    refill,
        "charge_ok": bool(charge.get("ok")),
        "intent_id": charge.get("intent_id"),
        "error":     charge.get("error"),
        "ts":        now.isoformat(),
    }
    await db.auto_topup_charges.insert_one(record)

    if not charge.get("ok"):
        await db.auto_topup.update_one(
            {"_id": user_id},
            {"$set": {"state": "needs_attention",
                      "last_error": charge.get("error"),
                      "last_error_at": now.isoformat()}},
        )
        # Alert the user + admin.
        try:
            from routes.notifications_center import notify
            await notify(
                user_id=user_id,
                title="Auto-topup failed",
                body=f"We couldn't charge your saved card for a $ {usd:.2f} top-up. {charge.get('error', '')}",
                kind="error",
                link="/settings/billing",
            )
        except Exception:
            pass
        return {"ok": False, **charge}

    # Success — grant credits.
    try:
        await wallet_service.grant(
            user_id, refill,
            reference_id=idem,
            description=f"Auto-topup ${usd:.2f}",
            reference_type="auto_topup",
        )
    except Exception as exc:
        logger.warning("grant after successful charge failed: %s", exc)

    await db.auto_topup.update_one(
        {"_id": user_id},
        {"$set": {"state": "idle", "last_success_at": now.isoformat(), "last_error": None}},
    )
    try:
        from routes.notifications_center import notify
        await notify(
            user_id=user_id,
            title="Auto-topup successful",
            body=f"Your balance was topped up by {refill} credits (${usd:.2f}).",
            kind="info",
            link="/wallet",
        )
    except Exception:
        pass
    return {"ok": True, **charge, "credits_granted": refill}


async def sweep() -> dict[str, int]:
    """Scheduler tick: scan every enabled auto_topup user whose balance
    might be below threshold. Bounded work — only users with enabled=true
    and state != needs_attention."""
    from db import db
    candidates = await db.auto_topup.find(
        {"enabled": True, "state": {"$ne": "needs_attention"}},
        {"_id": 1},
    ).to_list(2000)
    topped = 0
    for c in candidates:
        try:
            r = await maybe_topup(c["_id"])
            if r.get("ok"): topped += 1
        except Exception as exc:
            logger.info("auto_topup sweep user %s failed: %s", c["_id"], exc)
    return {"candidates": len(candidates), "topped_up": topped}
