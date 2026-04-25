"""Outcomes — client-facing dashboard endpoints.

Unlike /admin/gateway/intel (operator internals), these endpoints are
for the paying client. They surface results, not machinery:

  GET /api/outcomes            — single call, full dashboard payload
  GET /api/outcomes/pipeline   — lead → email → reply → meeting
  GET /api/outcomes/content    — posts, images, videos
  GET /api/outcomes/campaigns  — running + paused + completed
  GET /api/outcomes/workflows  — active workflows + run success rate
  GET /api/outcomes/team       — agents configured + working now
  GET /api/outcomes/usage      — plan consumption (percent, not credits)
  GET /api/outcomes/activity   — recent done-things stream
  GET /api/outcomes/capacity   — what this plan can DO (capacity language)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends

from auth import get_current_user
from models.schemas import User

router = APIRouter()


@router.get("/outcomes")
async def outcomes_overview(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import overview
    return await overview(current_user.user_id)


@router.get("/outcomes/pipeline")
async def outcomes_pipeline(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import pipeline_block
    return await pipeline_block(current_user.user_id)


@router.get("/outcomes/content")
async def outcomes_content(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import content_block
    return await content_block(current_user.user_id)


@router.get("/outcomes/campaigns")
async def outcomes_campaigns(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import campaigns_block
    return await campaigns_block(current_user.user_id)


@router.get("/outcomes/workflows")
async def outcomes_workflows(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import workflows_block
    return await workflows_block(current_user.user_id)


@router.get("/outcomes/team")
async def outcomes_team(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import team_block
    return await team_block(current_user.user_id)


@router.get("/outcomes/usage")
async def outcomes_usage(current_user: User = Depends(get_current_user)):
    from services.outcomes_service import usage_block
    return await usage_block(current_user.user_id)


@router.get("/outcomes/activity")
async def outcomes_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    from services.outcomes_service import recent_activity
    return {"object": "list", "data": await recent_activity(current_user.user_id, limit=limit)}


@router.get("/outcomes/capacity")
async def outcomes_capacity(current_user: User = Depends(get_current_user)):
    """Client's plan capacity in buyer language ("up to 1,500 AI
    messages / month"), not credits."""
    from db import db
    from services.plan_capacity import plan_capacity
    sub = await db.subscriptions.find_one(
        {"user_id": current_user.user_id},
        {"plan_id": 1, "_id": 0},
    )
    plan_id = (sub or {}).get("plan_id") or "free"
    return await plan_capacity(plan_id)
