/**
 * Admin Page Wrappers - Standalone pages for each admin tab.
 * Each wrapper fetches its own data and renders the corresponding tab component.
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { Plus, X, Check, Package } from "lucide-react";
import { OverviewTab } from "../components/admin/tabs/OverviewTab";
import { UsersTab } from "../components/admin/tabs/UsersTab";
import { AgentsTab } from "../components/admin/tabs/AgentsTab";
import { TransactionsTab } from "../components/admin/tabs/TransactionsTab";
import { ApiKeysTab } from "../components/admin/tabs/ApiKeysTab";
import { PricingManagerTab } from "../components/admin/tabs/PricingManagerTab";
import { PaymentSetupTab } from "../components/admin/tabs/PaymentSetupTab";
import { AuditLogTab } from "../components/admin/tabs/AuditLogTab";
import { UniversalGatewayTab } from "../components/admin/tabs/UniversalGatewayTab";
import AnalyticsTab from "./AnalyticsTab";
import SmtpConfigTab from "./SmtpConfigTab";
import BrandingTab from "./BrandingTab";
import KnowledgeBaseTab from "./KnowledgeBaseTab";
import CustomPackagesTab from "../components/admin/CustomPackagesTab";
import IntegrationsTab from "../components/admin/IntegrationsTab";

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

const AdminLoader = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 192 }}>
    <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
  </div>
);

// --- Overview ---
export function AdminOverviewPage() {
  const { token } = useAuth();
  const [stats, setStats] = useState(null);
  const [profitData, setProfitData] = useState(null);
  const [apiKeysConfig, setApiKeysConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const h = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    Promise.all([
      fetch(`${API}/admin/stats`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/profit`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/api-keys`, { headers: h }).then(r => r.ok ? r.json() : null),
    ]).then(([s, p, k]) => {
      setStats(s); setProfitData(p); setApiKeysConfig(k); setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  if (loading) return <AdminLoader />;
  return <OverviewTab stats={stats} profitData={profitData} apiKeysConfig={apiKeysConfig} />;
}

// --- Analytics ---
export function AdminAnalyticsPage() {
  return <AnalyticsTab />;
}

// --- Users ---
export function AdminUsersPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/admin/users`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(d => { setUsers(d.users || d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  if (loading) return <AdminLoader />;
  return <UsersTab users={users} />;
}

// --- Agents ---
export function AdminAgentsPage() {
  const { token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateAgent, setShowCreateAgent] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: "", description: "", role: "", system_prompt: "", model_provider: "openai", model_name: "gpt-5.2", capabilities: "" });
  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchAgents = useCallback(() => {
    fetch(`${API}/admin/agents`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(d => { setAgents(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);

  const handleCreateAgent = async () => {
    if (!newAgent.name || !newAgent.role || !newAgent.system_prompt) { toast.error("Name, role, and system prompt required"); return; }
    const res = await fetch(`${API}/admin/agents`, { method: "POST", headers: h, body: JSON.stringify({ ...newAgent, capabilities: newAgent.capabilities.split(",").map(c => c.trim()).filter(Boolean) }) });
    if (res.ok) { toast.success("Agent created"); setShowCreateAgent(false); setNewAgent({ name: "", description: "", role: "", system_prompt: "", model_provider: "openai", model_name: "gpt-5.2", capabilities: "" }); fetchAgents(); }
    else toast.error("Failed to create agent");
  };

  const handleDeleteAgent = async (agentId, agentName) => {
    if (!window.confirm(`Delete agent "${agentName}"?`)) return;
    const res = await fetch(`${API}/admin/agents/${agentId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    if (res.ok) { toast.success("Agent deleted"); fetchAgents(); } else toast.error("Failed");
  };

  if (loading) return <AdminLoader />;
  return <AgentsTab agents={agents} setAgents={setAgents} showCreateAgent={showCreateAgent} setShowCreateAgent={setShowCreateAgent} newAgent={newAgent} setNewAgent={setNewAgent} handleCreateAgent={handleCreateAgent} handleDeleteAgent={handleDeleteAgent} token={token} />;
}

// --- Transactions ---
export function AdminTransactionsPage() {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/admin/transactions`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(d => { setTransactions(d.transactions || d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [token]);

  if (loading) return <AdminLoader />;
  return <TransactionsTab transactions={transactions} />;
}

// --- Pricing & Packages (Unified) ---
export function AdminPricingManagerPage() {
  const { token } = useAuth();
  const [pricingConfig, setPricingConfig] = useState(null);
  const [pricingEdit, setPricingEdit] = useState(null);
  const [calcInputs, setCalcInputs] = useState({ ai_cost_per_credit: 0.003, target_profit_margin: 200, bdt_exchange_rate: 107 });
  const [calcResult, setCalcResult] = useState(null);
  const [liveCost, setLiveCost] = useState({ avg_cost_per_credit: 0.003, total_cost_usd: 0, total_calls: 0, source: "default" });
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newPlan, setNewPlan] = useState({ plan_id: "", name: "", price_usd: 0, price_bdt: 0, credits: 0, max_agents: 0, max_custom_agents: 0, includes_commander: false, max_team_members: 1, features: [] });
  const [newFeature, setNewFeature] = useState("");
  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchPricing = useCallback(() => {
    Promise.all([
      fetch(`${API}/admin/pricing`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/avg-cost`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/exchange-rate`).then(r => r.ok ? r.json() : null),
    ]).then(([p, avg, rate]) => {
      if (p) { setPricingConfig(p); setPricingEdit(JSON.parse(JSON.stringify(p))); setCalcInputs(ci => ({ ...ci, ai_cost_per_credit: p.ai_cost_per_credit || 0.003, target_profit_margin: p.target_profit_margin || 200, bdt_exchange_rate: p.bdt_exchange_rate || 107 })); }
      if (avg?.source === "real_usage" && avg.avg_cost_per_credit > 0) { setCalcInputs(ci => ({ ...ci, ai_cost_per_credit: avg.avg_cost_per_credit })); setLiveCost(avg); }
      if (rate?.usd_bdt > 0) setCalcInputs(ci => ({ ...ci, bdt_exchange_rate: rate.usd_bdt }));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchPricing(); }, [fetchPricing]);

  const handleCreatePlan = async () => {
    if (!newPlan.plan_id || !newPlan.name) { toast.error("Plan ID and name are required"); return; }
    setSaving(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans`, { method: "POST", headers: h, body: JSON.stringify(newPlan) });
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

  const handleDeletePlan = async (planId) => {
    if (planId === "free") { toast.error("Cannot delete the free plan"); return; }
    const planName = pricingEdit?.plans?.[planId]?.name || planId;
    if (!window.confirm(`Delete plan "${planName}"? This cannot be undone.`)) return;
    setSaving(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans/${planId}`, { method: "DELETE", headers: h });
      if (res.ok) { toast.success("Plan deleted"); fetchPricing(); }
      else { const err = await res.json(); toast.error(err.detail || "Failed to delete"); }
    } catch { toast.error("Failed to delete plan"); }
    setSaving(false);
  };

  if (loading) return <AdminLoader />;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="pricing-packages-page">
      <style>{STYLES}</style>

      {/* Page Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: 0 }} data-testid="pricing-page-title">Pricing & Packages</h1>
          <p style={{ fontSize: 13, color: T.zinc, marginTop: 2 }}>Manage subscription plans, pricing margins, and custom packages from one place.</p>
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

      {/* Margin Calculator + Inline Plan Editor */}
      <PricingManagerTab pricingConfig={pricingConfig} setPricingConfig={setPricingConfig} pricingEdit={pricingEdit} setPricingEdit={setPricingEdit} calcInputs={calcInputs} setCalcInputs={setCalcInputs} calcResult={calcResult} setCalcResult={setCalcResult} liveCost={liveCost} token={token} onDeletePlan={handleDeletePlan} onRefresh={fetchPricing} />

      {/* Custom Packages */}
      <CustomPackagesTab />
    </div>
  );
}

// --- API Keys & Integrations ---
export function AdminApiKeysPage() {
  const { token } = useAuth();
  const [apiKeysConfig, setApiKeysConfig] = useState(null);
  const [apiKeyInputs, setApiKeyInputs] = useState({ openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: "", active_provider: "maars" });
  const [apiUsage, setApiUsage] = useState(null);
  const [testingKey, setTestingKey] = useState(null);
  const [loading, setLoading] = useState(true);
  const h = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(() => {
    Promise.all([
      fetch(`${API}/admin/api-keys`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/api-usage`, { headers: h }).then(r => r.ok ? r.json() : null),
    ]).then(([k, u]) => {
      if (k) { setApiKeysConfig(k); setApiKeyInputs(prev => ({ ...prev, active_provider: k.active_provider || "maars" })); }
      if (u) setApiUsage(u);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <AdminLoader />;
  return (
    <>
      <ApiKeysTab apiKeysConfig={apiKeysConfig} apiKeyInputs={apiKeyInputs} setApiKeyInputs={setApiKeyInputs} apiUsage={apiUsage} testingKey={testingKey} setTestingKey={setTestingKey} token={token} onRefresh={fetchData} />
      <div style={{ marginTop: 24 }}><IntegrationsTab /></div>
    </>
  );
}

// --- Payment Setup ---
export function AdminPaymentSetupPage() {
  const { token } = useAuth();
  return <PaymentSetupTab token={token} />;
}

// --- SMTP ---
export function AdminSmtpPage() {
  return <SmtpConfigTab />;
}

// --- Branding ---
export function AdminBrandingPage() {
  return <BrandingTab />;
}

// --- Knowledge Base ---
export function AdminKnowledgeBasePage() {
  return <KnowledgeBaseTab />;
}

// --- Audit Log ---
export function AdminAuditLogPage() {
  return <AuditLogTab />;
}

// --- Universal Gateway ---
export function AdminUniversalGatewayPage() {
  const { token } = useAuth();
  return <UniversalGatewayTab token={token} />;
}
