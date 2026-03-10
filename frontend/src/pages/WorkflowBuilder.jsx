import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "../App";
import { Plus, Save, Trash2, Play, Search, GripVertical, X, ArrowRight, ChevronDown, Settings } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

const NET_COLORS = {
  core_platform: "#10b981", strategic_executive: "#a855f7", venture_creation: "#3b82f6",
  product_development: "#06b6d4", engineering: "#f59e0b", creative_brand: "#ec4899",
  growth_distribution: "#22c55e", sales_revenue: "#f97316", customer_experience: "#14b8a6",
  operations: "#6366f1", finance_capital: "#eab308", research_intelligence: "#0ea5e9",
  simulation_foresight: "#d946ef", security: "#ef4444", execution: "#f97316",
};
const NET_LABELS = {
  core_platform: "Core", strategic_executive: "Strategic", venture_creation: "Venture",
  product_development: "Product", engineering: "Engineering", creative_brand: "Creative",
  growth_distribution: "Growth", sales_revenue: "Sales", customer_experience: "Customer",
  operations: "Operations", finance_capital: "Finance", research_intelligence: "Research",
  simulation_foresight: "Simulation", security: "Security", execution: "Execution",
  investment_portfolio: "Investment", legal_governance: "Legal", memory_knowledge: "Memory",
  tooling_capability: "Tooling", verification: "Verification", experimentation: "Experimentation",
  conflict_resolution: "Conflict", observability_incident: "Observability", recovery_resilience: "Recovery",
  communication_reporting: "Communication", web_search_intelligence: "Web Intel", industry_specific: "Industry",
};

export default function WorkflowBuilder() {
  const { token } = useAuth();
  const canvasRef = useRef(null);
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [current, setCurrent] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [wfName, setWfName] = useState("Untitled Workflow");
  const [wfDesc, setWfDesc] = useState("");
  const [loading, setLoading] = useState(true);
  const [agentSearch, setAgentSearch] = useState("");
  const [selectedNode, setSelectedNode] = useState(null);
  const [connecting, setConnecting] = useState(null);
  const [dragging, setDragging] = useState(null);
  const lastMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const h = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch(`${API}/api/agents`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/workflows`, { headers: h }).then(r => r.json()),
    ]).then(([ag, wf]) => {
      setAgents(Array.isArray(ag) ? ag : []);
      setWorkflows(Array.isArray(wf) ? wf : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const networkGroups = {};
  agents.forEach(a => {
    const net = a.network || "ungrouped";
    if (!networkGroups[net]) networkGroups[net] = [];
    networkGroups[net].push(a);
  });

  const filteredAgents = agentSearch
    ? agents.filter(a => a.name.toLowerCase().includes(agentSearch.toLowerCase()) || a.role.toLowerCase().includes(agentSearch.toLowerCase())).slice(0, 20)
    : [];

  const addNode = (agent, x, y) => {
    const id = `node_${Date.now()}`;
    setNodes(prev => [...prev, { id, agent_id: agent.agent_id, name: agent.name, role: agent.role, network: agent.network, avatar: agent.avatar, x: x || 300 + Math.random() * 400, y: y || 100 + nodes.length * 80 }]);
  };

  const removeNode = (nodeId) => {
    setNodes(prev => prev.filter(n => n.id !== nodeId));
    setEdges(prev => prev.filter(e => e.source !== nodeId && e.target !== nodeId));
    if (selectedNode === nodeId) setSelectedNode(null);
  };

  const addEdge = (source, target) => {
    if (source === target) return;
    if (edges.find(e => e.source === source && e.target === target)) return;
    setEdges(prev => [...prev, { id: `edge_${Date.now()}`, source, target }]);
  };

  const saveWorkflow = async () => {
    const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
    const body = { name: wfName, description: wfDesc, nodes, edges };
    if (current) {
      const res = await fetch(`${API}/api/kernel/workflows/${current}`, { method: "PUT", headers: h, body: JSON.stringify(body) });
      if (res.ok) {
        const wfs = await fetch(`${API}/api/kernel/workflows`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json());
        setWorkflows(wfs);
      }
    } else {
      const res = await fetch(`${API}/api/kernel/workflows`, { method: "POST", headers: h, body: JSON.stringify(body) });
      if (res.ok) {
        const wf = await res.json();
        setCurrent(wf.workflow_id);
        const wfs = await fetch(`${API}/api/kernel/workflows`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json());
        setWorkflows(wfs);
      }
    }
  };

  const loadWorkflow = (wf) => {
    setCurrent(wf.workflow_id);
    setWfName(wf.name);
    setWfDesc(wf.description || "");
    setNodes(wf.nodes || []);
    setEdges(wf.edges || []);
    setSelectedNode(null);
  };

  const newWorkflow = () => {
    setCurrent(null);
    setWfName("Untitled Workflow");
    setWfDesc("");
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
  };

  const deleteWorkflow = async (wfId) => {
    await fetch(`${API}/api/kernel/workflows/${wfId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    setWorkflows(prev => prev.filter(w => w.workflow_id !== wfId));
    if (current === wfId) newWorkflow();
  };

  const onCanvasMouseDown = (e) => {
    if (connecting && e.target === canvasRef.current?.firstChild) {
      setConnecting(null);
    }
  };

  const onNodeMouseDown = (e, nodeId) => {
    e.stopPropagation();
    if (connecting) {
      addEdge(connecting, nodeId);
      setConnecting(null);
      return;
    }
    setSelectedNode(nodeId);
    setDragging(nodeId);
    lastMouse.current = { x: e.clientX, y: e.clientY };
  };

  const onMouseMove = useCallback((e) => {
    if (!dragging) return;
    const dx = e.clientX - lastMouse.current.x;
    const dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    setNodes(prev => prev.map(n => n.id === dragging ? { ...n, x: n.x + dx, y: n.y + dy } : n));
  }, [dragging]);

  const onMouseUp = useCallback(() => { setDragging(null); }, []);

  useEffect(() => {
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => { window.removeEventListener("mousemove", onMouseMove); window.removeEventListener("mouseup", onMouseUp); };
  }, [onMouseMove, onMouseUp]);

  // Handle drag from palette  
  const onDragStart = (e, agent) => { e.dataTransfer.setData("agent", JSON.stringify(agent)); };
  const onDrop = (e) => {
    e.preventDefault();
    const data = e.dataTransfer.getData("agent");
    if (!data) return;
    const agent = JSON.parse(data);
    const rect = canvasRef.current.getBoundingClientRect();
    addNode(agent, e.clientX - rect.left, e.clientY - rect.top);
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="flex h-[calc(100vh-80px)] gap-0" data-testid="workflow-builder">
      {/* Agent Palette */}
      <div className="w-56 bg-zinc-900/60 border-r border-white/5 flex flex-col shrink-0" data-testid="agent-palette">
        <div className="p-3 border-b border-white/5">
          <p className="text-xs font-semibold text-zinc-400 mb-2">Agent Palette</p>
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500" />
            <input type="text" placeholder="Search agents..." value={agentSearch} onChange={e => setAgentSearch(e.target.value)}
              className="w-full bg-zinc-800/50 border border-white/5 rounded pl-7 pr-2 py-1.5 text-[11px] text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30"
              data-testid="wf-agent-search" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {agentSearch ? (
            filteredAgents.map(a => (
              <div key={a.agent_id} draggable onDragStart={e => onDragStart(e, a)}
                className="flex items-center gap-2 px-2 py-1.5 rounded cursor-grab hover:bg-white/5 active:cursor-grabbing"
                data-testid={`palette-agent-${a.agent_id}`}>
                {a.avatar ? <img src={a.avatar} alt="" className="w-5 h-5 rounded object-cover" /> : <div className="w-5 h-5 rounded bg-zinc-700 flex items-center justify-center text-[7px] font-bold text-zinc-400">{a.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>}
                <div className="flex-1 min-w-0"><p className="text-[10px] text-white truncate">{a.name}</p></div>
                <GripVertical className="w-3 h-3 text-zinc-600" />
              </div>
            ))
          ) : (
            Object.entries(networkGroups).sort((a, b) => a[0].localeCompare(b[0])).slice(0, 12).map(([net, netAgents]) => (
              <div key={net} className="mb-2">
                <p className="text-[9px] font-semibold uppercase tracking-wider px-2 py-1" style={{ color: NET_COLORS[net] || "#6366f1" }}>
                  {NET_LABELS[net] || net} ({netAgents.length})
                </p>
                {netAgents.slice(0, 3).map(a => (
                  <div key={a.agent_id} draggable onDragStart={e => onDragStart(e, a)}
                    className="flex items-center gap-2 px-2 py-1 rounded cursor-grab hover:bg-white/5 active:cursor-grabbing"
                    data-testid={`palette-agent-${a.agent_id}`}>
                    {a.avatar ? <img src={a.avatar} alt="" className="w-4 h-4 rounded object-cover" /> : <div className="w-4 h-4 rounded bg-zinc-700 flex items-center justify-center text-[6px] font-bold text-zinc-400">{a.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>}
                    <span className="text-[9px] text-zinc-400 truncate flex-1">{a.name}</span>
                    <GripVertical className="w-2.5 h-2.5 text-zinc-700" />
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5 bg-zinc-900/30" data-testid="wf-toolbar">
          <input type="text" value={wfName} onChange={e => setWfName(e.target.value)}
            className="bg-transparent border-b border-transparent hover:border-white/10 focus:border-indigo-500/50 text-sm font-semibold text-white px-1 py-0.5 focus:outline-none max-w-xs"
            data-testid="wf-name-input" />
          <span className="text-[10px] text-zinc-600">{nodes.length} nodes, {edges.length} edges</span>
          <div className="flex-1" />
          {connecting && <span className="text-[10px] text-amber-400 animate-pulse">Click a node to connect...</span>}
          <Button size="sm" variant="outline" className="h-7 text-[10px] border-white/10" onClick={newWorkflow} data-testid="wf-new"><Plus className="w-3 h-3 mr-1" /> New</Button>
          <Button size="sm" className="h-7 text-[10px] bg-indigo-600 hover:bg-indigo-700" onClick={saveWorkflow} data-testid="wf-save"><Save className="w-3 h-3 mr-1" /> Save</Button>
        </div>

        {/* Canvas */}
        <div ref={canvasRef} className="flex-1 relative overflow-auto bg-zinc-950/30" style={{ backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)", backgroundSize: "24px 24px" }}
          onDrop={onDrop} onDragOver={e => e.preventDefault()} onMouseDown={onCanvasMouseDown} data-testid="wf-canvas">
          {/* Edge Lines (via Canvas) */}
          <EdgeCanvas nodes={nodes} edges={edges} />
          {/* Nodes */}
          {nodes.map(node => {
            const color = NET_COLORS[node.network] || "#6366f1";
            const isSel = selectedNode === node.id;
            const isConn = connecting === node.id;
            return (
              <div key={node.id} style={{ position: "absolute", left: `${node.x}px`, top: `${node.y}px`, zIndex: isSel ? 10 : 1 }}
                onMouseDown={e => onNodeMouseDown(e, node.id)} data-testid={`wf-node-${node.id}`}>
                <div className={`w-44 rounded-xl border-2 transition-all cursor-pointer ${isSel ? "border-white/30 shadow-lg" : isConn ? "border-amber-400/50 shadow-amber-500/10" : "border-white/5 hover:border-white/10"}`}
                  style={{ borderColor: isSel ? color : undefined, boxShadow: isSel ? `0 0 16px ${color}30` : undefined }}>
                  <div className="px-3 py-2 rounded-t-xl" style={{ backgroundColor: `${color}15` }}>
                    <div className="flex items-center gap-2">
                      {node.avatar ? <img src={node.avatar} alt="" className="w-6 h-6 rounded object-cover" /> : <div className="w-6 h-6 rounded flex items-center justify-center text-[8px] font-bold" style={{ backgroundColor: `${color}30`, color }}>{node.name.split(" ").map(w => w[0]).join("").slice(0, 2)}</div>}
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-medium text-white truncate">{node.name}</p>
                        <p className="text-[8px] truncate" style={{ color }}>{NET_LABELS[node.network] || node.network}</p>
                      </div>
                    </div>
                  </div>
                  <div className="px-3 py-1.5 bg-zinc-900/80 rounded-b-xl">
                    <p className="text-[9px] text-zinc-500 truncate">{node.role}</p>
                  </div>
                </div>
                {/* Connect / Delete buttons */}
                {isSel && (
                  <div className="absolute -top-2 -right-2 flex gap-1">
                    <button onClick={(e) => { e.stopPropagation(); setConnecting(node.id); }} className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center hover:bg-amber-400" title="Connect" data-testid={`wf-connect-${node.id}`}>
                      <ArrowRight className="w-3 h-3 text-black" />
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); removeNode(node.id); }} className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center hover:bg-red-400" title="Delete" data-testid={`wf-delete-${node.id}`}>
                      <X className="w-3 h-3 text-black" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center" data-testid="wf-empty">
              <div className="text-center">
                <p className="text-zinc-600 text-sm">Drag agents from the palette to build your workflow</p>
                <p className="text-zinc-700 text-xs mt-1">Click a node, then click the arrow to connect agents</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Saved Workflows Sidebar */}
      <div className="w-48 bg-zinc-900/60 border-l border-white/5 flex flex-col shrink-0" data-testid="wf-saved-list">
        <div className="p-3 border-b border-white/5">
          <p className="text-xs font-semibold text-zinc-400">Saved Workflows</p>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {workflows.map(wf => (
            <div key={wf.workflow_id} className={`group flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-colors ${current === wf.workflow_id ? "bg-indigo-500/10 text-indigo-400" : "hover:bg-white/[0.04] text-zinc-400"}`}
              onClick={() => loadWorkflow(wf)} data-testid={`wf-item-${wf.workflow_id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] truncate">{wf.name}</p>
                <p className="text-[9px] text-zinc-600">{(wf.nodes || []).length} nodes</p>
              </div>
              <button onClick={e => { e.stopPropagation(); deleteWorkflow(wf.workflow_id); }} className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400" data-testid={`wf-delete-item-${wf.workflow_id}`}>
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
          {workflows.length === 0 && <p className="text-[10px] text-zinc-600 text-center py-4">No saved workflows</p>}
        </div>
      </div>
    </div>
  );
}

// Separate component for edge rendering using HTML5 Canvas
function EdgeCanvas({ nodes, edges }) {
  const canvasEl = useRef(null);
  useEffect(() => {
    const canvas = canvasEl.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = parent.scrollWidth * dpr;
    canvas.height = parent.scrollHeight * dpr;
    canvas.style.width = parent.scrollWidth + "px";
    canvas.style.height = parent.scrollHeight + "px";
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, parent.scrollWidth, parent.scrollHeight);

    const nodeMap = {};
    nodes.forEach(n => { nodeMap[n.id] = n; });

    edges.forEach(e => {
      const s = nodeMap[e.source], t = nodeMap[e.target];
      if (!s || !t) return;
      const sx = s.x + 88, sy = s.y + 30;
      const tx = t.x + 88, ty = t.y + 30;
      const color = NET_COLORS[s.network] || "#6366f1";

      ctx.beginPath();
      const cpx1 = sx + (tx - sx) * 0.5;
      const cpy1 = sy;
      const cpx2 = tx - (tx - sx) * 0.5;
      const cpy2 = ty;
      ctx.moveTo(sx, sy);
      ctx.bezierCurveTo(cpx1, cpy1, cpx2, cpy2, tx, ty);
      ctx.strokeStyle = color;
      ctx.globalAlpha = 0.5;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Arrow
      const angle = Math.atan2(ty - cpy2, tx - cpx2);
      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(tx - 8 * Math.cos(angle - 0.3), ty - 8 * Math.sin(angle - 0.3));
      ctx.lineTo(tx - 8 * Math.cos(angle + 0.3), ty - 8 * Math.sin(angle + 0.3));
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.6;
      ctx.fill();
      ctx.globalAlpha = 1;
    });
  }, [nodes, edges]);

  return <canvas ref={canvasEl} style={{ position: "absolute", top: 0, left: 0, pointerEvents: "none", zIndex: 0 }} />;
}
