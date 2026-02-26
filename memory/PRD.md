# MAARS Global Corporation - AI Team Platform PRD

## Original Problem Statement
Build a full-stack AI team platform inspired by Sintra and Emergent, named "MAARS Global Corporation". The platform features a team of 20 specialized AI agents that can use multiple LLM models (GPT-5.2, Claude 4.5, Gemini 3). It is a subscription-based SaaS product with Stripe payments, credit system, and multi-currency support (USD/BDT). The admin (management.maars@marsgc.net) has a private admin section with full platform control.

## User Personas
1. **Platform Admin** - `management.maars@marsgc.net` - Full access, manage users/agents/billing, use AI team without restrictions
2. **Business Subscribers** - Pay for Pro/Business plans to access AI employees for their work
3. **Free Users** - Limited access with 50 credits/month and 1 agent

## Core Requirements
- 20 specialized AI agents with unique futuristic robot avatars
- Auto model selection + manual model switching (7 LLMs)
- Subscription tiers: Free, Starter ($29), Pro ($79), Business ($199)
- Credit-based usage system with 200% profit margin
- Custom agent creation costs 20 credits + plan-based limits
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
- Pricing page with USD/BDT currency toggle (prices now match backend)
- Credit packages for on-demand purchases
- Webhook handling for payment events

### Phase 3 - Admin Section (Feb 26, 2026)
- Private admin dashboard at /admin (separate page with red/orange theme)
- Admin-only access for management.maars@marsgc.net
- Overview tab: Platform-wide stats (users, chats, messages, revenue, credits)
- Users tab: All registered users with subscription info
- Agents tab: Full CRUD for agents (create default agents visible to all)
- Transactions tab: All payment history
- Admin bypass for credit limits (unlimited usage)

### Phase 4 - Robot Avatars & Custom Agent Charging (Feb 26, 2026)
- Generated 20 unique futuristic/sci-fi robot avatars using AI image generation
- Each agent has a distinct robot design matching their role/personality
- Custom agent creation now costs 20 credits
- Plan-based limits: Free=0, Starter=2, Pro=5, Business=unlimited
- Admin bypasses all creation limits
- Create Agent page shows cost info card (credits, slots, plan)
- Blocked users see upgrade prompts with disabled form
- Pricing page updated to match backend prices and show custom agent features

## Subscription Plans (200% Profit Margin)
| Plan | USD | BDT | Credits | Agents | Custom Agents |
|------|-----|-----|---------|--------|---------------|
| Free | $0 | ৳0 | 50 | 1 | 0 |
| Starter | $29 | ৳3,100 | 500 | 5 | 2 |
| Pro | $79 | ৳8,400 | 2,000 | 10 | 5 |
| Business | $199 | ৳21,100 | 6,000 | 20 | Unlimited |

## Tech Stack
- **Frontend:** React 19, Tailwind CSS, Shadcn UI
- **Backend:** FastAPI, Pydantic, Motor (async MongoDB)
- **Database:** MongoDB
- **Auth:** JWT + Emergent Google OAuth
- **Payments:** Stripe via emergentintegrations
- **AI:** OpenAI GPT-5.2, Claude Sonnet/Opus 4.5, Gemini 3 Flash/Pro via Emergent LLM Key

## Prioritized Backlog

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
- Agents: `/api/agents` (GET/POST), `/api/agents/{id}` (GET/DELETE), `/api/agents/create/info` (GET)
- Chat: `/api/chats` (GET/POST), `/api/chats/{id}/messages` (POST)
- Billing: `/api/checkout`, `/api/checkout/status/{id}`, `/api/subscription`, `/api/credits`, `/api/plans`
- Admin: `/api/admin/stats`, `/api/admin/users`, `/api/admin/agents` (GET/POST/DELETE), `/api/admin/transactions`

## Test Credentials
- **Admin:** management.maars@marsgc.net / MaarsAdmin2024! (also has Google OAuth)
- **Test User:** admin@test.com / Admin1234!
