import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Activity, Zap, Clock, CheckCircle, XCircle, AlertTriangle, Search, ArrowRight, DollarSign } from "lucide-react";

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

const STATUS_META = {
  completed: { icon: CheckCircle, color: T.green },
  failed:    { icon: XCircle, color: T.red },
  pending:   { icon: Clock, color: T.amber },
  running:   { icon: Activity, color: T.blue },
};

export default function ExecutionGateway() {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/execution-logs?limit=200`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/agents`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([logsData, agentsData]) => {
        setLogs(Array.isArray(logsData) ? logsData : []);
        setAgents(Array.isArray(agentsData) ? agentsData : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  const getAgent = (agentId) => agents.find(a => a.agent_id === agentId);

  const filteredLogs = logs.filter(log => {
    if (statusFilter !== "all" && log.status !== statusFilter) return false;
    if (searchTerm) {
      const agent = getAgent(log.agent_id);
      const match = log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.agent_id?.toLowerCase().includes(searchTerm.toLowerCase());
      if (!match) return false;
    }
    return true;
  });

  const totalCost = logs.reduce((s, l) => s + (l.cost || 0), 0);
  const avgLatency = logs.length > 0 ? (logs.reduce((s, l) => s + (l.latency_ms || 0), 0) / logs.length).toFixed(0) : 0;
  const successRate = logs.length > 0 ? ((logs.filter(l => l.status === "completed").length / logs.length) * 100).toFixed(1) : 0;

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const METRIC_CARDS = [
    { icon: Zap, label: "Total Executions", value: logs.length, accent: T.indigo },
    { icon: CheckCircle, label: "Success Rate", value: `${successRate}%`, accent: T.green },
    { icon: Clock, label: "Avg Latency", value: `${avgLatency}ms`, accent: T.amber },
    { icon: DollarSign, label: "Total Cost", value: `$${totalCost.toFixed(4)}`, accent: T.cyan },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="execution-gateway">
      <style>{STYLES}</style>

      {/* Header */}
      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Execution Gateway</h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>All agent actions flow through governed execution with cost metering and audit trails</p>
      </div>

      {/* Metrics */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }} data-testid="exec-metrics">
        {METRIC_CARDS.map(c => (
          <div key={c.label} style={{ position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 16px", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: c.accent }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <c.icon size={14} style={{ color: c.accent }} />
              <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em" }}>{c.label}</span>
            </div>
            <div style={{ fontSize: 24, fontWeight: 700, color: c.label === "Success Rate" ? c.accent : "#fff", fontFamily: "'Outfit',sans-serif" }}>{c.value}</div>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        <div style={{ position: "relative", flex: 1, maxWidth: 320 }}>
          <Search size={13} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
          <input
            type="text"
            placeholder="Search actions or agents..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            data-testid="exec-search"
            style={{
              width: "100%", boxSizing: "border-box",
              paddingLeft: 32, paddingRight: 12, paddingTop: 8, paddingBottom: 8,
              background: T.glass, border: `1px solid ${T.border}`, borderRadius: 10,
              color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit",
            }}
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          data-testid="exec-status-filter"
          style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 10, padding: "8px 12px", color: "#fff", fontSize: 12, cursor: "pointer" }}
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="pending">Pending</option>
        </select>
        <span style={{ fontSize: 11, color: T.zinc, marginLeft: "auto" }}>{filteredLogs.length} of {logs.length} entries</span>
      </div>

      {/* Log List */}
      {filteredLogs.length === 0 ? (
        <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }} data-testid="exec-empty">
          <Activity size={44} style={{ color: "rgba(255,255,255,.08)", marginBottom: 14 }} />
          <p style={{ fontSize: 13, color: T.zinc }}>{logs.length === 0 ? "No executions yet. Actions are logged as you chat with agents." : "No matching executions"}</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }} data-testid="exec-log-list">
          {filteredLogs.map((log, i) => {
            const agent = getAgent(log.agent_id);
            const sm = STATUS_META[log.status] || STATUS_META.completed;
            const StatusIcon = sm.icon;
            return (
              <div
                key={i}
                data-testid={`exec-log-${i}`}
                style={{ display: "flex", alignItems: "center", gap: 12, padding: "11px 16px", borderRadius: 10, background: T.glass, border: `1px solid ${T.border}`, transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
              >
                <StatusIcon size={15} style={{ color: sm.color, flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 13, color: "#fff", fontWeight: 500 }}>{log.action}</span>
                    <ArrowRight size={11} style={{ color: T.zinc }} />
                    <span style={{ fontSize: 11, color: T.zinc }}>{agent?.name || log.agent_id || "System"}</span>
                    {log.tool_id && <span style={{ fontSize: 10, background: "rgba(255,255,255,.06)", color: T.zinc, padding: "1px 6px", borderRadius: 5 }}>{log.tool_id}</span>}
                  </div>
                  {log.input_summary && <p style={{ fontSize: 11, color: T.zinc, margin: "2px 0 0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{log.input_summary}</p>}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 11, color: T.zinc, flexShrink: 0 }}>
                  {log.cost > 0 && <span style={{ color: T.cyan }}>${log.cost.toFixed(4)}</span>}
                  {log.latency_ms > 0 && <span>{log.latency_ms.toFixed(0)}ms</span>}
                  <span style={{ fontSize: 10, fontWeight: 600, color: sm.color, background: `${sm.color}18`, padding: "2px 8px", borderRadius: 5 }}>{log.status}</span>
                  <span style={{ fontSize: 10, color: "rgba(113,113,122,.6)" }}>{log.created_at ? new Date(log.created_at).toLocaleTimeString() : ""}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
