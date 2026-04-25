"""Blog posts — foundation for content marketing.

Schema mirrors `changelog_entries`: slug, title, summary, body, author,
tag, published, published_at, cover_image, reading_minutes.

Everything public unauthenticated. Admin can draft via
/admin/blog endpoints (covered separately).
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/blog")
async def list_posts(
    tag: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    from db import db
    q: dict = {"published": True}
    if tag:
        q["tags"] = tag
    docs = await db.blog_posts.find(
        q, {"_id": 0, "body": 0}   # omit full body in list view
    ).sort("published_at", -1).skip(offset).limit(limit).to_list(limit)
    total = await db.blog_posts.count_documents(q)
    return {"object": "list", "data": docs, "total": total, "offset": offset}


@router.get("/blog/{slug}")
async def get_post(slug: str):
    from db import db
    doc = await db.blog_posts.find_one({"slug": slug, "published": True}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "post not found")
    return doc
