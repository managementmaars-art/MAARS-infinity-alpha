"""Cost-optimization toggles — the operator-settable "turn this on to cut cost" switches.

Each lever here represents a specific cost-reduction action the
operator can take (install local GPU, self-host SMTP, switch voice
provider, etc). The ledger (`plan_economics_full`) reads this config
and recomputes the all-in cost per plan accordingly.

Toggles are stored in Mongo `cost_config` (one singleton doc) so the
operator can flip them from the admin UI without touching env vars.
For levers that require an accompanying env var (e.g. MAARS_SMTP_HOST
for SMTP host), the toggle is a "claim" the operator makes — they're
saying "I've configured this infrastructure, charge my ledger
accordingly." The backend verifies the claim when possible (checks env
vars exist, pings the local server) and reports status.

Levers:
  local_media          — SDXL/Whisper/XTTS/SVD self-host → media $0
  self_smtp            — Postfix self-host → email $0
  telnyx_voice         — Telnyx instead of Twilio → voice ~45% off
  native_lead_research — BrowserAgent scraping → Apollo $0
  proxy_pool           — residential proxy pool active
"""
from __future__ import annotations
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LEVERS = {
    "local_media":          {"active": False, "configured": False, "savings_per_heavy_client_usd": 18.0},
    "self_smtp":            {"active": False, "configured": False, "savings_per_heavy_client_usd": 0.40},
    "telnyx_voice":         {"active": False, "configured": False, "savings_per_heavy_client_usd": 5.00},
    "native_lead_research": {"active": True,  "configured": True,  "savings_per_heavy_client_usd": 15.0},
    "proxy_pool":           {"active": False, "configured": False, "savings_per_heavy_client_usd": 0.0},
}


async def _check_env() -> dict[str, bool]:
    """Detect whether each lever's prerequisite env vars are set.
    This is the 'configured' check — infrastructure detected, not
    necessarily verified healthy."""
    return {
        "local_media":          bool(os.environ.get("MAARS_LOCAL_IMAGE_URL")),
        "self_smtp":            bool(os.environ.get("MAARS_SMTP_HOST")),
        "telnyx_voice":         bool(os.environ.get("TELNYX_API_KEY")),
        "native_lead_research": True,   # always configured — uses built-in BrowserAgent
        "proxy_pool":           bool(os.environ.get("MAARS_PROXY_POOL")),
    }


async def get_config() -> dict[str, Any]:
    """Current toggle state merged with env detection.

    Returns:
      {
        levers: {
          local_media: {active, configured, env_detected, savings_per_heavy_client_usd, ...}
          ...
        },
        updated_at, updated_by
      }
    """
    from db import db
    doc = await db.cost_config.find_one({"_id": "singleton"}) or {}
    env = await _check_env()
    levers: dict[str, dict] = {}
    for key, default in DEFAULT_LEVERS.items():
        saved = (doc.get("levers") or {}).get(key) or {}
        # active = operator toggled on AND env detected
        env_ok = env.get(key, False)
        active_claim = bool(saved.get("active", default["active"]))
        levers[key] = {
            "active":        active_claim and env_ok,
            "active_claim":  active_claim,
            "configured":    env_ok,
            "env_detected":  env_ok,
            "savings_per_heavy_client_usd": default["savings_per_heavy_client_usd"],
            "last_changed":  saved.get("last_changed"),
        }
    return {
        "levers":      levers,
        "updated_at":  doc.get("updated_at"),
        "updated_by":  doc.get("updated_by"),
    }


async def set_lever(key: str, *, active: bool, updated_by: str = "") -> dict[str, Any]:
    """Flip one toggle. Persists operator intent; actual activation also
    requires the env var to be set (enforced at read time in get_config)."""
    if key not in DEFAULT_LEVERS:
        raise ValueError(f"unknown lever '{key}'")
    from db import db
    now = time.time()
    await db.cost_config.update_one(
        {"_id": "singleton"},
        {"$set": {
            f"levers.{key}": {"active": bool(active), "last_changed": now},
            "updated_at": now,
            "updated_by": updated_by,
        }},
        upsert=True,
    )
    return await get_config()


async def summary_savings(active_heavy_clients: int = 10) -> dict[str, Any]:
    """Forward-look: 'If you activate every lever not yet on, you'd save
    $X/month across your active client fleet.' Used by the UI to pitch
    the operator on enabling the remaining switches."""
    cfg = await get_config()
    total_current = 0.0
    total_possible = 0.0
    missing = []
    for key, state in cfg["levers"].items():
        savings = float(state["savings_per_heavy_client_usd"]) * active_heavy_clients
        total_possible += savings
        if state["active"]:
            total_current += savings
        else:
            missing.append({
                "key":      key,
                "savings":  round(savings, 2),
                "env_detected":  state["env_detected"],
                "active_claim":  state["active_claim"],
            })
    return {
        "active_heavy_clients": active_heavy_clients,
        "current_monthly_savings_usd": round(total_current, 2),
        "possible_monthly_savings_usd": round(total_possible, 2),
        "untapped_monthly_savings_usd": round(total_possible - total_current, 2),
        "levers_off": missing,
    }
