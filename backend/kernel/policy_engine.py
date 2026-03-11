"""MAARS Kernel — Policy Engine.
Enforces rules and constraints across all system operations.
Policies are stored in DB and evaluated before any controlled action."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

POLICY_COLLECTION = "policies"

# Default policies seeded on first run
DEFAULT_POLICIES = [
    {
        "policy_id": "max_daily_spend",
        "name": "Maximum Daily Spend",
        "category": "budget",
        "rule": {"type": "threshold", "metric": "daily_spend", "max_value": 100.0},
        "action_on_violation": "block",
        "severity": "high",
        "active": True,
    },
    {
        "policy_id": "max_agent_autonomy",
        "name": "Maximum Agent Autonomy",
        "category": "autonomy",
        "rule": {"type": "max_tier", "max_value": 3},
        "action_on_violation": "require_approval",
        "severity": "medium",
        "active": True,
    },
    {
        "policy_id": "require_verification",
        "name": "Require Verification for High-Risk",
        "category": "verification",
        "rule": {"type": "risk_threshold", "min_risk": "high"},
        "action_on_violation": "block",
        "severity": "critical",
        "active": True,
    },
    {
        "policy_id": "max_retry_count",
        "name": "Maximum Retry Count",
        "category": "execution",
        "rule": {"type": "threshold", "metric": "retry_count", "max_value": 5},
        "action_on_violation": "escalate",
        "severity": "medium",
        "active": True,
    },
    {
        "policy_id": "simulation_mode_default",
        "name": "Simulation Mode Default",
        "category": "safety",
        "rule": {"type": "default_environment", "value": "simulation"},
        "action_on_violation": "block",
        "severity": "critical",
        "active": True,
    },
]


async def seed_default_policies():
    """Seed default policies if not present."""
    for policy in DEFAULT_POLICIES:
        existing = await db[POLICY_COLLECTION].find_one({"policy_id": policy["policy_id"]})
        if not existing:
            policy["created_at"] = datetime.now(timezone.utc).isoformat()
            await db[POLICY_COLLECTION].insert_one(policy)


async def get_policies(category: str = None, active_only: bool = True):
    """Get all policies, optionally filtered."""
    query = {}
    if category:
        query["category"] = category
    if active_only:
        query["active"] = True
    cursor = db[POLICY_COLLECTION].find(query, {"_id": 0})
    return await cursor.to_list(length=100)


async def evaluate_policy(policy_id: str, context: dict):
    """Evaluate a single policy against a context dict.
    Returns {passed, action, reason}."""
    policy = await db[POLICY_COLLECTION].find_one({"policy_id": policy_id, "active": True}, {"_id": 0})
    if not policy:
        return {"passed": True, "action": None, "reason": "policy_not_found"}

    rule = policy["rule"]
    rule_type = rule.get("type")

    if rule_type == "threshold":
        metric_val = context.get(rule["metric"], 0)
        if metric_val > rule["max_value"]:
            await log_action(
                "policy_violation", "system", "policy_engine",
                target_type="policy", target_id=policy_id,
                details={"context": context, "rule": rule},
                result="violation",
            )
            return {"passed": False, "action": policy["action_on_violation"], "reason": f"{rule['metric']} ({metric_val}) exceeds max ({rule['max_value']})"}

    elif rule_type == "max_tier":
        tier = context.get("autonomy_tier", 0)
        if tier > rule["max_value"]:
            return {"passed": False, "action": policy["action_on_violation"], "reason": f"autonomy tier {tier} exceeds max {rule['max_value']}"}

    elif rule_type == "risk_threshold":
        risk = context.get("risk_level", "low")
        risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        if risk_order.get(risk, 0) >= risk_order.get(rule["min_risk"], 2):
            verified = context.get("verified", False)
            if not verified:
                return {"passed": False, "action": policy["action_on_violation"], "reason": f"high-risk output not verified"}

    return {"passed": True, "action": None, "reason": "ok"}


async def check_all_policies(context: dict, categories: list = None):
    """Evaluate all active policies (optionally filtered by category).
    Returns {all_passed, violations: []}."""
    policies = await get_policies(category=None, active_only=True)
    if categories:
        policies = [p for p in policies if p["category"] in categories]

    violations = []
    for policy in policies:
        result = await evaluate_policy(policy["policy_id"], context)
        if not result["passed"]:
            violations.append({**result, "policy_id": policy["policy_id"], "policy_name": policy["name"]})

    return {"all_passed": len(violations) == 0, "violations": violations}
