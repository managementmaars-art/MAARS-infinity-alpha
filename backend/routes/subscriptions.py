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
    """Get all subscription plans + custom package config"""
    custom_config = await get_custom_package_config()
    custom_config.pop("config_type", None)
    credit_pkgs = await get_credit_packages()
    return {"plans": SUBSCRIPTION_PLANS, "credit_packages": credit_pkgs, "custom_package": custom_config}

@router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        # Create default free subscription
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
    
    plan_info = SUBSCRIPTION_PLANS.get(sub.get("plan_id", "free"), SUBSCRIPTION_PLANS["free"])
    return {**sub, "plan_info": plan_info}

@router.post("/checkout")
async def create_checkout(checkout_data: CheckoutRequest, request: Request, current_user: User = Depends(get_current_user)):
    """Create a Stripe checkout session for subscription or credits"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    host_url = checkout_data.origin_url
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/stripe"
    currency = checkout_data.currency.lower()
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    if checkout_data.type == "subscription":
        if checkout_data.plan_id not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan = SUBSCRIPTION_PLANS[checkout_data.plan_id]
        price_key = "price_bdt" if currency == "bdt" else "price_usd"
        if plan[price_key] == 0:
            raise HTTPException(status_code=400, detail="Free plan doesn't require payment")
        
        amount = plan[price_key]
        metadata = {
            "type": "subscription",
            "plan_id": checkout_data.plan_id,
            "user_id": current_user.user_id,
            "email": current_user.email,
            "currency": currency
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
                "currency": currency
            }
    else:
        raise HTTPException(status_code=400, detail="Invalid checkout type")
    
    success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/settings"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(amount),
        currency=currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "type": checkout_data.type,
        "amount": amount,
        "currency": "usd",
        "metadata": metadata,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, current_user: User = Depends(get_current_user)):
    """Check payment status and update subscription/credits"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
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
            return {"status": "success", "message": f"Subscribed to {plan['name']} plan", "payment_status": "paid"}
        
        elif metadata.get("type") == "credits":
            credits_to_add = int(metadata.get("credits", 0))
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$inc": {"credits": credits_to_add}},
                upsert=True
            )
            return {"status": "success", "message": f"Added {credits_to_add} credits", "payment_status": "paid"}
        
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
    """Handle Stripe webhooks"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "status": webhook_response.event_type,
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
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
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "plan_id": plan_id,
                                "credits": plan["credits"],
                                "credits_used": 0,
                                "status": "active",
                                "renewed_at": datetime.now(timezone.utc).isoformat()
                            }},
                            upsert=True
                        )
                    elif metadata.get("type") == "credits":
                        credits_to_add = int(metadata.get("credits", 0))
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$inc": {"credits": credits_to_add}},
                            upsert=True
                        )
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
    """Create a Stripe checkout for a custom package"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
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
    
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(total),
        currency=currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
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
        "session_id": session.session_id,
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

