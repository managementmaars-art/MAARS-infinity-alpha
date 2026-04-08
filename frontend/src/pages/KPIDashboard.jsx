import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { BarChart3, TrendingUp, DollarSign, Target, Shield, Zap, AlertTriangle, CheckCircle, Activity, Plus, X } from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
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
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "7px 10px", color: "#fff", fontSize: 12,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
};

const StatCard = ({ icon: Icon, label, value, subtitle, accent = T.indigo }) => (
  <div
    style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 16px", position: "relative", overflow: "hidden" }}
    data-testid={`stat-${label.toLowerCase().replace(/\s+/g, "-")}`}
  >
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent }} />
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{ width: 38, height: 38, borderRadius: 10, background: `${accent}18`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Icon size={16} style={{ color: accent }} />
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 2 }}>{label}</div>
        <div style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "'Outfit',sans-serif", lineHeight: 1 }}>{value}</div>
        {subtitle && <div style={{ fontSize: 10, color: T.zinc, marginTop: 2 }}>{subtitle}</div>}
      </div>
    </div>
  </div>
);

const Bar = ({ value, max, color }) => (
  <div style={{ height: 4, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden", flex: 1 }}>
    <div style={{ height: "100%", borderRadius: 4, background: color, width: `${Math.min(100, (value / Math.max(max, 1)) * 100)}%`, transition: "width .6s" }} />
  </div>
);

const SectionHead = ({ label }) => (
  <div style={{ fontSize: 10, fontWeight: 700, color: T.zinc, textTransform: "uppercase", letterSpacing: ".1em", marginBottom: 14 }}>{label}</div>
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
      if (modeRes.ok) { const d = await modeRes.json(); setSystemMode(d.mode); }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const toggleMode = async () => {
    const newMode = systemMode === "simulation" ? "execution" : "simulation";
    try {
      const res = await fetch(`${API}/system/mode`, { method: "PUT", headers, body: JSON.stringify({ mode: newMode }) });
      if (res.ok) { setSystemMode(newMode); toast.success(`Switched to ${newMode} mode`); }
    } catch { toast.error("Failed to switch mode"); }
  };

  const addCustomKpi = async () => {
    if (!newKpi.name) return;
    try {
      const res = await fetch(`${API}/kpis/custom`, { method: "POST", headers, body: JSON.stringify(newKpi) });
      if (res.ok) { toast.success("KPI added"); setShowAddKpi(false); setNewKpi({ name: "", value: 0, target: 0, unit: "" }); fetchData(); }
    } catch { toast.error("Failed to add KPI"); }
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", paddingTop: 80 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.teal}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const ops = kpis?.operational || {};
  const gov = kpis?.governance || {};
  const cost = kpis?.cost || {};
  const isExec = systemMode === "execution";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28, animation: "fadeUp .4s ease" }} data-testid="kpi-dashboard">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 14, background: "rgba(129,140,248,.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <BarChart3 size={20} style={{ color: T.indigo }} />
          </div>
          <div>
            <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 22, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 2 }}>KPI Command Center</h1>
            <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>Real-time business intelligence & cost governance</p>
          </div>
        </div>

        {/* System Mode Toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 16px", borderRadius: 12, background: T.glass, border: `1px solid ${T.border}` }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: isExec ? T.green : T.amber, animation: isExec ? "pulse 1.5s infinite" : "none" }} />
          <span style={{ fontSize: 11, color: "#e4e4e7", fontWeight: 600 }}>{isExec ? "LIVE MODE" : "SIMULATION"}</span>
          <button
            onClick={toggleMode}
            data-testid="mode-toggle"
            style={{
              width: 40, height: 22, borderRadius: 11, border: "none", cursor: "pointer",
              background: isExec ? T.green : "rgba(255,255,255,.15)", position: "relative",
              transition: "background .2s",
            }}
          >
            <div style={{
              position: "absolute", top: 3, width: 16, height: 16, borderRadius: "50%",
              background: "#fff", transition: "left .2s",
              left: isExec ? 21 : 3,
            }} />
          </button>
        </div>
      </div>

      {/* Operational KPIs */}
      <div>
        <SectionHead label="Operational Performance" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))", gap: 12 }}>
          <StatCard icon={Target} label="Projects" value={ops.total_projects || 0} subtitle={`${ops.project_completion_rate || 0}% completed`} accent={T.blue} />
          <StatCard icon={CheckCircle} label="Tasks Done" value={ops.completed_tasks || 0} subtitle={`of ${ops.total_tasks || 0} total`} accent={T.green} />
          <StatCard icon={Zap} label="AI Chats" value={ops.total_chats || 0} accent={T.violet} />
          <StatCard icon={Activity} label="Collaborations" value={ops.total_collaborations || 0} accent={T.cyan} />
        </div>
      </div>

      {/* Governance KPIs */}
      <div>
        <SectionHead label="Governance & Risk" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))", gap: 12 }}>
          <StatCard icon={Shield} label="Approvals" value={gov.total_approvals || 0} subtitle={`${gov.pending_approvals || 0} pending`} accent={T.amber} />
          <StatCard icon={Zap} label="Tool Calls" value={gov.total_tool_calls || 0} accent={T.indigo} />
          <StatCard icon={AlertTriangle} label="Risk Incidents" value={gov.risk_incidents || 0} accent={T.red} />
        </div>
      </div>

      {/* Cost Governance */}
      <div>
        <SectionHead label="Cost Governance" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))", gap: 12, marginBottom: 14 }}>
          <StatCard icon={DollarSign} label="Total AI Cost" value={`$${cost.total_ai_cost || 0}`} accent={T.green} />
          <StatCard icon={Activity} label="Total AI Calls" value={cost.total_ai_calls || 0} accent={T.indigo} />
          <StatCard icon={TrendingUp} label="Avg Cost/Call" value={`$${cost.avg_cost_per_call || 0}`} accent={T.violet} />
        </div>

        {costData?.agent_costs?.length > 0 && (
          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px" }}>
            <div style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 14 }}>Cost by Agent</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {costData.agent_costs.slice(0, 10).map((ac, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 11, color: T.zinc, width: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flexShrink: 0 }}>{ac.agent}</span>
                  <Bar value={ac.total_cost} max={costData.agent_costs[0]?.total_cost || 1} color={T.teal} />
                  <span style={{ fontSize: 11, color: "#fff", fontFamily: "monospace", width: 56, textAlign: "right", flexShrink: 0 }}>${ac.total_cost}</span>
                  <span style={{ fontSize: 10, color: T.zinc, width: 52, textAlign: "right", flexShrink: 0 }}>{ac.call_count} calls</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Custom KPIs */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: T.zinc, textTransform: "uppercase", letterSpacing: ".1em" }}>Custom KPIs</div>
          <button
            onClick={() => setShowAddKpi(!showAddKpi)}
            data-testid="add-kpi-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: showAddKpi ? "rgba(239,68,68,.08)" : "rgba(79,209,197,.08)", border: `1px solid ${showAddKpi ? "rgba(239,68,68,.25)" : "rgba(79,209,197,.25)"}`, color: showAddKpi ? T.red : T.teal, fontSize: 11, fontWeight: 600, cursor: "pointer" }}
          >
            {showAddKpi ? <><X size={12} /> Cancel</> : <><Plus size={12} /> Add KPI</>}
          </button>
        </div>

        {showAddKpi && (
          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px", marginBottom: 14 }}>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "flex-end" }}>
              <div style={{ flex: 1, minWidth: 120 }}>
                <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Name</label>
                <input value={newKpi.name} onChange={e => setNewKpi({ ...newKpi, name: e.target.value })} style={formInput} placeholder="Revenue" data-testid="kpi-name-input" />
              </div>
              <div style={{ width: 90 }}>
                <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Value</label>
                <input type="number" value={newKpi.value} onChange={e => setNewKpi({ ...newKpi, value: parseFloat(e.target.value) || 0 })} style={formInput} />
              </div>
              <div style={{ width: 90 }}>
                <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Target</label>
                <input type="number" value={newKpi.target} onChange={e => setNewKpi({ ...newKpi, target: parseFloat(e.target.value) || 0 })} style={formInput} />
              </div>
              <div style={{ width: 70 }}>
                <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Unit</label>
                <input value={newKpi.unit} onChange={e => setNewKpi({ ...newKpi, unit: e.target.value })} style={formInput} placeholder="$" />
              </div>
              <button
                onClick={addCustomKpi}
                data-testid="save-kpi-btn"
                style={{ padding: "8px 18px", borderRadius: 10, background: `linear-gradient(135deg, ${T.teal}, #14b8a6)`, border: "none", color: "#000", fontSize: 12, fontWeight: 700, cursor: "pointer" }}
              >
                Save
              </button>
            </div>
          </div>
        )}

        {kpis?.custom_kpis?.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px,1fr))", gap: 12 }}>
            {kpis.custom_kpis.map(k => {
              const pct = k.target > 0 ? Math.min(100, (k.value / k.target) * 100) : 0;
              const barColor = pct >= 100 ? T.green : pct >= 60 ? T.teal : T.amber;
              return (
                <div key={k.kpi_id} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 16px", position: "relative", overflow: "hidden" }}>
                  <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: barColor }} />
                  <div style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 4 }}>{k.name}</div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: "#fff", fontFamily: "'Outfit',sans-serif", lineHeight: 1, marginBottom: 8 }}>{k.unit}{k.value}</div>
                  {k.target > 0 && (
                    <>
                      <Bar value={k.value} max={k.target} color={barColor} />
                      <div style={{ fontSize: 10, color: T.zinc, marginTop: 4 }}>Target: {k.unit}{k.target}</div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        ) : !showAddKpi && (
          <div style={{ textAlign: "center", padding: "40px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
            <Target size={36} style={{ color: "rgba(255,255,255,.08)", marginBottom: 12 }} />
            <p style={{ fontSize: 13, color: T.zinc }}>No custom KPIs yet. Add revenue, CAC, LTV, and more.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default KPIDashboard;
