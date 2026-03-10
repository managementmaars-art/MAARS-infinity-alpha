# MAARS Infinity — Product Requirements Document

## Overview
MAARS ∞ is an autonomous AI enterprise operating system by MAARS Global Corporation.  
458+ AI agents across 27 networks, 16 system layers, powered by 13 LLM providers with 45+ models.

## Architecture
- **Backend**: FastAPI (Python) + MongoDB + WebSocket
- **Frontend**: React 18 + Tailwind CSS + Shadcn/UI (PWA-enabled)
- **Payments**: Stripe (test key integrated, checkout sessions + webhooks)
- **AI**: OpenAI, Anthropic, Google, Groq, Together AI, Fireworks, AI21, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs

## Refactored Service Architecture
```
backend/services/
├── kernel_service.py       # Core kernel + re-export hub
├── campaign_service.py     # Campaigns, templates, PDF, scheduling
├── analytics_service.py    # Cost governance, trust analytics, widgets
├── integration_service.py  # Third-party integration hub
├── organization_service.py # Multi-tenancy, teams, org management
├── agent_service.py        # Agent catalog, seeding, CRUD
├── llm_service.py          # LLM routing, provider management
└── rag_service.py          # RAG/embedding service
```

## Completed Features

### Core Platform
- [x] User authentication (JWT) + RBAC
- [x] Dashboard with real-time stats
- [x] Command palette + voice commands
- [x] Agent catalog (458+ agents with unique SVG avatars)
- [x] Agent networks (27 categories)
- [x] Brain profiles + Workspace Brain
- [x] Chat with multi-model support

### AI & Execution
- [x] Real LLM-powered workflow execution engine
- [x] Visual workflow builder (drag-and-drop)
- [x] Campaign builder with scheduling
- [x] Vibe coding, content generator, reference intel
- [x] Agent-to-agent collaboration within workflows

### Enterprise Features
- [x] Dynamic pricing system (admin CRUD + inline editing)
- [x] Functional API integrations hub
- [x] Code explorer (tree, viewer, search, ZIP)
- [x] Organization/Team management (multi-tenancy)
- [x] Trust analytics with trends & anomaly detection
- [x] Agent suggestions / self-expanding agents
- [x] Stripe payment integration

### Admin Control Panel — Sidebar Breakdown
- [x] Overview (/admin/overview)
- [x] Analytics (/admin/analytics)
- [x] Users (/admin/users)
- [x] Agents (/admin/agents)
- [x] Transactions (/admin/transactions)
- [x] Pricing & Packages (/admin/pricing-manager) — **UNIFIED** (merged Plan Editor + Pricing Manager + Custom Packages)
- [x] API Keys & Integrations (/admin/api-keys)
- [x] Payment Setup (/admin/payments)
- [x] Email SMTP (/admin/smtp)
- [x] Branding & Domain (/admin/branding)
- [x] Knowledge Base (/admin/knowledge)
- [x] Audit Log (/admin/audit)
- [x] Code Explorer (/admin/code-explorer)
- [x] Access Control (/rbac)
- [x] Circuit Breakers (/circuit-breakers)
- [x] Cost Governance (/cost-governance)

### PWA / Mobile
- [x] manifest.json with MAARS metadata
- [x] Service worker (sw.js) with cache-first strategy
- [x] PWA icons (192x192, 512x512)
- [x] Apple mobile web app meta tags
- [x] Installable on mobile via "Add to Home Screen"

### Multi-Org Switching
- [x] Org Switcher in sidebar (above search)
- [x] Create Organization flow
- [x] Personal Workspace default

### Advanced Dashboard Widgets
- [x] Auto-refresh toggle (30s interval)
- [x] Last refresh timestamp
- [x] Manual refresh button
- [x] Widget catalog with 8 types

### Unified Pricing Admin (Feb 10, 2026)
- [x] Consolidated Plan Editor + Pricing Manager into single page
- [x] Create new plans with full fields (ID, name, pricing, credits, agents, commander, team, features)
- [x] Delete plans (except Free)
- [x] Per-plan margin controls (100%, 200%, 500%, 1000%, custom)
- [x] Features editor with badge display and inline add/remove
- [x] Commander toggle and Team Members per plan
- [x] Profit Margin Calculator with live AI cost sync
- [x] Custom Packages (Credit Presets, Extra Credit Packs)
- [x] Publish Pricing Changes
- [x] No overlapping/duplicate UI components

## Credentials
- Admin: management.maars@marsgc.net / Admin123!

## P2 Backlog
- Mobile-native app wrapper (React Native / Capacitor)
- Advanced multi-org switching with shared resources
- Custom branded login pages per org
- Billing history / invoice dashboard
- Advanced trust analytics and customizable dashboard widgets
- Agent-to-agent collaboration within workflows (further enhancements)
- Further multi-tenancy enhancements (org-switcher improvements)
- Align backend route files to import directly from new services instead of kernel_service.py shim
