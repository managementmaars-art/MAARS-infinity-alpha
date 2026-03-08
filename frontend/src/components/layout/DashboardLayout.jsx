import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  Bot, MessageSquare, ListTodo, Users, Settings, LogOut, Menu, X,
  Shield, BarChart3, Package, Rocket, Brain, FileCheck, Cpu, LayoutDashboard,
  Activity, Gauge, Radio, Code, Palette, PenTool, Info,
  PanelLeftClose, PanelLeftOpen, Search, FileCode, Database
} from "lucide-react";
import { useState, useEffect } from "react";
import CommandPalette from "../CommandPalette";

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
          <NavItem icon={Shield} label="Admin Panel" to="/admin" onClick={closeMobile ? () => { navigate("/admin"); closeMobile(); } : undefined} />
          <NavItem icon={FileCode} label="Code Explorer" to="/admin/code-explorer" onClick={closeMobile ? () => { navigate("/admin/code-explorer"); closeMobile(); } : undefined} />
        </>
      )}
    </>
  );

  return (
    <div className="min-h-screen bg-zinc-950" data-testid="dashboard-layout">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-13 bg-zinc-900/95 backdrop-blur-xl border-b border-white/[0.06] z-40 flex items-center px-4">
        <button onClick={() => setMobileOpen(!mobileOpen)} className="p-2 rounded-lg hover:bg-white/10 text-zinc-400" data-testid="mobile-sidebar-toggle">
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <Link to="/dashboard" className="ml-3 flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
            <Rocket className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-semibold font-['Outfit'] text-sm">MAARS Command</span>
        </Link>
        <button onClick={() => setCmdOpen(true)} className="ml-auto mr-2 p-2 rounded-lg hover:bg-white/10 text-zinc-400" data-testid="mobile-search-btn">
          <Search className="w-4 h-4" />
        </button>
      </div>

      {/* Sidebar -- Desktop */}
      <aside className={`hidden lg:flex fixed inset-y-0 left-0 ${sidebarW} bg-zinc-900/50 backdrop-blur-md border-r border-white/[0.06] z-30 flex-col transition-all duration-200`}>
        {/* Logo */}
        <div className={`h-14 flex items-center border-b border-white/[0.06] ${collapsed ? "justify-center px-2" : "gap-3 px-4"}`}>
          <Link to="/dashboard" className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shrink-0">
              <Rocket className="w-4 h-4 text-white" />
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <h1 className="text-white font-bold text-[13px] font-['Outfit'] truncate leading-tight">MAARS Command</h1>
                <p className="text-[9px] text-zinc-600 truncate leading-tight">{user?.name || "AI Workforce"}</p>
              </div>
            )}
          </Link>
        </div>

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
