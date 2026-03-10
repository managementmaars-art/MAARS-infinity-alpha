"""MAARS Command -- Premium dark-themed PDF documentation generator.

Matches the About page aesthetic: dark background, colored accents,
card-based stats, badge pills, and professional typography.
"""
import io
import logging
from pathlib import Path
from datetime import datetime, timezone
from fpdf import FPDF
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from auth import get_current_user, User
from db import db

logger = logging.getLogger(__name__)
router = APIRouter()

# Font name - use DejaVu for Unicode support
_FONT_DIR = Path(__file__).parent.parent
_DEJAVU = _FONT_DIR / "DejaVuSans.ttf"
_DEJAVU_BOLD = _FONT_DIR / "DejaVuSans-Bold.ttf"
FN = "DejaVu" if _DEJAVU.exists() else "Helvetica"


def _s(t):
    return str(t)


# === COLORS ===
BG = (10, 10, 14)
CARD_BG = (20, 20, 26)
CARD_BG_ALT = (26, 26, 34)
BORDER = (38, 38, 50)
WHITE = (240, 240, 248)
LIGHT = (185, 185, 200)
DIM = (110, 110, 130)
MUTED = (70, 70, 88)
INDIGO = (99, 102, 241)
VIOLET = (139, 92, 246)
EMERALD = (52, 211, 153)
AMBER = (251, 191, 36)
ROSE = (244, 63, 94)
CYAN = (34, 211, 238)
PINK = (236, 72, 153)
SKY = (56, 189, 248)
ORANGE = (251, 146, 60)
RED = (239, 68, 68)
TEAL = (45, 212, 191)
YELLOW = (250, 204, 21)
GREEN = (74, 222, 128)
BLUE = (96, 165, 250)

LAYER_COLORS = {
    "Executive Layer": AMBER,
    "Product & Technical Layer": CYAN,
    "Creative & Brand Layer": PINK,
    "Growth & Marketing Layer": GREEN,
    "Operations Layer": INDIGO,
    "Finance Layer": EMERALD,
    "Governance Layer": RED,
    "Intelligence Layer": VIOLET,
}

BADGE_COLORS = [
    (INDIGO, "Multi-Agent Orchestration"),
    (EMERALD, "Quality Control"),
    (AMBER, "LLM Router"),
    (PINK, "Content Generation"),
    (CYAN, "Vibe Coding"),
    (VIOLET, "Memory Governance"),
    (ROSE, "Voice Commands"),
    (SKY, "Code Explorer"),
]

STAT_CARDS = [
    ("458+", "AI Agents", INDIGO),
    ("27", "Networks", AMBER),
    ("17", "Core Systems", EMERALD),
    ("13", "LLM Providers", VIOLET),
    ("212+", "API Endpoints", CYAN),
]

SYSTEM_COLORS = [
    ROSE, VIOLET, EMERALD, CYAN, INDIGO, PINK, AMBER, GREEN,
    BLUE, ORANGE, TEAL, SKY, ROSE, SKY, VIOLET, CYAN, YELLOW,
]


class DarkPDF(FPDF):
    """Dark-themed PDF matching the MAARS Command About page aesthetic."""

    def __init__(self):
        super().__init__()
        if _DEJAVU.exists():
            self.add_font("DejaVu", "", str(_DEJAVU))
        if _DEJAVU_BOLD.exists():
            self.add_font("DejaVu", "B", str(_DEJAVU_BOLD))

    def _fill_page(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, self.w, self.h, style="F")

    def header(self):
        self._fill_page()
        if self.page_no() == 1:
            return
        # Top accent bar
        self.set_fill_color(*INDIGO)
        self.rect(0, 0, self.w, 1.2, style="F")
        # Header text area
        self.set_fill_color(15, 15, 20)
        self.rect(0, 1.2, self.w, 10, style="F")
        self.set_y(2.5)
        self.set_font(FN, "B", 7)
        self.set_text_color(*INDIGO)
        self.set_x(self.l_margin)
        self.cell(0, 5, _s("MAARS Command"))
        self.set_font(FN, "", 6.5)
        self.set_text_color(*DIM)
        self.cell(0, 5, "Comprehensive System Documentation", align="R")
        # Separator
        self.set_draw_color(*BORDER)
        self.set_line_width(0.15)
        self.line(self.l_margin, 11.2, self.w - self.r_margin, 11.2)
        self.set_y(14)

    def footer(self):
        self.set_y(-12)
        # Footer line
        self.set_draw_color(*BORDER)
        self.set_line_width(0.15)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-10)
        self.set_font(FN, "", 6)
        self.set_text_color(*MUTED)
        self.cell(self.w / 2 - self.l_margin, 5, f"MAARS Global Corporation  |  {datetime.now(timezone.utc).strftime('%B %d, %Y')}")
        self.set_font(FN, "B", 6)
        self.set_text_color(*DIM)
        self.cell(0, 5, f"Page {self.page_no()} / {{nb}}", align="R")

    # --- Drawing helpers ---

    def _ensure_space(self, needed):
        if self.get_y() + needed > self.h - 16:
            self.add_page()

    def dark_card(self, x, y, w, h, accent_color=None):
        self.set_fill_color(*CARD_BG)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.rect(x, y, w, h, style="DF")
        if accent_color:
            self.set_fill_color(*accent_color)
            self.rect(x, y, 1.5, h, style="F")

    def accent_card(self, x, y, w, h, accent_color):
        self.set_fill_color(*CARD_BG)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.rect(x, y, w, h, style="DF")
        # Top accent bar
        self.set_fill_color(*accent_color)
        self.rect(x, y, w, 1.8, style="F")

    def badge_pill(self, x, y, text, color):
        self.set_font(FN, "B", 6.5)
        tw = self.get_string_width(text) + 10
        # Pill background with slight transparency effect
        r, g, b = color
        self.set_fill_color(r // 4, g // 4, b // 4)
        self.set_draw_color(*color)
        self.set_line_width(0.4)
        self.rect(x, y, tw, 6, style="DF")
        self.set_text_color(*color)
        self.set_xy(x, y + 0.3)
        self.cell(tw, 5.5, _s(text), align="C")
        return tw

    def stat_card(self, x, y, w, h, number, label, color):
        self.accent_card(x, y, w, h, color)
        # Number
        self.set_font(FN, "B", 24)
        self.set_text_color(*color)
        self.set_xy(x, y + 5)
        self.cell(w, 10, _s(str(number)), align="C")
        # Label
        self.set_font(FN, "", 7.5)
        self.set_text_color(*LIGHT)
        self.set_xy(x, y + 17)
        self.cell(w, 5, _s(label), align="C")

    def colored_dot(self, x, y, r, color):
        self.set_fill_color(*color)
        self.ellipse(x - r, y - r, r * 2, r * 2, style="F")

    # --- Text helpers ---

    def section_title(self, text, color=None):
        self._ensure_space(18)
        self.ln(6)
        y = self.get_y()
        c = color or INDIGO
        # Accent bar
        self.set_fill_color(*c)
        self.rect(self.l_margin, y, 3, 9, style="F")
        # Title text
        self.set_font(FN, "B", 16)
        self.set_text_color(*WHITE)
        self.set_x(self.l_margin + 6)
        self.cell(0, 9, _s(text))
        self.ln(12)

    def subsection(self, text, color=None):
        self._ensure_space(10)
        self.ln(2)
        y = self.get_y()
        c = color or LIGHT
        self.set_fill_color(*c)
        self.rect(self.l_margin + 2, y + 1.5, 1.5, 4, style="F")
        self.set_font(FN, "B", 11)
        self.set_text_color(*WHITE)
        self.set_x(self.l_margin + 6)
        self.cell(0, 6, _s(text))
        self.ln(7)

    def sub3(self, text, color=None):
        self.set_font(FN, "B", 9)
        self.set_text_color(*(color or LIGHT))
        self.set_x(self.l_margin + 4)
        self.multi_cell(0, 4.5, _s(text))

    def body(self, text):
        self.set_font(FN, "", 8.5)
        self.set_text_color(*LIGHT)
        self.set_x(self.l_margin + 2)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 2, 4.3, _s(text))
        self.ln(1)

    def bullet(self, text, color=None):
        self.set_font(FN, "", 8)
        tc = color or LIGHT
        self.set_text_color(*tc)
        x_start = self.l_margin + 6
        y = self.get_y()
        # Bullet dot
        self.colored_dot(self.l_margin + 4, y + 2, 0.8, tc)
        self.set_x(x_start)
        self.multi_cell(self.w - x_start - self.r_margin, 4, _s(text))

    def dim_text(self, text):
        self.set_font(FN, "", 7.5)
        self.set_text_color(*DIM)
        self.set_x(self.l_margin + 4)
        self.multi_cell(0, 3.8, _s(text))

    def kv_row(self, key, value, val_color=None):
        self._ensure_space(6)
        y = self.get_y()
        # Alternating row bg
        if int(y) % 2 == 0:
            self.set_fill_color(*CARD_BG)
            self.rect(self.l_margin, y, self.w - self.l_margin - self.r_margin, 5.5, style="F")
        self.set_font(FN, "", 8.5)
        self.set_text_color(*DIM)
        self.set_x(self.l_margin + 4)
        self.cell(62, 5.5, _s(key))
        self.set_font(FN, "B", 8.5)
        self.set_text_color(*(val_color or INDIGO))
        self.cell(0, 5.5, _s(str(value)), new_x="LMARGIN", new_y="NEXT")

    def divider(self):
        self.set_draw_color(*BORDER)
        self.set_line_width(0.1)
        self.line(self.l_margin + 2, self.get_y(), self.w - self.r_margin - 2, self.get_y())
        self.ln(2)

    def accent_divider(self, color=None):
        y = self.get_y()
        c = color or INDIGO
        # Center dot with lines
        mid = self.w / 2
        self.set_draw_color(*BORDER)
        self.set_line_width(0.15)
        self.line(self.l_margin + 20, y, mid - 6, y)
        self.line(mid + 6, y, self.w - self.r_margin - 20, y)
        self.colored_dot(mid - 3, y, 1, c)
        self.colored_dot(mid, y, 1.3, c)
        self.colored_dot(mid + 3, y, 1, c)
        self.ln(4)


# ============================================================
# DATA
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
    ("Custom Brain Profiles", "Every agent has a configurable brain: LLM model selection (13 providers), autonomy level (1-10), communication style (formal/casual/technical/creative), creativity temperature (0.0-1.0), tool permissions (web search, code execution, email), and context window size. Profiles persist per-user.", "GET/PUT/DELETE /api/agents/{id}/brain, GET /api/brain-profiles"),
    ("Quality Control & Failure Recovery", "Critic Module (GPT-4o) auto-reviews every output on a 1-10 scale (accuracy, completeness, relevance). Failed tasks auto-retry with fallback chain: GPT-5.2 -> Claude Sonnet -> Gemini Pro -> GPT-4o. If all fail, escalates to Commander then user.", "POST /api/enterprise/quality/review, GET /api/enterprise/quality/history"),
    ("Model-Agnostic LLM Router", "Analyzes task content for complexity signals (coding, reasoning, creative, data, legal, simple). Maps to tiers: Premium (GPT-5.2, Claude), Standard (GPT-4o, Gemini Flash), Economy (GPT-4o Mini, Haiku). Logs all decisions. User preference can override.", "POST /api/enterprise/router/route-task, GET /api/enterprise/router/history"),
    ("Autonomous Collaboration Engine", "After each task, maps agent to 1 of 27 network categories. Scans result for cross-domain keywords. Auto-creates collaboration requests to relevant agents. 458+ agents across 27 networks with trigger rules for seamless coordination.", "POST/GET/PATCH /api/collaborations, GET /api/enterprise/collaboration/log"),
    ("Universal Reference Intelligence", "Analyzes reference text to extract Style Blueprints: writing style, tone, vocabulary, sentence patterns, audience profile, content structure, key phrases. Blueprints stored and reusable across Content Generator.", "POST /api/reference/analyze, GET /api/reference/blueprints"),
    ("Content Generator", "Generates on-brand content using Style Blueprints. 8 types: blog, social, email, ad copy, product desc, press release, newsletter, script. Length control (short/medium/long), tone override, generation history.", "POST /api/content/generate, GET /api/content/history"),
    ("Vibe Coding App Builder", "Chat-based full-stack app generation. Each message: intent analysis -> code generation (HTML/CSS/JS/Tailwind) -> live iframe preview -> iterative refinement -> download. Persistent projects.", "POST /api/vibe/projects, POST /api/vibe/projects/{id}/chat, GET .../preview"),
    ("Agent Activity Monitor (WebSocket)", "Real-time dashboard via WebSocket (/api/ws/activity, 8s updates). Shows: agent status with completion rates, inter-agent communication flows, task dependency graph, recent tool executions. REST fallback polling at 10s.", "WS /api/ws/activity, GET /api/enterprise/activity/live"),
    ("Simulation vs. Execution Mode", "System-wide toggle. Simulation (default): agents return descriptive responses, no external APIs called. Execution: real Gmail sends, Calendar events, API calls. Confirmation prompt before mode switch.", "GET/PUT /api/enterprise/system/mode"),
    ("Real-World Action Layer", "Google Suite integration (Gmail + Calendar) via OAuth 2.0. All actions gated by system mode. Personal Secretary as execution bridge. Full action logging.", "GET /api/oauth/gmail/login, POST /api/actions/send-email, POST /api/actions/create-event"),
    ("Flexible LLM Configuration", "13 providers, 45+ models. Users choose preferred model in Settings. Override priority: Agent brain profile > User default > LLM Router auto-selection.", "PUT /api/users/me/config"),
    ("Voice Command Interface", "Mic button in Command Palette captures audio (WebM via MediaRecorder), transcribes via OpenAI Whisper, auto-fills search for hands-free navigation across pages, agents, and actions.", "POST /api/voice/transcribe"),
    ("Admin Code Explorer", "Full codebase browser: recursive file tree, code viewer with line numbers and language detection, file search, copy-to-clipboard, ZIP download of entire codebase. Admin-only with path traversal protection.", "GET /api/admin/code/tree, /file, /search, /export"),
    ("Memory Governance", "CRUD with versioning (every update creates version). Relevance scoring: time-decay (30-day half-life) + access frequency + importance weight. Auto-pruning with dry-run preview. 500-entry limit. Stats dashboard.", "POST/GET/PUT/DELETE /api/memory/entries, POST /api/memory/prune, GET /api/memory/stats"),
    ("Agent Memory Auto-Learning", "GPT-4o-mini extracts 1-3 key learnings from every completed task. Categories: fact, preference, instruction, context, decision. Near-duplicate detection. Async execution (never blocks task completion).", "Auto-triggered by orchestration_service.py and agent_service.py"),
    ("Command Palette", "VS Code-style quick search (press / or Cmd+K). Searches 50+ pages, 458+ agents, and quick actions. Keyboard navigation, recent searches in localStorage, voice integration via mic button.", "Frontend-only (uses /api/agents/public for agent data)"),
]

PROVIDERS = [
    ("OpenAI", EMERALD, [("GPT-5.2", "Flagship", "$2.50/$10"), ("GPT-4o", "Fast", "$2.50/$10"), ("GPT-4o Mini", "Economy", "$0.15/$0.60"), ("O3", "Reasoning", "$10/$40"), ("O3 Mini", "Reasoning", "$1.10/$4.40"), ("GPT Image 1", "Image", "$0.02/img"), ("Sora 2", "Video", "$0.10/sec"), ("Whisper", "STT", "Included")]),
    ("Anthropic", ORANGE, [("Claude Sonnet 4.5", "Flagship", "$3/$15"), ("Claude Opus 4.5", "Premium", "$15/$75"), ("Claude Haiku 4.5", "Economy", "$0.80/$4")]),
    ("Google Gemini", BLUE, [("Gemini 3 Flash", "Fast", "$0.075/$0.30"), ("Gemini 3 Pro", "Flagship", "$1.25/$5"), ("Nano Banana 2", "Image", "$0.02/img")]),
    ("xAI (Grok)", SKY, [("Grok 3", "Flagship", "$3/$15"), ("Grok 3 Mini", "Economy", "$0.30/$0.50"), ("Grok 2", "Fast", "$2/$10")]),
    ("DeepSeek", TEAL, [("DeepSeek Chat", "Economy", "$0.14/$0.28"), ("DeepSeek Reasoner", "Reasoning", "$0.55/$2.19")]),
    ("Mistral AI", AMBER, [("Mistral Large", "Flagship", "$2/$6"), ("Mistral Medium", "Fast", "$0.40/$2"), ("Mistral Small", "Economy", "$0.10/$0.30")]),
    ("Perplexity", INDIGO, [("Sonar", "Search", "$1/$1"), ("Sonar Pro", "Research", "$3/$15")]),
    ("Cohere", PINK, [("Command R+", "Flagship", "$2.50/$10"), ("Command R", "Economy", "$0.15/$0.60")]),
    ("ElevenLabs", ROSE, [("Multilingual v2", "Voice", "$0.30/1K ch"), ("Turbo v2.5", "Voice", "$0.18/1K ch")]),
    ("Groq", AMBER, [("Llama 4 Scout", "Fast", "$0.11/$0.34"), ("Llama 4 Maverick", "Flagship", "$0.50/$0.77"), ("Llama 3.3 70B", "Economy", "$0.59/$0.79")]),
    ("Together AI", GREEN, [("Llama 4 Maverick FP8", "Flagship", "$0.27/$0.85"), ("Llama 3.3 70B Turbo", "Fast", "$0.88/$0.88"), ("DeepSeek R1", "Reasoning", "$3/$7")]),
    ("Fireworks AI", ORANGE, [("Llama 4 Scout", "Fast", "$0.15/$0.60"), ("Llama 4 Maverick", "Flagship", "$0.50/$0.77"), ("DeepSeek V3", "Economy", "$0.56/$1.88")]),
    ("AI21", INDIGO, [("Jamba Large 1.7", "Flagship", "$2/$8"), ("Jamba Mini 1.7", "Economy", "$0.20/$0.40")]),
]

TIER_MAP = {"Flagship": AMBER, "Fast": CYAN, "Economy": EMERALD, "Premium": VIOLET, "Reasoning": ROSE, "Search": SKY, "Research": INDIGO, "Image": PINK, "Video": RED, "Voice": ORANGE, "STT": TEAL}


# ============================================================
# PDF BUILD
# ============================================================

@router.get("/summary/pdf")
async def download_summary_pdf(current_user: User = Depends(get_current_user)):
    total_tasks = await db.tasks.count_documents({})
    total_projects = await db.projects.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_memories = await db.memory_entries.count_documents({"user_id": current_user.user_id})
    auto_learned = await db.memory_entries.count_documents({"user_id": current_user.user_id, "source": "auto_learn"})

    pdf = DarkPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)

    # ===== PAGE 1: COVER PAGE =====
    pdf.add_page()

    # Decorative top bar -- gradient-like stacked bars
    bar_colors = [INDIGO, VIOLET, PINK, CYAN, EMERALD]
    for i, c in enumerate(bar_colors):
        pdf.set_fill_color(*c)
        pdf.rect(0, i * 1.5, pdf.w, 1.5, style="F")
    pdf.ln(12)

    # Side accent decoration
    pdf.set_fill_color(*INDIGO)
    pdf.rect(pdf.l_margin, 18, 2.5, 45, style="F")

    # Title block
    pdf.set_y(20)
    pdf.set_font(FN, "B", 36)
    pdf.set_text_color(*WHITE)
    pdf.set_x(pdf.l_margin + 8)
    pdf.cell(0, 16, _s("MAARS Command"))
    pdf.ln(14)

    pdf.set_font(FN, "", 12)
    pdf.set_text_color(*INDIGO)
    pdf.set_x(pdf.l_margin + 8)
    pdf.cell(0, 7, "Autonomous AI Enterprise Operating System")
    pdf.ln(8)

    pdf.set_font(FN, "", 9)
    pdf.set_text_color(*DIM)
    pdf.set_x(pdf.l_margin + 8)
    pdf.cell(0, 5, "by MAARS Global Corporation")
    pdf.ln(8)

    # Divider
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.15)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # Description
    pdf.set_font(FN, "", 9)
    pdf.set_text_color(*LIGHT)
    pdf.set_x(pdf.l_margin + 2)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 4, 4.5, _s(
        "MAARS Command deploys a workforce of 458+ specialized AI agents organized across 27 network categories "
        "and 16 system layers, powered by 13 LLM providers with 45+ models. It merges the power of preset "
        "specialist business agents with autonomous execution, persistent memory, and real-world action capabilities. "
        "Users set high-level business goals, and the AI workforce autonomously plans, delegates, executes, "
        "collaborates, and delivers -- with quality control, failure recovery, and human oversight at every step."
    ))
    pdf.ln(5)

    # Badge pills -- two rows
    bx = pdf.l_margin + 2
    by = pdf.get_y()
    for i, (color, label) in enumerate(BADGE_COLORS):
        tw = pdf.badge_pill(bx, by, label, color)
        bx += tw + 3
        if bx > pdf.w - 50:
            bx = pdf.l_margin + 2
            by += 8
    pdf.set_y(by + 12)

    # Stat cards row
    card_w = (pdf.w - 2 * pdf.l_margin - 4 * 4) / 5
    cx = pdf.l_margin
    cy = pdf.get_y()
    for num, label, color in STAT_CARDS:
        pdf.stat_card(cx, cy, card_w, 28, num, label, color)
        cx += card_w + 4
    pdf.set_y(cy + 34)

    # Table of Contents card
    toc_y = pdf.get_y()
    toc_h = 58
    pdf.dark_card(pdf.l_margin, toc_y, pdf.w - pdf.l_margin - pdf.r_margin, toc_h, INDIGO)
    pdf.set_xy(pdf.l_margin + 6, toc_y + 3)
    pdf.set_font(FN, "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, "Table of Contents")
    pdf.ln(1)

    toc_items = [
        ("1", "Platform Statistics", EMERALD),
        ("2", "The 458-Agent AI Workforce (8 Layers)", AMBER),
        ("3", f"Core Systems & Capabilities ({len(SYSTEMS)} Systems)", CYAN),
        ("4", f"AI Models & Providers ({len(PROVIDERS)} Providers)", VIOLET),
        ("5", "Technical Architecture", PINK),
        ("6", "Complete API Reference (212+ Endpoints)", SKY),
    ]
    pdf.ln(1)
    for num, name, color in toc_items:
        pdf.set_x(pdf.l_margin + 8)
        pdf.set_font(FN, "B", 9.5)
        pdf.set_text_color(*color)
        pdf.cell(9, 6.5, num + ".")
        pdf.set_font(FN, "", 9.5)
        pdf.set_text_color(*WHITE)
        pdf.cell(0, 6.5, _s(name), new_x="LMARGIN", new_y="NEXT")

    # Footer branding on cover
    pdf.set_y(pdf.h - 25)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.15)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)
    pdf.set_font(FN, "B", 7)
    pdf.set_text_color(*DIM)
    pdf.cell(0, 4, f"Generated {datetime.now(timezone.utc).strftime('%B %d, %Y')}  |  Confidential  |  MAARS Global Corporation", align="C")

    # ===== SECTION 1: STATISTICS =====
    pdf.add_page()
    pdf.section_title("1. Platform Statistics", EMERALD)

    # Stats in a card
    stats_data = [
        ("AI Agents", "458+", INDIGO), ("Organizational Layers", "8", AMBER),
        ("Core Systems", str(len(SYSTEMS)), EMERALD), ("AI Providers", str(len(PROVIDERS)), VIOLET),
        ("AI Models Available", "30+", CYAN), ("API Endpoints", "212+", SKY),
        ("Frontend Pages", "20+", PINK), ("Database Collections", "27+", ORANGE),
        ("Total Projects", str(total_projects), LIGHT), ("Total Tasks Executed", str(total_tasks), LIGHT),
        ("Chat Conversations", str(total_chats), LIGHT),
        ("Memory Entries", f"{total_memories} ({auto_learned} auto-learned)", LIGHT),
    ]
    card_y = pdf.get_y()
    card_h = len(stats_data) * 5.8 + 6
    pdf.dark_card(pdf.l_margin, card_y, pdf.w - pdf.l_margin - pdf.r_margin, card_h, EMERALD)
    pdf.set_y(card_y + 3)
    for label, value, color in stats_data:
        pdf.set_font(FN, "", 8.5)
        pdf.set_text_color(*DIM)
        pdf.set_x(pdf.l_margin + 6)
        pdf.cell(65, 5.8, _s(label))
        pdf.set_font(FN, "B", 8.5)
        pdf.set_text_color(*color)
        pdf.cell(0, 5.8, _s(str(value)), new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(card_y + card_h + 4)

    # ===== SECTION 2: AGENTS =====
    pdf.add_page()
    pdf.section_title("2. The 458-Agent AI Workforce", AMBER)
    pdf.body("Each agent has a unique identity and Custom Brain Profile: LLM model, autonomy level (1-10), communication style, tool permissions, and creativity temperature. Organized into 8 enterprise layers.")
    pdf.ln(2)

    for layer_name, count, agents in AGENT_LAYERS:
        layer_color = LAYER_COLORS.get(layer_name, LIGHT)

        # Layer header card
        pdf._ensure_space(14)
        lh_y = pdf.get_y()
        pdf.set_fill_color(layer_color[0] // 5, layer_color[1] // 5, layer_color[2] // 5)
        pdf.rect(pdf.l_margin, lh_y, pdf.w - pdf.l_margin - pdf.r_margin, 8.5, style="F")
        pdf.set_fill_color(*layer_color)
        pdf.rect(pdf.l_margin, lh_y, 2.5, 8.5, style="F")
        pdf.set_xy(pdf.l_margin + 6, lh_y + 1)
        pdf.set_font(FN, "B", 10)
        pdf.set_text_color(*layer_color)
        pdf.cell(0, 6, _s(f"{layer_name}  ({count} agents)"))
        pdf.set_y(lh_y + 10)

        for name, role, model, desc, caps in agents:
            pdf._ensure_space(20)
            # Agent entry with left accent
            ay = pdf.get_y()
            pdf.set_fill_color(*CARD_BG)
            card_w_full = pdf.w - pdf.l_margin - pdf.r_margin - 4
            pdf.rect(pdf.l_margin + 4, ay, card_w_full, 0.3, style="F")
            pdf.set_fill_color(*BORDER)
            pdf.rect(pdf.l_margin + 4, ay, card_w_full, 0.1, style="F")

            # Agent name and role
            pdf.set_xy(pdf.l_margin + 6, ay + 1)
            pdf.set_font(FN, "B", 8.5)
            pdf.set_text_color(*WHITE)
            pdf.cell(0, 4.5, _s(name))
            pdf.set_x(pdf.l_margin + 6 + pdf.get_string_width(name) + 3)
            pdf.set_font(FN, "", 7)
            pdf.set_text_color(*layer_color)
            pdf.cell(20, 4.5, _s(f"[{role}]"))
            pdf.set_text_color(*DIM)
            pdf.cell(0, 4.5, _s(f"Default: {model}"))
            pdf.ln(5)

            # Description
            pdf.set_font(FN, "", 7.5)
            pdf.set_text_color(*LIGHT)
            pdf.set_x(pdf.l_margin + 6)
            pdf.multi_cell(card_w_full - 4, 3.8, _s(desc))

            # Capabilities
            pdf.set_font(FN, "", 6.5)
            pdf.set_text_color(*DIM)
            pdf.set_x(pdf.l_margin + 6)
            pdf.multi_cell(card_w_full - 4, 3.5, _s(f"Capabilities: {caps}"))
            pdf.ln(2.5)

        pdf.ln(3)

    # ===== SECTION 3: SYSTEMS =====
    pdf.add_page()
    pdf.section_title(f"3. Core Systems & Capabilities ({len(SYSTEMS)} Systems)", CYAN)
    pdf.body("These are the engines powering MAARS Command. Each system has its own data model, API endpoints, and configuration.")
    pdf.ln(2)

    for i, (name, desc, endpoints) in enumerate(SYSTEMS):
        sys_color = SYSTEM_COLORS[i % len(SYSTEM_COLORS)]

        # System card
        # Estimate height for content
        pdf._ensure_space(28)
        sy = pdf.get_y()

        # System number + name
        pdf.set_fill_color(sys_color[0] // 5, sys_color[1] // 5, sys_color[2] // 5)
        pdf.rect(pdf.l_margin, sy, pdf.w - pdf.l_margin - pdf.r_margin, 7, style="F")
        pdf.set_fill_color(*sys_color)
        pdf.rect(pdf.l_margin, sy, pdf.w - pdf.l_margin - pdf.r_margin, 0.8, style="F")

        pdf.set_xy(pdf.l_margin + 3, sy + 1)
        pdf.set_font(FN, "B", 9)
        pdf.set_text_color(*sys_color)
        pdf.cell(7, 5, _s(f"{i+1}."))
        pdf.set_text_color(*WHITE)
        pdf.cell(0, 5, _s(name))
        pdf.set_y(sy + 9)

        # Description
        pdf.set_font(FN, "", 8)
        pdf.set_text_color(*LIGHT)
        pdf.set_x(pdf.l_margin + 3)
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 6, 4, _s(desc))
        pdf.ln(1)

        # Endpoints
        pdf.set_font(FN, "B", 7)
        pdf.set_text_color(*sys_color)
        pdf.set_x(pdf.l_margin + 3)
        pdf.cell(18, 4, "Endpoints:")
        pdf.set_font(FN, "", 7)
        pdf.set_text_color(*DIM)
        pdf.multi_cell(0, 4, _s(endpoints))
        pdf.ln(3)

    # ===== SECTION 4: AI PROVIDERS =====
    pdf.add_page()
    pdf.section_title(f"4. AI Models & Providers ({len(PROVIDERS)} Providers)", VIOLET)
    pdf.body("13 AI providers with 45+ models for text, reasoning, search, image generation, video, voice, and speech-to-text. All accessible via Emergent Universal LLM Key or direct API keys.")
    pdf.ln(2)

    for prov_name, prov_color, models in PROVIDERS:
        pdf._ensure_space(12 + len(models) * 5.5)

        # Provider header
        py = pdf.get_y()
        pdf.set_fill_color(prov_color[0] // 5, prov_color[1] // 5, prov_color[2] // 5)
        pw = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.rect(pdf.l_margin, py, pw, 7, style="F")
        pdf.set_fill_color(*prov_color)
        pdf.rect(pdf.l_margin, py, 2.5, 7, style="F")

        pdf.set_xy(pdf.l_margin + 6, py + 1)
        pdf.set_font(FN, "B", 10)
        pdf.set_text_color(*prov_color)
        pdf.cell(0, 5, _s(f"{prov_name}  ({len(models)} models)"))
        pdf.set_y(py + 9)

        # Table header
        pdf.set_fill_color(*CARD_BG)
        hdr_y = pdf.get_y()
        pdf.rect(pdf.l_margin + 2, hdr_y, pw - 4, 5, style="F")
        pdf.set_font(FN, "B", 7)
        pdf.set_text_color(*DIM)
        pdf.set_x(pdf.l_margin + 5)
        pdf.cell(55, 5, "Model")
        pdf.cell(28, 5, "Tier")
        pdf.cell(0, 5, "Cost (In/Out per 1M tok)", new_x="LMARGIN", new_y="NEXT")

        # Model rows
        for j, (mname, tier, cost) in enumerate(models):
            pdf._ensure_space(5.5)
            ry = pdf.get_y()
            # Alternating row
            if j % 2 == 0:
                pdf.set_fill_color(15, 15, 20)
                pdf.rect(pdf.l_margin + 2, ry, pw - 4, 5, style="F")

            pdf.set_font(FN, "", 8)
            pdf.set_text_color(*WHITE)
            pdf.set_x(pdf.l_margin + 5)
            pdf.cell(55, 5, _s(mname))
            # Tier badge
            tc = TIER_MAP.get(tier, LIGHT)
            pdf.set_text_color(*tc)
            pdf.set_font(FN, "B", 7.5)
            pdf.cell(28, 5, _s(tier))
            pdf.set_text_color(*DIM)
            pdf.set_font(FN, "", 7.5)
            pdf.cell(0, 5, _s(cost), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # ===== SECTION 5: ARCHITECTURE =====
    pdf.add_page()
    pdf.section_title("5. Technical Architecture", PINK)

    arch_sections = [
        ("Backend Stack", ROSE, [
            "FastAPI (Python 3.11) -- async/await, high-performance ASGI",
            "MongoDB -- 27+ collections (agents, tasks, projects, chats, memories...)",
            "WebSocket -- real-time Activity Monitor streaming (8s updates)",
            "JWT authentication with admin role detection",
            "Emergent Integrations SDK -- unified 9-provider LLM access",
            "Background tasks via asyncio.create_task (non-blocking)",
            "StreamingResponse for ZIP/PDF file downloads",
        ]),
        ("Frontend Stack", CYAN, [
            "React 18 with hooks and Context API",
            "Tailwind CSS with custom dark theme",
            "Shadcn/UI component library (Button, Card, Badge, etc.)",
            "React Router v6 with protected and admin routes",
            "DashboardLayout -- single resizable sidebar for all 20+ pages",
            "Command Palette with voice integration",
            "WebSocket client with REST fallback",
        ]),
        ("AI & LLM Layer", VIOLET, [
            "13 providers: OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs, Groq, Together AI, Fireworks AI, AI21",
            "45+ models: text, reasoning, search, image, video, voice, STT",
            "Model-Agnostic LLM Router (auto-selects optimal model)",
            "Quality Control Critic Module (GPT-4o, 1-10 scoring)",
            "Failure Recovery (GPT-5.2 -> Claude -> Gemini -> GPT-4o)",
            "Memory Auto-Learning (GPT-4o-mini knowledge extraction)",
            "Universal Emergent LLM Key (single key, all providers)",
        ]),
        ("Database (27+ Collections)", AMBER, [
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
    ]

    for section_name, section_color, items in arch_sections:
        pdf._ensure_space(12 + len(items) * 5)
        ay = pdf.get_y()
        # Section card
        card_h = 8 + len(items) * 4.5 + 3
        pdf.dark_card(pdf.l_margin, ay, pdf.w - pdf.l_margin - pdf.r_margin, card_h, section_color)

        pdf.set_xy(pdf.l_margin + 6, ay + 2)
        pdf.set_font(FN, "B", 10)
        pdf.set_text_color(*section_color)
        pdf.cell(0, 5, _s(section_name))
        pdf.set_y(ay + 9)

        for item in items:
            pdf.set_font(FN, "", 7.5)
            pdf.set_text_color(*LIGHT)
            x_start = pdf.l_margin + 8
            iy = pdf.get_y()
            pdf.colored_dot(pdf.l_margin + 6, iy + 1.8, 0.7, section_color)
            pdf.set_x(x_start)
            pdf.multi_cell(pdf.w - x_start - pdf.r_margin - 4, 4.5, _s(item))

        pdf.set_y(ay + card_h + 5)

    # ===== SECTION 6: API REFERENCE =====
    pdf.add_page()
    pdf.section_title("6. Complete API Reference (212+ Endpoints)", SKY)
    pdf.body("All endpoints require JWT auth (Authorization: Bearer <token>) unless noted. Admin endpoints require is_admin=true.")
    pdf.ln(2)

    api_groups = [
        ("Authentication", EMERALD, ["POST /api/auth/register", "POST /api/auth/login", "GET /api/auth/me", "GET /api/stats"]),
        ("Agents (41)", INDIGO, ["GET /api/agents/public", "GET/POST /api/agents", "GET /api/agents/{id}", "POST /api/agents/{id}/chat", "GET/PUT/DELETE /api/agents/{id}/brain"]),
        ("Projects & Orchestration", ROSE, ["POST /api/projects", "GET /api/projects", "POST /api/projects/{id}/execute", "GET /api/projects/{id}", "PATCH/DELETE /api/projects/{id}"]),
        ("Tasks", AMBER, ["GET /api/tasks", "POST /api/tasks", "PATCH /api/tasks/{id}", "POST /api/tasks/{id}/execute"]),
        ("Enterprise", CYAN, ["POST/GET/PATCH /api/collaborations", "GET /api/enterprise/kpis", "GET /api/enterprise/activity/live", "WS /api/ws/activity", "GET/PUT /api/enterprise/system/mode", "POST /api/enterprise/quality/review", "POST /api/enterprise/router/route-task"]),
        ("Memory", VIOLET, ["POST/GET /api/memory/entries", "PUT/DELETE /api/memory/entries/{id}", "GET /api/memory/entries/{id}/versions", "POST /api/memory/prune", "GET /api/memory/stats"]),
        ("Content & Intelligence", PINK, ["POST /api/reference/analyze", "GET /api/reference/blueprints", "POST /api/content/generate", "GET /api/content/history"]),
        ("Vibe Coding", GREEN, ["POST /api/vibe/projects", "GET /api/vibe/projects", "POST /api/vibe/projects/{id}/chat", "GET /api/vibe/projects/{id}/preview"]),
        ("Voice & Code Explorer", SKY, ["POST /api/voice/transcribe", "GET /api/admin/code/tree", "GET /api/admin/code/file", "GET /api/admin/code/search", "GET /api/admin/code/export", "GET /api/summary/pdf"]),
        ("Real-World Actions", ORANGE, ["GET /api/oauth/gmail/login", "GET /api/oauth/gmail/callback", "POST /api/actions/send-email", "POST /api/actions/create-event"]),
        ("Teams", TEAL, ["POST /api/teams", "GET /api/teams", "POST /api/teams/{id}/invite", "PUT /api/teams/{id}/members/{uid}", "POST /api/chats/{id}/share"]),
        ("Billing", EMERALD, ["GET /api/plans", "GET /api/subscription", "POST /api/checkout", "GET /api/credits"]),
        ("Admin (30+)", RED, ["GET /api/admin/stats", "GET /api/admin/users", "GET /api/admin/analytics", "GET /api/admin/profit", "GET /api/admin/audit-log", "GET /api/admin/agent-performance"]),
    ]

    for section_name, section_color, endpoints in api_groups:
        pdf._ensure_space(8 + len(endpoints) * 4.5)
        gy = pdf.get_y()

        # Group header
        pdf.colored_dot(pdf.l_margin + 2, gy + 2.5, 1.5, section_color)
        pdf.set_x(pdf.l_margin + 6)
        pdf.set_font(FN, "B", 9)
        pdf.set_text_color(*section_color)
        pdf.cell(0, 5, _s(section_name))
        pdf.ln(6)

        for ep in endpoints:
            pdf._ensure_space(5)
            pdf.set_font(FN, "", 7.5)
            pdf.set_text_color(*LIGHT)
            pdf.set_x(pdf.l_margin + 8)
            # Color the HTTP method
            parts = ep.split(" ", 1)
            if len(parts) == 2:
                method, path = parts
                method_colors = {"GET": EMERALD, "POST": INDIGO, "PUT": AMBER, "PATCH": ORANGE, "DELETE": ROSE, "WS": CYAN}
                # Handle compound methods like GET/POST
                pdf.set_font(FN, "B", 7)
                mc = INDIGO
                for m in method_colors:
                    if m in method:
                        mc = method_colors[m]
                        break
                pdf.set_text_color(*mc)
                pdf.cell(38, 4, _s(method))
                pdf.set_font(FN, "", 7.5)
                pdf.set_text_color(*LIGHT)
                pdf.cell(0, 4, _s(path), new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 4, _s(ep), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ===== END PAGE =====
    pdf.add_page()
    pdf.ln(30)

    # Centered end decoration
    pdf.accent_divider(INDIGO)
    pdf.ln(5)

    # End card
    ey = pdf.get_y()
    ew = 100
    ex = (pdf.w - ew) / 2
    pdf.dark_card(ex, ey, ew, 30, INDIGO)
    pdf.set_xy(ex, ey + 5)
    pdf.set_font(FN, "B", 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(ew, 8, "MAARS Command", align="C")
    pdf.set_xy(ex, ey + 15)
    pdf.set_font(FN, "", 8)
    pdf.set_text_color(*DIM)
    pdf.cell(ew, 5, "End of Documentation", align="C")
    pdf.set_xy(ex, ey + 21)
    pdf.set_font(FN, "", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(ew, 4, _s(f"Generated {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}"), align="C")

    pdf.set_y(ey + 40)
    pdf.accent_divider(VIOLET)

    # Bottom branding bars
    for i, c in enumerate(bar_colors):
        pdf.set_fill_color(*c)
        pdf.rect(0, pdf.h - 7.5 + i * 1.5, pdf.w, 1.5, style="F")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=MAARS-Command-Documentation.pdf"})
