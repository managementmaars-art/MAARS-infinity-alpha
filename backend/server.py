from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Request, UploadFile, File, Form, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any

# Import models from extracted schemas
from models.schemas import (
    UserCreate, UserLogin, User, Agent, AgentCreate,
    Message, Chat, ChatCreate, MessageCreate,
    SubscriptionCreate, CreditPurchase, CheckoutRequest,
    Task, TaskCreate, TaskUpdate,
    TeamCreate, TeamInvite, TeamMemberUpdate
)

# Import agent/tool config from extracted config
from config import DEFAULT_AGENTS, CLARIFICATION_INSTRUCTION, AGENT_TOOLS, AGENT_TOOL_MAP
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import httpx
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexus-ai-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# LLM Settings
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Email Settings (Gmail SMTP)
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

async def send_email_notification(to_email: str, subject: str, html_body: str):
    """Send email via Gmail SMTP. Silently skips if credentials not configured."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.info(f"Email skipped (SMTP not configured): to={to_email}, subject={subject}")
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"MAARS Command <{SMTP_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))
        
        def _send():
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        
        await asyncio.to_thread(_send)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False

# Direct API Keys (can be overridden from admin panel via DB)
DIRECT_API_KEYS = {
    "openai": os.environ.get('OPENAI_API_KEY', ''),
    "anthropic": os.environ.get('ANTHROPIC_API_KEY', ''),
    "gemini": os.environ.get('GOOGLE_API_KEY', ''),
}

async def get_api_keys():
    """Get API keys - prioritize DB-stored keys, then env vars, then Emergent key"""
    config = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
    keys = {
        "openai": "",
        "anthropic": "",
        "gemini": "",
        "xai": "",
        "deepseek": "",
        "mistral": "",
        "perplexity": "",
        "cohere": "",
        "elevenlabs": "",
        "emergent": EMERGENT_LLM_KEY,
        "active_provider": "emergent"
    }
    if config:
        for p in ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]:
            keys[p] = config.get(f"{p}_key", "") or DIRECT_API_KEYS.get(p, "")
        keys["active_provider"] = config.get("active_provider", "emergent")
    return keys

# Integration keys for 3rd party services (Slack, GitHub, SendGrid, etc.)
INTEGRATION_SERVICES = {
    "slack": {"name": "Slack", "key_fields": ["bot_token"], "description": "Send messages to Slack channels and workspaces"},
    "github": {"name": "GitHub", "key_fields": ["personal_access_token"], "description": "Create issues, PRs, read/write repos"},
    "sendgrid": {"name": "SendGrid", "key_fields": ["api_key"], "description": "Send transactional and marketing emails"},
    "resend": {"name": "Resend", "key_fields": ["api_key"], "description": "Modern email sending API"},
    "twilio": {"name": "Twilio", "key_fields": ["account_sid", "auth_token", "phone_number"], "description": "Send SMS and voice calls"},
    "airtable": {"name": "Airtable", "key_fields": ["api_key"], "description": "Read/write Airtable bases and records"},
    "calendly": {"name": "Calendly", "key_fields": ["api_key"], "description": "Schedule meetings and manage events"},
    "giphy": {"name": "Giphy", "key_fields": ["api_key"], "description": "Search and send GIFs"},
    "google_suite": {"name": "Google Suite", "key_fields": ["service_account_json"], "description": "Gmail, Google Calendar, Google Drive"},
}

async def get_integration_keys():
    """Get integration keys from DB"""
    config = await db.platform_config.find_one({"config_type": "integration_keys"}, {"_id": 0})
    return config or {"config_type": "integration_keys"}

async def get_integration_key(service: str, field: str = None):
    """Get a specific integration key"""
    config = await get_integration_keys()
    service_config = config.get(service, {})
    if field:
        return service_config.get(field, "")
    # Return first key field value
    service_def = INTEGRATION_SERVICES.get(service, {})
    for f in service_def.get("key_fields", []):
        val = service_config.get(f, "")
        if val:
            return val
    return ""

# Stripe Settings
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Admin Settings
ADMIN_EMAIL = "management.maars@marsgc.net"

# ============== SUBSCRIPTION PLANS (200% profit margin) ==============
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price_usd": 0.0,
        "price_bdt": 0.0,
        "credits": 50,
        "max_agents": 1,
        "max_custom_agents": 0,
        "includes_commander": False,
        "max_team_members": 1,
        "features": ["1 AI employee", "50 credits/month", "Basic support"]
    },
    "starter": {
        "name": "Starter",
        "price_usd": 29.0,
        "price_bdt": 3100.0,
        "credits": 500,
        "max_agents": 5,
        "max_custom_agents": 2,
        "includes_commander": False,
        "max_team_members": 3,
        "features": ["5 AI employees", "500 credits/month", "2 custom agents", "Team (up to 3)", "Priority support", "File uploads"]
    },
    "pro": {
        "name": "Pro",
        "price_usd": 79.0,
        "price_bdt": 8400.0,
        "credits": 2000,
        "max_agents": 10,
        "max_custom_agents": 5,
        "includes_commander": True,
        "max_team_members": 10,
        "features": ["10 AI employees + Commander AI", "2,000 credits/month", "5 custom agents", "Team (up to 10)", "Priority support", "Unlimited uploads"]
    },
    "business": {
        "name": "Business",
        "price_usd": 199.0,
        "price_bdt": 21100.0,
        "credits": 6000,
        "max_agents": 20,
        "max_custom_agents": -1,
        "includes_commander": True,
        "max_team_members": -1,
        "features": ["All 20 AI employees + Commander AI", "6,000 credits/month", "Unlimited custom agents", "Unlimited team members", "Dedicated support", "Unlimited everything", "API access"]
    }
}

# Custom agent creation cost
CUSTOM_AGENT_CREDIT_COST = 20

# Default custom package pricing (admin can override via DB)
DEFAULT_CUSTOM_PACKAGE_CONFIG = {
    "per_agent_price_usd": 5.0,
    "per_agent_price_bdt": 535.0,
    "commander_addon_price_usd": 15.0,
    "commander_addon_price_bdt": 1605.0,
    "credit_presets": [
        {"id": "cp_100", "credits": 100, "price_usd": 6.0, "price_bdt": 640.0},
        {"id": "cp_500", "credits": 500, "price_usd": 25.0, "price_bdt": 2675.0},
        {"id": "cp_1000", "credits": 1000, "price_usd": 45.0, "price_bdt": 4815.0},
        {"id": "cp_2000", "credits": 2000, "price_usd": 80.0, "price_bdt": 8560.0},
        {"id": "cp_5000", "credits": 5000, "price_usd": 180.0, "price_bdt": 19260.0},
    ]
}

async def get_custom_package_config():
    config = await db.platform_config.find_one({"config_type": "custom_packages"}, {"_id": 0})
    if config:
        return config
    return DEFAULT_CUSTOM_PACKAGE_CONFIG

# Exchange rate cache (refreshes daily)
_exchange_rate_cache = {"rate": None, "fetched_at": None}

async def get_live_bdt_rate():
    """Fetch live USD/BDT rate from HexaRate API, cached for 1 hour"""
    now = datetime.now(timezone.utc)
    if _exchange_rate_cache["rate"] and _exchange_rate_cache["fetched_at"]:
        age = (now - _exchange_rate_cache["fetched_at"]).total_seconds()
        if age < 3600:  # 1 hour cache
            return _exchange_rate_cache["rate"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://hexarate.paikama.co/api/rates/latest/USD?target=BDT")
            if resp.status_code == 200:
                data = resp.json()
                rate = data.get("data", {}).get("mid")
                if rate and rate > 0:
                    _exchange_rate_cache["rate"] = round(rate, 2)
                    _exchange_rate_cache["fetched_at"] = now
                    return _exchange_rate_cache["rate"]
    except Exception as e:
        logger.error(f"Exchange rate fetch error: {e}")
    # Fallback: check DB for last saved rate
    saved = await db.platform_config.find_one({"config_type": "exchange_rate"}, {"_id": 0})
    if saved and saved.get("usd_bdt"):
        return saved["usd_bdt"]
    return 121.0  # Ultimate fallback

CREDIT_PACKAGES = None  # Loaded from DB, fallback below

DEFAULT_CREDIT_PACKAGES = [
    {"id": "credits_100", "credits": 100, "price_usd": 6.0, "price_bdt": 640.0, "name": "100 Credits"},
    {"id": "credits_300", "credits": 300, "price_usd": 18.0, "price_bdt": 1910.0, "name": "300 Credits"},
    {"id": "credits_700", "credits": 700, "price_usd": 42.0, "price_bdt": 4450.0, "name": "700 Credits"},
    {"id": "credits_1500", "credits": 1500, "price_usd": 90.0, "price_bdt": 9540.0, "name": "1,500 Credits"},
]

async def get_credit_packages():
    config = await db.platform_config.find_one({"config_type": "credit_packages"}, {"_id": 0})
    if config and config.get("packages"):
        pkgs = {}
        for p in config["packages"]:
            pkgs[p["id"]] = p
        return pkgs
    return {p["id"]: p for p in DEFAULT_CREDIT_PACKAGES}

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

# Health check endpoint (must be on app directly, not api_router, for Kubernetes probes)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

# ============== AUTH HELPERS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Google OAuth session
        session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
        if session:
            expires_at = session.get("expires_at")
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at > datetime.now(timezone.utc):
                user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
                if user:
                    if isinstance(user.get('created_at'), str):
                        user['created_at'] = datetime.fromisoformat(user['created_at'])
                    user['is_admin'] = user.get('email') == ADMIN_EMAIL
                    return User(**user)
    
    # Try JWT token from header
    if credentials:
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
            if user:
                if isinstance(user.get('created_at'), str):
                    user['created_at'] = datetime.fromisoformat(user['created_at'])
                user['is_admin'] = user.get('email') == ADMIN_EMAIL
                return User(**user)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            pass
    
    raise HTTPException(status_code=401, detail="Not authenticated")

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============== DEFAULT AGENTS (defined in config.py) ==============

async def seed_default_agents():
    for agent_data in DEFAULT_AGENTS:
        existing = await db.agents.find_one({"agent_id": agent_data["agent_id"]})
        if not existing:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.agents.insert_one(agent_data)
        else:
            # Update avatar and tools if changed
            update_fields = {}
            if existing.get("avatar") != agent_data["avatar"]:
                update_fields["avatar"] = agent_data["avatar"]
            if "tools" in agent_data and existing.get("tools") != agent_data.get("tools"):
                update_fields["tools"] = agent_data["tools"]
            if update_fields:
                await db.agents.update_one(
                    {"agent_id": agent_data["agent_id"]},
                    {"$set": update_fields}
                )
    logger.info("Default agents seeded")
    
    # Set default capability flags for agents that should have them
    capability_defaults = {
        "agent_graphics": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_video": {"can_generate_image": False, "can_generate_video": True, "can_generate_pdf": True, "can_generate_files": True},
        "agent_socialmedia": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_contentwriter": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_webdesigner": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
    }
    for agent_id, caps in capability_defaults.items():
        existing = await db.agents.find_one({"agent_id": agent_id})
        if existing:
            update = {}
            for field, default_val in caps.items():
                if field not in existing:
                    update[field] = default_val
            if update:
                await db.agents.update_one({"agent_id": agent_id}, {"$set": update})
    
    # Ensure all agents have capability fields (default: PDF and Files only)
    all_agents = await db.agents.find({}).to_list(50)
    for agent in all_agents:
        update = {}
        for field in ["can_generate_image", "can_generate_video", "can_generate_pdf", "can_generate_files"]:
            if field not in agent:
                update[field] = field in ("can_generate_pdf", "can_generate_files")
        if update:
            await db.agents.update_one({"agent_id": agent["agent_id"]}, {"$set": update})

# ============== CLARIFICATION INSTRUCTION ==============

# CLARIFICATION_INSTRUCTION, AGENT_TOOLS, AGENT_TOOL_MAP imported from config.py


# ============== WORKSPACE CONTEXT (Cross-Agent Communication) ==============

async def build_workspace_context(user_id: str, current_agent_id: str) -> str:
    """Build shared workspace context for cross-agent awareness.
    Includes: recent tasks, recent activity from other agent conversations."""
    context_parts = []

    # 1. Get recent tasks for this user (last 15)
    tasks_cursor = db.tasks.find(
        {"user_id": user_id}, {"_id": 0, "task_id": 1, "title": 1, "description": 1, "status": 1, "priority": 1, "assigned_agents": 1, "created_at": 1, "result": 1}
    ).sort("created_at", -1).limit(15)
    tasks = await tasks_cursor.to_list(15)
    if tasks:
        task_lines = []
        for t in tasks:
            assigned = ", ".join(t.get("assigned_agents", [])) or "unassigned"
            result_snippet = ""
            if t.get("result"):
                result_snippet = f" | Result: {str(t['result'])[:150]}..."
            task_lines.append(f"- [{t.get('status','pending').upper()}] {t.get('title','')} (Priority: {t.get('priority','medium')}, Assigned: {assigned}, ID: {t.get('task_id','')}){result_snippet}")
        context_parts.append("## WORKSPACE TASKS\n" + "\n".join(task_lines))

    # 2. Get recent messages from OTHER agent conversations (last message from each)
    other_chats = db.chats.find(
        {"user_id": user_id, "agent_id": {"$ne": current_agent_id, "$exists": True}},
        {"_id": 0, "agent_id": 1, "messages": {"$slice": -2}}
    ).sort("updated_at", -1).limit(8)
    summaries = []
    async for chat in other_chats:
        agent_id = chat.get("agent_id", "")
        agent_doc = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "name": 1, "role": 1})
        agent_name = agent_doc.get("name", agent_id) if agent_doc else agent_id
        agent_role = agent_doc.get("role", "") if agent_doc else ""
        msgs = chat.get("messages", [])
        if msgs:
            last = msgs[-1]
            content_preview = str(last.get("content", ""))[:300]
            role = "User" if last.get("role") == "user" else agent_name
            summaries.append(f"- {agent_name} ({agent_role}): {role} said: \"{content_preview}\"")
    if summaries:
        context_parts.append("## RECENT TEAM ACTIVITY (Other Agents)\n" + "\n".join(summaries))

    if not context_parts:
        return ""

    return "\n\n--- SHARED WORKSPACE CONTEXT ---\n" + "\n\n".join(context_parts) + "\n--- END WORKSPACE CONTEXT ---\n\nUse this context to understand what other team members are working on and what tasks exist. Reference tasks by their ID when relevant. Collaborate with the user's goals across agents.\n"


async def execute_tool(tool_name: str, tool_input: dict, user_id: str) -> str:
    """Execute a tool and return the result as a string."""
    try:
        if tool_name == "web_search":
            query = tool_input.get("query", "")
            if not query:
                return "Error: No search query provided."
            async with httpx.AsyncClient(timeout=15) as client:
                # Use DuckDuckGo Instant Answer API (free, no key)
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
                )
                data = resp.json()
                results = []
                if data.get("AbstractText"):
                    results.append(f"Summary: {data['AbstractText']}")
                    if data.get("AbstractSource"):
                        results.append(f"Source: {data['AbstractSource']}")
                for topic in (data.get("RelatedTopics", []))[:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append(f"- {topic['Text']}")
                if not results:
                    results.append(f"Web search for '{query}' returned no instant results. Based on general knowledge, I'll provide what I know.")
                return "\n".join(results)

        elif tool_name == "calculate":
            expression = tool_input.get("expression", "")
            if not expression:
                return "Error: No expression provided."
            # Safe math evaluation
            import ast
            import operator
            allowed_ops = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow, ast.Mod: operator.mod,
                ast.USub: operator.neg, ast.UAdd: operator.pos,
            }
            def safe_eval(node):
                if isinstance(node, ast.Expression):
                    return safe_eval(node.body)
                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        return node.value
                    raise ValueError("Only numbers allowed")
                elif isinstance(node, ast.BinOp):
                    op = allowed_ops.get(type(node.op))
                    if not op:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(safe_eval(node.left), safe_eval(node.right))
                elif isinstance(node, ast.UnaryOp):
                    op = allowed_ops.get(type(node.op))
                    if not op:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(safe_eval(node.operand))
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")
            try:
                tree = ast.parse(expression, mode='eval')
                result = safe_eval(tree)
                return f"Result: {result}"
            except Exception as e:
                return f"Calculation error: {e}. Expression: {expression}"

        elif tool_name == "create_task":
            title = tool_input.get("title", "Untitled Task")
            description = tool_input.get("description", "")
            priority = tool_input.get("priority", "medium")
            if priority not in ("low", "medium", "high"):
                priority = "medium"
            task_doc = {
                "task_id": f"task_{uuid.uuid4().hex[:12]}",
                "user_id": user_id,
                "title": title,
                "description": description,
                "status": "pending",
                "priority": priority,
                "assigned_agents": [],
                "result": None,
                "source": "agent_tool",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.tasks.insert_one(task_doc)
            return f"Task created successfully: '{title}' (Priority: {priority}, ID: {task_doc['task_id']})"

        elif tool_name == "query_tasks":
            status_filter = tool_input.get("status", "")
            query = {"user_id": user_id}
            if status_filter and status_filter in ("pending", "in_progress", "completed", "cancelled"):
                query["status"] = status_filter
            cursor = db.tasks.find(query, {"_id": 0}).sort("created_at", -1).limit(20)
            tasks = await cursor.to_list(20)
            if not tasks:
                return "No tasks found."
            lines = []
            for t in tasks:
                assigned = ", ".join(t.get("assigned_agents", [])) or "unassigned"
                lines.append(f"[{t['status'].upper()}] {t['title']} | Priority: {t.get('priority','medium')} | Assigned: {assigned} | ID: {t['task_id']}\n  Description: {t.get('description','')[:200]}")
                if t.get("result"):
                    lines.append(f"  Result: {str(t['result'])[:300]}")
            return f"Found {len(tasks)} tasks:\n" + "\n".join(lines)

        elif tool_name == "update_task":
            task_id = tool_input.get("task_id", "")
            if not task_id:
                return "Error: task_id is required"
            task = await db.tasks.find_one({"task_id": task_id, "user_id": user_id}, {"_id": 0})
            if not task:
                return f"Task '{task_id}' not found."
            update = {}
            if tool_input.get("status") in ("pending", "in_progress", "completed", "cancelled"):
                update["status"] = tool_input["status"]
            if tool_input.get("result"):
                update["result"] = tool_input["result"]
            if tool_input.get("description"):
                update["description"] = tool_input["description"]
            if not update:
                return f"Task '{task_id}' found but no valid updates provided. Current: [{task['status']}] {task['title']}"
            update["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.tasks.update_one({"task_id": task_id}, {"$set": update})
            return f"Task '{task['title']}' updated: {', '.join(f'{k}={v}' for k, v in update.items() if k != 'updated_at')}"

        elif tool_name == "query_agent_history":
            target_agent = tool_input.get("agent_id", "")
            if not target_agent:
                return "Error: agent_id is required (e.g. 'agent_marketing', 'agent_projectmanager')"
            chat = await db.chats.find_one(
                {"user_id": user_id, "agent_id": target_agent},
                {"_id": 0, "messages": {"$slice": -10}}
            )
            if not chat or not chat.get("messages"):
                return f"No conversation history found with {target_agent}."
            agent_doc = await db.agents.find_one({"agent_id": target_agent}, {"_id": 0, "name": 1, "role": 1})
            agent_name = agent_doc.get("name", target_agent) if agent_doc else target_agent
            lines = [f"Recent conversation with {agent_name}:"]
            for msg in chat["messages"]:
                role = "User" if msg.get("role") == "user" else agent_name
                lines.append(f"  {role}: {str(msg.get('content',''))[:400]}")
            return "\n".join(lines)

        elif tool_name == "analyze_data":
            data_str = tool_input.get("data", "")
            question = tool_input.get("question", "Summarize the data")
            if not data_str:
                return "Error: No data provided to analyze."
            lines = data_str.strip().split("\n")
            numbers = []
            for line in lines:
                for part in line.replace(",", " ").split():
                    try:
                        numbers.append(float(part))
                    except ValueError:
                        pass
            analysis = [f"Data has {len(lines)} lines."]
            if numbers:
                analysis.append(f"Found {len(numbers)} numbers: min={min(numbers)}, max={max(numbers)}, avg={sum(numbers)/len(numbers):.2f}, sum={sum(numbers):.2f}")
            analysis.append(f"Analysis question: {question}")
            return "\n".join(analysis)

        elif tool_name == "send_slack":
            token = await get_integration_key("slack", "bot_token")
            if not token:
                return "Slack is not configured. Ask your admin to add a Slack Bot Token in the Integrations panel."
            channel = tool_input.get("channel", "#general").lstrip("#")
            message = tool_input.get("message", "")
            if not message:
                return "Error: No message provided."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"channel": channel, "text": message}
                )
                data = resp.json()
                if data.get("ok"):
                    return f"Message sent to #{channel} successfully."
                return f"Slack error: {data.get('error', 'Unknown error')}"

        elif tool_name == "send_email":
            # Try SendGrid first, then Resend
            sg_key = await get_integration_key("sendgrid", "api_key")
            resend_key = await get_integration_key("resend", "api_key")
            to_email = tool_input.get("to", "")
            subject = tool_input.get("subject", "No Subject")
            body = tool_input.get("body", "")
            if not to_email:
                return "Error: No recipient email provided."
            if sg_key:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={"Authorization": f"Bearer {sg_key}", "Content-Type": "application/json"},
                        json={
                            "personalizations": [{"to": [{"email": to_email}]}],
                            "from": {"email": "noreply@maarsglobal.com"},
                            "subject": subject,
                            "content": [{"type": "text/html", "value": body}]
                        }
                    )
                    if resp.status_code in (200, 201, 202):
                        return f"Email sent to {to_email} via SendGrid successfully."
                    return f"SendGrid error: {resp.status_code} - {resp.text[:200]}"
            elif resend_key:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json={"from": "noreply@maarsglobal.com", "to": [to_email], "subject": subject, "html": body}
                    )
                    if resp.status_code in (200, 201):
                        return f"Email sent to {to_email} via Resend successfully."
                    return f"Resend error: {resp.status_code} - {resp.text[:200]}"
            return "Email service not configured. Ask your admin to add SendGrid or Resend API key in Integrations."

        elif tool_name == "send_sms":
            sid = await get_integration_key("twilio", "account_sid")
            auth = await get_integration_key("twilio", "auth_token")
            from_phone = await get_integration_key("twilio", "phone_number")
            if not sid or not auth:
                return "Twilio is not configured. Ask your admin to add Twilio credentials in the Integrations panel."
            to_phone = tool_input.get("to", "")
            sms_body = tool_input.get("message", "")
            if not to_phone or not sms_body:
                return "Error: Phone number and message are required."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                    auth=(sid, auth),
                    data={"To": to_phone, "From": from_phone, "Body": sms_body[:160]}
                )
                data = resp.json()
                if resp.status_code in (200, 201):
                    return f"SMS sent to {to_phone} successfully. SID: {data.get('sid', 'N/A')}"
                return f"Twilio error: {data.get('message', resp.text[:200])}"

        elif tool_name == "github_action":
            token = await get_integration_key("github", "personal_access_token")
            if not token:
                return "GitHub is not configured. Ask your admin to add a GitHub Personal Access Token in Integrations."
            action = tool_input.get("action", "list_repos")
            repo = tool_input.get("repo", "")
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
            async with httpx.AsyncClient(timeout=10) as client:
                if action == "create_issue":
                    if not repo:
                        return "Error: repo (owner/repo) is required."
                    resp = await client.post(
                        f"https://api.github.com/repos/{repo}/issues",
                        headers=headers,
                        json={"title": tool_input.get("title", "New Issue"), "body": tool_input.get("body", "")}
                    )
                    if resp.status_code == 201:
                        data = resp.json()
                        return f"Issue created: #{data['number']} - {data['title']} ({data['html_url']})"
                    return f"GitHub error: {resp.status_code} - {resp.text[:200]}"
                elif action == "list_issues":
                    if not repo:
                        return "Error: repo (owner/repo) is required."
                    resp = await client.get(f"https://api.github.com/repos/{repo}/issues?per_page=10", headers=headers)
                    issues = resp.json()
                    if isinstance(issues, list):
                        return "\n".join([f"#{i['number']} [{i['state']}] {i['title']}" for i in issues[:10]])
                    return f"GitHub error: {resp.text[:200]}"
                elif action == "list_repos":
                    resp = await client.get("https://api.github.com/user/repos?per_page=10&sort=updated", headers=headers)
                    repos = resp.json()
                    if isinstance(repos, list):
                        return "\n".join([f"{r['full_name']} - {r.get('description', 'No description')}" for r in repos[:10]])
                    return f"GitHub error: {resp.text[:200]}"
                elif action == "search_code":
                    query = tool_input.get("body", tool_input.get("title", ""))
                    resp = await client.get(f"https://api.github.com/search/code?q={query}&per_page=5", headers=headers)
                    data = resp.json()
                    items = data.get("items", [])
                    return "\n".join([f"{it['repository']['full_name']}/{it['path']}" for it in items[:5]]) or "No results found."
            return "Unknown GitHub action."

        elif tool_name == "airtable_action":
            token = await get_integration_key("airtable", "api_key")
            if not token:
                return "Airtable is not configured. Ask your admin to add an Airtable API key in Integrations."
            action = tool_input.get("action", "list_records")
            base_id = tool_input.get("base_id", "")
            table_name = tool_input.get("table_name", "")
            if not base_id or not table_name:
                return "Error: base_id and table_name are required."
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=10) as client:
                if action == "list_records":
                    resp = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}?maxRecords=10", headers=headers)
                    data = resp.json()
                    records = data.get("records", [])
                    return "\n".join([str(r.get("fields", {})) for r in records[:10]]) or "No records found."
                elif action == "create_record":
                    fields = tool_input.get("fields", {})
                    resp = await client.post(
                        f"https://api.airtable.com/v0/{base_id}/{table_name}",
                        headers=headers,
                        json={"records": [{"fields": fields}]}
                    )
                    if resp.status_code == 200:
                        return "Record created successfully."
                    return f"Airtable error: {resp.text[:200]}"
            return "Unknown Airtable action."

        elif tool_name == "search_gif":
            token = await get_integration_key("giphy", "api_key")
            if not token:
                return "Giphy is not configured. Ask your admin to add a Giphy API key in Integrations."
            query = tool_input.get("query", "")
            if not query:
                return "Error: No search query provided."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.giphy.com/v1/gifs/search",
                    params={"api_key": token, "q": query, "limit": 3, "rating": "g"}
                )
                data = resp.json()
                gifs = data.get("data", [])
                if gifs:
                    return "\n".join([f"![{g['title']}]({g['images']['fixed_height']['url']})" for g in gifs[:3]])
                return "No GIFs found."

        elif tool_name == "schedule_meeting":
            token = await get_integration_key("calendly", "api_key")
            if not token:
                return "Calendly is not configured. Ask your admin to add a Calendly API key in Integrations."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.calendly.com/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code == 200:
                    user_data = resp.json()
                    scheduling_url = user_data.get("resource", {}).get("scheduling_url", "")
                    return f"Calendly scheduling link: {scheduling_url}\nShare this with participants to schedule a meeting."
                return f"Calendly error: {resp.text[:200]}"

        elif tool_name == "google_calendar":
            svc_json = await get_integration_key("google_suite", "service_account_json")
            if not svc_json:
                return "Google Suite is not configured. Ask your admin to add Google Suite credentials in Integrations."
            action = tool_input.get("action", "list_events")
            return f"Google Calendar {action}: This feature requires Google Suite OAuth setup. Please configure in Admin > Integrations."

        elif tool_name == "send_gmail":
            svc_json = await get_integration_key("google_suite", "service_account_json")
            if not svc_json:
                return "Google Suite is not configured. Ask your admin to add Google Suite credentials in Integrations."
            return "Gmail: This feature requires Google Suite OAuth setup. Please configure in Admin > Integrations."

        return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool execution error ({tool_name}): {str(e)[:200]}"


async def build_tool_prompt_async(tools: list) -> str:
    """Build the tool instruction section for the system prompt, filtering out unconfigured integrations."""
    if not tools:
        return ""
    
    integration_keys = await get_integration_keys()
    
    tool_descriptions = []
    available_tools = []
    for tool_name in tools:
        tool = AGENT_TOOLS.get(tool_name)
        if not tool:
            continue
        # Check if integration tool has its key configured
        requires = tool.get("requires")
        if requires:
            service_config = integration_keys.get(requires, {})
            service_def = INTEGRATION_SERVICES.get(requires, {})
            has_key = any(service_config.get(f) for f in service_def.get("key_fields", []))
            if not has_key:
                continue
        tool_descriptions.append(f"  - {tool['name']}: {tool['description']} | Parameters: {tool['parameters']}")
        available_tools.append(tool_name)
    
    if not tool_descriptions:
        return ""
    
    return f"""

You are an autonomous AI agent with access to tools. When a task requires real-time data, calculations, or actions, you MUST use your tools.

AVAILABLE TOOLS:
{chr(10).join(tool_descriptions)}

HOW TO USE A TOOL — output this exact format on a single line:
[TOOL_CALL] tool_name | {{"param1": "value1"}}

RULES:
1. When the user asks to search, look up, or find current info → use web_search
2. When the user needs math, percentages, or number crunching → use calculate
3. When the user asks to create, add, or track a task → use create_task
4. When data analysis is needed → use analyze_data
5. When the user asks to send a message to Slack → use send_slack
6. When the user asks to send an email → use send_email
7. When the user asks to send a text/SMS → use send_sms
8. When the user asks about GitHub repos/issues → use github_action
9. When the user references tasks, to-dos, or shared work → use query_tasks first
10. When the user asks about what another team member/agent discussed → use query_agent_history
11. When the user asks to update, complete, or change a task → use update_task
12. For questions you can fully answer from memory, respond directly
13. After receiving a tool result, weave it naturally into your final answer"""


async def agent_execute_with_tools(
    agent: dict,
    user_content: str,
    chat_id: str,
    api_keys: dict,
    model_provider: str,
    model_name: str,
    user_id: str,
    attachments: list = None
) -> dict:
    """Execute an agent with tool support using a ReAct loop.
    Returns: {"content": str, "execution_steps": list}
    """
    agent_tools = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    
    # If agent has no tools, fall back to regular execution
    if not agent_tools:
        return None
    
    tool_prompt = await build_tool_prompt_async(agent_tools)
    enhanced_system_prompt = agent["system_prompt"] + CLARIFICATION_INSTRUCTION + tool_prompt
    
    # Inject workspace context so agent can see cross-agent tasks and activity
    workspace_ctx = await build_workspace_context(user_id, agent.get("agent_id", ""))
    if workspace_ctx:
        enhanced_system_prompt += workspace_ctx
    
    # Apply user-specific overrides if present
    user_override = await db.user_agent_overrides.find_one(
        {"user_id": user_id, "agent_id": agent.get("agent_id")}, {"_id": 0}
    )
    if user_override:
        override_parts = []
        if user_override.get("personality_tone"):
            override_parts.append(f"User-requested personality adjustment: {user_override['personality_tone']}")
        if user_override.get("custom_instructions"):
            override_parts.append(f"User-specific instructions: {user_override['custom_instructions']}")
        if override_parts:
            enhanced_system_prompt += "\n\n--- USER CUSTOMIZATION ---\n" + "\n".join(override_parts)
    
    execution_steps = []
    max_iterations = 4
    accumulated_context = f"User: {user_content}"
    if attachments:
        accumulated_context += f"\n[User attached {len(attachments)} file(s)]"
    
    final_response = ""
    
    for iteration in range(max_iterations):
        # Call the LLM with fallback
        try:
            llm_response, model_provider, model_name = await call_llm_with_fallback(
                api_keys, model_provider, model_name,
                enhanced_system_prompt, accumulated_context,
                attachments if iteration == 0 else None,
                f"{chat_id}_tool_{iteration}"
            )
        except Exception as e:
            logger.error(f"Agent tool loop LLM error (iter {iteration}): {e}")
            if not final_response:
                final_response = f"I apologize, but I encountered an error: {str(e)}"
            break
        
        # Check for tool calls in the response
        import re
        tool_match = re.search(r'\[TOOL_CALL\]\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)
        
        # Also try alternative formats the LLM might use
        if not tool_match:
            tool_match = re.search(r'TOOL_CALL:\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)
        if not tool_match:
            tool_match = re.search(r'\[TOOL\]\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)
        
        if tool_match:
            tool_name = tool_match.group(1).strip()
            tool_input_str = tool_match.group(2).strip()
            
            # Extract thinking (text before the tool call)
            thinking_text = llm_response[:tool_match.start()].strip()
            if thinking_text:
                execution_steps.append({
                    "step_type": "thinking",
                    "content": thinking_text
                })
            
            # Parse tool input
            import json as json_lib
            try:
                tool_input = json_lib.loads(tool_input_str)
            except json_lib.JSONDecodeError:
                tool_input = {"query": tool_input_str}
            
            # Validate tool
            if tool_name not in agent_tools:
                execution_steps.append({
                    "step_type": "tool_error",
                    "tool_name": tool_name,
                    "content": f"Tool '{tool_name}' is not available."
                })
                accumulated_context += f"\n\nSystem: Tool '{tool_name}' is not available. Please use one of: {', '.join(agent_tools)}. Or respond directly."
                continue
            
            execution_steps.append({
                "step_type": "tool_call",
                "tool_name": tool_name,
                "tool_input": tool_input
            })
            
            # Execute the tool
            tool_result = await execute_tool(tool_name, tool_input, user_id)
            
            execution_steps.append({
                "step_type": "tool_result",
                "tool_name": tool_name,
                "content": tool_result
            })
            
            # Feed result back to the LLM
            accumulated_context += f"\n\nAssistant: {thinking_text}\n[Used tool: {tool_name}]\n\nTool Result ({tool_name}):\n{tool_result}\n\nNow incorporate this tool result into your response to the user. Do NOT use another tool call unless absolutely necessary. Provide your final answer."
        else:
            # No tool call - this is the final response
            final_response = llm_response
            break
    
    if not final_response and execution_steps:
        # If we exhausted iterations, try to use last accumulated context
        final_response = "Based on my analysis, here's what I found:\n\n"
        for step in execution_steps:
            if step["step_type"] == "tool_result":
                final_response += f"{step['content']}\n\n"
    
    if not final_response:
        final_response = "I encountered an issue while processing your request. Please try again."
    
    return {
        "content": final_response,
        "execution_steps": execution_steps if execution_steps else None
    }

# ============== AUTH ENDPOINTS ==============

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = hash_password(user_data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_pw,
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Welcome notification
    await create_notification(user_id, "welcome", "Welcome to MAARS Command!", "Your AI team of 21 specialists is ready. Start by chatting with any agent.", "/dashboard")
    
    token = create_jwt_token(user_id, user_data.email)
    is_admin = user_data.email == ADMIN_EMAIL
    return {"token": token, "user": {"user_id": user_id, "email": user_data.email, "name": user_data.name, "is_admin": is_admin}}

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user or not verify_password(user_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["user_id"], user["email"])
    is_admin = user["email"] == ADMIN_EMAIL
    return {"token": token, "user": {"user_id": user["user_id"], "email": user["email"], "name": user["name"], "is_admin": is_admin}}

@api_router.post("/auth/session")
async def exchange_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Exchange session_id with Emergent Auth
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            data = resp.json()
        except Exception as e:
            logger.error(f"Auth exchange error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Find or create user
    user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
        user = user_doc
    else:
        user_id = user["user_id"]
        # Update picture if changed
        if data.get("picture") and data["picture"] != user.get("picture"):
            await db.users.update_one({"user_id": user_id}, {"$set": {"picture": data["picture"]}})
            user["picture"] = data["picture"]
    
    # Store session
    session_token = data.get("session_token", f"session_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {"user_id": user_id, "email": user["email"], "name": user["name"], "picture": user.get("picture"), "is_admin": user["email"] == ADMIN_EMAIL}

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    user_doc = await db.users.find_one({"user_id": current_user.user_id}, {"_id": 0})
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat() if isinstance(current_user.created_at, datetime) else current_user.created_at,
        "onboarding_completed": user_doc.get("onboarding_completed", False) if user_doc else False
    }

@api_router.post("/auth/onboarding-complete")
async def complete_onboarding(current_user: User = Depends(get_current_user)):
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"onboarding_completed": True}}
    )
    return {"success": True}

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}

# ============== AGENT ENDPOINTS ==============

@api_router.get("/agents/public")
async def get_agents_public():
    """Public endpoint: return default agents (no auth required)"""
    agents = await db.agents.find(
        {"is_custom": False, "is_active": {"$ne": False}},
        {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1, "description": 1, "capabilities": 1, "is_commander": 1}
    ).to_list(50)
    # Inject tools info
    for agent in agents:
        agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    agents.sort(key=lambda a: (0 if a.get("agent_id") == "agent_commander" else 1, a.get("name", "")))
    return agents

@api_router.get("/agents/tools")
async def get_available_tools():
    """Get all available tools and their descriptions"""
    return {
        "tools": {name: {"name": t["name"], "description": t["description"]} for name, t in AGENT_TOOLS.items()},
        "agent_tools": AGENT_TOOL_MAP
    }

@api_router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user)):
    # Get default agents and user's custom agents, filter out deactivated ones
    agents = await db.agents.find(
        {"$or": [{"is_custom": False}, {"creator_id": current_user.user_id}], "is_active": {"$ne": False}},
        {"_id": 0}
    ).to_list(100)
    
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
        # Inject tools info from AGENT_TOOL_MAP
        if not agent.get("tools"):
            agent["tools"] = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    
    # Sort: Commander first, then others
    agents.sort(key=lambda a: (0 if a.get("agent_id") == "agent_commander" else 1, a.get("name", "")))
    
    return agents

@api_router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if isinstance(agent.get('created_at'), str):
        agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    
    return agent

@api_router.post("/agents", response_model=Agent)
async def create_agent(agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    is_admin = current_user.email == ADMIN_EMAIL
    
    # Get user subscription
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not user_sub:
        user_sub = {
            "user_id": current_user.user_id,
            "plan_id": "free",
            "credits": 50,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(user_sub)
    
    plan_id = user_sub.get("plan_id", "free")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_custom = plan.get("max_custom_agents", 0)
    
    if not is_admin:
        # Check plan limit (-1 means unlimited)
        if max_custom != -1:
            current_custom_count = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
            if current_custom_count >= max_custom:
                if max_custom == 0:
                    raise HTTPException(status_code=403, detail="Custom agent creation is not available on the Free plan. Please upgrade to Starter or higher.")
                raise HTTPException(status_code=403, detail=f"You've reached the custom agent limit ({max_custom}) for your {plan['name']} plan. Upgrade to create more.")
        
        # Check credits
        credits_remaining = user_sub.get("credits", 0)
        if credits_remaining < CUSTOM_AGENT_CREDIT_COST:
            raise HTTPException(status_code=402, detail=f"Creating a custom agent costs {CUSTOM_AGENT_CREDIT_COST} credits. You have {credits_remaining} credits remaining.")
    
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    
    agent_doc = {
        "agent_id": agent_id,
        "name": agent_data.name,
        "description": agent_data.description,
        "avatar": agent_data.avatar or "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/43ae7e2a837703cb3a5da4fdd616bc12c825f9f0f15b7e9304e61a3dab0bd257.png",
        "role": agent_data.role,
        "system_prompt": agent_data.system_prompt,
        "model_provider": agent_data.model_provider,
        "model_name": agent_data.model_name,
        "is_custom": True,
        "creator_id": current_user.user_id,
        "capabilities": agent_data.capabilities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.agents.insert_one(agent_doc)
    
    # Deduct credits for non-admin users
    if not is_admin:
        await db.subscriptions.update_one(
            {"user_id": current_user.user_id},
            {"$inc": {"credits": -CUSTOM_AGENT_CREDIT_COST, "credits_used": CUSTOM_AGENT_CREDIT_COST}}
        )
    
    agent_doc.pop("_id", None)
    agent_doc['created_at'] = datetime.fromisoformat(agent_doc['created_at'])
    return Agent(**agent_doc)

@api_router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if not agent.get("is_custom") or agent.get("creator_id") != current_user.user_id:
        raise HTTPException(status_code=403, detail="Cannot delete this agent")
    
    await db.agents.delete_one({"agent_id": agent_id})
    return {"message": "Agent deleted"}

@api_router.get("/agents/create/info")
async def get_create_agent_info(current_user: User = Depends(get_current_user)):
    """Get info about custom agent creation limits and cost for current user"""
    is_admin = current_user.email == ADMIN_EMAIL
    
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    plan_id = user_sub.get("plan_id", "free") if user_sub else "free"
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_custom = plan.get("max_custom_agents", 0)
    credits = user_sub.get("credits", 0) if user_sub else 0
    
    current_custom_count = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
    
    return {
        "credit_cost": CUSTOM_AGENT_CREDIT_COST,
        "credits_remaining": credits,
        "can_afford": credits >= CUSTOM_AGENT_CREDIT_COST or is_admin,
        "max_custom_agents": max_custom if not is_admin else -1,
        "current_custom_count": current_custom_count,
        "can_create": is_admin or (max_custom == -1 or current_custom_count < max_custom) and credits >= CUSTOM_AGENT_CREDIT_COST,
        "plan_name": plan["name"],
        "is_admin": is_admin
    }


# ============== CHAT ENDPOINTS ==============

@api_router.get("/chats", response_model=List[Chat])
async def get_chats(current_user: User = Depends(get_current_user)):
    chats = await db.chats.find({"user_id": current_user.user_id}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    
    for chat in chats:
        if isinstance(chat.get('created_at'), str):
            chat['created_at'] = datetime.fromisoformat(chat['created_at'])
        if isinstance(chat.get('updated_at'), str):
            chat['updated_at'] = datetime.fromisoformat(chat['updated_at'])
        for msg in chat.get('messages', []):
            if isinstance(msg.get('created_at'), str):
                msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return chats

@api_router.post("/chats", response_model=Chat)
async def create_chat(chat_data: ChatCreate, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": chat_data.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    chat_id = f"chat_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    chat_doc = {
        "chat_id": chat_id,
        "user_id": current_user.user_id,
        "agent_id": chat_data.agent_id,
        "title": chat_data.title or f"Chat with {agent['name']}",
        "messages": [],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.chats.insert_one(chat_doc)
    chat_doc['created_at'] = now
    chat_doc['updated_at'] = now
    return Chat(**chat_doc)

@api_router.get("/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if isinstance(chat.get('created_at'), str):
        chat['created_at'] = datetime.fromisoformat(chat['created_at'])
    if isinstance(chat.get('updated_at'), str):
        chat['updated_at'] = datetime.fromisoformat(chat['updated_at'])
    for msg in chat.get('messages', []):
        if isinstance(msg.get('created_at'), str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return chat

# ============== AUTO MODEL SELECTION ==============

def detect_video_generation_request(content: str, agent_role: str) -> bool:
    """Detect if a user message is requesting video generation. Only video-specialist agents can generate videos."""
    # ONLY video-specialist agents can trigger video generation
    video_roles = ['video content specialist', 'videographer', 'filmmaker', 'animator']
    is_video_agent = any(r in agent_role.lower() for r in video_roles)
    if not is_video_agent:
        return False
    
    content_lower = content.lower()
    generation_verbs = ['generate', 'create', 'make', 'produce', 'render', 'build me', 'give me', 'shoot', 'film', 'record']
    has_verb = any(v in content_lower for v in generation_verbs)
    return has_verb


def detect_image_generation_request(content: str, agent_role: str) -> bool:
    """Detect if a user message is requesting image/visual generation. Only design agents can generate images."""
    # ONLY graphic/design agents can trigger image generation
    visual_roles = ['graphic designer', 'designer', 'illustrator', 'artist']
    is_visual_agent = any(r in agent_role.lower() for r in visual_roles)
    if not is_visual_agent:
        return False
    
    content_lower = content.lower()
    generation_verbs = ['generate', 'create', 'make', 'design', 'draw', 'sketch', 'produce',
                        'illustrate', 'render', 'build me', 'give me', 'show me', 'craft']
    visual_nouns = ['image', 'picture', 'logo', 'banner', 'illustration', 'icon', 'graphic',
                    'visual', 'poster', 'thumbnail', 'artwork', 'photo', 'infographic',
                    'mockup', 'cover', 'avatar', 'badge', 'flyer', 'brochure', 'card',
                    'wallpaper', 'meme', 'diagram', 'drawing', 'painting', 'portrait']
    
    has_verb = any(v in content_lower for v in generation_verbs)
    has_noun = any(n in content_lower for n in visual_nouns)
    
    if has_verb:
        return True
    if has_verb and has_noun:
        return True
    
    return False


import re as _re

def detect_file_format_request(content: str) -> Optional[str]:
    """Detect if user is requesting output in a downloadable file format. Returns format or None."""
    content_lower = content.lower()
    
    format_patterns = {
        "pdf": [r'\bpdf\b', r'\bpdf format\b', r'\bas a pdf\b', r'\bin pdf\b', r'\bto pdf\b'],
        "docx": [r'\bdocx?\b', r'\bword\b', r'\bword doc\b', r'\bas a doc\b', r'\bin word\b', r'\bword format\b'],
        "csv": [r'\bcsv\b', r'\bcsv format\b', r'\bas a csv\b', r'\bin csv\b'],
        "xlsx": [r'\bxlsx?\b', r'\bexcel\b', r'\bspreadsheet\b', r'\bas an? excel\b', r'\bin excel\b'],
        "txt": [r'\btxt\b', r'\btext file\b', r'\bas a text file\b', r'\bin txt\b', r'\bplain text file\b'],
    }
    
    for fmt, patterns in format_patterns.items():
        for pattern in patterns:
            if _re.search(pattern, content_lower):
                return fmt
    return None


def extract_document_content(raw_text: str) -> str:
    """Strip AI conversational preamble and extract only the actual document content."""
    lines = raw_text.split('\n')
    
    # Look for the start of the actual document: first heading, separator, or "AGREEMENT"/"CONTRACT" etc.
    doc_start_patterns = [
        r'^#{1,3}\s',          # Markdown headings
        r'^---+$', r'^\*\*\*+$',  # Separators
        r'^\*\*[A-Z]',        # Bold uppercase start (e.g. **MUTUAL NON-DISCLOSURE**)
        r'^[A-Z][A-Z\s]{5,}$', # ALL CAPS lines (e.g. SUPPLY AGREEMENT)
    ]
    
    start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in doc_start_patterns:
            if _re.match(pattern, stripped):
                start_idx = i
                break
        if start_idx > 0:
            break
    
    # If we found a document start after some preamble, use from there
    if start_idx > 0:
        content = '\n'.join(lines[start_idx:])
    else:
        content = raw_text
    
    # Remove trailing AI notes like "**Important Note:**" or "*I am an AI*" or "Next Steps for You"
    end_patterns = [r'\*\*Important Note', r'\*I am an AI', r'\*Please note:', r'\*Disclaimer:', 
                    r'### Next Steps', r'\*\*Next Steps', r'Would you like me to']
    result_lines = content.split('\n')
    cut_idx = len(result_lines)
    for i, line in enumerate(result_lines):
        for pattern in end_patterns:
            if _re.search(pattern, line):
                cut_idx = i
                break
        if cut_idx < len(result_lines):
            break
    
    return '\n'.join(result_lines[:cut_idx]).strip()


def generate_file_from_content(content: str, file_format: str, filename_base: str) -> tuple:
    """Generate a file from text content. Returns (filepath, filename, content_type)."""
    file_id = uuid.uuid4().hex[:10]
    
    # Strip AI preamble for all formats
    doc_content = extract_document_content(content)
    if not doc_content.strip():
        doc_content = content  # Fallback to full content if extraction found nothing
    
    if file_format == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_LEFT
        from io import BytesIO
        
        filename = f"{file_id}_{filename_base}.pdf"
        filepath = UPLOAD_DIR / filename
        
        doc_pdf = SimpleDocTemplate(str(filepath), pagesize=A4,
                                     leftMargin=25*mm, rightMargin=25*mm,
                                     topMargin=20*mm, bottomMargin=20*mm)
        
        styles = getSampleStyleSheet()
        style_body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=4)
        style_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, leading=22, spaceAfter=8, spaceBefore=12)
        style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=15, leading=19, spaceAfter=6, spaceBefore=10)
        style_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=13, leading=17, spaceAfter=4, spaceBefore=8)
        style_bullet = ParagraphStyle('Bullet', parent=style_body, leftIndent=15, bulletIndent=5)
        
        def clean_md(t):
            # First escape ampersands and angle brackets
            t = t.replace('&', '&amp;')
            t = t.replace('<', '&lt;').replace('>', '&gt;')
            # Then convert markdown bold/italic to reportlab XML tags
            t = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
            t = _re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)
            t = _re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', t)
            return t
        
        story = []
        for line in doc_content.split('\n'):
            s = line.strip()
            if s.startswith('# '):
                story.append(Paragraph(clean_md(s[2:].strip('*')), style_h1))
            elif s.startswith('## '):
                story.append(Paragraph(clean_md(s[3:].strip('*')), style_h2))
            elif s.startswith('### '):
                story.append(Paragraph(clean_md(s[4:].strip('*')), style_h3))
            elif _re.match(r'^---+$', s) or _re.match(r'^\*\*\*+$', s):
                story.append(HRFlowable(width="100%", thickness=1, color="grey"))
                story.append(Spacer(1, 4*mm))
            elif s == '':
                story.append(Spacer(1, 3*mm))
            elif s.startswith('- ') or s.startswith('* '):
                story.append(Paragraph(clean_md(s[2:]), style_bullet, bulletText='\u2022'))
            elif _re.match(r'^(\d+[\.\)])\s(.+)', s):
                m = _re.match(r'^(\d+[\.\)])\s(.+)', s)
                story.append(Paragraph(clean_md(m.group(2)), style_bullet, bulletText=m.group(1)))
            elif s:
                story.append(Paragraph(clean_md(s), style_body))
        
        if not story:
            story.append(Paragraph("(Empty document)", style_body))
        
        doc_pdf.build(story)
        return filepath, filename, "application/pdf"
    
    elif file_format == "docx":
        from docx import Document
        from docx.shared import Pt, Inches
        doc = Document()
        
        for line in doc_content.split('\n'):
            clean = line.strip()
            if clean.startswith('# '):
                doc.add_heading(clean[2:].strip('*'), level=1)
            elif clean.startswith('## '):
                doc.add_heading(clean[3:].strip('*'), level=2)
            elif clean.startswith('### '):
                doc.add_heading(clean[4:].strip('*'), level=3)
            elif clean.startswith('---') or clean.startswith('***'):
                doc.add_paragraph('_' * 50)
            elif clean.startswith('- ') or clean.startswith('* '):
                doc.add_paragraph(clean[2:], style='List Bullet')
            elif _re.match(r'^\d+\.', clean):
                doc.add_paragraph(clean, style='List Number')
            elif clean:
                text = _re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
                text = _re.sub(r'\*(.*?)\*', r'\1', text)
                doc.add_paragraph(text)
        
        filename = f"{file_id}_{filename_base}.docx"
        filepath = UPLOAD_DIR / filename
        doc.save(str(filepath))
        return filepath, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    elif file_format == "csv":
        filename = f"{file_id}_{filename_base}.csv"
        filepath = UPLOAD_DIR / filename
        lines = doc_content.strip().split('\n')
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                # Try to detect table rows (| col1 | col2 |)
                if '|' in line and not line.strip().startswith('---'):
                    cells = [c.strip().strip('*') for c in line.split('|') if c.strip() and c.strip() != '---']
                    if cells:
                        f.write(','.join(f'"{c}"' for c in cells) + '\n')
                elif line.strip():
                    f.write(line.strip() + '\n')
        return filepath, filename, "text/csv"
    
    elif file_format == "xlsx":
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        
        row_num = 1
        for line in doc_content.strip().split('\n'):
            if '|' in line and not line.strip().replace('-', '').replace('|', '').strip() == '':
                cells = [c.strip().strip('*') for c in line.split('|') if c.strip()]
                if cells and not all(c.replace('-', '').strip() == '' for c in cells):
                    for col, cell in enumerate(cells, 1):
                        ws.cell(row=row_num, column=col, value=cell)
                    row_num += 1
            elif line.strip():
                ws.cell(row=row_num, column=1, value=line.strip())
                row_num += 1
        
        filename = f"{file_id}_{filename_base}.xlsx"
        filepath = UPLOAD_DIR / filename
        wb.save(str(filepath))
        return filepath, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    else:  # txt
        filename = f"{file_id}_{filename_base}.txt"
        filepath = UPLOAD_DIR / filename
        text = _re.sub(r'\*\*(.*?)\*\*', r'\1', doc_content)
        text = _re.sub(r'\*(.*?)\*', r'\1', text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return filepath, filename, "text/plain"



def auto_select_model(content: str, agent_role: str) -> tuple:
    """
    Automatically select the best AI model based on task content and agent role.
    Returns (provider, model_name, reason)
    """
    content_lower = content.lower()
    
    # Keywords for different task types
    coding_keywords = ['code', 'programming', 'function', 'api', 'debug', 'error', 'python', 'javascript', 
                       'react', 'database', 'sql', 'algorithm', 'deploy', 'github', 'bug', 'script',
                       'html', 'css', 'backend', 'frontend', 'app', 'software', 'developer', 'build',
                       'implement', 'refactor', 'regex', 'json', 'xml', 'yaml', 'docker', 'server']
    
    reasoning_keywords = ['analyze', 'compare', 'evaluate', 'why', 'how does', 'explain', 'reasoning',
                          'logic', 'problem', 'solve', 'calculate', 'math', 'strategy', 'decision',
                          'pros and cons', 'trade-off', 'complex', 'think through', 'proof', 'theorem',
                          'equation', 'formula', 'deduce', 'infer', 'hypothesis']
    
    creative_keywords = ['write', 'story', 'creative', 'blog', 'article', 'content', 'copy', 
                         'headline', 'tagline', 'slogan', 'narrative', 'engaging', 'compelling',
                         'persuasive', 'emotional', 'brand voice', 'tone', 'poem', 'script',
                         'dialogue', 'marketing', 'campaign', 'ad']
    
    quick_keywords = ['quick', 'simple', 'brief', 'short', 'summarize', 'list', 'bullet points',
                      'yes or no', 'define', 'what is', 'translate', 'convert', 'format',
                      'hello', 'hi', 'thanks', 'how are you']
    
    long_form_keywords = ['detailed', 'comprehensive', 'in-depth', 'thorough', 'research', 
                          'report', 'whitepaper', 'documentation', 'guide', 'tutorial', 'essay',
                          'paper', 'thesis', 'literature review', 'case study']
    
    data_keywords = ['data', 'analytics', 'metrics', 'dashboard', 'visualization', 'chart',
                     'statistics', 'trends', 'forecast', 'numbers', 'spreadsheet', 'excel',
                     'csv', 'graph', 'table', 'pivot', 'regression']
    
    legal_keywords = ['contract', 'legal', 'compliance', 'regulation', 'law', 'clause',
                      'terms', 'policy', 'agreement', 'liability', 'jurisdiction']
    
    # Role-based preferences
    coding_roles = ['app developer', 'web designer', 'developer', 'engineer', 'technical']
    creative_roles = ['copywriter', 'content writer', 'marketing', 'social media', 'video', 'graphic', 'email marketing']
    analytical_roles = ['strategist', 'analyst', 'research', 'financial', 'data']
    support_roles = ['customer service', 'secretary', 'hr', 'project manager']
    legal_roles = ['legal']
    
    # Count keyword matches
    coding_score = sum(1 for kw in coding_keywords if kw in content_lower)
    reasoning_score = sum(1 for kw in reasoning_keywords if kw in content_lower)
    creative_score = sum(1 for kw in creative_keywords if kw in content_lower)
    quick_score = sum(1 for kw in quick_keywords if kw in content_lower)
    long_form_score = sum(1 for kw in long_form_keywords if kw in content_lower)
    data_score = sum(1 for kw in data_keywords if kw in content_lower)
    legal_score = sum(1 for kw in legal_keywords if kw in content_lower)
    
    # Boost scores based on agent role
    agent_role_lower = agent_role.lower()
    if any(r in agent_role_lower for r in coding_roles):
        coding_score += 3
    if any(r in agent_role_lower for r in creative_roles):
        creative_score += 3
    if any(r in agent_role_lower for r in analytical_roles):
        reasoning_score += 2
        data_score += 2
    if any(r in agent_role_lower for r in support_roles):
        quick_score += 2
    if any(r in agent_role_lower for r in legal_roles):
        legal_score += 3
        reasoning_score += 1
    
    # Determine best model
    scores = {
        'coding': coding_score,
        'reasoning': reasoning_score,
        'creative': creative_score,
        'quick': quick_score,
        'long_form': long_form_score,
        'data': data_score,
        'legal': legal_score
    }
    
    best_task = max(scores, key=scores.get)
    best_score = scores[best_task]
    
    # Select model based on task type — use reliable providers (OpenAI/Gemini via Emergent key)
    if best_score >= 2:
        if best_task == 'coding':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best for coding & technical tasks')
        elif best_task == 'reasoning':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best for complex reasoning & analysis')
        elif best_task == 'creative':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best for creative work')
        elif best_task == 'quick':
            return ('openai', 'gpt-4o-mini', 'GPT-4o Mini selected - fastest for simple tasks')
        elif best_task == 'long_form':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best for detailed long-form content')
        elif best_task == 'data':
            return ('openai', 'gpt-4o', 'GPT-4o selected - best for data analysis & multimodal')
        elif best_task == 'legal':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - precise for legal analysis')
    
    # For very short messages or greetings, use fast model
    if len(content) < 50:
        return ('openai', 'gpt-4o-mini', 'GPT-4o Mini selected - efficient for short messages')
    
    # Default to GPT-5.2 for general tasks
    return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best all-around model')

async def call_direct_llm(provider: str, model_name: str, system_prompt: str, content: str, attachments: list, api_key: str) -> str:
    """Call LLM directly using provider SDKs"""
    import json as json_lib
    
    if provider == "openai":
        async with httpx.AsyncClient(timeout=120) as client:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_name, "messages": messages, "max_tokens": 4096}
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    
    elif provider == "anthropic":
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": content}]
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]
    
    elif provider == "gemini":
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": content}]}],
                    "generationConfig": {"maxOutputTokens": 4096}
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    
    elif provider == "xai":
        return await call_direct_xai(model_name, system_prompt, content, api_key)
    
    elif provider == "deepseek":
        return await call_direct_deepseek(model_name, system_prompt, content, api_key)
    
    elif provider == "mistral":
        return await call_direct_mistral(model_name, system_prompt, content, api_key)
    
    elif provider == "perplexity":
        return await call_direct_perplexity(model_name, system_prompt, content, api_key)
    
    elif provider == "cohere":
        return await call_direct_cohere(model_name, system_prompt, content, api_key)
    
    raise ValueError(f"Unsupported provider: {provider}")


async def call_direct_xai(model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    """Call xAI Grok API (OpenAI-compatible)"""
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096}
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_direct_deepseek(model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    """Call DeepSeek API (OpenAI-compatible)"""
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096}
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_direct_mistral(model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    """Call Mistral API"""
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096}
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_direct_perplexity(model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    """Call Perplexity API (OpenAI-compatible)"""
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096}
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_direct_cohere(model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    """Call Cohere API"""
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(
            "https://api.cohere.com/v2/chat",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096}
        )
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        parts = msg.get("content", [])
        return parts[0].get("text", "") if parts else ""


async def call_llm_with_fallback(api_keys, model_provider, model_name, system_prompt, content, attachments, chat_id, temperature=None, max_tokens=None):
    """Call LLM with automatic fallback to alternative models on failure."""
    fallback_models = [
        (model_provider, model_name),
        ("openai", "gpt-5.2"),
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-3-flash-preview"),
    ]
    seen = set()
    unique_fallbacks = []
    for mp, mn in fallback_models:
        key = f"{mp}/{mn}"
        if key not in seen:
            seen.add(key)
            unique_fallbacks.append((mp, mn))
    
    last_error = None
    for fb_provider, fb_model in unique_fallbacks:
        try:
            if api_keys["active_provider"] == "direct":
                direct_key = api_keys.get(fb_provider, "")
                if direct_key:
                    result = await call_direct_llm(fb_provider, fb_model, system_prompt, content, attachments, direct_key)
                    return result, fb_provider, fb_model
            
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            llm_chat = LlmChat(
                api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
                session_id=f"{chat_id}_{uuid.uuid4().hex[:6]}",
                system_message=system_prompt
            ).with_model(fb_provider, fb_model)
            # Apply temperature and max_tokens if set
            extra_params = {}
            if temperature is not None:
                extra_params["temperature"] = temperature
            if max_tokens is not None:
                extra_params["max_tokens"] = max_tokens
            if extra_params:
                llm_chat = llm_chat.with_params(**extra_params)
            message_content = content
            if attachments:
                message_content += f"\n\n[User attached {len(attachments)} file(s)]"
            user_message = UserMessage(text=message_content)
            result = await llm_chat.send_message(user_message)
            return result, fb_provider, fb_model
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed for {fb_provider}/{fb_model}: {e}. Trying fallback...")
            continue
    
    raise last_error or Exception("All LLM models failed")



@api_router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: str, message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    agent = await db.agents.find_one({"agent_id": chat["agent_id"]}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check user credits (admin bypasses credit check)
    is_admin = current_user.email == ADMIN_EMAIL
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not user_sub:
        # Create default free subscription
        user_sub = {
            "user_id": current_user.user_id,
            "plan_id": "free" if not is_admin else "business",
            "credits": 50 if not is_admin else 999999,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(user_sub)
    
    # Enforce agent access based on subscription
    if not is_admin:
        agent_id = chat["agent_id"]
        is_commander = agent_id == "agent_commander"
        plan_id = user_sub.get("plan_id", "free")
        selected_agents = user_sub.get("selected_agents", [])
        
        if plan_id == "custom":
            has_commander = user_sub.get("has_commander", False)
            if is_commander and not has_commander:
                raise HTTPException(status_code=403, detail="Commander AI is not included in your custom package. Please upgrade or add Commander to your package.")
            if not is_commander and selected_agents and agent_id not in selected_agents:
                raise HTTPException(status_code=403, detail="This agent is not in your custom package. Please update your package to include this agent.")
        else:
            plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
            if is_commander and not plan.get("includes_commander", False):
                raise HTTPException(status_code=403, detail="Commander AI is only available on Pro and Business plans. Please upgrade your plan.")
            if selected_agents and not is_commander and agent_id not in selected_agents:
                raise HTTPException(status_code=403, detail="This agent is not in your selected agents. Go to Settings to update your agent selection.")
    
    credits_remaining = user_sub.get("credits", 0)
    if credits_remaining <= 0 and not is_admin:
        raise HTTPException(status_code=402, detail="Insufficient credits. Please upgrade your plan or purchase more credits.")
    
    # Auto-select model if set to "auto" or not specified
    auto_selected = False
    model_reason = ""
    
    if message_data.model_provider == "auto" or (not message_data.model_provider and not message_data.model_name):
        # Auto-select based on content and agent role
        model_provider, model_name, model_reason = auto_select_model(message_data.content, agent.get("role", ""))
        auto_selected = True
    else:
        model_provider = message_data.model_provider or "openai"
        model_name = message_data.model_name or "gpt-5.2"
    
    # Create user message
    now = datetime.now(timezone.utc)
    user_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "user",
        "content": message_data.content,
        "attachments": message_data.attachments,
        "model_used": f"{model_provider}/{model_name}",
        "auto_selected": auto_selected,
        "model_reason": model_reason if auto_selected else None,
        "created_at": now.isoformat()
    }
    
    # Get AI response
    try:
        api_keys = await get_api_keys()
        
        # Build conversation history for context
        chat_messages = chat.get("messages", [])
        history_lines = []
        for prev_msg in chat_messages[-20:]:  # Last 20 messages for context
            role_label = "User" if prev_msg.get("role") == "user" else "Assistant"
            history_lines.append(f"{role_label}: {prev_msg.get('content', '')[:1500]}")
        
        conversation_context = ""
        if history_lines:
            conversation_context = "--- CONVERSATION HISTORY ---\n" + "\n".join(history_lines) + "\n--- END HISTORY ---\n\nLatest message from user:\n"
        
        full_user_content = conversation_context + message_data.content
        
        # Build enhanced system prompt with clarification instruction
        enhanced_agent_prompt = agent["system_prompt"] + CLARIFICATION_INSTRUCTION
        
        # Inject shared workspace context (tasks, other agents' work)
        workspace_ctx = await build_workspace_context(current_user.user_id, agent.get("agent_id", ""))
        if workspace_ctx:
            enhanced_agent_prompt += workspace_ctx
        
        # Apply user-specific agent overrides (personality, temperature, etc.)
        user_override = await db.user_agent_overrides.find_one(
            {"user_id": current_user.user_id, "agent_id": agent.get("agent_id")}, {"_id": 0}
        )
        if user_override:
            override_parts = []
            if user_override.get("personality_tone"):
                override_parts.append(f"User-requested personality adjustment: {user_override['personality_tone']}")
            if user_override.get("custom_instructions"):
                override_parts.append(f"User-specific instructions: {user_override['custom_instructions']}")
            if override_parts:
                enhanced_agent_prompt += "\n\n--- USER CUSTOMIZATION ---\n" + "\n".join(override_parts)
        
        # Check if this is Commander AI - use delegation
        is_commander = agent.get("is_commander", False) or agent.get("agent_id") == "agent_commander"
        
        delegation_data = None
        execution_steps = None
        
        if is_commander:
            # Run Commander delegation as background task (takes 2-3 min for multiple agents)
            processing_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            processing_msg = {
                "message_id": processing_msg_id,
                "chat_id": chat_id,
                "role": "assistant",
                "content": f"Analyzing your goal and deploying specialists... This will take a moment as I coordinate multiple agents.\n\nGoal: {message_data.content}",
                "model_used": f"{model_provider}/{model_name}",
                "agent_id": agent.get("agent_id"),
                "created_at": now.isoformat(),
                "commander_status": "processing"
            }
            
            # Save user msg + processing msg immediately
            await db.chats.update_one(
                {"chat_id": chat_id},
                {"$push": {"messages": {"$each": [user_msg, processing_msg]}}, "$set": {"updated_at": now.isoformat()}}
            )
            
            # Start background task
            asyncio.create_task(background_commander_delegate(
                message_data.content, chat_id, processing_msg_id, api_keys, current_user.user_id
            ))
            
            # Deduct 1 credit for the commander call
            await db.subscriptions.update_one({"user_id": current_user.user_id}, {"$inc": {"credits": -1}})
            
            return {
                "user_message": user_msg,
                "assistant_message": processing_msg,
                "credits_used": 1
            }
        else:
            # Try tool-augmented execution first
            tool_result = await agent_execute_with_tools(
                agent, full_user_content, chat_id, api_keys,
                model_provider, model_name, current_user.user_id,
                message_data.attachments
            )
            
            if tool_result:
                response_text = tool_result["content"]
                execution_steps = tool_result.get("execution_steps")
            else:
                # Get agent-level temperature and max_tokens settings, with user overrides taking priority
                agent_temp = agent.get("temperature")
                agent_max_tokens = agent.get("max_tokens")
                if user_override:
                    if user_override.get("temperature") is not None:
                        agent_temp = user_override["temperature"]
                    if user_override.get("max_tokens") is not None:
                        agent_max_tokens = user_override["max_tokens"]
                response_text, model_provider, model_name = await call_llm_with_fallback(
                    api_keys, model_provider, model_name,
                    enhanced_agent_prompt, full_user_content,
                    message_data.attachments, chat_id,
                    temperature=agent_temp, max_tokens=agent_max_tokens
                )
        
    except Exception as e:
        logger.error(f"LLM error: {e}")
        response_text = f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    # Agent-to-Agent Collaboration: check if response contains consultation requests
    try:
        if "[CONSULT:" in response_text:
            import re
            consult_matches = re.findall(r'\[CONSULT:(\w+)\](.*?)\[/CONSULT\]', response_text, re.DOTALL)
            for consult_agent_id, consult_query in consult_matches:
                consult_agent = await db.agents.find_one({"agent_id": consult_agent_id})
                if consult_agent:
                    try:
                        consult_prompt = f"A colleague ({agent.get('name')}, {agent.get('role')}) is asking for your expert input. Give a concise, direct answer. Do not ask questions.\n\nTheir question: {consult_query.strip()}"
                        consult_response, _, _ = await call_llm_with_fallback(
                            api_keys, consult_agent.get("model_provider", "openai"),
                            consult_agent.get("model_name", "gpt-5.2"),
                            consult_agent["system_prompt"], consult_prompt, [], chat_id
                        )
                        # Replace the consultation tag with the actual response
                        tag = f"[CONSULT:{consult_agent_id}]{consult_query}[/CONSULT]"
                        replacement = f"\n\n**Input from {consult_agent['name']} ({consult_agent['role']}):**\n{consult_response}\n"
                        response_text = response_text.replace(tag, replacement)
                    except Exception as ce:
                        logger.error(f"Consultation with {consult_agent_id} failed: {ce}")
                        response_text = response_text.replace(f"[CONSULT:{consult_agent_id}]{consult_query}[/CONSULT]", f"\n(Tried to consult {consult_agent.get('name')} but they were unavailable)\n")
    except Exception as collab_err:
        logger.error(f"Collaboration processing error: {collab_err}")
    
    # Auto-detect image generation requests (only if agent has can_generate_image permission)
    generated_image = None
    if agent.get("can_generate_image", False) and detect_image_generation_request(message_data.content, agent.get("role", "")):
        try:
            api_keys_img = await get_api_keys()
            # Always use Emergent key for image generation (most reliable)
            img_api_key = api_keys_img.get("emergent") or EMERGENT_LLM_KEY
            
            # Use LLM response as an enhanced prompt, or build one from user content
            img_prompt = message_data.content
            # Refine prompt for professional-grade image output
            try:
                from emergentintegrations.llm.chat import LlmChat, UserMessage as UM
                prompt_chat = LlmChat(
                    api_key=img_api_key,
                    session_id=f"imgprompt_{uuid.uuid4().hex[:8]}",
                    system_message="""You are an expert prompt engineer for GPT Image 1 (the same model used in ChatGPT). Your job is to write prompts that produce stunning, professional, publication-ready images.

Rules:
- Output ONLY the image prompt. No explanations.
- Be extremely detailed and specific about every visual element.
- For LOGOS: Specify vector-style clean design, flat or minimal 3D, precise typography style (sans-serif/serif/geometric), exact colors as hex values, white or transparent background, centered composition, no photographic elements, scalable crisp edges.
- For ILLUSTRATIONS/ART: Specify art style, medium, color palette, mood, lighting direction, background details.
- For MARKETING materials: Layout, hierarchy, grid structure, brand colors, call-to-action placement.
- Always include: style, composition, color palette, background, mood/atmosphere.
- Aim for the quality level of a professional graphic designer's output."""
                ).with_model("openai", "gpt-4o-mini")
                img_prompt = await prompt_chat.send_message(UM(text=f"User request: {message_data.content}\n\nDesigner's creative brief:\n{response_text[:2000]}"))
            except Exception as prompt_err:
                logger.warning(f"Prompt refinement failed, using original: {prompt_err}")
            
            from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
            image_gen = OpenAIImageGeneration(api_key=img_api_key)
            images = await image_gen.generate_images(
                prompt=img_prompt[:2000],
                model="gpt-image-1",
                number_of_images=1,
                quality="high"
            )
            
            if images and len(images) > 0:
                file_id = uuid.uuid4().hex[:10]
                filename = f"{file_id}_generated.png"
                filepath = UPLOAD_DIR / filename
                with open(filepath, "wb") as f:
                    f.write(images[0])
                generated_image = {
                    "filename": filename,
                    "url": f"/files/{filename}",
                    "model": "gpt-image-1",
                    "prompt": img_prompt[:500]
                }
                logger.info(f"Auto-generated image for user request: {message_data.content[:80]}")
        except Exception as img_err:
            logger.error(f"Auto image generation failed: {img_err}")
            # Don't fail the entire message, just skip image generation
    
    # Auto-detect video generation requests (only if agent has can_generate_video permission)
    generated_video = None
    video_generating = False
    if agent.get("can_generate_video", False) and not generated_image and detect_video_generation_request(message_data.content, agent.get("role", "")):
        video_generating = True
        # Video generation happens in background after response is sent
    
    # Auto-detect file format requests (check agent permissions)
    generated_file = None
    requested_format = detect_file_format_request(message_data.content)
    can_gen_files = agent.get("can_generate_files", True)
    can_gen_pdf = agent.get("can_generate_pdf", True)
    if requested_format and response_text and not generated_image and can_gen_files:
        if requested_format == "pdf" and not can_gen_pdf:
            pass  # Agent not allowed to generate PDFs
        else:
            try:
                # Create a clean filename from the chat context
                words = _re.sub(r'[^\w\s]', '', message_data.content.lower()).split()[:4]
                filename_base = '_'.join(words) if words else 'document'
                filepath, filename, content_type = generate_file_from_content(
                    response_text, requested_format, filename_base
                )
                generated_file = {
                    "filename": filename,
                    "url": f"/files/{filename}",
                    "format": requested_format,
                    "content_type": content_type,
                    "size": filepath.stat().st_size
                }
                logger.info(f"Auto-generated {requested_format} file: {filename}")
            except Exception as file_err:
                logger.error(f"Auto file generation failed: {file_err}")
    
    # Create assistant message
    assistant_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "assistant",
        "content": response_text,
        "model_used": f"{model_provider}/{model_name}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if delegation_data:
        assistant_msg["delegation_data"] = delegation_data
    if execution_steps:
        assistant_msg["execution_steps"] = execution_steps
    if generated_image:
        assistant_msg["generated_image"] = generated_image
    if generated_video:
        assistant_msg["generated_video"] = generated_video
    if generated_file:
        assistant_msg["generated_file"] = generated_file
    if video_generating:
        assistant_msg["video_generating"] = True
    
    # Update chat
    await db.chats.update_one(
        {"chat_id": chat_id},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Deduct 1 credit for the message
    await db.subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"credits": -1, "credits_used": 1}}
    )
    
    # Log API usage for cost tracking
    try:
        input_text = message_data.content + (agent.get("system_prompt", "") or "")
        est_input_tokens = max(len(input_text) // 4, 50)
        est_output_tokens = max(len(response_text) // 4, 50)
        
        model_used = assistant_msg.get("model_used", "gpt-5.2")
        provider_used = agent.get("model_provider", "openai")
        
        model_clean = model_used.split("/")[-1] if "/" in model_used else model_used
        costs = MODEL_COSTS_MAP.get(model_clean, {"input": 2.50, "output": 10.00, "provider": provider_used})
        est_cost = (est_input_tokens * costs["input"] / 1_000_000) + (est_output_tokens * costs["output"] / 1_000_000)
        
        usage_log = {
            "log_id": f"usage_{uuid.uuid4().hex[:10]}",
            "user_id": current_user.user_id,
            "chat_id": chat_id,
            "agent_id": chat["agent_id"],
            "model": model_used,
            "provider": provider_used,
            "input_tokens": est_input_tokens,
            "output_tokens": est_output_tokens,
            "estimated_cost_usd": round(est_cost, 6),
            "key_source": api_keys.get("active_provider", "emergent"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.usage_logs.insert_one(usage_log)
    except Exception as log_err:
        logger.error(f"Usage logging error: {log_err}")
    
    # Update title if first message
    if len(chat.get("messages", [])) == 0:
        title = message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"title": title}})
    
    # Get updated credits
    updated_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    credits_remaining = updated_sub.get("credits", 0) if updated_sub else 0
    
    # Low credits notification
    if credits_remaining > 0 and credits_remaining <= 20:
        existing_low = await db.notifications.find_one({"user_id": current_user.user_id, "type": "credits_low", "read": False})
        if not existing_low:
            await create_notification(current_user.user_id, "credits_low", "Credits Running Low!", f"You have {credits_remaining} credits left. Consider upgrading your plan or purchasing more credits.", "/pricing")
    
    # Start background video generation if needed
    if video_generating:
        user_attachments = message_data.attachments or []
        user_attachment_files = message_data.attachment_files or []
        async def _bg_video_gen():
            try:
                api_keys_vid = await get_api_keys()
                vid_api_key = api_keys_vid.get("emergent") or EMERGENT_LLM_KEY
                
                vid_prompt = message_data.content
                if len(response_text) > 50:
                    try:
                        from emergentintegrations.llm.chat import LlmChat, UserMessage as UM
                        pc = LlmChat(api_key=vid_api_key, session_id=f"vidp_{uuid.uuid4().hex[:6]}", system_message="You are a professional video prompt engineer for Sora 2 AI. Convert the description into a detailed cinematic video prompt (max 200 words). Include: scene composition, camera movement (dolly, crane, tracking shot), lighting (golden hour, studio, neon), subject action/motion, mood/atmosphere, color grading style, depth of field. Be specific and visual. Output ONLY the prompt.").with_model("openai", "gpt-4o-mini")
                        vid_prompt = await pc.send_message(UM(text=f"User: {message_data.content}\n\nDirector's brief:\n{response_text[:2000]}"))
                    except Exception:
                        pass
                
                from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
                vg = OpenAIVideoGeneration(api_key=vid_api_key)
                
                # Check if user attached an image for image-to-video
                source_image_path = None
                source_mime = "image/jpeg"
                
                # Check attachment_files first (saved files with paths)
                for af in user_attachment_files:
                    if af.get("type", "").startswith("image/"):
                        file_url = af.get("file_url", "")
                        fname = file_url.split("/")[-1] if file_url else ""
                        fpath = UPLOAD_DIR / fname
                        if fpath.exists():
                            source_image_path = str(fpath)
                            source_mime = af.get("type", "image/jpeg")
                            logger.info(f"Using uploaded image for video: {fname}")
                            break
                
                # Fallback: check base64 attachments
                if not source_image_path:
                    for att in user_attachments:
                        if isinstance(att, str) and att.startswith("data:image/"):
                            # Save base64 image to disk
                            try:
                                header, b64data = att.split(",", 1)
                                mime = header.split(":")[1].split(";")[0]
                                ext = mime.split("/")[1].replace("jpeg", "jpg")
                                img_bytes = base64.b64decode(b64data)
                                tmp_name = f"{uuid.uuid4().hex[:10]}_vidref.{ext}"
                                tmp_path = UPLOAD_DIR / tmp_name
                                with open(tmp_path, 'wb') as f:
                                    f.write(img_bytes)
                                source_image_path = str(tmp_path)
                                source_mime = mime
                                logger.info(f"Saved base64 image for video: {tmp_name}")
                                break
                            except Exception as b64_err:
                                logger.warning(f"Failed to decode base64 image: {b64_err}")
                
                # Also check if we just generated an image - use it as source for video
                if not source_image_path and generated_image and generated_image.get("filename"):
                    img_path = UPLOAD_DIR / generated_image["filename"]
                    if img_path.exists():
                        source_image_path = str(img_path)
                        source_mime = "image/png"
                
                if source_image_path:
                    logger.info(f"Starting Sora 2 image-to-video: image={source_image_path}, prompt={vid_prompt[:80]}...")
                else:
                    logger.info(f"Starting Sora 2 text-to-video: prompt={vid_prompt[:100]}...")
                
                def _sync_gen():
                    kwargs = dict(prompt=vid_prompt[:2000], model="sora-2", size="1280x720", duration=8, max_wait_time=600)
                    if source_image_path:
                        kwargs["image_path"] = source_image_path
                        kwargs["mime_type"] = source_mime
                    return vg.text_to_video(**kwargs)
                
                vb = await asyncio.to_thread(_sync_gen)
                logger.info(f"Video gen result: type={type(vb)}, has_data={bool(vb)}")
                
                if vb:
                    fid = uuid.uuid4().hex[:10]
                    fn = f"{fid}_video.mp4"
                    fp = UPLOAD_DIR / fn
                    vg.save_video(vb, str(fp))
                    vid_data = {"filename": fn, "url": f"/files/{fn}", "model": "sora-2", "prompt": vid_prompt[:500]}
                    await db.chats.update_one(
                        {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                        {"$set": {"messages.$.generated_video": vid_data, "messages.$.video_generating": False}}
                    )
                    logger.info(f"Background video generated: {fn}")
                else:
                    await db.chats.update_one(
                        {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                        {"$set": {"messages.$.video_generating": False, "messages.$.video_error": "Video generation returned empty"}}
                    )
            except Exception as ve:
                logger.error(f"Background video gen failed: {ve}")
                await db.chats.update_one(
                    {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                    {"$set": {"messages.$.video_generating": False, "messages.$.video_error": str(ve)[:200]}}
                )
        asyncio.create_task(_bg_video_gen())
    
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "model_used": f"{model_provider}/{model_name}",
        "auto_selected": auto_selected,
        "model_reason": model_reason if auto_selected else None,
        "credits_remaining": credits_remaining,
        "generated_image": generated_image,
        "generated_video": generated_video,
        "generated_file": generated_file
    }

# ============== FILE UPLOAD ENDPOINT ==============

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload any file and return base64 encoded data + save to disk for processing"""
    try:
        contents = await file.read()
        
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")
        
        b64_content = base64.b64encode(contents).decode('utf-8')
        content_type = file.content_type or "application/octet-stream"
        data_url = f"data:{content_type};base64,{b64_content}"
        
        # Also save to disk for image-to-video and other processing
        file_id = uuid.uuid4().hex[:10]
        ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'bin'
        saved_filename = f"{file_id}_upload.{ext}"
        saved_path = UPLOAD_DIR / saved_filename
        with open(saved_path, 'wb') as f:
            f.write(contents)
        
        return {
            "filename": file.filename,
            "saved_filename": saved_filename,
            "file_url": f"/files/{saved_filename}",
            "content_type": content_type,
            "size": len(contents),
            "data_url": data_url
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ============== COMMANDER AI DELEGATION ==============

AGENT_ROLE_MAP = {
    "marketing": "agent_marketing",
    "strategy": "agent_strategist",
    "business": "agent_strategist",
    "web design": "agent_webdesigner",
    "ui/ux": "agent_webdesigner",
    "development": "agent_appdev",
    "coding": "agent_appdev",
    "copywriting": "agent_copywriter",
    "copy": "agent_copywriter",
    "seo": "agent_seo",
    "sales": "agent_sales",
    "social media": "agent_socialmedia",
    "data": "agent_analyst",
    "analytics": "agent_analyst",
    "content": "agent_contentwriter",
    "blog": "agent_contentwriter",
    "customer service": "agent_customerservice",
    "support": "agent_customerservice",
    "project management": "agent_projectmanager",
    "planning": "agent_projectmanager",
    "research": "agent_researcher",
    "finance": "agent_finance",
    "budget": "agent_finance",
    "hr": "agent_hr",
    "hiring": "agent_hr",
    "graphic design": "agent_graphics",
    "design": "agent_graphics",
    "legal": "agent_legal",
    "contract": "agent_legal",
    "email": "agent_email",
    "newsletter": "agent_email",
    "video": "agent_video",
    "youtube": "agent_video",
    "secretary": "agent_secretary",
    "schedule": "agent_secretary",
}

async def background_commander_delegate(goal: str, chat_id: str, msg_id: str, api_keys: dict, user_id: str):
    """Run commander delegation in background and update chat when complete."""
    try:
        result = await commander_delegate(goal, chat_id, api_keys, user_id)
        # Update the processing message with the final result
        await db.chats.update_one(
            {"chat_id": chat_id, "messages.message_id": msg_id},
            {"$set": {
                "messages.$.content": result["content"],
                "messages.$.delegation_data": result.get("delegation_data"),
                "messages.$.commander_status": "complete"
            }}
        )
        logger.info(f"Commander delegation complete for chat {chat_id}")
    except Exception as e:
        logger.error(f"Background commander delegation failed: {e}")
        await db.chats.update_one(
            {"chat_id": chat_id, "messages.message_id": msg_id},
            {"$set": {
                "messages.$.content": f"I encountered an issue while coordinating the specialists. Please try again.\n\nError: {str(e)[:200]}",
                "messages.$.commander_status": "error"
            }}
        )

async def commander_delegate(goal: str, chat_id: str, api_keys: dict, user_id: str) -> dict:
    """Commander AI breaks down a goal, delegates to specialists, and auto-creates tasks.
    Returns a dict with 'content' (summary text) and 'delegation_data' (structured group chat data)."""
    # Step 1: Use LLM to analyze the goal and create a delegation plan
    plan_prompt = f"""You are Commander Orion. A user has given you this goal:

"{goal}"

Analyze this goal and create a delegation plan. Return ONLY a JSON array of sub-tasks in this exact format:
[
  {{"task": "Brief task description", "agent_role": "one of: marketing, strategy, web design, development, copywriting, seo, sales, social media, data, content, customer service, project management, research, finance, hr, graphic design, legal, email, video, secretary", "priority": "high or medium or low", "title": "Short task title for tracking"}},
  ...
]

Choose 2-4 most relevant specialists. Be specific about what each should do. Assign priority based on urgency and importance. Return ONLY the JSON array, no other text."""

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        planner = LlmChat(
            api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
            session_id=f"{chat_id}_commander_plan",
            system_message="You are a task planning AI. Output only valid JSON arrays."
        ).with_model("openai", "gpt-5.2")
        
        plan_text = await planner.send_message(UserMessage(text=plan_prompt))
        
        # Parse the plan
        import json
        plan_text_clean = plan_text.strip()
        if plan_text_clean.startswith("```"):
            plan_text_clean = plan_text_clean.split("\n", 1)[1] if "\n" in plan_text_clean else plan_text_clean[3:]
        if plan_text_clean.endswith("```"):
            plan_text_clean = plan_text_clean[:-3]
        plan_text_clean = plan_text_clean.strip()
        
        tasks = json.loads(plan_text_clean)
        
    except Exception as e:
        logger.error(f"Commander planning error: {e}")
        fallback = f"I analyzed your goal: \"{goal}\"\n\nI encountered an issue breaking this down automatically. Let me provide my strategic assessment instead:\n\nThis goal would benefit from a multi-disciplinary approach. I recommend starting with research and strategy, then moving to execution. Would you like me to try again, or shall I connect you with a specific specialist?"
        return {"content": fallback, "delegation_data": None}
    
    # Step 2: Auto-create tasks in the database
    created_tasks = []
    now = datetime.now(timezone.utc).isoformat()
    
    for i, task_item in enumerate(tasks):
        task_desc = task_item.get("task", "")
        agent_role = task_item.get("agent_role", "").lower()
        agent_id = AGENT_ROLE_MAP.get(agent_role, "agent_strategist")
        priority = task_item.get("priority", "medium").lower()
        if priority not in ("high", "medium", "low"):
            priority = "medium"
        title = task_item.get("title", task_desc[:60])
        
        task_doc = {
            "task_id": f"task_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "title": title,
            "description": task_desc,
            "status": "pending",
            "priority": priority,
            "assigned_agents": [agent_id],
            "result": None,
            "source": "commander",
            "source_goal": goal[:200],
            "created_at": now,
            "updated_at": now,
        }
        await db.tasks.insert_one(task_doc)
        created_tasks.append({"task_id": task_doc["task_id"], "title": title, "agent_id": agent_id, "priority": priority, "desc": task_desc})
    
    # Step 3: Execute each sub-task with the appropriate agent and collect structured data
    delegation_agents = []
    
    for i, ct in enumerate(created_tasks):
        agent = await db.agents.find_one({"agent_id": ct["agent_id"]}, {"_id": 0})
        if not agent:
            continue
        
        agent_entry = {
            "agent_id": ct["agent_id"],
            "agent_name": agent.get("name", "Agent"),
            "agent_role": agent.get("role", "Specialist"),
            "agent_avatar": agent.get("avatar", ""),
            "task": ct["desc"],
            "task_title": ct["title"],
            "priority": ct["priority"],
            "response": "",
            "status": "completed"
        }
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            specialist = LlmChat(
                api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
                session_id=f"{chat_id}_commander_{ct['agent_id']}",
                system_message=agent["system_prompt"]
            ).with_model(agent.get("model_provider", "openai"), agent.get("model_name", "gpt-5.2"))
            
            specialist_prompt = f"The Commander has assigned you this task as part of a larger project. Do NOT ask clarifying questions — just execute the task directly with your best professional output.\n\nWrite in clean, conversational paragraphs. Avoid excessive markdown headers (## ###). Use bold sparingly. Be concise and professional.\n\nOverall Goal: {goal}\n\nYour specific task: {ct['desc']}\n\nProvide a concise but actionable response. Focus on deliverables and next steps."
            
            response = await specialist.send_message(UserMessage(text=specialist_prompt))
            agent_entry["response"] = response
            
            await db.tasks.update_one(
                {"task_id": ct["task_id"]},
                {"$set": {"status": "completed", "result": response[:2000], "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
        except Exception as e:
            logger.error(f"Commander delegation error for {ct['agent_id']}: {e}")
            agent_entry["response"] = "Unable to complete - task saved for manual execution."
            agent_entry["status"] = "failed"
        
        delegation_agents.append(agent_entry)
    
    # Build summary content (still readable as plain text for backwards compatibility)
    summary = f"Mission Report: {len(created_tasks)} specialists deployed for your goal. {len(created_tasks)} tasks auto-created. Check the Tasks page for tracking."
    
    delegation_data = {
        "type": "commander_delegation",
        "goal": goal,
        "task_count": len(created_tasks),
        "agents": delegation_agents,
        "summary": summary
    }
    
    # Also build plain text content as fallback
    text_parts = [f"Commander Orion's Mission Report\n\nGoal: {goal}\n\nDelegation Plan: {len(tasks)} specialists deployed | {len(created_tasks)} tasks created\n\n---\n"]
    for i, a in enumerate(delegation_agents):
        priority_label = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(a["priority"], "MED")
        text_parts.append(f"{i+1}. {a['agent_name']} ({a['agent_role']}) [{priority_label}]\nTask: {a['task']}\n\n{a['response']}\n\n---\n")
    text_parts.append(f"\nAll specialists have reported. {len(created_tasks)} tasks have been auto-created and can be found on your Tasks page. Let me know if you'd like any section expanded or revised.")
    
    return {"content": "\n".join(text_parts), "delegation_data": delegation_data}

# ============== AUDIO ENDPOINTS (TTS/STT) ==============

@api_router.post("/audio/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...), language: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    """Transcribe audio to text using OpenAI Whisper"""
    try:
        contents = await audio_file.read()
        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large. Max 25MB.")
        
        from emergentintegrations.llm.openai import OpenAISpeechToText
        
        api_keys = await get_api_keys()
        stt_key = api_keys.get("emergent", EMERGENT_LLM_KEY)
        
        stt = OpenAISpeechToText(api_key=stt_key)
        
        audio_io = io.BytesIO(contents)
        audio_io.name = audio_file.filename or "audio.webm"
        
        kwargs = {"file": audio_io, "model": "whisper-1", "response_format": "json"}
        if language:
            kwargs["language"] = language
        
        response = await stt.transcribe(**kwargs)
        
        return {"text": response.text, "language": language}
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")

# ============== AVAILABLE MODELS ENDPOINT ==============

@api_router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    """Get all available AI models for switching"""
    return {
        "models": [
            # OpenAI
            {"provider": "openai", "model": "gpt-5.2", "name": "GPT-5.2", "category": "flagship", "cost_per_credit": 0.006, "best_for": "Coding, analysis, general tasks"},
            {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o", "category": "fast", "cost_per_credit": 0.003, "best_for": "Balanced speed and quality"},
            {"provider": "openai", "model": "gpt-4o-mini", "name": "GPT-4o Mini", "category": "economy", "cost_per_credit": 0.001, "best_for": "Simple tasks, quick answers"},
            {"provider": "openai", "model": "o3", "name": "O3", "category": "reasoning", "cost_per_credit": 0.012, "best_for": "Complex reasoning, math, logic"},
            {"provider": "openai", "model": "o3-mini", "name": "O3 Mini", "category": "reasoning", "cost_per_credit": 0.005, "best_for": "Light reasoning tasks"},
            # Anthropic
            {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "category": "flagship", "cost_per_credit": 0.005, "best_for": "Creative writing, analysis"},
            {"provider": "anthropic", "model": "claude-opus-4-5-20251101", "name": "Claude Opus 4.5", "category": "premium", "cost_per_credit": 0.025, "best_for": "Long-form, deep research"},
            {"provider": "anthropic", "model": "claude-haiku-4-5-20250929", "name": "Claude Haiku 4.5", "category": "economy", "cost_per_credit": 0.001, "best_for": "Quick responses, summaries"},
            # Google
            {"provider": "gemini", "model": "gemini-3-flash-preview", "name": "Gemini 3 Flash", "category": "fast", "cost_per_credit": 0.002, "best_for": "Fast responses, simple tasks"},
            {"provider": "gemini", "model": "gemini-3-pro-preview", "name": "Gemini 3 Pro", "category": "flagship", "cost_per_credit": 0.005, "best_for": "Multimodal, research"},
            # Generation models
            {"provider": "openai", "model": "gpt-image-1", "name": "GPT Image 1", "category": "image_gen", "cost_per_credit": 0.02, "best_for": "AI image generation from text"},
            {"provider": "openai", "model": "dall-e-3", "name": "DALL-E 3", "category": "image_gen", "cost_per_credit": 0.015, "best_for": "Creative image generation"},
            {"provider": "openai", "model": "sora-2", "name": "Sora 2", "category": "video_gen", "cost_per_credit": 0.10, "best_for": "AI video generation from text"},
            # xAI Grok
            {"provider": "xai", "model": "grok-3", "name": "Grok 3", "category": "flagship", "cost_per_credit": 0.005, "best_for": "Reasoning, analysis, 1M context"},
            {"provider": "xai", "model": "grok-3-mini", "name": "Grok 3 Mini", "category": "economy", "cost_per_credit": 0.001, "best_for": "Cost-efficient reasoning"},
            {"provider": "xai", "model": "grok-2", "name": "Grok 2", "category": "fast", "cost_per_credit": 0.003, "best_for": "General tasks, competitive with GPT-4o"},
            # DeepSeek
            {"provider": "deepseek", "model": "deepseek-chat", "name": "DeepSeek Chat", "category": "economy", "cost_per_credit": 0.001, "best_for": "Cost-efficient chat, 128K context"},
            {"provider": "deepseek", "model": "deepseek-reasoner", "name": "DeepSeek Reasoner", "category": "reasoning", "cost_per_credit": 0.001, "best_for": "Deep reasoning, math, logic"},
            # Mistral
            {"provider": "mistral", "model": "mistral-large-latest", "name": "Mistral Large", "category": "flagship", "cost_per_credit": 0.004, "best_for": "Complex reasoning, enterprise"},
            {"provider": "mistral", "model": "mistral-medium-latest", "name": "Mistral Medium", "category": "fast", "cost_per_credit": 0.002, "best_for": "Balanced performance"},
            {"provider": "mistral", "model": "mistral-small-latest", "name": "Mistral Small", "category": "economy", "cost_per_credit": 0.001, "best_for": "Simple tasks, very fast"},
            # Perplexity
            {"provider": "perplexity", "model": "sonar", "name": "Perplexity Sonar", "category": "search", "cost_per_credit": 0.002, "best_for": "Web-grounded answers, search"},
            {"provider": "perplexity", "model": "sonar-pro", "name": "Perplexity Sonar Pro", "category": "search", "cost_per_credit": 0.008, "best_for": "Deep web research"},
            # Cohere
            {"provider": "cohere", "model": "command-r-plus", "name": "Cohere Command R+", "category": "flagship", "cost_per_credit": 0.005, "best_for": "RAG, enterprise tasks"},
            {"provider": "cohere", "model": "command-r", "name": "Cohere Command R", "category": "fast", "cost_per_credit": 0.001, "best_for": "Cost-efficient RAG, summaries"},
        ],
        "default": {"provider": "openai", "model": "gpt-5.2"}
    }

@api_router.post("/tts/generate")
async def generate_tts(request: Request, current_user: User = Depends(get_current_user)):
    """Generate text-to-speech audio using OpenAI TTS (works with Emergent key)"""
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice", "nova")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Truncate to 4096 chars (OpenAI TTS limit)
    text = text[:4096]
    
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        
        # Use Emergent key or admin-configured OpenAI key
        api_key = EMERGENT_LLM_KEY
        if not api_key:
            admin_keys = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
            if admin_keys:
                api_key = admin_keys.get("openai", "")
        
        if not api_key:
            raise HTTPException(400, "No API key available for TTS")
        
        tts = OpenAITextToSpeech(api_key=api_key)
        audio_bytes = await tts.generate_speech(
            text=text,
            model="tts-1",
            voice=voice,
            response_format="mp3",
            speed=1.0
        )
        
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return {"audio_url": f"data:audio/mpeg;base64,{audio_b64}", "text": text, "voice": voice}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@api_router.get("/tts/voices")
async def get_tts_voices(current_user: User = Depends(get_current_user)):
    """Get available OpenAI TTS voices"""
    return {"voices": [
        {"voice_id": "alloy", "name": "Alloy", "description": "Neutral, balanced"},
        {"voice_id": "nova", "name": "Nova", "description": "Energetic, upbeat"},
        {"voice_id": "shimmer", "name": "Shimmer", "description": "Bright, cheerful"},
        {"voice_id": "echo", "name": "Echo", "description": "Smooth, calm"},
        {"voice_id": "onyx", "name": "Onyx", "description": "Deep, authoritative"},
        {"voice_id": "fable", "name": "Fable", "description": "Expressive, storytelling"},
        {"voice_id": "coral", "name": "Coral", "description": "Warm, friendly"},
        {"voice_id": "sage", "name": "Sage", "description": "Wise, measured"},
        {"voice_id": "ash", "name": "Ash", "description": "Clear, articulate"},
    ]}

# ============== FILE GENERATION ENDPOINTS ==============

from fastapi.staticfiles import StaticFiles

UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@api_router.get("/files/{filename}")
async def serve_file(filename: str):
    """Serve a generated file"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    import mimetypes
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    
    def file_iter():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_iter(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@api_router.post("/generate/document")
async def generate_document(request: Request, current_user: User = Depends(get_current_user)):
    """Generate PDF, Excel, DOCX, CSV, or TXT documents"""
    body = await request.json()
    doc_type = body.get("type", "pdf").lower()  # pdf, xlsx, docx, csv, txt
    title = body.get("title", "Generated Document")
    content = body.get("content", "")
    rows = body.get("rows", [])  # For spreadsheets: list of lists
    
    if not content and not rows:
        raise HTTPException(status_code=400, detail="Content or rows required")
    
    file_id = uuid.uuid4().hex[:10]
    
    try:
        if doc_type == "pdf":
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.pdf"
            filepath = UPLOAD_DIR / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(title, styles['Title']),
                Spacer(1, 20),
            ]
            for para in content.split("\n"):
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 8))
            doc.build(story)
        
        elif doc_type == "xlsx":
            from openpyxl import Workbook
            from openpyxl.styles import Font
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.xlsx"
            filepath = UPLOAD_DIR / filename
            
            wb = Workbook()
            ws = wb.active
            ws.title = title[:31]
            
            if rows:
                for r_idx, row in enumerate(rows, 1):
                    for c_idx, val in enumerate(row, 1):
                        cell = ws.cell(row=r_idx, column=c_idx, value=val)
                        if r_idx == 1:
                            cell.font = Font(bold=True)
            else:
                ws.cell(row=1, column=1, value=title).font = Font(bold=True)
                for i, line in enumerate(content.split("\n"), 2):
                    ws.cell(row=i, column=1, value=line.strip())
            
            wb.save(str(filepath))
        
        elif doc_type == "docx":
            from docx import Document
            from docx.shared import Pt
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.docx"
            filepath = UPLOAD_DIR / filename
            
            doc = Document()
            doc.add_heading(title, level=1)
            for para in content.split("\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())
            doc.save(str(filepath))
        
        elif doc_type == "csv":
            import csv as csv_module
            
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.csv"
            filepath = UPLOAD_DIR / filename
            
            with open(filepath, "w", newline="") as f:
                writer = csv_module.writer(f)
                if rows:
                    for row in rows:
                        writer.writerow(row)
                else:
                    for line in content.split("\n"):
                        writer.writerow([line.strip()])
        
        elif doc_type == "txt":
            filename = f"{file_id}_{title.replace(' ', '_')[:30]}.txt"
            filepath = UPLOAD_DIR / filename
            
            with open(filepath, "w") as f:
                f.write(content)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported doc type: {doc_type}. Use: pdf, xlsx, docx, csv, txt")
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "type": doc_type,
            "title": title,
            "size": filepath.stat().st_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@api_router.post("/generate/image")
async def generate_image(request: Request, current_user: User = Depends(get_current_user)):
    """Generate an image using GPT Image 1 or DALL-E 3"""
    body = await request.json()
    prompt = body.get("prompt", "")
    model = body.get("model", "gpt-image-1")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        api_keys = await get_api_keys()
        api_key = api_keys.get("emergent") or EMERGENT_LLM_KEY
        
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        
        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=prompt,
            model=model,
            number_of_images=1,
            quality="high"
        )
        
        if not images or len(images) == 0:
            raise HTTPException(status_code=500, detail="No image generated")
        
        file_id = uuid.uuid4().hex[:10]
        filename = f"{file_id}_generated.png"
        filepath = UPLOAD_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(images[0])
        
        image_b64 = base64.b64encode(images[0]).decode()
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "preview": f"data:image/png;base64,{image_b64}",
            "model": model,
            "prompt": prompt
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@api_router.post("/generate/video")
async def generate_video(request: Request, current_user: User = Depends(get_current_user)):
    """Generate a video using Sora 2"""
    body = await request.json()
    prompt = body.get("prompt", "")
    size = body.get("size", "1280x720")
    duration = body.get("duration", 4)
    model = body.get("model", "sora-2")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    if size not in ("1280x720", "1792x1024", "1024x1792", "1024x1024"):
        size = "1280x720"
    if duration not in (4, 8, 12):
        duration = 4
    
    try:
        api_keys = await get_api_keys()
        api_key = api_keys.get("emergent") or EMERGENT_LLM_KEY
        
        from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
        import aiohttp
        
        video_gen = OpenAIVideoGeneration(api_key=api_key)
        
        def _gen():
            return video_gen.text_to_video(
                prompt=prompt,
                model=model,
                size=size,
                duration=duration,
                max_wait_time=600
            )
        
        loop = asyncio.get_event_loop()
        video_bytes = await loop.run_in_executor(None, _gen)
        
        if not video_bytes:
            raise HTTPException(status_code=500, detail="Video generation failed")
        
        file_id = uuid.uuid4().hex[:10]
        filename = f"{file_id}_video.mp4"
        filepath = UPLOAD_DIR / filename
        
        video_gen.save_video(video_bytes, str(filepath))
        
        return {
            "filename": filename,
            "url": f"/files/{filename}",
            "model": model,
            "size": size,
            "duration": duration,
            "prompt": prompt
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@api_router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, current_user: User = Depends(get_current_user)):
    result = await db.chats.delete_one({"chat_id": chat_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted"}

# ============== TASK ENDPOINTS ==============

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await db.tasks.find({"user_id": current_user.user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for task in tasks:
        if isinstance(task.get('created_at'), str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if isinstance(task.get('updated_at'), str):
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
    
    return tasks

@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    task_doc = {
        "task_id": task_id,
        "user_id": current_user.user_id,
        "title": task_data.title,
        "description": task_data.description,
        "status": "pending",
        "priority": task_data.priority,
        "assigned_agents": task_data.assigned_agents,
        "result": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.tasks.insert_one(task_doc)
    task_doc['created_at'] = now
    task_doc['updated_at'] = now
    return Task(**task_doc)

@api_router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.tasks.update_one({"task_id": task_id}, {"$set": update_data})
    
    updated_task = await db.tasks.find_one({"task_id": task_id}, {"_id": 0})
    if isinstance(updated_task.get('created_at'), str):
        updated_task['created_at'] = datetime.fromisoformat(updated_task['created_at'])
    if isinstance(updated_task.get('updated_at'), str):
        updated_task['updated_at'] = datetime.fromisoformat(updated_task['updated_at'])
    
    return Task(**updated_task)

@api_router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"task_id": task_id, "user_id": current_user.user_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.get("assigned_agents"):
        raise HTTPException(status_code=400, detail="No agents assigned to task")
    
    # Update status to in_progress
    await db.tasks.update_one({"task_id": task_id}, {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}})
    
    results = []
    for agent_id in task["assigned_agents"]:
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        if not agent:
            continue
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            llm_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"{task_id}_{agent_id}",
                system_message=agent["system_prompt"]
            ).with_model(agent["model_provider"], agent["model_name"])
            
            prompt = f"Task: {task['title']}\n\nDescription: {task['description']}\n\nPlease complete this task and provide your output."
            user_message = UserMessage(text=prompt)
            response = await llm_chat.send_message(user_message)
            results.append(f"**{agent['name']}:**\n{response}")
        except Exception as e:
            logger.error(f"Task execution error for agent {agent_id}: {e}")
            results.append(f"**{agent['name']}:** Error - {str(e)}")
    
    combined_result = "\n\n---\n\n".join(results)
    
    await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {"status": "completed", "result": combined_result, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"status": "completed", "result": combined_result}

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    result = await db.tasks.delete_one({"task_id": task_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

# ============== STATS ENDPOINT ==============

@api_router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    chats_count = await db.chats.count_documents({"user_id": current_user.user_id})
    tasks_count = await db.tasks.count_documents({"user_id": current_user.user_id})
    completed_tasks = await db.tasks.count_documents({"user_id": current_user.user_id, "status": "completed"})
    custom_agents = await db.agents.count_documents({"creator_id": current_user.user_id, "is_custom": True})
    
    # Count total messages
    pipeline = [
        {"$match": {"user_id": current_user.user_id}},
        {"$project": {"message_count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$message_count"}}}
    ]
    messages_result = await db.chats.aggregate(pipeline).to_list(1)
    total_messages = messages_result[0]["total"] if messages_result else 0
    
    # Get user subscription info
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    credits_remaining = user_sub.get("credits", 50) if user_sub else 50
    plan = user_sub.get("plan_id", "free") if user_sub else "free"
    
    return {
        "total_chats": chats_count,
        "total_tasks": tasks_count,
        "completed_tasks": completed_tasks,
        "custom_agents": custom_agents,
        "total_messages": total_messages,
        "credits_remaining": credits_remaining,
        "plan": plan
    }

# ============== USER INSIGHTS DASHBOARD ==============

@api_router.get("/user/insights")
async def get_user_insights(current_user: User = Depends(get_current_user)):
    """Comprehensive usage insights for the current user."""
    uid = current_user.user_id
    now = datetime.now(timezone.utc)
    thirty_days_ago = (now - timedelta(days=30)).isoformat()

    # --- Basic stats ---
    user_chats = await db.chats.find({"user_id": uid}, {"_id": 0, "chat_id": 1, "agent_id": 1, "messages": 1, "created_at": 1}).to_list(1000)
    total_chats = len(user_chats)
    total_messages = sum(len(c.get("messages", [])) for c in user_chats)
    user_messages = sum(1 for c in user_chats for m in c.get("messages", []) if m.get("role") == "user")
    ai_messages = sum(1 for c in user_chats for m in c.get("messages", []) if m.get("role") == "assistant")

    # --- Credits ---
    user_sub = await db.subscriptions.find_one({"user_id": uid}, {"_id": 0})
    credits_remaining = user_sub.get("credits", 50) if user_sub else 50
    credits_used = user_sub.get("credits_used", 0) if user_sub else 0
    plan = user_sub.get("plan_id", "free") if user_sub else "free"

    # --- Favorite agents (most used) ---
    agent_count = {}
    for c in user_chats:
        aid = c.get("agent_id", "unknown")
        msg_count = len([m for m in c.get("messages", []) if m.get("role") == "assistant"])
        agent_count[aid] = agent_count.get(aid, 0) + msg_count

    all_agents = await db.agents.find({"is_active": {"$ne": False}}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1, "description": 1}).to_list(200)
    agent_map = {a["agent_id"]: a for a in all_agents}

    favorite_agents = sorted(agent_count.items(), key=lambda x: x[1], reverse=True)[:5]
    favorites = []
    for aid, count in favorite_agents:
        info = agent_map.get(aid, {})
        favorites.append({
            "agent_id": aid,
            "name": info.get("name", aid),
            "avatar": info.get("avatar", ""),
            "role": info.get("role", ""),
            "messages": count
        })

    # --- Agents not yet used (recommendations) ---
    used_agents = set(agent_count.keys())
    recommendations = []
    for a in all_agents:
        if a["agent_id"] not in used_agents and not a.get("is_commander"):
            recommendations.append({
                "agent_id": a["agent_id"],
                "name": a["name"],
                "avatar": a.get("avatar", ""),
                "role": a.get("role", ""),
                "description": a.get("description", ""),
            })
    # Limit recommendations
    recommendations = recommendations[:6]

    # --- Daily activity (last 30 days) ---
    daily_activity = {}
    for c in user_chats:
        for m in c.get("messages", []):
            ca = m.get("created_at", "")
            if ca and ca >= thirty_days_ago:
                day = ca[:10]
                daily_activity[day] = daily_activity.get(day, 0) + 1

    activity_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        activity_series.append({"date": d, "messages": daily_activity.get(d, 0)})

    # --- Feedback given ---
    feedback_up = 0
    feedback_down = 0
    for c in user_chats:
        for m in c.get("messages", []):
            fb = m.get("feedback")
            if fb == "up":
                feedback_up += 1
            elif fb == "down":
                feedback_down += 1

    # --- Streak (consecutive days with activity) ---
    streak = 0
    for i in range(30):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        if daily_activity.get(d, 0) > 0:
            streak += 1
        else:
            break

    return {
        "stats": {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "credits_remaining": credits_remaining,
            "credits_used": credits_used,
            "plan": plan,
            "feedback_up": feedback_up,
            "feedback_down": feedback_down,
            "streak": streak,
        },
        "favorite_agents": favorites,
        "recommendations": recommendations,
        "daily_activity": activity_series,
    }

# ============== TEAM COLLABORATION ENDPOINTS ==============

@api_router.post("/teams")
async def create_team(data: TeamCreate, current_user: User = Depends(get_current_user)):
    """Create a new team. Owner is the creator."""
    existing = await db.teams.find_one({"owner_id": current_user.user_id})
    if existing:
        raise HTTPException(400, "You already own a team. Delete it first to create a new one.")
    
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    team = {
        "team_id": team_id,
        "name": data.name,
        "owner_id": current_user.user_id,
        "members": [
            {"user_id": current_user.user_id, "role": "owner", "email": current_user.email, "name": current_user.name, "joined_at": datetime.now(timezone.utc).isoformat()}
        ],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.insert_one(team)
    team.pop("_id", None)
    return team

@api_router.get("/teams")
async def get_my_teams(current_user: User = Depends(get_current_user)):
    """Get all teams the user belongs to (as owner or member)."""
    teams = await db.teams.find(
        {"members.user_id": current_user.user_id}, {"_id": 0}
    ).to_list(20)
    return teams

@api_router.get("/teams/{team_id}")
async def get_team(team_id: str, current_user: User = Depends(get_current_user)):
    """Get a single team's details."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id}, {"_id": 0})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    return team

@api_router.post("/teams/{team_id}/invite")
async def invite_to_team(team_id: str, data: TeamInvite, current_user: User = Depends(get_current_user)):
    """Invite a user by email. Only owner and admins can invite."""
    team = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not team:
        raise HTTPException(404, "Team not found")
    
    # Check permissions
    member = next((m for m in team["members"] if m["user_id"] == current_user.user_id), None)
    if not member or member["role"] not in ("owner", "admin"):
        raise HTTPException(403, "Only team owners and admins can invite members")
    
    # Check team size limit
    user_sub = await db.subscriptions.find_one({"user_id": team["owner_id"]}, {"_id": 0})
    plan_id = user_sub.get("plan_id", "free") if user_sub else "free"
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
    max_members = plan.get("max_team_members", 1)
    if max_members != -1 and len(team["members"]) >= max_members:
        raise HTTPException(400, f"Team size limit reached ({max_members} members on {plan['name']} plan). Upgrade to add more members.")
    
    # Check if already a member
    if any(m.get("email") == data.email for m in team["members"]):
        raise HTTPException(400, "This user is already a team member")
    
    # Check for existing pending invite
    existing_invite = await db.team_invites.find_one({"team_id": team_id, "email": data.email, "status": "pending"})
    if existing_invite:
        raise HTTPException(400, "An invite is already pending for this email")
    
    invite_token = uuid.uuid4().hex
    invite = {
        "invite_id": f"inv_{uuid.uuid4().hex[:12]}",
        "team_id": team_id,
        "team_name": team["name"],
        "email": data.email,
        "role": data.role if data.role in ("admin", "member") else "member",
        "invited_by": current_user.user_id,
        "invited_by_name": current_user.name,
        "status": "pending",
        "token": invite_token,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.team_invites.insert_one(invite)
    invite.pop("_id", None)
    
    # Send email notification (non-blocking, skips if SMTP not configured)
    asyncio.create_task(send_email_notification(
        to_email=data.email,
        subject=f"You've been invited to {team['name']} on MAARS Command",
        html_body=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#111;color:#fff;border-radius:12px;">
            <h2 style="color:#818cf8;">You're Invited!</h2>
            <p>{current_user.name} has invited you to join <strong>{team['name']}</strong> on MAARS Command as a <strong>{data.role}</strong>.</p>
            <p>Log in to your MAARS Command account to accept the invitation and start collaborating with your team.</p>
            <p style="margin-top:20px;"><a href="{os.environ.get('FRONTEND_URL', 'https://maarscommand.com')}/team" style="display:inline-block;padding:12px 24px;background:linear-gradient(to right,#6366f1,#8b5cf6);color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;">Accept Invitation</a></p>
            <p style="color:#888;font-size:12px;margin-top:30px;">MAARS Command by MAARS Global Corporation</p>
        </div>"""
    ))
    
    return invite

@api_router.get("/teams/invites/pending")
async def get_my_pending_invites(current_user: User = Depends(get_current_user)):
    """Get all pending invites for the current user."""
    invites = await db.team_invites.find(
        {"email": current_user.email, "status": "pending"}, {"_id": 0}
    ).to_list(50)
    return invites

@api_router.post("/teams/invites/{invite_id}/accept")
async def accept_invite(invite_id: str, current_user: User = Depends(get_current_user)):
    """Accept a team invite."""
    invite = await db.team_invites.find_one({"invite_id": invite_id, "email": current_user.email, "status": "pending"})
    if not invite:
        raise HTTPException(404, "Invite not found or already responded")
    
    team = await db.teams.find_one({"team_id": invite["team_id"]})
    if not team:
        raise HTTPException(404, "Team no longer exists")
    
    # Add member
    new_member = {
        "user_id": current_user.user_id,
        "role": invite["role"],
        "email": current_user.email,
        "name": current_user.name,
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    await db.teams.update_one(
        {"team_id": invite["team_id"]},
        {"$push": {"members": new_member}}
    )
    await db.team_invites.update_one({"invite_id": invite_id}, {"$set": {"status": "accepted"}})
    
    # Notify team owner
    owner_id = team.get("owner_id")
    if owner_id:
        await create_notification(owner_id, "team_join", f"{current_user.name} joined your team", f"{current_user.name} accepted the invite to {team.get('name', 'your team')}.", "/team")
    
    return {"success": True, "team_id": invite["team_id"], "team_name": invite["team_name"]}

@api_router.post("/teams/invites/{invite_id}/decline")
async def decline_invite(invite_id: str, current_user: User = Depends(get_current_user)):
    """Decline a team invite."""
    invite = await db.team_invites.find_one({"invite_id": invite_id, "email": current_user.email, "status": "pending"})
    if not invite:
        raise HTTPException(404, "Invite not found or already responded")
    await db.team_invites.update_one({"invite_id": invite_id}, {"$set": {"status": "declined"}})
    return {"success": True}

@api_router.put("/teams/{team_id}/members/{user_id}")
async def update_member_role(team_id: str, user_id: str, data: TeamMemberUpdate, current_user: User = Depends(get_current_user)):
    """Update a team member's role. Only owner can change roles."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    if team["owner_id"] != current_user.user_id:
        raise HTTPException(403, "Only the team owner can change roles")
    if user_id == current_user.user_id:
        raise HTTPException(400, "Cannot change your own role")
    if data.role not in ("admin", "member"):
        raise HTTPException(400, "Role must be 'admin' or 'member'")
    
    result = await db.teams.update_one(
        {"team_id": team_id, "members.user_id": user_id},
        {"$set": {"members.$.role": data.role}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Member not found in team")
    return {"success": True}

@api_router.delete("/teams/{team_id}/members/{user_id}")
async def remove_member(team_id: str, user_id: str, current_user: User = Depends(get_current_user)):
    """Remove a member from team. Owner/admins can remove, or members can leave."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    
    member = next((m for m in team["members"] if m["user_id"] == current_user.user_id), None)
    if not member:
        raise HTTPException(403, "You are not a member of this team")
    
    # Owners can't be removed
    if user_id == team["owner_id"]:
        raise HTTPException(400, "Cannot remove the team owner")
    
    # Self-removal (leaving) is always allowed
    is_self = user_id == current_user.user_id
    if not is_self and member["role"] not in ("owner", "admin"):
        raise HTTPException(403, "Only owners and admins can remove members")
    
    await db.teams.update_one(
        {"team_id": team_id},
        {"$pull": {"members": {"user_id": user_id}}}
    )
    return {"success": True}

@api_router.delete("/teams/{team_id}")
async def delete_team(team_id: str, current_user: User = Depends(get_current_user)):
    """Delete a team. Only the owner can delete."""
    team = await db.teams.find_one({"team_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    if team["owner_id"] != current_user.user_id:
        raise HTTPException(403, "Only the team owner can delete the team")
    
    await db.teams.delete_one({"team_id": team_id})
    await db.team_invites.delete_many({"team_id": team_id})
    # Unshare all team chats
    await db.chats.update_many(
        {"shared_with_team": team_id},
        {"$unset": {"shared_with_team": ""}}
    )
    return {"success": True}

@api_router.post("/chats/{chat_id}/share")
async def share_chat_with_team(chat_id: str, current_user: User = Depends(get_current_user)):
    """Toggle sharing a chat with the user's team."""
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id})
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    team = await db.teams.find_one({"members.user_id": current_user.user_id}, {"_id": 0, "team_id": 1})
    if not team:
        raise HTTPException(400, "You are not part of any team")
    
    is_shared = chat.get("shared_with_team") == team["team_id"]
    if is_shared:
        await db.chats.update_one({"chat_id": chat_id}, {"$unset": {"shared_with_team": ""}})
        return {"shared": False}
    else:
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"shared_with_team": team["team_id"]}})
        return {"shared": True, "team_id": team["team_id"]}

@api_router.get("/teams/{team_id}/shared-chats")
async def get_shared_chats(team_id: str, current_user: User = Depends(get_current_user)):
    """Get all chats shared with this team."""
    team = await db.teams.find_one({"team_id": team_id, "members.user_id": current_user.user_id})
    if not team:
        raise HTTPException(404, "Team not found or you're not a member")
    
    chats = await db.chats.find(
        {"shared_with_team": team_id},
        {"_id": 0, "chat_id": 1, "title": 1, "agent_id": 1, "user_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(100)
    
    # Add owner info
    for chat in chats:
        owner = await db.users.find_one({"user_id": chat["user_id"]}, {"_id": 0, "name": 1, "email": 1})
        chat["owner_name"] = owner.get("name", "Unknown") if owner else "Unknown"
    
    return chats

# ============== SUBSCRIPTION & PAYMENT ENDPOINTS ==============

@api_router.get("/plans")
async def get_plans():
    """Get all subscription plans + custom package config"""
    custom_config = await get_custom_package_config()
    custom_config.pop("config_type", None)
    credit_pkgs = await get_credit_packages()
    return {"plans": SUBSCRIPTION_PLANS, "credit_packages": credit_pkgs, "custom_package": custom_config}

@api_router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        # Create default free subscription
        sub = {
            "user_id": current_user.user_id,
            "plan_id": "free",
            "credits": 50,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "renewed_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(sub)
    
    plan_info = SUBSCRIPTION_PLANS.get(sub.get("plan_id", "free"), SUBSCRIPTION_PLANS["free"])
    return {**sub, "plan_info": plan_info}

@api_router.post("/checkout")
async def create_checkout(checkout_data: CheckoutRequest, request: Request, current_user: User = Depends(get_current_user)):
    """Create a Stripe checkout session for subscription or credits"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    host_url = checkout_data.origin_url
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/stripe"
    currency = checkout_data.currency.lower()
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    if checkout_data.type == "subscription":
        if checkout_data.plan_id not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan = SUBSCRIPTION_PLANS[checkout_data.plan_id]
        price_key = "price_bdt" if currency == "bdt" else "price_usd"
        if plan[price_key] == 0:
            raise HTTPException(status_code=400, detail="Free plan doesn't require payment")
        
        amount = plan[price_key]
        metadata = {
            "type": "subscription",
            "plan_id": checkout_data.plan_id,
            "user_id": current_user.user_id,
            "email": current_user.email,
            "currency": currency
        }
    elif checkout_data.type == "credits":
        credit_pkgs = await get_credit_packages()
        
        # Support custom credit amounts (custom_<credits>)
        if checkout_data.package_id and checkout_data.package_id.startswith("custom_"):
            try:
                custom_credits = int(checkout_data.package_id.split("_")[1])
                if custom_credits < 5:
                    raise HTTPException(status_code=400, detail="Minimum 5 credits")
                custom_price_usd = custom_credits / 5.0
                rate = await get_usd_bdt_rate()
                custom_price_bdt = round(custom_price_usd * rate, 2)
                price = custom_price_bdt if currency == "bdt" else custom_price_usd
                metadata = {
                    "type": "credits",
                    "package_id": checkout_data.package_id,
                    "credits": str(custom_credits),
                    "user_id": current_user.user_id,
                    "email": current_user.email,
                    "currency": currency
                }
                amount = price
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid custom credit amount")
        elif checkout_data.package_id not in credit_pkgs:
            raise HTTPException(status_code=400, detail="Invalid credit package")
        else:
            package = credit_pkgs[checkout_data.package_id]
            price_key = "price_bdt" if currency == "bdt" else "price_usd"
            amount = package[price_key]
            metadata = {
                "type": "credits",
                "package_id": checkout_data.package_id,
                "credits": str(package["credits"]),
                "user_id": current_user.user_id,
                "email": current_user.email,
                "currency": currency
            }
    else:
        raise HTTPException(status_code=400, detail="Invalid checkout type")
    
    success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/settings"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(amount),
        currency=currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "type": checkout_data.type,
        "amount": amount,
        "currency": "usd",
        "metadata": metadata,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, current_user: User = Depends(get_current_user)):
    """Check payment status and update subscription/credits"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
    except Exception as e:
        logger.error(f"Error checking checkout status: {e}")
        raise HTTPException(status_code=400, detail="Failed to check payment status")
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if already processed
    if transaction.get("payment_status") == "paid":
        return {"status": "success", "message": "Payment already processed", "payment_status": "paid"}
    
    # Update transaction
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": status.status,
            "payment_status": status.payment_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # If payment successful, update subscription or add credits
    if status.payment_status == "paid":
        metadata = transaction.get("metadata", {})
        
        if metadata.get("type") == "subscription":
            plan_id = metadata.get("plan_id")
            plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$set": {
                    "plan_id": plan_id,
                    "credits": plan["credits"],
                    "credits_used": 0,
                    "status": "active",
                    "renewed_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            return {"status": "success", "message": f"Subscribed to {plan['name']} plan", "payment_status": "paid"}
        
        elif metadata.get("type") == "credits":
            credits_to_add = int(metadata.get("credits", 0))
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$inc": {"credits": credits_to_add}},
                upsert=True
            )
            return {"status": "success", "message": f"Added {credits_to_add} credits", "payment_status": "paid"}
        
        elif metadata.get("type") == "custom_package":
            credits_to_add = int(metadata.get("credits", 0))
            selected_agents = [a for a in metadata.get("selected_agents", "").split(",") if a]
            include_commander = metadata.get("include_commander", "False") == "True"
            
            await db.subscriptions.update_one(
                {"user_id": current_user.user_id},
                {"$set": {
                    "plan_id": "custom",
                    "credits": credits_to_add,
                    "credits_used": 0,
                    "selected_agents": selected_agents,
                    "has_commander": include_commander,
                    "status": "active",
                    "renewed_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            return {"status": "success", "message": f"Custom package activated with {len(selected_agents)} agents and {credits_to_add} credits", "payment_status": "paid"}
    
    return {"status": status.status, "payment_status": status.payment_status}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "status": webhook_response.event_type,
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Process payment if successful
            if webhook_response.payment_status == "paid":
                transaction = await db.payment_transactions.find_one(
                    {"session_id": webhook_response.session_id}, {"_id": 0}
                )
                if transaction:
                    metadata = transaction.get("metadata", {})
                    user_id = metadata.get("user_id")
                    
                    if metadata.get("type") == "subscription":
                        plan_id = metadata.get("plan_id")
                        plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["free"])
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "plan_id": plan_id,
                                "credits": plan["credits"],
                                "credits_used": 0,
                                "status": "active",
                                "renewed_at": datetime.now(timezone.utc).isoformat()
                            }},
                            upsert=True
                        )
                    elif metadata.get("type") == "credits":
                        credits_to_add = int(metadata.get("credits", 0))
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$inc": {"credits": credits_to_add}},
                            upsert=True
                        )
                    elif metadata.get("type") == "custom_package":
                        credits_to_add = int(metadata.get("credits", 0))
                        selected_agents = [a for a in metadata.get("selected_agents", "").split(",") if a]
                        include_commander = metadata.get("include_commander", "False") == "True"
                        await db.subscriptions.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "plan_id": "custom",
                                "credits": credits_to_add,
                                "credits_used": 0,
                                "selected_agents": selected_agents,
                                "has_commander": include_commander,
                                "status": "active",
                                "renewed_at": datetime.now(timezone.utc).isoformat()
                            }},
                            upsert=True
                        )
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@api_router.get("/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """Get user's current credits"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        return {"credits": 50, "plan": "free"}
    return {"credits": sub.get("credits", 0), "plan": sub.get("plan_id", "free")}

# ============== CUSTOM PACKAGE ENDPOINTS ==============

@api_router.get("/custom-package/config")
async def get_custom_package_config_endpoint():
    """Get custom package pricing config (public)"""
    config = await get_custom_package_config()
    config.pop("config_type", None)
    return config

@api_router.post("/custom-package/checkout")
async def custom_package_checkout(request: Request, current_user: User = Depends(get_current_user)):
    """Create a Stripe checkout for a custom package"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    body = await request.json()
    selected_agents = body.get("selected_agents", [])
    credit_preset_id = body.get("credit_preset_id", "")
    include_commander = body.get("include_commander", False)
    origin_url = body.get("origin_url", "")
    currency = body.get("currency", "usd").lower()
    
    if not selected_agents:
        raise HTTPException(status_code=400, detail="Select at least one agent")
    if not credit_preset_id:
        raise HTTPException(status_code=400, detail="Select a credit package")
    
    config = await get_custom_package_config()
    
    # Find the credit preset
    credit_preset = None
    for preset in config.get("credit_presets", []):
        if preset["id"] == credit_preset_id:
            credit_preset = preset
            break
    if not credit_preset:
        raise HTTPException(status_code=400, detail="Invalid credit preset")
    
    price_key = "price_bdt" if currency == "bdt" else "price_usd"
    agent_price_key = f"per_agent_{price_key}"
    commander_price_key = f"commander_addon_{price_key}"
    
    # Calculate total
    num_agents = len(selected_agents)
    agent_cost = num_agents * config.get(agent_price_key, config.get("per_agent_price_usd", 5.0))
    credit_cost = credit_preset[price_key]
    commander_cost = config.get(commander_price_key, 0) if include_commander else 0
    total = agent_cost + credit_cost + commander_cost
    
    if total <= 0:
        raise HTTPException(status_code=400, detail="Invalid package total")
    
    metadata = {
        "type": "custom_package",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "selected_agents": ",".join(selected_agents),
        "credit_preset_id": credit_preset_id,
        "credits": str(credit_preset["credits"]),
        "include_commander": str(include_commander),
        "currency": currency
    }
    
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(total),
        currency=currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "type": "custom_package",
        "amount": total,
        "currency": currency,
        "metadata": metadata,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {
        "checkout_url": session.url,
        "session_id": session.session_id,
        "breakdown": {
            "agents": num_agents,
            "agent_cost": agent_cost,
            "credits": credit_preset["credits"],
            "credit_cost": credit_cost,
            "commander": include_commander,
            "commander_cost": commander_cost,
            "total": total
        }
    }

@api_router.get("/subscription/agents")
async def get_selected_agents(current_user: User = Depends(get_current_user)):
    """Get user's selected agents"""
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        return {"selected_agents": [], "plan_id": "free", "max_agents": 1, "includes_commander": False}
    
    plan_id = sub.get("plan_id", "free")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
    
    is_custom = plan_id == "custom"
    selected = sub.get("selected_agents", [])
    has_commander = sub.get("has_commander", False)
    
    if not is_custom and plan:
        includes_commander = plan.get("includes_commander", False)
    else:
        includes_commander = has_commander
    
    return {
        "selected_agents": selected,
        "plan_id": plan_id,
        "max_agents": plan.get("max_agents", 1) if plan else 0,
        "includes_commander": includes_commander,
        "is_custom": is_custom
    }

@api_router.put("/subscription/agents")
async def update_selected_agents(request: Request, current_user: User = Depends(get_current_user)):
    """Update user's selected agents (for fixed plans)"""
    body = await request.json()
    selected_agents = body.get("selected_agents", [])
    
    is_admin = current_user.email == ADMIN_EMAIL
    
    sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=400, detail="No subscription found")
    
    plan_id = sub.get("plan_id", "free")
    
    if plan_id == "custom":
        raise HTTPException(status_code=400, detail="Custom package agents are set at purchase time")
    
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
    max_agents = plan.get("max_agents", 1)
    
    # Filter out commander from count (it's controlled by plan)
    non_commander = [a for a in selected_agents if a != "agent_commander"]
    
    if not is_admin and len(non_commander) > max_agents:
        raise HTTPException(status_code=400, detail=f"Your {plan['name']} plan allows up to {max_agents} agents. You selected {len(non_commander)}.")
    
    await db.subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"selected_agents": selected_agents}}
    )
    
    return {"selected_agents": selected_agents, "message": "Agents updated"}


# ============== ADMIN ENDPOINTS ==============



@api_router.get("/admin/api-keys")
async def admin_get_api_keys(admin: User = Depends(require_admin)):
    """Get current API key configuration (masked)"""
    config = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
    if not config:
        config = {"active_provider": "emergent", "openai_key": "", "anthropic_key": "", "gemini_key": ""}
    
    # Mask keys for display
    def mask(key):
        if not key:
            return ""
        if len(key) < 10:
            return "***"
        return key[:8] + "..." + key[-4:]
    
    # Direct provider cost reference (per 1M tokens unless noted)
    cost_reference = {
        "openai": {
            "models": [
                {"name": "GPT-5.2", "input": "$2.50", "output": "$10.00"},
                {"name": "GPT-4o", "input": "$2.50", "output": "$10.00"},
                {"name": "GPT-4o Mini", "input": "$0.15", "output": "$0.60"},
                {"name": "O3", "input": "$10.00", "output": "$40.00"},
                {"name": "O3 Mini", "input": "$1.10", "output": "$4.40"},
                {"name": "GPT Image 1", "input": "$0.02/img", "output": "1024x1024"},
                {"name": "DALL-E 3", "input": "$0.04/img", "output": "1024x1024"},
                {"name": "Sora 2", "input": "$0.10/sec", "output": "4-12 sec video"},
            ],
            "unit": "per 1M tokens (text) / per image or second (gen)"
        },
        "anthropic": {
            "models": [
                {"name": "Claude Sonnet 4.5", "input": "$3.00", "output": "$15.00"},
                {"name": "Claude Opus 4.5", "input": "$15.00", "output": "$75.00"},
                {"name": "Claude Haiku 4.5", "input": "$0.80", "output": "$4.00"},
            ],
            "unit": "per 1M tokens"
        },
        "gemini": {
            "models": [
                {"name": "Gemini 3 Flash", "input": "$0.075", "output": "$0.30"},
                {"name": "Gemini 3 Pro", "input": "$1.25", "output": "$5.00"},
            ],
            "unit": "per 1M tokens"
        },
        "xai": {
            "models": [
                {"name": "Grok 3", "input": "$3.00", "output": "$15.00"},
                {"name": "Grok 3 Mini", "input": "$0.30", "output": "$0.50"},
                {"name": "Grok 2", "input": "$2.00", "output": "$10.00"},
            ],
            "unit": "per 1M tokens"
        },
        "deepseek": {
            "models": [
                {"name": "DeepSeek Chat", "input": "$0.14", "output": "$0.28"},
                {"name": "DeepSeek Reasoner", "input": "$0.55", "output": "$2.19"},
            ],
            "unit": "per 1M tokens"
        },
        "mistral": {
            "models": [
                {"name": "Mistral Large", "input": "$2.00", "output": "$6.00"},
                {"name": "Mistral Medium", "input": "$0.40", "output": "$2.00"},
                {"name": "Mistral Small", "input": "$0.10", "output": "$0.30"},
            ],
            "unit": "per 1M tokens"
        },
        "perplexity": {
            "models": [
                {"name": "Sonar", "input": "$1.00", "output": "$1.00"},
                {"name": "Sonar Pro", "input": "$3.00", "output": "$15.00"},
            ],
            "unit": "per 1M tokens + $5/1K search"
        },
        "cohere": {
            "models": [
                {"name": "Command R+", "input": "$2.50", "output": "$10.00"},
                {"name": "Command R", "input": "$0.15", "output": "$0.60"},
            ],
            "unit": "per 1M tokens"
        },
        "elevenlabs": {
            "models": [
                {"name": "Multilingual v2", "input": "$0.30/1K chars", "output": "TTS audio"},
                {"name": "Turbo v2.5", "input": "$0.18/1K chars", "output": "Fast TTS"},
            ],
            "unit": "per 1K characters"
        },
        "slack": {
            "models": [
                {"name": "Post Message", "input": "Free", "output": "per message"},
                {"name": "Read Channel", "input": "Free", "output": "per request"},
            ],
            "unit": "Free with Bot Token (Slack workspace subscription separate)"
        },
        "github": {
            "models": [
                {"name": "REST API", "input": "Free", "output": "5,000 req/hr"},
                {"name": "Create Issue/PR", "input": "Free", "output": "per action"},
            ],
            "unit": "Free for public repos. Requires Personal Access Token"
        },
        "sendgrid": {
            "models": [
                {"name": "Transactional Email", "input": "$0.001", "output": "per email"},
                {"name": "Marketing Email", "input": "$0.002", "output": "per email"},
            ],
            "unit": "Free: 100/day. Essentials: $19.95/50K emails/mo"
        },
        "resend": {
            "models": [
                {"name": "Email Send", "input": "$0.001", "output": "per email"},
                {"name": "Batch Email", "input": "$0.0008", "output": "per email"},
            ],
            "unit": "Free: 100/day. Pro: $20/50K emails/mo"
        },
        "twilio": {
            "models": [
                {"name": "SMS (US)", "input": "$0.0079", "output": "per SMS"},
                {"name": "SMS (Intl)", "input": "$0.01-0.15", "output": "per SMS"},
                {"name": "Voice Call", "input": "$0.014", "output": "per minute"},
            ],
            "unit": "Pay-as-you-go. Prices vary by country"
        },
        "airtable": {
            "models": [
                {"name": "Read Records", "input": "Free", "output": "5 req/sec"},
                {"name": "Write Records", "input": "Free", "output": "5 req/sec"},
            ],
            "unit": "Free: 1,000 records. Plus: $20/mo unlimited"
        },
        "calendly": {
            "models": [
                {"name": "Schedule Event", "input": "Free", "output": "per event"},
                {"name": "List Events", "input": "Free", "output": "per request"},
            ],
            "unit": "Free tier available. Pro: $12/mo includes API"
        },
        "giphy": {
            "models": [
                {"name": "Search GIFs", "input": "Free", "output": "42 req/hr"},
                {"name": "Trending GIFs", "input": "Free", "output": "42 req/hr"},
            ],
            "unit": "Free API. Rate limited (production key: 1000 req/hr)"
        },
        "google_suite": {
            "models": [
                {"name": "Gmail Send", "input": "Free", "output": "per email"},
                {"name": "Calendar Event", "input": "Free", "output": "per event"},
                {"name": "Drive Read/Write", "input": "Free", "output": "per file"},
            ],
            "unit": "Free with service account. Google Workspace quota limits apply"
        },
    }
    
    all_providers = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
    result = {
        "active_provider": config.get("active_provider", "emergent"),
        "emergent_key_set": bool(EMERGENT_LLM_KEY),
        "cost_reference": cost_reference,
    }
    for p in all_providers:
        key_val = config.get(f"{p}_key", "")
        result[f"{p}_key"] = mask(key_val)
        result[f"{p}_key_set"] = bool(key_val)
    
    return result

@api_router.put("/admin/api-keys")
async def admin_update_api_keys(request: Request, admin: User = Depends(require_admin)):
    """Admin can update API keys and switch between Emergent and direct provider keys"""
    key_data = await request.json()
    update_doc = {
        "config_type": "api_keys",
        "active_provider": key_data.get("active_provider", "emergent"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }
    
    # Only update keys that are provided (non-empty)
    all_providers = ["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"]
    for p in all_providers:
        if key_data.get(f"{p}_key"):
            update_doc[f"{p}_key"] = key_data[f"{p}_key"]
    
    # Merge with existing (preserve keys not being updated)
    existing = await db.platform_config.find_one({"config_type": "api_keys"})
    if existing:
        for p in all_providers:
            field = f"{p}_key"
            if field not in update_doc and field in existing:
                update_doc[field] = existing[field]
    
    await db.platform_config.update_one(
        {"config_type": "api_keys"},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "API keys updated", "active_provider": update_doc["active_provider"]}

@api_router.post("/admin/api-keys/test")
async def admin_test_api_key(request: Request, admin: User = Depends(require_admin)):
    """Test an API key using lightweight validation (list models, not completions)"""
    test_data = await request.json()
    provider = test_data.get("provider")
    api_key = test_data.get("api_key")
    
    if not provider or not api_key:
        raise HTTPException(status_code=400, detail="Provider and api_key required")
    
    test_configs = {
        "openai": {
            "url": "https://api.openai.com/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('data', []))} models.",
            "help": "Get your key at https://platform.openai.com/api-keys"
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/models",
            "headers": {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            "success_codes": [200, 403],
            "success_msg": lambda r: "Key verified! Anthropic API access confirmed.",
            "help": "Get your key at https://console.anthropic.com/settings/keys"
        },
        "gemini": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            "headers": {},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('models', []))} Gemini models.",
            "help": "Get your key at https://aistudio.google.com/app/apikey"
        },
        "xai": {
            "url": "https://api.x.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! xAI (Grok) API access confirmed. {len(r.json().get('data', []))} models.",
            "help": "Get your key at https://console.x.ai/team/default/api-keys"
        },
        "deepseek": {
            "url": "https://api.deepseek.com/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! DeepSeek API access confirmed.",
            "help": "Get your key at https://platform.deepseek.com/api_keys"
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: f"Key verified! Access to {len(r.json().get('data', []))} Mistral models.",
            "help": "Get your key at https://console.mistral.ai/api-keys"
        },
        "perplexity": {
            "url": "https://api.perplexity.ai/chat/completions",
            "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            "method": "post",
            "body": {"model": "sonar", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
            "success_codes": [200, 422],
            "success_msg": lambda r: "Key verified! Perplexity API access confirmed.",
            "help": "Get your key at https://www.perplexity.ai/settings/api"
        },
        "cohere": {
            "url": "https://api.cohere.ai/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "success_msg": lambda r: "Key verified! Cohere API access confirmed.",
            "help": "Get your key at https://dashboard.cohere.com/api-keys"
        },
        "elevenlabs": {
            "url": "https://api.elevenlabs.io/v1/user",
            "headers": {"xi-api-key": api_key},
            "success_msg": lambda r: "Key verified! ElevenLabs API access confirmed.",
            "help": "Get your key at https://elevenlabs.io/app/settings/api-keys"
        },
    }
    
    config = test_configs.get(provider)
    if not config:
        return {"success": False, "message": f"Unknown provider '{provider}'. Supported: {', '.join(test_configs.keys())}"}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            success_codes = config.get("success_codes", [200])
            if config.get("method") == "post":
                resp = await client.post(config["url"], headers=config["headers"], json=config.get("body", {}))
            else:
                resp = await client.get(config["url"], headers=config["headers"])
            
            if resp.status_code in success_codes or resp.status_code == 200:
                return {"success": True, "message": config["success_msg"](resp)}
            elif resp.status_code == 401:
                return {"success": False, "message": f"Invalid API key. The key was rejected by {provider}. {config['help']}"}
            elif resp.status_code == 403:
                return {"success": True, "message": f"Key accepted but may have restricted permissions. Check your {provider} dashboard."}
            elif resp.status_code == 429:
                return {"success": False, "message": f"Rate limited by {provider}. Your key is valid but you've hit the rate limit. Try again in a moment."}
            else:
                error_detail = ""
                try:
                    error_detail = resp.json().get("error", {}).get("message", resp.text[:150])
                except Exception:
                    error_detail = resp.text[:150]
                return {"success": False, "message": f"{provider} returned {resp.status_code}: {error_detail}. {config['help']}"}
    except httpx.ConnectError:
        return {"success": False, "message": f"Cannot connect to {provider} API. Check your internet connection or the provider may be down."}
    except httpx.TimeoutException:
        return {"success": False, "message": f"Connection to {provider} timed out. The API may be slow or unreachable. Try again."}
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)[:150]}. {config.get('help', '')}"}


@api_router.get("/admin/pricing")
async def admin_get_pricing(admin: User = Depends(require_admin)):
    """Get current pricing configuration from DB or default"""
    pricing = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
    if not pricing:
        # Return default pricing
        pricing = {
            "config_type": "pricing",
            "plans": SUBSCRIPTION_PLANS,
            "custom_agent_credit_cost": CUSTOM_AGENT_CREDIT_COST,
            "ai_cost_per_credit": 0.003,
            "target_profit_margin": 200,
            "bdt_exchange_rate": 107
        }
    return pricing

@api_router.put("/admin/pricing")
async def admin_update_pricing(request: Request, admin: User = Depends(require_admin)):
    """Admin can update platform pricing. Changes take effect immediately."""
    global SUBSCRIPTION_PLANS, CUSTOM_AGENT_CREDIT_COST
    
    pricing_data = await request.json()
    
    plans = pricing_data.get("plans")
    if plans:
        # Validate plan structure
        for plan_id, plan in plans.items():
            if not all(k in plan for k in ["name", "price_usd", "price_bdt", "credits", "max_agents", "max_custom_agents"]):
                raise HTTPException(status_code=400, detail=f"Invalid plan structure for {plan_id}")
            # Ensure max_team_members is preserved
            if "max_team_members" not in plan:
                plan["max_team_members"] = SUBSCRIPTION_PLANS.get(plan_id, {}).get("max_team_members", 1)
        SUBSCRIPTION_PLANS.update(plans)
    
    if "custom_agent_credit_cost" in pricing_data:
        CUSTOM_AGENT_CREDIT_COST = pricing_data["custom_agent_credit_cost"]
    
    # Save to DB
    config_doc = {
        "config_type": "pricing",
        "plans": SUBSCRIPTION_PLANS,
        "custom_agent_credit_cost": CUSTOM_AGENT_CREDIT_COST,
        "ai_cost_per_credit": pricing_data.get("ai_cost_per_credit", 0.003),
        "target_profit_margin": pricing_data.get("target_profit_margin", 200),
        "bdt_exchange_rate": pricing_data.get("bdt_exchange_rate", 107),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }
    
    await db.platform_config.update_one(
        {"config_type": "pricing"},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "Pricing updated successfully", "pricing": config_doc}

@api_router.get("/admin/avg-cost")
async def admin_avg_cost(admin: User = Depends(require_admin)):
    """Get the real average cost per API call from usage_logs"""
    cost_pipeline = [
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"}
        }}
    ]
    cost_result = await db.usage_logs.aggregate(cost_pipeline).to_list(1)
    if cost_result and cost_result[0]["total_calls"] > 0:
        r = cost_result[0]
        avg = r["total_cost"] / r["total_calls"]
        return {
            "avg_cost_per_credit": round(avg, 6),
            "total_cost_usd": round(r["total_cost"], 6),
            "total_calls": r["total_calls"],
            "total_input_tokens": r.get("total_input_tokens", 0),
            "total_output_tokens": r.get("total_output_tokens", 0),
            "source": "real_usage"
        }
    return {"avg_cost_per_credit": 0.003, "total_cost_usd": 0, "total_calls": 0, "total_input_tokens": 0, "total_output_tokens": 0, "source": "default"}

@api_router.get("/exchange-rate")
async def get_exchange_rate():
    """Get live USD/BDT exchange rate (public, no auth required)"""
    rate = await get_live_bdt_rate()
    return {"usd_bdt": rate, "source": "hexarate" if _exchange_rate_cache.get("rate") else "fallback"}

@api_router.post("/admin/pricing/calculate")
async def admin_calculate_pricing(calc_data: dict, admin: User = Depends(require_admin)):
    """Calculate recommended prices based on AI costs and target profit margin"""
    ai_cost_per_credit = calc_data.get("ai_cost_per_credit", 0.003)
    target_margin_pct = calc_data.get("target_profit_margin", 200)
    bdt_rate = calc_data.get("bdt_exchange_rate", 107)
    
    # Calculate recommended prices for each plan
    plans = {}
    plan_configs = {
        "free": {"credits": 50, "max_agents": 1, "max_custom_agents": 0},
        "starter": {"credits": 500, "max_agents": 5, "max_custom_agents": 2},
        "pro": {"credits": 2000, "max_agents": 10, "max_custom_agents": 5},
        "business": {"credits": 6000, "max_agents": 20, "max_custom_agents": -1},
    }
    
    for plan_id, config in plan_configs.items():
        base_cost_usd = config["credits"] * ai_cost_per_credit
        margin_multiplier = 1 + (target_margin_pct / 100)
        recommended_usd = round(base_cost_usd * margin_multiplier, 2)
        recommended_bdt = round(recommended_usd * bdt_rate)
        
        plans[plan_id] = {
            "credits": config["credits"],
            "base_ai_cost_usd": round(base_cost_usd, 2),
            "recommended_price_usd": recommended_usd if plan_id != "free" else 0,
            "recommended_price_bdt": recommended_bdt if plan_id != "free" else 0,
            "profit_per_user_usd": round(recommended_usd - base_cost_usd, 2) if plan_id != "free" else 0,
            "actual_margin_pct": target_margin_pct if plan_id != "free" else 0
        }
    
    return {
        "ai_cost_per_credit": ai_cost_per_credit,
        "target_profit_margin": target_margin_pct,
        "bdt_exchange_rate": bdt_rate,
        "plan_calculations": plans
    }


@api_router.get("/admin/stats")
async def admin_stats(admin: User = Depends(require_admin)):
    """Get platform-wide statistics for admin"""
    total_users = await db.users.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    total_agents = await db.agents.count_documents({})
    custom_agents = await db.agents.count_documents({"is_custom": True})
    active_subs = await db.subscriptions.count_documents({"status": "active"})
    
    # Count messages across all chats
    msg_pipeline = [
        {"$project": {"message_count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$message_count"}}}
    ]
    msg_result = await db.chats.aggregate(msg_pipeline).to_list(1)
    total_messages = msg_result[0]["total"] if msg_result else 0
    
    # Plan distribution
    plan_pipeline = [
        {"$group": {"_id": "$plan_id", "count": {"$sum": 1}}}
    ]
    plan_dist = await db.subscriptions.aggregate(plan_pipeline).to_list(10)
    plan_distribution = {item["_id"]: item["count"] for item in plan_dist if item["_id"]}
    
    # Revenue from transactions
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0
    total_transactions = rev_result[0]["count"] if rev_result else 0
    
    # Total credits used
    credits_pipeline = [
        {"$group": {"_id": None, "total_used": {"$sum": "$credits_used"}, "total_remaining": {"$sum": "$credits"}}}
    ]
    credits_result = await db.subscriptions.aggregate(credits_pipeline).to_list(1)
    total_credits_used = credits_result[0]["total_used"] if credits_result else 0
    total_credits_remaining = credits_result[0]["total_remaining"] if credits_result else 0
    
    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "total_tasks": total_tasks,
        "total_agents": total_agents,
        "custom_agents": custom_agents,
        "total_messages": total_messages,
        "active_subscriptions": active_subs,
        "plan_distribution": plan_distribution,
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "total_credits_used": total_credits_used,
        "total_credits_remaining": total_credits_remaining
    }

@api_router.get("/admin/profit")
async def admin_profit(admin: User = Depends(require_admin)):
    """Get profit analytics - revenue vs API costs"""
    
    # Total revenue
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0
    
    # Total API cost from usage logs
    cost_pipeline = [
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"},
            "total_calls": {"$sum": 1}
        }}
    ]
    cost_result = await db.usage_logs.aggregate(cost_pipeline).to_list(1)
    total_cost = cost_result[0]["total_cost"] if cost_result else 0
    total_input_tokens = cost_result[0]["total_input_tokens"] if cost_result else 0
    total_output_tokens = cost_result[0]["total_output_tokens"] if cost_result else 0
    total_api_calls = cost_result[0]["total_calls"] if cost_result else 0
    
    # Per-provider breakdown
    provider_pipeline = [
        {"$group": {
            "_id": "$provider",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1},
            "input_tokens": {"$sum": "$input_tokens"},
            "output_tokens": {"$sum": "$output_tokens"}
        }}
    ]
    provider_result = await db.usage_logs.aggregate(provider_pipeline).to_list(10)
    provider_costs = {item["_id"]: {
        "cost": round(item["cost"], 4),
        "calls": item["calls"],
        "input_tokens": item["input_tokens"],
        "output_tokens": item["output_tokens"]
    } for item in provider_result if item["_id"]}
    
    # Per-model breakdown
    model_pipeline = [
        {"$group": {
            "_id": "$model",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1},
        }},
        {"$sort": {"cost": -1}}
    ]
    model_result = await db.usage_logs.aggregate(model_pipeline).to_list(20)
    model_costs = [{"model": item["_id"], "cost": round(item["cost"], 4), "calls": item["calls"]} for item in model_result if item["_id"]]
    
    # Per-plan estimated cost (based on credits used * avg cost per credit)
    avg_cost_per_call = total_cost / max(total_api_calls, 1)
    
    plan_profits = {}
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan_id == "free":
            plan_profits[plan_id] = {"revenue": 0, "est_max_cost": round(plan["credits"] * avg_cost_per_call, 2), "profit": 0}
        else:
            plan_profits[plan_id] = {
                "revenue": plan["price_usd"],
                "est_max_cost": round(plan["credits"] * avg_cost_per_call, 2),
                "profit": round(plan["price_usd"] - (plan["credits"] * avg_cost_per_call), 2),
                "margin_pct": round(((plan["price_usd"] - (plan["credits"] * avg_cost_per_call)) / max(plan["price_usd"], 0.01)) * 100, 1)
            }
    
    net_profit = total_revenue - total_cost
    
    return {
        "revenue": round(total_revenue, 2),
        "total_api_cost": round(total_cost, 4),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round((net_profit / max(total_revenue, 0.01)) * 100, 1),
        "total_api_calls": total_api_calls,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "avg_cost_per_call": round(avg_cost_per_call, 5),
        "provider_costs": provider_costs,
        "model_costs": model_costs,
        "plan_profits": plan_profits,
    }

@api_router.get("/admin/api-usage")
async def admin_api_usage(admin: User = Depends(require_admin)):
    """Check balance/usage for saved API keys"""
    api_keys_config = await get_api_keys()
    result = {}
    
    provider_checks = {
        "openai": {
            "url": "https://api.openai.com/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "OpenAI uses pay-as-you-go billing. Check dashboard.openai.com for balance."
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/models",
            "headers_fn": lambda k: {"x-api-key": k, "anthropic-version": "2023-06-01"},
            "ok_codes": [200, 403],
            "note": "Anthropic uses pay-as-you-go billing. Check console.anthropic.com for balance."
        },
        "gemini": {
            "url_fn": lambda k: f"https://generativelanguage.googleapis.com/v1beta/models?key={k}",
            "ok_codes": [200],
            "models_key": "models",
            "note": "Gemini has free tier with rate limits. Paid tier via Google Cloud billing."
        },
        "xai": {
            "url": "https://api.x.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "xAI Grok. Check console.x.ai for billing."
        },
        "deepseek": {
            "url": "https://api.deepseek.com/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "note": "DeepSeek. Check platform.deepseek.com for billing."
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "models_key": "data",
            "note": "Mistral AI. Check console.mistral.ai for billing."
        },
        "perplexity": {
            "url": "https://api.perplexity.ai/chat/completions",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200, 401, 422],
            "note": "Perplexity. Check perplexity.ai/settings for billing."
        },
        "cohere": {
            "url": "https://api.cohere.ai/v1/models",
            "headers_fn": lambda k: {"Authorization": f"Bearer {k}"},
            "ok_codes": [200],
            "note": "Cohere. Check dashboard.cohere.com for billing."
        },
        "elevenlabs": {
            "url": "https://api.elevenlabs.io/v1/user",
            "headers_fn": lambda k: {"xi-api-key": k},
            "ok_codes": [200],
            "note": "ElevenLabs TTS. Check elevenlabs.io for billing."
        },
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        for provider_id, check in provider_checks.items():
            key = api_keys_config.get(provider_id, "")
            if not key:
                continue
            try:
                url = check.get("url_fn", lambda k: check["url"])(key)
                hdrs = check.get("headers_fn", lambda k: {})(key)
                resp = await client.get(url, headers=hdrs)
                entry = {
                    "status": "active" if resp.status_code in check["ok_codes"] else "error",
                    "note": check.get("note", "")
                }
                models_key = check.get("models_key")
                if models_key and resp.status_code == 200:
                    try:
                        entry["models_available"] = len(resp.json().get(models_key, []))
                    except Exception:
                        pass
                result[provider_id] = entry
            except Exception as e:
                result[provider_id] = {"status": "error", "note": str(e)[:100]}
    
    # Our tracked usage per provider
    provider_pipeline = [
        {"$group": {
            "_id": "$provider",
            "total_cost": {"$sum": "$estimated_cost_usd"},
            "total_calls": {"$sum": 1},
            "total_tokens": {"$sum": {"$add": ["$input_tokens", "$output_tokens"]}}
        }}
    ]
    usage = await db.usage_logs.aggregate(provider_pipeline).to_list(10)
    tracked_usage = {item["_id"]: {
        "total_cost": round(item["total_cost"], 4),
        "total_calls": item["total_calls"],
        "total_tokens": item["total_tokens"]
    } for item in usage if item["_id"]}
    
    return {"providers": result, "tracked_usage": tracked_usage}

@api_router.get("/admin/users")
async def admin_get_users(admin: User = Depends(require_admin)):
    """Get all users with their subscription info"""
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(500)
    
    # Enrich with subscription data
    for u in users:
        sub = await db.subscriptions.find_one({"user_id": u["user_id"]}, {"_id": 0})
        u["subscription"] = sub or {"plan_id": "free", "credits": 0, "credits_used": 0}
        u["is_admin"] = u.get("email") == ADMIN_EMAIL
    
    return users

@api_router.get("/admin/agents")
async def admin_get_all_agents(admin: User = Depends(require_admin)):
    """Get all agents including custom ones"""
    agents = await db.agents.find({}, {"_id": 0}).to_list(200)
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    return agents

@api_router.post("/admin/agents")
async def admin_create_agent(agent_data: AgentCreate, admin: User = Depends(require_admin)):
    """Admin can create agents visible to all users"""
    agent_id = f"agent_{uuid.uuid4().hex[:12]}"
    agent_doc = {
        "agent_id": agent_id,
        "name": agent_data.name,
        "description": agent_data.description,
        "avatar": agent_data.avatar or "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg",
        "role": agent_data.role,
        "system_prompt": agent_data.system_prompt,
        "model_provider": agent_data.model_provider,
        "model_name": agent_data.model_name,
        "is_custom": False,
        "creator_id": None,
        "capabilities": agent_data.capabilities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.agents.insert_one(agent_doc)
    agent_doc.pop("_id", None)
    agent_doc['created_at'] = datetime.fromisoformat(agent_doc['created_at'])
    return Agent(**agent_doc)

@api_router.delete("/admin/agents/{agent_id}")
async def admin_delete_agent(agent_id: str, admin: User = Depends(require_admin)):
    """Admin can delete any agent"""
    result = await db.agents.delete_one({"agent_id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted"}

@api_router.get("/admin/custom-package")
async def admin_get_custom_package(admin: User = Depends(require_admin)):
    """Get custom package pricing config"""
    config = await get_custom_package_config()
    config.pop("config_type", None)
    return config

@api_router.post("/admin/custom-package")
async def admin_update_custom_package(request: Request, admin: User = Depends(require_admin)):
    """Update custom package pricing config"""
    body = await request.json()
    
    update_doc = {
        "config_type": "custom_packages",
        "per_agent_price_usd": float(body.get("per_agent_price_usd", 5.0)),
        "per_agent_price_bdt": float(body.get("per_agent_price_bdt", 535.0)),
        "commander_addon_price_usd": float(body.get("commander_addon_price_usd", 15.0)),
        "commander_addon_price_bdt": float(body.get("commander_addon_price_bdt", 1605.0)),
    }
    
    # Validate and save credit presets
    presets = body.get("credit_presets", [])
    if presets:
        validated_presets = []
        for p in presets:
            validated_presets.append({
                "id": p.get("id", f"cp_{p.get('credits', 0)}"),
                "credits": int(p.get("credits", 0)),
                "price_usd": float(p.get("price_usd", 0)),
                "price_bdt": float(p.get("price_bdt", 0)),
            })
        update_doc["credit_presets"] = validated_presets
    
    await db.platform_config.update_one(
        {"config_type": "custom_packages"},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "Custom package config updated", "config": update_doc}

@api_router.get("/admin/credit-packages")
async def admin_get_credit_packages(admin: User = Depends(require_admin)):
    """Get extra credit packages config"""
    config = await db.platform_config.find_one({"config_type": "credit_packages"}, {"_id": 0})
    if config and config.get("packages"):
        return {"packages": config["packages"]}
    return {"packages": DEFAULT_CREDIT_PACKAGES}

@api_router.post("/admin/credit-packages")
async def admin_update_credit_packages(request: Request, admin: User = Depends(require_admin)):
    """Update extra credit packages"""
    body = await request.json()
    packages = []
    for p in body.get("packages", []):
        packages.append({
            "id": p.get("id", f"credits_{p.get('credits', 0)}"),
            "credits": int(p.get("credits", 0)),
            "price_usd": float(p.get("price_usd", 0)),
            "price_bdt": float(p.get("price_bdt", 0)),
            "name": p.get("name", f"{p.get('credits', 0)} Credits"),
        })
    await db.platform_config.update_one(
        {"config_type": "credit_packages"},
        {"$set": {"config_type": "credit_packages", "packages": packages}},
        upsert=True
    )
    return {"message": "Credit packages updated", "packages": packages}

@api_router.get("/admin/transactions")
async def admin_get_transactions(admin: User = Depends(require_admin)):
    """Get all payment transactions"""
    transactions = await db.payment_transactions.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return transactions

@api_router.patch("/admin/users/{user_id}/subscription")
async def admin_update_subscription(user_id: str, plan_id: str, credits: int = 0, admin: User = Depends(require_admin)):
    """Admin can update user subscription"""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {
            "plan_id": plan_id,
            "credits": credits if credits > 0 else plan["credits"],
            "credits_used": 0,
            "status": "active",
            "renewed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": f"User updated to {plan['name']} plan"}


# ============== STARTUP ==============

# ============== USAGE LOG BACKFILL ==============

MODEL_COSTS_MAP = {
    "gpt-5.2": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "provider": "openai"},
    "o3": {"input": 10.00, "output": 40.00, "provider": "openai"},
    "o3-mini": {"input": 1.10, "output": 4.40, "provider": "openai"},
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    "claude-haiku-4-5-20250929": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    "gemini-3-flash-preview": {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-3-pro-preview": {"input": 1.25, "output": 5.00, "provider": "gemini"},
}

async def backfill_usage_logs():
    """Backfill usage logs from historical chat messages (runs once)"""
    already_done = await db.platform_config.find_one({"config_type": "usage_backfill_done"})
    if already_done:
        return
    
    logger.info("Backfilling usage logs from historical chats...")
    count = 0
    
    chats = await db.chats.find({}, {"_id": 0}).to_list(5000)
    
    for chat in chats:
        agent_id = chat.get("agent_id", "")
        user_id = chat.get("user_id", "")
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        
        default_model = agent.get("model_name", "gpt-5.2") if agent else "gpt-5.2"
        default_provider = agent.get("model_provider", "openai") if agent else "openai"
        
        messages = chat.get("messages", [])
        # Pair user messages with assistant responses
        for i, msg in enumerate(messages):
            if msg.get("role") != "assistant":
                continue
            
            content = msg.get("content", "")
            model_used = msg.get("model_used", default_model)
            
            # Find the preceding user message for input estimation
            user_content = ""
            if i > 0 and messages[i-1].get("role") == "user":
                user_content = messages[i-1].get("content", "")
            
            # Estimate tokens
            system_prompt = agent.get("system_prompt", "") if agent else ""
            input_text = user_content + system_prompt
            est_input_tokens = max(len(input_text) // 4, 50)
            est_output_tokens = max(len(content) // 4, 50)
            
            # Clean model name for cost lookup
            model_clean = model_used.split("/")[-1] if "/" in model_used else model_used
            costs = MODEL_COSTS_MAP.get(model_clean, {"input": 2.50, "output": 10.00, "provider": default_provider})
            est_cost = (est_input_tokens * costs["input"] / 1_000_000) + (est_output_tokens * costs["output"] / 1_000_000)
            
            created_at = msg.get("timestamp") or chat.get("created_at") or datetime.now(timezone.utc).isoformat()
            
            usage_log = {
                "log_id": f"backfill_{uuid.uuid4().hex[:10]}",
                "user_id": user_id,
                "chat_id": chat.get("chat_id", ""),
                "agent_id": agent_id,
                "model": model_used,
                "provider": costs.get("provider", default_provider),
                "input_tokens": est_input_tokens,
                "output_tokens": est_output_tokens,
                "estimated_cost_usd": round(est_cost, 6),
                "key_source": "emergent",
                "created_at": created_at,
                "backfilled": True
            }
            await db.usage_logs.insert_one(usage_log)
            count += 1
    
    await db.platform_config.insert_one({"config_type": "usage_backfill_done", "count": count, "done_at": datetime.now(timezone.utc).isoformat()})
    logger.info(f"Backfilled {count} usage log entries from historical chats")

@api_router.post("/admin/backfill-usage")
async def admin_backfill_usage(admin: User = Depends(require_admin)):
    """Force re-backfill usage logs from all chat history"""
    await db.usage_logs.delete_many({"backfilled": True})
    await db.platform_config.delete_one({"config_type": "usage_backfill_done"})
    await backfill_usage_logs()
    count = await db.usage_logs.count_documents({"backfilled": True})
    return {"message": f"Backfilled {count} usage log entries from chat history"}

# ============== ADMIN INTEGRATION MANAGEMENT ==============

@api_router.get("/admin/integrations")
async def admin_get_integrations(admin: User = Depends(require_admin)):
    """Get all integration configs and their status"""
    config = await get_integration_keys()
    result = {}
    for svc_id, svc_def in INTEGRATION_SERVICES.items():
        svc_config = config.get(svc_id, {})
        has_key = any(svc_config.get(f) for f in svc_def.get("key_fields", []))
        result[svc_id] = {
            "name": svc_def["name"],
            "description": svc_def["description"],
            "key_fields": svc_def["key_fields"],
            "configured": has_key,
            "keys_set": {f: bool(svc_config.get(f)) for f in svc_def["key_fields"]}
        }
    return result

@api_router.post("/admin/integrations")
async def admin_update_integrations(request: Request, admin: User = Depends(require_admin)):
    """Update integration keys"""
    data = await request.json()
    config = await get_integration_keys()
    
    for svc_id, svc_data in data.items():
        if svc_id in INTEGRATION_SERVICES and isinstance(svc_data, dict):
            if svc_id not in config:
                config[svc_id] = {}
            for field in INTEGRATION_SERVICES[svc_id]["key_fields"]:
                if field in svc_data and svc_data[field]:
                    config[svc_id][field] = svc_data[field]
    
    config["config_type"] = "integration_keys"
    await db.platform_config.update_one(
        {"config_type": "integration_keys"},
        {"$set": config},
        upsert=True
    )
    return {"message": "Integration keys updated successfully"}

@api_router.get("/admin/integrations/test/{service_id}")
async def admin_test_integration(service_id: str, admin: User = Depends(require_admin)):
    """Test if an integration is working"""
    if service_id not in INTEGRATION_SERVICES:
        raise HTTPException(404, "Unknown service")
    
    config = await get_integration_keys()
    svc_config = config.get(service_id, {})
    svc_def = INTEGRATION_SERVICES[service_id]
    has_key = any(svc_config.get(f) for f in svc_def.get("key_fields", []))
    
    if not has_key:
        return {"status": "not_configured", "message": "No API key configured"}
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if service_id == "slack":
                resp = await client.post(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {svc_config.get('bot_token', '')}"}
                )
                data = resp.json()
                return {"status": "active" if data.get("ok") else "error", "message": data.get("team", data.get("error", ""))}
            elif service_id == "github":
                resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {svc_config.get('personal_access_token', '')}"}
                )
                if resp.status_code == 200:
                    return {"status": "active", "message": f"Authenticated as {resp.json().get('login', '')}"}
                return {"status": "error", "message": f"Auth failed: {resp.status_code}"}
            elif service_id == "sendgrid":
                resp = await client.get(
                    "https://api.sendgrid.com/v3/user/profile",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "resend":
                resp = await client.get(
                    "https://api.resend.com/api-keys",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "giphy":
                resp = await client.get(
                    "https://api.giphy.com/v1/gifs/trending",
                    params={"api_key": svc_config.get("api_key", ""), "limit": 1}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "airtable":
                resp = await client.get(
                    "https://api.airtable.com/v0/meta/whoami",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "calendly":
                resp = await client.get(
                    "https://api.calendly.com/users/me",
                    headers={"Authorization": f"Bearer {svc_config.get('api_key', '')}"}
                )
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            elif service_id == "twilio":
                sid = svc_config.get("account_sid", "")
                auth = svc_config.get("auth_token", "")
                resp = await client.get(f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json", auth=(sid, auth))
                return {"status": "active" if resp.status_code == 200 else "error", "message": "Connected" if resp.status_code == 200 else f"Error: {resp.status_code}"}
            else:
                return {"status": "unknown", "message": "Test not available for this service"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}

# ============== CUSTOMER ANALYTICS DASHBOARD ==============

@api_router.get("/admin/analytics")
async def admin_analytics(admin: User = Depends(require_admin)):
    """Comprehensive analytics dashboard data for admin."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    seven_days_ago = (now - timedelta(days=7)).isoformat()

    # --- KPIs ---
    total_users = await db.users.count_documents({})
    active_7d = await db.users.count_documents({"last_active": {"$gte": seven_days_ago}})
    active_30d = await db.users.count_documents({"last_active": {"$gte": thirty_days_ago}})
    # Fallback: if last_active isn't tracked, count users who created chats recently
    if active_7d == 0 and total_users > 0:
        recent_chatters_7d = await db.chats.distinct("user_id", {"created_at": {"$gte": seven_days_ago}})
        active_7d = len(recent_chatters_7d)
        recent_chatters_30d = await db.chats.distinct("user_id", {"created_at": {"$gte": thirty_days_ago}})
        active_30d = len(recent_chatters_30d)

    total_chats = await db.chats.count_documents({})

    # Revenue
    rev_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    rev_result = await db.payment_transactions.aggregate(rev_pipeline).to_list(1)
    total_revenue = rev_result[0]["total"] if rev_result else 0

    # MRR: sum of active paid subscription plan prices
    mrr = 0
    subs = await db.subscriptions.find({"status": "active"}, {"_id": 0, "plan_id": 1}).to_list(1000)
    for s in subs:
        plan = SUBSCRIPTION_PLANS.get(s.get("plan_id", "free"), {})
        mrr += plan.get("price_usd", 0)

    # --- Daily Signups (last 30 days) ---
    all_users = await db.users.find({}, {"_id": 0, "created_at": 1}).to_list(5000)
    daily_signups = {}
    for u in all_users:
        ca = u.get("created_at", "")
        if ca:
            day = ca[:10]
            daily_signups[day] = daily_signups.get(day, 0) + 1

    # Build last 30 days array
    signup_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        signup_series.append({"date": d, "signups": daily_signups.get(d, 0)})

    # --- Daily Messages (last 30 days) ---
    all_chats = await db.chats.find({}, {"_id": 0, "messages": 1}).to_list(5000)
    daily_messages = {}
    for chat in all_chats:
        for msg in chat.get("messages", []):
            ca = msg.get("created_at", "")
            if ca:
                day = ca[:10]
                daily_messages[day] = daily_messages.get(day, 0) + 1

    message_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        message_series.append({"date": d, "messages": daily_messages.get(d, 0)})

    # --- Daily Revenue (last 30 days) ---
    paid_txns = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "amount": 1, "created_at": 1}
    ).to_list(5000)
    daily_revenue = {}
    for tx in paid_txns:
        ca = tx.get("created_at", "")
        if ca:
            day = ca[:10]
            daily_revenue[day] = daily_revenue.get(day, 0) + tx.get("amount", 0)

    revenue_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        revenue_series.append({"date": d, "revenue": round(daily_revenue.get(d, 0), 2)})

    # --- Agent Usage ---
    agent_usage_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    agent_usage_raw = await db.chats.aggregate(agent_usage_pipeline).to_list(50)
    # Enrich with agent names
    agent_map = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1}).to_list(200)
    for a in all_agents:
        agent_map[a["agent_id"]] = a
    agent_usage = []
    for item in agent_usage_raw:
        aid = item["_id"]
        agent_info = agent_map.get(aid, {})
        agent_usage.append({
            "agent_id": aid,
            "name": agent_info.get("name", aid or "Unknown"),
            "messages": item["count"]
        })

    # --- Subscription Distribution ---
    plan_pipeline = [
        {"$group": {"_id": "$plan_id", "count": {"$sum": 1}}}
    ]
    plan_dist = await db.subscriptions.aggregate(plan_pipeline).to_list(10)
    plan_distribution = [{"plan": item["_id"] or "free", "count": item["count"]} for item in plan_dist]

    # --- Token Usage (last 30 days from usage_logs) ---
    token_pipeline = [
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {"$substr": ["$created_at", 0, 10]},
            "input_tokens": {"$sum": "$input_tokens"},
            "output_tokens": {"$sum": "$output_tokens"},
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    token_raw = await db.usage_logs.aggregate(token_pipeline).to_list(31)
    token_map = {item["_id"]: item for item in token_raw}
    token_series = []
    for i in range(30, -1, -1):
        d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = token_map.get(d, {})
        token_series.append({
            "date": d,
            "input_tokens": entry.get("input_tokens", 0),
            "output_tokens": entry.get("output_tokens", 0),
            "cost": round(entry.get("cost", 0), 4),
            "calls": entry.get("calls", 0)
        })

    # --- Top Users by Messages ---
    top_users_pipeline = [
        {"$project": {"user_id": 1, "msg_count": {"$size": "$messages"}}},
        {"$group": {"_id": "$user_id", "total_messages": {"$sum": "$msg_count"}}},
        {"$sort": {"total_messages": -1}},
        {"$limit": 10}
    ]
    top_users_raw = await db.chats.aggregate(top_users_pipeline).to_list(10)
    user_ids = [u["_id"] for u in top_users_raw]
    user_map = {}
    if user_ids:
        user_docs = await db.users.find({"user_id": {"$in": user_ids}}, {"_id": 0, "user_id": 1, "name": 1, "email": 1}).to_list(10)
        for ud in user_docs:
            user_map[ud["user_id"]] = ud
    top_users = []
    for u in top_users_raw:
        info = user_map.get(u["_id"], {})
        top_users.append({
            "user_id": u["_id"],
            "name": info.get("name", "Unknown"),
            "email": info.get("email", ""),
            "total_messages": u["total_messages"]
        })

    # --- Cost by Model ---
    model_cost_pipeline = [
        {"$group": {
            "_id": "$model",
            "cost": {"$sum": "$estimated_cost_usd"},
            "calls": {"$sum": 1}
        }},
        {"$sort": {"cost": -1}},
        {"$limit": 10}
    ]
    model_costs = await db.usage_logs.aggregate(model_cost_pipeline).to_list(10)
    model_cost_data = [{"model": m["_id"] or "unknown", "cost": round(m["cost"], 4), "calls": m["calls"]} for m in model_costs]

    return {
        "kpis": {
            "total_users": total_users,
            "active_7d": active_7d,
            "active_30d": active_30d,
            "total_chats": total_chats,
            "total_revenue": round(total_revenue, 2),
            "mrr": round(mrr, 2),
        },
        "daily_signups": signup_series,
        "daily_messages": message_series,
        "daily_revenue": revenue_series,
        "agent_usage": agent_usage,
        "plan_distribution": plan_distribution,
        "token_usage": token_series,
        "top_users": top_users,
        "model_costs": model_cost_data,
    }


# ============== SMTP CONFIGURATION ==============

@api_router.get("/admin/smtp-config")
async def admin_get_smtp_config(admin: User = Depends(require_admin)):
    """Get current SMTP configuration status (masked)."""
    return {
        "email": SMTP_EMAIL or "",
        "has_password": bool(SMTP_PASSWORD),
        "configured": bool(SMTP_EMAIL and SMTP_PASSWORD)
    }

@api_router.post("/admin/smtp-config")
async def admin_update_smtp_config(request: Request, admin: User = Depends(require_admin)):
    """Update SMTP configuration. Saves to .env and reloads in memory."""
    global SMTP_EMAIL, SMTP_PASSWORD
    data = await request.json()
    new_email = data.get("email", "").strip()
    new_password = data.get("password", "").strip()

    if not new_email:
        raise HTTPException(400, "Email is required")

    # Update globals
    SMTP_EMAIL = new_email
    if new_password:
        SMTP_PASSWORD = new_password

    # Persist to .env file
    env_path = ROOT_DIR / '.env'
    lines = env_path.read_text().splitlines()
    new_lines = []
    email_set = False
    password_set = False
    for line in lines:
        if line.startswith("SMTP_EMAIL="):
            new_lines.append(f"SMTP_EMAIL={new_email}")
            email_set = True
        elif line.startswith("SMTP_PASSWORD=") and new_password:
            new_lines.append(f"SMTP_PASSWORD={new_password}")
            password_set = True
        else:
            new_lines.append(line)
    if not email_set:
        new_lines.append(f"SMTP_EMAIL={new_email}")
    if new_password and not password_set:
        new_lines.append(f"SMTP_PASSWORD={new_password}")
    env_path.write_text("\n".join(new_lines) + "\n")

    return {"success": True, "configured": bool(SMTP_EMAIL and SMTP_PASSWORD)}

@api_router.post("/admin/smtp-test")
async def admin_test_smtp(request: Request, admin: User = Depends(require_admin)):
    """Send a test email to verify SMTP configuration."""
    data = await request.json()
    test_to = data.get("to_email", admin.email)

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise HTTPException(400, "SMTP not configured. Save credentials first.")

    html = """
    <div style="font-family:Arial;padding:20px;background:#111;color:#fff;border-radius:12px;">
        <h2 style="color:#ef4444;">MAARS Command - SMTP Test</h2>
        <p>This is a test email from your MAARS Command platform.</p>
        <p>If you're seeing this, your Gmail SMTP is configured correctly!</p>
        <hr style="border-color:#333;"/>
        <p style="color:#666;font-size:12px;">MAARS Global Corporation</p>
    </div>
    """
    success = await send_email_notification(test_to, "MAARS Command - SMTP Test", html)
    if success:
        return {"success": True, "message": f"Test email sent to {test_to}"}
    else:
        raise HTTPException(500, "Failed to send test email. Check your credentials.")


# ============== MESSAGE FEEDBACK (THUMBS UP/DOWN) ==============

@api_router.post("/chats/{chat_id}/messages/{message_id}/feedback")
async def submit_message_feedback(chat_id: str, message_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Submit thumbs up/down feedback on an assistant message."""
    data = await request.json()
    feedback = data.get("feedback")  # "up", "down", or null (remove)
    if feedback not in ("up", "down", None):
        raise HTTPException(400, "feedback must be 'up', 'down', or null")

    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(404, "Chat not found")

    # Find the message and update feedback
    messages = chat.get("messages", [])
    found = False
    for msg in messages:
        if msg.get("message_id") == message_id and msg.get("role") == "assistant":
            msg["feedback"] = feedback
            msg["feedback_at"] = datetime.now(timezone.utc).isoformat()
            msg["feedback_by"] = current_user.user_id
            found = True
            break

    if not found:
        raise HTTPException(404, "Message not found")

    await db.chats.update_one({"chat_id": chat_id}, {"$set": {"messages": messages}})
    return {"success": True, "feedback": feedback}


@api_router.get("/admin/agent-performance")
async def admin_agent_performance(admin: User = Depends(require_admin)):
    """Get performance metrics for all agents based on user feedback."""
    # Aggregate feedback from all chats
    pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant", "messages.feedback": {"$in": ["up", "down"]}}},
        {"$group": {
            "_id": "$agent_id",
            "total_feedback": {"$sum": 1},
            "thumbs_up": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "up"]}, 1, 0]}},
            "thumbs_down": {"$sum": {"$cond": [{"$eq": ["$messages.feedback", "down"]}, 1, 0]}},
        }},
        {"$sort": {"total_feedback": -1}}
    ]
    feedback_data = await db.chats.aggregate(pipeline).to_list(50)

    # Get total messages per agent
    msg_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "total_messages": {"$sum": 1}}},
    ]
    msg_data = await db.chats.aggregate(msg_pipeline).to_list(50)
    msg_map = {m["_id"]: m["total_messages"] for m in msg_data}

    # Get agent names
    agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1}).to_list(200)
    agent_map = {a["agent_id"]: a for a in agents}
    feedback_map = {f["_id"]: f for f in feedback_data}

    performance = []
    for a in agents:
        aid = a["agent_id"]
        f = feedback_map.get(aid, {})
        total_msgs = msg_map.get(aid, 0)
        up = f.get("thumbs_up", 0)
        down = f.get("thumbs_down", 0)
        total_fb = up + down
        satisfaction = round((up / total_fb * 100), 1) if total_fb > 0 else None
        performance.append({
            "agent_id": aid,
            "name": a.get("name", aid),
            "avatar": a.get("avatar", ""),
            "role": a.get("role", ""),
            "total_messages": total_msgs,
            "thumbs_up": up,
            "thumbs_down": down,
            "total_feedback": total_fb,
            "satisfaction_rate": satisfaction,
            "feedback_rate": round((total_fb / total_msgs * 100), 1) if total_msgs > 0 else 0,
        })

    performance.sort(key=lambda x: (x["satisfaction_rate"] or 0, x["total_messages"]), reverse=True)
    return performance


# ============== REAL-TIME ACTIVITY FEED ==============

@api_router.get("/admin/activity-feed")
async def admin_activity_feed(limit: int = 30, admin: User = Depends(require_admin)):
    """Get recent platform activity events for the live feed."""
    events = []

    # Recent signups
    recent_users = await db.users.find(
        {}, {"_id": 0, "user_id": 1, "name": 1, "email": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    for u in recent_users:
        events.append({
            "type": "signup",
            "icon": "user-plus",
            "title": f"New user signed up",
            "detail": u.get("name") or u.get("email", "Unknown"),
            "timestamp": u.get("created_at", ""),
        })

    # Recent payments
    recent_payments = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "email": 1, "amount": 1, "currency": 1, "type": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    for p in recent_payments:
        curr = "$" if p.get("currency", "usd") == "usd" else "৳"
        events.append({
            "type": "payment",
            "icon": "dollar-sign",
            "title": f"Payment received: {curr}{p.get('amount', 0):.2f}",
            "detail": f"{p.get('email', 'Unknown')} — {p.get('type', 'subscription')}",
            "timestamp": p.get("created_at", ""),
        })

    # Recent chats created
    recent_chats = await db.chats.find(
        {}, {"_id": 0, "chat_id": 1, "user_id": 1, "agent_id": 1, "title": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(limit)
    agent_map = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1}).to_list(200)
    for a in all_agents:
        agent_map[a["agent_id"]] = a.get("name", a["agent_id"])
    user_map = {}
    user_ids = list(set(c.get("user_id") for c in recent_chats if c.get("user_id")))
    if user_ids:
        user_docs = await db.users.find({"user_id": {"$in": user_ids}}, {"_id": 0, "user_id": 1, "name": 1}).to_list(500)
        for ud in user_docs:
            user_map[ud["user_id"]] = ud.get("name", "Unknown")
    for c in recent_chats:
        agent_name = agent_map.get(c.get("agent_id"), "Unknown Agent")
        user_name = user_map.get(c.get("user_id"), "Unknown User")
        events.append({
            "type": "chat",
            "icon": "message-square",
            "title": f"Chat started with {agent_name}",
            "detail": user_name,
            "timestamp": c.get("created_at", ""),
        })

    # Recent team creations
    recent_teams = await db.teams.find(
        {}, {"_id": 0, "name": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(10)
    for t in recent_teams:
        events.append({
            "type": "team",
            "icon": "users",
            "title": f"Team created: {t.get('name', 'Unnamed')}",
            "detail": "",
            "timestamp": t.get("created_at", ""),
        })

    # Sort all events by timestamp descending
    events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    return events[:limit]


# ============== BRANDING & WHITE-LABEL ==============

@api_router.get("/admin/branding")
async def get_branding(admin: User = Depends(require_admin)):
    """Get current branding configuration."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    defaults = {
        "config_type": "branding",
        "platform_name": "MAARS Command",
        "tagline": "AI-Powered Team Platform",
        "logo_url": "",
        "favicon_url": "",
        "primary_color": "#ef4444",
        "accent_color": "#f97316",
        "custom_domain": "",
        "custom_domain_status": "not_configured",
        "footer_text": "MAARS Global Corporation",
        "support_email": "",
    }
    if config:
        defaults.update({k: v for k, v in config.items() if v is not None})
    return defaults

@api_router.post("/admin/branding")
async def update_branding(request: Request, admin: User = Depends(require_admin)):
    """Update branding and white-label settings."""
    data = await request.json()
    allowed_fields = {
        "platform_name", "tagline", "logo_url", "favicon_url",
        "primary_color", "accent_color", "custom_domain",
        "footer_text", "support_email"
    }
    update = {k: v for k, v in data.items() if k in allowed_fields}
    if not update:
        raise HTTPException(400, "No valid fields to update")

    # If custom domain changed, set status
    if "custom_domain" in update:
        domain = update["custom_domain"].strip()
        update["custom_domain"] = domain
        update["custom_domain_status"] = "pending_verification" if domain else "not_configured"
        update["custom_domain_updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.platform_config.update_one(
        {"config_type": "branding"},
        {"$set": {**update, "config_type": "branding", "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return await get_branding(admin)

@api_router.post("/admin/branding/upload-logo")
async def upload_branding_logo(file: UploadFile = File(...), admin: User = Depends(require_admin)):
    """Upload logo or favicon for branding. Returns the file URL."""
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "Logo file too large. Max 5MB.")
    allowed_ext = {"png", "jpg", "jpeg", "svg", "webp", "ico"}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_ext:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed_ext)}")
    file_id = uuid.uuid4().hex[:10]
    saved_filename = f"brand_{file_id}.{ext}"
    saved_path = UPLOAD_DIR / saved_filename
    with open(saved_path, 'wb') as f:
        f.write(contents)
    return {"url": f"/api/files/{saved_filename}", "filename": saved_filename}

@api_router.post("/admin/branding/verify-domain")
async def verify_custom_domain(request: Request, admin: User = Depends(require_admin)):
    """Check DNS status of the configured custom domain."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    domain = config.get("custom_domain", "") if config else ""
    if not domain:
        raise HTTPException(400, "No custom domain configured")
    import socket
    status = "pending_verification"
    dns_result = None
    try:
        result = socket.getaddrinfo(domain, None)
        dns_result = result[0][4][0] if result else None
        status = "verified" if dns_result else "pending_verification"
    except socket.gaierror:
        status = "dns_not_found"
    except Exception:
        status = "verification_error"
    await db.platform_config.update_one(
        {"config_type": "branding"},
        {"$set": {"custom_domain_status": status, "custom_domain_verified_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"domain": domain, "status": status, "dns_result": dns_result}

@api_router.get("/branding/public")
async def get_public_branding():
    """Public endpoint for branding (no auth) — used by frontend to apply customization."""
    config = await db.platform_config.find_one({"config_type": "branding"}, {"_id": 0})
    defaults = {
        "platform_name": "MAARS Command",
        "tagline": "AI-Powered Team Platform",
        "logo_url": "",
        "favicon_url": "",
        "primary_color": "#ef4444",
        "accent_color": "#f97316",
        "footer_text": "MAARS Global Corporation",
    }
    if config:
        for k in defaults:
            if config.get(k):
                defaults[k] = config[k]
    return defaults


@api_router.get("/admin/analytics/export")
async def admin_analytics_export(format: str = "csv", admin: User = Depends(require_admin)):
    """Export analytics data as CSV."""
    import io
    import csv

    now = datetime.now(timezone.utc)

    # Users
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1, "email": 1, "created_at": 1}).to_list(5000)

    # Subscriptions
    subs = await db.subscriptions.find({}, {"_id": 0, "user_id": 1, "plan_id": 1, "credits": 1, "credits_used": 1, "status": 1}).to_list(5000)
    sub_map = {s["user_id"]: s for s in subs}

    # Agent usage
    agent_pipeline = [
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "assistant"}},
        {"$group": {"_id": "$agent_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    agent_usage = await db.chats.aggregate(agent_pipeline).to_list(50)
    agent_names = {}
    all_agents = await db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1}).to_list(200)
    for a in all_agents:
        agent_names[a["agent_id"]] = a.get("name", a["agent_id"])

    # Payment transactions
    txns = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "email": 1, "amount": 1, "currency": 1, "type": 1, "created_at": 1}
    ).to_list(5000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Sheet 1: Users
    writer.writerow(["=== USERS ==="])
    writer.writerow(["User ID", "Name", "Email", "Signed Up", "Plan", "Credits", "Credits Used"])
    for u in users:
        s = sub_map.get(u["user_id"], {})
        writer.writerow([u["user_id"], u.get("name", ""), u.get("email", ""), u.get("created_at", ""), s.get("plan_id", "free"), s.get("credits", 0), s.get("credits_used", 0)])

    writer.writerow([])
    writer.writerow(["=== AGENT USAGE ==="])
    writer.writerow(["Agent", "Messages"])
    for au in agent_usage:
        writer.writerow([agent_names.get(au["_id"], au["_id"]), au["count"]])

    writer.writerow([])
    writer.writerow(["=== PAYMENTS ==="])
    writer.writerow(["Email", "Amount", "Currency", "Type", "Date"])
    for t in txns:
        writer.writerow([t.get("email", ""), t.get("amount", 0), t.get("currency", "usd"), t.get("type", ""), t.get("created_at", "")])

    writer.writerow([])
    writer.writerow(["=== SUMMARY ==="])
    writer.writerow(["Total Users", len(users)])
    writer.writerow(["Total Paid Transactions", len(txns)])
    writer.writerow(["Total Revenue", sum(t.get("amount", 0) for t in txns)])
    writer.writerow(["Report Generated", now.isoformat()])

    csv_content = output.getvalue()
    output.close()

    from starlette.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=maars_analytics_{now.strftime('%Y%m%d')}.csv"}
    )


# ============== NOTIFICATION CENTER ==============

async def create_notification(user_id: str, ntype: str, title: str, message: str, link: str = None):
    """Create a notification for a user."""
    notif = {
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "type": ntype,
        "title": title,
        "message": message,
        "link": link,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notif)
    return notif["notification_id"]

@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Get user's notifications (newest first, last 50)."""
    notifs = await db.notifications.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    unread = sum(1 for n in notifs if not n.get("read"))
    return {"notifications": notifs, "unread_count": unread}

@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user.user_id},
        {"$set": {"read": True}}
    )
    return {"success": result.modified_count > 0}

@api_router.post("/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user.user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

@api_router.delete("/notifications/clear")
async def clear_notifications(current_user: User = Depends(get_current_user)):
    await db.notifications.delete_many({"user_id": current_user.user_id, "read": True})
    return {"success": True}


# ============== USER AGENT CUSTOMIZATION (Per-User Overrides) ==============

@api_router.get("/agents/{agent_id}/my-settings")
async def get_user_agent_settings(agent_id: str, current_user: User = Depends(get_current_user)):
    """Get user's personal customization for an agent."""
    override = await db.user_agent_overrides.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    if not override:
        return {"agent_id": agent_id, "has_override": False}
    override["has_override"] = True
    return override

@api_router.put("/agents/{agent_id}/my-settings")
async def update_user_agent_settings(agent_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Save user's personal agent customization (temperature, max_tokens, personality_tone, custom_instructions)."""
    data = await request.json()
    allowed = {"temperature", "max_tokens", "personality_tone", "custom_instructions"}
    update = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not update:
        raise HTTPException(400, "No valid fields to update")
    
    # Validate ranges
    if "temperature" in update:
        update["temperature"] = max(0, min(2, float(update["temperature"])))
    if "max_tokens" in update:
        update["max_tokens"] = max(256, min(16384, int(update["max_tokens"])))
    
    await db.user_agent_overrides.update_one(
        {"user_id": current_user.user_id, "agent_id": agent_id},
        {"$set": {**update, "user_id": current_user.user_id, "agent_id": agent_id, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    result = await db.user_agent_overrides.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0}
    )
    result["has_override"] = True
    return result

@api_router.delete("/agents/{agent_id}/my-settings")
async def reset_user_agent_settings(agent_id: str, current_user: User = Depends(get_current_user)):
    """Reset user's agent customization back to defaults."""
    await db.user_agent_overrides.delete_one({"user_id": current_user.user_id, "agent_id": agent_id})
    return {"success": True, "agent_id": agent_id}


@app.on_event("startup")
async def startup():
    global SUBSCRIPTION_PLANS, CUSTOM_AGENT_CREDIT_COST
    await seed_default_agents()
    await backfill_usage_logs()
    
    # Load admin-configured pricing from DB (overrides hardcoded defaults)
    saved_pricing = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
    if saved_pricing and saved_pricing.get("plans"):
        SUBSCRIPTION_PLANS.update(saved_pricing["plans"])
        logger.info("Loaded pricing from database")
    if saved_pricing and "custom_agent_credit_cost" in saved_pricing:
        CUSTOM_AGENT_CREDIT_COST = saved_pricing["custom_agent_credit_cost"]
    
    logger.info("MAARS Global AI Team Backend started")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ============== ADMIN AGENT MANAGEMENT ==============

@api_router.put("/admin/agents/{agent_id}/settings")
async def admin_update_agent_settings(agent_id: str, body: dict = Body(...), admin: User = Depends(require_admin)):
    """Update agent settings including generation permissions"""
    allowed_fields = {"can_generate_image", "can_generate_video", "can_generate_pdf", "can_generate_files", "system_prompt", "capabilities", "is_active"}
    update = {k: v for k, v in body.items() if k in allowed_fields}
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    result = await db.agents.update_one({"agent_id": agent_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"success": True, "updated": list(update.keys())}

@api_router.put("/admin/agents/{agent_id}/brain")
async def admin_update_agent_brain(agent_id: str, body: dict = Body(...), admin: User = Depends(require_admin)):
    """Update agent brain configuration — personality, tone, knowledge, rules."""
    agent = await db.agents.find_one({"agent_id": agent_id})
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    allowed = {"name", "role", "description", "system_prompt", "personality_tone", "expertise_areas", "dos", "donts", "example_responses", "knowledge_base", "model_provider", "model_name", "temperature", "max_tokens"}
    update = {k: v for k, v in body.items() if k in allowed}
    if not update:
        raise HTTPException(400, "No valid fields")
    
    # Auto-rebuild system prompt from brain fields if personality fields are provided
    brain_fields = {"personality_tone", "expertise_areas", "dos", "donts", "knowledge_base"}
    if brain_fields.intersection(update.keys()):
        # Save brain fields separately and also rebuild system prompt
        tone = update.get("personality_tone", agent.get("personality_tone", ""))
        expertise = update.get("expertise_areas", agent.get("expertise_areas", ""))
        dos = update.get("dos", agent.get("dos", ""))
        donts = update.get("donts", agent.get("donts", ""))
        knowledge = update.get("knowledge_base", agent.get("knowledge_base", ""))
        name = update.get("name", agent.get("name"))
        role = update.get("role", agent.get("role"))
        
        brain_prompt_parts = [agent.get("system_prompt", "").split("\n\n--- BRAIN CONFIG ---")[0].strip()]
        brain_config = []
        if tone: brain_config.append(f"Personality & Tone: {tone}")
        if expertise: brain_config.append(f"Expertise Areas: {expertise}")
        if dos: brain_config.append(f"Always do: {dos}")
        if donts: brain_config.append(f"Never do: {donts}")
        if knowledge: brain_config.append(f"Knowledge Base: {knowledge}")
        
        if brain_config:
            brain_prompt_parts.append("\n\n--- BRAIN CONFIG ---\n" + "\n".join(brain_config))
        
        update["system_prompt"] = "\n".join(brain_prompt_parts)
    
    await db.agents.update_one({"agent_id": agent_id}, {"$set": update})
    
    updated_agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    return {"success": True, "agent": updated_agent}

@api_router.get("/admin/agents/{agent_id}")
async def admin_get_agent_detail(agent_id: str, admin: User = Depends(require_admin)):
    """Get full agent details for brain editor."""
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
