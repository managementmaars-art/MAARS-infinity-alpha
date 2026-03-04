import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  Bot, MessageSquare, ListTodo, Users, Settings, LogOut, Menu, X,
  Shield, BarChart3, Package, Rocket, Brain, FileCheck, Cpu, LayoutDashboard,
  Activity, Gauge, Radio, Code, Palette, PenTool
} from "lucide-react";
import { useState } from "react";
import { BrandFooter } from "../BrandFooter";

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
];

const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-zinc-950" data-testid="dashboard-layout">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-zinc-900/90 backdrop-blur-xl border-b border-white/5 z-40 flex items-center px-4">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-lg hover:bg-white/10 text-zinc-400" data-testid="mobile-sidebar-toggle">
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <Link to="/dashboard" className="ml-3 flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-semibold font-['Outfit'] text-sm">MAARS Command</span>
        </Link>
      </div>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 w-64 bg-zinc-900/50 border-r border-white/5 z-30 transform transition-transform lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="h-full flex flex-col">
          <div className="p-4 border-b border-white/5">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                <Rocket className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-white font-bold text-sm font-['Outfit']">MAARS Command</h1>
                <p className="text-[10px] text-zinc-500">{user?.name || "AI Workforce"}</p>
              </div>
            </Link>
          </div>

          <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
            {navItems.map(item => {
              const Icon = item.icon;
              const isActive = location.pathname === item.to || (item.to !== "/dashboard" && location.pathname.startsWith(item.to));
              return (
                <button
                  key={item.to}
                  onClick={() => { navigate(item.to); setSidebarOpen(false); }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? "bg-indigo-500/15 text-indigo-400"
                      : "text-zinc-400 hover:bg-white/5 hover:text-white"
                  }`}
                  data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
            {user?.is_admin && (
              <button
                onClick={() => { navigate("/admin"); setSidebarOpen(false); }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:bg-white/5 hover:text-white"
                data-testid="nav-admin"
              >
                <Shield className="w-4 h-4" />Admin Panel
              </button>
            )}
          </nav>

          <div className="p-3 border-t border-white/5">
            <div className="flex items-center gap-3 px-3 py-2 mb-1">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                {user?.picture ? (
                  <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <span className="text-white text-xs font-semibold">{user?.name?.charAt(0) || "U"}</span>
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-white truncate">{user?.name}</p>
                <p className="text-[10px] text-zinc-500 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:bg-white/5 hover:text-red-400"
              data-testid="nav-logout"
            >
              <LogOut className="w-4 h-4" />Log Out
            </button>
          </div>

          <BrandFooter />
        </div>
      </div>

      {/* Overlay */}
      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      {/* Main content */}
      <div className="lg:ml-64 pt-14 lg:pt-0">
        <div className="p-6 lg:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
