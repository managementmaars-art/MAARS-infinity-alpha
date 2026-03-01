# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### User Agent Customization (Mar 1, 2026 - Latest)
- **Per-user agent overrides**: Users can customize agent behavior for their own sessions only (not global)
- "Customize" button in chat header next to agent name opens settings panel
- Fields: Personality Adjustment, Custom Instructions, Temperature (0-2 slider), Max Tokens (256-16384 slider)
- Settings persist per user+agent pair in `user_agent_overrides` collection
- Reset to defaults button clears overrides
- Backend applies overrides during message generation (personality/instructions → system prompt, temp/tokens → LLM params)
- Endpoints: GET/PUT/DELETE `/api/agents/{agent_id}/my-settings`
- All 21 tests passed (iteration_34)

### Custom Domain UI & White-Label Branding (Mar 1, 2026)
- **Branding & Domain** admin tab with 4 sections:
  - Brand Identity: Platform Name, Tagline, Footer Text, Support Email
  - Logo & Favicon: File upload (PNG/JPG/SVG/WebP, 5MB max) + URL paste
  - Brand Colors: Primary & Accent color pickers with hex input & live preview
  - Custom Domain: Domain input, CNAME DNS instructions, Verify DNS button
- **BrandingProvider** context: Applies CSS variables, dynamic favicon, page title
- **BrandFooter** dynamically shows platform name and footer text
- Backend: GET/POST /api/admin/branding, POST /upload-logo, POST /verify-domain, GET /branding/public
- All 18 tests passed (iteration_33)

### Notification Center, User Insights, Onboarding, Analytics, AI Controls, SMTP, Refactoring
- See previous changelog for full details on these features

## Previously Implemented
- 21 AI agents with Brain Editor, Commander AI, Agent Collaboration
- Auto model selection (25 models), File/Image/Video generation
- Voice mode (OpenAI TTS), Dynamic Stripe subscriptions + Credits
- Team collaboration, JWT + Google OAuth, Kubernetes /health

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Backend refactoring - extract admin routes from server.py (~5700 lines) to routes/admin.py
- P1: Third-party integrations (Slack, Calendly, Airtable) - UI exists, backend logic not implemented
- P2: AdminDashboard.jsx refactoring - extract remaining tabs into components
- P2: Complete server.py modularization - extract auth, chats, teams routes

## Architecture
```
/app/backend/
├── server.py (5700+ lines - monolithic, needs refactoring)
├── config.py (agent definitions, tool configs)
├── models/schemas.py (Pydantic models)
├── uploads/ (file storage)
└── tests/

/app/frontend/src/
├── App.js (BrandingProvider wraps app)
├── pages/
│   ├── AdminDashboard.jsx (all admin tabs)
│   ├── BrandingTab.jsx (branding & domain admin UI)
│   ├── AgentChat.jsx (chat + Customize button)
│   └── ...
└── components/
    ├── AgentCustomizePanel.jsx (NEW - per-user agent settings)
    ├── BrandingProvider.jsx (dynamic branding context)
    ├── BrandFooter.jsx (dynamic footer)
    └── ...
```

## Key DB Collections
- `user_agent_overrides`: {user_id, agent_id, temperature, max_tokens, personality_tone, custom_instructions}
- `platform_config`: {config_type: "branding", platform_name, primary_color, accent_color, custom_domain, ...}

## Test Reports (All 100%)
- iteration_34: User Agent Customization + Admin Brain/Toggle + Branding (21/21 backend + all frontend)
- iteration_33: Branding & Custom Domain (18/18)
