# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI with auto-task delegation, multi-language audio, file generation (PDF/Excel/Word/CSV/Text/Images/Videos), subscription SaaS with Stripe, custom "Build Your Own" packages, private admin dashboard with cost reference.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 20 AI agents with unique sci-fi robot avatars
- Chat with 10+ LLMs (GPT-5.2, Claude, Gemini, etc.)
- Smart auto-selection across 7 task types

### Commander AI (Phase 7-9)
- Commander Orion: breaks goals → sub-tasks → delegates to specialists
- Auto-creates tasks in DB with priority, assigned agent, results
- Tasks page shows Commander-created tasks with badge

### Audio (Phase 7)
- STT via OpenAI Whisper, TTS via ElevenLabs
- Mic button in chat, play button on messages
- ElevenLabs API key in admin panel

### File Generation (Phase 10)
- **Documents**: PDF (reportlab), Excel (openpyxl), Word (python-docx), CSV, TXT
- **Images**: GPT Image 1, DALL-E 3 via emergent integrations
- **Videos**: Sora 2 via emergent integrations
- Download/serve via `/api/files/{filename}`
- FileGenButtons on every assistant message (6 types)
- Inline preview for images, video player for videos
- Direct API key support for all generation

### Subscriptions & Billing
- 4 plans (Free/Starter/Pro/Business) + "Build Your Own" custom packages
- Agent picker: users select specific agents by name
- Credit presets, Commander as paid add-on
- Agent access enforcement in chat
- Stripe checkout, multi-currency (USD/BDT)
- Admin: dynamic pricing, profit margins, custom package config

### Admin Dashboard (8 tabs)
- Overview, Users, Agents, Transactions, Pricing Manager
- Custom Packages, API Keys (with cost reference), Payment Setup
- Direct provider costs for all 13+ models including generation

### Landing Page
- Shows all 21 agents with Commander badge
- 4 AI model sections: OpenAI, Anthropic, Google, AI Generation

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/me
- Agents: /api/agents, /api/agents/public
- Chat: /api/chats, /api/chats/{id}/messages
- Tasks: /api/tasks, /api/tasks/{id}/execute
- Audio: /api/audio/speech-to-text, /api/audio/text-to-speech
- Generate: /api/generate/document, /api/generate/image, /api/generate/video
- Files: /api/files/{filename}
- Plans: /api/plans, /api/custom-package/config, /api/custom-package/checkout
- Subscription: /api/subscription, /api/subscription/agents
- Admin: /api/admin/stats, /api/admin/api-keys, /api/admin/pricing, /api/admin/custom-package

## Backlog
- P1: E2E subscription/credit testing, Commander paid add-on flow
- P2: Backend refactoring, custom domain UI
- P3: Chat export, mobile optimization

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
