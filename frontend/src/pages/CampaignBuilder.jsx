import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Play, Plus, Trash2, Clock, CheckCircle, AlertCircle, ChevronRight, ChevronDown, FileText, Zap, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

export default function CampaignBuilder() {
  const { token } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [view, setView] = useState("list"); // list, detail, create
  const [contextInput, setContextInput] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pollTimer, setPollTimer] = useState(null);

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchAll = async () => {
    try {
      const [tRes, cRes] = await Promise.all([
        fetch(`${API}/api/kernel/campaign-templates`, { headers: h }),
        fetch(`${API}/api/kernel/campaigns`, { headers: h }),
      ]);
      if (tRes.ok) setTemplates(await tRes.json());
      if (cRes.ok) setCampaigns(await cRes.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchAll(); return () => { if (pollTimer) clearInterval(pollTimer); }; }, [token]);

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
      // Start polling
      const interval = setInterval(async () => {
        const r = await fetch(`${API}/api/kernel/campaigns/${campId}`, { headers: h });
        if (r.ok) {
          const data = await r.json();
          setSelected(data);
          setCampaigns(prev => prev.map(c => c.campaign_id === campId ? data : c));
          if (data.status === "completed" || data.status === "failed") {
            clearInterval(interval);
            setPollTimer(null);
          }
        }
      }, 1500);
      setPollTimer(interval);
      // Update local state immediately
      setSelected(prev => prev ? { ...prev, status: "running" } : prev);
    }
  };

  const deleteCampaign = async (campId) => {
    await fetch(`${API}/api/kernel/campaigns/${campId}`, { method: "DELETE", headers: h });
    setCampaigns(prev => prev.filter(c => c.campaign_id !== campId));
    if (selected?.campaign_id === campId) { setSelected(null); setView("list"); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  // Detail view
  if (view === "detail" && selected) {
    const steps = selected.steps || [];
    const completedSteps = steps.filter(s => s.status === "completed").length;
    const isRunning = selected.status === "running";
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6" data-testid="campaign-detail">
        <div className="flex items-center gap-3">
          <Button size="sm" variant="ghost" className="h-7 text-zinc-400" onClick={() => { setView("list"); setSelected(null); }} data-testid="campaign-back">
            <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back
          </Button>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-white">{selected.name}</h2>
            <p className="text-xs text-zinc-500">{selected.description} &middot; {selected.category}</p>
          </div>
          <StatusBadge status={selected.status} />
          {(selected.status === "draft" || selected.status === "completed" || selected.status === "failed") && (
            <Button size="sm" className="h-8 text-xs bg-emerald-600 hover:bg-emerald-700" onClick={() => runCampaign(selected.campaign_id)}
              data-testid="campaign-run-btn">
              <Play className="w-3.5 h-3.5 mr-1" /> {selected.status === "draft" ? "Run Campaign" : "Re-run"}
            </Button>
          )}
          {isRunning && (
            <span className="text-xs text-amber-400 animate-pulse flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> Running... {completedSteps}/{steps.length}
            </span>
          )}
        </div>

        {selected.context && (
          <div className="bg-zinc-900/50 border border-white/5 rounded-lg p-4">
            <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1">Campaign Context</p>
            <p className="text-sm text-zinc-300">{selected.context}</p>
          </div>
        )}

        {/* Progress bar */}
        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full transition-all duration-500" style={{
            width: `${steps.length > 0 ? (completedSteps / steps.length) * 100 : 0}%`,
            backgroundColor: selected.status === "failed" ? "#ef4444" : "#10b981"
          }} />
        </div>

        {/* Steps */}
        <div className="space-y-3" data-testid="campaign-steps">
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
      <div className="max-w-4xl mx-auto p-6 space-y-6" data-testid="campaign-create">
        <div className="flex items-center gap-3">
          <Button size="sm" variant="ghost" className="h-7 text-zinc-400" onClick={() => setView("list")} data-testid="campaign-create-back">
            <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back
          </Button>
          <h2 className="text-lg font-bold text-white">New Campaign</h2>
        </div>

        <p className="text-sm text-zinc-400">Choose a template and provide context for your campaign.</p>

        {/* Template selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="template-grid">
          {templates.map(t => (
            <div key={t.template_id}
              className={`rounded-xl border-2 p-4 cursor-pointer transition-all ${selectedTemplate?.template_id === t.template_id ? "border-white/30 bg-white/[0.04]" : "border-white/5 hover:border-white/10 bg-zinc-900/30"}`}
              onClick={() => setSelectedTemplate(t)}
              data-testid={`template-${t.template_id}`}>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: t.color }} />
                <p className="text-sm font-semibold text-white">{t.name}</p>
              </div>
              <p className="text-xs text-zinc-500 mb-2">{t.description}</p>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{t.category}</span>
                <span className="text-[10px] text-zinc-600">{t.steps.length} steps</span>
              </div>
            </div>
          ))}
        </div>

        {selectedTemplate && (
          <div className="space-y-3">
            <div className="bg-zinc-900/50 border border-white/5 rounded-lg p-4">
              <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">Steps Preview</p>
              {selectedTemplate.steps.map((s, i) => (
                <div key={i} className="flex items-center gap-2 py-1.5">
                  <span className="text-[10px] font-mono text-zinc-600 w-4">{s.order}</span>
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: selectedTemplate.color }} />
                  <span className="text-xs text-zinc-300">{s.title}</span>
                  <span className="text-[10px] text-zinc-600">— {s.agent_role}</span>
                </div>
              ))}
            </div>

            <div>
              <label className="text-xs font-medium text-zinc-400 block mb-1">Campaign Context (optional)</label>
              <textarea
                value={contextInput}
                onChange={e => setContextInput(e.target.value)}
                placeholder="Add specific context for this campaign, e.g., 'We are launching a new AI-powered CRM tool targeting small businesses in the US market...'"
                className="w-full bg-zinc-800/50 border border-white/5 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30 resize-none"
                rows={3}
                data-testid="campaign-context-input"
              />
            </div>

            <Button className="bg-indigo-600 hover:bg-indigo-700 h-9 text-sm" onClick={createCampaign} data-testid="campaign-create-btn">
              <Zap className="w-3.5 h-3.5 mr-1.5" /> Create Campaign
            </Button>
          </div>
        )}
      </div>
    );
  }

  // List view
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6" data-testid="campaign-list">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Campaign Builder</h1>
          <p className="text-sm text-zinc-500">Multi-step automated workflows powered by AI agents</p>
        </div>
        <Button className="bg-indigo-600 hover:bg-indigo-700 h-9 text-sm" onClick={() => setView("create")} data-testid="new-campaign-btn">
          <Plus className="w-3.5 h-3.5 mr-1.5" /> New Campaign
        </Button>
      </div>

      {/* Templates quick access */}
      <div>
        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Quick Start Templates</p>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {templates.map(t => (
            <button key={t.template_id}
              className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg border border-white/5 hover:border-white/10 bg-zinc-900/30 transition-colors"
              onClick={() => { setSelectedTemplate(t); setView("create"); }}
              data-testid={`quick-template-${t.template_id}`}>
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: t.color }} />
              <span className="text-xs text-zinc-300">{t.name}</span>
              <span className="text-[10px] text-zinc-600">{t.steps.length} steps</span>
            </button>
          ))}
        </div>
      </div>

      {/* Campaigns list */}
      <div>
        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Your Campaigns</p>
        {campaigns.length === 0 ? (
          <div className="text-center py-12 text-zinc-600">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No campaigns yet. Create one from a template above.</p>
          </div>
        ) : (
          <div className="space-y-2" data-testid="campaigns-list">
            {campaigns.map(c => (
              <div key={c.campaign_id}
                className="group flex items-center gap-4 px-4 py-3 rounded-xl border border-white/5 hover:border-white/10 bg-zinc-900/30 cursor-pointer transition-all"
                onClick={() => { setSelected(c); setView("detail"); }}
                data-testid={`campaign-item-${c.campaign_id}`}>
                <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: c.color || "#6366f1" }} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white">{c.name}</p>
                  <p className="text-[10px] text-zinc-500">{c.category} &middot; {(c.steps || []).length} steps</p>
                </div>
                <StatusBadge status={c.status} />
                <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400" />
                <button onClick={e => { e.stopPropagation(); deleteCampaign(c.campaign_id); }}
                  className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400 transition-opacity"
                  data-testid={`campaign-delete-${c.campaign_id}`}>
                  <Trash2 className="w-3.5 h-3.5" />
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
  const styles = {
    draft: "bg-zinc-800 text-zinc-400",
    running: "bg-amber-500/10 text-amber-400",
    completed: "bg-emerald-500/10 text-emerald-400",
    failed: "bg-red-500/10 text-red-400",
  };
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${styles[status] || styles.draft}`} data-testid="campaign-status">
      {status || "draft"}
    </span>
  );
}

function StepCard({ step, index, isLast }) {
  const [expanded, setExpanded] = useState(step.status === "completed" || step.status === "failed");

  return (
    <div className="relative" data-testid={`step-card-${index}`}>
      {/* Connector line */}
      {!isLast && <div className="absolute left-[15px] top-10 bottom-0 w-px bg-zinc-800" />}
      <div className={`flex gap-3 ${step.status === "running" ? "animate-pulse" : ""}`}>
        {/* Step indicator */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
          step.status === "completed" ? "bg-emerald-500/20 text-emerald-400" :
          step.status === "running" ? "bg-amber-500/20 text-amber-400" :
          step.status === "failed" ? "bg-red-500/20 text-red-400" :
          "bg-zinc-800 text-zinc-500"
        }`}>
          {step.status === "completed" ? <CheckCircle className="w-4 h-4" /> :
           step.status === "running" ? <Clock className="w-4 h-4 animate-spin" /> :
           step.status === "failed" ? <AlertCircle className="w-4 h-4" /> :
           index + 1}
        </div>

        {/* Step content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => setExpanded(!expanded)}>
            <p className="text-sm font-medium text-white">{step.title}</p>
            <span className="text-[10px] text-zinc-500">{step.agent_name} &middot; {step.agent_role}</span>
            <div className="flex-1" />
            {step.output && (expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />)}
          </div>

          {/* Task */}
          <p className="text-[10px] text-zinc-600 mt-0.5 line-clamp-1">{step.task}</p>

          {/* Expanded output */}
          {expanded && step.output && (
            <div className={`mt-2 rounded-lg p-3 text-xs leading-relaxed whitespace-pre-wrap ${
              step.status === "failed" ? "bg-red-950/30 border border-red-500/10 text-red-300" : "bg-zinc-800/50 border border-white/5 text-zinc-300"
            }`} data-testid={`step-output-${index}`}>
              {step.output}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
