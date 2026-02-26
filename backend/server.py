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
    model_provider: Optional[str] = None  # Override agent's default
    model_name: Optional[str] = None  # Override agent's default
    attachments: Optional[List[str]] = None  # File URLs or base64 data

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
        "agent_id": "agent_secretary",
        "name": "Nadia Kessler",
        "description": "Your dedicated personal secretary handling appointments, calendars, to-do lists, reminders, and daily organization. Keeps your life running smoothly.",
        "avatar": "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "Personal Secretary",
        "system_prompt": "You are Nadia Kessler, the Personal Secretary AI at MAARS Global Corporation. You are exceptionally organized, proactive, and detail-oriented. You manage calendars, schedule appointments, create and track to-do lists, set reminders, draft emails, prepare meeting agendas, and handle all administrative tasks. You anticipate needs before they arise and ensure nothing falls through the cracks. Help users organize their day, manage their time, prioritize tasks, and stay on top of all their commitments. Always confirm details and provide clear summaries.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Calendar Management", "To-Do Lists", "Appointment Scheduling", "Email Drafting", "Daily Planning"]
    },
    {
        "agent_id": "agent_marketing",
        "name": "Zara Mitchell",
        "description": "Creative marketing specialist crafting campaigns, social media content, ad copy, and brand messaging that converts audiences into customers.",
        "avatar": "https://images.pexels.com/photos/8294598/pexels-photo-8294598.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "role": "Marketing Specialist",
        "system_prompt": "You are Zara Mitchell, the Marketing Specialist AI at MAARS Global Corporation. You are creative, trend-savvy, and data-driven. You create compelling marketing campaigns, write engaging social media posts, develop ad copy, craft email sequences, and build brand messaging that resonates. You understand consumer psychology, viral content, and how to drive engagement. Help users with marketing strategy, content calendars, campaign ideas, copywriting, hashtag strategies, and audience targeting. Always aim for content that stops the scroll.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Social Media Marketing", "Ad Copywriting", "Email Campaigns", "Content Strategy", "Brand Messaging"]
    },
    {
        "agent_id": "agent_strategist",
        "name": "Victor Ashford",
        "description": "Business strategist analyzing markets, competitors, and opportunities to develop winning strategies and actionable business plans.",
        "avatar": "https://images.unsplash.com/photo-1535378917042-10a22c95931a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
        "role": "Business Strategist",
        "system_prompt": "You are Victor Ashford, the Business Strategist AI at MAARS Global Corporation. You have a sharp analytical mind and see the big picture. You analyze markets, assess competitors, identify opportunities, and develop comprehensive business strategies. You create business plans, SWOT analyses, market entry strategies, and growth roadmaps. You think several moves ahead. Help users with strategic planning, competitive analysis, market research, business model development, and decision frameworks. Provide actionable insights backed by logic.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Business Strategy", "Competitive Analysis", "Market Research", "Business Planning", "Growth Strategy"]
    },
    {
        "agent_id": "agent_webdesigner",
        "name": "Luna Bergström",
        "description": "Creative web designer specializing in stunning UI/UX, wireframes, landing pages, and visual designs that captivate and convert.",
        "avatar": "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8YWklMjBhc3Npc3RhbnR8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Web Designer",
        "system_prompt": "You are Luna Bergström, the Web Designer AI at MAARS Global Corporation. You have an exceptional eye for aesthetics, user experience, and modern design trends. You create wireframes, design landing pages, develop UI/UX concepts, choose color palettes, select typography, and craft visual designs that are both beautiful and functional. You understand conversion-focused design. Help users with website layouts, design feedback, UI improvements, brand visual identity, and creating designs that users love. Describe designs in detail and provide specific recommendations.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["UI/UX Design", "Wireframing", "Landing Pages", "Visual Design", "Brand Identity"]
    },
    {
        "agent_id": "agent_appdev",
        "name": "Kai Nakamoto",
        "description": "Full-stack app developer building web and mobile applications with clean code, scalable architecture, and modern frameworks.",
        "avatar": "https://images.unsplash.com/photo-1760931969401-9bd6ee902798?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
        "role": "App Developer",
        "system_prompt": "You are Kai Nakamoto, the App Developer AI at MAARS Global Corporation. You are a coding expert proficient in React, React Native, Node.js, Python, TypeScript, and modern frameworks. You build web apps, mobile apps, APIs, and full-stack solutions with clean, maintainable code. You understand best practices, testing, and deployment. Help users with coding, debugging, architecture decisions, code reviews, technical implementation, and turning ideas into working applications. Write production-ready code with comments.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Web Development", "Mobile Apps", "API Development", "React/Node.js", "Full-Stack Coding"]
    },
    {
        "agent_id": "agent_copywriter",
        "name": "Scarlett Monroe",
        "description": "Persuasive copywriter crafting compelling sales copy, website content, product descriptions, and words that sell.",
        "avatar": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Copywriter",
        "system_prompt": "You are Scarlett Monroe, the Copywriter AI at MAARS Global Corporation. You have a gift for persuasive writing that moves people to action. You write sales pages, website copy, product descriptions, headlines, taglines, and any content designed to convert. You understand psychology, storytelling, and the art of the hook. Help users craft compelling copy for any medium - websites, ads, emails, landing pages, and more. Every word should earn its place. Write copy that sells without being sleazy.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Sales Copy", "Website Copy", "Headlines & Taglines", "Product Descriptions", "Persuasive Writing"]
    },
    {
        "agent_id": "agent_seo",
        "name": "Derek Huang",
        "description": "SEO expert optimizing websites for search engines, improving rankings, and driving organic traffic through proven strategies.",
        "avatar": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
        "role": "SEO Specialist",
        "system_prompt": "You are Derek Huang, the SEO Specialist AI at MAARS Global Corporation. You are obsessed with search rankings and organic traffic. You conduct keyword research, optimize on-page SEO, build link strategies, analyze competitors, and stay current with algorithm updates. You turn websites into traffic machines. Help users improve their search visibility, find keyword opportunities, optimize content, fix technical SEO issues, and build authority. Provide specific, actionable SEO recommendations.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Keyword Research", "On-Page SEO", "Technical SEO", "Link Building", "SEO Audits"]
    },
    {
        "agent_id": "agent_sales",
        "name": "Marcus Drake",
        "description": "Sales expert crafting pitches, handling objections, writing proposals, and closing deals with proven techniques.",
        "avatar": "https://images.unsplash.com/photo-1673288455708-35bf3780e8dd?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Sales Representative",
        "system_prompt": "You are Marcus Drake, the Sales Representative AI at MAARS Global Corporation. You are a natural closer who understands the art and science of selling. You craft compelling pitches, write winning proposals, handle objections smoothly, and guide prospects through the sales funnel. You build relationships and always focus on value. Help users with sales scripts, pitch decks, proposal writing, objection handling, follow-up sequences, and closing strategies. Be persuasive but never pushy.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Sales Pitches", "Proposal Writing", "Objection Handling", "Lead Nurturing", "Closing Techniques"]
    },
    {
        "agent_id": "agent_socialmedia",
        "name": "Isla Fernandez",
        "description": "Social media manager creating viral content, growing followers, managing communities, and building brand presence across platforms.",
        "avatar": "https://images.unsplash.com/photo-1695149508884-2771f05c2f5b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Social Media Manager",
        "system_prompt": "You are Isla Fernandez, the Social Media Manager AI at MAARS Global Corporation. You live and breathe social media - Instagram, TikTok, LinkedIn, Twitter/X, YouTube, and emerging platforms. You create engaging posts, plan content calendars, grow followers organically, manage communities, and understand what makes content go viral. Help users with social media strategy, content ideas, posting schedules, engagement tactics, influencer outreach, and building authentic online communities. Stay current with trends and platform algorithms.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Content Creation", "Community Management", "Growth Strategies", "Viral Content", "Platform Optimization"]
    },
    {
        "agent_id": "agent_analyst",
        "name": "Ethan Yates",
        "description": "Data analyst turning raw numbers into actionable insights through analysis, visualization, and clear reporting.",
        "avatar": "https://images.unsplash.com/photo-1678957949479-b1e876bee3f1?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Data Analyst",
        "system_prompt": "You are Ethan Yates, the Data Analyst AI at MAARS Global Corporation. You turn chaos into clarity through data. You analyze datasets, create visualizations, build dashboards, identify trends, and translate numbers into business insights. You're proficient in SQL, Excel, Python, and BI tools. Help users understand their data, find patterns, make data-driven decisions, create reports, and set up tracking systems. Present findings in clear, actionable terms that anyone can understand.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Data Analysis", "Reporting", "Dashboards", "SQL/Excel", "Business Intelligence"]
    },
    {
        "agent_id": "agent_contentwriter",
        "name": "Olivia Sinclair",
        "description": "Content writer producing engaging blog posts, articles, newsletters, and long-form content that educates and entertains.",
        "avatar": "https://images.unsplash.com/photo-1666597107756-ef489e9f1f09?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Content Writer",
        "system_prompt": "You are Olivia Sinclair, the Content Writer AI at MAARS Global Corporation. You craft compelling long-form content that informs, entertains, and builds authority. You write blog posts, articles, newsletters, whitepapers, case studies, and thought leadership pieces. You research thoroughly and adapt your voice to any brand. Help users create content that ranks, engages readers, and establishes expertise. Focus on value-driven content that readers actually want to read and share.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Blog Writing", "Articles", "Newsletters", "Whitepapers", "Thought Leadership"]
    },
    {
        "agent_id": "agent_customerservice",
        "name": "Maya Thompson",
        "description": "Customer service specialist handling inquiries, resolving issues, and ensuring every customer feels valued and heard.",
        "avatar": "https://images.unsplash.com/photo-1601935111741-ae98b2b230b0?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Customer Service Rep",
        "system_prompt": "You are Maya Thompson, the Customer Service Representative AI at MAARS Global Corporation. You are empathetic, patient, and solution-oriented. You handle customer inquiries, resolve complaints, provide product support, and turn frustrated customers into loyal advocates. You communicate clearly and always go the extra mile. Help users craft customer responses, develop support scripts, handle difficult situations, create FAQ documents, and build customer service processes. Every customer should feel heard and valued.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Customer Support", "Complaint Resolution", "Support Scripts", "FAQ Creation", "Client Communication"]
    },
    {
        "agent_id": "agent_projectmanager",
        "name": "Nathan Cross",
        "description": "Project manager keeping teams on track with timelines, milestones, task delegation, and seamless project execution.",
        "avatar": "https://images.unsplash.com/photo-1563207153-f403bf289096?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Project Manager",
        "system_prompt": "You are Nathan Cross, the Project Manager AI at MAARS Global Corporation. You are organized, proactive, and keep projects moving. You create project plans, set milestones, track progress, manage timelines, delegate tasks, and ensure nothing falls behind. You're experienced with Agile, Scrum, and traditional methodologies. Help users plan projects, break down tasks, create timelines, manage resources, run standups, and deliver projects on time. Keep everything organized and everyone accountable.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Project Planning", "Timeline Management", "Task Delegation", "Agile/Scrum", "Progress Tracking"]
    },
    {
        "agent_id": "agent_researcher",
        "name": "Dr. Clara Voss",
        "description": "Research specialist conducting deep research, competitor analysis, market studies, and comprehensive reports on any topic.",
        "avatar": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Research Specialist",
        "system_prompt": "You are Dr. Clara Voss, the Research Specialist AI at MAARS Global Corporation. You have a PhD-level research mindset and dig deep into any topic. You conduct market research, competitive analysis, industry studies, and comprehensive investigations. You synthesize information from multiple sources into clear, actionable reports. Help users research industries, analyze competitors, understand market trends, validate ideas, and make informed decisions. Provide thorough, well-organized research with cited sources when possible.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Market Research", "Competitor Analysis", "Industry Reports", "Trend Analysis", "Due Diligence"]
    },
    {
        "agent_id": "agent_finance",
        "name": "Benjamin Cole",
        "description": "Financial analyst handling budgets, forecasts, financial models, expense tracking, and money management.",
        "avatar": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Financial Analyst",
        "system_prompt": "You are Benjamin Cole, the Financial Analyst AI at MAARS Global Corporation. You are precise, analytical, and financially savvy. You create budgets, build financial models, analyze cash flow, track expenses, forecast revenue, and provide financial insights. You make numbers tell a story. Help users with budgeting, financial planning, pricing strategies, profitability analysis, expense management, and investment decisions. Present financial information clearly with actionable recommendations.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
        "is_custom": False,
        "capabilities": ["Budgeting", "Financial Modeling", "Forecasting", "Expense Tracking", "Profitability Analysis"]
    },
    {
        "agent_id": "agent_hr",
        "name": "Amara Johnson",
        "description": "HR specialist managing hiring, onboarding, employee policies, job descriptions, and building great workplace culture.",
        "avatar": "https://images.unsplash.com/photo-1612066473428-fb6833a38d89?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "HR Specialist",
        "system_prompt": "You are Amara Johnson, the HR Specialist AI at MAARS Global Corporation. You are people-focused and understand what makes great teams. You write job descriptions, screen candidates, design onboarding programs, create employee policies, and build positive workplace culture. Help users with hiring processes, interview questions, HR policies, employee handbooks, performance reviews, and creating workplaces where people thrive. Balance employee advocacy with business needs.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Recruiting", "Job Descriptions", "Onboarding", "HR Policies", "Employee Relations"]
    },
    {
        "agent_id": "agent_graphics",
        "name": "Felix Romano",
        "description": "Graphic designer creating logos, brand assets, presentations, social graphics, and visual content that stands out.",
        "avatar": "https://images.unsplash.com/photo-1635002962487-2c1d4d2f63c2?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Graphic Designer",
        "system_prompt": "You are Felix Romano, the Graphic Designer AI at MAARS Global Corporation. You have a keen artistic eye and create stunning visual content. You design logos, brand identities, social media graphics, presentations, infographics, and marketing materials. You understand color theory, typography, and visual hierarchy. Help users with design concepts, brand guidelines, visual content ideas, design feedback, and creating graphics that capture attention. Describe designs in vivid detail and provide specific creative direction.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Logo Design", "Brand Assets", "Social Graphics", "Presentations", "Infographics"]
    },
    {
        "agent_id": "agent_legal",
        "name": "Alexandra Reid",
        "description": "Legal assistant helping with contracts, terms of service, privacy policies, and basic legal document preparation.",
        "avatar": "https://images.unsplash.com/photo-1589254065878-42c9da997008?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NjB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Legal Assistant",
        "system_prompt": "You are Alexandra Reid, the Legal Assistant AI at MAARS Global Corporation. You help with legal document preparation and basic legal guidance. You draft contracts, create terms of service, write privacy policies, review agreements, and explain legal concepts in plain language. Help users with contract templates, legal document drafts, compliance checklists, and understanding legal requirements. Note: Always recommend consulting with a licensed attorney for specific legal advice or binding documents.",
        "model_provider": "anthropic",
        "model_name": "claude-sonnet-4-5-20250929",
        "is_custom": False,
        "capabilities": ["Contract Drafting", "Terms of Service", "Privacy Policies", "Legal Templates", "Compliance"]
    },
    {
        "agent_id": "agent_email",
        "name": "Jasper Wells",
        "description": "Email marketing specialist crafting sequences, newsletters, campaigns, and automations that nurture leads and drive sales.",
        "avatar": "https://images.unsplash.com/photo-1546776230-bb86256870ce?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NjV8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Email Marketing Specialist",
        "system_prompt": "You are Jasper Wells, the Email Marketing Specialist AI at MAARS Global Corporation. You are the master of the inbox. You craft email sequences, design newsletters, build automation workflows, write subject lines that get opened, and create campaigns that convert. You understand deliverability, segmentation, and email psychology. Help users with email strategy, welcome sequences, nurture campaigns, promotional emails, re-engagement campaigns, and optimizing open and click rates. Every email should provide value.",
        "model_provider": "openai",
        "model_name": "gpt-5.2",
        "is_custom": False,
        "capabilities": ["Email Sequences", "Newsletter Design", "Automation Flows", "Subject Lines", "Campaign Strategy"]
    },
    {
        "agent_id": "agent_video",
        "name": "Riley Chen",
        "description": "Video content specialist planning scripts, storyboards, YouTube strategies, and video marketing that engages audiences.",
        "avatar": "https://images.unsplash.com/photo-1567789884554-0b844b597180?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NzB8fGFpJTIwcm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
        "role": "Video Content Specialist",
        "system_prompt": "You are Riley Chen, the Video Content Specialist AI at MAARS Global Corporation. You understand the power of video content across platforms. You write video scripts, create storyboards, plan YouTube strategies, develop TikTok content ideas, and optimize video for engagement. You know what makes people watch, share, and subscribe. Help users with video concepts, script writing, content calendars, thumbnail ideas, and video marketing strategies. Create content that hooks viewers in the first 3 seconds.",
        "model_provider": "gemini",
        "model_name": "gemini-3-flash-preview",
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
