import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import {
  Palette, Globe, Image, Type, Loader2, CheckCircle, Clock,
  XCircle, Upload, Copy, RefreshCw, AlertCircle, Save, Sparkles
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const BrandingTab = () => {
  const { token } = useAuth();
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const authHeaders = { Authorization: `Bearer ${token}` };
  const logoRef = useRef(null);
  const faviconRef = useRef(null);

  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [uploadingFavicon, setUploadingFavicon] = useState(false);

  useEffect(() => { fetchBranding(); }, []);

  const fetchBranding = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/branding`, { credentials: "include", headers: authHeaders });
      if (res.ok) setConfig(await res.json());
    } catch {}
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { config_type, custom_domain_status, custom_domain_updated_at, custom_domain_verified_at, updated_at, ...payload } = config;
      const res = await fetch(`${API}/admin/branding`, {
        method: "POST", credentials: "include", headers,
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
        method: "POST", credentials: "include", headers: authHeaders, body: formData,
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
        method: "POST", credentials: "include", headers,
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
    if (url.startsWith("/api")) return `${process.env.REACT_APP_BACKEND_URL}${url}`;
    return url;
  };

  if (loading || !config) return <div className="flex items-center justify-center h-32"><Loader2 className="w-6 h-6 animate-spin text-red-400" /></div>;

  const domainStatus = config.custom_domain_status || "not_configured";

  return (
    <div className="space-y-6" data-testid="branding-tab">
      {/* Brand Identity */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-rose-500/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-rose-400" />
            </div>
            Brand Identity
          </CardTitle>
          <p className="text-zinc-400 text-sm">Customize how your platform appears to users</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm flex items-center gap-1.5"><Type className="w-3 h-3" /> Platform Name</Label>
              <Input value={config.platform_name || ""} onChange={e => updateField("platform_name", e.target.value)} placeholder="MAARS Command" className="bg-zinc-800/50 border-white/10" data-testid="brand-name-input" />
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Tagline</Label>
              <Input value={config.tagline || ""} onChange={e => updateField("tagline", e.target.value)} placeholder="AI-Powered Team Platform" className="bg-zinc-800/50 border-white/10" data-testid="brand-tagline-input" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Footer Text</Label>
              <Input value={config.footer_text || ""} onChange={e => updateField("footer_text", e.target.value)} placeholder="MAARS Global Corporation" className="bg-zinc-800/50 border-white/10" data-testid="brand-footer-input" />
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Support Email</Label>
              <Input type="email" value={config.support_email || ""} onChange={e => updateField("support_email", e.target.value)} placeholder="support@yourdomain.com" className="bg-zinc-800/50 border-white/10" data-testid="brand-support-email" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logo & Favicon */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <Image className="w-5 h-5 text-violet-400" />
            </div>
            Logo & Favicon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Logo */}
            <div className="space-y-3">
              <Label className="text-zinc-300 text-sm">Platform Logo</Label>
              <div className="border border-dashed border-white/20 rounded-xl p-5 flex flex-col items-center gap-3">
                {config.logo_url ? (
                  <div className="w-28 h-28 rounded-lg bg-zinc-800 flex items-center justify-center overflow-hidden">
                    <img src={resolveUrl(config.logo_url)} alt="Logo" className="max-w-full max-h-full object-contain" data-testid="brand-logo-preview" onError={e => e.target.style.display = "none"} />
                  </div>
                ) : (
                  <div className="w-28 h-28 rounded-lg bg-zinc-800/50 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-zinc-600" />
                  </div>
                )}
                <input ref={logoRef} type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" className="hidden" onChange={e => handleUpload(e.target.files[0], "logo")} />
                <Button variant="outline" size="sm" onClick={() => logoRef.current?.click()} disabled={uploadingLogo} className="border-white/10 text-zinc-300 hover:bg-white/5" data-testid="brand-upload-logo-btn">
                  {uploadingLogo ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Upload className="w-4 h-4 mr-2" />}
                  Upload Logo
                </Button>
                <span className="text-[11px] text-zinc-500">PNG, JPG, SVG, WebP. Max 5MB.</span>
              </div>
              <div>
                <Label className="text-zinc-500 text-xs">Or paste URL</Label>
                <Input value={config.logo_url || ""} onChange={e => updateField("logo_url", e.target.value)} placeholder="https://..." className="bg-zinc-800/50 border-white/10 mt-1 text-sm" data-testid="brand-logo-input" />
              </div>
            </div>

            {/* Favicon */}
            <div className="space-y-3">
              <Label className="text-zinc-300 text-sm">Favicon</Label>
              <div className="border border-dashed border-white/20 rounded-xl p-5 flex flex-col items-center gap-3">
                {config.favicon_url ? (
                  <div className="w-16 h-16 rounded-lg bg-zinc-800 flex items-center justify-center overflow-hidden">
                    <img src={resolveUrl(config.favicon_url)} alt="Favicon" className="max-w-full max-h-full object-contain" data-testid="brand-favicon-preview" onError={e => e.target.style.display = "none"} />
                  </div>
                ) : (
                  <div className="w-16 h-16 rounded-lg bg-zinc-800/50 flex items-center justify-center">
                    <Upload className="w-5 h-5 text-zinc-600" />
                  </div>
                )}
                <input ref={faviconRef} type="file" accept="image/png,image/x-icon,image/svg+xml,image/webp,.ico" className="hidden" onChange={e => handleUpload(e.target.files[0], "favicon")} />
                <Button variant="outline" size="sm" onClick={() => faviconRef.current?.click()} disabled={uploadingFavicon} className="border-white/10 text-zinc-300 hover:bg-white/5" data-testid="brand-upload-favicon-btn">
                  {uploadingFavicon ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Upload className="w-4 h-4 mr-2" />}
                  Upload Favicon
                </Button>
                <span className="text-[11px] text-zinc-500">ICO, PNG, SVG. Max 5MB.</span>
              </div>
              <div>
                <Label className="text-zinc-500 text-xs">Or paste URL</Label>
                <Input value={config.favicon_url || ""} onChange={e => updateField("favicon_url", e.target.value)} placeholder="https://..." className="bg-zinc-800/50 border-white/10 mt-1 text-sm" data-testid="brand-favicon-input" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Colors */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <Palette className="w-5 h-5 text-indigo-400" />
            </div>
            Brand Colors
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Primary Color</Label>
              <div className="flex items-center gap-3">
                <input type="color" value={config.primary_color || "#ef4444"} onChange={e => updateField("primary_color", e.target.value)} className="w-12 h-10 rounded-lg border border-white/10 cursor-pointer bg-transparent" data-testid="brand-primary-color" />
                <Input value={config.primary_color || "#ef4444"} onChange={e => updateField("primary_color", e.target.value)} className="bg-zinc-800/50 border-white/10 font-mono text-sm flex-1" />
              </div>
              <p className="text-[11px] text-zinc-500">Buttons, highlights, active states</p>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Accent Color</Label>
              <div className="flex items-center gap-3">
                <input type="color" value={config.accent_color || "#f97316"} onChange={e => updateField("accent_color", e.target.value)} className="w-12 h-10 rounded-lg border border-white/10 cursor-pointer bg-transparent" data-testid="brand-accent-color" />
                <Input value={config.accent_color || "#f97316"} onChange={e => updateField("accent_color", e.target.value)} className="bg-zinc-800/50 border-white/10 font-mono text-sm flex-1" />
              </div>
              <p className="text-[11px] text-zinc-500">Gradients, secondary highlights</p>
            </div>
          </div>
          <div className="mt-4 p-4 rounded-xl bg-white/5">
            <p className="text-xs text-zinc-500 mb-3">Live Preview</p>
            <div className="flex items-center gap-3 flex-wrap">
              <div className="h-10 w-32 rounded-lg" style={{ background: `linear-gradient(135deg, ${config.primary_color}, ${config.accent_color})` }} />
              <button className="px-4 py-2 rounded-lg text-white text-sm font-medium" style={{ background: config.primary_color }}>Primary</button>
              <button className="px-4 py-2 rounded-lg text-sm font-medium border" style={{ borderColor: config.primary_color, color: config.primary_color }}>Outline</button>
              <Badge style={{ backgroundColor: `${config.primary_color}20`, color: config.primary_color, border: "none" }}>Badge</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Custom Domain */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
              <Globe className="w-5 h-5 text-cyan-400" />
            </div>
            Custom Domain
            <Badge className={`ml-2 border-0 text-xs ${
              domainStatus === "verified" ? "bg-emerald-500/20 text-emerald-400" :
              domainStatus === "pending_verification" ? "bg-amber-500/20 text-amber-400" :
              domainStatus === "dns_not_found" || domainStatus === "verification_error" ? "bg-red-500/20 text-red-400" :
              "bg-zinc-500/20 text-zinc-400"
            }`} data-testid="brand-domain-status">
              {domainStatus === "verified" && <CheckCircle className="w-3 h-3 mr-1" />}
              {domainStatus === "pending_verification" && <Clock className="w-3 h-3 mr-1" />}
              {(domainStatus === "dns_not_found" || domainStatus === "verification_error") && <XCircle className="w-3 h-3 mr-1" />}
              {domainStatus === "not_configured" && <AlertCircle className="w-3 h-3 mr-1" />}
              {domainStatus === "verified" ? "Verified" :
               domainStatus === "pending_verification" ? "Pending" :
               domainStatus === "dns_not_found" ? "DNS Not Found" :
               domainStatus === "verification_error" ? "Error" : "Not Configured"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end gap-3">
            <div className="flex-1 space-y-2">
              <Label className="text-zinc-300 text-sm">Your Domain</Label>
              <Input value={config.custom_domain || ""} onChange={e => updateField("custom_domain", e.target.value)} placeholder="app.yourdomain.com" className="bg-zinc-800/50 border-white/10" data-testid="brand-domain-input" />
            </div>
            {config.custom_domain && (
              <Button variant="outline" size="sm" onClick={handleVerifyDomain} disabled={verifying} className="border-white/10 text-zinc-300 hover:bg-white/5 h-10" data-testid="brand-verify-domain-btn">
                {verifying ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <RefreshCw className="w-4 h-4 mr-1" />}
                Verify DNS
              </Button>
            )}
          </div>

          {config.custom_domain && (
            <div className="p-4 rounded-xl bg-white/5 space-y-3">
              <p className="text-sm text-white font-medium">DNS Configuration</p>
              <p className="text-xs text-zinc-400">Add these DNS records with your domain registrar:</p>
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-zinc-900/80 font-mono text-xs border border-white/5">
                  <div className="grid grid-cols-3 gap-3 text-zinc-500 mb-2 border-b border-white/5 pb-2">
                    <span>Type</span><span>Name</span><span>Value</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-cyan-400">
                    <span>CNAME</span>
                    <span className="text-white">{config.custom_domain.split(".")[0] || "app"}</span>
                    <span className="flex items-center gap-1.5">
                      {window.location.hostname}
                      <button onClick={() => copyText(window.location.hostname)} className="text-zinc-500 hover:text-white"><Copy className="w-3 h-3" /></button>
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <p className="text-[11px] text-zinc-500">DNS changes may take up to 48 hours. SSL certificates are automatically provisioned after verification.</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save */}
      <Button onClick={handleSave} disabled={saving} className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 w-full" data-testid="save-branding-btn">
        {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
        Save Branding & Domain Settings
      </Button>
    </div>
  );
};

export default BrandingTab;
