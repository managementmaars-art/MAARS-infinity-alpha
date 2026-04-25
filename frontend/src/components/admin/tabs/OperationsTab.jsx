import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import {
  Activity, Mail, Users as UsersIcon, Webhook, Ban, PlayCircle, PauseCircle,
  CheckCircle2, AlertTriangle, XCircle, Target, Clock, RefreshCw,
} from "lucide-react";
import { API } from "../../../App";

/* ────────────────────────────────────────────────────────────────────
   Admin Operations tab — visual control plane for every outbound
   surface:
     - Scheduler health (is the 30s poller alive? queue depths?)
     - Campaigns (running, paused, completed) with inline pause/resume
     - Email event stats (delivered / bounced / opened / complained)
     - Webhook subscriptions (customer-facing)
     - Product readiness (which integrations are keyed vs pending)
   Each section hits a backend endpoint that already exists — this is
   just the operator-facing skin.
──────────────────────────────────────────────────────────────────── */

const SectionCard = ({ icon: Icon, title, accent, badge, children }) => (
  <Card className="bg-zinc-900/50 border-white/10">
    <CardHeader>
      <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg bg-${accent}-500/20 flex items-center justify-center`}>
          <Icon className={`w-4 h-4 text-${accent}-400`} />
        </div>
        {title}
        {badge}
      </CardTitle>
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

const StatusPill = ({ status }) => {
  const map = {
    scheduled:  { cls: "bg-amber-500/20 text-amber-400", label: "scheduled" },
    processing: { cls: "bg-indigo-500/20 text-indigo-400", label: "processing" },
    sent:       { cls: "bg-emerald-500/20 text-emerald-400", label: "sent" },
    published:  { cls: "bg-emerald-500/20 text-emerald-400", label: "published" },
    initiated:  { cls: "bg-emerald-500/20 text-emerald-400", label: "initiated" },
    failed:     { cls: "bg-red-500/20 text-red-400", label: "failed" },
    paused:     { cls: "bg-zinc-500/20 text-zinc-400", label: "paused" },
    running:    { cls: "bg-emerald-500/20 text-emerald-400", label: "running" },
    live:       { cls: "bg-emerald-500/20 text-emerald-400", label: "live" },
    needs_config:{cls: "bg-amber-500/20 text-amber-400", label: "needs config" },
    partial:    { cls: "bg-amber-500/20 text-amber-400", label: "partial" },
    vapor:      { cls: "bg-zinc-500/20 text-zinc-500", label: "not wired" },
  };
  const m = map[status] || { cls: "bg-zinc-700/40 text-zinc-400", label: status };
  return <Badge className={`text-[10px] ${m.cls}`}>{m.label}</Badge>;
};

export const OperationsTab = ({ token }) => {
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const [scheduler, setScheduler] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [emailStats, setEmailStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      setLoading(true);
      const endpoints = [
        [`${API}/admin/scheduler/status`, setScheduler],
        [`${API}/campaigns`, (d) => setCampaigns(d?.data || [])],
        [`${API}/admin/product-readiness`, setReadiness],
        [`${API}/email-events/stats`, setEmailStats],
      ];
      await Promise.all(endpoints.map(async ([url, set]) => {
        try {
          const r = await fetch(url, { headers });
          if (!r.ok) return;
          const data = await r.json();
          if (alive) set(data);
        } catch { /* silent */ }
      }));
      if (alive) setLoading(false);
    };
    load();
    const t = setInterval(() => setRefreshTick((n) => n + 1), 30_000);
    return () => { alive = false; clearInterval(t); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, refreshTick]);

  const toggleCampaign = async (c) => {
    const paused = c.status === "paused";
    const url = `${API}/campaigns/${c.campaign_id}/${paused ? "resume" : "pause"}`;
    try {
      await fetch(url, { method: "POST", headers });
      setRefreshTick((n) => n + 1);
    } catch { /* ignore */ }
  };

  if (loading && !scheduler) {
    return <div className="text-zinc-500 text-sm">Loading operations…</div>;
  }

  // Aggregate queue counts
  const queueTotal = (key) =>
    Object.values(scheduler?.queues || {}).reduce((n, q) => n + (q[key] || 0), 0);

  return (
    <div className="space-y-6">

      {/* ── Scheduler health ────────────────────────────────────── */}
      <SectionCard
        icon={Activity}
        title="Background Scheduler"
        accent="emerald"
        badge={<Badge className={`text-[10px] ${scheduler?.running ? "bg-emerald-500/20 text-emerald-400 animate-pulse" : "bg-red-500/20 text-red-400"}`}>
          {scheduler?.running ? "running" : "stopped"}
        </Badge>}
      >
        <p className="text-[11px] text-zinc-500 mb-3 leading-relaxed">
          30-second poller fires scheduled posts, cold emails, and calls at their `scheduled_at` time. If this stops, nothing automated runs. Restart the backend to re-arm.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            ["Scheduled", queueTotal("scheduled"), "amber"],
            ["Processing", queueTotal("processing"), "indigo"],
            ["Sent / Published", queueTotal("sent"), "emerald"],
            ["Failed", queueTotal("failed"), "red"],
          ].map(([label, n, color]) => (
            <div key={label} className={`p-3 rounded-lg bg-${color}-500/10 border border-${color}-500/20`}>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wide">{label}</p>
              <p className={`text-2xl font-bold text-${color}-400 font-mono`}>{n}</p>
            </div>
          ))}
        </div>
        {scheduler?.jobs?.[0]?.next_run_time && (
          <p className="text-[10px] text-zinc-600 mt-3 flex items-center gap-1.5">
            <Clock className="w-3 h-3" />
            Next tick: {new Date(scheduler.jobs[0].next_run_time).toLocaleTimeString()}
          </p>
        )}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
          {Object.entries(scheduler?.queues || {}).map(([coll, q]) => (
            <div key={coll} className="p-2 rounded-md bg-white/5 border border-white/5">
              <p className="text-[10px] text-zinc-500 font-mono">{coll}</p>
              <p className="text-xs text-zinc-300 mt-0.5">
                {q.scheduled} ⏳ · {q.sent} ✓ · {q.failed} ✗
              </p>
            </div>
          ))}
        </div>
      </SectionCard>

      {/* ── Active campaigns ────────────────────────────────────── */}
      <SectionCard
        icon={Mail}
        title="Outbound Campaigns"
        accent="indigo"
        badge={<Badge className="bg-indigo-500/20 text-indigo-400 text-[10px]">{campaigns.length} total</Badge>}
      >
        {campaigns.length === 0 ? (
          <p className="text-zinc-500 text-sm">No campaigns yet. Start one via the Campaigns section or agent chat ("run a cold-email campaign for SaaS founders").</p>
        ) : (
          <div className="space-y-2">
            {campaigns.slice(0, 12).map((c) => (
              <div key={c.campaign_id} className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <p className="text-sm text-white font-medium truncate">{c.name}</p>
                    <StatusPill status={c.status} />
                  </div>
                  <p className="text-[10px] text-zinc-500 font-mono">
                    {c.scheduled_count || 0} scheduled · first {c.first_send_at ? new Date(c.first_send_at).toLocaleString() : "—"} · last {c.last_send_at ? new Date(c.last_send_at).toLocaleString() : "—"}
                  </p>
                </div>
                {["scheduled", "drafting", "paused"].includes(c.status) && (
                  <Button
                    size="sm" variant="outline"
                    className="border-white/10 text-zinc-300 hover:bg-white/5 text-xs"
                    onClick={() => toggleCampaign(c)}
                  >
                    {c.status === "paused" ? <><PlayCircle className="w-3 h-3 mr-1" /> Resume</> : <><PauseCircle className="w-3 h-3 mr-1" /> Pause</>}
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      {/* ── Email deliverability ────────────────────────────────── */}
      <SectionCard
        icon={CheckCircle2}
        title="Email Deliverability"
        accent="teal"
        badge={<Badge className="bg-teal-500/20 text-teal-400 text-[10px]">last 30 days</Badge>}
      >
        <p className="text-[11px] text-zinc-500 mb-3 leading-relaxed">
          Counts from provider webhooks (SendGrid/Resend). Auto-suppression fires on bounces + spam complaints to protect your domain reputation.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {[
            ["delivered", CheckCircle2, "emerald"],
            ["opened", Activity, "indigo"],
            ["clicked", Target, "violet"],
            ["bounced", XCircle, "red"],
            ["complained", AlertTriangle, "amber"],
          ].map(([ev, Icon, color]) => {
            const n = emailStats?.counts?.[ev] ?? emailStats?.counts?.[ev.replace("ed","")] ?? 0;
            return (
              <div key={ev} className={`p-3 rounded-lg bg-${color}-500/5 border border-${color}-500/15`}>
                <div className="flex items-center gap-1.5 mb-1">
                  <Icon className={`w-3 h-3 text-${color}-400`} />
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wide">{ev}</p>
                </div>
                <p className={`text-xl font-bold text-${color}-400 font-mono`}>{n}</p>
              </div>
            );
          })}
        </div>
      </SectionCard>

      {/* ── Product readiness ───────────────────────────────────── */}
      {readiness && (
        <SectionCard
          icon={Webhook}
          title="Product Readiness"
          accent="violet"
          badge={<Badge className="bg-violet-500/20 text-violet-400 text-[10px]">
            {readiness.summary?.live}/{readiness.summary?.total} live
          </Badge>}
        >
          <p className="text-[11px] text-zinc-500 mb-3 leading-relaxed">
            Every capability the platform offers and whether it's ready to ship. Operators fix <strong className="text-amber-400">needs_config</strong> items first (fastest revenue unlocks).
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {(readiness.features || []).map((f, i) => (
              <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/5">
                <div className="flex items-center justify-between gap-2 mb-1 flex-wrap">
                  <p className="text-sm text-white font-medium">{f.capability}</p>
                  <StatusPill status={f.status} />
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed">{f.notes}</p>
                {f.setup_url && (
                  <a
                    href={f.setup_url}
                    target="_blank" rel="noreferrer"
                    className="text-[10px] text-indigo-400 hover:text-indigo-300 mt-1 inline-block"
                  >
                    Set up →
                  </a>
                )}
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* ── Refresh ────────────────────────────────────────────── */}
      <div className="flex justify-end">
        <Button
          size="sm" variant="outline"
          className="border-white/10 text-zinc-400 hover:bg-white/5 text-xs"
          onClick={() => setRefreshTick((n) => n + 1)}
        >
          <RefreshCw className="w-3 h-3 mr-1.5" /> Refresh
        </Button>
      </div>
    </div>
  );
};
