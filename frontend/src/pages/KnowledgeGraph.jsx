import { useState, useEffect, useRef } from "react";
import { useAuth } from "../App";
import { Search, ZoomIn, ZoomOut, Maximize2, X, Circle, ArrowRight } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const TYPE_COLORS = {
  network: { fill: "#6366f1", stroke: "#818cf8", bg: "bg-indigo-500/10", text: "text-indigo-400" },
  agent: { fill: "#10b981", stroke: "#34d399", bg: "bg-emerald-500/10", text: "text-emerald-400" },
  venture: { fill: "#f59e0b", stroke: "#fbbf24", bg: "bg-amber-500/10", text: "text-amber-400" },
  product: { fill: "#ec4899", stroke: "#f472b6", bg: "bg-pink-500/10", text: "text-pink-400" },
  market: { fill: "#06b6d4", stroke: "#22d3ee", bg: "bg-cyan-500/10", text: "text-cyan-400" },
  entity: { fill: "#8b5cf6", stroke: "#a78bfa", bg: "bg-violet-500/10", text: "text-violet-400" },
};

const REL_COLORS = {
  belongs_to: "#6366f1", supports: "#10b981", secures: "#ef4444", governs: "#f59e0b",
  drives: "#22c55e", creates_for: "#ec4899", informs: "#06b6d4", validates: "#8b5cf6",
  monitored_by: "#f97316", feeds: "#14b8a6", enables: "#84cc16", related_to: "#71717a",
};

function computeLayout(nodes) {
  const pos = {};
  const networks = nodes.filter(n => n.type === "network");
  const agents = nodes.filter(n => n.type === "agent");
  const cx = 550, cy = 420, radius = 340;
  networks.forEach((n, i) => {
    const angle = (2 * Math.PI * i) / networks.length - Math.PI / 2;
    pos[n.node_id] = { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) };
  });
  agents.forEach((a) => {
    const net = a.properties?.network;
    const netPos = pos[`net_${net}`];
    if (netPos) {
      const netAgents = agents.filter(ag => ag.properties?.network === net);
      const i = netAgents.indexOf(a);
      const angle = (2 * Math.PI * i) / Math.max(netAgents.length, 1);
      pos[a.node_id] = { x: netPos.x + 60 * Math.cos(angle), y: netPos.y + 60 * Math.sin(angle) };
    } else {
      pos[a.node_id] = { x: 100 + Math.random() * 900, y: 100 + Math.random() * 700 };
    }
  });
  return pos;
}

export default function KnowledgeGraph() {
  const { token } = useAuth();
  const canvasRef = useRef(null);
  const canvasElRef = useRef(null);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [positions, setPositions] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [zoom, setZoom] = useState(0.55);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [filterType, setFilterType] = useState("all");
  const [dragging, setDragging] = useState(null);
  const [isPanning, setIsPanning] = useState(false);
  const lastMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    fetch(`${API}/api/kernel/knowledge-graph`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        setGraph(data);
        setPositions(computeLayout(data.nodes));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  // Draw edges on canvas
  useEffect(() => {
    const canvas = canvasElRef.current;
    if (!canvas || !Object.keys(positions).length) return;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    canvas.width = 1200 * dpr;
    canvas.height = 900 * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, 1200, 900);

    const filteredIds = new Set(graph.nodes.filter(n => {
      if (filterType !== "all" && n.type !== filterType) return false;
      if (searchTerm && !n.label.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    }).map(n => n.node_id));

    graph.edges.forEach(e => {
      if (!filteredIds.has(e.source) || !filteredIds.has(e.target)) return;
      const s = positions[e.source], t = positions[e.target];
      if (!s || !t) return;
      const c = REL_COLORS[e.relationship] || "#71717a";
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = c;
      ctx.globalAlpha = 0.3;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.globalAlpha = 1;
    });
  }, [positions, graph, filterType, searchTerm]);

  const filteredNodes = graph.nodes.filter(n => {
    if (filterType !== "all" && n.type !== filterType) return false;
    if (searchTerm && !n.label.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });
  const nodeTypes = [...new Set(graph.nodes.map(n => n.type))];

  const onMouseDown = (e) => {
    lastMouse.current = { x: e.clientX, y: e.clientY };
    if (!dragging) setIsPanning(true);
  };
  const onMouseMove = (e) => {
    const dx = e.clientX - lastMouse.current.x;
    const dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    if (isPanning) setPan(p => ({ x: p.x + dx, y: p.y + dy }));
    if (dragging) {
      setPositions(prev => ({
        ...prev,
        [dragging]: { x: (prev[dragging]?.x || 0) + dx / zoom, y: (prev[dragging]?.y || 0) + dy / zoom },
      }));
    }
  };
  const onMouseUp = () => { setIsPanning(false); setDragging(null); };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-4" data-testid="knowledge-graph">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Knowledge Graph</h1>
          <p className="text-sm text-zinc-400 mt-1">{graph.nodes.length} nodes, {graph.edges.length} relationships, {nodeTypes.length} types</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input type="text" placeholder="Search nodes..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
              className="bg-zinc-900/60 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-zinc-500 w-52 focus:outline-none focus:border-indigo-500/50" data-testid="kg-search" />
          </div>
          <select value={filterType} onChange={e => setFilterType(e.target.value)}
            className="bg-zinc-900/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" data-testid="kg-type-filter">
            <option value="all">All Types</option>
            {nodeTypes.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
          </select>
          <div className="flex items-center gap-1 bg-zinc-900/60 border border-white/10 rounded-lg px-1">
            <button onClick={() => setZoom(z => Math.max(0.2, z - 0.1))} className="p-1.5 text-zinc-400 hover:text-white" data-testid="kg-zoom-out"><ZoomOut className="w-4 h-4" /></button>
            <span className="text-xs text-zinc-500 w-10 text-center">{Math.round(zoom * 100)}%</span>
            <button onClick={() => setZoom(z => Math.min(2, z + 0.1))} className="p-1.5 text-zinc-400 hover:text-white" data-testid="kg-zoom-in"><ZoomIn className="w-4 h-4" /></button>
            <button onClick={() => { setZoom(0.55); setPan({ x: 0, y: 0 }); }} className="p-1.5 text-zinc-400 hover:text-white" data-testid="kg-reset"><Maximize2 className="w-4 h-4" /></button>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3" data-testid="kg-legend">
        {Object.entries(TYPE_COLORS).filter(([k]) => nodeTypes.includes(k)).map(([type, c]) => (
          <div key={type} className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${c.bg} ${c.text} text-[11px] font-medium`}>
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.fill }} />
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </div>
        ))}
      </div>

      <div className="flex gap-4">
        <div ref={canvasRef} className="flex-1 bg-zinc-950/50 border border-white/5 rounded-xl overflow-hidden relative"
          style={{ height: "65vh", cursor: isPanning ? "grabbing" : "grab" }}
          onMouseDown={onMouseDown} onMouseMove={onMouseMove} onMouseUp={onMouseUp} onMouseLeave={onMouseUp} data-testid="kg-canvas">
          <div style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, transformOrigin: "center center", width: "1200px", height: "900px", position: "relative" }}>
            {/* Canvas for edges */}
            <canvas ref={canvasElRef} style={{ position: "absolute", top: 0, left: 0, width: "1200px", height: "900px", pointerEvents: "none" }} />
            {/* Node elements */}
            {filteredNodes.map(n => {
              const p = positions[n.node_id];
              if (!p) return null;
              const tc = TYPE_COLORS[n.type] || TYPE_COLORS.entity;
              const size = n.type === "network" ? 40 : 24;
              const sel = selectedNode?.node_id === n.node_id;
              return (
                <div
                  key={n.node_id}
                  data-testid={`kg-node-${n.node_id}`}
                  onMouseDown={(e) => { e.stopPropagation(); setDragging(n.node_id); setSelectedNode(n); lastMouse.current = { x: e.clientX, y: e.clientY }; }}
                  style={{
                    position: "absolute",
                    left: `${p.x - size / 2}px`,
                    top: `${p.y - size / 2}px`,
                    width: `${size}px`,
                    height: `${size}px`,
                    borderRadius: "50%",
                    backgroundColor: tc.fill,
                    border: sel ? "2px solid #fff" : `1.5px solid ${tc.stroke}`,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    transition: "box-shadow 0.15s",
                    boxShadow: sel ? `0 0 12px ${tc.fill}60` : "none",
                    zIndex: sel ? 10 : 1,
                  }}
                  title={n.label}
                >
                  <span style={{
                    position: "absolute",
                    top: `${size + 4}px`,
                    left: "50%",
                    transform: "translateX(-50%)",
                    whiteSpace: "nowrap",
                    fontSize: n.type === "network" ? "9px" : "7px",
                    color: "#a1a1aa",
                    fontWeight: 500,
                    textAlign: "center",
                    pointerEvents: "none",
                    maxWidth: "80px",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}>
                    {n.label.length > 18 ? n.label.slice(0, 16) + ".." : n.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {selectedNode && (
          <div className="w-72 bg-zinc-900/40 border border-white/5 rounded-xl p-4 shrink-0" data-testid="kg-detail-panel">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white truncate">{selectedNode.label}</h3>
              <button onClick={() => setSelectedNode(null)} className="text-zinc-500 hover:text-white"><X className="w-4 h-4" /></button>
            </div>
            <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium mb-3 ${(TYPE_COLORS[selectedNode.type] || TYPE_COLORS.entity).bg} ${(TYPE_COLORS[selectedNode.type] || TYPE_COLORS.entity).text}`}>
              <Circle className="w-2.5 h-2.5" fill="currentColor" />
              {selectedNode.type}
            </div>
            <div className="space-y-2">
              {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                <div key={k}><p className="text-[10px] text-zinc-600 uppercase">{k}</p><p className="text-xs text-zinc-300">{String(v)}</p></div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-white/5">
              <p className="text-[10px] text-zinc-600 uppercase mb-2">Connections</p>
              {graph.edges.filter(e => e.source === selectedNode.node_id || e.target === selectedNode.node_id).slice(0, 10).map((e, i) => {
                const other = e.source === selectedNode.node_id ? e.target : e.source;
                const otherNode = graph.nodes.find(n => n.node_id === other);
                return (
                  <div key={i} className="flex items-center gap-1.5 text-[11px] text-zinc-400 py-0.5">
                    <ArrowRight className="w-3 h-3 text-zinc-600" /><span className="text-zinc-500">{e.relationship}</span><span className="text-zinc-300 truncate">{otherNode?.label || other}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
