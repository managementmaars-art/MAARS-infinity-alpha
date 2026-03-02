import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth, API } from "../../App";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  ArrowLeft, Play, CheckCircle, Clock, AlertTriangle, Brain,
  Target, Gauge, Shield, Users, Zap, ChevronDown, ChevronUp,
  Trash2, Loader2
} from "lucide-react";
import { toast } from "sonner";

const STATUS_ICONS = {
  pending: Clock,
  in_progress: Zap,
  completed: CheckCircle,
  failed: AlertTriangle,
};

const STATUS_COLORS = {
  pending: "text-zinc-500",
  in_progress: "text-indigo-400",
  completed: "text-emerald-400",
  failed: "text-red-400",
};

const ProjectDetail = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [expandedTasks, setExpandedTasks] = useState({});

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const res = await fetch(`${API}/projects/${projectId}`, { headers });
        if (res.ok) setProject(await res.json());
        else navigate("/projects");
      } catch { navigate("/projects"); }
      finally { setLoading(false); }
    };
    fetchProject();
    const interval = setInterval(fetchProject, 5000);
    return () => clearInterval(interval);
  }, [projectId, token]);

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const res = await fetch(`${API}/projects/${projectId}/execute`, { method: "POST", headers });
      if (res.ok) toast.success("Execution started");
    } catch { toast.error("Failed"); }
    finally { setExecuting(false); }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this project and all its tasks?")) return;
    try {
      await fetch(`${API}/projects/${projectId}`, { method: "DELETE", headers });
      toast.success("Project deleted");
      navigate("/projects");
    } catch { toast.error("Failed to delete"); }
  };

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
    </div>
  );

  if (!project) return null;

  const scores = project.scores || {};
  const tasks = project.tasks_detail || [];
  const taskMap = Object.fromEntries(tasks.map(t => [t.task_id, t]));
  const pct = project.total_tasks > 0 ? Math.round((project.completed_tasks / project.total_tasks) * 100) : 0;

  return (
    <div className="space-y-6" data-testid="project-detail">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate("/projects")} className="text-zinc-400 hover:text-white shrink-0 mt-1" data-testid="back-to-projects">
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white font-['Outfit'] truncate">{project.title}</h1>
            <Badge variant="outline" className={`border-white/10 text-xs ${
              project.status === "completed" ? "text-emerald-400" :
              project.status === "executing" ? "text-indigo-400" : "text-zinc-400"
            }`}>{project.status}</Badge>
          </div>
          <p className="text-sm text-zinc-400">{project.goal}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          {["planning", "active"].includes(project.status) && (
            <Button onClick={handleExecute} disabled={executing} className="bg-indigo-600 hover:bg-indigo-500 text-white" size="sm" data-testid="execute-btn">
              {executing ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Play className="w-4 h-4 mr-1" />}
              Execute
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={handleDelete} className="text-zinc-500 hover:text-red-400" data-testid="delete-project-btn">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Scores Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <ScoreCard icon={Gauge} label="Confidence" value={`${scores.confidence || 0}/10`} color="indigo" />
        <ScoreCard icon={Brain} label="Complexity" value={`${scores.complexity || 0}/10`} color="violet" />
        <ScoreCard icon={Shield} label="Risk" value={scores.risk_level || "medium"} color={scores.risk_level === "low" ? "emerald" : scores.risk_level === "high" ? "red" : "amber"} />
        <ScoreCard icon={Users} label="Agents" value={scores.estimated_agents || 0} color="cyan" />
        <ScoreCard icon={Clock} label="Est. Hours" value={scores.estimated_hours || "?"} color="zinc" />
      </div>

      {/* Progress */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-white font-medium">Progress</p>
            <span className="text-xs text-zinc-400">{project.completed_tasks || 0}/{project.total_tasks || 0} tasks</span>
          </div>
          <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-700 ${pct === 100 ? "bg-emerald-500" : "bg-indigo-500"}`} style={{ width: `${pct}%` }} />
          </div>
        </CardContent>
      </Card>

      {/* Strategy */}
      {project.execution_strategy && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-4">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Execution Strategy</p>
            <p className="text-sm text-zinc-300">{project.execution_strategy}</p>
            {project.success_criteria?.length > 0 && (
              <div className="mt-3">
                <p className="text-xs text-zinc-500 mb-1">Success Criteria:</p>
                <ul className="space-y-1">
                  {project.success_criteria.map((c, i) => (
                    <li key={i} className="text-xs text-zinc-400 flex items-start gap-2">
                      <CheckCircle className="w-3 h-3 text-emerald-500 mt-0.5 shrink-0" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Milestones & Tasks */}
      <div className="space-y-4">
        {project.milestones?.map((ms, msIdx) => {
          const msTasks = ms.task_ids?.map(id => taskMap[id]).filter(Boolean) || [];
          const msComplete = msTasks.filter(t => t.status === "completed").length;
          return (
            <Card key={ms.milestone_id} className="bg-zinc-900/50 border-white/10" data-testid={`milestone-${msIdx}`}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white text-sm font-['Outfit'] flex items-center gap-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      ms.status === "completed" ? "bg-emerald-500/20 text-emerald-400" :
                      ms.status === "in_progress" ? "bg-indigo-500/20 text-indigo-400" :
                      "bg-zinc-800 text-zinc-500"
                    }`}>{msIdx + 1}</div>
                    {ms.title}
                  </CardTitle>
                  <span className="text-[10px] text-zinc-500">{msComplete}/{msTasks.length}</span>
                </div>
                {ms.description && <p className="text-xs text-zinc-500 ml-8">{ms.description}</p>}
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2 ml-8">
                  {msTasks.map(task => {
                    const StatusIcon = STATUS_ICONS[task.status] || Clock;
                    const isExpanded = expandedTasks[task.task_id];
                    return (
                      <div key={task.task_id} className="border border-white/5 rounded-lg overflow-hidden" data-testid={`task-${task.task_id}`}>
                        <button
                          onClick={() => setExpandedTasks(prev => ({...prev, [task.task_id]: !prev[task.task_id]}))}
                          className="w-full flex items-center gap-3 p-3 hover:bg-white/[0.02] transition-colors text-left"
                        >
                          <StatusIcon className={`w-4 h-4 shrink-0 ${STATUS_COLORS[task.status]}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{task.title}</p>
                            <p className="text-[10px] text-zinc-500">{task.agent_name} ({task.agent_role})</p>
                          </div>
                          <Badge variant="outline" className={`text-[9px] border-white/10 ${
                            task.priority === "high" ? "text-red-400" : task.priority === "low" ? "text-zinc-500" : "text-amber-400"
                          }`}>{task.priority}</Badge>
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
                        </button>
                        {isExpanded && (
                          <div className="px-3 pb-3 border-t border-white/5">
                            <p className="text-xs text-zinc-400 mt-2 mb-2">{task.description}</p>
                            {task.result && (
                              <div className="p-3 bg-zinc-800/50 rounded-lg mt-2">
                                <p className="text-[10px] text-zinc-500 mb-1 uppercase tracking-wider">Agent Result</p>
                                <div className="text-xs text-zinc-300 whitespace-pre-wrap max-h-[300px] overflow-y-auto">{task.result}</div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

const ScoreCard = ({ icon: Icon, label, value, color }) => (
  <div className={`p-3 rounded-xl bg-${color}-500/5 border border-${color}-500/10 text-center`}>
    <Icon className={`w-4 h-4 text-${color}-400 mx-auto mb-1`} />
    <p className="text-base font-bold text-white">{value}</p>
    <p className="text-[9px] text-zinc-500 uppercase">{label}</p>
  </div>
);

export default ProjectDetail;
