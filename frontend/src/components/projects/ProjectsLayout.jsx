import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  LayoutDashboard, MessageSquare, Rocket, ListTodo, Users, Package,
  Settings, LogOut, BarChart3, Shield, Menu, X, Brain, FileCheck, Cpu
} from "lucide-react";
import { useState } from "react";
import { BrandFooter } from "../BrandFooter";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", to: "/dashboard" },
  { icon: Rocket, label: "Projects", to: "/projects" },
  { icon: MessageSquare, label: "Chat", to: "/chat" },
  { icon: Brain, label: "Workspace Brain", to: "/workspace" },
  { icon: Cpu, label: "Brain Profiles", to: "/brain-profiles" },
  { icon: FileCheck, label: "Approvals", to: "/approvals" },
  { icon: ListTodo, label: "Tasks", to: "/tasks" },
  { icon: Users, label: "Team", to: "/team" },
  { icon: Package, label: "Products", to: "/products" },
  { icon: BarChart3, label: "Insights", to: "/insights" },
  { icon: Settings, label: "Settings", to: "/settings" },
];

const ProjectsLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const isAdmin = user?.email === "management.maars@marsgc.net";

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-zinc-900/90 backdrop-blur-xl border-b border-white/5 z-40 flex items-center px-4">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-lg hover:bg-white/10 text-zinc-400">
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <span className="ml-3 text-white font-semibold font-['Outfit'] text-sm">MAARS Command</span>
      </div>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 w-64 bg-zinc-900/50 border-r border-white/5 z-30 transform transition-transform lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="p-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
              <Rocket className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-white font-bold text-sm font-['Outfit']">MAARS Command</h1>
              <p className="text-[10px] text-zinc-500">{user?.name || "AI Workforce"}</p>
            </div>
          </div>
        </div>

        <nav className="p-3 flex-1 space-y-0.5">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.to);
            return (
              <button
                key={item.to}
                onClick={() => { navigate(item.to); setSidebarOpen(false); }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-indigo-500/15 text-indigo-400"
                    : "text-zinc-400 hover:bg-white/5 hover:text-white"
                }`}
                data-testid={`nav-${item.label.toLowerCase()}`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
          {isAdmin && (
            <button
              onClick={() => navigate("/admin")}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:bg-white/5 hover:text-white"
            >
              <Shield className="w-4 h-4" />Admin
            </button>
          )}
        </nav>

        <div className="p-3 border-t border-white/5">
          <button onClick={logout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-zinc-400 hover:bg-white/5 hover:text-red-400">
            <LogOut className="w-4 h-4" />Log Out
          </button>
        </div>

        <BrandFooter />
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

export default ProjectsLayout;
