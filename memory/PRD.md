# MAARS Command - Product Requirements Document

## Original Problem Statement
Make the "MAARS Command" application absolutely market ready/ready for official launch. This involves:
- **P0: About Page & Documentation:** Complete overhaul with all 458+ agents, simple language, print-ready output via browser's native print dialog
- **P1: Agent Team Builder, Advanced Trust Analytics, Agent-to-Agent Collaboration**

## Architecture
- **Backend:** FastAPI (Python) + MongoDB
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI
- **AI:** 13 providers via Emergent Universal Key, DALL-E for avatars

## Completed Features

### P0 - About Page & Documentation (COMPLETE)
- Comprehensive About page with all system descriptions in 6th-grader language
- Dynamic loading of 458+ agents with full descriptions, skills, tools, autonomy levels
- Support email updated to support.maars@marsgc.net
- Print-ready output via `window.print()` with comprehensive `@media print` CSS
- Clean page breaks: each major section starts on new page (98-page PDF verified)
- Print CSS: white background, dark text, no sidebar/watermark, proper margins

### P1 - Agent Team Builder (COMPLETE)
- UI: `frontend/src/pages/TeamBuilder.jsx`
- Backend: `/api/teams` endpoints (POST, GET)

### P1 - Advanced Trust Analytics (COMPLETE)
- Enhanced `frontend/src/pages/TrustScores.jsx` with new widgets

### P1 - Agent-to-Agent Collaboration (COMPLETE)
- Upgraded `frontend/src/pages/CollaborationEngine.jsx`

### Critical Bug Fixes
- Avatar persistence: non-destructive seeding in `backend/services/kernel_service.py`
- Legacy "MAARS Infinity" branding removed across codebase

## Key Files
- `frontend/src/pages/AboutPage.jsx` - Main About page
- `frontend/src/index.css` - Print CSS styles
- `frontend/src/components/layout/DashboardLayout.jsx` - Sidebar (hidden in print)
- `frontend/src/App.js` - Watermark component (hidden in print)
- `backend/main.py` - All API endpoints
- `backend/services/kernel_service.py` - Agent seeding & descriptions

## Key Endpoints
- `/api/agents` (GET) - Agent data for About page
- `/api/teams` (POST, GET) - Team Builder

## Credentials
- Admin: management.maars@marsgc.net

## Backlog
- Remove dead code: `/api/download-summary` endpoint and `backend/services/summary.py`
- Remove unused html2pdf.js CDN script from `public/index.html`
