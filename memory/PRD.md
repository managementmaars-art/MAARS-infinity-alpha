# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "Martian AI by MAARS Global Corporation". 20+ specialized AI agents with unique robot avatars, powered by 10+ AI models with smart auto-selection. Commander AI bot for task delegation. Multi-language audio support (Bengali text/audio). Subscription SaaS with Stripe, dynamic pricing with profit margin calculator, multi-currency (USD/BDT). Private admin dashboard. Support for both Emergent Universal Key and direct provider API keys (OpenAI, Anthropic, Google, ElevenLabs). Custom "Build Your Own" packages where users pick specific agents and credit amounts.

## What's Been Implemented

### Phase 1-6 (Previous Sessions)
- React + FastAPI + MongoDB full-stack
- JWT + Google OAuth authentication
- 20 AI agents with unique sci-fi robot avatars
- Chat with 10+ LLMs (GPT-5.2, Claude, Gemini, etc.)
- Stripe subscription system (Free/Starter/Pro/Business)
- Credit system with usage tracking
- Dynamic pricing with profit margin calculator
- Admin dashboard (7 tabs)
- API key management (Emergent + direct provider keys)
- White-labeled "Martian AI" branding
- Custom agent creation (20 credits)

### Phase 7 - Commander AI & Audio (Feb 2026)
- Commander Orion: AI Commander that delegates goals to specialist agents
- Speech-to-Text via OpenAI Whisper (mic button in chat)
- Text-to-Speech via ElevenLabs (play button on messages)
- ElevenLabs API key in admin panel alongside other providers

### Phase 8 - Custom Packages & Agent Selection (Feb 2026)
- **"Build Your Own" Package**: Users pick specific agents by name + credit preset
- Agent picker grid on Pricing page (20 agents, click to select)
- 5 credit presets (100/500/1000/2000/5000 credits)
- Commander AI as separate paid add-on ($15/mo)
- Real-time price calculator (agents + credits + commander = total)
- Stripe checkout integration for custom packages
- **Agent Selection for Fixed Plans**: Settings page allows users to choose which agents (up to plan limit)
- **Agent Access Enforcement**: Chat blocks access to non-selected agents
- Commander AI restricted to Pro/Business plans only
- **Admin Custom Packages Tab**: Configure per-agent price, commander price, credit presets
- Multi-currency support (USD/BDT) for all custom package pricing

## Prioritized Backlog

### P1
- End-to-end subscription/credit flow testing (full lifecycle)
- Commander AI as purchasable add-on purchase flow finalization

### P2
- Backend refactoring (split monolithic server.py into modular routers)
- Custom domain setup UI

### P3
- Chat history search/export
- Mobile optimization

## Architecture
```
/app/
  backend/
    server.py          # All backend logic
    .env               # MONGO_URL, DB_NAME, EMERGENT_LLM_KEY, JWT_SECRET, STRIPE_API_KEY
  frontend/
    src/
      App.js
      pages/
        AdminDashboard.jsx  # 8-tab admin panel (incl. Custom Packages)
        AgentChat.jsx       # Chat with mic/TTS
        LandingPage.jsx     # Landing with Commander badge
        PricingPage.jsx     # 4 plans + Build Your Own
        Settings.jsx        # Agent selection
        Dashboard.jsx, Agents.jsx, Tasks.jsx
```

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/session, /api/auth/me
- Agents: /api/agents, /api/agents/{id}
- Chat: /api/chats, /api/chats/{id}/messages
- Audio: /api/audio/speech-to-text, /api/audio/text-to-speech, /api/audio/voices
- Plans: /api/plans (returns plans + custom_package config)
- Custom Package: /api/custom-package/config, /api/custom-package/checkout
- Subscription: /api/subscription, /api/subscription/agents (GET/PUT)
- Admin: /api/admin/stats, /api/admin/api-keys, /api/admin/pricing, /api/admin/custom-package

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
- Test: admin@test.com / Admin1234!
