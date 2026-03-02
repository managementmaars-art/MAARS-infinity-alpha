# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Build a full-stack AI team platform ("MAARS Command") comparable to Sintra.ai and Emergent, ready for launch to sell subscriptions. Features include specialized AI agents, Commander AI delegation, multi-model support, Stripe subscriptions, admin dashboard, RAG knowledge base, web browsing, image analysis (vision), product scanning, product catalog, and commercial video generation.

## Core Requirements
1. AI Team & Commander AI with 21+ specialized agents
2. Multi-model support with universal key + direct provider keys
3. Stripe-integrated subscription tiers with dynamic credit system
4. Admin dashboard for pricing, agent management, analytics
5. RAG knowledge base (per-agent document uploads)
6. Automatic web browsing for real-time information
7. Image analysis (vision) for all agents
8. Product scanning - identify products from images, search web for details/pricing/reviews
9. Product Catalog - save products, track prices, one-click generate marketing content
10. Video/image generation (Sora 2, DALL-E 3, Nano Banana 2) with product-aware pipeline
11. TTS/STT (ElevenLabs, OpenAI, Whisper)
12. Real-time Commander delegation with live collaboration workflow

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
- [x] Product Scanner - vision-based product ID + web details/images
- [x] **Product Catalog** - save/manage products, re-scan, one-click content generation
- [x] **Quick Generate** - Video prompts, Ad Copy, Social Posts, Full Campaigns from catalog
- [x] **Admin Product View** - see all users' product catalogs
- [x] **Save to Catalog** button in chat when product_scan results appear
- [x] Product-aware video generation (Sora 2 uses product scan data)
- [x] Video generation (Sora 2) with background processing
- [x] Image generation (DALL-E 3, Nano Banana 2, GPT Image 1)
- [x] TTS/STT (ElevenLabs, OpenAI TTS, Whisper)
- [x] Agent customization panel
- [x] Notification system
- [x] Admin analytics, branding, SMTP config
- [x] Integration tools (Slack, GitHub, SendGrid, etc.)
- [x] Backend refactoring: auth.py, db.py, routes/auth.py, routes/products.py
- [x] Frontend refactoring: CustomPackagesTab, IntegrationsTab extracted

## Product Catalog Feature Details
- **Save:** Users save scanned products from chat or manually
- **Manage:** View, update, delete products from dedicated /products page
- **Re-scan:** One-click re-scan fetches latest web data and price history
- **Quick Generate:** 4 content types from any saved product:
  - Video Prompt (Sora 2 ready)
  - Ad Copy (Google/Facebook Ads)
  - Social Posts (Instagram, Twitter, LinkedIn, TikTok, Facebook)
  - Full Campaign (comprehensive marketing brief)
- **Admin:** Admin sees all users' catalogs with user info and generation counts
- **Integration:** "Save to Catalog" button in chat execution steps

## Backlog
### P2 - Remaining Refactoring
- Extract agent, chat, admin, generation routes from server.py
- Extract remaining AdminDashboard inline tabs

## Key Files
- `/app/backend/server.py` - Main server
- `/app/backend/auth.py` - Shared auth utilities
- `/app/backend/db.py` - Shared database connection
- `/app/backend/routes/auth.py` - Auth routes
- `/app/backend/routes/products.py` - Product catalog routes
- `/app/backend/services/product_scanner.py` - Product scanning service
- `/app/backend/services/rag_service.py` - RAG TF-IDF service
- `/app/backend/services/web_search.py` - Web search service
- `/app/backend/config.py` - Agent definitions, tools, tool maps
- `/app/frontend/src/pages/ProductCatalog.jsx` - Product catalog page
- `/app/frontend/src/pages/AgentChat.jsx` - Main chat interface
- `/app/frontend/src/pages/AdminDashboard.jsx` - Admin panel
- `/app/frontend/src/components/chat/CollaborationWorkflow.jsx` - Commander view

## Test Reports
- iterations 43-45: All passed 100%
- Manual API testing: Product CRUD all verified (create, read, update, delete, admin list)
- Frontend verified via screenshots: product grid, detail panel, generate buttons
