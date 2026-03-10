import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { GitBranch, Plus, ChevronRight, Clock, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_STYLES = {
  draft: { color: "zinc", label: "Draft" },
  active: { color: "emerald", label: "Active" },
  completed: { color: "blue", label: "Completed" },
  failed: { color: "red", label: "Failed" },
  paused: { color: "amber", label: "Paused" },
};

export default function TaskGraphs() {
  const { token } = useAuth();
  const [graphs, setGraphs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ title: "", objective: "", scope: "", timeline: "" });

  const fetchGraphs = async () => {
    try {
      const res = await fetch(`${API}/api/kernel/task-graphs`, { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      setGraphs(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchGraphs(); }, [token]);

  const createGraph = async () => {
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      await fetch(`${API}/api/kernel/task-graphs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...form, nodes: [], edges: [] }),
      });
      setForm({ title: "", objective: "", scope: "", timeline: "" });
      fetchGraphs();
    } catch (e) { console.error(e); }
    setCreating(false);
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="task-graphs">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Task Graphs</h1>
        <p className="text-sm text-zinc-400 mt-1">Structured task decomposition with dependencies, approval gates, and verification rules</p>
      </div>

      {/* Create Form */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-5" data-testid="create-graph-form">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-400" /> New Task Graph
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            type="text" placeholder="Title" value={form.title}
            onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
            className="bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500/50"
            data-testid="graph-title-input"
          />
          <input
            type="text" placeholder="Timeline (e.g., 2 weeks)" value={form.timeline}
            onChange={e => setForm(p => ({ ...p, timeline: e.target.value }))}
            className="bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500/50"
            data-testid="graph-timeline-input"
          />
          <input
            type="text" placeholder="Objective" value={form.objective}
            onChange={e => setForm(p => ({ ...p, objective: e.target.value }))}
            className="bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500/50 md:col-span-2"
            data-testid="graph-objective-input"
          />
        </div>
        <button
          onClick={createGraph} disabled={creating || !form.title.trim()}
          className="mt-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
          data-testid="create-graph-btn"
        >
          {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Create Graph
        </button>
      </div>

      {/* Graphs List */}
      {graphs.length === 0 ? (
        <div className="bg-zinc-900/20 border border-dashed border-white/5 rounded-xl p-12 text-center">
          <GitBranch className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-500">No task graphs yet</p>
          <p className="text-xs text-zinc-600 mt-1">Create your first task graph to structure and track complex workflows</p>
        </div>
      ) : (
        <div className="space-y-3" data-testid="graphs-list">
          {graphs.map(g => {
            const st = STATUS_STYLES[g.status] || STATUS_STYLES.draft;
            return (
              <div key={g.id || g.title} className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-colors" data-testid={`graph-item-${g.id}`}>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-zinc-800 flex items-center justify-center">
                    <GitBranch className="w-4 h-4 text-zinc-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-medium text-white truncate">{g.title}</h4>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded-full bg-${st.color}-500/10 text-${st.color}-400`}>{st.label}</span>
                    </div>
                    {g.objective && <p className="text-[11px] text-zinc-500 mt-0.5 truncate">{g.objective}</p>}
                    <div className="flex items-center gap-4 mt-2 text-[10px] text-zinc-600">
                      {g.timeline && <span><Clock className="w-3 h-3 inline mr-1" />{g.timeline}</span>}
                      <span>{g.nodes?.length || 0} nodes</span>
                      <span>v{g.version}</span>
                      {g.risk_score > 0 && <span className="text-amber-500"><AlertCircle className="w-3 h-3 inline mr-1" />Risk: {g.risk_score}</span>}
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-600" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
