import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Users, MessageSquare, DollarSign, TrendingUp, Activity,
  BarChart3, PieChart as PieChartIcon, Loader2, Bot, Zap, Crown,
  UserPlus, Radio, RefreshCw, Download, ThumbsUp, ThumbsDown, Star
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4", "#8b5cf6", "#ec4899", "#14b8a6"];

const KpiCard = ({ title, value, subtitle, icon: Icon, color }) => (
  <div className={`p-5 rounded-xl bg-${color}-500/10 border border-${color}-500/20 relative overflow-hidden`} data-testid={`kpi-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="absolute top-3 right-3 opacity-20">
      <Icon className={`w-10 h-10 text-${color}-400`} />
    </div>
    <p className={`text-xs font-medium text-${color}-400 mb-1 uppercase tracking-wide`}>{title}</p>
    <p className="text-2xl font-bold text-white">{value}</p>
    {subtitle && <p className="text-xs text-zinc-500 mt-1">{subtitle}</p>}
  </div>
);

const ChartCard = ({ title, icon: Icon, children, className = "" }) => (
  <Card className={`bg-zinc-900/50 border-white/10 ${className}`}>
    <CardHeader className="pb-2">
      <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-red-400" />}
        {title}
      </CardTitle>
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-zinc-800 border border-white/10 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-zinc-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-medium" style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' && p.name.includes('$') ? `$${p.value.toFixed(2)}` : p.value?.toLocaleString?.() ?? p.value}
        </p>
      ))}
    </div>
  );
};

const getTimeAgo = (timestamp) => {
  if (!timestamp) return "";
  const now = new Date();
  const date = new Date(timestamp);
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

const AnalyticsTab = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feed, setFeed] = useState([]);
  const [feedLoading, setFeedLoading] = useState(false);
  const [performance, setPerformance] = useState([]);
  const [retention, setRetention] = useState([]);
  const [projections, setProjections] = useState(null);
  const [creditBurn, setCreditBurn] = useState(null);
  const feedRef = useRef([]);

  useEffect(() => {
    fetchAnalytics();
    fetchFeed();
    fetchPerformance();
    fetchRetention();
    fetchProjections();
    fetchCreditBurn();
    const interval = setInterval(fetchFeed, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchFeed = async () => {
    try {
      const res = await fetch(`${API}/admin/activity-feed?limit=20`, { headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const newFeed = await res.json();
        setFeed(newFeed);
        feedRef.current = newFeed;
      }
    } catch {}
  };

  const fetchPerformance = async () => {
    try {
      const res = await fetch(`${API}/admin/agent-performance`, { headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setPerformance(await res.json());
    } catch {}
  };

  const fetchRetention = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/retention`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setRetention(await res.json());
    } catch {}
  };

  const fetchProjections = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/projections`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setProjections(await res.json());
    } catch {}
  };

  const fetchCreditBurn = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/credit-burn`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setCreditBurn(await res.json());
    } catch {}
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/analytics`, { headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setData(await res.json());
      } else {
        toast.error("Failed to load analytics");
      }
    } catch {
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/export?format=csv`, { headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `maars_analytics_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast.success("Analytics exported");
      } else {
        toast.error("Export failed");
      }
    } catch {
      toast.error("Export failed");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="analytics-loading">
        <Loader2 className="w-8 h-8 animate-spin text-red-400" />
      </div>
    );
  }

  if (!data) return <p className="text-zinc-500">No analytics data available.</p>;

  const { kpis, daily_signups, daily_messages, daily_revenue, agent_usage, plan_distribution, token_usage, top_users, model_costs } = data;

  // Format dates for display (show MMM DD)
  const formatDate = (dateStr) => {
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  const signupData = daily_signups?.map(d => ({ ...d, date: formatDate(d.date) })) || [];
  const messageData = daily_messages?.map(d => ({ ...d, date: formatDate(d.date) })) || [];
  const revenueData = daily_revenue?.map(d => ({ ...d, date: formatDate(d.date) })) || [];
  const tokenData = token_usage?.map(d => ({ ...d, date: formatDate(d.date) })) || [];

  return (
    <div className="space-y-6" data-testid="analytics-tab">
      {/* Header with Export */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white font-['Outfit']">Platform Analytics</h2>
          <p className="text-xs text-zinc-500">Real-time business intelligence</p>
        </div>
        <Button
          onClick={handleExportCSV}
          variant="outline"
          className="border-white/10 text-zinc-300 hover:text-white"
          data-testid="export-csv-btn"
        >
          <Download className="w-4 h-4 mr-2" /> Export CSV
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard title="Total Users" value={kpis.total_users} icon={Users} color="indigo" />
        <KpiCard title="Active (7d)" value={kpis.active_7d} subtitle={`${kpis.total_users > 0 ? ((kpis.active_7d / kpis.total_users) * 100).toFixed(0) : 0}% of total`} icon={Activity} color="emerald" />
        <KpiCard title="Active (30d)" value={kpis.active_30d} icon={Activity} color="teal" />
        <KpiCard title="Total Chats" value={kpis.total_chats} icon={MessageSquare} color="violet" />
        <KpiCard title="Total Revenue" value={`$${kpis.total_revenue.toFixed(2)}`} icon={DollarSign} color="amber" />
        <KpiCard title="MRR" value={`$${kpis.mrr.toFixed(2)}`} subtitle="Monthly Recurring" icon={TrendingUp} color="red" />
      </div>

      {/* Live Activity Feed */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="activity-feed">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
              <div className="relative">
                <Radio className="w-4 h-4 text-red-400" />
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              </div>
              Live Activity Feed
            </CardTitle>
            <button onClick={fetchFeed} className="text-zinc-500 hover:text-white transition-colors" data-testid="refresh-feed-btn">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-zinc-500">Auto-refreshes every 15 seconds</p>
        </CardHeader>
        <CardContent>
          <div className="max-h-64 overflow-y-auto space-y-1 pr-1 scrollbar-thin">
            {feed.length > 0 ? feed.map((event, i) => {
              const IconMap = {
                "user-plus": UserPlus,
                "dollar-sign": DollarSign,
                "message-square": MessageSquare,
                "users": Users,
              };
              const colorMap = {
                signup: "emerald",
                payment: "amber",
                chat: "indigo",
                team: "violet",
              };
              const EventIcon = IconMap[event.icon] || Activity;
              const color = colorMap[event.type] || "zinc";
              const timeAgo = getTimeAgo(event.timestamp);
              return (
                <div key={`${event.type}-${i}`} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 transition-colors" data-testid={`feed-item-${i}`}>
                  <div className={`w-8 h-8 rounded-full bg-${color}-500/15 flex items-center justify-center shrink-0`}>
                    <EventIcon className={`w-4 h-4 text-${color}-400`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{event.title}</p>
                    {event.detail && <p className="text-xs text-zinc-500 truncate">{event.detail}</p>}
                  </div>
                  <span className="text-[10px] text-zinc-600 whitespace-nowrap shrink-0">{timeAgo}</span>
                </div>
              );
            }) : (
              <p className="text-zinc-500 text-sm text-center py-6">No activity yet</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Row 1: User Signups + Messages */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Daily Signups (30d)" icon={Users}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={signupData}>
                <defs>
                  <linearGradient id="signupGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                <YAxis tick={{ fill: '#71717a', fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="signups" stroke="#6366f1" fill="url(#signupGrad)" name="Signups" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Daily Messages (30d)" icon={MessageSquare}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={messageData}>
                <defs>
                  <linearGradient id="msgGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                <YAxis tick={{ fill: '#71717a', fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="messages" stroke="#22c55e" fill="url(#msgGrad)" name="Messages" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Row 2: Revenue + Token Cost */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Daily Revenue (30d)" icon={DollarSign}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="revenue" fill="#eab308" radius={[4, 4, 0, 0]} name="$ Revenue" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Daily API Cost (30d)" icon={Zap}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={tokenData}>
                <defs>
                  <linearGradient id="costGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="cost" stroke="#ef4444" fill="url(#costGrad)" name="$ Cost" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Row 3: Agent Usage + Subscription Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Agent Usage (by messages)" icon={Bot}>
          {agent_usage?.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={agent_usage.slice(0, 12)} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis type="number" tick={{ fill: '#71717a', fontSize: 11 }} allowDecimals={false} />
                  <YAxis dataKey="name" type="category" tick={{ fill: '#d4d4d8', fontSize: 11 }} width={120} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="messages" fill="#ef4444" radius={[0, 4, 4, 0]} name="Messages" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-zinc-500 text-sm py-8 text-center">No agent usage data yet</p>
          )}
        </ChartCard>

        <ChartCard title="Subscription Distribution" icon={Crown}>
          {plan_distribution?.length > 0 ? (
            <div className="h-72 flex items-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={plan_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="count"
                    nameKey="plan"
                    label={({ plan, count }) => `${plan} (${count})`}
                  >
                    {plan_distribution.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend formatter={(value) => <span className="text-zinc-300 capitalize text-sm">{value}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-zinc-500 text-sm py-8 text-center">No subscription data yet</p>
          )}
        </ChartCard>
      </div>

      {/* Row 4: Top Users + Model Costs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Top Users by Messages" icon={Users}>
          {top_users?.length > 0 ? (
            <div className="space-y-2">
              {top_users.map((u, i) => (
                <div key={u.user_id} className="flex items-center gap-3 p-3 rounded-lg bg-white/5" data-testid={`top-user-${i}`}>
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-amber-500/20 text-amber-400' :
                    i === 1 ? 'bg-zinc-400/20 text-zinc-300' :
                    i === 2 ? 'bg-orange-500/20 text-orange-400' :
                    'bg-white/5 text-zinc-500'
                  }`}>
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white font-medium truncate">{u.name || "Unknown"}</p>
                    <p className="text-xs text-zinc-500 truncate">{u.email}</p>
                  </div>
                  <Badge variant="outline" className="border-white/10 text-zinc-300 shrink-0">
                    {u.total_messages} msgs
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-zinc-500 text-sm py-8 text-center">No user data yet</p>
          )}
        </ChartCard>

        <ChartCard title="Cost by AI Model" icon={Zap}>
          {model_costs?.length > 0 ? (
            <div className="space-y-2">
              {model_costs.map((m, i) => {
                const maxCost = model_costs[0]?.cost || 1;
                return (
                  <div key={m.model} className="space-y-1" data-testid={`model-cost-${i}`}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-zinc-300 truncate max-w-[200px]">{m.model}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-zinc-500 text-xs">{m.calls} calls</span>
                        <span className="text-white font-medium">${m.cost.toFixed(4)}</span>
                      </div>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-red-500 to-orange-500"
                        style={{ width: `${(m.cost / maxCost) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-zinc-500 text-sm py-8 text-center">No model cost data yet</p>
          )}
        </ChartCard>
      </div>

      {/* Token Usage Details */}
      <ChartCard title="Token Usage Breakdown (30d)" icon={BarChart3}>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tokenData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
              <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend formatter={(value) => <span className="text-zinc-300 text-sm">{value}</span>} />
              <Bar dataKey="input_tokens" stackId="a" fill="#6366f1" name="Input Tokens" />
              <Bar dataKey="output_tokens" stackId="a" fill="#8b5cf6" name="Output Tokens" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Agent Performance Scoring */}
      <ChartCard title="Agent Performance Scoring" icon={Star} className="col-span-full">
        {performance.length > 0 ? (
          <div className="space-y-2">
            {performance.map((agent, i) => {
              const sat = agent.satisfaction_rate;
              const barColor = sat === null ? "bg-zinc-600" : sat >= 80 ? "bg-emerald-500" : sat >= 50 ? "bg-amber-500" : "bg-red-500";
              return (
                <div key={agent.agent_id} className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/[0.07] transition-colors" data-testid={`perf-agent-${i}`}>
                  <img src={agent.avatar} alt="" className="w-9 h-9 rounded-lg object-cover shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-white font-medium truncate">{agent.name}</p>
                      <span className="text-[10px] text-zinc-500">{agent.role}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden max-w-[200px]">
                        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${sat ?? 0}%` }} />
                      </div>
                      <div className="flex items-center gap-2 text-[11px]">
                        <span className="text-zinc-500">{agent.total_messages} msgs</span>
                        {agent.total_feedback > 0 && (
                          <>
                            <span className="text-emerald-400 flex items-center gap-0.5"><ThumbsUp className="w-3 h-3" />{agent.thumbs_up}</span>
                            <span className="text-red-400 flex items-center gap-0.5"><ThumbsDown className="w-3 h-3" />{agent.thumbs_down}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0 w-16">
                    {sat !== null ? (
                      <p className={`text-lg font-bold ${sat >= 80 ? "text-emerald-400" : sat >= 50 ? "text-amber-400" : "text-red-400"}`}>{sat}%</p>
                    ) : (
                      <p className="text-xs text-zinc-600">No ratings</p>
                    )}
                    {agent.feedback_rate > 0 && <p className="text-[10px] text-zinc-600">{agent.feedback_rate}% rated</p>}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-zinc-500 text-sm py-8 text-center">No performance data yet. Users will rate responses with thumbs up/down.</p>
        )}
      </ChartCard>

      {/* Revenue Projections */}
      {projections && (
        <ChartCard title="Revenue Projections (6 Months)" icon={TrendingUp} className="col-span-2">
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-xs text-emerald-400">Current MRR</p>
              <p className="text-lg font-bold text-white">${projections.current?.mrr?.toLocaleString()}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <p className="text-xs text-blue-400">30d Revenue</p>
              <p className="text-lg font-bold text-white">${projections.current?.revenue_30d?.toLocaleString()}</p>
            </div>
            <div className="p-3 rounded-lg bg-violet-500/10 border border-violet-500/20">
              <p className="text-xs text-violet-400">Profit Margin</p>
              <p className="text-lg font-bold text-white">{projections.current?.profit_margin}%</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={projections.projections} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#71717a', fontSize: 11 }} />
              <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="projected_revenue" name="$ Revenue" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="projected_cost" name="$ Cost" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      {/* User Retention Cohorts */}
      {retention.length > 0 && (
        <ChartCard title="User Retention (Weekly Cohorts)" icon={UserPlus}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={retention} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="week_start" tick={{ fill: '#71717a', fontSize: 11 }} />
              <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="signed_up" name="Signed Up" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="returned_week1" name="Returned W1" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              <Bar dataKey="returned_week2" name="Returned W2" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      {/* Credit Burn Rate */}
      {creditBurn && (
        <ChartCard title="Credit Burn - Daily (7d)" icon={Zap}>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={creditBurn.daily_burn} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 10 }} />
              <YAxis tick={{ fill: '#71717a', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="cost" name="$ Cost" stroke="#ef4444" fill="rgba(239,68,68,0.2)" />
            </AreaChart>
          </ResponsiveContainer>
          {creditBurn.by_model?.length > 0 && (
            <div className="mt-3 space-y-1.5">
              <p className="text-xs text-zinc-400 font-medium mb-2">Top Models by Cost (30d)</p>
              {creditBurn.by_model.slice(0, 5).map((m, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 truncate">{m.model}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-zinc-500">{m.total_calls} calls</span>
                    <span className="text-amber-400 font-medium">${m.total_cost.toFixed(4)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ChartCard>
      )}

      {/* Top Agents by Cost */}
      {creditBurn?.by_agent?.length > 0 && (
        <ChartCard title="Agent Cost Efficiency (30d)" icon={Bot}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={creditBurn.by_agent.slice(0, 8)} layout="vertical" margin={{ top: 5, right: 10, left: 60, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#71717a', fontSize: 10 }} />
              <YAxis dataKey="agent_name" type="category" tick={{ fill: '#a1a1aa', fontSize: 10 }} width={55} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="total_cost" name="$ Total Cost" fill="#f97316" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}
    </div>
  );
};

export default AnalyticsTab;
