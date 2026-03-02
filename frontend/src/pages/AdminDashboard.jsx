import { useState, useEffect, useCallback, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import {
  Bot, Users, MessageSquare, CreditCard, TrendingUp, Shield,
  LayoutDashboard, ListTodo, Settings, LogOut, Menu, X,
  DollarSign, Activity, Key, Loader2,
  BarChart3, Mail, Paintbrush, BookOpen, Package, ScrollText
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";
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

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
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
  const [apiKeyInputs, setApiKeyInputs] = useState({ openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: "", active_provider: "emergent" });
  const [testingKey, setTestingKey] = useState(null);
  const [newAgent, setNewAgent] = useState({
    name: "", description: "", role: "", system_prompt: "",
    model_provider: "openai", model_name: "gpt-5.2", capabilities: ""
  });

  // Live cost tracking state - auto-updates in background
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

  // Background polling every 15s for live cost data
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
      if (usersRes.ok) setUsers(await usersRes.json());
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (txRes.ok) setTransactions(await txRes.json());
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
        setApiKeyInputs(prev => ({...prev, active_provider: k.active_provider || "emergent"}));
      }
      
      // Fetch profit data and API usage
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

  const handleLogout = async () => {
    await logout();
    navigate("/");
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
  ];

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active ? "bg-red-500/20 text-red-400" : "text-zinc-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6">
        <Link to="/admin" className="flex items-center gap-2" data-testid="admin-sidebar-logo">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold text-white font-['Outfit']">MAARS Command Admin</span>
            <p className="text-[10px] text-red-400 -mt-1">Control Panel</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <NavItem icon={Shield} label="Admin Panel" to="/admin" active />
        <Separator className="bg-white/10 my-3" />
        <NavItem icon={LayoutDashboard} label="Dashboard" to="/dashboard" />
        <NavItem icon={MessageSquare} label="Chat" to="/chat" />
        <NavItem icon={Users} label="Agents" to="/agents" />
        <NavItem icon={ListTodo} label="Tasks" to="/tasks" />
        <NavItem icon={Settings} label="Settings" to="/settings" />
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.name}</p>
            <p className="text-xs text-red-400 truncate">Administrator</p>
          </div>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start text-zinc-400 hover:text-white hover:bg-white/5 mt-2"
          onClick={handleLogout}
          data-testid="admin-logout-btn"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="admin-dashboard">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-red-500/20">
        <div className="flex items-center justify-between h-16 px-4">
          <Link to="/admin" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white font-['Outfit']">MAARS Admin</span>
          </Link>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-zinc-400" data-testid="admin-mobile-menu">
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-zinc-900 border-r border-white/10">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 bottom-0 w-64 bg-zinc-900/50 border-r border-red-500/10">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-6 lg:p-8 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-6 h-6 text-red-400" />
              <h1 className="text-2xl lg:text-3xl font-bold text-white font-['Outfit']">
                Admin Control Panel
              </h1>
            </div>
            <p className="text-zinc-400">Manage your platform, users, agents, and revenue</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mb-6 bg-zinc-900/50 p-1 rounded-lg border border-white/10 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? "bg-gradient-to-r from-red-500 to-orange-500 text-white"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
                data-testid={`admin-tab-${tab.id}`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === "overview" && <OverviewTab stats={stats} profitData={profitData} apiKeysConfig={apiKeysConfig} />}
          {activeTab === "analytics" && <AnalyticsTab />}
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
              />
              <div className="mt-6"><CustomPackagesTab /></div>
            </>
          )}
          {activeTab === "apikeys" && (
            <>
              <ApiKeysTab
                apiKeysConfig={apiKeysConfig} apiKeyInputs={apiKeyInputs} setApiKeyInputs={setApiKeyInputs}
                apiUsage={apiUsage} testingKey={testingKey} setTestingKey={setTestingKey}
                token={token} onRefresh={fetchAdminData}
              />
              <div className="mt-6"><IntegrationsTab /></div>
            </>
          )}
          {activeTab === "payments" && <PaymentSetupTab token={token} />}
          {activeTab === "smtp" && <SmtpConfigTab />}
          {activeTab === "branding" && <BrandingTab />}
          {activeTab === "knowledge" && <KnowledgeBaseTab />}
          {activeTab === "products" && <AdminProductsTab token={token} />}
          {activeTab === "audit" && <AuditLogTab />}
        </div>
      </div>
      <div className="lg:ml-64"><BrandFooter /></div>
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

  if (loading) return <div className="flex items-center justify-center h-32"><Loader2 className="w-8 h-8 animate-spin text-red-400" /></div>;

  return (
    <div className="space-y-6" data-testid="admin-products-tab">
      <div>
        <h2 className="text-xl font-bold text-white font-['Outfit']">Product Catalog (All Users)</h2>
        <p className="text-zinc-400 text-sm mt-1">{products.length} products across all users</p>
      </div>
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="border-b border-white/10">
              <tr className="text-zinc-500 text-xs">
                <th className="text-left p-4">Product</th>
                <th className="text-left p-4">User</th>
                <th className="text-left p-4">Category</th>
                <th className="text-right p-4">Generated</th>
                <th className="text-right p-4">Scanned</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.product_id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      {p.images?.[0]?.thumbnail ? (
                        <img src={p.images[0].thumbnail} alt="" className="w-10 h-10 rounded-lg object-cover" onError={e => { e.target.style.display = 'none'; }} />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center"><Package className="w-5 h-5 text-zinc-600" /></div>
                      )}
                      <div>
                        <p className="text-white font-medium">{p.name}</p>
                        {p.brand && <p className="text-zinc-500 text-xs">{p.brand}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <p className="text-zinc-300 text-xs">{p.user_name || "Unknown"}</p>
                    <p className="text-zinc-600 text-[10px]">{p.user_email}</p>
                  </td>
                  <td className="p-4"><Badge className="bg-indigo-500/20 text-indigo-300 text-[9px]">{p.category || "Uncategorized"}</Badge></td>
                  <td className="p-4 text-right text-zinc-400">{p.generated_count || 0}</td>
                  <td className="p-4 text-right text-zinc-500 text-xs">{p.last_scanned ? new Date(p.last_scanned).toLocaleDateString() : "-"}</td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr><td colSpan="5" className="p-8 text-center text-zinc-500">No products saved by any user yet</td></tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
};



const StatCard = ({ title, value, icon: Icon, color }) => {
  const colors = {
    indigo: "bg-indigo-500/20 text-indigo-400",
    violet: "bg-violet-500/20 text-violet-400",
    emerald: "bg-emerald-500/20 text-emerald-400",
    amber: "bg-amber-500/20 text-amber-400",
    cyan: "bg-cyan-500/20 text-cyan-400",
    pink: "bg-pink-500/20 text-pink-400",
    orange: "bg-orange-500/20 text-orange-400",
    teal: "bg-teal-500/20 text-teal-400",
  };

  return (
    <Card className="bg-zinc-900/50 border-white/10">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-zinc-400">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AdminDashboard;

