import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Brain, Shield, Zap, ChevronRight, ChevronDown, Save, RotateCcw,
  Cpu, Lock, Unlock, AlertTriangle, Target, Gauge, Users, X
} from "lucide-react";
import { toast } from "sonner";

const MEMORY_SCOPES = [
  { id: "working", label: "Working", desc: "Short-term task memory" },
  { id: "long_term", label: "Long-Term", desc: "Persistent across sessions" },
  { id: "domain", label: "Domain", desc: "Specialized knowledge" },
  { id: "shared", label: "Shared", desc: "Cross-agent access" },
];

const AUTONOMY_LABELS = {
  0: "None", 1: "Minimal", 2: "Low", 3: "Medium", 4: "High", 5: "Full",
};

const AUTONOMY_COLORS = {
  0: "bg-zinc-600", 1: "bg-red-500", 2: "bg-orange-500",
  3: "bg-amber-500", 4: "bg-indigo-500", 5: "bg-emerald-500",
};

const BrainProfileCard = ({ profile, onSelect }) => {
  const autonomy = profile.autonomy_level || 3;
  return (
    <div
      className="bg-zinc-900/50 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all cursor-pointer group"
      onClick={() => onSelect(profile.agent_id)}
      data-testid={`brain-card-${profile.agent_id}`}
    >
      <div className="flex items-center gap-3 mb-3">
        <img src={profile.agent_avatar} alt="" className="w-10 h-10 rounded-lg object-cover" />
        <div className="flex-1 min-w-0">
          <h3 className="text-white text-sm font-medium truncate">{profile.agent_name}</h3>
          <p className="text-[10px] text-zinc-500">{profile.agent_role}</p>
        </div>
        {profile.is_custom && (
          <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 text-[9px]">Custom</Badge>
        )}
        <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
      </div>
      <div className="flex items-center gap-3 text-[10px]">
        <div className="flex items-center gap-1">
          <Gauge className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-400">Autonomy: {autonomy}/5</span>
          <div className={`w-2 h-2 rounded-full ${AUTONOMY_COLORS[autonomy]}`} />
        </div>
        <div className="flex items-center gap-1">
          {profile.approval_required ? (
            <><Lock className="w-3 h-3 text-amber-400" /><span className="text-amber-400">Approval</span></>
          ) : (
            <><Unlock className="w-3 h-3 text-emerald-400" /><span className="text-emerald-400">Auto</span></>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Cpu className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-400">{profile.primary_model?.model || "gpt-5.2"}</span>
        </div>
      </div>
      {profile.communication_style && (
        <p className="text-[10px] text-zinc-600 mt-2 truncate">Style: {profile.communication_style}</p>
      )}
    </div>
  );
};

const BrainEditor = ({ agentId, onClose }) => {
  const { token } = useAuth();
  const [brain, setBrain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [edited, setEdited] = useState({});

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  useEffect(() => {
    const fetchBrain = async () => {
      try {
        const res = await fetch(`${API}/agents/${agentId}/brain`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          setBrain(data);
          setEdited(data);
        }
      } catch {} finally { setLoading(false); }
    };
    fetchBrain();
  }, [agentId, token]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/agents/${agentId}/brain`, {
        method: "PUT", headers,
        body: JSON.stringify({
          autonomy_level: edited.autonomy_level,
          approval_required: edited.approval_required,
          communication_style: edited.communication_style,
          memory_scopes: edited.memory_scopes,
          kpis: edited.kpis,
          escalation_rules: edited.escalation_rules,
          risk_boundaries: edited.risk_boundaries,
          primary_model: edited.primary_model,
          fallback_models: edited.fallback_models,
          output_templates: edited.output_templates,
        }),
      });
      if (res.ok) {
        toast.success("Brain profile saved");
        setBrain(await res.json());
      } else toast.error("Failed to save");
    } catch { toast.error("Error saving"); }
    finally { setSaving(false); }
  };

  const handleReset = async () => {
    if (!window.confirm("Reset to default brain profile?")) return;
    try {
      await fetch(`${API}/agents/${agentId}/brain`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      toast.success("Reset to defaults");
      onClose();
    } catch { toast.error("Reset failed"); }
  };

  if (loading) return <div className="flex items-center justify-center py-20"><div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" /></div>;

  if (!brain) return null;

  const updateField = (field, value) => setEdited(prev => ({ ...prev, [field]: value }));

  return (
    <div className="space-y-4" data-testid="brain-editor">
      <div className="flex items-center gap-3 mb-2">
        <Button variant="ghost" size="sm" onClick={onClose} className="text-zinc-400 hover:text-white">
          <X className="w-4 h-4" />
        </Button>
        <Brain className="w-5 h-5 text-indigo-400" />
        <h2 className="text-white font-semibold text-lg font-['Outfit']">Custom Brain Profile</h2>
        <div className="ml-auto flex gap-2">
          {brain.is_custom && (
            <Button variant="ghost" size="sm" onClick={handleReset} className="text-zinc-400 hover:text-red-400">
              <RotateCcw className="w-4 h-4 mr-1" />Reset
            </Button>
          )}
          <Button size="sm" onClick={handleSave} disabled={saving} className="bg-indigo-600 hover:bg-indigo-500 text-white" data-testid="save-brain-btn">
            <Save className="w-4 h-4 mr-1" />{saving ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>

      {/* Autonomy Level */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-4 h-4 text-indigo-400" />
            <p className="text-sm text-white font-medium">Autonomy Level</p>
            <Badge className={`ml-auto text-[10px] text-white ${AUTONOMY_COLORS[edited.autonomy_level || 3]}`}>
              {edited.autonomy_level || 3}/5 — {AUTONOMY_LABELS[edited.autonomy_level || 3]}
            </Badge>
          </div>
          <input
            type="range" min="0" max="5" step="1"
            value={edited.autonomy_level ?? 3}
            onChange={(e) => updateField("autonomy_level", parseInt(e.target.value))}
            className="w-full accent-indigo-500"
            data-testid="autonomy-slider"
          />
          <div className="flex justify-between text-[9px] text-zinc-600 mt-1">
            {Object.entries(AUTONOMY_LABELS).map(([k, v]) => <span key={k}>{v}</span>)}
          </div>
        </CardContent>
      </Card>

      {/* Approval Required */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-amber-400" />
              <p className="text-sm text-white font-medium">Approval Required</p>
            </div>
            <button
              onClick={() => updateField("approval_required", !edited.approval_required)}
              className={`w-10 h-5 rounded-full transition-colors ${edited.approval_required ? "bg-amber-500" : "bg-zinc-700"}`}
              data-testid="approval-toggle"
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${edited.approval_required ? "translate-x-5" : "translate-x-0.5"}`} />
            </button>
          </div>
          <p className="text-[10px] text-zinc-500 mt-1">
            {edited.approval_required ? "Agent actions require your approval before execution" : "Agent can execute actions autonomously"}
          </p>
        </CardContent>
      </Card>

      {/* Communication Style */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Communication Style</p>
          <Input
            value={edited.communication_style || ""}
            onChange={(e) => updateField("communication_style", e.target.value)}
            placeholder="e.g. Professional, data-driven, concise"
            className="bg-zinc-800/50 border-white/10 text-white text-sm"
            data-testid="communication-style-input"
          />
        </CardContent>
      </Card>

      {/* Memory Scopes */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Memory Scopes</p>
          <div className="grid grid-cols-2 gap-2">
            {MEMORY_SCOPES.map(scope => {
              const active = (edited.memory_scopes || []).includes(scope.id);
              return (
                <button
                  key={scope.id}
                  onClick={() => {
                    const current = edited.memory_scopes || [];
                    updateField("memory_scopes",
                      active ? current.filter(s => s !== scope.id) : [...current, scope.id]
                    );
                  }}
                  className={`p-2 rounded-lg border text-left transition-colors ${
                    active ? "border-indigo-500/30 bg-indigo-500/10" : "border-white/5 bg-zinc-800/30"
                  }`}
                  data-testid={`memory-${scope.id}`}
                >
                  <p className={`text-xs font-medium ${active ? "text-indigo-400" : "text-zinc-400"}`}>{scope.label}</p>
                  <p className="text-[9px] text-zinc-600">{scope.desc}</p>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* KPIs */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">KPIs</p>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {(edited.kpis || []).map((kpi, i) => (
              <Badge key={i} variant="outline" className="border-white/10 text-zinc-300 text-[10px] gap-1">
                <Target className="w-2.5 h-2.5" />{kpi}
                <button onClick={() => updateField("kpis", edited.kpis.filter((_, j) => j !== i))} className="ml-1 text-zinc-500 hover:text-red-400">
                  <X className="w-2.5 h-2.5" />
                </button>
              </Badge>
            ))}
          </div>
          <Input
            placeholder="Add a KPI and press Enter"
            className="bg-zinc-800/50 border-white/10 text-white text-xs"
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.target.value.trim()) {
                updateField("kpis", [...(edited.kpis || []), e.target.value.trim()]);
                e.target.value = "";
              }
            }}
            data-testid="kpi-input"
          />
        </CardContent>
      </Card>

      {/* Escalation Rules */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Escalation Rules</p>
          <div className="space-y-1.5 mb-2">
            {(edited.escalation_rules || []).map((rule, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-zinc-300 bg-zinc-800/30 rounded-lg px-3 py-1.5">
                <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                <span className="flex-1">{rule}</span>
                <button onClick={() => updateField("escalation_rules", edited.escalation_rules.filter((_, j) => j !== i))} className="text-zinc-500 hover:text-red-400">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
          <Input
            placeholder="Add an escalation rule and press Enter"
            className="bg-zinc-800/50 border-white/10 text-white text-xs"
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.target.value.trim()) {
                updateField("escalation_rules", [...(edited.escalation_rules || []), e.target.value.trim()]);
                e.target.value = "";
              }
            }}
            data-testid="escalation-input"
          />
        </CardContent>
      </Card>

      {/* Risk Boundaries */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Risk Boundaries</p>
          <div className="space-y-3">
            <div>
              <label className="text-[10px] text-zinc-500 mb-1 block">Max Budget Authority ($)</label>
              <Input
                type="number"
                value={edited.risk_boundaries?.max_budget_authority || 0}
                onChange={(e) => updateField("risk_boundaries", { ...edited.risk_boundaries, max_budget_authority: parseInt(e.target.value) || 0 })}
                className="bg-zinc-800/50 border-white/10 text-white text-sm"
                data-testid="budget-authority-input"
              />
            </div>
            <div className="flex items-center justify-between">
              <p className="text-xs text-zinc-400">Can Approve External Communications</p>
              <button
                onClick={() => updateField("risk_boundaries", { ...edited.risk_boundaries, can_approve_external_comms: !edited.risk_boundaries?.can_approve_external_comms })}
                className={`w-10 h-5 rounded-full transition-colors ${edited.risk_boundaries?.can_approve_external_comms ? "bg-emerald-500" : "bg-zinc-700"}`}
                data-testid="external-comms-toggle"
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${edited.risk_boundaries?.can_approve_external_comms ? "translate-x-5" : "translate-x-0.5"}`} />
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const BrainProfiles = () => {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [search, setSearch] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  const fetchProfiles = useCallback(async () => {
    try {
      const res = await fetch(`${API}/brain-profiles`, { headers });
      if (res.ok) {
        const data = await res.json();
        setProfiles(data.profiles || []);
      }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchProfiles(); }, [fetchProfiles]);

  const filtered = profiles.filter(p =>
    !search || p.agent_name?.toLowerCase().includes(search.toLowerCase()) || p.agent_role?.toLowerCase().includes(search.toLowerCase())
  );

  if (selectedAgent) {
    return <BrainEditor agentId={selectedAgent} onClose={() => { setSelectedAgent(null); fetchProfiles(); }} />;
  }

  return (
    <div className="space-y-6" data-testid="brain-profiles-page">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/15 flex items-center justify-center">
          <Brain className="w-5 h-5 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Custom Brain Profiles</h1>
          <p className="text-xs text-zinc-500">Configure each agent's AI brain, autonomy, memory, and behavior</p>
        </div>
      </div>

      <Input
        placeholder="Search agents..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="bg-zinc-900/50 border-white/10 text-white text-sm"
        data-testid="brain-search"
      />

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtered.map(profile => (
            <BrainProfileCard
              key={profile.agent_id}
              profile={profile}
              onSelect={setSelectedAgent}
            />
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="text-center py-12">
          <Brain className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
          <p className="text-zinc-400">No agents found</p>
        </div>
      )}
    </div>
  );
};

export default BrainProfiles;
