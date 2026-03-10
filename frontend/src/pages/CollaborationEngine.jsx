import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  MessageSquare, ArrowRight, Clock, CheckCircle, AlertTriangle,
  Zap, Users, ChevronDown, ChevronUp, Filter
} from "lucide-react";

const STATUS_COLORS = {
  pending: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  in_progress: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  failed: "bg-red-500/15 text-red-400 border-red-500/30",
};

const RISK_COLORS = {
  low: "text-emerald-400",
  medium: "text-amber-400",
  high: "text-red-400",
  critical: "text-red-500",
};

const CollabCard = ({ collab }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <Card className="bg-zinc-900/50 border-white/5 hover:border-white/10 transition-all">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center shrink-0 mt-0.5">
            <MessageSquare className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-sm font-medium text-white">{collab.sender || "System"}</span>
              <ArrowRight className="w-3 h-3 text-zinc-600" />
              <span className="text-sm text-indigo-400">{(collab.receivers || []).join(", ") || "All"}</span>
              <Badge variant="outline" className={`text-[9px] ${STATUS_COLORS[collab.status] || STATUS_COLORS.pending}`}>
                {collab.status}
              </Badge>
              <Badge variant="outline" className={`text-[9px] border-white/10 ${RISK_COLORS[collab.risk_level] || RISK_COLORS.low}`}>
                {collab.risk_level} risk
              </Badge>
            </div>
            <p className="text-sm text-zinc-300 mb-1">{collab.objective}</p>
            {collab.context && (
              <p className="text-xs text-zinc-500 line-clamp-2">{collab.context}</p>
            )}

            {expanded && (
              <div className="mt-3 space-y-2 border-t border-white/5 pt-3">
                {collab.required_output && (
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Required Output</p>
                    <p className="text-xs text-zinc-300">{collab.required_output}</p>
                  </div>
                )}
                {collab.dependencies?.length > 0 && (
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Dependencies</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {collab.dependencies.map((d, i) => (
                        <Badge key={i} variant="outline" className="border-white/10 text-zinc-400 text-[9px]">{d}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {collab.response && (
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Response</p>
                    <p className="text-xs text-zinc-300 whitespace-pre-wrap">{collab.response}</p>
                  </div>
                )}
                {collab.deadline && (
                  <div className="flex items-center gap-1 text-[10px] text-zinc-500">
                    <Clock className="w-3 h-3" />Deadline: {collab.deadline}
                  </div>
                )}
              </div>
            )}

            <button onClick={() => setExpanded(!expanded)} className="mt-2 flex items-center gap-1 text-[10px] text-zinc-500 hover:text-zinc-300">
              {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {expanded ? "Less" : "More details"}
            </button>
          </div>
          <div className="text-[10px] text-zinc-600 shrink-0">
            {collab.created_at ? new Date(collab.created_at).toLocaleDateString() : ""}
          </div>
        </div>
      </CardContent>
    </Card>
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

  /* Stats */
  const statusCounts = collabs.reduce((acc, c) => { acc[c.status] = (acc[c.status] || 0) + 1; return acc; }, {});
  const uniqueAgents = new Set([...collabs.map(c => c.sender), ...collabs.flatMap(c => c.receivers || [])]);

  const statusFilters = ["all", "pending", "in_progress", "completed", "failed"];

  return (
    <div className="space-y-6" data-testid="collaboration-engine">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
          <Users className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Agent-to-Agent Collaboration</h1>
          <p className="text-xs text-zinc-500">Inter-agent communication, task handoff & cross-domain coordination</p>
        </div>
        <Badge variant="outline" className="ml-auto border-white/10 text-zinc-400">{total} total</Badge>
      </div>

      {/* Collaboration Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="collab-stats">
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
          <div className="flex items-center gap-2 mb-1"><MessageSquare className="w-3.5 h-3.5 text-violet-400" /><span className="text-[10px] text-zinc-500">Total Collabs</span></div>
          <p className="text-lg font-bold text-white">{total}</p>
        </div>
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
          <div className="flex items-center gap-2 mb-1"><Users className="w-3.5 h-3.5 text-indigo-400" /><span className="text-[10px] text-zinc-500">Agents Involved</span></div>
          <p className="text-lg font-bold text-white">{uniqueAgents.size}</p>
        </div>
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
          <div className="flex items-center gap-2 mb-1"><CheckCircle className="w-3.5 h-3.5 text-emerald-400" /><span className="text-[10px] text-zinc-500">Completed</span></div>
          <p className="text-lg font-bold text-white">{statusCounts.completed || 0}</p>
        </div>
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
          <div className="flex items-center gap-2 mb-1"><Clock className="w-3.5 h-3.5 text-amber-400" /><span className="text-[10px] text-zinc-500">Pending</span></div>
          <p className="text-lg font-bold text-white">{statusCounts.pending || 0}</p>
        </div>
      </div>

      {/* Filters + Create Button */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-zinc-500" />
        {statusFilters.map(s => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${filter === s ? "bg-indigo-500/15 text-indigo-400" : "bg-zinc-800/50 text-zinc-500 hover:text-zinc-300"}`}
            data-testid={`filter-${s}`}>
            {s === "all" ? "All" : s.replace("_", " ")}
          </button>
        ))}
        <button onClick={() => setShowCreate(!showCreate)}
          className="ml-auto px-3 py-1.5 rounded-lg text-xs bg-violet-500/15 text-violet-400 hover:bg-violet-500/25 transition-colors"
          data-testid="initiate-collab-btn">
          <Zap className="w-3 h-3 inline mr-1" />Initiate Collaboration
        </button>
      </div>

      {/* Create Collaboration Form */}
      {showCreate && (
        <Card className="bg-zinc-900/50 border-violet-500/20" data-testid="create-collab-form">
          <CardContent className="p-4 space-y-3">
            <p className="text-sm font-bold text-white">Initiate Agent-to-Agent Collaboration</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={newCollab.sender} onChange={e => setNewCollab(p => ({ ...p, sender: e.target.value }))}
                className="bg-zinc-800 border border-white/10 rounded-md px-3 py-2 text-xs text-zinc-300" data-testid="collab-sender">
                <option value="">Select sender agent...</option>
                {agents.slice(0, 50).map(a => <option key={a.agent_id} value={a.name}>{a.name} ({a.role})</option>)}
              </select>
              <select value="" onChange={e => {
                if (e.target.value && !newCollab.receivers.includes(e.target.value))
                  setNewCollab(p => ({ ...p, receivers: [...p.receivers, e.target.value] }));
              }}
                className="bg-zinc-800 border border-white/10 rounded-md px-3 py-2 text-xs text-zinc-300" data-testid="collab-receiver">
                <option value="">Add receiver agent...</option>
                {agents.slice(0, 50).filter(a => a.name !== newCollab.sender).map(a => <option key={a.agent_id} value={a.name}>{a.name} ({a.role})</option>)}
              </select>
            </div>
            {newCollab.receivers.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {newCollab.receivers.map(r => (
                  <Badge key={r} className="bg-violet-500/15 text-violet-300 border border-violet-500/20 text-[10px] gap-1">
                    {r}<button onClick={() => setNewCollab(p => ({ ...p, receivers: p.receivers.filter(x => x !== r) }))} className="hover:text-white">&times;</button>
                  </Badge>
                ))}
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <input value={newCollab.objective} onChange={e => setNewCollab(p => ({ ...p, objective: e.target.value }))}
                placeholder="Collaboration objective..." className="sm:col-span-3 bg-zinc-800 border border-white/10 rounded-md px-3 py-2 text-xs text-zinc-300 placeholder:text-zinc-600" data-testid="collab-objective" />
              <select value={newCollab.collab_type} onChange={e => setNewCollab(p => ({ ...p, collab_type: e.target.value }))}
                className="bg-zinc-800 border border-white/10 rounded-md px-3 py-2 text-xs text-zinc-300" data-testid="collab-type">
                <option value="information_sharing">Info Sharing</option>
                <option value="review_request">Review Request</option>
                <option value="data_handoff">Data Handoff</option>
                <option value="coordination">Coordination</option>
              </select>
            </div>
            <Button onClick={handleCreateCollab} disabled={creating} size="sm" className="bg-violet-600 hover:bg-violet-700 text-xs" data-testid="submit-collab-btn">
              {creating ? "Creating..." : "Create Collaboration"}
            </Button>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : collabs.length > 0 ? (
        <div className="space-y-3">
          {collabs.map(c => <CollabCard key={c.collab_id} collab={c} />)}
        </div>
      ) : (
        <div className="text-center py-16 border border-dashed border-white/10 rounded-xl">
          <Users className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
          <p className="text-zinc-400 text-sm">No collaboration logs yet</p>
          <p className="text-zinc-600 text-xs mt-1">Collaborations are created automatically when agents work together on projects</p>
        </div>
      )}
    </div>
  );
};

export default CollaborationEngine;
