import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../../App";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import {
  Rocket, Target, CheckCircle, Clock, AlertTriangle, Play,
  ChevronRight, Zap, Brain, TrendingUp, Shield, Loader2, Plus,
  BarChart3, Users, Gauge
} from "lucide-react";
import { toast } from "sonner";

const STATUS_CONFIG = {
  planning: { label: "Planning", color: "bg-amber-500/15 text-amber-400 border-amber-500/20", icon: Brain },
  active: { label: "Active", color: "bg-blue-500/15 text-blue-400 border-blue-500/20", icon: Play },
  executing: { label: "Executing", color: "bg-indigo-500/15 text-indigo-400 border-indigo-500/20", icon: Zap },
  completed: { label: "Completed", color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20", icon: CheckCircle },
  completed_with_issues: { label: "Done (Issues)", color: "bg-orange-500/15 text-orange-400 border-orange-500/20", icon: AlertTriangle },
  error: { label: "Error", color: "bg-red-500/15 text-red-400 border-red-500/20", icon: AlertTriangle },
};

const MODE_CONFIG = {
  draft: { label: "Draft", desc: "Review plan before execution" },
  approval: { label: "Approval", desc: "Approve each milestone" },
  autonomous: { label: "Autonomous", desc: "Full auto-execution" },
};

const ProjectStatusBadge = ({ status }) => {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.planning;
  const Icon = cfg.icon;
  return (
    <Badge variant="outline" className={`${cfg.color} border text-[10px] gap-1`} data-testid={`project-status-${status}`}>
      <Icon className="w-3 h-3" />{cfg.label}
    </Badge>
  );
};

const ProgressBar = ({ completed, total }) => {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${pct === 100 ? "bg-emerald-500" : "bg-indigo-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] text-zinc-500 w-8 text-right">{pct}%</span>
    </div>
  );
};

const CommandInput = ({ onSubmit, loading }) => {
  const [goal, setGoal] = useState("");
  const [mode, setMode] = useState("approval");
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!goal.trim() || loading) return;
    onSubmit(goal.trim(), mode);
    setGoal("");
    setExpanded(false);
  };

  return (
    <form onSubmit={handleSubmit} className="relative" data-testid="command-input">
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-cyan-500/20 rounded-2xl blur-sm opacity-0 group-focus-within:opacity-100 transition-opacity" />
        <div className="relative bg-zinc-900/80 border border-white/10 rounded-2xl p-1 group-focus-within:border-indigo-500/30 transition-colors">
          <div className="flex items-center gap-2 px-3">
            <Target className="w-5 h-5 text-indigo-400 shrink-0" />
            <input
              type="text"
              value={goal}
              onChange={(e) => { setGoal(e.target.value); if (e.target.value) setExpanded(true); }}
              onFocus={() => goal && setExpanded(true)}
              placeholder="Set a business goal... (e.g. 'Launch Q2 marketing campaign for our SaaS product')"
              className="flex-1 bg-transparent text-white py-3 text-sm focus:outline-none placeholder:text-zinc-600"
              data-testid="goal-input"
            />
            <Button
              type="submit"
              disabled={!goal.trim() || loading}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-4"
              data-testid="create-project-btn"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
            </Button>
          </div>

          {expanded && goal && (
            <div className="px-4 pb-3 pt-1 border-t border-white/5 mt-1 flex items-center gap-3">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Mode:</span>
              {Object.entries(MODE_CONFIG).map(([key, cfg]) => (
                <button
                  type="button"
                  key={key}
                  onClick={() => setMode(key)}
                  className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                    mode === key
                      ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                      : "text-zinc-500 hover:text-zinc-300 border border-transparent"
                  }`}
                  data-testid={`mode-${key}`}
                >
                  {cfg.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </form>
  );
};

const ProjectCard = ({ project, onExecute, onView }) => {
  const pct = project.total_tasks > 0 ? Math.round((project.completed_tasks / project.total_tasks) * 100) : 0;
  const scores = project.scores || {};

  return (
    <div
      className="bg-zinc-900/50 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all cursor-pointer group"
      onClick={() => onView(project.project_id)}
      data-testid={`project-card-${project.project_id}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-medium text-sm truncate">{project.title}</h3>
          <p className="text-[11px] text-zinc-500 truncate mt-0.5">{project.goal}</p>
        </div>
        <ProjectStatusBadge status={project.status} />
      </div>

      <ProgressBar completed={project.completed_tasks || 0} total={project.total_tasks || 0} />

      <div className="flex items-center justify-between mt-3">
        <div className="flex items-center gap-3">
          {scores.confidence && (
            <div className="flex items-center gap-1" title="Confidence Score">
              <Gauge className="w-3 h-3 text-indigo-400" />
              <span className="text-[10px] text-zinc-400">{scores.confidence}/10</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <Users className="w-3 h-3 text-zinc-500" />
            <span className="text-[10px] text-zinc-400">{scores.estimated_agents || "?"} agents</span>
          </div>
          <div className="flex items-center gap-1">
            <BarChart3 className="w-3 h-3 text-zinc-500" />
            <span className="text-[10px] text-zinc-400">{project.completed_tasks || 0}/{project.total_tasks || 0} tasks</span>
          </div>
        </div>

        {(project.status === "planning" || project.status === "active") && (
          <Button
            size="sm"
            variant="ghost"
            className="text-indigo-400 hover:bg-indigo-500/10 h-7 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => { e.stopPropagation(); onExecute(project.project_id); }}
            data-testid={`execute-project-${project.project_id}`}
          >
            <Play className="w-3 h-3 mr-1" />Execute
          </Button>
        )}
      </div>
    </div>
  );
};

const AutonomySlider = ({ level, onChange }) => {
  const levels = ["manual", "approval", "autonomous"];
  const idx = levels.indexOf(level);
  const labels = { manual: "Manual", approval: "Approval", autonomous: "Autonomous" };
  const colors = { manual: "bg-zinc-500", approval: "bg-indigo-500", autonomous: "bg-emerald-500" };
  const descriptions = {
    manual: "You control everything",
    approval: "AI plans, you approve",
    autonomous: "Full auto-execution"
  };

  return (
    <div className="flex items-center gap-3" data-testid="autonomy-slider">
      <div className="flex-1">
        <div className="flex items-center justify-between mb-2">
          {levels.map((l, i) => (
            <button
              key={l}
              onClick={() => onChange(l)}
              className={`text-[10px] font-medium transition-colors ${l === level ? "text-white" : "text-zinc-600 hover:text-zinc-400"}`}
              data-testid={`autonomy-${l}`}
            >
              {labels[l]}
            </button>
          ))}
        </div>
        <div className="h-1.5 bg-zinc-800 rounded-full relative">
          <div
            className={`h-full rounded-full transition-all duration-300 ${colors[level]}`}
            style={{ width: `${((idx + 1) / levels.length) * 100}%` }}
          />
        </div>
        <p className="text-[10px] text-zinc-500 mt-1">{descriptions[level]}</p>
      </div>
    </div>
  );
};

const CommandCenter = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [autonomy, setAutonomy] = useState("approval");
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    try {
      const [summaryRes, autoRes] = await Promise.all([
        fetch(`${API}/projects/active-summary`, { headers }),
        fetch(`${API}/user/autonomy`, { headers }),
      ]);
      if (summaryRes.ok) setSummary(await summaryRes.json());
      if (autoRes.ok) {
        const d = await autoRes.json();
        setAutonomy(d.autonomy_level || "approval");
      }
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Poll for updates every 10s
  useEffect(() => {
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleCreateProject = async (goal, mode) => {
    setCreating(true);
    try {
      const res = await fetch(`${API}/projects`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ goal, execution_mode: mode, priority: "high" }),
      });
      if (res.ok) {
        const project = await res.json();
        toast.success(`Project created: ${project.title}`);
        fetchData();
        if (mode === "autonomous") {
          toast.info("Agents are executing autonomously...");
        }
      } else {
        toast.error("Failed to create project");
      }
    } catch { toast.error("Error creating project"); }
    finally { setCreating(false); }
  };

  const handleExecute = async (projectId) => {
    try {
      const res = await fetch(`${API}/projects/${projectId}/execute`, {
        method: "POST", headers,
      });
      if (res.ok) {
        toast.success("Execution started — agents are working");
        fetchData();
      }
    } catch { toast.error("Failed to start execution"); }
  };

  const handleAutonomyChange = async (level) => {
    setAutonomy(level);
    try {
      await fetch(`${API}/user/autonomy`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ autonomy_level: level }),
      });
    } catch {}
  };

  if (loading) return null;

  const projects = summary?.projects || [];
  const active = projects.filter(p => ["active", "executing", "planning"].includes(p.status));
  const completed = projects.filter(p => ["completed", "completed_with_issues"].includes(p.status));

  return (
    <div className="space-y-6" data-testid="command-center">
      {/* Command Input */}
      <CommandInput onSubmit={handleCreateProject} loading={creating} />

      {/* Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard icon={Rocket} label="Active Projects" value={summary?.active_count || 0} color="indigo" />
        <StatCard icon={CheckCircle} label="Completed" value={summary?.completed_count || 0} color="emerald" />
        <StatCard icon={Zap} label="Agents Working" value={summary?.agents_working || 0} color="amber" />
        <StatCard icon={Target} label="Total Projects" value={summary?.total_count || 0} color="violet" />
      </div>

      {/* Autonomy Control */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/15 flex items-center justify-center">
              <Shield className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <p className="text-sm text-white font-medium">Autonomy Control</p>
              <p className="text-[10px] text-zinc-500">Set default execution mode for new projects</p>
            </div>
          </div>
          <AutonomySlider level={autonomy} onChange={handleAutonomyChange} />
        </CardContent>
      </Card>

      {/* Active Projects */}
      {active.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />Active Missions ({active.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {active.map(p => (
              <ProjectCard key={p.project_id} project={p} onExecute={handleExecute} onView={(id) => navigate(`/projects/${id}`)} />
            ))}
          </div>
        </div>
      )}

      {/* Completed Projects */}
      {completed.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />Completed ({completed.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {completed.slice(0, 4).map(p => (
              <ProjectCard key={p.project_id} project={p} onExecute={handleExecute} onView={(id) => navigate(`/projects/${id}`)} />
            ))}
          </div>
        </div>
      )}

      {projects.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
            <Rocket className="w-8 h-8 text-indigo-400" />
          </div>
          <h3 className="text-white font-semibold mb-2">Launch Your First Mission</h3>
          <p className="text-zinc-500 text-sm max-w-md mx-auto">
            Type a business goal above. Your AI workforce will analyze it, create a strategic plan, and execute autonomously.
          </p>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color }) => (
  <div className={`p-3 rounded-xl bg-${color}-500/5 border border-${color}-500/10`}>
    <div className="flex items-center gap-2 mb-1">
      <Icon className={`w-4 h-4 text-${color}-400`} />
      <span className="text-[10px] text-zinc-500 uppercase tracking-wider">{label}</span>
    </div>
    <p className="text-xl font-bold text-white">{value}</p>
  </div>
);

export default CommandCenter;
