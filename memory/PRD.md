# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform (rebranded from Martian AI to MAARS Command) with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard.

## Implemented Features

### Branding
- Rebranded from "Martian AI" to "MAARS Command" across entire app
- MAARS Global Corporation watermark (fixed bottom-right, scroll-adapted)

### Credits System UI
- Global credit balance pill (fixed top-right, visible on all authenticated pages)
- Buy Credits modal: Dynamic packages from /api/plans (admin-configured prices)
- Currency toggle (USD/BDT), Stripe checkout integration

### Admin Dashboard
- Live profit calculator with auto-updating AI cost
- Agent Capability Management: expandable rows with toggles for image/video/pdf/files generation
- Real-time badge display (IMG, VID, PDF, FILES)

### Smart Clarification Questions (Feb 28, 2026)
- All 21 agents ask targeted clarifying questions before generating deliverables
- Conversation history (last 20 messages) for context continuity
- Simple questions get direct answers

### User Feedback Fixes (Feb 28, 2026)
- Fixed "currentAgent is not defined" runtime error on file generation buttons
- Fixed "Failed to load data" — resilient API fetching on Dashboard/Tasks
- Fixed scrolling issue in task agent assignment (scrollable container with max-height)
- Changed "Danger Zone" → "Account" in Settings
- Agent roles now visible in task assignment dialog and task cards
- Task "in progress" status now shows "working on it..."
- Agent cards show complete info (name, role, description, capabilities, tools)

### Auto File/Image/Video Generation
- PDF, DOCX, XLSX, CSV, TXT generation with inline download links
- GPT Image 1 with smart detection + prompt refinement
- Sora 2 background video generation, image-to-video support

### Deployment
- Added /health endpoint for Kubernetes probes (directly on app, not api_router)

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
