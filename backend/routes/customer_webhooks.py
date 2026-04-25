"""Customer webhook subscription CRUD."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from auth import get_current_user
from models.schemas import User
from services import customer_webhooks

router = APIRouter()


class SubscribeRequest(BaseModel):
    url: str          # accept str for pydantic-v1 compatibility; service validates
    events: list[str]
    secret: str | None = None
    description: str | None = None


@router.post("/webhooks")
async def create_subscription(
    body: SubscribeRequest,
    current_user: User = Depends(get_current_user),
):
    """Register a webhook endpoint. Returns the subscription with the
    secret — save this; you cannot retrieve it later (like every other
    SaaS webhook system)."""
    result = await customer_webhooks.subscribe(
        user_id=current_user.user_id,
        url=body.url,
        events=body.events,
        secret=body.secret,
        description=body.description,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error"))
    return result


@router.get("/webhooks")
async def list_subs(current_user: User = Depends(get_current_user)):
    data = await customer_webhooks.list_subscriptions(current_user.user_id)
    return {"object": "list", "data": data, "count": len(data)}


@router.delete("/webhooks/{subscription_id}")
async def delete_sub(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
):
    return await customer_webhooks.delete_subscription(subscription_id, current_user.user_id)


@router.get("/webhooks/events")
async def list_events(_: User = Depends(get_current_user)):
    """Enumerate all event types customers can subscribe to."""
    return {
        "object": "list",
        "events": sorted(list(customer_webhooks.VALID_EVENTS)),
    }
