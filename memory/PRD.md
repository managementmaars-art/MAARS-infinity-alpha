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
- Verification system (factual, citation, consistency checks)
- Observability + audit + cost system (real-time metrics, alerting, sparklines)
- Recovery + rollback + incident system (quarantine, retry, rollback)
- Command center UI (7 Infinity pages)

## Architecture
```
/app/backend/
  runtime/           → Shared Agent Runtime (13-step execution loop for ALL agents)
  orchestrator/      → Commander Orion (AI-powered: classify → decompose → execute → verify → report)
  kernel/            → Budget, Policy, Scheduler, Task Graph, Tool Registry, Approval Controller
  router/            → Model Router (auto-select across 9 models, 3 providers, with fallback chain)
  intelligence/      → Search Engine (DuckDuckGo), Monitors, Citations
  memory_system/     → Working Memory, Episodic Memory, Knowledge Graph (traversal/search/pathfinding)
  verification/      → Verification Engine (confidence scoring, crosscheck consensus)
  governance/        → Audit, Circuit Breakers, Trust, Incidents, Autonomy, Metrics, Alerting, Recovery
  portfolio/         → Venture Portfolio
  testing_harness/   → 5 Validation Scenarios (A-E)
  services/          → infinity_llm.py, catalog_manager.py, llm_service.py, agent_service.py
  infinity_catalog.py → 370+ agent definitions with role packs
  routes/infinity_routes.py → 100+ API endpoints
  server.py          → Rate limiting, CORS, middleware
```

## Agent Runtime Loop (13 Steps)
Every agent executes through this identical pipeline:
1. Load Role Pack → 2. Load Context → 3. Retrieve Memory → 4. Analyze Task →
5. Plan (Model Selection) → 6. Choose Action → 7. Create ActionRequest →
8. Run Policy → 9. Request Approval (if needed) → 10. Execute via Gateway →
11. Verify Result → 12. Update Memory → 13. Continue / Escalate / Stop

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
- `/observability` — Live metrics (7 cards), sparklines, execution runs, model performance, alerts
- `/commander` — Full Execute (classify → decompose → execute → verify → report)
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

## Key API Endpoints (100+)
### Runtime
- POST /api/infinity/runtime/execute — 13-step agent execution loop
- GET /api/infinity/runtime/history — Execution history

### Commander
- POST /api/infinity/orchestrator/full-execute — Full pipeline: classify → decompose → execute → verify → report
- POST /api/infinity/orchestrator/execute — Plan only: classify → decompose → assign
- GET /api/infinity/orchestrator/runs — Execution run history

### Catalog
- GET /api/infinity/catalog/agents — Search/filter agent catalog
- GET /api/infinity/catalog/stats — Catalog statistics
- GET /api/infinity/catalog/networks — Network definitions

### Metrics & Alerts
- GET /api/infinity/metrics/live — Real-time system metrics
- GET /api/infinity/metrics/history — Trend data
- GET /api/infinity/alerts/rules — Alert rules

### Recovery
- POST /api/infinity/recovery/quarantine — Quarantine agent
- POST /api/infinity/recovery/rollback/{graph_id} — Rollback execution
- POST /api/infinity/recovery/retry/{graph_id}/{node_id} — Retry failed node

## Credentials
- Admin: management.maars@marsgc.net / admin123
