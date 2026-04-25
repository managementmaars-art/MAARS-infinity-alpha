import { useState, useEffect, useCallback, useMemo } from "react";
import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import {
  Workflow, RefreshCw, AlertTriangle, CheckCircle2,
  Play, Activity, Zap, ExternalLink, Clock
} from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

export const UniversalGatewayWorkflows = ({ token }) => {
  const [stats, setStats] = useState(null);
  const [windowHours, setWindowHours] = useState(24);
  const [loading, setLoading] = useState(true);
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

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await doFetch(`/admin/gateway/workflows/stats?window_hours=${windowHours}`);
      setStats(r);
    } catch (e) {
      toast.error("Failed to load workflow stats: " + e.message);
    } finally {
      setLoading(false);
    }
  }, [doFetch, windowHours]);

  useEffect(() => { load(); }, [load]);

  const replayRun = async (runId) => {
    setBusy(true);
    try {
      const r = await doFetch(`/admin/gateway/workflows/${runId}/replay`, { method: "POST" });
      toast.success(`Replay queued → new run ${r.run_id}`);
      await load();
    } catch (e) {
      toast.error("Replay failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const diagnoseRun = async (runId) => {
    setBusy(true);
    try {
      const r = await doFetch(`/admin/gateway/workflows/${runId}/diagnose`);
      const summary = r.summary || "No summary returned";
      const fix = r.proposed_fix ? ` · Fix: ${r.proposed_fix.kind} on ${r.proposed_fix.target_node_id}` : "";
      toast(summary + fix, { duration: 8000 });
    } catch (e) {
      toast.error("Diagnose failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const gotoBuilder = () => {
    window.open("/workflow-builder", "_blank");
  };

  const runs    = stats?.runs || {};
  const wfMeta  = stats?.workflows || {};
  const topRuns = stats?.top_workflows_by_runs || [];
  const topSpend = stats?.top_workflows_by_spend || [];
  const failures = stats?.recent_failures || [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500/30 to-indigo-500/30 flex items-center justify-center">
            <Workflow className="w-5 h-5 text-violet-300" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white font-['Outfit']">Workflows</h3>
            <p className="text-xs text-zinc-500">
              Fleet-wide workflow health · shares `gateway_usage_logs` with LLM spend
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={windowHours}
            onChange={e => setWindowHours(parseInt(e.target.value, 10))}
            className="bg-zinc-900/50 border border-white/10 rounded-md px-2 py-1.5 text-sm text-white"
          >
            <option value={1}>Last hour</option>
            <option value={6}>6 hours</option>
            <option value={24}>24 hours</option>
            <option value={168}>7 days</option>
            <option value={720}>30 days</option>
          </select>
          <Button size="sm" variant="outline" onClick={load} disabled={loading}
            className="border-white/10 text-zinc-400 hover:text-white">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
          <Button size="sm" onClick={gotoBuilder}
            className="bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 border border-violet-500/40">
            <ExternalLink className="w-4 h-4 mr-1.5" /> Open Builder
          </Button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        {[
          { label: "Total workflows", value: wfMeta.total ?? "—", icon: Workflow, color: "text-violet-300" },
          { label: "Active",          value: wfMeta.active ?? "—", icon: Zap, color: "text-teal-300" },
          { label: "Runs in window",  value: runs.total ?? "—", icon: Activity, color: "text-indigo-300" },
          { label: "Completed",       value: runs.completed ?? "—", icon: CheckCircle2, color: "text-emerald-300" },
          { label: "Failed",          value: runs.failed ?? "—", icon: AlertTriangle, color: "text-rose-300" },
          { label: "Error rate",      value: (runs.error_rate_pct ?? 0).toFixed(1) + "%", icon: AlertTriangle,
            color: (runs.error_rate_pct ?? 0) > 10 ? "text-rose-300" : "text-zinc-300" },
        ].map((kpi, i) => (
          <Card key={i} className="bg-zinc-900/30 border-white/10">
            <CardContent className="p-3">
              <div className="flex items-center gap-2 text-xs text-zinc-500 mb-1">
                <kpi.icon className={`w-3.5 h-3.5 ${kpi.color}`} /> {kpi.label}
              </div>
              <div className={`text-xl font-bold ${kpi.color}`}>{kpi.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {runs.stuck_queued > 0 && (
        <Card className="bg-amber-500/5 border-amber-500/30">
          <CardContent className="p-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-300" />
            <span className="text-sm text-amber-200">
              <b>{runs.stuck_queued}</b> run(s) stuck in `queued` for &gt; 5 min — scheduler tick may be lagging.
            </span>
          </CardContent>
        </Card>
      )}

      {/* Top workflows by runs */}
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-white mb-3">Top workflows by runs</div>
          {topRuns.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm p-6">No runs in this window.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="text-zinc-500 border-b border-white/10">
                  <tr>
                    <th className="text-left py-2">Workflow</th>
                    <th className="text-right py-2">Runs</th>
                    <th className="text-right py-2">Failed</th>
                    <th className="text-right py-2">Error %</th>
                    <th className="text-left py-2 pl-4">Last</th>
                  </tr>
                </thead>
                <tbody>
                  {topRuns.map(r => (
                    <tr key={r.workflow_id} className="border-b border-white/5">
                      <td className="py-2">
                        <div className="text-white">{r.name}</div>
                        <div className="text-zinc-600 font-mono">{r.workflow_id}</div>
                      </td>
                      <td className="text-right text-zinc-300 font-mono">{r.runs}</td>
                      <td className={`text-right font-mono ${r.failed_runs > 0 ? "text-rose-300" : "text-zinc-600"}`}>
                        {r.failed_runs}
                      </td>
                      <td className={`text-right font-mono ${r.error_rate_pct > 10 ? "text-rose-300" : "text-zinc-400"}`}>
                        {r.error_rate_pct}%
                      </td>
                      <td className="pl-4 text-zinc-500">{r.last_started_at?.slice(0, 19).replace("T", " ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Top workflows by spend */}
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-white mb-3">Top by LLM spend (from gateway_usage_logs)</div>
          {topSpend.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm p-6">No workflow LLM calls in this window.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="text-zinc-500 border-b border-white/10">
                  <tr>
                    <th className="text-left py-2">Source tag</th>
                    <th className="text-right py-2">Calls</th>
                    <th className="text-right py-2">Credits</th>
                    <th className="text-right py-2">Cost USD</th>
                  </tr>
                </thead>
                <tbody>
                  {topSpend.map(s => (
                    <tr key={s.source} className="border-b border-white/5">
                      <td className="py-2 text-zinc-300 font-mono">{s.source}</td>
                      <td className="text-right text-zinc-400 font-mono">{s.calls}</td>
                      <td className="text-right text-zinc-400 font-mono">{s.credits}</td>
                      <td className="text-right text-emerald-300 font-mono">${s.cost_usd.toFixed(6)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent failures */}
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-white mb-3">Recent failures</div>
          {failures.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm p-6">No failures in this window. 🎉</div>
          ) : (
            <div className="space-y-2">
              {failures.map(f => (
                <div key={f.run_id} className="p-3 bg-zinc-950 border border-rose-500/20 rounded-md text-xs">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2 min-w-0">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-300 shrink-0" />
                      <Badge variant="outline" className="border-rose-500/30 text-rose-300 shrink-0">
                        {f.failed_node || "node"}
                      </Badge>
                      <span className="text-zinc-400 font-mono truncate">{f.run_id}</span>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <Button size="sm" variant="ghost" onClick={() => diagnoseRun(f.run_id)} disabled={busy}
                        className="h-7 text-indigo-300 hover:bg-indigo-500/10 text-xs">
                        Diagnose
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => replayRun(f.run_id)} disabled={busy}
                        className="h-7 text-teal-300 hover:bg-teal-500/10 text-xs">
                        <Play className="w-3 h-3 mr-1" /> Replay
                      </Button>
                    </div>
                  </div>
                  <div className="text-zinc-300 pl-6 whitespace-pre-wrap">{(f.error || "").slice(0, 300)}</div>
                  <div className="text-zinc-600 pl-6 mt-1 font-mono">
                    workflow {f.workflow_id} · user {f.user_id?.slice(0, 8)}… · {f.started_at?.slice(0, 19).replace("T", " ")}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UniversalGatewayWorkflows;
