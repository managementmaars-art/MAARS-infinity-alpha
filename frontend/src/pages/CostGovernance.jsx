import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { DollarSign, TrendingUp, BarChart3, AlertTriangle, Bot, Cpu, Settings, Layers } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

export default function CostGovernance() {
  const { token } = useAuth();
  const [overview, setOverview] = useState({ total_cost: 0, total_executions: 0, avg_cost: 0, max_cost: 0 });
  const [byModel, setByModel] = useState([]);
  const [byAgent, setByAgent] = useState([]);
  const [byProvider, setByProvider] = useState([]);
  const [budget, setBudget] = useState({ monthly_limit: 100, daily_limit: 10, alert_threshold: 0.8, auto_pause: false });
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editBudget, setEditBudget] = useState(false);

  useEffect(() => {
    const h = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch(`${API}/api/kernel/cost/overview`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/cost/by-model`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/cost/by-agent`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/cost/budget`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/agents`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/cost/by-provider`, { headers: h }).then(r => r.json()),
    ]).then(([ov, bm, ba, bg, ag, bp]) => {
      setOverview(ov); setByModel(Array.isArray(bm) ? bm : []);
      setByAgent(Array.isArray(ba) ? ba : []); setBudget(bg);
      setAgents(Array.isArray(ag) ? ag : []); setByProvider(Array.isArray(bp) ? bp : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const getAgent = (id) => agents.find(a => a.agent_id === id);
  const budgetUsed = budget.monthly_limit > 0 ? (overview.total_cost / budget.monthly_limit) * 100 : 0;
  const isAlert = budgetUsed >= budget.alert_threshold * 100;

  const saveBudget = async () => {
    const res = await fetch(`${API}/api/kernel/cost/budget`, {
      method: "PUT", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(budget),
    });
    if (res.ok) { setBudget(await res.json()); setEditBudget(false); }
  };

  const fmtTokens = (n) => n >= 1000 ? `${(n / 1000).toFixed(1)}K` : String(n);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="cost-governance">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Cost Governance</h1>
          <p className="text-sm text-zinc-400 mt-1">Monitor, control, and optimize AI execution costs across the system</p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="cost-overview">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><DollarSign className="w-4 h-4 text-emerald-400" /><span className="text-xs text-zinc-500">Total Spend</span></div>
          <p className="text-2xl font-bold text-white">${overview.total_cost.toFixed(4)}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><BarChart3 className="w-4 h-4 text-indigo-400" /><span className="text-xs text-zinc-500">Total Operations</span></div>
          <p className="text-2xl font-bold text-white">{overview.total_executions}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><TrendingUp className="w-4 h-4 text-cyan-400" /><span className="text-xs text-zinc-500">Avg Cost/Op</span></div>
          <p className="text-2xl font-bold text-white">${overview.avg_cost.toFixed(6)}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle className="w-4 h-4 text-amber-400" /><span className="text-xs text-zinc-500">Max Single Op</span></div>
          <p className="text-2xl font-bold text-white">${overview.max_cost.toFixed(6)}</p>
        </div>
      </div>

      {/* Budget Bar */}
      <div className={`bg-zinc-900/40 border rounded-xl p-4 ${isAlert ? "border-amber-500/30" : "border-white/5"}`} data-testid="budget-bar">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">Monthly Budget</span>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-bold ${isAlert ? "text-amber-400" : "text-emerald-400"}`}>
              ${overview.total_cost.toFixed(2)} / ${budget.monthly_limit.toFixed(2)}
            </span>
            <Button size="sm" variant="outline" className="h-6 text-[10px] border-white/10" onClick={() => setEditBudget(!editBudget)}>
              <Settings className="w-3 h-3 mr-1" /> {editBudget ? "Cancel" : "Configure"}
            </Button>
          </div>
        </div>
        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all ${isAlert ? "bg-amber-500" : "bg-emerald-500"}`} style={{ width: `${Math.min(budgetUsed, 100)}%` }} />
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-[10px] text-zinc-600">{budgetUsed.toFixed(1)}% used</span>
          <span className="text-[10px] text-zinc-600">Alert at {(budget.alert_threshold * 100).toFixed(0)}%</span>
        </div>
        {editBudget && (
          <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-2 gap-3" data-testid="budget-edit">
            <div>
              <label className="text-[10px] text-zinc-500 block mb-1">Monthly Limit ($)</label>
              <input type="number" value={budget.monthly_limit} onChange={e => setBudget(p => ({ ...p, monthly_limit: parseFloat(e.target.value) || 0 }))}
                className="w-full bg-zinc-900 border border-white/10 rounded px-2 py-1.5 text-xs text-white" />
            </div>
            <div>
              <label className="text-[10px] text-zinc-500 block mb-1">Daily Limit ($)</label>
              <input type="number" value={budget.daily_limit} onChange={e => setBudget(p => ({ ...p, daily_limit: parseFloat(e.target.value) || 0 }))}
                className="w-full bg-zinc-900 border border-white/10 rounded px-2 py-1.5 text-xs text-white" />
            </div>
            <div>
              <label className="text-[10px] text-zinc-500 block mb-1">Alert Threshold (%)</label>
              <input type="number" min="0" max="100" value={budget.alert_threshold * 100} onChange={e => setBudget(p => ({ ...p, alert_threshold: (parseFloat(e.target.value) || 80) / 100 }))}
                className="w-full bg-zinc-900 border border-white/10 rounded px-2 py-1.5 text-xs text-white" />
            </div>
            <div className="flex items-end">
              <Button size="sm" className="w-full h-8 text-xs bg-indigo-600 hover:bg-indigo-700" onClick={saveBudget} data-testid="save-budget">Save Budget</Button>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Cost by Model */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4" data-testid="cost-by-model">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Cpu className="w-4 h-4 text-zinc-500" /> Cost By Model</h3>
          {byModel.length === 0 ? (
            <p className="text-xs text-zinc-600 text-center py-6">No model cost data yet. Interact with agents to generate cost data.</p>
          ) : (
            <div className="space-y-2">
              {byModel.map((m, i) => {
                const maxCost = byModel[0]?.total_cost || 1;
                return (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-[11px] text-zinc-400 w-44 truncate font-mono">{m.model}</span>
                    <span className="text-[10px] text-zinc-600 w-14 text-right">{m.count} calls</span>
                    <span className="text-[11px] text-rose-400 font-semibold w-16 text-right font-mono">${m.total_cost.toFixed(4)}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Cost by Provider */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4" data-testid="cost-by-provider">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Layers className="w-4 h-4 text-zinc-500" /> Cost By Provider</h3>
          {byProvider.length === 0 ? (
            <p className="text-xs text-zinc-600 text-center py-6">No provider cost data yet. Interact with agents to generate cost data.</p>
          ) : (
            <div className="space-y-4">
              {byProvider.map((p, i) => (
                <div key={i} className="pb-3 border-b border-white/5 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-base font-semibold text-white">{p.provider}</span>
                    <span className="text-base font-bold text-rose-400 font-mono">${p.total_cost.toFixed(4)}</span>
                  </div>
                  <span className="text-[10px] text-zinc-500">
                    {p.count} calls{p.input_tokens > 0 && <>&nbsp;&nbsp;&nbsp;{fmtTokens(p.input_tokens)} input</>}{p.output_tokens > 0 && <>&nbsp;&nbsp;&nbsp;{fmtTokens(p.output_tokens)} output</>}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Cost by Agent */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4" data-testid="cost-by-agent">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Bot className="w-4 h-4 text-zinc-500" /> Cost By Agent</h3>
        {byAgent.length === 0 ? (
          <p className="text-xs text-zinc-600 text-center py-6">No agent cost data yet. Chat with agents to generate cost data.</p>
        ) : (
          <div className="space-y-2">
            {byAgent.slice(0, 15).map((a, i) => {
              const agent = getAgent(a.agent_id);
              const maxCost = byAgent[0]?.total_cost || 1;
              return (
                <div key={i} className="flex items-center gap-3">
                  {agent?.avatar ? (
                    <img src={agent.avatar} alt="" className="w-5 h-5 rounded object-cover" />
                  ) : (
                    <div className="w-5 h-5 rounded bg-zinc-700 flex items-center justify-center text-[7px] font-bold text-zinc-400">
                      {(agent?.name || a.agent_id).slice(0, 2).toUpperCase()}
                    </div>
                  )}
                  <span className="text-[11px] text-zinc-400 w-28 truncate">{agent?.name || a.agent_id}</span>
                  <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(a.total_cost / maxCost) * 100}%` }} />
                  </div>
                  <span className="text-[11px] text-zinc-300 w-20 text-right">${a.total_cost.toFixed(4)}</span>
                  <span className="text-[9px] text-zinc-600 w-12 text-right">{a.count} ops</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
