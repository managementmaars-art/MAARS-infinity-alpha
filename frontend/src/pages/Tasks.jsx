import { useState, useEffect } from "react";
import { Bot, Plus, Play, Trash2, CheckCircle, Clock, AlertCircle, Shield, ListTodo, X, ChevronDown } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  bg: "#030712",
  glass: "rgba(255,255,255,0.03)",
  glass2: "rgba(255,255,255,0.06)",
  border: "rgba(255,255,255,0.08)",
  teal: "#4fd1c5",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  orange: "#f97316",
  zinc: "#71717a",
};

const PRIORITY_META = {
  critical: { color: T.red, bg: "rgba(239,68,68,0.12)", label: "Critical" },
  high:     { color: T.orange, bg: "rgba(249,115,22,0.12)", label: "High" },
  medium:   { color: T.amber, bg: "rgba(245,158,11,0.12)", label: "Medium" },
  low:      { color: T.zinc, bg: "rgba(113,113,122,0.12)", label: "Low" },
};

const STATUS_META = {
  completed:  { color: T.green,  icon: CheckCircle, label: "Completed" },
  in_progress:{ color: T.amber,  icon: Clock,       label: "Running" },
  pending:    { color: T.zinc,   icon: AlertCircle, label: "Pending" },
  failed:     { color: T.red,    icon: AlertCircle, label: "Failed" },
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
@keyframes slideIn { from{opacity:0;transform:scale(.96)} to{opacity:1;transform:scale(1)} }
`;

const glass = {
  background: T.glass,
  border: `1px solid ${T.border}`,
  borderRadius: 16,
  backdropFilter: "blur(12px)",
};

const glassInput = {
  width: "100%",
  background: "rgba(255,255,255,0.04)",
  border: `1px solid ${T.border}`,
  borderRadius: 10,
  padding: "9px 12px",
  color: "#fff",
  fontSize: 13,
  outline: "none",
  fontFamily: "inherit",
  boxSizing: "border-box",
};

const Tasks = () => {
  const { user, token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [executing, setExecuting] = useState(null);
  const [filter, setFilter] = useState("all");
  const [expandedResult, setExpandedResult] = useState(null);

  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "medium",
    assigned_agents: [],
  });

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [tasksRes, agentsRes] = await Promise.all([
        fetch(`${API}/tasks`, { headers }).catch(() => null),
        fetch(`${API}/agents`, { headers }).catch(() => null),
      ]);
      if (tasksRes?.ok) setTasks(await tasksRes.json());
      if (agentsRes?.ok) setAgents(await agentsRes.json());
    } catch { toast.error("Failed to load data"); }
    finally { setLoading(false); }
  };

  const createTask = async (e) => {
    e.preventDefault();
    if (!newTask.title || !newTask.description) { toast.error("Fill in all required fields"); return; }
    try {
      const res = await fetch(`${API}/tasks`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });
      if (res.ok) {
        const created = await res.json();
        setTasks(prev => [created, ...prev]);
        setNewTask({ title: "", description: "", priority: "medium", assigned_agents: [] });
        setModalOpen(false);
        toast.success("Task created!");
      } else toast.error("Failed to create task");
    } catch { toast.error("Failed to create task"); }
  };

  const executeTask = async (taskId) => {
    setExecuting(taskId);
    try {
      const res = await fetch(`${API}/tasks/${taskId}/execute`, { method: "POST", headers });
      if (res.ok) {
        const result = await res.json();
        setTasks(prev => prev.map(t => t.task_id === taskId ? { ...t, status: "completed", result: result.result } : t));
        toast.success("Task completed!");
      } else toast.error("Failed to execute task");
    } catch { toast.error("Failed to execute task"); }
    finally { setExecuting(null); }
  };

  const deleteTask = async (taskId) => {
    try {
      const res = await fetch(`${API}/tasks/${taskId}`, { method: "DELETE", headers });
      if (res.ok) { setTasks(prev => prev.filter(t => t.task_id !== taskId)); toast.success("Task deleted"); }
    } catch { toast.error("Failed to delete task"); }
  };

  const toggleAgent = (agentId) => {
    setNewTask(prev => ({
      ...prev,
      assigned_agents: prev.assigned_agents.includes(agentId)
        ? prev.assigned_agents.filter(id => id !== agentId)
        : [...prev.assigned_agents, agentId],
    }));
  };

  const FILTERS = [
    { v: "all", l: "All" },
    { v: "pending", l: "Pending" },
    { v: "in_progress", l: "Running" },
    { v: "completed", l: "Done" },
  ];

  const filtered = filter === "all" ? tasks : tasks.filter(t => t.status === filter);

  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === "pending").length,
    running: tasks.filter(t => t.status === "in_progress").length,
    done: tasks.filter(t => t.status === "completed").length,
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 300 }}>
      <div style={{ width: 32, height: 32, borderRadius: "50%", border: `2px solid ${T.teal}`, borderTopColor: "transparent", animation: "spin 0.8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  return (
    <div data-testid="tasks-page" style={{ animation: "fadeUp .4s ease" }}>
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28, gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 28, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>AI Tasks</h1>
          <p style={{ color: T.zinc, fontSize: 14, margin: 0 }}>Assign tasks to your AI team and track autonomous execution</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          data-testid="create-task-btn"
          style={{
            display: "flex", alignItems: "center", gap: 8,
            background: `linear-gradient(135deg, ${T.violet}, #9333ea)`,
            border: "none", borderRadius: 12, padding: "10px 20px",
            color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer",
            boxShadow: `0 0 24px rgba(124,58,237,0.35)`,
          }}
        >
          <Plus size={16} /> New Task
        </button>
      </div>

      {/* Quick Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
        {[
          { label: "Total", value: stats.total, color: T.teal },
          { label: "Pending", value: stats.pending, color: T.zinc },
          { label: "Running", value: stats.running, color: T.amber },
          { label: "Completed", value: stats.done, color: T.green },
        ].map(s => (
          <div key={s.label} style={{ ...glass, padding: "14px 16px", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color, borderRadius: "16px 16px 0 0" }} />
            <div style={{ fontSize: 22, fontWeight: 700, color: "#fff", lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 11, color: T.zinc, marginTop: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 20 }}>
        {FILTERS.map(f => (
          <button
            key={f.v}
            onClick={() => setFilter(f.v)}
            style={{
              padding: "6px 16px", borderRadius: 20, fontSize: 12, fontWeight: 500, cursor: "pointer",
              background: filter === f.v ? `rgba(79,209,197,0.15)` : "transparent",
              border: filter === f.v ? `1px solid rgba(79,209,197,0.4)` : `1px solid ${T.border}`,
              color: filter === f.v ? T.teal : T.zinc,
              transition: "all .2s",
            }}
          >
            {f.l} {f.v !== "all" && <span style={{ opacity: .7 }}>({tasks.filter(t => t.status === f.v).length})</span>}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      {filtered.length === 0 ? (
        <div style={{ ...glass, padding: 48, textAlign: "center" }}>
          <ListTodo size={48} style={{ color: "rgba(255,255,255,.12)", marginBottom: 16 }} />
          <h3 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 18, color: "#fff", margin: "0 0 8px" }}>
            {filter === "all" ? "No Tasks Yet" : `No ${filter} tasks`}
          </h3>
          <p style={{ color: T.zinc, fontSize: 14, margin: "0 0 20px" }}>
            {filter === "all" ? "Create your first task and assign AI agents to execute it." : "All clear in this category."}
          </p>
          {filter === "all" && (
            <button
              onClick={() => setModalOpen(true)}
              style={{
                background: `linear-gradient(135deg, ${T.violet}, #9333ea)`,
                border: "none", borderRadius: 12, padding: "10px 24px",
                color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer",
              }}
            >
              <Plus size={14} style={{ verticalAlign: "middle", marginRight: 6 }} />
              Create Your First Task
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {filtered.map((task) => {
            const sm = STATUS_META[task.status] || STATUS_META.pending;
            const pm = PRIORITY_META[task.priority] || PRIORITY_META.medium;
            const StatusIcon = sm.icon;
            const isExpanded = expandedResult === task.task_id;
            return (
              <div
                key={task.task_id}
                data-testid={`task-card-${task.task_id}`}
                style={{ ...glass, padding: 16, position: "relative", overflow: "hidden", transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.14)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
              >
                {/* Left color bar */}
                <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: sm.color, borderRadius: "16px 0 0 16px" }} />

                <div style={{ display: "flex", gap: 14, paddingLeft: 4 }}>
                  {/* Status icon */}
                  <div style={{ paddingTop: 2, flexShrink: 0 }}>
                    <StatusIcon size={18} style={{ color: sm.color, animation: task.status === "in_progress" ? "pulse 1.5s infinite" : "none" }} />
                  </div>

                  {/* Content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, color: "#fff", fontSize: 15 }}>{task.title}</span>
                      {/* Priority badge */}
                      <span style={{ background: pm.bg, color: pm.color, fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 6, textTransform: "uppercase", letterSpacing: ".05em" }}>
                        {pm.label}
                      </span>
                      {/* Status badge */}
                      <span style={{ background: `${sm.color}18`, color: sm.color, fontSize: 10, fontWeight: 500, padding: "2px 8px", borderRadius: 6 }}>
                        {task.status === "in_progress" ? "Working..." : sm.label}
                      </span>
                      {task.source === "commander" && (
                        <span data-testid="commander-badge" style={{ display: "flex", alignItems: "center", gap: 4, background: "rgba(245,158,11,0.12)", color: T.amber, fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 6 }}>
                          <Shield size={10} /> Commander
                        </span>
                      )}
                    </div>

                    <p style={{ color: T.zinc, fontSize: 13, margin: "0 0 10px", lineHeight: 1.5 }}>{task.description}</p>

                    {task.source === "commander" && task.source_goal && (
                      <p style={{ color: "rgba(113,113,122,.7)", fontSize: 11, fontStyle: "italic", margin: "0 0 8px" }}>Goal: "{task.source_goal}"</p>
                    )}

                    {/* Assigned agents */}
                    {task.assigned_agents?.length > 0 && (
                      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginBottom: 10 }}>
                        <span style={{ fontSize: 11, color: T.zinc }}>Assigned:</span>
                        {task.assigned_agents.map((agentId) => {
                          const agent = agents.find(a => a.agent_id === agentId);
                          return agent ? (
                            <div key={agentId} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px", borderRadius: 8, background: "rgba(255,255,255,0.05)", border: `1px solid ${T.border}` }}>
                              <img src={agent.avatar} alt={agent.name} style={{ width: 18, height: 18, borderRadius: "50%", objectFit: "cover" }} />
                              <span style={{ fontSize: 11, color: "#e4e4e7" }}>{agent.name}</span>
                              <span style={{ fontSize: 10, color: T.zinc }}>· {agent.role}</span>
                            </div>
                          ) : null;
                        })}
                      </div>
                    )}

                    {/* Result */}
                    {task.result && (
                      <div>
                        <button
                          onClick={() => setExpandedResult(isExpanded ? null : task.task_id)}
                          style={{ display: "flex", alignItems: "center", gap: 4, background: "none", border: "none", color: T.teal, fontSize: 12, cursor: "pointer", padding: 0, marginBottom: 6 }}
                        >
                          <ChevronDown size={14} style={{ transform: isExpanded ? "rotate(180deg)" : "none", transition: ".2s" }} />
                          {isExpanded ? "Hide" : "View"} Result
                        </button>
                        {isExpanded && (
                          <div style={{ background: "rgba(0,0,0,0.3)", borderRadius: 10, border: `1px solid ${T.border}`, padding: "12px 14px", maxHeight: 180, overflowY: "auto" }}>
                            <p style={{ fontSize: 12, color: "#d4d4d8", whiteSpace: "pre-wrap", margin: 0, lineHeight: 1.6 }}>{task.result}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div style={{ display: "flex", gap: 6, alignItems: "flex-start", flexShrink: 0 }}>
                    {task.status === "pending" && task.assigned_agents?.length > 0 && (
                      <button
                        onClick={() => executeTask(task.task_id)}
                        disabled={executing === task.task_id}
                        data-testid={`execute-task-${task.task_id}`}
                        style={{
                          display: "flex", alignItems: "center", justifyContent: "center",
                          width: 32, height: 32, borderRadius: 8,
                          background: "rgba(52,211,153,0.15)", border: `1px solid rgba(52,211,153,0.3)`,
                          cursor: executing === task.task_id ? "not-allowed" : "pointer",
                          color: T.green, opacity: executing === task.task_id ? .6 : 1,
                        }}
                      >
                        {executing === task.task_id
                          ? <div style={{ width: 14, height: 14, border: `2px solid ${T.green}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
                          : <Play size={14} />
                        }
                      </button>
                    )}
                    <button
                      onClick={() => deleteTask(task.task_id)}
                      data-testid={`delete-task-${task.task_id}`}
                      style={{
                        display: "flex", alignItems: "center", justifyContent: "center",
                        width: 32, height: 32, borderRadius: 8,
                        background: "transparent", border: `1px solid ${T.border}`,
                        cursor: "pointer", color: T.zinc,
                        transition: "all .2s",
                      }}
                      onMouseEnter={e => { e.currentTarget.style.color = T.red; e.currentTarget.style.borderColor = "rgba(239,68,68,.3)"; e.currentTarget.style.background = "rgba(239,68,68,.08)"; }}
                      onMouseLeave={e => { e.currentTarget.style.color = T.zinc; e.currentTarget.style.borderColor = T.border; e.currentTarget.style.background = "transparent"; }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Task Modal */}
      {modalOpen && (
        <div
          style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,.7)", backdropFilter: "blur(8px)" }}
          onClick={e => e.target === e.currentTarget && setModalOpen(false)}
        >
          <div style={{ background: "#0d1117", border: `1px solid ${T.border}`, borderRadius: 20, width: "100%", maxWidth: 520, maxHeight: "90vh", overflowY: "auto", padding: "28px 28px", animation: "slideIn .2s ease", boxShadow: "0 25px 60px rgba(0,0,0,.5)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
              <h2 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 20, fontWeight: 700, color: "#fff", margin: 0 }}>Create New Task</h2>
              <button onClick={() => setModalOpen(false)} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4 }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={createTask} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div>
                <label style={{ display: "block", fontSize: 12, color: T.zinc, marginBottom: 6, fontWeight: 500 }}>Title *</label>
                <input
                  value={newTask.title}
                  onChange={e => setNewTask(p => ({ ...p, title: e.target.value }))}
                  placeholder="Task title..."
                  style={glassInput}
                  required
                  data-testid="task-title-input"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: 12, color: T.zinc, marginBottom: 6, fontWeight: 500 }}>Description *</label>
                <textarea
                  value={newTask.description}
                  onChange={e => setNewTask(p => ({ ...p, description: e.target.value }))}
                  placeholder="Describe the task in detail..."
                  rows={4}
                  style={{ ...glassInput, resize: "vertical", lineHeight: 1.6 }}
                  required
                  data-testid="task-description-input"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: 12, color: T.zinc, marginBottom: 8, fontWeight: 500 }}>Priority</label>
                <div style={{ display: "flex", gap: 8 }}>
                  {Object.entries(PRIORITY_META).map(([v, meta]) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setNewTask(p => ({ ...p, priority: v }))}
                      data-testid="task-priority-select"
                      style={{
                        flex: 1, padding: "8px 4px", borderRadius: 10, fontSize: 11, fontWeight: 600,
                        cursor: "pointer", textTransform: "uppercase", letterSpacing: ".04em",
                        background: newTask.priority === v ? meta.bg : "rgba(255,255,255,0.03)",
                        border: newTask.priority === v ? `1px solid ${meta.color}60` : `1px solid ${T.border}`,
                        color: newTask.priority === v ? meta.color : T.zinc,
                        transition: "all .15s",
                      }}
                    >
                      {meta.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: 12, color: T.zinc, marginBottom: 8, fontWeight: 500 }}>
                  Assign Agents <span style={{ color: "rgba(113,113,122,.6)" }}>({newTask.assigned_agents.length} selected)</span>
                </label>
                <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6, padding: "2px 0" }}>
                  {agents.map(agent => {
                    const selected = newTask.assigned_agents.includes(agent.agent_id);
                    return (
                      <button
                        key={agent.agent_id}
                        type="button"
                        onClick={() => toggleAgent(agent.agent_id)}
                        data-testid={`assign-agent-${agent.agent_id}`}
                        style={{
                          display: "flex", alignItems: "center", gap: 10,
                          padding: "8px 12px", borderRadius: 10, cursor: "pointer",
                          background: selected ? "rgba(79,209,197,0.08)" : "rgba(255,255,255,0.03)",
                          border: selected ? `1px solid rgba(79,209,197,0.4)` : `1px solid ${T.border}`,
                          transition: "all .15s", textAlign: "left",
                        }}
                      >
                        <img src={agent.avatar} alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover", flexShrink: 0 }} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 13, color: selected ? T.teal : "#e4e4e7", fontWeight: selected ? 600 : 400 }}>{agent.name}</div>
                          <div style={{ fontSize: 11, color: T.zinc }}>{agent.role}</div>
                        </div>
                        {selected && <CheckCircle size={14} style={{ color: T.teal, flexShrink: 0 }} />}
                      </button>
                    );
                  })}
                  {agents.length === 0 && <p style={{ color: T.zinc, fontSize: 12, textAlign: "center", padding: "12px 0" }}>No agents available</p>}
                </div>
              </div>

              <div style={{ display: "flex", gap: 10, paddingTop: 4 }}>
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  style={{
                    flex: 1, padding: "11px 0", borderRadius: 12, fontSize: 14, fontWeight: 500, cursor: "pointer",
                    background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: T.zinc,
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  data-testid="submit-task-btn"
                  style={{
                    flex: 2, padding: "11px 0", borderRadius: 12, fontSize: 14, fontWeight: 600, cursor: "pointer",
                    background: `linear-gradient(135deg, ${T.violet}, #9333ea)`,
                    border: "none", color: "#fff",
                    boxShadow: `0 0 20px rgba(124,58,237,0.3)`,
                  }}
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;
