"""Artifact registry for durable outputs created by agents and tools."""
import json
import uuid
from datetime import datetime, timezone

from db import db


ARTIFACT_COLLECTION = "artifacts"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _artifact_id():
    return f"art_{uuid.uuid4().hex[:12]}"


def _preview_from_payload(payload):
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload[:500]
    try:
        return json.dumps(payload, default=str)[:500]
    except Exception:
        return str(payload)[:500]


async def create_artifact(
    user_id: str,
    artifact_type: str,
    title: str,
    payload=None,
    source_tool: str = "",
    source_integration: str = "",
    content_type: str = "application/json",
    status: str = "created",
    metadata: dict = None,
):
    doc = {
        "artifact_id": _artifact_id(),
        "user_id": user_id,
        "artifact_type": artifact_type,
        "title": title,
        "payload": payload,
        "preview": _preview_from_payload(payload),
        "content_type": content_type,
        "status": status,
        "source_tool": source_tool,
        "source_integration": source_integration,
        "metadata": metadata or {},
        "created_at": _now(),
        "updated_at": _now(),
    }
    await db[ARTIFACT_COLLECTION].insert_one(doc)
    doc.pop("_id", None)
    return doc


async def list_artifacts(user_id: str, artifact_type: str = None, limit: int = 50):
    query = {"user_id": user_id}
    if artifact_type:
        query["artifact_type"] = artifact_type
    cursor = db[ARTIFACT_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_artifact(user_id: str, artifact_id: str):
    return await db[ARTIFACT_COLLECTION].find_one(
        {"user_id": user_id, "artifact_id": artifact_id},
        {"_id": 0},
    )
