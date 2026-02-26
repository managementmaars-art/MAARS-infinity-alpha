# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "Martian AI by MAARS Global Corporation". 20 specialized AI agents with unique robot avatars, powered by 10 AI models with smart auto-selection. Subscription SaaS with Stripe, dynamic pricing with profit margin calculator, multi-currency (USD/BDT). Private admin dashboard. Support for both Emergent Universal Key and direct provider API keys.

## What's Been Implemented

### Phase 1 - Foundation
- React + FastAPI + MongoDB, 20 AI agents, chat with LLMs, JWT + Google OAuth

### Phase 2 - Monetization
- Stripe subscriptions, credit system, pricing page (USD/BDT), custom agent charging

### Phase 3 - Admin Section
- Private admin dashboard (7 tabs: Overview, Users, Agents, Transactions, Pricing Manager, API Keys, Payment Setup)

### Phase 4 - Robot Avatars & Custom Agents
- 20 unique sci-fi robot avatars, custom agent creation (20 credits + plan limits)

### Phase 5 - Rebrand & Dynamic Pricing & Models
- "Martian AI by MAARS Global Corporation" branding, removed Emergent badge
- Dynamic Pricing Manager with profit margin calculator (auto + manual)
- 10 AI models: GPT-5.2, GPT-4o, GPT-4o Mini, O3, O3 Mini, Claude Sonnet/Opus/Haiku 4.5, Gemini 3 Flash/Pro
- Smarter auto-selection across 7 task types
- Cost price + profit margin always visible in admin pricing editor

### Phase 6 - Direct API Keys Support
- Admin can choose between Emergent Universal Key or Direct Provider Keys
- Per-provider key management (OpenAI, Anthropic, Google) with test functionality
- Fallback system: direct keys → Emergent key
- Keys masked in UI, stored securely in DB

## Prioritized Backlog
### P1
- Test subscription/credit flow end-to-end
- Implement agent selection for plans
### P2
- Backend refactoring (split server.py)
### P3
- Chat history search/export, mobile optimization

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
- Test: admin@test.com / Admin1234!
