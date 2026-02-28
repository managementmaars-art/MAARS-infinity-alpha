# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard. Must include ALL major AI providers. Agents should be autonomous systems that can plan tasks, use tools, make decisions, and complete multi-step work. Platform should match Emergent-level features including all major 3rd party integrations.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars

### Chat UI
- Resizable sidebar (drag to adjust width, 200-600px range)
- Navigation (Dashboard/All Agents/Tasks) at TOP of sidebar
- Sticky message input that stays visible while scrolling
- Model selector with 25+ models across 9 providers
- File attachments, voice input (Whisper STT), TTS playback
- Execution steps display for agent tool usage

### Autonomous Agent Architecture
- **Tool System**: ReAct-pattern execution engine supporting multi-step reasoning
- **Core Tools**: web_search, calculate, create_task, analyze_data
- **Integration Tools**: send_slack, send_email, send_sms, github_action, airtable_action, search_gif, schedule_meeting, google_calendar, send_gmail
- **Dynamic Tool Availability**: Integration tools only available when admin configures API keys

### 3rd Party Service Integrations (Admin Configurable)
- Slack, GitHub, SendGrid, Resend, Twilio, Airtable, Calendly, Giphy, Google Suite
- Each with admin UI config, Test Connection, and auto-detection by agents

### AI Models (25+ models across 9 providers)
- OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs
- API Key testing verified for ALL 9 providers with descriptive error messages

### File Generation
- Documents: PDF, Excel, Word, CSV, TXT
- Images: GPT Image 1, DALL-E 3
- Videos: Sora 2

### Admin Dashboard
- Overview, Users, Agents, Transactions, Pricing Manager, Custom Packages, API Keys & Integrations, Payment Setup

### Subscriptions & Billing (Verified E2E - Feb 28 2026)
- 4 plans (Free/Starter/Pro/Business) + "Build Your Own" + Extra Credit Packs
- Stripe checkout integration working
- Credit deduction on message send verified
- Default free plan with 50 credits for new users

### Commander AI + Group Chat

## Backlog
- P1: Teams & Collaboration (invite members, shared agents, role-based permissions)
- P1: Commander AI as purchasable add-on
- P2: Backend refactoring (break server.py into modules)
- P2: Frontend refactoring (break AdminDashboard.jsx into sub-components)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Architecture
```
/app/
  backend/
    server.py   # Monolithic (4300+ lines) - auth, chat, ReAct engine, billing, admin, tools, integrations
    .env
  frontend/src/
    App.js
    pages/ (AdminDashboard.jsx, AgentChat.jsx, PricingPage.jsx, etc.)
    components/ui/ (Shadcn)
```
