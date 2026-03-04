"""Comprehensive MAARS Command System Documentation PDF Generator.

Generates a detailed, multi-section PDF covering every feature, system,
agent, API endpoint, and architectural detail of the platform.
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


def _s(text):
    """Sanitize text for Helvetica font (strip unsupported unicode)."""
    return (str(text).replace("\u2013", "-").replace("\u2014", "--").replace("\u2018", "'")
            .replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2192", "->").replace("\u2026", "...").replace("\u2022", "-")
            .replace("\u00a0", " "))


class DocPDF(FPDF):
    """Custom PDF with professional MAARS Command branding."""

    def header(self):
        if self.page_no() == 1:
            return  # Title page has custom header
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(140, 140, 140)
        self.cell(0, 6, "MAARS Command - Comprehensive System Documentation", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(79, 70, 229)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_line_width(0.2)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(140, 140, 140)
        ts = datetime.now(timezone.utc).strftime("%B %d, %Y")
        self.cell(self.w / 2 - self.l_margin, 8, f"Generated {ts}")
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="R")

    # --- Formatting Helpers ---

    def h1(self, text):
        self.ln(5)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(79, 70, 229)
        self.set_x(self.l_margin)
        self.multi_cell(0, 8, _s(text))
        self.set_draw_color(79, 70, 229)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.l_margin + 55, self.get_y())
        self.set_line_width(0.2)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def h2(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(50, 50, 50)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, _s(text))
        self.ln(1)

    def h3(self, text):
        self.ln(1)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(70, 70, 70)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5, _s(text))

    def p(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(60, 60, 60)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, _s(text))
        self.ln(1.5)

    def b(self, text):
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(70, 70, 70)
        self.set_x(self.l_margin + 4)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 4, 4.2, _s("- " + text))

    def kv(self, key, value):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.set_x(self.l_margin + 4)
        self.cell(50, 5, _s(key))
        self.set_font("Helvetica", "", 9)
        self.set_text_color(79, 70, 229)
        self.cell(0, 5, _s(str(value)), new_x="LMARGIN", new_y="NEXT")

    def row3(self, c1, c2, c3, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 8)
        self.set_text_color(60, 60, 60)
        self.set_x(self.l_margin + 2)
        self.cell(65, 4.5, _s(c1))
        self.set_text_color(34, 139, 34) if not bold else None
        self.cell(35, 4.5, _s(c2))
        self.set_text_color(200, 140, 0) if not bold else None
        self.cell(0, 4.5, _s(c3), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(60, 60, 60)

    def sep(self):
        self.set_draw_color(220, 220, 220)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)


# ============================================================
# DATA
# ============================================================

AGENT_DETAILS = [
    {
        "layer": "Executive Layer",
        "desc": "The strategic command center. These agents handle high-level planning, goal decomposition, and organization-wide strategy. Commander Orion leads the entire AI workforce.",
        "agents": [
            ("Commander Orion", "Commander", "gpt-5.2",
             "The supreme orchestrator of the AI workforce. When given a business goal, Commander Orion analyzes it, decomposes it into 3-7 actionable sub-tasks, assigns each to the most appropriate specialist agent, sets priorities and timelines, and compiles the final deliverable. It coordinates multi-step projects involving 5-15 agents simultaneously.",
             ["Task Delegation", "Strategic Planning", "Team Orchestration", "Goal Breakdown", "Multi-Agent Coordination"]),
            ("Chief Strategy Officer (Victor Ashford)", "Strategist", "gpt-5.2",
             "Analyzes markets, competitors, and opportunities to develop winning strategies. Creates SWOT analyses, business plans, market entry strategies, and growth roadmaps. Thinks several moves ahead with data-backed recommendations.",
             ["Business Strategy", "Competitive Analysis", "Market Research", "Business Planning", "Growth Strategy"]),
            ("Revenue Strategist", "Revenue", "gpt-5.2",
             "Focuses on monetization modeling, pricing strategy, revenue optimization, and financial growth. Designs pricing tiers, subscription models, upsell strategies, and revenue forecasts based on market data.",
             ["Revenue Optimization", "Pricing Strategy", "Monetization", "Financial Forecasting"]),
            ("Investor Relations", "Investor Relations", "gpt-5.2",
             "Manages investor communications, prepares pitch decks, fundraising materials, financial reports, and quarterly updates. Expert in startup fundraising language, VC expectations, and financial storytelling.",
             ["Investor Communications", "Fundraising", "Pitch Decks", "Financial Reporting"]),
            ("Business Strategist", "Business Strategy", "gpt-5.2",
             "Specializes in market positioning, business model innovation, and go-to-market strategy. Creates detailed market analyses and strategic recommendations for product launches and market expansion.",
             ["Market Positioning", "Business Models", "GTM Strategy", "Strategic Planning"]),
        ],
    },
    {
        "layer": "Product & Technical Layer",
        "desc": "The engineering and product backbone. These agents build, automate, optimize, and secure the technical infrastructure.",
        "agents": [
            ("Product Manager", "PM", "gpt-5.2",
             "Creates product roadmaps, writes user stories, prioritizes features using frameworks like RICE/MoSCoW, conducts sprint planning, and manages the product lifecycle from ideation to launch.",
             ["Product Roadmaps", "Feature Prioritization", "User Stories", "Sprint Planning"]),
            ("Project Manager", "PM", "gpt-5.2",
             "Manages timelines, resources, and milestones. Creates Gantt charts, tracks dependencies, identifies blockers, and ensures projects are delivered on time and within budget.",
             ["Timeline Management", "Resource Allocation", "Risk Management", "Milestone Tracking"]),
            ("App Developer (Kai Nakamoto)", "Developer", "gpt-5.2",
             "Full-stack coding expert proficient in React, Node.js, Python, TypeScript, and modern frameworks. Builds web apps, mobile apps, APIs, and full-stack solutions with clean, production-ready code.",
             ["Web Development", "Mobile Apps", "API Development", "React/Node.js", "Full-Stack"]),
            ("Automation Engineer", "Automation", "gpt-5.2",
             "Designs and implements workflow automation, CI/CD pipelines, process optimization, and integration scripts. Reduces manual work through intelligent automation.",
             ["Workflow Automation", "CI/CD Pipelines", "Process Optimization", "Integration Scripts"]),
            ("AI Optimizer", "AI Specialist", "gpt-4o",
             "Tunes ML models, optimizes AI performance, monitors costs, and ensures the AI layer runs efficiently. Specializes in prompt engineering, model selection, and cost-performance tradeoffs.",
             ["ML Model Tuning", "Performance Optimization", "Cost Monitoring", "Prompt Engineering"]),
            ("Data Engineer", "Data Engineering", "gpt-5.2",
             "Builds data pipelines, ETL processes, database architectures, and data warehouses. Ensures clean, reliable data flows throughout the organization.",
             ["Data Pipelines", "ETL", "Database Architecture", "Data Warehousing"]),
            ("Cybersecurity Officer", "Security", "gpt-5.2",
             "Conducts security audits, vulnerability assessments, penetration testing planning, and compliance checks. Implements security best practices and incident response plans.",
             ["Security Audits", "Vulnerability Assessments", "Compliance", "Incident Response"]),
        ],
    },
    {
        "layer": "Creative & Brand Layer",
        "desc": "The creative powerhouse. These agents handle all visual, written, and brand-related content creation with a focus on aesthetics and conversion.",
        "agents": [
            ("Brand Architect", "Brand Strategy", "gpt-5.2", "Develops brand identity systems, positioning strategies, visual language guidelines, and brand voice documentation. Creates comprehensive brand books and style guides.", ["Brand Identity", "Positioning", "Visual Language", "Brand Books"]),
            ("Graphics Designer", "Visual Design", "gpt-5.2", "Creates images, visual assets, marketing materials, infographics, and social media graphics. Expert in composition, color theory, and visual storytelling.", ["Image Creation", "Visual Assets", "Infographics", "Social Graphics"]),
            ("Video Specialist", "Video Production", "gpt-5.2", "Plans video content, writes scripts, creates storyboards, and manages video production workflows. Specializes in YouTube, TikTok, and social media video formats.", ["Video Scripts", "Storyboarding", "Motion Graphics", "Social Video"]),
            ("Copywriter (Scarlett Monroe)", "Content Writing", "gpt-5.2", "Crafts persuasive sales copy, website content, product descriptions, email sequences, and headlines that convert. Master of AIDA, PAS, and other copywriting frameworks.", ["Sales Copy", "Website Content", "Product Descriptions", "Email Sequences"]),
            ("Web Designer (Luna Bergstrom)", "Web Design", "gpt-5.2", "Creates wireframes, designs landing pages, develops UI/UX concepts, chooses color palettes, selects typography, and crafts conversion-focused designs.", ["UI/UX Design", "Wireframing", "Landing Pages", "Visual Design"]),
            ("UX Researcher", "User Research", "gpt-5.2", "Conducts user testing, creates journey maps, performs usability analyses, and develops persona profiles. Ensures products are built around real user needs.", ["User Testing", "Journey Mapping", "Usability Analysis", "Persona Development"]),
            ("3D Specialist", "3D Design", "gpt-5.2", "Creates 3D models, product visualizations, immersive content, and AR/VR experiences. Expert in spatial design and interactive 3D.", ["3D Modeling", "Product Visualization", "AR/VR", "Immersive Content"]),
        ],
    },
    {
        "layer": "Growth & Marketing Layer",
        "desc": "The growth engine. These agents drive customer acquisition, retention, and revenue growth through marketing, sales, and public relations.",
        "agents": [
            ("Marketing Specialist (Zara Mitchell)", "Marketing", "gpt-5.2", "Creates campaigns, social media content, ad copy, and brand messaging. Understands consumer psychology, viral content, and conversion optimization.", ["Campaign Strategy", "Performance Marketing", "Ad Copy", "Audience Targeting"]),
            ("Growth Hacker", "Growth", "gpt-5.2", "Designs viral loops, A/B tests, conversion funnels, and growth experiments. Data-driven approach to finding scalable growth channels.", ["Viral Loops", "A/B Testing", "Conversion Optimization", "Growth Experiments"]),
            ("SEO Specialist", "SEO", "gpt-5.2", "Performs keyword research, on-page/off-page optimization, technical SEO audits, and content strategy for organic search growth.", ["Keyword Research", "On-Page SEO", "Technical SEO", "Content Strategy"]),
            ("Social Media Manager", "Social Media", "gpt-5.2", "Manages platform strategy, community engagement, content calendars, and social listening. Expert in TikTok, Instagram, LinkedIn, Twitter/X algorithms.", ["Platform Strategy", "Community Management", "Content Calendars", "Social Listening"]),
            ("Email Marketing", "Email", "gpt-5.2", "Creates drip campaigns, newsletters, segmentation strategies, and automated email flows. Expert in deliverability, open rates, and conversion.", ["Drip Campaigns", "Newsletters", "Segmentation", "Automated Flows"]),
            ("Sales Representative", "Sales", "gpt-5.2", "Qualifies leads, creates outreach sequences, manages pipeline analysis, and develops sales scripts. Expert in B2B and B2C sales methodologies.", ["Lead Qualification", "Outreach Sequences", "Pipeline Analysis", "Sales Scripts"]),
            ("PR Manager", "Public Relations", "gpt-5.2", "Manages media relations, writes press releases, handles crisis communications, and develops thought leadership content.", ["Media Relations", "Press Releases", "Crisis Communications", "Thought Leadership"]),
        ],
    },
    {
        "layer": "Operations Layer",
        "desc": "The operational backbone. These agents ensure smooth day-to-day operations, resource management, and customer satisfaction.",
        "agents": [
            ("Operations Manager", "Operations", "gpt-5.2", "Optimizes processes, allocates resources, and improves operational efficiency. Creates SOPs, workflow diagrams, and capacity plans.", ["Process Optimization", "Resource Allocation", "SOPs", "Capacity Planning"]),
            ("Inventory Manager", "Inventory", "gpt-5.2", "Manages stock levels, supply chain optimization, demand forecasting, and warehouse logistics. Prevents stockouts and overstock situations.", ["Stock Management", "Supply Chain", "Demand Forecasting", "Logistics"]),
            ("Procurement Manager", "Procurement", "gpt-5.2", "Handles vendor management, cost negotiation, sourcing strategies, and procurement workflows. Optimizes spend while maintaining quality.", ["Vendor Management", "Cost Negotiation", "Sourcing", "Procurement"]),
            ("HR Specialist", "HR", "gpt-5.2", "Manages recruitment, onboarding, culture development, performance reviews, and HR policy creation. Builds high-performing teams.", ["Recruitment", "Onboarding", "Culture Development", "Performance Reviews"]),
            ("Customer Service Agent", "Support", "gpt-5.2", "Resolves tickets, manages FAQs, handles customer complaints, and ensures satisfaction. Expert in de-escalation and proactive support.", ["Ticket Resolution", "FAQ Management", "Customer Satisfaction", "De-escalation"]),
            ("CX Architect", "Customer Experience", "gpt-5.2", "Optimizes customer journeys, improves NPS scores, designs loyalty programs, and creates delightful experiences across touchpoints.", ["Journey Optimization", "NPS Improvement", "Loyalty Programs", "CX Design"]),
        ],
    },
    {
        "layer": "Finance Layer",
        "desc": "The financial intelligence center. These agents handle financial modeling, analytics, and business intelligence.",
        "agents": [
            ("Financial Analyst", "Finance", "gpt-5.2", "Creates financial models, forecasts, budgets, and P&L analyses. Expert in DCF valuations, scenario planning, and financial reporting.", ["Financial Modeling", "Forecasting", "Budgeting", "Valuation"]),
            ("Data Analyst", "Analytics", "gpt-5.2", "Builds dashboards, analyzes trends, creates visualizations, and provides data-driven insights for business decisions.", ["Business Intelligence", "Dashboards", "Trend Analysis", "Data Visualization"]),
        ],
    },
    {
        "layer": "Governance Layer",
        "desc": "The compliance and ethics backbone. These agents ensure the organization operates within legal, regulatory, and ethical boundaries.",
        "agents": [
            ("Legal Assistant", "Legal", "gpt-5.2", "Reviews contracts, conducts legal research, checks compliance, and drafts legal documents. Identifies risks and provides recommendations.", ["Contract Review", "Legal Research", "Compliance", "Document Drafting"]),
            ("Compliance Officer", "Compliance", "gpt-5.2", "Ensures regulatory adherence, prepares for audits, monitors policy changes, and maintains compliance frameworks.", ["Regulatory Adherence", "Audit Preparation", "Policy Monitoring", "Frameworks"]),
            ("Ethics Officer", "Ethics", "gpt-5.2", "Governs ethical AI usage, detects bias, ensures fair practices, and maintains responsible AI guidelines.", ["Ethical AI", "Bias Detection", "Fair Practices", "Responsible AI"]),
        ],
    },
    {
        "layer": "Intelligence Layer",
        "desc": "The knowledge and research engine. These agents gather intelligence, manage knowledge, and enable global operations.",
        "agents": [
            ("Research Specialist", "Research", "gpt-5.2", "Conducts deep research, competitive analysis, trend forecasting, and market intelligence. Produces comprehensive research reports.", ["Deep Research", "Competitive Analysis", "Trend Forecasting", "Market Intelligence"]),
            ("Knowledge Architect", "Knowledge", "gpt-5.2", "Curates knowledge bases, designs taxonomies, organizes information architecture, and builds institutional memory systems.", ["Knowledge Base", "Taxonomy Design", "Information Architecture", "Institutional Memory"]),
            ("Localization Specialist", "Localization", "gpt-5.2", "Handles translation, cultural adaptation, market-specific content, and multi-language communications. Supports 50+ languages.", ["Translation", "Cultural Adaptation", "Multi-Language", "Market Content"]),
            ("Personal Secretary (Nadia Kessler)", "Executive Assistant", "gpt-5.2", "Manages calendars, schedules appointments, drafts emails, handles to-do lists, and serves as the bridge for real-world action execution. Receives Commander results and executes communications.", ["Calendar Management", "Email Drafting", "Scheduling", "Action Execution", "Commander Handoff"]),
        ],
    },
]

SYSTEMS_DETAILED = [
    {
        "name": "1. Autonomous Orchestration Engine",
        "what": "The core execution engine of MAARS Command. When a user sets a business goal, the system autonomously plans, delegates, executes, and delivers results without manual intervention.",
        "how": "Commander Orion receives the goal and performs: (a) Goal Scoring -- evaluates complexity, scope, and required expertise on a 1-10 scale. (b) Strategic Planning -- decomposes the goal into 3-7 milestones, each with specific tasks. (c) Agent Assignment -- matches each task to the optimal specialist agent based on role, capabilities, and workload. (d) Parallel Execution -- tasks are executed concurrently where dependencies allow, with the orchestration service managing the execution order. (e) Result Compilation -- all task outputs are collected, reviewed for quality, and compiled into a unified deliverable.",
        "config": "Users can set autonomy level (1-10) per agent: Level 1 = every action needs approval, Level 10 = fully autonomous. System Mode (Simulation/Execution) controls whether real-world actions are triggered.",
        "data": "Projects stored in 'projects' collection with: project_id, title, goal, status (planned/in_progress/completed/failed), milestones, tasks, total_cost, created_at. Tasks in 'tasks' collection with: task_id, agent_id, status, result, quality_score, quality_verdict.",
        "endpoints": "POST /api/projects (create), GET /api/projects (list), POST /api/projects/{id}/execute (run), GET /api/projects/{id} (detail), PATCH /api/projects/{id} (update), DELETE /api/projects/{id} (remove).",
    },
    {
        "name": "2. Custom Brain Profiles",
        "what": "Every one of the 41 agents has a fully configurable 'brain' that determines how it thinks, communicates, and operates. This allows fine-tuning agent behavior for specific business contexts.",
        "how": "Each brain profile contains: (a) Model Selection -- choose which LLM powers the agent (GPT-5.2, Claude Sonnet 4.5, Gemini 3, etc.). (b) Autonomy Level -- 1-10 scale controlling how much freedom the agent has. (c) Communication Style -- formal, casual, technical, creative, or custom. (d) Creativity Temperature -- 0.0 (deterministic) to 1.0 (highly creative). (e) Tool Permissions -- which tools (web search, code execution, email) the agent can use. (f) Context Window -- how much conversation history the agent retains. (g) Custom Instructions -- additional system prompt overrides for specialized behavior.",
        "config": "Brain profiles are stored per-user, allowing each user to customize the same agent differently. Profiles persist across sessions.",
        "data": "Stored in 'agent_brains' collection: user_id, agent_id, model_provider, model_name, autonomy_level, comm_style, temperature, tools, context_window, custom_instructions.",
        "endpoints": "GET /api/agents/{id}/brain (read), PUT /api/agents/{id}/brain (update), DELETE /api/agents/{id}/brain (reset), GET /api/brain-profiles (list all).",
    },
    {
        "name": "3. Quality Control & Failure Recovery",
        "what": "An automated quality assurance system that reviews every task output and automatically recovers from failures by retrying with different LLM models.",
        "how": "After every task completion: (a) Critic Module -- a separate GPT-4o instance reviews the output on a 1-10 scale evaluating accuracy, completeness, relevance, and quality. Scores 8+ are 'excellent', 5-7 are 'acceptable', below 5 'needs revision'. (b) Failure Recovery -- if a task fails or scores below threshold, the system automatically retries using a fallback chain: GPT-5.2 -> Claude Sonnet 4.5 -> Gemini 2.5 Pro -> GPT-4o. (c) Escalation -- if all fallbacks fail, the task is escalated to the Commander, then to the user for manual intervention.",
        "config": "Quality thresholds configurable: excellent >= 8, acceptable >= 5, needs_revision < 5. Fallback chain can be customized per project.",
        "data": "Reviews stored in 'quality_reviews' collection: review_id, task_id, score, verdict, feedback, model_used. History queryable via /api/enterprise/quality/history.",
        "endpoints": "POST /api/enterprise/quality/review (trigger), GET /api/enterprise/quality/history (list), POST /api/enterprise/quality/retry (manual retry).",
    },
    {
        "name": "4. Model-Agnostic LLM Router",
        "what": "An intelligent routing system that analyzes every incoming task and automatically selects the optimal LLM model based on complexity, cost, speed requirements, and the user's preferences.",
        "how": "The router performs: (a) Task Classification -- analyzes content for complexity signals: coding keywords, reasoning indicators, creative language, data tasks, legal terms, or simple queries. Produces a complexity score and category. (b) Tier Selection -- maps complexity to tiers: Premium (complex tasks -> GPT-5.2, Claude Sonnet), Standard (moderate -> GPT-4o, Gemini Flash), Economy (simple -> GPT-4o Mini, Claude Haiku). (c) Model Matching -- within the selected tier, matches the task's category (coding/reasoning/creative) to model strengths. (d) User Override -- if the user has a preferred model set in Settings, that takes priority unless the router detects a significant mismatch.",
        "config": "Users can set preferred model in Settings -> AI Configuration. Router logs all decisions for transparency.",
        "data": "Routing logs in 'routing_logs' collection: task content, complexity score, selected model, reasoning, timestamp.",
        "endpoints": "POST /api/enterprise/router/route-task (route), GET /api/enterprise/router/history (log).",
    },
    {
        "name": "5. Autonomous Collaboration Engine",
        "what": "Enables agents to automatically detect when they need input from other agents and initiate cross-domain collaboration without human intervention.",
        "how": "After each task completion in a project, the system: (a) Domain Analysis -- maps the completing agent's role to one of 9 domains (strategy, marketing, technical, creative, finance, operations, legal, research, support). (b) Dependency Detection -- analyzes the task result for keywords and patterns indicating cross-domain needs (e.g., a marketing task mentioning 'legal review' triggers Legal Assistant). (c) Auto-Collaboration -- creates a collaboration request with objective, context, and required output, sends it to the appropriate agent(s), and waits for response. (d) Result Integration -- collaboration outputs are merged back into the project workflow.",
        "config": "Collaboration can be set to auto (fully autonomous) or approval-required (user must approve before cross-agent communication happens).",
        "data": "Collaborations in 'collaborations' collection: collab_id, sender, receivers, objective, context, status (pending/in_progress/completed), response.",
        "endpoints": "POST /api/collaborations (create), GET /api/collaborations (list), PATCH /api/collaborations/{id} (update), GET /api/enterprise/collaboration/log (history).",
    },
    {
        "name": "6. Universal Reference Intelligence",
        "what": "Analyzes any reference material (text, articles, competitors' content) and extracts a structured 'Style Blueprint' that captures the reference's writing style, tone, audience, and design patterns.",
        "how": "Users provide reference text or URLs. The system: (a) Content Analysis -- uses an LLM to deeply analyze writing style (formal/casual/technical), tone (authoritative/friendly/urgent), vocabulary complexity, sentence structure patterns, and rhetorical devices. (b) Audience Profiling -- identifies the target audience, their expertise level, and communication preferences. (c) Blueprint Generation -- produces a structured JSON blueprint containing: writing_style, tone, vocabulary_level, sentence_patterns, audience_profile, content_structure, and key_phrases. (d) Storage -- blueprints are saved and can be applied to any Content Generator request.",
        "config": "Users can create multiple blueprints per different reference sources and apply them selectively.",
        "data": "Blueprints in 'style_blueprints' collection: blueprint_id, user_id, reference_text, analysis, blueprint (JSON), created_at.",
        "endpoints": "POST /api/reference/analyze (create blueprint), GET /api/reference/blueprints (list), GET /api/reference/blueprints/{id} (detail).",
    },
    {
        "name": "7. Content Generator",
        "what": "Generates on-brand content using Style Blueprints from the Reference Intelligence system. Supports 8 content types with full customization.",
        "how": "Users select a Style Blueprint and specify content type (blog post, social media, email, ad copy, product description, press release, newsletter, script). The system: (a) Blueprint Loading -- retrieves the style rules from the selected blueprint. (b) Prompt Engineering -- constructs a detailed prompt incorporating the blueprint's tone, style, vocabulary, and audience. (c) Generation -- the LLM generates content matching the reference style. (d) Length Control -- users specify short (150 words), medium (400), or long (800+) output. (e) Tone Override -- optional override of the blueprint's default tone.",
        "config": "8 content types, 3 length options, optional tone override, full generation history.",
        "data": "Generated content in 'generated_content' collection: content_id, user_id, blueprint_id, content_type, prompt, result, created_at.",
        "endpoints": "POST /api/content/generate (generate), GET /api/content/history (list past generations).",
    },
    {
        "name": "8. Vibe Coding App Builder",
        "what": "A chat-based interface for building complete web applications through natural language conversation. Users describe what they want, and the system generates a full HTML/CSS/JavaScript application.",
        "how": "Users create a 'vibe project' and chat with the system. Each message: (a) Intent Analysis -- understands what the user wants to build or change. (b) Code Generation -- produces complete, self-contained HTML with embedded Tailwind CSS and JavaScript. (c) Live Preview -- the generated code is rendered in an iframe for instant visual feedback. (d) Iterative Refinement -- users can request changes ('make the button blue', 'add a login form') and the system modifies the existing code. (e) Download -- users can download the complete application code.",
        "config": "Projects are persistent -- users can return to any vibe project and continue building.",
        "data": "Vibe projects in 'vibe_projects' collection: vibe_id, user_id, title, messages (chat history), latest_code, created_at.",
        "endpoints": "POST /api/vibe/projects (create), GET /api/vibe/projects (list), POST /api/vibe/projects/{id}/chat (send message), GET /api/vibe/projects/{id}/preview (render), DELETE /api/vibe/projects/{id}.",
    },
    {
        "name": "9. Agent Activity Monitor (WebSocket)",
        "what": "A real-time dashboard that displays the entire AI workforce's activity, communication flows, task dependencies, and tool executions with live streaming updates.",
        "how": "The monitor operates in two modes: (a) WebSocket Live Mode -- connects to /api/ws/activity with token authentication. Receives full activity snapshots every 8 seconds including: agent status (active/idle with task counts and completion rates), inter-agent communication flows (sender -> receiver with objectives and status), task dependency graph (task status across projects), and recent tool executions with timing data. The client can send 'ping' for health checks or 'refresh' for immediate updates. (b) REST Fallback Mode -- if WebSocket is unavailable, the monitor falls back to polling GET /api/enterprise/activity/live every 10 seconds.",
        "config": "Users can toggle between Live (WebSocket) and Paused modes. Connection status is displayed: 'WebSocket Live' (green), 'Polling' (amber), or 'Paused' (gray).",
        "data": "Aggregated from tasks, collaborations, and tool_calls collections in real-time. No separate storage.",
        "endpoints": "WS /api/ws/activity (WebSocket), GET /api/enterprise/activity/live (REST fallback).",
    },
    {
        "name": "10. Simulation vs. Execution Mode",
        "what": "A system-wide safety toggle that controls whether agents can perform real-world actions (send emails, create calendar events, make API calls) or only simulate them.",
        "how": "A single toggle switches the entire platform: (a) Simulation Mode (default) -- agents process requests normally but return simulated responses for any real-world action. Email sends return 'Email would be sent to X'. Calendar events return 'Event would be created'. No external APIs are called. (b) Execution Mode -- agents perform actual real-world actions: emails are sent via Gmail, calendar events are created via Google Calendar, and other integrations execute live. A confirmation prompt appears before mode switch.",
        "config": "Toggle via PUT /api/enterprise/system/mode. Affects all agents for all users simultaneously.",
        "data": "Current mode stored in 'system_config' collection. Mode change events logged for audit.",
        "endpoints": "GET /api/enterprise/system/mode (read), PUT /api/enterprise/system/mode (toggle).",
    },
    {
        "name": "11. Real-World Action Layer",
        "what": "Enables agents to execute real-world actions through Google Suite integration (Gmail + Google Calendar) via OAuth 2.0, with all actions gated by the Simulation/Execution mode.",
        "how": "The Personal Secretary (Nadia Kessler) serves as the primary execution bridge: (a) Gmail Integration -- send emails, read inbox, compose drafts. OAuth 2.0 flow for user authentication. (b) Calendar Integration -- create events, check availability, manage schedules. (c) Action Gating -- every real-world action checks the system mode before executing. In Simulation mode, actions return descriptive responses without external calls. In Execution mode, actual API calls are made. (d) Logging -- all actions (simulated or real) are logged with timestamps and results.",
        "config": "Users must complete Google OAuth flow to connect their accounts. Disconnect available via /api/oauth/gmail/disconnect.",
        "data": "OAuth tokens stored securely in 'oauth_tokens' collection. Action logs in 'action_logs'.",
        "endpoints": "GET /api/oauth/gmail/login (initiate OAuth), GET /api/oauth/gmail/callback (complete), GET /api/oauth/gmail/status (check), POST /api/actions/send-email, POST /api/actions/create-event, POST /api/actions/test.",
    },
    {
        "name": "12. Flexible LLM Configuration",
        "what": "Allows users to choose their preferred AI model from 9 providers and 30+ models. The selection applies to all AI features unless overridden by the LLM Router or agent-specific brain profiles.",
        "how": "In Settings, users can: (a) Select Provider -- choose from OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, or AI Generation services. (b) Select Model -- each provider offers multiple models at different price/performance tiers. (c) Apply -- the selection is stored in the user's config and used as the default for all AI operations. (d) Override Priority -- Agent brain profiles override user default, and the LLM Router can override both if it detects a significant mismatch for task requirements.",
        "config": "Stored per-user in 'users' collection: preferred_provider, preferred_model.",
        "data": "User preferences in 'users' collection. Model usage logged in 'usage_logs'.",
        "endpoints": "PUT /api/users/me/config (update preference), GET /api/users/me (read). Admin: GET /api/admin/api-keys, PUT /api/admin/api-keys.",
    },
    {
        "name": "13. Voice Command Interface",
        "what": "Enables hands-free interaction with the entire MAARS Command platform through voice commands. Users speak into their microphone, and the system transcribes their speech into text for instant navigation and actions.",
        "how": "A microphone button in the Command Palette: (a) Recording -- captures audio via the browser's MediaRecorder API in WebM format. Visual feedback shows recording state (pulsing red). (b) Transcription -- the audio is sent to POST /api/voice/transcribe, which uses OpenAI Whisper (via Emergent SDK) to convert speech to text. (c) Auto-Fill -- the transcribed text automatically populates the Command Palette search input, triggering instant search across pages, agents, and actions. (d) Execution -- users can speak a page name ('Dashboard'), an agent name ('Commander Orion'), or an action ('New Project') and navigate directly.",
        "config": "Requires browser microphone permission. Works in all modern browsers supporting MediaRecorder API.",
        "data": "No persistent storage -- transcriptions are ephemeral and used only for the current search.",
        "endpoints": "POST /api/voice/transcribe (upload audio, receive text).",
    },
    {
        "name": "14. Admin Code Explorer",
        "what": "A full codebase browser for admin users that provides read-only access to the entire application source code directly within the MAARS Command UI.",
        "how": "The Code Explorer provides: (a) File Tree -- recursive directory listing of backend/ and frontend/src/ with expand/collapse, file counts per directory, and file sizes. Language-specific colored icons for Python, JavaScript, JSON, HTML, CSS, etc. (b) Code Viewer -- click any file to view its full content with line numbers, language detection, file metadata (name, path, lines, size), and a copy-to-clipboard button. (c) File Search -- type in the search box to find files by name across the entire codebase (max 50 results). (d) Code Download -- a 'Download Code' button generates and downloads a ZIP archive of the entire codebase (backend + frontend), excluding node_modules, __pycache__, .git, and upload directories.",
        "config": "Admin-only access (403 for non-admin users). Path traversal protection prevents accessing files outside /app.",
        "data": "No database storage -- reads directly from the filesystem.",
        "endpoints": "GET /api/admin/code/tree (file tree), GET /api/admin/code/file?path=X (read file), GET /api/admin/code/search?q=X (search), GET /api/admin/code/export (download ZIP).",
    },
    {
        "name": "15. Memory Governance",
        "what": "A complete memory management system that allows users and agents to create, version, score, and prune memory entries. Memories represent accumulated institutional knowledge that makes agents progressively smarter.",
        "how": "The system provides: (a) CRUD Operations -- create memory entries with content, category (fact/preference/instruction/context/decision), importance (0-1), tags, and optional agent association. (b) Version History -- every update creates a new version with the previous content preserved. Users can view the full version timeline with update reasons. (c) Relevance Scoring -- each entry gets a dynamic relevance score calculated using: time-decay (30-day half-life, newer = more relevant), access frequency (more accesses = higher score), and importance weight (user-set priority). Formula: score = decay * importance + min(access_count * 0.05, 0.5). (d) Auto-Pruning -- identifies entries below a relevance threshold (default 0.15) and offers dry-run preview before deletion. (e) Statistics -- dashboard showing total entries, usage percentage (500 max), average relevance, low-relevance count, category breakdown, and agent breakdown.",
        "config": "Max 500 entries per user. Relevance half-life: 30 days. Prune threshold: configurable (default 0.15).",
        "data": "Stored in 'memory_entries' collection: memory_id, user_id, agent_id, category, content, importance, access_count, version, versions[], tags, source, created_at.",
        "endpoints": "POST /api/memory/entries (create), GET /api/memory/entries (list with scores), PUT /api/memory/entries/{id} (update+version), DELETE /api/memory/entries/{id}, GET /api/memory/entries/{id}/versions (history), POST /api/memory/prune (prune), GET /api/memory/stats.",
    },
    {
        "name": "16. Agent Memory Auto-Learning",
        "what": "An automated knowledge extraction system that captures learnings from every completed task and stores them as memory entries, creating an ever-growing institutional knowledge base.",
        "how": "When any agent completes a task (via project orchestration or commander delegation): (a) Extraction -- GPT-4o-mini analyzes the task result and extracts 1-3 key learnings that are genuinely useful for future work. Each learning includes: content (1-2 sentences), category (fact/preference/instruction/context/decision), importance (0-1), summary (3-5 words), and tags. (b) Duplicate Detection -- before saving, the system checks if a similar memory already exists (first 40 characters match) to prevent redundancy. (c) Storage -- entries are saved with source='auto_learn', the source task title, project ID, and quality score. (d) Async Execution -- the learning process runs as a background task (asyncio.create_task) and never blocks or slows down task completion.",
        "config": "Automatic -- no user configuration needed. Max 3 learnings per task. Respects the 500-entry memory limit.",
        "data": "Same 'memory_entries' collection with source='auto_learn' and additional fields: source_task_title, source_project_id, quality_score.",
        "endpoints": "No dedicated endpoint -- triggered automatically by orchestration_service.py and agent_service.py. Viewable via GET /api/memory/entries (filter by source).",
    },
    {
        "name": "17. Command Palette",
        "what": "A VS Code/Notion-style quick search interface for instant navigation to any page, agent, or action in the platform. Accessible via the '/' keyboard shortcut or the sidebar search button.",
        "how": "The Command Palette provides: (a) Global Search -- searches across 20+ pages, 41 agents, and quick actions simultaneously. Fuzzy matching ensures partial searches work. (b) Categorized Results -- results are grouped into: Recent (last 10 searches from localStorage), Pages (all navigable pages), Agents (all 41 agents with roles), and Quick Actions (New Project, New Task, etc.). (c) Keyboard Navigation -- full keyboard support: up/down arrows to navigate, Enter to select, Escape to close. (d) Voice Integration -- a microphone button in the search bar enables voice input via the Voice Command Interface. (e) Search Persistence -- recent searches are stored in localStorage for quick re-access.",
        "config": "Triggered by: pressing '/', clicking sidebar search button, or Cmd+K. Persists recent searches in browser localStorage.",
        "data": "No backend storage -- frontend-only with localStorage for recents.",
        "endpoints": "No backend endpoint -- purely frontend component using existing /api/agents/public for agent data.",
    },
]

AI_PROVIDERS = [
    ("OpenAI", "The foundational AI provider. Industry-leading models for coding, reasoning, and general intelligence.",
     [("GPT-5.2", "Flagship", "$2.50 / $10.00 per 1M tok", "Most capable model -- excels at complex coding, multi-step analysis, and creative work"),
      ("GPT-4o", "Fast", "$2.50 / $10.00 per 1M tok", "Balanced speed and quality for everyday tasks"),
      ("GPT-4o Mini", "Economy", "$0.15 / $0.60 per 1M tok", "Ultra cost-efficient for simple queries and summaries"),
      ("O3", "Reasoning", "$10.00 / $40.00 per 1M tok", "Specialized for math, logic, and multi-step reasoning problems"),
      ("O3 Mini", "Reasoning", "$1.10 / $4.40 per 1M tok", "Lightweight reasoning at lower cost"),
      ("GPT Image 1", "Image Gen", "$0.02/image", "Text-to-image generation for marketing and design assets"),
      ("Sora 2", "Video Gen", "$0.10/second", "AI video generation from text prompts (4-12 second clips)"),
      ("Whisper", "STT", "Included", "Speech-to-text transcription in 50+ languages"),
     ]),
    ("Anthropic", "Known for safety-focused AI and exceptional creative writing quality.",
     [("Claude Sonnet 4.5", "Flagship", "$3.00 / $15.00 per 1M tok", "Excellent for creative writing, nuanced analysis, and legal review"),
      ("Claude Opus 4.5", "Premium", "$15.00 / $75.00 per 1M tok", "Deepest research and most complex analysis"),
      ("Claude Haiku 4.5", "Economy", "$0.80 / $4.00 per 1M tok", "Fast responses, summaries, and simple tasks"),
     ]),
    ("Google Gemini", "Multimodal AI with strong reasoning and data analysis capabilities.",
     [("Gemini 3 Flash", "Fast", "$0.075 / $0.30 per 1M tok", "Lightning-fast responses at minimal cost"),
      ("Gemini 3 Pro", "Flagship", "$1.25 / $5.00 per 1M tok", "Advanced multimodal research and analysis"),
      ("Nano Banana 2", "Image Gen", "$0.02/image", "Gemini-powered image generation"),
     ]),
    ("xAI (Grok)", "High-context models with 1M token windows and strong reasoning.",
     [("Grok 3", "Flagship", "$3.00 / $15.00 per 1M tok", "1M context window, excellent reasoning"),
      ("Grok 3 Mini", "Economy", "$0.30 / $0.50 per 1M tok", "Cost-efficient reasoning"),
      ("Grok 2", "Fast", "$2.00 / $10.00 per 1M tok", "Competitive general-purpose model"),
     ]),
    ("DeepSeek", "Ultra-affordable models with strong performance-to-cost ratio.",
     [("DeepSeek Chat", "Economy", "$0.14 / $0.28 per 1M tok", "128K context, extremely cost-efficient"),
      ("DeepSeek Reasoner", "Reasoning", "$0.55 / $2.19 per 1M tok", "Deep math and logic reasoning"),
     ]),
    ("Mistral AI", "European AI provider with enterprise-grade security and multilingual excellence.",
     [("Mistral Large", "Flagship", "$2.00 / $6.00 per 1M tok", "Complex reasoning, enterprise-grade"),
      ("Mistral Medium", "Fast", "$0.40 / $2.00 per 1M tok", "Balanced performance for most tasks"),
      ("Mistral Small", "Economy", "$0.10 / $0.30 per 1M tok", "Ultra-fast for simple tasks"),
     ]),
    ("Perplexity", "Search-augmented AI with real-time web grounding and citations.",
     [("Sonar", "Search", "$1.00 / $1.00 per 1M tok + $5/1K searches", "Web-grounded answers with citations"),
      ("Sonar Pro", "Research", "$3.00 / $15.00 per 1M tok + $5/1K searches", "Deep web research with comprehensive citations"),
     ]),
    ("Cohere", "Enterprise RAG specialist with strong embedding and retrieval capabilities.",
     [("Command R+", "Flagship", "$2.50 / $10.00 per 1M tok", "Retrieval-augmented generation and enterprise tasks"),
      ("Command R", "Economy", "$0.15 / $0.60 per 1M tok", "Cost-efficient for summaries and simple retrieval"),
     ]),
    ("ElevenLabs (Voice)", "Industry-leading text-to-speech with natural, expressive voices.",
     [("Multilingual v2", "Voice", "$0.30/1K chars", "Natural multilingual TTS (Bangla, English, etc.)"),
      ("Turbo v2.5", "Voice", "$0.18/1K chars", "Fastest TTS for real-time applications"),
     ]),
]


@router.get("/summary/pdf")
async def download_summary_pdf(current_user: User = Depends(get_current_user)):
    """Generate comprehensive system documentation PDF."""

    # Live stats
    total_tasks = await db.tasks.count_documents({})
    total_projects = await db.projects.count_documents({})
    total_chats = await db.chats.count_documents({})
    total_memories = await db.memory_entries.count_documents({"user_id": current_user.user_id})
    auto_learned = await db.memory_entries.count_documents({"user_id": current_user.user_id, "source": "auto_learn"})
    total_agents_count = sum(len(layer["agents"]) for layer in AGENT_DETAILS)
    total_models = sum(len(models) for _, _, models in AI_PROVIDERS)

    pdf = DocPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ========== TITLE PAGE ==========
    pdf.add_page()
    # Title is in header for page 1
    pdf.p(
        f"MAARS Command is an Autonomous AI Enterprise Operating System that deploys "
        f"{total_agents_count} specialized AI agents organized across 8 organizational layers "
        f"with {len(SYSTEMS_DETAILED)} core systems, {total_models}+ AI models from {len(AI_PROVIDERS)} providers, "
        f"and 212+ API endpoints. This document provides a complete technical reference "
        f"covering every feature, system, agent, and capability of the platform."
    )
    pdf.ln(2)
    pdf.h2("Table of Contents")
    for i, name in enumerate([
        "Platform Statistics",
        f"The {total_agents_count}-Agent AI Workforce (8 Layers)",
        f"Core Systems & Capabilities ({len(SYSTEMS_DETAILED)} Systems)",
        f"AI Models & Providers ({len(AI_PROVIDERS)} Providers, {total_models}+ Models)",
        "Technical Architecture",
        "Complete API Reference (212+ Endpoints)",
    ], 1):
        pdf.p(f"  {i}. {name}")

    # ========== STATISTICS ==========
    pdf.add_page()
    pdf.h1("1. Platform Statistics")
    for label, value in [
        ("AI Agents", total_agents_count),
        ("Organizational Layers", 8),
        ("Core Systems", len(SYSTEMS_DETAILED)),
        ("AI Providers", len(AI_PROVIDERS)),
        ("AI Models", f"{total_models}+"),
        ("API Endpoints", "212+"),
        ("Frontend Pages", "20+"),
        ("Database Collections", "27+"),
        ("Total Projects Created", total_projects),
        ("Total Tasks Executed", total_tasks),
        ("Chat Conversations", total_chats),
        ("Memory Entries", f"{total_memories} ({auto_learned} auto-learned)"),
    ]:
        pdf.kv(label, value)

    # ========== AGENT WORKFORCE ==========
    pdf.add_page()
    pdf.h1(f"2. The {total_agents_count}-Agent AI Workforce")
    pdf.p(
        "Each agent has a unique identity, personality, and Custom Brain Profile that defines its "
        "LLM model, autonomy level, communication style, tool permissions, and creativity temperature. "
        "Agents are organized into 8 specialized layers reflecting a complete enterprise organization."
    )

    for layer_data in AGENT_DETAILS:
        pdf.h2(f"{layer_data['layer']} ({len(layer_data['agents'])} agents)")
        pdf.p(layer_data["desc"])
        for agent in layer_data["agents"]:
            name, role, model, desc, caps = agent
            pdf.h3(f"{name} [{role}]")
            pdf.p(desc)
            pdf.b(f"Default Model: {model}")
            pdf.b(f"Capabilities: {', '.join(caps)}")
            pdf.ln(1)

    # ========== CORE SYSTEMS ==========
    pdf.add_page()
    pdf.h1(f"3. Core Systems & Capabilities ({len(SYSTEMS_DETAILED)} Systems)")
    pdf.p(
        "These are the engines that power MAARS Command. Each system is a self-contained module "
        "with its own data model, API endpoints, and configuration options."
    )

    for sys in SYSTEMS_DETAILED:
        pdf.h2(sys["name"])
        pdf.h3("What It Does")
        pdf.p(sys["what"])
        pdf.h3("How It Works")
        pdf.p(sys["how"])
        pdf.h3("Configuration")
        pdf.p(sys["config"])
        pdf.h3("Data Model")
        pdf.p(sys["data"])
        pdf.h3("API Endpoints")
        pdf.p(sys["endpoints"])
        pdf.sep()

    # ========== AI PROVIDERS ==========
    pdf.add_page()
    pdf.h1(f"4. AI Models & Providers ({len(AI_PROVIDERS)} Providers, {total_models}+ Models)")
    pdf.p(
        "MAARS Command supports 9 AI providers offering text generation, reasoning, search, "
        "image generation, video generation, voice synthesis, and speech-to-text. All providers "
        "are accessible through the Emergent Universal LLM Key for unified billing, or users can "
        "configure their own API keys for direct provider access."
    )

    for provider_name, provider_desc, models in AI_PROVIDERS:
        pdf.h2(f"{provider_name} ({len(models)} models)")
        pdf.p(provider_desc)
        pdf.ln(1)
        pdf.row3("Model", "Input Cost", "Notes", bold=True)
        for name, tier, cost, desc in models:
            pdf.row3(f"{name} [{tier}]", cost, desc)
        pdf.ln(2)

    # ========== ARCHITECTURE ==========
    pdf.add_page()
    pdf.h1("5. Technical Architecture")

    pdf.h2("Backend Stack")
    for item in [
        "FastAPI (Python 3.11) -- async/await throughout, high-performance ASGI server",
        "MongoDB -- 27+ collections for agents, tasks, projects, chats, memories, etc.",
        "WebSocket support -- real-time streaming for Activity Monitor (8-second updates)",
        "JWT authentication -- secure token-based auth with admin role detection",
        "Emergent Integrations SDK -- unified access to 9+ AI providers via single key",
        "Background task execution -- asyncio.create_task for non-blocking operations",
        "File streaming -- ZIP export and PDF generation via StreamingResponse",
    ]:
        pdf.b(item)

    pdf.h2("Frontend Stack")
    for item in [
        "React 18 -- component-based UI with hooks and context API",
        "Tailwind CSS -- utility-first styling with custom dark theme",
        "Shadcn/UI -- high-quality component library (Button, Card, Badge, etc.)",
        "React Router v6 -- client-side routing with protected and admin routes",
        "DashboardLayout -- single, consistent, resizable sidebar across all 20+ pages",
        "Command Palette -- VS Code-style search with voice integration",
        "WebSocket client -- real-time activity streaming with REST fallback",
        "PDF/ZIP download -- browser-based file downloads via Blob API",
    ]:
        pdf.b(item)

    pdf.h2("AI & LLM Layer")
    for item in [
        "9 AI providers: OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs",
        "30+ models spanning text, reasoning, search, image, video, voice, and speech-to-text",
        "Model-agnostic LLM Router -- auto-selects optimal model per task",
        "Quality Control -- Critic Module (GPT-4o) auto-reviews every output on 1-10 scale",
        "Failure Recovery -- automatic fallback chain: GPT-5.2 -> Claude -> Gemini -> GPT-4o",
        "Memory Auto-Learning -- GPT-4o-mini extracts key learnings from every completed task",
        "Universal Emergent LLM Key -- single key for all providers with unified billing",
    ]:
        pdf.b(item)

    pdf.h2("Database Collections (27+)")
    for item in [
        "users, agents, agent_brains -- User accounts, agent definitions, custom brain profiles",
        "chats, messages -- Conversation history with agents",
        "tasks, projects -- Task execution and project orchestration data",
        "collaborations -- Inter-agent collaboration requests and responses",
        "quality_reviews -- Quality control scores and feedback",
        "memory_entries -- Memory governance with versioning and relevance scores",
        "vibe_projects -- Vibe Coding app builder projects and code",
        "style_blueprints, generated_content -- Reference Intelligence and Content Generator",
        "teams, team_invites -- Team management and shared resources",
        "subscriptions, transactions, usage_logs -- Billing and usage tracking",
        "routing_logs -- LLM Router decision logs",
        "oauth_tokens, action_logs -- Google OAuth and real-world action logs",
        "approvals, products -- Approval workflows and product catalog",
        "system_config -- System-wide settings (simulation/execution mode)",
    ]:
        pdf.b(item)

    # ========== API REFERENCE ==========
    pdf.add_page()
    pdf.h1("6. Complete API Reference (212+ Endpoints)")
    pdf.p(
        "MAARS Command exposes 212+ REST API endpoints and 1 WebSocket endpoint. "
        "All endpoints require JWT authentication (Authorization: Bearer <token>) unless noted. "
        "Admin endpoints require is_admin=true."
    )

    api_sections = [
        ("Authentication & Users", [
            "POST /api/auth/register -- Create new user account",
            "POST /api/auth/login -- Authenticate and receive JWT token",
            "GET /api/auth/me -- Get current user profile",
            "GET /api/stats -- User statistics dashboard",
            "GET /api/user/insights -- Personalized usage insights",
        ]),
        ("Agents (41 agents)", [
            "GET /api/agents/public -- List all 41 agents (public info)",
            "GET /api/agents -- List agents for current user",
            "GET /api/agents/{id} -- Get agent detail",
            "POST /api/agents -- Create custom agent",
            "DELETE /api/agents/{id} -- Delete custom agent",
            "GET /api/agents/tools -- List available tools",
            "GET /api/agents/{id}/brain -- Get agent brain profile",
            "PUT /api/agents/{id}/brain -- Update brain profile (model, autonomy, style, temp, tools)",
            "DELETE /api/agents/{id}/brain -- Reset to defaults",
            "GET /api/brain-profiles -- List all brain profiles",
            "POST /api/agents/{id}/chat -- Chat with agent (streaming capable)",
        ]),
        ("Projects & Orchestration", [
            "POST /api/projects -- Create autonomous project with goal",
            "GET /api/projects -- List all projects",
            "GET /api/projects/{id} -- Get project detail with tasks",
            "POST /api/projects/{id}/execute -- Execute project (triggers orchestration)",
            "PATCH /api/projects/{id} -- Update project",
            "DELETE /api/projects/{id} -- Delete project",
            "GET /api/projects/active-summary -- Summary of active projects",
            "GET /api/user/autonomy -- Get autonomy settings",
            "PUT /api/user/autonomy -- Update autonomy settings",
        ]),
        ("Tasks", [
            "GET /api/tasks -- List all tasks",
            "POST /api/tasks -- Create manual task",
            "PATCH /api/tasks/{id} -- Update task status",
            "POST /api/tasks/{id}/execute -- Execute single task",
            "DELETE /api/tasks/{id} -- Delete task",
        ]),
        ("Enterprise Features", [
            "POST /api/collaborations -- Create inter-agent collaboration",
            "GET /api/collaborations -- List collaborations",
            "PATCH /api/collaborations/{id} -- Update collaboration",
            "GET /api/enterprise/collaboration/log -- Collaboration history",
            "GET /api/enterprise/kpis -- KPI dashboard data",
            "POST /api/enterprise/kpis -- Create/update KPI",
            "GET /api/enterprise/activity/live -- Live activity feed",
            "WS /api/ws/activity -- WebSocket real-time activity (token auth)",
            "GET /api/enterprise/system/mode -- Get simulation/execution mode",
            "PUT /api/enterprise/system/mode -- Toggle system mode",
            "POST /api/enterprise/quality/review -- Trigger quality review",
            "GET /api/enterprise/quality/history -- Quality score history",
            "POST /api/enterprise/router/route-task -- LLM model routing",
            "GET /api/enterprise/router/history -- Routing decision logs",
        ]),
        ("Memory Governance", [
            "POST /api/memory/entries -- Create memory entry",
            "GET /api/memory/entries -- List entries with relevance scores",
            "PUT /api/memory/entries/{id} -- Update (creates new version)",
            "DELETE /api/memory/entries/{id} -- Delete entry",
            "GET /api/memory/entries/{id}/versions -- Version history",
            "POST /api/memory/prune -- Auto-prune (dry_run option)",
            "GET /api/memory/stats -- Usage stats",
        ]),
        ("Content & Intelligence", [
            "POST /api/reference/analyze -- Analyze reference, create Style Blueprint",
            "GET /api/reference/blueprints -- List blueprints",
            "POST /api/content/generate -- Generate styled content",
            "GET /api/content/history -- Generation history",
        ]),
        ("Vibe Coding App Builder", [
            "POST /api/vibe/projects -- Create new app project",
            "GET /api/vibe/projects -- List projects",
            "GET /api/vibe/projects/{id} -- Get project detail",
            "POST /api/vibe/projects/{id}/chat -- Send build instruction",
            "GET /api/vibe/projects/{id}/preview -- Render live preview",
            "DELETE /api/vibe/projects/{id} -- Delete project",
        ]),
        ("Voice & Code Explorer", [
            "POST /api/voice/transcribe -- Transcribe audio (Whisper)",
            "GET /api/admin/code/tree -- File tree (admin)",
            "GET /api/admin/code/file?path=X -- Read file (admin)",
            "GET /api/admin/code/search?q=X -- Search files (admin)",
            "GET /api/admin/code/export -- Download ZIP (admin)",
            "GET /api/summary/pdf -- Download this PDF",
        ]),
        ("Real-World Actions", [
            "GET /api/oauth/gmail/login -- Initiate Google OAuth",
            "GET /api/oauth/gmail/callback -- OAuth callback",
            "GET /api/oauth/gmail/status -- Connection status",
            "GET /api/oauth/gmail/disconnect -- Disconnect",
            "POST /api/actions/send-email -- Send email (gated by mode)",
            "POST /api/actions/create-event -- Create calendar event",
            "GET /api/actions/integrations -- List connected integrations",
            "POST /api/actions/test -- Test action execution",
        ]),
        ("Teams & Collaboration", [
            "POST /api/teams -- Create team",
            "GET /api/teams -- List teams",
            "POST /api/teams/{id}/invite -- Invite member",
            "POST /api/teams/invites/{id}/accept -- Accept invite",
            "PUT /api/teams/{id}/members/{uid} -- Update member role",
            "DELETE /api/teams/{id}/members/{uid} -- Remove member",
            "POST /api/chats/{id}/share -- Share chat with team",
            "GET /api/teams/{id}/shared-chats -- Team shared chats",
            "GET /api/teams/{id}/activity -- Team activity feed",
            "GET /api/teams/{id}/stats -- Team statistics",
        ]),
        ("Subscriptions & Billing", [
            "GET /api/plans -- Available subscription plans",
            "GET /api/subscription -- Current subscription",
            "POST /api/checkout -- Create Stripe checkout session",
            "GET /api/checkout/status/{id} -- Check payment status",
            "GET /api/credits -- Credit balance",
            "POST /api/webhook/stripe -- Stripe webhook handler",
        ]),
        ("Admin Panel (30+ endpoints)", [
            "GET /api/admin/stats -- Platform-wide statistics",
            "GET /api/admin/users -- User management",
            "GET /api/admin/agents -- Agent management",
            "POST /api/admin/agents -- Create agent",
            "GET /api/admin/analytics -- Comprehensive analytics",
            "GET /api/admin/api-usage -- API usage tracking",
            "GET /api/admin/profit -- Revenue and profit analysis",
            "GET /api/admin/audit-log -- System audit trail",
            "GET /api/admin/analytics/retention -- User retention",
            "GET /api/admin/analytics/projections -- Growth projections",
            "GET /api/admin/analytics/agent-leaderboard -- Top agents",
            "GET /api/admin/analytics/engagement-heatmap -- Usage patterns",
            "GET /api/admin/analytics/revenue-trends -- Revenue analysis",
            "GET /api/admin/agent-performance -- Per-agent metrics",
            "GET /api/admin/activity-feed -- Admin activity feed",
            "POST /api/admin/branding -- Update platform branding",
            "POST /api/admin/smtp-config -- Configure email settings",
        ]),
    ]

    for section_name, endpoints in api_sections:
        pdf.h2(section_name)
        for ep in endpoints:
            pdf.b(ep)
        pdf.ln(1)

    # ========== FINAL ==========
    pdf.ln(6)
    pdf.sep()
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(79, 70, 229)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 5, "End of Document")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 4.5, _s(f"Generated {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')} | MAARS Global Corporation | Confidential"))

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=MAARS-Command-Documentation.pdf"},
    )
