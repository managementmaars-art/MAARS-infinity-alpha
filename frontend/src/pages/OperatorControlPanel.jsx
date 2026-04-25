import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Shield, AlertTriangle, CheckCircle, Clock, Play,
  Activity, Users, Zap, Lock, Eye, FileCheck, Beaker, ChevronRight,
  XCircle, AlertCircle
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  cyan: "#22d3ee",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  violet: "#a78bfa",
  indigo: "#818cf8",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const STEP_STATUS = {
  pass: { color: T.green, bg: "rgba(52,211,153,.1)", border: "rgba(52,211,153,.2)" },
  fail: { color: T.red, bg: "rgba(239,68,68,.1)", border: "rgba(239,68,68,.2)" },
  warn: { color: T.amber, bg: "rgba(245,158,11,.1)", border: "rgba(245,158,11,.2)" },
};

const SEV_COLOR = { high: T.red, medium: T.amber, low: T.zinc };

export default function OperatorControlPanel() {
  const [dashboard, setDashboard] = useState(null);
  const [scenarios, setScenarios] = useState({});
  const [testResults, setTestResults] = useState(null);
  const [runningTest, setRunningTest] = useState(null);
  const [testHistory, setTestHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const token = localStorage.getItem("token");
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

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
  }, [headers]);

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

  const Spinner = () => <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22, animation: "fadeUp .4s ease" }} data-testid="operator-control-panel">
      <style>{STYLES}</style>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 24, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4, display: "flex", alignItems: "center", gap: 10 }}>
            <Shield size={22} style={{ color: T.cyan }} /> Operator Control Panel
          </h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>System oversight, approvals, test harness, and autonomy management</p>
        </div>
        <span style={{
          fontSize: 11, fontWeight: 700, padding: "4px 12px", borderRadius: 20,
          background: dashboard?.system_health === "operational" ? "rgba(52,211,153,.15)" : "rgba(239,68,68,.15)",
          color: dashboard?.system_health === "operational" ? T.green : T.red,
          border: `1px solid ${dashboard?.system_health === "operational" ? "rgba(52,211,153,.3)" : "rgba(239,68,68,.3)"}`,
        }} data-testid="system-health-badge">
          {dashboard?.system_health === "operational" ? "All Systems Operational" : "System Degraded"}
        </span>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: 4, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}`, borderRadius: 10, padding: 4 }} data-testid="tab-nav">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} data-testid={`tab-${t.id}`}
            style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 7, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all .2s",
              background: activeTab === t.id ? "rgba(34,211,238,.15)" : "transparent",
              color: activeTab === t.id ? T.cyan : T.zinc }}>
            <t.icon size={13} /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && dashboard && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }} data-testid="overview-tab">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
            {[
              { label: "Pending Approvals", value: dashboard.pending_approvals, icon: FileCheck, color: T.amber, bg: "rgba(245,158,11,.15)" },
              { label: "Open Incidents", value: dashboard.open_incidents, icon: AlertTriangle, color: T.red, bg: "rgba(239,68,68,.15)" },
              { label: "Open Escalations", value: dashboard.open_escalations, icon: AlertCircle, color: "#f97316", bg: "rgba(249,115,22,.15)" },
              { label: "Circuit Breakers Tripped", value: dashboard.circuit_breakers?.tripped || 0, icon: Zap, color: T.violet, bg: "rgba(167,139,250,.15)" },
            ].map((s, i) => (
              <div key={i} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", display: "flex", alignItems: "center", gap: 12 }} data-testid={`stat-${s.label.toLowerCase().replace(/\s/g, '-')}`}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: s.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <s.icon size={16} style={{ color: s.color }} />
                </div>
                <div>
                  <p style={{ fontSize: 9, color: T.zinc, textTransform: "uppercase", letterSpacing: "0.08em", margin: 0 }}>{s.label}</p>
                  <p style={{ fontSize: 20, fontWeight: 700, color: "#fff", margin: 0 }}>{s.value}</p>
                </div>
              </div>
            ))}
          </div>

          {dashboard.incidents?.length > 0 && (
            <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
                <AlertTriangle size={13} style={{ color: T.red }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Open Incidents</span>
              </div>
              <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 6 }}>
                {dashboard.incidents.map((inc, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 12px", borderRadius: 8, background: "rgba(255,255,255,.025)", border: `1px solid ${T.border}` }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: `${SEV_COLOR[inc.severity] || T.zinc}20`, color: SEV_COLOR[inc.severity] || T.zinc }}>{inc.severity}</span>
                      <span style={{ fontSize: 11, color: "#d4d4d8" }}>{inc.type}: {inc.description?.slice(0, 80)}</span>
                    </div>
                    <span style={{ fontSize: 10, color: T.zinc }}>{inc.detected_at?.slice(0, 16)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {dashboard.low_trust_entities?.length > 0 && (
            <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
                <Users size={13} style={{ color: T.amber }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Low Trust Entities</span>
              </div>
              <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 4 }}>
                {dashboard.low_trust_entities.map((e, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "7px 10px", borderRadius: 7, background: "rgba(255,255,255,.025)", fontSize: 11 }}>
                    <span style={{ color: "#d4d4d8" }}>{e.entity_id}</span>
                    <span style={{ padding: "2px 8px", borderRadius: 20, background: "rgba(239,68,68,.15)", color: T.red, fontWeight: 700, fontSize: 10 }}>{e.score?.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Approvals Tab */}
      {activeTab === "approvals" && (
        <div data-testid="approvals-tab">
          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
            <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              <FileCheck size={13} style={{ color: T.amber }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Pending Approvals ({dashboard?.pending_approvals || 0})</span>
            </div>
            <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 8 }}>
              {dashboard?.approvals?.length > 0 ? dashboard.approvals.map((a, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 14px", borderRadius: 10, background: "rgba(255,255,255,.025)", border: `1px solid ${T.border}` }} data-testid={`approval-${a.task_id}`}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: a.urgency === "high" ? "rgba(239,68,68,.15)" : "rgba(113,113,122,.15)", color: a.urgency === "high" ? T.red : T.zinc }}>{a.urgency}</span>
                      <span style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>{a.action}</span>
                    </div>
                    <p style={{ fontSize: 11, color: T.zinc, margin: "0 0 3px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.reason}</p>
                    <p style={{ fontSize: 10, color: "rgba(113,113,122,.6)", margin: 0 }}>Task: {a.task_id} | Graph: {a.graph_id}</p>
                  </div>
                  <div style={{ display: "flex", gap: 7, flexShrink: 0, marginLeft: 12 }}>
                    <button onClick={() => decideApproval(a.task_id, true)} data-testid={`approve-${a.task_id}`}
                      style={{ display: "inline-flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 7, border: "none", background: "rgba(52,211,153,.2)", color: T.green, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                      <CheckCircle size={11} /> Approve
                    </button>
                    <button onClick={() => decideApproval(a.task_id, false)} data-testid={`deny-${a.task_id}`}
                      style={{ display: "inline-flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 7, border: `1px solid rgba(239,68,68,.3)`, background: "rgba(239,68,68,.08)", color: T.red, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                      <XCircle size={11} /> Deny
                    </button>
                  </div>
                </div>
              )) : (
                <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "20px 0" }}>No pending approvals</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Test Harness Tab */}
      {activeTab === "harness" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }} data-testid="harness-tab">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Validation Scenarios</span>
            <button onClick={runAll} disabled={!!runningTest} data-testid="run-all-btn"
              style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "7px 16px", borderRadius: 9, border: "none", background: runningTest ? "rgba(34,211,238,.2)" : "rgba(34,211,238,.85)", color: "#000", fontSize: 12, fontWeight: 700, cursor: runningTest ? "not-allowed" : "pointer" }}>
              {runningTest === "ALL" ? <Spinner /> : <Play size={13} />}
              Run All Scenarios
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
            {Object.entries(scenarios).map(([id, s]) => (
              <div key={id} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }} data-testid={`scenario-card-${id}`}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                  <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 20, background: "rgba(34,211,238,.15)", color: T.cyan }}>Scenario {id}</span>
                  <button onClick={() => runScenario(id)} disabled={!!runningTest} data-testid={`run-scenario-${id}`}
                    style={{ width: 26, height: 26, borderRadius: 6, border: `1px solid ${T.border}`, background: "transparent", cursor: runningTest ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: T.zinc }}>
                    {runningTest === id ? <Spinner /> : <Play size={11} />}
                  </button>
                </div>
                <h3 style={{ fontSize: 12, fontWeight: 600, color: "#fff", margin: "0 0 4px" }}>{s.name}</h3>
                <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{s.description}</p>
              </div>
            ))}
          </div>

          {testResults && (
            <div style={{ background: T.glass, border: `1px solid ${testResults.overall_status === "pass" ? "rgba(52,211,153,.25)" : "rgba(239,68,68,.25)"}`, borderRadius: 12, overflow: "hidden" }} data-testid="test-results">
              <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  {testResults.overall_status === "pass" ? <CheckCircle size={14} style={{ color: T.green }} /> : <XCircle size={14} style={{ color: T.red }} />}
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{testResults.scenarios ? "Full Suite Results" : `Scenario ${testResults.scenario_id} Results`}</span>
                </div>
                <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 20, background: testResults.overall_status === "pass" ? "rgba(52,211,153,.15)" : "rgba(239,68,68,.15)", color: testResults.overall_status === "pass" ? T.green : T.red }}>
                  {testResults.overall_status?.toUpperCase()}
                </span>
              </div>
              <div style={{ padding: "12px 14px", display: "flex", flexDirection: "column", gap: 14 }}>
                {(testResults.scenarios || [testResults]).map((sc, si) => (
                  <div key={si} style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                    {testResults.scenarios && (
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 6, background: "rgba(255,255,255,.07)", color: T.zinc }}>{sc.scenario_id}</span>
                        <span style={{ fontSize: 11, color: "#d4d4d8" }}>{sc.scenario_name}</span>
                        <span style={{ fontSize: 10, fontWeight: 700, padding: "1px 7px", borderRadius: 20, background: sc.overall_status === "pass" ? "rgba(52,211,153,.1)" : "rgba(239,68,68,.1)", color: sc.overall_status === "pass" ? T.green : T.red }}>{sc.summary?.passed}/{sc.summary?.total}</span>
                      </div>
                    )}
                    {sc.steps?.map((step, i) => {
                      const sm = STEP_STATUS[step.status] || STEP_STATUS.warn;
                      return (
                        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 7, background: sm.bg, border: `1px solid ${sm.border}`, color: sm.color, fontSize: 11 }} data-testid={`step-${sc.scenario_id}-${step.step}`}>
                          {step.status === "pass" ? <CheckCircle size={11} style={{ flexShrink: 0 }} /> : step.status === "fail" ? <XCircle size={11} style={{ flexShrink: 0 }} /> : <AlertCircle size={11} style={{ flexShrink: 0 }} />}
                          <span style={{ fontWeight: 600 }}>{step.step}</span>
                          <ChevronRight size={11} style={{ color: T.zinc }} />
                          <span style={{ color: "#a1a1aa", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{step.detail}</span>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          )}

          {testHistory.length > 0 && (
            <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
                <Clock size={13} style={{ color: T.zinc }} />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Recent Test Runs</span>
              </div>
              <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 5 }}>
                {testHistory.map((h, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "7px 10px", borderRadius: 7, background: "rgba(255,255,255,.025)", fontSize: 11 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 10, padding: "1px 7px", borderRadius: 5, background: "rgba(255,255,255,.06)", color: T.zinc }}>{h.scenario_id}</span>
                      <span style={{ color: "#d4d4d8" }}>{h.scenario_name}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ color: T.zinc }}>{h.summary?.passed}/{h.summary?.total}</span>
                      <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: h.overall_status === "pass" ? "rgba(52,211,153,.1)" : "rgba(239,68,68,.1)", color: h.overall_status === "pass" ? T.green : T.red }}>{h.overall_status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Autonomy Tab */}
      {activeTab === "autonomy" && dashboard && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }} data-testid="autonomy-tab">
          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
            <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              <Lock size={13} style={{ color: T.violet }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Autonomy Tiers</span>
            </div>
            <div style={{ padding: "10px 14px", display: "flex", flexDirection: "column", gap: 8 }}>
              {Object.entries(dashboard.tiers || {}).map(([tier, info]) => (
                <div key={tier} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 14px", borderRadius: 10, background: "rgba(255,255,255,.025)", border: `1px solid ${T.border}` }} data-testid={`tier-${tier}`}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 9, background: "rgba(167,139,250,.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: T.violet }}>T{tier}</div>
                    <div>
                      <p style={{ fontSize: 12, fontWeight: 600, color: "#fff", margin: 0 }}>{info.name}</p>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>Max spend: ${info.max_spend} | Approval: {info.requires_approval ? "Required" : "Auto"}</p>
                    </div>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 5, maxWidth: 220 }}>
                    {info.allowed_actions?.slice(0, 4).map((a, i) => (
                      <span key={i} style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid ${T.border}`, color: T.zinc }}>{a}</span>
                    ))}
                    {info.allowed_actions?.length > 4 && <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid ${T.border}`, color: T.zinc }}>+{info.allowed_actions.length - 4}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
            <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
              <Users size={13} style={{ color: T.green }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Agent Workload by Network</span>
            </div>
            <div style={{ padding: "12px 14px", display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>
              {dashboard.agent_workload?.slice(0, 12).map((w, i) => (
                <div key={i} style={{ padding: "10px 12px", borderRadius: 9, background: "rgba(255,255,255,.025)", border: `1px solid ${T.border}`, textAlign: "center" }} data-testid={`workload-${w.network}`}>
                  <p style={{ fontSize: 9, color: T.zinc, margin: "0 0 4px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{w.network?.replace(/_/g, " ")}</p>
                  <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: "0 0 6px" }}>{w.busy}/{w.total}</p>
                  <div style={{ height: 3, background: "rgba(255,255,255,.07)", borderRadius: 99, overflow: "hidden" }}>
                    <div style={{ height: "100%", background: "rgba(52,211,153,.6)", borderRadius: 99, width: `${w.total > 0 ? (w.busy / w.total) * 100 : 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
