"""Pydantic models for MAARS Command API."""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=64)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

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
    avatar: str = ""
    role: str
    system_prompt: str = ""
    model_provider: str = "openai"
    model_name: str = "gpt-5.2"
    is_custom: bool = False
    is_commander: bool = False
    is_infinity: bool = False
    network: Optional[str] = None
    autonomy_tier: int = 1
    authority_tier: str = "department"
    lifecycle_state: str = "active"
    sector: Optional[str] = None
    creator_id: Optional[str] = None
    capabilities: List[str] = []
    tools: List[str] = []
    created_at: Optional[datetime] = None

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1, max_length=2_000)
    avatar: Optional[str] = Field(None, max_length=2_048)
    role: str = Field(..., min_length=1, max_length=128)
    system_prompt: str = Field(..., min_length=1, max_length=32_000)
    model_provider: str = Field("openai", max_length=64)
    model_name: str = Field("gpt-5.2", max_length=128)
    capabilities: List[str] = Field(default_factory=list, max_length=50)

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
    content: str = Field(..., min_length=1, max_length=32_000)
    model_provider: Optional[str] = Field(None, max_length=64)
    model_name: Optional[str] = Field(None, max_length=128)
    quality_tier: Optional[str] = Field(None, pattern=r"^(economy|standard|premium|auto)?$")
    task_hint: Optional[str] = Field(None, pattern=r"^(code|math|reasoning|creative|translation|summary|research|data|chat|auto)?$")
    attachments: Optional[List[str]] = Field(None, max_length=10)
    attachment_files: Optional[List[dict]] = Field(None, max_length=10)

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
    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(..., min_length=1, max_length=8_000)
    priority: str = Field("medium", pattern=r"^(low|medium|high|critical)$")
    assigned_agents: List[str] = Field(default_factory=list, max_length=20)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, min_length=1, max_length=8_000)
    status: Optional[str] = Field(None, pattern=r"^(pending|in_progress|completed|failed|cancelled)?$")
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|critical)?$")
    assigned_agents: Optional[List[str]] = Field(None, max_length=20)

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
    goal: str = Field(..., min_length=1, max_length=4_000)
    execution_mode: str = Field("approval", pattern=r"^(draft|approval|autonomous)$")
    priority: str = Field("high", pattern=r"^(low|medium|high|critical)$")

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    execution_mode: Optional[str] = None
    priority: Optional[str] = None

class AutonomySettings(BaseModel):
    autonomy_level: str = "approval"  # manual, approval, autonomous
