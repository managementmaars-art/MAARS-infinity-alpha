import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import { Bot, ArrowLeft, Plus, X, Sparkles, CreditCard, Lock, AlertTriangle } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const CreateAgent = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [capability, setCapability] = useState("");
  const [createInfo, setCreateInfo] = useState(null);
  const [infoLoading, setInfoLoading] = useState(true);
  
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    role: "",
    system_prompt: "",
    model_provider: "openai",
    model_name: "gpt-5.2",
    avatar: "",
    capabilities: []
  });

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchCreateInfo();
  }, []);

  const fetchCreateInfo = async () => {
    try {
      const res = await fetch(`${API}/agents/create/info`, { credentials: "include", headers });
      if (res.ok) setCreateInfo(await res.json());
    } catch {
      // Silently fail
    } finally {
      setInfoLoading(false);
    }
  };

  const modelOptions = {
    openai: [
      { value: "gpt-5.2", label: "GPT-5.2 (Latest)" },
      { value: "gpt-4o", label: "GPT-4o" },
      { value: "o3", label: "O3 (Reasoning)" }
    ],
    anthropic: [
      { value: "claude-sonnet-4-5-20250929", label: "Claude Sonnet 4.5" },
      { value: "claude-opus-4-5-20251101", label: "Claude Opus 4.5" }
    ],
    gemini: [
      { value: "gemini-3-flash-preview", label: "Gemini 3 Flash" },
      { value: "gemini-3-pro-preview", label: "Gemini 3 Pro" }
    ]
  };

  const robotAvatars = [
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/43ae7e2a837703cb3a5da4fdd616bc12c825f9f0f15b7e9304e61a3dab0bd257.png",
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c4305af2c26cea8648db361e275c2f1ef2db69815efff20a57aa4e0807abfcce.png",
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/48310a3af62b331e8f13d73aa7ac03cdfd9565c00fc03fd7dade81f63edfe3a7.png",
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c608195e54230fb30922f73d04dd840a095e7d6ee759b4b9cfe368511284876d.png",
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/2ceaf34f302e1bf7d622058c516b8e86782c142d9a32dee38b13da10b8f0514c.png",
    "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/96d5c274e3657d527a5a8c4bf869dcfdb08530445029e0df555139dba990b2cc.png"
  ];

  const addCapability = () => {
    if (capability.trim() && !formData.capabilities.includes(capability.trim())) {
      setFormData(prev => ({ ...prev, capabilities: [...prev.capabilities, capability.trim()] }));
      setCapability("");
    }
  };

  const removeCapability = (cap) => {
    setFormData(prev => ({ ...prev, capabilities: prev.capabilities.filter(c => c !== cap) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.role || !formData.system_prompt) {
      toast.error("Please fill in all required fields");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API}/agents`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const agent = await response.json();
        toast.success("Agent created successfully!");
        navigate(`/chat/${agent.agent_id}`);
      } else {
        const data = await response.json();
        toast.error(data.detail || "Failed to create agent");
      }
    } catch {
      toast.error("Failed to create agent");
    } finally {
      setLoading(false);
    }
  };

  const canCreate = createInfo?.can_create;
  const isBlocked = createInfo && !canCreate && !createInfo.is_admin;

  return (
    <div className="min-h-screen bg-background" data-testid="create-agent-page">
      <div className="max-w-3xl mx-auto p-6 lg:p-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            to="/agents"
            className="inline-flex items-center gap-2 text-zinc-400 hover:text-white mb-4 transition-colors"
            data-testid="back-to-agents"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Agents
          </Link>
          <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
            Create Custom Agent
          </h1>
          <p className="text-zinc-400">Build a personalized AI agent tailored to your needs</p>
        </div>

        {/* Cost & Limits Info Card */}
        {!infoLoading && createInfo && (
          <Card className={`mb-6 border ${isBlocked ? 'bg-red-950/20 border-red-500/30' : 'bg-zinc-900/50 border-white/10'}`} data-testid="create-agent-info-card">
            <CardContent className="p-4">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <CreditCard className={`w-4 h-4 ${isBlocked ? 'text-red-400' : 'text-indigo-400'}`} />
                  <span className="text-sm text-zinc-300">
                    Cost: <span className="font-semibold text-white">{createInfo.credit_cost} credits</span>
                  </span>
                </div>
                <div className="w-px h-4 bg-white/10" />
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-300">
                    {createInfo.max_custom_agents === -1 ? (
                      "Unlimited custom agents"
                    ) : (
                      <>Used: <span className="font-semibold text-white">{createInfo.current_custom_count}/{createInfo.max_custom_agents}</span> slots</>
                    )}
                  </span>
                </div>
                <div className="w-px h-4 bg-white/10" />
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-300">
                    Balance: <span className="font-semibold text-white">{createInfo.credits_remaining} credits</span>
                  </span>
                </div>
                <Badge className={`ml-auto text-xs ${
                  createInfo.plan_name === 'Business' ? 'bg-amber-500/20 text-amber-400' :
                  createInfo.plan_name === 'Pro' ? 'bg-violet-500/20 text-violet-400' :
                  createInfo.plan_name === 'Starter' ? 'bg-indigo-500/20 text-indigo-400' :
                  'bg-zinc-500/20 text-zinc-400'
                }`}>
                  {createInfo.plan_name} Plan
                </Badge>
              </div>

              {isBlocked && (
                <div className="mt-3 flex items-start gap-2 p-3 rounded-lg bg-red-500/10">
                  <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                  <div className="text-sm">
                    {createInfo.max_custom_agents === 0 ? (
                      <p className="text-red-300">
                        Custom agent creation is not available on the Free plan. 
                        <button onClick={() => navigate("/pricing")} className="text-red-400 underline ml-1 hover:text-red-300">Upgrade now</button>
                      </p>
                    ) : !createInfo.can_afford ? (
                      <p className="text-red-300">
                        Not enough credits ({createInfo.credits_remaining}/{createInfo.credit_cost} needed). 
                        <button onClick={() => navigate("/pricing")} className="text-red-400 underline ml-1 hover:text-red-300">Buy credits</button>
                      </p>
                    ) : (
                      <p className="text-red-300">
                        Custom agent limit reached ({createInfo.current_custom_count}/{createInfo.max_custom_agents}). 
                        <button onClick={() => navigate("/pricing")} className="text-red-400 underline ml-1 hover:text-red-300">Upgrade plan</button>
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Avatar Selection */}
          <div>
            <Label className="text-zinc-300 mb-3 block">Avatar</Label>
            <div className="flex flex-wrap gap-3">
              {robotAvatars.map((url, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, avatar: url }))}
                  className={`w-16 h-16 rounded-lg overflow-hidden transition-all ${
                    formData.avatar === url
                      ? "ring-2 ring-indigo-500 ring-offset-2 ring-offset-background"
                      : "opacity-60 hover:opacity-100"
                  }`}
                  data-testid={`avatar-option-${i}`}
                >
                  <img src={url} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-zinc-300">Agent Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Project Manager AI"
                className="bg-zinc-900/50 border-white/10 focus:border-indigo-500"
                required
                disabled={isBlocked}
                data-testid="agent-name-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role" className="text-zinc-300">Role *</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                placeholder="e.g., Project Manager"
                className="bg-zinc-900/50 border-white/10 focus:border-indigo-500"
                required
                disabled={isBlocked}
                data-testid="agent-role-input"
              />
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-zinc-300">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe what this agent does..."
              className="bg-zinc-900/50 border-white/10 focus:border-indigo-500 min-h-[80px]"
              disabled={isBlocked}
              data-testid="agent-description-input"
            />
          </div>

          {/* System Prompt */}
          <div className="space-y-2">
            <Label htmlFor="system_prompt" className="text-zinc-300">System Prompt *</Label>
            <Textarea
              id="system_prompt"
              value={formData.system_prompt}
              onChange={(e) => setFormData(prev => ({ ...prev, system_prompt: e.target.value }))}
              placeholder="You are an expert AI assistant that..."
              className="bg-zinc-900/50 border-white/10 focus:border-indigo-500 min-h-[150px] font-mono text-sm"
              required
              disabled={isBlocked}
              data-testid="agent-prompt-input"
            />
            <p className="text-xs text-zinc-500">This defines your agent's personality and expertise</p>
          </div>

          {/* Model Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-zinc-300">AI Provider</Label>
              <Select
                value={formData.model_provider}
                onValueChange={(value) => {
                  setFormData(prev => ({
                    ...prev,
                    model_provider: value,
                    model_name: modelOptions[value][0].value
                  }));
                }}
                disabled={isBlocked}
              >
                <SelectTrigger className="bg-zinc-900/50 border-white/10" data-testid="provider-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                  <SelectItem value="gemini">Google (Gemini)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">Model</Label>
              <Select
                value={formData.model_name}
                onValueChange={(value) => setFormData(prev => ({ ...prev, model_name: value }))}
                disabled={isBlocked}
              >
                <SelectTrigger className="bg-zinc-900/50 border-white/10" data-testid="model-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {modelOptions[formData.model_provider].map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      {model.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Capabilities */}
          <div className="space-y-2">
            <Label className="text-zinc-300">Capabilities</Label>
            <div className="flex gap-2">
              <Input
                value={capability}
                onChange={(e) => setCapability(e.target.value)}
                placeholder="Add a capability..."
                className="bg-zinc-900/50 border-white/10 focus:border-indigo-500"
                onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addCapability())}
                disabled={isBlocked}
                data-testid="capability-input"
              />
              <Button type="button" onClick={addCapability} variant="outline" className="border-white/10 hover:bg-white/5" disabled={isBlocked} data-testid="add-capability-btn">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            {formData.capabilities.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {formData.capabilities.map((cap, i) => (
                  <Badge key={i} variant="secondary" className="bg-indigo-500/20 text-indigo-300 border-0 pr-1">
                    {cap}
                    <button type="button" onClick={() => removeCapability(cap)} className="ml-2 hover:text-white" data-testid={`remove-cap-${i}`}>
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Submit */}
          <div className="flex gap-4 pt-4">
            <Button type="button" variant="outline" className="flex-1 border-white/10 hover:bg-white/5" onClick={() => navigate("/agents")} data-testid="cancel-btn">
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary"
              disabled={loading || isBlocked}
              data-testid="create-agent-submit-btn"
            >
              {loading ? "Creating..." : isBlocked ? (
                <><Lock className="w-4 h-4 mr-2" />Upgrade to Create</>
              ) : (
                <><Sparkles className="w-4 h-4 mr-2" />Create Agent ({createInfo?.credit_cost || 20} credits)</>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAgent;
