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
  Wallet, CreditCard, ArrowUpRight, Percent
} from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";
import { useAuth } from "../../../App";

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
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedLog, setExpandedLog] = useState(null);
  const [activeSection, setActiveSection] = useState("overview");
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

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    try {
      const [statsRes, logsRes, healthRes, keysRes] = await Promise.all([
        fetch(`${API}/admin/gateway/stats`, { headers }),
        fetch(`${API}/admin/gateway/logs?limit=50`, { headers }),
        fetch(`${API}/admin/gateway/health`, { headers }),
        fetch(`${API}/admin/gateway/client-keys`, { headers }),
      ]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (logsRes.ok) { const d = await logsRes.json(); setLogs(d.logs || []); }
      if (healthRes.ok) setHealth(await healthRes.json());
      if (keysRes.ok) setClientKeys(await keysRes.json());
    } catch { toast.error("Failed to load gateway data"); }
    finally { setLoading(false); setRefreshing(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

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
    { id: "playground",  label: "Playground",       icon: Play },
    { id: "compare",     label: "Compare Models",   icon: GitCompare },
    { id: "clients",     label: "Client Keys",      icon: Key },
    { id: "webhooks",    label: "Webhooks",         icon: Webhook },
    { id: "sdk",         label: "API Reference",    icon: Shield },
    { id: "providers",   label: "Provider Health",  icon: Network },
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

      {/* Sub-nav */}
      <div className="flex gap-1 bg-zinc-900/50 p-1 rounded-lg border border-white/10 overflow-x-auto">
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => setActiveSection(s.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all whitespace-nowrap ${
              activeSection === s.id
                ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
                : "text-zinc-400 hover:text-white hover:bg-white/5"
            }`}
          >
            <s.icon className="w-4 h-4" />
            {s.label}
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

      {/* ── PROVIDER HEALTH ── */}
      {activeSection === "providers" && health && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {health.providers?.map(p => (
              <Card key={p.id} className={`border ${
                p.is_active ? "bg-zinc-900/50 border-white/10" : "bg-zinc-950/50 border-red-500/20"
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${p.is_active ? "bg-emerald-400" : "bg-red-400"}`} />
                      <span className={`text-sm font-medium ${PROVIDER_COLORS[p.id] || "text-zinc-300"}`}>
                        {p.name}
                      </span>
                    </div>
                    <Badge className={
                      p.key_source === "direct"   ? "bg-emerald-500/20 text-emerald-300 text-[10px]" :
                      p.key_source === "emergent" ? "bg-blue-500/20 text-blue-300 text-[10px]" :
                      "bg-red-500/20 text-red-300 text-[10px]"
                    }>
                      {p.key_source === "direct" ? "Direct Key" :
                       p.key_source === "emergent" ? "MAARS Key" : "No Key"}
                    </Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {p.models?.slice(0, 2).map(m => (
                      <span key={m} className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">{m}</span>
                    ))}
                  </div>
                  <div className="mt-2 flex items-center gap-1">
                    {p.is_active
                      ? <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      : <XCircle className="w-3 h-3 text-red-400" />}
                    <span className={`text-[11px] ${p.is_active ? "text-emerald-400" : "text-red-400"}`}>
                      {p.is_active ? "Ready to route" : "No API key — configure in API Keys tab"}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <p className="text-xs text-zinc-500">
            Configure API keys in the <strong className="text-zinc-400">API Keys & Integrations</strong> tab.
            Providers without a direct key will use the MAARS universal key if configured (OpenAI, Anthropic, Gemini only).
          </p>
        </div>
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

export default UniversalGatewayTab;
