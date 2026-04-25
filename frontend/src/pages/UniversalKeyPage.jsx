import { useState, useEffect, useCallback, useMemo } from "react";
import { useAuth } from "../App";
import {
  Key, Zap, DollarSign, TrendingUp, CreditCard, ArrowRight, Check,
  Copy, Eye, EyeOff, RefreshCw, BarChart3, Activity, Cpu, Shield,
  Clock, Loader2, ChevronRight, Info, Sparkles, Globe, Lock
} from "lucide-react";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const MODEL_ALLOCATION = 65;   // % to AI costs
const PROFIT_ALLOCATION = 35;  // % platform profit

export default function UniversalKeyPage() {
  const { token } = useAuth();
  const [keyStatus, setKeyStatus] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [topupAmount, setTopupAmount] = useState(25);
  const [currency, setCurrency] = useState("usd");
  const [topping, setTopping] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [activeSection, setActiveSection] = useState("overview");

  const h = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const fetchAll = useCallback(async () => {
    try {
      const [keyRes, pricingRes, txRes, statsRes] = await Promise.all([
        fetch(`${API}/api/universal/key/status`, { headers: h }),
        fetch(`${API}/api/universal/key/pricing`, { headers: h }),
        fetch(`${API}/api/universal/key/transactions`, { headers: h }),
        fetch(`${API}/api/universal/stats`, { headers: h }),
      ]);
      if (keyRes.ok) setKeyStatus(await keyRes.json());
      if (pricingRes.ok) setPricing(await pricingRes.json());
      if (txRes.ok) setTransactions((await txRes.json()).transactions || []);
      if (statsRes.ok) setStats(await statsRes.json());
    } catch {}
    setLoading(false);
  }, [h]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleTopup = async () => {
    if (topupAmount < 5) { toast.error("Minimum top-up is $5"); return; }
    setTopping(true);
    try {
      const res = await fetch(`${API}/api/universal/key/topup`, {
        method: "POST", headers: h,
        body: JSON.stringify({ amount_usd: topupAmount, currency }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`${data.credits_issued} credits added!`);
        fetchAll();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Top-up failed");
      }
    } catch { toast.error("Top-up failed"); }
    setTopping(false);
  };

  const copyKey = () => {
    navigator.clipboard.writeText(keyStatus?.masked_key || "");
    toast.success("Key copied");
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const aiAlloc = Math.round(topupAmount * MODEL_ALLOCATION / 100 * 100) / 100;
  const profitAlloc = Math.round(topupAmount * PROFIT_ALLOCATION / 100 * 100) / 100;
  const creditsPreview = Math.round(aiAlloc * (pricing?.credits_per_ai_dollar || 16.67));

  return (
    <div className="space-y-5 max-w-6xl mx-auto" data-testid="universal-key-page">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <Key className="w-6 h-6 text-teal-400" />
            Universal Gateway Key
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Pay-as-you-go access to 33 AI providers, 600+ models via a single key.
            65% goes to AI costs, 35% covers platform infrastructure.
          </p>
        </div>
        <button onClick={fetchAll} className="p-2 rounded-lg border border-white/10 text-zinc-500 hover:text-white transition-colors">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Key status card */}
      <div className="relative overflow-hidden rounded-2xl border border-teal-500/20"
        style={{ background: "linear-gradient(135deg, rgba(79,209,197,0.06) 0%, rgba(6,182,212,0.04) 50%, rgba(124,58,237,0.05) 100%)" }}>
        {/* Animated glow */}
        <div style={{ position: "absolute", top: -40, right: -40, width: 200, height: 200, background: "radial-gradient(circle, rgba(79,209,197,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />

        <div className="p-6 relative">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* Key */}
            <div className="sm:col-span-2">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">Your Universal Key</p>
              <div className="flex items-center gap-2 p-3 bg-zinc-900/60 rounded-xl border border-white/8">
                <Key className="w-4 h-4 text-teal-400 shrink-0" />
                <span className="font-mono text-xs text-zinc-300 flex-1 truncate">
                  {showKey ? (keyStatus?.key_id || "maars-sk-xxxxxxxxxxxxxxxxxxxxxxxx") : (keyStatus?.masked_key || "maars-sk-••••••••••••••••••••••••")}
                </span>
                <button onClick={() => setShowKey(!showKey)} className="text-zinc-600 hover:text-zinc-400">
                  {showKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
                <button onClick={copyKey} className="text-zinc-600 hover:text-teal-400">
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${keyStatus?.status === "active" ? "bg-emerald-400" : "bg-red-400"}`}
                  style={{ animation: keyStatus?.status === "active" ? "neural-pulse-green 2s ease-in-out infinite" : "none" }} />
                <span className="text-xs text-zinc-500">
                  {keyStatus?.status === "active" ? "Active" : "Depleted"} · Plan: <span className="text-white capitalize">{keyStatus?.plan || "Free"}</span>
                </span>
              </div>
            </div>

            {/* Credits */}
            <div>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">Credits Remaining</p>
              <p className="text-3xl font-bold text-white">{(keyStatus?.credits_remaining || 0).toLocaleString()}</p>
              <p className="text-xs text-zinc-600 mt-1">≈ ${((keyStatus?.credits_remaining || 0) / (pricing?.credits_per_ai_dollar || 16.67)).toFixed(2)} AI budget</p>
            </div>

            {/* Budget */}
            <div>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">AI Budget Used</p>
              <p className="text-3xl font-bold text-white">${(keyStatus?.budget_usd_used || 0).toFixed(2)}</p>
              <p className="text-xs text-zinc-600 mt-1">of ${(keyStatus?.budget_usd_total || 0).toFixed(2)} total</p>
              {keyStatus?.budget_usd_total > 0 && (
                <div className="mt-1.5 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full transition-all"
                    style={{ width: `${Math.min(keyStatus.utilization_pct, 100)}%` }} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Section tabs */}
      <div className="flex gap-1 bg-zinc-900/50 border border-white/5 rounded-xl p-1">
        {[
          { key: "overview", label: "Top Up", icon: CreditCard },
          { key: "how", label: "How It Works", icon: Info },
          { key: "history", label: "Transaction History", icon: Clock },
          { key: "usage", label: "Usage Stats", icon: BarChart3 },
        ].map(s => {
          const Icon = s.icon;
          return (
            <button key={s.key} onClick={() => setActiveSection(s.key)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all flex-1 justify-center ${
                activeSection === s.key ? "bg-teal-500/15 text-teal-400 border border-teal-500/25" : "text-zinc-500 hover:text-white"
              }`}>
              <Icon className="w-3.5 h-3.5" />{s.label}
            </button>
          );
        })}
      </div>

      {/* Top Up Section */}
      {activeSection === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Top-up form */}
          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-5 space-y-4">
            <p className="text-sm font-semibold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-teal-400" />Add Credits — Pay As You Go
            </p>

            {/* Amount selector */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs text-zinc-400">Amount</label>
                <select value={currency} onChange={e => setCurrency(e.target.value)}
                  className="bg-zinc-900/60 border border-white/8 rounded px-2 py-1 text-xs text-white focus:outline-none">
                  <option value="usd">USD ($)</option>
                  <option value="bdt">BDT (৳)</option>
                </select>
              </div>

              {/* Quick amounts */}
              <div className="grid grid-cols-4 gap-2 mb-3">
                {[10, 25, 50, 100].map(amt => (
                  <button key={amt}
                    onClick={() => setTopupAmount(amt)}
                    className={`py-2 rounded-lg text-xs font-medium border transition-all ${topupAmount === amt ? "bg-teal-500/20 border-teal-500/40 text-teal-400" : "border-white/10 text-zinc-500 hover:text-white"}`}>
                    ${amt}
                  </button>
                ))}
              </div>

              {/* Custom amount */}
              <div className="flex items-center gap-2 p-3 bg-zinc-900/60 border border-white/8 rounded-xl">
                <span className="text-zinc-500 text-sm">{currency === "usd" ? "$" : "৳"}</span>
                <input
                  type="number" min={5} max={10000}
                  value={topupAmount}
                  onChange={e => setTopupAmount(Number(e.target.value))}
                  className="flex-1 bg-transparent text-xl font-bold text-white focus:outline-none"
                  data-testid="topup-amount"
                />
                <span className="text-zinc-600 text-xs">{currency.toUpperCase()}</span>
              </div>
            </div>

            {/* Allocation breakdown */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-white/5 space-y-3">
              <p className="text-[10px] text-zinc-500 font-semibold uppercase tracking-wider">How Your Payment Is Allocated</p>

              <div className="relative h-3 bg-zinc-800 rounded-full overflow-hidden">
                <div className="absolute left-0 top-0 h-full rounded-l-full" style={{ width: `${MODEL_ALLOCATION}%`, background: "linear-gradient(90deg, #4fd1c5, #06b6d4)" }} />
                <div className="absolute right-0 top-0 h-full rounded-r-full" style={{ width: `${PROFIT_ALLOCATION}%`, background: "linear-gradient(90deg, #7c3aed, #a855f7)" }} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 rounded-lg" style={{ background: "rgba(79,209,197,0.08)", border: "1px solid rgba(79,209,197,0.15)" }}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <Cpu className="w-3 h-3 text-teal-400" />
                    <span className="text-[9px] text-zinc-400 uppercase font-semibold">AI Model Budget</span>
                  </div>
                  <p className="text-lg font-bold text-teal-400">${aiAlloc.toFixed(2)}</p>
                  <p className="text-[9px] text-zinc-600">{MODEL_ALLOCATION}% of payment</p>
                  <p className="text-[9px] text-teal-300/70 mt-0.5">= {creditsPreview} credits</p>
                </div>
                <div className="p-2.5 rounded-lg" style={{ background: "rgba(124,58,237,0.08)", border: "1px solid rgba(124,58,237,0.15)" }}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <Shield className="w-3 h-3 text-violet-400" />
                    <span className="text-[9px] text-zinc-400 uppercase font-semibold">Platform & Ops</span>
                  </div>
                  <p className="text-lg font-bold text-violet-400">${profitAlloc.toFixed(2)}</p>
                  <p className="text-[9px] text-zinc-600">{PROFIT_ALLOCATION}% of payment</p>
                  <p className="text-[9px] text-zinc-600 mt-0.5">Infra, routing, support</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-xs text-zinc-500">Credits you receive:</span>
                <span className="text-sm font-bold text-white">{creditsPreview.toLocaleString()} credits</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500">Cost per credit:</span>
                <span className="text-xs text-zinc-300">${(topupAmount / Math.max(creditsPreview, 1)).toFixed(4)}</span>
              </div>
            </div>

            <button
              onClick={handleTopup}
              disabled={topping || topupAmount < 5}
              className="w-full py-3 rounded-xl text-sm font-semibold text-black disabled:opacity-40 transition-all"
              style={{ background: "linear-gradient(135deg, #4fd1c5 0%, #06b6d4 50%, #7c3aed 100%)" }}
              data-testid="topup-btn">
              {topping
                ? <><Loader2 className="w-4 h-4 animate-spin inline mr-2" />Processing...</>
                : <><Zap className="w-4 h-4 inline mr-2" />Top Up ${topupAmount} → {creditsPreview.toLocaleString()} Credits</>
              }
            </button>

            <p className="text-[10px] text-zinc-600 text-center">
              Secure payment via Stripe. Credits expire when subscription ends.
            </p>
          </div>

          {/* Pricing table */}
          <div className="space-y-4">
            <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
              <p className="text-xs font-semibold text-zinc-400 mb-3">Example Allocations</p>
              <div className="space-y-2">
                {(pricing?.examples || []).map((ex, i) => (
                  <div key={i}
                    className="flex items-center gap-3 py-2 border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/2 rounded px-1 transition-colors"
                    onClick={() => setTopupAmount(ex.amount_usd)}>
                    <div className="w-12 text-xs font-bold text-white">${ex.amount_usd}</div>
                    <div className="flex-1">
                      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                        <div className="h-full rounded-l-full" style={{ width: `${MODEL_ALLOCATION}%`, background: "linear-gradient(90deg, #4fd1c5, #06b6d4)" }} />
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-semibold text-teal-400">{ex.credits_issued.toLocaleString()} credits</p>
                      <p className="text-[9px] text-zinc-600">${ex.ai_budget_usd} AI budget</p>
                    </div>
                    <ChevronRight className="w-3 h-3 text-zinc-700" />
                  </div>
                ))}
              </div>
            </div>

            {/* Provider coverage */}
            <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
              <p className="text-xs font-semibold text-zinc-400 mb-3 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5" />One Key, Every Provider
              </p>
              <div className="grid grid-cols-3 gap-1.5">
                {["OpenAI","Anthropic","Google","xAI","DeepSeek","Mistral","Perplexity","Cohere","Groq","Cerebras","Together","Fireworks","NVIDIA","Moonshot","Qwen","Novita","Lepton","Lambda","Minimax","Inception","Arcee","AI21","SambaNova","Amazon","ElevenLabs"].map(p => (
                  <div key={p} className="text-[9px] text-zinc-500 bg-zinc-800/40 rounded px-2 py-1 text-center">{p}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* How It Works */}
      {activeSection === "how" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              step: "01", icon: CreditCard, color: "#4fd1c5", title: "You Pay a Top-Up Amount",
              desc: "Choose any amount from $5 to $10,000. Pay via Stripe (card, bank, or any major payment method).",
            },
            {
              step: "02", icon: Cpu, color: "#06b6d4", title: "65% Goes to AI Model Budget",
              desc: `${MODEL_ALLOCATION}% of your payment is allocated as AI model budget — used to pay OpenAI, Anthropic, Google, and 30 other providers for actual LLM API calls made by your agents.`,
            },
            {
              step: "03", icon: Shield, color: "#7c3aed", title: "35% Covers Platform",
              desc: `${PROFIT_ALLOCATION}% covers infrastructure costs: routing layer, failover logic, monitoring, logging, support, and platform development.`,
            },
            {
              step: "04", icon: Zap, color: "#f59e0b", title: "Credits Issued to Your Account",
              desc: "Your AI budget is converted to MAARS credits. Each credit ≈ one LLM API call. Economy models use fewer credits; premium models use more.",
            },
            {
              step: "05", icon: Activity, color: "#10b981", title: "Smart Router Picks the Best Model",
              desc: "Every request is auto-routed to the best model for the task. Code → GPT-4.1 or DeepSeek V3. Math → O4-mini. Research → Perplexity Deep Research.",
            },
            {
              step: "06", icon: TrendingUp, color: "#ec4899", title: "Real-Time Budget Tracking",
              desc: "Watch your AI budget and credit balance update in real-time. Get notified when balance is low. Top up anytime — no subscriptions required.",
            },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="flex gap-4 p-4 bg-zinc-900/40 border border-white/5 rounded-xl">
                <div className="shrink-0">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${item.color}15` }}>
                    <Icon className="w-5 h-5" style={{ color: item.color }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[9px] font-bold text-zinc-600">{item.step}</span>
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                  </div>
                  <p className="text-xs text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Transaction History */}
      {activeSection === "history" && (
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl">
          <div className="p-4 border-b border-white/5 flex items-center justify-between">
            <p className="text-sm font-semibold text-white">Pay-As-You-Go History</p>
            <div className="text-right">
              <p className="text-xs text-zinc-500">Total paid</p>
              <p className="text-sm font-bold text-teal-400">${transactions.reduce((s, t) => s + (t.amount_usd || 0), 0).toFixed(2)}</p>
            </div>
          </div>
          {transactions.length === 0 ? (
            <div className="text-center py-12 text-zinc-600">
              <CreditCard className="w-8 h-8 mx-auto mb-2 opacity-40" />
              <p className="text-sm">No top-ups yet</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {transactions.map((tx, i) => (
                <div key={i} className="flex items-center gap-4 px-4 py-3" data-testid={`tx-${tx.transaction_id}`}>
                  <div className="w-9 h-9 rounded-xl bg-teal-500/10 flex items-center justify-center shrink-0">
                    <Zap className="w-4 h-4 text-teal-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white">Top-Up — {tx.credits_issued?.toLocaleString()} credits</p>
                    <p className="text-[10px] text-zinc-600 font-mono">{tx.transaction_id}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-bold text-white">${tx.amount_usd?.toFixed(2)}</p>
                    <p className="text-[9px] text-zinc-600">{tx.created_at?.slice(0, 10)}</p>
                  </div>
                  <div className="text-right shrink-0 hidden sm:block">
                    <p className="text-[9px] text-teal-400">AI: ${tx.ai_budget_usd?.toFixed(2)}</p>
                    <p className="text-[9px] text-zinc-600">Platform: ${tx.profit_usd?.toFixed(2)}</p>
                  </div>
                  <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400">{tx.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Usage Stats */}
      {activeSection === "usage" && stats && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {[
              { label: "Total API Calls", value: stats.total_calls?.toLocaleString(), icon: Activity, color: "#4fd1c5" },
              { label: "Credits Used", value: stats.total_credits_used?.toLocaleString(), icon: Zap, color: "#f59e0b" },
              { label: "USD Cost", value: `$${stats.total_cost_usd?.toFixed(4)}`, icon: DollarSign, color: "#10b981" },
              { label: "Fallback Rate", value: `${stats.fallback_rate_pct}%`, icon: RefreshCw, color: "#8b5cf6" },
              { label: "Avg Cost/Call", value: `$${stats.avg_cost_per_call_usd?.toFixed(6)}`, icon: TrendingUp, color: "#ec4899" },
            ].map((s, i) => {
              const Icon = s.icon;
              return (
                <div key={i} className="bg-zinc-900/40 border border-white/5 rounded-xl p-3">
                  <Icon className="w-4 h-4 mb-2" style={{ color: s.color }} />
                  <p className="text-xs text-zinc-500">{s.label}</p>
                  <p className="text-lg font-bold text-white mt-0.5">{s.value}</p>
                </div>
              );
            })}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
              <p className="text-xs font-semibold text-zinc-400 mb-3">Calls by Task Type</p>
              {Object.entries(stats.calls_by_task_type || {}).sort(([,a],[,b]) => b-a).map(([task, count]) => (
                <div key={task} className="flex items-center gap-3 py-1.5 border-b border-white/5 last:border-0">
                  <span className="text-xs text-zinc-400 w-24 capitalize">{task}</span>
                  <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full"
                      style={{ width: `${Math.round(count / Math.max(stats.total_calls, 1) * 100)}%` }} />
                  </div>
                  <span className="text-xs text-zinc-500 w-8 text-right">{count}</span>
                </div>
              ))}
            </div>

            <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
              <p className="text-xs font-semibold text-zinc-400 mb-3">Calls by Provider</p>
              {Object.entries(stats.calls_by_provider || {}).sort(([,a],[,b]) => b-a).slice(0, 8).map(([provider, count]) => (
                <div key={provider} className="flex items-center gap-3 py-1.5 border-b border-white/5 last:border-0">
                  <span className="text-xs text-zinc-400 w-24 capitalize">{provider}</span>
                  <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full"
                      style={{ width: `${Math.round(count / Math.max(stats.total_calls, 1) * 100)}%` }} />
                  </div>
                  <span className="text-xs text-zinc-500 w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
