import { useState, useEffect } from "react";
import { useAuth, API } from "../App";
import {
  Brain, Building2, Target, Shield, Globe, PenLine, Clock, Save,
  Loader2, Trash2, Tag, FileText, Swords, CheckCircle
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#7c3aed",
  indigo: "#818cf8",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const FIELDS = [
  { key: "company_name", label: "Company Name", icon: Building2, placeholder: "Acme Corp", type: "input" },
  { key: "industry", label: "Industry", icon: Globe, placeholder: "SaaS, E-commerce, Healthcare...", type: "input" },
  { key: "brand_voice", label: "Brand Voice & Tone", icon: PenLine, placeholder: "Professional yet approachable, data-driven, innovative...", type: "textarea" },
  { key: "products_services", label: "Products / Services", icon: Tag, placeholder: "Describe your main products or services...", type: "textarea" },
  { key: "target_audience", label: "Target Audience", icon: Target, placeholder: "SMBs, enterprise CTOs, millennial consumers...", type: "textarea" },
  { key: "competitors", label: "Key Competitors", icon: Swords, placeholder: "Competitor A, Competitor B...", type: "input" },
  { key: "unique_value_prop", label: "Unique Value Proposition", icon: Shield, placeholder: "What makes you different...", type: "textarea" },
  { key: "pricing_info", label: "Pricing Info", icon: FileText, placeholder: "Starter $29/mo, Pro $99/mo...", type: "input" },
  { key: "regions", label: "Markets / Regions", icon: Globe, placeholder: "US, EU, MENA, Global...", type: "input" },
  { key: "website", label: "Website", icon: Globe, placeholder: "https://yourcompany.com", type: "input" },
  { key: "policies", label: "Key Policies", icon: Shield, placeholder: "Return policy, SLA, privacy...", type: "textarea" },
  { key: "writing_style", label: "Writing Style", icon: PenLine, placeholder: "concise", type: "select", options: ["professional", "casual", "concise", "creative", "academic", "technical"] },
  { key: "timezone", label: "Timezone", icon: Clock, placeholder: "UTC", type: "input" },
  { key: "working_hours", label: "Working Hours", icon: Clock, placeholder: "9:00-17:00", type: "input" },
  { key: "custom_instructions", label: "Custom Instructions", icon: Brain, placeholder: "Any special instructions for all agents...", type: "textarea" },
];

const WorkspaceBrain = () => {
  const { token } = useAuth();
  const [profile, setProfile] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetch(`${API}/workspace/profile`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setProfile(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  const handleChange = (key, value) => {
    setProfile(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/workspace/profile`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (res.ok) {
        toast.success("Workspace Brain saved — all agents will use this context");
        setHasChanges(false);
      }
    } catch { toast.error("Failed to save"); }
    finally { setSaving(false); }
  };

  const handleReset = async () => {
    if (!window.confirm("Clear all workspace brain data? Agents will lose business context.")) return;
    await fetch(`${API}/workspace/profile`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    setProfile({});
    setHasChanges(false);
    toast.success("Workspace Brain cleared");
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.violet}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const filledCount = FIELDS.filter(f => profile[f.key]?.trim?.()).length;
  const pct = (filledCount / FIELDS.length) * 100;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="workspace-brain">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(124,58,237,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Brain size={22} style={{ color: T.violet }} />
          </div>
          <div>
            <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }}>Workspace Brain</h1>
            <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Configure your business profile — every agent uses this context to tailor responses to your brand</p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: 20, background: T.glass, border: `1px solid ${T.border}` }}>
            <CheckCircle size={11} style={{ color: pct === 100 ? T.green : T.zinc }} />
            <span style={{ fontSize: 11, color: pct === 100 ? T.green : T.zinc, fontWeight: 600 }}>{filledCount}/{FIELDS.length} configured</span>
          </div>
          {hasChanges && (
            <button
              onClick={handleSave}
              disabled={saving}
              data-testid="save-brain"
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 16px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 600, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? .7 : 1 }}
            >
              {saving
                ? <><div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> Saving…</>
                : <><Save size={13} /> Save</>}
            </button>
          )}
        </div>
      </div>

      {/* Completion bar */}
      <div>
        <div style={{ height: 6, background: "rgba(255,255,255,.06)", borderRadius: 6, overflow: "hidden", marginBottom: 6 }}>
          <div style={{ height: "100%", borderRadius: 6, background: `linear-gradient(90deg, ${T.violet}, ${T.indigo})`, width: `${pct}%`, transition: "width .5s" }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: T.zinc }}>
          <span>{pct.toFixed(0)}% complete</span>
          <span>{FIELDS.length - filledCount} fields remaining</span>
        </div>
      </div>

      {/* Fields grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12 }}>
        {FIELDS.map(field => {
          const Icon = field.icon;
          const isWide = field.type === "textarea";
          return (
            <div
              key={field.key}
              style={{
                gridColumn: isWide ? "1 / -1" : undefined,
                background: T.glass, border: `1px solid ${T.border}`,
                borderRadius: 12, padding: "14px 16px",
              }}
            >
              <label style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 11, color: T.zinc, marginBottom: 8, fontWeight: 600, textTransform: "uppercase", letterSpacing: ".05em" }}>
                <Icon size={12} style={{ color: T.zinc }} />
                {field.label}
              </label>
              {field.type === "textarea" ? (
                <textarea
                  value={profile[field.key] || ""}
                  onChange={e => handleChange(field.key, e.target.value)}
                  placeholder={field.placeholder}
                  data-testid={`brain-${field.key}`}
                  style={{ ...formInput, minHeight: 72, resize: "vertical", lineHeight: 1.5 }}
                  onFocus={e => e.target.style.borderColor = "rgba(124,58,237,.5)"}
                  onBlur={e => e.target.style.borderColor = T.border}
                />
              ) : field.type === "select" ? (
                <select
                  value={profile[field.key] || ""}
                  onChange={e => handleChange(field.key, e.target.value)}
                  data-testid={`brain-${field.key}`}
                  style={{ ...formInput, cursor: "pointer" }}
                  onFocus={e => e.target.style.borderColor = "rgba(124,58,237,.5)"}
                  onBlur={e => e.target.style.borderColor = T.border}
                >
                  {field.options.map(o => (
                    <option key={o} value={o} style={{ background: "#1a1a2e" }}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={profile[field.key] || ""}
                  onChange={e => handleChange(field.key, e.target.value)}
                  placeholder={field.placeholder}
                  data-testid={`brain-${field.key}`}
                  style={formInput}
                  onFocus={e => e.target.style.borderColor = "rgba(124,58,237,.5)"}
                  onBlur={e => e.target.style.borderColor = T.border}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Footer actions */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 16, borderTop: `1px solid ${T.border}` }}>
        <button
          onClick={handleReset}
          data-testid="reset-brain"
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 10, background: "transparent", border: `1px solid transparent`, color: T.zinc, fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}
          onMouseEnter={e => { e.currentTarget.style.color = T.red; e.currentTarget.style.borderColor = "rgba(239,68,68,.3)"; }}
          onMouseLeave={e => { e.currentTarget.style.color = T.zinc; e.currentTarget.style.borderColor = "transparent"; }}
        >
          <Trash2 size={13} /> Clear All Data
        </button>
        {hasChanges && (
          <button
            onClick={handleSave}
            disabled={saving}
            data-testid="save-brain-bottom"
            style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 22px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? .7 : 1 }}
          >
            {saving
              ? <><div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> Saving…</>
              : <><Save size={13} /> Save Workspace Brain</>}
          </button>
        )}
      </div>
    </div>
  );
};

export default WorkspaceBrain;
