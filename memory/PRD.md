# AI Legends by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "AI Legends by MAARS Global Corporation". The platform features 20 specialized AI agents with unique futuristic robot avatars. It is a subscription-based SaaS product with Stripe payments, credit system, and multi-currency support (USD/BDT). The admin (management.maars@marsgc.net) has a private admin section with full platform control including payment setup guide.

## User Personas
1. **Platform Admin** - `management.maars@marsgc.net` - Full access, manage users/agents/billing, payment configuration
2. **Business Subscribers** - Pay for Pro/Business plans to access AI employees
3. **Free Users** - Limited access with 50 credits/month and 1 agent

## What's Been Implemented

### Phase 1 - Platform Foundation (Feb 26, 2026)
- Full-stack scaffolding (React + FastAPI + MongoDB)
- 20 specialized AI agents with unique futuristic robot avatars
- Chat with Auto Model Selection across 7 LLMs
- Manual model switching, file upload (up to 50MB)
- JWT + Google OAuth authentication

### Phase 2 - Monetization (Feb 26, 2026)
- Stripe integration, 4 subscription tiers (Free/Starter/Pro/Business)
- Credit system, pricing page with USD/BDT toggle
- Custom agent creation: 20 credits + plan-based limits

### Phase 3 - Admin Section (Feb 26, 2026)
- Private admin dashboard at /admin with 5 tabs (Overview, Users, Agents, Transactions, Payment Setup)
- Admin-only access, unlimited credits
- Agent CRUD, user management, platform stats

### Phase 4 - Rebranding (Feb 26, 2026)
- Rebranded from "MAARS Global Corporation" to "AI Legends by MAARS Global Corporation"
- Updated all sidebars, headers, footers, login/register pages, admin panel
- Browser tab title: "AI Legends | MAARS Global Corporation"
- Payment Setup tab with Stripe guide, Bangladesh payment options (SSLCommerz, Stripe multi-currency, Paddle), env variable reference, pricing table

## Subscription Plans (200% Profit Margin)
| Plan | USD | BDT | Credits | Agents | Custom Agents |
|------|-----|-----|---------|--------|---------------|
| Free | $0 | ₹0 | 50 | 1 | 0 |
| Starter | $29 | ₹3,100 | 500 | 5 | 2 |
| Pro | $79 | ₹8,400 | 2,000 | 10 | 5 |
| Business | $199 | ₹21,100 | 6,000 | 20 | Unlimited |

## Tech Stack
- Frontend: React 19, Tailwind CSS, Shadcn UI
- Backend: FastAPI, Pydantic, Motor (async MongoDB)
- Database: MongoDB
- Auth: JWT + Emergent Google OAuth
- Payments: Stripe via emergentintegrations
- AI: OpenAI GPT-5.2, Claude 4.5, Gemini 3 via Emergent LLM Key

## Prioritized Backlog

### P1 - High Priority
- Test and fix subscription/credit deduction flow end-to-end
- Implement agent selection mechanism for subscription plans
- Verify 200% profit margin pricing

### P2 - Medium Priority
- Admin usage/cost tracker
- Backend refactoring (split server.py)

### P3 - Nice to Have
- Chat history search/export
- Mobile responsive optimization

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
- Test User: admin@test.com / Admin1234!
