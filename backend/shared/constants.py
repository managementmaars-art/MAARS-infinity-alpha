"""Shared constants and configuration used across the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# LLM Settings
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Email Settings
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Direct API Keys (can be overridden from admin panel via DB)
DIRECT_API_KEYS = {
    "openai": os.environ.get('OPENAI_API_KEY', ''),
    "anthropic": os.environ.get('ANTHROPIC_API_KEY', ''),
    "gemini": os.environ.get('GOOGLE_API_KEY', ''),
    "groq": os.environ.get('GROQ_API_KEY', ''),
    "together": os.environ.get('TOGETHER_API_KEY', ''),
    "fireworks": os.environ.get('FIREWORKS_API_KEY', ''),
    "ai21": os.environ.get('AI21_API_KEY', ''),
}

# Upload directory
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Subscription plans (mutable - updated from DB on startup)
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
        "features": ["3 AI agents", "50 credits/month", "Basic chat & tasks", "1 LLM provider", "Community support"]
    },
    "starter": {
        "name": "Starter",
        "price_usd": 29.0,
        "price_bdt": 3100.0,
        "credits": 500,
        "max_agents": 10,
        "max_custom_agents": 2,
        "includes_commander": False,
        "max_team_members": 3,
        "features": ["10 AI agents", "500 credits/month", "2 custom agents", "5 LLM providers", "Vibe Coding & Content Generator", "Voice commands", "Team (up to 3)", "Priority support", "File uploads"]
    },
    "pro": {
        "name": "Pro",
        "price_usd": 79.0,
        "price_bdt": 8400.0,
        "credits": 2000,
        "max_agents": 25,
        "max_custom_agents": 5,
        "includes_commander": True,
        "max_team_members": 10,
        "features": ["25 AI agents + Commander Orion", "2,000 credits/month", "5 custom agents", "All 13 LLM providers (45+ models)", "Autonomous orchestration", "Quality control & auto-learning", "Memory governance", "Real-time activity monitor", "Reference intelligence", "Team (up to 10)", "Unlimited uploads"]
    },
    "business": {
        "name": "Business",
        "price_usd": 199.0,
        "price_bdt": 21100.0,
        "credits": 6000,
        "max_agents": 41,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "features": ["All 41 AI agents + Commander Orion", "6,000 credits/month", "Unlimited custom agents", "All 13 LLM providers (45+ models)", "Full autonomous orchestration", "All 17 core systems", "KPI dashboard & collaboration engine", "Admin code explorer", "Unlimited team members", "Dedicated support", "API access"]
    }
}

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
    "slack": {"name": "Slack", "key_fields": ["bot_token"], "description": "Send messages to Slack channels and workspaces"},
    "github": {"name": "GitHub", "key_fields": ["personal_access_token"], "description": "Create issues, PRs, read/write repos"},
    "sendgrid": {"name": "SendGrid", "key_fields": ["api_key"], "description": "Send transactional and marketing emails"},
    "resend": {"name": "Resend", "key_fields": ["api_key"], "description": "Modern email sending API"},
    "twilio": {"name": "Twilio", "key_fields": ["account_sid", "auth_token", "phone_number"], "description": "Send SMS and voice calls"},
    "airtable": {"name": "Airtable", "key_fields": ["api_key"], "description": "Read/write Airtable bases and records"},
    "calendly": {"name": "Calendly", "key_fields": ["api_key"], "description": "Schedule meetings and manage events"},
    "giphy": {"name": "Giphy", "key_fields": ["api_key"], "description": "Search and send GIFs"},
    "google_suite": {"name": "Google Suite", "key_fields": ["service_account_json", "delegate_email"], "description": "Gmail, Google Calendar, Google Drive"},
}
