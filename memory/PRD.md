# MAARS Command by MAARS Global Corporation — PRD

## Original Problem Statement
Build "MAARS Command," a commercial, production-ready AI business operating system that merges the capabilities of Sintra.ai (preset specialist business agents) and Emergent.sh (autonomous execution, memory, tool use, and app building). The system must be an "Autonomous AI Workforce Operating System" with multi-agent collaboration, real-world action execution, persistent memory, and enterprise-grade features.

## Core Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI, CORS, MongoDB indexes for 10+ collections)
│   ├── config.py (41 agents, tools, brain profiles, tool maps)
│   ├── services/
│   │   ├── agent_service.py (Execution, brain context, workspace context, simulation mode, tool logging)
│   │   ├── orchestration_service.py (Goal decomposition, project execution, media gen, collaboration logging, Secretary handoff)
│   │   └── cache_service.py (Redis caching)
│   ├── routes/
│   │   ├── enterprise.py (Collaboration Engine, KPI Framework, System Mode, Cost Governance, Quality Control)
│   │   ├── agents.py (CRUD + Custom Brain Profiles)
│   │   ├── projects.py, workspace.py, approvals.py, chats.py, admin.py, tasks.py, products.py, teams.py, insights.py, settings.py
│   └── shared/, models/
└── frontend/
    └── src/
        ├── App.js (Router, auth, 15+ routes)
        ├── pages/ (Dashboard, AgentChat, Projects, ProjectDetail, BrainProfiles, KPIDashboard, CollaborationEngine, Approvals, WorkspaceBrain, Agents, Tasks, Team, Products, Settings, InsightsPage, AdminDashboard, LandingPage)
        └── components/ (DashboardLayout, ProjectsLayout, CommandCenter, BrandFooter, UI components)
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
- **13 NEW Agents (41 total):** Chief Strategy Officer (Cassandra Steele), Investor Relations (Richard Ashworth), Product Manager (Priya Kapoor), Data Engineer (Nikolai Volkov), Brand Architect (Valentina Cruz), UX Researcher (Yuki Tanaka), 3D Visualization Specialist (Marco De Luca), PR Manager (Catherine Blake), Procurement Manager (Arjun Mehta), CX Architect (Sofia Reyes), Ethics Officer (Prof. James Whitfield), Knowledge Architect (Dr. Eleanor Shaw), Localization Specialist (Layla Mansouri)
- **Collaboration Engine:** Inter-agent messaging with structured schema (sender, receivers, objective, context, risk level, dependencies, status). Auto-logged during project task execution. Frontend at /collaborations with status filters.
- **KPI Command Center:** Real-time dashboard aggregating operational (projects, tasks, chats), governance (approvals, tool calls, risk incidents), and cost metrics. Custom KPI creation with targets and progress tracking. Frontend at /kpi-dashboard.
- **System Mode Toggle:** Simulation (blocks real-world API calls) vs Execution (live). Persists per user. Enforced in tool execution layer.
- **Cost Governance:** Per-agent cost breakdown, budget caps (monthly cap + alert threshold). API endpoints for monitoring and configuration.
- **Quality Control Protocol:** Quality review records for agent outputs (self-check, peer review, compliance). API for creation and listing.
- **Enhanced Autonomy Enforcement:** Simulation mode blocks send_email, send_gmail, send_sms, send_slack, schedule_meeting, google_calendar, github_action in non-execution mode.

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
agents, agent_brains, projects, workspace_brain, tool_calls, approvals, collaborations, kpi_store, quality_reviews, system_config, chats, tasks, products, teams, transactions, users

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
- `/api/projects`, `/api/workspace`, `/api/approvals`

## Prioritized Backlog

### P1 — High Priority
- **Real-World Action Layer**: Wire agents to actually execute external API calls (Gmail, Calendar, social posting)
- **"Vibe Coding" App Builder**: Chat-based full-stack app building with GitHub integration
- **Universal Reference Intelligence**: Image analysis, brand detection, style blueprints

### P2 — Medium Priority
- **Model-Agnostic LLM Router**: Dynamic model selection based on task complexity/cost/privacy
- **Memory Governance**: Versioning, tenant isolation, pruning, relevance scoring
- **Failure Recovery Protocol**: Auto-retry, fallback models, escalation chain
- **Advanced Integrations**: WhatsApp, Meta Ads, TikTok Ads, Google Ads, Shopify, ERP

### P3 — Future
- Real-time agent activity visualizer, Workflow builder UI
- Custom agent creation by users, Multi-tenant isolation
- Enterprise org chart visualization, Architecture diagrams
- QR/Barcode generation for Inventory Manager

## Testing
- Iteration 53: 100% pass rate — 26/26 backend, all frontend passed
- Iteration 52: 100% — 20/20 backend, all frontend passed
- Admin: management.maars@marsgc.net / admin123
