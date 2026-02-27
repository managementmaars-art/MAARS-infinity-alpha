# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI delegation, file generation, subscriptions, admin dashboard. Must include ALL major AI providers. Agents should be autonomous systems that can plan tasks, use tools, make decisions, and complete multi-step work.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars

### Autonomous Agent Architecture (NEW)
- **Tool System**: ReAct-pattern execution engine supporting multi-step reasoning
- **Available Tools**: web_search (DuckDuckGo), calculate (safe math eval), create_task (task management), analyze_data (data analysis)
- **Agent-Tool Mapping**: Each agent has specific tools based on their role (e.g., finance agent has calculate + analyze_data + web_search)
- **Execution Steps**: Frontend displays reasoning steps (thinking, tool calls, tool results) in collapsible UI
- **Feedback Loop**: Agents review tool results and incorporate them into final responses
- **Self-correction**: Multi-iteration loop (up to 4 iterations) for complex tool chains

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
- API Keys management for all 9 providers with cost reference (FIXED - now shows all 9)
- API Usage tracking for all 9 providers (FIXED - backend now checks all 9)
- Live BDT exchange rate from HexaRate API
- Full profit/cost analytics
- Create Agent form supports all 8 LLM providers

### Subscriptions & Billing
- 4 plans + "Build Your Own" + Extra Credit Packs
- Stripe checkout, multi-currency (USD/BDT)
- All pricing admin-configurable

### Commander AI + Group Chat
- Delegation renders as individual agent chat bubbles

### Brand Footer
- "Martian AI by MAARS Global Corporation (c) 2026" on ALL pages

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
