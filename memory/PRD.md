# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI delegation, file generation, subscriptions, admin dashboard. Must include ALL major AI providers.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars

### AI Models (25+ models across 9 providers)
- **OpenAI**: GPT-5.2, GPT-4o, GPT-4o Mini, O3, O3 Mini, GPT Image 1, DALL-E 3, Sora 2
- **Anthropic**: Claude Sonnet 4.5, Claude Opus 4.5, Claude Haiku 4.5
- **Google**: Gemini 3 Flash, Gemini 3 Pro
- **xAI**: Grok 3, Grok 3 Mini, Grok 2
- **DeepSeek**: DeepSeek Chat, DeepSeek Reasoner
- **Mistral AI**: Mistral Large, Mistral Medium, Mistral Small
- **Perplexity**: Sonar, Sonar Pro
- **Cohere**: Command R+, Command R
- **ElevenLabs**: Multilingual v2 TTS (Bangla, English, etc.)

### Voice & Audio
- STT via OpenAI Whisper (mic button in chat)
- TTS via ElevenLabs Multilingual v2 (Volume2 button on each message)
- Supports 50+ languages including Bangla

### File Generation
- Documents: PDF, Excel, Word, CSV, TXT
- Images: GPT Image 1, DALL-E 3
- Videos: Sora 2

### Admin Dashboard (8 tabs)
- Pricing Manager with LIVE SYNC (real cost data)
- Pricing Control Center with profit margin calculator
- API Keys management for all 9 providers with cost reference
- Live BDT exchange rate from HexaRate API
- Full profit/cost analytics

### Subscriptions & Billing
- 4 plans + "Build Your Own" + Extra Credit Packs
- Stripe checkout, multi-currency (USD/BDT)
- All pricing admin-configurable

### Commander AI + Group Chat
- Delegation renders as individual agent chat bubbles

### Brand Footer
- "Martian AI by MAARS Global Corporation © 2026" on ALL pages

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
