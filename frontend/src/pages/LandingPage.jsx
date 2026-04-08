import { useState, useRef, useEffect, useMemo, lazy, Suspense } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot, Sparkles, Users, Zap, MessageSquare, BarChart3, ChevronRight, ChevronDown, Menu, X, Terminal, Globe, Code2, Key, ArrowRight } from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import CustomCursor from "../components/CustomCursor";

gsap.registerPlugin(ScrollTrigger);

const NeuralCommandCanvas = lazy(() => import("../components/3d/NeuralCommandCanvas"));

// ─── Palette ─────────────────────────────────────────────────────────────────
const C = {
  bg:     "#030712",
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  glass:  "rgba(255,255,255,0.04)",
  border: "rgba(255,255,255,0.08)",
};

// ─── Shared micro-components ──────────────────────────────────────────────────
const GlassCard = ({ children, style, className = "", hover = true }) => (
  <div
    className={`relative rounded-2xl overflow-hidden ${hover ? "group transition-all duration-300 hover:border-white/20 hover:-translate-y-1" : ""} ${className}`}
    style={{
      background: C.glass,
      border: `1px solid ${C.border}`,
      backdropFilter: "blur(12px)",
      ...style,
    }}
  >
    {children}
  </div>
);

const GlowBadge = ({ children, color = "teal" }) => (
  <span
    className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full tracking-wide"
    style={{
      background: color === "teal" ? "rgba(79,209,197,0.12)" : "rgba(124,58,237,0.15)",
      border: `1px solid ${color === "teal" ? "rgba(79,209,197,0.3)" : "rgba(124,58,237,0.35)"}`,
      color: color === "teal" ? C.teal : "#a78bfa",
    }}
  >
    {children}
  </span>
);

const SectionLabel = ({ children }) => (
  <div className="flex items-center gap-3 mb-4">
    <span className="block w-8 h-px" style={{ background: C.teal }} />
    <span className="text-xs font-bold tracking-[0.2em] uppercase" style={{ color: C.teal }}>{children}</span>
  </div>
);

// ─── Data ─────────────────────────────────────────────────────────────────────
// Professional suited CDN portraits — same source as backend config
const EA = "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/";

// Role → accent colour
const roleAccent = (role = "", isCommander = false) => {
  if (isCommander) return "#f59e0b";
  const r = role.toLowerCase();
  if (/analyst|data|research/i.test(r))               return "#4fd1c5";
  if (/creative|writer|content|copy|design|brand/i.test(r)) return "#a78bfa";
  if (/developer|engineer|technical|code/i.test(r))   return "#60a5fa";
  if (/market|growth|seo|social|pr|campaign/i.test(r))return "#f472b6";
  if (/finance|revenue|investor/i.test(r))             return "#fbbf24";
  if (/legal|compliance|govern/i.test(r))              return "#94a3b8";
  if (/hr|recruit|operat|manag|project/i.test(r))      return "#34d399";
  if (/security|cyber/i.test(r))                       return "#f87171";
  return "#4fd1c5";
};

const agents = [
  { name: "Commander Orion",      role: "AI Commander",              avatar: EA+"9a3eb3186a873a3337de51d37d80e0dac2da6db7ef21b2bef016307c59557b27.png", capabilities: ["Task Delegation", "Strategy", "Orchestration"], isCommander: true },
  { name: "Nadia Kessler",        role: "Personal Secretary",        avatar: EA+"4e2850c614aa1c3711c4417f5358bd28b1b5c24bfa75abb3a1361b1fed079c60.png", capabilities: ["Scheduling", "To-Do Lists", "Email Drafting"] },
  { name: "Zara Mitchell",        role: "Marketing Specialist",      avatar: EA+"fb16f517812221326ad131382b9b06c3965961e251319d278f27e132382cbe59.png", capabilities: ["Social Media", "Ad Copy", "Campaigns"] },
  { name: "Victor Ashford",       role: "Business Strategist",       avatar: EA+"5f057725298a1552ecc39a3c3de30b2068e94d77888fa433b28a81c254d6f366.png", capabilities: ["Strategy", "Market Research", "Analysis"] },
  { name: "Luna Bergström",       role: "Web Designer",              avatar: EA+"18df20edd8fea63dd3f42bf6aa110307b55e1a46e57426bf4930c29c635857bf.png", capabilities: ["UI/UX", "Landing Pages", "Branding"] },
  { name: "Kai Nakamoto",         role: "App Developer",             avatar: EA+"d61615bbb8ef939f24f083d0a30a5df23a49ea6ec19c4bb3032a7f594661effb.png", capabilities: ["Web Apps", "Mobile Apps", "Full-Stack"] },
  { name: "Scarlett Monroe",      role: "Copywriter",                avatar: EA+"9ebf04f46ebf0f541e00c1afa6a6cf2f60e5ff38caafaf777131b1dbb5631a51.png", capabilities: ["Blog Posts", "Ad Copy", "Scripts"] },
  { name: "Derek Huang",          role: "SEO Specialist",            avatar: EA+"f1478028a00b7568b29d851ee148d74298c984c0c84412512fafe6acecb79e68.png", capabilities: ["Keywords", "Technical SEO", "Analytics"] },
  { name: "Marcus Drake",         role: "Sales Representative",      avatar: EA+"f58dec61c7d57ae195e889db7f107160c013b6ca4f61bee75266edc8139e6f65.png", capabilities: ["Outreach", "Proposals", "CRM"] },
  { name: "Isla Fernandez",       role: "Social Media Manager",      avatar: EA+"798f2bed9ad1f212875416e9f21ba960580048aeb210cb9efbde8bbc365f0a00.png", capabilities: ["Content Strategy", "Engagement", "Analytics"] },
  { name: "Ethan Yates",          role: "Data Analyst",              avatar: EA+"334c45614287e640d642e44c8e4f0c8838e0813105f170db17a003c0ac47802f.png", capabilities: ["Data Viz", "Reports", "SQL"] },
  { name: "Olivia Sinclair",      role: "Content Writer",            avatar: EA+"6514b7a797d37d1e04470bfd5ec62dda493f71bbf1187da2dfc669ac4dea8984.png", capabilities: ["Articles", "Stories", "Editing"] },
  { name: "Maya Thompson",        role: "Customer Service Rep",      avatar: EA+"f06e5db223fc3ae402cb2fa11a430f404a64bec41c6252e9da47814aed1a8997.png", capabilities: ["Support", "FAQ", "Tickets"] },
  { name: "Nathan Cross",         role: "Project Manager",           avatar: EA+"54fe8dafe0ffded87354be24fafd0ff2bbbebd2699b7671751bf16b64cbcd39d.png", capabilities: ["Agile", "Planning", "Timelines"] },
  { name: "Dr. Clara Voss",       role: "Research Specialist",       avatar: EA+"cf71c32849d1c29539e9bcc6673d483b4db0eb98f4ed89f3f8000bc5d23da801.png", capabilities: ["Papers", "Analysis", "Citations"] },
  { name: "Benjamin Cole",        role: "Financial Analyst",         avatar: EA+"6e0f47d6af19122133c6cc631c515a0de5493bd5976d95aea6f02e408e755931.png", capabilities: ["Forecasting", "Budgets", "Reports"] },
  { name: "Amara Johnson",        role: "HR Specialist",             avatar: EA+"ee7890378b0a54d85529a56bda988190c24693d702ff2ef004584cb89e8fe4ce.png", capabilities: ["Recruiting", "Policies", "Onboarding"] },
  { name: "Felix Romano",         role: "Graphic Designer",          avatar: EA+"87f5df94dac8449fe045a0c876b50224b7c9dec0cecc9ad5ca49b3991efcfba0.png", capabilities: ["Logos", "Illustrations", "Branding"] },
  { name: "Alexandra Reid",       role: "Legal Assistant",           avatar: EA+"605e790242497984c3777d551af763849dc85b7c107cf6ca42b8bc399ebd63d8.png", capabilities: ["Contracts", "Compliance", "Legal Docs"] },
  { name: "Jasper Wells",         role: "Email Marketing",           avatar: EA+"d4091ddd69e0491820ee6a99bd6f186b74645e03de5037599d7d836a5e465c18.png", capabilities: ["Campaigns", "Newsletters", "A/B Testing"] },
  { name: "Riley Chen",           role: "Video Content",             avatar: EA+"2aaa884e525d1bb1afb68a429016993c0a24b4764a3c455022690c05c151b070.png", capabilities: ["Scripts", "Storyboards", "Editing"] },
  { name: "Damien Voss",          role: "Cybersecurity Officer",     avatar: EA+"7eb081231afdea773949d6946afd7a1bbae48d272b14f772a7627f7b90e83ba1.png", capabilities: ["Security Audits", "Threat Analysis", "Compliance"] },
  { name: "Serena Okafor",        role: "Automation Engineer",       avatar: EA+"181e17ed139f7030802f0c3ae0801ea69b15f780828b07cc8329a77b03b42bea.png", capabilities: ["Workflows", "Integrations", "Automation"] },
  { name: "Axel Brennan",         role: "Growth Hacker",             avatar: EA+"9f40cce8b43dc4c59cb24cc91e4b666fefe90ce2e51ade93e45680337e63c643.png", capabilities: ["Growth Experiments", "A/B Testing", "Funnels"] },
  { name: "Victoria Harrington",  role: "Compliance Officer",        avatar: EA+"23f2f01a9c55a73c9e199bce775bc74541dc0311694e5fd12987682886041616.png", capabilities: ["Regulatory", "Audits", "GDPR"] },
  { name: "Dr. Luca Bernstein",   role: "AI Optimizer",              avatar: EA+"d888a9a6ab8bd8a3afe850ddbf31e706fc38e011b454a3e8acf4a8ebe0e9f165.png", capabilities: ["AI Tuning", "Cost Reduction", "Prompts"] },
  { name: "Diana Morales",        role: "Operations Manager",        avatar: EA+"d974fde36e8b923670637ccaa3babac5b46cc28fade0c0033c96ba86b4d66091.png", capabilities: ["Process", "Supply Chain", "KPIs"] },
  { name: "Maximilian Wolfe",     role: "Revenue Strategist",        avatar: EA+"707cf99fa483834d42b8825e48537bbd3351e4e3f465e88bdd0c577d54e6b92c.png", capabilities: ["Pricing", "Revenue Models", "Monetization"] },
  { name: "Cassandra Steele",     role: "Chief Strategy Officer",    avatar: EA+"e5ef1d410dcd7e499baa4089564365be54806a20a1946170f4a53d7b43e976a4.png", capabilities: ["Corporate Strategy", "Market Expansion", "OKRs"] },
  { name: "Richard Ashworth",     role: "Investor Relations",        avatar: EA+"da0d3b9c51198fe0df21bc3c98f064839f81dea915c88e590cf7b8d9380dd8c2.png", capabilities: ["Pitch Decks", "Fundraising", "Valuations"] },
  { name: "Elena Kovacs",         role: "Product Manager",           avatar: EA+"3de9f03d7891c8833bf377ba7f45efad1b78b195066710674ef4d8ea83a3bce1.png", capabilities: ["Roadmaps", "User Stories", "Sprints"] },
  { name: "Nikolai Volkov",       role: "Data Engineer",             avatar: EA+"c565764f7f90fc78fc100d2f4b4ff43c8baf755ace694139c1c54ee96a0429e4.png", capabilities: ["Pipelines", "ETL", "Databases"] },
  { name: "Valentina Cruz",       role: "Brand Architect",           avatar: EA+"19d90fd5dc3ea2d4ce4d9916762a4ebead00fdfdad82397a879c59099a3d516f.png", capabilities: ["Brand Identity", "Guidelines", "Visual Systems"] },
  { name: "Yuki Tanaka",          role: "UX Researcher",             avatar: EA+"db0fa9edc51497eef8627fe55936a764657127f3627fff193b6a09571c8885bb.png", capabilities: ["User Research", "Usability", "Personas"] },
  { name: "Marco De Luca",        role: "3D Specialist",             avatar: EA+"8ec4b4a27946e20891cca2de789d559338c6ab2f18a63b0ecebfa6eaa013fd8a.png", capabilities: ["3D Rendering", "Motion Graphics", "AR/VR"] },
  { name: "Catherine Blake",      role: "PR Manager",                avatar: EA+"706aaf93ddbb0793256c82bd6389048070877ee8dee4e69b64b4abb02d8420c8.png", capabilities: ["PR Strategy", "Crisis Mgmt", "Media"] },
  { name: "Adrian Stone",         role: "Procurement Manager",       avatar: EA+"84eae30d456323c117055f6217e22dead13c792020daf9019af55c745f44a344.png", capabilities: ["Vendor Mgmt", "Contracts", "Supply Chain"] },
  { name: "Sofia Reyes",          role: "CX Architect",              avatar: EA+"c2715d85ace40876df7f859d06f00275e4a34ca06d90436090bfd9569e6c6b24.png", capabilities: ["Journey Maps", "Loyalty", "NPS"] },
  { name: "Prof. James Whitfield",role: "Ethics Officer",            avatar: EA+"5ab58f9fabff5a03e86596e12c555d71e72d4821271702c03f48eddc4cbef804.png", capabilities: ["Ethics", "Risk", "Governance"] },
  { name: "Dr. Eleanor Shaw",     role: "Knowledge Architect",       avatar: EA+"ea78ac11ca9f7675017f9311b0f4dcc70a5fb2f4344f8701aceab4b9dc242718.png", capabilities: ["Knowledge Mgmt", "Documentation", "Taxonomies"] },
  { name: "Layla Mansouri",       role: "Localization Specialist",   avatar: EA+"d4c51d4c86045d6d0d1d9dccec55d81792f448d8734452de56f90e029c602ed5.png", capabilities: ["Localization", "Translation", "Global Markets"] },
];

const features = [
  { icon: Bot, title: "458+ Specialized AI Agents", desc: "Pre-built expert agents across 27 networks — engineering, finance, legal, creative, and more.", accent: C.teal },
  { icon: Sparkles, title: "175,000+ AI Models", desc: "609 curated models + all of HuggingFace's open-source catalogue via universal pass-through.", accent: "#a78bfa" },
  { icon: Users, title: "Agent Collaboration", desc: "Multiple agents working in concert across 27 specialized networks to tackle complex goals.", accent: C.blue },
  { icon: MessageSquare, title: "Chat with Any Agent", desc: "Natural conversation with 458+ context-aware AI agents, each with unique expertise and tools.", accent: C.teal },
  { icon: BarChart3, title: "Trust Scores & Governance", desc: "Every action governed, metered, and audited. Agent trust scores built from live execution history.", accent: "#a78bfa" },
  { icon: Zap, title: "One Key. All Providers.", desc: "Single OpenAI-compatible endpoint for all 33 providers. Drop-in replace base_url and you're done.", accent: C.blue },
];

const stats = [
  { value: "458+", label: "AI Agents" },
  { value: "27", label: "Agent Networks" },
  { value: "33", label: "LLM Providers" },
  { value: "609+", label: "Curated Models" },
  { value: "175k+", label: "HF Pass-through" },
  { value: "1", label: "Universal Key" },
];

const providers = [
  { name: "OpenAI", color: "#10b981", models: [
    { name: "GPT-5", tag: "Flagship" }, { name: "GPT-4o", tag: "Fast" }, { name: "O3", tag: "Reasoning" },
  ]},
  { name: "Anthropic", color: "#f97316", models: [
    { name: "Claude Opus 4.6", tag: "Premium" }, { name: "Claude Sonnet 4.6", tag: "Flagship" },
  ]},
  { name: "Google", color: "#3b82f6", models: [
    { name: "Gemini 3 Flash", tag: "Fast" }, { name: "Gemini 3 Pro", tag: "Flagship" },
  ]},
  { name: "xAI (Grok)", color: "#6b7280", models: [
    { name: "Grok 4", tag: "Flagship" }, { name: "Grok 3 Mini", tag: "Economy" },
  ]},
  { name: "DeepSeek", color: C.teal, models: [
    { name: "DeepSeek Chat", tag: "Economy" }, { name: "DeepSeek Reasoner", tag: "Reasoning" },
  ]},
  { name: "Mistral AI", color: "#8b5cf6", models: [
    { name: "Mistral Large", tag: "Flagship" }, { name: "Mistral Small", tag: "Economy" },
  ]},
  { name: "Groq + Cerebras", color: "#eab308", models: [
    { name: "Llama 4 Maverick", tag: "Ultra-Fast" }, { name: "QwQ-32B", tag: "Reasoning" },
  ]},
  { name: "Together AI", color: "#22c55e", models: [
    { name: "Llama 4 Maverick FP8", tag: "Fast" }, { name: "Qwen 3 235B", tag: "Flagship" },
  ]},
  { name: "NVIDIA", color: "#76c442", models: [
    { name: "Nemotron Ultra 253B", tag: "Premium" }, { name: "Nemotron Super 49B", tag: "Fast" },
  ]},
  { name: "SambaNova", color: "#f43f5e", models: [
    { name: "DeepSeek R1-0528", tag: "Reasoning" }, { name: "Llama 4 Maverick", tag: "Fast" },
  ]},
  { name: "Perplexity", color: C.teal, models: [
    { name: "Sonar Pro", tag: "Research" }, { name: "Sonar", tag: "Search" },
  ]},
  { name: "Cohere", color: "#ec4899", models: [
    { name: "Command R+", tag: "Flagship" }, { name: "Command R", tag: "Economy" },
  ]},
  { name: "Amazon Bedrock", color: "#f97316", models: [
    { name: "Nova Pro", tag: "Flagship" }, { name: "Nova Lite", tag: "Fast" },
  ]},
  { name: "HuggingFace", color: "#eab308", models: [
    { name: "huggingface/{any}", tag: "Pass-Through" }, { name: "175,000+ Models", tag: "Open-Source" },
  ]},
  { name: "Meta Llama API", color: "#60a5fa", models: [
    { name: "Llama 4 Scout", tag: "Fast" }, { name: "Llama 4 Maverick", tag: "Flagship" },
  ]},
  { name: "Moonshot AI", color: "#3b82f6", models: [
    { name: "Kimi 1M Context", tag: "Long-Context" }, { name: "Moonshot v1", tag: "Fast" },
  ]},
  { name: "Qwen / Alibaba", color: "#60a5fa", models: [
    { name: "Qwen Max", tag: "Flagship" }, { name: "Qwen 3 235B", tag: "Open" },
  ]},
  { name: "Yi / 01.AI", color: "#10b981", models: [
    { name: "Yi Lightning", tag: "Fast" }, { name: "Yi Large FC", tag: "Tool-Use" },
  ]},
  { name: "Zhipu AI (GLM)", color: "#3b82f6", models: [
    { name: "GLM-5", tag: "Flagship" }, { name: "CodeGeeX-4", tag: "Code" },
  ]},
  { name: "ByteDance Doubao", color: "#f59e0b", models: [
    { name: "Seed 1.6", tag: "Flagship" }, { name: "Doubao Pro 128K", tag: "Long-Context" },
  ]},
  { name: "Upstage Solar", color: "#eab308", models: [
    { name: "Solar Pro", tag: "Flagship" }, { name: "Solar Mini", tag: "Economy" },
  ]},
  { name: "Writer Palmyra", color: "#a855f7", models: [
    { name: "Palmyra X 004", tag: "Flagship" }, { name: "Palmyra Med", tag: "Medical" },
  ]},
  { name: "Hyperbolic", color: C.teal, models: [
    { name: "Llama 3.1 405B", tag: "Flagship" }, { name: "DeepSeek-R1", tag: "Reasoning" },
  ]},
  { name: "Novita AI", color: "#8b5cf6", models: [
    { name: "Llama 4 Maverick", tag: "Fast" }, { name: "DeepSeek R1", tag: "Reasoning" },
  ]},
  { name: "Lepton AI", color: "#6366f1", models: [
    { name: "Llama 4 Scout", tag: "Economy" }, { name: "Mixtral 8x7B", tag: "Fast" },
  ]},
  { name: "Lambda Labs", color: "#6b7280", models: [
    { name: "Hermes 3 405B", tag: "Flagship" }, { name: "Llama 3.3 70B", tag: "Fast" },
  ]},
  { name: "Minimax", color: "#ec4899", models: [
    { name: "MiniMax Text-01", tag: "Flagship" }, { name: "MiniMax-01", tag: "Vision" },
  ]},
  { name: "Inception AI", color: "#06b6d4", models: [
    { name: "Mercury Coder Small", tag: "Code" }, { name: "Mercury Coder Mini", tag: "Fast" },
  ]},
  { name: "Arcee AI", color: "#a78bfa", models: [
    { name: "Arcee Maestro", tag: "Reasoning" }, { name: "Arcee Spark", tag: "Fast" },
  ]},
  { name: "AI21 Labs", color: "#6366f1", models: [
    { name: "Jamba Large 1.7", tag: "Flagship" }, { name: "Jamba Mini 1.7", tag: "Fast" },
  ]},
  { name: "Fireworks AI", color: "#f59e0b", models: [
    { name: "Llama 4 Maverick FP8", tag: "Fast" }, { name: "DeepSeek R1", tag: "Reasoning" },
  ]},
  { name: "Hugging Face (Hub)", color: "#eab308", models: [
    { name: "175,000+ models", tag: "Open-Source" },
  ]},
  { name: "ElevenLabs (TTS)", color: "#f43f5e", models: [
    { name: "Multilingual v2", tag: "Voice" }, { name: "Turbo v2.5", tag: "Fast-TTS" },
  ]},
];

// ─── Live activity labels per role keyword ─────────────────────────────────
const ROLE_ACTIVITIES = {
  commander:    ["Coordinating 14 agents…", "Routing new task…", "Strategic planning…", "Delegating to team…", "Monitoring missions…"],
  secretary:    ["Drafting email…", "Scheduling meeting…", "Managing calendar…", "Filing documents…", "Preparing briefing…"],
  marketing:    ["Analyzing campaign data…", "Writing ad copy…", "Running A/B test…", "Building audience…", "Optimizing funnel…"],
  strategist:   ["Mapping competitors…", "Building strategy…", "Market analysis…", "Identifying gaps…", "Forecasting trends…"],
  designer:     ["Refining UI layout…", "Creating wireframes…", "Building component…", "Iterating design…", "Polishing visuals…"],
  developer:    ["Writing clean code…", "Debugging API…", "Deploying update…", "Reviewing PR…", "Optimizing query…"],
  copywriter:   ["Crafting headline…", "Writing blog draft…", "Polishing script…", "SEO-optimizing…", "Editing final copy…"],
  seo:          ["Keyword research…", "Fixing broken links…", "Audit in progress…", "Rank tracking…", "Content gap analysis…"],
  sales:        ["Writing proposal…", "Following up lead…", "CRM update…", "Booking demo…", "Qualifying prospect…"],
  social:       ["Scheduling posts…", "Drafting captions…", "Trend analysis…", "Engagement review…", "Building content calendar…"],
  analyst:      ["Running SQL query…", "Building report…", "Cleaning dataset…", "Forecasting model…", "Visualizing data…"],
  writer:       ["Writing article…", "Editing draft…", "Research phase…", "Structuring narrative…", "Final proofread…"],
  support:      ["Resolving ticket…", "Writing FAQ…", "Updating KB…", "Escalating issue…", "Following up…"],
  manager:      ["Updating roadmap…", "Sprint planning…", "Risk assessment…", "Stakeholder update…", "Timeline review…"],
  research:     ["Reading papers…", "Summarizing findings…", "Citation check…", "Hypothesis testing…", "Literature review…"],
  finance:      ["Building forecast…", "Budget analysis…", "P&L review…", "Cash flow model…", "Risk calculation…"],
  hr:           ["Screening resume…", "Writing JD…", "Onboarding check…", "Policy update…", "Culture assessment…"],
  graphic:      ["Designing logo…", "Layout iteration…", "Color palette…", "Exporting assets…", "Brand refresh…"],
  legal:        ["Reviewing contract…", "Compliance check…", "NDA drafting…", "Risk audit…", "Policy update…"],
  email:        ["Campaign setup…", "A/B subject test…", "List segmentation…", "Deliverability check…", "Flow optimization…"],
  video:        ["Writing script…", "Storyboarding…", "Scene planning…", "Review notes…", "Export ready…"],
  security:     ["Threat scanning…", "Audit in progress…", "Patch analysis…", "Zero-day check…", "Risk scoring…"],
  automation:   ["Building workflow…", "Testing trigger…", "Integration sync…", "Mapping API…", "Flow deployed…"],
  growth:       ["Funnel analysis…", "Experiment design…", "Metric review…", "Hypothesis testing…", "Scaling winner…"],
  compliance:   ["Regulatory scan…", "GDPR audit…", "Policy drafting…", "Risk matrix…", "Compliance report…"],
  ai:           ["Tuning prompts…", "Cost optimization…", "Benchmarking…", "Provider test…", "Latency analysis…"],
  operations:   ["Process mapping…", "KPI review…", "Supply audit…", "Bottleneck fix…", "OKR update…"],
  revenue:      ["Pricing model…", "Revenue forecast…", "Monetization plan…", "Upsell strategy…", "Conversion review…"],
  strategy:     ["OKR planning…", "Market expansion…", "Competitive move…", "Board deck prep…", "Vision alignment…"],
  investor:     ["Pitch deck…", "Valuation model…", "Fundraise outreach…", "Due diligence…", "Cap table review…"],
  product:      ["Roadmap update…", "User story sprint…", "Feature scope…", "Backlog grooming…", "Release planning…"],
  data:         ["ETL pipeline…", "Schema design…", "Query tuning…", "Data migration…", "Warehouse sync…"],
  brand:        ["Identity system…", "Brand guidelines…", "Visual audit…", "Tone of voice…", "Asset library…"],
  ux:           ["User interview…", "Usability test…", "Journey mapping…", "Persona update…", "Prototype review…"],
  "3d":         ["3D render…", "Motion graphics…", "Scene lighting…", "Asset texturing…", "AR export…"],
  pr:           ["Press release…", "Media outreach…", "Crisis prep…", "Journalist pitch…", "Coverage tracking…"],
  procurement:  ["Vendor eval…", "Contract terms…", "Supply review…", "Cost negotiation…", "PO processing…"],
  cx:           ["Journey mapping…", "NPS analysis…", "Loyalty program…", "Touchpoint audit…", "CSAT review…"],
  ethics:       ["Ethics review…", "Risk assessment…", "Governance audit…", "Policy drafting…", "Bias check…"],
  knowledge:    ["Building taxonomy…", "Docs update…", "Knowledge graph…", "Wiki structuring…", "Gap analysis…"],
  localization: ["Translating content…", "Regional review…", "Locale testing…", "Glossary update…", "Cultural check…"],
};

function getActivity(role = "") {
  const r = role.toLowerCase();
  for (const [key, acts] of Object.entries(ROLE_ACTIVITIES)) {
    if (r.includes(key)) return acts;
  }
  return ["Processing request…", "Analyzing data…", "Thinking…"];
}

// ─── Live activity ticker ──────────────────────────────────────────────────
function ActivityTicker({ role, accent, delay = 0 }) {
  const activities = useMemo(() => getActivity(role), [role]);
  const [idx, setIdx] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const init = setTimeout(() => {
      const interval = setInterval(() => {
        setVisible(false);
        setTimeout(() => { setIdx(i => (i + 1) % activities.length); setVisible(true); }, 350);
      }, 3200 + delay * 400);
      return () => clearInterval(interval);
    }, delay * 600);
    return () => clearTimeout(init);
  }, [activities, delay]);

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 6,
      height: 18, overflow: "hidden",
    }}>
      {/* Waveform bars */}
      <div style={{ display: "flex", alignItems: "center", gap: 1.5, flexShrink: 0 }}>
        {[1,2,3,4,5].map(n => (
          <div key={n} style={{
            width: 2, borderRadius: 2,
            background: accent, opacity: 0.8,
            animation: `ac_wave_${n} ${0.7 + n * 0.12}s ease-in-out ${n * 0.1}s infinite`,
          }} />
        ))}
      </div>
      <span style={{
        fontSize: 10, color: accent, fontWeight: 600,
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(4px)",
        transition: "opacity 0.3s ease, transform 0.3s ease",
        whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: 160,
      }}>
        {activities[idx]}
      </span>
    </div>
  );
}

// ─── AgentCarousel ────────────────────────────────────────────────────────────
function AgentCarousel({ agents, navigate }) {
  const trackRef    = useRef(null);
  const [canLeft,   setCanLeft]  = useState(false);
  const [canRight,  setCanRight] = useState(true);
  const [dragging,  setDragging] = useState(false);
  const [paused,    setPaused]   = useState(false);
  const dragStart   = useRef({ x: 0, sl: 0 });
  const autoRef     = useRef(null);

  const CARD_W  = 240;
  const GAP     = 20;
  const STEP    = (CARD_W + GAP) * 3;

  const updateArrows = () => {
    const el = trackRef.current;
    if (!el) return;
    setCanLeft(el.scrollLeft > 4);
    setCanRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 4);
  };

  const scrollBy = (dir) => trackRef.current?.scrollBy({ left: dir * STEP, behavior: "smooth" });

  // Drag-to-scroll
  const onMouseDown = (e) => {
    setDragging(true);
    dragStart.current = { x: e.clientX, sl: trackRef.current?.scrollLeft || 0 };
    e.preventDefault();
  };
  const onMouseMove = (e) => {
    if (!dragging) return;
    const dx = e.clientX - dragStart.current.x;
    if (trackRef.current) trackRef.current.scrollLeft = dragStart.current.sl - dx;
    updateArrows();
  };
  const onMouseUp = () => setDragging(false);

  // Auto-scroll (slow creep)
  useEffect(() => {
    if (paused) { clearInterval(autoRef.current); return; }
    autoRef.current = setInterval(() => {
      const el = trackRef.current;
      if (!el) return;
      if (el.scrollLeft >= el.scrollWidth - el.clientWidth - 4) {
        el.scrollTo({ left: 0, behavior: "smooth" });
      } else {
        el.scrollBy({ left: CARD_W + GAP, behavior: "smooth" });
      }
      updateArrows();
    }, 4500);
    return () => clearInterval(autoRef.current);
  }, [paused]);

  return (
    <section id="agents" className="depth-section" style={{ padding: "100px 0", overflow: "hidden", position: "relative" }}>
      <style>{`
        @keyframes lp_card_in    { from{opacity:0;transform:translateY(32px) scale(0.91)} to{opacity:1;transform:translateY(0) scale(1)} }
        @keyframes lp_float_card { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes lp_img_alive  {
          0%,100%{ transform:scale(1.0) translateY(0px);    filter:brightness(1)   saturate(1); }
          40%    { transform:scale(1.04) translateY(-3px);  filter:brightness(1.05) saturate(1.06); }
          70%    { transform:scale(1.02) translateY(-1px);  filter:brightness(1.03) saturate(1.03); }
        }
        @keyframes lp_glow_beat  { 0%,100%{opacity:0.5} 50%{opacity:1.0} }
        @keyframes lp_dot_live   {
          0%,100%{ box-shadow:0 0 0 0 rgba(52,211,153,0.9); }
          60%    { box-shadow:0 0 0 6px rgba(52,211,153,0); }
        }
        @keyframes lp_shimmer    { 0%{transform:translateX(-100%)} 100%{transform:translateX(200%)} }
        @keyframes lp_border_run {
          0%   { background-position: 0%   50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0%   50%; }
        }
        @keyframes ac_wave_1 { 0%,100%{height:2px}  50%{height:10px} }
        @keyframes ac_wave_2 { 0%,100%{height:5px}  50%{height:16px} }
        @keyframes ac_wave_3 { 0%,100%{height:9px}  50%{height:4px}  }
        @keyframes ac_wave_4 { 0%,100%{height:3px}  50%{height:13px} }
        @keyframes ac_wave_5 { 0%,100%{height:7px}  50%{height:3px}  }
        @keyframes lp_scan   { 0%{top:0%;opacity:0} 5%{opacity:0.6} 95%{opacity:0.6} 100%{top:100%;opacity:0} }

        .lp3-track::-webkit-scrollbar { display:none; }
        .lp3-track { scrollbar-width:none; user-select:none; }

        .lp3-card {
          animation: lp_card_in 0.6s cubic-bezier(0.22,1,0.36,1) both;
          transition: box-shadow 0.4s ease, border-color 0.4s ease;
        }
        .lp3-card:hover .lp3-img {
          transform: scale(1.1) translateY(-4px) !important;
          filter: brightness(1.1) saturate(1.12) !important;
        }
        .lp3-img {
          transition: transform 0.7s cubic-bezier(0.22,1,0.36,1), filter 0.7s ease !important;
        }
        .lp3-card:hover .lp3-shimmer { opacity: 1 !important; }
        .lp3-card:hover .lp3-badge   { opacity: 1 !important; transform: translateY(0) !important; }

        .lp3-arrow {
          transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
        }
        .lp3-arrow:hover:not(:disabled) {
          transform: scale(1.14);
          background: rgba(255,255,255,0.12) !important;
          box-shadow: 0 0 16px rgba(79,209,197,0.25);
        }
        .lp3-arrow:disabled { opacity: 0.2; cursor: not-allowed; }
      `}</style>

      {/* ── Header ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="heading-3d" style={{ marginBottom: 52, display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 20 }}>
          <div>
            <SectionLabel>The Workforce</SectionLabel>
            <h2 className="font-['Outfit'] font-bold text-white" style={{ fontSize: "clamp(2.1rem, 4vw, 3rem)", lineHeight: 1.1 }}>
              Meet Your{" "}
              <span style={{
                background: "linear-gradient(135deg, #a78bfa 0%, #4fd1c5 60%, #818cf8 100%)",
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              }}>
                AI Team
              </span>
            </h2>
            <p style={{ color: "#475569", marginTop: 10, fontSize: 15 }}>
              458+ specialists, each alive and working for you — right now.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button className="lp3-arrow" disabled={!canLeft} onClick={() => scrollBy(-1)} style={{
              width: 44, height: 44, borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)",
              color: canLeft ? "#e2e8f0" : "#1e293b",
              display: "flex", alignItems: "center", justifyContent: "center", cursor: canLeft ? "pointer" : "not-allowed",
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <button className="lp3-arrow" disabled={!canRight} onClick={() => scrollBy(1)} style={{
              width: 44, height: 44, borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)",
              color: canRight ? "#e2e8f0" : "#1e293b",
              display: "flex", alignItems: "center", justifyContent: "center", cursor: canRight ? "pointer" : "not-allowed",
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
            <button
              onClick={() => navigate("/register")}
              style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                padding: "11px 24px", borderRadius: 10, fontSize: 13, fontWeight: 700,
                background: "linear-gradient(135deg, rgba(167,139,250,0.15), rgba(79,209,197,0.12))",
                color: "#c4b5fd", cursor: "pointer",
                border: "1px solid rgba(167,139,250,0.25)", transition: "all 0.2s",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(167,139,250,0.55)"; e.currentTarget.style.background = "linear-gradient(135deg, rgba(167,139,250,0.22), rgba(79,209,197,0.18))"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(167,139,250,0.25)"; e.currentTarget.style.background = "linear-gradient(135deg, rgba(167,139,250,0.15), rgba(79,209,197,0.12))"; }}
            >
              Access All 458 Agents
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
        </div>
      </div>

      {/* ── Carousel track ── */}
      <div
        ref={trackRef}
        className="lp3-track"
        onScroll={updateArrows}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={() => { onMouseUp(); setPaused(false); }}
        onMouseEnter={() => setPaused(true)}
        style={{
          display: "flex", gap: GAP,
          overflowX: "auto", overflowY: "visible",
          paddingLeft: "max(1rem, calc((100vw - 1280px)/2 + 2rem))",
          paddingRight: 40, paddingTop: 12, paddingBottom: 40,
          cursor: dragging ? "grabbing" : "grab",
        }}
      >
        {agents.map((agent, i) => {
          const accent   = roleAccent(agent.role, agent.isCommander);
          const delay    = `${(i * 0.055) % 2.2}s`;
          const floatDur = `${3.5 + (i % 5) * 0.4}s`;
          const breathDur= `${4.5 + (i % 7) * 0.35}s`;
          const cardW    = agent.isCommander ? 268 : CARD_W;
          const cardH    = agent.isCommander ? 410 : 368;

          return (
            <div
              key={i}
              onClick={() => !dragging && navigate("/register")}
              className="lp3-card"
              style={{
                flexShrink: 0, width: cardW, height: cardH,
                borderRadius: 22, overflow: "hidden",
                position: "relative",
                animationDelay: delay,
                border: `1px solid ${agent.isCommander ? "rgba(245,158,11,0.45)" : "rgba(255,255,255,0.09)"}`,
                boxShadow: agent.isCommander
                  ? `0 0 60px rgba(245,158,11,0.2), 0 32px 64px rgba(0,0,0,0.6)`
                  : `0 20px 48px rgba(0,0,0,0.5)`,
                animation: agent.isCommander
                  ? `lp_card_in 0.6s cubic-bezier(0.22,1,0.36,1) ${delay} both, lp_float_card ${floatDur} ease-in-out ${delay} infinite`
                  : `lp_card_in 0.6s cubic-bezier(0.22,1,0.36,1) ${delay} both`,
              }}
              onMouseEnter={e => {
                if (dragging) return;
                e.currentTarget.style.borderColor = `${accent}cc`;
                e.currentTarget.style.boxShadow = `0 0 0 1px ${accent}44, 0 0 40px ${accent}28, 0 32px 64px rgba(0,0,0,0.6)`;
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = agent.isCommander ? "rgba(245,158,11,0.45)" : "rgba(255,255,255,0.09)";
                e.currentTarget.style.boxShadow = agent.isCommander
                  ? `0 0 60px rgba(245,158,11,0.2), 0 32px 64px rgba(0,0,0,0.6)`
                  : `0 20px 48px rgba(0,0,0,0.5)`;
              }}
            >
              {/* ── Full-bleed breathing portrait ── */}
              <img
                src={agent.avatar}
                alt={agent.name}
                className="lp3-img"
                loading="lazy"
                draggable={false}
                style={{
                  position: "absolute", inset: 0,
                  width: "100%", height: "100%",
                  objectFit: "cover", objectPosition: "center top",
                  animation: `lp_img_alive ${breathDur} ease-in-out ${delay} infinite`,
                  transformOrigin: "50% 20%",
                }}
                onError={e => {
                  e.target.src = `https://randomuser.me/api/portraits/${i % 2 === 0 ? "men" : "women"}/${(i * 3 + 7) % 70 + 1}.jpg`;
                }}
              />

              {/* ── Shimmer sweep on hover ── */}
              <div className="lp3-shimmer" style={{
                position: "absolute", inset: 0, zIndex: 3,
                background: "linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.12) 50%, transparent 65%)",
                opacity: 0, pointerEvents: "none",
                animation: "lp_shimmer 1.4s ease-in-out",
                transition: "opacity 0.3s",
              }} />

              {/* ── Scan line (subtle HUD feel) ── */}
              <div style={{
                position: "absolute", left: 0, right: 0, height: 1, zIndex: 4,
                background: `linear-gradient(90deg, transparent, ${accent}66, transparent)`,
                animation: `lp_scan ${7 + i % 4}s linear ${delay} infinite`,
                pointerEvents: "none",
              }} />

              {/* ── Atmospheric gradient ── */}
              <div style={{
                position: "absolute", inset: 0, zIndex: 2,
                background: `linear-gradient(
                  to bottom,
                  rgba(3,7,18,0.04) 0%,
                  rgba(3,7,18,0.06) 30%,
                  rgba(3,7,18,0.45) 55%,
                  rgba(3,7,18,0.88) 75%,
                  rgba(3,7,18,0.97) 100%
                )`,
              }} />

              {/* ── Role-accent glow at bottom ── */}
              <div style={{
                position: "absolute", bottom: 0, left: 0, right: 0, height: "55%", zIndex: 2,
                background: `radial-gradient(ellipse at 50% 110%, ${accent}30 0%, transparent 65%)`,
                animation: `lp_glow_beat ${floatDur} ease-in-out ${delay} infinite`,
              }} />

              {/* ── Commander badge ── */}
              {agent.isCommander && (
                <div style={{
                  position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                  padding: "5px 16px", fontSize: 9, fontWeight: 900,
                  background: "linear-gradient(90deg, #f59e0b, #d97706, #f59e0b)",
                  backgroundSize: "200% 100%",
                  animation: "lp_border_run 3s ease infinite",
                  color: "#000", borderRadius: 24, letterSpacing: "0.2em",
                  whiteSpace: "nowrap", boxShadow: "0 0 20px rgba(245,158,11,0.7), 0 2px 12px rgba(0,0,0,0.5)",
                  zIndex: 10,
                }}>
                  ⚡ COMMANDER
                </div>
              )}

              {/* ── Live online dot ── */}
              <div style={{
                position: "absolute", top: 16, right: 16, zIndex: 10,
                display: "flex", alignItems: "center", gap: 5,
              }}>
                <div style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: "#34d399", border: "2px solid rgba(3,7,18,0.8)",
                  animation: `lp_dot_live 2.2s ease-in-out ${delay} infinite`,
                }} />
                <span style={{
                  fontSize: 9, color: "rgba(52,211,153,0.9)", fontWeight: 700,
                  letterSpacing: "0.08em", textShadow: "0 0 8px rgba(52,211,153,0.5)",
                }}>LIVE</span>
              </div>

              {/* ── Bottom info ── */}
              <div style={{
                position: "absolute", bottom: 0, left: 0, right: 0,
                padding: "0 20px 20px", zIndex: 5,
              }}>
                {/* Activity ticker */}
                <div style={{ marginBottom: 10 }}>
                  <ActivityTicker role={agent.role} accent={accent} delay={i} />
                </div>

                <p style={{
                  color: accent, fontSize: 10, fontWeight: 800,
                  letterSpacing: "0.12em", textTransform: "uppercase",
                  marginBottom: 5, opacity: 0.9,
                  textShadow: `0 0 12px ${accent}`,
                }}>{agent.role}</p>
                <h3 className="font-['Outfit'] font-bold text-white" style={{
                  fontSize: agent.isCommander ? 21 : 18,
                  lineHeight: 1.15, marginBottom: 10,
                  textShadow: "0 2px 16px rgba(0,0,0,0.8)",
                }}>
                  {agent.name}
                </h3>

                {/* Capability pills */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {agent.capabilities.slice(0, 2).map((cap, ci) => (
                    <span key={ci} style={{
                      padding: "4px 10px", fontSize: 10, borderRadius: 20, fontWeight: 600,
                      background: `${accent}18`, color: accent,
                      border: `1px solid ${accent}30`,
                      backdropFilter: "blur(6px)",
                    }}>{cap}</span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

// ─── LandingPage ──────────────────────────────────────────────────────────────
const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const scrollY = useRef(0);
  const heroRef = useRef(null);
  const heroContentRef = useRef(null);
  const sectionsRef = useRef([]);

  // Track scroll for camera parallax
  useEffect(() => {
    const onScroll = () => { scrollY.current = window.scrollY; };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Scroll-driven GSAP animations — unified scrub for full synchronization
  useEffect(() => {
    // Normalize scroll across browsers (fixes Windows Chrome jank)
    ScrollTrigger.normalizeScroll(true);

    const ctx = gsap.context(() => {

      // ── Hero content: scrub parallax (only this should be scrubbed) ──
      if (heroContentRef.current) {
        gsap.to(heroContentRef.current, {
          y: 90, opacity: 0.08, scale: 0.88,
          ease: "none",
          scrollTrigger: {
            trigger: heroRef.current,
            start: "top top",
            end: "bottom top",
            scrub: 0.6,
          },
        });
      }

      // ── Depth sections: play-once reveal, fires as soon as section enters viewport ──
      document.querySelectorAll(".depth-section").forEach((section) => {
        gsap.fromTo(section,
          { y: 50, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.7, ease: "power3.out",
            scrollTrigger: {
              trigger: section,
              start: "top 92%",
              toggleActions: "play none none none",
            },
          }
        );
      });

      // ── Cards: staggered play-once tilt entry ──
      document.querySelectorAll(".card-3d-entry").forEach((card, i) => {
        const tilt = i % 2 === 0 ? -6 : 6;
        gsap.fromTo(card,
          { y: 40, rotateY: tilt, opacity: 0, scale: 0.94 },
          { y: 0, rotateY: 0, opacity: 1, scale: 1,
            duration: 0.6, ease: "power3.out",
            delay: (i % 4) * 0.06,
            scrollTrigger: {
              trigger: card,
              start: "top 94%",
              toggleActions: "play none none none",
            },
          }
        );
      });

      // ── Headings: play-once fade+Y ──
      document.querySelectorAll(".heading-3d").forEach((h) => {
        gsap.fromTo(h,
          { y: 36, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.65, ease: "power3.out",
            scrollTrigger: {
              trigger: h,
              start: "top 92%",
              toggleActions: "play none none none",
            },
          }
        );
      });

      // ── CTA: dramatic play-once entrance ──
      const cta = document.querySelector(".cta-section");
      if (cta) {
        gsap.fromTo(cta,
          { y: 80, scale: 0.92, opacity: 0 },
          { y: 0, scale: 1, opacity: 1, duration: 0.9, ease: "power4.out",
            scrollTrigger: {
              trigger: cta,
              start: "top 90%",
              toggleActions: "play none none none",
            },
          }
        );
      }

      // ── Stats belt + staggered stat items ──
      const belt = document.querySelector(".stats-belt");
      if (belt) {
        gsap.fromTo(belt,
          { y: 40, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, ease: "power3.out",
            scrollTrigger: {
              trigger: belt,
              start: "top 92%",
              toggleActions: "play none none none",
            },
          }
        );
        belt.querySelectorAll(".stat-item-3d").forEach((item, i) => {
          gsap.fromTo(item,
            { y: 20, opacity: 0 },
            { y: 0, opacity: 1, duration: 0.5, ease: "power2.out",
              delay: i * 0.07,
              scrollTrigger: {
                trigger: belt,
                start: "top 90%",
                toggleActions: "play none none none",
              },
            }
          );
        });
      }

      // ── Depth orbs: scrub parallax (subtle background movement) ──
      document.querySelectorAll(".depth-orb").forEach((orb, i) => {
        const dir = i % 2 === 0 ? 1 : -1;
        gsap.to(orb, {
          y: dir * 90,
          ease: "none",
          scrollTrigger: {
            trigger: orb.parentElement,
            start: "top bottom",
            end: "bottom top",
            scrub: 1.5,
          },
        });
      });

    });

    // Refresh after all images and fonts have loaded so trigger positions are accurate
    const onLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", onLoad);
    // Also refresh once on next frame in case DOM settled
    requestAnimationFrame(() => ScrollTrigger.refresh());

    return () => {
      ctx.revert();
      window.removeEventListener("load", onLoad);
    };
  }, []);

  return (
    <div style={{
      background: C.bg, color: "#e2e8f0", minHeight: "100vh", cursor: "none",
    }}>
      <CustomCursor />

      {/* ── NAV ─────────────────────────────────────────────────────────────── */}
      <nav
        style={{
          position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
          backdropFilter: "blur(20px)",
          background: "rgba(3,7,18,0.75)",
          borderBottom: `1px solid ${C.border}`,
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2.5" data-testid="logo-link">
              <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-8 h-8 rounded-lg object-cover" style={{ boxShadow: `0 0 12px ${C.teal}44` }} />
              <span className="text-xl font-bold text-white font-['Outfit'] tracking-tight">MAARS Command</span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              {["#features", "#agents", "#models"].map((href, i) => (
                <a key={href} href={href} className="text-sm text-zinc-400 hover:text-white transition-colors" style={{ transition: "color 0.2s" }}>
                  {["Features", "Agents", "Models"][i]}
                </a>
              ))}
              <Link to="/pricing" className="text-sm text-zinc-400 hover:text-white transition-colors" data-testid="pricing-link">Pricing</Link>
              <Link to="/login" className="text-sm text-zinc-400 hover:text-white transition-colors" data-testid="login-link">Login</Link>
              <button
                onClick={() => navigate("/register")}
                data-testid="get-started-btn"
                data-cursor
                style={{
                  padding: "8px 20px", borderRadius: 8, fontSize: 14, fontWeight: 600,
                  background: `linear-gradient(135deg, ${C.teal}22, ${C.violet}33)`,
                  border: `1px solid ${C.teal}55`,
                  color: C.teal, cursor: "none", transition: "all 0.2s",
                }}
                onMouseEnter={e => { e.target.style.background = `linear-gradient(135deg, ${C.teal}33, ${C.violet}44)`; e.target.style.boxShadow = `0 0 20px ${C.teal}44`; }}
                onMouseLeave={e => { e.target.style.background = `linear-gradient(135deg, ${C.teal}22, ${C.violet}33)`; e.target.style.boxShadow = "none"; }}
              >
                Get Started
              </button>
            </div>

            <button className="md:hidden p-2 text-zinc-400 hover:text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-btn">
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div style={{ background: "rgba(3,7,18,0.95)", borderTop: `1px solid ${C.border}` }} className="md:hidden px-4 py-4 space-y-4">
            <a href="#features" className="block text-zinc-400 hover:text-white">Features</a>
            <a href="#agents" className="block text-zinc-400 hover:text-white">Agents</a>
            <Link to="/pricing" className="block text-zinc-400 hover:text-white">Pricing</Link>
            <Link to="/login" className="block text-zinc-400 hover:text-white">Login</Link>
            <button onClick={() => navigate("/register")} className="w-full" style={{ background: `linear-gradient(135deg, ${C.teal}, ${C.violet})`, border: "none", borderRadius: 8, padding: "8px 16px", color: "#fff", fontWeight: 600, cursor: "pointer" }}>
              Get Started
            </button>
          </div>
        )}
      </nav>

      {/* ── HERO ─────────────────────────────────────────────────────────────── */}
      <section ref={heroRef} style={{ position: "relative", height: "100vh", display: "flex", alignItems: "center", overflow: "hidden" }}>
        {/* 3D Canvas — full screen background */}
        <div style={{ position: "absolute", inset: 0, zIndex: 0 }}>
          <Suspense fallback={null}>
            <NeuralCommandCanvas scrollY={scrollY} />
          </Suspense>
        </div>

        {/* Perspective grid floor */}
        <div className="perspective-grid-floor" style={{ position: "absolute", bottom: 0, left: 0, right: 0, zIndex: 1, height: "55%", overflow: "hidden", pointerEvents: "none" }}>
          <div className="grid-plane" />
        </div>

        {/* Tunnel depth rings */}
        <div style={{ position: "absolute", inset: 0, zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
          {[0,1,2,3,4].map(i => (
            <div key={i} className="depth-orb" style={{
              position: "absolute",
              width: `${(i + 1) * 22}vw`, height: `${(i + 1) * 22}vw`,
              borderRadius: "50%",
              border: `1px solid rgba(79,209,197,${0.07 - i * 0.012})`,
              boxShadow: `0 0 ${30 + i * 20}px rgba(79,209,197,${0.03 - i * 0.005}) inset`,
              animation: `tunnel-pulse ${3.5 + i * 0.7}s ease-in-out ${i * 0.4}s infinite`,
            }} />
          ))}
        </div>

        {/* Vignette gradient */}
        <div style={{
          position: "absolute", inset: 0, zIndex: 2,
          background: `radial-gradient(ellipse 80% 70% at 50% 50%, transparent 0%, ${C.bg}cc 65%, ${C.bg} 100%)`,
        }} />

        {/* Hero text — left-anchored for asymmetric composition */}
        <div ref={heroContentRef} className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" style={{ zIndex: 3, willChange: "transform, opacity" }}>
          <div style={{ maxWidth: 620 }}>
            <GlowBadge color="teal">
              <Sparkles className="w-3 h-3" />
              The AI Workforce OS — MAARS Infinity
            </GlowBadge>

            <h1
              className="font-['Outfit'] font-black leading-[1.05] tracking-tight mt-5 mb-6"
              style={{ fontSize: "clamp(2.8rem, 7vw, 5.5rem)", color: "#fff" }}
            >
              458 AI Specialists.
              <br />
              <span style={{
                background: `linear-gradient(135deg, ${C.teal} 0%, #a78bfa 100%)`,
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              }}>
                One Command.
              </span>
            </h1>

            <p style={{ fontSize: "clamp(1rem, 2vw, 1.15rem)", color: "#94a3b8", lineHeight: 1.75, maxWidth: 520, marginBottom: 36 }}>
              The world's first enterprise-grade AI workforce platform.
              Chat with 458+ specialists, command them in parallel, and govern every action with live trust scoring — across 33 providers and 175,000+ models.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <button
                data-cursor
                onClick={() => navigate("/register")}
                data-testid="hero-get-started-btn"
                style={{
                  display: "inline-flex", alignItems: "center", gap: 10,
                  padding: "15px 34px", borderRadius: 11, fontSize: 16, fontWeight: 700,
                  background: `linear-gradient(135deg, ${C.teal}, ${C.blue})`,
                  color: "#030712", cursor: "none", border: "none",
                  boxShadow: `0 0 40px ${C.teal}44`, transition: "all 0.25s",
                }}
                onMouseEnter={e => { e.target.style.boxShadow = `0 0 60px ${C.teal}66`; e.target.style.transform = "scale(1.03)"; }}
                onMouseLeave={e => { e.target.style.boxShadow = `0 0 40px ${C.teal}44`; e.target.style.transform = "scale(1)"; }}
              >
                Deploy Your AI Team <ArrowRight className="w-4 h-4" />
              </button>
              <button
                data-cursor
                onClick={() => navigate("/login")}
                data-testid="hero-login-btn"
                style={{
                  display: "inline-flex", alignItems: "center", gap: 8,
                  padding: "15px 34px", borderRadius: 11, fontSize: 16, fontWeight: 600,
                  background: "transparent", color: "#e2e8f0", cursor: "none",
                  border: `1px solid ${C.border}`, transition: "all 0.25s",
                }}
                onMouseEnter={e => { e.target.style.borderColor = `${C.teal}66`; e.target.style.color = C.teal; }}
                onMouseLeave={e => { e.target.style.borderColor = C.border; e.target.style.color = "#e2e8f0"; }}
              >
                Sign In
              </button>
            </div>

            {/* Trust signals */}
            <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, color: "#334155", letterSpacing: "0.08em", textTransform: "uppercase", flexShrink: 0 }}>Powered by</span>
              {[
                { name: "GPT-5",   color: "#10b981" },
                { name: "Claude",  color: "#f97316" },
                { name: "Gemini",  color: "#3b82f6" },
                { name: "Grok",    color: "#94a3b8" },
                { name: "DeepSeek",color: C.teal },
                { name: "175k+",   color: "#a78bfa" },
              ].map(p => (
                <span key={p.name} style={{ fontSize: 11, fontWeight: 600, color: p.color, opacity: 0.7, padding: "3px 8px", borderRadius: 6, background: `${p.color}10`, border: `1px solid ${p.color}20` }}>
                  {p.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: "absolute", bottom: 32, left: "50%", transform: "translateX(-50%)", zIndex: 2,
          display: "flex", flexDirection: "column", alignItems: "center", gap: 8, opacity: 0.5,
          animation: "bounce 2s infinite",
        }}>
          <span style={{ fontSize: 11, letterSpacing: "0.15em", textTransform: "uppercase", color: C.teal }}>Scroll</span>
          <ChevronDown className="w-4 h-4" style={{ color: C.teal }} />
        </div>
      </section>

      {/* ── STATS BELT ───────────────────────────────────────────────────────── */}
      <div className="stats-belt" style={{ borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`, overflow: "hidden" }}>
        <div
          style={{ display: "flex", gap: 0 }}
          className="divide-x"
        >
          {stats.map((s, i) => (
            <div
              key={i}
              className="stat-item-3d"
              style={{
                flex: "1 1 0", minWidth: 100, padding: "20px 16px", textAlign: "center",
                borderColor: C.border,
              }}
            >
              <div style={{ fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800, color: i % 2 === 0 ? C.teal : "#a78bfa", lineHeight: 1.1, fontFamily: "Outfit, sans-serif" }}>
                {s.value}
              </div>
              <div style={{ fontSize: 11, color: "#64748b", letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 4 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── FEATURES ─────────────────────────────────────────────────────────── */}
      <section id="features" className="depth-section" style={{ padding: "100px 0", position: "relative" }}>
        {/* floating depth orbs */}
        <div className="depth-orb" style={{ position: "absolute", top: "10%", right: "-5%", width: 350, height: 350, borderRadius: "50%", background: `radial-gradient(circle, ${C.violet}10 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="depth-orb" style={{ position: "absolute", bottom: "15%", left: "-8%", width: 280, height: 280, borderRadius: "50%", background: `radial-gradient(circle, ${C.teal}08 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="heading-3d" style={{ marginBottom: 64 }}>
            <SectionLabel>Platform Capabilities</SectionLabel>
            <h2 className="font-['Outfit'] font-bold text-white" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
              Everything You Need to{" "}
              <span style={{ color: C.teal }}>Command AI</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <GlassCard key={i} className="card-3d-entry" data-3d data-3d-strength="12" data-3d-lift="10" style={{ padding: 28 }}>
                <div
                  style={{
                    width: 48, height: 48, borderRadius: 12, marginBottom: 20,
                    background: `${f.accent}18`,
                    border: `1px solid ${f.accent}33`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}
                >
                  <f.icon style={{ width: 22, height: 22, color: f.accent }} />
                </div>
                <h3 className="font-['Outfit'] font-semibold text-white mb-2" style={{ fontSize: 17 }}>{f.title}</h3>
                <p style={{ fontSize: 14, color: "#64748b", lineHeight: 1.65 }}>{f.desc}</p>
                {/* Hover glow accent line */}
                <div
                  className="absolute bottom-0 left-0 right-0 h-0.5 rounded-b-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ background: `linear-gradient(90deg, transparent, ${f.accent}88, transparent)` }}
                />
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────────────────────── */}
      <section className="depth-section" style={{ padding: "100px 0", borderTop: `1px solid ${C.border}`, position: "relative" }}>
        <div className="depth-orb" style={{ position: "absolute", top: "15%", left: "5%", width: 320, height: 320, borderRadius: "50%", background: `radial-gradient(circle, ${C.teal}08 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="depth-orb" style={{ position: "absolute", bottom: "20%", right: "5%", width: 280, height: 280, borderRadius: "50%", background: `radial-gradient(circle, ${C.violet}08 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="heading-3d" style={{ textAlign: "center", marginBottom: 72 }}>
            <SectionLabel>Getting Started</SectionLabel>
            <h2 className="font-['Outfit'] font-bold text-white" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
              From Zero to{" "}
              <span style={{ background: `linear-gradient(135deg, ${C.teal}, #a78bfa)`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                AI Command Center
              </span>{" "}
              in Minutes
            </h2>
            <p style={{ color: "#64748b", marginTop: 12, fontSize: 15, maxWidth: 520, margin: "12px auto 0" }}>
              Three steps to a fully operational AI workforce — no DevOps, no infrastructure, no model juggling.
            </p>
          </div>

          <div style={{ position: "relative" }}>
            {/* Connecting line */}
            <div style={{ position: "absolute", top: 40, left: "16.66%", right: "16.66%", height: 1, background: `linear-gradient(90deg, transparent, ${C.teal}40, ${C.violet}40, transparent)`, zIndex: 0, display: "none" }} className="md:block" />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  step: "01",
                  icon: Key,
                  color: C.teal,
                  title: "Get One API Key",
                  desc: "Sign up and receive your maars-sk key. One credential, universal access — 33 providers, 175,000+ models, all 458 agents.",
                  tag: "< 60 seconds",
                },
                {
                  step: "02",
                  icon: Bot,
                  color: "#a78bfa",
                  title: "Deploy Your Agents",
                  desc: "Chat with any of the 458 pre-built specialists or build custom agents with your own persona, tools, and knowledge base.",
                  tag: "No-code or API",
                },
                {
                  step: "03",
                  icon: BarChart3,
                  color: C.blue,
                  title: "Scale & Govern",
                  desc: "Trust scores, audit logs, budget controls, and live governance let you run autonomous agents at scale — safely.",
                  tag: "Enterprise-ready",
                },
              ].map(({ step, icon: Icon, color, title, desc, tag }, i) => (
                <div key={i} className="card-3d-entry" style={{ position: "relative", zIndex: 1 }}>
                  <GlassCard style={{ padding: 32, height: "100%" }} data-3d data-3d-strength="12" data-3d-lift="10">
                    {/* Step number */}
                    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
                      <div style={{
                        width: 52, height: 52, borderRadius: 14,
                        background: `${color}15`, border: `1px solid ${color}30`,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                      }}>
                        <Icon style={{ width: 22, height: 22, color }} />
                      </div>
                      <span style={{
                        fontSize: 48, fontWeight: 900, color: `${color}18`,
                        fontFamily: "Outfit, sans-serif", lineHeight: 1, letterSpacing: "-0.04em",
                        userSelect: "none",
                      }}>{step}</span>
                    </div>
                    <span style={{
                      display: "inline-block", padding: "3px 10px", borderRadius: 20,
                      background: `${color}12`, color, fontSize: 10, fontWeight: 700,
                      letterSpacing: "0.1em", textTransform: "uppercase",
                      border: `1px solid ${color}22`, marginBottom: 12,
                    }}>{tag}</span>
                    <h3 className="font-['Outfit'] font-bold text-white mb-3" style={{ fontSize: 18, lineHeight: 1.2 }}>{title}</h3>
                    <p style={{ fontSize: 14, color: "#64748b", lineHeight: 1.7 }}>{desc}</p>
                    {/* Bottom accent */}
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-b-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ background: `linear-gradient(90deg, transparent, ${color}66, transparent)` }} />
                  </GlassCard>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── AGENTS ───────────────────────────────────────────────────────────── */}
      <AgentCarousel agents={agents} navigate={navigate} />

      {/* ── MODELS / PROVIDERS ───────────────────────────────────────────────── */}
      <section id="models" className="depth-section" style={{ padding: "100px 0", position: "relative" }}>
        <div className="depth-orb" style={{ position: "absolute", top: "20%", left: "10%", width: 400, height: 400, borderRadius: "50%", background: `radial-gradient(circle, ${C.teal}08 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="heading-3d" style={{ marginBottom: 64, textAlign: "center" }}>
            <SectionLabel>Model Infrastructure</SectionLabel>
            <h2 className="font-['Outfit'] font-bold text-white" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
              33 Providers.{" "}
              <span style={{ background: `linear-gradient(135deg, ${C.teal}, #a78bfa)`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                175,000+ Models.
              </span>
            </h2>
            <p style={{ color: "#64748b", marginTop: 12, fontSize: 16, maxWidth: 520, margin: "12px auto 0" }}>
              609 curated models across every frontier provider, plus universal pass-through to all of HuggingFace's open-source catalogue.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {providers.map((p, pi) => (
              <div
                key={pi}
                className="card-3d-entry"
                data-3d data-3d-strength="10" data-3d-lift="8"
                style={{
                  padding: "18px 16px", borderRadius: 14,
                  background: C.glass, border: `1px solid ${C.border}`,
                  backdropFilter: "blur(8px)", transition: "all 0.25s",
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = `${p.color}55`; e.currentTarget.style.boxShadow = `0 4px 24px ${p.color}22`; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.boxShadow = "none"; }}
                data-testid={`models-${p.name.toLowerCase().replace(/[^a-z]/g, "")}`}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: p.color, boxShadow: `0 0 8px ${p.color}88`, flexShrink: 0 }} />
                  <h3 className="font-['Outfit'] font-semibold text-white" style={{ fontSize: 13, lineHeight: 1.3 }}>{p.name}</h3>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {p.models.map((m, mi) => (
                    <div key={mi} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ color: "#94a3b8", fontSize: 12, flex: 1, lineHeight: 1.3 }}>{m.name}</span>
                      <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 20, background: `${p.color}18`, color: p.color, whiteSpace: "nowrap" }}>
                        {m.tag}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* HuggingFace universal card */}
            <div
              className="card-3d-entry"
              data-3d data-3d-strength="10" data-3d-lift="8"
              style={{
                padding: "18px 16px", borderRadius: 14, gridColumn: "span 1",
                background: `linear-gradient(135deg, rgba(79,209,197,0.08), rgba(124,58,237,0.08))`,
                border: `1px solid ${C.teal}33`,
                backdropFilter: "blur(8px)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <Zap style={{ width: 14, height: 14, color: C.teal }} />
                <span className="font-['Outfit'] font-bold text-white" style={{ fontSize: 13 }}>Smart Routing</span>
              </div>
              <p style={{ fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>
                Each agent selects the optimal model for the task — coding, writing, research, or analysis.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── DEVELOPER API ─────────────────────────────────────────────────────── */}
      <section className="depth-section" style={{ padding: "100px 0", borderTop: `1px solid ${C.border}`, position: "relative" }}>
        <div className="depth-orb" style={{ position: "absolute", top: "30%", right: "-5%", width: 500, height: 500, borderRadius: "50%", background: `radial-gradient(circle, #a78bfa08 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="heading-3d" style={{ textAlign: "center", marginBottom: 56 }}>
            <GlowBadge color="violet">
              <Terminal className="w-3 h-3" /> Developer API
            </GlowBadge>
            <h2 className="font-['Outfit'] font-bold text-white mt-4" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
              One Key.{" "}
              <span style={{ color: "#a78bfa" }}>175,000+ Models.</span>{" "}
              Zero Hassle.
            </h2>
            <p style={{ color: "#64748b", marginTop: 12, fontSize: 16, maxWidth: 560, margin: "12px auto 0" }}>
              Single OpenAI-compatible endpoint. Drop-in replace your <code style={{ color: C.teal, background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: 4 }}>base_url</code> and call 175,000+ models with your existing SDK.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
            {[
              { icon: Globe, color: C.teal, title: "33 Providers + 175,000+ Models", desc: "609 curated models across all major providers, plus every HuggingFace open-source model via universal pass-through." },
              { icon: Zap, color: "#a78bfa", title: "10 Smart Aliases", desc: "Use maars/auto, maars/code, maars/fast — MAARS routes to the best model for your task and budget automatically." },
              { icon: Key, color: C.blue, title: "One maars-sk Key", desc: "Instant access to all 175,000+ models. Manage budgets, rate limits, and webhooks from a single admin panel." },
            ].map(({ icon: Icon, color, title, desc }) => (
              <GlassCard key={title} className="card-3d-entry" style={{ padding: 24 }} data-3d data-3d-strength="11" data-3d-lift="9">
                <div style={{ width: 42, height: 42, borderRadius: 10, background: `${color}18`, border: `1px solid ${color}33`, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16 }}>
                  <Icon style={{ width: 20, height: 20, color }} />
                </div>
                <h3 className="font-semibold text-white mb-2" style={{ fontSize: 15 }}>{title}</h3>
                <p style={{ fontSize: 13, color: "#64748b", lineHeight: 1.6 }}>{desc}</p>
              </GlassCard>
            ))}
          </div>

          {/* Code block */}
          <div
            className="card-3d-entry"
            data-3d data-3d-strength="8" data-3d-lift="14"
            style={{
              borderRadius: 16, border: `1px solid ${C.border}`,
              background: "rgba(0,0,0,0.4)", backdropFilter: "blur(12px)",
              overflow: "hidden", marginBottom: 32,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "14px 20px", borderBottom: `1px solid ${C.border}` }}>
              <div style={{ display: "flex", gap: 6 }}>
                {["#ff5f57", "#febc2e", "#28c840"].map(c => <div key={c} style={{ width: 12, height: 12, borderRadius: "50%", background: c }} />)}
              </div>
              <span style={{ fontSize: 12, color: "#475569", fontFamily: "monospace" }}>Python — drop-in replacement</span>
            </div>
            <pre style={{ padding: "24px", fontSize: 13, fontFamily: "monospace", color: "#94a3b8", overflowX: "auto", lineHeight: 1.8, margin: 0 }}>
{`from openai import OpenAI

client = OpenAI(
    base_url`}<span style={{ color: C.teal }}>=</span>{`"`}<span style={{ color: "#86efac" }}>https://maars.ai/api</span>{`",   `}<span style={{ color: "#475569" }}># ← change only this</span>{`
    api_key`}<span style={{ color: C.teal }}>=</span>{`"`}<span style={{ color: "#86efac" }}>maars-sk-...</span>{`",
)

`}<span style={{ color: "#475569" }}># Access 175,000+ models across 33 providers</span>{`
response = client.chat.completions.create(
    model`}<span style={{ color: C.teal }}>=</span>{`"`}<span style={{ color: "#fbbf24" }}>maars/auto</span>{`",   `}<span style={{ color: "#475569" }}># smart routing</span>{`
    messages=[{`}<span style={{ color: "#fbbf24" }}>"role"</span>{`: `}<span style={{ color: "#86efac" }}>"user"</span>{`, `}<span style={{ color: "#fbbf24" }}>"content"</span>{`: `}<span style={{ color: "#86efac" }}>"Hello!"</span>{`}],
)`}
            </pre>
          </div>

          <div data-reveal style={{ textAlign: "center" }}>
            <button
              data-cursor
              onClick={() => navigate("/register")}
              style={{
                display: "inline-flex", alignItems: "center", gap: 10,
                padding: "14px 32px", borderRadius: 10, fontSize: 15, fontWeight: 700,
                background: `linear-gradient(135deg, ${C.violet}, #6d28d9)`,
                color: "#fff", cursor: "none", border: "none",
                boxShadow: `0 0 40px ${C.violet}44`, transition: "all 0.25s",
              }}
              onMouseEnter={e => { e.target.style.boxShadow = `0 0 60px ${C.violet}66`; e.target.style.transform = "scale(1.03)"; }}
              onMouseLeave={e => { e.target.style.boxShadow = `0 0 40px ${C.violet}44`; e.target.style.transform = "scale(1)"; }}
            >
              Get Your Free API Key <ArrowRight className="w-4 h-4" />
            </button>
            <p style={{ fontSize: 12, color: "#64748b", marginTop: 12 }}>
              No credit card required · Free tier included · Full docs after sign-up
            </p>
          </div>
        </div>
      </section>

      {/* ── SOCIAL PROOF ─────────────────────────────────────────────────────── */}
      <section className="depth-section" style={{ padding: "100px 0", borderTop: `1px solid ${C.border}`, position: "relative" }}>
        <div className="depth-orb" style={{ position: "absolute", top: "20%", left: "50%", transform: "translateX(-50%)", width: 600, height: 600, borderRadius: "50%", background: `radial-gradient(circle, ${C.violet}06 0%, transparent 70%)`, pointerEvents: "none" }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="heading-3d" style={{ textAlign: "center", marginBottom: 64 }}>
            <SectionLabel>Why Teams Choose MAARS</SectionLabel>
            <h2 className="font-['Outfit'] font-bold text-white" style={{ fontSize: "clamp(1.8rem, 3.5vw, 2.5rem)" }}>
              Built for Teams That{" "}
              <span style={{ color: C.teal }}>Move Fast</span>
            </h2>
          </div>

          {/* Metric highlights */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-16">
            {[
              { value: "10×", label: "Faster execution", sub: "vs. manual workflows", color: C.teal },
              { value: "458+", label: "Expert agents", sub: "ready in seconds", color: "#a78bfa" },
              { value: "175k+", label: "Models available", sub: "from 33 providers", color: C.blue },
              { value: "100%", label: "Governance", sub: "every action audited", color: "#f59e0b" },
            ].map((m, i) => (
              <GlassCard key={i} className="card-3d-entry text-center" style={{ padding: "28px 20px" }} data-3d data-3d-strength="10" data-3d-lift="8">
                <div style={{ fontSize: "clamp(2rem, 3.5vw, 2.8rem)", fontWeight: 900, color: m.color, fontFamily: "Outfit, sans-serif", lineHeight: 1, marginBottom: 8 }}>{m.value}</div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", marginBottom: 4 }}>{m.label}</div>
                <div style={{ fontSize: 11, color: "#475569" }}>{m.sub}</div>
              </GlassCard>
            ))}
          </div>

          {/* Testimonial cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                quote: "We replaced three separate SaaS tools and a contractor with MAARS. The 458 pre-built agents cover everything from SEO audits to financial modeling.",
                name: "Head of Growth",
                company: "Series B SaaS",
                accent: C.teal,
              },
              {
                quote: "The Commander orchestration is a game-changer. One instruction fans out to 12 specialized agents in parallel. Tasks that took days now take minutes.",
                name: "CTO",
                company: "AI-native startup",
                accent: "#a78bfa",
              },
              {
                quote: "Governance was our blocker for AI adoption. MAARS trust scores, audit logs and RBAC gave us exactly what the legal team needed to approve it.",
                name: "VP Engineering",
                company: "FinTech scale-up",
                accent: C.blue,
              },
            ].map((t, i) => (
              <GlassCard key={i} className="card-3d-entry" style={{ padding: 28 }} data-3d data-3d-strength="10" data-3d-lift="8">
                {/* Quote mark */}
                <div style={{ fontSize: 48, lineHeight: 1, color: t.accent, opacity: 0.25, fontFamily: "serif", marginBottom: 8, userSelect: "none" }}>"</div>
                <p style={{ fontSize: 14, color: "#94a3b8", lineHeight: 1.75, marginBottom: 20, fontStyle: "italic" }}>{t.quote}</p>
                <div style={{ display: "flex", alignItems: "center", gap: 12, paddingTop: 16, borderTop: `1px solid rgba(255,255,255,0.06)` }}>
                  <div style={{ width: 36, height: 36, borderRadius: "50%", background: `${t.accent}20`, border: `1px solid ${t.accent}30`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <Users style={{ width: 16, height: 16, color: t.accent }} />
                  </div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0" }}>{t.name}</div>
                    <div style={{ fontSize: 11, color: "#475569" }}>{t.company}</div>
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-b-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ background: `linear-gradient(90deg, transparent, ${t.accent}66, transparent)` }} />
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────────── */}
      <section className="cta-section" style={{ padding: "120px 0", position: "relative", overflow: "hidden" }}>
        {/* radial glow */}
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
          <div style={{ width: 600, height: 600, borderRadius: "50%", background: `radial-gradient(circle, ${C.violet}18 0%, transparent 70%)` }} />
        </div>

        <div className="relative max-w-4xl mx-auto px-4 text-center" style={{ zIndex: 1 }}>
          <div data-reveal>
            <GlowBadge color="violet">Command Your AI Workforce</GlowBadge>
            <h2 className="font-['Outfit'] font-black text-white mt-5 mb-4" style={{ fontSize: "clamp(2.2rem, 5vw, 3.5rem)", lineHeight: 1.1 }}>
              Ready to Build Your
              <br />
              <span style={{ background: `linear-gradient(135deg, ${C.teal}, #a78bfa)`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                AI Team?
              </span>
            </h2>
            <p style={{ color: "#64748b", fontSize: 17, marginBottom: 40, maxWidth: 500, margin: "0 auto 40px" }}>
              Join professionals leveraging AI to supercharge their workflow. One key. Every model. Unlimited potential.
            </p>
            <button
              data-cursor
              onClick={() => navigate("/register")}
              data-testid="cta-get-started-btn"
              style={{
                display: "inline-flex", alignItems: "center", gap: 10,
                padding: "16px 40px", borderRadius: 12, fontSize: 17, fontWeight: 700,
                background: `linear-gradient(135deg, ${C.teal}, ${C.blue})`,
                color: "#030712", cursor: "none", border: "none",
                boxShadow: `0 0 60px ${C.teal}55`, transition: "all 0.25s",
              }}
              onMouseEnter={e => { e.target.style.boxShadow = `0 0 80px ${C.teal}77`; e.target.style.transform = "scale(1.04)"; }}
              onMouseLeave={e => { e.target.style.boxShadow = `0 0 60px ${C.teal}55`; e.target.style.transform = "scale(1)"; }}
            >
              Get Started Free <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────────── */}
      <footer style={{ borderTop: `1px solid ${C.border}`, padding: "32px 0" }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-6 h-6 rounded object-cover" />
            <span style={{ color: "#64748b", fontSize: 14 }}>MAARS Command by MAARS Global Corporation © 2026</span>
          </div>
          <div className="flex items-center gap-6" style={{ fontSize: 13, color: "#64748b" }}>
            <a href="#models" className="hover:text-white transition-colors">175,000+ Models</a>
            <a href="#agents" className="hover:text-white transition-colors">458+ Agents</a>
            <Link to="/developer" className="hover:text-white transition-colors">Developer API</Link>
            <Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link>
          </div>
        </div>
      </footer>

      {/* Deep 3D CSS */}
      <style>{`
        * { cursor: none !important; }

        @keyframes bounce {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(6px); }
        }

        /* ── Perspective grid floor ── */
        .perspective-grid-floor {
          perspective: 600px;
          perspective-origin: 50% 0%;
          overflow: hidden;
        }
        .grid-plane {
          position: absolute;
          bottom: 0;
          left: -50%;
          right: -50%;
          height: 100%;
          transform-origin: 50% 100%;
          transform: rotateX(72deg);
          background-image:
            linear-gradient(rgba(79,209,197,0.09) 1px, transparent 1px),
            linear-gradient(90deg, rgba(79,209,197,0.09) 1px, transparent 1px);
          background-size: 70px 70px;
          background-position: center bottom;
          animation: lp-grid-scroll 3s linear infinite;
          mask-image: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%);
          -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%);
        }
        @keyframes lp-grid-scroll {
          from { background-position: center 0; }
          to   { background-position: center 70px; }
        }

        /* ── Tunnel pulse rings ── */
        @keyframes tunnel-pulse {
          0%, 100% { transform: scale(1); opacity: 0.7; }
          50%       { transform: scale(1.04); opacity: 0.3; }
        }

        /* ── Smooth anchor scrolling ── */
        html { scroll-behavior: smooth; }

        /* ── Scroll-animated layers ── */
        .depth-section {
          will-change: transform, opacity;
        }
        .card-3d-entry {
          will-change: transform, opacity;
          transform-style: preserve-3d;
          backface-visibility: hidden;
        }
        .heading-3d {
          will-change: transform, opacity;
        }

        /* ── Global 3D card tilt ── */
        [data-3d] {
          transition: transform 0.08s linear, box-shadow 0.2s ease;
        }

        /* ── Depth orb parallax ── */
        .depth-orb {
          will-change: transform;
          pointer-events: none;
        }

        /* ── Stats belt ── */
        .stats-belt { will-change: transform, opacity; }
        .stat-item-3d { will-change: transform, opacity; }

        /* ── Floating depth glow behind sections ── */
        .section-depth-glow {
          position: absolute;
          border-radius: 50%;
          filter: blur(80px);
          pointer-events: none;
          will-change: transform;
        }

        /* ── Respect reduced-motion preference ── */
        @media (prefers-reduced-motion: reduce) {
          .depth-section, .card-3d-entry, .heading-3d,
          .stat-item-3d, .stats-belt, .cta-section {
            opacity: 1 !important;
            transform: none !important;
          }
          .depth-orb { transform: none !important; }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
