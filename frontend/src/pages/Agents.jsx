import { useState, useEffect, useRef } from "react";
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
  const [viewMode, setViewMode] = useState("cards"); // "cards" | "gallery"
  const [searchQuery, setSearchQuery] = useState("");
  const [hoveredAgent, setHoveredAgent] = useState(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });
  const hoverRef = useRef(null);

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

  const handleGalleryHover = (agent, e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setHoverPos({ x: rect.right + 12, y: Math.min(rect.top, window.innerHeight - 300) });
    setHoveredAgent(agent);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="agents-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1 font-['Outfit']">AI Agents</h1>
          <p className="text-sm text-blue-300/40">{agents.length} specialized AI team members</p>
        </div>
        <div className="flex items-center gap-2">
          {/* View Toggle */}
          <div className="flex bg-[#0d0d35]/80 rounded-lg border border-blue-500/10 p-0.5" data-testid="view-toggle">
            <button onClick={() => setViewMode("cards")}
              className={`p-2 rounded-md transition-colors ${viewMode === "cards" ? "bg-blue-500/20 text-blue-400" : "text-zinc-500 hover:text-zinc-300"}`}
              data-testid="view-cards">
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button onClick={() => setViewMode("gallery")}
              className={`p-2 rounded-md transition-colors ${viewMode === "gallery" ? "bg-blue-500/20 text-blue-400" : "text-zinc-500 hover:text-zinc-300"}`}
              data-testid="view-gallery">
              <Grid3X3 className="w-4 h-4" />
            </button>
          </div>
          <Button onClick={() => navigate("/agents/create")}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
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
          className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0d0d35]/60 border border-blue-500/10 focus:border-blue-500/30 focus:outline-none text-sm text-white placeholder-zinc-500 transition-colors"
          data-testid="agent-search" />
      </div>

      {viewMode === "gallery" ? (
        /* ===== GALLERY VIEW ===== */
        <div data-testid="gallery-view">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Agent Gallery</span>
            <span className="text-xs text-zinc-500">{defaultAgents.length} agents</span>
          </div>
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-2">
            {defaultAgents.map(agent => (
              <div key={agent.agent_id}
                className={`relative group cursor-pointer rounded-xl overflow-hidden border transition-all duration-200 ${
                  agent.hidden ? "opacity-40 border-zinc-800" : "border-blue-500/10 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/5"
                }`}
                onMouseEnter={e => handleGalleryHover(agent, e)}
                onMouseLeave={() => setHoveredAgent(null)}
                onClick={() => navigate(`/chat/${agent.agent_id}`)}
                data-testid={`gallery-agent-${agent.agent_id}`}>
                <div className="aspect-square relative">
                  <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300" loading="lazy" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#070721] via-transparent to-transparent opacity-60" />
                  {agent.hidden && (
                    <div className="absolute inset-0 bg-[#070721]/60 flex items-center justify-center">
                      <EyeOff className="w-4 h-4 text-zinc-500" />
                    </div>
                  )}
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-1.5">
                  <p className="text-[9px] font-medium text-white truncate leading-tight">{agent.name}</p>
                  <p className="text-[8px] text-blue-300/50 truncate">{agent.role}</p>
                </div>
                {user?.is_admin && (
                  <button onClick={e => { e.stopPropagation(); toggleAgentVisibility(agent.agent_id); }}
                    className="absolute top-1 right-1 p-1 rounded bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
                    data-testid={`toggle-visibility-${agent.agent_id}`}>
                    {agent.hidden ? <Eye className="w-3 h-3 text-zinc-400" /> : <EyeOff className="w-3 h-3 text-zinc-400" />}
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Hover Preview Tooltip */}
          {hoveredAgent && (
            <div ref={hoverRef}
              className="fixed z-50 w-72 rounded-xl bg-[#0d0d35]/95 backdrop-blur-xl border border-blue-500/15 shadow-2xl shadow-blue-500/10 p-4 pointer-events-none animate-fade-in"
              style={{ left: Math.min(hoverPos.x, window.innerWidth - 300), top: hoverPos.y }}
              data-testid="gallery-preview">
              <div className="flex items-center gap-3 mb-3">
                <img src={hoveredAgent.avatar} alt="" className="w-12 h-12 rounded-lg object-cover" />
                <div>
                  <h4 className="text-sm font-semibold text-white">{hoveredAgent.name}</h4>
                  <p className="text-xs text-blue-300/60">{hoveredAgent.role}</p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 mb-3 line-clamp-2">{hoveredAgent.description}</p>
              <div className="flex flex-wrap gap-1 mb-2">
                {hoveredAgent.capabilities?.slice(0, 4).map((cap, i) => (
                  <span key={i} className="px-1.5 py-0.5 text-[10px] rounded bg-blue-500/10 text-blue-300/70">{cap}</span>
                ))}
              </div>
              {hoveredAgent.tools?.length > 0 && (
                <div className="flex items-center gap-1 text-[10px] text-cyan-400/60">
                  <Wrench className="w-3 h-3" />
                  <span>{hoveredAgent.tools.length} tools available</span>
                </div>
              )}
              <div className="mt-2 text-[10px] text-blue-400/40 flex items-center gap-1">
                <MessageSquare className="w-3 h-3" /> Click to start chat
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ===== CARDS VIEW ===== */
        <div data-testid="cards-view">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Specialized Agents</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {defaultAgents.map(agent => (
              <Card key={agent.agent_id}
                className={`bg-[#0d0d35]/50 border-blue-500/8 hover:border-blue-500/20 transition-all group ${agent.hidden ? "opacity-50" : ""}`}
                data-testid={`agent-card-${agent.agent_id}`}>
                <CardContent className="p-0">
                  <div className="aspect-video relative overflow-hidden rounded-t-lg">
                    <img src={agent.avatar} alt={agent.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#070721] via-transparent to-transparent" />
                    <div className="absolute bottom-3 left-3">
                      <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-0">{agent.model_provider}</Badge>
                    </div>
                    {user?.is_admin && (
                      <button onClick={() => toggleAgentVisibility(agent.agent_id)}
                        className="absolute top-2 right-2 p-1.5 rounded-lg bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
                        data-testid={`toggle-card-visibility-${agent.agent_id}`}>
                        {agent.hidden ? <Eye className="w-4 h-4 text-zinc-400" /> : <EyeOff className="w-4 h-4 text-zinc-400" />}
                      </button>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                    <p className="text-sm text-blue-300/50 mb-3">{agent.role}</p>
                    <p className="text-sm text-zinc-500 mb-4 line-clamp-2">{agent.description}</p>
                    <div className="flex flex-wrap gap-1 mb-4">
                      {agent.capabilities?.slice(0, 3).map((cap, i) => (
                        <span key={i} className="px-2 py-0.5 text-xs rounded-full bg-blue-500/8 text-zinc-400">{cap}</span>
                      ))}
                    </div>
                    {agent.tools?.length > 0 && (
                      <div className="flex items-center gap-1.5 mb-3 flex-wrap" data-testid={`agent-tools-${agent.agent_id}`}>
                        <Wrench className="w-3 h-3 text-cyan-400 shrink-0" />
                        <span className="text-[10px] text-cyan-400/80 font-medium">Tools:</span>
                        {agent.tools.slice(0, 6).map((tool, i) => {
                          const toolIcons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Send };
                          const ToolIcon = toolIcons[tool] || Wrench;
                          const toolLabels = { web_search: "Search", calculate: "Math", create_task: "Tasks", analyze_data: "Analyze", send_slack: "Slack", send_email: "Email", send_sms: "SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIFs", schedule_meeting: "Calendly", google_calendar: "Calendar", send_gmail: "Gmail" };
                          return (
                            <span key={i} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/15">
                              <ToolIcon className="w-2.5 h-2.5" />{toolLabels[tool] || tool}
                            </span>
                          );
                        })}
                        {agent.tools.length > 6 && <span className="text-[10px] text-cyan-400/60">+{agent.tools.length - 6}</span>}
                      </div>
                    )}
                    <Button onClick={() => navigate(`/chat/${agent.agent_id}`)}
                      className="w-full bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/15"
                      data-testid={`chat-with-${agent.agent_id}`}>
                      <MessageSquare className="w-4 h-4 mr-2" /> Start Chat
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Custom Agents */}
      {customAgents.length > 0 && (
        <div className="mt-10">
          <div className="mb-4 flex items-center gap-2">
            <Bot className="w-4 h-4 text-fuchsia-400" />
            <span className="text-sm font-medium text-white font-['Outfit']">Your Custom Agents</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customAgents.map(agent => (
              <Card key={agent.agent_id} className="bg-[#0d0d35]/50 border-fuchsia-500/10 hover:border-fuchsia-500/20 transition-all group"
                data-testid={`custom-agent-card-${agent.agent_id}`}>
                <CardContent className="p-0">
                  <div className="aspect-video relative overflow-hidden rounded-t-lg">
                    <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#070721] via-transparent to-transparent" />
                    <div className="absolute bottom-3 left-3">
                      <Badge variant="secondary" className="bg-fuchsia-500/20 text-fuchsia-300 border-0">Custom</Badge>
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                    <p className="text-sm text-blue-300/50 mb-3">{agent.role}</p>
                    <p className="text-sm text-zinc-500 mb-4 line-clamp-2">{agent.description}</p>
                    <div className="flex gap-2">
                      <Button onClick={() => navigate(`/chat/${agent.agent_id}`)}
                        className="flex-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-300"
                        data-testid={`chat-with-custom-${agent.agent_id}`}>
                        <MessageSquare className="w-4 h-4 mr-2" /> Chat
                      </Button>
                      <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10"
                        onClick={() => deleteAgent(agent.agent_id)} data-testid={`delete-agent-${agent.agent_id}`}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {customAgents.length === 0 && (
        <div className="mt-10 p-8 rounded-xl border border-dashed border-blue-500/10 text-center">
          <Bot className="w-12 h-12 text-blue-500/20 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">No Custom Agents Yet</h3>
          <p className="text-zinc-500 mb-4 text-sm">Create your own AI agents tailored to your specific needs.</p>
          <Button onClick={() => navigate("/agents/create")}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700">
            <Plus className="w-4 h-4 mr-2" /> Create Your First Agent
          </Button>
        </div>
      )}
    </div>
  );
};

export default Agents;
