import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Rocket, Bot, Brain, Shield, Sparkles, Cpu, Activity, Radio, Code, Palette,
  PenTool, Gauge, Users, FileCheck, Zap, Mail, BarChart3, ChevronDown,
  ChevronRight, Globe, Lock, Eye, Target, Layers, Network, Server, Database,
  Download, Loader2, Mic, FileCode, Archive, Terminal, Search, Heart,
  Wrench, MessageSquare, RefreshCw, Briefcase, Building, TrendingUp,
  CheckCircle, Package, DollarSign, Printer
} from "lucide-react";

/* ── network label mapping ── */
const NETWORK_META = {
  strategic_executive: { label: "Strategic & Executive", icon: Target, color: "amber" },
  product_development: { label: "Product Development", icon: Package, color: "cyan" },
  engineering: { label: "Engineering", icon: Code, color: "emerald" },
  creative_brand: { label: "Creative & Brand", icon: Palette, color: "pink" },
  growth_distribution: { label: "Growth & Distribution", icon: TrendingUp, color: "green" },
  sales_revenue: { label: "Sales & Revenue", icon: DollarSign, color: "yellow" },
  operations: { label: "Operations", icon: Layers, color: "indigo" },
  finance_capital: { label: "Finance & Capital", icon: BarChart3, color: "emerald" },
  legal_governance: { label: "Legal & Governance", icon: Shield, color: "red" },
  research_intelligence: { label: "Research & Intelligence", icon: Search, color: "violet" },
  customer_experience: { label: "Customer Experience", icon: Heart, color: "rose" },
  security: { label: "Security", icon: Lock, color: "orange" },
  core_platform: { label: "Core Platform", icon: Server, color: "blue" },
  memory_knowledge: { label: "Memory & Knowledge", icon: Database, color: "violet" },
  tooling_capability: { label: "Tooling & Capability", icon: Wrench, color: "lime" },
  observability_incident: { label: "Observability & Incident", icon: Activity, color: "amber" },
  verification: { label: "Verification", icon: CheckCircle, color: "emerald" },
  execution: { label: "Execution", icon: Zap, color: "yellow" },
  simulation_foresight: { label: "Simulation & Foresight", icon: Eye, color: "purple" },
  experimentation: { label: "Experimentation", icon: Sparkles, color: "teal" },
  communication_reporting: { label: "Communication & Reporting", icon: MessageSquare, color: "sky" },
  conflict_resolution: { label: "Conflict Resolution", icon: Shield, color: "orange" },
  recovery_resilience: { label: "Recovery & Resilience", icon: RefreshCw, color: "green" },
  investment_portfolio: { label: "Investment & Portfolio", icon: Briefcase, color: "amber" },
  venture_creation: { label: "Venture Creation", icon: Rocket, color: "red" },
  web_search_intelligence: { label: "Web Search Intelligence", icon: Globe, color: "cyan" },
  industry_specific: { label: "Industry Specific", icon: Building, color: "slate" },
};

const colorMap = (c) => ({
  bg: `bg-${c}-500/10`, border: `border-${c}-500/20`, text: `text-${c}-400`, badge: `bg-${c}-500/20 text-${c}-400`,
});

/* ── systems ── */
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
    details: ["Critic Module: GPT-4o auto-reviews every task output", "Scoring: 1-10 on multiple quality dimensions", "Retry chain: GPT-5.2 \u2192 Claude Sonnet \u2192 Gemini Pro \u2192 GPT-4o", "Escalation: Failed tasks notify the user for manual review", "Quality Dashboard: pass rates, average scores, recovery metrics"]
  },
  {
    icon: Network, title: "Model-Agnostic LLM Router", color: "text-cyan-400",
    desc: "An intelligent routing system that analyzes task complexity and automatically selects the optimal LLM model. Simple queries get routed to fast, cheap models. Complex coding or legal tasks get premium models. The router considers task type (coding, creative, data, legal, reasoning), agent role, and content length.",
    details: ["Premium Tier: GPT-5.2, Claude Sonnet 4.5, Gemini 2.5 Pro (complex tasks)", "Standard Tier: GPT-4o, GPT-4.1, Gemini 3 Flash (moderate tasks)", "Economy Tier: GPT-4o-mini, Gemini Flash, Claude Haiku (simple tasks)", "User override: manually select a model in Settings", "Routing logs: model usage distribution, cost tracking"]
  },
  {
    icon: Activity, title: "Autonomous Collaboration Engine", color: "text-indigo-400",
    desc: "When an agent completes a task, the system automatically detects if the work impacts agents in related domains and creates collaboration entries. All 458+ agents are mapped to 27 network categories with cross-domain trigger rules. This ensures seamless coordination without manual intervention.",
    details: ["9 domains: executive, product, technical, creative, marketing, operations, finance, governance, intelligence", "Auto-detection: marketing \u2192 creative + technical, product \u2192 technical + creative + marketing", "Collaboration types: information sharing, review request, data handoff, coordination", "Up to 3 auto-collaborations per task to avoid noise"]
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
    desc: "A system-wide toggle that controls whether agents can perform real-world actions. In Simulation Mode (default), all external actions return simulated responses \u2014 safe for testing and review. In Execution Mode, agents send real emails, create actual calendar events, and post to live platforms.",
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
    details: ["OpenAI: GPT-5.2, GPT-5.1, GPT-4.1, GPT-4o, o3, o4-mini", "Anthropic: Claude Sonnet 4.5, Claude 4 Sonnet, Claude Haiku 4.5", "Google Gemini: Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash", "Groq: Llama 4 Scout, Llama 4 Maverick, Llama 3.3 70B", "Together AI: Llama 4 Maverick FP8, Llama 3.3 70B Turbo, DeepSeek R1", "Fireworks AI: Llama 4 Scout, Llama 4 Maverick, DeepSeek V3", "AI21: Jamba Large 1.7, Jamba Mini 1.7", "xAI (Grok), DeepSeek, Mistral, Perplexity, Cohere, ElevenLabs", "Powered by Emergent LLM Key (universal key across all providers)"]
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
    details: ["Searches 50+ pages, 458+ agents, and quick actions", "Keyboard navigation with arrow keys, Enter, and Escape", "Recent searches stored in localStorage", "Grouped results: Recent, Pages, Agents, Quick Actions", "Voice command integration via microphone button", "Accessible from sidebar search button or / keyboard shortcut"]
  },
  {
    icon: Users, title: "Agent Team Builder", color: "text-indigo-400",
    desc: "Assemble custom teams of agents for specific projects and workflows. Select agents from the full 458+ agent pool, organized by network category. Each team can have a defined purpose and mission, making it easy to deploy specialized groups for targeted business objectives.",
    details: ["Search and filter agents by name, role, network, or capability", "Create unlimited teams with custom names and mission descriptions", "Drag-and-drop agent selection from the full workforce pool", "Team overview with member count, capabilities, and network coverage", "Reusable teams for recurring project types"]
  },
  {
    icon: Gauge, title: "Trust Analytics & Scoring", color: "text-emerald-400",
    desc: "A comprehensive trust scoring system that evaluates every agent's reliability based on execution history, success rate, latency, and anomaly detection. Provides real-time dashboards with trend analysis, comparisons, and alerts for trust score degradation.",
    details: ["Per-agent trust scores (0-100) based on execution history", "Multi-dimensional scoring: success rate, latency, quality, consistency", "Trend analysis with historical graphs", "Anomaly detection for sudden performance drops", "Agent comparison and ranking", "Configurable alert thresholds for trust degradation"]
  },
  {
    icon: Zap, title: "Workflow Builder", color: "text-amber-400",
    desc: "A visual drag-and-drop workflow builder for creating multi-step automated processes. Connect agents, tools, and decision nodes into executable workflows. Supports conditional branching, parallel execution, and scheduled triggers.",
    details: ["Visual canvas with drag-and-drop node placement", "Node types: Agent Task, Decision, Parallel Split, Merge, Trigger", "Conditional branching based on task output or data", "Workflow templates for common business processes", "Execution history and performance tracking", "Scheduled and event-driven triggers"]
  },
  {
    icon: Briefcase, title: "Campaign Builder", color: "text-pink-400",
    desc: "Build and manage multi-channel marketing campaigns with AI agents. Define campaign goals, select channels, create content variations, and track performance \u2014 all orchestrated by specialized marketing agents.",
    details: ["Multi-channel campaigns: email, social, web, ads", "AI-generated content variations per channel", "Performance tracking and A/B testing", "Budget allocation and spend optimization", "Campaign templates and scheduling", "Integration with Content Generator and Reference Intelligence"]
  },
];

/* ── AI providers ── */
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
  { name: "OpenAI", color: "text-emerald-400", dotColor: "bg-emerald-400", models: [
    { name: "GPT-5.2", tier: "Flagship", desc: "Most capable for coding, analysis & complex tasks" },
    { name: "GPT-4o", tier: "Fast", desc: "Balanced speed and quality" },
    { name: "GPT-4o Mini", tier: "Economy", desc: "Cost-efficient for quick answers" },
    { name: "O3", tier: "Reasoning", desc: "Advanced reasoning for math & logic" },
    { name: "O3 Mini", tier: "Reasoning", desc: "Lightweight analytical tasks" },
  ]},
  { name: "Anthropic", color: "text-orange-400", dotColor: "bg-orange-400", models: [
    { name: "Claude Sonnet 4.5", tier: "Flagship", desc: "Creative writing, analysis & nuanced tasks" },
    { name: "Claude Opus 4.5", tier: "Premium", desc: "Deep research & complex analysis" },
    { name: "Claude Haiku 4.5", tier: "Economy", desc: "Fast responses & summaries" },
  ]},
  { name: "Google", color: "text-blue-400", dotColor: "bg-blue-400", models: [
    { name: "Gemini 3 Flash", tier: "Fast", desc: "Lightning-fast responses" },
    { name: "Gemini 3 Pro", tier: "Flagship", desc: "Multimodal research & analysis" },
  ]},
  { name: "xAI (Grok)", color: "text-sky-400", dotColor: "bg-sky-400", models: [
    { name: "Grok 3", tier: "Flagship", desc: "1M context, reasoning & analysis" },
    { name: "Grok 3 Mini", tier: "Economy", desc: "Cost-efficient reasoning" },
    { name: "Grok 2", tier: "Fast", desc: "Competitive with GPT-4o" },
  ]},
  { name: "DeepSeek", color: "text-teal-400", dotColor: "bg-teal-400", models: [
    { name: "DeepSeek Chat", tier: "Economy", desc: "128K context, ultra-affordable" },
    { name: "DeepSeek Reasoner", tier: "Reasoning", desc: "Deep math & logic reasoning" },
  ]},
  { name: "Mistral AI", color: "text-violet-400", dotColor: "bg-violet-400", models: [
    { name: "Mistral Large", tier: "Flagship", desc: "Complex reasoning, enterprise-grade" },
    { name: "Mistral Medium", tier: "Fast", desc: "Balanced performance" },
    { name: "Mistral Small", tier: "Economy", desc: "Ultra-fast, simple tasks" },
  ]},
  { name: "Perplexity", color: "text-cyan-400", dotColor: "bg-cyan-400", models: [
    { name: "Sonar", tier: "Search", desc: "Web-grounded real-time answers" },
    { name: "Sonar Pro", tier: "Research", desc: "Deep web research with citations" },
  ]},
  { name: "Cohere", color: "text-amber-400", dotColor: "bg-amber-400", models: [
    { name: "Command R+", tier: "Flagship", desc: "RAG & enterprise tasks" },
    { name: "Command R", tier: "Economy", desc: "Cost-efficient summaries" },
  ]},
  { name: "Groq (Llama 4)", color: "text-amber-300", dotColor: "bg-amber-300", models: [
    { name: "Llama 4 Scout", tier: "Economy", desc: "Ultra-fast 128K context, lowest cost" },
    { name: "Llama 4 Maverick", tier: "Fast", desc: "128E MoE architecture, balanced" },
    { name: "Llama 3.3 70B", tier: "Fast", desc: "Versatile open-source powerhouse" },
  ]},
  { name: "Together AI", color: "text-lime-400", dotColor: "bg-lime-400", models: [
    { name: "Llama 4 Maverick FP8", tier: "Fast", desc: "FP8 optimized Llama 4 inference" },
    { name: "Llama 3.3 70B Turbo", tier: "Fast", desc: "Turbo-optimized open-source" },
    { name: "DeepSeek R1", tier: "Reasoning", desc: "Open-source deep reasoning" },
  ]},
  { name: "Fireworks AI", color: "text-red-400", dotColor: "bg-red-400", models: [
    { name: "Llama 4 Scout", tier: "Economy", desc: "Serverless Llama 4 inference" },
    { name: "Llama 4 Maverick", tier: "Fast", desc: "High-throughput Llama 4" },
    { name: "DeepSeek V3", tier: "Fast", desc: "Cost-efficient DeepSeek hosting" },
  ]},
  { name: "AI21 (Jamba)", color: "text-indigo-300", dotColor: "bg-indigo-300", models: [
    { name: "Jamba Large 1.7", tier: "Flagship", desc: "256K context, SSM+Transformer hybrid" },
    { name: "Jamba Mini 1.7", tier: "Economy", desc: "Lightweight enterprise tasks" },
  ]},
  { name: "AI Generation + Voice", color: "text-pink-400", dotColor: "bg-pink-400", models: [
    { name: "Nano Banana 2", tier: "Image Gen", desc: "Gemini 3.1 Flash image generation" },
    { name: "GPT Image 1", tier: "Image Gen", desc: "Generate images from text" },
    { name: "DALL-E 3", tier: "Image Gen", desc: "Creative image generation" },
    { name: "Sora 2", tier: "Video Gen", desc: "AI video from text prompts" },
    { name: "ElevenLabs", tier: "Voice", desc: "Multilingual TTS (Bangla, English, etc.)" },
    { name: "Whisper", tier: "STT", desc: "Speech-to-text in 50+ languages" },
  ]},
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
  { name: "Groq (Llama 4)", unit: "per 1M tokens", models: [
    { name: "Llama 4 Scout", input: "$0.11", output: "$0.34" },
    { name: "Llama 4 Maverick", input: "$0.50", output: "$0.77" },
    { name: "Llama 3.3 70B", input: "$0.59", output: "$0.79" },
  ]},
  { name: "Together AI", unit: "per 1M tokens", models: [
    { name: "Llama 4 Maverick FP8", input: "$0.27", output: "$0.85" },
    { name: "Llama 3.3 70B Turbo", input: "$0.88", output: "$0.88" },
    { name: "DeepSeek R1", input: "$3.00", output: "$7.00" },
  ]},
  { name: "Fireworks AI", unit: "per 1M tokens", models: [
    { name: "Llama 4 Scout", input: "$0.15", output: "$0.60" },
    { name: "Llama 4 Maverick", input: "$0.50", output: "$0.77" },
    { name: "DeepSeek V3", input: "$0.56", output: "$1.68" },
  ]},
  { name: "AI21 (Jamba)", unit: "per 1M tokens", models: [
    { name: "Jamba Large 1.7", input: "$2.00", output: "$8.00" },
    { name: "Jamba Mini 1.7", input: "$0.20", output: "$0.40" },
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

/* ── shared components ── */
const Section = ({ title, icon: Icon, color, children, id }) => (
  <div className="mb-10 about-section" id={id}>
    <div className="flex items-center gap-3 mb-4">
      <div className={`w-9 h-9 rounded-xl ${color || "bg-indigo-500/15"} flex items-center justify-center print-icon`}>
        {Icon && <Icon className="w-5 h-5 text-white" />}
      </div>
      <h2 className="text-lg font-bold text-white font-['Outfit'] print-heading">{title}</h2>
    </div>
    {children}
  </div>
);

/* ── main component ── */
const AboutPage = () => {
  const { token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [expandedNetworks, setExpandedNetworks] = useState(new Set());
  const [expandedSystems, setExpandedSystems] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [printing, setPrinting] = useState(false);
  const printRef = useRef(null);

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch(`${API}/agents`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { setAgents(await res.json()); }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  /* Group agents by network */
  const networkGroups = agents.reduce((acc, agent) => {
    const net = agent.network || "core_team";
    if (!acc[net]) acc[net] = [];
    acc[net].push(agent);
    return acc;
  }, {});

  const sortedNetworks = Object.entries(networkGroups).sort((a, b) => b[1].length - a[1].length);
  const uniqueNetworks = Object.keys(networkGroups).length;

  const toggleNetwork = (id) => {
    setExpandedNetworks(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleSystem = (i) => {
    setExpandedSystems(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  /* Print-ready PDF download */
  const handlePrint = () => {
    setPrinting(true);
    /* expand all sections for print */
    setExpandedNetworks(new Set(sortedNetworks.map(([k]) => k)));
    setExpandedSystems(new Set(SYSTEMS.map((_, i) => i)));
    setTimeout(() => {
      window.print();
      setPrinting(false);
    }, 500);
  };

  const getNetworkMeta = (netId) => {
    const meta = NETWORK_META[netId];
    if (meta) return meta;
    return { label: netId === "core_team" ? "Core Team" : netId.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()), icon: Bot, color: "zinc" };
  };

  const getNetColors = (netId) => {
    const m = getNetworkMeta(netId);
    const c = m.color;
    return { bg: `bg-${c}-500/10`, border: `border-${c}-500/20`, text: `text-${c}-400`, badge: `bg-${c}-500/20 text-${c}-400` };
  };

  return (
    <div className="space-y-8 max-w-4xl print-container" data-testid="about-page" ref={printRef}>
      {/* Hero */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <img src="/mgc-logo.png" alt="MAARS Global Corporation" className="w-14 h-14 rounded-2xl object-contain" />
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white font-['Outfit']">MAARS Command</h1>
              <p className="text-sm text-zinc-400">Autonomous AI Enterprise Operating System</p>
              <p className="text-[10px] text-zinc-600">by MAARS Global Corporation</p>
            </div>
          </div>
          <Button
            onClick={handlePrint}
            variant="outline"
            className="border-white/10 text-zinc-300 hover:bg-white/5 no-print"
            data-testid="download-pdf-btn"
          >
            <Printer className="w-4 h-4 mr-2" />
            {printing ? "Preparing..." : "Download Docs"}
          </Button>
        </div>
        <p className="text-sm text-zinc-300 leading-relaxed max-w-3xl">
          MAARS Command is a <span className="text-white font-medium">governed, hierarchical, multi-agent intelligence and execution architecture</span> designed for enterprise-grade autonomous operations. It
          deploys <span className="text-indigo-400 font-medium"> {agents.length || "458"}+ specialized AI agents</span> across
          <span className="text-emerald-400 font-medium"> {uniqueNetworks || 27} network categories</span> and
          <span className="text-cyan-400 font-medium"> 16 system layers</span>, powered by <span className="text-amber-400 font-medium">13 LLM providers with 45+ models</span>.
          From strategic planning and content creation to financial analysis and compliance -- MAARS Command converts high-level human intent into reliable,
          measurable, auditable, and strategically useful execution at scale.
        </p>
        <div className="flex gap-2 mt-4 flex-wrap">
          {["Multi-Agent Orchestration","Quality Control","LLM Router","Content Generation","Vibe Coding","Memory Governance","Voice Commands","Code Explorer","Knowledge Graph","Workflow Builder","Campaign Builder","Integration Hub","Team Builder","Trust Analytics"].map((b, i) => {
            const colors = ["indigo","emerald","amber","pink","cyan","violet","rose","sky","blue","teal","orange","red","green","purple"];
            return <Badge key={b} className={`bg-${colors[i % colors.length]}-500/20 text-${colors[i % colors.length]}-400 border-0`}>{b}</Badge>;
          })}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
        {[
          { label: "AI Agents", value: `${agents.length || "458"}+`, color: "text-indigo-400" },
          { label: "Networks", value: uniqueNetworks || 27, color: "text-emerald-400" },
          { label: "Core Systems", value: SYSTEMS.length, color: "text-amber-400" },
          { label: "LLM Providers", value: "13", color: "text-violet-400" },
          { label: "AI Models", value: "45+", color: "text-cyan-400" },
          { label: "API Endpoints", value: "212+", color: "text-rose-400" },
        ].map(s => (
          <Card key={s.label} className="bg-zinc-900/50 border-white/5 print-card">
            <CardContent className="p-4 text-center">
              <p className={`text-2xl font-bold ${s.color} font-['Outfit']`}>{s.value}</p>
              <p className="text-[11px] text-zinc-500">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Dynamic Agent Workforce */}
      <Section title={`The ${agents.length || 458}-Agent AI Workforce`} icon={Users} color="bg-indigo-500/15" id="agents">
        <p className="text-xs text-zinc-400 mb-4">
          Every agent has a unique Custom Brain Profile defining its LLM model, tools, autonomy level, and communication style.
          Agents are organized into {uniqueNetworks || 27} specialized network categories. {printing ? "" : "Click a network to expand."}
        </p>
        {loading ? (
          <div className="flex items-center justify-center h-20"><Loader2 className="w-5 h-5 animate-spin text-indigo-400" /></div>
        ) : (
          <div className="space-y-2">
            {sortedNetworks.map(([netId, netAgents]) => {
              const meta = getNetworkMeta(netId);
              const colors = getNetColors(netId);
              const Icon = meta.icon;
              const isExpanded = expandedNetworks.has(netId) || printing;
              return (
                <div key={netId}>
                  <button
                    onClick={() => toggleNetwork(netId)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                      isExpanded ? `${colors.bg} ${colors.border}` : "bg-zinc-900/30 border-white/5 hover:border-white/10"
                    }`}
                    data-testid={`network-${netId}`}
                  >
                    <Icon className={`w-4 h-4 ${colors.text}`} />
                    <span className="text-sm font-medium text-white flex-1 text-left">{meta.label}</span>
                    <Badge className={`${colors.badge} border-0 text-[10px]`}>{netAgents.length} agents</Badge>
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500 no-print" /> : <ChevronRight className="w-4 h-4 text-zinc-500 no-print" />}
                  </button>
                  {isExpanded && (
                    <div className="mt-1 ml-4 space-y-1 py-2">
                      {netAgents.map(agent => (
                        <div key={agent.agent_id} className={`flex items-start gap-3 p-2.5 rounded-lg ${colors.bg} border ${colors.border}`}>
                          {agent.avatar && !agent.avatar.startsWith("data:") ? (
                            <img src={agent.avatar.startsWith("/") ? `${API.replace("/api", "")}${agent.avatar}` : agent.avatar} alt="" className="w-8 h-8 rounded-lg object-cover shrink-0" loading="lazy" />
                          ) : (
                            <div className={`w-8 h-8 rounded-lg ${colors.bg} flex items-center justify-center shrink-0`}>
                              <Bot className={`w-3.5 h-3.5 ${colors.text}`} />
                            </div>
                          )}
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <p className="text-xs font-medium text-white">{agent.name}</p>
                              <Badge className={`${colors.badge} border-0 text-[8px]`}>{agent.role}</Badge>
                            </div>
                            {agent.description && <p className="text-[10px] text-zinc-400 leading-relaxed mt-0.5 line-clamp-2 print-no-clamp">{agent.description}</p>}
                            {agent.capabilities?.length > 0 && (
                              <div className="flex gap-1 mt-1 flex-wrap">
                                {agent.capabilities.slice(0, 5).map(c => (
                                  <span key={c} className="text-[8px] px-1.5 py-0.5 rounded bg-white/5 text-zinc-500">{c}</span>
                                ))}
                                {agent.capabilities.length > 5 && <span className="text-[8px] text-zinc-600">+{agent.capabilities.length - 5} more</span>}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Section>

      {/* Core Systems */}
      <Section title={`${SYSTEMS.length} Core Systems & Capabilities`} icon={Layers} color="bg-emerald-500/15" id="systems">
        <p className="text-xs text-zinc-400 mb-4">The platform is built on {SYSTEMS.length} interconnected systems that work together to deliver autonomous business operations. {printing ? "" : "Click to expand each system."}</p>
        <div className="space-y-2">
          {SYSTEMS.map((sys, i) => {
            const isExpanded = expandedSystems.has(i) || printing;
            return (
              <div key={i}>
                <button
                  onClick={() => toggleSystem(i)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isExpanded ? "bg-zinc-800/60 border-white/10" : "bg-zinc-900/30 border-white/5 hover:border-white/10"
                  }`}
                  data-testid={`system-${i}`}
                >
                  <sys.icon className={`w-4 h-4 ${sys.color} shrink-0`} />
                  <span className="text-sm font-medium text-white flex-1 text-left">{sys.title}</span>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500 no-print" /> : <ChevronRight className="w-4 h-4 text-zinc-500 no-print" />}
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

      {/* Architecture */}
      <Section title="Technical Architecture" icon={Database} color="bg-cyan-500/15" id="architecture">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Card className="bg-zinc-900/50 border-white/5 print-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2"><Server className="w-4 h-4 text-cyan-400" /><p className="text-sm font-medium text-white">Backend</p></div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">FastAPI (Python) with async I/O</p>
                <p className="text-xs text-zinc-400">MongoDB with 27+ collections</p>
                <p className="text-xs text-zinc-400">212+ REST API endpoints</p>
                <p className="text-xs text-zinc-400">WebSocket real-time streaming</p>
                <p className="text-xs text-zinc-400">Emergent Integrations SDK</p>
                <p className="text-xs text-zinc-400">Stripe payment processing</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5 print-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2"><Eye className="w-4 h-4 text-pink-400" /><p className="text-sm font-medium text-white">Frontend</p></div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">React 18 + Tailwind CSS</p>
                <p className="text-xs text-zinc-400">Shadcn/UI component library</p>
                <p className="text-xs text-zinc-400">50+ pages & dashboards</p>
                <p className="text-xs text-zinc-400">Drag-and-drop workflow builder</p>
                <p className="text-xs text-zinc-400">Command Palette + Voice</p>
                <p className="text-xs text-zinc-400">PDF & ZIP export capabilities</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5 print-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2"><Sparkles className="w-4 h-4 text-amber-400" /><p className="text-sm font-medium text-white">AI Layer</p></div>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">OpenAI (GPT-5.2, 4o, o3, Whisper)</p>
                <p className="text-xs text-zinc-400">Anthropic (Claude Sonnet 4.5)</p>
                <p className="text-xs text-zinc-400">Google (Gemini 3 Flash, Pro)</p>
                <p className="text-xs text-zinc-400">Groq, Together AI, Fireworks, AI21</p>
                <p className="text-xs text-zinc-400">xAI Grok, DeepSeek, Mistral, Perplexity</p>
                <p className="text-xs text-zinc-400">ElevenLabs TTS + Image/Video Gen</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </Section>

      {/* AI Models & Providers */}
      <Section title="AI Models & Providers" icon={Sparkles} color="bg-amber-500/15" id="providers">
        <p className="text-xs text-zinc-400 mb-4">13 AI providers with 45+ models across text generation, reasoning, search, image generation, video, voice, and speech-to-text.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {AI_PROVIDERS.map(provider => (
            <Card key={provider.name} className="bg-zinc-900/50 border-white/5 print-card" data-testid={`provider-${provider.name}`}>
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

      {/* Security & Governance */}
      <Section title="Security & Governance" icon={Shield} color="bg-red-500/15" id="security">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            { title: "Role-Based Access Control (RBAC)", icon: Lock, desc: "Granular permissions for users, agents, and resources. Admin, Manager, and User roles with configurable access levels for every feature and API endpoint." },
            { title: "Circuit Breakers", icon: Shield, desc: "Automatic protection against cascading failures. When an agent or service exceeds error thresholds, the circuit breaker trips to prevent system-wide degradation." },
            { title: "Cost Governance", icon: DollarSign, desc: "Real-time spending controls with per-user and per-agent cost limits. Budget alerts, spending dashboards, and automatic throttling when limits are reached." },
            { title: "Audit Logging", icon: FileCheck, desc: "Complete audit trail of every action, decision, and API call. Immutable logs for compliance, debugging, and forensic analysis." },
            { title: "Trust Scoring", icon: Gauge, desc: "Every agent has a dynamic trust score based on execution history, success rate, latency, and anomaly detection. Low-trust agents are flagged or restricted automatically." },
            { title: "Simulation Mode", icon: Eye, desc: "System-wide safety toggle. In Simulation Mode, all external actions return safe, simulated responses. Flip to Execution Mode only when ready for real-world operations." },
          ].map(item => (
            <Card key={item.title} className="bg-zinc-900/50 border-white/5 print-card">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <item.icon className="w-4 h-4 text-red-400" />
                  <p className="text-sm font-medium text-white">{item.title}</p>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{item.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </Section>

      {/* Provider Costs */}
      <Section title="Direct Provider Costs" icon={BarChart3} color="bg-green-500/15" id="costs">
        <p className="text-xs text-zinc-400 mb-4">Reference pricing when using your own API keys. Prices are from provider websites and may change.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {COST_DATA.map(provider => (
            <Card key={provider.name} className="bg-zinc-900/50 border-white/5 print-card">
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
        <p className="text-xs text-zinc-500">MAARS Command v1.0 -- Autonomous AI Enterprise Operating System</p>
        <p className="text-[10px] text-zinc-600 mt-1">{agents.length || 458}+ Agents | {uniqueNetworks || 27} Networks | 13 LLM Providers | 45+ Models</p>
        <p className="text-[10px] text-zinc-600 mt-1">Built by MAARS Global Corporation | support.maars@marsgc.net</p>
      </div>
    </div>
  );
};

export default AboutPage;
