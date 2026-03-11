"""MAARS — Governance: Incident Management + Escalation."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

INCIDENT_COLLECTION = "incidents"
ESCALATION_COLLECTION = "escalations"


async def create_incident(incident_type: str, severity: str, description: str, affected: list = None):
    """Create an incident record."""
    incident = {
        "type": incident_type, "severity": severity, "description": description,
        "affected_components": affected or [], "status": "open",
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None, "resolution": None, "postmortem": None,
        "escalation_level": 0, "assigned_to": None,
    }
    await db[INCIDENT_COLLECTION].insert_one(incident)
    await log_action("incident_created", "system", "incident_manager", details={"type": incident_type, "severity": severity})
    incident.pop("_id", None)
    return incident


async def resolve_incident(incident_type: str, resolution: str, postmortem: str = ""):
    """Resolve an incident."""
    now = datetime.now(timezone.utc).isoformat()
    await db[INCIDENT_COLLECTION].update_one(
        {"type": incident_type, "status": "open"},
        {"$set": {"status": "resolved", "resolved_at": now, "resolution": resolution, "postmortem": postmortem}},
    )
    return {"type": incident_type, "status": "resolved"}


async def get_incidents(status: str = None, severity: str = None, limit: int = 50):
    """List incidents."""
    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity
    cursor = db[INCIDENT_COLLECTION].find(query, {"_id": 0}).sort("detected_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def escalate(source_task_id: str, reason: str, severity: str = "high"):
    """Create an escalation."""
    escalation = {
        "source_task_id": source_task_id, "reason": reason, "severity": severity,
        "status": "open", "current_handler": "operator",
        "escalation_chain": ["agent", "supervisor", "operator"],
        "created_at": datetime.now(timezone.utc).isoformat(), "resolved_at": None,
    }
    await db[ESCALATION_COLLECTION].insert_one(escalation)
    await log_action("escalation_created", "system", "escalation_system", "task", source_task_id, {"severity": severity})
    escalation.pop("_id", None)
    return escalation


async def get_escalations(status: str = "open", limit: int = 50):
    """List escalations."""
    query = {}
    if status:
        query["status"] = status
    cursor = db[ESCALATION_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def resolve_escalation(source_task_id: str, resolution: str):
    """Resolve an escalation."""
    await db[ESCALATION_COLLECTION].update_one(
        {"source_task_id": source_task_id, "status": "open"},
        {"$set": {"status": "resolved", "resolved_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"source_task_id": source_task_id, "status": "resolved"}
