# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (This Session - Mar 1, 2026)

### User Onboarding Flow
- 5-step guided tour: Welcome → Meet Agents → How It Works → Features → Ready
- Personalized greeting, agent avatars preview, feature highlights, sample prompt
- Skip tour and Start Chatting buttons both mark completion
- Onboarding state persisted in MongoDB, only shows once per user
- Endpoints: GET /api/auth/me (onboarding_completed field), POST /api/auth/onboarding-complete

### Agent Performance Scoring
- Thumbs up/down feedback on every AI assistant response
- Agent Performance Dashboard in admin Analytics tab
- Color-coded satisfaction bars (green >=80%, amber >=50%, red <50%)
- Endpoints: POST /feedback, GET /admin/agent-performance

### Customer Analytics Dashboard
- KPI cards (Total Users, Active 7d/30d, Total Chats, Revenue, MRR)
- 7 recharts charts + Agent Performance section + Live Activity Feed
- Export to CSV with users, agent usage, payments, summary

### AI Controllability
- Agent Enable/Disable Toggle (hidden from users when disabled)
- Per-agent Temperature slider (0.0-2.0) and Max Tokens slider (256-16384)
- Temperature/max_tokens passed to LLM calls via with_params()

### Gmail SMTP Configuration UI
- Admin tab for Gmail SMTP credentials with test email functionality
- Step-by-step setup guide for App Passwords

### Live Activity Feed
- Auto-refreshing (15s) feed showing signups, payments, chats, team events

### Backend Refactoring (Phase 1)
- Extracted 15 Pydantic models to /app/backend/models/schemas.py
- Created modular directory structure: models/, routes/, services/

## Previously Implemented (Before This Session)
- 21 specialized AI agents with Brain Editor
- Commander AI background delegation + Agent Collaboration
- Auto model selection (25 models, 8 providers)
- File/Image/Video generation (PDF, DOCX, DALL-E 3, Sora 2)
- Voice mode (OpenAI TTS, 9 voices)
- Dynamic Stripe subscriptions + Credit system
- Commander AI as purchasable add-on ($15/month)
- Team collaboration (invites, roles, shared chats)
- JWT + Google OAuth authentication
- Kubernetes-ready with /health endpoint

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP via Admin > Email (SMTP) tab
- [ ] Set custom domain + FRONTEND_URL

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Backend refactoring Phase 2 — extract admin routes to routes/admin.py, LLM services to services/llm.py
- P1: Third-party integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI
- P2: White-label/branding options

## Architecture
```
/app/backend/
├── server.py           (~5765 lines — main app)
├── models/schemas.py   (15 Pydantic models)
├── routes/             (ready for extraction)
├── services/           (ready for extraction)
├── tests/              (pytest files from testing agent)
└── .env

/app/frontend/src/pages/
├── AdminDashboard.jsx  (admin with tabs)
├── AnalyticsTab.jsx    (analytics + performance scoring)
├── SmtpConfigTab.jsx   (SMTP configuration)
├── OnboardingFlow.jsx  (5-step user onboarding)
├── AgentChat.jsx       (chat + feedback)
├── Dashboard.jsx       (main dashboard + onboarding trigger)
├── Team.jsx, Settings.jsx, PricingPage.jsx, etc.
```

## Test Reports
- iteration_26: Analytics + SMTP (100%)
- iteration_27: Activity Feed (100%)
- iteration_28: Agent Controls (100%)
- iteration_29: Feedback + Performance (100%)
- iteration_30: Onboarding Flow (100%)
