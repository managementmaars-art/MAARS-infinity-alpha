"""MAARS — Kernel: Approval Controller. Manages approval workflows and checkpoint gates."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

APPROVAL_COLLECTION = "approvals"


async def request_approval(task_id: str, graph_id: str, action: str, reason: str, requester: str = "system", urgency: str = "normal"):
    """Create an approval request."""
    approval = {
        "task_id": task_id, "graph_id": graph_id, "action": action,
        "reason": reason, "requester": requester, "urgency": urgency,
        "status": "pending", "approver": None, "decision_notes": None,
        "created_at": datetime.now(timezone.utc).isoformat(), "decided_at": None,
    }
    await db[APPROVAL_COLLECTION].insert_one(approval)
    await log_action("approval_requested", requester, "approval_controller", "task", task_id, {"action": action})
    approval.pop("_id", None)
    return approval


async def decide_approval(task_id: str, approved: bool, approver: str, notes: str = ""):
    """Approve or deny a pending request."""
    decision = "approved" if approved else "denied"
    await db[APPROVAL_COLLECTION].update_one(
        {"task_id": task_id, "status": "pending"},
        {"$set": {"status": decision, "approver": approver, "decision_notes": notes, "decided_at": datetime.now(timezone.utc).isoformat()}},
    )
    await log_action(f"approval_{decision}", approver, "approval_controller", "task", task_id)
    return {"task_id": task_id, "status": decision, "approver": approver}


async def get_pending_approvals(limit: int = 50):
    """Get all pending approval requests."""
    cursor = db[APPROVAL_COLLECTION].find({"status": "pending"}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_approval_history(limit: int = 50):
    """Get approval decision history."""
    cursor = db[APPROVAL_COLLECTION].find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
