# MAARS Command — Product Requirements Document

## Overview
MAARS Command is an autonomous AI enterprise operating system by MAARS Global Corporation.  
458+ AI agents across 27 networks, 16 system layers, powered by 13 LLM providers with 45+ models.

## Brand Identity
- **Name**: MAARS Command (by MAARS Global Corporation)
- **Logo**: MAARS Global Corporation globe logo (mgc-logo.png)
- **Colors**: Indigo/Violet theme - Dark backgrounds with indigo (#6366f1) and violet (#8b5cf6) accents
- **Typography**: Outfit (headings), system fonts (body)
- **Watermark**: Bottom-right corner with "MAARS COMMAND by MAARS Global Corporation"

## Architecture
- **Backend**: FastAPI (Python) + MongoDB + WebSocket + Static file serving
- **Frontend**: React 18 + Tailwind CSS + Shadcn/UI (PWA-enabled)
- **Payments**: Stripe
- **AI**: OpenAI, Anthropic, Google, Groq, Together AI, Fireworks, AI21, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs

## Completed Features

### Rebranding to MAARS Command (Feb 10, 2026)
- [x] Full rebrand from "MAARS ∞" to "MAARS Command"
- [x] Color scheme reverted to original indigo/violet theme
- [x] Company logo prominent throughout all pages (landing, login, sidebar, watermark)
- [x] Watermark moved to bottom-right corner
- [x] Health endpoint updated to return "MAARS Command"

### Agent Gallery View (Feb 10, 2026)
- [x] Cards view with compact agent cards showing avatar, name, role
- [x] Gallery view with 8-column portrait grid for all 458 agents
- [x] Hover-to-expand popup on both views: full portrait, role, name, capabilities, description
- [x] Agent visibility toggle: admin can hide/show agents
- [x] Search functionality by name, role, or capability
- [x] PUT /api/agents/{agent_id}/visibility endpoint

### Professional Dashboard (Feb 10, 2026)
- [x] Command Center with branded UI and stats grid
- [x] Shows only Commander Orion agent for focused experience
- [x] Quick Actions: New Chat, Create Task, Browse Agents, Create Agent
- [x] Recent Conversations section
- [x] Project missions tracking

### AI Portrait Avatars (Feb 10, 2026)
- [x] All 458 agents have unique AI-generated human-like portraits
- [x] CDN-hosted images via emergentagent.com static storage
- [x] Avatars display correctly in all views (cards, gallery, hover popup, chat, dashboard)

### Core Platform
- [x] User auth (JWT) + RBAC + Admin panel (16+ pages)
- [x] Agent catalog, networks, brain profiles, workspace brain
- [x] Chat with multi-model support, command palette, voice commands
- [x] Workflow builder, campaign builder, vibe coding
- [x] Dynamic pricing, Stripe integration, PWA support
- [x] Organization/team management, trust analytics, code explorer
- [x] Credits system with display in sidebar

## Credentials
- Admin: management.maars@marsgc.net / admin123

## Launch Readiness Status (Mar 10, 2026)
- All 17 launch-readiness tests PASSED (100% success rate)
- Avatars displaying correctly across all views
- Branding consistent throughout application
- All core features operational

## P1 Backlog
- None (application is launch-ready)

## P2 Backlog / Future
- Advanced trust analytics and customizable dashboard widgets
- Agent-to-agent collaboration within workflows
- Mobile-native app wrapper
- Advanced multi-org switching
- Billing history / invoice dashboard
- Custom branded login pages per org
