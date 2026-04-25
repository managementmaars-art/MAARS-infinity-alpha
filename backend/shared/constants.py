"""Shared constants and configuration used across the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# LLM Settings

# Email Settings
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Direct API Keys (can be overridden from admin panel via DB)
# All 33 providers: 32 text/LLM + ElevenLabs voice/TTS
_BYTEZ_KEY = os.environ.get('BYTEZ_API_KEY', '')
_WRITER_KEY = os.environ.get('WRITER_API_KEY', '')

DIRECT_API_KEYS = {
    "bytez":        _BYTEZ_KEY,
    "writer":       _WRITER_KEY,
    # ── Flagship ─────────────────────────────────────────────────────────────
    "openai":     os.environ.get('OPENAI_API_KEY', ''),
    "anthropic":  os.environ.get('ANTHROPIC_API_KEY', ''),
    "gemini":     os.environ.get('GOOGLE_API_KEY', '') or os.environ.get('GEMINI_API_KEY', ''),
    "xai":        os.environ.get('XAI_API_KEY', ''),
    # ── Specialist ───────────────────────────────────────────────────────────
    "deepseek":   os.environ.get('DEEPSEEK_API_KEY', ''),
    "mistral":    os.environ.get('MISTRAL_API_KEY', ''),
    "perplexity": os.environ.get('PERPLEXITY_API_KEY', ''),
    "cohere":     os.environ.get('COHERE_API_KEY', ''),
    # ── Fast Open-Source ─────────────────────────────────────────────────────
    "groq":       os.environ.get('GROQ_API_KEY', ''),
    "cerebras":   os.environ.get('CEREBRAS_API_KEY', ''),
    "together":   os.environ.get('TOGETHER_API_KEY', ''),
    "fireworks":  os.environ.get('FIREWORKS_API_KEY', ''),
    "ai21":       os.environ.get('AI21_API_KEY', ''),
    "sambanova":  os.environ.get('SAMBANOVA_API_KEY', ''),
    # ── Established Providers ─────────────────────────────────────────────────
    "nvidia":     os.environ.get('NVIDIA_API_KEY', '') or os.environ.get('NVIDIA_NIM_API_KEY', ''),
    "moonshot":   os.environ.get('MOONSHOT_API_KEY', ''),
    "qwen":       os.environ.get('DASHSCOPE_API_KEY', '') or os.environ.get('QWEN_API_KEY', ''),
    # ── New Direct Providers (replacing OpenRouter) ───────────────────────────
    "novita":    os.environ.get('NOVITA_API_KEY', ''),
    "lepton":    os.environ.get('LEPTON_API_KEY', ''),
    "lambda":    os.environ.get('LAMBDA_API_KEY', '') or os.environ.get('LAMBDA_LABS_API_KEY', ''),
    "amazon":    os.environ.get('AMAZON_API_KEY', '') or os.environ.get('AWS_BEDROCK_API_KEY', '') or os.environ.get('AWS_ACCESS_KEY_ID', ''),
    "minimax":   os.environ.get('MINIMAX_API_KEY', ''),
    "inception": os.environ.get('INCEPTION_API_KEY', ''),
    "arcee":     os.environ.get('ARCEE_API_KEY', ''),
    "reka":      os.environ.get('REKA_API_KEY', ''),
    # ── Regional & Enterprise ─────────────────────────────────────────────────
    "yi":          os.environ.get('YI_API_KEY', '') or os.environ.get('ZERO_ONE_API_KEY', ''),
    "zhipu":       os.environ.get('ZHIPU_API_KEY', '') or os.environ.get('GLM_API_KEY', ''),
    "doubao":      os.environ.get('DOUBAO_API_KEY', '') or os.environ.get('VOLCENGINE_API_KEY', ''),
    "hyperbolic":  os.environ.get('HYPERBOLIC_API_KEY', ''),
    "upstage":     os.environ.get('UPSTAGE_API_KEY', '') or os.environ.get('SOLAR_API_KEY', ''),
    "writer":      os.environ.get('WRITER_API_KEY', '') or os.environ.get('PALMYRA_API_KEY', ''),
    "huggingface": os.environ.get('HUGGINGFACE_API_KEY', '') or os.environ.get('HF_TOKEN', ''),
    "llama":       os.environ.get('LLAMA_API_KEY', '') or os.environ.get('META_API_KEY', ''),
    # ── Meta-routers ─────────────────────────────────────────────────────────
    "openrouter": os.environ.get('OPENROUTER_API_KEY', ''),
    "bytez":      os.environ.get('BYTEZ_API_KEY', ''),
    # ── Voice / TTS ───────────────────────────────────────────────────────────
    "elevenlabs": os.environ.get('ELEVENLABS_API_KEY', ''),
    # ── Media / image / video / STT providers ─────────────────────────────────
    # Fal hosts 8+ video models (LTX, Kling, Veo, Hailuo, Pika, Luma, Mochi,
    # CogVideoX) + FLUX image + MusicGen. Setting this one key unlocks the
    # entire premium media catalog for $0.02-0.05 per generation.
    "fal":        os.environ.get('FAL_KEY', '') or os.environ.get('FAL_API_KEY', ''),
    # Deepgram Nova-2 gives 45,000 STT minutes/month FREE + ~300ms latency.
    # Primary STT path when configured; OpenAI Whisper remains fallback.
    "deepgram":   os.environ.get('DEEPGRAM_API_KEY', ''),
    # Replicate hosts everything — Runway, Pika, Kling, Suno, Musicgen,
    # SDXL, FLUX, etc. Optional, but fills gaps Fal doesn't cover.
    "replicate":  os.environ.get('REPLICATE_API_KEY', '') or os.environ.get('REPLICATE_API_TOKEN', ''),
    # Stability AI direct for SD3/SDXL image + SVD video.
    "stability":  os.environ.get('STABILITY_API_KEY', ''),
    # Optional: Ideogram (text-in-image king), Runway (Gen-3), Pika direct.
    "ideogram":   os.environ.get('IDEOGRAM_API_KEY', ''),
    "runway":     os.environ.get('RUNWAY_API_KEY', ''),
    "pika":       os.environ.get('PIKA_API_KEY', ''),
}

# Upload directory - configurable via environment variable
# Defaults to ./uploads (current working directory) for development
# Set UPLOAD_DIR environment variable to override (absolute or relative path)
upload_dir_env = os.environ.get('UPLOAD_DIR', './uploads')
if os.path.isabs(upload_dir_env):
    # Absolute path
    UPLOAD_DIR = Path(upload_dir_env)
else:
    # Relative path - resolve relative to root backend directory
    UPLOAD_DIR = ROOT_DIR / upload_dir_env

# Ensure directory exists with proper error handling
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    import warnings
    warnings.warn(f"Warning: Cannot create upload directory {UPLOAD_DIR}. Check file permissions.")
except Exception as e:
    import warnings
    warnings.warn(f"Warning: Error creating upload directory {UPLOAD_DIR}: {str(e)}")

# Subscription plans (mutable - updated from DB on startup)
# Agent count: 41 core named agents + 417 MAARS Infinity = 458 total
# Credits: capped ~10,000 — enough for a full active month
# BDT and monthly_cap_usd are recomputed on publish from live rate & cost/credit
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price_usd": 0.0,
        "price_bdt": 0.0,
        "credits": 50,
        "max_agents": 3,
        "max_custom_agents": 0,
        "includes_commander": False,
        "max_team_members": 1,
        "monthly_cap_usd": 0.0,
        "features": [
            "3 AI agents", "50 credits/month",
            "Basic chat & task management", "1 LLM provider",
            "Community support",
        ],
    },
    "starter": {
        "name": "Starter",
        "price_usd": 50.0,
        "price_bdt": 5350.0,
        "credits": 300,
        "max_agents": 8,
        "max_custom_agents": 0,
        "includes_commander": False,
        "max_team_members": 1,
        "monthly_cap_usd": 0.9,
        "features": [
            "8 AI agents", "300 credits/month",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models (economy tier)",
            "Chat, tasks & projects", "File uploads",
            "Solo workspace", "Email support",
        ],
    },
    "essential": {
        "name": "Essential",
        "price_usd": 100.0,
        "price_bdt": 10700.0,
        "credits": 600,
        "max_agents": 12,
        "max_custom_agents": 1,
        "includes_commander": False,
        "max_team_members": 3,
        "monthly_cap_usd": 1.8,
        "features": [
            "12 AI agents", "600 credits/month", "1 custom agent",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models (economy + standard)",
            "Workflow builder", "File uploads",
            "Team (up to 3)", "Email support",
        ],
    },
    "basic": {
        "name": "Basic",
        "price_usd": 200.0,
        "price_bdt": 21400.0,
        "credits": 1200,
        "max_agents": 18,
        "max_custom_agents": 2,
        "includes_commander": False,
        "max_team_members": 5,
        "monthly_cap_usd": 3.6,
        "features": [
            "18 AI agents", "1,200 credits/month", "2 custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models (all tiers)",
            "Full workflow builder", "Content generator",
            "Basic analytics", "Team (up to 5)", "Priority email support",
        ],
    },
    "standard": {
        "name": "Standard",
        "price_usd": 350.0,
        "price_bdt": 37450.0,
        "credits": 2000,
        "max_agents": 25,
        "max_custom_agents": 3,
        "includes_commander": True,
        "max_team_members": 10,
        "monthly_cap_usd": 6.0,
        "features": [
            "25 AI agents + Commander Orion", "2,000 credits/month", "3 custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Autonomous orchestration", "Campaign builder",
            "Knowledge graph", "Trust scores",
            "Team (up to 10)", "Priority support",
        ],
    },
    "professional": {
        "name": "Professional",
        "price_usd": 500.0,
        "price_bdt": 53500.0,
        "credits": 3000,
        "max_agents": 35,
        "max_custom_agents": 5,
        "includes_commander": True,
        "max_team_members": 20,
        "monthly_cap_usd": 9.0,
        "features": [
            "35 AI agents + Commander Orion", "3,000 credits/month", "5 custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Vibe Coding & Reference Intelligence",
            "Memory hierarchy", "Analytics dashboard",
            "Team (up to 20)", "Live chat support",
        ],
    },
    "advanced": {
        "name": "Advanced",
        "price_usd": 750.0,
        "price_bdt": 80250.0,
        "credits": 4000,
        "max_agents": 41,
        "max_custom_agents": 10,
        "includes_commander": True,
        "max_team_members": 35,
        "monthly_cap_usd": 12.0,
        "features": [
            "All 41 core AI agents + Commander Orion", "4,000 credits/month", "10 custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Full observability dashboard", "Model router",
            "Circuit breakers", "Cost governance",
            "Team (up to 35)", "Dedicated Slack support",
        ],
    },
    "business": {
        "name": "Business",
        "price_usd": 1000.0,
        "price_bdt": 107000.0,
        "credits": 5000,
        "max_agents": 141,
        "max_custom_agents": 20,
        "includes_commander": True,
        "max_team_members": 50,
        "monthly_cap_usd": 15.0,
        "features": [
            "41 core + 100 MAARS Infinity agents + Commander Orion", "5,000 credits/month", "20 custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "MAARS Infinity agent networks", "Operator panel",
            "API access & webhooks", "Team (up to 50)", "Dedicated Slack support",
        ],
    },
    "agency": {
        "name": "Agency",
        "price_usd": 1500.0,
        "price_bdt": 160500.0,
        "credits": 6500,
        "max_agents": 241,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 19.5,
        "features": [
            "41 core + 200 MAARS Infinity agents + Commander Orion", "6,500 credits/month",
            "Unlimited custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "White-label ready", "RBAC & access control",
            "Client management tools", "SLA guarantee",
            "Unlimited team members", "Dedicated account manager",
        ],
    },
    "studio": {
        "name": "Studio",
        "price_usd": 2500.0,
        "price_bdt": 267500.0,
        "credits": 7500,
        "max_agents": 391,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 22.5,
        "features": [
            "41 core + 350 MAARS Infinity agents + Commander Orion", "7,500 credits/month",
            "Unlimited custom agents",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Venture portfolio", "Agent Catalog (350 networks)",
            "Custom integrations", "Multi-workspace",
            "Unlimited team members", "Priority dedicated support",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 3500.0,
        "price_bdt": 374500.0,
        "credits": 8500,
        "max_agents": 458,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 25.5,
        "features": [
            "All 458 agents + Commander Orion", "8,500 credits/month", "Unlimited everything",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Dedicated infrastructure", "Advanced security & compliance",
            "Custom AI integrations", "Onboarding & training",
            "Custom SLAs", "24/7 premium support",
        ],
    },
    "corporate": {
        "name": "Corporate",
        "price_usd": 5000.0,
        "price_bdt": 535000.0,
        "credits": 9500,
        "max_agents": 458,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 28.5,
        "features": [
            "All 458 agents + Commander Orion", "9,500 credits/month", "Unlimited everything",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Custom AI model fine-tuning", "Dedicated engineering support",
            "Multi-workspace management", "Custom contracts & billing",
            "Quarterly business reviews", "Executive priority support",
        ],
    },
    "elite": {
        "name": "Elite",
        "price_usd": 8000.0,
        "price_bdt": 856000.0,
        "credits": 10000,
        "max_agents": 458,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 30.0,
        "features": [
            "All 458 agents + Commander Orion", "10,000 credits/month", "Unlimited everything",
            "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
            "Custom agent development", "Dedicated servers & infrastructure",
            "Strategic AI consulting", "Full platform customization",
            "Executive support hotline", "Custom contract & billing",
        ],
    },
    "white_label": {
        "name": "White Label",
        "price_usd": 19999.0,
        "price_bdt": 2139893.0,
        "credits": 20000,
        "max_agents": 458,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "monthly_cap_usd": 60.0,
        "features": [
            "Every feature in Elite — unlimited agents, seats, credits",
            "Full white-label: your brand, your domain, your UI",
            "Dedicated deployment on infrastructure you own",
            "Co-pilot onboarding for your first 5 seats (live)",
            "Custom integrations + private tool nodes",
            "Reseller terms available — you bill your clients directly",
            "Quarterly strategic review + named engineering contact",
            "SLA with financial remedy; 24/7 critical-path escalation",
        ],
    },
}

# ---------------------------------------------------------------------------
# Subscription split — operator profit-share % per plan.
# Injected post-definition so the existing SUBSCRIPTION_PLANS structure stays
# readable. Free tier has 0 share (no revenue to split). Higher tiers retain
# more profit because their absolute provider cost-vs-margin ratio is better.
# Owner can override per-plan via /admin/pricing or the in-app pricing manager.
# ---------------------------------------------------------------------------
_DEFAULT_OPERATOR_SPLITS = {
    "free":         0.0,
    "starter":      0.30,
    "essential":    0.30,
    "basic":        0.32,
    "standard":     0.32,
    "professional": 0.32,
    "advanced":     0.35,
    "business":     0.35,
    "agency":       0.35,
    "studio":       0.40,
    "enterprise":   0.40,
    "corporate":    0.40,
    "elite":        0.40,
    "white_label":  0.45,
}
for _pid, _split in _DEFAULT_OPERATOR_SPLITS.items():
    if _pid in SUBSCRIPTION_PLANS:
        SUBSCRIPTION_PLANS[_pid].setdefault("operator_share_pct", _split)


# ---------------------------------------------------------------------------
# Credits ↔ USD conversion rate.
#
# 1 credit = $0.001  →  CREDITS_PER_USD = 1000
#
# This is the SINGLE source of truth that ties three things together:
#   1. Subscription split — when a user pays for a plan, the user-backing
#      portion of the cash (price × (1 - operator_share_pct)) is converted into
#      a spendable credit balance via this rate.
#   2. Per-call pricing — actual provider cost in USD is converted into
#      credits via this rate so user balance drains in real terms, not in a
#      flat per-model count.
#   3. Operator profit math — operator dashboards convert credit revenue back
#      to USD using this rate when computing margin.
#
# Owner-tunable in `platform_config.config_type="pricing"` under key
# `credits_per_usd`. Loaded into this constant at startup.
# ---------------------------------------------------------------------------
CREDITS_PER_USD = 1000


# Custom agent creation cost (mutable - updated from DB on startup)
CUSTOM_AGENT_CREDIT_COST = 20

# Default custom package pricing (admin can override via DB)
DEFAULT_CUSTOM_PACKAGE_CONFIG = {
    "per_agent_price_usd": 5.0,
    "per_agent_price_bdt": 535.0,
    "commander_addon_price_usd": 15.0,
    "commander_addon_price_bdt": 1605.0,
    "credit_presets": [
        {"id": "cp_100", "credits": 100, "price_usd": 6.0, "price_bdt": 640.0},
        {"id": "cp_500", "credits": 500, "price_usd": 25.0, "price_bdt": 2675.0},
        {"id": "cp_1000", "credits": 1000, "price_usd": 45.0, "price_bdt": 4815.0},
        {"id": "cp_2000", "credits": 2000, "price_usd": 80.0, "price_bdt": 8560.0},
        {"id": "cp_5000", "credits": 5000, "price_usd": 180.0, "price_bdt": 19260.0},
    ]
}

DEFAULT_CREDIT_PACKAGES = [
    {"id": "credits_100", "credits": 100, "price_usd": 6.0, "price_bdt": 640.0, "name": "100 Credits"},
    {"id": "credits_300", "credits": 300, "price_usd": 18.0, "price_bdt": 1910.0, "name": "300 Credits"},
    {"id": "credits_700", "credits": 700, "price_usd": 42.0, "price_bdt": 4450.0, "name": "700 Credits"},
    {"id": "credits_1500", "credits": 1500, "price_usd": 90.0, "price_bdt": 9540.0, "name": "1,500 Credits"},
]

# Integration services config
INTEGRATION_SERVICES = {
    # ── Productivity / Dev ──────────────────────────────────────────────────────
    "slack": {"name": "Slack", "key_fields": ["bot_token"], "description": "Send messages to Slack channels and workspaces", "category": "productivity"},
    "github": {"name": "GitHub", "key_fields": ["personal_access_token"], "description": "Create issues, PRs, read/write repos", "category": "development"},
    "sendgrid": {"name": "SendGrid", "key_fields": ["api_key"], "description": "Send transactional and marketing emails", "category": "email"},
    "resend": {"name": "Resend", "key_fields": ["api_key"], "description": "Modern email sending API", "category": "email"},
    "twilio": {"name": "Twilio", "key_fields": ["account_sid", "auth_token", "phone_number"], "description": "Send SMS, voice calls, and cold outreach", "category": "communications"},
    "airtable": {"name": "Airtable", "key_fields": ["api_key"], "description": "Read/write Airtable bases and records", "category": "productivity"},
    "calendly": {"name": "Calendly", "key_fields": ["api_key"], "description": "Schedule meetings, appointments, and calls", "category": "scheduling"},
    "giphy": {"name": "Giphy", "key_fields": ["api_key"], "description": "Search and send GIFs", "category": "media"},
    "google_suite": {"name": "Google Suite", "key_fields": ["service_account_json", "delegate_email"], "description": "Gmail, Google Calendar, Google Drive", "category": "productivity"},

    # ── Social Media Platforms ──────────────────────────────────────────────────
    "facebook": {
        "name": "Facebook",
        "key_fields": ["page_access_token", "page_id", "app_id", "app_secret"],
        "description": "Post content, send Messenger messages, boost posts with geo-targeting, manage Facebook Pages and ad campaigns",
        "category": "social_media",
        "capabilities": ["post", "story", "reel", "message", "boost", "ads", "geo_target", "analytics", "comment", "reply"],
        "oauth_url": "https://developers.facebook.com/apps/",
        "docs_url": "https://developers.facebook.com/docs/graph-api/",
    },
    "instagram": {
        "name": "Instagram",
        "key_fields": ["access_token", "instagram_business_account_id"],
        "description": "Post photos/reels/stories, send DMs, boost posts, reply to comments, geo-target audiences for the right regions",
        "category": "social_media",
        "capabilities": ["post", "reel", "story", "dm", "boost", "hashtag", "geo_target", "analytics", "comment"],
        "oauth_url": "https://developers.facebook.com/apps/",
        "docs_url": "https://developers.facebook.com/docs/instagram-api/",
    },
    "twitter": {
        "name": "Twitter / X",
        "key_fields": ["api_key", "api_secret", "access_token", "access_token_secret", "bearer_token"],
        "description": "Post tweets, reply to mentions, send DMs, run promoted tweet campaigns, engage with followers worldwide",
        "category": "social_media",
        "capabilities": ["tweet", "reply", "dm", "retweet", "like", "thread", "spaces", "ads", "analytics"],
        "oauth_url": "https://developer.twitter.com/en/portal/dashboard",
        "docs_url": "https://developer.twitter.com/en/docs/twitter-api",
    },
    "tiktok": {
        "name": "TikTok",
        "key_fields": ["access_token", "advertiser_id", "app_id"],
        "description": "Post videos, run geo-targeted TikTok ad campaigns, track performance, reach audiences in specific countries/languages",
        "category": "social_media",
        "capabilities": ["post", "boost", "ads", "geo_target", "analytics", "spark_ads", "duet"],
        "oauth_url": "https://ads.tiktok.com/marketing_api/apps/",
        "docs_url": "https://ads.tiktok.com/marketing_api/docs",
    },
    "whatsapp": {
        "name": "WhatsApp Business",
        "key_fields": ["phone_number_id", "access_token", "waba_id"],
        "description": "Send/receive messages, make voice & video calls, broadcast campaigns, send templates in local languages, manage Business catalog",
        "category": "social_media",
        "capabilities": ["message", "call", "broadcast", "template", "media", "catalog", "reply", "geo_target"],
        "oauth_url": "https://developers.facebook.com/apps/",
        "docs_url": "https://developers.facebook.com/docs/whatsapp/cloud-api/",
    },
    "viber": {
        "name": "Viber",
        "key_fields": ["auth_token"],
        "description": "Send messages, media, and broadcasts to Viber subscribers — strong reach in Eastern Europe & Southeast Asia",
        "category": "social_media",
        "capabilities": ["message", "broadcast", "media", "keyboard", "reply", "sticker"],
        "oauth_url": "https://partners.viber.com/",
        "docs_url": "https://developers.viber.com/docs/api/rest-bot-api/",
    },
    "line": {
        "name": "LINE",
        "key_fields": ["channel_access_token", "channel_secret"],
        "description": "Send messages, rich menus, and broadcasts to LINE followers — dominant in Japan, Thailand, Taiwan, Indonesia",
        "category": "social_media",
        "capabilities": ["message", "broadcast", "rich_menu", "flex_message", "push", "reply", "liff"],
        "oauth_url": "https://developers.line.biz/console/",
        "docs_url": "https://developers.line.biz/en/docs/messaging-api/",
    },
    "linkedin": {
        "name": "LinkedIn",
        "key_fields": ["access_token", "organization_id"],
        "description": "Post articles and updates, send InMail, run B2B lead-gen ad campaigns, target by industry/geography/seniority",
        "category": "social_media",
        "capabilities": ["post", "article", "inmail", "ads", "lead_gen", "geo_target", "analytics", "comment"],
        "oauth_url": "https://www.linkedin.com/developers/apps",
        "docs_url": "https://learn.microsoft.com/en-us/linkedin/",
    },
    "youtube": {
        "name": "YouTube",
        "key_fields": ["api_key", "oauth_client_id", "oauth_client_secret"],
        "description": "Upload videos, manage comments, run YouTube video ad campaigns, track analytics and subscriber engagement",
        "category": "social_media",
        "capabilities": ["upload", "comment", "reply", "live", "ads", "analytics", "playlist", "subtitle"],
        "oauth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/youtube/v3",
    },
    "telegram": {
        "name": "Telegram",
        "key_fields": ["bot_token", "channel_username"],
        "description": "Send messages to channels/groups, broadcast updates, manage bots with inline keyboards — global reach, zero cost",
        "category": "social_media",
        "capabilities": ["message", "broadcast", "channel", "group", "inline_keyboard", "media", "poll", "bot"],
        "oauth_url": "https://t.me/BotFather",
        "docs_url": "https://core.telegram.org/bots/api",
    },

    # —— Commerce / CRM / Knowledge / Ops ————————————————————————————————————————————————
    "shopify": {
        "name": "Shopify",
        "key_fields": ["store_url", "access_token"],
        "description": "Manage store data, products, customers, and order operations for commerce workflows",
        "category": "commerce",
        "capabilities": ["products", "orders", "customers", "inventory", "fulfillment", "analytics"],
        "oauth_url": "https://partners.shopify.com/",
        "docs_url": "https://shopify.dev/docs/api",
    },
    "hubspot": {
        "name": "HubSpot",
        "key_fields": ["access_token", "portal_id"],
        "description": "Sync contacts, deals, and lifecycle events with HubSpot CRM and marketing tools",
        "category": "crm",
        "capabilities": ["contacts", "companies", "deals", "tickets", "pipelines", "campaigns"],
        "oauth_url": "https://developers.hubspot.com/",
        "docs_url": "https://developers.hubspot.com/docs/api/overview",
    },
    "salesforce": {
        "name": "Salesforce",
        "key_fields": ["instance_url", "client_id", "client_secret", "refresh_token"],
        "description": "Connect sales, support, and revenue workflows to Salesforce data and automation",
        "category": "crm",
        "capabilities": ["leads", "opportunities", "accounts", "cases", "reports", "workflows"],
        "oauth_url": "https://developer.salesforce.com/",
        "docs_url": "https://developer.salesforce.com/docs",
    },
    "webhooks": {
        "name": "Custom Webhooks",
        "key_fields": ["webhook_url", "signing_secret"],
        "description": "Push signed events to custom endpoints for internal systems and external automations",
        "category": "automation",
        "capabilities": ["webhook", "signing", "retries", "events", "callbacks"],
        "docs_url": "https://webhooks.fyi/",
    },
    "notion": {
        "name": "Notion",
        "key_fields": ["integration_token"],
        "description": "Read and write workspace pages, databases, and structured operating documents",
        "category": "knowledge",
        "capabilities": ["pages", "databases", "search", "comments", "knowledge_sync"],
        "oauth_url": "https://www.notion.so/my-integrations",
        "docs_url": "https://developers.notion.com/",
    },
    "jira": {
        "name": "Jira",
        "key_fields": ["base_url", "email", "api_token"],
        "description": "Coordinate engineering and operations work through Jira issues, projects, and workflows",
        "category": "knowledge",
        "capabilities": ["issues", "projects", "sprints", "comments", "transitions"],
        "oauth_url": "https://developer.atlassian.com/console/myapps/",
        "docs_url": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/",
    },
    "confluence": {
        "name": "Confluence",
        "key_fields": ["base_url", "email", "api_token"],
        "description": "Store playbooks, runbooks, and operating knowledge in Confluence spaces and pages",
        "category": "knowledge",
        "capabilities": ["pages", "spaces", "search", "comments", "attachments"],
        "oauth_url": "https://developer.atlassian.com/console/myapps/",
        "docs_url": "https://developer.atlassian.com/cloud/confluence/rest/v2/",
    },
    "stripe": {
        "name": "Stripe",
        "key_fields": ["secret_key", "webhook_secret"],
        "description": "Inspect payments, customers, subscriptions, and billing events for revenue operations",
        "category": "finance",
        "capabilities": ["payments", "customers", "subscriptions", "billing", "webhooks"],
        "oauth_url": "https://dashboard.stripe.com/apikeys",
        "docs_url": "https://docs.stripe.com/api",
    },
    # ── Self-hosted automation backbone ─────────────────────────────────────
    # The embedded browser is an integration that doesn't reach out to a
    # third-party API — it IS the API surface MAARS uses to drive the open
    # web. Agents, the orchestrator, and the human UI all share the same
    # Chromium context per user, so logged-in sessions can be handed back
    # and forth without re-authenticating. Chromium lives in backend/browser_data/
    # (inside the MAARS install, not the host OS).
    "browser": {
        "name": "Embedded Browser",
        "key_fields": [],  # no external credentials required
        "description": "Self-hosted Chromium runtime. Agents and the human user share the same browser session to automate any website, complete OAuth flows, scrape data, fill forms, and handle 2FA handoffs.",
        "category": "automation",
        "capabilities": [
            "navigate", "click", "fill", "type", "scroll", "extract_text",
            "extract_html", "screenshot", "evaluate_js", "persistent_login",
            "three_way_handoff", "live_stream", "cookie_vault",
        ],
        "oauth_url": "",
        "docs_url": "/api/browser/health",
    },
}

# Pay-as-you-go Universal Key configuration
PAYG_CONFIG = {
    "model_allocation_pct": 0.65,    # 65% of payment goes to AI model costs
    "platform_profit_pct": 0.35,     # 35% goes to platform profit
    "credits_per_usd": 16.67,        # ~$0.06 per credit (standard rate)
    "min_topup_usd": 5.0,
    "max_topup_usd": 10000.0,
    "currency_support": ["usd", "bdt"],
    "bdt_to_usd_rate": 110.0,        # approx, updated live
}
