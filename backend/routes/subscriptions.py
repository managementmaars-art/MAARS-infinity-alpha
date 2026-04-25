"""Subscription, payment, and credit management endpoints."""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from db import db
from auth import get_current_user, require_admin, User, ADMIN_EMAIL
from models.schemas import CheckoutRequest
from shared.constants import SUBSCRIPTION_PLANS, STRIPE_API_KEY
from shared.utils import get_custom_package_config, get_live_bdt_rate as get_usd_bdt_rate, get_credit_packages

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/plans")
async def get_plans():
    """Get all subscription plans + credit packages + custom-package config.

    Response shape:
      plans            — legacy dict keyed by plan_id (what PricingPage reads)
      plans_v2         — list with monthly + annual per plan (what LandingPricingSection reads)
      credit_packages  — credit top-up packages
      custom_package   — agent-by-agent custom bundle config
      bdt_rate, annual_discount_pct — top-level helpers

    Single source: services.pricing_service. Change pricing math there
    once, every surface updates."""
    from services.pricing_service import load_plans_payload
    return await load_plans_payload()

@router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription"""
    is_admin = current_user.email == ADMIN_EMAIL

    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        sub = {
            "user_id": current_user.user_id,
            "plan_id": "free",
            "credits": 50,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "renewed_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(sub)

    # Admin/Owner gets unlimited everything
    if is_admin:
        owner_plan = {
            "plan_id": "owner",
            "name": "Owner",
            "price_usd": 0,
            "credits": 999999,
            "max_agents": -1,
            "max_custom_agents": -1,
            "includes_commander": True,
            "max_team_members": -1,
            "features": ["Unlimited credits", "All agents", "All features", "No restrictions"],
        }
        return {
            **sub,
            "plan_id": "owner",
            "credits": 999999,
            "credits_used": sub.get("credits_used", 0),
            "status": "active",
            "is_owner": True,
            "plan_info": owner_plan,
        }

    plan_info = SUBSCRIPTION_PLANS.get(sub.get("plan_id", "free"), SUBSCRIPTION_PLANS["free"])
    return {**sub, "plan_info": plan_info}

@router.post("/checkout")
async def create_checkout(checkout_data: CheckoutRequest, request: Request, current_user: User = Depends(get_current_user)):
    """Create a Stripe checkout session for subscription or credits"""
    import stripe as _stripe
    import asyncio as _asyncio
    _stripe.api_key = STRIPE_API_KEY

    host_url = checkout_data.origin_url
    currency = checkout_data.currency.lower()
    
    # Currency resolution — USD + BDT use plan-stored prices; EUR/GBP
    # go through the FX service for on-the-fly conversion (ECB rates
    # cached 1h). Keeps a single pricing table (USD) as the source of
    # truth, other currencies derive.
    from services.pricing_currencies import convert_from_usd, stripe_tax_enabled
    from services.billing.annual_billing import resolve_plan_pricing

    billing = (checkout_data.billing or "monthly").lower()
    if billing not in ("monthly", "annual"):
        billing = "monthly"

    if checkout_data.type == "subscription":
        if checkout_data.plan_id not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan")

        plan = SUBSCRIPTION_PLANS[checkout_data.plan_id]
        # Single source: pricing_service's resolve_plan_pricing owns
        # annual discount + credits-per-year + stripe interval math.
        pricing = resolve_plan_pricing(plan, billing, bdt_rate=107.0)
        if (pricing.get("price_usd") or 0) == 0:
            raise HTTPException(status_code=400, detail="Free plan doesn't require payment")

        # Resolve per-currency amount. BDT goes through the plan's
        # annual/monthly BDT; EUR/GBP convert from USD via FX.
        if currency == "bdt":
            amount = pricing.get("price_bdt", 0)
        elif currency in ("eur", "gbp"):
            amount = await convert_from_usd(pricing["price_usd"], currency)
        else:  # usd or unsupported → default USD
            currency = "usd"
            amount = pricing["price_usd"]

        metadata = {
            "type": "subscription",
            "plan_id": checkout_data.plan_id,
            "user_id": current_user.user_id,
            "email": current_user.email,
            "currency": currency,
            "billing": billing,
            "credits_granted": str(pricing.get("credits", 0)),
            "referral_code": checkout_data.referral_code or "",
        }
    elif checkout_data.type == "credits":
        credit_pkgs = await get_credit_packages()
        
        # Support custom credit amounts (custom_<credits>)
        if checkout_data.package_id and checkout_data.package_id.startswith("custom_"):
            try:
                custom_credits = int(checkout_data.package_id.split("_")[1])
                if custom_credits < 5:
                    raise HTTPException(status_code=400, detail="Minimum 5 credits")
                custom_price_usd = custom_credits / 5.0
                rate = await get_usd_bdt_rate()
                custom_price_bdt = round(custom_price_usd * rate, 2)
                price = custom_price_bdt if currency == "bdt" else custom_price_usd
                metadata = {
                    "type": "credits",
                    "package_id": checkout_data.package_id,
                    "credits": str(custom_credits),
                    "user_id": current_user.user_id,
                    "email": current_user.email,
                    "currency": currency
                }
                amount = price
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid custom credit amount")
        elif checkout_data.package_id not in credit_pkgs:
            raise HTTPException(status_code=400, detail="Invalid credit package")
        else:
            package = credit_pkgs[checkout_data.package_id]
            price_key = "price_bdt" if currency == "bdt" else "price_usd"
            amount = package[price_key]
            metadata = {
                "type": "credits",
                "package_id": checkout_data.package_id,
                "credits": str(package["credits"]),
                "user_id": current_user.user_id,
                "email": current_user.email,
                "currency": currency,
                # Per-category tagged top-up — the package's `category` field
                # (chat/code/image_hd/video/voiceover/...) flows through
                # Stripe metadata and tags the wallet transaction. "general"
                # means credits spend on any track. Enables per-category
                # revenue + margin tracking in treasury.
                "category": package.get("category") or "general",
            }
    else:
        raise HTTPException(status_code=400, detail="Invalid checkout type")
    
    success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/settings"

    product_name = f"MAARS {checkout_data.type} — {checkout_data.plan_id or checkout_data.package_id or ''}"
    amount_minor = int(round(float(amount) * 100))

    # Stripe recurring interval — "year" when user picked annual.
    stripe_interval = "year" if (checkout_data.type == "subscription" and billing == "annual") else "month"
    session_kwargs: dict = {
        "mode": "payment" if checkout_data.type == "credits" else "subscription",
        "line_items": [{
            "price_data": {
                "currency": currency,
                "product_data": {"name": product_name},
                "unit_amount": amount_minor,
                **({"recurring": {"interval": stripe_interval}} if checkout_data.type == "subscription" else {}),
            },
            "quantity": 1,
        }],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": metadata,
        "customer_email": current_user.email,
    }
    # Stripe Tax — enable automatic VAT collection for EU/UK currencies
    # when the operator has toggled Stripe Tax on (MAARS_STRIPE_TAX_ENABLED=1).
    if stripe_tax_enabled(currency):
        session_kwargs["automatic_tax"] = {"enabled": True}

    def _create():
        return _stripe.checkout.Session.create(**session_kwargs)
    session = await _asyncio.to_thread(_create)

    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "type": checkout_data.type,
        "amount": amount,
        "currency": currency,
        "metadata": metadata,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)

    return {"checkout_url": session.url, "session_id": session.id}

@router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, current_user: User = Depends(get_current_user)):
    """Check payment status and update subscription/credits"""
    import stripe as _stripe
    import asyncio as _asyncio
    _stripe.api_key = STRIPE_API_KEY

    try:
        session_obj = await _asyncio.to_thread(_stripe.checkout.Session.retrieve, session_id)
        # Shim to the same attribute surface the old wrapper exposed.
        class _StatusShim:
            def __init__(self, s):
                self.status = s.status or "open"
                self.payment_status = s.payment_status or "unpaid"
        status = _StatusShim(session_obj)
    except Exception as e:
        logger.error(f"Error checking checkout status: {e}")
        raise HTTPException(status_code=400, detail="Failed to check payment status")
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if already processed
    if transaction.get("payment_status") == "paid":
        return {"status": "success", "message": "Payment already processed", "payment_status": "paid"}
    
    # Update transaction
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": status.status,
            "payment_status": status.payment_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # If payment successful, update subscription or add credits
    if status.payment_status == "paid":
        metadata = transaction.get("metadata", {})
        
        if metadata.get("type") == "subscription":
            plan_id = metadata.get("plan_id")
            plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$set": {
                    "plan_id": plan_id,
                    "credits": plan["credits"],
                    "credits_used": 0,
                    "status": "active",
                    "renewed_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            # Update gateway key budget to match new plan's AI cost allocation
            await db.client_gateway_keys.update_one(
                {"user_id": current_user.user_id},
                {"$set": {
                    "plan_id":            plan_id,
                    "monthly_budget_usd": plan.get("monthly_cap_usd", 0.0),
                    "used_usd":           0.0,
                    "cycle_start":        datetime.now(timezone.utc).isoformat(),
                    "status":             "active",
                }},
                upsert=True
            )
            return {"status": "success", "message": f"Subscribed to {plan['name']} plan", "payment_status": "paid"}
        
        elif metadata.get("type") == "credits":
            credits_to_add = int(metadata.get("credits", 0))
            category = metadata.get("category") or "general"

            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$inc": {"credits": credits_to_add}},
                upsert=True
            )

            # Map the UI category (8 tracks + general) to the backend
            # BUCKETS (7 + general). image_std/image_hd both go to the
            # `image` bucket; tts joins `voice`; code → vibe. This lets
            # the operator sell 8-track top-ups while the wallet runs on
            # 7 consolidated pools (std + tts are free anyway — sharing
            # their paid counterpart's bucket costs nothing).
            UI_TO_BUCKET = {
                "chat":      "chat",
                "code":      "vibe",
                "image_std": "image", "image_hd": "image",
                "video":     "video",
                "voiceover": "voice", "tts":      "voice",
                "stt":       "stt",
                "general":   "general",
            }
            target_bucket = UI_TO_BUCKET.get(category, "general")

            # Grant credits into the matched bucket so the wallet reflects
            # the category-specific allowance. grant() handles the atomic
            # $inc on the nested bucket path + ledger entry.
            try:
                from services.billing import wallet_service
                await wallet_service.grant(
                    user_id=current_user.user_id,
                    credits=credits_to_add,
                    reference_type="stripe_topup",
                    reference_id=session_id or f"topup_{int(datetime.now(timezone.utc).timestamp())}",
                    bucket=target_bucket,
                    description=f"Top-up: {category} ({credits_to_add} credits)",
                )
            except Exception as _gex:
                # Fallback to legacy subscriptions.credits increment above
                # if the bucketed grant fails — user still gets credits.
                pass

            # Record the per-category top-up for treasury revenue rollup.
            try:
                from datetime import datetime, timezone
                await db.category_topups.insert_one({
                    "user_id":     current_user.user_id,
                    "category":    category,       # UI-level 8-track label
                    "bucket":      target_bucket,  # wallet-level consolidation
                    "credits":     credits_to_add,
                    "package_id":  metadata.get("package_id"),
                    "amount_usd":  float(metadata.get("amount_usd") or 0),
                    "currency":    metadata.get("currency"),
                    "session_id":  session_id,
                    "created_at":  datetime.now(timezone.utc).isoformat(),
                })
            except Exception as _tex:
                pass  # non-fatal
            return {"status": "success",
                    "message": f"Added {credits_to_add} credits to {target_bucket} bucket ({category})",
                    "payment_status": "paid"}
        
        elif metadata.get("type") == "custom_package":
            credits_to_add = int(metadata.get("credits", 0))
            selected_agents = [a for a in metadata.get("selected_agents", "").split(",") if a]
            include_commander = metadata.get("include_commander", "False") == "True"
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$set": {
                    "plan_id": "custom",
                    "credits": credits_to_add,
                    "credits_used": 0,
                    "selected_agents": selected_agents,
                    "has_commander": include_commander,
                    "status": "active",
                    "renewed_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            return {"status": "success", "message": f"Custom package activated with {len(selected_agents)} agents and {credits_to_add} credits", "payment_status": "paid"}
    
    return {"status": status.status, "payment_status": status.payment_status}

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks via native stripe SDK (signature-verified)."""
    import stripe as _stripe
    import os as _os
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")

    try:
        webhook_secret = _os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        if webhook_secret and signature:
            event = _stripe.Webhook.construct_event(body, signature, webhook_secret)
        else:
            # Dev mode: parse without signature verification.
            import json as _json
            event = _json.loads(body.decode("utf-8"))

        event_type = event.get("type", "") if isinstance(event, dict) else event["type"]
        session_obj = (event.get("data", {}) if isinstance(event, dict) else event["data"])
        session_obj = session_obj.get("object", {}) if isinstance(session_obj, dict) else session_obj["object"]

        # Shim to match the old attribute surface.
        class _WR:
            session_id = session_obj.get("id", "")
            event_type = event_type
            payment_status = session_obj.get("payment_status", "")
        webhook_response = _WR()

        if webhook_response.session_id:
            # Idempotency guard — a retried Stripe delivery of the same event
            # must not double-credit. We key on session_id+event_type, which is
            # what Stripe guarantees unique per delivery attempt succeeding.
            idempotency_key = f"{webhook_response.session_id}:{webhook_response.event_type}"
            already = await db.payment_transactions.find_one(
                {"session_id": webhook_response.session_id, "processed_events": idempotency_key},
                {"_id": 0, "session_id": 1},
            )
            if already:
                logger.info("stripe webhook replay ignored: %s", idempotency_key)
                return {"status": "ok", "idempotent": True}

            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "status": webhook_response.event_type,
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    "$addToSet": {"processed_events": idempotency_key},
                },
            )

            # Process payment if successful
            if webhook_response.payment_status == "paid":
                transaction = await db.payment_transactions.find_one(
                    {"session_id": webhook_response.session_id}, {"_id": 0}
                )
                if transaction:
                    metadata = transaction.get("metadata", {})
                    user_id = metadata.get("user_id")
                    
                    if metadata.get("type") == "subscription":
                        plan_id = metadata.get("plan_id")
                        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
                        billing_period = (metadata.get("billing") or "monthly").lower()
                        # Annual = monthly credits × (12 + bonus months), computed
                        # once in services.annual_billing.resolve_plan_pricing.
                        # metadata.credits_granted is the authoritative number the
                        # user was quoted at checkout.
                        credits_to_grant = int(metadata.get("credits_granted") or plan["credits"])
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "plan_id": plan_id,
                                "credits": credits_to_grant,
                                "credits_used": 0,
                                "status": "active",
                                "billing": billing_period,
                                "renewed_at": datetime.now(timezone.utc).isoformat()
                            }},
                            upsert=True
                        )
                        # Operator split — plan-level operator_share_pct decides
                        # how much of the cash is booked as profit vs how much
                        # backs the user's credit usage. Credits granted to the
                        # user are derived from the backing dollars × the
                        # CREDITS_PER_USD rate (real PAYG, not the plan's
                        # legacy fixed credits field). Both writes idempotent
                        # via the same session_id.
                        try:
                            from services import revenue_service
                            from services.billing import wallet_service
                            from services.billing.plan_buckets import split_credits, plan_allows_general_fallback
                            from shared.constants import CREDITS_PER_USD
                            price_usd = float(plan.get("price_usd") or 0.0)
                            share_pct = float(plan.get("operator_share_pct", 0.30))
                            operator_usd = round(price_usd * share_pct, 6)
                            user_backing_usd = round(price_usd - operator_usd, 6)
                            credits_derived = max(0, round(user_backing_usd * CREDITS_PER_USD))
                            # Subscription plans grant per-bucket allowances
                            # (chat / vibe / image / video / voice / stt / agent_sop)
                            # per the plan's ratio split in plan_buckets.py — so
                            # buyers see hard-limited pools in their wallet, not
                            # one vague credit number that funnels into general.
                            bucket_splits = split_credits(credits_derived, plan_id)
                            await wallet_service.grant_buckets(
                                user_id, bucket_splits,
                                reference_type="stripe_subscription",
                                reference_id=webhook_response.session_id,
                                description=f"Subscription: {plan_id} ({credits_derived} credits split by modality)",
                                metadata={"price_usd": price_usd, "operator_share_pct": share_pct,
                                          "operator_share_usd": operator_usd,
                                          "user_backing_usd": user_backing_usd,
                                          "plan_id": plan_id,
                                          "bucket_splits": bucket_splits},
                            )
                            # Propagate plan's fallback policy onto the wallet
                            # so plan-level spillover rules apply on debit.
                            await db.wallets.update_one(
                                {"user_id": user_id},
                                {"$set": {"allow_general_fallback": plan_allows_general_fallback(plan_id)}},
                            )
                            # Treasury: automated revenue / cogs-reserve / profit split.
                            # Operator no longer picks which provider gets what — this books
                            # the 3-way split on the operator's ledger. Provider payments
                            # still happen via each provider's own native auto-recharge.
                            try:
                                from services.billing import treasury
                                await treasury.on_subscription_paid(
                                    amount_usd=price_usd,
                                    plan_id=plan_id,
                                    user_id=user_id,
                                    reference_id=webhook_response.session_id,
                                    description=f"Subscription: {plan_id}",
                                )
                            except Exception as tex:
                                logger.warning("treasury booking failed for %s: %s",
                                               webhook_response.session_id, tex)
                            # Unified token quota grant — the CLIENT's single credit
                            # pool. credits_derived × 100,000 tokens (configurable).
                            # This is the hard cap the client spends from.
                            try:
                                from services.billing import token_quota
                                token_grant = token_quota.credits_to_tokens(credits_derived)
                                await token_quota.grant_tokens(
                                    user_id, token_grant,
                                    reference_id=webhook_response.session_id,
                                    description=f"Plan renewal: {plan_id} ({credits_derived} credits)",
                                    plan_id=plan_id,
                                    reset_period=True,   # monthly renewal resets used + period
                                )
                            except Exception as tqx:
                                logger.warning("token_quota grant failed for %s: %s",
                                               webhook_response.session_id, tqx)
                            if operator_usd > 0:
                                await revenue_service.record_revenue(
                                    amount_usd=operator_usd,
                                    source_type="stripe_subscription",
                                    source_ref=webhook_response.session_id,
                                    user_id=user_id, package_id=plan_id,
                                    metadata={"price_usd": price_usd, "operator_share_pct": share_pct},
                                )
                        except Exception as exc:
                            logger.warning("split booking failed for subscription %s: %s",
                                           webhook_response.session_id, exc)
                    elif metadata.get("type") == "credits":
                        credits_to_add = int(metadata.get("credits", 0))
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$inc": {"credits": credits_to_add}},
                            upsert=True
                        )
                        # Top-up credits — same operator-share heuristic, default
                        # 30% if the buyer's plan didn't specify one.
                        try:
                            from services import revenue_service
                            from services.billing import wallet_service
                            amount_usd = (transaction.get("amount") or 0) / 100.0
                            share_pct = 0.30
                            operator_usd = round(amount_usd * share_pct, 6)
                            # Top-ups land on `general` bucket (flexible pool)
                            # since the buyer didn't pick a modality. Plan
                            # renewals get split; ad-hoc top-ups stay generic.
                            await wallet_service.grant(
                                user_id, credits_to_add,
                                reference_type="stripe_credits_topup",
                                reference_id=webhook_response.session_id,
                                description=f"Credit top-up: {credits_to_add}",
                                metadata={"amount_usd": amount_usd, "operator_share_pct": share_pct},
                                bucket="general",
                            )
                            # Treasury: book the 3-way split for credit top-ups too.
                            try:
                                from services.billing import treasury
                                await treasury.on_subscription_paid(
                                    amount_usd=amount_usd,
                                    plan_id=metadata.get("package_id") or "creator",
                                    user_id=user_id,
                                    reference_id=webhook_response.session_id,
                                    description=f"Top-up: {credits_to_add} credits",
                                )
                            except Exception as tex:
                                logger.warning("treasury top-up booking failed for %s: %s",
                                               webhook_response.session_id, tex)
                            # Token quota top-up — additive (does NOT reset period).
                            try:
                                from services.billing import token_quota
                                topup_tokens = token_quota.credits_to_tokens(credits_to_add)
                                await token_quota.grant_tokens(
                                    user_id, topup_tokens,
                                    reference_id=webhook_response.session_id,
                                    description=f"Top-up: {credits_to_add} credits",
                                    plan_id=None,
                                    reset_period=False,
                                )
                            except Exception as tqx:
                                logger.warning("token_quota top-up grant failed: %s", tqx)
                            if operator_usd > 0:
                                await revenue_service.record_revenue(
                                    amount_usd=operator_usd,
                                    source_type="stripe_credits_topup",
                                    source_ref=webhook_response.session_id,
                                    user_id=user_id,
                                    metadata={"amount_usd": amount_usd, "credits": credits_to_add},
                                )
                        except Exception as exc:
                            logger.warning("split booking failed for credit top-up %s: %s",
                                           webhook_response.session_id, exc)
                    elif metadata.get("type") == "custom_package":
                        credits_to_add = int(metadata.get("credits", 0))
                        selected_agents = [a for a in metadata.get("selected_agents", "").split(",") if a]
                        include_commander = metadata.get("include_commander", "False") == "True"
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "plan_id": "custom",
                                "credits": credits_to_add,
                                "credits_used": 0,
                                "selected_agents": selected_agents,
                                "has_commander": include_commander,
                                "status": "active",
                                "renewed_at": datetime.now(timezone.utc).isoformat()
                            }},
                            upsert=True
                        )

                    # ── Cross-cutting post-payment side effects ──
                    # All run best-effort — never rollback the payment
                    # because one of these threw.
                    charge_amount_usd = float(transaction.get("amount") or 0)
                    if metadata.get("currency") == "bdt":
                        # Convert BDT back to USD for referral math
                        try:
                            from services.pricing_currencies import get_rates
                            rates = await get_rates()
                            charge_amount_usd = charge_amount_usd / max(rates.get("bdt", 122.0), 1)
                        except Exception:
                            charge_amount_usd = charge_amount_usd / 122.0

                    # 1) Attach referral if one came in on the checkout.
                    ref_code = metadata.get("referral_code")
                    if ref_code:
                        try:
                            from services import referrals
                            await referrals.attach_referral_to_signup(user_id, ref_code)
                        except Exception as exc:
                            logger.warning("referral attach failed: %s", exc)

                    # 2) Fire referral payout if the user was referred.
                    try:
                        from services import referrals
                        await referrals.on_paid_conversion(user_id, charge_amount_usd)
                    except Exception as exc:
                        logger.info("referral payout skipped: %s", exc)

                    # 3) In-app notification + transactional email — payment success.
                    try:
                        from routes.notifications_center import notify
                        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
                        label = (metadata.get("plan_id") or metadata.get("package_id") or "purchase").title()
                        await notify(
                            user_id,
                            f"Payment confirmed — {label}",
                            body=f"${charge_amount_usd:.2f} received. Credits are live.",
                            kind="success",
                            link="/dashboard",
                        )
                        if user_doc and user_doc.get("email"):
                            from services.transactional_emails import send_payment_success
                            await send_payment_success(
                                user_doc,
                                amount_usd=charge_amount_usd,
                                plan_name=label,
                                credits=int(metadata.get("credits_granted") or metadata.get("credits") or 0),
                            )
                    except Exception as exc:
                        logger.warning("payment-success notify/email skipped: %s", exc)

                    # 4) Customer webhook emit — lets customers' own backends
                    # react to credit top-ups via subscribed webhook URLs.
                    try:
                        from services.customer_webhooks import fire
                        await fire("credit.topped_up", {
                            "user_id": user_id,
                            "amount_usd": round(charge_amount_usd, 2),
                            "plan_id": metadata.get("plan_id"),
                            "package_id": metadata.get("package_id"),
                            "credits": int(metadata.get("credits_granted") or metadata.get("credits") or 0),
                            "billing": metadata.get("billing"),
                        }, user_id=user_id)
                    except Exception as exc:
                        logger.info("credit.topped_up webhook skipped: %s", exc)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """Get user's current credits"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        return {"credits": 50, "plan": "free"}
    return {"credits": sub.get("credits", 0), "plan": sub.get("plan_id", "free")}

# ============== CUSTOM PACKAGE ENDPOINTS ==============

@router.get("/custom-package/config")
async def get_custom_package_config_endpoint():
    """Get custom package pricing config (public)"""
    config = await get_custom_package_config()
    config.pop("config_type", None)
    return config

@router.post("/custom-package/checkout")
async def custom_package_checkout(request: Request, current_user: User = Depends(get_current_user)):
    """Create a Stripe checkout for a custom package via native stripe SDK."""
    import stripe as _stripe
    import asyncio as _asyncio
    _stripe.api_key = STRIPE_API_KEY

    body = await request.json()
    selected_agents = body.get("selected_agents", [])
    credit_preset_id = body.get("credit_preset_id", "")
    include_commander = body.get("include_commander", False)
    origin_url = body.get("origin_url", "")
    currency = body.get("currency", "usd").lower()
    
    if not selected_agents:
        raise HTTPException(status_code=400, detail="Select at least one agent")
    if not credit_preset_id:
        raise HTTPException(status_code=400, detail="Select a credit package")
    
    config = await get_custom_package_config()
    
    # Find the credit preset
    credit_preset = None
    for preset in config.get("credit_presets", []):
        if preset["id"] == credit_preset_id:
            credit_preset = preset
            break
    if not credit_preset:
        raise HTTPException(status_code=400, detail="Invalid credit preset")
    
    price_key = "price_bdt" if currency == "bdt" else "price_usd"
    agent_price_key = f"per_agent_{price_key}"
    commander_price_key = f"commander_addon_{price_key}"
    
    # Calculate total
    num_agents = len(selected_agents)
    agent_cost = num_agents * config.get(agent_price_key, config.get("per_agent_price_usd", 5.0))
    credit_cost = credit_preset[price_key]
    commander_cost = config.get(commander_price_key, 0) if include_commander else 0
    total = agent_cost + credit_cost + commander_cost
    
    if total <= 0:
        raise HTTPException(status_code=400, detail="Invalid package total")
    
    metadata = {
        "type": "custom_package",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "selected_agents": ",".join(selected_agents),
        "credit_preset_id": credit_preset_id,
        "credits": str(credit_preset["credits"]),
        "include_commander": str(include_commander),
        "currency": currency
    }
    
    success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/pricing"

    amount_minor = int(round(float(total) * 100))
    product_name = f"MAARS Custom — {num_agents} agents + {credit_preset['credits']} credits"

    def _create():
        return _stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": product_name},
                    "unit_amount": amount_minor,
                },
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
            customer_email=current_user.email,
        )
    session = await _asyncio.to_thread(_create)

    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "type": "custom_package",
        "amount": total,
        "currency": currency,
        "metadata": metadata,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "breakdown": {
            "agents": num_agents,
            "agent_cost": agent_cost,
            "credits": credit_preset["credits"],
            "credit_cost": credit_cost,
            "commander": include_commander,
            "commander_cost": commander_cost,
            "total": total
        }
    }

@router.get("/subscription/agents")
async def get_selected_agents(current_user: User = Depends(get_current_user)):
    """Get user's selected agents"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        return {"selected_agents": [], "plan_id": "free", "max_agents": 1, "includes_commander": False}
    
    plan_id = sub.get("plan_id", "free")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
    
    is_custom = plan_id == "custom"
    selected = sub.get("selected_agents", [])
    has_commander = sub.get("has_commander", False)
    
    if not is_custom and plan:
        includes_commander = plan.get("includes_commander", False)
    else:
        includes_commander = has_commander
    
    return {
        "selected_agents": selected,
        "plan_id": plan_id,
        "max_agents": plan.get("max_agents", 1) if plan else 0,
        "includes_commander": includes_commander,
        "is_custom": is_custom
    }

@router.put("/subscription/agents")
async def update_selected_agents(request: Request, current_user: User = Depends(get_current_user)):
    """Update user's selected agents (for fixed plans)"""
    body = await request.json()
    selected_agents = body.get("selected_agents", [])
    
    is_admin = current_user.email == ADMIN_EMAIL
    
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=400, detail="No subscription found")
    
    plan_id = sub.get("plan_id", "free")
    
    if plan_id == "custom":
        raise HTTPException(status_code=400, detail="Custom package agents are set at purchase time")
    
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
    max_agents = plan.get("max_agents", 1)
    
    # Filter out commander from count (it's controlled by plan)
    non_commander = [a for a in selected_agents if a != "agent_commander"]
    
    if not is_admin and len(non_commander) > max_agents:
        raise HTTPException(status_code=400, detail=f"Your {plan['name']} plan allows up to {max_agents} agents. You selected {len(non_commander)}.")
    
    await db.subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"selected_agents": selected_agents}}
    )
    
    return {"selected_agents": selected_agents, "message": "Agents updated"}

