import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Settings, Thermometer, Hash, RotateCcw, Loader2, X, Sparkles } from "lucide-react";
import { API, useAuth } from "../App";
import { toast } from "sonner";

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
      <div className="fixed inset-0 z-[59]" onClick={onClose} />
      <div className="fixed right-4 top-16 w-80 z-[60] bg-zinc-900 border border-white/10 rounded-xl shadow-2xl p-4 space-y-4" data-testid="agent-customize-panel">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-indigo-400" />
          <span className="text-sm font-medium text-white">Customize {agent.name}</span>
        </div>
        <button onClick={onClose} className="text-zinc-500 hover:text-white p-1" data-testid="customize-close-btn">
          <X className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
        </div>
      ) : (
        <>
          <p className="text-[11px] text-zinc-500">These settings apply only to your chats with this agent.</p>

          {/* Personality Tone */}
          <div className="space-y-1.5">
            <Label className="text-zinc-400 text-xs flex items-center gap-1.5">
              <Sparkles className="w-3 h-3" /> Personality Adjustment
            </Label>
            <Textarea
              value={settings.personality_tone}
              onChange={e => setSettings(p => ({ ...p, personality_tone: e.target.value }))}
              placeholder="e.g. Be more casual and use humor"
              className="bg-zinc-800/50 border-white/10 text-sm min-h-[50px] resize-none"
              data-testid="customize-personality"
            />
          </div>

          {/* Custom Instructions */}
          <div className="space-y-1.5">
            <Label className="text-zinc-400 text-xs">Custom Instructions</Label>
            <Textarea
              value={settings.custom_instructions}
              onChange={e => setSettings(p => ({ ...p, custom_instructions: e.target.value }))}
              placeholder="e.g. Always respond in bullet points"
              className="bg-zinc-800/50 border-white/10 text-sm min-h-[50px] resize-none"
              data-testid="customize-instructions"
            />
          </div>

          {/* Temperature */}
          <div className="space-y-1.5">
            <Label className="text-zinc-400 text-xs flex items-center gap-1.5">
              <Thermometer className="w-3 h-3" /> Temperature: {settings.temperature.toFixed(1)}
            </Label>
            <input
              type="range" min="0" max="2" step="0.1"
              value={settings.temperature}
              onChange={e => setSettings(p => ({ ...p, temperature: parseFloat(e.target.value) }))}
              className="w-full h-1.5 rounded-full appearance-none bg-zinc-700 accent-indigo-500"
              data-testid="customize-temperature"
            />
            <div className="flex justify-between text-[10px] text-zinc-600">
              <span>Precise</span><span>Creative</span>
            </div>
          </div>

          {/* Max Tokens */}
          <div className="space-y-1.5">
            <Label className="text-zinc-400 text-xs flex items-center gap-1.5">
              <Hash className="w-3 h-3" /> Max Tokens: {settings.max_tokens}
            </Label>
            <input
              type="range" min="256" max="16384" step="256"
              value={settings.max_tokens}
              onChange={e => setSettings(p => ({ ...p, max_tokens: parseInt(e.target.value) }))}
              className="w-full h-1.5 rounded-full appearance-none bg-zinc-700 accent-indigo-500"
              data-testid="customize-max-tokens"
            />
            <div className="flex justify-between text-[10px] text-zinc-600">
              <span>Short</span><span>Long</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-1">
            <Button
              onClick={handleSave}
              disabled={saving}
              size="sm"
              className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-xs h-8"
              data-testid="customize-save-btn"
            >
              {saving ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null}
              Save
            </Button>
            {hasOverride && (
              <Button
                onClick={handleReset}
                disabled={saving}
                variant="ghost"
                size="sm"
                className="text-zinc-400 hover:text-white text-xs h-8"
                data-testid="customize-reset-btn"
              >
                <RotateCcw className="w-3 h-3 mr-1" /> Reset
              </Button>
            )}
          </div>
        </>
      )}
    </div>
    </>
  );
};

export default AgentCustomizePanel;
