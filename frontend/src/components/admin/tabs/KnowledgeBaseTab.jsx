import { useState, useEffect, useCallback } from "react";
import {
  BookOpen, Upload, Trash2, FileText, Search, CheckCircle, XCircle, Clock, File
} from "lucide-react";
import { useAuth, API } from "../../../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

const KnowledgeBaseTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => { fetchAgents(); }, []);
  useEffect(() => { if (selectedAgent) fetchDocs(); }, [selectedAgent]);

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API}/agents`, { headers });
      if (res.ok) { const data = await res.json(); setAgents(data); if (data.length > 0) setSelectedAgent(data[0].agent_id); }
    } catch { toast.error("Failed to load agents"); }
  };

  const fetchDocs = useCallback(async () => {
    if (!selectedAgent) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge`, { headers });
      if (res.ok) setDocs(await res.json());
    } catch { toast.error("Failed to load documents"); }
    finally { setLoading(false); }
  }, [selectedAgent]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedAgent) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/upload`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`"${data.title}" uploaded. Processing…`);
        setTimeout(() => fetchDocs(), 3000);
        setTimeout(() => fetchDocs(), 8000);
        setTimeout(() => fetchDocs(), 15000);
      } else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Upload failed"); }
    } catch { toast.error("Upload failed"); }
    finally { setUploading(false); e.target.value = ""; }
  };

  const handleDelete = async (docId, title) => {
    if (!confirm(`Delete "${title}" and all its data?`)) return;
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/${docId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Document deleted"); fetchDocs(); }
    } catch { toast.error("Delete failed"); }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !selectedAgent) return;
    setSearching(true);
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/search`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      if (res.ok) { const data = await res.json(); setSearchResults(data.results); }
    } catch { toast.error("Search failed"); }
    finally { setSearching(false); }
  };

  const StatusIcon = ({ status }) => {
    if (status === "ready") return <CheckCircle size={14} style={{ color: T.green }} />;
    if (status === "processing" || status === "queued") return <Clock size={14} style={{ color: T.amber, animation: "pulse 1.5s ease infinite" }} />;
    return <XCircle size={14} style={{ color: T.red }} />;
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  const currentAgent = agents.find(a => a.agent_id === selectedAgent);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22, animation: "fadeUp .4s ease" }} data-testid="knowledge-base-tab">
      <style>{STYLES}</style>

      <div>
        <h2 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 22, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Knowledge Base (RAG)</h2>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Upload documents to give agents access to specific knowledge. They'll cite sources in responses.</p>
      </div>

      {/* Controls */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 13, color: T.zinc }}>Agent:</span>
          <select value={selectedAgent} onChange={e => setSelectedAgent(e.target.value)}
            data-testid="kb-agent-select"
            style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 9, padding: "7px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", cursor: "pointer", minWidth: 220 }}>
            {agents.map(a => <option key={a.agent_id} value={a.agent_id} style={{ background: "#0f0f1a" }}>{a.name} — {a.role}</option>)}
          </select>
        </div>
        <label style={{ cursor: uploading || !selectedAgent ? "not-allowed" : "pointer" }} data-testid="kb-upload-btn">
          <input type="file" style={{ display: "none" }} accept=".pdf,.txt,.md,.csv,.docx" onChange={handleUpload} disabled={uploading || !selectedAgent} />
          <span style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "8px 18px", borderRadius: 10, background: uploading || !selectedAgent ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, color: "#fff", fontSize: 13, fontWeight: 700, pointerEvents: uploading || !selectedAgent ? "none" : "auto" }}>
            {uploading
              ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
              : <Upload size={14} />}
            Upload Document
          </span>
        </label>
      </div>

      {/* Selected agent bar */}
      {currentAgent && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 10, background: "rgba(129,140,248,.08)", border: `1px solid rgba(129,140,248,.2)` }}>
          <img src={currentAgent.avatar} alt="" style={{ width: 32, height: 32, borderRadius: 8, objectFit: "cover" }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{currentAgent.name}</span>
          <span style={{ fontSize: 11, color: T.zinc }}>{docs.filter(d => d.status === "ready").length} documents ready</span>
        </div>
      )}

      {/* Docs list */}
      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "32px 0" }}>
          <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
        </div>
      ) : docs.length === 0 ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "48px 20px", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14 }}>
          <BookOpen size={44} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
          <p style={{ fontSize: 13, color: T.zinc, marginBottom: 4 }}>No documents uploaded for this agent yet.</p>
          <p style={{ fontSize: 11, color: "rgba(113,113,122,.5)" }}>Upload PDFs, text files, or documents to build the knowledge base.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {docs.map(doc => (
            <div key={doc.doc_id} data-testid={`kb-doc-${doc.doc_id}`}
              style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}`, transition: "border-color .2s" }}
              onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.13)"}
              onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
              <div style={{ flexShrink: 0 }}>
                {doc.file_type === ".pdf"
                  ? <FileText size={28} style={{ color: T.red }} />
                  : <File size={28} style={{ color: T.zinc }} />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 3 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{doc.title}</span>
                  <StatusIcon status={doc.status} />
                </div>
                <div style={{ display: "flex", gap: 10, fontSize: 11, color: T.zinc }}>
                  <span>{doc.filename}</span>
                  <span>{formatSize(doc.file_size || 0)}</span>
                  {doc.chunk_count > 0 && <span>{doc.chunk_count} chunks</span>}
                  {doc.status === "error" && <span style={{ color: T.red }}>{doc.error?.slice(0, 80)}</span>}
                </div>
              </div>
              <button onClick={() => handleDelete(doc.doc_id, doc.title)} data-testid={`kb-delete-${doc.doc_id}`}
                style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 6, transition: "color .2s" }}
                onMouseEnter={e => e.currentTarget.style.color = T.red}
                onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Search */}
      {docs.length > 0 && (
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 18px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <Search size={13} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Test Knowledge Search</span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="Ask a question to test retrieval…"
              data-testid="kb-search-input"
              style={{ flex: 1, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", transition: "border-color .2s" }}
              onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
              onBlur={e => e.target.style.borderColor = T.border} />
            <button onClick={handleSearch} disabled={searching || !searchQuery.trim()} data-testid="kb-search-btn"
              style={{ padding: "8px 14px", borderRadius: 8, background: searching || !searchQuery.trim() ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", cursor: searching || !searchQuery.trim() ? "not-allowed" : "pointer", display: "flex", alignItems: "center" }}>
              {searching
                ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
                : <Search size={14} />}
            </button>
          </div>
          {searchResults !== null && (
            <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
              {searchResults.length === 0 ? (
                <p style={{ fontSize: 12, color: T.zinc }}>No relevant results found.</p>
              ) : searchResults.map((r, i) => (
                <div key={i} style={{ padding: "10px 14px", borderRadius: 9, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}` }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 5 }}>
                    <span style={{ fontSize: 11, fontWeight: 600, color: T.indigo }}>
                      {r.doc_title} {r.pages?.length > 0 && `(Page${r.pages.length > 1 ? "s" : ""} ${r.pages.join(", ")})`}
                    </span>
                    <span style={{ fontSize: 10, color: T.zinc }}>Score: {r.score}</span>
                  </div>
                  <p style={{ fontSize: 12, color: "#d4d4d8", overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical" }}>{r.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KnowledgeBaseTab;
