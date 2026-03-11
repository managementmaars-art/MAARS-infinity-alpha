import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Rocket, GitBranch, Users, Cpu, Shield, Activity, AlertTriangle, CheckCircle, Clock, DollarSign, Brain, Search, Database, Eye } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

export default function ObservabilityDashboard() {
  const [status, setStatus] = useState(null);
  const [breakers, setBreakers] = useState([]);
  const [audit, setAudit] = useState([]);
  const [routerPerf, setRouterPerf] = useState([]);
  const [toolHealth, setToolHealth] = useState([]);
  const [trustLeaders, setTrustLeaders] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [commanderLog, setCommanderLog] = useState([]);
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchAll = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [s, b, a, rp, th, tl, inc, cl] = await Promise.all([
      f("/api/infinity/system/status"),
      f("/api/infinity/governance/circuit-breakers"),
      f("/api/infinity/governance/audit?limit=10"),
      f("/api/infinity/router/performance"),
      f("/api/infinity/tools/health"),
      f("/api/infinity/governance/trust/leaderboard?limit=5"),
      f("/api/infinity/governance/incidents?status=open"),
      f("/api/infinity/orchestrator/log?limit=5"),
    ]);
    if (s) setStatus(s);
    if (b) setBreakers(b);
    if (a?.entries) setAudit(a.entries);
    if (rp) setRouterPerf(rp);
    if (th) setToolHealth(th);
    if (tl) setTrustLeaders(tl);
    if (inc) setIncidents(inc);
    if (cl) setCommanderLog(cl);
  }, [token]);

  useEffect(() => { fetchAll(); const i = setInterval(fetchAll, 15000); return () => clearInterval(i); }, [fetchAll]);

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <Card className="bg-zinc-900/50 border-white/5" data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <CardContent className="p-4 flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg ${color} flex items-center justify-center`}><Icon className="w-4 h-4 text-white" /></div>
        <div><p className="text-[10px] text-zinc-500 uppercase tracking-wide">{label}</p><p className="text-lg font-bold text-white">{value ?? "—"}</p></div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6 max-w-7xl" data-testid="observability-dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Observability Dashboard</h1>
          <p className="text-sm text-zinc-400">Real-time system health, metrics, and governance</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={status?.status === "operational" ? "default" : "destructive"} className={status?.status === "operational" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : ""} data-testid="system-status-badge">
            {status?.status === "operational" ? "All Systems Operational" : "Degraded"}
          </Badge>
          <Button variant="outline" size="sm" onClick={fetchAll} data-testid="refresh-btn"><Activity className="w-3 h-3 mr-1" /> Refresh</Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3" data-testid="stats-grid">
        <StatCard icon={Users} label="Total Agents" value={status?.total_agents} color="bg-indigo-500/20" />
        <StatCard icon={Cpu} label="Busy Agents" value={status?.busy_agents} color="bg-cyan-500/20" />
        <StatCard icon={GitBranch} label="Active Workflows" value={status?.active_workflows} color="bg-amber-500/20" />
        <StatCard icon={Shield} label="Breakers Tripped" value={status?.circuit_breakers_tripped} color="bg-red-500/20" />
        <StatCard icon={Activity} label="Networks" value={status?.agent_networks} color="bg-emerald-500/20" />
        <StatCard icon={AlertTriangle} label="Open Incidents" value={incidents?.length ?? 0} color="bg-orange-500/20" />
        <StatCard icon={Rocket} label="Goals Executed" value={commanderLog?.length ?? 0} color="bg-violet-500/20" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Circuit Breakers */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="circuit-breakers-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Shield className="w-4 h-4 text-red-400" /> Circuit Breakers</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {breakers.slice(0, 5).map((b, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                <span className="text-xs text-zinc-300">{b.name}</span>
                <Badge variant={b.status === "closed" ? "outline" : "destructive"} className={b.status === "closed" ? "text-emerald-400 border-emerald-500/30" : ""}>
                  {b.status}
                </Badge>
              </div>
            ))}
            {breakers.length === 0 && <p className="text-xs text-zinc-500">No circuit breakers configured</p>}
          </CardContent>
        </Card>

        {/* Model Router Performance */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="router-performance-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Brain className="w-4 h-4 text-violet-400" /> Model Router Performance</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {routerPerf.slice(0, 5).map((m, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                <div>
                  <p className="text-xs text-white">{m.provider}/{m.model_name}</p>
                  <p className="text-[10px] text-zinc-500">{m.total_calls} calls, avg ${m.avg_cost}</p>
                </div>
                <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">{(m.success_rate * 100).toFixed(0)}%</Badge>
              </div>
            ))}
            {routerPerf.length === 0 && <p className="text-xs text-zinc-500">No model performance data yet</p>}
          </CardContent>
        </Card>

        {/* Trust Leaderboard */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="trust-leaderboard-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Trust Leaderboard</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {trustLeaders.map((t, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                <span className="text-xs text-zinc-300">{t.entity_id}</span>
                <Badge variant="outline" className={t.score >= 60 ? "text-emerald-400 border-emerald-500/30" : t.score >= 30 ? "text-amber-400 border-amber-500/30" : "text-red-400 border-red-500/30"}>
                  {t.score}
                </Badge>
              </div>
            ))}
            {trustLeaders.length === 0 && <p className="text-xs text-zinc-500">No trust scores recorded yet</p>}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Commander Orion Log */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="commander-log-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Rocket className="w-4 h-4 text-amber-400" /> Commander Orion — Recent Goals</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {commanderLog.map((g, i) => (
              <div key={i} className="p-2 rounded bg-zinc-800/40 border border-white/5">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1.5">
                    <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30 text-[10px]">{g.classification?.goal_type || "general"}</Badge>
                    {g.classification?.ai_powered && <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">AI</Badge>}
                  </div>
                  <Badge variant="outline" className="text-cyan-400 border-cyan-500/30">{g.node_count} nodes</Badge>
                </div>
                <p className="text-[10px] text-zinc-500">
                  {g.environment} | {g.assignments?.length ?? 0} assigned
                  {g.classification?.model_used && ` | ${g.classification.model_used}`}
                  {g.decomposition_meta?.ai_powered && ` | AI decomp`}
                  {" | "}{new Date(g.timestamp).toLocaleString()}
                </p>
              </div>
            ))}
            {commanderLog.length === 0 && <p className="text-xs text-zinc-500">No goals executed yet</p>}
          </CardContent>
        </Card>

        {/* Audit Trail */}
        <Card className="bg-zinc-900/50 border-white/5" data-testid="audit-trail-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Eye className="w-4 h-4 text-pink-400" /> Audit Trail</CardTitle></CardHeader>
          <CardContent className="space-y-1">
            {audit.map((a, i) => (
              <div key={i} className="flex items-center gap-2 p-1.5 rounded bg-zinc-800/40 border border-white/5">
                <div className={`w-1.5 h-1.5 rounded-full ${a.result === "success" ? "bg-emerald-400" : "bg-red-400"}`} />
                <span className="text-[10px] text-zinc-300 flex-1">{a.action}</span>
                <span className="text-[10px] text-zinc-500">{a.actor_id}</span>
              </div>
            ))}
            {audit.length === 0 && <p className="text-xs text-zinc-500">No audit entries yet</p>}
          </CardContent>
        </Card>
      </div>

      {/* Verification Stats */}
      {status?.verification_stats?.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="verification-stats-panel">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Search className="w-4 h-4 text-cyan-400" /> Verification Statistics</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {status.verification_stats.map((v, i) => (
                <div key={i} className="p-3 rounded bg-zinc-800/40 border border-white/5 text-center">
                  <p className="text-lg font-bold text-white">{(v.pass_rate * 100).toFixed(0)}%</p>
                  <p className="text-[10px] text-zinc-500">{v.type} ({v.total} checks)</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
