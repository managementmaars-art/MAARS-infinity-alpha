# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Customer Analytics Dashboard (Added Mar 1, 2026)
- Comprehensive admin analytics tab with KPI cards (Total Users, Active 7d/30d, Total Chats, Revenue, MRR)
- Daily Signups, Messages, Revenue, API Cost charts (30-day time series with recharts)
- Agent Usage horizontal bar chart (messages per agent)
- Subscription Distribution donut chart
- Top Users by Messages ranked list
- Cost by AI Model breakdown with progress bars
- Token Usage Breakdown stacked bar chart (Input/Output tokens)
- Endpoint: GET /api/admin/analytics

### Gmail SMTP Configuration UI (Added Mar 1, 2026)
- Admin panel tab for securely entering Gmail SMTP email and App Password
- Credentials saved to .env and loaded in memory
- Test email functionality to verify SMTP setup
- Step-by-step setup guide for Gmail App Passwords
- Endpoints: GET/POST /api/admin/smtp-config, POST /api/admin/smtp-test

### Dynamic Pricing (Fixed Mar 1, 2026)
- Admin-set prices persist across server restarts (loaded from DB on startup)
- /api/plans returns admin-configured prices (not hardcoded defaults)
- Team size limits included in plans (Free:1, Starter:3, Pro:10, Business:unlimited)

### Voice Mode / TTS (Added Mar 1, 2026)
- OpenAI TTS via Emergent key (no extra API key needed)
- 9 voices: Alloy, Nova, Shimmer, Echo, Onyx, Fable, Coral, Sage, Ash
- Speaker button on every assistant message in chat
- POST /api/tts/generate endpoint

### Brain Editor (Added Mar 1, 2026)
- Full agent customization in Admin > Agents > Edit Brain
- Fields: Personality/Tone, Expertise, Do's/Don'ts, Knowledge Base, Model
- Auto-rebuilds system prompt from brain config

### Agent Collaboration
- Agents consult other specialists mid-conversation via [CONSULT:] tags
- 10 specialist agents available for cross-consultation

### Commander AI — Background Delegation
- Instant response, background specialist coordination (2-3 min)
- Auto-creates tasks, polls for completion

### Team Collaboration
- Create teams, invite by email, accept/decline
- Owner/Admin/Member roles, shared credit pool
- Chat sharing toggle, shared chats view

### Smart Agent Behavior
- Clarification questions, clean writing style
- Conversation history, capability enforcement

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Stripe subscriptions, credit system
- Auto image/video/file generation, admin dashboard
- /health for Kubernetes deployment

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP (SMTP_EMAIL, SMTP_PASSWORD) via Admin > Email (SMTP) tab
- [ ] Set custom domain + FRONTEND_URL

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Commander AI as purchasable add-on for Build Your Own package
- P1: More integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI
- P2: Refactor server.py (5500+ lines) and AdminDashboard.jsx (2400+ lines) into modular structure

## Architecture
- Backend: /app/backend/server.py (monolithic - needs refactoring)
- Frontend: /app/frontend/src/pages/ (AdminDashboard.jsx + AnalyticsTab.jsx + SmtpConfigTab.jsx + AgentChat.jsx + Team.jsx)
- Database: MongoDB with collections: users, chats, agents, subscriptions, payment_transactions, usage_logs, teams, team_invites, tasks, platform_config, user_sessions
