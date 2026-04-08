import { useState, useEffect } from "react";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { TrendingUp } from "lucide-react";
import { useAuth, API } from "../../App";
import { toast } from "sonner";

const CustomPackagesTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const [config, setConfig] = useState(null);
  const [extraPacks, setExtraPacks] = useState(null);
  const [avgCost, setAvgCost] = useState(0.003);
  const [saving, setSaving] = useState(false);
  const [targetMargin, setTargetMargin] = useState(200);
  const [bdtRate, setBdtRate] = useState(107);

  useEffect(() => {
    fetchConfig();
  }, []);

  useEffect(() => {
    const fetchAvgCost = async () => {
      try {
        const res = await fetch(`${API}/admin/avg-cost`, { headers });
        if (res.ok) { const d = await res.json(); if (d.avg_cost_per_credit > 0) setAvgCost(d.avg_cost_per_credit); }
      } catch {}
    };
    const interval = setInterval(fetchAvgCost, 15000);
    return () => clearInterval(interval);
  }, [token]);

  const fetchConfig = async () => {
    try {
      const [res1, res2, res3, res4] = await Promise.all([
        fetch(`${API}/admin/custom-package`, { headers }),
        fetch(`${API}/admin/credit-packages`, { headers }),
        fetch(`${API}/admin/avg-cost`, { headers }),
        fetch(`${API}/exchange-rate`),
      ]);
      if (res1.ok) setConfig(await res1.json());
      if (res2.ok) { const d = await res2.json(); setExtraPacks(d.packages || []); }
      if (res3.ok) { const d = await res3.json(); if (d.avg_cost_per_credit > 0) setAvgCost(d.avg_cost_per_credit); }
      if (res4.ok) { const d = await res4.json(); if (d.usd_bdt > 0) setBdtRate(d.usd_bdt); }
    } catch {}
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const [r1, r2] = await Promise.all([
        fetch(`${API}/admin/custom-package`, {
          method: "POST", headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify(config)
        }),
        fetch(`${API}/admin/credit-packages`, {
          method: "POST", headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({ packages: extraPacks })
        }),
      ]);
      if (r1.ok && r2.ok) {
        toast.success("All pricing saved!");
        fetchConfig();
      } else toast.error("Failed to save");
    } catch { toast.error("Failed to save"); }
    finally { setSaving(false); }
  };

  const updatePreset = (index, field, value) => {
    setConfig(prev => {
      const presets = [...(prev.credit_presets || [])];
      presets[index] = { ...presets[index], [field]: parseFloat(value) || 0 };
      if (field === "price_usd") {
        presets[index].price_bdt = Math.round((parseFloat(value) || 0) * bdtRate);
      }
      return { ...prev, credit_presets: presets };
    });
  };

  const updateExtraPack = (index, field, value) => {
    setExtraPacks(prev => {
      const packs = [...prev];
      packs[index] = { ...packs[index], [field]: field === "name" ? value : (parseFloat(value) || 0) };
      if (field === "price_usd") {
        packs[index].price_bdt = Math.round((parseFloat(value) || 0) * bdtRate);
      }
      return packs;
    });
  };

  const applyMarginToAll = () => {
    const mult = 1 + (targetMargin / 100);
    if (config?.credit_presets) {
      setConfig(prev => ({
        ...prev,
        credit_presets: prev.credit_presets.map(p => {
          const cost = p.credits * avgCost;
          const usd = Math.round(cost * mult * 100) / 100;
          return { ...p, price_usd: usd, price_bdt: Math.round(usd * bdtRate) };
        })
      }));
    }
    if (extraPacks) {
      setExtraPacks(prev => prev.map(p => {
        const cost = p.credits * avgCost;
        const usd = Math.round(cost * mult * 100) / 100;
        return { ...p, price_usd: usd, price_bdt: Math.round(usd * bdtRate) };
      }));
    }
    if (config) {
      setConfig(prev => ({
        ...prev,
        per_agent_price_bdt: Math.round(prev.per_agent_price_usd * bdtRate),
        commander_addon_price_bdt: Math.round(prev.commander_addon_price_usd * bdtRate),
      }));
    }
    toast.success(`Applied ${targetMargin}% margin & synced BDT at rate ${bdtRate}`);
  };

  const syncAllBdt = (newRate) => {
    setBdtRate(newRate);
    if (config) {
      setConfig(prev => ({
        ...prev,
        per_agent_price_bdt: Math.round(prev.per_agent_price_usd * newRate),
        commander_addon_price_bdt: Math.round(prev.commander_addon_price_usd * newRate),
        credit_presets: (prev.credit_presets || []).map(p => ({ ...p, price_bdt: Math.round(p.price_usd * newRate) })),
      }));
    }
    if (extraPacks) {
      setExtraPacks(prev => prev.map(p => ({ ...p, price_bdt: Math.round(p.price_usd * newRate) })));
    }
  };

  if (!config || !extraPacks) return <div className="text-zinc-400 p-8">Loading...</div>;

  const marginMult = 1 + (targetMargin / 100);

  return (
    <div className="space-y-6" data-testid="custom-packages-tab">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white font-['Outfit']">Custom Package Pricing</h2>
          <p className="text-zinc-400 text-sm mt-1">Set prices for agents, credits, and extra credit packs with real-time cost and profit visibility.</p>
        </div>
      </div>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-violet-400" />
            </div>
            Credit & Package Margin Calculator
            <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px] ml-2">LIVE SYNC</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Set your target margin and apply it to all credit pricing, or manually edit individual prices below.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1">
              <Label className="text-zinc-300 text-sm">AI Cost per Credit (USD)</Label>
              <div className="flex items-center h-10 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-amber-400 font-mono font-bold"
                data-testid="pkg-calc-cost">
                ${avgCost.toFixed(6)}
              </div>
              <p className="text-[10px] text-emerald-500/70 flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live from real usage</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-300 text-sm">Target Profit Margin (%)</Label>
              <Input type="number" value={targetMargin}
                onChange={e => setTargetMargin(parseInt(e.target.value) || 0)}
                className="bg-zinc-800/50 border-white/10" data-testid="pkg-calc-margin" />
              <p className="text-[10px] text-zinc-500">{targetMargin}% means {marginMult.toFixed(1)}x the cost</p>
            </div>
            <div className="space-y-1">
              <Label className="text-zinc-300 text-sm">BDT Exchange Rate</Label>
              <div className="flex gap-2">
                <Input type="number" value={bdtRate}
                  onChange={e => syncAllBdt(parseFloat(e.target.value) || 0)}
                  className="bg-zinc-800/50 border-white/10 flex-1" data-testid="pkg-calc-bdt" />
                <Button variant="outline" size="sm" className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs whitespace-nowrap"
                  data-testid="pkg-refresh-rate-btn"
                  onClick={async () => {
                    try {
                      const res = await fetch(`${API}/exchange-rate`);
                      if (res.ok) { const d = await res.json(); syncAllBdt(d.usd_bdt); toast.success(`Rate updated: 1 USD = ${d.usd_bdt} BDT`); }
                    } catch { toast.error("Failed to fetch rate"); }
                  }}>
                  Refresh Live
                </Button>
              </div>
              <p className="text-[10px] text-emerald-500/70">Live rate: 1 USD = {bdtRate} BDT (auto-syncs all BDT prices)</p>
            </div>
          </div>
          <Button onClick={applyMarginToAll}
            className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
            data-testid="apply-margin-all-btn">
            Apply {targetMargin}% Margin to All Credits & Packs
          </Button>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white text-base flex items-center gap-2">Agent & Commander Pricing <span className="text-xs text-zinc-500">(Build Your Own)</span></CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Per Agent (USD)</label>
            <input type="number" step="0.5" value={config.per_agent_price_usd || 0}
              onChange={e => { const v = parseFloat(e.target.value) || 0; setConfig(p => ({...p, per_agent_price_usd: v, per_agent_price_bdt: Math.round(v * bdtRate)})); }}
              className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
              data-testid="per-agent-usd" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Per Agent (BDT) <span className="text-emerald-500/70 text-[10px]">auto</span></label>
            <input type="number" value={config.per_agent_price_bdt || 0} readOnly
              className="w-full bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-zinc-400 text-sm cursor-not-allowed"
              data-testid="per-agent-bdt" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Commander Add-on (USD)</label>
            <input type="number" step="0.5" value={config.commander_addon_price_usd || 0}
              onChange={e => { const v = parseFloat(e.target.value) || 0; setConfig(p => ({...p, commander_addon_price_usd: v, commander_addon_price_bdt: Math.round(v * bdtRate)})); }}
              className="w-full bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
              data-testid="commander-price-usd" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-zinc-400">Commander Add-on (BDT) <span className="text-emerald-500/70 text-[10px]">auto</span></label>
            <input type="number" value={config.commander_addon_price_bdt || 0} readOnly
              className="w-full bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-zinc-400 text-sm cursor-not-allowed"
              data-testid="commander-price-bdt" />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white text-base flex items-center gap-2">Credit Presets <span className="text-xs text-zinc-500">(Build Your Own package)</span></CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="grid grid-cols-7 gap-2 text-xs text-zinc-500 font-medium px-1">
              <span>Credits</span><span>AI Cost</span><span>USD Price</span><span>BDT <span className="text-emerald-500/70">(auto)</span></span><span>Profit</span><span>Margin</span><span></span>
            </div>
            {(config.credit_presets || []).map((preset, i) => {
              const cost = preset.credits * avgCost;
              const profit = preset.price_usd - cost;
              const margin = cost > 0 ? ((profit / cost) * 100).toFixed(0) : 0;
              return (
              <div key={preset.id || i} className="grid grid-cols-7 gap-2 items-center">
                <input type="number" value={preset.credits}
                  onChange={e => updatePreset(i, "credits", e.target.value)}
                  className="bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" />
                <span className="text-red-400 text-sm px-1">${cost.toFixed(2)}</span>
                <input type="number" step="0.5" value={preset.price_usd}
                  onChange={e => updatePreset(i, "price_usd", e.target.value)}
                  className="bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" />
                <span className="text-zinc-400 text-sm px-1">{preset.price_bdt}</span>
                <span className="text-amber-400 text-sm px-1">${profit.toFixed(2)}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${profit > 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>
                  {profit > 0 ? "+" : ""}{margin}%
                </span>
                <button onClick={() => setConfig(p => ({...p, credit_presets: p.credit_presets.filter((_, idx) => idx !== i)}))}
                  className="text-red-400 hover:text-red-300 text-xs">Remove</button>
              </div>
              );
            })}
            <Button variant="outline" size="sm" className="border-white/10 text-zinc-400"
              onClick={() => setConfig(p => ({...p, credit_presets: [...(p.credit_presets||[]), {id:`cp_new_${Date.now()}`, credits:0, price_usd:0, price_bdt:0}]}))}>
              + Add Preset
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white text-base flex items-center gap-2">Extra Credit Packs <span className="text-xs text-zinc-500">("Need More Credits?" section)</span></CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="grid grid-cols-8 gap-2 text-xs text-zinc-500 font-medium px-1">
              <span>Credits</span><span>AI Cost/Credit</span><span>AI Cost</span><span>USD Price</span><span>BDT <span className="text-emerald-500/70">(auto)</span></span><span>Profit</span><span>Margin</span><span></span>
            </div>
            {extraPacks.map((pack, i) => {
              const cost = pack.credits * avgCost;
              const profit = pack.price_usd - cost;
              const margin = cost > 0 ? ((profit / cost) * 100).toFixed(0) : 0;
              return (
              <div key={pack.id || i} className="grid grid-cols-8 gap-2 items-center" data-testid={`extra-pack-${i}`}>
                <input type="number" value={pack.credits}
                  onChange={e => updateExtraPack(i, "credits", e.target.value)}
                  className="bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" />
                <div className="bg-zinc-800/80 border border-white/5 rounded-lg px-3 py-2 text-amber-400 text-sm font-mono"
                  data-testid={`ai-cost-credit-pack-${i}`}>
                  ${avgCost.toFixed(6)}
                </div>
                <span className="text-red-400 text-sm px-1">${cost.toFixed(2)}</span>
                <input type="number" step="0.5" value={pack.price_usd}
                  onChange={e => updateExtraPack(i, "price_usd", e.target.value)}
                  className="bg-zinc-800 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" />
                <span className="text-zinc-400 text-sm px-1">{pack.price_bdt}</span>
                <span className="text-amber-400 text-sm px-1">${profit.toFixed(2)}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${profit > 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>
                  {profit > 0 ? "+" : ""}{margin}%
                </span>
                <button onClick={() => setExtraPacks(prev => prev.filter((_, idx) => idx !== i))}
                  className="text-red-400 hover:text-red-300 text-xs">Remove</button>
              </div>
              );
            })}
            <Button variant="outline" size="sm" className="border-white/10 text-zinc-400"
              onClick={() => setExtraPacks(prev => [...prev, {id:`credits_new_${Date.now()}`, credits:0, price_usd:0, price_bdt:0, name:"New Pack"}])}>
              + Add Pack
            </Button>
          </div>
        </CardContent>
      </Card>

      <Button onClick={handleSave} disabled={saving}
        className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 w-full"
        data-testid="save-custom-config-btn">
        {saving ? "Saving..." : "Save All Pricing"}
      </Button>
    </div>
  );
};

export default CustomPackagesTab;
