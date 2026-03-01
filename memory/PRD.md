# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (Latest First)

### P0 Verification Complete (Mar 1, 2026 - Latest)
- **Markdown Rendering:** react-markdown with remark-gfm renders chat messages correctly (headers, lists, bold, code, tables, blockquotes)
- **Nano Banana 2 Image Generation:** Backend uses Gemini gemini-3-pro-image-preview model for image generation. Verified working for graphic designer agent.
- **Admin Controls CORS Fix Verified:** Toggle permissions and brain save working after removing credentials: "include" from all frontend fetch calls
- **Signup flow:** Verified working
- All tests passed (iteration_38: 10/10 backend, 100% frontend)

### Cross-Agent Communication System (Mar 1, 2026)
- **Workspace Context Injection**: build_workspace_context() fetches recent tasks + other agents' latest messages and injects into EVERY agent's system prompt
- **New workspace tools** for ALL 21 agents: query_tasks, update_task, query_agent_history
- Tested: Secretary creates task -> PM reviews it and proposes subtasks (VERIFIED)
- All 14 backend + all frontend tests passed (iteration_37)

### Bug Fix: CORS + credentials causing API failures (Mar 1, 2026)
- Removed credentials: "include" from ALL frontend fetch calls (JWT auth doesn't need cookies)
- Made header badges (IMG/PDF/FILES) clickable toggles
- Fixed IntegrationsTab useEffect dependency (token)
- All 17 backend tests passed (iteration_36)

### User Agent Customization + White-Label Branding (Mar 1, 2026)
- Per-user agent overrides, Customize panel in chat, BrandingProvider context
- All 21 tests passed (iteration_34), 18 tests (iteration_33)

### Earlier Features
- Notification Center, User Insights, Onboarding, Analytics, AI Controls
- SMTP Config, Backend Refactoring Phase 1
- 21 AI agents, Commander AI, Voice Mode, Stripe Subscriptions, Team Collaboration

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Architecture
```
Cross-Agent Communication Flow:
1. User sends message to Agent A
2. build_workspace_context() fetches:
   - Recent tasks (from db.tasks)
   - Latest messages from other agent chats
3. Context injected into system prompt
4. Agent sees shared workspace + can use query_tasks/update_task/query_agent_history tools
5. Agent responds with full awareness of team activity
```

## Backlog (Prioritized)
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — admin UI exists, backend execution logic is MOCKED
- P2: Backend refactoring — extract remaining routes from server.py to modular routers
- P2: AdminDashboard.jsx component extraction (Pricing, Users, Agents tabs)
- P2: Complete server.py modularization

## Test Reports (All 100%)
- iteration_38: Markdown + Nano Banana 2 + Admin controls + Signup (10/10 backend + all frontend)
- iteration_37: Cross-agent communication (14/14 + all frontend)
- iteration_36: CORS fix (17/17)
- iteration_35: Header toggles (12/12)
- iteration_34: User customization (21/21)
- iteration_33: Branding (18/18)
