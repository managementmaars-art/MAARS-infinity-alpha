/**
 * WorkflowBuilder — Limitless AI Workflow Canvas
 *
 * Features:
 *  • 11 node types: Agent, Prompt, Branch, Loop, Merge, Trigger, Output, API Call, Code, Sub-Flow, Note
 *  • Full model picker per node — 33 providers, 175k+ models
 *  • Workflow Teams — colored group containers; connect team → team
 *  • Animated SVG edges with flow particles
 *  • Pan + Zoom (scroll wheel + middle-drag)
 *  • Mini-map overview
 *  • Templates for instant start
 *  • Variable passing: {{node_id}} in prompts
 *  • Complete node config: prompt, model, temperature, max_tokens, system prompt
 *  • Save / Load / Run with live execution state
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "../App";
import AgentAvatar from "../components/AgentAvatar";
import { toast } from "sonner";
import {
  Plus, Save, Trash2, Play, Search, X, Settings, FileText, Clock,
  CheckCircle, AlertCircle, Zap, Code2, GitBranch, Repeat, Globe,
  MessageSquare, Bot, ChevronDown, ZoomIn, ZoomOut,
  Download, Upload, Users, RotateCcw, Layers, Link2,
  ArrowRight, MoreHorizontal, Cpu, Sparkles, Database,
} from "lucide-react";

/* ── Constants ─────────────────────────────────────────────────────────────── */
const _BASE = process.env.REACT_APP_BACKEND_URL?.trim() || "http://localhost:8000";
const API   = `${_BASE}/api`;

const NODE_TYPES = {
  agent:        { label: "Agent",      Icon: Bot,          color: "#4fd1c5", desc: "AI agent from your roster" },
  prompt:       { label: "Prompt",     Icon: MessageSquare,color: "#a78bfa", desc: "Text prompt / template" },
  condition:    { label: "Branch",     Icon: GitBranch,    color: "#f59e0b", desc: "If/else conditional" },
  loop:         { label: "Loop",       Icon: Repeat,       color: "#60a5fa", desc: "Iterate over a collection" },
  merge:        { label: "Merge",      Icon: Layers,       color: "#34d399", desc: "Wait for multiple inputs" },
  trigger:      { label: "Trigger",    Icon: Zap,          color: "#fbbf24", desc: "Workflow entry point" },
  output:       { label: "Output",     Icon: Download,     color: "#f472b6", desc: "Export / send result" },
  api_call:     { label: "API Call",   Icon: Globe,        color: "#0ea5e9", desc: "HTTP request" },
  code:         { label: "Code",       Icon: Code2,        color: "#f97316", desc: "Run custom JavaScript" },
  sub_workflow: { label: "Sub-Flow",   Icon: Link2,        color: "#d946ef", desc: "Embed another workflow" },
  note:         { label: "Note",       Icon: FileText,     color: "#64748b", desc: "Comment / documentation" },
};

const NODE_DEFAULTS = {
  agent:        { task: "", model_provider: "auto", model_name: "auto", temperature: 0.7, max_tokens: 2000, system_prompt: "" },
  prompt:       { template: "", output_var: "prompt_out" },
  condition:    { condition: "", true_label: "True →", false_label: "False →" },
  loop:         { collection: "", item_var: "item", max_iterations: 10 },
  merge:        { mode: "all" },
  trigger:      { trigger_type: "manual", cron: "", description: "" },
  output:       { output_type: "text", destination: "" },
  api_call:     { method: "GET", url: "", headers: '{"Content-Type":"application/json"}', body: "" },
  code:         { code: "// Access inputs via: inputs.node_id\n// Return your result\nreturn inputs;" },
  sub_workflow: { workflow_id: "", workflow_name: "Select workflow…" },
  note:         { text: "Add notes here…" },
};

const MODELS = [
  { group: "Auto Router", items: [
    { provider: "auto", model: "auto", label: "Smart Auto Router", badge: "FREE", desc: "Best model per task" },
  ]},
  { group: "OpenAI", items: [
    { provider: "openai", model: "gpt-5",        label: "GPT-5",               badge: "3cr" },
    { provider: "openai", model: "gpt-4.1",      label: "GPT-4.1",             badge: "2cr" },
    { provider: "openai", model: "gpt-4o",       label: "GPT-4o",              badge: "2cr" },
    { provider: "openai", model: "gpt-4o-mini",  label: "GPT-4o Mini",         badge: "1cr" },
    { provider: "openai", model: "o4-mini",      label: "O4 Mini (Reasoning)", badge: "2cr" },
    { provider: "openai", model: "o3",           label: "O3 (Reasoning)",      badge: "5cr" },
  ]},
  { group: "Anthropic", items: [
    { provider: "anthropic", model: "claude-opus-4-6",           label: "Claude Opus 4.6",   badge: "5cr" },
    { provider: "anthropic", model: "claude-sonnet-4-6",         label: "Claude Sonnet 4.6", badge: "3cr" },
    { provider: "anthropic", model: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5",  badge: "1cr" },
  ]},
  { group: "Google", items: [
    { provider: "gemini", model: "gemini-2.5-pro",        label: "Gemini 2.5 Pro",   badge: "2cr" },
    { provider: "gemini", model: "gemini-2.5-flash",      label: "Gemini 2.5 Flash", badge: "1cr" },
    { provider: "gemini", model: "gemini-3-pro-preview",  label: "Gemini 3 Pro",     badge: "2cr" },
  ]},
  { group: "xAI Grok", items: [
    { provider: "xai", model: "grok-3",      label: "Grok 3",      badge: "3cr" },
    { provider: "xai", model: "grok-3-mini", label: "Grok 3 Mini", badge: "1cr" },
  ]},
  { group: "DeepSeek", items: [
    { provider: "deepseek", model: "deepseek-v3-0324", label: "DeepSeek V3",         badge: "1cr" },
    { provider: "deepseek", model: "deepseek-r1-0528", label: "DeepSeek R1 Reason",  badge: "2cr" },
  ]},
  { group: "Mistral", items: [
    { provider: "mistral", model: "mistral-large-latest",  label: "Mistral Large",  badge: "3cr" },
    { provider: "mistral", model: "codestral-latest",      label: "Codestral",      badge: "1cr" },
    { provider: "mistral", model: "pixtral-large-latest",  label: "Pixtral Large",  badge: "3cr" },
  ]},
  { group: "Fast / Open", items: [
    { provider: "groq",     model: "llama-4-maverick-17b-128e-instruct", label: "Llama 4 Maverick", badge: "1cr" },
    { provider: "groq",     model: "qwen-qwq-32b",                       label: "QwQ 32B Reason",   badge: "1cr" },
    { provider: "cerebras", model: "llama-3.3-70b",                      label: "Cerebras 70B",     badge: "1cr" },
    { provider: "deepseek", model: "deepseek-chat",                      label: "DeepSeek Chat",    badge: "1cr" },
  ]},
  { group: "Search / Research", items: [
    { provider: "perplexity", model: "sonar-pro",           label: "Sonar Pro",           badge: "3cr" },
    { provider: "perplexity", model: "sonar-deep-research", label: "Sonar Deep Research", badge: "3cr" },
    { provider: "perplexity", model: "sonar-reasoning-pro", label: "Sonar Reasoning Pro", badge: "3cr" },
  ]},
];

const NET_COLORS = {
  core_platform: "#10b981", strategic_executive: "#a855f7", venture_creation: "#3b82f6",
  product_development: "#06b6d4", engineering: "#f59e0b", creative_brand: "#ec4899",
  growth_distribution: "#22c55e", sales_revenue: "#f97316", customer_experience: "#14b8a6",
  operations: "#4fd1c5", finance_capital: "#eab308", research_intelligence: "#0ea5e9",
  simulation_foresight: "#d946ef", security: "#ef4444", execution: "#f97316",
  legal_governance: "#94a3b8", memory_knowledge: "#818cf8", tooling_capability: "#f472b6",
};

const TEMPLATES = [
  {
    name: "Content Pipeline",
    desc: "Research → Write → Edit → Publish",
    nodes: [
      { type: "trigger",  name: "Start",         x: 80,   y: 200, data: { trigger_type: "manual" } },
      { type: "agent",    name: "Researcher",     x: 300,  y: 200, data: { task: "Research the topic thoroughly", model_provider: "perplexity", model_name: "sonar-pro" } },
      { type: "agent",    name: "Writer",         x: 520,  y: 200, data: { task: "Write a compelling draft based on research", model_provider: "anthropic", model_name: "claude-sonnet-4-6" } },
      { type: "agent",    name: "Editor",         x: 740,  y: 200, data: { task: "Edit and refine the draft", model_provider: "openai", model_name: "gpt-4o" } },
      { type: "output",   name: "Publish",        x: 960,  y: 200, data: { output_type: "text" } },
    ],
    edges: [[0,1],[1,2],[2,3],[3,4]],
    teams: [
      { name: "Content Team", color: "#a78bfa", nodeIndices: [1,2,3] },
    ],
  },
  {
    name: "Market Intelligence",
    desc: "Multi-agent competitive analysis",
    nodes: [
      { type: "trigger",   name: "Start",         x: 80,   y: 300, data: { trigger_type: "manual" } },
      { type: "agent",     name: "Market Analyst",x: 300,  y: 160, data: { task: "Analyze market trends and competitive landscape", model_provider: "perplexity", model_name: "sonar-deep-research" } },
      { type: "agent",     name: "Data Scientist",x: 300,  y: 340, data: { task: "Process and analyze data sets for insights" } },
      { type: "agent",     name: "Strategist",    x: 300,  y: 520, data: { task: "Develop strategic recommendations" } },
      { type: "merge",     name: "Combine",       x: 560,  y: 340, data: { mode: "all" } },
      { type: "agent",     name: "Report Writer", x: 780,  y: 340, data: { task: "Write comprehensive market intelligence report", model_provider: "anthropic", model_name: "claude-opus-4-6" } },
      { type: "output",    name: "Report",        x: 1000, y: 340, data: { output_type: "text" } },
    ],
    edges: [[0,1],[0,2],[0,3],[1,4],[2,4],[3,4],[4,5],[5,6]],
    teams: [
      { name: "Research Team", color: "#0ea5e9", nodeIndices: [1,2,3] },
    ],
  },
  {
    name: "Code Review Pipeline",
    desc: "Automated code analysis & security scan",
    nodes: [
      { type: "trigger",   name: "Code Push",     x: 80,   y: 260, data: { trigger_type: "webhook" } },
      { type: "code",      name: "Parse Code",    x: 300,  y: 160, data: { code: "return { files: inputs.payload.files, language: inputs.payload.language };" } },
      { type: "agent",     name: "Code Reviewer", x: 300,  y: 360, data: { task: "Review code quality, patterns, and best practices", model_provider: "openai", model_name: "gpt-4o" } },
      { type: "agent",     name: "Security Agent",x: 520,  y: 160, data: { task: "Scan for security vulnerabilities and CVEs" } },
      { type: "condition", name: "Issues?",        x: 520,  y: 360, data: { condition: "has_issues === true" } },
      { type: "agent",     name: "Fix Suggester",  x: 740,  y: 280, data: { task: "Suggest specific code fixes and improvements" } },
      { type: "output",    name: "PR Comment",    x: 960,  y: 280, data: { output_type: "text" } },
    ],
    edges: [[0,1],[0,2],[1,3],[2,4],[3,5],[4,5],[5,6]],
    teams: [],
  },
];

/* ── helpers ───────────────────────────────────────────────────────────────── */
const uid = () => `n_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
const getNodeColor = (node) => {
  if (node.type === "agent" && node.data?.network) return NET_COLORS[node.data.network] || NODE_TYPES.agent.color;
  return NODE_TYPES[node.type]?.color || "#4fd1c5";
};

/* ── ModelPicker component ─────────────────────────────────────────────────── */
function ModelPicker({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const allItems = MODELS.flatMap(g => g.items);
  const current = allItems.find(m => m.provider === value?.provider && m.model === value?.model) || allItems[0];

  const filtered = search
    ? allItems.filter(m => m.label.toLowerCase().includes(search.toLowerCase()) || m.provider.toLowerCase().includes(search.toLowerCase()))
    : null;

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        style={{
          width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between",
          gap: 8, padding: "7px 10px", borderRadius: 9,
          background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
          color: "#e2e8f0", fontSize: 12, cursor: "pointer",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6, overflow: "hidden" }}>
          <Cpu style={{ width: 12, height: 12, color: "#4fd1c5", flexShrink: 0 }} />
          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{current?.label || "Select model"}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
          {current?.badge && <span style={{ fontSize: 9, padding: "1px 5px", borderRadius: 4, background: "rgba(79,209,197,0.15)", color: "#4fd1c5", fontWeight: 700 }}>{current.badge}</span>}
          <ChevronDown style={{ width: 11, height: 11, color: "#64748b" }} />
        </div>
      </button>

      {open && (
        <div style={{
          position: "absolute", left: 0, top: "calc(100% + 4px)", zIndex: 200,
          width: 280, maxHeight: 320, overflow: "hidden",
          background: "rgba(8,12,22,0.98)", backdropFilter: "blur(20px)",
          border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12,
          boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
          display: "flex", flexDirection: "column",
        }}>
          <div style={{ padding: "8px 8px 4px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
            <div style={{ position: "relative" }}>
              <Search style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", width: 11, height: 11, color: "#475569", pointerEvents: "none" }} />
              <input
                value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search models…"
                autoFocus
                style={{ width: "100%", paddingLeft: 26, height: 30, borderRadius: 7, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "#e2e8f0", fontSize: 11, outline: "none", boxSizing: "border-box" }}
              />
            </div>
          </div>
          <div style={{ overflowY: "auto", flex: 1 }}>
            {(filtered ? [{ group: "Results", items: filtered }] : MODELS).map(group => (
              <div key={group.group}>
                <p style={{ fontSize: 9, fontWeight: 700, color: "#475569", padding: "6px 10px 3px", letterSpacing: "0.1em", textTransform: "uppercase" }}>{group.group}</p>
                {group.items.map(item => (
                  <button key={`${item.provider}/${item.model}`} type="button"
                    onClick={() => { onChange({ provider: item.provider, model: item.model }); setOpen(false); setSearch(""); }}
                    style={{
                      width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between",
                      gap: 6, padding: "6px 10px", background: current?.model === item.model ? "rgba(79,209,197,0.1)" : "transparent",
                      border: "none", cursor: "pointer", textAlign: "left",
                    }}
                    onMouseEnter={e => { if (current?.model !== item.model) e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
                    onMouseLeave={e => { if (current?.model !== item.model) e.currentTarget.style.background = "transparent"; }}
                  >
                    <span style={{ fontSize: 11, color: current?.model === item.model ? "#4fd1c5" : "#e2e8f0" }}>{item.label}</span>
                    <span style={{ fontSize: 9, padding: "1px 5px", borderRadius: 4, background: current?.model === item.model ? "rgba(79,209,197,0.2)" : "rgba(255,255,255,0.07)", color: current?.model === item.model ? "#4fd1c5" : "#64748b", fontWeight: 700, flexShrink: 0 }}>{item.badge}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── SVG Edge component ────────────────────────────────────────────────────── */
function EdgeLine({ sourceNode, targetNode, edge, isRunning, isCompleted, isFailed, onDelete }) {
  const [hovered, setHovered] = useState(false);
  if (!sourceNode || !targetNode) return null;

  const NODE_W = 220, NODE_H = 80;
  const sx = sourceNode.x + NODE_W;
  const sy = sourceNode.y + NODE_H / 2;
  const tx = targetNode.x;
  const ty = targetNode.y + NODE_H / 2;
  const dx = Math.abs(tx - sx);
  const cpx1 = sx + Math.max(dx * 0.5, 60);
  const cpy1 = sy;
  const cpx2 = tx - Math.max(dx * 0.5, 60);
  const cpy2 = ty;
  const path = `M${sx},${sy} C${cpx1},${cpy1} ${cpx2},${cpy2} ${tx},${ty}`;
  const color = getNodeColor(sourceNode);
  const strokeColor = isFailed ? "#ef4444" : isCompleted ? "#34d399" : isRunning ? "#fbbf24" : color;

  // Arrow at target end
  const angle = Math.atan2(ty - cpy2, tx - cpx2);
  const arrowSize = 8;

  return (
    <g
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ cursor: "pointer" }}
    >
      {/* Click target (wider invisible path) */}
      <path d={path} fill="none" stroke="transparent" strokeWidth={14} />
      {/* Main edge */}
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth={hovered ? 2.5 : 1.8}
        strokeOpacity={hovered ? 0.9 : 0.55}
        strokeDasharray={isRunning ? "8 4" : "none"}
        style={isRunning ? { animation: "wf_flow 0.5s linear infinite" } : {}}
      />
      {/* Glow on hover */}
      {hovered && <path d={path} fill="none" stroke={strokeColor} strokeWidth={6} strokeOpacity={0.12} />}
      {/* Arrow */}
      <polygon
        points={`${tx},${ty} ${tx - arrowSize * Math.cos(angle - 0.4)},${ty - arrowSize * Math.sin(angle - 0.4)} ${tx - arrowSize * Math.cos(angle + 0.4)},${ty - arrowSize * Math.sin(angle + 0.4)}`}
        fill={strokeColor}
        opacity={0.75}
      />
      {/* Delete button on hover */}
      {hovered && (
        <g transform={`translate(${(sx + tx) / 2},${(sy + ty) / 2})`} onClick={onDelete}>
          <circle cx={0} cy={0} r={9} fill="#1e293b" stroke={strokeColor} strokeWidth={1} />
          <text x={0} y={4} textAnchor="middle" fontSize={11} fill="#94a3b8">×</text>
        </g>
      )}
    </g>
  );
}

/* ── Team Container ────────────────────────────────────────────────────────── */
function TeamContainer({ team, isSelected, onSelect, onUpdate, onDelete, children }) {
  const dragRef = useRef({ dragging: false, sx: 0, sy: 0, px: 0, py: 0 });

  const onMouseDown = (e) => {
    if (e.target.closest("button") || e.target.closest("input")) return;
    dragRef.current = { dragging: true, sx: e.clientX, sy: e.clientY, px: team.x, py: team.y };
    e.stopPropagation();
  };

  useEffect(() => {
    const move = (e) => {
      if (!dragRef.current.dragging) return;
      onUpdate({ x: dragRef.current.px + (e.clientX - dragRef.current.sx), y: dragRef.current.py + (e.clientY - dragRef.current.sy) });
    };
    const up = () => { dragRef.current.dragging = false; };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
    return () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
  }, [onUpdate]);

  return (
    <div
      onMouseDown={onMouseDown}
      onClick={(e) => { e.stopPropagation(); onSelect(); }}
      style={{
        position: "absolute",
        left: team.x, top: team.y,
        width: team.width, height: team.height,
        borderRadius: 18,
        border: `2px solid ${team.color}${isSelected ? "aa" : "44"}`,
        background: `${team.color}08`,
        backdropFilter: "blur(2px)",
        boxShadow: isSelected ? `0 0 0 1px ${team.color}33, 0 0 40px ${team.color}12` : "none",
        cursor: "grab",
        zIndex: 0,
        transition: "border-color 0.2s, box-shadow 0.2s",
      }}
    >
      {/* Team label */}
      <div style={{
        position: "absolute", top: -1, left: 16,
        display: "flex", alignItems: "center", gap: 6,
        padding: "3px 10px",
        background: team.color,
        borderRadius: "0 0 10px 10px",
        userSelect: "none",
      }}>
        <Users style={{ width: 10, height: 10, color: "#030712" }} />
        <span style={{ fontSize: 10, fontWeight: 800, color: "#030712", letterSpacing: "0.05em" }}>{team.name.toUpperCase()}</span>
        {isSelected && (
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
            style={{ background: "none", border: "none", cursor: "pointer", color: "rgba(3,7,18,0.6)", padding: 0, display: "flex", marginLeft: 4 }}
          >
            <X style={{ width: 10, height: 10 }} />
          </button>
        )}
      </div>
      {/* Team port — output right edge */}
      <div style={{
        position: "absolute", right: -8, top: "50%", transform: "translateY(-50%)",
        width: 16, height: 16, borderRadius: "50%",
        background: team.color, border: "2px solid #030712",
        boxShadow: `0 0 10px ${team.color}`,
        cursor: "crosshair",
        title: "Connect to another team",
      }} />
      {/* Team port — input left edge */}
      <div style={{
        position: "absolute", left: -8, top: "50%", transform: "translateY(-50%)",
        width: 16, height: 16, borderRadius: "50%",
        background: "#1e293b", border: `2px solid ${team.color}`,
        cursor: "crosshair",
      }} />
    </div>
  );
}

/* ── Node Card ─────────────────────────────────────────────────────────────── */
function NodeCard({ node, isSelected, isConnecting, nodeState, onMouseDown, onConnect, onDelete }) {
  const color = getNodeColor(node);
  const { Icon } = NODE_TYPES[node.type] || {};
  const statusColor = nodeState?.status === "completed" ? "#34d399" : nodeState?.status === "failed" ? "#ef4444" : nodeState?.status === "running" ? "#fbbf24" : null;

  return (
    <div
      onMouseDown={onMouseDown}
      data-testid={`wf-node-${node.id}`}
      style={{
        position: "absolute",
        left: node.x, top: node.y,
        width: 220,
        borderRadius: 14,
        background: isSelected ? "rgba(12,18,32,0.97)" : "rgba(8,12,24,0.92)",
        border: `1.5px solid ${isSelected ? color : isConnecting ? "#fbbf24" : "rgba(255,255,255,0.08)"}`,
        boxShadow: isSelected ? `0 0 0 1px ${color}40, 0 8px 32px rgba(0,0,0,0.5), 0 0 24px ${color}15` : "0 4px 16px rgba(0,0,0,0.4)",
        cursor: isConnecting ? "crosshair" : "grab",
        backdropFilter: "blur(12px)",
        zIndex: isSelected ? 10 : 2,
        transition: "border-color 0.15s, box-shadow 0.15s",
        overflow: "visible",
      }}
    >
      {/* Header */}
      <div style={{
        padding: "10px 12px 8px",
        background: `linear-gradient(135deg, ${color}20, ${color}08)`,
        borderBottom: `1px solid ${color}18`,
        borderRadius: "13px 13px 0 0",
        display: "flex", alignItems: "center", gap: 8,
      }}>
        {node.type === "agent" && node.data?.avatar ? (
          <img src={node.data.avatar} alt="" style={{ width: 24, height: 24, borderRadius: "50%", objectFit: "cover", border: `1px solid ${color}44` }} />
        ) : Icon ? (
          <div style={{ width: 24, height: 24, borderRadius: 7, background: `${color}22`, border: `1px solid ${color}33`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <Icon style={{ width: 12, height: 12, color }} />
          </div>
        ) : null}
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", lineHeight: 1.2 }}>{node.name || NODE_TYPES[node.type]?.label}</p>
          <p style={{ fontSize: 9, color, opacity: 0.8, marginTop: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {node.type === "agent" && node.data?.role ? node.data.role : NODE_TYPES[node.type]?.label}
          </p>
        </div>
        {statusColor && (
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: statusColor, boxShadow: `0 0 6px ${statusColor}`, flexShrink: 0 }} />
        )}
        {nodeState?.status === "running" && (
          <Clock style={{ width: 12, height: 12, color: "#fbbf24", animation: "wf_spin 1s linear infinite", flexShrink: 0 }} />
        )}
      </div>

      {/* Body */}
      <div style={{ padding: "8px 12px 10px", minHeight: 36 }}>
        {node.type === "agent" && node.data?.task && (
          <p style={{ fontSize: 10, color: "#94a3b8", lineHeight: 1.4, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{node.data.task}</p>
        )}
        {node.type === "agent" && (node.data?.model_provider && node.data.model_provider !== "auto") && (
          <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 4 }}>
            <Cpu style={{ width: 9, height: 9, color: "#4fd1c5" }} />
            <span style={{ fontSize: 9, color: "#4fd1c5" }}>{node.data.model_provider}/{node.data.model_name?.split("-").slice(0, 2).join("-")}</span>
          </div>
        )}
        {node.type === "prompt" && node.data?.template && (
          <p style={{ fontSize: 10, color: "#94a3b8", lineHeight: 1.4, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{node.data.template}</p>
        )}
        {node.type === "condition" && node.data?.condition && (
          <p style={{ fontSize: 10, color: "#f59e0b", fontFamily: "monospace" }}>if ({node.data.condition})</p>
        )}
        {node.type === "loop" && node.data?.collection && (
          <p style={{ fontSize: 10, color: "#60a5fa", fontFamily: "monospace" }}>for {node.data.item_var} in {node.data.collection}</p>
        )}
        {node.type === "api_call" && node.data?.url && (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ fontSize: 9, padding: "1px 5px", borderRadius: 4, background: "rgba(14,165,233,0.15)", color: "#0ea5e9", fontWeight: 700 }}>{node.data.method}</span>
            <span style={{ fontSize: 9, color: "#64748b", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>{node.data.url}</span>
          </div>
        )}
        {node.type === "code" && (
          <p style={{ fontSize: 9, color: "#f97316", fontFamily: "monospace" }}>{"{ JS }"}</p>
        )}
        {node.type === "trigger" && (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", animation: "wf_pulse 2s ease-in-out infinite" }} />
            <span style={{ fontSize: 9, color: "#34d399" }}>{node.data?.trigger_type || "manual"}</span>
          </div>
        )}
        {node.type === "note" && (
          <p style={{ fontSize: 10, color: "#64748b", lineHeight: 1.5 }}>{node.data?.text}</p>
        )}
        {/* LLM output preview */}
        {nodeState?.output && (
          <div style={{ marginTop: 6, padding: "5px 8px", borderRadius: 7, background: nodeState.status === "completed" ? "rgba(52,211,153,0.08)" : "rgba(248,113,113,0.08)", border: `1px solid ${nodeState.status === "completed" ? "rgba(52,211,153,0.2)" : "rgba(248,113,113,0.2)"}` }}>
            <p style={{ fontSize: 9, color: nodeState.status === "completed" ? "#34d399" : "#f87171", lineHeight: 1.4, display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{nodeState.output}</p>
          </div>
        )}
      </div>

      {/* Input port */}
      {node.type !== "trigger" && (
        <div style={{
          position: "absolute", left: -7, top: "50%", transform: "translateY(-50%)",
          width: 14, height: 14, borderRadius: "50%",
          background: "#1e293b", border: `2px solid ${color}`,
          zIndex: 3,
        }} />
      )}

      {/* Output port(s) */}
      {node.type !== "output" && node.type !== "note" && (
        <div
          onClick={(e) => { e.stopPropagation(); onConnect(node.id); }}
          title="Click to connect"
          style={{
            position: "absolute", right: -7, top: node.type === "condition" ? "35%" : "50%",
            transform: "translateY(-50%)",
            width: 14, height: 14, borderRadius: "50%",
            background: color, border: "2px solid #030712",
            zIndex: 3, cursor: "crosshair",
            boxShadow: `0 0 8px ${color}`,
          }}
        />
      )}
      {node.type === "condition" && (
        <div
          onClick={(e) => { e.stopPropagation(); onConnect(node.id); }}
          style={{
            position: "absolute", right: -7, top: "68%", transform: "translateY(-50%)",
            width: 14, height: 14, borderRadius: "50%",
            background: "#ef4444", border: "2px solid #030712",
            zIndex: 3, cursor: "crosshair", boxShadow: "0 0 8px #ef4444",
          }}
        />
      )}

      {/* Action buttons (when selected) */}
      {isSelected && (
        <div style={{ position: "absolute", top: -14, right: 6, display: "flex", gap: 4 }}>
          <button
            onMouseDown={(e) => e.stopPropagation()}
            onClick={(e) => { e.stopPropagation(); onConnect(node.id); }}
            title="Connect to node"
            style={{ width: 20, height: 20, borderRadius: "50%", background: "#f59e0b", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <ArrowRight style={{ width: 10, height: 10, color: "#030712" }} />
          </button>
          <button
            onMouseDown={(e) => e.stopPropagation()}
            onClick={(e) => { e.stopPropagation(); onDelete(node.id); }}
            title="Delete node"
            style={{ width: 20, height: 20, borderRadius: "50%", background: "#ef4444", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <X style={{ width: 10, height: 10, color: "#fff" }} />
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Node Config Panel ─────────────────────────────────────────────────────── */
function NodeConfigPanel({ node, workflows, onUpdate, onClose }) {
  if (!node) return null;
  const color = getNodeColor(node);
  const d = node.data || {};
  const NodeIcon = NODE_TYPES[node.type]?.Icon;

  const set = (key, val) => onUpdate(node.id, { ...d, [key]: val });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0, overflow: "hidden", height: "100%" }}>
      {/* Header */}
      <div style={{ padding: "12px 14px 10px", borderBottom: "1px solid rgba(255,255,255,0.06)", background: `linear-gradient(135deg, ${color}14, transparent)`, display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: `${color}22`, border: `1px solid ${color}33`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          {NodeIcon && <NodeIcon style={{ width: 13, height: 13, color }} />}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <input
            value={node.name || ""}
            onChange={e => onUpdate(node.id, d, e.target.value)}
            style={{ width: "100%", background: "transparent", border: "none", outline: "none", color: "#f1f5f9", fontSize: 13, fontWeight: 700 }}
          />
          <p style={{ fontSize: 9, color, margin: 0 }}>{NODE_TYPES[node.type]?.label}</p>
        </div>
        <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "#475569" }}>
          <X style={{ width: 13, height: 13 }} />
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px", display: "flex", flexDirection: "column", gap: 12 }}>

        {/* AGENT node config */}
        {node.type === "agent" && (
          <>
            <div>
              <label style={lbl}>Task Prompt</label>
              <textarea
                value={d.task || ""}
                onChange={e => set("task", e.target.value)}
                placeholder="What should this agent do? Use {{previous_node_id}} to reference prior outputs."
                style={{ ...ta, minHeight: 80 }}
                data-testid="wf-task-input"
              />
              <p style={{ fontSize: 9, color: "#334155", marginTop: 4 }}>Tip: use {"{{node_id}}"} to inject outputs from connected nodes</p>
            </div>
            <div>
              <label style={lbl}>Model</label>
              <ModelPicker
                value={{ provider: d.model_provider || "auto", model: d.model_name || "auto" }}
                onChange={({ provider, model }) => onUpdate(node.id, { ...d, model_provider: provider, model_name: model })}
              />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <div>
                <label style={lbl}>Temperature</label>
                <input type="number" min={0} max={2} step={0.1} value={d.temperature ?? 0.7}
                  onChange={e => set("temperature", parseFloat(e.target.value))}
                  style={inp} />
              </div>
              <div>
                <label style={lbl}>Max Tokens</label>
                <input type="number" min={100} max={32000} step={100} value={d.max_tokens ?? 2000}
                  onChange={e => set("max_tokens", parseInt(e.target.value))}
                  style={inp} />
              </div>
            </div>
            <div>
              <label style={lbl}>System Prompt Override</label>
              <textarea value={d.system_prompt || ""}
                onChange={e => set("system_prompt", e.target.value)}
                placeholder="Override the agent's default system prompt (optional)…"
                style={{ ...ta, minHeight: 60 }} />
            </div>
          </>
        )}

        {/* PROMPT node config */}
        {node.type === "prompt" && (
          <>
            <div>
              <label style={lbl}>Prompt Template</label>
              <textarea value={d.template || ""} onChange={e => set("template", e.target.value)}
                placeholder="Write your prompt. Use {{node_id}} to inject node outputs."
                style={{ ...ta, minHeight: 120 }} />
            </div>
            <div>
              <label style={lbl}>Model</label>
              <ModelPicker
                value={{ provider: d.model_provider || "auto", model: d.model_name || "auto" }}
                onChange={({ provider, model }) => onUpdate(node.id, { ...d, model_provider: provider, model_name: model })}
              />
            </div>
            <div>
              <label style={lbl}>Output Variable Name</label>
              <input value={d.output_var || "prompt_out"} onChange={e => set("output_var", e.target.value)} style={inp} placeholder="e.g. prompt_out" />
            </div>
          </>
        )}

        {/* CONDITION node */}
        {node.type === "condition" && (
          <>
            <div>
              <label style={lbl}>Condition Expression</label>
              <input value={d.condition || ""} onChange={e => set("condition", e.target.value)}
                style={inp} placeholder='e.g. output.includes("error") or score > 80' />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <div>
                <label style={lbl}>True Branch Label</label>
                <input value={d.true_label || "True →"} onChange={e => set("true_label", e.target.value)} style={inp} />
              </div>
              <div>
                <label style={lbl}>False Branch Label</label>
                <input value={d.false_label || "False →"} onChange={e => set("false_label", e.target.value)} style={inp} />
              </div>
            </div>
          </>
        )}

        {/* LOOP node */}
        {node.type === "loop" && (
          <>
            <div>
              <label style={lbl}>Collection / Variable</label>
              <input value={d.collection || ""} onChange={e => set("collection", e.target.value)} style={inp} placeholder="e.g. {{research.items}}" />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <div>
                <label style={lbl}>Item Variable</label>
                <input value={d.item_var || "item"} onChange={e => set("item_var", e.target.value)} style={inp} />
              </div>
              <div>
                <label style={lbl}>Max Iterations</label>
                <input type="number" value={d.max_iterations || 10} onChange={e => set("max_iterations", parseInt(e.target.value))} style={inp} />
              </div>
            </div>
          </>
        )}

        {/* MERGE node */}
        {node.type === "merge" && (
          <div>
            <label style={lbl}>Merge Mode</label>
            <select value={d.mode || "all"} onChange={e => set("mode", e.target.value)} style={inp}>
              <option value="all">Wait for ALL inputs</option>
              <option value="any">Proceed on ANY input</option>
              <option value="first">First input wins</option>
            </select>
          </div>
        )}

        {/* TRIGGER node */}
        {node.type === "trigger" && (
          <>
            <div>
              <label style={lbl}>Trigger Type</label>
              <select value={d.trigger_type || "manual"} onChange={e => set("trigger_type", e.target.value)} style={inp}>
                <option value="manual">Manual</option>
                <option value="schedule">Schedule (Cron)</option>
                <option value="webhook">Webhook</option>
                <option value="event">System Event</option>
              </select>
            </div>
            {d.trigger_type === "schedule" && (
              <div>
                <label style={lbl}>Cron Expression</label>
                <input value={d.cron || ""} onChange={e => set("cron", e.target.value)} style={inp} placeholder="0 9 * * 1-5 (weekdays 9am)" />
              </div>
            )}
            <div>
              <label style={lbl}>Description</label>
              <input value={d.description || ""} onChange={e => set("description", e.target.value)} style={inp} placeholder="What triggers this workflow?" />
            </div>
          </>
        )}

        {/* OUTPUT node */}
        {node.type === "output" && (
          <>
            <div>
              <label style={lbl}>Output Type</label>
              <select value={d.output_type || "text"} onChange={e => set("output_type", e.target.value)} style={inp}>
                <option value="text">Text Result</option>
                <option value="email">Send Email</option>
                <option value="webhook">Webhook POST</option>
                <option value="file">File Download</option>
                <option value="slack">Slack Message</option>
              </select>
            </div>
            {(d.output_type === "email" || d.output_type === "webhook" || d.output_type === "slack") && (
              <div>
                <label style={lbl}>Destination</label>
                <input value={d.destination || ""} onChange={e => set("destination", e.target.value)} style={inp}
                  placeholder={d.output_type === "email" ? "recipient@example.com" : d.output_type === "slack" ? "#channel-name" : "https://..."} />
              </div>
            )}
          </>
        )}

        {/* API CALL node */}
        {node.type === "api_call" && (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "80px 1fr", gap: 6 }}>
              <div>
                <label style={lbl}>Method</label>
                <select value={d.method || "GET"} onChange={e => set("method", e.target.value)} style={inp}>
                  <option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option><option>PATCH</option>
                </select>
              </div>
              <div>
                <label style={lbl}>URL</label>
                <input value={d.url || ""} onChange={e => set("url", e.target.value)} style={inp} placeholder="https://api.example.com/endpoint" />
              </div>
            </div>
            <div>
              <label style={lbl}>Headers (JSON)</label>
              <textarea value={d.headers || ""} onChange={e => set("headers", e.target.value)} style={{ ...ta, minHeight: 50, fontFamily: "monospace", fontSize: 10 }} placeholder='{"Authorization": "Bearer {{env.API_KEY}}"}' />
            </div>
            {["POST","PUT","PATCH"].includes(d.method) && (
              <div>
                <label style={lbl}>Body (JSON)</label>
                <textarea value={d.body || ""} onChange={e => set("body", e.target.value)} style={{ ...ta, minHeight: 60, fontFamily: "monospace", fontSize: 10 }} />
              </div>
            )}
          </>
        )}

        {/* CODE node */}
        {node.type === "code" && (
          <div>
            <label style={lbl}>JavaScript Code</label>
            <textarea value={d.code || ""} onChange={e => set("code", e.target.value)}
              style={{ ...ta, minHeight: 160, fontFamily: "monospace", fontSize: 11, lineHeight: 1.6 }} />
            <p style={{ fontSize: 9, color: "#334155", marginTop: 4 }}>Access inputs: inputs.node_id · Return value is passed to next nodes</p>
          </div>
        )}

        {/* SUB-WORKFLOW node */}
        {node.type === "sub_workflow" && (
          <>
            <div>
              <label style={lbl}>Select Workflow</label>
              <select value={d.workflow_id || ""} onChange={e => {
                const wf = workflows.find(w => w.workflow_id === e.target.value);
                onUpdate(node.id, { ...d, workflow_id: e.target.value, workflow_name: wf?.name || "" });
              }} style={inp}>
                <option value="">— pick a workflow —</option>
                {workflows.map(w => <option key={w.workflow_id} value={w.workflow_id}>{w.name}</option>)}
              </select>
            </div>
            {d.workflow_name && <p style={{ fontSize: 10, color: "#4fd1c5" }}>Selected: {d.workflow_name}</p>}
          </>
        )}

        {/* NOTE node */}
        {node.type === "note" && (
          <div>
            <label style={lbl}>Note Text</label>
            <textarea value={d.text || ""} onChange={e => set("text", e.target.value)} style={{ ...ta, minHeight: 100 }} />
          </div>
        )}
      </div>
    </div>
  );
}

// Shared styles for config panel
const lbl = { fontSize: 10, fontWeight: 700, color: "#64748b", display: "block", marginBottom: 4, letterSpacing: "0.06em", textTransform: "uppercase" };
const inp = { width: "100%", height: 34, padding: "0 10px", borderRadius: 8, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "#e2e8f0", fontSize: 11, outline: "none", boxSizing: "border-box" };
const ta  = { width: "100%", padding: "8px 10px", borderRadius: 8, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", color: "#e2e8f0", fontSize: 11, outline: "none", resize: "vertical", boxSizing: "border-box", lineHeight: 1.5 };

/* ── MiniMap ───────────────────────────────────────────────────────────────── */
function MiniMap({ nodes, teams, viewport, canvasSize }) {
  const scale = 0.14;
  const W = 180, H = 110;
  return (
    <div style={{ position: "absolute", bottom: 16, right: 16, width: W, height: H, borderRadius: 10, background: "rgba(8,12,22,0.92)", border: "1px solid rgba(255,255,255,0.1)", overflow: "hidden", zIndex: 50, backdropFilter: "blur(12px)" }}>
      <p style={{ position: "absolute", top: 4, left: 7, fontSize: 8, fontWeight: 700, color: "#475569", letterSpacing: "0.1em", textTransform: "uppercase", zIndex: 2 }}>MAP</p>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {teams.map(t => (
          <rect key={t.id} x={t.x * scale + 2} y={t.y * scale + 2} width={t.width * scale} height={t.height * scale}
            rx={4} fill={t.color} fillOpacity={0.12} stroke={t.color} strokeOpacity={0.4} strokeWidth={1} />
        ))}
        {nodes.map(n => (
          <rect key={n.id} x={n.x * scale + 2} y={n.y * scale + 2} width={220 * scale} height={70 * scale}
            rx={3} fill={getNodeColor(n)} fillOpacity={0.7} />
        ))}
        {/* Viewport indicator */}
        <rect
          x={(-viewport.x / viewport.zoom) * scale + 2}
          y={(-viewport.y / viewport.zoom) * scale + 2}
          width={(canvasSize.w / viewport.zoom) * scale}
          height={(canvasSize.h / viewport.zoom) * scale}
          rx={2} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth={1}
        />
      </svg>
    </div>
  );
}

/* ── Main WorkflowBuilder ─────────────────────────────────────────────────── */
export default function WorkflowBuilder() {
  const { token } = useAuth();
  const h = { Authorization: `Bearer ${token}` };
  const hj = { ...h, "Content-Type": "application/json" };

  // Data
  const [agents, setAgents]       = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [nodes, setNodes]         = useState([]);
  const [edges, setEdges]         = useState([]);
  const [teams, setTeams]         = useState([]);
  const [wfName, setWfName]       = useState("Untitled Workflow");
  const [wfDesc, setWfDesc]       = useState("");
  const [current, setCurrent]     = useState(null);
  const [loading, setLoading]     = useState(true);

  // UI state
  const [selectedNode, setSelectedNode]   = useState(null);
  const [selectedTeam, setSelectedTeam]   = useState(null);
  const [connecting, setConnecting]       = useState(null);
  const [agentSearch, setAgentSearch]     = useState("");
  const [activePanel, setActivePanel]     = useState("palette"); // "palette" | "workflows" | "config"
  const [showTemplates, setShowTemplates] = useState(false);
  const [runState, setRunState]           = useState(null);
  const [runHistory, setRunHistory]       = useState([]);

  // Canvas pan/zoom
  const [vp, setVp] = useState({ x: 0, y: 0, zoom: 1 });
  const canvasRef = useRef(null);
  const draggingNode = useRef(null);
  const panStart = useRef(null);
  const lastMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    Promise.all([
      fetch(`${API}/agents`, { headers: h }).then(r => r.ok ? r.json() : []),
      fetch(`${API}/kernel/workflows`, { headers: h }).then(r => r.ok ? r.json() : []),
    ]).then(([ag, wf]) => {
      setAgents(Array.isArray(ag) ? ag : []);
      setWorkflows(Array.isArray(wf) ? wf : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  // Network groups
  const networkGroups = {};
  agents.forEach(a => { const net = a.network || "ungrouped"; if (!networkGroups[net]) networkGroups[net] = []; networkGroups[net].push(a); });
  const filteredAgents = agentSearch ? agents.filter(a => (a.name + " " + a.role).toLowerCase().includes(agentSearch.toLowerCase())) : null;

  /* ── Canvas coordinate transform ── */
  const toCanvas = (clientX, clientY) => {
    const rect = canvasRef.current?.getBoundingClientRect() || { left: 0, top: 0 };
    return { x: (clientX - rect.left - vp.x) / vp.zoom, y: (clientY - rect.top - vp.y) / vp.zoom };
  };

  /* ── Node actions ── */
  const addNode = (type, x, y, extraData = {}) => {
    const n = { id: uid(), type, name: NODE_TYPES[type]?.label || type, x, y, data: { ...NODE_DEFAULTS[type], ...extraData } };
    setNodes(p => [...p, n]);
    setSelectedNode(n.id);
    setActivePanel("config");
    return n;
  };

  const addAgentNode = (agent, x, y) => {
    const n = { id: uid(), type: "agent", name: agent.name, x, y,
      data: { ...NODE_DEFAULTS.agent, agent_id: agent.agent_id, task: "", avatar: agent.avatar, role: agent.role, network: agent.network } };
    setNodes(p => [...p, n]);
    setSelectedNode(n.id);
    setActivePanel("config");
  };

  const removeNode = (nodeId) => {
    setNodes(p => p.filter(n => n.id !== nodeId));
    setEdges(p => p.filter(e => e.source !== nodeId && e.target !== nodeId));
    if (selectedNode === nodeId) { setSelectedNode(null); setActivePanel("palette"); }
  };

  const updateNode = (nodeId, data, name) => {
    setNodes(p => p.map(n => n.id === nodeId ? { ...n, data, ...(name !== undefined ? { name } : {}) } : n));
  };

  const addEdge = (source, target) => {
    if (source === target) return;
    if (edges.find(e => e.source === source && e.target === target)) return;
    setEdges(p => [...p, { id: uid(), source, target }]);
  };

  /* ── Team actions ── */
  const addTeam = () => {
    const t = { id: uid(), name: "Team " + (teams.length + 1), color: ["#4fd1c5","#a78bfa","#f59e0b","#60a5fa","#34d399","#f472b6"][teams.length % 6], x: 200, y: 150, width: 500, height: 300 };
    setTeams(p => [...p, t]);
    setSelectedTeam(t.id);
  };
  const updateTeam = (id, updates) => setTeams(p => p.map(t => t.id === id ? { ...t, ...updates } : t));
  const deleteTeam = (id) => { setTeams(p => p.filter(t => t.id !== id)); if (selectedTeam === id) setSelectedTeam(null); };

  /* ── Mouse events ── */
  const onCanvasMouseDown = (e) => {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      panStart.current = { x: e.clientX - vp.x, y: e.clientY - vp.y };
      e.preventDefault(); return;
    }
    if (connecting) { setConnecting(null); return; }
    setSelectedNode(null); setSelectedTeam(null);
    if (activePanel === "config") setActivePanel("palette");
  };

  const onNodeMouseDown = (e, nodeId) => {
    e.stopPropagation();
    if (connecting) { addEdge(connecting, nodeId); setConnecting(null); return; }
    setSelectedNode(nodeId);
    setActivePanel("config");
    setSelectedTeam(null);
    draggingNode.current = nodeId;
    lastMouse.current = { x: e.clientX, y: e.clientY };
  };

  const onMouseMove = useCallback((e) => {
    if (panStart.current) {
      setVp(p => ({ ...p, x: e.clientX - panStart.current.x, y: e.clientY - panStart.current.y }));
      return;
    }
    if (!draggingNode.current) return;
    const dx = (e.clientX - lastMouse.current.x) / vp.zoom;
    const dy = (e.clientY - lastMouse.current.y) / vp.zoom;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    setNodes(p => p.map(n => n.id === draggingNode.current ? { ...n, x: n.x + dx, y: n.y + dy } : n));
  }, [vp.zoom]);

  const onMouseUp = useCallback(() => { draggingNode.current = null; panStart.current = null; }, []);

  const onWheel = (e) => {
    e.preventDefault();
    const rect = canvasRef.current.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const factor = e.deltaY < 0 ? 1.1 : 0.91;
    setVp(prev => {
      const nz = Math.max(0.2, Math.min(3, prev.zoom * factor));
      return { zoom: nz, x: mx - (mx - prev.x) * (nz / prev.zoom), y: my - (my - prev.y) * (nz / prev.zoom) };
    });
  };

  useEffect(() => {
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => { window.removeEventListener("mousemove", onMouseMove); window.removeEventListener("mouseup", onMouseUp); };
  }, [onMouseMove, onMouseUp]);

  /* ── Drop from palette ── */
  const onDragStart = (e, payload) => { e.dataTransfer.setData("wf_payload", JSON.stringify(payload)); };
  const onDrop = (e) => {
    e.preventDefault();
    const raw = e.dataTransfer.getData("wf_payload"); if (!raw) return;
    const payload = JSON.parse(raw);
    const pos = toCanvas(e.clientX, e.clientY);
    if (payload.agentId) {
      const agent = agents.find(a => a.agent_id === payload.agentId);
      if (agent) addAgentNode(agent, pos.x - 110, pos.y - 40);
    } else if (payload.nodeType) {
      addNode(payload.nodeType, pos.x - 110, pos.y - 40);
    }
  };

  /* ── Save / Load / Run ── */
  const saveWorkflow = async () => {
    const body = { name: wfName, description: wfDesc, nodes, edges, teams };
    try {
      if (current) {
        const res = await fetch(`${API}/kernel/workflows/${current}`, { method: "PUT", headers: hj, body: JSON.stringify(body) });
        if (res.ok) { toast.success("Saved"); const wfs = await fetch(`${API}/kernel/workflows`, { headers: h }).then(r => r.json()); setWorkflows(wfs); }
      } else {
        const res = await fetch(`${API}/kernel/workflows`, { method: "POST", headers: hj, body: JSON.stringify(body) });
        if (res.ok) { const wf = await res.json(); setCurrent(wf.workflow_id); toast.success("Workflow created"); const wfs = await fetch(`${API}/kernel/workflows`, { headers: h }).then(r => r.json()); setWorkflows(wfs); }
      }
    } catch { toast.error("Save failed"); }
  };

  const loadWorkflow = (wf) => {
    setCurrent(wf.workflow_id); setWfName(wf.name); setWfDesc(wf.description || "");
    setNodes(wf.nodes || []); setEdges(wf.edges || []); setTeams(wf.teams || []);
    setSelectedNode(null); setRunState(null); setRunHistory([]);
    toast.success(`Loaded: ${wf.name}`);
  };

  const deleteWorkflow = async (wfId) => {
    await fetch(`${API}/kernel/workflows/${wfId}`, { method: "DELETE", headers: h });
    setWorkflows(p => p.filter(w => w.workflow_id !== wfId));
    if (current === wfId) newWorkflow();
    toast.success("Deleted");
  };

  const newWorkflow = () => {
    setCurrent(null); setWfName("Untitled Workflow"); setWfDesc("");
    setNodes([]); setEdges([]); setTeams([]); setSelectedNode(null); setRunState(null);
  };

  const runWorkflow = async () => {
    if (!current || nodes.length === 0) return;
    await saveWorkflow();
    try {
      const res = await fetch(`${API}/kernel/workflows/${current}/run`, { method: "POST", headers: h });
      if (res.ok) { const run = await res.json(); setRunState(run); pollRun(run.run_id); toast.success("Workflow started"); }
    } catch { toast.error("Run failed"); }
  };

  const pollRun = async (runId) => {
    for (let i = 0; i < 120; i++) {
      await new Promise(r => setTimeout(r, 1000));
      try {
        const res = await fetch(`${API}/kernel/workflow-runs/${runId}`, { headers: h });
        if (res.ok) {
          const run = await res.json();
          setRunState(run);
          if (run.status === "completed" || run.status === "failed") {
            toast[run.status === "completed" ? "success" : "error"](`Workflow ${run.status}`);
            const rhRes = await fetch(`${API}/kernel/workflows/${current}/runs`, { headers: h });
            if (rhRes.ok) setRunHistory(await rhRes.json());
            break;
          }
        }
      } catch {}
    }
  };

  /* ── Match template agent slot to a real agent from the user's roster ── */
  const matchAgentForSlot = (slotName, slotTask) => {
    if (!agents.length) return null;
    const text = `${slotName} ${slotTask || ""}`.toLowerCase();
    const keywords = text.split(/[\s_]+/).filter(w => w.length > 3);
    // Score each agent by keyword matches in name + role + network
    const scored = agents.map(a => {
      const hay = `${a.name || ""} ${a.role || ""} ${a.network || ""}`.toLowerCase();
      const score = keywords.reduce((acc, kw) => acc + (hay.includes(kw) ? 1 : 0), 0);
      return { a, score };
    });
    scored.sort((x, y) => y.score - x.score);
    return scored[0]?.score > 0 ? scored[0].a : agents[Math.floor(Math.random() * agents.length)];
  };

  /* ── Load template ── */
  const loadTemplate = (tpl) => {
    newWorkflow();
    setWfName(tpl.name);
    const nodeIds = tpl.nodes.map(() => uid());
    const newNodes = tpl.nodes.map((n, i) => {
      let data = { ...NODE_DEFAULTS[n.type], ...n.data };
      let name = n.name;
      // For agent nodes, match to a real agent from the roster
      if (n.type === "agent" && agents.length > 0) {
        const matched = matchAgentForSlot(n.name, n.data?.task);
        if (matched) {
          data = { ...data, agent_id: matched.agent_id, avatar: matched.avatar || null, role: matched.role || "", network: matched.network || "" };
          name = matched.name || n.name;
        }
      }
      return { id: nodeIds[i], type: n.type, name, x: n.x, y: n.y, data };
    });
    const newEdges = tpl.edges.map(([s, t]) => ({ id: uid(), source: nodeIds[s], target: nodeIds[t] }));
    const newTeams = (tpl.teams || []).map(t => ({
      id: uid(), name: t.name, color: t.color,
      x: Math.min(...t.nodeIndices.map(i => tpl.nodes[i].x)) - 30,
      y: Math.min(...t.nodeIndices.map(i => tpl.nodes[i].y)) - 50,
      width: Math.max(...t.nodeIndices.map(i => tpl.nodes[i].x)) - Math.min(...t.nodeIndices.map(i => tpl.nodes[i].x)) + 290,
      height: Math.max(...t.nodeIndices.map(i => tpl.nodes[i].y)) - Math.min(...t.nodeIndices.map(i => tpl.nodes[i].y)) + 160,
    }));
    setNodes(newNodes); setEdges(newEdges); setTeams(newTeams);
    setShowTemplates(false); toast.success(`Template loaded: ${tpl.name}`);
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", flexDirection: "column", gap: 12 }}>
      <div style={{ position: "relative", width: 40, height: 40 }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid transparent", borderTopColor: "#4fd1c5", animation: "wf_spin 0.9s linear infinite" }} />
        <div style={{ position: "absolute", inset: 6, borderRadius: "50%", border: "2px solid transparent", borderBottomColor: "#a78bfa", animation: "wf_spin 0.6s linear infinite reverse" }} />
      </div>
      <p style={{ fontSize: 12, color: "#475569" }}>Loading workflow engine…</p>
      <style>{`@keyframes wf_spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  const selectedNodeObj = nodes.find(n => n.id === selectedNode);

  return (
    <div style={{ display: "flex", height: "calc(100vh - 64px)", background: "#030712", overflow: "hidden", position: "relative" }} data-testid="workflow-builder">
      <style>{`
        @keyframes wf_spin  { to { transform: rotate(360deg); } }
        @keyframes wf_flow  { from { stroke-dashoffset: 24; } to { stroke-dashoffset: 0; } }
        @keyframes wf_pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.5)} }
        @keyframes wf_fadein{ from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      {/* ═══ LEFT SIDEBAR ═══ */}
      <div style={{ width: 220, background: "rgba(8,12,24,0.95)", borderRight: "1px solid rgba(255,255,255,0.06)", display: "flex", flexDirection: "column", zIndex: 10, flexShrink: 0 }}>
        {/* Sidebar tabs */}
        <div style={{ display: "flex", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
          {[["palette","Nodes"],["workflows","Flows"]].map(([k, label]) => (
            <button key={k} onClick={() => setActivePanel(k)}
              style={{ flex: 1, padding: "10px 0", fontSize: 10, fontWeight: 700, background: "none", border: "none", cursor: "pointer", color: activePanel === k ? "#4fd1c5" : "#475569", letterSpacing: "0.08em", textTransform: "uppercase", borderBottom: activePanel === k ? "2px solid #4fd1c5" : "2px solid transparent", transition: "all 0.15s" }}>
              {label}
            </button>
          ))}
        </div>

        {/* Palette panel */}
        {(activePanel === "palette" || activePanel === "config") && (
          <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
            {/* Node types */}
            <div style={{ padding: "10px 10px 6px", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
              <p style={{ fontSize: 9, fontWeight: 700, color: "#334155", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 6 }}>Node Types</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
                {Object.entries(NODE_TYPES).filter(([k]) => k !== "note").map(([type, { label, Icon, color }]) => (
                  <div key={type} draggable onDragStart={e => onDragStart(e, { nodeType: type })}
                    style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 8px", borderRadius: 8, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)", cursor: "grab", transition: "background 0.15s" }}
                    onMouseEnter={e => { e.currentTarget.style.background = `${color}14`; e.currentTarget.style.borderColor = `${color}30`; }}
                    onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.05)"; }}>
                    <Icon style={{ width: 11, height: 11, color, flexShrink: 0 }} />
                    <span style={{ fontSize: 9, color: "#94a3b8", fontWeight: 600 }}>{label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Agent search */}
            <div style={{ padding: "8px 10px 4px" }}>
              <p style={{ fontSize: 9, fontWeight: 700, color: "#334155", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 6 }}>Agents</p>
              <div style={{ position: "relative" }}>
                <Search style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", width: 11, height: 11, color: "#475569", pointerEvents: "none" }} />
                <input value={agentSearch} onChange={e => setAgentSearch(e.target.value)}
                  placeholder="Search agents…"
                  style={{ width: "100%", paddingLeft: 26, height: 30, borderRadius: 8, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", color: "#e2e8f0", fontSize: 11, outline: "none", boxSizing: "border-box" }}
                />
              </div>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "4px 6px 10px" }}>
              {filteredAgents ? filteredAgents.slice(0, 30).map(a => {
                const initials = (a.name || "??").split(" ").map(w=>w[0]||"").join("").slice(0,2).toUpperCase();
                const netColor = NET_COLORS[a.network] || "#4fd1c5";
                return (
                  <div key={a.agent_id} draggable onDragStart={e => onDragStart(e, { agentId: a.agent_id })}
                    style={{ display: "flex", alignItems: "center", gap: 7, padding: "6px 8px", borderRadius: 8, cursor: "grab", margin: "2px 0", transition: "background 0.12s" }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(79,209,197,0.07)"}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                    {a.avatar
                      ? <img src={a.avatar} alt="" style={{ width: 20, height: 20, borderRadius: "50%", objectFit: "cover", flexShrink: 0, border: `1px solid ${netColor}40` }} />
                      : <div style={{ width: 20, height: 20, borderRadius: "50%", background: `${netColor}22`, border: `1px solid ${netColor}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 7, color: netColor, fontWeight: 800, flexShrink: 0 }}>{initials}</div>}
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <p style={{ fontSize: 10, color: "#e2e8f0", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name || "Unnamed Agent"}</p>
                      <p style={{ fontSize: 8, color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.role || a.network?.replace(/_/g," ") || "Agent"}</p>
                    </div>
                  </div>
                );
              }) : Object.entries(networkGroups).sort(([a],[b]) => a.localeCompare(b)).slice(0,15).map(([net, netAgents]) => (
                <div key={net} style={{ marginBottom: 6 }}>
                  <p style={{ fontSize: 8, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", padding: "4px 8px 2px", color: NET_COLORS[net] || "#4fd1c5" }}>{net.replace(/_/g," ")} ({netAgents.length})</p>
                  {netAgents.slice(0, 4).map(a => {
                    const initials = (a.name || "??").split(" ").map(w=>w[0]||"").join("").slice(0,2).toUpperCase();
                    const nc = NET_COLORS[net] || "#4fd1c5";
                    return (
                      <div key={a.agent_id} draggable onDragStart={e => onDragStart(e, { agentId: a.agent_id })}
                        style={{ display: "flex", alignItems: "center", gap: 7, padding: "5px 8px", borderRadius: 7, cursor: "grab", transition: "background 0.12s" }}
                        onMouseEnter={e => e.currentTarget.style.background = `${nc}10`}
                        onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                        {a.avatar
                          ? <img src={a.avatar} alt="" style={{ width: 18, height: 18, borderRadius: "50%", objectFit: "cover", flexShrink: 0, border: `1px solid ${nc}40` }} />
                          : <div style={{ width: 18, height: 18, borderRadius: "50%", background: `${nc}22`, border: `1px solid ${nc}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 6, color: nc, fontWeight: 800, flexShrink: 0 }}>{initials}</div>}
                        <div style={{ minWidth: 0, flex: 1 }}>
                          <p style={{ fontSize: 9, color: "#e2e8f0", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.name || "Unnamed Agent"}</p>
                          <p style={{ fontSize: 8, color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.role || "Agent"}</p>
                        </div>
                      </div>
                    );
                  })}
                  {netAgents.length > 4 && <p style={{ fontSize: 8, color: "#334155", padding: "2px 8px" }}>+{netAgents.length - 4} more — search to find</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Saved Workflows panel */}
        {activePanel === "workflows" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <div style={{ padding: "8px 10px", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <button onClick={newWorkflow}
                style={{ width: "100%", padding: "8px 0", borderRadius: 9, background: "rgba(79,209,197,0.1)", border: "1px solid rgba(79,209,197,0.2)", color: "#4fd1c5", fontSize: 11, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                <Plus style={{ width: 12, height: 12 }} /> New Workflow
              </button>
            </div>
            <div style={{ flex: 1, overflowY: "auto", padding: "6px 8px" }}>
              {workflows.length === 0 && <p style={{ fontSize: 10, color: "#334155", textAlign: "center", padding: "24px 0" }}>No saved workflows</p>}
              {workflows.map(wf => (
                <div key={wf.workflow_id}
                  onClick={() => loadWorkflow(wf)}
                  style={{ padding: "9px 10px", borderRadius: 10, cursor: "pointer", background: current === wf.workflow_id ? "rgba(79,209,197,0.1)" : "transparent", border: `1px solid ${current === wf.workflow_id ? "rgba(79,209,197,0.25)" : "transparent"}`, marginBottom: 3, transition: "all 0.15s", position: "relative" }}
                  onMouseEnter={e => { if (current !== wf.workflow_id) e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
                  onMouseLeave={e => { if (current !== wf.workflow_id) e.currentTarget.style.background = "transparent"; }}>
                  <p style={{ fontSize: 11, fontWeight: 600, color: current === wf.workflow_id ? "#4fd1c5" : "#e2e8f0", marginBottom: 2 }}>{wf.name}</p>
                  <p style={{ fontSize: 9, color: "#475569" }}>{(wf.nodes||[]).length} nodes · {(wf.edges||[]).length} edges</p>
                  <button onClick={e => { e.stopPropagation(); deleteWorkflow(wf.workflow_id); }}
                    style={{ position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "#475569", padding: 4, opacity: 0, transition: "opacity 0.15s" }}
                    onMouseEnter={e => { e.currentTarget.style.opacity = 1; e.currentTarget.style.color = "#ef4444"; }}
                    onMouseLeave={e => { e.currentTarget.style.opacity = 0; }}>
                    <Trash2 style={{ width: 11, height: 11 }} />
                  </button>
                </div>
              ))}
            </div>
            {/* Run History */}
            {runHistory.length > 0 && (
              <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)", padding: "8px 10px" }}>
                <p style={{ fontSize: 8, fontWeight: 700, color: "#334155", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>Run History</p>
                {runHistory.slice(0, 5).map(rh => (
                  <div key={rh.run_id} style={{ display: "flex", alignItems: "center", gap: 6, padding: "3px 0" }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: rh.status === "completed" ? "#34d399" : rh.status === "failed" ? "#ef4444" : "#f59e0b" }} />
                    <span style={{ fontSize: 9, color: "#475569" }}>{rh.status} — {rh.total_steps || "?"} steps</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ═══ CENTER: TOOLBAR + CANVAS ═══ */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Toolbar */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 12px", borderBottom: "1px solid rgba(255,255,255,0.06)", background: "rgba(8,12,24,0.9)", backdropFilter: "blur(12px)", zIndex: 10, flexShrink: 0 }}>
          <input value={wfName} onChange={e => setWfName(e.target.value)}
            style={{ background: "transparent", border: "none", outline: "none", color: "#f1f5f9", fontSize: 14, fontWeight: 700, fontFamily: "Outfit, sans-serif", maxWidth: 220, minWidth: 80 }}
          />
          <span style={{ fontSize: 10, color: "#334155" }}>{nodes.length}n · {edges.length}e · {teams.length}t</span>

          {connecting && <span style={{ fontSize: 10, color: "#f59e0b", animation: "wf_pulse 1s ease-in-out infinite" }}>Click a node to connect…  [Esc to cancel]</span>}

          <div style={{ flex: 1 }} />

          {/* Templates */}
          <button onClick={() => setShowTemplates(v => !v)}
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 10px", borderRadius: 8, background: showTemplates ? "rgba(167,139,250,0.15)" : "rgba(255,255,255,0.04)", border: `1px solid ${showTemplates ? "rgba(167,139,250,0.3)" : "rgba(255,255,255,0.08)"}`, color: showTemplates ? "#a78bfa" : "#64748b", fontSize: 11, cursor: "pointer", transition: "all 0.15s" }}>
            <Sparkles style={{ width: 12, height: 12 }} /> Templates
          </button>

          {/* Add Team */}
          <button onClick={addTeam}
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 10px", borderRadius: 8, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", color: "#64748b", fontSize: 11, cursor: "pointer", transition: "all 0.15s" }}
            onMouseEnter={e => { e.currentTarget.style.background = "rgba(79,209,197,0.1)"; e.currentTarget.style.color = "#4fd1c5"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.color = "#64748b"; }}>
            <Users style={{ width: 12, height: 12 }} /> Team
          </button>

          {/* Zoom controls */}
          <div style={{ display: "flex", alignItems: "center", gap: 3, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "3px 6px" }}>
            <button onClick={() => setVp(p => ({ ...p, zoom: Math.max(0.2, p.zoom / 1.2) }))} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", padding: 2, display: "flex" }}><ZoomOut style={{ width: 12, height: 12 }} /></button>
            <span style={{ fontSize: 10, color: "#64748b", minWidth: 36, textAlign: "center" }}>{Math.round(vp.zoom * 100)}%</span>
            <button onClick={() => setVp(p => ({ ...p, zoom: Math.min(3, p.zoom * 1.2) }))} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", padding: 2, display: "flex" }}><ZoomIn style={{ width: 12, height: 12 }} /></button>
            <button onClick={() => setVp({ x: 60, y: 60, zoom: 1 })} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748b", padding: 2, display: "flex" }}><RotateCcw style={{ width: 11, height: 11 }} /></button>
          </div>

          <button onClick={saveWorkflow}
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 12px", borderRadius: 8, background: "rgba(79,209,197,0.1)", border: "1px solid rgba(79,209,197,0.25)", color: "#4fd1c5", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
            <Save style={{ width: 12, height: 12 }} /> Save
          </button>

          {current && nodes.filter(n => n.type !== "note").length > 0 && (
            <button onClick={runWorkflow} disabled={runState?.status === "running"}
              style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 12px", borderRadius: 8, background: runState?.status === "running" ? "rgba(251,191,36,0.15)" : "rgba(52,211,153,0.15)", border: `1px solid ${runState?.status === "running" ? "rgba(251,191,36,0.3)" : "rgba(52,211,153,0.3)"}`, color: runState?.status === "running" ? "#fbbf24" : "#34d399", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
              {runState?.status === "running"
                ? <><Clock style={{ width: 12, height: 12, animation: "wf_spin 1s linear infinite" }} /> Running…</>
                : <><Play style={{ width: 12, height: 12 }} /> Run</>}
            </button>
          )}
        </div>

        {/* Templates panel */}
        {showTemplates && (
          <div style={{ position: "absolute", top: 58, left: 220, right: 0, zIndex: 100, background: "rgba(8,12,22,0.98)", backdropFilter: "blur(24px)", borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "16px 20px", animation: "wf_fadein 0.15s ease" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <p style={{ fontSize: 13, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>Workflow Templates</p>
              <button onClick={() => setShowTemplates(false)} style={{ background: "none", border: "none", cursor: "pointer", color: "#475569" }}><X style={{ width: 14, height: 14 }} /></button>
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              {TEMPLATES.map(tpl => (
                <div key={tpl.name} onClick={() => loadTemplate(tpl)}
                  style={{ width: 200, padding: 14, borderRadius: 12, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", cursor: "pointer", transition: "all 0.15s" }}
                  onMouseEnter={e => { e.currentTarget.style.background = "rgba(79,209,197,0.08)"; e.currentTarget.style.borderColor = "rgba(79,209,197,0.25)"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"; }}>
                  <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>{tpl.name}</p>
                  <p style={{ fontSize: 10, color: "#475569", lineHeight: 1.4 }}>{tpl.desc}</p>
                  <p style={{ fontSize: 9, color: "#334155", marginTop: 8 }}>{tpl.nodes.length} nodes · {tpl.edges.length} edges</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Canvas */}
        <div
          ref={canvasRef}
          onDrop={onDrop}
          onDragOver={e => e.preventDefault()}
          onMouseDown={onCanvasMouseDown}
          onWheel={onWheel}
          style={{
            flex: 1, overflow: "hidden", position: "relative", cursor: panStart.current ? "grabbing" : connecting ? "crosshair" : "default",
            backgroundImage: "radial-gradient(circle, rgba(79,209,197,0.08) 1px, transparent 1px)",
            backgroundSize: `${28 * vp.zoom}px ${28 * vp.zoom}px`,
            backgroundPosition: `${vp.x}px ${vp.y}px`,
          }}
        >
          {/* Transformed layer */}
          <div style={{ position: "absolute", top: 0, left: 0, transformOrigin: "0 0", transform: `translate(${vp.x}px, ${vp.y}px) scale(${vp.zoom})` }}>
            {/* Team containers (below nodes) */}
            {teams.map(team => (
              <TeamContainer key={team.id} team={team} isSelected={selectedTeam === team.id}
                onSelect={() => { setSelectedTeam(team.id); setSelectedNode(null); }}
                onUpdate={u => updateTeam(team.id, u)}
                onDelete={() => deleteTeam(team.id)}
              />
            ))}

            {/* SVG edge layer */}
            <svg style={{ position: "absolute", top: 0, left: 0, overflow: "visible", pointerEvents: "all", zIndex: 1 }} width={4000} height={3000}>
              <defs>
                <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L6,3 z" fill="rgba(79,209,197,0.6)" />
                </marker>
              </defs>
              {edges.map(edge => {
                const sn = nodes.find(n => n.id === edge.source);
                const tn = nodes.find(n => n.id === edge.target);
                const isRunning = runState?.node_states?.[edge.target]?.status === "running";
                const isCompleted = runState?.node_states?.[edge.target]?.status === "completed";
                const isFailed = runState?.node_states?.[edge.target]?.status === "failed";
                return (
                  <EdgeLine key={edge.id} sourceNode={sn} targetNode={tn} edge={edge}
                    isRunning={isRunning} isCompleted={isCompleted} isFailed={isFailed}
                    onDelete={() => setEdges(p => p.filter(e => e.id !== edge.id))}
                  />
                );
              })}
            </svg>

            {/* Nodes */}
            {nodes.map(node => (
              <NodeCard
                key={node.id}
                node={node}
                isSelected={selectedNode === node.id}
                isConnecting={connecting === node.id}
                nodeState={runState?.node_states?.[node.id]}
                onMouseDown={e => onNodeMouseDown(e, node.id)}
                onConnect={nodeId => setConnecting(prev => prev === nodeId ? null : nodeId)}
                onDelete={removeNode}
              />
            ))}
          </div>

          {/* Empty state */}
          {nodes.length === 0 && (
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
              <div style={{ textAlign: "center" }}>
                <div style={{ width: 64, height: 64, borderRadius: 18, background: "rgba(79,209,197,0.08)", border: "1px solid rgba(79,209,197,0.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
                  <Sparkles style={{ width: 28, height: 28, color: "#4fd1c5", opacity: 0.6 }} />
                </div>
                <p style={{ fontSize: 15, fontWeight: 700, color: "#334155", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>Build your AI Workflow</p>
                <p style={{ fontSize: 12, color: "#1e293b" }}>Drag nodes from the left panel · Scroll to zoom · Alt+drag to pan</p>
                <p style={{ fontSize: 12, color: "#1e293b", marginTop: 4 }}>Or load a template → <span style={{ color: "#a78bfa" }}>Templates</span> button above</p>
              </div>
            </div>
          )}

          {/* Mini-map */}
          <MiniMap nodes={nodes} teams={teams} viewport={vp} canvasSize={{ w: canvasRef.current?.clientWidth || 800, h: canvasRef.current?.clientHeight || 600 }} />
        </div>
      </div>

      {/* ═══ RIGHT PANEL: Node Config ═══ */}
      {selectedNodeObj && (
        <div style={{ width: 260, background: "rgba(8,12,24,0.95)", borderLeft: "1px solid rgba(255,255,255,0.06)", display: "flex", flexDirection: "column", overflow: "hidden", zIndex: 10, flexShrink: 0, animation: "wf_fadein 0.15s ease" }}>
          <NodeConfigPanel
            node={selectedNodeObj}
            workflows={workflows}
            onUpdate={updateNode}
            onClose={() => { setSelectedNode(null); }}
          />
        </div>
      )}

      {/* Team config panel */}
      {selectedTeam && !selectedNode && (() => {
        const team = teams.find(t => t.id === selectedTeam);
        if (!team) return null;
        return (
          <div style={{ width: 220, background: "rgba(8,12,24,0.95)", borderLeft: "1px solid rgba(255,255,255,0.06)", padding: "14px 14px", zIndex: 10, flexShrink: 0, animation: "wf_fadein 0.15s ease" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0" }}>Team Settings</p>
              <button onClick={() => setSelectedTeam(null)} style={{ background: "none", border: "none", cursor: "pointer", color: "#475569" }}><X style={{ width: 12, height: 12 }} /></button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div>
                <label style={lbl}>Team Name</label>
                <input value={team.name} onChange={e => updateTeam(team.id, { name: e.target.value })} style={inp} />
              </div>
              <div>
                <label style={lbl}>Color</label>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {["#4fd1c5","#a78bfa","#f59e0b","#60a5fa","#34d399","#f472b6","#f97316","#ef4444"].map(c => (
                    <button key={c} onClick={() => updateTeam(team.id, { color: c })}
                      style={{ width: 22, height: 22, borderRadius: "50%", background: c, border: team.color === c ? "2px solid #fff" : "2px solid transparent", cursor: "pointer" }} />
                  ))}
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                <div><label style={lbl}>Width</label><input type="number" value={team.width} onChange={e => updateTeam(team.id, { width: parseInt(e.target.value) })} style={inp} /></div>
                <div><label style={lbl}>Height</label><input type="number" value={team.height} onChange={e => updateTeam(team.id, { height: parseInt(e.target.value) })} style={inp} /></div>
              </div>
              <button onClick={() => deleteTeam(team.id)}
                style={{ padding: "8px 0", borderRadius: 8, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)", color: "#f87171", fontSize: 11, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}>
                <Trash2 style={{ width: 11, height: 11 }} /> Delete Team
              </button>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
