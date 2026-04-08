import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Plus, Trash2, Save, Package, DollarSign,
  Edit2, X, Check, CreditCard, Users
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};
const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} }`;
const formInput = { background: "rgba(255,255,255,.04)", border: `1px solid rgba(255,255,255,0.08)`, borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" };
const formInputSm = { ...formInput, padding: "5px 10px", fontSize: 12 };

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

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 900, animation: "fadeUp .4s ease" }} data-testid="pricing-admin-page">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: 0 }} data-testid="pricing-admin-title">
            Pricing Management
          </h1>
          <p style={{ fontSize: 13, color: T.zinc, marginTop: 2 }}>
            Create, edit, and delete subscription plans. Changes take effect immediately.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          style={{ display: "flex", alignItems: "center", gap: 6, background: "#4f46e5", border: "none", borderRadius: 8, padding: "8px 14px", color: "#fff", fontSize: 13, cursor: "pointer", fontFamily: "inherit" }}
          data-testid="create-plan-btn"
        >
          <Plus size={14} /> New Plan
        </button>
      </div>

      {/* Create Plan Form */}
      {showCreate && (
        <div style={{ background: T.glass, border: `1px solid rgba(129,140,248,0.3)`, borderRadius: 12, padding: 20 }} data-testid="create-plan-form">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <span style={{ color: "#fff", fontSize: 15, fontWeight: 600 }}>Create New Plan</span>
            <button onClick={() => setShowCreate(false)} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4 }}><X size={16} /></button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Plan ID (unique, lowercase)</label>
                <input value={newPlan.plan_id} onChange={e => setNewPlan(p => ({ ...p, plan_id: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') }))} placeholder="enterprise" style={formInput} data-testid="new-plan-id" />
              </div>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Display Name</label>
                <input value={newPlan.name} onChange={e => setNewPlan(p => ({ ...p, name: e.target.value }))} placeholder="Enterprise" style={formInput} data-testid="new-plan-name" />
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Price USD/mo</label>
                <input type="number" value={newPlan.price_usd} onChange={e => setNewPlan(p => ({ ...p, price_usd: parseFloat(e.target.value) || 0 }))} style={formInput} data-testid="new-plan-price-usd" />
              </div>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Price BDT/mo</label>
                <input type="number" value={newPlan.price_bdt} onChange={e => setNewPlan(p => ({ ...p, price_bdt: parseFloat(e.target.value) || 0 }))} style={formInput} data-testid="new-plan-price-bdt" />
              </div>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Credits/mo</label>
                <input type="number" value={newPlan.credits} onChange={e => setNewPlan(p => ({ ...p, credits: parseInt(e.target.value) || 0 }))} style={formInput} data-testid="new-plan-credits" />
              </div>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Max Agents</label>
                <input type="number" value={newPlan.max_agents} onChange={e => setNewPlan(p => ({ ...p, max_agents: parseInt(e.target.value) || 0 }))} style={formInput} data-testid="new-plan-agents" />
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Max Custom Agents (-1 = unlimited)</label>
                <input type="number" value={newPlan.max_custom_agents} onChange={e => setNewPlan(p => ({ ...p, max_custom_agents: parseInt(e.target.value) || 0 }))} style={formInput} />
              </div>
              <div>
                <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 4 }}>Max Team Members (-1 = unlimited)</label>
                <input type="number" value={newPlan.max_team_members} onChange={e => setNewPlan(p => ({ ...p, max_team_members: parseInt(e.target.value) || 0 }))} style={formInput} />
              </div>
              <div style={{ display: "flex", alignItems: "flex-end", paddingBottom: 4 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                  <input type="checkbox" checked={newPlan.includes_commander} onChange={e => setNewPlan(p => ({ ...p, includes_commander: e.target.checked }))} style={{ width: 16, height: 16 }} />
                  <span style={{ fontSize: 13, color: "#d4d4d8" }}>Includes Commander</span>
                </label>
              </div>
            </div>
            {/* Features */}
            <div>
              <label style={{ color: "#a1a1aa", fontSize: 11, display: "block", marginBottom: 8 }}>Features (displayed on pricing page)</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 8 }}>
                {newPlan.features.map((f, i) => (
                  <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 4, background: "rgba(129,140,248,0.15)", color: T.indigo, borderRadius: 6, padding: "2px 8px", fontSize: 12 }}>
                    {f}
                    <button onClick={() => setNewPlan(p => ({ ...p, features: p.features.filter((_, j) => j !== i) }))} style={{ background: "none", border: "none", color: "inherit", cursor: "pointer", padding: 0, display: "flex" }}><X size={11} /></button>
                  </span>
                ))}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <input value={newFeature} onChange={e => setNewFeature(e.target.value)} placeholder="Add feature..." style={{ ...formInput, flex: 1 }} onKeyDown={e => { if (e.key === 'Enter' && newFeature.trim()) { setNewPlan(p => ({ ...p, features: [...p.features, newFeature.trim()] })); setNewFeature(''); }}} data-testid="new-plan-feature-input" />
                <button onClick={() => { if (newFeature.trim()) { setNewPlan(p => ({ ...p, features: [...p.features, newFeature.trim()] })); setNewFeature(''); }}} style={{ background: "none", border: `1px solid ${T.border}`, borderRadius: 8, padding: "0 12px", color: "#fff", cursor: "pointer", display: "flex", alignItems: "center" }} data-testid="add-feature-btn">
                  <Plus size={13} />
                </button>
              </div>
            </div>
            <button onClick={handleCreatePlan} disabled={saving} style={{ display: "flex", alignItems: "center", gap: 6, background: "#059669", border: "none", borderRadius: 8, padding: "9px 16px", color: "#fff", fontSize: 13, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? 0.7 : 1, fontFamily: "inherit" }} data-testid="save-new-plan-btn">
              {saving
                ? <div style={{ width: 14, height: 14, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                : <Check size={14} />}
              Create Plan
            </button>
          </div>
        </div>
      )}

      {/* Existing Plans */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: 16 }} data-testid="plans-grid">
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
      <div style={{ background: T.glass, border: `1px solid rgba(245,158,11,0.3)`, borderRadius: 12, padding: 16 }} data-testid={`edit-plan-${planId}`}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <span style={{ color: "#fff", fontSize: 14, fontWeight: 600 }}>Editing: {plan.name}</span>
          <button onClick={onCancel} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 4 }}><X size={15} /></button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Display Name</label>
              <input value={editData.name} onChange={e => setEditData(d => ({ ...d, name: e.target.value }))} style={formInputSm} />
            </div>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Credits/mo</label>
              <input type="number" value={editData.credits} onChange={e => setEditData(d => ({ ...d, credits: parseInt(e.target.value) || 0 }))} style={formInputSm} />
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Price USD/mo</label>
              <input type="number" value={editData.price_usd} onChange={e => setEditData(d => ({ ...d, price_usd: parseFloat(e.target.value) || 0 }))} style={formInputSm} />
            </div>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Price BDT/mo</label>
              <input type="number" value={editData.price_bdt} onChange={e => setEditData(d => ({ ...d, price_bdt: parseFloat(e.target.value) || 0 }))} style={formInputSm} />
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Max Agents</label>
              <input type="number" value={editData.max_agents} onChange={e => setEditData(d => ({ ...d, max_agents: parseInt(e.target.value) || 0 }))} style={formInputSm} />
            </div>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Max Custom (-1=∞)</label>
              <input type="number" value={editData.max_custom_agents} onChange={e => setEditData(d => ({ ...d, max_custom_agents: parseInt(e.target.value) || 0 }))} style={formInputSm} />
            </div>
            <div>
              <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 3 }}>Team Members (-1=∞)</label>
              <input type="number" value={editData.max_team_members} onChange={e => setEditData(d => ({ ...d, max_team_members: parseInt(e.target.value) || 0 }))} style={formInputSm} />
            </div>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
            <input type="checkbox" checked={editData.includes_commander} onChange={e => setEditData(d => ({ ...d, includes_commander: e.target.checked }))} style={{ width: 16, height: 16 }} />
            <span style={{ fontSize: 12, color: "#d4d4d8" }}>Includes Commander</span>
          </label>
          {/* Features editor */}
          <div>
            <label style={{ color: "#71717a", fontSize: 10, display: "block", marginBottom: 6 }}>Features</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 8 }}>
              {(editData.features || []).map((f, i) => (
                <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 3, background: "rgba(129,140,248,0.12)", color: T.indigo, borderRadius: 5, padding: "2px 6px", fontSize: 10 }}>
                  {f}
                  <button onClick={() => setEditData(d => ({ ...d, features: d.features.filter((_, j) => j !== i) }))} style={{ background: "none", border: "none", color: "inherit", cursor: "pointer", padding: 0, display: "flex" }}><X size={9} /></button>
                </span>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <input value={editFeature} onChange={e => setEditFeature(e.target.value)} placeholder="Add feature..." style={{ ...formInputSm, flex: 1 }} onKeyDown={e => { if (e.key === 'Enter' && editFeature.trim()) { setEditData(d => ({ ...d, features: [...(d.features || []), editFeature.trim()] })); setEditFeature(''); }}} />
              <button onClick={() => { if (editFeature.trim()) { setEditData(d => ({ ...d, features: [...(d.features || []), editFeature.trim()] })); setEditFeature(''); }}} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", display: "flex", alignItems: "center", padding: "0 8px" }}><Plus size={13} /></button>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => onSave(editData)} disabled={saving} style={{ display: "flex", alignItems: "center", gap: 4, background: "#059669", border: "none", borderRadius: 7, padding: "6px 12px", color: "#fff", fontSize: 12, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? 0.7 : 1, fontFamily: "inherit" }}>
              {saving
                ? <div style={{ width: 11, height: 11, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                : <Save size={11} />}
              Save
            </button>
            <button onClick={onCancel} style={{ background: "none", border: `1px solid ${T.border}`, borderRadius: 7, padding: "6px 12px", color: "#d4d4d8", fontSize: 12, cursor: "pointer", fontFamily: "inherit" }}>Cancel</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: 20, transition: "border-color .2s" }} data-testid={`plan-card-${planId}`}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(129,140,248,0.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Package size={15} color={T.indigo} />
          </div>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>{plan.name}</p>
            <p style={{ fontSize: 10, color: "#52525b", margin: 0 }}>ID: {planId}</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 4 }}>
          <button onClick={onEdit} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 6, borderRadius: 6, display: "flex" }} data-testid={`edit-btn-${planId}`}>
            <Edit2 size={13} />
          </button>
          {planId !== "free" && (
            <button onClick={onDelete} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", padding: 6, borderRadius: 6, display: "flex" }} data-testid={`delete-btn-${planId}`}>
              <Trash2 size={13} />
            </button>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 12 }}>
        <div style={{ textAlign: "center", padding: 8, borderRadius: 8, background: "rgba(255,255,255,0.03)" }}>
          <DollarSign size={11} color={T.green} style={{ margin: "0 auto 2px" }} />
          <p style={{ fontSize: 13, fontWeight: 700, color: "#fff", margin: 0 }}>${plan.price_usd}</p>
          <p style={{ fontSize: 9, color: "#52525b", margin: 0 }}>USD/mo</p>
        </div>
        <div style={{ textAlign: "center", padding: 8, borderRadius: 8, background: "rgba(255,255,255,0.03)" }}>
          <CreditCard size={11} color={T.amber} style={{ margin: "0 auto 2px" }} />
          <p style={{ fontSize: 13, fontWeight: 700, color: "#fff", margin: 0 }}>{plan.credits?.toLocaleString()}</p>
          <p style={{ fontSize: 9, color: "#52525b", margin: 0 }}>Credits</p>
        </div>
        <div style={{ textAlign: "center", padding: 8, borderRadius: 8, background: "rgba(255,255,255,0.03)" }}>
          <Users size={11} color={T.cyan} style={{ margin: "0 auto 2px" }} />
          <p style={{ fontSize: 13, fontWeight: 700, color: "#fff", margin: 0 }}>{plan.max_agents === -1 ? "All" : plan.max_agents}</p>
          <p style={{ fontSize: 9, color: "#52525b", margin: 0 }}>Agents</p>
        </div>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 8 }}>
        {plan.includes_commander && (
          <span style={{ background: "rgba(245,158,11,0.12)", color: T.amber, borderRadius: 5, padding: "2px 7px", fontSize: 9 }}>Commander</span>
        )}
        <span style={{ background: "rgba(113,113,122,0.2)", color: T.zinc, borderRadius: 5, padding: "2px 7px", fontSize: 9 }}>
          Team: {plan.max_team_members === -1 ? "Unlimited" : plan.max_team_members}
        </span>
        <span style={{ background: "rgba(113,113,122,0.2)", color: T.zinc, borderRadius: 5, padding: "2px 7px", fontSize: 9 }}>
          Custom: {plan.max_custom_agents === -1 ? "Unlimited" : plan.max_custom_agents}
        </span>
      </div>

      {plan.features && plan.features.length > 0 && (
        <div style={{ borderTop: `1px solid ${T.border}`, paddingTop: 8, display: "flex", flexDirection: "column", gap: 4 }}>
          {plan.features.slice(0, 5).map((f, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#a1a1aa" }}>
              <Check size={11} color={T.green} style={{ flexShrink: 0 }} />
              {f}
            </div>
          ))}
          {plan.features.length > 5 && (
            <p style={{ fontSize: 9, color: "#52525b", margin: 0 }}>+{plan.features.length - 5} more features</p>
          )}
        </div>
      )}
    </div>
  );
}
