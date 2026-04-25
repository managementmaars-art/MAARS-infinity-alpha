"""Centralized pricing math — single source of truth for every credit/cost
formula in MAARS-Command. All call sites (admin routes, provider_intelligence,
profit_engine, frontend mirror) read through this module so the locked
engine_config flows through every calculation automatically.

Before this module existed, the same formulas were inline in 5+ files with
inconsistent constants — backend used TOKENS_PER_CREDIT=500 while frontend
used 1000, media credit costs were hardcoded in provider_intelligence.py
instead of reading the operator's locked engine_config, and the margin
formula appeared in at least 3 places with subtle rounding differences.
"""
from __future__ import annotations
from typing import Any

# Defaults MUST match frontend/src/utils/pricingMath.js DEFAULT_ENGINE_CONFIG.
# When you change one, change the other.
#
# UNIFIED MODEL — 2026-04-24
#   1 credit = 100,000 tokens (hard cap the client spends from)
#   Media credits_per_action recalibrated against MEASURED provider costs
#   so every line here matches what the client can actually buy:
#     image_std   = 0       (Pollinations free; router-first)
#     image_hd    = 6       (if paid: Flux $0.003 ÷ $0.005/credit = 0.6 cr)  ×10 for HD safety
#     video/sec   = 1       (Fal LTX $0.005/sec ÷ $0.005 per-credit = 1)
#     tts         = 0       (Edge free)
#     voiceover   = 3       (ElevenLabs $0.018 / $0.005 = 3.6 → round 3)
#     stt         = 0       (Groq Whisper free)
DEFAULT_ENGINE_CONFIG: dict[str, float] = {
    "tokens_per_credit":         100_000,    # was 1000 — 100× bump to align with token_quota.py
    # Chat + Code per-action rates — NEW — operator sets these directly
    # rather than deriving from token math. 0.015 cr/msg assumes ~1500
    # tokens per realistic chat message (1k in + 500 out) at 100k tok/cr;
    # 0.04 cr/run assumes 4k tokens for a code/vibe run. Operator can
    # override to charge more/less per category without touching
    # tokens_per_credit. 0 = free (e.g. if operator wants chat to be
    # unlimited on a specific plan).
    "chat_credits_per_msg":      0.015,
    "code_credits_per_run":      0.04,
    "image_std_credits":         0,           # Pollinations free
    "image_hd_credits":          6,           # Flux-dev paid fallback
    "video_credits_per_sec":     1,           # Fal LTX $0.005/sec
    "tts_credits_per_min":       0,           # Edge TTS free
    "voiceover_credits_per_min": 3,           # ElevenLabs Turbo paid fallback
    "stt_credits_per_min":       0,           # Groq Whisper free
}

# Historical chat-only fallback. Retained for callers that MUST stay
# synchronous (no async access to gateway_usage_logs). New callers should
# use `real_cost_per_credit()` which pulls measured data via
# services.base_cost_calculator. A cold install has no measurements
# yet — in that case base_cost_calculator itself falls back to
# $0.001/credit (the audited mixed-workload figure), not the old
# $0.00003 fantasy.
DEFAULT_AI_COST_PER_CREDIT = 0.00003
DEFAULT_MARGIN_PCT         = 200
DEFAULT_BDT_RATE           = 107


async def real_cost_per_credit(
    *, user_id: str | None = None, plan_id: str | None = None,
) -> float:
    """Measured blended cost from the last 30 days of gateway_usage_logs.
    Prefer this over `DEFAULT_AI_COST_PER_CREDIT` everywhere a call site
    can go async. Falls back to $0.001/credit on a fresh install (mixed
    workload default) and $0.00003 only if base_cost_calculator breaks."""
    try:
        from services.costing.base_cost_calculator import effective_cost_per_credit
        return await effective_cost_per_credit(user_id=user_id, plan_id=plan_id)
    except Exception:
        return DEFAULT_AI_COST_PER_CREDIT


async def load_pricing_config() -> dict[str, Any]:
    """Load the active (locked) pricing config from DB; merge in defaults so
    consumers never see missing keys. Safe to call on every request — reads
    one small doc."""
    from db import db
    doc = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0}) or {}
    return {
        "engine_config": {**DEFAULT_ENGINE_CONFIG, **(doc.get("engine_config") or {})},
        "ai_cost_per_credit":   doc.get("ai_cost_per_credit", DEFAULT_AI_COST_PER_CREDIT),
        "target_profit_margin": doc.get("target_profit_margin", DEFAULT_MARGIN_PCT),
        "bdt_exchange_rate":    doc.get("bdt_exchange_rate", DEFAULT_BDT_RATE),
        "plans": doc.get("plans", {}),
        "locked_at":       doc.get("engine_config_locked_at"),
        "locked_by":       doc.get("engine_config_locked_by"),
        "locked_snapshot": doc.get("ai_cost_locked_snapshot"),
    }


# ── Pure formula primitives ────────────────────────────────────────────────

def ai_cost_usd(credits: float, cost_per_credit: float) -> float:
    """USD cost to serve `credits` at the given blended rate. This is the
    client's strict spend cap — they cannot consume more than this much
    compute regardless of their plan price."""
    return round(credits * cost_per_credit, 4)


def profit_usd(price_usd: float, ai_cost: float) -> float:
    """Per-customer profit = price - compute cost."""
    return round(price_usd - ai_cost, 2)


def margin_pct(profit: float, ai_cost: float) -> float:
    """Markup over cost. Returns 999999 when cost is zero (free tier)."""
    if ai_cost <= 0:
        return 999999.0
    return round((profit / ai_cost) * 100, 1)


def operator_share_pct(profit: float, price_usd: float) -> float:
    """What fraction of revenue the operator keeps (derived, not set)."""
    if price_usd <= 0:
        return 0.0
    return round((profit / price_usd) * 100, 2)


def suggested_price(ai_cost: float, margin_target_pct: float) -> float:
    """Auto-derived plan price at the target markup."""
    return round(ai_cost * (1 + margin_target_pct / 100), 2)


def token_cost_usd(
    *,
    prompt_tokens: int,
    completion_tokens: int,
    input_price_per_m: float,
    output_price_per_m: float,
) -> float:
    """Canonical per-call provider cost formula.

    Before this function existed, the same math was inline in
    `stream_billing.py` (twice), `smart_router.py`, and implicitly in
    several admin endpoints. Each used slightly different rounding and
    one averaged `(input+output)/2` which silently over-billed
    completion-heavy workloads. Call this helper instead of rolling your
    own multiplication.

    Prices are USD per 1 million tokens (the shape MODEL_COSTS_MAP uses).
    """
    return (
        (int(prompt_tokens or 0)     * float(input_price_per_m or 0)
        + int(completion_tokens or 0) * float(output_price_per_m or 0))
        / 1_000_000
    )


def usd_to_bdt(usd: float, rate: float) -> int:
    """Rounded BDT from USD."""
    return round(usd * rate)


def credits_to_tokens(credits: float, engine_config: dict) -> int:
    """Total LLM tokens the plan can consume end-to-end."""
    return int(credits * engine_config.get("tokens_per_credit", DEFAULT_ENGINE_CONFIG["tokens_per_credit"]))


def media_capacity(credits: float, engine_config: dict) -> dict[str, Any]:
    """If the client spent 100% of credits on one modality. Real use is a mix;
    these are the ceilings the Package Advisor surfaces."""
    ec = {**DEFAULT_ENGINE_CONFIG, **engine_config}
    vsec = ec["video_credits_per_sec"]
    video_clips_4s = credits // (vsec * 4) if vsec > 0 else 0
    return {
        "images_standard":   int(credits // ec["image_std_credits"]) if ec["image_std_credits"] else 0,
        "images_hd":         int(credits // ec["image_hd_credits"]) if ec["image_hd_credits"] else 0,
        "video_seconds":     round(credits / vsec, 1) if vsec else 0,
        "video_clips_4sec":  int(video_clips_4s),
        "video_incapable":   video_clips_4s < 1,
        "tts_minutes":       int(credits // ec["tts_credits_per_min"]) if ec["tts_credits_per_min"] else 0,
        "voiceover_minutes": int(credits // ec["voiceover_credits_per_min"]) if ec["voiceover_credits_per_min"] else 0,
        "stt_minutes":       int(credits // ec["stt_credits_per_min"]) if ec["stt_credits_per_min"] else 0,
    }


def plan_economics(
    credits: float,
    price_usd: float,
    cost_per_credit: float,
    margin_target_pct: float = DEFAULT_MARGIN_PCT,
    bdt_rate: float = DEFAULT_BDT_RATE,
) -> dict[str, Any]:
    """Full financial snapshot for one plan. Used by both the Pricing Command
    Center (UI calculations) and the Package Advisor (AI-cost breakdown)."""
    cost = ai_cost_usd(credits, cost_per_credit)
    profit = profit_usd(price_usd, cost)
    return {
        "credits":            credits,
        "price_usd":          price_usd,
        "ai_cost":            cost,
        "profit":             profit,
        "margin_pct":         margin_pct(profit, cost),
        "operator_share_pct": operator_share_pct(profit, price_usd),
        "suggested_price":    suggested_price(cost, margin_target_pct) if price_usd > 0 else 0.0,
        "price_bdt":          usd_to_bdt(price_usd, bdt_rate),
        "monthly_cap_usd":    cost,  # strict spend cap = compute cost
        "profitable":         profit > 0,
    }


def stamp_plan(plan: dict, bdt_rate: float, cost_per_credit: float) -> dict:
    """Stamp computed BDT + monthly_cap_usd onto a plan dict (mirrors the
    frontend stampDerived so the DB always has the same derived fields
    the UI shows). Returns a new dict, doesn't mutate."""
    credits = float(plan.get("credits", 0) or 0)
    price_usd = float(plan.get("price_usd", 0) or 0)
    return {
        **plan,
        "price_bdt":       usd_to_bdt(price_usd, bdt_rate),
        "monthly_cap_usd": ai_cost_usd(credits, cost_per_credit),
    }


async def plan_reality(plan_id: str) -> dict[str, Any]:
    """Definitive answer to 'is this plan priced and stocked correctly?'.

    Pulls the plan dict from constants / DB, uses MEASURED blended cost
    from base_cost_calculator (per-plan if the plan has active users,
    global otherwise), and returns a consistency report:

    {
      "plan_id", "name", "price_usd", "credits",
      "cost_per_credit_used": 0.0012,  # REAL, not fake
      "ai_cost_usd_real":     6.00,    # credits × real cost
      "profit_usd":           344.00,
      "margin_pct_real":      5733.3,
      "operator_share_pct_real": 98.2,
      "published_monthly_cap_usd": 6.00,
      "published_vs_real_delta":   0.0,
      "modality_capacity": {...},
      "warnings": [
        "Starter (300cr) can't afford 1 Sora video (needs 400cr)",
        "Published monthly_cap_usd $0.90 is 10x off from real $9.00",
      ],
      "profitable": true,
    }
    """
    from shared.constants import SUBSCRIPTION_PLANS
    cfg = await load_pricing_config()
    ec  = cfg["engine_config"]

    plan = dict(SUBSCRIPTION_PLANS.get(plan_id) or {})
    if not plan:
        return {"plan_id": plan_id, "error": "unknown plan"}
    plan.setdefault("credits", 0)
    plan.setdefault("price_usd", 0)

    # Use measured blended cost; if this plan has active users, their
    # shape is the right signal. Otherwise global.
    real_cpc = await real_cost_per_credit(plan_id=plan_id)

    credits   = float(plan["credits"])
    price_usd = float(plan["price_usd"])
    cost_real = ai_cost_usd(credits, real_cpc)
    profit    = profit_usd(price_usd, cost_real)

    # What the plan currently publishes (from stamp_plan or constants):
    published_cap = float(plan.get("monthly_cap_usd") or 0)

    cap = media_capacity(credits, ec)

    warnings: list[str] = []
    # Free tier is expected to run at a loss. Only flag margin pressure on paid plans.
    if price_usd > 0 and cost_real > price_usd * 0.95:
        warnings.append(
            f"Real cost (${cost_real:.2f}) is >=95% of price (${price_usd:.2f}) — margin under pressure"
        )
    if published_cap and abs(published_cap - cost_real) > max(0.5, published_cap * 0.3):
        warnings.append(
            f"Published monthly_cap_usd (${published_cap:.2f}) is inconsistent with real cost (${cost_real:.2f})"
        )
    if cap["video_incapable"] and any(
        "video" in f.lower() or "sora" in f.lower() for f in (plan.get("features") or [])
    ):
        warnings.append(
            f"Features promise video but {int(credits)}cr can't afford a single 4s clip "
            f"(needs {int(ec['video_credits_per_sec'] * 4)}cr)"
        )
    if cap["images_standard"] < 5 and any(
        "image" in f.lower() for f in (plan.get("features") or [])
    ):
        warnings.append(f"Features imply images but capacity is only {cap['images_standard']} standard images")

    # Credit grant sized relative to price. Flag outlier $/credit ratios.
    if price_usd > 0:
        price_per_credit = price_usd / max(credits, 1)
        if price_per_credit > 1.5:
            warnings.append(f"Price-per-credit (${price_per_credit:.2f}) is high vs peer plans (~$0.17-0.40)")

    return {
        "plan_id":          plan_id,
        "name":             plan.get("name", plan_id.title()),
        "price_usd":        price_usd,
        "credits":          credits,
        "cost_per_credit_used": real_cpc,
        "ai_cost_usd_real":     cost_real,
        "profit_usd":           profit,
        "margin_pct_real":      margin_pct(profit, cost_real),
        "operator_share_pct_real": operator_share_pct(profit, price_usd),
        "published_monthly_cap_usd": published_cap,
        "published_vs_real_delta":   round(cost_real - published_cap, 2),
        "modality_capacity":    cap,
        "warnings":             warnings,
        "profitable":           profit > 0,
        "generated_at":         __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }


async def all_plans_reality() -> list[dict[str, Any]]:
    """Snapshot across every plan. One Mongo hit per plan for per-user
    cost; cached 5 minutes inside base_cost_calculator."""
    from shared.constants import SUBSCRIPTION_PLANS
    out: list[dict[str, Any]] = []
    for pid in SUBSCRIPTION_PLANS.keys():
        out.append(await plan_reality(pid))
    return out
