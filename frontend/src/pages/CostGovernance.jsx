import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { DollarSign, TrendingUp, BarChart3, AlertTriangle, Bot, Cpu, Settings, Layers } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  blue: "#60a5fa",
  indigo: "#818cf8",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const PROVIDER_ACCENT = {
  openai: "#10b981", anthropic: "#f97316", google: "#3b82f6",
  deepseek: T.teal, mistral: "#ff7000", groq: "#f55036",
  xai: "#94a3b8", perplexity: "#8b5cf6",
};

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "6px 10px", color: "#fff", fontSize: 12,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
};

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
  const glassCard = { position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px", overflow: "hidden" };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.amber}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="cost-governance">
      <style>{STYLES}</style>

      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Cost Governance</h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Monitor, control, and optimize AI execution costs across the system</p>
      </div>

      {/* Overview Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }} data-testid="cost-overview">
        {[
          { icon: DollarSign, label: "Total Spend", value: `$${overview.total_cost.toFixed(4)}`, accent: T.green },
          { icon: BarChart3, label: "Total Operations", value: overview.total_executions, accent: T.indigo },
          { icon: TrendingUp, label: "Avg Cost/Op", value: `$${overview.avg_cost.toFixed(6)}`, accent: T.cyan },
          { icon: AlertTriangle, label: "Max Single Op", value: `$${overview.max_cost.toFixed(6)}`, accent: T.amber },
        ].map(c => (
          <div key={c.label} style={{ ...glassCard }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: c.accent }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <c.icon size={14} style={{ color: c.accent }} />
              <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em" }}>{c.label}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, color: "#fff" }}>{c.value}</div>
          </div>
        ))}
      </div>

      {/* Budget Bar */}
      <div style={{ background: isAlert ? "rgba(245,158,11,.05)" : T.glass, border: `1px solid ${isAlert ? "rgba(245,158,11,.3)" : T.border}`, borderRadius: 14, padding: "16px 20px" }} data-testid="budget-bar">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>Monthly Budget</span>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: isAlert ? T.amber : T.green }}>
              ${overview.total_cost.toFixed(2)} / ${budget.monthly_limit.toFixed(2)}
            </span>
            <button
              onClick={() => setEditBudget(!editBudget)}
              style={{ display: "flex", alignItems: "center", gap: 5, padding: "4px 10px", borderRadius: 8, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 10, fontWeight: 600, cursor: "pointer" }}
            >
              <Settings size={11} /> {editBudget ? "Cancel" : "Configure"}
            </button>
          </div>
        </div>
        <div style={{ height: 6, background: "rgba(255,255,255,.06)", borderRadius: 6, overflow: "hidden", marginBottom: 6 }}>
          <div style={{ height: "100%", borderRadius: 6, background: isAlert ? T.amber : T.green, width: `${Math.min(budgetUsed, 100)}%`, transition: "width .6s" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: T.zinc }}>
          <span>{budgetUsed.toFixed(1)}% used</span>
          <span>Alert at {(budget.alert_threshold * 100).toFixed(0)}%</span>
        </div>
        {editBudget && (
          <div style={{ marginTop: 16, paddingTop: 16, borderTop: `1px solid ${T.border}`, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }} data-testid="budget-edit">
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Monthly Limit ($)</label>
              <input type="number" value={budget.monthly_limit} onChange={e => setBudget(p => ({ ...p, monthly_limit: parseFloat(e.target.value) || 0 }))} style={formInput} />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Daily Limit ($)</label>
              <input type="number" value={budget.daily_limit} onChange={e => setBudget(p => ({ ...p, daily_limit: parseFloat(e.target.value) || 0 }))} style={formInput} />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Alert Threshold (%)</label>
              <input type="number" min="0" max="100" value={budget.alert_threshold * 100} onChange={e => setBudget(p => ({ ...p, alert_threshold: (parseFloat(e.target.value) || 80) / 100 }))} style={formInput} />
            </div>
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <button onClick={saveBudget} data-testid="save-budget" style={{ width: "100%", padding: "8px 0", borderRadius: 10, background: `linear-gradient(135deg, ${T.indigo}, ${T.violet})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                Save Budget
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Model + Provider */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Cost by Model */}
        <div style={glassCard} data-testid="cost-by-model">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Cpu size={14} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Cost By Model</span>
          </div>
          {byModel.length === 0 ? (
            <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "24px 0" }}>No model cost data yet. Interact with agents to generate data.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {byModel.map((m, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 11, color: T.zinc, width: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontFamily: "monospace", flexShrink: 0 }}>{m.model}</span>
                  <span style={{ fontSize: 10, color: T.zinc, width: 52, textAlign: "right", flexShrink: 0 }}>{m.count} calls</span>
                  <span style={{ fontSize: 11, color: T.red, fontWeight: 700, width: 64, textAlign: "right", fontFamily: "monospace", flexShrink: 0 }}>${m.total_cost.toFixed(4)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cost by Provider */}
        <div style={glassCard} data-testid="cost-by-provider">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Layers size={14} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Cost By Provider</span>
          </div>
          {byProvider.length === 0 ? (
            <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "24px 0" }}>No provider cost data yet. Interact with agents to generate data.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {byProvider.map((p, i) => {
                const accent = PROVIDER_ACCENT[p.provider] || T.teal;
                return (
                  <div key={i} style={{ paddingBottom: 12, borderBottom: i < byProvider.length - 1 ? `1px solid ${T.border}` : "none" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: accent }}>{p.provider}</span>
                      <span style={{ fontSize: 14, fontWeight: 700, color: T.red, fontFamily: "monospace" }}>${p.total_cost.toFixed(4)}</span>
                    </div>
                    <span style={{ fontSize: 10, color: T.zinc }}>
                      {p.count} calls{p.input_tokens > 0 && `   ${fmtTokens(p.input_tokens)} in`}{p.output_tokens > 0 && `   ${fmtTokens(p.output_tokens)} out`}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Cost by Agent */}
      <div style={glassCard} data-testid="cost-by-agent">
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <Bot size={14} style={{ color: T.zinc }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Cost By Agent</span>
        </div>
        {byAgent.length === 0 ? (
          <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "24px 0" }}>No agent cost data yet. Chat with agents to generate data.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {byAgent.slice(0, 15).map((a, i) => {
              const agent = getAgent(a.agent_id);
              const maxCost = byAgent[0]?.total_cost || 1;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  {agent?.avatar
                    ? <img src={agent.avatar} alt="" style={{ width: 20, height: 20, borderRadius: 6, objectFit: "cover", flexShrink: 0 }} />
                    : <div style={{ width: 20, height: 20, borderRadius: 6, background: "rgba(255,255,255,.08)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 7, fontWeight: 700, color: T.zinc, flexShrink: 0 }}>{(agent?.name || a.agent_id).slice(0, 2).toUpperCase()}</div>
                  }
                  <span style={{ fontSize: 11, color: T.zinc, width: 112, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flexShrink: 0 }}>{agent?.name || a.agent_id}</span>
                  <div style={{ flex: 1, height: 4, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, background: T.green, width: `${(a.total_cost / maxCost) * 100}%` }} />
                  </div>
                  <span style={{ fontSize: 11, color: "#e4e4e7", width: 72, textAlign: "right", flexShrink: 0 }}>${a.total_cost.toFixed(4)}</span>
                  <span style={{ fontSize: 10, color: T.zinc, width: 44, textAlign: "right", flexShrink: 0 }}>{a.count} ops</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
