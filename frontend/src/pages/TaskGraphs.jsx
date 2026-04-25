import { useState, useEffect } from "react";
import { useAuth } from "../App";
import {
  GitBranch, Plus, ChevronRight, Clock, AlertCircle,
  CheckCircle2, Loader2, Layers, Zap, Target, AlertTriangle
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

/* ─── Design tokens ─────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  green:  "#34d399",
  amber:  "#f59e0b",
  red:    "#f87171",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
};

const STATUS_MAP = {
  draft:     { color: "#64748b", label: "Draft",     bg: "rgba(100,116,139,0.1)" },
  active:    { color: "#34d399", label: "Active",    bg: "rgba(52,211,153,0.1)"  },
  completed: { color: "#60a5fa", label: "Done",      bg: "rgba(96,165,250,0.1)"  },
  failed:    { color: "#f87171", label: "Failed",    bg: "rgba(248,113,113,0.1)" },
  paused:    { color: "#f59e0b", label: "Paused",    bg: "rgba(245,158,11,0.1)"  },
};

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes tg_fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
  @keyframes tg_spin   { to { transform: rotate(360deg); } }
  @keyframes tg_pulse  { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(1.5); } }
`;

export default function TaskGraphs() {
  const { token } = useAuth();
  const [graphs, setGraphs]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm]       = useState({ title: "", objective: "", scope: "", timeline: "" });
  const [open, setOpen]       = useState(false);

  const fetchGraphs = async () => {
    try {
      const res = await fetch(`${API}/api/kernel/task-graphs`, { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      setGraphs(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchGraphs(); }, [token]);

  const createGraph = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await fetch(`${API}/api/kernel/task-graphs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...form, nodes: [], edges: [] }),
      });
      setForm({ title: "", objective: "", scope: "", timeline: "" });
      setOpen(false);
      fetchGraphs();
    } catch (e) { console.error(e); }
    setCreating(false);
  };

  const formField = (key, placeholder, span2 = false) => (
    <input
      value={form[key]}
      onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
      placeholder={placeholder}
      onKeyDown={e => e.key === "Enter" && createGraph()}
      data-testid={`graph-${key}-input`}
      style={{ gridColumn: span2 ? "1 / -1" : undefined, height: 40, paddingLeft: 12, paddingRight: 12, borderRadius: 9, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 13, outline: "none", transition: "border-color 0.15s", fontFamily: "inherit", boxSizing: "border-box" }}
      onFocus={e => e.target.style.borderColor = "rgba(79,209,197,0.35)"}
      onBlur={e => e.target.style.borderColor = T.border}
    />
  );

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256, flexDirection: "column", gap: 14 }}>
      <style>{STYLES}</style>
      <div style={{ position: "relative", width: 40, height: 40 }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid transparent", borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.25)", animation: "tg_spin 0.85s linear infinite" }} />
        <div style={{ position: "absolute", inset: 5, borderRadius: "50%", border: "2px solid transparent", borderBottomColor: T.violet, borderLeftColor: "rgba(124,58,237,0.25)", animation: "tg_spin 0.6s linear infinite reverse" }} />
      </div>
      <p style={{ fontSize: 12, color: "#475569" }}>Loading task graphs…</p>
    </div>
  );

  const counts = { total: graphs.length, active: graphs.filter(g => g.status === "active").length, completed: graphs.filter(g => g.status === "completed").length };

  return (
    <div data-testid="task-graphs" style={{ animation: "tg_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(79,209,197,0.12))", border: "1px solid rgba(124,58,237,0.2)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(124,58,237,0.1)" }}>
              <GitBranch style={{ width: 20, height: 20, color: T.violet }} />
            </div>
            <div>
              <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Task Graphs</h1>
              <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Structured decomposition with dependencies, gates, and verification</p>
            </div>
          </div>
          {/* Quick stats */}
          <div style={{ display: "flex", gap: 12, marginTop: 10 }}>
            {[
              { label: "Total",    value: counts.total,     color: "#64748b" },
              { label: "Active",   value: counts.active,    color: T.green },
              { label: "Complete", value: counts.completed, color: T.blue },
            ].map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                {s.value > 0 && <div style={{ width: 6, height: 6, borderRadius: "50%", background: s.color, animation: s.label === "Active" && s.value > 0 ? "tg_pulse 2s ease-in-out infinite" : "none" }} />}
                <span style={{ fontSize: 12, fontWeight: 700, color: s.color }}>{s.value}</span>
                <span style={{ fontSize: 11, color: "#334155" }}>{s.label}</span>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={() => setOpen(v => !v)}
          style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 18px", borderRadius: 11, background: open ? "rgba(79,209,197,0.12)" : `linear-gradient(135deg, ${T.teal}, ${T.blue})`, color: open ? T.teal : "#030712", fontSize: 13, fontWeight: 700, border: open ? `1px solid rgba(79,209,197,0.25)` : "none", cursor: "pointer", transition: "all 0.2s", boxShadow: open ? "none" : "0 0 24px rgba(79,209,197,0.2)" }}>
          <Plus style={{ width: 14, height: 14 }} /> New Graph
        </button>
      </div>

      {/* ── Create form (collapsible) ────────────────────────────────────── */}
      {open && (
        <div style={{ borderRadius: 16, border: `1px solid rgba(79,209,197,0.2)`, background: T.glass, backdropFilter: "blur(16px)", padding: 20, marginBottom: 24, animation: "tg_fadeUp 0.2s ease" }}
          data-testid="create-graph-form">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Zap style={{ width: 13, height: 13, color: T.teal }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>New Task Graph</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            {formField("title",    "Title *")}
            {formField("timeline", "Timeline (e.g. 2 weeks)")}
            {formField("objective","Objective",  true)}
          </div>
          <button
            onClick={createGraph}
            disabled={creating || !form.title.trim()}
            data-testid="create-graph-btn"
            style={{ display: "flex", alignItems: "center", gap: 7, padding: "9px 20px", borderRadius: 10, background: creating || !form.title.trim() ? "rgba(79,209,197,0.08)" : `linear-gradient(135deg, ${T.teal}, ${T.blue})`, border: "none", color: creating || !form.title.trim() ? T.teal : "#030712", fontSize: 12, fontWeight: 700, cursor: creating || !form.title.trim() ? "default" : "pointer", opacity: !form.title.trim() ? 0.5 : 1, transition: "all 0.2s" }}>
            {creating
              ? <><Loader2 style={{ width: 13, height: 13, animation: "tg_spin 1s linear infinite" }} /> Creating…</>
              : <><Plus style={{ width: 13, height: 13 }} /> Create Graph</>}
          </button>
        </div>
      )}

      {/* ── Graphs list ─────────────────────────────────────────────────── */}
      {graphs.length === 0 ? (
        <div style={{ padding: "64px 0", textAlign: "center", border: "1px dashed rgba(124,58,237,0.12)", borderRadius: 20, background: "rgba(124,58,237,0.02)" }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(124,58,237,0.08)", border: "1px solid rgba(124,58,237,0.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
            <GitBranch style={{ width: 28, height: 28, color: T.violet, opacity: 0.6 }} />
          </div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#e2e8f0", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>No Task Graphs Yet</h3>
          <p style={{ fontSize: 12, color: "#475569", marginBottom: 20 }}>Create structured workflows with dependencies, approval gates, and verification rules.</p>
          <button onClick={() => setOpen(true)}
            style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "10px 20px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.blue})`, color: "#f1f5f9", fontSize: 12, fontWeight: 700, border: "none", cursor: "pointer", boxShadow: "0 0 24px rgba(124,58,237,0.25)" }}>
            <Plus style={{ width: 13, height: 13 }} /> Create First Graph
          </button>
        </div>
      ) : (
        <div data-testid="graphs-list" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {graphs.map(g => {
            const st = STATUS_MAP[g.status] || STATUS_MAP.draft;
            return (
              <GraphCard key={g.id || g.title} graph={g} status={st} />
            );
          })}
        </div>
      )}
    </div>
  );
}

function GraphCard({ graph: g, status: st }) {
  const [hovered, setHovered] = useState(false);
  const nodeCount = g.nodes?.length || 0;
  const completedNodes = g.nodes?.filter(n => n.status === "completed")?.length || 0;
  const pct = nodeCount > 0 ? Math.round((completedNodes / nodeCount) * 100) : 0;

  return (
    <div
      data-testid={`graph-item-${g.id}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 16px", borderRadius: 14, background: hovered ? "rgba(79,209,197,0.04)" : "rgba(8,15,28,0.65)", border: `1px solid ${hovered ? "rgba(79,209,197,0.2)" : "rgba(255,255,255,0.07)"}`, backdropFilter: "blur(12px)", transition: "all 0.18s", cursor: "pointer" }}>
      {/* Icon */}
      <div style={{ width: 40, height: 40, borderRadius: 11, background: `${st.color}14`, border: `1px solid ${st.color}22`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <GitBranch style={{ width: 17, height: 17, color: st.color }} />
      </div>

      {/* Info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
          <h4 style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", margin: 0 }}>{g.title}</h4>
          <span style={{ padding: "1px 7px", borderRadius: 20, background: st.bg, color: st.color, fontSize: 9, fontWeight: 700, flexShrink: 0 }}>{st.label}</span>
        </div>
        {g.objective && <p style={{ fontSize: 11, color: "#475569", margin: "0 0 6px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{g.objective}</p>}
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          {g.timeline && (
            <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: "#475569" }}>
              <Clock style={{ width: 10, height: 10 }} /> {g.timeline}
            </span>
          )}
          <span style={{ fontSize: 10, color: "#334155" }}>
            <Layers style={{ width: 10, height: 10, display: "inline", marginRight: 3 }} />{nodeCount} nodes
          </span>
          <span style={{ fontSize: 10, color: "#334155" }}>v{g.version || 1}</span>
          {g.risk_score > 0 && (
            <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 10, color: "#f59e0b" }}>
              <AlertCircle style={{ width: 10, height: 10 }} /> Risk: {g.risk_score}
            </span>
          )}
        </div>
        {/* Progress bar */}
        {nodeCount > 0 && (
          <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ flex: 1, height: 3, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
              <div style={{ height: "100%", borderRadius: 2, background: `linear-gradient(90deg, ${st.color}, ${st.color}80)`, width: `${pct}%`, transition: "width 0.6s ease" }} />
            </div>
            <span style={{ fontSize: 9, color: "#475569", flexShrink: 0 }}>{pct}%</span>
          </div>
        )}
      </div>

      <ChevronRight style={{ width: 14, height: 14, color: "#334155", flexShrink: 0, transition: "transform 0.15s", transform: hovered ? "translateX(2px)" : "none" }} />
    </div>
  );
}
