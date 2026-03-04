# MAARS Command — PRD
## By MAARS Global Corporation

## Original Problem Statement
Build "MAARS Command," a commercial, production-ready AI business operating system that merges the capabilities of Sintra.ai (preset specialist business agents) and Emergent.sh (autonomous execution, memory, tool use, and app building).

## Architecture
- **Backend**: FastAPI (Python) + MongoDB + Emergent Integrations SDK
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **AI**: OpenAI (GPT-5.2), Anthropic (Claude Sonnet 4.5), Google Gemini (3 Flash, 2.5 Pro) via Emergent LLM Key
- **Payments**: Stripe

## What's Been Implemented

### Phase 1-4 (Previous Sessions)
- 41-agent AI workforce with Custom Brain Profiles
- Autonomous Orchestration Engine (goal → plan → execute)
- KPI Dashboard, Collaboration Engine, Quality Control
- Simulation/Execution mode, Credit-based billing

### Phase 5 (March 4, 2026 — Session 1)
- Agent Activity Monitor, Vibe Coding App Builder
- Universal Reference Intelligence, Flexible LLM Config
- Real-World Action Layer (Google OAuth)

### Phase 6 (March 4, 2026 — Session 2)
- Quality Control & Failure Recovery (Critic Module, retry chain, escalation)
- Model-Agnostic LLM Router (task complexity classification, auto-routing)
- Autonomous Collaboration Engine (9 domains, cross-domain triggers)
- Content Generator (8 types with Style Blueprint integration)

### Phase 7 (March 4, 2026 — Session 3)
- Consistent Sidebar (DashboardLayout across ALL 20+ pages, collapsible)
- About Page (comprehensive system docs, all 41 agents, 12 systems)
- **Command Palette**: VS Code/Notion-style quick search (press `/` or `Cmd+K`)
  - Search across pages (20+), agents (41), and quick actions (4)
  - Keyboard navigation (arrows, Enter, Escape)
  - Recent searches in localStorage
  - Grouped results: Recent, Pages, Agents, Quick Actions
  - Sidebar search button with `/` hint + mobile search icon

### Phase 8 (March 4, 2026 — Session 4)
- **Voice Command Interface**: Microphone button in Command Palette
  - Records audio via browser MediaRecorder API (WebM format)
  - Sends to POST /api/voice/transcribe (OpenAI Whisper via Emergent SDK)
  - Transcribed text auto-fills search input for navigation/actions
  - Visual states: idle, recording (pulse), transcribing (spinner)
  - "Voice" hint in Command Palette footer
- **Admin Code Explorer**: Full codebase browser at /admin/code-explorer
  - GET /api/admin/code/tree — recursive file tree (backend/, frontend/src/)
  - GET /api/admin/code/file?path=... — file content with language detection
  - GET /api/admin/code/search?q=... — file name search (max 50 results)
  - File tree panel with expand/collapse, file sizes, language-colored icons
  - Code viewer panel with line numbers, copy button, language badge
  - Path traversal protection, admin-only access (403 for non-admin)
  - Sidebar nav item + Command Palette entry for admin users

## Testing Status
- Iteration 53: 26/26 (100%)
- Iteration 54: 20/20 (100%)
- Iteration 55: 27/27 (100%)
- Iteration 56: Frontend 100%
- Iteration 57: Frontend 100% — Command Palette all 13 scenarios passed
- Iteration 58: 24/24 backend + all frontend UI verified (Voice + Code Explorer)

## Credentials
- Admin: management.maars@marsgc.net / admin123

## Prioritized Backlog

### P0 (Completed)
- Voice Command Interface
- Admin Code Explorer

### P1
- Memory Governance (versioning, pruning, relevance scoring)
- WebSocket real-time updates for Activity Monitor

### P2
- Enterprise RBAC with permissions UI
- Advanced integrations (WhatsApp, Meta Ads, Shopify, ERP)
- Cost Governance active monitoring
- Custom agent creation by users
- Campaign Builder (Reference Intel -> Content Gen -> Social scheduling)

### P3
- Multi-tenant isolation, Mobile app wrapper
- Workflow builder UI, Architecture diagrams
