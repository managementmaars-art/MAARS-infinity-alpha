import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  MessageSquare, Bot, Zap, TrendingUp, ThumbsUp, ThumbsDown,
  Flame, CreditCard, ArrowLeft, Loader2, ChevronRight, Sparkles,
  Activity, BarChart3, Star
} from "lucide-react";
import { toast } from "sonner";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";

/* ─── Design tokens ─────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  green:  "#34d399",
  amber:  "#f59e0b",
  red:    "#f87171",
  pink:   "#f472b6",
  indigo: "#6366f1",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
};

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes ins_fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
  @keyframes ins_spin   { to { transform: rotate(360deg); } }
  @keyframes ins_pulse  { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(1.4); } }
  @keyframes ins_bar    { from { transform:scaleY(0); } to { transform:scaleY(1); } }
`;

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "rgba(5,10,20,0.95)", border: `1px solid ${T.border}`, borderRadius: 10, padding: "10px 14px", backdropFilter: "blur(12px)" }}>
      <p style={{ fontSize: 11, color: "#475569", marginBottom: 5 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ fontSize: 13, fontWeight: 700, color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  );
}

const InsightsPage = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchInsights(); }, []);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/user/insights`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setData(await res.json());
      else toast.error("Failed to load insights");
    } catch { toast.error("Failed to load insights"); }
    setLoading(false);
  };

  if (loading) return (
    <div style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 14 }} data-testid="insights-loading">
      <style>{STYLES}</style>
      <div style={{ position: "relative", width: 44, height: 44 }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid transparent", borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.25)", animation: "ins_spin 0.85s linear infinite" }} />
        <div style={{ position: "absolute", inset: 6, borderRadius: "50%", border: "2px solid transparent", borderBottomColor: T.violet, borderLeftColor: "rgba(124,58,237,0.25)", animation: "ins_spin 0.6s linear infinite reverse" }} />
      </div>
      <p style={{ fontSize: 12, color: "#475569" }}>Loading your insights…</p>
    </div>
  );

  if (!data) return null;

  const { stats, favorite_agents, recommendations, daily_activity } = data;

  const formatDate = (d) => new Date(d + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const chartData  = daily_activity?.map(d => ({ ...d, date: formatDate(d.date) })) || [];

  const statItems = [
    { title: "Messages Sent",  value: stats.user_messages,            sub: `${stats.ai_messages} AI responses`,  icon: MessageSquare, color: T.indigo },
    { title: "Total Chats",    value: stats.total_chats,              sub: "conversations started",              icon: Bot,           color: T.violet },
    { title: "Credits Left",   value: stats.credits_remaining?.toLocaleString(), sub: `${stats.credits_used?.toLocaleString()} used`, icon: CreditCard, color: T.amber },
    { title: "Ratings Given",  value: stats.feedback_up + stats.feedback_down, sub: `${stats.feedback_up}↑ ${stats.feedback_down}↓`, icon: ThumbsUp, color: T.green },
    { title: "Day Streak",     value: `${stats.streak}d`,             sub: stats.streak >= 7 ? "🔥 On fire!" : "Keep going!", icon: Flame, color: T.red },
  ];

  return (
    <div data-testid="insights-page" style={{ animation: "ins_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 28 }}>
        <button
          onClick={() => navigate("/dashboard")}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 36, height: 36, borderRadius: 10, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#475569", cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.color = "#e2e8f0"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; }}
          onMouseLeave={e => { e.currentTarget.style.color = "#475569"; e.currentTarget.style.borderColor = T.border; }}>
          <ArrowLeft style={{ width: 15, height: 15 }} />
        </button>
        <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(124,58,237,0.15))", border: "1px solid rgba(99,102,241,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <BarChart3 style={{ width: 20, height: 20, color: T.indigo }} />
        </div>
        <div>
          <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Your Insights</h1>
          <p style={{ fontSize: 12, color: "#475569", margin: 0 }}>How you're using MAARS Command</p>
        </div>
        {stats.plan && (
          <span style={{ marginLeft: "auto", padding: "3px 10px", borderRadius: 20, background: "rgba(255,255,255,0.05)", border: `1px solid ${T.border}`, color: "#64748b", fontSize: 11, fontWeight: 600, textTransform: "capitalize" }}>
            {stats.plan} plan
          </span>
        )}
      </div>

      {/* ── Stat cards ──────────────────────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10, marginBottom: 28 }}>
        {statItems.map((s, i) => {
          const Icon = s.icon;
          return (
            <div key={i} data-testid={`insight-${s.title.toLowerCase().replace(/\s+/g, '-')}`}
              style={{ padding: "14px 16px", borderRadius: 14, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.color, opacity: 0.5 }} />
              <Icon style={{ width: 20, height: 20, color: s.color, opacity: 0.5, position: "absolute", top: 12, right: 12 }} />
              <p style={{ fontSize: 9, color: "#475569", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 6px" }}>{s.title}</p>
              <p style={{ fontSize: 22, fontWeight: 800, color: s.color, fontFamily: "Outfit, sans-serif", lineHeight: 1, margin: "0 0 4px" }}>{s.value}</p>
              {s.sub && <p style={{ fontSize: 10, color: "#475569", margin: 0 }}>{s.sub}</p>}
            </div>
          );
        })}
      </div>

      {/* ── Activity chart ──────────────────────────────────────────────── */}
      <div style={{ borderRadius: 16, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", padding: 20, marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <TrendingUp style={{ width: 14, height: 14, color: T.teal }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Activity — Last 30 Days</span>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: T.teal, animation: "ins_pulse 2.5s ease-in-out infinite" }} />
            <span style={{ fontSize: 10, color: T.teal, fontWeight: 600 }}>LIVE</span>
          </div>
        </div>
        <div style={{ height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="insGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={T.teal} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={T.teal} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fill: "#334155", fontSize: 10 }} interval={6} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#334155", fontSize: 10 }} allowDecimals={false} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: T.teal, strokeWidth: 1, strokeDasharray: "4 4" }} />
              <Area type="monotone" dataKey="messages" stroke={T.teal} strokeWidth={2} fill="url(#insGrad)" name="Messages" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Favorites + Recommendations ─────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 20 }}>
        {/* Favorite agents */}
        <div style={{ borderRadius: 16, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Star style={{ width: 14, height: 14, color: T.amber }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Your Favorite Agents</span>
          </div>
          {favorite_agents?.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {favorite_agents.map((agent, i) => (
                <Link key={agent.agent_id} to={`/chat/${agent.agent_id}`} data-testid={`fav-agent-${i}`}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 12, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textDecoration: "none", transition: "all 0.15s" }}
                  onMouseEnter={e => { e.currentTarget.style.background = "rgba(79,209,197,0.05)"; e.currentTarget.style.borderColor = "rgba(79,209,197,0.2)"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; e.currentTarget.style.borderColor = T.border; }}>
                  <img src={agent.avatar} alt="" style={{ width: 36, height: 36, borderRadius: 10, objectFit: "cover", flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", margin: "0 0 1px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</p>
                    <p style={{ fontSize: 10, color: "#475569", margin: 0 }}>{agent.role}</p>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0 }}>
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#94a3b8", margin: "0 0 1px" }}>{agent.messages}</p>
                    <p style={{ fontSize: 9, color: "#334155", margin: 0 }}>messages</p>
                  </div>
                  <ChevronRight style={{ width: 13, height: 13, color: "#334155", flexShrink: 0 }} />
                </Link>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "32px 0" }}>
              <Bot style={{ width: 36, height: 36, color: "#1e293b", margin: "0 auto 10px" }} />
              <p style={{ fontSize: 12, color: "#475569", marginBottom: 14 }}>Start chatting to discover your favorites!</p>
              <Link to="/agents" style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "8px 16px", borderRadius: 9, background: "rgba(79,209,197,0.1)", border: "1px solid rgba(79,209,197,0.2)", color: T.teal, fontSize: 12, fontWeight: 600, textDecoration: "none" }} data-testid="browse-agents-btn">
                Browse Agents
              </Link>
            </div>
          )}
        </div>

        {/* Recommendations */}
        <div style={{ borderRadius: 16, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Sparkles style={{ width: 14, height: 14, color: T.amber }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>Try These Agents</span>
          </div>
          <p style={{ fontSize: 10, color: "#334155", marginBottom: 14 }}>Agents you haven't used yet</p>
          {recommendations?.length > 0 ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {recommendations.map((agent, i) => (
                <Link key={agent.agent_id} to={`/chat/${agent.agent_id}`} data-testid={`rec-agent-${i}`}
                  style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "12px 8px", borderRadius: 12, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textDecoration: "none", transition: "all 0.15s", textAlign: "center" }}
                  onMouseEnter={e => { e.currentTarget.style.background = "rgba(79,209,197,0.06)"; e.currentTarget.style.borderColor = "rgba(79,209,197,0.2)"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.03)"; e.currentTarget.style.borderColor = T.border; }}>
                  <img src={agent.avatar} alt="" style={{ width: 40, height: 40, borderRadius: 10, objectFit: "cover", marginBottom: 8 }} />
                  <p style={{ fontSize: 11, fontWeight: 700, color: "#e2e8f0", margin: "0 0 2px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", width: "100%" }}>{agent.name}</p>
                  <p style={{ fontSize: 9, color: "#475569", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", width: "100%" }}>{agent.role}</p>
                </Link>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "32px 0" }}>
              <Sparkles style={{ width: 36, height: 36, color: "#1e293b", margin: "0 auto 10px" }} />
              <p style={{ fontSize: 12, color: "#475569" }}>You've tried all agents! Amazing.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InsightsPage;
