import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Brain, Trash2, Plus, Edit3, History, Zap,
  AlertTriangle, Tag, Search, Archive, X
} from "lucide-react";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#7c3aed",
  indigo: "#818cf8",
  cyan: "#22d3ee",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const CATEGORY_COLORS = {
  general: T.zinc, fact: "#60a5fa", preference: "#a78bfa",
  instruction: T.amber, context: T.green, decision: "#f87171",
};

const CATEGORIES = ["general", "fact", "preference", "instruction", "context", "decision"];

const RelevanceBar = ({ score }) => {
  const pct = Math.round((score || 0) * 100);
  const color = pct > 60 ? T.green : pct > 30 ? T.amber : T.red;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width: 70, height: 4, background: "rgba(255,255,255,.06)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ height: "100%", borderRadius: 3, background: color, width: `${pct}%` }} />
      </div>
      <span style={{ fontSize: 10, color: T.zinc }}>{pct}%</span>
    </div>
  );
};

export default function MemoryGovernance() {
  const { token } = useAuth();
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [editEntry, setEditEntry] = useState(null);
  const [versionEntry, setVersionEntry] = useState(null);
  const [versions, setVersions] = useState([]);
  const [pruneResult, setPruneResult] = useState(null);
  const [pruning, setPruning] = useState(false);
  const [search, setSearch] = useState("");

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchEntries = useCallback(async () => {
    try {
      const res = await fetch(`${API}/memory/entries?page=${page}&limit=20`, { headers });
      if (res.ok) {
        const data = await res.json();
        setEntries(data.entries || []);
        setTotalPages(data.pages || 1);
        setStats(data.stats);
      }
    } catch {} finally { setLoading(false); }
  }, [token, page]);

  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  const handleCreate = async (formData) => {
    const res = await fetch(`${API}/memory/entries`, { method: "POST", headers, body: JSON.stringify(formData) });
    if (res.ok) { setShowCreate(false); fetchEntries(); }
  };

  const handleUpdate = async (memoryId, formData) => {
    const res = await fetch(`${API}/memory/entries/${memoryId}`, { method: "PUT", headers, body: JSON.stringify(formData) });
    if (res.ok) { setEditEntry(null); fetchEntries(); }
  };

  const handleDelete = async (memoryId) => {
    if (!window.confirm("Delete this memory entry?")) return;
    await fetch(`${API}/memory/entries/${memoryId}`, { method: "DELETE", headers });
    fetchEntries();
  };

  const handleViewVersions = async (entry) => {
    setVersionEntry(entry);
    const res = await fetch(`${API}/memory/entries/${entry.memory_id}/versions`, { headers });
    if (res.ok) { const data = await res.json(); setVersions(data.versions || []); }
  };

  const handlePrune = async (dryRun = true) => {
    setPruning(true);
    const res = await fetch(`${API}/memory/prune`, { method: "POST", headers, body: JSON.stringify({ threshold: 0.15, dry_run: dryRun }) });
    if (res.ok) { const data = await res.json(); setPruneResult(data); if (!dryRun) fetchEntries(); }
    setPruning(false);
  };

  const filtered = search ? entries.filter(e =>
    e.content?.toLowerCase().includes(search.toLowerCase()) ||
    e.summary?.toLowerCase().includes(search.toLowerCase()) ||
    e.agent_name?.toLowerCase().includes(search.toLowerCase())
  ) : entries;

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 26, height: 26, border: `2px solid ${T.violet}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const glassCard = { background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="memory-governance-page">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(124,58,237,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Brain size={22} style={{ color: T.violet }} />
          </div>
          <div>
            <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }} data-testid="memory-title">Memory Governance</h1>
            <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Versioning, relevance scoring & auto-pruning for agent memory</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => handlePrune(true)} disabled={pruning} data-testid="prune-preview-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "7px 14px", borderRadius: 9, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, fontSize: 12, fontWeight: 600, cursor: pruning ? "not-allowed" : "pointer" }}>
            {pruning
              ? <div style={{ width: 12, height: 12, border: `2px solid ${T.zinc}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
              : <Archive size={13} />}
            Prune Preview
          </button>
          <button onClick={() => setShowCreate(true)} data-testid="create-memory-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "7px 14px", borderRadius: 9, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
            <Plus size={13} /> Add Memory
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 10 }} data-testid="memory-stats">
          {[
            { label: "Total Entries", value: stats.total_entries, sub: `${stats.usage_pct}% of ${stats.max_entries} limit`, accent: T.violet },
            { label: "Auto-Learned", value: stats.auto_learned || 0, sub: `${stats.manual || 0} manual`, accent: T.cyan },
            { label: "Avg Relevance", value: `${Math.round(stats.avg_relevance * 100)}%`, sub: <RelevanceBar score={stats.avg_relevance} />, accent: T.green },
            { label: "Low Relevance", value: stats.low_relevance_count, sub: "Candidates for pruning", accent: T.amber },
            { label: "Categories", value: Object.keys(stats.categories || {}).length, sub: (
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 3 }}>
                {Object.entries(stats.categories || {}).map(([cat, count]) => (
                  <span key={cat} style={{ fontSize: 8, padding: "1px 5px", borderRadius: 4, border: `1px solid ${CATEGORY_COLORS[cat] || T.zinc}40`, color: CATEGORY_COLORS[cat] || T.zinc }}>{cat}: {count}</span>
                ))}
              </div>
            ), accent: T.indigo },
          ].map(s => (
            <div key={s.label} style={{ position: "relative", ...glassCard, overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.accent }} />
              <div style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 6 }}>{s.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginBottom: 3 }}>{s.value}</div>
              <div style={{ fontSize: 10, color: T.zinc }}>{s.sub}</div>
            </div>
          ))}
        </div>
      )}

      {/* Prune result */}
      {pruneResult && (
        <div style={{ background: "rgba(245,158,11,.05)", border: `1px solid rgba(245,158,11,.2)`, borderRadius: 12, padding: "14px 16px" }} data-testid="prune-result">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <AlertTriangle size={14} style={{ color: T.amber }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fcd34d" }}>
                {pruneResult.dry_run ? `${pruneResult.candidates} entries eligible for pruning` : `${pruneResult.pruned} entries pruned`}
              </span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {pruneResult.dry_run && pruneResult.candidates > 0 && (
                <button onClick={() => handlePrune(false)} data-testid="confirm-prune-btn"
                  style={{ padding: "4px 12px", borderRadius: 7, background: T.red, border: "none", color: "#fff", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                  Confirm Prune
                </button>
              )}
              <button onClick={() => setPruneResult(null)}
                style={{ padding: "4px 10px", borderRadius: 7, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, fontSize: 11, cursor: "pointer" }}>
                Dismiss
              </button>
            </div>
          </div>
          {pruneResult.entries?.slice(0, 5).map(e => (
            <div key={e.memory_id} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 11, color: "#a1a1aa", paddingTop: 4 }}>
              <span style={{ color: T.red, fontFamily: "monospace", width: 36 }}>{Math.round(e.relevance_score * 100)}%</span>
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{e.content_preview}</span>
            </div>
          ))}
        </div>
      )}

      {/* Search */}
      <div style={{ position: "relative" }}>
        <Search size={13} style={{ position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Filter memories..."
          data-testid="memory-search"
          style={{ paddingLeft: 32, paddingRight: 12, paddingTop: 9, paddingBottom: 9, background: T.glass, border: `1px solid ${T.border}`, borderRadius: 10, color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }} />
      </div>

      {/* Entries */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }} data-testid="memory-entries-list">
        {filtered.length === 0 ? (
          <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
            <Brain size={44} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
            <p style={{ fontSize: 13, color: T.zinc, marginBottom: 4 }}>No memory entries yet</p>
            <p style={{ fontSize: 11, color: "rgba(113,113,122,.5)" }}>Add memories manually or they'll be created as agents learn</p>
          </div>
        ) : filtered.map(entry => (
          <div key={entry.memory_id}
            style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", transition: "border-color .2s" }}
            data-testid={`memory-entry-${entry.memory_id}`}
            onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
            onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap", marginBottom: 6 }}>
                  <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid ${CATEGORY_COLORS[entry.category] || T.zinc}40`, color: CATEGORY_COLORS[entry.category] || T.zinc, fontWeight: 700 }}>
                    {entry.category}
                  </span>
                  {entry.source === "auto_learn" && (
                    <span style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid rgba(34,211,238,.3)`, color: T.cyan, fontWeight: 700 }} data-testid={`auto-learn-badge-${entry.memory_id}`}>
                      <Zap size={8} /> Auto-learned
                    </span>
                  )}
                  {entry.agent_name && <span style={{ fontSize: 10, color: T.indigo }}>{entry.agent_name}</span>}
                  <span style={{ fontSize: 10, color: T.zinc }}>v{entry.version}</span>
                  {entry.source_task_title && <span style={{ fontSize: 10, color: "rgba(113,113,122,.6)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 120 }}>from: {entry.source_task_title}</span>}
                </div>
                <p style={{ fontSize: 13, color: "#d4d4d8", marginBottom: 5, lineHeight: 1.5 }}>{entry.content?.substring(0, 200)}{entry.content?.length > 200 ? "…" : ""}</p>
                {entry.summary && <p style={{ fontSize: 11, color: T.zinc, fontStyle: "italic", marginBottom: 6 }}>{entry.summary}</p>}
                <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                  <RelevanceBar score={entry.relevance_score || 0} />
                  {entry.tags?.length > 0 && (
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      {entry.tags.map(t => (
                        <span key={t} style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, color: T.zinc }}>{t}</span>
                      ))}
                    </div>
                  )}
                  <span style={{ fontSize: 10, color: "rgba(113,113,122,.5)", marginLeft: "auto" }}>{entry.access_count} accesses</span>
                </div>
              </div>
              <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                {[
                  { icon: History, action: () => handleViewVersions(entry), testId: `version-btn-${entry.memory_id}`, title: "Version history" },
                  { icon: Edit3, action: () => setEditEntry(entry), testId: `edit-btn-${entry.memory_id}`, title: "Edit" },
                  { icon: Trash2, action: () => handleDelete(entry.memory_id), testId: `delete-btn-${entry.memory_id}`, title: "Delete", danger: true },
                ].map(({ icon: Icon, action, testId, title, danger }) => (
                  <button key={testId} onClick={action} title={title} data-testid={testId}
                    style={{ padding: 6, borderRadius: 7, background: "transparent", border: "none", color: T.zinc, cursor: "pointer", transition: "color .2s" }}
                    onMouseEnter={e => e.currentTarget.style.color = danger ? T.red : "#e4e4e7"}
                    onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                    <Icon size={14} />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", gap: 6 }}>
          {Array.from({ length: totalPages }, (_, i) => (
            <button key={i} onClick={() => setPage(i + 1)}
              style={{ width: 32, height: 32, borderRadius: 8, border: `1px solid ${page === i + 1 ? T.violet : T.border}`, background: page === i + 1 ? `${T.violet}30` : T.glass, color: page === i + 1 ? "#fff" : T.zinc, fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
              {i + 1}
            </button>
          ))}
        </div>
      )}

      {/* Modals */}
      {(showCreate || editEntry) && (
        <MemoryModal
          entry={editEntry}
          onSave={(data) => editEntry ? handleUpdate(editEntry.memory_id, data) : handleCreate(data)}
          onClose={() => { setShowCreate(false); setEditEntry(null); }}
        />
      )}
      {versionEntry && (
        <VersionModal entry={versionEntry} versions={versions} onClose={() => { setVersionEntry(null); setVersions([]); }} />
      )}
    </div>
  );
}

function MemoryModal({ entry, onSave, onClose }) {
  const [content, setContent] = useState(entry?.content || "");
  const [summary, setSummary] = useState(entry?.summary || "");
  const [category, setCategory] = useState(entry?.category || "general");
  const [importance, setImportance] = useState(entry?.importance || 0.5);
  const [tags, setTags] = useState(entry?.tags?.join(", ") || "");
  const [reason, setReason] = useState("");

  const inputFocus = e => e.target.style.borderColor = "rgba(124,58,237,.5)";
  const inputBlur = e => e.target.style.borderColor = T.border;

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center" }} data-testid="memory-modal">
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,.6)", backdropFilter: "blur(4px)" }} onClick={onClose} />
      <div style={{ position: "relative", background: "#0f0f1a", border: `1px solid ${T.border}`, borderRadius: 18, padding: "24px", width: "100%", maxWidth: 480, margin: "0 16px", maxHeight: "80vh", overflowY: "auto", display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h3 style={{ fontSize: 17, fontWeight: 700, color: "#fff", margin: 0 }}>{entry ? "Edit Memory" : "Add Memory"}</h3>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4 }}><X size={16} /></button>
        </div>
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Content *</label>
          <textarea value={content} onChange={e => setContent(e.target.value)} rows={4} style={{ ...{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", resize: "vertical", lineHeight: 1.5, transition: "border-color .2s" } }} placeholder="Memory content…" data-testid="memory-content-input" onFocus={inputFocus} onBlur={inputBlur} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Summary</label>
          <input value={summary} onChange={e => setSummary(e.target.value)} style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" }} placeholder="Brief summary…" data-testid="memory-summary-input" onFocus={inputFocus} onBlur={inputBlur} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)} style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", cursor: "pointer" }} data-testid="memory-category-select">
              {CATEGORIES.map(c => <option key={c} value={c} style={{ background: "#0f0f1a" }}>{c}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Importance ({Math.round(importance * 100)}%)</label>
            <input type="range" min="0" max="1" step="0.05" value={importance} onChange={e => setImportance(parseFloat(e.target.value))} style={{ width: "100%", accentColor: T.violet, marginTop: 8 }} data-testid="memory-importance-slider" />
          </div>
        </div>
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Tags (comma-separated)</label>
          <input value={tags} onChange={e => setTags(e.target.value)} style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" }} placeholder="tag1, tag2…" data-testid="memory-tags-input" onFocus={inputFocus} onBlur={inputBlur} />
        </div>
        {entry && (
          <div>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Update Reason</label>
            <input value={reason} onChange={e => setReason(e.target.value)} style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "7px 11px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" }} placeholder="Why this change?" data-testid="memory-reason-input" onFocus={inputFocus} onBlur={inputBlur} />
          </div>
        )}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, paddingTop: 4 }}>
          <button onClick={onClose} style={{ padding: "7px 16px", borderRadius: 9, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 12, cursor: "pointer" }}>Cancel</button>
          <button onClick={() => onSave({ content, summary, category, importance, tags: tags.split(",").map(t => t.trim()).filter(Boolean), reason })} disabled={!content.trim()} data-testid="memory-save-btn"
            style={{ padding: "7px 18px", borderRadius: 9, background: !content.trim() ? "rgba(124,58,237,.3)" : `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: !content.trim() ? "not-allowed" : "pointer" }}>
            {entry ? "Save Changes" : "Create Memory"}
          </button>
        </div>
      </div>
    </div>
  );
}

function VersionModal({ entry, versions, onClose }) {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center" }} data-testid="version-modal">
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,.6)", backdropFilter: "blur(4px)" }} onClick={onClose} />
      <div style={{ position: "relative", background: "#0f0f1a", border: `1px solid ${T.border}`, borderRadius: 18, padding: "24px", width: "100%", maxWidth: 480, margin: "0 16px", maxHeight: "80vh", overflowY: "auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <History size={16} style={{ color: T.violet }} />
            <h3 style={{ fontSize: 17, fontWeight: 700, color: "#fff", margin: 0 }}>Version History</h3>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 11, color: T.zinc }}>Current: v{entry.version}</span>
            <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4 }}><X size={16} /></button>
          </div>
        </div>
        {versions.length === 0 ? (
          <p style={{ fontSize: 13, color: T.zinc, textAlign: "center", padding: "32px 0" }}>No version history</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[...versions].reverse().map((v) => {
              const isCurrent = v.version === entry.version;
              return (
                <div key={v.version} style={{ padding: "12px 14px", borderRadius: 10, border: `1px solid ${isCurrent ? "rgba(124,58,237,.25)" : T.border}`, background: isCurrent ? "rgba(124,58,237,.05)" : T.glass }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 5, border: `1px solid ${isCurrent ? "rgba(124,58,237,.3)" : T.border}`, color: isCurrent ? "#a78bfa" : T.zinc, fontWeight: 700 }}>
                      v{v.version} {isCurrent && "(current)"}
                    </span>
                    <span style={{ fontSize: 10, color: T.zinc }}>{new Date(v.updated_at).toLocaleString()}</span>
                  </div>
                  <p style={{ fontSize: 12, color: "#d4d4d8", lineHeight: 1.5 }}>{v.content?.substring(0, 150)}{v.content?.length > 150 ? "…" : ""}</p>
                  {v.reason && <p style={{ fontSize: 10, color: T.zinc, marginTop: 4, fontStyle: "italic" }}>{v.reason}</p>}
                </div>
              );
            })}
          </div>
        )}
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
          <button onClick={onClose} style={{ padding: "7px 16px", borderRadius: 9, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, fontSize: 12, cursor: "pointer" }}>Close</button>
        </div>
      </div>
    </div>
  );
}
