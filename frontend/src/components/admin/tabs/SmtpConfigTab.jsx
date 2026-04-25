import { useState, useEffect } from "react";
import { Mail, CheckCircle, XCircle, Send, Eye, EyeOff, ExternalLink } from "lucide-react";
import { useAuth, API } from "../../../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
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

const SmtpConfigTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};
  const [config, setConfig] = useState({ email: "", has_password: false, configured: false });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [testEmail, setTestEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchConfig(); }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/smtp-config`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
        setEmail(data.email || "");
      }
    } catch {}
    setLoading(false);
  };

  const handleSave = async () => {
    if (!email) { toast.error("Email is required"); return; }
    setSaving(true);
    try {
      const res = await fetch(`${API}/admin/smtp-config`, {
        method: "POST", headers,
        body: JSON.stringify({ email, password: password || undefined })
      });
      if (res.ok) {
        toast.success("SMTP configuration saved");
        setPassword("");
        fetchConfig();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to save");
      }
    } catch { toast.error("Failed to save SMTP config"); }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      const res = await fetch(`${API}/admin/smtp-test`, {
        method: "POST", headers,
        body: JSON.stringify({ to_email: testEmail || undefined })
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(data.message || "Test email sent!");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Test failed");
      }
    } catch { toast.error("Failed to send test email"); }
    setTesting(false);
  };

  const inputFocus = e => e.target.style.borderColor = "rgba(124,58,237,.5)";
  const inputBlur = e => e.target.style.borderColor = T.border;

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 128 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="smtp-config-tab">
      <style>{STYLES}</style>

      {/* Status Banner */}
      <div style={{
        display: "flex", alignItems: "flex-start", gap: 12, padding: "14px 16px", borderRadius: 12,
        background: config.configured ? "rgba(52,211,153,.08)" : "rgba(245,158,11,.08)",
        border: `1px solid ${config.configured ? "rgba(52,211,153,.2)" : "rgba(245,158,11,.2)"}`,
      }}>
        {config.configured
          ? <CheckCircle size={18} style={{ color: T.green, flexShrink: 0, marginTop: 1 }} />
          : <XCircle size={18} style={{ color: T.amber, flexShrink: 0, marginTop: 1 }} />}
        <div>
          <p style={{ fontSize: 13, fontWeight: 600, color: config.configured ? T.green : T.amber, margin: 0 }}>
            {config.configured ? "SMTP is configured and ready" : "SMTP not configured — email notifications are disabled"}
          </p>
          <p style={{ fontSize: 11, color: T.zinc, margin: "3px 0 0" }}>
            {config.configured ? `Using: ${config.email}` : "Configure Gmail SMTP to enable team invites and notifications"}
          </p>
        </div>
      </div>

      {/* Gmail SMTP Configuration */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: T.red, borderRadius: "14px 14px 0 0", position: "relative" }} />
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(239,68,68,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Mail size={18} style={{ color: T.red }} />
          </div>
          <div>
            <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Gmail SMTP Configuration</p>
            <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>Used for sending team invitations, notifications, and alerts</p>
          </div>
        </div>
        <div style={{ padding: "18px", display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>Gmail Address</label>
            <input
              type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="your-email@gmail.com"
              style={formInput} data-testid="smtp-email-input"
              onFocus={inputFocus} onBlur={inputBlur}
            />
          </div>

          <div>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>
              App Password
              {config.has_password && (
                <span style={{ fontSize: 10, padding: "1px 8px", borderRadius: 20, background: "rgba(52,211,153,.15)", color: T.green, fontWeight: 700 }}>Saved</span>
              )}
            </label>
            <div style={{ position: "relative" }}>
              <input
                type={showPassword ? "text" : "password"}
                value={password} onChange={e => setPassword(e.target.value)}
                placeholder={config.has_password ? "·········· (leave blank to keep current)" : "Enter your Gmail App Password"}
                style={{ ...formInput, paddingRight: 36 }} data-testid="smtp-password-input"
                onFocus={inputFocus} onBlur={inputBlur}
              />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: T.zinc, display: "flex", alignItems: "center" }}>
                {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          <button onClick={handleSave} disabled={saving || !email} data-testid="smtp-save-btn"
            style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "9px 18px", borderRadius: 10, border: "none", background: saving || !email ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.indigo}, ${T.violet})`, color: "#fff", fontSize: 13, fontWeight: 700, cursor: saving || !email ? "not-allowed" : "pointer", width: "fit-content" }}>
            {saving
              ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
              : <Mail size={14} />}
            Save SMTP Configuration
          </button>
        </div>
      </div>

      {/* Test Email */}
      {config.configured && (
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
          <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(129,140,248,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Send size={18} style={{ color: T.indigo }} />
            </div>
            <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Test Email</p>
          </div>
          <div style={{ padding: 18 }}>
            <label style={{ display: "block", fontSize: 11, color: T.zinc, marginBottom: 6 }}>
              Send test email to (optional — defaults to your admin email)
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <input type="email" value={testEmail} onChange={e => setTestEmail(e.target.value)}
                placeholder="test@example.com"
                style={formInput} data-testid="smtp-test-email-input"
                onFocus={inputFocus} onBlur={inputBlur}
              />
              <button onClick={handleTest} disabled={testing} data-testid="smtp-test-btn"
                style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "8px 16px", borderRadius: 9, border: `1px solid ${T.border}`, background: "transparent", color: "#fff", fontSize: 13, fontWeight: 600, cursor: testing ? "not-allowed" : "pointer", flexShrink: 0, whiteSpace: "nowrap" }}>
                {testing
                  ? <div style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
                  : <Send size={13} />}
                Send Test
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Setup Guide */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}` }}>
          <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>How to Get a Gmail App Password</p>
        </div>
        <div style={{ padding: "14px 18px", display: "flex", flexDirection: "column", gap: 8 }}>
          {[
            { step: "1", text: "Go to your Google Account security settings", link: "https://myaccount.google.com/security" },
            { step: "2", text: "Ensure 2-Step Verification is enabled" },
            { step: "3", text: 'Search for "App Passwords" in Google Account settings' },
            { step: "4", text: 'Select "Other (Custom name)" and enter "MAARS Command"' },
            { step: "5", text: "Google will generate a 16-character password — paste it above" },
          ].map(item => (
            <div key={item.step} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 14px", borderRadius: 9, background: "rgba(255,255,255,.025)" }}>
              <div style={{ width: 22, height: 22, borderRadius: "50%", background: "rgba(239,68,68,.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: T.red }}>{item.step}</span>
              </div>
              <div>
                <p style={{ fontSize: 12, color: "#d4d4d8", margin: 0 }}>{item.text}</p>
                {item.link && (
                  <a href={item.link} target="_blank" rel="noopener noreferrer"
                    style={{ display: "inline-flex", alignItems: "center", gap: 4, color: T.red, fontSize: 11, marginTop: 4, textDecoration: "none" }}
                    onMouseEnter={e => e.currentTarget.style.textDecoration = "underline"}
                    onMouseLeave={e => e.currentTarget.style.textDecoration = "none"}>
                    <ExternalLink size={11} /> {item.link}
                  </a>
                )}
              </div>
            </div>
          ))}

          <div style={{ padding: "12px 14px", borderRadius: 10, background: "rgba(245,158,11,.08)", border: `1px solid rgba(245,158,11,.2)`, marginTop: 4 }}>
            <p style={{ fontSize: 12, color: T.amber, margin: 0 }}>
              <strong>Important:</strong> Use an App Password, NOT your regular Gmail password. Regular passwords won't work with SMTP if 2FA is enabled.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmtpConfigTab;
