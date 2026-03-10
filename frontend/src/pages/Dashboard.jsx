import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import {
  Bot, MessageSquare, ListTodo, Sparkles, Plus, ChevronRight,
  Trash2, TrendingUp, Zap, Brain, Users, BarChart3
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

  const commander = agents.find(a => a.agent_id === "commander_orion" || a.name?.toLowerCase().includes("commander"));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
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
          <p className="text-sm text-zinc-500">Welcome back, {user?.name || "Commander"}. Your AI workforce is standing by.</p>
        </div>
        <NotificationCenter />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Chats", value: stats?.total_chats || 0, icon: MessageSquare, gradient: "from-indigo-500/15 to-violet-500/15", iconColor: "text-indigo-400" },
          { label: "Total Tasks", value: stats?.total_tasks || 0, icon: ListTodo, gradient: "from-violet-500/15 to-purple-500/15", iconColor: "text-violet-400" },
          { label: "Completed", value: stats?.completed_tasks || 0, icon: Sparkles, gradient: "from-emerald-500/15 to-teal-500/15", iconColor: "text-emerald-400" },
          { label: "Active Agents", value: agents.filter(a => !a.hidden).length, icon: Bot, gradient: "from-amber-500/15 to-orange-500/15", iconColor: "text-amber-400" },
        ].map(({ label, value, icon: Icon, gradient, iconColor }) => (
          <Card key={label} className="bg-zinc-900/50 border-white/[0.06] hover:border-white/10 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-zinc-500 font-medium">{label}</p>
                  <p className="text-2xl font-bold text-white mt-1 tabular-nums">{value}</p>
                </div>
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${iconColor}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Command Center */}
      <div className="mb-8"><CommandCenter /></div>

      {/* Commander Section */}
      {commander && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider font-['Outfit']">Your Commander</h2>
          </div>
          <div className="relative group cursor-pointer" onClick={() => navigate(`/chat/${commander.agent_id}`)} data-testid="commander-card">
            <Card className="bg-zinc-900/50 border-white/[0.06] hover:border-indigo-500/20 transition-all overflow-hidden">
              <CardContent className="p-0">
                <div className="flex items-center gap-5 p-5">
                  <div className="relative shrink-0">
                    <img src={commander.avatar} alt={commander.name}
                      className="w-16 h-16 rounded-xl object-cover ring-2 ring-indigo-500/20 group-hover:ring-indigo-500/40 transition-all" />
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-zinc-900 flex items-center justify-center">
                      <Zap className="w-2.5 h-2.5 text-white" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-white font-['Outfit']">{commander.name}</h3>
                    <p className="text-sm text-indigo-400/70 mb-1">{commander.role}</p>
                    <p className="text-sm text-zinc-500 line-clamp-2">{commander.description}</p>
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {(commander.capabilities || []).slice(0, 5).map((cap, i) => (
                        <span key={i} className="px-2 py-0.5 text-[10px] rounded-full bg-indigo-500/10 text-indigo-300/70 border border-indigo-500/10">{cap}</span>
                      ))}
                    </div>
                  </div>
                  <Button className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 shrink-0 shadow-lg shadow-indigo-500/20">
                    <MessageSquare className="w-4 h-4 mr-2" /> Chat
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-3 font-['Outfit']">Quick Actions</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { label: "New Chat", desc: "Start a conversation", icon: MessageSquare, onClick: () => navigate("/chat"), color: "indigo" },
            { label: "Create Task", desc: "Assign work to agents", icon: ListTodo, onClick: () => navigate("/tasks"), color: "violet" },
            { label: "Browse Agents", desc: `${agents.length} agents available`, icon: Users, onClick: () => navigate("/agents"), color: "purple" },
            { label: "Create Agent", desc: "Build a custom agent", icon: Plus, onClick: () => navigate("/agents/create"), color: "fuchsia" },
          ].map(({ label, desc, icon: Icon, onClick, color }) => (
            <Card key={label} onClick={onClick}
              className="bg-zinc-900/50 border-white/[0.06] hover:border-white/10 cursor-pointer transition-all group"
              data-testid={`quick-action-${label.toLowerCase().replace(' ', '-')}`}>
              <CardContent className="p-4 flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center group-hover:bg-${color}-500/20 transition-colors`}>
                  <Icon className={`w-5 h-5 text-${color}-400`} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{label}</p>
                  <p className="text-xs text-zinc-500">{desc}</p>
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
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider font-['Outfit']">Recent Conversations</h2>
            <Button variant="ghost" className="text-indigo-400/60 hover:text-indigo-300 text-xs"
              onClick={() => navigate("/chat")} data-testid="view-all-chats-btn">
              View All <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <div className="space-y-2">
            {recentChats.slice(0, 5).map(chat => {
              const agent = agents.find(a => a.agent_id === chat.agent_id);
              return (
                <Card key={chat.chat_id}
                  className="bg-zinc-900/50 border-white/[0.06] hover:border-white/10 cursor-pointer transition-colors group"
                  onClick={() => navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`)}
                  data-testid={`recent-chat-${chat.chat_id}`}>
                  <CardContent className="p-4 flex items-center gap-4">
                    <img src={agent?.avatar || "/branding/maars-logo.jpeg"} alt="" className="w-10 h-10 rounded-lg object-cover" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-white truncate">{chat.title}</p>
                      <p className="text-sm text-zinc-500 truncate">{agent?.name} · {chat.messages?.length || 0} messages</p>
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
