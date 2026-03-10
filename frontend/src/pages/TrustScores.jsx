import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Shield, TrendingUp, TrendingDown, Activity, Zap, Clock, AlertTriangle, CheckCircle, Search, BarChart3 } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

export default function TrustScores() {
  const { token } = useAuth();
  const [scores, setScores] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("trust_score");

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/trust-scores`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/agents`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([scoresData, agentsData]) => {
        setScores(Array.isArray(scoresData) ? scoresData : []);
        setAgents(Array.isArray(agentsData) ? agentsData : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  const getAgent = (agentId) => agents.find(a => a.agent_id === agentId);

  const getTrustColor = (score) => {
    if (score >= 90) return { bg: "bg-emerald-500/10", text: "text-emerald-400", bar: "bg-emerald-500" };
    if (score >= 70) return { bg: "bg-blue-500/10", text: "text-blue-400", bar: "bg-blue-500" };
    if (score >= 50) return { bg: "bg-amber-500/10", text: "text-amber-400", bar: "bg-amber-500" };
    return { bg: "bg-red-500/10", text: "text-red-400", bar: "bg-red-500" };
  };

  const sortedScores = [...scores].sort((a, b) => {
    if (sortBy === "trust_score") return b.trust_score - a.trust_score;
    if (sortBy === "executions") return b.total_executions - a.total_executions;
    if (sortBy === "latency") return a.avg_latency_ms - b.avg_latency_ms;
    return 0;
  });

  const filteredScores = sortedScores.filter(s => {
    if (!searchTerm) return true;
    const agent = getAgent(s.agent_id);
    return agent?.name?.toLowerCase().includes(searchTerm.toLowerCase()) || s.agent_id.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const avgTrust = scores.length > 0 ? (scores.reduce((s, x) => s + x.trust_score, 0) / scores.length).toFixed(1) : 0;
  const totalExec = scores.reduce((s, x) => s + x.total_executions, 0);
  const highTrust = scores.filter(s => s.trust_score >= 90).length;
  const lowTrust = scores.filter(s => s.trust_score < 50).length;

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="trust-scores">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Trust Scores</h1>
          <p className="text-sm text-zinc-400 mt-1">Agent reliability and performance metrics from execution history</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="trust-summary">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Shield className="w-4 h-4 text-indigo-400" /><span className="text-xs text-zinc-500">Avg Trust Score</span></div>
          <p className="text-2xl font-bold text-white">{avgTrust}%</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Activity className="w-4 h-4 text-cyan-400" /><span className="text-xs text-zinc-500">Total Executions</span></div>
          <p className="text-2xl font-bold text-white">{totalExec}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><CheckCircle className="w-4 h-4 text-emerald-400" /><span className="text-xs text-zinc-500">High Trust (90%+)</span></div>
          <p className="text-2xl font-bold text-emerald-400">{highTrust}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle className="w-4 h-4 text-red-400" /><span className="text-xs text-zinc-500">Low Trust (&lt;50%)</span></div>
          <p className="text-2xl font-bold text-red-400">{lowTrust}</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text" placeholder="Search agents..." value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900/60 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:border-indigo-500/50"
            data-testid="trust-search"
          />
        </div>
        <select
          value={sortBy} onChange={e => setSortBy(e.target.value)}
          className="bg-zinc-900/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
          data-testid="trust-sort"
        >
          <option value="trust_score">Sort by Trust Score</option>
          <option value="executions">Sort by Executions</option>
          <option value="latency">Sort by Latency</option>
        </select>
      </div>

      {/* Scores List */}
      {filteredScores.length === 0 ? (
        <div className="bg-zinc-900/20 border border-dashed border-white/5 rounded-xl p-12 text-center" data-testid="trust-empty">
          <BarChart3 className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-500">{scores.length === 0 ? "No execution data yet. Chat with agents to build trust scores." : "No matching agents"}</p>
        </div>
      ) : (
        <div className="space-y-2" data-testid="trust-list">
          {filteredScores.map((score, i) => {
            const agent = getAgent(score.agent_id);
            const tc = getTrustColor(score.trust_score);
            return (
              <div key={score.agent_id} className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-colors" data-testid={`trust-agent-${score.agent_id}`}>
                <div className="flex items-center gap-4">
                  <div className="text-lg font-bold text-zinc-600 w-8 text-center">#{i + 1}</div>
                  {agent?.avatar ? (
                    <img src={agent.avatar} alt="" className="w-10 h-10 rounded-lg object-cover" />
                  ) : (
                    <div className="w-10 h-10 rounded-lg bg-zinc-700/50 flex items-center justify-center text-xs font-bold text-zinc-400">
                      {(agent?.name || score.agent_id).split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-white truncate">{agent?.name || score.agent_id}</p>
                      {agent?.role && <span className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">{agent.role}</span>}
                    </div>
                    <div className="flex items-center gap-4 mt-1.5">
                      <div className="flex-1 max-w-xs">
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${tc.bar} transition-all`} style={{ width: `${score.trust_score}%` }} />
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-[11px]">
                        <span className="text-zinc-500 flex items-center gap-1"><Zap className="w-3 h-3" />{score.total_executions} runs</span>
                        <span className="text-emerald-400 flex items-center gap-1"><TrendingUp className="w-3 h-3" />{(score.success_rate * 100).toFixed(0)}% success</span>
                        {score.failure_rate > 0 && <span className="text-red-400 flex items-center gap-1"><TrendingDown className="w-3 h-3" />{(score.failure_rate * 100).toFixed(0)}% fail</span>}
                        <span className="text-zinc-500 flex items-center gap-1"><Clock className="w-3 h-3" />{score.avg_latency_ms.toFixed(0)}ms</span>
                      </div>
                    </div>
                  </div>
                  <div className={`text-xl font-bold ${tc.text} w-16 text-right`}>{score.trust_score}%</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
