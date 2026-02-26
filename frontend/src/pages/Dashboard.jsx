import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { 
  Bot, MessageSquare, ListTodo, Sparkles, Plus, ChevronRight,
  LayoutDashboard, Users, Settings, LogOut, Menu, X
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, chatsRes, statsRes] = await Promise.all([
        fetch(`${API}/agents`, { credentials: "include", headers }),
        fetch(`${API}/chats`, { credentials: "include", headers }),
        fetch(`${API}/stats`, { credentials: "include", headers })
      ]);

      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (chatsRes.ok) setRecentChats(await chatsRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active 
          ? "bg-indigo-500/20 text-indigo-400" 
          : "text-zinc-400 hover:bg-white/5 hover:text-white"
      }`}
      data-testid={`nav-${label.toLowerCase()}`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-2" data-testid="sidebar-logo">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white font-['Outfit']">Nexus AI</span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <NavItem icon={LayoutDashboard} label="Dashboard" to="/dashboard" active />
        <NavItem icon={MessageSquare} label="Chat" to="/chat" />
        <NavItem icon={Users} label="Agents" to="/agents" />
        <NavItem icon={ListTodo} label="Tasks" to="/tasks" />
        <NavItem icon={Settings} label="Settings" to="/settings" />
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            {user?.picture ? (
              <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" />
            ) : (
              <span className="text-white font-semibold">{user?.name?.charAt(0) || "U"}</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.name}</p>
            <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start text-zinc-400 hover:text-white hover:bg-white/5 mt-2"
          onClick={handleLogout}
          data-testid="logout-btn"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="dashboard-page">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white font-['Outfit']">Nexus AI</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 text-zinc-400 hover:text-white"
            data-testid="mobile-menu-toggle"
          >
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-zinc-900 border-r border-white/10">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 bottom-0 w-64 bg-zinc-900/50 border-r border-white/10">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-6 lg:p-8 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
              Welcome back, {user?.name?.split(" ")[0]}
            </h1>
            <p className="text-zinc-400">Here's what's happening with your AI team today.</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-zinc-400">Total Chats</p>
                    <p className="text-2xl font-bold text-white">{stats?.total_chats || 0}</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-indigo-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-zinc-400">Total Tasks</p>
                    <p className="text-2xl font-bold text-white">{stats?.total_tasks || 0}</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <ListTodo className="w-5 h-5 text-violet-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-zinc-400">Completed</p>
                    <p className="text-2xl font-bold text-white">{stats?.completed_tasks || 0}</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-emerald-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-zinc-400">Custom Agents</p>
                    <p className="text-2xl font-bold text-white">{stats?.custom_agents || 0}</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-amber-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4 font-['Outfit']">Quick Actions</h2>
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() => navigate("/chat")}
                className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
                data-testid="quick-new-chat-btn"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                New Chat
              </Button>
              <Button
                onClick={() => navigate("/tasks")}
                variant="outline"
                className="border-white/10 hover:bg-white/5"
                data-testid="quick-new-task-btn"
              >
                <ListTodo className="w-4 h-4 mr-2" />
                Create Task
              </Button>
              <Button
                onClick={() => navigate("/agents/create")}
                variant="outline"
                className="border-white/10 hover:bg-white/5"
                data-testid="quick-create-agent-btn"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Agent
              </Button>
            </div>
          </div>

          {/* Agents Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white font-['Outfit']">Your AI Team</h2>
              <Button
                variant="ghost"
                className="text-zinc-400 hover:text-white"
                onClick={() => navigate("/agents")}
                data-testid="view-all-agents-btn"
              >
                View All <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.slice(0, 6).map((agent) => (
                <Card
                  key={agent.agent_id}
                  className="bg-zinc-900/50 border-white/10 hover:border-white/20 cursor-pointer transition-colors group"
                  onClick={() => navigate(`/chat/${agent.agent_id}`)}
                  data-testid={`agent-card-${agent.agent_id}`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <img
                        src={agent.avatar}
                        alt={agent.name}
                        className="w-12 h-12 rounded-lg object-cover"
                      />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-white group-hover:text-indigo-400 transition-colors truncate">
                          {agent.name}
                        </h3>
                        <p className="text-sm text-zinc-400 truncate">{agent.role}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Chats */}
          {recentChats.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white font-['Outfit']">Recent Conversations</h2>
                <Button
                  variant="ghost"
                  className="text-zinc-400 hover:text-white"
                  onClick={() => navigate("/chat")}
                  data-testid="view-all-chats-btn"
                >
                  View All <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
              <div className="space-y-2">
                {recentChats.slice(0, 5).map((chat) => {
                  const agent = agents.find(a => a.agent_id === chat.agent_id);
                  return (
                    <Card
                      key={chat.chat_id}
                      className="bg-zinc-900/50 border-white/10 hover:border-white/20 cursor-pointer transition-colors"
                      onClick={() => navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`)}
                      data-testid={`recent-chat-${chat.chat_id}`}
                    >
                      <CardContent className="p-4 flex items-center gap-4">
                        <img
                          src={agent?.avatar || "https://via.placeholder.com/40"}
                          alt=""
                          className="w-10 h-10 rounded-lg object-cover"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-white truncate">{chat.title}</p>
                          <p className="text-sm text-zinc-400 truncate">
                            {agent?.name} • {chat.messages?.length || 0} messages
                          </p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-zinc-500" />
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
