import { useState, useEffect } from "react";
import { useAuth } from "../App";
import {
  Layers, Activity, Shield, Database, GitBranch, Network,
  Cpu, Clock, CheckCircle2, AlertTriangle, Zap, Server,
  Radio, Lock, RefreshCw, Radar
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── Design tokens ─────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  green:  "#34d399",
  amber:  "#f59e0b",
  red:    "#f87171",
  pink:   "#f472b6",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
};

const SUBSYSTEM_META = {
  agent_scheduler:     { icon: Activity,     color: T.teal,   label: "Agent Scheduler" },
  task_graph_runtime:  { icon: GitBranch,    color: T.violet, label: "Task Graph Runtime" },
  resource_manager:    { icon: Cpu,          color: "#60a5fa", label: "Resource Manager" },
  budget_controller:   { icon: Shield,       color: T.amber,  label: "Budget Controller" },
  execution_gateway:   { icon: Network,      color: T.green,  label: "Execution Gateway" },
  tool_registry:       { icon: Database,     color: "#a78bfa", label: "Tool Registry" },
  memory_controller:   { icon: Database,     color: "#6366f1", label: "Memory Controller" },
  policy_engine:       { icon: Lock,         color: "#f472b6", label: "Policy Engine" },
  approval_controller: { icon: CheckCircle2, color: T.green,  label: "Approval Controller" },
  failure_recovery:    { icon: RefreshCw,    color: T.amber,  label: "Failure Recovery" },
  circuit_breakers:    { icon: AlertTriangle,color: T.red,    label: "Circuit Breakers" },
};

const METRIC_COLORS = [T.teal, T.blue, T.violet, T.amber, "#06b6d4", "#f472b6", "#6366f1", "#f97316"];
const TIER_COLORS   = ["#34d399","#60a5fa","#a78bfa","#f59e0b","#f87171","#f472b6"];

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes kd_fadeUp  { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
  @keyframes kd_spin    { to { transform:rotate(360deg); } }
  @keyframes kd_pulse   { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(1.6); } }
  @keyframes kd_bar     { 0%,100% { transform:scaleY(0.4); } 50% { transform:scaleY(1); } }
  @keyframes kd_flow    { 0%,100% { background-position:0% 50%; } 50% { background-position:100% 50%; } }
`;

export default function KernelDashboard() {
  const { token } = useAuth();
  const [kernel, setKernel]           = useState(null);
  const [architecture, setArchitecture] = useState(null);
  const [loading, setLoading]         = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ks, arch] = await Promise.all([
          fetch(`${API}/api/kernel/status`,       { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
          fetch(`${API}/api/kernel/architecture`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
        ]);
        setKernel(ks);
        setArchitecture(arch);
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    fetchData();
  }, [token]);

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256, flexDirection: "column", gap: 14 }}>
      <style>{STYLES}</style>
      <div style={{ position: "relative", width: 40, height: 40 }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid transparent", borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.25)", animation: "kd_spin 0.85s linear infinite" }} />
        <div style={{ position: "absolute", inset: 5, borderRadius: "50%", border: "2px solid transparent", borderBottomColor: T.violet, borderLeftColor: "rgba(124,58,237,0.25)", animation: "kd_spin 0.6s linear infinite reverse" }} />
      </div>
      <p style={{ fontSize: 12, color: "#475569" }}>Loading kernel status…</p>
    </div>
  );

  const metrics = kernel?.metrics || {};
  const metricItems = [
    { label: "Agents",        value: metrics.total_agents },
    { label: "Active Tasks",  value: metrics.active_tasks },
    { label: "Task Graphs",   value: metrics.total_task_graphs },
    { label: "Executions",    value: metrics.execution_logs },
    { label: "Memory Entries",value: metrics.memory_entries },
    { label: "Tools",         value: metrics.tools_registered },
    { label: "Active Graphs", value: metrics.active_task_graphs },
    { label: "Total Tasks",   value: metrics.total_tasks },
  ];

  return (
    <div data-testid="kernel-dashboard" style={{ animation: "kd_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, rgba(79,209,197,0.2), rgba(124,58,237,0.15))", border: "1px solid rgba(79,209,197,0.2)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(79,209,197,0.12)" }}>
              <Server style={{ width: 20, height: 20, color: T.teal }} />
            </div>
            <div>
              <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>MAARS Kernel</h1>
              <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>Core runtime operating system — {Object.keys(kernel?.subsystems || {}).length} active subsystems</p>
            </div>
          </div>
        </div>

        {/* Waveform + status */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
            {[0,1,2,3,4].map(i => (
              <div key={i} style={{ width: 3, height: 14, borderRadius: 2, background: T.teal, animation: `kd_bar 0.7s ease-in-out ${i * 0.1}s infinite`, opacity: 0.7 }} />
            ))}
          </div>
          <span style={{ fontSize: 11, fontWeight: 700, color: T.teal, letterSpacing: "0.08em" }}>
            {kernel?.status?.toUpperCase() || "ONLINE"}
          </span>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: T.green, animation: "kd_pulse 2s ease-in-out infinite" }} />
        </div>
      </div>

      {/* ── Metrics grid ────────────────────────────────────────────────── */}
      {kernel && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 10, marginBottom: 28 }}>
          {metricItems.map((m, i) => (
            <div
              key={i}
              data-testid={`metric-${m.label.toLowerCase().replace(/ /g, '-')}`}
              style={{ padding: "14px 16px", borderRadius: 14, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, ${METRIC_COLORS[i % METRIC_COLORS.length]}, transparent)`, opacity: 0.6 }} />
              <p style={{ fontSize: 9, color: "#475569", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 6, margin: "0 0 4px" }}>{m.label}</p>
              <p style={{ fontSize: 22, fontWeight: 800, color: METRIC_COLORS[i % METRIC_COLORS.length], fontFamily: "Outfit, sans-serif", margin: 0, lineHeight: 1 }}>
                {(m.value ?? 0).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* ── Subsystems ──────────────────────────────────────────────────── */}
      {kernel?.subsystems && (
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Radio style={{ width: 14, height: 14, color: T.teal }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Kernel Subsystems</span>
            <span style={{ fontSize: 11, color: "#475569" }}>({Object.keys(kernel.subsystems).filter(k => k !== "circuit_breakers").length} online)</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 8 }}>
            {Object.entries(kernel.subsystems).filter(([k]) => k !== "circuit_breakers").map(([key, sub]) => {
              const meta = SUBSYSTEM_META[key] || { icon: Cpu, color: T.teal, label: key };
              const Icon = meta.icon;
              const isActive = sub.status === "active";
              const statusColor = isActive ? T.green : sub.status === "standby" ? T.amber : T.red;
              return (
                <div key={key} data-testid={`subsystem-${key}`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 12, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(8px)", transition: "border-color 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = `${meta.color}33`}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: `${meta.color}12`, border: `1px solid ${meta.color}20`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <Icon style={{ width: 16, height: 16, color: meta.color }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0", margin: "0 0 2px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{meta.label}</p>
                    <p style={{ fontSize: 10, color: "#475569", margin: 0 }}>
                      {sub.agents_registered != null && `${sub.agents_registered} agents`}
                      {sub.total_graphs != null && `${sub.total_graphs} graphs`}
                      {sub.total_executions != null && `${sub.total_executions} execs`}
                      {sub.tools_registered != null && `${sub.tools_registered} tools`}
                      {sub.entries != null && `${sub.entries} entries`}
                      {!sub.agents_registered && !sub.total_graphs && !sub.total_executions && !sub.tools_registered && !sub.entries && sub.status}
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <div style={{ width: 7, height: 7, borderRadius: "50%", background: statusColor, boxShadow: `0 0 6px ${statusColor}88`, animation: isActive ? "kd_pulse 2.5s ease-in-out infinite" : "none" }} />
                    <span style={{ fontSize: 9, color: statusColor, fontWeight: 700, textTransform: "uppercase" }}>{sub.status}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── System Architecture Layers ───────────────────────────────────── */}
      {architecture?.layers && (
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Layers style={{ width: 14, height: 14, color: T.violet }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>System Architecture</span>
            <span style={{ fontSize: 11, color: "#475569" }}>{architecture.layers.length} layers</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {architecture.layers.map((layer, i) => {
              const pct = ((architecture.layers.length - i) / architecture.layers.length) * 100;
              const c = TIER_COLORS[i % TIER_COLORS.length];
              return (
                <div key={i} data-testid={`layer-${i}`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 11, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(8px)", transition: "border-color 0.15s", position: "relative", overflow: "hidden" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = `${c}33`}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                  <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: c, borderRadius: "3px 0 0 3px", opacity: 0.6 }} />
                  <div style={{ width: 26, height: 26, borderRadius: 8, background: `${c}15`, border: `1px solid ${c}25`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginLeft: 4 }}>
                    <span style={{ fontSize: 10, fontWeight: 800, color: c, fontFamily: "monospace" }}>{i}</span>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", margin: "0 0 1px" }}>{layer.name}</p>
                    <p style={{ fontSize: 10, color: "#475569", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{layer.description}</p>
                  </div>
                  <div style={{ flexShrink: 0, textAlign: "right" }}>
                    <div style={{ width: 60, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                      <div style={{ height: "100%", borderRadius: 2, background: c, width: `${pct}%`, opacity: 0.7 }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Autonomy Tiers ──────────────────────────────────────────────── */}
      {architecture?.autonomy_tiers && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Radar style={{ width: 14, height: 14, color: T.amber }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Autonomy Tiers</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 8 }}>
            {Object.entries(architecture.autonomy_tiers).map(([tier, desc], i) => {
              const c = TIER_COLORS[i % TIER_COLORS.length];
              return (
                <div key={tier} data-testid={`tier-${tier}`}
                  style={{ padding: "12px 14px", borderRadius: 12, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(8px)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                    <span style={{ fontSize: 12, fontWeight: 800, color: c, fontFamily: "monospace" }}>T{tier}</span>
                    <div style={{ flex: 1, height: 1, background: `${c}20` }} />
                  </div>
                  <p style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5, margin: 0 }}>{desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      {architecture && (
        <div style={{ display: "flex", alignItems: "center", gap: 20, paddingTop: 16, borderTop: `1px solid ${T.border}`, flexWrap: "wrap" }}>
          {[
            { label: "Infinity Agents", value: architecture.total_agents, color: T.teal },
            { label: "Networks",        value: architecture.total_networks, color: T.violet },
            { label: "Layers",          value: architecture.layers?.length, color: T.blue },
          ].map((s, i) => (
            <div key={i} style={{ display: "flex", items: "center", gap: 6 }}>
              <span style={{ fontSize: 14, fontWeight: 800, color: s.color, fontFamily: "Outfit, sans-serif" }}>{s.value}</span>
              <span style={{ fontSize: 11, color: "#475569" }}>{s.label}</span>
            </div>
          ))}
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5, color: "#334155" }}>
            <Clock style={{ width: 11, height: 11 }} />
            <span style={{ fontSize: 10 }}>{kernel?.timestamp ? new Date(kernel.timestamp).toLocaleString() : "Live"}</span>
          </div>
        </div>
      )}
    </div>
  );
}
