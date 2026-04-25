"""Plan capacity translator — turn "credits" into "what the buyer can do."

A client paying $10K/month doesn't care about tokens_per_credit. They
care: how many cold emails can I send? How many posts scheduled? How
many images, videos, voice-overs?

This module converts a plan's credit grant into a human-readable
capacity table using the operator's locked engine_config. All functions
are synchronous — this is pure math, no DB.

Headline capacities the buyer cares about:

  ai_messages              — chat/agent calls (a meaningful "message" = 400 tokens in, 400 out)
  cold_emails              — personalized sends (LLM draft + actual send)
  social_posts             — generated + scheduled (usually short-form copy)
  brand_images             — 1024×1024 standard quality
  brand_images_hd          — 1024×1024 HD
  video_clips_4sec         — 4-second brand clips
  voiceover_minutes        — premium voice (brand voice quality)
  tts_minutes              — standard TTS (robotic/polished but generic)
  stt_minutes              — transcription
  workflow_runs            — full DAG executions (we model 5 nodes avg)
  leads_researched         — Apollo/Hunter enrichment queries
  cold_call_minutes        — Twilio minutes (separate hard-cost line)
"""
from __future__ import annotations
from typing import Any

# One "AI message" in buyer-land = ~400 tokens in + ~400 tokens out.
# At tokens_per_credit=1000, that's 0.8 credits per message.
MESSAGE_TOKENS       = 800
COLD_EMAIL_COST_CR   = 3      # draft (LLM) + personalization + send overhead
SOCIAL_POST_COST_CR  = 2      # short-form copy + scheduling
WORKFLOW_RUN_COST_CR = 8      # ~5 nodes avg, some of them LLM nodes
LEAD_RESEARCH_COST_CR = 2     # one enrichment query
COLD_CALL_MIN_COST_CR = 20    # Twilio + TTS + call handling per minute


def derive_capacity(credits: float, engine_config: dict) -> dict[str, Any]:
    """Given a credit grant + the operator's locked engine config, return
    a per-modality ceiling in units the buyer understands.

    Ceilings are INDEPENDENT — if the client uses 100% of their credits
    on one thing, they can't use ANY of the others. Real clients mix.
    The dashboard shows these as "up to" numbers.
    """
    c = float(credits or 0)
    tokens_per_credit        = int(engine_config.get("tokens_per_credit", 1000) or 1000)
    image_std_cr             = int(engine_config.get("image_std_credits", 20) or 20)
    image_hd_cr              = int(engine_config.get("image_hd_credits", 40) or 40)
    video_cr_per_sec         = int(engine_config.get("video_credits_per_sec", 100) or 100)
    tts_cr_per_min           = int(engine_config.get("tts_credits_per_min", 15) or 15)
    voiceover_cr_per_min     = int(engine_config.get("voiceover_credits_per_min", 30) or 30)
    stt_cr_per_min           = int(engine_config.get("stt_credits_per_min", 5) or 5)

    messages = int(c * tokens_per_credit / MESSAGE_TOKENS) if tokens_per_credit else 0

    return {
        "ai_messages":         messages,
        "cold_emails":         int(c // COLD_EMAIL_COST_CR),
        "social_posts":        int(c // SOCIAL_POST_COST_CR),
        "brand_images":        int(c // image_std_cr) if image_std_cr else 0,
        "brand_images_hd":     int(c // image_hd_cr) if image_hd_cr else 0,
        "video_clips_4sec":    int(c // (video_cr_per_sec * 4)) if video_cr_per_sec else 0,
        "video_seconds":       round(c / video_cr_per_sec, 1) if video_cr_per_sec else 0,
        "tts_minutes":         int(c // tts_cr_per_min) if tts_cr_per_min else 0,
        "voiceover_minutes":   int(c // voiceover_cr_per_min) if voiceover_cr_per_min else 0,
        "stt_minutes":         int(c // stt_cr_per_min) if stt_cr_per_min else 0,
        "workflow_runs":       int(c // WORKFLOW_RUN_COST_CR),
        "leads_researched":    int(c // LEAD_RESEARCH_COST_CR),
        "cold_call_minutes":   int(c // COLD_CALL_MIN_COST_CR),
    }


def capacity_features(credits: float, engine_config: dict,
                      include_all: bool = False) -> list[str]:
    """Human-readable feature list for a plan. The default trims to the
    top-signal items for a marketing page; include_all=True returns
    every capacity line for admin/comparison view."""
    cap = derive_capacity(credits, engine_config)

    def fmt(n: int) -> str:
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000:    return f"{n/1_000:.1f}k" if n % 1000 else f"{n//1000}k"
        return str(n)

    # Headline items for buyer-facing pricing cards.
    lines = [
        f"Up to {fmt(cap['ai_messages'])} AI assistant messages / month",
        f"Up to {fmt(cap['cold_emails'])} personalized cold emails",
        f"Up to {fmt(cap['social_posts'])} scheduled social posts",
        f"Up to {fmt(cap['brand_images'])} brand images",
    ]
    if cap["video_clips_4sec"] >= 1:
        lines.append(f"Up to {cap['video_clips_4sec']} brand videos (4-sec clips)")
    else:
        lines.append("Video generation available on Basic tier and above")
    if cap["voiceover_minutes"] >= 1:
        lines.append(f"Up to {cap['voiceover_minutes']} min of premium voice-over")
    lines += [
        f"Up to {fmt(cap['workflow_runs'])} workflow runs",
        f"Up to {fmt(cap['leads_researched'])} lead enrichments",
    ]

    if include_all:
        lines += [
            f"{cap['video_seconds']} seconds of video (total)",
            f"{cap['stt_minutes']} minutes of transcription",
            f"{cap['tts_minutes']} minutes of standard TTS",
            f"{cap['cold_call_minutes']} minutes of cold calls (Twilio)",
        ]
    return lines


async def plan_capacity(plan_id: str) -> dict[str, Any]:
    """Async variant that pulls the locked engine_config. Returns
    {plan, capacity, capacity_features, limits}."""
    from services.pricing_math import load_pricing_config
    from shared.constants import SUBSCRIPTION_PLANS

    cfg = await load_pricing_config()
    plan = dict(SUBSCRIPTION_PLANS.get(plan_id) or {})
    if not plan:
        return {"plan_id": plan_id, "error": "unknown plan"}

    credits = float(plan.get("credits") or 0)
    cap = derive_capacity(credits, cfg["engine_config"])
    return {
        "plan_id":   plan_id,
        "name":      plan.get("name", plan_id.title()),
        "price_usd": plan.get("price_usd", 0),
        "credits":   int(credits),
        "capacity":  cap,
        "capacity_features": capacity_features(credits, cfg["engine_config"]),
        "capacity_features_all": capacity_features(credits, cfg["engine_config"], include_all=True),
    }


async def all_plans_capacity() -> list[dict[str, Any]]:
    """Capacity snapshot across every plan — for the admin pricing page
    and the landing comparison matrix."""
    from shared.constants import SUBSCRIPTION_PLANS
    return [await plan_capacity(pid) for pid in SUBSCRIPTION_PLANS.keys()]
