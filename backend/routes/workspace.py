"""Workspace Brain / Business Profile endpoints."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Body

from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

DEFAULT_WORKSPACE = {
    "company_name": "",
    "industry": "",
    "brand_voice": "",
    "products_services": "",
    "target_audience": "",
    "competitors": "",
    "pricing_info": "",
    "unique_value_prop": "",
    "regions": "",
    "policies": "",
    "website": "",
    "timezone": "UTC",
    "working_hours": "9:00-17:00",
    "writing_style": "professional",
    "approval_rules": "require_approval",
    "custom_instructions": "",
}


@router.get("/workspace/profile")
async def get_workspace_profile(current_user: User = Depends(get_current_user)):
    """Get the user's workspace/business profile."""
    profile = await db.workspace_profiles.find_one(
        {"user_id": current_user.user_id}, {"_id": 0}
    )
    if not profile:
        return {**DEFAULT_WORKSPACE, "user_id": current_user.user_id}
    return profile


@router.put("/workspace/profile")
async def update_workspace_profile(
    body: dict = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Create or update the workspace/business profile."""
    allowed_fields = set(DEFAULT_WORKSPACE.keys())
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    updates["user_id"] = current_user.user_id
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.workspace_profiles.update_one(
        {"user_id": current_user.user_id},
        {"$set": updates, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )

    return {"success": True}


@router.delete("/workspace/profile")
async def delete_workspace_profile(current_user: User = Depends(get_current_user)):
    """Delete the workspace profile (memory boundary: user-controlled deletion)."""
    await db.workspace_profiles.delete_one({"user_id": current_user.user_id})
    return {"success": True}


async def get_workspace_context(user_id: str) -> str:
    """Build workspace context string for agent prompt injection."""
    profile = await db.workspace_profiles.find_one(
        {"user_id": user_id}, {"_id": 0}
    )
    if not profile:
        return ""

    parts = []
    if profile.get("company_name"):
        parts.append(f"Company: {profile['company_name']}")
    if profile.get("industry"):
        parts.append(f"Industry: {profile['industry']}")
    if profile.get("brand_voice"):
        parts.append(f"Brand Voice & Tone: {profile['brand_voice']}")
    if profile.get("products_services"):
        parts.append(f"Products/Services: {profile['products_services']}")
    if profile.get("target_audience"):
        parts.append(f"Target Audience: {profile['target_audience']}")
    if profile.get("competitors"):
        parts.append(f"Key Competitors: {profile['competitors']}")
    if profile.get("pricing_info"):
        parts.append(f"Pricing: {profile['pricing_info']}")
    if profile.get("unique_value_prop"):
        parts.append(f"Unique Value Proposition: {profile['unique_value_prop']}")
    if profile.get("regions"):
        parts.append(f"Markets/Regions: {profile['regions']}")
    if profile.get("policies"):
        parts.append(f"Key Policies: {profile['policies']}")
    if profile.get("website"):
        parts.append(f"Website: {profile['website']}")
    if profile.get("writing_style"):
        parts.append(f"Preferred Writing Style: {profile['writing_style']}")
    if profile.get("custom_instructions"):
        parts.append(f"Custom Instructions: {profile['custom_instructions']}")

    if not parts:
        return ""

    return (
        "\n\n--- WORKSPACE BRAIN (Business Profile) ---\n"
        + "\n".join(parts)
        + "\n--- END WORKSPACE BRAIN ---\n"
        + "You MUST use this business context in every response. Match the brand voice, "
        + "reference products/services when relevant, and tailor advice to the target audience and industry.\n"
    )


@router.get("/workspace/tool-logs")
async def get_tool_logs(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Get recent tool call logs for observability."""
    logs = await db.tool_logs.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    total = await db.tool_logs.count_documents({"user_id": current_user.user_id})
    return {"logs": logs, "total": total}
