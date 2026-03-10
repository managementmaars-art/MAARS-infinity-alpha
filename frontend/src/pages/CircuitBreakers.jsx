import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Activity, AlertTriangle, CheckCircle, XCircle, Clock, RotateCcw, Settings, Zap, Shield } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

const STATE_STYLES = {
  closed: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "Closed" },
  open: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20", label: "Open" },
  "half-open": { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", label: "Half-Open" },
};

export default function CircuitBreakers() {
  const { token } = useAuth();
  const [breakers, setBreakers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);

  const fetchBreakers = () => {
    fetch(`${API}/api/kernel/circuit-breakers/full`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setBreakers(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchBreakers(); }, [token]);

  const resetBreaker = async (breakerId) => {
    await fetch(`${API}/api/kernel/circuit-breakers/${breakerId}/reset`, {
      method: "POST", headers: { Authorization: `Bearer ${token}` },
    });
    fetchBreakers();
  };

  const updateBreaker = async (breakerId, data) => {
    await fetch(`${API}/api/kernel/circuit-breakers/${breakerId}`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    setEditing(null);
    fetchBreakers();
  };

  const closedCount = breakers.filter(b => b.state === "closed").length;
  const openCount = breakers.filter(b => b.state === "open").length;
  const halfOpenCount = breakers.filter(b => b.state === "half-open").length;

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="circuit-breakers-page">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Circuit Breakers</h1>
        <p className="text-sm text-zinc-400 mt-1">Monitor and configure service protection circuits across the MAARS ∞ infrastructure</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3" data-testid="cb-summary">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <div><p className="text-xl font-bold text-emerald-400">{closedCount}</p><p className="text-[10px] text-zinc-500">Closed (Healthy)</p></div>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 flex items-center gap-3">
          <XCircle className="w-5 h-5 text-red-400" />
          <div><p className="text-xl font-bold text-red-400">{openCount}</p><p className="text-[10px] text-zinc-500">Open (Tripped)</p></div>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <div><p className="text-xl font-bold text-amber-400">{halfOpenCount}</p><p className="text-[10px] text-zinc-500">Half-Open (Testing)</p></div>
        </div>
      </div>

      {/* Breaker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="cb-list">
        {breakers.map(cb => {
          const st = STATE_STYLES[cb.state] || STATE_STYLES.closed;
          const StIcon = st.icon;
          const isEditing = editing === cb.breaker_id;
          return (
            <div key={cb.breaker_id} className={`bg-zinc-900/40 border rounded-xl p-4 transition-colors ${st.border}`} data-testid={`cb-${cb.breaker_id}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className={`w-9 h-9 rounded-lg ${st.bg} flex items-center justify-center`}>
                    <StIcon className={`w-5 h-5 ${st.color}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{cb.name}</p>
                    <p className="text-[10px] text-zinc-500">{cb.description}</p>
                  </div>
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${st.bg} ${st.color}`}>{st.label}</span>
              </div>

              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-zinc-800/40 rounded-lg p-2 text-center">
                  <p className="text-[9px] text-zinc-500">Failures</p>
                  <p className="text-sm font-bold text-white">{cb.failures}<span className="text-zinc-600">/{cb.failure_threshold}</span></p>
                </div>
                <div className="bg-zinc-800/40 rounded-lg p-2 text-center">
                  <p className="text-[9px] text-zinc-500">Threshold</p>
                  <p className="text-sm font-bold text-white">{cb.failure_threshold}</p>
                </div>
                <div className="bg-zinc-800/40 rounded-lg p-2 text-center">
                  <p className="text-[9px] text-zinc-500">Reset</p>
                  <p className="text-sm font-bold text-white">{cb.reset_timeout_s}s</p>
                </div>
              </div>

              {isEditing ? (
                <div className="space-y-2 p-2 bg-zinc-800/30 rounded-lg" data-testid={`cb-edit-${cb.breaker_id}`}>
                  <div className="flex gap-2">
                    <label className="text-[10px] text-zinc-500 w-20">Threshold</label>
                    <input type="number" defaultValue={cb.failure_threshold} id={`thresh-${cb.breaker_id}`}
                      className="flex-1 bg-zinc-900 border border-white/10 rounded px-2 py-1 text-xs text-white" />
                  </div>
                  <div className="flex gap-2">
                    <label className="text-[10px] text-zinc-500 w-20">Reset (s)</label>
                    <input type="number" defaultValue={cb.reset_timeout_s} id={`reset-${cb.breaker_id}`}
                      className="flex-1 bg-zinc-900 border border-white/10 rounded px-2 py-1 text-xs text-white" />
                  </div>
                  <div className="flex gap-1.5 justify-end">
                    <Button size="sm" variant="ghost" className="h-7 text-[10px]" onClick={() => setEditing(null)}>Cancel</Button>
                    <Button size="sm" className="h-7 text-[10px] bg-indigo-600 hover:bg-indigo-700" onClick={() => {
                      const thresh = parseInt(document.getElementById(`thresh-${cb.breaker_id}`)?.value);
                      const reset = parseInt(document.getElementById(`reset-${cb.breaker_id}`)?.value);
                      updateBreaker(cb.breaker_id, { failure_threshold: thresh, reset_timeout_s: reset });
                    }}>Save</Button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-1.5">
                  <Button size="sm" variant="outline" className="h-7 text-[10px] flex-1 border-white/10 text-zinc-400" onClick={() => setEditing(cb.breaker_id)}>
                    <Settings className="w-3 h-3 mr-1" /> Configure
                  </Button>
                  {cb.state !== "closed" && (
                    <Button size="sm" className="h-7 text-[10px] bg-emerald-600 hover:bg-emerald-700" onClick={() => resetBreaker(cb.breaker_id)}
                      data-testid={`cb-reset-${cb.breaker_id}`}>
                      <RotateCcw className="w-3 h-3 mr-1" /> Reset
                    </Button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
