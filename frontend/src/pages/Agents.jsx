import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bot, Plus, MessageSquare, Trash2, Sparkles, Search,
  Eye, EyeOff, LayoutGrid, Grid3X3, Wrench, Zap, Filter, ImagePlus, Loader2
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import AgentAvatar from "../components/AgentAvatar";

/* ─── Design tokens ───────────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  pink:   "#f472b6",
  amber:  "#f59e0b",
  green:  "#34d399",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.6)",
  bg:     "#030712",
};

/* Provider accent colours */
const PROVIDER_COLORS = {
  openai: "#10a37f", anthropic: "#d97706", google: "#4285F4",
  mistral: "#ff7000", groq: "#f55036", cohere: "#39594d",
  default: T.teal,
};

const providerColor = (p = "") =>
  PROVIDER_COLORS[p.toLowerCase()] || PROVIDER_COLORS.default;

/* ─── Category tabs ───────────────────────────────────────────────────────── */
const CATEGORIES = [
  { id: "all",        label: "All Agents"  },
  { id: "analyst",    label: "Analysts"    },
  { id: "creative",   label: "Creative"    },
  { id: "technical",  label: "Technical"   },
  { id: "ops",        label: "Operations"  },
  { id: "custom",     label: "My Agents"   },
];

const agentCategory = (agent) => {
  if (agent.is_custom) return "custom";
  const r = (agent.role || "").toLowerCase();
  const c = (agent.capabilities || []).join(" ").toLowerCase();
  const text = r + " " + c;
  if (/analyt|data|insight|research|report|market/.test(text)) return "analyst";
  if (/creat|writ|design|content|copy|brand/.test(text))       return "creative";
  if (/code|dev|engin|technical|api|system|architect/.test(text)) return "technical";
  if (/operat|manage|project|workflow|task|execut/.test(text)) return "ops";
  return "all";
};

/* ─── Agent Card ──────────────────────────────────────────────────────────── */
function AgentCard({ agent, onChat, onDelete, onToggleVisibility, isAdmin, compact }) {
  const [hovered, setHovered] = useState(false);
  const accent = providerColor(agent.model_provider);

  if (compact) {
    return (
      <div
        data-testid={`gallery-agent-${agent.agent_id}`}
        style={{ position: "relative", cursor: "pointer" }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={() => onChat(agent.agent_id)}
      >
        <div className="holo-shimmer maars-agent-card" style={{
          background: T.glass, border: `1px solid ${hovered ? accent + "55" : T.border}`,
          borderRadius: 16, overflow: "hidden", transition: "all 0.25s",
          opacity: agent.hidden ? 0.4 : 1, position: "relative",
          transform: hovered ? "translateY(-4px) scale(1.02)" : "none",
          boxShadow: hovered ? `0 12px 36px ${accent}28, 0 0 0 1px ${accent}20` : `0 2px 12px rgba(0,0,0,0.3)`,
        }}>
          {/* Photorealistic animated avatar */}
          <div style={{ padding: "14px 0 6px", display: "flex", justifyContent: "center", background: `radial-gradient(ellipse at 50% 0%, ${accent}18, transparent 70%)` }}>
            <AgentAvatar agent={agent} size="lg" status="online" animate showRing showPulse={hovered} />
          </div>
          <div style={{ padding: "6px 10px 10px" }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", textAlign: "center" }}>{agent.name}</p>
            <p style={{ fontSize: 10, color: accent, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", textAlign: "center" }}>{agent.role}</p>
          </div>
        </div>

        {/* Hover popup */}
        {hovered && (
          <div style={{
            position: "absolute", left: "50%", bottom: "calc(100% + 8px)", transform: "translateX(-50%)",
            width: 240, borderRadius: 16, overflow: "hidden",
            border: `1px solid ${accent}33`, boxShadow: `0 12px 48px rgba(0,0,0,0.6), 0 0 0 1px ${accent}22`,
            background: "rgba(5,10,20,0.97)", backdropFilter: "blur(24px)", zIndex: 50,
            animation: "fadeUp 0.15s ease",
          }}>
            <div style={{ padding: "16px 16px 12px", display: "flex", alignItems: "center", gap: 12, borderBottom: `1px solid ${accent}22` }}>
              <AgentAvatar agent={agent} size="md" status="online" animate showRing />
              <div>
                <span style={{ display: "inline-block", padding: "2px 8px", borderRadius: 20, background: `${accent}cc`, color: "#fff", fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>
                  {agent.model_provider || "AI"}
                </span>
                <p style={{ fontSize: 10, color: accent, fontWeight: 600 }}>{agent.role}</p>
                <p style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>{agent.name}</p>
              </div>
            </div>
            <div style={{ padding: "10px 14px 14px" }}>
              <p style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5, marginBottom: 8 }}>{agent.description}</p>
              {(agent.capabilities || []).slice(0, 3).length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {agent.capabilities.slice(0, 3).map((cap, i) => (
                    <span key={i} style={{ padding: "2px 8px", fontSize: 9, borderRadius: 20, background: `${accent}14`, color: accent, border: `1px solid ${accent}25` }}>{cap}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {isAdmin && (
          <button onClick={e => { e.stopPropagation(); onToggleVisibility(agent.agent_id); }}
            data-testid={`toggle-visibility-${agent.agent_id}`}
            style={{ position: "absolute", top: 8, right: 8, padding: 5, borderRadius: 7, background: "rgba(0,0,0,0.6)", border: "none", cursor: "pointer", opacity: hovered ? 1 : 0, transition: "opacity 0.15s", color: "#94a3b8", zIndex: 10 }}>
            {agent.hidden ? <Eye style={{ width: 12, height: 12 }} /> : <EyeOff style={{ width: 12, height: 12 }} />}
          </button>
        )}
      </div>
    );
  }

  /* Cards view */
  return (
    <div
      data-testid={`agent-card-${agent.agent_id}`}
      style={{ position: "relative", cursor: "pointer" }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onChat(agent.agent_id)}
    >
      <div className="holo-shimmer" style={{
        background: T.glass, border: `1px solid ${hovered ? accent + "44" : T.border}`,
        borderRadius: 16, padding: "14px", backdropFilter: "blur(12px)",
        transition: "all 0.22s", opacity: agent.hidden ? 0.45 : 1,
        position: "relative", overflow: "hidden",
        transform: hovered ? "translateY(-3px)" : "none",
        boxShadow: hovered ? `0 12px 32px ${accent}18, 0 0 0 1px ${accent}10` : "none",
        display: "flex", alignItems: "center", gap: 14,
      }}>
        <AgentAvatar agent={agent} size="md" status="online" animate={hovered} showRing={hovered} style={{ flexShrink: 0 }} />
        <div style={{ minWidth: 0, flex: 1 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</h3>
          <p style={{ fontSize: 11, color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginTop: 1 }}>{agent.role}</p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4, flexShrink: 0 }}>
          {agent.tools?.length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 3, color: "#475569" }}>
              <Wrench style={{ width: 9, height: 9 }} />
              <span style={{ fontSize: 9 }}>{agent.tools.length}</span>
            </div>
          )}
          {agent.capabilities?.length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
              <Zap style={{ width: 9, height: 9, color: accent, opacity: 0.7 }} />
              <span style={{ fontSize: 9, color: "#475569" }}>{agent.capabilities.length}</span>
            </div>
          )}
        </div>
      </div>

      {/* Hover popup */}
      {hovered && (
        <div style={{
          position: "absolute", left: "50%", bottom: "calc(100% + 8px)", transform: "translateX(-50%)",
          width: 260, borderRadius: 16, overflow: "hidden",
          border: `1px solid ${accent}33`, boxShadow: `0 16px 56px rgba(0,0,0,0.7), 0 0 0 1px ${accent}18`,
          background: "rgba(5,10,20,0.97)", backdropFilter: "blur(24px)", zIndex: 50,
          animation: "fadeUp 0.15s ease",
        }}>
          <div style={{ padding: "16px 16px 12px", display: "flex", alignItems: "center", gap: 12, borderBottom: `1px solid ${accent}22`, background: `radial-gradient(ellipse at 50% 0%, ${accent}12, transparent 70%)` }}>
            <AgentAvatar agent={agent} size="lg" status="online" animate showRing />
            <div>
              <span style={{ display: "inline-block", padding: "2px 8px", borderRadius: 20, background: `${accent}cc`, color: "#fff", fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>
                {agent.model_provider || "AI"}
              </span>
              <p style={{ fontSize: 10, color: accent, fontWeight: 600 }}>{agent.role}</p>
              <p style={{ fontSize: 15, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>{agent.name}</p>
            </div>
          </div>
          <div style={{ padding: "10px 14px 14px" }}>
            <p style={{ fontSize: 11, color: "#64748b", lineHeight: 1.55, marginBottom: 10 }}>{agent.description}</p>
            {(agent.capabilities || []).slice(0, 4).length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 10 }}>
                {agent.capabilities.slice(0, 4).map((cap, i) => (
                  <span key={i} style={{ padding: "2px 8px", fontSize: 9, borderRadius: 20, background: `${accent}12`, color: accent, border: `1px solid ${accent}22` }}>{cap}</span>
                ))}
              </div>
            )}
            <button
              onClick={e => { e.stopPropagation(); onChat(agent.agent_id); }}
              style={{ width: "100%", padding: "8px 0", borderRadius: 9, background: `linear-gradient(135deg, ${accent}cc, ${T.blue}cc)`, color: "#030712", fontSize: 12, fontWeight: 700, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
              <MessageSquare style={{ width: 12, height: 12 }} /> Chat with {agent.name.split(" ")[0]}
            </button>
          </div>
        </div>
      )}

      {isAdmin && (
        <button onClick={e => { e.stopPropagation(); onToggleVisibility(agent.agent_id); }}
          data-testid={`toggle-card-visibility-${agent.agent_id}`}
          style={{ position: "absolute", top: 10, right: 10, padding: 5, borderRadius: 7, background: "rgba(0,0,0,0.6)", border: "none", cursor: "pointer", opacity: hovered ? 1 : 0, transition: "opacity 0.15s", color: "#94a3b8", zIndex: 10 }}>
          {agent.hidden ? <Eye style={{ width: 12, height: 12 }} /> : <EyeOff style={{ width: 12, height: 12 }} />}
        </button>
      )}
    </div>
  );
}

/* ─── Custom agent card (larger, with delete) ─────────────────────────────── */
function CustomAgentCard({ agent, onChat, onDelete }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      data-testid={`custom-agent-card-${agent.agent_id}`}
      style={{
        padding: 1.5, borderRadius: 19,
        background: hovered
          ? "linear-gradient(135deg, rgba(124,58,237,0.8), rgba(79,209,197,0.5), rgba(37,99,235,0.6), rgba(124,58,237,0.7))"
          : "linear-gradient(135deg, rgba(124,58,237,0.3), rgba(79,209,197,0.15), rgba(124,58,237,0.25))",
        backgroundSize: "300% 300%", animation: "holo 8s ease infinite",
        transition: "all 0.25s",
        transform: hovered ? "translateY(-2px)" : "none",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
    <div className="holo-shimmer" style={{
        background: T.glass, borderRadius: 18, padding: "20px", backdropFilter: "blur(12px)",
        position: "relative", overflow: "hidden",
        boxShadow: hovered ? "0 12px 40px rgba(124,58,237,0.15)" : "none",
        transition: "box-shadow 0.25s",
      }}
    >
      <div style={{ position: "absolute", top: -30, right: -30, width: 100, height: 100, borderRadius: "50%", background: "radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)", pointerEvents: "none" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 12 }}>
        <AgentAvatar agent={agent} size="md" status="online" animate showRing showPulse={false} />
        <div style={{ minWidth: 0, flex: 1 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</h3>
          <p style={{ fontSize: 11, color: "#7c3aed", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.role}</p>
        </div>
      </div>
      <p style={{ fontSize: 12, color: "#475569", lineHeight: 1.55, marginBottom: 16, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{agent.description}</p>
      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => onChat(agent.agent_id)}
          style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "9px 0", borderRadius: 10, background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.2)", color: "#a78bfa", fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.background = "rgba(124,58,237,0.22)"; }}
          onMouseLeave={e => { e.currentTarget.style.background = "rgba(124,58,237,0.12)"; }}>
          <MessageSquare style={{ width: 13, height: 13 }} /> Chat
        </button>
        <button onClick={() => onDelete(agent.agent_id)}
          style={{ padding: "9px 12px", borderRadius: 10, background: "transparent", border: `1px solid ${T.border}`, color: "#475569", cursor: "pointer", transition: "all 0.15s", display: "flex", alignItems: "center" }}
          onMouseEnter={e => { e.currentTarget.style.color = "#f87171"; e.currentTarget.style.borderColor = "rgba(248,113,113,0.3)"; e.currentTarget.style.background = "rgba(248,113,113,0.06)"; }}
          onMouseLeave={e => { e.currentTarget.style.color = "#475569"; e.currentTarget.style.borderColor = T.border; e.currentTarget.style.background = "transparent"; }}>
          <Trash2 style={{ width: 13, height: 13 }} />
        </button>
      </div>
    </div>
    </div>
  );
}

/* ─── Agents page ─────────────────────────────────────────────────────────── */
const Agents = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [agents,          setAgents]          = useState([]);
  const [loading,         setLoading]         = useState(true);
  const [viewMode,        setViewMode]        = useState("cards");
  const [searchQuery,     setSearchQuery]     = useState("");
  const [activeCategory,  setActiveCategory]  = useState("all");
  const [genState,        setGenState]        = useState(null);  // portrait generation progress

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const isAdmin = user?.email === "management.maars@marsgc.com" || user?.is_admin;

  useEffect(() => { fetchAgents(); }, []);

  // Poll portrait generation progress while running
  useEffect(() => {
    if (!genState?.running) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/admin/generate-avatars/status`, { headers });
        if (res.ok) {
          const s = await res.json();
          setGenState(s);
          if (!s.running) { clearInterval(interval); fetchAgents(); toast.success("Portrait generation complete!"); }
        }
      } catch {}
    }, 2000);
    return () => clearInterval(interval);
  }, [genState?.running]);

  const triggerPortraitGeneration = async () => {
    try {
      const res = await fetch(`${API}/admin/generate-avatars`, { method: "POST", headers });
      const data = await res.json();
      if (data.status === "started") {
        setGenState({ running: true, total: data.agents_queued, done: 0, failed: 0 });
        toast.success(`Generating portraits for ${data.agents_queued} agents…`);
      } else if (data.status === "all_done") {
        toast.success("All agents already have portrait photos!");
      } else if (data.status === "already_running") {
        setGenState(data);
        toast.info("Portrait generation already in progress");
      } else {
        toast.error(data.message || "Failed to start generation");
      }
    } catch { toast.error("Failed to connect to server"); }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API}/agents`, { headers });
      if (response.ok) setAgents(await response.json());
    } catch { toast.error("Failed to load agents"); }
    finally { setLoading(false); }
  };

  const deleteAgent = async (agentId) => {
    try {
      const response = await fetch(`${API}/agents/${agentId}`, { method: "DELETE", headers });
      if (response.ok) { setAgents(prev => prev.filter(a => a.agent_id !== agentId)); toast.success("Agent deleted"); }
      else { const data = await response.json(); toast.error(data.detail || "Failed to delete agent"); }
    } catch { toast.error("Failed to delete agent"); }
  };

  const toggleAgentVisibility = async (agentId) => {
    try {
      const agent = agents.find(a => a.agent_id === agentId);
      const newHidden = !agent.hidden;
      const response = await fetch(`${API}/agents/${agentId}/visibility`, {
        method: "PUT", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ hidden: newHidden }),
      });
      if (response.ok) {
        setAgents(prev => prev.map(a => a.agent_id === agentId ? { ...a, hidden: newHidden } : a));
        toast.success(newHidden ? "Agent hidden" : "Agent visible");
      }
    } catch { toast.error("Failed to update visibility"); }
  };

  const filtered = agents.filter(a => {
    const matchSearch = !searchQuery || (() => {
      const q = searchQuery.toLowerCase();
      return a.name?.toLowerCase().includes(q) || a.role?.toLowerCase().includes(q) ||
             a.capabilities?.some(c => c.toLowerCase().includes(q));
    })();
    const matchCat = activeCategory === "all" || agentCategory(a) === activeCategory ||
                     (activeCategory === "custom" && a.is_custom);
    return matchSearch && matchCat;
  });

  const defaultAgents = filtered.filter(a => !a.is_custom);
  const customAgents  = filtered.filter(a => a.is_custom);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "80px 0", flexDirection: "column", gap: 16 }}>
        <div style={{ position: "relative", width: 44, height: 44 }}>
          <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: `2px solid transparent`, borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.3)", animation: "spin 0.9s linear infinite" }} />
          <div style={{ position: "absolute", inset: 5, borderRadius: "50%", border: `2px solid transparent`, borderBottomColor: T.violet, borderLeftColor: "rgba(124,58,237,0.3)", animation: "spin 0.6s linear infinite reverse" }} />
        </div>
        <p style={{ fontSize: 13, color: "#475569", letterSpacing: "0.08em" }}>Initializing agents…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div data-testid="agents-page">
      <style>{`
        @keyframes fadeUp       { from { opacity: 0; transform: translateX(-50%) translateY(6px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
        @keyframes spin         { to { transform: rotate(360deg); } }
        @keyframes ag_pulse     { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(1.5); } }
        @keyframes ag_bar       { 0%,100% { transform:scaleY(0.4); } 50% { transform:scaleY(1); } }
        @keyframes neural-pulse { 0%,100% { opacity:0.2; transform:scale(1); } 50% { opacity:0.6; transform:scale(1.6); } }
      `}</style>

      {/* ── Live stat strip ──────────────────────────── */}
      <div style={{ display: "flex", gap: 10, marginBottom: 24, overflowX: "auto", paddingBottom: 2 }}>
        {[
          { label: "Total Agents",   value: agents.length,                         color: T.teal,   dot: true },
          { label: "Active",         value: agents.filter(a => !a.hidden).length,   color: "#34d399", dot: true },
          { label: "Custom Built",   value: agents.filter(a => a.is_custom).length, color: T.violet, dot: false },
          { label: "Analysts",       value: agents.filter(a => agentCategory(a) === "analyst").length,   color: "#60a5fa", dot: false },
          { label: "Creative",       value: agents.filter(a => agentCategory(a) === "creative").length,  color: "#a78bfa", dot: false },
          { label: "Technical",      value: agents.filter(a => agentCategory(a) === "technical").length, color: T.teal,   dot: false },
        ].map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "7px 14px", borderRadius: 20, background: "rgba(8,15,28,0.6)", border: `1px solid rgba(255,255,255,0.06)`, backdropFilter: "blur(8px)", flexShrink: 0 }}>
            {s.dot && <div style={{ width: 6, height: 6, borderRadius: "50%", background: s.color, animation: "ag_pulse 2s ease-in-out infinite" }} />}
            <span style={{ fontSize: 17, fontWeight: 800, color: s.color, fontFamily: "Outfit, sans-serif", lineHeight: 1 }}>{s.value}</span>
            <span style={{ fontSize: 11, color: "#475569", fontWeight: 500 }}>{s.label}</span>
          </div>
        ))}
        {/* Live waveform indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 20, background: "rgba(8,15,28,0.6)", border: "1px solid rgba(79,209,197,0.12)", backdropFilter: "blur(8px)", flexShrink: 0 }}>
          {[0,1,2,3,4].map(i => (
            <div key={i} style={{ width: 3, height: 14, borderRadius: 2, background: T.teal, animation: `ag_bar 0.7s ease-in-out ${i * 0.1}s infinite`, opacity: 0.7 }} />
          ))}
          <span style={{ fontSize: 11, color: T.teal, fontWeight: 600, marginLeft: 4 }}>LIVE</span>
        </div>
      </div>

      {/* ── Header ─────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28, position: "relative" }}>
        {/* Neural constellation background */}
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none", overflow: "hidden" }}>
          {[
            { x: "8%", y: "15%", size: 5, delay: "0s" },
            { x: "25%", y: "55%", size: 3, delay: "1.2s" },
            { x: "45%", y: "20%", size: 4, delay: "0.6s" },
          ].map((n, i) => (
            <div key={i} style={{ position: "absolute", left: n.x, top: n.y, width: n.size, height: n.size, borderRadius: "50%", background: T.teal, opacity: 0.25, animation: `neural-pulse ${2 + i * 0.5}s ease-in-out ${n.delay} infinite` }} />
          ))}
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <span style={{ width: 24, height: 1, background: `linear-gradient(90deg, ${T.teal}, ${T.violet})` }} />
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: T.teal }}>AI Workforce</span>
            <div className="waveform" style={{ height: 12 }}><span /><span /><span /></div>
          </div>
          <h1 style={{ fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800, fontFamily: "Outfit, sans-serif", lineHeight: 1.1, margin: 0, background: `linear-gradient(135deg, #f1f5f9 50%, ${T.teal} 80%)`, backgroundSize: "200% 200%", animation: "holo 8s ease infinite", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
            Agent Roster
          </h1>
          <p style={{ fontSize: 13, color: "#475569", marginTop: 5 }}>
            <span style={{ color: T.teal }}>{agents.filter(a => !a.hidden).length}</span> active ·{" "}
            <span style={{ color: T.violet }}>{agents.filter(a => a.is_custom).length}</span> custom
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* View toggle */}
          <div data-testid="view-toggle" style={{ display: "flex", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 10, padding: 3, gap: 2 }}>
            <button onClick={() => setViewMode("cards")}
              data-testid="view-cards"
              style={{ padding: "6px 8px", borderRadius: 8, border: "none", cursor: "pointer", transition: "all 0.15s", background: viewMode === "cards" ? "rgba(79,209,197,0.15)" : "transparent", color: viewMode === "cards" ? T.teal : "#475569" }}>
              <LayoutGrid style={{ width: 15, height: 15 }} />
            </button>
            <button onClick={() => setViewMode("gallery")}
              data-testid="view-gallery"
              style={{ padding: "6px 8px", borderRadius: 8, border: "none", cursor: "pointer", transition: "all 0.15s", background: viewMode === "gallery" ? "rgba(79,209,197,0.15)" : "transparent", color: viewMode === "gallery" ? T.teal : "#475569" }}>
              <Grid3X3 style={{ width: 15, height: 15 }} />
            </button>
          </div>

          {/* Generate Portraits (admin only) */}
          {isAdmin && (
            <button
              onClick={triggerPortraitGeneration}
              disabled={genState?.running}
              title="Generate AI photorealistic portraits for all agents"
              style={{ display: "flex", alignItems: "center", gap: 7, padding: "10px 14px", borderRadius: 11, background: genState?.running ? "rgba(167,139,250,0.08)" : "rgba(167,139,250,0.12)", border: `1px solid ${genState?.running ? "rgba(167,139,250,0.2)" : "rgba(167,139,250,0.3)"}`, color: "#a78bfa", fontSize: 12, fontWeight: 700, cursor: genState?.running ? "default" : "pointer", transition: "all 0.15s" }}
              onMouseEnter={e => { if (!genState?.running) e.currentTarget.style.background = "rgba(167,139,250,0.2)"; }}
              onMouseLeave={e => { if (!genState?.running) e.currentTarget.style.background = "rgba(167,139,250,0.12)"; }}>
              {genState?.running
                ? <><Loader2 style={{ width: 13, height: 13, animation: "spin 1s linear infinite" }} /> {genState.done}/{genState.total}</>
                : <><ImagePlus style={{ width: 13, height: 13 }} /> Generate Portraits</>}
            </button>
          )}

          {/* Create agent */}
          <button onClick={() => navigate("/agents/create")}
            data-testid="create-agent-btn"
            style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 18px", borderRadius: 11, background: `linear-gradient(135deg, ${T.teal}, ${T.blue})`, color: "#030712", fontSize: 13, fontWeight: 700, border: "none", cursor: "pointer", boxShadow: "0 0 24px rgba(79,209,197,0.25)", transition: "box-shadow 0.2s" }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = "0 0 40px rgba(79,209,197,0.45)"}
            onMouseLeave={e => e.currentTarget.style.boxShadow = "0 0 24px rgba(79,209,197,0.25)"}>
            <Plus style={{ width: 15, height: 15 }} /> Create Agent
          </button>
        </div>
      </div>

      {/* ── Search ─────────────────────────────────── */}
      <div style={{ position: "relative", marginBottom: 20 }}>
        <Search style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", width: 15, height: 15, color: "#475569", pointerEvents: "none" }} />
        <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
          placeholder="Search agents by name, role, or capability…"
          data-testid="agent-search"
          style={{ width: "100%", paddingLeft: 42, paddingRight: 16, height: 44, borderRadius: 12, background: T.glass, border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 14, outline: "none", backdropFilter: "blur(12px)", boxSizing: "border-box", transition: "border-color 0.15s" }}
          onFocus={e => e.target.style.borderColor = "rgba(79,209,197,0.3)"}
          onBlur={e => e.target.style.borderColor = T.border} />
      </div>

      {/* ── Category tabs ──────────────────────────── */}
      <div style={{ display: "flex", gap: 6, marginBottom: 28, overflowX: "auto", paddingBottom: 4 }}>
        {CATEGORIES.map(cat => (
          <button key={cat.id} onClick={() => setActiveCategory(cat.id)}
            style={{
              padding: "6px 14px", borderRadius: 20, fontSize: 12, fontWeight: 600,
              border: `1px solid ${activeCategory === cat.id ? "rgba(79,209,197,0.4)" : T.border}`,
              background: activeCategory === cat.id ? "rgba(79,209,197,0.1)" : T.glass,
              color: activeCategory === cat.id ? T.teal : "#475569",
              cursor: "pointer", transition: "all 0.15s", whiteSpace: "nowrap",
              backdropFilter: "blur(8px)",
              boxShadow: activeCategory === cat.id ? "0 0 12px rgba(79,209,197,0.15)" : "none",
            }}>
            {cat.label}
            {cat.id !== "all" && (
              <span style={{ marginLeft: 5, fontSize: 10, opacity: 0.7 }}>
                ({agents.filter(a => agentCategory(a) === cat.id || (cat.id === "custom" && a.is_custom)).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Agent grid ─────────────────────────────── */}
      {viewMode === "gallery" ? (
        <div data-testid="gallery-view">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Sparkles style={{ width: 14, height: 14, color: T.teal }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", fontFamily: "Outfit, sans-serif" }}>Agent Gallery</span>
            <span style={{ fontSize: 11, color: "#475569" }}>{defaultAgents.length} agents</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(110px, 1fr))", gap: 10 }}>
            {defaultAgents.map(agent => (
              <AgentCard key={agent.agent_id} agent={agent} compact
                onChat={id => navigate(`/chat/${id}`)}
                onDelete={deleteAgent}
                onToggleVisibility={toggleAgentVisibility}
                isAdmin={user?.is_admin} />
            ))}
          </div>
        </div>
      ) : (
        <div data-testid="cards-view">
          {activeCategory !== "custom" && defaultAgents.length > 0 && (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                <Sparkles style={{ width: 14, height: 14, color: T.teal }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", fontFamily: "Outfit, sans-serif" }}>Specialized Agents</span>
                <span style={{ fontSize: 11, color: "#475569" }}>{defaultAgents.length}</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 10, marginBottom: 40 }}>
                {defaultAgents.map(agent => (
                  <AgentCard key={agent.agent_id} agent={agent}
                    onChat={id => navigate(`/chat/${id}`)}
                    onDelete={deleteAgent}
                    onToggleVisibility={toggleAgentVisibility}
                    isAdmin={user?.is_admin} />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* ── Custom Agents ──────────────────────────── */}
      {(activeCategory === "all" || activeCategory === "custom") && (
        <div style={{ marginTop: activeCategory === "custom" ? 0 : 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Bot style={{ width: 14, height: 14, color: T.violet }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", fontFamily: "Outfit, sans-serif" }}>Your Custom Agents</span>
          </div>

          {customAgents.length > 0 ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
              {customAgents.map(agent => (
                <CustomAgentCard key={agent.agent_id} agent={agent}
                  onChat={id => navigate(`/chat/${id}`)}
                  onDelete={deleteAgent} />
              ))}
            </div>
          ) : (
            <div style={{ padding: "48px 0", textAlign: "center", border: `1px dashed rgba(124,58,237,0.15)`, borderRadius: 18, background: "rgba(124,58,237,0.03)" }}>
              <div style={{ width: 56, height: 56, borderRadius: "50%", background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.2)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
                <Bot style={{ width: 24, height: 24, color: T.violet }} />
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: "#e2e8f0", fontFamily: "Outfit, sans-serif", marginBottom: 8 }}>No Custom Agents Yet</h3>
              <p style={{ fontSize: 13, color: "#475569", marginBottom: 24 }}>Build agents tailored to your workflow.</p>
              <button onClick={() => navigate("/agents/create")}
                style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "11px 24px", borderRadius: 11, background: `linear-gradient(135deg, ${T.violet}, ${T.blue})`, color: "#f1f5f9", fontSize: 13, fontWeight: 700, border: "none", cursor: "pointer", boxShadow: "0 0 24px rgba(124,58,237,0.3)" }}>
                <Plus style={{ width: 15, height: 15 }} /> Create Your First Agent
              </button>
            </div>
          )}
        </div>
      )}

      {/* No results */}
      {filtered.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "60px 0" }}>
          <p style={{ fontSize: 14, color: "#475569" }}>No agents match your search.</p>
          <button onClick={() => { setSearchQuery(""); setActiveCategory("all"); }}
            style={{ marginTop: 12, fontSize: 12, color: T.teal, background: "none", border: "none", cursor: "pointer" }}>
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
};

export default Agents;
