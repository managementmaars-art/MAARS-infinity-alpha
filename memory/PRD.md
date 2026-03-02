# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform ("MAARS Command") comparable to Sintra.ai and Emergent, ready for launch to sell subscriptions. Features include specialized AI agents, Commander AI delegation, multi-model support, Stripe subscriptions, admin dashboard, RAG knowledge base, web browsing, image analysis (vision), product scanning, and commercial video generation.

## Core Requirements
1. AI Team & Commander AI with 21+ specialized agents
2. Multi-model support (GPT-5.2, Claude, Gemini, etc.) with universal key + direct provider keys
3. Stripe-integrated subscription tiers with dynamic credit system
4. Admin dashboard for pricing, agent management, analytics
5. RAG knowledge base (per-agent document uploads)
6. Automatic web browsing for real-time information
7. Image analysis (vision) for all agents
8. Product scanning - identify products from images, search web for details/pricing/reviews, find high-quality reference images
9. Video/image generation (Sora 2, DALL-E 3, Nano Banana 2) with product-aware pipeline
10. TTS/STT (ElevenLabs, OpenAI, Whisper)
11. Real-time Commander delegation with live collaboration workflow

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async driver)
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Auth:** JWT + Emergent Google OAuth (extracted to auth.py + routes/auth.py)
- **AI:** emergentintegrations library with Emergent LLM Key
- **Search:** DuckDuckGo text + image search + BeautifulSoup4
- **RAG:** scikit-learn TF-IDF local model
- **Payments:** Stripe
- **Database:** Shared via db.py module

## What's Implemented (Complete Feature List)
- [x] Full auth system (JWT + Google OAuth) - refactored
- [x] 21+ specialized AI agents with Commander AI delegation
- [x] Real-time Commander Collaboration Workflow (live progress)
- [x] Multi-model LLM support with auto-selection
- [x] Stripe subscription integration (multi-tier)
- [x] Dynamic model-aware credit system with UI display
- [x] Admin dashboard with full management capabilities
- [x] RAG knowledge base (TF-IDF, per-agent documents)
- [x] Automatic web browsing (DuckDuckGo + synthesis)
- [x] Image analysis (vision) - all agents, drag-and-drop + clipboard paste
- [x] **Product Scanner** - vision-based product ID + web details/images + reference image download
- [x] **Product-aware video generation** - Sora 2 uses product scan data for accurate prompts + reference images
- [x] Video generation (Sora 2) with background processing
- [x] Image generation (DALL-E 3, Nano Banana 2, GPT Image 1)
- [x] TTS/STT (ElevenLabs, OpenAI TTS, Whisper)
- [x] Agent customization panel
- [x] Notification system
- [x] Admin analytics, branding, SMTP config
- [x] Integration tools (Slack, GitHub, SendGrid, Resend, Twilio, Airtable, Calendly, Giphy)
- [x] Agent-to-Agent consultation ([CONSULT:] pattern)
- [x] Backend refactoring: auth.py, db.py, routes/auth.py
- [x] Frontend refactoring: CustomPackagesTab, IntegrationsTab extracted

## Product Scanner Pipeline (NEW)
1. User uploads product image → Vision AI identifies product (brand, model, features)
2. Agent auto-uses `product_scan` tool → searches web for specs, pricing, reviews
3. DuckDuckGo image search finds high-quality professional product photos
4. Best reference image downloaded for video generation source
5. If video requested → Sora 2 uses product scan data for cinematic prompt + reference image
6. Frontend shows special ProductScanCard with gradient border and image thumbnails

## Backlog
### P2 - Remaining Refactoring
- Extract agent, chat, admin, generation routes from server.py (~5900 lines)
- Extract remaining AdminDashboard inline tabs (Overview, Users, Agents, Transactions, PricingManager, PaymentSetup)

## Key Files
- `/app/backend/server.py` - Main server
- `/app/backend/auth.py` - Shared auth utilities
- `/app/backend/db.py` - Shared database connection
- `/app/backend/routes/auth.py` - Auth route endpoints
- `/app/backend/services/product_scanner.py` - Product scanning service
- `/app/backend/services/rag_service.py` - RAG TF-IDF service
- `/app/backend/services/web_search.py` - Web search service
- `/app/backend/config.py` - Agent definitions, tools, tool maps
- `/app/frontend/src/pages/AgentChat.jsx` - Main chat interface
- `/app/frontend/src/pages/AdminDashboard.jsx` - Admin panel
- `/app/frontend/src/components/chat/CollaborationWorkflow.jsx` - Live Commander delegation view
- `/app/frontend/src/components/admin/CustomPackagesTab.jsx` - Extracted tab
- `/app/frontend/src/components/admin/IntegrationsTab.jsx` - Extracted tab

## Test Reports
- `/app/test_reports/iteration_43.json` - Auth extraction, vision, tab extraction (100% pass)
- `/app/test_reports/iteration_44.json` - Collaboration workflow, Commander progress (100% pass)
- `/app/test_reports/iteration_45.json` - Product scanner, full pipeline (100% pass)
