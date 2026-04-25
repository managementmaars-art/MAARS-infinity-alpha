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
async def list_products(page: int = 1, limit: int = 50, current_user: User = Depends(get_current_user)):
    skip = (page - 1) * limit
    total = await db.product_catalog.count_documents({"user_id": current_user.user_id})
    cursor = db.product_catalog.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip)
    products = await cursor.to_list(limit)
    return {"products": products, "total": total, "page": page, "pages": max(1, -(-total // limit))}


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

    from services.llm_gateway import complete_text

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
        response = await complete_text(
            user_id=current_user.user_id,
            system_prompt="You are an elite marketing creative director. Generate premium, commercial-quality content.",
            user_prompt=prompt,
            model=f"{req.model_provider}/{req.model_name}" if req.model_provider and req.model_name else "maars/auto",
            source="products.generate",
        )
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


# ============== BATCH IMPORT ==============

import asyncio
import io
import csv
import logging
from fastapi import UploadFile, File

logger = logging.getLogger(__name__)


@router.post("/products/batch-import")
async def batch_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload CSV/XLSX with products to batch-scan and import."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

    content = await file.read()
    rows = []

    try:
        if ext == "csv":
            text = content.decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                name = row.get("name", row.get("Name", row.get("product", row.get("Product", "")))).strip()
                if name:
                    rows.append({
                        "name": name,
                        "brand": row.get("brand", row.get("Brand", "")).strip(),
                        "category": row.get("category", row.get("Category", "")).strip(),
                    })
        else:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
            ws = wb.active
            headers = []
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                if i == 0:
                    headers = [str(c).strip().lower() if c else "" for c in row]
                    continue
                row_dict = dict(zip(headers, row))
                name = str(row_dict.get("name", row_dict.get("product", "")) or "").strip()
                if name:
                    rows.append({
                        "name": name,
                        "brand": str(row_dict.get("brand", "") or "").strip(),
                        "category": str(row_dict.get("category", "") or "").strip(),
                    })
            wb.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)[:200]}")

    if not rows:
        raise HTTPException(status_code=400, detail="No valid product rows found. Ensure columns: name, brand, category")

    if len(rows) > 50:
        rows = rows[:50]

    batch_id = f"batch_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    items = []
    for i, row in enumerate(rows):
        items.append({
            "index": i,
            "name": row["name"],
            "brand": row.get("brand", ""),
            "category": row.get("category", ""),
            "status": "pending",
            "product_id": None,
            "error": None,
        })

    batch_doc = {
        "batch_id": batch_id,
        "user_id": current_user.user_id,
        "filename": file.filename,
        "total": len(items),
        "completed": 0,
        "failed": 0,
        "status": "processing",
        "items": items,
        "created_at": now,
        "updated_at": now,
    }
    await db.batch_imports.insert_one(batch_doc)

    asyncio.create_task(_process_batch(batch_id, current_user.user_id, items))

    return {"batch_id": batch_id, "total": len(items), "status": "processing"}


@router.get("/products/batch/{batch_id}")
async def get_batch_status(batch_id: str, current_user: User = Depends(get_current_user)):
    batch = await db.batch_imports.find_one(
        {"batch_id": batch_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/products/batches")
async def list_batches(current_user: User = Depends(get_current_user)):
    cursor = db.batch_imports.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "items": 0}
    ).sort("created_at", -1).limit(20)
    batches = await cursor.to_list(20)
    return {"batches": batches}


async def _process_batch(batch_id: str, user_id: str, items: list):
    """Background task: scan each product and save to catalog."""
    from services.product_scanner import scan_product_light

    completed = 0
    failed = 0

    for item in items:
        idx = item["index"]
        query = f"{item['brand']} {item['name']}".strip() or item["name"]

        try:
            await db.batch_imports.update_one(
                {"batch_id": batch_id, "items.index": idx},
                {"$set": {"items.$.status": "scanning", "updated_at": datetime.now(timezone.utc).isoformat()}}
            )

            result = await scan_product_light(query)

            product_id = f"prod_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()
            product_doc = {
                "product_id": product_id,
                "user_id": user_id,
                "name": item["name"],
                "brand": item.get("brand", ""),
                "category": item.get("category", ""),
                "description": "",
                "images": result.get("images", [])[:10],
                "reference_image_path": result.get("reference_image_path"),
                "specs": "\n".join(result.get("details", {}).get("snippets", [])[:3]),
                "price_info": "",
                "scan_data": result,
                "price_history": [],
                "generated_content": [],
                "source_chat_id": None,
                "created_at": now,
                "updated_at": now,
                "last_scanned": now,
            }
            await db.product_catalog.insert_one(product_doc)

            await db.batch_imports.update_one(
                {"batch_id": batch_id, "items.index": idx},
                {"$set": {
                    "items.$.status": "done",
                    "items.$.product_id": product_id,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            completed += 1
            logger.info(f"Batch {batch_id}: scanned {item['name']} -> {product_id}")

        except Exception as e:
            logger.error(f"Batch {batch_id}: failed {item['name']}: {e}")
            await db.batch_imports.update_one(
                {"batch_id": batch_id, "items.index": idx},
                {"$set": {
                    "items.$.status": "failed",
                    "items.$.error": str(e)[:200],
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            failed += 1

        await db.batch_imports.update_one(
            {"batch_id": batch_id},
            {"$set": {"completed": completed, "failed": failed}}
        )

        await asyncio.sleep(1)

    await db.batch_imports.update_one(
        {"batch_id": batch_id},
        {"$set": {
            "status": "complete",
            "completed": completed,
            "failed": failed,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    logger.info(f"Batch {batch_id} complete: {completed} done, {failed} failed")
