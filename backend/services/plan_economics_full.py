"""Centralized plan economics — every cost line, per plan, in one place.

pricing_math.plan_reality() already answers "is the plan's LLM cost math
consistent?". That's necessary but not sufficient: a real enterprise
client also incurs email, voice, lead research (proxy amortization),
self-host GPU amortization, infrastructure amortization. Without all
those lines folded in, "margin" is a sales-deck number, not a real
one.

This module produces ONE record per plan with:
  • Revenue                  (price_usd × expected_active_users)
  • Variable LLM cost        (credits × real blended $/credit)
  • Variable media cost      (GPU electricity share OR paid fallback)
  • Variable email cost      (SMTP self-host = $0, SendGrid fallback)
  • Variable voice cost      (Twilio minutes)
  • Proxy amortization       ($pool/month ÷ active scraping clients)
  • GPU amortization         ($hardware + electricity ÷ active media clients)
  • Infrastructure share     (VPS ÷ total clients)
  • Gross margin              (revenue − ALL variable costs)
  • Worst-case margin         (same but assuming client max-consumes every bucket)

Assumptions are explicit + tunable via env so the operator can swap
them to match real invoices. Defaults are conservative.

Public API:
  async plan_ledger(plan_id) -> dict
  async all_plan_ledgers() -> list[dict]
  async fleet_summary() -> dict  (totals across all plans combined)
"""
from __future__ import annotations
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ── Tunable cost assumptions (override via env) ───────────────────────

def _cfg() -> dict[str, float]:
    """Cost knobs. Pull from env so the operator can swap real numbers
    after they see their first month of invoices."""
    return {
        # Email
        "email_cost_self_hosted_usd":  float(os.environ.get("MAARS_COST_EMAIL_SELF_USD", "0.0")),
        "email_cost_sendgrid_usd":     float(os.environ.get("MAARS_COST_EMAIL_SG_USD", "0.0001")),
        # Voice (Twilio US domestic outbound)
        "voice_cost_per_min_usd":      float(os.environ.get("MAARS_COST_VOICE_PER_MIN_USD", "0.013")),
        # Proxy rental, amortized
        "proxy_rental_monthly_usd":    float(os.environ.get("MAARS_COST_PROXY_POOL_USD", "0.0")),
        # GPU box for local media (CapEx amortized over 24 months + electricity)
        "gpu_monthly_amortized_usd":   float(os.environ.get("MAARS_COST_GPU_MONTHLY_USD", "0.0")),
        # Infrastructure (VPS + Mongo if self-hosted + bandwidth)
        "infra_monthly_usd":           float(os.environ.get("MAARS_COST_INFRA_MONTHLY_USD", "80.0")),
        # SaaS you pay per flat monthly (Stripe fee folded into billed_usd; won't
        # add it to variable cost. Same for domain, CDN, etc.)
    }


# ── Usage-share model ─────────────────────────────────────────────────
# How clients on each plan USE their capacity — not pure ceilings, an
# expected realistic mix. These drive expected-cost math. A ceiling
# ("worst case") uses 100% of every bucket.

_EXPECTED_UTILIZATION = {
    # % of granted capacity a typical client on this plan actually consumes
    "chat":    0.30,   # 30% of the ceiling
    "image":   0.40,
    "video":   0.20,   # most plans burn most credits here if they go media-heavy
    "tts":     0.10,
    "voice_calls_minutes_per_user": {
        "free": 0, "starter": 10, "essential": 30, "basic": 60,
        "standard": 120, "professional": 200, "advanced": 300,
        "business": 400, "agency": 500, "studio": 600,
        "enterprise": 800, "corporate": 1000, "elite": 1200,
        "white_label": 2000,
    },
    "emails_per_user": {
        "free": 0, "starter": 100, "essential": 200, "basic": 400,
        "standard": 800, "professional": 1200, "advanced": 1600,
        "business": 2000, "agency": 2500, "studio": 3000,
        "enterprise": 4000, "corporate": 5000, "elite": 6000,
        "white_label": 10000,
    },
}


# Per-plan default credit mix across the 5 tracks. Overridden by
# plan["expected_mix"] when the operator has set it. Sums to ~1.0.
# These defaults match how the unified 5-tier is positioned:
#   Free     — mostly chat, sampled media
#   Creator  — balanced creator workflow
#   Studio   — media-heavy with coding
#   Scale    — production (images + video + app builds)
#   Infinity — heavy code + premium media
_DEFAULT_EXPECTED_MIX = {
    "free":     {"chat": 0.80, "code": 0.05, "image": 0.10, "video": 0.00, "voice": 0.05},
    "creator":  {"chat": 0.45, "code": 0.15, "image": 0.20, "video": 0.15, "voice": 0.05},
    "studio":   {"chat": 0.30, "code": 0.20, "image": 0.20, "video": 0.20, "voice": 0.10},
    "scale":    {"chat": 0.20, "code": 0.25, "image": 0.25, "video": 0.25, "voice": 0.05},
    "infinity": {"chat": 0.15, "code": 0.30, "image": 0.20, "video": 0.25, "voice": 0.10},
    # Generic fallback for any unknown plan_id (including legacy tiers).
    "_default": {"chat": 0.30, "code": 0.10, "image": 0.20, "video": 0.30, "voice": 0.10},
}


def _resolve_mix(plan: dict[str, Any], plan_id: str) -> dict[str, float]:
    """Pull the plan's expected mix, falling back to the defaults above.
    Operator can override by saving plan.expected_mix in the pricing
    config. Normalizes to sum=1.0 so downstream math is stable."""
    mix = dict(plan.get("expected_mix") or _DEFAULT_EXPECTED_MIX.get(plan_id) or _DEFAULT_EXPECTED_MIX["_default"])
    total = sum(float(v or 0) for v in mix.values())
    if total <= 0:
        mix = dict(_DEFAULT_EXPECTED_MIX["_default"])
        total = sum(mix.values())
    return {k: round(float(mix.get(k, 0)) / total, 4) for k in ("chat", "code", "image", "video", "voice")}

# How many active scraping clients amortize the proxy pool, and how
# many active media clients amortize the GPU box. Operator tunes.
_AMORTIZATION_ACTIVE_CLIENTS = {
    "proxy":  int(os.environ.get("MAARS_AMORT_PROXY_CLIENTS", "20") or 20),
    "gpu":    int(os.environ.get("MAARS_AMORT_GPU_CLIENTS",   "15") or 15),
    "infra":  int(os.environ.get("MAARS_AMORT_INFRA_CLIENTS", "50") or 50),
}


async def plan_ledger(plan_id: str) -> dict[str, Any]:
    """One full economic record for a plan.

    Plan source precedence (authoritative first):
      1. Live DB pricing config (platform_config.pricing.plans) — what the
         admin most recently saved in PricingManagerTab. This is the
         source of truth once the operator has published plans.
      2. Unified PLAN_CATALOG — the canonical 5-tier catalog. Used when a
         plan_id exists in the catalog but hasn't been persisted yet.
      3. Legacy SUBSCRIPTION_PLANS — 13-tier back-compat for existing
         subscribers; only consulted if neither of the above have the id.
    Without this precedence, Studio was rendering with the legacy $2500
    price while the UI showed the unified $99 (58.2% margin bug).
    """
    from shared.constants import SUBSCRIPTION_PLANS
    from services.pricing_math import load_pricing_config, real_cost_per_credit
    from services.plan_capacity import derive_capacity, capacity_features

    cfg = _cfg()
    pricing_cfg = await load_pricing_config()
    ec = pricing_cfg.get("engine_config") or {}

    live_plans = pricing_cfg.get("plans") or {}
    plan = dict(live_plans.get(plan_id) or {})
    if not plan:
        try:
            from services.billing.plan_deliverables import PLAN_CATALOG, total_credits_for
            catalog_plan = next((p for p in PLAN_CATALOG if p.get("plan_id") == plan_id), None)
            if catalog_plan:
                plan = {
                    "name":      catalog_plan.get("name", plan_id.title()),
                    "price_usd": catalog_plan.get("price_usd", 0),
                    "credits":   total_credits_for(plan_id),
                }
        except Exception:
            pass
    if not plan:
        plan = dict(SUBSCRIPTION_PLANS.get(plan_id) or {})
    if not plan:
        return {"plan_id": plan_id, "error": "unknown plan"}

    price = float(plan.get("price_usd") or 0)
    credits = float(plan.get("credits") or 0)
    real_cpc = await real_cost_per_credit(plan_id=plan_id)

    cap = derive_capacity(credits, ec)

    # ── Per-deliverable cost — 8 DEDICATED tracks, no merging ────────
    # Each deliverable type has its own $/credit rate (chat, code,
    # image_std, image_hd, video, voiceover, tts, stt). When a plan has
    # `deliverables_counts` (the new UI-driven shape), we compute cost
    # directly: count × credits_per_unit × $/credit_for_that_track.
    # When only legacy `expected_mix` is set, we fall back to splitting
    # credits by the 5-way mix (image/voice stay merged for that path
    # only — they split apart the moment the operator fills deliverables).
    from services.costing.blended_by_category import blended_by_category as _bbc, CATEGORY_KEYS
    per_cat_blended = await _bbc()
    rate = lambda k: (per_cat_blended.get(k, {}).get("value") or 0.0)

    deliverables_counts = plan.get("deliverables_counts") or {}
    if deliverables_counts:
        # AUTHORITATIVE PATH — each deliverable billed at its dedicated rate.
        # Chat + code now use operator-set per-action rates rather than
        # token-derived formulas. Operator tunes them in the engine config
        # strip just like the media rates.
        cr_per = {
            "chats":         float(ec.get("chat_credits_per_msg")      or 0.015),
            "code_runs":     float(ec.get("code_credits_per_run")      or 0.04),
            "hd_images":     float(ec.get("image_hd_credits")          or 0),
            "std_images":    float(ec.get("image_std_credits")         or 0),
            "videos_4s":     4.0 * float(ec.get("video_credits_per_sec") or 0),
            "voiceover_min": float(ec.get("voiceover_credits_per_min") or 0),
            "tts_min":       float(ec.get("tts_credits_per_min")       or 0),
            "stt_min":       float(ec.get("stt_credits_per_min")       or 0),
        }
        track_of = {
            "chats": "chat", "code_runs": "code",
            "hd_images": "image_hd", "std_images": "image_std",
            "videos_4s": "video",
            "voiceover_min": "voiceover", "tts_min": "tts", "stt_min": "stt",
        }
        per_cat_credits = {k: 0.0 for k in CATEGORY_KEYS}
        per_cat_cost    = {k: 0.0 for k in CATEGORY_KEYS}
        for delivery, count in (deliverables_counts or {}).items():
            track = track_of.get(delivery)
            if not track:
                continue
            cnt = float(count or 0)
            cr  = cnt * cr_per.get(delivery, 0)
            per_cat_credits[track] += cr
            per_cat_cost[track]    += cr * rate(track)
        per_cat_cost = {k: round(v, 4) for k, v in per_cat_cost.items()}
    else:
        # LEGACY PATH — _DEFAULT_EXPECTED_MIX (5 buckets) × credits.
        # Still splits image/voice into the dedicated rates by reweighting.
        mix = _resolve_mix(plan, plan_id)
        per_cat_credits = {k: 0.0 for k in CATEGORY_KEYS}
        per_cat_credits["chat"]  = credits * mix.get("chat",  0)
        per_cat_credits["code"]  = credits * mix.get("code",  0)
        # Legacy "image" → 70% std + 30% HD for back-compat estimation.
        per_cat_credits["image_std"] = credits * mix.get("image", 0) * 0.70
        per_cat_credits["image_hd"]  = credits * mix.get("image", 0) * 0.30
        per_cat_credits["video"] = credits * mix.get("video", 0)
        # Legacy "voice" → 40% tts + 40% vo + 20% stt.
        per_cat_credits["tts"]       = credits * mix.get("voice", 0) * 0.40
        per_cat_credits["voiceover"] = credits * mix.get("voice", 0) * 0.40
        per_cat_credits["stt"]       = credits * mix.get("voice", 0) * 0.20
        per_cat_cost = {k: round(per_cat_credits[k] * rate(k), 4) for k in CATEGORY_KEYS}

    # Legacy roll-ups for UI back-compat. `llm_chat` = text tracks,
    # `media` = everything else.
    llm_cost_expected   = per_cat_cost["chat"] + per_cat_cost["code"]
    media_cost_expected_measured = (
        per_cat_cost["image_std"] + per_cat_cost["image_hd"]
        + per_cat_cost["video"]
        + per_cat_cost["voiceover"] + per_cat_cost["tts"] + per_cat_cost["stt"]
    )

    # ── Read the cost_config toggles — operator's self-host levers ───
    # Ledger math is driven by `active_claim` (operator intent), not
    # `active` (claim + env verified). That lets the operator model
    # target deployment costs BEFORE the infra is wired — flip a
    # toggle, see the post-deploy cost immediately. The UI still shows
    # a NEEDS ENV warning when env_detected is False so nobody forgets
    # to wire the actual infrastructure at deploy time.
    try:
        from services.costing.cost_config import get_config as _cc
        lv = (await _cc()).get("levers") or {}
    except Exception:
        lv = {}
    def _claimed(key: str, env_var: str | None = None) -> bool:
        return bool(lv.get(key, {}).get("active_claim")) or bool(env_var and os.environ.get(env_var))
    using_local_media  = _claimed("local_media",  "MAARS_LOCAL_IMAGE_URL")
    using_self_smtp    = _claimed("self_smtp",    "MAARS_SMTP_HOST")
    using_telnyx_voice = _claimed("telnyx_voice", "TELNYX_API_KEY")

    # ── Variable media cost ───────────────────────────────────────────
    # If local GPU is active, marginal media = $0 (covered by gpu_share).
    # Otherwise use the measured-categorical figure from above.
    media_cost_expected = 0.0 if using_local_media else media_cost_expected_measured

    # Unified 5-tier plans fold cold-outreach costs into the credit pool —
    # there are no separate email/voice quotas to charge against. For those
    # plan_ids, zero out the bolt-on expectations (the client's actual
    # email/voice usage is already absorbed by the chat/media share of the
    # credit budget).
    try:
        from services.billing.plan_deliverables import PLAN_CATALOG as _UNIFIED_CATALOG
        _unified_ids = {p.get("plan_id") for p in _UNIFIED_CATALOG}
    except Exception:
        _unified_ids = {"free", "creator", "studio", "scale", "infinity"}
    is_unified_tier = plan_id in _unified_ids

    # ── Email ─────────────────────────────────────────────────────────
    emails_expected = 0 if is_unified_tier else _EXPECTED_UTILIZATION["emails_per_user"].get(plan_id, 0)
    email_per_unit = cfg["email_cost_self_hosted_usd"] if using_self_smtp else cfg["email_cost_sendgrid_usd"]
    email_cost_expected = emails_expected * email_per_unit

    # ── Voice ─────────────────────────────────────────────────────────
    # Telnyx is ~45% cheaper than Twilio's $0.013/min = $0.007/min.
    voice_minutes_expected = 0 if is_unified_tier else _EXPECTED_UTILIZATION["voice_calls_minutes_per_user"].get(plan_id, 0)
    voice_per_min = 0.007 if using_telnyx_voice else cfg["voice_cost_per_min_usd"]
    voice_cost_expected = voice_minutes_expected * voice_per_min

    # ── Amortizations ────────────────────────────────────────────────
    proxy_share = cfg["proxy_rental_monthly_usd"] / max(_AMORTIZATION_ACTIVE_CLIENTS["proxy"], 1)
    gpu_share   = cfg["gpu_monthly_amortized_usd"] / max(_AMORTIZATION_ACTIVE_CLIENTS["gpu"], 1) if using_local_media else 0
    infra_share = cfg["infra_monthly_usd"] / max(_AMORTIZATION_ACTIVE_CLIENTS["infra"], 1)

    # ── Worst-case (client maxes every bucket) ───────────────────────
    worst_llm   = credits * real_cpc                                   # all credits at real cpc
    worst_email = (cap.get("cold_emails") or 0) * email_per_unit
    worst_voice = (cap.get("cold_call_minutes") or 0) * cfg["voice_cost_per_min_usd"]
    worst_total = (
        worst_llm + worst_email + worst_voice
        + proxy_share + gpu_share + infra_share
    )

    expected_total_cost = (
        llm_cost_expected + media_cost_expected
        + email_cost_expected + voice_cost_expected
        + proxy_share + gpu_share + infra_share
    )

    return {
        "plan_id":            plan_id,
        "name":                plan.get("name", plan_id.title()),
        "price_usd":           price,
        "credits":             int(credits),

        # what the buyer sees
        "capacity_features":   capacity_features(credits, ec),

        # Deliverable counts (authoritative when set) + legacy mix.
        "deliverables_counts": deliverables_counts,

        # Per-track cost decomposition — 8 DEDICATED tracks, no merging.
        # Each key gets its own $/credit rate and its own cost line.
        # UI uses this to render the 8-card strip + cost breakdown.
        "per_category": {
            c: {
                "credits_allocated":  round(per_cat_credits.get(c, 0), 4),
                "blended_per_credit": per_cat_blended.get(c, {}).get("value", 0),
                "blended_source":     per_cat_blended.get(c, {}).get("source", "unknown"),
                "cost_usd":           per_cat_cost.get(c, 0),
            }
            for c in CATEGORY_KEYS
        },

        # variable cost lines
        "expected_costs": {
            "llm_chat":        round(llm_cost_expected, 4),
            "media":           round(media_cost_expected, 4),
            "email":           round(email_cost_expected, 4),
            "voice":           round(voice_cost_expected, 4),
            "proxy_share":     round(proxy_share, 4),
            "gpu_share":       round(gpu_share, 4),
            "infra_share":     round(infra_share, 4),
            "total":           round(expected_total_cost, 4),
        },

        # ceiling analysis
        "worst_case_costs": {
            "llm_all_credits": round(worst_llm, 4),
            "email":           round(worst_email, 4),
            "voice":           round(worst_voice, 4),
            "proxy_share":     round(proxy_share, 4),
            "gpu_share":       round(gpu_share, 4),
            "infra_share":     round(infra_share, 4),
            "total":           round(worst_total, 4),
        },

        "revenue_usd":          round(price, 2),
        "expected_margin_usd":  round(price - expected_total_cost, 2),
        "expected_margin_pct":  round(((price - expected_total_cost) / price) * 100, 2) if price > 0 else None,
        "worst_case_margin_usd": round(price - worst_total, 2),
        "worst_case_margin_pct": round(((price - worst_total) / price) * 100, 2) if price > 0 else None,
        "profitable_expected":  price > expected_total_cost,
        "profitable_worst_case": price > worst_total,

        # infra state the numbers assume
        "assumptions": {
            "blended_cost_per_credit_usd": real_cpc,
            "using_local_media":           using_local_media,
            "using_self_smtp":             using_self_smtp,
            "using_telnyx_voice":          using_telnyx_voice,
            "amortization_active_clients": _AMORTIZATION_ACTIVE_CLIENTS,
            "cost_knobs":                  cfg,
        },
    }


async def all_plan_ledgers() -> list[dict[str, Any]]:
    """Ledger for every plan the admin has published, falling back to the
    unified catalog + legacy SUBSCRIPTION_PLANS when nothing is saved yet.
    Mirrors plan_ledger()'s precedence so both endpoints agree on which
    plans exist."""
    from shared.constants import SUBSCRIPTION_PLANS
    from services.pricing_math import load_pricing_config
    try:
        from services.billing.plan_deliverables import PLAN_CATALOG
        catalog_ids = [p.get("plan_id") for p in PLAN_CATALOG if p.get("plan_id")]
    except Exception:
        catalog_ids = []
    pricing_cfg = await load_pricing_config()
    live_ids = list((pricing_cfg.get("plans") or {}).keys())

    seen: set[str] = set()
    pids: list[str] = []
    for pid in live_ids + catalog_ids + list(SUBSCRIPTION_PLANS.keys()):
        if pid and pid not in seen:
            seen.add(pid)
            pids.append(pid)

    out: list[dict[str, Any]] = []
    for pid in pids:
        out.append(await plan_ledger(pid))
    return out


async def fleet_summary() -> dict[str, Any]:
    """Summed fleet view — total revenue + total cost + gross margin
    IF you had 1 active customer on every plan tier. Useful to see
    which tiers pull the boat."""
    ledgers = await all_plan_ledgers()
    total_revenue = sum(l.get("revenue_usd", 0) for l in ledgers)
    total_expected_cost = sum(l.get("expected_costs", {}).get("total", 0) for l in ledgers)
    total_worst_cost    = sum(l.get("worst_case_costs", {}).get("total", 0) for l in ledgers)
    return {
        "total_plans":           len(ledgers),
        "revenue_usd_one_each":  round(total_revenue, 2),
        "expected_cost_usd":     round(total_expected_cost, 2),
        "expected_gross_margin_usd": round(total_revenue - total_expected_cost, 2),
        "expected_gross_margin_pct": round(
            ((total_revenue - total_expected_cost) / total_revenue) * 100, 2
        ) if total_revenue > 0 else None,
        "worst_case_cost_usd":   round(total_worst_cost, 2),
        "worst_case_margin_usd": round(total_revenue - total_worst_cost, 2),
        "plans": ledgers,
    }
