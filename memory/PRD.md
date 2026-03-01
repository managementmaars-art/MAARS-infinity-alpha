# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard, team collaboration, and email notifications — ready for production launch.

## Implemented Features

### Team Collaboration (Feb 28, 2026)
- Create & manage teams, invite by email, accept/decline invites
- 3 roles: Owner (billing+all), Admin (manage agents/members), Member (chat+tasks)
- Team size per plan: Free:1, Starter:3, Pro:10, Business:unlimited
- Shared credit pool from owner's subscription
- Chat sharing toggle in chat header, shared chats on Team page
- Team nav link on all pages

### Commander AI — Background Delegation (Fixed Feb 28, 2026)
- Returns immediately with "processing" status (no more timeouts)
- Background task coordinates 3-5 specialist agents
- Auto-polls for completion (every 5 seconds)
- Processing spinner UI while specialists work
- Auto-creates tasks with results on Tasks page
- Clean output format (minimal markdown)

### Smart Agent Behavior
- All 21 agents ask clarifying questions before deliverables
- Clean conversational writing style (minimal ##, ** usage)
- Conversation history (20 msgs) for continuity
- Specialists skip questions during Commander delegation

### Agent Capabilities (Seeded Defaults)
- Graphics/Social Media/Content Writer/Web Designer: can_generate_image=true
- Video Specialist: can_generate_video=true
- All agents: can_generate_pdf=true, can_generate_files=true
- Admin can toggle all capabilities from Admin > Agents tab

### Email Notifications (Placeholder)
- Gmail SMTP utility ready (send_email_notification)
- Gracefully skips when SMTP_EMAIL/SMTP_PASSWORD not set in .env
- Professional HTML invite email template built
- User to provide Gmail App Password when ready

### Bug Fixes
- Fixed "currentAgent is not defined" runtime error
- Fixed "Failed to load data" resilience
- Fixed scrolling in task agent assignment
- "Danger Zone" → "Account" in Settings
- Agent roles visible in task cards
- Fixed asyncio import (Commander background tasks)
- Removed duplicate /admin/agents endpoint

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Stripe subscriptions, credit system
- Admin dashboard with profit calculator, agent management
- /health endpoint for Kubernetes deployment

## Production Launch Checklist
- [ ] Set live Stripe key in backend .env (STRIPE_API_KEY)
- [ ] Set Gmail SMTP credentials (SMTP_EMAIL, SMTP_PASSWORD)
- [ ] Set custom domain
- [ ] Configure FRONTEND_URL in .env for email links

## Cost Structure
- Your AI cost per user: ~$3.50/month
- Starter: $29/mo → $25.50 profit/user
- Pro: $79/mo → $75.50 profit/user
- Business: $199/mo → $195.50 profit/user

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Commander AI as purchasable add-on for "Build Your Own"
- P2: Refactor server.py into modules
- P2: Custom domain UI
- P2: Admin panel API error details
