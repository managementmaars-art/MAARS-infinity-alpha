import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import {
  Rocket, Bot, Brain, Shield, Sparkles, Cpu, Activity, Radio, Code, Palette,
  PenTool, Gauge, Users, FileCheck, Zap, Mail, BarChart3, ChevronDown,
  ChevronRight, Globe, Lock, Eye, Target, Layers, Network, Server, Database,
  Download, Mic, FileCode, Archive, Terminal, Search, Heart,
  Wrench, MessageSquare, RefreshCw, Briefcase, Building, TrendingUp,
  CheckCircle, Package, DollarSign, Printer, Share2, Key
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
    desc: "MAARS Command has access to 600+ different AI models from 29 companies via the MAARS Universal API Gateway. The Smart Router classifies your prompt's task type (code, math, reasoning, creative, translation, research, etc.) and your current credit balance, then automatically picks the ideal model. Easy chats go to blazing-fast Groq or Cerebras. Complex reasoning goes to O4-mini or DeepSeek R1. Research goes to Perplexity Deep Research first. Developers get a maars-sk-* key and can call any model through a single OpenAI-compatible endpoint at /developer.",
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

const COST_DATA = [
  { name: "OpenAI", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "GPT-5", input: "$2.50", output: "$10.00" },
    { name: "GPT-4o", input: "$2.50", output: "$10.00" },
    { name: "GPT-4o Mini", input: "$0.15", output: "$0.60" },
    { name: "O3", input: "$10.00", output: "$40.00" },
    { name: "O3 Mini", input: "$1.10", output: "$4.40" },
    { name: "GPT Image 1", input: "$0.02/image", output: "1024x1024 px" },
    { name: "Sora 2 Video", input: "$0.10/second", output: "4-12 sec video" },
  ]},
  { name: "Anthropic", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Claude Sonnet 4.5", input: "$3.00", output: "$15.00" },
    { name: "Claude Opus 4.5", input: "$15.00", output: "$75.00" },
    { name: "Claude Haiku 4.5", input: "$0.80", output: "$4.00" },
  ]},
  { name: "Google Gemini", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Gemini 3 Flash", input: "$0.075", output: "$0.30" },
    { name: "Gemini 3 Pro", input: "$1.25", output: "$5.00" },
    { name: "Nano Banana 2", input: "$0.02/image", output: "1024x1024 px" },
  ]},
  { name: "xAI (Grok)", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Grok-4", input: "$3.00", output: "$15.00" },
    { name: "Grok-4 Fast", input: "$1.50", output: "$6.00" },
    { name: "Grok-3", input: "$3.00", output: "$15.00" },
    { name: "Grok-3 Mini", input: "$0.30", output: "$0.50" },
  ]},
  { name: "DeepSeek", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "DeepSeek Chat", input: "$0.14", output: "$0.28" },
    { name: "DeepSeek Reasoner", input: "$0.55", output: "$2.19" },
  ]},
  { name: "Mistral AI", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Mistral Large", input: "$2.00", output: "$6.00" },
    { name: "Mistral Medium", input: "$0.40", output: "$2.00" },
    { name: "Mistral Small", input: "$0.10", output: "$0.30" },
  ]},
  { name: "Perplexity", unit: "Price per 1 million tokens + $5 per 1,000 web searches", models: [
    { name: "Sonar", input: "$1.00", output: "$1.00" },
    { name: "Sonar Pro", input: "$3.00", output: "$15.00" },
  ]},
  { name: "Cohere", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Command R+", input: "$2.50", output: "$10.00" },
    { name: "Command R", input: "$0.15", output: "$0.60" },
  ]},
  { name: "Groq (Llama 4)", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Llama 4 Scout", input: "$0.11", output: "$0.34" },
    { name: "Llama 4 Maverick", input: "$0.50", output: "$0.77" },
    { name: "Llama 3.3 70B", input: "$0.59", output: "$0.79" },
  ]},
  { name: "Together AI", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Llama 4 Mav. FP8", input: "$0.27", output: "$0.85" },
    { name: "Llama 3.3 70B Turbo", input: "$0.88", output: "$0.88" },
    { name: "DeepSeek R1", input: "$3.00", output: "$7.00" },
  ]},
  { name: "Fireworks AI", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Llama 4 Scout", input: "$0.15", output: "$0.60" },
    { name: "Llama 4 Maverick", input: "$0.50", output: "$0.77" },
    { name: "DeepSeek V3", input: "$0.56", output: "$1.68" },
  ]},
  { name: "AI21 (Jamba)", unit: "Price per 1 million words (tokens) processed", models: [
    { name: "Jamba Large 1.7", input: "$2.00", output: "$8.00" },
    { name: "Jamba Mini 1.7", input: "$0.20", output: "$0.40" },
  ]},
  { name: "Cerebras", unit: "Price per 1 million tokens (one of the cheapest anywhere)", models: [
    { name: "Llama 3.3 70B", input: "$0.60", output: "$0.60" },
    { name: "Llama 3.1 70B", input: "$0.60", output: "$0.60" },
    { name: "Qwen 3-32B", input: "$0.40", output: "$0.40" },
  ]},
  { name: "SambaNova", unit: "Price per 1 million tokens", models: [
    { name: "Llama 4 Maverick", input: "$0.50", output: "$1.50" },
    { name: "DeepSeek R1-0528", input: "$1.30", output: "$1.30" },
    { name: "Qwen 2.5 72B", input: "$0.70", output: "$0.70" },
  ]},
  { name: "Novita AI", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Llama 4 Maverick", input: "$0.27", output: "$0.85" },
    { name: "Qwen 3 235B", input: "$0.22", output: "$0.88" },
    { name: "DeepSeek R1", input: "$0.55", output: "$2.19" },
  ]},
  { name: "Lepton AI", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Llama 4 Maverick", input: "$0.27", output: "$0.85" },
    { name: "DeepSeek R1-0528", input: "$0.55", output: "$2.19" },
  ]},
  { name: "Lambda Labs", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Hermes 3 405B", input: "$0.80", output: "$0.80" },
    { name: "Llama 4 Scout", input: "$0.18", output: "$0.59" },
  ]},
  { name: "Minimax AI", unit: "Price per 1 million tokens (USD)", models: [
    { name: "MiniMax Text-01", input: "$0.20", output: "$1.10" },
    { name: "MiniMax VL-01", input: "$0.20", output: "$1.10" },
  ]},
  { name: "Inception AI", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Mercury Coder Small", input: "$0.25", output: "$1.00" },
    { name: "Mercury Coder Large", input: "$0.50", output: "$2.00" },
  ]},
  { name: "Arcee AI", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Arcee Maestro", input: "$1.20", output: "$5.00" },
    { name: "Arcee Blaze", input: "$0.50", output: "$1.50" },
  ]},
  { name: "Amazon Bedrock", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Nova Pro", input: "$0.80", output: "$3.20" },
    { name: "Nova Lite", input: "$0.06", output: "$0.24" },
    { name: "Nova Micro", input: "$0.035", output: "$0.14" },
  ]},
  { name: "Nvidia NIM", unit: "Price per 1 million tokens on Nvidia infrastructure", models: [
    { name: "Nemotron Ultra 253B", input: "$1.90", output: "$1.90" },
    { name: "Nemotron Super 49B", input: "$0.35", output: "$0.35" },
    { name: "Llama 3.3 70B", input: "$0.60", output: "$0.60" },
  ]},
  { name: "Moonshot AI (Kimi)", unit: "Price per 1 million tokens (USD equivalent)", models: [
    { name: "Kimi 128K", input: "$0.73", output: "$0.73" },
    { name: "Kimi 32K", input: "$0.44", output: "$0.44" },
    { name: "Kimi 8K", input: "$0.18", output: "$0.18" },
  ]},
  { name: "Qwen / Alibaba", unit: "Price per 1 million tokens (DashScope API)", models: [
    { name: "Qwen Max", input: "$6.00", output: "$6.00" },
    { name: "Qwen Plus", input: "$0.80", output: "$0.80" },
    { name: "Qwen Turbo", input: "$0.15", output: "$0.15" },
    { name: "QwQ-32B", input: "$0.34", output: "$0.34" },
  ]},
  { name: "01.AI / Yi", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Yi Lightning", input: "$0.14", output: "$0.14" },
    { name: "Yi Large FC", input: "$3.00", output: "$3.00" },
    { name: "Yi Medium 200K", input: "$12.00", output: "$12.00" },
  ]},
  { name: "Zhipu AI (GLM)", unit: "Price per 1 million tokens (USD)", models: [
    { name: "GLM-4-Plus", input: "$7.00", output: "$7.00" },
    { name: "GLM-4-Air", input: "$0.13", output: "$0.13" },
    { name: "GLM-Z1-Air", input: "$0.13", output: "$0.13" },
  ]},
  { name: "ByteDance Doubao", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Doubao Pro 128K", input: "$0.80", output: "$0.80" },
    { name: "Doubao Lite 32K", input: "$0.04", output: "$0.04" },
  ]},
  { name: "Hyperbolic", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Llama 3.1 405B", input: "$2.00", output: "$2.00" },
    { name: "DeepSeek-R1", input: "$0.50", output: "$2.18" },
    { name: "Llama 3.3 70B", input: "$0.40", output: "$0.40" },
  ]},
  { name: "Upstage Solar", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Solar Pro", input: "$9.00", output: "$9.00" },
    { name: "Solar Mini", input: "$0.29", output: "$0.29" },
  ]},
  { name: "Writer Palmyra", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Palmyra X 004", input: "$0.50", output: "$2.50" },
    { name: "Palmyra Med", input: "$0.80", output: "$4.00" },
    { name: "Palmyra Fin", input: "$0.80", output: "$4.00" },
  ]},
  { name: "Meta Llama API", unit: "Price per 1 million tokens (USD)", models: [
    { name: "Llama 4 Scout", input: "$0.18", output: "$0.59" },
    { name: "Llama 4 Maverick", input: "$0.27", output: "$0.85" },
    { name: "Llama 3.3 70B", input: "$0.59", output: "$0.79" },
  ]},
  { name: "ElevenLabs Voice", unit: "Price per 1,000 characters of text spoken", models: [
    { name: "Multilingual v2", input: "$0.30/1K chars", output: "Audio file" },
    { name: "Turbo v2.5", input: "$0.18/1K chars", output: "Fast audio" },
  ]},
  { name: "Google Suite Actions", unit: "Free with your connected Google account", models: [
    { name: "Send Email (Gmail)", input: "Free", output: "Per email sent" },
    { name: "Calendar Event", input: "Free", output: "Per event created" },
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

  /* Print PDF */
  const handlePrint = () => {
    setPrinting(true);
    setExpandedNetworks(new Set(sortedNetworks.map(([k]) => k)));
    setExpandedSystems(new Set(SYSTEMS.map((_, i) => i)));
    setTimeout(() => { window.print(); setPrinting(false); }, 800);
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
            These agents are organized into <span className="text-emerald-400 font-medium">{uniqueNetworks || 27} specialized network categories</span> (like departments in a company).
            They're powered by <span className="text-amber-400 font-medium">33 AI providers with 175,609+ models</span> (GPT-5, Claude Opus 4.6, Gemini 2.5, Grok-4, DeepSeek R1, Mistral, Perplexity, Groq, Cerebras, SambaNova, and more).
            The system automatically picks the right AI model for each task, controls costs, ensures quality, and even lets agents collaborate with each other -- all without you lifting a finger.
          </p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {["Multi-Agent Orchestration","Quality Control","Smart Model Router","Developer API Gateway","600+ Models · 33 Providers","Content Generation","App Builder","Memory System","Voice Commands","Code Explorer","Knowledge Graph","Workflow Builder","Campaign Builder","Integration Hub","Team Builder","Trust Analytics","Real-World Actions","Command Palette"].map((b, i) => {
            const colors = ["indigo","emerald","amber","pink","cyan","violet","rose","sky","blue","teal","orange","red","green","purple","lime","yellow"];
            return <span key={b} className={`bg-${colors[i % colors.length]}-500/20 text-${colors[i % colors.length]}-400`} style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 20, display: "inline-block" }}>{b}</span>;
          })}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-6 gap-3 print-stats-row">
        {[
          { label: "AI Agents", value: `${agents.length || "458"}+`, color: "text-indigo-400", sub: "Specialized workers" },
          { label: "Networks", value: uniqueNetworks || 27, color: "text-emerald-400", sub: "Team categories" },
          { label: "Core Systems", value: SYSTEMS.length, color: "text-amber-400", sub: "Built-in tools" },
          { label: "LLM Providers", value: "29", color: "text-violet-400", sub: "AI companies" },
          { label: "AI Models", value: "600+", color: "text-cyan-400", sub: "Via gateway" },
          { label: "API Endpoints", value: "212+", color: "text-rose-400", sub: "Connection points" },
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
          {AI_PROVIDERS.map(provider => (
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

      {/* Provider Costs */}
      <Section title="What Each AI Model Costs" subtitle="Reference pricing so you know exactly what you're paying" icon={BarChart3} color="bg-green-500/15" id="costs">
        <p className="text-xs text-zinc-400 mb-4">
          Every time an AI model processes text, generates an image, or creates a video, it costs money. Here's how much each model charges.
          "Input" is what you send to the AI (your question or prompt). "Output" is what the AI sends back (the answer or result).
          Most prices are per 1 million tokens (roughly 750,000 words). Prices come directly from each provider's website and may change.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {COST_DATA.map(provider => (
            <div key={provider.name} className="bg-zinc-900/50 border-white/5 print-card" style={{ borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-white">{provider.name}</span>
                </div>
                <span className="text-[9px] text-zinc-600 block mb-2">{provider.unit}</span>
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
              </div>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-zinc-600 mt-3 italic">* When using the MAARS AI Gateway (which lets you use all providers with one key), there's a small convenience markup over these direct prices.</p>
      </Section>

      {/* Footer */}
      <div className="text-center py-6 border-t border-white/5">
        <p className="text-xs text-zinc-400">MAARS Command v1.0 -- Autonomous AI Enterprise Operating System</p>
        <p className="text-[10px] text-zinc-500 mt-1">{agents.length || 458}+ Agents | {uniqueNetworks || 27} Networks | {SYSTEMS.length} Core Systems | 33 Providers | 600+ Models | 212+ Endpoints</p>
        <p className="text-[10px] text-zinc-500 mt-1">Built by MAARS Global Corporation | Est. 2026</p>
        <p className="text-[10px] text-zinc-500 mt-0.5">Contact: support.maars@marsgc.net</p>
      </div>
    </div>
  );
};

export default AboutPage;
