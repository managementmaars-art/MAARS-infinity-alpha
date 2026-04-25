import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  teal: "#4fd1c5", violet: "#7c3aed", green: "#34d399",
  amber: "#f59e0b", red: "#f87171", blue: "#2563eb",
  mute: "#94a3b8", border: "rgba(255,255,255,0.08)", glass: "rgba(6,12,28,0.7)",
};

const card = {
  background: T.glass, borderRadius: 14, border: `1px solid ${T.border}`,
  backdropFilter: "blur(12px)", padding: 20,
};

function StatusDot({ status }) {
  const colors = { live: T.green, free_tier: T.green, free_credits: T.teal, check_dashboard: T.amber, error: T.red, no_key: T.mute };
  return <span style={{ width: 8, height: 8, borderRadius: "50%", background: colors[status] || T.mute, display: "inline-block" }} />;
}

function TierBadge({ tier }) {
  const map = {
    free: { bg: "rgba(52,211,153,0.15)", text: T.green, label: "FREE" },
    free_credits: { bg: "rgba(79,209,197,0.15)", text: T.teal, label: "FREE CREDITS" },
    trial: { bg: "rgba(245,158,11,0.15)", text: T.amber, label: "TRIAL" },
    paid: { bg: "rgba(124,58,237,0.15)", text: T.violet, label: "PAID" },
    audio: { bg: "rgba(37,99,235,0.15)", text: T.blue, label: "AUDIO" },
  };
  const c = map[tier] || map.paid;
  return (
    <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 7px", borderRadius: 4, background: c.bg, color: c.text, letterSpacing: 0.8 }}>
      {c.label}
    </span>
  );
}

export default function ProviderIntelligencePage({ embedded = false, initialTab = "providers" }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedSlug, setExpandedSlug] = useState(null);
  const [expandedPlan, setExpandedPlan] = useState(null);
  const [tab, setTab] = useState(initialTab); // providers | recommendations
  // When the parent (Universal Gateway) swaps initialTab prop (e.g. user clicks
  // Intelligence vs Package Advisor tabs at the outer level), honor the change
  // instead of staying on whatever tab was used at mount.
  useEffect(() => { setTab(initialTab); }, [initialTab]);

  const authHeaders = useCallback(() => {
    const tok = localStorage.getItem("token") || "";
    return tok ? { Authorization: `Bearer ${tok}` } : {};
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [intel, recs] = await Promise.all([
        fetch(`${API}/admin/intelligence/providers`, { headers: authHeaders() }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/admin/intelligence/recommendations`, { headers: authHeaders() }).then(r => r.ok ? r.json() : null),
      ]);
      setData(intel);
      setRecommendations(recs);
    } catch (e) {
      toast.error("Failed to load provider intelligence");
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => {
    if (!embedded && !user?.is_admin) navigate("/dashboard");
    else load();
  }, [user, navigate, load, embedded]);

  const refresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API}/admin/intelligence/refresh`, { method: "POST", headers: authHeaders() });
      await load();
      toast.success("Intelligence refreshed from live APIs");
    } catch (e) {
      toast.error("Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const providers = (data?.providers || []).filter(p => p.has_key);
  const unconfigured = (data?.providers || []).filter(p => !p.has_key);
  const summary = recommendations?.summary || {};
  const pkgRecs = recommendations?.package_recommendations || [];
  const planAdvice = recommendations?.plan_advice || [];

  const outerStyle = embedded
    ? { color: "#e6eaf2" }
    : { minHeight: "100vh", background: "#04070f", color: "#e6eaf2", padding: 40 };

  return (
    <div style={outerStyle}>
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>

        {/* Header - only show when standalone */}
        {!embedded && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700 }}>Provider Intelligence</h1>
            <p style={{ margin: "6px 0 0", color: T.mute, fontSize: 14 }}>
              Live data from {providers.length} provider APIs | {data?.total_models || 0} models accessible
            </p>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => setTab("providers")}
              style={{ padding: "8px 16px", borderRadius: 8, border: tab === "providers" ? "none" : `1px solid ${T.border}`, background: tab === "providers" ? `linear-gradient(90deg, ${T.teal}, ${T.violet})` : "transparent", color: "#fff", fontWeight: 600, fontSize: 13, cursor: "pointer" }}>
              Providers
            </button>
            <button onClick={() => setTab("recommendations")}
              style={{ padding: "8px 16px", borderRadius: 8, border: tab === "recommendations" ? "none" : `1px solid ${T.border}`, background: tab === "recommendations" ? `linear-gradient(90deg, ${T.teal}, ${T.violet})` : "transparent", color: "#fff", fontWeight: 600, fontSize: 13, cursor: "pointer" }}>
              Package Advisor
            </button>
            <button onClick={refresh} disabled={refreshing}
              style={{ padding: "8px 16px", borderRadius: 8, border: "none", cursor: "pointer", background: "rgba(79,209,197,0.15)", color: T.teal, fontWeight: 600, fontSize: 13, opacity: refreshing ? 0.5 : 1 }}>
              {refreshing ? "Refreshing..." : "Refresh Live"}
            </button>
          </div>
        </div>
        )}

        {/* Refresh button when embedded */}
        {embedded && (
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
            <button onClick={refresh} disabled={refreshing}
              style={{ padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer", background: "rgba(79,209,197,0.15)", color: T.teal, fontWeight: 600, fontSize: 12, opacity: refreshing ? 0.5 : 1 }}>
              {refreshing ? "Refreshing..." : "Refresh Live Data"}
            </button>
          </div>
        )}

        {/* Summary bar */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginBottom: 24 }}>
          {[
            { label: "Providers", value: providers.length, color: T.teal },
            { label: "Models", value: data?.total_models || 0, color: T.violet },
            { label: "Free Tier", value: summary.providers_free_tier || 0, color: T.green },
            { label: "With Balance", value: summary.providers_with_balance || 0, color: T.amber },
            { label: "Budget", value: `$${(summary.total_estimated_budget_usd || 0).toFixed(0)}`, color: T.blue },
          ].map(s => (
            <div key={s.label} style={{ ...card, padding: "14px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: T.mute, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 4 }}>{s.label}</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>

        {loading && !data ? (
          <div style={{ ...card, textAlign: "center", padding: 60, color: T.mute }}>
            Querying {providers.length || "all"} provider APIs for live data...
          </div>
        ) : tab === "providers" ? (
          <>
            {/* Provider cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 14 }}>
              {providers.map(p => {
                const bal = p.balance || {};
                const isExpanded = expandedSlug === p.slug;
                const balStatus = bal.status;
                const hasLiveBalance = balStatus === "live";
                const isFree = p.tier === "free" || p.tier === "free_credits";

                return (
                  <div key={p.slug} style={{
                    ...card, padding: 0, overflow: "hidden", cursor: "pointer",
                    border: `1px solid ${p.status === "error" ? "rgba(248,113,113,0.3)" : T.border}`,
                  }} onClick={() => setExpandedSlug(isExpanded ? null : p.slug)}>

                    {/* Card header */}
                    <div style={{ padding: "14px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <StatusDot status={balStatus} />
                        <span style={{ fontWeight: 700, fontSize: 15 }}>{p.display_name}</span>
                        <TierBadge tier={p.tier || p.category} />
                      </div>
                      <span style={{ fontSize: 12, color: T.teal, fontWeight: 600 }}>{p.model_count} models</span>
                    </div>

                    {/* Balance row */}
                    <div style={{ padding: "0 16px 12px", display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <div>
                        {hasLiveBalance && bal.balance_usd != null ? (
                          <span style={{ fontSize: 22, fontWeight: 700, color: bal.balance_usd > 5 ? T.green : bal.balance_usd > 1 ? T.amber : T.red }}>
                            ${bal.balance_usd.toFixed(2)}
                          </span>
                        ) : hasLiveBalance && bal.characters_remaining != null ? (
                          <span style={{ fontSize: 18, fontWeight: 700, color: T.teal }}>
                            {bal.characters_remaining.toLocaleString()} chars
                          </span>
                        ) : isFree ? (
                          <span style={{ fontSize: 18, fontWeight: 700, color: T.green }}>Free Tier</span>
                        ) : (
                          <span style={{ fontSize: 13, color: T.amber }}>
                            {bal.note || "Check dashboard"}
                          </span>
                        )}
                      </div>
                      {p.dashboard_url && (
                        <a href={p.dashboard_url} target="_blank" rel="noopener noreferrer"
                          onClick={e => e.stopPropagation()}
                          style={{ fontSize: 11, color: T.teal, textDecoration: "none", fontWeight: 600, padding: "3px 8px", borderRadius: 5, background: "rgba(79,209,197,0.1)", border: `1px solid rgba(79,209,197,0.2)` }}>
                          Dashboard
                        </a>
                      )}
                    </div>

                    {/* Expanded: model list + details */}
                    {isExpanded && (
                      <div style={{ borderTop: `1px solid ${T.border}`, padding: 16, background: "rgba(0,0,0,0.2)" }}>
                        {/* Balance details */}
                        {hasLiveBalance && (
                          <div style={{ marginBottom: 12 }}>
                            <div style={{ fontSize: 11, color: T.mute, textTransform: "uppercase", marginBottom: 4, fontWeight: 600 }}>Balance Details</div>
                            {Object.entries(bal).filter(([k]) => !["status", "note"].includes(k)).map(([k, v]) => (
                              <div key={k} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, padding: "2px 0" }}>
                                <span style={{ color: T.mute }}>{k.replace(/_/g, " ")}</span>
                                <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>{typeof v === "number" ? v.toLocaleString() : String(v)}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Rate limits */}
                        {p.rate_limits && (
                          <div style={{ marginBottom: 12 }}>
                            <div style={{ fontSize: 11, color: T.mute, textTransform: "uppercase", marginBottom: 4, fontWeight: 600 }}>Rate Limits</div>
                            {Object.entries(p.rate_limits).filter(([k]) => k !== "note").map(([k, v]) => (
                              <div key={k} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, padding: "2px 0" }}>
                                <span style={{ color: T.mute }}>{k.replace(/_/g, " ")}</span>
                                <span>{typeof v === "number" ? v.toLocaleString() : v}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Models list */}
                        <div style={{ fontSize: 11, color: T.mute, textTransform: "uppercase", marginBottom: 6, fontWeight: 600 }}>
                          Available Models ({p.model_count})
                        </div>
                        <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexWrap: "wrap", gap: 4 }}>
                          {(p.models || []).slice(0, 50).map((m, i) => (
                            <span key={i} style={{
                              fontSize: 10, padding: "2px 6px", borderRadius: 4,
                              background: "rgba(79,209,197,0.08)", color: T.teal,
                              border: `1px solid rgba(79,209,197,0.15)`,
                              fontFamily: "'JetBrains Mono', monospace",
                            }}>
                              {m.id || m.name || m.display_name || JSON.stringify(m)}
                            </span>
                          ))}
                          {(p.models || []).length > 50 && (
                            <span style={{ fontSize: 10, color: T.mute }}>+{p.models.length - 50} more</span>
                          )}
                        </div>

                        {p.note && (
                          <div style={{ fontSize: 11, color: T.mute, marginTop: 8, fontStyle: "italic" }}>{p.note}</div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Unconfigured providers */}
            {unconfigured.length > 0 && (
              <div style={{ ...card, marginTop: 24 }}>
                <h3 style={{ margin: "0 0 12px", fontSize: 16 }}>Unconfigured Providers ({unconfigured.length})</h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {unconfigured.map(p => (
                    <a key={p.slug} href={p.dashboard_url} target="_blank" rel="noopener noreferrer"
                      style={{ fontSize: 12, padding: "4px 10px", borderRadius: 6, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: T.mute, textDecoration: "none" }}>
                      {p.display_name}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          /* Advisor tab — operator split = profit margin */
          <div>
            {/* Key insight */}
            <div style={{ ...card, marginBottom: 20, background: "linear-gradient(135deg, rgba(79,209,197,0.08), rgba(124,58,237,0.08))", borderLeft: `3px solid ${T.teal}` }}>
              <h3 style={{ margin: "0 0 6px", fontSize: 18, color: T.teal }}>Your Operator Split = Your Profit Margin</h3>
              <p style={{ margin: 0, fontSize: 13, color: "#c4c9d4", lineHeight: 1.7 }}>
                Your smart router sends ~70% of traffic to <strong style={{ color: T.green }}>6 free-tier providers</strong> at $0 cost.
                The remaining 30% routes to cheap providers (DeepSeek, Together, Fireworks) at ~$0.50/1M tokens.
                Your real cost to serve each customer is <strong style={{ color: T.green }}>near zero</strong>.
                This means your <strong style={{ color: "#fff" }}>operator split percentage IS your profit margin</strong> — you keep it all.
              </p>
            </div>

            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
              {[
                { label: "Providers Live", value: summary.total_providers_with_keys || 0, color: T.teal },
                { label: "Free Providers", value: summary.providers_free_tier || 0, sub: "($0 routing cost)", color: T.green },
                { label: "Models Available", value: summary.total_models_accessible || 0, color: T.violet },
                { label: "Provider Budget", value: `$${(summary.total_estimated_budget_usd || 0).toFixed(0)}`, sub: "for paid routing only", color: T.blue },
              ].map(s => (
                <div key={s.label} style={{ ...card, padding: "14px 16px" }}>
                  <div style={{ fontSize: 11, color: T.mute, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 4 }}>{s.label}</div>
                  <div style={{ fontSize: 26, fontWeight: 700, color: s.color }}>{s.value}</div>
                  {s.sub && <div style={{ fontSize: 10, color: T.mute, marginTop: 2 }}>{s.sub}</div>}
                </div>
              ))}
            </div>

            {/* ── Advisor Initiative — proactive plan-improvement suggestions ── */}
            {planAdvice.length > 0 && (
              <div style={{ ...card, borderColor: "rgba(79,209,197,0.25)", background: "linear-gradient(135deg, rgba(79,209,197,0.04), rgba(124,58,237,0.04))" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 18 }}>💡</span>
                  <h2 style={{ margin: 0, fontSize: 18, color: T.teal }}>Advisor — Plan Improvement Suggestions</h2>
                  <span style={{ fontSize: 11, color: T.mute }}>
                    · {planAdvice.length} signal{planAdvice.length !== 1 ? "s" : ""} from live provider costs
                  </span>
                </div>
                <div style={{ display: "grid", gap: 10 }}>
                  {planAdvice.map((a, i) => {
                    const sev = a.severity || "info";
                    const styles = {
                      critical: { bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.3)", accent: T.red, tag: "CRITICAL" },
                      warn:     { bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.3)", accent: T.amber, tag: "WARN" },
                      info:     { bg: "rgba(79,209,197,0.06)", border: "rgba(79,209,197,0.25)", accent: T.teal, tag: "SUGGEST" },
                      success:  { bg: "rgba(52,211,153,0.08)", border: "rgba(52,211,153,0.3)", accent: T.green, tag: "OK" },
                    }[sev] || {};
                    return (
                      <div key={i} style={{ padding: "10px 14px", borderRadius: 10, background: styles.bg, border: `1px solid ${styles.border}` }}>
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                              <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 6px", borderRadius: 4, background: styles.border, color: styles.accent, letterSpacing: 0.8 }}>{styles.tag}</span>
                              <span style={{ fontSize: 13, fontWeight: 600, color: "#e6eaf2" }}>{a.title}</span>
                            </div>
                            <div style={{ fontSize: 11, color: T.mute, lineHeight: 1.5 }}>{a.detail}</div>
                            {a.suggested_price_usd != null && (
                              <div style={{ fontSize: 11, marginTop: 6, color: styles.accent }}>
                                → Suggested price: <strong>${a.suggested_price_usd}</strong>
                              </div>
                            )}
                            {a.suggested_plan && (
                              <div style={{ fontSize: 11, marginTop: 6, color: styles.accent, fontFamily: "ui-monospace,monospace" }}>
                                → {JSON.stringify(a.suggested_plan).replace(/[{}"]/g, "").replace(/,/g, " · ")}
                              </div>
                            )}
                          </div>
                          {a.action && (
                            <button
                              onClick={() => {
                                // Deep-link to pricing manager with a hash anchor. The manager
                                // can choose to pre-expand the relevant plan or open the new-plan dialog.
                                if (a.action === "add_plan" || a.action === "add_preset") {
                                  window.location.href = "/admin/pricing-manager#add-plan";
                                } else if (a.plan_id) {
                                  window.location.href = `/admin/pricing-manager#plan-${a.plan_id}`;
                                } else {
                                  window.location.href = "/admin/pricing-manager";
                                }
                              }}
                              style={{
                                padding: "6px 12px", borderRadius: 6, border: `1px solid ${styles.border}`,
                                background: "transparent", color: styles.accent, fontSize: 11, fontWeight: 600,
                                cursor: "pointer", whiteSpace: "nowrap",
                              }}
                            >
                              {a.action === "raise_price" ? "Raise price" :
                               a.action === "add_plan" || a.action === "add_preset" ? "Add plan" :
                               a.action === "review" ? "Review" : "Open"} ↗
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Package profitability table — same data as Pricing Command Center */}
            <div style={{ ...card }}>
              <h2 style={{ margin: "0 0 4px", fontSize: 20 }}>Package Profitability</h2>
              <p style={{ margin: "0 0 16px", color: T.mute, fontSize: 13 }}>
                AI Cost = credits × blended cost per credit (client's strict cap). Profit = Price - AI Cost.
                {pkgRecs[0]?.blended_cost_per_credit != null && (
                  <span style={{ color: T.teal }}> Live cost: ${pkgRecs[0].blended_cost_per_credit.toFixed(6)}/credit</span>
                )}
              </p>

              <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 800 }}>
                <thead>
                  <tr style={{ borderBottom: `2px solid ${T.border}` }}>
                    {["Package", "Price", "Credits", "AI Cost (cap)", "Profit", "Margin", "Capacity", ""].map(h => (
                      <th key={h} style={{ padding: "10px 12px", textAlign: "left", fontSize: 10, textTransform: "uppercase", color: T.mute, letterSpacing: 0.8, fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pkgRecs.map(r => {
                    const bd = r.operator_breakdown || {};
                    const uc = bd.usage_capacity || {};
                    const isOpen = expandedPlan === r.plan_id;
                    return (
                    <React.Fragment key={r.plan_id}>
                    <tr style={{ borderBottom: isOpen ? "none" : `1px solid ${T.border}`, cursor: "pointer", transition: "background 0.2s" }}
                      onClick={() => setExpandedPlan(isOpen ? null : r.plan_id)}
                      onMouseEnter={e => e.currentTarget.style.background = "rgba(79,209,197,0.03)"}
                      onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                      <td style={{ padding: "12px", fontWeight: 600, fontSize: 14 }}>
                        {r.plan_name}
                        <span style={{ fontSize: 10, color: T.mute, marginLeft: 6 }}>{isOpen ? "▲" : "▼"}</span>
                      </td>
                      <td style={{ padding: "12px", fontSize: 15, fontWeight: 600 }}>${r.price_usd}</td>
                      <td style={{ padding: "12px", fontFamily: "'JetBrains Mono', monospace", fontSize: 12 }}>
                        {r.credits?.toLocaleString()}
                      </td>
                      <td style={{ padding: "12px", color: T.amber, fontSize: 13, fontFamily: "'JetBrains Mono', monospace" }}>
                        ${r.ai_cost?.toFixed(2)}
                      </td>
                      <td style={{ padding: "12px" }}>
                        <span style={{ color: r.profit > 0 ? T.green : T.red, fontWeight: 700, fontSize: 18 }}>${r.profit?.toFixed(2)}</span>
                      </td>
                      <td style={{ padding: "12px" }}>
                        <span style={{
                          fontSize: 12, fontWeight: 700, padding: "2px 8px", borderRadius: 4,
                          background: r.margin_pct > 1000 ? "rgba(52,211,153,0.15)" : r.margin_pct > 100 ? "rgba(79,209,197,0.15)" : "rgba(245,158,11,0.15)",
                          color: r.margin_pct > 1000 ? T.green : r.margin_pct > 100 ? T.teal : T.amber,
                        }}>
                          {r.margin_pct > 10000 ? "∞" : `${r.margin_pct}%`}
                        </span>
                      </td>
                      <td style={{ padding: "12px" }}>
                        <span style={{ fontSize: 16, fontWeight: 700, color: r.customers_supportable > 100 ? T.green : r.customers_supportable > 10 ? T.teal : T.amber }}>
                          {r.customers_supportable > 999 ? "999+" : r.customers_supportable}
                        </span>
                      </td>
                      <td style={{ padding: "12px" }}>
                        {r.profitable ? (
                          <span style={{ color: "#04070f", background: T.green, fontWeight: 700, fontSize: 10, padding: "3px 10px", borderRadius: 4 }}>PROFITABLE</span>
                        ) : (
                          <span style={{ color: "#04070f", background: T.red, fontWeight: 700, fontSize: 10, padding: "3px 10px", borderRadius: 4 }}>LOSS</span>
                        )}
                      </td>
                    </tr>
                    {/* Operator-only breakdown (expanded) */}
                    {isOpen && bd && (
                    <tr style={{ borderBottom: `1px solid ${T.border}` }}>
                      <td colSpan={8} style={{ padding: "0 12px 16px", background: "rgba(79,209,197,0.02)" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 16, padding: "12px 0" }}>
                          {/* Credits → Tokens */}
                          <div style={{ padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                            <div style={{ fontSize: 10, color: T.teal, textTransform: "uppercase", fontWeight: 700, marginBottom: 8, letterSpacing: 0.5 }}>Credits → Tokens</div>
                            <div style={{ fontSize: 12, color: "#c4c9d4", lineHeight: 1.8 }}>
                              <div><span style={{ color: T.mute }}>Credits:</span> <strong>{r.credits?.toLocaleString()}</strong></div>
                              <div><span style={{ color: T.mute }}>Tokens/credit:</span> <strong>{bd.tokens_per_credit}</strong></div>
                              <div><span style={{ color: T.mute }}>Total tokens:</span> <strong style={{ color: T.teal }}>{bd.total_tokens?.toLocaleString()}</strong></div>
                              <div><span style={{ color: T.mute }}>Daily budget:</span> {bd.daily_credits} credits / {bd.daily_tokens?.toLocaleString()} tokens</div>
                            </div>
                          </div>
                          {/* Client Can Do — Chat */}
                          <div style={{ padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                            <div style={{ fontSize: 10, color: T.violet, textTransform: "uppercase", fontWeight: 700, marginBottom: 8, letterSpacing: 0.5 }}>Client Can Do — Chat &amp; Content</div>
                            <div style={{ fontSize: 12, color: "#c4c9d4", lineHeight: 1.8 }}>
                              <div><span style={{ color: T.mute }}>Short chats:</span> <strong>{uc.short_chats?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>~200 tok ea</span></div>
                              <div><span style={{ color: T.mute }}>Code completions:</span> <strong>{uc.code_completions?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>~300 tok ea</span></div>
                              <div><span style={{ color: T.mute }}>Long generations:</span> <strong>{uc.long_generations?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>~1000 tok ea</span></div>
                              <div><span style={{ color: T.mute }}>Doc summaries:</span> <strong>{uc.document_summaries?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>~800 tok ea</span></div>
                            </div>
                          </div>
                          {/* Media Capacity — NEW */}
                          {(() => {
                            const mc = bd.media_capacity || {};
                            const mco = bd.media_costs || {};
                            const videoWarn = mc.video_incapable === true;
                            return (
                              <div style={{ padding: 12, borderRadius: 8, background: "rgba(168,85,247,0.05)", border: `1px solid rgba(168,85,247,0.18)` }}>
                                <div style={{ fontSize: 10, color: "#c084fc", textTransform: "uppercase", fontWeight: 700, marginBottom: 8, letterSpacing: 0.5 }}>Client Can Do — Media (Images / Video / Audio)</div>
                                <div style={{ fontSize: 12, color: "#c4c9d4", lineHeight: 1.8 }}>
                                  <div><span style={{ color: T.mute }}>Images (standard):</span> <strong style={{ color: T.teal }}>{mc.images_standard?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>{mco.image_std_credits} cr each · Gemini/gpt-image-1</span></div>
                                  <div><span style={{ color: T.mute }}>Images (HD):</span> <strong style={{ color: T.teal }}>{mc.images_hd?.toLocaleString()}</strong> <span style={{ fontSize: 10, color: T.mute }}>{mco.image_hd_credits} cr each · DALL-E-3</span></div>
                                  <div style={{ color: videoWarn ? T.red : "#818cf8" }}>
                                    <span style={{ color: T.mute }}>Video (Sora-2):</span> <strong>{mc.video_seconds}</strong> sec <span style={{ fontSize: 10, color: T.mute }}>({mc.video_clips_4sec} × 4-sec clips · {mco.video_credits_per_sec} cr/sec)</span>
                                    {videoWarn && <span style={{ fontSize: 10, marginLeft: 6, color: T.red, fontWeight: 700 }}>{" "}⚠ cannot afford 1 clip</span>}
                                  </div>
                                  <div><span style={{ color: T.mute }}>TTS (standard):</span> <strong style={{ color: "#c084fc" }}>{mc.tts_minutes?.toLocaleString()}</strong> min <span style={{ fontSize: 10, color: T.mute }}>{mco.tts_credits_per_min} cr/min · OpenAI tts-1</span></div>
                                  <div><span style={{ color: T.mute }}>Voice-over (HD):</span> <strong style={{ color: "#c084fc" }}>{mc.voiceover_minutes?.toLocaleString()}</strong> min <span style={{ fontSize: 10, color: T.mute }}>{mco.voiceover_credits_per_min} cr/min · tts-1-hd / ElevenLabs</span></div>
                                  <div><span style={{ color: T.mute }}>Transcription (STT):</span> <strong style={{ color: "#e879f9" }}>{mc.stt_minutes?.toLocaleString()}</strong> min <span style={{ fontSize: 10, color: T.mute }}>{mco.stt_credits_per_min} cr/min · Whisper</span></div>
                                </div>
                              </div>
                            );
                          })()}
                          {/* Strict Cap */}
                          <div style={{ padding: 12, borderRadius: 8, background: "rgba(248,113,113,0.05)", border: `1px solid rgba(248,113,113,0.15)` }}>
                            <div style={{ fontSize: 10, color: T.red, textTransform: "uppercase", fontWeight: 700, marginBottom: 8, letterSpacing: 0.5 }}>Strict Cap</div>
                            <div style={{ fontSize: 12, color: "#c4c9d4", lineHeight: 1.8 }}>
                              <div><strong style={{ color: T.red }}>{r.credits?.toLocaleString()} credits/month</strong></div>
                              <div style={{ fontSize: 11, color: T.mute, marginTop: 4 }}>Client cannot exceed this. When credits run out, API returns 402. No overages, no surprise costs.</div>
                              <div style={{ fontSize: 11, color: T.amber, marginTop: 4 }}>Your max exposure: <strong>${r.ai_cost?.toFixed(2)}</strong></div>
                            </div>
                          </div>
                        </div>

                        {/* ── Smart Per-Category Allocation ──────────────
                            Each plan's total credit grant splits across
                            the 8 dedicated tracks at operator-set ratios.
                            Cost per track = credits × dedicated rate
                            (no merging, no averaging). Gives the operator
                            a ground-truth "out of N credits, X go to code
                            and cost me $Y" signal. */}
                        {r.per_category && (
                          <div style={{
                            marginTop: 6,
                            padding: 14,
                            borderRadius: 10,
                            background: "rgba(79,209,197,0.04)",
                            border: `1px solid rgba(79,209,197,0.18)`,
                          }}>
                            <div style={{ fontSize: 10, color: T.teal, textTransform: "uppercase", fontWeight: 700, marginBottom: 10, letterSpacing: 0.5, display: "flex", alignItems: "center", gap: 8 }}>
                              Smart Allocation — {r.credits?.toLocaleString()} credits split across 8 dedicated tracks
                              <span style={{ color: T.mute, fontSize: 10, fontWeight: 400, textTransform: "none", letterSpacing: 0, marginLeft: "auto" }}>
                                Total LLM cost: <strong style={{ color: T.teal }}>${r.per_category_cost_total?.toFixed(4)}</strong>
                                {r.allow_general_fallback && <span style={{ color: T.green, marginLeft: 8 }}>· fallback ON</span>}
                                {!r.allow_general_fallback && <span style={{ color: T.amber, marginLeft: 8 }}>· hard caps</span>}
                              </span>
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
                              {[
                                ["chat",      "Chat",        T.teal,  "#4fd1c5"],
                                ["code",      "Code / Vibe", T.violet,"#a78bfa"],
                                ["image_std", "Image Std",   T.green, "#fda4af"],
                                ["image_hd",  "Image HD",    "#e879f9","#e879f9"],
                                ["video",     "Video",       T.amber, "#fbbf24"],
                                ["voiceover", "Voiceover",   T.blue,  "#38bdf8"],
                                ["tts",       "TTS",         "#22d3ee","#22d3ee"],
                                ["stt",       "STT",         "#2dd4bf","#2dd4bf"],
                              ].map(([key, label, bg, fg]) => {
                                const cat = r.per_category[key] || {};
                                const pct = r.credits > 0 ? (cat.credits_allocated / r.credits) * 100 : 0;
                                return (
                                  <div key={key} style={{
                                    padding: "8px 10px",
                                    borderRadius: 8,
                                    background: `${fg}0a`,
                                    border: `1px solid ${fg}30`,
                                  }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 4 }}>
                                      <span style={{ fontSize: 10, fontWeight: 700, color: fg, textTransform: "uppercase", letterSpacing: 0.5 }}>
                                        {label}
                                      </span>
                                      <span style={{ fontSize: 9, color: T.mute }}>{pct.toFixed(1)}%</span>
                                    </div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>
                                      {cat.credits_allocated?.toLocaleString() || 0}
                                      <span style={{ fontSize: 9, color: T.mute, fontWeight: 400, marginLeft: 4 }}>cr</span>
                                    </div>
                                    <div style={{ fontSize: 9, color: T.mute, marginTop: 4, fontFamily: "'JetBrains Mono', monospace" }}>
                                      @ ${cat.rate?.toFixed(8) || "0.00000000"} = <strong style={{ color: cat.cost_usd > 0 ? T.amber : T.mute }}>
                                        {cat.cost_usd > 0 ? `$${cat.cost_usd.toFixed(4)}` : "free"}
                                      </strong>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                            {r.per_category_deliverables && (
                              <div style={{ marginTop: 10, padding: "8px 10px", borderRadius: 6, background: "rgba(0,0,0,0.25)", fontSize: 10, color: "#c4c9d4", lineHeight: 1.6 }}>
                                <span style={{ color: T.mute, textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 600, marginRight: 6 }}>Client delivers:</span>
                                <span style={{ color: T.teal }}>{typeof r.per_category_deliverables.chat_msgs === "number" ? r.per_category_deliverables.chat_msgs.toLocaleString() : r.per_category_deliverables.chat_msgs}</span> chats ·{" "}
                                <span style={{ color: T.violet }}>{typeof r.per_category_deliverables.code_runs === "number" ? r.per_category_deliverables.code_runs.toLocaleString() : r.per_category_deliverables.code_runs}</span> code runs ·{" "}
                                <span style={{ color: "#e879f9" }}>{typeof r.per_category_deliverables.hd_images === "number" ? r.per_category_deliverables.hd_images.toLocaleString() : r.per_category_deliverables.hd_images}</span> HD images ·{" "}
                                <span style={{ color: T.amber }}>{typeof r.per_category_deliverables.video_clips === "number" ? r.per_category_deliverables.video_clips.toLocaleString() : r.per_category_deliverables.video_clips}</span> video clips ·{" "}
                                <span style={{ color: T.blue }}>{typeof r.per_category_deliverables.vo_minutes === "number" ? r.per_category_deliverables.vo_minutes.toLocaleString() : r.per_category_deliverables.vo_minutes}</span> min VO
                              </div>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                    )}
                    </React.Fragment>
                  );})}
                </tbody>
              </table>
              </div>

              {pkgRecs.length === 0 && (
                <div style={{ padding: 24, textAlign: "center", color: T.mute }}>No paid packages configured yet. Go to Plans tab to create packages.</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
