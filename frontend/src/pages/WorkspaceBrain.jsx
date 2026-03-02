import { useState, useEffect } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Brain, Building2, Target, Shield, Globe, PenLine, Clock, Save,
  Loader2, Trash2, CheckCircle, Users, Swords, Tag, FileText
} from "lucide-react";
import { toast } from "sonner";

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

  if (loading) return null;

  const filledCount = FIELDS.filter(f => profile[f.key]?.trim?.()).length;

  return (
    <div className="space-y-6" data-testid="workspace-brain">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
              <Brain className="w-5 h-5 text-violet-400" />
            </div>
            Workspace Brain
          </h2>
          <p className="text-zinc-400 text-sm mt-1">Configure your business profile. Every AI agent uses this context to tailor responses to your brand.</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-white/10 text-zinc-400 text-xs">
            {filledCount}/{FIELDS.length} configured
          </Badge>
          {hasChanges && (
            <Button onClick={handleSave} disabled={saving} className="bg-indigo-600 hover:bg-indigo-500 text-white" size="sm" data-testid="save-brain">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Save className="w-4 h-4 mr-1" />}
              Save
            </Button>
          )}
        </div>
      </div>

      {/* Completion indicator */}
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all duration-500"
          style={{ width: `${(filledCount / FIELDS.length) * 100}%` }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {FIELDS.map(field => {
          const Icon = field.icon;
          return (
            <Card key={field.key} className={`bg-zinc-900/50 border-white/5 ${field.type === "textarea" ? "lg:col-span-2" : ""}`}>
              <CardContent className="p-4">
                <label className="flex items-center gap-2 text-sm text-zinc-300 mb-2">
                  <Icon className="w-4 h-4 text-zinc-500" />
                  {field.label}
                </label>
                {field.type === "textarea" ? (
                  <textarea
                    value={profile[field.key] || ""}
                    onChange={e => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full bg-zinc-800/50 border border-white/10 rounded-lg p-3 text-sm text-white placeholder:text-zinc-600 min-h-[80px] resize-none focus:outline-none focus:border-violet-500/50"
                    data-testid={`brain-${field.key}`}
                  />
                ) : field.type === "select" ? (
                  <select
                    value={profile[field.key] || ""}
                    onChange={e => handleChange(field.key, e.target.value)}
                    className="w-full bg-zinc-800/50 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-violet-500/50"
                    data-testid={`brain-${field.key}`}
                  >
                    {field.options.map(o => <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
                  </select>
                ) : (
                  <Input
                    value={profile[field.key] || ""}
                    onChange={e => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    className="bg-zinc-800/50 border-white/10 text-white"
                    data-testid={`brain-${field.key}`}
                  />
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="flex justify-between pt-4 border-t border-white/5">
        <Button variant="ghost" onClick={handleReset} className="text-zinc-500 hover:text-red-400" size="sm" data-testid="reset-brain">
          <Trash2 className="w-4 h-4 mr-1" />Clear All Data
        </Button>
        {hasChanges && (
          <Button onClick={handleSave} disabled={saving} className="bg-indigo-600 hover:bg-indigo-500 text-white" data-testid="save-brain-bottom">
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Save className="w-4 h-4 mr-1" />}
            Save Workspace Brain
          </Button>
        )}
      </div>
    </div>
  );
};

export default WorkspaceBrain;
