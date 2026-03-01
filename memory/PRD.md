# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features (Latest First)

### Bug Fix: Header Badge Toggles + Improved Error Handling (Mar 1, 2026 - Latest)
- **Root Cause**: IMG/PDF/FILES badges in agent rows were display-only Badge components, not clickable
- **Fix**: Changed to `<button>` elements with `onClick` handlers and `e.stopPropagation()`
- Badges always visible (greyed+strikethrough when disabled, colored when enabled)
- Improved error messages: show HTTP status codes and network error details
- Toast messages now say "Enabled/Disabled {type} generation"
- All 12 tests passed (iteration_35)

### User Agent Customization (Mar 1, 2026)
- Per-user agent overrides for personality, temperature, max_tokens, custom instructions
- "Customize" button in chat header, settings panel with sliders and text areas
- Endpoints: GET/PUT/DELETE `/api/agents/{agent_id}/my-settings`
- All 21 tests passed (iteration_34)

### Custom Domain UI & White-Label Branding (Mar 1, 2026)
- Admin tab: Brand Identity, Logo/Favicon upload, Color pickers, Custom Domain + DNS verification
- BrandingProvider context for dynamic theming
- All 18 tests passed (iteration_33)

### Earlier Features
- Notification Center, User Insights, Onboarding, Analytics, AI Controls, SMTP Config
- Backend Refactoring Phase 1 (models/schemas.py, config.py)
- 21 AI agents, Commander AI, Voice Mode, Stripe Subscriptions, Team Collaboration

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Backend refactoring - extract admin routes from server.py to routes/admin.py
- P1: Third-party integrations (Slack, Calendly, Airtable) backend logic
- P2: AdminDashboard.jsx refactoring
- P2: Complete server.py modularization

## Test Reports (All 100%)
- iteration_35: Header badge toggles bug fix (12/12)
- iteration_34: User agent customization (21/21)
- iteration_33: Branding & custom domain (18/18)
