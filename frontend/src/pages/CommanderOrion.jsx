import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Rocket, GitBranch, Cpu, CheckCircle, XCircle, Clock, Activity,
  Play, Loader2, AlertCircle, FileText, ChevronRight, Zap, Wifi, WifiOff,
  MessageCircle, FolderPlus
} from "lucide-react";
import AgentAvatar from "../components/AgentAvatar";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  blue: "#60a5fa",
  cyan: "#22d3ee",
  indigo: "#818cf8",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
@keyframes slideIn { from{opacity:0;transform:scale(.96)} to{opacity:1;transform:scale(1)} }
`;

const RISK_META = {
  low:      { color: T.green,  bg: "rgba(52,211,153,0.1)" },
  medium:   { color: T.amber,  bg: "rgba(245,158,11,0.1)" },
  high:     { color: T.red,    bg: "rgba(239,68,68,0.1)" },
  critical: { color: "#fca5a5", bg: "rgba(239,68,68,0.2)" },
};

const Chip = ({ children, color = T.zinc, bg, style = {} }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 6, background: bg || `${color}18`, color, letterSpacing: ".04em", ...style }}>
    {children}
  </span>
);

const glass = {
  background: T.glass,
  border: `1px solid ${T.border}`,
  borderRadius: 16,
  backdropFilter: "blur(12px)",
};

const COMMANDER_AGENT = {
  agent_id: "commander_orion",
  name: "Commander Orion",
  role: "AI Commander",
  isCommander: true,
  avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/9a3eb3186a873a3337de51d37d80e0dac2da6db7ef21b2bef016307c59557b27.png",
};

export default function CommanderOrion() {
  const navigate = useNavigate();
  const [goal, setGoal] = useState("");
  const [mode, setMode] = useState("full");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [liveSteps, setLiveSteps] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchRuns = useCallback(async () => {
    const res = await fetch(`${API}/api/infinity/orchestrator/runs?limit=8`, { headers }).catch(() => null);
    if (res?.ok) setRuns(await res.json());
  }, [token]);

  useEffect(() => { fetchRuns(); }, [fetchRuns]);

  useEffect(() => {
    if (!token) return;
    const wsUrl = API.replace(/^http/, "ws") + `/api/ws/infinity?token=${token}&channel=global`;
    let ws, reconnectTimer;
    const connect = () => {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => { setWsConnected(true); wsRef.current = ws; };
      ws.onclose = () => { setWsConnected(false); reconnectTimer = setTimeout(connect, 5000); };
      ws.onerror = () => ws.close();
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "step_update") {
            setLiveSteps(prev => {
              const existing = prev.findIndex(s => s.step === data.step && s.execution_id === data.execution_id);
              if (existing >= 0) { const updated = [...prev]; updated[existing] = data; return updated; }
              return [...prev, data];
            });
          }
        } catch {}
      };
    };
    connect();
    return () => { clearTimeout(reconnectTimer); ws?.close(); };
  }, [token]);

  const executeGoal = async () => {
    if (!goal.trim()) return;
    setLoading(true); setResult(null); setSelectedRun(null); setLiveSteps([]);
    try {
      const endpoint = mode === "full" ? "/api/infinity/orchestrator/full-execute" : "/api/infinity/orchestrator/execute";
      const res = await fetch(`${API}${endpoint}`, {
        method: "POST", headers,
        body: JSON.stringify({ description: goal, requester_id: "operator", environment: mode === "full" ? "production" : "simulation" }),
      });
      const data = await res.json();
      setResult(data);
      fetchRuns();
    } catch (e) { setResult({ error: e.message }); }
    setLoading(false);
  };

  const exec = result?.execution;
  const classification = result?.classification;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="commander-orion">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <AgentAvatar agent={COMMANDER_AGENT} size="xl" status="online" animate showRing />
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 24, fontWeight: 700, color: "#fff", margin: 0 }}>Commander Orion</h1>
              <Chip color={T.amber}>AI Commander</Chip>
            </div>
            <p style={{ fontSize: 13, color: T.zinc, margin: "0 0 12px" }}>AI-powered goal orchestration: classify, decompose, execute, verify, report</p>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => navigate("/chat/commander_orion")}
                data-testid="open-commander-chat"
                style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 8, background: "rgba(245,158,11,.1)", border: `1px solid rgba(245,158,11,.3)`, color: T.amber, fontSize: 11, fontWeight: 600, cursor: "pointer" }}
              >
                <MessageCircle size={13} /> Chat with Commander
              </button>
              <button
                onClick={() => { document.querySelector("[data-testid='goal-input']")?.scrollIntoView({ behavior: "smooth" }); setTimeout(() => document.querySelector("[data-testid='goal-input']")?.focus(), 400); }}
                style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 8, background: "rgba(124,58,237,.1)", border: `1px solid rgba(124,58,237,.3)`, color: T.violet, fontSize: 11, fontWeight: 600, cursor: "pointer" }}
              >
                <FolderPlus size={13} /> New Project
              </button>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 8, background: T.glass, border: `1px solid ${T.border}` }} data-testid="ws-status-commander">
          {wsConnected ? <><Wifi size={12} style={{ color: T.green }} /><span style={{ fontSize: 11, color: T.green }}>Live Stream</span></> : <><WifiOff size={12} style={{ color: T.zinc }} /><span style={{ fontSize: 11, color: T.zinc }}>Offline</span></>}
        </div>
      </div>

      {/* Goal Input */}
      <div style={{ ...glass, padding: "18px 20px" }}>
        <textarea
          value={goal} onChange={e => setGoal(e.target.value)}
          placeholder='Describe your goal... (e.g., "Analyze the competitive landscape for enterprise AI")'
          rows={3}
          data-testid="goal-input"
          style={{ width: "100%", boxSizing: "border-box", background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 10, padding: "10px 14px", color: "#fff", fontSize: 13, resize: "vertical", outline: "none", fontFamily: "inherit", lineHeight: 1.6 }}
        />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 12, gap: 10, flexWrap: "wrap" }}>
          <select
            value={mode} onChange={e => setMode(e.target.value)}
            data-testid="mode-select"
            style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, color: T.zinc, fontSize: 11, padding: "6px 12px", cursor: "pointer" }}
          >
            <option value="full">Full Execute (classify → decompose → execute → verify → report)</option>
            <option value="plan">Plan Only (classify → decompose → assign)</option>
          </select>
          <button
            onClick={executeGoal}
            disabled={loading || !goal.trim()}
            data-testid="execute-goal-btn"
            style={{
              display: "flex", alignItems: "center", gap: 8, padding: "9px 22px", borderRadius: 12,
              background: loading || !goal.trim() ? "rgba(245,158,11,.3)" : `linear-gradient(135deg, ${T.amber}, #d97706)`,
              border: "none", color: "#000", fontSize: 13, fontWeight: 700, cursor: loading || !goal.trim() ? "not-allowed" : "pointer",
            }}
          >
            {loading ? <div style={{ width: 16, height: 16, border: "2px solid #000", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Zap size={15} />}
            {mode === "full" ? "Execute Goal" : "Plan Goal"}
          </button>
        </div>
      </div>

      {/* Live Steps */}
      {loading && liveSteps.length > 0 && (
        <div style={{ ...glass, padding: 0, overflow: "hidden", border: `1px solid rgba(34,211,238,.2)` }} data-testid="live-steps-panel">
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "14px 18px 10px", borderBottom: `1px solid ${T.border}` }}>
            <Activity size={14} style={{ color: T.cyan, animation: "pulse 1.5s infinite" }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: T.cyan }}>Live Execution Progress</span>
          </div>
          <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 4 }}>
            {liveSteps.map((s, i) => {
              const sc = s.status === "pass" ? T.green : s.status === "fail" ? T.red : T.cyan;
              const StatusIcon = s.status === "pass" ? CheckCircle : s.status === "fail" ? XCircle : Loader2;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 8, background: `${sc}06`, border: `1px solid ${sc}18`, fontSize: 11 }}>
                  <StatusIcon size={12} style={{ color: sc, flexShrink: 0, animation: s.status === "running" ? "spin .8s linear infinite" : "none" }} />
                  <span style={{ color: T.zinc, width: 28, flexShrink: 0 }}>{s.step_num}</span>
                  <span style={{ color: "#e4e4e7", fontWeight: 500, flex: 1 }}>{s.step}</span>
                  <span style={{ color: T.zinc, flex: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.detail}</span>
                  <span style={{ color: sc, fontWeight: 600, flexShrink: 0 }}>{s.progress}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Loading fallback */}
      {loading && liveSteps.length === 0 && (
        <div style={{ ...glass, padding: "36px 20px", textAlign: "center" }}>
          <div style={{ width: 40, height: 40, border: `2px solid ${T.cyan}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite", margin: "0 auto 16px" }} />
          <p style={{ fontSize: 14, fontWeight: 600, color: "#fff", margin: "0 0 6px" }}>Executing goal pipeline...</p>
          <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>
            {mode === "full" ? "Classifying → Decomposing → Executing nodes → Verifying → Generating report" : "Classifying → Decomposing → Assigning agents"}
          </p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16, animation: "slideIn .3s ease" }} data-testid="execution-result">
          {/* Classification */}
          <div style={{ ...glass, padding: "16px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Cpu size={14} style={{ color: T.cyan }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Classification & Decomposition</span>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
              <Chip color={T.indigo}>{classification?.goal_type}</Chip>
              {(() => { const rm = RISK_META[classification?.risk_level] || {}; return <Chip color={rm.color} bg={rm.bg}>{classification?.risk_level} risk</Chip>; })()}
              <Chip color={T.zinc}>{classification?.complexity} complexity</Chip>
              {classification?.ai_powered && <Chip color={T.green}>AI via {classification.model_used} ({classification.latency_ms}ms)</Chip>}
              {result.decomposition_meta?.ai_powered && <Chip color={T.cyan}>Decomp via {result.decomposition_meta.model} ({result.decomposition_meta.latency_ms}ms)</Chip>}
            </div>
            {classification?.reasoning && classification.ai_powered && (
              <p style={{ fontSize: 12, color: T.zinc, background: "rgba(255,255,255,.03)", padding: "10px 12px", borderRadius: 8, border: `1px solid ${T.border}`, margin: 0, lineHeight: 1.6 }}>{classification.reasoning}</p>
            )}
          </div>

          {/* Task Graph */}
          <div style={{ ...glass, padding: "16px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <GitBranch size={14} style={{ color: T.amber }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Task Graph — {result.nodes} nodes</span>
              </div>
              {exec?.summary && (
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <Chip color={exec.summary.failed === 0 ? T.green : T.red}>{exec.summary.completed}/{exec.summary.total_nodes} completed</Chip>
                  <span style={{ fontSize: 10, color: T.zinc }}>${exec.summary.total_cost?.toFixed(4)} · {(exec.summary.total_latency_ms / 1000)?.toFixed(1)}s</span>
                </div>
              )}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {(exec?.node_results || result.node_details || []).map((n, i) => {
                const isExec = !!n.provider;
                const sc = n.status === "completed" ? T.green : n.status === "failed" ? T.red : T.amber;
                const StatusIcon = n.status === "completed" ? CheckCircle : n.status === "failed" ? XCircle : GitBranch;
                return (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 10, background: `${sc}06`, border: `1px solid ${sc}18` }} data-testid={`node-${n.node_id}`}>
                    <StatusIcon size={13} style={{ color: sc, flexShrink: 0 }} />
                    <span style={{ fontSize: 10, color: T.zinc, width: 50, flexShrink: 0 }}>{n.node_id}</span>
                    <span style={{ fontSize: 12, color: "#e4e4e7", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.task || n.task_description}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                      {isExec && (
                        <>
                          <Chip color={T.violet}>{n.provider}:{n.model?.split("/").pop()}</Chip>
                          <span style={{ fontSize: 10, color: T.zinc }}>{n.latency_ms}ms</span>
                          <Chip color={n.verification_pass ? T.green : T.amber}>v={n.verification_score?.toFixed(1)}</Chip>
                        </>
                      )}
                      {!isExec && n.model && <Chip color={T.violet}>{n.provider}:{n.model}</Chip>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Final Report */}
          {exec?.final_report && (
            <div style={{ ...glass, padding: "16px 20px", border: `1px solid rgba(52,211,153,.2)` }} data-testid="final-report">
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <FileText size={14} style={{ color: T.green }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: T.green }}>Final Consolidated Report</span>
              </div>
              <div style={{ background: "rgba(0,0,0,.25)", border: `1px solid ${T.border}`, borderRadius: 10, padding: "14px 16px", maxHeight: 360, overflowY: "auto" }}>
                <pre style={{ fontSize: 12, color: "#d4d4d8", whiteSpace: "pre-wrap", fontFamily: "monospace", lineHeight: 1.7, margin: 0 }}>{exec.final_report}</pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Runs */}
      {runs.length > 0 && (
        <div style={{ ...glass, padding: 0, overflow: "hidden" }} data-testid="recent-runs">
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "14px 18px 10px", borderBottom: `1px solid ${T.border}` }}>
            <Clock size={13} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Recent Execution Runs</span>
          </div>
          <div style={{ padding: "10px 18px", display: "flex", flexDirection: "column", gap: 6 }}>
            {runs.map((r, i) => (
              <div
                key={i}
                onClick={() => setSelectedRun(selectedRun?.run_id === r.run_id ? null : r)}
                data-testid={`history-run-${r.run_id}`}
                style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 12px", borderRadius: 10, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}`, cursor: "pointer", transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0 }}>
                  <Chip color={r.status === "completed" ? T.green : T.red}>{r.status}</Chip>
                  <span style={{ fontSize: 12, color: "#e4e4e7", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{r.objective?.slice(0, 60)}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
                  <span style={{ fontSize: 10, color: T.zinc }}>{r.summary?.completed}/{r.summary?.total_nodes} nodes</span>
                  <span style={{ fontSize: 10, color: T.zinc }}>${r.summary?.total_cost?.toFixed(4)}</span>
                  <ChevronRight size={13} style={{ color: T.zinc, transform: selectedRun?.run_id === r.run_id ? "rotate(90deg)" : "none", transition: ".2s" }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected Run Detail */}
      {selectedRun && (
        <div style={{ ...glass, padding: "16px 20px", border: `1px solid rgba(34,211,238,.2)` }} data-testid="run-detail">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Activity size={14} style={{ color: T.cyan }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: T.cyan }}>Run Detail: {selectedRun.run_id}</span>
          </div>
          <p style={{ fontSize: 12, color: T.zinc, marginBottom: 12 }}>{selectedRun.objective}</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {selectedRun.node_results?.map((n, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 8, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}`, fontSize: 11 }}>
                {n.status === "completed" ? <CheckCircle size={12} style={{ color: T.green }} /> : <XCircle size={12} style={{ color: T.red }} />}
                <span style={{ color: T.zinc, width: 50 }}>{n.node_id}</span>
                <span style={{ color: "#e4e4e7", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.task}</span>
                <span style={{ color: T.zinc }}>{n.provider}:{n.model?.split("/").pop()}</span>
                <span style={{ color: T.zinc }}>{n.latency_ms}ms</span>
              </div>
            ))}
          </div>
          {selectedRun.final_report && (
            <details style={{ marginTop: 12 }}>
              <summary style={{ fontSize: 11, color: T.cyan, cursor: "pointer" }}>View Report</summary>
              <pre style={{ fontSize: 11, color: "#d4d4d8", whiteSpace: "pre-wrap", marginTop: 8, padding: "10px 12px", background: "rgba(0,0,0,.25)", borderRadius: 8, maxHeight: 200, overflowY: "auto" }}>{selectedRun.final_report}</pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
