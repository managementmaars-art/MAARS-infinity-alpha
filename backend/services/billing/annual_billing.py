"""Annual billing support — 20% discount + 12-month Stripe subscription.

Monthly is the path of least resistance, but annual lifts LTV ~25% and
kills card-failure churn (one payment a year vs twelve attempts). Every
SaaS optimizing for revenue offers annual.

How it works:
  1. Each plan in SUBSCRIPTION_PLANS has price_usd (monthly). We derive
     the annual price as monthly × 12 × (1 - discount), default 0.20.
  2. `resolve_plan_pricing(plan_id, billing)` returns {usd, bdt, label,
     credits_bonus} — credits_bonus is a sweetener (extra 2 months'
     worth of credits) for people who commit.
  3. Stripe checkout session gets the annual price line item via the
     existing /checkout endpoint; we just pick the right interval.
"""
from __future__ import annotations
import os
from typing import Literal


Billing = Literal["monthly", "annual"]


ANNUAL_DISCOUNT = float(os.environ.get("MAARS_ANNUAL_DISCOUNT", "0.20"))
ANNUAL_CREDIT_BONUS_MONTHS = int(os.environ.get("MAARS_ANNUAL_CREDIT_BONUS_MONTHS", "2"))


def resolve_plan_pricing(plan: dict, billing: Billing = "monthly", bdt_rate: float = 107.0) -> dict:
    """Return price + credits for the requested billing period.

    Monthly: price_usd × 1 + credits × 1
    Annual:  price_usd × 12 × (1 - discount) with credits × (12 + bonus)
    """
    monthly_usd = float(plan.get("price_usd", 0) or 0)
    monthly_credits = int(plan.get("credits", 0) or 0)

    if billing == "annual":
        discount = ANNUAL_DISCOUNT
        usd = round(monthly_usd * 12 * (1 - discount), 2)
        credits = monthly_credits * (12 + ANNUAL_CREDIT_BONUS_MONTHS)
        label_suffix = f"/year ({int(discount*100)}% off)"
        stripe_interval = "year"
    else:
        usd = round(monthly_usd, 2)
        credits = monthly_credits
        label_suffix = "/month"
        stripe_interval = "month"

    return {
        "billing": billing,
        "price_usd": usd,
        "price_bdt": round(usd * bdt_rate),
        "credits": credits,
        "stripe_interval": stripe_interval,
        "label": f"${usd:,.0f}{label_suffix}",
        "monthly_equivalent_usd": round(usd / (12 if billing == "annual" else 1), 2),
        "savings_vs_monthly_usd": (
            round((monthly_usd * 12) - usd, 2) if billing == "annual" else 0
        ),
        "credit_bonus_months": ANNUAL_CREDIT_BONUS_MONTHS if billing == "annual" else 0,
    }
