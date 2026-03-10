import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Brain, Sparkles, Plus, CheckCircle, Activity, Workflow, FileText, Bot } from "lucide-react";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

export default function AgentSuggestions() {
  const { token } = useAuth();
  const [data, setData] = useState({ suggestions: [], analysis: {} });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(null);
  const [created, setCreated] = useState(new Set());

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = async () => {
    try {
      const res = await fetch(`${API}/api/kernel/agent-suggestions`, { headers: h });
      if (res.ok) setData(await res.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [token]);

  const createAgent = async (suggestion) => {
    setCreating(suggestion.name);
    const res = await fetch(`${API}/api/kernel/agent-suggestions/create`, {
      method: "POST", headers: h,
      body: JSON.stringify({
        name: suggestion.name,
        role: suggestion.role,
        network: suggestion.network,
        description: suggestion.description,
      }),
    });
    if (res.ok) {
      toast.success(`${suggestion.name} created successfully`);
      setCreated(prev => new Set([...prev, suggestion.name]));
    }
    setCreating(null);
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  const { suggestions, analysis } = data;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6" data-testid="agent-suggestions">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Brain className="w-5 h-5 text-indigo-400" /> Self-Expanding Agents
        </h1>
        <p className="text-sm text-zinc-500">AI-powered suggestions for new agents based on your usage patterns</p>
      </div>

      {/* Analysis summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="analysis-summary">
        <AnalysisCard icon={<FileText className="w-4 h-4 text-indigo-400" />} label="Campaigns" value={analysis.total_campaigns || 0} />
        <AnalysisCard icon={<Workflow className="w-4 h-4 text-emerald-400" />} label="Workflows" value={analysis.total_workflows || 0} />
        <AnalysisCard icon={<Bot className="w-4 h-4 text-amber-400" />} label="Existing Agents" value={analysis.existing_agent_count || 0} />
        <AnalysisCard icon={<Sparkles className="w-4 h-4 text-violet-400" />} label="Suggestions" value={suggestions.length} />
      </div>

      {/* Category breakdown */}
      {Object.keys(analysis.campaign_categories || {}).length > 0 && (
        <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-400 mb-2">Campaign Category Distribution</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(analysis.campaign_categories || {}).map(([cat, count]) => (
              <span key={cat} className="text-[10px] px-2 py-1 rounded-lg bg-zinc-800/50 text-zinc-300">
                {cat}: <span className="font-bold text-white">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      <div>
        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Recommended Agents</p>
        {suggestions.length === 0 ? (
          <div className="text-center py-12 bg-zinc-900/30 rounded-xl border border-white/5">
            <Activity className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
            <p className="text-sm text-zinc-500 mb-1">No suggestions yet</p>
            <p className="text-xs text-zinc-600">Create campaigns and workflows to get AI-powered agent recommendations.</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="suggestions-list">
            {suggestions.map((s, i) => {
              const isCreated = created.has(s.name);
              const isCreating = creating === s.name;
              return (
                <div key={i} className="rounded-xl border border-white/5 bg-zinc-900/30 p-4 transition-all hover:border-white/10" data-testid={`suggestion-${i}`}>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center shrink-0">
                      <Sparkles className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-white">{s.name}</p>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{s.network}</span>
                        <div className="flex-1" />
                        <span className="text-[9px] text-indigo-400/70">{Math.round((s.confidence || 0) * 100)}% confidence</span>
                      </div>
                      <p className="text-xs text-zinc-400 mt-0.5">{s.role}</p>
                      <p className="text-[10px] text-zinc-500 mt-1">{s.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-[9px] text-zinc-600">Based on: {s.based_on}</span>
                        <div className="flex-1" />
                        {isCreated ? (
                          <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Created</span>
                        ) : (
                          <Button size="sm" className="h-7 text-[10px] bg-indigo-600 hover:bg-indigo-700" disabled={isCreating}
                            onClick={() => createAgent(s)} data-testid={`create-suggestion-${i}`}>
                            {isCreating ? <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin mr-1" /> : <Plus className="w-3 h-3 mr-1" />}
                            Create Agent
                          </Button>
                        )}
                      </div>
                    </div>
                    {/* Confidence bar */}
                    <div className="w-16 shrink-0">
                      <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(s.confidence || 0) * 100}%` }} />
                      </div>
                    </div>
                  </div>
                  {s.reason && (
                    <div className="mt-3 px-3 py-2 bg-zinc-800/30 rounded-lg">
                      <p className="text-[9px] text-zinc-400"><span className="font-medium text-zinc-300">Rationale:</span> {s.reason}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function AnalysisCard({ icon, label, value }) {
  return (
    <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-3">
      <div className="flex items-center gap-2 mb-1">{icon}<span className="text-[10px] text-zinc-500">{label}</span></div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}
