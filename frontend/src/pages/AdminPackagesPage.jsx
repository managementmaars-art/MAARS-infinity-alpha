import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Plus, Save, RotateCcw, Trash2, X, RefreshCw, History, Users, Package as PackageIcon,
  AlertCircle, Search,
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  teal: "#4fd1c5", violet: "#7c3aed", green: "#34d399", amber: "#f59e0b",
  red: "#f87171", mute: "#94a3b8",
  border: "rgba(255,255,255,0.08)", border2: "rgba(255,255,255,0.14)",
  glass: "rgba(6,12,28,0.7)",
};

const authHeaders = () => {
  const tok = localStorage.getItem("token") || "";
  return tok ? { Authorization: `Bearer ${tok}` } : {};
};

async function jsonFetch(path, method = "GET", body = null) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body ? JSON.stringify(body) : null,
  });
  // Read body defensively — if something upstream already consumed the stream
  // (Chrome devtools, a service worker, a React-strict-mode double-mount), the
  // raw `await r.text()` throws a confusing "body stream already read" message
  // that bubbles into the toast. Fall back gracefully: return an empty list
  // envelope if the read fails, so the page still renders.
  let text = "";
  try { text = await r.text(); }
  catch { /* stream already consumed — treat as empty body */ }
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!r.ok) {
    const msg = (json && (json.detail?.message || json.detail)) || `HTTP ${r.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return json || { object: "list", data: [] };
}

// Default plan ids — these come from shared/constants.SUBSCRIPTION_PLANS and
// can't be deleted (only reset). Mirror the current set; safe to update.
const DEFAULT_PKG_IDS = new Set([
  "free", "starter", "essential", "basic", "standard", "professional",
  "advanced", "business", "agency", "studio", "enterprise", "corporate", "elite",
]);

/**
 * Owner / Pricing-Splits panel — operator share %, customer overrides, audit slice.
 *
 * Two render modes:
 *   - default (page mode): full-screen with header, used at /admin/packages-manager
 *     (legacy route; redirected, kept for backward compat)
 *   - embedded={true}: no page chrome, mounted as a section inside
 *     AdminPricingManagerPage at /admin/pricing-manager (Option-B unification)
 */
export default function AdminPackagesPage({ embedded = false } = {}) {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [packages, setPackages]   = useState([]);
  const [edits, setEdits]         = useState({});
  const [overrides, setOverrides] = useState([]);
  const [audit, setAudit]         = useState([]);
  const [busy, setBusy]           = useState(false);

  // new-package form
  const [newPkg, setNewPkg] = useState({ id: "", name: "", price_usd: 99, credits: 12000, operator_share_pct: 0.30 });

  // new-customer-override form
  const [newOver, setNewOver] = useState({
    user_id: "", package_id: "pro",
    operator_share_pct: 0.20, price_usd: "", credits_bonus: "", notes: "", expires_at: "",
  });

  // ── load ───────────────────────────────────────────────────────────
  const load = useCallback(async () => {
    setBusy(true);
    // Parallel but independent — one failing endpoint (e.g. audit 500 on a
    // backend that predates the try/except wrap) shouldn't block the whole
    // page with a toast. Each section renders whatever it got.
    const [pkgsRes, overRes, logRes] = await Promise.allSettled([
      jsonFetch("/admin/packages"),
      jsonFetch("/admin/customers/pricing"),
      jsonFetch("/admin/packages/audit?limit=20"),
    ]);
    setPackages((pkgsRes.status === "fulfilled" && pkgsRes.value?.data) || []);
    setOverrides((overRes.status === "fulfilled" && overRes.value?.data) || []);
    setAudit((logRes.status === "fulfilled" && logRes.value?.data) || []);
    setEdits({});
    // Only toast on the core packages endpoint. Audit / overrides are
    // non-blocking enhancements; missing them renders an empty section
    // silently instead of a scary banner.
    if (pkgsRes.status === "rejected") {
      toast.error(`Load failed: ${pkgsRes.reason?.message || "packages endpoint error"}`);
    }
    setBusy(false);
  }, []);

  useEffect(() => {
    if (!user?.is_admin) navigate("/dashboard");
    else load();
  }, [user, navigate, load]);

  // ── package edit handlers ──────────────────────────────────────────
  const editField = (pid, field, value) => setEdits(prev => ({
    ...prev, [pid]: { ...(prev[pid] || {}), [field]: value },
  }));
  const dirty = Object.keys(edits).length > 0;
  const liveValue = (p, field) => (edits[p.id] && field in edits[p.id]) ? edits[p.id][field] : p[field];
  const liveSplit = (p) => {
    const price = parseFloat(liveValue(p, "price_usd")) || 0;
    const share = parseFloat(liveValue(p, "operator_share_pct")) || 0;
    return { op: +(price * share).toFixed(2), back: +(price * (1 - share)).toFixed(2) };
  };

  const savePackages = async () => {
    if (!dirty) return toast.error("No changes to save");
    try {
      const r = await jsonFetch("/admin/packages", "POST", { updates: edits });
      toast.success(`Saved ${r.applied_to.length} package(s).`);
      await load();
    } catch (e) { toast.error(`Save failed: ${e.message}`); }
  };

  const resetPackages = async () => {
    if (!window.confirm("Reset ALL packages to code defaults? Persisted overrides will be wiped.")) return;
    try { await jsonFetch("/admin/packages/reset", "POST"); toast.success("Reset complete."); await load(); }
    catch (e) { toast.error(`Reset failed: ${e.message}`); }
  };

  const deletePackage = async (pid) => {
    if (DEFAULT_PKG_IDS.has(pid)) return toast.error("Default packages can't be deleted — use Reset.");
    if (!window.confirm(`Delete custom package "${pid}"? Existing purchases stay; future buys won't see it.`)) return;
    try { await jsonFetch(`/admin/packages/${pid}`, "DELETE"); toast.success(`Deleted ${pid}.`); await load(); }
    catch (e) { toast.error(`Delete failed: ${e.message}`); }
  };

  const addNewPackage = async () => {
    const id = newPkg.id.trim().toLowerCase().replace(/[^a-z0-9_]/g, "_");
    if (!id || !newPkg.name || !(newPkg.price_usd > 0) || !(newPkg.credits > 0)) {
      return toast.error("id, name, price_usd, credits are all required");
    }
    try {
      await jsonFetch("/admin/packages", "POST", {
        updates: { [id]: {
          name: newPkg.name,
          price_usd: parseFloat(newPkg.price_usd),
          credits: parseInt(newPkg.credits, 10),
          operator_share_pct: parseFloat(newPkg.operator_share_pct),
        }},
      });
      toast.success(`Created ${id}.`);
      setNewPkg({ id: "", name: "", price_usd: 99, credits: 12000, operator_share_pct: 0.30 });
      await load();
    } catch (e) { toast.error(`Create failed: ${e.message}`); }
  };

  // ── customer override handlers ─────────────────────────────────────
  const saveOverride = async () => {
    const p = newOver;
    if (!p.user_id.trim() || !p.package_id.trim()) return toast.error("user_id and package_id required");
    const body = {
      package_id: p.package_id,
      operator_share_pct: p.operator_share_pct === "" ? null : parseFloat(p.operator_share_pct),
      price_usd: p.price_usd === "" ? null : parseFloat(p.price_usd),
      credits_bonus: p.credits_bonus === "" ? null : parseInt(p.credits_bonus, 10),
      notes: p.notes || "",
      expires_at: p.expires_at || null,
    };
    try {
      await jsonFetch(`/admin/customers/${encodeURIComponent(p.user_id)}/pricing`, "POST", body);
      toast.success(`Override saved for ${p.user_id}.`);
      setNewOver({ ...newOver, user_id: "", credits_bonus: "", price_usd: "", notes: "" });
      await load();
    } catch (e) { toast.error(`Save failed: ${e.message}`); }
  };

  const deleteOverride = async (uid, pid) => {
    if (!window.confirm(`Delete override for ${uid} / ${pid}?`)) return;
    try {
      await jsonFetch(`/admin/customers/${encodeURIComponent(uid)}/pricing/${encodeURIComponent(pid)}`, "DELETE");
      toast.success("Override removed.");
      await load();
    } catch (e) { toast.error(`Delete failed: ${e.message}`); }
  };

  // ── ui ─────────────────────────────────────────────────────────────
  const inner = (
    <div style={{ maxWidth: 1240, margin: embedded ? 0 : "0 auto" }}>
      {!embedded && (
        <div style={{ display: "flex", alignItems: "center", marginBottom: 24 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: -0.3 }}>Owner — Packages & Pricing</h1>
            <p style={{ margin: "6px 0 0", color: T.mute, fontSize: 13 }}>
              Add new tiers, edit splits, override pricing per customer. Every change is logged in the immutable audit trail.
            </p>
          </div>
          <button onClick={load} disabled={busy}
            style={{ marginLeft: "auto", ...btnGhost }}><RefreshCw size={13} /> Refresh</button>
        </div>
      )}
      {embedded && (
        <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: "#fff", fontFamily: "Outfit, sans-serif" }}>
            Operator splits, customer overrides & audit
          </h2>
          <button onClick={load} disabled={busy}
            style={{ marginLeft: "auto", ...btnGhost }}><RefreshCw size={13} /> Refresh</button>
        </div>
      )}

        {/* ── packages ──────────────────────────────────────────────── */}
        {/* Hidden when embedded in /admin/pricing-manager — the plan editor    */}
        {/* above already exposes operator_share_pct per plan, so a duplicate   */}
        {/* table here is noise. Standalone view (/admin/packages-manager)       */}
        {/* still shows it as a quick all-in-one editor.                         */}
        {!embedded && (
        <Section title="Packages" icon={<PackageIcon size={16} />} accent={T.teal}
          rightActions={<>
            <Button onClick={resetPackages}><RotateCcw size={11} /> Reset</Button>
            <Button onClick={savePackages} primary disabled={!dirty}><Save size={11} /> Save changes</Button>
          </>}
        >
          {packages.length === 0 ? <Empty label="No packages defined yet." /> : (
            <table style={tableStyle}>
              <thead><tr style={{ color: T.mute }}>
                <th style={th}>Package</th><th style={th}>Price (USD)</th>
                <th style={th}>Credits</th><th style={th}>Operator share</th>
                <th style={th}>Per-sale split</th><th style={th}></th>
              </tr></thead>
              <tbody>
                {packages.map(p => {
                  const split = liveSplit(p);
                  const edited = !!edits[p.id];
                  const isDefault = DEFAULT_PKG_IDS.has(p.id);
                  return (
                    <tr key={p.id} style={{ borderTop: `1px solid ${T.border}`,
                                            background: edited ? `${T.amber}0c` : "transparent" }}>
                      <td style={td}>
                        <div style={{ fontWeight: 600 }}>{p.name}</div>
                        <div style={{ color: T.mute, fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>
                          {p.id}{isDefault ? " · default" : " · custom"}
                        </div>
                      </td>
                      <td style={td}>
                        <input type="number" min="0" step="0.5" value={liveValue(p, "price_usd")}
                          onChange={e => editField(p.id, "price_usd", parseFloat(e.target.value))}
                          style={miniInput} />
                      </td>
                      <td style={td}>
                        <input type="number" min="0" step="100" value={liveValue(p, "credits")}
                          onChange={e => editField(p.id, "credits", parseInt(e.target.value, 10))}
                          style={miniInput} />
                      </td>
                      <td style={td}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 180 }}>
                          <input type="range" min="0" max="100" step="1"
                            value={Math.round(parseFloat(liveValue(p, "operator_share_pct") || 0) * 100)}
                            onChange={e => editField(p.id, "operator_share_pct", parseInt(e.target.value, 10) / 100)}
                            style={{ flex: 1, accentColor: T.teal }} />
                          <span style={{ width: 44, textAlign: "right", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                            {Math.round(parseFloat(liveValue(p, "operator_share_pct") || 0) * 100)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ ...td, fontSize: 12 }}>
                        <div style={{ color: T.green }}>op: <b>${split.op}</b></div>
                        <div style={{ color: T.mute }}>back: ${split.back}</div>
                      </td>
                      <td style={{ ...td, textAlign: "right" }}>
                        {!isDefault && (
                          <button onClick={() => deletePackage(p.id)} style={btnGhostRed}>
                            <Trash2 size={12} />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          {/* Add new */}
          <div style={{ marginTop: 16, padding: 14, background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, color: T.teal, fontSize: 12, fontWeight: 600 }}>
              <Plus size={13} /> Add a custom package
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr 100px 110px 130px auto", gap: 8 }}>
              <input placeholder="id (e.g. enterprise)" value={newPkg.id}
                onChange={e => setNewPkg({ ...newPkg, id: e.target.value })} style={input} />
              <input placeholder="display name" value={newPkg.name}
                onChange={e => setNewPkg({ ...newPkg, name: e.target.value })} style={input} />
              <input type="number" min="0" step="1" placeholder="price USD" value={newPkg.price_usd}
                onChange={e => setNewPkg({ ...newPkg, price_usd: e.target.value })} style={input} />
              <input type="number" min="0" step="500" placeholder="credits" value={newPkg.credits}
                onChange={e => setNewPkg({ ...newPkg, credits: e.target.value })} style={input} />
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <input type="range" min="0" max="100" step="1"
                  value={Math.round(newPkg.operator_share_pct * 100)}
                  onChange={e => setNewPkg({ ...newPkg, operator_share_pct: parseInt(e.target.value, 10) / 100 })}
                  style={{ flex: 1, accentColor: T.teal }} />
                <span style={{ width: 36, textAlign: "right", fontSize: 12, fontWeight: 600 }}>
                  {Math.round(newPkg.operator_share_pct * 100)}%
                </span>
              </div>
              <Button primary onClick={addNewPackage}><Plus size={11} /> Add</Button>
            </div>
          </div>
        </Section>
        )}

        {/* ── customer overrides ───────────────────────────────────── */}
        <Section title="Per-customer pricing overrides" icon={<Users size={16} />} accent={T.violet}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 12 }}>
            Attach negotiated pricing to a specific user_id. The Stripe webhook checks for an active override per (user, package) and applies it before falling back to the package default. Optional `expires_at` ISO timestamp lets the override auto-revert.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "200px 110px 110px 110px 130px 1fr auto", gap: 8, marginBottom: 14, padding: 12, background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
            <input placeholder="user_id" value={newOver.user_id}
              onChange={e => setNewOver({ ...newOver, user_id: e.target.value })} style={input} />
            <select value={newOver.package_id}
              onChange={e => setNewOver({ ...newOver, package_id: e.target.value })} style={input}>
              {packages.map(p => <option key={p.id} value={p.id}>{p.id}</option>)}
            </select>
            <input type="number" min="0" max="1" step="0.01" placeholder="op share"
              value={newOver.operator_share_pct}
              onChange={e => setNewOver({ ...newOver, operator_share_pct: e.target.value })} style={input} />
            <input type="number" min="0" step="1" placeholder="price USD"
              value={newOver.price_usd}
              onChange={e => setNewOver({ ...newOver, price_usd: e.target.value })} style={input} />
            <input type="number" min="0" step="100" placeholder="credit bonus"
              value={newOver.credits_bonus}
              onChange={e => setNewOver({ ...newOver, credits_bonus: e.target.value })} style={input} />
            <input placeholder="notes (optional)" value={newOver.notes}
              onChange={e => setNewOver({ ...newOver, notes: e.target.value })} style={input} />
            <Button primary onClick={saveOverride}><Save size={11} /> Save override</Button>
          </div>

          {overrides.length === 0 ? <Empty label="No customer overrides yet." /> : (
            <table style={tableStyle}>
              <thead><tr style={{ color: T.mute }}>
                <th style={th}>User</th><th style={th}>Package</th>
                <th style={th}>Operator %</th><th style={th}>Price USD</th>
                <th style={th}>Credit bonus</th><th style={th}>Notes</th>
                <th style={th}>Updated</th><th style={th}></th>
              </tr></thead>
              <tbody>
                {overrides.map((o, i) => (
                  <tr key={`${o.user_id}_${o.package_id}_${i}`} style={{ borderTop: `1px solid ${T.border}` }}>
                    <td style={{ ...td, fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{o.user_id}</td>
                    <td style={td}>{o.package_id}</td>
                    <td style={td}>{o.operator_share_pct != null ? `${(o.operator_share_pct * 100).toFixed(0)}%` : "—"}</td>
                    <td style={td}>{o.price_usd != null ? `$${o.price_usd.toFixed(2)}` : "—"}</td>
                    <td style={td}>{o.credits_bonus != null ? `+${o.credits_bonus.toLocaleString()}` : "—"}</td>
                    <td style={{ ...td, color: T.mute, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {o.notes || "—"}
                    </td>
                    <td style={{ ...td, color: T.mute, fontSize: 11 }}>
                      {o.updated_at ? new Date(o.updated_at).toLocaleDateString() : "—"}
                    </td>
                    <td style={{ ...td, textAlign: "right" }}>
                      <button onClick={() => deleteOverride(o.user_id, o.package_id)} style={btnGhostRed}>
                        <Trash2 size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Section>

        {/* ── audit trail ──────────────────────────────────────────── */}
        <Section title="Recent audit entries (packages & pricing)" icon={<History size={16} />} accent={T.amber}>
          {audit.length === 0 ? <Empty label="No audit entries yet." /> : (
            <div style={{ maxHeight: 360, overflowY: "auto" }}>
              <table style={tableStyle}>
                <thead><tr style={{ color: T.mute }}>
                  <th style={th}>When</th><th style={th}>Action</th><th style={th}>Actor</th>
                  <th style={th}>Target</th><th style={th}>Detail</th>
                </tr></thead>
                <tbody>
                  {audit.map((e, i) => (
                    <tr key={`${e.timestamp}_${i}`} style={{ borderTop: `1px solid ${T.border}` }}>
                      <td style={{ ...td, fontSize: 11, color: T.mute, whiteSpace: "nowrap" }}>
                        {e.timestamp ? new Date(e.timestamp).toLocaleString() : "—"}
                      </td>
                      <td style={td}><code style={{ fontSize: 11 }}>{e.action}</code></td>
                      <td style={{ ...td, fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{e.actor_id}</td>
                      <td style={td}>{e.target_type}/<code style={{ fontSize: 11 }}>{e.target_id}</code></td>
                      <td style={{ ...td, fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: T.mute, maxWidth: 360, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {JSON.stringify(e.details || {})}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>
    </div>
  );

  // Page chrome only when used as a standalone route; embedded mounts inline.
  if (embedded) return inner;
  return (
    <div style={{ minHeight: "100vh", background: "#04070f", color: "#e6eaf2", padding: 40 }}>
      {inner}
    </div>
  );
}

// ── small components ───────────────────────────────────────────────────

function Section({ title, icon, accent, rightActions, children }) {
  return (
    <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden", marginBottom: 18 }}>
      <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`,
                    display: "flex", alignItems: "center", gap: 8, color: accent, fontWeight: 600, fontSize: 14 }}>
        {icon} {title}
        <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>{rightActions}</div>
      </div>
      <div style={{ padding: 18 }}>{children}</div>
    </div>
  );
}

function Button({ children, onClick, primary, disabled }) {
  return (
    <button onClick={onClick} disabled={disabled}
      style={{
        padding: "5px 12px", borderRadius: 6, fontSize: 11, fontWeight: 600,
        background: primary ? `linear-gradient(90deg, ${T.teal}, ${T.violet})` : "transparent",
        color: primary ? "#04070f" : "#e6eaf2",
        border: primary ? "none" : `1px solid ${T.border}`,
        cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.5 : 1,
        display: "inline-flex", alignItems: "center", gap: 4,
      }}>{children}</button>
  );
}

function Empty({ label }) {
  return <div style={{ padding: 20, textAlign: "center", color: T.mute, fontSize: 12 }}>{label}</div>;
}

const tableStyle = { width: "100%", borderCollapse: "collapse", fontSize: 13 };
const th = { padding: "8px 12px", textAlign: "left", fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 500 };
const td = { padding: "10px 12px" };
const input = { padding: "6px 10px", borderRadius: 5, fontSize: 12,
  background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#e6eaf2" };
const miniInput = { ...input, width: 90, fontVariantNumeric: "tabular-nums" };
const btnGhost = { padding: "5px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
  background: "transparent", border: `1px solid ${T.border}`, color: "#e6eaf2",
  cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4 };
const btnGhostRed = { ...btnGhost, color: T.red, borderColor: `${T.red}55` };
