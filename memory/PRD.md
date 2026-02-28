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
- Buy Credits modal: Dynamic packages fetched from /api/plans (admin-configured prices)
- Currency toggle (USD/BDT), Stripe checkout integration

### Admin Profit Calculator (Updated Feb 28, 2026)
- AI Cost/Credit is read-only, auto-populated from real usage data
- AI cost auto-updates across all profit calculators when usage data changes

### Admin Agent Capability Management (Added Feb 28, 2026)
- Expandable agent rows in Agents tab with "Generation Permissions" section
- Toggle buttons for: can_generate_image, can_generate_video, can_generate_pdf, can_generate_files
- Real-time badge display (IMG, VID, PDF, FILES) on collapsed agent rows
- Backend PUT /api/admin/agents/{agent_id}/settings endpoint

### Smart Clarification Questions (Added Feb 28, 2026)
- All 21 agents ask targeted clarifying questions before generating deliverables
- Agents ask about specifics: audience, goals, tone, format, constraints, etc.
- Simple factual questions and greetings get direct answers (no unnecessary Q&A)
- Conversation history (last 20 messages) passed to LLM for context continuity
- Agents use answers from previous messages to avoid re-asking
- Users can say "just do it" to skip questions and get output with reasonable defaults

### Auto File Generation
- PDF, DOCX, XLSX, CSV, TXT generation with download links inline
- Unicode-safe PDF generation with reportlab + markdown formatting

### Chat Management
- Delete chats, auto-expanding textarea

### Auto Image Generation
- GPT Image 1 with smart detection + prompt refinement

### Auto Video Generation
- Sora 2 background generation (~2-5 min), image-to-video support

### LLM Fallback + Smart Auto Selection
- Auto-retry across models

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
