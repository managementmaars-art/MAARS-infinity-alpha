import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { TrendingUp, CheckCircle, Trash2, Plus, X, ChevronDown, ChevronUp, ShieldAlert, Info, Sparkles, Lock, Unlock } from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";
// Centralized pricing math — single source of truth shared with the backend
// services/pricing_math.py module. Replaces inline formulas that had drifted
// out of sync with the backend (e.g. tokens_per_credit was 500 server-side,
// 1000 client-side).
import {
  DEFAULT_ENGINE_CONFIG,
  stampPlans,
  aiCostUsd,
  profitUsd,
  marginPct,
  operatorSharePct,
  suggestedPrice,
  usdToBdt,
} from "../../../utils/pricingMath";

// Real published model costs (USD per 1M tokens, input / output)
const MODEL_COSTS = [
  // OpenAI
  { name: "GPT-5",              provider: "OpenAI",      input: 2.50,  output: 10.00 },
  { name: "GPT-4.1",            provider: "OpenAI",      input: 2.00,  output: 8.00  },
  { name: "GPT-4.1 Mini",       provider: "OpenAI",      input: 0.40,  output: 1.60  },
  { name: "GPT-4.1 Nano",       provider: "OpenAI",      input: 0.10,  output: 0.40  },
  { name: "GPT-4o",             provider: "OpenAI",      input: 2.50,  output: 10.00 },
  { name: "GPT-4o mini",        provider: "OpenAI",      input: 0.15,  output: 0.60  },
  { name: "O4",                 provider: "OpenAI",      input: 15.00, output: 60.00 },
  { name: "O4 Mini",            provider: "OpenAI",      input: 1.10,  output: 4.40  },
  { name: "O3",                 provider: "OpenAI",      input: 10.00, output: 40.00 },
  { name: "O3 Mini",            provider: "OpenAI",      input: 1.10,  output: 4.40  },
  // Anthropic
  { name: "Claude Opus 4.6",    provider: "Anthropic",   input: 15.00, output: 75.00 },
  { name: "Claude Sonnet 4.6",  provider: "Anthropic",   input: 3.00,  output: 15.00 },
  { name: "Claude Haiku 4.5",   provider: "Anthropic",   input: 0.80,  output: 4.00  },
  // Google Gemini
  { name: "Gemini 2.5 Pro",     provider: "Google",      input: 1.25,  output: 10.00 },
  { name: "Gemini 2.5 Flash",   provider: "Google",      input: 0.075, output: 0.30  },
  { name: "Gemini 2.5 Flash Lite", provider: "Google",   input: 0.038, output: 0.15  },
  { name: "Gemini 3 Flash",     provider: "Google",      input: 0.075, output: 0.30  },
  // xAI
  { name: "Grok 3",             provider: "xAI",         input: 3.00,  output: 15.00 },
  { name: "Grok 3 Mini",        provider: "xAI",         input: 0.30,  output: 0.50  },
  // DeepSeek
  { name: "DeepSeek V3 0324",   provider: "DeepSeek",    input: 0.14,  output: 0.28  },
  { name: "DeepSeek R1 0528",   provider: "DeepSeek",    input: 0.55,  output: 2.19  },
  // Mistral
  { name: "Mistral Large",      provider: "Mistral",     input: 2.00,  output: 6.00  },
  { name: "Mistral Small",      provider: "Mistral",     input: 0.10,  output: 0.30  },
  { name: "Mistral Nemo",       provider: "Mistral",     input: 0.15,  output: 0.15  },
  { name: "Codestral",          provider: "Mistral",     input: 0.30,  output: 0.90  },
  // Perplexity
  { name: "Sonar Pro",          provider: "Perplexity",  input: 3.00,  output: 15.00 },
  { name: "Sonar Reasoning",    provider: "Perplexity",  input: 1.00,  output: 5.00  },
  { name: "Sonar",              provider: "Perplexity",  input: 1.00,  output: 1.00  },
  // Open-source / fast
  { name: "Llama 4 Scout",      provider: "Groq",        input: 0.11,  output: 0.34  },
  { name: "Llama 3.1 8B Instant", provider: "Groq",      input: 0.05,  output: 0.08  },
  { name: "Qwen QwQ 32B",       provider: "Groq",        input: 0.29,  output: 0.39  },
  { name: "Llama 3.3 70B",      provider: "Cerebras",    input: 0.60,  output: 0.60  },
  { name: "Llama 3.1 8B",       provider: "Cerebras",    input: 0.10,  output: 0.10  },
  { name: "DeepSeek R1 0528 (SambaNova)", provider: "SambaNova", input: 1.30,  output: 1.30  },
  { name: "AI21 Jamba Mini",    provider: "AI21",        input: 0.20,  output: 0.40  },
];
// NOTE: TOKENS_PER_CREDIT used to live here as a hardcoded const. It's now
// driven by engineConfig.tokens_per_credit (operator-editable in the Pricing
// Engine Config panel). Model Cost Reference + Media Budget Calculator both
// read from engineConfig so changing it live rebalances every calculation.

// Tokens per credit — the global conversion. Matches
// backend/services/billing/token_quota.py::TOKENS_PER_CREDIT.
// Operator-visible as the client's hard-cap multiplier.
const TOKENS_PER_CREDIT = 100_000;

// Unified 5-tier plan preset — matches backend PLAN_CATALOG in
// services/billing/plan_deliverables.py. This is the CANONICAL shape
// served on /api/plans plans_v2 and presented to buyers.
const buildUnifiedPresets = () => ({
  free: {
    name: "Free",
    price_usd: 0,
    credits: 10,              // 1M tokens
    max_agents: 3,
    max_custom_agents: 0,
    includes_commander: false,
    max_team_members: 1,
    features: [
      "10 credits / 1M tokens per month",
      "3 AI agents, no custom",
      "Chat, 10 images, 3 app builds",
      "Unlimited voiceover + transcription",
    ],
  },
  creator: {
    name: "Creator",
    price_usd: 29,
    credits: 50,              // 5M tokens
    max_agents: 12,
    max_custom_agents: 1,
    includes_commander: false,
    max_team_members: 1,
    features: [
      "50 credits / 5M tokens per month",
      "12 agents + 1 custom",
      "Smart router picks cheapest capable model per call",
      "Unlimited voiceover + transcription",
    ],
  },
  studio: {
    name: "Studio",
    price_usd: 99,
    credits: 200,             // 20M tokens
    max_agents: 25,
    max_custom_agents: 3,
    includes_commander: true,
    max_team_members: 10,
    features: [
      "200 credits / 20M tokens per month",
      "25 agents + 3 custom + Commander Orion",
      "Premium ElevenLabs voices unlocked",
      "Teams of 10",
    ],
  },
  scale: {
    name: "Scale",
    price_usd: 299,
    credits: 750,             // 75M tokens
    max_agents: 41,
    max_custom_agents: 10,
    includes_commander: true,
    max_team_members: 35,
    features: [
      "750 credits / 75M tokens per month",
      "All 41 core agents + 10 custom",
      "Priority routing, faster provider response",
      "Teams of 35 · dedicated Slack support",
    ],
  },
  infinity: {
    name: "Infinity",
    price_usd: 999,
    credits: 5000,            // 500M tokens fair-use
    max_agents: -1,           // unlimited
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "5,000 credits / 500M tokens per month (fair use)",
      "Unlimited agents + customization",
      "All 499 trained specialist agents",
      "Custom onboarding, named account manager, SLAs, SSO, audit logs",
    ],
  },
});

// Build preset plans — BDT and monthly_cap_usd are stamped on load/publish
// Agent count: 41 core named agents + 417 MAARS Infinity = 458 total
// Credits: capped ~10,000 — enough for a full month of active use
// LEGACY: Retained so existing ops can roll back; use buildUnifiedPresets above.
const buildPresets = () => ({
  free: {
    name: "Free",
    price_usd: 0,
    credits: 50,
    max_agents: 3,
    max_custom_agents: 0,
    includes_commander: false,
    max_team_members: 1,
    features: [
      "3 AI agents", "50 credits/month",
      "Basic chat & task management", "1 LLM provider",
      "Community support",
    ],
  },
  starter: {
    name: "Starter",
    price_usd: 50,
    credits: 300,
    max_agents: 8,
    max_custom_agents: 0,
    includes_commander: false,
    max_team_members: 1,
    features: [
      "8 AI agents", "300 credits/month",
      "Chat, tasks & projects", "3 LLM providers",
      "File uploads", "Solo workspace", "Email support",
    ],
  },
  essential: {
    name: "Essential",
    price_usd: 100,
    credits: 600,
    max_agents: 12,
    max_custom_agents: 1,
    includes_commander: false,
    max_team_members: 3,
    features: [
      "12 AI agents", "600 credits/month", "1 custom agent",
      "5 LLM providers", "Workflow builder (basic)",
      "File uploads", "Team (up to 3)", "Email support",
    ],
  },
  basic: {
    name: "Basic",
    price_usd: 200,
    credits: 1200,
    max_agents: 18,
    max_custom_agents: 2,
    includes_commander: false,
    max_team_members: 5,
    features: [
      "18 AI agents", "1,200 credits/month", "2 custom agents",
      "8 LLM providers", "Full workflow builder",
      "Content generator", "Basic analytics",
      "Team (up to 5)", "Priority email support",
    ],
  },
  standard: {
    name: "Standard",
    price_usd: 350,
    credits: 2000,
    max_agents: 25,
    max_custom_agents: 3,
    includes_commander: true,
    max_team_members: 10,
    features: [
      "25 AI agents + Commander Orion", "2,000 credits/month", "3 custom agents",
      "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "Autonomous orchestration",
      "Campaign builder", "Knowledge graph", "Trust scores",
      "Team (up to 10)", "Priority support",
    ],
  },
  professional: {
    name: "Professional",
    price_usd: 500,
    credits: 3000,
    max_agents: 35,
    max_custom_agents: 5,
    includes_commander: true,
    max_team_members: 20,
    features: [
      "35 AI agents + Commander Orion", "3,000 credits/month", "5 custom agents",
      "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "Vibe Coding & Reference Intelligence",
      "Memory hierarchy", "Analytics dashboard",
      "Team (up to 20)", "Live chat support",
    ],
  },
  advanced: {
    name: "Advanced",
    price_usd: 750,
    credits: 4000,
    max_agents: 41,
    max_custom_agents: 10,
    includes_commander: true,
    max_team_members: 35,
    features: [
      "All 41 core AI agents + Commander Orion", "4,000 credits/month", "10 custom agents",
      "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "Full observability dashboard",
      "Model router", "Circuit breakers", "Cost governance",
      "Team (up to 35)", "Dedicated Slack support",
    ],
  },
  business: {
    name: "Business",
    price_usd: 1000,
    credits: 5000,
    max_agents: 141,
    max_custom_agents: 20,
    includes_commander: true,
    max_team_members: 50,
    features: [
      "41 core + 100 MAARS Infinity agents + Commander Orion", "5,000 credits/month", "20 custom agents",
      "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "MAARS Infinity agent networks",
      "Operator panel", "API access & webhooks",
      "Team (up to 50)", "Dedicated Slack support",
    ],
  },
  agency: {
    name: "Agency",
    price_usd: 1500,
    credits: 6500,
    max_agents: 241,
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "41 core + 200 MAARS Infinity agents + Commander Orion", "6,500 credits/month",
      "Unlimited custom agents", "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
      "White-label ready", "RBAC & access control",
      "Client management tools", "SLA guarantee",
      "Unlimited team members", "Dedicated account manager",
    ],
  },
  studio: {
    name: "Studio",
    price_usd: 2500,
    credits: 7500,
    max_agents: 391,
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "41 core + 350 MAARS Infinity agents + Commander Orion", "7,500 credits/month",
      "Unlimited custom agents", "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
      "Venture portfolio", "Agent Catalog (350 networks)",
      "Custom integrations", "Multi-workspace",
      "Unlimited team members", "Priority dedicated support",
    ],
  },
  enterprise: {
    name: "Enterprise",
    price_usd: 3500,
    credits: 8500,
    max_agents: 458,
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "All 458 agents + Commander Orion", "8,500 credits/month",
      "Unlimited everything", "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
      "Dedicated infrastructure", "Advanced security & compliance",
      "Custom AI integrations", "Onboarding & training",
      "Custom SLAs", "24/7 premium support",
    ],
  },
  corporate: {
    name: "Corporate",
    price_usd: 5000,
    credits: 9500,
    max_agents: 458,
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "All 458 agents + Commander Orion", "9,500 credits/month",
      "Unlimited everything", "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
      "Custom AI model fine-tuning", "Dedicated engineering support",
      "Multi-workspace management", "Custom contracts & billing",
      "Quarterly business reviews", "Executive priority support",
    ],
  },
  elite: {
    name: "Elite",
    price_usd: 8000,
    credits: 10000,
    max_agents: 458,
    max_custom_agents: -1,
    includes_commander: true,
    max_team_members: -1,
    features: [
      "All 458 agents + Commander Orion", "10,000 credits/month",
      "Unlimited everything", "MAARS Universal AI Gateway — 33 providers, 175,000+ models",
      "Custom agent development", "Dedicated servers & infrastructure",
      "Strategic AI consulting", "Full platform customization",
      "Executive support hotline", "Custom contract & billing",
    ],
  },
});

// Deprecated thin alias — kept so existing call sites still work. The real
// implementation lives in utils/pricingMath.js (stampPlans). Any NEW code
// should import stampPlans directly instead of going through this shim.
const stampDerived = (plans, rate, costPerCredit) =>
  stampPlans(plans, rate, costPerCredit);

const BLANK_PLAN = {
  name: "",
  price_usd: 0,
  credits: 0,
  max_agents: 5,
  max_custom_agents: 0,
  max_team_members: 1,
  includes_commander: false,
  features: [],
  // Explicit media caps. null = "auto" (derive from credit budget).
  // Integer = hard cap. -1 = disabled (feature locked on this tier).
  media: {
    images_standard:    null,
    images_hd:          null,
    videos_4sec:        null,
    video_seconds:      null,
    tts_minutes:        null,
    voiceover_minutes:  null,
    stt_minutes:        null,
  },
  // null means "use global tokens_per_credit from Pricing Engine Config".
  tokens_per_credit: null,
};

// Default Pricing Engine Config — per-unit credit costs for each media modality.
// Operator can override any of these in the Pricing Engine Config card at the
// top of the manager; the values flow into plan.monthly_cap_usd computation
// and into the Media Capacity auto-derivation.
// ── MediaBudgetCalculator ─────────────────────────────────────────────
// Interactive explainer: type/drag a credit budget, see exactly how many
// images, videos, TTS minutes, etc. that gets the client. Also lets operator
// set a mix (sliders for how credits split across modalities) to preview
// realistic usage scenarios (e.g. 60% chat / 30% images / 10% video).
function MediaBudgetCalculator({ engineConfig, blendedByCategory }) {
  const [budget, setBudget] = useState(1000);
  // 8 dedicated tracks — each deliverable type has its own slider and
  // its own rate. No merging between image_std/image_hd or between
  // voiceover/tts/stt.
  const [mix, setMix] = useState({
    chat: 40, code: 15, image_std: 5, image_hd: 10,
    video: 15, voiceover: 10, tts: 3, stt: 2,
  });

  const ec = { ...DEFAULT_ENGINE_CONFIG, ...(engineConfig || {}) };
  const tpc            = ec.tokens_per_credit || 100000;
  const imgStdCost     = ec.image_std_credits;
  const imgHdCost      = ec.image_hd_credits;
  const videoCostSec   = ec.video_credits_per_sec;
  const ttsCost        = ec.tts_credits_per_min;
  const voCost         = ec.voiceover_credits_per_min;
  const sttCost        = ec.stt_credits_per_min;
  // Chat + Code per-action rates (operator-set, not token-derived).
  const chatCost       = parseFloat(ec.chat_credits_per_msg) || 0.015;
  const codeCost       = parseFloat(ec.code_credits_per_run) || 0.04;

  const capacity = (credits, perUnitCredits) =>
    (!perUnitCredits || perUnitCredits <= 0) ? "∞" : Math.floor(credits / perUnitCredits).toLocaleString();

  const mixTotal = Object.values(mix).reduce((s, v) => s + v, 0) || 1;
  const pct = (k) => (mix[k] / mixTotal);
  const setMixField = (k, v) => setMix(m => ({ ...m, [k]: Math.max(0, Math.min(100, parseInt(v, 10) || 0)) }));

  const ceilings = {
    // Chat + code now show max messages / runs at the per-action rate.
    // Tokens equivalent kept as the secondary hint for context.
    chat_msgs:      capacity(budget, chatCost),
    code_runs:      capacity(budget, codeCost),
    images_std:     capacity(budget, imgStdCost),
    images_hd:      capacity(budget, imgHdCost),
    video_clips_4s: capacity(budget, (videoCostSec || 0) * 4),
    video_seconds:  capacity(budget, videoCostSec),
    vo_min:         capacity(budget, voCost),
    tts_min:        capacity(budget, ttsCost),
    stt_min:        capacity(budget, sttCost),
  };

  // Realistic-mix capacity — each track dedicated, no overlap.
  const creditsFor = {
    chat:      budget * pct("chat"),
    code:      budget * pct("code"),
    image_std: budget * pct("image_std"),
    image_hd:  budget * pct("image_hd"),
    video:     budget * pct("video"),
    voiceover: budget * pct("voiceover"),
    tts:       budget * pct("tts"),
    stt:       budget * pct("stt"),
  };
  const mixed = {
    chat_msgs:   capacity(creditsFor.chat, chatCost),
    code_runs:   capacity(creditsFor.code, codeCost),
    images_std:  capacity(creditsFor.image_std, imgStdCost),
    images_hd:   capacity(creditsFor.image_hd,  imgHdCost),
    video_sec:   capacity(creditsFor.video,     videoCostSec),
    vo_min:      capacity(creditsFor.voiceover, voCost),
    tts_min:     capacity(creditsFor.tts,       ttsCost),
    stt_min:     capacity(creditsFor.stt,       sttCost),
  };

  // Live COST at this budget + mix — 8 separate rates, 8 separate costs.
  const rates = {
    chat:      blendedByCategory?.chat?.value      || 0,
    code:      blendedByCategory?.code?.value      || 0,
    image_std: blendedByCategory?.image_std?.value || 0,
    image_hd:  blendedByCategory?.image_hd?.value  || 0,
    video:     blendedByCategory?.video?.value     || 0,
    voiceover: blendedByCategory?.voiceover?.value || 0,
    tts:       blendedByCategory?.tts?.value       || 0,
    stt:       blendedByCategory?.stt?.value       || 0,
  };
  const costByCat = {
    chat:      creditsFor.chat      * rates.chat,
    code:      creditsFor.code      * rates.code,
    image_std: creditsFor.image_std * rates.image_std,
    image_hd:  creditsFor.image_hd  * rates.image_hd,
    video:     creditsFor.video     * rates.video,
    voiceover: creditsFor.voiceover * rates.voiceover,
    tts:       creditsFor.tts       * rates.tts,
    stt:       creditsFor.stt       * rates.stt,
  };
  const totalCost = Object.values(costByCat).reduce((s, v) => s + v, 0);

  return (
    <div className="p-3 rounded-lg bg-gradient-to-br from-indigo-500/5 to-teal-500/5 border border-indigo-500/20 space-y-3">
      <div className="flex items-center gap-2">
        <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
        <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wide">Media Budget Calculator</span>
        <span className="text-[10px] text-zinc-500">— set credits, watch capacity + cost update live</span>
      </div>

      {/* Budget input + slider */}
      <div className="flex items-center gap-3">
        <Input
          type="number"
          value={budget}
          onChange={(e) => setBudget(Math.max(0, parseInt(e.target.value, 10) || 0))}
          className="bg-zinc-900/60 border-indigo-500/30 border h-8 w-28 text-sm font-mono"
        />
        <span className="text-[10px] text-zinc-500">credits</span>
        <input
          type="range" min="0" max="20000" step="100" value={Math.min(budget, 20000)}
          onChange={(e) => setBudget(parseInt(e.target.value, 10))}
          className="flex-1 accent-indigo-400"
        />
        <div className="flex gap-1 text-[10px]">
          {[50, 300, 600, 1200, 2000, 3000, 5000, 10000].map(p => (
            <button
              key={p}
              onClick={() => setBudget(p)}
              className="px-2 py-1 rounded border border-white/10 text-zinc-400 hover:text-indigo-400 hover:border-indigo-500/30"
            >
              {p >= 1000 ? `${p/1000}k` : p}
            </button>
          ))}
        </div>
      </div>

      {/* Full-modality ceilings — 8 cells (one per dedicated track).
          Video is ONE cell showing seconds primary + 4-sec clip equivalent
          as a sub-label. No more "which Video column?" confusion. */}
      <div>
        <div className="text-[10px] text-zinc-500 mb-1">If client spent 100% on ONE modality:</div>
        <div className="grid grid-cols-2 lg:grid-cols-8 gap-2">
          {[
            ["Chat",      ceilings.chat_msgs,     null,                                                   "text-emerald-400", "msgs"],
            ["Code",      ceilings.code_runs,     null,                                                   "text-violet-400",  "runs"],
            ["Image Std", ceilings.images_std,    null,                                                   "text-rose-300",    "images"],
            ["Image HD",  ceilings.images_hd,     null,                                                   "text-rose-400",    "images"],
            ["Video",     ceilings.video_seconds, `≈ ${ceilings.video_clips_4s} × 4-sec clips`,          "text-amber-400",   "sec"],
            ["Voiceover", ceilings.vo_min,        null,                                                   "text-sky-400",     "min"],
            ["TTS",       ceilings.tts_min,       null,                                                   "text-cyan-400",    "min"],
            ["STT",       ceilings.stt_min,       null,                                                   "text-teal-400",    "min"],
          ].map(([label, val, sub, cls, unit]) => (
            <div key={label} className="p-2 rounded bg-zinc-900/40 border border-white/5">
              <div className="text-[9px] text-zinc-500 uppercase">{label}</div>
              <div className={`text-sm font-bold font-mono ${cls}`}>{val} <span className="text-[9px] text-zinc-600 font-normal">{unit}</span></div>
              {sub && <div className="text-[9px] text-zinc-600 font-mono mt-0.5">{sub}</div>}
            </div>
          ))}
        </div>
      </div>

      {/* Realistic usage mix — 8 dedicated tracks matching the top strip */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="text-[10px] text-zinc-500">Realistic mix ({mixTotal}% allocated) — same 8 dedicated tracks as the top strip:</div>
        </div>
        <div className="grid grid-cols-4 lg:grid-cols-8 gap-2">
          {[
            ["chat",       "Chat",      "emerald"],
            ["code",       "Code",      "violet"],
            ["image_std",  "Image Std", "rose"],
            ["image_hd",   "Image HD",  "fuchsia"],
            ["video",      "Video",     "amber"],
            ["voiceover",  "Voiceover", "sky"],
            ["tts",        "TTS",       "cyan"],
            ["stt",        "STT",       "teal"],
          ].map(([k, label, color]) => (
            <div key={k} className="space-y-1">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-zinc-400">{label}</span>
                <span className={`font-mono text-${color}-400`}>{mix[k]}%</span>
              </div>
              <input
                type="range" min="0" max="100" step="1" value={mix[k]}
                onChange={(e) => setMixField(k, e.target.value)}
                className={`w-full accent-${color}-400`}
              />
            </div>
          ))}
        </div>
        {/* Capacity at this mix — one tile per track (8 tiles, no merging) */}
        <div className="grid grid-cols-4 lg:grid-cols-8 gap-2 mt-2">
          {[
            ["Chat",      mixed.chat_msgs + " msgs",    "emerald"],
            ["Code",      mixed.code_runs + " runs",    "violet"],
            ["Image Std", mixed.images_std  + " std",   "rose"],
            ["Image HD",  mixed.images_hd   + " HD",    "fuchsia"],
            ["Video",     mixed.video_sec   + " sec",   "amber"],
            ["Voiceover", mixed.vo_min      + " min",   "sky"],
            ["TTS",       mixed.tts_min     + " min",   "cyan"],
            ["STT",       mixed.stt_min     + " min",   "teal"],
          ].map(([label, val, color]) => (
            <div key={label} className={`p-2 rounded bg-${color}-500/5 border border-${color}-500/15 text-center`}>
              <div className="text-[9px] text-zinc-500 uppercase">{label}</div>
              <div className={`text-xs font-bold font-mono text-${color}-400`}>{val}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Live cost — 8 dedicated tracks, 8 separate contributions */}
      <div className="p-2.5 rounded-lg bg-teal-500/5 border border-teal-500/20 text-[11px] space-y-1">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="text-zinc-500">LLM cost at this mix:</span>
          <span className="font-mono text-teal-400 font-semibold">${totalCost.toFixed(4)}</span>
          <span className="text-[9px] text-zinc-600 ml-auto">Each track billed at its DEDICATED rate · no merging</span>
        </div>
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[10px]">
          <span className="text-emerald-400 font-mono">${costByCat.chat.toFixed(4)} chat</span>
          <span className="text-violet-400 font-mono">${costByCat.code.toFixed(4)} code</span>
          <span className="text-rose-400 font-mono">${costByCat.image_std.toFixed(4)} img-std</span>
          <span className="text-fuchsia-400 font-mono">${costByCat.image_hd.toFixed(4)} img-hd</span>
          <span className="text-amber-400 font-mono">${costByCat.video.toFixed(4)} video</span>
          <span className="text-sky-400 font-mono">${costByCat.voiceover.toFixed(4)} voice</span>
          <span className="text-cyan-400 font-mono">${costByCat.tts.toFixed(4)} tts</span>
          <span className="text-teal-400 font-mono">${costByCat.stt.toFixed(4)} stt</span>
        </div>
      </div>
    </div>
  );
}

// DEFAULT_ENGINE_CONFIG is imported from utils/pricingMath.js so backend
// and frontend share the same defaults. Do not redeclare it here.

export const PricingManagerTab = ({
  pricingConfig, setPricingConfig,
  pricingEdit, setPricingEdit,
  calcInputs, setCalcInputs,
  calcResult, setCalcResult,
  liveCost, token,
  onDeletePlan, onAddPlan,
}) => {
  const headers = token
    ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    : {};

  const [showModelRef, setShowModelRef] = useState(false);
  const [sortByCost, setSortByCost] = useState(true);   // cheapest first by default
  const [freeOnly, setFreeOnly] = useState(false);      // hide paid rows filter
  const [showNewPlan, setShowNewPlan] = useState(false);
  const [newPlanId, setNewPlanId] = useState("");
  const [newPlan, setNewPlan] = useState({ ...BLANK_PLAN });
  const [newFeatureInputs, setNewFeatureInputs] = useState({});
  // Which plan cards are expanded to show the full editor (vs collapsed
  // to just the summary row). Default: all collapsed so the page is a clean
  // overview; click a row to edit. Toggling All expands/collapses every plan.
  const [expandedPlans, setExpandedPlans] = useState(() => new Set());
  const togglePlanExpanded = (pid) => {
    setExpandedPlans(prev => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid); else next.add(pid);
      return next;
    });
  };

  // Full ledger (LLM + media + email + voice + amortization) and cost-config
  // toggles — drive the "All-In Cost" column + "Cost Optimization" panel.
  const [fullLedger, setFullLedger] = useState(null);
  const [costConfig, setCostConfig] = useState(null);
  // Per-category blended cost — chat, code, image, video, voice ($/credit
  // each). Drives the 5-card strip under the main Effective card. Gives
  // the operator per-workload cost visibility instead of one misleading
  // overall blended figure.
  const [blendedByCategory, setBlendedByCategory] = useState(null);
  const _auth = () => ({ Authorization: `Bearer ${localStorage.getItem("token") || ""}` });
  const fetchFullLedger = async () => {
    try {
      const r = await fetch(`${API}/admin/pricing/full-ledger`, { headers: _auth() });
      if (r.ok) setFullLedger(await r.json());
    } catch (_) { /* ignore; UI keeps '…' until next fetch */ }
  };
  const fetchCostConfig = async () => {
    try {
      const r = await fetch(`${API}/admin/cost-config`, { headers: _auth() });
      if (r.ok) setCostConfig(await r.json());
    } catch (_) { /* ignore */ }
  };
  const fetchBlendedByCategory = async () => {
    try {
      const r = await fetch(`${API}/admin/pricing/blended-by-category`, { headers: _auth() });
      if (r.ok) setBlendedByCategory(await r.json());
    } catch (_) { /* ignore */ }
  };
  // Per-category revenue rollup (30-day window) for the "so which category
  // makes me money" panel. Reads category_topups tagged at Stripe webhook.
  const [revenueByCategory, setRevenueByCategory] = useState(null);
  const fetchRevenueByCategory = async () => {
    try {
      const r = await fetch(`${API}/admin/metrics/revenue-by-category?days=30`, { headers: _auth() });
      if (r.ok) setRevenueByCategory(await r.json());
    } catch (_) { /* ignore */ }
  };
  // Quality-gate telemetry (24-hour window) — escalation rate from the
  // cheap-tier confidence gate in llm_gateway. Lets operator see whether
  // the gate is firing appropriately (10-20% is healthy).
  const [qualityGate, setQualityGate] = useState(null);
  const fetchQualityGate = async () => {
    try {
      const r = await fetch(`${API}/admin/metrics/quality-gate?hours=24`, { headers: _auth() });
      if (r.ok) setQualityGate(await r.json());
    } catch (_) { /* ignore */ }
  };
  // plans_v2 carries per-bucket allowances — how each plan's total
  // credits split across the 6 paid pools (chat/vibe/image/video/voice/stt)
  // + agent_sop + general fallback. Operator needs this to answer "how
  // much code quota does Studio actually give?" without math in their head.
  const [plansV2, setPlansV2] = useState(null);
  const fetchPlansV2 = async () => {
    try {
      const r = await fetch(`${API}/plans`);
      if (r.ok) {
        const d = await r.json();
        setPlansV2(Array.isArray(d.plans_v2) ? d.plans_v2 : null);
      }
    } catch (_) { /* ignore */ }
  };
  useEffect(() => { fetchFullLedger(); fetchCostConfig(); fetchBlendedByCategory(); fetchRevenueByCategory(); fetchQualityGate(); fetchPlansV2(); }, []);

  const { ai_cost_per_credit, target_profit_margin, bdt_exchange_rate } = calcInputs;

  // ── Price Markup % — direct, unbounded ────────────────────────────
  // `target_profit_margin` is stored as a MARKUP percentage — i.e. the
  // value IS the markup you want applied. Price = cost × (1 + markup/100).
  // No conversion, no caps, no precision loss: 200%, 1000%, 5000% all
  // stored and displayed verbatim. Multi-digit operator workflows
  // (SaaS pricing often quotes "500% markup" or "10× cost") are served
  // directly. The per-plan "% margin" badge below still shows the true
  // profit-margin ratio (profit ÷ price) for honest reporting.
  const currentMarkupPct = parseFloat(target_profit_margin) || 0;
  const priceMultiplierFromMarkup = (markupPct) => 1 + (parseFloat(markupPct) || 0) / 100;

  // ── Effective-cost resolution — single source of truth for every plan. ──
  // Once the operator locks a configuration, the locked snapshot becomes
  // authoritative and drives all per-plan USD math. The live measurement is
  // kept visible as a drift reference so the operator can see when market
  // conditions have moved enough to justify re-locking.
  const lockedSnapshot = pricingConfig?.ai_cost_locked_snapshot || null;
  const liveCostPerCredit = ai_cost_per_credit || 0.00003;
  const effectiveCostPerCredit = lockedSnapshot?.ai_cost_per_credit ?? liveCostPerCredit;
  const effectiveMarginPct      = lockedSnapshot?.target_profit_margin ?? target_profit_margin ?? 200;
  const effectiveBdtRate        = lockedSnapshot?.bdt_exchange_rate    ?? bdt_exchange_rate    ?? 107;
  const costDriftPct = lockedSnapshot?.ai_cost_per_credit
    ? ((liveCostPerCredit - lockedSnapshot.ai_cost_per_credit)
        / Math.max(lockedSnapshot.ai_cost_per_credit, 1e-9)) * 100
    : 0;
  // `costPerCredit` is the value every plan card uses. When locked, it's the
  // snapshot; otherwise it tracks live. Changing the local edit inputs does
  // NOT move this until the operator locks again — that's the whole point
  // of a lock.
  const costPerCredit = effectiveCostPerCredit;

  // ── Live calculations ──
  // All formulas routed through utils/pricingMath.js so they stay in lockstep
  // with the backend. Semantics:
  //   AI Cost       = credits × blended cost per credit (client's strict cap)
  //   Price         = what you charge (manual OR auto from margin target)
  //   Profit        = Price - AI Cost
  //   Margin %      = (Profit / AI Cost) × 100
  //   Operator Share = Profit / Price (derived)
  const activePlans = pricingEdit?.plans || {};
  const liveCalcs = {};
  for (const [pid, plan] of Object.entries(activePlans)) {
    const credits = plan.credits || 0;
    const priceUsd = plan.price_usd || 0;
    const aiCost  = aiCostUsd(credits, costPerCredit);
    const profit  = profitUsd(priceUsd, aiCost);

    liveCalcs[pid] = {
      credits,
      name: plan.name || pid,
      priceUsd,
      aiCost,
      profit,
      marginPct:        marginPct(profit, aiCost),
      operatorSharePct: operatorSharePct(profit, priceUsd),
      suggestedPrice:   pid === "free" ? 0 : suggestedPrice(aiCost, target_profit_margin || 200),
      recBdt:           usdToBdt(priceUsd, effectiveBdtRate),
    };
  }

  // Auto-sync BDT on all plans whenever exchange rate changes
  useEffect(() => {
    if (!pricingEdit || !bdt_exchange_rate) return;
    setPricingEdit(prev => ({
      ...prev,
      plans: Object.fromEntries(
        Object.entries(prev.plans).map(([id, plan]) => [
          id,
          { ...plan, price_bdt: usdToBdt(plan.price_usd || 0, bdt_exchange_rate) },
        ])
      ),
    }));
  }, [bdt_exchange_rate]);

  const handlePublishPricing = async () => {
    if (!pricingEdit) return;
    // Stamp computed BDT and cap onto every plan before saving.
    // calcInputs fields (ai_cost_per_credit, target_profit_margin,
    // bdt_exchange_rate) live in separate state — merge them in here so the
    // backend doesn't fall back to its hard-coded defaults and silently reset
    // the live blended cost.
    const stamped = {
      ...pricingEdit,
      plans: stampDerived(pricingEdit.plans, bdt_exchange_rate || 107, ai_cost_per_credit || 0),
      ai_cost_per_credit,
      target_profit_margin,
      bdt_exchange_rate,
    };
    try {
      const res = await fetch(`${API}/admin/pricing`, {
        method: "PUT",
        headers,
        body: JSON.stringify(stamped),
      });
      if (res.ok) {
        const data = await res.json();
        setPricingConfig(data.pricing);
        toast.success("Pricing published — changes are now live.");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to publish pricing");
      }
    } catch {
      toast.error("Failed to publish pricing");
    }
  };

  const handleLoadPresets = () => {
    if (!window.confirm("Replace all plans with the MAARS preset tiers ($50 → $8,000)? The Free plan is kept. You can still edit before publishing.")) return;
    const presets = buildPresets(bdt_exchange_rate || 107);
    const withDerived = stampDerived(presets, bdt_exchange_rate || 107, ai_cost_per_credit || 0);
    setPricingEdit(prev => ({
      ...prev,
      plans: withDerived,
    }));
    toast.success("Preset plans loaded — review and publish when ready.");
  };

  // Load the UNIFIED 5-tier preset (Free/Creator/Studio/Scale/Infinity).
  // This is the canonical catalog served on /api/plans plans_v2 and used
  // by the token_quota hard-cap system. Swapping here + publishing aligns
  // the PricingManager with the buyer-facing site.
  const handleLoadUnifiedPresets = () => {
    if (!window.confirm(
      "Replace with the UNIFIED 5-tier catalog (Free, Creator $29, Studio $99, Scale $299, Infinity $999)?\n\n" +
      "This is what the public pricing page already shows. Publishing here brings the admin editor in sync. " +
      "Existing subscribers keep their plan_id via LEGACY_TO_UNIFIED mapping."
    )) return;
    const presets = buildUnifiedPresets();
    const withDerived = stampDerived(presets, bdt_exchange_rate || 107, ai_cost_per_credit || 0);
    setPricingEdit(prev => ({ ...prev, plans: withDerived }));
    toast.success("Unified 5-tier preset loaded. Tokens auto-derived from credits × 100k.");
  };

  // When price_usd changes on a plan, auto-derive BDT
  const updatePlanField = (planId, field, value) => {
    setPricingEdit(prev => {
      const plan = prev.plans[planId];
      let parsed;
      if (field === "includes_commander") {
        parsed = value;
      } else if (typeof plan[field] === "number" || field === "price_usd" || field === "credits" || field === "max_agents" || field === "max_custom_agents" || field === "max_team_members") {
        parsed = parseFloat(value) || 0;
      } else {
        parsed = value;
      }
      const updates = { [field]: parsed };
      // BDT always follows USD
      if (field === "price_usd") {
        updates.price_bdt = usdToBdt(parseFloat(value) || 0, bdt_exchange_rate);
      }
      return {
        ...prev,
        plans: { ...prev.plans, [planId]: { ...plan, ...updates } },
      };
    });
  };

  const addFeatureToPlan = (planId, feature) => {
    if (!feature.trim()) return;
    setPricingEdit(prev => ({
      ...prev,
      plans: {
        ...prev.plans,
        [planId]: { ...prev.plans[planId], features: [...(prev.plans[planId].features || []), feature.trim()] },
      },
    }));
  };

  const removeFeatureFromPlan = (planId, idx) => {
    setPricingEdit(prev => ({
      ...prev,
      plans: {
        ...prev.plans,
        [planId]: { ...prev.plans[planId], features: (prev.plans[planId].features || []).filter((_, i) => i !== idx) },
      },
    }));
  };

  const syncAllBdtPricing = (newRate) => {
    setCalcInputs(p => ({ ...p, bdt_exchange_rate: newRate }));
    // useEffect above handles syncing plans
  };

  const applyMarginToPlans = () => {
    if (!pricingEdit) return;
    // Markup is the direct multiplier % — whatever the operator typed,
    // no clamps. price = cost × (1 + markup/100). 5000% → 51× cost.
    const markup = currentMarkupPct || 0;
    const mult   = priceMultiplierFromMarkup(markup);
    setPricingEdit(prev => ({
      ...prev,
      plans: Object.fromEntries(
        Object.entries(prev.plans).map(([id, plan]) => {
          if (id === "free") return [id, plan];
          // Use all-in cost from ledger when available so markup math
          // reflects the real monthly cost (infra + categorical LLM),
          // not just credits × blended rate.
          const ledgerRow = (fullLedger?.plans || []).find(p => p.plan_id === id);
          const allInCost = ledgerRow?.expected_costs?.total;
          const credits   = plan.credits || 0;
          const flatCost  = aiCostUsd(credits, costPerCredit);
          const cost      = (allInCost != null && allInCost > 0) ? allInCost : flatCost;
          const newPrice  = Math.round(cost * mult * 100) / 100;
          return [id, {
            ...plan,
            price_usd: newPrice,
            price_bdt: usdToBdt(newPrice, bdt_exchange_rate),
          }];
        })
      ),
    }));
    toast.success(`Prices auto-set at ${markup.toLocaleString()}% markup (price = all-in cost × ${mult.toLocaleString(undefined, { maximumFractionDigits: 2 })})`);
  };

  const handleCreatePlan = async () => {
    const id = newPlanId.trim().toLowerCase().replace(/\s+/g, "_");
    if (!id) { toast.error("Plan ID required"); return; }
    if (!newPlan.name.trim()) { toast.error("Plan name required"); return; }
    if (pricingEdit?.plans[id]) { toast.error(`Plan ID "${id}" already exists`); return; }

    const planWithDerived = {
      ...newPlan,
      price_bdt:       usdToBdt(newPlan.price_usd || 0, effectiveBdtRate),
      monthly_cap_usd: aiCostUsd(newPlan.credits || 0, effectiveCostPerCredit),
    };
    if (onAddPlan) {
      await onAddPlan(id, planWithDerived);
    } else {
      setPricingEdit(prev => ({ ...prev, plans: { ...prev.plans, [id]: planWithDerived } }));
    }
    setNewPlanId("");
    setNewPlan({ ...BLANK_PLAN });
    setShowNewPlan(false);
    toast.success(`Plan "${newPlan.name}" added — publish to make it live.`);
  };

  // ── Pricing Engine Config ── global per-unit credit costs. Operator sets
  // once here, every plan's auto-derived media capacity + cap recomputes.
  const engineConfig = {
    ...DEFAULT_ENGINE_CONFIG,
    ...(pricingEdit?.engine_config || {}),
  };
  const updateEngineConfig = (field, value) => {
    const v = parseFloat(value) || 0;
    setPricingEdit(prev => ({
      ...prev,
      engine_config: { ...(prev.engine_config || DEFAULT_ENGINE_CONFIG), [field]: v },
    }));
  };

  // ── Engine Config: lock + dirty-state ──
  // Dirty when current edit differs from last published snapshot — covers
  // both the engine_config block AND the AI-cost fields (ai_cost_per_credit,
  // target_profit_margin, bdt_exchange_rate). These live in calcInputs and
  // drive every plan's USD cap, so a lock that ignores them would be stale
  // within one cost refresh cycle.
  const publishedEngineConfig = pricingConfig?.engine_config || null;
  const engineConfigDirty = publishedEngineConfig
    ? JSON.stringify(pricingEdit?.engine_config || DEFAULT_ENGINE_CONFIG)
      !== JSON.stringify({ ...DEFAULT_ENGINE_CONFIG, ...publishedEngineConfig })
    : Object.keys(pricingEdit?.engine_config || {}).length > 0;
  const aiCostDirty = pricingConfig
    ? (Math.abs((pricingConfig.ai_cost_per_credit ?? 0) - (ai_cost_per_credit ?? 0)) > 1e-9)
      || ((pricingConfig.target_profit_margin ?? 200) !== (target_profit_margin ?? 200))
      || ((pricingConfig.bdt_exchange_rate ?? 107) !== (bdt_exchange_rate ?? 107))
    : false;
  const configDirty = engineConfigDirty || aiCostDirty;
  const lockedAt = pricingConfig?.engine_config_locked_at;
  const lockedBy = pricingConfig?.engine_config_locked_by;

  const handleLockEngineConfig = async () => {
    if (!pricingEdit) return;
    const stamped = {
      ...pricingEdit,
      plans: stampDerived(pricingEdit.plans, bdt_exchange_rate || 107, ai_cost_per_credit || 0),
      engine_config: engineConfig,
      ai_cost_per_credit,
      target_profit_margin,
      bdt_exchange_rate,
      engine_config_lock: true,
    };
    try {
      const res = await fetch(`${API}/admin/pricing`, {
        method: "PUT",
        headers,
        body: JSON.stringify(stamped),
      });
      if (res.ok) {
        const data = await res.json();
        setPricingConfig(data.pricing);
        toast.success("Engine config locked — timestamp stamped.");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to lock config");
      }
    } catch {
      toast.error("Failed to lock config");
    }
  };
  const updatePlanMedia = (planId, field, rawValue) => {
    // Tri-state: "" → null (auto), "-1" → -1 (disabled), number → cap.
    let value = null;
    if (rawValue === "" || rawValue === null || rawValue === undefined) value = null;
    else if (String(rawValue).trim() === "-1") value = -1;
    else value = parseInt(rawValue, 10);
    if (Number.isNaN(value)) value = null;
    setPricingEdit(prev => {
      const plan = prev.plans[planId];
      return {
        ...prev,
        plans: {
          ...prev.plans,
          [planId]: {
            ...plan,
            media: { ...(plan.media || {}), [field]: value },
          },
        },
      };
    });
  };
  // Auto-compute a plan's effective media cap for a given field.
  // If plan.media[field] is null → derive from credits ÷ per-unit cost.
  // If -1 → disabled. Otherwise → explicit cap.
  const effectiveMediaCap = (plan, field, perUnitCost) => {
    const explicit = plan?.media?.[field];
    if (explicit === -1) return { value: 0, label: "disabled", derived: false };
    if (explicit == null) {
      const derived = Math.floor((plan?.credits || 0) / Math.max(perUnitCost, 1));
      return { value: derived, label: `${derived} (auto)`, derived: true };
    }
    return { value: explicit, label: `${explicit} (cap)`, derived: false };
  };

  return (
    <div className="space-y-6">

      {/* ── Active Pricing Configuration ─────────────────────────────────
          ONE card, ONE source of truth. Every per-plan calculation below
          reads from the numbers shown here. When locked, those numbers are
          frozen as a snapshot; live measurements stay visible as a drift
          reference. When unlocked, the live blended cost flows through. */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 flex-wrap">
            <div className="w-10 h-10 rounded-lg bg-teal-500/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-teal-400" />
            </div>
            Active Pricing Configuration
            <Badge className="bg-teal-500/20 text-teal-400 text-[10px]">DRIVES ALL PLANS</Badge>
            {lockedAt ? (
              <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px] flex items-center gap-1">
                <Lock className="w-3 h-3" />
                Locked {new Date(lockedAt).toLocaleString()}
                {lockedBy ? ` · ${lockedBy}` : ""}
              </Badge>
            ) : (
              <Badge className="bg-zinc-500/20 text-zinc-400 text-[10px] flex items-center gap-1">
                <Unlock className="w-3 h-3" />
                Never locked
              </Badge>
            )}
            {configDirty && (
              <Badge className="bg-amber-500/20 text-amber-400 text-[10px] animate-pulse">
                Unsaved changes
              </Badge>
            )}
            <div className="ml-auto flex items-center gap-2">
              <Button
                size="sm"
                onClick={handleLockEngineConfig}
                className="bg-emerald-600 hover:bg-emerald-700 text-white h-8 text-xs gap-1.5"
              >
                <Lock className="w-3.5 h-3.5" />
                Lock Configuration
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* ── Cost-source row — Live vs Locked vs Effective vs Drift ──
              This is the ONE source of truth. Every plan card below uses
              "Effective" for its USD math. "Live" is informational only. */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Blended (chat-dominant)
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </p>
              <p className="text-lg font-bold text-zinc-300 font-mono">${liveCostPerCredit.toFixed(6)}</p>
              <p className="text-[9px] text-zinc-600">{liveCost.total_calls?.toLocaleString() || 0} calls · most are chat; see per-plan below</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Locked Snapshot
                {lockedSnapshot ? <Lock className="w-2.5 h-2.5 text-emerald-400" /> : <Unlock className="w-2.5 h-2.5 text-zinc-500" />}
              </p>
              <p className={`text-lg font-bold font-mono ${lockedSnapshot ? "text-emerald-400" : "text-zinc-600"}`}>
                {lockedSnapshot ? `$${lockedSnapshot.ai_cost_per_credit.toFixed(6)}` : "—"}
              </p>
              <p className="text-[9px] text-zinc-600">
                {lockedSnapshot ? `locked ${new Date(lockedSnapshot.locked_at).toLocaleDateString()}` : "lock to freeze current values"}
              </p>
            </div>
            <div className="p-2 rounded-lg bg-zinc-800/40 border border-white/10 -m-2">
              <p className="text-[10px] text-zinc-400 mb-0.5 font-semibold">
                Flat Fallback $/credit
              </p>
              <p className="text-lg font-bold text-zinc-300 font-mono">${effectiveCostPerCredit.toFixed(6)}</p>
              <p className="text-[9px] text-zinc-600">used only when a plan has no mix · real math is per-plan below</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5">Drift (live vs locked)</p>
              <p className={`text-lg font-bold font-mono ${
                !lockedSnapshot ? "text-zinc-600" :
                Math.abs(costDriftPct) > 20 ? "text-red-400" :
                Math.abs(costDriftPct) > 5 ? "text-amber-400" : "text-emerald-400"
              }`}>
                {lockedSnapshot ? `${costDriftPct >= 0 ? "+" : ""}${costDriftPct.toFixed(1)}%` : "—"}
              </p>
              <p className="text-[9px] text-zinc-600">
                {!lockedSnapshot ? "no lock yet" :
                 Math.abs(costDriftPct) > 20 ? "re-lock recommended" :
                 Math.abs(costDriftPct) > 5 ? "minor drift" : "in sync"}
              </p>
            </div>
          </div>
          <p className="text-[11px] text-zinc-500 leading-relaxed">
            The blended figure above is chat-dominant — {liveCost.total_calls?.toLocaleString() || 0} calls measured, almost all text.
            <strong className="text-amber-400"> Pricing math sums each deliverable at its DEDICATED per-track rate</strong> (the 8 cards below).
            Image-Std / Image-HD / Video / Voiceover / TTS / STT each carry their own $/credit — no merging, no averaging.
            Enforcement is <strong>cost-cap per user</strong> (monthly_cap_usd on each plan), not token counts.
          </p>

          {/* ── Per-track dedicated blended strip — 8 workload tracks ──
              Each deliverable type has its own $/credit rate and its own
              routing policy. Routing: free-first; router escalates to
              premium only when the quality-score on the cheap tier falls
              below threshold — clients never get "just get it over with"
              outputs. Label under each card summarises the escalation
              tier so operator sees the policy at a glance. */}
          {blendedByCategory && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
              {[
                { key: "chat",      label: "Chat",        color: "emerald", routing: "Free-first · escalates to Claude/GPT-4 on complex reasoning" },
                { key: "code",      label: "Code / Vibe", color: "violet",  routing: "DeepSeek Coder · Qwen Coder · escalates to Claude Opus on architecture" },
                { key: "image_std", label: "Image Std",   color: "rose",    routing: "Pollinations (free) · escalates to Flux on finer detail" },
                { key: "image_hd",  label: "Image HD",    color: "fuchsia", routing: "Flux HD primary · premium-tier default" },
                { key: "video",     label: "Video",       color: "amber",   routing: "Fal LTX · escalates to Sora/Runway for cinematic tier" },
                { key: "voiceover", label: "Voiceover",   color: "sky",     routing: "ElevenLabs premium voices · studio-quality default" },
                { key: "tts",       label: "TTS",         color: "cyan",    routing: "Edge TTS (free) · escalates to ElevenLabs if client flags quality" },
                { key: "stt",       label: "STT",         color: "teal",    routing: "Groq Whisper (free) · Whisper Large V3 · near-premium accuracy" },
              ].map(({ key, label, color, routing }) => {
                const cat = blendedByCategory[key] || {};
                const val = cat.value || 0;
                const src = cat.source || "—";
                const calls = cat.call_count || 0;
                const freePct = cat.free_routing_pct || 0;
                const isMeasured = src === "real_usage" || src === "real_usage_calls_proxy";
                const isFree = val === 0;
                const colorMap = {
                  emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
                  violet:  "text-violet-400  bg-violet-500/10  border-violet-500/30",
                  rose:    "text-rose-400    bg-rose-500/10    border-rose-500/30",
                  fuchsia: "text-fuchsia-400 bg-fuchsia-500/10 border-fuchsia-500/30",
                  amber:   "text-amber-400   bg-amber-500/10   border-amber-500/30",
                  sky:     "text-sky-400     bg-sky-500/10     border-sky-500/30",
                  cyan:    "text-cyan-400    bg-cyan-500/10    border-cyan-500/30",
                  teal:    "text-teal-400    bg-teal-500/10    border-teal-500/30",
                };
                return (
                  <div key={key} className={`p-2 rounded-xl border ${colorMap[color]}`} title={routing}>
                    <p className="text-[10px] font-semibold mb-0.5 flex items-center gap-1">
                      {label}
                      <span className={`inline-block w-1.5 h-1.5 rounded-full ${isMeasured ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"}`} />
                    </p>
                    <p className="text-sm font-bold font-mono">{isFree ? "FREE" : `$${val.toFixed(8)}`}</p>
                    <p className="text-[9px] text-zinc-500 mt-0.5 truncate">
                      {isMeasured ? `${calls.toLocaleString()} calls · ${freePct.toFixed(0)}% free` : (cat.mix_assumption || "configured")}
                    </p>
                    <p className="text-[9px] text-zinc-600/80 mt-0.5 truncate leading-tight" title={routing}>
                      {routing}
                    </p>
                  </div>
                );
              })}
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-10 gap-3">
            {/* Tokens/Credit removed from operator UI — cost caps
                (monthly_cap_usd) are the authoritative enforcement. The
                token ratio stays in the backend token_quota for defense
                in depth but isn't a pricing lever. */}
            <div className="space-y-1">
              <Label className="text-emerald-400 text-xs">Chat / msg</Label>
              <Input
                type="number" step="0.001"
                value={engineConfig.chat_credits_per_msg ?? 0.015}
                onChange={(e) => updateEngineConfig("chat_credits_per_msg", e.target.value)}
                className="bg-zinc-800/50 border-emerald-500/30 border h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per chat msg</p>
            </div>
            <div className="space-y-1">
              <Label className="text-violet-400 text-xs">Code / run</Label>
              <Input
                type="number" step="0.01"
                value={engineConfig.code_credits_per_run ?? 0.04}
                onChange={(e) => updateEngineConfig("code_credits_per_run", e.target.value)}
                className="bg-zinc-800/50 border-violet-500/30 border h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per code run</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Image Standard</Label>
              <Input
                type="number"
                value={engineConfig.image_std_credits}
                onChange={(e) => updateEngineConfig("image_std_credits", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per 1024² image</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Image HD</Label>
              <Input
                type="number"
                value={engineConfig.image_hd_credits}
                onChange={(e) => updateEngineConfig("image_hd_credits", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per HD image</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Video / sec</Label>
              <Input
                type="number"
                value={engineConfig.video_credits_per_sec}
                onChange={(e) => updateEngineConfig("video_credits_per_sec", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per second</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">TTS / min</Label>
              <Input
                type="number"
                value={engineConfig.tts_credits_per_min}
                onChange={(e) => updateEngineConfig("tts_credits_per_min", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per TTS minute</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Voice-Over / min</Label>
              <Input
                type="number"
                value={engineConfig.voiceover_credits_per_min}
                onChange={(e) => updateEngineConfig("voiceover_credits_per_min", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per VO minute</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">STT / min</Label>
              <Input
                type="number"
                value={engineConfig.stt_credits_per_min}
                onChange={(e) => updateEngineConfig("stt_credits_per_min", e.target.value)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">credits per STT minute</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Price Markup %</Label>
              <Input
                type="number"
                step="any"
                min="0"
                value={currentMarkupPct}
                onChange={(e) => setCalcInputs(p => ({
                  ...p,
                  target_profit_margin: parseFloat(e.target.value) || 0,
                }))}
                className="bg-zinc-800/50 border-amber-500/30 border h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">price = cost × (1 + markup/100) · 200% = 3× cost · 1000% = 11× cost · 5000% = 51× cost</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">BDT Rate</Label>
              <Input
                type="number"
                value={bdt_exchange_rate}
                onChange={(e) => syncAllBdtPricing(parseFloat(e.target.value) || 0)}
                className="bg-zinc-800/50 border-white/10 h-9 text-sm text-white font-mono"
              />
              <p className="text-[9px] text-zinc-600">1 USD = ৳{bdt_exchange_rate}</p>
            </div>
          </div>
          {/* ── Interactive Media Budget Calculator ─────────────────────
              Type or drag a credit budget; every media ceiling updates live.
              The operator can use this to sanity-check a plan's credit pool
              BEFORE deciding what the hard caps should be in the plan editor. */}
          <MediaBudgetCalculator engineConfig={engineConfig} blendedByCategory={blendedByCategory} />
          {/* Tip uses the real engine_config rates, shows ∞ for free
              modalities (std images, TTS, STT at 0 credits each), and
              matches the Deliverables editor's per-unit math. */}
          <div className="text-[10px] text-zinc-500 p-2 rounded bg-teal-500/5 border border-teal-500/10">
            {(() => {
              const tpc  = engineConfig.tokens_per_credit || 100000;
              const hd   = engineConfig.image_hd_credits || 0;
              const vsec = engineConfig.video_credits_per_sec || 0;
              const tts  = engineConfig.tts_credits_per_min || 0;
              const vo   = engineConfig.voiceover_credits_per_min || 0;
              const per  = (divisor) => !divisor ? "∞" : Math.floor(1000 / divisor).toLocaleString();
              return (
                <>
                  <strong className="text-teal-400">Tip:</strong> At current settings, per 1,000 credits a client could produce either:
                  {" "}<strong className="text-white">{per(hd)}</strong> HD images
                  · <strong className="text-white">{per(vsec)}</strong> sec video
                  · <strong className="text-white">{per(vo)}</strong> min voiceover
                  · <strong className="text-white">{per(tts)}</strong> min TTS.
                  Std images / TTS / STT are free-tier (Pollinations / Edge / Whisper) unless you set a credit cost above.
                </>
              );
            })()}
          </div>
        </CardContent>
      </Card>

      {/* ── Revenue by Category (30-day) ─────────────────────────────
          Reads category_topups populated on Stripe webhook when a client
          buys a category-tagged credit pack. Each row = one of the 8
          tracks + a "general" row for untagged purchases. Operator sees
          at a glance: which category pulls the most revenue, what it
          actually cost to serve (credits × dedicated rate), what margin
          survived. Empty rows render at $0 so the full category set is
          visible from day one. */}
      {revenueByCategory && (
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
            </div>
            Revenue by Category (30-day)
            <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px] ml-2">
              {revenueByCategory.total_topups} top-ups · ${(revenueByCategory.total_revenue_usd || 0).toFixed(2)} revenue
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-zinc-500 border-b border-white/5">
                  <th className="text-left py-2 font-normal">Category</th>
                  <th className="text-right py-2 font-normal">Top-ups</th>
                  <th className="text-right py-2 font-normal">Credits sold</th>
                  <th className="text-right py-2 font-normal">Revenue</th>
                  <th className="text-right py-2 font-normal" title="credits × blended $/credit for this track">Est. COGS</th>
                  <th className="text-right py-2 font-normal">Profit</th>
                  <th className="text-right py-2 font-normal">Margin</th>
                  <th className="text-right py-2 font-normal">Share</th>
                </tr>
              </thead>
              <tbody>
                {(revenueByCategory.per_category || []).map(row => {
                  const colorMap = {
                    chat:      "text-emerald-400",
                    code:      "text-violet-400",
                    image_std: "text-rose-300",
                    image_hd:  "text-fuchsia-400",
                    video:     "text-amber-400",
                    voiceover: "text-sky-400",
                    tts:       "text-cyan-400",
                    stt:       "text-teal-400",
                    general:   "text-zinc-400",
                  };
                  const labelMap = {
                    chat: "Chat", code: "Code / Vibe",
                    image_std: "Image Std", image_hd: "Image HD",
                    video: "Video", voiceover: "Voiceover",
                    tts: "TTS", stt: "STT", general: "General (untagged)",
                  };
                  const empty = row.revenue_usd === 0;
                  return (
                    <tr key={row.category} className={`border-b border-white/5 hover:bg-white/[0.02] ${empty ? "opacity-40" : ""}`}>
                      <td className={`py-2 font-semibold ${colorMap[row.category] || "text-zinc-300"}`}>
                        {labelMap[row.category] || row.category}
                      </td>
                      <td className="py-2 text-right text-zinc-300 font-mono">{row.topups_count}</td>
                      <td className="py-2 text-right text-zinc-300 font-mono">{(row.credits_sold || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-white font-mono font-bold">${row.revenue_usd.toFixed(2)}</td>
                      <td className="py-2 text-right text-rose-400 font-mono">${row.cost_estimated_usd.toFixed(4)}</td>
                      <td className="py-2 text-right text-emerald-400 font-mono">${row.profit_usd.toFixed(2)}</td>
                      <td className="py-2 text-right font-mono">
                        <span className={
                          row.margin_pct === null ? "text-zinc-600" :
                          row.margin_pct >= 90 ? "text-emerald-400" :
                          row.margin_pct >= 50 ? "text-amber-400" : "text-rose-400"
                        }>
                          {row.margin_pct === null ? "—" : `${row.margin_pct}%`}
                        </span>
                      </td>
                      <td className="py-2 text-right text-zinc-400 font-mono">{row.share_of_revenue}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-zinc-600 mt-2">
            Est. COGS = credits_sold × per-category blended $/credit (live from 5-card strip above). Revenue comes from Stripe-tagged top-ups.
            Empty rows = no top-ups yet in that category — tag credit presets with a category in Custom Packages to start collecting data.
          </p>
        </CardContent>
      </Card>
      )}

      {/* ── Quality Gate (24-hour) ──────────────────────────────────
          Every cheap-tier call runs through the confidence_router.
          Low-confidence responses (by logprobs or hedge-phrase
          heuristics) get silently retried on maars/premium. This panel
          surfaces the firing rate so operator can tune the threshold:
            • 10-20% escalation = healthy
            • <5% = threshold too lax (weak responses slipping through)
            • >30% = cheap tier under-delivering for this traffic mix */}
      {qualityGate && (
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-violet-400" />
            </div>
            Quality Gate (24h)
            <Badge className="bg-violet-500/20 text-violet-400 text-[10px] ml-2">
              {qualityGate.total_assessed} assessed · {qualityGate.escalated_count} escalated · {qualityGate.escalation_rate_pct}% rate
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-zinc-800/40 border border-white/5">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wide">Calls assessed</p>
              <p className="text-2xl font-bold text-white font-mono">{qualityGate.total_assessed.toLocaleString()}</p>
              <p className="text-[9px] text-zinc-600 mt-0.5">cheap-tier calls in window</p>
            </div>
            <div className="p-3 rounded-xl bg-violet-500/10 border border-violet-500/30">
              <p className="text-[10px] text-violet-400 uppercase tracking-wide">Escalated</p>
              <p className="text-2xl font-bold text-violet-400 font-mono">{qualityGate.escalated_count.toLocaleString()}</p>
              <p className="text-[9px] text-zinc-500 mt-0.5">silently retried on premium</p>
            </div>
            <div className={`p-3 rounded-xl border ${
              qualityGate.escalation_rate_pct < 5 ? "bg-rose-500/10 border-rose-500/30" :
              qualityGate.escalation_rate_pct > 30 ? "bg-amber-500/10 border-amber-500/30" :
              "bg-emerald-500/10 border-emerald-500/30"
            }`}>
              <p className={`text-[10px] uppercase tracking-wide ${
                qualityGate.escalation_rate_pct < 5 ? "text-rose-400" :
                qualityGate.escalation_rate_pct > 30 ? "text-amber-400" : "text-emerald-400"
              }`}>Escalation rate</p>
              <p className={`text-2xl font-bold font-mono ${
                qualityGate.escalation_rate_pct < 5 ? "text-rose-400" :
                qualityGate.escalation_rate_pct > 30 ? "text-amber-400" : "text-emerald-400"
              }`}>{qualityGate.escalation_rate_pct}%</p>
              <p className="text-[9px] text-zinc-500 mt-0.5">
                {qualityGate.escalation_rate_pct < 5 ? "may need stricter threshold" :
                 qualityGate.escalation_rate_pct > 30 ? "cheap models under-delivering" : "healthy range"}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-zinc-800/40 border border-white/5">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wide">Avg confidence</p>
              <p className="text-2xl font-bold text-zinc-300 font-mono">
                {qualityGate.avg_score == null ? "—" : qualityGate.avg_score.toFixed(2)}
              </p>
              <p className="text-[9px] text-zinc-600 mt-0.5">0.0 uncertain → 1.0 confident</p>
            </div>
          </div>
          {/* By-method + by-tier breakdown */}
          {(Object.keys(qualityGate.by_method || {}).length > 0 || Object.keys(qualityGate.by_tier || {}).length > 0) && (
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-2.5 rounded-lg bg-white/5 border border-white/5">
                <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1.5">By signal method</p>
                <div className="space-y-1 text-[11px]">
                  {Object.entries(qualityGate.by_method || {}).map(([m, s]) => (
                    <div key={m} className="flex items-center justify-between">
                      <span className="text-zinc-300">{m}</span>
                      <span className="text-zinc-500 font-mono">
                        {s.count} · <span className="text-violet-400">{s.escalated} esc</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-white/5 border border-white/5">
                <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1.5">By client tier</p>
                <div className="space-y-1 text-[11px]">
                  {Object.entries(qualityGate.by_tier || {}).map(([t, s]) => (
                    <div key={t} className="flex items-center justify-between">
                      <span className="text-zinc-300 capitalize">{t}</span>
                      <span className="text-zinc-500 font-mono">
                        {s.count} · avg {s.avg_score} · <span className="text-violet-400">{s.escalated} esc</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          <p className="text-[10px] text-zinc-600 mt-2">
            Logprobs enabled on first-attempt cheap-tier calls (OpenAI / Groq / Cerebras / Fireworks / Together).
            Other providers fall back to hedge-phrase heuristic ("I'm not sure", "it depends", etc).
            Escalated calls flow to <span className="text-violet-400 font-mono">maars/premium</span>; the client sees only the final answer.
          </p>
        </CardContent>
      </Card>
      )}

      {/* ── Per-plan bucket allowances ───────────────────────────────
          Each plan's total credit grant splits across 6 DEDICATED pools
          (chat / vibe-code / image / video / voice / stt) + general
          fallback. Plans with `allow_general_fallback: true` flow
          excess usage into general so clients aren't hard-locked when
          they hit a category cap. Plans without fallback keep hard
          caps — prevents video abuse from draining the chat pool.

          Source: /api/plans.plans_v2[*].bucket_allowances + allow_general_fallback,
          computed by services/billing/plan_buckets.py. */}
      {plansV2 && plansV2.length > 0 && (
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            Per-Plan Credit Pools (Dedicated Buckets)
            <Badge className="bg-indigo-500/20 text-indigo-400 text-[10px] ml-2">
              {plansV2.length} plans · 6 paid pools each
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-zinc-500 border-b border-white/5">
                  <th className="text-left py-2 font-normal">Plan</th>
                  <th className="text-right py-2 font-normal">Total</th>
                  <th className="text-right py-2 font-normal text-emerald-400">Chat</th>
                  <th className="text-right py-2 font-normal text-violet-400">Code</th>
                  <th className="text-right py-2 font-normal text-rose-400">Image</th>
                  <th className="text-right py-2 font-normal text-amber-400">Video</th>
                  <th className="text-right py-2 font-normal text-sky-400">Voice</th>
                  <th className="text-right py-2 font-normal text-cyan-400">STT</th>
                  <th className="text-right py-2 font-normal text-zinc-400">Agent SOP</th>
                  <th className="text-right py-2 font-normal">Fallback</th>
                </tr>
              </thead>
              <tbody>
                {plansV2.map(plan => {
                  const b = plan.bucket_allowances || {};
                  return (
                    <tr key={plan.plan_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                      <td className="py-2 text-white font-semibold">{plan.name}</td>
                      <td className="py-2 text-right text-white font-mono font-bold">{(plan.credits || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-emerald-400 font-mono">{(b.chat || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-violet-400 font-mono">{(b.vibe || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-rose-400 font-mono">{(b.image || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-amber-400 font-mono">{(b.video || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-sky-400 font-mono">{(b.voice || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-cyan-400 font-mono">{(b.stt || 0).toLocaleString()}</td>
                      <td className="py-2 text-right text-zinc-400 font-mono">{(b.agent_sop || 0).toLocaleString()}</td>
                      <td className="py-2 text-right">
                        {plan.allow_general_fallback ? (
                          <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Enabled</Badge>
                        ) : (
                          <Badge className="bg-zinc-500/20 text-zinc-400 text-[10px]">Hard cap</Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-zinc-600 mt-2">
            Each plan's credits split across DEDICATED pools (ratios in
            <span className="font-mono text-zinc-400"> services/billing/plan_buckets.py</span>).
            <span className="text-emerald-400"> Fallback enabled</span> = over-cap usage flows to the general pool.
            <span className="text-zinc-400"> Hard cap</span> = pool exhaustion stops that category until top-up.
            Clients buy per-category top-ups on the pricing page; each pack lands in its matching bucket automatically.
          </p>
        </CardContent>
      </Card>
      )}

      {/* ── Plans & Preview (merged) ──
          One card, one list. Each plan is a collapsible row — collapsed
          shows the summary (credits · AI Cost · Price · Suggested · Profit
          · Margin); click the chevron to expand into the full editor. The
          Auto-Price button + Model Cost Reference sit at the top so every
          pricing control is in one place. */}
      {pricingEdit && (
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-2">
            <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-amber-400" />
              </div>
              Plans
              <Badge className="bg-teal-500/20 text-teal-400 text-[10px] ml-2">
                reads from Active Pricing ↑
              </Badge>
            </CardTitle>
            <div className="flex gap-2 flex-wrap">
              <Button
                size="sm" variant="outline"
                className="border-white/10 text-zinc-400 hover:bg-white/5 text-xs"
                onClick={() => {
                  const allIds = Object.keys(pricingEdit?.plans || {});
                  setExpandedPlans(expandedPlans.size === allIds.length ? new Set() : new Set(allIds));
                }}>
                {expandedPlans.size === Object.keys(pricingEdit?.plans || {}).length ? "Collapse all" : "Expand all"}
              </Button>
              <Button
                size="sm" variant="outline"
                className="border-teal-500/40 text-teal-300 hover:bg-teal-500/10 gap-1.5 text-xs font-semibold"
                onClick={handleLoadUnifiedPresets}
                title="Load the 5-tier catalog that matches the public pricing page (Free, Creator, Studio, Scale, Infinity). Each credit = 100,000 tokens hard-cap.">
                <Sparkles className="w-3.5 h-3.5" />
                Load UNIFIED 5-Tier Preset
              </Button>
              <Button
                size="sm" variant="outline"
                className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10 gap-1.5 text-xs"
                onClick={handleLoadPresets}
                title="Legacy 13-tier preset ($50 → $8,000). Retained for roll-back only; prefer the Unified preset above.">
                <Sparkles className="w-3.5 h-3.5" />
                Legacy 13-Tier
              </Button>
              <Button
                size="sm"
                className="bg-indigo-600 hover:bg-indigo-700 gap-1.5 text-xs"
                onClick={() => setShowNewPlan(v => !v)}>
                <Plus className="w-3.5 h-3.5" />
                New Plan
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-3 rounded-lg bg-teal-500/5 border border-teal-500/10 text-[11px] text-zinc-400 leading-relaxed">
            Every row below computes: <strong className="text-teal-400">AI Cost</strong> = credits × <span className="font-mono text-teal-400">${effectiveCostPerCredit.toFixed(6)}</span>
            {" "}({lockedSnapshot ? "locked" : "live, measured by Universal Gateway router"}) · <strong className="text-amber-400">Suggested Price</strong> = AI Cost × (1 + markup/100) ({currentMarkupPct.toLocaleString()}% markup target) ·
            {" "}<strong className="text-emerald-400">BDT</strong> = USD × {bdt_exchange_rate}.
            {liveCost.total_calls < 10 && (
              <span className="text-amber-400"> Live cost based on {liveCost.total_calls} test calls — will normalize with real traffic.</span>
            )}
          </div>

          {/* ── Inline Profit Margin Control + Auto-Price ──
              Profit Margin % (profit ÷ price) is the SaaS-standard metric
              — 95% means cost is 5% of price, i.e. price is 20× cost.
              Duplicated here from the Active Pricing panel so the operator
              can tweak without scrolling. Both inputs write to the same
              stored markup value via markupFromMargin(); the stored value
              stays as markup for DB back-compat. */}
          <div className="flex items-end gap-3 flex-wrap p-3 rounded-lg bg-white/5 border border-white/5">
            <div className="space-y-1">
              <Label className="text-zinc-400 text-xs">Price Markup % (price = cost × (1 + markup/100) · any value)</Label>
              <div className="flex items-center gap-1.5">
                {[100, 200, 500, 1000, 2000, 5000, 10000].map(m => {
                  const active = Math.abs(currentMarkupPct - m) < 0.5;
                  return (
                    <Button
                      key={m} size="sm" variant="outline"
                      className={`text-[10px] h-8 px-2 border-white/10 ${active ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : "text-zinc-400 hover:bg-white/5"}`}
                      onClick={() => setCalcInputs(p => ({ ...p, target_profit_margin: m }))}>
                      {m >= 1000 ? `${m/1000}k%` : `${m}%`}
                    </Button>
                  );
                })}
                <Input
                  type="number"
                  step="any"
                  min="0"
                  value={currentMarkupPct}
                  onChange={(e) => setCalcInputs(p => ({
                    ...p,
                    target_profit_margin: parseFloat(e.target.value) || 0,
                  }))}
                  className="bg-zinc-800/50 border-emerald-500/30 border h-8 w-28 text-sm text-white font-mono"
                />
                <span className="text-xs text-zinc-500 ml-1">%</span>
              </div>
              <p className="text-[10px] text-zinc-500">
                At {currentMarkupPct.toLocaleString()}% markup, price = cost × <span className="font-mono text-emerald-400">{priceMultiplierFromMarkup(currentMarkupPct).toLocaleString(undefined, { maximumFractionDigits: 2 })}×</span> — stamped into every Suggested column.
              </p>
            </div>
            <Button onClick={applyMarginToPlans}
              className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 ml-auto">
              Apply {currentMarkupPct.toLocaleString()}% Markup to All Plans
            </Button>
          </div>

          {/* Plan list renders below — each plan is a collapsible card.
              Model Cost Reference sits at the bottom of this card. */}
          {/* Model Cost Reference */}
          <div className="border border-white/10 rounded-lg overflow-hidden">
            <button
              className="w-full flex items-center justify-between px-4 py-3 text-sm text-zinc-400 hover:bg-white/5 transition-colors"
              onClick={() => setShowModelRef(v => !v)}>
              <span className="flex items-center gap-2">
                <Info className="w-4 h-4 text-indigo-400" />
                <span className="font-medium text-zinc-300">Model Cost Reference</span>
                <span className="text-[10px] text-zinc-500">— click a model to apply its cost per credit</span>
              </span>
              {showModelRef ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showModelRef && (() => {
              const tpc = engineConfig.tokens_per_credit || 1000;
              // Providers the smart router treats as free-tier (same set as
              // services.blended_cost.FREE_PROVIDERS). These route at $0 even
              // though their published per-token price is non-zero, because
              // the router uses their free-tier quota first.
              const FREE_TIER_PROVIDERS = new Set(["Groq", "Cerebras", "SambaNova", "Google", "HuggingFace", "NVIDIA", "Gemini"]);
              const rows = MODEL_COSTS.map(m => ({
                ...m,
                blended: ((m.input + m.output) / 2) * (tpc / 1_000_000),
                isFree: FREE_TIER_PROVIDERS.has(m.provider),
              }));
              const filtered = freeOnly ? rows.filter(r => r.isFree) : rows;
              const sorted = sortByCost ? [...filtered].sort((a, b) => a.blended - b.blended) : filtered;
              const cheapest = sorted[0];
              const paidSorted = rows.filter(r => !r.isFree).sort((a, b) => a.blended - b.blended);
              const cheapestPaid = paidSorted[0];
              // Live backend-measured blended cost (flows from shared
              // services.blended_cost.get_blended_cost_per_credit via the
              // /admin/avg-cost endpoint → liveCost prop). This is the REAL
              // $/credit the router is currently paying, including free-tier
              // routing. Compare to per-model pricebook values below to see
              // where the savings come from.
              const liveActual = liveCost?.avg_cost_per_credit;
              const liveSource = liveCost?.source;
              const freePct = liveCost?.free_routing_pct;
              return (
              <div className="px-4 pb-4 space-y-3">
                {/* ── Live-sync header + live actual cost banner ── */}
                <div className="flex flex-wrap items-center gap-3 p-2.5 rounded-lg bg-gradient-to-r from-teal-500/10 to-indigo-500/10 border border-teal-500/20">
                  <div className="flex items-center gap-2">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
                    <span className="text-[11px] text-teal-300 font-semibold uppercase tracking-wide">Live-synced</span>
                  </div>
                  <div className="text-[11px] text-zinc-400">
                    <span className="text-zinc-500">Tokens/Credit:</span>{" "}
                    <strong className="text-teal-400 font-mono">{tpc.toLocaleString()}</strong>
                    <span className="text-zinc-600 ml-1">(change in Pricing Engine Config above)</span>
                  </div>
                  {liveActual != null && (
                    <div className="text-[11px] text-zinc-400 ml-auto">
                      <span className="text-zinc-500">Actual blended cost across your active routes:</span>{" "}
                      <strong className="text-emerald-400 font-mono">${liveActual.toFixed(6)}/credit</strong>
                      {freePct != null && (
                        <span className="text-emerald-500 ml-1">· {freePct.toFixed(0)}% free-tier routing</span>
                      )}
                      <span className="text-zinc-600 ml-1 text-[9px] uppercase tracking-wider">
                        · {liveSource === "real_usage" ? "real usage" : liveSource === "estimated_from_model_pricing" ? "estimated" : "default"}
                      </span>
                    </div>
                  )}
                </div>

                {/* ── Controls row: sort + filter ── */}
                <div className="flex flex-wrap items-center gap-2 text-[11px]">
                  <button
                    onClick={() => setSortByCost(v => !v)}
                    className={`px-2.5 py-1 rounded border transition-colors ${
                      sortByCost
                        ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        : "bg-white/5 text-zinc-400 border-white/10 hover:text-white"
                    }`}
                  >
                    {sortByCost ? "↓ Cheapest first" : "Default order"}
                  </button>
                  <button
                    onClick={() => setFreeOnly(v => !v)}
                    className={`px-2.5 py-1 rounded border transition-colors ${
                      freeOnly
                        ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                        : "bg-white/5 text-zinc-400 border-white/10 hover:text-white"
                    }`}
                  >
                    {freeOnly ? "✓ Free-tier only" : "Show all providers"}
                  </button>
                  <span className="text-zinc-500 ml-auto">
                    {sorted.length} model{sorted.length !== 1 ? "s" : ""}
                    {cheapest && <> · cheapest: <strong className="text-white">{cheapest.name}</strong> @ <span className="text-amber-400 font-mono">${cheapest.blended.toFixed(6)}</span></>}
                    {!freeOnly && cheapestPaid && cheapestPaid !== cheapest && (
                      <> · cheapest paid: <strong className="text-white">{cheapestPaid.name}</strong> @ <span className="text-amber-400 font-mono">${cheapestPaid.blended.toFixed(6)}</span></>
                    )}
                  </span>
                </div>

                {/* ── Model table ── */}
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-1.5 text-zinc-500">Model</th>
                        <th className="text-left py-1.5 text-zinc-500">Provider</th>
                        <th className="text-right py-1.5 text-zinc-500">Input /1M</th>
                        <th className="text-right py-1.5 text-zinc-500">Output /1M</th>
                        <th className="text-right py-1.5 text-zinc-400 font-semibold">Cost/Credit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map((m) => (
                        <tr key={m.name} className="border-b border-white/5 hover:bg-white/5 cursor-pointer group"
                          onClick={() => {
                            const rounded = Math.round(m.blended * 1_000_000) / 1_000_000;
                            setCalcInputs(p => ({ ...p, ai_cost_per_credit: rounded }));
                            toast.success(`Cost/credit set to $${rounded.toFixed(6)} (${m.name} @ ${tpc.toLocaleString()} tok/credit)`);
                          }}>
                          <td className="py-1.5 text-zinc-300 group-hover:text-white flex items-center gap-1.5">
                            {m.name}
                            {m.isFree && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">FREE</span>}
                          </td>
                          <td className="py-1.5 text-zinc-500">{m.provider}</td>
                          <td className="text-right text-zinc-400">${m.input.toFixed(3)}</td>
                          <td className="text-right text-zinc-400">${m.output.toFixed(3)}</td>
                          <td className={`text-right font-mono ${m.isFree ? "text-emerald-400" : "text-amber-400"} group-hover:opacity-80`}>
                            ${m.blended.toFixed(6)}
                          </td>
                        </tr>
                      ))}
                      {sorted.length === 0 && (
                        <tr>
                          <td colSpan={5} className="text-center py-4 text-zinc-500 text-[11px]">
                            No models match current filters.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                <p className="text-[10px] text-zinc-600">
                  Click any row to apply that model's blended cost (at {tpc.toLocaleString()} tok/credit) to the Profit Margin Calculator above.
                  {" "}Rows marked <span className="text-emerald-400 font-bold">FREE</span> are providers the smart router uses at $0 (Groq, Cerebras, SambaNova, Google, HuggingFace, NVIDIA) via their free-tier quotas.
                </p>
              </div>
              );
            })()}
          </div>

            {/* ── Create New Plan Form ── */}
            {showNewPlan && (
              <div className="p-4 rounded-lg bg-indigo-500/10 border border-indigo-500/30 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-indigo-300 font-semibold text-sm">New Plan</h4>
                  <button onClick={() => { setShowNewPlan(false); setNewPlanId(""); setNewPlan({ ...BLANK_PLAN }); }}
                    className="text-zinc-500 hover:text-zinc-300"><X className="w-4 h-4" /></button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div className="space-y-1 col-span-2 md:col-span-1">
                    <Label className="text-zinc-400 text-xs">Plan ID <span className="text-zinc-600">(slug)</span></Label>
                    <Input value={newPlanId} onChange={(e) => setNewPlanId(e.target.value)}
                      placeholder="e.g. enterprise" className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Display Name</Label>
                    <Input value={newPlan.name} onChange={(e) => setNewPlan(p => ({ ...p, name: e.target.value }))}
                      placeholder="Enterprise" className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Price (USD) — central</Label>
                    <Input type="number" value={newPlan.price_usd}
                      onChange={(e) => setNewPlan(p => ({ ...p, price_usd: parseFloat(e.target.value) || 0 }))}
                      className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Price BDT <span className="text-zinc-600">(auto)</span></Label>
                    <div className="flex items-center h-9 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-zinc-400 font-mono">
                      ৳{usdToBdt(newPlan.price_usd || 0, bdt_exchange_rate).toLocaleString()}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Credits / month</Label>
                    <Input type="number" value={newPlan.credits}
                      onChange={(e) => setNewPlan(p => ({ ...p, credits: parseInt(e.target.value) || 0 }))}
                      className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3 text-orange-400" /> Monthly Cap <span className="text-zinc-600">(auto)</span>
                    </Label>
                    <div className="flex items-center h-9 px-3 rounded-md bg-zinc-800/80 border border-orange-500/20 text-sm text-orange-400 font-mono">
                      ${aiCostUsd(newPlan.credits || 0, effectiveCostPerCredit).toFixed(4)}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Max Agents</Label>
                    <Input type="number" value={newPlan.max_agents}
                      onChange={(e) => setNewPlan(p => ({ ...p, max_agents: parseInt(e.target.value) || 0 }))}
                      className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Custom Agents <span className="text-zinc-600">(-1 = ∞)</span></Label>
                    <Input type="number" value={newPlan.max_custom_agents}
                      onChange={(e) => setNewPlan(p => ({ ...p, max_custom_agents: parseInt(e.target.value) || 0 }))}
                      className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-zinc-400 text-xs">Team Size <span className="text-zinc-600">(-1 = ∞)</span></Label>
                    <Input type="number" value={newPlan.max_team_members}
                      onChange={(e) => setNewPlan(p => ({ ...p, max_team_members: parseInt(e.target.value) || 1 }))}
                      className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                  </div>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={newPlan.includes_commander}
                    onChange={(e) => setNewPlan(p => ({ ...p, includes_commander: e.target.checked }))}
                    className="w-3.5 h-3.5 rounded border-white/20 bg-zinc-800 accent-indigo-500" />
                  <span className="text-xs text-zinc-300">Includes Commander Orion</span>
                </label>
                <div className="flex gap-2 pt-1">
                  <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs" onClick={handleCreatePlan}>Add Plan</Button>
                  <Button size="sm" variant="ghost" className="text-zinc-400 text-xs"
                    onClick={() => { setShowNewPlan(false); setNewPlanId(""); setNewPlan({ ...BLANK_PLAN }); }}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* ── Existing Plans ── */}
            {Object.entries(pricingEdit.plans).map(([planId, plan]) => {
              const isFree = planId === "free";
              // Cost precedence: ledger.expected_costs.total (categorical
              // mix × per-track blended + infra) wins over flat blended
              // × credits. The flat figure is kept as a fallback for plans
              // the ledger hasn't seen yet (new plan, not yet published).
              const ledgerRow = (fullLedger?.plans || []).find(p => p.plan_id === planId);
              const allInCost  = ledgerRow?.expected_costs?.total;
              const flatCost   = aiCostUsd(plan.credits || 0, effectiveCostPerCredit);
              const costUsd    = (allInCost != null && allInCost > 0) ? allInCost : flatCost;
              const planProfit = profitUsd(plan.price_usd || 0, costUsd);
              // TRUE profit margin = profit / price (SaaS standard). The
              // previous calc used profit / cost (markup) and produced
              // five-figure percentages that weren't actionable.
              const planMargin = (plan.price_usd || 0) > 0
                ? Number((((plan.price_usd || 0) - costUsd) / (plan.price_usd || 1) * 100).toFixed(1))
                : 0;
              const isLoss       = planProfit < 0;
              const isLowMargin  = planMargin < 50 && !isLoss;
              const computedBdt  = usdToBdt(plan.price_usd || 0, effectiveBdtRate);
              const computedCap  = costUsd;

              const applyMarginToPlan = (markupPctValue) => {
                // markupPctValue is a markup % — price = cost × (1 + m/100).
                // No clamps; value stored verbatim.
                const raw = parseFloat(markupPctValue) || 0;
                const mult = priceMultiplierFromMarkup(raw);
                const usd  = Math.round(costUsd * mult * 100) / 100;
                updatePlanField(planId, "price_usd", usd);
                toast.success(`Applied ${raw.toLocaleString()}% markup to ${plan.name}`);
              };

              const isExpanded = expandedPlans.has(planId);
              // Suggested price = all-in cost × (1 + markup/100). Whatever
              // the operator typed — no clamps.
              const suggestedPriceUsd = isFree ? 0 : Math.round(costUsd * priceMultiplierFromMarkup(currentMarkupPct) * 100) / 100;
              return (
                <div key={planId} className="rounded-lg bg-white/5 border border-white/5 overflow-hidden">
                  {/* ── Summary row (always visible, click to expand) ──
                      Replaces the old Plan Preview table: shows every plan's
                      credits / AI Cost / Price / Suggested / Profit / Margin
                      in one line. Click anywhere to reveal the full editor. */}
                  <button
                    type="button"
                    onClick={() => togglePlanExpanded(planId)}
                    className="w-full px-4 py-3 flex items-center gap-3 hover:bg-white/[0.03] transition-colors text-left"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-zinc-400 shrink-0" /> : <ChevronDown className="w-4 h-4 text-zinc-400 shrink-0" />}
                    <div className="flex-1 grid grid-cols-2 md:grid-cols-7 gap-2 items-center text-sm">
                      <div className="flex items-center gap-2 col-span-2 md:col-span-1">
                        <span className="text-white font-semibold">{plan.name || planId}</span>
                        {plan.includes_commander && (
                          <Badge className="bg-violet-500/20 text-violet-400 text-[10px]">Commander</Badge>
                        )}
                      </div>
                      <div className="text-right md:text-left">
                        <span className="text-[10px] text-zinc-500 md:hidden">Credits: </span>
                        <span className="font-mono text-zinc-300">{(plan.credits || 0).toLocaleString()}</span>
                        <span className="text-[10px] text-zinc-600 hidden md:inline"> cr</span>
                      </div>
                      <div className="text-right md:text-left">
                        <span className="text-[10px] text-zinc-500 md:hidden">AI Cost: </span>
                        <span className="font-mono text-amber-400">${costUsd.toFixed(4)}</span>
                      </div>
                      <div className="text-right md:text-left">
                        <span className="text-[10px] text-zinc-500 md:hidden">Price: </span>
                        <span className="font-mono font-bold text-white">${(plan.price_usd || 0).toFixed(2)}</span>
                      </div>
                      <div className="text-right md:text-left">
                        <span className="text-[10px] text-zinc-500 md:hidden">Suggested: </span>
                        {isFree ? <span className="text-zinc-600">—</span> : (
                          <span
                            role="button"
                            tabIndex={0}
                            onClick={(e) => {
                              e.stopPropagation();
                              updatePlanField(planId, "price_usd", suggestedPriceUsd);
                              toast.success(`${plan.name} price set to $${suggestedPriceUsd}`);
                            }}
                            className="font-mono text-zinc-500 hover:text-teal-400 cursor-pointer underline decoration-dotted underline-offset-2"
                            title="Apply suggested price"
                          >
                            ${suggestedPriceUsd.toFixed(2)}
                          </span>
                        )}
                      </div>
                      <div className="text-right md:text-left">
                        <span className="text-[10px] text-zinc-500 md:hidden">Profit: </span>
                        {isFree ? <span className="text-zinc-600">—</span> : (
                          <span className={`font-mono font-bold ${isLoss ? "text-red-400" : "text-emerald-400"}`}>${planProfit.toFixed(2)}</span>
                        )}
                      </div>
                      <div className="text-right md:text-left">
                        {isFree ? <span className="text-zinc-600">—</span> : (
                          <Badge className={`text-[10px] ${isLoss ? "bg-red-500/20 text-red-400" : isLowMargin ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/20 text-emerald-400"}`}>
                            {isLoss ? "LOSS" : `${planMargin}% margin`}
                          </Badge>
                        )}
                      </div>
                    </div>
                    {!isFree && onDeletePlan && (
                      <span
                        role="button"
                        tabIndex={0}
                        aria-label={`Delete ${plan.name || planId}`}
                        onClick={(e) => { e.stopPropagation(); onDeletePlan(planId); }}
                        onKeyDown={(e) => { if (e.key === "Enter") { e.stopPropagation(); onDeletePlan(planId); } }}
                        className="h-7 w-7 shrink-0 flex items-center justify-center rounded text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </span>
                    )}
                  </button>

                  {/* ── Expanded editor body ── */}
                  {isExpanded && (<div className="px-4 pb-4 space-y-3 border-t border-white/5 pt-3">
                  <div className="text-[9px] text-zinc-600 font-mono">
                    {allInCost != null ? (
                      <>trace: all-in cost ${costUsd.toFixed(4)} from categorical ledger (mix × per-track blended + infra share)</>
                    ) : (
                      <>trace: {(plan.credits || 0).toLocaleString()} cr × ${effectiveCostPerCredit.toFixed(6)} {lockedSnapshot ? " (locked snapshot)" : " (live measurement)"} = ${costUsd.toFixed(4)} AI Cost (ledger not yet computed)</>
                    )}
                  </div>

                  {/* Quick markup buttons — price = cost × (1 + markup/100) */}
                  {!isFree && (
                    <div className="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5 flex-wrap">
                      <span className="text-xs text-zinc-400 shrink-0">Set markup:</span>
                      {[100, 200, 500, 1000, 2000, 5000].map(m => (
                        <Button key={m} size="sm" variant="outline"
                          className={`text-[10px] h-6 px-2 border-white/10 text-zinc-400 hover:bg-white/5`}
                          onClick={() => applyMarginToPlan(m)}>
                          {m >= 1000 ? `${m/1000}k%` : `${m}%`}
                        </Button>
                      ))}
                      <div className="flex items-center gap-1 ml-1">
                        <Input type="number" step="any" min="0" placeholder="Custom"
                          className="bg-zinc-800/50 border-white/10 h-6 w-20 text-[10px] px-1.5"
                          onKeyDown={(e) => { if (e.key === "Enter") applyMarginToPlan(parseFloat(e.target.value) || 0); }} />
                        <span className="text-[10px] text-zinc-500">%</span>
                      </div>
                    </div>
                  )}

                  {/* Fields */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-9 gap-3">
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Price USD ★</Label>
                      <Input type="number" step="0.01" value={plan.price_usd}
                        onChange={(e) => updatePlanField(planId, "price_usd", e.target.value)}
                        className="bg-zinc-800/50 border-indigo-500/30 border h-9 text-sm text-white" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Price BDT <span className="text-zinc-600">(auto)</span></Label>
                      <div className="flex items-center h-9 px-3 rounded-md bg-zinc-800/60 border border-white/5 text-sm text-zinc-400 font-mono">
                        ৳{computedBdt.toLocaleString()}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">
                        Credits/mo
                        <span className="text-teal-400 text-[10px] font-mono ml-1.5">auto-derived</span>
                      </Label>
                      <Input type="number" value={plan.credits}
                        onChange={(e) => updatePlanField(planId, "credits", e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Max Agents</Label>
                      <Input type="number" value={plan.max_agents}
                        onChange={(e) => updatePlanField(planId, "max_agents", e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Custom Agents</Label>
                      <Input type="number" value={plan.max_custom_agents}
                        onChange={(e) => updatePlanField(planId, "max_custom_agents", e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                      <p className="text-[9px] text-zinc-600">-1 = unlimited</p>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Team Size</Label>
                      <Input type="number" value={plan.max_team_members || 1}
                        onChange={(e) => updatePlanField(planId, "max_team_members", e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm" />
                      <p className="text-[9px] text-zinc-600">-1 = unlimited</p>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3 text-orange-400" /> Cap <span className="text-zinc-600">(budgeted)</span>
                      </Label>
                      <div className="flex items-center h-9 px-3 rounded-md bg-zinc-800/80 border border-orange-500/20 text-sm text-orange-400 font-mono">
                        ${computedCap.toFixed(4)}
                      </div>
                      {/* Real measured cost — compare budgeted (credits × ai_cost_per_credit
                          which is set in the Profit Margin Calculator) vs live measured
                          blended cost from /admin/avg-cost. When the measured figure is
                          LOWER than budgeted, we're routing more efficiently than planned;
                          when HIGHER, something drifted. Delta is shown inline in green/red. */}
                      {(() => {
                        const measured = liveCost?.avg_cost_per_credit;
                        if (measured == null || !plan.credits) return null;
                        const realCost = plan.credits * measured;
                        const delta = realCost - computedCap;
                        const deltaPct = computedCap > 0 ? (delta / computedCap) * 100 : 0;
                        const under = delta <= 0;
                        return (
                          <div className={`text-[9px] font-mono mt-0.5 leading-tight ${
                            under ? "text-emerald-400" : "text-rose-400"
                          }`}>
                            Real: ${realCost.toFixed(4)}
                            {" "}<span className="text-zinc-500">·</span>{" "}
                            {under ? "▼" : "▲"} {Math.abs(deltaPct).toFixed(0)}% {under ? "under" : "over"}
                          </div>
                        );
                      })()}
                      <p className="text-[9px] text-zinc-600">= credits × cost/credit</p>
                    </div>
                    {/* Operator share % — sits beside Cap because both are
                        operator-economics fields. Cap = AI cost we'll incur;
                        share = fraction of price retained as profit. */}
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs flex items-center gap-1">
                        <span className="w-3 h-3 inline-flex items-center justify-center text-emerald-400 text-[10px] font-bold">%</span>
                        Operator Share
                      </Label>
                      <div className="flex items-center h-9 px-2 rounded-md bg-zinc-800/80 border border-emerald-500/20 gap-2">
                        <input
                          type="range" min="0" max="100" step="1"
                          value={Math.round((parseFloat(plan.operator_share_pct ?? 0.30) || 0) * 100)}
                          onChange={(e) => updatePlanField(planId, "operator_share_pct", parseInt(e.target.value, 10) / 100)}
                          className="flex-1 accent-emerald-400"
                          style={{ minWidth: 40 }}
                        />
                        <span className="text-xs font-mono text-emerald-400 tabular-nums" style={{ width: 32, textAlign: "right" }}>
                          {Math.round((parseFloat(plan.operator_share_pct ?? 0.30) || 0) * 100)}%
                        </span>
                      </div>
                      <p className="text-[9px] text-zinc-600">
                        ${((parseFloat(plan.price_usd) || 0) * (parseFloat(plan.operator_share_pct ?? 0.30) || 0)).toFixed(2)} → profit pool
                      </p>
                    </div>
                    <div className="space-y-1 flex flex-col justify-end">
                      <label className="flex items-center gap-2 cursor-pointer h-9 px-2 rounded-md bg-zinc-800/30 border border-white/5">
                        <input type="checkbox" checked={plan.includes_commander || false}
                          onChange={(e) => updatePlanField(planId, "includes_commander", e.target.checked)}
                          className="w-3.5 h-3.5 rounded border-white/20 bg-zinc-800 accent-indigo-500" />
                        <span className="text-xs text-zinc-300">Commander</span>
                      </label>
                    </div>
                  </div>

                  {/* ── Media Capacity ─ tri-state: blank=auto / number=cap / -1=disabled.
                      Auto shows the derived ceiling from credits ÷ per-unit cost. */}
                  <div className="pt-3 mt-2 border-t border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Label className="text-zinc-400 text-xs font-semibold uppercase tracking-wide">Media Capacity</Label>
                      <span className="text-[10px] text-zinc-600">
                        blank = auto (derived from credits) · number = hard cap · -1 = disabled
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
                      {[
                        ["images_standard",   "Images Std",   engineConfig.image_std_credits,        "img"],
                        ["images_hd",         "Images HD",    engineConfig.image_hd_credits,         "img"],
                        ["videos_4sec",       "Video Clips (4s)", engineConfig.video_credits_per_sec * 4, "clips"],
                        ["video_seconds",     "Video Seconds", engineConfig.video_credits_per_sec,   "sec"],
                        ["tts_minutes",       "TTS Minutes",  engineConfig.tts_credits_per_min,      "min"],
                        ["voiceover_minutes", "Voice-Over Min", engineConfig.voiceover_credits_per_min, "min"],
                        ["stt_minutes",       "STT Minutes",  engineConfig.stt_credits_per_min,      "min"],
                      ].map(([field, label, perUnit, unit]) => {
                        const eff = effectiveMediaCap(plan, field, perUnit);
                        const raw = plan?.media?.[field];
                        const displayVal = raw === null || raw === undefined ? "" : raw;
                        const isDisabled = raw === -1;
                        const isAuto = raw === null || raw === undefined;
                        return (
                          <div key={field} className="space-y-1">
                            <Label className="text-zinc-400 text-[11px]">{label}</Label>
                            <Input
                              type="number"
                              placeholder={`${eff.value} auto`}
                              value={displayVal}
                              onChange={(e) => updatePlanMedia(planId, field, e.target.value)}
                              className={`bg-zinc-800/50 h-9 text-sm font-mono ${
                                isDisabled ? "border-rose-500/30 border text-rose-400" :
                                isAuto ? "border-white/10 text-zinc-400" :
                                "border-teal-500/30 border text-teal-400"
                              }`}
                            />
                            <p className="text-[9px] text-zinc-600 font-mono">
                              {isDisabled ? "DISABLED" : `${eff.value.toLocaleString()} ${unit}${isAuto ? " auto" : " cap"}`}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* ── Deliverables → Credits + Cost (auto) ───────────
                      Operator defines what the plan includes as concrete
                      counts (N chats, M videos, P HD images, etc.). From
                      those + engine_config's per-modality credit rates,
                      the plan's credits total and LLM cost auto-derive:

                        credits_per_category = count × rate
                        total_credits        = Σ category_credits
                        llm_cost_usd         = Σ category_credits × category_blended

                      plan.credits + plan.price_usd still drive the row
                      above; this panel is the source of truth for the
                      deliverable shape and the cost it produces. Change a
                      number → cost + margin update in real time. */}
                  <div className="pt-3 mt-2 border-t border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Label className="text-zinc-400 text-xs font-semibold uppercase tracking-wide">
                        Deliverables → Credits + Cost
                      </Label>
                      <span className="text-[10px] text-zinc-600">
                        Set counts · cost auto-computes from the 5 category rates
                      </span>
                    </div>
                    {(() => {
                      const ec = { ...DEFAULT_ENGINE_CONFIG, ...engineConfig };
                      // Credits-per-deliverable — chat + code now come
                      // from operator-set rates alongside the media ones.
                      // No more implicit token-math derivation.
                      const _n = (v, d) => { const p = parseFloat(v); return Number.isFinite(p) ? p : d; };
                      const CR_PER = {
                        chats:         _n(ec.chat_credits_per_msg,       0.015),
                        code_runs:     _n(ec.code_credits_per_run,       0.04),
                        hd_images:     _n(ec.image_hd_credits,           0),
                        std_images:    _n(ec.image_std_credits,          0),
                        videos_4s:     4 * _n(ec.video_credits_per_sec,  0),
                        voiceover_min: _n(ec.voiceover_credits_per_min,  0),
                        tts_min:       _n(ec.tts_credits_per_min,        0),
                        stt_min:       _n(ec.stt_credits_per_min,        0),
                      };
                      // Each deliverable maps to its OWN dedicated track —
                      // no merging. std vs HD images go to different rates;
                      // voiceover / tts / stt each have their own.
                      const CAT_OF = {
                        chats: "chat", code_runs: "code",
                        hd_images: "image_hd", std_images: "image_std",
                        videos_4s: "video",
                        voiceover_min: "voiceover", tts_min: "tts", stt_min: "stt",
                      };
                      // When operator hasn't typed explicit counts, IMPLY
                      // them from plan.credits using the same per-bucket
                      // ratios the backend ledger uses (services/billing/
                      // plan_buckets.py DEFAULT_RATIOS + per-tier overrides
                      // mirrored client-side). That way the Derived /
                      // LLM-cost / Margin line at the bottom always
                      // matches the trace at the top — no two-surface drift.
                      // Operator-typed values take precedence (a 0 from
                      // them stays 0; only missing keys get implied).
                      const PLAN_BUCKET_RATIOS = {
                        free:        { chat: 0.80, code: 0.05, image: 0.03, video: 0.00, voice: 0.01, stt: 0.01, agent_sop: 0.10 },
                        starter:     { chat: 0.60, code: 0.10, image: 0.08, video: 0.02, voice: 0.03, stt: 0.02, agent_sop: 0.15 },
                        creator:     { chat: 0.45, code: 0.15, image: 0.15, video: 0.10, voice: 0.04, stt: 0.01, agent_sop: 0.10 },
                        studio:      { chat: 0.30, code: 0.18, image: 0.17, video: 0.14, voice: 0.05, stt: 0.01, agent_sop: 0.15 },
                        scale:       { chat: 0.20, code: 0.22, image: 0.17, video: 0.16, voice: 0.04, stt: 0.01, agent_sop: 0.20 },
                        infinity:    { chat: 0.15, code: 0.25, image: 0.15, video: 0.20, voice: 0.04, stt: 0.01, agent_sop: 0.20 },
                        _default:    { chat: 0.50, code: 0.10, image: 0.10, video: 0.05, voice: 0.05, stt: 0.05, agent_sop: 0.15 },
                      };
                      const ratios = PLAN_BUCKET_RATIOS[planId] || PLAN_BUCKET_RATIOS._default;
                      const totalCreditsForSplit = parseFloat(plan.credits) || 0;
                      // Implied per-bucket credits (chat/code/image/video/voice/stt/agent_sop)
                      const impliedBucketCredits = {
                        chat:      totalCreditsForSplit * (ratios.chat || 0),
                        code:      totalCreditsForSplit * (ratios.code || 0),
                        image:     totalCreditsForSplit * (ratios.image || 0),
                        video:     totalCreditsForSplit * (ratios.video || 0),
                        voice:     totalCreditsForSplit * (ratios.voice || 0),
                        stt:       totalCreditsForSplit * (ratios.stt || 0),
                      };
                      // Convert bucket credits into deliverable counts at
                      // the current per-action rates. image bucket splits
                      // 70/30 std:hd, voice splits 60/30/10 vo/tts/stt to
                      // mirror the backend mapping in plan_economics_full.
                      const cnt = (cr, perUnit) => (perUnit > 0 ? Math.floor(cr / perUnit) : 0);
                      const impliedCounts = {
                        chats:        cnt(impliedBucketCredits.chat,            CR_PER.chats         || 0.015),
                        code_runs:    cnt(impliedBucketCredits.code,            CR_PER.code_runs     || 0.04),
                        std_images:   cnt(impliedBucketCredits.image * 0.70,    CR_PER.std_images    || 0),
                        hd_images:    cnt(impliedBucketCredits.image * 0.30,    CR_PER.hd_images     || 0),
                        videos_4s:    cnt(impliedBucketCredits.video,           CR_PER.videos_4s     || 0),
                        voiceover_min:cnt(impliedBucketCredits.voice * 0.60,    CR_PER.voiceover_min || 0),
                        tts_min:      cnt(impliedBucketCredits.voice * 0.30,    CR_PER.tts_min       || 0),
                        stt_min:      cnt(impliedBucketCredits.voice * 0.10 + impliedBucketCredits.stt, CR_PER.stt_min || 0),
                      };
                      const explicit = plan.deliverables_counts || {};
                      const hasExplicit = Object.keys(explicit).length > 0;
                      // counts = operator-typed values; impliedCounts only
                      // surfaces in the input placeholder + the derived
                      // Credits / Cost line. Once operator types ANY value
                      // we honour their explicit set verbatim (including 0).
                      const counts = explicit;
                      const updateCount = (k, raw) => {
                        const v = Math.max(0, parseInt(raw, 10) || 0);
                        const next = { ...counts, [k]: v };
                        updatePlanField(planId, "deliverables_counts", next);
                        // Auto-sync plan.credits to the derived total so
                        // the row above + downstream code stay in sync.
                        let total = 0;
                        for (const [key, cnt] of Object.entries(next)) {
                          total += (cnt || 0) * (CR_PER[key] || 0);
                        }
                        updatePlanField(planId, "credits", Math.round(total));
                      };
                      const DELIVERABLES = [
                        { key: "chats",         label: "Chats",         unit: "msgs",  dot: "bg-emerald-400", tint: "text-emerald-400", hint: "1.5k tok each" },
                        { key: "code_runs",     label: "Code runs",     unit: "runs",  dot: "bg-violet-400",  tint: "text-violet-400",  hint: "4k tok each · app builds / vibe / workflow" },
                        { key: "hd_images",     label: "HD images",     unit: "imgs",  dot: "bg-rose-400",    tint: "text-rose-400",    hint: "Flux HD paid" },
                        { key: "std_images",    label: "Std images",    unit: "imgs",  dot: "bg-rose-400",    tint: "text-rose-400/70", hint: "Pollinations free" },
                        { key: "videos_4s",     label: "Videos (4s)",   unit: "clips", dot: "bg-amber-400",   tint: "text-amber-400",   hint: "Fal LTX · 4-sec" },
                        { key: "voiceover_min", label: "Voiceover min", unit: "min",   dot: "bg-sky-400",     tint: "text-sky-400",     hint: "ElevenLabs paid" },
                        { key: "tts_min",       label: "TTS min",       unit: "min",   dot: "bg-sky-400",     tint: "text-sky-400/70",  hint: "Edge TTS free" },
                        { key: "stt_min",       label: "STT min",       unit: "min",   dot: "bg-sky-400",     tint: "text-sky-400/70",  hint: "Groq Whisper free" },
                      ];
                      // Effective count = operator-typed value when set,
                      // else implied (so display matches the backend
                      // ledger by default and totals never read 0 just
                      // because nobody filled the form).
                      const effectiveCount = (key) =>
                        (counts[key] !== undefined && counts[key] !== null && counts[key] !== "")
                          ? (parseInt(counts[key], 10) || 0)
                          : (impliedCounts[key] || 0);
                      let totalCr   = 0;
                      let totalCost = 0;
                      const rows = DELIVERABLES.map(({ key }) => {
                        const count    = effectiveCount(key);
                        const isImplied = !(key in counts);
                        const cr    = count * (CR_PER[key] || 0);
                        const cat   = CAT_OF[key];
                        const rate  = blendedByCategory?.[cat]?.value || 0;
                        const cost  = cr * rate;
                        totalCr   += cr;
                        totalCost += cost;
                        return { key, count, cr, cost, isImplied };
                      });
                      const price   = parseFloat(plan.price_usd) || 0;
                      const margin  = price > 0 ? ((price - totalCost) / price) * 100 : null;

                      return (
                        <>
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                            {DELIVERABLES.map(({ key, label, unit, dot, tint, hint }) => {
                              const r = rows.find(x => x.key === key);
                              const perUnit = CR_PER[key];
                              const isExplicit = key in counts;
                              const explicitVal = isExplicit ? counts[key] : "";
                              return (
                                <div key={key} className="space-y-1">
                                  <Label className="text-zinc-400 text-[11px] flex items-center gap-1.5">
                                    <span className={`inline-block w-1.5 h-1.5 rounded-full ${dot}`} />
                                    {label}
                                    <span className="text-[9px] text-zinc-600 ml-auto">{perUnit === 0 ? "free" : `${perUnit.toFixed(perUnit < 1 ? 3 : 0)} cr/${unit.slice(0, -1) || unit}`}</span>
                                  </Label>
                                  <Input
                                    type="number"
                                    min="0"
                                    placeholder={String(impliedCounts[key] || 0)}
                                    value={explicitVal === "" ? "" : explicitVal}
                                    onChange={(e) => updateCount(key, e.target.value)}
                                    className={`bg-zinc-800/50 h-9 text-sm font-mono ${isExplicit ? "border-white/10 text-white" : "border-white/5 text-zinc-500"}`}
                                  />
                                  <p className="text-[9px] text-zinc-500 font-mono leading-tight">
                                    {r.cr.toFixed(2)} cr · <span className={tint}>${r.cost.toFixed(4)}</span>
                                    {!isExplicit && <span className="text-zinc-600 ml-1">(implied)</span>}
                                  </p>
                                  <p className="text-[8.5px] text-zinc-600 leading-tight">{hint}</p>
                                </div>
                              );
                            })}
                          </div>
                          {/* Live totals — plan.credits auto-syncs from totalCr.
                              Cost cap (monthly_cap_usd) is the enforcement
                              bar — no tokens-hard-cap shown here. */}
                          <div className="mt-3 p-2.5 rounded-lg bg-teal-500/5 border border-teal-500/20 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px]">
                            <span className="text-zinc-500">Derived credits:</span>
                            <span className="font-mono text-teal-400 font-semibold">{Math.round(totalCr).toLocaleString()} cr</span>
                            <span className="text-zinc-600">·</span>
                            <span className="text-zinc-500">LLM cost:</span>
                            <span className="font-mono text-amber-400 font-semibold">${totalCost.toFixed(4)}</span>
                            <span className="text-zinc-600">·</span>
                            <span className="text-zinc-500">Margin @ ${price.toFixed(2)}:</span>
                            <span className={`font-mono font-semibold ${
                              margin === null ? 'text-zinc-500' :
                              margin >= 90 ? 'text-emerald-400' :
                              margin >= 50 ? 'text-amber-400' : 'text-rose-400'
                            }`}>
                              {margin === null ? '—' : margin.toFixed(1) + '%'}
                            </span>
                            <span className="text-[9px] text-zinc-600 ml-auto">
                              {hasExplicit
                                ? "Summed at each deliverable's DEDICATED rate · LLM-only · matches header trace"
                                : "Implied from plan credits × per-bucket ratios · type a value to override · matches header trace"}
                            </span>
                          </div>
                        </>
                      );
                    })()}
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    <Label className="text-zinc-400 text-xs">Features (shown on pricing page)</Label>
                    <div className="flex flex-wrap gap-1.5">
                      {(plan.features || []).map((f, i) => (
                        <Badge key={i} className="bg-indigo-500/15 text-indigo-400 border-0 text-[10px] gap-1">
                          {f}
                          <button onClick={() => removeFeatureFromPlan(planId, i)} className="hover:text-red-400">
                            <X className="w-2.5 h-2.5" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add feature…"
                        className="bg-zinc-800/50 border-white/10 h-7 text-xs flex-1"
                        value={newFeatureInputs[planId] || ""}
                        onChange={(e) => setNewFeatureInputs(p => ({ ...p, [planId]: e.target.value }))}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && newFeatureInputs[planId]?.trim()) {
                            addFeatureToPlan(planId, newFeatureInputs[planId]);
                            setNewFeatureInputs(p => ({ ...p, [planId]: "" }));
                          }
                        }}
                      />
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-zinc-400 hover:text-indigo-400"
                        onClick={() => {
                          if (newFeatureInputs[planId]?.trim()) {
                            addFeatureToPlan(planId, newFeatureInputs[planId]);
                            setNewFeatureInputs(p => ({ ...p, [planId]: "" }));
                          }
                        }}>
                        <Plus className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>

                  {/* Cost breakdown bar */}
                  {!isFree && (
                    <>
                      <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isLoss ? "bg-red-500" : "bg-gradient-to-r from-red-500 via-amber-500 to-emerald-500"}`}
                          style={{ width: `${Math.min(100, plan.price_usd > 0 ? (costUsd / plan.price_usd * 100) : 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-zinc-500">
                        <span>AI Cost: <span className="text-red-400">${costUsd.toFixed(4)}</span></span>
                        <span>Revenue: <span className="text-emerald-400">${plan.price_usd}</span></span>
                        <span>Profit: <span className={isLoss ? "text-red-400" : "text-amber-400"}>${planProfit.toFixed(2)}</span></span>
                      </div>
                    </>
                  )}
                  </div>)}
                </div>
              );
            })}

            {/* Custom agent cost */}
            <div className="p-4 rounded-lg bg-white/5 border border-white/5 space-y-3">
              <h4 className="text-white font-semibold text-sm">Custom Agent Creation Cost</h4>
              <div className="w-48">
                <Input
                  type="number"
                  value={pricingEdit.custom_agent_credit_cost}
                  onChange={(e) => setPricingEdit(p => ({ ...p, custom_agent_credit_cost: parseInt(e.target.value) || 0 }))}
                  className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                />
                <p className="text-[10px] text-zinc-500 mt-1">Credits charged per custom agent created</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button onClick={handlePublishPricing}
                className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600">
                Publish Pricing Changes
              </Button>
              <Button variant="outline" className="border-white/10"
                onClick={() => setPricingEdit(JSON.parse(JSON.stringify(pricingConfig)))}>
                Reset to Current
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Operator-Only Breakdown ── */}
      {pricingEdit && (
        <Card className="bg-zinc-900/50 border-amber-500/20">
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2 flex-wrap">
                <span className="text-amber-400">🔒</span> Operator Breakdown
                <Badge className="bg-amber-500/20 text-amber-400 text-[10px]">ADMIN ONLY</Badge>
                <Badge className="bg-teal-500/20 text-teal-400 text-[10px]">reads from Active Pricing ↑</Badge>
              </CardTitle>
              <span className="text-[10px] text-zinc-500">Not visible to clients</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">

            {/* Credit-to-token ratio */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <p className="text-[10px] text-zinc-500 mb-1">Credit ↔ Token Ratio</p>
                <p className="text-lg font-bold text-white font-mono">1 credit = {(engineConfig.tokens_per_credit || DEFAULT_ENGINE_CONFIG.tokens_per_credit).toLocaleString()} tokens</p>
                <p className="text-[10px] text-zinc-600 mt-1">
                  Hard cap per client. ~66 short chats or 1 video per credit.
                </p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <p className="text-[10px] text-zinc-500 mb-1">Cost per Token (blended)</p>
                <p className="text-lg font-bold text-emerald-400 font-mono">${(effectiveCostPerCredit / (engineConfig.tokens_per_credit || DEFAULT_ENGINE_CONFIG.tokens_per_credit)).toExponential(2)}</p>
                <p className="text-[10px] text-zinc-600 mt-1">
                  ${effectiveCostPerCredit.toFixed(6)}/credit {lockedSnapshot ? "(locked)" : "(live)"} ÷ {(engineConfig.tokens_per_credit || DEFAULT_ENGINE_CONFIG.tokens_per_credit).toLocaleString()} tok/credit
                </p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <p className="text-[10px] text-zinc-500 mb-1">Free-Tier Routing</p>
                <p className="text-lg font-bold text-emerald-400 font-mono">{liveCost.free_routing_pct?.toFixed(0) || 50}%</p>
                <p className="text-[10px] text-zinc-600 mt-1">{liveCost.providers_free || 6} free / {liveCost.providers_paid || 16} paid providers</p>
              </div>
            </div>

            {/* Smart router workflow */}
            <div className="p-4 rounded-xl bg-teal-500/5 border border-teal-500/15">
              <p className="text-[11px] font-semibold text-teal-400 mb-2 uppercase tracking-wide">Smart Router Workflow</p>
              <ol className="space-y-1.5 text-[11px] text-zinc-400 leading-relaxed">
                <li><span className="text-teal-400 font-mono">1.</span> Request arrives → classified by task type (chat, code, reasoning, research)</li>
                <li><span className="text-teal-400 font-mono">2.</span> Router checks free-tier first: Groq → Cerebras → SambaNova → Gemini → NVIDIA → HuggingFace</li>
                <li><span className="text-teal-400 font-mono">3.</span> If free unavailable → cheapest paid: DeepSeek → Together → Fireworks → Mistral</li>
                <li><span className="text-teal-400 font-mono">4.</span> Premium fallback (Opus/GPT-4/Sonnet) only if specifically requested</li>
                <li><span className="text-teal-400 font-mono">5.</span> 1 request = 1 credit deducted from client's strict cap</li>
              </ol>
            </div>

            {/* Per-plan usage capacity — driven by engine_config, not hardcoded. */}
            <div>
              <p className="text-[11px] font-semibold text-zinc-300 mb-2 uppercase tracking-wide">Client Usage Capacity per Plan</p>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-zinc-500 border-b border-white/5">
                      <th className="text-left py-2 font-normal">Plan</th>
                      <th className="text-right py-2 font-normal">Credits</th>
                      <th className="text-right py-2 font-normal">AI Messages*</th>
                      <th className="text-right py-2 font-normal">Cold Emails</th>
                      <th className="text-right py-2 font-normal">Social Posts</th>
                      <th className="text-right py-2 font-normal">Images</th>
                      <th className="text-right py-2 font-normal">Video (sec)</th>
                      <th className="text-right py-2 font-normal">VO (min)</th>
                      <th className="text-right py-2 font-normal" title="LLM inference only — credits × blended">LLM Cost</th>
                      <th className="text-right py-2 font-normal" title="Total: LLM + media + email + voice + infra (from full-ledger)">All-In Cost†</th>
                      <th className="text-right py-2 font-normal">Price</th>
                      <th className="text-right py-2 font-normal">Margin %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(pricingEdit.plans || {}).map(([pid, plan]) => {
                      // All derived from engine_config — same formulas the buyer-facing
                      // capacity + backend plan_economics use.
                      //
                      // credits_per_action of 0 means the modality is FREE
                      // via router (Pollinations/Edge/Groq/etc.) — display
                      // "∞" instead of NaN when dividing by zero.
                      const credits = plan.credits || 0;
                      const price   = plan.price_usd || 0;
                      const ec = { ...DEFAULT_ENGINE_CONFIG, ...engineConfig };
                      const tpc = ec.tokens_per_credit || DEFAULT_ENGINE_CONFIG.tokens_per_credit;
                      const MESSAGE_TOKENS = 1500;         // realistic chat: 1k in + 500 out
                      const messages    = Math.floor(credits * tpc / MESSAGE_TOKENS);
                      const coldEmails  = Math.floor(credits / 3);       // ~3 cr/email (draft+send)
                      const socialPosts = Math.floor(credits / 2);       // ~2 cr/post
                      // Handle free modalities: divisor 0 → unlimited (∞)
                      const images    = (ec.image_std_credits || 0) === 0 ? "∞" : Math.floor(credits / ec.image_std_credits);
                      const videoSec  = (ec.video_credits_per_sec || 0) === 0 ? "∞" : Math.floor(credits / ec.video_credits_per_sec);
                      const voMin     = (ec.voiceover_credits_per_min || 0) === 0 ? "∞" : Math.floor(credits / ec.voiceover_credits_per_min);
                      const llmCost     = aiCostUsd(credits, effectiveCostPerCredit);
                      // All-In cost pulled live from /api/admin/pricing/full-ledger (see fetchFullLedger below).
                      const ledgerRow   = (fullLedger?.plans || []).find(p => p.plan_id === pid);
                      const allInCost   = ledgerRow?.expected_costs?.total ?? null;
                      const trueMargin  = (allInCost !== null && price > 0)
                                          ? ((price - allInCost) / price) * 100 : null;
                      const fmt = (n) => n >= 1e9 ? (n/1e9).toFixed(1)+'B'
                                         : n >= 1e6 ? (n/1e6).toFixed(1)+'M'
                                         : n >= 1e3 ? (n/1e3).toFixed(1)+'k'
                                         : n.toLocaleString();
                      return (
                        <tr key={pid} className="border-b border-white/5 hover:bg-white/[0.02]">
                          <td className="py-2 text-white">{plan.name || pid}</td>
                          <td className="py-2 text-right text-white font-mono">{credits.toLocaleString()}</td>
                          <td className="py-2 text-right text-teal-300 font-mono">{fmt(messages)}</td>
                          <td className="py-2 text-right text-zinc-300 font-mono">{fmt(coldEmails)}</td>
                          <td className="py-2 text-right text-zinc-300 font-mono">{fmt(socialPosts)}</td>
                          <td className="py-2 text-right text-zinc-300 font-mono">{fmt(images)}</td>
                          <td className="py-2 text-right text-zinc-300 font-mono">{fmt(videoSec)}</td>
                          <td className="py-2 text-right text-zinc-300 font-mono">{fmt(voMin)}</td>
                          <td className="py-2 text-right text-emerald-400 font-mono" title="LLM inference only">${llmCost.toFixed(4)}</td>
                          <td className="py-2 text-right text-amber-300 font-mono" title="LLM + media + email + voice + infra (full ledger)">
                            {allInCost === null ? '…' : `$${allInCost.toFixed(2)}`}
                          </td>
                          <td className="py-2 text-right text-white font-mono">${price.toFixed(2)}</td>
                          <td className="py-2 text-right font-mono" style={{
                            color: trueMargin === null ? '#64748b'
                                 : trueMargin >= 90 ? '#34d399'
                                 : trueMargin >= 50 ? '#fbbf24'
                                 : '#f87171',
                          }}>{trueMargin === null ? '—' : trueMargin.toFixed(1) + '%'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="text-[9px] text-zinc-600 mt-2 leading-relaxed">
                * AI Messages = credits × tokens_per_credit ÷ 1,500 (realistic chat: 1k in + 500 out). Cold Emails ≈ 3 cr each, Social Posts ≈ 2 cr. Image / Video / VO use Active Pricing rates above.<br />
                <span className="text-emerald-400">LLM Cost</span> = provider inference only.&nbsp;
                <span className="text-amber-300">All-In Cost†</span> = LLM + media + email + voice + infra (from <a href="/api/admin/pricing/full-ledger" className="text-teal-400 underline">/api/admin/pricing/full-ledger</a>). Margin % reflects All-In.
              </p>
            </div>

            {/* Cost Optimization Levers */}
            <div className="mt-6 p-4 rounded-lg border border-amber-500/20 bg-amber-500/5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-[11px] font-semibold text-amber-300 uppercase tracking-wide">
                  Cost Optimization Levers
                </p>
                {costConfig?.savings && (
                  <span className="text-[11px] text-amber-200">
                    Untapped: <strong>${(costConfig.savings.untapped_monthly_savings_usd || 0).toFixed(2)}/mo</strong>
                    <span className="text-zinc-500"> at {costConfig.savings.active_heavy_clients || 10} heavy clients</span>
                  </span>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {costConfig?.config?.levers && Object.entries(costConfig.config.levers).map(([key, state]) => {
                  const labels = {
                    local_media:          { name: "Local media GPU",        hint: "SDXL / Whisper / XTTS / SVD self-host — set MAARS_LOCAL_IMAGE_URL" },
                    self_smtp:            { name: "Self-hosted SMTP",       hint: "Postfix + warmed IPs — set MAARS_SMTP_HOST" },
                    telnyx_voice:         { name: "Telnyx (vs Twilio)",     hint: "~45% cheaper/min — set TELNYX_API_KEY" },
                    native_lead_research: { name: "Native lead research",   hint: "BrowserAgent scraping (built-in) replaces Apollo/Hunter" },
                    proxy_pool:           { name: "Residential proxy pool", hint: "Scales scraping safely — set MAARS_PROXY_POOL" },
                  };
                  const info = labels[key] || { name: key };
                  return (
                    <div key={key} className="flex items-center justify-between p-2 bg-black/30 rounded border border-white/5">
                      <div className="flex-1 min-w-0 pr-3">
                        <div className="flex items-center gap-2">
                          <span className="text-[12px] text-white">{info.name}</span>
                          {state.active && <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/20 text-emerald-300 rounded">ACTIVE</span>}
                          {!state.active && state.active_claim && !state.env_detected && (
                            <span className="text-[9px] px-1.5 py-0.5 bg-red-500/20 text-red-300 rounded">NEEDS ENV</span>
                          )}
                          {!state.active && !state.active_claim && (
                            <span className="text-[9px] px-1.5 py-0.5 bg-zinc-500/20 text-zinc-400 rounded">OFF</span>
                          )}
                        </div>
                        <div className="text-[10px] text-zinc-500 mt-0.5">{info.hint}</div>
                        <div className="text-[10px] text-amber-300/80 mt-0.5">
                          Saves ~${state.savings_per_heavy_client_usd.toFixed(2)}/mo per heavy client
                        </div>
                      </div>
                      <button
                        onClick={async () => {
                          try {
                            await fetch(`${API}/admin/cost-config`, {
                              method: "PUT",
                              headers: {
                                "Content-Type": "application/json",
                                Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
                              },
                              body: JSON.stringify({ key, active: !state.active_claim }),
                            });
                            fetchCostConfig();
                            fetchFullLedger();
                          } catch (_) { /* surface via reloaded state */ }
                        }}
                        className={`text-[11px] px-3 py-1.5 rounded border transition ${
                          state.active_claim
                            ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
                            : "bg-zinc-700/50 border-zinc-600 text-zinc-300 hover:bg-zinc-600/50"
                        }`}
                      >
                        {state.active_claim ? "ON" : "OFF"}
                      </button>
                    </div>
                  );
                })}
              </div>
              <p className="text-[9px] text-zinc-600 mt-3 leading-relaxed">
                <span className="text-emerald-300">ACTIVE</span> = operator toggle on + env detected.&nbsp;
                <span className="text-red-300">NEEDS ENV</span> = toggle on, prerequisite missing — no effect until infra wired.&nbsp;
                All-In Cost column recalculates when a lever becomes ACTIVE.
              </p>
            </div>

          </CardContent>
        </Card>
      )}
    </div>
  );
};
