"""Summary PDF generation endpoint — comprehensive, aesthetic PDF."""
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
     "After every task, a Critic Module (GPT-4o) auto-reviews output on a 1-10 scale. Failed tasks retry with fallback models: GPT-5.2 -> Claude -> Gemini -> GPT-4o."),
    ("Model-Agnostic LLM Router",
     "Analyzes task complexity and auto-selects the optimal LLM. Premium tier for complex tasks, Economy tier for simple queries. User can override in Settings."),
    ("Autonomous Collaboration Engine",
     "Auto-detects cross-domain dependencies when agents complete tasks. 41 agents mapped to 9 domains with trigger rules for seamless coordination."),
    ("Universal Reference Intelligence",
     "Analyzes text and image references to extract Style Blueprints capturing writing style, tone, audience, color palettes, and design patterns."),
    ("Content Generator",
     "Generates on-brand content using Style Blueprints. 8 content types with length control, tone override, and full history."),
    ("Vibe Coding App Builder",
     "Chat-based full-stack app generation. Generates HTML/CSS/JS with Tailwind, live preview, iterative modifications, and download."),
    ("Agent Activity Monitor (WebSocket)",
     "Real-time dashboard with live WebSocket streaming (8s updates), fallback REST polling. Shows agent status, communication flows, task graphs, and tool executions."),
    ("Simulation vs. Execution Mode",
     "System-wide toggle controlling real-world actions. Simulation mode returns safe responses; Execution mode triggers real Gmail, Calendar, and API calls."),
    ("Real-World Action Layer",
     "Google Suite integration (Gmail + Calendar) via OAuth 2.0. Actions gated by Simulation/Execution mode. Personal Secretary as execution bridge."),
    ("Flexible LLM Configuration",
     "Users choose their preferred AI model from Settings. Supports 9 providers: OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs."),
    ("Voice Command Interface",
     "Microphone button in Command Palette. Records audio via MediaRecorder, transcribes via OpenAI Whisper, auto-fills search for hands-free navigation."),
    ("Admin Code Explorer",
     "Full codebase browser with recursive file tree, code viewer with line numbers and language detection, file search, copy, and ZIP download."),
    ("Memory Governance",
     "Full memory management: CRUD, version history, time-decay relevance scoring (30-day half-life), auto-pruning with dry-run, usage statistics."),
    ("Agent Memory Auto-Learning",
     "Uses GPT-4o-mini to extract 1-3 key learnings from completed tasks. Creates memory entries automatically with near-duplicate detection."),
    ("Command Palette",
     "VS Code-style quick search (press / or Cmd+K). Search across 20+ pages, 41 agents, and quick actions. Keyboard navigation, voice integration."),
]

AI_PROVIDERS = [
    ("OpenAI", [
        ("GPT-5.2", "Flagship", "Most capable for coding, analysis & complex tasks"),
        ("GPT-4o", "Fast", "Balanced speed and quality"),
        ("GPT-4o Mini", "Economy", "Cost-efficient for quick answers"),
        ("O3", "Reasoning", "Advanced reasoning for math & logic"),
        ("O3 Mini", "Reasoning", "Lightweight analytical tasks"),
    ]),
    ("Anthropic", [
        ("Claude Sonnet 4.5", "Flagship", "Creative writing, analysis & nuanced tasks"),
        ("Claude Opus 4.5", "Premium", "Deep research & complex analysis"),
        ("Claude Haiku 4.5", "Economy", "Fast responses & summaries"),
    ]),
    ("Google", [
        ("Gemini 3 Flash", "Fast", "Lightning-fast responses"),
        ("Gemini 3 Pro", "Flagship", "Multimodal research & analysis"),
    ]),
    ("xAI (Grok)", [
        ("Grok 3", "Flagship", "1M context, reasoning & analysis"),
        ("Grok 3 Mini", "Economy", "Cost-efficient reasoning"),
        ("Grok 2", "Fast", "Competitive with GPT-4o"),
    ]),
    ("DeepSeek", [
        ("DeepSeek Chat", "Economy", "128K context, ultra-affordable"),
        ("DeepSeek Reasoner", "Reasoning", "Deep math & logic reasoning"),
    ]),
    ("Mistral AI", [
        ("Mistral Large", "Flagship", "Complex reasoning, enterprise-grade"),
        ("Mistral Medium", "Fast", "Balanced performance"),
        ("Mistral Small", "Economy", "Ultra-fast, simple tasks"),
    ]),
    ("Perplexity", [
        ("Sonar", "Search", "Web-grounded real-time answers"),
        ("Sonar Pro", "Research", "Deep web research with citations"),
    ]),
    ("Cohere", [
        ("Command R+", "Flagship", "RAG & enterprise tasks"),
        ("Command R", "Economy", "Cost-efficient summaries"),
    ]),
    ("AI Generation + Voice", [
        ("Nano Banana 2", "Image Gen", "Gemini 3.1 Flash image generation"),
        ("GPT Image 1", "Image Gen", "Generate images from text"),
        ("DALL-E 3", "Image Gen", "Creative image generation"),
        ("Sora 2", "Video Gen", "AI video from text prompts"),
        ("ElevenLabs", "Voice", "Multilingual TTS"),
        ("Whisper", "STT", "Speech-to-text in 50+ languages"),
    ]),
]

COST_TABLE = [
    ("OpenAI (per 1M tokens / per img or sec)", [
        ("GPT-5.2", "$2.50", "$10.00"), ("GPT-4o", "$2.50", "$10.00"), ("GPT-4o Mini", "$0.15", "$0.60"),
        ("O3", "$10.00", "$40.00"), ("O3 Mini", "$1.10", "$4.40"),
        ("GPT Image 1", "$0.02/img", "1024x1024"), ("Sora 2", "$0.10/sec", "4-12 sec video"),
    ]),
    ("Anthropic (per 1M tokens)", [
        ("Claude Sonnet 4.5", "$3.00", "$15.00"), ("Claude Opus 4.5", "$15.00", "$75.00"), ("Claude Haiku 4.5", "$0.80", "$4.00"),
    ]),
    ("Gemini (per 1M tokens)", [
        ("Gemini 3 Flash", "$0.075", "$0.30"), ("Gemini 3 Pro", "$1.25", "$5.00"), ("Nano Banana 2", "$0.02/img", "1024x1024"),
    ]),
    ("xAI (per 1M tokens)", [
        ("Grok 3", "$3.00", "$15.00"), ("Grok 3 Mini", "$0.30", "$0.50"), ("Grok 2", "$2.00", "$10.00"),
    ]),
    ("DeepSeek (per 1M tokens)", [
        ("DeepSeek Chat", "$0.14", "$0.28"), ("DeepSeek Reasoner", "$0.55", "$2.19"),
    ]),
    ("Mistral (per 1M tokens)", [
        ("Mistral Large", "$2.00", "$6.00"), ("Mistral Medium", "$0.40", "$2.00"), ("Mistral Small", "$0.10", "$0.30"),
    ]),
    ("Perplexity (per 1M tokens + $5/1K search)", [
        ("Sonar", "$1.00", "$1.00"), ("Sonar Pro", "$3.00", "$15.00"),
    ]),
    ("Cohere (per 1M tokens)", [
        ("Command R+", "$2.50", "$10.00"), ("Command R", "$0.15", "$0.60"),
    ]),
    ("ElevenLabs (per 1K chars)", [
        ("Multilingual v2", "$0.30/1K", "TTS audio"), ("Turbo v2.5", "$0.18/1K", "Fast TTS"),
    ]),
]


def _safe(text):
    """Sanitize text for Helvetica font."""
    return (text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'")
            .replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2192", "->").replace("\u2026", "..."))


class SummaryPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            # Title page header
            self.ln(8)
            self.set_font("Helvetica", "B", 28)
            self.set_text_color(220, 220, 220)
            self.cell(0, 12, "MAARS Command", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 11)
            self.set_text_color(160, 160, 160)
            self.cell(0, 7, "Autonomous AI Enterprise Operating System", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, "by MAARS Global Corporation", align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(3)
            self.set_draw_color(79, 70, 229)
            self.set_line_width(0.5)
            self.line(self.w * 0.3, self.get_y(), self.w * 0.7, self.get_y())
            self.set_line_width(0.2)
            self.ln(6)
        else:
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, "MAARS Command - System Summary", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}  |  Generated {datetime.now(timezone.utc).strftime('%B %d, %Y')}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(79, 70, 229)
        self.cell(0, 8, _safe(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(79, 70, 229)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.l_margin + 50, self.get_y())
        self.set_line_width(0.2)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def subsection(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.cell(0, 6, _safe(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, _safe(text))
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, _safe("  - " + text))

    def stat_row(self, label, value):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(70, 5, _safe(label))
        self.set_font("Helvetica", "", 9)
        self.set_text_color(79, 70, 229)
        self.cell(0, 5, _safe(str(value)), new_x="LMARGIN", new_y="NEXT")

    def cost_row(self, name, inp, out):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(80, 80, 80)
        self.set_x(self.l_margin + 4)
        self.cell(55, 4.5, _safe(name))
        self.set_text_color(34, 139, 34)
        self.cell(30, 4.5, _safe(f"In: {inp}"))
        self.set_text_color(200, 150, 0)
        self.cell(0, 4.5, _safe(f"Out: {out}"), new_x="LMARGIN", new_y="NEXT")


@router.get("/summary/pdf")
async def download_summary_pdf(current_user: User = Depends(get_current_user)):
    """Generate comprehensive PDF summary of MAARS Command."""

    total_agents = sum(len(agents) for _, agents in AGENT_LAYERS)
    total_tasks = await db.tasks.count_documents({})
    total_projects = await db.projects.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_memories = await db.memory_entries.count_documents({"user_id": current_user.user_id})
    auto_learned = await db.memory_entries.count_documents({"user_id": current_user.user_id, "source": "auto_learn"})
    total_models = sum(len(models) for _, models in AI_PROVIDERS)

    pdf = SummaryPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Platform Overview ---
    pdf.section_title("Platform Overview")
    pdf.body(
        f"MAARS Command is an Autonomous AI Enterprise Operating System that deploys {total_agents} "
        f"specialized AI agents organized across 8 organizational layers. It merges preset specialist "
        f"business agents with autonomous execution, persistent memory, and real-world action capabilities. "
        f"The platform supports {total_models}+ AI models from 9 providers."
    )

    # --- Statistics ---
    pdf.section_title("Platform Statistics")
    for label, value in [
        ("AI Agents", total_agents),
        ("Organizational Layers", 8),
        ("Core Systems", len(CORE_SYSTEMS)),
        ("AI Providers", len(AI_PROVIDERS)),
        ("AI Models Available", f"{total_models}+"),
        ("API Endpoints", "50+"),
        ("Total Projects", total_projects),
        ("Total Tasks Executed", total_tasks),
        ("Chat Conversations", total_chats),
        ("Memory Entries", f"{total_memories} ({auto_learned} auto-learned)"),
    ]:
        pdf.stat_row(label, value)

    # --- Agent Workforce ---
    pdf.section_title(f"The {total_agents}-Agent AI Workforce")
    pdf.body("Each agent has a Custom Brain Profile: LLM model, autonomy level (1-10), communication style, tool permissions, and creativity temperature.")
    for layer_name, agents in AGENT_LAYERS:
        pdf.ln(1)
        pdf.subsection(f"{layer_name} ({len(agents)} agents)")
        for name, role, desc in agents:
            pdf.bullet(f"{name} [{role}] - {desc}")

    # --- Core Systems ---
    pdf.add_page()
    pdf.section_title(f"Core Systems ({len(CORE_SYSTEMS)})")
    for i, (title, desc) in enumerate(CORE_SYSTEMS, 1):
        pdf.ln(1)
        pdf.subsection(f"{i}. {title}")
        pdf.body(desc)

    # --- AI Models & Providers ---
    pdf.add_page()
    pdf.section_title(f"AI Models & Providers ({len(AI_PROVIDERS)} providers, {total_models}+ models)")
    pdf.body("MAARS Command supports 9 AI providers with 30+ models for text, reasoning, search, image, video, voice, and speech-to-text.")
    for provider_name, models in AI_PROVIDERS:
        pdf.ln(1)
        pdf.subsection(f"{provider_name} ({len(models)} models)")
        for name, tier, desc in models:
            pdf.bullet(f"{name} [{tier}] - {desc}")

    # --- Provider Costs ---
    pdf.add_page()
    pdf.section_title("Direct Provider Costs")
    pdf.body("Reference pricing when using your own API keys. Prices from provider websites.")
    pdf.ln(1)
    # Table header
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(50, 50, 50)
    pdf.set_x(pdf.l_margin + 4)
    pdf.cell(55, 5, "Model")
    pdf.cell(30, 5, "Input Cost")
    pdf.cell(0, 5, "Output Cost", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)

    for provider_label, models in COST_TABLE:
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 5, _safe(provider_label), new_x="LMARGIN", new_y="NEXT")
        for name, inp, out in models:
            pdf.cost_row(name, inp, out)

    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 4, "* Emergent Universal Key includes a small markup for convenience and unified billing.", new_x="LMARGIN", new_y="NEXT")

    # --- Technical Architecture ---
    pdf.add_page()
    pdf.section_title("Technical Architecture")

    pdf.subsection("Backend")
    for item in ["FastAPI (Python) with async/await", "MongoDB database with 27+ collections", "50+ API endpoints with JWT authentication", "WebSocket support for real-time streaming", "Emergent Integrations SDK for LLM access", "Auto-learning memory pipeline"]:
        pdf.bullet(item)

    pdf.ln(2)
    pdf.subsection("Frontend")
    for item in ["React 18 with Tailwind CSS", "Shadcn/UI component library", "20+ pages with responsive dashboard layout", "Collapsible sidebar with admin sections", "Command Palette with voice commands", "PDF export for system summary"]:
        pdf.bullet(item)

    pdf.ln(2)
    pdf.subsection("AI Layer")
    for item in ["9 AI providers with 30+ models", "OpenAI: GPT-5.2, GPT-4o, O3, Whisper, GPT Image 1, Sora 2", "Anthropic: Claude Sonnet 4.5, Claude Opus 4.5, Haiku 4.5", "Google: Gemini 3 Flash, Gemini 3 Pro, Nano Banana 2", "xAI: Grok 3, Grok 3 Mini, Grok 2", "DeepSeek: Chat, Reasoner", "Mistral: Large, Medium, Small", "Perplexity: Sonar, Sonar Pro", "Cohere: Command R+, Command R", "Universal Emergent LLM Key across all providers", "Smart model routing with cost optimization"]:
        pdf.bullet(item)

    # --- Key API Endpoints ---
    pdf.ln(3)
    pdf.section_title("Key API Endpoints (15)")
    endpoints = [
        ("POST /api/auth/login", "User authentication"),
        ("GET /api/agents/public", "List all 41 agents"),
        ("POST /api/agents/{id}/chat", "Chat with specific agent"),
        ("POST /api/projects", "Create autonomous project"),
        ("POST /api/enterprise/router/route-task", "LLM model routing"),
        ("GET /api/enterprise/activity/live", "Live activity feed"),
        ("WS /api/ws/activity", "WebSocket real-time activity"),
        ("POST /api/voice/transcribe", "Voice transcription (Whisper)"),
        ("GET /api/admin/code/tree", "Code explorer file tree"),
        ("GET /api/admin/code/export", "Download codebase as ZIP"),
        ("GET /api/memory/entries", "Memory governance CRUD"),
        ("POST /api/memory/prune", "Auto-prune memories"),
        ("POST /api/content/generate", "Content generation"),
        ("POST /api/reference/analyze", "Reference intelligence"),
        ("GET /api/summary/pdf", "This PDF summary"),
    ]
    for ep, desc in endpoints:
        pdf.bullet(f"{ep}  --  {desc}")

    # --- Final Footer ---
    pdf.ln(8)
    pdf.set_draw_color(79, 70, 229)
    pdf.set_line_width(0.3)
    pdf.line(pdf.w * 0.3, pdf.get_y(), pdf.w * 0.7, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, _safe(f"Generated {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "MAARS Global Corporation - Confidential", align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=MAARS-Command-Summary.pdf"},
    )
