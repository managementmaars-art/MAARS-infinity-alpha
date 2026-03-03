import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import {
  BarChart3, TrendingUp, DollarSign, Target, Shield, Zap,
  AlertTriangle, CheckCircle, Clock, Plus, X, Activity
} from "lucide-react";
import { toast } from "sonner";

const StatCard = ({ icon: Icon, label, value, subtitle, color = "indigo" }) => (
  <Card className="bg-zinc-900/50 border-white/5" data-testid={`stat-${label.toLowerCase().replace(/\s+/g, '-')}`}>
    <CardContent className="p-4">
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg bg-${color}-500/15 flex items-center justify-center shrink-0`}>
          <Icon className={`w-4 h-4 text-${color}-400`} />
        </div>
        <div className="min-w-0">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">{label}</p>
          <p className="text-xl font-bold text-white font-['Outfit']">{value}</p>
          {subtitle && <p className="text-[10px] text-zinc-400">{subtitle}</p>}
        </div>
      </div>
    </CardContent>
  </Card>
);

const ProgressBar = ({ value, max, color = "indigo" }) => (
  <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
    <div className={`h-full bg-${color}-500 rounded-full transition-all`} style={{ width: `${Math.min(100, (value / Math.max(max, 1)) * 100)}%` }} />
  </div>
);

const KPIDashboard = () => {
  const { token } = useAuth();
  const [kpis, setKpis] = useState(null);
  const [costData, setCostData] = useState(null);
  const [systemMode, setSystemMode] = useState("simulation");
  const [loading, setLoading] = useState(true);
  const [newKpi, setNewKpi] = useState({ name: "", value: 0, target: 0, unit: "" });
  const [showAddKpi, setShowAddKpi] = useState(false);

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = useCallback(async () => {
    try {
      const [kpiRes, costRes, modeRes] = await Promise.all([
        fetch(`${API}/kpis`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/cost-governance`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/system/mode`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (kpiRes.ok) setKpis(await kpiRes.json());
      if (costRes.ok) setCostData(await costRes.json());
      if (modeRes.ok) {
        const modeData = await modeRes.json();
        setSystemMode(modeData.mode);
      }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const toggleMode = async () => {
    const newMode = systemMode === "simulation" ? "execution" : "simulation";
    try {
      const res = await fetch(`${API}/system/mode`, {
        method: "PUT", headers,
        body: JSON.stringify({ mode: newMode }),
      });
      if (res.ok) {
        setSystemMode(newMode);
        toast.success(`Switched to ${newMode} mode`);
      }
    } catch { toast.error("Failed to switch mode"); }
  };

  const addCustomKpi = async () => {
    if (!newKpi.name) return;
    try {
      const res = await fetch(`${API}/kpis/custom`, {
        method: "POST", headers,
        body: JSON.stringify(newKpi),
      });
      if (res.ok) {
        toast.success("KPI added");
        setShowAddKpi(false);
        setNewKpi({ name: "", value: 0, target: 0, unit: "" });
        fetchData();
      }
    } catch { toast.error("Failed to add KPI"); }
  };

  if (loading) return <div className="flex items-center justify-center py-20"><div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" /></div>;

  const ops = kpis?.operational || {};
  const gov = kpis?.governance || {};
  const cost = kpis?.cost || {};

  return (
    <div className="space-y-6" data-testid="kpi-dashboard">
      {/* Header with System Mode */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white font-['Outfit']">KPI Command Center</h1>
            <p className="text-xs text-zinc-500">Real-time business intelligence & cost governance</p>
          </div>
        </div>

        {/* System Mode Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-zinc-900/80 border border-white/10 rounded-xl px-4 py-2">
            <div className={`w-2.5 h-2.5 rounded-full ${systemMode === "execution" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
            <span className="text-xs text-zinc-300 font-medium">{systemMode === "execution" ? "LIVE MODE" : "SIMULATION"}</span>
            <button
              onClick={toggleMode}
              className={`ml-2 w-10 h-5 rounded-full transition-colors ${systemMode === "execution" ? "bg-emerald-500" : "bg-zinc-700"}`}
              data-testid="mode-toggle"
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${systemMode === "execution" ? "translate-x-5" : "translate-x-0.5"}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Operational KPIs */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider">Operational Performance</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <StatCard icon={Target} label="Projects" value={ops.total_projects || 0} subtitle={`${ops.project_completion_rate || 0}% completed`} />
          <StatCard icon={CheckCircle} label="Tasks Done" value={ops.completed_tasks || 0} subtitle={`of ${ops.total_tasks || 0} total`} color="emerald" />
          <StatCard icon={Zap} label="AI Chats" value={ops.total_chats || 0} color="violet" />
          <StatCard icon={Activity} label="Collaborations" value={ops.total_collaborations || 0} color="cyan" />
        </div>
      </div>

      {/* Governance KPIs */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider">Governance & Risk</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard icon={Shield} label="Approvals" value={gov.total_approvals || 0} subtitle={`${gov.pending_approvals || 0} pending`} color="amber" />
          <StatCard icon={Zap} label="Tool Calls" value={gov.total_tool_calls || 0} color="indigo" />
          <StatCard icon={AlertTriangle} label="Risk Incidents" value={gov.risk_incidents || 0} color="red" />
        </div>
      </div>

      {/* Cost Governance */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider">Cost Governance</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
          <StatCard icon={DollarSign} label="Total AI Cost" value={`$${cost.total_ai_cost || 0}`} color="emerald" />
          <StatCard icon={Activity} label="Total AI Calls" value={cost.total_ai_calls || 0} color="indigo" />
          <StatCard icon={TrendingUp} label="Avg Cost/Call" value={`$${cost.avg_cost_per_call || 0}`} color="violet" />
        </div>
        {costData?.agent_costs?.length > 0 && (
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-4">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Cost by Agent</p>
              <div className="space-y-2">
                {costData.agent_costs.slice(0, 10).map((ac, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-zinc-400 w-40 truncate">{ac.agent}</span>
                    <div className="flex-1"><ProgressBar value={ac.total_cost} max={costData.agent_costs[0]?.total_cost || 1} /></div>
                    <span className="text-xs text-white font-mono w-16 text-right">${ac.total_cost}</span>
                    <span className="text-[10px] text-zinc-500 w-14 text-right">{ac.call_count} calls</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Custom KPIs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Custom KPIs</h2>
          <Button size="sm" variant="ghost" onClick={() => setShowAddKpi(!showAddKpi)} className="text-zinc-400 hover:text-white" data-testid="add-kpi-btn">
            <Plus className="w-4 h-4 mr-1" />{showAddKpi ? "Cancel" : "Add KPI"}
          </Button>
        </div>
        {showAddKpi && (
          <Card className="bg-zinc-900/50 border-white/10 mb-4">
            <CardContent className="p-4 flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-[120px]">
                <label className="text-[10px] text-zinc-500 mb-1 block">Name</label>
                <Input value={newKpi.name} onChange={e => setNewKpi({ ...newKpi, name: e.target.value })} className="bg-zinc-800/50 border-white/10 text-white text-xs" placeholder="Revenue" data-testid="kpi-name-input" />
              </div>
              <div className="w-24">
                <label className="text-[10px] text-zinc-500 mb-1 block">Value</label>
                <Input type="number" value={newKpi.value} onChange={e => setNewKpi({ ...newKpi, value: parseFloat(e.target.value) || 0 })} className="bg-zinc-800/50 border-white/10 text-white text-xs" />
              </div>
              <div className="w-24">
                <label className="text-[10px] text-zinc-500 mb-1 block">Target</label>
                <Input type="number" value={newKpi.target} onChange={e => setNewKpi({ ...newKpi, target: parseFloat(e.target.value) || 0 })} className="bg-zinc-800/50 border-white/10 text-white text-xs" />
              </div>
              <div className="w-20">
                <label className="text-[10px] text-zinc-500 mb-1 block">Unit</label>
                <Input value={newKpi.unit} onChange={e => setNewKpi({ ...newKpi, unit: e.target.value })} className="bg-zinc-800/50 border-white/10 text-white text-xs" placeholder="$" />
              </div>
              <Button size="sm" onClick={addCustomKpi} className="bg-indigo-600 hover:bg-indigo-500 text-white" data-testid="save-kpi-btn">Save</Button>
            </CardContent>
          </Card>
        )}
        {kpis?.custom_kpis?.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {kpis.custom_kpis.map(k => (
              <Card key={k.kpi_id} className="bg-zinc-900/50 border-white/5">
                <CardContent className="p-4">
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider">{k.name}</p>
                  <p className="text-lg font-bold text-white font-['Outfit']">{k.unit}{k.value}</p>
                  {k.target > 0 && (
                    <>
                      <ProgressBar value={k.value} max={k.target} color={k.value >= k.target ? "emerald" : "amber"} />
                      <p className="text-[10px] text-zinc-500 mt-1">Target: {k.unit}{k.target}</p>
                    </>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        ) : !showAddKpi && (
          <div className="text-center py-8 border border-dashed border-white/10 rounded-xl">
            <Target className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
            <p className="text-sm text-zinc-500">No custom KPIs yet. Add revenue, CAC, LTV, and more.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default KPIDashboard;
