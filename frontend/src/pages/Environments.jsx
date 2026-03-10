import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Globe, Shield, Zap, Check, Users, Lock, AlertTriangle, ArrowRight } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

const ENV_ICONS = { sandbox: AlertTriangle, staging: Shield, production: Zap };
const ENV_BG = { sandbox: "bg-amber-500/10", staging: "bg-blue-500/10", production: "bg-emerald-500/10" };

export default function Environments() {
  const { token } = useAuth();
  const [data, setData] = useState({ environments: {}, active: "sandbox", stats: {} });
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  const fetchData = () => {
    fetch(`${API}/api/kernel/environments`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [token]);

  const switchEnv = async (env) => {
    setSwitching(true);
    const res = await fetch(`${API}/api/kernel/environments/active`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ environment: env }),
    });
    if (res.ok) {
      setData(prev => ({ ...prev, active: env }));
    }
    setSwitching(false);
  };

  const envs = data.environments || {};
  const active = data.active;
  const stats = data.stats || {};

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="environments-page">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Environment Segregation</h1>
        <p className="text-sm text-zinc-400 mt-1">Manage execution environments — sandbox for testing, staging for validation, production for live operations</p>
      </div>

      {/* Active Environment Banner */}
      <div className={`rounded-xl border p-5 ${active === "production" ? "border-emerald-500/20 bg-emerald-500/5" : active === "staging" ? "border-blue-500/20 bg-blue-500/5" : "border-amber-500/20 bg-amber-500/5"}`} data-testid="active-env-banner">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full animate-pulse ${active === "production" ? "bg-emerald-500" : active === "staging" ? "bg-blue-500" : "bg-amber-500"}`} />
          <div>
            <p className="text-sm font-medium text-white">Active Environment: <span className="font-bold">{envs[active]?.name || active}</span></p>
            <p className="text-xs text-zinc-400 mt-0.5">{envs[active]?.description}</p>
          </div>
        </div>
      </div>

      {/* Environment Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="env-cards">
        {Object.entries(envs).map(([key, env]) => {
          const isActive = key === active;
          const Icon = ENV_ICONS[key] || Globe;
          const limits = env.limits || {};
          return (
            <div key={key} className={`rounded-xl border p-5 transition-all ${isActive ? "border-white/15 bg-zinc-900/60 ring-1 ring-white/5" : "border-white/5 bg-zinc-900/30 hover:border-white/10"}`}
              data-testid={`env-card-${key}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-xl ${ENV_BG[key] || "bg-zinc-800"} flex items-center justify-center`}>
                  <Icon className="w-5 h-5" style={{ color: env.color }} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{env.name}</p>
                  <p className="text-[10px] text-zinc-500">{stats[key]?.users || 0} active users</p>
                </div>
                {isActive && <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-white font-medium flex items-center gap-1"><Check className="w-3 h-3" /> Active</span>}
              </div>

              <p className="text-xs text-zinc-400 mb-4">{env.description}</p>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-zinc-500">Max Agents</span>
                  <span className="text-white font-medium">{limits.max_agents}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-zinc-500">Max Cost/Run</span>
                  <span className="text-white font-medium">${limits.max_cost_per_run?.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-zinc-500">Real Actions</span>
                  <span className={`font-medium ${limits.real_actions ? "text-emerald-400" : "text-amber-400"}`}>
                    {limits.real_actions ? "Enabled" : "Dry Run Only"}
                  </span>
                </div>
              </div>

              {!isActive && (
                <Button size="sm" className="w-full h-8 text-xs" style={{ backgroundColor: env.color }}
                  onClick={() => switchEnv(key)} disabled={switching} data-testid={`switch-to-${key}`}>
                  <ArrowRight className="w-3 h-3 mr-1" /> Switch to {env.name}
                </Button>
              )}
            </div>
          );
        })}
      </div>

      {/* Environment Comparison */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-5" data-testid="env-comparison">
        <h3 className="text-sm font-semibold text-white mb-4">Environment Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px]">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left text-zinc-500 pb-2 pr-4">Feature</th>
                {Object.entries(envs).map(([key, env]) => (
                  <th key={key} className="text-center pb-2 px-4" style={{ color: env.color }}>{env.name}</th>
                ))}
              </tr>
            </thead>
            <tbody className="text-zinc-300">
              {[
                { label: "Agent Limit", fn: (l) => l.max_agents },
                { label: "Cost Limit", fn: (l) => `$${l.max_cost_per_run?.toFixed(2)}` },
                { label: "Real Actions", fn: (l) => l.real_actions ? "Yes" : "No" },
                { label: "Data Persistence", fn: (_, k) => k === "sandbox" ? "Session" : k === "staging" ? "7 days" : "Permanent" },
                { label: "Audit Logging", fn: (_, k) => k === "sandbox" ? "Basic" : k === "staging" ? "Full" : "Full + Compliance" },
                { label: "Integrations", fn: (_, k) => k === "sandbox" ? "Mocked" : k === "staging" ? "Limited" : "All Active" },
              ].map((row, i) => (
                <tr key={i} className="border-b border-white/[0.03]">
                  <td className="py-2 pr-4 text-zinc-500">{row.label}</td>
                  {Object.entries(envs).map(([key, env]) => (
                    <td key={key} className="py-2 px-4 text-center">{row.fn(env.limits || {}, key)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
