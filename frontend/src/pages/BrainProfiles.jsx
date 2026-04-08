import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Brain, Shield, ChevronRight, Save, RotateCcw,
  Cpu, Lock, Unlock, AlertTriangle, Target, Gauge, X, Search
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const MEMORY_SCOPES = [
  { id: "working", label: "Working", desc: "Short-term task memory" },
  { id: "long_term", label: "Long-Term", desc: "Persistent across sessions" },
  { id: "domain", label: "Domain", desc: "Specialized knowledge" },
  { id: "shared", label: "Shared", desc: "Cross-agent access" },
];

const AUTONOMY_LABELS = { 0: "None", 1: "Minimal", 2: "Low", 3: "Medium", 4: "High", 5: "Full" };
const AUTONOMY_COLORS = {
  0: T.zinc, 1: "#ef4444", 2: "#f97316", 3: T.amber, 4: T.indigo, 5: T.green,
};

const Panel = ({ title, icon: Icon, iconColor, children, testId }) => (
  <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }} data-testid={testId}>
    {title && (
      <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 12 }}>
        {Icon && <Icon size={13} style={{ color: iconColor || T.zinc }} />}
        <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>{title}</span>
      </div>
    )}
    {children}
  </div>
);

const Toggle = ({ on, onChange, testId }) => (
  <button
    onClick={onChange}
    data-testid={testId}
    style={{
      width: 38, height: 20, borderRadius: 10, border: "none", cursor: "pointer",
      background: on ? T.green : "rgba(255,255,255,.1)", position: "relative", transition: "background .2s",
    }}
  >
    <div style={{
      width: 14, height: 14, borderRadius: 7, background: "#fff", position: "absolute",
      top: 3, left: on ? 21 : 3, transition: "left .2s",
    }} />
  </button>
);

const BrainProfileCard = ({ profile, onSelect }) => {
  const autonomy = profile.autonomy_level || 3;
  const aColor = AUTONOMY_COLORS[autonomy];
  return (
    <button
      onClick={() => onSelect(profile.agent_id)}
      data-testid={`brain-card-${profile.agent_id}`}
      style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", cursor: "pointer", textAlign: "left", transition: "border-color .2s", width: "100%" }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.15)"}
      onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        {profile.agent_avatar
          ? <img src={profile.agent_avatar} alt="" style={{ width: 38, height: 38, borderRadius: 10, objectFit: "cover" }} />
          : <div style={{ width: 38, height: 38, borderRadius: 10, background: "rgba(129,140,248,.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: T.indigo }}>{(profile.agent_name || "?").slice(0, 2).toUpperCase()}</div>
        }
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{profile.agent_name}</div>
          <div style={{ fontSize: 10, color: T.zinc }}>{profile.agent_role}</div>
        </div>
        {profile.is_custom && (
          <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid rgba(129,140,248,.3)`, color: T.indigo, fontWeight: 700 }}>Custom</span>
        )}
        <ChevronRight size={14} style={{ color: T.zinc }} />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <Gauge size={11} style={{ color: T.zinc }} />
          <span style={{ color: "#a1a1aa" }}>Autonomy: {autonomy}/5</span>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: aColor }} />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {profile.approval_required
            ? <><Lock size={11} style={{ color: T.amber }} /><span style={{ color: T.amber }}>Approval</span></>
            : <><Unlock size={11} style={{ color: T.green }} /><span style={{ color: T.green }}>Auto</span></>
          }
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <Cpu size={11} style={{ color: T.zinc }} />
          <span style={{ color: "#a1a1aa" }}>{profile.primary_model?.model || "gpt-5.2"}</span>
        </div>
      </div>
      {profile.communication_style && (
        <div style={{ fontSize: 10, color: T.zinc, marginTop: 6, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>Style: {profile.communication_style}</div>
      )}
    </button>
  );
};

const BrainEditor = ({ agentId, onClose }) => {
  const { token } = useAuth();
  const [brain, setBrain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [edited, setEdited] = useState({});

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/agents/${agentId}/brain`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) { const data = await res.json(); setBrain(data); setEdited(data); }
      } catch {} finally { setLoading(false); }
    })();
  }, [agentId, token]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/agents/${agentId}/brain`, {
        method: "PUT", headers,
        body: JSON.stringify({
          autonomy_level: edited.autonomy_level, approval_required: edited.approval_required,
          communication_style: edited.communication_style, memory_scopes: edited.memory_scopes,
          kpis: edited.kpis, escalation_rules: edited.escalation_rules,
          risk_boundaries: edited.risk_boundaries, primary_model: edited.primary_model,
          fallback_models: edited.fallback_models, output_templates: edited.output_templates,
        }),
      });
      if (res.ok) { toast.success("Brain profile saved"); setBrain(await res.json()); }
      else toast.error("Failed to save");
    } catch { toast.error("Error saving"); }
    finally { setSaving(false); }
  };

  const handleReset = async () => {
    if (!window.confirm("Reset to default brain profile?")) return;
    try {
      await fetch(`${API}/agents/${agentId}/brain`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      toast.success("Reset to defaults"); onClose();
    } catch { toast.error("Reset failed"); }
  };

  const updateField = (field, value) => setEdited(prev => ({ ...prev, [field]: value }));

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 240 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );
  if (!brain) return null;

  const autonomy = edited.autonomy_level ?? 3;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, animation: "fadeUp .3s ease" }} data-testid="brain-editor">
      <style>{STYLES}</style>
      {/* Editor header */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <button onClick={onClose} style={{ background: "transparent", border: `1px solid ${T.border}`, borderRadius: 8, padding: "5px 8px", color: T.zinc, cursor: "pointer", display: "flex", alignItems: "center" }}>
          <X size={14} />
        </button>
        <Brain size={18} style={{ color: T.indigo }} />
        <h2 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>Custom Brain Profile</h2>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {brain.is_custom && (
            <button onClick={handleReset} style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 12px", borderRadius: 8, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 12, cursor: "pointer" }}
              onMouseEnter={e => e.currentTarget.style.color = T.red}
              onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
              <RotateCcw size={12} /> Reset
            </button>
          )}
          <button onClick={handleSave} disabled={saving} data-testid="save-brain-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 14px", borderRadius: 8, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? .7 : 1 }}>
            <Save size={12} /> {saving ? "Saving…" : "Save"}
          </button>
        </div>
      </div>

      {/* Autonomy */}
      <Panel title="Autonomy Level" icon={Gauge} iconColor={T.indigo}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <span style={{ fontSize: 13, color: "#fff" }}>Level {autonomy}/5</span>
          <span style={{ fontSize: 11, fontWeight: 700, color: AUTONOMY_COLORS[autonomy], background: `${AUTONOMY_COLORS[autonomy]}20`, padding: "2px 9px", borderRadius: 5 }}>{AUTONOMY_LABELS[autonomy]}</span>
        </div>
        <input type="range" min="0" max="5" step="1" value={autonomy} onChange={e => updateField("autonomy_level", parseInt(e.target.value))}
          style={{ width: "100%", accentColor: T.indigo }} data-testid="autonomy-slider" />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: T.zinc, marginTop: 3 }}>
          {Object.values(AUTONOMY_LABELS).map(v => <span key={v}>{v}</span>)}
        </div>
      </Panel>

      {/* Approval */}
      <Panel title="Approval Required" icon={Shield} iconColor={T.amber}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 12, color: edited.approval_required ? T.amber : T.zinc }}>
            {edited.approval_required ? "Actions require your approval before execution" : "Agent can execute autonomously"}
          </span>
          <Toggle on={edited.approval_required} onChange={() => updateField("approval_required", !edited.approval_required)} testId="approval-toggle" />
        </div>
      </Panel>

      {/* Communication Style */}
      <Panel title="Communication Style">
        <input type="text" value={edited.communication_style || ""} onChange={e => updateField("communication_style", e.target.value)}
          placeholder="e.g. Professional, data-driven, concise" style={formInput}
          data-testid="communication-style-input"
          onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
          onBlur={e => e.target.style.borderColor = T.border} />
      </Panel>

      {/* Memory Scopes */}
      <Panel title="Memory Scopes">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {MEMORY_SCOPES.map(scope => {
            const active = (edited.memory_scopes || []).includes(scope.id);
            return (
              <button key={scope.id} data-testid={`memory-${scope.id}`}
                onClick={() => {
                  const cur = edited.memory_scopes || [];
                  updateField("memory_scopes", active ? cur.filter(s => s !== scope.id) : [...cur, scope.id]);
                }}
                style={{ padding: "9px 12px", borderRadius: 9, border: `1px solid ${active ? "rgba(129,140,248,.3)" : T.border}`, background: active ? "rgba(129,140,248,.08)" : T.glass, cursor: "pointer", textAlign: "left", transition: "all .2s" }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: active ? T.indigo : "#e4e4e7" }}>{scope.label}</div>
                <div style={{ fontSize: 9, color: T.zinc }}>{scope.desc}</div>
              </button>
            );
          })}
        </div>
      </Panel>

      {/* KPIs */}
      <Panel title="KPIs" icon={Target} iconColor={T.green}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 8 }}>
          {(edited.kpis || []).map((kpi, i) => (
            <span key={i} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, padding: "3px 8px", borderRadius: 5, background: "rgba(52,211,153,.1)", border: `1px solid rgba(52,211,153,.2)`, color: T.green }}>
              <Target size={9} /> {kpi}
              <button onClick={() => updateField("kpis", edited.kpis.filter((_, j) => j !== i))} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 0, lineHeight: 1, marginLeft: 2 }}
                onMouseEnter={e => e.currentTarget.style.color = T.red}
                onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                <X size={9} />
              </button>
            </span>
          ))}
        </div>
        <input placeholder="Add a KPI and press Enter" style={formInput} data-testid="kpi-input"
          onFocus={e => e.target.style.borderColor = "rgba(52,211,153,.4)"}
          onBlur={e => e.target.style.borderColor = T.border}
          onKeyDown={e => { if (e.key === "Enter" && e.target.value.trim()) { updateField("kpis", [...(edited.kpis || []), e.target.value.trim()]); e.target.value = ""; } }} />
      </Panel>

      {/* Escalation Rules */}
      <Panel title="Escalation Rules" icon={AlertTriangle} iconColor={T.amber}>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 8 }}>
          {(edited.escalation_rules || []).map((rule, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#d4d4d8", background: "rgba(255,255,255,.03)", borderRadius: 8, padding: "7px 10px" }}>
              <AlertTriangle size={11} style={{ color: T.amber, flexShrink: 0 }} />
              <span style={{ flex: 1 }}>{rule}</span>
              <button onClick={() => updateField("escalation_rules", edited.escalation_rules.filter((_, j) => j !== i))} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 0 }}
                onMouseEnter={e => e.currentTarget.style.color = T.red}
                onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
        <input placeholder="Add an escalation rule and press Enter" style={formInput} data-testid="escalation-input"
          onFocus={e => e.target.style.borderColor = "rgba(245,158,11,.4)"}
          onBlur={e => e.target.style.borderColor = T.border}
          onKeyDown={e => { if (e.key === "Enter" && e.target.value.trim()) { updateField("escalation_rules", [...(edited.escalation_rules || []), e.target.value.trim()]); e.target.value = ""; } }} />
      </Panel>

      {/* Risk Boundaries */}
      <Panel title="Risk Boundaries" icon={Shield} iconColor={T.red}>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Max Budget Authority ($)</label>
            <input type="number" value={edited.risk_boundaries?.max_budget_authority || 0}
              onChange={e => updateField("risk_boundaries", { ...edited.risk_boundaries, max_budget_authority: parseInt(e.target.value) || 0 })}
              style={formInput} data-testid="budget-authority-input"
              onFocus={e => e.target.style.borderColor = "rgba(239,68,68,.4)"}
              onBlur={e => e.target.style.borderColor = T.border} />
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 12, color: "#a1a1aa" }}>Can Approve External Communications</span>
            <Toggle on={edited.risk_boundaries?.can_approve_external_comms}
              onChange={() => updateField("risk_boundaries", { ...edited.risk_boundaries, can_approve_external_comms: !edited.risk_boundaries?.can_approve_external_comms })}
              testId="external-comms-toggle" />
          </div>
        </div>
      </Panel>
    </div>
  );
};

const BrainProfiles = () => {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [search, setSearch] = useState("");

  const fetchProfiles = useCallback(async () => {
    try {
      const res = await fetch(`${API}/brain-profiles`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); setProfiles(data.profiles || []); }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchProfiles(); }, [fetchProfiles]);

  const filtered = profiles.filter(p =>
    !search || p.agent_name?.toLowerCase().includes(search.toLowerCase()) || p.agent_role?.toLowerCase().includes(search.toLowerCase())
  );

  if (selectedAgent) {
    return <BrainEditor agentId={selectedAgent} onClose={() => { setSelectedAgent(null); fetchProfiles(); }} />;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="brain-profiles-page">
      <style>{STYLES}</style>

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(129,140,248,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Brain size={22} style={{ color: T.indigo }} />
        </div>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }}>Custom Brain Profiles</h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Configure each agent's AI brain, autonomy, memory, and behavior</p>
        </div>
      </div>

      <div style={{ position: "relative" }}>
        <Search size={13} style={{ position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
        <input type="text" placeholder="Search agents..." value={search} onChange={e => setSearch(e.target.value)}
          data-testid="brain-search"
          style={{ paddingLeft: 32, paddingRight: 12, paddingTop: 9, paddingBottom: 9, background: T.glass, border: `1px solid ${T.border}`, borderRadius: 10, color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }} />
      </div>

      {loading ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200 }}>
          <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px" }}>
          <Brain size={48} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
          <p style={{ fontSize: 13, color: T.zinc }}>No agents found</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
          {filtered.map(profile => (
            <BrainProfileCard key={profile.agent_id} profile={profile} onSelect={setSelectedAgent} />
          ))}
        </div>
      )}
    </div>
  );
};

export default BrainProfiles;
