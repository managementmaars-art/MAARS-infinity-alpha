import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Bot, ArrowLeft, Plus, X, Sparkles } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const CreateAgent = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [capability, setCapability] = useState("");
  
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

  const modelOptions = {
    openai: [
      { value: "gpt-5.2", label: "GPT-5.2 (Latest)" },
      { value: "gpt-5.1", label: "GPT-5.1" },
      { value: "gpt-4o", label: "GPT-4o" },
      { value: "o3", label: "O3 (Reasoning)" }
    ],
    anthropic: [
      { value: "claude-sonnet-4-5-20250929", label: "Claude Sonnet 4.5" },
      { value: "claude-opus-4-5-20251101", label: "Claude Opus 4.5" },
      { value: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5" }
    ],
    gemini: [
      { value: "gemini-3-flash-preview", label: "Gemini 3 Flash" },
      { value: "gemini-3-pro-preview", label: "Gemini 3 Pro" },
      { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" }
    ]
  };

  const avatarOptions = [
    "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1760931969401-9bd6ee902798?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
    "https://images.pexels.com/photos/8294598/pexels-photo-8294598.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "https://images.unsplash.com/photo-1535378917042-10a22c95931a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9ib3R8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85",
    "https://images.unsplash.com/photo-1546776310-eef45dd6d63c?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8YWklMjBhc3Npc3RhbnR8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=85"
  ];

  const addCapability = () => {
    if (capability.trim() && !formData.capabilities.includes(capability.trim())) {
      setFormData(prev => ({
        ...prev,
        capabilities: [...prev.capabilities, capability.trim()]
      }));
      setCapability("");
    }
  };

  const removeCapability = (cap) => {
    setFormData(prev => ({
      ...prev,
      capabilities: prev.capabilities.filter(c => c !== cap)
    }));
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
    } catch (error) {
      toast.error("Failed to create agent");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background" data-testid="create-agent-page">
      <div className="max-w-3xl mx-auto p-6 lg:p-8">
        {/* Header */}
        <div className="mb-8">
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

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Avatar Selection */}
          <div>
            <Label className="text-zinc-300 mb-3 block">Avatar</Label>
            <div className="flex flex-wrap gap-3">
              {avatarOptions.map((url, i) => (
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
                data-testid="capability-input"
              />
              <Button
                type="button"
                onClick={addCapability}
                variant="outline"
                className="border-white/10 hover:bg-white/5"
                data-testid="add-capability-btn"
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
            {formData.capabilities.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {formData.capabilities.map((cap, i) => (
                  <Badge
                    key={i}
                    variant="secondary"
                    className="bg-indigo-500/20 text-indigo-300 border-0 pr-1"
                  >
                    {cap}
                    <button
                      type="button"
                      onClick={() => removeCapability(cap)}
                      className="ml-2 hover:text-white"
                      data-testid={`remove-cap-${i}`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Submit */}
          <div className="flex gap-4 pt-4">
            <Button
              type="button"
              variant="outline"
              className="flex-1 border-white/10 hover:bg-white/5"
              onClick={() => navigate("/agents")}
              data-testid="cancel-btn"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary"
              disabled={loading}
              data-testid="create-agent-submit-btn"
            >
              {loading ? (
                "Creating..."
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Create Agent
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAgent;
