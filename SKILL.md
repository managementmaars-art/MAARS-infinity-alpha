---
name: MAARS-Command
description: MAARS Infinity — Autonomous AI Enterprise Operating System. Full-stack multi-agent orchestration platform with 458+ agents across 28 networks, 13 LLM providers, governance engine, memory systems, verification layer, real-time collaboration, and enterprise control surface. FastAPI backend + React frontend.
---

# MAARS Command — Autonomous AI Enterprise Operating System

MAARS Infinity is a production-grade, full-stack AI operations platform built for autonomous multi-agent execution at enterprise scale. It combines a React frontend with a FastAPI backend, supporting 458+ specialized agents across 28 agent networks, 13 LLM providers, and a governed execution runtime with memory, verification, and observability built in.

## When to Use

Activate this skill when:
- Building, extending, or debugging any part of the MAARS Infinity platform
- Working on multi-agent orchestration, task graphs, or agent networks
- Implementing LLM routing, fallback logic, or provider integrations
- Adding new API routes, services, or frontend pages
- Working on governance, approvals, circuit breakers, or policy engine
- Integrating external services (email, calendar, Stripe, OAuth, web search, social media)
- Implementing memory systems, RAG, knowledge graphs, or verification layers
- Deploying, configuring, or troubleshooting the stack

## Architecture Overview

### Stack
- **Backend:** FastAPI + Motor (async MongoDB) — `backend/`
- **Frontend:** React 19 + CRACO + Tailwind CSS + Radix UI — `frontend/`
- **Database:** MongoDB 5.0+
- **Auth:** JWT + HTTP-only session cookies + OAuth 2.0
- **Real-time:** WebSocket (`/api/ws`, `/api/infinity-ws`)
- **Runtime:** `http://localhost:8000` (backend), `http://localhost:3000` (frontend)

### Backend Structure (`backend/`)

```
server.py              — FastAPI entry point, route registration, startup seeding
config.py              — Agent catalog, system prompts, tool definitions, brain profiles
infinity_catalog.py    — Infinity catalog, network helpers, system prompts
db.py                  — MongoDB connection (Motor async driver)
auth.py                — JWT + session auth, role guards

routes/                — API endpoint handlers
  auth.py              — Registration, login, JWT, OAuth callbacks
  agents.py            — Agent CRUD, configuration, execution
  chats.py             — Chat history, LLM calls, tool execution, RAG, credits
  tasks.py             — Task creation, orchestration, execution logs
  teams.py             — Multi-user collaboration, team management
  subscriptions.py     — Billing, credits, usage tracking
  approvals.py         — Governance, approval workflows
  admin.py             — System administration, policy management
  admin_code.py        — Code-level admin controls
  agent_teams.py       — Agent team composition and routing
  actions.py           — Agentic action execution
  content.py           — Content generation pipelines
  enterprise.py        — Enterprise-tier features
  generation.py        — Media and document generation
  infinity_routes.py   — Infinity network API
  infinity_ws.py       — Infinity WebSocket
  kernel.py            — Kernel execution controls
  knowledge.py         — Knowledge operations
  knowledge_base.py    — RAG document ingestion and retrieval
  media.py             — Image, video, audio handling
  memory.py            — Memory system API
  notifications_routes.py — Notification delivery
  products.py          — Product catalog
  projects.py          — Project management
  social_media.py      — Social media integrations
  summary.py           — Summarization endpoints
  universal.py         — Universal gateway
  user.py              — User profile management
  v1_gateway.py        — V1 API compatibility gateway
  vibe_coding.py       — Vibe coding environment
  voice.py             — Voice/speech features
  websocket.py         — Real-time WebSocket hub
  workspace.py         — Workspace management

services/              — Business logic and orchestration layer
kernel/                — Runtime execution engine
governance/            — Policy engine, circuit breakers, audit logs
orchestrator/          — Task graph execution, DAG resolution
router/                — LLM routing, cost optimization, fallback logic
memory_system/         — Short/long-term, episodic, semantic memory
verification/          — Fact-checking, hallucination detection, code validation
runtime/               — Execution runtime
intelligence/          — Intelligence layer
portfolio/             — Venture portfolio management
```

### Frontend Structure (`frontend/src/`)

```
App.js                  — Main router, auth state, protected routes

pages/
  LandingPage.jsx        — Marketing and onboarding entry
  LoginPage.jsx          — Authentication
  RegisterPage.jsx       — User registration
  OnboardingFlow.jsx     — New user onboarding
  Dashboard.jsx          — Main command dashboard
  CommanderOrion.jsx     — Primary agent commander interface
  AgentChat.jsx          — Individual agent conversation UI
  Agents.jsx             — Agent management list
  AgentCatalog.jsx       — Browse 458+ agent catalog
  AgentNetworks.jsx      — 28 agent network management
  AgentSuggestions.jsx   — AI-powered agent recommendations
  CreateAgent.jsx        — Agent creation wizard
  Tasks.jsx              — Task management and tracking
  TaskGraphs.jsx         — DAG task graph visualization
  WorkflowBuilder.jsx    — Visual workflow composition
  Team.jsx               — Team management
  TeamBuilder.jsx        — Team composition
  CollaborationEngine.jsx — Real-time collaboration
  Projects.jsx           — Project management
  KnowledgeBaseTab.jsx   — RAG knowledge management
  KnowledgeGraph.jsx     — Knowledge graph visualization
  MemoryHierarchy.jsx    — Memory system hierarchy view
  MemoryGovernance.jsx   — Memory policy management
  ModelRouterDashboard.jsx — LLM routing configuration
  BrainProfiles.jsx      — Agent brain profile management
  WorkspaceBrain.jsx     — Workspace-level intelligence
  AdminDashboard.jsx     — System administration
  AdminPages.jsx         — Admin control pages
  AnalyticsDashboard.jsx — Usage and performance analytics
  AnalyticsTab.jsx       — Analytics tab component
  KPIDashboard.jsx       — KPI metrics dashboard
  ObservabilityDashboard.jsx — System observability
  ActivityMonitor.jsx    — Real-time activity monitoring
  InsightsPage.jsx       — AI-powered insights
  CostGovernance.jsx     — Cost tracking and limits
  CircuitBreakers.jsx    — Fault tolerance controls
  Approvals.jsx          — Approval workflow management
  TrustScores.jsx        — Agent trust scoring
  RBAC.jsx               — Role-based access control
  Environments.jsx       — Environment management
  ExecutionGateway.jsx   — Execution control gateway
  KernelDashboard.jsx    — Kernel runtime monitoring
  IntegrationHub.jsx     — External service integrations
  ContentGenerator.jsx   — AI content generation
  CampaignBuilder.jsx    — Marketing campaign tools
  SocialMediaCommand.jsx — Social media automation
  VibeCoding.jsx         — AI-assisted coding environment
  CodeExplorer.jsx       — Codebase exploration
  DeveloperPortal.jsx    — Developer tools and API docs
  VenturePortfolio.jsx   — Portfolio management
  ProductCatalog.jsx     — Product management
  Organization.jsx       — Org structure management
  ReferenceIntelligence.jsx — Reference data intelligence
  BrandingTab.jsx        — Brand configuration
  SmtpConfigTab.jsx      — Email (SMTP) configuration
  UniversalKeyPage.jsx   — Universal API key management
  Settings.jsx           — User and system settings
  PricingPage.jsx        — Subscription pricing
  PricingAdmin.jsx       — Pricing administration
  PaymentSuccess.jsx     — Payment confirmation
  OperatorControlPanel.jsx — Operator-level controls
  AboutPage.jsx          — About and platform info
```

## Core Capabilities

### Multi-Agent Orchestration
- **458+ specialized agents** across 28 agent networks
- **Commander Orion** as the primary orchestration agent
- DAG-based task decomposition with parallel execution
- Agent delegation, handoff, and team routing
- Brain profiles configurable per agent

### LLM Routing & Providers
- 13 LLM providers: OpenAI, Anthropic, Google Gemini, Groq, Cohere, Mistral, DeepSeek, xAI, Perplexity, MiniMax, Together, Fireworks, and more
- Intelligent routing with cost optimization
- Automatic fallback on failure
- Token budget management and context window awareness

### Memory Systems
- Short-term (in-context), working, long-term (MongoDB), episodic, semantic
- Knowledge graph integration
- Memory governance policies
- RAG (Retrieval-Augmented Generation) with document ingestion

### Governance & Safety
- Policy engine with configurable approval gates
- Circuit breakers for fault tolerance
- Audit logs for all administrative actions
- Trust scoring per agent
- RBAC (Role-Based Access Control)
- Hallucination detection and fact verification

### Integrations
- **Email:** SMTP (Gmail, custom)
- **OAuth:** Google, extensible
- **Payments:** Stripe (subscriptions, credits)
- **Calendar:** Google Calendar, Microsoft Calendar
- **Web Search:** DuckDuckGo, Serper, Bright Data
- **Social Media:** Twitter/X, LinkedIn, WeChat, Xiaohongshu
- **Voice/Speech:** ElevenLabs TTS, Whisper STT
- **AI Media:** Image/video generation pipelines
- **Documents:** PDF, PPTX, DOCX generation

### Observability
- Real-time activity monitoring via WebSocket
- Cost tracking and governance dashboards
- Execution trace logs
- KPI and analytics dashboards
- Incident detection and management

## API Endpoints

All prefixed with `/api`:

| Route | Purpose |
|-------|---------|
| `GET /api/health` | Health check |
| `/api/auth/*` | Registration, login, JWT, OAuth |
| `/api/agents/*` | Agent CRUD, execution, configuration |
| `/api/chats/*` | Chat, LLM calls, tool use, RAG |
| `/api/tasks/*` | Task orchestration and logs |
| `/api/teams/*` | Team management and collaboration |
| `/api/subscriptions/*` | Billing, credits, usage |
| `/api/approvals/*` | Governance workflows |
| `/api/knowledge-base/*` | Document ingestion, RAG retrieval |
| `/api/admin/*` | System administration |
| `/api/memory/*` | Memory system operations |
| `/api/kernel/*` | Kernel runtime controls |
| `/api/projects/*` | Project management |
| `/api/workspace/*` | Workspace operations |
| `/api/content/*` | Content generation |
| `/api/generation/*` | Media and document generation |
| `/api/social-media/*` | Social media operations |
| `/api/voice/*` | Voice and speech |
| `/api/enterprise/*` | Enterprise features |
| `/api/ws` | WebSocket real-time hub |
| `/api/docs` | Swagger API explorer |

## Instructions for Development

### Adding a New API Route
1. Create `backend/routes/new_route.py` with a FastAPI `APIRouter`
2. Add business logic to `backend/services/`
3. Register the router in `backend/server.py` under `api_router`
4. Add MongoDB indexes in the startup block if needed
5. Mirror frontend access in the appropriate page under `frontend/src/pages/`

### Adding a New Agent
1. Define agent config in `backend/config.py` (name, description, tools, system prompt)
2. Add to the appropriate network in `backend/infinity_catalog.py`
3. Seed via `backend/services/agent_service.py`
4. Ensure the agent appears in `AgentCatalog.jsx` and `AgentNetworks.jsx`

### Adding a New Frontend Page
1. Create `frontend/src/pages/NewPage.jsx`
2. Register the route in `frontend/src/App.js` with role protection if needed
3. Add navigation entry to the sidebar/nav components

### LLM Call Pattern
All LLM calls go through `routes/chats.py` → `services/` → `router/` for routing, cost check, credit deduction, tool execution, and logging.

### Environment Variables Required
```bash
# Required
MONGO_URL=mongodb://localhost:27017
DB_NAME=maars_infinity
JWT_SECRET=<32+ char secret>

# LLM (at least one)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
COHERE_API_KEY=

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Integrations (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=
SMTP_PASSWORD=
STRIPE_API_KEY=
DUCKDUCKGO_ENABLED=true
SERPER_API_KEY=
ELEVENLABS_API_KEY=

# CORS
CORS_ORIGINS=http://localhost:3000
```

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm install --legacy-peer-deps
node_modules/.bin/craco.cmd start
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Design System

- **Theme:** Dark-mode cyber-professional
- **Colors:** Deep blues, purples, cyan accents
- **Components:** Radix UI primitives + custom Tailwind variants
- **Typography:** Inter, JetBrains Mono, Outfit
- **Icons:** Lucide React
- **Charts:** Recharts
- **3D:** React Three Fiber + Drei + Rapier
- **Animations:** GSAP, Tailwind animate
- **Forms:** React Hook Form + Zod validation

## Key Design Principles

1. **Agent-first:** All operations are modeled as agent tasks with delegation, logging, and governance
2. **Service-oriented:** Business logic lives in `services/` and `kernel/`, not route handlers
3. **Credit-aware:** All LLM calls check and deduct credits; respect subscription limits
4. **Audit everything:** Administrative actions, LLM calls, tool executions all produce audit logs
5. **Fail safely:** Circuit breakers and fallback logic prevent cascading failures
6. **Memory-persistent:** Agents maintain context across sessions via the memory system
