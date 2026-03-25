import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Rocket, GitBranch, Users, Cpu, Shield, Activity, AlertTriangle, CheckCircle,
  Clock, Brain, Search, Eye, Bell, BellOff, TrendingUp, RefreshCw, Gauge,
  Plus, Trash2, Settings, Wifi, WifiOff, X, Save
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

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
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  /* ─── New rule form defaults ─── */
  const emptyRule = { rule_id: "", name: "", metric: "circuit_breakers_tripped", operator: ">", threshold: 0, severity: "medium", enabled: true };

  /* ─── Data fetching ─── */
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
  }, [token]);

  useEffect(() => {
    fetchAll();
    const i = setInterval(fetchAll, refreshRate * 1000);
    return () => clearInterval(i);
  }, [fetchAll, refreshRate]);

  /* ─── WebSocket connection ─── */
  useEffect(() => {
    if (!token) return;
    const wsUrl = API.replace(/^http/, "ws") + `/api/ws/infinity?token=${token}&channel=metrics`;
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => { setWsConnected(true); wsRef.current = ws; };
      ws.onclose = () => { setWsConnected(false); reconnectTimer = setTimeout(connect, 5000); };
      ws.onerror = () => { ws.close(); };
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "metrics_update" && data.metrics) {
            setLiveMetrics({ metrics: data.metrics, triggered_alerts: [] });
          }
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

  /* ─── Alert rule actions ─── */
  const ackAlert = async (ruleId) => {
    await fetch(`${API}/api/infinity/alerts/${ruleId}/acknowledge`, { method: "POST", headers });
    fetchAll();
  };

  const saveRule = async () => {
    if (!editingRule?.rule_id || !editingRule?.name) return;
    if (alertRules.find(r => r.rule_id === editingRule.rule_id && !editingRule._existing)) {
      // Updating existing rule
      await fetch(`${API}/api/infinity/alerts/rules/${editingRule.rule_id}`, {
        method: "PUT", headers, body: JSON.stringify({ threshold: editingRule.threshold, enabled: editingRule.enabled, severity: editingRule.severity }),
      });
    } else if (editingRule._existing) {
      await fetch(`${API}/api/infinity/alerts/rules/${editingRule.rule_id}`, {
        method: "PUT", headers, body: JSON.stringify({ threshold: editingRule.threshold, enabled: editingRule.enabled, severity: editingRule.severity }),
      });
    } else {
      await fetch(`${API}/api/infinity/alerts/rules`, {
        method: "POST", headers, body: JSON.stringify(editingRule),
      });
    }
    setEditingRule(null);
    setShowRuleEditor(false);
    fetchAll();
  };

  const deleteRule = async (ruleId) => {
    await fetch(`${API}/api/infinity/alerts/rules/${ruleId}`, { method: "DELETE", headers });
    fetchAll();
  };

  const toggleRule = async (rule) => {
    await fetch(`${API}/api/infinity/alerts/rules/${rule.rule_id}`, {
      method: "PUT", headers, body: JSON.stringify({ enabled: !rule.enabled }),
    });
    fetchAll();
  };

  const m = liveMetrics?.metrics || {};

  const MiniBar = ({ value, max, color }) => (
    <div className="h-1 bg-zinc-800 rounded-full w-full mt-1">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min((value / Math.max(max, 1)) * 100, 100)}%` }} />
    </div>
  );

  return (
    <div className="space-y-5 max-w-7xl" data-testid="observability-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Observability Dashboard</h1>
          <p className="text-sm text-zinc-400">Live system health, metrics, execution runs, and alerting</p>
        </div>
        <div className="flex items-center gap-2">
          {wsConnected ? (
            <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-[10px]" data-testid="ws-status"><Wifi className="w-3 h-3 mr-1" /> Live</Badge>
          ) : (
            <Badge className="bg-zinc-700/30 text-zinc-500 border-zinc-600/30 text-[10px]" data-testid="ws-status"><WifiOff className="w-3 h-3 mr-1" /> Polling</Badge>
          )}
          {alerts.length > 0 && (
            <Badge className="bg-red-500/20 text-red-400 border-red-500/30 animate-pulse" data-testid="alert-count-badge">
              <Bell className="w-3 h-3 mr-1" /> {alerts.length} Alert{alerts.length > 1 ? "s" : ""}
            </Badge>
          )}
          <Badge className={status?.status === "operational" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : "bg-red-500/20 text-red-400"} data-testid="system-status-badge">
            {status?.status === "operational" ? "Operational" : "Degraded"}
          </Badge>
          <select
            className="bg-zinc-800 text-zinc-400 text-[10px] border border-white/10 rounded px-1.5 py-1"
            value={refreshRate} onChange={e => setRefreshRate(+e.target.value)} data-testid="refresh-rate"
          >
            <option value={5}>5s</option><option value={10}>10s</option><option value={30}>30s</option><option value={60}>60s</option>
          </select>
          <Button variant="outline" size="sm" onClick={fetchAll} data-testid="refresh-btn"><RefreshCw className="w-3 h-3" /></Button>
          {lastRefresh && <span className="text-[9px] text-zinc-600">{lastRefresh.toLocaleTimeString()}</span>}
        </div>
      </div>

      {/* Active Alerts Banner */}
      {alerts.length > 0 && (
        <div className="space-y-1.5" data-testid="alerts-banner">
          {alerts.map((a, i) => (
            <div key={i} className={`flex items-center justify-between px-3 py-2 rounded-lg border ${a.severity === "high" ? "bg-red-500/5 border-red-500/20" : a.severity === "medium" ? "bg-amber-500/5 border-amber-500/20" : "bg-zinc-800/40 border-white/5"}`} data-testid={`alert-${a.rule_id}`}>
              <div className="flex items-center gap-2">
                <AlertTriangle className={`w-3.5 h-3.5 ${a.severity === "high" ? "text-red-400" : "text-amber-400"}`} />
                <span className="text-xs text-white font-medium">{a.rule_name}</span>
                <span className="text-[10px] text-zinc-400">{a.metric}={a.value} {a.operator} {a.threshold}</span>
                <Badge className={a.severity === "high" ? "bg-red-500/20 text-red-400 text-[9px]" : "bg-amber-500/20 text-amber-400 text-[9px]"}>{a.severity}</Badge>
              </div>
              <Button variant="ghost" size="sm" className="h-6 text-[10px] text-zinc-500 hover:text-white" onClick={() => ackAlert(a.rule_id)} data-testid={`ack-${a.rule_id}`}>
                <BellOff className="w-3 h-3 mr-1" /> Dismiss
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Live Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3" data-testid="metrics-grid">
        {[
          { icon: Users, label: "Agents", value: m.total_agents, sub: `${m.busy_agents || 0} busy`, color: "bg-indigo-500/20" },
          { icon: Gauge, label: "Utilization", value: `${m.agent_utilization || 0}%`, color: "bg-cyan-500/20" },
          { icon: GitBranch, label: "Networks", value: m.networks, color: "bg-amber-500/20" },
          { icon: Shield, label: "Breakers", value: `${m.circuit_breakers_tripped || 0}/${m.circuit_breakers_total || 0}`, color: m.circuit_breakers_tripped > 0 ? "bg-red-500/20" : "bg-emerald-500/20" },
          { icon: AlertTriangle, label: "Incidents", value: m.open_incidents, color: m.open_incidents > 0 ? "bg-orange-500/20" : "bg-emerald-500/20" },
          { icon: Brain, label: "Models", value: `${m.model_count || 0}`, sub: `${m.model_success_rate_min || 100}% min`, color: "bg-violet-500/20" },
          { icon: Rocket, label: "Runs", value: runs.length, sub: `${runs.filter(r => r.status === "completed").length} ok`, color: "bg-emerald-500/20" },
        ].map((s, i) => (
          <Card key={i} className="bg-zinc-900/50 border-white/5" data-testid={`metric-${s.label.toLowerCase()}`}>
            <CardContent className="p-3 flex items-center gap-2.5">
              <div className={`w-8 h-8 rounded-lg ${s.color} flex items-center justify-center shrink-0`}><s.icon className="w-3.5 h-3.5 text-white" /></div>
              <div className="min-w-0">
                <p className="text-[9px] text-zinc-500 uppercase tracking-wide">{s.label}</p>
                <p className="text-base font-bold text-white leading-tight">{s.value ?? "\u2014"}</p>
                {s.sub && <p className="text-[9px] text-zinc-600 truncate">{s.sub}</p>}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Metrics Sparklines */}
      {metricsHistory.length > 2 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="metrics-trends">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><TrendingUp className="w-4 h-4 text-cyan-400" /> Metrics Trend</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              {[
                { key: "agent_utilization", label: "Agent Utilization %", color: "bg-cyan-400" },
                { key: "model_success_rate_min", label: "Min Model Success %", color: "bg-emerald-400" },
                { key: "open_incidents", label: "Open Incidents", color: "bg-red-400" },
              ].map(({ key, label, color }) => {
                const vals = metricsHistory.map(h => h[key] ?? 0);
                const max = Math.max(...vals, 1);
                return (
                  <div key={key}>
                    <p className="text-[10px] text-zinc-500 mb-1">{label}</p>
                    <div className="flex items-end gap-px h-10">
                      {vals.map((v, i) => (
                        <div key={i} className={`flex-1 ${color} rounded-t-sm opacity-70`} style={{ height: `${Math.max((v / max) * 100, 2)}%` }} />
                      ))}
                    </div>
                    <p className="text-[10px] text-zinc-400 mt-0.5">Current: {vals[vals.length - 1]}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ════════════════════════════════════════════════════ */}
      {/* CUSTOM ALERT RULES MANAGEMENT */}
      {/* ════════════════════════════════════════════════════ */}
      <Card className="bg-zinc-900/50 border-white/5" data-testid="alert-rules-panel">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-white flex items-center gap-2">
              <Settings className="w-4 h-4 text-amber-400" /> Alert Rules
              <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{alertRules.length}</Badge>
            </CardTitle>
            <Button
              variant="outline" size="sm"
              className="h-7 text-[11px] gap-1"
              onClick={() => { setEditingRule({ ...emptyRule }); setShowRuleEditor(true); }}
              data-testid="create-alert-rule-btn"
            >
              <Plus className="w-3 h-3" /> New Rule
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {alertRules.map((rule, i) => (
            <div key={i} className={`flex items-center justify-between p-2 rounded-lg border ${rule.enabled ? "bg-zinc-800/40 border-white/5" : "bg-zinc-800/20 border-white/3 opacity-60"}`} data-testid={`alert-rule-${rule.rule_id}`}>
              <div className="flex items-center gap-2 min-w-0">
                <div className={`w-2 h-2 rounded-full shrink-0 ${rule.enabled ? "bg-emerald-400" : "bg-zinc-600"}`} />
                <span className="text-xs text-white font-medium truncate">{rule.name}</span>
                <span className="text-[10px] text-zinc-500">{rule.metric} {rule.operator} {rule.threshold}</span>
                <Badge className={
                  rule.severity === "high" ? "bg-red-500/20 text-red-400 text-[9px]" :
                  rule.severity === "medium" ? "bg-amber-500/20 text-amber-400 text-[9px]" :
                  "bg-zinc-700/30 text-zinc-400 text-[9px]"
                }>{rule.severity}</Badge>
                {rule.custom && <Badge className="bg-cyan-500/10 text-cyan-400 text-[9px]">custom</Badge>}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-500 hover:text-white" onClick={() => toggleRule(rule)} data-testid={`toggle-rule-${rule.rule_id}`}>
                  {rule.enabled ? <Bell className="w-3 h-3" /> : <BellOff className="w-3 h-3" />}
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-500 hover:text-amber-400" onClick={() => { setEditingRule({ ...rule, _existing: true }); setShowRuleEditor(true); }} data-testid={`edit-rule-${rule.rule_id}`}>
                  <Settings className="w-3 h-3" />
                </Button>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-500 hover:text-red-400" onClick={() => deleteRule(rule.rule_id)} data-testid={`delete-rule-${rule.rule_id}`}>
                  <Trash2 className="w-3 h-3" />
                </Button>
              </div>
            </div>
          ))}
          {alertRules.length === 0 && <p className="text-xs text-zinc-500">No alert rules configured</p>}
        </CardContent>
      </Card>

      {/* Alert Rule Editor Modal */}
      {showRuleEditor && editingRule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="alert-rule-editor-modal">
          <Card className="bg-zinc-900 border-white/10 w-full max-w-md shadow-2xl">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm text-white">{editingRule._existing ? "Edit Alert Rule" : "Create Alert Rule"}</CardTitle>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-500" onClick={() => { setShowRuleEditor(false); setEditingRule(null); }}><X className="w-4 h-4" /></Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {!editingRule._existing && (
                <div>
                  <label className="text-[10px] text-zinc-400 mb-1 block">Rule ID (unique identifier)</label>
                  <input
                    className="w-full bg-zinc-800 border border-white/10 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/40"
                    value={editingRule.rule_id} onChange={e => setEditingRule({ ...editingRule, rule_id: e.target.value.replace(/\s/g, "_").toLowerCase() })}
                    placeholder="e.g., high_latency_warning" data-testid="rule-id-input"
                  />
                </div>
              )}
              <div>
                <label className="text-[10px] text-zinc-400 mb-1 block">Rule Name</label>
                <input
                  className="w-full bg-zinc-800 border border-white/10 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/40"
                  value={editingRule.name} onChange={e => setEditingRule({ ...editingRule, name: e.target.value })}
                  placeholder="Human-readable name" data-testid="rule-name-input"
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] text-zinc-400 mb-1 block">Metric</label>
                  <select
                    className="w-full bg-zinc-800 border border-white/10 rounded px-2 py-1.5 text-xs text-white"
                    value={editingRule.metric} onChange={e => setEditingRule({ ...editingRule, metric: e.target.value })}
                    data-testid="rule-metric-select"
                  >
                    {AVAILABLE_METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-zinc-400 mb-1 block">Operator</label>
                  <select
                    className="w-full bg-zinc-800 border border-white/10 rounded px-2 py-1.5 text-xs text-white"
                    value={editingRule.operator} onChange={e => setEditingRule({ ...editingRule, operator: e.target.value })}
                    data-testid="rule-operator-select"
                  >
                    {OPERATORS.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-zinc-400 mb-1 block">Threshold</label>
                  <input
                    type="number"
                    className="w-full bg-zinc-800 border border-white/10 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/40"
                    value={editingRule.threshold} onChange={e => setEditingRule({ ...editingRule, threshold: parseFloat(e.target.value) || 0 })}
                    data-testid="rule-threshold-input"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-zinc-400 mb-1 block">Severity</label>
                  <select
                    className="w-full bg-zinc-800 border border-white/10 rounded px-2 py-1.5 text-xs text-white"
                    value={editingRule.severity} onChange={e => setEditingRule({ ...editingRule, severity: e.target.value })}
                    data-testid="rule-severity-select"
                  >
                    {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-xs text-zinc-300 cursor-pointer">
                    <input
                      type="checkbox" checked={editingRule.enabled}
                      onChange={e => setEditingRule({ ...editingRule, enabled: e.target.checked })}
                      className="rounded bg-zinc-800 border-white/20"
                      data-testid="rule-enabled-checkbox"
                    />
                    Enabled
                  </label>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => { setShowRuleEditor(false); setEditingRule(null); }} data-testid="cancel-rule-btn">Cancel</Button>
                <Button size="sm" className="bg-amber-600 hover:bg-amber-700" onClick={saveRule} disabled={!editingRule.rule_id || !editingRule.name} data-testid="save-rule-btn">
                  <Save className="w-3 h-3 mr-1" /> {editingRule._existing ? "Update" : "Create"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Execution Runs */}
      {runs.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="execution-runs">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Activity className="w-4 h-4 text-emerald-400" /> Recent Execution Runs</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {runs.map((r, i) => (
              <div key={i} className="p-2.5 rounded-lg bg-zinc-800/40 border border-white/5" data-testid={`run-${r.run_id}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-white font-medium truncate max-w-md">{r.objective?.slice(0, 80)}</span>
                  <div className="flex items-center gap-1.5">
                    <Badge className={r.status === "completed" ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>{r.status}</Badge>
                    <span className="text-[10px] text-zinc-500">${r.summary?.total_cost?.toFixed(4)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-zinc-500">
                  <span>{r.summary?.completed}/{r.summary?.total_nodes} nodes</span>
                  <span>{(r.summary?.total_latency_ms / 1000)?.toFixed(1)}s</span>
                  {r.node_results?.map((n, j) => (
                    <span key={j} className={`w-2 h-2 rounded-full ${n.status === "completed" ? "bg-emerald-400" : "bg-red-400"}`} title={n.node_id} />
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Circuit Breakers */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="circuit-breakers-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Shield className="w-4 h-4 text-red-400" /> Circuit Breakers</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {breakers.slice(0, 6).map((b, i) => (
              <div key={i} className="flex items-center justify-between p-1.5 rounded bg-zinc-800/40 border border-white/5">
                <span className="text-[11px] text-zinc-300">{b.name}</span>
                <Badge variant={b.status === "closed" ? "outline" : "destructive"} className={b.status === "closed" ? "text-emerald-400 border-emerald-500/30 text-[10px]" : "text-[10px]"}>{b.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Model Router Performance */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="router-performance-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Brain className="w-4 h-4 text-violet-400" /> Model Performance</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {routerPerf.slice(0, 6).map((p, i) => (
              <div key={i} className="p-1.5 rounded bg-zinc-800/40 border border-white/5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-white">{p.provider}/{p.model_name}</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30 text-[10px]">{(p.success_rate * 100).toFixed(0)}%</Badge>
                </div>
                <div className="flex items-center gap-2 text-[9px] text-zinc-500 mt-0.5">
                  <span>{p.total_calls} calls</span>
                  <span>avg ${p.avg_cost}</span>
                  <span>{p.avg_latency_ms}ms</span>
                </div>
                <MiniBar value={p.success_rate * 100} max={100} color="bg-emerald-500/60" />
              </div>
            ))}
            {routerPerf.length === 0 && <p className="text-xs text-zinc-500">No model data yet</p>}
          </CardContent>
        </Card>

        {/* Trust Leaderboard */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="trust-leaderboard-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Trust Leaderboard</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {trustLeaders.map((t, i) => (
              <div key={i} className="flex items-center justify-between p-1.5 rounded bg-zinc-800/40 border border-white/5">
                <span className="text-[11px] text-zinc-300">{t.entity_id}</span>
                <Badge variant="outline" className={t.score >= 60 ? "text-emerald-400 border-emerald-500/30 text-[10px]" : t.score >= 30 ? "text-amber-400 border-amber-500/30 text-[10px]" : "text-red-400 border-red-500/30 text-[10px]"}>{t.score}</Badge>
              </div>
            ))}
            {trustLeaders.length === 0 && <p className="text-xs text-zinc-500">No trust scores yet</p>}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Commander Orion Log */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="commander-log-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Rocket className="w-4 h-4 text-amber-400" /> Commander Orion \u2014 Recent Goals</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {commanderLog.map((g, i) => (
              <div key={i} className="p-2 rounded bg-zinc-800/40 border border-white/5">
                <div className="flex items-center justify-between mb-0.5">
                  <div className="flex items-center gap-1.5">
                    <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30 text-[10px]">{g.classification?.goal_type || "general"}</Badge>
                    {g.classification?.ai_powered && <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">AI</Badge>}
                    {g.decomposition_meta?.ai_powered && <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-[10px]">decomp</Badge>}
                  </div>
                  <Badge variant="outline" className="text-cyan-400 border-cyan-500/30 text-[10px]">{g.node_count} nodes</Badge>
                </div>
                <p className="text-[10px] text-zinc-500">{g.environment} | {g.assignments?.length ?? 0} assigned{g.classification?.model_used ? ` | ${g.classification.model_used}` : ""}</p>
              </div>
            ))}
            {commanderLog.length === 0 && <p className="text-xs text-zinc-500">No goals executed yet</p>}
          </CardContent>
        </Card>

        {/* Audit Trail */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="audit-trail-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Eye className="w-4 h-4 text-pink-400" /> Audit Trail</CardTitle></CardHeader>
          <CardContent className="space-y-1">
            {audit.map((a, i) => (
              <div key={i} className="flex items-center gap-2 p-1 rounded bg-zinc-800/40 border border-white/5">
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${a.result === "success" ? "bg-emerald-400" : "bg-red-400"}`} />
                <span className="text-[10px] text-zinc-300 flex-1 truncate">{a.action}</span>
                <span className="text-[9px] text-zinc-600">{a.actor_id}</span>
              </div>
            ))}
            {audit.length === 0 && <p className="text-xs text-zinc-500">No audit entries yet</p>}
          </CardContent>
        </Card>
      </div>

      {/* Verification Stats */}
      {status?.verification_stats?.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="verification-stats-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Search className="w-4 h-4 text-cyan-400" /> Verification Statistics</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {status.verification_stats.map((v, i) => (
                <div key={i} className="p-3 rounded bg-zinc-800/40 border border-white/5 text-center">
                  <p className="text-lg font-bold text-white">{(v.pass_rate * 100).toFixed(0)}%</p>
                  <p className="text-[10px] text-zinc-500">{v.type} ({v.total} checks)</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
