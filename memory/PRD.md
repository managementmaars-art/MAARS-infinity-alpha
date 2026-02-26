# MAARS Global Corporation - AI Team Platform PRD

## Original Problem Statement
Build a full-stack AI team platform inspired by Sintra and Emergent, named "MAARS Global Corporation". The platform features a team of 20 specialized AI agents that can use multiple LLM models (GPT-5.2, Claude 4.5, Gemini 3). It is a subscription-based SaaS product with Stripe payments, credit system, and multi-currency support (USD/BDT). The admin (management.maars@marsgc.net) has a private admin section with full platform control.

## User Personas
1. **Platform Admin** - `management.maars@marsgc.net` - Full access, manage users/agents/billing, use AI team without restrictions
2. **Business Subscribers** - Pay for Pro/Business plans to access AI employees for their work
3. **Free Users** - Limited access with 50 credits/month and 1 agent

## Core Requirements
- 20 specialized AI agents (Secretary, Marketing, Sales, Developer, etc.)
- Auto model selection + manual model switching (7 LLMs)
- Subscription tiers: Free, Starter ($29), Pro ($79), Business ($199)
- Credit-based usage system with 200% profit margin
- Stripe payments with USD and BDT currency support
- Private admin dashboard for platform owner
- File uploads up to 50MB
- JWT + Google OAuth authentication

## What's Been Implemented

### Phase 1 - Platform Foundation (Feb 26, 2026)
- Full-stack scaffolding (React + FastAPI + MongoDB)
- MAARS Global Corporation branding with dark theme
- 20 specialized AI agents with unique personalities
- Chat with Auto Model Selection across 7 LLMs
- Manual model switching
- File upload (up to 50MB)
- JWT + Google OAuth authentication
- Landing page, dashboard, agents, chat, tasks, settings pages

### Phase 2 - Monetization (Feb 26, 2026)
- Stripe integration for subscriptions and credit purchases
- 4 subscription tiers (Free/Starter/Pro/Business)
- Credit system with per-message deduction
- Pricing page with USD/BDT currency toggle
- Credit packages for on-demand purchases
- Webhook handling for payment events

### Phase 3 - Admin Section (Feb 26, 2026)
- Private admin dashboard at /admin (separate page with red/orange theme)
- Admin-only access for management.maars@marsgc.net
- Overview tab: Platform-wide stats (users, chats, messages, revenue, credits)
- Users tab: All registered users with subscription info
- Agents tab: Full CRUD for agents (create default agents visible to all)
- Transactions tab: All payment history
- Admin sidebar link visible only to admin users
- Admin bypass for credit limits (unlimited usage)
- Non-admin redirect protection on /admin route
- Backend `require_admin` dependency for API security

## Tech Stack
- **Frontend:** React 19, Tailwind CSS, Shadcn UI
- **Backend:** FastAPI, Pydantic, Motor (async MongoDB)
- **Database:** MongoDB
- **Auth:** JWT + Emergent Google OAuth
- **Payments:** Stripe via emergentintegrations
- **AI:** OpenAI GPT-5.2, Claude Sonnet/Opus 4.5, Gemini 3 Flash/Pro via Emergent LLM Key

## Prioritized Backlog

### P0 - Critical
- None currently

### P1 - High Priority
- Test and fix subscription/credit deduction flow end-to-end
- Implement agent selection mechanism for subscription plans (users choose specific agents)
- Verify 200% profit margin pricing is correct

### P2 - Medium Priority
- Admin usage/cost tracker
- Backend refactoring (split server.py into modular routers)
- Agent collaboration workflows

### P3 - Nice to Have
- Chat history search/filtering
- Export chat history
- Mobile responsive optimization
- Scheduled tasks

## Key Endpoints
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/session`
- Agents: `/api/agents` (GET/POST), `/api/agents/{id}` (GET/DELETE)
- Chat: `/api/chats` (GET/POST), `/api/chats/{id}/messages` (POST)
- Billing: `/api/checkout`, `/api/checkout/status/{id}`, `/api/subscription`, `/api/credits`, `/api/plans`
- Admin: `/api/admin/stats`, `/api/admin/users`, `/api/admin/agents` (GET/POST), `/api/admin/agents/{id}` (DELETE), `/api/admin/transactions`

## Test Credentials
- **Admin:** management.maars@marsgc.net / MaarsAdmin2024! (also has Google OAuth)
- **Test User:** admin@test.com / Admin1234!
