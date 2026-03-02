# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ autonomous agents, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard — production-ready for selling subscriptions.

## Implemented Features

### Production-Grade Web Browsing (Mar 2, 2026 - LATEST)
- **ChatGPT-like browsing:** Agents auto-search internet for factual/current questions
- **Smart detection:** FORCE patterns (dates, prices, news), SOFT patterns (2+ needed), question heuristic
- **DuckDuckGo search + page scraping:** 5 results, scrapes top 3 with BeautifulSoup
- **Key innovation:** Web data injected into USER MESSAGE (not system prompt) — forces LLM to use it
- **Source citations:** Agents cite with [Title](URL) format naturally
- **Globe icon:** Cyan indicator on web-searched messages in chat UI
- **No false triggers:** Greetings, short messages correctly skipped
- All tests passed (iteration_42: 10/10 backend, 6/6 frontend)

### Previous Features
- Model-Aware Credit System (28 models, tiered credits)
- RAG Knowledge Base (per-agent docs, TF-IDF search, citations)
- Video Gen Fix (Sora 2 retry), Avatar Persistence, Agent Switch Toast
- Markdown rendering, Nano Banana 2, Cross-Agent Communication
- User Customization, White-Label Branding, 21 agents, Stripe

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — MOCKED
- P2: Backend refactoring, AdminDashboard.jsx extraction
