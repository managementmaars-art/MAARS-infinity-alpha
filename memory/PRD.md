# MAARS ∞ — Product Requirements Document

## Original Problem Statement
Build "MAARS Command by MAARS Global Corporation," a commercial, production-ready, autonomous multi-agent AI business operating system. The platform evolved into **MAARS ∞ (Infinity)** — a governed, hierarchical, multi-agent intelligence and execution architecture designed to convert high-level human intent into reliable, measurable, auditable, safe, and strategically useful execution.

## Core Architecture
- **458+ AI Agents** across **27 network categories** (10A through 10AA)
- **16 system layers** from Human Governance to Infrastructure
- **6 Autonomy Tiers** (T0: Advisory → T5: Propose structural changes)
- **MAARS Kernel** with 15 subsystems (Agent Scheduler, Task Graph Runtime, Resource Manager, etc.)
- **Execution Gateway** for governed action routing with cost metering
- **Knowledge Graph** for entity/relationship visualization
- **Trust Score System** for agent reliability metrics
- **Tool Registry** for centralized tool management
- **Task Graph System** for structured workflow decomposition

## What's Been Implemented

### Phase 0 — Foundation (Previously Completed)
- 41 original AI agents with full chat capabilities
- Multi-LLM support (9 providers, 30+ models)
- Voice commands (OpenAI Whisper), Google Suite integration, Stripe
- Knowledge base & web search, KPI dashboard, collaboration engine
- Vibe Coding (app builder), Admin dashboard with code explorer
- PDF documentation export, About page, Pricing page, Landing page

### Phase 1 — MAARS ∞ Infrastructure (Completed)
- Agent Catalog: 41 → 458+ agents (417 new infinity agents across 27 networks)
- MAARS Kernel Backend with all 15 subsystems
- New Pages: Kernel Dashboard, Agent Networks Browser, Task Graphs
- Full rebrand from "MAARS Command" to "MAARS ∞"

### Phase 2 — Chat & Agent Integration (Completed: March 10, 2026)
- Enhanced Chat Agent Selector with network-grouped browsing, unified search, Browse 27 Networks panel
- All 458+ agents chattable with fallback initials avatar

### Phase 3 — Dashboards & Intelligence Layer (Completed: March 10, 2026)
- **All Agent Avatars**: Generated unique SVG data URL avatars for all 417 infinity agents with network-specific color gradients
- **Knowledge Graph** (`/knowledge-graph`): Interactive visualization with 108 nodes (27 networks + 81 agents), 91 edges, HTML/Canvas hybrid rendering, zoom/pan/search/filter, detail panel with connections
- **Trust Score Dashboard** (`/trust-scores`): Agent reliability metrics with summary cards, search, sorting, execution history tracking
- **Execution Gateway** (`/execution-gateway`): Governed execution logging with cost metering, success rate, latency tracking, audit trails
- **Execution Gateway Integration**: All chat messages now log to execution gateway for trust scoring and audit
- **Updated Landing Page**: 458+ agents, 27 networks, Knowledge Graph, Trust Scores, Execution Gateway featured
- **Updated About Page**: Stats grid (458+, 27 networks, 16 layers, 9 providers, 212+ endpoints), new badges for KG, Trust, Gateway
- **Updated Navigation**: Intelligence section includes Knowledge Graph, Trust Scores, Execution Gateway

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, Lucide Icons, Canvas 2D (for graph edges)
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB (Motor async driver)
- **LLM Providers**: OpenAI, Anthropic, Google, Groq, Mistral, Cohere, Together, Fireworks, Perplexity
- **Integrations**: Google Suite (Gmail, Calendar), Stripe, OpenAI Whisper, fpdf2

## Key API Endpoints
- `GET /api/kernel/status` — Kernel runtime status
- `GET /api/kernel/architecture` — Full system architecture
- `GET /api/kernel/networks` — List all 27 networks
- `GET /api/kernel/networks/{key}/agents` — Agents in a network
- `POST/GET /api/kernel/task-graphs` — Task graph CRUD
- `GET /api/kernel/knowledge-graph` — Knowledge graph nodes + edges (auto-seeds on first call)
- `POST /api/kernel/knowledge-graph/nodes` — Add knowledge graph node
- `POST /api/kernel/knowledge-graph/edges` — Add knowledge graph edge
- `DELETE /api/kernel/knowledge-graph/nodes/{id}` — Delete node + connected edges
- `POST /api/kernel/execute` — Execution gateway logging
- `GET /api/kernel/execution-logs` — Execution audit trail
- `GET /api/kernel/trust-scores` — Agent trust scores
- `GET /api/kernel/tools` — Tool registry
- `GET /api/kernel/circuit-breakers` — Circuit breaker status
- `GET /api/agents` — All 458 agents (authenticated)

## Database Collections
- `agents` (458+), `users`, `tasks`, `conversations`, `messages`
- `task_graphs`, `execution_logs`, `tool_registry`
- `knowledge_graph_nodes`, `knowledge_graph_edges`
- `memories`, `memory_entries`, `pricing_plans`, `workspace_profiles`
- `knowledge_base`, `collaborations`, `vibe_projects`, `usage_logs`

## P0 — Next Priority Tasks
- Enterprise RBAC with permissions management UI
- Circuit Breaker configuration UI
- Cost Governance active monitoring dashboard

## P1 — Upcoming Tasks
- Environment Segregation (sandbox/staging/production)
- Memory Hierarchy visualization (7 layers)
- Advanced Agent Trust analytics (trend charts, anomaly detection)
- Workflow Builder UI (visual drag-and-drop task graph creation)

## P2 — Future Tasks
- Advanced Integrations (WhatsApp, Shopify, CRM, ERP)
- Multi-tenant isolation
- Mobile wrapper app
- Campaign Builder
- Grep-style content search in Code Explorer
- Custom agent creation by users
- Self-expanding agent creation (governed, sandboxed)

## Credentials
- Admin: management.maars@marsgc.net / Admin123!
