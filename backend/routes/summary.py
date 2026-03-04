"""MAARS Command — Premium dark-themed PDF documentation generator.

Matches the About page aesthetic: dark background, colored accents,
card-based stats, badge pills, and professional typography.
"""
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


def _s(t):
    return (str(t).replace("\u2013", "-").replace("\u2014", "--").replace("\u2018", "'")
            .replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2192", "->").replace("\u2026", "...").replace("\u2022", "-").replace("\u00a0", " "))


# === COLORS ===
BG = (13, 13, 15)          # Page background
CARD_BG = (24, 24, 28)     # Card background
BORDER = (40, 40, 48)      # Subtle borders
WHITE = (240, 240, 245)
LIGHT = (180, 180, 190)
DIM = (120, 120, 135)
MUTED = (80, 80, 95)
INDIGO = (99, 102, 241)    # Primary accent
VIOLET = (139, 92, 246)
EMERALD = (52, 211, 153)
AMBER = (251, 191, 36)
ROSE = (244, 63, 94)
CYAN = (34, 211, 238)
PINK = (236, 72, 153)
SKY = (56, 189, 248)
ORANGE = (251, 146, 60)
RED = (239, 68, 68)

BADGE_COLORS = [
    ((99, 102, 241), "Multi-Agent Orchestration"),
    ((52, 211, 153), "Quality Control"),
    ((251, 191, 36), "LLM Router"),
    ((236, 72, 153), "Content Generation"),
    ((34, 211, 238), "Vibe Coding"),
    ((139, 92, 246), "Memory Governance"),
    ((244, 63, 94), "Voice Commands"),
    ((56, 189, 248), "Code Explorer"),
]

STAT_CARDS = [
    ("41", "AI Agents", INDIGO),
    ("8", "Org Layers", AMBER),
    ("17", "Core Systems", EMERALD),
    ("9", "LLM Providers", VIOLET),
    ("212+", "API Endpoints", CYAN),
]


class DarkPDF(FPDF):
    """Dark-themed PDF matching the MAARS Command About page aesthetic."""

    def _fill_page(self):
        """Fill current page with dark background."""
        self.set_fill_color(*BG)
        self.rect(0, 0, self.w, self.h, style="F")

    def header(self):
        self._fill_page()
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*DIM)
        self.cell(0, 6, "MAARS Command  |  Comprehensive System Documentation", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_line_width(0.2)
        self.ln(4)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*MUTED)
        self.cell(self.w / 2 - self.l_margin, 6, f"MAARS Global Corporation  |  {datetime.now(timezone.utc).strftime('%B %d, %Y')}")
        self.cell(0, 6, f"Page {self.page_no()}/{{nb}}", align="R")

    # --- Drawing helpers ---

    def dark_card(self, x, y, w, h):
        self.set_fill_color(*CARD_BG)
        self.set_draw_color(*BORDER)
        self.rect(x, y, w, h, style="DF")

    def badge_pill(self, x, y, text, color):
        self.set_font("Helvetica", "B", 7)
        tw = self.get_string_width(text) + 8
        self.set_fill_color(*color)
        self.set_draw_color(*color)
        self.rect(x, y, tw, 5.5, style="F")
        self.set_text_color(255, 255, 255)
        self.set_xy(x, y + 0.3)
        self.cell(tw, 5, text, align="C")
        return tw

    def stat_card(self, x, y, w, h, number, label, color):
        self.dark_card(x, y, w, h)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*color)
        self.set_xy(x, y + 4)
        self.cell(w, 10, _s(str(number)), align="C")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*LIGHT)
        self.set_xy(x, y + 16)
        self.cell(w, 5, _s(label), align="C")

    # --- Text helpers ---

    def section_title(self, text):
        self.ln(5)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*INDIGO)
        self.set_x(self.l_margin)
        self.multi_cell(0, 7, _s(text))
        y = self.get_y()
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.6)
        self.line(self.l_margin, y, self.l_margin + 45, y)
        self.set_line_width(0.2)
        self.ln(3)

    def subsection(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*WHITE)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5.5, _s(text))
        self.ln(0.5)

    def sub3(self, text):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*LIGHT)
        self.set_x(self.l_margin + 2)
        self.multi_cell(0, 4.5, _s(text))

    def body(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*LIGHT)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, _s(text))
        self.ln(1)

    def bullet(self, text, color=None):
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*(color or LIGHT))
        self.set_x(self.l_margin + 3)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 3, 4.2, _s("  " + text))

    def dim_text(self, text):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*DIM)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4, _s(text))

    def kv_row(self, key, value, val_color=None):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*LIGHT)
        self.set_x(self.l_margin + 3)
        self.cell(58, 5, _s(key))
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*(val_color or INDIGO))
        self.cell(0, 5, _s(str(value)), new_x="LMARGIN", new_y="NEXT")

    def divider(self):
        self.set_draw_color(*BORDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def accent_divider(self):
        y = self.get_y()
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.3)
        self.line(self.w * 0.35, y, self.w * 0.65, y)
        self.set_line_width(0.2)
        self.ln(3)

    def cost_row(self, name, inp, out):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*LIGHT)
        self.set_x(self.l_margin + 5)
        self.cell(52, 4.5, _s(name))
        self.set_text_color(*EMERALD)
        self.cell(30, 4.5, _s(inp))
        self.set_text_color(*AMBER)
        self.cell(0, 4.5, _s(out), new_x="LMARGIN", new_y="NEXT")


# ============================================================
# DATA (same comprehensive data as before)
# ============================================================

AGENT_LAYERS = [
    ("Executive Layer", 5, [
        ("Commander Orion", "Commander", "gpt-5.2", "Supreme orchestrator. Decomposes goals into 3-7 tasks, assigns to specialists, coordinates multi-agent execution, compiles deliverables.", "Task Delegation, Strategic Planning, Team Orchestration, Goal Breakdown"),
        ("Chief Strategy Officer", "Strategist", "gpt-5.2", "Markets, competitors, SWOT, business plans, growth roadmaps. Data-backed strategic recommendations.", "Business Strategy, Competitive Analysis, Market Research"),
        ("Revenue Strategist", "Revenue", "gpt-5.2", "Monetization modeling, pricing tiers, subscription models, upsell strategies, revenue forecasts.", "Revenue Optimization, Pricing Strategy, Financial Forecasting"),
        ("Investor Relations", "IR", "gpt-5.2", "Pitch decks, fundraising materials, quarterly updates, investor comms, financial storytelling.", "Investor Communications, Fundraising, Pitch Decks"),
        ("Business Strategist", "Strategy", "gpt-5.2", "Market positioning, business model innovation, go-to-market strategy, market expansion.", "Market Positioning, Business Models, GTM Strategy"),
    ]),
    ("Product & Technical Layer", 7, [
        ("Product Manager", "PM", "gpt-5.2", "Roadmaps, user stories, RICE/MoSCoW prioritization, sprint planning, product lifecycle.", "Product Roadmaps, Feature Prioritization, Sprint Planning"),
        ("Project Manager", "Project", "gpt-5.2", "Timelines, Gantt charts, dependencies, blockers, resource management, milestone tracking.", "Timeline Management, Risk Management, Resource Allocation"),
        ("App Developer", "Dev", "gpt-5.2", "Full-stack: React, Node.js, Python, TypeScript. Production-ready web/mobile/API code.", "Web Development, API Design, Full-Stack, React/Node.js"),
        ("Automation Engineer", "Auto", "gpt-5.2", "CI/CD pipelines, workflow automation, process optimization, integration scripts.", "Workflow Automation, CI/CD, Process Optimization"),
        ("AI Optimizer", "AI", "gpt-4o", "ML model tuning, prompt engineering, cost optimization, model selection.", "ML Tuning, Performance, Cost Monitoring, Prompt Engineering"),
        ("Data Engineer", "Data", "gpt-5.2", "Data pipelines, ETL, database architecture, data warehousing, clean data flows.", "Data Pipelines, ETL, Database Architecture"),
        ("Cybersecurity", "Security", "gpt-5.2", "Security audits, vulnerability assessments, penetration testing, compliance.", "Security Audits, Vulnerability Assessment, Compliance"),
    ]),
    ("Creative & Brand Layer", 7, [
        ("Brand Architect", "Brand", "gpt-5.2", "Brand identity systems, positioning, visual language, brand books, style guides.", "Brand Identity, Positioning, Visual Language"),
        ("Graphics Designer", "Design", "gpt-5.2", "Images, visual assets, infographics, social graphics, color theory, composition.", "Image Creation, Visual Assets, Infographics"),
        ("Video Specialist", "Video", "gpt-5.2", "Scripts, storyboards, YouTube/TikTok formats, motion graphics.", "Video Scripts, Storyboarding, Motion Graphics"),
        ("Copywriter", "Copy", "gpt-5.2", "Sales copy, website content, product descriptions, email sequences, AIDA/PAS.", "Sales Copy, Website Content, Email Sequences"),
        ("Web Designer", "Web", "gpt-5.2", "Wireframes, landing pages, UI/UX, color palettes, typography, conversion design.", "UI/UX Design, Wireframing, Landing Pages"),
        ("UX Researcher", "UXR", "gpt-5.2", "User testing, journey maps, usability analysis, persona development.", "User Testing, Journey Mapping, Persona Development"),
        ("3D Specialist", "3D", "gpt-5.2", "3D models, product visualization, AR/VR, immersive content.", "3D Modeling, Product Visualization, AR/VR"),
    ]),
    ("Growth & Marketing Layer", 7, [
        ("Marketing Specialist", "Marketing", "gpt-5.2", "Campaigns, ad copy, consumer psychology, viral content, conversion optimization.", "Campaign Strategy, Performance Marketing, Ad Copy"),
        ("Growth Hacker", "Growth", "gpt-5.2", "Viral loops, A/B tests, conversion funnels, growth experiments.", "Viral Loops, A/B Testing, Conversion Optimization"),
        ("SEO Specialist", "SEO", "gpt-5.2", "Keyword research, on-page/off-page, technical SEO, content strategy.", "Keyword Research, Technical SEO, Content Strategy"),
        ("Social Media Manager", "Social", "gpt-5.2", "Platform strategy, community, content calendars, TikTok/IG/LinkedIn algorithms.", "Platform Strategy, Community Management"),
        ("Email Marketing", "Email", "gpt-5.2", "Drip campaigns, newsletters, segmentation, deliverability, automated flows.", "Drip Campaigns, Newsletters, Segmentation"),
        ("Sales Representative", "Sales", "gpt-5.2", "Lead qualification, outreach sequences, pipeline, B2B/B2C sales.", "Lead Qualification, Outreach, Pipeline Analysis"),
        ("PR Manager", "PR", "gpt-5.2", "Media relations, press releases, crisis comms, thought leadership.", "Media Relations, Press Releases, Crisis Comms"),
    ]),
    ("Operations Layer", 6, [
        ("Operations Manager", "Ops", "gpt-5.2", "Process optimization, SOPs, workflow diagrams, capacity planning.", "Process Optimization, SOPs, Capacity Planning"),
        ("Inventory Manager", "Inventory", "gpt-5.2", "Stock levels, supply chain, demand forecasting, warehouse logistics.", "Stock Management, Supply Chain, Forecasting"),
        ("Procurement Manager", "Procurement", "gpt-5.2", "Vendor management, cost negotiation, sourcing strategies.", "Vendor Management, Cost Negotiation, Sourcing"),
        ("HR Specialist", "HR", "gpt-5.2", "Recruitment, onboarding, culture, performance reviews, HR policy.", "Recruitment, Onboarding, Performance Reviews"),
        ("Customer Service", "Support", "gpt-5.2", "Tickets, FAQs, complaints, de-escalation, proactive support.", "Ticket Resolution, FAQ, Customer Satisfaction"),
        ("CX Architect", "CX", "gpt-5.2", "Journey optimization, NPS, loyalty programs, touchpoint design.", "Journey Optimization, NPS, Loyalty Programs"),
    ]),
    ("Finance Layer", 2, [
        ("Financial Analyst", "Finance", "gpt-5.2", "Financial models, DCF valuations, forecasts, budgets, P&L analysis.", "Financial Modeling, Forecasting, Valuation"),
        ("Data Analyst", "Analytics", "gpt-5.2", "Dashboards, trend analysis, data visualization, business intelligence.", "Business Intelligence, Dashboards, Data Viz"),
    ]),
    ("Governance Layer", 3, [
        ("Legal Assistant", "Legal", "gpt-5.2", "Contract review, legal research, compliance, document drafting.", "Contract Review, Legal Research, Compliance"),
        ("Compliance Officer", "Compliance", "gpt-5.2", "Regulatory adherence, audit prep, policy monitoring, frameworks.", "Regulatory Adherence, Audit Preparation"),
        ("Ethics Officer", "Ethics", "gpt-5.2", "Ethical AI governance, bias detection, fair practices.", "Ethical AI, Bias Detection, Responsible AI"),
    ]),
    ("Intelligence Layer", 4, [
        ("Research Specialist", "Research", "gpt-5.2", "Deep research, competitive analysis, trend forecasting, market intelligence.", "Deep Research, Competitive Analysis, Trends"),
        ("Knowledge Architect", "Knowledge", "gpt-5.2", "Knowledge bases, taxonomy design, information architecture.", "Knowledge Base, Taxonomy, Info Architecture"),
        ("Localization Specialist", "L10n", "gpt-5.2", "Translation, cultural adaptation, multi-language content, 50+ languages.", "Translation, Cultural Adaptation, Multi-Language"),
        ("Personal Secretary", "Assistant", "gpt-5.2", "Calendars, emails, scheduling, real-world action bridge from Commander.", "Calendar, Email, Scheduling, Action Execution"),
    ]),
]

SYSTEMS = [
    ("Autonomous Orchestration Engine", "Commander Orion receives a business goal, scores complexity (1-10), decomposes into 3-7 milestones with tasks, assigns to optimal specialists, executes in parallel where dependencies allow, applies quality control, and compiles a unified deliverable. Supports failure recovery and escalation.", "POST /api/projects, POST /api/projects/{id}/execute, GET /api/projects/{id}"),
    ("Custom Brain Profiles", "Every agent has a configurable brain: LLM model selection (9 providers), autonomy level (1-10), communication style (formal/casual/technical/creative), creativity temperature (0.0-1.0), tool permissions (web search, code execution, email), and context window size. Profiles persist per-user.", "GET/PUT/DELETE /api/agents/{id}/brain, GET /api/brain-profiles"),
    ("Quality Control & Failure Recovery", "Critic Module (GPT-4o) auto-reviews every output on a 1-10 scale (accuracy, completeness, relevance). Failed tasks auto-retry with fallback chain: GPT-5.2 -> Claude Sonnet -> Gemini Pro -> GPT-4o. If all fail, escalates to Commander then user.", "POST /api/enterprise/quality/review, GET /api/enterprise/quality/history"),
    ("Model-Agnostic LLM Router", "Analyzes task content for complexity signals (coding, reasoning, creative, data, legal, simple). Maps to tiers: Premium (GPT-5.2, Claude), Standard (GPT-4o, Gemini Flash), Economy (GPT-4o Mini, Haiku). Logs all decisions. User preference can override.", "POST /api/enterprise/router/route-task, GET /api/enterprise/router/history"),
    ("Autonomous Collaboration Engine", "After each task, maps agent to 1 of 9 domains. Scans result for cross-domain keywords. Auto-creates collaboration requests to relevant agents. 41 agents across 9 domains with trigger rules for seamless coordination.", "POST/GET/PATCH /api/collaborations, GET /api/enterprise/collaboration/log"),
    ("Universal Reference Intelligence", "Analyzes reference text to extract Style Blueprints: writing style, tone, vocabulary, sentence patterns, audience profile, content structure, key phrases. Blueprints stored and reusable across Content Generator.", "POST /api/reference/analyze, GET /api/reference/blueprints"),
    ("Content Generator", "Generates on-brand content using Style Blueprints. 8 types: blog, social, email, ad copy, product desc, press release, newsletter, script. Length control (short/medium/long), tone override, generation history.", "POST /api/content/generate, GET /api/content/history"),
    ("Vibe Coding App Builder", "Chat-based full-stack app generation. Each message: intent analysis -> code generation (HTML/CSS/JS/Tailwind) -> live iframe preview -> iterative refinement -> download. Persistent projects.", "POST /api/vibe/projects, POST /api/vibe/projects/{id}/chat, GET .../preview"),
    ("Agent Activity Monitor (WebSocket)", "Real-time dashboard via WebSocket (/api/ws/activity, 8s updates). Shows: agent status with completion rates, inter-agent communication flows, task dependency graph, recent tool executions. REST fallback polling at 10s.", "WS /api/ws/activity, GET /api/enterprise/activity/live"),
    ("Simulation vs. Execution Mode", "System-wide toggle. Simulation (default): agents return descriptive responses, no external APIs called. Execution: real Gmail sends, Calendar events, API calls. Confirmation prompt before mode switch.", "GET/PUT /api/enterprise/system/mode"),
    ("Real-World Action Layer", "Google Suite integration (Gmail + Calendar) via OAuth 2.0. All actions gated by system mode. Personal Secretary as execution bridge. Full action logging.", "GET /api/oauth/gmail/login, POST /api/actions/send-email, POST /api/actions/create-event"),
    ("Flexible LLM Configuration", "9 providers, 30+ models. Users choose preferred model in Settings. Override priority: Agent brain profile > User default > LLM Router auto-selection.", "PUT /api/users/me/config"),
    ("Voice Command Interface", "Mic button in Command Palette captures audio (WebM via MediaRecorder), transcribes via OpenAI Whisper, auto-fills search for hands-free navigation across pages, agents, and actions.", "POST /api/voice/transcribe"),
    ("Admin Code Explorer", "Full codebase browser: recursive file tree, code viewer with line numbers and language detection, file search, copy-to-clipboard, ZIP download of entire codebase. Admin-only with path traversal protection.", "GET /api/admin/code/tree, /file, /search, /export"),
    ("Memory Governance", "CRUD with versioning (every update creates version). Relevance scoring: time-decay (30-day half-life) + access frequency + importance weight. Auto-pruning with dry-run preview. 500-entry limit. Stats dashboard.", "POST/GET/PUT/DELETE /api/memory/entries, POST /api/memory/prune, GET /api/memory/stats"),
    ("Agent Memory Auto-Learning", "GPT-4o-mini extracts 1-3 key learnings from every completed task. Categories: fact, preference, instruction, context, decision. Near-duplicate detection. Async execution (never blocks task completion).", "Auto-triggered by orchestration_service.py and agent_service.py"),
    ("Command Palette", "VS Code-style quick search (press / or Cmd+K). Searches 20+ pages, 41 agents, and quick actions. Keyboard navigation, recent searches in localStorage, voice integration via mic button.", "Frontend-only (uses /api/agents/public for agent data)"),
]

PROVIDERS = [
    ("OpenAI", [("GPT-5.2", "Flagship", "$2.50/$10"), ("GPT-4o", "Fast", "$2.50/$10"), ("GPT-4o Mini", "Economy", "$0.15/$0.60"), ("O3", "Reasoning", "$10/$40"), ("O3 Mini", "Reasoning", "$1.10/$4.40"), ("GPT Image 1", "Image", "$0.02/img"), ("Sora 2", "Video", "$0.10/sec"), ("Whisper", "STT", "Included")]),
    ("Anthropic", [("Claude Sonnet 4.5", "Flagship", "$3/$15"), ("Claude Opus 4.5", "Premium", "$15/$75"), ("Claude Haiku 4.5", "Economy", "$0.80/$4")]),
    ("Google Gemini", [("Gemini 3 Flash", "Fast", "$0.075/$0.30"), ("Gemini 3 Pro", "Flagship", "$1.25/$5"), ("Nano Banana 2", "Image", "$0.02/img")]),
    ("xAI (Grok)", [("Grok 3", "Flagship", "$3/$15"), ("Grok 3 Mini", "Economy", "$0.30/$0.50"), ("Grok 2", "Fast", "$2/$10")]),
    ("DeepSeek", [("DeepSeek Chat", "Economy", "$0.14/$0.28"), ("DeepSeek Reasoner", "Reasoning", "$0.55/$2.19")]),
    ("Mistral AI", [("Mistral Large", "Flagship", "$2/$6"), ("Mistral Medium", "Fast", "$0.40/$2"), ("Mistral Small", "Economy", "$0.10/$0.30")]),
    ("Perplexity", [("Sonar", "Search", "$1/$1"), ("Sonar Pro", "Research", "$3/$15")]),
    ("Cohere", [("Command R+", "Flagship", "$2.50/$10"), ("Command R", "Economy", "$0.15/$0.60")]),
    ("ElevenLabs", [("Multilingual v2", "Voice", "$0.30/1K ch"), ("Turbo v2.5", "Voice", "$0.18/1K ch")]),
]


@router.get("/summary/pdf")
async def download_summary_pdf(current_user: User = Depends(get_current_user)):
    total_tasks = await db.tasks.count_documents({})
    total_projects = await db.projects.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_memories = await db.memory_entries.count_documents({"user_id": current_user.user_id})
    auto_learned = await db.memory_entries.count_documents({"user_id": current_user.user_id, "source": "auto_learn"})

    pdf = DarkPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=14)

    # ===== PAGE 1: TITLE =====
    pdf.add_page()
    pdf.ln(4)

    # Title
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "MAARS Command", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DIM)
    pdf.cell(0, 6, "by MAARS Global Corporation", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Description
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 5, _s(
        "MAARS Command is an Autonomous AI Enterprise Operating System that deploys a workforce of "
        "41 specialized AI agents organized across 8 organizational layers. It merges the power of "
        "preset specialist business agents with autonomous execution, persistent memory, and real-world "
        "action capabilities. Users set high-level business goals, and the AI workforce autonomously "
        "plans, delegates, executes, collaborates, and delivers -- with quality control, failure recovery, "
        "and human oversight at every step."
    ))
    pdf.ln(4)

    # Badge pills
    bx = pdf.l_margin
    by = pdf.get_y()
    for color, label in BADGE_COLORS:
        tw = pdf.badge_pill(bx, by, label, color)
        bx += tw + 3
        if bx > pdf.w - 40:
            bx = pdf.l_margin
            by += 7.5
    pdf.set_y(by + 10)

    # Stat cards
    cw = (pdf.w - 2 * pdf.l_margin - 4 * 3) / 5
    cx = pdf.l_margin
    cy = pdf.get_y()
    for num, label, color in STAT_CARDS:
        pdf.stat_card(cx, cy, cw, 26, num, label, color)
        cx += cw + 3
    pdf.set_y(cy + 32)

    # Table of contents
    pdf.section_title("Table of Contents")
    for i, name in enumerate([
        "Platform Statistics",
        "The 41-Agent AI Workforce (8 Layers)",
        f"Core Systems & Capabilities ({len(SYSTEMS)} Systems)",
        f"AI Models & Providers ({len(PROVIDERS)} Providers)",
        "Technical Architecture",
        "Complete API Reference (212+ Endpoints)",
    ], 1):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*LIGHT)
        pdf.set_x(pdf.l_margin + 4)
        pdf.cell(8, 5, f"{i}.")
        pdf.set_text_color(*INDIGO)
        pdf.cell(0, 5, _s(name), new_x="LMARGIN", new_y="NEXT")

    # ===== SECTION 1: STATISTICS =====
    pdf.add_page()
    pdf.section_title("1. Platform Statistics")
    for label, value, color in [
        ("AI Agents", "41", INDIGO), ("Organizational Layers", "8", AMBER),
        ("Core Systems", str(len(SYSTEMS)), EMERALD), ("AI Providers", str(len(PROVIDERS)), VIOLET),
        ("AI Models Available", "30+", CYAN), ("API Endpoints", "212+", SKY),
        ("Frontend Pages", "20+", PINK), ("Database Collections", "27+", ORANGE),
        ("Total Projects", str(total_projects), LIGHT), ("Total Tasks Executed", str(total_tasks), LIGHT),
        ("Chat Conversations", str(total_chats), LIGHT),
        ("Memory Entries", f"{total_memories} ({auto_learned} auto-learned)", LIGHT),
    ]:
        pdf.kv_row(label, value, color)

    # ===== SECTION 2: AGENTS =====
    pdf.add_page()
    pdf.section_title("2. The 41-Agent AI Workforce")
    pdf.body("Each agent has a unique identity and Custom Brain Profile: LLM model, autonomy level (1-10), communication style, tool permissions, and creativity temperature. Organized into 8 enterprise layers.")

    for layer_name, count, agents in AGENT_LAYERS:
        pdf.subsection(f"{layer_name} ({count} agents)")
        for name, role, model, desc, caps in agents:
            pdf.sub3(f"{name}  [{role}]  |  Default: {model}")
            pdf.body(desc)
            pdf.bullet(f"Capabilities: {caps}", DIM)
            pdf.ln(0.5)
        pdf.divider()

    # ===== SECTION 3: SYSTEMS =====
    pdf.add_page()
    pdf.section_title(f"3. Core Systems & Capabilities ({len(SYSTEMS)} Systems)")
    pdf.body("These are the engines powering MAARS Command. Each system has its own data model, API endpoints, and configuration.")

    for i, (name, desc, endpoints) in enumerate(SYSTEMS, 1):
        pdf.subsection(f"{i}. {name}")
        pdf.body(desc)
        pdf.sub3("Endpoints")
        pdf.dim_text(endpoints)
        pdf.ln(1)
        if i < len(SYSTEMS):
            pdf.divider()

    # ===== SECTION 4: AI PROVIDERS =====
    pdf.add_page()
    pdf.section_title(f"4. AI Models & Providers ({len(PROVIDERS)} Providers)")
    pdf.body("9 AI providers with 30+ models for text, reasoning, search, image generation, video, voice, and speech-to-text. All accessible via Emergent Universal LLM Key or direct API keys.")

    for prov_name, models in PROVIDERS:
        pdf.subsection(f"{prov_name} ({len(models)} models)")
        # Header row
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*DIM)
        pdf.set_x(pdf.l_margin + 5)
        pdf.cell(52, 4.5, "Model")
        pdf.cell(25, 4.5, "Tier")
        pdf.cell(0, 4.5, "Cost (In/Out per 1M tok)", new_x="LMARGIN", new_y="NEXT")
        for mname, tier, cost in models:
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(*WHITE)
            pdf.set_x(pdf.l_margin + 5)
            pdf.cell(52, 4.5, _s(mname))
            # Tier with color
            tier_colors = {"Flagship": AMBER, "Fast": CYAN, "Economy": EMERALD, "Premium": VIOLET, "Reasoning": ROSE, "Search": SKY, "Research": INDIGO, "Image": PINK, "Video": RED, "Voice": ORANGE, "STT": CYAN}
            pdf.set_text_color(*(tier_colors.get(tier, LIGHT)))
            pdf.cell(25, 4.5, _s(tier))
            pdf.set_text_color(*DIM)
            pdf.cell(0, 4.5, _s(cost), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # ===== SECTION 5: ARCHITECTURE =====
    pdf.add_page()
    pdf.section_title("5. Technical Architecture")

    for section, items in [
        ("Backend Stack", [
            "FastAPI (Python 3.11) -- async/await, high-performance ASGI",
            "MongoDB -- 27+ collections (agents, tasks, projects, chats, memories...)",
            "WebSocket -- real-time Activity Monitor streaming (8s updates)",
            "JWT authentication with admin role detection",
            "Emergent Integrations SDK -- unified 9-provider LLM access",
            "Background tasks via asyncio.create_task (non-blocking)",
            "StreamingResponse for ZIP/PDF file downloads",
        ]),
        ("Frontend Stack", [
            "React 18 with hooks and Context API",
            "Tailwind CSS with custom dark theme",
            "Shadcn/UI component library (Button, Card, Badge, etc.)",
            "React Router v6 with protected and admin routes",
            "DashboardLayout -- single resizable sidebar for all 20+ pages",
            "Command Palette with voice integration",
            "WebSocket client with REST fallback",
        ]),
        ("AI & LLM Layer", [
            "9 providers: OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs",
            "30+ models: text, reasoning, search, image, video, voice, STT",
            "Model-Agnostic LLM Router (auto-selects optimal model)",
            "Quality Control Critic Module (GPT-4o, 1-10 scoring)",
            "Failure Recovery (GPT-5.2 -> Claude -> Gemini -> GPT-4o)",
            "Memory Auto-Learning (GPT-4o-mini knowledge extraction)",
            "Universal Emergent LLM Key (single key, all providers)",
        ]),
        ("Database (27+ Collections)", [
            "users, agents, agent_brains -- Accounts, definitions, brain profiles",
            "chats, messages -- Conversation history with agents",
            "tasks, projects -- Task execution and project orchestration",
            "collaborations -- Inter-agent collaboration requests",
            "quality_reviews -- Quality control scores and feedback",
            "memory_entries -- Versioned memory with relevance scoring",
            "vibe_projects -- Vibe Coding app builder projects",
            "style_blueprints, generated_content -- Reference Intelligence",
            "teams, team_invites -- Team management",
            "subscriptions, usage_logs -- Billing and usage tracking",
            "routing_logs -- LLM Router decision audit trail",
            "oauth_tokens, action_logs -- Google OAuth and action logs",
            "system_config -- System-wide settings",
        ]),
    ]:
        pdf.subsection(section)
        for item in items:
            pdf.bullet(item)
        pdf.ln(2)

    # ===== SECTION 6: API REFERENCE =====
    pdf.add_page()
    pdf.section_title("6. Complete API Reference (212+ Endpoints)")
    pdf.body("All endpoints require JWT auth (Authorization: Bearer <token>) unless noted. Admin endpoints require is_admin=true.")

    api_groups = [
        ("Authentication", ["POST /api/auth/register", "POST /api/auth/login", "GET /api/auth/me", "GET /api/stats"]),
        ("Agents (41)", ["GET /api/agents/public", "GET/POST /api/agents", "GET /api/agents/{id}", "POST /api/agents/{id}/chat", "GET/PUT/DELETE /api/agents/{id}/brain"]),
        ("Projects & Orchestration", ["POST /api/projects", "GET /api/projects", "POST /api/projects/{id}/execute", "GET /api/projects/{id}", "PATCH/DELETE /api/projects/{id}"]),
        ("Tasks", ["GET /api/tasks", "POST /api/tasks", "PATCH /api/tasks/{id}", "POST /api/tasks/{id}/execute"]),
        ("Enterprise", ["POST/GET/PATCH /api/collaborations", "GET /api/enterprise/kpis", "GET /api/enterprise/activity/live", "WS /api/ws/activity", "GET/PUT /api/enterprise/system/mode", "POST /api/enterprise/quality/review", "POST /api/enterprise/router/route-task"]),
        ("Memory", ["POST/GET /api/memory/entries", "PUT/DELETE /api/memory/entries/{id}", "GET /api/memory/entries/{id}/versions", "POST /api/memory/prune", "GET /api/memory/stats"]),
        ("Content & Intelligence", ["POST /api/reference/analyze", "GET /api/reference/blueprints", "POST /api/content/generate", "GET /api/content/history"]),
        ("Vibe Coding", ["POST /api/vibe/projects", "GET /api/vibe/projects", "POST /api/vibe/projects/{id}/chat", "GET /api/vibe/projects/{id}/preview"]),
        ("Voice & Code Explorer", ["POST /api/voice/transcribe", "GET /api/admin/code/tree", "GET /api/admin/code/file", "GET /api/admin/code/search", "GET /api/admin/code/export", "GET /api/summary/pdf"]),
        ("Real-World Actions", ["GET /api/oauth/gmail/login", "GET /api/oauth/gmail/callback", "POST /api/actions/send-email", "POST /api/actions/create-event"]),
        ("Teams", ["POST /api/teams", "GET /api/teams", "POST /api/teams/{id}/invite", "PUT /api/teams/{id}/members/{uid}", "POST /api/chats/{id}/share"]),
        ("Billing", ["GET /api/plans", "GET /api/subscription", "POST /api/checkout", "GET /api/credits"]),
        ("Admin (30+)", ["GET /api/admin/stats", "GET /api/admin/users", "GET /api/admin/analytics", "GET /api/admin/profit", "GET /api/admin/audit-log", "GET /api/admin/agent-performance"]),
    ]

    for section, endpoints in api_groups:
        pdf.subsection(section)
        for ep in endpoints:
            pdf.bullet(ep)
        pdf.ln(1)

    # ===== END =====
    pdf.ln(5)
    pdf.accent_divider()
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*INDIGO)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 5, "End of Document", align="C")
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*MUTED)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 4, _s(f"Generated {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}  |  MAARS Global Corporation  |  Confidential"), align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=MAARS-Command-Documentation.pdf"})
