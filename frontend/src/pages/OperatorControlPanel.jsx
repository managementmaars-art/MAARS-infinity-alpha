import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Shield, AlertTriangle, CheckCircle, Clock, Play, RotateCcw,
  Activity, Users, Zap, Lock, Eye, FileCheck, Beaker, ChevronRight,
  XCircle, AlertCircle, Loader2
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_COLORS = {
  pass: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  fail: "text-red-400 bg-red-500/10 border-red-500/20",
  warn: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

export default function OperatorControlPanel() {
  const [dashboard, setDashboard] = useState(null);
  const [scenarios, setScenarios] = useState({});
  const [testResults, setTestResults] = useState(null);
  const [runningTest, setRunningTest] = useState(null);
  const [testHistory, setTestHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchDashboard = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [d, s, h] = await Promise.all([
      f("/api/infinity/operator/dashboard"),
      f("/api/infinity/test-harness/scenarios"),
      f("/api/infinity/test-harness/history?limit=5"),
    ]);
    if (d) setDashboard(d);
    if (s) setScenarios(s);
    if (Array.isArray(h)) setTestHistory(h);
  }, [token]);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  const runScenario = async (id) => {
    setRunningTest(id);
    setTestResults(null);
    const res = await fetch(`${API}/api/infinity/test-harness/run/${id}`, { method: "POST", headers });
    const data = await res.json();
    setTestResults(data);
    setRunningTest(null);
    fetchDashboard();
  };

  const runAll = async () => {
    setRunningTest("ALL");
    setTestResults(null);
    const res = await fetch(`${API}/api/infinity/test-harness/run-all`, { method: "POST", headers });
    const data = await res.json();
    setTestResults(data);
    setRunningTest(null);
    fetchDashboard();
  };

  const decideApproval = async (taskId, approved) => {
    await fetch(`${API}/api/infinity/governance/approvals/decide`, {
      method: "POST", headers,
      body: JSON.stringify({ task_id: taskId, approved, approver: "operator", notes: "" }),
    });
    fetchDashboard();
  };

  const tabs = [
    { id: "overview", label: "Overview", icon: Eye },
    { id: "approvals", label: "Approvals", icon: FileCheck },
    { id: "harness", label: "Test Harness", icon: Beaker },
    { id: "autonomy", label: "Autonomy", icon: Lock },
  ];

  return (
    <div className="space-y-6" data-testid="operator-control-panel">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <Shield className="w-6 h-6 text-cyan-400" /> Operator Control Panel
          </h1>
          <p className="text-sm text-zinc-400">System oversight, approvals, test harness, and autonomy management</p>
        </div>
        <Badge className={dashboard?.system_health === "operational" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : "bg-red-500/20 text-red-400 border-red-500/30"} data-testid="system-health-badge">
          {dashboard?.system_health === "operational" ? "All Systems Operational" : "System Degraded"}
        </Badge>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-zinc-900/40 border border-white/5 rounded-lg p-1" data-testid="tab-nav">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === t.id ? "bg-cyan-500/20 text-cyan-400" : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"}`}
            data-testid={`tab-${t.id}`}
          >
            <t.icon className="w-3.5 h-3.5" /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && dashboard && (
        <div className="space-y-4" data-testid="overview-tab">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: "Pending Approvals", value: dashboard.pending_approvals, icon: FileCheck, color: "bg-amber-500/20", iconColor: "text-amber-400" },
              { label: "Open Incidents", value: dashboard.open_incidents, icon: AlertTriangle, color: "bg-red-500/20", iconColor: "text-red-400" },
              { label: "Open Escalations", value: dashboard.open_escalations, icon: AlertCircle, color: "bg-orange-500/20", iconColor: "text-orange-400" },
              { label: "Circuit Breakers Tripped", value: dashboard.circuit_breakers?.tripped || 0, icon: Zap, color: "bg-violet-500/20", iconColor: "text-violet-400" },
            ].map((s, i) => (
              <Card key={i} className="bg-zinc-900/50 border-white/5" data-testid={`stat-${s.label.toLowerCase().replace(/\s/g, '-')}`}>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg ${s.color} flex items-center justify-center`}>
                    <s.icon className={`w-4 h-4 ${s.iconColor}`} />
                  </div>
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wide">{s.label}</p>
                    <p className="text-lg font-bold text-white">{s.value}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Recent Incidents */}
          {dashboard.incidents?.length > 0 && (
            <Card className="bg-zinc-900/50 border-white/5">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-red-400" /> Open Incidents</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {dashboard.incidents.map((inc, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 border border-white/5">
                    <div className="flex items-center gap-2">
                      <Badge className={inc.severity === "high" ? "bg-red-500/20 text-red-400" : inc.severity === "medium" ? "bg-amber-500/20 text-amber-400" : "bg-zinc-500/20 text-zinc-400"}>{inc.severity}</Badge>
                      <span className="text-xs text-zinc-300">{inc.type}: {inc.description?.slice(0, 80)}</span>
                    </div>
                    <span className="text-[10px] text-zinc-500">{inc.detected_at?.slice(0, 16)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Low Trust Entities */}
          {dashboard.low_trust_entities?.length > 0 && (
            <Card className="bg-zinc-900/50 border-white/5">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Users className="w-4 h-4 text-amber-400" /> Low Trust Entities</CardTitle></CardHeader>
              <CardContent className="space-y-1">
                {dashboard.low_trust_entities.map((e, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 text-xs">
                    <span className="text-zinc-300">{e.entity_id}</span>
                    <Badge className="bg-red-500/20 text-red-400">{e.score?.toFixed(1)}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Approvals Tab */}
      {activeTab === "approvals" && (
        <div className="space-y-4" data-testid="approvals-tab">
          <Card className="bg-zinc-900/50 border-white/5">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><FileCheck className="w-4 h-4 text-amber-400" /> Pending Approvals ({dashboard?.pending_approvals || 0})</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {dashboard?.approvals?.length > 0 ? dashboard.approvals.map((a, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-zinc-800/40 border border-white/5" data-testid={`approval-${a.task_id}`}>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={a.urgency === "high" ? "bg-red-500/20 text-red-400" : "bg-zinc-500/20 text-zinc-400"}>{a.urgency}</Badge>
                      <span className="text-xs text-zinc-300 font-medium">{a.action}</span>
                    </div>
                    <p className="text-[11px] text-zinc-500 truncate">{a.reason}</p>
                    <p className="text-[10px] text-zinc-600">Task: {a.task_id} | Graph: {a.graph_id}</p>
                  </div>
                  <div className="flex gap-1.5 shrink-0 ml-3">
                    <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 h-7 px-2 text-[11px]" onClick={() => decideApproval(a.task_id, true)} data-testid={`approve-${a.task_id}`}>
                      <CheckCircle className="w-3 h-3 mr-1" /> Approve
                    </Button>
                    <Button size="sm" variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10 h-7 px-2 text-[11px]" onClick={() => decideApproval(a.task_id, false)} data-testid={`deny-${a.task_id}`}>
                      <XCircle className="w-3 h-3 mr-1" /> Deny
                    </Button>
                  </div>
                </div>
              )) : (
                <p className="text-xs text-zinc-500 text-center py-4">No pending approvals</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Test Harness Tab */}
      {activeTab === "harness" && (
        <div className="space-y-4" data-testid="harness-tab">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Validation Scenarios</h2>
            <Button onClick={runAll} disabled={!!runningTest} className="bg-cyan-600 hover:bg-cyan-700 h-8 text-xs" data-testid="run-all-btn">
              {runningTest === "ALL" ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Play className="w-3.5 h-3.5 mr-1" />}
              Run All Scenarios
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(scenarios).map(([id, s]) => (
              <Card key={id} className="bg-zinc-900/50 border-white/5" data-testid={`scenario-card-${id}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">Scenario {id}</Badge>
                    <Button size="sm" variant="outline" className="h-7 px-2 text-[11px] border-white/10" onClick={() => runScenario(id)} disabled={!!runningTest} data-testid={`run-scenario-${id}`}>
                      {runningTest === id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
                    </Button>
                  </div>
                  <h3 className="text-xs font-semibold text-white mb-1">{s.name}</h3>
                  <p className="text-[10px] text-zinc-500">{s.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Test Results */}
          {testResults && (
            <Card className={`border ${testResults.overall_status === "pass" ? "border-emerald-500/20" : "border-red-500/20"} bg-zinc-900/50`} data-testid="test-results">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-white flex items-center gap-2">
                    {testResults.overall_status === "pass" ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                    {testResults.scenarios ? "Full Suite Results" : `Scenario ${testResults.scenario_id} Results`}
                  </CardTitle>
                  <Badge className={testResults.overall_status === "pass" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}>
                    {testResults.overall_status?.toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {(testResults.scenarios || [testResults]).map((sc, si) => (
                  <div key={si} className="space-y-1.5">
                    {testResults.scenarios && (
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className="bg-zinc-800 text-zinc-300 text-[10px]">{sc.scenario_id}</Badge>
                        <span className="text-xs text-zinc-400">{sc.scenario_name}</span>
                        <Badge className={sc.overall_status === "pass" ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>{sc.summary?.passed}/{sc.summary?.total}</Badge>
                      </div>
                    )}
                    {sc.steps?.map((step, i) => (
                      <div key={i} className={`flex items-center gap-2 px-3 py-1.5 rounded border text-[11px] ${STATUS_COLORS[step.status] || STATUS_COLORS.warn}`} data-testid={`step-${sc.scenario_id}-${step.step}`}>
                        {step.status === "pass" ? <CheckCircle className="w-3 h-3 shrink-0" /> : step.status === "fail" ? <XCircle className="w-3 h-3 shrink-0" /> : <AlertCircle className="w-3 h-3 shrink-0" />}
                        <span className="font-medium">{step.step}</span>
                        <ChevronRight className="w-3 h-3 text-zinc-600" />
                        <span className="text-zinc-400 truncate">{step.detail}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Test History */}
          {testHistory.length > 0 && (
            <Card className="bg-zinc-900/50 border-white/5">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Clock className="w-4 h-4 text-zinc-400" /> Recent Test Runs</CardTitle></CardHeader>
              <CardContent className="space-y-1.5">
                {testHistory.map((h, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/40 text-xs">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-zinc-700/50 text-zinc-400 text-[10px]">{h.scenario_id}</Badge>
                      <span className="text-zinc-300">{h.scenario_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-500">{h.summary?.passed}/{h.summary?.total}</span>
                      <Badge className={h.overall_status === "pass" ? "bg-emerald-500/15 text-emerald-400 text-[10px]" : "bg-red-500/15 text-red-400 text-[10px]"}>{h.overall_status}</Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Autonomy Tab */}
      {activeTab === "autonomy" && dashboard && (
        <div className="space-y-4" data-testid="autonomy-tab">
          <Card className="bg-zinc-900/50 border-white/5">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Lock className="w-4 h-4 text-violet-400" /> Autonomy Tiers</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(dashboard.tiers || {}).map(([tier, info]) => (
                <div key={tier} className="flex items-center justify-between p-3 rounded-lg bg-zinc-800/40 border border-white/5" data-testid={`tier-${tier}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-violet-500/15 flex items-center justify-center text-violet-400 text-xs font-bold">T{tier}</div>
                    <div>
                      <p className="text-xs font-medium text-white">{info.name}</p>
                      <p className="text-[10px] text-zinc-500">Max spend: ${info.max_spend} | Approval: {info.requires_approval ? "Required" : "Auto"}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 max-w-xs">
                    {info.allowed_actions?.slice(0, 4).map((a, i) => (
                      <Badge key={i} variant="outline" className="text-[9px] text-zinc-500 border-zinc-700">{a}</Badge>
                    ))}
                    {info.allowed_actions?.length > 4 && <Badge variant="outline" className="text-[9px] text-zinc-500 border-zinc-700">+{info.allowed_actions.length - 4}</Badge>}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Agent Workload */}
          <Card className="bg-zinc-900/50 border-white/5">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-white flex items-center gap-2"><Users className="w-4 h-4 text-emerald-400" /> Agent Workload by Network</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {dashboard.agent_workload?.slice(0, 12).map((w, i) => (
                  <div key={i} className="p-2 rounded bg-zinc-800/40 border border-white/5 text-center" data-testid={`workload-${w.network}`}>
                    <p className="text-[10px] text-zinc-500 truncate">{w.network?.replace(/_/g, " ")}</p>
                    <p className="text-sm font-bold text-white">{w.busy}/{w.total}</p>
                    <div className="mt-1 h-1 bg-zinc-700/50 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500/60 rounded-full" style={{ width: `${w.total > 0 ? (w.busy / w.total) * 100 : 0}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
