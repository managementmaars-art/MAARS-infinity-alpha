from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import httpx

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

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    agent_id: str
    name: str
    description: str
    avatar: str
    role: str
    system_prompt: str
    model_provider: str = "openai"
    model_name: str = "gpt-5.2"
    is_custom: bool = False
    creator_id: Optional[str] = None
    capabilities: List[str] = []
    created_at: datetime

class AgentCreate(BaseModel):
    name: str
    description: str
    avatar: Optional[str] = None
    role: str
    system_prompt: str
    model_provider: str = "openai"
    model_name: str = "gpt-5.2"
    capabilities: List[str] = []

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message_id: str
    chat_id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime

class Chat(BaseModel):
    model_config = ConfigDict(extra="ignore")
    chat_id: str
    user_id: str
    agent_id: str
    title: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime

class ChatCreate(BaseModel):
    agent_id: str
    title: Optional[str] = None

class MessageCreate(BaseModel):
    content: str

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task_id: str
    user_id: str
    title: str
    description: str
    status: str = "pending"  # pending, in_progress, completed
    priority: str = "medium"  # low, medium, high
    assigned_agents: List[str] = []
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    assigned_agents: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_agents: Optional[List[str]] = None

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
                    return User(**user)
    
    # Try JWT token from header
    if credentials:
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
            if user:
                if isinstance(user.get('created_at'), str):
                    user['created_at'] = datetime.fromisoformat(user['created_at'])
                return User(**user)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            pass
    
    raise HTTPException(status_code=401, detail="Not authenticated")

# ============== DEFAULT AGENTS ==============

DEFAULT_AGENTS = [
    {
        "agent_id": "agent_marketing",
        "name": "Marketing Maven",
        "description": "Expert in digital marketing, content strategy, SEO, and brand development. Creates compelling campaigns and analyzes market trends.",
        "avatar": "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "Marketing Specialist",
        "system_prompt": "You are Marketing Maven, an expert AI marketing specialist. You excel at creating compelling marketing strategies, writing persuasive copy, analyzing market trends, and optimizing campaigns for maximum ROI. Help users with content creation, SEO optimization, social media strategy, email marketing, and brand development. Be creative, data-driven, and always focus on measurable results.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Content Strategy", "SEO", "Social Media", "Email Marketing", "Brand Development"]
    },
    {
        "agent_id": "agent_sales",
        "name": "Sales Strategist",
        "description": "Master of sales techniques, lead generation, and customer relationship management. Helps close deals and build lasting client relationships.",
        "avatar": "https://images.pexels.com/photos/8294598/pexels-photo-8294598.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "role": "Sales Expert",
        "system_prompt": "You are Sales Strategist, an expert AI sales professional. You specialize in lead generation, sales funnel optimization, objection handling, and closing techniques. Help users with prospecting strategies, pitch development, CRM optimization, and building long-term customer relationships. Be persuasive but ethical, always focusing on providing value to potential customers.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Lead Generation", "Sales Scripts", "CRM", "Negotiation", "Client Relations"]
    },
    {
        "agent_id": "agent_developer",
        "name": "Code Architect",
        "description": "Full-stack development expert proficient in multiple languages and frameworks. Helps with coding, debugging, and system design.",
        "avatar": "https://images.unsplash.com/photo-1760931969401-9bd6ee902798?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "Senior Developer",
        "system_prompt": "You are Code Architect, an expert AI software developer. You are proficient in multiple programming languages (Python, JavaScript, TypeScript, Java, Go, Rust) and frameworks (React, Node.js, FastAPI, Django). Help users with code writing, debugging, code reviews, system architecture, database design, and DevOps practices. Write clean, efficient, and well-documented code.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Full-Stack Development", "System Design", "Code Review", "DevOps", "Database Design"]
    },
    {
        "agent_id": "agent_analyst",
        "name": "Data Analyst",
        "description": "Expert in data analysis, visualization, and business intelligence. Transforms raw data into actionable insights.",
        "avatar": "https://images.unsplash.com/photo-1535378917042-10a22c95931a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
        "role": "Data Scientist",
        "system_prompt": "You are Data Analyst, an expert AI data scientist. You specialize in statistical analysis, data visualization, predictive modeling, and business intelligence. Help users with data cleaning, exploratory analysis, creating dashboards, and deriving actionable insights from complex datasets. Use clear explanations and recommend appropriate analytical approaches.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Data Analysis", "Visualization", "Predictive Modeling", "SQL", "Business Intelligence"]
    },
    {
        "agent_id": "agent_writer",
        "name": "Content Creator",
        "description": "Creative writer skilled in various content formats from blog posts to technical documentation and creative storytelling.",
        "avatar": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Content Writer",
        "system_prompt": "You are Content Creator, an expert AI writer with mastery in various content formats. You excel at blog posts, technical documentation, creative storytelling, copywriting, and editing. Help users craft compelling narratives, improve their writing, and create content that engages and converts. Adapt your style to match the user's brand voice and target audience.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Blog Writing", "Technical Docs", "Copywriting", "Editing", "Storytelling"]
    },
    {
        "agent_id": "agent_assistant",
        "name": "Executive Assistant",
        "description": "Your personal productivity expert handling scheduling, task management, email drafting, and administrative support.",
        "avatar": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8YWklMjBhc3Npc3RhbnR8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Personal Assistant",
        "system_prompt": "You are Executive Assistant, an expert AI personal assistant. You specialize in productivity optimization, task management, email communication, meeting preparation, and administrative support. Help users organize their work, draft professional communications, prepare meeting agendas, and manage their time effectively. Be proactive, organized, and detail-oriented.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Task Management", "Email Drafting", "Scheduling", "Meeting Prep", "Organization"]
    }
]

async def seed_default_agents():
    for agent_data in DEFAULT_AGENTS:
        existing = await db.agents.find_one({"agent_id": agent_data["agent_id"]})
        if not existing:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.agents.insert_one(agent_data)
    logger.info("Default agents seeded")

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
    
    token = create_jwt_token(user_id, user_data.email)
    return {"token": token, "user": {"user_id": user_id, "email": user_data.email, "name": user_data.name}}

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user or not verify_password(user_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["user_id"], user["email"])
    return {"token": token, "user": {"user_id": user["user_id"], "email": user["email"], "name": user["name"]}}

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
    
    return {"user_id": user_id, "email": user["email"], "name": user["name"], "picture": user.get("picture")}

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}

# ============== AGENT ENDPOINTS ==============

@api_router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user)):
    # Get default agents and user's custom agents
    agents = await db.agents.find(
        {"$or": [{"is_custom": False}, {"creator_id": current_user.user_id}]},
        {"_id": 0}
    ).to_list(100)
    
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    
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
        "is_custom": True,
        "creator_id": current_user.user_id,
        "capabilities": agent_data.capabilities,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.agents.insert_one(agent_doc)
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

@api_router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: str, message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    agent = await db.agents.find_one({"agent_id": chat["agent_id"]}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create user message
    now = datetime.now(timezone.utc)
    user_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "user",
        "content": message_data.content,
        "created_at": now.isoformat()
    }
    
    # Get AI response
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        llm_chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=chat_id,
            system_message=agent["system_prompt"]
        ).with_model(agent["model_provider"], agent["model_name"])
        
        # Build conversation history for context
        messages_for_context = chat.get("messages", [])[-10:]  # Last 10 messages
        
        user_message = UserMessage(text=message_data.content)
        response_text = await llm_chat.send_message(user_message)
        
    except Exception as e:
        logger.error(f"LLM error: {e}")
        response_text = f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    # Create assistant message
    assistant_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "assistant",
        "content": response_text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update chat
    await db.chats.update_one(
        {"chat_id": chat_id},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Update title if first message
    if len(chat.get("messages", [])) == 0:
        title = message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"title": title}})
    
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg
    }

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
    
    return {
        "total_chats": chats_count,
        "total_tasks": tasks_count,
        "completed_tasks": completed_tasks,
        "custom_agents": custom_agents,
        "total_messages": total_messages
    }

# ============== STARTUP ==============

@app.on_event("startup")
async def startup():
    await seed_default_agents()
    logger.info("Nexus AI Backend started")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
