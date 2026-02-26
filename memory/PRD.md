# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "Martian AI by MAARS Global Corporation". 20+ specialized AI agents with unique robot avatars, powered by 10+ AI models with smart auto-selection. Commander AI bot for task delegation with auto-task creation. Multi-language audio support (Bengali text/audio). Subscription SaaS with Stripe, dynamic pricing, multi-currency (USD/BDT). Custom "Build Your Own" packages. Private admin dashboard with cost reference.

## What's Been Implemented

### Phase 1-6 (Previous Sessions)
- Full-stack React + FastAPI + MongoDB
- JWT + Google OAuth, 20 AI agents with robot avatars
- Chat with 10+ LLMs, Stripe subscriptions, credit system
- Admin dashboard (8 tabs), dynamic pricing, API key management
- White-labeled branding, custom agent creation

### Phase 7 - Commander AI & Audio (Feb 2026)
- Commander Orion: AI Commander with task delegation
- STT via OpenAI Whisper, TTS via ElevenLabs
- ElevenLabs in admin panel

### Phase 8 - Custom Packages & Agent Selection (Feb 2026)
- "Build Your Own" package with agent picker + credit presets
- Agent selection for fixed plans in Settings
- Agent access enforcement in chat
- Admin Custom Packages tab

### Phase 9 - Commander Auto-Tasks & Admin Costs (Feb 2026)
- **Commander auto-creates tasks**: When given a goal, Commander breaks it down, creates task records in DB with priority, assigned agent, and description. Each specialist executes their task and results are saved.
- Tasks page shows "Commander" badge on auto-created tasks with goal reference
- **API key testing fixed**: Uses lightweight model-list validation (no more 429 rate limits)
- **Direct Provider Costs**: Admin panel shows per-model input/output pricing for all providers

## Prioritized Backlog

### P1
- End-to-end subscription/credit lifecycle testing
- Commander AI as paid add-on purchase flow

### P2
- Backend refactoring (split monolithic server.py)
- Custom domain setup UI

### P3
- Chat history search/export, mobile optimization

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/session, /api/auth/me
- Agents: /api/agents, /api/agents/public, /api/agents/{id}
- Chat: /api/chats, /api/chats/{id}/messages
- Tasks: /api/tasks, /api/tasks/{id}/execute
- Audio: /api/audio/speech-to-text, /api/audio/text-to-speech, /api/audio/voices
- Plans: /api/plans
- Custom Package: /api/custom-package/config, /api/custom-package/checkout
- Subscription: /api/subscription, /api/subscription/agents
- Admin: /api/admin/stats, /api/admin/api-keys, /api/admin/pricing, /api/admin/custom-package

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
