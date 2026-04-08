import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Users, Plus, Search, X, Trash2, Edit3, Check, Bot, Network,
  Save
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} }`;

const formInput = {
  background: "rgba(255,255,255,.04)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  padding: "8px 12px",
  color: "#fff",
  fontSize: 13,
  outline: "none",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
  transition: "border-color .2s",
};

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

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <style>{STYLES}</style>
      <div style={{ width: 20, height: 20, border: "2px solid #818cf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="team-builder-page">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif" }}>Agent Team Builder</h1>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: T.zinc }}>Assemble custom teams from {agents.length}+ agents for targeted projects</p>
        </div>
        {!creating && (
          <button
            onClick={() => setCreating(true)}
            style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", background: "linear-gradient(135deg,#6366f1,#7c3aed)", border: "none", borderRadius: 8, color: "#fff", fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}
            data-testid="create-team-btn"
          >
            <Plus size={14} /> New Team
          </button>
        )}
      </div>

      {/* Create / Edit Form */}
      {creating && (
        <div
          style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}
          data-testid="team-form"
        >
          <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <h2 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "#fff" }}>{editingId ? "Edit Team" : "Create New Team"}</h2>
              <button
                onClick={resetForm}
                style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4, display: "flex", alignItems: "center" }}
              >
                <X size={16} />
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
              <input
                placeholder="Team name *"
                value={teamName}
                onChange={e => setTeamName(e.target.value)}
                style={formInput}
                data-testid="team-name-input"
              />
              <input
                placeholder="Purpose (e.g. Q1 Marketing)"
                value={teamPurpose}
                onChange={e => setTeamPurpose(e.target.value)}
                style={formInput}
                data-testid="team-purpose-input"
              />
              <input
                placeholder="Description"
                value={teamDesc}
                onChange={e => setTeamDesc(e.target.value)}
                style={formInput}
                data-testid="team-desc-input"
              />
            </div>

            {/* Agent Selection */}
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ position: "relative", flex: 1 }}>
                <Search size={14} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
                <input
                  placeholder="Search agents..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  style={{ ...formInput, paddingLeft: 32 }}
                  data-testid="agent-search-input"
                />
              </div>
              <select
                value={networkFilter}
                onChange={e => setNetworkFilter(e.target.value)}
                style={{ background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "8px 12px", color: "#d4d4d8", fontSize: 12, outline: "none", fontFamily: "inherit", cursor: "pointer" }}
                data-testid="network-filter"
              >
                <option value="">All Networks</option>
                {networks.map(n => <option key={n} value={n}>{NETWORK_LABELS[n] || n}</option>)}
              </select>
              <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: "rgba(129,140,248,.15)", color: T.indigo, whiteSpace: "nowrap" }}>
                {selectedIds.size} selected
              </span>
            </div>

            {/* Agent Grid */}
            <div
              style={{ maxHeight: 256, overflowY: "auto", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 10, padding: 8, display: "flex", flexDirection: "column", gap: 4 }}
              data-testid="agent-selection-grid"
            >
              {filteredAgents.map(agent => {
                const isSelected = selectedIds.has(agent.agent_id);
                return (
                  <button
                    key={agent.agent_id}
                    onClick={() => toggleAgent(agent.agent_id)}
                    style={{
                      width: "100%",
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "6px 8px",
                      borderRadius: 8,
                      textAlign: "left",
                      background: isSelected ? "rgba(99,102,241,0.12)" : "transparent",
                      border: isSelected ? "1px solid rgba(99,102,241,0.3)" : "1px solid transparent",
                      cursor: "pointer",
                      fontFamily: "inherit",
                      transition: "background .15s, border-color .15s",
                    }}
                    data-testid={`agent-select-${agent.agent_id}`}
                  >
                    {agent.avatar && !agent.avatar.startsWith("data:") ? (
                      <img src={agent.avatar.startsWith("/") ? `${API.replace("/api", "")}${agent.avatar}` : agent.avatar} alt="" style={{ width: 28, height: 28, borderRadius: 6, objectFit: "cover" }} loading="lazy" />
                    ) : (
                      <div style={{ width: 28, height: 28, borderRadius: 6, background: "#3f3f46", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Bot size={14} color={T.zinc} />
                      </div>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ margin: 0, fontSize: 12, fontWeight: 500, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</p>
                      <p style={{ margin: 0, fontSize: 10, color: T.zinc, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {agent.role}{agent.network ? ` | ${NETWORK_LABELS[agent.network] || agent.network}` : ""}
                      </p>
                    </div>
                    {isSelected && <Check size={14} color={T.indigo} style={{ flexShrink: 0 }} />}
                  </button>
                );
              })}
              {filteredAgents.length === 0 && (
                <p style={{ margin: 0, fontSize: 12, color: T.zinc, textAlign: "center", padding: "16px 0" }}>No agents match your search</p>
              )}
            </div>

            {/* Selected preview */}
            {selectedIds.size > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {[...selectedIds].slice(0, 12).map(id => {
                  const a = getAgentById(id);
                  return a ? (
                    <span
                      key={id}
                      style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: "rgba(129,140,248,.15)", color: "#a5b4fc", border: "1px solid rgba(129,140,248,0.2)" }}
                    >
                      {a.name}
                      <X size={10} style={{ cursor: "pointer" }} onClick={() => toggleAgent(id)} />
                    </span>
                  ) : null;
                })}
                {selectedIds.size > 12 && (
                  <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: "rgba(113,113,122,.2)", color: T.zinc }}>
                    +{selectedIds.size - 12} more
                  </span>
                )}
              </div>
            )}

            <button
              onClick={handleSave}
              disabled={saving}
              style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, width: "100%", padding: "10px 16px", background: saving ? "rgba(99,102,241,0.5)" : "linear-gradient(135deg,#6366f1,#7c3aed)", border: "none", borderRadius: 8, color: "#fff", fontSize: 13, fontWeight: 600, cursor: saving ? "not-allowed" : "pointer", fontFamily: "inherit" }}
              data-testid="save-team-btn"
            >
              {saving
                ? <div style={{ width: 16, height: 16, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
                : <Save size={14} />
              }
              {editingId ? "Update Team" : "Create Team"}
            </button>
          </div>
        </div>
      )}

      {/* Teams List */}
      {teams.length === 0 && !creating ? (
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
          <div style={{ padding: "40px 20px", textAlign: "center" }}>
            <Users size={40} color="#3f3f46" style={{ display: "block", margin: "0 auto 12px" }} />
            <p style={{ margin: 0, fontSize: 13, color: T.zinc }}>No agent teams yet. Create your first team to get started.</p>
          </div>
        </div>
      ) : (
        <div
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}
          data-testid="teams-grid"
        >
          {teams.map(team => {
            const teamAgents = (team.agent_ids || []).map(id => getAgentById(id)).filter(Boolean);
            const networkCounts = {};
            teamAgents.forEach(a => { const n = a.network || "core"; networkCounts[n] = (networkCounts[n] || 0) + 1; });
            return (
              <div
                key={team.team_id}
                style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden", transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(99,102,241,0.25)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
                data-testid={`team-card-${team.team_id}`}
              >
                <div style={{ padding: 16 }}>
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 8 }}>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <h3 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{team.name}</h3>
                      {team.purpose && <p style={{ margin: "2px 0 0", fontSize: 10, color: T.indigo }}>{team.purpose}</p>}
                    </div>
                    <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
                      <button
                        onClick={() => handleEdit(team)}
                        style={{ background: "none", border: "none", cursor: "pointer", padding: 4, display: "flex", alignItems: "center", borderRadius: 6 }}
                        data-testid={`edit-team-${team.team_id}`}
                      >
                        <Edit3 size={13} color={T.zinc} />
                      </button>
                      <button
                        onClick={() => handleDelete(team.team_id)}
                        style={{ background: "none", border: "none", cursor: "pointer", padding: 4, display: "flex", alignItems: "center", borderRadius: 6 }}
                        data-testid={`delete-team-${team.team_id}`}
                      >
                        <Trash2 size={13} color={T.red} />
                      </button>
                    </div>
                  </div>

                  {team.description && (
                    <p style={{ margin: "0 0 8px", fontSize: 10, color: T.zinc }}>{team.description}</p>
                  )}

                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: "rgba(129,140,248,.15)", color: T.indigo }}>
                      <Users size={10} /> {teamAgents.length} agents
                    </span>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: "rgba(124,58,237,.15)", color: "#a78bfa" }}>
                      <Network size={10} /> {Object.keys(networkCounts).length} networks
                    </span>
                  </div>

                  {/* Agent avatar row */}
                  <div style={{ display: "flex" }}>
                    {teamAgents.slice(0, 8).map(a => (
                      a.avatar && !a.avatar.startsWith("data:") ? (
                        <img
                          key={a.agent_id}
                          src={a.avatar.startsWith("/") ? `${API.replace("/api", "")}${a.avatar}` : a.avatar}
                          alt=""
                          style={{ width: 28, height: 28, borderRadius: "50%", border: "2px solid #18181b", objectFit: "cover", marginLeft: -8 }}
                          title={a.name}
                          loading="lazy"
                        />
                      ) : (
                        <div
                          key={a.agent_id}
                          style={{ width: 28, height: 28, borderRadius: "50%", border: "2px solid #18181b", background: "#3f3f46", display: "flex", alignItems: "center", justifyContent: "center", marginLeft: -8 }}
                          title={a.name}
                        >
                          <Bot size={11} color={T.zinc} />
                        </div>
                      )
                    ))}
                    {teamAgents.length > 8 && (
                      <div style={{ width: 28, height: 28, borderRadius: "50%", border: "2px solid #18181b", background: "#3f3f46", display: "flex", alignItems: "center", justifyContent: "center", marginLeft: -8, fontSize: 9, color: T.zinc }}>
                        +{teamAgents.length - 8}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
