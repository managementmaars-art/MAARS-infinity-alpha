import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import {
  Code, Play, Download, Send, Trash2, Plus, ChevronLeft,
  Loader2, Eye, FileCode, MessageSquare, Copy, Zap, Sparkles,
  Terminal, Globe, Package, CheckCircle, Clock, Layers
} from "lucide-react";
import { toast } from "sonner";

/* ─── Design tokens ──────────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  pink:   "#f472b6",
  amber:  "#f59e0b",
  green:  "#34d399",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
  glass2: "rgba(5,10,20,0.85)",
  bg:     "#030712",
};

const STARTER_PROMPTS = [
  { icon: "📊", label: "Kanban Board", prompt: "A drag-and-drop kanban board with swim lanes, card priorities, and team assignment" },
  { icon: "💰", label: "Invoice Generator", prompt: "A professional invoice generator with line items, tax calculation, PDF export, and client management" },
  { icon: "📈", label: "Analytics Dashboard", prompt: "A real-time analytics dashboard with charts, KPIs, date range filters, and CSV export" },
  { icon: "🤖", label: "AI Chat UI", prompt: "A sleek AI chat interface with message history, typing indicators, and code highlighting" },
  { icon: "🗓️", label: "Calendar App", prompt: "A full calendar app with event creation, recurring events, reminders, and team sharing" },
  { icon: "🛒", label: "E-commerce UI", prompt: "A product catalog with filters, cart, checkout flow, and order confirmation" },
];

/* ─── Keyframes injected once ────────────────────────────────────────────── */
const STYLES = `
  @keyframes vc_spin     { to { transform: rotate(360deg); } }
  @keyframes vc_fadeUp   { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
  @keyframes vc_pulse    { 0%,100% { opacity:0.6; transform:scale(1); } 50% { opacity:1; transform:scale(1.3); } }
  @keyframes vc_shimmer  { 0% { background-position:200% center; } 100% { background-position:-200% center; } }
  @keyframes vc_bar      { 0%,100% { transform:scaleY(0.4); } 50% { transform:scaleY(1); } }
  @keyframes vc_glow     { 0%,100% { box-shadow:0 0 20px rgba(244,114,182,0.3); } 50% { box-shadow:0 0 40px rgba(244,114,182,0.6); } }
`;

function FileLanguageIcon({ name = "" }) {
  const ext = name.split(".").pop()?.toLowerCase();
  const map = { html: { color: "#f97316", label: "HTML" }, css: { color: "#3b82f6", label: "CSS" }, js: { color: "#eab308", label: "JS" }, jsx: { color: "#06b6d4", label: "JSX" }, ts: { color: "#3b82f6", label: "TS" }, tsx: { color: "#06b6d4", label: "TSX" }, py: { color: "#22c55e", label: "PY" }, json: { color: "#a78bfa", label: "JSON" } };
  const m = map[ext] || { color: T.teal, label: ext?.toUpperCase() || "?" };
  return (
    <span style={{ padding: "1px 6px", borderRadius: 5, background: `${m.color}18`, color: m.color, fontSize: 9, fontWeight: 700, letterSpacing: "0.05em", border: `1px solid ${m.color}28` }}>
      {m.label}
    </span>
  );
}

const VibeCoding = () => {
  const { token } = useAuth();
  const [projects, setProjects]       = useState([]);
  const [activeProject, setActive]    = useState(null);
  const [loading, setLoading]         = useState(true);
  const [creating, setCreating]       = useState(false);
  const [chatting, setChatting]       = useState(false);
  const [prompt, setPrompt]           = useState("");
  const [chatMsg, setChatMsg]         = useState("");
  const [activeTab, setActiveTab]     = useState("preview");
  const [activeFile, setActiveFile]   = useState(0);
  const [genProgress, setGenProgress] = useState(0);
  const iframeRef = useRef(null);
  const chatEndRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchProjects = useCallback(async () => {
    try {
      const res = await fetch(`${API}/vibe/projects`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setProjects((await res.json()).items || []);
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [activeProject?.chat_history]);

  // Fake generation progress bar
  useEffect(() => {
    if (!creating) { setGenProgress(0); return; }
    setGenProgress(5);
    const steps = [15, 30, 50, 68, 82, 93];
    const timers = steps.map((v, i) => setTimeout(() => setGenProgress(v), (i + 1) * 2500));
    return () => timers.forEach(clearTimeout);
  }, [creating]);

  const createProject = async () => {
    if (!prompt.trim()) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/vibe/projects`, {
        method: "POST", headers,
        body: JSON.stringify({ description: prompt }),
      });
      if (res.ok) {
        const project = await res.json();
        setGenProgress(100);
        setTimeout(() => { setActive(project); setPrompt(""); fetchProjects(); }, 400);
        toast.success("App generated!");
      } else toast.error("Failed to generate app");
    } catch { toast.error("Error creating project"); }
    finally { setTimeout(() => setCreating(false), 500); }
  };

  const loadProject = async (vibeId) => {
    try {
      const res = await fetch(`${API}/vibe/projects/${vibeId}`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { setActive(await res.json()); setActiveTab("preview"); setActiveFile(0); }
    } catch { toast.error("Failed to load project"); }
  };

  const sendChat = async () => {
    if (!chatMsg.trim() || !activeProject) return;
    setChatting(true);
    try {
      const res = await fetch(`${API}/vibe/projects/${activeProject.vibe_id}/chat`, {
        method: "POST", headers, body: JSON.stringify({ message: chatMsg }),
      });
      if (res.ok) { setActive(await res.json()); setChatMsg(""); toast.success("Changes applied!"); }
      else toast.error("Failed to apply changes");
    } catch { toast.error("Chat error"); }
    finally { setChatting(false); }
  };

  const deleteProject = async (vibeId) => {
    if (!window.confirm("Delete this project?")) return;
    try {
      await fetch(`${API}/vibe/projects/${vibeId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      setActive(null); fetchProjects(); toast.success("Project deleted");
    } catch {}
  };

  const downloadProject = () => {
    if (!activeProject?.files) return;
    activeProject.files.forEach(f => {
      const blob = new Blob([f.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = f.name; a.click(); URL.revokeObjectURL(url);
    });
    toast.success("Files downloaded!");
  };

  const copyCode = () => {
    const file = activeProject?.files?.[activeFile];
    if (file) { navigator.clipboard.writeText(file.content); toast.success("Code copied!"); }
  };

  useEffect(() => {
    if (activeTab === "preview" && activeProject?.files && iframeRef.current) {
      const htmlFile = activeProject.files.find(f => f.name.endsWith(".html"));
      if (htmlFile) {
        const blob = new Blob([htmlFile.content], { type: "text/html" });
        iframeRef.current.src = URL.createObjectURL(blob);
      }
    }
  }, [activeTab, activeProject, activeFile]);

  /* ── Project list view ──────────────────────────────────────────────────── */
  if (!activeProject) {
    return (
      <div data-testid="vibe-coding" style={{ animation: "vc_fadeUp 0.35s ease" }}>
        <style>{STYLES}</style>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 28 }}>
          <div style={{ width: 44, height: 44, borderRadius: 14, background: `linear-gradient(135deg, rgba(244,114,182,0.25), rgba(124,58,237,0.15))`, border: "1px solid rgba(244,114,182,0.2)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(244,114,182,0.15)" }}>
            <Code style={{ width: 20, height: 20, color: T.pink }} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
              <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Vibe Coding</h1>
              <span style={{ padding: "2px 8px", borderRadius: 20, background: "rgba(244,114,182,0.1)", border: "1px solid rgba(244,114,182,0.2)", color: T.pink, fontSize: 9, fontWeight: 700, letterSpacing: "0.1em" }}>AI-POWERED</span>
            </div>
            <p style={{ fontSize: 12, color: "#475569", margin: 0 }}>Describe any app in plain English — get production-ready code instantly</p>
          </div>
          {/* Live waveform */}
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 3 }}>
            {[0,1,2,3,4].map(i => (
              <div key={i} style={{ width: 3, height: 14, borderRadius: 2, background: T.pink, animation: `vc_bar 0.6s ease-in-out ${i * 0.1}s infinite`, opacity: 0.6 }} />
            ))}
          </div>
        </div>

        {/* ── Create new project ───────────────────────────────────────────── */}
        <div style={{ borderRadius: 20, padding: 1.5, background: creating ? `linear-gradient(135deg, rgba(244,114,182,0.6), rgba(124,58,237,0.5), rgba(79,209,197,0.4))` : `linear-gradient(135deg, rgba(244,114,182,0.25), rgba(124,58,237,0.15))`, marginBottom: 24, animation: creating ? "vc_glow 2s ease-in-out infinite" : "none" }}>
          <div style={{ borderRadius: 18, background: T.glass2, backdropFilter: "blur(20px)", padding: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <Sparkles style={{ width: 15, height: 15, color: T.pink }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>What do you want to build?</span>
            </div>
            <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
              <input
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => e.key === "Enter" && createProject()}
                disabled={creating}
                placeholder="e.g. A kanban board with drag-and-drop, team assignment, and priority labels..."
                data-testid="vibe-prompt"
                style={{ flex: 1, height: 48, paddingLeft: 16, paddingRight: 16, borderRadius: 12, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 14, outline: "none", transition: "border-color 0.15s", fontFamily: "inherit" }}
                onFocus={e => e.target.style.borderColor = "rgba(244,114,182,0.4)"}
                onBlur={e => e.target.style.borderColor = T.border}
              />
              <button
                onClick={createProject}
                disabled={creating || !prompt.trim()}
                data-testid="vibe-create-btn"
                style={{ display: "flex", alignItems: "center", gap: 8, padding: "0 20px", borderRadius: 12, background: creating ? "rgba(244,114,182,0.15)" : `linear-gradient(135deg, ${T.pink}, rgba(124,58,237,0.8))`, border: creating ? "1px solid rgba(244,114,182,0.2)" : "none", color: creating ? T.pink : "#fff", fontSize: 13, fontWeight: 700, cursor: creating || !prompt.trim() ? "default" : "pointer", opacity: !prompt.trim() && !creating ? 0.5 : 1, transition: "all 0.2s", whiteSpace: "nowrap", minWidth: 110 }}>
                {creating
                  ? <><Loader2 style={{ width: 14, height: 14, animation: "vc_spin 1s linear infinite" }} /> Building...</>
                  : <><Zap style={{ width: 14, height: 14 }} /> Build App</>}
              </button>
            </div>

            {/* Generation progress */}
            {creating && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ height: 3, borderRadius: 2, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                  <div style={{ height: "100%", borderRadius: 2, background: `linear-gradient(90deg, ${T.pink}, ${T.violet})`, width: `${genProgress}%`, transition: "width 0.8s ease", boxShadow: `0 0 8px ${T.pink}88` }} />
                </div>
                <p style={{ fontSize: 11, color: T.pink, marginTop: 8, animation: "vc_pulse 2s ease-in-out infinite" }}>
                  {genProgress < 30 ? "Analyzing your requirements..." : genProgress < 60 ? "Generating components and logic..." : genProgress < 85 ? "Assembling the final application..." : "Finishing up..."}
                </p>
              </div>
            )}

            {/* Starter prompts */}
            {!creating && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {STARTER_PROMPTS.map((s, i) => (
                  <button key={i} onClick={() => setPrompt(s.prompt)}
                    style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 20, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: "#64748b", fontSize: 11, cursor: "pointer", transition: "all 0.15s", fontFamily: "inherit" }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(244,114,182,0.25)"; e.currentTarget.style.color = "#94a3b8"; e.currentTarget.style.background = "rgba(244,114,182,0.06)"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = "#64748b"; e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}>
                    <span>{s.icon}</span> {s.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Projects list ─────────────────────────────────────────────────── */}
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "48px 0" }}>
            <div style={{ width: 32, height: 32, borderRadius: "50%", border: `2px solid transparent`, borderTopColor: T.pink, borderRightColor: "rgba(244,114,182,0.3)", animation: "vc_spin 0.8s linear infinite" }} />
          </div>
        ) : projects.length > 0 ? (
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Layers style={{ width: 13, height: 13, color: "#475569" }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>Your Apps</span>
              <span style={{ fontSize: 11, color: "#334155", marginLeft: 2 }}>({projects.length})</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 10 }}>
              {projects.map(p => (
                <ProjectCard key={p.vibe_id} project={p} onLoad={loadProject} onDelete={deleteProject} />
              ))}
            </div>
          </div>
        ) : (
          <div style={{ padding: "64px 0", textAlign: "center", border: "1px dashed rgba(244,114,182,0.12)", borderRadius: 20, background: "rgba(244,114,182,0.02)" }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(244,114,182,0.08)", border: "1px solid rgba(244,114,182,0.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
              <Terminal style={{ width: 28, height: 28, color: T.pink, opacity: 0.7 }} />
            </div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: "#e2e8f0", fontFamily: "Outfit, sans-serif", marginBottom: 8 }}>No Apps Yet</h3>
            <p style={{ fontSize: 13, color: "#475569" }}>Describe your app idea above and watch it come to life.</p>
          </div>
        )}
      </div>
    );
  }

  /* ── Active project editor ────────────────────────────────────────────── */
  const files = activeProject.files || [];
  const currentFile = files[activeFile] || files[0];

  return (
    <div data-testid="vibe-editor" style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 140px)", animation: "vc_fadeUp 0.3s ease" }}>
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, flexShrink: 0 }}>
        <button
          onClick={() => setActive(null)}
          style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 10px", borderRadius: 9, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#64748b", fontSize: 12, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.color = "#e2e8f0"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; }}
          onMouseLeave={e => { e.currentTarget.style.color = "#64748b"; e.currentTarget.style.borderColor = T.border; }}>
          <ChevronLeft style={{ width: 14, height: 14 }} /> Back
        </button>

        <div style={{ width: 1, height: 20, background: T.border }} />

        <Code style={{ width: 15, height: 15, color: T.pink, flexShrink: 0 }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <h2 style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", margin: 0 }}>
            {activeProject.title}
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2 }}>
            {activeProject.tech_stack?.slice(0, 4).map((t, i) => (
              <span key={i} style={{ padding: "1px 6px", borderRadius: 5, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#475569", fontSize: 9, fontWeight: 600 }}>{t}</span>
            ))}
            <span style={{ fontSize: 10, color: "#334155" }}>{files.length} file{files.length !== 1 ? "s" : ""}</span>
          </div>
        </div>

        <div style={{ display: "flex", gap: 6 }}>
          <IconBtn icon={<Copy style={{ width: 13, height: 13 }} />} onClick={copyCode} title="Copy code" testId="copy-code-btn" />
          <IconBtn icon={<Download style={{ width: 13, height: 13 }} />} onClick={downloadProject} title="Download files" testId="download-btn" />
          <IconBtn icon={<Trash2 style={{ width: 13, height: 13 }} />} onClick={() => deleteProject(activeProject.vibe_id)} title="Delete project" danger />
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 3, background: "rgba(8,15,28,0.6)", border: `1px solid ${T.border}`, borderRadius: 12, padding: 4, marginBottom: 14, flexShrink: 0, backdropFilter: "blur(12px)" }}>
        {[
          { id: "preview", icon: <Eye style={{ width: 13, height: 13 }} />, label: "Preview" },
          { id: "code",    icon: <FileCode style={{ width: 13, height: 13 }} />, label: "Code" },
          { id: "chat",    icon: <MessageSquare style={{ width: 13, height: 13 }} />, label: "Chat & Edit" },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            data-testid={`tab-${tab.id}`}
            style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "7px 0", borderRadius: 9, border: "none", cursor: "pointer", transition: "all 0.15s", fontSize: 12, fontWeight: 600,
              background: activeTab === tab.id ? "rgba(244,114,182,0.12)" : "transparent",
              color: activeTab === tab.id ? T.pink : "#475569",
              boxShadow: activeTab === tab.id ? `inset 0 0 0 1px rgba(244,114,182,0.2)` : "none",
            }}>
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Preview Tab */}
      {activeTab === "preview" && (
        <div style={{ flex: 1, borderRadius: 16, overflow: "hidden", border: `1px solid ${T.border}`, background: "#fff" }}>
          <iframe
            ref={iframeRef}
            title="App Preview"
            style={{ width: "100%", height: "100%", border: 0 }}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            data-testid="preview-iframe"
          />
        </div>
      )}

      {/* Code Tab */}
      {activeTab === "code" && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          {files.length > 1 && (
            <div style={{ display: "flex", gap: 4, marginBottom: 10, overflowX: "auto", paddingBottom: 2, flexShrink: 0 }}>
              {files.map((f, i) => (
                <button key={i} onClick={() => setActiveFile(i)}
                  style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 8, border: "none", cursor: "pointer", whiteSpace: "nowrap", transition: "all 0.15s", fontSize: 11, fontWeight: 600,
                    background: i === activeFile ? "rgba(244,114,182,0.12)" : "rgba(255,255,255,0.03)",
                    color: i === activeFile ? T.pink : "#475569",
                    outline: i === activeFile ? `1px solid rgba(244,114,182,0.2)` : "none",
                  }}>
                  <FileCode style={{ width: 11, height: 11 }} />
                  {f.name}
                  <FileLanguageIcon name={f.name} />
                </button>
              ))}
            </div>
          )}
          <div style={{ flex: 1, borderRadius: 14, overflow: "hidden", border: `1px solid ${T.border}`, background: "rgba(3,7,18,0.9)", display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 14px", background: "rgba(8,15,28,0.8)", borderBottom: `1px solid ${T.border}`, flexShrink: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ display: "flex", gap: 5 }}>
                  {["#f87171","#fbbf24","#34d399"].map((c,i) => <div key={i} style={{ width: 9, height: 9, borderRadius: "50%", background: c, opacity: 0.7 }} />)}
                </div>
                <span style={{ fontSize: 11, color: "#475569", fontFamily: "monospace" }}>{currentFile?.name}</span>
                <FileLanguageIcon name={currentFile?.name || ""} />
              </div>
              <span style={{ fontSize: 10, color: "#334155" }}>{(currentFile?.content || "").split("\n").length} lines</span>
            </div>
            <pre style={{ flex: 1, padding: 16, overflow: "auto", fontSize: 12, color: "#94a3b8", fontFamily: "'Fira Code', 'JetBrains Mono', monospace", lineHeight: 1.7, margin: 0 }}>
              <code>{currentFile?.content}</code>
            </pre>
          </div>
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          <div style={{ flex: 1, borderRadius: 14, border: `1px solid ${T.border}`, background: T.glass, backdropFilter: "blur(12px)", padding: 14, overflowY: "auto", marginBottom: 10 }}>
            {(activeProject.chat_history || []).length === 0 ? (
              <div style={{ textAlign: "center", padding: "32px 0", color: "#475569" }}>
                <MessageSquare style={{ width: 24, height: 24, margin: "0 auto 10px", opacity: 0.3 }} />
                <p style={{ fontSize: 12 }}>Describe what changes you'd like to make</p>
                <p style={{ fontSize: 11, marginTop: 4, color: "#334155" }}>e.g. "Add a dark mode toggle" or "Make the header sticky"</p>
              </div>
            ) : (
              (activeProject.chat_history || []).map((msg, i) => (
                <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
                  <div style={{ maxWidth: "80%", borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                    padding: "8px 14px",
                    background: msg.role === "user" ? "rgba(244,114,182,0.12)" : "rgba(255,255,255,0.04)",
                    border: `1px solid ${msg.role === "user" ? "rgba(244,114,182,0.2)" : T.border}`,
                    color: msg.role === "user" ? "#f9a8d4" : "#94a3b8",
                  }}>
                    <p style={{ fontSize: 12, lineHeight: 1.55, margin: 0 }}>{msg.content}</p>
                    {msg.timestamp && <p style={{ fontSize: 9, color: "#334155", marginTop: 4, margin: 0 }}>{new Date(msg.timestamp).toLocaleTimeString()}</p>}
                  </div>
                </div>
              ))
            )}
            <div ref={chatEndRef} />
          </div>
          <div style={{ display: "flex", gap: 10, flexShrink: 0 }}>
            <input
              value={chatMsg}
              onChange={e => setChatMsg(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendChat()}
              disabled={chatting}
              placeholder="Describe changes... e.g. 'Add a dark mode toggle'"
              data-testid="vibe-chat-input"
              style={{ flex: 1, height: 44, paddingLeft: 14, paddingRight: 14, borderRadius: 11, background: T.glass, border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 13, outline: "none", transition: "border-color 0.15s", fontFamily: "inherit", backdropFilter: "blur(8px)" }}
              onFocus={e => e.target.style.borderColor = "rgba(244,114,182,0.35)"}
              onBlur={e => e.target.style.borderColor = T.border}
            />
            <button
              onClick={sendChat}
              disabled={chatting || !chatMsg.trim()}
              data-testid="vibe-chat-send"
              style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, borderRadius: 11, background: chatting || !chatMsg.trim() ? "rgba(244,114,182,0.08)" : `linear-gradient(135deg, ${T.pink}, rgba(124,58,237,0.8))`, border: "none", cursor: chatting || !chatMsg.trim() ? "default" : "pointer", opacity: !chatMsg.trim() ? 0.5 : 1, transition: "all 0.2s" }}>
              {chatting ? <Loader2 style={{ width: 16, height: 16, color: T.pink, animation: "vc_spin 1s linear infinite" }} /> : <Send style={{ width: 16, height: 16, color: "#fff" }} />}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── Sub-components ─────────────────────────────────────────────────────── */
function ProjectCard({ project: p, onLoad, onDelete }) {
  const [hovered, setHovered] = useState(false);
  const isReady = p.status === "ready" || p.status === "complete";
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ cursor: "pointer", borderRadius: 14, background: hovered ? "rgba(244,114,182,0.06)" : T.glass, border: `1px solid ${hovered ? "rgba(244,114,182,0.25)" : T.border}`, transition: "all 0.2s", transform: hovered ? "translateY(-2px)" : "none", boxShadow: hovered ? "0 8px 28px rgba(244,114,182,0.1)" : "none", backdropFilter: "blur(12px)", padding: 14 }}
      onClick={() => onLoad(p.vibe_id)}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(244,114,182,0.1)", border: "1px solid rgba(244,114,182,0.15)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <Globe style={{ width: 16, height: 16, color: T.pink }} />
          </div>
          <div>
            <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", fontFamily: "Outfit, sans-serif", margin: "0 0 2px" }}>{p.title}</p>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              {isReady
                ? <><CheckCircle style={{ width: 9, height: 9, color: "#34d399" }} /><span style={{ fontSize: 9, color: "#34d399", fontWeight: 600 }}>READY</span></>
                : <><Clock style={{ width: 9, height: 9, color: T.amber }} /><span style={{ fontSize: 9, color: T.amber, fontWeight: 600 }}>{p.status?.toUpperCase()}</span></>}
            </div>
          </div>
        </div>
        <button
          onClick={e => { e.stopPropagation(); onDelete(p.vibe_id); }}
          style={{ padding: 5, borderRadius: 7, background: "transparent", border: "none", cursor: "pointer", color: "#334155", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.color = "#f87171"; e.currentTarget.style.background = "rgba(248,113,113,0.08)"; }}
          onMouseLeave={e => { e.currentTarget.style.color = "#334155"; e.currentTarget.style.background = "transparent"; }}>
          <Trash2 style={{ width: 12, height: 12 }} />
        </button>
      </div>
      <p style={{ fontSize: 11, color: "#475569", lineHeight: 1.5, margin: "0 0 10px", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{p.description}</p>
      {p.tech_stack?.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
          {p.tech_stack.slice(0, 4).map((t, i) => <FileLanguageIcon key={i} name={`.${t.toLowerCase()}`} />)}
        </div>
      )}
    </div>
  );
}

function IconBtn({ icon, onClick, title, danger, testId }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      title={title}
      data-testid={testId}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 32, height: 32, borderRadius: 8, border: `1px solid ${T.border}`, cursor: "pointer", transition: "all 0.15s",
        background: hovered ? (danger ? "rgba(248,113,113,0.1)" : "rgba(255,255,255,0.06)") : "rgba(255,255,255,0.03)",
        color: hovered ? (danger ? "#f87171" : "#e2e8f0") : "#475569",
      }}>
      {icon}
    </button>
  );
}

export default VibeCoding;
