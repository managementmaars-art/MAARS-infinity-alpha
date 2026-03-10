# MAARS ∞ — Product Requirements Document

## Original Problem Statement
Build "MAARS Command by MAARS Global Corporation," a commercial, production-ready, autonomous multi-agent AI business operating system. The platform evolved into **MAARS ∞ (Infinity)** — a governed, hierarchical, multi-agent intelligence and execution architecture designed to convert high-level human intent into reliable, measurable, auditable, safe, and strategically useful execution.

## Core Architecture
- **458+ AI Agents** across **27 network categories** (10A through 10AA)
- **16 system layers** from Human Governance to Infrastructure
- **6 Autonomy Tiers** (T0: Advisory → T5: Propose structural changes)
- **MAARS Kernel** with 15 subsystems (Agent Scheduler, Task Graph Runtime, Resource Manager, etc.)
- **Execution Gateway** for governed action routing
- **Tool Registry** for centralized tool management
- **Task Graph System** for structured workflow decomposition

## What's Been Implemented

### Phase 0 — Foundation (Previously Completed)
- 41 original AI agents with full chat capabilities
- Multi-LLM support (9 providers, 30+ models)
- Voice commands (OpenAI Whisper)
- Google Suite integration
- Stripe integration
- Knowledge base & web search
- KPI dashboard, collaboration engine, activity monitor
- Vibe Coding (app builder)
- Admin dashboard with code explorer
- PDF documentation export (aesthetic dark theme)
- About page, Pricing page, Landing page

### Phase 1 — MAARS ∞ Infrastructure (Completed: March 10, 2026)
- **Agent Catalog Expansion**: 41 → 458+ agents (417 new infinity agents)
  - 27 network categories: Core Platform, Strategic, Venture, Product, Engineering, Creative, Growth, Sales, Customer, Operations, Finance, Investment, Research, Simulation, Legal, Security, Memory, Tooling, Execution, Verification, Experimentation, Conflict Resolution, Observability, Recovery, Communication, Web Intelligence, Industry-Specific
  - Each agent has: name, role, description, capabilities, network, autonomy_tier, authority_tier, system_prompt
- **MAARS Kernel Backend**:
  - Kernel status API with 15 subsystem monitoring
  - System architecture endpoint (16 layers, 6 autonomy tiers)
  - Agent networks CRUD with per-network agent listing
  - Task Graph system (full CRUD with nodes, edges, dependencies)
  - Execution Gateway logging
  - Trust Score aggregation from execution history
  - Tool Registry (17 tools seeded)
  - Circuit Breaker status monitoring
- **New Frontend Pages**:
  - Kernel Dashboard (`/kernel`) — subsystem status, metrics, layers, autonomy tiers
  - Agent Networks Browser (`/networks`) — 27 networks with agent detail panel and search
  - Task Graphs (`/task-graphs`) — create and manage structured task workflows
- **UI/Branding Updates**:
  - Rebranded from "MAARS Command" to "MAARS ∞" throughout
  - Commander Orion → Commander Orion ∞ with updated system prompt
  - Updated sidebar navigation with Intelligence section
  - Updated pricing page stats (458+ agents, 27 networks)
  - Updated landing page references

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, Lucide Icons
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
- `POST /api/kernel/execute` — Execution gateway logging
- `GET /api/kernel/trust-scores` — Agent trust scores
- `GET /api/kernel/tools` — Tool registry
- `GET /api/kernel/circuit-breakers` — Circuit breaker status

## Database Collections
- `agents` (458+ documents), `users`, `tasks`, `conversations`, `messages`
- `task_graphs` (NEW), `execution_logs` (NEW), `tool_registry` (NEW)
- `memories`, `memory_entries`, `pricing_plans`, `workspace_profiles`
- `knowledge_base`, `collaborations`, `vibe_projects`

## P0 — Next Priority Tasks
1. **Execution Gateway Integration**: Wire task execution through the gateway with actual cost metering and approval routing
2. **Knowledge Graph**: Implement the node/edge knowledge graph per spec (agents, ventures, products, markets)
3. **Agent Chat Integration**: Enable chatting with any of the 417 new infinity agents
4. **Trust Score Dashboard**: Visual trust score display per agent based on execution history

## P1 — Upcoming Tasks
- Enterprise RBAC with permissions management UI
- Circuit Breaker configuration UI
- Environment Segregation (sandbox/staging/production)
- Cost Governance active monitoring dashboard
- Memory Hierarchy visualization (7 layers)

## P2 — Future Tasks
- Advanced Integrations (WhatsApp, Shopify, CRM, ERP)
- Multi-tenant isolation
- Mobile wrapper app
- Workflow builder UI
- Campaign Builder (Reference Intel → Content Gen → Social scheduling)
- Grep-style content search in Code Explorer
- Custom agent creation by users through lifecycle workflow
- Self-expanding agent creation (governed, sandboxed)

## Credentials
- Admin: management.maars@marsgc.net / Admin123!
