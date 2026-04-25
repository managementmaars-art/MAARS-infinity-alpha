import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Key, Plus, Trash2, Copy, Shield, AlertCircle, Eye, EyeOff } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  red:    "#f87171",
  amber:  "#f59e0b",
  green:  "#34d399",
  mute:   "#94a3b8",
  border: "rgba(255,255,255,0.08)",
  border2:"rgba(255,255,255,0.14)",
  glass:  "rgba(6,12,28,0.7)",
};

export default function ApiKeysPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [keys, setKeys] = useState([]);
  const [newKeyName, setNewKeyName] = useState("");
  const [rawKey, setRawKey] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(true);

  const authHeaders = useCallback(() => {
    const tok = localStorage.getItem("token") || "";
    return tok ? { Authorization: `Bearer ${tok}` } : {};
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/v1/api-keys`, { headers: authHeaders() });
      const j = await r.json();
      setKeys(j.data || []);
    } catch (e) {
      toast.error(`Failed to load keys: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => {
    if (!user) navigate("/login");
    else load();
  }, [user, navigate, load]);

  const create = async () => {
    try {
      const r = await fetch(`${API}/v1/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ name: newKeyName || "default" }),
      });
      if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
      const j = await r.json();
      setRawKey(j.key);
      setRevealed(true);
      setNewKeyName("");
      await load();
      toast.success("API key created. Copy it now — it won't be shown again.");
    } catch (e) {
      toast.error(`Create failed: ${e.message}`);
    }
  };

  const revoke = async (id) => {
    if (!window.confirm("Revoke this key? It cannot be undone.")) return;
    try {
      const r = await fetch(`${API}/v1/api-keys/${id}`, { method: "DELETE", headers: authHeaders() });
      if (!r.ok) throw new Error(r.statusText);
      await load();
      toast.success("Key revoked");
    } catch (e) {
      toast.error(`Revoke failed: ${e.message}`);
    }
  };

  const copyRaw = () => {
    navigator.clipboard.writeText(rawKey);
    toast.success("Copied to clipboard");
  };

  return (
    <div style={{ minHeight: "100vh", background: "#04070f", color: "#e6eaf2", padding: 40 }}>
      <div style={{ maxWidth: 960, margin: "0 auto" }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: -0.3 }}>API Keys</h1>
        <p style={{ margin: "6px 0 24px", color: T.mute, fontSize: 14 }}>
          Use these keys with any OpenAI-compatible client —
          <code style={{ padding: "2px 6px", margin: "0 4px", background: "rgba(255,255,255,0.06)", borderRadius: 4 }}>
            base_url = {window.location.origin}/api
          </code>
          and your key as <code>api_key</code>.
        </p>

        {/* ── create ───────────────────────────────────── */}
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: 20, marginBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <Plus size={16} color={T.teal} />
            <div style={{ fontWeight: 600 }}>Create a new key</div>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <input
              placeholder="e.g. production"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              style={{ flex: 1, padding: "10px 12px", background: "rgba(255,255,255,0.03)",
                       border: `1px solid ${T.border2}`, borderRadius: 8, color: "#e6eaf2", fontSize: 13 }}
            />
            <button onClick={create}
              style={{ padding: "10px 20px", borderRadius: 8, border: "none",
                       background: `linear-gradient(90deg, ${T.teal}, ${T.violet})`,
                       color: "#04070f", fontWeight: 600, cursor: "pointer" }}>
              Create key
            </button>
          </div>

          {rawKey && (
            <div style={{ marginTop: 14, padding: 14, background: `${T.amber}12`, border: `1px solid ${T.amber}55`, borderRadius: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, color: T.amber, fontSize: 13 }}>
                <AlertCircle size={14} />
                This key is shown <b>once</b>. Copy it now; MAARS stores only the hash.
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <code style={{ flex: 1, padding: "10px 12px", background: "rgba(0,0,0,0.5)",
                               borderRadius: 6, fontFamily: "'JetBrains Mono', monospace", fontSize: 12,
                               letterSpacing: 0.3, wordBreak: "break-all" }}>
                  {revealed ? rawKey : "•".repeat(Math.min(rawKey.length, 48))}
                </code>
                <button onClick={() => setRevealed(!revealed)}
                  style={{ padding: "0 14px", borderRadius: 6, background: "transparent",
                           border: `1px solid ${T.border2}`, color: "#e6eaf2", cursor: "pointer" }}>
                  {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
                <button onClick={copyRaw}
                  style={{ padding: "0 14px", borderRadius: 6, background: T.teal, color: "#04070f",
                           border: "none", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
                  <Copy size={14} /> Copy
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── list ─────────────────────────────────────── */}
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, overflow: "hidden" }}>
          <div style={{ padding: "14px 20px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
            <Key size={16} color={T.teal} />
            <div style={{ fontWeight: 600 }}>Your keys</div>
            <div style={{ marginLeft: "auto", color: T.mute, fontSize: 12 }}>
              {loading ? "loading…" : `${keys.length} total`}
            </div>
          </div>
          {keys.length === 0 && !loading && (
            <div style={{ padding: 36, textAlign: "center", color: T.mute, fontSize: 13 }}>
              No keys yet. Create one above.
            </div>
          )}
          {keys.map((k) => (
            <div key={k.api_key_id} style={{
              padding: "14px 20px", borderTop: `1px solid ${T.border}`,
              display: "flex", alignItems: "center", gap: 16,
              opacity: k.status === "revoked" ? 0.55 : 1,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, width: 48 }}>
                <Shield size={18} color={k.status === "active" ? T.green : T.red} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{k.name || "default"}</div>
                <div style={{ color: T.mute, fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }}>
                  maars_sk_live_…{k.last4}
                </div>
              </div>
              <div style={{ color: T.mute, fontSize: 12, minWidth: 140 }}>
                <div>plan: <b style={{ color: "#e6eaf2" }}>{k.plan_id}</b></div>
                <div>created {k.created_at?.slice(0, 10)}</div>
              </div>
              <div style={{ color: T.mute, fontSize: 12, minWidth: 120 }}>
                status: <b style={{ color: k.status === "active" ? T.green : T.red }}>{k.status}</b>
              </div>
              {k.status === "active" && (
                <button onClick={() => revoke(k.api_key_id)}
                  style={{ padding: "6px 12px", borderRadius: 6, background: "transparent",
                           border: `1px solid ${T.red}55`, color: T.red, cursor: "pointer",
                           display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
                  <Trash2 size={13} /> Revoke
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
