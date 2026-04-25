import { useState, useEffect, useMemo } from "react";
import { useAuth } from "../App";
import { Brain, Sparkles, Plus, CheckCircle, Activity, Workflow, FileText, Bot } from "lucide-react";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

export default function AgentSuggestions() {
  const { token } = useAuth();
  const [data, setData] = useState({ suggestions: [], analysis: {} });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(null);
  const [created, setCreated] = useState(new Set());

  const h = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/api/kernel/agent-suggestions`, { headers: h });
        if (res.ok) setData(await res.json());
      } catch {} finally { setLoading(false); }
    })();
  }, [h]);

  const createAgent = async (suggestion) => {
    setCreating(suggestion.name);
    const res = await fetch(`${API}/api/kernel/agent-suggestions/create`, {
      method: "POST", headers: h,
      body: JSON.stringify({ name: suggestion.name, role: suggestion.role, network: suggestion.network, description: suggestion.description }),
    });
    if (res.ok) { toast.success(`${suggestion.name} created successfully`); setCreated(prev => new Set([...prev, suggestion.name])); }
    setCreating(null);
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const { suggestions, analysis } = data;
  const STAT_CARDS = [
    { icon: FileText, color: T.indigo, label: "Campaigns", value: analysis.total_campaigns || 0 },
    { icon: Workflow, color: T.green, label: "Workflows", value: analysis.total_workflows || 0 },
    { icon: Bot, color: T.amber, label: "Existing Agents", value: analysis.existing_agent_count || 0 },
    { icon: Sparkles, color: "#a78bfa", label: "Suggestions", value: suggestions.length },
  ];

  return (
    <div style={{ maxWidth: 820, margin: "0 auto", display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="agent-suggestions">
      <style>{STYLES}</style>

      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4, display: "flex", alignItems: "center", gap: 10 }}>
          <Brain size={22} style={{ color: T.indigo }} /> Self-Expanding Agents
        </h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>AI-powered suggestions for new agents based on your usage patterns</p>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }} data-testid="analysis-summary">
        {STAT_CARDS.map(s => (
          <div key={s.label} style={{ position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "12px 14px", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <s.icon size={13} style={{ color: s.color }} />
              <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".05em" }}>{s.label}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, color: "#fff" }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Category breakdown */}
      {Object.keys(analysis.campaign_categories || {}).length > 0 && (
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }}>
          <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600, marginBottom: 8 }}>Campaign Category Distribution</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {Object.entries(analysis.campaign_categories || {}).map(([cat, count]) => (
              <span key={cat} style={{ fontSize: 10, padding: "4px 10px", borderRadius: 8, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, color: "#d4d4d8" }}>
                {cat}: <span style={{ fontWeight: 700, color: "#fff" }}>{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      <div>
        <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".07em", fontWeight: 600, marginBottom: 12 }}>Recommended Agents</p>
        {suggestions.length === 0 ? (
          <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
            <Activity size={40} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
            <p style={{ fontSize: 13, color: T.zinc, marginBottom: 4 }}>No suggestions yet</p>
            <p style={{ fontSize: 11, color: "rgba(113,113,122,.6)" }}>Create campaigns and workflows to get AI-powered agent recommendations.</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }} data-testid="suggestions-list">
            {suggestions.map((s, i) => {
              const isCreated = created.has(s.name);
              const isCreating = creating === s.name;
              const confidencePct = Math.round((s.confidence || 0) * 100);
              return (
                <div key={i} data-testid={`suggestion-${i}`}
                  style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "14px 16px", transition: "border-color .2s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.14)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                    <div style={{ width: 40, height: 40, borderRadius: 11, background: "rgba(129,140,248,.1)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <Sparkles size={18} style={{ color: T.indigo }} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 3 }}>
                        <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>{s.name}</span>
                        <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, background: "rgba(255,255,255,.06)", color: T.zinc }}>{s.network}</span>
                        <span style={{ marginLeft: "auto", fontSize: 9, color: "rgba(129,140,248,.7)" }}>{confidencePct}% confidence</span>
                      </div>
                      <p style={{ fontSize: 11, color: "#a1a1aa", marginBottom: 3 }}>{s.role}</p>
                      <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8 }}>{s.description}</p>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <span style={{ fontSize: 9, color: "rgba(113,113,122,.6)" }}>Based on: {s.based_on}</span>
                        <div style={{ flex: 1, height: 3, background: "rgba(255,255,255,.06)", borderRadius: 3, overflow: "hidden", maxWidth: 80 }}>
                          <div style={{ height: "100%", borderRadius: 3, background: T.indigo, width: `${confidencePct}%` }} />
                        </div>
                        {isCreated ? (
                          <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: T.green, fontWeight: 600 }}>
                            <CheckCircle size={12} /> Created
                          </span>
                        ) : (
                          <button onClick={() => createAgent(s)} disabled={isCreating} data-testid={`create-suggestion-${i}`}
                            style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: isCreating ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 11, fontWeight: 700, cursor: isCreating ? "not-allowed" : "pointer" }}>
                            {isCreating ? <div style={{ width: 11, height: 11, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Plus size={11} />}
                            Create Agent
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                  {s.reason && (
                    <div style={{ marginTop: 10, padding: "8px 12px", background: "rgba(255,255,255,.025)", borderRadius: 8 }}>
                      <p style={{ fontSize: 10, color: "#a1a1aa" }}><span style={{ fontWeight: 600, color: "#d4d4d8" }}>Rationale:</span> {s.reason}</p>
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
