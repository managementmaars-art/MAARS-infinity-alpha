import { useCallback, useEffect, useState } from "react";
import { API } from "../../App";
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

function BalanceBar({ value, max, color }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div style={{ width: "100%", height: 6, borderRadius: 3, background: "rgba(255,255,255,0.06)", marginTop: 6 }}>
      <div style={{ width: `${pct}%`, height: "100%", borderRadius: 3, background: color, transition: "width 0.3s" }} />
    </div>
  );
}

function severityColor(balance) {
  if (balance === null || balance === undefined) return T.mute;
  if (balance > 10) return T.green;
  if (balance > 2) return T.amber;
  return T.red;
}

function tierBadge(tier) {
  const colors = {
    tier1_api: { bg: "rgba(79,209,197,0.15)", text: T.teal, label: "Live API" },
    tier2_estimated: { bg: "rgba(245,158,11,0.15)", text: T.amber, label: "Estimated" },
    free: { bg: "rgba(52,211,153,0.15)", text: T.green, label: "Free Tier" },
    unconfigured: { bg: "rgba(148,163,184,0.1)", text: T.mute, label: "No Key" },
    unknown: { bg: "rgba(248,113,113,0.15)", text: T.red, label: "Error" },
  };
  const c = colors[tier] || colors.unknown;
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 4,
      background: c.bg, color: c.text, textTransform: "uppercase", letterSpacing: 0.5
    }}>
      {c.label}
    </span>
  );
}

export default function ProviderBalancePanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [configSlug, setConfigSlug] = useState(null);
  const [configBalance, setConfigBalance] = useState("");
  const [configThreshold, setConfigThreshold] = useState("");

  const authHeaders = useCallback(() => {
    const tok = localStorage.getItem("token") || "";
    return tok ? { Authorization: `Bearer ${tok}` } : {};
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/admin/metrics/provider-balances`, { headers: authHeaders() });
      if (r.ok) setData(await r.json());
    } catch (e) {
      toast.error("Failed to load provider balances");
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => {
    setRefreshing(true);
    try {
      const r = await fetch(`${API}/admin/metrics/provider-balances/refresh`, {
        method: "POST", headers: authHeaders(),
      });
      if (r.ok) {
        toast.success("Balances refreshed & snapshot saved");
        await load();
      }
    } catch (e) {
      toast.error("Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const saveConfig = async () => {
    if (!configSlug) return;
    try {
      const body = { slug: configSlug };
      if (configBalance) body.starting_balance_usd = parseFloat(configBalance);
      if (configThreshold) body.alert_threshold_usd = parseFloat(configThreshold);
      const r = await fetch(`${API}/admin/metrics/provider-balances/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        toast.success(`Config saved for ${configSlug}`);
        setConfigSlug(null);
        setConfigBalance("");
        setConfigThreshold("");
        await load();
      }
    } catch (e) {
      toast.error("Failed to save config");
    }
  };

  if (loading && !data) {
    return <div style={{ ...card, textAlign: "center", padding: 40, color: T.mute }}>Loading provider balances...</div>;
  }

  const providers = data?.providers || [];
  const alerts = data?.alerts || [];
  const configs = data?.configs || [];
  const configured = providers.filter(p => p.tier !== "unconfigured");
  const withBalance = configured.filter(p => p.balance_usd !== null && p.balance_usd !== undefined && p.tier !== "free");

  // Sort: alerts first, then by balance ascending
  const sorted = [...configured].sort((a, b) => {
    if (a.tier === "unconfigured") return 1;
    if (b.tier === "unconfigured") return -1;
    const aBalance = a.balance_usd ?? 999;
    const bBalance = b.balance_usd ?? 999;
    return aBalance - bBalance;
  });

  return (
    <div style={{ ...card, marginTop: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>Provider Balances</h2>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: T.mute }}>
            {configured.length} providers configured | {withBalance.length} with tracked balance | {alerts.length} alert{alerts.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button onClick={refresh} disabled={refreshing}
          style={{
            padding: "8px 16px", borderRadius: 8, border: "none", cursor: "pointer",
            background: `linear-gradient(90deg, ${T.teal}, ${T.violet})`, color: "#fff",
            fontWeight: 600, fontSize: 13, opacity: refreshing ? 0.6 : 1,
          }}>
          {refreshing ? "Refreshing..." : "Refresh All"}
        </button>
      </div>

      {/* Alert banner */}
      {alerts.length > 0 && (
        <div style={{
          background: "rgba(248,113,113,0.1)", border: `1px solid rgba(248,113,113,0.3)`,
          borderRadius: 10, padding: "12px 16px", marginBottom: 16,
        }}>
          <div style={{ fontWeight: 700, color: T.red, fontSize: 14, marginBottom: 6 }}>
            Low Balance Alerts
          </div>
          {alerts.map(a => (
            <div key={a.slug} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "4px 0" }}>
              <span style={{ color: "#e6eaf2", fontSize: 13 }}>
                <span style={{ color: a.severity === "critical" ? T.red : T.amber, fontWeight: 600 }}>
                  {a.severity === "critical" ? "!!!" : "!"}{" "}
                </span>
                {a.display_name}: ${a.balance_usd?.toFixed(2)} (threshold: ${a.threshold_usd?.toFixed(2)})
              </span>
              {a.dashboard_url && (
                <a href={a.dashboard_url} target="_blank" rel="noopener noreferrer"
                  style={{ color: T.teal, fontSize: 12, textDecoration: "none", fontWeight: 600 }}>
                  Top Up
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Provider grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
        {sorted.map(p => {
          const balance = p.balance_usd;
          const color = p.tier === "free" ? T.green : severityColor(balance);
          const configEntry = configs.find(c => c.slug === p.slug);

          return (
            <div key={p.slug} style={{
              background: "rgba(255,255,255,0.03)", borderRadius: 10,
              border: `1px solid ${balance !== null && balance < 2 && p.tier !== "free" ? "rgba(248,113,113,0.3)" : T.border}`,
              padding: "14px 16px", position: "relative",
            }}>
              {/* Provider name + tier */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontWeight: 600, fontSize: 14 }}>{p.display_name}</span>
                {tierBadge(p.tier)}
              </div>

              {/* Balance */}
              {p.tier === "free" ? (
                <div style={{ color: T.green, fontSize: 22, fontWeight: 700 }}>Free</div>
              ) : balance !== null && balance !== undefined ? (
                <div style={{ color, fontSize: 22, fontWeight: 700 }}>
                  ${balance.toFixed(2)}
                  {p.unlimited && <span style={{ fontSize: 12, color: T.mute, marginLeft: 6 }}>unlimited</span>}
                </div>
              ) : p.needs_starting_balance ? (
                <div style={{ color: T.amber, fontSize: 13 }}>
                  Set starting balance to track
                </div>
              ) : (
                <div style={{ color: T.mute, fontSize: 13 }}>No balance data</div>
              )}

              {/* Burn rate + days left */}
              {p.daily_burn_usd != null && (
                <div style={{ fontSize: 11, color: T.mute, marginTop: 4 }}>
                  Burn: ${p.daily_burn_usd.toFixed(2)}/day
                  {p.days_until_empty != null && (
                    <span style={{ color: p.days_until_empty < 3 ? T.red : p.days_until_empty < 10 ? T.amber : T.green }}>
                      {" "}| {p.days_until_empty.toFixed(0)}d left
                    </span>
                  )}
                </div>
              )}

              {/* ElevenLabs character display */}
              {p.characters_remaining != null && (
                <div style={{ fontSize: 11, color: T.mute, marginTop: 4 }}>
                  {p.characters_remaining.toLocaleString()} / {p.characters_limit?.toLocaleString()} chars
                  <BalanceBar value={p.characters_remaining} max={p.characters_limit || 1} color={T.teal} />
                </div>
              )}

              {/* Action buttons */}
              <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                {p.dashboard_url && (
                  <a href={p.dashboard_url} target="_blank" rel="noopener noreferrer"
                    style={{
                      padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                      background: "rgba(79,209,197,0.1)", color: T.teal, textDecoration: "none",
                      border: `1px solid rgba(79,209,197,0.2)`,
                    }}>
                    Top Up
                  </a>
                )}
                <button onClick={() => { setConfigSlug(p.slug); setConfigBalance(configEntry?.starting_balance_usd || ""); setConfigThreshold(configEntry?.alert_threshold_usd || ""); }}
                  style={{
                    padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                    background: "rgba(255,255,255,0.04)", color: T.mute,
                    border: `1px solid ${T.border}`, cursor: "pointer",
                  }}>
                  Configure
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Config modal */}
      {configSlug && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", display: "flex",
          alignItems: "center", justifyContent: "center", zIndex: 999,
        }} onClick={() => setConfigSlug(null)}>
          <div style={{ ...card, width: 400, maxWidth: "90vw" }} onClick={e => e.stopPropagation()}>
            <h3 style={{ margin: "0 0 16px", fontSize: 18 }}>Configure: {configSlug}</h3>
            <label style={{ fontSize: 13, color: T.mute, display: "block", marginBottom: 4 }}>
              Starting Balance (USD)
            </label>
            <input type="number" step="0.01" value={configBalance} onChange={e => setConfigBalance(e.target.value)}
              placeholder="e.g. 20.00"
              style={{
                width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${T.border}`,
                background: "rgba(255,255,255,0.05)", color: "#fff", fontSize: 14, marginBottom: 12,
              }}
            />
            <label style={{ fontSize: 13, color: T.mute, display: "block", marginBottom: 4 }}>
              Alert Threshold (USD)
            </label>
            <input type="number" step="0.01" value={configThreshold} onChange={e => setConfigThreshold(e.target.value)}
              placeholder="e.g. 2.00"
              style={{
                width: "100%", padding: "8px 12px", borderRadius: 8, border: `1px solid ${T.border}`,
                background: "rgba(255,255,255,0.05)", color: "#fff", fontSize: 14, marginBottom: 16,
              }}
            />
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button onClick={() => setConfigSlug(null)}
                style={{ padding: "8px 16px", borderRadius: 8, border: `1px solid ${T.border}`, background: "transparent", color: T.mute, cursor: "pointer" }}>
                Cancel
              </button>
              <button onClick={saveConfig}
                style={{
                  padding: "8px 16px", borderRadius: 8, border: "none", cursor: "pointer",
                  background: `linear-gradient(90deg, ${T.teal}, ${T.violet})`, color: "#fff", fontWeight: 600,
                }}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
