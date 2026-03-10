import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  MessageSquare, Bot, Zap, TrendingUp, ThumbsUp, ThumbsDown,
  Flame, CreditCard, ArrowLeft, Loader2, ChevronRight, Sparkles
} from "lucide-react";
import { toast } from "sonner";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";

const StatCard = ({ title, value, subtitle, icon: Icon, color }) => (
  <div className={`p-4 rounded-xl bg-${color}-500/10 border border-${color}-500/20 relative overflow-hidden`} data-testid={`insight-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="absolute top-3 right-3 opacity-15">
      <Icon className={`w-8 h-8 text-${color}-400`} />
    </div>
    <p className={`text-[11px] font-medium text-${color}-400 uppercase tracking-wide`}>{title}</p>
    <p className="text-xl font-bold text-white mt-1">{value}</p>
    {subtitle && <p className="text-[11px] text-zinc-500 mt-0.5">{subtitle}</p>}
  </div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-zinc-800 border border-white/10 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-zinc-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-medium" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

const InsightsPage = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchInsights(); }, []);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/user/insights`, { headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setData(await res.json());
      else toast.error("Failed to load insights");
    } catch { toast.error("Failed to load insights"); }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" data-testid="insights-loading">
        <Loader2 className="w-8 h-8 animate-spin text-red-400" />
      </div>
    );
  }

  if (!data) return null;

  const { stats, favorite_agents, recommendations, daily_activity } = data;

  const formatDate = (d) => {
    const date = new Date(d + "T00:00:00");
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };
  const chartData = daily_activity?.map(d => ({ ...d, date: formatDate(d.date) })) || [];

  return (
    <div className="min-h-screen bg-background" data-testid="insights-page">
      {/* Header */}
      <div className="border-b border-white/10 bg-zinc-900/50">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center gap-4">
          <button onClick={() => navigate("/dashboard")} className="text-zinc-500 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white font-['Outfit']">Your Insights</h1>
            <p className="text-sm text-zinc-500">See how you're using MAARS Command</p>
          </div>
          <Badge className="ml-auto bg-white/5 text-zinc-300 capitalize">{stats.plan} plan</Badge>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          <StatCard title="Messages Sent" value={stats.user_messages} subtitle={`${stats.ai_messages} AI responses`} icon={MessageSquare} color="indigo" />
          <StatCard title="Total Chats" value={stats.total_chats} icon={Bot} color="violet" />
          <StatCard title="Credits Left" value={stats.credits_remaining.toLocaleString()} subtitle={`${stats.credits_used.toLocaleString()} used`} icon={CreditCard} color="amber" />
          <StatCard title="Ratings Given" value={stats.feedback_up + stats.feedback_down} subtitle={`${stats.feedback_up} up / ${stats.feedback_down} down`} icon={ThumbsUp} color="emerald" />
          <StatCard title="Day Streak" value={`${stats.streak} days`} subtitle={stats.streak >= 7 ? "On fire!" : "Keep going!"} icon={Flame} color="red" />
        </div>

        {/* Activity Chart */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-red-400" />
              Your Activity (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="actGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                  <YAxis tick={{ fill: '#71717a', fontSize: 11 }} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="messages" stroke="#ef4444" fill="url(#actGrad)" name="Messages" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Favorite Agents + Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Favorites */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
                <Bot className="w-4 h-4 text-red-400" />
                Your Favorite Agents
              </CardTitle>
            </CardHeader>
            <CardContent>
              {favorite_agents.length > 0 ? (
                <div className="space-y-2">
                  {favorite_agents.map((agent, i) => (
                    <Link
                      key={agent.agent_id}
                      to={`/chat/${agent.agent_id}`}
                      className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors group"
                      data-testid={`fav-agent-${i}`}
                    >
                      <img src={agent.avatar} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white font-medium truncate">{agent.name}</p>
                        <p className="text-xs text-zinc-500">{agent.role}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-sm text-zinc-300 font-medium">{agent.messages}</p>
                        <p className="text-[10px] text-zinc-600">messages</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-white transition-colors shrink-0" />
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Bot className="w-10 h-10 text-zinc-700 mx-auto mb-2" />
                  <p className="text-zinc-500 text-sm">Start chatting to discover your favorites!</p>
                  <Link to="/agents">
                    <Button variant="outline" className="mt-3 border-white/10 text-sm" data-testid="browse-agents-btn">
                      Browse Agents
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader className="pb-2">
              <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Try These Agents
              </CardTitle>
              <p className="text-xs text-zinc-500">Agents you haven't used yet</p>
            </CardHeader>
            <CardContent>
              {recommendations.length > 0 ? (
                <div className="grid grid-cols-2 gap-2">
                  {recommendations.map((agent, i) => (
                    <Link
                      key={agent.agent_id}
                      to={`/chat/${agent.agent_id}`}
                      className="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-center group"
                      data-testid={`rec-agent-${i}`}
                    >
                      <img src={agent.avatar} alt="" className="w-10 h-10 rounded-lg mx-auto mb-2 object-cover" />
                      <p className="text-xs text-white font-medium truncate">{agent.name}</p>
                      <p className="text-[10px] text-zinc-500 truncate">{agent.role}</p>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Sparkles className="w-10 h-10 text-zinc-700 mx-auto mb-2" />
                  <p className="text-zinc-500 text-sm">You've tried all agents! Amazing.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default InsightsPage;
