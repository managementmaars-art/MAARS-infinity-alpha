# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard. Must include ALL major AI providers. Agents should be autonomous systems that can plan tasks, use tools, make decisions, and complete multi-step work. Platform should match Emergent-level features including all major 3rd party integrations.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars

### Autonomous Agent Architecture
- **Tool System**: ReAct-pattern execution engine supporting multi-step reasoning
- **Core Tools**: web_search (DuckDuckGo), calculate (safe math eval), create_task (task management), analyze_data (data analysis)
- **Integration Tools**: send_slack, send_email, send_sms, github_action, airtable_action, search_gif, schedule_meeting, google_calendar, send_gmail
- **Agent-Tool Mapping**: Each agent has specific tools based on their role
- **Execution Steps**: Frontend displays reasoning steps (thinking, tool calls, tool results) in collapsible UI
- **Feedback Loop**: Agents review tool results and incorporate them into final responses
- **Dynamic Tool Availability**: Integration tools only available when admin configures API keys

### 3rd Party Service Integrations (Admin Configurable)
- **Slack** - Bot Token, send messages to channels
- **GitHub** - Personal Access Token, create issues/PRs, read repos
- **SendGrid** - API Key, transactional/marketing emails
- **Resend** - API Key, modern email sending
- **Twilio** - Account SID + Auth Token + Phone, SMS/voice
- **Airtable** - API Key, read/write bases and records
- **Calendly** - API Key, schedule meetings
- **Giphy** - API Key, GIF search
- **Google Suite** - Service Account JSON, Gmail/Calendar/Drive
- Each integration has: admin UI config, Test Connection, auto-detected by agents

### AI Models (25+ models across 9 providers)
- OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs
- Universal Key + Direct API key support

### Voice & Audio
- STT via OpenAI Whisper, TTS via ElevenLabs Multilingual v2

### File Generation
- Documents: PDF, Excel, Word, CSV, TXT
- Images: GPT Image 1, DALL-E 3
- Videos: Sora 2

### Admin Dashboard (9 tabs)
- Overview, Users, Agents, Transactions, Pricing Manager, Custom Packages, API Keys, **Integrations** (NEW), Payment Setup
- All 9 AI providers shown in API Keys tab
- All 9 integration services configurable in Integrations tab with Test Connection

### Subscriptions & Billing
- 4 plans + "Build Your Own" + Extra Credit Packs
- Stripe checkout, multi-currency (USD/BDT)

### Commander AI + Group Chat
- Task delegation with group chat bubbles

## Backlog
- P1: Teams & Collaboration (invite members, shared agents, role-based permissions)
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
