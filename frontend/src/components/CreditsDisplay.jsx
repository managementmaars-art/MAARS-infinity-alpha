import { useState, useEffect, useRef, useCallback } from "react";
import { Diamond, Plus, Settings, Gift, RefreshCw, X, HelpCircle, Sparkles, ChevronDown } from "lucide-react";
import { API, useAuth } from "../App";
import { toast } from "sonner";

export const CreditsDisplay = () => {
  const { token } = useAuth();
  const [sub, setSub] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [customAmount, setCustomAmount] = useState("");
  const [buying, setBuying] = useState(false);
  const [currency, setCurrency] = useState("usd");
  const [creditPacks, setCreditPacks] = useState([]);
  const [exchangeRate, setExchangeRate] = useState(null);
  const dropdownRef = useRef(null);

  const fetchSub = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/subscription`, {
        credentials: "include",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setSub(await res.json());
    } catch (e) {
      console.error("Subscription fetch error:", e);
    }
  }, [token]);

  const fetchPackages = useCallback(async () => {
    try {
      const res = await fetch(`${API}/plans`);
      if (res.ok) {
        const data = await res.json();
        if (data.credit_packages) {
          const pkgs = Object.values(data.credit_packages).sort((a, b) => a.credits - b.credits);
          setCreditPacks(pkgs);
        }
      }
    } catch (e) {
      console.error("Plans fetch error:", e);
    }
  }, []);

  const fetchExchangeRate = useCallback(async () => {
    try {
      const res = await fetch(`${API}/exchange-rate`);
      if (res.ok) {
        const data = await res.json();
        setExchangeRate(data.usd_bdt);
      }
    } catch (e) {
      console.error("Exchange rate fetch error:", e);
    }
  }, []);

  useEffect(() => {
    fetchSub();
    fetchPackages();
    fetchExchangeRate();
    const interval = setInterval(fetchSub, 30000);
    return () => clearInterval(interval);
  }, [fetchSub, fetchPackages, fetchExchangeRate]);

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowDropdown(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleBuyPackage = async (pkg) => {
    setBuying(true);
    try {
      const res = await fetch(`${API}/checkout`, {
        method: "POST",
        credentials: "include",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "credits",
          package_id: pkg.id,
          origin_url: window.location.origin,
          currency,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.checkout_url) window.location.href = data.checkout_url;
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "Failed to start checkout");
      }
    } catch {
      toast.error("Checkout error");
    } finally {
      setBuying(false);
    }
  };

  const handleBuyCustom = async () => {
    const amount = parseFloat(customAmount);
    if (!amount || amount < 1) {
      toast.error("Minimum $1");
      return;
    }
    setBuying(true);
    try {
      const res = await fetch(`${API}/checkout`, {
        method: "POST",
        credentials: "include",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "credits",
          package_id: `custom_${Math.round(amount * 5)}`,
          origin_url: window.location.origin,
          currency: "usd",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.checkout_url) window.location.href = data.checkout_url;
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "Failed to start checkout");
      }
    } catch {
      toast.error("Checkout error");
    } finally {
      setBuying(false);
    }
  };

  const getPrice = (pkg) => {
    return currency === "bdt" ? pkg.price_bdt : pkg.price_usd;
  };

  const currencySymbol = currency === "bdt" ? "৳" : "$";

  const totalCredits = sub?.credits ?? 0;
  const planCredits = sub?.plan_info?.credits ?? 50;
  const planName = sub?.plan_info?.name ?? "Free";
  const freeCredits = Math.min(50, totalCredits);
  const topUpCredits = Math.max(0, totalCredits - planCredits);

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 hover:border-amber-500/60 transition-all cursor-pointer"
          data-testid="credits-balance-btn"
        >
          <Diamond className="w-4 h-4 text-amber-400" />
          <span className="text-sm font-bold text-amber-400">{sub ? totalCredits.toFixed(2) : "..."}</span>
          <span className="text-xs text-amber-500/60 font-medium ml-1 hidden sm:inline">+ Buy Credits</span>
        </button>

        {showDropdown && (
          <div className="absolute right-0 top-full mt-3 w-80 rounded-2xl bg-zinc-900 border border-white/10 shadow-[0_20px_60px_rgba(0,0,0,0.5)] z-[60] overflow-hidden" data-testid="credits-dropdown">
            <div className="p-5 pb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-zinc-400">Available Credits</span>
                  <HelpCircle className="w-3.5 h-3.5 text-zinc-600" />
                </div>
                <span className="px-3 py-1 text-xs font-bold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
                  {planName} <Sparkles className="w-3 h-3" />
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold text-amber-400">{totalCredits.toFixed(2)}</span>
                <Diamond className="w-5 h-5 text-amber-400" />
              </div>
            </div>

            <div className="mx-5 mb-4 rounded-xl bg-zinc-800/60 border border-white/5 divide-y divide-white/5">
              <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-2.5">
                  <Gift className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-300">Free Credits</span>
                </div>
                <span className="text-sm text-zinc-300 font-medium">{freeCredits.toFixed(2)} / 50</span>
              </div>
              <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-2.5">
                  <RefreshCw className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-300">Monthly Credits</span>
                </div>
                <span className="text-sm text-zinc-300 font-medium">{Math.max(0, totalCredits - topUpCredits - freeCredits).toFixed(2)} / {planCredits}</span>
              </div>
              <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-2.5">
                  <Diamond className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-300">Top up Credits</span>
                </div>
                <span className="text-sm text-zinc-300 font-medium">{topUpCredits.toFixed(2)}</span>
              </div>
            </div>

            <div className="border-t border-dashed border-white/10 p-4 space-y-2.5">
              <a href="/pricing" className="flex items-center justify-between w-full px-4 py-3 rounded-xl bg-zinc-800/60 border border-white/5 hover:bg-zinc-800 transition-colors">
                <span className="text-sm text-zinc-200 font-medium">Manage your Subscriptions</span>
                <Settings className="w-4 h-4 text-zinc-500" />
              </a>
              <button
                onClick={() => { setShowBuyModal(true); setShowDropdown(false); }}
                className="flex items-center justify-between w-full px-4 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-sm transition-colors"
                data-testid="buy-more-credits-btn"
              >
                Buy More Credits
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {showBuyModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={() => setShowBuyModal(false)}>
          <div className="w-full max-w-2xl bg-zinc-950 rounded-2xl border border-white/10 p-8 mx-4 shadow-2xl" onClick={e => e.stopPropagation()} data-testid="buy-credits-modal">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <Diamond className="w-7 h-7 text-amber-400" />
                  <Plus className="w-4 h-4 text-amber-400 -ml-2 -mt-3" />
                </div>
                <h2 className="text-2xl font-bold text-white">Buy more credits</h2>
              </div>
              <div className="flex items-center gap-3">
                {/* Currency Toggle */}
                <div className="flex items-center bg-zinc-800 rounded-lg border border-white/10 overflow-hidden" data-testid="currency-toggle">
                  <button
                    onClick={() => setCurrency("usd")}
                    className={`px-3 py-1.5 text-xs font-semibold transition-colors ${currency === "usd" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
                    data-testid="currency-usd-btn"
                  >
                    USD $
                  </button>
                  <button
                    onClick={() => setCurrency("bdt")}
                    className={`px-3 py-1.5 text-xs font-semibold transition-colors ${currency === "bdt" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
                    data-testid="currency-bdt-btn"
                  >
                    BDT ৳
                  </button>
                </div>
                <button onClick={() => setShowBuyModal(false)} className="text-zinc-500 hover:text-white transition-colors p-1" data-testid="close-buy-modal">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className={`grid gap-3 mb-6 ${creditPacks.length <= 3 ? "grid-cols-3" : creditPacks.length === 4 ? "grid-cols-4" : "grid-cols-5"}`}>
              {creditPacks.map((pkg, i) => {
                const isFeatured = i >= creditPacks.length - 2 && creditPacks.length > 2;
                const price = getPrice(pkg);
                return (
                  <div
                    key={pkg.id}
                    className={`rounded-xl border p-4 flex flex-col items-center justify-between text-center ${isFeatured ? "border-amber-500/50 bg-amber-500/5" : "border-white/10 bg-zinc-800/40"}`}
                    data-testid={`credit-pack-${pkg.id}`}
                  >
                    <Diamond className={`w-6 h-6 mb-3 ${isFeatured ? "text-amber-400" : "text-zinc-500"}`} />
                    <span className={`text-base font-bold ${isFeatured ? "text-amber-400" : "text-white"}`}>
                      {pkg.credits.toLocaleString()} credits
                    </span>
                    <span className={`text-sm mt-0.5 mb-3 ${isFeatured ? "text-amber-400/70" : "text-zinc-500"}`}>
                      {currencySymbol}{price.toLocaleString()}
                    </span>
                    <button
                      onClick={() => handleBuyPackage(pkg)}
                      disabled={buying}
                      className={`w-full py-2 rounded-full text-sm font-semibold transition-colors ${isFeatured ? "bg-amber-500 hover:bg-amber-400 text-black" : "bg-zinc-700 hover:bg-zinc-600 text-white"}`}
                      data-testid={`buy-pack-${pkg.id}`}
                    >
                      Buy Now
                    </button>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-3 mb-2">
              <input
                type="number"
                placeholder="+ Enter custom amount ($)"
                value={customAmount}
                onChange={(e) => setCustomAmount(e.target.value)}
                className="flex-1 px-5 py-3 rounded-xl bg-zinc-800/60 border border-white/10 text-white text-sm placeholder-zinc-500 focus:outline-none focus:border-amber-500/40"
                data-testid="custom-credits-input"
              />
              <button
                onClick={handleBuyCustom}
                disabled={buying}
                className="px-8 py-3 rounded-xl bg-zinc-700 hover:bg-zinc-600 text-white text-sm font-semibold transition-colors"
                data-testid="custom-buy-btn"
              >
                Buy
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
