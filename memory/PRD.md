# MAARS Command by MAARS Global Corporation - PRD

## Product Overview
A commercial, production-ready AI team platform comparable to platforms like Sintra.ai and Emergent. Features a team of specialized AI agents led by a "Commander AI" that delegates tasks automatically, with support for multiple AI models, credit system, subscription management, and admin panel.

## Core Requirements
1. **AI Team & Commander AI** - Team of 20+ specialized AI agents led by Commander Orion
2. **Multi-Model Support** - OpenAI, Anthropic, Gemini, XAI, DeepSeek, Mistral, Perplexity, Cohere
3. **Monetization** - Multi-tiered subscription model (Free, Starter, Pro, Business) with Stripe
4. **Admin Section** - Full admin panel for pricing, users, agents, analytics, branding
5. **Knowledge Base (RAG)** - Per-agent document upload and retrieval
6. **Web Browsing** - DuckDuckGo integration for real-time web search
7. **Image Analysis (Vision)** - Analyze uploaded images via multimodal models
8. **Product Catalog** - Save, manage, and scan products; batch CSV/XLSX import
9. **Team Collaboration** - Invite members, shared chat access

## Architecture

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── server.py                 # Thin app shell (~91 lines)
├── db.py                     # Shared MongoDB client
├── auth.py                   # Auth helpers (JWT, admin check)
├── config.py                 # Agent definitions, tools config
├── shared/
│   ├── constants.py          # SUBSCRIPTION_PLANS, STRIPE, UPLOAD_DIR, etc.
│   └── utils.py              # send_email, get_api_keys, create_notification
├── services/
│   ├── llm_service.py        # Model selection, LLM calling, file generation
│   ├── agent_service.py      # Tool execution, agent delegation, commander
│   ├── rag_service.py        # Knowledge base search
│   ├── web_search_service.py # DuckDuckGo search
│   └── product_scanner.py    # Vision-based product identification
└── routes/
    ├── auth.py               # Registration, login, session
    ├── agents.py             # Agent CRUD, user customization
    ├── chats.py              # Chat CRUD, send_message, feedback
    ├── tasks.py              # Task CRUD, execution
    ├── teams.py              # Team collaboration
    ├── subscriptions.py      # Plans, checkout, credits
    ├── admin.py              # All admin endpoints (~1771 lines)
    ├── generation.py         # Document/image/video generation
    ├── media.py              # Upload, TTS, STT, models
    ├── notifications_routes.py # Notification center
    ├── user.py               # Stats, insights
    ├── products.py           # Product catalog, batch import
    └── knowledge_base.py     # Knowledge doc CRUD
```

### Frontend (React + Tailwind)
```
/app/frontend/src/
├── App.js                    # Router, auth context
├── pages/
│   ├── AdminDashboard.jsx    # Thin shell (~498 lines)
│   ├── AgentChat.jsx         # Chat interface
│   └── ProductCatalog.jsx    # Product management
└── components/
    ├── admin/
    │   ├── CustomPackagesTab.jsx
    │   ├── IntegrationsTab.jsx
    │   └── tabs/
    │       ├── OverviewTab.jsx
    │       ├── UsersTab.jsx
    │       ├── AgentsTab.jsx
    │       ├── TransactionsTab.jsx
    │       ├── ApiKeysTab.jsx
    │       ├── PricingManagerTab.jsx
    │       ├── PaymentSetupTab.jsx
    │       └── AuditLogTab.jsx
    └── chat/
        ├── ChatSearch.jsx
        ├── CollaborationWorkflow.jsx
        └── ProductScanCard.jsx
```

## What's Been Implemented
- All 20+ AI agents with Commander AI delegation
- Multi-provider LLM support with auto model selection
- Credit system with model-aware costs
- Stripe payment integration
- Full admin panel with analytics, pricing, user/agent management
- RAG knowledge base with document upload
- Web browsing tool (DuckDuckGo)
- Image analysis (vision) with drag-and-drop UX
- Real-time agent collaboration view
- Product scanning pipeline (vision + web search)
- Full product catalog with batch CSV/XLSX import
- Team collaboration with invites
- Email notifications (SMTP)
- Branding customization
- **COMPLETED: Major codebase refactoring (Feb 2026)**
  - Backend: server.py 6039 → 91 lines (14 route modules)
  - Frontend: AdminDashboard.jsx 2032 → 498 lines (7 extracted tabs)

- **COMPLETED: Enhancement Features (Feb 2026)**
  - Chat Search: search across all user conversations
  - Message Pin/Export: pin messages, export chat as text, share with team
  - Enhanced Analytics: retention cohorts, revenue projections, credit burn analysis
  - Admin Audit Log: tracks all admin actions with timestamps
  - MongoDB performance indexes on all key collections

- **COMPLETED: Integration & Collaboration (Mar 2026)**
  - Google Calendar: full implementation (list events, create events with attendees)
  - Gmail: send emails via Google Suite service account with delegate email
  - Integration Status Dashboard: admin view of all 17 tools with active/inactive status
  - Google Suite test endpoint for validating service account credentials
  - Team Activity Feed: recent shared chats and member activity
  - Team Stats: member count, total chats, shared chats, per-member breakdown

- **COMPLETED: P1 Performance, Analytics, Wizard (Mar 2026)**
  - Performance: Server-side pagination for chats, products, admin users, transactions
  - Performance: In-memory TTL cache for agents list and frequently accessed data
  - Analytics: Agent Performance Leaderboard with satisfaction scores
  - Analytics: User Engagement Heatmap (activity by hour/day of week)
  - Analytics: Revenue Trends with cumulative tracking and growth rates
  - Analytics: CSV Export for users, revenue, agents, and overview reports
  - Integration Quick Setup Wizard: Guided step-by-step modal for Slack, GitHub, Google Suite
  - Team Notifications: Notifications for team invites, chat shares, member joins

## Remaining Tasks (Prioritized)
### P2 - Further Enhancements
- User onboarding improvements
- Advanced search and filtering across all entities
- Real-time collaboration (WebSocket for team activity)
- Multi-language support

## Credentials
- **Admin:** management.maars@marsgc.net / admin123
- **Test User:** test@test.com / test123

## 3rd Party Integrations
- **Stripe** - Payment processing (user API key)
- **Image Gen** - Gemini Nano Banana 2, GPT Image 1, DALL-E 3
- **Video Gen** - Sora 2
- **TTS** - ElevenLabs, OpenAI TTS
- **STT** - Whisper
- **Web Search** - DuckDuckGo
- **LLMs** - Multiple providers via Emergent LLM Key or direct keys
