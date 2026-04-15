"""Integration service for the unified connector catalog and user connection state."""
from copy import deepcopy
from datetime import datetime, timezone

from db import db
from shared.constants import INTEGRATION_SERVICES
from shared.utils import get_integration_keys


LEGACY_INTEGRATION_IDS = {
    "google_workspace": "google_suite",
}

SOCIAL_CATEGORIES = {"social_media"}

CATEGORY_LABELS = {
    "social_media": "Social Media & Messaging",
    "communications": "Communications & Outreach",
    "email": "Email & Cold Outreach",
    "scheduling": "Scheduling & Calendar",
    "productivity": "Productivity & Data",
    "development": "Development",
    "commerce": "Commerce",
    "crm": "CRM",
    "knowledge": "Knowledge",
    "finance": "Finance",
    "automation": "Automation",
}

DISPLAY_OVERRIDES = {
    "facebook": {"color": "#1877F2", "icon": "facebook"},
    "instagram": {"color": "#E4405F", "icon": "instagram"},
    "twitter": {"color": "#000000", "icon": "twitter"},
    "tiktok": {"color": "#FF0050", "icon": "music-2"},
    "whatsapp": {"color": "#25D366", "icon": "message-circle"},
    "viber": {"color": "#7360F2", "icon": "message-square"},
    "line": {"color": "#06C755", "icon": "messages-square"},
    "linkedin": {"color": "#0A66C2", "icon": "linkedin"},
    "youtube": {"color": "#FF0000", "icon": "play"},
    "telegram": {"color": "#2AABEE", "icon": "send"},
    "slack": {"color": "#4A154B", "icon": "hash"},
    "github": {"color": "#111827", "icon": "github"},
    "sendgrid": {"color": "#1A82E2", "icon": "mail"},
    "resend": {"color": "#111827", "icon": "mail"},
    "twilio": {"color": "#F22F46", "icon": "phone"},
    "airtable": {"color": "#18BFFF", "icon": "table"},
    "calendly": {"color": "#006BFF", "icon": "calendar"},
    "google_suite": {"color": "#4285F4", "icon": "sparkles"},
    "shopify": {"color": "#96BF48", "icon": "shopping-bag"},
    "hubspot": {"color": "#FF7A59", "icon": "users"},
    "salesforce": {"color": "#00A1E0", "icon": "cloud"},
    "zapier": {"color": "#FF4F00", "icon": "workflow"},
    "webhooks": {"color": "#0F766E", "icon": "webhook"},
    "notion": {"color": "#111827", "icon": "book"},
    "jira": {"color": "#0052CC", "icon": "kanban-square"},
    "confluence": {"color": "#172B4D", "icon": "file-text"},
    "stripe": {"color": "#635BFF", "icon": "credit-card"},
    "browser": {"color": "#2563EB", "icon": "globe"},
}

RUNTIME_SUPPORT = {
    "slack": "live",
    "github": "live",
    "sendgrid": "live",
    "resend": "live",
    "twilio": "live",
    "google_suite": "live",
    "whatsapp": "hybrid",
    "facebook": "hybrid",
    "instagram": "hybrid",
    "twitter": "hybrid",
    "tiktok": "hybrid",
    "viber": "hybrid",
    "line": "hybrid",
    "linkedin": "hybrid",
    "youtube": "hybrid",
    "telegram": "hybrid",
    "shopify": "hybrid",
    "hubspot": "hybrid",
    "salesforce": "hybrid",
    "airtable": "hybrid",
    "calendly": "hybrid",
    "giphy": "hybrid",
    "zapier": "hybrid",
    "webhooks": "hybrid",
    "notion": "planned",
    "jira": "planned",
    "confluence": "planned",
    "stripe": "live",
    "browser": "live",
}

MATURITY_BY_RUNTIME = {
    "live": "production_ready",
    "hybrid": "configurable",
    "planned": "planned",
}


def canonicalize_integration_id(integration_id):
    if not integration_id:
        return ""
    return LEGACY_INTEGRATION_IDS.get(integration_id, integration_id)


def _humanize_key(key):
    return key.replace("_", " ").replace("-", " ").title()


def _field_type_from_key(key):
    lowered = key.lower()
    if lowered.endswith("_url") or lowered == "base_url":
        return "url"
    if lowered.endswith("_email") or lowered == "email":
        return "email"
    if "json" in lowered:
        return "textarea"
    if any(token in lowered for token in ("token", "secret", "password", "key")):
        return "password"
    return "text"


def _build_config_fields(service_def):
    if service_def.get("config_fields"):
        return deepcopy(service_def["config_fields"])
    return [
        {
            "key": field_key,
            "label": _humanize_key(field_key),
            "type": _field_type_from_key(field_key),
            "required": True,
        }
        for field_key in service_def.get("key_fields", [])
    ]


def _build_catalog_entry(integration_id, service_def):
    runtime_support = RUNTIME_SUPPORT.get(integration_id, "hybrid")
    display = DISPLAY_OVERRIDES.get(integration_id, {})
    category = service_def.get("category", "productivity")
    config_fields = _build_config_fields(service_def)

    return {
        "integration_id": integration_id,
        "name": service_def.get("name", _humanize_key(integration_id)),
        "description": service_def.get("description", ""),
        "category": category,
        "category_label": CATEGORY_LABELS.get(category, _humanize_key(category)),
        "icon": display.get("icon", "plug"),
        "color": display.get("color", "#64748B"),
        "features": list(service_def.get("capabilities") or []),
        "capabilities": list(service_def.get("capabilities") or []),
        "docs_url": service_def.get("docs_url", ""),
        "oauth_url": service_def.get("oauth_url", ""),
        "config_fields": config_fields,
        "required_fields": [field["key"] for field in config_fields if field.get("required")],
        "runtime_support": runtime_support,
        "maturity": MATURITY_BY_RUNTIME.get(runtime_support, "configurable"),
        "connection_mode": "social_account" if category in SOCIAL_CATEGORIES else "workspace_config",
        "supports_system_config": category not in SOCIAL_CATEGORIES,
        "verification_mode": "config",
    }


def _build_available_integrations():
    catalog = []
    for integration_id, service_def in INTEGRATION_SERVICES.items():
        catalog.append(_build_catalog_entry(integration_id, service_def))
    catalog.sort(key=lambda item: (item["category"], item["name"].lower()))
    return catalog


AVAILABLE_INTEGRATIONS = _build_available_integrations()
AVAILABLE_INTEGRATIONS_BY_ID = {
    integration["integration_id"]: integration for integration in AVAILABLE_INTEGRATIONS
}


def _mask_value(value):
    if not isinstance(value, str):
        return value
    if len(value) <= 4:
        return "****"
    return f"{value[:4]}****"


def _mask_config(config):
    safe_config = {}
    for key, value in (config or {}).items():
        safe_config[key] = _mask_value(value)
    return safe_config


def _derive_connection_status(template, config, system_config=None, existing_status=None):
    required_fields = template.get("required_fields", [])
    missing_required_fields = [field for field in required_fields if not config.get(field)]
    system_required_fields = INTEGRATION_SERVICES.get(template["integration_id"], {}).get("key_fields", [])
    system_missing_fields = [field for field in system_required_fields if not (system_config or {}).get(field)]

    user_configured = bool(config) and not missing_required_fields
    system_configured = bool(system_required_fields) and not system_missing_fields

    if template["runtime_support"] == "planned":
        verification_status = "planned"
    elif not required_fields and not config and template["connection_mode"] == "workspace_config":
        verification_status = existing_status or "disconnected"
    elif missing_required_fields:
        verification_status = "incomplete"
    elif user_configured or system_configured:
        verification_status = existing_status or "verified"
    else:
        verification_status = existing_status or "configured"

    execution_ready = template["runtime_support"] != "planned" and (user_configured or system_configured)

    return {
        "configured_fields_count": len([field for field in required_fields if config.get(field)]),
        "required_fields_count": len(required_fields),
        "missing_required_fields": missing_required_fields,
        "user_configured": user_configured,
        "system_configured": system_configured,
        "system_missing_fields": system_missing_fields,
        "verification_status": verification_status,
        "execution_ready": execution_ready,
    }


def _normalize_connected_doc(template, raw_doc, source, system_keys=None):
    if not raw_doc:
        return None

    raw_config = raw_doc.get("credentials") if source == "social_connections" else raw_doc.get("config")
    config = raw_config or {}
    system_config = (system_keys or {}).get(template["integration_id"], {})
    status_meta = _derive_connection_status(
        template,
        config,
        system_config=system_config,
        existing_status=raw_doc.get("verification_status"),
    )

    connected_at = raw_doc.get("connected_at") or raw_doc.get("created_at")
    updated_at = raw_doc.get("updated_at") or connected_at
    enabled = raw_doc.get("is_active", True) if source == "social_connections" else raw_doc.get("enabled", True)

    return {
        "integration_id": template["integration_id"],
        "name": template["name"],
        "category": template["category"],
        "category_label": template["category_label"],
        "description": template["description"],
        "enabled": enabled,
        "status": raw_doc.get("status", "connected" if enabled else "disabled"),
        "connected_at": connected_at,
        "updated_at": updated_at,
        "last_verified_at": raw_doc.get("last_verified_at"),
        "config": _mask_config(config),
        "source": source,
        "account_name": raw_doc.get("account_name", ""),
        "account_id": raw_doc.get("account_id", ""),
        "runtime_support": template["runtime_support"],
        "maturity": template["maturity"],
        "supports_system_config": template["supports_system_config"],
        **status_meta,
    }


async def get_integrations():
    return [deepcopy(item) for item in AVAILABLE_INTEGRATIONS]


async def get_effective_integration_config(user_id, integration_id):
    canonical_id = canonicalize_integration_id(integration_id)
    template = AVAILABLE_INTEGRATIONS_BY_ID.get(canonical_id)
    if not template:
        return {}

    system_keys = await get_integration_keys()
    system_config = dict(system_keys.get(canonical_id, {}) or {})
    effective = dict(system_config)

    if template["connection_mode"] == "social_account":
        user_doc = await db.social_connections.find_one(
            {"user_id": user_id, "platform": canonical_id},
            {"_id": 0, "credentials": 1, "is_active": 1},
        )
        user_config = (user_doc or {}).get("credentials", {}) or {}
        effective.update(user_config)
        return {
            "integration_id": canonical_id,
            "config": effective,
            "has_user_config": bool(user_config),
            "has_system_config": bool(system_config),
            "enabled": (user_doc or {}).get("is_active", False),
        }

    user_doc = await db.user_integrations.find_one(
        {"user_id": user_id, "integration_id": canonical_id},
        {"_id": 0, "config": 1, "enabled": 1},
    )
    user_config = (user_doc or {}).get("config", {}) or {}
    effective.update(user_config)
    return {
        "integration_id": canonical_id,
        "config": effective,
        "has_user_config": bool(user_config),
        "has_system_config": bool(system_config),
        "enabled": (user_doc or {}).get("enabled", False) if user_doc else False,
    }


async def get_user_integrations(user_id):
    system_keys = await get_integration_keys()
    normalized = {}

    social_docs = await db.social_connections.find({"user_id": user_id}, {"_id": 0}).to_list(None)
    for doc in social_docs:
        integration_id = canonicalize_integration_id(doc.get("platform"))
        template = AVAILABLE_INTEGRATIONS_BY_ID.get(integration_id)
        if not template:
            continue
        normalized[integration_id] = _normalize_connected_doc(
            template,
            doc,
            "social_connections",
            system_keys=system_keys,
        )

    user_docs = await db.user_integrations.find({"user_id": user_id}, {"_id": 0}).to_list(None)
    for doc in user_docs:
        integration_id = canonicalize_integration_id(doc.get("integration_id"))
        template = AVAILABLE_INTEGRATIONS_BY_ID.get(integration_id)
        if not template:
            continue
        if integration_id in normalized and template["connection_mode"] == "social_account":
            continue
        normalized[integration_id] = _normalize_connected_doc(
            template,
            doc,
            "user_integrations",
            system_keys=system_keys,
        )

    results = [item for item in normalized.values() if item]
    results.sort(key=lambda item: (item["category"], item["name"].lower()))
    return results


async def get_integration_overview(user_id):
    available = await get_integrations()
    connected = await get_user_integrations(user_id)
    connected_by_id = {item["integration_id"]: item for item in connected}

    available_with_status = []
    for item in available:
        connection = connected_by_id.get(item["integration_id"])
        available_with_status.append({
            **item,
            "is_connected": bool(connection),
            "verification_status": connection.get("verification_status") if connection else "disconnected",
            "execution_ready": connection.get("execution_ready", False) if connection else False,
            "enabled": connection.get("enabled", False) if connection else False,
        })

    categories = {}
    for item in available_with_status:
        cat = item["category"]
        category_entry = categories.setdefault(cat, {"available": 0, "connected": 0, "ready": 0})
        category_entry["available"] += 1
        if item["is_connected"]:
            category_entry["connected"] += 1
        if item["execution_ready"]:
            category_entry["ready"] += 1

    return {
        "available": available_with_status,
        "connected": connected,
        "connected_ids": [item["integration_id"] for item in connected],
        "summary": {
            "total_available": len(available_with_status),
            "connected": len(connected),
            "ready": len([item for item in connected if item.get("execution_ready")]),
            "incomplete": len([item for item in connected if item.get("verification_status") == "incomplete"]),
            "planned": len([item for item in available_with_status if item.get("maturity") == "planned"]),
            "categories": categories,
        },
    }


async def save_user_integration(user_id, data):
    integration_id = canonicalize_integration_id(data.get("integration_id"))
    template = AVAILABLE_INTEGRATIONS_BY_ID.get(integration_id)
    if not template:
        return None

    now = datetime.now(timezone.utc).isoformat()
    config = data.get("config", {}) or {}
    enabled = data.get("enabled", True)
    system_keys = await get_integration_keys()
    status_meta = _derive_connection_status(
        template,
        config,
        system_config=system_keys.get(integration_id, {}),
    )

    if template["connection_mode"] == "social_account":
        existing = await db.social_connections.find_one(
            {"user_id": user_id, "platform": integration_id},
            {"_id": 0, "connected_at": 1},
        )
        doc = {
            "user_id": user_id,
            "platform": integration_id,
            "credentials": config,
            "account_name": data.get("account_name", ""),
            "account_id": data.get("account_id", ""),
            "is_active": enabled,
            "status": "connected",
            "connected_at": (existing or {}).get("connected_at", now),
            "updated_at": now,
            "last_verified_at": now,
            "verification_status": status_meta["verification_status"],
        }
        await db.social_connections.update_one(
            {"user_id": user_id, "platform": integration_id},
            {"$set": doc},
            upsert=True,
        )
        raw_doc = await db.social_connections.find_one(
            {"user_id": user_id, "platform": integration_id},
            {"_id": 0},
        )
        return _normalize_connected_doc(template, raw_doc, "social_connections", system_keys=system_keys)

    existing = await db.user_integrations.find_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"_id": 0, "connected_at": 1},
    )
    doc = {
        "user_id": user_id,
        "integration_id": integration_id,
        "name": template["name"],
        "category": template["category"],
        "config": config,
        "enabled": enabled,
        "status": "connected",
        "connected_at": (existing or {}).get("connected_at", now),
        "updated_at": now,
        "last_verified_at": now,
        "verification_status": status_meta["verification_status"],
    }
    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"$set": doc},
        upsert=True,
    )
    raw_doc = await db.user_integrations.find_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"_id": 0},
    )
    return _normalize_connected_doc(template, raw_doc, "user_integrations", system_keys=system_keys)


async def disconnect_integration(user_id, integration_id):
    canonical_id = canonicalize_integration_id(integration_id)
    aliases = [legacy for legacy, target in LEGACY_INTEGRATION_IDS.items() if target == canonical_id]
    match_ids = [canonical_id, *aliases]

    await db.user_integrations.delete_many({"user_id": user_id, "integration_id": {"$in": match_ids}})
    await db.social_connections.delete_many({"user_id": user_id, "platform": {"$in": match_ids}})
    return {"status": "disconnected", "integration_id": canonical_id}


async def toggle_integration(user_id, integration_id, enabled):
    canonical_id = canonicalize_integration_id(integration_id)
    system_keys = await get_integration_keys()
    now = datetime.now(timezone.utc).isoformat()

    social_result = await db.social_connections.find_one({"user_id": user_id, "platform": canonical_id}, {"_id": 0})
    if social_result:
        await db.social_connections.update_one(
            {"user_id": user_id, "platform": canonical_id},
            {"$set": {"is_active": enabled, "status": "connected" if enabled else "disabled", "updated_at": now}},
        )
        raw_doc = await db.social_connections.find_one({"user_id": user_id, "platform": canonical_id}, {"_id": 0})
        template = AVAILABLE_INTEGRATIONS_BY_ID.get(canonical_id)
        return _normalize_connected_doc(template, raw_doc, "social_connections", system_keys=system_keys)

    user_result = await db.user_integrations.find_one({"user_id": user_id, "integration_id": canonical_id}, {"_id": 0})
    if not user_result:
        return None

    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": canonical_id},
        {"$set": {"enabled": enabled, "status": "connected" if enabled else "disabled", "updated_at": now}},
    )
    raw_doc = await db.user_integrations.find_one({"user_id": user_id, "integration_id": canonical_id}, {"_id": 0})
    template = AVAILABLE_INTEGRATIONS_BY_ID.get(canonical_id)
    return _normalize_connected_doc(template, raw_doc, "user_integrations", system_keys=system_keys)


async def verify_user_integration(user_id, integration_id):
    canonical_id = canonicalize_integration_id(integration_id)
    template = AVAILABLE_INTEGRATIONS_BY_ID.get(canonical_id)
    if not template:
        return None

    connected = await get_user_integrations(user_id)
    current = next((item for item in connected if item["integration_id"] == canonical_id), None)
    if not current:
        return {
            "integration_id": canonical_id,
            "verification_status": "not_connected",
            "execution_ready": False,
            "message": "Integration is not connected yet.",
        }

    now = datetime.now(timezone.utc).isoformat()
    verification_status = current["verification_status"]
    message = "Integration is configured and ready for runtime use."
    if verification_status == "planned":
        message = "Connector is cataloged, but runtime execution is not wired yet."
    elif verification_status == "incomplete":
        message = "Integration is missing required fields."
    elif not current["execution_ready"]:
        message = "Integration is saved, but runtime access is not ready yet."

    if current["source"] == "social_connections":
        await db.social_connections.update_one(
            {"user_id": user_id, "platform": canonical_id},
            {"$set": {"last_verified_at": now, "verification_status": verification_status}},
        )
    else:
        await db.user_integrations.update_one(
            {"user_id": user_id, "integration_id": canonical_id},
            {"$set": {"last_verified_at": now, "verification_status": verification_status}},
        )

    refreshed = await get_user_integrations(user_id)
    updated = next((item for item in refreshed if item["integration_id"] == canonical_id), current)
    return {**updated, "message": message}
