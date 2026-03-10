import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Layers, Activity, Shield, Database, GitBranch, Network, Cpu, Clock, CheckCircle2, AlertTriangle } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const SUBSYSTEM_ICONS = {
  agent_scheduler: Activity,
  task_graph_runtime: GitBranch,
  resource_manager: Cpu,
  budget_controller: Shield,
  execution_gateway: Network,
  tool_registry: Database,
  memory_controller: Database,
  policy_engine: Shield,
  approval_controller: CheckCircle2,
  failure_recovery: AlertTriangle,
  circuit_breakers: AlertTriangle,
};

export default function KernelDashboard() {
  const { token } = useAuth();
  const [kernel, setKernel] = useState(null);
  const [architecture, setArchitecture] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ks, arch] = await Promise.all([
          fetch(`${API}/api/kernel/status`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
          fetch(`${API}/api/kernel/architecture`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
        ]);
        setKernel(ks);
        setArchitecture(arch);
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    fetchData();
  }, [token]);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-8" data-testid="kernel-dashboard">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">MAARS Kernel</h1>
        <p className="text-sm text-zinc-400 mt-1">Core runtime operating system — 15 subsystems</p>
      </div>

      {/* Status Overview */}
      {kernel && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Agents", value: kernel.metrics?.total_agents, color: "emerald" },
            { label: "Active Tasks", value: kernel.metrics?.active_tasks, color: "blue" },
            { label: "Task Graphs", value: kernel.metrics?.total_task_graphs, color: "purple" },
            { label: "Executions", value: kernel.metrics?.execution_logs, color: "amber" },
            { label: "Memory Entries", value: kernel.metrics?.memory_entries, color: "cyan" },
            { label: "Tools", value: kernel.metrics?.tools_registered, color: "rose" },
            { label: "Active Graphs", value: kernel.metrics?.active_task_graphs, color: "indigo" },
            { label: "Total Tasks", value: kernel.metrics?.total_tasks, color: "orange" },
          ].map((m, i) => (
            <div key={i} className="bg-zinc-900/60 border border-white/5 rounded-xl p-4" data-testid={`metric-${m.label.toLowerCase().replace(/ /g, '-')}`}>
              <p className="text-xs text-zinc-500 uppercase tracking-wider">{m.label}</p>
              <p className={`text-2xl font-bold text-${m.color}-400 mt-1`}>{m.value ?? 0}</p>
            </div>
          ))}
        </div>
      )}

      {/* Subsystems Status */}
      {kernel?.subsystems && (
        <div>
          <h2 className="text-base font-semibold text-white mb-4">Kernel Subsystems</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(kernel.subsystems).filter(([k]) => k !== 'circuit_breakers').map(([key, sub]) => {
              const Icon = SUBSYSTEM_ICONS[key] || Cpu;
              return (
                <div key={key} className="bg-zinc-900/40 border border-white/5 rounded-lg p-3 flex items-center gap-3" data-testid={`subsystem-${key}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${sub.status === 'active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
                    <Icon className={`w-4 h-4 ${sub.status === 'active' ? 'text-emerald-400' : 'text-amber-400'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white font-medium truncate">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                    <p className="text-[10px] text-zinc-500">
                      {sub.status}
                      {sub.agents_registered != null && ` — ${sub.agents_registered} agents`}
                      {sub.total_graphs != null && ` — ${sub.total_graphs} graphs`}
                      {sub.total_executions != null && ` — ${sub.total_executions} execs`}
                      {sub.tools_registered != null && ` — ${sub.tools_registered} tools`}
                      {sub.entries != null && ` — ${sub.entries} entries`}
                    </p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${sub.status === 'active' ? 'bg-emerald-400' : sub.status === 'standby' ? 'bg-amber-400' : 'bg-red-400'}`} />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* System Layers */}
      {architecture?.layers && (
        <div>
          <h2 className="text-base font-semibold text-white mb-4">System Architecture — {architecture.layers.length} Layers</h2>
          <div className="space-y-1">
            {architecture.layers.map((layer, i) => (
              <div key={i} className="flex items-center gap-3 bg-zinc-900/30 border border-white/5 rounded-lg px-4 py-2.5 hover:border-white/10 transition-colors" data-testid={`layer-${i}`}>
                <div className="w-6 h-6 rounded bg-zinc-800 flex items-center justify-center">
                  <span className="text-[10px] font-mono text-zinc-400">{i}</span>
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium text-white">{layer.name}</p>
                  <p className="text-[10px] text-zinc-500">{layer.description}</p>
                </div>
                <Layers className="w-3 h-3 text-zinc-600" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Autonomy Tiers */}
      {architecture?.autonomy_tiers && (
        <div>
          <h2 className="text-base font-semibold text-white mb-4">Autonomy Tiers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(architecture.autonomy_tiers).map(([tier, desc]) => (
              <div key={tier} className="bg-zinc-900/40 border border-white/5 rounded-lg p-3" data-testid={`tier-${tier}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-emerald-400">T{tier}</span>
                  <div className="flex-1 h-px bg-white/5" />
                </div>
                <p className="text-[11px] text-zinc-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Stats */}
      {architecture && (
        <div className="flex items-center gap-6 text-xs text-zinc-500 border-t border-white/5 pt-4">
          <span>{architecture.total_agents} Infinity Agents</span>
          <span>{architecture.total_networks} Networks</span>
          <span>{architecture.layers?.length} Layers</span>
          <span className="ml-auto"><Clock className="w-3 h-3 inline mr-1" />{kernel?.timestamp ? new Date(kernel.timestamp).toLocaleString() : ''}</span>
        </div>
      )}
    </div>
  );
}
