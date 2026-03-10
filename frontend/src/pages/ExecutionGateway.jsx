import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Activity, Zap, Clock, CheckCircle, XCircle, AlertTriangle, Search, Filter, ArrowRight, DollarSign } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_STYLES = {
  completed: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10" },
  failed: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10" },
  pending: { icon: Clock, color: "text-amber-400", bg: "bg-amber-500/10" },
  running: { icon: Activity, color: "text-blue-400", bg: "bg-blue-500/10" },
};

export default function ExecutionGateway() {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/execution-logs?limit=200`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/agents`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([logsData, agentsData]) => {
        setLogs(Array.isArray(logsData) ? logsData : []);
        setAgents(Array.isArray(agentsData) ? agentsData : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  const getAgent = (agentId) => agents.find(a => a.agent_id === agentId);

  const filteredLogs = logs.filter(log => {
    if (statusFilter !== "all" && log.status !== statusFilter) return false;
    if (searchTerm) {
      const agent = getAgent(log.agent_id);
      const match = log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.agent_id?.toLowerCase().includes(searchTerm.toLowerCase());
      if (!match) return false;
    }
    return true;
  });

  const totalCost = logs.reduce((s, l) => s + (l.cost || 0), 0);
  const avgLatency = logs.length > 0 ? (logs.reduce((s, l) => s + (l.latency_ms || 0), 0) / logs.length).toFixed(0) : 0;
  const successRate = logs.length > 0 ? ((logs.filter(l => l.status === "completed").length / logs.length) * 100).toFixed(1) : 0;

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="execution-gateway">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Execution Gateway</h1>
        <p className="text-sm text-zinc-400 mt-1">All agent actions flow through governed execution with cost metering and audit trails</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="exec-metrics">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Zap className="w-4 h-4 text-indigo-400" /><span className="text-xs text-zinc-500">Total Executions</span></div>
          <p className="text-2xl font-bold text-white">{logs.length}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><CheckCircle className="w-4 h-4 text-emerald-400" /><span className="text-xs text-zinc-500">Success Rate</span></div>
          <p className="text-2xl font-bold text-emerald-400">{successRate}%</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Clock className="w-4 h-4 text-amber-400" /><span className="text-xs text-zinc-500">Avg Latency</span></div>
          <p className="text-2xl font-bold text-white">{avgLatency}ms</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><DollarSign className="w-4 h-4 text-cyan-400" /><span className="text-xs text-zinc-500">Total Cost</span></div>
          <p className="text-2xl font-bold text-white">${totalCost.toFixed(4)}</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text" placeholder="Search actions or agents..." value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900/60 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:border-indigo-500/50"
            data-testid="exec-search"
          />
        </div>
        <select
          value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="bg-zinc-900/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
          data-testid="exec-status-filter"
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      {/* Execution Log */}
      {filteredLogs.length === 0 ? (
        <div className="bg-zinc-900/20 border border-dashed border-white/5 rounded-xl p-12 text-center" data-testid="exec-empty">
          <Activity className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-500">{logs.length === 0 ? "No executions yet. Actions are logged as you chat with agents." : "No matching executions"}</p>
        </div>
      ) : (
        <div className="space-y-1.5" data-testid="exec-log-list">
          {filteredLogs.map((log, i) => {
            const agent = getAgent(log.agent_id);
            const st = STATUS_STYLES[log.status] || STATUS_STYLES.completed;
            const StatusIcon = st.icon;
            return (
              <div key={i} className="bg-zinc-900/40 border border-white/5 rounded-lg px-4 py-3 hover:border-white/10 transition-colors" data-testid={`exec-log-${i}`}>
                <div className="flex items-center gap-3">
                  <StatusIcon className={`w-4 h-4 ${st.color} shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm text-white font-medium">{log.action}</span>
                      <ArrowRight className="w-3 h-3 text-zinc-600" />
                      <span className="text-xs text-zinc-400">{agent?.name || log.agent_id || "System"}</span>
                      {log.tool_id && <span className="text-[10px] bg-zinc-800 text-zinc-500 px-1.5 py-0.5 rounded">{log.tool_id}</span>}
                    </div>
                    {log.input_summary && <p className="text-[11px] text-zinc-500 mt-0.5 truncate">{log.input_summary}</p>}
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-zinc-500 shrink-0">
                    {log.cost > 0 && <span>${log.cost.toFixed(4)}</span>}
                    {log.latency_ms > 0 && <span>{log.latency_ms.toFixed(0)}ms</span>}
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${st.bg} ${st.color}`}>{log.status}</span>
                    <span className="text-zinc-600">{log.created_at ? new Date(log.created_at).toLocaleTimeString() : ""}</span>
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
