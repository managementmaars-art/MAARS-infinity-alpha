import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Bot, Send, Plus, ArrowLeft, MessageSquare, Trash2,
  LayoutDashboard, Users, ListTodo, Settings, LogOut, Menu, X,
  Paperclip, Image, FileText, Sparkles, Mic, MicOff,
  Download, Film, FileSpreadsheet, File, Volume2, VolumeX,
  Search, Calculator, ClipboardList, BarChart3, Wrench, ChevronDown, ChevronRight, Brain, Zap,
  Mail, MessageCircle, Phone, Github, Table, Calendar, Share2, ThumbsUp, ThumbsDown, Globe, Scan, Package
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { CollaborationWorkflow } from "../components/chat/CollaborationWorkflow";

const PROVIDER_COLORS = {
  openai:     "#10b981",
  anthropic:  "#f97316",
  gemini:     "#3b82f6",
  xai:        "#94a3b8",
  deepseek:   "#4fd1c5",
  mistral:    "#8b5cf6",
  perplexity: "#4fd1c5",
  groq:       "#eab308",
  cerebras:   "#f59e0b",
  together:   "#22c55e",
  fireworks:  "#f59e0b",
  cohere:     "#ec4899",
  amazon:     "#f97316",
  nvidia:     "#76c442",
  sambanova:  "#f43f5e",
  huggingface:"#eab308",
  qwen:       "#60a5fa",
  moonshot:   "#3b82f6",
  minimax:    "#ec4899",
  hyperbolic: "#4fd1c5",
  novita:     "#8b5cf6",
  lepton:     "#6366f1",
  lambda:     "#6b7280",
  inception:  "#06b6d4",
  arcee:      "#a78bfa",
  ai21:       "#6366f1",
  writer:     "#a855f7",
  upstage:    "#eab308",
  yi:         "#10b981",
  zhipu:      "#3b82f6",
  doubao:     "#f59e0b",
  llama:      "#60a5fa",
  auto:       "#818cf8",
};

const AVAILABLE_MODELS = [
  // ── Universal Smart Router ────────────────────────────────────────────────
  { provider: "auto", model: "auto", name: "Universal Auto Router", category: "auto", credits: 0, desc: "Smart routing across 33 providers — task & credit aware" },
  // ── OpenAI ────────────────────────────────────────────────────────────────
  { provider: "openai", model: "gpt-5",        name: "GPT-5",           category: "flagship",  credits: 3 },
  { provider: "openai", model: "gpt-4.1",      name: "GPT-4.1",         category: "flagship",  credits: 2 },
  { provider: "openai", model: "gpt-4.1-mini", name: "GPT-4.1 Mini",    category: "fast",      credits: 1 },
  { provider: "openai", model: "gpt-4.1-nano", name: "GPT-4.1 Nano",    category: "economy",   credits: 1 },
  { provider: "openai", model: "gpt-4o",       name: "GPT-4o",          category: "fast",      credits: 2 },
  { provider: "openai", model: "gpt-4o-mini",  name: "GPT-4o Mini",     category: "economy",   credits: 1 },
  { provider: "openai", model: "o4",           name: "O4 (Reasoning)",  category: "reasoning", credits: 5 },
  { provider: "openai", model: "o4-mini",      name: "O4 Mini",         category: "reasoning", credits: 2 },
  { provider: "openai", model: "o3",           name: "O3 (Reasoning)",  category: "reasoning", credits: 5 },
  { provider: "openai", model: "o3-mini",      name: "O3 Mini",         category: "reasoning", credits: 2 },
  // ── Anthropic ─────────────────────────────────────────────────────────────
  { provider: "anthropic", model: "claude-opus-4-6",           name: "Claude Opus 4.6",   category: "premium",  credits: 5 },
  { provider: "anthropic", model: "claude-sonnet-4-6",         name: "Claude Sonnet 4.6", category: "flagship", credits: 3 },
  { provider: "anthropic", model: "claude-haiku-4-5-20251001", name: "Claude Haiku 4.5",  category: "economy",  credits: 1 },
  { provider: "anthropic", model: "claude-sonnet-4-5-20250929", name: "Claude Sonnet 4.5", category: "flagship", credits: 3 },
  { provider: "anthropic", model: "claude-opus-4-5-20251101",  name: "Claude Opus 4.5",   category: "premium",  credits: 5 },
  // ── Google Gemini ─────────────────────────────────────────────────────────
  { provider: "gemini", model: "gemini-2.5-pro",        name: "Gemini 2.5 Pro",         category: "flagship", credits: 2 },
  { provider: "gemini", model: "gemini-2.5-flash",      name: "Gemini 2.5 Flash",       category: "fast",     credits: 1 },
  { provider: "gemini", model: "gemini-2.5-flash-lite", name: "Gemini 2.5 Flash Lite",  category: "economy",  credits: 1 },
  { provider: "gemini", model: "gemini-3-pro-preview",  name: "Gemini 3 Pro",           category: "flagship", credits: 2 },
  { provider: "gemini", model: "gemini-3-flash-preview", name: "Gemini 3 Flash",        category: "economy",  credits: 1 },
  // ── xAI Grok ─────────────────────────────────────────────────────────────
  { provider: "xai", model: "grok-3",      name: "Grok 3",      category: "flagship", credits: 3 },
  { provider: "xai", model: "grok-3-mini", name: "Grok 3 Mini", category: "economy",  credits: 1 },
  { provider: "xai", model: "grok-2",      name: "Grok 2",      category: "fast",     credits: 2 },
  // ── DeepSeek ──────────────────────────────────────────────────────────────
  { provider: "deepseek", model: "deepseek-v3-0324",  name: "DeepSeek V3",        category: "fast",      credits: 1 },
  { provider: "deepseek", model: "deepseek-chat",     name: "DeepSeek Chat",      category: "economy",   credits: 1 },
  { provider: "deepseek", model: "deepseek-r1-0528",  name: "DeepSeek R1",        category: "reasoning", credits: 2 },
  { provider: "deepseek", model: "deepseek-reasoner", name: "DeepSeek Reasoner",  category: "reasoning", credits: 2 },
  // ── Mistral ───────────────────────────────────────────────────────────────
  { provider: "mistral", model: "mistral-large-latest",  name: "Mistral Large",   category: "flagship", credits: 3 },
  { provider: "mistral", model: "mistral-medium-latest", name: "Mistral Medium",  category: "fast",     credits: 2 },
  { provider: "mistral", model: "mistral-small-latest",  name: "Mistral Small",   category: "economy",  credits: 1 },
  { provider: "mistral", model: "mistral-nemo",          name: "Mistral Nemo",    category: "economy",  credits: 1 },
  { provider: "mistral", model: "codestral-latest",      name: "Codestral",       category: "code",     credits: 1 },
  { provider: "mistral", model: "pixtral-large-latest",  name: "Pixtral Large",   category: "vision",   credits: 3 },
  // ── Perplexity ────────────────────────────────────────────────────────────
  { provider: "perplexity", model: "sonar-deep-research", name: "Sonar Deep Research", category: "research", credits: 3 },
  { provider: "perplexity", model: "sonar-reasoning-pro", name: "Sonar Reasoning Pro", category: "research", credits: 3 },
  { provider: "perplexity", model: "sonar-pro",           name: "Sonar Pro",           category: "research", credits: 3 },
  { provider: "perplexity", model: "sonar-reasoning",     name: "Sonar Reasoning",     category: "research", credits: 2 },
  { provider: "perplexity", model: "sonar",               name: "Sonar",               category: "search",   credits: 2 },
  // ── Cohere ────────────────────────────────────────────────────────────────
  { provider: "cohere", model: "command-a-03-2025", name: "Command A",   category: "flagship", credits: 3 },
  { provider: "cohere", model: "command-r-plus",    name: "Command R+",  category: "flagship", credits: 3 },
  { provider: "cohere", model: "command-r",         name: "Command R",   category: "economy",  credits: 1 },
  // ── Groq (Fast Open-Source) ───────────────────────────────────────────────
  { provider: "groq", model: "llama-4-maverick-17b-128e-instruct", name: "Llama 4 Maverick", category: "fast",    credits: 1 },
  { provider: "groq", model: "llama-4-scout-17b-16e-instruct",     name: "Llama 4 Scout",    category: "economy", credits: 1 },
  { provider: "groq", model: "llama-3.3-70b-versatile",            name: "Llama 3.3 70B",    category: "fast",    credits: 1 },
  { provider: "groq", model: "qwen-qwq-32b",                       name: "QwQ 32B",          category: "reasoning", credits: 1 },
  { provider: "groq", model: "gemma2-9b-it",                       name: "Gemma 2 9B",       category: "economy", credits: 1 },
  { provider: "groq", model: "llama-3.1-8b-instant",               name: "Llama 3.1 8B",     category: "economy", credits: 1 },
  // ── Cerebras (Ultra-Fast) ─────────────────────────────────────────────────
  { provider: "cerebras", model: "llama-3.3-70b", name: "Cerebras Llama 3.3 70B", category: "fast",    credits: 1 },
  { provider: "cerebras", model: "llama3.1-8b",   name: "Cerebras Llama 3.1 8B",  category: "economy", credits: 1 },
  { provider: "cerebras", model: "qwen-3-32b",    name: "Cerebras Qwen 3 32B",    category: "fast",    credits: 1 },
  // ── Together AI ───────────────────────────────────────────────────────────
  { provider: "together", model: "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", name: "Llama 4 Maverick FP8", category: "fast",      credits: 1 },
  { provider: "together", model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",           name: "Llama 3.3 70B Turbo",  category: "economy",   credits: 2 },
  { provider: "together", model: "Qwen/Qwen2.5-72B-Instruct-Turbo",                   name: "Qwen 2.5 72B",         category: "fast",      credits: 1 },
  { provider: "together", model: "Qwen/Qwen3-235B-A22B-Instruct-FP8",                 name: "Qwen 3 235B",          category: "flagship",  credits: 2 },
  { provider: "together", model: "deepseek-ai/DeepSeek-R1",                            name: "DeepSeek R1",          category: "reasoning", credits: 3 },
  // ── Fireworks AI ──────────────────────────────────────────────────────────
  { provider: "fireworks", model: "accounts/fireworks/models/llama4-maverick-instruct-basic", name: "FW Llama 4 Maverick", category: "fast",    credits: 1 },
  { provider: "fireworks", model: "accounts/fireworks/models/llama4-scout-instruct-basic",    name: "FW Llama 4 Scout",    category: "economy", credits: 1 },
  { provider: "fireworks", model: "accounts/fireworks/models/deepseek-v3",                    name: "FW DeepSeek V3",      category: "fast",    credits: 2 },
  { provider: "fireworks", model: "accounts/fireworks/models/phi-4",                          name: "FW Phi-4",            category: "fast",    credits: 1 },
  // ── AI21 ──────────────────────────────────────────────────────────────────
  { provider: "ai21", model: "jamba-large-1.7", name: "Jamba Large 1.7", category: "flagship", credits: 3 },
  { provider: "ai21", model: "jamba-mini-1.7",  name: "Jamba Mini 1.7",  category: "economy",  credits: 1 },
  // ── SambaNova ─────────────────────────────────────────────────────────────
  { provider: "sambanova", model: "Meta-Llama-3.3-70B-Instruct", name: "SN Llama 3.3 70B",   category: "fast",      credits: 1 },
  { provider: "sambanova", model: "Qwen2.5-72B-Instruct",        name: "SN Qwen 2.5 72B",    category: "fast",      credits: 1 },
  { provider: "sambanova", model: "DeepSeek-R1-0528",            name: "SN DeepSeek R1",      category: "reasoning", credits: 2 },
  // ── Nvidia NIM ────────────────────────────────────────────────────────────
  { provider: "nvidia", model: "nvidia/llama-3.1-nemotron-ultra-253b-v1", name: "Nemotron Ultra 253B", category: "premium",  credits: 2 },
  { provider: "nvidia", model: "nvidia/llama-3.1-nemotron-70b-instruct",  name: "Nemotron 70B",        category: "fast",     credits: 1 },
  { provider: "nvidia", model: "meta/llama-3.3-70b-instruct",             name: "NIM Llama 3.3 70B",   category: "fast",     credits: 1 },
  { provider: "nvidia", model: "meta/llama-3.1-8b-instruct",              name: "NIM Llama 3.1 8B",    category: "economy",  credits: 1 },
  // ── Moonshot AI (Kimi) ────────────────────────────────────────────────────
  { provider: "moonshot", model: "moonshot-v1-128k", name: "Kimi 128K", category: "long-context", credits: 2 },
  { provider: "moonshot", model: "moonshot-v1-32k",  name: "Kimi 32K",  category: "fast",         credits: 1 },
  { provider: "moonshot", model: "moonshot-v1-8k",   name: "Kimi 8K",   category: "economy",      credits: 1 },
  // ── Qwen / Alibaba ────────────────────────────────────────────────────────
  { provider: "qwen", model: "qwen-max",           name: "Qwen Max",          category: "flagship", credits: 3 },
  { provider: "qwen", model: "qwen3-235b-a22b",    name: "Qwen 3 235B",       category: "flagship", credits: 1 },
  { provider: "qwen", model: "qwen2.5-72b-instruct", name: "Qwen 2.5 72B",   category: "fast",     credits: 1 },
  { provider: "qwen", model: "qwen-plus",          name: "Qwen Plus",         category: "fast",     credits: 1 },
  { provider: "qwen", model: "qwen-turbo",         name: "Qwen Turbo",        category: "economy",  credits: 1 },
  // ── 01.AI / Yi ────────────────────────────────────────────────────────────
  { provider: "yi", model: "yi-lightning",   name: "Yi Lightning",    category: "fast",     credits: 1 },
  { provider: "yi", model: "yi-large-fc",    name: "Yi Large FC",     category: "flagship", credits: 2 },
  { provider: "yi", model: "yi-medium-200k", name: "Yi Medium 200K",  category: "flagship", credits: 3 },
  // ── Zhipu AI / GLM ───────────────────────────────────────────────────────
  { provider: "zhipu", model: "glm-4-plus",  name: "GLM-4-Plus",      category: "flagship", credits: 3 },
  { provider: "zhipu", model: "glm-4-air",   name: "GLM-4-Air",       category: "fast",     credits: 1 },
  { provider: "zhipu", model: "glm-z1-air",  name: "GLM-Z1-Air",      category: "reasoning",credits: 1 },
  // ── ByteDance Doubao ─────────────────────────────────────────────────────
  { provider: "doubao", model: "doubao-pro-128k", name: "Doubao Pro 128K", category: "flagship", credits: 2 },
  { provider: "doubao", model: "doubao-lite-32k",  name: "Doubao Lite 32K",  category: "economy",  credits: 1 },
  // ── Hyperbolic ────────────────────────────────────────────────────────────
  { provider: "hyperbolic", model: "meta-llama/Llama-3.3-70B-Instruct",       name: "Llama 3.3 70B (Hyperbolic)",  category: "fast",     credits: 1 },
  { provider: "hyperbolic", model: "meta-llama/Meta-Llama-3.1-405B-Instruct", name: "Llama 3.1 405B (Hyperbolic)", category: "flagship", credits: 2 },
  { provider: "hyperbolic", model: "deepseek-ai/DeepSeek-R1-hyperbolic",      name: "DeepSeek R1 (Hyperbolic)",    category: "reasoning",credits: 2 },
  // ── Upstage Solar ─────────────────────────────────────────────────────────
  { provider: "upstage", model: "solar-pro",  name: "Solar Pro",  category: "flagship", credits: 3 },
  { provider: "upstage", model: "solar-mini", name: "Solar Mini", category: "economy",  credits: 1 },
  // ── Writer Palmyra ───────────────────────────────────────────────────────
  { provider: "writer", model: "palmyra-x-004", name: "Palmyra X 004", category: "flagship", credits: 2 },
  { provider: "writer", model: "palmyra-med",   name: "Palmyra Med",   category: "flagship", credits: 2 },
  // ── HuggingFace ──────────────────────────────────────────────────────────
  { provider: "huggingface", model: "meta-llama/Llama-3.3-70B-Instruct", name: "Llama 3.3 70B (HF)",      category: "fast",    credits: 1 },
  { provider: "huggingface", model: "Qwen/Qwen2.5-72B-Instruct",          name: "Qwen 2.5 72B (HF)",       category: "fast",    credits: 1 },
  // ── Meta Llama API ────────────────────────────────────────────────────────
  { provider: "llama", model: "Llama-4-Maverick-17B-128E-Instruct-FP8", name: "Llama 4 Maverick (Meta)", category: "fast",    credits: 1 },
  { provider: "llama", model: "Llama-4-Scout-17B-16E-Instruct",          name: "Llama 4 Scout (Meta)",    category: "economy", credits: 1 },
  { provider: "llama", model: "Llama-3.3-70B-Instruct",                  name: "Llama 3.3 70B (Meta)",    category: "fast",    credits: 1 },
  // ── Novita AI ─────────────────────────────────────────────────────────────
  { provider: "novita", model: "meta-llama/llama-4-maverick-17b-128e-instruct", name: "Llama 4 Maverick (Novita)", category: "fast",     credits: 1 },
  { provider: "novita", model: "deepseek-ai/deepseek-r1",                       name: "DeepSeek R1 (Novita)",      category: "reasoning",credits: 2 },
  { provider: "novita", model: "meta-llama/llama-3.1-405b-instruct",            name: "Llama 3.1 405B (Novita)",   category: "flagship", credits: 2 },
  // ── Lepton AI ─────────────────────────────────────────────────────────────
  { provider: "lepton", model: "llama4-maverick", name: "Llama 4 Maverick (Lepton)", category: "fast",     credits: 1 },
  { provider: "lepton", model: "deepseek-r1",     name: "DeepSeek R1 (Lepton)",      category: "reasoning",credits: 2 },
  // ── Lambda Labs ───────────────────────────────────────────────────────────
  { provider: "lambda", model: "llama4-maverick-instruct",     name: "Llama 4 Maverick (Lambda)", category: "fast",     credits: 1 },
  { provider: "lambda", model: "hermes3-405b",                  name: "Hermes 3 405B (Lambda)",    category: "flagship", credits: 2 },
  { provider: "lambda", model: "deepseek-r1-671b",              name: "DeepSeek R1 (Lambda)",      category: "reasoning",credits: 3 },
  // ── Minimax AI ────────────────────────────────────────────────────────────
  { provider: "minimax", model: "MiniMax-M2",   name: "MiniMax M2",    category: "flagship", credits: 2 },
  { provider: "minimax", model: "MiniMax-M1",   name: "MiniMax M1",    category: "flagship", credits: 2 },
  { provider: "minimax", model: "MiniMax-01",   name: "MiniMax-01",    category: "fast",     credits: 1 },
  // ── Inception AI ─────────────────────────────────────────────────────────
  { provider: "inception", model: "mercury-2",     name: "Mercury 2",         category: "fast", credits: 1 },
  { provider: "inception", model: "mercury-coder", name: "Mercury Coder",     category: "code", credits: 1 },
  // ── Arcee AI ─────────────────────────────────────────────────────────────
  { provider: "arcee", model: "maestro-reasoning", name: "Arcee Maestro",        category: "reasoning", credits: 2 },
  { provider: "arcee", model: "virtuoso-large",    name: "Arcee Virtuoso Large", category: "flagship",  credits: 2 },
  { provider: "arcee", model: "spotlight",          name: "Arcee Spotlight",      category: "fast",      credits: 1 },
  // ── Amazon Bedrock ────────────────────────────────────────────────────────
  { provider: "amazon", model: "us.amazon.nova-pro-v1:0",    name: "Nova Pro (Amazon)",     category: "flagship", credits: 2 },
  { provider: "amazon", model: "us.amazon.nova-lite-v1:0",   name: "Nova Lite (Amazon)",    category: "fast",     credits: 1 },
  { provider: "amazon", model: "us.amazon.nova-micro-v1:0",  name: "Nova Micro (Amazon)",   category: "economy",  credits: 1 },
];

import NotificationCenter from "../components/NotificationCenter";
import AgentCustomizePanel from "../components/AgentCustomizePanel";
import MarkdownRenderer from "../components/MarkdownRenderer";
import { ChatSearch } from "../components/chat/ChatSearch";
import { Pin, Download as DownloadIcon, Copy, Check } from "lucide-react";
import AgentAvatar from "../components/AgentAvatar";

// Commander Group Chat Component - renders delegation as individual agent chat bubbles
const CommanderGroupChat = ({ msg, msgIndex, generatedFiles, generateFile, generatingFile, currentAgent }) => {
  const data = msg.delegation_data;
  const priorityColors = {
    high: "bg-red-500/20 text-red-400 border-red-500/30",
    medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  };

  return (
    <div className="space-y-3" data-testid={`commander-group-${msgIndex}`}>
      {/* Commander header card */}
      <div className="flex gap-3" data-testid={`message-${msgIndex}`}>
        <img
          src={currentAgent?.avatar}
          alt="Commander"
          className="w-8 h-8 rounded-lg object-cover flex-shrink-0"
        />
        <div className="flex-1 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-amber-400 text-sm">Commander Orion</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">MISSION BRIEFING</span>
          </div>
          <p className="text-zinc-200 text-sm font-medium mb-1">Goal: {data.goal}</p>
          <p className="text-zinc-400 text-xs">{data.task_count} specialists deployed &middot; {data.task_count} tasks created</p>
          
          {/* Agent avatars row */}
          <div className="flex items-center gap-1 mt-3">
            {data.agents.map((a, idx) => (
              <div key={idx} className="relative group">
                <img
                  src={a.agent_avatar}
                  alt={a.agent_name}
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-zinc-800 -ml-1 first:ml-0 hover:ring-indigo-500 transition-all hover:z-10 hover:scale-110"
                  title={a.agent_name}
                />
              </div>
            ))}
            <span className="text-xs text-zinc-500 ml-2">{data.agents.length} active</span>
          </div>
        </div>
      </div>

      {/* Individual agent responses */}
      {data.agents.map((agent, idx) => (
        <div key={idx} className="flex gap-3 ml-6 animate-in fade-in slide-in-from-left-2" style={{ animationDelay: `${idx * 100}ms` }} data-testid={`delegation-agent-${idx}`}>
          <div className="relative flex-shrink-0">
            <img
              src={agent.agent_avatar}
              alt={agent.agent_name}
              className="w-8 h-8 rounded-lg object-cover"
            />
            <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-900 ${agent.status === "completed" ? "bg-emerald-500" : "bg-red-500"}`} />
          </div>
          <div className="flex-1 rounded-xl bg-zinc-800/60 border border-white/5 p-4 hover:border-white/10 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">{agent.agent_name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-zinc-400">{agent.agent_role}</span>
              </div>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${priorityColors[agent.priority]}`}>
                {agent.priority.toUpperCase()}
              </span>
            </div>
            <div className="text-xs text-indigo-300/80 mb-2 flex items-center gap-1">
              <ListTodo className="w-3 h-3" />
              {agent.task_title || agent.task}
            </div>
            <MarkdownRenderer content={agent.response} />
          </div>
        </div>
      ))}

      {/* Commander summary footer */}
      <div className="flex gap-3 ml-6">
        <div className="w-8 flex-shrink-0 flex justify-center">
          <div className="w-px h-full bg-amber-500/20" />
        </div>
        <div className="flex-1 rounded-lg bg-zinc-900/50 border border-white/5 p-3">
          <p className="text-xs text-zinc-400">
            All specialists have reported. <span className="text-amber-400 font-medium">{data.task_count} tasks</span> auto-created on your Tasks page.
          </p>
        </div>
      </div>
    </div>
  );
};

// Execution Steps Component - shows agent's reasoning and tool usage
const ExecutionSteps = ({ steps, onSaveProduct }) => {
  const [expanded, setExpanded] = useState(false);
  if (!steps || steps.length === 0) return null;
  
  const toolIcons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Mail, product_scan: Scan, query_tasks: ClipboardList, update_task: ClipboardList, query_agent_history: Users };
  const toolLabels = { web_search: "Web Search", calculate: "Calculate", create_task: "Create Task", analyze_data: "Analyze Data", send_slack: "Slack Message", send_email: "Send Email", send_sms: "Send SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIF Search", schedule_meeting: "Schedule", google_calendar: "Calendar", send_gmail: "Gmail", product_scan: "Product Scanner", query_tasks: "Query Tasks", update_task: "Update Task", query_agent_history: "Agent History" };
  
  return (
    <div className="mb-2" data-testid="execution-steps">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-amber-400/80 hover:text-amber-300 transition-colors"
        data-testid="toggle-execution-steps"
      >
        <Brain className="w-3 h-3" />
        <span className="font-medium">{steps.length} reasoning step{steps.length > 1 ? 's' : ''}</span>
        {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>
      {expanded && (
        <div className="mt-2 space-y-1.5 pl-2 border-l-2 border-amber-500/20">
          {steps.map((step, idx) => {
            if (step.step_type === "thinking") {
              return (
                <div key={idx} className="flex items-start gap-2 text-xs" data-testid={`step-thinking-${idx}`}>
                  <Brain className="w-3 h-3 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-zinc-400 italic">{step.content}</p>
                </div>
              );
            }
            if (step.step_type === "tool_call") {
              const ToolIcon = toolIcons[step.tool_name] || Wrench;
              return (
                <div key={idx} className="flex items-start gap-2 text-xs" data-testid={`step-tool-call-${idx}`}>
                  <Zap className="w-3 h-3 text-amber-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-amber-400 font-medium">Using {toolLabels[step.tool_name] || step.tool_name}</span>
                    <span className="text-zinc-500 ml-1">
                      {step.tool_input?.query || step.tool_input?.expression || step.tool_input?.title || step.tool_input?.product_query || ''}
                    </span>
                  </div>
                </div>
              );
            }
            if (step.step_type === "tool_result") {
              // Special rendering for product_scan results
              const isProductScan = steps[idx - 1]?.tool_name === "product_scan" || (step.content && step.content.includes("PRODUCT SCAN RESULTS"));
              if (isProductScan && step.content) {
                const imageUrls = [];
                const urlRegex = /Image \d+: (https?:\/\/[^\s]+)/g;
                let match;
                while ((match = urlRegex.exec(step.content)) !== null) {
                  imageUrls.push(match[1]);
                }
                const productName = step.content.match(/PRODUCT SCAN RESULTS: (.+?)===/) ?
                  step.content.match(/PRODUCT SCAN RESULTS: (.+?)===/)[1].trim() : "Product";

                return (
                  <div key={idx} className="rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 p-3" data-testid={`product-scan-result-${idx}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Scan className="w-4 h-4 text-indigo-400" />
                        <span className="text-indigo-300 font-semibold text-xs">Product Identified: {productName}</span>
                      </div>
                      {onSaveProduct && (
                        <button
                          onClick={() => onSaveProduct(productName, imageUrls, step.content)}
                          className="flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-500/20 text-emerald-400 text-[10px] font-medium hover:bg-emerald-500/30 transition-colors"
                          data-testid="save-to-catalog-btn"
                        >
                          <Package className="w-3 h-3" />Save to Catalog
                        </button>
                      )}
                    </div>
                    {imageUrls.length > 0 && (
                      <div className="flex gap-2 mb-2 overflow-x-auto pb-1">
                        {imageUrls.slice(0, 4).map((url, imgIdx) => (
                          <img
                            key={imgIdx}
                            src={url}
                            alt={`Reference ${imgIdx + 1}`}
                            className="w-16 h-16 rounded-md object-cover border border-white/10 flex-shrink-0"
                            onError={(e) => e.target.style.display = 'none'}
                          />
                        ))}
                      </div>
                    )}
                    <p className="text-emerald-400/80 font-mono text-[10px] leading-relaxed whitespace-pre-wrap line-clamp-6">{step.content.replace(/Image \d+: https?:\/\/[^\s]+/g, '').slice(0, 500)}</p>
                  </div>
                );
              }
              return (
                <div key={idx} className="text-xs p-2 rounded bg-white/5 border border-white/5" data-testid={`step-tool-result-${idx}`}>
                  <p className="text-emerald-400/80 font-mono text-[10px] leading-relaxed whitespace-pre-wrap line-clamp-4">{step.content}</p>
                </div>
              );
            }
            return null;
          })}
        </div>
      )}
    </div>
  );
};

const AgentChat = () => {
  const navigate = useNavigate();
  const { agentId } = useParams();
  const [searchParams] = useSearchParams();
  const chatIdParam = searchParams.get("chat");
  
  const { user, logout, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [showSearch, setShowSearch] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [selectedModel, setSelectedModel] = useState("auto/auto");
  const [chatModels, setChatModels] = useState(AVAILABLE_MODELS);
  const [modelSearch, setModelSearch] = useState("");
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [routerQuality, setRouterQuality] = useState("auto");   // auto | economy | standard | premium
  const [routerTaskHint, setRouterTaskHint] = useState("auto"); // auto | code | math | reasoning | creative | translation | summary | research | data | chat
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [generatingFile, setGeneratingFile] = useState(null);
  const [generatedFiles, setGeneratedFiles] = useState({});
  const [ttsPlaying, setTtsPlaying] = useState(null);
  const [ttsLoading, setTtsLoading] = useState(null);
  const [feedbackState, setFeedbackState] = useState({});
  const [showCustomize, setShowCustomize] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const dragCounterRef = useRef(0);
  const ttsAudioRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const resizeRef = useRef(null);
  const textareaRef = useRef(null);

  // Sidebar resize handlers
  const startResize = (e) => {
    e.preventDefault();
    setIsResizing(true);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  // Fetch full model list from gateway API
  useEffect(() => {
    fetch(`${API}/v1/models`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (!d?.data?.length) return;
        const mapped = d.data.map(m => {
          const parts = m.id.split("/");
          const modelPart = parts.slice(1).join("/");
          // Derive a readable name from the model id
          const rawName = modelPart || m.id;
          const name = rawName
            .replace(/[-_]/g, " ")
            .replace(/\b(\w)/g, c => c.toUpperCase())
            .replace(/\b(\d+)b\b/gi, "$1B")
            .replace(/\bGpt\b/g, "GPT").replace(/\bLlm\b/g, "LLM")
            .replace(/\bLlama\b/g, "Llama").replace(/\bGemma\b/g, "Gemma")
            .replace(/\bDeepseek\b/g, "DeepSeek").replace(/\bQwen\b/g, "Qwen")
            .replace(/\bGrok\b/g, "Grok").replace(/\bMistral\b/g, "Mistral")
            .replace(/\bPhi\b/g, "Phi").replace(/\bNova\b/g, "Nova")
            .replace(/\bGlm\b/g, "GLM").replace(/\bVl\b/g, "VL")
            .replace(/\bMoe\b/g, "MoE").replace(/\bFp8\b/g, "FP8")
            .replace(/\bA(\d+)B\b/g, "A$1B")
            .trim();
          // Infer category from description/id
          const d2 = (m.description || "").toLowerCase();
          const id2 = m.id.toLowerCase();
          let category = "fast";
          if (m.is_maars_router) category = "auto";
          else if (/reason|r1|o4|o3|qwq|think/i.test(id2 + d2)) category = "reasoning";
          else if (/vision|vl|pixtral|llava|idefics/i.test(id2 + d2)) category = "vision";
          else if (/code|coder|starcoder|codestral/i.test(id2 + d2)) category = "code";
          else if (/sonar|search|perplexity/i.test(id2 + d2)) category = "search";
          else if (/opus|gpt-5|pro|large|max|ultra|405b|235b|70b/i.test(id2 + d2)) category = "flagship";
          else if (/nano|mini|tiny|small|1b|3b|7b|8b|lite/i.test(id2 + d2)) category = "economy";
          return {
            provider: m.provider,
            model: modelPart,
            name,
            category,
            credits: m.credits_per_call || 1,
            available: m.available !== false,
          };
        });
        setChatModels(mapped);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = Math.min(Math.max(e.clientX, 200), 600);
      setSidebarWidth(newWidth);
    };
    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const playTTS = async (msgId, text) => {
    if (ttsPlaying === msgId) {
      if (ttsAudioRef.current) { ttsAudioRef.current.pause(); ttsAudioRef.current = null; }
      setTtsPlaying(null);
      return;
    }
    setTtsLoading(msgId);
    try {
      const res = await fetch(`${API}/tts/generate`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.substring(0, 4000), voice: "nova" })
      });
      if (!res.ok) { const e = await res.json(); toast.error(e.detail || "TTS failed"); return; }
      const data = await res.json();
      if (ttsAudioRef.current) ttsAudioRef.current.pause();
      const audio = new Audio(data.audio_url);
      ttsAudioRef.current = audio;
      audio.onended = () => { setTtsPlaying(null); ttsAudioRef.current = null; };
      audio.play();
      setTtsPlaying(msgId);
    } catch { toast.error("TTS not available"); }
    finally { setTtsLoading(null); }
  };

  // Initialize feedback state from loaded messages
  const initFeedback = (msgs) => {
    const fb = {};
    msgs.forEach(m => { if (m.feedback) fb[m.message_id] = m.feedback; });
    setFeedbackState(fb);
  };

  const submitFeedback = async (chatId, messageId, type) => {
    const current = feedbackState[messageId];
    const newFeedback = current === type ? null : type;
    setFeedbackState(prev => ({ ...prev, [messageId]: newFeedback }));
    try {
      await fetch(`${API}/chats/${chatId}/messages/${messageId}/feedback`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ feedback: newFeedback })
      });
    } catch {}
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (agentId && agents.length > 0) {
      const agent = agents.find(a => a.agent_id === agentId);
      if (agent) {
        setSelectedAgent(agent);
        if (chatIdParam) {
          loadChat(chatIdParam);
        }
      }
    }
  }, [agentId, agents, chatIdParam]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Poll for background video generation completion
  useEffect(() => {
    const hasGenerating = messages.some(m => m.video_generating && !m.generated_video);
    const activeChatId = currentChat?.chat_id;
    if (!hasGenerating || !activeChatId) return;
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/chats/${activeChatId}`, { headers });
        if (res.ok) {
          const chat = await res.json();
          const updated = chat.messages || [];
          const changed = updated.some(m => m.generated_video && !m.video_generating);
          if (changed) {
            setMessages(updated);
            updated.forEach(m => {
              if (m.generated_video) {
                setGeneratedFiles(prev => ({ ...prev, [`${m.message_id}_video`]: m.generated_video }));
              }
            });
          }
          if (!updated.some(m => m.video_generating)) clearInterval(interval);
        }
      } catch {}
    }, 10000);
    
    return () => clearInterval(interval);
  }, [messages, currentChat]);

  // Poll for Commander delegation completion and progress
  useEffect(() => {
    const hasProcessing = messages.some(m => m.commander_status === "processing");
    const activeChatId = currentChat?.chat_id;
    if (!hasProcessing || !activeChatId) return;
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/chats/${activeChatId}`, { headers });
        if (res.ok) {
          const chat = await res.json();
          const updated = chat.messages || [];
          const complete = updated.some(m => m.commander_status === "complete" || m.commander_status === "error");
          // Always update messages to show live progress
          setMessages(updated);
          if (complete) {
            clearInterval(interval);
          }
        }
      } catch {}
    }, 3000);
    
    return () => clearInterval(interval);
  }, [messages.some(m => m.commander_status === "processing"), currentChat?.chat_id]);


  const fetchInitialData = async () => {
    try {
      const [agentsRes, chatsRes] = await Promise.all([
        fetch(`${API}/agents`, { headers }),
        fetch(`${API}/chats`, { headers })
      ]);

      if (agentsRes.ok) {
        const agentsData = await agentsRes.json();
        setAgents(agentsData);
        if (!agentId && agentsData.length > 0) {
          setSelectedAgent(agentsData[0]);
        }
      }
      if (chatsRes.ok) {
        const data = await chatsRes.json();
        setChats(data.chats || data);
      }
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const loadChat = async (chatId) => {
    try {
      const response = await fetch(`${API}/chats/${chatId}`, { headers
      });
      if (response.ok) {
        const chat = await response.json();
        setCurrentChat(chat);
        const msgs = chat.messages || [];
        setMessages(msgs);
        initFeedback(msgs);
        // Pre-populate generatedFiles from loaded messages (for videos/images completed in background)
        const filesFromMsgs = {};
        msgs.forEach(m => {
          if (m.generated_video) filesFromMsgs[`${m.message_id}_video`] = m.generated_video;
          if (m.generated_image) filesFromMsgs[`${m.message_id}_image`] = m.generated_image;
          if (m.generated_file) filesFromMsgs[`${m.message_id}_file`] = m.generated_file;
        });
        if (Object.keys(filesFromMsgs).length > 0) {
          setGeneratedFiles(prev => ({ ...prev, ...filesFromMsgs }));
        }
        const agent = agents.find(a => a.agent_id === chat.agent_id);
        if (agent) setSelectedAgent(agent);
      }
    } catch (error) {
      toast.error("Failed to load chat");
    }
  };

  const startNewChat = async () => {
    if (!selectedAgent) return;
    
    try {
      const response = await fetch(`${API}/chats`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ agent_id: selectedAgent.agent_id })
      });

      if (response.ok) {
        const chat = await response.json();
        setCurrentChat(chat);
        setMessages([]);
        setChats(prev => [chat, ...prev]);
        navigate(`/chat/${selectedAgent.agent_id}?chat=${chat.chat_id}`, { replace: true });
      }
    } catch (error) {
      toast.error("Failed to create chat");
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    // Create chat if needed
    let chatId = currentChat?.chat_id;
    if (!chatId) {
      try {
        const response = await fetch(`${API}/chats`, {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ agent_id: selectedAgent.agent_id })
        });
        if (response.ok) {
          const chat = await response.json();
          chatId = chat.chat_id;
          setCurrentChat(chat);
          setChats(prev => [chat, ...prev]);
        } else {
          toast.error("Failed to create chat");
          return;
        }
      } catch (error) {
        toast.error("Failed to create chat");
        return;
      }
    }

    setSending(true);
    const [provider, model] = selectedModel.split("/");
    const isAuto = provider === "auto";
    const userMessage = { role: "user", 
      content: input, 
      message_id: `temp_${Date.now()}`,
      attachments: attachments.map(a => a.preview),
      attachment_files: attachments.filter(a => a.file_url).map(a => ({ file_url: a.file_url, type: a.type, filename: a.filename })),
      model_used: isAuto ? "Auto-selecting..." : selectedModel,
      auto_selected: isAuto
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setAttachments([]);
    if (textareaRef.current) textareaRef.current.style.height = "40px";

    try {
      const response = await fetch(`${API}/chats/${chatId}/messages`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ content: userMessage.content,
          model_provider: isAuto ? "auto" : provider,
          model_name: isAuto ? "auto" : model,
          quality_tier: isAuto ? routerQuality : null,
          task_hint: isAuto && routerTaskHint !== "auto" ? routerTaskHint : null,
          attachments: userMessage.attachments,
          attachment_files: userMessage.attachment_files
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Attach credits_deducted to assistant message for display
        const assistantMsg = data.assistant_message;
        if (data.credits_deducted) {
          assistantMsg.credits_deducted = data.credits_deducted;
        }
        setMessages(prev => [
          ...prev.slice(0, -1),
          data.user_message,
          assistantMsg
        ]);
        // Auto-store generated image if present
        if (data.generated_image && data.assistant_message?.message_id) {
          const imgKey = `${data.assistant_message.message_id}_image`;
          setGeneratedFiles(prev => ({ ...prev, [imgKey]: data.generated_image }));
        }
        // Auto-store generated video if present
        if (data.generated_video && data.assistant_message?.message_id) {
          const vidKey = `${data.assistant_message.message_id}_video`;
          setGeneratedFiles(prev => ({ ...prev, [vidKey]: data.generated_video }));
        }
        // Auto-store generated file if present
        if (data.generated_file && data.assistant_message?.message_id) {
          const fileKey = `${data.assistant_message.message_id}_file`;
          setGeneratedFiles(prev => ({ ...prev, [fileKey]: data.generated_file }));
        }
        // Show toast if auto-selected
        if (data.auto_selected && data.model_reason) {
          toast.success(`Smart Selection: ${data.model_used} - ${data.model_reason}`);
        }
        // Update chat title in list if it changed
        setChats(prev => prev.map(c => 
          c.chat_id === chatId 
            ? { ...c, title: data.user_message.content.slice(0, 50) }
            : c
        ));
      } else {
        toast.error("Failed to send message");
        setMessages(prev => prev.slice(0, -1));
      }
    } catch (error) {
      toast.error("Failed to send message");
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API}/upload`, {
          method: "POST",
          headers: headers, body: formData
        });

        if (response.ok) {
          const data = await response.json();
          setAttachments(prev => [...prev, {
            filename: data.filename,
            type: data.content_type,
            size: data.size,
            preview: data.data_url,
            file_url: data.file_url
          }]);
          toast.success(`${file.name} uploaded`);
        } else {
          toast.error(`Failed to upload ${file.name}`);
        }
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Drag-and-drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current--;
    if (dragCounterRef.current === 0) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    dragCounterRef.current = 0;

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    setUploading(true);
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API}/upload`, {
          method: "POST",
          headers: headers,
          body: formData
        });
        if (response.ok) {
          const data = await response.json();
          setAttachments(prev => [...prev, {
            filename: data.filename,
            type: data.content_type,
            size: data.size,
            preview: data.data_url,
            file_url: data.file_url
          }]);
          toast.success(`${file.name} uploaded`);
        } else {
          toast.error(`Failed to upload ${file.name}`);
        }
      } catch {
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    setUploading(false);
  };


  const saveProductToCatalog = async (name, imageUrls, scanContent) => {
    try {
      const images = imageUrls.map(url => ({ url, thumbnail: url, title: name }));
      const res = await fetch(`${API}/products`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          images,
          scan_data: { context: scanContent },
          source_chat_id: currentChat?.chat_id,
        })
      });
      if (res.ok) {
        toast.success("Product saved to catalog!");
      } else {
        toast.error("Failed to save product");
      }
    } catch { toast.error("Failed to save product"); }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await transcribeAudio(audioBlob);
      };
      
      mediaRecorder.start();
      setRecording(true);
    } catch {
      toast.error("Microphone access denied. Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setTranscribing(true);
    try {
      const formData = new FormData();
      formData.append("audio_file", audioBlob, "recording.webm");
      
      const response = await fetch(`${API}/audio/speech-to-text`, {
        method: "POST",
        headers: { ...headers }, body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.text) {
          setInput(prev => prev ? `${prev} ${data.text}` : data.text);
          toast.success("Voice transcribed!");
        } else {
          toast.error("No speech detected");
        }
      } else {
        toast.error("Transcription failed");
      }
    } catch {
      toast.error("Transcription failed");
    } finally {
      setTranscribing(false);
    }
  };

  const generateFile = async (type, content, msgId, title) => {
    const key = `${msgId}_${type}`;
    setGeneratingFile(key);
    try {
      let endpoint = `${API}/generate/document`;
      let body = { type, title: title || "Generated File", content };
      
      if (type === "image") {
        endpoint = `${API}/generate/image`;
        body = { prompt: content, model: "gpt-image-1" };
      } else if (type === "video") {
        endpoint = `${API}/generate/video`;
        body = { prompt: content, model: "sora-2", duration: 4 };
      } else if (type === "xlsx") {
        // Try to parse content as table data
        const lines = content.split("\n").filter(l => l.trim());
        const rows = lines.map(l => l.split(/[,\t|]/).map(c => c.trim()));
        body = { type: "xlsx", title: title || "Spreadsheet", content, rows };
      }
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify(body)
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedFiles(prev => ({ ...prev, [key]: data }));
        toast.success(`${type.toUpperCase()} file generated!`);
      } else {
        const err = await response.json().catch(() => ({}));
        toast.error(err.detail || `${type} generation failed`);
      }
    } catch {
      toast.error(`${type} generation failed`);
    } finally {
      setGeneratingFile(null);
    }
  };

  const FileGenButtons = ({ content, msgId }) => {
    const truncated = content?.slice(0, 500) || "";
    return (
      <div className="flex flex-wrap gap-1.5 mt-2">
        {[
          { type: "pdf", icon: FileText, label: "PDF", color: "text-red-400 bg-red-500/10 hover:bg-red-500/20" },
          { type: "docx", icon: File, label: "Word", color: "text-blue-400 bg-blue-500/10 hover:bg-blue-500/20" },
          { type: "xlsx", icon: FileSpreadsheet, label: "Excel", color: "text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20" },
          { type: "txt", icon: FileText, label: "Text", color: "text-zinc-400 bg-zinc-500/10 hover:bg-zinc-500/20" },
          { type: "image", icon: Image, label: "Image", color: "text-rose-400 bg-rose-500/10 hover:bg-rose-500/20" },
          { type: "video", icon: Film, label: "Video", color: "text-violet-400 bg-violet-500/10 hover:bg-violet-500/20" },
        ].map(({ type, icon: Icon, label, color }) => {
          const key = `${msgId}_${type}`;
          const file = generatedFiles[key];
          const isGenerating = generatingFile === key;
          
          if (file) {
            return (
              <a
                key={type}
                href={file.preview || `${API}${file.url}`}
                target="_blank"
                rel="noopener noreferrer"
                download={file.filename}
                className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium ${color} border border-white/5`}
                data-testid={`download-${type}-${msgId}`}
              >
                <Download className="w-3 h-3" />
                {label}
              </a>
            );
          }
          
          return (
            <button
              key={type}
              onClick={() => generateFile(type, truncated, msgId, `${selectedAgent?.name || "Agent"} Output`)}
              disabled={isGenerating}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium transition-colors ${color} border border-white/5`}
              data-testid={`gen-${type}-${msgId}`}
            >
              {isGenerating ? <div style={{ width: 11, height: 11, border: "1.5px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "ac_spin .8s linear infinite" }} /> : <Icon size={11} />}
              {isGenerating ? "..." : label}
            </button>
          );
        })}
      </div>
    );
  };

  const deleteChat = async (chatId) => {
    try {
      const response = await fetch(`${API}/chats/${chatId}`, {
        method: "DELETE", headers
      });

      if (response.ok) {
        setChats(prev => prev.filter(c => c.chat_id !== chatId));
        if (currentChat?.chat_id === chatId) {
          setCurrentChat(null);
          setMessages([]);
        }
        toast.success("Chat deleted");
      }
    } catch (error) {
      toast.error("Failed to delete chat");
    }
  };

  const shareChat = async () => {
    if (!currentChat) return;
    try {
      const res = await fetch(`${API}/chats/${currentChat.chat_id}/share`, { method: "POST", headers });
      if (res.ok) {
        const data = await res.json();
        toast.success(data.shared ? "Chat shared with team" : "Chat unshared from team");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to share");
      }
    } catch { toast.error("Failed to share chat"); }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active 
          ? "bg-indigo-500/20 text-indigo-400" 
          : "text-zinc-400 hover:bg-white/5 hover:text-white"
      }`}
      data-testid={`nav-${label.toLowerCase()}`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-[100vh] lg:h-screen bg-background flex overflow-hidden" data-testid="chat-page">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <button onClick={() => setSidebarOpen(true)} className="p-2 text-zinc-400">
            <Menu className="w-6 h-6" />
          </button>
          <span className="font-semibold text-white">
            {selectedAgent?.name || "Chat"}
          </span>
          <button onClick={startNewChat} style={{ background: "none", border: "none", cursor: "pointer", color: "#818cf8", display: "flex", padding: 4 }} data-testid="mobile-new-chat-btn">
            <Plus size={20} />
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-zinc-900 border-r border-white/[0.08] flex flex-col">
            <div className="flex items-center justify-between p-3 border-b border-white/[0.06]">
              <span className="text-sm font-semibold text-white">Chats</span>
              <button onClick={() => setSidebarOpen(false)} className="p-1.5 text-zinc-500 hover:text-white rounded-lg hover:bg-white/[0.04]">
                <X className="w-4 h-4" />
              </button>
            </div>
            <SidebarContent 
              agents={agents}
              chats={chats}
              selectedAgent={selectedAgent}
              setSelectedAgent={setSelectedAgent}
              currentChat={currentChat}
              loadChat={loadChat}
              deleteChat={deleteChat}
              startNewChat={startNewChat}
              navigate={navigate}
            />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex flex-col bg-zinc-900/50 border-r border-white/[0.08] relative" style={{ width: sidebarWidth, minWidth: 200, maxWidth: 600 }}>
        <div className="p-3 border-b border-white/[0.06]">
          <button onClick={startNewChat} data-testid="new-chat-btn"
            style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 7, padding: "8px 0", borderRadius: 9, border: "none", background: "linear-gradient(135deg, #818cf8, #7c3aed)", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
            <Plus size={15} /> New Chat
          </button>
          <button onClick={() => setShowSearch(!showSearch)} data-testid="chat-search-btn"
            style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 7, padding: "6px 0", borderRadius: 8, border: "1px solid rgba(255,255,255,0.08)", background: "transparent", color: "#71717a", fontSize: 12, cursor: "pointer", marginTop: 6 }}>
            <Search size={13} /> Search Chats
          </button>
        </div>
        {showSearch && (
          <ChatSearch
            onSelectChat={(chatId, agentId) => {
              const agent = agents.find(a => a.agent_id === agentId);
              if (agent) setSelectedAgent(agent);
              loadChat(chatId);
            }}
            onClose={() => setShowSearch(false)}
          />
        )}
        <SidebarContent 
          agents={agents}
          chats={chats}
          selectedAgent={selectedAgent}
          setSelectedAgent={setSelectedAgent}
          currentChat={currentChat}
          loadChat={loadChat}
          deleteChat={deleteChat}
          startNewChat={startNewChat}
          navigate={navigate}
        />
        {/* Resize Handle */}
        <div
          ref={resizeRef}
          onMouseDown={startResize}
          className="absolute right-0 top-0 bottom-0 w-1.5 cursor-col-resize hover:bg-indigo-500/40 active:bg-indigo-500/60 transition-colors z-10"
          data-testid="sidebar-resize-handle"
        />
      </div>

      {/* Main Chat Area */}
      <div
        className="flex-1 flex flex-col h-screen pt-16 lg:pt-0 overflow-hidden relative"
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {/* Drag-and-drop overlay */}
        {isDragging && (
          <div className="absolute inset-0 z-40 bg-indigo-500/10 backdrop-blur-sm border-2 border-dashed border-indigo-500 rounded-xl flex items-center justify-center" data-testid="drag-drop-overlay">
            <div className="text-center">
              <Image className="w-12 h-12 text-indigo-400 mx-auto mb-3 animate-bounce" />
              <p className="text-lg font-semibold text-indigo-300">Drop files here</p>
              <p className="text-sm text-zinc-400 mt-1">Images, PDFs, documents — AI will analyze them</p>
            </div>
          </div>
        )}
        {/* Agent Header */}
        {selectedAgent && (
          <div className="hidden lg:flex items-center justify-between px-4 py-3 border-b border-white/[0.06] shrink-0" style={{ background: "rgba(4,8,18,0.5)", backdropFilter: "blur(12px)" }}>
            <div className="flex items-center gap-3">
              <AgentAvatar agent={selectedAgent} size="md" status="online" animate showRing showPulse={sending} />
              <div>
                <h2 className="font-semibold text-white text-sm" style={{ fontFamily: "Outfit, sans-serif" }}>{selectedAgent.name}</h2>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <p className="text-xs text-zinc-500">{selectedAgent.role}</p>
                  {sending && (
                    <div style={{ display: "flex", alignItems: "center", gap: 2 }}>
                      {[0,1,2].map(i => (
                        <div key={i} style={{ width: 3, height: 12, borderRadius: 2, background: "#4fd1c5", animation: `ac_wave 0.8s ease-in-out ${i * 0.12}s infinite alternate`, opacity: 0.8 }} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <button onClick={() => setShowCustomize(!showCustomize)} data-testid="customize-agent-btn"
                style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 7, border: "none", background: showCustomize ? "rgba(129,140,248,.12)" : "transparent", color: showCustomize ? "#818cf8" : "#71717a", fontSize: 12, cursor: "pointer" }}>
                <Settings size={13} />Customize
              </button>
            </div>
            <div className="flex items-center gap-1.5">
              {currentChat && (
                <>
                  <button data-testid="export-chat-btn"
                    onClick={async () => {
                      try {
                        const res = await fetch(`${API}/chats/${currentChat.chat_id}/export`, { headers: { Authorization: `Bearer ${token}` } });
                        const data = await res.json();
                        const blob = new Blob([data.content], { type: "text/plain" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `${data.title || "chat"}_export.txt`;
                        a.click();
                        URL.revokeObjectURL(url);
                        toast.success("Chat exported");
                      } catch { toast.error("Export failed"); }
                    }}
                    style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 10px", borderRadius: 7, border: "none", background: "transparent", color: "#71717a", fontSize: 12, cursor: "pointer" }}>
                    <Download size={13} />Export
                  </button>
                  <button onClick={shareChat} data-testid="share-chat-btn"
                    style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 10px", borderRadius: 7, border: "none", background: "transparent", color: "#71717a", fontSize: 12, cursor: "pointer" }}>
                    <Share2 size={13} />Share
                  </button>
                </>
              )}
            </div>
          </div>
        )}
        {showCustomize && selectedAgent && (
          <AgentCustomizePanel agent={selectedAgent} onClose={() => setShowCustomize(false)} />
        )}

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8" style={{ position: "relative" }}>
              {/* Ambient radial glow */}
              <div style={{ position: "absolute", top: "30%", left: "50%", transform: "translate(-50%,-50%)", width: 320, height: 320, borderRadius: "50%", background: "radial-gradient(circle, rgba(79,209,197,0.04) 0%, transparent 70%)", pointerEvents: "none" }} />
              {selectedAgent && (
                <>
                  <div style={{ marginBottom: 20 }}>
                    <AgentAvatar agent={selectedAgent} size="2xl" status="online" animate showRing showPulse />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-1 font-['Outfit']" style={{ fontFamily: "Outfit, sans-serif" }}>
                    Chat with {selectedAgent.name}
                  </h3>
                  <p className="text-sm text-zinc-500 max-w-sm mb-5">{selectedAgent.description}</p>
                  <div className="flex flex-wrap gap-1.5 justify-center max-w-md">
                    {selectedAgent.capabilities?.map((cap, i) => (
                      <span key={i} className="px-2.5 py-1 text-xs rounded-md bg-white/[0.06] text-zinc-400 border border-white/[0.06]">
                        {cap}
                      </span>
                    ))}
                  </div>
                  {selectedAgent.tools?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 justify-center mt-3 max-w-md" data-testid="agent-chat-tools">
                      <span className="flex items-center gap-1 text-[11px] text-zinc-600 mr-0.5">
                        <Wrench className="w-3 h-3" /> Tools:
                      </span>
                      {selectedAgent.tools.slice(0, 8).map((tool, i) => {
                        const icons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Mail };
                        const labels = { web_search: "Web Search", calculate: "Calculator", create_task: "Task Creator", analyze_data: "Data Analyzer", send_slack: "Slack", send_email: "Email", send_sms: "SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIFs", schedule_meeting: "Calendly", google_calendar: "Calendar", send_gmail: "Gmail" };
                        const Icon = icons[tool] || Wrench;
                        return (
                          <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] rounded-md bg-amber-500/8 text-amber-500/70 border border-amber-500/10">
                            <Icon className="w-2.5 h-2.5" /> {labels[tool] || tool}
                          </span>
                        );
                      })}
                      {selectedAgent.tools.length > 8 && (
                        <span className="text-[11px] text-zinc-600 px-2 py-0.5">+{selectedAgent.tools.length - 8} more</span>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="space-y-4 max-w-3xl mx-auto">
              {messages.map((msg, i) => {
                // Commander delegation group chat rendering
                if (msg.role === "assistant" && msg.delegation_data?.type === "commander_delegation") {
                  return (
                    <CommanderGroupChat 
                      key={msg.message_id || i} 
                      msg={msg} 
                      msgIndex={i}
                      generatedFiles={generatedFiles}
                      generateFile={generateFile}
                      generatingFile={generatingFile}
                      currentAgent={selectedAgent}
                    />
                  );
                }
                
                // Commander processing indicator with live collaboration view
                if (msg.role === "assistant" && msg.commander_status === "processing") {
                  return (
                    <div key={msg.message_id || i} className="flex gap-3" data-testid={`message-${i}`}>
                      {(msg.agent_avatar || selectedAgent?.avatar) ? (
                        <img src={msg.agent_avatar || selectedAgent?.avatar} alt="" className="w-8 h-8 rounded-lg object-cover flex-shrink-0" />
                      ) : (
                        <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center flex-shrink-0 text-[10px] font-bold text-indigo-400">
                          {(selectedAgent?.name || "AI").split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
                        </div>
                      )}
                      <div className="flex-1 max-w-[85%]">
                        {msg.delegation_progress ? (
                          <CollaborationWorkflow
                            progress={msg.delegation_progress}
                            commanderAvatar={msg.agent_avatar || selectedAgent?.avatar}
                          />
                        ) : (
                          <div className="rounded-xl px-4 py-3 bg-zinc-800/50 border border-indigo-500/20">
                            <div className="flex items-center gap-2 mb-2">
                              <div style={{ width:14, height:14, border:"2px solid rgba(129,140,248,.4)", borderTopColor:"#818cf8", borderRadius:"50%", animation:"ac_spin .8s linear infinite" }} />
                              <span className="text-indigo-400 text-sm font-medium">Commander is coordinating specialists...</span>
                            </div>
                            <MarkdownRenderer content={msg.content} className="text-sm" />
                            <p className="text-zinc-500 text-xs mt-2">This usually takes 1-3 minutes. Results will appear automatically.</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                }

                return (
                <div
                  key={msg.message_id || i}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                  data-testid={`message-${i}`}
                >
                  {msg.role === "assistant" && (
                    <div style={{ position: "relative", flexShrink: 0 }}>
                    {(msg.agent_avatar || selectedAgent?.avatar) ? (
                      <img
                        src={msg.agent_avatar || selectedAgent?.avatar}
                        alt=""
                        style={{ width: 32, height: 32, borderRadius: 9, objectFit: "cover", border: "1px solid rgba(79,209,197,0.2)", boxShadow: "0 0 10px rgba(79,209,197,0.15)" }}
                      />
                    ) : (
                      <div style={{ width: 32, height: 32, borderRadius: 9, background: "rgba(79,209,197,0.1)", border: "1px solid rgba(79,209,197,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: "#4fd1c5" }}>
                        {(selectedAgent?.name || "AI").split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
                      </div>
                    )}
                    </div>
                  )}
                  <div
                    className={`max-w-[80%]`}
                    style={{
                      padding: "14px 18px",
                      borderRadius: msg.role === "user" ? "14px 4px 14px 14px" : "4px 14px 14px 14px",
                      background: msg.role === "user"
                        ? "linear-gradient(135deg, rgba(79,209,197,0.15) 0%, rgba(37,99,235,0.12) 100%)"
                        : "linear-gradient(145deg, rgba(10,18,36,0.88) 0%, rgba(8,14,28,0.92) 100%)",
                      border: msg.role === "user"
                        ? "1px solid rgba(79,209,197,0.25)"
                        : "1px solid rgba(255,255,255,0.07)",
                      backdropFilter: "blur(20px)",
                      color: msg.role === "user" ? "#e2e8f0" : "#c8d4e6",
                      boxShadow: msg.role === "user"
                        ? "0 4px 24px rgba(79,209,197,0.10), inset 0 1px 0 rgba(79,209,197,0.12)"
                        : "0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04)",
                    }}
                  >
                    {msg.attachments?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {msg.attachments.map((att, idx) => (
                          att?.startsWith("data:image") ? (
                            <div key={idx} className="relative group">
                              <img src={att} alt="attachment" className="max-w-[200px] max-h-[160px] rounded-lg border border-white/10 object-cover" />
                              {msg.role === "user" && (
                                <div className="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/60 text-[10px] flex items-center gap-1" style={{ color: "#4fd1c5", border: "1px solid rgba(79,209,197,0.2)" }}>
                                  <Sparkles className="w-2.5 h-2.5" /> AI Vision
                                </div>
                              )}
                            </div>
                          ) : (
                            <div key={idx} className="px-3 py-2 bg-white/10 rounded-lg text-xs flex items-center gap-2">
                              <FileText className="w-4 h-4 text-zinc-400" />
                              <span>File attached</span>
                            </div>
                          )
                        ))}
                      </div>
                    )}
                    {msg.role === "assistant" && msg.execution_steps && (
                      <ExecutionSteps steps={msg.execution_steps} onSaveProduct={saveProductToCatalog} />
                    )}
                    {msg.role === "assistant" ? (
                      <MarkdownRenderer content={msg.content} />
                    ) : (
                      <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                    )}
                    {/* Citation pills — rendered when the assistant used
                        RAG retrieval. Data lives on `msg.citations` as
                        an array of {ref, doc_id, page, title, url}. */}
                    {msg.role === "assistant" && Array.isArray(msg.citations) && msg.citations.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {msg.citations.map((c, i) => (
                          <a key={i}
                             href={c.url || "#"}
                             target={c.url ? "_blank" : undefined}
                             rel="noreferrer"
                             className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20 hover:bg-violet-500/20 font-mono"
                             title={`${c.title || c.doc_id || ""}${c.page ? " · p" + c.page : ""}`}>
                            {c.ref || `[${i+1}]`}
                          </a>
                        ))}
                      </div>
                    )}
                    {msg.role === "assistant" && msg.trust?.score !== undefined && msg.trust?.score !== null && (
                      <div className="mt-1 text-[10px] text-zinc-500">
                        trust <span className={msg.trust.score >= 0.7 ? "text-teal-300" : msg.trust.score >= 0.5 ? "text-amber-300" : "text-rose-300"}>{(msg.trust.score * 100).toFixed(0)}%</span>
                        <span className="ml-1 text-zinc-600">({msg.trust.method})</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      {msg.model_used && msg.role === "assistant" && (() => {
                        const prov = msg.model_used.split("/")[0] || "";
                        const pColor = PROVIDER_COLORS[prov] || "#64748b";
                        return (
                          <div className="text-xs text-zinc-500 flex items-center gap-1.5 flex-wrap">
                            <span style={{ width: 6, height: 6, borderRadius: "50%", background: pColor, display: "inline-block", flexShrink: 0, boxShadow: `0 0 5px ${pColor}80` }} />
                            <span style={{ color: pColor, opacity: 0.75, fontWeight: 500 }}>{msg.model_used.split("/").pop()}</span>
                            {msg.auto_selected && msg.model_reason && (
                              <span className="text-indigo-400">· {msg.model_reason}</span>
                            )}
                            {msg.credits_deducted > 0 && (
                              <span className="text-zinc-600">· {msg.credits_deducted}cr</span>
                            )}
                            {msg.web_searched && (
                              <span className="text-cyan-400 flex items-center gap-0.5">· <Globe className="w-3 h-3" /> web</span>
                            )}
                          </div>
                        );
                      })()}
                      {msg.role === "assistant" && (
                        <button
                          onClick={() => playTTS(msg.message_id || i, msg.content)}
                          disabled={ttsLoading === (msg.message_id || i)}
                          className="text-xs text-zinc-500 hover:text-indigo-400 transition-colors flex items-center gap-1 ml-auto"
                          data-testid={`tts-btn-${i}`}
                          title="Read aloud"
                        >
                          {ttsLoading === (msg.message_id || i) ? <div style={{ width:11, height:11, border:"1.5px solid rgba(255,255,255,.3)", borderTopColor:"#fff", borderRadius:"50%", animation:"ac_spin .8s linear infinite" }} /> :
                           ttsPlaying === (msg.message_id || i) ? <VolumeX className="w-3 h-3 text-red-400" /> :
                           <Volume2 className="w-3 h-3" />}
                        </button>
                      )}
                      {msg.role === "assistant" && msg.message_id && (
                        <div className="flex items-center gap-1 ml-2 border-l border-white/10 pl-2">
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(msg.content);
                              toast.success("Copied to clipboard");
                            }}
                            className="p-1 rounded text-zinc-600 hover:text-white hover:bg-white/10 transition-colors"
                            data-testid={`copy-msg-${i}`}
                            title="Copy message"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                await fetch(`${API}/chats/${currentChat?.chat_id}/messages/${msg.message_id}/pin`, {
                                  method: "POST", headers: { Authorization: `Bearer ${token}` }
                                });
                                const msgs = [...messages];
                                msgs[i] = { ...msgs[i], pinned: !msgs[i].pinned };
                                setMessages(msgs);
                                toast.success(msgs[i].pinned ? "Message pinned" : "Message unpinned");
                              } catch {}
                            }}
                            className={`p-1 rounded transition-colors ${msg.pinned ? "text-amber-400 bg-amber-500/15" : "text-zinc-600 hover:text-amber-400 hover:bg-amber-500/10"}`}
                            data-testid={`pin-msg-${i}`}
                            title={msg.pinned ? "Unpin" : "Pin message"}
                          >
                            <Pin className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => submitFeedback(currentChat?.chat_id, msg.message_id, "up")}
                            className={`p-1 rounded transition-colors ${feedbackState[msg.message_id] === "up" ? "text-emerald-400 bg-emerald-500/15" : "text-zinc-600 hover:text-emerald-400 hover:bg-emerald-500/10"}`}
                            data-testid={`feedback-up-${i}`}
                            title="Good response"
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => submitFeedback(currentChat?.chat_id, msg.message_id, "down")}
                            className={`p-1 rounded transition-colors ${feedbackState[msg.message_id] === "down" ? "text-red-400 bg-red-500/15" : "text-zinc-600 hover:text-red-400 hover:bg-red-500/10"}`}
                            data-testid={`feedback-down-${i}`}
                            title="Poor response"
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                    {/* Generated file preview */}
                    {msg.role === "assistant" && (() => {
                      const imgKey = `${msg.message_id || i}_image`;
                      const vidKey = `${msg.message_id || i}_video`;
                      const fileKey = `${msg.message_id || i}_file`;
                      const imgFile = generatedFiles[imgKey] || msg.generated_image;
                      const vidFile = generatedFiles[vidKey] || msg.generated_video;
                      const docFile = generatedFiles[fileKey] || msg.generated_file;
                      const formatIcons = { pdf: "text-red-400 bg-red-500/10 border-red-500/30", docx: "text-blue-400 bg-blue-500/10 border-blue-500/30", xlsx: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30", csv: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30", txt: "text-zinc-400 bg-zinc-500/10 border-zinc-500/30" };
                      return (
                        <>
                          {docFile?.url && (
                            <div className={`mt-3 rounded-xl border p-4 max-w-sm flex items-center gap-3 ${formatIcons[docFile.format] || "text-zinc-400 bg-zinc-500/10 border-white/10"}`} data-testid={`generated-file-${msg.message_id || i}`}>
                              <FileText className="w-8 h-8 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">{docFile.filename}</p>
                                <p className="text-xs opacity-70">{docFile.format?.toUpperCase()} {docFile.size ? `- ${(docFile.size / 1024).toFixed(1)}KB` : ""}</p>
                              </div>
                              <a href={`${API}${docFile.url}`} download={docFile.filename} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-medium transition-colors">
                                <Download className="w-3.5 h-3.5" />Download
                              </a>
                            </div>
                          )}
                          {(imgFile?.preview || imgFile?.url) && (
                            <div className="mt-3 rounded-lg overflow-hidden border border-white/10 max-w-sm" data-testid={`generated-image-${msg.message_id || i}`}>
                              <img src={imgFile.preview || `${API}${imgFile.url}`} alt="Generated" className="w-full" />
                              <a href={imgFile.url ? `${API}${imgFile.url}` : imgFile.preview} download className="block text-center text-xs text-indigo-400 py-2 hover:bg-white/5">
                                <Download className="w-3 h-3 inline mr-1" />Download PNG
                              </a>
                            </div>
                          )}
                          {vidFile?.url && (
                            <div className="mt-3 rounded-lg overflow-hidden border border-white/10 max-w-sm" data-testid={`generated-video-${msg.message_id || i}`}>
                              <video controls className="w-full" src={`${API}${vidFile.url}`} />
                              <a href={`${API}${vidFile.url}`} download className="block text-center text-xs text-violet-400 py-2 hover:bg-white/5">
                                <Download className="w-3 h-3 inline mr-1" />Download MP4
                              </a>
                            </div>
                          )}
                          {!vidFile?.url && msg.video_generating && (
                            <div className="mt-3 rounded-lg border border-violet-500/30 bg-violet-500/5 p-4 max-w-sm" data-testid={`video-generating-${msg.message_id || i}`}>
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full border-2 border-violet-400 border-t-transparent animate-spin" />
                                <div>
                                  <p className="text-sm text-violet-300 font-medium">Generating video with Sora 2...</p>
                                  <p className="text-xs text-zinc-500 mt-0.5">This may take 3-5 minutes. You can continue chatting.</p>
                                </div>
                              </div>
                            </div>
                          )}
                          {msg.video_error && (
                            <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/5 p-3 max-w-sm">
                              <p className="text-xs text-red-400">Video generation failed: {msg.video_error}</p>
                            </div>
                          )}
                        </>
                      );
                    })()}
                    {/* File generation buttons */}
                    {msg.role === "assistant" && <FileGenButtons content={msg.content} msgId={msg.message_id || i} />}
                  </div>
                  {msg.role === "user" && (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-sm font-semibold">
                          {user?.name?.charAt(0) || "U"}
                        </span>
                      </div>
                      {msg.model_used && (
                        <div style={{ fontSize: 9, color: "#475569", textAlign: "center", maxWidth: 56, lineHeight: 1.3, letterSpacing: "0.03em" }}>
                          {msg.model_used.split("/").pop()?.split("-").slice(0, 2).join("-")}
                          {msg.model_reason && <div style={{ color: "rgba(79,209,197,0.5)", fontSize: 8 }}>{msg.model_reason.split(" ").slice(0, 2).join(" ")}</div>}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                );
              })}
              {sending && (
                <div className="flex gap-3" data-testid="typing-indicator">
                  <div style={{ position: "relative", flexShrink: 0 }}>
                    {selectedAgent?.avatar ? (
                      <img src={selectedAgent.avatar} alt="" style={{ width: 32, height: 32, borderRadius: 9, objectFit: "cover", border: "1px solid rgba(79,209,197,0.25)", boxShadow: "0 0 12px rgba(79,209,197,0.2)" }} />
                    ) : (
                      <div style={{ width: 32, height: 32, borderRadius: 9, background: "rgba(79,209,197,0.12)", border: "1px solid rgba(79,209,197,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Brain style={{ width: 14, height: 14, color: "#4fd1c5" }} />
                      </div>
                    )}
                    <div style={{ position: "absolute", bottom: -2, right: -2, width: 8, height: 8, borderRadius: "50%", background: "#10b981", border: "2px solid #030712", animation: "neural-pulse-green 1.5s ease-in-out infinite" }} />
                  </div>
                  <div style={{ background: "rgba(10,18,36,0.9)", border: "1px solid rgba(79,209,197,0.18)", borderRadius: "4px 14px 14px 14px", padding: "12px 20px", backdropFilter: "blur(16px)", display: "flex", alignItems: "center", gap: 12, boxShadow: "0 4px 20px rgba(79,209,197,0.06), inset 0 0 0 1px rgba(79,209,197,0.06)" }}>
                    <div className="waveform" style={{ height: 20 }}><span /><span /><span /><span /><span /></div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                      <span style={{ fontSize: 11, color: "rgba(79,209,197,0.7)", letterSpacing: "0.1em", fontWeight: 600 }}>Processing</span>
                      <span style={{ fontSize: 9, color: "#334155", letterSpacing: "0.06em" }}>{selectedAgent?.name?.split(" ")[0] || "Agent"} is thinking…</span>
                    </div>
                    <div style={{ marginLeft: "auto", display: "flex", gap: 3 }}>
                      {[0,1,2].map(i => (
                        <div key={i} style={{ width: 4, height: 4, borderRadius: "50%", background: `rgba(79,209,197,${0.3 + i*0.2})`, animation: `thinking-dot 1.4s ease-in-out ${i*0.2}s infinite` }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input - Always visible at bottom */}
        <div className="p-4 border-t border-white/10 shrink-0 bg-background">
          {/* Attachments Preview */}
          {attachments.length > 0 && (
            <div className="max-w-3xl mx-auto mb-3 p-3 bg-zinc-900/50 border border-white/10 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Image className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-xs text-indigo-400 font-medium">
                  {attachments.length} file{attachments.length > 1 ? 's' : ''} attached — AI will analyze {attachments.some(a => a.type?.startsWith("image/")) ? 'images' : 'files'}
                </span>
              </div>
              <div className="flex flex-wrap gap-3">
                {attachments.map((att, idx) => (
                  <div key={idx} className="relative group">
                    {att.type?.startsWith("image/") ? (
                      <img src={att.preview} alt={att.filename} className="w-20 h-20 object-cover rounded-lg border border-white/10" />
                    ) : (
                      <div className="w-20 h-20 bg-zinc-800 rounded-lg flex flex-col items-center justify-center border border-white/10">
                        <FileText className="w-6 h-6 text-zinc-400" />
                        <span className="text-[10px] text-zinc-500 mt-1">{att.filename?.split('.').pop()?.toUpperCase()}</span>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => removeAttachment(idx)}
                      className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-3 h-3 text-white" />
                    </button>
                    <p className="text-[10px] text-zinc-500 truncate w-20 mt-1 text-center">{att.filename}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Model Selector + Router Calibration */}
          <div className="max-w-3xl mx-auto mb-3 space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span className="text-xs text-zinc-400">Model:</span>
              </div>
              {/* Custom model dropdown */}
              <div style={{ position: "relative" }}>
                <button onClick={() => setModelDropdownOpen(v => !v)} data-testid="model-selector"
                  style={{ display: "flex", alignItems: "center", gap: 7, width: 240, height: 32, padding: "0 10px", borderRadius: 8, border: `1px solid ${(PROVIDER_COLORS[selectedModel?.split("/")[0]] || "rgba(255,255,255,0.1)") + "30"}`, background: "rgba(9,9,26,.5)", cursor: "pointer", fontSize: 12, color: "#e2e8f0", boxSizing: "border-box" }}>
                  {selectedModel && <span style={{ width: 6, height: 6, borderRadius: "50%", background: PROVIDER_COLORS[selectedModel.split("/")[0]] || "#64748b", flexShrink: 0, boxShadow: `0 0 6px ${PROVIDER_COLORS[selectedModel.split("/")[0]] || "#64748b"}88` }} />}
                  <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", textAlign: "left" }}>
                    {chatModels.find(m => `${m.provider}/${m.model}` === selectedModel)?.name || selectedModel}
                  </span>
                  <ChevronDown size={11} style={{ color: "#71717a", flexShrink: 0 }} />
                </button>
                {modelDropdownOpen && (
                  <div style={{ position: "absolute", top: "calc(100% + 4px)", left: 0, width: 300, maxHeight: 420, overflowY: "auto", background: "#0f0f1a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, zIndex: 100, boxShadow: "0 8px 32px rgba(0,0,0,0.6)" }}>
                    <div style={{ padding: "8px 10px", position: "sticky", top: 0, background: "#0f0f1a", borderBottom: "1px solid rgba(255,255,255,.05)", zIndex: 1 }}>
                      <input autoFocus value={modelSearch} onChange={e => setModelSearch(e.target.value)} onKeyDown={e => e.stopPropagation()}
                        placeholder="Search 175,000+ models..."
                        style={{ width: "100%", background: "rgba(255,255,255,.06)", border: "1px solid rgba(255,255,255,.1)", borderRadius: 6, padding: "5px 9px", fontSize: 11, color: "#fff", outline: "none", boxSizing: "border-box" }} />
                    </div>
                    {(() => {
                      const q = modelSearch.toLowerCase();
                      const filtered = q ? chatModels.filter(m => m.name.toLowerCase().includes(q) || m.model.toLowerCase().includes(q) || m.provider.toLowerCase().includes(q)) : chatModels;
                      const creditColor = (cr) => cr <= 1 ? { bg: "rgba(52,211,153,.12)", c: "#34d399" } : cr <= 2 ? { bg: "rgba(96,165,250,.12)", c: "#60a5fa" } : cr <= 3 ? { bg: "rgba(245,158,11,.12)", c: "#f59e0b" } : { bg: "rgba(239,68,68,.12)", c: "#ef4444" };
                      const ModelBtn = ({ m }) => { const cc = creditColor(m.credits); return (
                        <button onClick={() => { setSelectedModel(`${m.provider}/${m.model}`); setModelSearch(""); setModelDropdownOpen(false); }}
                          style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, padding: "6px 12px", background: selectedModel === `${m.provider}/${m.model}` ? "rgba(129,140,248,.12)" : "transparent", border: "none", cursor: "pointer", textAlign: "left" }}>
                          <span style={{ fontSize: 11, color: "#d4d4d8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{m.name}</span>
                          <span style={{ fontSize: 9, fontWeight: 700, padding: "1px 6px", borderRadius: 20, background: cc.bg, color: cc.c, flexShrink: 0 }}>{m.credits}cr</span>
                        </button>
                      ); };
                      if (!filtered.length) return <div style={{ padding: "16px 12px", fontSize: 11, color: "#71717a", textAlign: "center" }}>No models found</div>;
                      if (q) return filtered.slice(0, 80).map(m => <ModelBtn key={`${m.provider}/${m.model}`} m={m} />);
                      const autoModels = filtered.filter(m => m.category === "auto");
                      const providers = [...new Set(filtered.filter(m => m.category !== "auto").map(m => m.provider))];
                      return (<>
                        {autoModels.map(m => <ModelBtn key={`${m.provider}/${m.model}`} m={m} />)}
                        {providers.map(prov => {
                          const provModels = filtered.filter(m => m.provider === prov);
                          const label = prov.charAt(0).toUpperCase() + prov.slice(1);
                          const pColor = PROVIDER_COLORS[prov] || "#64748b";
                          return (<div key={prov}>
                            <div style={{ display: "flex", alignItems: "center", gap: 7, padding: "5px 12px 3px", borderTop: "1px solid rgba(255,255,255,.05)", marginTop: 2 }}>
                              <div style={{ width: 6, height: 6, borderRadius: "50%", background: pColor, boxShadow: `0 0 6px ${pColor}88` }} />
                              <span style={{ fontSize: 9, color: pColor, textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 700, opacity: 0.85 }}>{label}</span>
                              <span style={{ fontSize: 9, color: "#475569", marginLeft: "auto" }}>{provModels.length}</span>
                            </div>
                            {provModels.map(m => <ModelBtn key={`${m.provider}/${m.model}`} m={m} />)}
                          </div>);
                        })}
                      </>);
                    })()}
                  </div>
                )}
              </div>
              {selectedModel === "auto/auto" ? (
                <span className="text-xs text-indigo-400">Smart router — task & credit aware</span>
              ) : (
                <span className="text-xs text-zinc-500">
                  {chatModels.find(m => `${m.provider}/${m.model}` === selectedModel)?.credits || 2} credits per message
                </span>
              )}
            </div>

            {/* Router Calibration — shown only when Universal Auto is selected */}
            {selectedModel === "auto/auto" && (
              <div className="flex items-center gap-3 flex-wrap pl-6">
                <div className="flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-zinc-500" />
                  <span className="text-[11px] text-zinc-500">Quality:</span>
                  <div className="flex gap-1">
                    {[["auto","Auto"],["economy","Economy"],["standard","Standard"],["premium","Premium"]].map(([v,l]) => (
                      <button key={v} onClick={() => setRouterQuality(v)}
                        className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${routerQuality===v ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-300" : "border-white/10 text-zinc-500 hover:border-white/20"}`}>
                        {l}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <Brain className="w-3 h-3 text-zinc-500" />
                  <span className="text-[11px] text-zinc-500">Task:</span>
                  <select value={routerTaskHint} onChange={e => setRouterTaskHint(e.target.value)}
                    style={{ height: 24, fontSize: 11, background: "rgba(9,9,26,.5)", border: "1px solid rgba(255,255,255,.1)", borderRadius: 6, color: "#d4d4d8", padding: "0 6px", outline: "none", cursor: "pointer", width: 130 }}>
                    {[["auto","Auto-detect"],["code","Code / Dev"],["math","Math"],["reasoning","Reasoning"],["creative","Creative"],["translation","Translation"],["summary","Summary"],["research","Research"],["data","Data / Analytics"],["chat","Chat"]].map(([v,l]) => (
                      <option key={v} value={v} style={{ background: "#0f0f1a" }}>{l}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3 items-end">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              multiple
              className="hidden"
              accept="image/*,.pdf,.doc,.docx,.txt,.csv,.xlsx,.webp,.heic"
            />
            <button type="button" onClick={() => fileInputRef.current?.click()} disabled={uploading} data-testid="attach-file-btn"
              style={{ width: 38, height: 38, borderRadius: 9, border: "1px solid rgba(255,255,255,.1)", background: "transparent", cursor: uploading ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#71717a", flexShrink: 0 }}>
              {uploading ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "ac_spin .8s linear infinite" }} /> : <Paperclip size={15} />}
            </button>
            <button type="button" onClick={recording ? stopRecording : startRecording} disabled={transcribing} data-testid="mic-btn"
              title={recording ? "Stop recording" : transcribing ? "Transcribing..." : "Voice input"}
              style={{ width: 38, height: 38, borderRadius: 9, border: `1px solid ${recording ? "rgba(239,68,68,.5)" : "rgba(255,255,255,.1)"}`, background: recording ? "rgba(239,68,68,.15)" : "transparent", cursor: transcribing ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: recording ? "#ef4444" : "#71717a", flexShrink: 0, animation: recording ? "ac_pulse 1.5s ease infinite" : "none" }}>
              {transcribing ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "ac_spin .8s linear infinite" }} /> : recording ? <MicOff size={15} /> : <Mic size={15} />}
            </button>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px";
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (input.trim() && selectedAgent && !sending) sendMessage(e);
                }
              }}
              onPaste={async (e) => {
                const items = Array.from(e.clipboardData.items);
                const imageItems = items.filter(item => item.type.startsWith("image/"));
                if (imageItems.length > 0) {
                  e.preventDefault();
                  setUploading(true);
                  for (const item of imageItems) {
                    const file = item.getAsFile();
                    if (!file) continue;
                    try {
                      const formData = new FormData();
                      formData.append('file', file);
                      const response = await fetch(`${API}/upload`, {
                        method: "POST", headers, body: formData
                      });
                      if (response.ok) {
                        const data = await response.json();
                        setAttachments(prev => [...prev, {
                          filename: data.filename,
                          type: data.content_type,
                          size: data.size,
                          preview: data.data_url,
                          file_url: data.file_url
                        }]);
                        toast.success("Image pasted");
                      }
                    } catch { toast.error("Failed to paste image"); }
                  }
                  setUploading(false);
                }
              }}
              placeholder={`Message ${selectedAgent?.name || "AI"}...`}
              className="flex-1 bg-zinc-900/50 border border-white/10 focus:border-indigo-500 rounded-md px-3 py-2 text-sm text-white placeholder:text-zinc-500 resize-none overflow-y-auto outline-none"
              style={{ minHeight: "40px", maxHeight: "200px" }}
              rows={1}
              disabled={sending || !selectedAgent}
              data-testid="chat-input"
            />
            <button type="submit" disabled={sending || !input.trim() || !selectedAgent} data-testid="send-message-btn"
              style={{ width: 38, height: 38, borderRadius: 9, border: "none", background: sending || !input.trim() || !selectedAgent ? "rgba(129,140,248,.25)" : "linear-gradient(135deg, #818cf8, #7c3aed)", cursor: sending || !input.trim() || !selectedAgent ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", flexShrink: 0 }}>
              <Send size={15} />
            </button>
          </form>
        </div>
      </div>
      <style>{`
        @keyframes ac_spin { to { transform: rotate(360deg); } }
        @keyframes ac_wave { 0% { height: 4px; } 100% { height: 14px; } }
        @keyframes thinking-dot { 0%,80%,100% { transform: scale(0.6); opacity: 0.3; } 40% { transform: scale(1.2); opacity: 1; } }
        @keyframes neural-pulse-green { 0%,100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.8); } 60% { box-shadow: 0 0 0 6px rgba(16,185,129,0); } }
      `}</style>
    </div>
  );
};

// Sidebar Content Component
const NETWORK_LABELS = {
  core_platform: "Core Platform", strategic_executive: "Strategic", venture_creation: "Venture",
  product_development: "Product", engineering: "Engineering", creative_brand: "Creative",
  growth_distribution: "Growth", sales_revenue: "Sales", customer_experience: "Customer",
  operations: "Operations", finance_capital: "Finance", investment_portfolio: "Investment",
  research_intelligence: "Research", simulation_foresight: "Simulation", legal_governance: "Legal",
  security: "Security", memory_knowledge: "Memory", tooling_capability: "Tooling",
  execution: "Execution", verification: "Verification", experimentation: "Experimentation",
  conflict_resolution: "Conflict", observability_incident: "Observability", recovery_resilience: "Recovery",
  communication_reporting: "Communication", web_search_intelligence: "Web Intel", industry_specific: "Industry",
};

const NET_COLORS = {
  core_platform: "#10b981", strategic_executive: "#a855f7", venture_creation: "#3b82f6",
  product_development: "#06b6d4", engineering: "#f59e0b", creative_brand: "#ec4899",
  growth_distribution: "#22c55e", sales_revenue: "#f97316", customer_experience: "#14b8a6",
  operations: "#4fd1c5", finance_capital: "#eab308", investment_portfolio: "#8b5cf6",
  research_intelligence: "#0ea5e9", simulation_foresight: "#d946ef", legal_governance: "#f43f5e",
  security: "#ef4444", memory_knowledge: "#06b6d4", tooling_capability: "#84cc16",
  execution: "#f97316", verification: "#4fd1c5", experimentation: "#a855f7",
  conflict_resolution: "#f43f5e", observability_incident: "#22d3ee", recovery_resilience: "#10b981",
  communication_reporting: "#3b82f6", web_search_intelligence: "#0ea5e9", industry_specific: "#f59e0b",
};

const getInitials = (name) => name?.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || '??';

const SidebarContent = ({ agents, chats, selectedAgent, setSelectedAgent, 
  currentChat, loadChat, deleteChat, startNewChat, navigate 
}) => {
  const [agentSearch, setAgentSearch] = useState("");
  const [browseOpen, setBrowseOpen] = useState(false);
  const [expandedNet, setExpandedNet] = useState(null);
  
  const originalAgents = agents.filter(a => !a.is_infinity);
  const infinityAgents = agents.filter(a => a.is_infinity);
  
  // Build network groups for browsing
  const networkGroups = {};
  infinityAgents.forEach(a => {
    const net = a.network || "ungrouped";
    if (!networkGroups[net]) networkGroups[net] = [];
    networkGroups[net].push(a);
  });
  const sortedNetworks = Object.keys(networkGroups).sort((a, b) => 
    (NETWORK_LABELS[a] || a).localeCompare(NETWORK_LABELS[b] || b)
  );
  
  // Unified search across ALL agents
  const searchResults = agentSearch.trim().length > 0
    ? agents.filter(a =>
        a.name.toLowerCase().includes(agentSearch.toLowerCase()) ||
        a.role.toLowerCase().includes(agentSearch.toLowerCase()) ||
        (a.network || "").toLowerCase().includes(agentSearch.toLowerCase()) ||
        (NETWORK_LABELS[a.network] || "").toLowerCase().includes(agentSearch.toLowerCase())
      ).slice(0, 30)
    : [];

  const selectAgent = (agent) => {
    setSelectedAgent(agent);
    navigate(`/chat/${agent.agent_id}`);
    setAgentSearch("");
    setBrowseOpen(false);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="chat-sidebar">
      {/* Quick Access: Original Agents */}
      <div className="px-3 pt-3 pb-2 border-b border-white/[0.06]">
        <p className="text-[10px] font-semibold text-zinc-600 uppercase tracking-wider mb-2 px-1">Agents</p>
        <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {originalAgents.slice(0, 10).map((agent) => (
            <button
              key={agent.agent_id}
              onClick={() => selectAgent(agent)}
              className={`flex-shrink-0 p-1.5 rounded-lg transition-all ${
                selectedAgent?.agent_id === agent.agent_id
                  ? "bg-indigo-500/15 ring-1 ring-indigo-500/40"
                  : "bg-zinc-800/40 hover:bg-zinc-800"
              }`}
              title={agent.name}
              data-testid={`agent-btn-${agent.agent_id}`}
            >
              {agent.avatar ? (
                <img src={agent.avatar} alt={agent.name} className="w-8 h-8 rounded-md object-cover" />
              ) : (
                <div className="w-8 h-8 rounded-md bg-zinc-700 flex items-center justify-center text-[10px] font-bold text-zinc-300">
                  {getInitials(agent.name)}
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="mt-2 relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search 458+ agents..."
            value={agentSearch}
            onChange={e => setAgentSearch(e.target.value)}
            className="w-full bg-zinc-800/50 border border-white/5 rounded-md pl-7 pr-8 py-1.5 text-[11px] text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30"
            data-testid="agent-search-input"
          />
          {agentSearch && (
            <button onClick={() => setAgentSearch("")} className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white">
              <X className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Search Results */}
        {agentSearch && searchResults.length > 0 && (
          <div className="mt-1.5 max-h-56 overflow-y-auto space-y-0.5 bg-zinc-900/95 rounded-lg border border-white/10 p-1 shadow-xl" data-testid="search-results">
            {searchResults.map(agent => {
              const netColor = NET_COLORS[agent.network] || "#4fd1c5";
              return (
                <button
                  key={agent.agent_id}
                  onClick={() => selectAgent(agent)}
                  className="w-full text-left flex items-center gap-2.5 px-2 py-1.5 rounded-md hover:bg-white/5 transition-colors"
                  data-testid={`search-agent-${agent.agent_id}`}
                >
                  {agent.avatar ? (
                    <img src={agent.avatar} alt="" className="w-6 h-6 rounded object-cover" />
                  ) : (
                    <div className="w-6 h-6 rounded flex items-center justify-center text-[8px] font-bold" style={{ backgroundColor: `${netColor}20`, color: netColor }}>
                      {getInitials(agent.name)}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] text-white truncate">{agent.name}</p>
                    <p className="text-[9px] text-zinc-500 truncate">{agent.role} — {NETWORK_LABELS[agent.network] || agent.network || "General"}</p>
                  </div>
                  {agent.is_infinity && <span className="text-[8px] text-zinc-600 shrink-0">∞</span>}
                </button>
              );
            })}
            {searchResults.length >= 30 && (
              <p className="text-[9px] text-zinc-600 text-center py-1">Showing top 30 results</p>
            )}
          </div>
        )}
        {agentSearch && searchResults.length === 0 && (
          <p className="text-[10px] text-zinc-600 text-center py-3 mt-1">No agents match "{agentSearch}"</p>
        )}

        {/* Browse Networks Button */}
        <button
          onClick={() => setBrowseOpen(!browseOpen)}
          className={`w-full mt-2 flex items-center justify-between px-2.5 py-1.5 rounded-md text-[11px] transition-colors ${
            browseOpen ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" : "bg-zinc-800/30 text-zinc-500 hover:text-zinc-300 border border-transparent hover:border-white/5"
          }`}
          data-testid="browse-networks-btn"
        >
          <span className="flex items-center gap-1.5">
            <Users className="w-3 h-3" />
            Browse {sortedNetworks.length} Networks
          </span>
          <ChevronDown className={`w-3 h-3 transition-transform ${browseOpen ? "rotate-180" : ""}`} />
        </button>
      </div>

      {/* Network Browser Panel */}
      {browseOpen && (
        <div className="border-b border-white/[0.06] max-h-64 overflow-y-auto" data-testid="network-browser">
          {sortedNetworks.map(netKey => {
            const isExpanded = expandedNet === netKey;
            const netAgents = networkGroups[netKey];
            const netColor = NET_COLORS[netKey] || "#4fd1c5";
            return (
              <div key={netKey}>
                <button
                  onClick={() => setExpandedNet(isExpanded ? null : netKey)}
                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-white/[0.03] transition-colors"
                  data-testid={`network-group-${netKey}`}
                >
                  <div className="w-5 h-5 rounded flex items-center justify-center shrink-0" style={{ backgroundColor: `${netColor}15` }}>
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: netColor }} />
                  </div>
                  <span className="text-[11px] text-zinc-300 flex-1 text-left truncate">{NETWORK_LABELS[netKey] || netKey}</span>
                  <span className="text-[9px] text-zinc-600 mr-1">{netAgents.length}</span>
                  <ChevronRight className={`w-3 h-3 text-zinc-600 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
                </button>
                {isExpanded && (
                  <div className="pl-4 pr-2 pb-1 space-y-0.5">
                    {netAgents.map(agent => (
                      <button
                        key={agent.agent_id}
                        onClick={() => selectAgent(agent)}
                        className={`w-full text-left flex items-center gap-2 px-2 py-1.5 rounded-md transition-colors ${
                          selectedAgent?.agent_id === agent.agent_id ? "bg-indigo-500/10 text-indigo-300" : "hover:bg-white/[0.04] text-zinc-400"
                        }`}
                        data-testid={`net-agent-${agent.agent_id}`}
                      >
                        {agent.avatar ? (
                          <img src={agent.avatar} alt="" className="w-5 h-5 rounded object-cover" />
                        ) : (
                          <div className="w-5 h-5 rounded flex items-center justify-center text-[7px] font-bold" style={{ backgroundColor: `${netColor}20`, color: netColor }}>
                            {getInitials(agent.name)}
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-[10px] truncate">{agent.name}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Chat History */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        <div className="px-3 pt-3">
          <p className="text-[10px] font-semibold text-zinc-600 uppercase tracking-wider mb-2 px-1">Recent Chats</p>
          <div className="space-y-0.5">
            {chats.map((chat) => (
              <div
                key={chat.chat_id}
                className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${
                  currentChat?.chat_id === chat.chat_id
                    ? "bg-indigo-500/12 text-indigo-400"
                    : "hover:bg-white/[0.04] text-zinc-400 hover:text-zinc-300"
                }`}
                onClick={() => {
                  loadChat(chat.chat_id);
                  navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`);
                }}
                data-testid={`chat-item-${chat.chat_id}`}
              >
                <MessageSquare className="w-3.5 h-3.5 flex-shrink-0 opacity-50" />
                <span className="flex-1 text-[13px] truncate">{chat.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(chat.chat_id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-zinc-600 hover:text-red-400 transition-opacity"
                  data-testid={`delete-chat-${chat.chat_id}`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            {chats.length === 0 && (
              <p className="text-xs text-zinc-600 text-center py-6">No chats yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChat;
