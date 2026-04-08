import { useState, useEffect } from "react";
import { Settings, Thermometer, Hash, RotateCcw, X, Sparkles } from "lucide-react";
import { API, useAuth } from "../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#a78bfa",
  zinc: "#71717a",
};

const STYLES = `@keyframes cp_spin { to { transform: rotate(360deg); } }`;

const formInput = {
  background: "rgba(255,255,255,.05)",
  border: `1px solid ${T.border}`,
  borderRadius: 8,
  padding: "8px 12px",
  color: "#fff",
  fontSize: 12,
  outline: "none",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
  resize: "vertical",
  transition: "border-color .2s",
};

const AgentCustomizePanel = ({ agent, onClose }) => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const [settings, setSettings] = useState({
    temperature: agent?.temperature ?? 0.7,
    max_tokens: agent?.max_tokens ?? 4096,
    personality_tone: "",
    custom_instructions: "",
  });
  const [hasOverride, setHasOverride] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (agent?.agent_id) fetchSettings();
  }, [agent?.agent_id]);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/agents/${agent.agent_id}/my-settings`, { headers: authHeaders });
      if (res.ok) {
        const data = await res.json();
        if (data.has_override) {
          setSettings({
            temperature: data.temperature ?? agent?.temperature ?? 0.7,
            max_tokens: data.max_tokens ?? agent?.max_tokens ?? 4096,
            personality_tone: data.personality_tone || "",
            custom_instructions: data.custom_instructions || "",
          });
          setHasOverride(true);
        }
      }
    } catch {}
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/agents/${agent.agent_id}/my-settings`, {
        method: "PUT", headers,
        body: JSON.stringify(settings),
      });
      if (res.ok) {
        setHasOverride(true);
        toast.success("Agent customized for your sessions!");
      } else {
        toast.error("Failed to save");
      }
    } catch { toast.error("Failed to save"); }
    setSaving(false);
  };

  const handleReset = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/agents/${agent.agent_id}/my-settings`, {
        method: "DELETE", headers: authHeaders,
      });
      if (res.ok) {
        setSettings({
          temperature: agent?.temperature ?? 0.7,
          max_tokens: agent?.max_tokens ?? 4096,
          personality_tone: "",
          custom_instructions: "",
        });
        setHasOverride(false);
        toast.success("Reset to defaults");
      }
    } catch { toast.error("Failed to reset"); }
    setSaving(false);
  };

  if (!agent) return null;

  return (
    <>
      <style>{STYLES}</style>
      <div style={{ position: "fixed", inset: 0, zIndex: 59 }} onClick={onClose} />
      <div
        data-testid="agent-customize-panel"
        style={{
          position: "fixed", right: 16, top: 64, width: 300, zIndex: 60,
          background: "#111113", border: `1px solid ${T.border}`,
          borderRadius: 14, boxShadow: "0 24px 64px rgba(0,0,0,.6)",
          padding: 16, display: "flex", flexDirection: "column", gap: 14,
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Settings size={14} style={{ color: T.indigo }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Customize {agent.name}</span>
          </div>
          <button
            onClick={onClose}
            data-testid="customize-close-btn"
            style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4, borderRadius: 6, display: "flex", alignItems: "center" }}
            onMouseEnter={e => e.currentTarget.style.color = "#fff"}
            onMouseLeave={e => e.currentTarget.style.color = T.zinc}
          >
            <X size={14} />
          </button>
        </div>

        {loading ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "24px 0" }}>
            <div style={{ width: 18, height: 18, border: `2px solid rgba(129,140,248,.3)`, borderTopColor: T.indigo, borderRadius: "50%", animation: "cp_spin .8s linear infinite" }} />
          </div>
        ) : (
          <>
            <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>These settings apply only to your chats with this agent.</p>

            {/* Personality Tone */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 11, color: "#a1a1aa", display: "flex", alignItems: "center", gap: 5 }}>
                <Sparkles size={11} /> Personality Adjustment
              </label>
              <textarea
                value={settings.personality_tone}
                onChange={e => setSettings(p => ({ ...p, personality_tone: e.target.value }))}
                placeholder="e.g. Be more casual and use humor"
                rows={2}
                style={{ ...formInput }}
                data-testid="customize-personality"
                onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
                onBlur={e => e.target.style.borderColor = T.border}
              />
            </div>

            {/* Custom Instructions */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 11, color: "#a1a1aa" }}>Custom Instructions</label>
              <textarea
                value={settings.custom_instructions}
                onChange={e => setSettings(p => ({ ...p, custom_instructions: e.target.value }))}
                placeholder="e.g. Always respond in bullet points"
                rows={2}
                style={{ ...formInput }}
                data-testid="customize-instructions"
                onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
                onBlur={e => e.target.style.borderColor = T.border}
              />
            </div>

            {/* Temperature */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 11, color: "#a1a1aa", display: "flex", alignItems: "center", gap: 5 }}>
                <Thermometer size={11} /> Temperature: {settings.temperature.toFixed(1)}
              </label>
              <input
                type="range" min="0" max="2" step="0.1"
                value={settings.temperature}
                onChange={e => setSettings(p => ({ ...p, temperature: parseFloat(e.target.value) }))}
                style={{ width: "100%", accentColor: T.indigo }}
                data-testid="customize-temperature"
              />
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#52525b" }}>
                <span>Precise</span><span>Creative</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label style={{ fontSize: 11, color: "#a1a1aa", display: "flex", alignItems: "center", gap: 5 }}>
                <Hash size={11} /> Max Tokens: {settings.max_tokens}
              </label>
              <input
                type="range" min="256" max="16384" step="256"
                value={settings.max_tokens}
                onChange={e => setSettings(p => ({ ...p, max_tokens: parseInt(e.target.value) }))}
                style={{ width: "100%", accentColor: T.indigo }}
                data-testid="customize-max-tokens"
              />
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#52525b" }}>
                <span>Short</span><span>Long</span>
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: "flex", gap: 8, paddingTop: 4 }}>
              <button
                onClick={handleSave}
                disabled={saving}
                data-testid="customize-save-btn"
                style={{
                  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                  padding: "7px 14px", borderRadius: 9, border: "none",
                  background: saving ? "rgba(129,140,248,.25)" : "linear-gradient(135deg,#6366f1,#7c3aed)",
                  color: saving ? T.indigo : "#fff", fontSize: 12, fontWeight: 600,
                  cursor: saving ? "not-allowed" : "pointer",
                }}
              >
                {saving && <div style={{ width: 11, height: 11, border: "1.5px solid rgba(255,255,255,.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "cp_spin .8s linear infinite" }} />}
                Save
              </button>
              {hasOverride && (
                <button
                  onClick={handleReset}
                  disabled={saving}
                  data-testid="customize-reset-btn"
                  style={{
                    display: "flex", alignItems: "center", gap: 5,
                    padding: "7px 12px", borderRadius: 9, border: `1px solid ${T.border}`,
                    background: "transparent", color: T.zinc, fontSize: 12, fontWeight: 500,
                    cursor: saving ? "not-allowed" : "pointer",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.color = "#fff"; e.currentTarget.style.borderColor = "rgba(255,255,255,.2)"; }}
                  onMouseLeave={e => { e.currentTarget.style.color = T.zinc; e.currentTarget.style.borderColor = T.border; }}
                >
                  <RotateCcw size={11} /> Reset
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default AgentCustomizePanel;
