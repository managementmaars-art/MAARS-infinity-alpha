# MAARS Command -- Product Requirements Document

## Overview
MAARS Command is an autonomous AI enterprise operating system by MAARS Global Corporation.
458+ AI agents across 28 networks, 21 system layers, powered by 13 LLM providers with 45+ models.

## Brand Identity
- **Name**: MAARS Command (by MAARS Global Corporation)
- **Email**: support.maars@marsgc.net
- **Colors**: Indigo/Violet theme
- **Watermark**: Bottom-right corner

## Architecture
- **Backend**: FastAPI + MongoDB + WebSocket
- **Frontend**: React 18 + Tailwind CSS + Shadcn/UI
- **Payments**: Stripe
- **AI**: 13 LLM providers (OpenAI, Anthropic, Google, Groq, etc.)

## Completed Features

### About Page Overhaul (Mar 10, 2026)
- [x] Dynamic loading of ALL 458+ agents from API, grouped by 28 network categories
- [x] Comprehensive A-Z documentation: 21 core systems, security/governance, architecture, AI providers, costs
- [x] Print-ready PDF via window.print() with @media print CSS (replaces backend FPDF)
- [x] Email fixed to support.maars@marsgc.net throughout (About, Pricing)
- [x] New sections: Security & Governance, Agent Team Builder, Trust Analytics, Workflow Builder, Campaign Builder

### Agent Team Builder (Mar 10, 2026) -- P1
- [x] Backend: /api/agent-teams CRUD (POST, GET, GET/:id, PUT/:id, DELETE/:id)
- [x] Frontend: /team-builder page with full CRUD
- [x] Agent selection from 458+ pool with search and network filter
- [x] Team cards with avatar preview, agent count, network coverage
- [x] Sidebar nav item under AI Tools

### Advanced Trust Analytics (Mar 10, 2026) -- P1
- [x] Trust Distribution chart (Excellent/Good/Fair/Poor breakdown)
- [x] Top Performers ranking section
- [x] Needs Improvement ranking section
- [x] Enhanced TrustScores.jsx with 3-column analytics widgets

### Agent-to-Agent Collaboration (Mar 10, 2026) -- P1
- [x] Collaboration stats dashboard (Total, Agents Involved, Completed, Pending)
- [x] "Initiate Collaboration" form with sender/receiver agent selection
- [x] Collaboration types: info sharing, review request, data handoff, coordination
- [x] Enhanced CollaborationEngine.jsx

### Previous Completed
- [x] Avatar fix (seed persistence), rebranding to MAARS Command, dashboard, agent gallery
- [x] Full platform: auth, RBAC, chat, workflows, pricing, Stripe, PWA, 50+ pages

## Credentials
- Admin: management.maars@marsgc.net / admin123

## Testing Status
- Iteration 86: 19/19 features PASS (100%)
- Backend: 14/14 API tests PASS
- Frontend: 19/19 UI features verified

## P2 Backlog / Future
- Mobile-native app wrapper
- Billing history / invoice dashboard
- Custom branded login pages per org
