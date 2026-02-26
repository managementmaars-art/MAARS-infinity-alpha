# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "Martian AI by MAARS Global Corporation". 20 specialized AI agents with unique robot avatars, powered by 10+ AI models with smart auto-selection. Subscription-based SaaS with Stripe, dynamic pricing with profit margin calculator, multi-currency (USD/BDT). Private admin dashboard with full platform control.

## What's Been Implemented

### Phase 1 - Foundation (Feb 26, 2026)
- Full-stack (React + FastAPI + MongoDB), 20 AI agents, chat with 7 LLMs
- Auto model selection, file uploads (50MB), JWT + Google OAuth

### Phase 2 - Monetization (Feb 26, 2026)
- Stripe subscriptions (Free/Starter/Pro/Business), credit system
- Pricing page with USD/BDT toggle, credit packages

### Phase 3 - Admin Section (Feb 26, 2026)
- Private admin dashboard at /admin (6 tabs: Overview, Users, Agents, Transactions, Pricing Manager, Payment Setup)
- Admin-only access, unlimited credits, agent CRUD

### Phase 4 - Robot Avatars & Custom Agent Charging (Feb 26, 2026)
- 20 unique futuristic/sci-fi robot avatars, custom agent creation (20 credits + plan limits)

### Phase 5 - Rebrand & Dynamic Pricing & Models (Feb 26, 2026)
- Rebranded to "Martian AI by MAARS Global Corporation"
- Removed all "Emergent" visible branding (badge, meta description)
- Dynamic Pricing Manager: profit margin calculator (auto + manual), edit all plan prices, publish changes live
- Expanded to 10 AI models: GPT-5.2, GPT-4o, GPT-4o Mini, O3, O3 Mini, Claude Sonnet 4.5, Claude Opus 4.5, Claude Haiku 4.5, Gemini 3 Flash, Gemini 3 Pro
- Smarter auto-selection across 7 task types (coding, reasoning, creative, quick, long_form, data, legal)
- Payment Setup guide (Stripe, SSLCommerz, Paddle for Bangladesh)

## Prioritized Backlog
### P1 - High
- Test subscription/credit flow end-to-end
- Implement agent selection for plans (users choose specific agents)
### P2 - Medium
- Backend refactoring (split server.py)
### P3 - Nice to Have
- Chat history search/export, mobile optimization

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
- Test: admin@test.com / Admin1234!
