import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../App";
import { Globe, Shield, Zap, Check, AlertTriangle, ArrowRight } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  amber: "#f59e0b",
  green: "#34d399",
  blue: "#60a5fa",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

const ENV_ICONS = { sandbox: AlertTriangle, staging: Shield, production: Zap };
const ENV_ACCENT = { sandbox: T.amber, staging: T.blue, production: T.green };

export default function Environments() {
  const { token } = useAuth();
  const [data, setData] = useState({ environments: {}, active: "sandbox", stats: {} });
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  const fetchData = useCallback(() => {
    fetch(`${API}/api/kernel/environments`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const switchEnv = async (env) => {
    setSwitching(true);
    const res = await fetch(`${API}/api/kernel/environments/active`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ environment: env }),
    });
    if (res.ok) setData(prev => ({ ...prev, active: env }));
    setSwitching(false);
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.blue}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const envs = data.environments || {};
  const active = data.active;
  const stats = data.stats || {};
  const activeAccent = ENV_ACCENT[active] || T.teal;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="environments-page">
      <style>{STYLES}</style>

      {/* Header */}
      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Environment Segregation</h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Manage execution environments — sandbox for testing, staging for validation, production for live operations</p>
      </div>

      {/* Active Environment Banner */}
      <div
        data-testid="active-env-banner"
        style={{ padding: "16px 20px", borderRadius: 14, background: `${activeAccent}08`, border: `1px solid ${activeAccent}30` }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: activeAccent, animation: "pulse 1.5s infinite" }} />
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>
              Active Environment: <span style={{ color: activeAccent }}>{envs[active]?.name || active}</span>
            </p>
            <p style={{ fontSize: 11, color: T.zinc, margin: "2px 0 0" }}>{envs[active]?.description}</p>
          </div>
        </div>
      </div>

      {/* Environment Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }} data-testid="env-cards">
        {Object.entries(envs).map(([key, env]) => {
          const isActive = key === active;
          const Icon = ENV_ICONS[key] || Globe;
          const accent = ENV_ACCENT[key] || T.teal;
          const limits = env.limits || {};
          return (
            <div
              key={key}
              data-testid={`env-card-${key}`}
              style={{
                position: "relative", padding: "20px", borderRadius: 16, overflow: "hidden",
                background: T.glass, border: `1px solid ${isActive ? `${accent}40` : T.border}`,
                boxShadow: isActive ? `0 0 0 1px ${accent}20` : "none",
                transition: "border-color .2s",
              }}
              onMouseEnter={e => !isActive && (e.currentTarget.style.borderColor = "rgba(255,255,255,.14)")}
              onMouseLeave={e => !isActive && (e.currentTarget.style.borderColor = T.border)}
            >
              {/* Top accent */}
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent }} />

              {/* Icon + name */}
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: `${accent}15`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Icon size={20} style={{ color: accent }} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>{env.name}</div>
                  <div style={{ fontSize: 10, color: T.zinc }}>{stats[key]?.users || 0} active users</div>
                </div>
                {isActive && (
                  <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, fontWeight: 700, color: accent, background: `${accent}15`, padding: "3px 10px", borderRadius: 8 }}>
                    <Check size={11} /> Active
                  </span>
                )}
              </div>

              <p style={{ fontSize: 12, color: T.zinc, marginBottom: 16, lineHeight: 1.5 }}>{env.description}</p>

              {/* Limits */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
                {[
                  ["Max Agents", limits.max_agents],
                  ["Max Cost/Run", `$${limits.max_cost_per_run?.toFixed(2)}`],
                  ["Real Actions", limits.real_actions ? "Enabled" : "Dry Run Only", limits.real_actions ? T.green : T.amber],
                ].map(([label, val, vc]) => (
                  <div key={label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span style={{ fontSize: 11, color: T.zinc }}>{label}</span>
                    <span style={{ fontSize: 11, fontWeight: 600, color: vc || "#fff" }}>{val}</span>
                  </div>
                ))}
              </div>

              {!isActive && (
                <button
                  onClick={() => switchEnv(key)}
                  disabled={switching}
                  data-testid={`switch-to-${key}`}
                  style={{ width: "100%", padding: "9px 0", borderRadius: 10, background: `${accent}20`, border: `1px solid ${accent}40`, color: accent, fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
                >
                  <ArrowRight size={13} /> Switch to {env.name}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Comparison Table */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 16, padding: "20px 22px" }} data-testid="env-comparison">
        <div style={{ fontSize: 13, fontWeight: 600, color: "#fff", marginBottom: 16 }}>Environment Comparison</div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${T.border}` }}>
                <th style={{ textAlign: "left", color: T.zinc, paddingBottom: 10, paddingRight: 20, fontWeight: 500 }}>Feature</th>
                {Object.entries(envs).map(([key, env]) => (
                  <th key={key} style={{ textAlign: "center", paddingBottom: 10, paddingLeft: 16, paddingRight: 16, color: ENV_ACCENT[key] || T.teal, fontWeight: 700 }}>{env.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { label: "Agent Limit", fn: (l) => l.max_agents },
                { label: "Cost Limit", fn: (l) => `$${l.max_cost_per_run?.toFixed(2)}` },
                { label: "Real Actions", fn: (l) => l.real_actions ? "Yes" : "No" },
                { label: "Data Persistence", fn: (_, k) => k === "sandbox" ? "Session" : k === "staging" ? "7 days" : "Permanent" },
                { label: "Audit Logging", fn: (_, k) => k === "sandbox" ? "Basic" : k === "staging" ? "Full" : "Full + Compliance" },
                { label: "Integrations", fn: (_, k) => k === "sandbox" ? "Mocked" : k === "staging" ? "Limited" : "All Active" },
              ].map((row, i) => (
                <tr key={i} style={{ borderBottom: `1px solid rgba(255,255,255,.03)` }}>
                  <td style={{ padding: "9px 20px 9px 0", color: T.zinc }}>{row.label}</td>
                  {Object.entries(envs).map(([key, env]) => (
                    <td key={key} style={{ padding: "9px 16px", textAlign: "center", color: "#d4d4d8" }}>{row.fn(env.limits || {}, key)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
