import { useState, useEffect } from "react";
import { Loader2, CheckCircle, Clock, Zap } from "lucide-react";

const statusConfig = {
  pending: { color: "text-zinc-500", bg: "bg-zinc-500/10", ring: "ring-zinc-500/30", icon: Clock, label: "Queued" },
  working: { color: "text-amber-400", bg: "bg-amber-500/10", ring: "ring-amber-500/40", icon: Loader2, label: "Working" },
  completed: { color: "text-emerald-400", bg: "bg-emerald-500/10", ring: "ring-emerald-500/40", icon: CheckCircle, label: "Done" },
  failed: { color: "text-red-400", bg: "bg-red-500/10", ring: "ring-red-500/40", icon: Zap, label: "Error" },
};

const priorityColors = {
  high: "bg-red-500/20 text-red-400",
  medium: "bg-amber-500/20 text-amber-400",
  low: "bg-blue-500/20 text-blue-400",
};

export const CollaborationWorkflow = ({ progress, commanderAvatar }) => {
  const [animatedAgents, setAnimatedAgents] = useState([]);
  const phase = progress?.phase || "planning";
  const agents = progress?.agents || [];
  const currentAgent = progress?.current_agent;

  useEffect(() => {
    setAnimatedAgents(agents);
  }, [JSON.stringify(agents)]);

  const completedCount = animatedAgents.filter(a => a.status === "completed").length;
  const totalCount = animatedAgents.length;
  const progressPct = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  if (phase === "planning") {
    return (
      <div className="rounded-xl bg-zinc-900/80 border border-indigo-500/20 p-5 max-w-lg" data-testid="collab-planning">
        <div className="flex items-center gap-3 mb-3">
          <div className="relative">
            <img src={commanderAvatar} alt="Commander" className="w-10 h-10 rounded-lg object-cover" />
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-amber-500 ring-2 ring-zinc-900 animate-pulse" />
          </div>
          <div>
            <p className="text-amber-400 font-semibold text-sm">Commander Orion</p>
            <p className="text-zinc-500 text-xs">Analyzing goal & building strategy...</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-1 flex-1 rounded-full bg-zinc-800 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full animate-pulse w-1/3" />
          </div>
          <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-zinc-900/80 border border-white/10 p-5 max-w-2xl" data-testid="collab-workflow">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <img src={commanderAvatar} alt="Commander" className="w-9 h-9 rounded-lg object-cover" />
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-zinc-900" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Mission Control</p>
            <p className="text-zinc-500 text-[11px]">{completedCount}/{totalCount} specialists reporting</p>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-medium">
          LIVE
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 transition-all duration-700 ease-out"
            style={{ width: `${Math.max(progressPct, 5)}%` }}
          />
        </div>
      </div>

      {/* Agent cards */}
      <div className="space-y-2">
        {animatedAgents.map((agent, idx) => {
          const cfg = statusConfig[agent.status] || statusConfig.pending;
          const StatusIcon = cfg.icon;
          const isActive = agent.agent_name === currentAgent;

          return (
            <div
              key={agent.agent_id || idx}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                isActive ? "bg-amber-500/5 border border-amber-500/20" : "bg-white/[0.02] border border-transparent"
              }`}
              style={{ animationDelay: `${idx * 80}ms` }}
              data-testid={`collab-agent-${idx}`}
            >
              {/* Avatar with status ring */}
              <div className="relative flex-shrink-0">
                <img
                  src={agent.agent_avatar}
                  alt={agent.agent_name}
                  className={`w-8 h-8 rounded-full object-cover ring-2 ${cfg.ring} transition-all duration-300`}
                />
                {agent.status === "working" && (
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-amber-500 ring-2 ring-zinc-900 animate-pulse" />
                )}
                {agent.status === "completed" && (
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-zinc-900" />
                )}
              </div>

              {/* Agent info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm font-medium truncate">{agent.agent_name}</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${priorityColors[agent.priority]}`}>
                    {agent.priority?.toUpperCase()}
                  </span>
                </div>
                <p className="text-zinc-500 text-[11px] truncate">{agent.task_title}</p>
              </div>

              {/* Status */}
              <div className={`flex items-center gap-1.5 ${cfg.color}`}>
                <StatusIcon className={`w-3.5 h-3.5 ${agent.status === "working" ? "animate-spin" : ""}`} />
                <span className="text-[10px] font-medium">{cfg.label}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-white/5">
        <p className="text-zinc-600 text-[10px]">
          Results appear automatically when all specialists complete their tasks.
        </p>
      </div>
    </div>
  );
};
