import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Key, Activity, Plug, Zap, Globe, TrendingDown } from "lucide-react";
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
        toast.success(`API keys saved! Using: ${data.active_provider === 'direct' ? 'Direct Provider Keys' : 'MAARS AI Gateway'}`);
        fetchAdminData();
        setApiKeyInputs(prev => ({...prev, openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: "", groq_key: "", together_key: "", fireworks_key: "", ai21_key: "", cerebras_key: "", sambanova_key: "", nvidia_key: "", moonshot_key: "", qwen_key: "", yi_key: "", zhipu_key: "", doubao_key: "", hyperbolic_key: "", upstage_key: "", writer_key: "", huggingface_key: "", llama_key: "", novita_key: "", lepton_key: "", lambda_key: "", amazon_key: "", minimax_key: "", inception_key: "", arcee_key: ""}));
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

      {/* Universal Gateway Banner */}
      <Card className="bg-gradient-to-br from-indigo-950/80 to-violet-950/80 border-indigo-500/30">
        <CardContent className="pt-5 pb-5">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center shrink-0">
              <Zap className="w-6 h-6 text-indigo-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-white font-semibold text-base font-['Outfit']">MAARS Universal AI Gateway</h3>
                <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">ACTIVE</Badge>
              </div>
              <p className="text-zinc-400 text-sm mt-1">
                Single endpoint routing all <span className="text-indigo-300 font-medium">33 providers & 175,000+ models</span> —
                auto-selects the cheapest capable model per request. No per-provider switching needed.
              </p>
              <div className="flex flex-wrap gap-4 mt-3 text-xs text-zinc-400">
                <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-indigo-400" /><code className="bg-white/5 px-1.5 py-0.5 rounded text-indigo-300">POST /api/universal/chat</code></span>
                <span className="flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-emerald-400" /><code className="bg-white/5 px-1.5 py-0.5 rounded text-zinc-300">GET /api/universal/models</code></span>
                <span className="flex items-center gap-1.5"><TrendingDown className="w-3.5 h-3.5 text-amber-400" /><code className="bg-white/5 px-1.5 py-0.5 rounded text-zinc-300">GET /api/universal/stats</code></span>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 shrink-0">
              {[
                { label: "Economy", desc: "Gemini 2.5 Flash, Llama 4, Cerebras, Mistral Nemo", color: "emerald" },
                { label: "Standard", desc: "GPT-4.1, Gemini 2.5 Pro, DeepSeek R1, Claude Haiku", color: "amber" },
                { label: "Premium", desc: "GPT-5, Claude Opus 4.6, Claude Sonnet 4.6, Grok-4", color: "violet" },
              ].map(t => (
                <div key={t.label} className={`p-2.5 rounded-lg bg-${t.color}-500/10 border border-${t.color}-500/20 text-center`}>
                  <p className={`text-xs font-semibold text-${t.color}-400`}>{t.label}</p>
                  <p className="text-[10px] text-zinc-500 mt-0.5 leading-tight">{t.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

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
            {["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs", "groq", "together", "fireworks", "ai21", "cerebras", "sambanova", "nvidia", "moonshot", "qwen", "yi", "zhipu", "doubao", "hyperbolic", "upstage", "writer", "huggingface", "llama", "novita", "lepton", "lambda", "amazon", "minimax", "inception", "arcee"].map(provider => {
              const status = usage.providers?.[provider];
              const tracked = usage.tracked_usage?.[provider];
              const providerLabels = { openai: "OpenAI", anthropic: "Anthropic", gemini: "Google Gemini", xai: "xAI (Grok)", deepseek: "DeepSeek", mistral: "Mistral AI", perplexity: "Perplexity", cohere: "Cohere", elevenlabs: "ElevenLabs", groq: "Groq (Llama 4)", together: "Together AI", fireworks: "Fireworks AI", ai21: "AI21 (Jamba)", cerebras: "Cerebras (Ultra-Fast)", sambanova: "SambaNova", nvidia: "Nvidia NIM", moonshot: "Moonshot AI (Kimi)", qwen: "Qwen / Alibaba", yi: "01.AI / Yi", zhipu: "Zhipu AI (GLM)", doubao: "ByteDance Doubao", hyperbolic: "Hyperbolic", upstage: "Upstage Solar", writer: "Writer Palmyra", huggingface: "HuggingFace", llama: "Meta Llama API", novita: "Novita AI", lepton: "Lepton AI", lambda: "Lambda Labs", amazon: "Amazon Bedrock (Nova)", minimax: "Minimax AI", inception: "Inception AI (Mercury)", arcee: "Arcee AI" };
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
          <p className="text-zinc-400 text-sm">Choose how to power your AI agents. Use the MAARS AI Gateway for convenience, or plug in your own API keys to pay providers directly.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setApiKeyInputs(p => ({...p, active_provider: "maars"}))}
              className={`p-4 rounded-lg border text-left transition-all ${
                apiKeyInputs.active_provider === "maars" || apiKeyInputs.active_provider === "emergent"
                  ? "border-indigo-500 bg-indigo-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
              data-testid="provider-maars-btn"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${apiKeyInputs.active_provider === "maars" || apiKeyInputs.active_provider === "emergent" ? "bg-indigo-400" : "bg-zinc-600"}`} />
                <span className="text-white font-semibold">MAARS AI Gateway</span>
              </div>
              <p className="text-xs text-zinc-400">One key for all models. Billed through MAARS.</p>
              {(apiKeysConfig?.emergent_key_set || apiKeysConfig?.maars_key_set) && (
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
            { id: "cerebras", name: "Cerebras (Ultra-Fast)", url: "https://cloud.cerebras.ai/", color: "sky", set: apiKeysConfig?.cerebras_key_set, masked: apiKeysConfig?.cerebras_key },
            { id: "sambanova", name: "SambaNova", url: "https://cloud.sambanova.ai/apis", color: "fuchsia", set: apiKeysConfig?.sambanova_key_set, masked: apiKeysConfig?.sambanova_key },
            { id: "nvidia", name: "Nvidia NIM", url: "https://build.nvidia.com/", color: "green", set: apiKeysConfig?.nvidia_key_set, masked: apiKeysConfig?.nvidia_key },
            { id: "moonshot", name: "Moonshot AI (Kimi)", url: "https://platform.moonshot.cn/", color: "teal", set: apiKeysConfig?.moonshot_key_set, masked: apiKeysConfig?.moonshot_key },
            { id: "qwen", name: "Qwen / Alibaba DashScope", url: "https://dashscope.aliyuncs.com/", color: "orange", set: apiKeysConfig?.qwen_key_set, masked: apiKeysConfig?.qwen_key },
            { id: "yi", name: "01.AI / Yi", url: "https://platform.lingyiwanwu.com/", color: "purple", set: apiKeysConfig?.yi_key_set, masked: apiKeysConfig?.yi_key },
            { id: "zhipu", name: "Zhipu AI (GLM)", url: "https://open.bigmodel.cn/", color: "blue", set: apiKeysConfig?.zhipu_key_set, masked: apiKeysConfig?.zhipu_key },
            { id: "doubao", name: "ByteDance Doubao", url: "https://console.volcengine.com/ark/", color: "red", set: apiKeysConfig?.doubao_key_set, masked: apiKeysConfig?.doubao_key },
            { id: "hyperbolic", name: "Hyperbolic", url: "https://app.hyperbolic.xyz/settings", color: "emerald", set: apiKeysConfig?.hyperbolic_key_set, masked: apiKeysConfig?.hyperbolic_key },
            { id: "upstage", name: "Upstage Solar", url: "https://console.upstage.ai/api-keys", color: "amber", set: apiKeysConfig?.upstage_key_set, masked: apiKeysConfig?.upstage_key },
            { id: "writer", name: "Writer Palmyra", url: "https://dev.writer.com/api-guides/authentication", color: "slate", set: apiKeysConfig?.writer_key_set, masked: apiKeysConfig?.writer_key },
            { id: "huggingface", name: "HuggingFace", url: "https://huggingface.co/settings/tokens", color: "yellow", set: apiKeysConfig?.huggingface_key_set, masked: apiKeysConfig?.huggingface_key },
            { id: "llama", name: "Meta Llama API", url: "https://llama.meta.com/llama-api/", color: "blue", set: apiKeysConfig?.llama_key_set, masked: apiKeysConfig?.llama_key },
            { id: "novita", name: "Novita AI", url: "https://novita.ai/settings", color: "violet", set: apiKeysConfig?.novita_key_set, masked: apiKeysConfig?.novita_key },
            { id: "lepton", name: "Lepton AI", url: "https://dashboard.lepton.ai/", color: "orange", set: apiKeysConfig?.lepton_key_set, masked: apiKeysConfig?.lepton_key },
            { id: "lambda", name: "Lambda Labs", url: "https://lambdalabs.com/service/gpu-cloud/api-keys", color: "cyan", set: apiKeysConfig?.lambda_key_set, masked: apiKeysConfig?.lambda_key },
            { id: "amazon", name: "Amazon Bedrock (Nova)", url: "https://console.aws.amazon.com/bedrock/", color: "yellow", set: apiKeysConfig?.amazon_key_set, masked: apiKeysConfig?.amazon_key },
            { id: "minimax", name: "Minimax AI", url: "https://platform.minimaxi.com/", color: "sky", set: apiKeysConfig?.minimax_key_set, masked: apiKeysConfig?.minimax_key },
            { id: "inception", name: "Inception AI (Mercury)", url: "https://api.inception.ai/", color: "fuchsia", set: apiKeysConfig?.inception_key_set, masked: apiKeysConfig?.inception_key },
            { id: "arcee", name: "Arcee AI", url: "https://app.arcee.ai/", color: "rose", set: apiKeysConfig?.arcee_key_set, masked: apiKeysConfig?.arcee_key },
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
                <strong>Direct mode:</strong> AI calls will use your provider keys. If a key is missing for a provider, it falls back to the MAARS AI Gateway. Make sure at least one key is set per provider you use.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* End of API Keys section */}
    </div>
    );
};
