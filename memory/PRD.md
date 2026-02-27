# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI with auto-task delegation, multi-language audio, file generation (PDF/Excel/Word/CSV/Text/Images/Videos), subscription SaaS with Stripe, custom "Build Your Own" packages, private admin dashboard with cost reference.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars
- Chat with 10+ LLMs (GPT-5.2, Claude, Gemini, etc.)
- Smart auto-selection across 7 task types

### Commander AI (Phase 7-9 + Group Chat)
- Commander Orion: breaks goals -> sub-tasks -> delegates to specialists
- Auto-creates tasks in DB with priority, assigned agent, results
- Tasks page shows Commander-created tasks with badge
- Group Chat UI: Commander delegation renders as individual agent chat bubbles with avatars, roles, priority badges
- Backend returns structured `delegation_data` for rich rendering

### Audio (Phase 7)
- STT via OpenAI Whisper
- Mic button in chat
- ElevenLabs removed per user request

### File Generation (Phase 10)
- Documents: PDF (fpdf), Excel (openpyxl), Word (python-docx), CSV, TXT
- Images: GPT Image 1, DALL-E 3 via emergent integrations
- Videos: Sora 2 via emergent integrations
- Download/serve via `/api/files/{filename}`

### Subscriptions & Billing
- 4 plans (Free/Starter/Pro/Business) + "Build Your Own" custom packages
- Agent picker, credit presets, Commander as paid add-on
- Stripe checkout, multi-currency (USD/BDT)
- Admin: dynamic pricing with REAL cost data, profit margins

### Admin Dashboard (8 tabs)
- Overview, Users, Agents, Transactions, Pricing Manager
- Custom Packages, API Keys (with cost reference), Payment Setup
- Pricing Manager uses REAL cost data from usage_logs (`/api/admin/avg-cost`)

### Brand Footer
- "Martian AI by MAARS Global Corporation © 2026" footer visible on ALL pages
- Shared `BrandFooter` component used across Landing, Login, Register, Pricing, Dashboard, Chat, Agents, Tasks, Settings, Admin, PaymentSuccess

### Landing Page
- Shows all 21 agents with Commander badge
- 4 AI model sections: OpenAI, Anthropic, Google, AI Generation

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/me
- Agents: /api/agents, /api/agents/public
- Chat: /api/chats, /api/chats/{id}/messages
- Tasks: /api/tasks, /api/tasks/{id}/execute
- Audio: /api/audio/speech-to-text
- Generate: /api/generate/document, /api/generate/image, /api/generate/video
- Plans: /api/plans, /api/custom-package/config, /api/custom-package/checkout
- Subscription: /api/subscription, /api/subscription/agents
- Admin: /api/admin/stats, /api/admin/api-keys, /api/admin/pricing, /api/admin/avg-cost

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on for Build Your Own
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI
- P3: Chat export, mobile optimization

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
