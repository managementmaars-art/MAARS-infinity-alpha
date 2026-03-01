# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (This Session - Mar 1, 2026)

### Notification Center
- Bell icon with unread count badge in Dashboard and Chat headers
- Dropdown panel with notification list, "Read all", "Clear" buttons
- Auto-notifications on: user registration (welcome), credits low (<=20), team invite accepted
- Auto-polls every 30 seconds for new notifications
- Endpoints: GET /api/notifications, POST /read, POST /read-all, DELETE /clear

### User Usage Insights Dashboard
- Personal stats at /insights: messages, chats, credits, ratings, streak
- 30-day activity chart, favorite agents, agent recommendations
- Sidebar navigation: "My Insights"

### User Onboarding Flow
- 5-step guided tour: Welcome → Meet Agents → How It Works → Features → Ready
- Persisted in MongoDB, shows once per user

### Agent Performance Scoring
- Thumbs up/down feedback on every AI response
- Agent Performance Dashboard in admin Analytics tab

### Customer Analytics Dashboard
- KPI cards, 7 charts, Live Activity Feed (15s auto-refresh)
- Export to CSV

### AI Controllability
- Agent Enable/Disable Toggle, Temperature/Max Tokens sliders

### Gmail SMTP Configuration UI
- Admin tab for credentials with test email and setup guide

### Backend Refactoring
- Extracted 15 Pydantic models to models/schemas.py
- Extracted DEFAULT_AGENTS, constants, tool config to config.py
- server.py: 5887 → 5552 lines (~335 lines extracted)
- Modular directory: models/, routes/, services/, config.py

## Previously Implemented
- 21 AI agents with Brain Editor, Commander AI, Agent Collaboration
- Auto model selection (25 models), File/Image/Video generation
- Voice mode (OpenAI TTS), Dynamic Stripe subscriptions + Credits
- Team collaboration, JWT + Google OAuth, Kubernetes /health

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Continue route extraction (admin routes to routes/admin.py)
- P1: Third-party integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI, White-label options

## Test Reports (All 100%)
- iteration_26-31: Previous features
- iteration_32: Notification Center (12/12 backend + all frontend)
