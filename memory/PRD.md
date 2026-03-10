# MAARS ∞ — Product Requirements Document

## Original Problem Statement
Build "MAARS Command by MAARS Global Corporation," a commercial, production-ready, autonomous multi-agent AI business operating system. The platform evolved into **MAARS ∞ (Infinity)** — a governed, hierarchical, multi-agent intelligence and execution architecture.

## Core Architecture
- **458+ AI Agents** with personal names and SVG avatars across **27 network categories**
- **16 system layers**, **6 Autonomy Tiers**, **MAARS Kernel** with 15 subsystems
- **Execution Gateway** with cost metering, **Knowledge Graph** (108 nodes, 91 edges)
- **Trust Score System**, **Enterprise RBAC** (4 roles), **8 Circuit Breakers**
- **Cost Governance** with budget controls
- **Workflow Builder** with drag-and-drop + real LLM execution engine
- **Campaign Builder** with 6 templates and LLM-powered multi-step execution
- **Integration Hub** with 6 external service connectors (WhatsApp, Shopify, CRM, Slack, Zapier)
- **Environment Segregation** (sandbox/staging/production)
- **7-Layer Memory Hierarchy** (L1 Working → L7 Archival)
- **13 LLM Providers** with **45+ models** across text, reasoning, search, image, video, voice, STT
- **Custom Agent Creation** with 12 provider model selection

## Implementation History

### Phase 0 — Foundation
- 41 AI agents, Multi-LLM (9 providers), Voice, Google Suite, Stripe, KPI, Admin

### Phase 1 — MAARS ∞ Infrastructure
- 458+ agents, Kernel Backend, Agent Networks, Task Graphs, Rebranding

### Phase 2 — Chat & Agent Integration
- Enhanced Chat Sidebar with network browsing, unified search

### Phase 3 — Dashboards & Intelligence
- SVG avatars, Knowledge Graph, Trust Scores, Execution Gateway

### Phase 4 — Governance & Orchestration
- Enterprise RBAC, Circuit Breakers, Cost Governance, Workflow Builder

### Phase 5 — Execution & Memory
- Agent Naming, Workflow Execution Engine, Environment Segregation, Memory Hierarchy

### Phase 6 — LLM Provider Expansion (March 10, 2026)
- Added Groq, Together AI, Fireworks AI, AI21 (Jamba) — 13 providers total, 45+ models
- Full cost sheets, router tiers, admin panel, all UI pages updated

### Phase 7 — Campaign Builder & Integrations (March 10, 2026)
- **Real LLM Workflow Execution**: Replaced simulation with actual LLM calls via call_llm_with_fallback. Each node gets agent context + dependency outputs as prompt input.
- **Campaign Builder**: 6 templates (Content Marketing, Product Launch, Customer Onboarding, Sales Outreach, Security Audit, Data Analysis). Each campaign auto-assigns agents from matching networks. Steps execute sequentially with LLM-powered output chaining.
- **Integration Hub**: 6 external service connectors (WhatsApp Business, Shopify, HubSpot CRM, Salesforce, Slack, Zapier) with config forms, connect/disconnect, enable/disable.
- **Custom Agent Creation**: Updated with all 12 LLM providers in the model selector dropdown.

## Key API Endpoints (50+)
- Kernel: `/status`, `/architecture`, `/networks`, `/task-graphs`
- Knowledge Graph: `/knowledge-graph` (CRUD)
- Trust & Execution: `/trust-scores`, `/execution-logs`, `/execute`
- RBAC: `/rbac/config`, `/rbac/users`, `/rbac/users/{id}/role`
- Circuit Breakers: `/circuit-breakers/full`, `/{id}`, `/{id}/reset`
- Cost: `/cost/overview`, `/cost/by-model`, `/cost/by-agent`, `/cost/budget`
- Workflows: CRUD + `/workflows/{id}/run`, `/workflow-runs/{id}`
- Campaigns: `/campaign-templates`, CRUD + `/campaigns/{id}/run`
- Integrations: `/integrations/available`, `/integrations/connect`, `/{id}`, `/{id}/toggle`
- Environments: `/environments`, `/environments/active`
- Memory: `/memory/layers`, `/memory/stats`
- LLM Config: `/llm/config` (12 providers)
- Admin API Keys: `/admin/api-keys` (13 providers)

## Backlog

### P0 — Next Priority
- Connect Campaign Builder output to downloadable reports/PDFs
- Agent-to-agent collaboration within campaign/workflow execution

### P1 — Upcoming
- Multi-tenancy and mobile app wrapper
- Advanced trust analytics (trend charts, anomaly detection)

### P2 — Future
- Grep-style content search, Self-expanding agent creation
- Dashboard widgets and custom analytics

## Credentials
- Admin: management.maars@marsgc.net / Admin123!
