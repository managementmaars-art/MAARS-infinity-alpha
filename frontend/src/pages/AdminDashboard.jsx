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
  DollarSign, Activity, UserCheck, Plus, Trash2, ChevronDown, ChevronUp
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [agents, setAgents] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateAgent, setShowCreateAgent] = useState(false);
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
      const [statsRes, usersRes, agentsRes, txRes] = await Promise.all([
        fetch(`${API}/admin/stats`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/users`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/agents`, { credentials: "include", headers: authHeaders }),
        fetch(`${API}/admin/transactions`, { credentials: "include", headers: authHeaders })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (txRes.ok) setTransactions(await txRes.json());
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
            <span className="text-lg font-bold text-white font-['Outfit']">AI Legends Admin</span>
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

  const OverviewTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} icon={Users} color="indigo" />
        <StatCard title="Total Chats" value={stats?.total_chats || 0} icon={MessageSquare} color="violet" />
        <StatCard title="Messages Sent" value={stats?.total_messages || 0} icon={Activity} color="emerald" />
        <StatCard title="Revenue" value={`$${stats?.total_revenue?.toFixed(2) || '0.00'}`} icon={DollarSign} color="amber" />
      </div>

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
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Total Transactions</span>
              <span className="text-white font-semibold">{stats?.total_transactions || 0}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Agents" value={stats?.total_agents || 0} icon={Bot} color="cyan" />
        <StatCard title="Custom Agents" value={stats?.custom_agents || 0} icon={UserCheck} color="pink" />
        <StatCard title="Total Tasks" value={stats?.total_tasks || 0} icon={ListTodo} color="orange" />
        <StatCard title="Subscriptions" value={stats?.active_subscriptions || 0} icon={CreditCard} color="teal" />
      </div>
    </div>
  );

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
          {activeTab === "payments" && <PaymentSetupTab />}
        </div>
      </div>
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
