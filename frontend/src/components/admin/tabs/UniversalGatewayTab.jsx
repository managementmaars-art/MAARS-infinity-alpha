import { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import {
  Globe, TrendingUp, AlertTriangle, CheckCircle2, XCircle,
  RefreshCw, Coins, Clock, Activity, BarChart3, Network, Key,
  Shield, Loader2, Copy, RotateCcw, Users, DollarSign,
  Pencil, Check, X, Search, ChevronDown, ChevronUp,
  Play, Zap, Webhook, GitCompare, Send, Settings2, SlidersHorizontal,
  MessageSquare, PlusCircle, Trash2, TestTube2, ExternalLink, Code2,
  Wallet, CreditCard, ArrowUpRight, Percent, Sparkles, Package,
  GraduationCap, Workflow, Brain, Crown
} from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";
import { useAuth } from "../../../App";
import ProviderIntelligencePage from "../../../pages/ProviderIntelligencePage";
import { UniversalGatewayTraining } from "./UniversalGatewayTraining";
import { UniversalGatewayWorkflows } from "./UniversalGatewayWorkflows";
import { UniversalGatewayRAG } from "./UniversalGatewayRAG";
import { UniversalGatewayCommander } from "./UniversalGatewayCommander";

const PROVIDER_COLORS = {
  openai:     "text-emerald-400",
  anthropic:  "text-orange-400",
  gemini:     "text-blue-400",
  xai:        "text-sky-400",
  deepseek:   "text-teal-400",
  mistral:    "text-violet-400",
  perplexity: "text-cyan-400",
  cohere:     "text-amber-400",
  groq:       "text-yellow-400",
  cerebras:   "text-pink-400",
  together:   "text-lime-400",
  fireworks:  "text-red-400",
  ai21:       "text-indigo-300",
  sambanova:  "text-purple-400",
  novita:     "text-violet-400",
  lepton:     "text-orange-400",
  lambda:     "text-cyan-400",
  minimax:    "text-sky-400",
  inception:  "text-fuchsia-500",
  arcee:      "text-rose-400",
  amazon:     "text-orange-500",
  nvidia:     "text-green-400",
  moonshot:   "text-blue-300",
  qwen:       "text-orange-300",
  elevenlabs: "text-fuchsia-400",
};

const TASK_COLORS = {
  code:        "bg-emerald-500/20 text-emerald-300",
  math:        "bg-blue-500/20 text-blue-300",
  reasoning:   "bg-violet-500/20 text-violet-300",
  legal:       "bg-amber-500/20 text-amber-300",
  creative:    "bg-pink-500/20 text-pink-300",
  translation: "bg-cyan-500/20 text-cyan-300",
  summary:     "bg-teal-500/20 text-teal-300",
  research:    "bg-indigo-500/20 text-indigo-300",
  data:        "bg-orange-500/20 text-orange-300",
  vision:      "bg-sky-500/20 text-sky-300",
  chat:        "bg-zinc-500/20 text-zinc-300",
  general:     "bg-zinc-500/20 text-zinc-300",
};

const TIER_COLORS = {
  economy:  "bg-emerald-500/20 text-emerald-300",
  standard: "bg-blue-500/20 text-blue-300",
  premium:  "bg-violet-500/20 text-violet-300",
};

const BUDGET_COLORS = {
  micro:    "bg-red-500/20 text-red-300",
  tight:    "bg-amber-500/20 text-amber-300",
  normal:   "bg-blue-500/20 text-blue-300",
  generous: "bg-emerald-500/20 text-emerald-300",
};

const StatBox = ({ label, value, sub, icon: Icon, color = "indigo" }) => {
  const bg = {
    indigo: "bg-indigo-500/20 text-indigo-400",
    emerald:"bg-emerald-500/20 text-emerald-400",
    amber:  "bg-amber-500/20 text-amber-400",
    violet: "bg-violet-500/20 text-violet-400",
    rose:   "bg-rose-500/20 text-rose-400",
    cyan:   "bg-cyan-500/20 text-cyan-400",
  }[color] || "bg-indigo-500/20 text-indigo-400";

  return (
    <Card className="bg-zinc-900/50 border-white/10">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-zinc-500 mb-1">{label}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
            {sub && <p className="text-xs text-zinc-500 mt-1">{sub}</p>}
          </div>
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${bg}`}>
            <Icon className="w-4 h-4" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const BarRow = ({ label, value, total, color = "indigo" }) => {
  const pct = total ? Math.round((value / total) * 100) : 0;
  const barColor = {
    indigo: "bg-indigo-500", emerald: "bg-emerald-500", amber: "bg-amber-500",
    violet: "bg-violet-500", rose: "bg-rose-500", cyan: "bg-cyan-500",
    blue: "bg-blue-500", teal: "bg-teal-500",
  }[color] || "bg-indigo-500";

  return (
    <div className="flex items-center gap-3">
      <span className="w-32 text-sm text-zinc-300 capitalize truncate">{label}</span>
      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-zinc-400 w-16 text-right">{value} ({pct}%)</span>
    </div>
  );
};

export const UniversalGatewayTab = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [health, setHealth] = useState(null);
  const [clientKeys, setClientKeys] = useState(null);
  const [badges, setBadges] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedLog, setExpandedLog] = useState(null);
  // Honor ?tab=<section> on mount so deep-links (and the redirect from the
  // retired /admin/provider-intelligence page) land on the right sub-tab.
  const _initialTab = (() => {
    try {
      const p = new URLSearchParams(window.location.search).get("tab");
      const valid = ["overview","cost_health","onboarding","offices","teams","treasury","cost_automation","financials","playground","compare","clients","webhooks","sdk","providers","intelligence","advisor","breakdown","logs"];
      return valid.includes(p) ? p : "overview";
    } catch { return "overview"; }
  })();
  const [activeSection, setActiveSection] = useState(_initialTab);
  const [keySearch, setKeySearch] = useState("");
  const [revealedKeys, setRevealedKeys] = useState({});
  const [editingBudget, setEditingBudget] = useState({});
  const [provisioning, setProvisioning] = useState(false);

  // PAYG billing state
  const [billingModal, setBillingModal] = useState(null); // { userId, name, billing_mode, markup_pct, balance_usd }
  const [topupModal, setTopupModal] = useState(null);     // { userId, name, balance_usd }
  const [topupAmount, setTopupAmount] = useState("10.00");
  const [billingForm, setBillingForm] = useState({ billing_mode: "subscription", markup_pct: "0" });
  const [savingBilling, setSavingBilling] = useState(false);
  const [toppingUp, setToppingUp] = useState(false);

  // Playground state
  const [playModel, setPlayModel] = useState("maars/auto");
  const [playSystem, setPlaySystem] = useState("");
  const [playMessage, setPlayMessage] = useState("Explain quantum entanglement in one paragraph.");
  const [playTemp, setPlayTemp] = useState(0.7);
  const [playMaxTokens, setPlayMaxTokens] = useState(1024);
  const [playResponse, setPlayResponse] = useState(null);
  const [playLoading, setPlayLoading] = useState(false);
  const [playMeta, setPlayMeta] = useState(null);

  // Compare state
  const [compareModels, setCompareModels] = useState(["openai/gpt-4o", "anthropic/claude-sonnet-4-6"]);
  const [comparePrompt, setComparePrompt] = useState("Write a haiku about artificial intelligence.");
  const [compareResults, setCompareResults] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Webhooks state
  const [webhooks, setWebhooks] = useState([]);
  const [whLoading, setWhLoading] = useState(false);
  const [whUrl, setWhUrl] = useState("");
  const [whEvents, setWhEvents] = useState(["budget.90", "budget.100"]);
  const [whDesc, setWhDesc] = useState("");
  const [addingWh, setAddingWh] = useState(false);
  const [myMaarsKey, setMyMaarsKey] = useState("");

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const { user: admin } = useAuth();

  // Operator P&L state — merged in from the former /admin/metrics page.
  const [pnlDays, setPnlDays] = useState(7);
  const [pnlRevenue, setPnlRevenue] = useState(null);
  const [pnlProfit, setPnlProfit] = useState(null);
  const [pnlSpend, setPnlSpend] = useState(null);
  const [pnlRouting, setPnlRouting] = useState(null);
  // Per-track blended rates (chat/code/image_std/image_hd/video/voiceover/tts/stt).
  // Shared source-of-truth with PricingManager, Package Advisor, and the router.
  const [blendedByCategory, setBlendedByCategory] = useState(null);

  // Balance data — merged into Provider Health tab so each provider renders
  // exactly once with balance + tier + health + actions.
  const [balanceData, setBalanceData] = useState(null);
  const [balanceRefreshing, setBalanceRefreshing] = useState(false);
  const [configSlug, setConfigSlug] = useState(null);
  const [configBalance, setConfigBalance] = useState("");
  const [configThreshold, setConfigThreshold] = useState("");

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    try {
      const [statsRes, logsRes, healthRes, keysRes,
             revRes, profRes, spendRes, routRes, balRes, bbcRes] = await Promise.all([
        fetch(`${API}/admin/gateway/stats`, { headers }),
        fetch(`${API}/admin/gateway/logs?limit=50`, { headers }),
        fetch(`${API}/admin/gateway/health`, { headers }),
        fetch(`${API}/admin/gateway/client-keys`, { headers }),
        // Operator P&L — same gateway data, aggregated for the financial view.
        fetch(`${API}/admin/metrics/revenue?days=${pnlDays}`, { headers }),
        fetch(`${API}/admin/metrics/profitability?days=${pnlDays}`, { headers }),
        fetch(`${API}/admin/metrics/provider-spend?days=${pnlDays}`, { headers }),
        fetch(`${API}/admin/metrics/routing?days=${pnlDays}`, { headers }),
        fetch(`${API}/admin/metrics/provider-balances`, { headers }),
        // Per-track blended rates — shared with Pricing Manager + Advisor
        // so routing / attribution / pricing all read the same numbers.
        fetch(`${API}/admin/pricing/blended-by-category`, { headers }),
      ]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (logsRes.ok) { const d = await logsRes.json(); setLogs(d.logs || []); }
      if (healthRes.ok) setHealth(await healthRes.json());
      if (keysRes.ok) setClientKeys(await keysRes.json());
      if (revRes.ok)   setPnlRevenue(await revRes.json());
      if (profRes.ok)  setPnlProfit(await profRes.json());
      if (spendRes.ok) setPnlSpend(await spendRes.json());
      if (routRes.ok)  setPnlRouting(await routRes.json());
      if (balRes.ok)   setBalanceData(await balRes.json());
      if (bbcRes.ok)   setBlendedByCategory(await bbcRes.json());
    } catch { toast.error("Failed to load gateway data"); }
    finally { setLoading(false); setRefreshing(false); }
  }, [token, pnlDays]);

  const refreshBalances = async () => {
    setBalanceRefreshing(true);
    try {
      const r = await fetch(`${API}/admin/metrics/provider-balances/refresh`,
                            { method: "POST", headers });
      if (r.ok) {
        toast.success("Balances refreshed");
        const fresh = await fetch(`${API}/admin/metrics/provider-balances`, { headers });
        if (fresh.ok) setBalanceData(await fresh.json());
      }
    } catch { toast.error("Refresh failed"); }
    finally { setBalanceRefreshing(false); }
  };

  const saveProviderConfig = async () => {
    if (!configSlug) return;
    try {
      const body = { slug: configSlug };
      if (configBalance) body.starting_balance_usd = parseFloat(configBalance);
      if (configThreshold) body.alert_threshold_usd = parseFloat(configThreshold);
      const r = await fetch(`${API}/admin/metrics/provider-balances/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        toast.success(`Config saved for ${configSlug}`);
        setConfigSlug(null);
        setConfigBalance("");
        setConfigThreshold("");
        const fresh = await fetch(`${API}/admin/metrics/provider-balances`, { headers });
        if (fresh.ok) setBalanceData(await fresh.json());
      }
    } catch { toast.error("Failed to save config"); }
  };

  useEffect(() => { load(); }, [load]);

  // Refresh per-tab badge counts every 30s so Training / Workflows /
  // Commander tabs show red-dot counts when action is needed.
  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const tk = token || localStorage.getItem("token") || "";
        const r = await fetch(`${API}/admin/gateway/badges`, {
          headers: { Authorization: `Bearer ${tk}` },
        });
        if (!cancelled && r.ok) {
          const d = await r.json();
          setBadges(d.badges || {});
        }
      } catch {}
    };
    tick();
    const id = setInterval(tick, 30000);
    return () => { cancelled = true; clearInterval(id); };
  }, [token]);

  // Auto-sync: silently refetch every 60s while the tab is mounted so Provider
  // Health reflects the backend's auto-sync (smoke every 10min, balances every
  // 5min) + any operator-side actions (top-ups, EULA-accepts) within a minute.
  // Pause while the browser tab is hidden to avoid burning network on idle tabs.
  useEffect(() => {
    const tick = () => { if (!document.hidden) load(true); };
    const id = setInterval(tick, 60_000);
    const visHandler = () => { if (!document.hidden) load(true); };
    document.addEventListener("visibilitychange", visHandler);
    return () => { clearInterval(id); document.removeEventListener("visibilitychange", visHandler); };
  }, [load]);

  useEffect(() => {
    // Auto-detect admin's own MAARS key from clientKeys
    if (clientKeys?.clients?.length) {
      const myKey = clientKeys.clients[0]?.key || "";
      setMyMaarsKey(myKey);
    }
  }, [clientKeys]);

  const handleRegenerateKey = async (userId, userName) => {
    if (!window.confirm(`Regenerate MAARS key for ${userName}? The old key stops working immediately.`)) return;
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/${userId}/regenerate`, {
        method: "POST", headers,
      });
      if (res.ok) {
        toast.success(`Key regenerated for ${userName}`);
        load(true);
      } else toast.error("Failed to regenerate key");
    } catch { toast.error("Failed to regenerate key"); }
  };

  const handleUpdateBudget = async (userId, newBudget) => {
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/${userId}`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ monthly_budget_usd: parseFloat(newBudget) }),
      });
      if (res.ok) {
        toast.success("Budget updated");
        setEditingBudget(prev => { const n = {...prev}; delete n[userId]; return n; });
        load(true);
      } else toast.error("Failed to update budget");
    } catch { toast.error("Failed to update budget"); }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    const newStatus = currentStatus === "active" ? "suspended" : "active";
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/${userId}`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) { toast.success(`Key ${newStatus}`); load(true); }
      else toast.error("Failed to update status");
    } catch { toast.error("Failed to update status"); }
  };

  const handleProvisionAll = async () => {
    setProvisioning(true);
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/provision-all`, {
        method: "POST", headers,
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(`Provisioned ${d.provisioned} new keys (${d.total_users} total users)`);
        load(true);
      } else toast.error("Provision failed");
    } catch { toast.error("Provision failed"); }
    finally { setProvisioning(false); }
  };

  // ── PAYG billing handlers ──────────────────────────────────────────────────
  const openBillingModal = (c) => {
    setBillingForm({
      billing_mode: c.billing_mode || "subscription",
      markup_pct:   String(c.markup_pct ?? 0),
    });
    setBillingModal({ userId: c.user_id, name: c.name, balance_usd: c.balance_usd || 0 });
  };

  const handleSaveBilling = async () => {
    if (!billingModal) return;
    setSavingBilling(true);
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/${billingModal.userId}/billing`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          billing_mode: billingForm.billing_mode,
          markup_pct:   parseFloat(billingForm.markup_pct) || 0,
        }),
      });
      if (res.ok) {
        toast.success(`Billing updated for ${billingModal.name}`);
        setBillingModal(null);
        load(true);
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to update billing");
      }
    } catch { toast.error("Failed to update billing"); }
    finally { setSavingBilling(false); }
  };

  const handleTopup = async () => {
    if (!topupModal) return;
    const amount = parseFloat(topupAmount);
    if (isNaN(amount) || amount <= 0) { toast.error("Enter a valid amount"); return; }
    setToppingUp(true);
    try {
      const res = await fetch(`${API}/admin/gateway/client-keys/${topupModal.userId}/topup`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ amount_usd: amount, note: "Admin top-up" }),
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(`Added $${amount.toFixed(2)} → new balance $${d.new_balance?.toFixed(4)}`);
        setTopupModal(null);
        setTopupAmount("10.00");
        load(true);
      } else {
        const err = await res.json();
        toast.error(err.detail || "Top-up failed");
      }
    } catch { toast.error("Top-up failed"); }
    finally { setToppingUp(false); }
  };

  // ── Playground handler ─────────────────────────────────────────────────────
  const handlePlayground = async () => {
    setPlayLoading(true);
    setPlayResponse(null);
    setPlayMeta(null);
    try {
      const messages = [];
      if (playSystem.trim()) messages.push({ role: "system", content: playSystem.trim() });
      messages.push({ role: "user", content: playMessage });

      const start = Date.now();
      const res = await fetch(`${API}/admin/gateway/playground`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ model: playModel, messages, temperature: playTemp, max_tokens: playMaxTokens }),
      });
      const latency = Date.now() - start;
      if (!res.ok) { toast.error("Playground request failed"); return; }
      const data = await res.json();
      const content = data.choices?.[0]?.message?.content || "";
      const usage   = data.usage || {};
      setPlayResponse(content);
      setPlayMeta({
        provider:      data.x_playground?.actual_provider || "—",
        native_model:  data.x_playground?.native_model || "—",
        latency_ms:    data.x_playground?.latency_ms || latency,
        prompt_tokens: usage.prompt_tokens || 0,
        completion_tokens: usage.completion_tokens || 0,
        model_warning: data.x_playground?.model_warning || null,
      });
    } catch (e) { toast.error("Playground error: " + e.message); }
    finally { setPlayLoading(false); }
  };

  // ── Compare handler ─────────────────────────────────────────────────────────
  const handleCompare = async () => {
    if (compareModels.filter(Boolean).length < 2) { toast.error("Select at least 2 models"); return; }
    setCompareLoading(true);
    setCompareResults(null);
    try {
      const keyRes = await fetch(`${API}/admin/gateway/client-keys`, { headers });
      const keyData = await keyRes.json();
      const adminKey = keyData?.clients?.find(c => c.email === admin?.email)?.key || keyData?.clients?.[0]?.key || "";

      if (!adminKey) {
        toast.error("No MAARS API key found. Provision keys first.");
        return;
      }

      const cmpRes = await fetch(`${API}/v1/models/compare`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${adminKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          models: compareModels.filter(Boolean),
          messages: [{ role: "user", content: comparePrompt }],
          temperature: 0.7,
          max_tokens: 1024,
        }),
      });
      if (!cmpRes.ok) { toast.error("Compare failed"); return; }
      const cmpData = await cmpRes.json();
      setCompareResults(cmpData.results || []);
    } catch (e) { toast.error("Compare error: " + e.message); }
    finally { setCompareLoading(false); }
  };

  // ── Webhooks handlers ───────────────────────────────────────────────────────
  const loadWebhooks = async () => {
    if (!myMaarsKey) return;
    setWhLoading(true);
    try {
      const res = await fetch(`${API}/v1/webhooks`, {
        headers: { "Authorization": `Bearer ${myMaarsKey}` }
      });
      if (res.ok) { const d = await res.json(); setWebhooks(d.data || []); }
    } catch { } finally { setWhLoading(false); }
  };

  const handleAddWebhook = async () => {
    if (!whUrl || !myMaarsKey) { toast.error("MAARS key + URL required"); return; }
    setAddingWh(true);
    try {
      const res = await fetch(`${API}/v1/webhooks`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${myMaarsKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ url: whUrl, events: whEvents, description: whDesc }),
      });
      if (res.ok) {
        const d = await res.json();
        toast.success(`Webhook created. Secret: ${d.secret}`);
        setWhUrl(""); setWhDesc("");
        loadWebhooks();
      } else {
        const err = await res.json();
        toast.error(err?.error?.message || "Failed to create webhook");
      }
    } catch { toast.error("Failed"); }
    finally { setAddingWh(false); }
  };

  const handleDeleteWebhook = async (whId) => {
    if (!myMaarsKey) return;
    try {
      const res = await fetch(`${API}/v1/webhooks/${whId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${myMaarsKey}` },
      });
      if (res.ok) { toast.success("Webhook deleted"); loadWebhooks(); }
    } catch { toast.error("Failed to delete"); }
  };

  const handleTestWebhook = async (whId) => {
    if (!myMaarsKey) return;
    try {
      const res = await fetch(`${API}/v1/webhooks/${whId}/test`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${myMaarsKey}` },
      });
      const d = await res.json();
      if (d.success) toast.success("Test ping sent successfully!");
      else toast.error("Webhook test failed (check your endpoint)");
    } catch { toast.error("Test failed"); }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
    </div>
  );

  const totalCalls = stats?.total_calls || 0;

  const sections = [
    { id: "overview",    label: "Overview",        icon: Activity },
    { id: "cost_health", label: "Cost Health",     icon: DollarSign },
    { id: "onboarding",  label: "Provider Onboarding", icon: Key },
    { id: "offices",     label: "Agent Offices",   icon: Users },
    { id: "teams",       label: "Agent Teams",     icon: Users },
    { id: "treasury",    label: "Treasury",        icon: DollarSign },
    { id: "cost_automation", label: "Cost Automation", icon: DollarSign },
    { id: "financials",  label: "Financials",      icon: DollarSign },
    { id: "playground",  label: "Playground",       icon: Play },
    { id: "compare",     label: "Compare Models",   icon: GitCompare },
    { id: "clients",     label: "Client Keys",      icon: Key },
    { id: "webhooks",    label: "Webhooks",         icon: Webhook },
    { id: "sdk",         label: "API Reference",    icon: Shield },
    { id: "providers",   label: "Provider Health",  icon: Network },
    { id: "training",    label: "Agent Training",   icon: GraduationCap },
    { id: "workflows",   label: "Workflows",        icon: Workflow },
    { id: "rag",         label: "RAG",              icon: Brain },
    { id: "commander",   label: "Commander Intel",  icon: Crown },
    { id: "intelligence",label: "Intelligence",      icon: Sparkles },
    { id: "advisor",     label: "Package Advisor",  icon: Package },
    { id: "breakdown",   label: "Usage Breakdown",  icon: BarChart3 },
    { id: "logs",        label: "Routing Log",      icon: Shield },
  ];

  const filteredClients = (clientKeys?.clients || []).filter(c =>
    !keySearch ||
    c.name?.toLowerCase().includes(keySearch.toLowerCase()) ||
    c.email?.toLowerCase().includes(keySearch.toLowerCase()) ||
    c.plan_id?.toLowerCase().includes(keySearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500/30 to-violet-500/30 flex items-center justify-center">
              <Globe className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white font-['Outfit']">MAARS Universal AI Gateway</h2>
              <p className="text-xs text-zinc-500">33 providers · 175,000+ models · live validation · owner-only view</p>
            </div>
          </div>
        </div>
        <Button
          onClick={() => load(true)}
          disabled={refreshing}
          variant="outline"
          size="sm"
          className="border-white/10 text-zinc-400 hover:text-white"
        >
          {refreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          <span className="ml-2">Refresh</span>
        </Button>
      </div>

      {/* Gateway status banner */}
      {health && (
        <div className={`flex items-center gap-3 p-3 rounded-lg border ${
          health.gateway_ready
            ? "bg-emerald-500/10 border-emerald-500/30"
            : "bg-red-500/10 border-red-500/30"
        }`}>
          {health.gateway_ready
            ? <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            : <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />}
          <div>
            <p className="text-sm font-medium text-white">
              {health.gateway_ready ? "Gateway Operational" : "Gateway Degraded"}
            </p>
            <p className="text-xs text-zinc-400">
              {health.configured_count} / {health.total_providers} providers active ·{" "}
              {health.has_emergent_key ? "MAARS universal key configured" : "No universal key — direct keys only"}
            </p>
          </div>
          <div className="ml-auto flex gap-2 flex-wrap justify-end">
            {health.providers?.filter(p => p.is_active).slice(0, 6).map(p => (
              <Badge key={p.id} className="bg-emerald-500/20 text-emerald-300 text-[10px]">{p.name}</Badge>
            ))}
            {health.configured_count > 6 && (
              <Badge className="bg-zinc-500/20 text-zinc-400 text-[10px]">+{health.configured_count - 6} more</Badge>
            )}
          </div>
        </div>
      )}

      {/* Sub-nav — wraps to a second row on narrow viewports so no tab
          (Package Advisor, Usage Breakdown, Routing Log) ever gets clipped. */}
      <div className="flex gap-1 flex-wrap bg-zinc-900/50 p-1 rounded-lg border border-white/10">
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => {
              setActiveSection(s.id);
              // Keep URL ?tab= in sync so the tab is deep-linkable / bookmarkable.
              try {
                const u = new URL(window.location.href);
                u.searchParams.set("tab", s.id);
                window.history.replaceState({}, "", u.toString());
              } catch {}
            }}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all whitespace-nowrap ${
              activeSection === s.id
                ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
                : "text-zinc-400 hover:text-white hover:bg-white/5"
            }`}
          >
            <s.icon className="w-4 h-4" />
            {s.label}
            {(badges[s.id] || 0) > 0 && (
              <span className="ml-1 inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold rounded-full bg-rose-500 text-white">
                {badges[s.id] > 99 ? "99+" : badges[s.id]}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW ── */}
      {activeSection === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <StatBox label="Total Calls" value={totalCalls.toLocaleString()} icon={Activity} color="indigo" />
            <StatBox label="Total Cost (USD)" value={`$${stats?.total_cost_usd?.toFixed(4) || "0.0000"}`} sub="Admin view only" icon={TrendingUp} color="amber" />
            <StatBox label="Credits Burned" value={(stats?.total_credits_used || 0).toLocaleString()} icon={Coins} color="violet" />
            <StatBox label="Avg Cost/Call" value={`$${(stats?.avg_cost_per_call_usd || 0).toFixed(6)}`} icon={BarChart3} color="cyan" />
            <StatBox label="Fallback Rate" value={`${stats?.fallback_rate_pct || 0}%`} sub={`${stats?.fallback_count || 0} fallbacks`} icon={RefreshCw} color="rose" />
            <StatBox label="Avg Latency" value={`${stats?.avg_latency_ms || 0}ms`} icon={Clock} color="emerald" />
          </div>

          {/* Top providers mini-bars */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-400" /> Top Providers by Call Volume
              </h3>
              <div className="space-y-3">
                {Object.entries(stats?.calls_by_provider || {})
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 8)
                  .map(([prov, count]) => (
                    <BarRow key={prov} label={prov} value={count} total={totalCalls} color="indigo" />
                  ))}
                {!stats?.calls_by_provider && <p className="text-zinc-500 text-sm">No data yet</p>}
              </div>
            </CardContent>
          </Card>

          {/* Top users */}
          {stats?.top_users_by_calls?.length > 0 && (
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-white mb-4">Top Users by Gateway Calls</h3>
                <div className="space-y-2">
                  {stats.top_users_by_calls.map((u, i) => (
                    <div key={u.user_id} className="flex items-center justify-between py-1 border-b border-white/5">
                      <span className="text-xs text-zinc-500">#{i + 1} {u.user_id.slice(0, 16)}…</span>
                      <Badge className="bg-indigo-500/20 text-indigo-300">{u.calls} calls</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── COST HEALTH ── 6 metrics that tell you where money leaks */}
      {activeSection === "cost_health" && (
        <CostHealthSection token={token} />
      )}

      {/* ── PROVIDER ONBOARDING ── activate dormant providers */}
      {activeSection === "onboarding" && (
        <ProviderOnboardingSection token={token} />
      )}

      {/* ── AGENT OFFICES ── every agent's workspace, SOP, skills, quality rules */}
      {activeSection === "offices" && (
        <AgentOfficesSection token={token} />
      )}

      {/* ── AGENT TEAMS ── 29 collaborative workspaces, 499 agents */}
      {activeSection === "teams" && (
        <AgentTeamsSection token={token} />
      )}

      {/* ── TREASURY ── Revenue / COGS reserve / Profit, the unified money view */}
      {activeSection === "treasury" && (
        <TreasurySection token={token} />
      )}

      {/* ── COST AUTOMATION ── daily P&L + provider balances + auto-recharge setup */}
      {activeSection === "cost_automation" && (
        <CostAutomationSection token={token} />
      )}

      {/* ── FINANCIALS / OPERATOR P&L ── (absorbed from /admin/metrics) */}
      {activeSection === "financials" && (
        <div className="space-y-6">
          {/* Window selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-zinc-500 uppercase tracking-wide mr-2">Window</span>
            {[1, 7, 30, 90].map(d => (
              <Button
                key={d}
                size="sm"
                variant={pnlDays === d ? "default" : "outline"}
                onClick={() => setPnlDays(d)}
                className={pnlDays === d ? "bg-indigo-600 hover:bg-indigo-500" : "border-white/10 text-zinc-400"}
              >
                {d}d
              </Button>
            ))}
            <span className="text-[10px] text-zinc-600 ml-3">Reads from gateway_usage_logs · single source of truth.</span>
          </div>

          {/* KPI row — the 5 operator unit-economics numbers */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <StatBox
              label="Requests"
              value={(pnlRouting?.total_requests || 0).toLocaleString()}
              sub={`${pnlDays}-day window`}
              icon={Activity}
              color="indigo"
            />
            <StatBox
              label="Operator Revenue (Subs Split)"
              value={`$${(pnlRevenue?.total_revenue_usd || 0).toFixed(2)}`}
              sub={`${(pnlRevenue?.by_package || []).length} packages`}
              icon={DollarSign}
              color="emerald"
            />
            <StatBox
              label="Provider Spend (USD)"
              value={`$${(pnlSpend?.total_cost_usd || 0).toFixed(4)}`}
              sub="What MAARS pays providers"
              icon={TrendingUp}
              color="violet"
            />
            <StatBox
              label="Margin @ 1000/USD"
              value={`${pnlProfit?.margin_pct || 0}%`}
              sub={`$${(pnlProfit?.net_usd || 0).toFixed(4)} net`}
              icon={BarChart3}
              color="amber"
            />
            <StatBox
              label="Fallback Rate"
              value={`${stats?.fallback_rate_pct || 0}%`}
              sub={`${stats?.fallback_count || 0} of ${totalCalls.toLocaleString()} calls`}
              icon={RefreshCw}
              color="rose"
            />
          </div>

          {/* ── Per-Track Routing + Cost Attribution ─────────────────
              Every deliverable type has its own dedicated $/credit rate
              (no merging). This strip shows, for the selected window,
              how traffic split across the 8 tracks and what it cost
              the operator by track. Pulls live from /admin/pricing/
              blended-by-category which powers the same rates the
              Pricing Command Center, Package Advisor, and router
              all consume — single source of truth. */}
          {blendedByCategory && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Activity className="w-4 h-4 text-teal-400" />
                Per-Track Routing + Cost
                <span className="text-[10px] text-zinc-500 font-normal ml-2">
                  live $/credit · each track dedicated · no merging
                </span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
                {[
                  { key: "chat",      label: "Chat",      color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/5" },
                  { key: "code",      label: "Code/Vibe", color: "text-violet-400  border-violet-500/30  bg-violet-500/5"  },
                  { key: "image_std", label: "Image Std", color: "text-rose-300    border-rose-500/30    bg-rose-500/5"    },
                  { key: "image_hd",  label: "Image HD",  color: "text-fuchsia-400 border-fuchsia-500/30 bg-fuchsia-500/5" },
                  { key: "video",     label: "Video",     color: "text-amber-400   border-amber-500/30   bg-amber-500/5"   },
                  { key: "voiceover", label: "Voiceover", color: "text-sky-400     border-sky-500/30     bg-sky-500/5"     },
                  { key: "tts",       label: "TTS",       color: "text-cyan-400    border-cyan-500/30    bg-cyan-500/5"    },
                  { key: "stt",       label: "STT",       color: "text-teal-400    border-teal-500/30    bg-teal-500/5"    },
                ].map(({ key, label, color }) => {
                  const t = blendedByCategory[key] || {};
                  const v = t.value || 0;
                  const calls = t.call_count || 0;
                  const isMeasured = t.source === "real_usage" || t.source === "real_usage_calls_proxy";
                  const spent = (t.total_cost_usd || 0);
                  return (
                    <div key={key} className={`p-2.5 rounded-lg border ${color}`}>
                      <p className="text-[10px] font-semibold mb-1 flex items-center gap-1">
                        {label}
                        <span className={`inline-block w-1.5 h-1.5 rounded-full ${isMeasured ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"}`} />
                      </p>
                      <p className="text-sm font-bold font-mono">
                        {v === 0 ? "FREE" : `$${v.toFixed(8)}`}
                      </p>
                      <p className="text-[9px] text-zinc-500 mt-0.5">
                        {calls.toLocaleString()} calls{spent > 0 && ` · $${spent.toFixed(4)} spent`}
                      </p>
                    </div>
                  );
                })}
              </div>
              <div className="mt-3 text-[10px] text-zinc-600 leading-relaxed">
                Measured tracks (chat / code) read from <span className="font-mono text-zinc-400">gateway_usage_logs</span> grouped by source classification.
                Configured tracks (media) derive from <span className="font-mono text-zinc-400">engine_config</span> × live blended cost.
                Router uses these rates for per-call attribution + auto-escalates to premium when a client has tagged credits for that track.
              </div>
            </CardContent>
          </Card>
          )}

          {/* Revenue by package + Top buyers side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-emerald-400" /> Revenue by Package (subscription split)
                </h3>
                {(pnlRevenue?.by_package || []).length === 0 ? (
                  <p className="text-zinc-500 text-sm">No subscription revenue in this window yet.</p>
                ) : (
                  <div className="space-y-2">
                    {pnlRevenue.by_package.map((p, i) => (
                      <div key={p.package_id} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                        <div>
                          <div className="text-sm text-white">{p.package_id}</div>
                          <div className="text-[10px] text-zinc-500">
                            {p.count} sales · split {p.operator_share_pct != null ? `${Math.round(p.operator_share_pct * 100)}%` : "?"}
                          </div>
                        </div>
                        <div className="text-sm font-mono text-emerald-400">${(p.revenue_usd || 0).toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Users className="w-4 h-4 text-indigo-400" /> Top Buyers
                </h3>
                {(pnlRevenue?.top_users || []).length === 0 ? (
                  <p className="text-zinc-500 text-sm">No buyers in this window yet.</p>
                ) : (
                  <div className="space-y-2">
                    {pnlRevenue.top_users.slice(0, 10).map((u, i) => (
                      <div key={u.user_id} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                        <div className="text-sm text-zinc-300 truncate max-w-[60%]">{u.user_id}</div>
                        <div className="text-sm font-mono text-indigo-400">${(u.revenue_usd || 0).toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Routing by source + mode */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" /> Routing — by Source (feature)
                </h3>
                {Object.keys(pnlRouting?.by_task_type || {}).length === 0 ? (
                  <p className="text-zinc-500 text-sm">No data in this window yet.</p>
                ) : (
                  <div className="space-y-2">
                    {Object.entries(pnlRouting.by_task_type).slice(0, 12).map(([k, v]) => (
                      <BarRow key={k} label={k} value={v} total={pnlRouting.total_requests || 1} color="amber" />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-indigo-400" /> Routing — by Mode
                </h3>
                {Object.keys(pnlRouting?.by_routing_mode || {}).length === 0 ? (
                  <p className="text-zinc-500 text-sm">No data in this window yet.</p>
                ) : (
                  <div className="space-y-2">
                    {Object.entries(pnlRouting.by_routing_mode).map(([k, v]) => (
                      <BarRow key={k} label={k} value={v} total={pnlRouting.total_requests || 1} color="indigo" />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Provider spend table */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-violet-400" /> Provider Spend
              </h3>
              {(pnlSpend?.providers || []).length === 0 ? (
                <p className="text-zinc-500 text-sm">No provider spend in this window yet.</p>
              ) : (
                <table className="w-full text-[11px]">
                  <thead className="text-zinc-500 border-b border-white/5">
                    <tr>
                      <th className="text-left py-2 font-normal">Provider</th>
                      <th className="text-right py-2 font-normal">Calls</th>
                      <th className="text-right py-2 font-normal">Input Tokens</th>
                      <th className="text-right py-2 font-normal">Output Tokens</th>
                      <th className="text-right py-2 font-normal">Cost (USD)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pnlSpend.providers.map((p) => (
                      <tr key={p.provider} className="border-b border-white/5 hover:bg-white/[0.02]">
                        <td className="py-2 text-white">{p.provider}</td>
                        <td className="py-2 text-right text-zinc-400 font-mono">{p.calls}</td>
                        <td className="py-2 text-right text-zinc-400 font-mono">{(p.input_tokens || 0).toLocaleString()}</td>
                        <td className="py-2 text-right text-zinc-400 font-mono">{(p.output_tokens || 0).toLocaleString()}</td>
                        <td className="py-2 text-right text-violet-400 font-mono">${(p.cost_usd || 0).toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── CLIENT KEYS ── */}
      {activeSection === "clients" && (
        <div className="space-y-4">
          {/* Platform P&L banner */}
          {clientKeys?.platform_totals && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <StatBox label="Total Revenue" value={`$${clientKeys.platform_totals.total_subscription_revenue_usd?.toFixed(2)}`} icon={DollarSign} color="emerald" />
              <StatBox label="AI Budget Allocated" value={`$${clientKeys.platform_totals.total_ai_budget_allocated_usd?.toFixed(2)}`} icon={Coins} color="amber" />
              <StatBox label="Actual AI Cost" value={`$${clientKeys.platform_totals.total_actual_ai_cost_usd?.toFixed(4)}`} icon={TrendingUp} color="rose" />
              <StatBox label="Total Profit" value={`$${clientKeys.platform_totals.total_profit_usd?.toFixed(2)}`} icon={TrendingUp} color="indigo" />
              <StatBox label="Overall Margin" value={`${clientKeys.platform_totals.overall_margin_pct}%`} icon={BarChart3} color="violet" />
            </div>
          )}

          {/* Toolbar */}
          <div className="flex items-center gap-3 flex-wrap">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                value={keySearch}
                onChange={e => setKeySearch(e.target.value)}
                placeholder="Search by name, email, or plan…"
                className="w-full bg-zinc-900 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <Button
              onClick={handleProvisionAll}
              disabled={provisioning}
              size="sm"
              variant="outline"
              className="border-white/10 text-zinc-400 hover:text-white"
            >
              {provisioning ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Key className="w-4 h-4 mr-2" />}
              Provision All
            </Button>
            <span className="text-xs text-zinc-500">{filteredClients.length} clients</span>
          </div>

          {/* Client keys table */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead className="border-b border-white/10">
                    <tr className="text-zinc-500">
                      <th className="text-left p-3 font-medium">Client</th>
                      <th className="text-left p-3 font-medium">Plan</th>
                      <th className="text-left p-3 font-medium">MAARS Key</th>
                      <th className="text-right p-3 font-medium">AI Budget</th>
                      <th className="text-right p-3 font-medium">Spent (USD)</th>
                      <th className="text-right p-3 font-medium">Remaining</th>
                      <th className="text-right p-3 font-medium">Calls</th>
                      <th className="text-right p-3 font-medium">Profit</th>
                      <th className="text-center p-3 font-medium">Billing</th>
                      <th className="text-right p-3 font-medium">Status</th>
                      <th className="text-right p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredClients.map(c => {
                      const isRevealed = revealedKeys[c.user_id];
                      const isEditingBudget = editingBudget[c.user_id] !== undefined;
                      const budgetPct = c.budget_used_pct || 0;

                      return (
                        <tr key={c.user_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                          {/* Client */}
                          <td className="p-3">
                            <p className="text-zinc-200 font-medium">{c.name || "—"}</p>
                            <p className="text-zinc-500 text-[10px]">{c.email}</p>
                          </td>

                          {/* Plan */}
                          <td className="p-3">
                            <Badge className="bg-indigo-500/20 text-indigo-300 text-[10px]">{c.plan_name}</Badge>
                            <p className="text-zinc-500 text-[10px] mt-1">${c.plan_price_usd}/mo</p>
                          </td>

                          {/* Key */}
                          <td className="p-3">
                            <div className="flex items-center gap-1.5">
                              <span className="font-mono text-[10px] text-zinc-400 max-w-[160px] truncate">
                                {isRevealed ? c.key : `maars-sk-${"•".repeat(16)}`}
                              </span>
                              <button
                                onClick={() => setRevealedKeys(prev => ({...prev, [c.user_id]: !prev[c.user_id]}))}
                                className="text-zinc-600 hover:text-zinc-300 transition-colors"
                                title={isRevealed ? "Hide" : "Reveal"}
                              >
                                {isRevealed ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                              </button>
                              {isRevealed && (
                                <button
                                  onClick={() => { navigator.clipboard.writeText(c.key); toast.success("Key copied"); }}
                                  className="text-zinc-600 hover:text-zinc-300 transition-colors"
                                >
                                  <Copy className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          </td>

                          {/* AI Budget */}
                          <td className="p-3 text-right">
                            {isEditingBudget ? (
                              <div className="flex items-center gap-1 justify-end">
                                <span className="text-zinc-500">$</span>
                                <input
                                  type="number"
                                  step="0.01"
                                  defaultValue={c.monthly_budget_usd}
                                  onChange={e => setEditingBudget(prev => ({...prev, [c.user_id]: e.target.value}))}
                                  className="w-16 bg-zinc-800 border border-indigo-500/50 rounded px-1 py-0.5 text-zinc-200 text-xs text-right"
                                  autoFocus
                                />
                                <button onClick={() => handleUpdateBudget(c.user_id, editingBudget[c.user_id] ?? c.monthly_budget_usd)}
                                  className="text-emerald-400 hover:text-emerald-300"><Check className="w-3 h-3" /></button>
                                <button onClick={() => setEditingBudget(prev => { const n = {...prev}; delete n[c.user_id]; return n; })}
                                  className="text-red-400 hover:text-red-300"><X className="w-3 h-3" /></button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1 justify-end">
                                <span className="text-zinc-300">${c.monthly_budget_usd.toFixed(2)}</span>
                                <button
                                  onClick={() => setEditingBudget(prev => ({...prev, [c.user_id]: c.monthly_budget_usd}))}
                                  className="text-zinc-600 hover:text-zinc-400"
                                ><Pencil className="w-3 h-3" /></button>
                              </div>
                            )}
                            {/* Budget bar */}
                            <div className="w-full h-1 bg-zinc-800 rounded-full mt-1.5 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${budgetPct >= 90 ? "bg-red-500" : budgetPct >= 70 ? "bg-amber-500" : "bg-emerald-500"}`}
                                style={{ width: `${Math.min(budgetPct, 100)}%` }}
                              />
                            </div>
                            <p className="text-[10px] text-zinc-600 mt-0.5">{budgetPct}% used</p>
                          </td>

                          {/* Spent */}
                          <td className="p-3 text-right">
                            <span className={`font-mono ${c.actual_spend_usd > 0 ? "text-amber-400" : "text-zinc-500"}`}>
                              ${c.actual_spend_usd.toFixed(6)}
                            </span>
                          </td>

                          {/* Remaining */}
                          <td className="p-3 text-right">
                            <span className={`font-mono ${c.budget_remaining_usd <= 0 ? "text-red-400" : "text-emerald-400"}`}>
                              ${c.budget_remaining_usd.toFixed(4)}
                            </span>
                          </td>

                          {/* Calls */}
                          <td className="p-3 text-right text-zinc-400">{c.total_calls}</td>

                          {/* Profit */}
                          <td className="p-3 text-right">
                            <span className="text-emerald-400 font-medium">${c.total_profit_usd.toFixed(2)}</span>
                            <p className="text-zinc-600 text-[10px]">margin: ${c.gross_margin_usd.toFixed(2)}</p>
                          </td>

                          {/* Billing Mode */}
                          <td className="p-3 text-center">
                            <div className="flex flex-col items-center gap-1">
                              <Badge className={
                                c.billing_mode === "payg"   ? "bg-violet-500/20 text-violet-300 text-[9px]" :
                                c.billing_mode === "hybrid" ? "bg-blue-500/20 text-blue-300 text-[9px]" :
                                "bg-zinc-700/60 text-zinc-400 text-[9px]"
                              }>
                                {c.billing_mode === "payg" ? "PAYG" : c.billing_mode === "hybrid" ? "Hybrid" : "Sub"}
                              </Badge>
                              {c.billing_mode !== "subscription" && (
                                <span className="text-[9px] text-zinc-500">${(c.balance_usd || 0).toFixed(2)} bal</span>
                              )}
                              {c.markup_pct > 0 && (
                                <span className="text-[9px] text-violet-400">{c.markup_pct}% mkp</span>
                              )}
                            </div>
                          </td>

                          {/* Status */}
                          <td className="p-3 text-right">
                            <Badge className={c.key_status === "active"
                              ? "bg-emerald-500/20 text-emerald-300 text-[10px]"
                              : "bg-red-500/20 text-red-300 text-[10px]"}>
                              {c.key_status}
                            </Badge>
                          </td>

                          {/* Actions */}
                          <td className="p-3 text-right">
                            <div className="flex items-center gap-1 justify-end">
                              <button
                                onClick={() => openBillingModal(c)}
                                className="text-zinc-600 hover:text-violet-400 transition-colors"
                                title="Configure billing mode & markup"
                              >
                                <CreditCard className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => { setTopupModal({ userId: c.user_id, name: c.name, balance_usd: c.balance_usd || 0 }); setTopupAmount("10.00"); }}
                                className="text-zinc-600 hover:text-emerald-400 transition-colors"
                                title="Top up PAYG balance"
                              >
                                <ArrowUpRight className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleRegenerateKey(c.user_id, c.name)}
                                className="text-zinc-600 hover:text-amber-400 transition-colors"
                                title="Regenerate key"
                              >
                                <RotateCcw className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleToggleStatus(c.user_id, c.key_status)}
                                className={`transition-colors ${c.key_status === "active" ? "text-zinc-600 hover:text-red-400" : "text-zinc-600 hover:text-emerald-400"}`}
                                title={c.key_status === "active" ? "Suspend" : "Activate"}
                              >
                                {c.key_status === "active" ? <XCircle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                    {filteredClients.length === 0 && (
                      <tr>
                        <td colSpan={11} className="p-8 text-center text-zinc-500">
                          No clients found. Click <strong>Provision All</strong> to generate keys for all existing users.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <p className="text-xs text-zinc-600">
            Keys are auto-generated on registration and updated on plan change.
            <strong className="text-zinc-500"> Budget</strong> = subscription monthly cap.
            <strong className="text-zinc-500"> Billing</strong>: Sub (monthly cap) · PAYG (prepaid balance, per-call deduction) · Hybrid (cap first, then balance).
            <strong className="text-zinc-500"> Markup %</strong> is added on top of provider cost for PAYG/Hybrid clients — this is your margin.
            Click <CreditCard className="w-3 h-3 inline" /> to set billing mode + markup.
            Click <ArrowUpRight className="w-3 h-3 inline" /> to top up a client's PAYG balance.
            Clients call: <code className="bg-zinc-800 px-1 rounded text-indigo-300">{window.location.origin}/api/v1/chat/completions</code>
          </p>
        </div>
      )}

      {/* ── API REFERENCE ── */}
      {activeSection === "sdk" && (
        <div className="space-y-6">
          {/* What is this */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                <Globe className="w-4 h-4 text-indigo-400" /> MAARS Universal API
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                MAARS Universal API is a self-hosted universal AI gateway with 33 direct providers. A single endpoint your clients call from any codebase using any OpenAI SDK.
                175,000+ models across 33 providers. They use their <code className="bg-zinc-800 px-1 rounded text-indigo-300">maars-sk-</code> key (managed by you, invisible to them),
                address models as <code className="bg-zinc-800 px-1 rounded text-indigo-300">provider/model</code> or use 10 smart routing aliases like <code className="bg-zinc-800 px-1 rounded text-indigo-300">maars/auto</code>, <code className="bg-zinc-800 px-1 rounded text-indigo-300">maars/code</code>, <code className="bg-zinc-800 px-1 rounded text-indigo-300">maars/fast</code>.
                All billing, budgets, and per-client P&amp;L are yours to control.
              </p>
            </CardContent>
          </Card>

          {/* Base URL */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5 space-y-3">
              <h3 className="text-sm font-semibold text-white">Base URL</h3>
              <div className="bg-zinc-950 rounded-lg p-3 font-mono text-sm text-emerald-300 flex items-center justify-between">
                <span>{window.location.origin}/api</span>
                <button onClick={() => { navigator.clipboard.writeText(`${window.location.origin}/api`); }} className="text-zinc-600 hover:text-zinc-300">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-zinc-500">Set this as your OpenAI SDK <code className="text-zinc-400">base_url</code>. All <code className="text-zinc-400">/v1/</code> endpoints are mounted here.</p>
            </CardContent>
          </Card>

          {/* Model IDs */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-3">Model Addressing</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                {[
                  // MAARS smart routing aliases
                  ["maars/auto",      "Smart router — best model for your prompt"],
                  ["maars/smart",     "Task-classified routing (code, math, research…)"],
                  ["maars/economy",   "Fastest + cheapest capable model"],
                  ["maars/standard",  "Balanced quality and cost"],
                  ["maars/premium",   "Highest quality, no cost constraints"],
                  ["maars/code",      "Best coding model (Codestral, GPT-4.1, Claude)"],
                  ["maars/vision",    "Best multimodal vision model"],
                  ["maars/reasoning", "Best math/logic reasoning (o4, R1, DeepSeek)"],
                  ["maars/search",    "Web-search augmented (Perplexity Sonar)"],
                  ["maars/fast",      "Sub-second response via Cerebras or Groq"],
                  // Frontier models
                  ["openai/gpt-4.1",              "OpenAI GPT-4.1 (1M ctx)"],
                  ["openai/o4",                   "OpenAI o4 — frontier reasoning"],
                  ["openai/o1",                   "OpenAI o1 — original reasoning"],
                  ["anthropic/claude-opus-4-6",   "Anthropic Claude Opus 4.6"],
                  ["anthropic/claude-sonnet-4-6", "Anthropic Claude Sonnet 4.6"],
                  ["anthropic/claude-3-5-sonnet", "Claude 3.5 Sonnet (workhorse)"],
                  ["google/gemini-2.5-pro",        "Google Gemini 2.5 Pro (2M ctx)"],
                  ["google/gemini-2.5-flash",      "Google Gemini 2.5 Flash"],
                  ["xai/grok-3",                   "xAI Grok-3"],
                  ["xai/grok-2-vision",            "xAI Grok-2 Vision (multimodal)"],
                  ["deepseek/deepseek-r1",         "DeepSeek R1 reasoning"],
                  ["deepseek/deepseek-v3",         "DeepSeek V3 (best value)"],
                  ["mistral/codestral",            "Codestral — code specialist"],
                  ["mistral/pixtral-large",        "Pixtral Large — vision + text"],
                  ["perplexity/sonar-deep-research","Live deep web research"],
                  ["perplexity/sonar-pro",         "Web search + analysis"],
                  // Speed platforms
                  ["groq/llama-4-scout",           "Groq ultra-fast Llama 4 Scout"],
                  ["groq/deepseek-r1-70b",         "DeepSeek-R1 70B on Groq"],
                  ["cerebras/llama-3.3-70b",       "Cerebras — sub-second 70B"],
                  ["hyperbolic/llama-3.1-405b",    "Llama 405B on Hyperbolic"],
                  // Multi-model platforms
                  ["together/llama-4-maverick",    "Llama 4 Maverick on Together"],
                  ["together/hermes-3-70b",        "Hermes 3 70B (Nous Research)"],
                  ["together/mixtral-8x22b",       "Mixtral 8x22B on Together"],
                  ["fireworks/llama-4-scout",      "Llama 4 Scout on Fireworks"],
                  ["sambanova/deepseek-r1",        "DeepSeek-R1 on SambaNova"],
                  // Specialized / Regional
                  ["moonshot/kimi-k2",             "Kimi K2 — agentic coding"],
                  ["moonshot/kimi-128k",           "Kimi 128K long-context"],
                  ["qwen/qwen3-235b",              "Qwen3-235B — largest Qwen"],
                  ["qwen/qwq-32b",                 "QwQ-32B — Qwen reasoning"],
                  ["yi/yi-medium-200k",            "Yi Medium 200K context"],
                  ["zhipu/glm-4-plus",             "GLM-4-Plus (Zhipu AI)"],
                  ["doubao/doubao-pro-128k",       "Doubao Pro 128K (ByteDance)"],
                  ["nvidia/nemotron-ultra",         "Nemotron Ultra 253B (NVIDIA)"],
                  ["upstage/solar-pro",            "Solar Pro (Upstage)"],
                  ["writer/palmyra-x-004",         "Palmyra X 004 (Writer)"],
                  ["llama/llama-4-maverick",       "Llama 4 Maverick (Meta API)"],
                  ["minimax/minimax-text-01",      "MiniMax Text 01 (Minimax AI)"],
                  ["inception/mercury-coder-small","Mercury Coder Small (Inception AI)"],
                  ["arcee/arcee-maestro",          "Arcee Maestro (Arcee AI)"],
                  ["amazon/nova-pro",              "Nova Pro (Amazon Bedrock)"],
                ].map(([id, desc]) => (
                  <div key={id} className="flex items-start gap-2 py-1 border-b border-white/5">
                    <code className="text-indigo-300 w-52 shrink-0 text-[11px]">{id}</code>
                    <span className="text-zinc-500">{desc}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-zinc-600 mt-3">Full list of 175,000+ models: <code className="text-zinc-400">GET /api/v1/models</code> · Validate a model: <code className="text-zinc-400">GET /api/v1/models/validate?model=openai/gpt-5</code></p>
            </CardContent>
          </Card>

          {/* Code snippets */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[
              {
                label: "Python — Basic",
                lang: "python",
                code: `from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="maars-sk-your-key-here"
)

# Use any provider/model or MAARS smart aliases
response = client.chat.completions.create(
    model="maars/auto",           # smart routing
    # model="anthropic/claude-sonnet-4-6"
    # model="groq/llama-4-scout"  # ultra-fast
    # model="maars/code"          # best coding model
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=1024,
)
print(response.choices[0].message.content)
# x_maars field shows cost, latency, actual provider used
print(response.x_maars)`
              },
              {
                label: "Python — Tool Calling",
                lang: "python",
                code: `from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="maars-sk-your-key-here"
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius","fahrenheit"]}
            },
            "required": ["city"]
        }
    }
}]

response = client.chat.completions.create(
    model="openai/gpt-4.1",   # or anthropic/claude-sonnet-4-6
    messages=[{"role": "user", "content": "What's the weather in London?"}],
    tools=tools,
    tool_choice="auto",
)
# Handle tool call
if response.choices[0].finish_reason == "tool_calls":
    call = response.choices[0].message.tool_calls[0]
    print(call.function.name, call.function.arguments)`
              },
              {
                label: "Python — Vision (Image Input)",
                lang: "python",
                code: `from openai import OpenAI
import base64

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="maars-sk-your-key-here"
)

# Encode local image to base64
with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="maars/vision",    # auto-selects best vision model
    # model="openai/gpt-4o"
    # model="google/gemini-2.5-flash"
    messages=[{
        "role": "user",
        "content": [
            {"type": "text",      "text": "Describe this image in detail."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }],
    max_tokens=512,
)
print(response.choices[0].message.content)`
              },
              {
                label: "Python — Streaming",
                lang: "python",
                code: `from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="maars-sk-your-key-here"
)

# Native streaming — 22 providers support true SSE
stream = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Explain quantum entanglement"}],
    stream=True,
    temperature=0.5,
    max_tokens=2048,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)`
              },
              {
                label: "Python — Embeddings",
                lang: "python",
                code: `from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="maars-sk-your-key-here"
)

# Text embeddings via OpenAI, Cohere, or HuggingFace
response = client.embeddings.create(
    model="text-embedding-3-small",   # OpenAI
    # model="embed-english-v3.0"       # Cohere
    input="MAARS is a unified AI gateway",
)
vector = response.data[0].embedding
print(f"Embedding dim: {len(vector)}")`
              },
              {
                label: "JavaScript / Node.js",
                lang: "js",
                code: `import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "${window.location.origin}/api",
  apiKey: "maars-sk-your-key-here",
});

// Full parameter passthrough
const response = await client.chat.completions.create({
  model: "maars/auto",
  messages: [{ role: "user", content: "Hello!" }],
  temperature: 0.7,
  max_tokens: 1024,
  // tools: [...],          // function calling
  // response_format: { type: "json_object" }, // JSON mode
  // seed: 42,              // reproducible outputs
});
console.log(response.choices[0].message.content);
console.log(response.x_maars); // cost, latency, provider`
              },
              {
                label: "cURL — Chat",
                lang: "bash",
                code: `curl ${window.location.origin}/api/v1/chat/completions \\
  -H "Authorization: Bearer maars-sk-your-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "maars/auto",
    "messages": [{"role":"user","content":"Hello!"}],
    "temperature": 0.7,
    "stream": false
  }'`
              },
              {
                label: "cURL — List Models",
                lang: "bash",
                code: `# List all 175,000+ models
curl ${window.location.origin}/api/v1/models \\
  -H "Authorization: Bearer maars-sk-your-key"

# List all providers
curl ${window.location.origin}/api/v1/providers \\
  -H "Authorization: Bearer maars-sk-your-key"

# Check your usage + budget
curl ${window.location.origin}/api/v1/usage \\
  -H "Authorization: Bearer maars-sk-your-key"`
              },
            ].map(({ label, code }) => (
              <Card key={label} className="bg-zinc-950 border-white/10">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-zinc-400">{label}</span>
                    <button onClick={() => { navigator.clipboard.writeText(code); }} className="text-zinc-600 hover:text-zinc-300">
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <pre className="text-xs text-zinc-300 overflow-x-auto whitespace-pre-wrap leading-relaxed">{code}</pre>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Endpoints */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-3">Complete API Reference</h3>
              <div className="space-y-3 text-xs">
                {[
                  ["POST", "/v1/chat/completions",   "Chat completions — full OpenAI params: tools, vision, temperature, top_p, seed, response_format, n, logprobs…"],
                  ["POST", "/v1/completions",        "Legacy text completions (OpenAI compatible)"],
                  ["POST", "/v1/embeddings",         "Text embeddings — proxies to OpenAI, Cohere, or HuggingFace"],
                  ["GET",  "/v1/models",             "List all 175,000+ models with pricing, context length, provider"],
                  ["GET",  "/v1/models/{model_id}",  "Single model card with full metadata"],
                  ["GET",  "/v1/models/validate",    "Live check: is model active on provider API? Returns suggestions on miss"],
                  ["POST", "/v1/models/compare",     "Run same prompt on up to 4 models in parallel, returns latency/cost/tokens per model"],
                  ["GET",  "/v1/providers",          "List all 33 providers — configured status, capabilities, tier"],
                  ["GET",  "/v1/usage",              "Key spend, budget remaining, per-model and per-provider breakdown"],
                  ["GET",  "/v1/rate-limits",        "Rate limit status for this key"],
                ].map(([method, path, desc]) => (
                  <div key={path} className="flex items-start gap-3 py-2 border-b border-white/5">
                    <Badge className={`text-[10px] w-12 justify-center shrink-0 ${method === "POST" ? "bg-emerald-500/20 text-emerald-300" : "bg-blue-500/20 text-blue-300"}`}>{method}</Badge>
                    <code className="text-indigo-300 w-56 shrink-0">{path}</code>
                    <span className="text-zinc-500">{desc}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── PROVIDER HEALTH ── (balance + health + models + actions merged into one card per provider) */}
      {activeSection === "providers" && health && (() => {
        // Normalize aliases between the two endpoints (balance uses "google" /
        // "nvidia_nim" / "bedrock"; health uses "gemini" / "nvidia" / "amazon").
        // Canonical form is whatever the balance endpoint uses since it covers
        // more providers (38 vs 25).
        const CANONICAL = {
          gemini: "google", nvidia: "nvidia_nim", amazon: "bedrock",
          llama: "meta_llama_api",
        };
        const canon = (s) => CANONICAL[s] || s;
        // Build a joined map: canonical-slug → { ...balance, ...health }
        const byId = {};
        (balanceData?.providers || []).forEach(b => { byId[canon(b.slug)] = { ...b }; });
        (health.providers || []).forEach(h => {
          const k = canon(h.id);
          byId[k] = { ...(byId[k] || {}), ...h, slug: k };
        });
        const providers = Object.values(byId);
        const alerts = balanceData?.alerts || [];
        const configs = balanceData?.configs || [];
        // Sort: failing-with-key first (operator-actionable), then low-balance,
        // then healthy, then inactive (no key) last.
        providers.sort((a, b) => {
          const aActive = a.is_active ? 1 : 0;
          const bActive = b.is_active ? 1 : 0;
          const aFail = a.smoke_status === "fail" ? 1 : 0;
          const bFail = b.smoke_status === "fail" ? 1 : 0;
          if (aFail !== bFail) return bFail - aFail;
          if (aActive !== bActive) return bActive - aActive;
          const aLow = (a.balance_usd != null && a.tier !== "free" && a.balance_usd < 2) ? 1 : 0;
          const bLow = (b.balance_usd != null && b.tier !== "free" && b.balance_usd < 2) ? 1 : 0;
          if (aLow !== bLow) return bLow - aLow;
          return 0;
        });

        // Badge reflects whether the provider actually works RIGHT NOW.
        // A successful smoke call IS a live probe — if the provider returned
        // a real chat completion, "Live" is the accurate label regardless of
        // whether we can also scrape their dollar balance. The historical
        // tier1_api/tier2_estimated split only describes how the $ figure is
        // computed (their billing API vs our usage-log sum) and belongs in a
        // tooltip, not as the primary card badge.
        const badgeFor = (p) => {
          if (p.smoke_status === "ok")         return { cls: "bg-teal-500/20 text-teal-300",       label: "Live" };
          if (p.smoke_status === "media_only") return { cls: "bg-violet-500/20 text-violet-300",   label: "Live" };
          if (p.smoke_status === "fail")       return { cls: "bg-rose-500/20 text-rose-300",       label: "Needs Fix" };
          if (p.tier === "free")               return { cls: "bg-emerald-500/20 text-emerald-300", label: "Free Tier" };
          if (p.tier === "unconfigured")       return { cls: "bg-zinc-500/20 text-zinc-400",       label: "No Key" };
          if (p.is_active)                     return { cls: "bg-amber-500/20 text-amber-300",     label: "Untested" };
          return { cls: "bg-zinc-500/20 text-zinc-400", label: "Inactive" };
        };
        const tierTooltip = {
          tier1_api: "Balance read from provider's own billing API",
          tier2_estimated: "Balance estimated from gateway_usage_logs (provider has no public balance endpoint)",
          free: "Free tier — no balance to track",
          unconfigured: "No API key configured",
        };

        return (
          <div className="space-y-4">
            {/* Summary + Refresh + Smoke-Test */}
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="text-sm text-zinc-400">
                <span className="text-white font-semibold">{providers.length}</span> providers ·{" "}
                <span className="text-emerald-400">{providers.filter(p => p.smoke_status === "ok" || p.smoke_status === "media_only").length} reachable</span> ·{" "}
                <span className="text-red-400">{providers.filter(p => p.smoke_status === "fail").length} pending fix</span> ·{" "}
                <span className="text-zinc-500">{providers.filter(p => !p.is_active).length} need signup</span>
                {alerts.length > 0 && <> · <span className="text-red-400">{alerts.length} low-balance alert{alerts.length !== 1 ? "s" : ""}</span></>}
                {health.smoke_generated_at && (
                  <div className="text-[10px] text-zinc-600 mt-0.5">Last smoke test: {health.smoke_generated_at}</div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    setBalanceRefreshing(true);
                    try {
                      const r = await fetch(`${API}/admin/gateway/smoke-test`, { method: "POST", headers });
                      if (r.ok) {
                        toast.success("Smoke test complete — refreshing");
                        await load(true);
                      } else toast.error("Smoke test failed");
                    } catch { toast.error("Smoke test error"); }
                    finally { setBalanceRefreshing(false); }
                  }}
                  disabled={balanceRefreshing}
                  className="border-white/10 text-zinc-400 hover:text-white"
                >
                  <TestTube2 className={`w-3 h-3 mr-2 ${balanceRefreshing ? "animate-spin" : ""}`} />
                  Run Smoke Test
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={refreshBalances}
                  disabled={balanceRefreshing}
                  className="border-white/10 text-zinc-400 hover:text-white"
                >
                  <RefreshCw className={`w-3 h-3 mr-2 ${balanceRefreshing ? "animate-spin" : ""}`} />
                  Refresh Balances
                </Button>
              </div>
            </div>

            {/* Low-balance alert banner */}
            {alerts.length > 0 && (
              <Card className="bg-red-500/5 border-red-500/30">
                <CardContent className="p-4">
                  <div className="text-xs font-semibold text-red-300 uppercase tracking-wide mb-2">Low Balance Alerts</div>
                  <div className="space-y-1">
                    {alerts.map(a => (
                      <div key={a.slug} className="flex items-center justify-between text-xs">
                        <span className="text-zinc-300">
                          <span className={a.severity === "critical" ? "text-red-400" : "text-amber-400"}>●</span>{" "}
                          <strong>{a.display_name}</strong>: ${a.balance_usd?.toFixed(2)}{" "}
                          <span className="text-zinc-500">(threshold ${a.threshold_usd?.toFixed(2)})</span>
                        </span>
                        {a.dashboard_url && (
                          <a href={a.dashboard_url} target="_blank" rel="noopener noreferrer" className="text-teal-400 hover:text-teal-300">Top Up →</a>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* ── UNBLOCK CENTER ── Single consolidated panel listing every
                Needs-Fix provider + exact action + deposit + deep-link. Lets the
                operator knock them out in one session instead of hunting card-by-card. */}
            {(() => {
              const blocked = providers.filter(p => p.smoke_status === "fail" && p.fix_hint);
              if (blocked.length === 0) return null;
              // Order: free console-clicks → support cases → cheapest deposit → biggest deposit.
              const kindRank = { console: 0, support_case: 1, deposit: 2 };
              const sorted = [...blocked].sort((a, b) => {
                const ak = kindRank[a.fix_hint.kind] ?? 9;
                const bk = kindRank[b.fix_hint.kind] ?? 9;
                if (ak !== bk) return ak - bk;
                return (a.fix_hint.min_deposit_usd || 0) - (b.fix_hint.min_deposit_usd || 0);
              });
              const totalDeposit = sorted.reduce((s, p) => s + (p.fix_hint.min_deposit_usd || 0), 0);
              const freeCount = sorted.filter(p => p.fix_hint.kind === "console").length;
              const supportCaseCount = sorted.filter(p => p.fix_hint.kind === "support_case").length;
              return (
                <Card className="bg-gradient-to-br from-amber-500/5 to-rose-500/5 border-amber-500/30">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <div className="text-sm font-semibold text-amber-300">Unblock Center</div>
                        <div className="text-[11px] text-zinc-500">
                          {sorted.length} provider{sorted.length !== 1 ? "s" : ""} blocked ·{" "}
                          {freeCount > 0 && <><span className="text-emerald-400">{freeCount} free click-through</span> · </>}
                          {supportCaseCount > 0 && <><span className="text-sky-400">{supportCaseCount} support case</span> · </>}
                          <span className="text-amber-400">${totalDeposit} total deposit</span> unlocks all paid
                        </div>
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      {sorted.map(p => {
                        const h = p.fix_hint;
                        const kind = h.kind;
                        const kindStyles = {
                          console:      { row: "bg-emerald-500/5 border-emerald-500/20", tag: "text-emerald-400", cta: "text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10", label: "FREE",    action: "Open ↗" },
                          support_case: { row: "bg-sky-500/5 border-sky-500/20",         tag: "text-sky-400",     cta: "text-sky-400 border-sky-500/30 hover:bg-sky-500/10",         label: "CASE",    action: "Open case ↗" },
                          deposit:      { row: "bg-zinc-900/50 border-white/5",          tag: "text-amber-400",   cta: "text-amber-400 border-amber-500/30 hover:bg-amber-500/10",   label: `$${h.min_deposit_usd}`, action: "Top Up ↗" },
                        };
                        const st = kindStyles[kind] || kindStyles.deposit;
                        return (
                          <div key={p.id} className={`flex items-start gap-3 px-3 py-2 rounded border ${st.row}`}>
                            <div className="flex-shrink-0 w-14 text-right">
                              <span className={`text-[10px] font-mono ${st.tag}`}>{st.label}</span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className={`text-xs font-medium ${PROVIDER_COLORS[p.slug] || "text-zinc-200"}`}>
                                  {p.display_name || p.name}
                                </span>
                                <span className="text-[10px] text-zinc-500">· {h.action}</span>
                              </div>
                              <div className="text-[10px] text-zinc-500 mt-0.5 line-clamp-1">{h.detail}</div>
                            </div>
                            <a
                              href={h.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={`flex-shrink-0 text-[11px] px-2 py-1 rounded border ${st.cta}`}
                            >
                              {st.action}
                            </a>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              );
            })()}

            {/* Unified provider grid — one card per provider */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {providers.map(p => {
                const bal = p.balance_usd;
                const isLow = bal != null && p.tier !== "free" && bal < 2;
                const configEntry = configs.find(c => c.slug === p.slug);
                return (
                  <Card key={p.slug} className={`border ${
                    isLow ? "bg-zinc-950/50 border-red-500/30" :
                    p.is_active ? "bg-zinc-900/50 border-white/10" : "bg-zinc-950/50 border-white/5 opacity-75"
                  }`}>
                    <CardContent className="p-4">
                      {/* Header row — name + tier badge */}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${p.is_active ? "bg-emerald-400" : "bg-zinc-600"}`} />
                          <span className={`text-sm font-medium ${PROVIDER_COLORS[p.slug] || "text-zinc-200"}`}>
                            {p.display_name || p.name || p.slug}
                          </span>
                        </div>
                        {(() => {
                          const b = badgeFor(p);
                          return (
                            <Badge
                              className={`text-[10px] ${b.cls}`}
                              title={tierTooltip[p.tier] || ""}
                            >
                              {b.label}
                            </Badge>
                          );
                        })()}
                      </div>

                      {/* Balance line */}
                      {p.tier === "free" ? (
                        <div className="text-lg font-bold text-emerald-400">Free</div>
                      ) : bal != null ? (
                        <div className={`text-lg font-bold font-mono ${isLow ? "text-red-400" : bal > 10 ? "text-emerald-400" : "text-amber-400"}`}>
                          ${bal.toFixed(2)}
                          {p.unlimited && <span className="text-xs text-zinc-500 ml-2 font-normal">unlimited</span>}
                        </div>
                      ) : p.needs_starting_balance ? (
                        <div className="text-xs text-amber-400">Set starting balance to track →</div>
                      ) : p.is_active ? (
                        <div className="text-xs text-zinc-500">Balance not tracked for this provider</div>
                      ) : (
                        <div className="text-xs text-red-400">No API key — configure in API Keys tab</div>
                      )}

                      {/* Burn rate + days left */}
                      {p.daily_burn_usd != null && (
                        <div className="text-[10px] text-zinc-500 mt-1">
                          Burn: ${p.daily_burn_usd.toFixed(2)}/day
                          {p.days_until_empty != null && (
                            <span className={p.days_until_empty < 3 ? "text-red-400" : p.days_until_empty < 10 ? "text-amber-400" : "text-emerald-400"}>
                              {" "}· {p.days_until_empty.toFixed(0)}d left
                            </span>
                          )}
                        </div>
                      )}

                      {/* ElevenLabs characters */}
                      {p.characters_remaining != null && (
                        <div className="text-[10px] text-zinc-500 mt-1">
                          {p.characters_remaining.toLocaleString()} / {p.characters_limit?.toLocaleString()} chars
                          <div className="w-full h-1 bg-zinc-800 rounded-full mt-1 overflow-hidden">
                            <div className="h-full bg-teal-500" style={{ width: `${Math.min(100, (p.characters_remaining / (p.characters_limit || 1)) * 100)}%` }} />
                          </div>
                        </div>
                      )}

                      {/* Models */}
                      {p.models?.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {p.models.slice(0, 3).map(m => (
                            <span key={m} className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">{m}</span>
                          ))}
                          {p.models.length > 3 && (
                            <span className="text-[10px] text-zinc-600">+{p.models.length - 3}</span>
                          )}
                        </div>
                      )}

                      {/* Health status + key source */}
                      <div className="mt-2 flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          {p.smoke_status === "ok" ? (
                            <><CheckCircle2 className="w-3 h-3 text-emerald-400" />
                              <span className="text-[11px] text-emerald-400">Live · tested OK</span>
                              {p.smoke_wall_ms && <span className="text-[9px] text-zinc-600 ml-1">{p.smoke_wall_ms}ms</span>}</>
                          ) : p.smoke_status === "fail" ? (
                            <><XCircle className="w-3 h-3 text-red-400" />
                              <span className="text-[11px] text-red-400" title={p.smoke_error}>
                                Key present · provider rejected
                              </span></>
                          ) : p.smoke_status === "media_only" ? (
                            <><CheckCircle2 className="w-3 h-3 text-violet-400" />
                              <span className="text-[11px] text-violet-400">Media-only provider</span></>
                          ) : p.is_active ? (
                            <><CheckCircle2 className="w-3 h-3 text-amber-400" />
                              <span className="text-[11px] text-amber-400">Key set · untested</span></>
                          ) : (
                            <><XCircle className="w-3 h-3 text-zinc-500" /><span className="text-[11px] text-zinc-500">Inactive</span></>
                          )}
                        </div>
                        {p.key_source && (
                          <Badge className={`text-[9px] ${
                            p.key_source === "direct"   ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                            p.key_source === "emergent" ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                                                          "bg-zinc-500/10 text-zinc-500 border-zinc-500/20"
                          }`}>
                            {p.key_source === "direct" ? "Direct Key" : p.key_source === "emergent" ? "MAARS Key" : "No Key"}
                          </Badge>
                        )}
                      </div>

                      {/* Fix-hint banner for failing providers — shows exactly what to do */}
                      {p.fix_hint && (
                        <div className="mt-2 p-2 rounded bg-red-500/10 border border-red-500/20">
                          <div className="text-[10px] font-semibold text-red-300">{p.fix_hint.action}</div>
                          <div className="text-[9px] text-zinc-400 mt-0.5 leading-relaxed">{p.fix_hint.detail}</div>
                          {p.fix_hint.link && (
                            <a
                              href={p.fix_hint.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-red-300 hover:text-red-200 mt-1 inline-block font-semibold"
                            >
                              Fix now ↗
                            </a>
                          )}
                        </div>
                      )}
                      {/* Raw smoke error (only when no fix_hint to avoid dup) */}
                      {p.smoke_status === "fail" && p.smoke_error && !p.fix_hint && (
                        <div className="mt-1 text-[9px] text-red-300/70 font-mono truncate" title={p.smoke_error}>
                          {p.smoke_error.length > 80 ? p.smoke_error.slice(0, 80) + "…" : p.smoke_error}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="mt-3 flex gap-2">
                        {p.dashboard_url && (
                          <a
                            href={p.dashboard_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 rounded text-[10px] font-medium bg-teal-500/10 text-teal-300 border border-teal-500/20 hover:bg-teal-500/20"
                          >
                            Top Up ↗
                          </a>
                        )}
                        <button
                          onClick={() => {
                            setConfigSlug(p.slug);
                            setConfigBalance(configEntry?.starting_balance_usd || "");
                            setConfigThreshold(configEntry?.alert_threshold_usd || "");
                          }}
                          className="px-2 py-1 rounded text-[10px] font-medium bg-white/5 text-zinc-400 border border-white/10 hover:bg-white/10"
                        >
                          Configure
                        </button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <p className="text-xs text-zinc-500">
              Configure API keys in the <strong className="text-zinc-400">API Keys & Integrations</strong> tab.
              Providers without a direct key show as inactive. Free-tier providers (Groq, Gemini, Cerebras, etc.) have no balance to track.
            </p>

            {/* Configure modal */}
            {configSlug && (
              <div
                className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
                onClick={() => setConfigSlug(null)}
              >
                <Card
                  className="bg-zinc-900 border-white/10 w-96 max-w-[90vw]"
                  onClick={e => e.stopPropagation()}
                >
                  <CardContent className="p-5">
                    <h3 className="text-base font-semibold text-white mb-4">Configure: {configSlug}</h3>
                    <label className="text-xs text-zinc-400 mb-1 block">Starting Balance (USD)</label>
                    <input
                      type="number" step="0.01" value={configBalance}
                      onChange={e => setConfigBalance(e.target.value)}
                      placeholder="e.g. 20.00"
                      className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white mb-3 focus:outline-none focus:border-teal-500"
                    />
                    <label className="text-xs text-zinc-400 mb-1 block">Alert Threshold (USD)</label>
                    <input
                      type="number" step="0.01" value={configThreshold}
                      onChange={e => setConfigThreshold(e.target.value)}
                      placeholder="e.g. 2.00"
                      className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white mb-4 focus:outline-none focus:border-teal-500"
                    />
                    <div className="flex gap-2 justify-end">
                      <Button size="sm" variant="outline" onClick={() => setConfigSlug(null)} className="border-white/10 text-zinc-400">Cancel</Button>
                      <Button size="sm" onClick={saveProviderConfig} className="bg-teal-600 hover:bg-teal-500">Save</Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        );
      })()}

      {/* ── AGENT TRAINING ── curate golden examples, review training queue,
          rank agents by quality. Lives under Universal Gateway per the
          centralization rule: every AI/LLM admin surface here, not
          scattered across standalone pages. */}
      {activeSection === "training" && (
        <UniversalGatewayTraining token={token} />
      )}

      {/* ── WORKFLOWS ── fleet-wide workflow run health + spend. Reads the
          same gateway_usage_logs as the Financials tab so workflow spend
          is attributed consistently. Links out to /workflow-builder for
          authoring; this tab is pure observability + replay/diagnose. */}
      {activeSection === "workflows" && (
        <UniversalGatewayWorkflows token={token} />
      )}

      {/* ── RAG ── agentic retrieval: doc ingest, corrective-RAG query,
          citations. Uses Docling parser + cosine search over Mongo. */}
      {activeSection === "rag" && (
        <UniversalGatewayRAG token={token} />
      )}

      {/* ── COMMANDER INTELLIGENCE ── consolidated surface for:
          memory graph, SME corrections queue, LLM-judge eval harness,
          MCP token manager, retrieval router playground. */}
      {activeSection === "commander" && (
        <UniversalGatewayCommander token={token} />
      )}

      {/* ── INTELLIGENCE ── embeds the same ProviderIntelligencePage that
          /admin/provider-intelligence used to show as a standalone page. The
          component was designed with embedded=true mode from day one; we just
          host it here so the operator has one admin surface for everything
          gateway-related. Unique function preserved: live /v1/models counts
          per provider (real data, not a static frontend list) and per-provider
          balance/tier/dashboard links pulled from their actual billing APIs. */}
      {activeSection === "intelligence" && (
        <ProviderIntelligencePage embedded={true} initialTab="providers" />
      )}

      {/* ── PACKAGE ADVISOR ── same component, second tab — recommends which
          customer-facing subscription packages are viable based on the live
          capacity (models × free-tier × paid balance) the operator can serve. */}
      {activeSection === "advisor" && (
        <ProviderIntelligencePage embedded={true} initialTab="recommendations" />
      )}

      {/* ── USAGE BREAKDOWN ── */}
      {activeSection === "breakdown" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4">Task Type Distribution</h3>
              <div className="space-y-3">
                {Object.entries(stats?.calls_by_task_type || {})
                  .sort((a, b) => b[1] - a[1])
                  .map(([task, count]) => (
                    <div key={task} className="flex items-center gap-2">
                      <Badge className={`text-[10px] w-24 justify-center ${TASK_COLORS[task] || TASK_COLORS.general}`}>
                        {task}
                      </Badge>
                      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full"
                          style={{ width: `${totalCalls ? (count / totalCalls) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="text-xs text-zinc-400 w-10 text-right">{count}</span>
                    </div>
                  ))}
                {!stats?.calls_by_task_type && <p className="text-zinc-500 text-sm">No data yet</p>}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4">Quality Tier Usage</h3>
              <div className="space-y-3">
                {Object.entries(stats?.calls_by_tier || {})
                  .sort((a, b) => b[1] - a[1])
                  .map(([tier, count]) => (
                    <div key={tier} className="flex items-center gap-2">
                      <Badge className={`text-[10px] w-20 justify-center ${TIER_COLORS[tier] || "bg-zinc-500/20 text-zinc-300"}`}>
                        {tier}
                      </Badge>
                      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            tier === "economy" ? "bg-emerald-500" :
                            tier === "standard" ? "bg-blue-500" : "bg-violet-500"
                          }`}
                          style={{ width: `${totalCalls ? (count / totalCalls) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="text-xs text-zinc-400 w-10 text-right">{count}</span>
                    </div>
                  ))}
              </div>

              <h3 className="text-sm font-semibold text-white mt-6 mb-4">Credit Budget Distribution</h3>
              <div className="space-y-3">
                {Object.entries(stats?.calls_by_credit_budget || {})
                  .sort((a, b) => b[1] - a[1])
                  .map(([budget, count]) => (
                    <div key={budget} className="flex items-center gap-2">
                      <Badge className={`text-[10px] w-20 justify-center ${BUDGET_COLORS[budget] || "bg-zinc-500/20 text-zinc-300"}`}>
                        {budget}
                      </Badge>
                      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            budget === "generous" ? "bg-emerald-500" :
                            budget === "normal"   ? "bg-blue-500" :
                            budget === "tight"    ? "bg-amber-500" : "bg-red-500"
                          }`}
                          style={{ width: `${totalCalls ? (count / totalCalls) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="text-xs text-zinc-400 w-10 text-right">{count}</span>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── ROUTING LOG ── */}
      {activeSection === "logs" && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-0">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Last {logs.length} Routing Decisions</h3>
              <span className="text-xs text-zinc-500">Real-time log · admin only</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="border-b border-white/10">
                  <tr className="text-zinc-500">
                    <th className="text-left p-3 font-medium">Time</th>
                    <th className="text-left p-3 font-medium">User</th>
                    <th className="text-left p-3 font-medium">Provider / Model</th>
                    <th className="text-left p-3 font-medium">Task</th>
                    <th className="text-left p-3 font-medium">Tier</th>
                    <th className="text-right p-3 font-medium">Credits</th>
                    <th className="text-right p-3 font-medium">Cost (USD)</th>
                    <th className="text-right p-3 font-medium">Latency</th>
                    <th className="text-right p-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, i) => (
                    <>
                      <tr
                        key={log.log_id || i}
                        onClick={() => setExpandedLog(expandedLog === i ? null : i)}
                        className="border-b border-white/5 hover:bg-white/5 cursor-pointer"
                      >
                        <td className="p-3 text-zinc-500 whitespace-nowrap">
                          {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : "—"}
                        </td>
                        <td className="p-3">
                          <div className="text-zinc-300 truncate max-w-[120px]">{log.user_name || "—"}</div>
                          <div className="text-zinc-600 text-[10px] truncate max-w-[120px]">{log.user_email}</div>
                        </td>
                        <td className="p-3">
                          <span className={`font-medium ${PROVIDER_COLORS[log.provider] || "text-zinc-300"}`}>
                            {log.provider}
                          </span>
                          <div className="text-zinc-500 text-[10px] truncate max-w-[160px]">{log.model}</div>
                        </td>
                        <td className="p-3">
                          <Badge className={`text-[10px] ${TASK_COLORS[log.task_type] || TASK_COLORS.general}`}>
                            {log.task_type || "general"}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge className={`text-[10px] ${TIER_COLORS[log.quality_tier] || "bg-zinc-500/20 text-zinc-300"}`}>
                            {log.quality_tier}
                          </Badge>
                        </td>
                        <td className="p-3 text-right text-zinc-300">{log.credits_used}</td>
                        <td className="p-3 text-right text-amber-400">${log.cost_usd?.toFixed(6) || "0"}</td>
                        <td className="p-3 text-right text-zinc-400">{log.latency_ms}ms</td>
                        <td className="p-3 text-right">
                          {log.fallback_used
                            ? <Badge className="bg-amber-500/20 text-amber-300 text-[10px]">Fallback</Badge>
                            : <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px]">Direct</Badge>}
                        </td>
                      </tr>
                      {expandedLog === i && (
                        <tr key={`${i}-detail`} className="border-b border-white/5 bg-zinc-900/80">
                          <td colSpan={9} className="p-4">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                              <div><span className="text-zinc-500">Complexity:</span> <span className="text-zinc-300">{log.task_complexity}</span></div>
                              <div><span className="text-zinc-500">Credit Budget:</span> <span className="text-zinc-300">{log.credit_budget}</span></div>
                              <div><span className="text-zinc-500">Attempts:</span> <span className="text-zinc-300">{log.attempts}</span></div>
                              <div><span className="text-zinc-500">Prompt Words:</span> <span className="text-zinc-300">{log.prompt_words}</span></div>
                              <div className="col-span-2"><span className="text-zinc-500">Log ID:</span> <span className="text-zinc-500 font-mono">{log.log_id}</span></div>
                              <div><span className="text-zinc-500">Date:</span> <span className="text-zinc-300">{log.timestamp ? new Date(log.timestamp).toLocaleString() : "—"}</span></div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                  {logs.length === 0 && (
                    <tr>
                      <td colSpan={9} className="p-8 text-center text-zinc-500">
                        No gateway calls recorded yet. Calls appear here as users interact with the Universal Router.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── PLAYGROUND ── */}
      {activeSection === "playground" && (
        <div className="space-y-5">
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Play className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-semibold text-white">Model Playground</h3>
                <Badge className="bg-indigo-500/20 text-indigo-300 text-[10px] ml-auto">Admin-only — no key required</Badge>
              </div>

              {/* Model + Params row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-1">
                  <label className="text-xs text-zinc-400 mb-1 block">Model</label>
                  <select
                    value={playModel}
                    onChange={e => setPlayModel(e.target.value)}
                    className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <optgroup label="MAARS Smart Routing">
                      {["maars/auto","maars/smart","maars/economy","maars/standard","maars/premium","maars/code","maars/vision","maars/reasoning","maars/search","maars/fast"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="OpenAI">
                      {["openai/gpt-4.1","openai/gpt-4.1-mini","openai/gpt-4o","openai/gpt-4o-mini","openai/o4","openai/o4-mini","openai/o3"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Anthropic">
                      {["anthropic/claude-opus-4-6","anthropic/claude-sonnet-4-6","anthropic/claude-haiku-4-5","anthropic/claude-3-5-sonnet"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Google">
                      {["google/gemini-2.5-pro","google/gemini-2.5-flash","google/gemini-2.0-flash"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="xAI / DeepSeek / Mistral">
                      {["xai/grok-3","deepseek/deepseek-v3","deepseek/deepseek-r1","mistral/mistral-large","mistral/codestral"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="High Speed (Groq / Cerebras)">
                      {["groq/llama-4-scout","groq/llama-3.3-70b","cerebras/llama-3.3-70b","cerebras/llama-3.1-8b"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                    <optgroup label="Open Source (Together / Fireworks)">
                      {["together/llama-4-maverick","together/deepseek-r1","fireworks/llama-4-maverick","fireworks/deepseek-v3"].map(m => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </optgroup>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-zinc-400 mb-1 block">Temperature: {playTemp}</label>
                  <input type="range" min="0" max="2" step="0.1" value={playTemp}
                    onChange={e => setPlayTemp(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500" />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 mb-1 block">Max Tokens: {playMaxTokens}</label>
                  <input type="range" min="256" max="8192" step="256" value={playMaxTokens}
                    onChange={e => setPlayMaxTokens(parseInt(e.target.value))}
                    className="w-full accent-indigo-500" />
                </div>
              </div>

              {/* System prompt */}
              <div>
                <label className="text-xs text-zinc-400 mb-1 block">System Prompt (optional)</label>
                <textarea
                  value={playSystem}
                  onChange={e => setPlaySystem(e.target.value)}
                  rows={2}
                  placeholder="You are a helpful assistant..."
                  className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              {/* User message */}
              <div>
                <label className="text-xs text-zinc-400 mb-1 block">User Message</label>
                <textarea
                  value={playMessage}
                  onChange={e => setPlayMessage(e.target.value)}
                  rows={4}
                  placeholder="Enter your message..."
                  className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <Button
                onClick={handlePlayground}
                disabled={playLoading || !playMessage.trim()}
                className="bg-indigo-600 hover:bg-indigo-500 text-white w-full"
              >
                {playLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                {playLoading ? "Generating..." : `Send to ${playModel}`}
              </Button>
            </CardContent>
          </Card>

          {/* Response */}
          {playResponse !== null && (
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-5">
                {playMeta?.model_warning && (
                  <div className="mb-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-start gap-2 text-xs text-amber-300">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    <span>{playMeta.model_warning}</span>
                  </div>
                )}
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-emerald-400" /> Response
                  </h3>
                  {playMeta && (
                    <div className="flex gap-3 text-xs text-zinc-400">
                      <span className="text-indigo-400">{playMeta.provider}/{playMeta.native_model?.split("/").pop()}</span>
                      <span>{playMeta.latency_ms}ms</span>
                      <span>{playMeta.prompt_tokens}p + {playMeta.completion_tokens}c tokens</span>
                    </div>
                  )}
                </div>
                <div className="bg-zinc-800/80 rounded-lg p-4 text-sm text-zinc-200 whitespace-pre-wrap font-mono leading-relaxed max-h-96 overflow-y-auto">
                  {playResponse || <span className="text-zinc-500 italic">Empty response</span>}
                </div>
                <button
                  onClick={() => { navigator.clipboard.writeText(playResponse); toast.success("Copied!"); }}
                  className="mt-2 text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1"
                >
                  <Copy className="w-3 h-3" /> Copy response
                </button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── COMPARE MODELS ── */}
      {activeSection === "compare" && (
        <div className="space-y-5">
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <GitCompare className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-semibold text-white">Side-by-Side Model Comparison</h3>
                <Badge className="bg-violet-500/20 text-violet-300 text-[10px] ml-auto">Up to 4 models</Badge>
              </div>

              {/* Model selectors */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[0,1,2,3].map(i => (
                  <div key={i}>
                    <label className="text-xs text-zinc-400 mb-1 block">Model {i+1}{i < 2 ? " *" : " (opt)"}</label>
                    <input
                      value={compareModels[i] || ""}
                      onChange={e => {
                        const next = [...compareModels];
                        next[i] = e.target.value;
                        setCompareModels(next);
                      }}
                      placeholder={i < 2 ? "openai/gpt-4o" : "optional"}
                      className="w-full bg-zinc-800 border border-white/10 rounded-lg px-2 py-1.5 text-xs text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-violet-500"
                    />
                  </div>
                ))}
              </div>

              {/* Prompt */}
              <div>
                <label className="text-xs text-zinc-400 mb-1 block">Prompt</label>
                <textarea
                  value={comparePrompt}
                  onChange={e => setComparePrompt(e.target.value)}
                  rows={4}
                  placeholder="Enter comparison prompt..."
                  className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-violet-500 resize-none"
                />
              </div>

              {!myMaarsKey && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs text-amber-300">
                  No MAARS API key detected. Go to <strong>Client Keys</strong> and provision keys first, then return here.
                </div>
              )}

              <Button
                onClick={handleCompare}
                disabled={compareLoading || !comparePrompt.trim() || !myMaarsKey}
                className="bg-violet-600 hover:bg-violet-500 text-white w-full"
              >
                {compareLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <GitCompare className="w-4 h-4 mr-2" />}
                {compareLoading ? "Running comparison..." : "Compare Models"}
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          {compareResults && (
            <div className={`grid gap-4 ${compareResults.length === 2 ? "grid-cols-2" : compareResults.length === 3 ? "grid-cols-3" : "grid-cols-2 md:grid-cols-4"}`}>
              {compareResults.map((r, i) => (
                <Card key={i} className={`bg-zinc-900/50 border ${r.error ? "border-red-500/30" : "border-white/10"}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono text-indigo-300 truncate">{r.model}</span>
                      {r.error
                        ? <Badge className="bg-red-500/20 text-red-300 text-[10px] shrink-0 ml-1">Error</Badge>
                        : <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px] shrink-0 ml-1">OK</Badge>}
                    </div>
                    {!r.error && (
                      <div className="flex gap-3 text-[10px] text-zinc-500 mb-2">
                        <span>{r.latency_ms}ms</span>
                        <span>${r.cost_usd?.toFixed(6)}</span>
                        <span>{(r.usage?.prompt_tokens || 0) + (r.usage?.completion_tokens || 0)} tok</span>
                        {r.provider && r.provider !== r.model?.split("/")[0] && (
                          <span className="text-amber-400">↪ fallback</span>
                        )}
                      </div>
                    )}
                    {r.model_warning && (
                      <div className="mb-2 p-1.5 bg-amber-500/10 border border-amber-500/20 rounded text-[10px] text-amber-300 flex items-start gap-1">
                        <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                        <span className="leading-tight">{r.model_warning}</span>
                      </div>
                    )}
                    <div className="bg-zinc-800/60 rounded p-2 text-xs text-zinc-300 whitespace-pre-wrap max-h-64 overflow-y-auto leading-relaxed">
                      {r.error
                        ? <span className="text-red-400">{r.error}</span>
                        : r.content || <span className="text-zinc-500 italic">Empty</span>}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── WEBHOOKS ── */}
      {activeSection === "webhooks" && (
        <div className="space-y-5">
          {/* MAARS Key input */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Key className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-semibold text-white">Your MAARS API Key</h3>
                <span className="text-xs text-zinc-500 ml-2">Required to manage webhooks via /v1/webhooks API</span>
              </div>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={myMaarsKey}
                  onChange={e => setMyMaarsKey(e.target.value)}
                  placeholder="maars-sk-..."
                  className="flex-1 bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 font-mono focus:outline-none focus:border-amber-500"
                />
                <Button onClick={loadWebhooks} disabled={whLoading || !myMaarsKey} size="sm" variant="outline" className="border-white/10 text-zinc-400">
                  {whLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                </Button>
              </div>
              {myMaarsKey && <p className="text-xs text-emerald-400 mt-1">Key detected. <button onClick={loadWebhooks} className="underline">Load webhooks</button></p>}
            </CardContent>
          </Card>

          {/* Add webhook form */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center gap-2">
                <PlusCircle className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">Register Webhook</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-zinc-400 mb-1 block">HTTPS Endpoint URL *</label>
                  <input
                    value={whUrl}
                    onChange={e => setWhUrl(e.target.value)}
                    placeholder="https://your-server.com/webhooks/maars"
                    className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 mb-1 block">Description (optional)</label>
                  <input
                    value={whDesc}
                    onChange={e => setWhDesc(e.target.value)}
                    placeholder="Slack budget alerts"
                    className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-zinc-400 mb-2 block">Events to subscribe</label>
                <div className="flex flex-wrap gap-2">
                  {["budget.75", "budget.90", "budget.100", "rate_limit.exceeded", "request.completed"].map(evt => (
                    <label key={evt} className="flex items-center gap-1.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={whEvents.includes(evt)}
                        onChange={e => {
                          if (e.target.checked) setWhEvents(prev => [...prev, evt]);
                          else setWhEvents(prev => prev.filter(x => x !== evt));
                        }}
                        className="accent-emerald-500"
                      />
                      <span className="text-xs text-zinc-300">{evt}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-zinc-800/60 rounded-lg text-xs text-zinc-400">
                <strong className="text-zinc-300">How it works:</strong> When a threshold is crossed, MAARS sends a POST request to your URL with a JSON payload and <code className="text-amber-300">X-MAARS-Signature: sha256=...</code> header (HMAC-SHA256 using your webhook secret). Verify the signature on your server.
              </div>

              <Button
                onClick={handleAddWebhook}
                disabled={addingWh || !whUrl || !myMaarsKey || whEvents.length === 0}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                {addingWh ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <PlusCircle className="w-4 h-4 mr-2" />}
                Register Webhook
              </Button>
            </CardContent>
          </Card>

          {/* Webhooks list */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Webhook className="w-4 h-4 text-indigo-400" /> Active Webhooks
                {webhooks.length > 0 && <Badge className="bg-indigo-500/20 text-indigo-300 text-[10px]">{webhooks.length}</Badge>}
              </h3>
              {webhooks.length === 0 ? (
                <p className="text-sm text-zinc-500 text-center py-6">
                  {myMaarsKey ? "No webhooks configured yet. Register one above." : "Enter your MAARS key above to view webhooks."}
                </p>
              ) : (
                <div className="space-y-3">
                  {webhooks.map(wh => (
                    <div key={wh.webhook_id} className="flex items-start justify-between p-3 bg-zinc-800/50 rounded-lg border border-white/5">
                      <div className="flex-1 min-w-0 mr-3">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono text-zinc-300 truncate">{wh.url}</span>
                          <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px] shrink-0">active</Badge>
                        </div>
                        {wh.description && <p className="text-xs text-zinc-500 mb-1">{wh.description}</p>}
                        <div className="flex gap-1 flex-wrap">
                          {wh.events?.map(e => (
                            <Badge key={e} className="bg-indigo-500/20 text-indigo-300 text-[10px]">{e}</Badge>
                          ))}
                        </div>
                        <p className="text-[10px] text-zinc-600 mt-1">
                          ID: {wh.webhook_id} · {wh.fire_count || 0} fires
                          {wh.last_fired && ` · Last: ${new Date(wh.last_fired).toLocaleString()}`}
                        </p>
                      </div>
                      <div className="flex gap-1 shrink-0">
                        <Button size="sm" variant="outline" className="border-white/10 text-zinc-400 hover:text-cyan-400 h-7 px-2"
                          onClick={() => handleTestWebhook(wh.webhook_id)} title="Test webhook">
                          <Zap className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline" className="border-white/10 text-zinc-400 hover:text-red-400 h-7 px-2"
                          onClick={() => handleDeleteWebhook(wh.webhook_id)} title="Delete webhook">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── PAYG Billing Mode Modal ── */}
      {billingModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-violet-400" />
                Billing Mode — {billingModal.name}
              </h3>
              <button onClick={() => setBillingModal(null)} className="text-zinc-500 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-zinc-400 block mb-2">Billing Mode</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: "subscription", label: "Subscription", desc: "Monthly cap", color: "emerald" },
                    { id: "payg",         label: "Pay-As-You-Go", desc: "Prepaid balance", color: "violet" },
                    { id: "hybrid",       label: "Hybrid",        desc: "Sub + PAYG overflow", color: "blue" },
                  ].map(m => (
                    <button key={m.id}
                      onClick={() => setBillingForm(f => ({ ...f, billing_mode: m.id }))}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        billingForm.billing_mode === m.id
                          ? `border-${m.color}-500/60 bg-${m.color}-500/10`
                          : "border-white/10 bg-zinc-800/50 hover:border-white/20"
                      }`}>
                      <p className="text-xs font-semibold text-white">{m.label}</p>
                      <p className="text-[10px] text-zinc-500 mt-0.5">{m.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs text-zinc-400 block mb-2">
                  Markup % <span className="text-zinc-600">(charged on top of provider cost)</span>
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number" min="0" max="500" step="1"
                    value={billingForm.markup_pct}
                    onChange={e => setBillingForm(f => ({ ...f, markup_pct: e.target.value }))}
                    className="flex-1 bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-violet-500"
                  />
                  <span className="text-zinc-400 text-sm">%</span>
                </div>
                <p className="text-[10px] text-zinc-600 mt-1">
                  Provider cost × {1 + (parseFloat(billingForm.markup_pct) || 0) / 100} = client charge.
                  E.g. GPT-4o at $2.50/1M input → ${(2.50 * (1 + (parseFloat(billingForm.markup_pct) || 0) / 100)).toFixed(2)}/1M billed.
                </p>
              </div>

              {(billingForm.billing_mode === "payg" || billingForm.billing_mode === "hybrid") && (
                <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-lg text-xs text-violet-300">
                  <Wallet className="w-3.5 h-3.5 inline mr-1" />
                  Current balance: <strong>${(billingModal.balance_usd || 0).toFixed(4)}</strong>.
                  Use the top-up button to add credits after saving.
                </div>
              )}
            </div>

            <div className="flex gap-2 mt-6">
              <Button onClick={handleSaveBilling} disabled={savingBilling}
                className="flex-1 bg-violet-600 hover:bg-violet-700 text-white">
                {savingBilling ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                <span className="ml-2">Save</span>
              </Button>
              <Button variant="outline" onClick={() => setBillingModal(null)}
                className="border-white/10 text-zinc-400 hover:text-white">
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ── PAYG Top-Up Modal ── */}
      {topupModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 w-full max-w-sm shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Wallet className="w-4 h-4 text-emerald-400" />
                Top Up Balance — {topupModal.name}
              </h3>
              <button onClick={() => setTopupModal(null)} className="text-zinc-500 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mb-4 p-3 bg-zinc-800/60 rounded-lg text-sm">
              <p className="text-xs text-zinc-500 mb-1">Current Balance</p>
              <p className="text-xl font-bold text-white">${(topupModal.balance_usd || 0).toFixed(4)}</p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-zinc-400 block mb-2">Amount to Add (USD)</label>
                <div className="flex items-center gap-2">
                  <span className="text-zinc-400 text-sm">$</span>
                  <input
                    type="number" min="0.01" step="0.01"
                    value={topupAmount}
                    onChange={e => setTopupAmount(e.target.value)}
                    className="flex-1 bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                {[5, 10, 25, 50, 100].map(amt => (
                  <button key={amt} onClick={() => setTopupAmount(String(amt))}
                    className="flex-1 py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 border border-white/10 rounded-lg text-zinc-300 transition-colors">
                    ${amt}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-2 mt-5">
              <Button onClick={handleTopup} disabled={toppingUp}
                className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white">
                {toppingUp ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUpRight className="w-4 h-4" />}
                <span className="ml-2">Add ${parseFloat(topupAmount || 0).toFixed(2)}</span>
              </Button>
              <Button variant="outline" onClick={() => setTopupModal(null)}
                className="border-white/10 text-zinc-400 hover:text-white">
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── Cost Health: 6-metric leak-finder ─────────────────────────────── */

const CostHealthSection = ({ token }) => {
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API}/admin/gateway/cost-health?days=${days}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(d => { if (!cancelled) setData(d); })
      .catch(() => { if (!cancelled) setData({ ok: false }); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [days, token]);

  if (loading && !data) return <div className="text-zinc-500 py-10 text-center">Loading cost metrics…</div>;
  if (!data?.ok) return <div className="text-zinc-500 py-10 text-center">No data yet — start routing some calls.</div>;
  if (data.empty) return <div className="text-zinc-500 py-10 text-center">gateway_usage_logs is empty. Metrics populate after first LLM call.</div>;

  const m = data.metrics || {};
  const t = data.targets || {};

  const grade = (name, value, reversed = false) => {
    const target = t[name]?.target;
    if (value == null || target == null) return "neutral";
    const ok = reversed ? value >= target : value <= target;
    // Direction from the API: "high"=higher is better, "low"=lower is better
    const dir = t[name]?.direction;
    if (dir === "high") return value >= target ? "good" : "bad";
    if (dir === "low")  return value <= target ? "good" : "bad";
    return ok ? "good" : "bad";
  };

  const colorFor = (g) => g === "good" ? "#34d399" : g === "bad" ? "#fca5a5" : "#a3a3a3";

  const Metric = ({ label, value, unit, targetText, g }) => (
    <Card className="bg-zinc-900/50 border-white/10">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="text-xs text-zinc-500 uppercase tracking-wide">{label}</div>
          <span style={{
            width: 8, height: 8, borderRadius: 999, background: colorFor(g),
          }} />
        </div>
        <div className="text-2xl font-bold mt-2" style={{ color: colorFor(g) }}>
          {value ?? "—"} <span className="text-xs text-zinc-500">{unit}</span>
        </div>
        {targetText && <div className="text-[10px] text-zinc-500 mt-1">target: {targetText}</div>}
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Cost Health</h3>
          <p className="text-xs text-zinc-500 mt-1">Where money leaks — each red dot is a fix to do.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500 uppercase tracking-wide mr-2">Window</span>
          {[1, 7, 30, 90].map(d => (
            <Button key={d} size="sm"
              className={days === d ? "bg-violet-600 text-white" : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"}
              onClick={() => setDays(d)}>
              {d}d
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <Metric
          label="Cost per credit"
          value={`$${(m.cost_per_credit ?? 0).toFixed(6)}`}
          unit="USD/credit"
          targetText={`< $${t.cost_per_credit?.target}`}
          g={grade("cost_per_credit", m.cost_per_credit)}
        />
        <Metric
          label="Free-provider absorption"
          value={`${m.free_absorption_pct ?? 0}%`}
          unit=""
          targetText={`> ${t.free_absorption_pct?.target}%`}
          g={grade("free_absorption_pct", m.free_absorption_pct)}
        />
        <Metric
          label="Cache hit rate"
          value={`${m.cache_hit_pct ?? 0}%`}
          unit=""
          targetText={`> ${t.cache_hit_pct?.target}%`}
          g={grade("cache_hit_pct", m.cache_hit_pct)}
        />
        <Metric
          label="Cascade escalation"
          value={m.escalation_pct == null ? "—" : `${m.escalation_pct}%`}
          unit=""
          targetText={`< ${t.escalation_pct?.target}%`}
          g={grade("escalation_pct", m.escalation_pct)}
        />
        <Metric
          label="Retry multiplier"
          value={`${m.retry_multiplier ?? 1}x`}
          unit=""
          targetText={`< ${t.retry_multiplier?.target}x`}
          g={grade("retry_multiplier", m.retry_multiplier)}
        />
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-5">
            <div className="text-xs text-zinc-500 uppercase tracking-wide">Totals ({data.window_days}d)</div>
            <div className="mt-2 space-y-1 text-xs text-zinc-400">
              <div>Calls: <span className="text-white font-medium">{data.totals?.calls?.toLocaleString()}</span></div>
              <div>Credits: <span className="text-white font-medium">{data.totals?.credits?.toLocaleString()}</span></div>
              <div>API cost: <span className="text-white font-medium">${data.totals?.cost_usd}</span></div>
              <div>Billed: <span className="text-white font-medium">${data.totals?.billed_usd}</span></div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Free-quota utilisation */}
      <div>
        <h4 className="text-sm font-semibold text-white mb-3">Free-quota utilisation (today)</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(m.free_quota_util || {}).map(([prov, q]) => {
            const pct = q.util_pct ?? 0;
            const bar = q.cap ? Math.min(100, pct) : null;
            return (
              <div key={prov} className="bg-zinc-900/50 border border-white/10 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs text-white font-medium">{prov}</div>
                  <div className="text-[10px] text-zinc-500">{q.cap_unit || "—"}</div>
                </div>
                <div className="mt-2 text-[11px] text-zinc-400">
                  {q.used?.toLocaleString() ?? 0} {q.cap ? `/ ${q.cap.toLocaleString()}` : ""}
                </div>
                {bar != null && (
                  <div className="mt-2 h-1.5 bg-zinc-800 rounded">
                    <div className="h-1.5 rounded"
                      style={{
                        width: `${bar}%`,
                        background: bar > 95 ? "#f59e0b" : bar > 50 ? "#34d399" : "#71717a",
                      }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Provider distribution (by calls) */}
      <div>
        <h4 className="text-sm font-semibold text-white mb-3">Provider distribution</h4>
        <div className="bg-zinc-900/50 border border-white/10 rounded-lg divide-y divide-white/5">
          {(data.providers || []).slice(0, 15).map(p => (
            <div key={p.provider} className="flex items-center justify-between p-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-white">{p.provider}</span>
                {p.free_tier && <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/40 text-emerald-300">FREE</span>}
              </div>
              <div className="flex items-center gap-4 text-xs text-zinc-400">
                <div>{p.calls.toLocaleString()} calls</div>
                <div className="text-white font-medium">${p.cost_usd.toFixed(4)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ── Provider Onboarding: activate the dormant providers ──────────── */

const ProviderOnboardingSection = ({ token }) => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState({});           // per-provider busy flag
  const [pasteFor, setPasteFor] = useState(null); // provider id receiving manual paste
  const [pasteValue, setPasteValue] = useState("");
  const [result, setResult] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/admin/providers/onboarding`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await r.json();
      setProviders(d.providers || []);
    } catch (e) {
      setResult({ ok: false, error: String(e?.message || e) });
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { load(); }, []);

  const startSignup = async (prov) => {
    setBusy(b => ({ ...b, [prov]: "starting" }));
    try {
      const r = await fetch(`${API}/admin/providers/onboarding/start`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ provider: prov }),
      });
      const d = await r.json();
      if (d.session_id) {
        // Open the in-app BrowserPanel with this session so the operator
        // sees the provider's signup page and can click through themselves.
        window.open(`/browser?session=${d.session_id}&provider=${prov}`, "_blank");
        setResult({ ok: true, msg: `Session opened for ${prov}. Sign in + come back and click "Grab API key".`, session_id: d.session_id, provider: prov });
      } else {
        setResult({ ok: false, error: d.detail || d.error || "start failed" });
      }
    } catch (e) {
      setResult({ ok: false, error: String(e?.message || e) });
    } finally {
      setBusy(b => ({ ...b, [prov]: null }));
    }
  };

  const grabKey = async (prov) => {
    if (!result?.session_id || result?.provider !== prov) {
      setResult({ ok: false, error: `No active session for ${prov}. Click "Start signup" first.` });
      return;
    }
    setBusy(b => ({ ...b, [prov]: "grabbing" }));
    try {
      const r = await fetch(`${API}/admin/providers/onboarding/grab-key`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ provider: prov, session_id: result.session_id }),
      });
      const d = await r.json();
      if (d.ok) {
        setResult({ ok: true, msg: `${prov} LIVE. Key: ${d.key_preview}` });
        await load();
      } else {
        setResult({ ok: false, error: d.detail || d.error || "grab failed",
                   hint: "Use 'Paste manually' below to enter the key directly." });
      }
    } catch (e) {
      setResult({ ok: false, error: String(e?.message || e) });
    } finally {
      setBusy(b => ({ ...b, [prov]: null }));
    }
  };

  const pasteKey = async (prov) => {
    if (!pasteValue || pasteValue.length < 10) {
      setResult({ ok: false, error: "Paste a valid key first." });
      return;
    }
    setBusy(b => ({ ...b, [prov]: "pasting" }));
    try {
      const r = await fetch(`${API}/admin/providers/onboarding/paste`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ provider: prov, api_key: pasteValue }),
      });
      const d = await r.json();
      if (d.ok) {
        setResult({ ok: true, msg: `${prov} LIVE via paste. Key: ${d.key_preview}` });
        setPasteFor(null);
        setPasteValue("");
        await load();
      } else {
        setResult({ ok: false, error: d.detail || d.error || "paste failed" });
      }
    } catch (e) {
      setResult({ ok: false, error: String(e?.message || e) });
    } finally {
      setBusy(b => ({ ...b, [prov]: null }));
    }
  };

  if (loading) return <div className="text-zinc-500 py-10 text-center">Loading onboardable providers…</div>;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-bold text-white font-['Outfit']">Provider Onboarding</h3>
        <p className="text-xs text-zinc-500 mt-1">
          Activate dormant providers. "Start signup" opens the provider's page in the in-app browser — sign in yourself (2FA, payment, ToS), then click "Grab API key" and MAARS reads the key via DOM and saves it to the vault + .env.
        </p>
      </div>

      {result && (
        <div className={`p-3 rounded border text-xs ${result.ok ? "bg-emerald-900/20 border-emerald-500/30 text-emerald-300" : "bg-red-900/20 border-red-500/30 text-red-300"}`}>
          {result.msg || result.error} {result.hint && <span className="block mt-1 text-zinc-400">{result.hint}</span>}
        </div>
      )}

      <div className="grid gap-3">
        {providers.map(p => {
          const isLive = p.status === "live";
          const b = busy[p.provider];
          return (
            <div key={p.provider} className="bg-zinc-900/50 border border-white/10 rounded-lg p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{p.display_name}</span>
                    {p.supports_google_oauth && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-900/40 text-blue-300">Google OAuth</span>
                    )}
                    {p.needs_credit_card && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-900/40 text-amber-300">Credit card</span>
                    )}
                    {isLive
                      ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-900/40 text-emerald-300">LIVE</span>
                      : <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">NEEDS KEY</span>}
                  </div>
                  <div className="text-[11px] text-zinc-500 mt-1">{p.signup_notes}</div>
                  <div className="text-[10px] text-zinc-600 mt-1 font-mono">env: {p.env_var}</div>
                </div>
                <div className="flex gap-2">
                  {!isLive && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => startSignup(p.provider)}
                        disabled={!!b}
                        className="bg-violet-600 text-white hover:bg-violet-700"
                      >
                        {b === "starting" ? "Opening…" : "Start signup"}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => grabKey(p.provider)}
                        disabled={!!b}
                        className="bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                      >
                        {b === "grabbing" ? "Grabbing…" : "Grab API key"}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => { setPasteFor(pasteFor === p.provider ? null : p.provider); setPasteValue(""); }}
                        className="bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                      >
                        {pasteFor === p.provider ? "Cancel" : "Paste manually"}
                      </Button>
                    </>
                  )}
                  <a href={p.api_keys_url} target="_blank" rel="noopener noreferrer"
                    className="px-3 py-1.5 text-xs text-zinc-400 hover:text-white rounded">
                    Open externally ↗
                  </a>
                </div>
              </div>

              {pasteFor === p.provider && !isLive && (
                <div className="mt-3 flex gap-2">
                  <input
                    type="password"
                    value={pasteValue}
                    onChange={(e) => setPasteValue(e.target.value)}
                    placeholder="Paste API key from provider dashboard"
                    className="flex-1 bg-zinc-800 border border-white/10 rounded px-3 py-1.5 text-xs text-white"
                  />
                  <Button
                    size="sm"
                    onClick={() => pasteKey(p.provider)}
                    disabled={!pasteValue || !!b}
                    className="bg-emerald-600 text-white hover:bg-emerald-700"
                  >
                    {b === "pasting" ? "Saving…" : "Save"}
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/* ── Agent Offices: every agent's workspace + SOP ─────────────────── */

const AgentOfficesSection = ({ token }) => {
  const [departments, setDepartments] = useState([]);
  const [selected, setSelected] = useState(null);         // { department: "..." } or null (show all depts)
  const [offices, setOffices] = useState([]);             // offices in selected department
  const [openAgent, setOpenAgent] = useState(null);       // full office view
  const [loading, setLoading] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [sampleRequest, setSampleRequest] = useState("");
  const [seeding, setSeeding] = useState(false);

  const fetchJ = async (path, opts = {}) => {
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
  };

  useEffect(() => {
    fetchJ("/admin/offices/departments").then(d => setDepartments(d.departments || [])).catch(() => {});
  }, []);

  const loadDepartment = async (dept) => {
    setLoading(true);
    try {
      const d = await fetchJ(`/admin/offices?department=${encodeURIComponent(dept)}`);
      setOffices(d.offices || []);
      setSelected({ department: dept });
      setOpenAgent(null);
    } finally { setLoading(false); }
  };

  const openOffice = async (agent_id) => {
    setLoading(true);
    try { setOpenAgent(await fetchJ(`/admin/offices/${agent_id}`)); }
    finally { setLoading(false); }
  };

  const runSop = async () => {
    if (!openAgent || !sampleRequest.trim()) return;
    setRunResult({ pending: true });
    try {
      const r = await fetchJ("/admin/offices/run-sop", {
        method: "POST",
        body: JSON.stringify({
          agent_id: openAgent.agent_id,
          user_request: sampleRequest,
          dry_run: false,
        }),
      });
      setRunResult(r);
    } catch (e) {
      setRunResult({ ok: false, error: String(e?.message || e) });
    }
  };

  const reseed = async () => {
    setSeeding(true);
    try {
      const r = await fetchJ("/admin/offices/seed", {
        method: "POST",
        body: JSON.stringify({ force_rebuild: true }),
      });
      alert(`Reseeded ${r.offices_created} offices.`);
      const d = await fetchJ("/admin/offices/departments");
      setDepartments(d.departments || []);
    } finally { setSeeding(false); }
  };

  // ── Agent detail view ──
  if (openAgent) {
    return (
      <div className="space-y-4">
        <button onClick={() => setOpenAgent(null)} className="text-xs text-zinc-400 hover:text-white">← back to {selected?.department || "offices"}</button>
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-bold text-white font-['Outfit']">{openAgent.studio_name}</h3>
              <p className="text-xs text-zinc-500 mt-1">{openAgent.agent_name} · {openAgent.department} · network <code className="text-indigo-300">{openAgent.network}</code></p>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-zinc-500 uppercase">monthly budget</div>
              <div className="text-sm text-white font-mono">{openAgent.monthly_budget_credits?.toLocaleString()} credits</div>
            </div>
          </div>
          <p className="text-sm text-zinc-300 mt-3 italic">"{openAgent.mission}"</p>
        </div>

        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <div className="text-xs text-zinc-500 uppercase mb-2">Standard Operating Procedure</div>
            <div className="space-y-2">
              {(openAgent.sop || []).map((step, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className="text-[10px] text-zinc-500 pt-1 w-6 text-right">{i+1}.</div>
                  <div className="flex-1">
                    <div className="text-sm font-bold text-violet-300">{step.name}</div>
                    <div className="text-xs text-zinc-400 mt-0.5">{step.description}</div>
                    {step.tools?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {step.tools.map(t => <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-900/40 text-indigo-300">{t}</span>)}
                      </div>
                    )}
                    {step.expected_output && (
                      <div className="text-[10px] text-zinc-500 mt-0.5">→ {step.expected_output}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">Studio Tools ({(openAgent.studio_tools || []).length})</div>
              <div className="flex flex-wrap gap-1">
                {(openAgent.studio_tools || []).map(t => (
                  <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">{t}</span>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">Quality Rules ({(openAgent.quality_rules || []).length})</div>
              <div className="space-y-1">
                {(openAgent.quality_rules || []).map(q => (
                  <div key={q.name} className="text-xs">
                    <span className={`font-medium ${q.severity === 'hard' ? 'text-rose-300' : 'text-amber-300'}`}>{q.name}</span>
                    <span className="text-zinc-500 ml-2">{q.check}</span>
                  </div>
                ))}
                {(openAgent.quality_rules || []).length === 0 && <div className="text-xs text-zinc-500 italic">no quality rules</div>}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">Skills Library ({(openAgent.skills_library || []).length})</div>
              <div className="space-y-2">
                {(openAgent.skills_library || []).map(s => (
                  <div key={s.skill_id} className="text-xs">
                    <div className="font-medium text-emerald-300">{s.name} <span className="text-zinc-500">· {s.avg_credits} cr</span></div>
                    <div className="text-zinc-400 text-[10px] mt-0.5">{s.description}</div>
                  </div>
                ))}
                {(openAgent.skills_library || []).length === 0 && <div className="text-xs text-zinc-500 italic">no prebuilt skills yet</div>}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">Languages · Memory Tags · Training</div>
              <div className="text-[11px] text-zinc-400">
                <div><span className="text-zinc-500">languages:</span> {(openAgent.languages_supported || []).join(", ")}</div>
                <div className="mt-1"><span className="text-zinc-500">memory tags:</span> {(openAgent.reference_memory_tags || []).join(", ") || "—"}</div>
                <div className="mt-1"><span className="text-zinc-500">golden examples:</span> {openAgent.training_examples_count || 0} curated</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-violet-900/10 border-violet-500/30">
          <CardContent className="p-4">
            <div className="text-xs text-violet-300 uppercase mb-2">Test this office's SOP</div>
            <div className="flex gap-2">
              <input
                type="text"
                value={sampleRequest}
                onChange={(e) => setSampleRequest(e.target.value)}
                placeholder="e.g. 'generate a 30-second product ad for the iPhone 17 Pro Max, lifestyle tone, Spanish voiceover'"
                className="flex-1 bg-zinc-800 border border-white/10 rounded px-3 py-2 text-xs text-white"
              />
              <Button
                size="sm"
                onClick={runSop}
                disabled={!sampleRequest.trim() || runResult?.pending}
                className="bg-violet-600 text-white hover:bg-violet-700"
              >
                {runResult?.pending ? "Running..." : "Run SOP"}
              </Button>
            </div>
            {runResult && !runResult.pending && (
              <pre className="mt-3 p-2 bg-zinc-950 border border-white/5 rounded text-[10px] text-zinc-300 overflow-auto max-h-80">
                {JSON.stringify(runResult, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // ── Department list view ──
  if (selected) {
    return (
      <div className="space-y-3">
        <button onClick={() => setSelected(null)} className="text-xs text-zinc-400 hover:text-white">← back to departments</button>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white font-['Outfit']">{selected.department} <span className="text-zinc-500 font-normal">· {offices.length} offices</span></h3>
        </div>
        {loading ? <div className="text-zinc-500 text-sm py-6 text-center">Loading...</div> : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {offices.map(o => (
              <div
                key={o.agent_id}
                onClick={() => openOffice(o.agent_id)}
                className="bg-zinc-900/50 border border-white/10 rounded-lg p-3 cursor-pointer hover:border-violet-500/40"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-sm font-bold text-white">{o.agent_name}</div>
                    <div className="text-[10px] text-zinc-500">{o.studio_name}</div>
                  </div>
                  <div className="text-[10px] text-zinc-600">{o.sop?.length || 0} steps</div>
                </div>
                <div className="text-[11px] text-zinc-400 mt-2 line-clamp-2">{o.mission}</div>
                <div className="flex gap-1 mt-2 flex-wrap">
                  {(o.skills_library || []).slice(0, 3).map(s => (
                    <span key={s.skill_id} className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-900/40 text-emerald-300">{s.skill_id}</span>
                  ))}
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{(o.languages_supported || ["en"]).length} lang</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Department overview (default) ──
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Agent Offices</h3>
          <p className="text-xs text-zinc-500 mt-1">Every agent has a dedicated studio with a research-first SOP, role-specific tools, skills library, and quality rules. {departments.reduce((s, d) => s + d.office_count, 0)} offices across {departments.length} departments.</p>
        </div>
        <Button size="sm" onClick={reseed} disabled={seeding} className="bg-zinc-800 text-zinc-300 hover:bg-zinc-700">
          {seeding ? "Reseeding..." : "Rebuild all offices"}
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {departments.map(d => (
          <div
            key={d.department}
            onClick={() => loadDepartment(d.department)}
            className="bg-zinc-900/50 border border-white/10 rounded-lg p-4 cursor-pointer hover:border-violet-500/40 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="text-sm font-bold text-white">{d.department}</div>
              <div className="text-lg font-mono text-violet-300">{d.office_count}</div>
            </div>
            <div className="text-[11px] text-zinc-500 mt-2 line-clamp-2">
              {d.agents_sample?.slice(0, 3).join(" · ") || "—"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════
// AgentTeamsSection — 29 collaborative workspaces grouping 499 agents.
// ═══════════════════════════════════════════════════════════════════════
// Teams are the layer above individual agent offices: Video Production
// Team, Strategy Room, Growth & Marketing, etc. Commander Orion delegates
// to teams; teams coordinate their members internally.
//
// Data comes from:
//   GET  /admin/teams                — list with member counts
//   GET  /admin/teams/:id            — one team (mission, tools, members)
//   GET  /admin/teams/:id/members    — resolved agent rows
//   POST /admin/teams/seed           — rebuild from registry
// ═══════════════════════════════════════════════════════════════════════
const AgentTeamsSection = ({ token }) => {
  const [teams, setTeams] = useState([]);
  const [openTeam, setOpenTeam] = useState(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const fetchJ = async (path, opts = {}) => {
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
  };

  const loadTeams = async () => {
    setLoading(true);
    try {
      const d = await fetchJ("/admin/teams");
      setTeams(d.teams || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { loadTeams(); }, []);

  const openTeamDetail = async (team_id) => {
    setLoading(true);
    try {
      const [team, m] = await Promise.all([
        fetchJ(`/admin/teams/${team_id}`),
        fetchJ(`/admin/teams/${team_id}/members`),
      ]);
      setOpenTeam(team);
      setMembers(m.members || []);
    } finally { setLoading(false); }
  };

  const reseed = async () => {
    setSeeding(true);
    try {
      const r = await fetchJ("/admin/teams/seed", {
        method: "POST",
        body: JSON.stringify({ force_rebuild: true }),
      });
      alert(`Seeded ${r.teams_upserted} teams, assigned ${r.agents_assigned}/${r.agents_scanned} agents.`);
      await loadTeams();
    } finally { setSeeding(false); }
  };

  // ── Team detail view ──
  if (openTeam) {
    return (
      <div className="space-y-4">
        <button onClick={() => { setOpenTeam(null); setMembers([]); }}
                className="text-xs text-zinc-400 hover:text-white">
          ← back to all teams
        </button>
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-bold text-white font-['Outfit']">{openTeam.studio_name}</h3>
              <p className="text-xs text-zinc-500 mt-1">
                {openTeam.name} · {openTeam.department} · {openTeam.member_count} members
              </p>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-zinc-500 uppercase">monthly budget</div>
              <div className="text-sm text-white font-mono">{openTeam.monthly_budget_credits?.toLocaleString()} credits</div>
            </div>
          </div>
          <p className="text-sm text-zinc-300 mt-3 italic">"{openTeam.mission}"</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">
                Team Members ({members.length})
              </div>
              <div className="space-y-1 max-h-[340px] overflow-y-auto">
                {members.map(m => (
                  <div key={m.agent_id}
                       className="flex items-center gap-2 text-xs py-1 border-b border-white/5 last:border-0">
                    <span className="text-emerald-300 font-medium truncate flex-1">{m.name}</span>
                    <span className="text-zinc-500 text-[10px] truncate max-w-[40%]">{m.role}</span>
                    {m.is_commander && <span className="text-[9px] px-1 rounded bg-amber-900/40 text-amber-300">CMD</span>}
                  </div>
                ))}
                {members.length === 0 && <div className="text-xs text-zinc-500 italic">no members</div>}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-4">
              <div className="text-xs text-zinc-500 uppercase mb-2">
                Shared Tools ({(openTeam.shared_tools || []).length})
              </div>
              <div className="flex flex-wrap gap-1 mb-4">
                {(openTeam.shared_tools || []).map(t => (
                  <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-900/40 text-indigo-300">{t}</span>
                ))}
              </div>
              <div className="text-xs text-zinc-500 uppercase mb-2">Role Families</div>
              <div className="flex flex-wrap gap-1 mb-4">
                {(openTeam.role_families || []).map(f => (
                  <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-violet-900/40 text-violet-300">{f}</span>
                ))}
              </div>
              <div className="text-xs text-zinc-500 uppercase mb-2">Memory Tags</div>
              <div className="flex flex-wrap gap-1 mb-4">
                {(openTeam.memory_tags || []).map(t => (
                  <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{t}</span>
                ))}
              </div>
              <div className="text-[11px] text-zinc-400">
                <span className="text-zinc-500">languages:</span> {(openTeam.languages_supported || []).join(", ")}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // ── Teams grid ──
  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">
            Agent Teams <span className="text-zinc-500 font-normal">· {teams.length} teams · {teams.reduce((s, t) => s + (t.member_count || 0), 0)} agents</span>
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            Collaborative workspaces grouping the 499 agents. Commander Orion
            delegates to teams; teams coordinate their members on shared SOPs.
          </p>
        </div>
        <button onClick={reseed} disabled={seeding}
                className="text-xs px-3 py-1.5 rounded bg-indigo-900/40 hover:bg-indigo-800/40 text-indigo-300 disabled:opacity-50">
          {seeding ? "Reseeding..." : "Rebuild all teams"}
        </button>
      </div>

      {loading && <div className="text-xs text-zinc-500">loading…</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {teams.map(t => (
          <button
            key={t.team_id}
            onClick={() => openTeamDetail(t.team_id)}
            className="text-left bg-zinc-900/50 border border-white/10 hover:border-violet-500/60 rounded-lg p-4 transition-colors"
          >
            <div className="flex items-start justify-between mb-1">
              <div className="text-sm font-bold text-white truncate">{t.studio_name}</div>
              <div className="text-[10px] text-violet-300 font-mono shrink-0 ml-2">{t.member_count}</div>
            </div>
            <div className="text-[10px] text-zinc-500 mb-2">{t.department}</div>
            <div className="text-xs text-zinc-400 line-clamp-2">{t.mission}</div>
            <div className="flex flex-wrap gap-1 mt-2">
              {(t.role_families || []).slice(0, 3).map(f => (
                <span key={f} className="text-[9px] px-1 py-0.5 rounded bg-violet-900/30 text-violet-300">{f}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};


// ═══════════════════════════════════════════════════════════════════════
// CostAutomationSection — operator P&L + provider-balance monitor +
// native auto-recharge setup guide.
// ═══════════════════════════════════════════════════════════════════════
// Backend: services/billing/cost_automation.py + routes/admin_cost_automation.py
//   GET /admin/cost-automation/pnl          → daily P&L rows (30d window)
//   GET /admin/cost-automation/providers    → per-provider COGS + balance
//   GET /admin/cost-automation/alerts       → low-balance alerts
//   GET /admin/cost-automation/setup-guide  → native auto-recharge URLs
//   POST /admin/cost-automation/run         → force a snapshot tick
// ═══════════════════════════════════════════════════════════════════════
const CostAutomationSection = ({ token }) => {
  const [pnl, setPnl] = useState(null);
  const [providers, setProviders] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [guide, setGuide] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [days, setDays] = useState(30);

  const fetchJ = async (path, opts = {}) => {
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
  };

  const loadAll = async (windowDays = days) => {
    setLoading(true);
    try {
      const [pnlRes, provRes, alertsRes, guideRes] = await Promise.all([
        fetchJ(`/admin/cost-automation/pnl?days=${windowDays}`),
        fetchJ(`/admin/cost-automation/providers?days=${windowDays}`),
        fetchJ("/admin/cost-automation/alerts"),
        fetchJ("/admin/cost-automation/setup-guide"),
      ]);
      setPnl(pnlRes);
      setProviders(provRes);
      setAlerts(alertsRes.alerts || []);
      setGuide(guideRes.providers || []);
    } catch (e) {
      console.error("cost automation load failed", e);
    } finally { setLoading(false); }
  };

  useEffect(() => { loadAll(days); }, [days]);

  const forceTick = async () => {
    setRunning(true);
    try {
      await fetchJ("/admin/cost-automation/run", { method: "POST" });
      await loadAll(days);
    } finally { setRunning(false); }
  };

  const fmt$ = (v) => `$${(Number(v) || 0).toFixed(v >= 1 ? 2 : 4)}`;
  const fmt$big = (v) => `$${(Number(v) || 0).toLocaleString(undefined, {maximumFractionDigits: 2})}`;

  // Aggregate across the window
  const summary = pnl?.days?.reduce((s, d) => ({
    revenue: s.revenue + (d.revenue_usd || 0),
    cogs:    s.cogs    + (d.cogs_usd    || 0),
    calls:   s.calls   + (d.call_count  || 0),
  }), { revenue: 0, cogs: 0, calls: 0 }) || { revenue: 0, cogs: 0, calls: 0 };
  const totalMargin = summary.revenue - summary.cogs;
  const avgMarginPct = summary.revenue > 0 ? (totalMargin / summary.revenue) * 100 : 100;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Cost Automation</h3>
          <p className="text-xs text-zinc-500 mt-1">
            Operator P&amp;L + provider balances + native auto-recharge setup. Tick runs every 30 min; writes daily snapshots + alerts when any provider drops below threshold.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-zinc-500">
            Window:
            {[7, 30, 90].map(d => (
              <button key={d} onClick={() => setDays(d)}
                className={`px-2 py-0.5 rounded ${days===d ? 'bg-indigo-900/40 text-indigo-300' : 'text-zinc-500 hover:text-white'}`}>
                {d}d
              </button>
            ))}
          </div>
          <button onClick={forceTick} disabled={running}
            className="text-xs px-3 py-1.5 rounded bg-indigo-900/40 hover:bg-indigo-800/40 text-indigo-300 disabled:opacity-50">
            {running ? "Running..." : "Force tick"}
          </button>
        </div>
      </div>

      {/* ── P&L aggregate summary ─────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wide">Revenue · {days}d</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">{fmt$big(summary.revenue)}</div>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wide">COGS · {days}d</div>
            <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">{fmt$big(summary.cogs)}</div>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wide">Gross Margin</div>
            <div className="text-2xl font-bold text-white mt-1 font-mono">{fmt$big(totalMargin)}</div>
            <div className="text-[11px] text-zinc-400 mt-1">{avgMarginPct.toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wide">Total Calls · {days}d</div>
            <div className="text-2xl font-bold text-white mt-1 font-mono">{(summary.calls || 0).toLocaleString()}</div>
          </CardContent>
        </Card>
      </div>

      {/* ── Low-balance alerts ─────────────────────────────────── */}
      {alerts.length > 0 && (
        <Card className="bg-rose-950/40 border-rose-900/50">
          <CardContent className="p-4">
            <div className="text-xs font-bold text-rose-300 uppercase tracking-wide mb-3">
              Low-Balance Alerts ({alerts.length})
            </div>
            <div className="space-y-2">
              {alerts.map(a => (
                <div key={a.provider} className="flex items-center justify-between text-xs">
                  <span className="text-white font-medium">{a.provider}</span>
                  <span className="text-rose-300 font-mono">
                    {fmt$(a.balance_usd)} <span className="text-zinc-500">/ threshold {fmt$(a.threshold_usd)}</span>
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Per-provider COGS + balance table ──────────────────── */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="text-xs font-bold text-zinc-300 uppercase tracking-wide mb-3">
            Per-Provider COGS · {days}d
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-zinc-500 uppercase text-[10px] tracking-wide">
                  <th className="text-left py-2">Provider</th>
                  <th className="text-right py-2">COGS</th>
                  <th className="text-right py-2">Calls</th>
                  <th className="text-right py-2">Avg/call</th>
                  <th className="text-right py-2">Balance</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                {(providers?.providers || []).map(p => (
                  <tr key={p.provider} className="border-t border-white/5">
                    <td className="py-2 font-medium text-white">{p.provider}</td>
                    <td className="py-2 text-right font-mono text-rose-300">{fmt$(p.cogs_usd)}</td>
                    <td className="py-2 text-right font-mono">{p.call_count}</td>
                    <td className="py-2 text-right font-mono text-zinc-400">{fmt$(p.avg_usd)}</td>
                    <td className="py-2 text-right font-mono">
                      {p.balance_usd != null
                        ? <span className={p.balance_usd < 5 ? "text-amber-300" : "text-emerald-300"}>{fmt$(p.balance_usd)}</span>
                        : <span className="text-zinc-600">—</span>}
                    </td>
                  </tr>
                ))}
                {(!providers?.providers || providers.providers.length === 0) && (
                  <tr><td colSpan="5" className="py-6 text-center text-zinc-500 italic">
                    No COGS data for window. Run a few API calls first.
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ── Auto-recharge setup guide ─────────────────────────── */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="text-xs font-bold text-zinc-300 uppercase tracking-wide mb-1">
            Native Auto-Recharge Setup
          </div>
          <p className="text-[11px] text-zinc-500 mb-3">
            Providers don't accept revenue-split payments — each one bills the operator's payment method directly.
            Enable native auto-recharge once per provider; MAARS then monitors balances + alerts. Zero manual reconciliation.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {guide.map(p => (
              <a key={p.provider} href={p.url} target="_blank" rel="noopener noreferrer"
                 className="flex items-start gap-3 p-3 rounded bg-zinc-800/40 hover:bg-zinc-800/80 border border-white/5 transition">
                <div className={`mt-1 h-2 w-2 rounded-full shrink-0 ${p.has_key ? 'bg-emerald-400' : 'bg-zinc-600'}`}
                     title={p.has_key ? 'Configured' : 'Not configured'} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{p.display}</span>
                    <span className="text-[10px] text-zinc-500">
                      thresh {fmt$(p.recommended_threshold_usd)} · refill {fmt$(p.recommended_topup_usd)}
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-400 mt-1 line-clamp-2">{p.howto}</div>
                </div>
              </a>
            ))}
          </div>
        </CardContent>
      </Card>

      {loading && <div className="text-xs text-zinc-500">loading…</div>}
    </div>
  );
};


// ═══════════════════════════════════════════════════════════════════════
// TreasurySection — the unified operator money view.
// ═══════════════════════════════════════════════════════════════════════
// Revenue / COGS Reserve / Operator Profit — all three booked automatically
// at every Stripe charge and debited on every API call. No per-provider
// manual reconciliation.
//
// Backend: services/billing/treasury.py + /admin/treasury/* routes.
// ═══════════════════════════════════════════════════════════════════════
const TreasurySection = ({ token }) => {
  const [snap, setSnap] = useState(null);
  const [log, setLog]  = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const fetchJ = async (path, opts = {}) => {
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) },
    });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
  };

  const load = async () => {
    setLoading(true);
    try {
      const [s, l] = await Promise.all([
        fetchJ("/admin/treasury"),
        fetchJ("/admin/treasury/log?limit=50"),
      ]);
      setSnap(s);
      setLog(l.data || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const reconcile = async () => {
    if (!confirm("Close the month: roll any COGS surplus into profit, flag deficits. Proceed?")) return;
    setRunning(true);
    try {
      const r = await fetchJ("/admin/treasury/reconcile", { method: "POST" });
      alert(`Reconcile: ${r.action} ${r.amount_usd ? `($${r.amount_usd.toFixed(2)})` : ''}`);
      await load();
    } finally { setRunning(false); }
  };

  const fmt$ = (v) => `$${(Number(v) || 0).toLocaleString(undefined, {maximumFractionDigits: 2, minimumFractionDigits: 2})}`;

  const kindColor = {
    revenue:             "text-emerald-300",
    profit:              "text-emerald-200",
    reserve:             "text-amber-300",
    cogs_actual:         "text-rose-300",
    reconcile_surplus:   "text-indigo-300",
    reconcile_deficit:   "text-rose-400",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Treasury</h3>
          <p className="text-xs text-zinc-500 mt-1 max-w-2xl">
            One unified money view. Every client payment auto-splits into
            <span className="text-emerald-300"> Revenue</span> · <span className="text-amber-300">COGS Reserve</span> ·
            <span className="text-emerald-200"> Profit</span>. Every API call debits the reserve by actual provider cost.
            You never pick which provider gets what — providers auto-charge your card via their own native auto-recharge; MAARS tracks the money.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={load} disabled={loading}
            className="text-xs px-3 py-1.5 rounded bg-zinc-800/60 hover:bg-zinc-700/60 text-zinc-200 disabled:opacity-50">
            {loading ? "Loading..." : "Refresh"}
          </button>
          <button onClick={reconcile} disabled={running}
            className="text-xs px-3 py-1.5 rounded bg-indigo-900/40 hover:bg-indigo-800/40 text-indigo-200 disabled:opacity-50">
            {running ? "Reconciling..." : "Close month"}
          </button>
        </div>
      </div>

      {snap && (
        <>
          {/* ── Three headline cards ───────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Card className="bg-emerald-950/30 border-emerald-900/40">
              <CardContent className="p-5">
                <div className="text-[10px] text-emerald-400 uppercase tracking-widest font-bold">Revenue (lifetime)</div>
                <div className="text-3xl font-bold text-emerald-300 mt-2 font-mono">{fmt$(snap.revenue_usd)}</div>
                <div className="text-[11px] text-emerald-400/70 mt-1">Stripe + credit packages + top-ups</div>
              </CardContent>
            </Card>
            <Card className="bg-amber-950/30 border-amber-900/40">
              <CardContent className="p-5">
                <div className="text-[10px] text-amber-400 uppercase tracking-widest font-bold">COGS Reserve</div>
                <div className="text-3xl font-bold text-amber-300 mt-2 font-mono">{fmt$(snap.cogs_reserve_usd)}</div>
                <div className="text-[11px] text-amber-400/70 mt-1">
                  Actual COGS spent: {fmt$(snap.cogs_actual_usd)}
                </div>
              </CardContent>
            </Card>
            <Card className="bg-indigo-950/30 border-indigo-900/40">
              <CardContent className="p-5">
                <div className="text-[10px] text-indigo-400 uppercase tracking-widest font-bold">Operator Profit</div>
                <div className="text-3xl font-bold text-indigo-200 mt-2 font-mono">{fmt$(snap.operator_profit_usd)}</div>
                <div className="text-[11px] text-indigo-400/70 mt-1">
                  Gross margin {snap.gross_margin_pct}% · Net profit {fmt$(snap.net_profit_usd)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* ── Surplus rolled + alerts row ───────────────────── */}
          <div className="grid grid-cols-2 gap-3">
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4">
                <div className="text-[10px] text-zinc-500 uppercase tracking-wide">Surplus rolled to profit</div>
                <div className="text-xl font-bold text-emerald-300 mt-1 font-mono">{fmt$(snap.surplus_rolled_usd)}</div>
                <div className="text-[11px] text-zinc-500 mt-1">Unused COGS reserve reclaimed at each reconcile</div>
              </CardContent>
            </Card>
            <Card className={`border-white/10 ${snap.deficit_alerts > 0 ? 'bg-rose-950/30 border-rose-900/40' : 'bg-zinc-900/50'}`}>
              <CardContent className="p-4">
                <div className="text-[10px] text-zinc-500 uppercase tracking-wide">Deficit alerts</div>
                <div className={`text-xl font-bold mt-1 font-mono ${snap.deficit_alerts > 0 ? 'text-rose-300' : 'text-white'}`}>{snap.deficit_alerts}</div>
                <div className="text-[11px] text-zinc-500 mt-1">Times COGS reserve went negative since start</div>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* ── Recent activity ───────────────────────────────────── */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="text-xs font-bold text-zinc-300 uppercase tracking-wide mb-3">Recent Treasury Activity</div>
          {log.length === 0 ? (
            <div className="text-xs text-zinc-500 italic">No activity yet. First payment or API call will show here.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-zinc-500 uppercase text-[10px] tracking-wide">
                    <th className="text-left py-2">Kind</th>
                    <th className="text-right py-2">Amount</th>
                    <th className="text-left py-2 pl-3">Description</th>
                    <th className="text-right py-2">When</th>
                  </tr>
                </thead>
                <tbody>
                  {log.slice(0, 40).map((row, i) => (
                    <tr key={i} className="border-t border-white/5">
                      <td className={`py-1.5 font-bold ${kindColor[row.kind] || 'text-zinc-400'}`}>{row.kind}</td>
                      <td className="py-1.5 text-right font-mono">{fmt$(row.amount_usd)}</td>
                      <td className="py-1.5 pl-3 text-zinc-400 truncate max-w-xs">
                        {row.metadata?.description || row.metadata?.provider || row.metadata?.plan_id || ''}
                      </td>
                      <td className="py-1.5 text-right text-zinc-500 text-[10px] whitespace-nowrap">
                        {row.ts ? new Date(row.ts).toLocaleString() : ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};


export default UniversalGatewayTab;
