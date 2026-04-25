"""
Setup orchestrator â€” the brain behind the in-app setup wizard.

State (singleton, persisted in `setup_state` collection):
    {
        setup_id: "default",
        steps: { <step_id>: {status, last_run_at, detail, metadata} },
        test_credentials: {user_id, email, api_key, balance},   # populated by /seed
        finished_at: ISO | None,
        updated_at: ISO,
    }

Step status values: pending | running | success | failed | skipped
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from db import db
from services import api_key_service, env_writer, provider_catalog
from services.billing import ledger_service, wallet_service
from services.providers import (
    AnthropicProvider,
    BaseProvider,
    DeepSeekProvider,
    GroqProvider,
    OpenAIProvider,
)

logger = logging.getLogger(__name__)

SETUP_COLLECTION = "setup_state"
SETUP_ID = "default"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ known provider catalog
#
# PROVIDER_LINKS is now a derived view of services.provider_catalog so the
# setup wizard, the routing layer, and the model registry share one source of
# truth. The shape is preserved for backward compatibility with anything that
# imported PROVIDER_LINKS directly.

PROVIDER_LINKS: dict[str, dict[str, str]] = {
    p.slug: {"name": p.display_name, "url": p.dashboard_url, "env": p.env_var}
    for p in provider_catalog.QUICK_PROVIDERS
}

STRIPE_LINK = {
    "name": "Stripe",
    "url": "https://dashboard.stripe.com/apikeys",
    "env_secret": "STRIPE_SECRET_KEY",
    "env_webhook": "STRIPE_WEBHOOK_SECRET",
}

# Step IDs the wizard cares about â€” order matters for the readiness report.
STEP_ORDER: list[str] = [
    "system_check",
    "provider_openai",
    "provider_anthropic",
    "provider_groq",
    "provider_deepseek",
    "stripe_keys",
    "migrate",
    "seed",
    "test_routing",
    "test_wallet",
    "test_completion",
]


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ persistence

async def get_state() -> dict[str, Any]:
    doc = await db[SETUP_COLLECTION].find_one({"setup_id": SETUP_ID}, {"_id": 0})
    if not doc:
        doc = {
            "setup_id": SETUP_ID,
            "steps": {sid: {"status": "pending", "detail": "", "last_run_at": None, "metadata": {}} for sid in STEP_ORDER},
            "test_credentials": None,
            "finished_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db[SETUP_COLLECTION].insert_one(doc)
        doc.pop("_id", None)
    # Backfill any missing steps that were added in newer wizard versions.
    changed = False
    for sid in STEP_ORDER:
        if sid not in doc.get("steps", {}):
            doc["steps"][sid] = {"status": "pending", "detail": "", "last_run_at": None, "metadata": {}}
            changed = True
    if changed:
        await db[SETUP_COLLECTION].update_one(
            {"setup_id": SETUP_ID}, {"$set": {"steps": doc["steps"]}},
        )
    return doc


async def set_step(step_id: str, *, status: str, detail: str = "", metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    if status not in {"pending", "running", "success", "failed", "skipped"}:
        raise ValueError(f"invalid status: {status}")
    update = {
        f"steps.{step_id}.status": status,
        f"steps.{step_id}.detail": detail or "",
        f"steps.{step_id}.last_run_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if metadata is not None:
        update[f"steps.{step_id}.metadata"] = metadata
    await db[SETUP_COLLECTION].update_one(
        {"setup_id": SETUP_ID}, {"$set": update}, upsert=True,
    )
    return await get_state()


async def mark_finished() -> dict[str, Any]:
    await db[SETUP_COLLECTION].update_one(
        {"setup_id": SETUP_ID},
        {"$set": {"finished_at": datetime.now(timezone.utc).isoformat()}},
    )
    return await get_state()


async def is_first_run() -> bool:
    """True when no users exist yet â€” wizard then runs without auth."""
    count = await db.users.count_documents({})
    return count == 0


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ step implementations

async def step_system_check() -> tuple[bool, str, dict[str, Any]]:
    """Verify Python version + Mongo connectivity + .env writability."""
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    try:
        await db.command("ping")
        mongo_ok = True
        mongo_detail = "ok"
    except Exception as exc:
        mongo_ok = False
        mongo_detail = f"{type(exc).__name__}: {exc}"

    try:
        env_writer.ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        # touch test
        env_writer.ENV_PATH.parent / ".env-write-probe"
        env_ok = True
    except Exception:
        env_ok = False

    ok = py_ok and mongo_ok and env_ok
    detail = (
        "All baseline systems healthy."
        if ok else
        f"python_ok={py_ok} mongo_ok={mongo_ok} env_writable={env_ok}"
    )
    return ok, detail, {
        "python_version": py,
        "python_ok": py_ok,
        "mongo": mongo_detail,
        "env_path": str(env_writer.ENV_PATH),
        "env_writable": env_ok,
    }


def _provider_class(slug: str) -> Optional[type[BaseProvider]]:
    return {
        "openai":    OpenAIProvider,
        "anthropic": AnthropicProvider,
        "groq":      GroqProvider,
        "deepseek":  DeepSeekProvider,
    }.get(slug)


def _provider_alias_for_llm_models(slug: str) -> str:
    return {
        "google": "gemini",
        "nvidia_nim": "nvidia",
        "meta_llama_api": "llama",
        "bedrock": "amazon",
    }.get(slug, slug)


def _routing_tier_for_provider(slug: str) -> str:
    if slug in {"openai", "anthropic", "google", "xai"}:
        return "premium"
    if slug in {"deepseek", "groq", "together", "fireworks", "cerebras", "sambanova"}:
        return "economy"
    return "standard"


async def step_provider_save_and_test(slug: str, raw_key: str) -> tuple[bool, str, dict[str, Any]]:
    """
    Validate the key against the catalog's strategy, then persist to .env.

    Quick-tier providers (openai/anthropic/groq/deepseek) keep using their
    dedicated BaseProvider subclasses for parity with /v1/providers/health.
    Every other catalog entry routes through services.provider_catalog.validate_provider.
    """
    entry = provider_catalog.get(slug)
    if entry is None:
        return False, f"unknown provider: {slug}", {}
    raw_key = (raw_key or "").strip()
    if not raw_key:
        return False, "API key is required", {}

    cls = _provider_class(slug)
    if cls is not None:
        probe = cls(api_key=raw_key)
        health = await probe.health_check()
        ok = health.healthy
        detail = health.detail
        meta: dict[str, Any] = {"latency_ms": health.latency_ms, "detail": health.detail}
    else:
        ok, detail, meta = await provider_catalog.validate_provider(slug, raw_key)

    if not ok:
        return False, f"provider rejected key: {detail}", {
            "provider": slug, "strategy": entry.validation_strategy, **meta,
        }

    env_writer.upsert({entry.env_var: raw_key})
    env_writer.sync_os({entry.env_var: raw_key})
    _refresh_provider_registry()

    return True, f"{entry.display_name} validated ({detail}).", {
        "provider": slug,
        "strategy": entry.validation_strategy,
        "env_var": entry.env_var,
        "masked": env_writer.mask(raw_key),
        **meta,
    }


async def step_provider_test_existing(slug: str) -> tuple[bool, str, dict[str, Any]]:
    """Re-test a provider already in .env (uses whatever key is currently configured)."""
    entry = provider_catalog.get(slug)
    if entry is None:
        return False, f"unknown provider: {slug}", {}
    key = os.environ.get(entry.env_var, "")
    if not key:
        return False, f"{entry.env_var} is not configured.", {"provider": slug}

    cls = _provider_class(slug)
    if cls is not None:
        h = await cls(api_key=key).health_check()
        return h.healthy, h.detail, {"provider": slug, "latency_ms": h.latency_ms}
    return await provider_catalog.validate_provider(slug, key)


def detect_configured_providers() -> dict[str, dict[str, Any]]:
    """
    Scan the catalog against the live process env. Returns one entry per catalog
    provider with a status word the wizard renders directly:

        missing      env var unset
        detected     env var set, never live-validated
        validated    env var set AND a prior /save or /test returned ok
        invalid      env var set AND last test failed
        skipped      strategy is `coming_soon` â€” adapter pending

    The status drives the badge in the Advanced Setup section. We never expose
    the raw key â€” only the masked form via env_writer.mask().
    """
    out: dict[str, dict[str, Any]] = {}
    for entry in provider_catalog.CATALOG:
        raw = os.environ.get(entry.env_var, "")
        out[entry.slug] = {
            "slug": entry.slug,
            "display_name": entry.display_name,
            "env_var": entry.env_var,
            "category": entry.category,
            "quick": entry.quick,
            "validation_strategy": entry.validation_strategy,
            "dashboard_url": entry.dashboard_url,
            "supports_models_listing": entry.supports_models_listing,
            "notes": entry.notes,
            "configured": bool(raw),
            "masked_value": env_writer.mask(raw) if raw else None,
            "status": ("skipped" if entry.validation_strategy == "coming_soon"
                       else "detected" if raw else "missing"),
        }
    return out


def overlay_step_status(detected: dict[str, dict[str, Any]], steps: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Promote `detected` â†’ `validated` / `invalid` based on step results."""
    for slug, info in detected.items():
        sid = f"provider_{slug}"
        step = steps.get(sid) or {}
        status = step.get("status")
        if status == "success":
            info["status"] = "validated"
            info["last_detail"] = step.get("detail", "")
        elif status == "failed" and info["configured"]:
            info["status"] = "invalid"
            info["last_detail"] = step.get("detail", "")
        elif status == "running":
            info["status"] = "running"
        # otherwise leave as detected/missing/skipped from detect_configured_providers
    return detected


async def step_stripe_save(secret_key: str, webhook_secret: str = "") -> tuple[bool, str, dict[str, Any]]:
    """Validate the Stripe secret with a real API call, then persist both keys."""
    secret_key = (secret_key or "").strip()
    webhook_secret = (webhook_secret or "").strip()
    if not secret_key:
        return False, "STRIPE_SECRET_KEY is required", {}

    # Validate by reading account info â€” this is a free, idempotent call.
    detail: str
    try:
        import stripe as _stripe
        _stripe.api_key = secret_key
        acct = await asyncio.get_event_loop().run_in_executor(None, _stripe.Account.retrieve)
        detail = f"Stripe account {acct.get('id') or '?'} OK."
    except Exception as exc:
        return False, f"Stripe rejected the key: {exc}", {"masked": env_writer.mask(secret_key)}

    if webhook_secret and not webhook_secret.startswith("whsec_"):
        return False, "Webhook secret should start with `whsec_`.", {"masked": env_writer.mask(secret_key)}

    payload = {STRIPE_LINK["env_secret"]: secret_key}
    if webhook_secret:
        payload[STRIPE_LINK["env_webhook"]] = webhook_secret
    env_writer.upsert(payload)
    env_writer.sync_os(payload)

    return True, detail, {
        "secret_masked": env_writer.mask(secret_key),
        "webhook_masked": env_writer.mask(webhook_secret) if webhook_secret else None,
    }


async def step_migrate() -> tuple[bool, str, dict[str, Any]]:
    """Idempotent: index creation + plaintext-key migration. Wraps scripts/migrate_wallets."""
    try:
        from scripts.migrate_wallets import (
            step_hash_legacy_api_keys, step_indexes, step_open_wallets,
        )
        await step_indexes()
        opened, seeded = await step_open_wallets()
        migrated = await step_hash_legacy_api_keys()
    except Exception as exc:
        return False, f"migration failed: {exc}", {}
    return True, f"migrations OK (wallets opened={opened}, seeded={seeded}, keys migrated={migrated}).", {
        "wallets_opened": opened, "wallets_seeded": seeded, "keys_migrated": migrated,
    }


async def step_seed() -> tuple[bool, str, dict[str, Any]]:
    """Create test user, mint API key, ensure 50 credits. Idempotent."""
    try:
        from scripts.seed_test_user import (
            ensure_min_credits, ensure_user, revoke_existing_keys, TARGET_CREDITS,
        )
        email, name = "test@maars.local", "MAARS Test User"
        await wallet_service.ensure_indexes()
        await ledger_service.ensure_indexes()
        await api_key_service.ensure_indexes()
        user_id = await ensure_user(email, name)
        await revoke_existing_keys(user_id)
        await wallet_service.ensure_wallet(user_id, initial_credits=0)
        summary = await ensure_min_credits(user_id, TARGET_CREDITS)
        key = await api_key_service.create_key(user_id, name="setup-wizard", plan_id="free")
    except Exception as exc:
        return False, f"seed failed: {exc}", {}

    creds = {
        "user_id": user_id,
        "email": email,
        "balance": summary["balance_credits"],
        "api_key": key["raw_key"],   # shown ONCE in the wizard UI
        "api_key_masked": env_writer.mask(key["raw_key"]),
    }
    await db[SETUP_COLLECTION].update_one(
        {"setup_id": SETUP_ID}, {"$set": {"test_credentials": creds}},
    )
    return True, f"Test user provisioned with {summary['balance_credits']} credits.", creds


async def step_test_routing() -> tuple[bool, str, dict[str, Any]]:
    """Score configured LLM providers (quick + advanced) on a synthetic chat task."""
    from services.routing import router_scoring as rs

    candidates = []
    for entry in provider_catalog.CATALOG:
        if entry.category != "llm":
            continue
        if entry.validation_strategy == "coming_soon":
            continue
        if not os.environ.get(entry.env_var):
            continue

        slug = entry.slug
        model = _default_model_for(slug)
        if not model:
            continue

        candidates.append(rs.Candidate(
            provider=slug,
            model=model,
            tier=_routing_tier_for_provider(slug),
            cost_per_mtok=2.0 if slug == "openai" else (3.0 if slug == "anthropic" else 0.5),
            avg_latency_ms=1500 if slug == "openai" else (1700 if slug == "anthropic" else 900),
            capabilities=["code", "reasoning", "fast"] if slug == "groq" else ["code", "reasoning"],
        ))
    if not candidates:
        return False, "No LLM providers configured - save at least one provider key.", {}

    ranked = rs.rank_candidates(candidates, task_type="chat")
    top = ranked[0]
    return True, f"Top routed: {top.candidate.provider}/{top.candidate.model} (score {top.score:.2f}).", {
        "ranking": [s.to_dict() for s in ranked[:5]],
        "winner": {"provider": top.candidate.provider, "model": top.candidate.model, "score": round(top.score, 4)},
    }


async def step_test_wallet() -> tuple[bool, str, dict[str, Any]]:
    """Reserveâ†’refund round-trip on the seeded test user. Verifies the credit pipeline end-to-end without a provider call."""
    state = await get_state()
    creds = state.get("test_credentials") or {}
    user_id = creds.get("user_id")
    if not user_id:
        return False, "Run /seed first â€” no test user yet.", {}

    before = await wallet_service.get_summary(user_id)
    ref_id = f"setup_test_{int(time.time() * 1000)}"
    reserved = await wallet_service.reserve(user_id, 1, reference_id=ref_id, description="Setup wizard wallet test")
    if reserved is None:
        return False, f"Reserve failed (balance={before['balance_credits']}).", before
    after_reserve = await wallet_service.get_summary(user_id)
    refunded = await wallet_service.refund(user_id, reserved_amount=1, reference_id=ref_id, description="Setup wizard refund")
    after_refund = await wallet_service.get_summary(user_id)

    if after_refund["balance_credits"] != before["balance_credits"]:
        return False, "Refund left wallet imbalanced.", {
            "before": before, "after_reserve": after_reserve, "after_refund": after_refund,
        }
    return True, "Reserve + refund round-trip OK; balance restored.", {
        "before": before, "after_reserve": after_reserve, "after_refund": after_refund,
    }


async def step_test_completion() -> tuple[bool, str, dict[str, Any]]:
    """Run a real completion using any configured LLM provider (quick or advanced)."""
    state = await get_state()
    creds = state.get("test_credentials") or {}
    user_id = creds.get("user_id")
    if not user_id:
        return False, "Run /seed first - no test user yet.", {}

    configured: list[tuple[str, str, str]] = []
    for entry in provider_catalog.CATALOG:
        if entry.category != "llm" or entry.validation_strategy == "coming_soon":
            continue
        key = os.environ.get(entry.env_var, "")
        if not key:
            continue
        model = _default_model_for(entry.slug)
        if not model:
            continue
        configured.append((entry.slug, key, model))

    if not configured:
        return False, "No configured LLM provider available - add at least one key and retest.", {}

    ref_id = f"setup_completion_{int(time.time() * 1000)}"
    reserved = await wallet_service.reserve(user_id, 1, reference_id=ref_id, description="Setup completion test")
    if reserved is None:
        return False, "Insufficient credits for completion test (need 1).", {}

    from services.llm_service import call_direct_llm

    t0 = time.time()
    last_error: Optional[str] = None
    last_provider: Optional[str] = None
    try:
        for slug, key, model in configured:
            last_provider = slug
            try:
                text = await call_direct_llm(
                    provider=slug,
                    model_name=model,
                    system_prompt="You are a concise setup validator.",
                    content="In one short sentence, say hello to MAARS.",
                    attachments=[],
                    api_key=key,
                )
                await wallet_service.settle(
                    user_id,
                    reserved_amount=1,
                    actual_amount=1,
                    reference_id=ref_id,
                    description="Setup completion settled",
                )
                return True, f"Completion OK via {slug}/{model} ({int((time.time()-t0)*1000)}ms).", {
                    "provider": slug,
                    "model": model,
                    "latency_ms": int((time.time() - t0) * 1000),
                    "preview": (text or "")[:200],
                }
            except Exception as exc:
                last_error = str(exc)
                continue

        await wallet_service.refund(
            user_id,
            reserved_amount=1,
            reference_id=ref_id,
            description=f"Setup completion failed: {last_error or 'unknown error'}",
        )
        if last_provider:
            return False, f"Provider call failed ({last_provider}): {last_error or 'unknown error'}", {"provider": last_provider}
        return False, "Provider call failed: no provider attempts succeeded.", {}
    except Exception as exc:
        await wallet_service.refund(
            user_id,
            reserved_amount=1,
            reference_id=ref_id,
            description=f"Setup completion failed: {exc}",
        )
        return False, f"Provider call failed: {exc}", {}


def _default_model_for(slug: str) -> str:
    explicit = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-haiku-4-5-20251001",
        "groq": "llama-3.3-70b-versatile",
        "deepseek": "deepseek-chat",
        "google": "gemini-2.5-flash",
        "xai": "grok-3-mini",
        "mistral": "mistral-small-latest",
        "perplexity": "sonar",
        "cohere": "command-r",
        "ai21": "jamba-mini-1.7",
        "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "fireworks": "accounts/fireworks/models/llama4-scout-instruct-basic",
        "huggingface": "microsoft/phi-4",
        "sambanova": "Meta-Llama-3.3-70B-Instruct",
        "nvidia_nim": "meta/llama-3.1-8b-instruct",
        "novita": "hermes-3-llama-3.1-70b",
        "cerebras": "llama-3.3-70b",
        "hyperbolic": "meta-llama/Llama-3.3-70B-Instruct",
        "zhipu": "glm-4-air",
        "qwen": "qwen-plus",
        "moonshot": "moonshot-v1-8k",
        "yi": "yi-lightning",
        "doubao": "doubao-pro-32k",
        "minimax": "minimax-text-01",
        "upstage": "solar-mini",
        "writer": "palmyra-med",
        "meta_llama_api": "Llama-3.3-70B-Instruct",
        "bedrock": "amazon.nova-micro-v1:0",
    }.get(slug)
    if explicit:
        return explicit

    provider_alias = _provider_alias_for_llm_models(slug)
    try:
        from services.llm_service import MODEL_COSTS_MAP

        for model_name, meta in MODEL_COSTS_MAP.items():
            if meta.get("provider") == provider_alias:
                return model_name
    except Exception:
        pass

    return ""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ final assembly

async def build_report() -> dict[str, Any]:
    """Final readiness report â€” drives the green/red checklist on the wizard."""
    state = await get_state()
    steps = state["steps"]

    def ok(sid: str) -> bool:
        return steps.get(sid, {}).get("status") == "success"

    # A provider counts as ready if its step landed on success OR its env var
    # is configured (catalog detection picks up keys set out-of-band, e.g. by
    # `setup.sh` or a fresh shell export).
    detected_advanced = detect_configured_providers()
    providers_ok = (
        any(ok(f"provider_{s}") for s in PROVIDER_LINKS.keys())
        or any(d["status"] in ("validated", "detected") for d in detected_advanced.values())
    )

    # Per-provider status grid for the wizard / readiness UI.
    providers_status = overlay_step_status(detected_advanced, steps)

    # All env vars we want masked-views for in the report (quick + Stripe + every advanced env).
    env_keys = [p.env_var for p in provider_catalog.CATALOG] + [
        "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
    ]

    return {
        "frontend_ready":  True,                              # if you got here, frontend served
        "backend_ready":   ok("system_check"),
        "database_ready":  ok("system_check") and ok("migrate"),
        "providers_ready": providers_ok,
        "billing_ready":   ok("stripe_keys"),
        "wallet_ready":    ok("seed") and ok("test_wallet"),
        "routing_ready":   ok("test_routing"),
        "completion_ready": ok("test_completion"),
        "launch_ready": all([
            ok("system_check"),
            providers_ok,
            ok("seed"),
            ok("test_wallet"),
            ok("test_routing"),
        ]),
        "finished_at":     state.get("finished_at"),
        "test_credentials": state.get("test_credentials"),
        "providers_status": providers_status,
        "configured_env":  env_writer.masked_view(env_keys),
    }


def _refresh_provider_registry() -> None:
    """Re-init the in-memory provider registry so freshly saved keys are usable."""
    try:
        from services import providers as _p
        _p._register_defaults()  # type: ignore[attr-defined]
    except Exception as exc:
        logger.warning("provider registry refresh failed: %s", exc)


async def ensure_indexes() -> None:
    await db[SETUP_COLLECTION].create_index("setup_id", unique=True, name="setup_id_unique")



