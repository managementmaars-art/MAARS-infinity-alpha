import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import {
  Activity, Zap, ArrowRight, CheckCircle, Clock, AlertTriangle,
  Radio, Users, GitBranch, Terminal, RefreshCw, Wifi, WifiOff
} from "lucide-react";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  blue: "#60a5fa",
  zinc: "#71717a",
  indigo: "#818cf8",
  cyan: "#22d3ee",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

const STATUS_COLOR = {
  completed:  T.green,
  in_progress: T.indigo,
  pending:    T.amber,
  failed:     T.red,
};

const ActivityMonitor = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [liveMode, setLiveMode] = useState(true);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchActivity = useCallback(async () => {
    try {
      const res = await fetch(`${API}/activity/live`, { headers });
      if (res.ok) setData(await res.json());
    } catch {} finally { setLoading(false); }
  }, [token]);

  const connectWs = useCallback(() => {
    if (!token || !liveMode) return;
    const apiUrl = API.replace(/\/api$/, "");
    const wsProtocol = apiUrl.startsWith("https") ? "wss" : "ws";
    const wsHost = apiUrl.replace(/^https?:\/\//, "");
    const wsUrl = `${wsProtocol}://${wsHost}/api/ws/activity?token=${token}`;
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onopen = () => { setWsConnected(true); setLoading(false); };
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "pong") return;
          if (msg.type === "snapshot" || msg.agent_activity) { setData(msg); setLoading(false); }
        } catch {}
      };
      ws.onclose = () => {
        setWsConnected(false); wsRef.current = null;
        if (liveMode) reconnectRef.current = setTimeout(connectWs, 3000);
      };
      ws.onerror = () => ws.close();
    } catch { setWsConnected(false); fetchActivity(); }
  }, [token, liveMode]);

  useEffect(() => {
    if (liveMode) { connectWs(); }
    else { if (wsRef.current) { wsRef.current.close(); wsRef.current = null; } fetchActivity(); }
    return () => {
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [liveMode, connectWs, fetchActivity]);

  useEffect(() => {
    if (wsConnected || !liveMode) return;
    const interval = setInterval(fetchActivity, 10000);
    return () => clearInterval(interval);
  }, [wsConnected, liveMode, fetchActivity]);

  useEffect(() => { fetchActivity(); }, []);

  const handleRefresh = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) wsRef.current.send("refresh");
    else fetchActivity();
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", paddingTop: 80 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.green}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const agents = data?.agent_activity || [];
  const flows = data?.communication_flows || [];
  const tasks = data?.task_graph || [];
  const tools = data?.recent_tool_calls || [];

  const SectionHead = ({ icon, label, count, accent = T.zinc }) => (
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
      <span style={{ color: accent }}>{icon}</span>
      <span style={{ fontSize: 11, fontWeight: 700, color: T.zinc, textTransform: "uppercase", letterSpacing: ".08em" }}>{label}</span>
      {count != null && (
        <span style={{ fontSize: 10, color: accent, background: `${accent}15`, padding: "2px 8px", borderRadius: 6, fontWeight: 600, marginLeft: "auto" }}>{count}</span>
      )}
    </div>
  );

  const EmptyState = ({ icon, text }) => (
    <div style={{ textAlign: "center", padding: "32px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
      <div style={{ color: "rgba(255,255,255,.1)", marginBottom: 10 }}>{icon}</div>
      <p style={{ fontSize: 12, color: T.zinc }}>{text}</p>
    </div>
  );

  const wsStatusColor = wsConnected ? T.green : liveMode ? T.amber : T.zinc;
  const wsLabel = wsConnected ? "WebSocket Live" : liveMode ? "Polling (10s)" : "Paused";
  const WsIcon = wsConnected ? Wifi : WifiOff;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28, animation: "fadeUp .4s ease" }} data-testid="activity-monitor">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 14, background: "rgba(52,211,153,0.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Radio size={20} style={{ color: T.green }} />
          </div>
          <div>
            <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 22, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 2 }}>Agent Activity Monitor</h1>
            <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>Real-time execution, communication flows & task dependencies</p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {/* WS status */}
          <div data-testid="ws-status" style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 8, background: T.glass, border: `1px solid ${T.border}` }}>
            <WsIcon size={12} style={{ color: wsStatusColor }} />
            <span style={{ fontSize: 11, color: wsStatusColor, fontWeight: 500 }}>{wsLabel}</span>
          </div>
          <button
            onClick={() => setLiveMode(!liveMode)}
            data-testid="toggle-live"
            style={{
              padding: "5px 14px", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: "pointer",
              background: liveMode ? "rgba(52,211,153,.12)" : "rgba(255,255,255,.04)",
              border: liveMode ? `1px solid rgba(52,211,153,.35)` : `1px solid ${T.border}`,
              color: liveMode ? T.green : T.zinc,
            }}
          >
            {liveMode ? "Live" : "Paused"}
          </button>
          <button
            onClick={handleRefresh}
            data-testid="refresh-btn"
            style={{ width: 32, height: 32, borderRadius: 8, background: T.glass, border: `1px solid ${T.border}`, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: T.zinc }}
          >
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Active Projects */}
      {data?.active_projects?.length > 0 && (
        <div>
          <SectionHead icon={<Zap size={14} />} label="Active Projects" count={data.active_projects.length} accent={T.amber} />
          <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 4 }}>
            {data.active_projects.map(p => (
              <div
                key={p.project_id}
                style={{ flexShrink: 0, width: 240, padding: "12px 14px", borderRadius: 12, background: "rgba(245,158,11,.05)", border: `1px solid rgba(245,158,11,.2)` }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: T.amber, animation: "pulse 1.5s infinite" }} />
                  <span style={{ fontSize: 12, fontWeight: 600, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.title || "Untitled"}</span>
                </div>
                <p style={{ fontSize: 10, color: T.zinc, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.goal?.substring(0, 80)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Workforce */}
      <div>
        <SectionHead icon={<Users size={14} />} label="Agent Workforce Status" count={`${agents.length} active`} accent={T.indigo} />
        {agents.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px,1fr))", gap: 10 }}>
            {agents.slice(0, 20).map((a, i) => {
              const done = a.completed === a.task_count;
              const pct = Math.round((a.completed / Math.max(a.task_count, 1)) * 100);
              return (
                <div
                  key={i}
                  style={{ padding: "12px 14px", borderRadius: 12, background: T.glass, border: `1px solid ${T.border}`, transition: "border-color .2s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: done ? T.green : T.indigo, animation: done ? "none" : "pulse 1.5s infinite", flexShrink: 0 }} />
                    <span style={{ fontSize: 11, fontWeight: 500, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.agent}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, color: T.zinc }}>{a.completed}/{a.task_count} tasks</span>
                    <span style={{ fontSize: 10, color: done ? T.green : T.indigo, fontWeight: 600 }}>{pct}%</span>
                  </div>
                  <div style={{ height: 3, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, background: done ? T.green : T.indigo, width: `${pct}%`, transition: "width .6s ease" }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState icon={<Users size={32} />} text="No active agents. Start a project to see agent workforce." />
        )}
      </div>

      {/* Communication Flows */}
      <div>
        <SectionHead icon={<ArrowRight size={14} />} label="Inter-Agent Communication Flows" count={flows.length} accent={T.violet} />
        {flows.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {flows.slice(0, 12).map((f, i) => {
              const statusColor = STATUS_COLOR[f.status] || T.amber;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 10, background: T.glass, border: `1px solid ${T.border}` }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                    <span style={{ fontSize: 11, fontWeight: 600, color: T.indigo }}>{f.from}</span>
                    <ArrowRight size={12} style={{ color: T.zinc }} />
                    <span style={{ fontSize: 11, fontWeight: 600, color: T.violet }}>{f.to}</span>
                  </div>
                  <span style={{ fontSize: 11, color: T.zinc, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{f.objective}</span>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: statusColor, flexShrink: 0 }} />
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState icon={<ArrowRight size={28} />} text="No communication flows yet. Run a project to see agent collaboration." />
        )}
      </div>

      {/* Task Dependency Graph */}
      <div>
        <SectionHead icon={<GitBranch size={14} />} label="Task Dependency Graph" count={tasks.length} accent={T.cyan} />
        {tasks.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px,1fr))", gap: 10 }}>
            {tasks.slice(0, 15).map((t, i) => {
              const sc = STATUS_COLOR[t.status] || T.amber;
              return (
                <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 12px", borderRadius: 10, background: T.glass, border: `1px solid ${T.border}` }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: sc, marginTop: 4, flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 11, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", margin: "0 0 2px" }}>{t.title}</p>
                    <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{t.agent}</p>
                  </div>
                  <span style={{ fontSize: 9, fontWeight: 600, color: sc, background: `${sc}18`, padding: "2px 7px", borderRadius: 5, flexShrink: 0 }}>{t.status}</span>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState icon={<GitBranch size={28} />} text="No tasks in the dependency graph yet." />
        )}
      </div>

      {/* Tool Executions */}
      <div>
        <SectionHead icon={<Terminal size={14} />} label="Recent Tool Executions" count={tools.length} accent={T.amber} />
        {tools.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {tools.slice(0, 10).map((t, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 8, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", background: t.status === "success" ? T.green : T.red, flexShrink: 0 }} />
                <span style={{ fontSize: 11, fontFamily: "monospace", color: T.indigo, width: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flexShrink: 0 }}>{t.tool_name}</span>
                <span style={{ fontSize: 11, color: T.zinc, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.agent_name}</span>
                <span style={{ fontSize: 10, color: "rgba(113,113,122,.6)", flexShrink: 0 }}>{t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : ""}</span>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", paddingTop: 16 }}>No recent tool calls</p>
        )}
      </div>
    </div>
  );
};

export default ActivityMonitor;
