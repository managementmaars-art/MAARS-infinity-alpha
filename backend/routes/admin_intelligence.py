"""
Provider Intelligence — live API data for the operator dashboard.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from auth import require_admin
from models.schemas import User

router = APIRouter()


@router.get("/admin/intelligence/providers")
async def all_provider_intel(_: User = Depends(require_admin)):
    """Full intelligence for every configured provider — models, balance, tier."""
    from services import provider_intelligence
    data = await provider_intelligence.fetch_all_intel()
    keyed = [p for p in data if p.get("has_key")]
    return {
        "object": "provider_intelligence",
        "total": len(data),
        "configured": len(keyed),
        "total_models": sum(p.get("model_count", 0) for p in keyed),
        "providers": data,
    }


@router.get("/admin/intelligence/provider/{slug}")
async def single_provider_intel(
    slug: str,
    _: User = Depends(require_admin),
):
    """Detailed intelligence for a single provider."""
    from services import provider_intelligence
    from services.provider_catalog import get
    import os
    from shared.utils import get_api_keys

    provider = get(slug)
    if not provider:
        return {"error": f"Unknown provider: {slug}"}

    api_keys = await get_api_keys()
    key = api_keys.get(slug, "") or os.environ.get(provider.env_var, "")

    intel = await provider_intelligence.fetch_intel(slug, key)
    intel["display_name"] = provider.display_name
    intel["dashboard_url"] = provider.dashboard_url
    intel["category"] = provider.category
    intel["has_key"] = bool(key)
    return intel


@router.post("/admin/intelligence/refresh")
async def refresh_intel(_: User = Depends(require_admin)):
    """Force refresh all provider intelligence (clears cache)."""
    from services import provider_intelligence
    provider_intelligence.clear_cache()
    data = await provider_intelligence.fetch_all_intel()
    keyed = [p for p in data if p.get("has_key")]
    return {
        "status": "refreshed",
        "configured": len(keyed),
        "total_models": sum(p.get("model_count", 0) for p in keyed),
        "providers": data,
    }


@router.get("/admin/intelligence/recommendations")
async def package_recommendations(_: User = Depends(require_admin)):
    """Package recommendations based on current provider capacity."""
    from services import provider_intelligence
    return await provider_intelligence.get_package_recommendations()
