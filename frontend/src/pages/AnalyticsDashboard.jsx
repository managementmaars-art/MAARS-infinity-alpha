import { useState, useEffect, useCallback, useMemo } from "react";
import { useAuth } from "../App";
import { BarChart3, Plus, X, TrendingUp, Activity, Shield, Plug, PieChart, Clock, Workflow, Cpu } from "lucide-react";
import { BarChart, Bar, PieChart as RPie, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";
const COLORS = ["#4fd1c5", "#10b981", "#f59e0b", "#ef4444", "#a78bfa", "#ec4899", "#14b8a6", "#f97316"];

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} }`;

const WIDGET_ICONS = {
  agent_usage: BarChart3, cost_trend: TrendingUp, campaign_performance: PieChart,
  trust_overview: Shield, active_integrations: Plug, model_distribution: PieChart,
  latency_heatmap: Clock, workflow_status: Workflow,
};

export default function AnalyticsDashboard() {
  const { token } = useAuth();
  const [catalog, setCatalog] = useState([]);
  const [dashboard, setDashboard] = useState({ widgets: [] });
  const [widgetData, setWidgetData] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const h = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const fetchData = useCallback(async (silent = false) => {
    if (!silent) setRefreshing(true);
    try {
      const [catRes, dashRes] = await Promise.all([
        fetch(`${API}/api/kernel/widgets/catalog`, { headers: h }),
        fetch(`${API}/api/kernel/dashboard/custom`, { headers: h }),
      ]);
      if (catRes.ok) setCatalog(await catRes.json());
      if (dashRes.ok) {
        const d = await dashRes.json();
        setDashboard(d);
        const widgets = d.widgets || [];
        const dataPromises = widgets.map(w =>
          fetch(`${API}/api/kernel/widgets/${w.widget_id}/data`, { headers: h }).then(r => r.json()).then(data => ({ id: w.widget_id, data }))
        );
        const results = await Promise.all(dataPromises);
        const dataMap = {};
        results.forEach(r => { dataMap[r.id] = r.data; });
        setWidgetData(dataMap);
      }
      setLastRefresh(new Date());
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }, [h]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Auto-refresh every 30 seconds when enabled
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => fetchData(true), 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchData]);

  const addWidget = async (widgetId) => {
    const widgets = [...(dashboard.widgets || []), { widget_id: widgetId, x: 0, y: dashboard.widgets.length }];
    await fetch(`${API}/api/kernel/dashboard/custom`, {
      method: "PUT", headers: h, body: JSON.stringify({ widgets }),
    });
    toast.success("Widget added");
    setShowAdd(false);
    fetchData();
  };

  const removeWidget = async (widgetId) => {
    const widgets = (dashboard.widgets || []).filter(w => w.widget_id !== widgetId);
    await fetch(`${API}/api/kernel/dashboard/custom`, {
      method: "PUT", headers: h, body: JSON.stringify({ widgets }),
    });
    toast.success("Widget removed");
    fetchData();
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <style>{STYLES}</style>
      <div style={{ width: 20, height: 20, border: "2px solid #818cf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
    </div>
  );

  const activeWidgetIds = new Set((dashboard.widgets || []).map(w => w.widget_id));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="analytics-dashboard">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif" }}>Analytics Dashboard</h1>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: T.zinc }}>Custom widgets for real-time platform insights</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {lastRefresh && (
            <span style={{ fontSize: 9, color: "#52525b" }}>
              {refreshing ? "Refreshing..." : `Updated ${lastRefresh.toLocaleTimeString()}`}
            </span>
          )}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{
              padding: "4px 8px",
              borderRadius: 6,
              fontSize: 10,
              border: autoRefresh ? "1px solid rgba(52,211,153,0.3)" : "1px solid rgba(255,255,255,0.1)",
              color: autoRefresh ? T.green : T.zinc,
              background: autoRefresh ? "rgba(52,211,153,0.1)" : "transparent",
              cursor: "pointer",
              fontFamily: "inherit",
              transition: "all .2s",
            }}
            data-testid="auto-refresh-toggle"
          >
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh"}
          </button>
          <button
            onClick={() => fetchData()}
            disabled={refreshing}
            style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 10px", background: "transparent", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#d4d4d8", fontSize: 12, cursor: refreshing ? "not-allowed" : "pointer", fontFamily: "inherit", opacity: refreshing ? 0.6 : 1 }}
            data-testid="refresh-btn"
          >
            <Activity size={13} style={refreshing ? { animation: "spin .8s linear infinite" } : {}} /> Refresh
          </button>
          <button
            onClick={() => setShowAdd(!showAdd)}
            style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 10px", background: "linear-gradient(135deg,#6366f1,#7c3aed)", border: "none", borderRadius: 8, color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}
            data-testid="add-widget-btn"
          >
            <Plus size={13} /> Add Widget
          </button>
        </div>
      </div>

      {/* Add widget panel */}
      {showAdd && (
        <div
          style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: 16 }}
          data-testid="widget-catalog"
        >
          <p style={{ margin: "0 0 12px", fontSize: 12, fontWeight: 600, color: T.zinc }}>Available Widgets</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 8 }}>
            {catalog.map(w => {
              const Icon = WIDGET_ICONS[w.widget_id] || Cpu;
              const added = activeWidgetIds.has(w.widget_id);
              return (
                <button
                  key={w.widget_id}
                  disabled={added}
                  onClick={() => !added && addWidget(w.widget_id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: 12,
                    borderRadius: 10,
                    textAlign: "left",
                    border: added ? "1px solid rgba(52,211,153,0.2)" : "1px solid rgba(255,255,255,0.05)",
                    background: added ? "rgba(52,211,153,0.05)" : "rgba(255,255,255,0.02)",
                    opacity: added ? 0.6 : 1,
                    cursor: added ? "default" : "pointer",
                    fontFamily: "inherit",
                    transition: "border-color .15s, background .15s",
                  }}
                  data-testid={`catalog-widget-${w.widget_id}`}
                >
                  <Icon size={16} color={T.indigo} style={{ flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <p style={{ margin: 0, fontSize: 11, fontWeight: 500, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{w.name}</p>
                    <p style={{ margin: 0, fontSize: 8, color: T.zinc, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{w.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Widget Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }} data-testid="widget-grid">
        {(dashboard.widgets || []).map(w => {
          const meta = catalog.find(c => c.widget_id === w.widget_id);
          const data = widgetData[w.widget_id] || {};
          return (
            <WidgetCard key={w.widget_id} widget={w} meta={meta} data={data} onRemove={() => removeWidget(w.widget_id)} />
          );
        })}
      </div>

      {(dashboard.widgets || []).length === 0 && (
        <div style={{ textAlign: "center", padding: "48px 0", color: "#52525b" }}>
          <BarChart3 size={32} style={{ display: "block", margin: "0 auto 8px", opacity: 0.5 }} />
          <p style={{ margin: 0, fontSize: 13 }}>No widgets added yet. Click "Add Widget" to customize your dashboard.</p>
        </div>
      )}
    </div>
  );
}

function WidgetCard({ widget, meta, data, onRemove }) {
  const Icon = WIDGET_ICONS[widget.widget_id] || Cpu;

  const renderContent = () => {
    switch (widget.widget_id) {
      case "trust_overview":
        return (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "16px 0" }}>
            <div style={{ position: "relative", width: 96, height: 96 }}>
              <svg viewBox="0 0 100 100" style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }}>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#27272a" strokeWidth="8" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#4fd1c5" strokeWidth="8"
                  strokeDasharray={`${(data.avg_trust || 0) * 2.51} 251`} strokeLinecap="round" />
              </svg>
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>{data.avg_trust || 0}%</span>
                <span style={{ fontSize: 8, color: "#71717a" }}>{data.total_agents || 0} agents</span>
              </div>
            </div>
          </div>
        );
      case "active_integrations":
        return (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "24px 0" }}>
            <div style={{ textAlign: "center" }}>
              <p style={{ margin: 0, fontSize: 30, fontWeight: 700, color: "#fff" }}>{data.active || 0}</p>
              <p style={{ margin: 0, fontSize: 10, color: "#71717a" }}>of {data.total || 0} connected</p>
            </div>
          </div>
        );
      case "workflow_status":
        return (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "24px 0" }}>
            <div style={{ textAlign: "center" }}>
              <p style={{ margin: 0, fontSize: 30, fontWeight: 700, color: "#fff" }}>{data.total || 0}</p>
              <p style={{ margin: 0, fontSize: 10, color: "#71717a" }}>workflows</p>
            </div>
          </div>
        );
      case "agent_usage": {
        const agents = (data.agents || []).slice(0, 5);
        return (
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={agents}>
              <XAxis dataKey="name" tick={{ fontSize: 8, fill: "#71717a" }} />
              <YAxis tick={{ fontSize: 8, fill: "#71717a" }} />
              <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
              <Bar dataKey="executions" fill="#4fd1c5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
      }
      case "cost_trend":
        return (
          <div>
            <ResponsiveContainer width="100%" height={130}>
              <LineChart data={data.days || []}>
                <XAxis dataKey="day" tick={{ fontSize: 8, fill: "#71717a" }} />
                <YAxis tick={{ fontSize: 8, fill: "#71717a" }} />
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
                <Line type="monotone" dataKey="cost" stroke="#10b981" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <p style={{ margin: 0, fontSize: 10, color: "#71717a", textAlign: "right" }}>Total: ${data.total || 0}</p>
          </div>
        );
      case "campaign_performance": {
        const pieData = [
          { name: "Completed", value: data.completed || 0 },
          { name: "Failed", value: data.failed || 0 },
          { name: "Draft", value: data.draft || 0 },
        ].filter(d => d.value > 0);
        if (pieData.length === 0) return <p style={{ margin: 0, fontSize: 12, color: "#52525b", textAlign: "center", padding: "32px 0" }}>No campaign data</p>;
        return (
          <ResponsiveContainer width="100%" height={150}>
            <RPie>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={3} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
            </RPie>
          </ResponsiveContainer>
        );
      }
      case "model_distribution": {
        const models = Object.entries(data.models || {}).map(([name, value]) => ({ name, value }));
        return (
          <ResponsiveContainer width="100%" height={150}>
            <RPie>
              <Pie data={models} cx="50%" cy="50%" innerRadius={30} outerRadius={55} paddingAngle={2} dataKey="value">
                {models.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
            </RPie>
          </ResponsiveContainer>
        );
      }
      case "latency_heatmap": {
        const cells = data.cells || [];
        const maxLatency = Math.max(...cells.map(c => c.latency), 1);
        return (
          <div style={{ overflowX: "auto" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(24, 1fr)", gap: 1 }}>
              {Array.from({ length: 7 }).map((_, day) =>
                Array.from({ length: 24 }).map((_, hour) => {
                  const cell = cells.find(c => c.hour === hour && c.day === day);
                  const intensity = cell ? cell.latency / maxLatency : 0;
                  return (
                    <div
                      key={`${day}-${hour}`}
                      style={{ width: "100%", aspectRatio: "1", borderRadius: 2, backgroundColor: `rgba(99, 102, 241, ${0.1 + intensity * 0.8})` }}
                      title={`${["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][day]} ${hour}:00 — ${cell?.latency || 0}ms`}
                    />
                  );
                })
              )}
            </div>
          </div>
        );
      }
      default:
        return <p style={{ margin: 0, fontSize: 12, color: "#52525b", textAlign: "center", padding: "32px 0" }}>Widget data unavailable</p>;
    }
  };

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14,
        padding: 16,
        ...(meta?.size === "large" ? { gridColumn: "span 2" } : {}),
      }}
      data-testid={`widget-${widget.widget_id}`}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <Icon size={14} color="#818cf8" />
        <p style={{ margin: 0, fontSize: 12, fontWeight: 600, color: "#d4d4d8", flex: 1 }}>{meta?.name || widget.widget_id}</p>
        <button
          onClick={onRemove}
          style={{ background: "none", border: "none", cursor: "pointer", padding: 2, display: "flex", alignItems: "center", color: "#52525b" }}
          data-testid={`remove-widget-${widget.widget_id}`}
        >
          <X size={13} />
        </button>
      </div>
      {renderContent()}
    </div>
  );
}
