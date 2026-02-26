import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
import { 
  Bot, Check, Sparkles, Zap, Crown, Building, CreditCard,
  ArrowLeft, Loader2, Globe, Package, Plus, X, Shield
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const PricingPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [currentPlan, setCurrentPlan] = useState("free");
  const [credits, setCredits] = useState(0);
  const [processingPlan, setProcessingPlan] = useState(null);
  const [currency, setCurrency] = useState("usd");
  const [dynamicPlans, setDynamicPlans] = useState(null);

  // Custom package state
  const [agents, setAgents] = useState([]);
  const [customConfig, setCustomConfig] = useState(null);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [selectedCredit, setSelectedCredit] = useState(null);
  const [includeCommander, setIncludeCommander] = useState(false);
  const [customLoading, setCustomLoading] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const icons = { free: <Sparkles className="w-6 h-6" />, starter: <Zap className="w-6 h-6" />, pro: <Crown className="w-6 h-6" />, business: <Building className="w-6 h-6" /> };

  const defaultPlans = [
    {
      id: "free",
      name: "Free",
      price_usd: 0,
      price_bdt: 0,
      credits: 50,
      icon: <Sparkles className="w-6 h-6" />,
      features: ["50 credits/month", "1 AI employee", "Basic support", "No custom agents"],
      popular: false
    },
    {
      id: "starter",
      name: "Starter",
      price_usd: 29,
      price_bdt: 3100,
      credits: 500,
      icon: <Zap className="w-6 h-6" />,
      features: ["500 credits/month", "5 AI employees", "2 custom agents (20 credits each)", "Priority support", "File uploads"],
      popular: false
    },
    {
      id: "pro",
      name: "Pro",
      price_usd: 79,
      price_bdt: 8400,
      credits: 2000,
      icon: <Crown className="w-6 h-6" />,
      features: ["2,000 credits/month", "10 AI employees", "5 custom agents (20 credits each)", "Priority support", "Unlimited uploads"],
      popular: true
    },
    {
      id: "business",
      name: "Business",
      price_usd: 199,
      price_bdt: 21100,
      credits: 6000,
      icon: <Building className="w-6 h-6" />,
      features: ["6,000 credits/month", "All 20 AI employees", "Unlimited custom agents", "Dedicated support", "Unlimited everything", "API access"],
      popular: false
    }
  ];

  const creditPackages = [
    { id: "credits_100", credits: 100, price_usd: 6, price_bdt: 640 },
    { id: "credits_300", credits: 300, price_usd: 18, price_bdt: 1910 },
    { id: "credits_700", credits: 700, price_usd: 42, price_bdt: 4450 },
    { id: "credits_1500", credits: 1500, price_usd: 90, price_bdt: 9540 }
  ];

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
      }
    } catch {}
  };

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API}/plans`);
      if (!res.ok) return;
      // We need agent names - use the plans endpoint which is public
      // For agents we need auth, so use a static list
    } catch {}
    // Fetch agent list (if logged in) or use defaults
    if (token) {
      try {
        const res = await fetch(`${API}/agents`, { headers: { Authorization: `Bearer ${token}` }, credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          setAgents(data.filter(a => !a.is_custom && a.agent_id !== "agent_commander"));
        }
      } catch {}
    }
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
      const response = await fetch(`${API}/subscription`, {
        credentials: "include",
        headers
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
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
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
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
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
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
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
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white font-['Outfit']">Martian AI</span>
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
        </div>

        {/* Subscription Plans */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`bg-zinc-900/50 border-white/10 relative ${
                plan.popular ? "ring-2 ring-indigo-500" : ""
              } ${currentPlan === plan.id ? "border-emerald-500" : ""}`}
              data-testid={`plan-${plan.id}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-indigo-500 to-violet-500 text-white border-0">
                    Most Popular
                  </Badge>
                </div>
              )}
              {currentPlan === plan.id && (
                <div className="absolute -top-3 right-4">
                  <Badge className="bg-emerald-500 text-white border-0">Current Plan</Badge>
                </div>
              )}
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
            </Card>
          ))}
        </div>

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
          <p>All plans include access to all 20 AI employees and auto model selection.</p>
          <p className="mt-2">Questions? Contact support@maarsglobal.com</p>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
