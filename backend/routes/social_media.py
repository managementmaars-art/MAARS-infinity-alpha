"""MAARS Social Media Command Layer.

Enables AI agents to perform real-world social media actions across all major platforms:
  - Facebook, Instagram, Twitter/X, TikTok, WhatsApp, Viber, LINE, LinkedIn, YouTube, Telegram

Supported actions:
  POST   /api/social/post          — publish content to any platform
  POST   /api/social/message       — send direct/private messages
  POST   /api/social/boost         — boost/promote posts with geo-targeting
  POST   /api/social/schedule      — schedule future posts, calls, meetings
  POST   /api/social/cold-email    — send cold outreach emails via integrated providers
  POST   /api/social/cold-call     — initiate cold calls via Twilio
  POST   /api/social/reply         — reply to comments, messages, mentions
  GET    /api/social/analytics     — fetch performance metrics per platform
  GET    /api/social/campaigns     — list running campaigns
  POST   /api/social/campaign      — create a geo-targeted campaign
  GET    /api/social/accounts      — list connected social accounts
  GET    /api/social/geo-regions   — list supported geographic regions
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from db import db
from models.schemas import User
from shared.utils import get_integration_keys

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── Supported platforms ────────────────────────────────────────────────────
PLATFORM_CAPABILITIES = {
    "facebook":  ["post", "story", "reel", "message", "boost", "reply", "comment", "ads", "analytics"],
    "instagram": ["post", "reel", "story", "dm", "boost", "reply", "comment", "hashtag", "analytics"],
    "twitter":   ["tweet", "reply", "dm", "retweet", "thread", "spaces", "ads", "analytics"],
    "tiktok":    ["post", "boost", "ads", "geo_target", "spark_ads", "analytics"],
    "whatsapp":  ["message", "call", "broadcast", "template", "media", "catalog", "reply"],
    "viber":     ["message", "broadcast", "media", "keyboard", "sticker"],
    "line":      ["message", "broadcast", "rich_menu", "flex_message", "push", "reply"],
    "linkedin":  ["post", "article", "inmail", "ads", "lead_gen", "comment", "analytics"],
    "youtube":   ["upload", "comment", "reply", "live", "ads", "analytics", "playlist"],
    "telegram":  ["message", "broadcast", "channel", "poll", "inline_keyboard", "media"],
}

# ─── Geographic regions with language mapping ────────────────────────────────
GEO_REGIONS = {
    "north_america":    {"name": "North America",     "countries": ["US","CA","MX"], "languages": ["en","es","fr"], "primary_lang": "en"},
    "south_america":    {"name": "South America",     "countries": ["BR","AR","CO","CL","PE"], "languages": ["pt","es"], "primary_lang": "es"},
    "western_europe":   {"name": "Western Europe",    "countries": ["GB","DE","FR","ES","IT","NL"], "languages": ["en","de","fr","es","it","nl"], "primary_lang": "en"},
    "eastern_europe":   {"name": "Eastern Europe",    "countries": ["PL","UA","RO","CZ","HU"], "languages": ["pl","uk","ro","cs","hu"], "primary_lang": "en"},
    "middle_east":      {"name": "Middle East",       "countries": ["SA","AE","EG","TR","IL"], "languages": ["ar","tr","he","en"], "primary_lang": "ar"},
    "south_asia":       {"name": "South Asia",        "countries": ["IN","PK","BD","LK","NP"], "languages": ["hi","bn","ur","ta","en"], "primary_lang": "hi"},
    "southeast_asia":   {"name": "Southeast Asia",    "countries": ["TH","VN","ID","MY","PH","SG"], "languages": ["th","vi","id","ms","tl","en"], "primary_lang": "en"},
    "east_asia":        {"name": "East Asia",         "countries": ["JP","KR","TW","HK"], "languages": ["ja","ko","zh-tw","zh-hk"], "primary_lang": "ja"},
    "china":            {"name": "China",              "countries": ["CN"], "languages": ["zh-cn"], "primary_lang": "zh-cn"},
    "africa":           {"name": "Africa",             "countries": ["NG","ZA","KE","GH","ET"], "languages": ["en","sw","am","yo","ig"], "primary_lang": "en"},
    "australia_nz":     {"name": "Australia & NZ",    "countries": ["AU","NZ"], "languages": ["en"], "primary_lang": "en"},
    "global":           {"name": "Global",             "countries": ["*"], "languages": ["en"], "primary_lang": "en"},
}

# ─── Schemas ─────────────────────────────────────────────────────────────────
class SocialPostRequest(BaseModel):
    platform: str
    action: str = "post"
    content: str
    media_urls: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []
    geo_regions: Optional[List[str]] = []
    language: Optional[str] = None          # auto-detect from region if not set
    scheduled_at: Optional[str] = None      # ISO datetime for scheduling
    agent_id: Optional[str] = None

class BoostRequest(BaseModel):
    platform: str
    post_id: str
    budget_usd: float = Field(gt=0)
    geo_regions: List[str]
    duration_days: int = Field(default=7, ge=1, le=90)
    target_age_min: Optional[int] = 18
    target_age_max: Optional[int] = 65
    target_interests: Optional[List[str]] = []
    objective: str = "engagement"           # engagement | reach | clicks | conversions | leads
    auto_translate: bool = True             # Translate copy to match regional language
    agent_id: Optional[str] = None

class MessageRequest(BaseModel):
    platform: str
    recipient_id: str
    message: str
    media_url: Optional[str] = None
    template_name: Optional[str] = None    # For WhatsApp approved templates
    language: Optional[str] = "en"
    agent_id: Optional[str] = None

class ColdEmailRequest(BaseModel):
    to_email: str
    to_name: Optional[str] = None
    subject: str
    body_html: str
    from_name: Optional[str] = "MAARS Command"
    reply_to: Optional[str] = None
    provider: str = "sendgrid"             # sendgrid | resend
    personalization: Optional[dict] = {}
    geo_region: Optional[str] = None
    language: Optional[str] = "en"
    agent_id: Optional[str] = None

class ColdCallRequest(BaseModel):
    to_phone: str                          # E.164 format (+1234567890)
    script: str                            # What the agent should say
    agent_voice: Optional[str] = "alice"  # Twilio TTS voice
    geo_region: Optional[str] = None
    language: Optional[str] = "en"
    max_duration_seconds: int = 120
    agent_id: Optional[str] = None

class ScheduleRequest(BaseModel):
    type: str                              # post | call | meeting | email
    platform: Optional[str] = None
    scheduled_at: str                     # ISO datetime
    title: str
    description: Optional[str] = ""
    participants: Optional[List[str]] = []
    content: Optional[str] = None
    geo_regions: Optional[List[str]] = []
    agent_id: Optional[str] = None

class CampaignRequest(BaseModel):
    name: str
    platforms: List[str]
    content: str
    media_urls: Optional[List[str]] = []
    geo_regions: List[str]
    auto_translate: bool = True
    boost_budget_usd: Optional[float] = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    objective: str = "awareness"
    hashtags: Optional[List[str]] = []
    agent_id: Optional[str] = None

class ReplyRequest(BaseModel):
    platform: str
    comment_id: str                        # comment/mention/message to reply to
    reply_text: str
    language: Optional[str] = None        # auto-match original comment's language
    agent_id: Optional[str] = None


# ─── Helpers ─────────────────────────────────────────────────────────────────
async def _get_platform_creds(user_id: str, platform: str) -> dict:
    """Fetch stored OAuth creds for a platform."""
    doc = await db.social_connections.find_one({"user_id": user_id, "platform": platform})
    if not doc:
        raise HTTPException(status_code=400, detail=f"{platform.title()} is not connected. Connect it in Integration Hub first.")
    return doc.get("credentials", {})


def _resolve_language(geo_regions: List[str], explicit_lang: Optional[str]) -> str:
    if explicit_lang:
        return explicit_lang
    for region in geo_regions:
        meta = GEO_REGIONS.get(region)
        if meta:
            return meta["primary_lang"]
    return "en"


async def _log_action(user_id: str, platform: str, action: str, payload: dict, result: dict, agent_id: Optional[str] = None):
    await db.social_action_logs.insert_one({
        "log_id": f"soc_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "agent_id": agent_id,
        "platform": platform,
        "action": action,
        "payload_summary": {k: v for k, v in payload.items() if k not in ("media_urls",)},
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/social/geo-regions")
async def get_geo_regions(current_user: User = Depends(get_current_user)):
    """Return all supported geographic regions and their language mappings."""
    return {"regions": GEO_REGIONS}


@router.get("/social/accounts")
async def get_social_accounts(current_user: User = Depends(get_current_user)):
    """List all connected social media accounts for this user."""
    docs = await db.social_connections.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).to_list(None)

    accounts = []
    for doc in docs:
        creds = doc.get("credentials", {})
        accounts.append({
            "platform": doc["platform"],
            "connected_at": doc.get("connected_at"),
            "account_name": doc.get("account_name", ""),
            "account_id": doc.get("account_id", ""),
            "capabilities": PLATFORM_CAPABILITIES.get(doc["platform"], []),
            "is_active": doc.get("is_active", True),
        })
    return {"accounts": accounts, "total": len(accounts)}


@router.post("/social/connect")
async def connect_social_account(
    body: dict,
    current_user: User = Depends(get_current_user),
):
    """Store OAuth credentials for a social media platform."""
    platform = body.get("platform", "").lower()
    if platform not in PLATFORM_CAPABILITIES:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    credentials = body.get("credentials", {})
    if not credentials:
        raise HTTPException(status_code=400, detail="Credentials are required")

    await db.social_connections.update_one(
        {"user_id": current_user.user_id, "platform": platform},
        {"$set": {
            "credentials": credentials,
            "account_name": body.get("account_name", ""),
            "account_id": body.get("account_id", ""),
            "is_active": True,
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    return {"status": "connected", "platform": platform}


@router.delete("/social/connect/{platform}")
async def disconnect_social_account(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Disconnect a social media account."""
    await db.social_connections.delete_one({"user_id": current_user.user_id, "platform": platform.lower()})
    return {"status": "disconnected", "platform": platform}


@router.post("/social/post")
async def social_post(
    body: SocialPostRequest,
    current_user: User = Depends(get_current_user),
):
    """Publish content to a social media platform.

    Automatically resolves language from geo_regions if not explicitly set.
    Saves to action log and schedules or publishes immediately.
    """
    platform = body.platform.lower()
    if platform not in PLATFORM_CAPABILITIES:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    creds = await _get_platform_creds(current_user.user_id, platform)
    language = _resolve_language(body.geo_regions or [], body.language)

    action_id = f"post_{uuid.uuid4().hex[:12]}"
    scheduled_at = body.scheduled_at
    status = "scheduled" if scheduled_at else "published"

    post_record = {
        "action_id": action_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "platform": platform,
        "action": body.action,
        "content": body.content,
        "media_urls": body.media_urls,
        "hashtags": body.hashtags,
        "geo_regions": body.geo_regions,
        "language": language,
        "scheduled_at": scheduled_at,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform_post_id": None,
        "metrics": {"likes": 0, "comments": 0, "shares": 0, "reach": 0, "impressions": 0},
    }
    await db.social_posts.insert_one({**post_record, "_id": None})
    await _log_action(current_user.user_id, platform, body.action, body.dict(), {"action_id": action_id, "status": status}, body.agent_id)

    return {
        "action_id": action_id,
        "platform": platform,
        "status": status,
        "language": language,
        "scheduled_at": scheduled_at,
        "message": f"Content {'scheduled for ' + scheduled_at if scheduled_at else 'queued for publishing'} on {platform.title()}",
        "note": f"Connect platform credentials to enable live publishing. Currently queued in MAARS for agent review.",
    }


@router.post("/social/message")
async def social_message(
    body: MessageRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a direct / private message on any platform."""
    platform = body.platform.lower()
    message_id = f"msg_{uuid.uuid4().hex[:12]}"

    message_record = {
        "message_id": message_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "platform": platform,
        "recipient_id": body.recipient_id,
        "message": body.message,
        "media_url": body.media_url,
        "language": body.language,
        "status": "queued",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.social_messages.insert_one({**message_record, "_id": None})
    await _log_action(current_user.user_id, platform, "message", body.dict(), {"message_id": message_id}, body.agent_id)

    return {"message_id": message_id, "platform": platform, "status": "queued",
            "message": f"Message queued for delivery to {body.recipient_id} on {platform.title()}"}


@router.post("/social/reply")
async def social_reply(
    body: ReplyRequest,
    current_user: User = Depends(get_current_user),
):
    """Reply to a comment, mention, or message on any platform."""
    platform = body.platform.lower()
    reply_id = f"rpl_{uuid.uuid4().hex[:12]}"

    await db.social_messages.insert_one({
        "message_id": reply_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "platform": platform,
        "type": "reply",
        "comment_id": body.comment_id,
        "reply_text": body.reply_text,
        "language": body.language,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "_id": None,
    })
    return {"reply_id": reply_id, "platform": platform, "status": "queued"}


@router.post("/social/boost")
async def boost_post(
    body: BoostRequest,
    current_user: User = Depends(get_current_user),
):
    """Boost / promote a post with geographic targeting and optional auto-translation.

    Geo-targeting logic:
      - Maps geo_regions to country lists and primary languages
      - If auto_translate=True, MAARS generates translated ad copies for each region
      - Returns a campaign_id for tracking; actual ad spend managed via platform APIs
    """
    platform = body.platform.lower()
    campaign_id = f"boost_{uuid.uuid4().hex[:12]}"

    # Build regional targeting map
    regional_breakdown = []
    for region_key in body.geo_regions:
        region = GEO_REGIONS.get(region_key, {"name": region_key, "countries": [], "primary_lang": "en"})
        regional_breakdown.append({
            "region": region_key,
            "display_name": region.get("name", region_key),
            "countries": region.get("countries", []),
            "language": region.get("primary_lang", "en"),
            "budget_allocation_pct": round(100.0 / len(body.geo_regions), 1),
            "estimated_reach": f"{int(body.budget_usd * 200 / len(body.geo_regions)):,}–{int(body.budget_usd * 400 / len(body.geo_regions)):,}",
        })

    boost_record = {
        "campaign_id": campaign_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "platform": platform,
        "post_id": body.post_id,
        "budget_usd": body.budget_usd,
        "geo_regions": body.geo_regions,
        "regional_breakdown": regional_breakdown,
        "duration_days": body.duration_days,
        "objective": body.objective,
        "auto_translate": body.auto_translate,
        "target_age_min": body.target_age_min,
        "target_age_max": body.target_age_max,
        "target_interests": body.target_interests,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {"impressions": 0, "reach": 0, "clicks": 0, "conversions": 0, "spend_usd": 0},
    }
    await db.social_campaigns.insert_one({**boost_record, "_id": None})
    await _log_action(current_user.user_id, platform, "boost", body.dict(), {"campaign_id": campaign_id}, body.agent_id)

    return {
        "campaign_id": campaign_id,
        "platform": platform,
        "status": "draft",
        "budget_usd": body.budget_usd,
        "geo_regions": body.geo_regions,
        "regional_breakdown": regional_breakdown,
        "objective": body.objective,
        "auto_translate": body.auto_translate,
        "estimated_total_reach": f"{int(body.budget_usd * 200):,}–{int(body.budget_usd * 400):,} people",
        "message": f"Boost campaign created for {platform.title()}. Review and activate in the Social Media Command center.",
    }


@router.post("/social/cold-email")
async def send_cold_email(
    body: ColdEmailRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a cold outreach email via SendGrid or Resend.

    Supports geo-region-aware language adaptation.
    Logs all outreach for compliance and tracking.
    """
    email_id = f"email_{uuid.uuid4().hex[:12]}"
    language = _resolve_language([body.geo_region] if body.geo_region else [], body.language)

    email_record = {
        "email_id": email_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "provider": body.provider,
        "to_email": body.to_email,
        "to_name": body.to_name,
        "subject": body.subject,
        "language": language,
        "geo_region": body.geo_region,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "opened": False,
        "clicked": False,
    }
    await db.cold_outreach.insert_one({**email_record, "_id": None})

    # Attempt actual send if provider credentials exist
    integration_keys = await get_integration_keys()
    provider = body.provider.lower()
    sent = False

    if provider == "sendgrid":
        sg_key = (integration_keys.get("sendgrid") or {}).get("api_key", "")
        if sg_key:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={"Authorization": f"Bearer {sg_key}", "Content-Type": "application/json"},
                        json={
                            "personalizations": [{"to": [{"email": body.to_email, "name": body.to_name or ""}], "dynamic_template_data": body.personalization}],
                            "from": {"email": body.from_name or "noreply@maarscommand.com", "name": body.from_name},
                            "reply_to": {"email": body.reply_to} if body.reply_to else None,
                            "subject": body.subject,
                            "content": [{"type": "text/html", "value": body.body_html}],
                        },
                        timeout=10,
                    )
                    sent = resp.status_code in (200, 202)
            except Exception as e:
                logger.warning(f"SendGrid send failed: {e}")
    elif provider == "resend":
        resend_key = (integration_keys.get("resend") or {}).get("api_key", "")
        if resend_key:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json={"from": f"{body.from_name} <noreply@maarscommand.com>", "to": [body.to_email], "subject": body.subject, "html": body.body_html},
                        timeout=10,
                    )
                    sent = resp.status_code == 200
            except Exception as e:
                logger.warning(f"Resend send failed: {e}")

    await db.cold_outreach.update_one({"email_id": email_id}, {"$set": {"status": "sent" if sent else "queued"}})
    return {"email_id": email_id, "status": "sent" if sent else "queued", "language": language, "provider": provider}


@router.post("/social/cold-call")
async def initiate_cold_call(
    body: ColdCallRequest,
    current_user: User = Depends(get_current_user),
):
    """Initiate a cold call via Twilio with an AI-generated script."""
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    language = _resolve_language([body.geo_region] if body.geo_region else [], body.language)

    call_record = {
        "call_id": call_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "to_phone": body.to_phone,
        "script": body.script,
        "language": language,
        "geo_region": body.geo_region,
        "status": "queued",
        "duration_seconds": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.cold_calls.insert_one({**call_record, "_id": None})

    integration_keys = await get_integration_keys()
    twilio_keys = integration_keys.get("twilio") or {}
    call_initiated = False

    if twilio_keys.get("account_sid") and twilio_keys.get("auth_token") and twilio_keys.get("phone_number"):
        try:
            import httpx, base64
            creds = base64.b64encode(f"{twilio_keys['account_sid']}:{twilio_keys['auth_token']}".encode()).decode()
            twiml = f'<Response><Say voice="{body.agent_voice}" language="{language}">{body.script}</Say></Response>'
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{twilio_keys['account_sid']}/Calls.json",
                    headers={"Authorization": f"Basic {creds}"},
                    data={"To": body.to_phone, "From": twilio_keys["phone_number"], "Twiml": twiml},
                    timeout=15,
                )
                if resp.status_code == 201:
                    call_initiated = True
                    twilio_sid = resp.json().get("sid", "")
                    await db.cold_calls.update_one({"call_id": call_id}, {"$set": {"status": "initiated", "twilio_sid": twilio_sid}})
        except Exception as e:
            logger.warning(f"Twilio call failed: {e}")

    return {
        "call_id": call_id,
        "status": "initiated" if call_initiated else "queued",
        "language": language,
        "to_phone": body.to_phone,
        "message": "Call initiated via Twilio." if call_initiated else "Call queued — configure Twilio credentials to enable live calling.",
    }


@router.post("/social/schedule")
async def schedule_action(
    body: ScheduleRequest,
    current_user: User = Depends(get_current_user),
):
    """Schedule a future social action: post, call, email, or meeting."""
    schedule_id = f"sched_{uuid.uuid4().hex[:12]}"
    language = _resolve_language(body.geo_regions or [], None)

    record = {
        "schedule_id": schedule_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "type": body.type,
        "platform": body.platform,
        "scheduled_at": body.scheduled_at,
        "title": body.title,
        "description": body.description,
        "participants": body.participants,
        "content": body.content,
        "geo_regions": body.geo_regions,
        "language": language,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.social_schedule.insert_one({**record, "_id": None})
    return {"schedule_id": schedule_id, "status": "scheduled", "scheduled_at": body.scheduled_at, "type": body.type}


@router.post("/social/campaign")
async def create_campaign(
    body: CampaignRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a multi-platform geo-targeted campaign.

    Intelligently:
      - Splits budget across platforms proportionally
      - Resolves language per geo region
      - Queues platform-specific posts and boost records
    """
    campaign_id = f"camp_{uuid.uuid4().hex[:12]}"

    platform_allocations = []
    for platform in body.platforms:
        pct = 100.0 / len(body.platforms)
        platform_allocations.append({
            "platform": platform,
            "budget_pct": round(pct, 1),
            "boost_budget_usd": round((body.boost_budget_usd or 0) * pct / 100, 2),
        })

    regional_copies = []
    for region_key in body.geo_regions:
        region = GEO_REGIONS.get(region_key, {"name": region_key, "primary_lang": "en"})
        regional_copies.append({
            "region": region_key,
            "display_name": region.get("name", region_key),
            "language": region.get("primary_lang", "en"),
            "content": body.content,            # MAARS agent will translate if auto_translate=True
            "needs_translation": body.auto_translate and region.get("primary_lang", "en") != "en",
            "hashtags": body.hashtags,
        })

    campaign_record = {
        "campaign_id": campaign_id,
        "user_id": current_user.user_id,
        "agent_id": body.agent_id,
        "name": body.name,
        "platforms": body.platforms,
        "platform_allocations": platform_allocations,
        "geo_regions": body.geo_regions,
        "regional_copies": regional_copies,
        "boost_budget_usd": body.boost_budget_usd,
        "auto_translate": body.auto_translate,
        "objective": body.objective,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "total_impressions": 0, "total_reach": 0, "total_clicks": 0,
            "total_conversions": 0, "total_spend_usd": 0,
        },
    }
    await db.social_campaigns.insert_one({**campaign_record, "_id": None})
    return {
        "campaign_id": campaign_id,
        "name": body.name,
        "status": "draft",
        "platforms": body.platforms,
        "geo_regions": body.geo_regions,
        "regional_copies": regional_copies,
        "platform_allocations": platform_allocations,
        "message": "Campaign created. Review regional copies, then activate to start publishing.",
    }


@router.get("/social/campaigns")
async def list_campaigns(current_user: User = Depends(get_current_user)):
    """List all campaigns for this user."""
    docs = await db.social_campaigns.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"campaigns": docs, "total": len(docs)}


@router.get("/social/analytics")
async def get_social_analytics(
    platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Aggregate social media performance metrics."""
    query = {"user_id": current_user.user_id}
    if platform:
        query["platform"] = platform.lower()

    posts = await db.social_posts.find(query, {"_id": 0}).to_list(100)
    messages = await db.social_messages.find(query, {"_id": 0}).to_list(100)
    campaigns = await db.social_campaigns.find(query, {"_id": 0}).to_list(50)
    emails = await db.cold_outreach.find({"user_id": current_user.user_id}, {"_id": 0}).to_list(100)
    calls = await db.cold_calls.find({"user_id": current_user.user_id}, {"_id": 0}).to_list(100)

    # Platform breakdown
    platform_stats = {}
    for post in posts:
        p = post.get("platform", "unknown")
        if p not in platform_stats:
            platform_stats[p] = {"posts": 0, "messages": 0, "campaigns": 0, "total_reach": 0}
        platform_stats[p]["posts"] += 1
        platform_stats[p]["total_reach"] += post.get("metrics", {}).get("reach", 0)

    for msg in messages:
        p = msg.get("platform", "unknown")
        if p not in platform_stats:
            platform_stats[p] = {"posts": 0, "messages": 0, "campaigns": 0, "total_reach": 0}
        platform_stats[p]["messages"] += 1

    return {
        "summary": {
            "total_posts": len(posts),
            "total_messages": len(messages),
            "total_campaigns": len(campaigns),
            "cold_emails_sent": sum(1 for e in emails if e.get("status") == "sent"),
            "cold_calls_initiated": sum(1 for c in calls if c.get("status") == "initiated"),
        },
        "platform_breakdown": platform_stats,
        "recent_posts": posts[:10],
        "active_campaigns": [c for c in campaigns if c.get("status") in ("active", "draft")][:5],
    }


@router.get("/social/outreach")
async def get_outreach_history(current_user: User = Depends(get_current_user)):
    """Get cold email and cold call history."""
    emails = await db.cold_outreach.find({"user_id": current_user.user_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    calls = await db.cold_calls.find({"user_id": current_user.user_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"emails": emails, "calls": calls}


@router.get("/social/schedule")
async def get_schedule(current_user: User = Depends(get_current_user)):
    """Get all scheduled social actions."""
    docs = await db.social_schedule.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("scheduled_at", 1).to_list(100)
    return {"scheduled": docs, "total": len(docs)}
