import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  Bot, MessageSquare, ListTodo, Sparkles, Plus, ChevronRight,
  Trash2, TrendingUp, Zap, Brain
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import OnboardingFlow from "./OnboardingFlow";
import NotificationCenter from "../components/NotificationCenter";
import CommandCenter from "../components/projects/CommandCenter";

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchData();
    if (user && !user.onboarding_completed) setShowOnboarding(true);
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, chatsRes, statsRes] = await Promise.all([
        fetch(`${API}/agents`, { headers }).catch(() => null),
        fetch(`${API}/chats`, { headers }).catch(() => null),
        fetch(`${API}/stats`, { headers }).catch(() => null)
      ]);
      if (agentsRes?.ok) setAgents(await agentsRes.json());
      if (chatsRes?.ok) { const data = await chatsRes.json(); setRecentChats(data.chats || data); }
      if (statsRes?.ok) setStats(await statsRes.json());
    } catch { toast.error("Failed to load dashboard data"); }
    finally { setLoading(false); }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      const res = await fetch(`${API}/chats/${chatId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { setRecentChats(prev => prev.filter(c => c.chat_id !== chatId)); toast.success("Chat deleted"); }
    } catch { toast.error("Failed to delete chat"); }
  };

  // Filter out hidden agents for non-admin
  const visibleAgents = agents.filter(a => !a.hidden || user?.is_admin);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="dashboard-page">
      {showOnboarding && <OnboardingFlow onComplete={() => setShowOnboarding(false)} />}

      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1 font-['Outfit']">Command Center</h1>
          <p className="text-sm text-blue-300/40">Deploy agents. Execute missions. Scale your AI workforce.</p>
        </div>
        <NotificationCenter />
      </div>

      {/* Command Center */}
      <div className="mb-8"><CommandCenter /></div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Chats", value: stats?.total_chats || 0, icon: MessageSquare, color: "blue" },
          { label: "Total Tasks", value: stats?.total_tasks || 0, icon: ListTodo, color: "cyan" },
          { label: "Completed", value: stats?.completed_tasks || 0, icon: Sparkles, color: "emerald" },
          { label: "Custom Agents", value: stats?.custom_agents || 0, icon: Bot, color: "fuchsia" },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="bg-[#0d0d35]/50 border-blue-500/8 hover:border-blue-500/15 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-blue-300/40 font-medium">{label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{value}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg bg-${color}-500/15 flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 text-${color}-400`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-blue-300/50 uppercase tracking-wider mb-3 font-['Outfit']">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => navigate("/chat")}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg shadow-blue-500/10"
            data-testid="quick-new-chat-btn">
            <MessageSquare className="w-4 h-4 mr-2" /> New Chat
          </Button>
          <Button onClick={() => navigate("/tasks")} variant="outline"
            className="border-blue-500/15 hover:bg-blue-500/5 text-zinc-300"
            data-testid="quick-new-task-btn">
            <ListTodo className="w-4 h-4 mr-2" /> Create Task
          </Button>
          <Button onClick={() => navigate("/agents/create")} variant="outline"
            className="border-blue-500/15 hover:bg-blue-500/5 text-zinc-300"
            data-testid="quick-create-agent-btn">
            <Plus className="w-4 h-4 mr-2" /> Create Agent
          </Button>
        </div>
      </div>

      {/* Agents Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-blue-300/50 uppercase tracking-wider font-['Outfit']">Your AI Team</h2>
          <Button variant="ghost" className="text-blue-400/60 hover:text-blue-300 text-xs"
            onClick={() => navigate("/agents")} data-testid="view-all-agents-btn">
            View All <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {visibleAgents.slice(0, 15).map(agent => (
            <div key={agent.agent_id} className="relative group">
              <Card className={`bg-[#0d0d35]/50 border-blue-500/8 hover:border-blue-500/20 cursor-pointer transition-all ${agent.hidden ? "opacity-40" : ""}`}
                onClick={() => navigate(`/chat/${agent.agent_id}`)}
                data-testid={`agent-card-${agent.agent_id}`}>
                <CardContent className="p-3">
                  <div className="flex items-center gap-3">
                    <img src={agent.avatar} alt={agent.name} className="w-10 h-10 rounded-lg object-cover shrink-0" />
                    <div className="min-w-0">
                      <h3 className="font-semibold text-sm text-white truncate">{agent.name}</h3>
                      <p className="text-xs text-blue-300/40 truncate">{agent.role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              {/* Hover popup */}
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-56 rounded-xl overflow-hidden border border-blue-500/20 shadow-[0_8px_40px_rgba(59,130,246,0.15)] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300 z-50 bg-[#0a0a2e]"
                onClick={() => navigate(`/chat/${agent.agent_id}`)}>
                <div className="relative aspect-square">
                  <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#070721] via-[#070721]/40 to-transparent" />
                  <span className="absolute top-2 right-2 px-2 py-0.5 text-[9px] font-bold rounded-full bg-blue-500 text-white uppercase tracking-wider">
                    {agent.model_provider || "AI"}
                  </span>
                  <div className="absolute bottom-0 left-0 right-0 p-3">
                    <p className="text-cyan-400 text-[10px] font-medium">{agent.role}</p>
                    <h3 className="font-bold text-white text-sm leading-tight">{agent.name}</h3>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {(agent.capabilities || []).slice(0, 3).map((cap, i) => (
                        <span key={i} className="px-1.5 py-0.5 text-[8px] rounded-full bg-blue-500/15 text-blue-200/70 backdrop-blur-sm">{cap}</span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="p-3 border-t border-blue-500/10">
                  <p className="text-[11px] text-zinc-400 leading-relaxed line-clamp-3">{agent.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Chats */}
      {recentChats.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-blue-300/50 uppercase tracking-wider font-['Outfit']">Recent Conversations</h2>
            <Button variant="ghost" className="text-blue-400/60 hover:text-blue-300 text-xs"
              onClick={() => navigate("/chat")} data-testid="view-all-chats-btn">
              View All <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <div className="space-y-2">
            {recentChats.slice(0, 5).map(chat => {
              const agent = agents.find(a => a.agent_id === chat.agent_id);
              return (
                <Card key={chat.chat_id}
                  className="bg-[#0d0d35]/50 border-blue-500/8 hover:border-blue-500/15 cursor-pointer transition-colors group"
                  onClick={() => navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`)}
                  data-testid={`recent-chat-${chat.chat_id}`}>
                  <CardContent className="p-4 flex items-center gap-4">
                    <img src={agent?.avatar || "/branding/maars-logo.jpeg"} alt="" className="w-10 h-10 rounded-lg object-cover" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-white truncate">{chat.title}</p>
                      <p className="text-sm text-blue-300/40 truncate">{agent?.name} · {chat.messages?.length || 0} messages</p>
                    </div>
                    <button onClick={e => { e.stopPropagation(); handleDeleteChat(chat.chat_id); }}
                      className="opacity-0 group-hover:opacity-100 p-2 text-zinc-500 hover:text-red-400 transition-all"
                      data-testid={`delete-recent-chat-${chat.chat_id}`}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <ChevronRight className="w-5 h-5 text-zinc-600" />
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
