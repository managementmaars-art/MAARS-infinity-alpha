import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  Bot, MessageSquare, ListTodo, Users, Settings, LogOut, Menu, X,
  Shield, BarChart3, Package, Rocket, Brain, FileCheck, Cpu, LayoutDashboard,
  Activity, Gauge, Radio, Code, Palette, PenTool, Info,
  PanelLeftClose, PanelLeftOpen, Search, FileCode, Database,
  Network, GitBranch, Layers, Share2, Zap, Lock, CircuitBoard, DollarSign, Workflow,
  Globe, HardDrive, Megaphone, Plug, Building2, PieChart, Sparkles,
  CreditCard, Key, Mail, Paintbrush, BookOpen, ScrollText, TrendingUp,
  Diamond, Plus
} from "lucide-react";
import { useState, useEffect, useCallback, useRef } from "react";
import CommandPalette from "../CommandPalette";

const API = process.env.REACT_APP_BACKEND_URL;

function OrgSwitcher() {
  const { token, user } = useAuth();
  const [org, setOrg] = useState(null);
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/api/kernel/organization`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null).then(d => { if (d) setOrg(d); }).catch(() => {});
  }, [token]);

  const createOrg = async () => {
    if (!newName.trim()) return;
    const res = await fetch(`${API}/api/kernel/organization`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName.trim() }),
    });
    if (res.ok) {
      const data = await res.json();
      setOrg(data);
      setCreating(false);
      setNewName("");
    }
  };

  return (
    <div className="px-2 pt-2" data-testid="org-switcher">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left hover:bg-white/[0.04] border border-white/[0.04] transition-colors"
      >
        <div className="w-5 h-5 rounded bg-indigo-500/20 flex items-center justify-center shrink-0">
          <Building2 className="w-3 h-3 text-indigo-400" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-medium text-zinc-300 truncate">{org?.name || "Personal Workspace"}</p>
          <p className="text-[8px] text-zinc-600 truncate">{org ? `${org.members?.length || 1} members` : "Click to create org"}</p>
        </div>
        <svg className={`w-3 h-3 text-zinc-600 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </button>
      {open && (
        <div className="mt-1 p-2 rounded-lg bg-zinc-900/80 border border-white/[0.06]">
          {org ? (
            <div className="space-y-1">
              <div className="px-2 py-1 rounded bg-indigo-500/10 text-[10px] text-indigo-400">{org.name}</div>
              <div className="text-[9px] text-zinc-600 px-2">ID: {org.org_id?.slice(0, 12)}...</div>
              <div className="text-[9px] text-zinc-600 px-2">Members: {org.members?.length || 1}</div>
            </div>
          ) : creating ? (
            <div className="space-y-1">
              <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Organization name..." className="w-full bg-zinc-800 border border-white/10 rounded px-2 py-1 text-xs text-white" autoFocus onKeyDown={e => e.key === "Enter" && createOrg()} data-testid="org-name-input" />
              <div className="flex gap-1">
                <button onClick={createOrg} className="flex-1 px-2 py-1 bg-indigo-600 rounded text-[10px] text-white" data-testid="create-org-btn">Create</button>
                <button onClick={() => setCreating(false)} className="px-2 py-1 bg-zinc-800 rounded text-[10px] text-zinc-400">Cancel</button>
              </div>
            </div>
          ) : (
            <button onClick={() => setCreating(true)} className="w-full px-2 py-1.5 rounded text-[10px] text-indigo-400 hover:bg-indigo-500/10 text-left" data-testid="new-org-btn">
              + Create Organization
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function SidebarCredits({ collapsed }) {
  const { token } = useAuth();
  const [credits, setCredits] = useState(null);
  const [planName, setPlanName] = useState("Free");

  const fetchCredits = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/subscription`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setCredits(data.credits ?? 0);
        setPlanName(data.plan_info?.name ?? "Free");
      }
    } catch {}
  }, [token]);

  useEffect(() => {
    fetchCredits();
    const interval = setInterval(fetchCredits, 30000);
    return () => clearInterval(interval);
  }, [fetchCredits]);

  const navigate = useNavigate();

  if (collapsed) {
    return (
      <div className="px-2 pt-2">
        <button
          onClick={() => navigate("/pricing")}
          title={credits !== null ? `${credits.toFixed(0)} credits` : "Credits"}
          className="w-full flex items-center justify-center py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 hover:border-indigo-500/40 transition-colors"
          data-testid="sidebar-credits-btn"
        >
          <Diamond className="w-4 h-4 text-indigo-400" />
        </button>
      </div>
    );
  }

  return (
    <div className="px-2 pt-2" data-testid="sidebar-credits">
      <div className="rounded-lg bg-indigo-500/[0.06] border border-indigo-500/10 px-3 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Diamond className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-[12px] font-bold text-indigo-400 tabular-nums">
              {credits !== null ? credits.toFixed(2) : "..."}
            </span>
          </div>
          <span className="text-[9px] font-medium text-violet-400/60 px-1.5 py-0.5 rounded bg-violet-500/10">{planName}</span>
        </div>
        <button
          onClick={() => navigate("/pricing")}
          className="mt-1.5 w-full flex items-center justify-center gap-1 py-1 rounded-md bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-400 text-[10px] font-semibold transition-colors"
          data-testid="sidebar-buy-credits-btn"
        >
          <Plus className="w-3 h-3" /> Buy Credits
        </button>
      </div>
    </div>
  );
}

const navSections = [
  {
    label: null,
    items: [
      { icon: LayoutDashboard, label: "Dashboard", to: "/dashboard" },
    ],
  },
  {
    label: "Workspace",
    items: [
      { icon: Rocket, label: "Projects", to: "/projects" },
      { icon: MessageSquare, label: "Chat", to: "/chat" },
      { icon: ListTodo, label: "Tasks", to: "/tasks" },
      { icon: FileCheck, label: "Approvals", to: "/approvals" },
    ],
  },
  {
    label: "AI Tools",
    items: [
      { icon: Users, label: "Agents", to: "/agents" },
      { icon: Users, label: "Team Builder", to: "/team-builder" },
      { icon: Brain, label: "Workspace Brain", to: "/workspace" },
      { icon: Cpu, label: "Brain Profiles", to: "/brain-profiles" },
      { icon: Code, label: "Vibe Coding", to: "/vibe-coding" },
      { icon: Palette, label: "Reference Intel", to: "/reference-intelligence" },
      { icon: PenTool, label: "Content Generator", to: "/content-generator" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { icon: Layers, label: "Kernel", to: "/kernel" },
      { icon: Network, label: "Agent Networks", to: "/networks" },
      { icon: GitBranch, label: "Task Graphs", to: "/task-graphs" },
      { icon: Share2, label: "Knowledge Graph", to: "/knowledge-graph" },
      { icon: Shield, label: "Trust Scores", to: "/trust-scores" },
      { icon: Zap, label: "Execution Gateway", to: "/execution-gateway" },
      { icon: Workflow, label: "Workflow Builder", to: "/workflow-builder" },
      { icon: Megaphone, label: "Campaign Builder", to: "/campaigns" },
      { icon: Plug, label: "Integrations", to: "/integrations" },
      { icon: PieChart, label: "Analytics", to: "/analytics" },
      { icon: Sparkles, label: "Agent Suggestions", to: "/agent-suggestions" },
      { icon: Globe, label: "Environments", to: "/environments" },
      { icon: HardDrive, label: "Memory Hierarchy", to: "/memory-hierarchy" },
      { icon: Database, label: "Memory", to: "/memory" },
      { icon: Activity, label: "Collaborations", to: "/collaborations" },
      { icon: Gauge, label: "KPI Dashboard", to: "/kpi-dashboard" },
      { icon: Radio, label: "Activity Monitor", to: "/activity-monitor" },
      { icon: BarChart3, label: "My Insights", to: "/insights" },
    ],
  },
  {
    label: "Manage",
    items: [
      { icon: Package, label: "Products", to: "/products" },
      { icon: Users, label: "Team", to: "/team" },
      { icon: Building2, label: "Organization", to: "/organization" },
      { icon: Settings, label: "Settings", to: "/settings" },
      { icon: Info, label: "About", to: "/about" },
    ],
  },
];

const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [cmdOpen, setCmdOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try { return localStorage.getItem("maars_sidebar_collapsed") === "true"; } catch { return false; }
  });

  useEffect(() => {
    try { localStorage.setItem("maars_sidebar_collapsed", String(collapsed)); } catch {}
  }, [collapsed]);

  useEffect(() => {
    const handler = (e) => {
      const tag = e.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || e.target.isContentEditable) return;
      if (e.key === "/" && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        setCmdOpen(true);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCmdOpen(true);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const sidebarW = collapsed ? "w-[68px]" : "w-56";
  const mainML = collapsed ? "lg:ml-[68px]" : "lg:ml-56";

  const isActive = (to) => location.pathname === to || (to !== "/dashboard" && location.pathname.startsWith(to));

  const NavItem = ({ icon: Icon, label, to, onClick }) => {
    const active = isActive(to);
    return (
      <button
        onClick={onClick || (() => navigate(to))}
        title={collapsed ? label : undefined}
        className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-[7px] rounded-lg text-[13px] transition-all duration-150 relative ${
          active
            ? "bg-indigo-500/12 text-indigo-400 font-medium"
            : "text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-300"
        }`}
        data-testid={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
      >
        {active && !collapsed && (
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 rounded-r-full bg-indigo-500" />
        )}
        <Icon className={`w-[16px] h-[16px] shrink-0 ${active ? "" : ""}`} />
        {!collapsed && <span className="truncate">{label}</span>}
      </button>
    );
  };

  const SectionLabel = ({ label }) => {
    if (collapsed) return <div className="my-2 mx-3 h-px bg-white/[0.06]" />;
    return (
      <div className="mt-4 mb-1 px-3">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-600">{label}</span>
      </div>
    );
  };

  const renderNav = (closeMobile) => (
    <>
      {navSections.map((section, si) => (
        <div key={si}>
          {section.label && <SectionLabel label={section.label} />}
          {!section.label && si === 0 && null}
          {section.items.map(item => (
            <NavItem
              key={item.to}
              icon={item.icon}
              label={item.label}
              to={item.to}
              onClick={closeMobile ? () => { navigate(item.to); closeMobile(); } : undefined}
            />
          ))}
        </div>
      ))}
      {user?.is_admin && (
        <>
          {collapsed ? <div className="my-2 mx-3 h-px bg-white/[0.06]" /> : (
            <div className="mt-4 mb-1 px-3">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Admin</span>
            </div>
          )}
          <NavItem icon={Activity} label="Overview" to="/admin/overview" onClick={closeMobile ? () => { navigate("/admin/overview"); closeMobile(); } : undefined} />
          <NavItem icon={BarChart3} label="Analytics" to="/admin/analytics" onClick={closeMobile ? () => { navigate("/admin/analytics"); closeMobile(); } : undefined} />
          <NavItem icon={Users} label="Users" to="/admin/users" onClick={closeMobile ? () => { navigate("/admin/users"); closeMobile(); } : undefined} />
          <NavItem icon={Bot} label="Agents" to="/admin/agents" onClick={closeMobile ? () => { navigate("/admin/agents"); closeMobile(); } : undefined} />
          <NavItem icon={DollarSign} label="Transactions" to="/admin/transactions" onClick={closeMobile ? () => { navigate("/admin/transactions"); closeMobile(); } : undefined} />
          <NavItem icon={TrendingUp} label="Pricing & Packages" to="/admin/pricing-manager" onClick={closeMobile ? () => { navigate("/admin/pricing-manager"); closeMobile(); } : undefined} />
          <NavItem icon={Key} label="API Keys" to="/admin/api-keys" onClick={closeMobile ? () => { navigate("/admin/api-keys"); closeMobile(); } : undefined} />
          <NavItem icon={CreditCard} label="Payment Setup" to="/admin/payments" onClick={closeMobile ? () => { navigate("/admin/payments"); closeMobile(); } : undefined} />
          <NavItem icon={Mail} label="Email (SMTP)" to="/admin/smtp" onClick={closeMobile ? () => { navigate("/admin/smtp"); closeMobile(); } : undefined} />
          <NavItem icon={Paintbrush} label="Branding" to="/admin/branding" onClick={closeMobile ? () => { navigate("/admin/branding"); closeMobile(); } : undefined} />
          <NavItem icon={BookOpen} label="Knowledge Base" to="/admin/knowledge" onClick={closeMobile ? () => { navigate("/admin/knowledge"); closeMobile(); } : undefined} />
          <NavItem icon={ScrollText} label="Audit Log" to="/admin/audit" onClick={closeMobile ? () => { navigate("/admin/audit"); closeMobile(); } : undefined} />
          <NavItem icon={FileCode} label="Code Explorer" to="/admin/code-explorer" onClick={closeMobile ? () => { navigate("/admin/code-explorer"); closeMobile(); } : undefined} />
          <NavItem icon={Lock} label="Access Control" to="/rbac" onClick={closeMobile ? () => { navigate("/rbac"); closeMobile(); } : undefined} />
          <NavItem icon={CircuitBoard} label="Circuit Breakers" to="/circuit-breakers" onClick={closeMobile ? () => { navigate("/circuit-breakers"); closeMobile(); } : undefined} />
          <NavItem icon={Gauge} label="Cost Governance" to="/cost-governance" onClick={closeMobile ? () => { navigate("/cost-governance"); closeMobile(); } : undefined} />
        </>
      )}
    </>
  );

  return (
    <div className="min-h-screen bg-zinc-950" data-testid="dashboard-layout">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-13 bg-zinc-900/95 backdrop-blur-xl border-b border-white/[0.06] z-40 flex items-center px-4 no-print">
        <button onClick={() => setMobileOpen(!mobileOpen)} className="p-2 rounded-lg hover:bg-white/10 text-zinc-400" data-testid="mobile-sidebar-toggle">
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <Link to="/dashboard" className="ml-3 flex items-center gap-2">
          <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-7 h-7 rounded-lg object-cover" />
          <span className="text-white font-semibold font-['Outfit'] text-sm">MAARS Command</span>
        </Link>
        <button onClick={() => setCmdOpen(true)} className="ml-auto mr-2 p-2 rounded-lg hover:bg-white/10 text-zinc-400" data-testid="mobile-search-btn">
          <Search className="w-4 h-4" />
        </button>
      </div>

      {/* Sidebar -- Desktop */}
      <aside className={`hidden lg:flex fixed inset-y-0 left-0 ${sidebarW} bg-zinc-900/50 backdrop-blur-md border-r border-white/[0.06] z-30 flex-col transition-all duration-200 no-print`}>
        {/* Logo */}
        <div className={`h-14 flex items-center border-b border-white/[0.06] ${collapsed ? "justify-center px-2" : "gap-3 px-4"}`}>
          <Link to="/dashboard" className="flex items-center gap-2.5 min-w-0">
            <img src="/branding/maars-logo.jpeg" alt="MAARS" className={`${collapsed ? "w-8 h-8" : "w-9 h-9"} rounded-xl object-cover shrink-0 ring-1 ring-indigo-500/20`} />
            {!collapsed && (
              <div className="min-w-0">
                <h1 className="text-white font-bold text-[13px] font-['Outfit'] truncate leading-tight">MAARS Command</h1>
                <p className="text-[9px] text-zinc-600 truncate leading-tight">by MAARS Global Corporation</p>
              </div>
            )}
          </Link>
        </div>

        {/* Credits Display */}
        <SidebarCredits collapsed={collapsed} />

        {/* Org Switcher */}
        {!collapsed && (
          <OrgSwitcher />
        )}

        {/* Search trigger */}
        <div className="px-2 pt-3 pb-1">
          <button
            onClick={() => setCmdOpen(true)}
            className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2 px-2.5 py-[7px] rounded-lg text-[12px] transition-colors bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] text-zinc-500 hover:text-zinc-400`}
            title={collapsed ? "Search (press /)" : undefined}
            data-testid="sidebar-search-btn"
          >
            <Search className="w-3.5 h-3.5 shrink-0" />
            {!collapsed && (
              <>
                <span className="flex-1 text-left">Search...</span>
                <kbd className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.04] border border-white/[0.06] text-zinc-600 font-mono">/</kbd>
              </>
            )}
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden py-1 px-2 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent" data-testid="sidebar-nav">
          {renderNav(null)}
        </nav>

        {/* Collapse toggle */}
        <div className="px-2 py-1.5 border-t border-white/[0.06]">
          <button
            onClick={() => setCollapsed(c => !c)}
            className="w-full flex items-center justify-center gap-2 px-2.5 py-[7px] rounded-lg text-[11px] text-zinc-600 hover:bg-white/[0.04] hover:text-zinc-400 transition-colors"
            data-testid="sidebar-collapse-btn"
          >
            {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <><PanelLeftClose className="w-4 h-4" /><span>Collapse</span></>}
          </button>
        </div>

        {/* User + Logout */}
        <div className={`px-2 pb-2 pt-1 border-t border-white/[0.06] ${collapsed ? "flex flex-col items-center gap-1" : ""}`}>
          {!collapsed && (
            <div className="flex items-center gap-2.5 px-2.5 py-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                {user?.picture ? (
                  <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <span className="text-white text-[10px] font-semibold">{user?.name?.charAt(0) || "U"}</span>
                )}
              </div>
              <div className="min-w-0">
                <p className="text-[12px] font-medium text-zinc-300 truncate leading-tight">{user?.name}</p>
                <p className="text-[9px] text-zinc-600 truncate leading-tight">{user?.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            title={collapsed ? "Log Out" : undefined}
            className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-[7px] rounded-lg text-[12px] text-zinc-600 hover:bg-white/[0.04] hover:text-red-400 transition-colors`}
            data-testid="nav-logout"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Log Out</span>}
          </button>
        </div>
      </aside>

      {/* Sidebar -- Mobile */}
      {mobileOpen && (
        <>
          <div className="fixed inset-0 bg-black/60 z-20 lg:hidden" onClick={() => setMobileOpen(false)} />
          <aside className="fixed inset-y-0 left-0 w-56 bg-zinc-900 border-r border-white/[0.06] z-30 lg:hidden flex flex-col">
            <div className="h-14 flex items-center gap-3 px-4 border-b border-white/[0.06]">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                <Rocket className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-white font-bold text-[13px] font-['Outfit']">MAARS Command</h1>
              <button onClick={() => setMobileOpen(false)} className="ml-auto text-zinc-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <SidebarCredits collapsed={false} />
            <nav className="flex-1 overflow-y-auto py-1 px-2">
              {renderNav(() => setMobileOpen(false))}
            </nav>
            <div className="p-2 border-t border-white/[0.06]">
              <button onClick={handleLogout} className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-[12px] text-zinc-500 hover:text-red-400">
                <LogOut className="w-4 h-4" />Log Out
              </button>
            </div>
          </aside>
        </>
      )}

      {/* Main content */}
      <div className={`${mainML} pt-14 lg:pt-0 transition-all duration-200 min-h-screen`}>
        {location.pathname.startsWith("/chat") ? (
          children
        ) : (
          <div className="p-4 lg:p-6 xl:p-8 max-w-7xl mx-auto">
            {children}
          </div>
        )}
      </div>

      {/* Command Palette */}
      <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
    </div>
  );
};

export default DashboardLayout;
