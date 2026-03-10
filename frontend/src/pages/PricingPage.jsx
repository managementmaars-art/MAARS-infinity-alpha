import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
import { Bot, Check, Sparkles, Zap, Crown, Building, CreditCard,
  ArrowLeft, Loader2, Globe, Package, Plus, X, Shield, Edit2, Save
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";
import { Input } from "../components/ui/input";

const PricingPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [currentPlan, setCurrentPlan] = useState("free");
  const [credits, setCredits] = useState(0);
  const [processingPlan, setProcessingPlan] = useState(null);
  const [currency, setCurrency] = useState("usd");
  const [dynamicPlans, setDynamicPlans] = useState(null);
  const [adminEditing, setAdminEditing] = useState(false);
  const [editingPlanId, setEditingPlanId] = useState(null);
  const [editData, setEditData] = useState(null);
  const [savingPlan, setSavingPlan] = useState(false);
  const [showNewPlan, setShowNewPlan] = useState(false);
  const [newPlan, setNewPlan] = useState({ plan_id: "", name: "", price_usd: 0, price_bdt: 0, credits: 0, max_agents: 0, max_custom_agents: 0, includes_commander: false, max_team_members: 1, features: [] });
  const [newFeatureText, setNewFeatureText] = useState("");

  // Custom package state
  const [agents, setAgents] = useState([]);
  const [customConfig, setCustomConfig] = useState(null);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [selectedCredit, setSelectedCredit] = useState(null);
  const [includeCommander, setIncludeCommander] = useState(false);
  const [customLoading, setCustomLoading] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const isAdmin = user?.is_admin;

  const startEdit = (planId, plan) => {
    setEditingPlanId(planId);
    setEditData({ ...plan });
  };

  const cancelEdit = () => { setEditingPlanId(null); setEditData(null); };

  const saveEdit = async () => {
    setSavingPlan(true);
    try {
      const updatedPlans = { ...dynamicPlans, [editingPlanId]: editData };
      const res = await fetch(`${API}/admin/pricing`, {
        method: "PUT", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ plans: updatedPlans })
      });
      if (res.ok) { toast.success("Plan updated"); fetchPlans(); cancelEdit(); }
      else toast.error("Failed to update");
    } catch { toast.error("Failed to update"); }
    setSavingPlan(false);
  };

  const deletePlan = async (planId) => {
    if (planId === "free") { toast.error("Cannot delete free plan"); return; }
    if (!window.confirm(`Delete "${dynamicPlans[planId]?.name}" plan?`)) return;
    setSavingPlan(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans/${planId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Plan deleted"); fetchPlans(); }
      else toast.error("Failed to delete");
    } catch { toast.error("Failed"); }
    setSavingPlan(false);
  };

  const createNewPlan = async () => {
    if (!newPlan.plan_id || !newPlan.name) { toast.error("ID and name required"); return; }
    setSavingPlan(true);
    try {
      const res = await fetch(`${API}/admin/pricing/plans`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(newPlan)
      });
      if (res.ok) { toast.success(`Plan "${newPlan.name}" created`); setShowNewPlan(false); setNewPlan({ plan_id: "", name: "", price_usd: 0, price_bdt: 0, credits: 0, max_agents: 0, max_custom_agents: 0, includes_commander: false, max_team_members: 1, features: [] }); fetchPlans(); }
      else { const err = await res.json(); toast.error(err.detail || "Failed"); }
    } catch { toast.error("Failed"); }
    setSavingPlan(false);
  };

  const icons = { free: <Sparkles className="w-6 h-6" />, starter: <Zap className="w-6 h-6" />, pro: <Crown className="w-6 h-6" />, business: <Building className="w-6 h-6" /> };

  const defaultPlans = [
    {
      id: "free",
      name: "Free",
      price_usd: 0,
      price_bdt: 0,
      credits: 50,
      icon: <Sparkles className="w-6 h-6" />,
      features: ["3 AI agents", "50 credits/month", "Basic chat & tasks", "1 LLM provider", "Community support"],
      popular: false
    },
    {
      id: "starter",
      name: "Starter",
      price_usd: 29,
      price_bdt: 3100,
      credits: 500,
      icon: <Zap className="w-6 h-6" />,
      features: ["10 AI agents", "500 credits/month", "2 custom agents", "5 LLM providers", "Vibe Coding & Content Generator", "Voice commands", "Team (up to 3)", "Priority support", "File uploads"],
      popular: false
    },
    {
      id: "pro",
      name: "Pro",
      price_usd: 79,
      price_bdt: 8400,
      credits: 2000,
      icon: <Crown className="w-6 h-6" />,
      features: ["25 AI agents + Commander Orion", "2,000 credits/month", "5 custom agents", "All 13 LLM providers (45+ models)", "Autonomous orchestration", "Quality control & auto-learning", "Memory governance", "Real-time activity monitor", "Reference intelligence", "Team (up to 10)", "Unlimited uploads"],
      popular: true
    },
    {
      id: "business",
      name: "Business",
      price_usd: 199,
      price_bdt: 21100,
      credits: 6000,
      icon: <Building className="w-6 h-6" />,
      features: ["All 458+ AI agents + Commander Orion ∞", "6,000 credits/month", "Unlimited custom agents", "All 13 LLM providers (45+ models)", "Full autonomous orchestration", "All 27 agent networks", "MAARS Kernel & Task Graphs", "KPI dashboard & collaboration engine", "Admin code explorer", "Unlimited team members", "Dedicated support", "API access"],
      popular: false
    }
  ];

  const [creditPackages, setCreditPackages] = useState([
    { id: "credits_100", credits: 100, price_usd: 6, price_bdt: 640 },
    { id: "credits_300", credits: 300, price_usd: 18, price_bdt: 1910 },
    { id: "credits_700", credits: 700, price_usd: 42, price_bdt: 4450 },
    { id: "credits_1500", credits: 1500, price_usd: 90, price_bdt: 9540 }
  ]);

  const formatPrice = (plan) => {
    if (currency === "bdt") {
      return `৳${plan.price_bdt.toLocaleString()}`;
    }
    return `$${plan.price_usd}`;
  };

  const formatCreditPrice = (pkg) => {
    if (currency === "bdt") {
      return `৳${pkg.price_bdt.toLocaleString()}`;
    }
    return `$${pkg.price_usd}`;
  };

  useEffect(() => {
    if (user) {
      fetchSubscription();
    }
    fetchPlans();
    fetchAgents();
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (timezone === "Asia/Dhaka") {
      setCurrency("bdt");
    }
  }, [user]);

  const fetchPlans = async () => {
    try {
      const res = await fetch(`${API}/plans`);
      if (res.ok) {
        const data = await res.json();
        setDynamicPlans(data.plans);
        if (data.custom_package) setCustomConfig(data.custom_package);
        if (data.credit_packages) {
          const pkgs = Object.entries(data.credit_packages).map(([id, p]) => ({ id, ...p }));
          if (pkgs.length > 0) setCreditPackages(pkgs);
        }
      }
    } catch {}
  };

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API}/agents/public`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data.filter(a => !a.is_commander));
      }
    } catch {}
  };

  const plans = dynamicPlans ? Object.entries(dynamicPlans).map(([id, p]) => ({
    id,
    name: p.name,
    price_usd: p.price_usd,
    price_bdt: p.price_bdt,
    credits: p.credits,
    icon: icons[id] || <Sparkles className="w-6 h-6" />,
    features: p.features || [],
    popular: id === "pro"
  })) : defaultPlans;

  const fetchSubscription = async () => {
    try {
      const response = await fetch(`${API}/subscription`, { headers
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(data.plan_id || "free");
        setCredits(data.credits || 0);
      }
    } catch (error) {
      console.error("Failed to fetch subscription");
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      navigate("/register");
      return;
    }

    if (planId === "free") {
      toast.info("You're already on the free plan");
      return;
    }

    setProcessingPlan(planId);
    setLoading(true);

    try {
      const response = await fetch(`${API}/checkout`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({
          type: "subscription",
          plan_id: planId,
          origin_url: window.location.origin,
          currency: currency
        })
      });

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.checkout_url;
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create checkout");
      }
    } catch (error) {
      toast.error("Failed to process subscription");
    } finally {
      setLoading(false);
      setProcessingPlan(null);
    }
  };

  const handleBuyCredits = async (packageId) => {
    if (!user) {
      navigate("/register");
      return;
    }

    setProcessingPlan(packageId);
    setLoading(true);

    try {
      const response = await fetch(`${API}/checkout`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({
          type: "credits",
          package_id: packageId,
          origin_url: window.location.origin,
          currency: currency
        })
      });

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.checkout_url;
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create checkout");
      }
    } catch (error) {
      toast.error("Failed to process purchase");
    } finally {
      setLoading(false);
      setProcessingPlan(null);
    }
  };

  // Custom package helpers
  const toggleAgent = (agentId) => {
    setSelectedAgents(prev => 
      prev.includes(agentId) ? prev.filter(id => id !== agentId) : [...prev, agentId]
    );
  };

  const priceKey = currency === "bdt" ? "price_bdt" : "price_usd";
  const agentPriceKey = currency === "bdt" ? "per_agent_price_bdt" : "per_agent_price_usd";
  const commanderPriceKey = currency === "bdt" ? "commander_addon_price_bdt" : "commander_addon_price_usd";
  const currSymbol = currency === "bdt" ? "৳" : "$";

  const customTotal = customConfig ? (
    (selectedAgents.length * (customConfig[agentPriceKey] || 0)) +
    (selectedCredit ? (customConfig.credit_presets?.find(p => p.id === selectedCredit)?.[priceKey] || 0) : 0) +
    (includeCommander ? (customConfig[commanderPriceKey] || 0) : 0)
  ) : 0;

  const handleCustomCheckout = async () => {
    if (!user) { navigate("/register"); return; }
    if (selectedAgents.length === 0) { toast.error("Select at least one agent"); return; }
    if (!selectedCredit) { toast.error("Select a credit package"); return; }

    setCustomLoading(true);
    try {
      const response = await fetch(`${API}/custom-package/checkout`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({
          selected_agents: selectedAgents,
          credit_preset_id: selectedCredit,
          include_commander: includeCommander,
          origin_url: window.location.origin,
          currency
        })
      });
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.checkout_url;
      } else {
        const error = await response.json();
        toast.error(error.detail || "Checkout failed");
      }
    } catch { toast.error("Checkout failed"); }
    finally { setCustomLoading(false); }
  };

  return (
    <div className="min-h-screen bg-background" data-testid="pricing-page">
      {/* Header */}
      <nav className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2.5">
              <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-8 h-8 rounded-lg object-cover ring-1 ring-indigo-500/20" />
              <span className="text-lg font-bold text-white font-['Outfit']">MAARS Command</span>
            </Link>
            {user ? (
              <Button onClick={() => navigate("/dashboard")} variant="outline" className="border-white/10">
                Dashboard
              </Button>
            ) : (
              <div className="flex gap-3">
                <Button onClick={() => navigate("/login")} variant="ghost">Login</Button>
                <Button onClick={() => navigate("/register")} className="bg-gradient-to-r from-indigo-500 to-violet-500">
                  Get Started
                </Button>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Back link for logged in users */}
        {user && (
          <Link to="/settings" className="inline-flex items-center gap-2 text-zinc-400 hover:text-white mb-6">
            <ArrowLeft className="w-4 h-4" /> Back to Settings
          </Link>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
            Choose Your Plan
          </h1>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto mb-6">
            Get access to your AI team with flexible pricing. Start free, upgrade anytime.
          </p>
          
          {/* Currency Toggle */}
          <div className="inline-flex items-center gap-4 px-4 py-3 rounded-lg bg-zinc-900/50 border border-white/10">
            <Globe className="w-4 h-4 text-zinc-400" />
            <div className="flex items-center gap-2">
              <span className={`text-sm ${currency === "usd" ? "text-white" : "text-zinc-500"}`}>USD ($)</span>
              <Switch
                checked={currency === "bdt"}
                onCheckedChange={(checked) => setCurrency(checked ? "bdt" : "usd")}
                data-testid="currency-toggle"
              />
              <span className={`text-sm ${currency === "bdt" ? "text-white" : "text-zinc-500"}`}>BDT (৳)</span>
            </div>
            {currency === "bdt" && (
              <Badge className="bg-emerald-500/20 text-emerald-400 border-0">Bangladesh</Badge>
            )}
          </div>

          {user && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/20 text-indigo-300">
              <CreditCard className="w-4 h-4" />
              <span>Current: <strong>{currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}</strong> • {credits} credits remaining</span>
            </div>
          )}

          {/* Admin Controls */}
          {isAdmin && (
            <div className="mt-4 flex items-center justify-center gap-3" data-testid="admin-pricing-controls">
              <Button
                size="sm"
                variant={adminEditing ? "default" : "outline"}
                className={adminEditing ? "bg-amber-600 hover:bg-amber-700" : "border-white/10 text-zinc-400"}
                onClick={() => { setAdminEditing(!adminEditing); cancelEdit(); setShowNewPlan(false); }}
                data-testid="toggle-admin-edit"
              >
                <Edit2 className="w-3 h-3 mr-1" /> {adminEditing ? "Exit Edit Mode" : "Admin Edit"}
              </Button>
              {adminEditing && (
                <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700" onClick={() => setShowNewPlan(true)} data-testid="add-plan-btn">
                  <Plus className="w-3 h-3 mr-1" /> Add Plan
                </Button>
              )}
            </div>
          )}
        </div>

        {/* New Plan Form (Admin) */}
        {showNewPlan && adminEditing && (
          <div className="mb-8 max-w-2xl mx-auto bg-zinc-900/70 border border-indigo-500/30 rounded-xl p-6" data-testid="new-plan-inline-form">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Create New Plan</h3>
              <Button size="sm" variant="ghost" onClick={() => setShowNewPlan(false)}><X className="w-4 h-4" /></Button>
            </div>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div><label className="text-[10px] text-zinc-500">Plan ID</label><Input value={newPlan.plan_id} onChange={e => setNewPlan(p => ({ ...p, plan_id: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" placeholder="enterprise" data-testid="inline-new-plan-id" /></div>
              <div><label className="text-[10px] text-zinc-500">Name</label><Input value={newPlan.name} onChange={e => setNewPlan(p => ({ ...p, name: e.target.value }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" placeholder="Enterprise" data-testid="inline-new-plan-name" /></div>
            </div>
            <div className="grid grid-cols-4 gap-3 mb-3">
              <div><label className="text-[10px] text-zinc-500">USD/mo</label><Input type="number" value={newPlan.price_usd} onChange={e => setNewPlan(p => ({ ...p, price_usd: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" /></div>
              <div><label className="text-[10px] text-zinc-500">BDT/mo</label><Input type="number" value={newPlan.price_bdt} onChange={e => setNewPlan(p => ({ ...p, price_bdt: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" /></div>
              <div><label className="text-[10px] text-zinc-500">Credits</label><Input type="number" value={newPlan.credits} onChange={e => setNewPlan(p => ({ ...p, credits: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" /></div>
              <div><label className="text-[10px] text-zinc-500">Agents (-1=all)</label><Input type="number" value={newPlan.max_agents} onChange={e => setNewPlan(p => ({ ...p, max_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" /></div>
            </div>
            <div className="mb-3">
              <label className="text-[10px] text-zinc-500">Features (comma-separated)</label>
              <Input value={newPlan.features.join(", ")} onChange={e => setNewPlan(p => ({ ...p, features: e.target.value.split(",").map(f => f.trim()).filter(Boolean) }))} className="bg-zinc-800/50 border-white/10 h-8 text-sm" placeholder="Feature 1, Feature 2, Feature 3" />
            </div>
            <Button onClick={createNewPlan} disabled={savingPlan} className="bg-emerald-600 hover:bg-emerald-700" data-testid="inline-save-new-plan">
              {savingPlan ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Check className="w-4 h-4 mr-1" />} Create Plan
            </Button>
          </div>
        )}

        {/* Subscription Plans */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {plans.map((plan) => {
            const isEditingThis = editingPlanId === plan.id && editData;
            return (
            <Card
              key={plan.id}
              className={`bg-zinc-900/50 border-white/10 relative ${
                plan.popular ? "ring-2 ring-indigo-500" : ""
              } ${currentPlan === plan.id ? "border-emerald-500" : ""} ${isEditingThis ? "ring-2 ring-amber-500" : ""}`}
              data-testid={`plan-${plan.id}`}
            >
              {plan.popular && !isEditingThis && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-indigo-500 to-violet-500 text-white border-0">
                    Most Popular
                  </Badge>
                </div>
              )}
              {currentPlan === plan.id && !isEditingThis && (
                <div className="absolute -top-3 right-4">
                  <Badge className="bg-emerald-500 text-white border-0">Current Plan</Badge>
                </div>
              )}
              {/* Admin edit/delete icons */}
              {adminEditing && !isEditingThis && (
                <div className="absolute top-2 right-2 flex gap-1 z-10">
                  <button onClick={() => startEdit(plan.id, dynamicPlans?.[plan.id] || {})} className="w-6 h-6 rounded bg-amber-500/20 flex items-center justify-center text-amber-400 hover:bg-amber-500/30" data-testid={`edit-plan-inline-${plan.id}`}>
                    <Edit2 className="w-3 h-3" />
                  </button>
                  {plan.id !== "free" && (
                    <button onClick={() => deletePlan(plan.id)} className="w-6 h-6 rounded bg-red-500/20 flex items-center justify-center text-red-400 hover:bg-red-500/30" data-testid={`delete-plan-inline-${plan.id}`}>
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>
              )}

              {isEditingThis ? (
                /* Inline Edit Form */
                <CardContent className="p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-amber-400">Editing: {plan.name}</span>
                    <button onClick={cancelEdit} className="text-zinc-500 hover:text-white"><X className="w-4 h-4" /></button>
                  </div>
                  <div><label className="text-[9px] text-zinc-500">Name</label><Input value={editData.name || ""} onChange={e => setEditData(d => ({ ...d, name: e.target.value }))} className="bg-zinc-800/50 border-white/10 h-7 text-xs" /></div>
                  <div className="grid grid-cols-2 gap-2">
                    <div><label className="text-[9px] text-zinc-500">USD/mo</label><Input type="number" value={editData.price_usd || 0} onChange={e => setEditData(d => ({ ...d, price_usd: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-7 text-xs" /></div>
                    <div><label className="text-[9px] text-zinc-500">BDT/mo</label><Input type="number" value={editData.price_bdt || 0} onChange={e => setEditData(d => ({ ...d, price_bdt: parseFloat(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-7 text-xs" /></div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div><label className="text-[9px] text-zinc-500">Credits</label><Input type="number" value={editData.credits || 0} onChange={e => setEditData(d => ({ ...d, credits: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-7 text-xs" /></div>
                    <div><label className="text-[9px] text-zinc-500">Max Agents</label><Input type="number" value={editData.max_agents || 0} onChange={e => setEditData(d => ({ ...d, max_agents: parseInt(e.target.value) || 0 }))} className="bg-zinc-800/50 border-white/10 h-7 text-xs" /></div>
                  </div>
                  <div>
                    <label className="text-[9px] text-zinc-500">Features (one per line)</label>
                    <textarea value={(editData.features || []).join("\n")} onChange={e => setEditData(d => ({ ...d, features: e.target.value.split("\n").filter(Boolean) }))} className="w-full bg-zinc-800/50 border border-white/10 rounded px-2 py-1 text-xs text-white min-h-[80px] resize-y" />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={saveEdit} disabled={savingPlan} className="bg-emerald-600 hover:bg-emerald-700 flex-1" data-testid={`save-edit-${plan.id}`}>
                      {savingPlan ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3 mr-1" />} Save
                    </Button>
                    <Button size="sm" variant="outline" className="border-white/10" onClick={cancelEdit}>Cancel</Button>
                  </div>
                </CardContent>
              ) : (
                /* Normal Plan Display */
                <>
              <CardHeader className="text-center pb-2">
                <div className="w-12 h-12 rounded-lg bg-indigo-500/20 flex items-center justify-center mx-auto mb-3 text-indigo-400">
                  {plan.icon}
                </div>
                <CardTitle className="text-white font-['Outfit']">{plan.name}</CardTitle>
                <div className="mt-2">
                  <span className="text-4xl font-bold text-white">{formatPrice(plan)}</span>
                  <span className="text-zinc-400">/month</span>
                </div>
                <p className="text-sm text-indigo-400 mt-1">{plan.credits} credits/month</p>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm text-zinc-300">
                      <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={loading || currentPlan === plan.id}
                  className={`w-full ${
                    plan.popular
                      ? "bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
                      : "bg-white/10 hover:bg-white/20"
                  }`}
                  data-testid={`subscribe-${plan.id}`}
                >
                  {processingPlan === plan.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : currentPlan === plan.id ? (
                    "Current Plan"
                  ) : plan.price_usd === 0 ? (
                    "Get Started"
                  ) : (
                    "Subscribe"
                  )}
                </Button>
              </CardContent>
                </>
              )}
            </Card>
            );
          })}
        </div>

        {/* ====== BUILD YOUR OWN PACKAGE ====== */}
        {customConfig && (
          <div className="mb-16" data-testid="custom-package-section">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-sm mb-4">
                <Package className="w-4 h-4" /> New
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 font-['Outfit']">
                Build Your Own Package
              </h2>
              <p className="text-zinc-400 max-w-xl mx-auto">
                Pick exactly the agents you need and the credits you want. Pay only for what you use.
              </p>
            </div>

            <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Agent Picker */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">Select Your Agents</h3>
                  <span className="text-sm text-zinc-400">
                    {selectedAgents.length} selected &middot; {currSymbol}{(selectedAgents.length * (customConfig[agentPriceKey] || 0)).toLocaleString()}/mo
                  </span>
                </div>

                <div className="max-h-[340px] overflow-y-auto pr-1 rounded-xl border border-white/5 p-3 bg-zinc-950/40 custom-scrollbar">
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {agents.map((agent) => {
                      const isSelected = selectedAgents.includes(agent.agent_id);
                      return (
                        <button
                          key={agent.agent_id}
                          onClick={() => toggleAgent(agent.agent_id)}
                          className={`relative flex flex-col items-center gap-2 p-3 rounded-xl border transition-all text-left ${
                            isSelected
                              ? "border-indigo-500 bg-indigo-500/15 ring-1 ring-indigo-500/40"
                              : "border-white/10 bg-zinc-900/50 hover:border-white/20 hover:bg-zinc-800/50"
                          }`}
                          data-testid={`pick-agent-${agent.agent_id}`}
                        >
                          {isSelected && (
                            <div className="absolute top-1.5 right-1.5 w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                              <Check className="w-3 h-3 text-white" />
                            </div>
                          )}
                          <img
                            src={agent.avatar}
                            alt={agent.name}
                            className="w-10 h-10 rounded-lg object-cover"
                          />
                          <div className="text-center">
                            <p className="text-xs font-medium text-white truncate max-w-[90px]">{agent.name}</p>
                            <p className="text-[10px] text-zinc-500 truncate max-w-[90px]">{agent.role}</p>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Commander Add-on */}
                <button
                  onClick={() => setIncludeCommander(!includeCommander)}
                  className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all ${
                    includeCommander
                      ? "border-amber-500 bg-amber-500/10 ring-1 ring-amber-500/30"
                      : "border-white/10 bg-zinc-900/50 hover:border-white/20"
                  }`}
                  data-testid="commander-addon-toggle"
                >
                  <div className="w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-amber-400" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-semibold text-white">Commander Orion (Add-on)</p>
                    <p className="text-xs text-zinc-400">Delegates tasks across your team. Breaks down complex goals automatically.</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-sm font-bold text-amber-400">+{currSymbol}{(customConfig[commanderPriceKey] || 0).toLocaleString()}</p>
                    <p className="text-[10px] text-zinc-500">/month</p>
                  </div>
                  {includeCommander && (
                    <div className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-black" />
                    </div>
                  )}
                </button>
              </div>

              {/* Right: Summary & Credit Picker */}
              <div className="space-y-4">
                <Card className="bg-zinc-900/70 border-white/10 sticky top-6">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white text-lg font-['Outfit']">Your Package</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Credit Presets */}
                    <div>
                      <p className="text-sm text-zinc-400 mb-2">Choose credits</p>
                      <div className="space-y-2">
                        {(customConfig.credit_presets || []).map((preset) => (
                          <button
                            key={preset.id}
                            onClick={() => setSelectedCredit(preset.id)}
                            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg border transition-all text-sm ${
                              selectedCredit === preset.id
                                ? "border-indigo-500 bg-indigo-500/15 text-white"
                                : "border-white/10 bg-zinc-800/50 text-zinc-300 hover:border-white/20"
                            }`}
                            data-testid={`credit-preset-${preset.id}`}
                          >
                            <span className="font-medium">{preset.credits.toLocaleString()} credits</span>
                            <span className={selectedCredit === preset.id ? "text-indigo-400 font-semibold" : "text-zinc-500"}>
                              {currSymbol}{preset[priceKey].toLocaleString()}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Price Breakdown */}
                    <div className="border-t border-white/10 pt-3 space-y-2">
                      <div className="flex justify-between text-sm text-zinc-400">
                        <span>{selectedAgents.length} agent{selectedAgents.length !== 1 ? "s" : ""}</span>
                        <span>{currSymbol}{(selectedAgents.length * (customConfig[agentPriceKey] || 0)).toLocaleString()}</span>
                      </div>
                      {selectedCredit && (
                        <div className="flex justify-between text-sm text-zinc-400">
                          <span>{customConfig.credit_presets?.find(p => p.id === selectedCredit)?.credits.toLocaleString()} credits</span>
                          <span>{currSymbol}{(customConfig.credit_presets?.find(p => p.id === selectedCredit)?.[priceKey] || 0).toLocaleString()}</span>
                        </div>
                      )}
                      {includeCommander && (
                        <div className="flex justify-between text-sm text-amber-400">
                          <span>Commander AI</span>
                          <span>+{currSymbol}{(customConfig[commanderPriceKey] || 0).toLocaleString()}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-lg font-bold text-white pt-2 border-t border-white/10">
                        <span>Total</span>
                        <span>{currSymbol}{customTotal.toLocaleString()}/mo</span>
                      </div>
                    </div>

                    <Button
                      onClick={handleCustomCheckout}
                      disabled={customLoading || selectedAgents.length === 0 || !selectedCredit}
                      className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black font-semibold"
                      data-testid="custom-checkout-btn"
                    >
                      {customLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Package className="w-4 h-4 mr-2" />
                          Build Package
                        </>
                      )}
                    </Button>

                    {!user && (
                      <p className="text-xs text-center text-zinc-500">
                        <Link to="/register" className="text-indigo-400 underline">Sign up</Link> to build your package
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* Credit Top-ups */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6 text-center font-['Outfit']">
            Need More Credits?
          </h2>
          <p className="text-zinc-400 text-center mb-8">
            Buy additional credits anytime. They never expire.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {creditPackages.map((pkg) => (
              <Card
                key={pkg.id}
                className="bg-zinc-900/50 border-white/10 hover:border-white/20 cursor-pointer transition-colors"
                data-testid={`credits-${pkg.id}`}
              >
                <CardContent className="p-4 text-center">
                  <p className="text-2xl font-bold text-white mb-1">{pkg.credits}</p>
                  <p className="text-sm text-zinc-400 mb-3">credits</p>
                  <Button
                    onClick={() => handleBuyCredits(pkg.id)}
                    disabled={loading || !user}
                    variant="outline"
                    className="w-full border-white/10 hover:bg-white/5"
                    data-testid={`buy-${pkg.id}`}
                  >
                    {processingPlan === pkg.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      formatCreditPrice(pkg)
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Regional Note */}
        {currency === "bdt" && (
          <div className="text-center p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 mb-8">
            <p className="text-emerald-400">
              Prices shown in Bangladeshi Taka (BDT). Payment processed via Stripe.
            </p>
          </div>
        )}

        {/* FAQ or Note */}
        <div className="text-center text-zinc-500 text-sm">
          <p>458+ specialized AI agents across 27 network categories and 16 system layers. Commander Orion ∞ included in Pro and Business plans.</p>
          <p className="mt-2">Questions? Contact support@maarsglobal.com</p>
        </div>
        <BrandFooter className="mt-8" />
      </div>
    </div>
  );
};

export default PricingPage;
