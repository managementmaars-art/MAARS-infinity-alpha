import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useAuth } from "../App";
import { Play, Plus, Trash2, Clock, CheckCircle, AlertCircle, ChevronRight, ChevronDown, FileText, Zap, ArrowLeft, Download, CalendarClock } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} } @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`;

const formInput = {
  background: "rgba(255,255,255,.04)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  padding: "8px 12px",
  color: "#fff",
  fontSize: 13,
  outline: "none",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
  transition: "border-color .2s",
};

const btnPrimary = {
  background: "linear-gradient(135deg,#6366f1,#7c3aed)",
  border: "none",
  borderRadius: 8,
  color: "#fff",
  fontSize: 12,
  fontWeight: 600,
  padding: "6px 14px",
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  gap: 5,
  fontFamily: "inherit",
};

const btnGhost = {
  background: "transparent",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  color: "#a1a1aa",
  fontSize: 12,
  fontWeight: 500,
  padding: "6px 12px",
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  gap: 5,
  fontFamily: "inherit",
};

const btnGreen = {
  ...btnPrimary,
  background: "linear-gradient(135deg,#059669,#10b981)",
};

const btnRed = {
  ...btnGhost,
  color: "#f87171",
  border: "none",
  padding: "4px 8px",
};

export default function CampaignBuilder() {
  const { token } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [view, setView] = useState("list"); // list, detail, create
  const [contextInput, setContextInput] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduleData, setScheduleData] = useState({ frequency: "weekly", day_of_week: 1, hour: 9 });
  const pollTimerRef = useRef(null);

  const h = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const fetchAll = useCallback(async () => {
    try {
      const [tRes, cRes] = await Promise.all([
        fetch(`${API}/api/kernel/campaign-templates`, { headers: h }),
        fetch(`${API}/api/kernel/campaigns`, { headers: h }),
      ]);
      if (tRes.ok) setTemplates(await tRes.json());
      if (cRes.ok) setCampaigns(await cRes.json());
    } catch {}
    setLoading(false);
  }, [h]);

  useEffect(() => {
    fetchAll();
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [fetchAll]);

  const createCampaign = async () => {
    if (!selectedTemplate) return;
    const res = await fetch(`${API}/api/kernel/campaigns`, {
      method: "POST", headers: h,
      body: JSON.stringify({ template_id: selectedTemplate.template_id, context: contextInput }),
    });
    if (res.ok) {
      const camp = await res.json();
      setCampaigns(prev => [camp, ...prev]);
      setSelected(camp);
      setView("detail");
      setContextInput("");
      setSelectedTemplate(null);
    }
  };

  const runCampaign = async (campId) => {
    const res = await fetch(`${API}/api/kernel/campaigns/${campId}/run`, { method: "POST", headers: h });
    if (res.ok) {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      const interval = setInterval(async () => {
        const r = await fetch(`${API}/api/kernel/campaigns/${campId}`, { headers: h });
        if (r.ok) {
          const data = await r.json();
          setSelected(data);
          setCampaigns(prev => prev.map(c => c.campaign_id === campId ? data : c));
          if (data.status === "completed" || data.status === "failed") {
            clearInterval(interval);
            pollTimerRef.current = null;
          }
        }
      }, 1500);
      pollTimerRef.current = interval;
      setSelected(prev => prev ? { ...prev, status: "running" } : prev);
    }
  };

  const deleteCampaign = async (campId) => {
    await fetch(`${API}/api/kernel/campaigns/${campId}`, { method: "DELETE", headers: h });
    setCampaigns(prev => prev.filter(c => c.campaign_id !== campId));
    if (selected?.campaign_id === campId) { setSelected(null); setView("list"); }
  };

  const downloadReport = (campId) => {
    window.open(`${API}/api/kernel/campaigns/${campId}/report?token=${token}`, "_blank");
  };

  const saveCampaignSchedule = async (campId) => {
    await fetch(`${API}/api/kernel/campaigns/${campId}/schedule`, {
      method: "POST", headers: h,
      body: JSON.stringify(scheduleData),
    });
    setShowSchedule(false);
    const res = await fetch(`${API}/api/kernel/campaigns/${campId}`, { headers: h });
    if (res.ok) {
      const data = await res.json();
      setSelected(data);
      setCampaigns(prev => prev.map(c => c.campaign_id === campId ? data : c));
    }
  };

  const removeSchedule = async (campId) => {
    await fetch(`${API}/api/kernel/campaigns/${campId}/schedule`, { method: "DELETE", headers: h });
    const res = await fetch(`${API}/api/kernel/campaigns/${campId}`, { headers: h });
    if (res.ok) {
      const data = await res.json();
      setSelected(data);
      setCampaigns(prev => prev.map(c => c.campaign_id === campId ? data : c));
    }
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: "2px solid #6366f1", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
    </div>
  );

  // Detail view
  if (view === "detail" && selected) {
    const steps = selected.steps || [];
    const completedSteps = steps.filter(s => s.status === "completed").length;
    const isRunning = selected.status === "running";
    return (
      <div style={{ maxWidth: 896, margin: "0 auto", padding: 24, display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="campaign-detail">
        <style>{STYLES}</style>
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <button style={btnGhost} onClick={() => { setView("list"); setSelected(null); }} data-testid="campaign-back">
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>{selected.name}</h2>
            <p style={{ fontSize: 11, color: "#52525b", margin: "2px 0 0" }}>{selected.description} &middot; {selected.category}</p>
          </div>
          <StatusBadge status={selected.status} />
          {selected.status === "completed" && (
            <button style={btnGhost} onClick={() => downloadReport(selected.campaign_id)} data-testid="campaign-download-btn">
              <Download style={{ width: 14, height: 14 }} /> PDF Report
            </button>
          )}
          <button style={btnGhost} onClick={() => setShowSchedule(!showSchedule)} data-testid="campaign-schedule-btn">
            <CalendarClock style={{ width: 14, height: 14 }} /> Schedule
          </button>
          {(selected.status === "draft" || selected.status === "completed" || selected.status === "failed") && (
            <button style={btnGreen} onClick={() => runCampaign(selected.campaign_id)} data-testid="campaign-run-btn">
              <Play style={{ width: 14, height: 14 }} /> {selected.status === "draft" ? "Run Campaign" : "Re-run"}
            </button>
          )}
          {isRunning && (
            <span style={{ fontSize: 11, color: T.amber, display: "flex", alignItems: "center", gap: 5, animation: "pulse 1.5s ease-in-out infinite" }}>
              <Clock style={{ width: 14, height: 14 }} /> Running... {completedSteps}/{steps.length}
            </span>
          )}
        </div>

        {selected.context && (
          <div style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 10, padding: 16 }}>
            <p style={{ fontSize: 10, fontWeight: 600, color: "#52525b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 4 }}>Campaign Context</p>
            <p style={{ fontSize: 13, color: "#d4d4d8", margin: 0 }}>{selected.context}</p>
          </div>
        )}

        {/* Schedule Panel */}
        {showSchedule && (
          <div style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(99,102,241,0.1)", borderRadius: 10, padding: 16 }} data-testid="schedule-panel">
            <p style={{ fontSize: 11, fontWeight: 600, color: T.indigo, marginBottom: 10 }}>Auto-Schedule</p>
            {selected.schedule?.enabled ? (
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <p style={{ fontSize: 11, color: "#d4d4d8", flex: 1, margin: 0 }}>
                  Scheduled: <span style={{ color: "#fff", fontWeight: 600 }}>{selected.schedule.frequency}</span> at {String(selected.schedule.hour).padStart(2, "0")}:{String(selected.schedule.minute || 0).padStart(2, "0")} UTC
                </p>
                <button style={btnRed} onClick={() => removeSchedule(selected.campaign_id)} data-testid="remove-schedule-btn">Remove Schedule</button>
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                <select
                  value={scheduleData.frequency}
                  onChange={e => setScheduleData(p => ({ ...p, frequency: e.target.value }))}
                  style={{ ...formInput, width: "auto", fontSize: 11, padding: "5px 10px", cursor: "pointer" }}
                  data-testid="schedule-frequency"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
                {scheduleData.frequency === "weekly" && (
                  <select
                    value={scheduleData.day_of_week}
                    onChange={e => setScheduleData(p => ({ ...p, day_of_week: +e.target.value }))}
                    style={{ ...formInput, width: "auto", fontSize: 11, padding: "5px 10px", cursor: "pointer" }}
                  >
                    {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d, i) => <option key={i} value={i}>{d}</option>)}
                  </select>
                )}
                <input
                  type="number" min={0} max={23}
                  value={scheduleData.hour}
                  onChange={e => setScheduleData(p => ({ ...p, hour: +e.target.value }))}
                  style={{ ...formInput, width: 56, fontSize: 11, padding: "5px 8px" }}
                  placeholder="Hour"
                />
                <span style={{ fontSize: 10, color: "#52525b" }}>UTC</span>
                <button style={btnPrimary} onClick={() => saveCampaignSchedule(selected.campaign_id)} data-testid="save-schedule-btn">Save</button>
              </div>
            )}
          </div>
        )}

        {/* Progress bar */}
        <div style={{ height: 6, background: "#27272a", borderRadius: 9999, overflow: "hidden" }}>
          <div style={{
            height: "100%",
            borderRadius: 9999,
            transition: "width 0.5s ease",
            width: `${steps.length > 0 ? (completedSteps / steps.length) * 100 : 0}%`,
            backgroundColor: selected.status === "failed" ? T.red : T.green,
          }} />
        </div>

        {/* Steps */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }} data-testid="campaign-steps">
          {steps.map((step, i) => (
            <StepCard key={i} step={step} index={i} isLast={i === steps.length - 1} />
          ))}
        </div>
      </div>
    );
  }

  // Create view
  if (view === "create") {
    return (
      <div style={{ maxWidth: 896, margin: "0 auto", padding: 24, display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="campaign-create">
        <style>{STYLES}</style>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button style={btnGhost} onClick={() => setView("list")} data-testid="campaign-create-back">
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>New Campaign</h2>
        </div>

        <p style={{ fontSize: 13, color: "#71717a", margin: 0 }}>Choose a template and provide context for your campaign.</p>

        {/* Template selection */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }} data-testid="template-grid">
          {templates.map(t => (
            <div
              key={t.template_id}
              style={{
                borderRadius: 12,
                border: selectedTemplate?.template_id === t.template_id ? "2px solid rgba(255,255,255,0.3)" : "2px solid rgba(255,255,255,0.05)",
                background: selectedTemplate?.template_id === t.template_id ? "rgba(255,255,255,0.04)" : "rgba(9,9,11,0.3)",
                padding: 16,
                cursor: "pointer",
                transition: "border-color .15s",
              }}
              onClick={() => setSelectedTemplate(t)}
              data-testid={`template-${t.template_id}`}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: t.color, flexShrink: 0 }} />
                <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>{t.name}</p>
              </div>
              <p style={{ fontSize: 11, color: "#52525b", margin: "0 0 8px" }}>{t.description}</p>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ fontSize: 10, padding: "2px 6px", borderRadius: 4, background: "#27272a", color: "#71717a" }}>{t.category}</span>
                <span style={{ fontSize: 10, color: "#3f3f46" }}>{t.steps.length} steps</span>
              </div>
            </div>
          ))}
        </div>

        {selectedTemplate && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 10, padding: 16 }}>
              <p style={{ fontSize: 10, fontWeight: 600, color: "#52525b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Steps Preview</p>
              {selectedTemplate.steps.map((s, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0" }}>
                  <span style={{ fontSize: 10, fontFamily: "monospace", color: "#3f3f46", width: 16 }}>{s.order}</span>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: selectedTemplate.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, color: "#d4d4d8" }}>{s.title}</span>
                  <span style={{ fontSize: 10, color: "#3f3f46" }}>— {s.agent_role}</span>
                </div>
              ))}
            </div>

            <div>
              <label style={{ fontSize: 11, fontWeight: 500, color: "#71717a", display: "block", marginBottom: 6 }}>Campaign Context (optional)</label>
              <textarea
                value={contextInput}
                onChange={e => setContextInput(e.target.value)}
                placeholder="Add specific context for this campaign, e.g., 'We are launching a new AI-powered CRM tool targeting small businesses in the US market...'"
                style={{ ...formInput, resize: "none", minHeight: 72 }}
                rows={3}
                data-testid="campaign-context-input"
              />
            </div>

            <button style={btnPrimary} onClick={createCampaign} data-testid="campaign-create-btn">
              <Zap style={{ width: 14, height: 14 }} /> Create Campaign
            </button>
          </div>
        )}
      </div>
    );
  }

  // List view
  return (
    <div style={{ maxWidth: 1024, margin: "0 auto", padding: 24, display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="campaign-list">
      <style>{STYLES}</style>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#fff", margin: 0 }}>Campaign Builder</h1>
          <p style={{ fontSize: 13, color: "#52525b", margin: "4px 0 0" }}>Multi-step automated workflows powered by AI agents</p>
        </div>
        <button style={btnPrimary} onClick={() => setView("create")} data-testid="new-campaign-btn">
          <Plus style={{ width: 14, height: 14 }} /> New Campaign
        </button>
      </div>

      {/* Templates quick access */}
      <div>
        <p style={{ fontSize: 11, fontWeight: 600, color: "#52525b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Quick Start Templates</p>
        <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 8 }}>
          {templates.map(t => (
            <button
              key={t.template_id}
              style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", borderRadius: 8, border: "1px solid rgba(255,255,255,0.05)", background: "rgba(9,9,11,0.3)", cursor: "pointer", fontFamily: "inherit", transition: "border-color .15s" }}
              onClick={() => { setSelectedTemplate(t); setView("create"); }}
              data-testid={`quick-template-${t.template_id}`}
            >
              <div style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: t.color }} />
              <span style={{ fontSize: 11, color: "#d4d4d8" }}>{t.name}</span>
              <span style={{ fontSize: 10, color: "#3f3f46" }}>{t.steps.length} steps</span>
            </button>
          ))}
        </div>
      </div>

      {/* Campaigns list */}
      <div>
        <p style={{ fontSize: 11, fontWeight: 600, color: "#52525b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Your Campaigns</p>
        {campaigns.length === 0 ? (
          <div style={{ textAlign: "center", padding: "48px 0", color: "#3f3f46" }}>
            <FileText style={{ width: 32, height: 32, margin: "0 auto 8px", opacity: 0.5, display: "block" }} />
            <p style={{ fontSize: 13, color: "#52525b" }}>No campaigns yet. Create one from a template above.</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }} data-testid="campaigns-list">
            {campaigns.map(c => (
              <div
                key={c.campaign_id}
                style={{ display: "flex", alignItems: "center", gap: 16, padding: "12px 16px", borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)", background: "rgba(9,9,11,0.3)", cursor: "pointer", transition: "border-color .15s" }}
                onClick={() => { setSelected(c); setView("detail"); }}
                data-testid={`campaign-item-${c.campaign_id}`}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.10)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.05)"}
              >
                <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: c.color || "#4fd1c5", flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: 13, fontWeight: 500, color: "#fff", margin: 0 }}>{c.name}</p>
                  <p style={{ fontSize: 10, color: "#52525b", margin: "2px 0 0" }}>{c.category} &middot; {(c.steps || []).length} steps</p>
                </div>
                <StatusBadge status={c.status} />
                <ChevronRight style={{ width: 16, height: 16, color: "#52525b", flexShrink: 0 }} />
                <button
                  style={{ ...btnRed, opacity: 0.6 }}
                  onClick={e => { e.stopPropagation(); deleteCampaign(c.campaign_id); }}
                  data-testid={`campaign-delete-${c.campaign_id}`}
                  onMouseEnter={e => e.currentTarget.style.opacity = "1"}
                  onMouseLeave={e => e.currentTarget.style.opacity = "0.6"}
                >
                  <Trash2 style={{ width: 14, height: 14 }} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    draft: { background: "rgba(39,39,42,0.8)", color: "#71717a" },
    running: { background: "rgba(245,158,11,0.1)", color: "#fbbf24" },
    completed: { background: "rgba(16,185,129,0.1)", color: "#34d399" },
    failed: { background: "rgba(239,68,68,0.1)", color: "#f87171" },
  };
  const s = map[status] || map.draft;
  return (
    <span
      style={{ fontSize: 10, fontWeight: 500, padding: "2px 9px", borderRadius: 20, background: s.background, color: s.color }}
      data-testid="campaign-status"
    >
      {status || "draft"}
    </span>
  );
}

function StepCard({ step, index, isLast }) {
  const [expanded, setExpanded] = useState(step.status === "completed" || step.status === "failed");

  const indicatorStyle = {
    width: 32, height: 32, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 11, fontWeight: 700,
    ...(step.status === "completed" ? { background: "rgba(16,185,129,0.2)", color: "#34d399" } :
        step.status === "running"   ? { background: "rgba(245,158,11,0.2)", color: "#fbbf24" } :
        step.status === "failed"    ? { background: "rgba(239,68,68,0.2)", color: "#f87171" } :
        { background: "#27272a", color: "#71717a" }),
  };

  return (
    <div style={{ position: "relative" }} data-testid={`step-card-${index}`}>
      {!isLast && <div style={{ position: "absolute", left: 15, top: 40, bottom: 0, width: 1, background: "#27272a" }} />}
      <div style={{ display: "flex", gap: 12, opacity: step.status === "running" ? undefined : 1, animation: step.status === "running" ? "pulse 1.5s ease-in-out infinite" : "none" }}>
        <div style={indicatorStyle}>
          {step.status === "completed" ? <CheckCircle style={{ width: 16, height: 16 }} /> :
           step.status === "running"   ? <Clock style={{ width: 16, height: 16, animation: "spin 1s linear infinite" }} /> :
           step.status === "failed"    ? <AlertCircle style={{ width: 16, height: 16 }} /> :
           index + 1}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }} onClick={() => setExpanded(!expanded)}>
            <p style={{ fontSize: 13, fontWeight: 500, color: "#fff", margin: 0 }}>{step.title}</p>
            <span style={{ fontSize: 10, color: "#52525b" }}>{step.agent_name} &middot; {step.agent_role}</span>
            <div style={{ flex: 1 }} />
            {step.output && (expanded
              ? <ChevronDown style={{ width: 14, height: 14, color: "#52525b" }} />
              : <ChevronRight style={{ width: 14, height: 14, color: "#52525b" }} />
            )}
          </div>

          <p style={{ fontSize: 10, color: "#3f3f46", marginTop: 2, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>{step.task}</p>

          {expanded && step.output && (
            <div
              style={{
                marginTop: 8, borderRadius: 8, padding: 12, fontSize: 11, lineHeight: 1.6, whiteSpace: "pre-wrap",
                ...(step.status === "failed"
                  ? { background: "rgba(127,29,29,0.3)", border: "1px solid rgba(239,68,68,0.1)", color: "#fca5a5" }
                  : { background: "rgba(39,39,42,0.5)", border: "1px solid rgba(255,255,255,0.05)", color: "#d4d4d8" }),
              }}
              data-testid={`step-output-${index}`}
            >
              {step.output}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
