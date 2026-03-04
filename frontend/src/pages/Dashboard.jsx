import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Bot, MessageSquare, ListTodo, Sparkles, Plus, ChevronRight,
  Users, Trash2, Rocket
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
    // Show onboarding for new users
    if (user && !user.onboarding_completed) {
      setShowOnboarding(true);
    }
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, chatsRes, statsRes] = await Promise.all([
        fetch(`${API}/agents`, { headers }).catch(() => null),
        fetch(`${API}/chats`, { headers }).catch(() => null),
        fetch(`${API}/stats`, { headers }).catch(() => null)
      ]);

      if (agentsRes?.ok) setAgents(await agentsRes.json());
      if (chatsRes?.ok) {
        const data = await chatsRes.json();
        setRecentChats(data.chats || data);
      }
      if (statsRes?.ok) setStats(await statsRes.json());
    } catch (error) {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      const res = await fetch(`${API}/chats/${chatId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        setRecentChats(prev => prev.filter(c => c.chat_id !== chatId));
        toast.success("Chat deleted");
      }
    } catch { toast.error("Failed to delete chat"); }
  };


  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="dashboard-page">
      {showOnboarding && (
        <OnboardingFlow onComplete={() => setShowOnboarding(false)} />
      )}
          {/* Header */}
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
                Command Center
              </h1>
              <p className="text-zinc-400">Set goals. Deploy agents. Run your AI workforce.</p>
            </div>
            <NotificationCenter />
          </div>

          {/* Command Center */}
          <div className="mb-8">
            <CommandCenter />
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
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {agents.map((agent) => (
                <div
                  key={agent.agent_id}
                  className="relative group"
                >
                  <Card
                    className="bg-zinc-900/50 border-white/10 hover:border-white/30 cursor-pointer transition-colors"
                    onClick={() => navigate(`/chat/${agent.agent_id}`)}
                    data-testid={`agent-card-${agent.agent_id}`}
                  >
                    <CardContent className="p-3">
                      <div className="flex items-center gap-3">
                        <img src={agent.avatar} alt={agent.name} className="w-10 h-10 rounded-lg object-cover shrink-0" />
                        <div className="min-w-0">
                          <h3 className="font-semibold text-sm text-white truncate">{agent.name}</h3>
                          <p className="text-xs text-zinc-400 truncate">{agent.role}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  {/* Hover popup */}
                  <div
                    className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-56 rounded-xl overflow-hidden border border-amber-500/50 shadow-[0_8px_40px_rgba(245,158,11,0.2)] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300 z-50 bg-zinc-950"
                    onClick={() => navigate(`/chat/${agent.agent_id}`)}
                  >
                    <div className="relative aspect-square">
                      <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
                      <span className="absolute top-2 right-2 px-2 py-0.5 text-[9px] font-bold rounded-full bg-amber-500 text-black uppercase tracking-wider">
                        {agent.role}
                      </span>
                      <div className="absolute bottom-0 left-0 right-0 p-3">
                        <p className="text-indigo-400 text-[10px] font-medium">{agent.role}</p>
                        <h3 className="font-bold text-white text-sm leading-tight">{agent.name}</h3>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(agent.capabilities || []).slice(0, 3).map((cap, i) => (
                            <span key={i} className="px-1.5 py-0.5 text-[8px] rounded-full bg-white/15 text-zinc-300 backdrop-blur-sm">{cap}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="p-3 border-t border-white/5">
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
                      className="bg-zinc-900/50 border-white/10 hover:border-white/20 cursor-pointer transition-colors group"
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
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteChat(chat.chat_id);
                          }}
                          className="opacity-0 group-hover:opacity-100 p-2 text-zinc-500 hover:text-red-400 transition-all"
                          data-testid={`delete-recent-chat-${chat.chat_id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                        <ChevronRight className="w-5 h-5 text-zinc-500" />
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
