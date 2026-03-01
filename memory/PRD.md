# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (Latest First)

### Bug Fix: CORS credentials causing "Failed to save/update" (Mar 1, 2026 - Latest)
- **Root Cause**: `credentials: "include"` in ALL frontend fetch calls caused CORS errors in the user's browser. When credentials mode is "include", browsers require specific CORS headers that K8s proxy may not provide. Since the app uses JWT tokens in Authorization header (NOT cookies), `credentials: "include"` was unnecessary.
- **Fix**: Removed `credentials: "include"` from ALL 17+ frontend files
- Made header badges (IMG/PDF/FILES) clickable toggles directly
- Improved error messages with HTTP status codes
- All 17 backend tests + all frontend tests passed (iteration_36)

### User Agent Customization (Mar 1, 2026)
- Per-user agent overrides for personality, temperature, max_tokens, custom instructions
- "Customize" button in chat header
- Endpoints: GET/PUT/DELETE `/api/agents/{agent_id}/my-settings`

### Custom Domain UI & White-Label Branding (Mar 1, 2026)
- Admin tab: Brand Identity, Logo/Favicon upload, Color pickers, Custom Domain + DNS verification
- BrandingProvider context for dynamic theming

### Earlier Features
- Notification Center, User Insights, Onboarding, Analytics, AI Controls, SMTP Config
- 21 AI agents, Commander AI, Voice Mode, Stripe Subscriptions, Team Collaboration

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Backend refactoring - extract admin routes from server.py to routes/admin.py
- P1: Third-party integrations (Slack, Calendly, Airtable) backend logic
- P2: AdminDashboard.jsx refactoring
- P2: Complete server.py modularization

## Test Reports (All 100%)
- iteration_36: CORS fix verified, all admin features (17/17 + all frontend)
- iteration_35: Header badge toggles (12/12)
- iteration_34: User agent customization (21/21)
- iteration_33: Branding & custom domain (18/18)
