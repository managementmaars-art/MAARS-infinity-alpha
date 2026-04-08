import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  MessageSquare, ArrowRight, Clock, CheckCircle, AlertTriangle,
  Zap, Users, ChevronDown, ChevronUp, Filter
} from "lucide-react";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#7c3aed",
  indigo: "#818cf8",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const STATUS_META = {
  pending: { color: T.amber, bg: "rgba(245,158,11,.12)" },
  in_progress: { color: T.indigo, bg: "rgba(129,140,248,.12)" },
  completed: { color: T.green, bg: "rgba(52,211,153,.12)" },
  failed: { color: T.red, bg: "rgba(239,68,68,.12)" },
};

const RISK_COLOR = { low: T.green, medium: T.amber, high: T.red, critical: "#dc2626" };

const selectStyle = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "7px 10px", color: "#a1a1aa", fontSize: 12,
  outline: "none", fontFamily: "inherit", cursor: "pointer", width: "100%",
};

const CollabCard = ({ collab }) => {
  const [expanded, setExpanded] = useState(false);
  const sm = STATUS_META[collab.status] || STATUS_META.pending;
  const riskColor = RISK_COLOR[collab.risk_level] || T.green;
  return (
    <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", transition: "border-color .2s" }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.13)"}
      onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
        <div style={{ width: 34, height: 34, borderRadius: 9, background: "rgba(129,140,248,.12)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <MessageSquare size={15} style={{ color: T.indigo }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 5 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{collab.sender || "System"}</span>
            <ArrowRight size={11} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, color: T.indigo }}>{(collab.receivers || []).join(", ") || "All"}</span>
            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, background: sm.bg, color: sm.color, fontWeight: 700 }}>{collab.status}</span>
            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, background: "rgba(255,255,255,.04)", color: riskColor, fontWeight: 700 }}>{collab.risk_level} risk</span>
          </div>
          <p style={{ fontSize: 13, color: "#d4d4d8", marginBottom: 4 }}>{collab.objective}</p>
          {collab.context && <p style={{ fontSize: 11, color: T.zinc, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: expanded ? "unset" : 2, WebkitBoxOrient: "vertical" }}>{collab.context}</p>}

          {expanded && (
            <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${T.border}`, display: "flex", flexDirection: "column", gap: 10 }}>
              {collab.required_output && (
                <div>
                  <p style={{ fontSize: 9, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 4 }}>Required Output</p>
                  <p style={{ fontSize: 12, color: "#d4d4d8" }}>{collab.required_output}</p>
                </div>
              )}
              {collab.dependencies?.length > 0 && (
                <div>
                  <p style={{ fontSize: 9, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 5 }}>Dependencies</p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                    {collab.dependencies.map((d, i) => (
                      <span key={i} style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid ${T.border}`, color: T.zinc }}>{d}</span>
                    ))}
                  </div>
                </div>
              )}
              {collab.response && (
                <div>
                  <p style={{ fontSize: 9, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 4 }}>Response</p>
                  <p style={{ fontSize: 12, color: "#d4d4d8", whiteSpace: "pre-wrap" }}>{collab.response}</p>
                </div>
              )}
              {collab.deadline && (
                <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: T.zinc }}>
                  <Clock size={11} /> Deadline: {collab.deadline}
                </div>
              )}
            </div>
          )}

          <button onClick={() => setExpanded(!expanded)}
            style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: T.zinc, background: "none", border: "none", cursor: "pointer", padding: 0, marginTop: 8, transition: "color .2s" }}
            onMouseEnter={e => e.currentTarget.style.color = "#a1a1aa"}
            onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
            {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
            {expanded ? "Less" : "More details"}
          </button>
        </div>
        <span style={{ fontSize: 10, color: "rgba(113,113,122,.5)", flexShrink: 0 }}>
          {collab.created_at ? new Date(collab.created_at).toLocaleDateString() : ""}
        </span>
      </div>
    </div>
  );
};

const CollaborationEngine = () => {
  const { token } = useAuth();
  const [collabs, setCollabs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [total, setTotal] = useState(0);
  const [showCreate, setShowCreate] = useState(false);
  const [newCollab, setNewCollab] = useState({ sender: "", receivers: [], objective: "", collab_type: "information_sharing" });
  const [creating, setCreating] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchCollabs = useCallback(async () => {
    try {
      const [collabRes, agentsRes] = await Promise.all([
        fetch(`${API}/collaborations?page=1&limit=50${filter !== "all" ? `&status=${filter}` : ""}`, { headers }),
        fetch(`${API}/agents`, { headers }),
      ]);
      if (collabRes.ok) { const data = await collabRes.json(); setCollabs(data.items || []); setTotal(data.total || 0); }
      if (agentsRes.ok) setAgents(await agentsRes.json());
    } catch {} finally { setLoading(false); }
  }, [token, filter]);

  useEffect(() => { fetchCollabs(); }, [fetchCollabs]);

  const handleCreateCollab = async () => {
    if (!newCollab.sender || newCollab.receivers.length === 0 || !newCollab.objective) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/collaborations`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(newCollab),
      });
      if (res.ok) { setShowCreate(false); setNewCollab({ sender: "", receivers: [], objective: "", collab_type: "information_sharing" }); fetchCollabs(); }
    } catch {} finally { setCreating(false); }
  };

  const statusCounts = collabs.reduce((acc, c) => { acc[c.status] = (acc[c.status] || 0) + 1; return acc; }, {});
  const uniqueAgents = new Set([...collabs.map(c => c.sender), ...collabs.flatMap(c => c.receivers || [])]);
  const statusFilters = ["all", "pending", "in_progress", "completed", "failed"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22, animation: "fadeUp .4s ease" }} data-testid="collaboration-engine">
      <style>{STYLES}</style>

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(124,58,237,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Users size={22} style={{ color: T.violet }} />
        </div>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }}>Agent-to-Agent Collaboration</h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Inter-agent communication, task handoff & cross-domain coordination</p>
        </div>
        <span style={{ marginLeft: "auto", fontSize: 11, padding: "4px 12px", borderRadius: 20, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc }}>{total} total</span>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }} data-testid="collab-stats">
        {[
          { icon: MessageSquare, label: "Total Collabs", value: total, color: T.violet },
          { icon: Users, label: "Agents Involved", value: uniqueAgents.size, color: T.indigo },
          { icon: CheckCircle, label: "Completed", value: statusCounts.completed || 0, color: T.green },
          { icon: Clock, label: "Pending", value: statusCounts.pending || 0, color: T.amber },
        ].map(s => (
          <div key={s.label} style={{ position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "12px 14px", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <s.icon size={12} style={{ color: s.color }} />
              <span style={{ fontSize: 10, color: T.zinc }}>{s.label}</span>
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: "#fff" }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Filters + create */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <Filter size={13} style={{ color: T.zinc }} />
        {statusFilters.map(s => (
          <button key={s} onClick={() => setFilter(s)} data-testid={`filter-${s}`}
            style={{ padding: "5px 12px", borderRadius: 8, border: `1px solid ${filter === s ? "rgba(129,140,248,.3)" : T.border}`, background: filter === s ? "rgba(129,140,248,.1)" : T.glass, color: filter === s ? T.indigo : T.zinc, fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}>
            {s === "all" ? "All" : s.replace("_", " ")}
          </button>
        ))}
        <button onClick={() => setShowCreate(!showCreate)} data-testid="initiate-collab-btn"
          style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5, padding: "6px 14px", borderRadius: 9, background: "rgba(124,58,237,.15)", border: `1px solid rgba(124,58,237,.3)`, color: "#c4b5fd", fontSize: 12, fontWeight: 700, cursor: "pointer", transition: "background .2s" }}>
          <Zap size={12} /> Initiate Collaboration
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div style={{ background: T.glass, border: `1px solid rgba(124,58,237,.2)`, borderRadius: 14, padding: "16px 18px", display: "flex", flexDirection: "column", gap: 12 }} data-testid="create-collab-form">
          <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Initiate Agent-to-Agent Collaboration</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <select value={newCollab.sender} onChange={e => setNewCollab(p => ({ ...p, sender: e.target.value }))} style={selectStyle} data-testid="collab-sender">
              <option value="">Select sender agent…</option>
              {agents.slice(0, 50).map(a => <option key={a.agent_id} value={a.name} style={{ background: "#0f0f1a" }}>{a.name} ({a.role})</option>)}
            </select>
            <select value="" onChange={e => { if (e.target.value && !newCollab.receivers.includes(e.target.value)) setNewCollab(p => ({ ...p, receivers: [...p.receivers, e.target.value] })); }} style={selectStyle} data-testid="collab-receiver">
              <option value="">Add receiver agent…</option>
              {agents.slice(0, 50).filter(a => a.name !== newCollab.sender).map(a => <option key={a.agent_id} value={a.name} style={{ background: "#0f0f1a" }}>{a.name} ({a.role})</option>)}
            </select>
          </div>
          {newCollab.receivers.length > 0 && (
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {newCollab.receivers.map(r => (
                <span key={r} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, padding: "3px 8px", borderRadius: 5, background: "rgba(124,58,237,.12)", border: `1px solid rgba(124,58,237,.25)`, color: "#c4b5fd" }}>
                  {r}
                  <button onClick={() => setNewCollab(p => ({ ...p, receivers: p.receivers.filter(x => x !== r) }))} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 0, lineHeight: 1 }}>×</button>
                </span>
              ))}
            </div>
          )}
          <div style={{ display: "grid", gridTemplateColumns: "3fr 1fr", gap: 10 }}>
            <input value={newCollab.objective} onChange={e => setNewCollab(p => ({ ...p, objective: e.target.value }))}
              placeholder="Collaboration objective…" style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit" }} data-testid="collab-objective" />
            <select value={newCollab.collab_type} onChange={e => setNewCollab(p => ({ ...p, collab_type: e.target.value }))} style={selectStyle} data-testid="collab-type">
              <option value="information_sharing" style={{ background: "#0f0f1a" }}>Info Sharing</option>
              <option value="review_request" style={{ background: "#0f0f1a" }}>Review Request</option>
              <option value="data_handoff" style={{ background: "#0f0f1a" }}>Data Handoff</option>
              <option value="coordination" style={{ background: "#0f0f1a" }}>Coordination</option>
            </select>
          </div>
          <button onClick={handleCreateCollab} disabled={creating} data-testid="submit-collab-btn"
            style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 6, padding: "8px 18px", borderRadius: 9, background: creating ? "rgba(124,58,237,.3)" : `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: creating ? "not-allowed" : "pointer" }}>
            {creating ? <div style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : null}
            {creating ? "Creating…" : "Create Collaboration"}
          </button>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200 }}>
          <div style={{ width: 24, height: 24, border: `2px solid ${T.violet}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
        </div>
      ) : collabs.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {collabs.map(c => <CollabCard key={c.collab_id} collab={c} />)}
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
          <Users size={44} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
          <p style={{ fontSize: 13, color: T.zinc, marginBottom: 4 }}>No collaboration logs yet</p>
          <p style={{ fontSize: 11, color: "rgba(113,113,122,.5)" }}>Collaborations are created automatically when agents work together on projects</p>
        </div>
      )}
    </div>
  );
};

export default CollaborationEngine;
