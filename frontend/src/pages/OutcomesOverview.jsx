/**
 * OutcomesOverview — the page a paying client sees on day 1.
 *
 * NO model internals. NO credit numbers. NO routing details.
 * Just the results the platform produced: leads moved, content
 * published, campaigns running, workflows firing, agents working.
 *
 * Reads /api/outcomes (one parallel-fanout call) and
 * /api/outcomes/activity for the recent stream.
 */
import { useEffect, useState } from "react";
import {
  TrendingUp, Mail, MessageSquare, Image as ImageIcon, Film,
  Users, Zap, Calendar, Activity, Clock, CheckCircle, AlertCircle,
  Target, Sparkles, Send
} from "lucide-react";
import { useAuth, API } from "../App";

const T = {
  glass:  "rgba(8,15,28,0.65)",
  border: "rgba(255,255,255,0.08)",
  teal:   "#4fd1c5",
  green:  "#34d399",
  violet: "#a78bfa",
  blue:   "#60a5fa",
  amber:  "#f59e0b",
  rose:   "#f87171",
  pink:   "#ec4899",
};

function authHeaders() {
  const t = localStorage.getItem("token");
  return t ? { Authorization: `Bearer ${t}` } : {};
}

function Card({ icon: Icon, label, value, sub, color = T.teal }) {
  return (
    <div style={{
      background: T.glass, border: `1px solid ${T.border}`,
      borderRadius: 14, padding: "18px 20px", minHeight: 92,
      display: "flex", flexDirection: "column", gap: 6,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10,
                    color: color, fontSize: 12, fontWeight: 600,
                    textTransform: "uppercase", letterSpacing: 1 }}>
        {Icon && <Icon size={16} />} {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: "#fff" }}>{value}</div>
      {sub != null && (
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)" }}>{sub}</div>
      )}
    </div>
  );
}

function UsageBar({ pct = 0, plan = "—", nearLimit = false }) {
  const color = nearLimit ? T.amber : T.green;
  return (
    <div style={{
      background: T.glass, border: `1px solid ${T.border}`,
      borderRadius: 14, padding: "18px 20px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", marginBottom: 10 }}>
        <div style={{ color: "#fff", fontWeight: 600 }}>
          This month on <span style={{ color: T.teal }}>{plan}</span>
        </div>
        <div style={{ color, fontWeight: 700 }}>{pct}% used</div>
      </div>
      <div style={{ height: 8, borderRadius: 999,
                    background: "rgba(255,255,255,0.08)", overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${Math.min(100, pct)}%`,
          background: color, borderRadius: 999,
          transition: "width 0.4s ease",
        }} />
      </div>
      {nearLimit && (
        <div style={{ marginTop: 8, fontSize: 12, color: T.amber,
                      display: "flex", alignItems: "center", gap: 6 }}>
          <AlertCircle size={14} /> Near limit — top-up or upgrade to avoid
          interruption.
        </div>
      )}
    </div>
  );
}

function ActivityItem({ item }) {
  const ts = item.ts ? new Date(item.ts).toLocaleString() : "";
  const line = (() => {
    switch (item.kind) {
      case "email_sent":
        return (<>
          <Mail size={14} style={{ color: T.teal }} />
          <span style={{ color: "#fff" }}>Email sent</span>
          <span style={{ color: "rgba(255,255,255,0.6)" }}>
            to {item.to} — "{(item.subject || "").slice(0, 60)}"
          </span>
        </>);
      case "post_published":
        return (<>
          <Send size={14} style={{ color: T.violet }} />
          <span style={{ color: "#fff" }}>
            Posted to {(item.platforms || []).join(", ")}
          </span>
          <span style={{ color: "rgba(255,255,255,0.6)" }}>
            — "{(item.preview || "").slice(0, 60)}"
          </span>
        </>);
      case "workflow_run":
        return (<>
          <Zap size={14} style={{
            color: item.status === "completed" ? T.green : T.rose,
          }} />
          <span style={{ color: "#fff" }}>
            Workflow {item.workflow_id} — {item.status}
          </span>
          <span style={{ color: "rgba(255,255,255,0.6)" }}>
            ({item.nodes_fired || 0} nodes)
          </span>
        </>);
      default:
        return <span style={{ color: "rgba(255,255,255,0.6)" }}>{item.kind}</span>;
    }
  })();
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 8, fontSize: 13,
      padding: "8px 0", borderBottom: `1px solid ${T.border}`,
    }}>
      {line}
      <span style={{ marginLeft: "auto", color: "rgba(255,255,255,0.4)",
                     fontSize: 11, whiteSpace: "nowrap" }}>
        {ts}
      </span>
    </div>
  );
}

export default function OutcomesOverview() {
  const { user } = useAuth() || {};
  const [overview, setOverview] = useState(null);
  const [activity, setActivity] = useState([]);
  const [capacity, setCapacity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    Promise.all([
      fetch(`${API}/outcomes`, { headers: authHeaders() }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/outcomes/activity?limit=20`, { headers: authHeaders() }).then(r => r.ok ? r.json() : { data: [] }),
      fetch(`${API}/outcomes/capacity`, { headers: authHeaders() }).then(r => r.ok ? r.json() : null),
    ]).then(([o, a, c]) => {
      if (!alive) return;
      setOverview(o);
      setActivity((a && a.data) || []);
      setCapacity(c);
      setLoading(false);
    }).catch((e) => {
      if (!alive) return;
      setErr(String(e).slice(0, 200));
      setLoading(false);
    });
    return () => { alive = false; };
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 40, color: "rgba(255,255,255,0.6)" }}>
        Loading your results…
      </div>
    );
  }
  if (err) {
    return (
      <div style={{ padding: 40, color: T.rose }}>
        Could not load outcomes: {err}
      </div>
    );
  }

  const p = overview?.pipeline || {};
  const c = overview?.content || {};
  const camp = overview?.campaigns || {};
  const wf = overview?.workflows || {};
  const tm = overview?.team || {};
  const us = overview?.usage || {};

  return (
    <div style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <div style={{ marginBottom: 8 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, color: "#fff", margin: 0 }}>
          Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""}.
        </h1>
        <p style={{ color: "rgba(255,255,255,0.55)", marginTop: 6, fontSize: 15 }}>
          Here's what your AI team accomplished this month.
        </p>
      </div>

      {/* Usage bar */}
      <div style={{ marginTop: 24 }}>
        <UsageBar pct={us.used_pct || 0} plan={us.plan_name || us.plan_id}
                  nearLimit={us.near_limit} />
      </div>

      {/* Pipeline */}
      <SectionHeader icon={Target} label="Pipeline" color={T.teal} />
      <Grid>
        <Card icon={Users}       label="Leads sourced" value={p.leads_sourced ?? 0} color={T.teal} />
        <Card icon={Mail}        label="Emails sent"   value={p.emails_sent ?? 0} color={T.teal} />
        <Card icon={MessageSquare} label="Replies"     value={p.replies ?? 0}
              sub={p.reply_rate_pct != null ? `${p.reply_rate_pct}% reply rate` : null}
              color={T.green} />
        <Card icon={Calendar}    label="Meetings"      value={p.meetings ?? 0} color={T.violet} />
      </Grid>

      {/* Content */}
      <SectionHeader icon={Sparkles} label="Content produced" color={T.violet} />
      <Grid>
        <Card icon={MessageSquare} label="Text pieces"  value={c.text_pieces ?? 0} color={T.violet} />
        <Card icon={Send}          label="Posts published" value={c.posts_published ?? 0}
              sub={c.posts_scheduled ? `+ ${c.posts_scheduled} scheduled` : null}
              color={T.pink} />
        <Card icon={ImageIcon}     label="Images" value={c.images_created ?? 0} color={T.blue} />
        <Card icon={Film}          label="Videos" value={c.videos_created ?? 0} color={T.amber} />
      </Grid>

      {/* Campaigns + Workflows + Team row */}
      <SectionHeader icon={TrendingUp} label="Running right now" color={T.green} />
      <Grid>
        <Card icon={Mail}  label="Email campaigns"
              value={camp.email_campaigns_active ?? 0}
              sub={`${camp.email_campaigns_paused ?? 0} paused · ${camp.email_campaigns_completed ?? 0} completed`}
              color={T.teal} />
        <Card icon={Send}  label="Social campaigns"
              value={camp.social_campaigns_active ?? 0} color={T.pink} />
        <Card icon={Zap}   label="Workflow runs"
              value={wf.runs_this_month ?? 0}
              sub={`${wf.success_rate_pct ?? 100}% success · ${wf.workflows_active ?? 0} active`}
              color={T.green} />
        <Card icon={Users} label="Agents"
              value={tm.agents_configured ?? 0}
              sub={tm.agents_working_now ? `${tm.agents_working_now} working now` : "idle"}
              color={T.violet} />
      </Grid>

      {/* Two-column: Activity + Capacity */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 20, marginTop: 32 }}>
        {/* Activity */}
        <div style={{
          background: T.glass, border: `1px solid ${T.border}`,
          borderRadius: 14, padding: 20,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8,
                        color: T.blue, fontSize: 12, fontWeight: 600,
                        textTransform: "uppercase", letterSpacing: 1,
                        marginBottom: 12 }}>
            <Activity size={16} /> Recent activity
          </div>
          {activity.length === 0 && (
            <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 13, padding: "12px 0" }}>
              No activity in the last 48 hours. Launch a campaign or post
              to get started.
            </div>
          )}
          {activity.map((item, i) => <ActivityItem key={i} item={item} />)}
        </div>

        {/* Capacity */}
        <div style={{
          background: T.glass, border: `1px solid ${T.border}`,
          borderRadius: 14, padding: 20,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8,
                        color: T.amber, fontSize: 12, fontWeight: 600,
                        textTransform: "uppercase", letterSpacing: 1,
                        marginBottom: 12 }}>
            <Clock size={16} /> What your plan can do
          </div>
          {capacity?.capacity_features && (
            <ul style={{ padding: 0, margin: 0, listStyle: "none" }}>
              {capacity.capacity_features.map((line, i) => (
                <li key={i} style={{
                  display: "flex", gap: 8, padding: "7px 0",
                  color: "rgba(255,255,255,0.82)", fontSize: 13,
                  borderBottom: `1px solid ${T.border}`,
                }}>
                  <CheckCircle size={14} style={{ color: T.green, flexShrink: 0, marginTop: 2 }} />
                  {line}
                </li>
              ))}
            </ul>
          )}
          {!capacity?.capacity_features && (
            <div style={{ color: "rgba(255,255,255,0.5)", fontSize: 13 }}>
              Plan capacity unavailable. Contact support if this persists.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, label, color }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      marginTop: 34, marginBottom: 14,
      color: color || "#fff", fontSize: 14, fontWeight: 600,
      textTransform: "uppercase", letterSpacing: 1,
    }}>
      {Icon && <Icon size={18} />} {label}
    </div>
  );
}

function Grid({ children }) {
  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
      gap: 14,
    }}>
      {children}
    </div>
  );
}
