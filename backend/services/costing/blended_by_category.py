"""Per-category blended cost — $/credit broken out into 8 DEDICATED tracks.

Each deliverable type gets its own $/credit rate. No merging, no
overlap — "Voice" no longer bundles TTS+VO+STT, "Image" no longer
bundles std+HD. Every track is its own provider family with its own
measured or configured cost:

  - chat       — text LLM (Gemini / Groq / Cerebras / DeepSeek)
  - code       — coding LLM (DeepSeek Coder / Qwen Coder, vibe workflows)
  - image_std  — Pollinations (standard/cheap tier)
  - image_hd   — Flux HD (paid tier)
  - video      — Fal LTX / Sora
  - voiceover  — ElevenLabs premium TTS
  - tts        — Edge TTS (basic/free tier)
  - stt        — Groq Whisper (free-tier transcription)

plan_ledger() sums per-deliverable costs directly (no category merging),
so a plan with "50 videos + 500 HD images + 25k chats" gets exactly:
  50 × video_credits × $/cr[video]
  + 500 × image_hd_credits × $/cr[image_hd]
  + 25000 × chat_credits × $/cr[chat]
  + ...

Returned shape (per track key):
    {
      "value":             <float USD/credit>,
      "source":            "real_usage" | "estimated" | "configured",
      "call_count":        <int>,
      "total_cost_usd":    <float>,
      "free_routing_pct":  <float 0-100>,
      "providers":         [(provider, calls), ...]
    }
"""
from __future__ import annotations
import logging
from typing import Any

from db import db
from shared.free_providers import FREE_PROVIDERS as _FREE

logger = logging.getLogger(__name__)

FREE_PROVIDERS: set[str] = set(_FREE)

_cache: dict[str, Any] = {"value": None, "ts": 0.0}
_CACHE_TTL = 30.0

MIN_CALLS_FOR_REAL_DATA = 5   # per category — lower bar than overall since
                              # categories will have smaller samples until
                              # each workload type has run a few times.


# ── Source-string classification ─────────────────────────────────────
# gateway_usage_logs tags each row with a `source` string. Classify it
# into the 5 canonical tracks. Any source not matched here is treated
# as chat — the safe default since text is the dominant workload.

_CODE_PREFIXES = (
    "vibe.",            # vibe-coded app creation (vibe.create, vibe.revise)
    "workflow.",        # workflow evaluator / diagnose / repair
    "workflow_",        # workflow_generator.*, workflow_diagnose
    "agent.code",       # agents tagged as coding
    "sim.vibe",         # vibe smoke tests
)
# Dedicated per-track prefix maps — each deliverable type gets its own
# classification so the rates stay isolated. Std vs HD images go to
# different tracks; TTS/VO/STT each stand alone.
_IMAGE_STD_PREFIXES = ("media.image.std", "media.image_std", "image_std.", "img.std.")
_IMAGE_HD_PREFIXES  = ("media.image.hd",  "media.image_hd",  "image_hd.",  "img.hd.", "media.image", "image.", "img.")  # default image bucket → HD
_VIDEO_PREFIXES     = ("media.video", "video.", "vid.")
_VOICEOVER_PREFIXES = ("media.vo",    "media.voiceover", "voiceover.", "vo.")
_TTS_PREFIXES       = ("media.tts",   "tts.")
_STT_PREFIXES       = ("media.stt",   "stt.")

# Canonical track order — referenced by the frontend top strip and
# MediaBudgetCalculator to render cards in a stable sequence.
CATEGORY_KEYS = ["chat", "code", "image_std", "image_hd", "video", "voiceover", "tts", "stt"]


def classify_source(source: str | None) -> str:
    """Map a log's `source` string to one of the 8 dedicated tracks."""
    if not source:
        return "chat"
    s = str(source).lower()
    if any(s.startswith(p) for p in _STT_PREFIXES):        return "stt"
    if any(s.startswith(p) for p in _TTS_PREFIXES):        return "tts"
    if any(s.startswith(p) for p in _VOICEOVER_PREFIXES):  return "voiceover"
    if any(s.startswith(p) for p in _VIDEO_PREFIXES):      return "video"
    if any(s.startswith(p) for p in _IMAGE_STD_PREFIXES):  return "image_std"
    if any(s.startswith(p) for p in _IMAGE_HD_PREFIXES):   return "image_hd"
    if any(s.startswith(p) for p in _CODE_PREFIXES):       return "code"
    return "chat"


async def _category_blended_from_logs(cat: str) -> dict[str, Any] | None:
    """Compute $/credit for one category from gateway_usage_logs.

    We can't filter Mongo by a classified-category field since the
    logs store raw `source` strings. Instead we aggregate by
    (source, provider) and group client-side. For the volumes we have
    (thousands of rows) this is fine; if it grows, add a persisted
    `category` field at write time and switch to a server-side match.
    """
    try:
        pipeline = [
            {"$group": {
                "_id":     {"src": "$source", "prov": "$provider"},
                "calls":   {"$sum": 1},
                "cost":    {"$sum": {"$ifNull": ["$cost_usd", "$estimated_cost_usd"]}},
                "credits": {"$sum": {"$ifNull": ["$credits_charged", 1]}},
            }},
        ]
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1000)
    except Exception as exc:
        logger.warning("blended_by_category: aggregate failed: %s", exc)
        return None

    matched = [r for r in rows if classify_source((r.get("_id") or {}).get("src")) == cat]
    if not matched:
        return None

    total_calls   = sum(r.get("calls", 0) or 0 for r in matched)
    total_cost    = sum(r.get("cost", 0) or 0 for r in matched)
    total_credits = sum(r.get("credits", 0) or 0 for r in matched)
    if total_calls < MIN_CALLS_FOR_REAL_DATA:
        return None

    free_calls = sum(r["calls"] for r in matched if (r.get("_id") or {}).get("prov") in FREE_PROVIDERS)
    paid_calls = total_calls - free_calls
    denom = total_credits if total_credits > 0 else total_calls
    prov_tally: dict[str, int] = {}
    for r in matched:
        p = (r.get("_id") or {}).get("prov") or "unknown"
        prov_tally[p] = prov_tally.get(p, 0) + (r.get("calls") or 0)
    top_providers = sorted(prov_tally.items(), key=lambda kv: kv[1], reverse=True)[:5]

    return {
        "value":             round(total_cost / denom, 8) if denom else 0.0,
        "source":            "real_usage" if total_credits > 0 else "real_usage_calls_proxy",
        "call_count":        total_calls,
        "total_cost_usd":    round(total_cost, 6),
        "free_routing_pct":  round((free_calls / total_calls) * 100, 1) if total_calls else 0,
        "paid_calls":        paid_calls,
        "free_calls":        free_calls,
        "providers":         top_providers,
    }


async def _estimated_media_rate(cat: str, engine_config: dict[str, Any], real_cpc: float) -> dict[str, Any]:
    """For tracks that don't yet emit gateway_usage_logs rows (the media
    tracks — image_std/image_hd/video/voiceover/tts/stt), derive $/credit
    directly from engine_config. Each track is DEDICATED: no blending,
    no weighted averages across providers. If Pollinations is free and
    Flux-HD costs 6 credits, they appear as two separate rates.

    Once media calls start logging with media.* sources, real_usage
    takes over automatically.
    """
    ec = engine_config or {}
    if cat == "image_std":
        per_credit = (ec.get("image_std_credits", 0) or 0) * real_cpc
        is_free = (ec.get("image_std_credits", 0) or 0) == 0
        return {
            "value":            round(per_credit, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 100.0 if is_free else 0.0,
            "providers":        [("pollinations", 0)],
            "mix_assumption":   "Pollinations (free)" if is_free else "std image provider",
        }
    if cat == "image_hd":
        per_credit = (ec.get("image_hd_credits", 6) or 6) * real_cpc
        return {
            "value":            round(per_credit, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 0.0,
            "providers":        [("fal_flux_hd", 0)],
            "mix_assumption":   "Flux HD (paid)",
        }
    if cat == "video":
        per_sec = (ec.get("video_credits_per_sec", 1) or 1) * real_cpc
        return {
            "value":            round(per_sec, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 0.0,
            "providers":        [("fal_ltx", 0)],
            "mix_assumption":   "1 cr/sec · Fal LTX",
        }
    if cat == "voiceover":
        per_credit = (ec.get("voiceover_credits_per_min", 3) or 3) * real_cpc
        return {
            "value":            round(per_credit, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 0.0,
            "providers":        [("elevenlabs", 0)],
            "mix_assumption":   "ElevenLabs premium (paid)",
        }
    if cat == "tts":
        per_credit = (ec.get("tts_credits_per_min", 0) or 0) * real_cpc
        is_free = (ec.get("tts_credits_per_min", 0) or 0) == 0
        return {
            "value":            round(per_credit, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 100.0 if is_free else 0.0,
            "providers":        [("edge_tts", 0)],
            "mix_assumption":   "Edge TTS (free)" if is_free else "TTS provider",
        }
    if cat == "stt":
        per_credit = (ec.get("stt_credits_per_min", 0) or 0) * real_cpc
        is_free = (ec.get("stt_credits_per_min", 0) or 0) == 0
        return {
            "value":            round(per_credit, 8),
            "source":           "configured",
            "call_count":       0,
            "total_cost_usd":   0.0,
            "free_routing_pct": 100.0 if is_free else 0.0,
            "providers":        [("groq_whisper", 0)],
            "mix_assumption":   "Groq Whisper (free)" if is_free else "STT provider",
        }
    # chat / code — if no logs, return real_cpc as a safe fallback
    return {
        "value":            round(real_cpc, 8),
        "source":           "fallback",
        "call_count":       0,
        "total_cost_usd":   0.0,
        "free_routing_pct": 0.0,
        "providers":        [],
    }


async def blended_by_category() -> dict[str, Any]:
    """Return per-category blended $/credit plus an overall roll-up.

    Shape:
        {
          "chat":    {value, source, call_count, ...},
          "code":    {...},
          "image":   {...},
          "video":   {...},
          "voice":   {...},
          "overall": {...},   # identical to the legacy blended_cost payload
          "generated_at": iso,
        }
    """
    import time, datetime
    now = time.time()
    if _cache["value"] is not None and (now - _cache["ts"]) < _CACHE_TTL:
        return _cache["value"]

    # Engine config + real_cpc drive the estimated fallback for media.
    from services.pricing_math import load_pricing_config, real_cost_per_credit
    pricing_cfg = await load_pricing_config()
    ec = pricing_cfg.get("engine_config") or {}
    real_cpc = await real_cost_per_credit()

    per_cat: dict[str, Any] = {}
    for cat in CATEGORY_KEYS:
        measured = await _category_blended_from_logs(cat)
        if measured:
            per_cat[cat] = measured
        else:
            per_cat[cat] = await _estimated_media_rate(cat, ec, real_cpc)

    # Overall roll-up — legacy single-figure blended (preserves the card
    # on pages that still read blended_cost.get_blended_cost_per_credit).
    from services.costing.blended_cost import get_blended_cost_per_credit
    overall = await get_blended_cost_per_credit()

    result = {
        **per_cat,
        "overall":      overall,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _cache.update({"value": result, "ts": now})
    return result


def invalidate_cache() -> None:
    _cache["value"] = None
    _cache["ts"] = 0.0
