import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  CheckCircle2, XCircle, Loader, ExternalLink, Copy, Rocket, RefreshCw,
  Database, Key, Wallet, Activity, Server, ChevronDown, ChevronRight, AlertCircle,
  Search, Layers, Sparkles,
} from "lucide-react";
import { API } from "../App";
import { toast } from "sonner";

const T = {
  teal:    "#4fd1c5",
  violet:  "#7c3aed",
  green:   "#34d399",
  amber:   "#f59e0b",
  red:     "#f87171",
  mute:    "#94a3b8",
  border:  "rgba(255,255,255,0.08)",
  border2: "rgba(255,255,255,0.14)",
  glass:   "rgba(6,12,28,0.7)",
};

const PROVIDERS = ["openai", "anthropic", "groq", "deepseek"];
const PROVIDER_NAMES = {
  openai: "OpenAI", anthropic: "Anthropic", groq: "Groq", deepseek: "DeepSeek",
};

function statusIcon(status) {
  if (status === "success" || status === "validated") return <CheckCircle2 size={16} color={T.green} />;
  if (status === "failed" || status === "invalid")    return <XCircle size={16} color={T.red} />;
  if (status === "running")                           return <Loader size={16} color={T.amber} className="spin" />;
  if (status === "detected")                          return <CheckCircle2 size={16} color={T.amber} />;
  if (status === "skipped")                           return <AlertCircle size={16} color={T.mute} />;
  return <div style={{ width: 8, height: 8, borderRadius: 999, background: T.mute, marginLeft: 4, marginRight: 4 }} />;
}

function badge(status) {
  const colors = {
    success: T.green, validated: T.green,
    failed: T.red,    invalid: T.red,
    running: T.amber, detected: T.amber,
    pending: T.mute,  missing: T.mute, skipped: T.mute,
  };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "3px 10px", borderRadius: 999, fontSize: 11, fontWeight: 600,
      background: `${colors[status] || T.mute}22`, color: colors[status] || T.mute,
      textTransform: "uppercase", letterSpacing: 0.5,
    }}>{statusIcon(status)} {status || "pending"}</span>
  );
}

const authHeaders = () => {
  const tok = localStorage.getItem("token") || "";
  return tok ? { Authorization: `Bearer ${tok}` } : {};
};

async function call(path, method = "POST", body = undefined) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!r.ok) {
    const msg = (json && (json.detail?.error?.message || json.detail?.message || json.detail)) || `HTTP ${r.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return json;
}

export default function SetupWizard() {
  const navigate = useNavigate();
  const [state, setState]     = useState(null);
  const [report, setReport]   = useState(null);
  const [catalog, setCatalog] = useState({ quick: [], advanced: [], totals: {} });
  const [keys, setKeys]       = useState({});       // { slug: "raw key being typed" }
  const [stripe, setStripe]   = useState({ secret_key: "", webhook_secret: "" });
  const [busy, setBusy]       = useState({});
  const [savedCreds, setSavedCreds] = useState(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [advFilter, setAdvFilter] = useState("");
  const [advCategory, setAdvCategory] = useState("all");

  const setBusyOn  = (k) => setBusy(b => ({ ...b, [k]: true }));
  const setBusyOff = (k) => setBusy(b => ({ ...b, [k]: false }));

  const refresh = useCallback(async () => {
    try {
      const [s, r, c] = await Promise.all([
        call("/setup/status", "GET"),
        call("/setup/report", "GET"),
        call("/setup/providers/catalog", "GET"),
      ]);
      setState(s);
      setReport(r);
      setCatalog(c || { quick: [], advanced: [], totals: {} });
      if (r?.test_credentials) setSavedCreds(r.test_credentials);
    } catch (e) {
      toast.error(`Setup access denied: ${e.message}`);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // ── action handlers ──────────────────────────────────────────

  const runStep = (key, path, body) => async () => {
    setBusyOn(key);
    try {
      const r = await call(path, "POST", body);
      if (r?.metadata?.api_key) setSavedCreds(r.metadata);
      toast.success(r.detail || "ok");
      await refresh();
    } catch (e) { toast.error(e.message); }
    finally { setBusyOff(key); }
  };

  const openLink = async (provider) => {
    try {
      const info = provider === "stripe"
        ? await call("/setup/stripe/open-link")
        : await call("/setup/providers/open-link", "POST", { provider });
      window.open(info.url, "_blank", "noopener,noreferrer");
    } catch (e) { toast.error(e.message); }
  };

  const saveProvider = async (slug, displayName) => {
    if (!keys[slug]) return toast.error(`Paste a ${displayName || slug} key first`);
    await runStep(`p_${slug}`, "/setup/providers/save", { provider: slug, api_key: keys[slug] })();
    setKeys(k => ({ ...k, [slug]: "" }));      // clear input after save
  };

  const filteredAdvanced = useMemo(() => {
    let list = catalog.advanced || [];
    if (advCategory !== "all") list = list.filter(p => p.category === advCategory);
    if (advFilter) {
      const needle = advFilter.toLowerCase();
      list = list.filter(p =>
        p.slug.includes(needle) ||
        (p.display_name || "").toLowerCase().includes(needle) ||
        (p.notes || "").toLowerCase().includes(needle));
    }
    return list;
  }, [catalog, advCategory, advFilter]);

  const advCategories = useMemo(() => {
    const s = new Set((catalog.advanced || []).map(p => p.category));
    return ["all", ...Array.from(s).sort()];
  }, [catalog]);

  const saveStripe = async () => {
    if (!stripe.secret_key) return toast.error("Stripe secret key required");
    await runStep("stripe", "/setup/stripe/save", stripe)();
    setStripe({ secret_key: "", webhook_secret: "" });
  };

  const launch = async () => {
    setBusyOn("launch");
    try {
      const r = await call("/setup/launch", "POST");
      toast.success("MAARS launched. Redirecting…");
      setTimeout(() => navigate("/dashboard"), 1200);
    } catch (e) {
      toast.error(`Cannot launch: ${e.message}`);
    } finally { setBusyOff("launch"); }
  };

  const stepStatus = (id) => state?.steps?.[id]?.status || "pending";
  const stepDetail = (id) => state?.steps?.[id]?.detail || "";

  // ── ui ───────────────────────────────────────────────────────

  return (
    <div style={{ minHeight: "100vh", background: "#04070f", color: "#e6eaf2", padding: 40 }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } } .spin { animation: spin 1s linear infinite; }`}</style>
      <div style={{ maxWidth: 1080, margin: "0 auto" }}>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: -0.4 }}>MAARS Guided Setup</h1>
            <p style={{ margin: "8px 0 0", color: T.mute, fontSize: 14 }}>
              Click. Paste keys when asked. The wizard validates, persists, and tests everything else.
            </p>
          </div>
          <button onClick={refresh}
            style={{ padding: "8px 14px", borderRadius: 8, background: "transparent",
                     border: `1px solid ${T.border2}`, color: "#e6eaf2", cursor: "pointer",
                     display: "flex", alignItems: "center", gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {/* ── Section 1: System check ─────────────────────────── */}
        <Section title="System Check" icon={<Server size={16} />} status={stepStatus("system_check")} detail={stepDetail("system_check")}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 13 }}>
            Verifies Python 3.11+, MongoDB connectivity, and that <code>.env</code> is writable.
          </p>
          <Button onClick={runStep("check", "/setup/check")} busy={busy.check}>Run system check</Button>
        </Section>

        {/* ── Section 2: Quick Setup (catalog-driven 4 providers) ─ */}
        <Section title="Quick Setup — core providers" icon={<Sparkles size={16} />}
                 status={report?.providers_ready ? "success" : "pending"}
                 detail={report?.providers_ready
                   ? `${catalog.totals?.configured ?? 0} of ${catalog.quick.length + catalog.advanced.length} providers configured.`
                   : "Configure at least one provider to enable routing."}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 13 }}>
            Enough to get MAARS running. Each save validates against the provider's <code>/v1/models</code> (or equivalent) endpoint before persisting to <code>.env</code>.
          </p>
          {catalog.quick.map(p => (
            <ProviderRow key={p.slug} p={p}
              keys={keys} setKeys={setKeys} busy={busy}
              onOpen={() => openLink(p.slug)}
              onSave={() => saveProvider(p.slug, p.display_name)}
              onRetest={runStep(`pt_${p.slug}`, "/setup/providers/test", { provider: p.slug })}
              stepStatus={stepStatus(`provider_${p.slug}`)} />
          ))}
        </Section>

        {/* ── Section 2b: Advanced providers (collapsible) ──────── */}
        <Section title={`Advanced Provider Setup — full MAARS network (${catalog.advanced.length})`}
                 icon={<Layers size={16} />}
                 status={catalog.totals?.configured > catalog.quick.length ? "success" : "pending"}
                 detail="Frontier, open-model hosts, regional, vertical, audio. Optional — Quick Setup alone is enough to launch.">
          <button onClick={() => setAdvancedOpen(o => !o)}
            style={{ ...btnGhost, marginBottom: 14 }}>
            {advancedOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            {advancedOpen ? "Hide advanced providers" : "Show advanced providers"}
          </button>

          {advancedOpen && (
            <>
              <div style={{ display: "flex", gap: 10, marginBottom: 14, alignItems: "center" }}>
                <div style={{ position: "relative", flex: 1 }}>
                  <Search size={13} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: T.mute }} />
                  <input value={advFilter} onChange={e => setAdvFilter(e.target.value)}
                    placeholder="Search by name, slug, or notes…"
                    style={{ ...inputStyle, paddingLeft: 30, width: "100%" }} />
                </div>
                <select value={advCategory} onChange={e => setAdvCategory(e.target.value)}
                  style={{ ...inputStyle, minWidth: 140 }}>
                  {advCategories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <div style={{ color: T.mute, fontSize: 12 }}>{filteredAdvanced.length} shown</div>
              </div>

              {filteredAdvanced.map(p => (
                <ProviderRow key={p.slug} p={p}
                  keys={keys} setKeys={setKeys} busy={busy}
                  onOpen={() => openLink(p.slug)}
                  onSave={() => saveProvider(p.slug, p.display_name)}
                  onRetest={runStep(`pt_${p.slug}`, "/setup/providers/test", { provider: p.slug })}
                  stepStatus={stepStatus(`provider_${p.slug}`)} advanced />
              ))}
              {filteredAdvanced.length === 0 && (
                <div style={{ padding: 24, textAlign: "center", color: T.mute, fontSize: 12 }}>
                  No providers match the current filter.
                </div>
              )}
            </>
          )}
        </Section>

        {/* ── Section 3: Stripe ───────────────────────────────── */}
        <Section title="Billing Setup (Stripe — optional)" icon={<Rocket size={16} />}
                 status={stepStatus("stripe_keys")} detail={stepDetail("stripe_keys")}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 13 }}>
            Paste your Stripe <b>secret key</b> and (optional) webhook signing secret. The key is validated by reading your account before save.
          </p>
          <div style={{ display: "flex", gap: 10, marginBottom: 8 }}>
            <button onClick={() => openLink("stripe")} style={btnGhost}>
              <ExternalLink size={12} /> Open Stripe dashboard
            </button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: 8 }}>
            <input type="password" value={stripe.secret_key}
              onChange={e => setStripe(s => ({ ...s, secret_key: e.target.value }))}
              placeholder={report?.configured_env?.STRIPE_SECRET_KEY ? `current: ${report.configured_env.STRIPE_SECRET_KEY}` : "sk_test_… or sk_live_…"}
              style={inputStyle} />
            <input type="password" value={stripe.webhook_secret}
              onChange={e => setStripe(s => ({ ...s, webhook_secret: e.target.value }))}
              placeholder={report?.configured_env?.STRIPE_WEBHOOK_SECRET ? `current: ${report.configured_env.STRIPE_WEBHOOK_SECRET}` : "whsec_… (optional)"}
              style={inputStyle} />
            <Button busy={busy.stripe} onClick={saveStripe} primary>Save & test</Button>
          </div>
        </Section>

        {/* ── Section 4: Database ─────────────────────────────── */}
        <Section title="Database Setup" icon={<Database size={16} />} status={stepStatus("migrate")} detail={stepDetail("migrate")}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 13 }}>
            Creates wallet/ledger/api-key indexes and back-fills wallets for any pre-existing users.
          </p>
          <Button busy={busy.migrate} onClick={runStep("migrate", "/setup/migrate")}>Run migrations</Button>
        </Section>

        {/* ── Section 5: Seed ─────────────────────────────────── */}
        <Section title="Seed / Test Setup" icon={<Wallet size={16} />} status={stepStatus("seed")} detail={stepDetail("seed")}>
          <p style={{ margin: "0 0 12px", color: T.mute, fontSize: 13 }}>
            Provisions a test user, mints an API key, and grants 50 credits. Idempotent — running again rotates the key.
          </p>
          <Button busy={busy.seed} onClick={runStep("seed", "/setup/seed")} primary>Seed test user</Button>

          {savedCreds?.api_key && (
            <CredCard creds={savedCreds} />
          )}
        </Section>

        {/* ── Section 6: Tests ────────────────────────────────── */}
        <Section title="Validation Tests" icon={<Activity size={16} />}
                 status={
                   stepStatus("test_routing") === "success" &&
                   stepStatus("test_wallet") === "success" &&
                   stepStatus("test_completion") === "success" ? "success" :
                   (stepStatus("test_routing") === "failed" || stepStatus("test_wallet") === "failed" || stepStatus("test_completion") === "failed") ? "failed" : "pending"
                 }
                 detail="">
          <Row label="Routing decision" status={stepStatus("test_routing")} detail={stepDetail("test_routing")}
               action={<Button busy={busy.tr} onClick={runStep("tr", "/setup/test-routing")}>Run</Button>} />
          <Row label="Wallet reserve / refund" status={stepStatus("test_wallet")} detail={stepDetail("test_wallet")}
               action={<Button busy={busy.tw} onClick={runStep("tw", "/setup/test-wallet")}>Run</Button>} />
          <Row label="Live chat completion" status={stepStatus("test_completion")} detail={stepDetail("test_completion")}
               action={<Button busy={busy.tc} onClick={runStep("tc", "/setup/test-completion")}>Run</Button>} />
        </Section>

        {/* ── Section 7: Launch readiness ─────────────────────── */}
        <Section title="Launch Status" icon={<Rocket size={16} />} status={report?.launch_ready ? "success" : "pending"} detail="">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 14 }}>
            <Check label="Frontend"  ok={report?.frontend_ready} />
            <Check label="Backend"   ok={report?.backend_ready} />
            <Check label="Database"  ok={report?.database_ready} />
            <Check label="Providers" ok={report?.providers_ready} />
            <Check label="Billing"   ok={report?.billing_ready} optional />
            <Check label="Wallet"    ok={report?.wallet_ready} />
            <Check label="Routing"   ok={report?.routing_ready} />
            <Check label="Completion test" ok={report?.completion_ready} optional />
          </div>
          <Button onClick={launch} busy={busy.launch} primary
                  disabled={!report?.launch_ready}>
            <Rocket size={14} /> Launch MAARS
          </Button>
          {report?.finished_at && (
            <div style={{ marginTop: 10, color: T.green, fontSize: 12 }}>
              Setup completed at {new Date(report.finished_at).toLocaleString()}.
            </div>
          )}
        </Section>
      </div>
    </div>
  );
}

// ─── small components ────────────────────────────────────────────

function ProviderRow({ p, keys, setKeys, busy, onOpen, onSave, onRetest, stepStatus, advanced }) {
  // Status precedence: live step status > catalog-detected status (validated/detected/missing/skipped)
  const effStatus =
    stepStatus && stepStatus !== "pending" ? stepStatus
    : (p.status || "missing");
  const skipped = p.validation_strategy === "coming_soon";
  const manual  = p.validation_strategy === "placeholder_manual";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0",
                  borderTop: `1px solid ${T.border}`, fontSize: 13, opacity: skipped ? 0.7 : 1 }}>
      <div style={{ width: 160 }}>
        <div style={{ fontWeight: 600 }}>{p.display_name}</div>
        {advanced && <div style={{ fontSize: 10, color: T.mute, marginTop: 2 }}>{p.category}</div>}
      </div>
      {badge(effStatus)}
      <button onClick={onOpen} style={btnGhost}>
        <ExternalLink size={12} /> Open
      </button>
      <input type="password" value={keys[p.slug] || ""}
        onChange={e => setKeys(k => ({ ...k, [p.slug]: e.target.value }))}
        placeholder={p.masked_value
          ? `current: ${p.masked_value}${manual ? "  (manual validation)" : ""}`
          : (skipped ? "adapter pending — env will save but won't route" : "paste API key")}
        disabled={skipped}
        style={{ flex: 1, padding: "6px 10px", borderRadius: 6, fontSize: 12,
                 background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border2}`,
                 color: "#e6eaf2", opacity: skipped ? 0.5 : 1 }} />
      <Button busy={busy[`p_${p.slug}`]} onClick={onSave} primary disabled={skipped}>
        Save & test
      </Button>
      {p.configured && !manual && !skipped && (
        <Button busy={busy[`pt_${p.slug}`]} onClick={onRetest}>Re-test</Button>
      )}
    </div>
  );
}

function Section({ title, icon, status, detail, children }) {
  return (
    <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
        <span style={{ color: T.teal }}>{icon}</span>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>{title}</h3>
        <div style={{ marginLeft: "auto" }}>{badge(status)}</div>
      </div>
      {detail && <div style={{ color: T.mute, fontSize: 12, marginBottom: 12 }}>{detail}</div>}
      {children}
    </div>
  );
}

function Row({ label, status, detail, action }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderTop: `1px solid ${T.border}` }}>
      <div style={{ width: 220, fontSize: 13, fontWeight: 500 }}>{label}</div>
      {badge(status)}
      <div style={{ flex: 1, color: T.mute, fontSize: 12 }}>{detail}</div>
      {action}
    </div>
  );
}

function Check({ label, ok, optional }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px",
                  background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
      {ok ? <CheckCircle2 size={16} color={T.green} /> : <XCircle size={16} color={optional ? T.mute : T.red} />}
      <span style={{ fontSize: 13 }}>{label}</span>
      {optional && !ok && <span style={{ color: T.mute, fontSize: 11, marginLeft: "auto" }}>optional</span>}
    </div>
  );
}

function CredCard({ creds }) {
  const copy = () => { navigator.clipboard.writeText(creds.api_key); toast.success("API key copied"); };
  return (
    <div style={{ marginTop: 14, padding: 14, background: `${T.amber}12`, border: `1px solid ${T.amber}55`, borderRadius: 8 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, color: T.amber, fontSize: 13 }}>
        <AlertCircle size={14} /> Test credentials — copy the API key now, it won't be shown again.
      </div>
      <div style={{ fontSize: 12, color: T.mute, marginBottom: 4 }}>user_id: <code>{creds.user_id}</code></div>
      <div style={{ fontSize: 12, color: T.mute, marginBottom: 4 }}>email:   <code>{creds.email}</code></div>
      <div style={{ fontSize: 12, color: T.mute, marginBottom: 8 }}>balance: <code>{creds.balance} credits</code></div>
      <div style={{ display: "flex", gap: 8 }}>
        <code style={{ flex: 1, padding: "10px 12px", background: "rgba(0,0,0,0.5)", borderRadius: 6,
                       fontFamily: "'JetBrains Mono', monospace", fontSize: 12, wordBreak: "break-all" }}>
          {creds.api_key}
        </code>
        <button onClick={copy}
          style={{ padding: "0 14px", borderRadius: 6, background: T.teal, color: "#04070f",
                   border: "none", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
          <Copy size={14} /> Copy
        </button>
      </div>
    </div>
  );
}

function Button({ children, onClick, busy, primary, disabled }) {
  return (
    <button onClick={onClick} disabled={busy || disabled}
      style={{
        padding: "8px 14px", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: (busy || disabled) ? "not-allowed" : "pointer",
        background: primary ? `linear-gradient(90deg, ${T.teal}, ${T.violet})` : "transparent",
        color: primary ? "#04070f" : "#e6eaf2",
        border: primary ? "none" : `1px solid ${T.border2}`,
        opacity: disabled ? 0.55 : 1,
        display: "inline-flex", alignItems: "center", gap: 6,
      }}>
      {busy ? <Loader size={12} className="spin" /> : null}
      {children}
    </button>
  );
}

const inputStyle = {
  padding: "8px 10px", borderRadius: 6, fontSize: 12,
  background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border2}`, color: "#e6eaf2",
};
const btnGhost = {
  padding: "6px 10px", borderRadius: 6, fontSize: 12,
  background: "transparent", border: `1px solid ${T.border2}`, color: "#e6eaf2",
  cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4,
};
