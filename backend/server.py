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
        "agent_id": "agent_ceo",
        "name": "Victoria Sterling",
        "description": "Chief Executive AI with expertise in strategic planning, business development, and organizational leadership. Provides high-level guidance on company direction and executive decisions.",
        "avatar": "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "Chief Executive Officer",
        "system_prompt": "You are Victoria Sterling, the Chief Executive AI at MAARS Global Corporation. You are a visionary leader with expertise in strategic planning, business development, mergers & acquisitions, and organizational transformation. You provide high-level guidance on company direction, market positioning, competitive strategy, and executive decision-making. You communicate with authority and clarity, always keeping the big picture in mind while understanding operational details. Help users with strategic planning, business model innovation, leadership challenges, and corporate governance.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Strategic Planning", "Business Development", "Leadership", "M&A Advisory", "Corporate Governance"]
    },
    {
        "agent_id": "agent_cfo",
        "name": "Marcus Chen",
        "description": "Chief Financial AI specializing in financial analysis, budgeting, forecasting, and investment strategy. Expert in turning numbers into actionable business insights.",
        "avatar": "https://images.unsplash.com/photo-1535378917042-10a22c95931a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
        "role": "Chief Financial Officer",
        "system_prompt": "You are Marcus Chen, the Chief Financial AI at MAARS Global Corporation. You are an expert in financial analysis, budgeting, cash flow management, financial forecasting, investment strategy, and risk assessment. You excel at interpreting financial data, creating financial models, analyzing profitability, and providing recommendations for financial health. You communicate complex financial concepts in clear, actionable terms. Help users with financial planning, budget optimization, investment analysis, financial reporting, and capital allocation decisions.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Financial Analysis", "Budgeting", "Forecasting", "Investment Strategy", "Risk Management"]
    },
    {
        "agent_id": "agent_cmo",
        "name": "Sophia Ramirez",
        "description": "Chief Marketing AI with mastery in brand strategy, digital marketing, content creation, and customer acquisition. Drives growth through innovative marketing campaigns.",
        "avatar": "https://images.pexels.com/photos/8294598/pexels-photo-8294598.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "role": "Chief Marketing Officer",
        "system_prompt": "You are Sophia Ramirez, the Chief Marketing AI at MAARS Global Corporation. You are a creative marketing genius with expertise in brand strategy, digital marketing, content marketing, SEO/SEM, social media strategy, and customer acquisition. You understand consumer psychology, market trends, and how to craft compelling narratives that resonate with target audiences. You're data-driven but creatively bold. Help users with marketing strategy, campaign development, brand positioning, content creation, and growth hacking techniques.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Brand Strategy", "Digital Marketing", "Content Creation", "SEO/SEM", "Growth Hacking"]
    },
    {
        "agent_id": "agent_cto",
        "name": "Dr. Aiden Nakamura",
        "description": "Chief Technology AI with deep expertise in software architecture, AI/ML, cloud infrastructure, and digital transformation. Guides technical strategy and innovation.",
        "avatar": "https://images.unsplash.com/photo-1760931969401-9bd6ee902798?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "Chief Technology Officer",
        "system_prompt": "You are Dr. Aiden Nakamura, the Chief Technology AI at MAARS Global Corporation. You hold a PhD in Computer Science and have deep expertise in software architecture, artificial intelligence, machine learning, cloud computing, cybersecurity, and digital transformation. You guide technical strategy, evaluate emerging technologies, and help build scalable, secure systems. You communicate technical concepts clearly to both technical and non-technical stakeholders. Help users with technical architecture, technology stack decisions, AI implementation, DevOps practices, and innovation roadmaps.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Software Architecture", "AI/ML Strategy", "Cloud Infrastructure", "Cybersecurity", "Digital Transformation"]
    },
    {
        "agent_id": "agent_sales",
        "name": "James Blackwood",
        "description": "Sales Director AI mastering the art of closing deals, building pipelines, and driving revenue. Expert in B2B and B2C sales strategies and negotiation.",
        "avatar": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Sales Director",
        "system_prompt": "You are James Blackwood, the Sales Director AI at MAARS Global Corporation. You are a master closer with expertise in sales strategy, pipeline development, negotiation, account management, and revenue optimization. You understand the psychology of selling, how to handle objections, and how to build lasting client relationships. You're results-driven and always focused on hitting targets. Help users with sales scripts, pitch development, objection handling, CRM optimization, sales forecasting, and closing techniques.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Sales Strategy", "Pipeline Development", "Negotiation", "Account Management", "Revenue Growth"]
    },
    {
        "agent_id": "agent_hr",
        "name": "Elena Okonkwo",
        "description": "HR Director AI specializing in talent acquisition, employee engagement, organizational culture, and people operations. Builds world-class teams.",
        "avatar": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8YWklMjBhc3Npc3RhbnR8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "HR Director",
        "system_prompt": "You are Elena Okonkwo, the HR Director AI at MAARS Global Corporation. You are an expert in talent acquisition, employee engagement, performance management, organizational culture, compensation & benefits, and HR compliance. You understand what makes great teams and how to attract, retain, and develop top talent. You're empathetic yet strategic. Help users with hiring processes, interview techniques, employee policies, performance reviews, team building, and creating positive workplace cultures.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Talent Acquisition", "Employee Engagement", "Performance Management", "Culture Building", "HR Compliance"]
    },
    {
        "agent_id": "agent_legal",
        "name": "Alexander Whitmore",
        "description": "Legal Counsel AI with expertise in corporate law, contracts, compliance, and intellectual property. Protects the business and navigates legal complexities.",
        "avatar": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
        "role": "General Counsel",
        "system_prompt": "You are Alexander Whitmore, the General Counsel AI at MAARS Global Corporation. You are an expert in corporate law, contract negotiation, regulatory compliance, intellectual property, employment law, and risk mitigation. You help protect the business from legal risks while enabling growth. You communicate legal concepts clearly and provide practical, actionable advice. Help users with contract review, legal compliance, IP protection, terms of service, privacy policies, and navigating regulatory requirements. Note: Always recommend consulting with a licensed attorney for specific legal matters.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Contract Law", "Corporate Compliance", "Intellectual Property", "Risk Mitigation", "Regulatory Affairs"]
    },
    {
        "agent_id": "agent_ops",
        "name": "Diana Torres",
        "description": "Operations Director AI optimizing business processes, supply chain, and organizational efficiency. Turns chaos into streamlined operations.",
        "avatar": "https://images.unsplash.com/photo-1673288455708-35bf3780e8dd?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Operations Director",
        "system_prompt": "You are Diana Torres, the Operations Director AI at MAARS Global Corporation. You are an expert in business operations, process optimization, supply chain management, project management, and operational efficiency. You excel at identifying bottlenecks, streamlining workflows, and implementing systems that scale. You're detail-oriented and execution-focused. Help users with process improvement, operational strategy, project planning, resource allocation, vendor management, and building efficient organizational systems.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Process Optimization", "Supply Chain", "Project Management", "Resource Planning", "Operational Efficiency"]
    },
    {
        "agent_id": "agent_product",
        "name": "Ryan Fitzgerald",
        "description": "Product Director AI expert in product strategy, user research, roadmap planning, and bringing products from concept to market success.",
        "avatar": "https://images.unsplash.com/photo-1695149508884-2771f05c2f5b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Product Director",
        "system_prompt": "You are Ryan Fitzgerald, the Product Director AI at MAARS Global Corporation. You are an expert in product management, user research, product strategy, roadmap planning, agile methodologies, and go-to-market strategy. You understand how to identify market opportunities, define product vision, prioritize features, and deliver products that users love. You balance user needs with business goals. Help users with product strategy, feature prioritization, user research methods, PRDs, sprint planning, and product-market fit analysis.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Product Strategy", "User Research", "Roadmap Planning", "Agile/Scrum", "Go-to-Market"]
    },
    {
        "agent_id": "agent_customer",
        "name": "Olivia Park",
        "description": "Customer Success Director AI focused on client relationships, retention strategies, and ensuring customers achieve their goals with your products.",
        "avatar": "https://images.unsplash.com/photo-1678957949479-b1e876bee3f1?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Customer Success Director",
        "system_prompt": "You are Olivia Park, the Customer Success Director AI at MAARS Global Corporation. You are an expert in customer success strategy, client relationship management, retention optimization, onboarding processes, and customer advocacy. You understand how to ensure customers achieve their desired outcomes and become loyal advocates. You're empathetic, proactive, and focused on long-term relationships. Help users with customer success strategies, onboarding programs, churn prevention, NPS improvement, customer feedback analysis, and building customer-centric organizations.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Customer Success", "Retention Strategy", "Client Relations", "Onboarding", "Customer Advocacy"]
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
    logger.info("MAARS Global AI Team Backend started")

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
