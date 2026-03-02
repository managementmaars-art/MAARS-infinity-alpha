"""MAARS Command Backend - Thin application shell.
All business logic is in routes/ and services/."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from db import db, client
import shared.constants as constants
from services.agent_service import seed_default_agents, backfill_usage_logs

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MAARS Command API")

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

app.include_router(api_router)


@app.on_event("startup")
async def startup():
    await seed_default_agents()
    await backfill_usage_logs()

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
    await db.knowledge_docs.create_index([("agent_id", 1)])
    logger.info("MongoDB indexes ensured")

    # Load admin-configured pricing from DB (overrides hardcoded defaults)
    saved_pricing = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
    if saved_pricing and saved_pricing.get("plans"):
        constants.SUBSCRIPTION_PLANS.update(saved_pricing["plans"])
        logger.info("Loaded pricing from database")
    if saved_pricing and "custom_agent_credit_cost" in saved_pricing:
        constants.CUSTOM_AGENT_CREDIT_COST = saved_pricing["custom_agent_credit_cost"]

    logger.info("MAARS Global AI Team Backend started")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "MAARS Command"}


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
