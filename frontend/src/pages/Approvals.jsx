import { useState, useEffect } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  CheckCircle, XCircle, Clock, Send, Eye, ChevronDown, ChevronUp,
  Loader2, Trash2, FileCheck, AlertTriangle, Filter
} from "lucide-react";
import { toast } from "sonner";

const STATUS_CONFIG = {
  draft: { label: "Pending Approval", color: "bg-amber-500/15 text-amber-400 border-amber-500/20", icon: Clock },
  approved: { label: "Approved", color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20", icon: CheckCircle },
  revision_requested: { label: "Revision Needed", color: "bg-orange-500/15 text-orange-400 border-orange-500/20", icon: AlertTriangle },
  published: { label: "Published", color: "bg-indigo-500/15 text-indigo-400 border-indigo-500/20", icon: Send },
};

const TYPE_LABELS = {
  social_post: "Social Post",
  email_campaign: "Email Campaign",
  blog_post: "Blog Post",
  general: "General",
};

const Approvals = () => {
  const { token } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [expanded, setExpanded] = useState({});
  const [actionLoading, setActionLoading] = useState({});

  const headers = { Authorization: `Bearer ${token}` };

  const fetchApprovals = async () => {
    try {
      const url = filter ? `${API}/approvals?status=${filter}` : `${API}/approvals`;
      const res = await fetch(url, { headers });
      if (res.ok) {
        const data = await res.json();
        setApprovals(data.approvals || []);
        setPendingCount(data.pending_count || 0);
      }
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchApprovals(); }, [token, filter]);

  const handleAction = async (id, action) => {
    setActionLoading(prev => ({ ...prev, [id]: action }));
    try {
      const res = await fetch(`${API}/approvals/${id}/${action}`, {
        method: "POST", headers,
      });
      if (res.ok) {
        toast.success(`${action === "approve" ? "Approved" : action === "publish" ? "Published" : "Revision requested"}`);
        fetchApprovals();
      }
    } catch { toast.error("Action failed"); }
    finally { setActionLoading(prev => ({ ...prev, [id]: null })); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this approval?")) return;
    await fetch(`${API}/approvals/${id}`, { method: "DELETE", headers });
    fetchApprovals();
  };

  if (loading) return null;

  return (
    <div className="space-y-6" data-testid="approvals-page">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
              <FileCheck className="w-5 h-5 text-emerald-400" />
            </div>
            Approvals
            {pendingCount > 0 && (
              <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/20 ml-2">{pendingCount} pending</Badge>
            )}
          </h2>
          <p className="text-zinc-400 text-sm mt-1">Review and approve content before it's published — social posts, emails, campaigns.</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2" data-testid="approval-filters">
        {[{ key: "", label: "All" }, { key: "draft", label: "Pending" }, { key: "approved", label: "Approved" }, { key: "published", label: "Published" }].map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${
              filter === f.key ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30" : "text-zinc-500 hover:text-zinc-300 border border-transparent"
            }`}
            data-testid={`filter-${f.key || "all"}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {approvals.length === 0 ? (
        <div className="text-center py-16">
          <FileCheck className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-zinc-500 text-sm">No approvals yet. When agents create publishable content, it will appear here for your review.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {approvals.map(item => {
            const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.draft;
            const Icon = cfg.icon;
            const isExpanded = expanded[item.approval_id];
            const isLoading = actionLoading[item.approval_id];

            return (
              <Card key={item.approval_id} className="bg-zinc-900/50 border-white/5" data-testid={`approval-${item.approval_id}`}>
                <CardContent className="p-0">
                  {/* Header */}
                  <button
                    onClick={() => setExpanded(prev => ({ ...prev, [item.approval_id]: !prev[item.approval_id] }))}
                    className="w-full flex items-center gap-3 p-4 text-left hover:bg-white/[0.02] transition-colors"
                  >
                    <Icon className={`w-5 h-5 shrink-0 ${cfg.color.split(" ")[1]}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium truncate">{item.title}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-zinc-500">{TYPE_LABELS[item.type] || item.type}</span>
                        {item.agent_name && <span className="text-[10px] text-zinc-600">by {item.agent_name}</span>}
                        <span className="text-[10px] text-zinc-700">{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <Badge variant="outline" className={`${cfg.color} border text-[10px]`}>{cfg.label}</Badge>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
                  </button>

                  {/* Expanded content */}
                  {isExpanded && (
                    <div className="px-4 pb-4 border-t border-white/5">
                      {/* Content Preview */}
                      <div className="mt-3 p-4 bg-zinc-800/50 rounded-lg" data-testid="approval-content-preview">
                        <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Content Preview</p>
                        <div className="text-sm text-zinc-300 whitespace-pre-wrap">{item.content}</div>
                      </div>

                      {/* Metadata */}
                      {item.metadata && Object.keys(item.metadata).length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {Object.entries(item.metadata).map(([k, v]) => (
                            <div key={k} className="px-2 py-1 rounded bg-white/5 text-[10px] text-zinc-400">
                              <span className="text-zinc-600">{k}:</span> {String(v)}
                            </div>
                          ))}
                        </div>
                      )}

                      {item.rejection_reason && (
                        <div className="mt-3 p-3 bg-orange-500/5 border border-orange-500/10 rounded-lg">
                          <p className="text-xs text-orange-400">Revision note: {item.rejection_reason}</p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="mt-4 flex items-center gap-2">
                        {item.status === "draft" && (
                          <>
                            <Button
                              size="sm"
                              className="bg-emerald-600 hover:bg-emerald-500 text-white"
                              onClick={() => handleAction(item.approval_id, "approve")}
                              disabled={!!isLoading}
                              data-testid={`approve-btn-${item.approval_id}`}
                            >
                              {isLoading === "approve" ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <CheckCircle className="w-3 h-3 mr-1" />}
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="border-orange-500/30 text-orange-400 hover:bg-orange-500/10"
                              onClick={() => handleAction(item.approval_id, "reject")}
                              disabled={!!isLoading}
                              data-testid={`reject-btn-${item.approval_id}`}
                            >
                              <XCircle className="w-3 h-3 mr-1" />Request Revision
                            </Button>
                          </>
                        )}
                        {item.status === "approved" && (
                          <Button
                            size="sm"
                            className="bg-indigo-600 hover:bg-indigo-500 text-white"
                            onClick={() => handleAction(item.approval_id, "publish")}
                            disabled={!!isLoading}
                            data-testid={`publish-btn-${item.approval_id}`}
                          >
                            {isLoading === "publish" ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Send className="w-3 h-3 mr-1" />}
                            Publish
                          </Button>
                        )}
                        <div className="flex-1" />
                        <Button variant="ghost" size="sm" className="text-zinc-600 hover:text-red-400" onClick={() => handleDelete(item.approval_id)} data-testid={`delete-btn-${item.approval_id}`}>
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Approvals;
