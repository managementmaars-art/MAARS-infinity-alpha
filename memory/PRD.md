# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Agent Performance Scoring (Added Mar 1, 2026)
- **Thumbs Up/Down feedback** on every AI assistant response — users rate quality inline
- **Agent Performance Dashboard** in admin Analytics tab — satisfaction rates, thumbs up/down counts, total messages per agent
- Color-coded performance bars (green >=80%, amber >=50%, red <50%)
- Feedback stored with timestamp and user attribution
- Endpoints: POST /api/chats/{chat_id}/messages/{message_id}/feedback, GET /api/admin/agent-performance

### AI Controllability & Flexibility (Added Mar 1, 2026)
- **Agent Enable/Disable Toggle:** Admin can activate/deactivate any agent. Disabled agents hidden from users.
- **Temperature Control:** Per-agent temperature slider (0.0 Precise → 2.0 Creative) in Brain Editor
- **Max Tokens Control:** Per-agent max response length slider (256 → 16384) in Brain Editor
- **Analytics Export:** Download full analytics as CSV (Users, Agent Usage, Payments, Summary)

### Real-time Activity Feed (Added Mar 1, 2026)
- Live feed on Analytics dashboard showing recent signups, payments, chats, team creations
- Auto-refreshes every 15 seconds with manual refresh button

### Customer Analytics Dashboard (Added Mar 1, 2026)
- KPI cards (Total Users, Active 7d/30d, Total Chats, Revenue, MRR)
- 7 recharts charts: daily signups, messages, revenue, API cost, agent usage, subscription distribution, token usage
- Top Users by Messages, Cost by AI Model breakdown

### Gmail SMTP Configuration UI (Added Mar 1, 2026)
- Admin tab for securely entering Gmail SMTP email and App Password
- Test email functionality, step-by-step setup guide

### Backend Refactoring (Started Mar 1, 2026)
- Extracted 15 Pydantic models to `/app/backend/models/schemas.py`
- Created modular directory structure: `models/`, `routes/`, `services/`
- server.py reduced from ~5900 to ~5765 lines (first phase)

### Core Platform Features (Complete)
- 21 specialized AI agents with distinct personalities and brain configs
- Commander AI background delegation with auto-task creation
- Agent-to-Agent collaboration via [CONSULT:] tags
- Auto model selection (25 models from 8 providers) with per-agent overrides
- File generation (PDF, DOCX), Image generation (DALL-E 3, GPT Image 1), Video generation (Sora 2)
- Voice mode (OpenAI TTS, 9 voices)
- Brain Editor (personality, tone, expertise, dos/donts, knowledge base, model, temperature, max_tokens)
- Capability gating per agent (toggle image/video/PDF/files)
- Dynamic Stripe subscriptions (Free, Starter, Pro, Business, Custom Build Your Own)
- Commander AI as purchasable add-on ($15/month)
- Credit system with admin-configurable pricing
- Team collaboration (invites, roles, shared chats)
- JWT + Google OAuth authentication
- React + FastAPI + MongoDB, Kubernetes-ready

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP via Admin > Email (SMTP) tab
- [ ] Set custom domain + FRONTEND_URL

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Continue refactoring — extract admin routes to routes/admin.py, services to services/llm.py
- P1: More integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI
- P2: White-label/custom branding options

## Architecture
```
/app/backend/
├── server.py           (main app, routes, services — ~5765 lines, being refactored)
├── models/
│   ├── __init__.py
│   └── schemas.py      (15 Pydantic models extracted)
├── routes/
│   └── __init__.py     (ready for route extraction)
├── services/
│   └── __init__.py     (ready for service extraction)
└── .env

/app/frontend/src/
├── pages/
│   ├── AdminDashboard.jsx  (main admin with tabs)
│   ├── AnalyticsTab.jsx    (extracted analytics + performance)
│   ├── SmtpConfigTab.jsx   (extracted SMTP config)
│   ├── AgentChat.jsx       (chat + feedback buttons)
│   ├── Team.jsx            (team management)
│   ├── PricingPage.jsx     (subscription pricing)
│   └── Settings.jsx        (user settings)
└── components/ui/          (shadcn components)
```

## Database Collections
users, chats, agents, subscriptions, payment_transactions, usage_logs, teams, team_invites, tasks, platform_config, user_sessions
