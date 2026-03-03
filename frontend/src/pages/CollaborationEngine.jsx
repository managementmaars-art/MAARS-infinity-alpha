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
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [total, setTotal] = useState(0);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchCollabs = useCallback(async () => {
    try {
      const params = new URLSearchParams({ page: "1", limit: "50" });
      if (filter !== "all") params.set("status", filter);
      const res = await fetch(`${API}/collaborations?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setCollabs(data.items || []);
        setTotal(data.total || 0);
      }
    } catch {} finally { setLoading(false); }
  }, [token, filter]);

  useEffect(() => { fetchCollabs(); }, [fetchCollabs]);

  const statusFilters = ["all", "pending", "in_progress", "completed", "failed"];

  return (
    <div className="space-y-6" data-testid="collaboration-engine">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
          <Users className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Collaboration Engine</h1>
          <p className="text-xs text-zinc-500">Inter-agent communication logs & task collaboration</p>
        </div>
        <Badge variant="outline" className="ml-auto border-white/10 text-zinc-400">{total} total</Badge>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-zinc-500" />
        {statusFilters.map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
              filter === s ? "bg-indigo-500/15 text-indigo-400" : "bg-zinc-800/50 text-zinc-500 hover:text-zinc-300"
            }`}
            data-testid={`filter-${s}`}
          >
            {s === "all" ? "All" : s.replace("_", " ")}
          </button>
        ))}
      </div>

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
