import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot, Check, Sparkles, Zap, Crown, Building, CreditCard,
  ArrowLeft, Globe, Package, Plus, X, Shield, Edit2, Save
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

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
const formInput = { background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" };

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

  const icons = { free: <Sparkles style={{ width: 24, height: 24 }} />, starter: <Zap style={{ width: 24, height: 24 }} />, pro: <Crown style={{ width: 24, height: 24 }} />, business: <Building style={{ width: 24, height: 24 }} /> };

  const defaultPlans = [
    {
      id: "free",
      name: "Free",
      price_usd: 0,
      price_bdt: 0,
      credits: 50,
      icon: <Sparkles style={{ width: 24, height: 24 }} />,
      features: ["3 AI agents", "50 credits/month", "Basic chat & tasks", "1 LLM provider", "Community support"],
      popular: false
    },
    {
      id: "starter",
      name: "Starter",
      price_usd: 29,
      price_bdt: 3100,
      credits: 500,
      icon: <Zap style={{ width: 24, height: 24 }} />,
      features: ["10 AI agents", "500 credits/month", "2 custom agents", "5 LLM providers", "Vibe Coding & Content Generator", "Voice commands", "Team (up to 3)", "Priority support", "File uploads"],
      popular: false
    },
    {
      id: "pro",
      name: "Pro",
      price_usd: 79,
      price_bdt: 8400,
      credits: 2000,
      icon: <Crown style={{ width: 24, height: 24 }} />,
      features: ["25 AI agents + Commander Orion", "2,000 credits/month", "5 custom agents", "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "Autonomous orchestration", "Quality control & auto-learning", "Memory governance", "Real-time activity monitor", "Reference intelligence", "Team (up to 10)", "Unlimited uploads"],
      popular: true
    },
    {
      id: "business",
      name: "Business",
      price_usd: 199,
      price_bdt: 21100,
      credits: 6000,
      icon: <Building style={{ width: 24, height: 24 }} />,
      features: ["All 458+ AI agents + Commander Orion ∞", "6,000 credits/month", "Unlimited custom agents", "MAARS Universal AI Gateway — 33 providers, 175,000+ models", "Full autonomous orchestration", "All 27 agent networks", "MAARS Kernel & Task Graphs", "KPI dashboard & collaboration engine", "Admin code explorer", "Unlimited team members", "Dedicated support", "API access"],
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
    icon: icons[id] || <Sparkles style={{ width: 24, height: 24 }} />,
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

  const inputSm = { ...formInput, fontSize: 12, padding: "4px 8px", height: 32, borderRadius: 6 };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b", animation: "fadeUp .4s ease" }} data-testid="pricing-page">
      <style>{STYLES}</style>

      {/* Header Nav */}
      <nav style={{ borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 16px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 }}>
            <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
              <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{ width: 32, height: 32, borderRadius: 8, objectFit: "cover", boxShadow: "0 0 0 1px rgba(129,140,248,0.2)" }} />
              <span style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif" }}>MAARS Command</span>
            </Link>
            {user ? (
              <button onClick={() => navigate("/dashboard")} style={{ padding: "6px 16px", borderRadius: 8, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "#fff", cursor: "pointer", fontSize: 14, fontFamily: "inherit" }}>
                Dashboard
              </button>
            ) : (
              <div style={{ display: "flex", gap: 12 }}>
                <button onClick={() => navigate("/login")} style={{ padding: "6px 16px", borderRadius: 8, border: "none", background: "transparent", color: "#a1a1aa", cursor: "pointer", fontSize: 14, fontFamily: "inherit" }}>Login</button>
                <button onClick={() => navigate("/register")} style={{ padding: "6px 16px", borderRadius: 8, border: "none", background: "linear-gradient(135deg, #818cf8, #7c3aed)", color: "#fff", cursor: "pointer", fontSize: 14, fontWeight: 600, fontFamily: "inherit" }}>
                  Get Started
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "48px 16px" }}>
        {/* Back link for logged in users */}
        {user && (
          <Link to="/settings" style={{ display: "inline-flex", alignItems: "center", gap: 8, color: "#a1a1aa", textDecoration: "none", marginBottom: 24, fontSize: 14 }}>
            <ArrowLeft style={{ width: 16, height: 16 }} /> Back to Settings
          </Link>
        )}

        {/* Page Header */}
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <h1 style={{ fontSize: "clamp(28px, 5vw, 40px)", fontWeight: 700, color: "#fff", marginBottom: 16, fontFamily: "Outfit, sans-serif" }}>
            Choose Your Plan
          </h1>
          <p style={{ fontSize: 18, color: T.zinc, maxWidth: 672, margin: "0 auto 24px" }}>
            Get access to your AI team with flexible pricing. Start free, upgrade anytime.
          </p>

          {/* Currency Toggle */}
          <div style={{ display: "inline-flex", alignItems: "center", gap: 16, padding: "12px 16px", borderRadius: 8, background: "rgba(24,24,27,0.5)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <Globe style={{ width: 16, height: 16, color: "#a1a1aa" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 14, color: currency === "usd" ? "#fff" : "#71717a" }}>USD ($)</span>
              {/* Native toggle switch */}
              <label style={{ position: "relative", display: "inline-block", width: 40, height: 22, cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={currency === "bdt"}
                  onChange={(e) => setCurrency(e.target.checked ? "bdt" : "usd")}
                  style={{ opacity: 0, width: 0, height: 0 }}
                  data-testid="currency-toggle"
                />
                <span style={{
                  position: "absolute", inset: 0, borderRadius: 11,
                  background: currency === "bdt" ? T.indigo : "rgba(255,255,255,0.1)",
                  transition: "background .2s",
                }}>
                  <span style={{
                    position: "absolute", top: 3, left: currency === "bdt" ? 21 : 3,
                    width: 16, height: 16, borderRadius: "50%", background: "#fff",
                    transition: "left .2s",
                  }} />
                </span>
              </label>
              <span style={{ fontSize: 14, color: currency === "bdt" ? "#fff" : "#71717a" }}>BDT (৳)</span>
            </div>
            {currency === "bdt" && (
              <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 999, background: "rgba(52,211,153,0.2)", color: T.green, fontWeight: 500 }}>Bangladesh</span>
            )}
          </div>

          {user && (
            <div style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 999, background: "rgba(129,140,248,0.2)", color: "#a5b4fc", fontSize: 14 }}>
              <CreditCard style={{ width: 16, height: 16 }} />
              <span>Current: <strong>{currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}</strong> • {credits} credits remaining</span>
            </div>
          )}

          {/* Admin Controls */}
          {isAdmin && (
            <div style={{ marginTop: 16, display: "flex", alignItems: "center", justifyContent: "center", gap: 12 }} data-testid="admin-pricing-controls">
              <button
                style={{ display: "flex", alignItems: "center", gap: 4, padding: "6px 14px", borderRadius: 8, fontSize: 13, fontWeight: 500, border: adminEditing ? "none" : "1px solid rgba(255,255,255,0.1)", background: adminEditing ? "#b45309" : "transparent", color: adminEditing ? "#fff" : "#a1a1aa", cursor: "pointer", fontFamily: "inherit" }}
                onClick={() => { setAdminEditing(!adminEditing); cancelEdit(); setShowNewPlan(false); }}
                data-testid="toggle-admin-edit"
              >
                <Edit2 style={{ width: 12, height: 12 }} /> {adminEditing ? "Exit Edit Mode" : "Admin Edit"}
              </button>
              {adminEditing && (
                <button style={{ display: "flex", alignItems: "center", gap: 4, padding: "6px 14px", borderRadius: 8, fontSize: 13, fontWeight: 500, border: "none", background: "#4f46e5", color: "#fff", cursor: "pointer", fontFamily: "inherit" }} onClick={() => setShowNewPlan(true)} data-testid="add-plan-btn">
                  <Plus style={{ width: 12, height: 12 }} /> Add Plan
                </button>
              )}
            </div>
          )}
        </div>

        {/* New Plan Form (Admin) */}
        {showNewPlan && adminEditing && (
          <div style={{ marginBottom: 32, maxWidth: 672, margin: "0 auto 32px", background: "rgba(24,24,27,0.7)", border: "1px solid rgba(129,140,248,0.3)", borderRadius: 12, padding: 24 }} data-testid="new-plan-inline-form">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, color: "#fff", margin: 0 }}>Create New Plan</h3>
              <button onClick={() => setShowNewPlan(false)} style={{ background: "none", border: "none", color: "#a1a1aa", cursor: "pointer", display: "flex", alignItems: "center" }}><X style={{ width: 16, height: 16 }} /></button>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>Plan ID</label><input value={newPlan.plan_id} onChange={e => setNewPlan(p => ({ ...p, plan_id: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') }))} style={inputSm} placeholder="enterprise" data-testid="inline-new-plan-id" /></div>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>Name</label><input value={newPlan.name} onChange={e => setNewPlan(p => ({ ...p, name: e.target.value }))} style={inputSm} placeholder="Enterprise" data-testid="inline-new-plan-name" /></div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>USD/mo</label><input type="number" value={newPlan.price_usd} onChange={e => setNewPlan(p => ({ ...p, price_usd: parseFloat(e.target.value) || 0 }))} style={inputSm} /></div>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>BDT/mo</label><input type="number" value={newPlan.price_bdt} onChange={e => setNewPlan(p => ({ ...p, price_bdt: parseFloat(e.target.value) || 0 }))} style={inputSm} /></div>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>Credits</label><input type="number" value={newPlan.credits} onChange={e => setNewPlan(p => ({ ...p, credits: parseInt(e.target.value) || 0 }))} style={inputSm} /></div>
              <div><label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>Agents (-1=all)</label><input type="number" value={newPlan.max_agents} onChange={e => setNewPlan(p => ({ ...p, max_agents: parseInt(e.target.value) || 0 }))} style={inputSm} /></div>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 10, color: T.zinc, display: "block", marginBottom: 4 }}>Features (comma-separated)</label>
              <input value={newPlan.features.join(", ")} onChange={e => setNewPlan(p => ({ ...p, features: e.target.value.split(",").map(f => f.trim()).filter(Boolean) }))} style={inputSm} placeholder="Feature 1, Feature 2, Feature 3" />
            </div>
            <button onClick={createNewPlan} disabled={savingPlan} style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 20px", borderRadius: 8, border: "none", background: "#059669", color: "#fff", fontSize: 14, fontWeight: 600, cursor: savingPlan ? "not-allowed" : "pointer", fontFamily: "inherit", opacity: savingPlan ? 0.7 : 1 }} data-testid="inline-save-new-plan">
              {savingPlan
                ? <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                : <Check style={{ width: 16, height: 16 }} />
              } Create Plan
            </button>
          </div>
        )}

        {/* Subscription Plans */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 24, marginBottom: 64 }}>
          {plans.map((plan) => {
            const isEditingThis = editingPlanId === plan.id && editData;
            return (
              <div
                key={plan.id}
                style={{
                  background: "rgba(24,24,27,0.5)",
                  border: `1px solid ${currentPlan === plan.id ? "#34d399" : plan.popular ? T.indigo : "rgba(255,255,255,0.1)"}`,
                  borderRadius: 12,
                  position: "relative",
                  boxShadow: plan.popular ? `0 0 0 2px ${T.indigo}` : isEditingThis ? `0 0 0 2px ${T.amber}` : "none",
                }}
                data-testid={`plan-${plan.id}`}
              >
                {plan.popular && !isEditingThis && (
                  <div style={{ position: "absolute", top: -12, left: "50%", transform: "translateX(-50%)" }}>
                    <span style={{ padding: "3px 12px", borderRadius: 999, background: "linear-gradient(135deg, #818cf8, #7c3aed)", color: "#fff", fontSize: 11, fontWeight: 600 }}>Most Popular</span>
                  </div>
                )}
                {currentPlan === plan.id && !isEditingThis && (
                  <div style={{ position: "absolute", top: -12, right: 16 }}>
                    <span style={{ padding: "3px 12px", borderRadius: 999, background: "#059669", color: "#fff", fontSize: 11, fontWeight: 600 }}>Current Plan</span>
                  </div>
                )}
                {/* Admin edit/delete icons */}
                {adminEditing && !isEditingThis && (
                  <div style={{ position: "absolute", top: 8, right: 8, display: "flex", gap: 4, zIndex: 10 }}>
                    <button onClick={() => startEdit(plan.id, dynamicPlans?.[plan.id] || {})} style={{ width: 24, height: 24, borderRadius: 4, background: "rgba(245,158,11,0.2)", border: "none", display: "flex", alignItems: "center", justifyContent: "center", color: T.amber, cursor: "pointer" }} data-testid={`edit-plan-inline-${plan.id}`}>
                      <Edit2 style={{ width: 12, height: 12 }} />
                    </button>
                    {plan.id !== "free" && (
                      <button onClick={() => deletePlan(plan.id)} style={{ width: 24, height: 24, borderRadius: 4, background: "rgba(239,68,68,0.2)", border: "none", display: "flex", alignItems: "center", justifyContent: "center", color: T.red, cursor: "pointer" }} data-testid={`delete-plan-inline-${plan.id}`}>
                        <X style={{ width: 12, height: 12 }} />
                      </button>
                    )}
                  </div>
                )}

                {isEditingThis ? (
                  /* Inline Edit Form */
                  <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: T.amber }}>Editing: {plan.name}</span>
                      <button onClick={cancelEdit} style={{ background: "none", border: "none", color: T.zinc, cursor: "pointer", display: "flex" }}><X style={{ width: 16, height: 16 }} /></button>
                    </div>
                    <div><label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>Name</label><input value={editData.name || ""} onChange={e => setEditData(d => ({ ...d, name: e.target.value }))} style={{ ...inputSm, height: 28, fontSize: 12 }} /></div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                      <div><label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>USD/mo</label><input type="number" value={editData.price_usd || 0} onChange={e => setEditData(d => ({ ...d, price_usd: parseFloat(e.target.value) || 0 }))} style={{ ...inputSm, height: 28, fontSize: 12 }} /></div>
                      <div><label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>BDT/mo</label><input type="number" value={editData.price_bdt || 0} onChange={e => setEditData(d => ({ ...d, price_bdt: parseFloat(e.target.value) || 0 }))} style={{ ...inputSm, height: 28, fontSize: 12 }} /></div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                      <div><label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>Credits</label><input type="number" value={editData.credits || 0} onChange={e => setEditData(d => ({ ...d, credits: parseInt(e.target.value) || 0 }))} style={{ ...inputSm, height: 28, fontSize: 12 }} /></div>
                      <div><label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>Max Agents</label><input type="number" value={editData.max_agents || 0} onChange={e => setEditData(d => ({ ...d, max_agents: parseInt(e.target.value) || 0 }))} style={{ ...inputSm, height: 28, fontSize: 12 }} /></div>
                    </div>
                    <div>
                      <label style={{ fontSize: 9, color: T.zinc, display: "block", marginBottom: 2 }}>Features (one per line)</label>
                      <textarea value={(editData.features || []).join("\n")} onChange={e => setEditData(d => ({ ...d, features: e.target.value.split("\n").filter(Boolean) }))} style={{ ...formInput, fontSize: 12, minHeight: 80, resize: "vertical" }} />
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button onClick={saveEdit} disabled={savingPlan} style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 4, padding: "6px 12px", borderRadius: 6, border: "none", background: "#059669", color: "#fff", fontSize: 12, fontWeight: 600, cursor: savingPlan ? "not-allowed" : "pointer", fontFamily: "inherit", opacity: savingPlan ? 0.7 : 1 }} data-testid={`save-edit-${plan.id}`}>
                        {savingPlan
                          ? <div style={{ width: 12, height: 12, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                          : <Save style={{ width: 12, height: 12 }} />
                        } Save
                      </button>
                      <button onClick={cancelEdit} style={{ padding: "6px 12px", borderRadius: 6, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "#a1a1aa", fontSize: 12, cursor: "pointer", fontFamily: "inherit" }}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  /* Normal Plan Display */
                  <div style={{ padding: 24 }}>
                    {/* Card Header */}
                    <div style={{ textAlign: "center", marginBottom: 16 }}>
                      <div style={{ width: 48, height: 48, borderRadius: 8, background: "rgba(129,140,248,0.2)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px", color: T.indigo }}>
                        {plan.icon}
                      </div>
                      <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: "0 0 8px" }}>{plan.name}</p>
                      <div>
                        <span style={{ fontSize: 36, fontWeight: 700, color: "#fff" }}>{formatPrice(plan)}</span>
                        <span style={{ color: T.zinc, fontSize: 14 }}>/month</span>
                      </div>
                      <p style={{ fontSize: 14, color: T.indigo, margin: "4px 0 0" }}>{plan.credits} credits/month</p>
                    </div>
                    {/* Features */}
                    <ul style={{ listStyle: "none", padding: 0, margin: "0 0 24px", display: "flex", flexDirection: "column", gap: 12 }}>
                      {plan.features.map((feature, idx) => (
                        <li key={idx} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14, color: "#d4d4d8" }}>
                          <Check style={{ width: 16, height: 16, color: T.green, flexShrink: 0 }} />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => handleSubscribe(plan.id)}
                      disabled={loading || currentPlan === plan.id}
                      style={{
                        width: "100%", padding: "10px 16px", borderRadius: 8, border: "none",
                        background: plan.popular ? "linear-gradient(135deg, #818cf8, #7c3aed)" : "rgba(255,255,255,0.1)",
                        color: "#fff", fontSize: 14, fontWeight: 600, cursor: (loading || currentPlan === plan.id) ? "not-allowed" : "pointer",
                        display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                        fontFamily: "inherit", opacity: (loading || currentPlan === plan.id) ? 0.7 : 1,
                        transition: "opacity .2s",
                      }}
                      data-testid={`subscribe-${plan.id}`}
                    >
                      {processingPlan === plan.id ? (
                        <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      ) : currentPlan === plan.id ? (
                        "Current Plan"
                      ) : plan.price_usd === 0 ? (
                        "Get Started"
                      ) : (
                        "Subscribe"
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* ====== BUILD YOUR OWN PACKAGE ====== */}
        {customConfig && (
          <div style={{ marginBottom: 64 }} data-testid="custom-package-section">
            <div style={{ textAlign: "center", marginBottom: 32 }}>
              <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "4px 12px", borderRadius: 999, background: "rgba(245,158,11,0.2)", color: T.amber, fontSize: 14, marginBottom: 16 }}>
                <Package style={{ width: 16, height: 16 }} /> New
              </div>
              <h2 style={{ fontSize: "clamp(24px, 4vw, 32px)", fontWeight: 700, color: "#fff", marginBottom: 8, fontFamily: "Outfit, sans-serif" }}>
                Build Your Own Package
              </h2>
              <p style={{ color: T.zinc, maxWidth: 560, margin: "0 auto" }}>
                Pick exactly the agents you need and the credits you want. Pay only for what you use.
              </p>
            </div>

            <div style={{ maxWidth: 1024, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr", gap: 24 }}>
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24, alignItems: "start" }}>
                {/* Left: Agent Picker */}
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <h3 style={{ fontSize: 18, fontWeight: 600, color: "#fff", margin: 0 }}>Select Your Agents</h3>
                    <span style={{ fontSize: 14, color: T.zinc }}>
                      {selectedAgents.length} selected &middot; {currSymbol}{(selectedAgents.length * (customConfig[agentPriceKey] || 0)).toLocaleString()}/mo
                    </span>
                  </div>

                  <div style={{ maxHeight: 340, overflowY: "auto", borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)", padding: 12, background: "rgba(9,9,11,0.4)" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))", gap: 12 }}>
                      {agents.map((agent) => {
                        const isSelected = selectedAgents.includes(agent.agent_id);
                        return (
                          <button
                            key={agent.agent_id}
                            onClick={() => toggleAgent(agent.agent_id)}
                            style={{
                              position: "relative", display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: 12,
                              borderRadius: 12, border: `1px solid ${isSelected ? T.indigo : "rgba(255,255,255,0.1)"}`,
                              background: isSelected ? "rgba(129,140,248,0.15)" : "rgba(24,24,27,0.5)",
                              cursor: "pointer", transition: "all .2s", fontFamily: "inherit",
                              boxShadow: isSelected ? `0 0 0 1px rgba(129,140,248,0.4)` : "none",
                            }}
                            data-testid={`pick-agent-${agent.agent_id}`}
                          >
                            {isSelected && (
                              <div style={{ position: "absolute", top: 6, right: 6, width: 20, height: 20, borderRadius: "50%", background: T.indigo, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                <Check style={{ width: 12, height: 12, color: "#fff" }} />
                              </div>
                            )}
                            <img
                              src={agent.avatar}
                              alt={agent.name}
                              style={{ width: 40, height: 40, borderRadius: 8, objectFit: "cover" }}
                            />
                            <div style={{ textAlign: "center" }}>
                              <p style={{ fontSize: 12, fontWeight: 500, color: "#fff", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 90 }}>{agent.name}</p>
                              <p style={{ fontSize: 10, color: T.zinc, margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 90 }}>{agent.role}</p>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Commander Add-on */}
                  <button
                    onClick={() => setIncludeCommander(!includeCommander)}
                    style={{
                      width: "100%", display: "flex", alignItems: "center", gap: 16, padding: 16,
                      borderRadius: 12, border: `1px solid ${includeCommander ? T.amber : "rgba(255,255,255,0.1)"}`,
                      background: includeCommander ? "rgba(245,158,11,0.1)" : "rgba(24,24,27,0.5)",
                      cursor: "pointer", transition: "all .2s", fontFamily: "inherit",
                      boxShadow: includeCommander ? `0 0 0 1px rgba(245,158,11,0.3)` : "none",
                    }}
                    data-testid="commander-addon-toggle"
                  >
                    <div style={{ width: 48, height: 48, borderRadius: 8, background: "rgba(245,158,11,0.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <Shield style={{ width: 24, height: 24, color: T.amber }} />
                    </div>
                    <div style={{ flex: 1, textAlign: "left" }}>
                      <p style={{ fontSize: 14, fontWeight: 600, color: "#fff", margin: "0 0 2px" }}>Commander Orion (Add-on)</p>
                      <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>Delegates tasks across your team. Breaks down complex goals automatically.</p>
                    </div>
                    <div style={{ textAlign: "right", flexShrink: 0 }}>
                      <p style={{ fontSize: 14, fontWeight: 700, color: T.amber, margin: 0 }}>+{currSymbol}{(customConfig[commanderPriceKey] || 0).toLocaleString()}</p>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>/month</p>
                    </div>
                    {includeCommander && (
                      <div style={{ width: 20, height: 20, borderRadius: "50%", background: T.amber, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                        <Check style={{ width: 12, height: 12, color: "#000" }} />
                      </div>
                    )}
                  </button>
                </div>

                {/* Right: Summary & Credit Picker */}
                <div style={{ position: "sticky", top: 24 }}>
                  <div style={{ background: "rgba(24,24,27,0.7)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
                    <h3 style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: 0 }}>Your Package</h3>

                    {/* Credit Presets */}
                    <div>
                      <p style={{ fontSize: 14, color: T.zinc, marginBottom: 8, marginTop: 0 }}>Choose credits</p>
                      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                        {(customConfig.credit_presets || []).map((preset) => (
                          <button
                            key={preset.id}
                            onClick={() => setSelectedCredit(preset.id)}
                            style={{
                              width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between",
                              padding: "10px 12px", borderRadius: 8,
                              border: `1px solid ${selectedCredit === preset.id ? T.indigo : "rgba(255,255,255,0.1)"}`,
                              background: selectedCredit === preset.id ? "rgba(129,140,248,0.15)" : "rgba(39,39,42,0.5)",
                              color: selectedCredit === preset.id ? "#fff" : "#d4d4d8",
                              fontSize: 14, cursor: "pointer", transition: "all .2s", fontFamily: "inherit",
                            }}
                            data-testid={`credit-preset-${preset.id}`}
                          >
                            <span style={{ fontWeight: 500 }}>{preset.credits.toLocaleString()} credits</span>
                            <span style={{ color: selectedCredit === preset.id ? T.indigo : T.zinc, fontWeight: selectedCredit === preset.id ? 600 : 400 }}>
                              {currSymbol}{preset[priceKey].toLocaleString()}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Price Breakdown */}
                    <div style={{ borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, color: T.zinc }}>
                        <span>{selectedAgents.length} agent{selectedAgents.length !== 1 ? "s" : ""}</span>
                        <span>{currSymbol}{(selectedAgents.length * (customConfig[agentPriceKey] || 0)).toLocaleString()}</span>
                      </div>
                      {selectedCredit && (
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, color: T.zinc }}>
                          <span>{customConfig.credit_presets?.find(p => p.id === selectedCredit)?.credits.toLocaleString()} credits</span>
                          <span>{currSymbol}{(customConfig.credit_presets?.find(p => p.id === selectedCredit)?.[priceKey] || 0).toLocaleString()}</span>
                        </div>
                      )}
                      {includeCommander && (
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, color: T.amber }}>
                          <span>Commander AI</span>
                          <span>+{currSymbol}{(customConfig[commanderPriceKey] || 0).toLocaleString()}</span>
                        </div>
                      )}
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 18, fontWeight: 700, color: "#fff", paddingTop: 8, borderTop: "1px solid rgba(255,255,255,0.1)", marginTop: 4 }}>
                        <span>Total</span>
                        <span>{currSymbol}{customTotal.toLocaleString()}/mo</span>
                      </div>
                    </div>

                    <button
                      onClick={handleCustomCheckout}
                      disabled={customLoading || selectedAgents.length === 0 || !selectedCredit}
                      style={{
                        width: "100%", padding: "12px 16px", borderRadius: 8, border: "none",
                        background: "linear-gradient(135deg, #f59e0b, #ea580c)",
                        color: "#000", fontSize: 14, fontWeight: 700, cursor: (customLoading || selectedAgents.length === 0 || !selectedCredit) ? "not-allowed" : "pointer",
                        display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                        fontFamily: "inherit", opacity: (customLoading || selectedAgents.length === 0 || !selectedCredit) ? 0.6 : 1,
                        transition: "opacity .2s",
                      }}
                      data-testid="custom-checkout-btn"
                    >
                      {customLoading ? (
                        <div style={{ width: 16, height: 16, border: "2px solid rgba(0,0,0,0.3)", borderTopColor: "#000", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      ) : (
                        <>
                          <Package style={{ width: 16, height: 16 }} />
                          Build Package
                        </>
                      )}
                    </button>

                    {!user && (
                      <p style={{ fontSize: 12, textAlign: "center", color: T.zinc, margin: 0 }}>
                        <Link to="/register" style={{ color: T.indigo }}>Sign up</Link> to build your package
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Credit Top-ups */}
        <div style={{ marginBottom: 48 }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, color: "#fff", textAlign: "center", marginBottom: 24, fontFamily: "Outfit, sans-serif" }}>
            Need More Credits?
          </h2>
          <p style={{ color: T.zinc, textAlign: "center", marginBottom: 32, marginTop: 0 }}>
            Buy additional credits anytime. They never expire.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 16, maxWidth: 768, margin: "0 auto" }}>
            {creditPackages.map((pkg) => (
              <div
                key={pkg.id}
                style={{ background: "rgba(24,24,27,0.5)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, padding: 16, textAlign: "center", transition: "border-color .2s" }}
                data-testid={`credits-${pkg.id}`}
              >
                <p style={{ fontSize: 28, fontWeight: 700, color: "#fff", margin: "0 0 4px" }}>{pkg.credits}</p>
                <p style={{ fontSize: 14, color: T.zinc, margin: "0 0 12px" }}>credits</p>
                <button
                  onClick={() => handleBuyCredits(pkg.id)}
                  disabled={loading || !user}
                  style={{
                    width: "100%", padding: "8px 12px", borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.1)", background: "transparent",
                    color: "#d4d4d8", fontSize: 14, fontWeight: 600,
                    cursor: (loading || !user) ? "not-allowed" : "pointer",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: "inherit", opacity: (loading || !user) ? 0.5 : 1,
                    transition: "background .2s",
                  }}
                  data-testid={`buy-${pkg.id}`}
                >
                  {processingPlan === pkg.id ? (
                    <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                  ) : (
                    formatCreditPrice(pkg)
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Regional Note */}
        {currency === "bdt" && (
          <div style={{ textAlign: "center", padding: 16, borderRadius: 8, background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)", marginBottom: 32 }}>
            <p style={{ color: T.green, margin: 0 }}>
              Prices shown in Bangladeshi Taka (BDT). Payment processed via Stripe.
            </p>
          </div>
        )}

        {/* FAQ or Note */}
        <div style={{ textAlign: "center", color: T.zinc, fontSize: 14 }}>
          <p style={{ margin: 0 }}>458+ specialized AI agents across 28 network categories and 36 core systems. Commander Orion ∞ included in Pro and Business plans.</p>
          <p style={{ marginTop: 8, marginBottom: 0 }}>Questions? Contact support.maars@marsgc.net</p>
        </div>
        <BrandFooter className="mt-8" />
      </div>
    </div>
  );
};

export default PricingPage;
