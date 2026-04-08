import { useState, useEffect, useCallback } from "react";
import { Briefcase, Target, Plus } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#7c3aed",
  indigo: "#818cf8",
  green: "#34d399",
  red: "#ef4444",
  cyan: "#22d3ee",
  amber: "#f59e0b",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
`;

const STAGE_META = {
  idea: { color: T.zinc, bg: "rgba(113,113,122,.15)" },
  validation: { color: "#60a5fa", bg: "rgba(96,165,250,.15)" },
  mvp: { color: T.cyan, bg: "rgba(34,211,238,.15)" },
  growth: { color: T.green, bg: "rgba(52,211,153,.15)" },
  scale: { color: "#a78bfa", bg: "rgba(167,139,250,.15)" },
  mature: { color: T.amber, bg: "rgba(245,158,11,.15)" },
  sunset: { color: T.red, bg: "rgba(239,68,68,.15)" },
};

const ACTION_COLORS = { scale: T.green, optimize: T.cyan, pivot: T.amber, pause: "#f97316", kill: T.red };

const STAGES = ["idea","validation","mvp","growth","scale","mature","sunset"];

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

export default function VenturePortfolio() {
  const [ventures, setVentures] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", stage: "idea" });
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [v, s] = await Promise.all([f("/api/infinity/portfolio/ventures"), f("/api/infinity/portfolio/summary")]);
    if (v) setVentures(v);
    if (s) setSummary(s);
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const createVenture = async () => {
    await fetch(`${API}/api/infinity/portfolio/ventures`, { method: "POST", headers, body: JSON.stringify(form) });
    setShowCreate(false);
    setForm({ name: "", description: "", stage: "idea" });
    fetchData();
  };

  const inputFocus = e => e.target.style.borderColor = "rgba(124,58,237,.5)";
  const inputBlur = e => e.target.style.borderColor = T.border;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22, maxWidth: 900, animation: "fadeUp .4s ease" }} data-testid="venture-portfolio-page">
      <style>{STYLES}</style>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4, display: "flex", alignItems: "center", gap: 10 }}>
            <Briefcase size={22} style={{ color: "#a78bfa" }} /> Venture Portfolio
          </h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Portfolio state machine — track, score, and decide: scale / optimize / pivot / kill</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} data-testid="create-venture-btn"
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
          <Plus size={14} /> New Venture
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 10 }} data-testid="portfolio-summary">
          {[
            { label: "Ventures", value: summary.total_ventures, color: T.violet },
            { label: "Revenue", value: `$${(summary.total_revenue || 0).toLocaleString()}`, color: T.green },
            { label: "Costs", value: `$${(summary.total_costs || 0).toLocaleString()}`, color: T.red },
            { label: "Avg Score", value: (summary.avg_opportunity_score || 0).toFixed(0), color: "#fff" },
            { label: "Avg Runway", value: `${(summary.avg_runway || 0).toFixed(0)}mo`, color: T.cyan },
          ].map(s => (
            <div key={s.label} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 0", textAlign: "center" }}>
              <div style={{ fontSize: 20, fontWeight: 700, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 10, color: T.zinc, marginTop: 3 }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <div style={{ background: T.glass, border: `1px solid rgba(124,58,237,.2)`, borderRadius: 12, padding: "16px 18px", display: "flex", flexDirection: "column", gap: 10 }} data-testid="create-venture-form">
          <input placeholder="Venture name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} style={formInput} data-testid="venture-name-input" onFocus={inputFocus} onBlur={inputBlur} />
          <input placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} style={formInput} data-testid="venture-desc-input" onFocus={inputFocus} onBlur={inputBlur} />
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <select value={form.stage} onChange={e => setForm({...form, stage: e.target.value}) } style={{ ...formInput, cursor: "pointer", width: "auto" }} data-testid="venture-stage-select">
              {STAGES.map(s => <option key={s} value={s} style={{ background: "#0f0f1a" }}>{s}</option>)}
            </select>
            <button onClick={createVenture} data-testid="submit-venture-btn"
              style={{ padding: "8px 18px", borderRadius: 9, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
              Create
            </button>
          </div>
        </div>
      )}

      {/* Ventures grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 14 }} data-testid="ventures-grid">
        {ventures.length === 0 ? (
          <p style={{ fontSize: 13, color: T.zinc, textAlign: "center", padding: "32px 0", gridColumn: "1 / -1" }}>No ventures yet. Create your first venture to get started.</p>
        ) : ventures.map((v, i) => {
          const sm = STAGE_META[v.stage] || STAGE_META.idea;
          const actionColor = ACTION_COLORS[v.next_action] || T.zinc;
          const profit = (v.revenue || 0) - (v.costs || 0);
          return (
            <div key={i} data-testid={`venture-card-${i}`}
              style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 18px", transition: "border-color .2s" }}
              onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
              onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>{v.name}</h3>
                <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 20, background: sm.bg, color: sm.color }}>{v.stage}</span>
              </div>
              <p style={{ fontSize: 12, color: T.zinc, marginBottom: 12 }}>{v.description}</p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8, marginBottom: 10 }}>
                {[
                  { label: "Revenue", value: `$${(v.revenue || 0).toLocaleString()}`, color: T.green },
                  { label: "Costs", value: `$${(v.costs || 0).toLocaleString()}`, color: T.red },
                  { label: "Score", value: v.opportunity_score || 0, color: profit >= 0 ? T.green : T.amber },
                ].map(s => (
                  <div key={s.label} style={{ textAlign: "center", padding: "8px 6px", borderRadius: 8, background: "rgba(255,255,255,.03)" }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: s.color }}>{s.value}</div>
                    <div style={{ fontSize: 9, color: T.zinc }}>{s.label}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <Target size={11} style={{ color: T.zinc }} />
                  <span style={{ fontSize: 11, fontWeight: 700, color: actionColor }}>{v.next_action?.toUpperCase()}</span>
                </div>
                <span style={{ fontSize: 10, color: T.zinc }}>Runway: {v.runway_months || 0}mo</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
