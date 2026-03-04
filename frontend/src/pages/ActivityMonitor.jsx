import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Activity, Zap, ArrowRight, CheckCircle, Clock, AlertTriangle,
  Radio, Users, GitBranch, Terminal, RefreshCw, Wifi, WifiOff
} from "lucide-react";
import { Button } from "../components/ui/button";

const STATUS_DOT = {
  completed: "bg-emerald-400",
  in_progress: "bg-indigo-400 animate-pulse",
  pending: "bg-amber-400",
  failed: "bg-red-400",
};

const ActivityMonitor = () => {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [liveMode, setLiveMode] = useState(true);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}` };

  // Fallback: fetch via REST
  const fetchActivity = useCallback(async () => {
    try {
      const res = await fetch(`${API}/activity/live`, { headers });
      if (res.ok) setData(await res.json());
    } catch {} finally { setLoading(false); }
  }, [token]);

  // WebSocket connection
  const connectWs = useCallback(() => {
    if (!token || !liveMode) return;

    // Build WS URL from API URL
    const apiUrl = API.replace(/\/api$/, "");
    const wsProtocol = apiUrl.startsWith("https") ? "wss" : "ws";
    const wsHost = apiUrl.replace(/^https?:\/\//, "");
    const wsUrl = `${wsProtocol}://${wsHost}/api/ws/activity?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        setLoading(false);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "pong") return;
          if (msg.type === "snapshot" || msg.agent_activity) {
            setData(msg);
            setLoading(false);
          }
        } catch {}
      };

      ws.onclose = () => {
        setWsConnected(false);
        wsRef.current = null;
        // Reconnect after 3 seconds
        if (liveMode) {
          reconnectRef.current = setTimeout(connectWs, 3000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // Fallback to polling
      setWsConnected(false);
      fetchActivity();
    }
  }, [token, liveMode]);

  useEffect(() => {
    if (liveMode) {
      connectWs();
    } else {
      // Disconnect WS and use polling
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      fetchActivity();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
      }
    };
  }, [liveMode, connectWs, fetchActivity]);

  // Polling fallback when WS is not connected
  useEffect(() => {
    if (wsConnected || !liveMode) return;
    const interval = setInterval(fetchActivity, 10000);
    return () => clearInterval(interval);
  }, [wsConnected, liveMode, fetchActivity]);

  // Initial REST fetch as fallback
  useEffect(() => {
    fetchActivity();
  }, []);

  const handleRefresh = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send("refresh");
    } else {
      fetchActivity();
    }
  };

  if (loading) return <div className="flex items-center justify-center py-20"><div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" /></div>;

  const agents = data?.agent_activity || [];
  const flows = data?.communication_flows || [];
  const tasks = data?.task_graph || [];
  const tools = data?.recent_tool_calls || [];

  return (
    <div className="space-y-6" data-testid="activity-monitor">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
            <Radio className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white font-['Outfit']">Agent Activity Monitor</h1>
            <p className="text-xs text-zinc-500">Real-time agent execution, communication flows & task dependencies</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Connection status */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900/50 border border-white/5" data-testid="ws-status">
            {wsConnected ? (
              <>
                <Wifi className="w-3 h-3 text-emerald-400" />
                <span className="text-[10px] text-emerald-400 font-medium">WebSocket Live</span>
              </>
            ) : liveMode ? (
              <>
                <WifiOff className="w-3 h-3 text-amber-400" />
                <span className="text-[10px] text-amber-400">Polling (10s)</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3 text-zinc-500" />
                <span className="text-[10px] text-zinc-500">Paused</span>
              </>
            )}
          </div>
          <Button size="sm" variant={liveMode ? "default" : "ghost"} onClick={() => setLiveMode(!liveMode)} className={liveMode ? "bg-emerald-600 hover:bg-emerald-700 text-white text-xs" : "text-zinc-400 text-xs"} data-testid="toggle-live">
            {liveMode ? "Live" : "Paused"}
          </Button>
          <Button size="sm" variant="ghost" onClick={handleRefresh} className="text-zinc-400" data-testid="refresh-btn">
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Active Projects */}
      {data?.active_projects?.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-2 uppercase tracking-wider flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />Active Projects
          </h2>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {data.active_projects.map(p => (
              <Card key={p.project_id} className="bg-amber-500/5 border-amber-500/20 shrink-0 w-64">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                    <p className="text-xs font-medium text-white truncate">{p.title || "Untitled"}</p>
                  </div>
                  <p className="text-[10px] text-zinc-500 truncate">{p.goal?.substring(0, 80)}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Agent Activity Grid */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <Users className="w-3.5 h-3.5 text-indigo-400" />Agent Workforce Status
          <Badge variant="outline" className="border-white/10 text-zinc-500 text-[9px] ml-auto">{agents.length} active</Badge>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
          {agents.slice(0, 20).map((a, i) => (
            <div key={i} className="bg-zinc-900/50 border border-white/5 rounded-lg p-3 hover:border-white/10 transition-all">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2 h-2 rounded-full ${a.completed === a.task_count ? "bg-emerald-400" : "bg-indigo-400 animate-pulse"}`} />
                <p className="text-xs font-medium text-white truncate">{a.agent}</p>
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-zinc-500">{a.completed}/{a.task_count} tasks</span>
                <div className="w-16 h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(a.completed / Math.max(a.task_count, 1)) * 100}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Communication Flows */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <ArrowRight className="w-3.5 h-3.5 text-violet-400" />Inter-Agent Communication Flows
        </h2>
        {flows.length > 0 ? (
          <div className="space-y-2">
            {flows.slice(0, 12).map((f, i) => (
              <div key={i} className="flex items-center gap-3 bg-zinc-900/30 border border-white/5 rounded-lg px-4 py-2.5">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs font-medium text-indigo-400 shrink-0">{f.from}</span>
                  <ArrowRight className="w-3 h-3 text-zinc-600 shrink-0" />
                  <span className="text-xs font-medium text-violet-400 shrink-0">{f.to}</span>
                </div>
                <span className="text-[10px] text-zinc-500 truncate flex-1">{f.objective}</span>
                <div className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT[f.status] || STATUS_DOT.pending}`} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border border-dashed border-white/10 rounded-xl">
            <ArrowRight className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
            <p className="text-xs text-zinc-500">No communication flows yet. Run a project to see agent collaboration.</p>
          </div>
        )}
      </div>

      {/* Task Dependency Graph */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <GitBranch className="w-3.5 h-3.5 text-cyan-400" />Task Dependency Graph
        </h2>
        {tasks.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {tasks.slice(0, 15).map((t, i) => (
              <div key={i} className="bg-zinc-900/50 border border-white/5 rounded-lg p-3 flex items-start gap-2">
                <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${STATUS_DOT[t.status] || STATUS_DOT.pending}`} />
                <div className="min-w-0">
                  <p className="text-xs text-white truncate">{t.title}</p>
                  <p className="text-[10px] text-zinc-500">{t.agent}</p>
                </div>
                <Badge variant="outline" className={`shrink-0 text-[8px] ml-auto ${
                  t.status === "completed" ? "border-emerald-500/30 text-emerald-400" :
                  t.status === "in_progress" ? "border-indigo-500/30 text-indigo-400" :
                  "border-white/10 text-zinc-500"
                }`}>{t.status}</Badge>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border border-dashed border-white/10 rounded-xl">
            <GitBranch className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
            <p className="text-xs text-zinc-500">No tasks in the dependency graph yet.</p>
          </div>
        )}
      </div>

      {/* Recent Tool Calls */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-amber-400" />Recent Tool Executions
        </h2>
        {tools.length > 0 ? (
          <div className="space-y-1.5">
            {tools.slice(0, 10).map((t, i) => (
              <div key={i} className="flex items-center gap-3 text-xs bg-zinc-900/30 rounded-lg px-3 py-2">
                <div className={`w-1.5 h-1.5 rounded-full ${t.status === "success" ? "bg-emerald-400" : "bg-red-400"}`} />
                <span className="text-indigo-400 font-mono w-28 truncate">{t.tool_name}</span>
                <span className="text-zinc-500 truncate flex-1">{t.agent_name}</span>
                <span className="text-[10px] text-zinc-600 shrink-0">{t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : ""}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-zinc-500 text-center py-4">No recent tool calls</p>
        )}
      </div>
    </div>
  );
};

export default ActivityMonitor;
