import { useState, useEffect, useCallback, useMemo } from "react";
import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import {
  GraduationCap, Search, Plus, Sparkles, RefreshCw, Loader2,
  ThumbsUp, AlertTriangle, CheckCircle2, XCircle, Save,
  Trash2, Brain, ListChecks, BarChart3
} from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

const SUBTABS = [
  { id: "agents",      label: "Agents",              icon: Brain },
  { id: "queue",       label: "Training Queue",      icon: ListChecks },
  { id: "performance", label: "Performance",         icon: BarChart3 },
];

export const UniversalGatewayTraining = ({ token }) => {
  const [sub, setSub] = useState("agents");
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [networkFilter, setNetworkFilter] = useState("all");
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [perf, setPerf] = useState([]);
  const [queue, setQueue] = useState([]);
  const [busy, setBusy] = useState(false);

  const doFetch = useCallback(async (path, opts = {}) => {
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(opts.headers || {}),
    };
    const r = await fetch(`${API}${path}`, { ...opts, headers });
    const body = r.status !== 204 ? await r.json().catch(() => ({})) : {};
    if (!r.ok) throw new Error(body?.detail || `${r.status} ${r.statusText}`);
    return body;
  }, [token]);

  const loadAgents = useCallback(async () => {
    setLoading(true);
    try {
      const r = await doFetch("/admin/gateway/training/agents");
      setAgents(r?.agents || []);
    } catch (e) {
      toast.error("Failed to load agents: " + e.message);
    } finally {
      setLoading(false);
    }
  }, [doFetch]);

  const loadDetail = useCallback(async (agentId) => {
    try {
      const r = await doFetch(`/admin/gateway/training/agents/${agentId}`);
      setDetail(r);
    } catch (e) {
      toast.error("Failed to load agent: " + e.message);
    }
  }, [doFetch]);

  const loadPerf = useCallback(async () => {
    try {
      const r = await doFetch("/admin/gateway/training/performance?window_days=7");
      setPerf(r?.agents || []);
    } catch (e) {
      toast.error("Failed to load performance: " + e.message);
    }
  }, [doFetch]);

  const loadQueue = useCallback(async () => {
    try {
      const r = await doFetch("/admin/gateway/training/queue?status=pending_review");
      setQueue(r?.items || []);
    } catch (e) {
      toast.error("Failed to load queue: " + e.message);
    }
  }, [doFetch]);

  useEffect(() => { loadAgents(); }, [loadAgents]);
  useEffect(() => { if (selected) loadDetail(selected); }, [selected, loadDetail]);
  useEffect(() => { if (sub === "performance") loadPerf(); }, [sub, loadPerf]);
  useEffect(() => { if (sub === "queue") loadQueue(); }, [sub, loadQueue]);

  const networks = useMemo(() => {
    const set = new Set();
    agents.forEach(a => a.network && set.add(a.network));
    return ["all", ...Array.from(set).sort()];
  }, [agents]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return agents.filter(a => {
      if (networkFilter !== "all" && a.network !== networkFilter) return false;
      if (!q) return true;
      return (
        (a.name || "").toLowerCase().includes(q) ||
        (a.role || "").toLowerCase().includes(q) ||
        (a.agent_id || "").toLowerCase().includes(q)
      );
    });
  }, [agents, search, networkFilter]);

  const seedExamples = async (scope) => {
    if (!selected) return;
    setBusy(true);
    try {
      const r = await doFetch("/admin/gateway/training/seed", {
        method: "POST",
        body: JSON.stringify({ agent_id: selected, scope, count: 3 }),
      });
      toast.success(`Seeded ${r?.created_count || 0} examples at ${scope} scope`);
      await loadDetail(selected);
      await loadAgents();
    } catch (e) {
      toast.error("Seed failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const savePrompt = async () => {
    if (!selected || !detail) return;
    const sp = (detail.agent?.system_prompt || "").trim();
    if (sp.length < 10) {
      toast.error("System prompt is too short");
      return;
    }
    setBusy(true);
    try {
      await doFetch(`/admin/gateway/training/agents/${selected}/prompt`, {
        method: "PUT",
        body: JSON.stringify({ system_prompt: sp }),
      });
      toast.success("Prompt saved. Skill cache cleared.");
    } catch (e) {
      toast.error("Save failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const deleteExample = async (exampleId) => {
    setBusy(true);
    try {
      await doFetch(`/admin/gateway/training/examples/${exampleId}`, { method: "DELETE" });
      toast.success("Example deleted");
      await loadDetail(selected);
      await loadAgents();
    } catch (e) {
      toast.error("Delete failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const actQueue = async (queueId, action, scope = "agent") => {
    setBusy(true);
    try {
      await doFetch("/admin/gateway/training/queue/act", {
        method: "POST",
        body: JSON.stringify({ queue_id: queueId, action, scope_for_approve: scope }),
      });
      toast.success(`${action} complete`);
      await loadQueue();
    } catch (e) {
      toast.error("Action failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500/30 to-cyan-500/30 flex items-center justify-center">
          <GraduationCap className="w-5 h-5 text-teal-300" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Agent Training</h3>
          <p className="text-xs text-zinc-500">
            Curate golden examples · review continuous-improvement queue · rank agents by quality
          </p>
        </div>
      </div>

      {/* Sub-nav */}
      <div className="flex gap-2 border-b border-white/10">
        {SUBTABS.map(s => (
          <button
            key={s.id}
            onClick={() => setSub(s.id)}
            className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 ${
              sub === s.id
                ? "text-white border-teal-400"
                : "text-zinc-500 border-transparent hover:text-zinc-300"
            }`}
          >
            <s.icon className="w-4 h-4 inline mr-1.5 -mt-0.5" />
            {s.label}
          </button>
        ))}
      </div>

      {sub === "agents" && (
        <div className="grid grid-cols-12 gap-4">
          {/* Agent list */}
          <div className="col-span-5 space-y-3">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-zinc-500" />
                <input
                  className="w-full pl-9 pr-3 py-2 text-sm bg-zinc-900/50 border border-white/10 rounded-md text-white placeholder-zinc-500"
                  placeholder="Search by name, role, or agent_id"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <select
                className="bg-zinc-900/50 border border-white/10 rounded-md px-2 py-2 text-sm text-white"
                value={networkFilter}
                onChange={e => setNetworkFilter(e.target.value)}
              >
                {networks.map(n => <option key={n} value={n}>{n === "all" ? "All networks" : n}</option>)}
              </select>
              <Button size="sm" variant="outline" onClick={loadAgents} disabled={loading}
                className="border-white/10 text-zinc-400 hover:text-white">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              </Button>
            </div>
            <div className="text-xs text-zinc-500">{filtered.length} of {agents.length} agents</div>
            <div className="max-h-[70vh] overflow-y-auto space-y-1 pr-2">
              {filtered.map(a => (
                <button
                  key={a.agent_id}
                  onClick={() => setSelected(a.agent_id)}
                  className={`w-full text-left p-3 rounded-md border transition-colors ${
                    selected === a.agent_id
                      ? "bg-teal-500/10 border-teal-500/40"
                      : "bg-zinc-900/30 border-white/5 hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="min-w-0">
                      <div className="text-sm font-medium text-white truncate">{a.name || a.agent_id}</div>
                      <div className="text-xs text-zinc-500 truncate">
                        {a.role || "—"}{a.network ? ` · ${a.network}` : ""}
                      </div>
                    </div>
                    <Badge variant="outline" className={`shrink-0 ${
                      a.golden_examples?.effective > 0
                        ? "border-teal-500/30 text-teal-300"
                        : "border-white/10 text-zinc-500"
                    }`}>
                      {a.golden_examples?.effective || 0} ex
                    </Badge>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Agent detail */}
          <div className="col-span-7 space-y-3">
            {!detail && (
              <Card className="bg-zinc-900/30 border-white/10">
                <CardContent className="p-8 text-center text-zinc-500">
                  Select an agent to view and edit its training.
                </CardContent>
              </Card>
            )}
            {detail && (
              <>
                <Card className="bg-zinc-900/30 border-white/10">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-base font-bold text-white">{detail.agent.name}</div>
                        <div className="text-xs text-zinc-500">
                          {detail.agent.role}
                          {detail.agent.network && ` · ${detail.agent.network}`}
                          {detail.agent.is_commander && " · Commander"}
                          {detail.agent.is_infinity && " · Infinity"}
                        </div>
                      </div>
                      <Button size="sm" onClick={savePrompt} disabled={busy}
                        className="bg-teal-500 hover:bg-teal-600 text-white">
                        {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        <span className="ml-1.5">Save prompt</span>
                      </Button>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500 mb-1">System prompt (edit directly)</div>
                      <textarea
                        className="w-full bg-zinc-950 border border-white/10 rounded-md p-3 text-xs text-white font-mono"
                        rows={10}
                        value={detail.agent.system_prompt || ""}
                        onChange={e => setDetail({
                          ...detail,
                          agent: { ...detail.agent, system_prompt: e.target.value },
                        })}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-zinc-900/30 border-white/10">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium text-white">Golden Examples</div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => seedExamples("role")} disabled={busy}
                          className="border-teal-500/30 text-teal-300 hover:bg-teal-500/10">
                          <Sparkles className="w-4 h-4 mr-1.5" /> Seed role-level
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => seedExamples("agent")} disabled={busy}
                          className="border-white/10 text-zinc-400 hover:text-white">
                          <Sparkles className="w-4 h-4 mr-1.5" /> Seed agent-specific
                        </Button>
                      </div>
                    </div>
                    <div className="text-xs text-zinc-500">
                      Effective at runtime: {detail.effective_examples?.length || 0} example(s).
                      Agent-specific (priority 1) override network (2) override role (3).
                    </div>
                    {(detail.effective_examples || []).length === 0 && (
                      <div className="text-xs text-amber-300/80 bg-amber-500/5 border border-amber-500/20 rounded p-2">
                        No golden examples yet. Seed a few to establish the quality bar.
                      </div>
                    )}
                    {(detail.effective_examples || []).map(ex => (
                      <div key={ex.example_id} className="p-3 bg-zinc-950 border border-white/5 rounded-md text-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="border-white/10 text-zinc-400">
                            {ex.scope}:{ex.scope_value}
                          </Badge>
                          <Button size="sm" variant="ghost" onClick={() => deleteExample(ex.example_id)}
                            className="h-6 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10">
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                        <div>
                          <div className="text-zinc-500 mb-0.5">User input</div>
                          <div className="text-zinc-300 whitespace-pre-wrap">{ex.user_input}</div>
                        </div>
                        <div>
                          <div className="text-zinc-500 mb-0.5">Ideal output</div>
                          <div className="text-zinc-300 whitespace-pre-wrap">{ex.ideal_output}</div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      )}

      {sub === "queue" && (
        <Card className="bg-zinc-900/30 border-white/10">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-white">Pending review</div>
                <div className="text-xs text-zinc-500">
                  Auto-generated by the daily training loop. Approve to add to golden examples / kick off DSPy rewrite.
                </div>
              </div>
              <Button size="sm" variant="outline" onClick={loadQueue}
                className="border-white/10 text-zinc-400 hover:text-white">
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
            {queue.length === 0 && (
              <div className="text-center text-zinc-500 text-sm p-8">
                Queue is empty. The daily training job runs at 24h intervals and promotes thumbed-up responses.
              </div>
            )}
            {queue.map((item, i) => (
              <div key={item._id || item.message_id || i}
                className="p-3 bg-zinc-950 border border-white/5 rounded-md text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {item.kind === "promote_golden" ? (
                      <Badge className="bg-teal-500/20 text-teal-300 border-teal-500/30">
                        <ThumbsUp className="w-3 h-3 mr-1" /> Promote Golden
                      </Badge>
                    ) : (
                      <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30">
                        <AlertTriangle className="w-3 h-3 mr-1" /> DSPy Rewrite
                      </Badge>
                    )}
                    <span className="text-zinc-400">{item.agent_id}</span>
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost"
                      onClick={() => actQueue(item._id || item.message_id, "approve")}
                      className="h-6 text-teal-400 hover:bg-teal-500/10">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> Approve
                    </Button>
                    <Button size="sm" variant="ghost"
                      onClick={() => actQueue(item._id || item.message_id, "reject")}
                      className="h-6 text-rose-400 hover:bg-rose-500/10">
                      <XCircle className="w-3 h-3 mr-1" /> Reject
                    </Button>
                  </div>
                </div>
                {item.kind === "promote_golden" && (
                  <>
                    <div>
                      <div className="text-zinc-500 mb-0.5">User asked</div>
                      <div className="text-zinc-300">{item.user_input}</div>
                    </div>
                    <div>
                      <div className="text-zinc-500 mb-0.5">Agent replied (thumbs up)</div>
                      <div className="text-zinc-300">{item.ideal_output}</div>
                    </div>
                  </>
                )}
                {item.kind === "dspy_rewrite" && (
                  <div className="text-zinc-400">
                    Avg quality score: <b>{item.avg_score ?? "—"}</b> across {item.reviews ?? 0} reviews.
                    Approving kicks off DSPy optimizer; revised prompt will appear here for review.
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {sub === "performance" && (
        <Card className="bg-zinc-900/30 border-white/10">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-white">Last 7 days</div>
                <div className="text-xs text-zinc-500">
                  Blended score = 55% avg quality + 30% user sentiment + 15% efficiency
                </div>
              </div>
              <Button size="sm" variant="outline" onClick={loadPerf}
                className="border-white/10 text-zinc-400 hover:text-white">
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
            {perf.length === 0 && (
              <div className="text-center text-zinc-500 text-sm p-8">
                No measurable signal yet. Data appears once agents handle traffic + get quality-reviewed or thumbed.
              </div>
            )}
            {perf.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead className="text-zinc-500 border-b border-white/10">
                    <tr>
                      <th className="text-left py-2">Agent</th>
                      <th className="text-right py-2">Score</th>
                      <th className="text-right py-2">Quality (1-10)</th>
                      <th className="text-right py-2">Sentiment</th>
                      <th className="text-right py-2">Calls</th>
                      <th className="text-right py-2">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {perf.map(r => (
                      <tr key={r.agent_id} className="border-b border-white/5">
                        <td className="py-2">
                          <div className="text-white">{r.name || r.agent_id}</div>
                          <div className="text-zinc-500">{r.role || ""}</div>
                        </td>
                        <td className="text-right">
                          <span className={`font-mono ${
                            r.score === null ? "text-zinc-600"
                              : r.score >= 0.7 ? "text-teal-300"
                              : r.score >= 0.5 ? "text-amber-300"
                              : "text-rose-300"
                          }`}>
                            {r.score === null ? "—" : r.score.toFixed(2)}
                          </span>
                        </td>
                        <td className="text-right text-zinc-300 font-mono">
                          {(r.quality?.avg_score ?? "—")}{" "}
                          <span className="text-zinc-600">({r.quality?.review_count || 0})</span>
                        </td>
                        <td className="text-right text-zinc-300 font-mono">
                          {r.feedback?.total ? `↑${r.feedback.up}/↓${r.feedback.down}` : "—"}
                        </td>
                        <td className="text-right text-zinc-400 font-mono">{r.cost?.calls || 0}</td>
                        <td className="text-right text-zinc-400 font-mono">
                          ${(r.cost?.cost_usd || 0).toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default UniversalGatewayTraining;
