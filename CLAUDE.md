# MAARS-Command

Universal AI Gateway. Clients buy credits, smart router picks cheapest capable provider across 22 integrated LLM APIs.

## Stack
- Backend: Python FastAPI
- Frontend: React
- DB: MongoDB
- Billing: Stripe
- Repo: github.com/managementmaars-art/MAARS-infinity-alpha (branch: main)
- Path: C:\Users\Yaleena Yara\MAARS-COMMAND

## Active work
- Add Runway/Pika adapters to VIDEO_CHAIN to enable video on plans below Basic (currently 400 credits per 4-sec Sora clip gates cheap plans)
- Upgrade ElevenLabs paid plan so premium voice-over uses actual ElevenLabs library voices (router falls through to tts-1-hd today)
- Fix usage_logs bug in backend/routes/v1_gateway.py (privacy-strip zeroes cost before logging)
- AI21 Labs + HuggingFace /v1/models return 0 models

## Structure (post-consolidation, Audit 020 — 2026-04-23)
Frontend hubs (sub-tabbed parent pages, `?view=` URL param):
- `/dashboard` — DashboardHub: Overview + KPIs + Analytics + Observability (4 tabs)
- `/agents` — AgentsHub: My Agents + Create + Suggestions + Catalog (4 tabs)
- `/memory` — MemoryHub: Workspace Brain + Brain Profiles + Governance + Knowledge Graph + Hierarchy (5 tabs)
- `/integrations` + `/integrations/:provider` — credential hub + per-app command center (10 providers)
- `/admin/gateway` — UniversalGatewayTab: AI/LLM admin (memory, SME, eval, MCP, router, authority)
- `/admin/governance` — GovernanceTab: RBAC + Circuit Breakers + Cost Governance + Trust Scores + Operator Panel + Activity Monitor (6 sub-views, admin-only)

Backend service subdirs:
- `services/billing/` — wallet, ledger, stripe, auto_topup, annual_billing, stream_billing, media_billing
- `services/agents/` — agent_performance, agent_budget, agent_orchestrator, agent_prompt_enhancer, agent_router_map
- `services/routing/` — llm_router, smart_router, bandit_router, pareto_router, confidence_router, router_scoring, router_evolution, retrieval_router
- `services/costing/` — base_cost_calculator, blended_cost, cost_allocation, cost_anomaly, cost_config
- `services/workflows/` — workflow_executor, workflow_services, workflow_tools, workflow_generator, workflow_versioning, workflow_pollers, workflow_diagnose, workflow_autocomplete

Retired routes (redirect to canonical):
- `/kpi-dashboard`, `/analytics`, `/observability` → `/dashboard?view=X`
- `/agents/create`, `/agent-suggestions`, `/agent-catalog` → `/agents?view=X`
- `/workspace`, `/brain-profiles`, `/knowledge-graph`, `/memory-hierarchy` → `/memory?view=X`
- `/rbac`, `/circuit-breakers`, `/cost-governance`, `/trust-scores`, `/operator`, `/activity-monitor` → `/admin/governance?view=X`
- `/apps`, `/apps/:provider` → `/integrations/*`
- `/social` (retired) → `/integrations`

## History
- Audit 020 (2026-04-23): Full-codebase consolidation sweep — 12 batch items, zero feature loss. Deleted 2 orphan pages (AdminDashboard, AdminMetricsPage) + 1 duplicate route file (notifications_routes.py, endpoints ported to notifications_center.py). Created 4 hub pages folding 17 top-level pages into 4 sub-tabbed parents (DashboardHub/AgentsHub/MemoryHub/GovernanceTab). Moved 6 governance pages to admin-only under /admin/governance. Grouped 28 backend services into 5 subdirs (billing/ agents/ routing/ costing/ workflows/), ~80 import sites rewritten. Sidebar 19-item Intelligence section split into Operations (10) + Monitoring (6). Smoke: server boots clean, 14 frontend routes + 5 backend endpoints all 200, scheduler registers 6 jobs.
- Audit 019 (2026-04-19): Fix-hint banners per rejected provider (Novita=add balance, xAI=request credits, Together=top up $1, Hyperbolic=phone-verify $1, Amazon=attach AmazonBedrockFullAccess IAM). Probed /v1/models on each rejection to distinguish adapter bugs from billing issues; found Fireworks had 12 deployed models but I was testing wrong ID — flipped to `deepseek-v3p1` and it works. Fixed 2 dead dashboard URLs (Fireworks api-keys, Lepton post-NVIDIA-acquisition). Final: 15 live, 5 pending fix (actionable per card), 17 need signup.
- Audit 018 (2026-04-19): Integrated every provider — smoke-tested all 22 keyed providers via backend/scripts/provider_smoke.py. Fixed 5 adapter/model-ID bugs (Anthropic date, Cohere retired, Cerebras slug, AI21 name, HuggingFace router URL); rewrote AWS Bedrock adapter to use boto3 Converse API. Added POST /admin/gateway/smoke-test + smoke_status in /admin/gateway/health. Provider Health cards show actual reachability (Live/Key-rejected/Untested) with HTTP error detail. 14/22 live; 6 operator-action-required (xai 403, together/hyperbolic/novita 402, fireworks 404-no-models, amazon IAM); 13 need signup.
- Audit 017 (2026-04-19): Provider Health tab — merged ProviderBalancePanel + Live Health Ping into a single unified per-provider card (balance + tier + models + health + actions). Joined /admin/metrics/provider-balances with /admin/gateway/health using canonical-slug alias map (gemini↔google, nvidia↔nvidia_nim, amazon↔bedrock). 38 cards deduped to 35 (one per provider).
- Audit 016 (2026-04-19): Consolidated admin UI surfaces. Operator Metrics page (/admin/metrics) merged into Universal Gateway (/admin/gateway) as new "Financials" tab — KPI row, Revenue by Package, Top Buyers, Routing by Source/Mode, Provider Spend table. Provider Balance panel merged into Provider Health tab (balance+burn+health+alerts on one scroll). /admin/metrics now redirects to /admin/gateway. Metrics endpoints fixed to read gateway_usage_logs (same stale-collection pattern as Audit 015). Live: 119 reqs, 96.24% margin, 71% of traffic on free-tier providers.
- Audit 015 (2026-04-19): ONE ROUTER consolidation. Extracted services/llm_gateway.py:complete() as the single entry point; migrated 22 call sites across 11 files (all of: chats, content, vibe, tasks, products, enterprise, agent_service, orchestration_service, quality_service, memory_learning, infinity_llm). Closed the chat billing gap — every agent chat, content gen, vibe-coded app now hits wallet reserve/settle + gateway_usage_logs with a source tag. Fixed /admin/gateway dashboard collection stale filter (llm_usage_logs → gateway_usage_logs). Live verified: Total Calls 0 → 117, Gemini+Groq 65% of traffic (free tier).
- Audit 014 (2026-04-19): moved per-plan media capacity from PricingManagerTab (reverted) to Provider Intelligence page's per-plan expansion — new "CLIENT CAN DO — MEDIA" card with images/video/TTS/voice-over/STT + provider & cr/unit legend + rose-red video-gate warning. Surfaced "one router" consolidation plan (Option A: extract llm_gateway.complete()) as next-up priority.
- Audit 013 (2026-04-19): ran system as real SMB client end-to-end, migrated 499 agents to auto routing (were hardcoded to openai/gpt-5.2), tuned smart_router cost weight 0.25→0.40 (Gemini-flash/Groq/Cerebras now top picks), rebuilt /admin/pricing-manager Client-Usage-Capacity table as 11-col matrix with per-plan image/video/TTS/voice-over/STT capacity + rose-red video-gate warning for Free/Starter. Realistic mixed blended cost: $0.001/credit (vs $0.000038 chat-only).
- Audit 012 (2026-04-19): closed 4 deferred items — Cohere retired-model alias, Sora plan gate (Basic+), wallet reserve/settle wired into all 4 media endpoints via services/media_billing.py, benchmark social-post check corrected. 14/14 calls green.
- Audit 011 (2026-04-19): emergent fully removed — 35 LLM + 4 Stripe sites across 13 files converted; every modality now flows through MAARS router (chat via call_direct_llm; image/video/tts/stt via services/media_router.py)

## Notes
- Full memory in memory/MEMORY.md
- Do NOT auto-regenerate CLAUDE.md via autoskills — it produces an 8+ MB file that hangs Claude Code subprocess init
