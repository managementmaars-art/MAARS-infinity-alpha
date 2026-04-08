"""Admin panel endpoints - stats, pricing, users, agents, integrations, analytics, branding."""
import os
import io
import csv
import uuid
import socket
import asyncio
import logging
import httpx
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Body
from starlette.responses import Response
from db import db
from auth import get_current_user, require_admin, User, ADMIN_EMAIL
from models.schemas import Agent, AgentCreate
from shared import constants as shared_constants
from shared.constants import (
    SUBSCRIPTION_PLANS, CUSTOM_AGENT_CREDIT_COST,
    EMERGENT_LLM_KEY, UPLOAD_DIR, STRIPE_API_KEY,
    DEFAULT_CUSTOM_PACKAGE_CONFIG, DEFAULT_CREDIT_PACKAGES,
    INTEGRATION_SERVICES, ROOT_DIR
)
from shared.utils import (
    get_api_keys, get_integration_keys, get_custom_package_config,
    get_live_bdt_rate, send_email_notification
)
from services.llm_service import MODEL_COSTS_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

# Track portrait generation progress in memory
_portrait_gen_state = {"running": False, "total": 0, "done": 0, "failed": 0, "last_updated": None}

@router.get("/admin/generate-avatars/status")
async def get_avatar_gen_status(admin: User = Depends(require_admin)):
    return _portrait_gen_state

@router.post("/admin/generate-avatars")
async def trigger_avatar_generation(admin: User = Depends(require_admin)):
    """Generate AI photorealistic portraits for all agents that still have SVG placeholder avatars."""
    global _portrait_gen_state
    if _portrait_gen_state["running"]:
        return {"status": "already_running", **_portrait_gen_state}

    # Find all SVG-avatar agents
    agents_to_gen = await db.agents.find(
        {"avatar": {"$regex": "^data:image/svg"}},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1}
    ).to_list(600)

    # Also include agents with missing or empty avatar
    no_avatar = await db.agents.find(
        {"$or": [{"avatar": {"$exists": False}}, {"avatar": ""}]},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1}
    ).to_list(100)
    agents_to_gen += no_avatar

    # Filter out already-generated PNG files
    from pathlib import Path
    avatar_dir = Path(__file__).parent.parent / "static" / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    to_generate = [a for a in agents_to_gen if not (avatar_dir / f"{a['agent_id']}.png").exists()]

    if not to_generate:
        return {"status": "all_done", "message": "All agents already have portrait photos", **_portrait_gen_state}

    _portrait_gen_state = {"running": True, "total": len(to_generate), "done": 0, "failed": 0, "last_updated": datetime.now(timezone.utc).isoformat()}

    async def _run_generation():
        global _portrait_gen_state
        try:
            from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
            import hashlib
            llm_key = EMERGENT_LLM_KEY
            if not llm_key:
                _portrait_gen_state["running"] = False
                _portrait_gen_state["error"] = "EMERGENT_LLM_KEY not configured"
                return

            image_gen = OpenAIImageGeneration(api_key=llm_key)
            SKIN_TONES = ["light", "medium", "olive", "tan", "brown", "dark"]
            HAIR_STYLES = ["short straight", "medium length", "curly", "slicked back", "shoulder length"]
            HAIR_COLORS = ["black", "dark brown", "brown", "auburn", "blonde", "gray"]
            ATTIRE = ["navy suit", "charcoal blazer", "white shirt", "gray turtleneck", "black blazer", "burgundy blazer"]
            BACKGROUNDS = ["dark navy studio", "dark charcoal gradient", "deep slate gray", "midnight blue"]

            sem = asyncio.Semaphore(3)

            async def gen_one(agent, idx):
                agent_id = agent["agent_id"]
                name = agent.get("name") or "Agent"
                role = agent.get("role") or ""
                file_path = avatar_dir / f"{agent_id}.png"
                if file_path.exists() and file_path.stat().st_size > 1000:
                    await db.agents.update_one({"agent_id": agent_id}, {"$set": {"avatar": f"/api/static/avatars/{agent_id}.png"}})
                    _portrait_gen_state["done"] += 1
                    return
                async with sem:
                    try:
                        hv = int(hashlib.md5(name.encode()).hexdigest(), 16)
                        gender = "male" if hv % 2 == 0 else "female"
                        age = ["late 20s","early 30s","mid 30s","early 40s"][hv % 4]
                        skin = SKIN_TONES[hv % len(SKIN_TONES)]
                        hair_s = HAIR_STYLES[(hv >> 4) % len(HAIR_STYLES)]
                        hair_c = HAIR_COLORS[(hv >> 8) % len(HAIR_COLORS)]
                        attire = ATTIRE[(hv >> 12) % len(ATTIRE)]
                        bg = BACKGROUNDS[(hv >> 16) % len(BACKGROUNDS)]
                        prompt = (f"Professional corporate headshot portrait of a {gender} professional in their {age}, "
                                  f"{skin} skin tone, {hair_c} {hair_s} hair, wearing a {attire}, "
                                  f"confident and approachable expression, studio lighting, {bg} background, "
                                  f"4K photorealistic, sharp focus, business portrait style")
                        images = await image_gen.generate_images(prompt=prompt, model="gpt-image-1", number_of_images=1)
                        if images:
                            file_path.write_bytes(images[0])
                            await db.agents.update_one({"agent_id": agent_id}, {"$set": {"avatar": f"/api/static/avatars/{agent_id}.png"}})
                            _portrait_gen_state["done"] += 1
                        else:
                            _portrait_gen_state["failed"] += 1
                    except Exception as e:
                        logger.warning(f"Avatar gen failed for {name}: {e}")
                        _portrait_gen_state["failed"] += 1
                    _portrait_gen_state["last_updated"] = datetime.now(timezone.utc).isoformat()
                    await asyncio.sleep(0.3)

            tasks = [gen_one(a, i) for i, a in enumerate(to_generate)]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Avatar generation error: {e}")
            _portrait_gen_state["error"] = str(e)
        finally:
            _portrait_gen_state["running"] = False
            _portrait_gen_state["last_updated"] = datetime.now(timezone.utc).isoformat()

    asyncio.create_task(_run_generation())
    return {"status": "started", "agents_queued": len(to_generate)}

@router.get("/admin/api-keys")
async def admin_get_api_keys(admin: User = Depends(require_admin)):
    """Get current API key configuration (masked)"""
    config = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
    if not config:
        config = {"active_provider": "emergent", "openai_key": "", "anthropic_key": "", "gemini_key": ""}
    
    # Mask keys for display
    def mask(key):
        if not key:
            return ""
        if len(key) < 10:
            return "***"
        return key[:8] + "..." + key[-4:]
    
    # Direct provider cost reference (per 1M tokens unless noted)
    cost_reference = {
        "openai": {
            "models": [
                {"name": "GPT-5", "input": "$2.50", "output": "$10.00"},
                {"name": "GPT-4.1", "input": "$2.00", "output": "$8.00"},
                {"name": "GPT-4.1 Mini", "input": "$0.40", "output": "$1.60"},
                {"name": "GPT-4.1 Nano", "input": "$0.10", "output": "$0.40"},
                {"name": "GPT-4o", "input": "$2.50", "output": "$10.00"},
                {"name": "GPT-4o Mini", "input": "$0.15", "output": "$0.60"},
                {"name": "O4", "input": "$15.00", "output": "$60.00"},
                {"name": "O4 Mini", "input": "$1.10", "output": "$4.40"},
                {"name": "O3", "input": "$10.00", "output": "$40.00"},
                {"name": "O3 Mini", "input": "$1.10", "output": "$4.40"},
                {"name": "GPT Image 1", "input": "$0.02/img", "output": "1024x1024"},
                {"name": "DALL-E 3", "input": "$0.04/img", "output": "1024x1024"},
                {"name": "Sora 2", "input": "$0.10/sec", "output": "4-12 sec video"},
            ],
            "unit": "per 1M tokens (text) / per image or second (gen)"
        },
        "anthropic": {
            "models": [
                {"name": "Claude Opus 4.6", "input": "$15.00", "output": "$75.00"},
                {"name": "Claude Sonnet 4.6", "input": "$3.00", "output": "$15.00"},
                {"name": "Claude Sonnet 4.5", "input": "$3.00", "output": "$15.00"},
                {"name": "Claude Opus 4.5", "input": "$15.00", "output": "$75.00"},
                {"name": "Claude Haiku 4.5", "input": "$0.80", "output": "$4.00"},
            ],
            "unit": "per 1M tokens"
        },
        "gemini": {
            "models": [
                {"name": "Gemini 2.5 Pro", "input": "$1.25", "output": "$10.00"},
                {"name": "Gemini 2.5 Flash", "input": "$0.075", "output": "$0.30"},
                {"name": "Gemini 2.5 Flash Lite", "input": "$0.038", "output": "$0.15"},
                {"name": "Gemini 3 Flash", "input": "$0.075", "output": "$0.30"},
                {"name": "Gemini 3 Pro", "input": "$1.25", "output": "$5.00"},
            ],
            "unit": "per 1M tokens"
        },
        "xai": {
            "models": [
                {"name": "Grok 3", "input": "$3.00", "output": "$15.00"},
                {"name": "Grok 3 Mini", "input": "$0.30", "output": "$0.50"},
                {"name": "Grok 2", "input": "$2.00", "output": "$10.00"},
            ],
            "unit": "per 1M tokens"
        },
        "deepseek": {
            "models": [
                {"name": "DeepSeek V3 0324", "input": "$0.14", "output": "$0.28"},
                {"name": "DeepSeek Chat (V3)", "input": "$0.14", "output": "$0.28"},
                {"name": "DeepSeek R1 0528", "input": "$0.55", "output": "$2.19"},
                {"name": "DeepSeek Reasoner (R1)", "input": "$0.55", "output": "$2.19"},
            ],
            "unit": "per 1M tokens"
        },
        "mistral": {
            "models": [
                {"name": "Mistral Large", "input": "$2.00", "output": "$6.00"},
                {"name": "Mistral Medium", "input": "$0.40", "output": "$2.00"},
                {"name": "Mistral Small", "input": "$0.10", "output": "$0.30"},
                {"name": "Mistral Nemo", "input": "$0.15", "output": "$0.15"},
                {"name": "Codestral", "input": "$0.30", "output": "$0.90"},
                {"name": "Pixtral Large", "input": "$2.00", "output": "$6.00"},
            ],
            "unit": "per 1M tokens"
        },
        "perplexity": {
            "models": [
                {"name": "Sonar", "input": "$1.00", "output": "$1.00"},
                {"name": "Sonar Pro", "input": "$3.00", "output": "$15.00"},
                {"name": "Sonar Reasoning", "input": "$1.00", "output": "$5.00"},
                {"name": "Sonar Reasoning Pro", "input": "$2.00", "output": "$8.00"},
                {"name": "Sonar Deep Research", "input": "$2.00", "output": "$8.00"},
            ],
            "unit": "per 1M tokens + $5/1K search"
        },
        "cohere": {
            "models": [
                {"name": "Command A (Mar 2025)", "input": "$2.50", "output": "$10.00"},
                {"name": "Command R+", "input": "$2.50", "output": "$10.00"},
                {"name": "Command R", "input": "$0.15", "output": "$0.60"},
            ],
            "unit": "per 1M tokens"
        },
        "elevenlabs": {
            "models": [
                {"name": "Multilingual v2", "input": "$0.30/1K chars", "output": "TTS audio"},
                {"name": "Turbo v2.5", "input": "$0.18/1K chars", "output": "Fast TTS"},
            ],
            "unit": "per 1K characters"
        },
        "groq": {
            "models": [
                {"name": "Llama 4 Scout 17B", "input": "$0.11", "output": "$0.34"},
                {"name": "Llama 4 Maverick 17B", "input": "$0.50", "output": "$0.77"},
                {"name": "Llama 3.3 70B", "input": "$0.59", "output": "$0.79"},
                {"name": "Llama 3.1 8B Instant", "input": "$0.05", "output": "$0.08"},
                {"name": "Qwen QwQ 32B", "input": "$0.29", "output": "$0.39"},
                {"name": "Gemma 2 9B", "input": "$0.20", "output": "$0.20"},
            ],
            "unit": "per 1M tokens"
        },
        "together": {
            "models": [
                {"name": "Llama 4 Maverick FP8", "input": "$0.27", "output": "$0.85"},
                {"name": "Llama 3.3 70B Turbo", "input": "$0.88", "output": "$0.88"},
                {"name": "Qwen 2.5 72B Turbo", "input": "$0.72", "output": "$0.72"},
                {"name": "Qwen 3 235B A22B FP8", "input": "$0.20", "output": "$0.60"},
                {"name": "DeepSeek R1", "input": "$3.00", "output": "$7.00"},
            ],
            "unit": "per 1M tokens"
        },
        "fireworks": {
            "models": [
                {"name": "Llama 4 Scout", "input": "$0.15", "output": "$0.60"},
                {"name": "Llama 4 Maverick", "input": "$0.50", "output": "$0.77"},
                {"name": "Qwen 3 30B A3B", "input": "$0.15", "output": "$0.60"},
                {"name": "Phi-4", "input": "$0.90", "output": "$0.90"},
                {"name": "DeepSeek V3", "input": "$0.56", "output": "$1.68"},
            ],
            "unit": "per 1M tokens"
        },
        "ai21": {
            "models": [
                {"name": "Jamba Large 1.7", "input": "$2.00", "output": "$8.00"},
                {"name": "Jamba Mini 1.7", "input": "$0.20", "output": "$0.40"},
            ],
            "unit": "per 1M tokens"
        },
        "cerebras": {
            "models": [
                {"name": "Llama 3.3 70B", "input": "$0.60", "output": "$0.60"},
                {"name": "Llama 3.1 8B", "input": "$0.10", "output": "$0.10"},
                {"name": "Qwen 3 32B", "input": "$0.40", "output": "$0.40"},
            ],
            "unit": "per 1M tokens (ultra-fast inference)"
        },
        "sambanova": {
            "models": [
                {"name": "Meta Llama 3.3 70B", "input": "$0.60", "output": "$0.60"},
                {"name": "Qwen 2.5 72B", "input": "$0.70", "output": "$0.70"},
                {"name": "DeepSeek R1 0528", "input": "$1.30", "output": "$1.30"},
            ],
            "unit": "per 1M tokens"
        },
        "nvidia": {
            "models": [
                {"name": "Nemotron Ultra 253B", "input": "$1.90", "output": "$1.90"},
                {"name": "Nemotron Super 49B", "input": "$0.35", "output": "$0.35"},
                {"name": "Llama 3.3 70B NIM", "input": "$0.60", "output": "$0.60"},
                {"name": "Mistral NIM 7B", "input": "$0.20", "output": "$0.20"},
            ],
            "unit": "per 1M tokens"
        },
        "moonshot": {
            "models": [
                {"name": "Kimi K2", "input": "$0.60", "output": "$2.50"},
                {"name": "Moonshot v1 8K", "input": "$1.63", "output": "$4.89"},
                {"name": "Moonshot v1 32K", "input": "$3.26", "output": "$9.78"},
                {"name": "Moonshot v1 128K", "input": "$8.16", "output": "$24.48"},
            ],
            "unit": "per 1M tokens"
        },
        "qwen": {
            "models": [
                {"name": "Qwen3 235B A22B", "input": "$0.22", "output": "$0.88"},
                {"name": "Qwen3 32B", "input": "$0.07", "output": "$0.28"},
                {"name": "Qwen2.5 72B Instruct", "input": "$0.40", "output": "$1.20"},
                {"name": "QwQ 32B", "input": "$0.15", "output": "$0.60"},
            ],
            "unit": "per 1M tokens"
        },
        "yi": {
            "models": [
                {"name": "Yi-Large", "input": "$3.00", "output": "$3.00"},
                {"name": "Yi-Medium", "input": "$0.80", "output": "$0.80"},
                {"name": "Yi-Lightning", "input": "$0.14", "output": "$0.14"},
            ],
            "unit": "per 1M tokens"
        },
        "zhipu": {
            "models": [
                {"name": "GLM-4-Plus", "input": "$0.70", "output": "$0.70"},
                {"name": "GLM-4-Air", "input": "$0.14", "output": "$0.14"},
                {"name": "GLM-4-Flash", "input": "$0.01", "output": "$0.01"},
            ],
            "unit": "per 1M tokens"
        },
        "doubao": {
            "models": [
                {"name": "Doubao Pro 32K", "input": "$0.11", "output": "$0.28"},
                {"name": "Doubao Lite 32K", "input": "$0.04", "output": "$0.07"},
            ],
            "unit": "per 1M tokens"
        },
        "hyperbolic": {
            "models": [
                {"name": "Llama 4 Scout", "input": "$0.10", "output": "$0.10"},
                {"name": "Llama 3.3 70B", "input": "$0.40", "output": "$0.40"},
                {"name": "Qwen 2.5 72B", "input": "$0.40", "output": "$0.40"},
            ],
            "unit": "per 1M tokens"
        },
        "upstage": {
            "models": [
                {"name": "Solar Pro", "input": "$2.00", "output": "$8.00"},
                {"name": "Solar Mini", "input": "$0.15", "output": "$0.15"},
            ],
            "unit": "per 1M tokens"
        },
        "writer": {
            "models": [
                {"name": "Palmyra X5", "input": "$1.00", "output": "$5.00"},
                {"name": "Palmyra X4", "input": "$0.50", "output": "$2.50"},
            ],
            "unit": "per 1M tokens"
        },
        "huggingface": {
            "models": [
                {"name": "Inference API (Free)", "input": "Free", "output": "rate limited"},
                {"name": "Inference Endpoints", "input": "varies", "output": "per compute hour"},
            ],
            "unit": "Free tier available. PRO: $9/mo for priority"
        },
        "llama": {
            "models": [
                {"name": "Llama 4 Scout 17B", "input": "$0.11", "output": "$0.11"},
                {"name": "Llama 4 Maverick 17B", "input": "$0.22", "output": "$0.88"},
                {"name": "Llama 3.3 70B", "input": "$0.20", "output": "$0.20"},
            ],
            "unit": "per 1M tokens (Meta Llama API)"
        },
        "novita": {
            "models": [
                {"name": "Llama 3.3 70B", "input": "$0.23", "output": "$0.23"},
                {"name": "DeepSeek R1", "input": "$0.55", "output": "$2.19"},
                {"name": "Qwen 2.5 72B", "input": "$0.23", "output": "$0.23"},
                {"name": "Llama 4 Scout", "input": "$0.12", "output": "$0.12"},
            ],
            "unit": "per 1M tokens"
        },
        "lepton": {
            "models": [
                {"name": "Llama 3.3 70B", "input": "$0.30", "output": "$0.30"},
                {"name": "DeepSeek R1", "input": "$0.55", "output": "$2.19"},
                {"name": "Qwen 2.5 72B", "input": "$0.30", "output": "$0.30"},
            ],
            "unit": "per 1M tokens"
        },
        "lambda": {
            "models": [
                {"name": "Llama 4 Scout", "input": "$0.17", "output": "$0.17"},
                {"name": "Llama 4 Maverick", "input": "$0.65", "output": "$0.65"},
                {"name": "Llama 3.3 70B", "input": "$0.30", "output": "$0.30"},
            ],
            "unit": "per 1M tokens"
        },
        "minimax": {
            "models": [
                {"name": "MiniMax Text 01", "input": "$0.20", "output": "$1.10"},
                {"name": "MiniMax M1", "input": "$0.30", "output": "$1.65"},
                {"name": "Abab 6.5s", "input": "$0.10", "output": "$0.10"},
            ],
            "unit": "per 1M tokens"
        },
        "inception": {
            "models": [
                {"name": "Mercury Coder Small", "input": "$0.25", "output": "$1.00"},
                {"name": "Mercury Coder Mini", "input": "$0.10", "output": "$0.40"},
            ],
            "unit": "per 1M tokens"
        },
        "arcee": {
            "models": [
                {"name": "Arcee Blitz", "input": "$0.50", "output": "$0.50"},
                {"name": "Virtuoso Large", "input": "$1.00", "output": "$1.00"},
                {"name": "Coder Large", "input": "$1.00", "output": "$1.00"},
            ],
            "unit": "per 1M tokens"
        },
        "amazon": {
            "models": [
                {"name": "Nova Pro", "input": "$0.80", "output": "$3.20"},
                {"name": "Nova Lite", "input": "$0.06", "output": "$0.24"},
                {"name": "Nova Micro", "input": "$0.04", "output": "$0.14"},
                {"name": "Titan Text Express", "input": "$0.80", "output": "$1.60"},
            ],
            "unit": "per 1M tokens (via Bedrock)"
        },
        "slack": {
            "models": [
                {"name": "Post Message", "input": "Free", "output": "per message"},
                {"name": "Read Channel", "input": "Free", "output": "per request"},
            ],
            "unit": "Free with Bot Token (Slack workspace subscription separate)"
        },
        "github": {
            "models": [
                {"name": "REST API", "input": "Free", "output": "5,000 req/hr"},
                {"name": "Create Issue/PR", "input": "Free", "output": "per action"},
            ],
            "unit": "Free for public repos. Requires Personal Access Token"
        },
        "sendgrid": {
            "models": [
                {"name": "Transactional Email", "input": "$0.001", "output": "per email"},
                {"name": "Marketing Email", "input": "$0.002", "output": "per email"},
            ],
            "unit": "Free: 100/day. Essentials: $19.95/50K emails/mo"
        },
        "resend": {
            "models": [
                {"name": "Email Send", "input": "$0.001", "output": "per email"},
                {"name": "Batch Email", "input": "$0.0008", "output": "per email"},
            ],
            "unit": "Free: 100/day. Pro: $20/50K emails/mo"
        },
        "twilio": {
            "models": [
                {"name": "SMS (US)", "input": "$0.0079", "output": "per SMS"},
                {"name": "SMS (Intl)", "input": "$0.01-0.15", "output": "per SMS"},
                {"name": "Voice Call", "input": "$0.014", "output": "per minute"},
            ],
            "unit": "Pay-as-you-go. Prices vary by country"
        },
        "airtable": {
            "models": [
                {"name": "Read Records", "input": "Free", "output": "5 req/sec"},
                {"name": "Write Records", "input": "Free", "output": "5 req/sec"},
            ],
            "unit": "Free: 1,000 records. Plus: $20/mo unlimited"
        },
        "calendly": {
            "models": [
                {"name": "Schedule Event", "input": "Free", "output": "per event"},
                {"name": "List Events", "input": "Free", "output": "per request"},
            ],
            "unit": "Free tier available. Pro: $12/mo includes API"
        },
        "giphy": {
            "models": [
                {"name": "Search GIFs", "input": "Free", "output": "42 req/hr"},
                {"name": "Trending GIFs", "input": "Free", "output": "42 req/hr"},
            ],
            "unit": "Free API. Rate limited (production key: 1000 req/hr)"
        },
        "google_suite": {
            "models": [
                {"name": "Gmail Send", "input": "Free", "output": "per email"},
                {"name": "Calendar Event", "input": "Free", "output": "per event"},
                {"name": "Drive Read/Write", "input": "Free", "output": "per file"},
            ],
            "unit": "Free with service account. Google Workspace quota limits apply"
        },
    }
    
    all_providers = [
        "openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere",
        "elevenlabs", "groq", "together", "fireworks", "ai21", "cerebras", "sambanova",
        "nvidia", "moonshot", "qwen",
        "yi", "zhipu", "doubao", "hyperbolic", "upstage", "writer", "huggingface", "llama",
        "novita", "lepton", "lambda", "amazon", "minimax", "inception", "arcee",
    ]
    result = {
        "active_provider": config.get("active_provider", "emergent"),
        "emergent_key_set": bool(EMERGENT_LLM_KEY),
        "cost_reference": cost_reference,
    }
    for p in all_providers:
        key_val = config.get(f"{p}_key", "")
        result[f"{p}_key"] = mask(key_val)
        result[f"{p}_key_set"] = bool(key_val)
    
    return result

@router.put("/admin/api-keys")
async def admin_update_api_keys(request: Request, admin: User = Depends(require_admin)):
    """Admin can update API keys and switch between Emergent and direct provider keys"""
    key_data = await request.json()
    update_doc = {
        "config_type": "api_keys",
        "active_provider": key_data.get("active_provider", "emergent"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }
    
    # Only update keys that are provided (non-empty)
    all_providers = [
        "openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere",
        "elevenlabs", "groq", "together", "fireworks", "ai21", "cerebras", "sambanova",
        "nvidia", "moonshot", "qwen",
        "yi", "zhipu", "doubao", "hyperbolic", "upstage", "writer", "huggingface", "llama",
        "novita", "lepton", "lambda", "amazon", "minimax", "inception", "arcee",
    ]
    for p in all_providers:
        if key_data.get(f"{p}_key"):
            update_doc[f"{p}_key"] = key_data[f"{p}_key"]
    
    # Merge with existing (preserve keys not being updated)
    existing = await db.platform_config.find_one({"config_type": "api_keys"})
    if existing:
        for p in all_providers:
            field = f"{p}_key"
            if field not in update_doc and field in existing:
                update_doc[field] = existing[field]
    
    await db.platform_config.update_one(
        {"config_type": "api_keys"},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "API keys updated", "active_provider": update_doc["active_provider"]}

@router.post("/admin/api-keys/test")
async def admin_test_api_key(request: Request, admin: User = Depends(require_admin)):
    """Test an API key using lightweight validation (list models, not completions)"""
    test_data = await request.json()
    provider = test_data.get("provider")
    api_key = test_data.get("api_key")
    
    if not provider or not api_key:
        raise HTTPException(status_code=400, detail="Provider and api_key required")
    
    test_configs = {
        "openai": {
            "url": "https://api.openai.com/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('data', []))} models.",
            "help": "Get your key at https://platform.openai.com/api-keys"
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/models",
            "headers": {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            "success_codes": [200, 403],
            "success_msg": lambda r: "Key verified! Anthropic API access confirmed.",
            "help": "Get your key at https://console.anthropic.com/settings/keys"
        },
        "gemini": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            "headers": {},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('models', []))} Gemini models.",
            "help": "Get your key at https://aistudio.google.com/app/apikey"
        },
        "xai": {
            "url": "https://api.x.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! xAI (Grok) API access confirmed. {len(r.json().get('data', []))} models.",
            "help": "Get your key at https://console.x.ai/team/default/api-keys"
        },
        "deepseek": {
            "url": "https://api.deepseek.com/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! DeepSeek API access confirmed.",
            "help": "Get your key at https://platform.deepseek.com/api_keys"
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('data', []))} Mistral models.",
            "help": "Get your key at https://console.mistral.ai/api-keys"
        },
        "perplexity": {
            "url": "https://api.perplexity.ai/chat/completions",
            "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            "method": "post",
            "body": {"model": "sonar", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
            "success_codes": [200, 422],
            "success_msg": lambda r: "Key verified! Perplexity API access confirmed.",
            "help": "Get your key at https://www.perplexity.ai/settings/api"
        },
        "cohere": {
            "url": "https://api.cohere.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Cohere API access confirmed.",
            "help": "Get your key at https://dashboard.cohere.com/api-keys"
        },
        "elevenlabs": {
            "url": "https://api.elevenlabs.io/v1/user",
            "headers": {"xi-api-key": api_key},
            "success_msg": lambda r: "Key verified! ElevenLabs API access confirmed.",
            "help": "Get your key at https://elevenlabs.io/app/settings/api-keys"
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('data', []))} Groq models.",
            "help": "Get your key at https://console.groq.com/keys"
        },
        "together": {
            "url": "https://api.together.xyz/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Together AI API access confirmed.",
            "help": "Get your key at https://api.together.ai/settings/api-keys"
        },
        "fireworks": {
            "url": "https://api.fireworks.ai/inference/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Fireworks AI API access confirmed.",
            "help": "Get your key at https://fireworks.ai/account/api-keys"
        },
        "ai21": {
            "url": "https://api.ai21.com/studio/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! AI21 API access confirmed.",
            "help": "Get your key at https://studio.ai21.com/account/api-key"
        },
        "cerebras": {
            "url": "https://api.cerebras.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Cerebras access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://cloud.cerebras.ai/"
        },
        "sambanova": {
            "url": "https://api.sambanova.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! SambaNova access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://cloud.sambanova.ai/apis"
        },
        "novita": {
            "url": "https://api.novita.ai/v3/openai/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Novita AI access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://novita.ai/settings"
        },
        "lepton": {
            "url": "https://api.lepton.ai/api/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Lepton AI access confirmed.",
            "help": "Get your key at https://dashboard.lepton.ai/"
        },
        "lambda": {
            "url": "https://api.lambda.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Lambda Labs access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://lambdalabs.com/service/gpu-cloud/api-keys"
        },
        "minimax": {
            "url": "https://api.minimaxi.chat/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Minimax AI access confirmed.",
            "help": "Get your key at https://platform.minimaxi.com/"
        },
        "inception": {
            "url": "https://api.inception.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Inception AI (Mercury) access confirmed.",
            "help": "Get your key at https://api.inception.ai/"
        },
        "arcee": {
            "url": "https://api.arcee.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Arcee AI access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://app.arcee.ai/"
        },
        "amazon": {
            "url": "https://bedrock-runtime.us-east-1.amazonaws.com/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Amazon Bedrock access confirmed.",
            "help": "Get AWS credentials at https://console.aws.amazon.com/bedrock/"
        },
        "nvidia": {
            "url": "https://integrate.api.nvidia.com/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Nvidia NIM access confirmed. {len(r.json().get('data', []))} models available.",
            "help": "Get your key at https://build.nvidia.com/"
        },
        "moonshot": {
            "url": "https://api.moonshot.cn/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Moonshot AI (Kimi) access confirmed.",
            "help": "Get your key at https://platform.moonshot.cn/"
        },
        "qwen": {
            "url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Qwen / Alibaba DashScope access confirmed.",
            "help": "Get your key at https://dashscope.aliyuncs.com/"
        },
    }
    
    config = test_configs.get(provider)
    if not config:
        return {"success": False, "message": f"Unknown provider '{provider}'. Supported: {', '.join(test_configs.keys())}"}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            success_codes = config.get("success_codes", [200])
            if config.get("method") == "post":
                resp = await client.post(config["url"], headers=config["headers"], json=config.get("body", {}))
            else:
                resp = await client.get(config["url"], headers=config["headers"])
            
            if resp.status_code in success_codes or resp.status_code == 200:
                return {"success": True, "message": config["success_msg"](resp)}
            elif resp.status_code == 401:
                return {"success": False, "message": f"Invalid API key. The key was rejected by {provider}. {config['help']}"}
            elif resp.status_code == 403:
                return {"success": True, "message": f"Key accepted but may have restricted permissions. Check your {provider} dashboard."}
            elif resp.status_code == 429:
                return {"success": False, "message": f"Rate limited by {provider}. Your key is valid but you've hit the rate limit. Try again in a moment."}
            else:
                error_detail = ""
                try:
                    error_detail = resp.json().get("error", {}).get("message", resp.text[:150])
                except Exception:
                    error_detail = resp.text[:150]
                return {"success": False, "message": f"{provider} returned {resp.status_code}: {error_detail}. {config['help']}"}
    except httpx.ConnectError:
        return {"success": False, "message": f"Cannot connect to {provider} API. Check your internet connection or the provider may be down."}
    except httpx.TimeoutException:
        return {"success": False, "message": f"Connection to {provider} timed out. The API may be slow or unreachable. Try again."}
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)[:150]}. {config.get('help', '')}"}


@router.get("/admin/pricing")
async def admin_get_pricing(admin: User = Depends(require_admin)):
    """Get current pricing configuration from DB or default"""
    pricing = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
    if not pricing:
        pricing = {
            "config_type": "pricing",
            "plans": SUBSCRIPTION_PLANS,
            "custom_agent_credit_cost": shared_constants.CUSTOM_AGENT_CREDIT_COST,
            "ai_cost_per_credit": 0.003,
            "target_profit_margin": 200,
            "bdt_exchange_rate": 107
        }
    return pricing

@router.put("/admin/pricing")
async def admin_update_pricing(request: Request, admin: User = Depends(require_admin)):
    """Admin can update platform pricing. Changes take effect immediately."""
    pricing_data = await request.json()

    plans = pricing_data.get("plans")
    if plans:
        # Replace ALL plans with what admin sends — no hardcoded validation
        SUBSCRIPTION_PLANS.clear()
        SUBSCRIPTION_PLANS.update(plans)

    if "custom_agent_credit_cost" in pricing_data:
        shared_constants.CUSTOM_AGENT_CREDIT_COST = pricing_data["custom_agent_credit_cost"]

    config_doc = {
        "config_type": "pricing",
        "plans": SUBSCRIPTION_PLANS,
        "custom_agent_credit_cost": shared_constants.CUSTOM_AGENT_CREDIT_COST,
        "ai_cost_per_credit": pricing_data.get("ai_cost_per_credit", 0.003),
        "target_profit_margin": pricing_data.get("target_profit_margin", 200),
        "bdt_exchange_rate": pricing_data.get("bdt_exchange_rate", 107),
        "credit_packages": pricing_data.get("credit_packages"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }

    await db.platform_config.update_one(
        {"config_type": "pricing"},
        {"$set": config_doc},
        upsert=True
    )

    await log_admin_action(admin.email, "pricing_update", {"plans_updated": list(plans.keys()) if plans else []})
    return {"message": "Pricing updated successfully", "pricing": config_doc}

@router.post("/admin/pricing/plans")
async def admin_create_plan(request: Request, admin: User = Depends(require_admin)):
    """Create a new subscription plan."""
    plan_data = await request.json()
    plan_id = plan_data.get("plan_id")
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id is required")
    if plan_id in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=409, detail=f"Plan '{plan_id}' already exists")

    SUBSCRIPTION_PLANS[plan_id] = {
        "name": plan_data.get("name", plan_id.title()),
        "price_usd": plan_data.get("price_usd", 0),
        "price_bdt": plan_data.get("price_bdt", 0),
        "credits": plan_data.get("credits", 0),
        "max_agents": plan_data.get("max_agents", 0),
        "max_custom_agents": plan_data.get("max_custom_agents", 0),
        "includes_commander": plan_data.get("includes_commander", False),
        "max_team_members": plan_data.get("max_team_members", 1),
        "features": plan_data.get("features", []),
    }

    await db.platform_config.update_one(
        {"config_type": "pricing"},
        {"$set": {"plans": SUBSCRIPTION_PLANS, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    await log_admin_action(admin.email, "plan_created", {"plan_id": plan_id})
    return {"message": f"Plan '{plan_id}' created", "plan": SUBSCRIPTION_PLANS[plan_id]}

@router.delete("/admin/pricing/plans/{plan_id}")
async def admin_delete_plan(plan_id: str, admin: User = Depends(require_admin)):
    """Delete a subscription plan."""
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found")
    if plan_id == "free":
        raise HTTPException(status_code=400, detail="Cannot delete the free plan")
    del SUBSCRIPTION_PLANS[plan_id]

    await db.platform_config.update_one(
        {"config_type": "pricing"},
        {"$set": {"plans": SUBSCRIPTION_PLANS, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    await log_admin_action(admin.email, "plan_deleted", {"plan_id": plan_id})
    return {"message": f"Plan '{plan_id}' deleted"}

@router.get("/admin/avg-cost")
async def admin_avg_cost(admin: User = Depends(require_admin)):
    """Get the real average cost per API call from usage_logs"""
    cost_pipeline = [
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"}
        }}
    ]
    cost_result = await db.usage_logs.aggregate(cost_pipeline).to_list(1)
    if cost_result and cost_result[0]["total_calls"] > 0:
        r = cost_result[0]
        avg = r["total_cost"] / r["total_calls"]
        return {
            "avg_cost_per_credit": round(avg, 6),
            "total_cost_usd": round(r["total_cost"], 6),
            "total_calls": r["total_calls"],
            "total_input_tokens": r.get("total_input_tokens", 0),
            "total_output_tokens": r.get("total_output_tokens", 0),
            "source": "real_usage"
        }
    return {"avg_cost_per_credit": 0.003, "total_cost_usd": 0, "total_calls": 0, "total_input_tokens": 0, "total_output_tokens": 0, "source": "default"}

@router.get("/exchange-rate")
async def get_exchange_rate():
    """Get live USD/BDT exchange rate (public, no auth required)"""
    rate = await get_live_bdt_rate()
    return {"usd_bdt": rate, "source": "live"}

@router.post("/admin/pricing/calculate")
async def admin_calculate_pricing(calc_data: dict, admin: User = Depends(require_admin)):
    """Calculate recommended prices based on AI costs and target profit margin"""
    ai_cost_per_credit = calc_data.get("ai_cost_per_credit", 0.003)
    target_margin_pct = calc_data.get("target_profit_margin", 200)
    bdt_rate = calc_data.get("bdt_exchange_rate", 107)
    
    # Calculate recommended prices for each plan
    plans = {}
    plan_configs = {
        "free": {"credits": 50, "max_agents": 1, "max_custom_agents": 0},
        "starter": {"credits": 500, "max_agents": 5, "max_custom_agents": 2},
        "pro": {"credits": 2000, "max_agents": 10, "max_custom_agents": 5},
        "business": {"credits": 6000, "max_agents": 20, "max_custom_agents": -1},
    }
    
    for plan_id, config in plan_configs.items():
        base_cost_usd = config["credits"] * ai_cost_per_credit
        margin_multiplier = 1 + (target_margin_pct / 100)
        recommended_usd = round(base_cost_usd * margin_multiplier, 2)
        recommended_bdt = round(recommended_usd * bdt_rate)
        
        plans[plan_id] = {
            "credits": config["credits"],
            "base_ai_cost_usd": round(base_cost_usd, 2),
            "recommended_price_usd": recommended_usd if plan_id != "free" else 0,
            "recommended_price_bdt": recommended_bdt if plan_id != "free" else 0,
            "profit_per_user_usd": round(recommended_usd - base_cost_usd, 2) if plan_id != "free" else 0,
            "actual_margin_pct": target_margin_pct if plan_id != "free" else 0
        }
    
    return {
        "ai_cost_per_credit": ai_cost_per_credit,
        "target_profit_margin": target_margin_pct,
        "bdt_exchange_rate": bdt_rate,
        "plan_calculations": plans
    }


@router.get("/admin/stats")
async def admin_stats(admin: User = Depends(require_admin)):
    """Get platform-wide statistics for admin"""
    total_users = await db.users.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    total_agents = await db.agents.count_documents({})
    custom_agents = await db.agents.count_documents({"is_custom": True})
    active_subs = await db.subscriptions.count_documents({"status": "active"})
    
    # Count messages across all chats
    msg_pipeline = [
        {"$project": {"message_count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$message_count"}}}
    ]
    msg_result = await db.chats.aggregate(msg_pipeline).to_list(1)
    total_messages = msg_result[0]["total"] if msg_result else 0
    
    # Plan distribution
    plan_pipeline = [
        {"$group": {"_id": "$plan_id", "count": {"$sum": 1}}}
    ]
    plan_dist = await db.subscriptions.aggregate(plan_pipeline).to_list(10)
    plan_distribution = {item["_id"]: item["count"] for item in plan_dist if item["_id"]}
    
    # Revenue from transactions
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0
    total_transactions = rev_result[0]["count"] if rev_result else 0
    
    # Total credits used
    credits_pipeline = [
        {"$group": {"_id": None, "total_used": {"$sum": "$credits_used"}, "total_remaining": {"$sum": "$credits"}}}
    ]
    credits_result = await db.subscriptions.aggregate(credits_pipeline).to_list(1)
    total_credits_used = credits_result[0]["total_used"] if credits_result else 0
    total_credits_remaining = credits_result[0]["total_remaining"] if credits_result else 0
    
    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "total_tasks": total_tasks,
        "total_agents": total_agents,
        "custom_agents": custom_agents,
        "total_messages": total_messages,
        "active_subscriptions": active_subs,
        "plan_distribution": plan_distribution,
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "total_credits_used": total_credits_used,
        "total_credits_remaining": total_credits_remaining
    }

@router.get("/admin/profit")
async def admin_profit(admin: User = Depends(require_admin)):
    """Get profit analytics - revenue vs API costs"""
    
    # Total revenue
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0
    
    # Total API cost from usage logs
    cost_pipeline = [
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"},
            "total_calls": {"$sum": 1}
        }}
    ]
    cost_result = await db.usage_logs.aggregate(cost_pipeline).to_list(1)
    total_cost = cost_result[0]["total_cost"] if cost_result else 0
    total_input_tokens = cost_result[0]["total_input_tokens"] if cost_result else 0
    total_output_tokens = cost_result[0]["total_output_tokens"] if cost_result else 0
    total_api_calls = cost_result[0]["total_calls"] if cost_result else 0
    
    # Per-provider breakdown
    provider_pipeline = [
        {"$group": {
            "_id": "$provider",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1},
            "input_tokens": {"$sum": "$input_tokens"},
            "output_tokens": {"$sum": "$output_tokens"}
        }}
    ]
    provider_result = await db.usage_logs.aggregate(provider_pipeline).to_list(10)
    provider_costs = {item["_id"]: {
        "cost": round(item["cost"], 4),
        "calls": item["calls"],
        "input_tokens": item["input_tokens"],
        "output_tokens": item["output_tokens"]
    } for item in provider_result if item["_id"]}
    
    # Per-model breakdown
    model_pipeline = [
        {"$group": {
            "_id": "$model",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1},
        }},
        {"$sort": {"cost": -1}}
    ]
    model_result = await db.usage_logs.aggregate(model_pipeline).to_list(20)
    model_costs = [{"model": item["_id"], "cost": round(item["cost"], 4), "calls": item["calls"]} for item in model_result if item["_id"]]
    
    # Per-plan estimated cost (based on credits used * avg cost per credit)
    avg_cost_per_call = total_cost / max(total_api_calls, 1)
    
    plan_profits = {}
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan_id == "free":
            plan_profits[plan_id] = {"revenue": 0, "est_max_cost": round(plan["credits"] * avg_cost_per_call, 2), "profit": 0}
        else:
            plan_profits[plan_id] = {
                "revenue": plan["price_usd"],
                "est_max_cost": round(plan["credits"] * avg_cost_per_call, 2),
                "profit": round(plan["price_usd"] - (plan["credits"] * avg_cost_per_call), 2),
                "margin_pct": round(((plan["price_usd"] - (plan["credits"] * avg_cost_per_call)) / max(plan["price_usd"], 0.01)) * 100, 1)
            }
    
    net_profit = total_revenue - total_cost
    
    return {
        "revenue": round(total_revenue, 2),
        "total_api_cost": round(total_cost, 4),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round((net_profit / max(total_revenue, 0.01)) * 100, 1),
        "total_api_calls": total_api_calls,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "avg_cost_per_call": round(avg_cost_per_call, 5),
        "provider_costs": provider_costs,
        "model_costs": model_costs,
        "plan_profits": plan_profits,
    }

@router.get("/admin/api-usage")
async def admin_api_usage(admin: User = Depends(require_admin)):
    """Check balance/usage for saved API keys"""
    api_keys_config = await get_api_keys()
    result = {}
    
    provider_checks = {
        "openai": {
            "url": "https://api.openai.com/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "OpenAI uses pay-as-you-go billing. Check dashboard.openai.com for balance."
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/models",
            "headers_fn": lambda k: {"x-api-key": k, "anthropic-version": "2023-06-01"},
            "ok_codes": [200, 403],
            "note": "Anthropic uses pay-as-you-go billing. Check console.anthropic.com for balance."
        },
        "gemini": {
            "url_fn": lambda k: f"https://generativelanguage.googleapis.com/v1beta/models?key={k}",
            "ok_codes": [200],
            "models_key": "models",
            "note": "Gemini has free tier with rate limits. Paid tier via Google Cloud billing."
        },
        "xai": {
            "url": "https://api.x.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "xAI Grok. Check console.x.ai for billing."
        },
        "deepseek": {
            "url": "https://api.deepseek.com/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "note": "DeepSeek. Check platform.deepseek.com for billing."
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "Mistral AI. Check console.mistral.ai for billing."
        },
        "perplexity": {
            "url": "https://api.perplexity.ai/chat/completions",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200, 401, 422],
            "note": "Perplexity. Check perplexity.ai/settings for billing."
        },
        "cohere": {
            "url": "https://api.cohere.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "note": "Cohere. Check dashboard.cohere.com for billing."
        },
        "elevenlabs": {
            "url": "https://api.elevenlabs.io/v1/user",
            "headers_fn": lambda k: {"xi-api-key": k},
            "ok_codes": [200],
            "note": "ElevenLabs TTS. Check elevenlabs.io for billing."
        },
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        for provider_id, check in provider_checks.items():
            key = api_keys_config.get(provider_id, "")
            if not key:
                continue
            try:
                url = check.get("url_fn", lambda k: check["url"])(key)
                hdrs = check.get("headers_fn", lambda k: {})(key)
                resp = await client.get(url, headers=hdrs)
                entry = {
                    "status": "active" if resp.status_code in check["ok_codes"] else "error",
                    "note": check.get("note", "")
                }
                models_key = check.get("models_key")
                if models_key and resp.status_code == 200:
                    try:
                        entry["models_available"] = len(resp.json().get(models_key, []))
                    except Exception:
                        pass
                result[provider_id] = entry
            except Exception as e:
                result[provider_id] = {"status": "error", "note": str(e)[:100]}
    
    # Our tracked usage per provider
    provider_pipeline = [
        {"$group": {
            "_id": "$provider",
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
            "total_tokens": {"$sum": {"$add": ["$input_tokens", "$output_tokens"]}}
        }}
    ]
    usage = await db.usage_logs.aggregate(provider_pipeline).to_list(10)
    tracked_usage = {item["_id"]: {
        "total_cost": round(item["total_cost"], 4),
        "total_calls": item["total_calls"],
        "total_tokens": item["total_tokens"]
    } for item in usage if item["_id"]}
    
    return {"providers": result, "tracked_usage": tracked_usage}

@router.get("/admin/users")
async def admin_get_users(page: int = 1, limit: int = 50, search: str = "", admin: User = Depends(require_admin)):
    """Get all users with their subscription info (paginated)"""
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    skip = (page - 1) * limit
    total = await db.users.count_documents(query)
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).skip(skip).to_list(limit)
    
    # Enrich with subscription data
    for u in users:
        sub = await db.subscriptions.find_one({"user_id": u["user_id"]}, {"_id": 0})
        u["subscription"] = sub or {"plan_id": "free", "credits": 0, "credits_used": 0}
        u["is_admin"] = u.get("email") == ADMIN_EMAIL
    
    return {"users": users, "total": total, "page": page, "pages": max(1, -(-total // limit))}

@router.get("/admin/agents")
async def admin_get_all_agents(admin: User = Depends(require_admin)):
    """Get all agents including custom ones"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(200)
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    return agents

@router.post("/admin/agents")
async def admin_create_agent(agent_data: AgentCreate, admin: User = Depends(require_admin)):
    """Admin can create agents visible to all users"""
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    agent_doc = {
        "agent_id": agent_id,
        "name": agent_data.name,
        "description": agent_data.description,
        "avatar": agent_data.avatar or "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg",
        "role": agent_data.role,
        "system_prompt": agent_data.system_prompt,
        "model_provider": agent_data.model_provider,
        "model_name": agent_data.model_name,
        "is_custom": False,
        "creator_id": None,
        "capabilities": agent_data.capabilities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.agents.insert_one(agent_doc)
    agent_doc.pop("_id", None)
    agent_doc['created_at'] = datetime.fromisoformat(agent_doc['created_at'])
    return Agent(**agent_doc)

@router.delete("/admin/agents/{agent_id}")
async def admin_delete_agent(agent_id: str, admin: User = Depends(require_admin)):
    """Admin can delete any agent"""
    result = await db.agents.delete_one({"agent_id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted"}

@router.get("/admin/custom-package")
async def admin_get_custom_package(admin: User = Depends(require_admin)):
    """Get custom package pricing config"""
    config = await get_custom_package_config()
    config.pop("config_type", None)
    return config

@router.post("/admin/custom-package")
async def admin_update_custom_package(request: Request, admin: User = Depends(require_admin)):
    """Update custom package pricing config"""
    body = await request.json()
    
    update_doc = {
        "config_type": "custom_packages",
        "per_agent_price_usd": float(body.get("per_agent_price_usd", 5.0)),
        "per_agent_price_bdt": float(body.get("per_agent_price_bdt", 535.0)),
        "commander_addon_price_usd": float(body.get("commander_addon_price_usd", 15.0)),
        "commander_addon_price_bdt": float(body.get("commander_addon_price_bdt", 1605.0)),
    }
    
    # Validate and save credit presets
    presets = body.get("credit_presets", [])
    if presets:
        validated_presets = []
        for p in presets:
            validated_presets.append({
                "id": p.get("id", f"cp_{p.get('credits', 0)}"),
                "credits": int(p.get("credits", 0)),
                "price_usd": float(p.get("price_usd", 0)),
                "price_bdt": float(p.get("price_bdt", 0)),
            })
        update_doc["credit_presets"] = validated_presets
    
    await db.platform_config.update_one(
        {"config_type": "custom_packages"},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "Custom package config updated", "config": update_doc}

@router.get("/admin/credit-packages")
async def admin_get_credit_packages(admin: User = Depends(require_admin)):
    """Get extra credit packages config"""
    config = await db.platform_config.find_one({"config_type": "credit_packages"}, {"_id": 0})
    if config and config.get("packages"):
        return {"packages": config["packages"]}
    return {"packages": DEFAULT_CREDIT_PACKAGES}

@router.post("/admin/credit-packages")
async def admin_update_credit_packages(request: Request, admin: User = Depends(require_admin)):
    """Update extra credit packages"""
    body = await request.json()
    packages = []
    for p in body.get("packages", []):
        packages.append({
            "id": p.get("id", f"credits_{p.get('credits', 0)}"),
            "credits": int(p.get("credits", 0)),
            "price_usd": float(p.get("price_usd", 0)),
            "price_bdt": float(p.get("price_bdt", 0)),
            "name": p.get("name", f"{p.get('credits', 0)} Credits"),
        })
    await db.platform_config.update_one(
        {"config_type": "credit_packages"},
        {"$set": {"config_type": "credit_packages", "packages": packages}},
        upsert=True
    )
    return {"message": "Credit packages updated", "packages": packages}

@router.get("/admin/transactions")
async def admin_get_transactions(page: int = 1, limit: int = 50, admin: User = Depends(require_admin)):
    """Get all payment transactions (paginated)"""
    skip = (page - 1) * limit
    total = await db.payment_transactions.count_documents({})
    transactions = await db.payment_transactions.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).to_list(limit)
    return {"transactions": transactions, "total": total, "page": page, "pages": max(1, -(-total // limit))}

@router.patch("/admin/users/{user_id}/subscription")
async def admin_update_subscription(user_id: str, plan_id: str, credits: int = 0, admin: User = Depends(require_admin)):
    """Admin can update user subscription"""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {
            "plan_id": plan_id,
            "credits": credits if credits > 0 else plan["credits"],
            "credits_used": 0,
            "status": "active",
            "renewed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": f"User updated to {plan['name']} plan"}


# ============== STARTUP ==============

# ============== USAGE LOG BACKFILL ==============

MODEL_COSTS_MAP = {
    # OpenAI Text
    "gpt-5.2": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "provider": "openai"},
    "o3": {"input": 10.00, "output": 40.00, "provider": "openai"},
    "o3-mini": {"input": 1.10, "output": 4.40, "provider": "openai"},
    # Anthropic
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    "claude-haiku-4-5-20250929": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    # Gemini Text
    "gemini-3-flash-preview": {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-3-pro-preview": {"input": 1.25, "output": 5.00, "provider": "gemini"},
    # Gemini Image (Nano Banana 2)
    "gemini-3-pro-image-preview": {"input": 0.02, "output": 0.0, "provider": "gemini", "per_unit": "image"},
    "gemini-nano-banana-2": {"input": 0.02, "output": 0.0, "provider": "gemini", "per_unit": "image"},
    # xAI Grok
    "grok-3": {"input": 3.00, "output": 15.00, "provider": "xai"},
    "grok-3-mini": {"input": 0.30, "output": 0.50, "provider": "xai"},
    "grok-2": {"input": 2.00, "output": 10.00, "provider": "xai"},
    # DeepSeek
    "deepseek-chat": {"input": 0.14, "output": 0.28, "provider": "deepseek"},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19, "provider": "deepseek"},
    # Mistral
    "mistral-large-latest": {"input": 2.00, "output": 6.00, "provider": "mistral"},
    "mistral-medium-latest": {"input": 0.40, "output": 2.00, "provider": "mistral"},
    "mistral-small-latest": {"input": 0.10, "output": 0.30, "provider": "mistral"},
    # Perplexity
    "sonar": {"input": 1.00, "output": 1.00, "provider": "perplexity"},
    "sonar-pro": {"input": 3.00, "output": 15.00, "provider": "perplexity"},
    # Cohere
    "command-r-plus": {"input": 2.50, "output": 10.00, "provider": "cohere"},
    "command-r": {"input": 0.15, "output": 0.60, "provider": "cohere"},
    # OpenAI Image Generation
    "gpt-image-1": {"input": 0.02, "output": 0.0, "provider": "openai", "per_unit": "image"},
    "dall-e-3": {"input": 0.04, "output": 0.0, "provider": "openai", "per_unit": "image"},
    # OpenAI Video
    "sora-2": {"input": 0.10, "output": 0.0, "provider": "openai", "per_unit": "second"},
}

# Credit cost per model — how many credits each model consumes per message
MODEL_CREDIT_COSTS = {
    # Economy (1 credit)
    "gpt-4o-mini": 1, "claude-haiku-4-5-20250929": 1, "gemini-3-flash-preview": 1,
    "deepseek-chat": 1, "mistral-small-latest": 1, "command-r": 1, "grok-3-mini": 1,
    # Standard (2 credits)
    "gpt-4o": 2, "grok-2": 2, "mistral-medium-latest": 2, "sonar": 2,
    "gemini-3-pro-preview": 2, "deepseek-reasoner": 2,
    # Flagship (3 credits)
    "gpt-5.2": 3, "claude-sonnet-4-5-20250929": 3, "grok-3": 3,
    "mistral-large-latest": 3, "command-r-plus": 3, "sonar-pro": 3,
    # Premium (5 credits)
    "claude-opus-4-5-20251101": 5, "o3": 5,
    # Reasoning (2 credits)
    "o3-mini": 2,
    # Image Generation (5 credits)
    "gemini-3-pro-image-preview": 5, "gemini-nano-banana-2": 5,
    "gpt-image-1": 5, "dall-e-3": 5,
    # Video Generation (10 credits)
    "sora-2": 10,
}

def get_credit_cost(model_name: str, has_image: bool = False, has_video: bool = False) -> int:
    """Get the credit cost for a model, with extras for generation."""
    model_clean = model_name.split("/")[-1] if "/" in model_name else model_name
    base_cost = MODEL_CREDIT_COSTS.get(model_clean, 2)
    if has_image:
        base_cost += MODEL_CREDIT_COSTS.get("gemini-nano-banana-2", 5)
    if has_video:
        base_cost += MODEL_CREDIT_COSTS.get("sora-2", 10)
    return base_cost

async def backfill_usage_logs():
    """Backfill usage logs from historical chat messages (runs once)"""
    already_done = await db.platform_config.find_one({"config_type": "usage_backfill_done"})
    if already_done:
        return
    
    logger.info("Backfilling usage logs from historical chats...")
    count = 0
    
    chats = await db.chats.find({}, {"_id": 0}).to_list(5000)
    
    for chat in chats:
        agent_id = chat.get("agent_id", "")
        user_id = chat.get("user_id", "")
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        
        default_model = agent.get("model_name", "gpt-5.2") if agent else "gpt-5.2"
        default_provider = agent.get("model_provider", "openai") if agent else "openai"
        
        messages = chat.get("messages", [])
        # Pair user messages with assistant responses
        for i, msg in enumerate(messages):
            if msg.get("role") != "assistant":
                continue
            
            content = msg.get("content", "")
            model_used = msg.get("model_used", default_model)
            
            # Find the preceding user message for input estimation
            user_content = ""
            if i > 0 and messages[i-1].get("role") == "user":
                user_content = messages[i-1].get("content", "")
            
            # Estimate tokens
            system_prompt = agent.get("system_prompt", "") if agent else ""
            input_text = user_content + system_prompt
            est_input_tokens = max(len(input_text) // 4, 50)
            est_output_tokens = max(len(content) // 4, 50)
            
            # Clean model name for cost lookup
            model_clean = model_used.split("/")[-1] if "/" in model_used else model_used
            costs = MODEL_COSTS_MAP.get(model_clean, {"input": 2.50, "output": 10.00, "provider": default_provider})
            est_cost = (est_input_tokens * costs["input"] / 1_000_000) + (est_output_tokens * costs["output"] / 1_000_000)
            
            created_at = msg.get("timestamp") or chat.get("created_at") or datetime.now(timezone.utc).isoformat()
            
            usage_log = {
                "log_id": f"backfill_{uuid.uuid4().hex[:10]}",
                "user_id": user_id,
                "chat_id": chat.get("chat_id", ""),
                "agent_id": agent_id,
                "model": model_used,
                "provider": costs.get("provider", default_provider),
                "input_tokens": est_input_tokens,
                "output_tokens": est_output_tokens,
                "estimated_cost_usd": round(est_cost, 6),
                "key_source": "emergent",
                "created_at": created_at,
                "backfilled": True
            }
            await db.usage_logs.insert_one(usage_log)
            count += 1
    
    await db.platform_config.insert_one({"config_type": "usage_backfill_done", "count": count, "done_at": datetime.now(timezone.utc).isoformat()})
    logger.info(f"Backfilled {count} usage log entries from historical chats")

@router.post("/admin/backfill-usage")
async def admin_backfill_usage(admin: User = Depends(require_admin)):
    """Force re-backfill usage logs from all chat history"""
    await db.usage_logs.delete_many({"backfilled": True})
    await db.platform_config.delete_one({"config_type": "usage_backfill_done"})
    await backfill_usage_logs()
    count = await db.usage_logs.count_documents({"backfilled": True})
    return {"message": f"Backfilled {count} usage log entries from chat history"}

# ============== ADMIN INTEGRATION MANAGEMENT ==============

@router.get("/admin/integrations")
async def admin_get_integrations(admin: User = Depends(require_admin)):
    """Get all integration configs and their status"""
    config = await get_integration_keys()
    result = {}
    for svc_id, svc_def in INTEGRATION_SERVICES.items():
        svc_config = config.get(svc_id, {})
        has_key = any(svc_config.get(f) for f in svc_def.get("key_fields", []))
        result[svc_id] = {
            "name": svc_def["name"],
            "description": svc_def["description"],
            "key_fields": svc_def["key_fields"],
            "configured": has_key,
            "keys_set": {f: bool(svc_config.get(f)) for f in svc_def["key_fields"]}
        }
    return result

@router.post("/admin/integrations")
async def admin_update_integrations(request: Request, admin: User = Depends(require_admin)):
    """Update integration keys"""
    data = await request.json()
    config = await get_integration_keys()
    
    for svc_id, svc_data in data.items():
        if svc_id in INTEGRATION_SERVICES and isinstance(svc_data, dict):
            if svc_id not in config:
                config[svc_id] = {}
            for field in INTEGRATION_SERVICES[svc_id]["key_fields"]:
                if field in svc_data and svc_data[field]:
                    config[svc_id][field] = svc_data[field]
    
    config["config_type"] = "integration_keys"
    await db.platform_config.update_one(
        {"config_type": "integration_keys"},
        {"$set": config},
        upsert=True
    )
    return {"message": "Integration keys updated successfully"}

@router.get("/admin/integrations/test/{service_id}")
async def admin_test_integration(service_id: str, admin: User = Depends(require_admin)):
    """Test if an integration is working"""
    if service_id not in INTEGRATION_SERVICES:
        raise HTTPException(404, "Unknown service")
    
    config = await get_integration_keys()
    svc_config = config.get(service_id, {})
    svc_def = INTEGRATION_SERVICES[service_id]
    has_key = any(svc_config.get(f) for f in svc_def.get("key_fields", []))
    
    if not has_key:
        return {"status": "not_configured", "message": "No API key configured"}
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if service_id == "slack":
                resp = await client.post(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {svc_config.get('bot_token', '')}"}
                )
                data = resp.json()
                return {"status": "active" if data.get("ok") else "error", "message": data.get("team", data.get("error", ""))}
            elif service_id == "github":
                resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {svc_config.get('personal_access_token', '')}"}
                )
                if resp.status_code == 200:
                    return {"status": "active", "message": f"Authenticated as {resp.json().get('login', '')}"}
                return {"status": "error", "message": f"Auth failed: {resp.status_code}"}
            elif service_id == "sendgrid":
                resp = await client.get(
                    "https://api.sendgrid.com/v3/user/profile",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "resend":
                resp = await client.get(
                    "https://api.resend.com/api-keys",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "giphy":
                resp = await client.get(
                    "https://api.giphy.com/v1/gifs/trending",
                    params={"api_key": svc_config.get("api_key", ""), "limit": 1}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "airtable":
                resp = await client.get(
                    "https://api.airtable.com/v0/meta/whoami",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "calendly":
                resp = await client.get(
                    "https://api.calendly.com/users/me",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "twilio":
                sid = svc_config.get("account_sid", "")
                auth = svc_config.get("auth_token", "")
                resp = await client.get(f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json", auth=(sid, auth))
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "google_suite":
                svc_json = svc_config.get("service_account_json", "")
                if not svc_json:
                    return {"status": "not_configured", "message": "No Service Account JSON configured"}
                try:
                    import json as _json
                    from google.oauth2 import service_account as _sa
                    from googleapiclient.discovery import build as _build
                    info = _json.loads(svc_json) if isinstance(svc_json, str) else svc_json
                    creds = _sa.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/calendar.readonly"])
                    service = _build("calendar", "v3", credentials=creds)
                    service.calendarList().list(maxResults=1).execute()
                    delegate_email = svc_config.get("delegate_email", "")
                    msg = f"Service account authenticated ({info.get('client_email', 'OK')})"
                    if delegate_email:
                        msg += f". Delegate: {delegate_email}"
                    return {"status": "active", "message": msg}
                except Exception as gs_err:
                    return {"status": "error", "message": str(gs_err)[:200]}
            else:
                return {"status": "unknown", "message": "Test not available for this service"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}


@router.get("/admin/integration-status")
async def admin_integration_status(admin: User = Depends(require_admin)):
    """Get status of all integration tools - which are active vs inactive."""
    config = await get_integration_keys()
    from config import AGENT_TOOLS
    
    tool_status = []
    for tool_name, tool_def in AGENT_TOOLS.items():
        requires = tool_def.get("requires")
        status = "active"
        reason = "No key required"
        if requires:
            svc_config = config.get(requires, {})
            svc_def = INTEGRATION_SERVICES.get(requires, {})
            has_key = any(svc_config.get(f) for f in svc_def.get("key_fields", []))
            if has_key:
                status = "active"
                reason = f"{svc_def.get('name', requires)} configured"
            else:
                status = "inactive"
                reason = f"Requires {svc_def.get('name', requires)} API key"
        tool_status.append({
            "tool_name": tool_name,
            "display_name": tool_def.get("name", tool_name),
            "description": tool_def.get("description", ""),
            "status": status,
            "reason": reason,
            "requires_service": requires,
        })
    
    active_count = sum(1 for t in tool_status if t["status"] == "active")
    return {
        "tools": tool_status,
        "active_count": active_count,
        "total_count": len(tool_status),
    }


# ============== CUSTOMER ANALYTICS DASHBOARD ==============

@router.get("/admin/analytics")
async def admin_analytics(admin: User = Depends(require_admin)):
    """Comprehensive analytics dashboard data for admin."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    seven_days_ago = (now - timedelta(days=7)).isoformat()

    # --- KPIs ---
    total_users = await db.users.count_documents({})
    active_7d = await db.users.count_documents({"last_active": {"$gte": seven_days_ago}})
    active_30d = await db.users.count_documents({"last_active": {"$gte": thirty_days_ago}})
    # Fallback: if last_active isn't tracked, count users who created chats recently
    if active_7d == 0 and total_users > 0:
        recent_chatters_7d = await db.chats.distinct("user_id", {"created_at": {"$gte": seven_days_ago}})
        active_7d = len(recent_chatters_7d)
        recent_chatters_30d = await db.chats.distinct("user_id", {"created_at": {"$gte": thirty_days_ago}})
        active_30d = len(recent_chatters_30d)

    total_chats = await db.chats.count_documents({})

    # Revenue
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0

    # MRR: sum of active paid subscription plan prices
    mrr = 0
    subs = await db.subscriptions.find({"status": "active"}, {"_id": 0, "plan_id": 1}).to_list(1000)
    for s in subs:
        plan = SUBSCRIPTION_PLANS.get(s.get("plan_id", "free"), {})
        mrr += plan.get("price_usd", 0)

    # --- Daily Signups (last 30 days) ---
    all_users = await db.users.find({}, {"_id": 0, "created_at": 1}).to_list(5000)
    daily_signups = {}
    for u in all_users:
        ca = u.get("created_at", "")
        if ca:
            day = ca[:10]
            daily_signups[day] = daily_signups.get(day, 0) + 1

    # Build last 30 days array
    signup_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        signup_series.append({"date": d, "signups": daily_signups.get(d, 0)})

    # --- Daily Messages (last 30 days) ---
    all_chats = await db.chats.find({}, {"_id": 0, "messages": 1}).to_list(5000)
    daily_messages = {}
    for chat in all_chats:
        for msg in chat.get("messages", []):
            ca = msg.get("created_at", "")
            if ca:
                day = ca[:10]
                daily_messages[day] = daily_messages.get(day, 0) + 1

    message_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        message_series.append({"date": d, "messages": daily_messages.get(d, 0)})

    # --- Daily Revenue (last 30 days) ---
    paid_txns = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "amount": 1, "created_at": 1}
    ).to_list(5000)
    daily_revenue = {}
    for tx in paid_txns:
        ca = tx.get("created_at", "")
        if ca:
            day = ca[:10]
            daily_revenue[day] = daily_revenue.get(day, 0) + tx.get("amount", 0)

    revenue_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        revenue_series.append({"date": d, "revenue": round(daily_revenue.get(d, 0), 2)})

    # --- Agent Usage ---
    agent_usage_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    agent_usage_raw = await db.chats.aggregate(agent_usage_pipeline).to_list(50)
    # Enrich with agent names
    agent_map = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1}).to_list(200)
    for a in all_agents:
        agent_map[a["agent_id"]] = a
    agent_usage = []
    for item in agent_usage_raw:
        aid = item["_id"]
        agent_info = agent_map.get(aid, {})
        agent_usage.append({
            "agent_id": aid,
            "name": agent_info.get("name", aid or "Unknown"),
            "messages": item["count"]
        })

    # --- Subscription Distribution ---
    plan_pipeline = [
        {"$group": {"_id": "$plan_id", "count": {"$sum": 1}}}
    ]
    plan_dist = await db.subscriptions.aggregate(plan_pipeline).to_list(10)
    plan_distribution = [{"plan": item["_id"] or "free", "count": item["count"]} for item in plan_dist]

    # --- Token Usage (last 30 days from usage_logs) ---
    token_pipeline = [
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "input_tokens": {"$sum": "$input_tokens"},
            "output_tokens": {"$sum": "$output_tokens"},
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    token_raw = await db.usage_logs.aggregate(token_pipeline).to_list(31)
    token_map = {item["_id"]: item for item in token_raw}
    token_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = token_map.get(d, {})
        token_series.append({
            "date": d,
            "input_tokens": entry.get("input_tokens", 0),
            "output_tokens": entry.get("output_tokens", 0),
            "cost": round(entry.get("cost", 0), 4),
            "calls": entry.get("calls", 0)
        })

    # --- Top Users by Messages ---
    top_users_pipeline = [
        {"$project": {"user_id": 1, "msg_count": {"$size": "$messages"}}},
        {"$group": {"_id": "$user_id", "total_messages": {"$sum": "$msg_count"}}},
        {"$sort": {"total_messages": -1}},
        {"$limit": 10}
    ]
    top_users_raw = await db.chats.aggregate(top_users_pipeline).to_list(10)
    user_ids = [u["_id"] for u in top_users_raw]
    user_map = {}
    if user_ids:
        user_docs = await db.users.find({"user_id": {"$in": user_ids}}, {"_id": 0, "user_id": 1, "name": 1, "email": 1}).to_list(10)
        for ud in user_docs:
            user_map[ud["user_id"]] = ud
    top_users = []
    for u in top_users_raw:
        info = user_map.get(u["_id"], {})
        top_users.append({
            "user_id": u["_id"],
            "name": info.get("name", "Unknown"),
            "email": info.get("email", ""),
            "total_messages": u["total_messages"]
        })

    # --- Cost by Model ---
    model_cost_pipeline = [
        {"$group": {
            "_id": "$model",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1}
        }},
        {"$sort": {"cost": -1}},
        {"$limit": 10}
    ]
    model_costs = await db.usage_logs.aggregate(model_cost_pipeline).to_list(10)
    model_cost_data = [{"model": m["_id"] or "unknown", "cost": round(m["cost"], 4), "calls": m["calls"]} for m in model_costs]

    return {
        "kpis": {
            "total_users": total_users,
            "active_7d": active_7d,
            "active_30d": active_30d,
            "total_chats": total_chats,
            "total_revenue": round(total_revenue, 2),
            "mrr": round(mrr, 2),
        },
        "daily_signups": signup_series,
        "daily_messages": message_series,
        "daily_revenue": revenue_series,
        "agent_usage": agent_usage,
        "plan_distribution": plan_distribution,
        "token_usage": token_series,
        "top_users": top_users,
        "model_costs": model_cost_data,
    }


# ============== SMTP CONFIGURATION ==============

@router.get("/admin/smtp-config")
async def admin_get_smtp_config(admin: User = Depends(require_admin)):
    """Get current SMTP configuration status (masked)."""
    return {
        "email": shared_constants.SMTP_EMAIL or "",
        "has_password": bool(shared_constants.SMTP_PASSWORD),
        "configured": bool(shared_constants.SMTP_EMAIL and shared_constants.SMTP_PASSWORD)
    }

@router.post("/admin/smtp-config")
async def admin_update_smtp_config(request: Request, admin: User = Depends(require_admin)):
    """Update SMTP configuration. Saves to .env and reloads in memory."""
    data = await request.json()
    new_email = data.get("email", "").strip()
    new_password = data.get("password", "").strip()

    if not new_email:
        raise HTTPException(400, "Email is required")

    # Update module-level vars
    shared_constants.SMTP_EMAIL = new_email
    if new_password:
        shared_constants.SMTP_PASSWORD = new_password

    await log_admin_action(admin.email, "smtp_update", {"email": new_email})

    # Persist to .env file
    env_path = ROOT_DIR / '.env'
    lines = env_path.read_text().splitlines()
    new_lines = []
    email_set = False
    password_set = False
    for line in lines:
        if line.startswith("SMTP_EMAIL="):
            new_lines.append(f"SMTP_EMAIL={new_email}")
            email_set = True
        elif line.startswith("SMTP_PASSWORD=") and new_password:
            new_lines.append(f"SMTP_PASSWORD={new_password}")
            password_set = True
        else:
            new_lines.append(line)
    if not email_set:
        new_lines.append(f"SMTP_EMAIL={new_email}")
    if new_password and not password_set:
        new_lines.append(f"SMTP_PASSWORD={new_password}")
    env_path.write_text("\n".join(new_lines) + "\n")

    return {"success": True, "configured": bool(shared_constants.SMTP_EMAIL and shared_constants.SMTP_PASSWORD)}

@router.post("/admin/smtp-test")
async def admin_test_smtp(request: Request, admin: User = Depends(require_admin)):
    """Send a test email to verify SMTP configuration."""
    data = await request.json()
    test_to = data.get("to_email", admin.email)

    if not shared_constants.SMTP_EMAIL or not shared_constants.SMTP_PASSWORD:
        raise HTTPException(400, "SMTP not configured. Save credentials first.")

    html = """
    <div style="font-family:Arial;padding:20px;background:#111;color:#fff;border-radius:12px;">
        <h2 style="color:#6366f1;">MAARS Command - SMTP Test</h2>
        <p>This is a test email from your MAARS Command platform.</p>
        <p>If you're seeing this, your Gmail SMTP is configured correctly!</p>
        <hr style="border-color:#333;"/>
        <p style="color:#666;font-size:12px;">MAARS Global Corporation</p>
    </div>
    """
    success = await send_email_notification(test_to, "MAARS Command - SMTP Test", html)
    if success:
        return {"success": True, "message": f"Test email sent to {test_to}"}
    else:
        raise HTTPException(500, "Failed to send test email. Check your credentials.")


@router.get("/admin/agent-performance")
async def admin_agent_performance(admin: User = Depends(require_admin)):
    """Get performance metrics for all agents based on user feedback."""
    # Aggregate feedback from all chats
    pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant", "messages.feedback": {"$in": ["up", "down"]}}},
        {"$group": {
            "_id": "$agent_id",
            "total_feedback": {"$sum": 1},
            "thumbs_up": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "up"]}, 1, 0]}},
            "thumbs_down": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "down"]}, 1, 0]}},
        }},
        {"$sort": {"total_feedback": -1}}
    ]
    feedback_data = await db.chats.aggregate(pipeline).to_list(50)

    # Get total messages per agent
    msg_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "total_messages": {"$sum": 1}}},
    ]
    msg_data = await db.chats.aggregate(msg_pipeline).to_list(50)
    msg_map = {m["_id"]: m["total_messages"] for m in msg_data}

    # Get agent names
    agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1}).to_list(200)
    agent_map = {a["agent_id"]: a for a in agents}
    feedback_map = {f["_id"]: f for f in feedback_data}

    performance = []
    for a in agents:
        aid = a["agent_id"]
        f = feedback_map.get(aid, {})
        total_msgs = msg_map.get(aid, 0)
        up = f.get("thumbs_up", 0)
        down = f.get("thumbs_down", 0)
        total_fb = up + down
        satisfaction = round((up / total_fb * 100), 1) if total_fb > 0 else None
        performance.append({
            "agent_id": aid,
            "name": a.get("name", aid),
            "avatar": a.get("avatar", ""),
            "role": a.get("role", ""),
            "total_messages": total_msgs,
            "thumbs_up": up,
            "thumbs_down": down,
            "total_feedback": total_fb,
            "satisfaction_rate": satisfaction,
            "feedback_rate": round((total_fb / total_msgs * 100), 1) if total_msgs > 0 else 0,
        })

    performance.sort(key=lambda x: (x["satisfaction_rate"] or 0, x["total_messages"]), reverse=True)
    return performance

# ============== REAL-TIME ACTIVITY FEED ==============

@router.get("/admin/activity-feed")
async def admin_activity_feed(limit: int = 30, admin: User = Depends(require_admin)):
    """Get recent platform activity events for the live feed."""
    events = []

    # Recent signups
    recent_users = await db.users.find(
        {}, {"_id": 0, "user_id": 1, "name": 1, "email": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    for u in recent_users:
        events.append({
            "type": "signup",
            "icon": "user-plus",
            "title": "New user signed up",
            "detail": u.get("name") or u.get("email", "Unknown"),
            "timestamp": u.get("created_at", ""),
        })

    # Recent payments
    recent_payments = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "email": 1, "amount": 1, "currency": 1, "type": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    for p in recent_payments:
        curr = "$" if p.get("currency", "usd") == "usd" else "৳"
        events.append({
            "type": "payment",
            "icon": "dollar-sign",
            "title": f"Payment received: {curr}{p.get('amount', 0):.2f}",
            "detail": f"{p.get('email', 'Unknown')} — {p.get('type', 'subscription')}",
            "timestamp": p.get("created_at", ""),
        })

    # Recent chats created
    recent_chats = await db.chats.find(
        {}, {"_id": 0, "chat_id": 1, "user_id": 1, "agent_id": 1, "title": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    agent_map = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1}).to_list(200)
    for a in all_agents:
        agent_map[a["agent_id"]] = a.get("name", a["agent_id"])
    user_map = {}
    user_ids = list(set(c.get("user_id") for c in recent_chats if c.get("user_id")))
    if user_ids:
        user_docs = await db.users.find({"user_id": {"$in": user_ids}}, {"_id": 0, "user_id": 1, "name": 1}).to_list(500)
        for ud in user_docs:
            user_map[ud["user_id"]] = ud.get("name", "Unknown")
    for c in recent_chats:
        agent_name = agent_map.get(c.get("agent_id"), "Unknown Agent")
        user_name = user_map.get(c.get("user_id"), "Unknown User")
        events.append({
            "type": "chat",
            "icon": "message-square",
            "title": f"Chat started with {agent_name}",
            "detail": user_name,
            "timestamp": c.get("created_at", ""),
        })

    # Recent team creations
    recent_teams = await db.teams.find(
        {}, {"_id": 0, "name": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(10)
    for t in recent_teams:
        events.append({
            "type": "team",
            "icon": "users",
            "title": f"Team created: {t.get('name', 'Unnamed')}",
            "detail": "",
            "timestamp": t.get("created_at", ""),
        })

    # Sort all events by timestamp descending
    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    return events[:limit]

# ============== BRANDING & WHITE-LABEL ==============

@router.get("/admin/branding")
async def get_branding(admin: User = Depends(require_admin)):
    """Get current branding configuration."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    defaults = {
        "config_type": "branding",
        "platform_name": "MAARS Command",
        "tagline": "AI-Powered Team Platform",
        "logo_url": "",
        "favicon_url": "",
        "primary_color": "#6366f1",
        "accent_color": "#8b5cf6",
        "custom_domain": "",
        "custom_domain_status": "not_configured",
        "footer_text": "MAARS Global Corporation",
        "support_email": "",
    }
    if config:
        defaults.update({k: v for k, v in config.items() if v is not None})
    return defaults

@router.post("/admin/branding")
async def update_branding(request: Request, admin: User = Depends(require_admin)):
    """Update branding and white-label settings."""
    data = await request.json()
    allowed_fields = {
        "platform_name", "tagline", "logo_url", "favicon_url",
        "primary_color", "accent_color", "custom_domain",
        "footer_text", "support_email"
    }
    update = {k: v for k, v in data.items() if k in allowed_fields}
    if not update:
        raise HTTPException(400, "No valid fields to update")

    # If custom domain changed, set status
    if "custom_domain" in update:
        domain = update["custom_domain"].strip()
        update["custom_domain"] = domain
        update["custom_domain_status"] = "pending_verification" if domain else "not_configured"
        update["custom_domain_updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.platform_config.update_one(
        {"config_type": "branding"},
        {"$set": {**update, "config_type": "branding", "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return await get_branding(admin)

@router.post("/admin/branding/upload-logo")
async def upload_branding_logo(file: UploadFile = File(...), admin: User = Depends(require_admin)):
    """Upload logo or favicon for branding. Returns the file URL."""
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "Logo file too large. Max 5MB.")
    allowed_ext = {"png", "jpg", "jpeg", "svg", "webp", "ico"}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_ext:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed_ext)}")
    file_id = uuid.uuid4().hex[:10]
    saved_filename = f"brand_{file_id}.{ext}"
    saved_path = UPLOAD_DIR / saved_filename
    with open(saved_path, 'wb') as f:
        f.write(contents)
    return {"url": f"/api/files/{saved_filename}", "filename": saved_filename}

@router.post("/admin/branding/verify-domain")
async def verify_custom_domain(request: Request, admin: User = Depends(require_admin)):
    """Check DNS status of the configured custom domain."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    domain = config.get("custom_domain", "") if config else ""
    if not domain:
        raise HTTPException(400, "No custom domain configured")
    status = "pending_verification"
    dns_result = None
    try:
        result = socket.getaddrinfo(domain, None)
        dns_result = result[0][4][0] if result else None
        status = "verified" if dns_result else "pending_verification"
    except socket.gaierror:
        status = "dns_not_found"
    except Exception:
        status = "verification_error"
    await db.platform_config.update_one(
        {"config_type": "branding"},
        {"$set": {"custom_domain_status": status, "custom_domain_verified_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"domain": domain, "status": status, "dns_result": dns_result}

@router.get("/branding/public")
async def get_public_branding():
    """Public endpoint for branding (no auth) — used by frontend to apply customization."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    defaults = {
        "platform_name": "MAARS Command",
        "tagline": "AI-Powered Team Platform",
        "logo_url": "",
        "favicon_url": "",
        "primary_color": "#6366f1",
        "accent_color": "#8b5cf6",
        "footer_text": "MAARS Global Corporation",
    }
    if config:
        for k in defaults:
            if config.get(k):
                defaults[k] = config[k]
    return defaults

@router.get("/admin/analytics/export")
async def admin_analytics_export(format: str = "csv", admin: User = Depends(require_admin)):
    """Export analytics data as CSV."""

    now = datetime.now(timezone.utc)

    # Users
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1, "email": 1, "created_at": 1}).to_list(5000)

    # Subscriptions
    subs = await db.subscriptions.find({}, {"_id": 0, "user_id": 1, "plan_id": 1, "credits": 1, "credits_used": 1, "status": 1}).to_list(5000)
    sub_map = {s["user_id"]: s for s in subs}

    # Agent usage
    agent_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    agent_usage = await db.chats.aggregate(agent_pipeline).to_list(50)
    agent_names = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1}).to_list(200)
    for a in all_agents:
        agent_names[a["agent_id"]] = a.get("name", a["agent_id"])

    # Payment transactions
    txns = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "email": 1, "amount": 1, "currency": 1, "type": 1, "created_at": 1}
    ).to_list(5000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Sheet 1: Users
    writer.writerow(["=== USERS ==="])
    writer.writerow(["User ID", "Name", "Email", "Signed Up", "Plan", "Credits", "Credits Used"])
    for u in users:
        s = sub_map.get(u["user_id"], {})
        writer.writerow([u["user_id"], u.get("name", ""), u.get("email", ""), u.get("created_at", ""), s.get("plan_id", "free"), s.get("credits", 0), s.get("credits_used", 0)])

    writer.writerow([])
    writer.writerow(["=== AGENT USAGE ==="])
    writer.writerow(["Agent", "Messages"])
    for au in agent_usage:
        writer.writerow([agent_names.get(au["_id"], au["_id"]), au["count"]])

    writer.writerow([])
    writer.writerow(["=== PAYMENTS ==="])
    writer.writerow(["Email", "Amount", "Currency", "Type", "Date"])
    for t in txns:
        writer.writerow([t.get("email", ""), t.get("amount", 0), t.get("currency", "usd"), t.get("type", ""), t.get("created_at", "")])

    writer.writerow([])
    writer.writerow(["=== SUMMARY ==="])
    writer.writerow(["Total Users", len(users)])
    writer.writerow(["Total Paid Transactions", len(txns)])
    writer.writerow(["Total Revenue", sum(t.get("amount", 0) for t in txns)])
    writer.writerow(["Report Generated", now.isoformat()])

    csv_content = output.getvalue()
    output.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=maars_analytics_{now.strftime('%Y%m%d')}.csv"}
    )



# ============== ADMIN AGENT MANAGEMENT ==============

@router.put("/admin/agents/{agent_id}/settings")
async def admin_update_agent_settings(agent_id: str, body: dict = Body(...), admin: User = Depends(require_admin)):
    """Update agent settings including generation permissions"""
    allowed_fields = {"can_generate_image", "can_generate_video", "can_generate_pdf", "can_generate_files", "system_prompt", "capabilities", "is_active"}
    update = {k: v for k, v in body.items() if k in allowed_fields}
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    result = await db.agents.update_one({"agent_id": agent_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "updated": list(update.keys())}

@router.put("/admin/agents/{agent_id}/brain")
async def admin_update_agent_brain(agent_id: str, body: dict = Body(...), admin: User = Depends(require_admin)):
    """Update agent brain configuration."""
    agent = await db.agents.find_one({"agent_id": agent_id})
    if not agent:
        raise HTTPException(404, "Agent not found")
    allowed = {"name", "role", "description", "system_prompt", "personality_tone", "expertise_areas", "dos", "donts", "example_responses", "knowledge_base", "model_provider", "model_name", "temperature", "max_tokens"}
    update = {k: v for k, v in body.items() if k in allowed}
    if not update:
        raise HTTPException(400, "No valid fields")
    brain_fields = {"personality_tone", "expertise_areas", "dos", "donts", "knowledge_base"}
    if brain_fields.intersection(update.keys()):
        tone = update.get("personality_tone", agent.get("personality_tone", ""))
        expertise = update.get("expertise_areas", agent.get("expertise_areas", ""))
        dos = update.get("dos", agent.get("dos", ""))
        donts = update.get("donts", agent.get("donts", ""))
        knowledge = update.get("knowledge_base", agent.get("knowledge_base", ""))
        brain_prompt_parts = [agent.get("system_prompt", "").split("\n\n--- BRAIN CONFIG ---")[0].strip()]
        brain_config = []
        if tone: brain_config.append(f"Personality & Tone: {tone}")
        if expertise: brain_config.append(f"Expertise Areas: {expertise}")
        if dos: brain_config.append(f"Always do: {dos}")
        if donts: brain_config.append(f"Never do: {donts}")
        if knowledge: brain_config.append(f"Knowledge Base: {knowledge}")
        if brain_config:
            brain_prompt_parts.append("\n\n--- BRAIN CONFIG ---\n" + "\n".join(brain_config))
        update["system_prompt"] = "\n".join(brain_prompt_parts)
    await db.agents.update_one({"agent_id": agent_id}, {"$set": update})
    updated_agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    return {"success": True, "agent": updated_agent}

@router.get("/admin/agents/{agent_id}")
async def admin_get_agent_detail(agent_id: str, admin: User = Depends(require_admin)):
    """Get full agent details for brain editor."""
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent



# ============== ADMIN AUDIT LOG ==============

@router.get("/admin/audit-log")
async def admin_get_audit_log(limit: int = 50, admin: User = Depends(require_admin)):
    """Get recent admin audit log entries."""
    logs = await db.audit_log.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return logs


async def log_admin_action(admin_email: str, action: str, details: dict = None):
    """Record an admin action to the audit log."""
    await db.audit_log.insert_one({
        "admin_email": admin_email,
        "action": action,
        "details": details or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    })


# ============== ENHANCED ANALYTICS ==============

@router.get("/admin/analytics/retention")
async def admin_retention_analytics(admin: User = Depends(require_admin)):
    """User retention cohort analysis - weekly cohorts for the last 8 weeks."""
    now = datetime.now(timezone.utc)
    cohorts = []

    for week_offset in range(8):
        cohort_start = now - timedelta(weeks=week_offset + 1)
        cohort_end = now - timedelta(weeks=week_offset)
        cohort_start_str = cohort_start.isoformat()
        cohort_end_str = cohort_end.isoformat()

        # Users who signed up in this week
        signed_up = await db.users.find(
            {"created_at": {"$gte": cohort_start_str, "$lt": cohort_end_str}},
            {"_id": 0, "user_id": 1}
        ).to_list(500)
        signed_up_ids = [u["user_id"] for u in signed_up]

        if not signed_up_ids:
            cohorts.append({
                "week": f"W-{week_offset + 1}",
                "week_start": cohort_start.strftime("%b %d"),
                "signed_up": 0,
                "returned_week1": 0,
                "returned_week2": 0,
                "retention_rate": 0
            })
            continue

        # How many returned (sent a message) in the following week
        next_week_start = cohort_end.isoformat()
        next_week_end = (cohort_end + timedelta(weeks=1)).isoformat()
        returned_chats = await db.chats.distinct(
            "user_id",
            {"user_id": {"$in": signed_up_ids}, "created_at": {"$gte": next_week_start, "$lt": next_week_end}}
        )

        # Week 2 retention
        week2_start = next_week_end
        week2_end = (cohort_end + timedelta(weeks=2)).isoformat()
        returned_w2 = await db.chats.distinct(
            "user_id",
            {"user_id": {"$in": signed_up_ids}, "created_at": {"$gte": week2_start, "$lt": week2_end}}
        )

        retention = round(len(returned_chats) / len(signed_up_ids) * 100) if signed_up_ids else 0
        cohorts.append({
            "week": f"W-{week_offset + 1}",
            "week_start": cohort_start.strftime("%b %d"),
            "signed_up": len(signed_up_ids),
            "returned_week1": len(returned_chats),
            "returned_week2": len(returned_w2),
            "retention_rate": retention
        })

    cohorts.reverse()  # oldest first
    return cohorts


@router.get("/admin/analytics/projections")
async def admin_revenue_projections(admin: User = Depends(require_admin)):
    """Revenue projections based on current trends."""
    now = datetime.now(timezone.utc)

    # Get last 30 days revenue
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    recent_txns = await db.payment_transactions.find(
        {"payment_status": "paid", "created_at": {"$gte": thirty_days_ago}},
        {"_id": 0, "amount": 1, "created_at": 1}
    ).to_list(5000)

    total_30d = sum(t.get("amount", 0) for t in recent_txns)
    daily_avg = total_30d / 30 if total_30d else 0

    # Current MRR
    from shared.constants import SUBSCRIPTION_PLANS
    subs = await db.subscriptions.find({"status": "active"}, {"_id": 0, "plan_id": 1}).to_list(1000)
    mrr = sum(SUBSCRIPTION_PLANS.get(s.get("plan_id", "free"), {}).get("price_usd", 0) for s in subs)

    # Credit consumption rate
    credit_logs = await db.usage_logs.find(
        {"created_at": {"$gte": thirty_days_ago}},
        {"_id": 0, "estimated_cost_usd": 1}
    ).to_list(10000)
    total_cost_30d = sum(l.get("estimated_cost_usd", 0) for l in credit_logs)
    daily_cost_avg = total_cost_30d / 30 if total_cost_30d else 0

    # Growth rate (users)
    sixty_days_ago = (now - timedelta(days=60)).isoformat()
    users_last_30d = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    users_prev_30d = await db.users.count_documents(
        {"created_at": {"$gte": sixty_days_ago, "$lt": thirty_days_ago}}
    )
    growth_rate = ((users_last_30d - users_prev_30d) / max(users_prev_30d, 1)) * 100

    # Projections
    projections = []
    for month in range(1, 7):
        projected_users_growth = 1 + (growth_rate / 100) * month
        proj_mrr = mrr * projected_users_growth
        proj_revenue = (daily_avg * 30) * projected_users_growth
        proj_cost = (daily_cost_avg * 30) * projected_users_growth
        month_label = (now + timedelta(days=30 * month)).strftime("%b %Y")
        projections.append({
            "month": month_label,
            "projected_mrr": round(proj_mrr, 2),
            "projected_revenue": round(proj_revenue, 2),
            "projected_cost": round(proj_cost, 2),
            "projected_profit": round(proj_revenue - proj_cost, 2),
        })

    return {
        "current": {
            "mrr": round(mrr, 2),
            "revenue_30d": round(total_30d, 2),
            "cost_30d": round(total_cost_30d, 4),
            "daily_revenue_avg": round(daily_avg, 2),
            "daily_cost_avg": round(daily_cost_avg, 4),
            "user_growth_rate": round(growth_rate, 1),
            "profit_margin": round(((total_30d - total_cost_30d) / max(total_30d, 0.01)) * 100, 1)
        },
        "projections": projections
    }


@router.get("/admin/analytics/credit-burn")
async def admin_credit_burn_rate(admin: User = Depends(require_admin)):
    """Credit consumption trends by model and agent."""
    now = datetime.now(timezone.utc)
    seven_days_ago = (now - timedelta(days=7)).isoformat()
    thirty_days_ago = (now - timedelta(days=30)).isoformat()

    # By model (last 30d)
    model_pipeline = [
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": "$model",
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"},
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": 15}
    ]
    by_model = await db.usage_logs.aggregate(model_pipeline).to_list(15)

    # By agent (last 30d)
    agent_pipeline = [
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": "$agent_id",
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": 15}
    ]
    by_agent_raw = await db.usage_logs.aggregate(agent_pipeline).to_list(15)

    # Enrich with agent names
    agent_map = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1}).to_list(100)
    for a in all_agents:
        agent_map[a["agent_id"]] = a.get("name", a["agent_id"])

    by_agent = [{
        "agent_id": a["_id"],
        "agent_name": agent_map.get(a["_id"], a["_id"] or "Unknown"),
        "total_cost": round(a["total_cost"], 4),
        "total_calls": a["total_calls"],
        "avg_cost_per_call": round(a["total_cost"] / max(a["total_calls"], 1), 6)
    } for a in by_agent_raw]

    # Daily burn rate (last 7d)
    daily_pipeline = [
        {"$match": {"created_at": {"$gte": seven_days_ago}}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_burn = await db.usage_logs.aggregate(daily_pipeline).to_list(7)

    return {
        "by_model": [{
            "model": m["_id"] or "unknown",
            "total_cost": round(m["total_cost"], 4),
            "total_calls": m["total_calls"],
            "input_tokens": m.get("total_input_tokens", 0),
            "output_tokens": m.get("total_output_tokens", 0),
            "avg_cost_per_call": round(m["total_cost"] / max(m["total_calls"], 1), 6)
        } for m in by_model],
        "by_agent": by_agent,
        "daily_burn": [{
            "date": d["_id"],
            "cost": round(d["cost"], 4),
            "calls": d["calls"]
        } for d in daily_burn]
    }


# ============== ENHANCED ANALYTICS - PHASE 3 ==============

@router.get("/admin/analytics/agent-leaderboard")
async def admin_agent_leaderboard(admin: User = Depends(require_admin)):
    """Agent performance leaderboard - most used, best rated, fastest."""
    pipeline = [
        {"$group": {
            "_id": "$agent_id",
            "total_chats": {"$sum": 1},
            "total_messages": {"$sum": {"$size": {"$ifNull": ["$messages", []]}}},
            "last_used": {"$max": "$updated_at"},
        }},
        {"$sort": {"total_chats": -1}}
    ]
    usage = await db.chats.aggregate(pipeline).to_list(50)
    
    agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1}).to_list(200)
    agent_map = {a["agent_id"]: a for a in agents}
    
    # Get feedback stats
    feedback_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.feedback": {"$exists": True}}},
        {"$group": {
            "_id": "$agent_id",
            "positive": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "up"]}, 1, 0]}},
            "negative": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "down"]}, 1, 0]}},
            "total_feedback": {"$sum": 1}
        }}
    ]
    feedback = await db.chats.aggregate(feedback_pipeline).to_list(50)
    feedback_map = {f["_id"]: f for f in feedback}
    
    leaderboard = []
    for u in usage:
        aid = u["_id"]
        agent = agent_map.get(aid, {})
        fb = feedback_map.get(aid, {})
        positive = fb.get("positive", 0)
        total_fb = fb.get("total_feedback", 0)
        satisfaction = round((positive / max(total_fb, 1)) * 100, 1)
        leaderboard.append({
            "agent_id": aid,
            "name": agent.get("name", aid),
            "avatar": agent.get("avatar", ""),
            "role": agent.get("role", ""),
            "total_chats": u["total_chats"],
            "total_messages": u["total_messages"],
            "satisfaction_pct": satisfaction,
            "positive_feedback": positive,
            "negative_feedback": fb.get("negative", 0),
            "last_used": u.get("last_used", ""),
        })
    
    return {"leaderboard": leaderboard}


@router.get("/admin/analytics/engagement-heatmap")
async def admin_engagement_heatmap(admin: User = Depends(require_admin)):
    """User activity heatmap - messages by hour and day of week."""
    pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "user"}},
        {"$project": {
            "timestamp": "$messages.created_at"
        }}
    ]
    raw = await db.chats.aggregate(pipeline).to_list(10000)
    
    heatmap = [[0]*24 for _ in range(7)]  # 7 days x 24 hours
    for r in raw:
        ts = r.get("timestamp", "")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00")) if isinstance(ts, str) else ts
            heatmap[dt.weekday()][dt.hour] += 1
        except Exception:
            continue
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    result = []
    for d_idx, day in enumerate(days):
        for h in range(24):
            if heatmap[d_idx][h] > 0:
                result.append({"day": day, "hour": h, "count": heatmap[d_idx][h]})
    
    max_count = max((r["count"] for r in result), default=1)
    for r in result:
        r["intensity"] = round(r["count"] / max(max_count, 1), 2)
    
    return {"heatmap": result, "days": days, "max_count": max_count}


@router.get("/admin/analytics/revenue-trends")
async def admin_revenue_trends(days: int = 30, admin: User = Depends(require_admin)):
    """Revenue trends with growth rates."""
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days)).isoformat()
    
    pipeline = [
        {"$match": {"created_at": {"$gte": start}, "payment_status": "paid"}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "revenue": {"$sum": "$amount"},
            "transactions": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily = await db.payment_transactions.aggregate(pipeline).to_list(days)
    
    trends = []
    for i, d in enumerate(daily):
        prev_rev = daily[i-1]["revenue"] if i > 0 else d["revenue"]
        growth = round(((d["revenue"] - prev_rev) / max(prev_rev, 0.01)) * 100, 1) if i > 0 else 0
        cumulative = sum(dd["revenue"] for dd in daily[:i+1])
        trends.append({
            "date": d["_id"],
            "revenue": round(d["revenue"], 2),
            "transactions": d["transactions"],
            "growth_pct": growth,
            "cumulative": round(cumulative, 2),
        })
    
    total = sum(d["revenue"] for d in daily)
    avg_daily = total / max(len(daily), 1)
    
    return {
        "trends": trends,
        "summary": {
            "total_revenue": round(total, 2),
            "avg_daily_revenue": round(avg_daily, 2),
            "total_transactions": sum(d["transactions"] for d in daily),
            "period_days": days,
        }
    }


# ─────────────────────────────────────────────
# Client Visibility Settings
# ─────────────────────────────────────────────

@router.get("/admin/nav-visibility")
async def get_nav_visibility(admin: User = Depends(require_admin)):
    """Get which nav pages are visible to clients."""
    config = await db.platform_config.find_one({"config_type": "nav_visibility"}, {"_id": 0})
    if not config:
        return {"visibility": {}}
    return {"visibility": config.get("visibility", {})}


@router.put("/admin/nav-visibility")
async def update_nav_visibility(request: Request, admin: User = Depends(require_admin)):
    """Update which nav pages are visible to clients."""
    body = await request.json()
    visibility = body.get("visibility", {})
    await db.platform_config.update_one(
        {"config_type": "nav_visibility"},
        {"$set": {"config_type": "nav_visibility", "visibility": visibility}},
        upsert=True,
    )
    return {"success": True}


@router.get("/admin/nav-visibility/public")
async def get_nav_visibility_public():
    """Public endpoint — returns client nav visibility (no auth needed)."""
    config = await db.platform_config.find_one({"config_type": "nav_visibility"}, {"_id": 0})
    if not config:
        return {"visibility": {}}
    return {"visibility": config.get("visibility", {})}


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL GATEWAY ADMIN ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/admin/gateway/stats")
async def admin_gateway_stats(current_user: User = Depends(require_admin)):
    """Admin-only: aggregated Universal Gateway usage stats across ALL users."""
    logs = await db.llm_usage_logs.find(
        {"source": "universal_gateway"},
        {"_id": 0}
    ).sort("timestamp", -1).limit(5000).to_list(5000)

    total_calls   = len(logs)
    total_cost    = round(sum(l.get("cost_usd", 0) for l in logs), 6)
    total_credits = sum(l.get("credits_used", 0) for l in logs)
    fallback_cnt  = sum(1 for l in logs if l.get("fallback_used"))
    avg_latency   = round(sum(l.get("latency_ms", 0) for l in logs) / max(total_calls, 1), 1)

    by_provider: dict = {}
    by_tier:     dict = {}
    by_task:     dict = {}
    by_budget:   dict = {}
    by_user:     dict = {}

    for l in logs:
        p  = l.get("provider", "unknown")
        t  = l.get("quality_tier", "standard")
        tt = l.get("task_type", "general")
        b  = l.get("credit_budget", "normal")
        u  = l.get("user_id", "unknown")
        by_provider[p]  = by_provider.get(p, 0) + 1
        by_tier[t]      = by_tier.get(t, 0) + 1
        by_task[tt]     = by_task.get(tt, 0) + 1
        by_budget[b]    = by_budget.get(b, 0) + 1
        by_user[u]      = by_user.get(u, 0) + 1

    # Top 10 users by gateway calls
    top_users = sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_calls":           total_calls,
        "total_cost_usd":        total_cost,
        "total_credits_used":    total_credits,
        "avg_latency_ms":        avg_latency,
        "fallback_count":        fallback_cnt,
        "fallback_rate_pct":     round(fallback_cnt / max(total_calls, 1) * 100, 1),
        "avg_cost_per_call_usd": round(total_cost / max(total_calls, 1), 8),
        "calls_by_provider":     by_provider,
        "calls_by_tier":         by_tier,
        "calls_by_task_type":    by_task,
        "calls_by_credit_budget":by_budget,
        "top_users_by_calls":    [{"user_id": u, "calls": c} for u, c in top_users],
    }


@router.get("/admin/gateway/logs")
async def admin_gateway_logs(
    limit: int = 50,
    current_user: User = Depends(require_admin)
):
    """Admin-only: last N routing decisions across all users."""
    limit = min(max(limit, 1), 200)
    logs = await db.llm_usage_logs.find(
        {"source": "universal_gateway"},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)

    # Enrich with user email where possible
    user_ids = list({l.get("user_id") for l in logs if l.get("user_id")})
    user_docs = await db.users.find(
        {"user_id": {"$in": user_ids}}, {"_id": 0, "user_id": 1, "email": 1, "name": 1}
    ).to_list(len(user_ids))
    user_map = {u["user_id"]: u for u in user_docs}

    result = []
    for l in logs:
        uid = l.get("user_id", "")
        u = user_map.get(uid, {})
        result.append({
            "log_id":         l.get("log_id", ""),
            "timestamp":      l.get("timestamp", ""),
            "user_id":        uid,
            "user_email":     u.get("email", ""),
            "user_name":      u.get("name", ""),
            "provider":       l.get("provider", ""),
            "model":          l.get("model", ""),
            "quality_tier":   l.get("quality_tier", ""),
            "task_type":      l.get("task_type", "general"),
            "task_complexity":l.get("task_complexity", ""),
            "credit_budget":  l.get("credit_budget", ""),
            "credits_used":   l.get("credits_used", 0),
            "cost_usd":       l.get("cost_usd", 0),
            "latency_ms":     l.get("latency_ms", 0),
            "attempts":       l.get("attempts", 1),
            "fallback_used":  l.get("fallback_used", False),
            "prompt_words":   l.get("prompt_words", 0),
        })

    return {"logs": result, "count": len(result)}


@router.get("/admin/gateway/health")
async def admin_gateway_health(current_user: User = Depends(require_admin)):
    """Admin-only: provider key configuration status for all 19 gateway providers."""
    api_keys = await get_api_keys()

    ALL_PROVIDERS = [
        {"id": "openai",     "name": "OpenAI",          "models": ["GPT-5", "GPT-4.1", "O4"]},
        {"id": "anthropic",  "name": "Anthropic",        "models": ["Claude Opus 4.6", "Claude Sonnet 4.6"]},
        {"id": "gemini",     "name": "Google Gemini",    "models": ["Gemini 2.5 Pro", "Gemini 2.5 Flash"]},
        {"id": "xai",        "name": "xAI (Grok)",       "models": ["Grok 3", "Grok 3 Mini"]},
        {"id": "deepseek",   "name": "DeepSeek",         "models": ["DeepSeek V3", "DeepSeek R1"]},
        {"id": "mistral",    "name": "Mistral AI",       "models": ["Mistral Large", "Codestral"]},
        {"id": "perplexity", "name": "Perplexity",       "models": ["Sonar Pro", "Sonar Deep Research"]},
        {"id": "cohere",     "name": "Cohere",           "models": ["Command A", "Command R+"]},
        {"id": "groq",       "name": "Groq",             "models": ["Llama 4 Scout", "Llama 4 Maverick"]},
        {"id": "cerebras",   "name": "Cerebras",         "models": ["Llama 3.3 70B", "Llama 3.1 70B"]},
        {"id": "together",   "name": "Together AI",      "models": ["Llama 4 Maverick FP8", "DeepSeek R1"]},
        {"id": "fireworks",  "name": "Fireworks AI",     "models": ["Llama 4 Scout", "DeepSeek V3"]},
        {"id": "ai21",       "name": "AI21 (Jamba)",     "models": ["Jamba Large 1.7", "Jamba Mini 1.7"]},
        {"id": "sambanova",  "name": "SambaNova",        "models": ["Llama 4 Maverick", "DeepSeek R1-0528"]},
        {"id": "novita",     "name": "Novita AI",         "models": ["Llama 4 Scout", "Qwen3-235B", "DeepSeek R1"]},
        {"id": "lepton",     "name": "Lepton AI",         "models": ["Llama 4 Maverick", "DeepSeek R1-0528"]},
        {"id": "lambda",     "name": "Lambda Labs",       "models": ["Llama 4 Scout", "Hermes 3 405B"]},
        {"id": "minimax",    "name": "Minimax AI",        "models": ["MiniMax-Text-01", "MiniMax-VL-01"]},
        {"id": "inception",  "name": "Inception AI",      "models": ["Mercury Coder Small", "Mercury Coder Large"]},
        {"id": "arcee",      "name": "Arcee AI",          "models": ["Arcee Maestro", "Arcee Blaze"]},
        {"id": "amazon",     "name": "Amazon Bedrock",    "models": ["Nova Pro", "Nova Lite", "Nova Micro"]},
        {"id": "nvidia",     "name": "Nvidia NIM",       "models": ["Nemotron Ultra 253B", "Nemotron Super 49B"]},
        {"id": "moonshot",   "name": "Moonshot (Kimi)",  "models": ["Kimi Auto", "Kimi 128K"]},
        {"id": "qwen",       "name": "Qwen / Alibaba",   "models": ["Qwen Max", "QwQ-32B"]},
        {"id": "elevenlabs", "name": "ElevenLabs (TTS)", "models": ["Multilingual v2", "Turbo v2.5"]},
    ]

    has_emergent = bool(api_keys.get("emergent", ""))

    providers = []
    configured_count = 0
    for p in ALL_PROVIDERS:
        has_key = bool(api_keys.get(p["id"], ""))
        # openai/anthropic/gemini can also use emergent key
        can_use_emergent = p["id"] in ("openai", "anthropic", "gemini") and has_emergent
        is_active = has_key or can_use_emergent
        if is_active:
            configured_count += 1
        providers.append({
            **p,
            "has_direct_key":   has_key,
            "can_use_emergent": can_use_emergent,
            "is_active":        is_active,
            "key_source":       "direct" if has_key else ("emergent" if can_use_emergent else "none"),
        })

    return {
        "providers": providers,
        "configured_count": configured_count,
        "total_providers":  19,
        "has_emergent_key": has_emergent,
        "gateway_ready":    configured_count >= 1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT GATEWAY KEY MANAGEMENT  (admin-only)
# Each client gets one MAARS API key auto-generated on registration/subscription.
# Keys are invisible to clients — admin manages them all from here.
# Budget = monthly_cap_usd from their plan (the AI cost slice of their subscription).
# Profit = plan_price_usd - monthly_cap_usd (your margin, tracked per billing cycle).
# ─────────────────────────────────────────────────────────────────────────────

def _generate_maars_key() -> str:
    """Generate a MAARS API key: maars-sk- + 40 hex chars."""
    import secrets
    return f"maars-sk-{secrets.token_hex(20)}"


async def _ensure_client_key(user_id: str, plan_id: str = "free") -> dict:
    """Get or create the gateway key record for a user."""
    existing = await db.client_gateway_keys.find_one({"user_id": user_id}, {"_id": 0})
    if existing:
        return existing
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    doc = {
        "user_id":           user_id,
        "key":               _generate_maars_key(),
        "plan_id":           plan_id,
        "monthly_budget_usd": plan.get("monthly_cap_usd", 0.0),
        "used_usd":          0.0,
        "cycle_start":       datetime.now(timezone.utc).isoformat(),
        "status":            "active",
        "created_at":        datetime.now(timezone.utc).isoformat(),
        "notes":             "",
    }
    await db.client_gateway_keys.insert_one(doc)
    return doc


@router.get("/admin/gateway/client-keys")
async def admin_list_client_keys(
    search: str = "",
    current_user: User = Depends(require_admin)
):
    """Admin: list all client gateway keys with spend, budget, and profit data."""
    # Fetch all users
    query = {}
    if search:
        query["$or"] = [
            {"name":  {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).to_list(500)

    result = []
    for u in users:
        uid = u["user_id"]
        # Get subscription
        sub = await db.subscriptions.find_one({"user_id": uid}, {"_id": 0}) or {}
        plan_id = sub.get("plan_id", "free")
        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free", {}))

        # Get or create key record
        key_doc = await _ensure_client_key(uid, plan_id)

        # Recalculate actual spend from llm_usage_logs this cycle
        cycle_start = key_doc.get("cycle_start", "")
        spend_pipeline = [
            {"$match": {"user_id": uid, "timestamp": {"$gte": cycle_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$cost_usd"}, "calls": {"$sum": 1}}},
        ]
        spend_agg = await db.llm_usage_logs.aggregate(spend_pipeline).to_list(1)
        actual_spend = round((spend_agg[0]["total"] if spend_agg else 0), 6)
        total_calls  = spend_agg[0]["calls"] if spend_agg else 0

        monthly_budget  = key_doc.get("monthly_budget_usd", 0.0)
        plan_price_usd  = plan.get("price_usd", 0.0)
        # Profit = subscription revenue - AI budget allocation
        # If actual spend < budget, the unused AI budget is also profit
        gross_margin    = round(plan_price_usd - monthly_budget, 4)
        ai_surplus      = round(max(monthly_budget - actual_spend, 0), 6)
        total_profit    = round(gross_margin + ai_surplus, 4)

        result.append({
            "user_id":          uid,
            "name":             u.get("name", ""),
            "email":            u.get("email", ""),
            "plan_id":          plan_id,
            "plan_name":        plan.get("name", plan_id.capitalize()),
            "plan_price_usd":   plan_price_usd,
            "key":              key_doc["key"],
            "key_status":       key_doc.get("status", "active"),
            "monthly_budget_usd": monthly_budget,
            "actual_spend_usd": actual_spend,
            "budget_remaining_usd": round(max(monthly_budget - actual_spend, 0), 6),
            "budget_used_pct":  round(actual_spend / monthly_budget * 100, 1) if monthly_budget > 0 else 0,
            "total_calls":      total_calls,
            "gross_margin_usd": gross_margin,
            "ai_surplus_usd":   ai_surplus,
            "total_profit_usd": total_profit,
            "cycle_start":      cycle_start,
            "notes":            key_doc.get("notes", ""),
            "created_at":       key_doc.get("created_at", ""),
        })

    # Platform totals
    total_revenue = sum(r["plan_price_usd"] for r in result)
    total_ai_cost = sum(r["actual_spend_usd"] for r in result)
    total_profit_all = sum(r["total_profit_usd"] for r in result)
    total_budget_alloc = sum(r["monthly_budget_usd"] for r in result)

    return {
        "clients": result,
        "count": len(result),
        "platform_totals": {
            "total_subscription_revenue_usd": round(total_revenue, 2),
            "total_ai_budget_allocated_usd":  round(total_budget_alloc, 4),
            "total_actual_ai_cost_usd":       round(total_ai_cost, 6),
            "total_profit_usd":               round(total_profit_all, 4),
            "overall_margin_pct":             round((total_profit_all / total_revenue * 100) if total_revenue > 0 else 0, 1),
        },
    }


@router.post("/admin/gateway/client-keys/{user_id}/regenerate")
async def admin_regenerate_client_key(
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """Admin: generate a new key for a specific client (invalidates the old one)."""
    new_key = _generate_maars_key()
    await db.client_gateway_keys.update_one(
        {"user_id": user_id},
        {"$set": {"key": new_key, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"user_id": user_id, "key": new_key, "status": "regenerated"}


@router.put("/admin/gateway/client-keys/{user_id}")
async def admin_update_client_key(
    user_id: str,
    body: dict = Body(...),
    current_user: User = Depends(require_admin)
):
    """Admin: update budget, status, or notes for a client key."""
    allowed = {"monthly_budget_usd", "status", "notes"}
    update = {k: v for k, v in body.items() if k in allowed}
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.client_gateway_keys.update_one(
        {"user_id": user_id},
        {"$set": update},
        upsert=True,
    )
    return {"user_id": user_id, "updated": list(update.keys())}


# ─────────────────────────────────────────────────────────────────────────────
# PAYG BILLING MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/admin/gateway/client-keys/{user_id}/billing")
async def admin_set_billing_mode(
    user_id: str,
    body: dict = Body(...),
    current_user: User = Depends(require_admin)
):
    """Admin: configure billing mode, markup, and balance for a client key.

    Fields:
      billing_mode  — "subscription" | "payg" | "hybrid"
      markup_pct    — float, margin % added on top of provider cost (e.g. 30 = 30%)
      monthly_budget_usd — subscription cap (used in subscription/hybrid modes)
      low_balance_threshold_usd — alert threshold for PAYG balance
      auto_topup_enabled — bool
    """
    allowed = {
        "billing_mode", "markup_pct", "monthly_budget_usd",
        "low_balance_threshold_usd", "auto_topup_enabled", "rpm_limit",
    }
    update = {k: v for k, v in body.items() if k in allowed}
    if "billing_mode" in update and update["billing_mode"] not in ("subscription", "payg", "hybrid"):
        raise HTTPException(status_code=400, detail="billing_mode must be 'subscription', 'payg', or 'hybrid'")
    if "markup_pct" in update:
        try:
            update["markup_pct"] = float(update["markup_pct"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="markup_pct must be a number")
        if not (0 <= update["markup_pct"] <= 500):
            raise HTTPException(status_code=400, detail="markup_pct must be between 0 and 500")
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.client_gateway_keys.find_one_and_update(
        {"user_id": user_id},
        {"$set": update},
        return_document=True,
        upsert=False,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"No gateway key for user {user_id}")
    await log_admin_action(current_user.email, "billing_mode_updated", {"user_id": user_id, "changes": update})
    return {
        "user_id":       user_id,
        "billing_mode":  result.get("billing_mode", "subscription"),
        "markup_pct":    result.get("markup_pct", 0.0),
        "balance_usd":   result.get("balance_usd", 0.0),
        "updated":       list(update.keys()),
    }


@router.post("/admin/gateway/client-keys/{user_id}/topup")
async def admin_topup_balance(
    user_id: str,
    body: dict = Body(...),
    current_user: User = Depends(require_admin)
):
    """Admin: add prepaid credit to a client's PAYG balance.

    Body: { "amount_usd": float, "note": str (optional) }
    """
    amount = body.get("amount_usd")
    if amount is None:
        raise HTTPException(status_code=400, detail="amount_usd is required")
    try:
        amount = round(float(amount), 6)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="amount_usd must be a number")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount_usd must be positive")

    result = await db.client_gateway_keys.find_one_and_update(
        {"user_id": user_id},
        {
            "$inc":  {"balance_usd": amount},
            "$set":  {"updated_at": datetime.now(timezone.utc).isoformat()},
        },
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"No gateway key for user {user_id}")

    # Write a topup transaction record
    await db.gateway_topups.insert_one({
        "topup_id":   f"tu_{user_id[:8]}_{int(datetime.now(timezone.utc).timestamp()*1000)}",
        "user_id":    user_id,
        "amount_usd": amount,
        "new_balance": result.get("balance_usd", 0.0),
        "note":       body.get("note", "Admin top-up"),
        "added_by":   current_user.email,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    })
    await log_admin_action(current_user.email, "balance_topup", {
        "user_id": user_id, "amount_usd": amount,
        "new_balance": result.get("balance_usd", 0.0)
    })
    return {
        "user_id":       user_id,
        "amount_added":  amount,
        "new_balance":   round(result.get("balance_usd", 0.0), 6),
        "billing_mode":  result.get("billing_mode", "subscription"),
    }


@router.get("/admin/gateway/payg-overview")
async def admin_payg_overview(current_user: User = Depends(require_admin)):
    """Admin: PAYG revenue overview — active PAYG/hybrid clients, balances, markup revenue."""
    payg_keys = await db.client_gateway_keys.find(
        {"billing_mode": {"$in": ["payg", "hybrid"]}},
        {"_id": 0}
    ).to_list(1000)

    total_balance   = round(sum(k.get("balance_usd", 0) for k in payg_keys), 4)
    total_markup_rev = 0.0

    # Aggregate markup revenue from usage logs this month
    from datetime import datetime, timezone
    cycle_floor = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0).isoformat()
    logs = await db.gateway_usage_logs.find(
        {"billing_mode": {"$in": ["payg", "hybrid"]}, "timestamp": {"$gte": cycle_floor}},
        {"cost_usd": 1, "billed_usd": 1, "_id": 0}
    ).to_list(50000)

    total_provider_cost = round(sum(l.get("cost_usd", 0) for l in logs), 6)
    total_billed        = round(sum(l.get("billed_usd", l.get("cost_usd", 0)) for l in logs), 6)
    total_markup_rev    = round(total_billed - total_provider_cost, 6)

    clients = []
    for k in payg_keys:
        clients.append({
            "user_id":      k.get("user_id"),
            "key_prefix":   k.get("key", "")[:16],
            "billing_mode": k.get("billing_mode"),
            "balance_usd":  round(k.get("balance_usd", 0), 4),
            "markup_pct":   k.get("markup_pct", 0.0),
            "used_usd":     round(k.get("used_usd", 0), 4),
            "total_calls":  k.get("total_calls", 0),
            "status":       k.get("status", "active"),
        })

    return {
        "object":               "payg_overview",
        "total_payg_clients":   len(payg_keys),
        "total_balance_held":   total_balance,
        "this_month": {
            "provider_cost_usd":  total_provider_cost,
            "billed_to_clients":  total_billed,
            "markup_revenue_usd": total_markup_rev,
            "call_count":         len(logs),
        },
        "clients": clients,
    }


@router.get("/admin/gateway/topups")
async def admin_topup_history(
    limit: int = 50,
    current_user: User = Depends(require_admin)
):
    """Admin: view top-up transaction history."""
    topups = await db.gateway_topups.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"object": "topup_list", "data": topups, "total": len(topups)}


@router.post("/admin/gateway/client-keys/provision-all")
async def admin_provision_all_keys(current_user: User = Depends(require_admin)):
    """Admin: backfill — ensure every existing user has a gateway key record."""
    users = await db.users.find({}, {"_id": 0, "user_id": 1}).to_list(10000)
    created = 0
    for u in users:
        uid = u["user_id"]
        sub = await db.subscriptions.find_one({"user_id": uid}, {"_id": 0}) or {}
        existing = await db.client_gateway_keys.find_one({"user_id": uid})
        if not existing:
            await _ensure_client_key(uid, sub.get("plan_id", "free"))
            created += 1
    return {"provisioned": created, "total_users": len(users)}


@router.post("/admin/gateway/playground")
async def admin_gateway_playground(request: Request, admin: User = Depends(require_admin)):
    """Admin playground — call gateway models using admin JWT."""
    from routes.v1_gateway import (
        _parse_model_id, _call_with_fallback, _extract_prompt_text,
        _stream_response, _MAARS_ALIASES, _resolve_maars_alias,
    )
    from shared.utils import get_api_keys

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    model_raw   = body.get("model", "maars/auto")
    messages    = body.get("messages", [{"role": "user", "content": "Hello"}])
    stream      = body.get("stream", False)
    params      = {}
    for p in ["temperature", "top_p", "max_tokens", "stop", "seed"]:
        val = body.get(p)
        if val is not None:
            params[p] = val
    if "max_tokens" not in params:
        params["max_tokens"] = 2048

    api_keys = await get_api_keys()
    prompt_text = _extract_prompt_text(messages)

    if model_raw in _MAARS_ALIASES:
        provider, native_id = await _resolve_maars_alias(model_raw, prompt_text, 100, api_keys)
    else:
        entry = _parse_model_id(model_raw)
        if not entry:
            raise HTTPException(status_code=400, detail=f"Unknown model: {model_raw}")
        _, provider, native_id, _, _ = entry

    api_key = api_keys.get(provider, "")

    if stream:
        from fastapi.responses import StreamingResponse
        async def gen():
            async for chunk in _stream_response(provider, native_id, "", messages, api_key, model_raw, params):
                yield chunk
        return StreamingResponse(gen(), media_type="text/event-stream",
                                  headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    import time as _time
    start = _time.time()
    data, actual_prov, actual_model, model_warning = await _call_with_fallback(
        provider, native_id, messages, api_key, params, api_keys
    )
    latency = int((_time.time() - start) * 1000)
    data["x_playground"] = {"actual_provider": actual_prov, "native_model": actual_model,
                             "latency_ms": latency, "model_warning": model_warning}
    return data
