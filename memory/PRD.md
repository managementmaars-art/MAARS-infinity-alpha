# MAARS ∞ — Product Requirements Document

## Original Problem Statement
Build "MAARS Command by MAARS Global Corporation," a commercial, production-ready, autonomous multi-agent AI business operating system. The platform evolved into **MAARS ∞ (Infinity)** — a governed, hierarchical, multi-agent intelligence and execution architecture designed to convert high-level human intent into reliable, measurable, auditable, safe, and strategically useful execution.

## Core Architecture
- **458+ AI Agents** across **27 network categories**
- **16 system layers** from Human Governance to Infrastructure
- **6 Autonomy Tiers** (T0: Advisory → T5: Propose structural changes)
- **MAARS Kernel** with 15 subsystems
- **Execution Gateway** for governed action routing with cost metering
- **Knowledge Graph** for entity/relationship visualization
- **Trust Score System** for agent reliability metrics
- **Enterprise RBAC** with 4 roles and granular permissions
- **Circuit Breakers** for service protection
- **Cost Governance** with budget controls
- **Workflow Builder** for drag-and-drop agent orchestration

## Implementation History

### Phase 0 — Foundation (Previously Completed)
- 41 AI agents, Multi-LLM (9 providers, 30+ models), Voice, Google Suite, Stripe
- Knowledge base, KPI, Collaboration, Vibe Coding, Admin, PDF export

### Phase 1 — MAARS ∞ Infrastructure (Completed)
- 458+ agents, Kernel Backend, Agent Networks, Task Graphs, Rebranding

### Phase 2 — Chat & Agent Integration (Completed: March 10, 2026)
- Enhanced Chat Sidebar with network browsing, unified search, Browse 27 Networks

### Phase 3 — Dashboards & Intelligence (Completed: March 10, 2026)
- SVG avatars for 417 infinity agents, Knowledge Graph (108 nodes, 91 edges)
- Trust Score Dashboard, Execution Gateway, Updated Landing/About pages

### Phase 4 — Governance & Orchestration (Completed: March 10, 2026)
- **Enterprise RBAC** (`/rbac`): 4 roles (Admin, Manager, Analyst, Viewer), permission matrix (10 resources × 5 actions), user role management
- **Circuit Breakers** (`/circuit-breakers`): 8 service circuits (LLM Gateway, Tool Execution, Memory Store, Web Search, Email, Calendar, Stripe, File Processing), state monitoring, threshold config, reset controls
- **Cost Governance** (`/cost-governance`): Real-time cost tracking, budget controls (monthly/daily limits, alert thresholds), cost-by-model and cost-by-agent breakdowns
- **Visual Workflow Builder** (`/workflow-builder`): Drag-and-drop agent orchestration canvas, agent palette with 27 networks, Bezier curve edges with Canvas 2D, workflow CRUD (create/save/load/delete)

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, Lucide Icons, Canvas 2D
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB (Motor async driver)
- **LLM Providers**: OpenAI, Anthropic, Google, Groq, Mistral, Cohere, Together, Fireworks, Perplexity
- **Integrations**: Google Suite, Stripe, OpenAI Whisper, fpdf2

## Key API Endpoints
- `GET /api/kernel/status|architecture|networks` — Kernel system
- `GET/POST /api/kernel/task-graphs` — Task graph CRUD
- `GET /api/kernel/knowledge-graph` — Knowledge graph (auto-seeds)
- `GET /api/kernel/trust-scores` — Agent trust scores
- `GET /api/kernel/execution-logs` — Execution audit trail
- `GET /api/kernel/rbac/config|users` — RBAC configuration
- `PUT /api/kernel/rbac/users/{id}/role` — Role assignment
- `GET /api/kernel/circuit-breakers/full` — Circuit breaker status
- `PUT /api/kernel/circuit-breakers/{id}` — Update breaker config
- `POST /api/kernel/circuit-breakers/{id}/reset` — Reset breaker
- `GET /api/kernel/cost/overview|by-model|by-agent|budget` — Cost governance
- `PUT /api/kernel/cost/budget` — Update budget limits
- `GET/POST /api/kernel/workflows` — Workflow CRUD
- `GET/PUT/DELETE /api/kernel/workflows/{id}` — Single workflow ops

## P0 — Next Priority Tasks
- Environment Segregation (sandbox/staging/production)
- Memory Hierarchy visualization (7 layers)
- Advanced Agent Trust analytics (trend charts, anomaly detection)

## P1 — Upcoming Tasks
- Advanced Integrations (WhatsApp, Shopify, CRM, ERP)
- Campaign Builder
- Workflow execution engine (run workflows, track progress)

## P2 — Future Tasks
- Multi-tenant isolation
- Mobile wrapper app
- Grep-style content search in Code Explorer
- Custom agent creation by users
- Self-expanding agent creation (governed, sandboxed)

## Credentials
- Admin: management.maars@marsgc.net / Admin123!
