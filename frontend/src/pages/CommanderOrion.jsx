import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Rocket, GitBranch, Cpu, CheckCircle, XCircle, Clock, Activity,
  Play, Loader2, AlertCircle, FileText, ChevronRight, Zap, Wifi, WifiOff
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const riskColor = {
  low: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  high: "bg-red-500/20 text-red-400 border-red-500/30",
  critical: "bg-red-600/30 text-red-300 border-red-600/40",
};

export default function CommanderOrion() {
  const [goal, setGoal] = useState("");
  const [mode, setMode] = useState("full");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [liveSteps, setLiveSteps] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchRuns = useCallback(async () => {
    const res = await fetch(`${API}/api/infinity/orchestrator/runs?limit=8`, { headers }).catch(() => null);
    if (res?.ok) setRuns(await res.json());
  }, [token]);

  useEffect(() => { fetchRuns(); }, [fetchRuns]);

  /* ─── WebSocket for live step streaming ─── */
  useEffect(() => {
    if (!token) return;
    const wsUrl = API.replace(/^http/, "ws") + `/api/ws/infinity?token=${token}&channel=global`;
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => { setWsConnected(true); wsRef.current = ws; };
      ws.onclose = () => { setWsConnected(false); reconnectTimer = setTimeout(connect, 5000); };
      ws.onerror = () => { ws.close(); };
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "step_update") {
            setLiveSteps(prev => {
              const existing = prev.findIndex(s => s.step === data.step && s.execution_id === data.execution_id);
              if (existing >= 0) {
                const updated = [...prev];
                updated[existing] = data;
                return updated;
              }
              return [...prev, data];
            });
          }
        } catch {}
      };
    };
    connect();

    return () => { clearTimeout(reconnectTimer); ws?.close(); };
  }, [token]);

  const executeGoal = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setResult(null);
    setSelectedRun(null);
    setLiveSteps([]);
    try {
      const endpoint = mode === "full" ? "/api/infinity/orchestrator/full-execute" : "/api/infinity/orchestrator/execute";
      const res = await fetch(`${API}${endpoint}`, {
        method: "POST", headers,
        body: JSON.stringify({ description: goal, requester_id: "operator", environment: mode === "full" ? "production" : "simulation" }),
      });
      const data = await res.json();
      setResult(data);
      fetchRuns();
    } catch (e) {
      setResult({ error: e.message });
    }
    setLoading(false);
  };

  const exec = result?.execution;
  const classification = result?.classification;

  return (
    <div className="space-y-5" data-testid="commander-orion">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <Rocket className="w-6 h-6 text-amber-400" /> Commander Orion
          </h1>
          <p className="text-sm text-zinc-400">AI-powered goal orchestration: classify, decompose, execute, verify, report</p>
        </div>
        {wsConnected ? (
          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-[10px]" data-testid="ws-status-commander"><Wifi className="w-3 h-3 mr-1" /> Live Stream</Badge>
        ) : (
          <Badge className="bg-zinc-700/30 text-zinc-500 border-zinc-600/30 text-[10px]" data-testid="ws-status-commander"><WifiOff className="w-3 h-3 mr-1" /> Offline</Badge>
        )}
      </div>

      {/* Goal Input */}
      <Card className="bg-zinc-900/50 border-white/5">
        <CardContent className="p-4">
          <textarea
            value={goal} onChange={e => setGoal(e.target.value)}
            placeholder="Describe your goal... (e.g., 'Analyze the competitive landscape for enterprise AI')"
            className="w-full bg-zinc-800/50 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-zinc-500 resize-none focus:outline-none focus:border-cyan-500/30"
            rows={3} data-testid="goal-input"
          />
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-2">
              <select value={mode} onChange={e => setMode(e.target.value)} className="bg-zinc-800 text-zinc-400 text-xs border border-white/10 rounded px-2 py-1.5" data-testid="mode-select">
                <option value="full">Full Execute (classify \u2192 decompose \u2192 execute \u2192 verify \u2192 report)</option>
                <option value="plan">Plan Only (classify \u2192 decompose \u2192 assign)</option>
              </select>
            </div>
            <Button onClick={executeGoal} disabled={loading || !goal.trim()} className="bg-amber-600 hover:bg-amber-700" data-testid="execute-goal-btn">
              {loading ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Zap className="w-4 h-4 mr-1" />}
              {mode === "full" ? "Execute Goal" : "Plan Goal"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Live Step Progress (WebSocket) */}
      {loading && liveSteps.length > 0 && (
        <Card className="bg-zinc-900/50 border-cyan-500/20" data-testid="live-steps-panel">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-cyan-400 flex items-center gap-2">
              <Activity className="w-4 h-4 animate-pulse" /> Live Execution Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {liveSteps.map((s, i) => (
              <div key={i} className={`flex items-center gap-2 p-1.5 rounded text-[11px] ${s.status === "pass" ? "bg-emerald-500/5 border border-emerald-500/10" : s.status === "fail" ? "bg-red-500/5 border border-red-500/10" : "bg-zinc-800/40 border border-white/5"}`}>
                {s.status === "pass" ? <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0" /> : s.status === "fail" ? <XCircle className="w-3 h-3 text-red-400 shrink-0" /> : <Loader2 className="w-3 h-3 text-cyan-400 animate-spin shrink-0" />}
                <span className="text-zinc-500 w-8 shrink-0">{s.step_num}</span>
                <span className="text-zinc-300 font-medium">{s.step}</span>
                <span className="text-zinc-500 flex-1 truncate">{s.detail}</span>
                <Badge className="bg-zinc-800 text-zinc-400 text-[9px]">{s.progress}%</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Loading State (fallback when no WS steps) */}
      {loading && liveSteps.length === 0 && (
        <Card className="bg-zinc-900/50 border-cyan-500/20">
          <CardContent className="p-6 text-center">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
            <p className="text-sm text-white font-medium">Executing goal pipeline...</p>
            <p className="text-xs text-zinc-400 mt-1">
              {mode === "full" ? "Classifying \u2192 Decomposing \u2192 Executing nodes \u2192 Verifying \u2192 Generating report" : "Classifying \u2192 Decomposing \u2192 Assigning agents"}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-4" data-testid="execution-result">
          {/* Classification */}
          <Card className="bg-zinc-900/50 border-white/5">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Cpu className="w-4 h-4 text-cyan-400" /> Classification & Decomposition</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-1.5">
                <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">{classification?.goal_type}</Badge>
                <Badge className={riskColor[classification?.risk_level] || ""}>{classification?.risk_level} risk</Badge>
                <Badge variant="outline" className="text-zinc-400">{classification?.complexity} complexity</Badge>
                {classification?.ai_powered && (
                  <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30">
                    AI via {classification.model_used} ({classification.latency_ms}ms)
                  </Badge>
                )}
                {result.decomposition_meta?.ai_powered && (
                  <Badge className="bg-cyan-500/15 text-cyan-400 border-cyan-500/30">
                    Decomp via {result.decomposition_meta.model} ({result.decomposition_meta.latency_ms}ms)
                  </Badge>
                )}
              </div>
              {classification?.reasoning && classification.ai_powered && (
                <p className="text-xs text-zinc-400 bg-zinc-800/40 p-2 rounded border border-white/5">{classification.reasoning}</p>
              )}
            </CardContent>
          </Card>

          {/* Task Graph + Execution */}
          <Card className="bg-zinc-900/50 border-white/5">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm text-white flex items-center gap-2"><GitBranch className="w-4 h-4 text-amber-400" /> Task Graph \u2014 {result.nodes} nodes</CardTitle>
                {exec?.summary && (
                  <div className="flex items-center gap-2">
                    <Badge className={exec.summary.failed === 0 ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>
                      {exec.summary.completed}/{exec.summary.total_nodes} completed
                    </Badge>
                    <span className="text-[10px] text-zinc-500">${exec.summary.total_cost?.toFixed(4)} | {(exec.summary.total_latency_ms / 1000)?.toFixed(1)}s</span>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-1.5">
              {(exec?.node_results || result.node_details || []).map((n, i) => {
                const isExec = !!n.provider;
                return (
                  <div key={i} className={`flex items-center gap-2 p-2 rounded border ${n.status === "completed" ? "bg-emerald-500/5 border-emerald-500/10" : n.status === "failed" ? "bg-red-500/5 border-red-500/10" : "bg-zinc-800/30 border-white/5"}`} data-testid={`node-${n.node_id}`}>
                    {isExec ? (
                      n.status === "completed" ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                    ) : (
                      <GitBranch className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    )}
                    <span className="text-[10px] text-zinc-500 w-12 shrink-0">{n.node_id}</span>
                    <span className="text-xs text-zinc-300 flex-1 truncate">{n.task || n.task_description}</span>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {isExec && (
                        <>
                          <Badge variant="outline" className="text-violet-400 border-violet-500/30 text-[9px]">{n.provider}:{n.model?.split("/").pop()}</Badge>
                          <span className="text-[9px] text-zinc-500">{n.latency_ms}ms</span>
                          <Badge className={n.verification_pass ? "bg-emerald-500/10 text-emerald-400 text-[9px]" : "bg-amber-500/10 text-amber-400 text-[9px]"}>v={n.verification_score?.toFixed(1)}</Badge>
                        </>
                      )}
                      {!isExec && n.model && (
                        <Badge variant="outline" className="text-violet-400 border-violet-500/30 text-[9px]">{n.provider}:{n.model}</Badge>
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Final Report */}
          {exec?.final_report && (
            <Card className="bg-zinc-900/50 border-emerald-500/15" data-testid="final-report">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-emerald-400 flex items-center gap-2"><FileText className="w-4 h-4" /> Final Consolidated Report</CardTitle></CardHeader>
              <CardContent>
                <div className="bg-zinc-800/40 border border-white/5 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-xs text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed">{exec.final_report}</pre>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Recent Runs */}
      {runs.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/5" data-testid="recent-runs">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Clock className="w-4 h-4 text-zinc-400" /> Recent Execution Runs</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {runs.map((r, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5 cursor-pointer hover:bg-zinc-800/60 transition-colors" onClick={() => setSelectedRun(selectedRun?.run_id === r.run_id ? null : r)} data-testid={`history-run-${r.run_id}`}>
                <div className="flex items-center gap-2 min-w-0">
                  <Badge className={r.status === "completed" ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>{r.status}</Badge>
                  <span className="text-xs text-zinc-300 truncate">{r.objective?.slice(0, 60)}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] text-zinc-500">{r.summary?.completed}/{r.summary?.total_nodes} nodes</span>
                  <span className="text-[10px] text-zinc-500">${r.summary?.total_cost?.toFixed(4)}</span>
                  <ChevronRight className={`w-3 h-3 text-zinc-600 transition-transform ${selectedRun?.run_id === r.run_id ? "rotate-90" : ""}`} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Selected Run Detail */}
      {selectedRun && (
        <Card className="bg-zinc-900/50 border-cyan-500/15" data-testid="run-detail">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-cyan-400 flex items-center gap-2"><Activity className="w-4 h-4" /> Run Detail: {selectedRun.run_id}</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <p className="text-xs text-zinc-400">{selectedRun.objective}</p>
            {selectedRun.node_results?.map((n, i) => (
              <div key={i} className="flex items-center gap-2 p-1.5 rounded bg-zinc-800/40 border border-white/5 text-[10px]">
                {n.status === "completed" ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : <XCircle className="w-3 h-3 text-red-400" />}
                <span className="text-zinc-500 w-12">{n.node_id}</span>
                <span className="text-zinc-300 flex-1 truncate">{n.task}</span>
                <span className="text-zinc-500">{n.provider}:{n.model?.split("/").pop()}</span>
                <span className="text-zinc-500">{n.latency_ms}ms</span>
              </div>
            ))}
            {selectedRun.final_report && (
              <details className="mt-2">
                <summary className="text-[10px] text-cyan-400 cursor-pointer">View Report</summary>
                <pre className="text-[10px] text-zinc-400 whitespace-pre-wrap mt-1 p-2 bg-zinc-800/40 rounded max-h-48 overflow-y-auto">{selectedRun.final_report}</pre>
              </details>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
