# MAARS-Command Architecture

**One-page map of your entire system.** Last verified: 2026-04-23.

---

## 1. The Big Picture

```
                    ┌──────────────────────────────────────┐
                    │         CLIENTS (buyers)             │
                    │  Free · Starter · Basic · … · Elite  │
                    └───────────────┬──────────────────────┘
                                    │ HTTP (JWT auth)
                    ┌───────────────▼──────────────────────┐
                    │        FastAPI gateway (server.py)   │
                    │  /api/v1/* · /api/* · /admin/*       │
                    └─────┬─────────────┬─────────────┬────┘
                          │             │             │
            ┌─────────────▼──┐  ┌───────▼──────┐  ┌──▼─────────────┐
            │ Universal AI   │  │ Agent Office │  │ Billing & Plan │
            │ Gateway        │  │ Runtime      │  │ Engine         │
            │                │  │              │  │                │
            │ • complete_text│  │ • 499 agents │  │ • Stripe webhook│
            │ • complete_media  │ • 34 offices │  │ • 7-pool wallet │
            │ • maars/* alias│  │ • SOP runner │  │ • Revenue split │
            │ • 14/13/4/4    │  │ • Commander  │  │ • Ledger        │
            │   media chains │  │   Orion DAG  │  │                 │
            └───────┬────────┘  └──────┬───────┘  └────────┬────────┘
                    │                  │                   │
                    └──────────┬───────┴──────────┬────────┘
                               │                  │
                    ┌──────────▼──┐       ┌───────▼──────┐
                    │ 22+ LLM     │       │ MongoDB      │
                    │ providers   │       │              │
                    │ (OpenAI,    │       │ • agents     │
                    │ Anthropic,  │       │ • agent_offices│
                    │ Gemini,     │       │ • wallets    │
                    │ Fal, Groq,  │       │ • ledger_entries│
                    │ Cerebras,   │       │ • gateway_usage_logs│
                    │ Together,   │       │ • revenue_ledger│
                    │ etc.)       │       │ • subscriptions│
                    └─────────────┘       └──────────────┘
```

---

## 2. Money flow — what happens when a client pays $50

```
Client clicks "Subscribe" on /pricing
          │
          ▼
POST /api/checkout                          (routes/subscriptions.py:75)
          │
          ▼
Stripe Checkout session created             (services/billing/stripe_service.py)
          │
          ▼
Client completes payment on Stripe.com
          │
          ▼
Stripe → POST /api/webhook/stripe           (routes/subscriptions.py:321)
          │
          ├──────────────────────────────────────────────────────────┐
          │                                                          │
          ▼                                                          ▼
   wallet_service.grant_buckets(user_id,                    revenue_service.record_revenue(
       pools={                                                   amount_usd = price_usd * operator_share_pct,
           "chat":      plan*0.60,                              source="stripe_subscription",
           "agent_sop": plan*0.15,                              user_id, package_id=plan_id
           "vibe":      plan*0.10,                          )
           "image":     plan*0.08,                              │
           "video":     plan*0.02,                              ▼
           "voice":     plan*0.03,                      operator_revenue_ledger
           "stt":       plan*0.02,                      (operator_share_usd = $50 × 0.30 = $15)
       }, reference_id=session_id)
          │
          ▼
   wallets.buckets.{chat|vibe|image|…}
   Each pool gets its own balance + reserved fields
```

### When the client calls the API

```
POST /api/v1/chat/completions                (routes/v1_gateway.py)
          │
          ▼
   llm_gateway.complete_text(source="chat")  (services/llm_gateway.py)
          │
          ├─────────────┬─────────────────────────────┬─────────────┐
          ▼             ▼                             ▼             ▼
   wallet_service   router.pick_provider          semantic_cache   circuit_breaker
   .reserve(              │                       (88% hit rate!)  (per-provider
    bucket="chat")        ▼                             │           auto-trip)
                   _resolve_maars_alias                 │
                   (maars/auto → gemini,                │
                    maars/code → claude,                │
                    maars/video → fal, etc.)            │
                          │                             │
                          ▼                             │
                   Provider HTTP call                   │
                   (OpenAI / Anthropic / Fal / …)        │
                          │                             │
                          └─────────────┬───────────────┘
                                        │
                                        ▼
                       wallet_service.settle(
                           actual_amount = real cost in credits,
                           bucket = picked up from reserve stash
                       )
                                        │
                                        ▼
                       gateway_usage_logs row written
                       (provider, model, cost_usd, cost_credits, bucket, source)
```

### The 7 credit pools (per wallet)

| Bucket | Default Ratio | Starter=300 | Basic=1200 | Advanced=4000 |
|---|---:|---:|---:|---:|
| chat | 50% | 180 | 600 | 2000 |
| agent_sop | 15% | 45 | 180 | 600 |
| vibe | 10% | 30 | 120 | 400 |
| image | 10% | 24 | 120 | 400 |
| video | 5% | 6 | 60 | 200 |
| voice | 5% | 9 | 60 | 200 |
| stt | 5% | 6 | 60 | 200 |

**Starter/Essential** plans are **hard-limited** (no spillover between pools).
**Basic+** plans allow **general fallback** — empty pools fall through to a shared `general` buffer.

---

## 3. Agent system — 499 agents across 34 offices

```
┌──────────────────────────────────────────────────────────────────┐
│ db.agents (499 rows, each with system_prompt + capabilities)     │
└───────────────────────┬──────────────────────────────────────────┘
                        │ seeded once via POST /admin/offices/seed
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│ office_seeder.seed_all_offices() — 4-tier priority:              │
│                                                                  │
│   1. Commander Orion  ← special-case SOP (orchestrator)          │
│   2. Video Content    ← flagship 10-step SOP                     │
│   3. Role family      ← 34 templates in role_templates.py        │
│   4. Department       ← 10 templates in office_templates.py      │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│ db.agent_offices (499 rows)                                      │
│                                                                  │
│ Each office has:                                                 │
│   • studio_name, department, mission                             │
│   • sop[]                — ordered 6-10 step workflow            │
│   • studio_tools[]       — allowed tools for this role           │
│   • skills_library[]     — prebuilt multi-step skills            │
│   • quality_rules[]      — what "good" output looks like         │
│   • reference_memory_tags[] — memory namespacing                 │
│   • monthly_budget_credits                                       │
│   • languages_supported[]                                        │
└──────────────────────────────────────────────────────────────────┘
```

### Current office distribution

| Studio suffix (role family) | Agents |
|---|---:|
| Strategy Room | 59 |
| Research Desk | 32 |
| Domain Desk | 31 |
| Design Studio | 27 |
| Growth Office · Platform Office · Risk Office | 26 each |
| Agent PMO | 25 |
| Analytics Desk | 22 |
| Finance Desk · Verification Desk | 20 each |
| Incident Room | 18 |
| Writing Desk · Support Studio · Product Office | 13 each |
| Operations Center · Execution Console | 12 each |
| Engineering Bay · Sales Office · Ops Desk · Reporting Desk | 11 each |
| Legal Desk · PR Office | 10 each |
| Experimentation Lab | 9 |
| Graph Office | 7 |
| Procurement Desk | 5 |
| AI Lab | 4 |
| Production Studio | 3 |
| Commander's Bridge · Executive Office · Cross PMO · People Office · Morales PMO · IR Desk | 2 each |

### How an agent runs a task

```
User request → run_sop(office, user_request)
                       │
                       ▼
      [optional] skill-library keyword match → substitutes skill's SOP
                       │
                       ▼
      for each SOP step (understand → research → plan → produce → verify → deliver):
          │
          ▼
      complete_text(
          system_prompt = office.mission + step.description + agent.system_prompt,
          user_prompt   = user_request + accumulated_context,
          model         = "maars/auto",
          agent_id      = office.agent_id,
          source        = f"office_sop:{agent_id}:{step.name}"
      )
          │
          ▼
      parse <tool_calls>[...] blocks from output
          │
          ▼
      for each tool call → execute via workflow_executor.TOOL_REGISTRY
                            (90+ registered tools: web_search, generate_image,
                             generate_video, send_email, github_action, etc.)
          │
          ▼
      accumulate results in context, pass to next step
                       │
                       ▼
      Return {output, trace, quality_checks, matched_skill}
```

---

## 4. Universal AI Gateway

```
                ┌────────────────────────────────────────┐
                │       Caller says model="..."          │
                └────────────────────────────────────────┘
                                  │
             ┌────────────────────┼─────────────────────┐
             │                    │                     │
      model="maars/auto"  model="maars/code"   model="openai/gpt-5"
             │                    │                     │
             ▼                    ▼                     ▼
     _resolve_maars_alias   _resolve_maars_alias    explicit provider/model
     (smart router picks:   (Claude/DeepSeek/Qwen-     │
      cheapest capable)      Coder/Codestral/Kimi)     │
             │                    │                     │
             └────────────────────┼─────────────────────┘
                                  ▼
                  ┌────────────────────────────────┐
                  │ rate_limiter.wait_for_slot()   │
                  │ (8-sec waiting cascade through │
                  │  free-tier providers)          │
                  └────────────┬───────────────────┘
                               │
                               ▼
                  ┌────────────────────────────────┐
                  │ semantic_cache.lookup()        │
                  │ (88% hit rate when prompts     │
                  │  repeat; returns instantly)    │
                  └────────────┬───────────────────┘
                               │ miss
                               ▼
                  ┌────────────────────────────────┐
                  │ provider adapter (22+ options) │
                  │ → circuit_breaker.allow()      │
                  │ → compression (LLMLingua)      │
                  │ → prompt_formatter.shape()     │
                  │ → prompt_cache_helper.annotate()│
                  │ → HTTP call                    │
                  └────────────────────────────────┘
```

### Media aliases (new, via `complete_media`)

```
maars/image            → IMAGE_CHAIN_STANDARD (14 entries)
maars/image/premium    → IMAGE_CHAIN_PREMIUM  (9 entries)
maars/video            → VIDEO_CHAIN          (13 entries, Fal LTX first)
maars/voice            → TTS_CHAIN_STANDARD   (4 entries)
maars/voice/premium    → TTS_CHAIN_PREMIUM    (5 entries)
maars/music            → MUSIC_CHAIN          (4 entries)
maars/stt              → STT_CHAIN            (4 entries)
```

### Real measured COGS (from backend/scripts/cost_simulation_report.json)

| Modality | Per call | Top provider | Near-zero? |
|---|---:|---|:---:|
| chat_short | $0.000002 | cache 94% · Cerebras · Groq | ✅ |
| chat_long | $0.000029 | cache 94% · Groq | ✅ |
| vibe_create | $0.000069 | cache 87% · Cerebras · Groq | ✅ |
| vibe_chat | $0.000019 | cache 87% · Cerebras | ✅ |
| image | $0.000 | Pollinations (free, unlimited) | ✅ |
| video 4s | **$0.020** | **Fal LTX** (was Sora $0.40 before funding) | cost driver |
| tts | $0.0003 | Edge (free) 83% · OpenAI 17% | ✅ |
| stt | $0.000 | Groq Whisper (free) 100% | ✅ |

**Starter $50 plan COGS ≈ $0.86/mo → 98.3% gross margin.**

---

## 5. Frontend surfaces

```
 Sidebar navigation (operator + client views)
┌───────────────────────────────────┐
│ /dashboard        DashboardHub    │
│ /agents           AgentsHub       │
│ /memory           MemoryHub       │
│ /integrations     IntegrationHub  │
│ /workflows        WorkflowBuilder │
│ /wallet           WalletDashboard │  ← per-bucket pools visible
│ /pricing          PricingPage     │  ← per-bucket allowances per plan card
│ /vibe             VibeCoding      │  ← routes to maars/code
│ /admin/gateway    UniversalGateway│  ← AI admin (memory/SME/eval/MCP/router)
│ /admin/governance Governance      │  ← RBAC/circuit-breaker/cost-gov/trust
└───────────────────────────────────┘
```

**75 pages** under `frontend/src/pages/`. 34 route paths in `App.js`. No orphans (SEO landing pages at `/alternatives/*` are live).

---

## 6. What was confusing you — and what I cleaned up today

| Confusion | Resolution |
|---|---|
| "Do I have two billing systems?" | No. `routes/subscriptions.py` is canonical (hit by UI `/checkout` + Stripe `/webhook/stripe`). `routes/billing.py` was a parallel unused implementation — **deleted today**. |
| "Subscription grants not going into buckets?" | True as of this morning. `subscriptions.py` webhook was calling `grant()` direct, landing 100% in `general`. **Fixed today** — now calls `grant_buckets()` with plan_buckets.split_credits. |
| "Two orchestrators?" | Complementary, not duplicates. `orchestrator/commander.py` = DAG/task-graph. `services/agents/agent_orchestrator.py` = 3-phase plan/execute/verify. Different use cases, both kept. |
| "Only Designer role-family SOP coded?" | Wrong. 34 role families are live in `role_templates.py`, covering all 499 agents. Audit tool missed the full list. |
| "AlternativesHub.jsx orphaned?" | No. Live SEO landing pages at `/alternatives/jasper`, `/alternatives/cursor`, etc. Kept. |
| "`auto_topup.py` is a stub" | Correct. **Phase 4** of the cleanup plan targets this: native provider auto-recharge + operator COGS/profit split ledger. |

---

## 7. What's next (phased plan)

**Phase 1 — DONE** (this session):
- ✅ Subscription webhook now routes through `grant_buckets()` → real per-bucket allowances
- ✅ Deleted duplicate `routes/billing.py`
- ✅ Verified 499/499 office coverage across 34 role families
- ✅ This document

**Phase 2 — team restructure** (needs your sign-off):
- Introduce `db.teams` — each team = shared workspace + multiple member agents
- Propose ~15-20 teams (Video Production, Copy Desk, Sales Outbound, etc.) → you approve taxonomy → I migrate agents

**Phase 3 — deep SOP training** (every team like Video Content Specialist):
- Wire `web_search` + `browser_*` tools into `TOOL_REGISTRY` (Serper / Tavily / Playwright)
- Upgrade every team's SOP to real tool-calling depth, not narrative

**Phase 4 — cost automation**:
- Enable native auto-recharge on every provider (OpenAI, Anthropic, Fal, Groq, ElevenLabs, Deepgram — all support it)
- Build `services/cost_automation.py` — books COGS reserve + operator profit as two separate ledger entries at ingest
- Scheduled job alerts when any provider balance < threshold and (optionally) auto-tops via API

---

**Keep this doc in sync when the shape changes.** One file, one page, one source of truth about how MAARS-Command actually works.
