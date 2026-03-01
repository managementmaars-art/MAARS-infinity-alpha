import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import {
  Palette, Globe, Image, Type, Loader2, CheckCircle, Clock,
  XCircle, ExternalLink, Sparkles, Save
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const BrandingTab = () => {
  const { token } = useAuth();
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => { fetchBranding(); }, []);

  const fetchBranding = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/branding`, { credentials: "include", headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setConfig(await res.json());
    } catch {}
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const { config_type, custom_domain_status, custom_domain_updated_at, updated_at, ...payload } = config;
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

  const updateField = (field, value) => setConfig(prev => ({ ...prev, [field]: value }));

  if (loading || !config) return <div className="flex items-center justify-center h-32"><Loader2 className="w-6 h-6 animate-spin text-red-400" /></div>;

  const domainStatus = config.custom_domain_status || "not_configured";
  const StatusIcon = domainStatus === "active" ? CheckCircle : domainStatus === "pending_verification" ? Clock : XCircle;
  const statusColor = domainStatus === "active" ? "emerald" : domainStatus === "pending_verification" ? "amber" : "zinc";

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
              <Input
                value={config.platform_name || ""}
                onChange={e => updateField("platform_name", e.target.value)}
                placeholder="MAARS Command"
                className="bg-zinc-800/50 border-white/10"
                data-testid="brand-name-input"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Tagline</Label>
              <Input
                value={config.tagline || ""}
                onChange={e => updateField("tagline", e.target.value)}
                placeholder="AI-Powered Team Platform"
                className="bg-zinc-800/50 border-white/10"
                data-testid="brand-tagline-input"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm flex items-center gap-1.5"><Image className="w-3 h-3" /> Logo URL</Label>
              <Input
                value={config.logo_url || ""}
                onChange={e => updateField("logo_url", e.target.value)}
                placeholder="https://your-domain.com/logo.png"
                className="bg-zinc-800/50 border-white/10"
                data-testid="brand-logo-input"
              />
              {config.logo_url && (
                <div className="p-3 rounded-lg bg-white/5 flex items-center gap-3">
                  <img src={config.logo_url} alt="Logo preview" className="h-10 object-contain" onError={e => e.target.style.display = "none"} />
                  <span className="text-xs text-zinc-500">Preview</span>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Favicon URL</Label>
              <Input
                value={config.favicon_url || ""}
                onChange={e => updateField("favicon_url", e.target.value)}
                placeholder="https://your-domain.com/favicon.ico"
                className="bg-zinc-800/50 border-white/10"
                data-testid="brand-favicon-input"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm">Footer Text</Label>
            <Input
              value={config.footer_text || ""}
              onChange={e => updateField("footer_text", e.target.value)}
              placeholder="MAARS Global Corporation"
              className="bg-zinc-800/50 border-white/10"
              data-testid="brand-footer-input"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm">Support Email</Label>
            <Input
              type="email"
              value={config.support_email || ""}
              onChange={e => updateField("support_email", e.target.value)}
              placeholder="support@yourdomain.com"
              className="bg-zinc-800/50 border-white/10"
              data-testid="brand-support-email"
            />
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
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Primary Color</Label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={config.primary_color || "#ef4444"}
                  onChange={e => updateField("primary_color", e.target.value)}
                  className="w-12 h-10 rounded-lg border border-white/10 cursor-pointer bg-transparent"
                  data-testid="brand-primary-color"
                />
                <Input
                  value={config.primary_color || "#ef4444"}
                  onChange={e => updateField("primary_color", e.target.value)}
                  className="bg-zinc-800/50 border-white/10 font-mono text-sm flex-1"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Accent Color</Label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={config.accent_color || "#f97316"}
                  onChange={e => updateField("accent_color", e.target.value)}
                  className="w-12 h-10 rounded-lg border border-white/10 cursor-pointer bg-transparent"
                  data-testid="brand-accent-color"
                />
                <Input
                  value={config.accent_color || "#f97316"}
                  onChange={e => updateField("accent_color", e.target.value)}
                  className="bg-zinc-800/50 border-white/10 font-mono text-sm flex-1"
                />
              </div>
            </div>
          </div>
          {/* Preview */}
          <div className="mt-4 p-4 rounded-xl bg-white/5">
            <p className="text-xs text-zinc-500 mb-2">Color Preview</p>
            <div className="flex items-center gap-3">
              <div className="h-10 flex-1 rounded-lg" style={{ background: `linear-gradient(to right, ${config.primary_color}, ${config.accent_color})` }} />
              <button className="px-4 py-2 rounded-lg text-white text-sm font-medium" style={{ background: config.primary_color }}>Primary</button>
              <button className="px-4 py-2 rounded-lg text-white text-sm font-medium" style={{ background: config.accent_color }}>Accent</button>
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
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className={`p-3 rounded-lg border flex items-center gap-3 bg-${statusColor}-500/10 border-${statusColor}-500/20`}>
            <StatusIcon className={`w-5 h-5 text-${statusColor}-400 shrink-0`} />
            <div>
              <p className={`text-sm font-medium text-${statusColor}-300`}>
                {domainStatus === "active" ? "Domain is active and verified" :
                 domainStatus === "pending_verification" ? "Domain pending DNS verification" :
                 "No custom domain configured"}
              </p>
              {config.custom_domain && <p className="text-xs text-zinc-500 mt-0.5">{config.custom_domain}</p>}
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm">Your Domain</Label>
            <Input
              value={config.custom_domain || ""}
              onChange={e => updateField("custom_domain", e.target.value)}
              placeholder="app.yourdomain.com"
              className="bg-zinc-800/50 border-white/10"
              data-testid="brand-domain-input"
            />
          </div>

          {config.custom_domain && (
            <div className="p-4 rounded-xl bg-white/5 space-y-3">
              <p className="text-sm text-white font-medium">DNS Configuration</p>
              <p className="text-xs text-zinc-400">Add the following DNS records to your domain provider:</p>
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-zinc-800/50 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">Type:</span>
                    <span className="text-white">CNAME</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-zinc-400">Name:</span>
                    <span className="text-white">{config.custom_domain.split(".")[0]}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-zinc-400">Value:</span>
                    <span className="text-cyan-400">maars-command.emergentagent.com</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800/50 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">Type:</span>
                    <span className="text-white">TXT</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-zinc-400">Name:</span>
                    <span className="text-white">_maars-verify</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-zinc-400">Value:</span>
                    <span className="text-cyan-400">maars-verify={config.custom_domain.replace(/\./g, "-")}</span>
                  </div>
                </div>
              </div>
              <p className="text-[11px] text-zinc-500">DNS changes may take up to 48 hours to propagate.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <Button
        onClick={handleSave}
        disabled={saving}
        className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 w-full"
        data-testid="save-branding-btn"
      >
        {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
        Save Branding & Domain Settings
      </Button>
    </div>
  );
};

export default BrandingTab;
