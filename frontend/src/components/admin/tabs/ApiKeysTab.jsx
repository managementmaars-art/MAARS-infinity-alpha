import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Key, Activity, Plug } from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

export const ApiKeysTab = ({ apiKeysConfig, apiKeyInputs, setApiKeyInputs, apiUsage, testingKey, setTestingKey, token, onRefresh }) => {
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
  const fetchAdminData = onRefresh;

  const handleSaveApiKeys = async () => {
    try {
      const res = await fetch(`${API}/admin/api-keys`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(apiKeyInputs)
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`API keys saved! Using: ${data.active_provider === 'direct' ? 'Direct Provider Keys' : 'Emergent Universal Key'}`);
        fetchAdminData();
        setApiKeyInputs(prev => ({...prev, openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: "", groq_key: "", together_key: "", fireworks_key: "", ai21_key: ""}));
      } else {
        toast.error("Failed to save API keys");
      }
    } catch {
      toast.error("Failed to save API keys");
    }
  };

  const handleTestKey = async (provider, key) => {
    if (!key) { toast.error("Enter a key to test"); return; }
    setTestingKey(provider);
    try {
      const res = await fetch(`${API}/admin/api-keys/test`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: key })
      });
      const data = await res.json();
      if (data.success) {
        toast.success(data.message);
      } else {
        toast.error(data.message);
      }
    } catch {
      toast.error("Test failed");
    } finally {
      setTestingKey(null);
    }
  };

  const costs = apiKeysConfig?.cost_reference || {};
    const usage = apiUsage || {};
    const [integrationStatus, setIntegrationStatus] = useState({});
    
    useEffect(() => {
      if (token) {
        fetch(`${API}/admin/integrations`, { headers: { Authorization: `Bearer ${token}` } })
          .then(r => r.json()).then(data => setIntegrationStatus(data)).catch(() => {});
      }
    }, [token]);
    
  return (
    <div className="space-y-6">
      {/* Provider Status & Usage */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="api-usage-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2 text-base">
            <Activity className="w-5 h-5 text-emerald-400" />
            API Key Status & Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs", "groq", "together", "fireworks", "ai21"].map(provider => {
              const status = usage.providers?.[provider];
              const tracked = usage.tracked_usage?.[provider];
              const providerLabels = { openai: "OpenAI", anthropic: "Anthropic", gemini: "Google Gemini", xai: "xAI (Grok)", deepseek: "DeepSeek", mistral: "Mistral AI", perplexity: "Perplexity", cohere: "Cohere", elevenlabs: "ElevenLabs", groq: "Groq (Llama 4)", together: "Together AI", fireworks: "Fireworks AI", ai21: "AI21 (Jamba)" };
              const hasKey = status?.status === 'active' || status?.status === 'error';
              return (
                <div key={provider} className="p-3 rounded-lg bg-white/5 border border-white/10" data-testid={`api-status-${provider}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{providerLabels[provider] || provider}</span>
                    <Badge className={status?.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : hasKey ? 'bg-red-500/20 text-red-400' : 'bg-zinc-500/20 text-zinc-400'}>
                      {status?.status || 'no key'}
                    </Badge>
                  </div>
                  {status?.models_available > 0 && (
                    <p className="text-xs text-zinc-400">{status.models_available} models available</p>
                  )}
                  {tracked ? (
                    <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">API Calls</span>
                        <span className="text-white">{tracked.total_calls}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">Tokens Used</span>
                        <span className="text-white">{(tracked.total_tokens / 1000).toFixed(1)}K</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">Est. Cost</span>
                        <span className="text-red-400 font-mono">${tracked.total_cost.toFixed(4)}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-2 pt-2 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500">{hasKey ? '' : 'No key configured'}</p>
                    </div>
                  )}
                  {status?.note && <p className="text-[10px] text-zinc-600 mt-2">{status.note}</p>}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Service Integration Status */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="integration-status-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2 text-base">
            <Plug className="w-5 h-5 text-violet-400" />
            Service Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.entries(integrationStatus).map(([svcId, svc]) => {
              const costData = {
                slack: { unit: "per message", cost: "$0.00", note: "Free (Bot Token). Slack charges per workspace, not per API call." },
                github: { unit: "per request", cost: "$0.00", note: "Free for public repos. 5,000 req/hr with token." },
                sendgrid: { unit: "per email", cost: "$0.001", note: "Free tier: 100 emails/day. Paid: ~$0.001/email." },
                resend: { unit: "per email", cost: "$0.001", note: "Free tier: 100 emails/day. Paid: ~$0.001/email." },
                twilio: { unit: "per SMS", cost: "$0.0079", note: "~$0.0079/SMS (US). Varies by country." },
                airtable: { unit: "per record", cost: "$0.00", note: "Free tier: 1,000 records. Paid: unlimited." },
                calendly: { unit: "per event", cost: "$0.00", note: "Free tier available. API included in paid plans." },
                giphy: { unit: "per search", cost: "$0.00", note: "Free API. Rate limited to 42 searches/hr." },
                google_suite: { unit: "per request", cost: "$0.00", note: "Free with service account. Quotas apply." },
              };
              const pricing = costData[svcId] || { unit: "per call", cost: "$0.00", note: "" };
              return (
                <div key={svcId} className="p-3 rounded-lg bg-white/5 border border-white/10" data-testid={`integration-status-${svcId}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{svc.name}</span>
                    <Badge className={svc.configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-500/20 text-zinc-400'}>
                      {svc.configured ? 'active' : 'no key'}
                    </Badge>
                  </div>
                  <p className="text-xs text-zinc-400">{svc.description}</p>
                  <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-500">Cost {pricing.unit}</span>
                      <span className="text-red-400 font-mono">{pricing.cost}</span>
                    </div>
                    {svc.key_fields?.map(field => (
                      <div key={field} className="flex justify-between text-xs">
                        <span className="text-zinc-500">{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <span className={svc.keys_set?.[field] ? "text-emerald-400" : "text-zinc-600"}>{svc.keys_set?.[field] ? "Set" : "Not set"}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-[10px] text-zinc-600 mt-2">{pricing.note}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Provider Selection */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <Key className="w-5 h-5 text-indigo-400" />
            </div>
            AI Provider Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Choose how to power your AI agents. Use the Emergent Universal Key for convenience, or plug in your own API keys to pay providers directly.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setApiKeyInputs(p => ({...p, active_provider: "emergent"}))}
              className={`p-4 rounded-lg border text-left transition-all ${
                apiKeyInputs.active_provider === "emergent"
                  ? "border-indigo-500 bg-indigo-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
              data-testid="provider-emergent-btn"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${apiKeyInputs.active_provider === "emergent" ? "bg-indigo-400" : "bg-zinc-600"}`} />
                <span className="text-white font-semibold">Emergent Universal Key</span>
              </div>
              <p className="text-xs text-zinc-400">One key for all models. Billed through Emergent.</p>
              {apiKeysConfig?.emergent_key_set && (
                <Badge className="mt-2 bg-emerald-500/20 text-emerald-400 text-[10px]">Active</Badge>
              )}
            </button>

            <button
              onClick={() => setApiKeyInputs(p => ({...p, active_provider: "direct"}))}
              className={`p-4 rounded-lg border text-left transition-all ${
                apiKeyInputs.active_provider === "direct"
                  ? "border-amber-500 bg-amber-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
              data-testid="provider-direct-btn"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${apiKeyInputs.active_provider === "direct" ? "bg-amber-400" : "bg-zinc-600"}`} />
                <span className="text-white font-semibold">Direct Provider Keys</span>
              </div>
              <p className="text-xs text-zinc-400">Your own API keys. Pay OpenAI, Anthropic & Google directly.</p>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Direct API Keys Input */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">
            {apiKeyInputs.active_provider === "direct" ? "Enter Your API Keys" : "Direct API Keys (Optional Backup)"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { id: "openai", name: "OpenAI", url: "https://platform.openai.com/api-keys", color: "emerald", set: apiKeysConfig?.openai_key_set, masked: apiKeysConfig?.openai_key },
            { id: "anthropic", name: "Anthropic", url: "https://console.anthropic.com/settings/keys", color: "orange", set: apiKeysConfig?.anthropic_key_set, masked: apiKeysConfig?.anthropic_key },
            { id: "gemini", name: "Google Gemini", url: "https://aistudio.google.com/apikey", color: "blue", set: apiKeysConfig?.gemini_key_set, masked: apiKeysConfig?.gemini_key },
            { id: "xai", name: "xAI (Grok)", url: "https://console.x.ai/", color: "zinc", set: apiKeysConfig?.xai_key_set, masked: apiKeysConfig?.xai_key },
            { id: "deepseek", name: "DeepSeek", url: "https://platform.deepseek.com/api_keys", color: "cyan", set: apiKeysConfig?.deepseek_key_set, masked: apiKeysConfig?.deepseek_key },
            { id: "mistral", name: "Mistral AI", url: "https://console.mistral.ai/api-keys/", color: "violet", set: apiKeysConfig?.mistral_key_set, masked: apiKeysConfig?.mistral_key },
            { id: "perplexity", name: "Perplexity", url: "https://www.perplexity.ai/settings/api", color: "teal", set: apiKeysConfig?.perplexity_key_set, masked: apiKeysConfig?.perplexity_key },
            { id: "cohere", name: "Cohere", url: "https://dashboard.cohere.com/api-keys", color: "pink", set: apiKeysConfig?.cohere_key_set, masked: apiKeysConfig?.cohere_key },
            { id: "groq", name: "Groq (Llama 4)", url: "https://console.groq.com/keys", color: "amber", set: apiKeysConfig?.groq_key_set, masked: apiKeysConfig?.groq_key },
            { id: "together", name: "Together AI", url: "https://api.together.ai/settings/api-keys", color: "lime", set: apiKeysConfig?.together_key_set, masked: apiKeysConfig?.together_key },
            { id: "fireworks", name: "Fireworks AI", url: "https://fireworks.ai/account/api-keys", color: "red", set: apiKeysConfig?.fireworks_key_set, masked: apiKeysConfig?.fireworks_key },
            { id: "ai21", name: "AI21 (Jamba)", url: "https://studio.ai21.com/account/api-key", color: "indigo", set: apiKeysConfig?.ai21_key_set, masked: apiKeysConfig?.ai21_key },
            { id: "elevenlabs", name: "ElevenLabs (TTS)", url: "https://elevenlabs.io/app/settings/api-keys", color: "yellow", set: apiKeysConfig?.elevenlabs_key_set, masked: apiKeysConfig?.elevenlabs_key },
          ].map((provider) => (
            <div key={provider.id} className="p-4 rounded-lg bg-white/5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full bg-${provider.color}-400`} />
                  <span className="text-white font-medium">{provider.name}</span>
                  {provider.set && <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Saved: {provider.masked}</Badge>}
                </div>
                <a href={provider.url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline">Get key</a>
              </div>
              <div className="flex gap-2">
                <Input
                  type="password"
                  value={apiKeyInputs[`${provider.id}_key`]}
                  onChange={(e) => setApiKeyInputs(p => ({...p, [`${provider.id}_key`]: e.target.value}))}
                  placeholder={provider.set ? "Enter new key to replace..." : `sk-... or your ${provider.name} API key`}
                  className="bg-zinc-800/50 border-white/10 text-sm font-mono"
                  data-testid={`apikey-${provider.id}-input`}
                />
                <Button
                  variant="outline"
                  size="sm"
                  className="border-white/10 shrink-0"
                  onClick={() => handleTestKey(provider.id, apiKeyInputs[`${provider.id}_key`])}
                  disabled={!apiKeyInputs[`${provider.id}_key`] || testingKey === provider.id}
                  data-testid={`test-${provider.id}-btn`}
                >
                  {testingKey === provider.id ? "Testing..." : "Test"}
                </Button>
              </div>
            </div>
          ))}

          <div className="flex gap-3 pt-2">
            <Button
              onClick={handleSaveApiKeys}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
              data-testid="save-apikeys-btn"
            >
              Save Configuration
            </Button>
          </div>

          {apiKeyInputs.active_provider === "direct" && (
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <p className="text-amber-300 text-sm">
                <strong>Direct mode:</strong> AI calls will use your provider keys. If a key is missing for a provider, it falls back to Emergent key. Make sure at least one key is set per provider you use.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* End of API Keys section */}
    </div>
    );
};
