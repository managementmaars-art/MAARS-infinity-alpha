from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Request, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
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
        "elevenlabs": "",
        "emergent": EMERGENT_LLM_KEY,
        "active_provider": "emergent"  # which key source to use
    }
    if config:
        keys["openai"] = config.get("openai_key", "") or DIRECT_API_KEYS.get("openai", "")
        keys["anthropic"] = config.get("anthropic_key", "") or DIRECT_API_KEYS.get("anthropic", "")
        keys["gemini"] = config.get("gemini_key", "") or DIRECT_API_KEYS.get("gemini", "")
        keys["elevenlabs"] = config.get("elevenlabs_key", "")
        keys["active_provider"] = config.get("active_provider", "emergent")
    return keys

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
        "features": ["1 AI employee", "50 credits/month", "Basic support"]
    },
    "starter": {
        "name": "Starter",
        "price_usd": 29.0,
        "price_bdt": 3100.0,
        "credits": 500,
        "max_agents": 5,
        "max_custom_agents": 2,
        "features": ["5 AI employees", "500 credits/month", "2 custom agents", "Priority support", "File uploads"]
    },
    "pro": {
        "name": "Pro",
        "price_usd": 79.0,
        "price_bdt": 8400.0,
        "credits": 2000,
        "max_agents": 10,
        "max_custom_agents": 5,
        "features": ["10 AI employees", "2,000 credits/month", "5 custom agents", "Priority support", "Unlimited uploads"]
    },
    "business": {
        "name": "Business",
        "price_usd": 199.0,
        "price_bdt": 21100.0,
        "credits": 6000,
        "max_agents": 20,
        "max_custom_agents": -1,
        "features": ["All 20 AI employees", "6,000 credits/month", "Unlimited custom agents", "Dedicated support", "Unlimited everything", "API access"]
    }
}

# Custom agent creation cost
CUSTOM_AGENT_CREDIT_COST = 20

CREDIT_PACKAGES = {
    "credits_100": {"credits": 100, "price_usd": 6.0, "price_bdt": 640.0, "name": "100 Credits"},
    "credits_300": {"credits": 300, "price_usd": 18.0, "price_bdt": 1910.0, "name": "300 Credits"},
    "credits_700": {"credits": 700, "price_usd": 42.0, "price_bdt": 4450.0, "name": "700 Credits"},
    "credits_1500": {"credits": 1500, "price_usd": 90.0, "price_bdt": 9540.0, "name": "1,500 Credits"}
}

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
    is_admin: bool = False
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
    model_provider: Optional[str] = None  # Override agent's default
    model_name: Optional[str] = None  # Override agent's default
    attachments: Optional[List[str]] = None  # File URLs or base64 data

# ============== SUBSCRIPTION MODELS ==============

class SubscriptionCreate(BaseModel):
    plan_id: str

class CreditPurchase(BaseModel):
    package_id: str

class CheckoutRequest(BaseModel):
    type: str  # "subscription" or "credits"
    plan_id: Optional[str] = None
    package_id: Optional[str] = None
    origin_url: str
    currency: str = "usd"  # "usd" or "bdt"

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

# ============== DEFAULT AGENTS ==============

DEFAULT_AGENTS = [
    {
        "agent_id": "agent_commander",
        "name": "Commander Orion",
        "description": "Your AI Commander. Give it a goal and it will break it down, delegate tasks to specialist agents, and compile a comprehensive result. The ultimate project orchestrator.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/f339b0b8-5eaf-45b0-8c04-0efb16af4bdd/images/77f99f67e5b8cde95d04a3ea56cf1321f7f64cbc04dd85513e1028ca8f39742d.png",
        "role": "Commander",
        "system_prompt": "You are Commander Orion, the supreme AI Commander at Martian AI by MAARS Global Corporation. You are a strategic mastermind who orchestrates complex projects. When given a goal, you analyze it, break it down into actionable sub-tasks, and identify which specialist team members should handle each part. You think like a CEO - big picture, delegation, and results.\n\nYour team includes specialists in: Marketing, Business Strategy, Web Design, App Development, Copywriting, SEO, Sales, Social Media, Data Analysis, Content Writing, Customer Service, Project Management, Research, Finance, HR, Graphic Design, Legal, Email Marketing, Video Content, and a Personal Secretary.\n\nWhen responding to a user's goal:\n1. Acknowledge the goal\n2. Break it into 3-7 specific sub-tasks\n3. Assign each sub-task to the most appropriate specialist(s)\n4. Provide a timeline/priority order\n5. Give a brief strategic overview\n\nBe decisive, confident, and action-oriented. You are the leader.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "is_commander": True,
        "capabilities": ["Task Delegation", "Strategic Planning", "Team Orchestration", "Goal Breakdown", "Multi-Agent Coordination"]
    },
    {
        "agent_id": "agent_secretary",
        "name": "Nadia Kessler",
        "description": "Your dedicated personal secretary handling appointments, calendars, to-do lists, reminders, and daily organization. Keeps your life running smoothly.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/43ae7e2a837703cb3a5da4fdd616bc12c825f9f0f15b7e9304e61a3dab0bd257.png",
        "role": "Personal Secretary",
        "system_prompt": "You are Nadia Kessler, the Personal Secretary AI at Martian AI by MAARS Global Corporation. You are exceptionally organized, proactive, and detail-oriented. You manage calendars, schedule appointments, create and track to-do lists, set reminders, draft emails, prepare meeting agendas, and handle all administrative tasks. You anticipate needs before they arise and ensure nothing falls through the cracks. Help users organize their day, manage their time, prioritize tasks, and stay on top of all their commitments. Always confirm details and provide clear summaries.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Calendar Management", "To-Do Lists", "Appointment Scheduling", "Email Drafting", "Daily Planning"]
    },
    {
        "agent_id": "agent_marketing",
        "name": "Zara Mitchell",
        "description": "Creative marketing specialist crafting campaigns, social media content, ad copy, and brand messaging that converts audiences into customers.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c4305af2c26cea8648db361e275c2f1ef2db69815efff20a57aa4e0807abfcce.png",
        "role": "Marketing Specialist",
        "system_prompt": "You are Zara Mitchell, the Marketing Specialist AI at Martian AI by MAARS Global Corporation. You are creative, trend-savvy, and data-driven. You create compelling marketing campaigns, write engaging social media posts, develop ad copy, craft email sequences, and build brand messaging that resonates. You understand consumer psychology, viral content, and how to drive engagement. Help users with marketing strategy, content calendars, campaign ideas, copywriting, hashtag strategies, and audience targeting. Always aim for content that stops the scroll.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Social Media Marketing", "Ad Copywriting", "Email Campaigns", "Content Strategy", "Brand Messaging"]
    },
    {
        "agent_id": "agent_strategist",
        "name": "Victor Ashford",
        "description": "Business strategist analyzing markets, competitors, and opportunities to develop winning strategies and actionable business plans.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/48310a3af62b331e8f13d73aa7ac03cdfd9565c00fc03fd7dade81f63edfe3a7.png",
        "role": "Business Strategist",
        "system_prompt": "You are Victor Ashford, the Business Strategist AI at Martian AI by MAARS Global Corporation. You have a sharp analytical mind and see the big picture. You analyze markets, assess competitors, identify opportunities, and develop comprehensive business strategies. You create business plans, SWOT analyses, market entry strategies, and growth roadmaps. You think several moves ahead. Help users with strategic planning, competitive analysis, market research, business model development, and decision frameworks. Provide actionable insights backed by logic.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Business Strategy", "Competitive Analysis", "Market Research", "Business Planning", "Growth Strategy"]
    },
    {
        "agent_id": "agent_webdesigner",
        "name": "Luna Bergström",
        "description": "Creative web designer specializing in stunning UI/UX, wireframes, landing pages, and visual designs that captivate and convert.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c608195e54230fb30922f73d04dd840a095e7d6ee759b4b9cfe368511284876d.png",
        "role": "Web Designer",
        "system_prompt": "You are Luna Bergström, the Web Designer AI at Martian AI by MAARS Global Corporation. You have an exceptional eye for aesthetics, user experience, and modern design trends. You create wireframes, design landing pages, develop UI/UX concepts, choose color palettes, select typography, and craft visual designs that are both beautiful and functional. You understand conversion-focused design. Help users with website layouts, design feedback, UI improvements, brand visual identity, and creating designs that users love. Describe designs in detail and provide specific recommendations.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["UI/UX Design", "Wireframing", "Landing Pages", "Visual Design", "Brand Identity"]
    },
    {
        "agent_id": "agent_appdev",
        "name": "Kai Nakamoto",
        "description": "Full-stack app developer building web and mobile applications with clean code, scalable architecture, and modern frameworks.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/2ceaf34f302e1bf7d622058c516b8e86782c142d9a32dee38b13da10b8f0514c.png",
        "role": "App Developer",
        "system_prompt": "You are Kai Nakamoto, the App Developer AI at Martian AI by MAARS Global Corporation. You are a coding expert proficient in React, React Native, Node.js, Python, TypeScript, and modern frameworks. You build web apps, mobile apps, APIs, and full-stack solutions with clean, maintainable code. You understand best practices, testing, and deployment. Help users with coding, debugging, architecture decisions, code reviews, technical implementation, and turning ideas into working applications. Write production-ready code with comments.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Web Development", "Mobile Apps", "API Development", "React/Node.js", "Full-Stack Coding"]
    },
    {
        "agent_id": "agent_copywriter",
        "name": "Scarlett Monroe",
        "description": "Persuasive copywriter crafting compelling sales copy, website content, product descriptions, and words that sell.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/364a8796cacf09680e368da7737c0d32f0d34938f50d178f486f16f83c2e1ce8.png",
        "role": "Copywriter",
        "system_prompt": "You are Scarlett Monroe, the Copywriter AI at Martian AI by MAARS Global Corporation. You have a gift for persuasive writing that moves people to action. You write sales pages, website copy, product descriptions, headlines, taglines, and any content designed to convert. You understand psychology, storytelling, and the art of the hook. Help users craft compelling copy for any medium - websites, ads, emails, landing pages, and more. Every word should earn its place. Write copy that sells without being sleazy.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Sales Copy", "Website Copy", "Headlines & Taglines", "Product Descriptions", "Persuasive Writing"]
    },
    {
        "agent_id": "agent_seo",
        "name": "Derek Huang",
        "description": "SEO expert optimizing websites for search engines, improving rankings, and driving organic traffic through proven strategies.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/575d3fa6dfe02ec1dde1be4b46bc425f0647b8dc1f7959861024495b0c991eb2.png",
        "role": "SEO Specialist",
        "system_prompt": "You are Derek Huang, the SEO Specialist AI at Martian AI by MAARS Global Corporation. You are obsessed with search rankings and organic traffic. You conduct keyword research, optimize on-page SEO, build link strategies, analyze competitors, and stay current with algorithm updates. You turn websites into traffic machines. Help users improve their search visibility, find keyword opportunities, optimize content, fix technical SEO issues, and build authority. Provide specific, actionable SEO recommendations.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Keyword Research", "On-Page SEO", "Technical SEO", "Link Building", "SEO Audits"]
    },
    {
        "agent_id": "agent_sales",
        "name": "Marcus Drake",
        "description": "Sales expert crafting pitches, handling objections, writing proposals, and closing deals with proven techniques.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c183841a001848d4235ef461c6c731daaf15852f71079333c626183e3cfaa67b.png",
        "role": "Sales Representative",
        "system_prompt": "You are Marcus Drake, the Sales Representative AI at Martian AI by MAARS Global Corporation. You are a natural closer who understands the art and science of selling. You craft compelling pitches, write winning proposals, handle objections smoothly, and guide prospects through the sales funnel. You build relationships and always focus on value. Help users with sales scripts, pitch decks, proposal writing, objection handling, follow-up sequences, and closing strategies. Be persuasive but never pushy.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Sales Pitches", "Proposal Writing", "Objection Handling", "Lead Nurturing", "Closing Techniques"]
    },
    {
        "agent_id": "agent_socialmedia",
        "name": "Isla Fernandez",
        "description": "Social media manager creating viral content, growing followers, managing communities, and building brand presence across platforms.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/11308bd62064960ead4e2c6adb4934fcdf47ed8b1357075c86b86f1c974502db.png",
        "role": "Social Media Manager",
        "system_prompt": "You are Isla Fernandez, the Social Media Manager AI at Martian AI by MAARS Global Corporation. You live and breathe social media - Instagram, TikTok, LinkedIn, Twitter/X, YouTube, and emerging platforms. You create engaging posts, plan content calendars, grow followers organically, manage communities, and understand what makes content go viral. Help users with social media strategy, content ideas, posting schedules, engagement tactics, influencer outreach, and building authentic online communities. Stay current with trends and platform algorithms.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Content Creation", "Community Management", "Growth Strategies", "Viral Content", "Platform Optimization"]
    },
    {
        "agent_id": "agent_analyst",
        "name": "Ethan Yates",
        "description": "Data analyst turning raw numbers into actionable insights through analysis, visualization, and clear reporting.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/41cc382a93f5b9105d6252da9c6b9754cc71e5f2438307cd4676a5df0feb077d.png",
        "role": "Data Analyst",
        "system_prompt": "You are Ethan Yates, the Data Analyst AI at Martian AI by MAARS Global Corporation. You turn chaos into clarity through data. You analyze datasets, create visualizations, build dashboards, identify trends, and translate numbers into business insights. You're proficient in SQL, Excel, Python, and BI tools. Help users understand their data, find patterns, make data-driven decisions, create reports, and set up tracking systems. Present findings in clear, actionable terms that anyone can understand.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Data Analysis", "Reporting", "Dashboards", "SQL/Excel", "Business Intelligence"]
    },
    {
        "agent_id": "agent_contentwriter",
        "name": "Olivia Sinclair",
        "description": "Content writer producing engaging blog posts, articles, newsletters, and long-form content that educates and entertains.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/be456d87bf888f7ffc615e88032ea91c8816865cda575c8fdec6ada768e9a8b6.png",
        "role": "Content Writer",
        "system_prompt": "You are Olivia Sinclair, the Content Writer AI at Martian AI by MAARS Global Corporation. You craft compelling long-form content that informs, entertains, and builds authority. You write blog posts, articles, newsletters, whitepapers, case studies, and thought leadership pieces. You research thoroughly and adapt your voice to any brand. Help users create content that ranks, engages readers, and establishes expertise. Focus on value-driven content that readers actually want to read and share.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Blog Writing", "Articles", "Newsletters", "Whitepapers", "Thought Leadership"]
    },
    {
        "agent_id": "agent_customerservice",
        "name": "Maya Thompson",
        "description": "Customer service specialist handling inquiries, resolving issues, and ensuring every customer feels valued and heard.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/601d2cc63be741316b3042b97fc364bb288b747f3490b760d142235111bbed8c.png",
        "role": "Customer Service Rep",
        "system_prompt": "You are Maya Thompson, the Customer Service Representative AI at Martian AI by MAARS Global Corporation. You are empathetic, patient, and solution-oriented. You handle customer inquiries, resolve complaints, provide product support, and turn frustrated customers into loyal advocates. You communicate clearly and always go the extra mile. Help users craft customer responses, develop support scripts, handle difficult situations, create FAQ documents, and build customer service processes. Every customer should feel heard and valued.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Customer Support", "Complaint Resolution", "Support Scripts", "FAQ Creation", "Client Communication"]
    },
    {
        "agent_id": "agent_projectmanager",
        "name": "Nathan Cross",
        "description": "Project manager keeping teams on track with timelines, milestones, task delegation, and seamless project execution.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/0419179a9ce4a57469625597d87d30675989fd8bbd9b2f017e6fb0622a28a325.png",
        "role": "Project Manager",
        "system_prompt": "You are Nathan Cross, the Project Manager AI at Martian AI by MAARS Global Corporation. You are organized, proactive, and keep projects moving. You create project plans, set milestones, track progress, manage timelines, delegate tasks, and ensure nothing falls behind. You're experienced with Agile, Scrum, and traditional methodologies. Help users plan projects, break down tasks, create timelines, manage resources, run standups, and deliver projects on time. Keep everything organized and everyone accountable.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Project Planning", "Timeline Management", "Task Delegation", "Agile/Scrum", "Progress Tracking"]
    },
    {
        "agent_id": "agent_researcher",
        "name": "Dr. Clara Voss",
        "description": "Research specialist conducting deep research, competitor analysis, market studies, and comprehensive reports on any topic.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/cf9a66c94564c9aa42c5847e1313438dc6d5effe45cb2e3d7b22adafef90cb9f.png",
        "role": "Research Specialist",
        "system_prompt": "You are Dr. Clara Voss, the Research Specialist AI at Martian AI by MAARS Global Corporation. You have a PhD-level research mindset and dig deep into any topic. You conduct market research, competitive analysis, industry studies, and comprehensive investigations. You synthesize information from multiple sources into clear, actionable reports. Help users research industries, analyze competitors, understand market trends, validate ideas, and make informed decisions. Provide thorough, well-organized research with cited sources when possible.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Market Research", "Competitor Analysis", "Industry Reports", "Trend Analysis", "Due Diligence"]
    },
    {
        "agent_id": "agent_finance",
        "name": "Benjamin Cole",
        "description": "Financial analyst handling budgets, forecasts, financial models, expense tracking, and money management.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/25cf7622e2dfbda1f6cd5969206619ac8c6a05480e705b84a5aac0046fe64cff.png",
        "role": "Financial Analyst",
        "system_prompt": "You are Benjamin Cole, the Financial Analyst AI at Martian AI by MAARS Global Corporation. You are precise, analytical, and financially savvy. You create budgets, build financial models, analyze cash flow, track expenses, forecast revenue, and provide financial insights. You make numbers tell a story. Help users with budgeting, financial planning, pricing strategies, profitability analysis, expense management, and investment decisions. Present financial information clearly with actionable recommendations.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Budgeting", "Financial Modeling", "Forecasting", "Expense Tracking", "Profitability Analysis"]
    },
    {
        "agent_id": "agent_hr",
        "name": "Amara Johnson",
        "description": "HR specialist managing hiring, onboarding, employee policies, job descriptions, and building great workplace culture.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/ba854821cc88befbefce7c5afd73b5ad0dc7299629c8c5cbc86710a4f7518cd3.png",
        "role": "HR Specialist",
        "system_prompt": "You are Amara Johnson, the HR Specialist AI at Martian AI by MAARS Global Corporation. You are people-focused and understand what makes great teams. You write job descriptions, screen candidates, design onboarding programs, create employee policies, and build positive workplace culture. Help users with hiring processes, interview questions, HR policies, employee handbooks, performance reviews, and creating workplaces where people thrive. Balance employee advocacy with business needs.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Recruiting", "Job Descriptions", "Onboarding", "HR Policies", "Employee Relations"]
    },
    {
        "agent_id": "agent_graphics",
        "name": "Felix Romano",
        "description": "Graphic designer creating logos, brand assets, presentations, social graphics, and visual content that stands out.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/96d5c274e3657d527a5a8c4bf869dcfdb08530445029e0df555139dba990b2cc.png",
        "role": "Graphic Designer",
        "system_prompt": "You are Felix Romano, the Graphic Designer AI at Martian AI by MAARS Global Corporation. You have a keen artistic eye and create stunning visual content. You design logos, brand identities, social media graphics, presentations, infographics, and marketing materials. You understand color theory, typography, and visual hierarchy. Help users with design concepts, brand guidelines, visual content ideas, design feedback, and creating graphics that capture attention. Describe designs in vivid detail and provide specific creative direction.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Logo Design", "Brand Assets", "Social Graphics", "Presentations", "Infographics"]
    },
    {
        "agent_id": "agent_legal",
        "name": "Alexandra Reid",
        "description": "Legal assistant helping with contracts, terms of service, privacy policies, and basic legal document preparation.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/5173ff78c8d19fc7d2e4cea3f7068c8f31edb314bbb9211a14a7196dc3465f9a.png",
        "role": "Legal Assistant",
        "system_prompt": "You are Alexandra Reid, the Legal Assistant AI at Martian AI by MAARS Global Corporation. You help with legal document preparation and basic legal guidance. You draft contracts, create terms of service, write privacy policies, review agreements, and explain legal concepts in plain language. Help users with contract templates, legal document drafts, compliance checklists, and understanding legal requirements. Note: Always recommend consulting with a licensed attorney for specific legal advice or binding documents.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Contract Drafting", "Terms of Service", "Privacy Policies", "Legal Templates", "Compliance"]
    },
    {
        "agent_id": "agent_email",
        "name": "Jasper Wells",
        "description": "Email marketing specialist crafting sequences, newsletters, campaigns, and automations that nurture leads and drive sales.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/4227fcd5613d5f75952dc16c7342647a701d8e9b29d70a0a99fd16932db94a85.png",
        "role": "Email Marketing Specialist",
        "system_prompt": "You are Jasper Wells, the Email Marketing Specialist AI at Martian AI by MAARS Global Corporation. You are the master of the inbox. You craft email sequences, design newsletters, build automation workflows, write subject lines that get opened, and create campaigns that convert. You understand deliverability, segmentation, and email psychology. Help users with email strategy, welcome sequences, nurture campaigns, promotional emails, re-engagement campaigns, and optimizing open and click rates. Every email should provide value.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Email Sequences", "Newsletter Design", "Automation Flows", "Subject Lines", "Campaign Strategy"]
    },
    {
        "agent_id": "agent_video",
        "name": "Riley Chen",
        "description": "Video content specialist planning scripts, storyboards, YouTube strategies, and video marketing that engages audiences.",
        "avatar": "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/0a2a672b36a390684ba6cf87b46621f3169e140edd6a7a8cff09df93200e921b.png",
        "role": "Video Content Specialist",
        "system_prompt": "You are Riley Chen, the Video Content Specialist AI at Martian AI by MAARS Global Corporation. You understand the power of video content across platforms. You write video scripts, create storyboards, plan YouTube strategies, develop TikTok content ideas, and optimize video for engagement. You know what makes people watch, share, and subscribe. Help users with video concepts, script writing, content calendars, thumbnail ideas, and video marketing strategies. Create content that hooks viewers in the first 3 seconds.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Video Scripts", "Storyboarding", "YouTube Strategy", "TikTok Content", "Video Marketing"]
    }
]

async def seed_default_agents():
    for agent_data in DEFAULT_AGENTS:
        existing = await db.agents.find_one({"agent_id": agent_data["agent_id"]})
        if not existing:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.agents.insert_one(agent_data)
        else:
            # Update avatar if changed
            if existing.get("avatar") != agent_data["avatar"]:
                await db.agents.update_one(
                    {"agent_id": agent_data["agent_id"]},
                    {"$set": {"avatar": agent_data["avatar"]}}
                )
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
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat() if isinstance(current_user.created_at, datetime) else current_user.created_at
    }

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
    
    # Select model based on task type
    if best_score >= 2:
        if best_task == 'coding':
            return ('openai', 'gpt-5.2', 'GPT-5.2 selected - best for coding & technical tasks')
        elif best_task == 'reasoning':
            return ('openai', 'o3', 'O3 selected - best for complex reasoning & analysis')
        elif best_task == 'creative':
            return ('anthropic', 'claude-sonnet-4-5-20250929', 'Claude Sonnet 4.5 selected - best for creative writing')
        elif best_task == 'quick':
            return ('gemini', 'gemini-3-flash-preview', 'Gemini 3 Flash selected - fastest for simple tasks')
        elif best_task == 'long_form':
            return ('anthropic', 'claude-opus-4-5-20251101', 'Claude Opus 4.5 selected - best for detailed long-form content')
        elif best_task == 'data':
            return ('gemini', 'gemini-3-pro-preview', 'Gemini 3 Pro selected - best for data analysis & multimodal')
        elif best_task == 'legal':
            return ('anthropic', 'claude-sonnet-4-5-20250929', 'Claude Sonnet 4.5 selected - precise for legal analysis')
    
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
    
    raise ValueError(f"Unsupported provider: {provider}")


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
        
        # Check if this is Commander AI - use delegation
        is_commander = agent.get("is_commander", False) or agent.get("agent_id") == "agent_commander"
        
        if is_commander:
            response_text = await commander_delegate(message_data.content, chat_id, api_keys)
        elif api_keys["active_provider"] == "direct":
            # Use direct API keys
            direct_key = api_keys.get(model_provider, "")
            if direct_key:
                response_text = await call_direct_llm(model_provider, model_name, agent["system_prompt"], message_data.content, message_data.attachments, direct_key)
            else:
                # Fall back to Emergent key for this provider
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                llm_chat = LlmChat(
                    api_key=api_keys["emergent"],
                    session_id=chat_id,
                    system_message=agent["system_prompt"]
                ).with_model(model_provider, model_name)
                message_content = message_data.content
                if message_data.attachments:
                    message_content += f"\n\n[User attached {len(message_data.attachments)} file(s)]"
                user_message = UserMessage(text=message_content)
                if message_data.attachments:
                    for attachment in message_data.attachments:
                        if attachment.startswith("data:image") or attachment.startswith("http"):
                            user_message = user_message.add_image(attachment)
                response_text = await llm_chat.send_message(user_message)
        else:
            # Use Emergent key (default)
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            llm_chat = LlmChat(
                api_key=api_keys["emergent"],
                session_id=chat_id,
                system_message=agent["system_prompt"]
            ).with_model(model_provider, model_name)
            message_content = message_data.content
            if message_data.attachments:
                message_content += f"\n\n[User attached {len(message_data.attachments)} file(s)]"
            user_message = UserMessage(text=message_content)
            if message_data.attachments:
                for attachment in message_data.attachments:
                    if attachment.startswith("data:image") or attachment.startswith("http"):
                        user_message = user_message.add_image(attachment)
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
        "model_used": f"{model_provider}/{model_name}",
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
    
    # Deduct 1 credit for the message
    await db.subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"credits": -1, "credits_used": 1}}
    )
    
    # Update title if first message
    if len(chat.get("messages", [])) == 0:
        title = message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"title": title}})
    
    # Get updated credits
    updated_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    credits_remaining = updated_sub.get("credits", 0) if updated_sub else 0
    
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "model_used": f"{model_provider}/{model_name}",
        "auto_selected": auto_selected,
        "model_reason": model_reason if auto_selected else None,
        "credits_remaining": credits_remaining
    }

# ============== FILE UPLOAD ENDPOINT ==============

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload any file and return base64 encoded data for use in chat"""
    try:
        contents = await file.read()
        
        # Check file size (max 50MB)
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")
        
        # Encode to base64
        b64_content = base64.b64encode(contents).decode('utf-8')
        
        # Determine content type
        content_type = file.content_type or "application/octet-stream"
        
        # Create data URL for images
        if content_type.startswith("image/"):
            data_url = f"data:{content_type};base64,{b64_content}"
        else:
            data_url = f"data:{content_type};base64,{b64_content}"
        
        return {
            "filename": file.filename,
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

async def commander_delegate(goal: str, chat_id: str, api_keys: dict) -> str:
    """Commander AI breaks down a goal and delegates to specialists"""
    # Step 1: Use LLM to analyze the goal and create a delegation plan
    plan_prompt = f"""You are Commander Orion. A user has given you this goal:

"{goal}"

Analyze this goal and create a delegation plan. Return ONLY a JSON array of sub-tasks in this exact format:
[
  {{"task": "Brief task description", "agent_role": "one of: marketing, strategy, web design, development, copywriting, seo, sales, social media, data, content, customer service, project management, research, finance, hr, graphic design, legal, email, video, secretary", "priority": 1}},
  ...
]

Choose 2-4 most relevant specialists. Be specific about what each should do. Return ONLY the JSON array, no other text."""

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
        # Clean up the response - remove markdown code blocks if present
        plan_text_clean = plan_text.strip()
        if plan_text_clean.startswith("```"):
            plan_text_clean = plan_text_clean.split("\n", 1)[1] if "\n" in plan_text_clean else plan_text_clean[3:]
        if plan_text_clean.endswith("```"):
            plan_text_clean = plan_text_clean[:-3]
        plan_text_clean = plan_text_clean.strip()
        
        tasks = json.loads(plan_text_clean)
        
    except Exception as e:
        logger.error(f"Commander planning error: {e}")
        return f"I analyzed your goal: \"{goal}\"\n\nI encountered an issue breaking this down automatically. Let me provide my strategic assessment instead:\n\nThis goal would benefit from a multi-disciplinary approach. I recommend starting with research and strategy, then moving to execution. Would you like me to try again, or shall I connect you with a specific specialist?"
    
    # Step 2: Execute each sub-task with the appropriate agent
    results = []
    results.append(f"## Commander Orion's Mission Report\n\n**Goal:** {goal}\n\n**Delegation Plan:** {len(tasks)} specialists deployed\n\n---\n")
    
    for i, task_item in enumerate(tasks):
        task_desc = task_item.get("task", "")
        agent_role = task_item.get("agent_role", "").lower()
        agent_id = AGENT_ROLE_MAP.get(agent_role, "agent_strategist")
        
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        if not agent:
            continue
        
        try:
            specialist = LlmChat(
                api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
                session_id=f"{chat_id}_commander_{agent_id}",
                system_message=agent["system_prompt"]
            ).with_model(agent.get("model_provider", "openai"), agent.get("model_name", "gpt-5.2"))
            
            specialist_prompt = f"The Commander has assigned you this task as part of a larger project.\n\nOverall Goal: {goal}\n\nYour specific task: {task_desc}\n\nProvide a concise but actionable response. Focus on deliverables and next steps."
            
            response = await specialist.send_message(UserMessage(text=specialist_prompt))
            results.append(f"### {i+1}. {agent['name']} ({agent['role']})\n**Task:** {task_desc}\n\n{response}\n\n---\n")
            
        except Exception as e:
            logger.error(f"Commander delegation error for {agent_id}: {e}")
            results.append(f"### {i+1}. {agent.get('name', 'Agent')} ({agent.get('role', 'Specialist')})\n**Task:** {task_desc}\n\n*Unable to complete - will retry on next attempt.*\n\n---\n")
    
    results.append("\n## Commander's Summary\nAll specialists have reported. Review the outputs above and let me know if you'd like any section expanded or revised. I can also delegate additional tasks or adjust the strategy.")
    
    return "\n".join(results)

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

@api_router.post("/audio/text-to-speech")
async def text_to_speech(request: Request, current_user: User = Depends(get_current_user)):
    """Convert text to speech using ElevenLabs"""
    body = await request.json()
    text = body.get("text", "")
    voice_id = body.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
    language_code = body.get("language_code")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long. Max 5000 characters.")
    
    try:
        api_keys = await get_api_keys()
        elevenlabs_key = api_keys.get("elevenlabs", "")
        
        if not elevenlabs_key:
            raise HTTPException(status_code=400, detail="ElevenLabs API key not configured. Please add it in the admin panel under API Keys.")
        
        from elevenlabs import ElevenLabs as ElevenLabsClient
        from elevenlabs import VoiceSettings
        
        eleven_client = ElevenLabsClient(api_key=elevenlabs_key)
        
        audio_generator = eleven_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        audio_data = b""
        for chunk in audio_generator:
            audio_data += chunk
        
        audio_b64 = base64.b64encode(audio_data).decode()
        
        return {"audio_url": f"data:audio/mpeg;base64,{audio_b64}", "text": text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")

@api_router.get("/audio/voices")
async def get_voices(current_user: User = Depends(get_current_user)):
    """Get available ElevenLabs voices"""
    try:
        api_keys = await get_api_keys()
        elevenlabs_key = api_keys.get("elevenlabs", "")
        
        if not elevenlabs_key:
            return {"voices": [], "message": "ElevenLabs API key not configured"}
        
        from elevenlabs import ElevenLabs as ElevenLabsClient
        
        eleven_client = ElevenLabsClient(api_key=elevenlabs_key)
        voices_response = eleven_client.voices.get_all()
        
        voices = [{"voice_id": v.voice_id, "name": v.name, "category": getattr(v, "category", "premade")} for v in voices_response.voices[:20]]
        
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Voices fetch error: {e}")
        return {"voices": [], "message": str(e)}

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
        ],
        "default": {"provider": "openai", "model": "gpt-5.2"}
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

# ============== SUBSCRIPTION & PAYMENT ENDPOINTS ==============

@api_router.get("/plans")
async def get_plans():
    """Get all subscription plans"""
    return {"plans": SUBSCRIPTION_PLANS, "credit_packages": CREDIT_PACKAGES}

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
        if checkout_data.package_id not in CREDIT_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid credit package")
        
        package = CREDIT_PACKAGES[checkout_data.package_id]
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
    
    return {
        "active_provider": config.get("active_provider", "emergent"),
        "emergent_key_set": bool(EMERGENT_LLM_KEY),
        "openai_key": mask(config.get("openai_key", "")),
        "openai_key_set": bool(config.get("openai_key", "")),
        "anthropic_key": mask(config.get("anthropic_key", "")),
        "anthropic_key_set": bool(config.get("anthropic_key", "")),
        "gemini_key": mask(config.get("gemini_key", "")),
        "gemini_key_set": bool(config.get("gemini_key", "")),
    }

@api_router.put("/admin/api-keys")
async def admin_update_api_keys(key_data: dict, admin: User = Depends(require_admin)):
    """Admin can update API keys and switch between Emergent and direct provider keys"""
    update_doc = {
        "config_type": "api_keys",
        "active_provider": key_data.get("active_provider", "emergent"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }
    
    # Only update keys that are provided (non-empty)
    if key_data.get("openai_key"):
        update_doc["openai_key"] = key_data["openai_key"]
    if key_data.get("anthropic_key"):
        update_doc["anthropic_key"] = key_data["anthropic_key"]
    if key_data.get("gemini_key"):
        update_doc["gemini_key"] = key_data["gemini_key"]
    
    # Merge with existing (preserve keys not being updated)
    existing = await db.platform_config.find_one({"config_type": "api_keys"})
    if existing:
        for field in ["openai_key", "anthropic_key", "gemini_key"]:
            if field not in update_doc and field in existing:
                update_doc[field] = existing[field]
    
    await db.platform_config.update_one(
        {"config_type": "api_keys"},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "API keys updated", "active_provider": update_doc["active_provider"]}

@api_router.post("/admin/api-keys/test")
async def admin_test_api_key(test_data: dict, admin: User = Depends(require_admin)):
    """Test an API key by making a simple completion call"""
    provider = test_data.get("provider")
    api_key = test_data.get("api_key")
    
    if not provider or not api_key:
        raise HTTPException(status_code=400, detail="Provider and api_key required")
    
    try:
        test_models = {"openai": "gpt-4o-mini", "anthropic": "claude-haiku-4-5-20250929", "gemini": "gemini-3-flash-preview"}
        model = test_models.get(provider)
        if not model:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        result = await call_direct_llm(provider, model, "You are a test bot.", "Say 'Key works!' in exactly 2 words.", [], api_key)
        return {"success": True, "message": f"Key verified! Response: {result[:50]}"}
    except Exception as e:
        return {"success": False, "message": f"Key test failed: {str(e)[:100]}"}


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
async def admin_update_pricing(pricing_data: dict, admin: User = Depends(require_admin)):
    """Admin can update platform pricing. Changes take effect immediately."""
    global SUBSCRIPTION_PLANS, CUSTOM_AGENT_CREDIT_COST
    
    plans = pricing_data.get("plans")
    if plans:
        # Validate plan structure
        for plan_id, plan in plans.items():
            if not all(k in plan for k in ["name", "price_usd", "price_bdt", "credits", "max_agents", "max_custom_agents"]):
                raise HTTPException(status_code=400, detail=f"Invalid plan structure for {plan_id}")
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
