import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Rocket, GitBranch, Play, Users, Cpu, Clock, CheckCircle, AlertCircle, ArrowRight, Loader2 } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

export default function CommanderOrion() {
  const [goalInput, setGoalInput] = useState("");
  const [env, setEnv] = useState("simulation");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const executeGoal = async () => {
    if (!goalInput.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/infinity/orchestrator/execute`, {
        method: "POST", headers,
        body: JSON.stringify({ description: goalInput, environment: env }),
      });
      const data = await res.json();
      setResult(data);
      setHistory(prev => [data, ...prev.slice(0, 9)]);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const riskColor = { low: "text-emerald-400 border-emerald-500/30", medium: "text-amber-400 border-amber-500/30", high: "text-red-400 border-red-500/30", critical: "text-red-400 bg-red-500/20 border-red-500/30" };
  const typeIcons = { research: "magnifying-glass", engineering: "code", marketing: "megaphone", financial: "chart-bar", legal: "scale", crisis: "exclamation-triangle" };

  return (
    <div className="space-y-6 max-w-5xl" data-testid="commander-orion-page">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2"><Rocket className="w-6 h-6 text-amber-400" /> Commander Orion</h1>
        <p className="text-sm text-zinc-400">Autonomous goal orchestration — classify, decompose, assign, execute, verify</p>
      </div>

      {/* Goal Input */}
      <Card className="bg-zinc-900/50 border-white/5" data-testid="goal-input-card">
        <CardContent className="p-4 space-y-3">
          <textarea
            data-testid="goal-input"
            className="w-full bg-zinc-800/60 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-zinc-500 resize-none focus:outline-none focus:ring-1 focus:ring-amber-500/50"
            rows={3}
            placeholder="Describe your goal... (e.g., 'Research the competitive landscape for enterprise AI platforms and produce a strategic brief')"
            value={goalInput}
            onChange={e => setGoalInput(e.target.value)}
          />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <select data-testid="env-select" className="bg-zinc-800 border border-white/10 rounded px-2 py-1 text-xs text-white" value={env} onChange={e => setEnv(e.target.value)}>
                <option value="simulation">Simulation Mode</option>
                <option value="production">Production Mode</option>
              </select>
              <Badge variant="outline" className="text-zinc-400 border-zinc-600">{env === "simulation" ? "Safe — no real actions" : "Live — real execution"}</Badge>
            </div>
            <Button onClick={executeGoal} disabled={loading || !goalInput.trim()} className="bg-amber-500 hover:bg-amber-600 text-black" data-testid="execute-goal-btn">
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Play className="w-4 h-4 mr-1" />}
              Execute Goal
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card className="bg-zinc-900/50 border-amber-500/20" data-testid="goal-result-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-400 flex items-center gap-2"><CheckCircle className="w-4 h-4" /> Goal Orchestrated</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Classification */}
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">{result.classification?.goal_type}</Badge>
              <Badge className={riskColor[result.classification?.risk_level] || ""}>{result.classification?.risk_level} risk</Badge>
              <Badge variant="outline" className="text-zinc-400">{result.classification?.complexity} complexity</Badge>
              <Badge variant="outline" className="text-cyan-400 border-cyan-500/30">{result.environment}</Badge>
              {result.classification?.ai_powered && (
                <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30">
                  <Cpu className="w-3 h-3 mr-1" />AI via {result.classification?.model_used} ({result.classification?.latency_ms}ms)
                </Badge>
              )}
            </div>

            {/* AI Reasoning */}
            {result.classification?.reasoning && result.classification.ai_powered && (
              <div className="bg-zinc-800/40 border border-white/5 rounded-lg p-3">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wide mb-1">AI Classification Reasoning</p>
                <p className="text-xs text-zinc-300">{result.classification.reasoning}</p>
              </div>
            )}

            {/* Reasoning */}
            <p className="text-xs text-zinc-400 bg-zinc-800/60 p-3 rounded-lg border border-white/5">{result.reasoning}</p>

            {/* Task Graph */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wide">Task Graph — {result.nodes} nodes</p>
                {result.decomposition_meta?.ai_powered && (
                  <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">
                    AI decomposed via {result.decomposition_meta?.model} ({result.decomposition_meta?.latency_ms}ms)
                  </Badge>
                )}
              </div>
              <div className="space-y-1.5">
                {result.goal && (
                  <div className="text-xs text-zinc-300 bg-zinc-800/40 p-2 rounded border border-white/5">
                    <span className="text-zinc-500">Goal ID:</span> {result.goal.goal_id} | <span className="text-zinc-500">Graph:</span> {result.graph_id}
                  </div>
                )}
                {result.node_details?.map((n, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded bg-zinc-800/30 border border-white/5" data-testid={`task-node-${n.node_id}`}>
                    <GitBranch className="w-3 h-3 text-amber-400 shrink-0" />
                    <span className="text-[10px] text-zinc-500 w-12 shrink-0">{n.node_id}</span>
                    <span className="text-xs text-zinc-300 flex-1 truncate">{n.task}</span>
                    <Badge variant="outline" className="text-violet-400 border-violet-500/30 text-[10px] shrink-0">{n.provider}:{n.model}</Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Assignments */}
            {result.assignments?.length > 0 && (
              <div>
                <p className="text-[10px] text-zinc-500 uppercase tracking-wide mb-2">Agent Assignments</p>
                <div className="space-y-1">
                  {result.assignments.map((a, i) => (
                    <div key={i} className="flex items-center gap-2 p-2 rounded bg-zinc-800/40 border border-white/5">
                      <Users className="w-3 h-3 text-indigo-400" />
                      <span className="text-xs text-white flex-1">{a.agent}</span>
                      <ArrowRight className="w-3 h-3 text-zinc-500" />
                      <span className="text-xs text-zinc-400">{a.node_id}</span>
                      <Badge variant="outline" className="text-violet-400 border-violet-500/30 text-[10px]">{a.model}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {result.assignments?.length === 0 && (
              <p className="text-xs text-zinc-500">No agents auto-assigned (agents may lack matching capabilities in DB)</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* History */}
      {history.length > 1 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="goal-history-card">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Clock className="w-4 h-4 text-zinc-400" /> Recent Goals</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {history.slice(1).map((h, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                <div className="flex items-center gap-2">
                  <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30 text-[10px]">{h.classification?.goal_type}</Badge>
                  <span className="text-xs text-zinc-300">{h.nodes} nodes</span>
                </div>
                <span className="text-[10px] text-zinc-500">{h.environment}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
