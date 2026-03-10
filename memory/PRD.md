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

### Avatar Fix & Persistence (Mar 10, 2026)
- [x] Fixed root cause: seed_default_agents() was overwriting photo avatars with SVG data URIs on every restart
- [x] Modified agent_service.py to preserve non-SVG avatar URLs during seeding
- [x] Updated 417 infinity agents from SVG data URIs to /api/static/avatars/{agent_id}.png
- [x] Generated 2 missing avatar images for agent_10r_discovery and agent_10aa_quality_mfg
- [x] All 458 agents now have real AI-generated human portrait photos

### About Page & PDF Branding Update (Mar 10, 2026)
- [x] Updated summary.py: all "MAARS Infinity" / "MAARS ∞" references changed to "MAARS Command"
- [x] PDF cover, header, and description now say "MAARS Command"
- [x] Frontend download filename: "MAARS-Command-Documentation.pdf"
- [x] Health endpoint returns "MAARS Command"

### Rebranding to MAARS Command (Feb 10, 2026)
- [x] Full rebrand from "MAARS ∞" to "MAARS Command"
- [x] Color scheme: original indigo/violet theme
- [x] Company logo prominent throughout all pages
- [x] Watermark in bottom-right corner

### Agent Gallery View (Feb 10, 2026)
- [x] Cards view with hover-to-expand popup
- [x] Gallery view with 8-column portrait grid
- [x] Search, agent visibility toggle, view mode switching

### Professional Dashboard (Feb 10, 2026)
- [x] Command Center with stats, Commander Orion only, Quick Actions
- [x] Credits display in sidebar

### Core Platform
- [x] User auth (JWT) + RBAC + Admin panel (16+ pages)
- [x] Agent catalog, networks, brain profiles, workspace brain
- [x] Chat with multi-model support, command palette, voice commands
- [x] Workflow builder, campaign builder, vibe coding
- [x] Dynamic pricing, Stripe integration, PWA support
- [x] Organization/team management, trust analytics, code explorer

## Credentials
- Admin: management.maars@marsgc.net / admin123

## Launch Readiness Status (Mar 10, 2026)
- Iteration 85: 11/11 tests PASSED (100%)
- All 458 agents with real portrait photos
- PDF download working with MAARS Command branding
- Branding consistent throughout application

## P2 Backlog / Future
- Advanced trust analytics and customizable dashboard widgets
- Agent-to-agent collaboration within workflows
- Mobile-native app wrapper
- Billing history / invoice dashboard
