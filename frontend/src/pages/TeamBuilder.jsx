import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Users, Plus, Search, X, Trash2, Edit3, Check, Bot, Network,
  ChevronRight, Save, Loader2
} from "lucide-react";
import { toast } from "sonner";

const NETWORK_LABELS = {
  strategic_executive: "Strategic & Executive", product_development: "Product Development",
  engineering: "Engineering", creative_brand: "Creative & Brand",
  growth_distribution: "Growth & Distribution", sales_revenue: "Sales & Revenue",
  operations: "Operations", finance_capital: "Finance & Capital",
  legal_governance: "Legal & Governance", research_intelligence: "Research & Intelligence",
  customer_experience: "Customer Experience", security: "Security",
  core_platform: "Core Platform", memory_knowledge: "Memory & Knowledge",
  tooling_capability: "Tooling & Capability", observability_incident: "Observability & Incident",
  verification: "Verification", execution: "Execution",
  simulation_foresight: "Simulation & Foresight", experimentation: "Experimentation",
  communication_reporting: "Communication & Reporting", conflict_resolution: "Conflict Resolution",
  recovery_resilience: "Recovery & Resilience", investment_portfolio: "Investment & Portfolio",
  venture_creation: "Venture Creation", web_search_intelligence: "Web Search Intelligence",
  industry_specific: "Industry Specific",
};

export default function TeamBuilder() {
  const { token } = useAuth();
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const [agents, setAgents] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [networkFilter, setNetworkFilter] = useState("");
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);

  /* form state */
  const [teamName, setTeamName] = useState("");
  const [teamPurpose, setTeamPurpose] = useState("");
  const [teamDesc, setTeamDesc] = useState("");
  const [selectedIds, setSelectedIds] = useState(new Set());

  const fetchData = useCallback(async () => {
    try {
      const [agentsRes, teamsRes] = await Promise.all([
        fetch(`${API}/agents`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/agent-teams`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (teamsRes.ok) setTeams(await teamsRes.json());
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const resetForm = () => {
    setTeamName(""); setTeamPurpose(""); setTeamDesc("");
    setSelectedIds(new Set()); setCreating(false); setEditingId(null);
  };

  const handleSave = async () => {
    if (!teamName.trim()) return toast.error("Team name is required");
    if (selectedIds.size === 0) return toast.error("Select at least one agent");
    setSaving(true);
    try {
      const body = { name: teamName, purpose: teamPurpose, description: teamDesc, agent_ids: [...selectedIds] };
      const url = editingId ? `${API}/agent-teams/${editingId}` : `${API}/agent-teams`;
      const method = editingId ? "PUT" : "POST";
      const res = await fetch(url, { method, headers, body: JSON.stringify(body) });
      if (res.ok) {
        toast.success(editingId ? "Team updated" : "Team created");
        resetForm();
        fetchData();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to save team");
      }
    } catch { toast.error("Network error"); }
    finally { setSaving(false); }
  };

  const handleEdit = (team) => {
    setEditingId(team.team_id);
    setTeamName(team.name);
    setTeamPurpose(team.purpose || "");
    setTeamDesc(team.description || "");
    setSelectedIds(new Set(team.agent_ids || []));
    setCreating(true);
  };

  const handleDelete = async (teamId) => {
    try {
      const res = await fetch(`${API}/agent-teams/${teamId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Team deleted"); fetchData(); }
    } catch { toast.error("Failed to delete"); }
  };

  const toggleAgent = (agentId) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(agentId) ? next.delete(agentId) : next.add(agentId);
      return next;
    });
  };

  /* filter agents */
  const filteredAgents = agents.filter(a => {
    const q = search.toLowerCase();
    const matchesSearch = !q || a.name?.toLowerCase().includes(q) || a.role?.toLowerCase().includes(q) || a.capabilities?.some(c => c.toLowerCase().includes(q));
    const matchesNetwork = !networkFilter || (a.network || "") === networkFilter;
    return matchesSearch && matchesNetwork;
  });

  const networks = [...new Set(agents.map(a => a.network).filter(Boolean))].sort();

  const getAgentById = (id) => agents.find(a => a.agent_id === id);

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 animate-spin text-indigo-400" /></div>;

  return (
    <div className="space-y-6" data-testid="team-builder-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Agent Team Builder</h1>
          <p className="text-sm text-zinc-400">Assemble custom teams from {agents.length}+ agents for targeted projects</p>
        </div>
        {!creating && (
          <Button onClick={() => setCreating(true)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="create-team-btn">
            <Plus className="w-4 h-4 mr-2" /> New Team
          </Button>
        )}
      </div>

      {/* Create / Edit Form */}
      {creating && (
        <Card className="bg-zinc-900/50 border-indigo-500/20" data-testid="team-form">
          <CardContent className="p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white">{editingId ? "Edit Team" : "Create New Team"}</h2>
              <Button variant="ghost" size="sm" onClick={resetForm}><X className="w-4 h-4" /></Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Input placeholder="Team name *" value={teamName} onChange={e => setTeamName(e.target.value)} className="bg-zinc-800 border-white/10" data-testid="team-name-input" />
              <Input placeholder="Purpose (e.g. Q1 Marketing)" value={teamPurpose} onChange={e => setTeamPurpose(e.target.value)} className="bg-zinc-800 border-white/10" data-testid="team-purpose-input" />
              <Input placeholder="Description" value={teamDesc} onChange={e => setTeamDesc(e.target.value)} className="bg-zinc-800 border-white/10" data-testid="team-desc-input" />
            </div>

            {/* Agent Selection */}
            <div className="flex items-center gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <Input placeholder="Search agents..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9 bg-zinc-800 border-white/10" data-testid="agent-search-input" />
              </div>
              <select value={networkFilter} onChange={e => setNetworkFilter(e.target.value)} className="bg-zinc-800 border border-white/10 rounded-md px-3 py-2 text-sm text-zinc-300" data-testid="network-filter">
                <option value="">All Networks</option>
                {networks.map(n => <option key={n} value={n}>{NETWORK_LABELS[n] || n}</option>)}
              </select>
              <Badge className="bg-indigo-500/20 text-indigo-400 border-0">{selectedIds.size} selected</Badge>
            </div>

            {/* Agent Grid */}
            <div className="max-h-64 overflow-y-auto border border-white/5 rounded-lg p-2 space-y-1" data-testid="agent-selection-grid">
              {filteredAgents.map(agent => {
                const isSelected = selectedIds.has(agent.agent_id);
                return (
                  <button key={agent.agent_id} onClick={() => toggleAgent(agent.agent_id)}
                    className={`w-full flex items-center gap-3 p-2 rounded-lg text-left transition-all ${isSelected ? "bg-indigo-500/15 border border-indigo-500/30" : "hover:bg-white/5 border border-transparent"}`}
                    data-testid={`agent-select-${agent.agent_id}`}>
                    {agent.avatar && !agent.avatar.startsWith("data:") ? (
                      <img src={agent.avatar.startsWith("/") ? `${API.replace("/api", "")}${agent.avatar}` : agent.avatar} alt="" className="w-7 h-7 rounded-md object-cover" loading="lazy" />
                    ) : (
                      <div className="w-7 h-7 rounded-md bg-zinc-700 flex items-center justify-center"><Bot className="w-3.5 h-3.5 text-zinc-400" /></div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{agent.name}</p>
                      <p className="text-[10px] text-zinc-500 truncate">{agent.role} {agent.network ? `| ${NETWORK_LABELS[agent.network] || agent.network}` : ""}</p>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-indigo-400 shrink-0" />}
                  </button>
                );
              })}
              {filteredAgents.length === 0 && <p className="text-xs text-zinc-500 text-center py-4">No agents match your search</p>}
            </div>

            {/* Selected preview */}
            {selectedIds.size > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {[...selectedIds].slice(0, 12).map(id => {
                  const a = getAgentById(id);
                  return a ? (
                    <Badge key={id} className="bg-indigo-500/15 text-indigo-300 border border-indigo-500/20 text-[10px] gap-1">
                      {a.name}
                      <X className="w-3 h-3 cursor-pointer hover:text-white" onClick={() => toggleAgent(id)} />
                    </Badge>
                  ) : null;
                })}
                {selectedIds.size > 12 && <Badge className="bg-zinc-700 text-zinc-400 border-0 text-[10px]">+{selectedIds.size - 12} more</Badge>}
              </div>
            )}

            <Button onClick={handleSave} disabled={saving} className="bg-indigo-600 hover:bg-indigo-700 w-full" data-testid="save-team-btn">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
              {editingId ? "Update Team" : "Create Team"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Teams List */}
      {teams.length === 0 && !creating ? (
        <Card className="bg-zinc-900/50 border-white/5">
          <CardContent className="p-10 text-center">
            <Users className="w-10 h-10 text-zinc-600 mx-auto mb-3" />
            <p className="text-sm text-zinc-400">No agent teams yet. Create your first team to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="teams-grid">
          {teams.map(team => {
            const teamAgents = (team.agent_ids || []).map(id => getAgentById(id)).filter(Boolean);
            const networkCounts = {};
            teamAgents.forEach(a => { const n = a.network || "core"; networkCounts[n] = (networkCounts[n] || 0) + 1; });
            return (
              <Card key={team.team_id} className="bg-zinc-900/50 border-white/5 hover:border-indigo-500/20 transition-all" data-testid={`team-card-${team.team_id}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-sm font-bold text-white">{team.name}</h3>
                      {team.purpose && <p className="text-[10px] text-indigo-400">{team.purpose}</p>}
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => handleEdit(team)} data-testid={`edit-team-${team.team_id}`}>
                        <Edit3 className="w-3.5 h-3.5 text-zinc-400" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => handleDelete(team.team_id)} data-testid={`delete-team-${team.team_id}`}>
                        <Trash2 className="w-3.5 h-3.5 text-red-400" />
                      </Button>
                    </div>
                  </div>
                  {team.description && <p className="text-[10px] text-zinc-500 mb-2">{team.description}</p>}
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className="bg-indigo-500/20 text-indigo-400 border-0 text-[10px]">
                      <Users className="w-3 h-3 mr-1" />{teamAgents.length} agents
                    </Badge>
                    <Badge className="bg-violet-500/20 text-violet-400 border-0 text-[10px]">
                      <Network className="w-3 h-3 mr-1" />{Object.keys(networkCounts).length} networks
                    </Badge>
                  </div>
                  {/* Agent avatar row */}
                  <div className="flex -space-x-2">
                    {teamAgents.slice(0, 8).map(a => (
                      a.avatar && !a.avatar.startsWith("data:") ? (
                        <img key={a.agent_id} src={a.avatar.startsWith("/") ? `${API.replace("/api", "")}${a.avatar}` : a.avatar} alt="" className="w-7 h-7 rounded-full border-2 border-zinc-900 object-cover" title={a.name} loading="lazy" />
                      ) : (
                        <div key={a.agent_id} className="w-7 h-7 rounded-full border-2 border-zinc-900 bg-zinc-700 flex items-center justify-center" title={a.name}>
                          <Bot className="w-3 h-3 text-zinc-400" />
                        </div>
                      )
                    ))}
                    {teamAgents.length > 8 && (
                      <div className="w-7 h-7 rounded-full border-2 border-zinc-900 bg-zinc-700 flex items-center justify-center text-[9px] text-zinc-400">+{teamAgents.length - 8}</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
