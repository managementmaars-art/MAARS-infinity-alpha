# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform named "Martian AI by MAARS Global Corporation". 20+ specialized AI agents with unique robot avatars, powered by 10+ AI models with smart auto-selection. Commander AI bot for task delegation. Multi-language audio support (Bengali text/audio). Subscription SaaS with Stripe, dynamic pricing with profit margin calculator, multi-currency (USD/BDT). Private admin dashboard. Support for both Emergent Universal Key and direct provider API keys (OpenAI, Anthropic, Google, ElevenLabs).

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

### Phase 6 - Direct API Keys Support
- Admin can choose between Emergent Universal Key or Direct Provider Keys
- Per-provider key management (OpenAI, Anthropic, Google) with test functionality
- Fallback system: direct keys -> Emergent key

### Phase 7 - Commander AI & Audio Support (Feb 2026)
- **Commander Orion**: New AI Commander agent that breaks down goals, delegates to 20 specialist agents, and compiles comprehensive results
- Commander appears first in all agent lists with special golden badge on landing page
- **Speech-to-Text (STT)**: Voice input via OpenAI Whisper (uses Emergent Universal Key)
- **Text-to-Speech (TTS)**: Audio playback via ElevenLabs (requires admin-configured API key)
- **ElevenLabs in Admin Panel**: Added alongside OpenAI/Anthropic/Google in API Keys tab with test functionality
- Microphone button in chat input for voice recording
- Listen/play button on all assistant messages

## Prioritized Backlog

### P1
- Test subscription/credit flow end-to-end
- Implement agent selection for plans (users choose which agents)
- Commander AI as a paid add-on (purchase flow)

### P2
- Backend refactoring (split server.py into modular routers)
- Custom domain setup UI

### P3
- Chat history search/export
- Mobile optimization

## Test Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
- Test: admin@test.com / Admin1234!

## Architecture
```
/app/
  backend/
    server.py          # Monolithic backend (auth, chat, billing, admin, agents, audio)
    .env               # MONGO_URL, DB_NAME, EMERGENT_LLM_KEY, JWT_SECRET, STRIPE_API_KEY
  frontend/
    src/
      App.js           # Router, auth context
      pages/
        AdminDashboard.jsx  # 7-tab admin panel
        AgentChat.jsx       # Chat with mic/TTS buttons
        LandingPage.jsx     # Landing with Commander badge
        Dashboard.jsx
        Agents.jsx
        Settings.jsx
        PricingPage.jsx
        ...
```

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/session, /api/auth/me
- Agents: /api/agents, /api/agents/{id}
- Chat: /api/chats, /api/chats/{id}/messages
- Audio: /api/audio/speech-to-text, /api/audio/text-to-speech, /api/audio/voices
- Admin: /api/admin/stats, /api/admin/api-keys, /api/admin/pricing
- Billing: /api/plans, /api/checkout, /api/subscription, /api/credits
