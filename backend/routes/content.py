"""Content Generator — Style Blueprint-driven content creation.

Uses Reference Intelligence Style Blueprints to generate on-brand content
matching a reference's tone, structure, and aesthetic.
"""
import os
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Depends
from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

CONTENT_TYPES = [
    {"id": "marketing_copy", "label": "Marketing Copy", "description": "Landing pages, product descriptions, value props"},
    {"id": "social_post", "label": "Social Media Post", "description": "LinkedIn, Twitter/X, Instagram captions"},
    {"id": "email_campaign", "label": "Email Campaign", "description": "Newsletters, drip campaigns, announcements"},
    {"id": "blog_article", "label": "Blog Article", "description": "Thought leadership, tutorials, company news"},
    {"id": "ad_copy", "label": "Ad Copy", "description": "Google Ads, Meta Ads, display banners"},
    {"id": "press_release", "label": "Press Release", "description": "Company announcements, product launches"},
    {"id": "brand_guidelines", "label": "Brand Guidelines", "description": "Voice & tone docs, style guides"},
    {"id": "custom", "label": "Custom", "description": "Describe exactly what you need"},
]


async def _get_user_llm_config(user_id: str):
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )
    if config:
        return config.get("provider", "openai"), config.get("model", "gpt-5.2")
    return "openai", "gpt-5.2"


@router.get("/content/types")
async def get_content_types(current_user: User = Depends(get_current_user)):
    """List available content types for generation."""
    return {"types": CONTENT_TYPES}


@router.post("/content/generate")
async def generate_content(request: Request, current_user: User = Depends(get_current_user)):
    """Generate content using a Style Blueprint from Reference Intelligence."""
    data = await request.json()
    blueprint_id = data.get("blueprint_id", "")
    content_type = data.get("content_type", "custom")
    prompt = data.get("prompt", "")
    tone_override = data.get("tone_override", "")
    length = data.get("length", "medium")  # short, medium, long

    if not prompt:
        raise HTTPException(400, "Provide a content prompt")

    # Fetch the style blueprint if provided
    blueprint_context = ""
    blueprint_source = ""
    if blueprint_id:
        ref = await db.reference_analyses.find_one(
            {"ref_id": blueprint_id, "user_id": current_user.user_id}, {"_id": 0}
        )
        if ref:
            analysis = ref.get("analysis", "")
            blueprint_context = f"""
STYLE BLUEPRINT (extracted from reference):
{analysis[:2500]}

SOURCE: {ref.get('source', '')[:200]}
TYPE: {ref.get('type', 'text')}
"""
            blueprint_source = ref.get("source", "")[:100]

    # Content type guidance
    type_guidance = {
        "marketing_copy": "Write compelling marketing copy. Focus on benefits, use power words, include a clear CTA.",
        "social_post": "Write engaging social media content. Use hooks, be conversational, add relevant hashtags.",
        "email_campaign": "Write a professional email with a clear subject line, engaging opener, body, and CTA.",
        "blog_article": "Write a well-structured blog article with intro, sections, insights, and conclusion.",
        "ad_copy": "Write concise, high-converting ad copy. Focus on value proposition and urgency.",
        "press_release": "Write in standard press release format: headline, dateline, lead, body, boilerplate.",
        "brand_guidelines": "Create brand voice and tone guidelines with examples and do's/don'ts.",
        "custom": "Follow the user's specific instructions precisely.",
    }

    length_guidance = {
        "short": "Keep it concise. 100-200 words.",
        "medium": "Moderate length. 300-500 words.",
        "long": "Comprehensive and detailed. 800-1500 words.",
    }

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        provider, model = await _get_user_llm_config(current_user.user_id)

        system_msg = f"""You are a world-class content creator and brand strategist. Generate high-quality, on-brand content.

{blueprint_context}

CONTENT TYPE: {content_type}
GUIDANCE: {type_guidance.get(content_type, type_guidance['custom'])}
LENGTH: {length_guidance.get(length, length_guidance['medium'])}
{f'TONE OVERRIDE: {tone_override}' if tone_override else ''}

RULES:
1. If a Style Blueprint is provided, match its tone, voice, and style elements EXACTLY
2. Generate original content — never copy the reference verbatim
3. Be creative, compelling, and professional
4. Format appropriately for the content type
5. Include concrete details and actionable elements"""

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"content_gen_{uuid.uuid4().hex[:8]}",
            system_message=system_msg
        ).with_model(provider, model)

        generated = await chat.send_message(UserMessage(text=prompt))

        result = {
            "content_id": f"cnt_{uuid.uuid4().hex[:10]}",
            "user_id": current_user.user_id,
            "content_type": content_type,
            "prompt": prompt[:500],
            "blueprint_id": blueprint_id,
            "blueprint_source": blueprint_source,
            "content": generated,
            "model_used": f"{provider}/{model}",
            "length": length,
            "tone_override": tone_override,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.generated_content.insert_one(result)
        result.pop("_id", None)
        return result

    except Exception as e:
        raise HTTPException(500, f"Content generation failed: {str(e)[:200]}")


@router.get("/content/history")
async def get_content_history(current_user: User = Depends(get_current_user)):
    """Get all previously generated content."""
    items = await db.generated_content.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    return {"items": items}


@router.delete("/content/{content_id}")
async def delete_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Delete a generated content item."""
    result = await db.generated_content.delete_one(
        {"content_id": content_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(404, "Content not found")
    return {"success": True}
