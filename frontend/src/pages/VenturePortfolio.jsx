import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Briefcase, TrendingUp, DollarSign, Target, ArrowUpRight, ArrowDownRight, Plus, BarChart3 } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

export default function VenturePortfolio() {
  const [ventures, setVentures] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", stage: "idea" });
  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = useCallback(async () => {
    const f = (url) => fetch(`${API}${url}`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null);
    const [v, s] = await Promise.all([f("/api/infinity/portfolio/ventures"), f("/api/infinity/portfolio/summary")]);
    if (v) setVentures(v);
    if (s) setSummary(s);
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const createVenture = async () => {
    await fetch(`${API}/api/infinity/portfolio/ventures`, { method: "POST", headers, body: JSON.stringify(form) });
    setShowCreate(false);
    setForm({ name: "", description: "", stage: "idea" });
    fetchData();
  };

  const stageColors = { idea: "bg-zinc-500/20 text-zinc-400", validation: "bg-blue-500/20 text-blue-400", mvp: "bg-cyan-500/20 text-cyan-400", growth: "bg-emerald-500/20 text-emerald-400", scale: "bg-violet-500/20 text-violet-400", mature: "bg-amber-500/20 text-amber-400", sunset: "bg-red-500/20 text-red-400" };
  const actionColors = { scale: "text-emerald-400", optimize: "text-cyan-400", pivot: "text-amber-400", pause: "text-orange-400", kill: "text-red-400" };

  return (
    <div className="space-y-6 max-w-6xl" data-testid="venture-portfolio-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2"><Briefcase className="w-6 h-6 text-violet-400" /> Venture Portfolio</h1>
          <p className="text-sm text-zinc-400">Portfolio state machine — track, score, and decide: scale / optimize / pivot / kill</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)} className="bg-violet-500 hover:bg-violet-600" data-testid="create-venture-btn"><Plus className="w-4 h-4 mr-1" /> New Venture</Button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3" data-testid="portfolio-summary">
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-4 text-center">
            <p className="text-lg font-bold text-white">{summary.total_ventures}</p><p className="text-[10px] text-zinc-500">Ventures</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-4 text-center">
            <p className="text-lg font-bold text-emerald-400">${(summary.total_revenue || 0).toLocaleString()}</p><p className="text-[10px] text-zinc-500">Revenue</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-4 text-center">
            <p className="text-lg font-bold text-red-400">${(summary.total_costs || 0).toLocaleString()}</p><p className="text-[10px] text-zinc-500">Costs</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-4 text-center">
            <p className="text-lg font-bold text-white">{(summary.avg_opportunity_score || 0).toFixed(0)}</p><p className="text-[10px] text-zinc-500">Avg Score</p>
          </CardContent></Card>
          <Card className="bg-zinc-900/50 border-white/5"><CardContent className="p-4 text-center">
            <p className="text-lg font-bold text-cyan-400">{(summary.avg_runway || 0).toFixed(0)}mo</p><p className="text-[10px] text-zinc-500">Avg Runway</p>
          </CardContent></Card>
        </div>
      )}

      {/* Create Form */}
      {showCreate && (
        <Card className="bg-zinc-900/50 border-violet-500/20" data-testid="create-venture-form">
          <CardContent className="p-4 space-y-3">
            <input className="w-full bg-zinc-800 border border-white/10 rounded px-3 py-2 text-sm text-white" placeholder="Venture name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} data-testid="venture-name-input" />
            <input className="w-full bg-zinc-800 border border-white/10 rounded px-3 py-2 text-sm text-white" placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} data-testid="venture-desc-input" />
            <div className="flex gap-2">
              <select className="bg-zinc-800 border border-white/10 rounded px-2 py-1 text-xs text-white" value={form.stage} onChange={e => setForm({...form, stage: e.target.value})} data-testid="venture-stage-select">
                {["idea","validation","mvp","growth","scale","mature","sunset"].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <Button onClick={createVenture} size="sm" className="bg-violet-500 hover:bg-violet-600" data-testid="submit-venture-btn">Create</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Ventures */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4" data-testid="ventures-grid">
        {ventures.map((v, i) => (
          <Card key={i} className="bg-zinc-900/50 border-white/5 hover:border-white/10 transition-all" data-testid={`venture-card-${i}`}>
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">{v.name}</h3>
                <Badge className={stageColors[v.stage] || ""}>{v.stage}</Badge>
              </div>
              <p className="text-xs text-zinc-400">{v.description}</p>
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-2 rounded bg-zinc-800/40">
                  <p className="text-sm font-bold text-emerald-400">${(v.revenue || 0).toLocaleString()}</p><p className="text-[10px] text-zinc-500">Revenue</p>
                </div>
                <div className="text-center p-2 rounded bg-zinc-800/40">
                  <p className="text-sm font-bold text-red-400">${(v.costs || 0).toLocaleString()}</p><p className="text-[10px] text-zinc-500">Costs</p>
                </div>
                <div className="text-center p-2 rounded bg-zinc-800/40">
                  <p className="text-sm font-bold text-white">{v.opportunity_score || 0}</p><p className="text-[10px] text-zinc-500">Score</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <Target className="w-3 h-3 text-zinc-500" />
                  <span className={`text-xs font-medium ${actionColors[v.next_action] || "text-zinc-400"}`}>
                    {v.next_action?.toUpperCase()}
                  </span>
                </div>
                <span className="text-[10px] text-zinc-500">Runway: {v.runway_months || 0}mo</span>
              </div>
            </CardContent>
          </Card>
        ))}
        {ventures.length === 0 && <p className="text-sm text-zinc-500 col-span-2 text-center py-8">No ventures yet. Create your first venture to get started.</p>}
      </div>
    </div>
  );
}
