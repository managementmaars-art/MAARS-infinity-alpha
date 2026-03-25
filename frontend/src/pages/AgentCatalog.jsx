import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Users, Search, Brain, Shield, Layers, ChevronRight, Play,
  Loader2, CheckCircle, AlertTriangle, Cpu, GitBranch, Filter, X
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const MATURITY_COLORS = {
  "production-ready": "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  "partial": "bg-amber-500/15 text-amber-400 border-amber-500/20",
  "experimental": "bg-violet-500/15 text-violet-400 border-violet-500/20",
  "catalog-only": "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
};

const TIER_COLORS = ["text-zinc-500", "text-zinc-400", "text-cyan-400", "text-emerald-400", "text-amber-400", "text-red-400"];

export default function AgentCatalog() {
  const [stats, setStats] = useState(null);
  const [networks, setNetworks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [filterNetwork, setFilterNetwork] = useState("");
  const [filterMaturity, setFilterMaturity] = useState("");
  const [filterTier, setFilterTier] = useState("");
  const [selected, setSelected] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [execResult, setExecResult] = useState(null);
  const [taskInput, setTaskInput] = useState("");
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [s, n] = await Promise.all([f("/api/infinity/catalog/stats"), f("/api/infinity/catalog/networks")]);
    if (s) setStats(s);
    if (n) setNetworks(n);
  }, [token]);

  const fetchAgents = useCallback(async () => {
    const params = new URLSearchParams({ limit: "50" });
    if (search) params.set("search", search);
    if (filterNetwork) params.set("network", filterNetwork);
    if (filterMaturity) params.set("maturity", filterMaturity);
    if (filterTier) params.set("tier", filterTier);
    const res = await fetch(`${API}/api/infinity/catalog/agents?${params}`, { headers }).catch(() => null);
    if (res?.ok) {
      const d = await res.json();
      setAgents(d.agents || []);
      setTotal(d.total || 0);
    }
  }, [token, search, filterNetwork, filterMaturity, filterTier]);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const selectAgent = async (agentId) => {
    setExecResult(null);
    setTaskInput("");
    const res = await fetch(`${API}/api/infinity/catalog/agents/${agentId}`, { headers }).catch(() => null);
    if (res?.ok) setSelected(await res.json());
  };

  const executeAgent = async () => {
    if (!selected || !taskInput.trim()) return;
    setExecuting(true);
    setExecResult(null);
    const res = await fetch(`${API}/api/infinity/runtime/execute`, {
      method: "POST", headers,
      body: JSON.stringify({ agent_id: selected.agent_id, task_description: taskInput, environment: "sandbox" }),
    });
    if (res.ok) setExecResult(await res.json());
    setExecuting(false);
  };

  const clearFilters = () => { setSearch(""); setFilterNetwork(""); setFilterMaturity(""); setFilterTier(""); };
  const hasFilters = search || filterNetwork || filterMaturity || filterTier;

  return (
    <div className="space-y-5" data-testid="agent-catalog">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2"><Users className="w-6 h-6 text-indigo-400" /> Agent Catalog</h1>
          <p className="text-sm text-zinc-400">{stats?.total_agents || 0} agents across {networks.length} networks — full registry, search, inspect, execute</p>
        </div>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="catalog-stats">
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-white">{stats.total_agents}</p><p className="text-[10px] text-zinc-500">Total Agents</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-white">{stats.by_network?.length}</p><p className="text-[10px] text-zinc-500">Networks</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-white">{stats.by_tier?.length}</p><p className="text-[10px] text-zinc-500">Autonomy Tiers</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-emerald-400">{stats.by_maturity?.find(m => m.maturity === "production-ready")?.count || 0}</p>
            <p className="text-[10px] text-zinc-500">Production Ready</p>
          </CardContent></Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-zinc-900/50 border-white/5" data-testid="catalog-filters">
        <CardContent className="p-3 flex flex-wrap items-center gap-2">
          <div className="relative flex-1 min-w-48">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search agents by name, role, or ID..."
              className="w-full bg-zinc-800/50 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500/30" data-testid="search-input" />
          </div>
          <select value={filterNetwork} onChange={e => setFilterNetwork(e.target.value)} className="bg-zinc-800 text-zinc-400 text-[11px] border border-white/10 rounded px-2 py-1.5" data-testid="filter-network">
            <option value="">All Networks</option>
            {networks.map(n => <option key={n.network_id} value={n.network_id}>{n.name} ({n.agent_count})</option>)}
          </select>
          <select value={filterMaturity} onChange={e => setFilterMaturity(e.target.value)} className="bg-zinc-800 text-zinc-400 text-[11px] border border-white/10 rounded px-2 py-1.5" data-testid="filter-maturity">
            <option value="">All Maturity</option>
            <option value="production-ready">Production Ready</option>
            <option value="partial">Partial</option>
            <option value="experimental">Experimental</option>
            <option value="catalog-only">Catalog Only</option>
          </select>
          <select value={filterTier} onChange={e => setFilterTier(e.target.value)} className="bg-zinc-800 text-zinc-400 text-[11px] border border-white/10 rounded px-2 py-1.5" data-testid="filter-tier">
            <option value="">All Tiers</option>
            {[0,1,2,3,4,5].map(t => <option key={t} value={t}>Tier {t}</option>)}
          </select>
          {hasFilters && <Button variant="ghost" size="sm" onClick={clearFilters} className="h-7 text-[10px] text-zinc-500"><X className="w-3 h-3 mr-1" />Clear</Button>}
          <span className="text-[10px] text-zinc-500">{total} results</span>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Agent List */}
        <div className="lg:col-span-2 space-y-1.5" data-testid="agent-list">
          {agents.map(a => (
            <div key={a.agent_id} onClick={() => selectAgent(a.agent_id)}
              className={`flex items-center gap-3 p-2.5 rounded-lg border cursor-pointer transition-all ${selected?.agent_id === a.agent_id ? "bg-cyan-500/5 border-cyan-500/20" : "bg-zinc-900/50 border-white/5 hover:bg-zinc-800/50"}`}
              data-testid={`agent-row-${a.agent_id}`}>
              <div className={`w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center text-indigo-400 text-[10px] font-bold shrink-0`}>
                T{a.autonomy_tier}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-white font-medium truncate">{a.name}</span>
                  <Badge className={`${MATURITY_COLORS[a.maturity] || MATURITY_COLORS["production-ready"]} text-[8px] px-1 py-0`}>{a.maturity || "ready"}</Badge>
                </div>
                <p className="text-[10px] text-zinc-500 truncate">{a.role} — {a.network?.replace(/_/g, " ")}</p>
              </div>
              <ChevronRight className="w-3 h-3 text-zinc-600 shrink-0" />
            </div>
          ))}
          {agents.length === 0 && <p className="text-xs text-zinc-500 text-center py-8">No agents match your filters</p>}
        </div>

        {/* Agent Detail Panel */}
        <div className="space-y-3" data-testid="agent-detail-panel">
          {selected ? (
            <>
              <Card className="bg-zinc-900/50 border-cyan-500/15">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm text-white">{selected.name}</CardTitle>
                    <Badge className={MATURITY_COLORS[selected.maturity] || MATURITY_COLORS["production-ready"]}>{selected.maturity || "production-ready"}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-xs text-zinc-400">{selected.description}</p>
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="outline" className="text-indigo-400 border-indigo-500/30 text-[9px]">Tier {selected.autonomy_tier}</Badge>
                    <Badge variant="outline" className="text-zinc-400 border-zinc-600 text-[9px]">{selected.network?.replace(/_/g, " ")}</Badge>
                    {selected.authority_tier && <Badge variant="outline" className="text-amber-400 border-amber-500/30 text-[9px]">{selected.authority_tier}</Badge>}
                  </div>
                  <div>
                    <p className="text-[10px] text-zinc-500 mb-1">Capabilities</p>
                    <div className="flex flex-wrap gap-1">
                      {selected.capabilities?.map((c, i) => (
                        <Badge key={i} variant="outline" className="text-cyan-400 border-cyan-500/20 text-[8px]">{c}</Badge>
                      ))}
                    </div>
                  </div>
                  {selected.trust_detail && (
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-zinc-500">Trust Score:</span>
                      <Badge className={selected.trust_detail.score >= 60 ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-amber-500/15 text-amber-400 text-[10px]"}>{selected.trust_detail.score?.toFixed(1)}</Badge>
                    </div>
                  )}
                  <p className="text-[9px] text-zinc-600 font-mono">{selected.agent_id}</p>
                </CardContent>
              </Card>

              {/* Execute Agent */}
              <Card className="bg-zinc-900/50 border-white/5">
                <CardHeader className="pb-2"><CardTitle className="text-xs text-white flex items-center gap-2"><Play className="w-3 h-3 text-emerald-400" /> Execute Agent</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  <textarea value={taskInput} onChange={e => setTaskInput(e.target.value)}
                    placeholder={`Give ${selected.name} a task...`}
                    className="w-full bg-zinc-800/50 border border-white/10 rounded p-2 text-xs text-white placeholder-zinc-500 resize-none focus:outline-none focus:border-cyan-500/30"
                    rows={2} data-testid="task-input" />
                  <Button onClick={executeAgent} disabled={executing || !taskInput.trim()} className="bg-emerald-600 hover:bg-emerald-700 w-full text-xs" data-testid="execute-agent-btn">
                    {executing ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Play className="w-3 h-3 mr-1" />}
                    Execute via Runtime Loop
                  </Button>
                </CardContent>
              </Card>

              {/* Execution Result */}
              {execResult && (
                <Card className={`border ${execResult.status === "completed" ? "border-emerald-500/15" : "border-red-500/15"} bg-zinc-900/50`} data-testid="exec-result">
                  <CardHeader className="pb-1">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xs text-white">Runtime Result</CardTitle>
                      <Badge className={execResult.status === "completed" ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>
                        {execResult.summary?.passed}/{execResult.summary?.total} steps | {execResult.summary?.latency_ms}ms
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-1">
                    {execResult.steps?.map((s, i) => (
                      <div key={i} className="flex items-center gap-1.5 text-[10px]">
                        {s.status === "pass" ? <CheckCircle className="w-2.5 h-2.5 text-emerald-400" /> : <AlertTriangle className="w-2.5 h-2.5 text-red-400" />}
                        <span className="text-zinc-500 w-24 shrink-0">{s.step}</span>
                        <span className="text-zinc-400 truncate">{s.detail}</span>
                      </div>
                    ))}
                    {execResult.output && (
                      <details className="mt-2">
                        <summary className="text-[10px] text-cyan-400 cursor-pointer">View Output</summary>
                        <pre className="text-[10px] text-zinc-400 whitespace-pre-wrap mt-1 p-2 bg-zinc-800/40 rounded max-h-40 overflow-y-auto">{execResult.output}</pre>
                      </details>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Recent Executions */}
              {selected.recent_executions?.length > 0 && (
                <Card className="bg-zinc-900/50 border-white/5">
                  <CardHeader className="pb-1"><CardTitle className="text-xs text-zinc-400">Recent Executions</CardTitle></CardHeader>
                  <CardContent className="space-y-1">
                    {selected.recent_executions.map((e, i) => (
                      <div key={i} className="flex items-center justify-between text-[10px] p-1 rounded bg-zinc-800/40">
                        <span className="text-zinc-400 truncate">{e.task}</span>
                        <Badge className={e.status === "completed" ? "bg-emerald-500/10 text-emerald-400 text-[8px]" : "bg-red-500/10 text-red-400 text-[8px]"}>{e.status}</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card className="bg-zinc-900/50 border-white/5">
              <CardContent className="p-8 text-center">
                <Users className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                <p className="text-xs text-zinc-500">Select an agent to inspect</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
