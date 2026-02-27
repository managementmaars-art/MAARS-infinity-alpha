# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI with auto-task delegation, multi-language audio, file generation (PDF/Excel/Word/CSV/Text/Images/Videos), subscription SaaS with Stripe, custom "Build Your Own" packages, private admin dashboard with cost reference.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with unique sci-fi robot avatars
- Chat with 10+ LLMs (GPT-5.2, Claude, Gemini, etc.)

### Commander AI + Group Chat
- Commander Orion: breaks goals -> sub-tasks -> delegates to specialists
- Auto-creates tasks in DB with priority, assigned agent, results
- Group Chat UI: delegation renders as individual agent chat bubbles

### Audio
- STT via OpenAI Whisper, mic button in chat

### File Generation
- Documents: PDF, Excel, Word, CSV, TXT
- Images: GPT Image 1, DALL-E 3
- Videos: Sora 2

### Subscriptions & Billing
- 4 plans (Free/Starter/Pro/Business) + "Build Your Own"
- Stripe checkout, multi-currency (USD/BDT)

### Admin Dashboard (8 tabs)
- Overview, Users, Agents, Transactions, Pricing Manager, Custom Packages, API Keys, Payment Setup
- **Pricing Manager**: LIVE SYNC calculator with real cost data
- **Pricing Control Center** (Custom Packages tab): Full control over ALL pricing:
  - Agent & Commander per-unit pricing (USD/BDT)
  - Credit Presets for Build Your Own (add/remove/edit with margin badges)
  - Extra Credit Packs for "Need More Credits?" section (add/remove/edit with margin badges)
  - Profit margins auto-calculated from real API cost
  - Single "Save All Pricing" button saves everything
  - `/api/admin/credit-packages` GET/POST for extra credit packs
  - All pricing stored in DB, no hardcoded values

### Brand Footer
- "Martian AI by MAARS Global Corporation © 2026" on ALL pages

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/me
- Chat: /api/chats, /api/chats/{id}/messages
- Tasks: /api/tasks
- Admin: /api/admin/stats, /api/admin/pricing, /api/admin/avg-cost
- Admin Pricing: /api/admin/custom-package, /api/admin/credit-packages

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on for Build Your Own
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
