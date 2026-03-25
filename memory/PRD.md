# MAARS COMMAND — AI Operating System
## Product Requirements Document

## System Definition
MAARS Command is a production-ready, autonomous multi-agent AI operating system. Not a chatbot. Not a model picker. An AI Operating System with:
- Shared agent runtime (single kernel, 13-step execution loop)
- Commander/orchestrator (goal → task graph → execution → verification → report)
- Full agent catalog (459 agents, 28 networks, ALL included with maturity states)
- Model orchestration engine (automatic selection, not manual)
- Policy + approval + governance system
- Execution gateway (governed, safe execution)
- Memory + knowledge system (working, episodic, semantic, knowledge graph)
- Semantic memory layer (concept storage, cross-agent learning, context-aware retrieval)
- Verification system (factual, citation, consistency checks)
- Observability + audit + cost system (real-time metrics, alerting, sparklines, custom alert rules)
- Recovery + rollback + incident system (quarantine, retry, rollback)
- Worker queue system (async background jobs with progress tracking)
- WebSocket streaming (real-time execution progress, metrics, alerts)
- Multi-environment segregation (production, staging, sandbox, simulation)
- Command center UI (7 Infinity pages)

## Architecture
```
/app/backend/
  runtime/           → Shared Agent Runtime (13-step execution loop for ALL agents)
  orchestrator/      → Commander Orion (AI-powered: classify → decompose → execute → verify → report)
  kernel/            → Budget, Policy, Scheduler, Task Graph, Tool Registry, Approval Controller
  router/            → Model Router (auto-select across 9 models, 3 providers, with fallback chain)
  intelligence/      → Search Engine (DuckDuckGo), Monitors, Citations
  memory_system/     → Working Memory, Episodic Memory, Semantic Memory, Knowledge Graph
  verification/      → Verification Engine (confidence scoring, crosscheck consensus)
  governance/        → Audit, Circuit Breakers, Trust, Incidents, Autonomy, Metrics, Alerting, Recovery, Environments
  workers/           → Async Job Queue Manager (background LLM tasks, batch processing)
  portfolio/         → Venture Portfolio
  testing_harness/   → 5 Validation Scenarios (A-E)
  services/          → infinity_llm.py, catalog_manager.py, llm_service.py, agent_service.py
  infinity_catalog.py → 370+ agent definitions with role packs
  routes/infinity_routes.py → 120+ API endpoints
  routes/infinity_ws.py → WebSocket streaming (execution steps, metrics, alerts, jobs)
  server.py          → Rate limiting, CORS, middleware
```

## Agent Runtime Loop (13 Steps)
Every agent executes through this identical pipeline:
1. Load Role Pack → 1.5. Validate Environment → 2. Load Context → 3. Retrieve Memory (working + episodic + semantic) →
4. Analyze Task → 5. Plan (Model Selection) → 6. Choose Action → 7. Create ActionRequest →
8. Run Policy → 9. Request Approval (if needed) → 10. Execute via Gateway →
11. Verify Result → 12. Update Memory (working + episodic + semantic concept extraction) → 13. Continue / Escalate / Stop

## Memory System
- **Working Memory**: Active task context scoped to task_id
- **Episodic Memory**: Event sequences and outcomes for agent learning
- **Semantic Memory**: High-level concepts bridging episodic events and knowledge graph
  - Concept storage with confidence scores and tags
  - Cross-agent learning via semantic queries
  - Agent context building for runtime integration
  - Auto-extraction of concepts from execution results
- **Knowledge Graph**: Entity-relationship graph with provenance, traversal, pathfinding

## Worker Queue System
- Background job processing via asyncio for non-blocking execution
- Job types: llm_execution, agent_runtime, batch_analysis, search_and_report
- Progress tracking (0-100%) with status updates
- Retry logic with exponential backoff
- MongoDB-backed persistence

## WebSocket Streaming
- Real-time execution step updates during 13-step runtime
- Live metrics broadcasting
- Alert trigger notifications
- Job progress updates
- Channels: global, metrics, exec:{id}, job:{id}

## Multi-Environment Segregation
- 4 environments: production, staging, sandbox, simulation
- Per-environment config: allowed models, max autonomy tier, budget multiplier, rate limits
- Environment validation integrated into agent runtime
- Custom config overrides via API

## Custom Alert Rules
- Full CRUD: Create, Read, Update, Delete alert rules
- Available metrics: circuit_breakers_tripped, open_incidents, low_trust_count, agent_utilization, model_success_rate_min, recent_failures, busy_agents, total_agents
- Operators: >, <, >=, ==
- Severity levels: low, medium, high
- Toggle enable/disable per rule

## Agent Maturity States
- `production-ready` — Fully implemented, tested, production-safe
- `partial` — Core logic implemented, some features missing
- `experimental` — Under development, sandbox-only
- `catalog-only` — Registered in catalog, no runtime implementation yet

## Model Orchestration (Smart Auto)
- Auto-selection based on: task type, agent role, cost, latency, quality, policy
- Providers: OpenAI (GPT-5.2, GPT-4o, GPT-4o-mini, o3), Anthropic (Claude Sonnet 4.5, Opus 4.5, Haiku 4.5), Google (Gemini 3 Flash, Gemini 3 Pro)
- Fallback chain: GPT-5.2 → Claude Sonnet 4.5 → Gemini 3 Flash
- All routing logged with selected/rejected models, reasoning, cost, latency

## Frontend Command Center
- `/observability` — Live metrics (7 cards), sparklines, execution runs, model performance, alerts, **custom alert rule management UI**
- `/commander` — Full Execute (classify → decompose → execute → verify → report) with **WebSocket live step streaming**
- `/model-router` — Route + Execute tasks with auto-selected LLM
- `/operator` — Operator Control Panel (Overview, Approvals, Test Harness, Autonomy)
- `/agent-catalog` — Full 459-agent catalog with search, filter, inspect, execute
- `/venture-portfolio` — Venture Portfolio management

## Test Reports (All 100% pass rate)
- iteration_87: Phase 2 Intelligence — 60/60 tests
- iteration_88: Phase 5 Operator — 41/41 tests
- iteration_89: LLM Integration — 33/33 tests
- iteration_90: Execution + Metrics — 34/34 tests
- iteration_91: Runtime + Catalog + Recovery — 23/23 tests
- iteration_92: Semantic Memory + Workers + WebSocket + Environments + Alert Rules — 26/26 backend + 9/9 frontend

## Key API Endpoints (120+)
### Runtime
- POST /api/infinity/runtime/execute — 13-step agent execution loop (now with semantic memory + env validation)
- GET /api/infinity/runtime/history — Execution history

### Commander
- POST /api/infinity/orchestrator/full-execute — Full pipeline
- POST /api/infinity/orchestrator/execute — Plan only
- GET /api/infinity/orchestrator/runs — Execution run history

### Catalog
- GET /api/infinity/catalog/agents — Search/filter agent catalog
- GET /api/infinity/catalog/stats — Catalog statistics
- GET /api/infinity/catalog/networks — Network definitions

### Semantic Memory
- POST /api/infinity/memory/semantic/store — Store semantic concepts
- POST /api/infinity/memory/semantic/query — Query across concepts, episodes, entities
- POST /api/infinity/memory/semantic/agent-context — Build agent runtime context
- GET /api/infinity/memory/semantic/concept/{concept} — Get single concept
- GET /api/infinity/memory/semantic/stats — Semantic memory statistics

### Worker Queues
- POST /api/infinity/workers/enqueue — Enqueue background job
- GET /api/infinity/workers/jobs — List jobs
- GET /api/infinity/workers/jobs/{job_id} — Get job status
- POST /api/infinity/workers/jobs/{job_id}/cancel — Cancel job
- GET /api/infinity/workers/stats — Queue statistics

### Multi-Environment
- GET /api/infinity/environments — List all environments
- GET /api/infinity/environments/active — Active environment
- POST /api/infinity/environments/set — Switch environment
- GET /api/infinity/environments/stats — Environment stats
- POST /api/infinity/environments/validate — Validate execution
- POST /api/infinity/environments/configure — Override config

### Alerts (Enhanced with CRUD)
- GET /api/infinity/alerts/rules — List all alert rules
- POST /api/infinity/alerts/rules — Create custom alert rule
- PUT /api/infinity/alerts/rules/{rule_id} — Update rule
- DELETE /api/infinity/alerts/rules/{rule_id} — Delete rule
- GET /api/infinity/alerts/active — Active alerts
- POST /api/infinity/alerts/{rule_id}/acknowledge — Acknowledge alert

### WebSocket
- WS /api/ws/infinity — Real-time streaming (channels: global, metrics, exec:{id}, job:{id})
- GET /api/infinity/ws/stats — Connection statistics

### Recovery
- POST /api/infinity/recovery/quarantine — Quarantine agent
- POST /api/infinity/recovery/rollback/{graph_id} — Rollback execution
- POST /api/infinity/recovery/retry/{graph_id}/{node_id} — Retry failed node

## Credentials
- Admin: management.maars@marsgc.net / admin123

## Backlog
- **P2**: Knowledge Graph visualization improvements (force-directed graph layout)
