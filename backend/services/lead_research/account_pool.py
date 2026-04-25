"""Multi-LinkedIn account rotation for the scraper.

One LinkedIn account doing Sales Navigator at scale gets flagged.
Five accounts round-robined behave like five different sales reps —
LinkedIn's anti-scraping heuristics watch per-account rate, not
per-IP (they assume one human = one account).

Accounts live in `credential_vault` under provider="linkedin_scrape".
The scraper picks the next idle account, uses it for a session, and
cools it down on challenge pages.

State per account tracked in Mongo `linkedin_account_state`:
  {_id: email, state: 'idle'|'in_use'|'cooldown'|'burned',
   last_used_ts, pulls, challenges, last_error}

Accounts get cooled down for 1 hour on a challenge page, 24 hours on
a login failure, and marked "burned" (needs operator attention) after
3 consecutive challenges.

Public API:
  async register(email, password, *, label=None, scope="system")
  async get_available() -> {"email","password","id"} | None
  async mark_success(email)
  async mark_challenge(email)
  async mark_login_failed(email)
  async snapshot() -> list
"""
from __future__ import annotations
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

COOLDOWN_CHALLENGE = 3600          # 1 hour
COOLDOWN_LOGIN_FAIL = 24 * 3600    # 1 day
MAX_CONSECUTIVE_CHALLENGES = 3


async def register(email: str, password: str, *,
                   label: str | None = None,
                   scope: str = "system",
                   scope_id: str = "global") -> dict[str, Any]:
    """Store an account in credential_vault + initialize pool state.
    Each account gets its own vault row keyed by email so the secret
    is encrypted at rest."""
    from services import credential_vault
    from db import db
    await credential_vault.put(credential_vault.Credential(
        scope=scope, scope_id=scope_id,
        provider="linkedin_scrape",
        kind=f"account_{email.lower()}",
        secret=f"{email}\n{password}",
        public={"email": email, "label": label or email},
    ))
    await db.linkedin_account_state.update_one(
        {"_id": email.lower()},
        {"$setOnInsert": {
            "_id": email.lower(), "email": email, "label": label,
            "state": "idle", "pulls": 0, "challenges": 0,
            "created_at": time.time(),
        }},
        upsert=True,
    )
    return {"ok": True, "email": email}


async def _load_credentials_for(email: str) -> dict[str, str] | None:
    """Pull the stored email + password back out of the vault."""
    from services import credential_vault
    # Try all three scopes — account may be system-wide or per-org.
    for scope, scope_id in [("system", "global"), ("org", "global"), ("user", email)]:
        c = await credential_vault.get(
            "linkedin_scrape",
            user_id=scope_id if scope == "user" else None,
            org_id=scope_id if scope == "org" else None,
            kind=f"account_{email.lower()}",
            auto_refresh=False,
        )
        if c and c.secret:
            e, _, p = (c.secret or "").partition("\n")
            if e and p: return {"email": e, "password": p}
    return None


async def get_available() -> dict[str, Any] | None:
    """Atomically claim the least-recently-used idle account. Revives
    accounts whose cooldown expired."""
    from db import db
    now = time.time()

    # Revive cooldown'd accounts whose timer expired.
    try:
        await db.linkedin_account_state.update_many(
            {"state": "cooldown", "cooldown_until": {"$lte": now}},
            {"$set": {"state": "idle"}},
        )
    except Exception:
        pass

    try:
        doc = await db.linkedin_account_state.find_one_and_update(
            {"state": "idle"},
            {"$set": {"state": "in_use", "last_used_ts": now},
             "$inc": {"pulls": 1}},
            sort=[("last_used_ts", 1)],
            return_document=True,
        )
    except Exception:
        doc = None
    if not doc: return None

    creds = await _load_credentials_for(doc["_id"])
    if not creds:
        # Vault row missing — mark burned so we skip it.
        await db.linkedin_account_state.update_one(
            {"_id": doc["_id"]},
            {"$set": {"state": "burned", "last_error": "creds missing in vault"}},
        )
        return None
    return {"id": doc["_id"], **creds}


async def mark_success(email: str) -> None:
    from db import db
    await db.linkedin_account_state.update_one(
        {"_id": email.lower()},
        {"$set": {"state": "idle", "last_success_ts": time.time(),
                  "challenges": 0}},
    )


async def mark_challenge(email: str, *, reason: str = "") -> None:
    """LinkedIn showed a challenge / captcha / security page. Cooldown
    this account for an hour; if it hits MAX_CONSECUTIVE_CHALLENGES in
    a row, mark burned."""
    from db import db
    doc = await db.linkedin_account_state.find_one({"_id": email.lower()})
    challenges = int((doc or {}).get("challenges", 0)) + 1
    update: dict[str, Any] = {
        "challenges": challenges,
        "last_challenge_ts": time.time(),
        "last_error": (reason or "challenge")[:200],
    }
    if challenges >= MAX_CONSECUTIVE_CHALLENGES:
        update["state"] = "burned"
    else:
        update["state"] = "cooldown"
        update["cooldown_until"] = time.time() + COOLDOWN_CHALLENGE
    await db.linkedin_account_state.update_one(
        {"_id": email.lower()}, {"$set": update},
    )


async def mark_login_failed(email: str, *, reason: str = "") -> None:
    """Credentials rejected — long cooldown + alert."""
    from db import db
    await db.linkedin_account_state.update_one(
        {"_id": email.lower()},
        {"$set": {
            "state": "cooldown",
            "cooldown_until": time.time() + COOLDOWN_LOGIN_FAIL,
            "last_error": (reason or "login failed")[:200],
            "last_login_fail_ts": time.time(),
        }},
    )


async def release(email: str) -> None:
    """Return an in-use account to idle without claiming
    success/challenge — e.g. caller aborted for an unrelated reason."""
    from db import db
    await db.linkedin_account_state.update_one(
        {"_id": email.lower(), "state": "in_use"},
        {"$set": {"state": "idle"}},
    )


async def revive(email: str) -> bool:
    from db import db
    r = await db.linkedin_account_state.update_one(
        {"_id": email.lower()},
        {"$set": {"state": "idle", "challenges": 0}},
    )
    return bool(r.modified_count)


async def snapshot() -> list[dict[str, Any]]:
    """Admin dashboard — NO passwords returned."""
    from db import db
    try:
        rows = await db.linkedin_account_state.find({}).to_list(200)
    except Exception:
        return []
    return [{
        "email":         r["_id"],
        "state":         r.get("state"),
        "pulls":         r.get("pulls", 0),
        "challenges":    r.get("challenges", 0),
        "last_used_ts":  r.get("last_used_ts"),
        "last_error":    r.get("last_error"),
        "label":         r.get("label"),
    } for r in rows]
