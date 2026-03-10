import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Mail, CheckCircle, XCircle, Loader2, Send, Eye, EyeOff, ExternalLink } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

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

  if (loading) return <div className="flex items-center justify-center h-32"><Loader2 className="w-6 h-6 animate-spin text-red-400" /></div>;

  return (
    <div className="space-y-6" data-testid="smtp-config-tab">
      {/* Status Banner */}
      <div className={`p-4 rounded-xl border flex items-center gap-3 ${
        config.configured
          ? "bg-emerald-500/10 border-emerald-500/20"
          : "bg-amber-500/10 border-amber-500/20"
      }`}>
        {config.configured ? (
          <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
        ) : (
          <XCircle className="w-5 h-5 text-amber-400 shrink-0" />
        )}
        <div>
          <p className={`text-sm font-medium ${config.configured ? "text-emerald-300" : "text-amber-300"}`}>
            {config.configured ? "SMTP is configured and ready" : "SMTP not configured - email notifications are disabled"}
          </p>
          <p className="text-xs text-zinc-500 mt-0.5">
            {config.configured ? `Using: ${config.email}` : "Configure Gmail SMTP to enable team invites and notifications"}
          </p>
        </div>
      </div>

      {/* Configuration Card */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <Mail className="w-5 h-5 text-red-400" />
            </div>
            Gmail SMTP Configuration
          </CardTitle>
          <p className="text-zinc-400 text-sm">Used for sending team invitations, notifications, and alerts</p>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm">Gmail Address</Label>
            <Input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="your-email@gmail.com"
              className="bg-zinc-800/50 border-white/10"
              data-testid="smtp-email-input"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm">
              App Password
              {config.has_password && (
                <Badge className="ml-2 bg-emerald-500/20 text-emerald-400 text-[10px]">Saved</Badge>
              )}
            </Label>
            <div className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder={config.has_password ? "********** (leave blank to keep current)" : "Enter your Gmail App Password"}
                className="bg-zinc-800/50 border-white/10 pr-10"
                data-testid="smtp-password-input"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <Button
            onClick={handleSave}
            disabled={saving || !email}
            className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
            data-testid="smtp-save-btn"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Mail className="w-4 h-4 mr-2" />}
            Save SMTP Configuration
          </Button>
        </CardContent>
      </Card>

      {/* Test Email */}
      {config.configured && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                <Send className="w-5 h-5 text-indigo-400" />
              </div>
              Test Email
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Send test email to (optional — defaults to your admin email)</Label>
              <div className="flex gap-3">
                <Input
                  type="email"
                  value={testEmail}
                  onChange={e => setTestEmail(e.target.value)}
                  placeholder="test@example.com"
                  className="bg-zinc-800/50 border-white/10"
                  data-testid="smtp-test-email-input"
                />
                <Button
                  onClick={handleTest}
                  disabled={testing}
                  variant="outline"
                  className="border-white/10 shrink-0"
                  data-testid="smtp-test-btn"
                >
                  {testing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                  Send Test
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Setup Guide */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">How to Get a Gmail App Password</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            { step: "1", text: "Go to your Google Account security settings", link: "https://myaccount.google.com/security" },
            { step: "2", text: "Ensure 2-Step Verification is enabled" },
            { step: "3", text: 'Search for "App Passwords" in Google Account settings' },
            { step: "4", text: 'Select "Other (Custom name)" and enter "MAARS Command"' },
            { step: "5", text: "Google will generate a 16-character password — paste it above" },
          ].map(item => (
            <div key={item.step} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
              <div className="w-6 h-6 rounded-full bg-red-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <span className="text-xs font-bold text-red-400">{item.step}</span>
              </div>
              <div>
                <p className="text-zinc-300 text-sm">{item.text}</p>
                {item.link && (
                  <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-red-400 text-xs hover:underline flex items-center gap-1 mt-1">
                    <ExternalLink className="w-3 h-3" /> {item.link}
                  </a>
                )}
              </div>
            </div>
          ))}

          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 mt-4">
            <p className="text-amber-300 text-sm">
              <strong>Important:</strong> Use an App Password, NOT your regular Gmail password. Regular passwords won't work with SMTP if 2FA is enabled.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SmtpConfigTab;
