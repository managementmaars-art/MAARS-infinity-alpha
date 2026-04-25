"""MAARS Command Backend - Thin application shell.
All business logic is in routes/ and services/."""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# On Windows, force the ProactorEventLoop so asyncio.create_subprocess_exec
# works — it's required by Playwright (embedded browser) and anything else
# that spawns OS subprocesses. Uvicorn's --reload mode otherwise uses
# SelectorEventLoop, which raises NotImplementedError on subprocess_exec.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from services.health_service import REQUIRED_ENV_VARS

ROOT_DIR = Path(__file__).parent
PROJECT_ROOT = ROOT_DIR.parent

# Prefer root-level .env (documented setup), while still supporting backend/.env.
load_dotenv(PROJECT_ROOT / '.env')
load_dotenv(ROOT_DIR / '.env', override=False)

# ==================== ENVIRONMENT VALIDATION ====================
# Validate all critical environment variables before starting application
def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = REQUIRED_ENV_VARS
    
    environment = os.environ.get('ENVIRONMENT', 'development')
    missing_vars = []
    
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"  • {var}: {description}")
    
    if missing_vars:
        error_msg = (
            f"\n{'='*80}\n"
            f"STARTUP FAILED: Missing required environment variables\n"
            f"{'='*80}\n"
            f"\nThe following environment variables must be set in .env:\n"
            f"{chr(10).join(missing_vars)}\n"
            f"\nTo get started:\n"
            f"  1. Copy .env.example to .env\n"
            f"  2. Edit .env with your actual values\n"
            f"  3. Restart the application\n"
            f"\nFor local development:\n"
            f"  MONGO_URL=mongodb://localhost:27017\n"
            f"  DB_NAME=maars_infinity\n"
            f"  JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')\n"
            f"{'='*80}\n"
        )
        raise ValueError(error_msg)
    
    if environment == 'production':
        # Additional production safety checks
        jwt_secret = os.environ.get('JWT_SECRET', '')
        if len(jwt_secret) < 32:
            raise ValueError(
                "SECURITY ERROR: JWT_SECRET in production must be at least 32 characters long. "
                "Generate a strong secret using: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

# Call validation immediately when module is imported
validate_environment()
# ==================================================================

from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware

from db import db, client
import shared.constants as constants
from services.agent_service import seed_default_agents, backfill_usage_logs
from services.health_service import (
    build_api_health_response,
    build_liveness_response,
    build_readiness_response,
    build_root_health_response,
)
from services.kernel_service import seed_default_tools

# Route imports
from routes.auth import router as auth_router
from routes.agents import router as agents_router
from routes.chats import router as chats_router
from routes.tasks import router as tasks_router
from routes.teams import router as teams_router
from routes.subscriptions import router as subscriptions_router
from routes.admin import router as admin_router
from routes.generation import router as generation_router
from routes.media import router as media_router
from routes.user import router as user_router
from routes.products import router as products_router
from routes.knowledge_base import router as knowledge_base_router
from routes.projects import router as projects_router
from routes.workspace import router as workspace_router
from routes.approvals import router as approvals_router
from routes.enterprise import router as enterprise_router
from routes.vibe_coding import router as vibe_router
from routes.actions import router as actions_router
from routes.content import router as content_router
from routes.voice import router as voice_router
from routes.admin_code import router as admin_code_router
from routes.memory import router as memory_router
from routes.summary import router as summary_router
from routes.websocket import router as ws_router
from routes.kernel import router as kernel_router
from routes.agent_teams import router as agent_teams_router
from routes.infinity_routes import router as infinity_router
from routes.infinity_ws import router as infinity_ws_router
from routes.universal import router as universal_router
from routes.v1_gateway import router as v1_gateway_router
from routes.social_media import router as social_media_router
from routes.lead_research import router as lead_research_router
from routes.unsubscribe import router as unsubscribe_router
from routes.campaigns import router as campaigns_router
from routes.email_events import router as email_events_router
from routes.referrals import router as referrals_router
from routes.customer_webhooks import router as customer_webhooks_router
from routes.compliance import router as compliance_router
from routes.customer_dashboard import router as customer_dashboard_router
# Pricing is owned by routes/subscriptions.py (GET /plans) which now
# delegates to services.pricing_service for all shape/format logic.
# The former public_pricing_router was deleted as duplicative.
from routes.status_and_changelog import router as status_changelog_router
from routes.prompts_library import router as prompts_library_router
from routes.leads_csv import router as leads_csv_router
from routes.workflows import router as workflows_router
from routes.integration_handlers import router as integration_handlers_router
from routes.rag import router as rag_router
from routes.health_deep import router as health_deep_router
from routes.seo_statics import router as seo_statics_router
from routes.notifications_center import router as notifications_center_router
from routes.cost_preflight import router as cost_preflight_router
from routes.blog import router as blog_router
from routes.browser import router as browser_router
from routes.wallet import router as wallet_router
from routes.admin_wallet import router as admin_wallet_router
from routes.admin_metrics import router as admin_metrics_router
from routes.admin_intelligence import router as admin_intelligence_router
# routes/billing.py retired — canonical billing lives in routes/subscriptions.py
# (uses /checkout, /webhook/stripe, and now routes plan grants through
# wallet_service.grant_buckets per plan_buckets split).
from routes.platform import router as platform_router
from routes.setup import router as setup_router
from routes.admin_packages import router as admin_packages_router
from routes.admin_gateway_intel import router as admin_gateway_intel_router
from routes.oauth import router as oauth_router
from routes.webhooks_in import router as webhooks_in_router
from routes.outcomes import router as outcomes_router
from routes.provider_onboarding import router as provider_onboarding_router
from routes.agent_offices import router as agent_offices_router
from routes.admin_teams import router as admin_teams_router
from routes.admin_cost_automation import router as admin_cost_automation_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] [req=%(request_id)s user=%(user_id)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Install request-context + secret-scrubbing log filters on the root logger so
# every log line across the app carries req_id/user_id and never leaks keys.
from services.request_context import install_filters as _install_log_filters
_install_log_filters()

app = FastAPI(title="MAARS Command API")

# ── Sentry error monitoring — no-op if SENTRY_DSN not set ──────────
try:
    from services.error_monitoring import init_sentry
    init_sentry()
except Exception:
    pass

# ── Per-user rate limiting ─────────────────────────────────────────
try:
    from middleware.rate_limit_per_user import rate_limit_middleware
    app.middleware("http")(rate_limit_middleware)
except Exception:
    pass
SERVICE_NAME = "MAARS Command"
STARTUP_STATE = {
    "ready": False,
    "started_at": datetime.now(timezone.utc).isoformat(),
    "completed_at": None,
    "last_error": None,
    "tasks": {
        "seed_default_agents": False,
        "backfill_usage_logs": False,
        "seed_default_tools": False,
        "seed_governance_defaults": False,
        "ensure_mongodb_indexes": False,
        "load_pricing_config": False,
    },
}

# Serve generated avatar images
from fastapi.staticfiles import StaticFiles
avatar_dir = ROOT_DIR / "static" / "avatars"
avatar_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")

# Include all routers under /api prefix
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(agents_router)
api_router.include_router(chats_router)
api_router.include_router(tasks_router)
api_router.include_router(teams_router)
api_router.include_router(subscriptions_router)
api_router.include_router(admin_router)
api_router.include_router(generation_router)
api_router.include_router(media_router)
api_router.include_router(user_router)
api_router.include_router(products_router)
api_router.include_router(knowledge_base_router)
api_router.include_router(projects_router)
api_router.include_router(workspace_router)
api_router.include_router(approvals_router)
api_router.include_router(enterprise_router)
api_router.include_router(vibe_router)
api_router.include_router(actions_router)
api_router.include_router(content_router)
api_router.include_router(voice_router)
api_router.include_router(admin_code_router)
api_router.include_router(memory_router)
api_router.include_router(summary_router)
api_router.include_router(kernel_router)
api_router.include_router(agent_teams_router)
api_router.include_router(infinity_router)
api_router.include_router(universal_router)
api_router.include_router(v1_gateway_router)
api_router.include_router(social_media_router)
api_router.include_router(lead_research_router)
api_router.include_router(unsubscribe_router)
api_router.include_router(campaigns_router)
api_router.include_router(email_events_router)
api_router.include_router(referrals_router)
api_router.include_router(customer_webhooks_router)
api_router.include_router(compliance_router)
api_router.include_router(customer_dashboard_router)
api_router.include_router(status_changelog_router)
api_router.include_router(prompts_library_router)
api_router.include_router(leads_csv_router)
api_router.include_router(workflows_router)
api_router.include_router(integration_handlers_router)
api_router.include_router(rag_router)
api_router.include_router(health_deep_router)
api_router.include_router(notifications_center_router)
api_router.include_router(cost_preflight_router)
api_router.include_router(blog_router)
# seo_statics paths (sitemap.xml, robots.txt, security.txt) are
# deliberately NOT under /api — they must be at the root for crawlers.
app.include_router(seo_statics_router)
api_router.include_router(browser_router)
api_router.include_router(wallet_router)
api_router.include_router(admin_wallet_router)
api_router.include_router(admin_metrics_router)
api_router.include_router(admin_intelligence_router)
# billing_router retired (see import line above)
api_router.include_router(platform_router)
api_router.include_router(setup_router)
api_router.include_router(admin_packages_router)
api_router.include_router(admin_gateway_intel_router)
api_router.include_router(oauth_router)
api_router.include_router(webhooks_in_router)
api_router.include_router(outcomes_router)
api_router.include_router(provider_onboarding_router)
api_router.include_router(agent_offices_router)
api_router.include_router(admin_teams_router)
api_router.include_router(admin_cost_automation_router)

app.include_router(api_router)

# WebSocket routes (outside /api prefix — ingress handles /ws differently)
app.include_router(ws_router, prefix="/api")
app.include_router(infinity_ws_router, prefix="/api")


@app.on_event("startup")
async def startup():
    STARTUP_STATE["started_at"] = datetime.now(timezone.utc).isoformat()
    STARTUP_STATE["completed_at"] = None
    STARTUP_STATE["last_error"] = None
    STARTUP_STATE["ready"] = False
    for task_name in STARTUP_STATE["tasks"]:
        STARTUP_STATE["tasks"][task_name] = False

    try:
        await seed_default_agents()
        STARTUP_STATE["tasks"]["seed_default_agents"] = True

        await backfill_usage_logs()
        STARTUP_STATE["tasks"]["backfill_usage_logs"] = True

        await seed_default_tools()
        STARTUP_STATE["tasks"]["seed_default_tools"] = True

        # Seed MAARS Infinity defaults
        from kernel.policy_engine import seed_default_policies
        from governance.circuit_breaker import seed_default_breakers

        await seed_default_policies()
        await seed_default_breakers()
        STARTUP_STATE["tasks"]["seed_governance_defaults"] = True

        # Create MongoDB indexes for performance
        await db.chats.create_index([("user_id", 1), ("updated_at", -1)])
        await db.chats.create_index([("agent_id", 1)])
        await db.chats.create_index("created_at")
        await db.tasks.create_index([("user_id", 1), ("status", 1)])
        await db.tasks.create_index("created_at")
        await db.usage_logs.create_index("created_at")
        await db.usage_logs.create_index([("user_id", 1), ("created_at", -1)])
        await db.usage_logs.create_index("model")
        await db.notifications.create_index([("user_id", 1), ("read", 1)])
        await db.products.create_index([("user_id", 1), ("status", 1)])
        await db.payment_transactions.create_index([("user_id", 1), ("created_at", -1)])
        await db.subscriptions.create_index("user_id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.audit_log.create_index([("created_at", -1)])
        await db.projects.create_index([("user_id", 1), ("status", 1)])
        await db.projects.create_index([("user_id", 1), ("created_at", -1)])
        await db.tasks.create_index([("project_id", 1)])
        await db.workspace_profiles.create_index([("user_id", 1)], unique=True)
        await db.approvals.create_index([("user_id", 1), ("status", 1)])
        await db.tool_logs.create_index([("user_id", 1), ("created_at", -1)])
        await db.artifacts.create_index([("user_id", 1), ("created_at", -1)])
        await db.artifacts.create_index([("user_id", 1), ("artifact_type", 1)])
        await db.knowledge_docs.create_index([("agent_id", 1)])
        await db.agent_brains.create_index([("user_id", 1), ("agent_id", 1)], unique=True)
        await db.collaborations.create_index([("user_id", 1), ("project_id", 1)])
        await db.kpi_store.create_index([("user_id", 1)])
        await db.quality_reviews.create_index([("user_id", 1), ("project_id", 1)])
        await db.system_config.create_index([("user_id", 1)])
        await db.reference_analyses.create_index([("user_id", 1), ("created_at", -1)])
        await db.vibe_projects.create_index([("user_id", 1), ("created_at", -1)])
        await db.google_tokens.create_index([("user_id", 1)], unique=True)
        await db.generated_content.create_index([("user_id", 1), ("created_at", -1)])
        await db.routing_logs.create_index([("user_id", 1), ("created_at", -1)])
        await db.memory_entries.create_index([("user_id", 1), ("created_at", -1)])
        await db.memory_entries.create_index([("user_id", 1), ("agent_id", 1)])
        # MAARS Infinity indexes
        await db.task_graphs.create_index([("user_id", 1), ("status", 1)])
        await db.task_graphs.create_index([("user_id", 1), ("updated_at", -1)])
        await db.execution_logs.create_index([("user_id", 1), ("created_at", -1)])
        await db.execution_logs.create_index([("agent_id", 1)])
        await db.tool_registry.create_index("tool_id", unique=True)
        await db.agents.create_index("network")
        await db.agents.create_index("is_infinity")
        await db.gateway_usage_logs.create_index([("user_id", 1), ("timestamp", -1)])
        await db.gateway_usage_logs.create_index([("source", 1), ("timestamp", -1)])
        await db.client_gateway_keys.create_index("user_id", unique=True)
        await db.client_gateway_keys.create_index("key", unique=True)

        # Wallet + ledger + api-key foundation (MAARS Universal Gateway prereqs)
        from services.billing import wallet_service as _wallet_service
        from services.billing import ledger_service as _ledger_service
        from services import api_key_service as _api_key_service
        from services import memory_facade as _memory_facade
        from workers import task_runner as _task_runner
        from services import setup_orchestrator as _setup_orch
        from services import revenue_service as _revenue_service
        await _wallet_service.ensure_indexes()
        await _ledger_service.ensure_indexes()
        await _api_key_service.ensure_indexes()
        await _memory_facade.ensure_indexes()
        await _task_runner.ensure_indexes()
        await _setup_orch.ensure_indexes()
        await _revenue_service.ensure_indexes()

        # Pull any persisted package overrides into the in-memory PACKAGES dict
        # so the wizard / Stripe webhook see the operator's configured splits.
        from services.billing import stripe_service as _stripe_service
        from services import customer_pricing_service as _cpps
        await _stripe_service.load_overrides_from_db()
        await _cpps.ensure_indexes()

        STARTUP_STATE["tasks"]["ensure_mongodb_indexes"] = True
        logger.info("MongoDB indexes ensured")

        # Load admin-configured pricing from DB (overrides hardcoded defaults)
        saved_pricing = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
        if saved_pricing and saved_pricing.get("plans"):
            constants.SUBSCRIPTION_PLANS.update(saved_pricing["plans"])
            logger.info("Loaded pricing from database")
        if saved_pricing and "custom_agent_credit_cost" in saved_pricing:
            constants.CUSTOM_AGENT_CREDIT_COST = saved_pricing["custom_agent_credit_cost"]
        STARTUP_STATE["tasks"]["load_pricing_config"] = True

        # Auto-sync: re-run provider smoke + balance refresh in the background so
        # the Provider Health dashboard reflects top-ups / EULA-accepts / billing
        # fixes within minutes, without operator needing to click "Run Smoke
        # Test". Smoke runs every 10 min, balances every 5 min. Same script we
        # expose via POST /admin/gateway/smoke-test — just on a timer.
        async def _auto_smoke_loop():
            import asyncio as _aio, json as _json, sys as _sys
            from pathlib import Path as _Path
            from services import provider_balance as _pb
            smoke_script = _Path(__file__).parent / "scripts" / "provider_smoke.py"
            report_path = _Path(__file__).parent / "scripts" / "provider_smoke_report.json"
            # Operator-confirmed minimum top-up amounts (from FIX_HINTS).
            # When a provider flips fail → ok and no starting_balance is set,
            # auto-seed it with this amount so the balance dashboard shows a
            # realistic figure instead of $0.
            _MIN_DEPOSITS = {
                "xai": 5, "together": 5, "hyperbolic": 5, "novita": 1,
                "arcee": 5, "minimax": 5, "moonshot": 10, "openrouter": 5,
            }
            prev_status = {}
            while True:
                try:
                    proc = await _aio.create_subprocess_exec(
                        _sys.executable, str(smoke_script),
                        stdout=_aio.subprocess.DEVNULL, stderr=_aio.subprocess.DEVNULL,
                    )
                    await _aio.wait_for(proc.communicate(), timeout=300)
                    # Post-smoke: detect fail→ok transitions and auto-seed balances
                    if report_path.exists():
                        report = _json.loads(report_path.read_text())
                        for r in report.get("results", []):
                            slug = r.get("provider")
                            now_ok = r.get("ok") is True
                            was_fail = prev_status.get(slug) is False
                            if now_ok and was_fail and slug in _MIN_DEPOSITS:
                                # Flipped fail → ok; check if starting_balance is unset
                                cfg = await _pb.get_all_configs()
                                existing = next((c for c in cfg if c.get("slug") == slug), {})
                                if not existing.get("starting_balance_usd"):
                                    await _pb.set_provider_config(
                                        slug=slug,
                                        starting_balance_usd=float(_MIN_DEPOSITS[slug]),
                                        alert_threshold_usd=2.0,
                                    )
                                    logger.info(f"auto-seeded {slug} balance to ${_MIN_DEPOSITS[slug]} after fail→ok")
                            prev_status[slug] = r.get("ok")
                except Exception as _exc:
                    logger.warning(f"auto-smoke tick failed: {_exc}")
                await _aio.sleep(600)  # 10 minutes

        async def _auto_balance_loop():
            import asyncio as _aio
            from services import provider_balance as _pb
            while True:
                try:
                    await _pb.fetch_all_balances()  # writes to provider_balances collection
                except Exception as _exc:
                    logger.warning(f"auto-balance tick failed: {_exc}")
                await _aio.sleep(300)  # 5 minutes

        asyncio.create_task(_auto_smoke_loop())
        asyncio.create_task(_auto_balance_loop())
        STARTUP_STATE["tasks"]["provider_auto_sync"] = True
        logger.info("Provider auto-sync enabled (smoke every 10min, balances every 5min)")

        # Background scheduler — makes scheduled posts/emails/calls
        # actually fire. Without this, every scheduled_at row in
        # social_posts / cold_emails / cold_calls sits forever.
        try:
            from services.scheduler import start_scheduler
            await start_scheduler()
            STARTUP_STATE["tasks"]["scheduler"] = True
        except Exception as exc:
            logger.exception("Scheduler failed to start: %s", exc)

        # MongoDB indexes on hot collections. Idempotent — re-runs
        # silently skip existing indexes. Without these, queries scale
        # from O(log n) to O(n) and the dashboard slows under load.
        try:
            from services.db_indexes import ensure_indexes
            idx_summary = await ensure_indexes()
            STARTUP_STATE["tasks"]["db_indexes"] = idx_summary.get("errored_count", 0) == 0
            logger.info("DB indexes: %s", idx_summary)
        except Exception as exc:
            logger.exception("Index ensure failed: %s", exc)

        STARTUP_STATE["ready"] = True
        STARTUP_STATE["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("MAARS Global AI Team Backend started")
    except Exception as exc:
        STARTUP_STATE["last_error"] = f"{type(exc).__name__}: {exc}"
        logger.exception("Backend startup failed")
        raise


@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        from services.scheduler import stop_scheduler
        await stop_scheduler()
    except Exception:
        logger.exception("Scheduler shutdown failed")
    client.close()


@app.get("/health")
async def root_health_check():
    return build_root_health_response(SERVICE_NAME, STARTUP_STATE)


@app.get("/api/health")
async def health_check():
    return build_api_health_response(SERVICE_NAME, STARTUP_STATE)


@app.get("/health/live")
@app.get("/api/health/live")
async def live_check():
    return build_liveness_response(SERVICE_NAME)


@app.get("/health/ready")
@app.get("/api/health/ready")
async def readiness_check(response: Response):
    payload = await build_readiness_response(SERVICE_NAME, STARTUP_STATE)
    response.status_code = 200 if payload["ready"] else 503
    return payload


# ── Rate Limiting Middleware ──
import time as _time
from collections import defaultdict

_RATE_LIMITS = defaultdict(list)
_RATE_WINDOW = 60  # seconds
_RATE_MAX = 120  # requests per window for infinity endpoints


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    path = request.url.path
    if path.startswith("/api/infinity/") or path.startswith("/api/v1/"):
        ip = request.client.host if request.client else "unknown"
        now = _time.time()
        _RATE_LIMITS[ip] = [t for t in _RATE_LIMITS[ip] if now - t < _RATE_WINDOW]
        if len(_RATE_LIMITS[ip]) >= _RATE_MAX:
            from starlette.responses import JSONResponse
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        _RATE_LIMITS[ip].append(now)
    response = await call_next(request)
    return response


# ── Response Cache for Read-Heavy Endpoints ──
_CACHE = {}
_CACHE_TTL = 5  # seconds


def _cache_get(key):
    if key in _CACHE:
        val, ts = _CACHE[key]
        if _time.time() - ts < _CACHE_TTL:
            return val
        del _CACHE[key]
    return None


def _cache_set(key, val):
    _CACHE[key] = (val, _time.time())
    # Evict old entries
    if len(_CACHE) > 200:
        oldest_key = min(_CACHE, key=lambda k: _CACHE[k][1])
        del _CACHE[oldest_key]


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=60,  # short preflight cache so route additions don't get stuck
)

# Compress responses >=1KB. Long JSON payloads from /v1 gateway and
# admin dashboards shrink ~5x on the wire — cheap wins on egress.
from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Prometheus scrape endpoint — counters live in services.prometheus_metrics."""
    from fastapi.responses import PlainTextResponse
    from services import prometheus_metrics as pm
    return PlainTextResponse(pm.render(), media_type="text/plain; version=0.0.4")

# Request-scoped observability + per-IP rate limit. Runs on every /api/* call,
# stamps X-Request-ID + X-Response-Time-Ms headers, emits one structured
# access log, and 429s abusive IPs before auth or body parsing.
from middleware.request_observability import RequestObservabilityMiddleware
app.add_middleware(
    RequestObservabilityMiddleware,
    rpm_per_ip=int(os.environ.get("MAARS_IP_RPM", 300)),
)
