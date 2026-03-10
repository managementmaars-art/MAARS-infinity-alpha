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
  - 27 network categories
  - Each agent has: name, role, description, capabilities, network, autonomy_tier, authority_tier, system_prompt
- **MAARS Kernel Backend**: Kernel status, architecture, networks, task graphs, execution gateway, trust scores, tool registry, circuit breakers
- **New Frontend Pages**: Kernel Dashboard, Agent Networks Browser, Task Graphs
- **UI/Branding**: Rebranded from "MAARS Command" to "MAARS ∞"

### Phase 2 — Chat & Agent Integration (Completed: March 10, 2026)
- **Enhanced Chat Agent Selector**: Refactored SidebarContent with:
  - Quick access row showing 10 original agents with avatars
  - Unified search across all 458+ agents (original + infinity)
  - "Browse 27 Networks" expandable panel with network-grouped agent browsing
  - Fallback initials avatar for infinity agents (no images)
- **All Agents Chattable**: Both original and infinity agents can be selected and chatted with
- **"Chat with Agent" from Networks**: AgentNetworks page has Chat button on each agent that navigates to /chat/:agentId
- **Fallback Avatar System**: Initials-based avatar displays in header, empty state, message bubbles, sidebar, and network browser

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
- `GET /api/agents` — All 458 agents (authenticated)

## Database Collections
- `agents` (458+ documents), `users`, `tasks`, `conversations`, `messages`
- `task_graphs`, `execution_logs`, `tool_registry`
- `memories`, `memory_entries`, `pricing_plans`, `workspace_profiles`
- `knowledge_base`, `collaborations`, `vibe_projects`

## P0 — Next Priority Tasks
1. **Knowledge Graph**: Backend API + frontend visualization for entity/relationship knowledge graph
2. **Trust Score Dashboard**: Visual trust score display per agent based on execution history
3. **Execution Gateway Integration**: Wire task execution through gateway with cost metering and approval routing

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
- Campaign Builder
- Grep-style content search in Code Explorer
- Custom agent creation by users
- Self-expanding agent creation (governed, sandboxed)

## Credentials
- Admin: management.maars@marsgc.net / Admin123!
