# MAARS Command by MAARS Global Corporation — PRD

## Original Problem Statement
Build "MAARS Command," a commercial, production-ready AI business operating system that merges the capabilities of Sintra.ai (preset specialist business agents) and Emergent.sh (autonomous execution, memory, tool use, and app building). The system must be an "Autonomous AI Workforce Operating System" with multi-agent collaboration, real-world action execution, persistent memory, and enterprise-grade features.

## Core Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI, CORS, MongoDB indexes for 15+ collections)
│   ├── config.py (41 agents, tools, brain profiles, tool maps)
│   ├── services/
│   │   ├── agent_service.py (Execution, brain context, workspace context, simulation mode, tool logging)
│   │   ├── orchestration_service.py (Goal decomposition, project execution, media gen, collaboration logging)
│   │   └── llm_service.py (LLM fallback chain)
│   ├── routes/
│   │   ├── enterprise.py (Collaboration, KPI, System Mode, Cost Governance, Quality Control, Activity Monitor, Reference Intelligence, LLM Config)
│   │   ├── vibe_coding.py (Vibe Coding App Builder - project CRUD + chat + preview)
│   │   ├── actions.py (Real-world actions: Google OAuth, Gmail, Calendar, integrations listing)
│   │   ├── agents.py (CRUD + Custom Brain Profiles)
│   │   └── auth.py, chats.py, projects.py, workspace.py, approvals.py, tasks.py, products.py, teams.py, admin.py, etc.
│   └── shared/, models/
└── frontend/
    └── src/
        ├── App.js (Router, auth, 18+ routes)
        ├── pages/ (Dashboard, AgentChat, Projects, BrainProfiles, KPIDashboard, CollaborationEngine, ActivityMonitor, VibeCoding, ReferenceIntelligence, Approvals, WorkspaceBrain, Agents, Tasks, Team, Products, Settings, InsightsPage, AdminDashboard, LandingPage)
        └── components/ (DashboardLayout with sidebar, ProjectsLayout, CommandCenter, BrandFooter, UI components)
```

## What's Been Implemented

### Phase 1 — Foundation
- Multi-provider LLM support via Emergent LLM Key
- Credit-based billing with Stripe, full admin panel, RAG knowledge base
- Web browsing, image analysis, document tools, product catalog, team collaboration

### Phase 2 — Autonomous Orchestration
- Orchestration Engine: Goal → plan → milestones → tasks → auto-execution
- Executive Command Dashboard, Workspace Brain, Approval Workflows
- Tool Call Observability, API pagination + Redis caching

### Phase 3 — Custom Brain Profiles & Agent Expansion (March 2, 2026)
- 7 new agents (28 total), Custom Brain Profiles system, enhanced prompts
- Commander → Personal Secretary handoff, media deliverable rendering
- Navigation fixes, consistent professional corporate avatars for all agents

### Phase 4 — Enterprise Operating System (March 3, 2026)
- 13 NEW Agents (41 total) across all organizational layers
- Collaboration Engine, KPI Command Center, System Mode Toggle
- Cost Governance, Quality Control Protocol

### Phase 5 — P0/P1 Features Complete (March 4, 2026)
- **Agent Activity Monitor**: Real-time dashboard at /activity-monitor showing agent workforce status, inter-agent communication flows, task dependency graph, and recent tool executions. Auto-refresh with live/paused toggle.
- **Vibe Coding App Builder**: Chat-based full-stack app generation at /vibe-coding. Creates single-page HTML/CSS/JS apps from text prompts using LLM. Supports iterative modifications via chat, live preview in iframe, code view, file download.
- **Universal Reference Intelligence**: Style Blueprint extraction at /reference-intelligence. Analyzes text (marketing copy, brand voice) and images (visual style, brand detection) using LLM. Creates structured style blueprints for content generation.
- **Flexible LLM Configuration**: Model-agnostic system supporting OpenAI (gpt-5.2, gpt-5.1, gpt-4.1, etc.), Anthropic (Claude Sonnet/Haiku), and Google Gemini (gemini-3-flash, gemini-2.5-pro). User-configurable in Settings.
- **Real-World Action Layer**: Google OAuth integration for Gmail/Calendar. Simulation mode gates all real-world actions. Integrations management in Settings with connect/disconnect UI.
- **Enhanced Settings**: LLM Model Configuration card (provider/model selection), Integrations & Actions card (Google Suite, system mode status).
- **Updated Navigation**: Sidebar includes Activity Monitor, Vibe Coding, Reference Intel links.

## 41 Agent Organizational Structure
**Executive:** Commander, Chief Strategy Officer, Revenue Strategist, Investor Relations
**Product & Technical:** Product Manager, App Developer, Automation Engineer, AI Optimizer, Data Engineer, Cybersecurity Officer
**Creative & Brand:** Brand Architect, Graphics Designer, Video Specialist, Copywriter, Web Designer, UX Researcher, 3D Specialist
**Growth & Marketing:** Marketing Specialist, Growth Hacker, SEO Specialist, Social Media Manager, Email Marketing, Sales Rep, PR Manager
**Operations:** Operations Manager, Inventory Manager, Procurement Manager, HR Specialist, Customer Service, CX Architect
**Finance:** Financial Analyst, Data Analyst
**Governance:** Legal Assistant, Compliance Officer, Ethics Officer
**Intelligence:** Research Specialist, Knowledge Architect, Localization Specialist, Personal Secretary

## Key DB Collections
agents, agent_brains, projects, workspace_brain, tool_calls, tool_logs, approvals, collaborations, kpi_store, quality_reviews, system_config, chats, tasks, products, teams, transactions, users, vibe_projects, reference_analyses, google_tokens, oauth_states

## Key API Endpoints
- `/api/agents/public` — 41 agents
- `/api/agents/{id}/brain` — CRUD brain profiles
- `/api/brain-profiles` — All 41 brain profiles
- `/api/collaborations` — Collaboration engine CRUD
- `/api/kpis` — KPI dashboard data
- `/api/kpis/custom` — Custom KPIs
- `/api/system/mode` — Simulation/Execution toggle
- `/api/cost-governance` — Cost tracking + budget caps
- `/api/quality-review(s)` — Quality control
- `/api/activity/live` — Real-time agent activity monitor
- `/api/reference/analyze` — Reference Intelligence analysis
- `/api/reference/history` — Analysis history
- `/api/llm/config` — LLM provider/model configuration (GET/PUT)
- `/api/vibe/projects` — Vibe Coding project CRUD
- `/api/vibe/projects/{id}/chat` — Vibe Coding chat modifications
- `/api/vibe/projects/{id}/preview` — Vibe project HTML preview
- `/api/actions/integrations` — List action integrations
- `/api/actions/send-email` — Send email (simulation/execution mode)
- `/api/actions/create-event` — Create calendar event (simulation/execution mode)
- `/api/oauth/gmail/status|login|callback|disconnect` — Google OAuth flow

## Prioritized Backlog

### P1 — High Priority
- **Collaboration Engine Autonomous Logic**: Agents autonomously initiate collaboration based on task dependencies
- **Quality Control & Failure Recovery**: Critic module, auto-retry, fallback models, escalation chain
- **Model-Agnostic LLM Router**: Dynamic model selection based on task complexity/cost/privacy

### P2 — Medium Priority
- **Memory Governance**: Versioning, tenant isolation, pruning, relevance scoring
- **Advanced Integrations**: WhatsApp, Meta Ads, TikTok Ads, Google Ads, Shopify, ERP
- **Enterprise RBAC System**: Granular role-based access control with permissions UI

### P3 — Future
- Real-time agent activity visualizer with WebSocket, Workflow builder UI
- Custom agent creation by users, Multi-tenant isolation
- Enterprise org chart visualization, Architecture diagrams
- QR/Barcode generation for Inventory Manager

## Testing
- Iteration 54: 100% pass rate — 20/20 backend, all frontend passed (Activity Monitor, Vibe Coding, Reference Intelligence, LLM Config, Actions Integrations)
- Iteration 53: 100% pass rate — 26/26 backend, all frontend passed
- Admin: management.maars@marsgc.net / admin123
