import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth, API } from "../App";
import {
  Globe, ArrowLeft, ArrowRight, RotateCw, Power, X,
  Hand, Bot, Sparkles, Lock, Unlock, Loader2, Plus, Monitor,
  Gauge, Play, Eye, StopCircle, CheckCircle2, AlertCircle,
  Maximize2, Minimize2, Plug, Layers, Zap,
} from "lucide-react";
import { toast } from "sonner";

/* ─── Design tokens ──────────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  blue:   "#2563eb",
  amber:  "#f59e0b",
  pink:   "#f472b6",
  green:  "#34d399",
  red:    "#ef4444",
  border: "rgba(255,255,255,0.08)",
  glass:  "rgba(8,15,28,0.75)",
  glass2: "rgba(5,10,20,0.9)",
  bg:     "#030712",
  text:   "#e5e7eb",
  mute:   "#94a3b8",
};

const DRIVER_BADGE = {
  shared: { color: T.mute,  icon: Sparkles, label: "Shared" },
  user:   { color: T.green, icon: Hand,     label: "User in control" },
  agent:  { color: T.teal,  icon: Bot,      label: "Agent in control" },
  system: { color: T.amber, icon: Monitor,  label: "System in control" },
};

const INTEGRATION_MATURITY_COLOR = {
  live:    T.green,
  hybrid:  T.amber,
  planned: T.mute,
};

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, { method = "GET", body, baseOverride } = {}) {
  const base = baseOverride || `${API}/browser`;
  const url = `${base}${path}`;
  const headers = { ...authHeaders() };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  let resp;
  try {
    resp = await fetch(url, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    console.error("[BrowserPanel] fetch failed", { url, method, error: networkErr });
    throw new Error(`network error contacting ${url} (${networkErr.message}).`);
  }
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`${resp.status} from ${url}: ${err}`);
  }
  const raw = await resp.text();
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    const preview = raw.slice(0, 240).replace(/\s+/g, " ");
    throw new Error(`invalid JSON from ${url}: ${preview}`);
  }
}

function extractIntegrationList(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.integrations)) return payload.integrations;
  if (payload && Array.isArray(payload.available)) return payload.available;
  return [];
}

function hasIntegrationShape(payload) {
  return (
    Array.isArray(payload) ||
    (payload && Array.isArray(payload.integrations)) ||
    (payload && Array.isArray(payload.available))
  );
}

function normalizeIntegrations(payload) {
  const byId = new Map();
  for (const raw of extractIntegrationList(payload)) {
    if (!raw || typeof raw !== "object") continue;
    const integrationId = String(raw.integration_id || raw.id || "").trim();
    if (!integrationId) continue;
    const key = integrationId.toLowerCase();
    if (byId.has(key)) continue;
    byId.set(key, {
      ...raw,
      integration_id: integrationId,
      name: raw.name || integrationId,
    });
  }
  return [...byId.values()].sort((a, b) =>
    String(a.name || a.integration_id).localeCompare(String(b.name || b.integration_id))
  );
}

/* ─── Main ─────────────────────────────────────────────────────────────── */
export default function BrowserPanel() {
  useAuth();
  const [health, setHealth]       = useState(null);
  const [sessions, setSessions]   = useState([]);
  const [active, setActive]       = useState(null);     // session state
  const [frame, setFrame]         = useState(null);     // base64
  const [frameMime, setFrameMime] = useState("image/png");
  const [connected, setConnected] = useState(false);
  const [urlInput, setUrlInput]   = useState("https://www.google.com");
  const [busy, setBusy]           = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [leftTab, setLeftTab]     = useState("sessions");   // "sessions" | "integrations"
  const [integrations, setIntegrations] = useState([]);
  const [integrationsLoading, setIntegrationsLoading] = useState(false);
  const [integrationsError, setIntegrationsError] = useState("");

  // Streaming config
  const [streamMode, setStreamMode] = useState(() => localStorage.getItem("browserStreamMode") || "event");
  const [streamFmt,  setStreamFmt]  = useState(() => localStorage.getItem("browserStreamFmt")  || "png");
  const [streamFps,  setStreamFps]  = useState(() => Number(localStorage.getItem("browserStreamFps")) || 10);

  // Agent runner
  const [goal, setGoal]             = useState("");
  const [agentEvents, setAgentEvents] = useState([]);
  const [agentRunning, setAgentRunning] = useState(false);
  const agentAbort = useRef(null);

  const [usage, setUsage] = useState(null);

  const wsRef     = useRef(null);
  const canvasRef = useRef(null);
  const imageRef  = useRef(null);
  const rootRef   = useRef(null);

  /* --- health + session list ------------------------------------------ */
  const loadHealth = useCallback(async () => {
    try { setHealth(await api("/health")); }
    catch (e) { setHealth({ available: false, install_hint: String(e) }); }
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const list = await api("/sessions");
      setSessions(list);
      // Honor ?session=X from a deep link (e.g. from the Integration
      // Hub's "Connect Browser" button) so the operator lands on the
      // right Playwright session without manually picking it.
      const qs = new URLSearchParams(window.location.search);
      const wantedId = qs.get("session");
      if (wantedId) {
        const match = list.find(s => s.session_id === wantedId);
        if (match) { setActive(match); return; }
      }
      if (list.length && !active) setActive(list[0]);
    } catch (_) { /* auth / unavailable */ }
  }, [active]);

  const loadUsage = useCallback(async () => {
    try { setUsage(await api("/usage")); } catch (_) { /* ignore */ }
  }, []);

  const loadIntegrations = useCallback(async () => {
    setIntegrationsLoading(true);
    setIntegrationsError("");
    try {
      try {
        const enterprisePayload = await api("/integrations", { baseOverride: `${API}/enterprise` });
        const normalized = normalizeIntegrations(enterprisePayload);
        if (normalized.length > 0 || hasIntegrationShape(enterprisePayload)) {
          setIntegrations(normalized);
          return;
        }
      } catch (_) {
        // fall through to kernel fallback
      }

      try {
        const kernelPayload = await api("/integrations/available", { baseOverride: `${API}/kernel` });
        setIntegrations(normalizeIntegrations(kernelPayload));
      } catch (_) {
        setIntegrations([]);
        setIntegrationsError("Could not load integrations right now.");
      }
    } finally {
      setIntegrationsLoading(false);
    }
  }, []);

  useEffect(() => { loadHealth(); loadSessions(); loadUsage(); loadIntegrations(); },
           [loadHealth, loadSessions, loadUsage, loadIntegrations]);

  useEffect(() => {
    if (!health || health.available) return;
    const id = setInterval(() => { loadHealth(); }, 3000);
    return () => clearInterval(id);
  }, [health, loadHealth]);

  useEffect(() => { localStorage.setItem("browserStreamMode", streamMode); }, [streamMode]);
  useEffect(() => { localStorage.setItem("browserStreamFmt",  streamFmt);  }, [streamFmt]);
  useEffect(() => { localStorage.setItem("browserStreamFps",  String(streamFps));  }, [streamFps]);

  /* --- fullscreen ------------------------------------------------------ */
  async function toggleFullscreen() {
    try {
      if (!document.fullscreenElement) {
        await rootRef.current?.requestFullscreen?.();
      } else {
        await document.exitFullscreen?.();
      }
    } catch (e) { toast.error(`fullscreen: ${e.message}`); }
  }
  useEffect(() => {
    const h = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", h);
    return () => document.removeEventListener("fullscreenchange", h);
  }, []);

  /* --- sessions + tabs ------------------------------------------------- */
  async function openSession() {
    setBusy(true);
    try {
      const s = await api("/sessions", { method: "POST", body: { start_url: urlInput } });
      setActive(s);
      await loadSessions();
    } catch (e) {
      if (/^503/.test(e.message || "")) { await loadHealth(); }
      toast.error(`Could not open session: ${e.message}`);
    } finally { setBusy(false); }
  }

  async function closeSession(id) {
    try { await api(`/sessions/${id}`, { method: "DELETE" }); } catch (_) {}
    if (active?.session_id === id) { setActive(null); setFrame(null); }
    await loadSessions();
  }

  async function openTab(url) {
    if (!active) return;
    try {
      await api(`/sessions/${active.session_id}/tabs`, { method: "POST", body: { url: url || "about:blank" } });
    } catch (e) { toast.error(`new tab: ${e.message}`); }
  }

  async function switchTab(tabId) {
    if (!active) return;
    try { await api(`/sessions/${active.session_id}/tabs/${tabId}/activate`, { method: "POST" }); }
    catch (e) { toast.error(`switch tab: ${e.message}`); }
  }

  async function closeTab(tabId) {
    if (!active) return;
    try { await api(`/sessions/${active.session_id}/tabs/${tabId}`, { method: "DELETE" }); }
    catch (e) { toast.error(`close tab: ${e.message}`); }
  }

  async function connectIntegration(integrationId) {
    try {
      const res = await api(`/integrations/${integrationId}/connect`, {
        method: "POST",
        body: { session_id: active?.session_id, run_agent: false },
      });
      await loadSessions();
      if (res.session_id) setActive((a) => a?.session_id === res.session_id ? a : { session_id: res.session_id });
      toast.success(`opened ${integrationId} in a new tab`);
      setLeftTab("sessions");
    } catch (e) { toast.error(`connect ${integrationId}: ${e.message}`); }
  }

  /* --- WebSocket ------------------------------------------------------- */
  useEffect(() => {
    if (!active?.session_id) return;
    const token = localStorage.getItem("token") || "";
    const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
    const wsHost = /^https?:/.test(API) ? new URL(API).host : window.location.host;
    const qs = new URLSearchParams({ token, stream: streamMode, fmt: streamFmt, fps: String(streamFps) });
    const url = `${wsProto}://${wsHost}/api/browser/sessions/${active.session_id}/ws?${qs.toString()}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen    = () => setConnected(true);
    ws.onclose   = () => setConnected(false);
    ws.onerror   = () => setConnected(false);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "frame" && msg.image_base64) {
          setFrame(msg.image_base64);
          setFrameMime(msg.mime || "image/png");
          if (msg.state) setActive((a) => a ? { ...a, ...msg.state } : msg.state);
        } else if (msg.type === "error") {
          toast.error(msg.message || "browser error");
        }
      } catch (_) {}
    };
    return () => { ws.close(); };
  }, [active?.session_id, streamMode, streamFmt, streamFps]);

  /* --- render screenshot to canvas ------------------------------------ */
  useEffect(() => {
    if (!frame) return;
    const img = new Image();
    img.onload = () => {
      imageRef.current = img;
      const cv = canvasRef.current;
      if (!cv) return;
      cv.width  = img.naturalWidth;
      cv.height = img.naturalHeight;
      cv.getContext("2d").drawImage(img, 0, 0);
    };
    img.src = `data:${frameMime};base64,${frame}`;
  }, [frame, frameMime]);

  /* --- user input forwarding ------------------------------------------ */
  function sendWS(msg) {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify(msg));
  }
  function handleCanvasClick(e) {
    const cv = canvasRef.current;
    if (!cv || !imageRef.current) return;
    const rect = cv.getBoundingClientRect();
    const scaleX = imageRef.current.naturalWidth  / rect.width;
    const scaleY = imageRef.current.naturalHeight / rect.height;
    sendWS({ type: "click", x: Math.round((e.clientX - rect.left) * scaleX), y: Math.round((e.clientY - rect.top) * scaleY) });
  }
  function handleKey(e) {
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) sendWS({ type: "type", text: e.key });
    else sendWS({ type: "key", key: e.key });
    e.preventDefault();
  }
  function handleWheel(e) { sendWS({ type: "scroll", dy: Math.round(e.deltaY) }); e.preventDefault(); }

  const navTo     = (u) => { if (u) sendWS({ type: "navigate", url: u }); };
  const goBack    = () => sendWS({ type: "key", key: "Alt+ArrowLeft" });
  const goForward = () => sendWS({ type: "key", key: "Alt+ArrowRight" });
  const reload    = () => active && sendWS({ type: "navigate", url: active.url });

  async function takeControl() {
    if (!active) return;
    await api(`/sessions/${active.session_id}/take-control`, { method: "POST", body: { driver: "user" } });
    setActive((a) => ({ ...a, driver: "user" }));
  }
  async function releaseControl() {
    if (!active) return;
    await api(`/sessions/${active.session_id}/release-control`, { method: "POST", body: { driver: "user" } });
    setActive((a) => ({ ...a, driver: "shared" }));
  }

  /* --- autonomous agent runner (SSE) ---------------------------------- */
  async function runAgentGoal() {
    if (!goal.trim()) { toast.error("Describe the goal first"); return; }
    if (agentRunning) return;
    setAgentEvents([]);
    setAgentRunning(true);
    const controller = new AbortController();
    agentAbort.current = controller;
    try {
      const resp = await fetch(`${API}/browser/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          goal, session_id: active?.session_id || undefined,
          start_url: active ? undefined : urlInput, max_steps: 20,
        }),
        signal: controller.signal,
      });
      if (!resp.ok || !resp.body) {
        throw new Error((await resp.text()) || `HTTP ${resp.status}`);
      }
      const reader = resp.body.getReader(); const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buffer.indexOf("\n\n")) >= 0) {
          const chunk = buffer.slice(0, idx); buffer = buffer.slice(idx + 2);
          const line = chunk.split("\n").find((l) => l.startsWith("data:"));
          if (!line) continue;
          try {
            const evt = JSON.parse(line.slice(5).trim());
            setAgentEvents((ev) => [...ev, evt]);
            if (evt.state) setActive((a) => a ? { ...a, ...evt.state } : evt.state);
            if (evt.kind === "done")  toast.success(evt.message || "Agent done");
            if (evt.kind === "error") toast.error(evt.message || "Agent error");
          } catch (_) {}
        }
      }
    } catch (e) {
      if (e.name !== "AbortError") toast.error(`Agent run failed: ${e.message}`);
    } finally {
      setAgentRunning(false); agentAbort.current = null;
      loadUsage(); loadSessions();
    }
  }
  function stopAgent() { agentAbort.current?.abort(); }

  /* --- Commander-driven goal ----------------------------------------- */
  async function runCommanderGoal() {
    if (!goal.trim()) { toast.error("Describe the goal first"); return; }
    if (!active?.session_id) { toast.error("Open a session first"); return; }
    if (agentRunning) return;
    setAgentEvents([]);
    setAgentRunning(true);
    try {
      const resp = await fetch(`${API}/commander/drive-browser`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          session_id: active.session_id,
          goal,
          max_steps: 10,
        }),
      });
      if (!resp.ok) throw new Error((await resp.text()) || `HTTP ${resp.status}`);
      const data = await resp.json();
      (data.trace || []).forEach(t => setAgentEvents(ev => [...ev, { kind: t.kind, message: t.summary, step: t.step }]));
      toast.success(`Commander Orion ran ${data.steps} step(s) toward: ${data.goal.slice(0, 60)}…`);
    } catch (e) {
      toast.error(`Commander drive failed: ${e.message}`);
    } finally {
      setAgentRunning(false);
      loadUsage(); loadSessions();
    }
  }

  /* ─── Render ────────────────────────────────────────────────────── */
  const notAvailable = health && !health.available;
  const activeTabs   = active?.tabs || [];

  return (
    <div ref={rootRef} style={{
      minHeight: "100vh",
      background: T.bg, color: T.text,
      padding: fullscreen ? 12 : 20,
    }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <Globe size={28} color={T.blue} />
        <div>
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Embedded Browser</h1>
          <p style={{ margin: 0, fontSize: 12, color: T.mute }}>
            Chromium inside MAARS. Agents, the system, and you share the same session.
          </p>
        </div>
        <div style={{ flex: 1 }} />
        {usage && (
          <div title={`Today's browser minutes: ${usage.minutes_used}/${usage.unlimited ? '∞' : usage.budget_minutes}`}
               style={{ fontSize: 11, color: T.mute, display: "flex", alignItems: "center", gap: 4 }}>
            <Gauge size={12} />
            {usage.unlimited
              ? `${Math.round(usage.minutes_used)} min today`
              : `${Math.round(usage.minutes_used)}/${usage.budget_minutes} min`}
          </div>
        )}
        {connected && <span style={{ fontSize: 11, color: T.green }}>● connected</span>}
        {!connected && active && <span style={{ fontSize: 11, color: T.amber }}>○ connecting…</span>}
        <button onClick={toggleFullscreen} style={{ ...btnStyle(), background: `${T.blue}20`, borderColor: T.blue }}
                title={fullscreen ? "Exit fullscreen" : "Enter fullscreen"}>
          {fullscreen ? <Minimize2 size={14}/> : <Maximize2 size={14}/>}
        </button>
      </div>

      {/* Origin strip */}
      <div style={{
        display: "flex", gap: 8, alignItems: "center",
        fontSize: 10, color: T.mute, marginBottom: 8, fontFamily: "ui-monospace, monospace",
      }}>
        <span>page: {typeof window !== "undefined" ? window.location.origin : "?"}</span>
        <span>·</span>
        <span>api: {API}</span>
        <span>·</span>
        <span style={{ color: health?.available ? T.green : T.amber }}>
          health: {health === null ? "loading…" : health.available ? "ok" : "unavailable"}
        </span>
      </div>

      {/* Install-needed banner */}
      {notAvailable && (
        <div style={{
          padding: 14, background: "rgba(239,68,68,0.08)", border: `1px solid ${T.red}40`,
          borderRadius: 10, marginBottom: 12, fontSize: 13, whiteSpace: "pre-wrap",
          display: "flex", alignItems: "flex-start", gap: 12,
        }}>
          <div style={{ flex: 1 }}>
            <strong style={{ color: T.red }}>Browser engine not installed.</strong>{"\n"}
            {health?.install_hint}
          </div>
          <button onClick={loadHealth} style={{ ...btnStyle(), flexShrink: 0, borderColor: T.red, background: `${T.red}20` }}>
            <RotateCw size={12} /> Retry
          </button>
        </div>
      )}

      {/* Stream toolbar + Agent goal runner */}
      <div style={{
        display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center",
        padding: "10px 12px", background: T.glass, border: `1px solid ${T.border}`,
        borderRadius: 12, marginBottom: 12, fontSize: 12,
      }}>
        <span style={{ color: T.mute, marginRight: 4 }}>Stream:</span>
        <select value={streamMode} onChange={(e) => setStreamMode(e.target.value)} style={selectStyle}>
          <option value="event">on change</option>
          <option value="continuous">continuous</option>
        </select>
        <select value={streamFmt} onChange={(e) => setStreamFmt(e.target.value)} style={selectStyle}>
          <option value="png">PNG (crisp)</option>
          <option value="jpeg">JPEG (fast)</option>
        </select>
        {streamMode === "continuous" && (
          <>
            <span style={{ color: T.mute }}>fps:</span>
            <input type="number" min={1} max={24} value={streamFps}
                   onChange={(e) => setStreamFps(Math.max(1, Math.min(24, Number(e.target.value))))}
                   style={{ ...selectStyle, width: 52 }} />
          </>
        )}
        <div style={{ width: 1, height: 20, background: T.border, margin: "0 6px" }} />
        <Bot size={14} color={T.teal} />
        <input
          type="text"
          placeholder="Goal for autonomous BrowserAgent (e.g. 'log in to Gmail and find the last invoice from Stripe')"
          value={goal} onChange={(e) => setGoal(e.target.value)}
          style={{ flex: 1, minWidth: 280, padding: "6px 10px", borderRadius: 6,
                   background: "rgba(0,0,0,0.35)", border: `1px solid ${T.border}`, color: T.text, fontSize: 12 }}
          disabled={agentRunning}
          onKeyDown={(e) => e.key === "Enter" && runAgentGoal()}
        />
        {!agentRunning
          ? <>
              <button onClick={runAgentGoal} disabled={!goal.trim()}
                      title="Run the generic BrowserAgent (vision → action loop)"
                      style={{ ...btnStyle(), background: `${T.teal}25`, borderColor: T.teal }}>
                <Play size={12} /> Run
              </button>
              <button onClick={runCommanderGoal} disabled={!goal.trim() || !active?.session_id}
                      title="Commander Orion drives this session toward the goal. His authority, training, and audit trail apply."
                      style={{ ...btnStyle(),
                               background: "linear-gradient(90deg, rgba(168,85,247,0.3), rgba(79,209,197,0.3))",
                               borderColor: "rgba(168,85,247,0.5)", color: "#c4b5fd" }}>
                <Sparkles size={12} /> Commander
              </button>
            </>
          : <button onClick={stopAgent} style={{ ...btnStyle(), background: `${T.red}25`, borderColor: T.red }}>
              <StopCircle size={12} /> Stop
            </button>
        }
      </div>

      {/* Agent event log */}
      {(agentRunning || agentEvents.length > 0) && (
        <div style={{
          maxHeight: 180, overflow: "auto", marginBottom: 12,
          background: "rgba(0,0,0,0.45)", border: `1px solid ${T.border}`, borderRadius: 12,
          fontSize: 11, fontFamily: "ui-monospace, monospace",
        }}>
          {agentEvents.length === 0 && (
            <div style={{ padding: 10, color: T.mute }}>
              <Loader2 size={12} className="animate-spin" style={{ display: "inline", marginRight: 6 }} />
              Agent starting…
            </div>
          )}
          {agentEvents.map((evt, i) => {
            const color =
              evt.kind === "done"    ? T.green :
              evt.kind === "error"   ? T.red   :
              evt.kind === "handoff" ? T.amber :
              evt.kind === "waiting_for_user" ? T.amber :
              evt.kind === "action"  ? T.teal  : T.mute;
            const Icon =
              evt.kind === "done"    ? CheckCircle2 :
              evt.kind === "error"   ? AlertCircle  :
              evt.kind === "handoff" ? Hand         :
              evt.kind === "action"  ? Eye          : Sparkles;
            return (
              <div key={i} style={{
                padding: "6px 10px", borderBottom: `1px solid ${T.border}`,
                display: "flex", alignItems: "flex-start", gap: 6,
              }}>
                <Icon size={12} color={color} style={{ flexShrink: 0, marginTop: 2 }} />
                <span style={{ color, width: 48, flexShrink: 0 }}>{evt.kind}</span>
                <span style={{ color: T.mute, width: 40, flexShrink: 0 }}>#{evt.step}</span>
                <span style={{ color: T.text, flex: 1, wordBreak: "break-word" }}>
                  {evt.action?.kind ? `${evt.action.kind}` : ""}
                  {evt.action?.reason && `  —  ${evt.action.reason}`}
                  {!evt.action && evt.message}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 12 }}>
        {/* Left sidebar — sessions or integrations */}
        <aside style={{
          background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12,
          padding: 12, height: "fit-content",
        }}>
          {/* Tabs for sidebar */}
          <div style={{ display: "flex", gap: 4, marginBottom: 10 }}>
            <button onClick={() => setLeftTab("sessions")}
                    style={{
                      ...tabPill, flex: 1,
                      background: leftTab === "sessions" ? `${T.blue}25` : "transparent",
                      borderColor: leftTab === "sessions" ? T.blue : T.border,
                    }}>
              <Layers size={12} style={{ marginRight: 4 }} />
              Sessions
            </button>
            <button onClick={() => setLeftTab("integrations")}
                    style={{
                      ...tabPill, flex: 1,
                      background: leftTab === "integrations" ? `${T.blue}25` : "transparent",
                      borderColor: leftTab === "integrations" ? T.blue : T.border,
                    }}>
              <Plug size={12} style={{ marginRight: 4 }} />
              Integrations
            </button>
          </div>

          {leftTab === "sessions" && (
            <>
              <button onClick={openSession} disabled={busy || notAvailable}
                      style={{
                        width: "100%", padding: 10, borderRadius: 8, border: `1px solid ${T.blue}60`,
                        background: `${T.blue}20`, color: T.text, cursor: busy ? "wait" : "pointer",
                        fontSize: 12, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                        opacity: notAvailable ? 0.5 : 1,
                      }}>
                {busy ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                New session
              </button>
              <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                {sessions.length === 0 && (
                  <div style={{ fontSize: 11, color: T.mute, padding: 8, textAlign: "center" }}>
                    No active sessions
                  </div>
                )}
                {sessions.map((s) => {
                  const isActive = active?.session_id === s.session_id;
                  const d = DRIVER_BADGE[s.driver || "shared"] || DRIVER_BADGE.shared;
                  const DIcon = d.icon;
                  return (
                    <div key={s.session_id} onClick={() => setActive(s)} style={{
                      padding: 10, borderRadius: 8,
                      background: isActive ? `${T.blue}25` : "rgba(255,255,255,0.03)",
                      border: `1px solid ${isActive ? T.blue + "60" : T.border}`,
                      cursor: "pointer",
                    }}>
                      <div style={{ fontSize: 12, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {s.title || s.url || "(blank)"}
                      </div>
                      <div style={{ fontSize: 10, color: T.mute, marginTop: 4, display: "flex", alignItems: "center", gap: 4 }}>
                        <DIcon size={10} color={d.color} />
                        <span>{d.label}</span>
                        {s.tabs && <span>· {s.tabs.length} tab{s.tabs.length === 1 ? "" : "s"}</span>}
                        <button onClick={(e) => { e.stopPropagation(); closeSession(s.session_id); }}
                                style={{ marginLeft: "auto", background: "none", border: "none", color: T.mute, cursor: "pointer" }}
                                aria-label="close">
                          <X size={12} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {leftTab === "integrations" && (
            <>
              <div style={{ fontSize: 11, color: T.mute, marginBottom: 8 }}>
                Click to open in a new tab. Agent can drive OAuth / login flows; you handle 2FA.
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                {integrations.map((it) => {
                  const color = INTEGRATION_MATURITY_COLOR[it.runtime_support || it.maturity || "hybrid"] || T.mute;
                  return (
                    <button key={it.integration_id}
                            onClick={() => connectIntegration(it.integration_id)}
                            title={`${it.name} — ${it.runtime_support || it.maturity || ""}`}
                            style={{
                              padding: "8px 6px", borderRadius: 8,
                              background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`,
                              color: T.text, cursor: "pointer", fontSize: 11,
                              display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
                              borderLeft: `3px solid ${color}`,
                            }}>
                      <Zap size={14} color={color} />
                      <span style={{ fontSize: 10, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", width: "100%", textAlign: "center" }}>
                        {it.name || it.integration_id}
                      </span>
                    </button>
                  );
                })}
                {integrationsLoading && (
                  <div style={{ gridColumn: "1 / -1", fontSize: 11, color: T.mute, padding: 8, textAlign: "center" }}>
                    Loading integrations…
                  </div>
                )}
                {!integrationsLoading && integrationsError && (
                  <div style={{ gridColumn: "1 / -1", fontSize: 11, color: T.red, padding: 8, textAlign: "center" }}>
                    {integrationsError}
                  </div>
                )}
                {!integrationsLoading && !integrationsError && integrations.length === 0 && (
                  <div style={{ gridColumn: "1 / -1", fontSize: 11, color: T.mute, padding: 8, textAlign: "center" }}>
                    No integrations available.
                  </div>
                )}
              </div>
            </>
          )}
        </aside>

        {/* Main viewport */}
        <main style={{ background: T.glass2, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
          {/* Tab strip */}
          {active && activeTabs.length > 0 && (
            <div style={{
              display: "flex", alignItems: "stretch", gap: 2,
              background: "rgba(0,0,0,0.45)", borderBottom: `1px solid ${T.border}`,
              padding: "6px 6px 0", overflowX: "auto",
            }}>
              {activeTabs.map((t) => {
                const isActive = t.is_active || t.tab_id === active.active_tab_id;
                const host = (() => { try { return new URL(t.url).host; } catch { return t.url || ""; }})();
                return (
                  <div key={t.tab_id}
                       onClick={() => !isActive && switchTab(t.tab_id)}
                       style={{
                         display: "flex", alignItems: "center", gap: 6,
                         padding: "6px 10px", maxWidth: 220,
                         background: isActive ? T.glass2 : "transparent",
                         borderTop: `2px solid ${isActive ? T.blue : "transparent"}`,
                         borderLeft:  `1px solid ${T.border}`,
                         borderRight: `1px solid ${T.border}`,
                         borderRadius: "6px 6px 0 0",
                         cursor: isActive ? "default" : "pointer",
                         fontSize: 11, color: isActive ? T.text : T.mute,
                         whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                       }}>
                    <Globe size={11} style={{ flexShrink: 0 }} />
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {t.label || t.title || host || "blank"}
                    </span>
                    {activeTabs.length > 1 && (
                      <button onClick={(e) => { e.stopPropagation(); closeTab(t.tab_id); }}
                              style={{ background: "none", border: "none", color: T.mute, cursor: "pointer", padding: 0 }}>
                        <X size={11} />
                      </button>
                    )}
                  </div>
                );
              })}
              <button onClick={() => openTab("about:blank")}
                      style={{ background: "none", border: "none", color: T.mute, cursor: "pointer", padding: "6px 10px" }}
                      title="New tab">
                <Plus size={12} />
              </button>
            </div>
          )}

          {/* URL bar */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: 10, background: "rgba(0,0,0,0.35)", borderBottom: `1px solid ${T.border}`,
          }}>
            <button onClick={goBack}    style={btnStyle()} title="Back"    disabled={!active}><ArrowLeft size={14}/></button>
            <button onClick={goForward} style={btnStyle()} title="Forward" disabled={!active}><ArrowRight size={14}/></button>
            <button onClick={reload}    style={btnStyle()} title="Reload"  disabled={!active}><RotateCw size={14}/></button>
            <input type="text" value={urlInput} onChange={(e) => setUrlInput(e.target.value)}
                   onKeyDown={(e) => e.key === "Enter" && navTo(urlInput)}
                   placeholder="https://…"
                   style={{ flex: 1, padding: "8px 10px", borderRadius: 6,
                            background: "rgba(0,0,0,0.45)", border: `1px solid ${T.border}`,
                            color: T.text, fontSize: 13, fontFamily: "ui-monospace, monospace" }}
                   disabled={!active} />
            <button onClick={() => navTo(urlInput)}
                    style={{ ...btnStyle(), background: `${T.blue}30`, borderColor: T.blue }}
                    disabled={!active}>
              Go
            </button>
            {active && (active.driver === "user"
              ? <button onClick={releaseControl} style={{ ...btnStyle(), background: `${T.green}25`, borderColor: T.green }} title="Release control"><Unlock size={14}/></button>
              : <button onClick={takeControl}    style={{ ...btnStyle(), background: `${T.amber}25`, borderColor: T.amber }} title="Take control"><Lock   size={14}/></button>
            )}
            {active && (
              <button onClick={() => closeSession(active.session_id)}
                      style={{ ...btnStyle(), background: `${T.red}20`, borderColor: T.red }}
                      title="Close session">
                <Power size={14}/>
              </button>
            )}
          </div>

          {/* Driver status strip */}
          {active && (
            <div style={{ padding: "6px 12px", background: "rgba(0,0,0,0.2)",
                          borderBottom: `1px solid ${T.border}`, fontSize: 11,
                          color: T.mute, display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{active.url}</span>
              <span style={{ flex: 1 }} />
              {(() => {
                const d = DRIVER_BADGE[active.driver || "shared"] || DRIVER_BADGE.shared;
                const DIcon = d.icon;
                return <><DIcon size={11} color={d.color} /><span style={{ color: d.color }}>{d.label}</span></>;
              })()}
            </div>
          )}

          {/* Canvas */}
          <div style={{
            background: "#0b1220",
            minHeight: fullscreen ? "calc(100vh - 280px)" : 640,
            display: "flex", alignItems: "center", justifyContent: "center", padding: 12,
          }}
               tabIndex={0} onKeyDown={handleKey} onWheel={handleWheel}>
            {!active && (
              <div style={{ textAlign: "center", color: T.mute }}>
                <Globe size={42} style={{ marginBottom: 12, opacity: 0.4 }} />
                <div style={{ fontSize: 14 }}>Open a session to start browsing.</div>
                <div style={{ fontSize: 11, marginTop: 6 }}>Agents, tools, and you all share this session.</div>
              </div>
            )}
            {active && !frame && (
              <div style={{ color: T.mute, fontSize: 12, display: "flex", alignItems: "center", gap: 8 }}>
                <Loader2 size={16} className="animate-spin" /> Waiting for first frame…
              </div>
            )}
            <canvas ref={canvasRef} onClick={handleCanvasClick}
                    style={{ maxWidth: "100%", maxHeight: fullscreen ? "calc(100vh - 260px)" : "70vh",
                             borderRadius: 6, boxShadow: "0 8px 40px rgba(0,0,0,0.5)",
                             display: frame ? "block" : "none", cursor: "crosshair" }} />
          </div>
        </main>
      </div>
    </div>
  );
}

function btnStyle() {
  return {
    padding: "6px 10px", borderRadius: 6,
    background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`,
    color: T.text, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12,
  };
}

const selectStyle = {
  padding: "4px 8px", borderRadius: 6,
  background: "rgba(0,0,0,0.35)", border: `1px solid ${T.border}`,
  color: T.text, fontSize: 12,
};

const tabPill = {
  padding: "6px 8px", borderRadius: 8,
  border: `1px solid ${T.border}`, color: T.text,
  cursor: "pointer", fontSize: 11,
  display: "flex", alignItems: "center", justifyContent: "center",
};
