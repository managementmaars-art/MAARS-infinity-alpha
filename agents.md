# AGENTS.md

## Project Overview
MAARS Infinity Alpha is a full-stack AI operations platform with a React frontend and a FastAPI backend. It supports multi-agent orchestration, chat-driven workflows, tool execution, governance controls, approvals, subscriptions/credits, and integrations (email, calendar, messaging, web search, etc.).

- **Frontend:** `frontend/` (Create React App + CRACO + Tailwind + Radix UI)
- **Backend:** `backend/` (FastAPI + Motor/MongoDB + service-oriented modules)
- **Core runtime model:** Agent-first architecture with Commander delegation, task orchestration, and execution logging.

## High-Level Architecture

### Backend (`backend/`)
- **Entry point:** `server.py`
  - Initializes FastAPI app, mounts static files, registers `/api` routes + websocket routes.
  - Performs startup seeding (`seed_default_agents`, `seed_default_tools`, policy/breaker seeds).
  - Creates many MongoDB indexes for chats, tasks, logs, approvals, knowledge, routing, memory, etc.
  - Adds middleware (CORS, rate limiting for infinity endpoints, lightweight in-memory response cache helpers).

- **Auth + DB core:**
  - `db.py`: MongoDB client/database connection from env vars.
  - `auth.py`: JWT + session-cookie auth, current-user/admin guards.

- **Agent and platform config:**
  - `config.py`: massive built-in agent catalog, system prompts, tool definitions, agent-to-tool map, brain profile defaults.
  - `infinity_catalog.py`: Infinity catalog/system prompt/network helpers.

- **Route layer (`routes/`):**
  - Covers auth, chats, tasks, teams, subscriptions, admin, generation/media, projects, workspace, approvals, enterprise, memory, kernel, websocket, infinity, etc.
  - Example heavy route: `routes/chats.py` handles chat CRUD, LLM calls, RAG context, tool execution, image/video/file generation, usage logging, credit deductions, and collaboration hooks.

- **Service layer (`services/`):**
  - Encapsulates orchestration and domain logic (LLM routing/fallback, agent operations, kernel execution logging, analytics, integrations, RAG, memory learning, product scan, web search).

- **Kernel/governance/runtime modules:**
  - `kernel/`, `governance/`, `runtime/`, `verification/`, `orchestrator/`, `router/`, `memory_system/` indicate a governed execution model with policy checks and observability.

### Frontend (`frontend/`)
- **Entry:** `src/index.js`
- **Main router/app shell:** `src/App.js`
  - Handles auth state, protected/admin routes, OAuth callback handling, and full page map.
  - Exposes a very large multi-page dashboard app (agent chat, admin tabs, observability, model router, workflow builder, integrations, portfolio, etc.).

- **UI:**
  - `src/components/ui/` has Radix-based primitives.
  - Feature pages in `src/pages/` reflect broad enterprise control surface.

## Operational Notes for Contributors
- Use `backend/server.py` as the source of truth for route registration and startup behavior.
- Keep business logic in `services/` and `kernel/` modules; avoid bloating route handlers further.
- When adding new entities, also add required Mongo indexes in startup.
- Respect credit/subscription checks and audit logging paths when extending chat/task execution flows.
- Frontend route additions should be mirrored in `App.js` with role protection where needed.

## Suggested Local Run Workflow
1. Configure backend env vars (`MONGO_URL`, `DB_NAME`, API keys, JWT secret, etc.).
2. Start backend from `backend/` with uvicorn entry for `server:app`.
3. Install frontend deps and run `yarn start` from `frontend/`.
4. Validate `/api/health` and authentication flow before feature testing.
