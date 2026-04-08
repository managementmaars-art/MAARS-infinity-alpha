import { useState, useEffect, useCallback } from "react";
import {
  Key, Copy, Eye, EyeOff, RefreshCw, Search, Filter,
  Play, Send, Code2, Zap, Globe, CheckCircle2, XCircle,
  ChevronDown, Terminal, BookOpen, MessageSquare, SlidersHorizontal,
  ExternalLink, AlertTriangle, TrendingUp, Clock, Activity,
  Wallet, DollarSign, CreditCard, BarChart3, ArrowUpRight
} from "lucide-react";
import { API } from "../App";
import { useAuth } from "../App";
import { toast } from "sonner";

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
const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} }`;
const formInput = { background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" };

const PROVIDER_COLORS = {
  openai:      { bg: "rgba(52,211,153,.15)",  color: "#6ee7b7" },
  anthropic:   { bg: "rgba(249,115,22,.15)",  color: "#fdba74" },
  gemini:      { bg: "rgba(59,130,246,.15)",  color: "#93c5fd" },
  xai:         { bg: "rgba(14,165,233,.15)",  color: "#7dd3fc" },
  deepseek:    { bg: "rgba(20,184,166,.15)",  color: "#5eead4" },
  mistral:     { bg: "rgba(124,58,237,.15)",  color: "#c4b5fd" },
  groq:        { bg: "rgba(234,179,8,.15)",   color: "#fde047" },
  cerebras:    { bg: "rgba(236,72,153,.15)",  color: "#f9a8d4" },
  together:    { bg: "rgba(132,204,22,.15)",  color: "#bef264" },
  fireworks:   { bg: "rgba(239,68,68,.15)",   color: "#fca5a5" },
  perplexity:  { bg: "rgba(34,211,238,.15)",  color: "#67e8f9" },
  cohere:      { bg: "rgba(245,158,11,.15)",  color: "#fcd34d" },
  nvidia:      { bg: "rgba(34,197,94,.15)",   color: "#86efac" },
  sambanova:   { bg: "rgba(168,85,247,.15)",  color: "#d8b4fe" },
  huggingface: { bg: "rgba(202,138,4,.15)",   color: "#fde047" },
  hyperbolic:  { bg: "rgba(217,70,239,.15)",  color: "#f0abfc" },
  moonshot:    { bg: "rgba(100,116,139,.15)", color: "#cbd5e1" },
  qwen:        { bg: "rgba(244,63,94,.15)",   color: "#fda4af" },
  amazon:      { bg: "rgba(194,65,12,.15)",   color: "#fdba74" },
  minimax:     { bg: "rgba(2,132,199,.15)",   color: "#7dd3fc" },
  inception:   { bg: "rgba(162,28,175,.15)",  color: "#f0abfc" },
  arcee:       { bg: "rgba(190,18,60,.15)",   color: "#fda4af" },
  ai21:        { bg: "rgba(13,148,136,.15)",  color: "#5eead4" },
  novita:      { bg: "rgba(109,40,217,.15)",  color: "#c4b5fd" },
  lepton:      { bg: "rgba(234,88,12,.15)",   color: "#fdba74" },
  lambda:      { bg: "rgba(8,145,178,.15)",   color: "#67e8f9" },
  zhipu:       { bg: "rgba(29,78,216,.15)",   color: "#93c5fd" },
  doubao:      { bg: "rgba(185,28,28,.15)",   color: "#fca5a5" },
  llama:       { bg: "rgba(67,56,202,.15)",   color: "#a5b4fc" },
  yi:          { bg: "rgba(4,120,87,.15)",    color: "#6ee7b7" },
  writer:      { bg: "rgba(126,34,206,.15)",  color: "#d8b4fe" },
  upstage:     { bg: "rgba(77,124,15,.15)",   color: "#bef264" },
  maars:       { bg: "rgba(99,102,241,.15)",  color: "#a5b4fc" },
};

const Spinner = ({ size = 16 }) => (
  <div style={{ width: size, height: size, border: "2px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite", flexShrink: 0 }} />
);

const TABS = [
  { id: "key",        label: "My API Key",    icon: Key },
  { id: "models",     label: "Model Browser", icon: Globe },
  { id: "playground", label: "Playground",     icon: Play },
  { id: "quickstart", label: "Quickstart",     icon: Code2 },
];

export default function DeveloperPortal() {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const [tab, setTab] = useState("key");

  // ── API Key state ──────────────────────────────────────────────────────────
  const [keyInfo, setKeyInfo] = useState(null);
  const [keyLoading, setKeyLoading] = useState(true);
  const [revealed, setRevealed] = useState(false);
  const [fullKey, setFullKey] = useState("");

  // ── Model Browser state ────────────────────────────────────────────────────
  const [models, setModels] = useState([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [providerFilter, setProviderFilter] = useState("all");
  const [capFilter, setCapFilter] = useState("all");
  const [validating, setValidating] = useState({});  // modelId → "checking"|"valid"|"invalid"|{warning,suggestions}
  const [validateAll, setValidateAll] = useState(false);

  // ── Playground state ───────────────────────────────────────────────────────
  const [playModel, setPlayModel] = useState("maars/auto");
  const [playSystem, setPlaySystem] = useState("");
  const [playMessage, setPlayMessage] = useState("Explain the difference between GPT-4o and Claude Sonnet in 2 sentences.");
  const [playTemp, setPlayTemp] = useState(0.7);
  const [playMaxTokens, setPlayMaxTokens] = useState(1024);
  const [playResponse, setPlayResponse] = useState(null);
  const [playMeta, setPlayMeta] = useState(null);
  const [playLoading, setPlayLoading] = useState(false);

  // ── Load API key info ──────────────────────────────────────────────────────
  const loadKeyInfo = useCallback(async () => {
    setKeyLoading(true);
    try {
      const res = await fetch(`${API}/user/gateway-key`, { headers });
      if (res.ok) setKeyInfo(await res.json());
    } catch { toast.error("Failed to load API key"); }
    finally { setKeyLoading(false); }
  }, [token]);

  useEffect(() => { loadKeyInfo(); }, [loadKeyInfo]);

  // ── Load models ────────────────────────────────────────────────────────────
  const loadModels = useCallback(async () => {
    if (models.length > 0) return; // already loaded
    setModelsLoading(true);
    try {
      const res = await fetch(`${API}/v1/models`);
      if (res.ok) {
        const d = await res.json();
        setModels(d.data || []);
      }
    } catch { toast.error("Failed to load models"); }
    finally { setModelsLoading(false); }
  }, [models.length]);

  useEffect(() => {
    if (tab === "models") loadModels();
  }, [tab, loadModels]);

  // ── Reveal key ────────────────────────────────────────────────────────────
  const handleReveal = async () => {
    if (fullKey) { setRevealed(r => !r); return; }
    try {
      const res = await fetch(`${API}/user/gateway-key?reveal=true`, { headers });
      if (res.ok) {
        const d = await res.json();
        setFullKey(d.key_revealed || "");
        setRevealed(true);
      }
    } catch { toast.error("Failed to reveal key"); }
  };

  const copyKey = () => {
    const k = revealed && fullKey ? fullKey : keyInfo?.masked_key || "";
    navigator.clipboard.writeText(fullKey || k);
    toast.success("API key copied!");
  };

  // ── Live model validation ──────────────────────────────────────────────────
  const validateModel = async (modelId) => {
    setValidating(v => ({ ...v, [modelId]: "checking" }));
    try {
      const res = await fetch(`${API}/v1/models/validate?model=${encodeURIComponent(modelId)}`);
      const d = await res.json();
      setValidating(v => ({
        ...v,
        [modelId]: d.valid ? "valid" : { warning: d.warning, suggestions: d.suggestions || [] }
      }));
    } catch {
      setValidating(v => ({ ...v, [modelId]: "error" }));
    }
  };

  const validateAllModels = async () => {
    setValidateAll(true);
    const nonRouters = models.filter(m => !m.is_maars_router).slice(0, 50);
    for (const m of nonRouters) {
      if (!validating[m.id]) await validateModel(m.id);
    }
    setValidateAll(false);
  };

  // ── Playground send ────────────────────────────────────────────────────────
  const handlePlay = async () => {
    if (!fullKey && !keyInfo) { toast.error("Load your API key first"); return; }
    const apiKey = fullKey || "";
    if (!apiKey) {
      // Need to reveal first
      const res = await fetch(`${API}/user/gateway-key?reveal=true`, { headers });
      if (res.ok) { const d = await res.json(); setFullKey(d.key_revealed || ""); }
    }
    setPlayLoading(true);
    setPlayResponse(null);
    setPlayMeta(null);
    try {
      const msgs = [];
      if (playSystem.trim()) msgs.push({ role: "system", content: playSystem });
      msgs.push({ role: "user", content: playMessage });
      const start = Date.now();
      const res = await fetch(`${API}/v1/chat/completions`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${fullKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model: playModel, messages: msgs, temperature: playTemp, max_tokens: playMaxTokens }),
      });
      const latency = Date.now() - start;
      if (!res.ok) {
        const err = await res.json();
        toast.error(err?.error?.message || "Request failed");
        return;
      }
      const data = await res.json();
      const content = data.choices?.[0]?.message?.content || "";
      setPlayResponse(content);
      setPlayMeta({
        model:       data.x_maars?.native_model || playModel,
        provider:    data.x_maars?.actual_provider || "—",
        latency:     data.x_maars?.latency_ms || latency,
        pt:          data.usage?.prompt_tokens || 0,
        ct:          data.usage?.completion_tokens || 0,
        cost:        data.x_maars?.cost_usd || 0,
        billed:      data.x_maars?.billed_usd || data.x_maars?.cost_usd || 0,
        markup_pct:  data.x_maars?.markup_pct || 0,
        billing_mode: data.x_maars?.billing_mode || "subscription",
        remaining:   data.x_maars?.remaining_usd,
        fallback:    data.x_maars?.fallback_used,
        warning:     data.x_maars?.model_warning || null,
      });
    } catch (e) { toast.error("Error: " + e.message); }
    finally { setPlayLoading(false); }
  };

  // ── Filter models ──────────────────────────────────────────────────────────
  const providers = ["all", ...Array.from(new Set(models.map(m => m.provider).filter(Boolean))).sort()];

  const filteredModels = models.filter(m => {
    const q = search.toLowerCase();
    const matchSearch = !q || m.id?.toLowerCase().includes(q) || m.description?.toLowerCase().includes(q) || m.provider?.toLowerCase().includes(q);
    const matchProvider = providerFilter === "all" || m.provider === providerFilter;
    const matchCap = capFilter === "all"
      || (capFilter === "vision"    && !m.is_maars_router && ["openai","anthropic","gemini","xai","groq","together","fireworks","nvidia","minimax"].includes(m.provider))
      || (capFilter === "reasoning" && (m.id?.includes("r1") || m.id?.includes("/o") || m.id?.includes("reasoning") || m.id?.includes("think") || m.id?.includes("qwq")))
      || (capFilter === "code"      && (m.id?.includes("coder") || m.id?.includes("codestral") || m.id?.includes("starcoder") || m.id?.includes("devstral") || m.id?.includes("codellama")))
      || (capFilter === "fast"      && ["groq","cerebras"].includes(m.provider))
      || (capFilter === "search"    && m.provider === "perplexity")
      || (capFilter === "maars"     && m.is_maars_router);
    return matchSearch && matchProvider && matchCap;
  });

  const displayKey = revealed && fullKey ? fullKey : (keyInfo?.masked_key || "Loading...");

  return (
    <div style={{ maxWidth: 1152, margin: "0 auto", display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }}>
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg, rgba(99,102,241,.3), rgba(124,58,237,.3))", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Terminal size={20} color={T.indigo} />
        </div>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: 0 }}>MAARS Developer API</h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>One API key · 175,000+ models · 33 providers · OpenAI-compatible</p>
        </div>
        <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(52,211,153,.15)", color: "#6ee7b7" }}>
          v1 · Live
        </span>
      </div>

      {/* Tab nav */}
      <div style={{ display: "flex", gap: 4, background: "rgba(24,24,27,.5)", padding: 4, borderRadius: 12, border: `1px solid ${T.border}`, overflowX: "auto" }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 8,
            border: "none", cursor: "pointer", fontSize: 13, fontWeight: 500, whiteSpace: "nowrap", fontFamily: "inherit",
            background: tab === t.id ? "linear-gradient(90deg, #6366f1, #7c3aed)" : "transparent",
            color: tab === t.id ? "#fff" : T.zinc,
            transition: "all .2s",
          }}>
            <t.icon size={15} />
            {t.label}
          </button>
        ))}
      </div>

      {/* ── API KEY TAB ── */}
      {tab === "key" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {keyLoading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 160 }}>
              <Spinner size={24} />
            </div>
          ) : keyInfo ? (
            <>
              {/* Key card */}
              <div style={{ background: T.glass, border: "1px solid rgba(99,102,241,.2)", borderRadius: 14, overflow: "hidden" }}>
                <div style={{ padding: "20px 24px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                    <Key size={15} color={T.indigo} />
                    <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>Your MAARS API Key</h3>
                    <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: keyInfo.status === "active" ? "rgba(52,211,153,.15)" : "rgba(239,68,68,.15)", color: keyInfo.status === "active" ? "#6ee7b7" : "#fca5a5" }}>
                      {keyInfo.status}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                    <div style={{ flex: 1, background: "rgba(24,24,27,.8)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "10px 16px", fontFamily: "monospace", fontSize: 13, color: "#d4d4d8", overflowX: "auto", whiteSpace: "nowrap" }}>
                      {displayKey}
                    </div>
                    <button onClick={handleReveal} title={revealed ? "Hide" : "Reveal"} style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "8px 10px", borderRadius: 8, border: `1px solid ${T.border}`, background: "transparent", color: T.zinc, cursor: "pointer", flexShrink: 0 }}>
                      {revealed ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                    <button onClick={copyKey} title="Copy" style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "8px 10px", borderRadius: 8, border: `1px solid ${T.border}`, background: "transparent", color: T.zinc, cursor: "pointer", flexShrink: 0 }}>
                      <Copy size={15} />
                    </button>
                  </div>

                  <div style={{ padding: 12, background: "rgba(245,158,11,.1)", border: "1px solid rgba(245,158,11,.2)", borderRadius: 8, fontSize: 12, color: "#fcd34d", marginBottom: 20 }}>
                    Keep your API key secret. Never expose it in client-side code or public repositories.
                  </div>

                  {/* Billing mode badge */}
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
                    {keyInfo.billing_mode === "payg" && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(124,58,237,.2)", color: "#c4b5fd", border: "1px solid rgba(124,58,237,.3)" }}>
                        <Wallet size={11} /> Pay-As-You-Go
                      </span>
                    )}
                    {keyInfo.billing_mode === "hybrid" && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(59,130,246,.2)", color: "#93c5fd", border: "1px solid rgba(59,130,246,.3)" }}>
                        <CreditCard size={11} /> Hybrid (Subscription + PAYG)
                      </span>
                    )}
                    {(!keyInfo.billing_mode || keyInfo.billing_mode === "subscription") && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(52,211,153,.2)", color: "#6ee7b7", border: "1px solid rgba(52,211,153,.3)" }}>
                        <Zap size={11} /> Subscription
                      </span>
                    )}
                    {keyInfo.markup_pct > 0 && (
                      <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(63,63,70,.6)", color: T.zinc, border: `1px solid ${T.border}` }}>
                        {keyInfo.markup_pct}% markup applied
                      </span>
                    )}
                  </div>

                  {/* PAYG balance highlight */}
                  {(keyInfo.billing_mode === "payg" || keyInfo.billing_mode === "hybrid") && (
                    <div style={{
                      marginBottom: 16, padding: 16, borderRadius: 12, display: "flex", alignItems: "center", gap: 16,
                      background: keyInfo.balance_usd > 5 ? "rgba(124,58,237,.1)" : keyInfo.balance_usd > 0 ? "rgba(245,158,11,.1)" : "rgba(239,68,68,.1)",
                      border: `1px solid ${keyInfo.balance_usd > 5 ? "rgba(124,58,237,.3)" : keyInfo.balance_usd > 0 ? "rgba(245,158,11,.3)" : "rgba(239,68,68,.3)"}`,
                    }}>
                      <Wallet size={32} color={keyInfo.balance_usd > 5 ? "#c4b5fd" : keyInfo.balance_usd > 0 ? "#fcd34d" : "#fca5a5"} style={{ flexShrink: 0 }} />
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: 12, color: T.zinc, margin: "0 0 2px 0" }}>Prepaid Balance</p>
                        <p style={{ fontSize: 24, fontWeight: 700, color: "#fff", margin: 0 }}>${(keyInfo.balance_usd || 0).toFixed(4)}</p>
                        {keyInfo.balance_usd <= 0 && (
                          <p style={{ fontSize: 12, color: "#fca5a5", marginTop: 4, marginBottom: 0 }}>Balance depleted — contact your administrator to top up.</p>
                        )}
                        {keyInfo.balance_usd > 0 && keyInfo.balance_usd <= 5 && (
                          <p style={{ fontSize: 12, color: "#fcd34d", marginTop: 4, marginBottom: 0 }}>Low balance — consider topping up soon.</p>
                        )}
                      </div>
                      {keyInfo.billing_mode === "hybrid" && (
                        <div style={{ textAlign: "right" }}>
                          <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 2px 0" }}>Subscription Budget</p>
                          <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>
                            ${(keyInfo.used_usd || 0).toFixed(4)} / ${(keyInfo.monthly_budget_usd || 0).toFixed(2)}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Usage stats */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 12 }}>
                    {[
                      { label: "Total Calls", value: keyInfo.total_calls?.toLocaleString() || "0", icon: Activity, color: T.indigo },
                      { label: "Used This Month", value: `$${(keyInfo.used_usd || 0).toFixed(4)}`, icon: TrendingUp, color: T.amber },
                      {
                        label: keyInfo.billing_mode === "payg" ? "Balance" : "Budget",
                        value: keyInfo.billing_mode === "payg"
                          ? `$${(keyInfo.balance_usd || 0).toFixed(4)}`
                          : keyInfo.monthly_budget_usd > 0
                            ? `$${keyInfo.monthly_budget_usd.toFixed(2)}`
                            : "Unlimited",
                        icon: keyInfo.billing_mode === "payg" ? Wallet : Zap,
                        color: T.green,
                      },
                      { label: "Rate Limit", value: `${keyInfo.rpm_limit} req/min`, icon: Clock, color: T.violet },
                    ].map(s => (
                      <div key={s.label} style={{ background: "rgba(39,39,42,.6)", borderRadius: 8, padding: 12 }}>
                        <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0", display: "flex", alignItems: "center", gap: 4 }}>
                          <s.icon size={11} color={s.color} /> {s.label}
                        </p>
                        <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>{s.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Connection info */}
              <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
                <div style={{ padding: "18px 20px" }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: "0 0 16px 0", display: "flex", alignItems: "center", gap: 8 }}>
                    <Globe size={15} color={T.green} /> Connection Details
                  </h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16, fontSize: 13 }}>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Base URL</p>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <code style={{ color: T.green, background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, flex: 1, overflowX: "auto", display: "block" }}>{window.location.origin}/api</code>
                        <button onClick={() => { navigator.clipboard.writeText(`${window.location.origin}/api`); toast.success("Copied!"); }}
                          style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 2 }}>
                          <Copy size={12} />
                        </button>
                      </div>
                    </div>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Chat Completions</p>
                      <code style={{ color: "#d4d4d8", background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, display: "block", overflowX: "auto" }}>POST /v1/chat/completions</code>
                    </div>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Model List</p>
                      <code style={{ color: "#d4d4d8", background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, display: "block" }}>GET /v1/models</code>
                    </div>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Your Usage</p>
                      <code style={{ color: "#d4d4d8", background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, display: "block" }}>GET /v1/usage</code>
                    </div>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Balance (PAYG)</p>
                      <code style={{ color: "#d4d4d8", background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, display: "block" }}>GET /v1/balance</code>
                    </div>
                    <div>
                      <p style={{ fontSize: 12, color: "#52525b", margin: "0 0 4px 0" }}>Per-Model Pricing</p>
                      <code style={{ color: "#d4d4d8", background: "rgba(39,39,42,1)", padding: "3px 8px", borderRadius: 4, fontSize: 12, display: "block" }}>GET /v1/pricing</code>
                    </div>
                  </div>
                </div>
              </div>

              {/* Mini quickstart */}
              <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
                <div style={{ padding: "18px 20px" }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: "0 0 12px 0", display: "flex", alignItems: "center", gap: 8 }}>
                    <Terminal size={15} color="#c4b5fd" /> 30-Second Quickstart
                  </h3>
                  <pre style={{ background: "rgba(39,39,42,.8)", borderRadius: 8, padding: 16, fontSize: 12, color: "#d4d4d8", overflowX: "auto", lineHeight: 1.6, fontFamily: "monospace", margin: 0 }}>
{`from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="${revealed && fullKey ? fullKey : 'YOUR_MAARS_KEY'}",
)

response = client.chat.completions.create(
    model="maars/auto",     # or "openai/gpt-4o", "anthropic/claude-sonnet-4-6" ...
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)`}
                  </pre>
                </div>
              </div>
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "64px 0", color: T.zinc }}>No API key found. Contact your administrator.</div>
          )}
        </div>
      )}

      {/* ── MODEL BROWSER TAB ── */}
      {tab === "models" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Search + filters */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
              <Search size={15} color={T.zinc} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)" }} />
              <input value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search models, providers, capabilities..."
                style={{ ...formInput, paddingLeft: 32, background: "rgba(24,24,27,.5)" }}
              />
            </div>
            <select value={providerFilter} onChange={e => setProviderFilter(e.target.value)}
              style={{ ...formInput, width: "auto", cursor: "pointer", background: "rgba(24,24,27,.5)" }}>
              {providers.map(p => <option key={p} value={p}>{p === "all" ? "All Providers" : p}</option>)}
            </select>
            <select value={capFilter} onChange={e => setCapFilter(e.target.value)}
              style={{ ...formInput, width: "auto", cursor: "pointer", background: "rgba(24,24,27,.5)" }}>
              <option value="all">All Capabilities</option>
              <option value="maars">MAARS Smart Routing</option>
              <option value="vision">Vision / Multimodal</option>
              <option value="reasoning">Reasoning / Thinking</option>
              <option value="code">Code Specialist</option>
              <option value="fast">High Speed (Groq/Cerebras)</option>
              <option value="search">Web Search (Perplexity)</option>
            </select>
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>{filteredModels.length} models {search || providerFilter !== "all" || capFilter !== "all" ? "(filtered)" : `of ${models.length} total`}</p>
            <button onClick={validateAllModels} disabled={validateAll || modelsLoading}
              style={{ fontSize: 12, color: T.indigo, background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, opacity: (validateAll || modelsLoading) ? 0.4 : 1, fontFamily: "inherit" }}>
              {validateAll ? <Spinner size={12} /> : <CheckCircle2 size={12} />}
              {validateAll ? "Validating..." : "Check Live Status"}
            </button>
          </div>

          {modelsLoading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 160 }}>
              <Spinner size={24} />
            </div>
          ) : (
            <div style={{ overflowX: "auto", borderRadius: 12, border: `1px solid ${T.border}` }}>
              <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${T.border}`, background: "rgba(24,24,27,.8)" }}>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Model ID</th>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Provider</th>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Context</th>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Input $/M</th>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Output $/M</th>
                    <th style={{ padding: "10px 12px", textAlign: "left", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Live?</th>
                    <th style={{ padding: "10px 12px", textAlign: "right", fontSize: 12, color: T.zinc, fontWeight: 500 }}>Use</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredModels.map((m, i) => {
                    const pc = PROVIDER_COLORS[m.provider] || { bg: "rgba(113,113,122,.2)", color: "#d4d4d8" };
                    return (
                      <tr key={m.id} style={{ borderBottom: `1px solid rgba(255,255,255,.04)`, background: i % 2 === 0 ? "transparent" : "rgba(24,24,27,.2)", transition: "background .15s" }}>
                        <td style={{ padding: "10px 12px" }}>
                          <div style={{ fontFamily: "monospace", fontSize: 12, color: "#fff" }}>{m.id}</div>
                          <div style={{ fontSize: 10, color: "#52525b", marginTop: 2 }}>{m.description}</div>
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: pc.bg, color: pc.color }}>
                            {m.provider}
                          </span>
                        </td>
                        <td style={{ padding: "10px 12px", fontSize: 12, color: T.zinc }}>
                          {m.context_length >= 1_000_000 ? `${m.context_length/1_000_000}M` : m.context_length >= 1000 ? `${Math.round(m.context_length/1000)}K` : m.context_length}
                        </td>
                        <td style={{ padding: "10px 12px", fontSize: 12, color: T.zinc }}>
                          {m.pricing?.prompt > 0 ? `$${m.pricing.prompt}` : m.is_maars_router ? "varies" : "—"}
                        </td>
                        <td style={{ padding: "10px 12px", fontSize: 12, color: T.zinc }}>
                          {m.pricing?.completion > 0 ? `$${m.pricing.completion}` : m.is_maars_router ? "varies" : "—"}
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          {m.is_maars_router ? (
                            <span style={{ fontSize: 10, color: T.indigo }}>router</span>
                          ) : validating[m.id] === "checking" ? (
                            <Spinner size={13} />
                          ) : validating[m.id] === "valid" ? (
                            <CheckCircle2 size={13} color={T.green} title="Live on provider API" />
                          ) : validating[m.id] === "error" ? (
                            <span style={{ fontSize: 10, color: "#3f3f46" }}>err</span>
                          ) : validating[m.id]?.warning ? (
                            <span title={validating[m.id].warning + (validating[m.id].suggestions.length ? "\nSuggested: " + validating[m.id].suggestions.slice(0,3).join(", ") : "")}>
                              <XCircle size={13} color={T.red} style={{ cursor: "help" }} />
                            </span>
                          ) : (
                            <button onClick={() => validateModel(m.id)}
                              style={{ fontSize: 10, color: T.zinc, background: "none", border: "none", cursor: "pointer", fontFamily: "inherit" }}>
                              check
                            </button>
                          )}
                        </td>
                        <td style={{ padding: "10px 12px", textAlign: "right" }}>
                          <button onClick={() => { setPlayModel(m.id); setTab("playground"); }}
                            style={{ fontSize: 10, color: T.indigo, background: "none", border: "none", cursor: "pointer", fontFamily: "inherit" }}>
                            Try →
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                  {filteredModels.length === 0 && (
                    <tr><td colSpan={7} style={{ padding: 40, textAlign: "center", color: T.zinc, fontSize: 13 }}>No models match your filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── PLAYGROUND TAB ── */}
      {tab === "playground" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {!fullKey && (
            <div style={{ padding: 16, background: "rgba(245,158,11,.1)", border: "1px solid rgba(245,158,11,.3)", borderRadius: 12, fontSize: 13, color: "#fcd34d", display: "flex", alignItems: "center", gap: 12 }}>
              <AlertTriangle size={15} style={{ flexShrink: 0 }} />
              <span>Go to <button style={{ background: "none", border: "none", color: "#fcd34d", textDecoration: "underline", fontWeight: 600, cursor: "pointer", fontFamily: "inherit", fontSize: 13, padding: 0 }} onClick={() => setTab("key")}>My API Key</button> tab and click "Reveal" first to enable the playground.</span>
            </div>
          )}

          <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
            <div style={{ padding: "18px 20px", display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16 }}>
                <div>
                  <label style={{ fontSize: 12, color: T.zinc, display: "block", marginBottom: 4 }}>Model</label>
                  <input value={playModel} onChange={e => setPlayModel(e.target.value)}
                    placeholder="maars/auto or openai/gpt-4o..."
                    style={{ ...formInput, fontFamily: "monospace" }}
                  />
                  <p style={{ fontSize: 10, color: "#3f3f46", marginTop: 4, marginBottom: 0 }}>Try: maars/auto, openai/gpt-4.1, anthropic/claude-sonnet-4-6, groq/llama-4-scout...</p>
                </div>
                <div>
                  <label style={{ fontSize: 12, color: T.zinc, display: "block", marginBottom: 4 }}>Temperature: {playTemp}</label>
                  <input type="range" min="0" max="2" step="0.1" value={playTemp}
                    onChange={e => setPlayTemp(parseFloat(e.target.value))}
                    style={{ width: "100%", accentColor: T.indigo, marginTop: 8 }} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: T.zinc, display: "block", marginBottom: 4 }}>Max Tokens: {playMaxTokens}</label>
                  <input type="range" min="256" max="4096" step="256" value={playMaxTokens}
                    onChange={e => setPlayMaxTokens(parseInt(e.target.value))}
                    style={{ width: "100%", accentColor: T.indigo, marginTop: 8 }} />
                </div>
              </div>

              <div>
                <label style={{ fontSize: 12, color: T.zinc, display: "block", marginBottom: 4 }}>System Prompt (optional)</label>
                <textarea value={playSystem} onChange={e => setPlaySystem(e.target.value)} rows={2}
                  placeholder="You are a helpful assistant..."
                  style={{ ...formInput, height: 64, resize: "vertical" }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: T.zinc, display: "block", marginBottom: 4 }}>Message</label>
                <textarea value={playMessage} onChange={e => setPlayMessage(e.target.value)} rows={4}
                  placeholder="Enter your message..."
                  style={{ ...formInput, height: 96, resize: "vertical" }}
                />
              </div>

              <button onClick={handlePlay} disabled={playLoading || !playMessage.trim()}
                style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 7, padding: "10px 16px", borderRadius: 10, border: "none", background: "linear-gradient(90deg, #4f46e5, #7c3aed)", color: "#fff", fontSize: 13, fontWeight: 700, cursor: playLoading || !playMessage.trim() ? "not-allowed" : "pointer", opacity: playLoading || !playMessage.trim() ? 0.6 : 1, fontFamily: "inherit", width: "100%" }}>
                {playLoading ? <Spinner size={15} /> : <Send size={15} />}
                {playLoading ? "Generating..." : `Run with ${playModel}`}
              </button>
            </div>
          </div>

          {playResponse !== null && (
            <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
              <div style={{ padding: "18px 20px" }}>
                {playMeta?.warning && (
                  <div style={{ marginBottom: 12, padding: 12, background: "rgba(245,158,11,.1)", border: "1px solid rgba(245,158,11,.2)", borderRadius: 8, display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12, color: "#fcd34d" }}>
                    <AlertTriangle size={13} style={{ flexShrink: 0, marginTop: 1 }} />
                    <span>{playMeta.warning}</span>
                  </div>
                )}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <MessageSquare size={15} color={T.green} />
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Response</span>
                    {playMeta?.fallback && <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(245,158,11,.2)", color: "#fcd34d" }}>fallback used</span>}
                  </div>
                  {playMeta && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 12, fontSize: 12, color: T.zinc }}>
                      <span style={{ color: T.indigo, fontFamily: "monospace" }}>{playMeta.provider}/{playMeta.model?.split("/").pop()}</span>
                      <span>{playMeta.latency}ms</span>
                      <span>{playMeta.pt}↑ {playMeta.ct}↓ tokens</span>
                      <span title="Provider cost">provider: ${playMeta.cost?.toFixed(6)}</span>
                      {playMeta.markup_pct > 0 && (
                        <span style={{ color: "#c4b5fd" }} title={`Billed = provider cost × ${1 + playMeta.markup_pct/100}`}>
                          billed: ${playMeta.billed?.toFixed(6)} (+{playMeta.markup_pct}%)
                        </span>
                      )}
                      {playMeta.remaining !== undefined && (
                        <span style={{ color: playMeta.remaining < 1 ? T.red : T.green }}>
                          remaining: ${playMeta.remaining?.toFixed(4)}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <div style={{ background: "rgba(39,39,42,.8)", borderRadius: 8, padding: 16, fontSize: 13, color: "#e4e4e7", whiteSpace: "pre-wrap", fontFamily: "monospace", lineHeight: 1.6, maxHeight: 384, overflowY: "auto" }}>
                  {playResponse || <span style={{ color: T.zinc, fontStyle: "italic" }}>Empty response</span>}
                </div>
                <button onClick={() => { navigator.clipboard.writeText(playResponse); toast.success("Copied!"); }}
                  style={{ marginTop: 8, fontSize: 12, color: T.zinc, background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, fontFamily: "inherit" }}>
                  <Copy size={11} /> Copy
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── QUICKSTART TAB ── */}
      {tab === "quickstart" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {[
            {
              lang: "Python (OpenAI SDK)",
              color: "#93c5fd",
              code: `pip install openai

from openai import OpenAI

client = OpenAI(
    base_url="${window.location.origin}/api",
    api_key="YOUR_MAARS_KEY",  # maars-sk-...
)

# Use any of 175,000+ models with one key
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",   # provider/model format
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=1024,
)
print(response.choices[0].message.content)

# Smart routing — MAARS picks the best model for you
response = client.chat.completions.create(
    model="maars/auto",
    messages=[{"role": "user", "content": "Write Python code to sort a list"}],
)`,
            },
            {
              lang: "JavaScript / TypeScript",
              color: "#fde047",
              code: `npm install openai

import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "${window.location.origin}/api",
  apiKey: "YOUR_MAARS_KEY",
  dangerouslyAllowBrowser: true, // for client-side; use server-side in production
});

const response = await client.chat.completions.create({
  model: "openai/gpt-4.1",
  messages: [{ role: "user", content: "Hello!" }],
  stream: true,
});

for await (const chunk of response) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "");
}`,
            },
            {
              lang: "cURL",
              color: "#86efac",
              code: `# Chat completions
curl ${window.location.origin}/api/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_MAARS_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "maars/auto",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 512
  }'

# List all 175,000+ models (no auth required)
curl ${window.location.origin}/api/v1/models

# Your usage and budget
curl ${window.location.origin}/api/v1/usage \\
  -H "Authorization: Bearer YOUR_MAARS_KEY"`,
            },
            {
              lang: "Tool Calling / Function Calling",
              color: "#c4b5fd",
              code: `response = client.chat.completions.create(
    model="openai/gpt-4.1",  # or anthropic/claude-sonnet-4-6
    messages=[{"role": "user", "content": "What's the weather in Dhaka?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            }
        }
    }],
    tool_choice="auto",
)
# Works across OpenAI, Anthropic, Mistral — MAARS handles format translation`,
            },
            {
              lang: "MAARS Smart Routing Aliases",
              color: "#a5b4fc",
              code: `# 10 intelligent routing aliases — MAARS picks the best model automatically

"maars/auto"       → Picks best available model for your prompt
"maars/smart"      → Task-classified routing (analyzes content type)
"maars/economy"    → Cheapest capable model (Haiku, Gemini Flash, GPT-4o-mini)
"maars/standard"   → Balanced quality/cost (Sonnet, GPT-4o, Gemini Flash)
"maars/premium"    → Highest quality (Opus, GPT-4.1, Gemini 2.5 Pro)
"maars/code"       → Best coding model (Codestral, Devstral, GPT-4.1)
"maars/vision"     → Best vision model (GPT-4o, Claude, Gemini 2.5)
"maars/reasoning"  → Best reasoning (o4, R1, Claude Opus, QwQ)
"maars/search"     → Web-grounded answers (Perplexity Sonar Pro)
"maars/fast"       → Fastest response (Cerebras Llama, Groq Scout)

# Example: auto-route a coding task
response = client.chat.completions.create(
    model="maars/code",
    messages=[{"role": "user", "content": "Write a binary search tree in Rust"}],
)`,
            },
          ].map(({ lang, color, code }) => (
            <div key={lang} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
              <div style={{ padding: "18px 20px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color, margin: 0 }}>{lang}</h3>
                  <button onClick={() => { navigator.clipboard.writeText(code); toast.success("Copied!"); }}
                    style={{ fontSize: 12, color: T.zinc, background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, fontFamily: "inherit" }}>
                    <Copy size={11} /> Copy
                  </button>
                </div>
                <pre style={{ background: "rgba(39,39,42,.8)", borderRadius: 8, padding: 16, fontSize: 12, color: "#d4d4d8", overflowX: "auto", lineHeight: 1.6, fontFamily: "monospace", whiteSpace: "pre", margin: 0 }}>
                  {code}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
