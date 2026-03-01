# MAARS Command by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform inspired by Sintra AI + Emergent. 20+ autonomous agents with separate brains, Commander AI delegation, agent collaboration, voice mode, file generation, subscriptions, admin dashboard, team collaboration — production-ready for selling subscriptions.

## User Personas
- **Admin (management.maars@marsgc.net):** Manages platform, agents, pricing, branding, knowledge bases
- **Subscribers:** Use AI agents for tasks, can customize agents, upload documents to knowledge bases
- **Team Members:** Collaborate within shared workspaces

## Core Requirements
1. AI Team & Commander AI with autonomous delegation
2. Multi-model support (GPT, Claude, Gemini) with universal + direct keys
3. Stripe subscription system with credit system
4. Admin panel for full platform management
5. Team collaboration via email invites
6. White-labeling with custom domains, logos, colors
7. RAG (Knowledge Base) for domain-specific knowledge per agent
8. Inter-agent communication and shared workspace context

## Implemented Features

### RAG Knowledge Base System (Mar 1, 2026 - LATEST)
- **Per-agent document upload:** PDFs, TXT, MD, CSV, DOCX (max 25MB)
- **Text extraction & chunking:** PyPDF2 for PDFs, overlapping chunks with page tracking
- **TF-IDF search:** Fast semantic search using sklearn (no external API needed)
- **RAG context injection:** Relevant knowledge base chunks auto-injected into agent prompts
- **Source citations:** Agents cite "According to [Document], Page X..."
- **Admin UI:** Knowledge Base tab in admin dashboard with agent selector, upload, search testing
- All tests passed (iteration_39: 9/9 backend, all frontend verified)

### UI Fixes (Mar 1, 2026)
- **Avatar persistence:** Past messages keep their original agent's avatar (stored agent_avatar in messages)
- **Agent switch toast:** "Switched to [agent name]" toast on agent change

### Previous Implementations
- P0 Verification (Markdown rendering, Nano Banana 2 image gen, Admin CORS fix) — iteration_38
- Cross-Agent Communication System — iteration_37
- CORS Bug Fix (removed credentials: include) — iteration_36
- User Agent Customization + White-Label Branding — iterations_33-34
- Notification Center, Onboarding, Analytics, AI Controls, SMTP, 21 agents, Stripe, etc.

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!

## Architecture
```
Backend: FastAPI + MongoDB + TF-IDF (sklearn)
Frontend: React + Tailwind + Shadcn UI
RAG Flow:
  1. Admin uploads document to agent's knowledge base
  2. Background task extracts text, chunks it, stores in MongoDB
  3. User sends message to agent
  4. TF-IDF search finds relevant chunks
  5. Context injected into agent prompt with citation instructions
  6. Agent responds with cited sources
```

## Key Collections
- knowledge_docs: {doc_id, agent_id, title, filename, status, chunk_count, ...}
- knowledge_chunks: {chunk_id, doc_id, agent_id, doc_title, text, pages, chunk_index}
- user_agent_overrides: {user_id, agent_id, settings}
- config: {branding, custom_domain}

## Backlog (Prioritized)
- P1: Third-party integrations backend logic (Slack, Calendly, Airtable) — admin UI exists, backend execution logic is MOCKED
- P2: Backend refactoring — extract remaining routes from server.py to modular routers
- P2: AdminDashboard.jsx component extraction (Pricing, Users, Agents tabs)

## Test Reports (All 100%)
- iteration_39: RAG + avatar persistence + agent switch toast (9/9 + all frontend)
- iteration_38: Markdown + Nano Banana 2 + Admin controls (10/10 + all frontend)
- iteration_37: Cross-agent communication (14/14 + all frontend)
- iteration_36: CORS fix (17/17)
- iteration_35: Header toggles (12/12)
- iteration_34: User customization (21/21)
- iteration_33: Branding (18/18)
