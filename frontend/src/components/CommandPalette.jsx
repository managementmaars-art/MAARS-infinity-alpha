import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  Search, LayoutDashboard, Rocket, MessageSquare, Users, Brain, Cpu,
  Activity, Gauge, Radio, Code, Palette, PenTool, FileCheck, Package,
  ListTodo, BarChart3, Settings, Info, Shield, Bot, ArrowRight,
  CornerDownLeft, ChevronUp, ChevronDown, X, Zap, Plus, Command
} from "lucide-react";

const PAGE_ITEMS = [
  { id: "dashboard", label: "Dashboard", desc: "Command center overview", icon: LayoutDashboard, to: "/dashboard", category: "pages" },
  { id: "projects", label: "Projects", desc: "Autonomous project management", icon: Rocket, to: "/projects", category: "pages" },
  { id: "chat", label: "Chat", desc: "Talk to AI agents", icon: MessageSquare, to: "/chat", category: "pages" },
  { id: "agents", label: "Agents", desc: "View all 41 AI agents", icon: Users, to: "/agents", category: "pages" },
  { id: "workspace", label: "Workspace Brain", desc: "Agent workspace config", icon: Brain, to: "/workspace", category: "pages" },
  { id: "brain-profiles", label: "Brain Profiles", desc: "Custom brain configurations", icon: Cpu, to: "/brain-profiles", category: "pages" },
  { id: "collaborations", label: "Collaborations", desc: "Inter-agent collaboration logs", icon: Activity, to: "/collaborations", category: "pages" },
  { id: "kpi", label: "KPI Dashboard", desc: "Key performance indicators", icon: Gauge, to: "/kpi-dashboard", category: "pages" },
  { id: "activity", label: "Activity Monitor", desc: "Real-time agent activity", icon: Radio, to: "/activity-monitor", category: "pages" },
  { id: "vibe", label: "Vibe Coding", desc: "Build apps with AI", icon: Code, to: "/vibe-coding", category: "pages" },
  { id: "reference", label: "Reference Intelligence", desc: "Extract style blueprints", icon: Palette, to: "/reference-intelligence", category: "pages" },
  { id: "content", label: "Content Generator", desc: "Generate on-brand content", icon: PenTool, to: "/content-generator", category: "pages" },
  { id: "approvals", label: "Approvals", desc: "Task approval workflows", icon: FileCheck, to: "/approvals", category: "pages" },
  { id: "products", label: "Products", desc: "Product catalog", icon: Package, to: "/products", category: "pages" },
  { id: "tasks", label: "Tasks", desc: "Task management", icon: ListTodo, to: "/tasks", category: "pages" },
  { id: "insights", label: "My Insights", desc: "Analytics & insights", icon: BarChart3, to: "/insights", category: "pages" },
  { id: "team", label: "Team", desc: "Team management", icon: Users, to: "/team", category: "pages" },
  { id: "settings", label: "Settings", desc: "Account, LLM config, integrations", icon: Settings, to: "/settings", category: "pages" },
  { id: "about", label: "About", desc: "System documentation", icon: Info, to: "/about", category: "pages" },
  { id: "admin", label: "Admin Panel", desc: "Admin dashboard", icon: Shield, to: "/admin", category: "pages" },
];

const ACTION_ITEMS = [
  { id: "new-project", label: "Create New Project", desc: "Start a new AI project", icon: Plus, category: "actions", action: "navigate", to: "/projects" },
  { id: "new-content", label: "Generate Content", desc: "Create on-brand content", icon: PenTool, category: "actions", action: "navigate", to: "/content-generator" },
  { id: "new-app", label: "Build an App", desc: "Start vibe coding", icon: Code, category: "actions", action: "navigate", to: "/vibe-coding" },
  { id: "analyze-ref", label: "Analyze Reference", desc: "Extract style blueprint", icon: Palette, category: "actions", action: "navigate", to: "/reference-intelligence" },
];

const CATEGORY_ORDER = ["recent", "pages", "agents", "actions"];
const CATEGORY_LABELS = { recent: "Recent", pages: "Pages", agents: "Agents", actions: "Quick Actions" };

const CommandPalette = ({ open, onClose }) => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const inputRef = useRef(null);
  const listRef = useRef(null);
  const [query, setQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [agents, setAgents] = useState([]);
  const [recents, setRecents] = useState(() => {
    try { return JSON.parse(localStorage.getItem("maars_cmd_recents") || "[]"); } catch { return []; }
  });

  // Fetch agents once
  useEffect(() => {
    if (!token) return;
    fetch(`${API}/agents/public`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : [])
      .then(data => setAgents(data))
      .catch(() => {});
  }, [token]);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setQuery("");
      setSelectedIdx(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  // Build agent items
  const agentItems = useMemo(() =>
    agents.map(a => ({
      id: `agent-${a.agent_id}`,
      label: a.name,
      desc: a.role || a.specialty || "",
      icon: Bot,
      avatar: a.avatar,
      to: `/chat/${a.agent_id}`,
      category: "agents",
    })),
    [agents]
  );

  // Build recent items
  const recentItems = useMemo(() =>
    recents.slice(0, 5).map(r => {
      const found = [...PAGE_ITEMS, ...agentItems, ...ACTION_ITEMS].find(i => i.id === r);
      return found ? { ...found, category: "recent" } : null;
    }).filter(Boolean),
    [recents, agentItems]
  );

  // All items
  const allItems = useMemo(() => [...PAGE_ITEMS, ...agentItems, ...ACTION_ITEMS], [agentItems]);

  // Filter
  const filtered = useMemo(() => {
    if (!query.trim()) {
      // Show recents + all pages (limited) + actions
      return [...recentItems, ...PAGE_ITEMS.slice(0, 6), ...ACTION_ITEMS];
    }
    const q = query.toLowerCase();
    return allItems.filter(item =>
      item.label.toLowerCase().includes(q) ||
      item.desc.toLowerCase().includes(q) ||
      (item.category === "agents" && item.label.toLowerCase().includes(q))
    ).slice(0, 20);
  }, [query, allItems, recentItems]);

  // Group by category
  const grouped = useMemo(() => {
    const groups = {};
    for (const item of filtered) {
      if (!groups[item.category]) groups[item.category] = [];
      groups[item.category].push(item);
    }
    return CATEGORY_ORDER.filter(c => groups[c]?.length).map(c => ({ category: c, items: groups[c] }));
  }, [filtered]);

  // Flat list for keyboard navigation
  const flatList = useMemo(() => grouped.flatMap(g => g.items), [grouped]);

  // Clamp selectedIdx
  useEffect(() => {
    if (selectedIdx >= flatList.length) setSelectedIdx(Math.max(0, flatList.length - 1));
  }, [flatList.length, selectedIdx]);

  // Scroll selected into view
  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-idx="${selectedIdx}"]`);
    el?.scrollIntoView({ block: "nearest" });
  }, [selectedIdx]);

  const select = useCallback((item) => {
    // Save to recents
    const updated = [item.id, ...recents.filter(r => r !== item.id)].slice(0, 10);
    setRecents(updated);
    try { localStorage.setItem("maars_cmd_recents", JSON.stringify(updated)); } catch {}

    onClose();
    if (item.to) navigate(item.to);
  }, [navigate, onClose, recents]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIdx(i => Math.min(i + 1, flatList.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIdx(i => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (flatList[selectedIdx]) select(flatList[selectedIdx]);
    } else if (e.key === "Escape") {
      onClose();
    }
  }, [flatList, selectedIdx, select, onClose]);

  if (!open) return null;

  let globalIdx = 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]" data-testid="command-palette">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Palette */}
      <div className="relative w-full max-w-lg bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
          <Search className="w-4 h-4 text-zinc-500 shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={e => { setQuery(e.target.value); setSelectedIdx(0); }}
            onKeyDown={handleKeyDown}
            placeholder="Search pages, agents, actions..."
            className="flex-1 bg-transparent text-sm text-white placeholder-zinc-500 outline-none"
            data-testid="cmd-search-input"
          />
          <kbd className="hidden sm:flex items-center gap-1 px-1.5 py-0.5 rounded bg-zinc-800 border border-white/10 text-[10px] text-zinc-500">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div ref={listRef} className="max-h-[50vh] overflow-y-auto py-1" data-testid="command-results">
          {grouped.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <Search className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
              <p className="text-sm text-zinc-500">No results for "{query}"</p>
              <p className="text-xs text-zinc-600 mt-1">Try searching for a page, agent name, or action</p>
            </div>
          ) : (
            grouped.map(group => (
              <div key={group.category}>
                <div className="px-4 pt-2 pb-1">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-zinc-600">
                    {CATEGORY_LABELS[group.category]}
                  </p>
                </div>
                {group.items.map(item => {
                  const idx = globalIdx++;
                  const Icon = item.icon;
                  const isSelected = idx === selectedIdx;
                  return (
                    <button
                      key={`${item.category}-${item.id}`}
                      data-idx={idx}
                      onClick={() => select(item)}
                      onMouseEnter={() => setSelectedIdx(idx)}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${
                        isSelected ? "bg-indigo-500/10" : "hover:bg-white/[0.03]"
                      }`}
                      data-testid={`cmd-item-${item.id}`}
                    >
                      {item.avatar ? (
                        <img src={item.avatar} alt="" className="w-7 h-7 rounded-lg object-cover shrink-0" />
                      ) : (
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                          isSelected ? "bg-indigo-500/20" : "bg-zinc-800/80"
                        }`}>
                          <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-indigo-400" : "text-zinc-500"}`} />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm truncate ${isSelected ? "text-white" : "text-zinc-300"}`}>
                          {item.label}
                        </p>
                        <p className="text-[11px] text-zinc-600 truncate">{item.desc}</p>
                      </div>
                      {isSelected && (
                        <div className="flex items-center gap-1 text-[10px] text-zinc-500 shrink-0">
                          <CornerDownLeft className="w-3 h-3" />
                          <span>Open</span>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>

        {/* Footer hints */}
        <div className="px-4 py-2 border-t border-white/5 flex items-center gap-4 text-[10px] text-zinc-600">
          <span className="flex items-center gap-1"><ChevronUp className="w-3 h-3" /><ChevronDown className="w-3 h-3" /> Navigate</span>
          <span className="flex items-center gap-1"><CornerDownLeft className="w-3 h-3" /> Open</span>
          <span className="flex items-center gap-1"><span className="font-mono">ESC</span> Close</span>
          <span className="ml-auto flex items-center gap-1"><Command className="w-3 h-3" /> MAARS Command</span>
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;
