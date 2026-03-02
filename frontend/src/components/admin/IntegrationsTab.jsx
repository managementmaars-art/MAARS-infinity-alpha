import { useState, useEffect } from "react";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import { Plug, Loader2 } from "lucide-react";
import { useAuth, API } from "../../App";
import { toast } from "sonner";

const IntegrationsTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const [integrations, setIntegrations] = useState({});
  const [inputs, setInputs] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const serviceIcons = {
    slack: "https://cdn.simpleicons.org/slack/E01E5A",
    github: "https://cdn.simpleicons.org/github/white",
    sendgrid: "https://cdn.simpleicons.org/sendgrid/1A82E2",
    resend: "https://cdn.simpleicons.org/resend/white",
    twilio: "https://cdn.simpleicons.org/twilio/F22F46",
    airtable: "https://cdn.simpleicons.org/airtable/18BFFF",
    calendly: "https://cdn.simpleicons.org/calendly/006BFF",
    giphy: "https://cdn.simpleicons.org/giphy/black",
    google_suite: "https://cdn.simpleicons.org/google/4285F4",
  };

  const keyLabels = {
    bot_token: "Bot Token",
    personal_access_token: "Personal Access Token",
    api_key: "API Key",
    account_sid: "Account SID",
    auth_token: "Auth Token",
    phone_number: "Phone Number",
    service_account_json: "Service Account JSON",
  };

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/admin/integrations`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).then(data => {
      setIntegrations(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {};
      for (const [svcId, fields] of Object.entries(inputs)) {
        const hasValue = Object.values(fields).some(v => v && v.trim());
        if (hasValue) payload[svcId] = fields;
      }
      if (Object.keys(payload).length === 0) {
        toast.info("No changes to save");
        setSaving(false);
        return;
      }
      const resp = await fetch(`${API}/admin/integrations`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        toast.success("Integration keys saved!");
        setInputs({});
        const data = await fetch(`${API}/admin/integrations`, { headers }).then(r => r.json());
        setIntegrations(data);
      } else toast.error("Failed to save");
    } catch { toast.error("Save failed"); }
    setSaving(false);
  };

  const handleTest = async (svcId) => {
    setTesting(prev => ({ ...prev, [svcId]: true }));
    try {
      const resp = await fetch(`${API}/admin/integrations/test/${svcId}`, { headers });
      const data = await resp.json();
      setTestResults(prev => ({ ...prev, [svcId]: data }));
      if (data.status === "active") toast.success(`${integrations[svcId]?.name}: Connected!`);
      else toast.error(`${integrations[svcId]?.name}: ${data.message}`);
    } catch { toast.error("Test failed"); }
    setTesting(prev => ({ ...prev, [svcId]: false }));
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-red-400" /></div>;

  return (
    <div className="space-y-6" data-testid="integrations-tab">
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <Plug className="w-5 h-5 text-violet-400" />
            </div>
            Service Integrations
          </CardTitle>
          <p className="text-zinc-400 text-sm">Configure third-party services your AI agents can use as tools (Slack, GitHub, Email, SMS, etc.)</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(integrations).map(([svcId, svc]) => {
            const docUrls = {
              slack: "https://api.slack.com/apps", github: "https://github.com/settings/tokens",
              sendgrid: "https://app.sendgrid.com/settings/api_keys", resend: "https://resend.com/api-keys",
              twilio: "https://console.twilio.com/", airtable: "https://airtable.com/create/tokens",
              calendly: "https://calendly.com/integrations/api_webhooks", giphy: "https://developers.giphy.com/dashboard/",
              google_suite: "https://console.cloud.google.com/iam-admin/serviceaccounts"
            };
            return (
              <div key={svcId} className="p-4 rounded-lg bg-white/5 space-y-3" data-testid={`integration-card-${svcId}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <img src={serviceIcons[svcId]} alt={svc.name} className="w-5 h-5" onError={(e) => { e.target.style.display = 'none'; }} />
                    <span className="text-white font-medium">{svc.name}</span>
                    <span className="text-xs text-zinc-500 hidden sm:inline">-- {svc.description}</span>
                    {svc.configured && <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Active</Badge>}
                  </div>
                  <a href={docUrls[svcId] || "#"} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline">Get key</a>
                </div>
                {svc.key_fields?.map(field => (
                  <div key={field} className="flex gap-2">
                    <Input
                      type="password"
                      value={inputs[svcId]?.[field] || ""}
                      onChange={e => setInputs(prev => ({ ...prev, [svcId]: { ...prev[svcId], [field]: e.target.value } }))}
                      placeholder={svc.keys_set?.[field] ? `${keyLabels[field] || field}: ******** (saved)` : `Enter ${keyLabels[field] || field}`}
                      className="bg-zinc-800/50 border-white/10 text-sm font-mono"
                      data-testid={`integration-input-${svcId}-${field}`}
                    />
                    {svc.key_fields.indexOf(field) === svc.key_fields.length - 1 && (
                      <Button
                        variant="outline" size="sm" className="border-white/10 shrink-0"
                        onClick={() => handleTest(svcId)}
                        disabled={testing[svcId] || !svc.configured}
                        data-testid={`test-integration-${svcId}`}
                      >
                        {testing[svcId] ? "Testing..." : "Test"}
                      </Button>
                    )}
                  </div>
                ))}
                {testResults[svcId] && (
                  <p className={`text-xs ${testResults[svcId].status === 'active' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {testResults[svcId].status === 'active' ? 'Connected successfully' : testResults[svcId].message?.slice(0, 60)}
                  </p>
                )}
              </div>
            );
          })}

          <div className="flex gap-3 pt-2">
            <Button onClick={handleSave} disabled={saving}
              className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
              data-testid="save-integrations-btn">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plug className="w-4 h-4 mr-2" />}
              Save Integrations
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <h3 className="text-white font-medium mb-2">How Integrations Work</h3>
          <ul className="text-sm text-zinc-400 space-y-1">
            <li>1. Add API keys for the services you want to enable</li>
            <li>2. AI agents automatically gain access to configured integrations as tools</li>
            <li>3. Agents use tools when relevant (e.g., send_email, send_slack, github_action)</li>
            <li>4. Unconfigured integrations are hidden from agents until keys are added</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default IntegrationsTab;
