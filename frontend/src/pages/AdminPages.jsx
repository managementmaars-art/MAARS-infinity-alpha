/**
 * Admin Page Wrappers - Standalone pages for each admin tab.
 * Each wrapper fetches its own data and renders the corresponding tab component.
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { Loader2, Plus, X, Check, Package } from "lucide-react";
import { OverviewTab } from "../components/admin/tabs/OverviewTab";
import { UsersTab } from "../components/admin/tabs/UsersTab";
import { AgentsTab } from "../components/admin/tabs/AgentsTab";
import { TransactionsTab } from "../components/admin/tabs/TransactionsTab";
import { ApiKeysTab } from "../components/admin/tabs/ApiKeysTab";
import { PricingManagerTab } from "../components/admin/tabs/PricingManagerTab";
import { PaymentSetupTab } from "../components/admin/tabs/PaymentSetupTab";
import { AuditLogTab } from "../components/admin/tabs/AuditLogTab";
import AnalyticsTab from "./AnalyticsTab";
import SmtpConfigTab from "./SmtpConfigTab";
import BrandingTab from "./BrandingTab";
import KnowledgeBaseTab from "./KnowledgeBaseTab";
import CustomPackagesTab from "../components/admin/CustomPackagesTab";
import IntegrationsTab from "../components/admin/IntegrationsTab";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";

const AdminLoader = () => (
  <div className="flex items-center justify-center h-48">
    <Loader2 className="w-6 h-6 text-red-400 animate-spin" />
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
    <div className="space-y-6" data-testid="pricing-packages-page">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']" data-testid="pricing-page-title">Pricing & Packages</h1>
          <p className="text-sm text-zinc-500 mt-0.5">Manage subscription plans, pricing margins, and custom packages from one place.</p>
        </div>
        <Button onClick={() => setShowCreate(true)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="create-plan-btn">
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
  const [apiKeyInputs, setApiKeyInputs] = useState({ openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: "", active_provider: "emergent" });
  const [apiUsage, setApiUsage] = useState(null);
  const [testingKey, setTestingKey] = useState(null);
  const [loading, setLoading] = useState(true);
  const h = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(() => {
    Promise.all([
      fetch(`${API}/admin/api-keys`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/api-usage`, { headers: h }).then(r => r.ok ? r.json() : null),
    ]).then(([k, u]) => {
      if (k) { setApiKeysConfig(k); setApiKeyInputs(prev => ({ ...prev, active_provider: k.active_provider || "emergent" })); }
      if (u) setApiUsage(u);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <AdminLoader />;
  return (
    <>
      <ApiKeysTab apiKeysConfig={apiKeysConfig} apiKeyInputs={apiKeyInputs} setApiKeyInputs={setApiKeyInputs} apiUsage={apiUsage} testingKey={testingKey} setTestingKey={setTestingKey} token={token} onRefresh={fetchData} />
      <div className="mt-6"><IntegrationsTab /></div>
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
