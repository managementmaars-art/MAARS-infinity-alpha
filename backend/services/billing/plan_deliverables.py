"""UNIFIED PLAN MODEL — the single source of truth for what a buyer gets.

Before this module, the product exposed THREE mental models:
  1. Pricing page talked about "credits/month"
  2. Wallet showed 7 technical buckets (chat/vibe/agent_sop/image/video/voice/stt)
  3. Admin used raw per-provider COGS

For a buyer, all three are confusing. This module introduces the
**unified language: Deliverables**. Concrete actions in human units:

  * 5,000 chat messages
  * 500 images
  * 10 videos
  * 50 app builds
  * unlimited voice-overs (Edge TTS)
  * unlimited transcription (Groq Whisper)

Every surface the USER sees speaks deliverables. Under the hood the
bucket system stays intact — it's the cost-attribution layer the
operator uses to monitor provider spend. This file is the ONLY place
where the translation happens.

Data flow:
  Plan choice          →  plan_deliverables.CATALOG (config)
  Plan renewal          →  split_credits() [unchanged]
                        →  deliverables are implied by bucket allowances
  User usage            →  reserve/settle on buckets [unchanged]
  Wallet display        →  deliverables_remaining(wallet) here
  Pricing page display  →  plan_deliverables(plan_id) here
"""
from __future__ import annotations
from typing import Any


# ── Deliverable catalog ──────────────────────────────────────────────
# Maps human-facing deliverables to internal bucket + credit-cost-per-action.
# Adding one: pick a DeliverableKey, set label/icon/bucket/credits_per_action.
# The translator uses credits_per_action to convert bucket balance → count.

# credits_per_action — calibrated against MEASURED provider costs at
# 1 credit = 100,000 tokens, blended $0.05/M tokens cheap-first routing.
# Most modalities are effectively FREE because the router hits Pollinations
# (images), Edge (voice), Groq Whisper (STT) by default. Video is the only
# real credit sink: Fal LTX 4-sec clip ≈ 4 credits.
#
# These values are used for display math ("X credits = Y videos") and for
# the plan-deliverable back-translation UI. They do NOT gate calls — the
# token_quota.py hard cap is what enforces spending.
DELIVERABLES = {
    "chats": {
        "label": "Chat messages",
        "icon":  "MessageSquare",
        "bucket": "chat",
        "credits_per_action": 0.015,   # ~1.5k tokens avg (router picks cheap)
        "unit": "message",
        "hint": "Any text conversation with any agent. Router picks cheapest capable model.",
    },
    "apps": {
        "label": "App / website builds",
        "icon":  "Code2",
        "bucket": "vibe",
        "credits_per_action": 0.08,    # ~8k tokens for full app generation
        "unit": "build",
        "hint": "Full-stack app generation or iterative code edits via Vibe Coding",
    },
    "agent_runs": {
        "label": "Agent full-workflow runs",
        "icon":  "Users",
        "bucket": "agent_sop",
        "credits_per_action": 0.05,    # ~5k tokens for 6-step SOP
        "unit": "run",
        "hint": "Commander Orion or any specialist agent running their full SOP",
    },
    "images": {
        "label": "Images",
        "icon":  "Image",
        "bucket": "image",
        "credits_per_action": 0,       # Pollinations FREE; router-first
        "unit": "image",
        "hint": "Generation via Pollinations (free) · Flux / DALL-E / Gemini fallback",
    },
    "videos": {
        "label": "Videos (4-second clips)",
        "icon":  "Film",
        "bucket": "video",
        "credits_per_action": 4,       # Fal LTX $0.02/4s ÷ $0.005/credit
        "unit": "clip",
        "hint": "Video clip — Fal LTX, CogVideoX, Hailuo, Kling, Sora fallback",
    },
    "voiceovers": {
        "label": "Voice-overs",
        "icon":  "Mic",
        "bucket": "voice",
        "credits_per_action": 0,       # Edge TTS FREE; ElevenLabs paid fallback
        "unit": "voiceover",
        "hint": "Text-to-speech, 29 languages. Edge TTS (free) · ElevenLabs premium",
    },
    "transcription_minutes": {
        "label": "Transcription minutes",
        "icon":  "Headphones",
        "bucket": "stt",
        "credits_per_action": 0,       # Groq Whisper FREE
        "unit": "minute",
        "hint": "Audio → text · Groq Whisper (free) · Deepgram · OpenAI Whisper",
    },
}


# ── 5-tier unified plan catalog ──────────────────────────────────────
# Each plan declares deliverable quantities in human units. Internally,
# we derive total_credits + per-bucket ratios from these quantities so
# the existing wallet/reserve/settle flow keeps working unchanged.
#
# Quantities chosen for ~90-98% gross margin at typical usage profile
# (verified against measured COGS in cost_simulation_report.json).
#
# `unlimited: True` means fair-use — we don't track a count; the wallet
# shows "unlimited". Internally we still reserve credits but a very
# large pool is granted so users won't hit it under normal use.

PLAN_CATALOG = [
    {
        "plan_id": "free",
        "name":    "Free",
        "price_usd": 0,
        "credits_per_period": 10,     # 10 credits × 100k tokens = 1M tokens hard cap
        # Expected credit allocation across the 5 tracks (sum=1.0). Drives
        # plan_ledger's categorical cost math. Operator-tunable in admin UI.
        "expected_mix": {"chat": 0.80, "code": 0.05, "image": 0.10, "video": 0.00, "voice": 0.05},
        "tagline": "Try MAARS — 100% of the gateway, generous starter quota.",
        "deliverables": {
            "chats":                 100,
            "apps":                  3,
            "agent_runs":            10,
            "images":                10,
            "videos":                0,          # free users nudged to upgrade for video
            "voiceovers":            "unlimited", # Edge TTS free
            "transcription_minutes": "unlimited", # Groq Whisper free
        },
        "max_agents":       3,
        "max_custom_agents": 0,
        "includes_commander": False,
        "highlights": [
            "100 chat messages/mo",
            "10 images · 3 app builds",
            "Unlimited voiceover + transcription (always free)",
            "3 pre-built agents",
        ],
    },
    {
        "plan_id": "creator",
        "name":    "Creator",
        "price_usd": 29,
        "credits_per_period": 50,      # 5M tokens hard cap · realistic COGS $0.60 · 97.9% margin
        "expected_mix": {"chat": 0.45, "code": 0.15, "image": 0.20, "video": 0.15, "voice": 0.05},
        "tagline": "The SaaS baseline. Videos, images, chat, apps, all included.",
        "deliverables": {
            "chats":                 5_000,
            "apps":                  50,
            "agent_runs":            100,
            "images":                500,
            "videos":                10,          # 10 × 4-sec clips/mo
            "voiceovers":            "unlimited",
            "transcription_minutes": "unlimited",
        },
        "max_agents":       12,
        "max_custom_agents": 1,
        "includes_commander": False,
        "highlights": [
            "5,000 chats · 500 images · 10 videos",
            "50 full-stack app builds",
            "100 agent-workflow runs",
            "12 pre-built agents + 1 custom",
            "Unlimited voiceover + transcription",
        ],
        "popular": True,
    },
    {
        "plan_id": "studio",
        "name":    "Studio",
        "price_usd": 99,
        "credits_per_period": 200,     # 20M tokens hard cap · COGS ~$2.40 · 97.6% margin
        "expected_mix": {"chat": 0.30, "code": 0.20, "image": 0.20, "video": 0.20, "voice": 0.10},
        "tagline": "For teams shipping content daily. Premium voices, premium video.",
        "deliverables": {
            "chats":                 25_000,
            "apps":                  250,
            "agent_runs":            500,
            "images":                2_500,
            "videos":                50,
            "voiceovers":            "unlimited",
            "transcription_minutes": "unlimited",
        },
        "max_agents":       25,
        "max_custom_agents": 3,
        "includes_commander": True,
        "highlights": [
            "25,000 chats · 2,500 images · 50 videos",
            "250 full-stack app builds",
            "500 agent-workflow runs with Commander Orion",
            "25 agents + 3 custom · teams of 10",
            "Premium ElevenLabs voices unlocked",
        ],
    },
    {
        "plan_id": "scale",
        "name":    "Scale",
        "price_usd": 299,
        "credits_per_period": 750,     # 75M tokens hard cap · COGS ~$9 · 97.0% margin
        "expected_mix": {"chat": 0.20, "code": 0.25, "image": 0.25, "video": 0.25, "voice": 0.05},
        "tagline": "Heavy production. Unlimited images, 200 videos, 1k app builds.",
        "deliverables": {
            "chats":                 100_000,
            "apps":                  1_000,
            "agent_runs":            2_000,
            "images":                "unlimited",
            "videos":                200,
            "voiceovers":            "unlimited",
            "transcription_minutes": "unlimited",
        },
        "max_agents":       41,
        "max_custom_agents": 10,
        "includes_commander": True,
        "highlights": [
            "100,000 chats · unlimited images · 200 videos",
            "1,000 app builds · 2,000 agent runs",
            "All 41 core agents + 10 custom",
            "Priority routing · faster provider response",
            "Teams of 35 · dedicated Slack support",
        ],
    },
    {
        "plan_id": "infinity",
        "name":    "Infinity",
        "price_usd": 999,
        "credits_per_period": 5000,    # 500M tokens fair-use · COGS ~$60 · 94% margin
        "expected_mix": {"chat": 0.15, "code": 0.30, "image": 0.20, "video": 0.25, "voice": 0.10},
        "tagline": "Everything, fair-use. White-glove onboarding.",
        "deliverables": {
            "chats":                 "unlimited",
            "apps":                  "unlimited",
            "agent_runs":            "unlimited",
            "images":                "unlimited",
            "videos":                1_000,       # fair-use ceiling only
            "voiceovers":            "unlimited",
            "transcription_minutes": "unlimited",
        },
        "max_agents":       -1,  # no cap
        "max_custom_agents": -1,
        "includes_commander": True,
        "highlights": [
            "Fair-use unlimited everything",
            "Unlimited agents · unlimited customization",
            "All 499 trained specialist agents",
            "Custom onboarding · named account manager",
            "SLAs · SSO · audit logs",
        ],
    },
]


# ── Legacy → unified plan map ────────────────────────────────────────
# Existing subscribers on the 13-tier ladder map forward to the new
# tiers. Used when /api/plans is requested by a user on an old plan;
# their plan_id stays, but the UI renders under the unified labels.

LEGACY_TO_UNIFIED = {
    "free":          "free",
    "starter":       "creator",
    "essential":     "creator",
    "basic":         "studio",
    "standard":      "studio",
    "professional":  "scale",
    "advanced":      "scale",
    "growth":        "scale",
    "scale":         "scale",
    "business":      "scale",
    "enterprise":    "infinity",
    "elite":         "infinity",
    "infinity":      "infinity",
    "lifetime":      "infinity",
}


# ── Translators ──────────────────────────────────────────────────────

def _deliverable_count(allowance: Any) -> int | str:
    """Pass through 'unlimited' / 0 / numeric as-is for display."""
    if isinstance(allowance, str) and allowance.lower() == "unlimited":
        return "unlimited"
    try:
        return int(allowance)
    except (TypeError, ValueError):
        return 0


def plan_deliverables(plan_id: str | None) -> list[dict]:
    """Return the ordered deliverable list for a plan, in display order.

    Each row: {key, label, icon, unit, count, unlimited, hint}
    If the plan_id is a legacy id, we resolve via LEGACY_TO_UNIFIED first.
    """
    resolved = LEGACY_TO_UNIFIED.get(plan_id or "", plan_id)
    plan = next((p for p in PLAN_CATALOG if p["plan_id"] == resolved), None)
    if plan is None:
        return []
    rows: list[dict] = []
    for key, meta in DELIVERABLES.items():
        allowance = plan["deliverables"].get(key, 0)
        count = _deliverable_count(allowance)
        rows.append({
            "key":       key,
            "label":     meta["label"],
            "icon":      meta["icon"],
            "unit":      meta["unit"],
            "count":     count,
            "unlimited": count == "unlimited",
            "hint":      meta["hint"],
            "bucket":    meta["bucket"],
        })
    return rows


def total_credits_for(plan_id: str) -> int:
    """Return the plan's authoritative credit quota for one period.

    Reads `credits_per_period` directly off the plan entry — the same
    value the operator edits in PricingManagerTab and that becomes the
    client's hard cap. Deliverables are DISPLAY illustrations, not
    quota derivation (prior versions summed them, which double-counted
    unlimited fair-use ceilings and produced nonsense big numbers like
    206,550 credits for Creator).
    """
    resolved = LEGACY_TO_UNIFIED.get(plan_id or "", plan_id)
    plan = next((p for p in PLAN_CATALOG if p["plan_id"] == resolved), None)
    if plan is None:
        return 0
    return int(plan.get("credits_per_period") or 0)


def bucket_split_from_deliverables(plan_id: str) -> dict[str, int]:
    """Returns a per-bucket credit allocation for wallet_service.grant_buckets.

    Since the unified model is ONE token pool (not per-modality quotas),
    this just pours the full plan credit count into `general` so legacy
    bucket-based wallet code keeps working. The actual spend limit is
    enforced by the token_quota hard cap, not per-bucket limits.
    """
    total = total_credits_for(plan_id)
    if total <= 0:
        return {}
    return {"general": int(total)}


def deliverables_remaining(plan_id: str | None, wallet_buckets: dict) -> list[dict]:
    """Translate a wallet's current bucket balances back into human
    deliverable counts. Used by the wallet / header widget.

    Each returned row: {key, label, icon, unit, used, total, remaining,
                        unlimited, progress_pct}
    """
    plan_id = plan_id or ""
    plan_rows = plan_deliverables(plan_id)
    remaining: list[dict] = []
    for row in plan_rows:
        bucket = row.get("bucket")
        per_action = (DELIVERABLES.get(row["key"]) or {}).get("credits_per_action", 1) or 1
        balance = int(((wallet_buckets or {}).get(bucket) or {}).get("balance", 0))
        remaining_count = balance // max(1, per_action)
        total = row["count"]
        if row["unlimited"]:
            used = None
            remaining_disp = "unlimited"
            progress_pct = 0
        else:
            try:
                total_int = int(total)
            except (TypeError, ValueError):
                total_int = 0
            used = max(0, total_int - remaining_count)
            remaining_disp = max(0, remaining_count)
            progress_pct = int(used / total_int * 100) if total_int > 0 else 0
        remaining.append({
            **row,
            "used":         used,
            "total":        total,
            "remaining":    remaining_disp,
            "progress_pct": progress_pct,
        })
    return remaining


def user_plan_summary(plan_id: str | None, price_usd: float, wallet_buckets: dict) -> dict:
    """Everything the wallet widget + dashboard needs in one call.
    Wraps plan metadata + remaining deliverables so the frontend doesn't
    need to cross-reference multiple endpoints."""
    resolved = LEGACY_TO_UNIFIED.get(plan_id or "", plan_id)
    plan = next((p for p in PLAN_CATALOG if p["plan_id"] == resolved), None)
    return {
        "plan_id":         plan_id,
        "unified_plan_id": resolved,
        "plan_name":       (plan or {}).get("name") or "Unknown",
        "price_usd":       price_usd,
        "tagline":         (plan or {}).get("tagline"),
        "includes_commander": (plan or {}).get("includes_commander", False),
        "deliverables":    deliverables_remaining(plan_id, wallet_buckets),
    }
