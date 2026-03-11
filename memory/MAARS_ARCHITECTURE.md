# MAARS INFINITY — FULL SYSTEM ARCHITECTURE

## System Overview

MAARS Infinity is an Autonomous AI Enterprise Operating System comprising 11 major system domains, 458+ agents across 28 networks, 13 LLM providers, and 45+ models. The architecture is designed for correctness, safety, verification, traceability, execution quality, cost efficiency, strategic leverage, and operator control.

---

## 1. ARCHITECTURE MAP — How All Subsystems Connect

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPERATOR CONTROL PANEL                           │
│  (Inspect / Pause / Override / Approve / Deny / Retire / Budget)    │
└──────────────┬──────────────────────────────────────┬───────────────┘
               │                                      │
    ┌──────────▼──────────┐              ┌────────────▼────────────┐
    │ OBSERVABILITY LAYER │              │  GOVERNANCE LAYER       │
    │ • Dashboards        │              │  • Audit Logs           │
    │ • Trace Logs        │              │  • Circuit Breakers     │
    │ • Agent Metrics     │              │  • Trust Scoring        │
    │ • Model Metrics     │              │  • Autonomy Tiers       │
    │ • Cost Tracking     │              │  • Policy Engine        │
    │ • Incident Mgmt     │              │  • Escalation System    │
    └──────────┬──────────┘              └────────────┬────────────┘
               │                                      │
    ┌──────────▼──────────────────────────────────────▼───────────────┐
    │              STRATEGIC INTELLIGENCE LAYER                       │
    │                                                                 │
    │  ┌─────────────────────────────────────────────────────────┐    │
    │  │              COMMANDER ORION                             │    │
    │  │  Goal Classification → Task Decomposition →             │    │
    │  │  Agent Assignment → Execution Coordination →            │    │
    │  │  Verification Trigger → Result Aggregation              │    │
    │  └──────────────────────┬──────────────────────────────────┘    │
    │                         │                                       │
    │  ┌──────────────────────▼──────────────────────────────────┐    │
    │  │           TASK GRAPH RUNTIME                             │    │
    │  │  DAG execution • Dependency resolution • Parallel/       │    │
    │  │  Sequential • Checkpoints • Approval gates              │    │
    │  └──────────────────────┬──────────────────────────────────┘    │
    └─────────────────────────┼───────────────────────────────────────┘
                              │
    ┌─────────────────────────▼───────────────────────────────────────┐
    │                   CORE RUNTIME LAYER (KERNEL)                   │
    │                                                                 │
    │  ┌────────────┐ ┌────────────┐ ┌─────────────┐ ┌────────────┐  │
    │  │  Agent     │ │  Resource  │ │  Budget     │ │  Policy    │  │
    │  │  Scheduler │ │  Manager   │ │  Controller │ │  Engine    │  │
    │  └────────────┘ └────────────┘ └─────────────┘ └────────────┘  │
    │  ┌────────────┐ ┌────────────┐ ┌─────────────┐ ┌────────────┐  │
    │  │  Approval  │ │ Environment│ │  Failure    │ │  Rollback  │  │
    │  │  Controller│ │ Segregation│ │  Recovery   │ │  Manager   │  │
    │  └────────────┘ └────────────┘ └─────────────┘ └────────────┘  │
    └──────┬──────────────┬──────────────┬──────────────┬─────────────┘
           │              │              │              │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐ ┌────▼─────────┐
    │ VERIFICATION│ │  MODEL    │ │  TOOL &    │ │  MEMORY &    │
    │ CIVILIZATION│ │  ROUTER   │ │  EXECUTION │ │  KNOWLEDGE   │
    │             │ │           │ │            │ │              │
    │ •Fact       │ │ •Classify │ │ •Registry  │ │ •Short-term  │
    │ •Source     │ │ •Select   │ │ •Health    │ │ •Working     │
    │ •Hallucin.  │ │ •Cost-opt │ │ •Schema    │ │ •Long-term   │
    │ •Code       │ │ •Fallback │ │ •Gateway   │ │ •Episodic    │
    │ •Quant      │ │ •Perf-log │ │ •Fallback  │ │ •Semantic    │
    │ •Compliance │ │ •Learn    │ │ •Perms     │ │ •Knowledge   │
    │ •Crosscheck │ │           │ │            │ │  Graph       │
    │ •Confidence │ │           │ │            │ │ •Provenance  │
    └─────────────┘ └───────────┘ └────────────┘ └──────────────┘
           │              │              │              │
    ┌──────▼──────────────▼──────────────▼──────────────▼─────────────┐
    │              LIVE WEB INTELLIGENCE LAYER                        │
    │                                                                 │
    │  Query Planning → Search Execution → Source Ranking →           │
    │  Freshness Detection → Multi-source Verification →              │
    │  Citation Engine → News/Competitor/Regulatory Monitors          │
    └─────────────────────────┬───────────────────────────────────────┘
                              │
    ┌─────────────────────────▼───────────────────────────────────────┐
    │              ECONOMIC & PORTFOLIO LAYER                         │
    │                                                                 │
    │  Venture Portfolio State Machine → Capital Allocation →         │
    │  Revenue/CAC/LTV Tracking → Burn/Runway → Kill/Scale/Pivot →   │
    │  Reinvestment Logic → Opportunity Scoring                       │
    └─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────▼───────────────────────────────────────┐
    │              AGENT NETWORKS (28 Networks, 458+ Agents)          │
    │                                                                 │
    │  Strategic & Executive │ Core Platform │ Tooling & Capability   │
    │  Verification │ Web Search │ Research │ Venture Creation        │
    │  Engineering │ Creative & Brand │ Growth & Distribution         │
    │  Sales & Revenue │ Finance & Capital │ Operations               │
    │  Legal & Governance │ Simulation & Foresight │ + 13 more        │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 2. FULL BACKEND SERVICE MAP

### Existing Services (Already Built)
| Service | File | Lines | Status |
|---------|------|-------|--------|
| LLM Router | `services/llm_router.py` | 213 | Partial — needs task-based routing |
| Orchestration | `services/orchestration_service.py` | 663 | Partial — needs task graph DAGs |
| Kernel | `services/kernel_service.py` | 745 | Partial — agent seeding, needs runtime |
| Quality | `services/quality_service.py` | 258 | Partial — basic checks |
| Web Search | `services/web_search.py` | 270 | Partial — needs source ranking |
| LLM Service | `services/llm_service.py` | 504 | Active — multi-provider LLM calls |
| Agent Service | `services/agent_service.py` | — | Active — agent CRUD |
| Analytics | `services/analytics_service.py` | — | Active — basic analytics |
| Cache | `services/cache_service.py` | — | Active — caching |
| Campaign | `services/campaign_service.py` | — | Active — campaign builder |
| Memory Learning | `services/memory_learning_service.py` | — | Partial — auto-learning |
| RAG | `services/rag_service.py` | — | Active — knowledge base |

### New Services Required
| Domain | Service Module | Purpose |
|--------|---------------|---------|
| **Kernel** | `kernel/scheduler.py` | Agent scheduling, task assignment queue |
| **Kernel** | `kernel/task_graph.py` | DAG execution engine, dependency resolution |
| **Kernel** | `kernel/resource_manager.py` | System resource allocation |
| **Kernel** | `kernel/budget_controller.py` | Real-time spend tracking, limits |
| **Kernel** | `kernel/policy_engine.py` | Rule enforcement, constraint validation |
| **Kernel** | `kernel/approval_controller.py` | Approval workflows, checkpoint gates |
| **Kernel** | `kernel/environment.py` | Sandbox vs production segregation |
| **Kernel** | `kernel/failure_recovery.py` | Error handling, retry logic, fallbacks |
| **Kernel** | `kernel/rollback_manager.py` | State snapshots, rollback execution |
| **Orchestrator** | `orchestrator/commander.py` | Commander Orion — goal→execution pipeline |
| **Orchestrator** | `orchestrator/goal_classifier.py` | Goal type, risk, complexity classification |
| **Orchestrator** | `orchestrator/task_decomposer.py` | Goal → task graph generation |
| **Orchestrator** | `orchestrator/agent_assigner.py` | Task → agent matching with trust/skill |
| **Orchestrator** | `orchestrator/planner.py` | Long-horizon strategic planning |
| **Verification** | `verification/fact_verifier.py` | Factual accuracy checking |
| **Verification** | `verification/source_verifier.py` | Source credibility, provenance |
| **Verification** | `verification/hallucination.py` | Hallucination detection |
| **Verification** | `verification/code_verifier.py` | Code correctness validation |
| **Verification** | `verification/compliance.py` | Policy & regulatory compliance |
| **Verification** | `verification/crosscheck.py` | Multi-agent consensus verification |
| **Verification** | `verification/confidence.py` | Confidence aggregation scoring |
| **Router** | `router/classifier.py` | Task → model class classification |
| **Router** | `router/selector.py` | Model selection with cost/latency/safety |
| **Router** | `router/fallback.py` | Provider failure → fallback routing |
| **Router** | `router/performance.py` | Model performance tracking & learning |
| **Memory** | `memory/short_term.py` | Session-scoped context |
| **Memory** | `memory/working.py` | Active task context |
| **Memory** | `memory/long_term.py` | Persistent knowledge store |
| **Memory** | `memory/episodic.py` | Event sequence memory |
| **Memory** | `memory/semantic.py` | Concept/relationship memory |
| **Memory** | `memory/knowledge_graph.py` | Entity-relationship graph |
| **Memory** | `memory/provenance.py` | Source & freshness tracking |
| **Intelligence** | `intelligence/search_engine.py` | Query planning & execution |
| **Intelligence** | `intelligence/source_ranker.py` | Source credibility ranking |
| **Intelligence** | `intelligence/freshness.py` | Data freshness detection |
| **Intelligence** | `intelligence/monitors.py` | News/competitor/regulatory/trend/sentiment |
| **Intelligence** | `intelligence/citation.py` | Citation & provenance engine |
| **Portfolio** | `portfolio/ventures.py` | Venture portfolio state machine |
| **Portfolio** | `portfolio/capital.py` | Capital allocation |
| **Portfolio** | `portfolio/metrics.py` | Revenue/CAC/LTV/burn/runway |
| **Portfolio** | `portfolio/opportunity.py` | Opportunity scoring |
| **Governance** | `governance/audit.py` | Immutable audit logging |
| **Governance** | `governance/circuit_breaker.py` | Circuit breaker system |
| **Governance** | `governance/trust_scoring.py` | Dynamic trust scores |
| **Governance** | `governance/autonomy.py` | Tier enforcement |
| **Governance** | `governance/incidents.py` | Incident management |
| **Governance** | `governance/escalation.py` | Escalation workflows |

### Full API Route Map
| Prefix | Route File | Key Endpoints |
|--------|-----------|---------------|
| `/api/kernel` | `routes/kernel_routes.py` | `POST /execute`, `GET /status`, `POST /pause`, `POST /resume` |
| `/api/orchestrator` | `routes/orchestrator_routes.py` | `POST /goal`, `GET /plan/{id}`, `POST /execute/{id}` |
| `/api/tasks` | `routes/task_routes.py` | `POST /graph`, `GET /graph/{id}`, `PATCH /graph/{id}/node/{nid}` |
| `/api/verify` | `routes/verify_routes.py` | `POST /check`, `GET /result/{id}`, `POST /crosscheck` |
| `/api/router` | `routes/router_routes.py` | `POST /select`, `GET /performance`, `GET /costs` |
| `/api/memory` | `routes/memory_routes.py` | `POST /store`, `GET /recall`, `POST /knowledge-graph` |
| `/api/intelligence` | `routes/intelligence_routes.py` | `POST /search`, `GET /monitor/{type}`, `POST /verify-sources` |
| `/api/portfolio` | `routes/portfolio_routes.py` | `GET /ventures`, `POST /score`, `GET /metrics` |
| `/api/governance` | `routes/governance_routes.py` | `GET /audit`, `GET /circuit-breakers`, `POST /trust-score` |
| `/api/observe` | `routes/observe_routes.py` | `GET /dashboard`, `GET /metrics/{domain}`, `GET /incidents` |

---

## 3. FULL DATABASE DESIGN

### MongoDB Collections

#### Core Runtime
```
kernel_state {
  _id, status, active_workflows, active_agents, environment,
  budget_used, budget_limit, circuit_breaker_state,
  last_health_check, uptime_start, config
}

task_graphs {
  _id, goal_id, objective, status, created_at, updated_at,
  created_by, environment, priority, deadline,
  budget_allocated, budget_used,
  nodes: [{
    node_id, type, task_description, status,
    assigned_agent_id, backup_agent_id,
    model_class, model_used, tool_requirements,
    dependencies: [node_id], outputs,
    verification_status, verification_score,
    started_at, completed_at, retry_count,
    cost, error_log, rollback_plan
  }],
  edges: [{ from, to, type }],
  collaboration_mode, approval_checkpoints,
  final_output, verification_result
}

goals {
  _id, description, classification, risk_level,
  freshness_requirement, complexity, priority,
  requester_id, status, task_graph_id,
  created_at, completed_at, outcome_metrics
}
```

#### Verification
```
verification_results {
  _id, task_id, task_graph_id, output_id,
  verification_type, verifier_agent_id,
  verification_pass, confidence_score,
  completeness, correctness, source_grounding,
  actionability, compliance, professionalism,
  verification_notes, retry_recommendation,
  escalation_recommendation,
  created_at, model_used, cost
}

crosscheck_results {
  _id, task_id, verifier_ids: [],
  individual_scores: [], consensus_score,
  consensus_reached, final_verdict,
  dissenting_notes, created_at
}
```

#### Model Routing
```
model_routing_log {
  _id, task_id, task_type, difficulty, risk_level,
  speed_requirement, cost_sensitivity,
  selected_model, selected_provider,
  selection_reason, expected_cost, latency_target,
  actual_cost, actual_latency,
  verification_passed, retry_count,
  created_at
}

model_performance {
  _id, provider, model_name,
  task_class, total_calls, success_count,
  avg_cost, avg_latency, verification_pass_rate,
  hallucination_rate, retry_rate,
  last_updated, trust_score
}
```

#### Agent System
```
agents {
  _id, agent_id, name, role, network,
  description, capabilities: [], tools: [],
  autonomy_tier, trust_score, status,
  avatar, model_preference,
  performance: {
    tasks_started, tasks_completed,
    avg_completion_time, retry_count,
    verification_pass_rate, incident_rate
  },
  budget_cap, created_at, updated_at
}

agent_networks {
  _id, network_id, name, description,
  agent_count, capabilities: [],
  collaboration_modes: [], lead_agent_id
}
```

#### Memory & Knowledge
```
memory_short_term {
  _id, session_id, agent_id, context,
  created_at, expires_at
}

memory_working {
  _id, task_id, agent_id, context,
  intermediate_results, created_at
}

memory_long_term {
  _id, agent_id, topic, content,
  source, confidence, created_at,
  last_accessed, access_count
}

memory_episodic {
  _id, agent_id, event_type, event_data,
  outcome, lessons_learned, timestamp
}

knowledge_graph {
  _id, entity, entity_type, relationships: [{
    target, relationship_type, weight,
    source, created_at
  }],
  attributes, provenance, freshness_score,
  last_verified, created_at
}
```

#### Web Intelligence
```
search_cache {
  _id, query_hash, query, results,
  sources: [], freshness_score,
  created_at, expires_at
}

intelligence_monitors {
  _id, monitor_type, target, status,
  last_check, findings: [],
  alert_level, created_at
}
```

#### Economic & Portfolio
```
ventures {
  _id, name, description, status,
  stage, revenue, costs,
  cac, ltv, burn_rate, runway_months,
  opportunity_score, next_action,
  created_at, updated_at, metrics_history: []
}

budget_tracking {
  _id, entity_type, entity_id,
  period, allocated, spent,
  remaining, alerts: [],
  transactions: [{
    amount, model, task_id, timestamp
  }]
}
```

#### Governance
```
audit_log {
  _id, action, actor_type, actor_id,
  target_type, target_id, details,
  result, timestamp, immutable: true
}

circuit_breakers {
  _id, name, target_type, target_id,
  status, trigger_condition,
  trigger_threshold, current_value,
  tripped_at, recovered_at,
  action_taken, created_at
}

trust_scores {
  _id, entity_type, entity_id,
  score, factors: {
    verification_pass_rate, compliance,
    usefulness, cost_efficiency, incident_rate
  },
  history: [{ score, timestamp }],
  last_updated
}

incidents {
  _id, type, severity, description,
  affected_components: [], detected_at,
  resolved_at, resolution, postmortem,
  escalation_level, assigned_to
}

escalations {
  _id, source_task_id, reason, severity,
  current_handler, escalation_chain: [],
  status, created_at, resolved_at
}
```

---

## 4. AGENT SYSTEM ARCHITECTURE

### Agent Entity Model
Every agent is a structured entity with:
- **Identity**: agent_id, name, avatar
- **Role**: role title, network membership
- **Capabilities**: skill tags, domain expertise
- **Tools**: permitted tool list, tool permissions
- **Autonomy**: tier 0-5 with corresponding limits
- **Trust**: dynamic score 0-100
- **Performance**: tasks completed, pass rate, avg time, incidents
- **Budget**: per-agent spending cap
- **Model Preference**: preferred LLM for this agent's task class

### Network Structure (28 Networks)
| # | Network | Agent Count | Primary Function |
|---|---------|------------|-----------------|
| 1 | Strategic & Executive | 14 | Command, planning, strategy |
| 2 | Core Platform | 18 | Runtime, health, infrastructure |
| 3 | Tooling & Capability | 12 | Tool management, API reliability |
| 4 | Verification | 12 | All verification types |
| 5 | Web Search Intelligence | 20 | Live web research, monitoring |
| 6 | Research & Intelligence | 18 | Deep research, analysis |
| 7 | Venture Creation | 18 | New business development |
| 8 | Engineering | 22 | Code, architecture, DevOps |
| 9 | Creative & Brand | 19 | Design, content, brand |
| 10 | Growth & Distribution | 23 | Marketing, SEO, distribution |
| 11 | Sales & Revenue | 15 | Sales, revenue optimization |
| 12 | Finance & Capital | 21 | Financial analysis, treasury |
| 13 | Operations | 18 | HR, procurement, SLA |
| 14 | Legal & Governance | 19 | Legal, ethics, compliance |
| 15 | Simulation & Foresight | 12 | Scenario modeling, forecasting |
| 16 | Industry Specific | 40 | Domain expertise |
| 17 | Customer Experience | 14 | Support, onboarding, VoC |
| 18 | Investment & Portfolio | 14 | Venture scoring, portfolio mgmt |
| 19 | Memory & Knowledge | 13 | Knowledge architecture |
| 20 | Execution | 12 | Task execution, automation |
| 21 | Observability & Incident | 12 | Monitoring, alerting |
| 22 | Communication & Reporting | 11 | Reports, alerts, PR |
| 23 | Experimentation | 11 | A/B testing, PMF |
| 24 | Product Development | 17 | Product spec, iteration |
| 25 | Security | 14 | Cybersecurity, anomaly detection |
| 26 | Core Team | 19 | App dev, UX, growth hacking |
| 27 | Recovery & Resilience | 10 | Disaster recovery, state repair |
| 28 | Conflict Resolution | 10 | Arbitration, deadlock resolution |

### Runtime Behavior
1. Agent receives task assignment from Scheduler
2. Agent checks autonomy tier → may require approval
3. Agent selects tools from permitted list
4. Model Router selects LLM based on task classification
5. Agent executes via Execution Gateway
6. Output sent to Verification Pipeline
7. Results logged to Audit + Observability
8. Trust score updated based on outcome
9. Memory updated (episodic + long-term learning)

---

## 5. DEPENDENCY GRAPH

```
Level 0 (Foundation):
  MongoDB ← Config ← Auth

Level 1 (Core Runtime):
  Audit Logger ← Policy Engine ← Budget Controller
  Environment Controller ← Rollback Manager

Level 2 (Execution Infrastructure):
  Agent Scheduler ← Task Graph Runtime
  Tool Registry ← Execution Gateway
  Model Router (Classifier + Selector + Fallback)

Level 3 (Intelligence):
  Memory System (Short/Working/Long-term)
  Web Search Engine ← Source Ranker ← Freshness Detector

Level 4 (Verification):
  Fact Verifier ← Source Verifier ← Hallucination Detector
  Crosscheck Coordinator ← Confidence Aggregator

Level 5 (Orchestration):
  Goal Classifier ← Task Decomposer ← Agent Assigner
  Commander Orion (depends on Levels 1-4)

Level 6 (Observability):
  Observability Dashboard (reads all metrics)
  Circuit Breaker System ← Trust Scoring Engine
  Operator Control Panel

Level 7 (Economics):
  Venture Portfolio ← Capital Allocation
  Revenue/CAC/LTV Tracking ← Kill/Scale/Pivot Logic

Level 8 (Advanced):
  Knowledge Graph ← Semantic Memory
  Intelligence Monitors (News/Competitor/Regulatory)
  Escalation System ← Incident Management ← Postmortem
```

---

## 6. CRITICAL BUILD PATH

The minimum sequence to reach a working full MAARS architecture:

```
Phase 1: Foundation (Runtime + Routing + Verification Core)
├── 1a. Kernel: Budget Controller, Policy Engine, Audit Logger
├── 1b. Task Graph Runtime: DAG engine, node execution
├── 1c. Model Router: Task classifier, model selector, fallback
├── 1d. Verification Core: Fact verifier, confidence scorer, crosscheck
└── 1e. Agent Scheduler: Task queue, agent assignment

Phase 2: Intelligence + Memory
├── 2a. Memory: Working memory, episodic memory
├── 2b. Web Intelligence: Search engine, source ranking, freshness
├── 2c. Verification Expansion: All 7 verifier types
└── 2d. Tool Registry: Health monitoring, schema validation

Phase 3: Orchestration + Governance
├── 3a. Commander Orion: Full goal→execution pipeline
├── 3b. Goal Classifier + Task Decomposer + Agent Assigner
├── 3c. Circuit Breakers: Spend/error/verification triggers
├── 3d. Trust Scoring: Dynamic scores for agents/models/tools
└── 3e. Observability Dashboard: All metric domains

Phase 4: Economics + Advanced
├── 4a. Venture Portfolio: State machine, opportunity scoring
├── 4b. Capital Allocation + Revenue tracking
├── 4c. Knowledge Graph + Semantic Memory
├── 4d. Intelligence Monitors: All 6 monitor types
└── 4e. Incident Management + Postmortem + Escalation

Phase 5: Operator Control + Test Harness
├── 5a. Operator Control Panel: Full inspect/pause/override UI
├── 5b. Approval Controller: Checkpoint gates, approval workflows
├── 5c. Test Harness: Scenarios A-E with metrics
├── 5d. Environment Segregation: Sandbox ↔ Production
└── 5e. Long-horizon Planning + Planning Memory
```

---

## 7. PHASED IMPLEMENTATION ROADMAP

### Phase 1: Foundation — Core Runtime, Routing, Verification
**Goal**: A single task can be classified, routed to the right model, executed, verified, and logged.

| Task | Service | Priority |
|------|---------|----------|
| Audit Logger | `governance/audit.py` | P0 |
| Budget Controller | `kernel/budget_controller.py` | P0 |
| Policy Engine | `kernel/policy_engine.py` | P0 |
| Task Graph Runtime | `kernel/task_graph.py` | P0 |
| Agent Scheduler | `kernel/scheduler.py` | P0 |
| Model Router Classifier | `router/classifier.py` | P0 |
| Model Router Selector | `router/selector.py` | P0 |
| Model Router Fallback | `router/fallback.py` | P0 |
| Fact Verifier | `verification/fact_verifier.py` | P0 |
| Confidence Scorer | `verification/confidence.py` | P0 |
| Crosscheck Coordinator | `verification/crosscheck.py` | P0 |
| API Routes for above | `routes/` | P0 |
| Frontend: Task Graph Viewer | UI | P1 |
| Frontend: Router Dashboard | UI | P1 |
| Frontend: Verification Results | UI | P1 |

### Phase 2: Intelligence + Memory
**Goal**: System can search the web, verify sources, remember past work, and use context.

| Task | Service | Priority |
|------|---------|----------|
| Working Memory | `memory/working.py` | P0 |
| Episodic Memory | `memory/episodic.py` | P0 |
| Search Engine | `intelligence/search_engine.py` | P0 |
| Source Ranker | `intelligence/source_ranker.py` | P0 |
| Freshness Detector | `intelligence/freshness.py` | P0 |
| Source Verifier | `verification/source_verifier.py` | P0 |
| Hallucination Detector | `verification/hallucination.py` | P0 |
| Code Verifier | `verification/code_verifier.py` | P1 |
| Compliance Verifier | `verification/compliance.py` | P1 |
| Tool Registry + Health | `tools/registry.py` | P1 |

### Phase 3: Orchestration + Governance
**Goal**: Commander Orion can take a goal, plan, execute, verify, and report — with full governance.

| Task | Service | Priority |
|------|---------|----------|
| Commander Orion | `orchestrator/commander.py` | P0 |
| Goal Classifier | `orchestrator/goal_classifier.py` | P0 |
| Task Decomposer | `orchestrator/task_decomposer.py` | P0 |
| Agent Assigner | `orchestrator/agent_assigner.py` | P0 |
| Circuit Breakers | `governance/circuit_breaker.py` | P0 |
| Trust Scoring | `governance/trust_scoring.py` | P0 |
| Autonomy Enforcer | `governance/autonomy.py` | P0 |
| Observability Dashboard | Frontend | P0 |
| Failure Recovery | `kernel/failure_recovery.py` | P1 |
| Rollback Manager | `kernel/rollback_manager.py` | P1 |

### Phase 4: Economics + Advanced Intelligence
**Goal**: System tracks business value, manages ventures, and monitors the external world.

| Task | Service | Priority |
|------|---------|----------|
| Venture Portfolio | `portfolio/ventures.py` | P0 |
| Capital Allocation | `portfolio/capital.py` | P0 |
| Revenue/CAC/LTV | `portfolio/metrics.py` | P0 |
| Knowledge Graph | `memory/knowledge_graph.py` | P1 |
| Semantic Memory | `memory/semantic.py` | P1 |
| Intelligence Monitors | `intelligence/monitors.py` | P1 |
| Citation Engine | `intelligence/citation.py` | P1 |

### Phase 5: Operator Control + Test Harness
**Goal**: Full human control, approval workflows, and validated test scenarios.

| Task | Service | Priority |
|------|---------|----------|
| Operator Control Panel | Frontend | P0 |
| Approval Controller | `kernel/approval_controller.py` | P0 |
| Environment Segregation | `kernel/environment.py` | P0 |
| Test Scenarios A-E | `tests/` | P0 |
| Incident Management | `governance/incidents.py` | P1 |
| Postmortem Workflow | `governance/postmortem.py` | P1 |
| Escalation System | `governance/escalation.py` | P1 |
| Long-horizon Planner | `orchestrator/planner.py` | P1 |

---

## 8. BUILD PHILOSOPHY

> Design for the full Infinity architecture.
> Build in controlled phases.
> Activate capabilities incrementally.
> Do not reduce scope at the architecture level.

Every service module will be created with its full interface from day one, even if the initial implementation is a structured stub that logs and returns controlled defaults. As each phase completes, stubs are replaced with production logic.

No capability without control.
No action without verification.
No scale without observability.
No autonomy without governance.
No workflow without outcome measurement.
