import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft, RefreshCcw, Send, Inbox, Activity, Shield,
  CheckCircle2, Circle, ExternalLink, AlertTriangle, MessageSquare,
  Megaphone, Users, Plug, Zap
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

/* Provider layout: "chat" = messaging template, "feed" = social template */
const PROVIDER_LAYOUT = {
  slack:     "chat",
  discord:   "chat",
  telegram:  "chat",
  whatsapp:  "chat",
  x:         "feed",
  linkedin:  "feed",
  facebook:  "feed",
  instagram: "feed",
  tiktok:    "feed",
  youtube:   "feed",
};

/* Compose schema per provider — what fields appear in the composer */
const COMPOSE_SCHEMA = {
  slack:     { action: "send", fields: [{ key: "channel",  label: "Channel (#name or C…)" }, { key: "content", label: "Message", textarea: true }] },
  discord:   { action: "send", fields: [{ key: "channel_id", label: "Channel ID" }, { key: "content", label: "Message", textarea: true }] },
  telegram:  { action: "send", fields: [{ key: "chat_id", label: "Chat ID" }, { key: "content", label: "Message", textarea: true }] },
  whatsapp:  { action: "send_message", fields: [{ key: "phone_number_id", label: "Phone number ID" }, { key: "to", label: "To (E.164)" }, { key: "content", label: "Message", textarea: true }] },
  x:         { action: "post", fields: [{ key: "content", label: "Post (280 char max)", textarea: true, max: 280 }] },
  linkedin:  { action: "post", fields: [{ key: "content", label: "Post text", textarea: true, max: 3000 }] },
  facebook:  { action: "post", fields: [{ key: "page_id", label: "Page ID" }, { key: "content", label: "Post text", textarea: true }] },
  instagram: { action: "post", fields: [{ key: "ig_user_id", label: "IG Business ID" }, { key: "image_url", label: "Image URL" }, { key: "content", label: "Caption", textarea: true }] },
  tiktok:    { action: "post_video", fields: [{ key: "video_url", label: "Video URL" }, { key: "content", label: "Title (150 chars)" }] },
  youtube:   { action: "upload", fields: [{ key: "title", label: "Title" }, { key: "content", label: "Description", textarea: true }] },
};

function token() { return localStorage.getItem("access_token") || ""; }
async function apiGet(path) {
  const r = await fetch(`${API}${path}`, { headers: { Authorization: `Bearer ${token()}` } });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}
async function apiPost(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
    body: JSON.stringify(body || {}),
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}
function agoLabel(iso) {
  if (!iso) return "never";
  const t = Date.parse(iso);
  if (!t) return iso;
  const s = Math.round((Date.now() - t) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  if (s < 86400) return `${Math.round(s / 3600)}h ago`;
  return `${Math.round(s / 86400)}d ago`;
}

export default function AppDetail() {
  const { provider } = useParams();
  const layout = PROVIDER_LAYOUT[provider] || "feed";
  const composeSchema = COMPOSE_SCHEMA[provider];

  const [dash, setDash] = useState(null);
  const [feed, setFeed] = useState([]);
  const [grants, setGrants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [err, setErr] = useState("");

  const [selected, setSelected]   = useState(null);   // currently-open thread/item
  const [composer, setComposer]   = useState({});
  const [composeBusy, setComposeBusy] = useState(false);
  const [composeResult, setComposeResult] = useState(null);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [d, f, g] = await Promise.all([
        apiGet(`/integrations/${provider}/dashboard`),
        apiGet(`/integrations/${provider}/feed?limit=100`),
        apiGet(`/integrations/${provider}/agent-grants`),
      ]);
      setDash(d); setFeed(f.items || []); setGrants(g.grants || []);
      setErr("");
    } catch (e) {
      setErr(String(e?.message || e));
    } finally { setLoading(false); }
  };

  const pollNow = async () => {
    setPolling(true);
    try { await apiPost(`/integrations/${provider}/poll`); await loadAll(); }
    catch (e) { setErr(String(e?.message || e)); }
    finally { setPolling(false); }
  };

  const markSeen = async (ids) => {
    if (!ids || ids.length === 0) return;
    try { await apiPost(`/integrations/${provider}/mark-seen`, { external_ids: ids }); }
    catch {}
  };

  useEffect(() => { loadAll(); setSelected(null); setComposer({}); setComposeResult(null); }, [provider]);

  /* Chat layout: group items into threads by sender (for messaging providers) */
  const threads = useMemo(() => {
    if (layout !== "chat") return [];
    const groups = new Map();
    for (const it of feed) {
      const key = it.from || "unknown";
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(it);
    }
    return Array.from(groups.entries()).map(([from, items]) => ({
      from, items, latest: items[0], unseen: items.filter(i => !i.seen).length,
    })).sort((a, b) => {
      const ta = Date.parse(a.latest?.occurred_at || 0);
      const tb = Date.parse(b.latest?.occurred_at || 0);
      return tb - ta;
    });
  }, [feed, layout]);

  const compose = async () => {
    if (!composeSchema) return;
    setComposeBusy(true);
    setComposeResult(null);
    try {
      // Prefill messaging reply target from selected thread
      const params = { ...composer };
      if (layout === "chat" && selected) {
        if (provider === "telegram" && !params.chat_id) params.chat_id = selected.from;
        if (provider === "slack" && !params.channel)    params.channel = selected.from;
        if (provider === "discord" && !params.channel_id) params.channel_id = selected.from;
        if (provider === "whatsapp" && !params.to)      params.to = selected.from;
      }
      const res = await apiPost("/integrations/act", {
        provider, action: composeSchema.action, params,
      });
      setComposeResult(res);
      if (res?.ok) {
        setComposer({});
        await loadAll();
      }
    } catch (e) {
      setComposeResult({ ok: false, error: String(e?.message || e) });
    } finally { setComposeBusy(false); }
  };

  if (loading) return <div style={{ padding: 40, color: "#9ca3af" }}>Loading…</div>;
  if (!dash) return <div style={{ padding: 40, color: "#f87171" }}>Failed to load: {err}</div>;

  const ready = (dash.status?.ready_modes || []).length > 0;

  return (
    <div style={{ padding: "20px 28px", color: "#e5e7eb", maxWidth: 1500, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 }}>
        <div>
          <Link to="/integrations" style={{ display: "inline-flex", alignItems: "center", gap: 4, color: "#9ca3af", textDecoration: "none", fontSize: 12, marginBottom: 6 }}>
            <ArrowLeft size={12} /> Integrations
          </Link>
          <h1 style={{ fontSize: 24, margin: 0, fontWeight: 600, display: "flex", alignItems: "center", gap: 10 }}>
            {dash.display_name}
            {ready
              ? <CheckCircle2 size={18} color="#34d399" />
              : <Circle size={18} color="#52525b" />}
            <span style={{ fontSize: 10, padding: "2px 8px", background: "rgba(255,255,255,0.05)", color: "#9ca3af", borderRadius: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
              {layout === "chat" ? "Messenger" : "Feed"}
            </span>
          </h1>
          <div style={{ color: "#9ca3af", fontSize: 12, marginTop: 3 }}>
            {(dash.status?.ready_modes || []).join(" + ") || "not connected"} · polled {agoLabel(dash.last_polled_at)}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={pollNow} disabled={polling} style={btnStyle}>
            <RefreshCcw size={14} style={{ marginRight: 6 }} />
            {polling ? "Polling…" : "Refresh"}
          </button>
        </div>
      </div>

      {err && (
        <div style={{ padding: 10, background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 8, color: "#fca5a5", marginBottom: 14 }}>
          <AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: "middle" }} />{err}
        </div>
      )}

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 14 }}>
        <KPI label="24h actions" value={dash.totals_24h?.actions ?? 0} />
        <KPI label="Failed 24h" value={dash.totals_24h?.failed ?? 0} color={dash.totals_24h?.failed > 0 ? "#fca5a5" : undefined} />
        <KPI label="Error rate" value={`${dash.totals_24h?.error_rate_pct ?? 0}%`} />
        <KPI label="Unread" value={dash.unseen_count ?? 0} color={dash.unseen_count > 0 ? "#fde68a" : undefined} />
      </div>

      {/* Desktop-app-style 3-pane */}
      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr 260px", gap: 12, height: "calc(100vh - 280px)", minHeight: 500 }}>
        {/* LEFT: inbox / threads */}
        <Pane title={layout === "chat" ? "Chats" : "Inbox"} icon={Inbox} count={layout === "chat" ? threads.length : feed.length}>
          {layout === "chat"
            ? (threads.length === 0
                ? <Empty>No conversations yet.</Empty>
                : threads.map((t) => (
                  <ThreadRow
                    key={t.from}
                    thread={t}
                    active={selected?.from === t.from}
                    onClick={() => {
                      setSelected(t);
                      markSeen(t.items.filter(i => !i.seen).map(i => i.external_id));
                    }}
                  />
                )))
            : (feed.length === 0
                ? <Empty>No inbound items yet. Click Refresh after connecting.</Empty>
                : feed.slice(0, 60).map((it) => (
                  <FeedRow
                    key={it.external_id}
                    item={it}
                    active={selected?.external_id === it.external_id}
                    onClick={() => {
                      setSelected(it);
                      if (!it.seen) markSeen([it.external_id]);
                    }}
                  />
                )))
          }
        </Pane>

        {/* CENTER: conversation / composer */}
        <Pane title={selected ? (layout === "chat" ? `Chat with ${selected.from || "…"}` : selected.from || "Post") : (composeSchema ? "Compose" : "Actions")} icon={layout === "chat" ? MessageSquare : Megaphone}>
          {layout === "chat" && selected ? (
            <ChatThread thread={selected} myName="You" />
          ) : layout === "feed" && selected ? (
            <FeedItemView item={selected} />
          ) : null}

          {composeSchema ? (
            <Composer
              schema={composeSchema}
              values={composer}
              onChange={setComposer}
              onSend={compose}
              busy={composeBusy}
              result={composeResult}
              replyTarget={layout === "chat" && selected ? selected.from : null}
            />
          ) : (
            <Empty>No composer available for this provider.</Empty>
          )}
        </Pane>

        {/* RIGHT: agents + capabilities + recent actions */}
        <Pane title="Context" icon={Shield}>
          <Subhead><Users size={10} /> Agents with authority ({grants.length})</Subhead>
          {grants.length === 0
            ? <MiniEmpty>No agents granted. <Link to="/integrations" style={{ color: "#60a5fa" }}>Grant →</Link></MiniEmpty>
            : grants.slice(0, 4).map((g) => (
              <MiniCard key={g.agent_id}>
                <div style={{ fontSize: 12, color: "#e5e7eb" }}>{g.agent?.name || g.agent_id}</div>
                <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 1 }}>{(g.actions || ["all"]).join(", ")}</div>
              </MiniCard>
            ))
          }

          <Subhead><Zap size={10} /> Capabilities ({(dash.actions_available || []).length})</Subhead>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 10 }}>
            {(dash.actions_available || []).map((a) => (
              <span key={a} style={{ padding: "2px 7px", background: "rgba(124,58,237,0.15)", color: "#c4b5fd", borderRadius: 3, fontSize: 10 }}>{a}</span>
            ))}
          </div>

          <Subhead><Activity size={10} /> Recent actions</Subhead>
          {(dash.recent_actions || []).length === 0
            ? <MiniEmpty>None yet.</MiniEmpty>
            : (dash.recent_actions || []).slice(0, 6).map((a, i) => (
              <MiniCard key={i}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
                  <span style={{ color: a.ok ? "#34d399" : "#fca5a5" }}>{a.ok ? "✓" : "✗"} {a.action}</span>
                  <span style={{ color: "#71717a", fontSize: 10 }}>{agoLabel(a.at)}</span>
                </div>
              </MiniCard>
            ))
          }

          <Subhead><Plug size={10} /> Connection</Subhead>
          <MiniCard>
            <div style={{ fontSize: 11, color: "#9ca3af" }}>
              API credential: {dash.status?.has_api_credential ? "✓" : "—"}<br />
              Modes: {(dash.status?.modes_available || []).join(", ") || "none"}
            </div>
            <Link to="/integrations" style={{ fontSize: 11, color: "#60a5fa", textDecoration: "none" }}>Manage →</Link>
          </MiniCard>
        </Pane>
      </div>
    </div>
  );
}

/* ── Subcomponents ─────────────────────────────────────────────── */

function KPI({ label, value, color }) {
  return (
    <div style={{ padding: 12, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10 }}>
      <div style={{ fontSize: 10, color: "#9ca3af", textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 600, color: color || "#f3f4f6", marginTop: 2 }}>{value}</div>
    </div>
  );
}

function Pane({ title, icon: Icon, count, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, minHeight: 0 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 12px", borderBottom: "1px solid rgba(255,255,255,0.06)", flexShrink: 0 }}>
        <Icon size={13} color="#a78bfa" />
        <div style={{ fontSize: 12, fontWeight: 600, color: "#f3f4f6" }}>{title}</div>
        {typeof count === "number" && (
          <div style={{ fontSize: 10, color: "#71717a", marginLeft: "auto" }}>{count}</div>
        )}
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 10 }}>{children}</div>
    </div>
  );
}

function Empty({ children }) {
  return <div style={{ color: "#6b7280", fontSize: 12, padding: "20px 0", textAlign: "center" }}>{children}</div>;
}
function MiniEmpty({ children }) {
  return <div style={{ color: "#71717a", fontSize: 11, padding: "6px 0" }}>{children}</div>;
}
function Subhead({ children }) {
  return <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: "#9ca3af", textTransform: "uppercase", letterSpacing: 0.5, marginTop: 10, marginBottom: 4 }}>{children}</div>;
}
function MiniCard({ children }) {
  return <div style={{ padding: "6px 8px", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 5, marginBottom: 4 }}>{children}</div>;
}

function ThreadRow({ thread, active, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: "10px 11px", cursor: "pointer", borderRadius: 8, marginBottom: 3,
        background: active ? "rgba(124,58,237,0.18)" : thread.unseen > 0 ? "rgba(251,191,36,0.05)" : "transparent",
        border: active ? "1px solid rgba(124,58,237,0.4)" : "1px solid transparent",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: "#f3f4f6", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{thread.from}</div>
        {thread.unseen > 0 && (
          <span style={{ background: "#f59e0b", color: "#1c1917", fontSize: 10, fontWeight: 600, borderRadius: 8, padding: "1px 6px" }}>{thread.unseen}</span>
        )}
      </div>
      <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {thread.latest?.preview || "(no text)"}
      </div>
      <div style={{ fontSize: 10, color: "#71717a", marginTop: 2 }}>{agoLabel(thread.latest?.occurred_at)}</div>
    </div>
  );
}

function FeedRow({ item, active, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: "10px 11px", cursor: "pointer", borderRadius: 8, marginBottom: 4,
        background: active ? "rgba(124,58,237,0.18)" : !item.seen ? "rgba(251,191,36,0.05)" : "rgba(255,255,255,0.02)",
        border: active ? "1px solid rgba(124,58,237,0.4)" : "1px solid rgba(255,255,255,0.05)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#9ca3af", marginBottom: 3 }}>
        <span style={{ textTransform: "uppercase", letterSpacing: 0.5, color: "#a78bfa" }}>{item.kind}</span>
        <span>{agoLabel(item.occurred_at)}</span>
      </div>
      <div style={{ fontSize: 12, color: "#e5e7eb", fontWeight: 500 }}>{item.from || "unknown"}</div>
      <div style={{ fontSize: 11, color: "#d1d5db", marginTop: 2, lineHeight: 1.35, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{item.preview || "(no text)"}</div>
    </div>
  );
}

function ChatThread({ thread, myName }) {
  const items = (thread.items || []).slice().reverse();  // oldest → newest
  return (
    <div style={{ marginBottom: 12 }}>
      {items.map((m) => (
        <div key={m.external_id} style={{ marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#9ca3af", marginBottom: 3 }}>
            <span style={{ color: "#e5e7eb", fontWeight: 500 }}>{m.from || "unknown"}</span>
            <span>{agoLabel(m.occurred_at)}</span>
          </div>
          <div style={{ padding: "8px 10px", background: "rgba(255,255,255,0.04)", borderRadius: 8, fontSize: 13, color: "#f3f4f6", lineHeight: 1.4 }}>
            {m.preview || "(no text)"}
          </div>
        </div>
      ))}
    </div>
  );
}

function FeedItemView({ item }) {
  return (
    <div style={{ marginBottom: 14, padding: "14px 14px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#9ca3af", marginBottom: 6 }}>
        <span style={{ color: "#a78bfa", textTransform: "uppercase", letterSpacing: 0.5 }}>{item.kind}</span>
        <span>{agoLabel(item.occurred_at)}</span>
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: "#f3f4f6" }}>{item.from || "unknown"}</div>
      <div style={{ fontSize: 13, color: "#e5e7eb", marginTop: 8, lineHeight: 1.5, whiteSpace: "pre-wrap" }}>{item.preview || "(no text)"}</div>
      {item.url && (
        <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, color: "#60a5fa", marginTop: 10, textDecoration: "none" }}>
          View original <ExternalLink size={11} />
        </a>
      )}
    </div>
  );
}

function Composer({ schema, values, onChange, onSend, busy, result, replyTarget }) {
  const textVal = (k) => values[k] ?? "";
  return (
    <div style={{ marginTop: 10, padding: 12, background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 8 }}>
      <div style={{ fontSize: 11, color: "#9ca3af", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 8 }}>
        {schema.action}{replyTarget ? ` → ${replyTarget}` : ""}
      </div>
      {schema.fields.map((f) => (
        <div key={f.key} style={{ marginBottom: 8 }}>
          <label style={{ fontSize: 10, color: "#9ca3af", display: "block", marginBottom: 3 }}>
            {f.label}{f.max ? ` (${textVal(f.key).length}/${f.max})` : ""}
          </label>
          {f.textarea ? (
            <textarea
              value={textVal(f.key)}
              onChange={(e) => onChange({ ...values, [f.key]: e.target.value })}
              rows={3}
              maxLength={f.max}
              style={inputStyle}
            />
          ) : (
            <input
              type="text"
              value={textVal(f.key)}
              onChange={(e) => onChange({ ...values, [f.key]: e.target.value })}
              style={inputStyle}
            />
          )}
        </div>
      ))}
      <button onClick={onSend} disabled={busy} style={{ ...btnStyle, background: "#7c3aed", borderColor: "#7c3aed", color: "#fff", width: "100%" }}>
        <Send size={14} style={{ marginRight: 6 }} />
        {busy ? "Sending…" : "Send"}
      </button>
      {result && (
        <div style={{ marginTop: 8, padding: 8, background: result.ok ? "rgba(52,211,153,0.08)" : "rgba(239,68,68,0.08)", border: `1px solid ${result.ok ? "rgba(52,211,153,0.25)" : "rgba(239,68,68,0.25)"}`, borderRadius: 6, color: result.ok ? "#86efac" : "#fca5a5", fontSize: 11 }}>
          {result.ok ? `Sent via ${result.mode} (${result.latency_ms}ms)` : `Failed: ${result.error || "unknown"}`}
        </div>
      )}
    </div>
  );
}

const btnStyle = {
  display: "inline-flex", alignItems: "center", justifyContent: "center",
  padding: "8px 14px", background: "rgba(255,255,255,0.04)",
  border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8,
  color: "#e5e7eb", cursor: "pointer", fontSize: 12, fontWeight: 500,
};
const inputStyle = {
  width: "100%", boxSizing: "border-box",
  background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 6, padding: "7px 10px", color: "#e5e7eb",
  fontSize: 13, outline: "none", fontFamily: "inherit", resize: "vertical",
};
