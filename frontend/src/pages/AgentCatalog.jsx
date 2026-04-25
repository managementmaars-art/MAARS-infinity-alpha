import { useState, useEffect, useCallback, useMemo } from "react";
import {
  Users, Search, CheckCircle, AlertTriangle, Play, ChevronRight, X
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  cyan: "#22d3ee",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  violet: "#7c3aed",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const MATURITY_COLORS = {
  "production-ready": { color: T.green, bg: "rgba(52,211,153,.12)", border: "rgba(52,211,153,.25)" },
  "partial": { color: T.amber, bg: "rgba(245,158,11,.12)", border: "rgba(245,158,11,.25)" },
  "experimental": { color: "#a78bfa", bg: "rgba(167,139,250,.12)", border: "rgba(167,139,250,.25)" },
  "catalog-only": { color: T.zinc, bg: "rgba(113,113,122,.12)", border: "rgba(113,113,122,.25)" },
};

const maturityStyle = (m) => MATURITY_COLORS[m] || MATURITY_COLORS["production-ready"];

export default function AgentCatalog() {
  const [stats, setStats] = useState(null);
  const [networks, setNetworks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [filterNetwork, setFilterNetwork] = useState("");
  const [filterMaturity, setFilterMaturity] = useState("");
  const [filterTier, setFilterTier] = useState("");
  const [selected, setSelected] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [execResult, setExecResult] = useState(null);
  const [taskInput, setTaskInput] = useState("");
  const token = localStorage.getItem("token");
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const fetchData = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [s, n] = await Promise.all([f("/api/infinity/catalog/stats"), f("/api/infinity/catalog/networks")]);
    if (s) setStats(s);
    if (n) setNetworks(n);
  }, [headers]);

  const fetchAgents = useCallback(async () => {
    const params = new URLSearchParams({ limit: "50" });
    if (search) params.set("search", search);
    if (filterNetwork) params.set("network", filterNetwork);
    if (filterMaturity) params.set("maturity", filterMaturity);
    if (filterTier) params.set("tier", filterTier);
    const res = await fetch(`${API}/api/infinity/catalog/agents?${params}`, { headers }).catch(() => null);
    if (res?.ok) { const d = await res.json(); setAgents(d.agents || []); setTotal(d.total || 0); }
  }, [headers, search, filterNetwork, filterMaturity, filterTier]);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const selectAgent = async (agentId) => {
    setExecResult(null); setTaskInput("");
    const res = await fetch(`${API}/api/infinity/catalog/agents/${agentId}`, { headers }).catch(() => null);
    if (res?.ok) setSelected(await res.json());
  };

  const executeAgent = async () => {
    if (!selected || !taskInput.trim()) return;
    setExecuting(true); setExecResult(null);
    const res = await fetch(`${API}/api/infinity/runtime/execute`, {
      method: "POST", headers,
      body: JSON.stringify({ agent_id: selected.agent_id, task_description: taskInput, environment: "sandbox" }),
    });
    if (res.ok) setExecResult(await res.json());
    setExecuting(false);
  };

  const clearFilters = () => { setSearch(""); setFilterNetwork(""); setFilterMaturity(""); setFilterTier(""); };
  const hasFilters = search || filterNetwork || filterMaturity || filterTier;

  const selectStyle = { background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 7, padding: "5px 10px", color: "#a1a1aa", fontSize: 11, outline: "none", fontFamily: "inherit", cursor: "pointer" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18, animation: "fadeUp .4s ease" }} data-testid="agent-catalog">
      <style>{STYLES}</style>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4, display: "flex", alignItems: "center", gap: 10 }}>
            <Users size={22} style={{ color: T.indigo }} /> Agent Catalog
          </h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>{stats?.total_agents || 0} agents across {networks.length} networks — search, inspect, execute</p>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }} data-testid="catalog-stats">
          {[
            { label: "Total Agents", value: stats.total_agents, accent: T.indigo },
            { label: "Networks", value: stats.by_network?.length, accent: T.cyan },
            { label: "Autonomy Tiers", value: stats.by_tier?.length, accent: "#a78bfa" },
            { label: "Production Ready", value: stats.by_maturity?.find(m => m.maturity === "production-ready")?.count || 0, accent: T.green },
          ].map(s => (
            <div key={s.label} style={{ position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "12px 14px", textAlign: "center", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.accent }} />
              <div style={{ fontSize: 22, fontWeight: 700, color: "#fff" }}>{s.value}</div>
              <div style={{ fontSize: 10, color: T.zinc, marginTop: 2 }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "12px 14px", display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8 }} data-testid="catalog-filters">
        <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
          <Search size={12} style={{ position: "absolute", left: 9, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search agents by name, role, or ID…"
            data-testid="search-input"
            style={{ paddingLeft: 28, paddingRight: 10, paddingTop: 7, paddingBottom: 7, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }} />
        </div>
        <select value={filterNetwork} onChange={e => setFilterNetwork(e.target.value)} style={selectStyle} data-testid="filter-network">
          <option value="">All Networks</option>
          {networks.map(n => <option key={n.network_id} value={n.network_id} style={{ background: "#0f0f1a" }}>{n.name} ({n.agent_count})</option>)}
        </select>
        <select value={filterMaturity} onChange={e => setFilterMaturity(e.target.value)} style={selectStyle} data-testid="filter-maturity">
          <option value="">All Maturity</option>
          <option value="production-ready">Production Ready</option>
          <option value="partial">Partial</option>
          <option value="experimental">Experimental</option>
          <option value="catalog-only">Catalog Only</option>
        </select>
        <select value={filterTier} onChange={e => setFilterTier(e.target.value)} style={selectStyle} data-testid="filter-tier">
          <option value="">All Tiers</option>
          {[0,1,2,3,4,5].map(t => <option key={t} value={t} style={{ background: "#0f0f1a" }}>Tier {t}</option>)}
        </select>
        {hasFilters && (
          <button onClick={clearFilters} style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 10px", borderRadius: 7, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 11, cursor: "pointer" }}>
            <X size={11} /> Clear
          </button>
        )}
        <span style={{ fontSize: 10, color: T.zinc }}>{total} results</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 14 }}>
        {/* Agent list */}
        <div style={{ display: "flex", flexDirection: "column", gap: 5 }} data-testid="agent-list">
          {agents.length === 0 ? (
            <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "32px 0" }}>No agents match your filters</p>
          ) : agents.map(a => {
            const ms = maturityStyle(a.maturity);
            const isSelected = selected?.agent_id === a.agent_id;
            return (
              <div key={a.agent_id} onClick={() => selectAgent(a.agent_id)}
                data-testid={`agent-row-${a.agent_id}`}
                style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 10, border: `1px solid ${isSelected ? "rgba(34,211,238,.25)" : T.border}`, background: isSelected ? "rgba(34,211,238,.04)" : T.glass, cursor: "pointer", transition: "all .2s" }}
                onMouseEnter={e => !isSelected && (e.currentTarget.style.borderColor = "rgba(255,255,255,.13)")}
                onMouseLeave={e => !isSelected && (e.currentTarget.style.borderColor = T.border)}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(129,140,248,.12)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: T.indigo, flexShrink: 0 }}>
                  T{a.autonomy_tier}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name}</span>
                    <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 4, background: ms.bg, color: ms.color, border: `1px solid ${ms.border}`, fontWeight: 700, flexShrink: 0 }}>{a.maturity || "ready"}</span>
                  </div>
                  <p style={{ fontSize: 10, color: T.zinc, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.role} — {a.network?.replace(/_/g, " ")}</p>
                </div>
                <ChevronRight size={12} style={{ color: T.zinc, flexShrink: 0 }} />
              </div>
            );
          })}
        </div>

        {/* Detail panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }} data-testid="agent-detail-panel">
          {selected ? (
            <>
              <div style={{ background: T.glass, border: `1px solid rgba(34,211,238,.15)`, borderRadius: 12, padding: "14px 16px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                  <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>{selected.name}</span>
                  {(() => { const ms = maturityStyle(selected.maturity); return (
                    <span style={{ fontSize: 9, padding: "3px 8px", borderRadius: 5, background: ms.bg, color: ms.color, border: `1px solid ${ms.border}`, fontWeight: 700 }}>{selected.maturity || "production-ready"}</span>
                  ); })()}
                </div>
                <p style={{ fontSize: 12, color: "#a1a1aa", marginBottom: 10, lineHeight: 1.5 }}>{selected.description}</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 10 }}>
                  <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid rgba(129,140,248,.3)`, color: T.indigo }}>Tier {selected.autonomy_tier}</span>
                  <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid ${T.border}`, color: T.zinc }}>{selected.network?.replace(/_/g, " ")}</span>
                  {selected.authority_tier && <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 5, border: `1px solid rgba(245,158,11,.3)`, color: T.amber }}>{selected.authority_tier}</span>}
                </div>
                {selected.capabilities?.length > 0 && (
                  <div style={{ marginBottom: 10 }}>
                    <p style={{ fontSize: 10, color: T.zinc, marginBottom: 5 }}>Capabilities</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {selected.capabilities.map((c, i) => (
                        <span key={i} style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, border: `1px solid rgba(34,211,238,.2)`, color: T.cyan }}>{c}</span>
                      ))}
                    </div>
                  </div>
                )}
                {selected.trust_detail && (
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 10, color: T.zinc }}>Trust Score:</span>
                    <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 5, background: selected.trust_detail.score >= 60 ? "rgba(52,211,153,.1)" : "rgba(245,158,11,.1)", color: selected.trust_detail.score >= 60 ? T.green : T.amber }}>
                      {selected.trust_detail.score?.toFixed(1)}
                    </span>
                  </div>
                )}
                <p style={{ fontSize: 9, color: "rgba(113,113,122,.5)", fontFamily: "monospace", marginTop: 8 }}>{selected.agent_id}</p>
              </div>

              {/* Execute */}
              <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 10 }}>
                  <Play size={12} style={{ color: T.green }} />
                  <span style={{ fontSize: 11, fontWeight: 600, color: "#fff" }}>Execute Agent</span>
                </div>
                <textarea value={taskInput} onChange={e => setTaskInput(e.target.value)}
                  placeholder={`Give ${selected.name} a task…`}
                  style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 8, padding: "8px 10px", color: "#fff", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", resize: "none", minHeight: 54, lineHeight: 1.5 }}
                  rows={2} data-testid="task-input" />
                <button onClick={executeAgent} disabled={executing || !taskInput.trim()} data-testid="execute-agent-btn"
                  style={{ marginTop: 8, width: "100%", padding: "8px 0", borderRadius: 8, background: executing || !taskInput.trim() ? "rgba(52,211,153,.2)" : `linear-gradient(135deg, #059669, ${T.green})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: executing || !taskInput.trim() ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                  {executing ? <div style={{ width: 12, height: 12, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Play size={12} />}
                  Execute via Runtime Loop
                </button>
              </div>

              {/* Result */}
              {execResult && (
                <div style={{ background: T.glass, border: `1px solid ${execResult.status === "completed" ? "rgba(52,211,153,.2)" : "rgba(239,68,68,.2)"}`, borderRadius: 12, padding: "12px 14px" }} data-testid="exec-result">
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>Runtime Result</span>
                    <span style={{ fontSize: 9, padding: "2px 8px", borderRadius: 5, background: execResult.status === "completed" ? "rgba(52,211,153,.1)" : "rgba(239,68,68,.1)", color: execResult.status === "completed" ? T.green : T.red }}>
                      {execResult.summary?.passed}/{execResult.summary?.total} steps · {execResult.summary?.latency_ms}ms
                    </span>
                  </div>
                  {execResult.steps?.map((s, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 10, paddingBottom: 4 }}>
                      {s.status === "pass" ? <CheckCircle size={10} style={{ color: T.green }} /> : <AlertTriangle size={10} style={{ color: T.red }} />}
                      <span style={{ color: T.zinc, width: 90, flexShrink: 0 }}>{s.step}</span>
                      <span style={{ color: "#a1a1aa", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.detail}</span>
                    </div>
                  ))}
                  {execResult.output && (
                    <details style={{ marginTop: 8 }}>
                      <summary style={{ fontSize: 10, color: T.cyan, cursor: "pointer" }}>View Output</summary>
                      <pre style={{ fontSize: 10, color: "#a1a1aa", whiteSpace: "pre-wrap", marginTop: 5, padding: "8px 10px", background: "rgba(255,255,255,.03)", borderRadius: 6, maxHeight: 140, overflow: "auto" }}>{execResult.output}</pre>
                    </details>
                  )}
                </div>
              )}

              {/* Recent executions */}
              {selected.recent_executions?.length > 0 && (
                <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "12px 14px" }}>
                  <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600, marginBottom: 8 }}>Recent Executions</p>
                  {selected.recent_executions.map((e, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 10, padding: "5px 8px", borderRadius: 6, background: "rgba(255,255,255,.025)", marginBottom: 4 }}>
                      <span style={{ color: "#a1a1aa", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>{e.task}</span>
                      <span style={{ fontSize: 9, padding: "1px 7px", borderRadius: 4, background: e.status === "completed" ? "rgba(52,211,153,.1)" : "rgba(239,68,68,.1)", color: e.status === "completed" ? T.green : T.red, flexShrink: 0, marginLeft: 8 }}>{e.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "40px 20px", textAlign: "center" }}>
              <Users size={36} style={{ color: "rgba(255,255,255,.06)", marginBottom: 10 }} />
              <p style={{ fontSize: 12, color: T.zinc }}>Select an agent to inspect</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
