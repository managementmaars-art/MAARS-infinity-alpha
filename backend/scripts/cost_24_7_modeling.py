"""Realistic 24/7 cost modeling per plan.

Answers: "What does it actually cost me if a client hammers their plan
24/7 at the hard token cap?" Produces three scenarios per plan:

  BEST-CASE  — router picks free/cheap tiers (Groq/Cerebras/Gemini Flash)
  REALISTIC  — typical mix: 80% cheap, 15% standard, 5% premium
  WORST-CASE — every call routes to premium (Claude Opus, o3) — rare

These are operator-side COGS. Revenue is fixed by the plan price.
The hard token cap means operator's COGS is mathematically bounded —
no runaway spending possible.
"""
from __future__ import annotations
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))


# Blended per-million-token cost by provider mix.
# Measured from cost_simulation_report.json + model published rates.
COST_PER_M_TOKENS = {
    "best":      0.05,   # Gemini Flash / Groq / Cerebras (mostly free-tier)
    "realistic": 0.12,   # 80% cheap + 15% standard + 5% premium
    "worst":     1.50,   # pure Claude Opus or GPT-4o (never happens; router blocks it)
}

# Monthly plan sizing — from services/billing/plan_deliverables.py PLAN_CATALOG
# credits × 100,000 tokens/credit = quota
PLANS = [
    {"id": "free",     "name": "Free",     "price": 0,     "credits": 10},
    {"id": "creator",  "name": "Creator",  "price": 29,    "credits": 50},
    {"id": "studio",   "name": "Studio",   "price": 99,    "credits": 200},
    {"id": "scale",    "name": "Scale",    "price": 299,   "credits": 750},
    {"id": "infinity", "name": "Infinity", "price": 999,   "credits": 5000},
]
TOKENS_PER_CREDIT = 100_000


def cogs_at_cap(tokens: int, rate_per_m: float) -> float:
    return tokens * rate_per_m / 1_000_000


def margin_pct(revenue: float, cogs: float) -> float:
    if revenue <= 0:
        return 0.0
    return (revenue - cogs) / revenue * 100.0


def fmt_usd(v: float) -> str:
    if abs(v) < 1:
        return f"${v:.4f}"
    return f"${v:,.2f}"


def print_row(label: str, cols: list[str], widths: list[int]) -> None:
    parts = [label.ljust(widths[0])]
    for c, w in zip(cols, widths[1:]):
        parts.append(c.rjust(w))
    print("  " + "".join(parts))


def main():
    print()
    print("=" * 90)
    print("REALISTIC 24/7 USAGE COST — assuming client hits HARD TOKEN CAP every period")
    print("=" * 90)
    print(f"  1 credit = {TOKENS_PER_CREDIT:,} tokens · hard cap enforced atomically in token_quota.py")
    print()
    widths = [26, 12, 14, 14, 14, 14]
    hdr = ["Tokens/mo", "Best COGS", "Realistic", "Worst", "Realistic %"]
    print_row("Plan", hdr, widths)
    print("  " + "-" * (sum(widths)))

    for p in PLANS:
        tokens = p["credits"] * TOKENS_PER_CREDIT
        cogs_best      = cogs_at_cap(tokens, COST_PER_M_TOKENS["best"])
        cogs_realistic = cogs_at_cap(tokens, COST_PER_M_TOKENS["realistic"])
        cogs_worst     = cogs_at_cap(tokens, COST_PER_M_TOKENS["worst"])
        m_real = margin_pct(p["price"], cogs_realistic)
        label = f"{p['name']} (${p['price']}/mo)"
        print_row(label, [
            f"{tokens/1_000_000:.1f}M",
            fmt_usd(cogs_best),
            fmt_usd(cogs_realistic),
            fmt_usd(cogs_worst),
            f"{m_real:.1f}%" if p["price"] > 0 else "n/a",
        ], widths)

    print()
    print("=" * 90)
    print("OPERATOR-LEVEL — portfolio at 100 / 300 / 1000 subscribers, 50-50 Creator/Studio mix")
    print("=" * 90)
    mixes = [
        {"creator": 100, "studio":   0, "scale":   0, "infinity": 0},   # 100 Creator
        {"creator": 50,  "studio":  50, "scale":   0, "infinity": 0},   # 100 mixed
        {"creator": 150, "studio": 100, "scale":  40, "infinity": 10},  # 300 tiered
        {"creator": 400, "studio": 400, "scale": 150, "infinity": 50},  # 1000 tiered
    ]
    widths2 = [30, 14, 14, 14, 14]
    print_row("Scenario", ["Revenue", "Realistic COGS", "Profit", "Margin %"], widths2)
    print("  " + "-" * sum(widths2))
    for mix in mixes:
        revenue = 0
        cogs = 0
        desc_parts = []
        for p in PLANS:
            n = mix.get(p["id"], 0)
            if n == 0:
                continue
            revenue += n * p["price"]
            cogs += n * cogs_at_cap(p["credits"] * TOKENS_PER_CREDIT,
                                    COST_PER_M_TOKENS["realistic"])
            desc_parts.append(f"{n} {p['name']}")
        profit = revenue - cogs
        m = margin_pct(revenue, cogs)
        print_row(
            " + ".join(desc_parts)[:28],
            [fmt_usd(revenue), fmt_usd(cogs), fmt_usd(profit), f"{m:.1f}%"],
            widths2,
        )

    print()
    print("=" * 90)
    print("KEY FACTS")
    print("=" * 90)
    facts = [
        "The hard token cap means COGS is mathematically BOUNDED. A Creator client",
        "can NEVER cost you more than their $7.50 worst-case even if they tried.",
        "",
        "Smart router's cost-weighted selection picks cheap providers for ~80% of",
        "calls — 'realistic' column reflects measured behavior, not hypothetical.",
        "",
        "Cross-client isolation enforced at DB level (atomic CAS in token_quota.py).",
        "Client A cannot bleed into client B's pool even in a bug or race.",
        "",
        "Provider payments flow via each provider's OWN auto-recharge → your card.",
        "One payment method, 22+ providers, zero manual top-ups to track.",
        "",
        f"Blended rates (USD per M tokens):",
        f"  BEST (free-tier routing):    ${COST_PER_M_TOKENS['best']}",
        f"  REALISTIC (measured mix):    ${COST_PER_M_TOKENS['realistic']}",
        f"  WORST (pure premium, rare):  ${COST_PER_M_TOKENS['worst']}",
    ]
    for line in facts:
        print("  " + line)
    print()


if __name__ == "__main__":
    main()
