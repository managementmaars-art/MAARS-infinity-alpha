"""Canonical credit-bucket definitions.

A wallet holds N dedicated pools — chat, vibe, image, video, voice, stt,
agent_sop, general — each with its own balance + reserved. A charge is
tagged with a modality and debits the matching pool; if that pool can't
cover the charge and the plan allows it, the charge falls through to the
`general` pool.

Buckets live as `buckets.<name>.balance` / `.reserved` in Mongo so atomic
$inc on nested paths works.

Adding a bucket is a two-step:
  1. Append the name to BUCKETS here.
  2. Extend the plan catalog (services.billing.plan_buckets) with an
     allowance for that bucket per tier.
"""
from __future__ import annotations

# Canonical bucket names. Order matters for the ensure-all-pools migration.
BUCKETS: tuple[str, ...] = (
    "chat",        # text-only LLM chat + content generation
    "vibe",        # vibe-coding / full-stack app generator
    "agent_sop",   # agent Office SOP runs (multi-step)
    "image",       # image generation
    "video",       # video generation
    "voice",       # TTS + voice-over
    "stt",         # speech-to-text
    "general",     # fallback / unbucketed (e.g. operator adjustments, legacy grants)
)

# Keywords → bucket (lower-case substring match). First match wins.
# Used by classify_source() when only a source tag is known.
SOURCE_TO_BUCKET: tuple[tuple[str, str], ...] = (
    ("office_sop",       "agent_sop"),
    ("agent.",           "agent_sop"),
    ("vibe",             "vibe"),
    ("image",            "image"),
    ("media_image",      "image"),
    ("video",            "video"),
    ("media_video",      "video"),
    ("voice",            "voice"),
    ("tts",              "voice"),
    ("media_tts",        "voice"),
    ("stt",              "stt"),
    ("media_stt",        "stt"),
    ("chat",             "chat"),
    ("content",          "chat"),
    ("workflow",         "chat"),
    ("cold_email",       "chat"),
    ("campaign",         "chat"),
)


def classify_source(source: str | None, modality: str | None = None) -> str:
    """Pick the bucket to charge based on an explicit modality (wins) or
    a source tag keyword. Falls back to `general` so unlabeled legacy
    calls don't break."""
    if modality and modality in BUCKETS:
        return modality
    if not source:
        return "general"
    s = source.lower()
    for kw, bucket in SOURCE_TO_BUCKET:
        if kw in s:
            return bucket
    return "general"


def empty_buckets() -> dict[str, dict[str, int]]:
    """Factory: a fresh wallet's zero'd bucket structure."""
    return {name: {"balance": 0, "reserved": 0} for name in BUCKETS}
