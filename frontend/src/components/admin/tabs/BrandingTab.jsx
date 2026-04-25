import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import {
  Palette, Globe, Image, Type, CheckCircle, Clock,
  XCircle, Upload, Copy, RefreshCw, AlertCircle, Save, Sparkles
} from "lucide-react";
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
  cyan: "#22d3ee",
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

const DOMAIN_STATUS_META = {
  verified: { color: T.green, bg: "rgba(52,211,153,.15)", icon: CheckCircle, label: "Verified" },
  pending_verification: { color: T.amber, bg: "rgba(245,158,11,.15)", icon: Clock, label: "Pending" },
  dns_not_found: { color: T.red, bg: "rgba(239,68,68,.15)", icon: XCircle, label: "DNS Not Found" },
  verification_error: { color: T.red, bg: "rgba(239,68,68,.15)", icon: XCircle, label: "Error" },
  not_configured: { color: T.zinc, bg: "rgba(113,113,122,.15)", icon: AlertCircle, label: "Not Configured" },
};

const BrandingTab = () => {
  const { token } = useAuth();
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);
  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);
  const logoRef = useRef(null);
  const faviconRef = useRef(null);

  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [uploadingFavicon, setUploadingFavicon] = useState(false);

  const fetchBranding = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/branding`, { headers: authHeaders });
      if (res.ok) setConfig(await res.json());
    } catch {}
    setLoading(false);
  }, [authHeaders]);

  useEffect(() => { fetchBranding(); }, [fetchBranding]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const { config_type, custom_domain_status, custom_domain_updated_at, custom_domain_verified_at, updated_at, ...payload } = config;
      const res = await fetch(`${API}/admin/branding`, {
        method: "POST", headers,
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
        toast.success("Branding saved successfully");
      } else {
        toast.error("Failed to save branding");
      }
    } catch { toast.error("Save failed"); }
    setSaving(false);
  };

  const handleUpload = async (file, type) => {
    if (!file) return;
    const setter = type === "logo" ? setUploadingLogo : setUploadingFavicon;
    setter(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/admin/branding/upload-logo`, {
        method: "POST", headers: authHeaders, body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        const field = type === "logo" ? "logo_url" : "favicon_url";
        setConfig(prev => ({ ...prev, [field]: data.url }));
        toast.success(`${type === "logo" ? "Logo" : "Favicon"} uploaded`);
      } else {
        const err = await res.json();
        toast.error(err.detail || "Upload failed");
      }
    } catch { toast.error("Upload failed"); }
    setter(false);
  };

  const handleVerifyDomain = async () => {
    setVerifying(true);
    try {
      const res = await fetch(`${API}/admin/branding/verify-domain`, {
        method: "POST", headers,
      });
      if (res.ok) {
        const data = await res.json();
        setConfig(prev => ({ ...prev, custom_domain_status: data.status }));
        if (data.status === "verified") toast.success("Domain verified!");
        else if (data.status === "dns_not_found") toast.error("DNS records not found. Check your CNAME configuration.");
        else toast.info("Verification pending. DNS changes may take up to 48h.");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Verification failed");
      }
    } catch { toast.error("Verification failed"); }
    setVerifying(false);
  };

  const copyText = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied!");
  };

  const updateField = (field, value) => setConfig(prev => ({ ...prev, [field]: value }));

  const resolveUrl = (url) => {
    if (!url) return "";
    if (url.startsWith("/api")) return `${process.env.REACT_APP_BACKEND_URL?.trim() || ""}${url}`;
    return url;
  };

  const inputFocus = e => e.target.style.borderColor = "rgba(124,58,237,.5)";
  const inputBlur = e => e.target.style.borderColor = T.border;

  if (loading || !config) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 128 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const domainStatus = config.custom_domain_status || "not_configured";
  const dsMeta = DOMAIN_STATUS_META[domainStatus] || DOMAIN_STATUS_META.not_configured;
  const DsIcon = dsMeta.icon;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="branding-tab">
      <style>{STYLES}</style>

      {/* Brand Identity */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(244,63,94,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Sparkles size={18} style={{ color: "#fb7185" }} />
          </div>
          <div>
            <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Brand Identity</p>
            <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>Customize how your platform appears to users</p>
          </div>
        </div>
        <div style={{ padding: 18, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <div>
            <label style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>
              <Type size={11} /> Platform Name
            </label>
            <input value={config.platform_name || ""} onChange={e => updateField("platform_name", e.target.value)}
              placeholder="MAARS Command" style={formInput} data-testid="brand-name-input"
              onFocus={inputFocus} onBlur={inputBlur} />
          </div>
          <div>
            <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>Tagline</label>
            <input value={config.tagline || ""} onChange={e => updateField("tagline", e.target.value)}
              placeholder="AI-Powered Team Platform" style={formInput} data-testid="brand-tagline-input"
              onFocus={inputFocus} onBlur={inputBlur} />
          </div>
          <div>
            <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>Footer Text</label>
            <input value={config.footer_text || ""} onChange={e => updateField("footer_text", e.target.value)}
              placeholder="MAARS Global Corporation" style={formInput} data-testid="brand-footer-input"
              onFocus={inputFocus} onBlur={inputBlur} />
          </div>
          <div>
            <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>Support Email</label>
            <input type="email" value={config.support_email || ""} onChange={e => updateField("support_email", e.target.value)}
              placeholder="support@yourdomain.com" style={formInput} data-testid="brand-support-email"
              onFocus={inputFocus} onBlur={inputBlur} />
          </div>
        </div>
      </div>

      {/* Logo & Favicon */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(167,139,250,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Image size={18} style={{ color: "#a78bfa" }} />
          </div>
          <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Logo & Favicon</p>
        </div>
        <div style={{ padding: 18, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          {/* Logo */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <label style={{ fontSize: 11, color: "#d4d4d8", fontWeight: 600 }}>Platform Logo</label>
            <div style={{ border: `1px dashed rgba(255,255,255,.2)`, borderRadius: 12, padding: 20, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
              {config.logo_url ? (
                <div style={{ width: 112, height: 112, borderRadius: 10, background: "rgba(255,255,255,.06)", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
                  <img src={resolveUrl(config.logo_url)} alt="Logo" style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} data-testid="brand-logo-preview" onError={e => e.target.style.display = "none"} />
                </div>
              ) : (
                <div style={{ width: 112, height: 112, borderRadius: 10, background: "rgba(255,255,255,.04)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Upload size={32} style={{ color: "rgba(255,255,255,.15)" }} />
                </div>
              )}
              <input ref={logoRef} type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" style={{ display: "none" }} onChange={e => handleUpload(e.target.files[0], "logo")} />
              <button onClick={() => logoRef.current?.click()} disabled={uploadingLogo} data-testid="brand-upload-logo-btn"
                style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "7px 14px", borderRadius: 8, border: `1px solid ${T.border}`, background: "transparent", color: "#d4d4d8", fontSize: 12, fontWeight: 600, cursor: uploadingLogo ? "not-allowed" : "pointer" }}>
                {uploadingLogo ? <div style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Upload size={13} />}
                Upload Logo
              </button>
              <span style={{ fontSize: 10, color: T.zinc }}>PNG, JPG, SVG, WebP. Max 5MB.</span>
            </div>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Or paste URL</label>
              <input value={config.logo_url || ""} onChange={e => updateField("logo_url", e.target.value)}
                placeholder="https://..." style={formInput} data-testid="brand-logo-input"
                onFocus={inputFocus} onBlur={inputBlur} />
            </div>
          </div>

          {/* Favicon */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <label style={{ fontSize: 11, color: "#d4d4d8", fontWeight: 600 }}>Favicon</label>
            <div style={{ border: `1px dashed rgba(255,255,255,.2)`, borderRadius: 12, padding: 20, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
              {config.favicon_url ? (
                <div style={{ width: 64, height: 64, borderRadius: 10, background: "rgba(255,255,255,.06)", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
                  <img src={resolveUrl(config.favicon_url)} alt="Favicon" style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} data-testid="brand-favicon-preview" onError={e => e.target.style.display = "none"} />
                </div>
              ) : (
                <div style={{ width: 64, height: 64, borderRadius: 10, background: "rgba(255,255,255,.04)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Upload size={20} style={{ color: "rgba(255,255,255,.15)" }} />
                </div>
              )}
              <input ref={faviconRef} type="file" accept="image/png,image/x-icon,image/svg+xml,image/webp,.ico" style={{ display: "none" }} onChange={e => handleUpload(e.target.files[0], "favicon")} />
              <button onClick={() => faviconRef.current?.click()} disabled={uploadingFavicon} data-testid="brand-upload-favicon-btn"
                style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "7px 14px", borderRadius: 8, border: `1px solid ${T.border}`, background: "transparent", color: "#d4d4d8", fontSize: 12, fontWeight: 600, cursor: uploadingFavicon ? "not-allowed" : "pointer" }}>
                {uploadingFavicon ? <div style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Upload size={13} />}
                Upload Favicon
              </button>
              <span style={{ fontSize: 10, color: T.zinc }}>ICO, PNG, SVG. Max 5MB.</span>
            </div>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5 }}>Or paste URL</label>
              <input value={config.favicon_url || ""} onChange={e => updateField("favicon_url", e.target.value)}
                placeholder="https://..." style={formInput} data-testid="brand-favicon-input"
                onFocus={inputFocus} onBlur={inputBlur} />
            </div>
          </div>
        </div>
      </div>

      {/* Brand Colors */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(129,140,248,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Palette size={18} style={{ color: T.indigo }} />
          </div>
          <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Brand Colors</p>
        </div>
        <div style={{ padding: 18 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div>
              <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 8, fontWeight: 600 }}>Primary Color</label>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <input type="color" value={config.primary_color || "#ef4444"} onChange={e => updateField("primary_color", e.target.value)}
                  style={{ width: 44, height: 36, borderRadius: 8, border: `1px solid ${T.border}`, cursor: "pointer", background: "transparent" }} data-testid="brand-primary-color" />
                <input value={config.primary_color || "#ef4444"} onChange={e => updateField("primary_color", e.target.value)}
                  style={{ ...formInput, fontFamily: "monospace" }} onFocus={inputFocus} onBlur={inputBlur} />
              </div>
              <p style={{ fontSize: 10, color: T.zinc, marginTop: 5 }}>Buttons, highlights, active states</p>
            </div>
            <div>
              <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 8, fontWeight: 600 }}>Accent Color</label>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <input type="color" value={config.accent_color || "#f97316"} onChange={e => updateField("accent_color", e.target.value)}
                  style={{ width: 44, height: 36, borderRadius: 8, border: `1px solid ${T.border}`, cursor: "pointer", background: "transparent" }} data-testid="brand-accent-color" />
                <input value={config.accent_color || "#f97316"} onChange={e => updateField("accent_color", e.target.value)}
                  style={{ ...formInput, fontFamily: "monospace" }} onFocus={inputFocus} onBlur={inputBlur} />
              </div>
              <p style={{ fontSize: 10, color: T.zinc, marginTop: 5 }}>Gradients, secondary highlights</p>
            </div>
          </div>

          <div style={{ marginTop: 16, padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)" }}>
            <p style={{ fontSize: 10, color: T.zinc, marginBottom: 12 }}>Live Preview</p>
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              <div style={{ height: 40, width: 120, borderRadius: 10, background: `linear-gradient(135deg, ${config.primary_color || "#ef4444"}, ${config.accent_color || "#f97316"})` }} />
              <button style={{ padding: "8px 16px", borderRadius: 10, border: "none", color: "#fff", fontSize: 13, fontWeight: 600, background: config.primary_color || "#ef4444", cursor: "default" }}>Primary</button>
              <button style={{ padding: "8px 16px", borderRadius: 10, fontSize: 13, fontWeight: 600, background: "transparent", border: `1px solid ${config.primary_color || "#ef4444"}`, color: config.primary_color || "#ef4444", cursor: "default" }}>Outline</button>
              <span style={{ padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 700, background: `${config.primary_color || "#ef4444"}20`, color: config.primary_color || "#ef4444" }}>Badge</span>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Domain */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
        <div style={{ padding: "16px 18px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(34,211,238,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Globe size={18} style={{ color: T.cyan }} />
          </div>
          <p style={{ fontSize: 14, fontWeight: 700, color: "#fff", margin: 0 }}>Custom Domain</p>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 20, background: dsMeta.bg, color: dsMeta.color }} data-testid="brand-domain-status">
            <DsIcon size={10} /> {dsMeta.label}
          </span>
        </div>
        <div style={{ padding: 18, display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 10 }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: 11, color: "#d4d4d8", marginBottom: 6, fontWeight: 600 }}>Your Domain</label>
              <input value={config.custom_domain || ""} onChange={e => updateField("custom_domain", e.target.value)}
                placeholder="app.yourdomain.com" style={formInput} data-testid="brand-domain-input"
                onFocus={inputFocus} onBlur={inputBlur} />
            </div>
            {config.custom_domain && (
              <button onClick={handleVerifyDomain} disabled={verifying} data-testid="brand-verify-domain-btn"
                style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 9, border: `1px solid ${T.border}`, background: "transparent", color: "#d4d4d8", fontSize: 12, fontWeight: 600, cursor: verifying ? "not-allowed" : "pointer", whiteSpace: "nowrap", flexShrink: 0 }}>
                {verifying ? <div style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <RefreshCw size={13} />}
                Verify DNS
              </button>
            )}
          </div>

          {config.custom_domain && (
            <div style={{ padding: "14px 16px", borderRadius: 12, background: "rgba(255,255,255,.03)", display: "flex", flexDirection: "column", gap: 12 }}>
              <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>DNS Configuration</p>
              <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>Add these DNS records with your domain registrar:</p>
              <div style={{ padding: "12px 14px", borderRadius: 9, background: "rgba(0,0,0,.3)", border: `1px solid ${T.border}`, fontFamily: "monospace", fontSize: 12 }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr 3fr", gap: 12, color: T.zinc, marginBottom: 8, paddingBottom: 8, borderBottom: `1px solid ${T.border}` }}>
                  <span>Type</span><span>Name</span><span>Value</span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr 3fr", gap: 12, color: T.cyan }}>
                  <span>CNAME</span>
                  <span style={{ color: "#fff" }}>{config.custom_domain.split(".")[0] || "app"}</span>
                  <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ color: "#fff" }}>{window.location.hostname}</span>
                    <button onClick={() => copyText(window.location.hostname)}
                      style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, display: "flex", padding: 0 }}
                      onMouseEnter={e => e.currentTarget.style.color = "#fff"}
                      onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                      <Copy size={12} />
                    </button>
                  </span>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
                <AlertCircle size={14} style={{ color: T.amber, flexShrink: 0, marginTop: 1 }} />
                <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>DNS changes may take up to 48 hours. SSL certificates are automatically provisioned after verification.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Save */}
      <button onClick={handleSave} disabled={saving} data-testid="save-branding-btn"
        style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "11px 0", borderRadius: 12, border: "none", background: saving ? "rgba(129,140,248,.2)" : `linear-gradient(135deg, ${T.indigo}, ${T.violet})`, color: "#fff", fontSize: 14, fontWeight: 700, cursor: saving ? "not-allowed" : "pointer", width: "100%" }}>
        {saving ? <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Save size={15} />}
        Save Branding & Domain Settings
      </button>
    </div>
  );
};

export default BrandingTab;
