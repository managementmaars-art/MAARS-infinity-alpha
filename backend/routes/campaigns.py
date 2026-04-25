"""Campaign API — the operator/user interface for outbound orchestration."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


class RunCampaignRequest(BaseModel):
    name: str
    persona: dict
    subject_template: str
    email_template: str
    lead_count: int = 25
    send_window_days: int = 5
    daily_send_cap: int = 30
    from_name: str | None = None
    reply_to: str | None = None


@router.post("/campaigns/run")
async def run_campaign_endpoint(
    body: RunCampaignRequest,
    current_user: User = Depends(get_current_user),
):
    """Start a new outbound campaign. Returns campaign_id immediately
    and schedules sends; the background poller fires them."""
    from services import campaign_orchestrator
    result = await campaign_orchestrator.run_campaign(
        user_id=current_user.user_id,
        **body.model_dump(),
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "Campaign launch failed"))
    return result


@router.get("/campaigns/{campaign_id}")
async def get_campaign_endpoint(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
):
    """Campaign progress + per-email status list."""
    from services import campaign_orchestrator
    result = await campaign_orchestrator.get_campaign(campaign_id)
    if not result.get("ok"):
        raise HTTPException(404, "Campaign not found")
    return result


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign_endpoint(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
):
    from services import campaign_orchestrator
    return await campaign_orchestrator.pause_campaign(campaign_id)


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign_endpoint(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
):
    from services import campaign_orchestrator
    return await campaign_orchestrator.resume_campaign(campaign_id)


@router.get("/campaigns")
async def list_campaigns(current_user: User = Depends(get_current_user)):
    """List all campaigns owned by the current user."""
    from db import db
    docs = await db.outbound_campaigns.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "email_template": 0},  # exclude big text
    ).sort("created_at", -1).to_list(100)
    return {"object": "list", "data": docs, "count": len(docs)}
