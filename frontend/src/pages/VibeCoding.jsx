import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Code, Play, Download, Send, Trash2, Plus, ChevronLeft,
  Loader2, Eye, FileCode, MessageSquare, Copy
} from "lucide-react";
import { toast } from "sonner";

const VibeCoding = () => {
  const { token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [chatMsg, setChatMsg] = useState("");
  const [activeTab, setActiveTab] = useState("preview");
  const [activeFile, setActiveFile] = useState(0);
  const iframeRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchProjects = useCallback(async () => {
    try {
      const res = await fetch(`${API}/vibe/projects`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setProjects((await res.json()).items || []);
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

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
        setActiveProject(project);
        setPrompt("");
        fetchProjects();
        toast.success("App generated!");
      } else toast.error("Failed to generate app");
    } catch { toast.error("Error creating project"); }
    finally { setCreating(false); }
  };

  const loadProject = async (vibeId) => {
    try {
      const res = await fetch(`${API}/vibe/projects/${vibeId}`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setActiveProject(await res.json());
    } catch { toast.error("Failed to load project"); }
  };

  const sendChat = async () => {
    if (!chatMsg.trim() || !activeProject) return;
    setChatting(true);
    try {
      const res = await fetch(`${API}/vibe/projects/${activeProject.vibe_id}/chat`, {
        method: "POST", headers,
        body: JSON.stringify({ message: chatMsg }),
      });
      if (res.ok) {
        setActiveProject(await res.json());
        setChatMsg("");
        toast.success("Changes applied!");
      } else toast.error("Failed to apply changes");
    } catch { toast.error("Chat error"); }
    finally { setChatting(false); }
  };

  const deleteProject = async (vibeId) => {
    if (!window.confirm("Delete this project?")) return;
    try {
      await fetch(`${API}/vibe/projects/${vibeId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      setActiveProject(null);
      fetchProjects();
      toast.success("Project deleted");
    } catch {}
  };

  const downloadProject = () => {
    if (!activeProject?.files) return;
    activeProject.files.forEach(f => {
      const blob = new Blob([f.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = f.name;
      a.click(); URL.revokeObjectURL(url);
    });
    toast.success("Files downloaded!");
  };

  const copyCode = () => {
    const file = activeProject?.files?.[activeFile];
    if (file) {
      navigator.clipboard.writeText(file.content);
      toast.success("Code copied!");
    }
  };

  // Render preview in iframe
  useEffect(() => {
    if (activeTab === "preview" && activeProject?.files && iframeRef.current) {
      const htmlFile = activeProject.files.find(f => f.name.endsWith(".html"));
      if (htmlFile) {
        const blob = new Blob([htmlFile.content], { type: "text/html" });
        iframeRef.current.src = URL.createObjectURL(blob);
      }
    }
  }, [activeTab, activeProject, activeFile]);

  // Project list view
  if (!activeProject) {
    return (
      <div className="space-y-6" data-testid="vibe-coding">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-pink-500/15 flex items-center justify-center">
            <Code className="w-5 h-5 text-pink-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white font-['Outfit']">Vibe Coding</h1>
            <p className="text-xs text-zinc-500">Build full-stack apps from chat. Describe it, and we build it.</p>
          </div>
        </div>

        {/* Create new project */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <p className="text-sm text-white mb-3">What do you want to build?</p>
            <div className="flex gap-2">
              <Input
                value={prompt} onChange={e => setPrompt(e.target.value)}
                placeholder="e.g. A task management app with drag-and-drop kanban board..."
                className="bg-zinc-800/50 border-white/10 text-white text-sm flex-1"
                onKeyDown={e => e.key === "Enter" && createProject()}
                disabled={creating}
                data-testid="vibe-prompt"
              />
              <Button onClick={createProject} disabled={creating || !prompt.trim()} className="bg-pink-600 hover:bg-pink-500 text-white shrink-0" data-testid="vibe-create-btn">
                {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Plus className="w-4 h-4 mr-1" />Build</>}
              </Button>
            </div>
            {creating && <p className="text-xs text-pink-400 mt-2 animate-pulse">Generating your app... This may take 15-30 seconds.</p>}
          </CardContent>
        </Card>

        {/* Projects list */}
        {loading ? (
          <div className="flex items-center justify-center py-12"><div className="w-6 h-6 border-2 border-pink-400 border-t-transparent rounded-full animate-spin" /></div>
        ) : projects.length > 0 ? (
          <div className="space-y-2">
            <h2 className="text-sm text-zinc-400 uppercase tracking-wider">Your Apps</h2>
            {projects.map(p => (
              <div key={p.vibe_id} className="bg-zinc-900/50 border border-white/5 rounded-lg p-4 hover:border-white/10 transition-all cursor-pointer flex items-center gap-3" onClick={() => loadProject(p.vibe_id)}>
                <FileCode className="w-5 h-5 text-pink-400 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{p.title}</p>
                  <p className="text-[10px] text-zinc-500 truncate">{p.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  {p.tech_stack?.slice(0, 3).map((t, i) => (
                    <Badge key={i} variant="outline" className="border-white/10 text-zinc-500 text-[8px]">{t}</Badge>
                  ))}
                  <Badge variant="outline" className={`text-[9px] ${p.status === "ready" ? "border-emerald-500/30 text-emerald-400" : "border-amber-500/30 text-amber-400"}`}>{p.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 border border-dashed border-white/10 rounded-xl">
            <Code className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-sm text-zinc-400">No apps yet. Describe what you want to build above.</p>
          </div>
        )}
      </div>
    );
  }

  // Active project editor view
  const files = activeProject.files || [];
  const currentFile = files[activeFile] || files[0];

  return (
    <div className="space-y-4" data-testid="vibe-editor">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => setActiveProject(null)} className="text-zinc-400 hover:text-white">
          <ChevronLeft className="w-4 h-4" />
        </Button>
        <Code className="w-5 h-5 text-pink-400" />
        <div className="flex-1 min-w-0">
          <h2 className="text-white font-semibold text-sm truncate">{activeProject.title}</h2>
          <p className="text-[10px] text-zinc-500">{files.length} file(s) {activeProject.tech_stack?.join(", ")}</p>
        </div>
        <div className="flex gap-1.5">
          <Button size="sm" variant="ghost" onClick={copyCode} className="text-zinc-400 hover:text-white" data-testid="copy-code-btn">
            <Copy className="w-3.5 h-3.5" />
          </Button>
          <Button size="sm" variant="ghost" onClick={downloadProject} className="text-zinc-400 hover:text-white" data-testid="download-btn">
            <Download className="w-3.5 h-3.5" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => deleteProject(activeProject.vibe_id)} className="text-zinc-400 hover:text-red-400">
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Tabs: Preview / Code / Chat */}
      <div className="flex gap-1 bg-zinc-900/50 p-1 rounded-lg border border-white/5">
        {[
          { id: "preview", icon: Eye, label: "Preview" },
          { id: "code", icon: FileCode, label: "Code" },
          { id: "chat", icon: MessageSquare, label: "Chat" },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-colors flex-1 justify-center ${
              activeTab === tab.id ? "bg-pink-500/15 text-pink-400" : "text-zinc-500 hover:text-zinc-300"
            }`}
            data-testid={`tab-${tab.id}`}
          >
            <tab.icon className="w-3.5 h-3.5" />{tab.label}
          </button>
        ))}
      </div>

      {/* Preview Tab */}
      {activeTab === "preview" && (
        <div className="rounded-xl overflow-hidden border border-white/10 bg-white" style={{ height: "60vh" }}>
          <iframe ref={iframeRef} title="App Preview" className="w-full h-full border-0" sandbox="allow-scripts allow-same-origin allow-forms allow-popups" data-testid="preview-iframe" />
        </div>
      )}

      {/* Code Tab */}
      {activeTab === "code" && (
        <div>
          {files.length > 1 && (
            <div className="flex gap-1 mb-2 overflow-x-auto">
              {files.map((f, i) => (
                <button key={i} onClick={() => setActiveFile(i)} className={`px-3 py-1 rounded-md text-xs shrink-0 ${i === activeFile ? "bg-pink-500/15 text-pink-400" : "bg-zinc-800/50 text-zinc-500"}`}>
                  {f.name}
                </button>
              ))}
            </div>
          )}
          <div className="rounded-xl overflow-hidden border border-white/10 bg-zinc-950" style={{ height: "60vh" }}>
            <div className="flex items-center justify-between px-3 py-1.5 bg-zinc-900/80 border-b border-white/5">
              <span className="text-[10px] text-zinc-500">{currentFile?.name}</span>
              <span className="text-[10px] text-zinc-600">{currentFile?.language}</span>
            </div>
            <pre className="p-4 overflow-auto text-xs text-zinc-300 font-mono leading-relaxed" style={{ height: "calc(60vh - 28px)" }}>
              <code>{currentFile?.content}</code>
            </pre>
          </div>
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <div>
          <div className="rounded-xl border border-white/10 bg-zinc-900/30 p-4 mb-3 overflow-y-auto" style={{ height: "50vh" }}>
            {(activeProject.chat_history || []).map((msg, i) => (
              <div key={i} className={`mb-3 ${msg.role === "user" ? "text-right" : ""}`}>
                <div className={`inline-block max-w-[80%] rounded-xl px-3 py-2 ${
                  msg.role === "user" ? "bg-pink-500/15 text-pink-300" : "bg-zinc-800/50 text-zinc-300"
                }`}>
                  <p className="text-xs">{msg.content}</p>
                  <p className="text-[9px] text-zinc-600 mt-1">{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ""}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={chatMsg} onChange={e => setChatMsg(e.target.value)}
              placeholder="Describe changes... e.g. 'Add a dark mode toggle'"
              className="bg-zinc-800/50 border-white/10 text-white text-sm flex-1"
              onKeyDown={e => e.key === "Enter" && sendChat()}
              disabled={chatting}
              data-testid="vibe-chat-input"
            />
            <Button onClick={sendChat} disabled={chatting || !chatMsg.trim()} className="bg-pink-600 hover:bg-pink-500 text-white" data-testid="vibe-chat-send">
              {chatting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VibeCoding;
