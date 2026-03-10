import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";
import { Label } from "../../ui/label";
import { TrendingUp, CheckCircle, Trash2, Plus, X } from "lucide-react";
import { API } from "../../../App";
import { toast } from "sonner";

export const PricingManagerTab = ({ pricingConfig, setPricingConfig, pricingEdit, setPricingEdit, calcInputs, setCalcInputs, calcResult, setCalcResult, liveCost, token, onDeletePlan, onRefresh }) => {
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};

  const handleCalculate = async () => {
    try {
      const res = await fetch(`${API}/admin/pricing/calculate`, {
        method: "POST",
        headers,
        body: JSON.stringify(calcInputs)
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
        // Auto-apply calculated prices to the editor
        if (pricingEdit) {
          const updated = { ...pricingEdit };
          for (const [planId, calc] of Object.entries(data.plan_calculations)) {
            if (updated.plans[planId]) {
              updated.plans[planId].price_usd = calc.recommended_price_usd;
              updated.plans[planId].price_bdt = calc.recommended_price_bdt;
            }
          }
          updated.ai_cost_per_credit = calcInputs.ai_cost_per_credit;
          updated.target_profit_margin = calcInputs.target_profit_margin;
          updated.bdt_exchange_rate = calcInputs.bdt_exchange_rate;
          setPricingEdit(updated);
        }
      }
    } catch {
      toast.error("Calculation failed");
    }
  };

  // Auto-sync: recalculate prices client-side whenever calcInputs change
  useEffect(() => {
    if (!pricingEdit) return;
    const { ai_cost_per_credit, target_profit_margin, bdt_exchange_rate } = calcInputs;
    if (!ai_cost_per_credit || !target_profit_margin || !bdt_exchange_rate) return;
    
    const marginMultiplier = 1 + (target_profit_margin / 100);
    const updated = { ...pricingEdit, plans: { ...pricingEdit.plans } };
    let changed = false;
    
    for (const [planId, plan] of Object.entries(updated.plans)) {
      if (planId === "free") continue;
      const baseCost = (plan.credits || 0) * ai_cost_per_credit;
      const recUsd = Math.round(baseCost * marginMultiplier * 100) / 100;
      const recBdt = Math.round(recUsd * bdt_exchange_rate);
      if (plan.price_usd !== recUsd || plan.price_bdt !== recBdt) {
        updated.plans[planId] = { ...plan, price_usd: recUsd, price_bdt: recBdt };
        changed = true;
      }
    }
    
    if (changed) {
      updated.ai_cost_per_credit = ai_cost_per_credit;
      updated.target_profit_margin = target_profit_margin;
      updated.bdt_exchange_rate = bdt_exchange_rate;
      setPricingEdit(updated);
    }
  }, [calcInputs.ai_cost_per_credit, calcInputs.target_profit_margin, calcInputs.bdt_exchange_rate]);

  const handlePublishPricing = async () => {
    if (!pricingEdit) return;
    try {
      const res = await fetch(`${API}/admin/pricing`, {
        method: "PUT",
        headers,
        body: JSON.stringify(pricingEdit)
      });
      if (res.ok) {
        const data = await res.json();
        setPricingConfig(data.pricing);
        toast.success("Pricing published! Changes are now live.");
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to publish pricing");
      }
    } catch {
      toast.error("Failed to publish pricing");
    }
  };

  const updatePlanField = (planId, field, value) => {
    setPricingEdit(prev => ({
      ...prev,
      plans: {
        ...prev.plans,
        [planId]: {
          ...prev.plans[planId],
          [field]: field === 'includes_commander' ? value : (typeof prev.plans[planId][field] === 'number' ? parseFloat(value) || 0 : value)
        }
      }
    }));
  };

  const addFeatureToPlan = (planId, feature) => {
    if (!feature.trim()) return;
    setPricingEdit(prev => ({
      ...prev,
      plans: {
        ...prev.plans,
        [planId]: {
          ...prev.plans[planId],
          features: [...(prev.plans[planId].features || []), feature.trim()]
        }
      }
    }));
  };

  const removeFeatureFromPlan = (planId, featureIndex) => {
    setPricingEdit(prev => ({
      ...prev,
      plans: {
        ...prev.plans,
        [planId]: {
          ...prev.plans[planId],
          features: (prev.plans[planId].features || []).filter((_, i) => i !== featureIndex)
        }
      }
    }));
  };

    // Compute live calculations from current inputs
    const { ai_cost_per_credit, target_profit_margin, bdt_exchange_rate } = calcInputs;
    const marginMultiplier = 1 + ((target_profit_margin || 0) / 100);
    const planCredits = { free: 50, starter: 500, pro: 2000, business: 6000 };
    const liveCalcs = {};
    for (const [pid, credits] of Object.entries(planCredits)) {
      const base = credits * (ai_cost_per_credit || 0);
      const rec = pid === "free" ? 0 : Math.round(base * marginMultiplier * 100) / 100;
      const recBdt = pid === "free" ? 0 : Math.round(rec * (bdt_exchange_rate || 0));
      liveCalcs[pid] = { credits, base: Math.round(base * 100) / 100, rec, recBdt, profit: Math.round((rec - base) * 100) / 100 };
    }

    const syncAllBdtPricing = (newRate) => {
      setCalcInputs(p => ({...p, bdt_exchange_rate: newRate}));
      if (pricingEdit) {
        const updated = { ...pricingEdit, plans: { ...pricingEdit.plans } };
        for (const [planId, plan] of Object.entries(updated.plans)) {
          if (planId !== 'free') {
            updated.plans[planId] = { ...plan, price_bdt: Math.round((plan.price_usd || 0) * newRate) };
          }
        }
        setPricingEdit(updated);
      }
    };

    const applyMarginToPlans = () => {
      if (pricingEdit) {
        const updated = { ...pricingEdit, plans: { ...pricingEdit.plans } };
        for (const [planId, plan] of Object.entries(updated.plans)) {
          if (planId !== 'free') {
            const cost = (plan.credits || 0) * (ai_cost_per_credit || 0.003);
            const usd = Math.round(cost * marginMultiplier * 100) / 100;
            updated.plans[planId] = { ...plan, price_usd: usd, price_bdt: Math.round(usd * (bdt_exchange_rate || 107)) };
          }
        }
        setPricingEdit(updated);
        toast.success(`Applied ${target_profit_margin}% margin to all plans`);
      }
    };

  return (
    <div className="space-y-6">
      {/* Profit Margin Calculator */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-amber-400" />
            </div>
            Profit Margin Calculator
            <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px] ml-2">LIVE SYNC</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Live AI Cost Summary - auto-updates every 15s */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 rounded-xl bg-white/5 border border-white/5" data-testid="live-cost-summary">
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Total AI Cost <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </p>
              <p className="text-xl font-bold text-red-400 font-mono" data-testid="live-total-cost">${liveCost.total_cost_usd?.toFixed(4) || '0.00'}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5 flex items-center gap-1">
                Cost per Credit <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </p>
              <p className="text-xl font-bold text-amber-400 font-mono" data-testid="live-cost-per-credit">${liveCost.avg_cost_per_credit?.toFixed(6) || '0.003'}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5">Total API Calls</p>
              <p className="text-xl font-bold text-white font-mono" data-testid="live-total-calls">{liveCost.total_calls?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 mb-0.5">Data Source</p>
              <p className="text-sm font-medium mt-1">
                {liveCost.source === "real_usage" 
                  ? <span className="text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Real Usage</span>
                  : <span className="text-zinc-500">Default Estimate</span>
                }
              </p>
              <p className="text-[10px] text-zinc-600 mt-0.5">Refreshes every 15s</p>
            </div>
          </div>

          <p className="text-zinc-400 text-sm">Set your target margin and apply it to all pricing — plan prices and credit packs update instantly.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">AI Cost per Credit (USD)</Label>
              <div
                className="flex items-center h-10 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-amber-400 font-mono font-bold"
                data-testid="calc-cost-display"
              >
                ${(calcInputs.ai_cost_per_credit || 0).toFixed(6)}
              </div>
              <p className="text-[10px] text-emerald-500/70 flex items-center gap-1"><span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live from {liveCost.total_calls} API calls</p>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">Target Profit Margin (%)</Label>
              <Input
                type="number"
                value={calcInputs.target_profit_margin}
                onChange={(e) => setCalcInputs(p => ({...p, target_profit_margin: parseInt(e.target.value) || 0}))}
                className="bg-zinc-800/50 border-white/10"
                data-testid="calc-margin-input"
              />
              <p className="text-[10px] text-zinc-500">{target_profit_margin}% means {(marginMultiplier).toFixed(1)}x the cost</p>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">BDT Exchange Rate</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={calcInputs.bdt_exchange_rate}
                  onChange={(e) => syncAllBdtPricing(parseFloat(e.target.value) || 0)}
                  className="bg-zinc-800/50 border-white/10 flex-1"
                  data-testid="calc-bdt-input"
                />
                <Button variant="outline" size="sm" className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs whitespace-nowrap"
                  data-testid="refresh-rate-btn"
                  onClick={async () => {
                    try {
                      const res = await fetch(`${API}/exchange-rate`);
                      if (res.ok) { const d = await res.json(); syncAllBdtPricing(d.usd_bdt); toast.success(`Rate updated: 1 USD = ${d.usd_bdt} BDT`); }
                    } catch { toast.error("Failed to fetch rate"); }
                  }}>
                  Refresh Live
                </Button>
              </div>
              <p className="text-[10px] text-emerald-500/70">Live rate: 1 USD = {bdt_exchange_rate} BDT (auto-syncs all BDT prices)</p>
            </div>
          </div>

          <Button onClick={applyMarginToPlans}
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
            data-testid="apply-margin-plans-btn">
            Apply {target_profit_margin}% Margin to All Plans
          </Button>

          {/* Live price preview table */}
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-zinc-400">Plan</th>
                  <th className="text-right py-2 text-zinc-400">Credits</th>
                  <th className="text-right py-2 text-zinc-400">AI Cost</th>
                  <th className="text-right py-2 text-zinc-400">Price USD</th>
                  <th className="text-right py-2 text-zinc-400">Price BDT</th>
                  <th className="text-right py-2 text-zinc-400">Profit/User</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                {Object.entries(liveCalcs).map(([id, calc]) => (
                  <tr key={id} className="border-b border-white/5">
                    <td className="py-2 capitalize font-medium">{id}</td>
                    <td className="text-right">{calc.credits}</td>
                    <td className="text-right text-red-400">${calc.base}</td>
                    <td className="text-right text-emerald-400">${calc.rec}</td>
                    <td className="text-right text-emerald-400">{calc.recBdt}</td>
                    <td className="text-right text-amber-400">${calc.profit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Manual Price Editor with Cost & Margin */}
      {pricingEdit && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Edit Plan Pricing</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(pricingEdit.plans).map(([planId, plan]) => {
              const isFree = planId === "free";
              const costUsd = (plan.credits || 0) * (calcInputs.ai_cost_per_credit || 0.003);
              const profitUsd = (plan.price_usd || 0) - costUsd;
              const marginPct = costUsd > 0 ? ((profitUsd / costUsd) * 100).toFixed(0) : 0;
              const isLoss = profitUsd < 0;
              const isLowMargin = marginPct < 100 && !isLoss;

              const applyMarginToPlan = (margin) => {
                const mult = 1 + (margin / 100);
                const usd = Math.round(costUsd * mult * 100) / 100;
                updatePlanField(planId, 'price_usd', usd);
                updatePlanField(planId, 'price_bdt', Math.round(usd * (bdt_exchange_rate || 107)));
                toast.success(`Applied ${margin}% margin to ${plan.name}`);
              };

              return (
                <div key={planId} className="p-4 rounded-lg bg-white/5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-white font-semibold capitalize">{plan.name} Plan</h4>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500">Cost: <span className="text-red-400 font-mono">${costUsd.toFixed(2)}</span></span>
                      <span className="text-xs text-zinc-500">Profit: <span className={`font-mono ${isLoss ? 'text-red-400' : 'text-emerald-400'}`}>${profitUsd.toFixed(2)}</span></span>
                      <Badge className={`text-[10px] ${
                        isLoss ? 'bg-red-500/20 text-red-400' :
                        isLowMargin ? 'bg-amber-500/20 text-amber-400' :
                        'bg-emerald-500/20 text-emerald-400'
                      }`} data-testid={`margin-${planId}`}>
                        {isLoss ? 'LOSS' : `${marginPct}% margin`}
                      </Badge>
                      {!isFree && onDeletePlan && (
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400" onClick={() => onDeletePlan(planId)} data-testid={`delete-plan-${planId}`}>
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Per-plan margin control */}
                  {!isFree && (
                    <div className="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5">
                      <span className="text-xs text-zinc-400 shrink-0">Set margin:</span>
                      {[100, 200, 500, 1000].map(m => (
                        <Button key={m} size="sm" variant="outline"
                          className={`text-[10px] h-6 px-2 border-white/10 ${parseInt(marginPct) === m ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'text-zinc-400 hover:bg-white/5'}`}
                          onClick={() => applyMarginToPlan(m)}
                          data-testid={`plan-margin-${planId}-${m}`}
                        >{m}%</Button>
                      ))}
                      <div className="flex items-center gap-1 ml-1">
                        <Input
                          type="number" placeholder="Custom"
                          className="bg-zinc-800/50 border-white/10 h-6 w-16 text-[10px] px-1.5"
                          data-testid={`plan-margin-${planId}-custom`}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') applyMarginToPlan(parseInt(e.target.value) || 0);
                          }}
                        />
                        <span className="text-[10px] text-zinc-500">%</span>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Price USD</Label>
                      <Input type="number" step="0.01" value={plan.price_usd} onChange={(e) => updatePlanField(planId, 'price_usd', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-usd`} />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Price BDT</Label>
                      <Input type="number" value={plan.price_bdt} onChange={(e) => updatePlanField(planId, 'price_bdt', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-bdt`} />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Credits/mo</Label>
                      <Input type="number" value={plan.credits} onChange={(e) => updatePlanField(planId, 'credits', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-credits`} />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Max Agents</Label>
                      <Input type="number" value={plan.max_agents} onChange={(e) => updatePlanField(planId, 'max_agents', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-agents`} />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Custom Agents</Label>
                      <Input type="number" value={plan.max_custom_agents} onChange={(e) => updatePlanField(planId, 'max_custom_agents', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-custom`} />
                      <p className="text-[9px] text-zinc-600">-1 = unlimited</p>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Team Size</Label>
                      <Input type="number" value={plan.max_team_members || 1} onChange={(e) => updatePlanField(planId, 'max_team_members', e.target.value)} className="bg-zinc-800/50 border-white/10 h-9 text-sm" data-testid={`edit-${planId}-team`} />
                      <p className="text-[9px] text-zinc-600">-1 = unlimited</p>
                    </div>
                    <div className="space-y-1 flex flex-col justify-end">
                      <label className="flex items-center gap-2 cursor-pointer h-9 px-2 rounded-md bg-zinc-800/30 border border-white/5">
                        <input type="checkbox" checked={plan.includes_commander || false} onChange={(e) => updatePlanField(planId, 'includes_commander', e.target.checked)} className="w-3.5 h-3.5 rounded border-white/20 bg-zinc-800 accent-indigo-500" data-testid={`edit-${planId}-commander`} />
                        <span className="text-xs text-zinc-300">Commander</span>
                      </label>
                    </div>
                  </div>

                  {/* Features Editor */}
                  <div className="space-y-2">
                    <Label className="text-zinc-400 text-xs">Features (displayed on pricing page)</Label>
                    <div className="flex flex-wrap gap-1.5">
                      {(plan.features || []).map((f, i) => (
                        <Badge key={i} className="bg-indigo-500/15 text-indigo-400 border-0 text-[10px] gap-1">
                          {f}
                          <button onClick={() => removeFeatureFromPlan(planId, i)} className="hover:text-red-400"><X className="w-2.5 h-2.5" /></button>
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add feature..."
                        className="bg-zinc-800/50 border-white/10 h-7 text-xs flex-1"
                        data-testid={`feature-input-${planId}`}
                        onKeyDown={(e) => { if (e.key === 'Enter' && e.target.value.trim()) { addFeatureToPlan(planId, e.target.value); e.target.value = ''; }}}
                      />
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-zinc-400 hover:text-indigo-400" onClick={(e) => {
                        const input = e.currentTarget.previousElementSibling;
                        if (input?.value?.trim()) { addFeatureToPlan(planId, input.value); input.value = ''; }
                      }}><Plus className="w-3 h-3" /></Button>
                    </div>
                  </div>

                  {/* Cost breakdown bar */}
                  {!isFree && (
                    <>
                      <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isLoss ? 'bg-red-500' : 'bg-gradient-to-r from-red-500 via-amber-500 to-emerald-500'}`}
                          style={{ width: `${Math.min(100, plan.price_usd > 0 ? (costUsd / plan.price_usd * 100) : 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-zinc-500">
                        <span>AI Cost: ${costUsd.toFixed(2)}</span>
                        <span>Your Price: ${plan.price_usd}</span>
                      </div>
                    </>
                  )}
                </div>
              );
            })}

            <div className="p-4 rounded-lg bg-white/5 space-y-3">
              <h4 className="text-white font-semibold">Custom Agent Creation Cost</h4>
              <div className="w-48">
                <Input
                  type="number"
                  value={pricingEdit.custom_agent_credit_cost}
                  onChange={(e) => setPricingEdit(p => ({...p, custom_agent_credit_cost: parseInt(e.target.value) || 0}))}
                  className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                  data-testid="edit-agent-cost"
                />
                <p className="text-[10px] text-zinc-500 mt-1">Credits charged per custom agent</p>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                onClick={handlePublishPricing}
                className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
                data-testid="publish-pricing-btn"
              >
                Publish Pricing Changes
              </Button>
              <Button
                variant="outline"
                className="border-white/10"
                onClick={() => setPricingEdit(JSON.parse(JSON.stringify(pricingConfig)))}
                data-testid="reset-pricing-btn"
              >
                Reset to Current
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
