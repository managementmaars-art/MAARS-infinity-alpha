import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Bot, Plus, MessageSquare, Trash2, Sparkles, Search, Eye, EyeOff,
  LayoutGrid, Grid3X3, Wrench, Calculator, ClipboardList, BarChart3,
  Mail, MessageCircle, Phone, Github, Table, Image, Calendar, Send
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const Agents = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState("cards");
  const [searchQuery, setSearchQuery] = useState("");

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => { fetchAgents(); }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API}/agents`, { headers });
      if (response.ok) setAgents(await response.json());
    } catch { toast.error("Failed to load agents"); }
    finally { setLoading(false); }
  };

  const deleteAgent = async (agentId) => {
    try {
      const response = await fetch(`${API}/agents/${agentId}`, { method: "DELETE", headers });
      if (response.ok) { setAgents(prev => prev.filter(a => a.agent_id !== agentId)); toast.success("Agent deleted"); }
      else { const data = await response.json(); toast.error(data.detail || "Failed to delete agent"); }
    } catch { toast.error("Failed to delete agent"); }
  };

  const toggleAgentVisibility = async (agentId) => {
    try {
      const agent = agents.find(a => a.agent_id === agentId);
      const newHidden = !agent.hidden;
      const response = await fetch(`${API}/agents/${agentId}/visibility`, {
        method: "PUT", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ hidden: newHidden })
      });
      if (response.ok) {
        setAgents(prev => prev.map(a => a.agent_id === agentId ? { ...a, hidden: newHidden } : a));
        toast.success(newHidden ? "Agent hidden" : "Agent visible");
      }
    } catch { toast.error("Failed to update visibility"); }
  };

  const filtered = agents.filter(a => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return a.name?.toLowerCase().includes(q) || a.role?.toLowerCase().includes(q) ||
           a.capabilities?.some(c => c.toLowerCase().includes(q));
  });

  const defaultAgents = filtered.filter(a => !a.is_custom);
  const customAgents = filtered.filter(a => a.is_custom);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="agents-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1 font-['Outfit']">AI Agents</h1>
          <p className="text-sm text-zinc-500">{agents.length} specialized AI team members</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-zinc-900/80 rounded-lg border border-white/[0.06] p-0.5" data-testid="view-toggle">
            <button onClick={() => setViewMode("cards")}
              className={`p-2 rounded-md transition-colors ${viewMode === "cards" ? "bg-indigo-500/20 text-indigo-400" : "text-zinc-500 hover:text-zinc-300"}`}
              data-testid="view-cards">
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button onClick={() => setViewMode("gallery")}
              className={`p-2 rounded-md transition-colors ${viewMode === "gallery" ? "bg-indigo-500/20 text-indigo-400" : "text-zinc-500 hover:text-zinc-300"}`}
              data-testid="view-gallery">
              <Grid3X3 className="w-4 h-4" />
            </button>
          </div>
          <Button onClick={() => navigate("/agents/create")}
            className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
            data-testid="create-agent-btn">
            <Plus className="w-4 h-4 mr-2" /> Create Agent
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
          placeholder="Search agents by name, role, or capability..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/[0.06] focus:border-indigo-500/30 focus:outline-none text-sm text-white placeholder-zinc-500 transition-colors"
          data-testid="agent-search" />
      </div>

      {viewMode === "gallery" ? (
        /* ===== GALLERY VIEW — same hover-expand as dashboard ===== */
        <div data-testid="gallery-view">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Agent Gallery</span>
            <span className="text-xs text-zinc-500">{defaultAgents.length} agents</span>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-3">
            {defaultAgents.map(agent => (
              <div key={agent.agent_id} className="relative group" data-testid={`gallery-agent-${agent.agent_id}`}>
                <Card className={`bg-zinc-900/50 border-white/[0.06] hover:border-indigo-500/20 cursor-pointer transition-all ${agent.hidden ? "opacity-40" : ""}`}
                  onClick={() => navigate(`/chat/${agent.agent_id}`)}>
                  <CardContent className="p-2">
                    <div className="aspect-square rounded-lg overflow-hidden mb-2">
                      <img src={agent.avatar} alt={agent.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300" loading="lazy" />
                    </div>
                    <p className="text-xs font-semibold text-white truncate">{agent.name}</p>
                    <p className="text-[10px] text-zinc-500 truncate">{agent.role}</p>
                  </CardContent>
                </Card>

                {/* Hover Expand Popup — same style as dashboard */}
                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-60 rounded-xl overflow-hidden border border-indigo-500/20 shadow-[0_8px_40px_rgba(99,102,241,0.15)] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300 z-50 bg-zinc-900"
                  onClick={() => navigate(`/chat/${agent.agent_id}`)}>
                  <div className="relative aspect-square">
                    <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/40 to-transparent" />
                    <span className="absolute top-2 right-2 px-2 py-0.5 text-[9px] font-bold rounded-full bg-indigo-500 text-white uppercase tracking-wider">
                      {agent.model_provider || "AI"}
                    </span>
                    <div className="absolute bottom-0 left-0 right-0 p-3">
                      <p className="text-indigo-400 text-[10px] font-medium">{agent.role}</p>
                      <h3 className="font-bold text-white text-sm leading-tight">{agent.name}</h3>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {(agent.capabilities || []).slice(0, 3).map((cap, i) => (
                          <span key={i} className="px-1.5 py-0.5 text-[8px] rounded-full bg-indigo-500/15 text-indigo-200/70">{cap}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border-t border-white/[0.06]">
                    <p className="text-[11px] text-zinc-400 leading-relaxed line-clamp-3">{agent.description}</p>
                    {agent.tools?.length > 0 && (
                      <div className="flex items-center gap-1 mt-2 text-[10px] text-violet-400/70">
                        <Wrench className="w-3 h-3" /> {agent.tools.length} tools
                      </div>
                    )}
                  </div>
                </div>

                {user?.is_admin && (
                  <button onClick={e => { e.stopPropagation(); toggleAgentVisibility(agent.agent_id); }}
                    className="absolute top-3 right-3 p-1 rounded bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity z-40"
                    data-testid={`toggle-visibility-${agent.agent_id}`}>
                    {agent.hidden ? <Eye className="w-3 h-3 text-zinc-400" /> : <EyeOff className="w-3 h-3 text-zinc-400" />}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* ===== CARDS VIEW — with hover-expand popup ===== */
        <div data-testid="cards-view">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Specialized Agents</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {defaultAgents.map(agent => (
              <div key={agent.agent_id} className="relative group" data-testid={`agent-card-${agent.agent_id}`}>
                <Card className={`bg-zinc-900/50 border-white/[0.06] hover:border-indigo-500/20 cursor-pointer transition-all ${agent.hidden ? "opacity-40" : ""}`}
                  onClick={() => navigate(`/chat/${agent.agent_id}`)}>
                  <CardContent className="p-3">
                    <div className="flex items-center gap-3">
                      <img src={agent.avatar} alt={agent.name} className="w-10 h-10 rounded-lg object-cover shrink-0" />
                      <div className="min-w-0">
                        <h3 className="font-semibold text-sm text-white truncate">{agent.name}</h3>
                        <p className="text-xs text-zinc-500 truncate">{agent.role}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Hover Expand Popup */}
                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-56 rounded-xl overflow-hidden border border-indigo-500/20 shadow-[0_8px_40px_rgba(99,102,241,0.15)] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300 z-50 bg-zinc-900"
                  onClick={() => navigate(`/chat/${agent.agent_id}`)}>
                  <div className="relative aspect-square">
                    <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/40 to-transparent" />
                    <span className="absolute top-2 right-2 px-2 py-0.5 text-[9px] font-bold rounded-full bg-indigo-500 text-white uppercase tracking-wider">
                      {agent.model_provider || "AI"}
                    </span>
                    <div className="absolute bottom-0 left-0 right-0 p-3">
                      <p className="text-indigo-400 text-[10px] font-medium">{agent.role}</p>
                      <h3 className="font-bold text-white text-sm leading-tight">{agent.name}</h3>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {(agent.capabilities || []).slice(0, 3).map((cap, i) => (
                          <span key={i} className="px-1.5 py-0.5 text-[8px] rounded-full bg-indigo-500/15 text-indigo-200/70">{cap}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border-t border-white/[0.06]">
                    <p className="text-[11px] text-zinc-400 leading-relaxed line-clamp-3">{agent.description}</p>
                  </div>
                </div>

                {user?.is_admin && (
                  <button onClick={e => { e.stopPropagation(); toggleAgentVisibility(agent.agent_id); }}
                    className="absolute top-3 right-3 p-1 rounded bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity z-40"
                    data-testid={`toggle-card-visibility-${agent.agent_id}`}>
                    {agent.hidden ? <Eye className="w-3 h-3 text-zinc-400" /> : <EyeOff className="w-3 h-3 text-zinc-400" />}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Custom Agents */}
      {customAgents.length > 0 && (
        <div className="mt-10">
          <div className="mb-4 flex items-center gap-2">
            <Bot className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Your Custom Agents</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customAgents.map(agent => (
              <Card key={agent.agent_id} className="bg-zinc-900/50 border-violet-500/10 hover:border-violet-500/20 transition-all group"
                data-testid={`custom-agent-card-${agent.agent_id}`}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <img src={agent.avatar} alt={agent.name} className="w-10 h-10 rounded-lg object-cover" />
                    <div className="min-w-0">
                      <h3 className="font-semibold text-white truncate">{agent.name}</h3>
                      <p className="text-xs text-zinc-500 truncate">{agent.role}</p>
                    </div>
                  </div>
                  <p className="text-sm text-zinc-500 mb-4 line-clamp-2">{agent.description}</p>
                  <div className="flex gap-2">
                    <Button onClick={() => navigate(`/chat/${agent.agent_id}`)}
                      className="flex-1 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/10">
                      <MessageSquare className="w-4 h-4 mr-2" /> Chat
                    </Button>
                    <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10"
                      onClick={() => deleteAgent(agent.agent_id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty Create Agent */}
      {customAgents.length === 0 && (
        <div className="mt-10 p-8 rounded-xl border border-dashed border-white/[0.06] text-center">
          <Bot className="w-12 h-12 text-indigo-500/20 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">No Custom Agents Yet</h3>
          <p className="text-zinc-500 mb-4 text-sm">Create your own AI agents tailored to your specific needs.</p>
          <Button onClick={() => navigate("/agents/create")}
            className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600">
            <Plus className="w-4 h-4 mr-2" /> Create Your First Agent
          </Button>
        </div>
      )}
    </div>
  );
};

export default Agents;
