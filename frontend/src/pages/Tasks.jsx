import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { ScrollArea } from "../components/ui/scroll-area";
import { Bot, Plus, Play, Trash2, CheckCircle, Clock, AlertCircle,
  LayoutDashboard, Users, MessageSquare, ListTodo, Settings, LogOut, Menu, X,
  Shield, Package
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const Tasks = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(null);
  
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "medium",
    assigned_agents: []
  });

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tasksRes, agentsRes] = await Promise.all([
        fetch(`${API}/tasks`, { headers }).catch(() => null),
        fetch(`${API}/agents`, { headers }).catch(() => null)
      ]);

      if (tasksRes?.ok) setTasks(await tasksRes.json());
      if (agentsRes?.ok) setAgents(await agentsRes.json());
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    
    if (!newTask.title || !newTask.description) {
      toast.error("Please fill in all required fields");
      return;
    }

    try {
      const response = await fetch(`${API}/tasks`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify(newTask)
      });

      if (response.ok) {
        const task = await response.json();
        setTasks(prev => [task, ...prev]);
        setNewTask({ title: "", description: "", priority: "medium", assigned_agents: [] });
        setCreateDialogOpen(false);
        toast.success("Task created!");
      } else {
        toast.error("Failed to create task");
      }
    } catch (error) {
      toast.error("Failed to create task");
    }
  };

  const executeTask = async (taskId) => {
    setExecuting(taskId);
    
    try {
      const response = await fetch(`${API}/tasks/${taskId}/execute`, {
        method: "POST", headers
      });

      if (response.ok) {
        const result = await response.json();
        setTasks(prev => prev.map(t => 
          t.task_id === taskId 
            ? { ...t, status: "completed", result: result.result }
            : t
        ));
        toast.success("Task completed!");
      } else {
        toast.error("Failed to execute task");
      }
    } catch (error) {
      toast.error("Failed to execute task");
    } finally {
      setExecuting(null);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      const response = await fetch(`${API}/tasks/${taskId}`, {
        method: "DELETE", headers
      });

      if (response.ok) {
        setTasks(prev => prev.filter(t => t.task_id !== taskId));
        toast.success("Task deleted");
      }
    } catch (error) {
      toast.error("Failed to delete task");
    }
  };

  const toggleAgent = (agentId) => {
    setNewTask(prev => ({
      ...prev,
      assigned_agents: prev.assigned_agents.includes(agentId)
        ? prev.assigned_agents.filter(id => id !== agentId)
        : [...prev.assigned_agents, agentId]
    }));
  };
  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case "in_progress":
        return <Clock className="w-5 h-5 text-amber-400 animate-pulse" />;
      default:
        return <AlertCircle className="w-5 h-5 text-zinc-400" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "bg-red-500/20 text-red-300";
      case "low":
        return "bg-zinc-500/20 text-zinc-300";
      default:
        return "bg-amber-500/20 text-amber-300";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="tasks-page">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
                AI Tasks
              </h1>
              <p className="text-zinc-400">Assign tasks to your AI team and track progress</p>
            </div>
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
                  data-testid="create-task-btn"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Task
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-zinc-900 border-white/10 max-w-lg">
                <DialogHeader>
                  <DialogTitle className="text-white font-['Outfit']">Create New Task</DialogTitle>
                </DialogHeader>
                <form onSubmit={createTask} className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label className="text-zinc-300">Title *</Label>
                    <Input
                      value={newTask.title}
                      onChange={(e) => setNewTask(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Task title..."
                      className="bg-zinc-800/50 border-white/10"
                      required
                      data-testid="task-title-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-zinc-300">Description *</Label>
                    <Textarea
                      value={newTask.description}
                      onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe the task in detail..."
                      className="bg-zinc-800/50 border-white/10 min-h-[100px]"
                      required
                      data-testid="task-description-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-zinc-300">Priority</Label>
                    <Select
                      value={newTask.priority}
                      onValueChange={(value) => setNewTask(prev => ({ ...prev, priority: value }))}
                    >
                      <SelectTrigger className="bg-zinc-800/50 border-white/10" data-testid="task-priority-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-zinc-300">Assign Agents</Label>
                    <div className="max-h-48 overflow-y-auto rounded-lg border border-white/5 p-2">
                      <div className="flex flex-wrap gap-2">
                        {agents.map((agent) => (
                          <button
                            key={agent.agent_id}
                            type="button"
                            onClick={() => toggleAgent(agent.agent_id)}
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                              newTask.assigned_agents.includes(agent.agent_id)
                                ? "bg-indigo-500/20 ring-1 ring-indigo-500"
                                : "bg-zinc-800/50 hover:bg-zinc-800"
                            }`}
                            data-testid={`assign-agent-${agent.agent_id}`}
                          >
                            <img src={agent.avatar} alt="" className="w-6 h-6 rounded object-cover" />
                            <div className="text-left">
                              <span className="text-sm text-zinc-300 block leading-tight">{agent.name}</span>
                              <span className="text-[10px] text-zinc-500 block leading-tight">{agent.role}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      className="flex-1 border-white/10"
                      onClick={() => setCreateDialogOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500"
                      data-testid="submit-task-btn"
                    >
                      Create Task
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Tasks List */}
          {tasks.length === 0 ? (
            <div className="p-8 rounded-xl border border-dashed border-white/10 text-center">
              <ListTodo className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">
                No Tasks Yet
              </h3>
              <p className="text-zinc-400 mb-4">
                Create your first task and assign AI agents to complete it.
              </p>
              <Button
                onClick={() => setCreateDialogOpen(true)}
                className="bg-gradient-to-r from-indigo-500 to-violet-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Task
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {tasks.map((task) => (
                <Card
                  key={task.task_id}
                  className="bg-zinc-900/50 border-white/10"
                  data-testid={`task-card-${task.task_id}`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="pt-1">{getStatusIcon(task.status)}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <h3 className="font-semibold text-white">{task.title}</h3>
                          <Badge className={`${getPriorityColor(task.priority)} border-0 text-xs`}>
                            {task.priority}
                          </Badge>
                          <Badge className="bg-zinc-700 text-zinc-300 border-0 text-xs">
                            {task.status === "in_progress" ? "working on it..." : task.status.replace("_", " ")}
                          </Badge>
                          {task.source === "commander" && (
                            <Badge className="bg-amber-500/20 text-amber-400 border-0 text-xs flex items-center gap-1" data-testid="commander-badge">
                              <Shield className="w-3 h-3" />
                              Commander
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-zinc-400 mb-3">{task.description}</p>
                        {task.source === "commander" && task.source_goal && (
                          <p className="text-xs text-zinc-500 mb-2 italic">Goal: "{task.source_goal}"</p>
                        )}
                        
                        {task.assigned_agents?.length > 0 && (
                          <div className="flex items-center gap-2 mb-3 flex-wrap">
                            <span className="text-xs text-zinc-500">Assigned:</span>
                            {task.assigned_agents.map((agentId) => {
                              const agent = agents.find(a => a.agent_id === agentId);
                              return agent ? (
                                <div key={agentId} className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/5">
                                  <img
                                    src={agent.avatar}
                                    alt={agent.name}
                                    className="w-5 h-5 rounded-full object-cover"
                                  />
                                  <span className="text-xs text-zinc-300">{agent.name}</span>
                                  <span className="text-[10px] text-zinc-500">({agent.role})</span>
                                </div>
                              ) : null;
                            })}
                          </div>
                        )}

                        {task.result && (
                          <div className="mt-3 p-3 rounded-lg bg-zinc-800/50 border border-white/5">
                            <p className="text-xs text-zinc-500 mb-2">Result:</p>
                            <ScrollArea className="max-h-40">
                              <p className="text-sm text-zinc-300 whitespace-pre-wrap">{task.result}</p>
                            </ScrollArea>
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2">
                        {task.status === "pending" && task.assigned_agents?.length > 0 && (
                          <Button
                            size="sm"
                            onClick={() => executeTask(task.task_id)}
                            disabled={executing === task.task_id}
                            className="bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                            data-testid={`execute-task-${task.task_id}`}
                          >
                            {executing === task.task_id ? (
                              <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                            ) : (
                              <Play className="w-4 h-4" />
                            )}
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => deleteTask(task.task_id)}
                          className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10"
                          data-testid={`delete-task-${task.task_id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
    </div>
  );
};

export default Tasks;
