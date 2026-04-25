"""Per-plan bucket allowances — the multi-modality credit split.

A plan has one headline number (e.g. Starter = 300 credits/month). That
number is split across the seven dedicated pools:

    chat, vibe, agent_sop, image, video, voice, stt

Ratios below were tuned off the April 2026 cost simulation:
  - chat / vibe / voice / stt are near-free per call (big allowances)
  - video is the single cost driver ($0.40 on Sora → $0.02 on Fal LTX)
  - image is effectively free via Pollinations
  - agent_sop costs ~$0.007 per 6-step run

The goal: every plan tier gets REAL dedicated allowances per modality,
so operator COGS stays predictable. A user who burns their `video`
pool can't accidentally drain their chat budget — the pool is
hard-limited unless their plan enables `allow_general_fallback`.
"""
from __future__ import annotations
from typing import Any

from services.billing.credit_buckets import BUCKETS


# ── Ratio table (normalized to 1.0) ──────────────────────────────────
# Applied to a plan's total-credit headline to produce per-bucket
# allowances. Values reflect cost-model per $50 Starter → $19,999 top tier.

DEFAULT_RATIOS = {
    "chat":      0.50,
    "agent_sop": 0.15,
    "vibe":      0.10,
    "image":     0.10,
    "video":     0.05,
    "voice":     0.05,
    "stt":       0.05,
}
# Sanity: must sum to ~1.0
assert abs(sum(DEFAULT_RATIOS.values()) - 1.0) < 1e-6


# ── Per-plan overrides ───────────────────────────────────────────────
# A plan can override the default ratio split — e.g. a content-ops plan
# might want more video, a pure-dev plan more vibe. Missing entries fall
# back to DEFAULT_RATIOS.

PLAN_OVERRIDES: dict[str, dict[str, float]] = {
    # Free tier: essentially chat-only. No video (too expensive to gift).
    "free": {
        "chat":      0.80,
        "agent_sop": 0.10,
        "vibe":      0.05,
        "image":     0.03,
        "video":     0.00,
        "voice":     0.01,
        "stt":       0.01,
    },
    # Starter: capped video but everything else usable.
    "starter": {
        "chat":      0.60,
        "agent_sop": 0.15,
        "vibe":      0.10,
        "image":     0.08,
        "video":     0.02,
        "voice":     0.03,
        "stt":       0.02,
    },
    # ── Unified 5-tier overrides (canonical going forward) ──
    # Each of these matches how the plan's deliverables were sized in
    # plan_deliverables.py. "image" bucket covers both std + HD (std is
    # free via Pollinations, so it doesn't debit); "voice" covers
    # voiceover + TTS (TTS is free via Edge TTS).
    "creator": {
        # Balanced creator workflow — chats, images, videos, apps.
        "chat":      0.45,  # 5,000 chats / month
        "vibe":      0.15,  # 50 app builds
        "agent_sop": 0.10,  # 100 agent-workflow runs
        "image":     0.15,  # 500 images (mostly std/free)
        "video":     0.10,  # 10 × 4-sec clips
        "voice":     0.04,  # unlimited VO/TTS (fair-use)
        "stt":       0.01,  # unlimited transcription (fair-use)
    },
    "studio": {
        # Content-daily teams — heavier media + app builds.
        "chat":      0.30,  # 25,000 chats
        "vibe":      0.18,  # 250 app builds
        "agent_sop": 0.15,  # 500 agent runs with Commander
        "image":     0.17,  # 2,500 images
        "video":     0.14,  # 50 videos
        "voice":     0.05,
        "stt":       0.01,
    },
    "scale": {
        # Production teams — heavy video + code + image.
        "chat":      0.20,
        "vibe":      0.22,
        "agent_sop": 0.20,  # 2,000 agent runs
        "image":     0.17,  # unlimited images
        "video":     0.16,  # 200 videos
        "voice":     0.04,
        "stt":       0.01,
    },
    "infinity": {
        # Fair-use unlimited — code + video dominant.
        "chat":      0.15,
        "vibe":      0.25,
        "agent_sop": 0.20,
        "image":     0.15,
        "video":     0.20,  # 1,000 videos fair-use
        "voice":     0.04,
        "stt":       0.01,
    },
}


# ── Allow-fallback policy per plan ───────────────────────────────────
# If True, running out of a specific bucket falls through to the
# `general` pool (plan-level buffer). Free/Starter keep hard limits
# so video abuse can't drain chat. Higher tiers get the flexibility.

FALLBACK_POLICY: dict[str, bool] = {
    # Unified 5-tier — free gets hard buckets (can't drain chat by
    # running out of video); paid tiers flow through to general so
    # clients aren't hard-locked when they push a category hot.
    "creator":       True,
    "studio":        True,
    "scale":         True,
    "infinity":      True,
    # Legacy 13-tier (kept for existing subscribers)
    "free":          False,
    "starter":       False,
    "essential":     False,
    "basic":         True,
    "standard":      True,
    "professional":  True,
    "advanced":      True,
    "growth":        True,
    "scale":         True,
    "business":      True,
    "enterprise":    True,
    "elite":         True,
    "infinity":      True,
    "lifetime":      True,
}


def split_credits(total_credits: int, plan_id: str | None = None) -> dict[str, int]:
    """Split a plan's headline credit grant across all buckets.

    Returns {bucket: int_credits}. Any rounding shortfall lands in the
    largest bucket so the sum still equals `total_credits`.
    """
    total = max(0, int(total_credits))
    ratios = dict(DEFAULT_RATIOS)
    if plan_id and plan_id in PLAN_OVERRIDES:
        ratios.update(PLAN_OVERRIDES[plan_id])
    # Round each bucket down, then distribute the leftover to the pool
    # with the biggest ratio so we don't lose credits.
    allocated: dict[str, int] = {}
    for bucket in BUCKETS:
        if bucket == "general":
            allocated[bucket] = 0
            continue
        ratio = ratios.get(bucket, 0)
        allocated[bucket] = int(total * ratio)
    shortfall = total - sum(allocated.values())
    if shortfall > 0:
        biggest = max(ratios.items(), key=lambda kv: kv[1])[0]
        allocated[biggest] = allocated.get(biggest, 0) + shortfall
    return allocated


def plan_allows_general_fallback(plan_id: str | None) -> bool:
    if not plan_id:
        return False
    return FALLBACK_POLICY.get(plan_id, False)


def plan_bucket_summary(plan_id: str, total_credits: int) -> dict[str, Any]:
    """Shape suitable for the pricing UI — shows each bucket allowance
    and the fallback policy so the buyer knows what they're getting."""
    split = split_credits(total_credits, plan_id)
    return {
        "plan_id": plan_id,
        "total_credits": total_credits,
        "bucket_allowances": split,
        "allow_general_fallback": plan_allows_general_fallback(plan_id),
    }
