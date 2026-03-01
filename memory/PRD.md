# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### AI Controllability & Flexibility (Added Mar 1, 2026)
- **Agent Enable/Disable Toggle:** Admin can activate/deactivate any agent. Disabled agents are hidden from users but visible to admin.
- **Temperature Control:** Per-agent temperature slider (0.0 Precise → 2.0 Creative) in Brain Editor
- **Max Tokens Control:** Per-agent max response length slider (256 → 16384) in Brain Editor
- **Analytics Export:** Download full analytics as CSV (Users, Agent Usage, Payments, Summary)
- Temperature and max_tokens are passed through to LLM calls via `with_params()`

### Real-time Activity Feed (Added Mar 1, 2026)
- Live feed on Analytics dashboard showing recent signups, payments, chats, team creations
- Auto-refreshes every 15 seconds with manual refresh button
- Events sorted by timestamp (newest first), relative timestamps

### Customer Analytics Dashboard (Added Mar 1, 2026)
- KPI cards (Total Users, Active 7d/30d, Total Chats, Revenue, MRR)
- 7 recharts charts: daily signups, messages, revenue, API cost, agent usage, subscription distribution, token usage
- Top Users by Messages, Cost by AI Model breakdown

### Gmail SMTP Configuration UI (Added Mar 1, 2026)
- Admin tab for securely entering Gmail SMTP email and App Password
- Test email functionality, step-by-step setup guide

### Commander AI Add-on (Complete)
- Purchasable add-on in "Build Your Own" package ($15/month)
- Included by default in Pro and Business plans

### Brain Editor (Complete)
- Full agent customization: Personality, Expertise, Do's/Don'ts, Knowledge Base, Model, Temperature, Max Tokens

### Core AI Functionality (Complete)
- 21 specialized AI agents with distinct personalities
- Auto model selection (25 models from 8 providers)
- Agent-to-Agent collaboration via [CONSULT:] tags
- Commander AI background delegation
- Clarification questions, conversation history
- Tool execution (web search, calculate, tasks, email, Slack, GitHub, etc.)
- File generation (PDF, DOCX), Image generation (DALL-E 3, GPT Image 1), Video generation (Sora 2)
- Voice mode (OpenAI TTS, 9 voices)
- Capability gating per agent (toggle image/video/PDF/files)

### Monetization (Complete)
- Dynamic Stripe subscriptions (Free, Starter, Pro, Business, Custom)
- Credit system, admin-configurable pricing
- Build Your Own package with per-agent selection

### Team Collaboration (Complete)
- Team creation, email invites, role management (Owner/Admin/Member)
- Shared credit pool, chat sharing

### Platform (Complete)
- JWT + Google OAuth authentication
- React + FastAPI + MongoDB
- Kubernetes-ready with /health endpoint

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP via Admin > Email (SMTP) tab
- [ ] Set custom domain + FRONTEND_URL

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: More integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI
- P2: Refactor server.py (5800+ lines) and AdminDashboard.jsx into modular structure

## Architecture
- Backend: /app/backend/server.py (monolithic)
- Frontend: /app/frontend/src/pages/ (AdminDashboard.jsx, AnalyticsTab.jsx, SmtpConfigTab.jsx, AgentChat.jsx, Team.jsx, PricingPage.jsx, Settings.jsx)
- Database: MongoDB (users, chats, agents, subscriptions, payment_transactions, usage_logs, teams, team_invites, tasks, platform_config, user_sessions)
