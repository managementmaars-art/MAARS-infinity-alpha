import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Rocket, Bot, Brain, Shield, Sparkles, Cpu, Activity, Radio, Code, Palette,
  PenTool, Gauge, Users, FileCheck, Zap, Mail, BarChart3, ChevronDown,
  ChevronRight, Globe, Lock, Eye, Target, Layers, Network, Server, Database,
  Download, Loader2, Mic, FileCode, Archive, Terminal
} from "lucide-react";

const LAYER_COLORS = {
  executive: { bg: "bg-amber-500/10", border: "border-amber-500/20", text: "text-amber-400", badge: "bg-amber-500/20 text-amber-400" },
  technical: { bg: "bg-cyan-500/10", border: "border-cyan-500/20", text: "text-cyan-400", badge: "bg-cyan-500/20 text-cyan-400" },
  creative: { bg: "bg-pink-500/10", border: "border-pink-500/20", text: "text-pink-400", badge: "bg-pink-500/20 text-pink-400" },
  marketing: { bg: "bg-green-500/10", border: "border-green-500/20", text: "text-green-400", badge: "bg-green-500/20 text-green-400" },
  operations: { bg: "bg-indigo-500/10", border: "border-indigo-500/20", text: "text-indigo-400", badge: "bg-indigo-500/20 text-indigo-400" },
  finance: { bg: "bg-emerald-500/10", border: "border-emerald-500/20", text: "text-emerald-400", badge: "bg-emerald-500/20 text-emerald-400" },
  governance: { bg: "bg-red-500/10", border: "border-red-500/20", text: "text-red-400", badge: "bg-red-500/20 text-red-400" },
  intelligence: { bg: "bg-violet-500/10", border: "border-violet-500/20", text: "text-violet-400", badge: "bg-violet-500/20 text-violet-400" },
};

const AGENT_LAYERS = [
  {
    id: "executive", label: "Executive Layer", icon: Target,
    agents: [
      { name: "Commander Orion", role: "Commander", desc: "Strategic planning, goal decomposition, workforce orchestration. Receives high-level business goals and decomposes them into structured projects with milestones and tasks." },
      { name: "Chief Strategy Officer", role: "Strategist", desc: "Long-term strategy, market analysis, competitive intelligence, and strategic roadmapping." },
      { name: "Revenue Strategist", role: "Revenue", desc: "Revenue optimization, pricing strategy, monetization modeling, and growth forecasting." },
      { name: "Investor Relations", role: "Investor Relations", desc: "Investor communications, fundraising support, financial reporting, and stakeholder management." },
      { name: "Business Strategist", role: "Business Strategy", desc: "Market positioning, business model innovation, go-to-market strategy, and competitive landscape analysis." },
    ]
  },
  {
    id: "technical", label: "Product & Technical Layer", icon: Cpu,
    agents: [
      { name: "Product Manager", role: "PM", desc: "Product roadmaps, feature prioritization, user stories, sprint planning, and cross-functional alignment." },
      { name: "Project Manager", role: "Project Management", desc: "Timeline management, resource allocation, milestone tracking, risk mitigation, and stakeholder communication." },
      { name: "App Developer", role: "Developer", desc: "Full-stack development, code generation, debugging, API design, and architecture decisions." },
      { name: "Automation Engineer", role: "Automation", desc: "Workflow automation, CI/CD pipelines, process optimization, and integration scripting." },
      { name: "AI Optimizer", role: "AI Specialist", desc: "ML model tuning, AI performance monitoring, cost optimization, and model selection strategy." },
      { name: "Data Engineer", role: "Data Engineering", desc: "Data pipelines, ETL processes, database architecture, and data quality governance." },
      { name: "Cybersecurity Officer", role: "Security", desc: "Security audits, vulnerability assessments, compliance verification, and incident response planning." },
    ]
  },
  {
    id: "creative", label: "Creative & Brand Layer", icon: Palette,
    agents: [
      { name: "Brand Architect", role: "Brand Strategy", desc: "Brand identity design, positioning strategy, visual language systems, and brand guidelines." },
      { name: "Graphics Designer", role: "Visual Design", desc: "Image creation, visual assets, marketing materials, infographics, and design systems." },
      { name: "Video Specialist", role: "Video Production", desc: "Video content creation, animation, motion graphics, storyboarding, and post-production." },
      { name: "Copywriter", role: "Content Writing", desc: "Marketing copy, brand voice development, storytelling, headlines, and editorial content." },
      { name: "Web Designer", role: "Web Design", desc: "UI/UX design, landing pages, web experiences, responsive layouts, and interaction design." },
      { name: "UX Researcher", role: "User Research", desc: "User testing, journey mapping, usability analysis, persona development, and experience audits." },
      { name: "3D Specialist", role: "3D Design", desc: "3D modeling, product visualization, immersive content, AR/VR assets, and spatial design." },
    ]
  },
  {
    id: "marketing", label: "Growth & Marketing Layer", icon: Zap,
    agents: [
      { name: "Marketing Specialist", role: "Marketing", desc: "Campaign strategy, channel planning, performance marketing, attribution, and marketing analytics." },
      { name: "Growth Hacker", role: "Growth", desc: "Viral loops, A/B testing, conversion optimization, growth experiments, and user acquisition." },
      { name: "SEO Specialist", role: "SEO", desc: "Search optimization, keyword strategy, technical SEO, link building, and SERP analysis." },
      { name: "Social Media Manager", role: "Social Media", desc: "Platform strategy, community management, content scheduling, engagement, and social analytics." },
      { name: "Email Marketing Specialist", role: "Email", desc: "Drip campaigns, newsletters, segmentation, deliverability, and email automation." },
      { name: "Sales Representative", role: "Sales", desc: "Lead qualification, outreach sequences, deal management, pipeline analysis, and CRM optimization." },
      { name: "PR Manager", role: "Public Relations", desc: "Media relations, press releases, crisis communications, thought leadership, and brand reputation." },
    ]
  },
  {
    id: "operations", label: "Operations Layer", icon: Layers,
    agents: [
      { name: "Operations Manager", role: "Operations", desc: "Process optimization, resource allocation, efficiency metrics, and operational excellence." },
      { name: "Inventory Manager", role: "Inventory", desc: "Stock management, supply chain optimization, demand forecasting, and warehouse logistics." },
      { name: "Procurement Manager", role: "Procurement", desc: "Vendor management, cost negotiation, sourcing strategy, and supplier evaluation." },
      { name: "HR Specialist", role: "Human Resources", desc: "Recruitment, onboarding, culture development, policy creation, and employee engagement." },
      { name: "Customer Service Agent", role: "Support", desc: "Ticket resolution, FAQ management, customer satisfaction, and support escalation." },
      { name: "CX Architect", role: "Customer Experience", desc: "Journey optimization, NPS improvement, experience design, and customer loyalty programs." },
    ]
  },
  {
    id: "finance", label: "Finance Layer", icon: BarChart3,
    agents: [
      { name: "Financial Analyst", role: "Finance", desc: "Financial modeling, forecasting, budgeting, P&L analysis, and investment evaluation." },
      { name: "Data Analyst", role: "Analytics", desc: "Business intelligence, dashboard creation, trend analysis, statistical modeling, and reporting." },
    ]
  },
  {
    id: "governance", label: "Governance Layer", icon: Shield,
    agents: [
      { name: "Legal Assistant", role: "Legal", desc: "Contract review, legal research, compliance checks, regulatory guidance, and risk assessment." },
      { name: "Compliance Officer", role: "Compliance", desc: "Regulatory adherence, audit preparation, policy enforcement, and compliance training." },
      { name: "Ethics Officer", role: "Ethics", desc: "Ethical AI governance, bias detection, responsible practices, and ethical review protocols." },
    ]
  },
  {
    id: "intelligence", label: "Intelligence Layer", icon: Globe,
    agents: [
      { name: "Research Specialist", role: "Research", desc: "Deep research, competitive analysis, academic papers, market intelligence, and trend forecasting." },
      { name: "Knowledge Architect", role: "Knowledge Management", desc: "Knowledge base curation, taxonomy design, information architecture, and organizational learning." },
      { name: "Localization Specialist", role: "Localization", desc: "Translation, cultural adaptation, market-specific content, and international go-to-market." },
      { name: "Personal Secretary", role: "Executive Assistant", desc: "Scheduling, email drafting, meeting preparation, and real-world action execution bridge." },
    ]
  },
];

const SYSTEMS = [
  {
    icon: Rocket, title: "Autonomous Orchestration Engine", color: "text-red-400",
    desc: "The core brain of MAARS Command. When you set a high-level business goal, Commander Orion analyzes it, scores its clarity and complexity, then creates a structured strategic plan with milestones and tasks. Each task is automatically assigned to the most qualified specialist agent. The system executes tasks in parallel across milestones, with built-in quality control and failure recovery.",
    details: ["Goal Scoring: clarity, complexity, risk, confidence metrics", "Strategic plan generation with milestones and tasks", "Auto-assignment based on agent specialization", "Parallel execution with progress tracking", "Media generation (images via GPT Image 1, videos via Sora 2)", "Commander to Personal Secretary handoff for real-world actions"]
  },
  {
    icon: Brain, title: "Custom Brain Profiles", color: "text-violet-400",
    desc: "Every agent has a configurable brain profile that controls its behavior. You can fine-tune each agent's primary LLM model, autonomy level (1-10), communication style, available tools, creativity temperature, max tokens, and context window. This allows dynamic configuration without changing core logic.",
    details: ["Per-agent LLM model selection (GPT-5.2, Claude, Gemini, etc.)", "Autonomy Level: 1 (always ask) to 10 (fully autonomous)", "Communication styles: professional, casual, technical, creative", "Tool permissions: web browsing, image gen, code execution, etc.", "Creativity temperature: 0.0 deterministic to 1.0 highly creative"]
  },
  {
    icon: Shield, title: "Quality Control & Failure Recovery", color: "text-emerald-400",
    desc: "After every task completion, an automated Critic Module (powered by GPT-4o) reviews the output and scores it on a 1-10 scale for completeness, accuracy, actionability, and professionalism. If a task fails, the system automatically retries with fallback models. If all retries fail, it escalates to the user.",
    details: ["Critic Module: GPT-4o auto-reviews every task output", "Scoring: 1-10 on multiple quality dimensions", "Retry chain: GPT-5.2 → Claude Sonnet → Gemini Pro → GPT-4o", "Escalation: Failed tasks notify the user for manual review", "Quality Dashboard: pass rates, average scores, recovery metrics"]
  },
  {
    icon: Network, title: "Model-Agnostic LLM Router", color: "text-cyan-400",
    desc: "An intelligent routing system that analyzes task complexity and automatically selects the optimal LLM model. Simple queries get routed to fast, cheap models. Complex coding or legal tasks get premium models. The router considers task type (coding, creative, data, legal, reasoning), agent role, and content length.",
    details: ["Premium Tier: GPT-5.2, Claude Sonnet 4.5, Gemini 2.5 Pro (complex tasks)", "Standard Tier: GPT-4o, GPT-4.1, Gemini 3 Flash (moderate tasks)", "Economy Tier: GPT-4o-mini, Gemini Flash, Claude Haiku (simple tasks)", "User override: manually select a model in Settings", "Routing logs: model usage distribution, cost tracking"]
  },
  {
    icon: Activity, title: "Autonomous Collaboration Engine", color: "text-indigo-400",
    desc: "When an agent completes a task, the system automatically detects if the work impacts agents in related domains and creates collaboration entries. All 41 agents are mapped to 9 organizational domains with cross-domain trigger rules. This ensures seamless coordination without manual intervention.",
    details: ["9 domains: executive, product, technical, creative, marketing, operations, finance, governance, intelligence", "Auto-detection: marketing → creative + technical, product → technical + creative + marketing", "Collaboration types: information sharing, review request, data handoff, coordination", "Up to 3 auto-collaborations per task to avoid noise"]
  },
  {
    icon: Palette, title: "Universal Reference Intelligence", color: "text-pink-400",
    desc: "Analyzes text references (marketing copy, brand voice, articles) and images (visual style, brand detection) to extract structured 'Style Blueprints'. These blueprints capture writing style, tone, target audience, visual elements, color palettes, and design patterns from any reference material.",
    details: ["Text analysis: writing style, tone, messaging patterns, brand voice", "Image analysis: brand detection, visual style, emotional tone, design patterns", "Style Blueprint output for reuse in Content Generator", "History tracking of all analyses"]
  },
  {
    icon: PenTool, title: "Content Generator", color: "text-amber-400",
    desc: "Generates on-brand content using Style Blueprints from Reference Intelligence. Select a content type (marketing copy, social posts, emails, blog articles, ad copy, press releases, brand guidelines), optionally apply a Style Blueprint for tone matching, and describe what you need.",
    details: ["8 content types: marketing copy, social, email, blog, ads, press, brand guides, custom", "Blueprint integration: matches extracted tone and style exactly", "Length control: short (100-200 words), medium (300-500), long (800-1500)", "Optional tone override for specific variations", "Full history with copy/delete functionality"]
  },
  {
    icon: Code, title: "Vibe Coding App Builder", color: "text-green-400",
    desc: "Chat-based full-stack application generation. Describe an app you want to build, and the AI generates a complete working HTML/CSS/JavaScript application with Tailwind CSS. You can iteratively modify the app through conversation, preview it live in an iframe, view the code, and download files.",
    details: ["Conversational interface for app building", "Single HTML file generation with inline CSS/JS", "Tailwind CSS via CDN for modern design", "Live preview in iframe", "Iterative modifications via chat", "Code view and file download"]
  },
  {
    icon: Radio, title: "Agent Activity Monitor (WebSocket)", color: "text-blue-400",
    desc: "Real-time dashboard showing the entire AI workforce in action via live WebSocket streaming (8-second updates). Visualizes agent status, communication flows, task dependency graphs, and tool executions. Falls back to REST polling when WebSocket is unavailable.",
    details: ["WebSocket connection with token authentication", "8-second periodic updates with full activity snapshots", "Live/Paused toggle and manual refresh", "Connection status indicator: WebSocket Live / Polling / Paused", "Communication flow visualization: sender to receiver mapping", "Task dependency graph with status tracking", "Recent tool executions with response times"]
  },
  {
    icon: Lock, title: "Simulation vs. Execution Mode", color: "text-orange-400",
    desc: "A system-wide toggle that controls whether agents can perform real-world actions. In Simulation Mode (default), all external actions return simulated responses — safe for testing and review. In Execution Mode, agents send real emails, create actual calendar events, and post to live platforms.",
    details: ["System-wide toggle accessible from KPI Dashboard", "Simulation: all actions return safe, simulated responses", "Execution: real Gmail sends, real Calendar events, real API calls", "Visual indicators throughout the UI for current mode"]
  },
  {
    icon: Globe, title: "Real-World Action Layer", color: "text-teal-400",
    desc: "Enables agents to execute real-world actions through API integrations. Currently supports Google Suite (Gmail + Calendar) via OAuth 2.0. Actions are strictly gated by the Simulation/Execution mode toggle. The Personal Secretary agent acts as the final execution bridge.",
    details: ["Google Suite: Gmail (send email) + Calendar (create event)", "OAuth 2.0 flow for secure user authorization", "Connect/disconnect from Settings page", "Integration status and action testing endpoints"]
  },
  {
    icon: Server, title: "Flexible LLM Configuration", color: "text-purple-400",
    desc: "Users can choose their preferred AI model provider and model from Settings. The selection applies to all AI features including Content Generator, Vibe Coding, Reference Intelligence, and agent task execution (unless the LLM Router auto-selects).",
    details: ["OpenAI: GPT-5.2, GPT-5.1, GPT-4.1, GPT-4o, o3, o4-mini", "Anthropic: Claude Sonnet 4.5, Claude 4 Sonnet, Claude Haiku 4.5", "Google Gemini: Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash", "Powered by Emergent LLM Key (universal key across all providers)"]
  },
  {
    icon: Mic, title: "Voice Command Interface", color: "text-rose-400",
    desc: "Enables hands-free interaction with the entire MAARS Command platform. A microphone button in the Command Palette records audio, transcribes it using OpenAI Whisper, and automatically fills the search input for instant navigation and actions.",
    details: ["Browser MediaRecorder API captures audio in WebM format", "OpenAI Whisper transcription via Emergent SDK", "Auto-fills Command Palette search for voice-based navigation", "Visual states: idle, recording (pulse), transcribing (spinner)", "Voice hint displayed in Command Palette footer"]
  },
  {
    icon: FileCode, title: "Admin Code Explorer", color: "text-sky-400",
    desc: "A full codebase browser for admin users, accessible from the sidebar. Browse the entire file tree, view any file with syntax-aware display, search files by name, and download the complete codebase as a ZIP archive.",
    details: ["Recursive file tree with expand/collapse and file counts", "Code viewer with line numbers, language detection, and copy button", "File search across all directories", "ZIP export: Download entire codebase (backend + frontend)", "Language-colored icons for Python, JS, JSON, HTML, CSS, etc.", "Admin-only access with path traversal protection"]
  },
  {
    icon: Archive, title: "Memory Governance", color: "text-violet-400",
    desc: "A complete memory management system for the AI workforce. Create, edit, version, and prune memory entries with time-decay relevance scoring. Memories represent accumulated institutional knowledge that makes agents progressively smarter.",
    details: ["Full CRUD for memory entries with category tagging", "Version history tracking with update reasons", "Time-decay relevance scoring (30-day half-life) + access frequency + importance", "Auto-pruning with dry-run preview for low-relevance entries", "Usage statistics: total entries, avg relevance, category breakdown", "500-entry limit per user with usage percentage tracking"]
  },
  {
    icon: Sparkles, title: "Agent Memory Auto-Learning", color: "text-cyan-400",
    desc: "When agents complete tasks (via project orchestration or commander delegation), the system automatically extracts 1-3 key learnings using GPT-4o-mini and stores them as memory entries. This creates an ever-growing knowledge base that makes every agent smarter over time.",
    details: ["Hooked into orchestration (project execution) and commander delegation flows", "Extracts: facts, decisions, preferences, instructions, context", "Importance scoring based on task quality and content significance", "Near-duplicate detection prevents redundant memories", "Auto-learned entries shown with cyan badge in Memory Governance", "Runs asynchronously - never blocks task completion"]
  },
  {
    icon: Terminal, title: "Command Palette", color: "text-yellow-400",
    desc: "A VS Code/Notion-style quick search interface for instant navigation. Press / or Cmd+K to open a modal that searches across all pages, agents, and quick actions with keyboard navigation and recent search history.",
    details: ["Searches 20+ pages, 41 agents, and quick actions", "Keyboard navigation with arrow keys, Enter, and Escape", "Recent searches stored in localStorage", "Grouped results: Recent, Pages, Agents, Quick Actions", "Voice command integration via microphone button", "Accessible from sidebar search button or / keyboard shortcut"]
  },
];

const TIER_COLORS = {
  "Flagship": "bg-amber-500/20 text-amber-400",
  "Fast": "bg-cyan-500/20 text-cyan-400",
  "Economy": "bg-emerald-500/20 text-emerald-400",
  "Premium": "bg-violet-500/20 text-violet-400",
  "Reasoning": "bg-rose-500/20 text-rose-400",
  "Search": "bg-blue-500/20 text-blue-400",
  "Research": "bg-indigo-500/20 text-indigo-400",
  "Image Gen": "bg-pink-500/20 text-pink-400",
  "Video Gen": "bg-red-500/20 text-red-400",
  "Voice": "bg-orange-500/20 text-orange-400",
  "STT": "bg-teal-500/20 text-teal-400",
};

const AI_PROVIDERS = [
  {
    name: "OpenAI", color: "text-emerald-400", dotColor: "bg-emerald-400",
    models: [
      { name: "GPT-5.2", tier: "Flagship", desc: "Most capable for coding, analysis & complex tasks" },
      { name: "GPT-4o", tier: "Fast", desc: "Balanced speed and quality" },
      { name: "GPT-4o Mini", tier: "Economy", desc: "Cost-efficient for quick answers" },
      { name: "O3", tier: "Reasoning", desc: "Advanced reasoning for math & logic" },
      { name: "O3 Mini", tier: "Reasoning", desc: "Lightweight analytical tasks" },
    ],
  },
  {
    name: "Anthropic", color: "text-orange-400", dotColor: "bg-orange-400",
    models: [
      { name: "Claude Sonnet 4.5", tier: "Flagship", desc: "Creative writing, analysis & nuanced tasks" },
      { name: "Claude Opus 4.5", tier: "Premium", desc: "Deep research & complex analysis" },
      { name: "Claude Haiku 4.5", tier: "Economy", desc: "Fast responses & summaries" },
    ],
  },
  {
    name: "Google", color: "text-blue-400", dotColor: "bg-blue-400",
    models: [
      { name: "Gemini 3 Flash", tier: "Fast", desc: "Lightning-fast responses" },
      { name: "Gemini 3 Pro", tier: "Flagship", desc: "Multimodal research & analysis" },
    ],
  },
  {
    name: "xAI (Grok)", color: "text-sky-400", dotColor: "bg-sky-400",
    models: [
      { name: "Grok 3", tier: "Flagship", desc: "1M context, reasoning & analysis" },
      { name: "Grok 3 Mini", tier: "Economy", desc: "Cost-efficient reasoning" },
      { name: "Grok 2", tier: "Fast", desc: "Competitive with GPT-4o" },
    ],
  },
  {
    name: "DeepSeek", color: "text-teal-400", dotColor: "bg-teal-400",
    models: [
      { name: "DeepSeek Chat", tier: "Economy", desc: "128K context, ultra-affordable" },
      { name: "DeepSeek Reasoner", tier: "Reasoning", desc: "Deep math & logic reasoning" },
    ],
  },
  {
    name: "Mistral AI", color: "text-violet-400", dotColor: "bg-violet-400",
    models: [
      { name: "Mistral Large", tier: "Flagship", desc: "Complex reasoning, enterprise-grade" },
      { name: "Mistral Medium", tier: "Fast", desc: "Balanced performance" },
      { name: "Mistral Small", tier: "Economy", desc: "Ultra-fast, simple tasks" },
    ],
  },
  {
    name: "Perplexity", color: "text-cyan-400", dotColor: "bg-cyan-400",
    models: [
      { name: "Sonar", tier: "Search", desc: "Web-grounded real-time answers" },
      { name: "Sonar Pro", tier: "Research", desc: "Deep web research with citations" },
    ],
  },
  {
    name: "Cohere", color: "text-amber-400", dotColor: "bg-amber-400",
    models: [
      { name: "Command R+", tier: "Flagship", desc: "RAG & enterprise tasks" },
      { name: "Command R", tier: "Economy", desc: "Cost-efficient summaries" },
    ],
  },
  {
    name: "AI Generation + Voice", color: "text-pink-400", dotColor: "bg-pink-400",
    models: [
      { name: "Nano Banana 2", tier: "Image Gen", desc: "Gemini 3.1 Flash image generation" },
      { name: "GPT Image 1", tier: "Image Gen", desc: "Generate images from text" },
      { name: "DALL-E 3", tier: "Image Gen", desc: "Creative image generation" },
      { name: "Sora 2", tier: "Video Gen", desc: "AI video from text prompts" },
      { name: "ElevenLabs", tier: "Voice", desc: "Multilingual TTS (Bangla, English, etc.)" },
      { name: "Whisper", tier: "STT", desc: "Speech-to-text in 50+ languages" },
    ],
  },
];

const COST_DATA = [
  { name: "OpenAI", unit: "per 1M tokens (text) / per image or second (gen)", models: [
    { name: "GPT-5.2", input: "$2.50", output: "$10.00" },
    { name: "GPT-4o", input: "$2.50", output: "$10.00" },
    { name: "GPT-4o Mini", input: "$0.15", output: "$0.60" },
    { name: "O3", input: "$10.00", output: "$40.00" },
    { name: "O3 Mini", input: "$1.10", output: "$4.40" },
    { name: "GPT Image 1", input: "$0.02/img", output: "1024x1024" },
    { name: "Sora 2", input: "$0.10/sec", output: "4-12 sec video" },
  ]},
  { name: "Anthropic", unit: "per 1M tokens", models: [
    { name: "Claude Sonnet 4.5", input: "$3.00", output: "$15.00" },
    { name: "Claude Opus 4.5", input: "$15.00", output: "$75.00" },
    { name: "Claude Haiku 4.5", input: "$0.80", output: "$4.00" },
  ]},
  { name: "Gemini", unit: "per 1M tokens", models: [
    { name: "Gemini 3 Flash", input: "$0.075", output: "$0.30" },
    { name: "Gemini 3 Pro", input: "$1.25", output: "$5.00" },
    { name: "Nano Banana 2", input: "$0.02/img", output: "1024x1024" },
  ]},
  { name: "xAI", unit: "per 1M tokens", models: [
    { name: "Grok 3", input: "$3.00", output: "$15.00" },
    { name: "Grok 3 Mini", input: "$0.30", output: "$0.50" },
    { name: "Grok 2", input: "$2.00", output: "$10.00" },
  ]},
  { name: "DeepSeek", unit: "per 1M tokens", models: [
    { name: "DeepSeek Chat", input: "$0.14", output: "$0.28" },
    { name: "DeepSeek Reasoner", input: "$0.55", output: "$2.19" },
  ]},
  { name: "Mistral", unit: "per 1M tokens", models: [
    { name: "Mistral Large", input: "$2.00", output: "$6.00" },
    { name: "Mistral Medium", input: "$0.40", output: "$2.00" },
    { name: "Mistral Small", input: "$0.10", output: "$0.30" },
  ]},
  { name: "Perplexity", unit: "per 1M tokens + $5/1K search", models: [
    { name: "Sonar", input: "$1.00", output: "$1.00" },
    { name: "Sonar Pro", input: "$3.00", output: "$15.00" },
  ]},
  { name: "Cohere", unit: "per 1M tokens", models: [
    { name: "Command R+", input: "$2.50", output: "$10.00" },
    { name: "Command R", input: "$0.15", output: "$0.60" },
  ]},
  { name: "ElevenLabs", unit: "per 1K characters", models: [
    { name: "Multilingual v2", input: "$0.30/1K chars", output: "TTS audio" },
    { name: "Turbo v2.5", input: "$0.18/1K chars", output: "Fast TTS" },
  ]},
  { name: "Google Suite", unit: "Free with service account", models: [
    { name: "Gmail Send", input: "Free", output: "per email" },
    { name: "Calendar Event", input: "Free", output: "per event" },
    { name: "Drive Read/Write", input: "Free", output: "per file" },
  ]},
];

const Section = ({ title, icon: Icon, color, children }) => (
  <div className="mb-10">
    <div className="flex items-center gap-3 mb-4">
      <div className={`w-9 h-9 rounded-xl ${color || "bg-indigo-500/15"} flex items-center justify-center`}>
        {Icon && <Icon className="w-5 h-5 text-white" />}
      </div>
      <h2 className="text-lg font-bold text-white font-['Outfit']">{title}</h2>
    </div>
    {children}
  </div>
);

const AboutPage = () => {
  const { token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [expandedLayer, setExpandedLayer] = useState(null);
  const [expandedSystem, setExpandedSystem] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch(`${API}/agents/public`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setAgents(await res.json());
    } catch {}
  }, [token]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${API}/summary/pdf`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "MAARS-Command-Summary.pdf";
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch {}
    setDownloading(false);
  };

  const totalAgents = AGENT_LAYERS.reduce((sum, l) => sum + l.agents.length, 0);

  return (
    <div className="space-y-8 max-w-4xl" data-testid="about-page">
      {/* Hero */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shadow-lg shadow-red-500/20">
              <Rocket className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white font-['Outfit']">MAARS Command</h1>
              <p className="text-sm text-zinc-400">by MAARS Global Corporation</p>
            </div>
          </div>
          <Button
            onClick={handleDownloadPDF}
            disabled={downloading}
            variant="outline"
            className="border-white/10 text-zinc-300 hover:bg-white/5"
            data-testid="download-pdf-btn"
          >
            {downloading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Download className="w-4 h-4 mr-2" />}
            {downloading ? "Generating..." : "Download PDF"}
          </Button>
        </div>
        <p className="text-sm text-zinc-300 leading-relaxed max-w-3xl">
          MAARS Command is an <span className="text-white font-medium">Autonomous AI Enterprise Operating System</span> that
          deploys a workforce of <span className="text-indigo-400 font-medium">{totalAgents} specialized AI agents</span> organized
          across 8 organizational layers. It merges the power of preset specialist business agents with autonomous execution,
          persistent memory, and real-world action capabilities. Users set high-level business goals, and the AI workforce
          autonomously plans, delegates, executes, collaborates, and delivers — with quality control, failure recovery, and
          human oversight at every step.
        </p>
        <div className="flex gap-2 mt-4 flex-wrap">
          <Badge className="bg-indigo-500/20 text-indigo-400 border-0">Multi-Agent Orchestration</Badge>
          <Badge className="bg-emerald-500/20 text-emerald-400 border-0">Quality Control</Badge>
          <Badge className="bg-amber-500/20 text-amber-400 border-0">LLM Router</Badge>
          <Badge className="bg-pink-500/20 text-pink-400 border-0">Content Generation</Badge>
          <Badge className="bg-cyan-500/20 text-cyan-400 border-0">Vibe Coding</Badge>
          <Badge className="bg-violet-500/20 text-violet-400 border-0">Memory Governance</Badge>
          <Badge className="bg-rose-500/20 text-rose-400 border-0">Voice Commands</Badge>
          <Badge className="bg-sky-500/20 text-sky-400 border-0">Code Explorer</Badge>
        </div>
      </div>

      {/* Platform Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { label: "AI Agents", value: totalAgents, color: "text-indigo-400" },
          { label: "Org Layers", value: "8", color: "text-amber-400" },
          { label: "Core Systems", value: SYSTEMS.length, color: "text-emerald-400" },
          { label: "LLM Providers", value: "3", color: "text-violet-400" },
          { label: "API Endpoints", value: "50+", color: "text-cyan-400" },
        ].map(s => (
          <Card key={s.label} className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-4 text-center">
              <p className={`text-2xl font-bold ${s.color} font-['Outfit']`}>{s.value}</p>
              <p className="text-[11px] text-zinc-500">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Agent Workforce */}
      <Section title={`The ${totalAgents}-Agent AI Workforce`} icon={Users} color="bg-indigo-500/15">
        <p className="text-xs text-zinc-400 mb-4">Each agent has a unique Custom Brain Profile defining its LLM model, tools, autonomy level, and communication style. Click a layer to expand.</p>
        <div className="space-y-2">
          {AGENT_LAYERS.map(layer => {
            const colors = LAYER_COLORS[layer.id];
            const Icon = layer.icon;
            const isExpanded = expandedLayer === layer.id;
            return (
              <div key={layer.id}>
                <button
                  onClick={() => setExpandedLayer(isExpanded ? null : layer.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isExpanded ? `${colors.bg} ${colors.border}` : "bg-zinc-900/30 border-white/5 hover:border-white/10"
                  }`}
                  data-testid={`layer-${layer.id}`}
                >
                  <Icon className={`w-4 h-4 ${colors.text}`} />
                  <span className="text-sm font-medium text-white flex-1 text-left">{layer.label}</span>
                  <Badge className={`${colors.badge} border-0 text-[10px]`}>{layer.agents.length} agents</Badge>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
                </button>
                {isExpanded && (
                  <div className="mt-1 ml-4 space-y-1.5 py-2">
                    {layer.agents.map(agent => {
                      const avatarAgent = agents.find(a => a.name === agent.name);
                      return (
                        <div key={agent.name} className={`flex items-start gap-3 p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                          {avatarAgent?.avatar ? (
                            <img src={avatarAgent.avatar} alt="" className="w-9 h-9 rounded-lg object-cover shrink-0" />
                          ) : (
                            <div className={`w-9 h-9 rounded-lg ${colors.bg} flex items-center justify-center shrink-0`}>
                              <Bot className={`w-4 h-4 ${colors.text}`} />
                            </div>
                          )}
                          <div>
                            <p className="text-sm font-medium text-white">{agent.name}</p>
                            <Badge className={`${colors.badge} border-0 text-[9px] mb-1`}>{agent.role}</Badge>
                            <p className="text-xs text-zinc-400 leading-relaxed">{agent.desc}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Section>

      {/* Core Systems */}
      <Section title="Core Systems & Capabilities" icon={Layers} color="bg-emerald-500/15">
        <p className="text-xs text-zinc-400 mb-4">The platform is built on {SYSTEMS.length} interconnected systems that work together to deliver autonomous business operations.</p>
        <div className="space-y-2">
          {SYSTEMS.map((sys, i) => {
            const isExpanded = expandedSystem === i;
            return (
              <div key={i}>
                <button
                  onClick={() => setExpandedSystem(isExpanded ? null : i)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isExpanded ? "bg-zinc-800/60 border-white/10" : "bg-zinc-900/30 border-white/5 hover:border-white/10"
                  }`}
                  data-testid={`system-${i}`}
                >
                  <sys.icon className={`w-4 h-4 ${sys.color} shrink-0`} />
                  <span className="text-sm font-medium text-white flex-1 text-left">{sys.title}</span>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
                </button>
                {isExpanded && (
                  <div className="mt-1 ml-4 p-4 rounded-lg bg-zinc-800/30 border border-white/5">
                    <p className="text-sm text-zinc-300 leading-relaxed mb-3">{sys.desc}</p>
                    <div className="space-y-1.5">
                      {sys.details.map((d, j) => (
                        <div key={j} className="flex items-start gap-2">
                          <div className="w-1 h-1 rounded-full bg-zinc-500 mt-2 shrink-0" />
                          <p className="text-xs text-zinc-400">{d}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Section>

      {/* Architecture Overview */}
      <Section title="Technical Architecture" icon={Database} color="bg-cyan-500/15">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Server className="w-4 h-4 text-cyan-400" />
                <p className="text-sm font-medium text-white">Backend</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">FastAPI (Python)</p>
                <p className="text-xs text-zinc-400">MongoDB database</p>
                <p className="text-xs text-zinc-400">27+ DB collections</p>
                <p className="text-xs text-zinc-400">50+ API endpoints</p>
                <p className="text-xs text-zinc-400">WebSocket real-time streaming</p>
                <p className="text-xs text-zinc-400">Emergent Integrations SDK</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="w-4 h-4 text-pink-400" />
                <p className="text-sm font-medium text-white">Frontend</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">React 18 + Tailwind CSS</p>
                <p className="text-xs text-zinc-400">Shadcn/UI components</p>
                <p className="text-xs text-zinc-400">20+ pages</p>
                <p className="text-xs text-zinc-400">Responsive dashboard layout</p>
                <p className="text-xs text-zinc-400">Command Palette + Voice</p>
                <p className="text-xs text-zinc-400">PDF export capabilities</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <p className="text-sm font-medium text-white">AI Layer</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">OpenAI (GPT-5.2, 4o, o3, Whisper)</p>
                <p className="text-xs text-zinc-400">Anthropic (Claude Sonnet 4.5)</p>
                <p className="text-xs text-zinc-400">Google (Gemini 3 Flash, 2.5 Pro)</p>
                <p className="text-xs text-zinc-400">Universal Emergent LLM Key</p>
                <p className="text-xs text-zinc-400">Smart model routing</p>
                <p className="text-xs text-zinc-400">Auto-learning from task results</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </Section>

      {/* AI Models & Providers */}
      <Section title="AI Models & Providers" icon={Sparkles} color="bg-amber-500/15">
        <p className="text-xs text-zinc-400 mb-4">9 AI providers with 30+ models across text generation, reasoning, search, image generation, video, voice, and speech-to-text.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {AI_PROVIDERS.map(provider => (
            <Card key={provider.name} className="bg-zinc-900/50 border-white/5" data-testid={`provider-${provider.name}`}>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className={`w-4 h-4 ${provider.color}`} />
                  <p className="text-sm font-bold text-white">{provider.name}</p>
                </div>
                <div className="space-y-2">
                  {provider.models.map(m => (
                    <div key={m.name} className="flex items-start gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${provider.dotColor}`} />
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-medium text-zinc-200">{m.name}</span>
                          <Badge className={`text-[8px] px-1.5 py-0 border-0 ${TIER_COLORS[m.tier] || "bg-zinc-700 text-zinc-400"}`}>{m.tier}</Badge>
                        </div>
                        <p className="text-[10px] text-zinc-500">{m.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </Section>

      {/* Provider Costs */}
      <Section title="Direct Provider Costs" icon={BarChart3} color="bg-green-500/15">
        <p className="text-xs text-zinc-400 mb-4">Reference pricing when using your own API keys. Prices are from provider websites and may change.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {COST_DATA.map(provider => (
            <Card key={provider.name} className="bg-zinc-900/50 border-white/5">
              <CardContent className="p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-white">{provider.name}</span>
                  <span className="text-[9px] text-zinc-600">{provider.unit}</span>
                </div>
                <div className="space-y-1">
                  {provider.models.map(m => (
                    <div key={m.name} className="flex items-center justify-between text-[11px]">
                      <span className="text-zinc-400">{m.name}</span>
                      <div className="flex gap-3">
                        <span className="text-zinc-500">In: <span className="text-emerald-400 font-medium">{m.input}</span></span>
                        <span className="text-zinc-500">Out: <span className="text-amber-400 font-medium">{m.output}</span></span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        <p className="text-[10px] text-zinc-600 mt-3 italic">* Emergent Universal Key includes a small markup over direct pricing for convenience and unified billing.</p>
      </Section>

      {/* Footer */}
      <div className="text-center py-6 border-t border-white/5">
        <p className="text-xs text-zinc-500">MAARS Command v1.0 — Autonomous AI Enterprise Operating System</p>
        <p className="text-[10px] text-zinc-600 mt-1">Built by MAARS Global Corporation</p>
      </div>
    </div>
  );
};

export default AboutPage;
