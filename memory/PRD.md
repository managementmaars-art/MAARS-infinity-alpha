# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, file generation, subscriptions, admin dashboard, and team collaboration.

## Implemented Features

### Team Collaboration (Added Feb 28, 2026)
- **Create & manage teams** — Owner creates team, invites members by email
- **Role-based permissions** — Owner (billing + all), Admin (manage agents/members), Member (chat + tasks)
- **Team size limits per plan** — Free: 1, Starter: 3, Pro: 10, Business: unlimited
- **Shared credit pool** — All team members use owner's subscription credits
- **Chat sharing** — Chats private by default, share/unshare via toggle button in chat header
- **Shared chats view** — Team page shows all shared chats with owner info
- **Invite flow** — Send invite by email, invitee sees pending invites, accept/decline
- **Team navigation** — "Team" link added to sidebar on all pages

### Admin Agent Capability Management
- Expandable agent rows with toggle buttons for image/video/pdf/files generation permissions
- Backend PUT /api/admin/agents/{agent_id}/settings endpoint

### Smart Agent Behavior
- Agents ask clarifying questions before generating deliverables
- Clean conversational writing style (minimal markdown)
- Conversation history (last 20 messages) for context continuity

### Bug Fixes (Feb 28, 2026)
- Fixed "currentAgent is not defined" runtime error on file generation buttons
- Fixed "Failed to load data" — resilient API fetching on Dashboard/Tasks
- Fixed scrolling issue in task agent assignment
- Changed "Danger Zone" → "Account" in Settings
- Agent roles visible in task assignment and task cards
- Task status shows "working on it..." for in-progress items

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents with auto image/video/file generation
- Stripe subscriptions, credit system, admin dashboard
- Deployment-ready with /health endpoint for Kubernetes probes

## Backlog
- P1: Commander AI as purchasable add-on for "Build Your Own"
- P2: Refactor server.py / AdminDashboard.jsx into modules
- P2: Custom domain UI
- P2: Admin panel API error details and integration setup guides

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
