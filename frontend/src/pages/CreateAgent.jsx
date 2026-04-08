import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot, ArrowLeft, Plus, X, Sparkles, CreditCard, Lock, AlertTriangle } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const PLAN_ACCENT = {
  Business: T.amber, Pro: "#a78bfa", Starter: T.indigo, Free: T.zinc,
};

const PROVIDER_ACCENT = {
  openai: "#10b981", anthropic: "#f97316", gemini: "#3b82f6",
  xai: "#94a3b8", deepseek: T.indigo, mistral: "#ff7000",
  perplexity: "#8b5cf6", cohere: "#2563eb", groq: "#f55036",
  together: "#14b8a6", fireworks: "#f97316", ai21: "#06b6d4",
};

const PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "gemini", label: "Google" },
  { value: "xai", label: "xAI" },
  { value: "deepseek", label: "DeepSeek" },
  { value: "mistral", label: "Mistral" },
  { value: "perplexity", label: "Perplexity" },
  { value: "cohere", label: "Cohere" },
  { value: "groq", label: "Groq" },
  { value: "together", label: "Together AI" },
  { value: "fireworks", label: "Fireworks" },
  { value: "ai21", label: "AI21" },
];

const modelOptions = {
  openai: [
    { value: "gpt-5", label: "GPT-5 (Flagship)" },
    { value: "gpt-4o", label: "GPT-4o (Fast)" },
    { value: "gpt-4o-mini", label: "GPT-4o Mini (Economy)" },
    { value: "o3", label: "O3 (Reasoning)" },
    { value: "o3-mini", label: "O3 Mini (Light)" },
  ],
  anthropic: [
    { value: "claude-sonnet-4-5-20250929", label: "Claude Sonnet 4.5 (Flagship)" },
    { value: "claude-opus-4-5-20251101", label: "Claude Opus 4.5 (Premium)" },
    { value: "claude-haiku-4-5-20250929", label: "Claude Haiku 4.5 (Economy)" },
  ],
  gemini: [
    { value: "gemini-3-flash-preview", label: "Gemini 3 Flash (Fast)" },
    { value: "gemini-3-pro-preview", label: "Gemini 3 Pro (Flagship)" },
  ],
  xai: [
    { value: "grok-3", label: "Grok 3 (Flagship)" },
    { value: "grok-3-mini", label: "Grok 3 Mini (Fast)" },
    { value: "grok-2", label: "Grok 2 (Standard)" },
  ],
  deepseek: [
    { value: "deepseek-chat", label: "DeepSeek Chat (Standard)" },
    { value: "deepseek-reasoner", label: "DeepSeek Reasoner" },
  ],
  mistral: [
    { value: "mistral-large-latest", label: "Mistral Large (Flagship)" },
    { value: "mistral-medium-latest", label: "Mistral Medium" },
    { value: "mistral-small-latest", label: "Mistral Small (Economy)" },
  ],
  perplexity: [
    { value: "sonar", label: "Sonar (Standard)" },
    { value: "sonar-pro", label: "Sonar Pro (Advanced)" },
  ],
  cohere: [
    { value: "command-r-plus", label: "Command R+ (Flagship)" },
    { value: "command-r", label: "Command R (Standard)" },
  ],
  groq: [
    { value: "llama-4-scout-17b-16e-instruct", label: "Llama 4 Scout (Economy)" },
    { value: "llama-4-maverick-17b-128e-instruct", label: "Llama 4 Maverick (Fast)" },
    { value: "llama-3.3-70b-versatile", label: "Llama 3.3 70B (Versatile)" },
  ],
  together: [
    { value: "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", label: "Llama 4 Maverick FP8" },
    { value: "meta-llama/Llama-3.3-70B-Instruct-Turbo", label: "Llama 3.3 70B Turbo" },
    { value: "deepseek-ai/DeepSeek-R1", label: "DeepSeek R1 (Reasoning)" },
  ],
  fireworks: [
    { value: "accounts/fireworks/models/llama4-scout-instruct-basic", label: "Llama 4 Scout" },
    { value: "accounts/fireworks/models/llama4-maverick-instruct-basic", label: "Llama 4 Maverick" },
    { value: "accounts/fireworks/models/deepseek-v3", label: "DeepSeek V3" },
  ],
  ai21: [
    { value: "jamba-large-1.7", label: "Jamba Large 1.7 (Flagship)" },
    { value: "jamba-mini-1.7", label: "Jamba Mini 1.7 (Economy)" },
  ],
};

const robotAvatars = [
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-alpha&backgroundColor=1e1b4b",
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-beta&backgroundColor=1e1b4b",
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-gamma&backgroundColor=312e81",
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-delta&backgroundColor=312e81",
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-epsilon&backgroundColor=1e1b4b",
  "https://api.dicebear.com/7.x/bottts/svg?seed=maars-zeta&backgroundColor=312e81",
];

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 9, padding: "9px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const CreateAgent = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [capability, setCapability] = useState("");
  const [createInfo, setCreateInfo] = useState(null);
  const [infoLoading, setInfoLoading] = useState(true);

  const [formData, setFormData] = useState({
    name: "", description: "", role: "", system_prompt: "",
    model_provider: "openai", model_name: "gpt-5.2",
    avatar: "", capabilities: [],
  });

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/agents/create/info`, { headers });
        if (res.ok) setCreateInfo(await res.json());
      } catch {} finally { setInfoLoading(false); }
    })();
  }, []);

  const addCapability = () => {
    if (capability.trim() && !formData.capabilities.includes(capability.trim())) {
      setFormData(prev => ({ ...prev, capabilities: [...prev.capabilities, capability.trim()] }));
      setCapability("");
    }
  };

  const removeCapability = (cap) => {
    setFormData(prev => ({ ...prev, capabilities: prev.capabilities.filter(c => c !== cap) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.role || !formData.system_prompt) {
      toast.error("Please fill in all required fields");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${API}/agents`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        const agent = await response.json();
        toast.success("Agent created successfully!");
        navigate(`/chat/${agent.agent_id}`);
      } else {
        const data = await response.json();
        toast.error(data.detail || "Failed to create agent");
      }
    } catch { toast.error("Failed to create agent"); }
    finally { setLoading(false); }
  };

  const canCreate = createInfo?.can_create;
  const isBlocked = createInfo && !canCreate && !createInfo.is_admin;

  const inputFocus = e => e.target.style.borderColor = "rgba(129,140,248,.5)";
  const inputBlur = e => e.target.style.borderColor = T.border;

  return (
    <div style={{ minHeight: "100vh", background: "#030712" }} data-testid="create-agent-page">
      <style>{STYLES}</style>
      <div style={{ maxWidth: 720, margin: "0 auto", padding: "32px 24px", animation: "fadeUp .4s ease" }}>

        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <Link to="/agents" data-testid="back-to-agents"
            style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: T.zinc, textDecoration: "none", marginBottom: 16, transition: "color .2s" }}
            onMouseEnter={e => e.currentTarget.style.color = "#fff"}
            onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
            <ArrowLeft size={14} /> Back to Agents
          </Link>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 30, fontWeight: 700, color: "#fff", margin: "0 0 6px" }}>Create Custom Agent</h1>
          <p style={{ fontSize: 14, color: T.zinc, margin: 0 }}>Build a personalized AI agent tailored to your needs</p>
        </div>

        {/* Info card */}
        {!infoLoading && createInfo && (
          <div style={{ marginBottom: 24, background: isBlocked ? "rgba(239,68,68,.05)" : T.glass, border: `1px solid ${isBlocked ? "rgba(239,68,68,.3)" : T.border}`, borderRadius: 12, padding: "14px 18px" }} data-testid="create-agent-info-card">
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <CreditCard size={14} style={{ color: isBlocked ? T.red : T.indigo }} />
                <span style={{ fontSize: 13, color: "#d4d4d8" }}>Cost: <span style={{ fontWeight: 700, color: "#fff" }}>{createInfo.credit_cost} credits</span></span>
              </div>
              <div style={{ width: 1, height: 14, background: T.border }} />
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <Bot size={14} style={{ color: T.zinc }} />
                <span style={{ fontSize: 13, color: "#d4d4d8" }}>
                  {createInfo.max_custom_agents === -1 ? "Unlimited custom agents" : <>Used: <span style={{ fontWeight: 700, color: "#fff" }}>{createInfo.current_custom_count}/{createInfo.max_custom_agents}</span> slots</>}
                </span>
              </div>
              <div style={{ width: 1, height: 14, background: T.border }} />
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <Sparkles size={14} style={{ color: T.zinc }} />
                <span style={{ fontSize: 13, color: "#d4d4d8" }}>Balance: <span style={{ fontWeight: 700, color: "#fff" }}>{createInfo.credits_remaining} credits</span></span>
              </div>
              <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 5, background: `${PLAN_ACCENT[createInfo.plan_name] || T.zinc}20`, color: PLAN_ACCENT[createInfo.plan_name] || T.zinc }}>
                {createInfo.plan_name} Plan
              </span>
            </div>
            {isBlocked && (
              <div style={{ marginTop: 10, display: "flex", alignItems: "flex-start", gap: 8, padding: "10px 14px", borderRadius: 9, background: "rgba(239,68,68,.08)" }}>
                <AlertTriangle size={14} style={{ color: T.red, flexShrink: 0, marginTop: 1 }} />
                <span style={{ fontSize: 13, color: "#fca5a5" }}>
                  {createInfo.max_custom_agents === 0 ? <>Custom agents not available on Free plan. <button onClick={() => navigate("/pricing")} style={{ color: T.red, textDecoration: "underline", background: "none", border: "none", cursor: "pointer", fontSize: 13 }}>Upgrade now</button></> :
                  !createInfo.can_afford ? <>Not enough credits ({createInfo.credits_remaining}/{createInfo.credit_cost} needed). <button onClick={() => navigate("/pricing")} style={{ color: T.red, textDecoration: "underline", background: "none", border: "none", cursor: "pointer", fontSize: 13 }}>Buy credits</button></> :
                  <>Agent limit reached ({createInfo.current_custom_count}/{createInfo.max_custom_agents}). <button onClick={() => navigate("/pricing")} style={{ color: T.red, textDecoration: "underline", background: "none", border: "none", cursor: "pointer", fontSize: 13 }}>Upgrade plan</button></>}
                </span>
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24 }}>

          {/* Avatar */}
          <div>
            <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 10, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Avatar</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {robotAvatars.map((url, i) => (
                <button key={i} type="button" onClick={() => setFormData(prev => ({ ...prev, avatar: url }))} data-testid={`avatar-option-${i}`}
                  style={{ width: 60, height: 60, borderRadius: 10, overflow: "hidden", border: `2px solid ${formData.avatar === url ? T.indigo : "transparent"}`, opacity: formData.avatar === url ? 1 : 0.55, transition: "all .2s", cursor: "pointer", padding: 0 }}
                  onMouseEnter={e => e.currentTarget.style.opacity = "1"}
                  onMouseLeave={e => e.currentTarget.style.opacity = formData.avatar === url ? "1" : "0.55"}>
                  <img src={url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                </button>
              ))}
            </div>
          </div>

          {/* Name + Role */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <label htmlFor="name" style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Agent Name *</label>
              <input id="name" type="text" value={formData.name} onChange={e => setFormData(p => ({ ...p, name: e.target.value }))}
                placeholder="e.g., Project Manager AI" style={formInput} required disabled={isBlocked} data-testid="agent-name-input"
                onFocus={inputFocus} onBlur={inputBlur} />
            </div>
            <div>
              <label htmlFor="role" style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Role *</label>
              <input id="role" type="text" value={formData.role} onChange={e => setFormData(p => ({ ...p, role: e.target.value }))}
                placeholder="e.g., Project Manager" style={formInput} required disabled={isBlocked} data-testid="agent-role-input"
                onFocus={inputFocus} onBlur={inputBlur} />
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Description</label>
            <textarea id="description" value={formData.description} onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
              placeholder="Describe what this agent does…" style={{ ...formInput, minHeight: 72, resize: "vertical", lineHeight: 1.5 }} disabled={isBlocked} data-testid="agent-description-input"
              onFocus={inputFocus} onBlur={inputBlur} />
          </div>

          {/* System prompt */}
          <div>
            <label htmlFor="system_prompt" style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>System Prompt *</label>
            <textarea id="system_prompt" value={formData.system_prompt} onChange={e => setFormData(p => ({ ...p, system_prompt: e.target.value }))}
              placeholder="You are an expert AI assistant that…" style={{ ...formInput, minHeight: 140, resize: "vertical", lineHeight: 1.6, fontFamily: "monospace", fontSize: 12 }} required disabled={isBlocked} data-testid="agent-prompt-input"
              onFocus={inputFocus} onBlur={inputBlur} />
            <p style={{ fontSize: 11, color: T.zinc, marginTop: 5 }}>This defines your agent's personality and expertise</p>
          </div>

          {/* Provider + Model */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>AI Provider</label>
              <select value={formData.model_provider} onChange={e => setFormData(p => ({ ...p, model_provider: e.target.value, model_name: modelOptions[e.target.value][0].value }))}
                disabled={isBlocked} data-testid="provider-select"
                style={{ ...formInput, cursor: "pointer" }}
                onFocus={inputFocus} onBlur={inputBlur}>
                {PROVIDERS.map(p => <option key={p.value} value={p.value} style={{ background: "#0f0f1a" }}>{p.label}</option>)}
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Model</label>
              <select value={formData.model_name} onChange={e => setFormData(p => ({ ...p, model_name: e.target.value }))}
                disabled={isBlocked} data-testid="model-select"
                style={{ ...formInput, cursor: "pointer" }}
                onFocus={inputFocus} onBlur={inputBlur}>
                {(modelOptions[formData.model_provider] || []).map(m => <option key={m.value} value={m.value} style={{ background: "#0f0f1a" }}>{m.label}</option>)}
              </select>
            </div>
          </div>

          {/* Provider selection pills */}
          <div>
            <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Quick Provider</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {PROVIDERS.map(p => {
                const active = formData.model_provider === p.value;
                const accent = PROVIDER_ACCENT[p.value] || T.zinc;
                return (
                  <button key={p.value} type="button" disabled={isBlocked}
                    onClick={() => setFormData(prev => ({ ...prev, model_provider: p.value, model_name: modelOptions[p.value][0].value }))}
                    style={{ padding: "4px 12px", borderRadius: 20, border: `1px solid ${active ? accent : T.border}`, background: active ? `${accent}18` : T.glass, color: active ? accent : T.zinc, fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}>
                    {p.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Capabilities */}
          <div>
            <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Capabilities</label>
            <div style={{ display: "flex", gap: 8 }}>
              <input value={capability} onChange={e => setCapability(e.target.value)}
                placeholder="Add a capability…" style={{ ...formInput, flex: 1 }} disabled={isBlocked} data-testid="capability-input"
                onFocus={inputFocus} onBlur={inputBlur}
                onKeyPress={e => e.key === "Enter" && (e.preventDefault(), addCapability())} />
              <button type="button" onClick={addCapability} disabled={isBlocked} data-testid="add-capability-btn"
                style={{ padding: "9px 14px", borderRadius: 9, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, cursor: "pointer", display: "flex", alignItems: "center" }}>
                <Plus size={14} />
              </button>
            </div>
            {formData.capabilities.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                {formData.capabilities.map((cap, i) => (
                  <span key={i} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, padding: "4px 10px", borderRadius: 6, background: "rgba(129,140,248,.12)", color: T.indigo, border: `1px solid rgba(129,140,248,.25)` }}>
                    {cap}
                    <button type="button" onClick={() => removeCapability(cap)} data-testid={`remove-cap-${i}`}
                      style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 0, lineHeight: 1 }}
                      onMouseEnter={e => e.currentTarget.style.color = T.red}
                      onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                      <X size={10} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Submit row */}
          <div style={{ display: "flex", gap: 12, paddingTop: 8 }}>
            <button type="button" onClick={() => navigate("/agents")} data-testid="cancel-btn"
              style={{ flex: 1, padding: "11px 0", borderRadius: 10, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
              Cancel
            </button>
            <button type="submit" disabled={loading || isBlocked} data-testid="create-agent-submit-btn"
              style={{ flex: 1, padding: "11px 0", borderRadius: 10, background: loading || isBlocked ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.indigo}, ${T.violet})`, border: "none", color: "#fff", fontSize: 14, fontWeight: 700, cursor: loading || isBlocked ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 7 }}>
              {loading ? (
                <><div style={{ width: 15, height: 15, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> Creating…</>
              ) : isBlocked ? (
                <><Lock size={14} /> Upgrade to Create</>
              ) : (
                <><Sparkles size={14} /> Create Agent ({createInfo?.credit_cost || 20} credits)</>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAgent;
