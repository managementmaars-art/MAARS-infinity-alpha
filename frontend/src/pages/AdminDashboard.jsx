import { useState, useEffect, useCallback, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bot, Users, MessageSquare, CreditCard, TrendingUp, Shield,
  LayoutDashboard, ListTodo, Settings, LogOut, Menu, X,
  DollarSign, Activity, Key,
  BarChart3, Mail, Paintbrush, BookOpen, Package, ScrollText, Eye
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import AnalyticsTab from "./AnalyticsTab";
import SmtpConfigTab from "./SmtpConfigTab";
import BrandingTab from "./BrandingTab";
import KnowledgeBaseTab from "./KnowledgeBaseTab";
import CustomPackagesTab from "../components/admin/CustomPackagesTab";
import IntegrationsTab from "../components/admin/IntegrationsTab";
import { OverviewTab } from "../components/admin/tabs/OverviewTab";
import { UsersTab } from "../components/admin/tabs/UsersTab";
import { AgentsTab } from "../components/admin/tabs/AgentsTab";
import { TransactionsTab } from "../components/admin/tabs/TransactionsTab";
import { ApiKeysTab } from "../components/admin/tabs/ApiKeysTab";
import { PricingManagerTab } from "../components/admin/tabs/PricingManagerTab";
import { PaymentSetupTab } from "../components/admin/tabs/PaymentSetupTab";
import { AuditLogTab } from "../components/admin/tabs/AuditLogTab";
import { ClientVisibilityTab } from "../components/admin/tabs/ClientVisibilityTab";
import { UniversalGatewayTab } from "../components/admin/tabs/UniversalGatewayTab";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  zinc: "#71717a",
};

const STYLES = `
@keyframes spin { to{transform:rotate(360deg)} }
`;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [agents, setAgents] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [profitData, setProfitData] = useState(null);
  const [apiUsage, setApiUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateAgent, setShowCreateAgent] = useState(false);
  const [pricingConfig, setPricingConfig] = useState(null);
  const [pricingEdit, setPricingEdit] = useState(null);
  const [calcResult, setCalcResult] = useState(null);
  const [calcInputs, setCalcInputs] = useState({ ai_cost_per_credit: 0.003, target_profit_margin: 200, bdt_exchange_rate: 107 });
  const [apiKeysConfig, setApiKeysConfig] = useState(null);
  const [apiKeyInputs, setApiKeyInputs] = useState({
    active_provider: "maars",
    openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "",
    deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "",
    elevenlabs_key: "", groq_key: "", together_key: "", fireworks_key: "",
    ai21_key: "", cerebras_key: "", sambanova_key: "", nvidia_key: "",
    moonshot_key: "", qwen_key: "",
    yi_key: "", zhipu_key: "", doubao_key: "", hyperbolic_key: "",
    upstage_key: "", writer_key: "", huggingface_key: "", llama_key: "",
    novita_key: "", lepton_key: "", lambda_key: "", amazon_key: "",
    minimax_key: "", inception_key: "", arcee_key: "",
  });
  const [testingKey, setTestingKey] = useState(null);
  const [newAgent, setNewAgent] = useState({
    name: "", description: "", role: "", system_prompt: "",
    model_provider: "openai", model_name: "gpt-5.2", capabilities: ""
  });

  const [liveCost, setLiveCost] = useState({ avg_cost_per_credit: 0.003, total_cost_usd: 0, total_calls: 0, source: "default" });
  const liveCostRef = useRef(liveCost);
  liveCostRef.current = liveCost;

  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const fetchLiveCost = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/admin/avg-cost`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setLiveCost(data);
        if (data.source === "real_usage" && data.avg_cost_per_credit > 0) {
          setCalcInputs(prev => ({ ...prev, ai_cost_per_credit: data.avg_cost_per_credit }));
        }
      }
    } catch (e) { /* silent */ }
  }, [token]);

  useEffect(() => {
    fetchAdminData();
  }, []);

  useEffect(() => {
    fetchLiveCost();
    const interval = setInterval(fetchLiveCost, 15000);
    return () => clearInterval(interval);
  }, [fetchLiveCost]);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, agentsRes, txRes, pricingRes, keysRes] = await Promise.all([
        fetch(`${API}/admin/stats`, { headers: authHeaders }),
        fetch(`${API}/admin/users`, { headers: authHeaders }),
        fetch(`${API}/admin/agents`, { headers: authHeaders }),
        fetch(`${API}/admin/transactions`, { headers: authHeaders }),
        fetch(`${API}/admin/pricing`, { headers: authHeaders }),
        fetch(`${API}/admin/api-keys`, { headers: authHeaders })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (usersRes.ok) {
        const data = await usersRes.json();
        setUsers(data.users || data);
      }
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (txRes.ok) {
        const data = await txRes.json();
        setTransactions(data.transactions || data);
      }
      if (pricingRes.ok) {
        const p = await pricingRes.json();
        setPricingConfig(p);
        setPricingEdit(JSON.parse(JSON.stringify(p)));
        setCalcInputs({
          ai_cost_per_credit: p.ai_cost_per_credit || 0.003,
          target_profit_margin: p.target_profit_margin || 200,
          bdt_exchange_rate: p.bdt_exchange_rate || 107
        });
      }
      if (keysRes.ok) {
        const k = await keysRes.json();
        setApiKeysConfig(k);
        setApiKeyInputs(prev => ({...prev, active_provider: k.active_provider || "maars"}));
      }

      const [profitRes, usageRes, avgCostRes, rateRes] = await Promise.all([
        fetch(`${API}/admin/profit`, { headers: authHeaders }),
        fetch(`${API}/admin/api-usage`, { headers: authHeaders }),
        fetch(`${API}/admin/avg-cost`, { headers: authHeaders }),
        fetch(`${API}/exchange-rate`),
      ]);
      if (profitRes.ok) setProfitData(await profitRes.json());
      if (usageRes.ok) setApiUsage(await usageRes.json());
      if (avgCostRes.ok) {
        const avgCost = await avgCostRes.json();
        if (avgCost.source === "real_usage" && avgCost.avg_cost_per_credit > 0) {
          setCalcInputs(prev => ({...prev, ai_cost_per_credit: avgCost.avg_cost_per_credit}));
        }
      }
      if (rateRes.ok) {
        const rateData = await rateRes.json();
        if (rateData.usd_bdt > 0) {
          setCalcInputs(prev => ({...prev, bdt_exchange_rate: rateData.usd_bdt}));
        }
      }
    } catch (error) {
      toast.error("Failed to load admin data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    if (!newAgent.name || !newAgent.role || !newAgent.system_prompt) {
      toast.error("Name, role, and system prompt are required");
      return;
    }
    try {
      const res = await fetch(`${API}/admin/agents`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          ...newAgent,
          capabilities: newAgent.capabilities.split(",").map(c => c.trim()).filter(Boolean)
        })
      });
      if (res.ok) {
        toast.success("Agent created successfully");
        setShowCreateAgent(false);
        setNewAgent({ name: "", description: "", role: "", system_prompt: "", model_provider: "openai", model_name: "gpt-5.2", capabilities: "" });
        fetchAdminData();
      } else {
        const err = await res.json();
        toast.error(err.detail || "Failed to create agent");
      }
    } catch {
      toast.error("Failed to create agent");
    }
  };

  const handleDeleteAgent = async (agentId, agentName) => {
    if (!window.confirm(`Delete agent "${agentName}"? This cannot be undone.`)) return;
    try {
      const res = await fetch(`${API}/admin/agents/${agentId}`, {
        method: "DELETE",
        headers: authHeaders
      });
      if (res.ok) {
        toast.success("Agent deleted");
        fetchAdminData();
      } else {
        toast.error("Failed to delete agent");
      }
    } catch {
      toast.error("Failed to delete agent");
    }
  };

  const tabs = [
    { id: "overview", label: "Overview", icon: Activity },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "gateway", label: "Universal Gateway", icon: Shield },
    { id: "users", label: "Users", icon: Users },
    { id: "agents", label: "Agents", icon: Bot },
    { id: "transactions", label: "Transactions", icon: DollarSign },
    { id: "pricing", label: "Pricing & Packages", icon: TrendingUp },
    { id: "apikeys", label: "API Keys & Integrations", icon: Key },
    { id: "payments", label: "Payment Setup", icon: CreditCard },
    { id: "smtp", label: "Email (SMTP)", icon: Mail },
    { id: "branding", label: "Branding & Domain", icon: Paintbrush },
    { id: "knowledge", label: "Knowledge Base", icon: BookOpen },
    { id: "products", label: "Product Catalog", icon: Package },
    { id: "audit", label: "Audit Log", icon: ScrollText },
    { id: "client-visibility", label: "Client Visibility", icon: Eye },
  ];

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <style>{STYLES}</style>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
          <div style={{ width: 32, height: 32, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
          <p style={{ color: T.zinc, fontSize: 13 }}>Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="admin-dashboard">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
          <Shield size={22} style={{ color: T.indigo }} />
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 28, fontWeight: 700, color: "#fff", margin: 0 }}>Admin Control Panel</h1>
        </div>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Manage your platform, users, agents, and revenue</p>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 3, marginBottom: 24, background: "rgba(255,255,255,.02)", padding: 4, borderRadius: 12, border: `1px solid ${T.border}`, overflowX: "auto" }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            data-testid={`admin-tab-${tab.id}`}
            style={{
              display: "flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600, whiteSpace: "nowrap", transition: "all .2s",
              background: activeTab === tab.id ? `linear-gradient(135deg, ${T.indigo}, ${T.violet})` : "transparent",
              color: activeTab === tab.id ? "#fff" : T.zinc,
            }}
            onMouseEnter={e => { if (activeTab !== tab.id) { e.currentTarget.style.color = "#fff"; e.currentTarget.style.background = "rgba(255,255,255,.05)"; } }}
            onMouseLeave={e => { if (activeTab !== tab.id) { e.currentTarget.style.color = T.zinc; e.currentTarget.style.background = "transparent"; } }}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && <OverviewTab stats={stats} profitData={profitData} apiKeysConfig={apiKeysConfig} />}
      {activeTab === "analytics" && <AnalyticsTab />}
      {activeTab === "gateway" && <UniversalGatewayTab token={token} />}
      {activeTab === "users" && <UsersTab users={users} />}
      {activeTab === "agents" && (
        <AgentsTab
          agents={agents} setAgents={setAgents}
          showCreateAgent={showCreateAgent} setShowCreateAgent={setShowCreateAgent}
          newAgent={newAgent} setNewAgent={setNewAgent}
          handleCreateAgent={handleCreateAgent} handleDeleteAgent={handleDeleteAgent}
          token={token}
        />
      )}
      {activeTab === "transactions" && <TransactionsTab transactions={transactions} />}
      {activeTab === "pricing" && (
        <>
          <PricingManagerTab
            pricingConfig={pricingConfig} setPricingConfig={setPricingConfig}
            pricingEdit={pricingEdit} setPricingEdit={setPricingEdit}
            calcInputs={calcInputs} setCalcInputs={setCalcInputs}
            calcResult={calcResult} setCalcResult={setCalcResult}
            liveCost={liveCost} token={token}
            onDeletePlan={async (planId) => {
              if (!window.confirm(`Delete plan "${planId}"? This cannot be undone.`)) return;
              try {
                const res = await fetch(`${API}/admin/pricing/plans/${planId}`, {
                  method: "DELETE",
                  headers: { Authorization: `Bearer ${token}` },
                });
                if (res.ok) {
                  setPricingEdit(prev => {
                    const plans = { ...prev.plans };
                    delete plans[planId];
                    return { ...prev, plans };
                  });
                  toast.success(`Plan "${planId}" deleted`);
                } else {
                  const err = await res.json();
                  toast.error(err.detail || "Failed to delete plan");
                }
              } catch { toast.error("Failed to delete plan"); }
            }}
            onAddPlan={async (id, planData) => {
              setPricingEdit(prev => ({
                ...prev,
                plans: { ...prev.plans, [id]: planData },
              }));
            }}
          />
          <div style={{ marginTop: 24 }}><CustomPackagesTab /></div>
        </>
      )}
      {activeTab === "apikeys" && (
        <>
          <ApiKeysTab
            apiKeysConfig={apiKeysConfig} apiKeyInputs={apiKeyInputs} setApiKeyInputs={setApiKeyInputs}
            apiUsage={apiUsage} testingKey={testingKey} setTestingKey={setTestingKey}
            token={token} onRefresh={fetchAdminData}
          />
          <div style={{ marginTop: 24 }}><IntegrationsTab /></div>
        </>
      )}
      {activeTab === "payments" && <PaymentSetupTab token={token} />}
      {activeTab === "smtp" && <SmtpConfigTab />}
      {activeTab === "branding" && <BrandingTab />}
      {activeTab === "knowledge" && <KnowledgeBaseTab />}
      {activeTab === "products" && <AdminProductsTab token={token} />}
      {activeTab === "audit" && <AuditLogTab />}
      {activeTab === "client-visibility" && <ClientVisibilityTab />}
    </div>
  );
};


const AdminProductsTab = ({ token }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetch(`${API}/admin/products`, { headers }).then(r => r.json()).then(data => {
      setProducts(data.products || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 128 }}>
      <div style={{ width: 32, height: 32, border: "2px solid #818cf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }} data-testid="admin-products-tab">
      <div>
        <h2 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 20, fontWeight: 700, color: "#fff", margin: 0 }}>Product Catalog (All Users)</h2>
        <p style={{ fontSize: 13, color: "#71717a", marginTop: 4 }}>{products.length} products across all users</p>
      </div>
      <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
              {["Product", "User", "Category", "Generated", "Scanned"].map((h, i) => (
                <th key={h} style={{ padding: "10px 16px", textAlign: i >= 3 ? "right" : "left", fontSize: 11, color: "#71717a", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.product_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)", transition: "background .15s" }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,.03)"}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                <td style={{ padding: "12px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    {p.images?.[0]?.thumbnail ? (
                      <img src={p.images[0].thumbnail} alt="" style={{ width: 40, height: 40, borderRadius: 8, objectFit: "cover" }} onError={e => { e.target.style.display = "none"; }} />
                    ) : (
                      <div style={{ width: 40, height: 40, borderRadius: 8, background: "rgba(255,255,255,.06)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Package size={18} style={{ color: "#52525b" }} />
                      </div>
                    )}
                    <div>
                      <p style={{ color: "#fff", fontWeight: 600, margin: 0 }}>{p.name}</p>
                      {p.brand && <p style={{ color: "#71717a", fontSize: 11, margin: 0 }}>{p.brand}</p>}
                    </div>
                  </div>
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <p style={{ color: "#d4d4d8", fontSize: 12, margin: 0 }}>{p.user_name || "Unknown"}</p>
                  <p style={{ color: "#52525b", fontSize: 10, margin: 0 }}>{p.user_email}</p>
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(129,140,248,.15)", color: "#818cf8" }}>{p.category || "Uncategorized"}</span>
                </td>
                <td style={{ padding: "12px 16px", textAlign: "right", color: "#a1a1aa" }}>{p.generated_count || 0}</td>
                <td style={{ padding: "12px 16px", textAlign: "right", color: "#71717a", fontSize: 11 }}>{p.last_scanned ? new Date(p.last_scanned).toLocaleDateString() : "—"}</td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr><td colSpan="5" style={{ padding: 32, textAlign: "center", color: "#71717a", fontSize: 13 }}>No products saved by any user yet</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;
