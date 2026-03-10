"""Integration Service — Third-party integration hub management."""
from datetime import datetime, timezone
from bson import ObjectId
from db import db


AVAILABLE_INTEGRATIONS = [
    {
        "integration_id": "whatsapp",
        "name": "WhatsApp Business",
        "description": "Send and receive messages via WhatsApp Business API",
        "category": "Messaging",
        "icon": "message-circle",
        "color": "#25D366",
        "config_fields": [
            {"key": "phone_number_id", "label": "Phone Number ID", "type": "text", "required": True},
            {"key": "access_token", "label": "Access Token", "type": "password", "required": True},
            {"key": "verify_token", "label": "Verify Token", "type": "text", "required": True},
        ],
    },
    {
        "integration_id": "shopify",
        "name": "Shopify",
        "description": "Manage products, orders, and customers on Shopify",
        "category": "E-Commerce",
        "icon": "shopping-bag",
        "color": "#96BF48",
        "config_fields": [
            {"key": "store_url", "label": "Store URL", "type": "text", "required": True},
            {"key": "api_key", "label": "API Key", "type": "text", "required": True},
            {"key": "api_secret", "label": "API Secret", "type": "password", "required": True},
            {"key": "access_token", "label": "Access Token", "type": "password", "required": True},
        ],
    },
    {
        "integration_id": "hubspot",
        "name": "HubSpot CRM",
        "description": "Sync contacts, deals, and marketing data with HubSpot",
        "category": "CRM",
        "icon": "users",
        "color": "#FF7A59",
        "config_fields": [
            {"key": "api_key", "label": "API Key", "type": "password", "required": True},
            {"key": "portal_id", "label": "Portal ID", "type": "text", "required": True},
        ],
    },
    {
        "integration_id": "salesforce",
        "name": "Salesforce",
        "description": "Connect to Salesforce CRM for lead and opportunity management",
        "category": "CRM",
        "icon": "cloud",
        "color": "#00A1E0",
        "config_fields": [
            {"key": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True},
            {"key": "username", "label": "Username", "type": "text", "required": True},
            {"key": "password", "label": "Password", "type": "password", "required": True},
            {"key": "security_token", "label": "Security Token", "type": "password", "required": True},
        ],
    },
    {
        "integration_id": "slack",
        "name": "Slack",
        "description": "Send notifications and interact through Slack channels",
        "category": "Messaging",
        "icon": "hash",
        "color": "#4A154B",
        "config_fields": [
            {"key": "bot_token", "label": "Bot Token", "type": "password", "required": True},
            {"key": "signing_secret", "label": "Signing Secret", "type": "password", "required": True},
            {"key": "default_channel", "label": "Default Channel", "type": "text", "required": False},
        ],
    },
    {
        "integration_id": "google_workspace",
        "name": "Google Workspace",
        "description": "Gmail, Google Calendar, Google Drive",
        "category": "Productivity",
        "icon": "mail",
        "color": "#4285F4",
        "config_fields": [
            {"key": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True},
            {"key": "refresh_token", "label": "Refresh Token", "type": "password", "required": True},
        ],
    },
]


async def get_integrations():
    return AVAILABLE_INTEGRATIONS


async def get_user_integrations(user_id):
    results = []
    async for doc in db.user_integrations.find({"user_id": user_id}, {"_id": 0}):
        results.append(doc)
    return results


async def save_user_integration(user_id, data):
    integration_id = data.get("integration_id")
    template = next((i for i in AVAILABLE_INTEGRATIONS if i["integration_id"] == integration_id), None)
    if not template:
        return None

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": user_id,
        "integration_id": integration_id,
        "name": template["name"],
        "category": template["category"],
        "config": data.get("config", {}),
        "enabled": True,
        "status": "connected",
        "connected_at": now,
        "updated_at": now,
    }
    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"$set": doc},
        upsert=True,
    )
    safe_doc = {**doc}
    safe_config = {}
    for k, v in doc.get("config", {}).items():
        safe_config[k] = v[:4] + "****" if isinstance(v, str) and len(v) > 4 else "****"
    safe_doc["config"] = safe_config
    return safe_doc


async def disconnect_integration(user_id, integration_id):
    await db.user_integrations.delete_one({"user_id": user_id, "integration_id": integration_id})
    return {"status": "disconnected"}


async def toggle_integration(user_id, integration_id, enabled):
    now = datetime.now(timezone.utc).isoformat()
    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"$set": {"enabled": enabled, "updated_at": now}}
    )
    return await db.user_integrations.find_one(
        {"user_id": user_id, "integration_id": integration_id}, {"_id": 0}
    )
