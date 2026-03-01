# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Video Generation Fix (Mar 1, 2026 - LATEST)
- **Backend retry logic**: Sora 2 retries once (30s delay) if first attempt returns empty
- **Frontend file hydration**: Pre-populates generatedFiles from DB when loading messages — videos/images completed in background now visible when returning to chat
- **Better error messages**: Detailed error logging instead of generic "returned empty"
- Verified: Sora 2 generated 5.8MB video successfully after retry

### Model-Aware Credit System (Mar 1, 2026)
- Dynamic credit costs: Economy=1, Fast=2, Flagship=3, Premium=5
- Generation add-ons: Image gen +5cr, Video gen +10cr
- 28 models across 9 providers in MODEL_CREDIT_COSTS
- Frontend credit badges in model selector, credits shown per message
- All tests passed (iteration_40: 9/9 backend, 6/6 frontend)

### RAG Knowledge Base System (Mar 1, 2026)
- Per-agent document upload, TF-IDF search, auto context injection, source citations
- All tests passed (iteration_39)

### Previous
- Markdown rendering, Nano Banana 2, Admin CORS fix, Cross-Agent Communication
- User Customization, White-Label Branding, 21 agents, Stripe, etc.

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — MOCKED
- P2: Backend refactoring, AdminDashboard.jsx extraction
