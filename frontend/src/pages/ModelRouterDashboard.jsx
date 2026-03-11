import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Brain, Zap, DollarSign, Clock, ArrowRight, Search, Play, Loader2, FileText } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const PROVIDER_COLORS = {
  openai: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  anthropic: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  google: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  groq: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  deepseek: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  xai: "bg-red-500/20 text-red-400 border-red-500/30",
  perplexity: "bg-violet-500/20 text-violet-400 border-violet-500/30",
};

export default function ModelRouterDashboard() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [execResult, setExecResult] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [history, setHistory] = useState([]);
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const routeTask = async () => {
    if (!query.trim()) return;
    setExecResult(null);
    const res = await fetch(`${API}/api/infinity/router/route`, { method: "POST", headers, body: JSON.stringify({ task_description: query }) });
    const data = await res.json();
    setResult(data);
    setHistory(prev => [{ query, ...data }, ...prev.slice(0, 9)]);
  };

  const executeTask = async () => {
    if (!query.trim()) return;
    setExecuting(true);
    try {
      const res = await fetch(`${API}/api/infinity/router/execute`, { method: "POST", headers, body: JSON.stringify({ task_description: query }) });
      const data = await res.json();
      setExecResult(data);
      setResult(data.routing);
    } catch (e) { console.error(e); }
    setExecuting(false);
  };

  return (
    <div className="space-y-6 max-w-5xl" data-testid="model-router-page">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2"><Brain className="w-6 h-6 text-violet-400" /> Model Router Intelligence</h1>
        <p className="text-sm text-zinc-400">Task-based, cost-aware, latency-aware model selection across 13 providers</p>
      </div>

      {/* Route a Task */}
      <Card className="bg-zinc-900/50 border-white/5" data-testid="route-input-card">
        <CardContent className="p-4">
          <div className="flex gap-2">
            <input
              data-testid="route-query-input"
              className="flex-1 bg-zinc-800/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-violet-500/50"
              placeholder="Describe a task to route... (e.g., 'Analyze competitor pricing strategies')"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && routeTask()}
            />
            <Button onClick={routeTask} className="bg-violet-500 hover:bg-violet-600" data-testid="route-btn"><Search className="w-4 h-4 mr-1" /> Route</Button>
            <Button onClick={executeTask} disabled={executing || !query.trim()} className="bg-emerald-600 hover:bg-emerald-700" data-testid="execute-btn">
              {executing ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Play className="w-4 h-4 mr-1" />} Execute
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card className="bg-zinc-900/50 border-violet-500/20" data-testid="route-result-card">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-violet-400">Routing Decision</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-zinc-800/60 border border-white/10 flex-1">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wide mb-1">Classification</p>
                <div className="flex flex-wrap gap-1">
                  <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">{result.classification?.task_type}</Badge>
                  <Badge variant="outline" className="text-zinc-400">{result.classification?.difficulty}</Badge>
                  <Badge variant="outline" className={result.classification?.risk_level === "high" ? "text-red-400 border-red-500/30" : "text-zinc-400"}>{result.classification?.risk_level} risk</Badge>
                  <Badge variant="outline" className="text-zinc-400">{result.classification?.cost_sensitivity} cost</Badge>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-zinc-500 shrink-0" />
              <div className="p-3 rounded-lg bg-zinc-800/60 border border-white/10 flex-1">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wide mb-1">Selected Model</p>
                <div className="flex items-center gap-2">
                  <Badge className={PROVIDER_COLORS[result.selection?.provider] || ""}>{result.selection?.provider}</Badge>
                  <span className="text-sm font-bold text-white">{result.selection?.model}</span>
                  <Badge variant="outline" className="text-zinc-400">{result.selection?.tier}</Badge>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="p-2 rounded bg-zinc-800/40 text-center"><Zap className="w-3 h-3 text-amber-400 mx-auto mb-1" /><p className="text-xs text-zinc-400">{result.selection?.latency_class}</p><p className="text-[10px] text-zinc-500">Latency</p></div>
              <div className="p-2 rounded bg-zinc-800/40 text-center"><DollarSign className="w-3 h-3 text-emerald-400 mx-auto mb-1" /><p className="text-xs text-zinc-400">${result.selection?.expected_cost_per_1k_out}/1K out</p><p className="text-[10px] text-zinc-500">Cost</p></div>
              <div className="p-2 rounded bg-zinc-800/40 text-center"><Brain className="w-3 h-3 text-violet-400 mx-auto mb-1" /><p className="text-xs text-zinc-400">{result.selection?.reason?.split(":")[0]}</p><p className="text-[10px] text-zinc-500">Reason</p></div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Execution Output */}
      {execResult && (
        <Card className="bg-zinc-900/50 border-emerald-500/20" data-testid="exec-result-card">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-emerald-400 flex items-center gap-2"><FileText className="w-4 h-4" /> LLM Execution Result</CardTitle>
              <div className="flex items-center gap-2">
                <Badge className={PROVIDER_COLORS[execResult.execution?.provider] || ""}>{execResult.execution?.provider}</Badge>
                <span className="text-xs text-white">{execResult.execution?.model}</span>
                <Badge variant="outline" className="text-zinc-400 text-[10px]">{execResult.execution?.latency_ms}ms</Badge>
                <Badge variant="outline" className="text-emerald-400 border-emerald-500/30 text-[10px]">${execResult.execution?.estimated_cost?.toFixed(4)}</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-zinc-800/40 border border-white/5 rounded-lg p-3 max-h-64 overflow-y-auto">
              <pre className="text-xs text-zinc-300 whitespace-pre-wrap font-mono">{execResult.output}</pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* History */}
      {history.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="route-history-card">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Clock className="w-4 h-4 text-zinc-400" /> Routing History</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {history.map((h, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30 text-[10px] shrink-0">{h.classification?.task_type}</Badge>
                  <span className="text-xs text-zinc-300 truncate">{h.query}</span>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Badge className={PROVIDER_COLORS[h.selection?.provider] || ""} >{h.selection?.provider}</Badge>
                  <span className="text-xs text-white">{h.selection?.model}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
