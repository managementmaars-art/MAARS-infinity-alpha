import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../App";
import {
  Activity, AlertTriangle, CheckCircle, XCircle, Clock,
  RotateCcw, Settings, Zap, Shield, Save, X
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

const STATE_META = {
  closed:      { icon: CheckCircle,  color: T.green, label: "Closed",    desc: "Healthy" },
  open:        { icon: XCircle,      color: T.red,   label: "Open",      desc: "Tripped" },
  "half-open": { icon: AlertTriangle,color: T.amber, label: "Half-Open", desc: "Testing" },
};

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes cb_fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
  @keyframes cb_spin   { to { transform: rotate(360deg); } }
  @keyframes cb_pulse  { 0%,100% { opacity:1; box-shadow:0 0 0 0 currentColor; } 60% { opacity:0.5; box-shadow:0 0 0 6px transparent; } }
  @keyframes cb_scan   { 0% { transform: translateX(-100%); } 100% { transform: translateX(400%); } }
`;

export default function CircuitBreakers() {
  const { token }               = useAuth();
  const [breakers, setBreakers] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [editing, setEditing]   = useState(null);
  const [editVals, setEditVals] = useState({});

  const fetchBreakers = useCallback(() => {
    fetch(`${API}/api/kernel/circuit-breakers/full`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setBreakers(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchBreakers(); }, [fetchBreakers]);

  const resetBreaker = async (id) => {
    await fetch(`${API}/api/kernel/circuit-breakers/${id}/reset`, {
      method: "POST", headers: { Authorization: `Bearer ${token}` },
    });
    fetchBreakers();
  };

  const startEdit = (cb) => {
    setEditing(cb.breaker_id);
    setEditVals({ failure_threshold: cb.failure_threshold, reset_timeout_s: cb.reset_timeout_s });
  };

  const updateBreaker = async (id) => {
    await fetch(`${API}/api/kernel/circuit-breakers/${id}`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(editVals),
    });
    setEditing(null);
    fetchBreakers();
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256, flexDirection: "column", gap: 14 }}>
      <style>{STYLES}</style>
      <div style={{ position: "relative", width: 40, height: 40 }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid transparent", borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.25)", animation: "cb_spin 0.85s linear infinite" }} />
        <div style={{ position: "absolute", inset: 5, borderRadius: "50%", border: "2px solid transparent", borderBottomColor: T.violet, borderLeftColor: "rgba(124,58,237,0.25)", animation: "cb_spin 0.6s linear infinite reverse" }} />
      </div>
      <p style={{ fontSize: 12, color: "#475569" }}>Loading circuit breakers…</p>
    </div>
  );

  const closedCount   = breakers.filter(b => b.state === "closed").length;
  const openCount     = breakers.filter(b => b.state === "open").length;
  const halfOpenCount = breakers.filter(b => b.state === "half-open").length;

  const summaryItems = [
    { icon: CheckCircle,  count: closedCount,   color: T.green, label: "Closed",    sub: "Healthy" },
    { icon: XCircle,      count: openCount,     color: T.red,   label: "Open",      sub: "Tripped" },
    { icon: AlertTriangle,count: halfOpenCount, color: T.amber, label: "Half-Open", sub: "Testing" },
  ];

  return (
    <div data-testid="circuit-breakers-page" style={{ animation: "cb_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, rgba(248,113,113,0.2), rgba(245,158,11,0.12))", border: "1px solid rgba(248,113,113,0.2)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(248,113,113,0.1)" }}>
          <Shield style={{ width: 20, height: 20, color: T.red }} />
        </div>
        <div>
          <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Circuit Breakers</h1>
          <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Service protection circuits — {breakers.length} monitors across MAARS infrastructure</p>
        </div>
      </div>

      {/* ── Summary stat cards ──────────────────────────────────────────── */}
      <div data-testid="cb-summary" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 24 }}>
        {summaryItems.map((s, i) => {
          const Icon = s.icon;
          return (
            <div key={i} style={{ padding: "14px 16px", borderRadius: 14, background: T.glass, border: `1px solid ${s.color}22`, backdropFilter: "blur(12px)", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color, opacity: 0.5 }} />
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: `${s.color}12`, border: `1px solid ${s.color}20`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon style={{ width: 17, height: 17, color: s.color }} />
                </div>
                <div>
                  <p style={{ fontSize: 22, fontWeight: 800, color: s.color, fontFamily: "Outfit, sans-serif", lineHeight: 1, margin: 0 }}>{s.count}</p>
                  <p style={{ fontSize: 10, color: "#475569", margin: 0 }}>{s.label} · {s.sub}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Breaker cards ───────────────────────────────────────────────── */}
      <div data-testid="cb-list" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 12 }}>
        {breakers.map(cb => {
          const st      = STATE_META[cb.state] || STATE_META.closed;
          const Icon    = st.icon;
          const isOpen  = cb.state === "open";
          const pct     = Math.min(100, Math.round((cb.failures / Math.max(cb.failure_threshold, 1)) * 100));
          const isEditing = editing === cb.breaker_id;

          return (
            <div key={cb.breaker_id} data-testid={`cb-${cb.breaker_id}`}
              style={{ padding: "16px", borderRadius: 16, background: T.glass, border: `1px solid ${isOpen ? T.red + "33" : T.border}`, backdropFilter: "blur(12px)", transition: "border-color 0.2s", position: "relative", overflow: "hidden" }}>

              {/* Top accent line */}
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, ${st.color}, transparent)`, opacity: 0.6 }} />

              {/* Scanning animation for open breakers */}
              {isOpen && (
                <div style={{ position: "absolute", top: 0, bottom: 0, left: 0, width: 40, background: `linear-gradient(90deg, transparent, ${T.red}08, transparent)`, animation: "cb_scan 3s ease-in-out infinite" }} />
              )}

              {/* Header row */}
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 38, height: 38, borderRadius: 11, background: `${st.color}12`, border: `1px solid ${st.color}25`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <Icon style={{ width: 17, height: 17, color: st.color }} />
                  </div>
                  <div>
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", margin: 0 }}>{cb.name}</p>
                    <p style={{ fontSize: 10, color: "#475569", margin: "1px 0 0" }}>{cb.description}</p>
                  </div>
                </div>
                <span style={{ padding: "2px 8px", borderRadius: 20, background: `${st.color}12`, border: `1px solid ${st.color}25`, color: st.color, fontSize: 9, fontWeight: 700, flexShrink: 0 }}>
                  {st.label}
                </span>
              </div>

              {/* Failure progress bar */}
              <div style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
                  <span style={{ fontSize: 10, color: "#475569" }}>Failure Rate</span>
                  <span style={{ fontSize: 10, color: st.color, fontWeight: 700 }}>{cb.failures}/{cb.failure_threshold}</span>
                </div>
                <div style={{ height: 4, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                  <div style={{ height: "100%", borderRadius: 2, background: pct >= 80 ? T.red : pct >= 50 ? T.amber : T.green, width: `${pct}%`, transition: "width 0.5s ease, background 0.3s ease" }} />
                </div>
              </div>

              {/* Stats row */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6, marginBottom: 14 }}>
                {[
                  { label: "Failures",  value: cb.failures },
                  { label: "Threshold", value: cb.failure_threshold },
                  { label: "Reset",     value: `${cb.reset_timeout_s}s` },
                ].map((s, i) => (
                  <div key={i} style={{ padding: "8px 6px", borderRadius: 9, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textAlign: "center" }}>
                    <p style={{ fontSize: 9, color: "#475569", margin: "0 0 3px" }}>{s.label}</p>
                    <p style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", margin: 0 }}>{s.value}</p>
                  </div>
                ))}
              </div>

              {/* Edit form or Action buttons */}
              {isEditing ? (
                <div data-testid={`cb-edit-${cb.breaker_id}`}
                  style={{ padding: 12, borderRadius: 10, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 10 }}>
                    {[
                      { label: "Failure Threshold", key: "failure_threshold", type: "number" },
                      { label: "Reset Timeout (s)", key: "reset_timeout_s",   type: "number" },
                    ].map(f => (
                      <div key={f.key}>
                        <label style={{ fontSize: 9, color: "#475569", display: "block", marginBottom: 4, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>{f.label}</label>
                        <input
                          type={f.type}
                          value={editVals[f.key] ?? ""}
                          onChange={e => setEditVals(v => ({ ...v, [f.key]: parseInt(e.target.value) || 0 }))}
                          style={{ width: "100%", height: 34, paddingLeft: 10, paddingRight: 10, borderRadius: 7, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 13, outline: "none", boxSizing: "border-box", fontFamily: "inherit" }}
                        />
                      </div>
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                    <button onClick={() => setEditing(null)}
                      style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 12px", borderRadius: 7, background: "transparent", border: `1px solid ${T.border}`, color: "#475569", fontSize: 11, cursor: "pointer" }}>
                      <X style={{ width: 11, height: 11 }} /> Cancel
                    </button>
                    <button onClick={() => updateBreaker(cb.breaker_id)}
                      style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 14px", borderRadius: 7, background: `linear-gradient(135deg, ${T.teal}, ${T.blue})`, border: "none", color: "#030712", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                      <Save style={{ width: 11, height: 11 }} /> Save
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{ display: "flex", gap: 6 }}>
                  <button onClick={() => startEdit(cb)}
                    style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 5, padding: "8px 0", borderRadius: 9, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#64748b", fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all 0.15s" }}
                    onMouseEnter={e => { e.currentTarget.style.color = "#e2e8f0"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; }}
                    onMouseLeave={e => { e.currentTarget.style.color = "#64748b"; e.currentTarget.style.borderColor = T.border; }}>
                    <Settings style={{ width: 12, height: 12 }} /> Configure
                  </button>
                  {cb.state !== "closed" && (
                    <button onClick={() => resetBreaker(cb.breaker_id)}
                      data-testid={`cb-reset-${cb.breaker_id}`}
                      style={{ display: "flex", alignItems: "center", gap: 5, padding: "8px 14px", borderRadius: 9, background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)", color: T.green, fontSize: 11, fontWeight: 700, cursor: "pointer", transition: "all 0.15s" }}
                      onMouseEnter={e => e.currentTarget.style.background = "rgba(52,211,153,0.18)"}
                      onMouseLeave={e => e.currentTarget.style.background = "rgba(52,211,153,0.1)"}>
                      <RotateCcw style={{ width: 12, height: 12 }} /> Reset
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
