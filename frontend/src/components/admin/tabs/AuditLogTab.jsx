import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { ScrollText, Shield, Loader2 } from "lucide-react";
import { API, useAuth } from "../../../App";

export const AuditLogTab = () => {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/admin/audit-log?limit=100`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setLogs(await res.json());
    } catch {} finally {
      setLoading(false);
    }
  };

  const formatTime = (ts) => {
    if (!ts) return "";
    const d = new Date(ts);
    return d.toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  const actionColors = {
    pricing_update: "bg-amber-500/15 text-amber-400",
    user_update: "bg-blue-500/15 text-blue-400",
    agent_update: "bg-violet-500/15 text-violet-400",
    api_key_update: "bg-emerald-500/15 text-emerald-400",
    branding_update: "bg-pink-500/15 text-pink-400",
    smtp_update: "bg-cyan-500/15 text-cyan-400",
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <div data-testid="audit-log-tab">
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader className="pb-3">
          <CardTitle className="text-white font-['Outfit'] text-base flex items-center gap-2">
            <ScrollText className="w-4 h-4 text-indigo-400" />
            Admin Audit Log
            <Badge variant="outline" className="ml-2 text-zinc-400 border-white/10">{logs.length} entries</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
              <p className="text-zinc-500 text-sm">No admin actions recorded yet.</p>
              <p className="text-zinc-600 text-xs mt-1">Actions like pricing changes, user updates, and key modifications will appear here.</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {logs.map((log, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-zinc-800/30 border border-white/5 hover:border-white/10 transition-colors" data-testid={`audit-entry-${i}`}>
                  <div className="w-2 h-2 mt-2 rounded-full bg-red-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${actionColors[log.action] || "bg-zinc-700/50 text-zinc-400"}`}>
                        {log.action?.replace(/_/g, " ")}
                      </span>
                      <span className="text-[10px] text-zinc-600">{formatTime(log.created_at)}</span>
                    </div>
                    <p className="text-xs text-zinc-400">{log.admin_email}</p>
                    {log.details && Object.keys(log.details).length > 0 && (
                      <p className="text-[11px] text-zinc-600 mt-1 truncate">
                        {JSON.stringify(log.details).slice(0, 120)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
