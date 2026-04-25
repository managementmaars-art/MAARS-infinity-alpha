import { useState, useEffect, useCallback, useRef } from "react";
import {
  Users, MessageSquare, DollarSign, TrendingUp, Activity,
  BarChart3, PieChart as PieChartIcon, Bot, Zap, Crown,
  UserPlus, Radio, RefreshCw, Download, ThumbsUp, ThumbsDown, Star
} from "lucide-react";
import { useAuth, API } from "../../../App";
import { toast } from "sonner";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4", "#8b5cf6", "#ec4899", "#14b8a6"];

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const KPI_COLORS = {
  indigo: { color: "#818cf8", bg: "rgba(129,140,248,.15)" },
  emerald: { color: "#34d399", bg: "rgba(52,211,153,.15)" },
  teal: { color: "#2dd4bf", bg: "rgba(45,212,191,.15)" },
  violet: { color: "#a78bfa", bg: "rgba(167,139,250,.15)" },
  amber: { color: "#f59e0b", bg: "rgba(245,158,11,.15)" },
  red: { color: "#ef4444", bg: "rgba(239,68,68,.15)" },
};

const KpiCard = ({ title, value, subtitle, icon: Icon, color }) => {
  const c = KPI_COLORS[color] || KPI_COLORS.indigo;
  return (
    <div style={{ padding: "18px 20px", borderRadius: 14, background: c.bg, border: `1px solid ${c.color}30`, position: "relative", overflow: "hidden" }} data-testid={`kpi-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <div style={{ position: "absolute", top: 10, right: 12, opacity: 0.15 }}>
        <Icon size={40} style={{ color: c.color }} />
      </div>
      <p style={{ fontSize: 9, fontWeight: 700, color: c.color, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.1em" }}>{title}</p>
      <p style={{ fontSize: 24, fontWeight: 700, color: "#fff", margin: 0 }}>{value}</p>
      {subtitle && <p style={{ fontSize: 10, color: "#71717a", marginTop: 3 }}>{subtitle}</p>}
    </div>
  );
};

const ChartCard = ({ title, icon: Icon, children }) => (
  <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, overflow: "hidden" }}>
    <div style={{ padding: "12px 16px", borderBottom: "1px solid rgba(255,255,255,0.08)", display: "flex", alignItems: "center", gap: 8 }}>
      {Icon && <Icon size={14} style={{ color: "#ef4444" }} />}
      <span style={{ fontSize: 13, fontWeight: 600, color: "#fff", fontFamily: "'Outfit',sans-serif" }}>{title}</span>
    </div>
    <div style={{ padding: "14px 16px" }}>{children}</div>
  </div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#27272a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, padding: "10px 12px", boxShadow: "0 8px 32px rgba(0,0,0,0.4)" }}>
      <p style={{ fontSize: 11, color: "#71717a", marginBottom: 4 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ fontSize: 13, fontWeight: 500, color: p.color, margin: 0 }}>
          {p.name}: {typeof p.value === 'number' && p.name.includes('$') ? `$${p.value.toFixed(2)}` : p.value?.toLocaleString?.() ?? p.value}
        </p>
      ))}
    </div>
  );
};

const FEED_COLOR = {
  signup: "#34d399", payment: "#f59e0b", chat: "#818cf8", team: "#a78bfa"
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
  const [leaderboard, setLeaderboard] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [revTrends, setRevTrends] = useState(null);
  const feedRef = useRef([]);

  useEffect(() => {
    fetchAnalytics();
    fetchFeed();
    fetchPerformance();
    fetchRetention();
    fetchProjections();
    fetchCreditBurn();
    fetchLeaderboard();
    fetchHeatmap();
    fetchRevTrends();
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

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/agent-leaderboard`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setLeaderboard(await res.json());
    } catch {}
  };

  const fetchHeatmap = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/engagement-heatmap`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setHeatmap(await res.json());
    } catch {}
  };

  const fetchRevTrends = async () => {
    try {
      const res = await fetch(`${API}/admin/analytics/revenue-trends?days=30`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setRevTrends(await res.json());
    } catch {}
  };

  const handleExport = (report) => {
    window.open(`${API}/admin/analytics/export?report=${report}&token=${token}`, "_blank");
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
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }} data-testid="analytics-loading">
        <div style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          border: "3px solid rgba(129,140,248,0.2)",
          borderTopColor: "#818cf8",
          animation: "spin 0.75s linear infinite"
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!data) return <p style={{ color: "#71717a" }}>No analytics data available.</p>;

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
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }} data-testid="analytics-tab">
      {/* Header with Export */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, color: "#fff", fontFamily: "'Outfit',sans-serif", margin: 0 }}>Platform Analytics</h2>
          <p style={{ fontSize: 11, color: "#71717a", margin: 0 }}>Real-time business intelligence</p>
        </div>
        <button
          onClick={handleExportCSV}
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 8, background: "transparent", border: "1px solid rgba(255,255,255,0.1)", color: "#d4d4d8", fontSize: 13, cursor: "pointer" }}
          data-testid="export-csv-btn"
        >
          <Download size={14} /> Export CSV
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 16 }}>
        <KpiCard title="Total Users" value={kpis.total_users} icon={Users} color="indigo" />
        <KpiCard title="Active (7d)" value={kpis.active_7d} subtitle={`${kpis.total_users > 0 ? ((kpis.active_7d / kpis.total_users) * 100).toFixed(0) : 0}% of total`} icon={Activity} color="emerald" />
        <KpiCard title="Active (30d)" value={kpis.active_30d} icon={Activity} color="teal" />
        <KpiCard title="Total Chats" value={kpis.total_chats} icon={MessageSquare} color="violet" />
        <KpiCard title="Total Revenue" value={`$${kpis.total_revenue.toFixed(2)}`} icon={DollarSign} color="amber" />
        <KpiCard title="MRR" value={`$${kpis.mrr.toFixed(2)}`} subtitle="Monthly Recurring" icon={TrendingUp} color="red" />
      </div>

      {/* Live Activity Feed */}
      <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, overflow: "hidden" }} data-testid="activity-feed">
        <div style={{ padding: "12px 16px", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ position: "relative" }}>
                <Radio size={14} style={{ color: "#ef4444" }} />
                <span style={{ position: "absolute", top: -2, right: -2, width: 7, height: 7, background: "#ef4444", borderRadius: "50%", animation: "pulse 1.5s ease-in-out infinite" }} />
                <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }`}</style>
              </div>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#fff", fontFamily: "'Outfit',sans-serif" }}>Live Activity Feed</span>
            </div>
            <button onClick={fetchFeed} style={{ background: "none", border: "none", color: "#71717a", cursor: "pointer", padding: 4 }} data-testid="refresh-feed-btn">
              <RefreshCw size={14} />
            </button>
          </div>
          <p style={{ fontSize: 11, color: "#71717a", margin: "4px 0 0 0" }}>Auto-refreshes every 15 seconds</p>
        </div>
        <div style={{ padding: "14px 16px" }}>
          <div style={{ maxHeight: 256, overflowY: "auto", display: "flex", flexDirection: "column", gap: 2 }}>
            {feed.length > 0 ? feed.map((event, i) => {
              const IconMap = {
                "user-plus": UserPlus,
                "dollar-sign": DollarSign,
                "message-square": MessageSquare,
                "users": Users,
              };
              const EventIcon = IconMap[event.icon] || Activity;
              const iconColor = FEED_COLOR[event.type] || "#71717a";
              const timeAgo = getTimeAgo(event.timestamp);
              return (
                <div key={`${event.type}-${i}`} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px", borderRadius: 8 }} data-testid={`feed-item-${i}`}>
                  <div style={{ width: 32, height: 32, borderRadius: "50%", background: `${iconColor}26`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <EventIcon size={14} style={{ color: iconColor }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 13, color: "#fff", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{event.title}</p>
                    {event.detail && <p style={{ fontSize: 11, color: "#71717a", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{event.detail}</p>}
                  </div>
                  <span style={{ fontSize: 10, color: "#52525b", whiteSpace: "nowrap", flexShrink: 0 }}>{timeAgo}</span>
                </div>
              );
            }) : (
              <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "24px 0" }}>No activity yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Row 1: User Signups + Messages */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
        <ChartCard title="Daily Signups (30d)" icon={Users}>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={signupData}>
                <defs>
                  <linearGradient id="signupGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4fd1c5" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#4fd1c5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval={6} />
                <YAxis tick={{ fill: '#71717a', fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="signups" stroke="#4fd1c5" fill="url(#signupGrad)" name="Signups" />
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
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
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
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
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
            <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "32px 0" }}>No agent usage data yet</p>
          )}
        </ChartCard>

        <ChartCard title="Subscription Distribution" icon={Crown}>
          {plan_distribution?.length > 0 ? (
            <div className="h-72" style={{ display: "flex", alignItems: "center" }}>
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
            <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "32px 0" }}>No subscription data yet</p>
          )}
        </ChartCard>
      </div>

      {/* Row 4: Top Users + Model Costs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
        <ChartCard title="Top Users by Messages" icon={Users}>
          {top_users?.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {top_users.map((u, i) => {
                const rankStyle =
                  i === 0 ? { background: "rgba(245,158,11,0.2)", color: "#f59e0b" } :
                  i === 1 ? { background: "rgba(161,161,170,0.2)", color: "#d4d4d8" } :
                  i === 2 ? { background: "rgba(249,115,22,0.2)", color: "#fb923c" } :
                  { background: "rgba(255,255,255,0.05)", color: "#71717a" };
                return (
                  <div key={u.user_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 8, background: "rgba(255,255,255,0.05)" }} data-testid={`top-user-${i}`}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, flexShrink: 0, ...rankStyle }}>
                      {i + 1}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontSize: 13, color: "#fff", fontWeight: 500, margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{u.name || "Unknown"}</p>
                      <p style={{ fontSize: 11, color: "#71717a", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{u.email}</p>
                    </div>
                    <span style={{ border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, padding: "2px 8px", fontSize: 11, color: "#d4d4d8", flexShrink: 0 }}>
                      {u.total_messages} msgs
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "32px 0" }}>No user data yet</p>
          )}
        </ChartCard>

        <ChartCard title="Cost by AI Model" icon={Zap}>
          {model_costs?.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {model_costs.map((m, i) => {
                const maxCost = model_costs[0]?.cost || 1;
                return (
                  <div key={m.model} style={{ display: "flex", flexDirection: "column", gap: 4 }} data-testid={`model-cost-${i}`}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 13 }}>
                      <span style={{ color: "#d4d4d8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 200 }}>{m.model}</span>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <span style={{ color: "#71717a", fontSize: 11 }}>{m.calls} calls</span>
                        <span style={{ color: "#fff", fontWeight: 500 }}>${m.cost.toFixed(4)}</span>
                      </div>
                    </div>
                    <div style={{ height: 8, background: "rgba(255,255,255,0.05)", borderRadius: 4, overflow: "hidden" }}>
                      <div
                        style={{ height: "100%", borderRadius: 4, background: "linear-gradient(to right, #ef4444, #f97316)", width: `${(m.cost / maxCost) * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "32px 0" }}>No model cost data yet</p>
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
              <Bar dataKey="input_tokens" stackId="a" fill="#4fd1c5" name="Input Tokens" />
              <Bar dataKey="output_tokens" stackId="a" fill="#8b5cf6" name="Output Tokens" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Agent Performance Scoring */}
      <ChartCard title="Agent Performance Scoring" icon={Star}>
        {performance.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {performance.map((agent, i) => {
              const sat = agent.satisfaction_rate;
              const barColor = sat === null ? "#52525b" : sat >= 80 ? "#10b981" : sat >= 50 ? "#f59e0b" : "#ef4444";
              const satTextColor = sat === null ? "#52525b" : sat >= 80 ? "#34d399" : sat >= 50 ? "#f59e0b" : "#ef4444";
              return (
                <div key={agent.agent_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 8, background: "rgba(255,255,255,0.05)" }} data-testid={`perf-agent-${i}`}>
                  <img src={agent.avatar} alt="" style={{ width: 36, height: 36, borderRadius: 8, objectFit: "cover", flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <p style={{ fontSize: 13, color: "#fff", fontWeight: 500, margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</p>
                      <span style={{ fontSize: 10, color: "#71717a" }}>{agent.role}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 4 }}>
                      <div style={{ flex: 1, height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3, overflow: "hidden", maxWidth: 200 }}>
                        <div style={{ height: "100%", borderRadius: 3, background: barColor, width: `${sat ?? 0}%` }} />
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11 }}>
                        <span style={{ color: "#71717a" }}>{agent.total_messages} msgs</span>
                        {agent.total_feedback > 0 && (
                          <>
                            <span style={{ color: "#34d399", display: "flex", alignItems: "center", gap: 2 }}><ThumbsUp size={10} />{agent.thumbs_up}</span>
                            <span style={{ color: "#ef4444", display: "flex", alignItems: "center", gap: 2 }}><ThumbsDown size={10} />{agent.thumbs_down}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0, width: 64 }}>
                    {sat !== null ? (
                      <p style={{ fontSize: 18, fontWeight: 700, color: satTextColor, margin: 0 }}>{sat}%</p>
                    ) : (
                      <p style={{ fontSize: 11, color: "#3f3f46", margin: 0 }}>No ratings</p>
                    )}
                    {agent.feedback_rate > 0 && <p style={{ fontSize: 10, color: "#3f3f46", margin: 0 }}>{agent.feedback_rate}% rated</p>}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ color: "#71717a", fontSize: 13, textAlign: "center", padding: "32px 0" }}>No performance data yet. Users will rate responses with thumbs up/down.</p>
        )}
      </ChartCard>

      {/* Revenue Projections */}
      {projections && (
        <ChartCard title="Revenue Projections (6 Months)" icon={TrendingUp}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 16 }}>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)" }}>
              <p style={{ fontSize: 11, color: "#34d399", margin: 0 }}>Current MRR</p>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>${projections.current?.mrr?.toLocaleString()}</p>
            </div>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.2)" }}>
              <p style={{ fontSize: 11, color: "#60a5fa", margin: 0 }}>30d Revenue</p>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>${projections.current?.revenue_30d?.toLocaleString()}</p>
            </div>
            <div style={{ padding: "10px 12px", borderRadius: 8, background: "rgba(167,139,250,0.1)", border: "1px solid rgba(167,139,250,0.2)" }}>
              <p style={{ fontSize: 11, color: "#a78bfa", margin: 0 }}>Profit Margin</p>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>{projections.current?.profit_margin}%</p>
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
            <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
              <p style={{ fontSize: 11, color: "#a1a1aa", fontWeight: 500, marginBottom: 8 }}>Top Models by Cost (30d)</p>
              {creditBurn.by_model.slice(0, 5).map((m, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 11 }}>
                  <span style={{ color: "#d4d4d8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{m.model}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ color: "#71717a" }}>{m.total_calls} calls</span>
                    <span style={{ color: "#f59e0b", fontWeight: 500 }}>${m.total_cost.toFixed(4)}</span>
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

      {/* Agent Leaderboard */}
      {leaderboard?.leaderboard?.length > 0 && (
        <ChartCard title="Agent Leaderboard" icon={Crown}>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }} data-testid="agent-leaderboard">
            {leaderboard.leaderboard.slice(0, 10).map((agent, i) => {
              const rankStyle =
                i === 0 ? { background: "rgba(245,158,11,0.2)", color: "#f59e0b" } :
                i === 1 ? { background: "rgba(161,161,170,0.2)", color: "#d4d4d8" } :
                i === 2 ? { background: "rgba(249,115,22,0.2)", color: "#fb923c" } :
                { background: "#27272a", color: "#71717a" };
              return (
                <div key={agent.agent_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 8, background: "rgba(255,255,255,0.03)" }} data-testid={`leaderboard-agent-${i}`}>
                  <span style={{ width: 24, height: 24, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "50%", fontSize: 11, fontWeight: 700, flexShrink: 0, ...rankStyle }}>{i + 1}</span>
                  {agent.avatar && <img src={agent.avatar} alt="" style={{ width: 32, height: 32, borderRadius: "50%", objectFit: "cover" }} />}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 13, color: "#fff", fontWeight: 500, margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</p>
                    <p style={{ fontSize: 10, color: "#71717a", margin: 0 }}>{agent.role}</p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 11 }}>
                    <div style={{ textAlign: "center" }}>
                      <p style={{ color: "#fff", fontWeight: 500, margin: 0 }}>{agent.total_chats}</p>
                      <p style={{ color: "#3f3f46", margin: 0 }}>chats</p>
                    </div>
                    <div style={{ textAlign: "center" }}>
                      <p style={{ color: "#fff", fontWeight: 500, margin: 0 }}>{agent.total_messages}</p>
                      <p style={{ color: "#3f3f46", margin: 0 }}>msgs</p>
                    </div>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        {agent.satisfaction_pct >= 70 ? <ThumbsUp size={10} style={{ color: "#34d399" }} /> : <ThumbsDown size={10} style={{ color: "#ef4444" }} />}
                        <span style={{ color: agent.satisfaction_pct >= 70 ? "#34d399" : "#ef4444" }}>{agent.satisfaction_pct}%</span>
                      </div>
                      <p style={{ color: "#3f3f46", margin: 0 }}>rating</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ChartCard>
      )}

      {/* Engagement Heatmap */}
      {heatmap?.heatmap?.length > 0 && (
        <ChartCard title="User Activity Heatmap" icon={Activity}>
          <div data-testid="engagement-heatmap">
            <div style={{ display: "flex", gap: 2 }}>
              <div style={{ width: 32 }} />
              {Array.from({length: 24}, (_, h) => (
                <div key={h} style={{ flex: 1, textAlign: "center", fontSize: 8, color: "#52525b" }}>{h}</div>
              ))}
            </div>
            {(heatmap.days || []).map(day => {
              const dayData = Object.fromEntries(heatmap.heatmap.filter(h => h.day === day).map(h => [h.hour, h]));
              return (
                <div key={day} style={{ display: "flex", gap: 2, marginBottom: 2 }}>
                  <div style={{ width: 32, fontSize: 9, color: "#71717a", display: "flex", alignItems: "center" }}>{day}</div>
                  {Array.from({length: 24}, (_, h) => {
                    const cell = dayData[h];
                    const intensity = cell?.intensity || 0;
                    return (
                      <div
                        key={h}
                        style={{ flex: 1, aspectRatio: "1", borderRadius: 2, backgroundColor: intensity > 0 ? `rgba(99,102,241,${0.15 + intensity * 0.85})` : 'rgba(255,255,255,0.03)' }}
                        title={cell ? `${day} ${h}:00 - ${cell.count} messages` : `${day} ${h}:00 - 0`}
                      />
                    );
                  })}
                </div>
              );
            })}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 4, marginTop: 8 }}>
              <span style={{ fontSize: 9, color: "#52525b" }}>Less</span>
              {[0.1, 0.3, 0.5, 0.7, 1].map(v => (
                <div key={v} style={{ width: 12, height: 12, borderRadius: 2, backgroundColor: `rgba(99,102,241,${0.15 + v * 0.85})` }} />
              ))}
              <span style={{ fontSize: 9, color: "#52525b" }}>More</span>
            </div>
          </div>
        </ChartCard>
      )}

      {/* Revenue Trends */}
      {revTrends?.trends?.length > 0 && (
        <ChartCard title="Revenue Trends (30d)" icon={TrendingUp}>
          <div style={{ display: "flex", gap: 16, marginBottom: 12 }} data-testid="revenue-trends-summary">
            <div style={{ padding: "8px 12px", borderRadius: 8, background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)", flex: 1, textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>${revTrends.summary?.total_revenue?.toFixed(2)}</p>
              <p style={{ fontSize: 10, color: "#34d399", margin: 0 }}>Total Revenue</p>
            </div>
            <div style={{ padding: "8px 12px", borderRadius: 8, background: "rgba(129,140,248,0.1)", border: "1px solid rgba(129,140,248,0.2)", flex: 1, textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>${revTrends.summary?.avg_daily_revenue?.toFixed(2)}</p>
              <p style={{ fontSize: 10, color: "#818cf8", margin: 0 }}>Avg Daily</p>
            </div>
            <div style={{ padding: "8px 12px", borderRadius: 8, background: "rgba(167,139,250,0.1)", border: "1px solid rgba(167,139,250,0.2)", flex: 1, textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>{revTrends.summary?.total_transactions}</p>
              <p style={{ fontSize: 10, color: "#a78bfa", margin: 0 }}>Transactions</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={revTrends.trends} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 9 }} />
              <YAxis tick={{ fill: '#71717a', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="cumulative" name="$ Cumulative" stroke="#22c55e" fill="rgba(34,197,94,0.15)" />
              <Area type="monotone" dataKey="revenue" name="$ Daily" stroke="#8b5cf6" fill="rgba(139,92,246,0.15)" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      {/* Export Section */}
      <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: 16 }} data-testid="analytics-export">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
          <div>
            <p style={{ color: "#fff", fontWeight: 500, fontSize: 13, margin: 0 }}>Export Analytics</p>
            <p style={{ fontSize: 11, color: "#71717a", margin: 0 }}>Download reports as CSV files</p>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {[{id: "overview", label: "Overview"}, {id: "users", label: "Users"}, {id: "revenue", label: "Revenue"}, {id: "agents", label: "Agents"}].map(r => (
              <button key={r.id} style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 12px", borderRadius: 6, background: "transparent", border: "1px solid rgba(255,255,255,0.1)", color: "#d4d4d8", fontSize: 12, cursor: "pointer" }} onClick={() => handleExport(r.id)} data-testid={`export-${r.id}`}>
                <Download size={11} />{r.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsTab;
