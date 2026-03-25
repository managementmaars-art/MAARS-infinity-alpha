"""MAARS — Multi-Environment Segregation.
Enforces staging vs production separation for data, policies, and execution."""

import os
import logging
from datetime import datetime, timezone
from db import db

logger = logging.getLogger(__name__)

ENV_CONFIG_COLLECTION = "environment_configs"

# Supported environments
ENVIRONMENTS = {
    "production": {
        "label": "Production",
        "color": "red",
        "requires_approval": True,
        "max_autonomy_tier": 3,
        "budget_multiplier": 1.0,
        "allowed_models": ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-pro"],
        "rate_limit_rpm": 60,
        "data_retention_days": 365,
    },
    "staging": {
        "label": "Staging",
        "color": "amber",
        "requires_approval": False,
        "max_autonomy_tier": 5,
        "budget_multiplier": 0.5,
        "allowed_models": ["gpt-4o", "gpt-4o-mini", "claude-sonnet-4.5", "gemini-3-flash"],
        "rate_limit_rpm": 120,
        "data_retention_days": 90,
    },
    "sandbox": {
        "label": "Sandbox",
        "color": "blue",
        "requires_approval": False,
        "max_autonomy_tier": 10,
        "budget_multiplier": 0.1,
        "allowed_models": ["gpt-4o-mini", "gemini-3-flash"],
        "rate_limit_rpm": 300,
        "data_retention_days": 30,
    },
    "simulation": {
        "label": "Simulation",
        "color": "zinc",
        "requires_approval": False,
        "max_autonomy_tier": 10,
        "budget_multiplier": 0.0,
        "allowed_models": ["gpt-4o-mini", "gemini-3-flash"],
        "rate_limit_rpm": 999,
        "data_retention_days": 7,
    },
}

# Active environment (default from env var or sandbox)
_active_env = os.environ.get("MAARS_ENVIRONMENT", "sandbox")


def get_active_environment():
    """Get the currently active environment."""
    return _active_env


def set_active_environment(env: str):
    """Set the active environment (runtime only)."""
    global _active_env
    if env not in ENVIRONMENTS:
        return {"error": f"Unknown environment: {env}. Valid: {list(ENVIRONMENTS.keys())}"}
    _active_env = env
    return {"environment": env, "status": "active"}


def get_environment_config(env: str = None):
    """Get configuration for an environment."""
    env = env or _active_env
    config = ENVIRONMENTS.get(env)
    if not config:
        return None
    return {"environment": env, **config}


def get_all_environments():
    """Get all environment configurations."""
    return [{"environment": k, **v} for k, v in ENVIRONMENTS.items()]


def validate_execution_environment(requested_env: str, autonomy_tier: int = 1, model: str = None):
    """Validate whether an execution is allowed in the requested environment."""
    config = ENVIRONMENTS.get(requested_env)
    if not config:
        return {"allowed": False, "reason": f"Unknown environment: {requested_env}"}

    violations = []

    # Check autonomy tier
    if autonomy_tier > config["max_autonomy_tier"]:
        violations.append(
            f"Autonomy tier {autonomy_tier} exceeds max {config['max_autonomy_tier']} for {requested_env}"
        )

    # Check model allowed
    if model and config["allowed_models"] and model not in config["allowed_models"]:
        violations.append(
            f"Model {model} not allowed in {requested_env}. Allowed: {config['allowed_models']}"
        )

    if violations:
        return {"allowed": False, "reason": "; ".join(violations), "violations": violations}

    return {"allowed": True, "environment": requested_env, "config": config}


def get_collection_name(base_name: str, env: str = None):
    """Get environment-scoped collection name for data segregation."""
    env = env or _active_env
    if env == "production":
        return base_name
    return f"{base_name}_{env}"


async def get_environment_stats():
    """Get statistics for each environment."""
    stats = []
    for env_name in ENVIRONMENTS:
        # Count executions per environment
        exec_count = await db["runtime_executions"].count_documents({"environment": env_name})
        run_count = await db["execution_runs"].count_documents({"environment": env_name})
        stats.append({
            "environment": env_name,
            **ENVIRONMENTS[env_name],
            "executions": exec_count,
            "runs": run_count,
        })
    return stats


async def store_environment_config(env: str, overrides: dict):
    """Store custom environment config overrides in DB."""
    allowed_overrides = {
        "requires_approval", "max_autonomy_tier", "budget_multiplier",
        "rate_limit_rpm", "data_retention_days",
    }
    filtered = {k: v for k, v in overrides.items() if k in allowed_overrides}
    if not filtered:
        return {"error": "No valid overrides provided"}

    now = datetime.now(timezone.utc).isoformat()
    await db[ENV_CONFIG_COLLECTION].update_one(
        {"environment": env},
        {"$set": {**filtered, "updated_at": now}, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )

    # Apply overrides to runtime config
    if env in ENVIRONMENTS:
        ENVIRONMENTS[env].update(filtered)

    return {"environment": env, "overrides": filtered, "status": "applied"}
