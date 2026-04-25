"""
Profit optimization engine — observes internal cost vs. credits charged and
exposes a signal the router can use to downgrade tiers when margin collapses
or credits run low.

No side effects on its own — it returns a decision and the caller (v1_gateway
or router_scoring) acts on it. This keeps the profit engine testable in
isolation and preserves a single source of truth for margin math.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

DEFAULT_MIN_MARGIN_PCT = 15.0           # below this, prefer cheaper models
DEFAULT_CREDITS_PER_USD = 1000.0
DEFAULT_LOW_BALANCE_THRESHOLD = 10      # credits — switch to economy on this floor


@dataclass
class MarginSnapshot:
    revenue_usd: float
    cost_usd: float
    margin_usd: float
    margin_pct: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "revenue_usd": round(self.revenue_usd, 6),
            "cost_usd": round(self.cost_usd, 6),
            "margin_usd": round(self.margin_usd, 6),
            "margin_pct": round(self.margin_pct, 2),
        }


@dataclass
class ProfitDecision:
    action: str                          # "use_requested" | "downgrade_tier" | "force_economy"
    reason: str
    suggested_tier: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "suggested_tier": self.suggested_tier,
            "metadata": self.metadata,
        }


def compute_margin(
    *,
    credits_charged: int,
    internal_cost_usd: float,
    credits_per_usd: float = DEFAULT_CREDITS_PER_USD,
) -> MarginSnapshot:
    """Revenue → cost → margin breakdown for a single call/batch. The raw
    percentage math is delegated to pricing_math so every margin-percent
    value in the system uses the same formula (previously implemented
    twice, in this module and in pricing_math.margin_pct)."""
    revenue_usd = credits_charged / credits_per_usd if credits_per_usd > 0 else 0.0
    margin_usd = revenue_usd - internal_cost_usd
    # Operator-share semantics: margin as a % of revenue (not of cost).
    from services.pricing_math import operator_share_pct
    margin_pct = operator_share_pct(margin_usd, revenue_usd)
    return MarginSnapshot(
        revenue_usd=revenue_usd,
        cost_usd=internal_cost_usd,
        margin_usd=margin_usd,
        margin_pct=margin_pct,
    )


def decide(
    *,
    credits_remaining: int,
    estimated_credits: int,
    estimated_cost_usd: float,
    requested_tier: str = "standard",
    min_margin_pct: float = DEFAULT_MIN_MARGIN_PCT,
    low_balance_threshold: int = DEFAULT_LOW_BALANCE_THRESHOLD,
    credits_per_usd: float = DEFAULT_CREDITS_PER_USD,
) -> ProfitDecision:
    """
    Advise the router on whether to honor the requested tier, downgrade one
    step, or force economy. No mutation — caller decides whether to act.
    """
    # Hard floor on balance — keep the user alive with the cheapest tier.
    if credits_remaining <= low_balance_threshold:
        return ProfitDecision(
            action="force_economy",
            reason=f"Balance {credits_remaining} ≤ floor {low_balance_threshold} — using economy.",
            suggested_tier="economy",
            metadata={"credits_remaining": credits_remaining, "threshold": low_balance_threshold},
        )

    # Margin check — use the standard per-USD conversion.
    snap = compute_margin(
        credits_charged=estimated_credits,
        internal_cost_usd=estimated_cost_usd,
        credits_per_usd=credits_per_usd,
    )
    if snap.revenue_usd > 0 and snap.margin_pct < min_margin_pct:
        # Downgrade one tier from requested.
        demote = {"premium": "standard", "standard": "economy", "economy": "economy"}
        suggested = demote.get(requested_tier, "economy")
        return ProfitDecision(
            action="downgrade_tier",
            reason=f"Projected margin {snap.margin_pct:.1f}% below floor {min_margin_pct:.1f}%.",
            suggested_tier=suggested,
            metadata={"margin": snap.to_dict(), "requested_tier": requested_tier},
        )

    return ProfitDecision(
        action="use_requested",
        reason="Requested tier fits budget + margin policy.",
        suggested_tier=requested_tier,
        metadata={"margin": snap.to_dict()},
    )
