# MAARS Command by MAARS Global Corporation — PRD

## Original Problem Statement
Build "MAARS Command," a commercial, production-ready AI business operating system that merges the capabilities of Sintra.ai (preset specialist business agents) and Emergent.sh (autonomous execution, memory, tool use, and app building). The system must be an "Autonomous AI Workforce Operating System" with multi-agent collaboration, real-world action execution, persistent memory, and enterprise-grade features.

## User Personas
- **Business Executive**: Uses Commander to delegate high-level goals, monitors projects, reviews deliverables
- **Team Lead**: Manages agents, configures brain profiles, reviews approval workflows
- **Admin**: Configures pricing, manages users, views analytics and audit logs

## Core Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI app, CORS, startup, MongoDB indexes)
│   ├── config.py (28 agents, tools, brain profiles, tool maps)
│   ├── db.py (MongoDB connection)
│   ├── auth.py (JWT authentication)
│   ├── models/schemas.py (Pydantic models)
│   ├── services/
│   │   ├── agent_service.py (Agent execution, brain context, workspace context, tool logging)
│   │   ├── orchestration_service.py (Goal decomposition, project execution, media generation, Commander→Secretary handoff)
│   │   └── cache_service.py (Redis caching)
│   ├── routes/ (agents, chats, projects, workspace, approvals, admin, tasks, products, teams, insights, settings)
│   └── shared/ (utils, notifications)
└── frontend/
    └── src/
        ├── App.js (Router, auth context, API URL)
        ├── pages/ (Dashboard, AgentChat, Projects, ProjectDetail, BrainProfiles, Approvals, WorkspaceBrain, AdminDashboard, Settings, Tasks, Team, Products, Insights)
        └── components/ (CommandCenter, ProjectsLayout, BrandFooter, admin wizards, UI components)
```

## What's Been Implemented

### Phase 1 — Foundation (Previous sessions)
- 21 preset AI agents with distinct personalities, roles, system prompts
- Multi-provider LLM support via Emergent LLM Key (OpenAI, Gemini, Claude)
- Credit-based billing system with Stripe integration
- Full admin panel with analytics (leaderboards, engagement heatmaps)
- RAG knowledge base for agent context
- Web browsing, image analysis, document tools
- Product catalog with batch import
- Team collaboration with notifications and activity feed

### Phase 2 — Autonomous Orchestration (Previous session)
- Orchestration Engine: Goal → structured plan → milestones → tasks → auto-execution
- Executive Command Dashboard with project overview
- Workspace Brain: Persistent business context injected into all agent prompts
- Approval Workflows for gating sensitive agent actions
- Tool Call Observability: All agent tool calls logged for audit
- Performance: API pagination + Redis caching

### Phase 3 — Custom Brain Profiles & Agent Expansion (March 2, 2026)
- **7 New Agent Roles**: Cybersecurity Officer (Damien Voss), Automation Engineer (Serena Okafor), Growth Hacker (Axel Brennan), Compliance Officer (Victoria Harrington), AI Optimization Specialist (Dr. Luca Bernstein), Operations Manager (Diana Morales), Revenue Optimization Strategist (Maximilian Wolfe) — all with unique AI-generated avatars
- **Custom Brain Profiles (MANDATORY per spec)**: Each agent has an isolated brain config with:
  - Primary/fallback models
  - Memory scopes (Working, Long-Term, Domain, Shared)
  - Autonomy level (0-5 slider)
  - Approval requirements
  - Output templates
  - KPIs
  - Escalation rules
  - Communication style
  - Risk boundaries (budget authority, external comms approval)
- **Brain Profiles UI**: Full management page at /brain-profiles with search, agent cards showing autonomy/approval status, and full brain editor
- **Enhanced Agent Prompts**: Legal Assistant (country-specific law, business-favorable contracts), Social Media Manager (geographic boost, platform selection, scheduling), Sales (multi-channel outreach), Customer Service (multi-channel communication), Personal Secretary (Commander handoff, execution protocols)
- **Commander → Personal Secretary Handoff**: Auto-creates secretary tasks with project deliverables when Commander completes a project
- **Media Deliverable Rendering**: Project results can now display generated images and videos inline with dedicated media viewers
- **Brain Context Injection**: All agents receive their Custom Brain Profile context in their system prompts during execution

## Key DB Collections
- `agents` — Agent definitions (28 total)
- `agent_brains` — User-specific brain profile customizations (indexed: user_id + agent_id, unique)
- `projects` — Projects with milestones and tasks
- `workspace_brain` — Persistent business context per user
- `tool_calls` — Tool execution audit log
- `approvals` — Pending approval workflows
- `chats`, `tasks`, `products`, `teams`, `transactions`, `users`

## Key API Endpoints
- `GET /api/agents/public` — List all 28 agents
- `GET /api/agents/{id}/brain` — Get agent brain profile
- `PUT /api/agents/{id}/brain` — Update brain profile
- `DELETE /api/agents/{id}/brain` — Reset to defaults
- `GET /api/brain-profiles` — List all brain profiles
- `POST /api/projects` — Create project from goal
- `GET /api/projects/{id}` — Get project details
- `GET/PUT /api/workspace` — Workspace brain CRUD
- `GET/PUT /api/approvals` — Approval workflows

## Prioritized Backlog

### P0 — Critical
- None currently blocked

### P1 — High Priority
- **Real-World Action Layer**: Wire agents to actually execute external API calls (Gmail, Calendar, social media posting, messaging) through the approvals system
- **"Vibe Coding" App Builder**: Chat-based full-stack app building with GitHub integration

### P2 — Medium Priority
- **Model-Agnostic LLM Router**: Dynamic model selection based on task complexity, cost, privacy
- **Enterprise Features**: Granular RBAC, enhanced audit logs, custom agent builder framework
- **Advanced Integrations**: QuickBooks, CRMs, WhatsApp/Viber/Signal APIs, Meta Ads, TikTok Ads
- **Inventory Manager Enhancements**: QR/barcode generation, SKU tracking, cost/revenue/profit margins

### P3 — Future
- Real-time agent activity visualizer
- Workflow builder UI
- Custom agent creation by users
- Multi-tenant isolation
- Advanced analytics dashboards

## Testing
- Iteration 52: 100% pass rate — 20/20 backend tests, all frontend tests passed
- All previous iterations (5-8): Passed
- Admin credentials: management.maars@marsgc.net / admin123
