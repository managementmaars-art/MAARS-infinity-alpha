# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform (rebranded from Martian AI to MAARS Command) with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard.

## Implemented Features

### Branding
- Rebranded from "Martian AI" to "MAARS Command" across entire app
- MAARS Global Corporation watermark (fixed bottom-right, scroll-adapted)
- "Powered by GPT-5.2, Claude & Gemini" badge

### Credits System UI (Updated Feb 28, 2026)
- Global credit balance pill (fixed top-right, visible on all authenticated pages)
- "Buy Credits" golden button with dropdown panel
- Dropdown: Available Credits, Free/Monthly/Top-up breakdown, Manage Subscriptions
- Buy Credits modal: Dynamic packages fetched from /api/plans (admin-configured prices)
- Currency toggle (USD/BDT) in Buy Credits modal
- Custom amount input for flexible purchases
- Stripe checkout integration for all purchases

### Admin Profit Calculator (Updated Feb 28, 2026)
- AI Cost/Credit is read-only, auto-populated from real usage data
- Removed editable $/Credit inputs from plan editors and credit pack rows
- AI cost auto-updates across all profit calculators when usage data changes

### Chat Management
- Delete chats from Dashboard (hover trash icon on recent conversations)
- Delete chats from Chat sidebar (existing)

### Auto Image Generation
- GPT Image 1 with smart detection + prompt refinement, inline rendering

### Auto Video Generation
- Sora 2 background generation (non-blocking, ~2-5 min)
- Polling UI: spinner during gen, auto-updates with video player

### LLM Fallback + Smart Auto Selection
- Auto-retry across models, routes to reliable OpenAI/Gemini providers

### Agent Card Hover Popups
- Floating popup with full avatar, role badge, capabilities, description

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth, 21 AI agents
- ReAct autonomous agents, 9 service integrations, Stripe subscriptions

## Backlog
- P1: Teams & Collaboration (invites, shared agents, roles)
- P1: Commander AI as purchasable add-on
- P2: Refactor server.py / AdminDashboard.jsx
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
