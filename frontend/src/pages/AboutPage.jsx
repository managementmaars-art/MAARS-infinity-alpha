import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import {
  Rocket, Bot, Brain, Shield, Sparkles, Cpu, Activity, Radio, Code, Palette,
  PenTool, Gauge, Users, FileCheck, Zap, Mail, BarChart3, ChevronDown,
  ChevronRight, Globe, Lock, Eye, Target, Layers, Network, Server, Database,
  Download, Mic, FileCode, Archive, Terminal, Search, Heart,
  Wrench, MessageSquare, RefreshCw, Briefcase, Building, TrendingUp,
  CheckCircle, Package, DollarSign, Printer, Share2, Key, BookOpen
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

/* ── systems - written so a 6th grader can understand ── */
const SYSTEMS = [
  {
    icon: Rocket, title: "Autonomous Orchestration Engine", subtitle: "The Boss Brain That Runs Everything", color: "text-red-400",
    desc: "Think of this as the main brain of MAARS Command. When you tell it what you want to accomplish (like \"launch a new product\" or \"write a marketing plan\"), it breaks your big goal into smaller steps, figures out which AI agent is best at each step, and assigns the work automatically. It's like having a super-smart project manager who never sleeps, never forgets, and can manage hundreds of tasks at the same time.",
    details: [
      "You type in a goal in plain English (like \"Create a social media campaign for our new app\")",
      "The system scores your goal on how clear it is and how hard it will be to complete",
      "It creates a step-by-step plan with milestones (checkpoints) and individual tasks",
      "Each task gets automatically assigned to the AI agent who is best at that type of work",
      "Multiple tasks can run at the same time (not one-by-one), so things get done faster",
      "If something goes wrong with a task, the system automatically tries again with a different AI model",
      "It can also generate images (using GPT Image 1) and videos (using Sora 2) as part of the plan",
      "When tasks need real-world actions (like sending an email), it hands off to the Personal Secretary agent",
    ]
  },
  {
    icon: Brain, title: "Custom Brain Profiles", subtitle: "Personalizing How Each Agent Thinks", color: "text-violet-400",
    desc: "Every AI agent has its own \"brain profile\" -- a set of settings that control how it thinks, talks, and works. You can change these settings anytime. It's like adjusting the personality and skills of each team member. Want one agent to be super creative? Turn up its creativity. Want another to be very precise and careful? Turn down its creativity and pick a more accurate AI model.",
    details: [
      "Each agent can use a different AI model (like GPT-5 for hard tasks, or a faster model for simple ones)",
      "Autonomy Level (1 to 10): Level 1 means the agent always asks you before doing anything. Level 10 means it does everything on its own",
      "Communication Style: You can set each agent to talk professionally, casually, technically, or creatively",
      "Tool Permissions: You decide what tools each agent can use -- web browsing, making images, running code, etc.",
      "Creativity Temperature (0.0 to 1.0): 0.0 means the agent gives the same answer every time (very predictable). 1.0 means it gets very creative and surprising",
      "Max Tokens: This controls how long the agent's responses can be (more tokens = longer answers)",
    ]
  },
  {
    icon: Shield, title: "Quality Control & Failure Recovery", subtitle: "Making Sure Every Answer Is Good Enough", color: "text-emerald-400",
    desc: "Every time an AI agent finishes a task, another AI (called the Critic) checks the work and gives it a score from 1 to 10. If the score is too low, the system tries again with a different AI model. If it still can't get a good result after several tries, it tells you so you can handle it yourself. This way, you never get bad work without knowing about it.",
    details: [
      "The Critic Module (powered by GPT-4o) automatically reviews every single task output",
      "It scores work on: completeness (did it finish everything?), accuracy (is it correct?), actionability (can you use it?), and professionalism (does it look good?)",
      "Each score is from 1 to 10. Higher is better",
      "If a task fails, the system automatically tries again using different AI models in this order: GPT-5 first, then Claude Sonnet, then Gemini Pro, then GPT-4o",
      "If ALL retries fail, the task gets flagged and you receive a notification so you can review it yourself",
      "The Quality Dashboard shows you pass rates (what percentage of tasks succeed), average scores, and how often recovery was needed",
    ]
  },
  {
    icon: Network, title: "Smart Universal AI Router", subtitle: "33 Providers, 600+ Models — Routing the Right Brain for Every Job", color: "text-cyan-400",
    desc: "MAARS Command has access to 600+ different AI models from 33 companies via the MAARS Universal API Gateway. The Smart Router classifies your prompt's task type (code, math, reasoning, creative, translation, research, etc.) and your current credit balance, then automatically picks the ideal model. Easy chats go to blazing-fast Groq or Cerebras. Complex reasoning goes to O4-mini or DeepSeek R1. Research goes to Perplexity Deep Research first. Developers get a maars-sk-* key and can call any model through a single OpenAI-compatible endpoint at /developer.",
    details: [
      "Premium Tier (hard tasks): O4, O4-mini, Claude Opus 4.6, Claude Sonnet 4.6, GPT-5, Grok 3 — smartest models for complex reasoning, legal, and research",
      "Standard Tier (medium tasks): GPT-4.1, Gemini 2.5 Pro, DeepSeek R1, Mistral Large, Cohere Command A — balanced quality and cost",
      "Economy Tier (easy tasks): Groq Llama 4 Scout, Cerebras Llama 3.3, Gemini Flash, DeepSeek Chat, Mistral Nemo — ultra-fast at rock-bottom cost",
      "Task classification: the router scores your prompt against 11 keyword banks (code, math, reasoning, legal, creative, translation, summary, research, data, vision, chat) to find the best match",
      "Credit-budget awareness: if you have ≤3 credits (micro), it routes to economy only. 11-50 credits = full routing. 51+ = best model, no restrictions",
      "Per-task preferred models: code → GPT-4.1 or Claude Sonnet 4.6 first; math → O4-mini or DeepSeek R1; research → Perplexity Deep Research; translation → DeepSeek or Qwen",
      "Manual override: pick any specific model in chat or set a default in Settings. Quality (economy/standard/premium) and task hint (code/math/etc.) can be saved as preferences",
      "All 33 providers are accessed directly via their own API keys — the MAARS Universal Key also covers OpenAI, Anthropic, and Gemini as a fallback",
    ]
  },
  {
    icon: Activity, title: "Autonomous Collaboration Engine", subtitle: "Agents Automatically Working Together", color: "text-indigo-400",
    desc: "When one agent finishes a task, the system automatically figures out if other agents should know about it. For example, if the Marketing agent creates a campaign plan, the system automatically tells the Creative agent (to make visuals) and the Technical agent (to build the landing page). This happens without you doing anything -- the agents coordinate by themselves.",
    details: [
      "All 458+ agents are organized into 9 work domains: executive, product, technical, creative, marketing, operations, finance, governance, and intelligence",
      "The system has built-in rules for which domains affect each other. Example: when marketing creates something, it triggers creative + technical",
      "There are 4 types of collaboration: information sharing (FYI), review request (please check this), data handoff (here's what you need), and coordination (let's work together)",
      "Each task creates up to 3 automatic collaborations to keep things focused and not overwhelm agents with notifications",
      "You can also manually start a collaboration between any two agents using the Collaboration Engine page",
    ]
  },
  {
    icon: Palette, title: "Universal Reference Intelligence", subtitle: "Learning Your Style From Examples", color: "text-pink-400",
    desc: "Give this system any example of writing or design you like, and it will study it to understand the style. Upload a marketing email you love? It extracts the writing tone, word choices, and messaging patterns. Upload a brand image? It identifies colors, design patterns, and visual style. It saves all of this as a \"Style Blueprint\" that other tools can use to create content that matches your brand perfectly.",
    details: [
      "Text Analysis: paste in any text (an email, article, ad copy) and it identifies the writing style, tone, target audience, and messaging patterns",
      "Image Analysis: upload any image and it detects brand elements, visual style, emotional tone, color palette, and design patterns",
      "The output is a \"Style Blueprint\" -- a saved profile that captures everything about that style",
      "You can reuse Style Blueprints in the Content Generator to create new content that matches the same style",
      "History tracking keeps all your previous analyses so you can go back to them anytime",
    ]
  },
  {
    icon: PenTool, title: "Content Generator", subtitle: "Creating On-Brand Content Instantly", color: "text-amber-400",
    desc: "Need to write a blog post, social media caption, email, or ad? Just tell this tool what you need, optionally select a Style Blueprint to match a specific tone, and it generates professional content for you. It's like having a writing team that can produce any type of content in seconds, and it always matches your brand voice.",
    details: [
      "8 content types you can generate: marketing copy, social media posts, emails, blog articles, ad copy, press releases, brand guidelines, and custom (anything else)",
      "Style Blueprint integration: pick a blueprint you created in Reference Intelligence, and the content will match that exact tone and style",
      "Length control: choose short (100-200 words), medium (300-500 words), or long (800-1500 words)",
      "Optional tone override: even with a blueprint, you can adjust the tone for specific pieces",
      "Full history: every piece of content you generate is saved. You can copy it, reuse it, or delete it",
    ]
  },
  {
    icon: Code, title: "Vibe Coding App Builder", subtitle: "Build Apps Just By Talking", color: "text-green-400",
    desc: "Describe an app you want to build using plain English, and this tool creates a complete working web application for you. No coding knowledge needed. You can say things like \"make me a todo list app with a dark theme\" and it builds it instantly. You can keep talking to modify it -- \"add a calendar view\" or \"change the color to blue\" -- and it updates in real time.",
    details: [
      "Chat-based interface: just describe what you want in normal English",
      "Creates complete HTML/CSS/JavaScript applications with modern design (Tailwind CSS)",
      "Live preview: see your app running in real-time right next to the chat",
      "Iterative modifications: keep chatting to change, add, or remove features",
      "Code view: switch to see the actual code if you want to learn or customize further",
      "Download: export your finished app as a file you can host anywhere",
    ]
  },
  {
    icon: Radio, title: "Agent Activity Monitor", subtitle: "Watching All Agents Work in Real-Time", color: "text-blue-400",
    desc: "This is a live dashboard that shows you what every AI agent is doing right now. It updates every 8 seconds using a real-time connection (WebSocket). You can see which agents are active, what they're working on, who they're talking to, and how fast they're completing tasks. Think of it like a security camera system, but for your AI workforce.",
    details: [
      "Real-time updates every 8 seconds using WebSocket (a fast, always-on internet connection)",
      "Shows agent status: which agents are active, idle, or working on tasks",
      "Communication flows: see messages being sent between agents (who sent what to whom)",
      "Task dependency graph: a visual map showing how tasks relate to each other and their current status",
      "Tool execution tracking: see when agents use tools (like web search or image generation) and how long each tool takes",
      "Pause/Resume: you can pause the live feed to examine a specific moment, then resume",
      "Connection indicator: shows if you're connected via WebSocket (fast), REST polling (slower backup), or Paused",
    ]
  },
  {
    icon: Lock, title: "Simulation vs. Execution Mode", subtitle: "A Safety Switch for Real-World Actions", color: "text-orange-400",
    desc: "MAARS Command has a master safety switch. In Simulation Mode (the default), agents can plan and think, but they CAN'T do anything in the real world -- no real emails are sent, no real calendar events are created, no real social media posts go live. Everything is pretend. When you're ready to go live, you flip the switch to Execution Mode, and agents can perform real actions. This keeps you safe while testing.",
    details: [
      "System-wide toggle: one switch controls ALL agents at once (found on the KPI Dashboard)",
      "Simulation Mode (default): all real-world actions return fake, safe responses. Nothing actually happens in the real world",
      "Execution Mode: agents send real emails via Gmail, create real Google Calendar events, and interact with real APIs",
      "Visual indicators: the UI clearly shows which mode you're in, so you always know if actions are real or simulated",
      "You can switch between modes at any time -- no restart needed",
    ]
  },
  {
    icon: Globe, title: "Real-World Action Layer", subtitle: "Letting Agents Do Things in the Real World", color: "text-teal-400",
    desc: "This is the system that actually connects agents to real-world services. Right now it supports Google Suite (Gmail for sending emails and Google Calendar for creating events). When an agent needs to send an email or schedule a meeting, this layer handles the actual sending. All actions are controlled by the Simulation/Execution toggle -- nothing real happens unless you explicitly allow it.",
    details: [
      "Google Gmail: agents can compose and send real emails on your behalf",
      "Google Calendar: agents can create, update, and manage calendar events",
      "OAuth 2.0 authentication: you securely connect your Google account (your password is never shared with MAARS)",
      "You connect and disconnect from the Settings page",
      "Integration status dashboard shows which services are connected and working",
      "The Personal Secretary agent is the one who actually performs these actions (other agents request through it)",
    ]
  },
  {
    icon: Server, title: "MAARS Universal API Gateway", subtitle: "600+ Models · 33 Providers · One OpenAI-Compatible Key", color: "text-purple-400",
    desc: "MAARS is a self-hosted universal AI gateway — on steroids. A single maars-sk-* API key lets you call any of 175,000+ models across 33 providers using the same OpenAI SDK you already use. MAARS smart routing aliases (maars/auto, maars/code, maars/fast...) automatically pick the best model for your task and budget. The full Developer Portal is at /developer.",
    details: [
      "OpenAI: GPT-5, GPT-4.1/mini/nano (1M ctx), GPT-4o, O4 & O4-mini & O3 & O3-pro (reasoning/math)",
      "Anthropic: Claude Opus 4.6 & 4.5 (deepest reasoning), Claude Sonnet 4.6 & 3.7 (creative + code), Claude Haiku 4.5 (fast + cheap)",
      "Google Gemini: Gemini 2.5 Pro (2M ctx research), Gemini 2.5 Flash (speed), Gemma 3 open models (1B–27B)",
      "xAI Grok: Grok-4 & Grok-4 Fast Reasoning (256K ctx), Grok-3, Grok-2 Vision — made by Elon Musk's xAI",
      "DeepSeek: DeepSeek V3-0324 (code + data, ultra cheap), DeepSeek R1-0528 (math + reasoning, open-source champ)",
      "Mistral AI: Mistral Large, Magistral Medium (reasoning), Codestral (code-specialist, 256K ctx), Pixtral Large (vision)",
      "Perplexity: Sonar Deep Research (live web research), Sonar Pro, Sonar Reasoning Pro — web-grounded answers",
      "Cohere: Command A (enterprise docs), Command R+ — optimized for business document retrieval",
      "Groq + Cerebras: blazing-fast open-source inference — Llama 4, Qwen QwQ-32B at sub-second latency",
      "Together AI (39 models), Fireworks AI (20), SambaNova (14), NVIDIA NIM (12), Novita AI (12), Lepton AI (8), Lambda Labs (6): open-source hosting",
      "AI21 Jamba (256K ctx), Moonshot Kimi (128K), Qwen/Alibaba (multilingual), Minimax AI, Inception AI (Mercury), Arcee AI, Amazon Bedrock (Nova), Yi, Zhipu, Doubao, Hyperbolic, Upstage, LLaMA, Writer, HuggingFace",
      "10 MAARS smart routing aliases: maars/auto, maars/smart, maars/economy, maars/premium, maars/code, maars/vision, maars/reasoning, maars/search, maars/fast, maars/standard",
      "Live model validation: before every call, the gateway checks the provider's live /models API and auto-fallbacks if a model is not yet live",
      "Webhooks: register HTTPS endpoints for budget alerts (75%/90%/100%), rate limit events, and request completion — signed with HMAC-SHA256",
    ]
  },
  {
    icon: Mic, title: "Voice Command Interface", subtitle: "Talk to MAARS Instead of Typing", color: "text-rose-400",
    desc: "Instead of typing, you can just talk. Click the microphone button, say what you want (like \"show me my agents\" or \"open the dashboard\"), and MAARS Command understands you and takes action. Your voice is converted to text using OpenAI's Whisper technology, which understands 50+ languages.",
    details: [
      "Click the microphone button in the Command Palette (or press / then click the mic icon)",
      "Speak naturally in any of 50+ supported languages",
      "Your speech is recorded using your browser's microphone",
      "OpenAI Whisper converts your speech to text in real-time",
      "The text automatically fills the search box, so you can navigate, search agents, or trigger actions",
      "Visual feedback: the mic pulses red while recording, shows a spinner while transcribing",
    ]
  },
  {
    icon: FileCode, title: "Admin Code Explorer", subtitle: "Browse the Entire Codebase", color: "text-sky-400",
    desc: "For admin users who want to look under the hood, the Code Explorer lets you browse every file in the MAARS Command codebase. You can navigate through folders, read any file with color-coded syntax highlighting, search for specific files, and even download the entire codebase as a ZIP file. It's like having a built-in file manager for the whole system.",
    details: [
      "Full file tree: browse all backend and frontend directories with expand/collapse folders",
      "Code viewer: read any file with line numbers, automatic language detection, and a copy button",
      "File search: find files by name across all directories",
      "ZIP export: download the complete codebase (backend + frontend) as a single ZIP file",
      "Language-colored icons: Python files are blue, JavaScript files are yellow, JSON is green, etc.",
      "Security: only admin users can access this feature, and path traversal attacks are blocked",
    ]
  },
  {
    icon: Archive, title: "Memory Governance", subtitle: "The AI's Long-Term Memory System", color: "text-violet-400",
    desc: "Just like humans remember important things, MAARS Command has a memory system. Memories are facts, decisions, preferences, and knowledge that agents learn over time. You can create, edit, and delete memories manually. Old or unimportant memories automatically fade over time (like forgetting what you had for lunch last month), keeping the system focused on what matters most.",
    details: [
      "Full control: create, read, update, and delete memory entries",
      "Category tagging: organize memories by type (facts, decisions, preferences, instructions, context)",
      "Version history: every change to a memory is tracked with timestamps and reasons for the change",
      "Time-decay scoring: memories become less relevant over time (30-day half-life). Frequently accessed memories stay stronger",
      "Relevance = (time decay score) + (how often it's accessed) + (importance rating you give it)",
      "Auto-pruning: you can preview and remove low-relevance memories to keep the system clean",
      "Usage statistics: see total entries, average relevance score, and breakdown by category",
      "500-entry limit per user with a percentage indicator showing how much you've used",
    ]
  },
  {
    icon: Sparkles, title: "Agent Memory Auto-Learning", subtitle: "Agents Get Smarter After Every Task", color: "text-cyan-400",
    desc: "Every time an agent completes a task, the system automatically extracts the most important lessons learned and saves them as memories. Over time, this creates a growing knowledge base that makes every agent smarter. It's like how you get better at your job the more experience you have -- except the AI remembers everything perfectly.",
    details: [
      "After every completed task, GPT-4o-mini automatically extracts 1-3 key learnings",
      "Learnings are saved as: facts, decisions, preferences, instructions, or context",
      "Each learning gets an importance score based on how significant the task was and what was learned",
      "Near-duplicate detection: if the system already knows something similar, it won't save a duplicate",
      "Auto-learned entries are marked with a special cyan badge in the Memory Governance page so you can tell them apart from manually created memories",
      "This runs in the background and never slows down task completion",
    ]
  },
  {
    icon: Terminal, title: "Command Palette", subtitle: "Instant Search & Navigation (Like Spotlight)", color: "text-yellow-400",
    desc: "Press the / key (or Cmd+K on Mac) and a search box pops up. Start typing anything -- a page name, an agent name, or an action -- and it instantly shows matching results. Select one and you're taken there immediately. It's just like Spotlight on Mac or the search bar in VS Code. It searches across all 50+ pages, all 458+ agents, and all quick actions.",
    details: [
      "Open it with / key or Cmd+K (Ctrl+K on Windows)",
      "Searches across: all pages (Dashboard, Agents, Chat, etc.), all 458+ agents, and quick actions",
      "Keyboard navigation: use arrow keys to move up/down, Enter to select, Escape to close",
      "Recent searches: your last searches are remembered so you can quickly redo them",
      "Results are grouped into categories: Recent, Pages, Agents, Quick Actions",
      "Voice command: click the microphone icon to search by speaking instead of typing",
      "Also accessible from the search button in the sidebar",
    ]
  },
  {
    icon: Users, title: "Agent Team Builder", subtitle: "Create Custom Teams for Projects", color: "text-indigo-400",
    desc: "Pick agents from the full 458+ agent workforce and group them into custom teams. Give each team a name and a mission (like \"Q1 Marketing Team\" or \"Product Launch Crew\"). This makes it easy to organize agents for specific projects, see which skills your team covers, and quickly deploy the right group of agents for any job.",
    details: [
      "Search and filter agents by name, role, network category, or specific capability",
      "Create as many teams as you want with custom names and mission descriptions",
      "Select agents from the full 458+ workforce pool -- no limits on team size",
      "Team cards show: member count, network coverage (how many different specialties), and avatar previews",
      "Edit or delete teams anytime",
      "Teams are saved to your account so they persist between sessions",
    ]
  },
  {
    icon: Gauge, title: "Trust Analytics & Scoring", subtitle: "Rating How Reliable Each Agent Is", color: "text-emerald-400",
    desc: "Every agent gets a trust score from 0 to 100 based on its track record. Did it complete tasks on time? Were the results good? Did it cause any errors? The Trust Analytics dashboard shows you which agents are your most reliable performers, which ones need improvement, and how trust levels are trending over time. It's like a performance review for your AI workforce.",
    details: [
      "Trust scores range from 0 (never trust) to 100 (completely reliable)",
      "Scores are calculated from: success rate (did tasks complete?), latency (how fast?), quality (how good?), and consistency (same quality every time?)",
      "Trust Distribution chart: see how many agents fall into Excellent (90-100), Good (70-89), Fair (50-69), and Poor (below 50) ranges",
      "Top Performers: a ranking of your best agents",
      "Needs Improvement: a ranking of agents that need attention",
      "Anomaly detection: if an agent's performance suddenly drops, the system flags it",
      "Historical trend graphs: see how trust scores change over time",
    ]
  },
  {
    icon: Zap, title: "Workflow Builder", subtitle: "Create Automated Step-by-Step Processes", color: "text-amber-400",
    desc: "A visual drag-and-drop tool for building automated workflows. Think of it like building a flowchart: connect different steps together, and MAARS Command runs them automatically. For example: \"When a new lead comes in, have the Research agent look them up, then have the Sales agent write a personalized email, then have the Secretary agent send it.\"",
    details: [
      "Visual canvas: drag and drop nodes (steps) onto a canvas and connect them with lines",
      "Node types: Agent Task (assign work to an agent), Decision (if/then branching), Parallel Split (do multiple things at once), Merge (wait for all parallel tasks to finish), Trigger (what starts the workflow)",
      "Conditional branching: set rules like \"if the quality score is above 7, proceed; otherwise, redo\"",
      "Workflow templates: pre-built workflows for common business processes to get you started",
      "Execution history: see every time a workflow ran, how long it took, and if anything failed",
      "Triggers: start workflows on a schedule (daily, weekly) or when specific events happen",
    ]
  },
  {
    icon: Terminal, title: "MAARS Developer API Gateway", subtitle: "One Key · 600+ Models · 33 Providers · OpenAI-Compatible", color: "text-indigo-400",
    desc: "MAARS is a self-hosted universal AI gateway — on steroids. Every registered user gets a maars-sk-* API key. With one key and a single base_url change, developers can call any of 175,000+ AI models across 33 providers using their existing OpenAI SDK code. The gateway validates models live against provider APIs, automatically falls back when a model is unavailable, fires signed webhooks on budget thresholds, and lets you run side-by-side model comparisons in one request.",
    details: [
      "Developer Portal at /developer: 4 tabs — My API Key (masked/reveal/copy), Model Browser (175,000+ models, searchable, filterable), Playground (test any model in browser), Quickstart (copy-paste code for Python/JS/cURL)",
      "OpenAI-compatible: POST /v1/chat/completions — change base_url from api.openai.com to your domain. No other code changes needed",
      "609+ real models: OpenAI (35), Groq (35), Together AI (77), Novita AI (56), Fireworks AI (44), HuggingFace (38), Qwen/Alibaba (32), Mistral (31), Lepton AI (28), NVIDIA NIM (27), SambaNova (20), Lambda Labs (20), Cerebras (18), Google/Gemini (18), Hyperbolic (14), Anthropic (13), DeepSeek (12), xAI (11), Zhipu/GLM (11), ByteDance/Doubao (10), Cohere (9), Moonshot (8), Meta Llama API (6), Perplexity (6), 01.AI/Yi (5), Writer (5), AI21/Jamba (4), Amazon Bedrock (4), Minimax (4), Upstage (3), Arcee AI (3), Inception AI (2), ElevenLabs (voice)",
      "10 MAARS smart routing aliases: maars/auto, maars/smart, maars/economy, maars/standard, maars/premium, maars/code, maars/vision, maars/reasoning, maars/search, maars/fast",
      "Live model validation: before each call, checks provider's /models API (cached 1 hour). If model not found, skips to fallback and includes model_warning in response",
      "Auto-fallback chain: tries up to 4 providers on failure — GPT-4.1 → Claude Sonnet → Gemini Flash → DeepSeek",
      "Webhooks: register HTTPS endpoints for budget.75, budget.90, budget.100, rate_limit.exceeded, request.completed — all signed with HMAC-SHA256",
      "Model comparison: POST /v1/models/compare runs the same prompt on up to 4 models in parallel and returns latency, cost, tokens, and content per model side-by-side",
      "Real token billing from provider responses, not estimates. Full parameter passthrough: temperature, top_p, max_tokens, tools, vision, seed, response_format",
      "Budget enforcement and per-key rate limiting (configurable RPM). All usage logged to gateway_usage_logs for admin P&L tracking",
    ]
  },
  {
    icon: Briefcase, title: "Campaign Builder", subtitle: "Plan Multi-Channel Marketing Campaigns", color: "text-pink-400",
    desc: "Plan and run marketing campaigns across multiple channels (email, social media, web, ads) all in one place. Define your campaign goals, pick which channels to use, and let AI agents create content variations for each channel. Track how each campaign performs and let the AI optimize your budget allocation.",
    details: [
      "Multi-channel support: email, social media, website, and paid advertising",
      "AI-generated content: agents create different versions of your message for each channel automatically",
      "A/B testing: create multiple variations and see which performs better",
      "Performance tracking: see opens, clicks, conversions, and engagement for each campaign",
      "Budget allocation: set your budget and let the AI suggest how to split it across channels",
      "Campaign templates and scheduling: plan campaigns in advance and have them launch automatically",
      "Works with Content Generator and Reference Intelligence for on-brand content",
    ]
  },
  {
    icon: Share2, title: "Social Media Command Center", subtitle: "10 Platforms · AI-Powered Posting, Messaging & Geo-Targeted Boosting", color: "text-teal-400",
    desc: "MAARS agents can now operate across 10 major social media and messaging platforms simultaneously. From composing geo-targeted posts in the right language, to sending cold DMs, running multi-region ad boosts, broadcasting on WhatsApp and Telegram, and making cold calls via Twilio — all from a single command center. This isn't traditional social media management. It's an AI-driven omnichannel growth engine.",
    details: [
      "10 platforms connected: Facebook, Instagram, Twitter/X, TikTok, WhatsApp Business, Viber, LINE, LinkedIn, YouTube, Telegram",
      "Post & Publish: agents auto-generate and publish content across all connected platforms in one click — with platform-specific formatting",
      "Geographic Targeting: select target regions (North America, Southeast Asia, Middle East, etc.) and content is auto-published with the right language for each region",
      "Non-Traditional Boosting: beyond basic boosts — A/B test ad creatives per region, TikTok Spark Ads, LinkedIn Lead Gen forms, Facebook dynamic creatives, YouTube TrueView campaigns",
      "Auto-Translation: agents translate your content to Japanese (Japan), Arabic (Middle East), Thai (Southeast Asia), Hindi (South Asia), etc. — automatically matched to your target region",
      "Cold Email Outreach: send personalized cold emails via SendGrid or Resend with geo-aware subject lines and body copy",
      "Cold Calling: initiate Twilio voice calls with AI-generated scripts delivered in the target region's language (English, Spanish, French, Arabic, Hindi, and more)",
      "Direct Messaging: send DMs on WhatsApp, Instagram, Viber, LINE, and Telegram — including WhatsApp Business templates and LINE rich messages",
      "Reply to Everything: agents can reply to comments, mentions, and DMs across all platforms — in the right language",
      "Scheduling: queue posts, calls, meetings, and campaigns for future dates with full calendar view",
      "Multi-Platform Campaigns: one campaign name, content in, agents adapt and post across all selected platforms simultaneously",
      "Omnichannel Analytics: track reach, impressions, clicks, and conversions per platform and per geographic region",
    ]
  },
  {
    icon: Layers, title: "Task Graph Execution Kernel", subtitle: "DAG-Based Task Orchestration with Dependency Resolution", color: "text-sky-400",
    desc: "The Kernel turns any goal into a directed-acyclic task graph (DAG) and executes it. Instead of running steps one-by-one, it figures out which tasks depend on which, runs independent branches in parallel, and holds dependent tasks until their inputs are ready. Built-in retry logic, budget enforcement per branch, and checkpointed resumption let a workflow survive provider outages, human pauses, and multi-hour runs without losing state.",
    details: [
      "131 dedicated Infinity endpoints under /api/infinity (task-graphs, goals, scheduler, budget, policies, runtime, recovery, workers, environments)",
      "Task graph compiler: accepts a natural-language goal → emits a DAG with nodes (agent/tool calls), edges (data dependencies), checkpoints, and rollback markers",
      "Parallel branch execution: independent branches run concurrently, respecting per-branch credit budgets and per-agent rate limits",
      "Deterministic resumption: every step emits a checkpoint so a halted graph can resume mid-run without re-executing completed nodes",
      "Scheduler + worker pool: /kernel/scheduler.py dispatches ready nodes to worker processes; job queue tracked at /api/infinity/workers/*",
      "Budget controller enforces per-user, per-agent, per-environment credit caps — hits a ceiling, the graph pauses instead of overspending",
      "Visual task-graph page (frontend/src/pages/TaskGraphs.jsx) renders every node, edge, status, and cost in real time",
    ]
  },
  {
    icon: Gauge, title: "10-Tier Autonomy Framework", subtitle: "From Full Human Approval (T1) to Unsupervised Autonomy (T10)", color: "text-orange-400",
    desc: "Every agent runs at one of ten autonomy tiers. Tier 1 means every action needs explicit human approval before it leaves the sandbox. Tier 10 means the agent operates unsupervised within its budget and policy envelope. Tiers 2-9 interpolate — some tools are pre-approved, some actions auto-execute if trust score > threshold, some require dual-agent cross-verification. You dial autonomy per agent, and the kernel enforces the tier on every tool call.",
    details: [
      "Tier 1 — Supervised: every action queues for human approval in the Approvals page",
      "Tier 2-3 — Assisted: non-destructive reads auto-approve; writes and external actions require approval",
      "Tier 4-6 — Delegated: pre-approved tools run freely; high-cost or high-impact actions gate on approval",
      "Tier 7-9 — Empowered: all allow-listed actions run; only novel tool calls or policy edge cases escalate",
      "Tier 10 — Autonomous: full autonomy within budget + policy; post-facto audit only",
      "Per-agent override: set any agent's tier from the Brain Profiles page; changes logged immutably",
      "Trust-gated elevation: an agent's effective tier is min(assigned_tier, ceil(trust_score / 10)) — low trust can't bypass review",
      "Tier enforcement lives in backend/governance/autonomy.py and is checked on every tool invocation before execution",
    ]
  },
  {
    icon: Globe, title: "Embedded Browser Runtime", subtitle: "Self-Hosted Chromium · Multi-Tab · Three-Way Shared Control · Autonomous Vision Agent", color: "text-blue-400",
    desc: "MAARS ships with a full Chromium runtime — not a call out to a remote browser service, not a thin iframe. The binary lives inside the MAARS install under backend/browser_data/, so when you container-ize or ship MAARS the browser comes with it. Agents, the orchestrator, and the human user all drive the same session: when the autonomous BrowserAgent hits a 2FA screen it hands the driver lock to you, you complete the one-time code, and the agent picks back up where it left off — cookies preserved, no re-login. Every one of 29 integrations has a click-to-connect button that opens the right OAuth URL in a tagged tab and optionally invokes the agent to walk through the flow.",
    details: [
      "Chromium runs on a dedicated OS thread with a ProactorEventLoop — sidesteps the uvicorn --reload SelectorEventLoop subprocess bug on Windows",
      "Multi-tab per session: Chrome-style tab strip, click to switch, × to close, + for blank — context shared across tabs so cookies/localStorage are unified",
      "Three-way shared control: driver ∈ {shared, user, agent, system}; take-control / release-control via REST, WS message, or UI buttons",
      "Autonomous BrowserAgent (services/browser_agent.py): perceive → decide (vision) → act loop with 2FA / CAPTCHA / payment hand-off to the human",
      "Vision fallback chain: OpenAI GPT-4o → Anthropic Claude. Returns strict JSON { kind, x, y, text, url, reason, confidence } — callable directly via browser_see_and_act",
      "WebSocket live view: event-driven or continuous streams, PNG (lossless) or JPEG (~10× smaller), 1–24 fps, user input events forwarded back to Playwright",
      "Integration Connect: POST /api/browser/integrations/{id}/connect — opens the right login URL in a tagged tab, optional run_agent=true drives OAuth automatically",
      "Governance: per-env domain allow/deny policy (fail-closed), per-user browser-minutes daily budget (default 60 min), 429 on exhaust",
      "11 agent tools: browser_open, browser_navigate, browser_click, browser_fill, browser_type, browser_extract, browser_screenshot, browser_evaluate, browser_close, browser_see_and_act, browser_run_goal",
      "32 routes under /api/browser/* incl. sessions, tabs, take/release-control, screenshot, extract, evaluate, agent/run (SSE), policy/domains, policy/budget, usage, integrations/{id}/connect",
      "Frontend at /browser: session sidebar, integration grid (29 chips), tab strip, URL bar, driver status strip, agent goal runner with SSE event log, fullscreen mode, stream config",
    ]
  },
  {
    icon: Building, title: "Multi-Environment Segregation", subtitle: "Production · Staging · Sandbox · Simulation — Isolated Policies & Budgets", color: "text-teal-400",
    desc: "MAARS ships with four isolated execution environments. Agents, workflows, and data in Simulation never touch Production. Each environment has its own budget multiplier, policy set, data retention rule, and audit trail. Promote from Sandbox → Staging → Production only after Verification Civilization signs off. Simulation runs at zero real cost (all external calls mocked) so you can stress-test autonomous behavior without risk.",
    details: [
      "Simulation: cost multiplier = 0, all integrations mocked, full logging, 7-day retention — safe for dry-runs and chaos testing",
      "Sandbox: real calls to test-mode APIs (Stripe test keys, Gmail test inbox), 30-day retention, relaxed policies",
      "Staging: production-like credentials, strict policies, 90-day retention, required for release promotion",
      "Production: real money, real users, immutable audit, 7-year retention, all circuit breakers enabled",
      "Environment-scoped budgets: cap spend per env independently — e.g., $10/day sandbox, $2,000/day production",
      "Env-scoped trust scores: an agent's trust in sandbox doesn't inherit to production until it's promoted",
      "Managed via backend/governance/environments.py and /api/infinity/environments/* endpoints",
    ]
  },
  {
    icon: CheckCircle, title: "Verification Civilization", subtitle: "Multi-Verifier Fact-Checking with 6-Dimensional Consensus Scoring", color: "text-emerald-400",
    desc: "Every factual claim an agent makes gets cross-verified by 2-4 independent verifiers (different models, different prompts, different retrieval sources). A claim only passes if consensus is reached across six dimensions: factual accuracy, source grounding, logical coherence, completeness, bias detection, and temporal freshness. Disagreements escalate to a human reviewer or a higher-tier verifier. The whole pipeline is inspired by Popperian epistemology — agents don't just \"answer,\" they make claims that survive attempted refutation.",
    details: [
      "6-dimensional scoring: factual accuracy, source grounding, logical coherence, completeness, bias, temporal freshness (0-100 each)",
      "Multi-model crosscheck: the same claim gets verified by e.g. Claude Opus + Gemini 2.5 Pro + DeepSeek R1 — disagreement = flag",
      "Source citations mandatory: every fact cites a retrievable source from the knowledge_chunks collection or live web search",
      "Hallucination detector: detects confabulation patterns (unverifiable specifics, made-up URLs, invented quotes) and quarantines the response",
      "Escalation routes: low-confidence → retry with higher-tier model; persistent disagreement → queue for human review",
      "Verification metrics tracked at /api/infinity/verification/stats — see pass rate, top failure modes, per-agent accuracy",
      "Engine lives in backend/verification/engine.py; exposed via /api/infinity/verification/* (4 routes)",
    ]
  },
  {
    icon: Brain, title: "Hierarchical Memory System", subtitle: "Working · Episodic · Semantic · Knowledge Graph — 4 Tiers, Automatic Decay", color: "text-violet-400",
    desc: "Human-inspired memory architecture with four tiers. Working memory holds the current task's context (capped at 50 items). Episodic memory logs every event chronologically for later recall. Semantic memory stores concept embeddings for similarity search. The Knowledge Graph captures entity-relationship edges so agents can traverse \"who knows what, connected to which, via which relationship.\" Old items automatically decay unless reinforced by usage, keeping the system focused without manual pruning.",
    details: [
      "Working memory (backend/memory_system/working.py): per-task scratchpad, 50-item cap, purged on task completion",
      "Episodic memory (episodic.py): time-ordered event log with time-decay scoring (30-day half-life), reinforces on recall",
      "Semantic memory (semantic.py): vector embeddings, cosine-similarity retrieval, concept clustering",
      "Knowledge Graph (knowledge_graph.py): entity + relationship store, traversable, Neo4j-style queries",
      "16 REST endpoints under /api/infinity/memory/* for CRUD, search, promotion between tiers, and decay tuning",
      "Auto-promotion: frequently-accessed episodic items get promoted to semantic; heavily-referenced semantic clusters get nodes in the graph",
      "500-entry soft cap per user with auto-pruning of lowest-relevance items when full",
      "Full UI at frontend/src/pages/MemoryHierarchy.jsx with tier breakdowns, decay charts, and per-entry relevance scoring",
    ]
  },
  {
    icon: RefreshCw, title: "Recovery & Incident Response", subtitle: "Quarantine · Rollback · Retry — Automatic Blast-Radius Containment", color: "text-rose-400",
    desc: "When something breaks (agent misbehavior, provider outage, runaway spend, repeated verification failure), the Recovery system isolates the problem instead of letting it cascade. Misbehaving agents get quarantined (tier forced to 1, tools stripped, flagged for review). Broken task graphs roll back to the last clean checkpoint. Transient failures retry with exponential backoff across alternate providers. Every incident gets a root-cause record with timeline, blast radius, and remediation steps.",
    details: [
      "Quarantine: an agent flagged for review loses all tools and drops to tier 1 until a human clears it",
      "Checkpointed rollback: any task graph can roll back to its last successful checkpoint — partial progress preserved",
      "Smart retry: failed LLM calls retry with a different model (GPT-5 → Claude Sonnet → Gemini Pro → GPT-4o) before escalating",
      "Incident ledger: every fault creates an incident record with timeline, severity, affected users/agents, and linked audit entries",
      "Circuit breakers (governance/circuit_breaker.py): 5 default breakers monitor spend spikes, error rate, retry storms, provider downtime, policy violations",
      "Recovery endpoints (/api/infinity/recovery/*): 5 routes for quarantine, rollback, retry, status, clear",
      "Post-incident reports auto-generated with root cause, blast radius, remediation, and preventive action taken",
    ]
  },
  {
    icon: FileCheck, title: "Approval Workflow Gates", subtitle: "Human-in-Loop Execution · Approve · Reject · Edit · Escalate", color: "text-blue-400",
    desc: "When an agent hits a step that requires explicit approval (per its autonomy tier, per a policy, or per a workflow gate), the action queues in the Approvals page. A human reviews the proposed action, the agent's reasoning, the expected cost/impact, and signs off — or rejects, edits the payload, or escalates to a higher role. Every decision is logged immutably with approver identity, timestamp, and rationale. The agent resumes from the gate with the approved (or modified) payload.",
    details: [
      "Gate types: tool-call approval, budget exceedance, policy exception, cross-environment promotion, high-impact-action review",
      "Approver experience: rich preview of proposed action (full prompt, parameters, cost estimate, similar past actions)",
      "Decision options: Approve · Reject with reason · Edit payload and approve · Escalate to role",
      "Multi-signature gates: high-risk actions can require 2+ approvers before proceeding",
      "SLA tracking: gates that sit unapproved past a deadline auto-escalate or auto-timeout per policy",
      "Every decision written to immutable audit log — who approved what, when, why, with what edits",
      "Backend: /kernel/approval_controller.py + 7 endpoints under /api/approvals and /api/infinity/approvals/*",
    ]
  },
  {
    icon: Database, title: "Knowledge Base & RAG Engine", subtitle: "Document Uploads · Per-Agent Knowledge · Cited Retrieval", color: "text-purple-400",
    desc: "Upload PDFs, DOCX, Markdown, or plain text and attach them to any agent. The Knowledge Base chunks and embeds each document, stores the chunks in MongoDB's knowledge_chunks collection, and retrieves the top-K relevant chunks at chat time. Every agent answer cites the exact source chunks it drew from. Combined with the 58k skill library and live web search, every agent grounds its replies in three retrieval sources: skills (curated), uploads (yours), and web (live).",
    details: [
      "Supported upload formats: PDF (via PyMuPDF), DOCX (python-docx), Markdown, plain text; up to 25 MB per file",
      "Automatic chunking: semantic paragraph chunks with 200-token overlap for retrieval quality",
      "Per-agent scoping: attach a document to one agent or a team — retrieval only pulls from that agent's documents",
      "Cited retrieval: every chat response shows which chunks (with doc title + page/section) grounded each claim",
      "Three-layer RAG: agent's skill library (from .claude/skills/) + its knowledge base (your uploads) + live web search (Perplexity)",
      "GET /agents/{id}/brain exposes the full chunk ledger for any agent — transparent debugging",
      "UI: KnowledgeBaseTab with upload, preview, chunk inspector, and re-embed controls",
      "Powered by backend/services/rag_service.py + 5 routes under /api/knowledge-base",
    ]
  },
  {
    icon: Network, title: "Integration Hub", subtitle: "29 External Providers · OAuth, API Keys, Webhooks — One Control Plane", color: "text-cyan-400",
    desc: "Every external service MAARS talks to is configured through one Integration Hub. OAuth providers (Google Suite, GitHub), API-key providers (Stripe, Twilio, SendGrid, ElevenLabs, all 33 LLM providers), webhook-based integrations (Slack, custom), and the self-hosted Embedded Browser all share the same credential vault, status dashboard, rate-limit tracker, and health checker. Flip an integration on/off globally; rotate keys without code changes; see per-integration call counts and error rates at a glance.",
    details: [
      "29 integrations: Stripe, Gmail, Google Calendar, Twilio, SendGrid, ElevenLabs, Whisper, GitHub, Salesforce, HubSpot, Shopify, Airtable, Slack, Zapier-style webhooks, Embedded Browser (self-hosted Chromium), plus all 33 LLM providers",
      "Categorized: Payments · Email · Calendar · SMS/Voice · CRM · E-commerce · Data · Dev Tools · Social Media · Search · Voice/Audio · LLM",
      "OAuth flows for Google Suite and GitHub; API-key config for the rest; signed-webhook receivers for inbound events",
      "Per-integration health dashboard: call count, success rate, p95 latency, last error, circuit-breaker state",
      "Integration-scoped audit: every external call logs to immutable audit trail with masked credentials",
      "Hot-swap credentials: rotate a key in Settings, live traffic fails over without downtime",
      "Backend: /routes/admin.py /admin/integrations/* + services/integration_service.py",
    ]
  },
  {
    icon: Search, title: "Product Intelligence Scanner", subtitle: "Real-Time Competitive Research — Pricing, Features, Positioning", color: "text-indigo-400",
    desc: "Point MAARS at a product URL, a company, or a market segment and the Product Scanner builds a living intelligence file. It pulls pricing tiers, feature lists, recent announcements, social sentiment, funding rounds, review aggregates, and positioning language — then keeps refreshing on a schedule. Agents across the Growth, Sales, Research, and Strategic networks use these files to plan campaigns, write competitive battlecards, and flag market shifts.",
    details: [
      "Scans: product pages, pricing pages, About/company pages, Crunchbase/LinkedIn public data, review sites, social mentions",
      "Extracts: pricing tiers, feature matrix, recent product updates, team size, funding stage, Glassdoor ratings, trust signals",
      "Living files: schedule a re-scan daily/weekly/monthly; diff detector surfaces material changes",
      "Competitive battlecards: one click turns a product file into a battlecard (their claims → our response + proof points)",
      "11 endpoints under /api/products for scan, catalog CRUD, subscribe-to-changes, export",
      "Integrated with CampaignBuilder and ContentGenerator so competitive insights flow directly into generated content",
      "Backend: backend/services/product_scanner.py",
    ]
  },
  {
    icon: TrendingUp, title: "Venture Portfolio & Enterprise KPIs", subtitle: "Multi-Product Tracking · Stage Gates · Metrics Framework", color: "text-green-400",
    desc: "MAARS Command can run as the OS for a whole portfolio of ventures — each with its own agent team, budget, KPIs, stage gate, and runway. The Enterprise layer tracks revenue/burn/retention/NPS per venture, enforces stage gates (idea → MVP → PMF → scale → profit), and surfaces cross-venture benchmarks. If a venture misses two consecutive stage gates, the portfolio manager escalates a decision: double down, pivot, or sunset.",
    details: [
      "Per-venture: agent team, budget, KPIs, OKRs, stage, runway, founder, cap table stub",
      "Stage gates: 5 stages (Idea · MVP · PMF · Scale · Profit) with exit criteria per stage — enforced automatically",
      "KPI tracking: revenue, burn, runway, retention, NPS, CAC, LTV — pulled from connected integrations",
      "Cross-venture benchmarks: anonymous comparisons against portfolio peers (e.g., \"your NPS is in the bottom quartile\")",
      "Quality metrics framework: 22 endpoints under /api/enterprise covering KPIs, collaborations, ventures, quality, approvals",
      "Decision intelligence: automated quarterly reviews produce double-down / pivot / sunset recommendations with evidence",
      "UI: VenturePortfolio.jsx with portfolio grid, stage gates, KPI charts, and decision inbox",
    ]
  },
  {
    icon: BookOpen, title: "Skill Library", subtitle: "58,000+ Curated Skills — Auto-Matched & Ingested Per Agent", color: "text-lime-400",
    desc: "MAARS ships with a massive library of 58,422 Claude Code skills at .claude/skills/. Each skill is a self-contained Markdown document with a YAML front-matter (name + description) and optional reference files (scripts, docs, evals). When you create a new agent, a keyword-matcher instantly picks the skills whose topics align with that agent's role, description, and capabilities, then chunks the Markdown and writes the chunks into the MongoDB knowledge_chunks collection so the agent can retrieve them during chat (RAG). You can also bulk-ingest the entire library for all agents at once via the ingest script. The original unfixed copies are kept at .claude/skills_backup/ as a safety net.",
    details: [
      "58,422 SKILL.md files, each with valid YAML front-matter — covers A/B testing, accessibility, ad creative, aluminum rolling, animal handling, Axum, AWS, booking flows, carbon-lang, creative frontends, data arch, delivery, delon, DevOps docs, drift check, frugal rerouter, healthcare, hyper-casual games, Kubernetes, LinkedIn ads, MkDocs, NestJS, Next.js, Norway roads, PostgreSQL, React, reviewing code, Salesforce, Vue, and tens of thousands more",
      "Automatic matching on agent creation: services/skills_service.py runs match_skills_for_agent(agent) against the agent's role, description, capabilities, network, and tags using SKILL_KEYWORDS, then calls ensure_agent_skills() to chunk and write the matched skills to db.knowledge_chunks",
      "Provider knowledge pack: match_providers_for_agent() also ships LLM-provider cheat sheets (from data/provider_skills.py) so agents know the strengths of every model they can call",
      "Zero-broken-YAML guarantee: every front-matter parses cleanly under yaml.safe_load; no stale \"hooks\" fields (hooks belong in settings.json, not skill frontmatter); description capped at 1024 chars and collapsed to one line",
      "Bulk ingest on demand: cd backend && python scripts/ingest_skills.py re-processes all agents — use --force to overwrite, --agents-only or --providers-only to narrow scope",
      "Knowledge chunks stored with source=\"skill\" + skill_name + doc_id so you can audit exactly which skill-chunks each agent has in its brain",
      "RAG-ready: routes/chats.py retrieves matching chunks during chat so agents ground their replies in the skill library instead of hallucinating",
      "Per-agent brain viewer: GET /agents/{agent_id}/brain returns every knowledge chunk currently loaded for that agent — full transparency into what any agent \"knows\"",
      "Extensible: drop a new folder under .claude/skills/<name>/ with a SKILL.md, and the next agent creation or ingest run picks it up automatically",
    ]
  },
  {
    icon: Key, title: "Universal Gateway Key — Pay As You Go", subtitle: "65% AI Budget · 35% Platform · Credits On Demand", color: "text-amber-400",
    desc: "The MAARS Universal Key is now fully pay-as-you-go. Top up any amount — no subscriptions required. 65% of every payment goes directly to AI model costs (OpenAI, Anthropic, Google, and 30 other providers). The remaining 35% covers platform infrastructure, routing, failover, monitoring, and support. Credits are issued instantly. Each credit ≈ one LLM API call, priced by the model used.",
    details: [
      "Pay any amount from $5 to $10,000 USD (or BDT equivalent) — no monthly commitment",
      "65% allocation: goes to your AI model budget — funds actual API calls to OpenAI, Anthropic, Google, DeepSeek, Groq, etc.",
      "35% allocation: covers MAARS infrastructure — routing layer, failover logic, monitoring dashboards, logging, support, and platform development",
      "Credits issued instantly: your AI budget is converted to MAARS credits at ~16.67 credits per $1 AI budget",
      "Real-time tracking: watch your credit balance and USD AI budget update in real-time after every LLM call",
      "One key, every provider: your maars-sk-* key unlocks access to all 33 providers and 600+ models — smart routing picks the best model for each task",
      "Budget transparency: every top-up shows the exact split — how much goes to AI costs vs. platform. No hidden fees",
      "Transaction history: full log of every top-up with amount paid, AI budget allocated, platform portion, and credits issued",
      "Usage stats: see breakdowns by provider, model, task type, and quality tier — understand exactly how your credits are spent",
      "Top-up anytime: credits never expire during your subscription period. Top up $10 today, $500 next month — fully flexible",
    ]
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
  { name: "OpenAI", color: "text-emerald-400", dotColor: "bg-emerald-400", desc: "The company behind ChatGPT. Their GPT-5 is the world's most capable text model. O4 pushes reasoning to new limits.", models: [
    { name: "GPT-5", tier: "Flagship", desc: "Most powerful all-around model — coding, writing, analysis" },
    { name: "GPT-4.1 / Mini / Nano", tier: "Fast", desc: "Latest generation: 4.1 for quality, Mini for balance, Nano for speed" },
    { name: "GPT-4o", tier: "Fast", desc: "Multimodal: understands images and text together" },
    { name: "O4 / O4-mini", tier: "Reasoning", desc: "Next-gen deep reasoning — best for math, code, and logic" },
    { name: "O3 / O3-mini", tier: "Reasoning", desc: "Frontier reasoning for hardest analytical tasks" },
  ]},
  { name: "Anthropic", color: "text-orange-400", dotColor: "bg-orange-400", desc: "Makes the Claude 4.6 family. Known for being very safe, thoughtful, and exceptional at creative writing and nuanced reasoning.", models: [
    { name: "Claude Sonnet 4.6", tier: "Flagship", desc: "Best balance of intelligence and speed — code, creative, legal" },
    { name: "Claude Opus 4.6", tier: "Premium", desc: "Deepest reasoning and most thoughtful responses available" },
    { name: "Claude Haiku 4.5", tier: "Economy", desc: "Ultra-fast for quick summaries and simple responses" },
  ]},
  { name: "Google Gemini", color: "text-blue-400", dotColor: "bg-blue-400", desc: "Google's AI models. Gemini understands text, images, code, and data all at once.", models: [
    { name: "Gemini 2.5 Flash", tier: "Fast", desc: "Lightning-fast with excellent quality — great default for most tasks" },
    { name: "Gemini 2.5 Pro", tier: "Flagship", desc: "Research-grade: data analysis, vision, long documents" },
    { name: "Gemini 3 Flash / Pro", tier: "Fast", desc: "Next-generation speed and multimodal capability" },
  ]},
  { name: "xAI (Grok)", color: "text-sky-400", dotColor: "bg-sky-400", desc: "Made by Elon Musk's xAI company. Grok-4 is xAI's frontier reasoning model with tool calling and vision. All models have 256K context.", models: [
    { name: "Grok-4", tier: "Flagship", desc: "xAI's frontier reasoning model — tool calling, vision, 256K context" },
    { name: "Grok-4 Fast / Reasoning", tier: "Fast", desc: "High-speed variants: non-reasoning for speed, reasoning for CoT" },
    { name: "Grok-3", tier: "Premium", desc: "1 million token context — reads entire books, strong long-form reasoning" },
    { name: "Grok-3 Mini", tier: "Economy", desc: "Affordable Grok for everyday tasks" },
    { name: "Grok-2 Vision", tier: "Fast", desc: "Multimodal Grok with image understanding" },
  ]},
  { name: "DeepSeek", color: "text-teal-400", dotColor: "bg-teal-400", desc: "Chinese AI company offering incredibly affordable models. Great value for money.", models: [
    { name: "DeepSeek Chat", tier: "Economy", desc: "128K context, one of the cheapest AI models available anywhere" },
    { name: "DeepSeek Reasoner", tier: "Reasoning", desc: "Specializes in math, logic, and step-by-step problem solving" },
  ]},
  { name: "Mistral AI", color: "text-violet-400", dotColor: "bg-violet-400", desc: "French AI company known for high-quality, efficient models that punch above their weight.", models: [
    { name: "Mistral Large", tier: "Flagship", desc: "Complex reasoning for enterprise-level tasks" },
    { name: "Mistral Medium", tier: "Fast", desc: "Well-balanced for most business tasks" },
    { name: "Mistral Small", tier: "Economy", desc: "Ultra-fast and cheap for simple tasks" },
  ]},
  { name: "Perplexity", color: "text-cyan-400", dotColor: "bg-cyan-400", desc: "AI search engine that gives answers grounded in real, up-to-date web information with source links.", models: [
    { name: "Sonar", tier: "Search", desc: "Searches the web in real-time and gives you answers with sources" },
    { name: "Sonar Pro", tier: "Research", desc: "Deep web research with detailed citations for thorough analysis" },
  ]},
  { name: "Cohere", color: "text-amber-400", dotColor: "bg-amber-400", desc: "Enterprise-focused AI. Great for working with documents, databases, and business data.", models: [
    { name: "Command R+", tier: "Flagship", desc: "Best for enterprise document analysis and retrieval tasks" },
    { name: "Command R", tier: "Economy", desc: "Cost-efficient for summaries and basic document tasks" },
  ]},
  { name: "Groq (Llama 4)", color: "text-amber-300", dotColor: "bg-amber-300", desc: "Runs open-source Llama 4 models on custom hardware for blazing-fast speed at rock-bottom prices.", models: [
    { name: "Llama 4 Scout", tier: "Economy", desc: "Ultra-fast with 128K context -- the cheapest way to use Llama 4" },
    { name: "Llama 4 Maverick", tier: "Fast", desc: "128-expert architecture for balanced performance" },
    { name: "Llama 3.3 70B", tier: "Fast", desc: "Versatile open-source model, great for general tasks" },
  ]},
  { name: "Together AI", color: "text-lime-400", dotColor: "bg-lime-400", desc: "Cloud platform for running open-source AI models. Offers optimized versions of popular models.", models: [
    { name: "Llama 4 Maverick FP8", tier: "Fast", desc: "FP8 optimized for faster inference with same quality" },
    { name: "Llama 3.3 70B Turbo", tier: "Fast", desc: "Turbo-optimized for maximum speed" },
    { name: "DeepSeek R1", tier: "Reasoning", desc: "Open-source deep reasoning model for complex problems" },
  ]},
  { name: "Fireworks AI", color: "text-red-400", dotColor: "bg-red-400", desc: "High-performance AI infrastructure. Great for running many requests at once with low latency.", models: [
    { name: "Llama 4 Scout", tier: "Economy", desc: "Serverless deployment of Llama 4 for easy scaling" },
    { name: "Llama 4 Maverick", tier: "Fast", desc: "High-throughput Llama 4 for demanding workloads" },
    { name: "DeepSeek V3", tier: "Fast", desc: "Cost-efficient hosting of DeepSeek's latest model" },
  ]},
  { name: "AI21 (Jamba)", color: "text-indigo-300", dotColor: "bg-indigo-300", desc: "Israeli AI company. Jamba combines transformer + Mamba architectures for exceptional long-document understanding.", models: [
    { name: "Jamba Large 1.7", tier: "Flagship", desc: "256K context window -- reads entire books with high accuracy" },
    { name: "Jamba Mini 1.7", tier: "Economy", desc: "Lightweight model for everyday business tasks" },
  ]},
  { name: "Cerebras", color: "text-pink-400", dotColor: "bg-pink-400", desc: "World's fastest AI inference using custom wafer-scale chips. Sub-second responses even for 70B models.", models: [
    { name: "Llama 3.3 70B", tier: "Fast", desc: "70B model running at speeds previously impossible — general tasks" },
    { name: "Llama 3.1 70B", tier: "Fast", desc: "Reliable open-source model at ultra-low latency" },
    { name: "Qwen 3-32B", tier: "Economy", desc: "Multilingual reasoning at blazing speed" },
  ]},
  { name: "SambaNova", color: "text-purple-400", dotColor: "bg-purple-400", desc: "Enterprise AI infrastructure running the latest DeepSeek and Llama models on dedicated hardware.", models: [
    { name: "Llama 4 Maverick", tier: "Fast", desc: "128-expert MoE architecture for enterprise performance" },
    { name: "DeepSeek R1-0528", tier: "Reasoning", desc: "Latest DeepSeek reasoning model on fast dedicated hardware" },
    { name: "Qwen 2.5 72B", tier: "Fast", desc: "High-quality multilingual model" },
  ]},
  { name: "Novita AI", color: "text-violet-400", dotColor: "bg-violet-400", desc: "Cost-efficient open-source model hosting. Extensive catalog of Llama, Qwen, DeepSeek, and Hermes models at competitive prices.", models: [
    { name: "Llama 4 Maverick", tier: "Fast", desc: "High-throughput Llama 4 for demanding workloads at low cost" },
    { name: "Qwen 3 235B", tier: "Flagship", desc: "Largest Qwen model — multilingual reasoning powerhouse" },
    { name: "DeepSeek R1", tier: "Reasoning", desc: "Open-source reasoning champion at Novita pricing" },
  ]},
  { name: "Lepton AI", color: "text-orange-400", dotColor: "bg-orange-400", desc: "Serverless AI inference platform. Run open-source models at scale without managing infrastructure.", models: [
    { name: "Llama 4 Maverick", tier: "Fast", desc: "Serverless Llama 4 with instant cold-start" },
    { name: "DeepSeek R1-0528", tier: "Reasoning", desc: "Latest DeepSeek reasoning on Lepton infrastructure" },
  ]},
  { name: "Lambda Labs", color: "text-cyan-400", dotColor: "bg-cyan-400", desc: "GPU cloud provider now offering hosted model inference. Known for research-grade compute and competitive pricing.", models: [
    { name: "Hermes 3 405B", tier: "Flagship", desc: "405B instruction-tuned model — excellent for complex tasks" },
    { name: "Llama 4 Scout", tier: "Economy", desc: "Efficient Llama 4 variant for budget-conscious workloads" },
  ]},
  { name: "Minimax AI", color: "text-sky-400", dotColor: "bg-sky-400", desc: "Chinese AI company with vision-capable models and long context. Strong multimodal capabilities.", models: [
    { name: "MiniMax Text-01", tier: "Flagship", desc: "Flagship text model with long context and vision support" },
    { name: "MiniMax VL-01", tier: "Fast", desc: "Vision-language model for image understanding tasks" },
  ]},
  { name: "Inception AI", color: "text-fuchsia-500", dotColor: "bg-fuchsia-500", desc: "Specializes in ultra-fast code generation. Mercury is the world's fastest code model using diffusion-based generation.", models: [
    { name: "Mercury Coder Small", tier: "Code", desc: "World's fastest code model — diffusion-based generation" },
    { name: "Mercury Coder Large", tier: "Code", desc: "Larger Mercury for complex multi-file code tasks" },
  ]},
  { name: "Arcee AI", color: "text-rose-400", dotColor: "bg-rose-400", desc: "Enterprise-focused AI with strong reasoning and agentic capabilities. Models fine-tuned for business workflows.", models: [
    { name: "Arcee Maestro", tier: "Flagship", desc: "Top-tier reasoning — built for enterprise decision-making" },
    { name: "Arcee Blaze", tier: "Fast", desc: "Fast and capable for everyday enterprise tasks" },
    { name: "Arcee Spark", tier: "Economy", desc: "Lightweight model optimized for quick responses" },
  ]},
  { name: "Amazon Bedrock", color: "text-orange-500", dotColor: "bg-orange-500", desc: "Amazon's managed AI inference platform. Nova models are Amazon's own multimodal foundation models.", models: [
    { name: "Nova Pro", tier: "Flagship", desc: "Amazon's flagship multimodal model — vision, text, and reasoning" },
    { name: "Nova Lite", tier: "Fast", desc: "Balanced performance for everyday multimodal tasks" },
    { name: "Nova Micro", tier: "Economy", desc: "Ultra-fast text-only model for high-volume workloads" },
  ]},
  { name: "Nvidia NIM", color: "text-green-400", dotColor: "bg-green-400", desc: "Nvidia's own AI inference platform. Run massive models on Nvidia's world-class GPU infrastructure.", models: [
    { name: "Nemotron Ultra 253B", tier: "Premium", desc: "253 billion parameter model — Nvidia's most powerful for complex reasoning" },
    { name: "Nemotron Super 49B", tier: "Standard", desc: "Fast 49B model optimized for enterprise tasks" },
    { name: "Llama 3.3 70B", tier: "Fast", desc: "Meta's Llama 3.3 on Nvidia's infrastructure" },
  ]},
  { name: "Moonshot AI (Kimi)", color: "text-blue-300", dotColor: "bg-blue-300", desc: "Chinese AI startup specializing in ultra-long context. Kimi can read and understand documents up to 128,000 words.", models: [
    { name: "Kimi Auto", tier: "Fast", desc: "Auto-selects the best context length for your task" },
    { name: "Kimi 128K", tier: "Standard", desc: "128,000 token context — for very long documents and research" },
    { name: "Kimi 32K", tier: "Economy", desc: "Balanced context length for most tasks" },
  ]},
  { name: "Qwen / Alibaba", color: "text-orange-300", dotColor: "bg-orange-300", desc: "Alibaba's world-class multilingual AI. Best for Chinese-English tasks, data analysis, and the QwQ reasoning model.", models: [
    { name: "Qwen Max", tier: "Flagship", desc: "Most powerful Qwen model — data, reasoning, multilingual" },
    { name: "Qwen Plus", tier: "Standard", desc: "Great for translation and code between languages" },
    { name: "QwQ-32B", tier: "Reasoning", desc: "Dedicated reasoning model for step-by-step math and logic" },
    { name: "Qwen Turbo", tier: "Economy", desc: "Ultra-fast for quick multilingual tasks" },
  ]},
  { name: "01.AI / Yi", color: "text-rose-300", dotColor: "bg-rose-300", desc: "Chinese AI lab behind the Yi model family. Yi Lightning is one of the cheapest capable models available.", models: [
    { name: "Yi Lightning", tier: "Economy", desc: "Ultra-cheap fast model — 16K context, great for simple tasks" },
    { name: "Yi Large FC", tier: "Standard", desc: "Function calling specialist — great for tool use and APIs" },
    { name: "Yi Medium 200K", tier: "Long-Context", desc: "200,000 token context — reads entire codebases and books" },
  ]},
  { name: "Zhipu AI (GLM)", color: "text-emerald-300", dotColor: "bg-emerald-300", desc: "Chinese AI company behind the GLM model family. Strong multilingual and reasoning capabilities.", models: [
    { name: "GLM-4-Plus", tier: "Flagship", desc: "Most powerful GLM — complex tasks, enterprise use" },
    { name: "GLM-4-Air", tier: "Economy", desc: "Fast efficient GLM — everyday tasks at low cost" },
    { name: "GLM-Z1-Air", tier: "Reasoning", desc: "GLM reasoning specialist for math and logic" },
  ]},
  { name: "ByteDance Doubao", color: "text-cyan-300", dotColor: "bg-cyan-300", desc: "ByteDance's (TikTok parent company) enterprise AI models. Strong at Chinese-language tasks.", models: [
    { name: "Doubao Pro 128K", tier: "Flagship", desc: "ByteDance's flagship — 128K context, excellent Chinese tasks" },
    { name: "Doubao Pro 32K", tier: "Standard", desc: "Balanced ByteDance model for most tasks" },
    { name: "Doubao Lite 128K", tier: "Economy", desc: "Fast cheap 128K — large documents at low cost" },
  ]},
  { name: "Hyperbolic", color: "text-indigo-300", dotColor: "bg-indigo-300", desc: "High-performance open-source GPU hosting. Run Llama 405B and DeepSeek-R1 at competitive prices.", models: [
    { name: "Llama 3.1 405B", tier: "Flagship", desc: "Largest open-source Llama — 405B parameters" },
    { name: "DeepSeek-R1", tier: "Reasoning", desc: "Fast DeepSeek reasoning on Hyperbolic infrastructure" },
    { name: "Llama 3.3 70B", tier: "Standard", desc: "Fast reliable 70B model" },
  ]},
  { name: "Upstage Solar", color: "text-yellow-300", dotColor: "bg-yellow-300", desc: "Korean AI company. Solar Pro achieves top benchmarks for its size.", models: [
    { name: "Solar Pro", tier: "Enterprise", desc: "Top-tier commercial model — best-in-class benchmarks" },
    { name: "Solar Mini", tier: "Economy", desc: "Efficient compact Upstage model" },
  ]},
  { name: "Writer Palmyra", color: "text-violet-300", dotColor: "bg-violet-300", desc: "Enterprise-focused AI models with domain-specific variants for healthcare and finance.", models: [
    { name: "Palmyra X 004", tier: "Enterprise", desc: "General enterprise LLM — 128K context" },
    { name: "Palmyra Med", tier: "Medical", desc: "Medical domain specialist — clinical notes, research" },
    { name: "Palmyra Fin", tier: "Finance", desc: "Financial domain specialist — reports, analysis" },
  ]},
  { name: "Meta Llama API", color: "text-blue-200", dotColor: "bg-blue-200", desc: "Meta's official Llama API — direct access to Llama 4 models from the creators themselves.", models: [
    { name: "Llama 4 Scout", tier: "Standard", desc: "17B params, 16 experts — fast and capable" },
    { name: "Llama 4 Maverick", tier: "Flagship", desc: "17B params, 128 experts — best open Llama" },
    { name: "Llama 3.3 70B", tier: "Economy", desc: "Proven 70B model from Meta's official API" },
  ]},
  { name: "HuggingFace Inference", color: "text-amber-200", dotColor: "bg-amber-200", desc: "Access hundreds of open-source models via HuggingFace's serverless Inference API.", models: [
    { name: "Microsoft Phi-4", tier: "Compact Reasoning", desc: "16K context, excellent at math and reasoning despite small size" },
    { name: "Gemma 2 9B", tier: "Economy", desc: "Google's open model, great at instruction following" },
    { name: "Mistral 7B", tier: "Economy", desc: "Classic efficient multilingual open model" },
  ]},
  { name: "AI Media & Voice", color: "text-pink-400", dotColor: "bg-pink-400", desc: "These aren't text models -- they create images, videos, and voice audio from text descriptions.", models: [
    { name: "Nano Banana 2", tier: "Image Gen", desc: "Creates images from text descriptions using Gemini 3.1 Flash" },
    { name: "GPT Image 1", tier: "Image Gen", desc: "OpenAI's image generator -- creates high-quality images from text" },
    { name: "DALL-E 3", tier: "Image Gen", desc: "Creates creative, artistic images from text prompts" },
    { name: "Sora 2", tier: "Video Gen", desc: "Creates short AI videos from text descriptions (4-12 seconds)" },
    { name: "ElevenLabs", tier: "Voice", desc: "Converts text to natural-sounding speech in multiple languages including Bangla and English" },
    { name: "Whisper", tier: "STT", desc: "Converts spoken audio to text in 50+ languages (speech-to-text)" },
  ]},
];


/* ── shared components ── */
const Section = ({ title, subtitle, icon: Icon, color, children, id, noPageBreak }) => (
  <div className={`mb-10 about-section ${noPageBreak ? "about-hero" : ""}`} id={id}>
    <div className="flex items-center gap-3 mb-1">
      <div className={`w-9 h-9 rounded-xl ${color || "bg-indigo-500/15"} flex items-center justify-center print-icon`}>
        {Icon && <Icon className="w-5 h-5 text-white" />}
      </div>
      <div>
        <h2 className="text-lg font-bold text-white font-['Outfit'] print-heading">{title}</h2>
        {subtitle && <p className="text-[10px] text-zinc-500">{subtitle}</p>}
      </div>
    </div>
    <div className="mt-3">{children}</div>
  </div>
);

/* ── FAQ controls: Expand all / Collapse all / Download ──────────────────
   Reads the Q/A pairs out of the rendered DOM under `#<rootId>` so the
   buttons stay in sync with whatever entries are currently shown.  */
function FAQControls({ rootId }) {
  const setAll = (open) => {
    const root = document.getElementById(rootId);
    if (!root) return;
    root.querySelectorAll("details").forEach((d) => { d.open = open; });
  };
  const download = () => {
    const root = document.getElementById(rootId);
    if (!root) return;
    const date = new Date().toISOString().slice(0, 10);
    const lines = [
      "# MAARS Command — FAQ",
      `_Exported ${date} · source: ${typeof window !== "undefined" ? window.location.origin : ""}/about#faq_`,
      "",
    ];
    root.querySelectorAll("details").forEach((d) => {
      const q = d.querySelector("summary")?.innerText?.trim() || "";
      // Strip the question out of the summary so we don't double-count it when
      // grabbing the answer text from the rest of the element.
      const full = (d.innerText || "").trim();
      const a = full.startsWith(q) ? full.slice(q.length).trim() : full;
      if (q) {
        lines.push(`## ${q}`);
        lines.push("");
        lines.push(a);
        lines.push("");
      }
    });
    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `maars-faq-${date}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const printPdf = () => {
    // Trigger the same full-page flow the "Download Docs" button uses: expand
    // every network, every system, and every <details> before printing — so
    // the user gets ONE canonical PDF instead of a partial FAQ-only view.
    const btn = document.querySelector("[data-testid='download-pdf-btn']");
    if (btn) { btn.click(); return; }
    // Fallback: just expand local details and print.
    setAll(true);
    setTimeout(() => {
      document.querySelectorAll("details").forEach((d) => { d.open = true; });
      requestAnimationFrame(() => window.print());
    }, 200);
  };
  const btn = {
    display: "inline-flex", alignItems: "center", gap: 4,
    fontSize: 11, padding: "4px 8px", borderRadius: 6,
    background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)",
    color: "#e5e7eb", cursor: "pointer",
  };
  return (
    <div className="flex items-center gap-2 no-print">
      <button onClick={() => setAll(true)}  style={btn} title="Expand every question">
        <ChevronDown className="w-3 h-3" /> Expand all
      </button>
      <button onClick={() => setAll(false)} style={btn} title="Collapse every question">
        <ChevronRight className="w-3 h-3" /> Collapse all
      </button>
      <button onClick={download} style={{ ...btn, borderColor: "rgba(56,189,248,0.35)", background: "rgba(56,189,248,0.12)" }}
              title="Download the FAQ as Markdown (.md)">
        <Download className="w-3 h-3" /> .md
      </button>
      <button onClick={printPdf} style={{ ...btn, borderColor: "rgba(167,139,250,0.35)", background: "rgba(167,139,250,0.12)" }}
              title="Expand all and open your browser's Print → Save as PDF dialog">
        <Printer className="w-3 h-3" /> PDF
      </button>
    </div>
  );
}

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

  /* Print PDF — expand EVERY collapsible region first, then trigger print.
     - Networks + Systems state is controlled by React, so we expand those via
       setState.
     - FAQ and any future <details> collapsibles are native DOM elements, so we
       force `open = true` on each one after React commits.
     - Print CSS in frontend/src/index.css forces `details > *` visible as a
       belt-and-suspenders so nothing can stay hidden in the PDF. */
  const handlePrint = () => {
    setPrinting(true);
    setExpandedNetworks(new Set(sortedNetworks.map(([k]) => k)));
    setExpandedSystems(new Set(SYSTEMS.map((_, i) => i)));
    // Give React a tick to commit, then force every <details> open and print.
    setTimeout(() => {
      document.querySelectorAll("details").forEach((d) => { d.open = true; });
      // Second rAF so the `open` attribute toggles render before print preview.
      requestAnimationFrame(() => {
        window.print();
        setPrinting(false);
      });
    }, 350);
  };

  const getNetworkMeta = (netId) => {
    const meta = NETWORK_META[netId];
    if (meta) return meta;
    return { label: netId === "core_team" ? "Core Team" : netId.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()), icon: Bot, color: "zinc" };
  };

  const getNetColors = (netId) => {
    const c = getNetworkMeta(netId).color;
    return { bg: `bg-${c}-500/10`, border: `border-${c}-500/20`, text: `text-${c}-400`, badge: `bg-${c}-500/20 text-${c}-400` };
  };

  return (
    <div className="space-y-8 max-w-4xl print-container" data-testid="about-page" ref={printRef}>
      {/* Hero */}
      <div className="about-hero">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <img src="/mgc-logo.png" alt="MAARS Global Corporation" className="w-14 h-14 rounded-2xl object-contain print-logo" />
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white font-['Outfit']">MAARS Command</h1>
              <p className="text-sm text-zinc-400">Autonomous AI Enterprise Operating System</p>
              <p className="text-[10px] text-zinc-600">by MAARS Global Corporation | Est. 2026</p>
            </div>
          </div>
          <button onClick={handlePrint} className="border-white/10 text-zinc-300 hover:bg-white/5 no-print" data-testid="download-pdf-btn" style={{ display: "flex", alignItems: "center", border: "1px solid rgba(255,255,255,0.10)", borderRadius: 8, padding: "6px 14px", background: "transparent", color: "rgb(212 212 216)", cursor: "pointer" }}>
            <Printer className="w-4 h-4 mr-2" />{printing ? "Preparing..." : "Download Docs"}
          </button>
        </div>

        <div className="bg-zinc-900/40 rounded-xl border border-white/5 p-4 mb-4">
          <h3 className="text-sm font-bold text-white mb-2">What is MAARS Command?</h3>
          <p className="text-sm text-zinc-300 leading-relaxed">
            Imagine you have a company with <span className="text-indigo-400 font-medium">{agents.length || "458"}+ AI employees</span>, each one an expert in something different -- marketing, coding, legal, finance, design, sales, research, and more.
            MAARS Command is the operating system that manages all of them. You tell it what you want to accomplish (in plain English), and it figures out which AI agents to assign, breaks your goal into steps, runs everything automatically, checks the quality of every result, and delivers the finished work to you.
          </p>
          <p className="text-sm text-zinc-300 leading-relaxed mt-2">
            These agents are organized into <span className="text-emerald-400 font-medium">{uniqueNetworks || 28} specialized network categories</span> (like departments in a company).
            They're powered by <span className="text-amber-400 font-medium">33 AI providers with 175,609+ models</span> (GPT-5, Claude Opus 4.6, Gemini 2.5, Grok-4, DeepSeek R1, Mistral, Perplexity, Groq, Cerebras, SambaNova, and more).
            Each agent is grounded in the <span className="text-lime-400 font-medium">58,422-skill library</span> — a curated knowledge pack of SKILL.md documents that is auto-matched and ingested into the agent's brain at creation time, so replies stand on real expertise instead of guesses.
            The system automatically picks the right AI model for each task, controls costs, ensures quality, and even lets agents collaborate with each other -- all without you lifting a finger.
          </p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {["Multi-Agent Orchestration","Quality Control","Smart Model Router","Developer API Gateway","600+ Models · 33 Providers","58k+ Skill Library","Content Generation","App Builder","Memory System","Voice Commands","Code Explorer","Knowledge Graph","Workflow Builder","Campaign Builder","Integration Hub","Team Builder","Trust Analytics","Real-World Actions","Command Palette"].map((b, i) => {
            const colors = ["indigo","emerald","amber","pink","cyan","violet","rose","sky","blue","teal","orange","red","green","purple","lime","yellow"];
            return <span key={b} className={`bg-${colors[i % colors.length]}-500/20 text-${colors[i % colors.length]}-400`} style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 20, display: "inline-block" }}>{b}</span>;
          })}
        </div>
      </div>

      {/* Vision & Mission */}
      <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 via-violet-500/5 to-transparent p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2"><Target className="w-4 h-4 text-indigo-300" /><p className="text-[10px] uppercase tracking-[0.3em] text-indigo-300 font-bold">Vision</p></div>
            <p className="text-sm text-zinc-200 leading-relaxed">
              A world where every organization — from a solo founder to a global enterprise — operates with a reliable, auditable, autonomous AI workforce.
              Not one chatbot. Not one copilot. An entire workforce, governed like a real company, grounded in verified knowledge, accountable to humans.
            </p>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2"><Rocket className="w-4 h-4 text-fuchsia-300" /><p className="text-[10px] uppercase tracking-[0.3em] text-fuchsia-300 font-bold">Mission</p></div>
            <p className="text-sm text-zinc-200 leading-relaxed">
              Build the operating system that makes autonomous AI workforces safe, provable, and economical. Replace 18–24 months of custom integration work with one platform and one API key.
              Ship agents that earn trust — through verification, audit, and recovery — instead of agents that just sound confident.
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 print-stats-row">
        {[
          { label: "AI Agents", value: `${agents.length || "458"}+`, color: "text-indigo-400", sub: "Specialized workers" },
          { label: "Networks", value: uniqueNetworks || 28, color: "text-emerald-400", sub: "Team categories" },
          { label: "Core Systems", value: SYSTEMS.length, color: "text-amber-400", sub: "Built-in tools" },
          { label: "LLM Providers", value: AI_PROVIDERS.length, color: "text-violet-400", sub: "AI companies" },
          { label: "AI Models", value: "600+", color: "text-cyan-400", sub: "Via gateway" },
          { label: "Skill Library", value: "58,422", color: "text-lime-400", sub: "Curated SKILL.md packs" },
          { label: "API Endpoints", value: "484", color: "text-rose-400", sub: "Across 32 route files" },
        ].map(s => (
          <div key={s.label} className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
            <div className="p-3 text-center">
              <p className={`text-2xl font-bold ${s.color} font-['Outfit']`}>{s.value}</p>
              <p className="text-[11px] text-zinc-400">{s.label}</p>
              <p className="text-[9px] text-zinc-600">{s.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Dynamic Agent Workforce */}
      <Section title={`The Complete ${agents.length || 458}-Agent AI Workforce`} subtitle="Every single agent, organized by specialty" icon={Users} color="bg-indigo-500/15" id="agents">
        <p className="text-xs text-zinc-400 mb-4">
          Below is every AI agent in MAARS Command, organized by their network category (like departments in a company). Each agent has a unique name, a specific job title (role), a description of what they do, and a list of all their skills (capabilities).
          {printing ? "" : " Click any network to see all the agents inside it."}
        </p>
        {loading ? (
          <div className="flex items-center justify-center h-20"><div className="w-5 h-5 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin" /></div>
        ) : (
          <div className="space-y-2">
            {sortedNetworks.map(([netId, netAgents]) => {
              const meta = getNetworkMeta(netId);
              const colors = getNetColors(netId);
              const Icon = meta.icon;
              const isExpanded = expandedNetworks.has(netId) || printing;
              return (
                <div key={netId} className="print-page-break">
                  <button onClick={() => toggleNetwork(netId)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${isExpanded ? `${colors.bg} ${colors.border}` : "bg-zinc-900/30 border-white/5 hover:border-white/10"}`}
                    data-testid={`network-${netId}`}>
                    <Icon className={`w-4 h-4 ${colors.text}`} />
                    <span className="text-sm font-medium text-white flex-1 text-left">{meta.label}</span>
                    <span className={`${colors.badge}`} style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, display: "inline-block" }}>{netAgents.length} agents</span>
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500 no-print" /> : <ChevronRight className="w-4 h-4 text-zinc-500 no-print" />}
                  </button>
                  {isExpanded && (
                    <div className="mt-1 ml-4 space-y-1 py-2">
                      {netAgents.map(agent => (
                        <div key={agent.agent_id} className={`flex items-start gap-3 p-2.5 rounded-lg ${colors.bg} border ${colors.border} print-agent-card`}>
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
                              <span className={`${colors.badge}`} style={{ fontSize: 8, fontWeight: 700, padding: "2px 6px", borderRadius: 20, display: "inline-block" }}>{agent.role}</span>
                              {agent.autonomy_tier && <span className="bg-white/5 text-zinc-500" style={{ fontSize: 8, fontWeight: 700, padding: "2px 6px", borderRadius: 20, display: "inline-block" }}>Autonomy {agent.autonomy_tier}/10</span>}
                            </div>
                            {agent.description && <p className="text-[10px] text-zinc-400 leading-relaxed mt-1 print-no-clamp">{agent.description}</p>}
                            {agent.capabilities?.length > 0 && (
                              <div className="mt-1.5">
                                <p className="text-[8px] text-zinc-600 mb-0.5 uppercase tracking-wider">Skills:</p>
                                <div className="flex gap-1 flex-wrap">
                                  {agent.capabilities.map(c => (
                                    <span key={c} className="text-[8px] px-1.5 py-0.5 rounded bg-white/5 text-zinc-500">{c}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {agent.tools?.length > 0 && (
                              <div className="mt-1">
                                <p className="text-[8px] text-zinc-600 mb-0.5 uppercase tracking-wider">Tools:</p>
                                <div className="flex gap-1 flex-wrap">
                                  {agent.tools.map(t => (
                                    <span key={t} className="text-[8px] px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400">{t}</span>
                                  ))}
                                </div>
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
      <Section title={`${SYSTEMS.length} Core Systems & Capabilities`} subtitle="Everything the platform can do, explained simply" icon={Layers} color="bg-emerald-500/15" id="systems">
        <p className="text-xs text-zinc-400 mb-4">
          These are the {SYSTEMS.length} major tools and systems built into MAARS Command. Each one does something different, and they all work together.
          Think of them like apps on your phone -- each has a specific purpose, but they can share information with each other.
          {printing ? "" : " Click any system to read the full explanation."}
        </p>
        <div className="space-y-2">
          {SYSTEMS.reduce((groups, sys, i) => {
            if (i % 3 === 0) groups.push([]);
            groups[groups.length - 1].push({ sys, i });
            return groups;
          }, []).map((group, gi) => (
            <div key={gi} className={gi > 0 ? "print-systems-group" : ""}>
              {group.map(({ sys, i }) => {
                const isExpanded = expandedSystems.has(i) || printing;
                return (
                  <div key={i} className="mb-2">
                    <button onClick={() => toggleSystem(i)}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all print-no-break ${isExpanded ? "bg-zinc-800/60 border-white/10" : "bg-zinc-900/30 border-white/5 hover:border-white/10"}`}
                      data-testid={`system-${i}`}>
                      <sys.icon className={`w-4 h-4 ${sys.color} shrink-0`} />
                      <div className="flex-1 text-left">
                        <span className="text-sm font-medium text-white">{sys.title}</span>
                        {sys.subtitle && <span className="text-[10px] text-zinc-500 ml-2">-- {sys.subtitle}</span>}
                      </div>
                      {isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500 no-print" /> : <ChevronRight className="w-4 h-4 text-zinc-500 no-print" />}
                    </button>
                    {isExpanded && (
                      <div className="mt-1 ml-4 p-4 rounded-lg bg-zinc-800/30 border border-white/5">
                        <p className="text-sm text-zinc-300 leading-relaxed mb-3">{sys.desc}</p>
                        <p className="text-[10px] text-zinc-500 font-medium mb-2 uppercase tracking-wide">How it works step by step:</p>
                        <div className="space-y-1.5">
                          {sys.details.map((d, j) => (
                            <div key={j} className="flex items-start gap-2">
                              <div className="w-1 h-1 rounded-full bg-zinc-500 mt-2 shrink-0" />
                              <p className="text-xs text-zinc-400 leading-relaxed">{d}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </Section>

      {/* Architecture */}
      <Section title="How MAARS Command Is Built" subtitle="The technology behind the scenes" icon={Database} color="bg-cyan-500/15" id="architecture">
        <p className="text-xs text-zinc-400 mb-3">MAARS Command is built with three main layers that work together, like a three-layer cake. Each layer has a specific job and they communicate constantly to deliver a seamless experience.</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2"><Server className="w-4 h-4 text-cyan-400" /><p className="text-sm font-medium text-white">Backend (The Engine)</p></div>
              <p className="text-[10px] text-zinc-500 mb-2">This is the part that runs on the server and does all the heavy work behind the scenes. It processes every request, manages data, and coordinates all 458+ agents.</p>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">FastAPI (Python) -- the programming framework that handles all requests at high speed with async processing</p>
                <p className="text-xs text-zinc-400">MongoDB -- the database that stores all agents, teams, memories, and user data across 27+ collections</p>
                <p className="text-xs text-zinc-400">212+ API endpoints -- connection points that the frontend uses to get and send data for every feature</p>
                <p className="text-xs text-zinc-400">WebSocket -- a real-time connection for live updates like the Agent Activity Monitor and collaboration feeds</p>
                <p className="text-xs text-zinc-400">MAARS Universal API Gateway: 175,000+ models across 33 direct providers, OpenAI-compatible /v1/chat/completions, live model validation, auto-fallback routing, webhooks, and model comparison endpoint</p>
                <p className="text-xs text-zinc-400">Stripe Integration -- handles credit card payments, subscription billing, and cost tracking</p>
                <p className="text-xs text-zinc-400">Background Task Queue -- manages long-running operations like batch agent deployments and report generation</p>
                <p className="text-xs text-zinc-400">Circuit Breaker System -- automatically detects and isolates failing services to prevent cascade failures</p>
                <p className="text-xs text-zinc-400">Skill ingestion pipeline (services/skills_service.py) -- reads .claude/skills/{'{'}name{'}'}/SKILL.md files, chunks the Markdown, and upserts into db.knowledge_chunks per agent using keyword-based matching</p>
              </div>
            </div>
          </div>
          <div className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2"><Eye className="w-4 h-4 text-pink-400" /><p className="text-sm font-medium text-white">Frontend (What You See)</p></div>
              <p className="text-[10px] text-zinc-500 mb-2">This is the part that runs in your web browser -- all the pages, buttons, charts, and visuals that you interact with every day.</p>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">React 18 -- the framework that builds the interactive user interface with real-time state management</p>
                <p className="text-xs text-zinc-400">Tailwind CSS -- makes everything look beautiful with a modern, consistent dark-themed design system</p>
                <p className="text-xs text-zinc-400">Shadcn/UI -- pre-built, accessible components like buttons, cards, menus, dialogs, and data tables</p>
                <p className="text-xs text-zinc-400">50+ pages & dashboards -- every feature has its own dedicated page with custom layouts and interactions</p>
                <p className="text-xs text-zinc-400">Progressive Web App (PWA) -- can be installed on your phone or desktop like a native app with offline support</p>
                <p className="text-xs text-zinc-400">Command Palette + Voice -- search and navigate instantly by typing keyboard shortcuts or speaking commands</p>
                <p className="text-xs text-zinc-400">Real-Time Charts & Visualizations -- live data rendered using Recharts for trust analytics and cost tracking</p>
                <p className="text-xs text-zinc-400">Print-Ready Documentation -- the entire system documentation can be exported as a formatted document</p>
              </div>
            </div>
          </div>
          <div className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2"><Sparkles className="w-4 h-4 text-amber-400" /><p className="text-sm font-medium text-white">AI Layer (The Brains)</p></div>
              <p className="text-[10px] text-zinc-500 mb-2">This connects MAARS Command to all the AI providers that power the agents. It routes tasks to the best model automatically.</p>
              <div className="space-y-1">
                <p className="text-xs text-zinc-400">OpenAI -- GPT-5, GPT-4.1/mini/nano (1M ctx), O4/O3 reasoning, Whisper STT, GPT Image 1, Sora 2</p>
                <p className="text-xs text-zinc-400">Anthropic -- Claude Opus 4.6 & 4.5, Sonnet 4.6 & 3.7, Haiku 4.5 — 200K context, extended thinking</p>
                <p className="text-xs text-zinc-400">Google -- Gemini 2.5 Pro (2M ctx), Gemini 2.5 Flash, Gemma 3 open models (1B–27B)</p>
                <p className="text-xs text-zinc-400">xAI -- Grok-4 & Grok-4 Fast Reasoning (256K ctx), Grok-3 (1M ctx), Grok-2 Vision</p>
                <p className="text-xs text-zinc-400">Groq, Cerebras -- sub-second inference on Llama 4, Qwen QwQ-32B</p>
                <p className="text-xs text-zinc-400">Together AI (39), Fireworks AI (20), SambaNova (14), NVIDIA NIM (12), Novita AI (12), Lepton AI (8), Lambda Labs (6), Minimax AI (4), Inception AI (2), Arcee AI (3), Amazon Bedrock (4) -- direct provider hosting</p>
                <p className="text-xs text-zinc-400">DeepSeek, Mistral, Perplexity, Cohere, AI21, Moonshot, Qwen, Yi, Zhipu, Doubao, Hyperbolic, Upstage, Writer, HuggingFace, LLaMA API</p>
                <p className="text-xs text-zinc-400">Live model validation -- checks provider /models API before every call, auto-fallbacks on stale IDs</p>
              </div>
            </div>
          </div>
        </div>
      </Section>

      {/* AI Models & Providers */}
      <Section title="All 33 AI Providers & 609+ Models" subtitle="Every AI brain available via the MAARS Universal API Gateway" icon={Sparkles} color="bg-amber-500/15" id="providers">
        <p className="text-xs text-zinc-400 mb-4">
          MAARS connects to 33 different AI companies, giving you access to 175,609+ models via a single <code className="text-indigo-300 bg-white/5 px-1 rounded">maars-sk-*</code> API key.
          Each model has different strengths — some are super fast but less powerful, some are incredibly smart but cost more.
          The Smart Router picks the best one automatically, or call any model directly via the Developer Portal at <code className="text-indigo-300 bg-white/5 px-1 rounded">/developer</code>.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[...AI_PROVIDERS].sort((a, b) => a.name.localeCompare(b.name)).map(provider => (
            <div key={provider.name} className="bg-zinc-900/50 border-white/5 print-card" data-testid={`provider-${provider.name}`} style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className={`w-4 h-4 ${provider.color}`} />
                  <p className="text-sm font-bold text-white">{provider.name}</p>
                </div>
                <p className="text-[10px] text-zinc-500 mb-3">{provider.desc}</p>
                <div className="space-y-2">
                  {provider.models.map(m => (
                    <div key={m.name} className="flex items-start gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${provider.dotColor}`} />
                      <div>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-xs font-medium text-zinc-200">{m.name}</span>
                          <span className={`${TIER_COLORS[m.tier] || "bg-zinc-700 text-zinc-400"}`} style={{ fontSize: 8, fontWeight: 700, padding: "2px 6px", borderRadius: 20, display: "inline-block" }}>{m.tier}</span>
                        </div>
                        <p className="text-[10px] text-zinc-500">{m.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Security & Governance */}
      <Section title="Security & Governance" subtitle="How MAARS Command keeps everything safe and controlled" icon={Shield} color="bg-red-500/15" id="security">
        <p className="text-xs text-zinc-400 mb-3">
          Running 458+ AI agents requires strong safety controls. Without proper governance, agents could overspend, leak data, or take unintended actions.
          Here are the six security systems that keep everything safe, fair, and auditable at all times.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            { title: "Role-Based Access Control (RBAC)", icon: Lock, desc: "Not everyone should have access to everything. RBAC lets you set different permission levels for different users. Admins can do anything -- manage all agents, change settings, and view billing. Managers can manage agents and view reports but cannot change system settings. Regular users can chat with agents and use tools but cannot modify configurations. Every page and every API endpoint checks permissions before allowing access. This prevents unauthorized users from accidentally (or intentionally) changing critical settings or accessing sensitive data." },
            { title: "Circuit Breakers", icon: Shield, desc: "If an AI model or service starts failing repeatedly, the circuit breaker automatically stops sending requests to it. This prevents one broken service from crashing the entire system -- like a fuse box in your house that trips to protect your appliances. The system monitors error rates in real-time. When failures exceed the threshold, the circuit 'opens' and redirects traffic to backup models. Once the original service recovers and passes health checks, the circuit breaker automatically re-enables it. All transitions are logged for review." },
            { title: "Cost Governance", icon: DollarSign, desc: "AI models cost money every time they're used -- some models cost just $0.10 per million tokens, while others cost $75 per million. Cost Governance tracks every single API call and its exact cost in real-time with per-agent and per-user breakdowns. You can set daily, weekly, or monthly spending limits for individual users and for the entire organization. When spending approaches the limit (80%), the system sends warning alerts. When limits are reached (100%), it automatically stops sending requests to paid models. This prevents surprise bills and ensures your AI budget is always under control." },
            { title: "Audit Logging", icon: FileCheck, desc: "Every action in MAARS Command is recorded in an immutable audit log -- who did what, when they did it, and what the result was. This includes agent task completions, user logins, configuration changes, permission modifications, and API calls to external services. These logs cannot be edited or deleted after creation, making them tamper-proof and suitable for compliance audits, legal requirements, and internal investigations. Logs can be searched, filtered, and exported for reporting. Retention policies ensure logs are kept for the required duration." },
            { title: "Trust Scoring", icon: Gauge, desc: "Every agent gets a trust score from 0 to 100 based on its complete performance history. The score factors in task completion rate, response quality, speed, error frequency, and user feedback. Agents that consistently deliver accurate, fast results earn higher scores over time. Agents that fail often, produce low-quality work, or generate errors get lower scores. Low-trust agents can be automatically restricted to simulation-only mode or flagged for human review. High-trust agents get priority assignment for critical tasks. The scoring algorithm is transparent -- you can see exactly why an agent has its current score." },
            { title: "Simulation Mode", icon: Eye, desc: "A system-wide safety switch that controls whether agents can take real-world actions. When Simulation Mode is ON (the default), all external actions -- sending emails, creating calendar events, making API calls, posting content -- return realistic fake responses instead of actually executing. This lets you safely test and review exactly what agents would do before going live. You can review simulated results, adjust agent configurations, and only flip to Execution Mode when you're confident everything works correctly. Individual agents can also be toggled independently between simulation and execution modes." },
          ].map(item => (
            <div key={item.title} className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <item.icon className="w-4 h-4 text-red-400" />
                  <p className="text-sm font-medium text-white">{item.title}</p>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Why MAARS is Different */}
      <Section title="Why MAARS Command Is Different" subtitle="What separates this from every other AI platform" icon={Sparkles} color="bg-fuchsia-500/15" id="differentiators">
        <p className="text-xs text-zinc-400 mb-4">
          Most AI platforms are either (a) one giant chatbot, (b) a skinny wrapper around OpenAI, or (c) a single-purpose agent (customer support, coding copilot, etc.).
          MAARS Command is built as an <span className="text-fuchsia-300 font-medium">enterprise operating system for autonomous AI</span> — the way a cloud platform is built for workloads, or an ERP is built for a business.
          Below are the nine things you get in MAARS that you cannot get by stitching together ChatGPT, a Zapier workflow, and a custom GPT.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            { icon: Users, title: "458+ Agents in 27 Networks — not one chatbot", text: "You don't prompt a generalist and hope it specializes. You dispatch work to the right specialist. A Commander coordinates. A CFO agent models the P&L. A Legal agent reads contracts. A Growth agent runs experiments. Each agent has its own brain profile, tool set, trust score, and memory — and they talk to each other through a real collaboration protocol, not fake multi-agent prompting." },
            { icon: Cpu, title: "Universal Gateway — 175,609+ models, one key", text: "A single maars-sk-* API key reaches 33 providers (OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Perplexity, Groq, Cerebras, plus 175,000+ HuggingFace models) through an OpenAI-compatible /v1/chat/completions endpoint. Smart routing, live model validation, auto-fallback, real token billing, webhooks. The other way to get this is to integrate 33 SDKs yourself." },
            { icon: BookOpen, title: "58,422-Skill Knowledge Pack pre-built", text: "Every agent is grounded in curated skill documents the moment it's created. You don't write system prompts from scratch. You don't hunt prompt libraries on Reddit. The keyword matcher picks the right skills per agent; the RAG engine retrieves them per turn; the brain endpoint shows you exactly what each agent \"knows.\"" },
            { icon: Gauge, title: "10-Tier Autonomy — not a binary switch", text: "\"Agent frameworks\" tend to let agents run wild or demand approval for everything. MAARS has 10 granular tiers: pre-approved tools vs. gated tools, trust-scored elevation, dual-signature gates, policy-aware bypass. You can run one agent at Tier 3 (conservative) and another at Tier 9 (autonomous) in the same workflow." },
            { icon: CheckCircle, title: "Verification Civilization instead of \"hope it's right\"", text: "Most AI output is trusted because the user has no other choice. MAARS cross-verifies claims across 2-4 independent models on 6 dimensions (factual, grounded, coherent, complete, bias, fresh) before the answer reaches you. Disagreements escalate. Hallucinations get quarantined. The agent's job isn't to sound confident — it's to survive attempted refutation." },
            { icon: Building, title: "4 Environments · Immutable Audit · Simulation mode", text: "Simulation, Sandbox, Staging, Production — each with its own budget, policies, credentials, and retention. Run autonomous experiments at zero real cost in Simulation. Flip to Production only after the Verification engine signs off. Every action — approvals, tool calls, model responses, policy violations — written to an immutable audit trail. Enterprise-ready out of the box." },
            { icon: Shield, title: "Circuit Breakers, Recovery, Incident Response built-in", text: "Spend spike? Breaker trips, agents pause, you're paged. Agent misbehaves? It's quarantined — tools stripped, tier dropped to 1, flagged for review. Task graph fails halfway? Rollback to last checkpoint. Provider outage? Auto-fallback across 33 alternates. These are not bolt-ons — they are core kernel functionality." },
            { icon: Zap, title: "Task Graph Kernel — real DAG execution", text: "Give MAARS a goal in English; it emits a task graph (DAG) with parallel branches, dependency resolution, retry, checkpoints, and per-branch budgets. Kill it at hour 4 — resume at hour 5 from exactly where it stopped. This is how long-horizon autonomous work actually ships, not by stuffing everything into one mega-prompt and hoping." },
            { icon: Key, title: "Pay-as-you-go with 65%/35% transparency", text: "No subscription lock-in. Top up any amount. Exactly 65% of every dollar goes to AI model costs (shown to you in real time), 35% covers the platform (routing, failover, governance, support). Credits never expire during your active period. Compare that to the \"your model quota resets every month at 11:59 pm\" world." },
          ].map(item => (
            <div key={item.title} className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <item.icon className="w-4 h-4 text-fuchsia-400 shrink-0" />
                  <p className="text-sm font-medium text-white">{item.title}</p>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{item.text}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Value Evaluation */}
      <Section title="Value Evaluation — What MAARS Saves You" subtitle="Rough ROI per feature so you know where the money goes" icon={DollarSign} color="bg-amber-500/15" id="value">
        <p className="text-xs text-zinc-400 mb-4">
          Building the same capability stack by hand takes roughly 18-24 months of engineering plus ongoing integration/ops overhead.
          Below is a concrete per-feature breakdown of what each MAARS subsystem replaces and the rough monthly cost/effort avoided.
          Numbers are conservative mid-market estimates; enterprise stacks are typically 2-5× higher.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead>
              <tr className="text-zinc-500 border-b border-white/10">
                <th className="text-left py-2 px-2 font-medium">Capability</th>
                <th className="text-left py-2 px-2 font-medium">What It Replaces</th>
                <th className="text-left py-2 px-2 font-medium">Typical Monthly Cost (DIY)</th>
                <th className="text-left py-2 px-2 font-medium">Effort Avoided</th>
              </tr>
            </thead>
            <tbody className="text-zinc-400">
              {[
                ["Universal Gateway (33 providers)", "33 separate LLM SDK integrations + routing layer", "$800–$2,500", "6-9 months eng"],
                ["458+ Agent Workforce", "Hiring 10-20 specialists + onboarding", "$80,000–$200,000 (salary)", "Ongoing"],
                ["58,422 Skill Library", "Custom prompt engineering per use case", "$3,000–$15,000 (agency)", "2-4 months"],
                ["Task Graph Kernel (DAG)", "Custom workflow engine (Temporal/Airflow + glue)", "$1,500–$5,000 (infra + eng)", "4-8 months eng"],
                ["Verification Civilization", "Manual QA review cycles + fact-check contractors", "$5,000–$20,000", "Ongoing"],
                ["Hierarchical Memory (4 tiers)", "Redis + Pinecone + Neo4j + custom orchestration", "$1,200–$4,000 (infra)", "3-6 months eng"],
                ["10-Tier Autonomy + Approvals", "Custom approval workflow + audit UI", "$2,000–$8,000 (eng + tooling)", "3-6 months eng"],
                ["Multi-Environment Segregation", "Separate AWS/GCP accounts + IAM + data isolation", "$1,000–$5,000 (infra + compliance)", "2-4 months eng"],
                ["Circuit Breakers + Recovery", "Custom SRE playbooks + monitoring + runbooks", "$3,000–$10,000 (SRE ops)", "Ongoing"],
                ["Integration Hub (29 providers)", "29 separate OAuth/API integrations + embedded browser + credential vault", "$2,000–$6,000", "6-12 months eng"],
                ["Knowledge Base + RAG", "Vector DB + chunking pipeline + UI + eval harness", "$800–$3,000", "3-5 months eng"],
                ["Trust Scoring + Analytics", "Custom scoring engine + dashboards", "$1,500–$5,000", "2-3 months eng"],
                ["Product Scanner", "Competitive intel tooling (Crayon, Klue, Kompyte)", "$1,500–$6,000 (SaaS)", "Ongoing"],
                ["Content Generator + Reference Intelligence", "Copy agency + brand voice consultancy", "$5,000–$20,000", "Ongoing"],
                ["Social Media Command (10 platforms)", "Hootsuite/Sprout + SMM agency", "$3,000–$15,000", "Ongoing"],
                ["Vibe Coding App Builder", "Junior dev or low-code platform (Retool, Bubble)", "$2,000–$10,000", "Ongoing"],
                ["Voice Command + STT/TTS", "ElevenLabs + Whisper + custom UI wiring", "$400–$1,500", "1-2 months eng"],
                ["Observability + Metrics + Alerts", "Datadog + PagerDuty + custom dashboards", "$2,000–$8,000", "Ongoing"],
                ["Developer Portal + OpenAI-compat API", "Building an LLM reseller gateway", "$3,000–$12,000 (eng + infra)", "8-12 months eng"],
                ["Venture Portfolio + KPIs", "Portfolio ops tooling (Visible, Carta, manual)", "$1,000–$4,000", "Ongoing"],
              ].map(([cap, repl, cost, eff]) => (
                <tr key={cap} className="border-b border-white/5 hover:bg-white/[0.02]">
                  <td className="py-2 px-2 text-zinc-200 font-medium">{cap}</td>
                  <td className="py-2 px-2">{repl}</td>
                  <td className="py-2 px-2 text-amber-400">{cost}</td>
                  <td className="py-2 px-2 text-cyan-400">{eff}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 mt-4">
          <p className="text-xs text-amber-200 leading-relaxed">
            <span className="font-bold">Aggregate estimate:</span> a comparable DIY stack runs <span className="font-bold">$110,000–$355,000/month</span> in tooling + salary,
            plus <span className="font-bold">18–24 months</span> of engineering to integrate. MAARS Command collapses that into one subscription with one API key.
          </p>
        </div>

        {/* Total System Value */}
        <div className="mt-6 rounded-2xl border border-fuchsia-500/30 bg-gradient-to-br from-fuchsia-500/10 via-violet-500/10 to-indigo-500/10 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-fuchsia-300" />
            <h3 className="text-base font-bold text-white font-['Outfit']">Total System Value — What MAARS Command Is Worth</h3>
          </div>
          <p className="text-xs text-zinc-300 leading-relaxed mb-4">
            Adding up every replaced subsystem, every avoided hire, every month of engineering collapsed into a turnkey platform:
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            {[
              { label: "Build-From-Scratch Cost", value: "$3.5M–$8.5M", sub: "8–15 engineers × 18–24 months", color: "text-fuchsia-300" },
              { label: "Annual Operating Cost", value: "$1.3M–$4.3M", sub: "Tooling, infra, SaaS, salaries", color: "text-amber-300" },
              { label: "3-Year TCO (DIY)", value: "$7.4M–$21.4M", sub: "Build + 3 yrs ops + integration debt", color: "text-rose-300" },
              { label: "Time-To-Market Saved", value: "18–24 months", sub: "From zero to enterprise-ready", color: "text-cyan-300" },
            ].map(s => (
              <div key={s.label} className="bg-black/30 border border-white/10 rounded-xl p-3 text-center">
                <p className={`text-xl font-bold ${s.color} font-['Outfit']`}>{s.value}</p>
                <p className="text-[10px] text-zinc-300 mt-1 font-medium">{s.label}</p>
                <p className="text-[9px] text-zinc-500 mt-0.5">{s.sub}</p>
              </div>
            ))}
          </div>
          <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
            <p>
              <span className="text-fuchsia-300 font-bold">Conservative replacement value: $7.4M over 3 years.</span> This is the TCO to rebuild MAARS Command from scratch with a mid-market engineering team
              — architecture + integrations + governance + UI + testing + ongoing SRE — <em>before</em> the model-call bill itself.
            </p>
            <p>
              <span className="text-amber-300 font-bold">Enterprise-grade replacement value: $21.4M+ over 3 years.</span> Organizations that need SOC2 compliance, multi-region deployment, per-tenant isolation,
              24/7 on-call, and domain-specific verifier tuning typically land at the top of this band — some well above it.
            </p>
            <p>
              <span className="text-cyan-300 font-bold">Real strategic value ≫ replacement cost.</span> Time-to-market is the hidden multiplier: shipping an autonomous-AI platform 18–24 months faster than a competitor
              is worth more than any line-item on this page. For a venture studio running 3+ products, MAARS Command replaces an entire AI platform team plus the tool stack — effectively a <span className="font-bold text-white">$10M–$30M+ internal program</span> substituted by one account.
            </p>
            <p className="text-[11px] text-zinc-500 italic pt-2">
              Ranges are conservative mid-market estimates. Enterprise deployments (SOC2, multi-region, custom verifiers, dedicated infra) routinely land 2–5× higher.
              Replacement cost ≠ list price — MAARS Command sells for a small fraction of TCO because it spreads platform R&D across every customer.
            </p>
          </div>
        </div>
      </Section>

      {/* System Worth */}
      <Section title="What MAARS Command Is Worth" subtitle="The whole-system valuation, seen through four lenses" icon={DollarSign} color="bg-emerald-500/15" id="worth">
        <p className="text-xs text-zinc-400 mb-4">
          \"Value\" depends on who's asking. A CFO asks replacement cost. A buyer asks acquisition comp. An investor asks pre-money. A founder asks strategic worth.
          Here is MAARS Command valued through all four lenses, each with its own math and comparables — so whichever seat you're in, the number is grounded.
        </p>

        {/* Headline value card */}
        <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/15 via-cyan-500/10 to-indigo-500/10 p-6 mb-5 text-center">
          <p className="text-[10px] uppercase tracking-[0.3em] text-emerald-300/80 font-bold mb-2">Headline Valuation</p>
          <p className="text-4xl sm:text-5xl font-bold font-['Outfit'] bg-gradient-to-r from-emerald-300 via-cyan-300 to-violet-300 bg-clip-text text-transparent">
            $40M – $180M
          </p>
          <p className="text-xs text-zinc-300 mt-3 max-w-2xl mx-auto leading-relaxed">
            As-built worth of the MAARS Command platform today — centered on the fair-market band for a pre-revenue enterprise AI platform with
            484 endpoints, 458 agents, 58,422 skills, 33 LLM providers, full governance + verification, and an OpenAI-compatible gateway.
            The floor is salvage/acqui-hire. The ceiling is strategic acquisition by an incumbent.
          </p>
        </div>

        {/* Four valuation lenses */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            {
              lens: "Replacement Cost",
              who: "CFO / rebuild-from-scratch view",
              value: "$7.4M – $21.4M",
              color: "text-amber-300",
              border: "border-amber-500/30",
              bg: "bg-amber-500/5",
              body: "Cost to rebuild MAARS Command from zero: $3.5M–$8.5M to build (8–15 engineers × 18–24 months) plus $1.3M–$4.3M/yr operating. 3-year TCO = $7.4M–$21.4M before a single customer API call. Enterprise-grade (SOC2, multi-region, 24/7 on-call) lands at the top of the band or above.",
            },
            {
              lens: "Fair Market Value",
              who: "Independent appraisal / asset transfer",
              value: "$15M – $45M",
              color: "text-cyan-300",
              border: "border-cyan-500/30",
              bg: "bg-cyan-500/5",
              body: "Arms-length sale of the codebase + IP + agent library + skill pack + gateway, assuming a knowledgeable buyer and no special synergies. Premium over pure replacement because the bugs are already found, the integrations work, and the design decisions are made — a year of de-risking baked in.",
            },
            {
              lens: "Strategic Acquisition Value",
              who: "Incumbent buyer (OpenAI, Anthropic, Salesforce, MSFT)",
              value: "$60M – $180M",
              color: "text-fuchsia-300",
              border: "border-fuchsia-500/30",
              bg: "bg-fuchsia-500/5",
              body: "What a strategic buyer pays to acquire the platform plus the team. Comparable AI-platform acqui-hires and strategic deals in 2024–2025 range $30M–$250M at this feature depth (governance + verification + gateway is rare). A vertical player buying to add enterprise orchestration would pay top-of-band.",
            },
            {
              lens: "Pre-Money Venture Valuation",
              who: "Seed / Series A investor",
              value: "$40M – $120M pre",
              color: "text-violet-300",
              border: "border-violet-500/30",
              bg: "bg-violet-500/5",
              body: "What a VC underwrites based on platform depth + TAM + team. AI-infrastructure rounds in 2024–2025 closed at $40M–$150M pre-money for platforms with this feature surface even pre-revenue. Early revenue traction (>$1M ARR) pushes the top to $250M+. Vertical SKU launches (MAARS-for-Law etc.) stack on.",
            },
          ].map(item => (
            <div key={item.lens} className={`${item.bg} border ${item.border} rounded-xl p-4`}>
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <p className="text-sm font-bold text-white">{item.lens}</p>
                  <p className="text-[10px] text-zinc-500">{item.who}</p>
                </div>
                <p className={`text-lg font-bold font-['Outfit'] ${item.color} shrink-0`}>{item.value}</p>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>

        {/* Bottom-line */}
        <div className="mt-5 rounded-xl border border-white/10 bg-zinc-900/50 p-4">
          <p className="text-xs text-zinc-300 leading-relaxed">
            <span className="text-emerald-300 font-bold">Bottom line:</span> MAARS Command is worth between <span className="font-bold text-white">$40M at the low end</span> (pre-revenue venture valuation or strategic floor)
            and <span className="font-bold text-white">$180M at the high end</span> (strategic acquisition by an incumbent who needs the platform + team). The numbers stack across lenses:
            rebuilding costs $7M+, fair market sale clears $15M+, a strategic buyer pays $60M+, and a VC underwrites $40M+ pre-money. Add early revenue
            (&gt;$1M ARR), a SOC2 cert, and one vertical SKU shipped — all reachable within 12 months — and the whole band shifts to <span className="font-bold text-white">$150M–$500M+</span>.
          </p>
        </div>

        <p className="text-[10px] text-zinc-600 mt-3 italic">
          All ranges are mid-2026 benchmarks. Private-market comps: Harvey AI ($3B), Glean ($4.6B), Writer ($1.9B), Cresta ($1.6B), Decagon ($1.5B), Sierra ($4.5B) — all AI-platform categories MAARS competes in.
          MAARS is earlier stage and pre-revenue, which is why the band starts at $40M, not $1B+.
        </p>
      </Section>

      {/* Pitch Deck */}
      <Section title="MAARS Command — Pitch Deck" subtitle="14 slides · the investor story, at a glance" icon={Rocket} color="bg-rose-500/15" id="pitch">
        <p className="text-xs text-zinc-400 mb-4">
          Fundraising-ready deck summarizing the business case in 14 slides. Each slide is a self-contained card —
          screenshot, paste into a Google Slides template, or use as speaker notes. All numbers are grounded in the platform you just read about.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            {
              n: "01",
              title: "Cover",
              kicker: "Autonomous AI Enterprise Operating System",
              body: (
                <>
                  <p className="text-sm text-white font-bold mb-1">MAARS Command</p>
                  <p className="text-xs text-zinc-300 leading-relaxed">
                    The operating system for autonomous AI workforces. 458 agents across 28 networks, 58,422 curated skills, 33 LLM providers, one API key.
                  </p>
                  <p className="text-[10px] text-zinc-500 mt-2">MAARS Global Corporation · Est. 2026 · Seeking Seed / Series A</p>
                </>
              ),
            },
            {
              n: "02",
              title: "The Problem",
              kicker: "Building enterprise AI is 18–24 months of integration hell",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li>Every org wants AI agents. Nobody wants to build the plumbing.</li>
                  <li>33 LLM providers, 29 integrations, 4 memory tiers, governance, verification, billing — an 18–24 month build.</li>
                  <li>DIY stacks cost <span className="text-amber-300 font-medium">$110k–$355k/month</span> in tooling + salary.</li>
                  <li>Meanwhile: chatbot wrappers hallucinate, no audit trail, no rollback, no cost controls, no trust.</li>
                </ul>
              ),
            },
            {
              n: "03",
              title: "The Solution",
              kicker: "One platform. One key. Every capability enterprises need.",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li><span className="text-white font-medium">Task Graph Kernel</span> — DAG execution with checkpoints + rollback</li>
                  <li><span className="text-white font-medium">Verification Civilization</span> — multi-model cross-check on 6 dimensions</li>
                  <li><span className="text-white font-medium">10-Tier Autonomy</span> — human-approval → unsupervised, per agent</li>
                  <li><span className="text-white font-medium">58,422 Skill Library</span> — grounded RAG, no prompt engineering</li>
                  <li><span className="text-white font-medium">Universal Gateway</span> — OpenAI-compatible, 175,609+ models, one key</li>
                </ul>
              ),
            },
            {
              n: "04",
              title: "How It Works",
              kicker: "From English goal to executed workflow",
              body: (
                <div className="text-xs text-zinc-300 space-y-1.5 leading-relaxed">
                  <p>① You describe a goal in English →</p>
                  <p>② Kernel compiles a task graph (DAG) →</p>
                  <p>③ Router picks the best model per node →</p>
                  <p>④ Agents execute in parallel, grounded in skills + KB →</p>
                  <p>⑤ Verification cross-checks every claim →</p>
                  <p>⑥ Approval gates where human sign-off required →</p>
                  <p>⑦ Audit log records every decision, forever.</p>
                </div>
              ),
            },
            {
              n: "05",
              title: "Market Size",
              kicker: "Enterprise AI orchestration — emerging $100B+ category",
              body: (
                <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
                  <div className="flex items-center justify-between"><span>TAM — Global enterprise AI ops</span><span className="text-emerald-300 font-bold">$150B by 2030</span></div>
                  <div className="flex items-center justify-between"><span>SAM — AI agent platforms</span><span className="text-cyan-300 font-bold">$40B by 2028</span></div>
                  <div className="flex items-center justify-between"><span>SOM — Mid-market + venture studios</span><span className="text-violet-300 font-bold">$2.5B 3-yr reachable</span></div>
                  <p className="text-[10px] text-zinc-500 pt-2 italic">Gartner, IDC, McKinsey 2024–2025 enterprise AI spend forecasts.</p>
                </div>
              ),
            },
            {
              n: "06",
              title: "Product Depth",
              kicker: "What's already built and shipping",
              body: (
                <div className="grid grid-cols-2 gap-2 text-xs text-zinc-300">
                  {[
                    ["458", "Agents"],
                    ["27", "Networks"],
                    ["58,422", "Skills"],
                    ["33", "LLM Providers"],
                    ["175,609+", "Models"],
                    ["484", "API Endpoints"],
                    ["62", "Frontend Pages"],
                    ["28", "Integrations"],
                  ].map(([v, l]) => (
                    <div key={l} className="bg-black/30 rounded p-2 text-center">
                      <p className="text-sm font-bold text-rose-300">{v}</p>
                      <p className="text-[9px] text-zinc-500 uppercase tracking-wider">{l}</p>
                    </div>
                  ))}
                </div>
              ),
            },
            {
              n: "07",
              title: "Why We Win",
              kicker: "Moats that compound over time",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li><span className="text-white font-medium">Depth moat</span> — 35 core systems vs. competitors' 3–5</li>
                  <li><span className="text-white font-medium">Data flywheel</span> — every verification pass is labeled data</li>
                  <li><span className="text-white font-medium">Platform lock-in</span> — custom skills + KB + brain profiles create switching cost</li>
                  <li><span className="text-white font-medium">Provider neutrality</span> — 33 providers = we win when models commoditize</li>
                  <li><span className="text-white font-medium">Governance trust</span> — SOC2 roadmap unlocks enterprise contracts competitors can't touch</li>
                </ul>
              ),
            },
            {
              n: "08",
              title: "Business Model",
              kicker: "Hybrid: subscription + PAYG + marketplace",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li><span className="text-white font-medium">PAYG credits</span> — 65% to AI costs, 35% platform take</li>
                  <li><span className="text-white font-medium">Subscription tiers</span> — $49/$299/$1,499/month user tiers</li>
                  <li><span className="text-white font-medium">Enterprise</span> — $50k–$500k+ ARR (SOC2, dedicated env, SLA)</li>
                  <li><span className="text-white font-medium">Marketplace (roadmap)</span> — 30% take on skill + agent + workflow sales</li>
                  <li><span className="text-white font-medium">Gateway API</span> — developer revenue on 175k+ model calls</li>
                </ul>
              ),
            },
            {
              n: "09",
              title: "Traction",
              kicker: "Platform shipped; commercial phase opening",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li>Platform code-complete — <span className="text-emerald-300">522 endpoints, 62 pages, 29 integrations live (incl. self-hosted Embedded Browser)</span></li>
                  <li>58,422-skill library ingested + matched — largest known skill catalog</li>
                  <li>Universal Gateway operational — OpenAI-compatible, live model validation</li>
                  <li>Governance + Verification engines in production flow</li>
                  <li>Early user cohort onboarding — feedback loop active</li>
                  <li className="text-rose-300 italic">Seeking seed to accelerate GTM, compliance, and vertical SKUs.</li>
                </ul>
              ),
            },
            {
              n: "10",
              title: "Competitive Landscape",
              kicker: "Owning the orchestration layer above every model",
              body: (
                <div className="space-y-1.5 text-xs text-zinc-300 leading-relaxed">
                  <div className="flex items-center justify-between"><span><span className="text-white font-medium">LangChain / LlamaIndex</span></span><span className="text-zinc-500">Dev library · no governance, no UI</span></div>
                  <div className="flex items-center justify-between"><span><span className="text-white font-medium">CrewAI / AutoGen</span></span><span className="text-zinc-500">Agent framework · no platform</span></div>
                  <div className="flex items-center justify-between"><span><span className="text-white font-medium">Zapier / Make</span></span><span className="text-zinc-500">No-code · no autonomy, no agents</span></div>
                  <div className="flex items-center justify-between"><span><span className="text-white font-medium">Glean / Writer / Harvey</span></span><span className="text-zinc-500">Vertical SaaS · single use case</span></div>
                  <div className="flex items-center justify-between"><span><span className="text-white font-medium">Salesforce Agentforce</span></span><span className="text-zinc-500">Bolt-on · locked in SF ecosystem</span></div>
                  <p className="pt-1 text-emerald-300 font-medium">MAARS = platform depth of all five combined, provider-neutral.</p>
                </div>
              ),
            },
            {
              n: "11",
              title: "Go-to-Market",
              kicker: "Three wedges, sequenced for compounding distribution",
              body: (
                <ul className="text-xs text-zinc-300 space-y-1.5 leading-relaxed list-disc pl-4">
                  <li><span className="text-white font-medium">Wedge 1 — Developers</span> — Universal Gateway with maars-sk-* key; bottom-up adoption via OpenAI compatibility</li>
                  <li><span className="text-white font-medium">Wedge 2 — Mid-market</span> — $299/$1,499 tiers; Campaign Builder + Content Generator + Social Command as acquisition magnets</li>
                  <li><span className="text-white font-medium">Wedge 3 — Enterprise</span> — SOC2 + vertical SKUs (Law, Finance, Healthcare); $50k–$500k ARR deals</li>
                  <li>Marketplace unlocks in year 2 — 3rd-party creators drive network effects</li>
                </ul>
              ),
            },
            {
              n: "12",
              title: "Financial Projections",
              kicker: "3-year ARR trajectory (base case)",
              body: (
                <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
                  <div className="flex items-center justify-between border-b border-white/10 pb-1.5"><span className="text-zinc-500">Year 1 — Dev + mid-market</span><span className="text-emerald-300 font-bold">$1.2M ARR</span></div>
                  <div className="flex items-center justify-between border-b border-white/10 pb-1.5"><span className="text-zinc-500">Year 2 — SOC2 + first vertical</span><span className="text-cyan-300 font-bold">$8M ARR</span></div>
                  <div className="flex items-center justify-between border-b border-white/10 pb-1.5"><span className="text-zinc-500">Year 3 — Enterprise + marketplace</span><span className="text-violet-300 font-bold">$35M ARR</span></div>
                  <div className="flex items-center justify-between pt-1"><span className="text-white font-medium">Gross margin target</span><span className="text-emerald-300 font-bold">65–72%</span></div>
                  <p className="text-[10px] text-zinc-500 italic pt-1">Comp benchmarks: Harvey $75M→$250M ARR Y2→Y3, Writer similar trajectory.</p>
                </div>
              ),
            },
            {
              n: "13",
              title: "Valuation",
              kicker: "As-built worth · with traction uplift",
              body: (
                <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
                  <div className="flex items-center justify-between"><span>Today (pre-revenue, as-built)</span><span className="text-emerald-300 font-bold">$40M–$180M</span></div>
                  <div className="flex items-center justify-between"><span>+12mo (ARR + SOC2 + vertical)</span><span className="text-cyan-300 font-bold">$150M–$500M</span></div>
                  <div className="flex items-center justify-between"><span>Category comps (2024–25)</span><span className="text-violet-300 font-bold">$1B–$4.6B</span></div>
                  <p className="text-[10px] text-zinc-500 italic pt-1">Category: Harvey ($3B), Glean ($4.6B), Writer ($1.9B), Sierra ($4.5B), Decagon ($1.5B).</p>
                </div>
              ),
            },
            {
              n: "14",
              title: "The Ask",
              kicker: "Raising to accelerate GTM and compliance",
              body: (
                <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
                  <p className="text-sm text-white font-bold">$8M Seed / Series A</p>
                  <p className="text-[11px] text-zinc-500">18-month runway · use of funds:</p>
                  <ul className="space-y-1 list-disc pl-4">
                    <li><span className="text-emerald-300 font-medium">40%</span> — GTM + sales team (mid-market + enterprise wedges)</li>
                    <li><span className="text-cyan-300 font-medium">25%</span> — SOC2 + HIPAA + first vertical SKU</li>
                    <li><span className="text-violet-300 font-medium">20%</span> — Engineering — marketplace, SDKs, mobile</li>
                    <li><span className="text-amber-300 font-medium">10%</span> — Brand + content + category creation</li>
                    <li><span className="text-rose-300 font-medium">5%</span> — Compliance + ops + legal</li>
                  </ul>
                  <p className="text-[11px] text-white font-medium pt-2">Target milestone: $8M ARR + SOC2 + 50 enterprise logos in 18 months.</p>
                </div>
              ),
            },
          ].map(slide => (
            <div key={slide.n} className="bg-zinc-900/60 border border-rose-500/20 rounded-xl overflow-hidden print-card">
              <div className="flex items-start gap-3 p-4 border-b border-white/5 bg-gradient-to-r from-rose-500/10 to-transparent">
                <div className="w-10 h-10 rounded-lg bg-rose-500/20 border border-rose-500/30 flex items-center justify-center shrink-0">
                  <p className="text-sm font-bold text-rose-300 font-['Outfit']">{slide.n}</p>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-white">{slide.title}</p>
                  <p className="text-[10px] text-zinc-400 leading-tight">{slide.kicker}</p>
                </div>
              </div>
              <div className="p-4">{slide.body}</div>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-zinc-600 mt-4 italic text-center">
          Numbers based on current product state + public category comps. Business projections directional, not commitments.
          Export the deck: click Download Docs at top → print to PDF → filter to this section.
        </p>
      </Section>

      {/* A-Z Feature Index */}
      <Section title="A-Z Feature Index" subtitle="Every feature, alphabetized — use Ctrl+F to jump" icon={FileCode} color="bg-indigo-500/15" id="az-index">
        <p className="text-xs text-zinc-400 mb-4">
          Quick reference of every user-facing feature in MAARS Command, alphabetized. Each entry is a short description so you know what it does at a glance.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-4 gap-y-1">
          {[
            ["Admin Dashboard", "Central admin hub — users, pricing, integrations, branding, analytics"],
            ["Agent Activity Monitor", "Live WebSocket feed of every agent's state, messages, and tool calls"],
            ["Agent Brain Viewer", "GET /agents/{id}/brain — see every knowledge chunk loaded for any agent"],
            ["Agent Catalog", "Browse all 458+ agents with network, role, and capability filters"],
            ["Agent Networks", "28 domain categories (Strategic, Engineering, Creative, Growth, Core Team, etc.)"],
            ["Agent Team Builder", "Group any subset of agents into custom named teams"],
            ["Analytics Dashboard", "Usage, cost, trust, performance — per user, agent, network, env"],
            ["API Keys", "Issue/rotate maars-sk-* keys for developer access to the Universal Gateway"],
            ["Approvals", "Human-in-loop queue for gated actions — approve, reject, edit, escalate"],
            ["Audit Log", "Immutable record of every action — tamper-proof, queryable, exportable"],
            ["Autonomy Tiers", "10 levels from full-approval (T1) to unsupervised (T10) per agent"],
            ["Avatar Generator", "Admin batch-generates agent avatars (unique per agent)"],
            ["Brain Profiles", "Per-agent model, tone, temperature, max-tokens, tool permissions"],
            ["Branding", "Admin configures logo, domain, theme — multi-tenant ready"],
            ["Browser — Embedded", "Self-hosted Chromium under backend/browser_data/ — lives inside MAARS, never at OS user level"],
            ["Browser — Multi-Tab", "Chrome-style tab strip; agents, system, and user share the same tabs with three-way handoff"],
            ["Browser — Fullscreen", "One-click fullscreen (Fullscreen API) — canvas scales to full viewport"],
            ["Browser — Stream Modes", "PNG/JPEG × event-driven or continuous 1–24 fps; persists per user"],
            ["Browser Agent (Autonomous)", "Natural-language goal → perceive (vision) → act → repeat. 2FA / CAPTCHA hand-off"],
            ["Browser Vision", "GPT-4o / Claude multi-modal decides next action from screenshot + goal"],
            ["Browser Integration Connect", "Click any of 29 integrations — opens login/OAuth in tagged tab, agent drives optionally"],
            ["Browser Domain Policy", "Per-env allow/deny hostname patterns; default blocks localhost/cloud-metadata"],
            ["Browser Minutes Budget", "Per-user daily cap (default 60 min); admin-overridable, 429 on exhaust"],
            ["Budget Controller", "Per-user, per-agent, per-env credit caps with soft/hard limits"],
            ["Campaign Builder", "Multi-channel campaign planning + AI-generated variants + A/B"],
            ["Catalog Manager", "458+ agent registry with network lookup and hot-swap"],
            ["Chat History", "Persistent chat threads per agent with search and PDF export"],
            ["Circuit Breakers", "Auto-trip on spend spike, error rate, retry storm, policy violation"],
            ["Code Explorer (Admin)", "Browse every backend/frontend file — view, search, ZIP export"],
            ["Collaboration Engine", "Agent-to-agent info share, review request, handoff, coordination"],
            ["Command Palette", "Press / or Ctrl+K — search pages, agents, actions with voice input"],
            ["Content Generator", "Marketing copy, social posts, emails, ads, press releases, blueprints"],
            ["Cost Governance", "Real-time per-call cost tracking with alert thresholds (80/100%)"],
            ["Credits", "Pay-as-you-go credit balance with instant top-up and transaction log"],
            ["Custom Brain", "Per-user custom instructions attached to agent knowledge"],
            ["Developer Portal", "/developer — API key, model browser, playground, quickstart"],
            ["Environments", "Simulation · Sandbox · Staging · Production — isolated policies/budgets"],
            ["Execution Mode", "System-wide toggle: real external actions ON vs. mocked (Simulation)"],
            ["Gmail Integration", "OAuth-based real email sending through connected Gmail account"],
            ["Google Calendar", "OAuth-based event creation, updates, and scheduling"],
            ["Image Generation", "GPT Image 1, DALL-E 3, Nano Banana (Gemini 3.1 Flash image)"],
            ["Incident Ledger", "Every fault logged with timeline, severity, blast radius, remediation"],
            ["Ingest Script", "backend/scripts/ingest_skills.py — bulk re-ingest skills to all agents"],
            ["Insights Page", "Personal analytics — your usage, best agents, cost breakdown"],
            ["Integration Hub", "29 providers: payments, email, CRM, ecommerce, social, dev, LLM, embedded browser"],
            ["Kernel Dashboard", "Task graphs, goals, scheduler, budget, policies — one control plane"],
            ["Knowledge Base", "Upload PDFs/DOCX/MD per agent; chunked, embedded, cited in replies"],
            ["Knowledge Graph", "Entity-relationship memory tier — traversable, queryable"],
            ["KPI Dashboard", "Venture/org-level KPIs: revenue, burn, retention, NPS, CAC, LTV"],
            ["LLM Router", "Classifies task type + budget → picks best model across 33 providers"],
            ["Media Upload", "Files, audio, video uploads with STT transcription (Whisper)"],
            ["Memory Governance", "CRUD memories with category tags, importance, decay, pruning"],
            ["Memory Hierarchy", "4 tiers: working · episodic · semantic · knowledge graph"],
            ["Messenger Chat", "Floating assistant widget on every page"],
            ["Model Comparison", "POST /v1/models/compare — run same prompt on up to 4 models"],
            ["Model Router Dashboard", "Live routing decisions, classification accuracy, per-model latency"],
            ["Notifications", "Real-time alerts for task completion, approvals, incidents, budget"],
            ["OAuth", "Google, GitHub OAuth flows with secure credential vault"],
            ["Observability Dashboard", "Live metrics, alerts, trace logs, per-service health"],
            ["Operator Control Panel", "Low-level kernel controls — halt, resume, reassign, escalate"],
            ["Organization", "Org-level settings, teams, roles, permissions"],
            ["Payments", "Stripe checkout, subscriptions, PAYG credit top-ups, invoices"],
            ["Personal Secretary", "Dedicated agent that executes real-world actions on your behalf"],
            ["Policy Engine", "Governance rules, compliance, autonomy enforcement per env"],
            ["Preview Mode", "Preview a workflow before executing in Production"],
            ["Pricing Admin", "Plan editor — tiers, credits, overage rules, per-provider markup"],
            ["Product Scanner", "Real-time competitive intelligence — pricing, features, sentiment"],
            ["Project Catalog", "Browse all active projects with phase, owner, timeline"],
            ["Projects", "Multi-task project lifecycle with phases and active summary"],
            ["Quality Service", "Pass rates, escalation tracking, auto-review of agent outputs"],
            ["RBAC", "Role-based access — admin · manager · user with page/route gates"],
            ["Real-World Actions", "Gmail, Calendar, Twilio, SendGrid — real external calls when enabled"],
            ["Recovery", "Quarantine · rollback · retry — automatic blast-radius containment"],
            ["Reference Intelligence", "Paste text/image → Style Blueprint for on-brand content generation"],
            ["RAG Engine", "Retrieval with chunk-level citations across skills, KB, web"],
            ["Settings", "User preferences, integrations, notifications, default model/tier"],
            ["Simulation Mode", "All external actions mocked — zero cost, full logging, chaos-safe"],
            ["Skill Library", "58,422 SKILL.md files auto-matched to agents at creation"],
            ["SMTP Config", "Admin-configurable SMTP for transactional email"],
            ["Social Media Command", "10 platforms: post, boost, DM, cold-email, cold-call, translate"],
            ["Stats (Admin)", "Platform-wide analytics: MRR, DAU, cost, top agents, top errors"],
            ["STT / Whisper", "Speech-to-text in 50+ languages via OpenAI Whisper"],
            ["Subscriptions", "Monthly plans, PAYG, hybrid billing with fallover"],
            ["Task Graph", "DAG execution with parallel branches, checkpoints, resumable"],
            ["Tasks", "Task creation, assignment, status, project linking"],
            ["Team Builder", "Group agents into named teams with missions"],
            ["Teams", "User team management with invites and roles"],
            ["Test Harness", "Scenario testing for autonomous workflows in Simulation"],
            ["Tool Registry", "Tool discovery, validation, sandboxing across 70+ built-in tools"],
            ["Trust Analytics", "0-100 trust score per agent — success, latency, quality, consistency"],
            ["TTS / ElevenLabs", "Text-to-speech in multiple languages including Bangla + English"],
            ["Universal Gateway Key", "One maars-sk-* key for all 175,609+ models, OpenAI-compatible"],
            ["Universal Reference Intelligence", "Extract style from any text/image → reusable Blueprint"],
            ["Usage Stats", "Per-user, per-agent, per-provider, per-task-type cost breakdowns"],
            ["Venture Portfolio", "Multi-product tracking with stage gates and cross-venture benchmarks"],
            ["Verification Civilization", "Multi-verifier fact-checking with 6-dimensional consensus"],
            ["Vibe Coding", "Build apps by talking — HTML/CSS/JS generated live with preview"],
            ["Video Generation", "Sora 2 — 4-12s AI video from text descriptions"],
            ["Voice Commands", "Microphone-based navigation and search via Whisper"],
            ["Web Search", "Perplexity-grounded live web search embedded in every chat"],
            ["WebSocket Streams", "Live activity feed + Infinity execution streaming"],
            ["Webhooks", "Signed HMAC-SHA256 webhooks for budget, rate limit, completion events"],
            ["Workers", "Job queue with per-worker stats, retry logic, priority levels"],
            ["Workflow Builder", "Visual drag-drop flowchart for automated multi-step workflows"],
            ["Workspace", "Per-user brain, artifacts, tool logs, KPIs, execution gateway"],
          ].map(([name, desc]) => (
            <div key={name} className="flex items-start gap-2 py-1 border-b border-white/[0.03]">
              <span className="text-[11px] font-medium text-indigo-300 shrink-0 min-w-[140px]">{name}</span>
              <span className="text-[10px] text-zinc-500 leading-tight">{desc}</span>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-zinc-600 mt-4 italic">{/* dynamic count */}
          {SYSTEMS.length} core systems · 522 API endpoints · 62 pages · 84+ UI components · 29 external integrations (incl. Embedded Browser) · 33 LLM providers · 175,609+ models · 58,422 skills · 458+ agents across 28 networks.
        </p>
      </Section>

      {/* Roadmap */}
      <Section title="Roadmap — What's Shipped, In-Flight, and Next" subtitle="12-month execution plan across product, compliance, and GTM" icon={Rocket} color="bg-cyan-500/15" id="roadmap">
        <p className="text-xs text-zinc-400 mb-4">
          Where MAARS Command is today and where it's going next. Shipped items are live in production. In-flight items are in active development. Next items are committed but not yet started.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              phase: "Shipped",
              badge: "✓ Live",
              badgeColor: "text-emerald-300 bg-emerald-500/20 border-emerald-500/30",
              border: "border-emerald-500/20",
              items: [
                "Task Graph Execution Kernel (131 endpoints)",
                "458+ agents across 28 networks",
                "58,422-skill library + RAG ingestion",
                "33 LLM providers · OpenAI-compat gateway",
                "10-tier autonomy + approval workflow",
                "Verification Civilization (6-dim scoring)",
                "Hierarchical memory (4 tiers)",
                "Multi-environment segregation (4 envs)",
                "Circuit breakers + recovery + incidents",
                "29 external integrations (OAuth + API)",
                "Embedded Browser runtime (multi-tab, fullscreen, agent-driven)",
                "Autonomous BrowserAgent with 2FA hand-off + vision (GPT-4o / Claude)",
                "Vibe Coding · Content Gen · Campaign Builder",
                "Social Media Command (10 platforms)",
                "PAYG + subscription billing",
                "Developer Portal + maars-sk-* keys",
                "522 API endpoints · 62 frontend pages",
              ],
            },
            {
              phase: "In-Flight (Q1–Q2)",
              badge: "In Progress",
              badgeColor: "text-amber-300 bg-amber-500/20 border-amber-500/30",
              border: "border-amber-500/20",
              items: [
                "SOC2 Type I audit — observation period active",
                "Skill Marketplace (beta) — creator revenue share",
                "Mobile PWA optimization for tablet/phone",
                "Per-tenant fine-tuned verifiers",
                "Advanced cost optimization (route-by-price)",
                "Enterprise SSO (Okta, Azure AD, Google Workspace)",
                "Dedicated VPC deployment option",
                "Webhook subscription library",
                "Expanded Slack + Teams native integration",
                "Voice agent (phone + ElevenLabs live calls)",
                "Real-time collaboration on task graphs",
                "Benchmark leaderboard (public)",
              ],
            },
            {
              phase: "Next (Q3–Q4)",
              badge: "Planned",
              badgeColor: "text-violet-300 bg-violet-500/20 border-violet-500/30",
              border: "border-violet-500/20",
              items: [
                "SOC2 Type II certification",
                "HIPAA compliance + healthcare SKU",
                "Vertical SKUs: MAARS-for-Law, MAARS-for-Finance",
                "Agent Marketplace (third-party certified agents)",
                "Workflow Marketplace (template commerce)",
                "Native iOS + Android apps",
                "EU data residency (Frankfurt region)",
                "GDPR DPA templates + CCPA toolkit",
                "GitHub App — MAARS as a PR reviewer",
                "ISO 27001 kickoff",
                "White-label / OEM partner program",
                "Verification-as-a-Service (/v1/verify public)",
                "Trust-Score-as-a-Service API",
                "Academic research partnerships + eval dataset publishing",
              ],
            },
          ].map(col => (
            <div key={col.phase} className={`bg-zinc-900/50 border ${col.border} rounded-xl p-4`}>
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-bold text-white">{col.phase}</p>
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${col.badgeColor}`}>{col.badge}</span>
              </div>
              <ul className="space-y-1.5">
                {col.items.map(item => (
                  <li key={item} className="flex items-start gap-2">
                    <div className="w-1 h-1 rounded-full bg-zinc-500 mt-2 shrink-0" />
                    <p className="text-[11px] text-zinc-300 leading-snug">{item}</p>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-zinc-600 mt-3 italic">
          Roadmap items are directional commitments; exact timing depends on enterprise customer feedback, compliance auditor scheduling, and ecosystem readiness.
        </p>
      </Section>

      {/* Security & Compliance Status */}
      <Section title="Security & Compliance — Current Status" subtitle="Which certifications and controls are live, in-progress, or planned" icon={Shield} color="bg-red-500/15" id="compliance">
        <p className="text-xs text-zinc-400 mb-4">
          Enterprise buyers need evidence, not promises. Here's exactly where MAARS stands on every major compliance framework and security control today.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { name: "SOC 2 Type I", status: "In Progress", color: "amber", note: "Observation period active · target audit completion Q2" },
            { name: "SOC 2 Type II", status: "Planned", color: "violet", note: "Q4 after Type I; 6-month continuous-controls window" },
            { name: "GDPR", status: "Ready", color: "emerald", note: "DPA template available · data-export + right-to-erasure live" },
            { name: "CCPA", status: "Ready", color: "emerald", note: "California resident opt-out flow implemented" },
            { name: "HIPAA", status: "Planned", color: "violet", note: "BAA-ready architecture · full compliance with healthcare SKU" },
            { name: "ISO 27001", status: "Planned", color: "violet", note: "Kickoff planned post-SOC2 Type II" },
            { name: "PCI-DSS", status: "Delegated", color: "cyan", note: "All card data handled by Stripe (PCI-DSS Level 1)" },
            { name: "Data Encryption", status: "Live", color: "emerald", note: "TLS 1.3 in transit · AES-256 at rest · hardware-backed keys" },
            { name: "Audit Logging", status: "Live", color: "emerald", note: "Immutable · 7-yr retention (prod) · full who/what/when" },
            { name: "RBAC", status: "Live", color: "emerald", note: "Admin · Manager · User · Custom roles · route + action gated" },
            { name: "Credential Vault", status: "Live", color: "emerald", note: "Encrypted secrets store · hot-rotate without downtime" },
            { name: "Penetration Testing", status: "Scheduled", color: "amber", note: "Annual third-party pentest · next cycle pre-SOC2 audit" },
            { name: "Incident Response", status: "Live", color: "emerald", note: "Playbooks · on-call rotation · incident ledger · RCA process" },
            { name: "SSO (Okta/Azure AD)", status: "In Progress", color: "amber", note: "Enterprise SSO beta Q2; SAML + OIDC" },
            { name: "Data Residency", status: "Planned", color: "violet", note: "US-only today · EU (Frankfurt) region Q4" },
            { name: "DDoS Protection", status: "Live", color: "emerald", note: "Cloud-provider WAF · rate-limit per API key · circuit breakers" },
            { name: "Backup & DR", status: "Live", color: "emerald", note: "Hourly snapshots · multi-AZ · tested quarterly" },
            { name: "Zero-Trust Network", status: "Live", color: "emerald", note: "Per-service mTLS · no flat-network access · JIT elevation" },
          ].map(item => {
            const statusColorMap = {
              emerald: "text-emerald-300 bg-emerald-500/20 border-emerald-500/30",
              amber: "text-amber-300 bg-amber-500/20 border-amber-500/30",
              violet: "text-violet-300 bg-violet-500/20 border-violet-500/30",
              cyan: "text-cyan-300 bg-cyan-500/20 border-cyan-500/30",
            };
            return (
              <div key={item.name} className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <p className="text-xs font-bold text-white">{item.name}</p>
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${statusColorMap[item.color]} shrink-0`}>{item.status}</span>
                </div>
                <p className="text-[10px] text-zinc-400 leading-relaxed">{item.note}</p>
              </div>
            );
          })}
        </div>
        <p className="text-[10px] text-zinc-600 mt-3 italic">
          Live = production, auditable today. In Progress = active work toward completion. Planned = committed, scheduled, not started. Delegated = handled by a certified third party.
        </p>
      </Section>

      {/* FAQ */}
      <Section title="FAQ — Common Questions" subtitle="What buyers, investors, and developers ask most often" icon={MessageSquare} color="bg-sky-500/15" id="faq">
        <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
          <p className="text-xs text-zinc-400">
            The questions we get every week. If you have one that isn't here, email support.maars@marsgc.net and we'll add it.
          </p>
          <FAQControls rootId="faq-list" />
        </div>
        <div id="faq-list" className="space-y-2" data-faq-list>
          {[
            {
              q: "How is this different from LangChain, CrewAI, or building on OpenAI directly?",
              a: "LangChain and CrewAI are libraries — you still build the platform around them: governance, verification, billing, UI, audit, recovery. Building on OpenAI directly means you're locked to one provider and you build everything else yourself. MAARS gives you the whole enterprise platform (governance, verification, multi-provider routing, UI, audit, recovery, skill library, 458 agents) as one product. Days to value, not quarters.",
            },
            {
              q: "Can I bring my own API keys and avoid your gateway markup?",
              a: "Yes. Every LLM provider can be configured with your own API key in Settings → Integrations. You pay the provider directly and MAARS just routes through. The Universal Gateway with maars-sk-* key is a convenience for teams who don't want to manage 33 provider relationships — but it's optional.",
            },
            {
              q: "What happens when a model provider goes down?",
              a: "Circuit breakers detect elevated error rates or latency and trip. The router automatically falls back through a configured chain (e.g. GPT-5 → Claude Sonnet → Gemini Pro → GPT-4o). If all fallbacks fail, the task graph pauses at the affected node and can resume when a provider recovers — no work lost.",
            },
            {
              q: "How do you handle hallucinations?",
              a: "Every factual claim goes through the Verification Civilization: 2-4 independent verifier models cross-check the same claim on 6 dimensions (factual, grounded, coherent, complete, unbiased, time-fresh). Disagreement flags the claim. Unverifiable specifics get quarantined. The agent's answer ships with the verification score and source citations. No blind trust.",
            },
            {
              q: "Where is data stored? Is it used to train models?",
              a: "Production data lives in the MongoDB cluster in the customer's region (US today; EU region Q4). Nothing is used to train third-party models — every provider is called in data-processor mode with zero-retention headers. Chat history is retained per your settings and fully exportable or deletable on demand (GDPR-compliant).",
            },
            {
              q: "Can I self-host or run on my own cloud?",
              a: "Docker Compose deployment is live today (docker-compose up — full stack in one command). Dedicated VPC deployment (your AWS/GCP/Azure account with MAARS-managed plane) is in-flight for Q2. True air-gapped on-prem is available for enterprise contracts.",
            },
            {
              q: "How much does it cost for a realistic workload?",
              a: "Pay-as-you-go pricing: 65% of every dollar goes to AI model costs (shown live), 35% covers platform. A typical mid-market team with 3-5 active workflows and moderate chat use lands at $500-$2,500/month. Enterprise contracts (SOC2, dedicated env, SLA) start at $50k ARR. Developer gateway usage is metered per call at near-pass-through pricing.",
            },
            {
              q: "Can agents take real-world actions (send emails, make charges, post to social)?",
              a: "Yes — through the Real-World Action Layer. But only when you flip Simulation Mode off. By default every external action returns a realistic mock response so you can safely test a workflow end-to-end before going live. Per-agent autonomy tiers gate what each agent can do, and high-impact actions require human approval.",
            },
            {
              q: "What happens if an agent misbehaves?",
              a: "The Recovery system quarantines it: tools stripped, autonomy forced to Tier 1, flagged for human review. The incident ledger logs the full timeline. You decide whether to reinstate, retrain, or retire the agent. Your workflows auto-reroute through healthy agents in the meantime.",
            },
            {
              q: "How do I add a custom skill or custom agent?",
              a: "Custom skills: drop a new folder at .claude/skills/<name>/ with a SKILL.md file — it's ingested automatically on agent creation or via the bulk ingest script. Custom agents: POST /agents with role, description, capabilities, and optional brain profile. The skill matcher runs automatically and populates the new agent's brain.",
            },
            {
              q: "Is there an OpenAI-compatible API I can point existing code at?",
              a: "Yes. Your maars-sk-* key works at POST /v1/chat/completions with the exact OpenAI SDK — only change the base_url. You get access to all 175,609+ models (609 curated + 175k HuggingFace pass-through) through the same SDK you already use. Model comparison endpoint (/v1/models/compare) runs the same prompt on 4 models in parallel.",
            },
            {
              q: "What's the team's AI background?",
              a: "MAARS was built by MAARS Global Corporation with a team combining full-stack engineering, AI research, and enterprise operations experience. The platform has been in active development since 2026 with focus on governance, verification, and multi-provider orchestration. Team details available under NDA for qualified investors.",
            },
          ].map((item, i) => (
            <details key={i} className="bg-zinc-900/50 border border-white/5 rounded-xl group">
              <summary className="cursor-pointer p-3 flex items-start gap-3 list-none hover:bg-white/[0.02]">
                <ChevronRight className="w-4 h-4 text-sky-400 shrink-0 mt-0.5 transition-transform group-open:rotate-90" />
                <p className="text-xs font-medium text-white flex-1">{item.q}</p>
              </summary>
              <div className="px-3 pb-3 pl-10">
                <p className="text-xs text-zinc-400 leading-relaxed">{item.a}</p>
              </div>
            </details>
          ))}
        </div>
      </Section>

      {/* Contact / CTA */}
      <Section title="Get Started" subtitle="Book a demo, join the developer waitlist, or talk to enterprise sales" icon={Mail} color="bg-violet-500/15" id="contact">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              icon: Eye,
              title: "Book a Demo",
              desc: "30-minute walkthrough of MAARS Command with a product specialist. Best for evaluating fit for your team.",
              cta: "Email to schedule",
              href: "mailto:support.maars@marsgc.net?subject=Demo%20Request%20-%20MAARS%20Command",
              color: "text-violet-300",
              border: "border-violet-500/30",
              bg: "bg-violet-500/10",
            },
            {
              icon: Code,
              title: "Developer Access",
              desc: "Get a maars-sk-* key and start calling 175,609+ models through the OpenAI-compatible gateway today.",
              cta: "Open Developer Portal",
              href: "/developer",
              color: "text-cyan-300",
              border: "border-cyan-500/30",
              bg: "bg-cyan-500/10",
            },
            {
              icon: Briefcase,
              title: "Enterprise Sales",
              desc: "SOC2 roadmap, dedicated VPC, BAA, SLA, custom training, and volume pricing. Deals starting at $50k ARR.",
              cta: "Contact enterprise",
              href: "mailto:enterprise.maars@marsgc.net?subject=Enterprise%20Inquiry%20-%20MAARS%20Command",
              color: "text-amber-300",
              border: "border-amber-500/30",
              bg: "bg-amber-500/10",
            },
          ].map(c => (
            <a key={c.title} href={c.href} target={c.href.startsWith("mailto:") ? "_self" : "_self"} className={`block rounded-xl border ${c.border} ${c.bg} p-4 hover:bg-white/5 transition-colors no-underline`}>
              <div className="flex items-center gap-2 mb-2">
                <c.icon className={`w-5 h-5 ${c.color}`} />
                <p className="text-sm font-bold text-white">{c.title}</p>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed mb-3">{c.desc}</p>
              <p className={`text-xs font-bold ${c.color} flex items-center gap-1`}>
                {c.cta} <ChevronRight className="w-3 h-3" />
              </p>
            </a>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[11px] text-zinc-400">
          <span className="flex items-center gap-1.5"><Mail className="w-3 h-3 text-violet-300" /> support.maars@marsgc.net</span>
          <span className="flex items-center gap-1.5"><Briefcase className="w-3 h-3 text-amber-300" /> enterprise.maars@marsgc.net</span>
          <span className="flex items-center gap-1.5"><Building className="w-3 h-3 text-cyan-300" /> MAARS Global Corporation</span>
          <span className="flex items-center gap-1.5"><Rocket className="w-3 h-3 text-rose-300" /> Est. 2026</span>
        </div>
      </Section>

      {/* Footer */}
      <div className="text-center py-6 border-t border-white/5">
        <p className="text-xs text-zinc-400">MAARS Command v1.0 -- Autonomous AI Enterprise Operating System</p>
        <p className="text-[10px] text-zinc-500 mt-1">{agents.length || 458}+ Agents | {uniqueNetworks || 28} Networks | {SYSTEMS.length} Core Systems | 33 Providers | 600+ Models | 58,422 Skills | 522+ Endpoints</p>
        <p className="text-[10px] text-zinc-500 mt-1">Built by MAARS Global Corporation | Est. 2026</p>
        <p className="text-[10px] text-zinc-500 mt-0.5">Contact: support.maars@marsgc.net</p>
      </div>
    </div>
  );
};

export default AboutPage;
