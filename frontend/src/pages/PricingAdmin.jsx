import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Plus, Trash2, Save, Loader2, Package, DollarSign,
  Edit2, X, Check, CreditCard, Users, Sparkles
} from "lucide-react";
import { toast } from "sonner";

export default function PricingAdmin() {
  const { token } = useAuth();
  const [plans, setPlans] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newPlan, setNewPlan] = useState({
    plan_id: "", name: "", price_usd: 0, price_bdt: 0, credits: 0,
    max_agents: 0, max_custom_agents: 0, includes_commander: false,
    max_team_members: 1, features: []
  });
  const [newFeature, setNewFeature] = useState("");
  const [editFeature, setEditFeature] = useState("");
  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchPricing = useCallback(async () => {
    try {
      const res = await fetch(`${API}/admin/pricing`, { headers: h });
      if (res.ok) {
        const data = await res.json();
        setPlans(data.plans || {});
      }
    } catch {}
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchPricing(); }, [fetchPricing]);

  const handleCreatePlan = async () => {
    if (!newPlan.plan_id || !newPlan.name) {
      toast.error("Plan ID and name are required");
      return;
    }
    setSaving(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans`, {
        method: "POST", headers: h,
        body: JSON.stringify(newPlan)
      });
      if (res.ok) {
        toast.success(`Plan "${newPlan.name}" created`);
        setShowCreate(false);
        setNewPlan({ plan_id: "", name: "", price_usd: 0, price_bdt: 0, credits: 0, max_agents: 0, max_custom_agents: 0, includes_commander: false, max_team_members: 1, features: [] });
        fetchPricing();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to create plan");
      }
    } catch { toast.error("Failed to create plan"); }
    setSaving(false);
  };

  const handleUpdatePlan = async (planId, planData) => {
    setSaving(true);
    try {
      const updatedPlans = { ...plans, [planId]: planData };
      const res = await fetch(`${API}/admin/pricing`, {
        method: "PUT", headers: h,
        body: JSON.stringify({ plans: updatedPlans })
      });
      if (res.ok) {
        toast.success(`Plan "${planData.name}" updated`);
        setEditingPlan(null);
        fetchPricing();
      } else {
        toast.error("Failed to update plan");
      }
    } catch { toast.error("Failed to update"); }
    setSaving(false);
  };

  const handleDeletePlan = async (planId) => {
    if (planId === "free") { toast.error("Cannot delete free plan"); return; }
    if (!window.confirm(`Delete plan "${plans[planId]?.name}"? This cannot be undone.`)) return;
    setSaving(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans/${planId}`, {
        method: "DELETE", headers: h
      });
      if (res.ok) {
        toast.success("Plan deleted");
        fetchPricing();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to delete");
      }
    } catch { toast.error("Failed to delete"); }
    setSaving(false);
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 text-indigo-500 animate-spin" /></div>;

  return (
    <div className="space-y-6 max-w-5xl" data-testid="pricing-admin-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']" data-testid="pricing-admin-title">
            Pricing Management
          </h1>
          <p className="text-sm text-zinc-500 mt-0.5">
            Create, edit, and delete subscription plans. Changes take effect immediately.
          </p>
        </div>
        <Button
          onClick={() => setShowCreate(true)}
          className="bg-indigo-600 hover:bg-indigo-700"
          data-testid="create-plan-btn"
        >
          <Plus className="w-4 h-4 mr-2" /> New Plan
        </Button>
      </div>

      {/* Create Plan Form */}
      {showCreate && (
        <Card className="bg-zinc-900/70 border-indigo-500/30" data-testid="create-plan-form">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white text-lg">Create New Plan</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => setShowCreate(false)}><X className="w-4 h-4" /></Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-zinc-400 text-xs">Plan ID (unique, lowercase)</Label>
                <Input value={newPlan.plan_id} onChange={e => setNewPlan(p => ({ ...p, plan_id: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') }))} placeholder="enterprise" className="bg-zinc-800/50 border-white/10" data-testid="new-plan-id" />
              </div>
              <div>
                <Label className="text-zinc-400 text-xs">Display Name</Label>
                <Input value={newPlan.name} onChange={e => setNewPlan(p => ({ ...p, name: e.target.value }))} placeholder="Enterprise" className="bg-zinc-800/50 border-white/10" data-testid="new-plan-name" />
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div>
                <Label className="text-zinc-400 text-xs">Price USD/mo</Label>
                <Input type="number" value={newPlan.price_usd} onChange={e => setNewPlan(p => ({ ...p, price_usd: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" data-testid="new-plan-price-usd" />
              </div>
              <div>
                <Label className="text-zinc-400 text-xs">Price BDT/mo</Label>
                <Input type="number" value={newPlan.price_bdt} onChange={e => setNewPlan(p => ({ ...p, price_bdt: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" data-testid="new-plan-price-bdt" />
              </div>
              <div>
                <Label className="text-zinc-400 text-xs">Credits/mo</Label>
                <Input type="number" value={newPlan.credits} onChange={e => setNewPlan(p => ({ ...p, credits: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" data-testid="new-plan-credits" />
              </div>
              <div>
                <Label className="text-zinc-400 text-xs">Max Agents</Label>
                <Input type="number" value={newPlan.max_agents} onChange={e => setNewPlan(p => ({ ...p, max_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" data-testid="new-plan-agents" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label className="text-zinc-400 text-xs">Max Custom Agents (-1 = unlimited)</Label>
                <Input type="number" value={newPlan.max_custom_agents} onChange={e => setNewPlan(p => ({ ...p, max_custom_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" />
              </div>
              <div>
                <Label className="text-zinc-400 text-xs">Max Team Members (-1 = unlimited)</Label>
                <Input type="number" value={newPlan.max_team_members} onChange={e => setNewPlan(p => ({ ...p, max_team_members: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10" />
              </div>
              <div className="flex items-end gap-2 pb-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={newPlan.includes_commander} onChange={e => setNewPlan(p => ({ ...p, includes_commander: e.target.checked }))} className="w-4 h-4 rounded border-white/20 bg-zinc-800" />
                  <span className="text-sm text-zinc-300">Includes Commander</span>
                </label>
              </div>
            </div>
            {/* Features */}
            <div>
              <Label className="text-zinc-400 text-xs">Features (displayed on pricing page)</Label>
              <div className="flex flex-wrap gap-2 mt-2 mb-2">
                {newPlan.features.map((f, i) => (
                  <Badge key={i} className="bg-indigo-500/20 text-indigo-400 border-0 gap-1">
                    {f}
                    <button onClick={() => setNewPlan(p => ({ ...p, features: p.features.filter((_, j) => j !== i) }))} className="hover:text-red-400"><X className="w-3 h-3" /></button>
                  </Badge>
                ))}
              </div>
              <div className="flex gap-2">
                <Input value={newFeature} onChange={e => setNewFeature(e.target.value)} placeholder="Add feature..." className="bg-zinc-800/50 border-white/10 flex-1" onKeyDown={e => { if (e.key === 'Enter' && newFeature.trim()) { setNewPlan(p => ({ ...p, features: [...p.features, newFeature.trim()] })); setNewFeature(''); }}} data-testid="new-plan-feature-input" />
                <Button size="sm" variant="outline" className="border-white/10" onClick={() => { if (newFeature.trim()) { setNewPlan(p => ({ ...p, features: [...p.features, newFeature.trim()] })); setNewFeature(''); }}} data-testid="add-feature-btn">
                  <Plus className="w-3 h-3" />
                </Button>
              </div>
            </div>
            <Button onClick={handleCreatePlan} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700" data-testid="save-new-plan-btn">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Check className="w-4 h-4 mr-2" />}
              Create Plan
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Existing Plans */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="plans-grid">
        {Object.entries(plans).map(([planId, plan]) => {
          const isEditing = editingPlan === planId;
          return (
            <PlanCard
              key={planId}
              planId={planId}
              plan={plan}
              isEditing={isEditing}
              onEdit={() => setEditingPlan(planId)}
              onCancel={() => setEditingPlan(null)}
              onSave={(updatedPlan) => handleUpdatePlan(planId, updatedPlan)}
              onDelete={() => handleDeletePlan(planId)}
              saving={saving}
              editFeature={editFeature}
              setEditFeature={setEditFeature}
            />
          );
        })}
      </div>
    </div>
  );
}

function PlanCard({ planId, plan, isEditing, onEdit, onCancel, onSave, onDelete, saving, editFeature, setEditFeature }) {
  const [editData, setEditData] = useState(plan);

  useEffect(() => { setEditData(plan); }, [plan]);

  if (isEditing) {
    return (
      <Card className="bg-zinc-900/70 border-amber-500/30" data-testid={`edit-plan-${planId}`}>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white text-base">Editing: {plan.name}</CardTitle>
            <Button size="sm" variant="ghost" onClick={onCancel}><X className="w-4 h-4" /></Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-zinc-500 text-[10px]">Display Name</Label>
              <Input value={editData.name} onChange={e => setEditData(d => ({ ...d, name: e.target.value }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
            <div>
              <Label className="text-zinc-500 text-[10px]">Credits/mo</Label>
              <Input type="number" value={editData.credits} onChange={e => setEditData(d => ({ ...d, credits: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-zinc-500 text-[10px]">Price USD/mo</Label>
              <Input type="number" value={editData.price_usd} onChange={e => setEditData(d => ({ ...d, price_usd: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
            <div>
              <Label className="text-zinc-500 text-[10px]">Price BDT/mo</Label>
              <Input type="number" value={editData.price_bdt} onChange={e => setEditData(d => ({ ...d, price_bdt: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <Label className="text-zinc-500 text-[10px]">Max Agents</Label>
              <Input type="number" value={editData.max_agents} onChange={e => setEditData(d => ({ ...d, max_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
            <div>
              <Label className="text-zinc-500 text-[10px]">Max Custom (-1=∞)</Label>
              <Input type="number" value={editData.max_custom_agents} onChange={e => setEditData(d => ({ ...d, max_custom_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
            <div>
              <Label className="text-zinc-500 text-[10px]">Team Members (-1=∞)</Label>
              <Input type="number" value={editData.max_team_members} onChange={e => setEditData(d => ({ ...d, max_team_members: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" />
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={editData.includes_commander} onChange={e => setEditData(d => ({ ...d, includes_commander: e.target.checked }))} className="w-4 h-4 rounded" />
            <span className="text-xs text-zinc-300">Includes Commander</span>
          </label>
          {/* Features editor */}
          <div>
            <Label className="text-zinc-500 text-[10px]">Features</Label>
            <div className="flex flex-wrap gap-1.5 mt-1 mb-2">
              {(editData.features || []).map((f, i) => (
                <Badge key={i} className="bg-indigo-500/15 text-indigo-400 border-0 text-[10px] gap-1">
                  {f}
                  <button onClick={() => setEditData(d => ({ ...d, features: d.features.filter((_, j) => j !== i) }))} className="hover:text-red-400"><X className="w-2.5 h-2.5" /></button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input value={editFeature} onChange={e => setEditFeature(e.target.value)} placeholder="Add feature..." className="bg-zinc-800/50 border-white/10 h-7 text-xs flex-1" onKeyDown={e => { if (e.key === 'Enter' && editFeature.trim()) { setEditData(d => ({ ...d, features: [...(d.features || []), editFeature.trim()] })); setEditFeature(''); }}} />
              <Button size="sm" variant="ghost" className="h-7 px-2" onClick={() => { if (editFeature.trim()) { setEditData(d => ({ ...d, features: [...(d.features || []), editFeature.trim()] })); setEditFeature(''); }}}><Plus className="w-3 h-3" /></Button>
            </div>
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={() => onSave(editData)} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700">
              {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3 mr-1" />} Save
            </Button>
            <Button size="sm" variant="outline" className="border-white/10" onClick={onCancel}>Cancel</Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-zinc-900/50 border-white/5 hover:border-white/10 transition-all" data-testid={`plan-card-${planId}`}>
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center">
              <Package className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{plan.name}</p>
              <p className="text-[10px] text-zinc-600">ID: {planId}</p>
            </div>
          </div>
          <div className="flex gap-1">
            <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-zinc-500 hover:text-white" onClick={onEdit} data-testid={`edit-btn-${planId}`}>
              <Edit2 className="w-3.5 h-3.5" />
            </Button>
            {planId !== "free" && (
              <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400" onClick={onDelete} data-testid={`delete-btn-${planId}`}>
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="text-center p-2 rounded-lg bg-zinc-800/40">
            <DollarSign className="w-3 h-3 text-emerald-400 mx-auto mb-0.5" />
            <p className="text-sm font-bold text-white">${plan.price_usd}</p>
            <p className="text-[9px] text-zinc-600">USD/mo</p>
          </div>
          <div className="text-center p-2 rounded-lg bg-zinc-800/40">
            <CreditCard className="w-3 h-3 text-amber-400 mx-auto mb-0.5" />
            <p className="text-sm font-bold text-white">{plan.credits?.toLocaleString()}</p>
            <p className="text-[9px] text-zinc-600">Credits</p>
          </div>
          <div className="text-center p-2 rounded-lg bg-zinc-800/40">
            <Users className="w-3 h-3 text-cyan-400 mx-auto mb-0.5" />
            <p className="text-sm font-bold text-white">{plan.max_agents === -1 ? "All" : plan.max_agents}</p>
            <p className="text-[9px] text-zinc-600">Agents</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-2">
          {plan.includes_commander && <Badge className="bg-amber-500/15 text-amber-400 border-0 text-[9px]">Commander</Badge>}
          <Badge className="bg-zinc-700/50 text-zinc-400 border-0 text-[9px]">Team: {plan.max_team_members === -1 ? "Unlimited" : plan.max_team_members}</Badge>
          <Badge className="bg-zinc-700/50 text-zinc-400 border-0 text-[9px]">Custom: {plan.max_custom_agents === -1 ? "Unlimited" : plan.max_custom_agents}</Badge>
        </div>

        {plan.features && plan.features.length > 0 && (
          <div className="space-y-1 border-t border-white/5 pt-2">
            {plan.features.slice(0, 5).map((f, i) => (
              <div key={i} className="flex items-center gap-1.5 text-[10px] text-zinc-400">
                <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                {f}
              </div>
            ))}
            {plan.features.length > 5 && (
              <p className="text-[9px] text-zinc-600">+{plan.features.length - 5} more features</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
