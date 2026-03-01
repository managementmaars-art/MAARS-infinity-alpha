# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard — production-ready for selling subscriptions.

## Implemented Features

### Agent Web Browsing (Mar 1, 2026 - LATEST)
- **Auto-detect:** Regex pattern matching (12 patterns) detects when a message needs web data
- **DuckDuckGo search:** Uses `ddgs` library for live web search (4 results per query)
- **Page scraping:** BeautifulSoup extracts clean text from top results with 8s timeout
- **Context injection:** Web data injected before workspace/RAG context for priority
- **System prompt updated:** Rule 5 tells agents they HAVE web browsing capability
- **Globe icon:** Cyan Globe icon + "Web" label shown on messages that used web search
- All tests passed (iteration_41: 8/8 backend, 6/6 frontend)

### Video Generation Fix (Mar 1, 2026)
- Sora 2 retry logic (30s delay), frontend file hydration on chat reload

### Model-Aware Credit System (Mar 1, 2026)
- 28 models, tiered credits: Economy=1, Fast=2, Flagship=3, Premium=5, Image+5, Video+10

### RAG Knowledge Base (Mar 1, 2026)
- Per-agent document upload, TF-IDF search, source citations

### Previous
- Markdown rendering, Nano Banana 2, Admin CORS fix, Cross-Agent Communication
- User Customization, White-Label Branding, 21 agents, Stripe, Team Collaboration

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — MOCKED
- P2: Backend refactoring, AdminDashboard.jsx extraction

## Test Reports (All 100%)
- iteration_41: Web browsing (8/8 + 6/6)
- iteration_40: Credit system (9/9 + 6/6)
- iteration_39: RAG + avatar + toast (9/9 + all)
- iteration_38: Markdown + Nano Banana 2 + Admin (10/10 + all)
