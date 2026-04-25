/**
 * Treasury Auto-Pilot — the operator's "I only see profits" page.
 *
 * One render answers: net profit, where it came from, what it cost,
 * which client / category / model drove it, and whether any cost
 * lever needs flipping. Backed by /api/admin/treasury/auto-pilot
 * which consolidates revenue, treasury split, per-category P&L,
 * per-client P&L, per-model spend, lever status, and provider
 * low-balance alerts into a single payload.
 *
 * The operator's stated mental model: pay clients money in, send
 * profit to the bank, never touch provider invoices manually. This
 * page is the dashboard that proves the automation is doing its job.
 */
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  TrendingUp, DollarSign, AlertTriangle, RefreshCw, ArrowUpRight,
  Wallet, Activity, Users, Package, Server, Shield,
} from "lucide-react";

const T = {
  bg:      "#030712",
  panel:   "rgba(8,16,32,0.85)",
  border:  "rgba(255,255,255,0.08)",
  border2: "rgba(255,255,255,0.14)",
  teal:    "#4fd1c5",
  green:   "#34d399",
  amber:   "#fbbf24",
  rose:    "#f87171",
  violet:  "#a78bfa",
  blue:    "#38bdf8",
  zinc:    "#94a3b8",
  white:   "#e6eaf2",
};

export default function TreasuryAutoPilot() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true); else setRefreshing(true);
    try {
      const r = await fetch(`${API}/admin/treasury/auto-pilot?days=${days}`,
        { headers: { Authorization: `Bearer ${token}` } });
      if (r.ok) setData(await r.json());
    } catch {}
    setLoading(false); setRefreshing(false);
  }, [token, days]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return (
    <div style={{ padding: 48, color: T.zinc }}>Loading treasury auto-pilot…</div>
  );
  if (!data) return (
    <div style={{ padding: 48, color: T.rose }}>Failed to load auto-pilot data.</div>
  );

  const t = data.treasury || {};
  const profitColor = data.net_profit_usd >= 0 ? T.green : T.rose;
  const marginColor = data.gross_margin_pct >= 80 ? T.green : data.gross_margin_pct >= 50 ? T.amber : T.rose;

  return (
    <div style={{ padding: "24px 32px", background: T.bg, minHeight: "100vh", color: T.white, fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* ── Header ───────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ color: T.zinc, fontSize: 11, textTransform: "uppercase", letterSpacing: 1.2, fontWeight: 600 }}>
            Treasury · Auto-Pilot
          </div>
          <h1 style={{ margin: "4px 0 0", fontSize: 28, fontWeight: 700, fontFamily: "Outfit, sans-serif" }}>
            You only see profits
          </h1>
          <p style={{ margin: "6px 0 0", color: T.zinc, fontSize: 13, maxWidth: 700 }}>
            Every client payment auto-splits into revenue, COGS reserve, and operator profit.
            Provider top-ups are handled by each provider's own auto-recharge against your card on file —
            MAARS never moves money to providers. This page just shows what's happening.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {[7, 30, 90, 365].map(d => (
            <button key={d} onClick={() => setDays(d)} style={{
              padding: "6px 12px", borderRadius: 6,
              border: `1px solid ${days === d ? T.teal : T.border2}`,
              background: days === d ? `${T.teal}22` : "transparent",
              color: days === d ? T.teal : T.zinc,
              cursor: "pointer", fontSize: 12, fontWeight: 600, fontFamily: "inherit",
            }}>{d}d</button>
          ))}
          <button onClick={() => fetchData(true)} disabled={refreshing} style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "6px 12px", borderRadius: 6, border: `1px solid ${T.border2}`,
            background: "transparent", color: T.white, cursor: "pointer", fontSize: 12, fontFamily: "inherit",
          }}>
            <RefreshCw size={12} style={{ animation: refreshing ? "spin 0.8s linear infinite" : "none" }} />
            Refresh
          </button>
        </div>
      </div>

      {/* ── Headline tiles — bottom-line view ────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 16, marginBottom: 24 }}>
        <Tile big accent={profitColor} icon={<TrendingUp size={28} />}
              label="Net Profit (lifetime)"
              value={`$${(data.net_profit_usd || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              sub={`Revenue $${(t.revenue_usd || 0).toFixed(2)} − Provider cost $${(t.cogs_actual_usd || 0).toFixed(2)}`} />
        <Tile accent={marginColor} icon={<Activity size={20} />}
              label="Gross Margin"
              value={`${data.gross_margin_pct.toFixed(1)}%`}
              sub={data.gross_margin_pct >= 80 ? "healthy" : data.gross_margin_pct >= 50 ? "tight" : "loss zone"} />
        <Tile accent={T.violet} icon={<Wallet size={20} />}
              label="COGS Reserve"
              value={`$${(t.cogs_reserve_usd || 0).toFixed(2)}`}
              sub={`Provisioned for next API calls`} />
        <Tile accent={T.amber} icon={<DollarSign size={20} />}
              label="Operator Profit Pool"
              value={`$${(t.operator_profit_usd || 0).toFixed(2)}`}
              sub={`Sweep this to your bank account anytime`} />
      </div>

      {/* ── Provider low-balance alerts ──────────────────────────── */}
      {data.provider_low_alerts && data.provider_low_alerts.length > 0 && (
        <Panel accent={T.amber} icon={<AlertTriangle size={16} />} title="Provider balance below threshold">
          <div style={{ fontSize: 12, color: T.zinc, marginBottom: 8 }}>
            Each provider's native auto-recharge will top up against your card on file. These are just heads-ups.
          </div>
          {data.provider_low_alerts.map(p => (
            <div key={p.slug} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${T.border}`, fontSize: 13 }}>
              <span style={{ color: T.white }}>{p.slug}</span>
              <span style={{ color: T.amber, fontFamily: "monospace" }}>
                ${p.balance_usd.toFixed(2)} <span style={{ color: T.zinc, fontSize: 11 }}>/ ${p.threshold_usd.toFixed(2)} threshold</span>
              </span>
            </div>
          ))}
        </Panel>
      )}

      {/* ── Cost Optimization Levers + tap headroom ──────────────── */}
      <Panel accent={T.green} icon={<Server size={16} />}
             title="Cost Levers · Untapped Savings"
             rightHeader={
               <span style={{ color: T.green, fontSize: 13 }}>
                 <strong>${data.untapped_monthly_usd_per_heavy_client.toFixed(2)}/mo</strong>
                 <span style={{ color: T.zinc, fontSize: 11, marginLeft: 6 }}>per heavy client (still off)</span>
               </span>
             }>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 10 }}>
          {(data.cost_levers || []).map(l => {
            const live = l.active_claim && l.env_detected;
            const dot  = live ? T.green : l.active_claim ? T.amber : T.zinc;
            const status = live ? "ACTIVE" : l.active_claim ? "NEEDS ENV" : "OFF";
            return (
              <div key={l.key} style={{
                padding: 10, borderRadius: 8, background: `${dot}0a`, border: `1px solid ${dot}33`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ color: T.white, fontSize: 12, fontWeight: 600 }}>{l.label}</span>
                  <span style={{ color: dot, fontSize: 9, fontWeight: 700, letterSpacing: 0.5 }}>{status}</span>
                </div>
                <div style={{ color: T.zinc, fontSize: 11 }}>
                  Saves <strong style={{ color: T.green }}>${l.savings_per_heavy_client.toFixed(2)}/mo</strong> per heavy client
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      {/* ── Per-category P&L ─────────────────────────────────────── */}
      <Panel accent={T.teal} icon={<Package size={16} />} title={`Per-Category P&L (${data.window_days}d)`}>
        <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ color: T.zinc, textAlign: "left", borderBottom: `1px solid ${T.border}` }}>
              <th style={th}>Category</th>
              <th style={thRight}>Top-ups</th>
              <th style={thRight}>Revenue</th>
              <th style={thRight}>Provider cost</th>
              <th style={thRight}>Profit</th>
              <th style={thRight}>Margin</th>
            </tr>
          </thead>
          <tbody>
            {(data.per_category || []).map(r => (
              <tr key={r.category} style={{ borderBottom: `1px solid ${T.border}`, opacity: r.revenue_usd === 0 ? 0.4 : 1 }}>
                <td style={td}><span style={{ color: catColor(r.category) }}>{catLabel(r.category)}</span></td>
                <td style={tdRight}>{r.topups_count}</td>
                <td style={tdRight}><strong style={{ color: T.white }}>${r.revenue_usd.toFixed(2)}</strong></td>
                <td style={tdRight}><span style={{ color: T.rose }}>${r.cost_usd.toFixed(4)}</span></td>
                <td style={tdRight}><strong style={{ color: r.profit_usd >= 0 ? T.green : T.rose }}>${r.profit_usd.toFixed(2)}</strong></td>
                <td style={tdRight}>
                  {r.margin_pct == null ? "—" :
                    <span style={{ color: r.margin_pct >= 80 ? T.green : r.margin_pct >= 50 ? T.amber : T.rose }}>
                      {r.margin_pct}%
                    </span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>

      {/* ── Per-client P&L (top 20) ──────────────────────────────── */}
      <Panel accent={T.violet} icon={<Users size={16} />} title={`Top Clients by Profit Contribution (${data.window_days}d)`}>
        {(data.per_client || []).length === 0 ? (
          <div style={{ color: T.zinc, fontSize: 13, padding: 16, textAlign: "center" }}>
            No client revenue or usage logged in this window yet.
          </div>
        ) : (
          <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ color: T.zinc, textAlign: "left", borderBottom: `1px solid ${T.border}` }}>
                <th style={th}>Client</th>
                <th style={thRight}>API calls</th>
                <th style={thRight}>Revenue</th>
                <th style={thRight}>Cost</th>
                <th style={thRight}>Profit</th>
                <th style={thRight}>Margin</th>
              </tr>
            </thead>
            <tbody>
              {data.per_client.map(r => (
                <tr key={r.user_id} style={{ borderBottom: `1px solid ${T.border}` }}>
                  <td style={td}><span style={{ fontFamily: "monospace", color: T.white }}>{r.user_id}</span></td>
                  <td style={tdRight}>{r.api_calls.toLocaleString()}</td>
                  <td style={tdRight}><strong style={{ color: T.white }}>${r.revenue_usd.toFixed(2)}</strong></td>
                  <td style={tdRight}><span style={{ color: T.rose }}>${r.cost_usd.toFixed(4)}</span></td>
                  <td style={tdRight}><strong style={{ color: r.profit_usd >= 0 ? T.green : T.rose }}>${r.profit_usd.toFixed(2)}</strong></td>
                  <td style={tdRight}>
                    {r.margin_pct == null ? "—" :
                      <span style={{ color: r.margin_pct >= 80 ? T.green : r.margin_pct >= 50 ? T.amber : T.rose }}>
                        {r.margin_pct}%
                      </span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      {/* ── Per-model spend (top 20) ─────────────────────────────── */}
      <Panel accent={T.blue} icon={<Activity size={16} />}
             title={`Provider Spend by Model (${data.window_days}d)`}
             rightHeader={
               <span style={{ color: T.zinc, fontSize: 12 }}>
                 Total provider cost: <strong style={{ color: T.rose }}>${data.total_provider_cost.toFixed(4)}</strong>
               </span>
             }>
        {(data.per_model || []).length === 0 ? (
          <div style={{ color: T.zinc, fontSize: 13, padding: 16, textAlign: "center" }}>
            No provider calls logged in this window yet.
          </div>
        ) : (
          <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ color: T.zinc, textAlign: "left", borderBottom: `1px solid ${T.border}` }}>
                <th style={th}>Provider</th>
                <th style={th}>Model</th>
                <th style={thRight}>Calls</th>
                <th style={thRight}>Cost</th>
                <th style={thRight}>$/call</th>
              </tr>
            </thead>
            <tbody>
              {data.per_model.map((m, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${T.border}` }}>
                  <td style={td}>{m.provider}</td>
                  <td style={td}><span style={{ fontFamily: "monospace", color: T.zinc }}>{m.model}</span></td>
                  <td style={tdRight}>{m.calls.toLocaleString()}</td>
                  <td style={tdRight}><strong style={{ color: T.rose }}>${m.cost_usd.toFixed(4)}</strong></td>
                  <td style={tdRight}><span style={{ color: T.zinc }}>${m.calls > 0 ? (m.cost_usd / m.calls).toFixed(6) : "—"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      {/* ── Quality floor reminder — anti-scam policy ────────────── */}
      <Panel accent={T.green} icon={<Shield size={16} />} title="Quality Floor (anti-scam guarantee)">
        <div style={{ color: T.zinc, fontSize: 13, lineHeight: 1.7 }}>
          Cost optimization never compromises client output:
          <ul style={{ margin: "8px 0 0 18px", padding: 0 }}>
            <li><strong style={{ color: T.white }}>Senior-Executive persona</strong> wraps every agent prompt — clients get caliber-floor outputs.</li>
            <li><strong style={{ color: T.white }}>Quality Gate</strong> assesses every cheap-tier response (logprobs + heuristic). Low-confidence answers silently retry on premium models.</li>
            <li><strong style={{ color: T.white }}>Tagged-credit auto-escalation</strong> — when a client buys a Code/Image-HD/Video top-up, the router prefers premium models for that track.</li>
            <li><strong style={{ color: T.white }}>Cap-not-cut</strong> — if a client hits their cost cap, the API returns 402 (asks them to top up). It never serves a degraded model just to stay under cost.</li>
          </ul>
        </div>
      </Panel>

      <p style={{ color: T.zinc, fontSize: 11, marginTop: 24, textAlign: "center" }}>
        Updated {data.generated_at ? new Date(data.generated_at).toLocaleString() : "—"}
      </p>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────
function Tile({ accent, label, value, sub, icon, big = false }) {
  return (
    <div style={{
      background: T.panel, border: `1px solid ${T.border}`, borderRadius: 12,
      padding: big ? "20px 24px" : 16, position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(600px 100px at 0% 0%, ${accent}14, transparent 60%)`, pointerEvents: "none" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, color: accent, marginBottom: 6 }}>
        {icon}
        <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 600 }}>{label}</span>
      </div>
      <div style={{ fontSize: big ? 36 : 22, fontWeight: 700, color: accent, fontVariantNumeric: "tabular-nums", lineHeight: 1.2 }}>
        {value}
      </div>
      {sub && <div style={{ color: T.zinc, fontSize: 11, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function Panel({ accent, icon, title, rightHeader, children }) {
  return (
    <div style={{
      background: T.panel, border: `1px solid ${T.border}`, borderRadius: 12,
      padding: "14px 18px", marginBottom: 16,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span style={{ color: accent }}>{icon}</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: T.white }}>{title}</span>
        {rightHeader && <span style={{ marginLeft: "auto" }}>{rightHeader}</span>}
      </div>
      {children}
    </div>
  );
}

const th     = { padding: "8px 6px", fontWeight: 500, fontSize: 11 };
const thRight= { ...th, textAlign: "right" };
const td     = { padding: "8px 6px" };
const tdRight= { ...td, textAlign: "right", fontFamily: "monospace" };

function catColor(c) {
  return ({
    chat: "#4fd1c5", code: "#a78bfa",
    image_std: "#fda4af", image_hd: "#e879f9",
    video: "#fbbf24", voiceover: "#38bdf8",
    tts: "#22d3ee", stt: "#2dd4bf",
    general: "#94a3b8",
  })[c] || "#94a3b8";
}
function catLabel(c) {
  return ({
    chat: "Chat", code: "Code / Vibe",
    image_std: "Image Std", image_hd: "Image HD",
    video: "Video", voiceover: "Voiceover",
    tts: "TTS", stt: "STT",
    general: "General (untagged)",
  })[c] || c;
}
