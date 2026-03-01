# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## Implemented Features

### Model-Aware Credit System (Mar 1, 2026 - LATEST)
- **Dynamic credit costs per model:** Economy=1, Fast=2, Flagship=3, Premium=5, Reasoning=2-5
- **Generation add-ons:** Image gen (Nano Banana 2) = +5 credits, Video gen (Sora 2) = +10 credits
- **MODEL_CREDIT_COSTS** map covers all 28 models across 9 providers
- **Frontend credit badges:** Color-coded pills (green/blue/amber/rose) in model selector
- **Chat credit display:** Shows credits deducted per message (e.g., "openai/gpt-5.2 • 3cr")
- **Nano Banana 2** added to landing page model cards and admin pricing table
- **Separate image gen cost tracking:** Usage logs with type='image_generation'
- All tests passed (iteration_40: 9/9 backend, 6/6 frontend)

### RAG Knowledge Base System (Mar 1, 2026)
- Per-agent document upload (PDF, TXT, MD, CSV, DOCX, max 25MB)
- TF-IDF search with cosine similarity, auto context injection, source citations
- Admin UI with agent selector, upload, search testing
- All tests passed (iteration_39: 9/9 backend, all frontend)

### UI Fixes (Mar 1, 2026)
- Avatar persistence for past messages, Agent switch toast notification

### Previous Implementations
- Markdown rendering, Nano Banana 2 image gen, Admin CORS fix — iteration_38
- Cross-Agent Communication System — iteration_37
- User Agent Customization + White-Label Branding — iterations_33-34
- All 21 agents, Commander AI, Voice Mode, Stripe Subscriptions, Team Collaboration

## Credit Tier Reference
| Tier | Credits | Models |
|---|---|---|
| Economy | 1 | GPT-4o Mini, Haiku, Gemini Flash, DeepSeek Chat, Mistral Small, Grok Mini, Command R |
| Fast/Standard | 2 | GPT-4o, Grok 2, Gemini Pro, O3 Mini, DeepSeek Reasoner, Mistral Medium, Sonar |
| Flagship | 3 | GPT-5.2, Claude Sonnet, Grok 3, Mistral Large, Command R+, Sonar Pro |
| Premium | 5 | Claude Opus, O3 |
| Image Gen | +5 | Nano Banana 2, GPT Image 1, DALL-E 3 |
| Video Gen | +10 | Sora 2 |

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Backlog (Prioritized)
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — MOCKED
- P2: Backend refactoring — extract remaining routes from server.py
- P2: AdminDashboard.jsx component extraction

## Test Reports (All 100%)
- iteration_40: Credit system (9/9 + 6/6 frontend)
- iteration_39: RAG + avatar + toast (9/9 + all frontend)
- iteration_38: Markdown + Nano Banana 2 + Admin controls (10/10 + all frontend)
- iteration_37: Cross-agent communication (14/14 + all frontend)
