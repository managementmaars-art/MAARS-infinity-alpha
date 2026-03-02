import { useState } from "react";
import { Card, CardContent } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { Textarea } from "../../ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../ui/dialog";
import {
  Bot, Plus, X, Trash2, ChevronDown, ChevronUp, CheckCircle, XCircle, Loader2,
  Image, Film, FileText, File, Brain, ToggleLeft, ToggleRight, Thermometer, Hash
} from "lucide-react";
import { useAuth, API } from "../../../App";
import { toast } from "sonner";

export const AgentsTab = ({ agents, setAgents, showCreateAgent, setShowCreateAgent, newAgent, setNewAgent, handleCreateAgent, handleDeleteAgent, token }) => {
  const [savingAgent, setSavingAgent] = useState(null);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [brainEdit, setBrainEdit] = useState(null);
  const [savingBrain, setSavingBrain] = useState(false);

  const openBrainEditor = (agent) => {
    setBrainEdit({
      agent_id: agent.agent_id,
      name: agent.name || "",
      role: agent.role || "",
      description: agent.description || "",
      personality_tone: agent.personality_tone || "",
      expertise_areas: agent.expertise_areas || "",
      dos: agent.dos || "",
      donts: agent.donts || "",
      knowledge_base: agent.knowledge_base || "",
      model_provider: agent.model_provider || "openai",
      model_name: agent.model_name || "gpt-5.2",
      temperature: agent.temperature ?? 0.7,
      max_tokens: agent.max_tokens ?? 4096
    });
  };

  const saveBrain = async () => {
    if (!brainEdit) return;
    setSavingBrain(true);
    try {
      const res = await fetch(`${API}/admin/agents/${brainEdit.agent_id}/brain`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(brainEdit)
      });
      if (res.ok) {
        const data = await res.json();
        setAgents(prev => prev.map(a => a.agent_id === brainEdit.agent_id ? { ...a, ...data.agent } : a));
        toast.success("Brain updated!");
        setBrainEdit(null);
      } else {
        let errMsg = `Save failed (HTTP ${res.status})`;
        try { const err = await res.json(); errMsg = err.detail || errMsg; } catch {}
        toast.error(errMsg);
        console.error("Brain save failed:", res.status, errMsg);
      }
    } catch (e) {
      console.error("Brain save error:", e);
      toast.error(`Connection error. Please refresh and try again.`);
    } finally { setSavingBrain(false); }
  };

  const handleToggleCapability = async (agentId, field, currentValue) => {
    setSavingAgent(agentId);
    try {
      const res = await fetch(`${API}/admin/agents/${agentId}/settings`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ [field]: !currentValue })
      });
      if (res.ok) {
        setAgents(prev => prev.map(a => a.agent_id === agentId ? { ...a, [field]: !currentValue } : a));
        const label = field === "is_active" ? "active status" : field.replace('can_generate_', '') + " generation";
        toast.success(`${!currentValue ? "Enabled" : "Disabled"} ${label}`);
      } else {
        let errMsg = `Toggle failed (HTTP ${res.status})`;
        try { const err = await res.json(); errMsg = err.detail || errMsg; } catch {}
        toast.error(errMsg);
        console.error("Toggle failed:", res.status, errMsg);
      }
    } catch (e) {
      console.error("Toggle error:", e);
      toast.error(`Connection error. Please refresh and try again.`);
    } finally {
      setSavingAgent(null);
    }
  };

  const CapabilityToggle = ({ agentId, field, label, icon: Icon, enabled }) => (
    <button
      onClick={() => handleToggleCapability(agentId, field, enabled)}
      disabled={savingAgent === agentId}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
        enabled
          ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/25"
          : "bg-zinc-800/50 text-zinc-500 border-zinc-700/50 hover:bg-zinc-700/50 hover:text-zinc-300"
      }`}
      data-testid={`toggle-${field}-${agentId}`}
    >
      {savingAgent === agentId ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Icon className="w-3.5 h-3.5" />}
      {label}
      {enabled ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
    </button>
  );

  const AgentsTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">All Agents ({agents.length})</h2>
        <Button
          onClick={() => setShowCreateAgent(!showCreateAgent)}
          className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
          data-testid="admin-create-agent-btn"
        >
          {showCreateAgent ? <X className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
          {showCreateAgent ? "Cancel" : "Create Agent"}
        </Button>
      </div>

      {showCreateAgent && (
        <Card className="bg-zinc-900/50 border-red-500/20">
          <CardContent className="p-6 space-y-4">
            <h3 className="text-white font-semibold font-['Outfit']">Create New Agent</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-zinc-300">Name</Label>
                <Input value={newAgent.name} onChange={(e) => setNewAgent(p => ({...p, name: e.target.value}))} placeholder="Agent Name" className="bg-zinc-800/50 border-white/10" data-testid="admin-agent-name-input" />
              </div>
              <div className="space-y-2">
                <Label className="text-zinc-300">Role</Label>
                <Input value={newAgent.role} onChange={(e) => setNewAgent(p => ({...p, role: e.target.value}))} placeholder="e.g. Data Scientist" className="bg-zinc-800/50 border-white/10" data-testid="admin-agent-role-input" />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">Description</Label>
              <Input value={newAgent.description} onChange={(e) => setNewAgent(p => ({...p, description: e.target.value}))} placeholder="Brief description of the agent" className="bg-zinc-800/50 border-white/10" data-testid="admin-agent-desc-input" />
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">System Prompt</Label>
              <Textarea value={newAgent.system_prompt} onChange={(e) => setNewAgent(p => ({...p, system_prompt: e.target.value}))} placeholder="You are... (define the agent's personality and instructions)" className="bg-zinc-800/50 border-white/10 min-h-[100px]" data-testid="admin-agent-prompt-input" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-zinc-300">Model Provider</Label>
                <select value={newAgent.model_provider} onChange={(e) => setNewAgent(p => ({...p, model_provider: e.target.value}))} className="w-full h-10 px-3 rounded-md bg-zinc-800/50 border border-white/10 text-white" data-testid="admin-agent-provider-select">
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="xai">xAI (Grok)</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="mistral">Mistral AI</option>
                  <option value="perplexity">Perplexity</option>
                  <option value="cohere">Cohere</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label className="text-zinc-300">Model Name</Label>
                <Input value={newAgent.model_name} onChange={(e) => setNewAgent(p => ({...p, model_name: e.target.value}))} placeholder="gpt-5.2" className="bg-zinc-800/50 border-white/10" data-testid="admin-agent-model-input" />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">Capabilities (comma-separated)</Label>
              <Input value={newAgent.capabilities} onChange={(e) => setNewAgent(p => ({...p, capabilities: e.target.value}))} placeholder="Skill 1, Skill 2, Skill 3" className="bg-zinc-800/50 border-white/10" data-testid="admin-agent-capabilities-input" />
            </div>
            <Button onClick={handleCreateAgent} className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600" data-testid="admin-save-agent-btn">
              Create Agent
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {agents.map((agent) => (
          <Card key={agent.agent_id} className="bg-zinc-900/50 border-white/10 overflow-hidden" data-testid={`admin-agent-${agent.agent_id}`}>
            <CardContent className="p-0">
              <div
                className="flex items-center gap-4 p-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
                onClick={() => setExpandedAgent(expandedAgent === agent.agent_id ? null : agent.agent_id)}
                data-testid={`agent-row-${agent.agent_id}`}
              >
                <img src={agent.avatar} alt={agent.name} className="w-12 h-12 rounded-lg object-cover shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white truncate">{agent.name}</p>
                    {agent.is_commander && <Badge className="bg-amber-500/20 text-amber-400 text-[10px]">Commander</Badge>}
                    {agent.is_custom && <Badge className="bg-cyan-500/20 text-cyan-400 text-[10px]">Custom</Badge>}
                    {agent.is_active === false && <Badge className="bg-red-500/20 text-red-400 text-[10px]">Disabled</Badge>}
                  </div>
                  <p className="text-sm text-zinc-400 truncate">{agent.role}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleToggleCapability(agent.agent_id, "is_active", agent.is_active !== false); }}
                    className={`p-1 rounded transition-colors ${agent.is_active !== false ? 'text-emerald-400 hover:text-emerald-300' : 'text-zinc-600 hover:text-zinc-400'}`}
                    title={agent.is_active !== false ? "Active — click to disable" : "Disabled — click to enable"}
                    data-testid={`toggle-active-${agent.agent_id}`}
                  >
                    {agent.is_active !== false ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
                  </button>
                  <div className="hidden sm:flex items-center gap-1">
                    <button onClick={(e) => { e.stopPropagation(); handleToggleCapability(agent.agent_id, "can_generate_image", !!agent.can_generate_image); }} title="Toggle image generation" data-testid={`header-toggle-img-${agent.agent_id}`}
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border transition-all cursor-pointer ${agent.can_generate_image ? 'bg-blue-500/15 text-blue-400 border-blue-500/20 hover:bg-blue-500/30' : 'bg-zinc-800/50 text-zinc-600 border-zinc-700/30 hover:bg-zinc-700/50 line-through'}`}>IMG</button>
                    <button onClick={(e) => { e.stopPropagation(); handleToggleCapability(agent.agent_id, "can_generate_pdf", !!agent.can_generate_pdf); }} title="Toggle PDF generation" data-testid={`header-toggle-pdf-${agent.agent_id}`}
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border transition-all cursor-pointer ${agent.can_generate_pdf ? 'bg-orange-500/15 text-orange-400 border-orange-500/20 hover:bg-orange-500/30' : 'bg-zinc-800/50 text-zinc-600 border-zinc-700/30 hover:bg-zinc-700/50 line-through'}`}>PDF</button>
                    <button onClick={(e) => { e.stopPropagation(); handleToggleCapability(agent.agent_id, "can_generate_files", !!agent.can_generate_files); }} title="Toggle file generation" data-testid={`header-toggle-files-${agent.agent_id}`}
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border transition-all cursor-pointer ${agent.can_generate_files ? 'bg-green-500/15 text-green-400 border-green-500/20 hover:bg-green-500/30' : 'bg-zinc-800/50 text-zinc-600 border-zinc-700/30 hover:bg-zinc-700/50 line-through'}`}>FILES</button>
                  </div>
                  {expandedAgent === agent.agent_id ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
                </div>
              </div>

              {expandedAgent === agent.agent_id && (
                <div className="border-t border-white/5 px-4 py-4 bg-zinc-950/30 space-y-4" data-testid={`agent-expanded-${agent.agent_id}`}>
                  <div>
                    <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2 font-medium">Generation Permissions</p>
                    <div className="flex flex-wrap gap-2">
                      <CapabilityToggle agentId={agent.agent_id} field="can_generate_image" label="Images" icon={Image} enabled={!!agent.can_generate_image} />
                      <CapabilityToggle agentId={agent.agent_id} field="can_generate_video" label="Videos" icon={Film} enabled={!!agent.can_generate_video} />
                      <CapabilityToggle agentId={agent.agent_id} field="can_generate_pdf" label="PDF" icon={FileText} enabled={!!agent.can_generate_pdf} />
                      <CapabilityToggle agentId={agent.agent_id} field="can_generate_files" label="Files" icon={File} enabled={!!agent.can_generate_files} />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-zinc-500">
                    <span>{agent.model_provider}/{agent.model_name}</span>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 h-7 text-xs"
                        onClick={(e) => { e.stopPropagation(); openBrainEditor(agent); }}
                        data-testid={`admin-edit-brain-${agent.agent_id}`}
                      >
                        <Brain className="w-3.5 h-3.5 mr-1" /> Edit Brain
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10 h-7 text-xs"
                        onClick={(e) => { e.stopPropagation(); handleDeleteAgent(agent.agent_id, agent.name); }}
                        data-testid={`admin-delete-agent-${agent.agent_id}`}
                      >
                        <Trash2 className="w-3.5 h-3.5 mr-1" /> Delete
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
        {agents.length === 0 && <p className="text-zinc-500 text-center py-8">No agents found</p>}
      </div>

      {/* Brain Editor Modal */}
      {brainEdit && (
        <Dialog open={!!brainEdit} onOpenChange={() => setBrainEdit(null)}>
          <DialogContent className="bg-zinc-900 border-white/10 max-w-2xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white font-['Outfit'] flex items-center gap-2"><Brain className="w-5 h-5 text-indigo-400" />Brain Editor — {brainEdit.name}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-2">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Name</Label>
                  <Input value={brainEdit.name} onChange={e => setBrainEdit(p => ({...p, name: e.target.value}))} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid="brain-name" />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Role</Label>
                  <Input value={brainEdit.role} onChange={e => setBrainEdit(p => ({...p, role: e.target.value}))} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid="brain-role" />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label className="text-zinc-400 text-xs">Description</Label>
                <Input value={brainEdit.description} onChange={e => setBrainEdit(p => ({...p, description: e.target.value}))} placeholder="What this agent does in one line" className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid="brain-description" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-zinc-400 text-xs">Personality & Tone</Label>
                <Textarea value={brainEdit.personality_tone} onChange={e => setBrainEdit(p => ({...p, personality_tone: e.target.value}))} placeholder="e.g. Professional but approachable. Uses data to back up claims. Avoids jargon unless explaining it." className="bg-zinc-800/50 border-white/10 text-sm min-h-[60px]" data-testid="brain-tone" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-zinc-400 text-xs">Expertise Areas</Label>
                <Textarea value={brainEdit.expertise_areas} onChange={e => setBrainEdit(p => ({...p, expertise_areas: e.target.value}))} placeholder="e.g. Digital marketing, brand strategy, social media campaigns, content marketing, analytics" className="bg-zinc-800/50 border-white/10 text-sm min-h-[60px]" data-testid="brain-expertise" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Always Do (Do's)</Label>
                  <Textarea value={brainEdit.dos} onChange={e => setBrainEdit(p => ({...p, dos: e.target.value}))} placeholder="e.g. Back up suggestions with data. Provide actionable steps. Consider ROI." className="bg-zinc-800/50 border-white/10 text-sm min-h-[80px]" data-testid="brain-dos" />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Never Do (Don'ts)</Label>
                  <Textarea value={brainEdit.donts} onChange={e => setBrainEdit(p => ({...p, donts: e.target.value}))} placeholder="e.g. Don't promise guaranteed results. Don't suggest unethical practices. Don't ignore budget constraints." className="bg-zinc-800/50 border-white/10 text-sm min-h-[80px]" data-testid="brain-donts" />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label className="text-zinc-400 text-xs">Knowledge Base (Optional)</Label>
                <Textarea value={brainEdit.knowledge_base} onChange={e => setBrainEdit(p => ({...p, knowledge_base: e.target.value}))} placeholder="Paste any specific knowledge, company info, brand guidelines, or reference material this agent should always have access to." className="bg-zinc-800/50 border-white/10 text-sm min-h-[80px]" data-testid="brain-knowledge" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Model Provider</Label>
                  <select value={brainEdit.model_provider} onChange={e => setBrainEdit(p => ({...p, model_provider: e.target.value}))} className="w-full h-9 px-3 rounded-md bg-zinc-800/50 border border-white/10 text-white text-sm" data-testid="brain-provider">
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="xai">xAI (Grok)</option>
                    <option value="deepseek">DeepSeek</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs">Model Name</Label>
                  <Input value={brainEdit.model_name} onChange={e => setBrainEdit(p => ({...p, model_name: e.target.value}))} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid="brain-model" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs flex items-center gap-1.5">
                    <Thermometer className="w-3 h-3" /> Temperature: {brainEdit.temperature?.toFixed(1) ?? "0.7"}
                  </Label>
                  <input
                    type="range" min="0" max="2" step="0.1"
                    value={brainEdit.temperature ?? 0.7}
                    onChange={e => setBrainEdit(p => ({...p, temperature: parseFloat(e.target.value)}))}
                    className="w-full h-2 rounded-full appearance-none bg-zinc-700 accent-indigo-500"
                    data-testid="brain-temperature"
                  />
                  <div className="flex justify-between text-[10px] text-zinc-600">
                    <span>Precise</span>
                    <span>Balanced</span>
                    <span>Creative</span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-zinc-400 text-xs flex items-center gap-1.5">
                    <Hash className="w-3 h-3" /> Max Tokens: {brainEdit.max_tokens ?? 4096}
                  </Label>
                  <input
                    type="range" min="256" max="16384" step="256"
                    value={brainEdit.max_tokens ?? 4096}
                    onChange={e => setBrainEdit(p => ({...p, max_tokens: parseInt(e.target.value)}))}
                    className="w-full h-2 rounded-full appearance-none bg-zinc-700 accent-indigo-500"
                    data-testid="brain-max-tokens"
                  />
                  <div className="flex justify-between text-[10px] text-zinc-600">
                    <span>256</span>
                    <span>8192</span>
                    <span>16384</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <Button onClick={saveBrain} disabled={savingBrain} className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="save-brain-btn">
                  {savingBrain ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Brain className="w-4 h-4 mr-2" />}Save Brain
                </Button>
                <Button variant="ghost" onClick={() => setBrainEdit(null)} className="text-zinc-400">Cancel</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};
