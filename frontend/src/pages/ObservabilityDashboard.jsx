import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import {
  Rocket, GitBranch, Users, Cpu, Shield, Activity, AlertTriangle, CheckCircle,
  Clock, Brain, Search, Eye, Bell, BellOff, TrendingUp, RefreshCw, Gauge,
  Plus, Trash2, Settings, Wifi, WifiOff, X, Save
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

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
  orange: "#f97316",
  blue: "#60a5fa",
  pink: "#f472b6",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
@keyframes slideIn { from{opacity:0;transform:scale(.96)} to{opacity:1;transform:scale(1)} }
@keyframes bar { from{width:0} to{width:var(--w)} }
`;

const glass = (extra = {}) => ({
  background: T.glass,
  border: `1px solid ${T.border}`,
  borderRadius: 16,
  backdropFilter: "blur(12px)",
  ...extra,
});

const Chip = ({ children, color = T.zinc, bg, style = {} }) => (
  <span style={{
    display: "inline-flex", alignItems: "center", gap: 4,
    fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 6,
    background: bg || `${color}18`, color,
    letterSpacing: ".04em",
    ...style,
  }}>{children}</span>
);

const Btn = ({ children, onClick, variant = "ghost", color, disabled, style = {}, ...rest }) => {
  const base = {
    display: "inline-flex", alignItems: "center", gap: 6,
    padding: "6px 14px", borderRadius: 10, fontSize: 12, fontWeight: 500,
    cursor: disabled ? "not-allowed" : "pointer",
    border: "none", outline: "none", fontFamily: "inherit",
    opacity: disabled ? .5 : 1, transition: "all .15s",
    ...style,
  };
  if (variant === "primary") return <button onClick={onClick} disabled={disabled} style={{ ...base, background: `linear-gradient(135deg, ${T.violet}, #9333ea)`, color: "#fff", ...style }} {...rest}>{children}</button>;
  if (variant === "outline") return <button onClick={onClick} disabled={disabled} style={{ ...base, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, ...style }} {...rest}>{children}</button>;
  if (variant === "danger") return <button onClick={onClick} disabled={disabled} style={{ ...base, background: "rgba(239,68,68,0.1)", color: T.red, ...style }} {...rest}>{children}</button>;
  return <button onClick={onClick} disabled={disabled} style={{ ...base, background: "transparent", color: color || T.zinc, ...style }} {...rest}>{children}</button>;
};

const Panel = ({ title, icon, children, accent = T.teal, testId, headerRight, style = {} }) => (
  <div style={{ ...glass(), padding: 0, overflow: "hidden", ...style }} data-testid={testId}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent }} />
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ color: accent }}>{icon}</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{title}</span>
      </div>
      {headerRight}
    </div>
    <div style={{ padding: "14px 18px" }}>{children}</div>
  </div>
);

const MiniBar = ({ value, max, color }) => (
  <div style={{ height: 3, background: "rgba(255,255,255,.06)", borderRadius: 4, width: "100%", marginTop: 4, overflow: "hidden" }}>
    <div style={{ height: "100%", borderRadius: 4, background: color, width: `${Math.min((value / Math.max(max, 1)) * 100, 100)}%` }} />
  </div>
);

/* ───── Available metrics for alert rules ───── */
const AVAILABLE_METRICS = [
  { value: "circuit_breakers_tripped", label: "Circuit Breakers Tripped" },
  { value: "open_incidents", label: "Open Incidents" },
  { value: "low_trust_count", label: "Low Trust Agents" },
  { value: "agent_utilization", label: "Agent Utilization %" },
  { value: "model_success_rate_min", label: "Min Model Success Rate %" },
  { value: "recent_failures", label: "Recent Execution Failures" },
  { value: "busy_agents", label: "Busy Agents" },
  { value: "total_agents", label: "Total Agents" },
];

const OPERATORS = [">", "<", ">=", "=="];
const SEVERITIES = ["low", "medium", "high"];

const formInput = {
  width: "100%", boxSizing: "border-box",
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "7px 10px",
  color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit",
};

export default function ObservabilityDashboard() {
  const [status, setStatus] = useState(null);
  const [breakers, setBreakers] = useState([]);
  const [audit, setAudit] = useState([]);
  const [routerPerf, setRouterPerf] = useState([]);
  const [trustLeaders, setTrustLeaders] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [commanderLog, setCommanderLog] = useState([]);
  const [liveMetrics, setLiveMetrics] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [runs, setRuns] = useState([]);
  const [refreshRate, setRefreshRate] = useState(10);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [alertRules, setAlertRules] = useState([]);
  const [showRuleEditor, setShowRuleEditor] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const token = localStorage.getItem("token");
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const emptyRule = { rule_id: "", name: "", metric: "circuit_breakers_tripped", operator: ">", threshold: 0, severity: "medium", enabled: true };

  const fetchAll = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [s, b, a, rp, tl, inc, cl, lm, mh, al, rn, rules] = await Promise.all([
      f("/api/infinity/system/status"),
      f("/api/infinity/governance/circuit-breakers"),
      f("/api/infinity/governance/audit?limit=8"),
      f("/api/infinity/router/performance"),
      f("/api/infinity/governance/trust/leaderboard?limit=5"),
      f("/api/infinity/governance/incidents?status=open"),
      f("/api/infinity/orchestrator/log?limit=5"),
      f("/api/infinity/metrics/live"),
      f("/api/infinity/metrics/history?limit=20"),
      f("/api/infinity/alerts/active"),
      f("/api/infinity/orchestrator/runs?limit=5"),
      f("/api/infinity/alerts/rules"),
    ]);
    if (s) setStatus(s);
    if (b) setBreakers(b);
    if (a?.entries) setAudit(a.entries);
    if (rp) setRouterPerf(rp);
    if (tl) setTrustLeaders(tl);
    if (inc) setIncidents(inc);
    if (cl) setCommanderLog(cl);
    if (lm) setLiveMetrics(lm);
    if (Array.isArray(mh)) setMetricsHistory(mh);
    if (Array.isArray(al)) setAlerts(al);
    if (Array.isArray(rn)) setRuns(rn);
    if (Array.isArray(rules)) setAlertRules(rules);
    setLastRefresh(new Date());
  }, [headers]);

  useEffect(() => {
    fetchAll();
    const i = setInterval(fetchAll, refreshRate * 1000);
    return () => clearInterval(i);
  }, [fetchAll, refreshRate]);

  useEffect(() => {
    if (!token) return;
    const wsUrl = API.replace(/^http/, "ws") + `/api/ws/infinity?token=${token}&channel=metrics`;
    let ws, reconnectTimer;
    const connect = () => {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => { setWsConnected(true); wsRef.current = ws; };
      ws.onclose = () => { setWsConnected(false); reconnectTimer = setTimeout(connect, 5000); };
      ws.onerror = () => ws.close();
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "metrics_update" && data.metrics) setLiveMetrics({ metrics: data.metrics, triggered_alerts: [] });
          if (data.type === "alert_triggered" && data.alert) {
            setAlerts(prev => {
              const exists = prev.find(a => a.rule_id === data.alert.rule_id);
              return exists ? prev : [data.alert, ...prev];
            });
          }
        } catch {}
      };
    };
    connect();
    return () => { clearTimeout(reconnectTimer); ws?.close(); };
  }, [token]);

  const ackAlert = async (ruleId) => {
    await fetch(`${API}/api/infinity/alerts/${ruleId}/acknowledge`, { method: "POST", headers });
    fetchAll();
  };

  const saveRule = async () => {
    if (!editingRule?.rule_id || !editingRule?.name) return;
    const isExisting = editingRule._existing || alertRules.find(r => r.rule_id === editingRule.rule_id);
    if (isExisting) {
      await fetch(`${API}/api/infinity/alerts/rules/${editingRule.rule_id}`, {
        method: "PUT", headers, body: JSON.stringify({ threshold: editingRule.threshold, enabled: editingRule.enabled, severity: editingRule.severity }),
      });
    } else {
      await fetch(`${API}/api/infinity/alerts/rules`, { method: "POST", headers, body: JSON.stringify(editingRule) });
    }
    setEditingRule(null); setShowRuleEditor(false); fetchAll();
  };

  const deleteRule = async (ruleId) => { await fetch(`${API}/api/infinity/alerts/rules/${ruleId}`, { method: "DELETE", headers }); fetchAll(); };
  const toggleRule = async (rule) => { await fetch(`${API}/api/infinity/alerts/rules/${rule.rule_id}`, { method: "PUT", headers, body: JSON.stringify({ enabled: !rule.enabled }) }); fetchAll(); };

  const m = liveMetrics?.metrics || {};
  const isOp = status?.status === "operational";

  const METRIC_CARDS = [
    { icon: <Users size={14} />, label: "Agents", value: m.total_agents, sub: `${m.busy_agents || 0} busy`, accent: T.teal },
    { icon: <Gauge size={14} />, label: "Utilization", value: `${m.agent_utilization || 0}%`, accent: T.blue },
    { icon: <GitBranch size={14} />, label: "Networks", value: m.networks, accent: T.amber },
    { icon: <Shield size={14} />, label: "Breakers", value: `${m.circuit_breakers_tripped || 0}/${m.circuit_breakers_total || 0}`, accent: (m.circuit_breakers_tripped > 0) ? T.red : T.green },
    { icon: <AlertTriangle size={14} />, label: "Incidents", value: m.open_incidents, accent: (m.open_incidents > 0) ? T.orange : T.green },
    { icon: <Brain size={14} />, label: "Models", value: `${m.model_count || 0}`, sub: `${m.model_success_rate_min || 100}% min`, accent: T.violet },
    { icon: <Rocket size={14} />, label: "Runs", value: runs.length, sub: `${runs.filter(r => r.status === "completed").length} ok`, accent: T.pink },
  ];

  return (
    <div style={{ maxWidth: 1280, animation: "fadeUp .4s ease" }} data-testid="observability-dashboard">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28, gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Observability</h1>
          <p style={{ color: T.zinc, fontSize: 13, margin: 0 }}>Live system health, metrics, execution runs, and alerting</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          {wsConnected
            ? <Chip color={T.green} style={{ padding: "4px 10px" }} data-testid="ws-status"><Wifi size={11} /> Live</Chip>
            : <Chip color={T.zinc} style={{ padding: "4px 10px" }} data-testid="ws-status"><WifiOff size={11} /> Polling</Chip>
          }
          {alerts.length > 0 && (
            <Chip color={T.red} style={{ padding: "4px 10px", animation: "pulse 1.5s infinite" }} data-testid="alert-count-badge">
              <Bell size={11} /> {alerts.length} Alert{alerts.length > 1 ? "s" : ""}
            </Chip>
          )}
          <Chip color={isOp ? T.green : T.red} style={{ padding: "4px 10px" }} data-testid="system-status-badge">
            {isOp ? "Operational" : "Degraded"}
          </Chip>
          <select
            value={refreshRate} onChange={e => setRefreshRate(+e.target.value)}
            data-testid="refresh-rate"
            style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, color: T.zinc, fontSize: 11, padding: "4px 8px", cursor: "pointer" }}
          >
            <option value={5}>5s</option><option value={10}>10s</option><option value={30}>30s</option><option value={60}>60s</option>
          </select>
          <button onClick={fetchAll} data-testid="refresh-btn" style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 32, height: 32, borderRadius: 8, background: T.glass, border: `1px solid ${T.border}`, cursor: "pointer", color: T.zinc }}>
            <RefreshCw size={13} />
          </button>
          {lastRefresh && <span style={{ fontSize: 10, color: T.zinc }}>{lastRefresh.toLocaleTimeString()}</span>}
        </div>
      </div>

      {/* Active Alerts Banner */}
      {alerts.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 20 }} data-testid="alerts-banner">
          {alerts.map((a, i) => {
            const sevColor = a.severity === "high" ? T.red : T.amber;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderRadius: 12, background: `${sevColor}08`, border: `1px solid ${sevColor}25` }} data-testid={`alert-${a.rule_id}`}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <AlertTriangle size={13} style={{ color: sevColor, flexShrink: 0 }} />
                  <span style={{ fontSize: 12, color: "#fff", fontWeight: 600 }}>{a.rule_name}</span>
                  <span style={{ fontSize: 11, color: T.zinc }}>{a.metric}={a.value} {a.operator} {a.threshold}</span>
                  <Chip color={sevColor}>{a.severity}</Chip>
                </div>
                <button onClick={() => ackAlert(a.rule_id)} data-testid={`ack-${a.rule_id}`} style={{ display: "flex", alignItems: "center", gap: 5, background: "none", border: "none", color: T.zinc, fontSize: 11, cursor: "pointer" }}>
                  <BellOff size={12} /> Dismiss
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Live Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 10, marginBottom: 20 }} data-testid="metrics-grid">
        {METRIC_CARDS.map((s, i) => (
          <div key={i} style={{ ...glass(), padding: "14px 14px", position: "relative", overflow: "hidden" }} data-testid={`metric-${s.label.toLowerCase()}`}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.accent }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: s.accent }}>{s.icon}</div>
            <div style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 2 }}>{s.label}</div>
            <div style={{ fontSize: 20, fontWeight: 700, color: "#fff", lineHeight: 1 }}>{s.value ?? "—"}</div>
            {s.sub && <div style={{ fontSize: 10, color: T.zinc, marginTop: 2 }}>{s.sub}</div>}
          </div>
        ))}
      </div>

      {/* Sparklines */}
      {metricsHistory.length > 2 && (
        <div style={{ ...glass(), padding: 20, marginBottom: 20 }} data-testid="metrics-trends">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <TrendingUp size={14} style={{ color: T.teal }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>Metrics Trend</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20 }}>
            {[
              { key: "agent_utilization", label: "Agent Utilization %", color: T.teal },
              { key: "model_success_rate_min", label: "Min Model Success %", color: T.green },
              { key: "open_incidents", label: "Open Incidents", color: T.red },
            ].map(({ key, label, color }) => {
              const vals = metricsHistory.map(h => h[key] ?? 0);
              const max = Math.max(...vals, 1);
              return (
                <div key={key}>
                  <p style={{ fontSize: 10, color: T.zinc, margin: "0 0 6px", textTransform: "uppercase", letterSpacing: ".05em" }}>{label}</p>
                  <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 40 }}>
                    {vals.map((v, i) => (
                      <div key={i} style={{ flex: 1, background: color, opacity: .7, borderRadius: "2px 2px 0 0", height: `${Math.max((v / max) * 100, 2)}%` }} />
                    ))}
                  </div>
                  <p style={{ fontSize: 10, color, margin: "4px 0 0", fontWeight: 600 }}>Current: {vals[vals.length - 1]}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Alert Rules Panel */}
      <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden", marginBottom: 20 }} data-testid="alert-rules-panel">
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.amber }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Settings size={14} style={{ color: T.amber }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Alert Rules</span>
            <Chip color={T.zinc}>{alertRules.length}</Chip>
          </div>
          <button
            onClick={() => { setEditingRule({ ...emptyRule }); setShowRuleEditor(true); }}
            data-testid="create-alert-rule-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: "rgba(245,158,11,0.12)", border: `1px solid rgba(245,158,11,0.3)`, color: T.amber, fontSize: 11, fontWeight: 600, cursor: "pointer" }}
          >
            <Plus size={12} /> New Rule
          </button>
        </div>
        <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 6 }}>
          {alertRules.map((rule, i) => (
            <div
              key={i}
              data-testid={`alert-rule-${rule.rule_id}`}
              style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 12px", borderRadius: 10, background: rule.enabled ? "rgba(255,255,255,.03)" : "rgba(255,255,255,.01)", border: `1px solid ${T.border}`, opacity: rule.enabled ? 1 : .5 }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: rule.enabled ? T.green : T.zinc, flexShrink: 0 }} />
                <span style={{ fontSize: 12, color: "#fff", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{rule.name}</span>
                <span style={{ fontSize: 10, color: T.zinc }}>{rule.metric} {rule.operator} {rule.threshold}</span>
                <Chip color={rule.severity === "high" ? T.red : rule.severity === "medium" ? T.amber : T.zinc}>{rule.severity}</Chip>
                {rule.custom && <Chip color={T.teal}>custom</Chip>}
              </div>
              <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                <button onClick={() => toggleRule(rule)} data-testid={`toggle-rule-${rule.rule_id}`} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4, borderRadius: 6 }}>
                  {rule.enabled ? <Bell size={13} /> : <BellOff size={13} />}
                </button>
                <button onClick={() => { setEditingRule({ ...rule, _existing: true }); setShowRuleEditor(true); }} data-testid={`edit-rule-${rule.rule_id}`} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4, borderRadius: 6 }}>
                  <Settings size={13} />
                </button>
                <button onClick={() => deleteRule(rule.rule_id)} data-testid={`delete-rule-${rule.rule_id}`} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4, borderRadius: 6 }}>
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
          {alertRules.length === 0 && <p style={{ fontSize: 12, color: T.zinc, padding: "4px 0" }}>No alert rules configured</p>}
        </div>
      </div>

      {/* Alert Rule Editor Modal */}
      {showRuleEditor && editingRule && (
        <div
          style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,.7)", backdropFilter: "blur(8px)" }}
          data-testid="alert-rule-editor-modal"
          onClick={e => e.target === e.currentTarget && (setShowRuleEditor(false), setEditingRule(null))}
        >
          <div style={{ background: "#0d1117", border: `1px solid ${T.border}`, borderRadius: 20, width: "100%", maxWidth: 440, padding: 28, animation: "slideIn .2s ease", boxShadow: "0 25px 60px rgba(0,0,0,.5)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 22 }}>
              <span style={{ fontSize: 16, fontWeight: 700, color: "#fff", fontFamily: "'Outfit',sans-serif" }}>
                {editingRule._existing ? "Edit Alert Rule" : "Create Alert Rule"}
              </span>
              <button onClick={() => { setShowRuleEditor(false); setEditingRule(null); }} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer" }}><X size={16} /></button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {!editingRule._existing && (
                <div>
                  <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Rule ID</label>
                  <input
                    style={formInput} value={editingRule.rule_id}
                    onChange={e => setEditingRule({ ...editingRule, rule_id: e.target.value.replace(/\s/g, "_").toLowerCase() })}
                    placeholder="e.g., high_latency_warning" data-testid="rule-id-input"
                  />
                </div>
              )}
              <div>
                <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Rule Name</label>
                <input style={formInput} value={editingRule.name} onChange={e => setEditingRule({ ...editingRule, name: e.target.value })} placeholder="Human-readable name" data-testid="rule-name-input" />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
                <div>
                  <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Metric</label>
                  <select style={formInput} value={editingRule.metric} onChange={e => setEditingRule({ ...editingRule, metric: e.target.value })} data-testid="rule-metric-select">
                    {AVAILABLE_METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Operator</label>
                  <select style={formInput} value={editingRule.operator} onChange={e => setEditingRule({ ...editingRule, operator: e.target.value })} data-testid="rule-operator-select">
                    {OPERATORS.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Threshold</label>
                  <input type="number" style={formInput} value={editingRule.threshold} onChange={e => setEditingRule({ ...editingRule, threshold: parseFloat(e.target.value) || 0 })} data-testid="rule-threshold-input" />
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <div>
                  <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Severity</label>
                  <select style={formInput} value={editingRule.severity} onChange={e => setEditingRule({ ...editingRule, severity: e.target.value })} data-testid="rule-severity-select">
                    {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div style={{ display: "flex", alignItems: "flex-end", paddingBottom: 2 }}>
                  <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: T.zinc, cursor: "pointer" }}>
                    <input type="checkbox" checked={editingRule.enabled} onChange={e => setEditingRule({ ...editingRule, enabled: e.target.checked })} data-testid="rule-enabled-checkbox" style={{ accentColor: T.teal }} />
                    Enabled
                  </label>
                </div>
              </div>
              <div style={{ display: "flex", gap: 8, paddingTop: 6 }}>
                <button onClick={() => { setShowRuleEditor(false); setEditingRule(null); }} data-testid="cancel-rule-btn" style={{ flex: 1, padding: "9px 0", borderRadius: 10, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 12, cursor: "pointer" }}>Cancel</button>
                <button onClick={saveRule} disabled={!editingRule.rule_id || !editingRule.name} data-testid="save-rule-btn" style={{ flex: 2, padding: "9px 0", borderRadius: 10, background: `linear-gradient(135deg, ${T.amber}cc, #d97706)`, border: "none", color: "#000", fontSize: 12, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                  <Save size={12} /> {editingRule._existing ? "Update" : "Create"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Execution Runs */}
      {runs.length > 0 && (
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden", marginBottom: 20 }} data-testid="execution-runs">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.green }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Activity size={14} style={{ color: T.green }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Recent Execution Runs</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 8 }}>
            {runs.map((r, i) => (
              <div key={i} style={{ padding: "10px 12px", borderRadius: 10, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }} data-testid={`run-${r.run_id}`}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 12, color: "#fff", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "60%" }}>{r.objective?.slice(0, 80)}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Chip color={r.status === "completed" ? T.green : T.red}>{r.status}</Chip>
                    <span style={{ fontSize: 10, color: T.zinc }}>${r.summary?.total_cost?.toFixed(4)}</span>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 10, color: T.zinc }}>
                  <span>{r.summary?.completed}/{r.summary?.total_nodes} nodes</span>
                  <span>{(r.summary?.total_latency_ms / 1000)?.toFixed(1)}s</span>
                  <div style={{ display: "flex", gap: 3 }}>
                    {r.node_results?.map((n, j) => (
                      <div key={j} style={{ width: 7, height: 7, borderRadius: "50%", background: n.status === "completed" ? T.green : T.red }} title={n.node_id} />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3-column panels */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16, marginBottom: 16 }}>
        {/* Circuit Breakers */}
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="circuit-breakers-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.red }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Shield size={14} style={{ color: T.red }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Circuit Breakers</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 6 }}>
            {breakers.slice(0, 6).map((b, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 10px", borderRadius: 8, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
                <span style={{ fontSize: 11, color: "#d4d4d8" }}>{b.name}</span>
                <Chip color={b.status === "closed" ? T.green : T.red}>{b.status}</Chip>
              </div>
            ))}
            {breakers.length === 0 && <p style={{ fontSize: 12, color: T.zinc }}>No breakers configured</p>}
          </div>
        </div>

        {/* Model Router Performance */}
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="router-performance-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.violet }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Brain size={14} style={{ color: T.violet }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Model Performance</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 8 }}>
            {routerPerf.slice(0, 5).map((p, i) => (
              <div key={i} style={{ padding: "6px 0" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "#fff" }}>{p.provider}/{p.model_name}</span>
                  <Chip color={T.green}>{(p.success_rate * 100).toFixed(0)}%</Chip>
                </div>
                <div style={{ fontSize: 10, color: T.zinc, marginBottom: 4 }}>{p.total_calls} calls · ${p.avg_cost} avg · {p.avg_latency_ms}ms</div>
                <MiniBar value={p.success_rate * 100} max={100} color={T.violet} />
              </div>
            ))}
            {routerPerf.length === 0 && <p style={{ fontSize: 12, color: T.zinc }}>No model data yet</p>}
          </div>
        </div>

        {/* Trust Leaderboard */}
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="trust-leaderboard-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.teal }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <CheckCircle size={14} style={{ color: T.teal }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Trust Leaderboard</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 8 }}>
            {trustLeaders.map((t, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 10px", borderRadius: 8, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 10, color: T.zinc, width: 16 }}>{i + 1}.</span>
                  <span style={{ fontSize: 11, color: "#d4d4d8" }}>{t.entity_id}</span>
                </div>
                <Chip color={t.score >= 60 ? T.green : t.score >= 30 ? T.amber : T.red}>{t.score}</Chip>
              </div>
            ))}
            {trustLeaders.length === 0 && <p style={{ fontSize: 12, color: T.zinc }}>No trust scores yet</p>}
          </div>
        </div>
      </div>

      {/* Commander Log + Audit Trail */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Commander Log */}
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="commander-log-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.amber }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Rocket size={14} style={{ color: T.amber }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Commander Orion — Recent Goals</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 8 }}>
            {commanderLog.map((g, i) => (
              <div key={i} style={{ padding: "8px 12px", borderRadius: 10, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4, flexWrap: "wrap" }}>
                  <Chip color={T.violet}>{g.classification?.goal_type || "general"}</Chip>
                  {g.classification?.ai_powered && <Chip color={T.green}>AI</Chip>}
                  {g.decomposition_meta?.ai_powered && <Chip color={T.teal}>decomp</Chip>}
                  <Chip color={T.teal} style={{ marginLeft: "auto" }}>{g.node_count} nodes</Chip>
                </div>
                <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{g.environment} · {g.assignments?.length ?? 0} assigned{g.classification?.model_used ? ` · ${g.classification.model_used}` : ""}</p>
              </div>
            ))}
            {commanderLog.length === 0 && <p style={{ fontSize: 12, color: T.zinc }}>No goals executed yet</p>}
          </div>
        </div>

        {/* Audit Trail */}
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="audit-trail-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.pink }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Eye size={14} style={{ color: T.pink }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Audit Trail</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 4 }}>
            {audit.map((a, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 8px", borderRadius: 8, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", background: a.result === "success" ? T.green : T.red, flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: "#d4d4d8", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.action}</span>
                <span style={{ fontSize: 10, color: T.zinc, flexShrink: 0 }}>{a.actor_id}</span>
              </div>
            ))}
            {audit.length === 0 && <p style={{ fontSize: 12, color: T.zinc }}>No audit entries yet</p>}
          </div>
        </div>
      </div>

      {/* Verification Stats */}
      {status?.verification_stats?.length > 0 && (
        <div style={{ position: "relative", ...glass(), padding: 0, overflow: "hidden" }} data-testid="verification-stats-panel">
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.blue }} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "16px 18px 12px", borderBottom: `1px solid ${T.border}` }}>
            <Search size={14} style={{ color: T.blue }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Verification Statistics</span>
          </div>
          <div style={{ padding: "16px 18px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
              {status.verification_stats.map((v, i) => (
                <div key={i} style={{ padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}`, textAlign: "center" }}>
                  <p style={{ fontSize: 22, fontWeight: 700, color: "#fff", margin: "0 0 4px" }}>{(v.pass_rate * 100).toFixed(0)}%</p>
                  <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{v.type} ({v.total} checks)</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
