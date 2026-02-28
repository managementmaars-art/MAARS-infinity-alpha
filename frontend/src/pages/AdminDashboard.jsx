import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Separator } from "../components/ui/separator";
import { Textarea } from "../components/ui/textarea";
import {
  Bot, Users, MessageSquare, CreditCard, TrendingUp, Shield,
  LayoutDashboard, ListTodo, Settings, LogOut, Menu, X,
  DollarSign, Activity, UserCheck, Plus, Trash2, ChevronDown, ChevronUp, Key,
  Plug, CheckCircle, XCircle, Loader2, ExternalLink, TestTube
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

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

  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, agentsRes, txRes, pricingRes, keysRes] = await Promise.all([
        fetch(`${API}/admin/stats`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/users`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/agents`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/transactions`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/pricing`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/api-keys`, { credentials: "include", headers: authHeaders })
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
        fetch(`${API}/admin/profit`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/api-usage`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/avg-cost`, { credentials: "include", headers: authHeaders }),
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
        credentials: "include",
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
        credentials: "include",
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
    { id: "users", label: "Users", icon: Users },
    { id: "agents", label: "Agents", icon: Bot },
    { id: "transactions", label: "Transactions", icon: DollarSign },
    { id: "pricing", label: "Pricing & Packages", icon: TrendingUp },
    { id: "apikeys", label: "API Keys & Integrations", icon: Key },
    { id: "payments", label: "Payment Setup", icon: CreditCard },
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

  const OverviewTab = () => {
    const p = profitData;
    const costs = apiKeysConfig?.cost_reference || {};
    return (
    <div className="space-y-6">
      {/* Top stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} icon={Users} color="indigo" />
        <StatCard title="Total Chats" value={stats?.total_chats || 0} icon={MessageSquare} color="violet" />
        <StatCard title="Messages Sent" value={stats?.total_messages || 0} icon={Activity} color="emerald" />
        <StatCard title="Revenue" value={`$${stats?.total_revenue?.toFixed(2) || '0.00'}`} icon={DollarSign} color="amber" />
      </div>

      {/* Subscription Distribution + Credits Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Subscription Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.plan_distribution && Object.keys(stats.plan_distribution).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.plan_distribution).map(([plan, count]) => (
                  <div key={plan} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        plan === 'business' ? 'bg-amber-400' :
                        plan === 'pro' ? 'bg-violet-400' :
                        plan === 'starter' ? 'bg-indigo-400' : 'bg-zinc-400'
                      }`} />
                      <span className="text-zinc-300 capitalize">{plan}</span>
                    </div>
                    <Badge variant="outline" className="border-white/10 text-zinc-300">{count} users</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-zinc-500 text-sm">No subscription data yet</p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Credits Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Total Credits Used</span>
              <span className="text-white font-semibold">{stats?.total_credits_used || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Credits Remaining (All Users)</span>
              <span className="text-white font-semibold">{stats?.total_credits_remaining || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Active Subscriptions</span>
              <span className="text-white font-semibold">{stats?.active_subscriptions || 0}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent/Task stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Agents" value={stats?.total_agents || 0} icon={Bot} color="cyan" />
        <StatCard title="Custom Agents" value={stats?.custom_agents || 0} icon={UserCheck} color="pink" />
        <StatCard title="Total Tasks" value={stats?.total_tasks || 0} icon={ListTodo} color="orange" />
        <StatCard title="Subscriptions" value={stats?.active_subscriptions || 0} icon={CreditCard} color="teal" />
      </div>

      {/* Profit Dashboard */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="profit-dashboard">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Profit Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-xs text-emerald-400 mb-1">Total Revenue</p>
              <p className="text-2xl font-bold text-white">${p?.revenue?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <p className="text-xs text-red-400 mb-1">Total API Cost</p>
              <p className="text-2xl font-bold text-white">${p?.total_api_cost?.toFixed(4) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <p className="text-xs text-amber-400 mb-1">Net Profit</p>
              <p className="text-2xl font-bold text-white">${p?.net_profit?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <p className="text-xs text-indigo-400 mb-1">Profit Margin</p>
              <p className="text-2xl font-bold text-white">{p?.profit_margin_pct?.toFixed(1) || '0'}%</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{p?.total_api_calls?.toLocaleString() || 0}</p>
              <p className="text-[10px] text-zinc-500">API Calls</p>
            </div>
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{((p?.total_input_tokens || 0) / 1000).toFixed(1)}K</p>
              <p className="text-[10px] text-zinc-500">Input Tokens</p>
            </div>
            <div className="text-center p-3 rounded-lg bg-white/5">
              <p className="text-lg font-bold text-white">{((p?.total_output_tokens || 0) / 1000).toFixed(1)}K</p>
              <p className="text-[10px] text-zinc-500">Output Tokens</p>
            </div>
          </div>

          <p className="text-[10px] text-zinc-600">* API costs are estimated based on token usage. Avg cost per call: ${p?.avg_cost_per_call?.toFixed(5) || '0'}</p>
        </CardContent>
      </Card>

      {/* Per-Plan Profit Breakdown */}
      {p?.plan_profits && (
        <Card className="bg-zinc-900/50 border-white/10" data-testid="plan-profit-card">
          <CardHeader>
            <CardTitle className="text-white font-['Outfit'] text-base">Profit Per Plan (if all credits used)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="grid grid-cols-5 gap-2 text-[10px] text-zinc-500 font-medium px-1">
                <span>Plan</span><span>Price</span><span>Est. Max Cost</span><span>Profit</span><span>Margin</span>
              </div>
              {Object.entries(p.plan_profits).map(([plan, data]) => (
                <div key={plan} className="grid grid-cols-5 gap-2 items-center text-sm">
                  <span className="text-white font-medium capitalize">{plan}</span>
                  <span className="text-emerald-400">${data.revenue}</span>
                  <span className="text-red-400">${data.est_max_cost}</span>
                  <span className={`font-semibold ${data.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    ${data.profit}
                  </span>
                  <span className={`text-xs ${(data.margin_pct || 0) >= 50 ? 'text-emerald-400' : (data.margin_pct || 0) >= 0 ? 'text-amber-400' : 'text-red-400'}`}>
                    {data.margin_pct || 0}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Per-Model Cost and Provider Cost */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {p?.model_costs?.length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] text-base">Cost By Model</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {p.model_costs.map((m, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-zinc-300">{m.model}</span>
                    <div className="flex gap-3 text-right">
                      <span className="text-zinc-500 text-xs">{m.calls} calls</span>
                      <span className="text-red-400 font-mono">${m.cost.toFixed(4)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {p?.provider_costs && Object.keys(p.provider_costs).length > 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] text-base">Cost By Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(p.provider_costs).map(([provider, data]) => (
                  <div key={provider} className="p-3 rounded-lg bg-white/5">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-white font-medium capitalize">{provider}</span>
                      <span className="text-red-400 font-mono">${data.cost.toFixed(4)}</span>
                    </div>
                    <div className="flex gap-4 text-[10px] text-zinc-500">
                      <span>{data.calls} calls</span>
                      <span>{(data.input_tokens / 1000).toFixed(1)}K input</span>
                      <span>{(data.output_tokens / 1000).toFixed(1)}K output</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Direct Provider Costs */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="cost-reference-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            Direct Provider Costs
          </CardTitle>
          <p className="text-zinc-500 text-xs mt-1">Reference pricing when using your own API keys. Prices are from provider websites and may change.</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(costs).map(([providerId, data]) => (
              <div key={providerId} className="rounded-lg border border-white/10 overflow-hidden">
                <div className="px-3 py-2 bg-white/5 border-b border-white/10">
                  <span className="text-sm font-semibold text-white capitalize">{providerId}</span>
                  <span className="text-[10px] text-zinc-500 ml-2">{data.unit}</span>
                </div>
                <div className="divide-y divide-white/5">
                  {(data.models || []).map((model, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2 text-xs">
                      <span className="text-zinc-300">{model.name}</span>
                      <div className="flex gap-3 text-right">
                        <span className="text-zinc-500">In: <span className="text-emerald-400">{model.input}</span></span>
                        <span className="text-zinc-500">Out: <span className="text-amber-400">{model.output}</span></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-zinc-600 mt-3">* Emergent Universal Key includes a small markup over direct pricing for convenience and unified billing.</p>
        </CardContent>
      </Card>
    </div>
    );
  };

  const UsersTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">All Users ({users.length})</h2>
      </div>
      <div className="space-y-2">
        {users.map((u) => (
          <Card key={u.user_id} className="bg-zinc-900/50 border-white/10" data-testid={`admin-user-${u.user_id}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                  {u.picture ? (
                    <img src={u.picture} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="text-white font-semibold text-sm">{u.name?.charAt(0) || "?"}</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white truncate">{u.name}</p>
                    {u.is_admin && <Badge className="bg-red-500/20 text-red-400 text-[10px]">Admin</Badge>}
                  </div>
                  <p className="text-sm text-zinc-400 truncate">{u.email}</p>
                </div>
                <div className="text-right shrink-0">
                  <Badge className={`${
                    u.subscription?.plan_id === 'business' ? 'bg-amber-500/20 text-amber-400' :
                    u.subscription?.plan_id === 'pro' ? 'bg-violet-500/20 text-violet-400' :
                    u.subscription?.plan_id === 'starter' ? 'bg-indigo-500/20 text-indigo-400' :
                    'bg-zinc-500/20 text-zinc-400'
                  }`}>
                    {u.subscription?.plan_id || "free"}
                  </Badge>
                  <p className="text-xs text-zinc-500 mt-1">{u.subscription?.credits || 0} credits</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {users.length === 0 && <p className="text-zinc-500 text-center py-8">No users found</p>}
      </div>
    </div>
  );

  const AgentsTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">All Agents ({agents.length})</h2>
        <Button
          onClick={() => setShowCreateAgent(!showCreateAgent)}
          className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
          data-testid="admin-create-agent-btn"
        >
          {showCreateAgent ? <X className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
          {showCreateAgent ? "Cancel" : "Create Agent"}
        </Button>
      </div>

      {showCreateAgent && (
        <Card className="bg-zinc-900/50 border-red-500/20">
          <CardContent className="p-6 space-y-4">
            <h3 className="text-white font-semibold font-['Outfit']">Create New Agent</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-zinc-300">Name</Label>
                <Input
                  value={newAgent.name}
                  onChange={(e) => setNewAgent(p => ({...p, name: e.target.value}))}
                  placeholder="Agent Name"
                  className="bg-zinc-800/50 border-white/10"
                  data-testid="admin-agent-name-input"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-zinc-300">Role</Label>
                <Input
                  value={newAgent.role}
                  onChange={(e) => setNewAgent(p => ({...p, role: e.target.value}))}
                  placeholder="e.g. Data Scientist"
                  className="bg-zinc-800/50 border-white/10"
                  data-testid="admin-agent-role-input"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">Description</Label>
              <Input
                value={newAgent.description}
                onChange={(e) => setNewAgent(p => ({...p, description: e.target.value}))}
                placeholder="Brief description of the agent"
                className="bg-zinc-800/50 border-white/10"
                data-testid="admin-agent-desc-input"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">System Prompt</Label>
              <Textarea
                value={newAgent.system_prompt}
                onChange={(e) => setNewAgent(p => ({...p, system_prompt: e.target.value}))}
                placeholder="You are... (define the agent's personality and instructions)"
                className="bg-zinc-800/50 border-white/10 min-h-[100px]"
                data-testid="admin-agent-prompt-input"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-zinc-300">Model Provider</Label>
                <select
                  value={newAgent.model_provider}
                  onChange={(e) => setNewAgent(p => ({...p, model_provider: e.target.value}))}
                  className="w-full h-10 px-3 rounded-md bg-zinc-800/50 border border-white/10 text-white"
                  data-testid="admin-agent-provider-select"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="xai">xAI (Grok)</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="mistral">Mistral AI</option>
                  <option value="perplexity">Perplexity</option>
                  <option value="cohere">Cohere</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label className="text-zinc-300">Model Name</Label>
                <Input
                  value={newAgent.model_name}
                  onChange={(e) => setNewAgent(p => ({...p, model_name: e.target.value}))}
                  placeholder="gpt-5.2"
                  className="bg-zinc-800/50 border-white/10"
                  data-testid="admin-agent-model-input"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-zinc-300">Capabilities (comma-separated)</Label>
              <Input
                value={newAgent.capabilities}
                onChange={(e) => setNewAgent(p => ({...p, capabilities: e.target.value}))}
                placeholder="Skill 1, Skill 2, Skill 3"
                className="bg-zinc-800/50 border-white/10"
                data-testid="admin-agent-capabilities-input"
              />
            </div>
            <Button
              onClick={handleCreateAgent}
              className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
              data-testid="admin-save-agent-btn"
            >
              Create Agent
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-2">
        {agents.map((agent) => (
          <Card key={agent.agent_id} className="bg-zinc-900/50 border-white/10" data-testid={`admin-agent-${agent.agent_id}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <img src={agent.avatar} alt={agent.name} className="w-12 h-12 rounded-lg object-cover shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white truncate">{agent.name}</p>
                    {agent.is_custom && <Badge className="bg-cyan-500/20 text-cyan-400 text-[10px]">Custom</Badge>}
                  </div>
                  <p className="text-sm text-zinc-400 truncate">{agent.role}</p>
                  <p className="text-xs text-zinc-500 truncate">{agent.model_provider}/{agent.model_name}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10 shrink-0"
                  onClick={() => handleDeleteAgent(agent.agent_id, agent.name)}
                  data-testid={`admin-delete-agent-${agent.agent_id}`}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {agents.length === 0 && <p className="text-zinc-500 text-center py-8">No agents found</p>}
      </div>
    </div>
  );

  const TransactionsTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">Payment Transactions ({transactions.length})</h2>
      </div>
      <div className="space-y-2">
        {transactions.map((tx) => (
          <Card key={tx.transaction_id} className="bg-zinc-900/50 border-white/10" data-testid={`admin-tx-${tx.transaction_id}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                  tx.payment_status === 'paid' ? 'bg-emerald-500/20' : 'bg-zinc-500/20'
                }`}>
                  <DollarSign className={`w-5 h-5 ${tx.payment_status === 'paid' ? 'text-emerald-400' : 'text-zinc-400'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">
                    {tx.metadata?.type === 'subscription' ? `${tx.metadata?.plan_id} Plan` : `${tx.metadata?.credits} Credits`}
                  </p>
                  <p className="text-sm text-zinc-400 truncate">{tx.email}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-semibold text-white">${tx.amount?.toFixed(2)}</p>
                  <Badge className={`text-[10px] ${
                    tx.payment_status === 'paid' ? 'bg-emerald-500/20 text-emerald-400' :
                    tx.payment_status === 'pending' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {tx.payment_status || 'pending'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {transactions.length === 0 && <p className="text-zinc-500 text-center py-8">No transactions yet</p>}
      </div>
    </div>
  );



  const handleSaveApiKeys = async () => {
    try {
      const res = await fetch(`${API}/admin/api-keys`, {
        method: "PUT",
        credentials: "include",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(apiKeyInputs)
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`API keys saved! Using: ${data.active_provider === 'direct' ? 'Direct Provider Keys' : 'Emergent Universal Key'}`);
        fetchAdminData();
        setApiKeyInputs(prev => ({...prev, openai_key: "", anthropic_key: "", gemini_key: "", xai_key: "", deepseek_key: "", mistral_key: "", perplexity_key: "", cohere_key: "", elevenlabs_key: ""}));
      } else {
        toast.error("Failed to save API keys");
      }
    } catch {
      toast.error("Failed to save API keys");
    }
  };

  const handleTestKey = async (provider, key) => {
    if (!key) { toast.error("Enter a key to test"); return; }
    setTestingKey(provider);
    try {
      const res = await fetch(`${API}/admin/api-keys/test`, {
        method: "POST",
        credentials: "include",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: key })
      });
      const data = await res.json();
      if (data.success) {
        toast.success(data.message);
      } else {
        toast.error(data.message);
      }
    } catch {
      toast.error("Test failed");
    } finally {
      setTestingKey(null);
    }
  };

  const ApiKeysTab = () => {
    const costs = apiKeysConfig?.cost_reference || {};
    const usage = apiUsage || {};
    const [integrationStatus, setIntegrationStatus] = useState({});
    
    useEffect(() => {
      if (token) {
        fetch(`${API}/admin/integrations`, { headers: { Authorization: `Bearer ${token}` } })
          .then(r => r.json()).then(data => setIntegrationStatus(data)).catch(() => {});
      }
    }, [token]);
    
    return (
    <div className="space-y-6">
      {/* Provider Status & Usage */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="api-usage-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2 text-base">
            <Activity className="w-5 h-5 text-emerald-400" />
            API Key Status & Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {["openai", "anthropic", "gemini", "xai", "deepseek", "mistral", "perplexity", "cohere", "elevenlabs"].map(provider => {
              const status = usage.providers?.[provider];
              const tracked = usage.tracked_usage?.[provider];
              const providerLabels = { openai: "OpenAI", anthropic: "Anthropic", gemini: "Google Gemini", xai: "xAI (Grok)", deepseek: "DeepSeek", mistral: "Mistral AI", perplexity: "Perplexity", cohere: "Cohere", elevenlabs: "ElevenLabs" };
              const hasKey = status?.status === 'active' || status?.status === 'error';
              return (
                <div key={provider} className="p-3 rounded-lg bg-white/5 border border-white/10" data-testid={`api-status-${provider}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{providerLabels[provider] || provider}</span>
                    <Badge className={status?.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : hasKey ? 'bg-red-500/20 text-red-400' : 'bg-zinc-500/20 text-zinc-400'}>
                      {status?.status || 'no key'}
                    </Badge>
                  </div>
                  {status?.models_available > 0 && (
                    <p className="text-xs text-zinc-400">{status.models_available} models available</p>
                  )}
                  {tracked ? (
                    <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">API Calls</span>
                        <span className="text-white">{tracked.total_calls}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">Tokens Used</span>
                        <span className="text-white">{(tracked.total_tokens / 1000).toFixed(1)}K</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">Est. Cost</span>
                        <span className="text-red-400 font-mono">${tracked.total_cost.toFixed(4)}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-2 pt-2 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500">{hasKey ? '' : 'No key configured'}</p>
                    </div>
                  )}
                  {status?.note && <p className="text-[10px] text-zinc-600 mt-2">{status.note}</p>}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Service Integration Status */}
      <Card className="bg-zinc-900/50 border-white/10" data-testid="integration-status-card">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-2 text-base">
            <Plug className="w-5 h-5 text-violet-400" />
            Service Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.entries(integrationStatus).map(([svcId, svc]) => {
              const costData = {
                slack: { unit: "per message", cost: "$0.00", note: "Free (Bot Token). Slack charges per workspace, not per API call." },
                github: { unit: "per request", cost: "$0.00", note: "Free for public repos. 5,000 req/hr with token." },
                sendgrid: { unit: "per email", cost: "$0.001", note: "Free tier: 100 emails/day. Paid: ~$0.001/email." },
                resend: { unit: "per email", cost: "$0.001", note: "Free tier: 100 emails/day. Paid: ~$0.001/email." },
                twilio: { unit: "per SMS", cost: "$0.0079", note: "~$0.0079/SMS (US). Varies by country." },
                airtable: { unit: "per record", cost: "$0.00", note: "Free tier: 1,000 records. Paid: unlimited." },
                calendly: { unit: "per event", cost: "$0.00", note: "Free tier available. API included in paid plans." },
                giphy: { unit: "per search", cost: "$0.00", note: "Free API. Rate limited to 42 searches/hr." },
                google_suite: { unit: "per request", cost: "$0.00", note: "Free with service account. Quotas apply." },
              };
              const pricing = costData[svcId] || { unit: "per call", cost: "$0.00", note: "" };
              return (
                <div key={svcId} className="p-3 rounded-lg bg-white/5 border border-white/10" data-testid={`integration-status-${svcId}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{svc.name}</span>
                    <Badge className={svc.configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-500/20 text-zinc-400'}>
                      {svc.configured ? 'active' : 'no key'}
                    </Badge>
                  </div>
                  <p className="text-xs text-zinc-400">{svc.description}</p>
                  <div className="mt-2 pt-2 border-t border-white/5 space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-500">Cost {pricing.unit}</span>
                      <span className="text-red-400 font-mono">{pricing.cost}</span>
                    </div>
                    {svc.key_fields?.map(field => (
                      <div key={field} className="flex justify-between text-xs">
                        <span className="text-zinc-500">{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <span className={svc.keys_set?.[field] ? "text-emerald-400" : "text-zinc-600"}>{svc.keys_set?.[field] ? "Set" : "Not set"}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-[10px] text-zinc-600 mt-2">{pricing.note}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Provider Selection */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <Key className="w-5 h-5 text-indigo-400" />
            </div>
            AI Provider Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Choose how to power your AI agents. Use the Emergent Universal Key for convenience, or plug in your own API keys to pay providers directly.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setApiKeyInputs(p => ({...p, active_provider: "emergent"}))}
              className={`p-4 rounded-lg border text-left transition-all ${
                apiKeyInputs.active_provider === "emergent"
                  ? "border-indigo-500 bg-indigo-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
              data-testid="provider-emergent-btn"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${apiKeyInputs.active_provider === "emergent" ? "bg-indigo-400" : "bg-zinc-600"}`} />
                <span className="text-white font-semibold">Emergent Universal Key</span>
              </div>
              <p className="text-xs text-zinc-400">One key for all models. Billed through Emergent.</p>
              {apiKeysConfig?.emergent_key_set && (
                <Badge className="mt-2 bg-emerald-500/20 text-emerald-400 text-[10px]">Active</Badge>
              )}
            </button>

            <button
              onClick={() => setApiKeyInputs(p => ({...p, active_provider: "direct"}))}
              className={`p-4 rounded-lg border text-left transition-all ${
                apiKeyInputs.active_provider === "direct"
                  ? "border-amber-500 bg-amber-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
              data-testid="provider-direct-btn"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${apiKeyInputs.active_provider === "direct" ? "bg-amber-400" : "bg-zinc-600"}`} />
                <span className="text-white font-semibold">Direct Provider Keys</span>
              </div>
              <p className="text-xs text-zinc-400">Your own API keys. Pay OpenAI, Anthropic & Google directly.</p>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Direct API Keys Input */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">
            {apiKeyInputs.active_provider === "direct" ? "Enter Your API Keys" : "Direct API Keys (Optional Backup)"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { id: "openai", name: "OpenAI", url: "https://platform.openai.com/api-keys", color: "emerald", set: apiKeysConfig?.openai_key_set, masked: apiKeysConfig?.openai_key },
            { id: "anthropic", name: "Anthropic", url: "https://console.anthropic.com/settings/keys", color: "orange", set: apiKeysConfig?.anthropic_key_set, masked: apiKeysConfig?.anthropic_key },
            { id: "gemini", name: "Google Gemini", url: "https://aistudio.google.com/apikey", color: "blue", set: apiKeysConfig?.gemini_key_set, masked: apiKeysConfig?.gemini_key },
            { id: "xai", name: "xAI (Grok)", url: "https://console.x.ai/", color: "zinc", set: apiKeysConfig?.xai_key_set, masked: apiKeysConfig?.xai_key },
            { id: "deepseek", name: "DeepSeek", url: "https://platform.deepseek.com/api_keys", color: "cyan", set: apiKeysConfig?.deepseek_key_set, masked: apiKeysConfig?.deepseek_key },
            { id: "mistral", name: "Mistral AI", url: "https://console.mistral.ai/api-keys/", color: "violet", set: apiKeysConfig?.mistral_key_set, masked: apiKeysConfig?.mistral_key },
            { id: "perplexity", name: "Perplexity", url: "https://www.perplexity.ai/settings/api", color: "teal", set: apiKeysConfig?.perplexity_key_set, masked: apiKeysConfig?.perplexity_key },
            { id: "cohere", name: "Cohere", url: "https://dashboard.cohere.com/api-keys", color: "pink", set: apiKeysConfig?.cohere_key_set, masked: apiKeysConfig?.cohere_key },
            { id: "elevenlabs", name: "ElevenLabs (TTS)", url: "https://elevenlabs.io/app/settings/api-keys", color: "yellow", set: apiKeysConfig?.elevenlabs_key_set, masked: apiKeysConfig?.elevenlabs_key },
          ].map((provider) => (
            <div key={provider.id} className="p-4 rounded-lg bg-white/5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full bg-${provider.color}-400`} />
                  <span className="text-white font-medium">{provider.name}</span>
                  {provider.set && <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Saved: {provider.masked}</Badge>}
                </div>
                <a href={provider.url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline">Get key</a>
              </div>
              <div className="flex gap-2">
                <Input
                  type="password"
                  value={apiKeyInputs[`${provider.id}_key`]}
                  onChange={(e) => setApiKeyInputs(p => ({...p, [`${provider.id}_key`]: e.target.value}))}
                  placeholder={provider.set ? "Enter new key to replace..." : `sk-... or your ${provider.name} API key`}
                  className="bg-zinc-800/50 border-white/10 text-sm font-mono"
                  data-testid={`apikey-${provider.id}-input`}
                />
                <Button
                  variant="outline"
                  size="sm"
                  className="border-white/10 shrink-0"
                  onClick={() => handleTestKey(provider.id, apiKeyInputs[`${provider.id}_key`])}
                  disabled={!apiKeyInputs[`${provider.id}_key`] || testingKey === provider.id}
                  data-testid={`test-${provider.id}-btn`}
                >
                  {testingKey === provider.id ? "Testing..." : "Test"}
                </Button>
              </div>
            </div>
          ))}

          <div className="flex gap-3 pt-2">
            <Button
              onClick={handleSaveApiKeys}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
              data-testid="save-apikeys-btn"
            >
              Save Configuration
            </Button>
          </div>

          {apiKeyInputs.active_provider === "direct" && (
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <p className="text-amber-300 text-sm">
                <strong>Direct mode:</strong> AI calls will use your provider keys. If a key is missing for a provider, it falls back to Emergent key. Make sure at least one key is set per provider you use.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* End of API Keys section */}
    </div>
    );
  };


  const handleCalculate = async () => {
    try {
      const res = await fetch(`${API}/admin/pricing/calculate`, {
        method: "POST",
        credentials: "include",
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
        credentials: "include",
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
          [field]: typeof prev.plans[planId][field] === 'number' ? parseFloat(value) || 0 : value
        }
      }
    }));
  };

  const PricingManagerTab = () => {
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
          <p className="text-zinc-400 text-sm">Set your target margin and apply it to all pricing — plan prices and credit packs update instantly.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label className="text-zinc-300 text-sm">AI Cost per Credit (USD)</Label>
              <div
                className="flex items-center h-10 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-zinc-300 font-mono"
                data-testid="calc-cost-display"
              >
                ${(calcInputs.ai_cost_per_credit || 0).toFixed(4)}
              </div>
              <p className="text-[10px] text-zinc-500">Auto-populated from real usage data</p>
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
            {Object.entries(pricingEdit.plans).filter(([id]) => id !== 'free').map(([planId, plan]) => {
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
                    </div>
                  </div>

                  {/* Per-plan margin control */}
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

                  <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">AI Cost/Credit</Label>
                      <div
                        className="flex items-center h-9 px-3 rounded-md bg-zinc-800/80 border border-white/5 text-sm text-zinc-400 font-mono"
                        data-testid={`ai-cost-${planId}`}
                      >
                        ${(calcInputs.ai_cost_per_credit || 0).toFixed(4)}
                      </div>
                      <p className="text-[10px] text-zinc-500">Auto from usage data</p>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Sell Price USD</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={plan.price_usd}
                        onChange={(e) => updatePlanField(planId, 'price_usd', e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                        data-testid={`edit-${planId}-usd`}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Sell Price BDT</Label>
                      <Input
                        type="number"
                        value={plan.price_bdt}
                        onChange={(e) => updatePlanField(planId, 'price_bdt', e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                        data-testid={`edit-${planId}-bdt`}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Credits</Label>
                      <Input
                        type="number"
                        value={plan.credits}
                        onChange={(e) => updatePlanField(planId, 'credits', e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                        data-testid={`edit-${planId}-credits`}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Max Agents</Label>
                      <Input
                        type="number"
                        value={plan.max_agents}
                        onChange={(e) => updatePlanField(planId, 'max_agents', e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                        data-testid={`edit-${planId}-agents`}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-zinc-400 text-xs">Custom Agents</Label>
                      <Input
                        type="number"
                        value={plan.max_custom_agents}
                        onChange={(e) => updatePlanField(planId, 'max_custom_agents', e.target.value)}
                        className="bg-zinc-800/50 border-white/10 h-9 text-sm"
                        data-testid={`edit-${planId}-custom`}
                      />
                      <p className="text-[10px] text-zinc-500">-1 = unlimited</p>
                    </div>
                  </div>

                  {/* Cost breakdown bar */}
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


  const PaymentSetupTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white font-['Outfit']">Payment Gateway Setup</h2>
        <Badge className="bg-amber-500/20 text-amber-400">Configuration Guide</Badge>
      </div>

      {/* Stripe Setup */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-violet-400" />
            </div>
            Stripe (Global Payments - USD & International Cards)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Stripe handles all international card payments, subscriptions, and credit purchases. Supports 135+ currencies including USD.</p>

          <div className="space-y-3">
            <h4 className="text-white font-semibold text-sm">Setup Steps:</h4>
            <div className="space-y-2">
              {[
                { step: "1", text: "Create a Stripe account", link: "https://dashboard.stripe.com/register" },
                { step: "2", text: "Go to Developers > API Keys in your Stripe Dashboard" },
                { step: "3", text: "Copy your Secret Key (sk_live_...) - keep this private!" },
                { step: "4", text: "Replace STRIPE_API_KEY in your backend .env file with the live key" },
                { step: "5", text: "Create Products/Prices matching your plans (Starter $29, Pro $79, Business $199)" },
                { step: "6", text: "Set up Webhook endpoint: yourdomain.com/api/stripe-webhook" },
                { step: "7", text: "In Webhook settings, listen for: checkout.session.completed, customer.subscription.updated" },
              ].map((item) => (
                <div key={item.step} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                  <div className="w-6 h-6 rounded-full bg-violet-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-violet-400">{item.step}</span>
                  </div>
                  <div>
                    <p className="text-zinc-300 text-sm">{item.text}</p>
                    {item.link && (
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-violet-400 text-xs hover:underline">{item.link}</a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <p className="text-emerald-300 text-sm">
              <strong>Tip:</strong> Use Stripe's test mode (sk_test_...) first to verify everything works, then switch to live keys when ready to accept real payments.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Bangladesh Payments */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-emerald-400" />
            </div>
            Bangladesh Payments (BDT)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-zinc-400 text-sm">Options for accepting payments from Bangladesh in BDT:</p>

          <div className="space-y-3">
            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 1: Stripe Multi-Currency (Recommended)
                <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Easiest</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">Stripe can accept BDT payments if you enable multi-currency in your Stripe dashboard. Funds are converted and deposited in your bank currency.</p>
              <ul className="text-zinc-400 text-sm space-y-1 ml-4 list-disc">
                <li>Go to Stripe Dashboard &gt; Settings &gt; Payments &gt; Currencies</li>
                <li>Enable BDT (Bangladeshi Taka)</li>
                <li>Customers see prices in BDT, you receive in your local currency</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 2: SSLCommerz (Bangladesh Gateway)
                <Badge className="bg-indigo-500/20 text-indigo-400 text-[10px]">Local</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">SSLCommerz is Bangladesh's leading payment gateway. Supports Bangladeshi bank cards, Visa/Mastercard, and mobile banking (Nagad, Rocket).</p>
              <ul className="text-zinc-400 text-sm space-y-1 ml-4 list-disc">
                <li>Register at <a href="https://www.sslcommerz.com" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">sslcommerz.com</a></li>
                <li>Requires Bangladeshi business trade license</li>
                <li>Can be managed remotely from abroad</li>
                <li>Supports bank transfer, cards, and mobile wallets</li>
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-white/5 space-y-2">
              <h4 className="text-white font-semibold text-sm flex items-center gap-2">
                Option 3: Paddle / Payoneer
                <Badge className="bg-amber-500/20 text-amber-400 text-[10px]">International</Badge>
              </h4>
              <p className="text-zinc-400 text-sm">If Stripe isn't available in your region, Paddle or Payoneer can act as a Merchant of Record, handling payments globally and paying you via bank transfer.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Environment Variables */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">Environment Variables (.env)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-zinc-400 text-sm">Update these in your backend <code className="text-violet-400 bg-violet-500/10 px-1.5 py-0.5 rounded">.env</code> file:</p>
          <div className="p-4 rounded-lg bg-zinc-950 font-mono text-sm space-y-2">
            <p className="text-zinc-500"># Stripe (replace with your live keys)</p>
            <p className="text-emerald-400">STRIPE_API_KEY=sk_live_your_stripe_secret_key</p>
            <p className="text-emerald-400">STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret</p>
            <p className="text-zinc-500 mt-3"># MongoDB (already configured)</p>
            <p className="text-zinc-600">MONGO_URL=mongodb://localhost:27017</p>
          </div>
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-red-300 text-sm">
              <strong>Important:</strong> Never share your secret keys publicly. After updating .env, restart the backend service for changes to take effect.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Current Pricing Summary */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] text-base">Your Pricing Structure (200% Profit Margin)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 text-zinc-400 font-medium">Plan</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">USD</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">BDT</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">Credits</th>
                  <th className="text-right py-2 text-zinc-400 font-medium">Custom Agents</th>
                </tr>
              </thead>
              <tbody className="text-zinc-300">
                <tr className="border-b border-white/5"><td className="py-2">Free</td><td className="text-right">$0</td><td className="text-right">$0</td><td className="text-right">50</td><td className="text-right">0</td></tr>
                <tr className="border-b border-white/5"><td className="py-2">Starter</td><td className="text-right">$29</td><td className="text-right">3,100</td><td className="text-right">500</td><td className="text-right">2</td></tr>
                <tr className="border-b border-white/5"><td className="py-2">Pro</td><td className="text-right">$79</td><td className="text-right">8,400</td><td className="text-right">2,000</td><td className="text-right">5</td></tr>
                <tr><td className="py-2">Business</td><td className="text-right">$199</td><td className="text-right">21,100</td><td className="text-right">6,000</td><td className="text-right">Unlimited</td></tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
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
          {activeTab === "overview" && <OverviewTab />}
          {activeTab === "users" && <UsersTab />}
          {activeTab === "agents" && <AgentsTab />}
          {activeTab === "transactions" && <TransactionsTab />}
          {activeTab === "pricing" && <><PricingManagerTab /><div className="mt-6"><CustomPackagesTab /></div></>}
          {activeTab === "apikeys" && <><ApiKeysTab /><div className="mt-6"><IntegrationsTab /></div></>}
          {activeTab === "payments" && <PaymentSetupTab />}
        </div>
      </div>
      <div className="lg:ml-64"><BrandFooter /></div>
    </div>
  );
};

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

  const fetchConfig = async () => {
    try {
      const [res1, res2, res3, res4] = await Promise.all([
        fetch(`${API}/admin/custom-package`, { headers, credentials: "include" }),
        fetch(`${API}/admin/credit-packages`, { headers, credentials: "include" }),
        fetch(`${API}/admin/avg-cost`, { headers, credentials: "include" }),
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
          credentials: "include", body: JSON.stringify(config)
        }),
        fetch(`${API}/admin/credit-packages`, {
          method: "POST", headers: { ...headers, "Content-Type": "application/json" },
          credentials: "include", body: JSON.stringify({ packages: extraPacks })
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
      // Auto-sync BDT when USD changes
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
      // Auto-sync BDT when USD changes
      if (field === "price_usd") {
        packs[index].price_bdt = Math.round((parseFloat(value) || 0) * bdtRate);
      }
      return packs;
    });
  };

  // Auto-apply target margin to all credit presets and extra packs
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
    // Also sync agent/commander BDT
    if (config) {
      setConfig(prev => ({
        ...prev,
        per_agent_price_bdt: Math.round(prev.per_agent_price_usd * bdtRate),
        commander_addon_price_bdt: Math.round(prev.commander_addon_price_usd * bdtRate),
      }));
    }
    toast.success(`Applied ${targetMargin}% margin & synced BDT at rate ${bdtRate}`);
  };

  // Sync all BDT prices when rate changes
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

      {/* Custom Packages Profit Margin Calculator */}
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
              <Input type="number" step="0.001" value={avgCost} readOnly
                className="bg-zinc-800/50 border-white/10 text-zinc-400" data-testid="pkg-calc-cost" />
              <p className="text-[10px] text-zinc-500">From real usage data (read-only)</p>
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

      {/* Agent & Commander Pricing */}
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

      {/* Credit Presets (Build Your Own) */}
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

      {/* Extra Credit Packs (Need More Credits?) */}
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
                <div className="bg-zinc-800/80 border border-white/5 rounded-lg px-3 py-2 text-zinc-400 text-sm font-mono"
                  data-testid={`ai-cost-credit-pack-${i}`}>
                  ${avgCost.toFixed(4)}
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
        className="bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 w-full"
        data-testid="save-custom-config-btn">
        {saving ? "Saving..." : "Save All Pricing"}
      </Button>
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

// ============== INTEGRATIONS TAB ==============
const IntegrationsTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const [integrations, setIntegrations] = useState({});
  const [inputs, setInputs] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const serviceIcons = {
    slack: "https://cdn.simpleicons.org/slack/E01E5A",
    github: "https://cdn.simpleicons.org/github/white",
    sendgrid: "https://cdn.simpleicons.org/sendgrid/1A82E2",
    resend: "https://cdn.simpleicons.org/resend/white",
    twilio: "https://cdn.simpleicons.org/twilio/F22F46",
    airtable: "https://cdn.simpleicons.org/airtable/18BFFF",
    calendly: "https://cdn.simpleicons.org/calendly/006BFF",
    giphy: "https://cdn.simpleicons.org/giphy/black",
    google_suite: "https://cdn.simpleicons.org/google/4285F4",
  };

  const keyLabels = {
    bot_token: "Bot Token",
    personal_access_token: "Personal Access Token",
    api_key: "API Key",
    account_sid: "Account SID",
    auth_token: "Auth Token",
    phone_number: "Phone Number",
    service_account_json: "Service Account JSON",
  };

  useEffect(() => {
    fetch(`${API}/admin/integrations`, { headers }).then(r => r.json()).then(data => {
      setIntegrations(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {};
      for (const [svcId, fields] of Object.entries(inputs)) {
        const hasValue = Object.values(fields).some(v => v && v.trim());
        if (hasValue) payload[svcId] = fields;
      }
      if (Object.keys(payload).length === 0) {
        toast.info("No changes to save");
        setSaving(false);
        return;
      }
      const resp = await fetch(`${API}/admin/integrations`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        toast.success("Integration keys saved!");
        setInputs({});
        const data = await fetch(`${API}/admin/integrations`, { headers }).then(r => r.json());
        setIntegrations(data);
      } else toast.error("Failed to save");
    } catch { toast.error("Save failed"); }
    setSaving(false);
  };

  const handleTest = async (svcId) => {
    setTesting(prev => ({ ...prev, [svcId]: true }));
    try {
      const resp = await fetch(`${API}/admin/integrations/test/${svcId}`, { headers });
      const data = await resp.json();
      setTestResults(prev => ({ ...prev, [svcId]: data }));
      if (data.status === "active") toast.success(`${integrations[svcId]?.name}: Connected!`);
      else toast.error(`${integrations[svcId]?.name}: ${data.message}`);
    } catch { toast.error("Test failed"); }
    setTesting(prev => ({ ...prev, [svcId]: false }));
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-red-400" /></div>;

  return (
    <div className="space-y-6" data-testid="integrations-tab">
      {/* Service Integrations - same style as API Keys */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <Plug className="w-5 h-5 text-violet-400" />
            </div>
            Service Integrations
          </CardTitle>
          <p className="text-zinc-400 text-sm">Configure third-party services your AI agents can use as tools (Slack, GitHub, Email, SMS, etc.)</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(integrations).map(([svcId, svc]) => {
            const docUrls = {
              slack: "https://api.slack.com/apps", github: "https://github.com/settings/tokens",
              sendgrid: "https://app.sendgrid.com/settings/api_keys", resend: "https://resend.com/api-keys",
              twilio: "https://console.twilio.com/", airtable: "https://airtable.com/create/tokens",
              calendly: "https://calendly.com/integrations/api_webhooks", giphy: "https://developers.giphy.com/dashboard/",
              google_suite: "https://console.cloud.google.com/iam-admin/serviceaccounts"
            };
            return (
              <div key={svcId} className="p-4 rounded-lg bg-white/5 space-y-3" data-testid={`integration-card-${svcId}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <img src={serviceIcons[svcId]} alt={svc.name} className="w-5 h-5" onError={(e) => { e.target.style.display = 'none'; }} />
                    <span className="text-white font-medium">{svc.name}</span>
                    <span className="text-xs text-zinc-500 hidden sm:inline">— {svc.description}</span>
                    {svc.configured && <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">Active</Badge>}
                  </div>
                  <a href={docUrls[svcId] || "#"} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline">Get key</a>
                </div>
                {svc.key_fields?.map(field => (
                  <div key={field} className="flex gap-2">
                    <Input
                      type="password"
                      value={inputs[svcId]?.[field] || ""}
                      onChange={e => setInputs(prev => ({ ...prev, [svcId]: { ...prev[svcId], [field]: e.target.value } }))}
                      placeholder={svc.keys_set?.[field] ? `${keyLabels[field] || field}: ******** (saved)` : `Enter ${keyLabels[field] || field}`}
                      className="bg-zinc-800/50 border-white/10 text-sm font-mono"
                      data-testid={`integration-input-${svcId}-${field}`}
                    />
                    {svc.key_fields.indexOf(field) === svc.key_fields.length - 1 && (
                      <Button
                        variant="outline" size="sm" className="border-white/10 shrink-0"
                        onClick={() => handleTest(svcId)}
                        disabled={testing[svcId] || !svc.configured}
                        data-testid={`test-integration-${svcId}`}
                      >
                        {testing[svcId] ? "Testing..." : "Test"}
                      </Button>
                    )}
                  </div>
                ))}
                {testResults[svcId] && (
                  <p className={`text-xs ${testResults[svcId].status === 'active' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {testResults[svcId].status === 'active' ? 'Connected successfully' : testResults[svcId].message?.slice(0, 60)}
                  </p>
                )}
              </div>
            );
          })}

          <div className="flex gap-3 pt-2">
            <Button onClick={handleSave} disabled={saving}
              className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
              data-testid="save-integrations-btn">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plug className="w-4 h-4 mr-2" />}
              Save Integrations
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-4">
          <h3 className="text-white font-medium mb-2">How Integrations Work</h3>
          <ul className="text-sm text-zinc-400 space-y-1">
            <li>1. Add API keys for the services you want to enable</li>
            <li>2. AI agents automatically gain access to configured integrations as tools</li>
            <li>3. Agents use tools when relevant (e.g., send_email, send_slack, github_action)</li>
            <li>4. Unconfigured integrations are hidden from agents until keys are added</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
