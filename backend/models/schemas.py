"""Pydantic models for MAARS Command API."""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


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
    is_commander: bool = False
    creator_id: Optional[str] = None
    capabilities: List[str] = []
    tools: List[str] = []
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
    role: str
    content: str
    created_at: datetime
    execution_steps: Optional[List[dict]] = None
    generated_image: Optional[dict] = None
    generated_video: Optional[dict] = None
    generated_file: Optional[dict] = None
    video_generating: Optional[bool] = None
    video_error: Optional[str] = None
    model_used: Optional[str] = None
    auto_selected: Optional[bool] = None
    model_reason: Optional[str] = None
    attachments: Optional[List[str]] = None
    delegation_data: Optional[dict] = None
    # Feedback fields for agent performance scoring
    feedback: Optional[str] = None  # "up", "down", or None
    feedback_at: Optional[str] = None  # ISO timestamp
    feedback_by: Optional[str] = None  # user_id who gave feedback

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
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    attachments: Optional[List[str]] = None
    attachment_files: Optional[List[dict]] = None

class SubscriptionCreate(BaseModel):
    plan_id: str

class CreditPurchase(BaseModel):
    package_id: str

class CheckoutRequest(BaseModel):
    type: str
    plan_id: Optional[str] = None
    package_id: Optional[str] = None
    origin_url: str
    currency: str = "usd"

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task_id: str
    user_id: str
    title: str
    description: str
    status: str = "pending"
    priority: str = "medium"
    assigned_agents: List[str] = []
    result: Optional[str] = None
    source: str = "manual"
    source_goal: Optional[str] = None
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

class TeamCreate(BaseModel):
    name: str

class TeamInvite(BaseModel):
    email: str
    role: str = "member"

class TeamMemberUpdate(BaseModel):
    role: str


# ============== PROJECT / WORKFLOW MODELS ==============

class MilestoneCreate(BaseModel):
    title: str
    description: str = ""

class ProjectCreate(BaseModel):
    goal: str
    execution_mode: str = "approval"  # draft, approval, autonomous
    priority: str = "high"

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    execution_mode: Optional[str] = None
    priority: Optional[str] = None

class AutonomySettings(BaseModel):
    autonomy_level: str = "approval"  # manual, approval, autonomous
