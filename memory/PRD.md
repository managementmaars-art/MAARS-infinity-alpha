# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Dynamic Pricing (Fixed Mar 1, 2026)
- Admin-set prices persist across server restarts (loaded from DB on startup)
- /api/plans returns admin-configured prices (not hardcoded defaults)
- Team size limits included in plans (Free:1, Starter:3, Pro:10, Business:unlimited)

### Voice Mode / TTS (Added Mar 1, 2026)
- OpenAI TTS via Emergent key (no extra API key needed)
- 9 voices: Alloy, Nova, Shimmer, Echo, Onyx, Fable, Coral, Sage, Ash
- Speaker button on every assistant message in chat
- POST /api/tts/generate endpoint

### Brain Editor (Added Mar 1, 2026)
- Full agent customization in Admin > Agents > Edit Brain
- Fields: Personality/Tone, Expertise, Do's/Don'ts, Knowledge Base, Model
- Auto-rebuilds system prompt from brain config

### Agent Collaboration
- Agents consult other specialists mid-conversation via [CONSULT:] tags
- 10 specialist agents available for cross-consultation

### Commander AI — Background Delegation
- Instant response, background specialist coordination (2-3 min)
- Auto-creates tasks, polls for completion

### Team Collaboration
- Create teams, invite by email, accept/decline
- Owner/Admin/Member roles, shared credit pool
- Chat sharing toggle, shared chats view

### Smart Agent Behavior
- Clarification questions, clean writing style
- Conversation history, capability enforcement

### Email Notifications (Placeholder)
- Gmail SMTP utility ready, professional HTML template
- Gracefully skips when credentials not set

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Stripe subscriptions, credit system
- Auto image/video/file generation, admin dashboard
- /health for Kubernetes deployment

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP (SMTP_EMAIL, SMTP_PASSWORD)
- [ ] Set custom domain + FRONTEND_URL

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: More integrations (Slack, Calendly, Airtable)
- P2: Custom domain UI, Refactor server.py
