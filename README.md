# MAARS Infinity - Autonomous AI Enterprise Operating System

**MAARS Infinity** is a full-stack AI operations platform featuring multi-agent orchestration, governance controls, integrations, and an enterprise control surface. It comprises a React frontend and FastAPI backend supporting 458+ agents across 28 networks with 13 LLM providers.

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ and Yarn
- MongoDB 5.0+
- API keys for LLM providers (optional based on your use case)

### Git hooks — one-time setup per clone

This repo ships a `post-commit` hook under `.githooks/` that auto-appends
every commit to the audit trail in `.claude/MEMORY.md`. Enable it once
per clone:

```bash
git config core.hooksPath .githooks
```

The hook is idempotent (won't re-log the same commit) and never blocks a
commit on failure. Hand-written audit sections (`## Audit NNN`) still sit
above the `## Commit log` divider; the hook only maintains the commit
trail below it.

### Local Development (5 minutes)

#### 1. Clone & Setup Backend
```bash
cd backend
cp ../.env.example ../.env
# Edit .env with your MongoDB URL and API keys
pip install -r requirements.txt
python server.py
```
Backend runs on `http://localhost:8000` with docs at `/docs`

#### 2. Setup Frontend
```bash
cd frontend
cp ../.env.example .env.local
# Edit .env.local and set REACT_APP_BACKEND_URL=http://localhost:8000
yarn install
yarn start
```
Frontend runs on `http://localhost:3000`

#### 3. Validate
- Open `http://localhost:3000` in your browser
- Backend health check: `curl http://localhost:8000/api/health`
- API Explorer: `http://localhost:8000/docs`

## Detailed Setup Guides

- **[SETUP.md](SETUP.md)** — Complete local development guide with troubleshooting
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Production deployment, Docker, environment configuration
- **[MAARS_ARCHITECTURE.md](memory/MAARS_ARCHITECTURE.md)** — System architecture and design documentation

## Project Structure

```
MAARS-Command/
├── backend/                    # FastAPI application
│   ├── server.py              # Main entry point
│   ├── config.py              # Agent catalog, system prompts, tool definitions
│   ├── db.py                  # MongoDB connection
│   ├── auth.py                # JWT and session authentication
│   ├── requirements.txt        # Python dependencies
│   ├── routes/                # API endpoints (auth, chats, agents, tasks, etc.)
│   ├── services/              # Business logic and orchestration
│   ├── kernel/                # Runtime execution and governance
│   ├── governance/            # Policy engine and circuit breakers
│   ├── router/                # LLM routing and fallback logic
│   ├── memory_system/         # Short/long-term memory and knowledge graphs
│   ├── verification/          # Fact-checking, hallucination detection
│   ├── orchestrator/          # Task graph execution and DAG resolution
│   └── static/                # Generated avatars and assets
│
├── frontend/                   # Create React App with CRACO
│   ├── package.json           # Node dependencies
│   ├── src/
│   │   ├── App.js             # Main router and layout
│   │   ├── pages/             # Feature pages
│   │   ├── components/        # Reusable UI components
│   │   └── lib/               # Utilities and hooks
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── craco.config.js         # Custom build configuration
│
├── .claude/
│   ├── skills/                 # 58k+ cleaned Claude Code skills (name + description YAML)
│   │                           # Loaded by backend at agent creation (see services/skills_service.py)
│   ├── skills_backup/          # Original unfixed skills — kept as backup
│   └── settings.json           # Claude Code permissions
├── scripts/legacy/             # Archived one-off migration scripts (batch creators, fetchers)
├── design_guidelines.json      # Brand identity and design system
├── agents.md                   # Project architecture documentation
├── memory/                     # Documentation and project notes
└── test_reports/               # Test iteration results
```

## Core Features

- **Skill Library** — 58k+ curated skills at `.claude/skills/` automatically matched to agents and ingested as knowledge chunks
- **Multi-Agent Orchestration** — 458+ agents across 28 networks managed via Commander Orion
- **Task Graph Execution** — DAG-based task decomposition and parallel execution
- **Governance & Approvals** — Policy engine, audit logs, trust scoring, and circuit breakers
- **LLM Routing** — Intelligent model selection with cost optimization and fallback logic
- **Built-in Tools** — Web search, code execution, email, calendar, Stripe, document generation
- **Memory Systems** — Short-term, working, long-term, episodic, and semantic memory
- **Verification Layer** — Fact-checking, source ranking, hallucination detection, code validation
- **Integration Hub** — OAuth, SMTP, Stripe, calendar services, web search, social media
- **Observability** — Dashboards, trace logs, cost tracking, incident management
- **Enterprise Controls** — Admin panels, subscriptions/credits, approvals, usage analytics

## API Overview

All endpoints are prefixed with `/api`:

| Endpoint | Purpose |
|----------|---------|
| `/auth/*` | User registration, login, JWT tokens, OAuth |
| `/chats/*` | Chat history, messages, LLM calls, tool execution |
| `/agents/*` | Agent CRUD, configuration, execution |
| `/tasks/*` | Task creation, orchestration, execution logs |
| `/teams/*` | Multi-user collaboration and team management |
| `/subscriptions/*` | Billing, credits, usage tracking |
| `/approvals/*` | Governance and approval workflows |
| `/knowledge-base/*` | RAG context, document ingestion |
| `/admin/*` | System administration, policy management |
| `/ws` | WebSocket real-time updates |
| `/docs` | Interactive API explorer (Swagger) |

See [DEPLOYMENT.md](DEPLOYMENT.md#api-endpoints) for the complete API reference.

## Development

### Running Tests
```bash
# Backend
cd backend
python -m pytest tests/

# Frontend
cd frontend
yarn test
```

### Code Quality
```bash
# Backend linting and formatting
cd backend
flake8 . && black .

# Frontend
cd frontend
yarn lint
```

## Environment Variables

See [.env.example](.env.example) for all configuration options with descriptions. Key required variables:

**Backend:**
- `MONGO_URL` — MongoDB connection string
- `DB_NAME` — Database name
- `JWT_SECRET` — Secret for JWT tokens (change in production!)

**Frontend:**
- `REACT_APP_BACKEND_URL` — Backend API endpoint (e.g., `http://localhost:8000`)

**LLM Providers (optional, at least one required):**
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `COHERE_API_KEY`

**Integrations (optional):**
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`
- Google OAuth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- Stripe: `STRIPE_API_KEY`
- Web Search: `DUCKDUCKGO_ENABLED`, `SERPER_API_KEY`

## Deployment

For production deployment with Docker, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick Docker start:
```bash
docker-compose up -d
```

## Architecture & Design

- **Design System:** Dark-mode cyber-professional theme using Tailwind CSS, Radix UI primitives
- **Backend:** FastAPI with Motor (async MongoDB driver), service-oriented architecture
- **Frontend:** Create React App with CRACO, React Router v7, React Hook Form, Tailwind CSS
- **Authentication:** JWT + HTTP-only session cookies, OAuth 2.0 support
- **Database:** MongoDB with comprehensive indexing for performance
- **Real-time:** WebSocket support for live updates and collaboration

## Security

- JWT tokens with configurable expiration
- CORS protection with origin whitelisting
- Rate limiting on sensitive endpoints
- Audit logging of all administrative actions
- Policy engine for workflow approval gates
- Credential validation on startup (production mode)

See [DEPLOYMENT.md](DEPLOYMENT.md#security) for security best practices.

## Troubleshooting

### Backend won't start
```
✓ Check MongoDB is running: mongosh --eval "db.adminCommand('ping')"
✓ Verify MONGO_URL and DB_NAME in .env
✓ Check all required LLM API keys are set
✓ Review logs in /app/backend/logs (if present)
```

### Frontend can't connect to backend
```
✓ Ensure backend is running on port 8000
✓ Check REACT_APP_BACKEND_URL in frontend/.env.local
✓ Verify CORS_ORIGINS in backend/.env includes frontend URL
✓ Check browser console for detailed error messages
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000           # macOS/Linux
netstat -ano | grep 8000 # Windows

# Change ports in .env and frontend/.env.local
```

For more help, see [SETUP.md](SETUP.md#troubleshooting).

## Support & Contributing

- **Report Issues:** Create a GitHub issue with steps to reproduce
- **Security Issues:** Contact the team directly (do not create public issues)
- **Contributions:** Follow the development setup and run tests before submitting PRs

## License

This project is built as part of MAARS Infinity. See LICENSE file for details.

## Team

Built by the MAARS team. See [agents.md](agents.md) for system architecture and operational notes.
