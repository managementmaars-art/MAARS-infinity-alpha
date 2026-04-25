import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Wallet, Zap, TrendingDown, Plus, ArrowDown, ArrowUp, RefreshCw, Shield, Activity } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BUCKETS, getPool, fmtCredits } from "../lib/bucketMeta";

/* ─── palette (matches Dashboard.jsx tokens) ────────────────────────────── */
const T = {
  teal:    "#4fd1c5",
  violet:  "#7c3aed",
  blue:    "#2563eb",
  green:   "#34d399",
  amber:   "#f59e0b",
  red:     "#f87171",
  mute:    "#94a3b8",
  border:  "rgba(255,255,255,0.08)",
  border2: "rgba(255,255,255,0.14)",
  glass:   "rgba(6,12,28,0.7)",
  glass2:  "rgba(8,16,32,0.85)",
};

const entryColor = {
  CREDIT:     T.green,
  RESERVE:    T.amber,
  RELEASE:    T.teal,
  DEBIT:      T.red,
  REFUND:     T.blue,
  ADJUSTMENT: T.violet,
};

const entryIcon = (type) => {
  if (type === "CREDIT" || type === "REFUND" || type === "RELEASE") return <ArrowUp size={14} />;
  if (type === "DEBIT" || type === "RESERVE") return <ArrowDown size={14} />;
  return <Activity size={14} />;
};

const fmt = (ts) => {
  if (!ts) return "—";
  try { return new Date(ts).toLocaleString(); } catch { return ts; }
};

export default function WalletDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [wallet, setWallet] = useState(null);
  const [ledger, setLedger] = useState([]);
  const [loading, setLoading] = useState(true);

  const authHeaders = useCallback(() => {
    const tok = localStorage.getItem("token") || "";
    return tok ? { Authorization: `Bearer ${tok}` } : {};
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [cRes, lRes] = await Promise.all([
        fetch(`${API}/v1/credits`, { headers: authHeaders() }),
        fetch(`${API}/v1/usage/ledger?limit=30`, { headers: authHeaders() }),
      ]);
      if (cRes.ok) setWallet(await cRes.json());
      if (lRes.ok) setLedger((await lRes.json()).data || []);
    } catch (e) {
      toast.error(`Failed to load wallet: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => {
    if (!user) navigate("/login");
    else load();
  }, [user, navigate, load]);

  return (
    <div style={{ minHeight: "100vh", background: "#04070f", color: "#e6eaf2", padding: 40 }}>
      <div style={{ maxWidth: 1180, margin: "0 auto" }}>
        {/* ── header ───────────────────────────────────────── */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: -0.3 }}>Wallet & Usage</h1>
            <p style={{ margin: "6px 0 0", color: T.mute, fontSize: 14 }}>
              Credits, reservations, and a full audit trail of your account activity.
            </p>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <button onClick={load}
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", borderRadius: 8,
                       background: "transparent", border: `1px solid ${T.border2}`, color: "#e6eaf2", cursor: "pointer" }}>
              <RefreshCw size={14} /> Refresh
            </button>
            <button onClick={() => navigate("/api-keys")}
              style={{ padding: "8px 14px", borderRadius: 8, border: `1px solid ${T.border2}`,
                       background: T.glass, color: "#e6eaf2", cursor: "pointer" }}>
              Manage API Keys
            </button>
            <button onClick={() => navigate("/pricing")}
              style={{ padding: "8px 14px", borderRadius: 8, border: "none",
                       background: `linear-gradient(90deg, ${T.teal}, ${T.violet})`, color: "#04070f",
                       fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
              <Plus size={14} /> Top Up
            </button>
          </div>
        </div>

        {/* ── balance tiles ───────────────────────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 28 }}>
          <Tile
            icon={<Wallet size={18} />} accent={T.teal} label="Available"
            value={wallet ? Number(wallet.balance_credits || 0).toLocaleString() : "—"}
            sub={wallet ? `${wallet.unit} · status: ${wallet.status}` : ""}
          />
          <Tile
            icon={<Shield size={18} />} accent={T.amber} label="Held in reserve"
            value={wallet ? Number(wallet.reserved_credits || 0).toLocaleString() : "—"}
            sub="Credits pending in-flight inference"
          />
          <Tile
            icon={<TrendingDown size={18} />} accent={T.violet} label="Recent debits"
            value={ledger.filter(e => e.type === "DEBIT").slice(0, 50).reduce((n, e) => n + (e.amount_credits || 0), 0).toLocaleString()}
            sub="Last 30 ledger entries"
          />
        </div>

        {/* ── Per-bucket balance strip ─────────────────────────────
            Each of the 6 dedicated pools + general fallback. Clients
            who've bought category-tagged top-ups (e.g., "Code Top-Up"
            on the pricing page) will see those credits land in the
            matching bucket — the router debits the right bucket on
            each call based on the deliverable type. Clicking any
            bucket routes to /pricing with that category tab pre-
            selected so the top-up flow is one click away. */}
        {wallet?.buckets && (
          <div style={{
            marginBottom: 28,
            background: T.glass,
            border: `1px solid ${T.border}`,
            borderRadius: 14,
            padding: 20,
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <div style={{ color: "#fff", fontSize: 14, fontWeight: 600 }}>
                Credits by Category
                <span style={{ marginLeft: 10, fontSize: 11, color: T.mute, fontWeight: 400 }}>
                  6 dedicated pools + general fallback
                </span>
              </div>
              <div style={{ fontSize: 11, color: T.mute }}>
                {wallet?.allow_general_fallback
                  ? <span style={{ color: T.green }}>Fallback enabled — over-cap flows to general</span>
                  : <span style={{ color: T.amber }}>Hard caps — buy category top-up when empty</span>}
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10 }}>
              {BUCKETS.map(b => {
                // getPool reads wallet.buckets[key]; guard against the
                // wallet object being passed by mistake (no top-level
                // chat/vibe keys → returns zeros).
                const pool = getPool(wallet?.buckets, b.key);
                const hex = b.accent === "teal" ? T.teal :
                            b.accent === "violet" ? T.violet :
                            b.accent === "blue" ? T.blue :
                            b.accent === "green" ? T.green :
                            b.accent === "amber" ? T.amber :
                            b.accent === "red" ? T.red : T.mute;
                const lowBalance = pool.balance > 0 && pool.balance < 10;
                return (
                  <div
                    key={b.key}
                    onClick={() => navigate(`/pricing?topup=${b.key === "vibe" ? "code" : b.key}`)}
                    style={{
                      padding: 12,
                      borderRadius: 10,
                      background: `${hex}0a`,
                      border: `1px solid ${hex}33`,
                      cursor: "pointer",
                      transition: "all .15s",
                      position: "relative",
                    }}
                    title={b.hint}
                    onMouseOver={(e) => e.currentTarget.style.background = `${hex}15`}
                    onMouseOut={(e) => e.currentTarget.style.background = `${hex}0a`}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                      <b.icon size={12} color={hex} />
                      <span style={{ fontSize: 10, fontWeight: 600, color: hex, textTransform: "uppercase", letterSpacing: 0.5 }}>
                        {b.label}
                      </span>
                    </div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#fff", fontVariantNumeric: "tabular-nums" }}>
                      {fmtCredits(pool.balance)}
                    </div>
                    <div style={{ fontSize: 10, color: T.mute, marginTop: 2 }}>
                      {pool.reserved > 0 ? `${pool.reserved} reserved · ` : ""}credits
                    </div>
                    {lowBalance && (
                      <div style={{
                        position: "absolute", top: 8, right: 8,
                        padding: "2px 6px", borderRadius: 999,
                        background: T.amber + "22", color: T.amber,
                        fontSize: 9, fontWeight: 700,
                      }}>LOW</div>
                    )}
                  </div>
                );
              })}
            </div>
            <div style={{ marginTop: 10, fontSize: 11, color: T.mute, lineHeight: 1.5 }}>
              Each pool is dedicated to one workload. Router debits the matching bucket per call — code runs drain the Code pool,
              image generations drain the Images pool, etc. Click any pool to buy a targeted top-up for that category.
            </div>
          </div>
        )}

        {/* ── This period's credit quota (UNIFIED client view) ──
            One number: the client's hard cap for the period. Spendable
            on any model across all providers. The router picks the
            cheapest capable provider per call automatically. No
            per-modality sub-budgets. */}
        {wallet?.credits && (
          <div style={{
            marginBottom: 28,
            background: T.glass2,
            border: `1px solid ${T.border2}`,
            borderRadius: 14,
            padding: 24,
            position: "relative",
            overflow: "hidden",
          }}>
            <div style={{ position: "absolute", inset: 0, background: `radial-gradient(900px 200px at 0% 0%, ${T.teal}18, transparent 60%)`, pointerEvents: "none" }} />
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 16, position: "relative" }}>
              <div>
                <div style={{ color: T.mute, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 600 }}>
                  Credits Remaining · {wallet.credits.plan_name}
                </div>
                <div style={{ marginTop: 8, display: "flex", alignItems: "baseline", gap: 10 }}>
                  <span style={{ fontSize: 48, fontWeight: 700, color: T.teal, fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>
                    {Number(wallet.credits.credits_remaining).toLocaleString(undefined, {maximumFractionDigits: 2})}
                  </span>
                  <span style={{ fontSize: 16, color: T.mute, fontVariantNumeric: "tabular-nums" }}>
                    / {Number(wallet.credits.credits_quota).toLocaleString()} this period
                  </span>
                </div>
              </div>
              <div style={{ textAlign: "right", color: T.mute, fontSize: 12 }}>
                <div>{(wallet.credits.total_calls || 0).toLocaleString()} calls</div>
                {wallet.credits.period_end && (() => {
                  try {
                    const days = Math.max(0, Math.ceil((new Date(wallet.credits.period_end) - Date.now()) / 86400000));
                    return <div style={{ marginTop: 4 }}>Renews in {days === 0 ? "today" : days === 1 ? "tomorrow" : `${days}d`}</div>;
                  } catch { return null; }
                })()}
              </div>
            </div>
            {/* Progress bar */}
            <div style={{ height: 8, background: "rgba(255,255,255,0.06)", borderRadius: 4, overflow: "hidden", position: "relative" }}>
              <div style={{
                height: "100%",
                width: `${Math.min(100, wallet.credits.pct_used || 0)}%`,
                background: (wallet.credits.pct_used || 0) >= 90 ? T.red : (wallet.credits.pct_used || 0) >= 75 ? T.amber : T.teal,
                transition: "width .3s",
              }} />
            </div>
            <div style={{ marginTop: 12, color: T.mute, fontSize: 12, position: "relative" }}>
              {(wallet.credits.pct_used || 0).toFixed(1)}% used — credits work everywhere: chat, app builds, images, videos, voice, transcription. Router picks the cheapest capable model automatically.
            </div>
          </div>
        )}

        {/* ── ledger table ────────────────────────────────── */}
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
          <div style={{ padding: "14px 20px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
            <Zap size={16} color={T.teal} />
            <div style={{ fontWeight: 600 }}>Recent activity</div>
            <div style={{ marginLeft: "auto", color: T.mute, fontSize: 12 }}>
              {loading ? "loading…" : `${ledger.length} entries`}
            </div>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ color: T.mute, textAlign: "left" }}>
                  <th style={th}>Type</th>
                  <th style={th}>Amount</th>
                  <th style={th}>Reference</th>
                  <th style={th}>Description</th>
                  <th style={th}>When</th>
                </tr>
              </thead>
              <tbody>
                {ledger.map((e) => (
                  <tr key={e.entry_id} style={{ borderTop: `1px solid ${T.border}` }}>
                    <td style={td}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "3px 8px",
                                     borderRadius: 999, background: `${entryColor[e.type] || T.mute}22`,
                                     color: entryColor[e.type] || T.mute, fontWeight: 600, fontSize: 11 }}>
                        {entryIcon(e.type)} {e.type}
                      </span>
                    </td>
                    <td style={{ ...td, fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>
                      {(e.amount_credits || 0).toLocaleString()}
                    </td>
                    <td style={{ ...td, color: T.mute, fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>
                      {e.reference_id?.slice(0, 32) || "—"}
                    </td>
                    <td style={{ ...td, color: "#cfd6e2" }}>{e.description || "—"}</td>
                    <td style={{ ...td, color: T.mute, whiteSpace: "nowrap" }}>{fmt(e.created_at)}</td>
                  </tr>
                ))}
                {!loading && ledger.length === 0 && (
                  <tr>
                    <td colSpan="5" style={{ padding: 40, textAlign: "center", color: T.mute }}>
                      No wallet activity yet. Start a chat or call the API to see your ledger populate.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

const th = { padding: "10px 20px", fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 500 };
const td = { padding: "10px 20px" };

function Tile({ icon, accent, label, value, sub }) {
  return (
    <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: 20, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(600px 120px at 0% 0%, ${accent}22, transparent 60%)`, pointerEvents: "none" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, color: accent, marginBottom: 10 }}>
        {icon}
        <span style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 600 }}>{label}</span>
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, fontVariantNumeric: "tabular-nums", marginBottom: 4 }}>{value}</div>
      <div style={{ color: T.mute, fontSize: 12 }}>{sub}</div>
    </div>
  );
}
