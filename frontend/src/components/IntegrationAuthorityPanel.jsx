import { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  Shield, Zap, Globe, Monitor, CheckCircle2, AlertCircle,
  PlayCircle, RefreshCw, Unlink, BookOpen, Crown, Lock
} from "lucide-react";
import { API } from "../App";

/**
 * Integration Authority Panel
 *
 * Surfaces:
 *  • The 10 driver-backed integrations MAARS can control (API or browser)
 *  • Per-provider ready mode (API / Browser / Needs connect)
 *  • One-click "Connect Browser" that opens a live sign-in session
 *  • "Test" button that fires a benign provider action (e.g. read_profile)
 *  • Commander Orion authority grant — operator explicitly opts in per provider
 *
 * This panel lives ABOVE the legacy credential grid in IntegrationHub so
 * the operator sees "what Commander can actually control" at a glance.
 */
export default function IntegrationAuthorityPanel({ token }) {
  const navigate = useNavigate();
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [grant, setGrant] = useState({ providers: [], agent_id: "agent_commander" });
  const [busy, setBusy] = useState(false);

  const doFetch = useCallback(async (path, opts = {}) => {
    const tk = token || localStorage.getItem("token") || "";
    const headers = {
      Authorization: `Bearer ${tk}`,
      "Content-Type": "application/json",
      ...(opts.headers || {}),
    };
    const r = await fetch(`${API}${path}`, { ...opts, headers });
    const body = r.status !== 204 ? await r.json().catch(() => ({})) : {};
    if (!r.ok) throw new Error(body?.detail || `${r.status} ${r.statusText}`);
    return body;
  }, [token]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [statusAll, currentGrant] = await Promise.all([
        doFetch("/integrations/status-all"),
        doFetch("/integrations/authority/agent_commander").catch(() => null),
      ]);
      setDrivers(statusAll.providers || []);
      if (currentGrant && currentGrant.providers) setGrant(currentGrant);
    } catch (e) {
      toast.error("Failed to load integration drivers: " + e.message);
    } finally {
      setLoading(false);
    }
  }, [doFetch]);

  useEffect(() => { load(); }, [load]);

  const togglePlatform = (provider) => {
    setGrant(g => {
      const set = new Set(g.providers || []);
      set.has(provider) ? set.delete(provider) : set.add(provider);
      return { ...g, providers: Array.from(set) };
    });
  };

  const saveGrant = async () => {
    setBusy(true);
    try {
      await doFetch("/integrations/authority", {
        method: "PUT",
        body: JSON.stringify({
          agent_id: "agent_commander",
          providers: grant.providers,
          actions: null,
        }),
      });
      toast.success(`Commander Orion now has authority on ${grant.providers.length} integration(s)`);
    } catch (e) {
      toast.error("Save failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const connectBrowser = async (provider) => {
    setBusy(true);
    try {
      const r = await doFetch(`/integrations/${provider}/connect-browser`, { method: "POST" });
      toast.success(`Opening in-app browser for ${provider} — sign in, Commander takes it from there.`);
      // Stay INSIDE MAARS — route internally to the BrowserPanel with the
      // Playwright session ID. No external tabs, no window.open.
      navigate(`/browser?session=${r.session_id}&provider=${provider}`);
    } catch (e) {
      toast.error("Connect failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const testAction = async (provider, action) => {
    setBusy(true);
    try {
      const r = await doFetch("/integrations/act", {
        method: "POST",
        body: JSON.stringify({
          provider, action,
          params: action === "post" ? { content: "MAARS integration test ping" }
                : action === "send_message" ? { content: "test", to: "+10000000000" }
                : {},
        }),
      });
      toast(r.ok ? `${provider}/${action} → ok (${r.mode})` : `${provider}/${action} → ${r.error || "failed"}`,
            { duration: 6000 });
    } catch (e) {
      toast.error(e.message);
    } finally {
      setBusy(false);
    }
  };

  const disconnect = async (provider) => {
    setBusy(true);
    try {
      await doFetch(`/integrations/${provider}/disconnect`, {
        method: "POST",
        body: JSON.stringify({ wipe_browser_session: false }),
      });
      toast.success(`Disconnected ${provider}`);
      await load();
    } catch (e) {
      toast.error(e.message);
    } finally {
      setBusy(false);
    }
  };

  const grantedSet = useMemo(() => new Set(grant.providers || []), [grant.providers]);
  const readyCount = drivers.filter(d => (d.ready_modes || []).length).length;

  return (
    <div style={{
      marginBottom: 16,
      padding: 20,
      borderRadius: 14,
      background: "linear-gradient(135deg, rgba(168,85,247,0.08), rgba(79,209,197,0.05))",
      border: "1px solid rgba(168,85,247,0.2)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10, display: "flex",
          alignItems: "center", justifyContent: "center",
          background: "linear-gradient(135deg, rgba(168,85,247,0.3), rgba(79,209,197,0.3))",
        }}>
          <Crown style={{ width: 18, height: 18, color: "#c4b5fd" }} />
        </div>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>
            Commander Orion — Integration Authority
          </p>
          <p style={{ fontSize: 11, color: "#94a3b8" }}>
            Which apps can Commander control on your behalf? {readyCount}/{drivers.length} drivers ready.
          </p>
        </div>
        <button onClick={load} disabled={loading || busy}
          style={{
            background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 8, padding: "6px 10px", color: "#94a3b8", cursor: "pointer",
            display: "flex", alignItems: "center", gap: 6, fontSize: 11,
          }}>
          <RefreshCw style={{ width: 12, height: 12 }} /> Refresh
        </button>
      </div>

      {loading && (
        <p style={{ textAlign: "center", color: "#64748b", padding: 24, fontSize: 12 }}>
          Loading drivers…
        </p>
      )}

      {!loading && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 10, marginTop: 12 }}>
            {drivers.map(d => {
              const ready = (d.ready_modes || []).length > 0;
              const granted = grantedSet.has(d.provider);
              return (
                <div key={d.provider} style={{
                  padding: 12, borderRadius: 10,
                  background: granted ? "rgba(79,209,197,0.06)" : "rgba(255,255,255,0.03)",
                  border: `1px solid ${granted ? "rgba(79,209,197,0.3)" : "rgba(255,255,255,0.08)"}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <input type="checkbox" checked={granted}
                      onChange={() => togglePlatform(d.provider)}
                      style={{ accentColor: "#4fd1c5" }} />
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", flex: 1 }}>
                      {d.display_name}
                    </p>
                    <span style={{
                      fontSize: 9, fontWeight: 700, padding: "2px 6px", borderRadius: 4,
                      background: ready ? "rgba(52,211,153,0.15)" : "rgba(100,116,139,0.2)",
                      color: ready ? "#34d399" : "#94a3b8",
                    }}>
                      {ready ? (d.ready_modes || []).join(" + ").toUpperCase() : "NOT READY"}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: 8, fontSize: 10, color: "#64748b", marginBottom: 8 }}>
                    {(d.modes_available || []).includes("api") && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>
                        <Zap style={{ width: 10, height: 10 }} />
                        API {d.has_api_credential ? "✓" : "—"}
                      </span>
                    )}
                    {(d.modes_available || []).includes("browser") && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>
                        <Monitor style={{ width: 10, height: 10 }} />
                        Browser {d.browser_has_session ? "✓" : "—"}
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {(d.modes_available || []).includes("browser") && !d.browser_has_session && (
                      <button disabled={busy} onClick={() => connectBrowser(d.provider)}
                        style={{
                          fontSize: 10, padding: "4px 8px", borderRadius: 6,
                          background: "rgba(168,85,247,0.15)", color: "#c4b5fd",
                          border: "1px solid rgba(168,85,247,0.3)", cursor: "pointer",
                        }}>
                        <Globe style={{ width: 10, height: 10, display: "inline", marginRight: 4 }} />
                        Connect Browser
                      </button>
                    )}
                    {ready && (d.api_actions || d.browser_actions || []).length > 0 && (
                      <button disabled={busy}
                        onClick={() => testAction(d.provider, (d.api_actions || d.browser_actions)[0])}
                        style={{
                          fontSize: 10, padding: "4px 8px", borderRadius: 6,
                          background: "rgba(79,209,197,0.12)", color: "#4fd1c5",
                          border: "1px solid rgba(79,209,197,0.3)", cursor: "pointer",
                        }}>
                        <PlayCircle style={{ width: 10, height: 10, display: "inline", marginRight: 4 }} />
                        Test
                      </button>
                    )}
                    {(d.browser_has_session || d.has_api_credential) && (
                      <button disabled={busy} onClick={() => disconnect(d.provider)}
                        style={{
                          fontSize: 10, padding: "4px 8px", borderRadius: 6,
                          background: "transparent", color: "#94a3b8",
                          border: "1px solid rgba(255,255,255,0.1)", cursor: "pointer",
                        }}>
                        <Unlink style={{ width: 10, height: 10, display: "inline", marginRight: 4 }} />
                        Disconnect
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{
            marginTop: 14, padding: 12, borderRadius: 10,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.08)",
            display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
              <Lock style={{ width: 14, height: 14, color: "#94a3b8" }} />
              <p style={{ fontSize: 12, color: "#cbd5e1" }}>
                Grant Commander Orion authority on <b>{grant.providers.length}</b> selected integration(s).
                Workflows that use <code style={{ background: "#0f172a", padding: "1px 4px", borderRadius: 3 }}>integration_action</code> will check this grant before any API or browser call.
              </p>
            </div>
            <button onClick={saveGrant} disabled={busy}
              style={{
                padding: "7px 14px", borderRadius: 8, fontSize: 12, fontWeight: 700,
                background: "linear-gradient(90deg, rgba(168,85,247,0.4), rgba(79,209,197,0.4))",
                color: "#fff", border: "1px solid rgba(168,85,247,0.5)", cursor: "pointer",
              }}>
              <Shield style={{ width: 12, height: 12, display: "inline", marginRight: 6 }} />
              {busy ? "Saving…" : "Save Authority"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
