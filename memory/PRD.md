# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform (rebranded from Martian AI to MAARS Command) with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard.

## Implemented Features

### Branding
- Rebranded from "Martian AI" to "MAARS Command" across entire app
- MAARS Global Corporation watermark (fixed bottom-right, scroll-adapted)
- "Powered by GPT-5.2, Claude & Gemini" badge

### Credits System UI
- Credit balance pill in header (amber diamond icon + amount)
- "Buy Credits" golden button
- Dropdown panel: Available Credits, Free/Monthly/Top-up breakdown, Manage Subscriptions
- Buy Credits modal: 5 preset packages (100/$20 to 6000/$1000) + custom amount input
- Stripe checkout integration for purchases

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
