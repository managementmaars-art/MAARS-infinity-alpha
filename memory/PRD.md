# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Custom Domain UI & White-Label Branding (Mar 1, 2026 - Latest)
- **Branding & Domain** admin tab with 4 sections:
  - Brand Identity: Platform Name, Tagline, Footer Text, Support Email
  - Logo & Favicon: File upload (PNG/JPG/SVG/WebP, 5MB max) + URL paste
  - Brand Colors: Primary & Accent color pickers with hex input & live preview
  - Custom Domain: Domain input, CNAME DNS instructions, Verify DNS button
- **BrandingProvider** context: Applies CSS variables, dynamic favicon, page title
- **BrandFooter** dynamically shows platform name and footer text
- Backend: GET/POST /api/admin/branding, POST /upload-logo, POST /verify-domain, GET /branding/public
- All 18 tests passed (iteration_33)

### Notification Center (Mar 1, 2026)
- Bell icon with unread count badge in Dashboard and Chat headers
- Dropdown panel with notification list, "Read all", "Clear" buttons
- Auto-notifications on: user registration, credits low, team invite accepted
- Endpoints: GET /api/notifications, POST /read, POST /read-all, DELETE /clear

### User Usage Insights Dashboard
- Personal stats at /insights: messages, chats, credits, ratings, streak
- 30-day activity chart, favorite agents, agent recommendations

### User Onboarding Flow
- 5-step guided tour: Welcome → Meet Agents → How It Works → Features → Ready

### Agent Performance Scoring
- Thumbs up/down feedback on every AI response
- Agent Performance Dashboard in admin Analytics tab

### Customer Analytics Dashboard
- KPI cards, 7 charts, Live Activity Feed (15s auto-refresh), Export to CSV

### AI Controllability
- Agent Enable/Disable Toggle, Temperature/Max Tokens sliders

### Gmail SMTP Configuration UI
- Admin tab for credentials with test email and setup guide

### Backend Refactoring (Phase 1)
- Extracted 15 Pydantic models to models/schemas.py
- Extracted DEFAULT_AGENTS, constants, tool config to config.py

## Previously Implemented
- 21 AI agents with Brain Editor, Commander AI, Agent Collaboration
- Auto model selection (25 models), File/Image/Video generation
- Voice mode (OpenAI TTS), Dynamic Stripe subscriptions + Credits
- Team collaboration, JWT + Google OAuth, Kubernetes /health

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Continue route extraction (admin routes to routes/admin.py) - server.py still ~5600 lines
- P1: Third-party integrations (Slack, Calendly, Airtable) - UI exists, backend logic not implemented
- P2: AdminDashboard.jsx refactoring - extract remaining tabs into components
- P2: Complete server.py modularization - extract auth, chats, teams routes

## Architecture
```
/app/backend/
├── server.py (5600+ lines - monolithic, needs refactoring)
├── config.py (agent definitions, tool configs)
├── models/schemas.py (Pydantic models)
├── uploads/ (file storage)
└── tests/

/app/frontend/src/
├── App.js (BrandingProvider wraps app)
├── pages/
│   ├── AdminDashboard.jsx (tabs: overview, analytics, users, agents, transactions, pricing, apikeys, payments, smtp, branding)
│   ├── BrandingTab.jsx (NEW - branding & domain admin UI)
│   ├── AnalyticsTab.jsx, SmtpConfigTab.jsx
│   ├── AgentChat.jsx, Dashboard.jsx, Insights.jsx
│   └── ...
└── components/
    ├── BrandingProvider.jsx (NEW - dynamic branding context)
    ├── BrandFooter.jsx (updated - uses branding context)
    ├── OnboardingFlow.jsx, NotificationCenter.jsx
    └── ...
```

## Test Reports (All 100%)
- iteration_33: Branding & Custom Domain (18/18 backend + all frontend)
- iteration_26-32: Previous features
