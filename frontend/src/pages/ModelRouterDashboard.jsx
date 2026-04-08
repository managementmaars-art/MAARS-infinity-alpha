import { useState } from "react";
import {
  Brain, Zap, Clock, ArrowRight, Search, Play, Loader2,
  FileText, Coins, Network, Cpu, BarChart3, Sparkles, ChevronRight
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── Design tokens ─────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  green:  "#34d399",
  amber:  "#f59e0b",
  red:    "#f87171",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
};

const PROVIDER_ACCENT = {
  openai:     "#10b981",
  anthropic:  "#f97316",
  google:     "#3b82f6",
  gemini:     "#3b82f6",
  groq:       "#f55036",
  deepseek:   "#4fd1c5",
  xai:        "#94a3b8",
  perplexity: "#8b5cf6",
  mistral:    "#ff7000",
  cohere:     "#39594d",
  together:   "#22c55e",
  default:    T.teal,
};

const provColor = (p = "") => PROVIDER_ACCENT[p.toLowerCase()] || PROVIDER_ACCENT.default;

const TASK_EXAMPLES = [
  "Analyze competitor pricing strategies for a SaaS product",
  "Write a Python function to process and validate JSON payloads",
  "Create a legal NDA template between two technology companies",
  "Translate this marketing copy into French and Spanish",
  "Explain the mathematics behind transformer attention mechanisms",
  "Summarize the key findings from this 50-page research report",
  "Generate a comprehensive SEO strategy for an e-commerce site",
  "Debug this React component with performance issues",
];

const TASK_TYPE_COLORS = {
  coding:          T.teal,
  research:        "#60a5fa",
  legal_compliance:"#f472b6",
  math_forecasting:"#a78bfa",
  creative:        "#f59e0b",
  summary:         "#34d399",
  real_time:       "#06b6d4",
  data_analysis:   "#818cf8",
  translation:     "#e879f9",
  security:        T.red,
  general:         "#64748b",
};

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes mr_fadeUp  { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
  @keyframes mr_spin    { to { transform: rotate(360deg); } }
  @keyframes mr_pulse   { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(1.5); } }
  @keyframes mr_flow    { 0% { background-position:0% 50%; } 100% { background-position:200% 50%; } }
  @keyframes mr_bar     { 0%,100% { transform:scaleY(0.4); } 50% { transform:scaleY(1); } }
`;

export default function ModelRouterDashboard() {
  const [query, setQuery]         = useState("");
  const [result, setResult]       = useState(null);
  const [execResult, setExecResult] = useState(null);
  const [routing, setRouting]     = useState(false);
  const [executing, setExecuting] = useState(false);
  const [history, setHistory]     = useState([]);
  const token   = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const routeTask = async () => {
    if (!query.trim()) return;
    setRouting(true); setExecResult(null);
    try {
      const res  = await fetch(`${API}/api/infinity/router/route`, { method: "POST", headers, body: JSON.stringify({ task_description: query }) });
      const data = await res.json();
      setResult(data);
      setHistory(prev => [{ query, ...data, ts: Date.now() }, ...prev.slice(0, 9)]);
    } catch (e) { console.error(e); }
    setRouting(false);
  };

  const executeTask = async () => {
    if (!query.trim()) return;
    setExecuting(true);
    try {
      const res  = await fetch(`${API}/api/infinity/router/execute`, { method: "POST", headers, body: JSON.stringify({ task_description: query }) });
      const data = await res.json();
      setExecResult(data);
      if (data.routing) { setResult(data.routing); setHistory(prev => [{ query, ...data.routing, ts: Date.now() }, ...prev.slice(0, 9)]); }
    } catch (e) { console.error(e); }
    setExecuting(false);
  };

  const taskType   = result?.classification?.task_type || "";
  const typeColor  = TASK_TYPE_COLORS[taskType] || "#64748b";
  const selProv    = result?.selection?.provider || "";
  const pColor     = provColor(selProv);

  return (
    <div data-testid="model-router-page" style={{ maxWidth: 900, animation: "mr_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 28 }}>
        <div style={{ width: 48, height: 48, borderRadius: 14, background: "linear-gradient(135deg, rgba(124,58,237,0.25), rgba(79,209,197,0.15))", border: "1px solid rgba(124,58,237,0.25)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 24px rgba(124,58,237,0.15)" }}>
          <Brain style={{ width: 22, height: 22, color: T.violet }} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
            <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Model Router Intelligence</h1>
            <span style={{ padding: "2px 8px", borderRadius: 20, background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.2)", color: T.violet, fontSize: 9, fontWeight: 700, letterSpacing: "0.1em" }}>AI-POWERED</span>
          </div>
          <p style={{ fontSize: 12, color: "#475569", margin: 0 }}>Task-aware, cost-efficient model selection across 33 providers and 175k+ models</p>
        </div>
        {/* waveform */}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 3 }}>
          {[0,1,2,3,4].map(i => (
            <div key={i} style={{ width: 3, height: 14, borderRadius: 2, background: T.violet, animation: `mr_bar 0.7s ease-in-out ${i * 0.1}s infinite`, opacity: 0.6 }} />
          ))}
        </div>
      </div>

      {/* ── Query input ─────────────────────────────────────────────────── */}
      <div style={{ borderRadius: 18, padding: 1.5, background: `linear-gradient(135deg, rgba(124,58,237,0.3), rgba(79,209,197,0.15))`, marginBottom: 20 }}>
        <div style={{ borderRadius: 16, background: T.glass, backdropFilter: "blur(20px)", padding: 20 }} data-testid="route-input-card">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Sparkles style={{ width: 14, height: 14, color: T.violet }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Describe your task</span>
            <span style={{ fontSize: 10, color: "#334155", marginLeft: "auto" }}>The router will intelligently select the optimal model</span>
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <input
              data-testid="route-query-input"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && routeTask()}
              placeholder="e.g. 'Analyze competitor pricing strategies' or 'Write a Python parser'..."
              style={{ flex: 1, height: 46, paddingLeft: 14, paddingRight: 14, borderRadius: 11, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#e2e8f0", fontSize: 13, outline: "none", transition: "border-color 0.15s", fontFamily: "inherit" }}
              onFocus={e => e.target.style.borderColor = "rgba(124,58,237,0.4)"}
              onBlur={e => e.target.style.borderColor = T.border}
            />
            <button
              onClick={routeTask}
              disabled={routing || !query.trim()}
              data-testid="route-btn"
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "0 16px", borderRadius: 11, background: routing ? "rgba(124,58,237,0.1)" : "rgba(124,58,237,0.15)", border: "1px solid rgba(124,58,237,0.25)", color: T.violet, fontSize: 12, fontWeight: 700, cursor: routing || !query.trim() ? "default" : "pointer", opacity: !query.trim() ? 0.5 : 1, transition: "all 0.2s", minWidth: 90 }}>
              {routing ? <Loader2 style={{ width: 13, height: 13, animation: "mr_spin 1s linear infinite" }} /> : <Search style={{ width: 13, height: 13 }} />}
              Route
            </button>
            <button
              onClick={executeTask}
              disabled={executing || !query.trim()}
              data-testid="execute-btn"
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "0 18px", borderRadius: 11, background: executing || !query.trim() ? "rgba(79,209,197,0.06)" : `linear-gradient(135deg, ${T.teal}, ${T.blue})`, border: "none", color: executing || !query.trim() ? T.teal : "#030712", fontSize: 12, fontWeight: 700, cursor: executing || !query.trim() ? "default" : "pointer", opacity: !query.trim() ? 0.5 : 1, transition: "all 0.2s", minWidth: 100, whiteSpace: "nowrap" }}>
              {executing ? <Loader2 style={{ width: 13, height: 13, animation: "mr_spin 1s linear infinite" }} /> : <Play style={{ width: 13, height: 13 }} />}
              Execute
            </button>
          </div>
          {/* Starter examples */}
          {!result && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
              {TASK_EXAMPLES.slice(0, 4).map((ex, i) => (
                <button key={i} onClick={() => setQuery(ex)}
                  style={{ padding: "4px 10px", borderRadius: 20, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: "#475569", fontSize: 10, cursor: "pointer", transition: "all 0.15s", fontFamily: "inherit" }}
                  onMouseEnter={e => { e.currentTarget.style.color = "#94a3b8"; e.currentTarget.style.borderColor = "rgba(124,58,237,0.25)"; e.currentTarget.style.background = "rgba(124,58,237,0.06)"; }}
                  onMouseLeave={e => { e.currentTarget.style.color = "#475569"; e.currentTarget.style.borderColor = T.border; e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}>
                  {ex.length > 45 ? ex.substring(0, 45) + "…" : ex}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Routing result ──────────────────────────────────────────────── */}
      {result && (
        <div data-testid="route-result-card" style={{ borderRadius: 16, background: T.glass, border: `1px solid rgba(124,58,237,0.2)`, backdropFilter: "blur(16px)", padding: 20, marginBottom: 16, animation: "mr_fadeUp 0.25s ease" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Network style={{ width: 14, height: 14, color: T.violet }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Routing Decision</span>
          </div>

          {/* Classification → Selection flow */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
            {/* Classification */}
            <div style={{ flex: 1, padding: "12px 14px", borderRadius: 12, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
              <p style={{ fontSize: 9, color: "#475569", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 8px" }}>Classification</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {[
                  { label: result.classification?.task_type, color: typeColor },
                  { label: result.classification?.difficulty, color: "#64748b" },
                  { label: `${result.classification?.risk_level} risk`, color: result.classification?.risk_level === "high" ? T.red : "#64748b" },
                ].filter(b => b.label).map((b, i) => (
                  <span key={i} style={{ padding: "2px 8px", borderRadius: 20, background: `${b.color}14`, border: `1px solid ${b.color}25`, color: b.color, fontSize: 10, fontWeight: 600 }}>{b.label}</span>
                ))}
              </div>
            </div>

            <ArrowRight style={{ width: 18, height: 18, color: "#334155", flexShrink: 0 }} />

            {/* Selected model */}
            <div style={{ flex: 1, padding: "12px 14px", borderRadius: 12, background: `${pColor}06`, border: `1px solid ${pColor}22` }}>
              <p style={{ fontSize: 9, color: "#475569", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 8px" }}>Selected Model</p>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: pColor, boxShadow: `0 0 6px ${pColor}88`, animation: "mr_pulse 2s ease-in-out infinite" }} />
                  <span style={{ fontSize: 11, fontWeight: 700, color: pColor }}>{selProv}</span>
                </div>
                <span style={{ fontSize: 13, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>{result.selection?.model}</span>
                <span style={{ padding: "1px 6px", borderRadius: 5, background: "rgba(255,255,255,0.05)", border: `1px solid ${T.border}`, color: "#475569", fontSize: 9, fontWeight: 600 }}>{result.selection?.tier}</span>
              </div>
            </div>
          </div>

          {/* Stat row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
            {[
              { icon: <Zap style={{ width: 13, height: 13, color: T.amber }} />,    label: "Latency",     value: result.selection?.latency_class || "—", color: T.amber },
              { icon: <Coins style={{ width: 13, height: 13, color: T.green }} />,  label: "Credits",     value: `${result.selection?.credits_per_call ?? "~1"}/call`, color: T.green },
              { icon: <Brain style={{ width: 13, height: 13, color: T.violet }} />, label: "Match Reason",value: result.selection?.reason?.split(":")[0] || "—", color: T.violet },
            ].map((s, i) => (
              <div key={i} style={{ padding: "10px 12px", borderRadius: 10, background: "rgba(255,255,255,0.02)", border: `1px solid ${T.border}`, textAlign: "center" }}>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 5 }}>{s.icon}</div>
                <p style={{ fontSize: 11, fontWeight: 700, color: s.color, margin: "0 0 2px" }}>{s.value}</p>
                <p style={{ fontSize: 9, color: "#475569", margin: 0 }}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Execution result ─────────────────────────────────────────────── */}
      {execResult && (
        <div data-testid="exec-result-card" style={{ borderRadius: 16, background: T.glass, border: `1px solid rgba(52,211,153,0.2)`, backdropFilter: "blur(16px)", padding: 20, marginBottom: 16, animation: "mr_fadeUp 0.25s ease" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <FileText style={{ width: 14, height: 14, color: T.green }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Execution Output</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              {execResult.execution?.provider && (
                <span style={{ padding: "2px 8px", borderRadius: 20, background: `${provColor(execResult.execution.provider)}14`, border: `1px solid ${provColor(execResult.execution.provider)}25`, color: provColor(execResult.execution.provider), fontSize: 10, fontWeight: 600 }}>
                  {execResult.execution.provider}
                </span>
              )}
              {execResult.execution?.model && (
                <span style={{ fontSize: 11, fontWeight: 700, color: "#e2e8f0" }}>{execResult.execution.model}</span>
              )}
              {execResult.execution?.latency_ms && (
                <span style={{ padding: "1px 6px", borderRadius: 5, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#475569", fontSize: 9 }}>{execResult.execution.latency_ms}ms</span>
              )}
            </div>
          </div>
          <div style={{ borderRadius: 12, background: "rgba(3,7,18,0.8)", border: `1px solid ${T.border}`, padding: "14px 16px", maxHeight: 280, overflowY: "auto" }}>
            <pre style={{ fontSize: 12, color: "#94a3b8", fontFamily: "'Fira Code', 'JetBrains Mono', monospace", lineHeight: 1.7, margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {execResult.output}
            </pre>
          </div>
        </div>
      )}

      {/* ── Routing history ──────────────────────────────────────────────── */}
      {history.length > 0 && (
        <div data-testid="route-history-card" style={{ borderRadius: 16, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(16px)", padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Clock style={{ width: 13, height: 13, color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0" }}>Routing History</span>
            <span style={{ fontSize: 10, color: "#334155" }}>({history.length} recent)</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {history.map((h, i) => {
              const hProv = h.selection?.provider || "";
              const hColor = provColor(hProv);
              const htColor = TASK_TYPE_COLORS[h.classification?.task_type] || "#64748b";
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 10, background: "rgba(255,255,255,0.02)", border: `1px solid ${T.border}`, cursor: "pointer", transition: "border-color 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
                  onClick={() => { setQuery(h.query); setResult(h); }}>
                  <span style={{ padding: "1px 7px", borderRadius: 20, background: `${htColor}12`, color: htColor, border: `1px solid ${htColor}20`, fontSize: 9, fontWeight: 700, flexShrink: 0 }}>{h.classification?.task_type}</span>
                  <span style={{ flex: 1, fontSize: 11, color: "#64748b", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{h.query}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 5, flexShrink: 0 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: hColor }} />
                    <span style={{ fontSize: 10, fontWeight: 600, color: "#94a3b8" }}>{hProv}/{h.selection?.model?.split("-").slice(-2).join("-")}</span>
                  </div>
                  <ChevronRight style={{ width: 11, height: 11, color: "#334155", flexShrink: 0 }} />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
