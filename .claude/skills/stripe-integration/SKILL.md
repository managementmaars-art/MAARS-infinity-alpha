---
name: stripe-integration
description: Stripe payments — Checkout, Payment Intents, subscriptions, webhooks, Connect, billing portal, fraud prevention for MAARS payment agents
---

# Stripe Integration — MAARS Reference

## Payment Intents
```python
import stripe
stripe.api_key = STRIPE_SECRET_KEY

def create_payment_intent(amount_cents: int, currency: str = "usd",
                           customer_id: str = None, metadata: dict = None):
    return stripe.PaymentIntent.create(
        amount=amount_cents, currency=currency,
        customer=customer_id, metadata=metadata or {},
        automatic_payment_methods={"enabled": True},
    )
```

## Checkout Session
```python
def create_checkout_session(price_id: str, customer_email: str,
                             success_url: str, cancel_url: str,
                             mode: str = "payment"):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode=mode,  # "payment" | "subscription" | "setup"
        customer_email=customer_email,
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )
```

## Subscriptions
```python
def create_subscription(customer_id: str, price_id: str, trial_days: int = 0):
    params = {"customer": customer_id, "items": [{"price": price_id}],
              "payment_behavior": "default_incomplete",
              "expand": ["latest_invoice.payment_intent"]}
    if trial_days:
        params["trial_period_days"] = trial_days
    return stripe.Subscription.create(**params)

def cancel_subscription(subscription_id: str, at_period_end: bool = True):
    return stripe.Subscription.modify(subscription_id,
                                       cancel_at_period_end=at_period_end)

def upgrade_subscription(subscription_id: str, new_price_id: str):
    sub = stripe.Subscription.retrieve(subscription_id)
    return stripe.Subscription.modify(subscription_id,
        items=[{"id": sub["items"]["data"][0]["id"], "price": new_price_id}],
        proration_behavior="create_prorations")

def create_billing_portal_session(customer_id: str, return_url: str):
    return stripe.billing_portal.Session.create(customer=customer_id,
                                                 return_url=return_url)
```

## Webhooks (FastAPI)
```python
from fastapi import Request, HTTPException

async def handle_stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(400, "Invalid webhook")
    
    handlers = {
        "payment_intent.succeeded": handle_payment_succeeded,
        "customer.subscription.created": handle_sub_created,
        "customer.subscription.deleted": handle_sub_deleted,
        "invoice.payment_failed": handle_invoice_failed,
    }
    handler = handlers.get(event["type"])
    if handler:
        await handler(event["data"]["object"])
    return {"received": True}
```

## Connect (Marketplace)
```python
def create_stripe_account(email: str, country: str = "US") -> str:
    account = stripe.Account.create(type="express", email=email,
        country=country,
        capabilities={"card_payments": {"requested": True},
                      "transfers": {"requested": True}})
    return account.id

def create_account_link(account_id: str, refresh_url: str, return_url: str):
    return stripe.AccountLink.create(account=account_id,
        refresh_url=refresh_url, return_url=return_url,
        type="account_onboarding")

def charge_with_platform_fee(amount: int, fee: int, connected_account_id: str):
    return stripe.PaymentIntent.create(amount=amount, currency="usd",
        application_fee_amount=fee,
        transfer_data={"destination": connected_account_id})
```

## Stripe CLI
```bash
stripe login
stripe listen --forward-to localhost:8000/webhooks/stripe
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

## Key Patterns
```python
STRIPE_BEST_PRACTICES = {
    "idempotency": "Always pass idempotency_key for POST requests",
    "error_handling": "Catch stripe.error.CardError, stripe.error.RateLimitError",
    "webhooks": "Always verify signature — never trust payload alone",
    "test_cards": {
        "success": "4242424242424242",
        "3ds_required": "4000002760003184",
        "decline": "4000000000000002",
        "insufficient_funds": "4000000000009995",
    },
    "amounts": "Always in smallest currency unit (cents for USD)",
    "metadata": "Store order_id, user_id in metadata for reconciliation",
}
```

## Models to Use
- **Payment flow architecture**: `claude-sonnet-4-6`
- **Webhook logic**: `claude-sonnet-4-6`
- **Fraud pattern analysis**: `claude-opus-4-6`
