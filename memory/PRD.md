# MAARS Command — Comprehensive System Summary
## By MAARS Global Corporation

---

## 1. PLATFORM OVERVIEW

**MAARS Command** is an autonomous multi-agent AI business operating system that combines the capabilities of preset specialist business agents (like Sintra.ai) with autonomous execution, memory, tool use, and app building (like Emergent.sh). It is a full-stack web application built with:

- **Backend**: FastAPI (Python) with MongoDB
- **Frontend**: React with Tailwind CSS, Shadcn/UI components
- **AI Engine**: Multi-provider LLM support via Emergent Integrations (OpenAI, Anthropic, Google Gemini)
- **Payments**: Stripe integration for credit-based billing

---

## 2. THE 41-AGENT AI WORKFORCE

MAARS Command deploys **41 specialized AI agents** organized across 8 organizational layers, each with a unique "Custom Brain Profile" that defines their LLM model, tools, autonomy level, and communication style.

### Executive Layer (4 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Commander Orion | Commander | Strategic planning, goal decomposition, workforce orchestration |
| Chief Strategy Officer | Strategist | Long-term strategy, market analysis, competitive intelligence |
| Revenue Strategist | Revenue | Revenue optimization, pricing strategy, monetization |
| Investor Relations | Investor Relations | Investor communications, fundraising, financial reporting |

### Product & Technical Layer (6 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Product Manager | PM | Product roadmaps, feature prioritization, user stories |
| App Developer | Developer | Full-stack development, code generation, debugging |
| Automation Engineer | Automation | Workflow automation, CI/CD, process optimization |
| AI Optimizer | AI Specialist | ML model tuning, AI performance, cost optimization |
| Data Engineer | Data Engineering | Data pipelines, ETL, database architecture |
| Cybersecurity Officer | Security | Security audits, vulnerability assessment, compliance |

### Creative & Brand Layer (7 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Brand Architect | Brand Strategy | Brand identity, positioning, visual language |
| Graphics Designer | Visual Design | Image creation, visual assets, marketing materials |
| Video Specialist | Video Production | Video content, animation, motion graphics |
| Copywriter | Content Writing | Marketing copy, brand voice, storytelling |
| Web Designer | Web Design | UI/UX design, landing pages, web experiences |
| UX Researcher | User Research | User testing, journey mapping, usability analysis |
| 3D Specialist | 3D Design | 3D modeling, product visualization, immersive content |

### Growth & Marketing Layer (7 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Marketing Specialist | Marketing | Campaign strategy, channel planning, performance marketing |
| Growth Hacker | Growth | Viral loops, A/B testing, conversion optimization |
| SEO Specialist | SEO | Search optimization, keyword strategy, technical SEO |
| Social Media Manager | Social Media | Platform strategy, community management, content scheduling |
| Email Marketing Specialist | Email | Drip campaigns, newsletters, segmentation |
| Sales Representative | Sales | Lead qualification, outreach, deal management |
| PR Manager | Public Relations | Media relations, press releases, crisis communications |

### Operations Layer (6 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Operations Manager | Operations | Process optimization, resource allocation, efficiency |
| Inventory Manager | Inventory | Stock management, supply chain, demand forecasting |
| Procurement Manager | Procurement | Vendor management, cost negotiation, sourcing |
| HR Specialist | Human Resources | Recruitment, onboarding, culture, policy |
| Customer Service Agent | Support | Ticket resolution, FAQ management, customer satisfaction |
| CX Architect | Customer Experience | Journey optimization, NPS improvement, experience design |

### Finance Layer (2 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Financial Analyst | Finance | Financial modeling, forecasting, budgeting |
| Data Analyst | Analytics | Business intelligence, dashboards, trend analysis |

### Governance Layer (3 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Legal Assistant | Legal | Contract review, compliance, regulatory guidance |
| Compliance Officer | Compliance | Regulatory adherence, audit preparation, risk assessment |
| Ethics Officer | Ethics | Ethical AI governance, bias detection, responsible practices |

### Intelligence Layer (4 agents)
| Agent | Role | Specialization |
|-------|------|----------------|
| Research Specialist | Research | Deep research, competitive analysis, academic papers |
| Knowledge Architect | Knowledge Management | Knowledge base curation, taxonomy, information architecture |
| Localization Specialist | Localization | Translation, cultural adaptation, market-specific content |
| Personal Secretary | Executive Assistant | Scheduling, email drafting, real-world action execution |

---

## 3. CORE SYSTEMS & FEATURES

### 3.1 Autonomous Orchestration Engine
**How it works:** User provides a high-level business goal → Commander agent scores it for clarity/complexity → Creates a strategic plan with milestones and tasks → Assigns tasks to specialist agents → Executes autonomously → Quality reviews each result → Creates cross-domain collaborations → Hands off to Personal Secretary for real-world actions.

**Key capabilities:**
- Goal scoring (clarity, complexity, risk, confidence)
- Strategic plan generation with milestones
- Automatic agent assignment based on task type
- Parallel milestone execution
- Media generation (images via GPT Image 1, videos via Sora 2)
- Commander → Personal Secretary handoff

### 3.2 Custom Brain Profiles
Every agent has a configurable brain profile controlling:
- **Primary LLM Model**: Which AI model to use (GPT-5.2, Claude Sonnet, Gemini, etc.)
- **Autonomy Level**: 1-10 scale (1 = always ask permission, 10 = fully autonomous)
- **Communication Style**: Professional, casual, technical, creative
- **Tools**: Which integrations and capabilities the agent can use
- **Creativity Temperature**: 0.0-1.0 (deterministic to highly creative)
- **Max Tokens**: Response length limit
- **Context Window**: How much history to consider

### 3.3 Quality Control & Failure Recovery (NEW)
**Critic Module**: After every task completion, an automated quality review runs using GPT-4o as the critic. It scores output 1-10 on completeness, accuracy, actionability, and professionalism.

**Retry/Fallback Chain**: When an LLM call fails, the system automatically retries with:
1. GPT-5.2 → 2. Claude Sonnet 4.5 → 3. Gemini 2.5 Pro → 4. GPT-4o

**Escalation**: If all retries fail, the task is escalated to the user with a notification.

**Quality Dashboard API** (`GET /api/quality/dashboard`):
- Total reviews, pass/fail/revision counts
- Average quality score
- Pass rate percentage
- Escalated and recovered task counts

### 3.4 Model-Agnostic LLM Router (NEW)
Intelligent routing system that selects the optimal LLM model based on task characteristics:

| Tier | Models | Use Case | Cost |
|------|--------|----------|------|
| Premium | GPT-5.2, Claude Sonnet 4.5, Gemini 2.5 Pro | Complex coding, reasoning, legal, long-form | High |
| Standard | GPT-4o, GPT-4.1, Gemini 3 Flash | Moderate data analysis, coding, creative | Medium |
| Economy | GPT-4o-mini, Gemini 2.5 Flash, Claude Haiku | Simple queries, translations, quick answers | Low |

**Task Classification** analyzes content for coding, reasoning, creative, data, legal, and quick signals, combined with the agent's role, to determine complexity tier and optimal model.

**Router Stats API** (`GET /api/router/stats`): Model usage distribution, complexity distribution, task type distribution, total credits used.

### 3.5 Autonomous Collaboration Engine (ENHANCED)
**Auto-detection**: When a task is completed by an agent, the system automatically detects if the work impacts agents in related domains and creates collaboration entries.

**Domain Mapping**: All 41 agents are mapped to 9 domains: executive, product, technical, creative, marketing, operations, finance, governance, intelligence.

**Cross-Domain Triggers**:
- Marketing tasks trigger Creative + Technical collaborations
- Technical tasks trigger Product + Operations collaborations
- Product tasks trigger Technical + Creative + Marketing collaborations
- Executive tasks trigger Finance + Product + Marketing collaborations

**Collaboration Types**: information_sharing, review_request, data_handoff, coordination

### 3.6 Content Generator (NEW)
Generate on-brand content using Style Blueprints extracted from Reference Intelligence.

**8 Content Types**:
1. Marketing Copy — Landing pages, product descriptions
2. Social Media Post — LinkedIn, Twitter, Instagram
3. Email Campaign — Newsletters, drip campaigns
4. Blog Article — Thought leadership, tutorials
5. Ad Copy — Google Ads, Meta Ads
6. Press Release — Company announcements
7. Brand Guidelines — Voice & tone docs
8. Custom — Freeform content

**Features**:
- Select a Style Blueprint from Reference Intelligence to match tone/style
- Adjustable content length (short/medium/long)
- Optional tone override
- Full generation history with copy/delete functionality
- Uses user's preferred LLM model

### 3.7 Universal Reference Intelligence
Analyzes text and images to extract "Style Blueprints":
- **Text Analysis**: Writing style, target audience, messaging patterns, brand voice, structure
- **Image Analysis**: Brand detection, visual style (colors, typography, composition), emotional tone, design patterns

Style Blueprints can be used by the Content Generator to produce on-brand content.

### 3.8 Vibe Coding App Builder
Chat-based full-stack app generation:
- Describe your app → AI generates complete HTML/CSS/JS
- Live preview in iframe
- Iterative modifications via chat
- Code view with syntax highlighting
- File download capability
- Uses user's preferred LLM model

### 3.9 Agent Activity Monitor
Real-time dashboard showing:
- **Agent Workforce Status**: Active agents with task counts and completion progress
- **Inter-Agent Communication Flows**: Sender → Receiver collaboration visualization
- **Task Dependency Graph**: Task status tracking (pending, in_progress, completed, failed)
- **Recent Tool Executions**: Latest tool calls with timing and results
- Live/paused toggle with auto-refresh

### 3.10 Real-World Action Layer
Enables agents to execute real-world actions:
- **Google Suite Integration**: Gmail (send emails) + Calendar (create events) via OAuth 2.0
- **Simulation Mode**: All actions gated by system-wide simulation/execution toggle
- **Integrations Management**: Connect/disconnect in Settings page

### 3.11 Flexible LLM Configuration
User-configurable AI model selection:
- **OpenAI**: gpt-5.2, gpt-5.1, gpt-4.1, gpt-4o, o3, o4-mini
- **Anthropic**: Claude Sonnet 4.5, Claude 4 Sonnet, Claude Haiku 4.5
- **Google Gemini**: Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash

Accessible in Settings → AI Model Configuration. Applies to all AI features (Content Generator, Vibe Coding, Reference Intelligence).

### 3.12 KPI Command Center
Track key performance indicators with:
- Custom KPI creation (name, value, target, trend)
- Visual dashboard with progress bars and sparklines
- Data source tracking
- Collaboration log integration

### 3.13 Simulation vs Execution Mode
System-wide toggle controlling real-world action execution:
- **Simulation Mode** (default): All actions return simulated responses. Safe for testing.
- **Execution Mode**: Actions execute for real (send actual emails, create real calendar events).

---

## 4. FRONTEND PAGES & NAVIGATION

| Page | Route | Description |
|------|-------|-------------|
| Landing | `/` | Agent showcase, hero section, pricing |
| Dashboard | `/dashboard` | Central command with project overview |
| Projects | `/projects` | Project list + detail view with media rendering |
| Chat | `/chat/:agentId` | Direct agent conversation |
| Agents | `/agents` | All 41 agents grid |
| Workspace Brain | `/workspace-brain` | Agent workspace configuration |
| Brain Profiles | `/brain-profiles` | Custom brain profile management |
| Collaborations | `/collaborations` | Inter-agent collaboration logs |
| KPI Dashboard | `/kpi-dashboard` | Key performance indicators |
| Activity Monitor | `/activity-monitor` | Real-time agent activity |
| Vibe Coding | `/vibe-coding` | Chat-based app builder |
| Reference Intel | `/reference-intelligence` | Style blueprint extraction |
| Content Generator | `/content-generator` | On-brand content creation |
| Approvals | `/approvals` | Task approval workflows |
| Tasks | `/tasks` | Task management |
| Team | `/team` | Team management |
| Products | `/products` | Product catalog |
| Insights | `/insights` | Analytics & insights |
| Settings | `/settings` | Profile, LLM config, integrations |
| Admin | `/admin` | Admin dashboard |
| Login/Register | `/login`, `/register` | Authentication |

---

## 5. KEY API ENDPOINTS

### Authentication
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login, returns JWT token

### Agents
- `GET /api/agents/public` — List all 41 agents
- `GET /api/agents/:id` — Get agent detail
- `PUT /api/agents/:id/brain` — Update brain profile
- `GET /api/brain-profiles` — All brain profiles

### Projects
- `POST /api/projects` — Create project from goal
- `GET /api/projects` — List projects
- `GET /api/projects/:id` — Project detail with milestones/tasks

### Enterprise
- `POST /api/collaborations` — Create collaboration
- `GET /api/collaborations` — List collaborations
- `GET /api/kpis` — KPI dashboard data
- `POST /api/kpis/custom` — Create custom KPI
- `PUT /api/system/mode` — Toggle simulation/execution
- `GET /api/cost-governance` — Cost tracking
- `GET /api/quality/dashboard` — Quality metrics
- `POST /api/quality/review` — Trigger critic review
- `POST /api/quality/retry` — Retry failed task
- `GET /api/router/stats` — LLM routing statistics
- `POST /api/router/analyze` — Analyze task routing (dry run)

### Activity Monitor
- `GET /api/activity/live` — Real-time agent activity

### Reference Intelligence
- `POST /api/reference/analyze` — Analyze text/image reference
- `GET /api/reference/history` — Analysis history

### Content Generator
- `GET /api/content/types` — 8 content types
- `POST /api/content/generate` — Generate content with optional blueprint
- `GET /api/content/history` — Generated content history
- `DELETE /api/content/:id` — Delete content

### Vibe Coding
- `POST /api/vibe/projects` — Create app from prompt
- `GET /api/vibe/projects` — List projects
- `POST /api/vibe/projects/:id/chat` — Chat modifications
- `GET /api/vibe/projects/:id/preview` — HTML preview

### LLM Configuration
- `GET /api/llm/config` — Get provider/model preference
- `PUT /api/llm/config` — Set provider/model preference

### Actions
- `GET /api/actions/integrations` — List integrations
- `POST /api/actions/send-email` — Send email (simulation/execution)
- `POST /api/actions/create-event` — Create calendar event
- `GET /api/oauth/gmail/status` — Google OAuth status
- `GET /api/oauth/gmail/login` — Initiate OAuth flow

---

## 6. DATABASE COLLECTIONS

| Collection | Purpose |
|------------|---------|
| users | User accounts, profiles |
| agents | 41 agent definitions |
| agent_brains | Custom brain profiles per user per agent |
| projects | Autonomous projects with milestones |
| tasks | Individual task assignments and results |
| chats | Agent conversation history |
| collaborations | Inter-agent collaboration logs |
| kpi_store | Key performance indicators |
| quality_reviews | Quality control review records |
| system_config | User preferences (LLM config, system mode) |
| vibe_projects | Vibe Coding app projects |
| reference_analyses | Reference Intelligence analyses |
| generated_content | Content Generator output |
| routing_logs | LLM router decision logs |
| google_tokens | Google OAuth tokens |
| tool_logs | Agent tool execution logs |
| tool_calls | Detailed tool call records |
| notifications | User notification queue |
| subscriptions | Credit-based billing |
| payment_transactions | Stripe payment records |
| products | Product catalog |
| teams | Team management |
| workspace_brain | Workspace configurations |
| approvals | Task approval workflows |
| knowledge_docs | RAG knowledge base |
| usage_logs | LLM usage tracking |
| audit_log | System audit trail |
| platform_config | Admin pricing/config |

---

## 7. TESTING STATUS

| Iteration | Tests | Pass Rate | Features Tested |
|-----------|-------|-----------|-----------------|
| 53 | 26/26 | 100% | KPI, Collaboration, Agent Expansion, Brain Profiles |
| 54 | 20/20 | 100% | Activity Monitor, Vibe Coding, Reference Intel, LLM Config |
| 55 | 27/27 | 100% | Quality Control, LLM Router, Content Generator, Autonomous Collaboration |

**Total**: 73 tests across 3 iterations, 100% pass rate.

---

## 8. CREDENTIALS

- **Admin**: management.maars@marsgc.net / admin123
- **LLM Provider**: Emergent LLM Key (universal key for OpenAI, Anthropic, Gemini)
- **Payments**: Stripe test key (pre-configured)

---

## 9. FUTURE ROADMAP

### P1 — High Priority
- Memory Governance (versioning, pruning, relevance scoring)
- WebSocket real-time updates for Activity Monitor

### P2 — Medium Priority
- Enterprise RBAC with granular permissions UI
- Advanced integrations (WhatsApp, Meta Ads, Shopify, ERP)
- Cost Governance active monitoring by AI Optimizer
- Custom agent creation by users

### P3 — Future
- Multi-tenant isolation
- Enterprise org chart visualization
- Workflow builder UI
- Architecture diagram generation
- Mobile app wrapper
