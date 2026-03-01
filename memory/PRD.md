# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (This Session - Mar 1, 2026)

### User Usage Insights Dashboard
- Personal stats page at /insights: messages sent, total chats, credits, ratings, activity streak
- Daily activity chart (30 days) using recharts
- Favorite agents ranked by usage
- Agent recommendations (agents user hasn't tried yet)
- Navigation link in sidebar: "My Insights"
- Endpoint: GET /api/user/insights

### User Onboarding Flow
- 5-step guided tour: Welcome → Meet Agents → How It Works → Features → Ready
- Personalized greeting, agent previews, sample prompts
- Skip tour or Start Chatting to complete, persisted in MongoDB
- Endpoints: GET /api/auth/me (onboarding_completed), POST /api/auth/onboarding-complete

### Agent Performance Scoring
- Thumbs up/down feedback on every AI response
- Agent Performance Dashboard in admin Analytics tab
- Color-coded satisfaction bars
- Endpoints: POST /feedback, GET /admin/agent-performance

### Customer Analytics Dashboard
- KPI cards, 7 recharts charts, Live Activity Feed (auto-refresh 15s)
- Export to CSV, Agent Performance section

### AI Controllability
- Agent Enable/Disable Toggle
- Per-agent Temperature (0.0-2.0) and Max Tokens (256-16384) sliders
- Values passed to LLM calls

### Gmail SMTP Configuration UI
- Admin tab for Gmail SMTP credentials with test email and setup guide

### Backend Refactoring
- Phase 1: Extracted 15 Pydantic models to models/schemas.py
- Phase 2: Extracted DEFAULT_AGENTS (257 lines), CLARIFICATION_INSTRUCTION, AGENT_TOOLS, AGENT_TOOL_MAP (150 lines) to config.py
- server.py reduced from 5887 to 5487 lines (~400 lines extracted)
- Modular directory: models/, routes/, services/, config.py

## Previously Implemented
- 21 AI agents with Brain Editor, Commander AI, Agent Collaboration
- Auto model selection (25 models), File/Image/Video generation
- Voice mode (OpenAI TTS), Dynamic Stripe subscriptions + Credits
- Team collaboration, JWT + Google OAuth, Kubernetes /health

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Continue route extraction to routes/admin.py
- P1: Third-party integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI, White-label options

## Test Reports (All 100%)
- iteration_26: Analytics + SMTP
- iteration_27: Activity Feed
- iteration_28: Agent Controls
- iteration_29: Feedback + Performance
- iteration_30: Onboarding Flow
- iteration_31: Insights Page + Refactoring
