import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { TrendingUp, CheckCircle, Trash2, Plus, X, ChevronDown, ChevronUp, ShieldAlert, Info, Sparkles } from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

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
  { name: "DeepSeek R1 0528",   provider: "SambaNova",   input: 1.30,  output: 1.30  },
  { name: "AI21 Jamba Mini",    provider: "AI21",        input: 0.20,  output: 0.40  },
];
const TOKENS_PER_CREDIT = 1000;

// Build preset plans — BDT and monthly_cap_usd are stamped on load/publish
// Agent count: 41 core named agents + 417 MAARS Infinity = 458 total
// Credits: capped ~10,000 — enough for a full month of active use
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

// Stamp BDT and cap onto every plan given rate and cost/credit
const stampDerived = (plans, rate, costPerCredit) =>
  Object.fromEntries(
    Object.entries(plans).map(([id, plan]) => [
      id,
      {
        ...plan,
        price_bdt: Math.round((plan.price_usd || 0) * rate),
        monthly_cap_usd: Math.round((plan.credits || 0) * costPerCredit * 10000) / 10000,
      },
    ])
  );

const BLANK_PLAN = {
  name: "",
  price_usd: 0,
  credits: 0,
  max_agents: 5,
  max_custom_agents: 0,
  max_team_members: 1,
  includes_commander: false,
  features: [],
};

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
  const [showNewPlan, setShowNewPlan] = useState(false);
  const [newPlanId, setNewPlanId] = useState("");
  const [newPlan, setNewPlan] = useState({ ...BLANK_PLAN });
  const [newFeatureInputs, setNewFeatureInputs] = useState({});

  const { ai_cost_per_credit, target_profit_margin, bdt_exchange_rate } = calcInputs;
  const marginMultiplier = 1 + ((target_profit_margin || 0) / 100);

  // Live calculations — derived from actual plans in pricingEdit
  const activePlans = pricingEdit?.plans || {};
  const liveCalcs = {};
  for (const [pid, plan] of Object.entries(activePlans)) {
    const credits = plan.credits || 0;
    const base = Math.round(credits * (ai_cost_per_credit || 0) * 10000) / 10000;
    const rec = pid === "free" ? 0 : Math.round(base * marginMultiplier * 100) / 100;
    const recBdt = Math.round((plan.price_usd || 0) * (bdt_exchange_rate || 0));
    const profit = Math.round((( plan.price_usd || 0) - base) * 100) / 100;
    const marginPct = base > 0 ? Math.round((((plan.price_usd || 0) - base) / base) * 100) : 0;
    liveCalcs[pid] = { credits, name: plan.name || pid, base, rec, recBdt, profit, marginPct, priceUsd: plan.price_usd || 0 };
  }

  // Auto-sync BDT on all plans whenever exchange rate changes
  useEffect(() => {
    if (!pricingEdit || !bdt_exchange_rate) return;
    setPricingEdit(prev => ({
      ...prev,
      plans: Object.fromEntries(
        Object.entries(prev.plans).map(([id, plan]) => [
          id,
          { ...plan, price_bdt: Math.round((plan.price_usd || 0) * bdt_exchange_rate) },
        ])
      ),
    }));
  }, [bdt_exchange_rate]);

  const handlePublishPricing = async () => {
    if (!pricingEdit) return;
    // Stamp computed BDT and cap onto every plan before saving
    const stamped = {
      ...pricingEdit,
      plans: stampDerived(pricingEdit.plans, bdt_exchange_rate || 107, ai_cost_per_credit || 0),
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
        updates.price_bdt = Math.round((parseFloat(value) || 0) * (bdt_exchange_rate || 107));
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
    setPricingEdit(prev => ({
      ...prev,
      plans: Object.fromEntries(
        Object.entries(prev.plans).map(([id, plan]) => {
          if (id === "free") return [id, plan];
          const cost = (plan.credits || 0) * (ai_cost_per_credit || 0.003);
          const usd = Math.round(cost * marginMultiplier * 100) / 100;
          return [id, { ...plan, price_usd: usd, price_bdt: Math.round(usd * (bdt_exchange_rate || 107)) }];
        })
      ),
    }));
    toast.success(`Applied ${target_profit_margin}% margin to all plans`);
  };

  const handleCreatePlan = async () => {
    const id = newPlanId.trim().toLowerCase().replace(/\s+/g, "_");
    if (!id) { toast.error("Plan ID required"); return; }
    if (!newPlan.name.trim()) { toast.error("Plan name required"); return; }
    if (pricingEdit?.plans[id]) { toast.error(`Plan ID "${id}" already exists`); return; }

    const planWithDerived = {
      ...newPlan,
      price_bdt: Math.round((newPlan.price_usd || 0) * (bdt_exchange_rate || 107)),
      monthly_cap_usd: Math.round((newPlan.credits || 0) * (ai_cost_per_credit || 0) * 10000) / 10000,
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

  return (
    <div className="space-y-6">

      {/* ── Profit Margin Calculator ── */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-amber-400" />
            </div>
            Profit Margin Calculator
            <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px] ml-2">LIVE SYNC</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">

          {/* Live AI cost stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 rounded-xl bg-white/5 border border-white/5">
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Total AI Cost <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </p>
              <p className="text-xl font-bold text-red-400 font-mono">${liveCost.total_cost_usd?.toFixed(4) || "0.00"}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Cost / Credit <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </p>
              <p className="text-xl font-bold text-amber-400 font-mono">${liveCost.avg_cost_per_credit?.toFixed(6) || "0.003"}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5">Total API Calls</p>
              <p className="text-xl font-bold text-white font-mono">{liveCost.total_calls?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5">Data Source</p>
              <p className="text-sm font-medium mt-1">
                {liveCost.source === "real_usage"
                  ? <span className="text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Real Usage</span>
                  : <span className="text-zinc-500">Default Estimate</span>}
              </p>
              <p className="text-[10px] text-zinc-600 mt-0.5">Refreshes every 15s</p>
            </div>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">AI Cost per Credit (USD)</Label>
              <div className="flex items-center h-10 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-amber-400 font-mono font-bold">
                ${(ai_cost_per_credit || 0).toFixed(6)}
              </div>
              <p className="text-[10px] text-emerald-500/70 flex items-center gap-1">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live from {liveCost.total_calls} API calls
              </p>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Target Profit Margin (%)</Label>
              <Input
                type="number"
                value={target_profit_margin}
                onChange={(e) => setCalcInputs(p => ({ ...p, target_profit_margin: parseInt(e.target.value) || 0 }))}
                className="bg-zinc-800/50 border-white/10"
              />
              <p className="text-[10px] text-zinc-500">{target_profit_margin}% = {marginMultiplier.toFixed(1)}× your cost</p>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">BDT Exchange Rate <span className="text-zinc-500 font-normal">(syncs all prices)</span></Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={bdt_exchange_rate}
                  onChange={(e) => syncAllBdtPricing(parseFloat(e.target.value) || 0)}
                  className="bg-zinc-800/50 border-white/10 flex-1"
                />
                <Button variant="outline" size="sm"
                  className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs whitespace-nowrap"
                  onClick={async () => {
                    try {
                      const res = await fetch(`${API}/exchange-rate`);
                      if (res.ok) { const d = await res.json(); syncAllBdtPricing(d.usd_bdt); toast.success(`Rate: 1 USD = ${d.usd_bdt} BDT`); }
                    } catch { toast.error("Failed to fetch rate"); }
                  }}>
                  Refresh Live
                </Button>
              </div>
              <p className="text-[10px] text-emerald-500/70">1 USD = {bdt_exchange_rate} BDT — all plan BDT prices auto-update</p>
            </div>
          </div>

          <Button onClick={applyMarginToPlans}
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600">
            Apply {target_profit_margin}% Margin to All Plans
          </Button>

          {/* Live plan preview table */}
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-zinc-400">Plan</th>
                  <th className="text-right py-2 text-zinc-400">Credits</th>
                  <th className="text-right py-2 text-zinc-400">AI Cost</th>
                  <th className="text-right py-2 text-zinc-400">Price USD</th>
                  <th className="text-right py-2 text-zinc-400">Price BDT</th>
                  <th className="text-right py-2 text-zinc-400">Profit/User</th>
                  <th className="text-right py-2 text-zinc-400">Margin</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                {Object.entries(liveCalcs).map(([id, calc]) => (
                  <tr key={id} className="border-b border-white/5">
                    <td className="py-2 font-medium">{calc.name}</td>
                    <td className="text-right">{calc.credits.toLocaleString()}</td>
                    <td className="text-right text-red-400">${calc.base.toFixed(4)}</td>
                    <td className="text-right text-emerald-400">${calc.priceUsd.toFixed(2)}</td>
                    <td className="text-right text-zinc-400">৳{calc.recBdt.toLocaleString()}</td>
                    <td className="text-right text-amber-400">${calc.profit.toFixed(2)}</td>
                    <td className="text-right">
                      <Badge className={`text-[10px] ${calc.marginPct >= 200 ? "bg-emerald-500/20 text-emerald-400" : calc.marginPct > 0 ? "bg-amber-500/20 text-amber-400" : "bg-zinc-700/40 text-zinc-500"}`}>
                        {id === "free" ? "—" : `${calc.marginPct}%`}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

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
            {showModelRef && (
              <div className="px-4 pb-4 space-y-3">
                <p className="text-[11px] text-zinc-500">
                  Assuming <strong className="text-zinc-300">{TOKENS_PER_CREDIT.toLocaleString()} tokens = 1 credit</strong> (50% input / 50% output blend).
                </p>
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
                      {MODEL_COSTS.map((m) => {
                        const blended = ((m.input + m.output) / 2) * (TOKENS_PER_CREDIT / 1_000_000);
                        return (
                          <tr key={m.name} className="border-b border-white/5 hover:bg-white/5 cursor-pointer group"
                            onClick={() => {
                              const rounded = Math.round(blended * 1_000_000) / 1_000_000;
                              setCalcInputs(p => ({ ...p, ai_cost_per_credit: rounded }));
                              toast.success(`Cost/credit set to $${rounded.toFixed(6)} (${m.name})`);
                            }}>
                            <td className="py-1.5 text-zinc-300 group-hover:text-white">{m.name}</td>
                            <td className="py-1.5 text-zinc-500">{m.provider}</td>
                            <td className="text-right text-zinc-400">${m.input.toFixed(3)}</td>
                            <td className="text-right text-zinc-400">${m.output.toFixed(3)}</td>
                            <td className="text-right font-mono text-amber-400 group-hover:text-amber-300">${blended.toFixed(6)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p className="text-[10px] text-zinc-600">Click any row to apply that model's blended cost.</p>
              </div>
            )}
          </div>

        </CardContent>
      </Card>

      {/* ── Plan Editor ── */}
      {pricingEdit && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-white font-['Outfit'] text-base">Plans & Packages</CardTitle>
              <div className="flex gap-2">
                <Button
                  size="sm" variant="outline"
                  className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10 gap-1.5 text-xs"
                  onClick={handleLoadPresets}>
                  <Sparkles className="w-3.5 h-3.5" />
                  Load Preset Tiers ($50 → $8K)
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
                      ৳{Math.round((newPlan.price_usd || 0) * (bdt_exchange_rate || 107)).toLocaleString()}
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
                      ${((newPlan.credits || 0) * (ai_cost_per_credit || 0)).toFixed(4)}
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
              const costUsd = (plan.credits || 0) * (ai_cost_per_credit || 0.003);
              const profitUsd = (plan.price_usd || 0) - costUsd;
              const marginPct = costUsd > 0 ? ((profitUsd / costUsd) * 100).toFixed(0) : 0;
              const isLoss = profitUsd < 0;
              const isLowMargin = marginPct < 100 && !isLoss;
              const computedBdt = Math.round((plan.price_usd || 0) * (bdt_exchange_rate || 107));
              const computedCap = Math.round(costUsd * 10000) / 10000;

              const applyMarginToPlan = (margin) => {
                const mult = 1 + (margin / 100);
                const usd = Math.round(costUsd * mult * 100) / 100;
                updatePlanField(planId, "price_usd", usd);
                toast.success(`Applied ${margin}% margin to ${plan.name}`);
              };

              return (
                <div key={planId} className="p-4 rounded-lg bg-white/5 border border-white/5 space-y-3">
                  {/* Header */}
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <h4 className="text-white font-semibold">{plan.name || planId}</h4>
                      {plan.includes_commander && (
                        <Badge className="bg-violet-500/20 text-violet-400 text-[10px]">Commander</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500">AI Cost: <span className="text-red-400 font-mono">${costUsd.toFixed(4)}</span></span>
                      <span className="text-xs text-zinc-500">Profit: <span className={`font-mono ${isLoss ? "text-red-400" : "text-emerald-400"}`}>${profitUsd.toFixed(2)}</span></span>
                      <Badge className={`text-[10px] ${isLoss ? "bg-red-500/20 text-red-400" : isLowMargin ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/20 text-emerald-400"}`}>
                        {isLoss ? "LOSS" : `${marginPct}% margin`}
                      </Badge>
                      {!isFree && onDeletePlan && (
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400"
                          onClick={() => onDeletePlan(planId)}>
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Quick margin buttons */}
                  {!isFree && (
                    <div className="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5 flex-wrap">
                      <span className="text-xs text-zinc-400 shrink-0">Set margin:</span>
                      {[100, 200, 500, 1000, 2000].map(m => (
                        <Button key={m} size="sm" variant="outline"
                          className={`text-[10px] h-6 px-2 border-white/10 ${parseInt(marginPct) === m ? "bg-amber-500/20 text-amber-400 border-amber-500/30" : "text-zinc-400 hover:bg-white/5"}`}
                          onClick={() => applyMarginToPlan(m)}>
                          {m}%
                        </Button>
                      ))}
                      <div className="flex items-center gap-1 ml-1">
                        <Input type="number" placeholder="Custom"
                          className="bg-zinc-800/50 border-white/10 h-6 w-16 text-[10px] px-1.5"
                          onKeyDown={(e) => { if (e.key === "Enter") applyMarginToPlan(parseInt(e.target.value) || 0); }} />
                        <span className="text-[10px] text-zinc-500">%</span>
                      </div>
                    </div>
                  )}

                  {/* Fields */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 gap-3">
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
                      <Label className="text-zinc-400 text-xs">Credits/mo</Label>
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
                        <ShieldAlert className="w-3 h-3 text-orange-400" /> Cap <span className="text-zinc-600">(auto)</span>
                      </Label>
                      <div className="flex items-center h-9 px-3 rounded-md bg-zinc-800/80 border border-orange-500/20 text-sm text-orange-400 font-mono">
                        ${computedCap.toFixed(4)}
                      </div>
                      <p className="text-[9px] text-zinc-600">= credits × cost/credit</p>
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
                        <span>Profit: <span className={isLoss ? "text-red-400" : "text-amber-400"}>${profitUsd.toFixed(2)}</span></span>
                      </div>
                    </>
                  )}
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
    </div>
  );
};
