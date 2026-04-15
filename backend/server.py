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
from routes.notifications_routes import router as notifications_router
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
from routes.browser import router as browser_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MAARS Command API")
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
api_router.include_router(notifications_router)
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
api_router.include_router(browser_router)

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

        STARTUP_STATE["ready"] = True
        STARTUP_STATE["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("MAARS Global AI Team Backend started")
    except Exception as exc:
        STARTUP_STATE["last_error"] = f"{type(exc).__name__}: {exc}"
        logger.exception("Backend startup failed")
        raise


@app.on_event("shutdown")
async def shutdown_db_client():
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
