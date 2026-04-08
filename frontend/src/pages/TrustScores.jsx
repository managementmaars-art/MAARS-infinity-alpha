import { useState, useEffect } from "react";
import { useAuth } from "../App";
import {
  Shield, TrendingUp, TrendingDown, Activity, Zap, AlertTriangle,
  CheckCircle, Search, XCircle
} from "lucide-react";
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const API = process.env.REACT_APP_BACKEND_URL;

const T = {
  bg: "#030712",
  glass: "rgba(255,255,255,0.03)",
  glass2: "rgba(255,255,255,0.06)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  blue: "#60a5fa",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

function getTrustMeta(score) {
  if (score >= 90) return { color: T.green,  bg: "rgba(52,211,153,0.10)",  label: "Excellent" };
  if (score >= 70) return { color: T.blue,   bg: "rgba(96,165,250,0.10)",  label: "Good" };
  if (score >= 50) return { color: T.amber,  bg: "rgba(245,158,11,0.10)",  label: "Fair" };
  return              { color: T.red,    bg: "rgba(239,68,68,0.10)",   label: "Poor" };
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#0d1117", border: `1px solid ${T.border}`, borderRadius: 10, padding: "10px 14px", fontSize: 11 }}>
      <div style={{ color: T.zinc, marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || T.teal, fontWeight: 600 }}>{p.name}: {typeof p.value === "number" ? p.value.toFixed(1) : p.value}</div>
      ))}
    </div>
  );
};

const glass = {
  background: T.glass,
  border: `1px solid ${T.border}`,
  borderRadius: 16,
  backdropFilter: "blur(12px)",
};

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

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.teal}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const scores = data?.scores || [];
  const trends = data?.trend_data || [];
  const anomalies = data?.anomalies || [];
  const summary = data?.summary || {};

  const getAgent = (id) => agents.find(a => a.agent_id === id);

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

  const healthMeta = summary.health_status === "healthy"
    ? { color: T.green, bg: "rgba(52,211,153,0.1)" }
    : summary.health_status === "warning"
    ? { color: T.amber, bg: "rgba(245,158,11,0.1)" }
    : { color: T.red, bg: "rgba(239,68,68,0.1)" };

  const SUMMARY_STATS = [
    { icon: Shield, label: "Avg Trust", value: `${summary.avg_trust_score || 0}%`, color: T.violet },
    { icon: Activity, label: "Agents Scored", value: summary.total_agents_scored || 0, color: T.teal },
    { icon: Zap, label: "Executions", value: summary.total_executions || 0, color: T.amber },
    { icon: AlertTriangle, label: "Anomalies", value: summary.anomaly_count || 0, color: T.red },
  ];

  const DISTRIBUTION = [
    { label: "Excellent (90–100)", min: 90, max: 100, color: T.green },
    { label: "Good (70–89)",       min: 70, max: 89,  color: T.blue },
    { label: "Fair (50–69)",       min: 50, max: 69,  color: T.amber },
    { label: "Poor (<50)",         min: 0,  max: 49,  color: T.red },
  ];

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", animation: "fadeUp .4s ease" }} data-testid="trust-analytics">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Trust Analytics</h1>
          <p style={{ color: T.zinc, fontSize: 13, margin: 0 }}>Agent reliability scoring, trend analysis, and anomaly detection</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, background: healthMeta.bg, border: `1px solid ${healthMeta.color}40`, borderRadius: 20, padding: "6px 14px" }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: healthMeta.color, animation: "pulse 2s infinite" }} />
          <span style={{ fontSize: 11, fontWeight: 700, color: healthMeta.color, letterSpacing: ".08em" }}>{(summary.health_status || "healthy").toUpperCase()}</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 20 }} data-testid="trust-summary">
        {SUMMARY_STATS.map(s => (
          <div key={s.label} style={{ ...glass, padding: "16px 18px", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color, borderRadius: "16px 16px 0 0" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <s.icon size={14} style={{ color: s.color }} />
              <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em" }}>{s.label}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, color: "#fff" }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Main Trend Chart */}
      {trends.length > 0 && (
        <div style={{ ...glass, padding: "20px 20px 12px", marginBottom: 16 }} data-testid="trust-trend-chart">
          <p style={{ fontSize: 12, fontWeight: 600, color: T.teal, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: ".06em" }}>Trust Score Trend — 30 Days</p>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="trustGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={T.teal} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={T.teal} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: T.zinc }} tickFormatter={v => v.slice(5)} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: T.zinc }} domain={[60, 100]} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="avg_trust" stroke={T.teal} fill="url(#trustGrad)" strokeWidth={2} name="Avg Trust" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Executions + Latency */}
      {trends.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
          <div style={{ ...glass, padding: "18px 18px 10px" }}>
            <p style={{ fontSize: 11, fontWeight: 600, color: T.green, margin: "0 0 14px", textTransform: "uppercase", letterSpacing: ".06em" }}>Daily Executions</p>
            <ResponsiveContainer width="100%" height={120}>
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="execGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={T.green} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={T.green} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 8, fill: T.zinc }} tickFormatter={v => v.slice(8)} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 8, fill: T.zinc }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="total_executions" stroke={T.green} fill="url(#execGrad)" strokeWidth={1.5} name="Executions" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div style={{ ...glass, padding: "18px 18px 10px" }}>
            <p style={{ fontSize: 11, fontWeight: 600, color: T.amber, margin: "0 0 14px", textTransform: "uppercase", letterSpacing: ".06em" }}>Avg Latency (ms)</p>
            <ResponsiveContainer width="100%" height={120}>
              <LineChart data={trends}>
                <XAxis dataKey="date" tick={{ fontSize: 8, fill: T.zinc }} tickFormatter={v => v.slice(8)} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 8, fill: T.zinc }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="avg_latency_ms" stroke={T.amber} strokeWidth={1.5} dot={false} name="Latency ms" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Distribution + Leaderboards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 20 }} data-testid="trust-distribution">
        {/* Distribution */}
        <div style={{ ...glass, padding: 20 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: T.zinc, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: ".06em" }}>Distribution</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {DISTRIBUTION.map(range => {
              const count = scores.filter(s => s.trust_score >= range.min && s.trust_score <= range.max).length;
              const pct = scores.length ? Math.round((count / scores.length) * 100) : 0;
              return (
                <div key={range.label}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, marginBottom: 4 }}>
                    <span style={{ color: T.zinc }}>{range.label}</span>
                    <span style={{ color: range.color, fontWeight: 600 }}>{count} ({pct}%)</span>
                  </div>
                  <div style={{ height: 4, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, background: range.color, width: `${pct}%`, transition: "width .6s ease" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Performers */}
        <div style={{ ...glass, padding: 20 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: T.green, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: ".06em" }}>Top Performers</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[...scores].sort((a, b) => b.trust_score - a.trust_score).slice(0, 5).map((s, i) => {
              const agent = getAgent(s.agent_id);
              return (
                <div key={s.agent_id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 10, color: T.zinc, width: 16 }}>{i + 1}.</span>
                  <span style={{ fontSize: 12, color: "#fff", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent?.name || s.agent_id}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: T.green }}>{Math.round(s.trust_score)}</span>
                </div>
              );
            })}
            {scores.length === 0 && <p style={{ fontSize: 11, color: T.zinc }}>No data yet</p>}
          </div>
        </div>

        {/* Needs Improvement */}
        <div style={{ ...glass, padding: 20 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: T.amber, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: ".06em" }}>Needs Improvement</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[...scores].sort((a, b) => a.trust_score - b.trust_score).slice(0, 5).map((s, i) => {
              const agent = getAgent(s.agent_id);
              const meta = getTrustMeta(s.trust_score);
              return (
                <div key={s.agent_id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 10, color: T.zinc, width: 16 }}>{i + 1}.</span>
                  <span style={{ fontSize: 12, color: "#fff", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent?.name || s.agent_id}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: meta.color }}>{Math.round(s.trust_score)}</span>
                </div>
              );
            })}
            {scores.length === 0 && <p style={{ fontSize: 11, color: T.zinc }}>No data yet</p>}
          </div>
        </div>
      </div>

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <div style={{ background: "rgba(239,68,68,0.04)", border: `1px solid rgba(239,68,68,0.15)`, borderRadius: 16, padding: 20, marginBottom: 20 }} data-testid="trust-anomalies">
          <p style={{ fontSize: 11, fontWeight: 700, color: T.red, margin: "0 0 12px", textTransform: "uppercase", letterSpacing: ".08em" }}>
            Anomalies Detected ({anomalies.length})
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {anomalies.map((a, i) => {
              const agent = getAgent(a.agent_id);
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                  <XCircle size={14} style={{ color: a.severity === "high" ? T.red : T.amber, flexShrink: 0 }} />
                  <span style={{ color: "#e4e4e7", fontWeight: 500 }}>{agent?.name || a.agent_id}</span>
                  <span style={{ color: T.zinc }}>{a.message}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Agent Scores Table */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
          <div style={{ position: "relative", flex: 1, maxWidth: 280 }}>
            <Search size={13} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
            <input
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              placeholder="Search agents..."
              data-testid="trust-search"
              style={{
                width: "100%", boxSizing: "border-box",
                paddingLeft: 32, paddingRight: 12, paddingTop: 7, paddingBottom: 7,
                background: T.glass, border: `1px solid ${T.border}`, borderRadius: 10,
                color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit",
              }}
            />
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            {[{ v: "trust_score", l: "Trust" }, { v: "executions", l: "Executions" }, { v: "latency", l: "Latency" }].map(s => (
              <button
                key={s.v}
                onClick={() => setSortBy(s.v)}
                style={{
                  padding: "5px 14px", borderRadius: 8, fontSize: 11, fontWeight: 500, cursor: "pointer",
                  background: sortBy === s.v ? "rgba(79,209,197,0.12)" : "transparent",
                  border: sortBy === s.v ? `1px solid rgba(79,209,197,0.35)` : `1px solid ${T.border}`,
                  color: sortBy === s.v ? T.teal : T.zinc,
                }}
              >
                {s.l}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 8 }} data-testid="trust-scores-list">
          {filteredScores.length === 0 && (
            <div style={{ textAlign: "center", padding: "40px 0" }}>
              <Shield size={36} style={{ color: "rgba(255,255,255,.08)", marginBottom: 12 }} />
              <p style={{ fontSize: 13, color: T.zinc }}>No trust score data yet. Execute agent tasks to build trust scores.</p>
            </div>
          )}
          {filteredScores.map(s => {
            const agent = getAgent(s.agent_id);
            const meta = getTrustMeta(s.trust_score);
            const TrendIcon = s.trust_score >= 80 ? TrendingUp : s.trust_score >= 50 ? Activity : TrendingDown;
            const trendColor = s.trust_score >= 80 ? T.green : s.trust_score >= 50 ? T.amber : T.red;
            return (
              <div
                key={s.agent_id}
                style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 16px", borderRadius: 12, background: T.glass, border: `1px solid ${T.border}`, transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
              >
                {/* Score badge */}
                <div style={{ width: 44, height: 44, borderRadius: 12, background: meta.bg, border: `1px solid ${meta.color}30`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <span style={{ fontSize: 14, fontWeight: 700, color: meta.color }}>{Math.round(s.trust_score)}</span>
                </div>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: 13, fontWeight: 500, color: "#fff", margin: 0, marginBottom: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent?.name || s.agent_id}</p>
                  <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{s.total_executions} executions · {s.avg_latency_ms}ms avg · <span style={{ color: meta.color }}>{meta.label}</span></p>
                </div>

                {/* Trust bar */}
                <div style={{ width: 96, flexShrink: 0 }}>
                  <div style={{ height: 4, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, background: meta.color, width: `${s.trust_score}%`, transition: "width .6s ease" }} />
                  </div>
                </div>

                {/* Trend icon */}
                <TrendIcon size={14} style={{ color: trendColor, flexShrink: 0 }} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
