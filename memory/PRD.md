# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard.

## Implemented Features

### Auto Image Generation
- Smart detection based on keywords + agent role
- Visual agents (Graphic Designer) auto-trigger
- GPT Image 1 with prompt refinement, inline rendering

### Auto Video Generation (Feb 28 2026)
- Smart detection for video/commercial/animation requests
- Video agents (Riley Chen) auto-trigger
- Sora 2 background generation (non-blocking, ~2-5 min)
- Polling-based UI: shows spinner during gen, auto-updates with video player
- Download MP4 support

### LLM Fallback System
- Auto-retry across models: Selected → GPT-5.2 → GPT-4o → GPT-4o-mini → Gemini 3 Flash
- No raw errors shown to users

### Smart Auto Model Selection
- Keyword + agent role scoring for task classification
- Routes to reliable providers (OpenAI/Gemini) by default

### Agent Card Hover Popups
- Floating popup on hover with full avatar, role badge, capabilities, description

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth, 21 AI agents
- Resizable sidebar, sticky input, 25+ models across 9 providers
- ReAct autonomous agents with tool execution
- 9 service integrations (Slack, GitHub, SendGrid, etc.)
- Stripe subscriptions, credit system, admin dashboard

## Backlog
- P1: Teams & Collaboration (invites, shared agents, roles)
- P1: Commander AI as purchasable add-on
- P2: Refactor server.py / AdminDashboard.jsx
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
