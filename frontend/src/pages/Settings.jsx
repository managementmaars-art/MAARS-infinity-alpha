import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { User, Mail, LogOut, CreditCard, Sparkles, Crown, Zap,
  Check, Save, Loader2, Cpu, Link2, Unlink, Shield, Users
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [allAgents, setAllAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [agentConfig, setAgentConfig] = useState(null);
  const [savingAgents, setSavingAgents] = useState(false);
  const [llmConfig, setLlmConfig] = useState(null);
  const [savingLlm, setSavingLlm] = useState(false);
  const [actionIntegrations, setActionIntegrations] = useState(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchSubscription();
    fetchAgents();
    fetchSelectedAgents();
    fetchLlmConfig();
    fetchActionIntegrations();
  }, []);

  const fetchSubscription = async () => {
    try {
      const response = await fetch(`${API}/subscription`, { headers
      });
      if (response.ok) {
        setSubscription(await response.json());
      }
    } catch (error) {
      console.error("Failed to fetch subscription");
    }
  };

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API}/agents`, { headers, });
      if (res.ok) setAllAgents(await res.json());
    } catch {}
  };

  const fetchSelectedAgents = async () => {
    try {
      const res = await fetch(`${API}/subscription/agents`, { headers, });
      if (res.ok) {
        const data = await res.json();
        setAgentConfig(data);
        setSelectedAgents(data.selected_agents || []);
      }
    } catch {}
  };

  const toggleAgentSelection = (agentId) => {
    setSelectedAgents(prev =>
      prev.includes(agentId) ? prev.filter(id => id !== agentId) : [...prev, agentId]
    );
  };

  const fetchLlmConfig = async () => {
    try {
      const res = await fetch(`${API}/llm/config`, { headers });
      if (res.ok) setLlmConfig(await res.json());
    } catch {}
  };

  const saveLlmConfig = async (provider, model) => {
    setSavingLlm(true);
    try {
      const res = await fetch(`${API}/llm/config`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ provider, model }),
      });
      if (res.ok) {
        const updated = await res.json();
        setLlmConfig(prev => ({ ...prev, ...updated }));
        toast.success(`Model updated to ${provider}/${model}`);
      }
    } catch { toast.error("Failed to save model config"); }
    finally { setSavingLlm(false); }
  };

  const fetchActionIntegrations = async () => {
    try {
      const res = await fetch(`${API}/actions/integrations`, { headers });
      if (res.ok) setActionIntegrations(await res.json());
    } catch {}
  };

  const connectGoogle = async () => {
    try {
      const res = await fetch(`${API}/oauth/gmail/login`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (data.auth_url) window.location.href = data.auth_url;
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Google OAuth not configured");
      }
    } catch { toast.error("Failed to start Google connection"); }
  };

  const disconnectGoogle = async () => {
    try {
      await fetch(`${API}/oauth/gmail/disconnect`, { headers });
      toast.success("Google disconnected");
      fetchActionIntegrations();
    } catch {}
  };

  const saveAgentSelection = async () => {
    setSavingAgents(true);
    try {
      const res = await fetch(`${API}/subscription/agents`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ selected_agents: selectedAgents })
      });
      if (res.ok) {
        toast.success("Agent selection saved!");
        fetchSelectedAgents();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to save");
      }
    } catch { toast.error("Failed to save"); }
    finally { setSavingAgents(false); }
  };

  const getPlanIcon = (plan) => {
    switch (plan) {
      case "business": return <Crown className="w-5 h-5" />;
      case "pro": return <Sparkles className="w-5 h-5" />;
      case "starter": return <Zap className="w-5 h-5" />;
      default: return <CreditCard className="w-5 h-5" />;
    }
  };

  const getPlanColor = (plan) => {
    switch (plan) {
      case "business": return "text-amber-400 bg-amber-500/20";
      case "pro": return "text-violet-400 bg-violet-500/20";
      case "starter": return "text-indigo-400 bg-indigo-500/20";
      default: return "text-zinc-400 bg-zinc-500/20";
    }
  };

  return (
    <div data-testid="settings-page">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
              Settings
            </h1>
            <p className="text-zinc-400">Manage your account and preferences</p>
          </div>

          {/* Profile Section */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <User className="w-5 h-5 text-indigo-400" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center overflow-hidden">
                  {user?.picture ? (
                    <img src={user.picture} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-2xl text-white font-semibold">
                      {user?.name?.charAt(0) || "U"}
                    </span>
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{user?.name}</h3>
                  <p className="text-zinc-400">{user?.email}</p>
                </div>
              </div>

              <Separator className="bg-white/10" />

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-zinc-300">Full Name</Label>
                  <Input
                    value={user?.name || ""}
                    disabled
                    className="bg-zinc-800/50 border-white/10"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-zinc-300">Email</Label>
                  <Input
                    value={user?.email || ""}
                    disabled
                    className="bg-zinc-800/50 border-white/10"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Subscription & Credits Section */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-indigo-400" />
                Subscription & Credits
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Current Plan */}
              <div className="p-4 rounded-lg bg-zinc-800/30">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getPlanColor(subscription?.plan_id || "free")}`}>
                      {getPlanIcon(subscription?.plan_id || "free")}
                    </div>
                    <div>
                      <p className="font-medium text-white">
                        {subscription?.plan_info?.name || "Free"} Plan
                      </p>
                      <p className="text-sm text-zinc-400">
                        ${subscription?.plan_info?.price || 0}/month
                      </p>
                    </div>
                  </div>
                  <Button
                    onClick={() => navigate("/pricing")}
                    className="bg-gradient-to-r from-indigo-500 to-violet-500"
                    data-testid="upgrade-plan-btn"
                  >
                    {subscription?.plan_id === "business" ? "Manage Plan" : "Upgrade"}
                  </Button>
                </div>
              </div>

              {/* Credits */}
              <div className="p-4 rounded-lg bg-zinc-800/30">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-white">Credits Remaining</p>
                  <Badge className={getPlanColor(subscription?.plan_id || "free")}>
                    {subscription?.credits || 0} credits
                  </Badge>
                </div>
                <Progress 
                  value={subscription?.plan_info?.credits ? 
                    ((subscription?.credits || 0) / subscription.plan_info.credits) * 100 : 
                    ((subscription?.credits || 0) / 50) * 100
                  } 
                  className="h-2 bg-zinc-700"
                />
                <div className="flex justify-between mt-2 text-xs text-zinc-500">
                  <span>Used: {subscription?.credits_used || 0}</span>
                  <span>Monthly: {subscription?.plan_info?.credits || 50}</span>
                </div>
              </div>

              {/* Buy More Credits */}
              <Button
                onClick={() => navigate("/pricing")}
                variant="outline"
                className="w-full border-white/10 hover:bg-white/5"
                data-testid="buy-credits-btn"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Buy More Credits
              </Button>
            </CardContent>
          </Card>

          {/* LLM Model Configuration */}
          {llmConfig && (
            <Card className="bg-zinc-900/50 border-white/10 mb-6" data-testid="llm-config-card">
              <CardHeader>
                <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-indigo-400" />
                  AI Model Configuration
                </CardTitle>
                <p className="text-xs text-zinc-400 mt-1">Choose your preferred LLM provider and model for Vibe Coding, Reference Intelligence, and other AI features</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {llmConfig.available_providers?.map(p => (
                    <button
                      key={p.id}
                      onClick={() => saveLlmConfig(p.id, p.models[0])}
                      className={`p-3 rounded-lg border transition-all text-left ${
                        llmConfig.provider === p.id
                          ? "border-indigo-500 bg-indigo-500/10"
                          : "border-white/10 bg-zinc-800/30 hover:border-white/20"
                      }`}
                      disabled={savingLlm}
                      data-testid={`llm-provider-${p.id}`}
                    >
                      <p className="text-sm font-medium text-white">{p.name}</p>
                      <p className="text-[10px] text-zinc-500 mt-1">{p.models.length} models</p>
                      {llmConfig.provider === p.id && (
                        <div className="mt-2 flex items-center gap-1">
                          <Check className="w-3 h-3 text-indigo-400" />
                          <span className="text-[10px] text-indigo-400">Active</span>
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                {/* Model Selector */}
                {llmConfig.available_providers?.filter(p => p.id === llmConfig.provider).map(p => (
                  <div key={p.id}>
                    <p className="text-xs text-zinc-400 mb-2">Select model for {p.name}:</p>
                    <div className="flex flex-wrap gap-2">
                      {p.models.map(m => (
                        <button
                          key={m}
                          onClick={() => saveLlmConfig(p.id, m)}
                          className={`px-3 py-1.5 rounded-md text-xs transition-colors ${
                            llmConfig.model === m
                              ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/40"
                              : "bg-zinc-800/50 text-zinc-400 border border-white/5 hover:border-white/15"
                          }`}
                          disabled={savingLlm}
                          data-testid={`llm-model-${m}`}
                        >
                          {m}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="p-3 rounded-lg bg-zinc-800/30 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-white">Current Model</p>
                    <p className="text-[10px] text-zinc-500 font-mono">{llmConfig.provider}/{llmConfig.model}</p>
                  </div>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-[10px]">Active</Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Integrations / Action Layer */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6" data-testid="integrations-card">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <Link2 className="w-5 h-5 text-indigo-400" />
                Integrations & Actions
              </CardTitle>
              <p className="text-xs text-zinc-400 mt-1">Connect external services for real-world agent actions</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Google Suite */}
              <div className="p-4 rounded-lg bg-zinc-800/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center">
                      <Mail className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">Google Suite</p>
                      <p className="text-[10px] text-zinc-500">Gmail, Calendar integration</p>
                      {actionIntegrations?.integrations?.[0]?.email && (
                        <p className="text-[10px] text-emerald-400">{actionIntegrations.integrations[0].email}</p>
                      )}
                    </div>
                  </div>
                  {actionIntegrations?.integrations?.[0]?.connected ? (
                    <Button size="sm" variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10" onClick={disconnectGoogle} data-testid="disconnect-google-btn">
                      <Unlink className="w-3.5 h-3.5 mr-1" />Disconnect
                    </Button>
                  ) : (
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-white" onClick={connectGoogle} data-testid="connect-google-btn">
                      <Link2 className="w-3.5 h-3.5 mr-1" />Connect
                    </Button>
                  )}
                </div>
              </div>

              {/* System Mode Info */}
              <div className="p-3 rounded-lg bg-zinc-800/20 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${actionIntegrations?.system_mode === "execution" ? "bg-emerald-400" : "bg-amber-400 animate-pulse"}`} />
                <p className="text-xs text-zinc-400">
                  System Mode: <span className={actionIntegrations?.system_mode === "execution" ? "text-emerald-400" : "text-amber-400"}>
                    {actionIntegrations?.system_mode === "execution" ? "Execution (Live)" : "Simulation (Safe)"}
                  </span>
                  <span className="text-zinc-600 ml-2">Toggle in KPI Dashboard</span>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Agent Selection */}
          {agentConfig && agentConfig.plan_id !== "custom" && (
            <Card className="bg-zinc-900/50 border-white/10 mb-6" data-testid="agent-selection-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                    <Users className="w-5 h-5 text-indigo-400" />
                    Your Agents
                  </CardTitle>
                  <Badge className="bg-indigo-500/20 text-indigo-400 border-0">
                    {selectedAgents.filter(a => a !== "agent_commander").length} / {agentConfig.max_agents} slots
                  </Badge>
                </div>
                <p className="text-sm text-zinc-400 mt-1">
                  Select which agents you want access to. Your {(subscription?.plan_info?.name || "Free")} plan allows up to {agentConfig.max_agents} agents.
                  {agentConfig.includes_commander && " Commander AI is included with your plan."}
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 mb-4">
                  {allAgents.filter(a => a.agent_id !== "agent_commander").map((agent) => {
                    const isSelected = selectedAgents.includes(agent.agent_id);
                    const atLimit = !isSelected && selectedAgents.filter(a => a !== "agent_commander").length >= agentConfig.max_agents;
                    return (
                      <button
                        key={agent.agent_id}
                        onClick={() => !atLimit && toggleAgentSelection(agent.agent_id)}
                        disabled={atLimit && !isSelected}
                        className={`relative flex flex-col items-center gap-1.5 p-2.5 rounded-lg border transition-all ${
                          isSelected
                            ? "border-indigo-500 bg-indigo-500/15"
                            : atLimit
                            ? "border-white/5 bg-zinc-900/30 opacity-40 cursor-not-allowed"
                            : "border-white/10 bg-zinc-800/30 hover:border-white/20"
                        }`}
                        data-testid={`select-agent-${agent.agent_id}`}
                      >
                        {isSelected && (
                          <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-indigo-500 flex items-center justify-center">
                            <Check className="w-2.5 h-2.5 text-white" />
                          </div>
                        )}
                        <img src={agent.avatar} alt="" className="w-8 h-8 rounded-md object-cover" />
                        <p className="text-[10px] text-white font-medium truncate max-w-[80px]">{agent.name}</p>
                        <p className="text-[8px] text-zinc-500 truncate max-w-[80px]">{agent.role}</p>
                      </button>
                    );
                  })}
                </div>
                <Button
                  onClick={saveAgentSelection}
                  disabled={savingAgents}
                  className="w-full bg-gradient-to-r from-indigo-500 to-violet-500"
                  data-testid="save-agents-btn"
                >
                  {savingAgents ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                  Save Selection
                </Button>
              </CardContent>
            </Card>
          )}

          {agentConfig?.plan_id === "custom" && (
            <Card className="bg-zinc-900/50 border-amber-500/20 mb-6" data-testid="custom-agents-info">
              <CardHeader>
                <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                  <Users className="w-5 h-5 text-amber-400" />
                  Your Custom Package Agents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 mb-3">
                  {allAgents.filter(a => selectedAgents.includes(a.agent_id)).map((agent) => (
                    <div key={agent.agent_id} className="flex flex-col items-center gap-1.5 p-2.5 rounded-lg border border-amber-500/20 bg-amber-500/5">
                      <img src={agent.avatar} alt="" className="w-8 h-8 rounded-md object-cover" />
                      <p className="text-[10px] text-white font-medium truncate max-w-[80px]">{agent.name}</p>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-zinc-500 text-center">
                  Custom package agents are set at purchase. <Link to="/pricing" className="text-amber-400 underline">Build a new package</Link> to change.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Account Section */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-400" />
                Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-800/30">
                <div>
                  <p className="font-medium text-white">User ID</p>
                  <p className="text-sm text-zinc-400 font-mono">{user?.user_id}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-800/30">
                <div>
                  <p className="font-medium text-white">AI Providers</p>
                  <p className="text-sm text-zinc-400">OpenAI, Anthropic, Google Gemini</p>
                </div>
                <span className="px-3 py-1 text-xs rounded-full bg-emerald-500/20 text-emerald-400">
                  Connected
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Account */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-zinc-300 font-['Outfit']">Account</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Sign Out</p>
                  <p className="text-sm text-zinc-400">Sign out from your account</p>
                </div>
                <Button
                  variant="outline"
                  className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  onClick={async () => { await logout(); navigate("/"); }}
                  data-testid="logout-btn"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            </CardContent>
          </Card>
    </div>
  );
};

export default SettingsPage;
