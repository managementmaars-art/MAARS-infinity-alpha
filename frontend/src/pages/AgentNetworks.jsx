import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import { Network, ChevronRight, Users, Layers, Search, Bot, MessageSquare } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "http://localhost:8000";

const LAYER_COLORS = {
  infrastructure: "emerald",
  strategic: "purple",
  executive: "blue",
  department: "cyan",
  intelligence: "amber",
  governance: "rose",
  execution: "orange",
  verification: "indigo",
};

export default function AgentNetworks() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [networks, setNetworks] = useState([]);
  const [selected, setSelected] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch(`${API}/api/kernel/networks`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setNetworks(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    if (!selected) { setAgents([]); return; }
    fetch(`${API}/api/kernel/networks/${selected}/agents`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => setAgents(data.agents || []))
      .catch(() => setAgents([]));
  }, [selected, token]);

  const filteredNetworks = networks.filter(n =>
    !searchTerm || n.name.toLowerCase().includes(searchTerm.toLowerCase()) || n.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredAgents = agents.filter(a =>
    !searchTerm || a.name.toLowerCase().includes(searchTerm.toLowerCase()) || a.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="agent-networks">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Agent Networks</h1>
          <p className="text-sm text-zinc-400 mt-1">{networks.length} networks — {networks.reduce((s, n) => s + n.agent_count, 0)} specialized agents</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search networks or agents..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="bg-zinc-900/60 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-zinc-500 w-64 focus:outline-none focus:border-emerald-500/50"
            data-testid="network-search"
          />
        </div>
      </div>

      <div className="flex gap-6">
        {/* Networks List */}
        <div className="w-full lg:w-1/2 space-y-2" data-testid="networks-list">
          {filteredNetworks.map(net => {
            const color = LAYER_COLORS[net.layer] || "zinc";
            const isSelected = selected === net.key;
            return (
              <button
                key={net.key}
                onClick={() => setSelected(isSelected ? null : net.key)}
                className={`w-full text-left bg-zinc-900/40 border rounded-xl p-4 transition-all hover:border-white/15 ${isSelected ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-white/5'}`}
                data-testid={`network-${net.code}`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center`}>
                    <Network className={`w-5 h-5 text-${color}-400`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">{net.code}</span>
                      <span className="text-sm font-medium text-white truncate">{net.name}</span>
                    </div>
                    <p className="text-[11px] text-zinc-500 mt-0.5 truncate">{net.purpose}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-400 bg-zinc-800/60 px-2 py-0.5 rounded-full">{net.agent_count}</span>
                    <ChevronRight className={`w-4 h-4 text-zinc-500 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Agent Detail Panel */}
        <div className="hidden lg:block w-1/2" data-testid="agent-detail-panel">
          {selected ? (
            <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-5 sticky top-4">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">{networks.find(n => n.key === selected)?.name} Agents</h3>
                <span className="text-[10px] text-zinc-500 ml-auto">{filteredAgents.length} agents</span>
              </div>
              <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-2">
                {filteredAgents.map(agent => (
                  <div key={agent.agent_id} className="bg-zinc-800/40 border border-white/5 rounded-lg p-3 hover:border-white/10 transition-colors group" data-testid={`agent-${agent.agent_id}`}>
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-zinc-700/50 flex items-center justify-center shrink-0">
                        <Bot className="w-4 h-4 text-zinc-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-white truncate">{agent.name}</p>
                        <p className="text-[10px] text-zinc-500">{agent.role}</p>
                        {agent.capabilities && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {agent.capabilities.slice(0, 4).map((cap, i) => (
                              <span key={i} className="text-[9px] bg-zinc-700/50 text-zinc-400 px-1.5 py-0.5 rounded">{cap}</span>
                            ))}
                            {agent.capabilities.length > 4 && (
                              <span className="text-[9px] text-zinc-500">+{agent.capabilities.length - 4}</span>
                            )}
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-1.5 shrink-0">
                        <span className="text-[9px] font-mono text-emerald-500/60 bg-emerald-500/5 px-1.5 py-0.5 rounded">T{agent.autonomy_tier}</span>
                        <button
                          onClick={() => navigate(`/chat/${agent.agent_id}`)}
                          className="flex items-center gap-1 px-2 py-1 rounded-md bg-indigo-500/10 text-indigo-400 text-[10px] font-medium hover:bg-indigo-500/20 transition-colors opacity-0 group-hover:opacity-100"
                          data-testid={`chat-agent-${agent.agent_id}`}
                        >
                          <MessageSquare className="w-3 h-3" />
                          Chat
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-zinc-900/20 border border-dashed border-white/5 rounded-xl p-12 flex flex-col items-center justify-center text-center">
              <Network className="w-12 h-12 text-zinc-700 mb-3" />
              <p className="text-sm text-zinc-500">Select a network to view its agents</p>
              <p className="text-xs text-zinc-600 mt-1">28 networks with 458+ specialized agents</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
