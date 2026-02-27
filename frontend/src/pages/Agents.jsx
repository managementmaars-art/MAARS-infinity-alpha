import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { 
  Bot, Plus, MessageSquare, Trash2, ArrowLeft,
  LayoutDashboard, Users, ListTodo, Settings, LogOut, Menu, X, Sparkles,
  Search, Calculator, ClipboardList, BarChart3, Wrench,
  Mail, MessageCircle, Phone, Github, Table, Image, Calendar, Send
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

const Agents = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API}/agents`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        setAgents(await response.json());
      }
    } catch (error) {
      toast.error("Failed to load agents");
    } finally {
      setLoading(false);
    }
  };

  const deleteAgent = async (agentId) => {
    try {
      const response = await fetch(`${API}/agents/${agentId}`, {
        method: "DELETE",
        credentials: "include",
        headers
      });

      if (response.ok) {
        setAgents(prev => prev.filter(a => a.agent_id !== agentId));
        toast.success("Agent deleted");
      } else {
        const data = await response.json();
        toast.error(data.detail || "Failed to delete agent");
      }
    } catch (error) {
      toast.error("Failed to delete agent");
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
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold text-white font-['Outfit']">Martian AI</span>
            <p className="text-[9px] text-zinc-500 -mt-1">by MAARS Global Corp</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <NavItem icon={LayoutDashboard} label="Dashboard" to="/dashboard" />
        <NavItem icon={MessageSquare} label="Chat" to="/chat" />
        <NavItem icon={Users} label="Agents" to="/agents" active />
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
        >
          <LogOut className="w-5 h-5 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );

  const defaultAgents = agents.filter(a => !a.is_custom);
  const customAgents = agents.filter(a => a.is_custom);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="agents-page">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white font-['Outfit']">Martian AI</span>
          </Link>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-zinc-400">
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
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
        <div className="p-6 lg:p-8 max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
                AI Agents
              </h1>
              <p className="text-zinc-400">Your specialized AI team members</p>
            </div>
            <Button
              onClick={() => navigate("/agents/create")}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
              data-testid="create-agent-btn"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Agent
            </Button>
          </div>

          {/* Default Agents */}
          <div className="mb-10">
            <h2 className="text-lg font-semibold text-white mb-4 font-['Outfit'] flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Specialized Agents
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {defaultAgents.map((agent) => (
                <Card
                  key={agent.agent_id}
                  className="bg-zinc-900/50 border-white/10 hover:border-white/20 transition-colors group"
                  data-testid={`agent-card-${agent.agent_id}`}
                >
                  <CardContent className="p-0">
                    <div className="aspect-video relative overflow-hidden rounded-t-lg">
                      <img
                        src={agent.avatar}
                        alt={agent.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-transparent to-transparent" />
                      <div className="absolute bottom-3 left-3">
                        <Badge variant="secondary" className="bg-indigo-500/20 text-indigo-300 border-0">
                          {agent.model_provider}
                        </Badge>
                      </div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                      <p className="text-sm text-zinc-400 mb-3">{agent.role}</p>
                      <p className="text-sm text-zinc-500 mb-4 line-clamp-2">{agent.description}</p>
                      <div className="flex flex-wrap gap-1 mb-4">
                        {agent.capabilities?.slice(0, 3).map((cap, i) => (
                          <span key={i} className="px-2 py-0.5 text-xs rounded-full bg-white/5 text-zinc-400">
                            {cap}
                          </span>
                        ))}
                      </div>
                      {agent.tools?.length > 0 && (
                        <div className="flex items-center gap-1.5 mb-3 flex-wrap" data-testid={`agent-tools-${agent.agent_id}`}>
                          <Wrench className="w-3 h-3 text-amber-400 shrink-0" />
                          <span className="text-[10px] text-amber-400/80 font-medium">Tools:</span>
                          {agent.tools.slice(0, 6).map((tool, i) => {
                            const toolIcons = { web_search: Search, calculate: Calculator, create_task: ClipboardList, analyze_data: BarChart3, send_slack: MessageCircle, send_email: Mail, send_sms: Phone, github_action: Github, airtable_action: Table, search_gif: Image, schedule_meeting: Calendar, google_calendar: Calendar, send_gmail: Send };
                            const ToolIcon = toolIcons[tool] || Wrench;
                            const toolLabels = { web_search: "Search", calculate: "Math", create_task: "Tasks", analyze_data: "Analyze", send_slack: "Slack", send_email: "Email", send_sms: "SMS", github_action: "GitHub", airtable_action: "Airtable", search_gif: "GIFs", schedule_meeting: "Calendly", google_calendar: "Calendar", send_gmail: "Gmail" };
                            return (
                              <span key={i} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                <ToolIcon className="w-2.5 h-2.5" />
                                {toolLabels[tool] || tool}
                              </span>
                            );
                          })}
                          {agent.tools.length > 6 && (
                            <span className="text-[10px] text-amber-400/60">+{agent.tools.length - 6}</span>
                          )}
                        </div>
                      )}
                      <Button
                        onClick={() => navigate(`/chat/${agent.agent_id}`)}
                        className="w-full bg-white/5 hover:bg-white/10 text-white"
                        data-testid={`chat-with-${agent.agent_id}`}
                      >
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Start Chat
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Custom Agents */}
          {customAgents.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-white mb-4 font-['Outfit'] flex items-center gap-2">
                <Bot className="w-5 h-5 text-violet-400" />
                Your Custom Agents
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {customAgents.map((agent) => (
                  <Card
                    key={agent.agent_id}
                    className="bg-zinc-900/50 border-white/10 hover:border-white/20 transition-colors group"
                    data-testid={`custom-agent-card-${agent.agent_id}`}
                  >
                    <CardContent className="p-0">
                      <div className="aspect-video relative overflow-hidden rounded-t-lg">
                        <img
                          src={agent.avatar}
                          alt={agent.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-transparent to-transparent" />
                        <div className="absolute bottom-3 left-3">
                          <Badge variant="secondary" className="bg-violet-500/20 text-violet-300 border-0">
                            Custom
                          </Badge>
                        </div>
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-white mb-1">{agent.name}</h3>
                        <p className="text-sm text-zinc-400 mb-3">{agent.role}</p>
                        <p className="text-sm text-zinc-500 mb-4 line-clamp-2">{agent.description}</p>
                        <div className="flex gap-2">
                          <Button
                            onClick={() => navigate(`/chat/${agent.agent_id}`)}
                            className="flex-1 bg-white/5 hover:bg-white/10 text-white"
                            data-testid={`chat-with-custom-${agent.agent_id}`}
                          >
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Chat
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10"
                            onClick={() => deleteAgent(agent.agent_id)}
                            data-testid={`delete-agent-${agent.agent_id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Empty State for Custom Agents */}
          {customAgents.length === 0 && (
            <div className="mt-8 p-8 rounded-xl border border-dashed border-white/10 text-center">
              <Bot className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">
                No Custom Agents Yet
              </h3>
              <p className="text-zinc-400 mb-4">
                Create your own AI agents tailored to your specific needs.
              </p>
              <Button
                onClick={() => navigate("/agents/create")}
                className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Agent
              </Button>
            </div>
          )}
        </div>
      </div>
      <div className="lg:ml-64"><BrandFooter /></div>
    </div>
  );
};

export default Agents;
