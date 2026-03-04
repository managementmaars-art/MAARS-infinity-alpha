"""Summary PDF generation endpoint."""
import io
import logging
from datetime import datetime, timezone
from fpdf import FPDF
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from auth import get_current_user, User
from db import db

logger = logging.getLogger(__name__)
router = APIRouter()

AGENT_LAYERS = [
    ("Executive Layer", [
        ("Commander Orion", "Commander", "Strategic planning, goal decomposition, workforce orchestration"),
        ("Chief Strategy Officer", "Strategist", "Long-term strategy, market analysis, competitive intelligence"),
        ("Revenue Strategist", "Revenue", "Revenue optimization, pricing strategy, monetization modeling"),
        ("Investor Relations", "Investor Relations", "Investor communications, fundraising, financial reporting"),
        ("Business Strategist", "Business Strategy", "Market positioning, business model innovation, go-to-market"),
    ]),
    ("Product & Technical Layer", [
        ("Product Manager", "PM", "Product roadmaps, feature prioritization, user stories"),
        ("Project Manager", "Project Management", "Timeline management, resource allocation, milestone tracking"),
        ("App Developer", "Developer", "Full-stack development, code generation, API design"),
        ("Automation Engineer", "Automation", "Workflow automation, CI/CD pipelines, process optimization"),
        ("AI Optimizer", "AI Specialist", "ML model tuning, AI performance, cost optimization"),
        ("Data Engineer", "Data Engineering", "Data pipelines, ETL, database architecture"),
        ("Cybersecurity Officer", "Security", "Security audits, vulnerability assessments, compliance"),
    ]),
    ("Creative & Brand Layer", [
        ("Brand Architect", "Brand Strategy", "Brand identity, positioning, visual language systems"),
        ("Graphics Designer", "Visual Design", "Image creation, visual assets, marketing materials"),
        ("Video Specialist", "Video Production", "Video content, animation, motion graphics"),
        ("Copywriter", "Content Writing", "Marketing copy, brand voice, storytelling"),
        ("Web Designer", "Web Design", "UI/UX, landing pages, responsive layouts"),
        ("UX Researcher", "User Research", "User testing, journey mapping, usability analysis"),
        ("3D Specialist", "3D Design", "3D modeling, product visualization, immersive content"),
    ]),
    ("Growth & Marketing Layer", [
        ("Marketing Specialist", "Marketing", "Campaign strategy, performance marketing, analytics"),
        ("Growth Hacker", "Growth", "Viral loops, A/B testing, conversion optimization"),
        ("SEO Specialist", "SEO", "Search optimization, keyword strategy, technical SEO"),
        ("Social Media Manager", "Social Media", "Platform strategy, community management, engagement"),
        ("Email Marketing", "Email", "Drip campaigns, newsletters, segmentation"),
        ("Sales Representative", "Sales", "Lead qualification, outreach sequences, pipeline analysis"),
        ("PR Manager", "Public Relations", "Media relations, press releases, crisis communications"),
    ]),
    ("Operations Layer", [
        ("Operations Manager", "Operations", "Process optimization, resource allocation, efficiency"),
        ("Inventory Manager", "Inventory", "Stock management, supply chain optimization"),
        ("Procurement Manager", "Procurement", "Vendor management, cost negotiation, sourcing"),
        ("HR Specialist", "HR", "Recruitment, onboarding, culture development"),
        ("Customer Service Agent", "Support", "Ticket resolution, FAQ management, satisfaction"),
        ("CX Architect", "Customer Experience", "Journey optimization, NPS improvement, loyalty"),
    ]),
    ("Finance Layer", [
        ("Financial Analyst", "Finance", "Financial modeling, forecasting, budgeting"),
        ("Data Analyst", "Analytics", "Business intelligence, dashboards, trend analysis"),
    ]),
    ("Governance Layer", [
        ("Legal Assistant", "Legal", "Contract review, legal research, compliance checks"),
        ("Compliance Officer", "Compliance", "Regulatory adherence, audit preparation"),
        ("Ethics Officer", "Ethics", "Ethical AI governance, bias detection"),
    ]),
    ("Intelligence Layer", [
        ("Research Specialist", "Research", "Deep research, competitive analysis, trend forecasting"),
        ("Knowledge Architect", "Knowledge Management", "Knowledge base curation, taxonomy design"),
        ("Localization Specialist", "Localization", "Translation, cultural adaptation, market content"),
        ("Personal Secretary", "Executive Assistant", "Scheduling, email drafting, real-world action bridge"),
    ]),
]

CORE_SYSTEMS = [
    ("Autonomous Orchestration Engine",
     "When you set a business goal, Commander Orion scores it, creates a strategic plan with milestones and tasks, assigns them to specialist agents, and executes with quality control and failure recovery."),
    ("Custom Brain Profiles",
     "Every agent has a configurable brain: LLM model selection, autonomy level (1-10), communication style, tool permissions, creativity temperature, and context window."),
    ("Quality Control & Failure Recovery",
     "After every task, a Critic Module (GPT-4o) auto-reviews output on a 1-10 scale. Failed tasks retry with fallback models: GPT-5.2 -> Claude Sonnet -> Gemini Pro -> GPT-4o."),
    ("Model-Agnostic LLM Router",
     "Analyzes task complexity and auto-selects the optimal LLM. Premium tier for complex tasks, Economy tier for simple queries. User can override in Settings."),
    ("Autonomous Collaboration Engine",
     "Auto-detects cross-domain dependencies when agents complete tasks. 41 agents mapped to 9 domains with trigger rules for seamless coordination."),
    ("Universal Reference Intelligence",
     "Analyzes text and image references to extract Style Blueprints capturing writing style, tone, audience, color palettes, and design patterns."),
    ("Content Generator",
     "Generates on-brand content using Style Blueprints. 8 content types with length control, tone override, and full history."),
    ("Vibe Coding App Builder",
     "Chat-based full-stack app generation. Generates complete HTML/CSS/JS with Tailwind, live preview, iterative modifications, and download."),
    ("Agent Activity Monitor (WebSocket)",
     "Real-time dashboard with live WebSocket streaming (8s updates), fallback REST polling. Shows agent status, communication flows, task graphs, and tool executions."),
    ("Simulation vs. Execution Mode",
     "System-wide toggle controlling real-world actions. Simulation mode returns safe responses; Execution mode triggers real Gmail, Calendar, and API calls."),
    ("Real-World Action Layer",
     "Google Suite integration (Gmail + Calendar) via OAuth 2.0. Actions gated by Simulation/Execution mode. Personal Secretary as execution bridge."),
    ("Flexible LLM Configuration",
     "Users choose their preferred AI model from Settings. Supports OpenAI (GPT-5.2, GPT-4.1, o3), Anthropic (Claude Sonnet 4.5), Google (Gemini 3 Flash, 2.5 Pro)."),
    ("Voice Command Interface",
     "Microphone button in the Command Palette. Records audio via browser MediaRecorder, transcribes via OpenAI Whisper, and auto-fills search for hands-free navigation."),
    ("Admin Code Explorer",
     "Full codebase browser with recursive file tree, code viewer with line numbers and language detection, file search, copy, and ZIP download of entire codebase."),
    ("Memory Governance",
     "Full memory management: CRUD, version history, time-decay relevance scoring (30-day half-life), auto-pruning with dry-run, usage statistics and category breakdown."),
    ("Agent Memory Auto-Learning",
     "When agents complete tasks, the system uses GPT-4o-mini to extract 1-3 key learnings (facts, decisions, preferences) and stores them as memory entries. Near-duplicate detection prevents spam."),
    ("Command Palette",
     "VS Code-style quick search (press / or Cmd+K). Search across 20+ pages, 41 agents, and quick actions. Keyboard navigation, recent searches, voice command integration."),
]


class SummaryPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, "MAARS Command", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Autonomous AI Enterprise Operating System", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, "by MAARS Global Corporation", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"MAARS Command Summary | Generated {datetime.now(timezone.utc).strftime('%B %d, %Y')} | Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(79, 70, 229)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(3)

    def subsection(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        safe = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2192", "->")
        self.multi_cell(0, 4.5, safe)
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        safe = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2192", "->")
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, "  - " + safe)


@router.get("/summary/pdf")
async def download_summary_pdf(current_user: User = Depends(get_current_user)):
    """Generate and download a comprehensive PDF summary of MAARS Command."""

    # Fetch live stats
    total_agents = await db.agents.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    total_projects = await db.projects.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_memories = await db.memory_entries.count_documents({"user_id": current_user.user_id})
    auto_learned = await db.memory_entries.count_documents({"user_id": current_user.user_id, "source": "auto_learn"})

    pdf = SummaryPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Overview ---
    pdf.section_title("Platform Overview")
    pdf.body_text(
        "MAARS Command is an Autonomous AI Enterprise Operating System that deploys a workforce of "
        f"{total_agents} specialized AI agents organized across 8 organizational layers. It merges the power of "
        "preset specialist business agents with autonomous execution, persistent memory, and real-world action "
        "capabilities. Users set high-level business goals, and the AI workforce autonomously plans, delegates, "
        "executes, collaborates, and delivers - with quality control, failure recovery, and human oversight at every step."
    )

    # --- Live Stats ---
    pdf.section_title("Platform Statistics")
    stats = [
        f"AI Agents: {total_agents}",
        f"Organizational Layers: 8",
        f"Core Systems: {len(CORE_SYSTEMS)}",
        f"LLM Providers: 3 (OpenAI, Anthropic, Google Gemini)",
        f"Total Projects Created: {total_projects}",
        f"Total Tasks Executed: {total_tasks}",
        f"Total Chat Conversations: {total_chats}",
        f"Memory Entries: {total_memories} ({auto_learned} auto-learned)",
    ]
    for s in stats:
        pdf.bullet(s)

    # --- Agent Workforce ---
    pdf.section_title(f"The {total_agents}-Agent AI Workforce")
    pdf.body_text(
        "Each agent has a unique Custom Brain Profile defining its LLM model, tools, autonomy level, "
        "and communication style. Agents are organized into 8 specialized layers:"
    )
    for layer_name, agents in AGENT_LAYERS:
        pdf.ln(1)
        pdf.subsection(f"{layer_name} ({len(agents)} agents)")
        for name, role, desc in agents:
            pdf.bullet(f"{name} [{role}] - {desc}")

    # --- Core Systems ---
    pdf.add_page()
    pdf.section_title(f"Core Systems & Capabilities ({len(CORE_SYSTEMS)} systems)")
    for title, desc in CORE_SYSTEMS:
        pdf.ln(1)
        pdf.subsection(title)
        pdf.body_text(desc)

    # --- Technical Architecture ---
    pdf.section_title("Technical Architecture")
    pdf.subsection("Backend")
    for item in ["FastAPI (Python) with async/await", "MongoDB database with 27+ collections", "50+ API endpoints with JWT authentication", "WebSocket support for real-time streaming", "Emergent Integrations SDK for LLM access"]:
        pdf.bullet(item)
    pdf.ln(2)
    pdf.subsection("Frontend")
    for item in ["React 18 with Tailwind CSS", "Shadcn/UI component library", "20+ pages with responsive dashboard layout", "Collapsible sidebar navigation (DashboardLayout)", "Command Palette with voice commands"]:
        pdf.bullet(item)
    pdf.ln(2)
    pdf.subsection("AI Layer")
    for item in ["OpenAI: GPT-5.2, GPT-4.1, GPT-4o, o3, o4-mini", "Anthropic: Claude Sonnet 4.5, Claude 4 Sonnet, Claude Haiku 4.5", "Google: Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash", "Universal Emergent LLM Key (single key across all providers)", "Smart model routing with cost optimization", "OpenAI Whisper for voice transcription", "GPT Image 1 for image generation, Sora 2 for video"]:
        pdf.bullet(item)

    # --- Key API Endpoints ---
    pdf.section_title("Key API Endpoints")
    endpoints = [
        ("POST /api/auth/login", "User authentication"),
        ("GET /api/agents/public", "List all 41 agents"),
        ("POST /api/agents/{id}/chat", "Chat with a specific agent"),
        ("POST /api/projects", "Create autonomous project"),
        ("POST /api/enterprise/router/route-task", "LLM model routing"),
        ("GET /api/enterprise/activity/live", "Live activity feed"),
        ("WS /api/ws/activity", "WebSocket real-time activity"),
        ("POST /api/voice/transcribe", "Voice transcription (Whisper)"),
        ("GET /api/admin/code/tree", "Code explorer file tree"),
        ("GET /api/admin/code/export", "Download codebase as ZIP"),
        ("GET /api/memory/entries", "Memory governance CRUD"),
        ("POST /api/memory/prune", "Auto-prune low-relevance memories"),
        ("POST /api/content/generate", "Content generation"),
        ("POST /api/reference/analyze", "Reference intelligence analysis"),
        ("POST /api/vibe/generate", "Vibe coding app builder"),
    ]
    for ep, desc in endpoints:
        pdf.bullet(f"{ep} - {desc}")

    # --- Footer ---
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "MAARS Global Corporation - Confidential", align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=MAARS-Command-Summary.pdf"},
    )
