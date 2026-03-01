# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent-to-agent collaboration, file generation, subscriptions, admin dashboard, team collaboration.

## Implemented Features

### Brain Editor (Added Mar 1, 2026)
- Full agent brain customization UI in Admin > Agents tab
- Editable fields: Name, Role, Description, Personality & Tone, Expertise Areas, Do's, Don'ts, Knowledge Base, Model Provider, Model Name
- Auto-rebuilds system prompt from brain config fields
- PUT /api/admin/agents/{agent_id}/brain endpoint
- Simple enough for non-technical business owner

### Agent-to-Agent Collaboration (Added Mar 1, 2026)
- Agents can consult other specialists mid-conversation
- Uses [CONSULT:agent_id]question[/CONSULT] tag system
- Backend intercepts tags, calls the referenced agent, integrates response
- 10 specialist agents available for cross-consultation

### Commander AI — Background Delegation
- Returns immediately, runs specialists in background (2-3 min)
- Auto-creates tasks, polls for completion every 5 seconds
- Processing spinner UI while specialists work

### Team Collaboration
- Create & manage teams, invite by email, accept/decline invites
- 3 roles: Owner/Admin/Member with different permissions
- Team size per plan: Free:1, Starter:3, Pro:10, Business:unlimited
- Chat sharing toggle, shared chats on Team page

### Smart Agent Behavior
- Clarification questions before deliverables
- Clean conversational writing style
- Conversation history for continuity

### Admin Dashboard
- Live profit calculator
- Agent capability toggles (image/video/pdf/files)
- Brain Editor for each agent
- Stripe payment setup

### Email Notifications (Placeholder)
- Gmail SMTP utility ready, professional HTML template
- Gracefully skips when credentials not set

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Stripe subscriptions, credit system
- Auto image/video/file generation
- /health endpoint for Kubernetes deployment

## Production Launch Checklist
- [ ] Set live Stripe key (STRIPE_API_KEY)
- [ ] Set Gmail SMTP credentials (SMTP_EMAIL, SMTP_PASSWORD)
- [ ] Set custom domain
- [ ] Configure FRONTEND_URL in .env for email links

## Backlog
- P1: Voice mode (ElevenLabs or OpenAI TTS)
- P1: More integrations (Slack, Calendly, Airtable, Google Suite)
- P2: Custom domain UI
- P2: Refactor server.py into modules

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
