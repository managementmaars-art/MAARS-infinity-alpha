/**
 * MessengerChat — Floating draggable chat dock
 *
 * • Pill dock: Commander avatar + "+" button, draggable anywhere
 * • Click Commander → opens Commander chat window
 * • Click "+" → agent picker (all agents, searchable)
 * • Each chat window is independently draggable
 * • Minimized chats collapse to heads in the dock
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import AgentAvatar from "./AgentAvatar";
import { Send, X, Minus, Maximize2, Rocket, FolderPlus, Loader2, Search, Plus } from "lucide-react";
import { toast } from "sonner";

const _BASE = process.env.REACT_APP_BACKEND_URL?.trim() || "";
const API   = `${_BASE}/api`;
const EA  = "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/";

const COMMANDER = {
  agent_id: "commander_orion",
  name: "Commander Orion",
  role: "AI Commander",
  isCommander: true,
  avatar: EA + "9a3eb3186a873a3337de51d37d80e0dac2da6db7ef21b2bef016307c59557b27.png",
};

/* ── avatar helper ─────────────────────────────────────────────────────────── */
const getAvatar = (agent = {}) => {
  const av = agent.avatar || "";
  if (av && !av.includes("dicebear.com")) return av;
  let h = 0;
  const seed = agent.name || agent.agent_id || "agent";
  for (let i = 0; i < seed.length; i++) h = ((h << 5) - h) + seed.charCodeAt(i);
  const idx = Math.abs(h) % 70 + 1;
  const fem = /a$|ia$|na$|la$|ra$|sa$|ta$|elle$|ley$/i.test(seed.split(" ")[0]);
  return `https://randomuser.me/api/portraits/${fem ? "women" : "men"}/${idx}.jpg`;
};

/* ── useMouseDrag — returns [pos, dragHandleProps, setPos] ──────────────────── */
function useMouseDrag(init) {
  const [pos, setPos] = useState(init);
  const ref = useRef({ dragging: false, sx: 0, sy: 0, px: 0, py: 0 });

  const onMouseDown = useCallback((e) => {
    if (e.target.closest("button,input,textarea,a")) return;
    ref.current = { dragging: true, sx: e.clientX, sy: e.clientY, px: pos.x, py: pos.y };
    e.preventDefault();
  }, [pos]);

  useEffect(() => {
    const move = (e) => {
      if (!ref.current.dragging) return;
      setPos({
        x: Math.max(40, Math.min(window.innerWidth  - 40, ref.current.px + e.clientX - ref.current.sx)),
        y: Math.max(40, Math.min(window.innerHeight - 40, ref.current.py + e.clientY - ref.current.sy)),
      });
    };
    const up = () => { ref.current.dragging = false; };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
    return () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
  }, []);

  return [pos, onMouseDown, setPos];
}

/* ── ChatWindow — individual draggable window ──────────────────────────────── */
function ChatWindow({ agent, onClose, onMinimize, initPos }) {
  const { token } = useAuth();
  const navigate  = useNavigate();
  const [pos, onDragHeader] = useMouseDrag(initPos);
  const [minimized, setMinimized] = useState(false);
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState("");
  const [sending, setSending]     = useState(false);
  const [chatId, setChatId]       = useState(null);
  const [projectMode, setProjectMode]   = useState(false);
  const [projectGoal, setProjectGoal]   = useState("");
  const [creatingProject, setCreating]  = useState(false);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const isCommander = agent.isCommander || agent.agent_id === "commander_orion";
  const accent = isCommander ? "#f59e0b" : "#4fd1c5";
  const imgSrc = getAvatar(agent);

  useEffect(() => { if (!minimized) bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, minimized]);
  useEffect(() => { if (!minimized) setTimeout(() => inputRef.current?.focus(), 120); }, [minimized]);

  const getOrCreate = useCallback(async () => {
    if (chatId) return chatId;
    const res = await fetch(`${API}/chats`, {
      method: "POST", headers: h,
      body: JSON.stringify({ agent_id: isCommander ? "commander_orion" : agent.agent_id }),
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    setChatId(data.chat_id);
    return data.chat_id;
  }, [chatId, agent.agent_id, isCommander]);

  const sendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || sending) return;
    const text = input.trim();
    if (isCommander && text.toLowerCase().startsWith("/project ")) {
      setProjectGoal(text.slice(9).trim()); setProjectMode(true); setInput(""); return;
    }
    setMessages(p => [...p, { role: "user", content: text, id: Date.now() }]);
    setInput(""); setSending(true);
    try {
      const cid = await getOrCreate();
      const res = await fetch(`${API}/chats/${cid}/messages`, {
        method: "POST", headers: h,
        body: JSON.stringify({ content: text, model_provider: "auto", model_name: "auto" }),
      });
      if (res.ok) {
        const d = await res.json();
        setMessages(p => [...p, { role: "assistant", content: d.assistant_message?.content || "...", id: Date.now() + 1 }]);
      }
    } catch { toast.error("Message failed"); }
    setSending(false);
  };

  const createProject = async () => {
    if (!projectGoal.trim()) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/projects`, {
        method: "POST", headers: h,
        body: JSON.stringify({ goal: projectGoal, execution_mode: "full", priority: "medium" }),
      });
      if (res.ok) {
        const p = await res.json();
        toast.success(`Project "${p.title || projectGoal.slice(0, 30)}" created!`);
        setMessages(prev => [...prev, {
          role: "assistant",
          content: `✅ Project "${p.title || projectGoal.slice(0, 40)}" created. Orchestrating agents now.`,
          id: Date.now(),
        }]);
        setProjectMode(false); setProjectGoal("");
        setTimeout(() => navigate("/projects"), 1600);
      } else { toast.error("Project creation failed"); }
    } catch { toast.error("Project creation failed"); }
    setCreating(false);
  };

  return (
    <div
      data-testid={`messenger-window-${agent.agent_id}`}
      style={{
        position: "fixed",
        left: pos.x,
        top:  pos.y,
        width: 320,
        zIndex: 10000,
        background: "rgba(8,12,22,0.98)",
        backdropFilter: "blur(28px)",
        border: `1px solid ${accent}33`,
        borderRadius: 18,
        overflow: "hidden",
        boxShadow: `0 28px 70px rgba(0,0,0,0.65), 0 0 0 1px ${accent}18`,
        display: "flex",
        flexDirection: "column",
        maxHeight: minimized ? 56 : 440,
        transition: "max-height 0.3s cubic-bezier(0.4,0,0.2,1)",
      }}
    >
      {/* ── Header (drag handle) ── */}
      <div
        onMouseDown={onDragHeader}
        style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "10px 12px",
          background: `linear-gradient(135deg, ${accent}14, transparent)`,
          borderBottom: minimized ? "none" : `1px solid ${accent}1a`,
          cursor: "grab",
          flexShrink: 0,
          userSelect: "none",
        }}
      >
        <AgentAvatar agent={agent} size="sm" status="online" animate={!minimized} showRing style={{ flexShrink: 0, pointerEvents: "none" }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", lineHeight: 1.2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{agent.name}</p>
          <p style={{ fontSize: 10, color: accent }}>{agent.role}</p>
        </div>
        <div style={{ display: "flex", gap: 4 }}>
          <button onClick={() => navigate(isCommander ? "/commander" : `/chat/${agent.agent_id}`)}
            title="Full chat" style={iconBtn}>
            <Maximize2 style={{ width: 12, height: 12 }} />
          </button>
          <button onClick={() => setMinimized(v => !v)} title={minimized ? "Expand" : "Minimize"} style={iconBtn}>
            <Minus style={{ width: 12, height: 12 }} />
          </button>
          <button onClick={onClose} title="Close" style={iconBtn}>
            <X style={{ width: 12, height: 12 }} />
          </button>
        </div>
      </div>

      {/* ── Body ── */}
      {!minimized && (
        <>
          <div style={{ flex: 1, overflowY: "auto", padding: "12px 12px 8px", display: "flex", flexDirection: "column", gap: 8, minHeight: 180 }}>
            {messages.length === 0 && (
              <div style={{ textAlign: "center", padding: "20px 8px" }}>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 10 }}>
                  <AgentAvatar agent={agent} size="lg" status="online" animate showRing showPulse />
                </div>
                <p style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 700 }}>{agent.name}</p>
                <p style={{ fontSize: 11, color: "#475569", marginTop: 4 }}>
                  {isCommander ? "Your AI Commander. Type /project <goal> to start a project." : `${agent.role} — ready to help.`}
                </p>
              </div>
            )}
            {messages.map(msg => (
              <div key={msg.id} style={{ display: "flex", flexDirection: msg.role === "user" ? "row-reverse" : "row", gap: 6, alignItems: "flex-end" }}>
                {msg.role === "assistant" && <img src={imgSrc} alt="" style={{ width: 22, height: 22, borderRadius: "50%", flexShrink: 0, objectFit: "cover" }} />}
                <div style={{
                  maxWidth: "78%", padding: "7px 10px",
                  borderRadius: msg.role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                  background: msg.role === "user" ? `linear-gradient(135deg,${accent}cc,${accent}99)` : "rgba(255,255,255,0.07)",
                  fontSize: 12, lineHeight: 1.5,
                  color: msg.role === "user" ? "#030712" : "#e2e8f0",
                  wordBreak: "break-word",
                }}>{msg.content}</div>
              </div>
            ))}
            {sending && (
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <img src={imgSrc} alt="" style={{ width: 22, height: 22, borderRadius: "50%", objectFit: "cover" }} />
                <div style={{ padding: "7px 12px", background: "rgba(255,255,255,0.07)", borderRadius: "14px 14px 14px 4px", display: "flex", gap: 4 }}>
                  {[1,2,3].map(i => <div key={i} className={`maars-typing-dot-${i}`} style={{ width: 5, height: 5, borderRadius: "50%", background: accent }} />)}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Commander project overlay */}
          {projectMode && (
            <div style={{ position: "absolute", inset: 56, background: "rgba(8,12,22,0.98)", backdropFilter: "blur(12px)", display: "flex", flexDirection: "column", gap: 12, padding: 16, zIndex: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(245,158,11,0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <FolderPlus style={{ width: 16, height: 16, color: "#f59e0b" }} />
                </div>
                <div>
                  <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Initiate Project</p>
                  <p style={{ fontSize: 10, color: "#64748b" }}>Commander will decompose & execute</p>
                </div>
              </div>
              <textarea value={projectGoal} onChange={e => setProjectGoal(e.target.value)} placeholder="Describe the goal…"
                style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 10, padding: 10, color: "#e2e8f0", fontSize: 12, resize: "none", outline: "none" }}
                rows={4} autoFocus />
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={() => { setProjectMode(false); setProjectGoal(""); }}
                  style={{ flex: 1, padding: "8px 0", borderRadius: 8, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", color: "#64748b", fontSize: 12, cursor: "pointer" }}>
                  Cancel
                </button>
                <button onClick={createProject} disabled={creatingProject || !projectGoal.trim()}
                  style={{ flex: 2, padding: "8px 0", borderRadius: 8, background: creatingProject || !projectGoal.trim() ? "rgba(245,158,11,0.3)" : "linear-gradient(135deg,#f59e0b,#d97706)", border: "none", color: "#030712", fontSize: 12, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                  {creatingProject ? <Loader2 style={{ width: 13, height: 13, animation: "ms_spin 1s linear infinite" }} /> : <Rocket style={{ width: 13, height: 13 }} />}
                  {creatingProject ? "Launching…" : "Launch Project"}
                </button>
              </div>
            </div>
          )}

          <form onSubmit={sendMessage} style={{ display: "flex", gap: 8, padding: "8px 12px 12px", borderTop: "1px solid rgba(255,255,255,0.06)", flexShrink: 0 }}>
            <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder={isCommander ? "Ask or /project…" : "Message…"}
              style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 20, padding: "7px 12px", color: "#e2e8f0", fontSize: 12, outline: "none" }}
            />
            <button type="submit" disabled={!input.trim() || sending}
              style={{ width: 32, height: 32, borderRadius: "50%", background: !input.trim() || sending ? "rgba(255,255,255,0.06)" : `linear-gradient(135deg,${accent},${accent}cc)`, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Send style={{ width: 13, height: 13, color: !input.trim() || sending ? "#64748b" : "#030712" }} />
            </button>
          </form>
        </>
      )}
    </div>
  );
}

const iconBtn = {
  background: "none", border: "none", cursor: "pointer", padding: 4,
  color: "#64748b", display: "flex", alignItems: "center", justifyContent: "center",
  borderRadius: 6, transition: "color 0.15s",
};

/* ── AgentPicker modal ──────────────────────────────────────────────────────── */
function AgentPicker({ onSelect, onClose, position }) {
  const { token } = useAuth();
  const [agents, setAgents]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch]   = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/agents`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : [])
      .then(d => setAgents(Array.isArray(d) ? d : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => { setTimeout(() => inputRef.current?.focus(), 80); }, []);

  const filtered = agents.filter(a => {
    if (!search) return true;
    const q = search.toLowerCase();
    return a.name?.toLowerCase().includes(q) || a.role?.toLowerCase().includes(q);
  });

  // Position the picker above/beside the dock
  const pickerStyle = {
    position: "fixed",
    right:  window.innerWidth  - position.x - 20,
    bottom: window.innerHeight - position.y + 20,
    zIndex: 10001,
    width: 310,
    maxHeight: 440,
    background: "rgba(8,12,22,0.98)",
    backdropFilter: "blur(28px)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 18,
    display: "flex",
    flexDirection: "column",
    boxShadow: "0 28px 70px rgba(0,0,0,0.6)",
    overflow: "hidden",
    animation: "ms_pickerIn 0.18s ease",
  };

  return (
    <div style={pickerStyle}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 14px 8px" }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "#64748b", letterSpacing: "0.12em", textTransform: "uppercase" }}>Start a Chat</span>
        <button onClick={onClose} style={{ ...iconBtn, color: "#475569" }}><X style={{ width: 13, height: 13 }} /></button>
      </div>

      {/* Commander pinned */}
      <div style={{ padding: "0 10px 8px" }}>
        <button onClick={() => onSelect(COMMANDER)}
          style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", borderRadius: 12, background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", cursor: "pointer", transition: "background 0.15s" }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(245,158,11,0.15)"}
          onMouseLeave={e => e.currentTarget.style.background = "rgba(245,158,11,0.08)"}>
          <AgentAvatar agent={COMMANDER} size="sm" showStatus={false} showRing={false} animate={false} />
          <div style={{ textAlign: "left" }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#f59e0b" }}>Commander Orion</p>
            <p style={{ fontSize: 10, color: "#64748b" }}>AI Commander · /project to launch a project</p>
          </div>
        </button>
      </div>

      {/* Search */}
      <div style={{ position: "relative", padding: "0 10px 8px" }}>
        <Search style={{ position: "absolute", left: 22, top: "50%", transform: "translateY(-50%)", width: 13, height: 13, color: "#475569", pointerEvents: "none" }} />
        <input ref={inputRef} value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search all agents…"
          style={{ width: "100%", paddingLeft: 34, height: 34, borderRadius: 10, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "#e2e8f0", fontSize: 12, outline: "none", boxSizing: "border-box" }}
        />
      </div>

      {/* Agent grid — scrollable */}
      <div style={{ overflowY: "auto", padding: "0 10px 12px", flex: 1 }}>
        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            {Array(6).fill(0).map((_, i) => <div key={i} style={{ height: 52, borderRadius: 10, background: "rgba(255,255,255,0.04)", animation: "ms_shimmer 1.2s ease-in-out infinite" }} />)}
          </div>
        ) : filtered.length === 0 ? (
          <p style={{ fontSize: 12, color: "#475569", textAlign: "center", padding: "16px 0" }}>No agents found</p>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            {filtered.map(a => (
              <button key={a.agent_id} onClick={() => onSelect(a)}
                style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", borderRadius: 10, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", cursor: "pointer", transition: "background 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.09)"}
                onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.04)"}>
                <AgentAvatar agent={a} size="xs" showStatus={false} showRing={false} animate={false} />
                <div style={{ textAlign: "left", overflow: "hidden" }}>
                  <p style={{ fontSize: 11, fontWeight: 600, color: "#e2e8f0", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: 88 }}>{a.name}</p>
                  <p style={{ fontSize: 9, color: "#64748b", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: 88 }}>{a.role}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Main MessengerChat ─────────────────────────────────────────────────────── */
export default function MessengerChat() {
  const { token } = useAuth();

  // Dock position (draggable pill)
  const [dockPos, onDockDrag] = useMouseDrag({
    x: window.innerWidth  - 80,
    y: window.innerHeight - 80,
  });

  const [openChats,   setOpenChats]   = useState([]);   // array of agent objects
  const [pickerOpen,  setPickerOpen]  = useState(false);

  const openChat = (agent) => {
    setPickerOpen(false);
    if (openChats.find(a => a.agent_id === agent.agent_id)) return;
    setOpenChats(prev => [...prev, agent].slice(-4));
  };

  const closeChat = (agentId) => {
    setOpenChats(prev => prev.filter(a => a.agent_id !== agentId));
  };

  // Calculate staggered initial positions for new windows
  const windowInitPos = (index) => ({
    x: Math.max(20, dockPos.x - 340 - index * 330),
    y: Math.max(20, dockPos.y - 440),
  });

  if (!token) return null;

  return (
    <>
      <style>{`
        @keyframes ms_spin      { to { transform: rotate(360deg); } }
        @keyframes ms_pickerIn  { from { opacity:0; transform:scale(0.94) translateY(6px); } to { opacity:1; transform:scale(1) translateY(0); } }
        @keyframes ms_shimmer   { 0%,100%{opacity:0.5} 50%{opacity:1} }
      `}</style>

      {/* Open chat windows */}
      {openChats.map((agent, i) => (
        <ChatWindow
          key={agent.agent_id}
          agent={agent}
          onClose={() => closeChat(agent.agent_id)}
          initPos={windowInitPos(i)}
        />
      ))}

      {/* Agent picker */}
      {pickerOpen && (
        <AgentPicker
          onSelect={openChat}
          onClose={() => setPickerOpen(false)}
          position={dockPos}
        />
      )}

      {/* Draggable dock pill */}
      <div
        onMouseDown={onDockDrag}
        style={{
          position: "fixed",
          left: dockPos.x,
          top:  dockPos.y,
          transform: "translate(-50%, -50%)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 12px 8px 8px",
          borderRadius: 40,
          background: "rgba(8,12,22,0.92)",
          backdropFilter: "blur(24px)",
          border: "1px solid rgba(255,255,255,0.1)",
          boxShadow: "0 8px 40px rgba(0,0,0,0.55), 0 0 0 1px rgba(79,209,197,0.08)",
          cursor: "grab",
          userSelect: "none",
        }}
      >
        {/* Commander always in dock */}
        <div
          onClick={() => openChat(COMMANDER)}
          title="Chat with Commander Orion"
          style={{ cursor: "pointer", animation: "maars-head-float 3s ease-in-out infinite" }}
          onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
          onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
        >
          <AgentAvatar agent={COMMANDER} size="md" status="online" animate showRing />
        </div>

        {/* Minimized open-chat heads (click to bring back) */}
        {openChats.map(agent => (
          <div
            key={agent.agent_id}
            title={agent.name}
            style={{ cursor: "pointer", animation: "maars-head-float 3s ease-in-out infinite", position: "relative" }}
            onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
            onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
          >
            <AgentAvatar agent={agent} size="sm" status="online" animate showRing />
          </div>
        ))}

        {/* Divider */}
        {openChats.length > 0 && (
          <div style={{ width: 1, height: 28, background: "rgba(255,255,255,0.1)", flexShrink: 0, marginLeft: 2 }} />
        )}

        {/* + button to open picker */}
        <button
          onClick={() => setPickerOpen(v => !v)}
          data-testid="messenger-toggle"
          title="Start a new chat"
          style={{
            width: 40, height: 40, borderRadius: "50%",
            background: pickerOpen
              ? "linear-gradient(135deg, #7c3aed, #4f46e5)"
              : "linear-gradient(135deg, #4fd1c5, #2563eb)",
            border: "none",
            cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: `0 4px 16px ${pickerOpen ? "rgba(124,58,237,0.4)" : "rgba(79,209,197,0.35)"}`,
            transition: "all 0.25s",
            transform: pickerOpen ? "rotate(45deg)" : "rotate(0deg)",
            flexShrink: 0,
          }}
        >
          <Plus style={{ width: 18, height: 18, color: "#fff" }} />
        </button>
      </div>
    </>
  );
}
