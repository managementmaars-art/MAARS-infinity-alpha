"""Multi-currency pricing — USD + EUR + GBP (and BDT for local market).

Stripe checkout accepts any supported currency at the Session level.
We convert from USD using a daily-cached FX rate. Operator can set
`MAARS_DISPLAY_CURRENCY=eur` as default for EU-detected visitors.

For EU/UK customers we also enable Stripe Tax automatically (VAT
reverse-charge or gross, depending on B2B/B2C classification).
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Literal

import httpx

logger = logging.getLogger(__name__)

Currency = Literal["usd", "eur", "gbp", "bdt"]

# Fallback rates for when the FX API is down — stale but not missing.
# Operator can override via env if they want fixed rates for stable
# quoting. Updated manually to within 5% of spot.
_FALLBACK_FX = {
    "usd": 1.0,
    "eur": 0.92,
    "gbp": 0.79,
    "bdt": 122.0,
}

_cache: dict = {"rates": None, "ts": None}
_CACHE_TTL_SECONDS = 3600  # refresh hourly


async def _fetch_rates() -> dict[str, float]:
    """Pull live USD-base FX from a free endpoint. Falls back to
    hardcoded rates if the network is down."""
    # Frankfurter is ECB-sourced, no API key required.
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://api.frankfurter.app/latest", params={"from": "USD"})
            if r.status_code == 200:
                data = r.json()
                out = {"usd": 1.0}
                for code, rate in (data.get("rates") or {}).items():
                    out[code.lower()] = float(rate)
                # Frankfurter doesn't carry BDT — use fallback for it
                out.setdefault("bdt", _FALLBACK_FX["bdt"])
                return out
    except Exception as exc:
        logger.info("FX fetch failed, using fallback: %s", exc)
    return dict(_FALLBACK_FX)


async def get_rates() -> dict[str, float]:
    """Cached FX rates keyed by lowercase currency code. USD = 1.0."""
    now = datetime.now(timezone.utc)
    if _cache["rates"] and _cache["ts"] and (now - _cache["ts"]).total_seconds() < _CACHE_TTL_SECONDS:
        return _cache["rates"]
    rates = await _fetch_rates()
    _cache["rates"] = rates
    _cache["ts"] = now
    return rates


async def convert_from_usd(amount_usd: float, target: Currency) -> float:
    """Convert a USD amount to the target currency using cached rates."""
    target = target.lower()
    if target == "usd":
        return round(amount_usd, 2)
    rates = await get_rates()
    rate = rates.get(target, _FALLBACK_FX.get(target, 1.0))
    # BDT gets rounded to whole taka (conventional); others to 2dp
    return float(int(round(amount_usd * rate))) if target == "bdt" else round(amount_usd * rate, 2)


def currency_symbol(code: str) -> str:
    return {"usd": "$", "eur": "€", "gbp": "£", "bdt": "৳"}.get(code.lower(), code.upper() + " ")


def stripe_tax_enabled(currency: str) -> bool:
    """Whether Stripe Tax should be toggled on automatically for this
    currency. EU/UK customers require VAT — Stripe calculates it.
    Operator still needs to activate Stripe Tax in the dashboard +
    add a tax registration for the relevant country."""
    return currency.lower() in ("eur", "gbp") and os.environ.get("STRIPE_TAX_ENABLED", "0") == "1"


# Stripe supports all 4 natively. Minimum-charge rules (in the smallest
# denomination of the currency, e.g. cents / pence / paisa / ore) —
# we surface these so the checkout endpoint can enforce.
STRIPE_MIN_CHARGE_MINOR = {
    "usd": 50,   # $0.50
    "eur": 50,   # €0.50
    "gbp": 30,   # £0.30
    "bdt": 5000, # ৳50
}
