# MAARS Infinity — Product Requirements Document

## Overview
MAARS ∞ is an autonomous AI enterprise operating system by MAARS Global Corporation.  
458+ AI agents across 27 networks, 16 system layers, powered by 13 LLM providers with 45+ models.

## Brand Identity
- **Logo**: MAARS Global Corporation globe logo (iridescent blue/purple/cyan)
- **Colors**: Deep space navy (#070721), Electric blue (#3b82f6), Cyan (#06b6d4), Magenta (#d946ef)
- **Typography**: Outfit (headings), Inter (body), JetBrains Mono (code)

## Architecture
- **Backend**: FastAPI (Python) + MongoDB + WebSocket + Static file serving
- **Frontend**: React 18 + Tailwind CSS + Shadcn/UI (PWA-enabled)
- **Payments**: Stripe
- **AI**: OpenAI, Anthropic, Google, Groq, Together AI, Fireworks, AI21, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs

## Completed Features

### Brand Overhaul (Feb 10, 2026)
- [x] MAARS GC logo placed in: sidebar, navbar, landing page, login, footer, watermark
- [x] Color scheme: deep navy + electric blue + cyan + magenta throughout
- [x] CSS variables updated in index.css for consistent theming
- [x] Gradient text, glow effects, glass morphism using brand palette
- [x] Watermark: centered bottom with logo + "MAARS GLOBAL CORPORATION"

### Agent Gallery View (Feb 10, 2026)
- [x] Compact 12-column grid showing all 458 portrait thumbnails
- [x] Hover-to-preview tooltip: name, role, description, capabilities, tools
- [x] View toggle: Cards (full) / Gallery (compact) modes
- [x] Agent visibility toggle: admin can hide/show agents (eye icon)
- [x] PUT /api/agents/{agent_id}/visibility endpoint

### Professional Dashboard (Feb 10, 2026)
- [x] Command Center with branded UI
- [x] Stats grid: Chats, Tasks, Completed, Custom Agents
- [x] Quick Actions: New Chat, Create Task, Create Agent
- [x] Agent cards with hover popup preview (avatar, role, capabilities, description)
- [x] Recent Conversations section

### AI Portrait Avatars (Feb 10, 2026)
- [x] All 458 agents have unique AI-generated human-like portraits
- [x] 41 CDN-hosted originals + 415 locally generated via GPT Image 1 + 2 CDN
- [x] Served via /api/static/avatars/ with FastAPI StaticFiles

### Core Platform
- [x] User auth (JWT) + RBAC + Admin panel (16+ pages)
- [x] Agent catalog, networks, brain profiles, workspace brain
- [x] Chat with multi-model support, command palette, voice commands
- [x] Workflow builder, campaign builder, vibe coding
- [x] Dynamic pricing, Stripe integration, PWA support
- [x] Organization/team management, trust analytics, code explorer

## Credentials
- Admin: management.maars@marsgc.net / Admin123!

## P2 Backlog
- Mobile-native app wrapper
- Advanced multi-org switching
- Billing history / invoice dashboard
- Custom branded login pages per org
