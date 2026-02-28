import { useState, useEffect, useRef } from "react";
import { Diamond, Plus, Settings, Gift, RefreshCw, X } from "lucide-react";
import { API, useAuth } from "../App";
import { toast } from "sonner";

const CREDIT_PACKAGES = [
  { credits: 100, price: 20, bonus: null },
  { credits: 250, price: 50, bonus: null },
  { credits: 500, price: 100, bonus: null },
  { credits: 3000, price: 500, bonus: "2500", featured: true },
  { credits: 6000, price: 1000, bonus: "5000", featured: true },
];

export const CreditsDisplay = () => {
  const { token } = useAuth();
  const [credits, setCredits] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [customAmount, setCustomAmount] = useState("");
  const [buying, setBuying] = useState(false);
  const dropdownRef = useRef(null);

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (!token) return;
    const fetchCredits = async () => {
      try {
        const [credRes, subRes] = await Promise.all([
          fetch(`${API}/credits`, { credentials: "include", headers }),
          fetch(`${API}/subscription`, { credentials: "include", headers }),
        ]);
        if (credRes.ok) setCredits(await credRes.json());
        if (subRes.ok) setSubscription(await subRes.json());
      } catch {}
    };
    fetchCredits();
    const interval = setInterval(fetchCredits, 30000);
    return () => clearInterval(interval);
  }, [token]);

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleBuyPackage = async (credits, price) => {
    setBuying(true);
    try {
      const res = await fetch(`${API}/checkout`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          type: "credits",
          credit_package_id: `pack_${credits}`,
          origin_url: window.location.origin,
          currency: "usd",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.checkout_url) window.location.href = data.checkout_url;
      } else {
        toast.error("Failed to start checkout");
      }
    } catch {
      toast.error("Checkout error");
    } finally {
      setBuying(false);
    }
  };

  if (!credits) return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-800/80 border border-white/10">
        <Diamond className="w-3.5 h-3.5 text-amber-400" />
        <span className="text-sm font-semibold text-zinc-500">--</span>
      </div>
      <button
        onClick={() => setShowBuyModal(true)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500 hover:bg-amber-400 text-black font-semibold text-xs transition-colors"
        data-testid="buy-credits-btn"
      >
        <Plus className="w-3 h-3" />
        Buy Credits
      </button>
    </div>
  );

  const totalCredits = credits.credits || 0;
  const planCredits = subscription?.plan?.credits || 0;
  const usedCredits = Math.max(0, planCredits - totalCredits);
  const planName = subscription?.plan?.name || "Free";

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        {/* Credit balance pill + Buy button */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-800/80 border border-white/10 hover:border-amber-500/30 transition-colors cursor-pointer"
            data-testid="credits-balance-btn"
          >
            <Diamond className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-sm font-semibold text-amber-400">{totalCredits.toFixed(2)}</span>
          </button>
          <button
            onClick={() => { setShowBuyModal(true); setShowDropdown(false); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500 hover:bg-amber-400 text-black font-semibold text-xs transition-colors"
            data-testid="buy-credits-btn"
          >
            <Plus className="w-3 h-3" />
            Buy Credits
          </button>
        </div>

        {/* Dropdown panel */}
        {showDropdown && (
          <div className="absolute right-0 top-full mt-2 w-72 rounded-xl bg-zinc-900 border border-white/10 shadow-2xl z-50 overflow-hidden" data-testid="credits-dropdown">
            <div className="p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-zinc-400">Available Credits</span>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  {planName}
                </span>
              </div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl font-bold text-amber-400">{totalCredits.toFixed(2)}</span>
                <Diamond className="w-4 h-4 text-amber-400" />
              </div>

              <div className="space-y-2.5 bg-zinc-800/50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Gift className="w-4 h-4 text-zinc-400" />
                    <span className="text-xs text-zinc-300">Free Credits</span>
                  </div>
                  <span className="text-xs text-zinc-400">{Math.min(totalCredits, 50).toFixed(2)} / 50</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-zinc-400" />
                    <span className="text-xs text-zinc-300">Monthly Credits</span>
                  </div>
                  <span className="text-xs text-zinc-400">{Math.max(0, totalCredits - 50).toFixed(2)} / {planCredits}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Diamond className="w-4 h-4 text-zinc-400" />
                    <span className="text-xs text-zinc-300">Top up Credits</span>
                  </div>
                  <span className="text-xs text-zinc-400">0.00</span>
                </div>
              </div>
            </div>

            <div className="border-t border-white/5 p-2 space-y-1">
              <a href="/pricing" className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white/5 transition-colors">
                <span className="text-sm text-zinc-300">Manage Subscriptions</span>
                <Settings className="w-4 h-4 text-zinc-500" />
              </a>
              <button
                onClick={() => { setShowBuyModal(true); setShowDropdown(false); }}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-semibold text-sm transition-colors"
                data-testid="buy-more-credits-btn"
              >
                Buy More Credits
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Buy Credits Modal */}
      {showBuyModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowBuyModal(false)}>
          <div className="w-full max-w-2xl bg-zinc-900 rounded-2xl border border-white/10 p-6 mx-4" onClick={e => e.stopPropagation()} data-testid="buy-credits-modal">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <Diamond className="w-6 h-6 text-amber-400" />
                <Plus className="w-4 h-4 text-amber-400 -ml-3 -mt-3" />
              </div>
              <button onClick={() => setShowBuyModal(false)} className="text-zinc-500 hover:text-white transition-colors" data-testid="close-buy-modal">
                <X className="w-5 h-5" />
              </button>
            </div>
            <h2 className="text-xl font-bold text-white mb-1">Buy more credits</h2>
            <p className="text-sm text-zinc-400 mb-5">
              Get <span className="text-amber-400 font-semibold">5 Credits</span> for just <span className="text-amber-400 font-semibold">$1</span>! Get our best value bundle with <span className="text-amber-400 font-semibold">20% OFF</span> or enter a custom amount.
            </p>

            <div className="grid grid-cols-5 gap-3 mb-5">
              {CREDIT_PACKAGES.map((pkg) => (
                <div
                  key={pkg.credits}
                  className={`rounded-xl border p-3 text-center flex flex-col items-center justify-between ${
                    pkg.featured
                      ? "border-amber-500/50 bg-amber-500/5"
                      : "border-white/10 bg-zinc-800/50"
                  }`}
                >
                  <Diamond className={`w-5 h-5 mb-2 ${pkg.featured ? "text-amber-400" : "text-zinc-500"}`} />
                  {pkg.bonus && (
                    <span className="text-[9px] text-amber-400 line-through mb-0.5">{pkg.bonus} credits</span>
                  )}
                  <span className={`text-sm font-bold ${pkg.featured ? "text-amber-400" : "text-white"}`}>
                    {pkg.credits.toLocaleString()} credits
                  </span>
                  <span className={`text-xs mt-0.5 ${pkg.featured ? "text-amber-400" : "text-zinc-400"}`}>
                    ${pkg.price.toLocaleString()}
                  </span>
                  <button
                    onClick={() => handleBuyPackage(pkg.credits, pkg.price)}
                    disabled={buying}
                    className={`mt-2 w-full py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                      pkg.featured
                        ? "bg-amber-500 hover:bg-amber-400 text-black"
                        : "bg-zinc-700 hover:bg-zinc-600 text-white"
                    }`}
                  >
                    Buy Now
                  </button>
                </div>
              ))}
            </div>

            <div className="flex gap-2 mb-4">
              <div className="flex-1 relative">
                <input
                  type="number"
                  placeholder="+ Enter custom amount ($)"
                  value={customAmount}
                  onChange={(e) => setCustomAmount(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg bg-zinc-800 border border-white/10 text-white text-sm placeholder-zinc-500 focus:outline-none focus:border-amber-500/50"
                  data-testid="custom-credits-input"
                />
              </div>
              <button
                onClick={() => {
                  const amt = parseFloat(customAmount);
                  if (amt >= 1) handleBuyPackage(amt * 5, amt);
                  else toast.error("Minimum $1");
                }}
                disabled={buying}
                className="px-6 py-2.5 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-white text-sm font-semibold transition-colors"
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
