# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard. Must include ALL major AI providers. Agents should be autonomous systems that can plan tasks, use tools, make decisions, and complete multi-step work.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars

### Chat UI
- Resizable sidebar, sticky message input, model selector with 25+ models
- File attachments, voice input (Whisper STT), TTS playback
- Execution steps display for agent tool usage

### LLM Fallback System (Feb 28 2026)
- **Auto-retry**: If selected model fails, automatically tries fallback models
- **Fallback order**: Selected model → GPT-5.2 → GPT-4o → GPT-4o-mini → Gemini 3 Flash
- **No raw errors**: Users never see API error messages, system gracefully falls back
- Applied to both direct message sending and ReAct tool execution loops

### Auto Image Generation (Feb 28 2026)
- Smart detection of image generation requests based on keywords + agent role
- Visual agents (Graphic Designer) auto-trigger image generation
- Uses GPT Image 1 with prompt refinement via GPT-4o-mini
- Generated images render inline in chat with Download PNG links

### Autonomous Agent Architecture
- ReAct-pattern execution engine with tool support
- Core Tools: web_search, calculate, create_task, analyze_data
- Integration Tools: send_slack, send_email, send_sms, github_action, etc.

### 3rd Party Service Integrations (Admin Configurable)
- Slack, GitHub, SendGrid, Resend, Twilio, Airtable, Calendly, Giphy, Google Suite

### AI Models (25+ models across 9 providers)
- OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs
- API Key testing verified for ALL 9 providers

### File Generation
- Documents: PDF, Excel, Word, CSV, TXT
- Images: GPT Image 1, DALL-E 3
- Videos: Sora 2

### Admin Dashboard
- Overview, Users, Agents, Transactions, Pricing, Custom Packages, API Keys & Integrations, Payment Setup

### Subscriptions & Billing (Verified E2E)
- 4 plans + "Build Your Own" + Extra Credit Packs, Stripe checkout
- Credit deduction on message send verified

### Commander AI + Group Chat

## Backlog
- P1: Teams & Collaboration (invite members, shared agents, role-based permissions)
- P1: Commander AI as purchasable add-on
- P2: Backend refactoring (break server.py into modules)
- P2: Frontend refactoring (break AdminDashboard.jsx into sub-components)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
