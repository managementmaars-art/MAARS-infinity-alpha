"""Shared utility functions used across the application."""
import os
import uuid
import logging
import asyncio
from datetime import datetime, timezone
import httpx
from db import db
from shared.constants import (
    EMERGENT_LLM_KEY, SMTP_EMAIL, SMTP_PASSWORD,
    DIRECT_API_KEYS, INTEGRATION_SERVICES,
    DEFAULT_CUSTOM_PACKAGE_CONFIG, DEFAULT_CREDIT_PACKAGES
)

logger = logging.getLogger(__name__)

# Exchange rate cache (refreshes hourly)
_exchange_rate_cache = {"rate": None, "fetched_at": None}


async def send_email_notification(to_email: str, subject: str, html_body: str):
    """Send email via Gmail SMTP. Silently skips if credentials not configured."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.info(f"Email skipped (SMTP not configured): to={to_email}, subject={subject}")
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"MAARS Command <{SMTP_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        def _send():
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, to_email, msg.as_string())

        await asyncio.to_thread(_send)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


async def get_api_keys():
    """Get API keys - prioritize DB-stored keys, then env vars, then Emergent key"""
    config = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
    keys = {
        "openai": "",
        "anthropic": "",
        "gemini": "",
        "xai": "",
        "deepseek": "",
        "mistral": "",
        "perplexity": "",
        "cohere": "",
        "elevenlabs": "",
        "emergent": EMERGENT_LLM_KEY,
        "active_provider": "emergent"
    }
    if config:
        for p in ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]:
            keys[p] = config.get(f"{p}_key", "") or DIRECT_API_KEYS.get(p, "")
        keys["active_provider"] = config.get("active_provider", "emergent")
    return keys


async def get_integration_keys():
    """Get integration keys from DB"""
    config = await db.platform_config.find_one({"config_type": "integration_keys"}, {"_id": 0})
    return config or {"config_type": "integration_keys"}


async def get_integration_key(service: str, field: str = None):
    """Get a specific integration key"""
    config = await get_integration_keys()
    service_config = config.get(service, {})
    if field:
        return service_config.get(field, "")
    service_def = INTEGRATION_SERVICES.get(service, {})
    for f in service_def.get("key_fields", []):
        val = service_config.get(f, "")
        if val:
            return val
    return ""


async def get_custom_package_config():
    config = await db.platform_config.find_one({"config_type": "custom_packages"}, {"_id": 0})
    if config:
        return config
    return DEFAULT_CUSTOM_PACKAGE_CONFIG


async def get_live_bdt_rate():
    """Fetch live USD/BDT rate from HexaRate API, cached for 1 hour"""
    now = datetime.now(timezone.utc)
    if _exchange_rate_cache["rate"] and _exchange_rate_cache["fetched_at"]:
        age = (now - _exchange_rate_cache["fetched_at"]).total_seconds()
        if age < 3600:
            return _exchange_rate_cache["rate"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://hexarate.paikama.co/api/rates/latest/USD?target=BDT")
            if resp.status_code == 200:
                data = resp.json()
                rate = data.get("data", {}).get("mid")
                if rate and rate > 0:
                    _exchange_rate_cache["rate"] = round(rate, 2)
                    _exchange_rate_cache["fetched_at"] = now
                    return _exchange_rate_cache["rate"]
    except Exception as e:
        logger.error(f"Exchange rate fetch error: {e}")
    saved = await db.platform_config.find_one({"config_type": "exchange_rate"}, {"_id": 0})
    if saved and saved.get("usd_bdt"):
        return saved["usd_bdt"]
    return 121.0


async def get_credit_packages():
    config = await db.platform_config.find_one({"config_type": "credit_packages"}, {"_id": 0})
    if config and config.get("packages"):
        pkgs = {}
        for p in config["packages"]:
            pkgs[p["id"]] = p
        return pkgs
    return {p["id"]: p for p in DEFAULT_CREDIT_PACKAGES}


async def create_notification(user_id: str, ntype: str, title: str, message: str, link: str = None):
    """Create a notification for a user."""
    await db.notifications.insert_one({
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "type": ntype,
        "title": title,
        "message": message,
        "link": link,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
