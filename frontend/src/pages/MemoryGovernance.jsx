import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Brain, Trash2, Plus, Edit3, History, BarChart3, Zap,
  AlertTriangle, RefreshCw, Tag, Filter, ChevronDown,
  ChevronRight, Loader2, Search, Archive
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

const CATEGORY_COLORS = {
  general: "border-zinc-500/30 text-zinc-400",
  fact: "border-blue-500/30 text-blue-400",
  preference: "border-violet-500/30 text-violet-400",
  instruction: "border-amber-500/30 text-amber-400",
  context: "border-emerald-500/30 text-emerald-400",
  decision: "border-rose-500/30 text-rose-400",
};

const CATEGORIES = ["general", "fact", "preference", "instruction", "context", "decision"];

const RelevanceBar = ({ score }) => {
  const pct = Math.round(score * 100);
  const color = pct > 60 ? "bg-emerald-500" : pct > 30 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-zinc-500">{pct}%</span>
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
    if (res.ok) {
      setShowCreate(false);
      fetchEntries();
    }
  };

  const handleUpdate = async (memoryId, formData) => {
    const res = await fetch(`${API}/memory/entries/${memoryId}`, { method: "PUT", headers, body: JSON.stringify(formData) });
    if (res.ok) {
      setEditEntry(null);
      fetchEntries();
    }
  };

  const handleDelete = async (memoryId) => {
    if (!window.confirm("Delete this memory entry?")) return;
    await fetch(`${API}/memory/entries/${memoryId}`, { method: "DELETE", headers });
    fetchEntries();
  };

  const handleViewVersions = async (entry) => {
    setVersionEntry(entry);
    const res = await fetch(`${API}/memory/entries/${entry.memory_id}/versions`, { headers });
    if (res.ok) {
      const data = await res.json();
      setVersions(data.versions || []);
    }
  };

  const handlePrune = async (dryRun = true) => {
    setPruning(true);
    const res = await fetch(`${API}/memory/prune`, { method: "POST", headers, body: JSON.stringify({ threshold: 0.15, dry_run: dryRun }) });
    if (res.ok) {
      const data = await res.json();
      setPruneResult(data);
      if (!dryRun) fetchEntries();
    }
    setPruning(false);
  };

  const filtered = search ? entries.filter(e =>
    e.content?.toLowerCase().includes(search.toLowerCase()) ||
    e.summary?.toLowerCase().includes(search.toLowerCase()) ||
    e.agent_name?.toLowerCase().includes(search.toLowerCase())
  ) : entries;

  if (loading) return <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 text-indigo-400 animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="memory-governance-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
            <Brain className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white font-['Outfit']" data-testid="memory-title">Memory Governance</h1>
            <p className="text-xs text-zinc-500">Versioning, relevance scoring & auto-pruning for agent memory</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => handlePrune(true)} disabled={pruning} className="text-zinc-400 border-white/10" data-testid="prune-preview-btn">
            {pruning ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" /> : <Archive className="w-3.5 h-3.5 mr-1" />}
            Prune Preview
          </Button>
          <Button size="sm" onClick={() => setShowCreate(true)} className="bg-violet-600 hover:bg-violet-700 text-white" data-testid="create-memory-btn">
            <Plus className="w-3.5 h-3.5 mr-1" /> Add Memory
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="memory-stats">
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-3">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Total Entries</p>
              <p className="text-xl font-bold text-white">{stats.total_entries}</p>
              <p className="text-[10px] text-zinc-600">{stats.usage_pct}% of {stats.max_entries} limit</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-3">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Avg Relevance</p>
              <p className="text-xl font-bold text-white">{Math.round(stats.avg_relevance * 100)}%</p>
              <RelevanceBar score={stats.avg_relevance} />
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-3">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Low Relevance</p>
              <p className="text-xl font-bold text-amber-400">{stats.low_relevance_count}</p>
              <p className="text-[10px] text-zinc-600">Candidates for pruning</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-white/5">
            <CardContent className="p-3">
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Categories</p>
              <p className="text-xl font-bold text-white">{Object.keys(stats.categories || {}).length}</p>
              <div className="flex gap-1 mt-0.5 flex-wrap">
                {Object.entries(stats.categories || {}).map(([cat, count]) => (
                  <Badge key={cat} variant="outline" className={`text-[8px] ${CATEGORY_COLORS[cat] || CATEGORY_COLORS.general}`}>{cat}: {count}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Prune Result */}
      {pruneResult && (
        <Card className="bg-amber-500/5 border-amber-500/20" data-testid="prune-result">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-medium text-amber-300">
                  {pruneResult.dry_run ? `${pruneResult.candidates} entries eligible for pruning` : `${pruneResult.pruned} entries pruned`}
                </span>
              </div>
              <div className="flex gap-2">
                {pruneResult.dry_run && pruneResult.candidates > 0 && (
                  <Button size="sm" variant="destructive" onClick={() => handlePrune(false)} className="text-xs" data-testid="confirm-prune-btn">
                    Confirm Prune
                  </Button>
                )}
                <Button size="sm" variant="ghost" onClick={() => setPruneResult(null)} className="text-zinc-400 text-xs">Dismiss</Button>
              </div>
            </div>
            {pruneResult.entries?.slice(0, 5).map(e => (
              <div key={e.memory_id} className="flex items-center gap-3 text-xs py-1 text-zinc-400">
                <span className="text-red-400 font-mono w-16">{Math.round(e.relevance_score * 100)}%</span>
                <span className="truncate">{e.content_preview}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <div className="flex items-center gap-2 bg-zinc-900/50 border border-white/5 rounded-lg px-3 py-2">
        <Search className="w-4 h-4 text-zinc-500" />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Filter memories..."
          className="flex-1 bg-transparent text-sm text-white placeholder-zinc-600 outline-none"
          data-testid="memory-search"
        />
      </div>

      {/* Memory Entries */}
      <div className="space-y-2" data-testid="memory-entries-list">
        {filtered.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-white/10 rounded-xl">
            <Brain className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-sm text-zinc-500">No memory entries yet</p>
            <p className="text-xs text-zinc-600 mt-1">Add memories manually or they'll be created as agents learn</p>
          </div>
        ) : (
          filtered.map(entry => (
            <div key={entry.memory_id} className="bg-zinc-900/50 border border-white/5 rounded-lg p-4 hover:border-white/10 transition-all" data-testid={`memory-entry-${entry.memory_id}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <Badge variant="outline" className={`text-[9px] ${CATEGORY_COLORS[entry.category] || CATEGORY_COLORS.general}`}>
                      {entry.category}
                    </Badge>
                    {entry.agent_name && (
                      <span className="text-[10px] text-indigo-400">{entry.agent_name}</span>
                    )}
                    <span className="text-[10px] text-zinc-600">v{entry.version}</span>
                    <span className="text-[10px] text-zinc-700">{entry.source}</span>
                  </div>
                  <p className="text-sm text-zinc-300 mb-1">{entry.content?.substring(0, 200)}{entry.content?.length > 200 ? "..." : ""}</p>
                  {entry.summary && <p className="text-xs text-zinc-500 italic">{entry.summary}</p>}
                  <div className="flex items-center gap-3 mt-2">
                    <RelevanceBar score={entry.relevance_score || 0} />
                    {entry.tags?.length > 0 && (
                      <div className="flex gap-1">
                        {entry.tags.map(t => (
                          <span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500 border border-white/5">{t}</span>
                        ))}
                      </div>
                    )}
                    <span className="text-[10px] text-zinc-700 ml-auto">{entry.access_count} accesses</span>
                  </div>
                </div>
                <div className="flex gap-1 shrink-0">
                  <button onClick={() => handleViewVersions(entry)} className="p-1.5 rounded-md hover:bg-white/5 text-zinc-600 hover:text-zinc-300" title="Version history" data-testid={`version-btn-${entry.memory_id}`}>
                    <History className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => setEditEntry(entry)} className="p-1.5 rounded-md hover:bg-white/5 text-zinc-600 hover:text-zinc-300" title="Edit" data-testid={`edit-btn-${entry.memory_id}`}>
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleDelete(entry.memory_id)} className="p-1.5 rounded-md hover:bg-white/5 text-zinc-600 hover:text-red-400" title="Delete" data-testid={`delete-btn-${entry.memory_id}`}>
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={`w-8 h-8 rounded-lg text-xs ${page === i + 1 ? "bg-violet-600 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreate || editEntry) && (
        <MemoryModal
          entry={editEntry}
          onSave={(data) => editEntry ? handleUpdate(editEntry.memory_id, data) : handleCreate(data)}
          onClose={() => { setShowCreate(false); setEditEntry(null); }}
        />
      )}

      {/* Version History Modal */}
      {versionEntry && (
        <VersionModal
          entry={versionEntry}
          versions={versions}
          onClose={() => { setVersionEntry(null); setVersions([]); }}
        />
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" data-testid="memory-modal">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-zinc-900 border border-white/10 rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[80vh] overflow-y-auto">
        <h3 className="text-lg font-semibold text-white mb-4">{entry ? "Edit Memory" : "Add Memory"}</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Content *</label>
            <textarea value={content} onChange={e => setContent(e.target.value)} rows={4} className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-violet-500/50" placeholder="Memory content..." data-testid="memory-content-input" />
          </div>
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Summary</label>
            <input value={summary} onChange={e => setSummary(e.target.value)} className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-violet-500/50" placeholder="Brief summary..." data-testid="memory-summary-input" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-zinc-400 mb-1 block">Category</label>
              <select value={category} onChange={e => setCategory(e.target.value)} className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none" data-testid="memory-category-select">
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-zinc-400 mb-1 block">Importance ({Math.round(importance * 100)}%)</label>
              <input type="range" min="0" max="1" step="0.05" value={importance} onChange={e => setImportance(parseFloat(e.target.value))} className="w-full" data-testid="memory-importance-slider" />
            </div>
          </div>
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Tags (comma-separated)</label>
            <input value={tags} onChange={e => setTags(e.target.value)} className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-violet-500/50" placeholder="tag1, tag2..." data-testid="memory-tags-input" />
          </div>
          {entry && (
            <div>
              <label className="text-xs text-zinc-400 mb-1 block">Update Reason</label>
              <input value={reason} onChange={e => setReason(e.target.value)} className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-violet-500/50" placeholder="Why this change?" data-testid="memory-reason-input" />
            </div>
          )}
        </div>
        <div className="flex justify-end gap-2 mt-5">
          <Button variant="ghost" onClick={onClose} className="text-zinc-400">Cancel</Button>
          <Button onClick={() => onSave({ content, summary, category, importance, tags: tags.split(",").map(t => t.trim()).filter(Boolean), reason })} disabled={!content.trim()} className="bg-violet-600 hover:bg-violet-700 text-white" data-testid="memory-save-btn">
            {entry ? "Save Changes" : "Create Memory"}
          </Button>
        </div>
      </div>
    </div>
  );
}

function VersionModal({ entry, versions, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" data-testid="version-modal">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-zinc-900 border border-white/10 rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <History className="w-4 h-4 text-violet-400" />
            Version History
          </h3>
          <span className="text-xs text-zinc-500">Current: v{entry.version}</span>
        </div>
        {versions.length === 0 ? (
          <p className="text-sm text-zinc-500 text-center py-8">No version history</p>
        ) : (
          <div className="space-y-3">
            {[...versions].reverse().map((v, i) => (
              <div key={v.version} className={`p-3 rounded-lg border ${v.version === entry.version ? "bg-violet-500/5 border-violet-500/20" : "bg-zinc-800/50 border-white/5"}`}>
                <div className="flex items-center justify-between mb-1.5">
                  <Badge variant="outline" className={v.version === entry.version ? "border-violet-500/30 text-violet-400 text-[9px]" : "border-white/10 text-zinc-500 text-[9px]"}>
                    v{v.version} {v.version === entry.version && "(current)"}
                  </Badge>
                  <span className="text-[10px] text-zinc-600">{new Date(v.updated_at).toLocaleString()}</span>
                </div>
                <p className="text-xs text-zinc-300">{v.content?.substring(0, 150)}{v.content?.length > 150 ? "..." : ""}</p>
                {v.reason && <p className="text-[10px] text-zinc-500 mt-1 italic">{v.reason}</p>}
              </div>
            ))}
          </div>
        )}
        <div className="flex justify-end mt-4">
          <Button variant="ghost" onClick={onClose} className="text-zinc-400">Close</Button>
        </div>
      </div>
    </div>
  );
}
