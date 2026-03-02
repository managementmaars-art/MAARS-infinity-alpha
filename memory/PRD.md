# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform ("MAARS Command") comparable to Sintra.ai and Emergent, ready for launch to sell subscriptions. Features include specialized AI agents, Commander AI delegation, multi-model support, Stripe subscriptions, admin dashboard, RAG knowledge base, web browsing, image analysis (vision), and multilingual audio I/O.

## Core Requirements
1. AI Team & Commander AI with 21+ specialized agents
2. Multi-model support (GPT-5.2, Claude, Gemini, etc.) with universal key + direct provider keys
3. Stripe-integrated subscription tiers with dynamic credit system
4. Admin dashboard for pricing, agent management, analytics
5. RAG knowledge base (per-agent document uploads)
6. Automatic web browsing for real-time information
7. Image analysis (vision) for all agents
8. Video/image generation (Sora 2, DALL-E 3, Nano Banana 2)
9. TTS/STT (ElevenLabs, OpenAI, Whisper)

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async driver)
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Auth:** JWT + Emergent Google OAuth
- **AI:** emergentintegrations library with Emergent LLM Key
- **Search:** DuckDuckGo + BeautifulSoup4
- **RAG:** scikit-learn TF-IDF local model
- **Payments:** Stripe

## What's Implemented (as of March 2, 2026)
- [x] Full auth system (JWT + Google OAuth) - **refactored to routes/auth.py**
- [x] 21+ specialized AI agents with Commander AI delegation
- [x] Multi-model LLM support with auto-selection
- [x] Stripe subscription integration (multi-tier)
- [x] Dynamic model-aware credit system with UI display
- [x] Admin dashboard with full management capabilities
- [x] RAG knowledge base (TF-IDF, per-agent documents)
- [x] Automatic web browsing (DuckDuckGo + synthesis)
- [x] Image analysis (vision) - all agents can analyze uploaded images
- [x] Drag-and-drop file uploads + clipboard paste
- [x] AI Vision badge on image attachments
- [x] Video generation (Sora 2) with background processing
- [x] Image generation (DALL-E 3, Nano Banana 2, GPT Image 1)
- [x] TTS/STT (ElevenLabs, OpenAI TTS, Whisper)
- [x] Agent customization panel
- [x] Notification system
- [x] Admin analytics, branding, SMTP config
- [x] Backend refactoring: auth routes extracted to routes/auth.py, shared auth module at auth.py, shared DB at db.py
- [x] Frontend refactoring: CustomPackagesTab and IntegrationsTab extracted to components/admin/

## Backlog
### P1
- Implement backend logic to USE saved integration API keys (Slack, Airtable, GitHub, etc.) - currently MOCKED

### P2
- Continue backend refactoring: extract agent, chat, admin, generation routes from server.py
- Continue frontend refactoring: extract remaining AdminDashboard inline tabs (Overview, Users, Agents, Transactions, PricingManager, PaymentSetup) to components

## Key Files
- `/app/backend/server.py` - Main server (still large, ~5900 lines)
- `/app/backend/auth.py` - Shared auth utilities
- `/app/backend/db.py` - Shared database connection
- `/app/backend/routes/auth.py` - Auth route endpoints
- `/app/backend/services/rag_service.py` - RAG TF-IDF service
- `/app/backend/services/web_search_service.py` - Web search service
- `/app/frontend/src/pages/AgentChat.jsx` - Main chat interface
- `/app/frontend/src/pages/AdminDashboard.jsx` - Admin panel
- `/app/frontend/src/components/admin/CustomPackagesTab.jsx` - Extracted tab
- `/app/frontend/src/components/admin/IntegrationsTab.jsx` - Extracted tab
