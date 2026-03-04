import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  Bot, MessageSquare, ListTodo, Users, Settings, LogOut, Menu, X,
  Shield, BarChart3, Package, Rocket, Brain, FileCheck, Cpu, LayoutDashboard,
  Activity, Gauge, Radio, Code, Palette, PenTool, Info,
  PanelLeftClose, PanelLeftOpen, Search
} from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { BrandFooter } from "../BrandFooter";
import CommandPalette from "../CommandPalette";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", to: "/dashboard" },
  { icon: Rocket, label: "Projects", to: "/projects" },
  { icon: MessageSquare, label: "Chat", to: "/chat" },
  { icon: Users, label: "Agents", to: "/agents" },
  { icon: Brain, label: "Workspace Brain", to: "/workspace" },
  { icon: Cpu, label: "Brain Profiles", to: "/brain-profiles" },
  { icon: Activity, label: "Collaborations", to: "/collaborations" },
  { icon: Gauge, label: "KPI Dashboard", to: "/kpi-dashboard" },
  { icon: Radio, label: "Activity Monitor", to: "/activity-monitor" },
  { icon: Code, label: "Vibe Coding", to: "/vibe-coding" },
  { icon: Palette, label: "Reference Intel", to: "/reference-intelligence" },
  { icon: PenTool, label: "Content Generator", to: "/content-generator" },
  { icon: FileCheck, label: "Approvals", to: "/approvals" },
  { icon: Package, label: "Products", to: "/products" },
  { icon: ListTodo, label: "Tasks", to: "/tasks" },
  { icon: BarChart3, label: "My Insights", to: "/insights" },
  { icon: Users, label: "Team", to: "/team" },
  { icon: Settings, label: "Settings", to: "/settings" },
  { icon: Info, label: "About", to: "/about" },
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

  // Global keyboard shortcut: `/` to open command palette
  useEffect(() => {
    const handler = (e) => {
      // Don't trigger if user is typing in an input/textarea
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

  const sidebarW = collapsed ? "w-[68px]" : "w-60";
  const mainML = collapsed ? "lg:ml-[68px]" : "lg:ml-60";

  return (
    <div className="min-h-screen bg-zinc-950" data-testid="dashboard-layout">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-13 bg-zinc-900/95 backdrop-blur-xl border-b border-white/5 z-40 flex items-center px-4">
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

      {/* Sidebar — Desktop */}
      <aside className={`hidden lg:flex fixed inset-y-0 left-0 ${sidebarW} bg-zinc-900/60 backdrop-blur-md border-r border-white/5 z-30 flex-col transition-all duration-200`}>
        {/* Logo */}
        <div className={`p-3 border-b border-white/5 flex items-center ${collapsed ? "justify-center" : "gap-3 px-4"}`}>
          <Link to="/dashboard" className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shrink-0">
              <Rocket className="w-4 h-4 text-white" />
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <h1 className="text-white font-bold text-sm font-['Outfit'] truncate">MAARS Command</h1>
                <p className="text-[9px] text-zinc-500 truncate">{user?.name || "AI Workforce"}</p>
              </div>
            )}
          </Link>
        </div>

        {/* Search trigger */}
        <div className="px-2 pt-2">
          <button
            onClick={() => setCmdOpen(true)}
            className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-2 rounded-lg text-[12px] transition-colors bg-zinc-800/40 border border-white/5 hover:border-white/10 text-zinc-500 hover:text-zinc-300`}
            title={collapsed ? "Search (press /)" : undefined}
            data-testid="sidebar-search-btn"
          >
            <Search className="w-3.5 h-3.5 shrink-0" />
            {!collapsed && (
              <>
                <span className="flex-1 text-left">Search...</span>
                <kbd className="text-[9px] px-1 py-0.5 rounded bg-zinc-700/50 border border-white/5 text-zinc-600 font-mono">/</kbd>
              </>
            )}
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden py-2 px-2 space-y-0.5 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent" data-testid="sidebar-nav">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname === item.to || (item.to !== "/dashboard" && location.pathname.startsWith(item.to));
            return (
              <button
                key={item.to}
                onClick={() => navigate(item.to)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-2 rounded-lg text-[13px] transition-colors ${
                  isActive
                    ? "bg-indigo-500/15 text-indigo-400"
                    : "text-zinc-400 hover:bg-white/5 hover:text-white"
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
          {user?.is_admin && (
            <button
              onClick={() => navigate("/admin")}
              title={collapsed ? "Admin Panel" : undefined}
              className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-2 rounded-lg text-[13px] text-zinc-400 hover:bg-white/5 hover:text-white`}
              data-testid="nav-admin"
            >
              <Shield className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="truncate">Admin Panel</span>}
            </button>
          )}
        </nav>

        {/* Collapse toggle */}
        <div className="px-2 py-1.5 border-t border-white/5">
          <button
            onClick={() => setCollapsed(c => !c)}
            className="w-full flex items-center justify-center gap-2 px-2.5 py-2 rounded-lg text-[11px] text-zinc-500 hover:bg-white/5 hover:text-zinc-300 transition-colors"
            data-testid="sidebar-collapse-btn"
          >
            {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <><PanelLeftClose className="w-4 h-4" /><span>Collapse</span></>}
          </button>
        </div>

        {/* User + Logout */}
        <div className={`p-2 border-t border-white/5 ${collapsed ? "flex flex-col items-center gap-1" : ""}`}>
          {!collapsed && (
            <div className="flex items-center gap-2.5 px-2.5 py-2 mb-0.5">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                {user?.picture ? (
                  <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <span className="text-white text-[10px] font-semibold">{user?.name?.charAt(0) || "U"}</span>
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-white truncate">{user?.name}</p>
                <p className="text-[9px] text-zinc-500 truncate">{user?.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            title={collapsed ? "Log Out" : undefined}
            className={`w-full flex items-center ${collapsed ? "justify-center" : ""} gap-2.5 px-2.5 py-2 rounded-lg text-[13px] text-zinc-400 hover:bg-white/5 hover:text-red-400`}
            data-testid="nav-logout"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Log Out</span>}
          </button>
        </div>
      </aside>

      {/* Sidebar — Mobile */}
      {mobileOpen && (
        <>
          <div className="fixed inset-0 bg-black/60 z-20 lg:hidden" onClick={() => setMobileOpen(false)} />
          <aside className="fixed inset-y-0 left-0 w-60 bg-zinc-900 border-r border-white/5 z-30 lg:hidden flex flex-col">
            <div className="p-4 border-b border-white/5 flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                <Rocket className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-white font-bold text-sm font-['Outfit']">MAARS Command</h1>
              <button onClick={() => setMobileOpen(false)} className="ml-auto text-zinc-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
              {navItems.map(item => {
                const Icon = item.icon;
                const isActive = location.pathname === item.to || (item.to !== "/dashboard" && location.pathname.startsWith(item.to));
                return (
                  <button
                    key={item.to}
                    onClick={() => { navigate(item.to); setMobileOpen(false); }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13px] transition-colors ${
                      isActive ? "bg-indigo-500/15 text-indigo-400" : "text-zinc-400 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
            </nav>
            <div className="p-3 border-t border-white/5">
              <button onClick={handleLogout} className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13px] text-zinc-400 hover:text-red-400">
                <LogOut className="w-4 h-4" />Log Out
              </button>
            </div>
          </aside>
        </>
      )}

      {/* Main content */}
      <div className={`${mainML} pt-14 lg:pt-0 transition-all duration-200`}>
        <div className="p-4 lg:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
    </div>
  );
};

export default DashboardLayout;
