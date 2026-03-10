/**
 * Admin Page Wrappers - Standalone pages for each admin tab.
 * Each wrapper fetches its own data and renders the corresponding tab component.
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
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

// --- Pricing & Packages ---
export function AdminPricingManagerPage() {
  const { token } = useAuth();
  const [pricingConfig, setPricingConfig] = useState(null);
  const [pricingEdit, setPricingEdit] = useState(null);
  const [calcInputs, setCalcInputs] = useState({ ai_cost_per_credit: 0.003, target_profit_margin: 200, bdt_exchange_rate: 107 });
  const [calcResult, setCalcResult] = useState(null);
  const [liveCost, setLiveCost] = useState({ avg_cost_per_credit: 0.003, total_cost_usd: 0, total_calls: 0, source: "default" });
  const [loading, setLoading] = useState(true);
  const h = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${API}/admin/pricing`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/admin/avg-cost`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/exchange-rate`).then(r => r.ok ? r.json() : null),
    ]).then(([p, avg, rate]) => {
      if (p) { setPricingConfig(p); setPricingEdit(JSON.parse(JSON.stringify(p))); setCalcInputs(ci => ({ ...ci, ai_cost_per_credit: p.ai_cost_per_credit || 0.003, target_profit_margin: p.target_profit_margin || 200, bdt_exchange_rate: p.bdt_exchange_rate || 107 })); }
      if (avg?.source === "real_usage" && avg.avg_cost_per_credit > 0) { setCalcInputs(ci => ({ ...ci, ai_cost_per_credit: avg.avg_cost_per_credit })); setLiveCost(avg); }
      if (rate?.usd_bdt > 0) setCalcInputs(ci => ({ ...ci, bdt_exchange_rate: rate.usd_bdt }));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  if (loading) return <AdminLoader />;
  return (
    <>
      <PricingManagerTab pricingConfig={pricingConfig} setPricingConfig={setPricingConfig} pricingEdit={pricingEdit} setPricingEdit={setPricingEdit} calcInputs={calcInputs} setCalcInputs={setCalcInputs} calcResult={calcResult} setCalcResult={setCalcResult} liveCost={liveCost} token={token} />
      <div className="mt-6"><CustomPackagesTab /></div>
    </>
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
