import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { BarChart3, Plus, X, TrendingUp, Activity, Shield, Plug, PieChart, Clock, Workflow, Cpu } from "lucide-react";
import { BarChart, Bar, PieChart as RPie, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;
const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"];

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

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = async (silent = false) => {
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
  };

  useEffect(() => { fetchData(); }, [token]);

  // Auto-refresh every 30 seconds when enabled
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => fetchData(true), 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, token]);

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

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  const activeWidgetIds = new Set((dashboard.widgets || []).map(w => w.widget_id));

  return (
    <div className="space-y-6" data-testid="analytics-dashboard">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Analytics Dashboard</h1>
          <p className="text-sm text-zinc-500">Custom widgets for real-time platform insights</p>
        </div>
        <div className="flex items-center gap-2">
          {lastRefresh && (
            <span className="text-[9px] text-zinc-600">
              {refreshing ? "Refreshing..." : `Updated ${lastRefresh.toLocaleTimeString()}`}
            </span>
          )}
          <button onClick={() => setAutoRefresh(!autoRefresh)} className={`px-2 py-1 rounded text-[10px] border transition-colors ${autoRefresh ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10" : "border-white/10 text-zinc-500"}`} data-testid="auto-refresh-toggle">
            {autoRefresh ? "Auto-refresh ON" : "Auto-refresh"}
          </button>
          <Button size="sm" variant="outline" className="border-white/10 h-8 text-xs" onClick={() => fetchData()} disabled={refreshing} data-testid="refresh-btn">
            <Activity className={`w-3.5 h-3.5 mr-1 ${refreshing ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 h-8 text-xs" onClick={() => setShowAdd(!showAdd)} data-testid="add-widget-btn">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Widget
          </Button>
        </div>
      </div>

      {/* Add widget panel */}
      {showAdd && (
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4" data-testid="widget-catalog">
          <p className="text-xs font-semibold text-zinc-400 mb-3">Available Widgets</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {catalog.map(w => {
              const Icon = WIDGET_ICONS[w.widget_id] || Cpu;
              const added = activeWidgetIds.has(w.widget_id);
              return (
                <button key={w.widget_id} disabled={added}
                  className={`flex items-center gap-2 p-3 rounded-lg border text-left transition-all ${added ? "border-emerald-500/20 bg-emerald-500/5 opacity-60" : "border-white/5 hover:border-white/10 bg-zinc-800/30"}`}
                  onClick={() => !added && addWidget(w.widget_id)} data-testid={`catalog-widget-${w.widget_id}`}>
                  <Icon className="w-4 h-4 text-indigo-400 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[11px] font-medium text-white truncate">{w.name}</p>
                    <p className="text-[8px] text-zinc-500 truncate">{w.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Widget Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="widget-grid">
        {(dashboard.widgets || []).map(w => {
          const meta = catalog.find(c => c.widget_id === w.widget_id);
          const data = widgetData[w.widget_id] || {};
          return (
            <WidgetCard key={w.widget_id} widget={w} meta={meta} data={data} onRemove={() => removeWidget(w.widget_id)} />
          );
        })}
      </div>

      {(dashboard.widgets || []).length === 0 && (
        <div className="text-center py-12 text-zinc-600">
          <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No widgets added yet. Click "Add Widget" to customize your dashboard.</p>
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
          <div className="flex items-center justify-center py-4">
            <div className="relative w-24 h-24">
              <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#27272a" strokeWidth="8" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#6366f1" strokeWidth="8"
                  strokeDasharray={`${(data.avg_trust || 0) * 2.51} 251`} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-bold text-white">{data.avg_trust || 0}%</span>
                <span className="text-[8px] text-zinc-500">{data.total_agents || 0} agents</span>
              </div>
            </div>
          </div>
        );
      case "active_integrations":
        return (
          <div className="flex items-center justify-center py-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{data.active || 0}</p>
              <p className="text-[10px] text-zinc-500">of {data.total || 0} connected</p>
            </div>
          </div>
        );
      case "workflow_status":
        return (
          <div className="flex items-center justify-center py-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{data.total || 0}</p>
              <p className="text-[10px] text-zinc-500">workflows</p>
            </div>
          </div>
        );
      case "agent_usage":
        const agents = (data.agents || []).slice(0, 5);
        return (
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={agents}>
              <XAxis dataKey="name" tick={{ fontSize: 8, fill: "#71717a" }} />
              <YAxis tick={{ fontSize: 8, fill: "#71717a" }} />
              <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "8px", fontSize: "10px" }} />
              <Bar dataKey="executions" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
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
            <p className="text-[10px] text-zinc-500 text-right">Total: ${data.total || 0}</p>
          </div>
        );
      case "campaign_performance":
        const pieData = [
          { name: "Completed", value: data.completed || 0 },
          { name: "Failed", value: data.failed || 0 },
          { name: "Draft", value: data.draft || 0 },
        ].filter(d => d.value > 0);
        if (pieData.length === 0) return <p className="text-xs text-zinc-600 text-center py-8">No campaign data</p>;
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
      case "model_distribution":
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
      case "latency_heatmap":
        const cells = data.cells || [];
        const maxLatency = Math.max(...cells.map(c => c.latency), 1);
        return (
          <div className="overflow-x-auto">
            <div className="grid gap-px" style={{ gridTemplateColumns: "repeat(24, 1fr)" }}>
              {Array.from({ length: 7 }).map((_, day) =>
                Array.from({ length: 24 }).map((_, hour) => {
                  const cell = cells.find(c => c.hour === hour && c.day === day);
                  const intensity = cell ? cell.latency / maxLatency : 0;
                  return <div key={`${day}-${hour}`} className="w-full aspect-square rounded-sm"
                    style={{ backgroundColor: `rgba(99, 102, 241, ${0.1 + intensity * 0.8})` }}
                    title={`${["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][day]} ${hour}:00 — ${cell?.latency || 0}ms`} />;
                })
              )}
            </div>
          </div>
        );
      default:
        return <p className="text-xs text-zinc-600 text-center py-8">Widget data unavailable</p>;
    }
  };

  return (
    <div className={`bg-zinc-900/50 border border-white/5 rounded-xl p-4 ${meta?.size === "large" ? "md:col-span-2" : ""}`} data-testid={`widget-${widget.widget_id}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-4 h-4 text-indigo-400" />
        <p className="text-xs font-semibold text-zinc-300 flex-1">{meta?.name || widget.widget_id}</p>
        <button onClick={onRemove} className="text-zinc-600 hover:text-red-400 transition-colors" data-testid={`remove-widget-${widget.widget_id}`}>
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
      {renderContent()}
    </div>
  );
}
