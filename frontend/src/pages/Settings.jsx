import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  User, Mail, LogOut, CreditCard, Sparkles, Crown, Zap,
  Check, Save, Loader2, Cpu, Link2, Unlink, Shield, Users
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  blue: "#60a5fa",
  orange: "#f97316",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes bar { from{width:0} to{width:var(--bar-w)} }
`;

const glass = {
  background: T.glass,
  border: `1px solid ${T.border}`,
  borderRadius: 16,
  backdropFilter: "blur(12px)",
  marginBottom: 20,
  position: "relative",
  overflow: "hidden",
};

const Section = ({ title, icon, accent = T.teal, children, testId }) => (
  <div style={glass} data-testid={testId}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent }} />
    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "18px 22px 14px", borderBottom: `1px solid ${T.border}` }}>
      <span style={{ color: accent }}>{icon}</span>
      <span style={{ fontFamily: "'Outfit',sans-serif", fontSize: 15, fontWeight: 700, color: "#fff" }}>{title}</span>
    </div>
    <div style={{ padding: "20px 22px" }}>{children}</div>
  </div>
);

const glassInput = {
  width: "100%", boxSizing: "border-box",
  background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`,
  borderRadius: 10, padding: "9px 12px",
  color: "rgba(255,255,255,.5)", fontSize: 13, outline: "none", fontFamily: "inherit",
};

const PLAN_META = {
  business: { color: T.amber, icon: Crown, label: "Business" },
  pro:      { color: T.violet, icon: Sparkles, label: "Pro" },
  starter:  { color: T.blue, icon: Zap, label: "Starter" },
  free:     { color: T.zinc, icon: CreditCard, label: "Free" },
};

const PROVIDER_ACCENT = {
  openai: "#10b981", anthropic: "#f97316", google: "#3b82f6",
  deepseek: T.teal, mistral: "#ff7000", groq: "#f55036",
  xai: "#94a3b8", perplexity: "#8b5cf6", cohere: "#d97706", together: "#06b6d4",
};

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [allAgents, setAllAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [agentConfig, setAgentConfig] = useState(null);
  const [savingAgents, setSavingAgents] = useState(false);
  const [llmConfig, setLlmConfig] = useState(null);
  const [savingLlm, setSavingLlm] = useState(false);
  const [actionIntegrations, setActionIntegrations] = useState(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchSubscription();
    fetchAgents();
    fetchSelectedAgents();
    fetchLlmConfig();
    fetchActionIntegrations();
  }, []);

  const fetchSubscription = async () => {
    try { const r = await fetch(`${API}/subscription`, { headers }); if (r.ok) setSubscription(await r.json()); } catch {}
  };
  const fetchAgents = async () => {
    try { const r = await fetch(`${API}/agents`, { headers }); if (r.ok) setAllAgents(await r.json()); } catch {}
  };
  const fetchSelectedAgents = async () => {
    try {
      const r = await fetch(`${API}/subscription/agents`, { headers });
      if (r.ok) { const d = await r.json(); setAgentConfig(d); setSelectedAgents(d.selected_agents || []); }
    } catch {}
  };
  const fetchLlmConfig = async () => {
    try { const r = await fetch(`${API}/llm/config`, { headers }); if (r.ok) setLlmConfig(await r.json()); } catch {}
  };
  const fetchActionIntegrations = async () => {
    try { const r = await fetch(`${API}/actions/integrations`, { headers }); if (r.ok) setActionIntegrations(await r.json()); } catch {}
  };

  const saveLlmConfig = async (provider, model, quality_tier, task_hint) => {
    setSavingLlm(true);
    try {
      const r = await fetch(`${API}/llm/config`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          provider, model,
          quality_tier: quality_tier ?? llmConfig?.quality_tier ?? "auto",
          task_hint:    task_hint    ?? llmConfig?.task_hint    ?? "auto",
        }),
      });
      if (r.ok) { const updated = await r.json(); setLlmConfig(prev => ({ ...prev, ...updated })); toast.success(`Model: ${provider}/${model}`); }
    } catch { toast.error("Failed to save model config"); }
    finally { setSavingLlm(false); }
  };

  const connectGoogle = async () => {
    try {
      const r = await fetch(`${API}/oauth/gmail/login`, { headers });
      if (r.ok) { const d = await r.json(); if (d.auth_url) window.location.href = d.auth_url; }
      else { const e = await r.json().catch(() => ({})); toast.error(e.detail || "Google OAuth not configured"); }
    } catch { toast.error("Failed to start Google connection"); }
  };
  const disconnectGoogle = async () => {
    try { await fetch(`${API}/oauth/gmail/disconnect`, { headers }); toast.success("Google disconnected"); fetchActionIntegrations(); } catch {}
  };
  const saveAgentSelection = async () => {
    setSavingAgents(true);
    try {
      const r = await fetch(`${API}/subscription/agents`, {
        method: "PUT", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ selected_agents: selectedAgents }),
      });
      if (r.ok) { toast.success("Agent selection saved!"); fetchSelectedAgents(); }
      else { const e = await r.json(); toast.error(e.detail || "Failed to save"); }
    } catch { toast.error("Failed to save"); }
    finally { setSavingAgents(false); }
  };
  const toggleAgentSelection = (agentId) => {
    setSelectedAgents(prev => prev.includes(agentId) ? prev.filter(id => id !== agentId) : [...prev, agentId]);
  };

  const planId = subscription?.plan_id || "free";
  const planMeta = PLAN_META[planId] || PLAN_META.free;
  const PlanIcon = planMeta.icon;
  const creditPct = subscription?.plan_info?.credits
    ? Math.min(((subscription?.credits || 0) / subscription.plan_info.credits) * 100, 100)
    : Math.min(((subscription?.credits || 0) / 50) * 100, 100);

  const isExecution = actionIntegrations?.system_mode === "execution";
  const googleConnected = actionIntegrations?.integrations?.[0]?.connected;

  return (
    <div data-testid="settings-page" style={{ maxWidth: 760, animation: "fadeUp .4s ease" }}>
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 28, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Settings</h1>
        <p style={{ color: T.zinc, fontSize: 14, margin: 0 }}>Manage your account, subscription, and AI preferences</p>
      </div>

      {/* Profile */}
      <Section title="Profile" icon={<User size={16} />} accent={T.violet}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 24 }}>
          <div style={{ width: 72, height: 72, borderRadius: "50%", background: `linear-gradient(135deg, ${T.violet}, #9333ea)`, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", flexShrink: 0, border: `3px solid rgba(124,58,237,.3)` }}>
            {user?.picture
              ? <img src={user.picture} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              : <span style={{ fontSize: 24, color: "#fff", fontWeight: 700 }}>{user?.name?.charAt(0) || "U"}</span>
            }
          </div>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "#fff", marginBottom: 2 }}>{user?.name}</div>
            <div style={{ fontSize: 13, color: T.zinc }}>{user?.email}</div>
            {user?.is_admin && <span style={{ fontSize: 10, background: "rgba(245,158,11,0.15)", color: T.amber, padding: "2px 8px", borderRadius: 6, marginTop: 4, display: "inline-block", fontWeight: 600 }}>ADMIN</span>}
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          {[["Full Name", user?.name], ["Email Address", user?.email]].map(([label, val]) => (
            <div key={label}>
              <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".05em" }}>{label}</label>
              <input value={val || ""} disabled style={glassInput} />
            </div>
          ))}
        </div>
      </Section>

      {/* Subscription & Credits */}
      <Section title="Subscription & Credits" icon={<CreditCard size={16} />} accent={T.amber} testId="subscription-section">
        {/* Plan row */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}`, marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: `${planMeta.color}18`, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <PlanIcon size={18} style={{ color: planMeta.color }} />
            </div>
            <div>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#fff" }}>{subscription?.plan_info?.name || "Free"} Plan</div>
              <div style={{ fontSize: 12, color: T.zinc }}>${subscription?.plan_info?.price || 0}/month</div>
            </div>
          </div>
          <button
            onClick={() => navigate("/pricing")}
            data-testid="upgrade-plan-btn"
            style={{ background: `linear-gradient(135deg, ${T.violet}, #9333ea)`, border: "none", borderRadius: 10, padding: "8px 18px", color: "#fff", fontSize: 13, fontWeight: 600, cursor: "pointer" }}
          >
            {planId === "business" ? "Manage Plan" : "Upgrade"}
          </button>
        </div>

        {/* Credits bar */}
        <div style={{ padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}`, marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>Credits Remaining</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: T.amber }}>{subscription?.credits || 0} credits</span>
          </div>
          <div style={{ height: 6, background: "rgba(255,255,255,.06)", borderRadius: 6, overflow: "hidden", marginBottom: 8 }}>
            <div style={{ "--bar-w": `${creditPct}%`, height: "100%", borderRadius: 6, background: `linear-gradient(90deg, ${T.amber}, #d97706)`, width: `${creditPct}%` }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: T.zinc }}>
            <span>Used: {subscription?.credits_used || 0}</span>
            <span>Monthly: {subscription?.plan_info?.credits || 50}</span>
          </div>
        </div>

        <button
          onClick={() => navigate("/pricing")}
          data-testid="buy-credits-btn"
          style={{ width: "100%", padding: "10px 0", borderRadius: 12, background: "rgba(245,158,11,.08)", border: `1px solid rgba(245,158,11,.25)`, color: T.amber, fontSize: 13, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}
        >
          <Sparkles size={14} /> Buy More Credits
        </button>
      </Section>

      {/* LLM Configuration */}
      {llmConfig && (
        <Section title="AI Model Configuration" icon={<Cpu size={16} />} accent={T.teal} testId="llm-config-card">
          <p style={{ fontSize: 12, color: T.zinc, marginBottom: 16 }}>Choose your preferred LLM provider and model for Vibe Coding, Reference Intelligence, and other AI features</p>

          {/* Provider grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginBottom: 16 }}>
            {llmConfig.available_providers?.map(p => {
              const active = llmConfig.provider === p.id;
              const accent = PROVIDER_ACCENT[p.id] || T.teal;
              return (
                <button
                  key={p.id}
                  onClick={() => saveLlmConfig(p.id, p.models[0])}
                  disabled={savingLlm}
                  data-testid={`llm-provider-${p.id}`}
                  style={{
                    padding: "10px 12px", borderRadius: 12, textAlign: "left", cursor: "pointer",
                    background: active ? `${accent}12` : "rgba(255,255,255,.03)",
                    border: active ? `1px solid ${accent}50` : `1px solid ${T.border}`,
                    transition: "all .15s",
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 600, color: active ? accent : "#e4e4e7", marginBottom: 2 }}>{p.name}</div>
                  <div style={{ fontSize: 10, color: T.zinc }}>{p.models.length} models</div>
                  {active && (
                    <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 5 }}>
                      <div style={{ width: 6, height: 6, borderRadius: "50%", background: accent }} />
                      <span style={{ fontSize: 10, color: accent, fontWeight: 600 }}>Active</span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Model selector */}
          {llmConfig.available_providers?.filter(p => p.id === llmConfig.provider).map(p => (
            <div key={p.id} style={{ marginBottom: 16 }}>
              <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8 }}>Select model for <span style={{ color: "#fff" }}>{p.name}</span>:</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {p.models.map(m => {
                  const active = llmConfig.model === m;
                  return (
                    <button
                      key={m}
                      onClick={() => saveLlmConfig(p.id, m)}
                      disabled={savingLlm}
                      data-testid={`llm-model-${m}`}
                      style={{
                        padding: "5px 12px", borderRadius: 8, fontSize: 11, cursor: "pointer",
                        background: active ? "rgba(79,209,197,.12)" : "rgba(255,255,255,.04)",
                        border: active ? `1px solid rgba(79,209,197,.4)` : `1px solid ${T.border}`,
                        color: active ? T.teal : T.zinc,
                      }}
                    >
                      {m}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Router Calibration */}
          <div style={{ borderTop: `1px solid ${T.border}`, paddingTop: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#fff", marginBottom: 4 }}>Universal Router Calibration</div>
            <div style={{ fontSize: 11, color: T.zinc, marginBottom: 14 }}>When using Auto mode in chat, these preferences guide the smart router.</div>

            <div style={{ marginBottom: 14 }}>
              <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8 }}>Default Quality Tier</p>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {[["auto","Auto ✦"],["economy","Economy"],["standard","Standard"],["premium","Premium"]].map(([v, l]) => {
                  const active = llmConfig.quality_tier === v;
                  return (
                    <button key={v} onClick={() => saveLlmConfig(llmConfig.provider, llmConfig.model, v, llmConfig.task_hint)} disabled={savingLlm}
                      style={{ padding: "5px 12px", borderRadius: 8, fontSize: 11, cursor: "pointer", background: active ? "rgba(79,209,197,.12)" : "rgba(255,255,255,.04)", border: active ? `1px solid ${T.teal}50` : `1px solid ${T.border}`, color: active ? T.teal : T.zinc }}>{l}</button>
                  );
                })}
              </div>
            </div>

            <div style={{ marginBottom: 14 }}>
              <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8 }}>Default Task Hint</p>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {[["auto","Auto"],["code","Code"],["math","Math"],["reasoning","Reasoning"],["creative","Creative"],["translation","Translation"],["summary","Summary"],["research","Research"],["data","Data"],["chat","Chat"]].map(([v, l]) => {
                  const active = llmConfig.task_hint === v;
                  return (
                    <button key={v} onClick={() => saveLlmConfig(llmConfig.provider, llmConfig.model, llmConfig.quality_tier, v)} disabled={savingLlm}
                      style={{ padding: "5px 12px", borderRadius: 8, fontSize: 11, cursor: "pointer", background: active ? "rgba(124,58,237,.12)" : "rgba(255,255,255,.04)", border: active ? `1px solid ${T.violet}50` : `1px solid ${T.border}`, color: active ? "#c4b5fd" : T.zinc }}>{l}</button>
                  );
                })}
              </div>
            </div>

            {/* Active config badge */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderRadius: 10, background: "rgba(79,209,197,.06)", border: `1px solid rgba(79,209,197,.2)` }}>
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "#fff" }}>Active Configuration</div>
                <div style={{ fontSize: 11, fontFamily: "monospace", color: T.teal, marginTop: 2 }}>{llmConfig.provider}/{llmConfig.model}</div>
                <div style={{ fontSize: 10, color: T.zinc }}>{llmConfig.quality_tier || "auto"} quality · {llmConfig.task_hint || "auto"} task</div>
              </div>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: T.green }} />
            </div>
          </div>
        </Section>
      )}

      {/* Integrations */}
      <Section title="Integrations & Actions" icon={<Link2 size={16} />} accent={T.blue} testId="integrations-card">
        <p style={{ fontSize: 12, color: T.zinc, marginBottom: 16 }}>Connect external services for real-world agent actions</p>

        {/* Google Suite */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}`, marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(96,165,250,.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Mail size={18} style={{ color: T.blue }} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#fff", marginBottom: 2 }}>Google Suite</div>
              <div style={{ fontSize: 11, color: T.zinc }}>Gmail, Calendar integration</div>
              {actionIntegrations?.integrations?.[0]?.email && (
                <div style={{ fontSize: 11, color: T.green }}>{actionIntegrations.integrations[0].email}</div>
              )}
            </div>
          </div>
          {googleConnected ? (
            <button onClick={disconnectGoogle} data-testid="disconnect-google-btn" style={{ padding: "7px 14px", borderRadius: 10, fontSize: 12, fontWeight: 600, cursor: "pointer", background: "rgba(239,68,68,.08)", border: `1px solid rgba(239,68,68,.25)`, color: T.red, display: "flex", alignItems: "center", gap: 6 }}>
              <Unlink size={13} /> Disconnect
            </button>
          ) : (
            <button onClick={connectGoogle} data-testid="connect-google-btn" style={{ padding: "7px 14px", borderRadius: 10, fontSize: 12, fontWeight: 600, cursor: "pointer", background: "rgba(96,165,250,.12)", border: `1px solid rgba(96,165,250,.3)`, color: T.blue, display: "flex", alignItems: "center", gap: 6 }}>
              <Link2 size={13} /> Connect
            </button>
          )}
        </div>

        {/* System mode */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.02)", border: `1px solid ${T.border}` }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: isExecution ? T.green : T.amber, flexShrink: 0 }} />
          <div style={{ fontSize: 12, color: T.zinc }}>
            System Mode: <span style={{ color: isExecution ? T.green : T.amber, fontWeight: 600 }}>{isExecution ? "Execution (Live)" : "Simulation (Safe)"}</span>
            <span style={{ color: "rgba(113,113,122,.6)", marginLeft: 8 }}>— Toggle in KPI Dashboard</span>
          </div>
        </div>
      </Section>

      {/* Agent Selection */}
      {agentConfig && agentConfig.plan_id !== "custom" && (
        <Section title="Your Agents" icon={<Users size={16} />} accent={T.violet} testId="agent-selection-card">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>
              Select agents for your plan. {agentConfig.includes_commander && "Commander AI is included."}
            </p>
            <span style={{ fontSize: 12, fontWeight: 600, color: T.violet, background: "rgba(124,58,237,.12)", padding: "3px 12px", borderRadius: 8, border: `1px solid rgba(124,58,237,.3)` }}>
              {selectedAgents.filter(a => a !== "agent_commander").length} / {agentConfig.max_agents}
            </span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(80px, 1fr))", gap: 10, marginBottom: 16 }}>
            {allAgents.filter(a => a.agent_id !== "agent_commander").map((agent) => {
              const isSelected = selectedAgents.includes(agent.agent_id);
              const atLimit = !isSelected && selectedAgents.filter(a => a !== "agent_commander").length >= agentConfig.max_agents;
              return (
                <button
                  key={agent.agent_id}
                  onClick={() => !atLimit && toggleAgentSelection(agent.agent_id)}
                  disabled={atLimit && !isSelected}
                  data-testid={`select-agent-${agent.agent_id}`}
                  style={{
                    position: "relative", display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
                    padding: "10px 6px", borderRadius: 12, cursor: atLimit && !isSelected ? "not-allowed" : "pointer",
                    background: isSelected ? "rgba(124,58,237,.1)" : "rgba(255,255,255,.03)",
                    border: isSelected ? `1px solid rgba(124,58,237,.4)` : `1px solid ${T.border}`,
                    opacity: atLimit && !isSelected ? .4 : 1, transition: "all .15s",
                  }}
                >
                  {isSelected && (
                    <div style={{ position: "absolute", top: 5, right: 5, width: 14, height: 14, borderRadius: "50%", background: T.violet, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Check size={9} style={{ color: "#fff" }} />
                    </div>
                  )}
                  <img src={agent.avatar} alt="" style={{ width: 36, height: 36, borderRadius: 8, objectFit: "cover" }} />
                  <span style={{ fontSize: 10, color: isSelected ? "#c4b5fd" : "#e4e4e7", fontWeight: 500, textAlign: "center", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 72 }}>{agent.name}</span>
                  <span style={{ fontSize: 9, color: T.zinc, textAlign: "center", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 72 }}>{agent.role}</span>
                </button>
              );
            })}
          </div>
          <button
            onClick={saveAgentSelection}
            disabled={savingAgents}
            data-testid="save-agents-btn"
            style={{ width: "100%", padding: "11px 0", borderRadius: 12, background: `linear-gradient(135deg, ${T.violet}, #9333ea)`, border: "none", color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}
          >
            {savingAgents ? <div style={{ width: 16, height: 16, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Save size={15} />}
            Save Selection
          </button>
        </Section>
      )}

      {agentConfig?.plan_id === "custom" && (
        <Section title="Your Custom Package Agents" icon={<Users size={16} />} accent={T.amber} testId="custom-agents-info">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(80px,1fr))", gap: 10, marginBottom: 14 }}>
            {allAgents.filter(a => selectedAgents.includes(a.agent_id)).map(agent => (
              <div key={agent.agent_id} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, padding: "10px 6px", borderRadius: 12, background: "rgba(245,158,11,.06)", border: `1px solid rgba(245,158,11,.2)` }}>
                <img src={agent.avatar} alt="" style={{ width: 36, height: 36, borderRadius: 8, objectFit: "cover" }} />
                <span style={{ fontSize: 10, color: "#fff", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 72 }}>{agent.name}</span>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 12, color: T.zinc, textAlign: "center" }}>
            Custom package agents are set at purchase.{" "}
            <Link to="/pricing" style={{ color: T.amber, textDecoration: "underline" }}>Build a new package</Link> to change.
          </p>
        </Section>
      )}

      {/* Account */}
      <Section title="Account" icon={<Shield size={16} />} accent={T.red}>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { label: "User ID", value: user?.user_id, mono: true },
            { label: "AI Providers", value: "OpenAI, Anthropic, Google Gemini", badge: { color: T.green, text: "Connected" } },
          ].map(row => (
            <div key={row.label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}` }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#fff", marginBottom: 2 }}>{row.label}</div>
                <div style={{ fontSize: 12, color: T.zinc, fontFamily: row.mono ? "monospace" : "inherit" }}>{row.value}</div>
              </div>
              {row.badge && <span style={{ fontSize: 11, fontWeight: 600, background: "rgba(52,211,153,.12)", color: T.green, padding: "3px 10px", borderRadius: 8 }}>{row.badge.text}</span>}
            </div>
          ))}

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: `1px solid ${T.border}` }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#fff", marginBottom: 2 }}>Sign Out</div>
              <div style={{ fontSize: 12, color: T.zinc }}>Sign out from your MAARS account</div>
            </div>
            <button
              onClick={async () => { await logout(); navigate("/"); }}
              data-testid="logout-btn"
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 10, background: "rgba(239,68,68,.08)", border: `1px solid rgba(239,68,68,.25)`, color: T.red, fontSize: 12, fontWeight: 600, cursor: "pointer" }}
            >
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        </div>
      </Section>
    </div>
  );
};

export default SettingsPage;
