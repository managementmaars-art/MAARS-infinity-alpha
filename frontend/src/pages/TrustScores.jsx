import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Shield, TrendingUp, TrendingDown, Activity, Zap, Clock, AlertTriangle, CheckCircle, Search, BarChart3, XCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

const API = process.env.REACT_APP_BACKEND_URL;

export default function TrustScores() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("trust_score");

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/trust-analytics`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/agents`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([analyticsData, agentsData]) => {
        setData(analyticsData);
        setAgents(Array.isArray(agentsData) ? agentsData : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  const getAgent = (agentId) => agents.find(a => a.agent_id === agentId);
  const getTrustColor = (score) => {
    if (score >= 90) return { bg: "bg-emerald-500/10", text: "text-emerald-400", bar: "bg-emerald-500" };
    if (score >= 70) return { bg: "bg-blue-500/10", text: "text-blue-400", bar: "bg-blue-500" };
    if (score >= 50) return { bg: "bg-amber-500/10", text: "text-amber-400", bar: "bg-amber-500" };
    return { bg: "bg-red-500/10", text: "text-red-400", bar: "bg-red-500" };
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  const scores = data?.scores || [];
  const trends = data?.trend_data || [];
  const anomalies = data?.anomalies || [];
  const summary = data?.summary || {};

  const sortedScores = [...scores].sort((a, b) => {
    if (sortBy === "trust_score") return b.trust_score - a.trust_score;
    if (sortBy === "executions") return b.total_executions - a.total_executions;
    if (sortBy === "latency") return a.avg_latency_ms - b.avg_latency_ms;
    return 0;
  });
  const filteredScores = sortedScores.filter(s => {
    if (!searchTerm) return true;
    const agent = getAgent(s.agent_id);
    return agent?.name?.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const healthColor = summary.health_status === "healthy" ? "text-emerald-400" : summary.health_status === "warning" ? "text-amber-400" : "text-red-400";

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6" data-testid="trust-analytics">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Trust Analytics</h1>
          <p className="text-sm text-zinc-500">Agent reliability scoring, trend analysis, and anomaly detection</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${summary.health_status === "healthy" ? "bg-emerald-500/10" : summary.health_status === "warning" ? "bg-amber-500/10" : "bg-red-500/10"}`}>
          <div className={`w-2 h-2 rounded-full ${summary.health_status === "healthy" ? "bg-emerald-400" : summary.health_status === "warning" ? "bg-amber-400" : "bg-red-400"}`} />
          <span className={`text-xs font-medium ${healthColor}`}>{(summary.health_status || "healthy").toUpperCase()}</span>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="trust-summary">
        <SummaryCard icon={<Shield className="w-4 h-4 text-indigo-400" />} label="Avg Trust" value={`${summary.avg_trust_score || 0}%`} />
        <SummaryCard icon={<Activity className="w-4 h-4 text-emerald-400" />} label="Agents Scored" value={summary.total_agents_scored || 0} />
        <SummaryCard icon={<Zap className="w-4 h-4 text-amber-400" />} label="Total Executions" value={summary.total_executions || 0} />
        <SummaryCard icon={<AlertTriangle className="w-4 h-4 text-red-400" />} label="Anomalies" value={summary.anomaly_count || 0} />
      </div>

      {/* Trend Chart */}
      {trends.length > 0 && (
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4" data-testid="trust-trend-chart">
          <p className="text-xs font-semibold text-zinc-400 mb-3">Trust Score Trend (30 days)</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="trustGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: "#71717a" }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 9, fill: "#71717a" }} domain={[60, 100]} />
              <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "11px" }} />
              <Area type="monotone" dataKey="avg_trust" stroke="#6366f1" fill="url(#trustGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Execution + Latency Chart */}
      {trends.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
            <p className="text-xs font-semibold text-zinc-400 mb-3">Daily Executions</p>
            <ResponsiveContainer width="100%" height={150}>
              <AreaChart data={trends}>
                <defs><linearGradient id="execGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.3} /><stop offset="95%" stopColor="#10b981" stopOpacity={0} /></linearGradient></defs>
                <XAxis dataKey="date" tick={{ fontSize: 8, fill: "#71717a" }} tickFormatter={v => v.slice(8)} />
                <YAxis tick={{ fontSize: 8, fill: "#71717a" }} />
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
                <Area type="monotone" dataKey="total_executions" stroke="#10b981" fill="url(#execGrad)" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
            <p className="text-xs font-semibold text-zinc-400 mb-3">Avg Latency (ms)</p>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={trends}>
                <XAxis dataKey="date" tick={{ fontSize: 8, fill: "#71717a" }} tickFormatter={v => v.slice(8)} />
                <YAxis tick={{ fontSize: 8, fill: "#71717a" }} />
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
                <Line type="monotone" dataKey="avg_latency_ms" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Trust Distribution + Top/Bottom Performers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3" data-testid="trust-distribution">
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-400 mb-3">Trust Distribution</p>
          <div className="space-y-2">
            {[
              { label: "Excellent (90-100)", min: 90, max: 100, color: "bg-emerald-500" },
              { label: "Good (70-89)", min: 70, max: 89, color: "bg-blue-500" },
              { label: "Fair (50-69)", min: 50, max: 69, color: "bg-amber-500" },
              { label: "Poor (<50)", min: 0, max: 49, color: "bg-red-500" },
            ].map(range => {
              const count = scores.filter(s => s.trust_score >= range.min && s.trust_score <= range.max).length;
              const pct = scores.length ? Math.round((count / scores.length) * 100) : 0;
              return (
                <div key={range.label}>
                  <div className="flex justify-between text-[10px] mb-0.5">
                    <span className="text-zinc-400">{range.label}</span>
                    <span className="text-zinc-500">{count} ({pct}%)</span>
                  </div>
                  <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${range.color}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-emerald-400 mb-3">Top Performers</p>
          <div className="space-y-1.5">
            {scores.slice(0, 5).sort((a, b) => b.trust_score - a.trust_score).map((s, i) => {
              const agent = getAgent(s.agent_id);
              return (
                <div key={s.agent_id} className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600 w-4">{i + 1}.</span>
                  <span className="text-xs text-white truncate flex-1">{agent?.name || s.agent_id}</span>
                  <span className="text-xs font-bold text-emerald-400">{Math.round(s.trust_score)}</span>
                </div>
              );
            })}
            {scores.length === 0 && <p className="text-[10px] text-zinc-600">No data yet</p>}
          </div>
        </div>
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-amber-400 mb-3">Needs Improvement</p>
          <div className="space-y-1.5">
            {scores.slice().sort((a, b) => a.trust_score - b.trust_score).slice(0, 5).map((s, i) => {
              const agent = getAgent(s.agent_id);
              const c = getTrustColor(s.trust_score);
              return (
                <div key={s.agent_id} className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600 w-4">{i + 1}.</span>
                  <span className="text-xs text-white truncate flex-1">{agent?.name || s.agent_id}</span>
                  <span className={`text-xs font-bold ${c.text}`}>{Math.round(s.trust_score)}</span>
                </div>
              );
            })}
            {scores.length === 0 && <p className="text-[10px] text-zinc-600">No data yet</p>}
          </div>
        </div>
      </div>

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <div className="bg-red-950/20 border border-red-500/10 rounded-xl p-4" data-testid="trust-anomalies">
          <p className="text-xs font-semibold text-red-400 mb-2">Anomalies Detected ({anomalies.length})</p>
          <div className="space-y-2">
            {anomalies.map((a, i) => {
              const agent = getAgent(a.agent_id);
              return (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <XCircle className={`w-3.5 h-3.5 ${a.severity === "high" ? "text-red-400" : "text-amber-400"}`} />
                  <span className="text-zinc-300 font-medium">{agent?.name || a.agent_id}</span>
                  <span className="text-zinc-500">{a.message}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Agent Scores */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} placeholder="Search agents..."
              className="w-full pl-8 pr-3 py-1.5 bg-zinc-900/50 border border-white/5 rounded-lg text-xs text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30" data-testid="trust-search" />
          </div>
          <div className="flex gap-1">
            {[{ v: "trust_score", l: "Trust" }, { v: "executions", l: "Executions" }, { v: "latency", l: "Latency" }].map(s => (
              <button key={s.v} onClick={() => setSortBy(s.v)} className={`px-2 py-1 rounded text-[10px] ${sortBy === s.v ? "bg-indigo-500/20 text-indigo-400" : "text-zinc-500 hover:text-zinc-300"}`}>{s.l}</button>
            ))}
          </div>
        </div>
        <div className="space-y-2" data-testid="trust-scores-list">
          {filteredScores.length === 0 && <p className="text-xs text-zinc-600 text-center py-8">No trust score data yet. Execute agent tasks to build trust scores.</p>}
          {filteredScores.map(s => {
            const agent = getAgent(s.agent_id);
            const c = getTrustColor(s.trust_score);
            return (
              <div key={s.agent_id} className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/5 bg-zinc-900/30">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold ${c.bg} ${c.text}`}>{Math.round(s.trust_score)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{agent?.name || s.agent_id}</p>
                  <p className="text-[10px] text-zinc-500">{s.total_executions} executions &middot; {s.avg_latency_ms}ms avg</p>
                </div>
                <div className="w-24 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${c.bar}`} style={{ width: `${s.trust_score}%` }} />
                </div>
                <div className="flex items-center gap-1">
                  {s.trust_score >= 80 ? <TrendingUp className="w-3.5 h-3.5 text-emerald-400" /> : s.trust_score >= 50 ? <Activity className="w-3.5 h-3.5 text-amber-400" /> : <TrendingDown className="w-3.5 h-3.5 text-red-400" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ icon, label, value }) {
  return (
    <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
      <div className="flex items-center gap-2 mb-1">{icon}<span className="text-[10px] text-zinc-500">{label}</span></div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}
