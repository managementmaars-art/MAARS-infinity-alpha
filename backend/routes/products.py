"""Product Catalog routes - Save, manage, and re-generate content for scanned products."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from db import db
from auth import get_current_user, require_admin
from models.schemas import User

router = APIRouter()


class ProductSave(BaseModel):
    name: str
    brand: Optional[str] = ""
    category: Optional[str] = ""
    description: Optional[str] = ""
    images: Optional[List[dict]] = []
    reference_image_path: Optional[str] = None
    specs: Optional[str] = ""
    price_info: Optional[str] = ""
    scan_data: Optional[dict] = {}
    source_chat_id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[str] = None
    price_info: Optional[str] = None


class GenerateRequest(BaseModel):
    content_type: str  # "video", "ad_copy", "social_post", "full_campaign"
    model_provider: Optional[str] = "openai"
    model_name: Optional[str] = "gpt-4o-mini"
    custom_instructions: Optional[str] = ""


@router.post("/products")
async def save_product(data: ProductSave, current_user: User = Depends(get_current_user)):
    product_id = f"prod_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "product_id": product_id,
        "user_id": current_user.user_id,
        "name": data.name,
        "brand": data.brand,
        "category": data.category,
        "description": data.description,
        "images": data.images[:10],
        "reference_image_path": data.reference_image_path,
        "specs": data.specs,
        "price_info": data.price_info,
        "scan_data": data.scan_data,
        "price_history": [],
        "source_chat_id": data.source_chat_id,
        "generated_content": [],
        "created_at": now,
        "updated_at": now,
        "last_scanned": now,
    }
    await db.product_catalog.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/products")
async def list_products(current_user: User = Depends(get_current_user)):
    cursor = db.product_catalog.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1)
    products = await cursor.to_list(100)
    return {"products": products}


@router.get("/products/{product_id}")
async def get_product(product_id: str, current_user: User = Depends(get_current_user)):
    product = await db.product_catalog.find_one(
        {"product_id": product_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}")
async def update_product(product_id: str, data: ProductUpdate, current_user: User = Depends(get_current_user)):
    updates = {k: v for k, v in data.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.product_catalog.update_one(
        {"product_id": product_id, "user_id": current_user.user_id},
        {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    product = await db.product_catalog.find_one({"product_id": product_id}, {"_id": 0})
    return product


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: User = Depends(get_current_user)):
    result = await db.product_catalog.delete_one(
        {"product_id": product_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}


@router.post("/products/{product_id}/rescan")
async def rescan_product(product_id: str, current_user: User = Depends(get_current_user)):
    product = await db.product_catalog.find_one(
        {"product_id": product_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    from services.product_scanner import scan_product
    from pathlib import Path
    UPLOAD_DIR = Path("/app/backend/uploads")
    UPLOAD_DIR.mkdir(exist_ok=True)

    query = f"{product['brand']} {product['name']}".strip() or product['name']
    result = await scan_product(query, UPLOAD_DIR)

    now = datetime.now(timezone.utc).isoformat()
    price_entry = {"date": now, "data": result.get("details", {}).get("snippets", [])[:2]}

    await db.product_catalog.update_one(
        {"product_id": product_id},
        {
            "$set": {
                "scan_data": result,
                "images": result.get("images", [])[:10] or product.get("images", []),
                "reference_image_path": result.get("reference_image_path") or product.get("reference_image_path"),
                "last_scanned": now,
                "updated_at": now,
            },
            "$push": {"price_history": price_entry}
        }
    )
    updated = await db.product_catalog.find_one({"product_id": product_id}, {"_id": 0})
    return updated


@router.post("/products/{product_id}/generate")
async def generate_content(product_id: str, req: GenerateRequest, current_user: User = Depends(get_current_user)):
    product = await db.product_catalog.find_one(
        {"product_id": product_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get API keys
    user_keys = await db.api_keys.find_one({"user_id": current_user.user_id}, {"_id": 0})
    api_keys = user_keys or {}
    universal_key = api_keys.get("universal_key", "")

    from emergentintegrations.llm.chat import LlmChat, UserMessage
    import os
    key = universal_key or api_keys.get(f"{req.model_provider}_key", "") or os.environ.get("LLM_KEY", "")
    if not key:
        raise HTTPException(status_code=400, detail="No API key available. Configure in Settings.")

    product_context = f"""
Product: {product['name']}
Brand: {product.get('brand', 'N/A')}
Category: {product.get('category', 'N/A')}
Description: {product.get('description', 'N/A')}
Specs: {product.get('specs', 'N/A')}
Price Info: {product.get('price_info', 'N/A')}
"""
    scan_ctx = product.get("scan_data", {}).get("context", "")
    if scan_ctx:
        product_context += f"\nDetailed Scan Data:\n{scan_ctx[:2000]}"

    prompts = {
        "video": f"Create a professional Sora 2 video generation prompt for a 15-second commercial showcasing this product. Include cinematic camera movements, dramatic lighting, and emphasize the product's key features. Output ONLY the video prompt.\n\n{product_context}",
        "ad_copy": f"Write 3 professional ad copy variations for this product. Include headline, body copy, and call-to-action for each. Target online advertising (Google Ads, Facebook Ads).\n\n{product_context}",
        "social_post": f"Create 5 social media posts for this product across different platforms (Instagram, Twitter/X, LinkedIn, TikTok caption, Facebook). Include relevant hashtags and emojis. Make them engaging and shareable.\n\n{product_context}",
        "full_campaign": f"Create a complete marketing campaign brief for this product including: 1) Campaign theme & tagline, 2) Target audience, 3) Key messages, 4) 3 ad copy variations, 5) 5 social media posts, 6) Email marketing subject lines, 7) Video concept description.\n\n{product_context}",
    }

    prompt = prompts.get(req.content_type, prompts["ad_copy"])
    if req.custom_instructions:
        prompt += f"\n\nAdditional instructions: {req.custom_instructions}"

    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"gen_{uuid.uuid4().hex[:8]}",
            system_message="You are an elite marketing creative director. Generate premium, commercial-quality content."
        ).with_model(req.model_provider, req.model_name)

        response = await chat.send_message(UserMessage(text=prompt))
        now = datetime.now(timezone.utc).isoformat()

        content_entry = {
            "content_id": f"gen_{uuid.uuid4().hex[:8]}",
            "type": req.content_type,
            "content": response,
            "created_at": now,
        }

        await db.product_catalog.update_one(
            {"product_id": product_id},
            {"$push": {"generated_content": content_entry}}
        )

        return {"content": response, "type": req.content_type, "content_id": content_entry["content_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)[:200]}")


# Admin endpoints
@router.get("/admin/products")
async def admin_list_all_products(admin: User = Depends(require_admin)):
    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "user_id", "as": "user_info"}},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "product_id": 1, "name": 1, "brand": 1, "category": 1,
            "user_id": 1, "user_name": "$user_info.name", "user_email": "$user_info.email",
            "images": {"$slice": ["$images", 1]},
            "created_at": 1, "last_scanned": 1,
            "generated_count": {"$size": {"$ifNull": ["$generated_content", []]}},
        }},
        {"$sort": {"created_at": -1}},
        {"$limit": 200},
    ]
    products = await db.product_catalog.aggregate(pipeline).to_list(200)
    return {"products": products}
