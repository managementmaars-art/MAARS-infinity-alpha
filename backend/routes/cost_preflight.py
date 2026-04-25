"""Pre-flight cost estimates — answers 'how many credits will this cost?'
BEFORE the user commits.

Customer-facing UX: before submitting a prompt or running a campaign,
show "≈ 12 credits" so there's no surprise. Massively reduces the
churn spike that comes from "my credits disappeared and I don't know why".

Estimates are conservative (round up) so we never undercharge later.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


class ChatEstimate(BaseModel):
    prompt: str
    max_tokens: int = 600
    quality: str = "standard"   # draft | standard | premium


class ImageEstimate(BaseModel):
    prompt: str
    quality: str = "standard"


class VideoEstimate(BaseModel):
    prompt: str
    duration: int = 4


class CampaignEstimate(BaseModel):
    lead_count: int = 25


class TtsEstimate(BaseModel):
    text: str
    tier: str = "standard"


@router.post("/estimate/chat")
async def estimate_chat(body: ChatEstimate, _: User = Depends(get_current_user)):
    """Rough token-count heuristic × tokens_per_credit from config.
    Conservative — adds +15% safety margin."""
    from services.pricing_math import load_pricing_config
    pc = await load_pricing_config()
    tpc = pc["engine_config"].get("tokens_per_credit", 1000)
    # Token estimate: ~4 chars/token input + max_tokens output.
    est_tokens = int(len(body.prompt) / 4) + int(body.max_tokens)
    raw_credits = est_tokens / tpc
    credits = max(1, int(raw_credits * 1.15) + 1)
    return {"credits": credits, "confidence": "estimate"}


@router.post("/estimate/image")
async def estimate_image(body: ImageEstimate, _: User = Depends(get_current_user)):
    from services.pricing_math import load_pricing_config
    pc = await load_pricing_config()
    ec = pc["engine_config"]
    if body.quality == "premium":
        credits = ec.get("image_hd_credits", 40)
    else:
        credits = ec.get("image_std_credits", 20)
    return {"credits": credits, "confidence": "exact"}


@router.post("/estimate/video")
async def estimate_video(body: VideoEstimate, _: User = Depends(get_current_user)):
    from services.pricing_math import load_pricing_config
    pc = await load_pricing_config()
    ec = pc["engine_config"]
    credits = int(body.duration * ec.get("video_credits_per_sec", 100))
    return {"credits": credits, "confidence": "exact"}


@router.post("/estimate/tts")
async def estimate_tts(body: TtsEstimate, _: User = Depends(get_current_user)):
    from services.pricing_math import load_pricing_config
    pc = await load_pricing_config()
    ec = pc["engine_config"]
    # ~150 words/min ≈ 750 chars/min of typical prose
    minutes = max(1, len(body.text) / 750)
    rate_key = "voiceover_credits_per_min" if body.tier == "premium" else "tts_credits_per_min"
    credits = max(1, int(minutes * ec.get(rate_key, 15)) + 1)
    return {"credits": credits, "confidence": "estimate"}


@router.post("/estimate/campaign")
async def estimate_campaign(body: CampaignEstimate, _: User = Depends(get_current_user)):
    """A campaign spends credits on 3 things:
      - Lead search (≈ 1 credit per lead on Apollo, batched)
      - Draft personalization (≈ 1 credit per lead via free-tier LLM)
      - Send transport (zero credits — email provider is paid subscription, not credits)
    """
    per_lead = 2   # search + draft
    credits = max(5, body.lead_count * per_lead)
    return {"credits": credits, "confidence": "estimate",
            "breakdown": {
                "lead_search": body.lead_count * 1,
                "personalization": body.lead_count * 1,
                "send": 0,
            }}
