/* Pricing comparison section — drops into LandingPage via import.
   Live-fetches /api/plans?billing=both so the landing page always
   reflects whatever the operator has set in Pricing Command Center.
   Monthly/annual toggle. Honest annual savings math. */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Check, ArrowRight, Sparkles } from "lucide-react";
import { API } from "../App";

const T = { teal: "#4fd1c5", violet: "#7c3aed", border: "rgba(255,255,255,0.08)" };

// Which plans get the "MOST POPULAR" ribbon. Keep narrow — too many
// highlights = no highlight. Ops can tune by adjusting this set.
const HIGHLIGHT_PLAN_IDS = new Set(["professional", "pro", "business"]);

const LandingPricingSection = () => {
  const [plans, setPlans] = useState([]);
  const [billing, setBilling] = useState("monthly"); // monthly | annual
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Single source: /api/plans returns both legacy dict + plans_v2 list.
    // We read plans_v2 here; PricingPage reads the legacy dict. One fetch,
    // one endpoint, zero drift — see backend/services/pricing_service.py.
    fetch(`${API}/plans`)
      .then((r) => (r.ok ? r.json() : { plans_v2: [] }))
      .then((d) => { setPlans(d.plans_v2 || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  // Show at most 4 plans on landing — keeps it scannable. Users who
  // want the full ladder click Pricing.
  const displayPlans = plans
    .filter((p) => p.plan_id !== "free" || (p.monthly?.price_usd ?? 0) === 0)
    .slice(0, 4);

  if (loading) return null;
  if (!displayPlans.length) return null;

  return (
    <section id="pricing" style={{ padding: "96px 16px 64px", position: "relative" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>

        {/* Heading */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "6px 14px", borderRadius: 999,
            background: `${T.teal}15`, border: `1px solid ${T.teal}30`,
            color: T.teal, fontSize: 11, fontWeight: 600, letterSpacing: "0.08em",
            textTransform: "uppercase", marginBottom: 20,
          }}>
            <Sparkles style={{ width: 12, height: 12 }} /> Simple pricing
          </div>
          <h2 style={{
            fontSize: "clamp(2rem, 5vw, 3.2rem)",
            fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif",
            lineHeight: 1.08, marginBottom: 16,
          }}>
            Pay for what you use.{" "}
            <span style={{
              background: `linear-gradient(135deg, ${T.teal}, #a78bfa)`,
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>Keep every credit.</span>
          </h2>
          <p style={{ color: "#94a3b8", fontSize: 16, maxWidth: 560, margin: "0 auto 24px" }}>
            Credits never expire. Cancel anytime. Annual plans save 20% + include bonus credits.
          </p>

          {/* Billing toggle */}
          <div style={{
            display: "inline-flex", padding: 4, borderRadius: 12,
            background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`,
            gap: 2,
          }}>
            {[
              { id: "monthly", label: "Monthly" },
              { id: "annual",  label: "Annual", badge: "–20%" },
            ].map((o) => (
              <button
                key={o.id}
                onClick={() => setBilling(o.id)}
                style={{
                  padding: "9px 20px", borderRadius: 9, border: "none",
                  fontSize: 13, fontWeight: 700, cursor: "pointer",
                  background: billing === o.id ? `linear-gradient(135deg, ${T.teal}, ${T.violet})` : "transparent",
                  color: billing === o.id ? "#030712" : "#94a3b8",
                  display: "inline-flex", alignItems: "center", gap: 8,
                  transition: "all 0.15s",
                }}
              >
                {o.label}
                {o.badge && (
                  <span style={{
                    fontSize: 10, padding: "2px 7px", borderRadius: 999,
                    background: billing === o.id ? "rgba(3,7,18,0.15)" : `${T.teal}20`,
                    color: billing === o.id ? "#030712" : T.teal, fontWeight: 700,
                  }}>{o.badge}</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Plan grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(auto-fit, minmax(${displayPlans.length > 3 ? 240 : 280}px, 1fr))`,
          gap: 16,
          marginBottom: 40,
        }}>
          {displayPlans.map((plan) => {
            const price = plan[billing] || plan.monthly || plan.annual || {};
            const isFree = plan.plan_id === "free" || (price.price_usd ?? 0) === 0;
            const isPopular = HIGHLIGHT_PLAN_IDS.has(plan.plan_id);
            return (
              <div
                key={plan.plan_id}
                style={{
                  position: "relative", padding: 28, borderRadius: 16,
                  background: isPopular ? `linear-gradient(180deg, ${T.teal}10, ${T.violet}08)` : "rgba(255,255,255,0.02)",
                  border: isPopular ? `1px solid ${T.teal}40` : `1px solid ${T.border}`,
                  boxShadow: isPopular ? `0 0 40px ${T.teal}15` : "none",
                  display: "flex", flexDirection: "column",
                }}
              >
                {isPopular && (
                  <div style={{
                    position: "absolute", top: -10, left: "50%", transform: "translateX(-50%)",
                    padding: "3px 12px", borderRadius: 999,
                    background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`,
                    color: "#030712", fontSize: 10, fontWeight: 700, letterSpacing: "0.08em",
                    textTransform: "uppercase",
                  }}>Most popular</div>
                )}

                <h3 style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", marginBottom: 8 }}>
                  {plan.name}
                </h3>

                {/* Price block */}
                <div style={{ marginBottom: 16 }}>
                  {isFree ? (
                    <>
                      <div style={{ fontSize: 40, fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif", lineHeight: 1 }}>
                        $0
                      </div>
                      <div style={{ color: "#94a3b8", fontSize: 13, marginTop: 4 }}>forever</div>
                    </>
                  ) : (
                    <>
                      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
                        <span style={{ fontSize: 40, fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif", lineHeight: 1 }}>
                          ${Math.round(billing === "annual" ? (price.monthly_equivalent_usd || 0) : (price.price_usd || 0))}
                        </span>
                        <span style={{ color: "#94a3b8", fontSize: 13 }}>/month</span>
                      </div>
                      {billing === "annual" && (price.savings_vs_monthly_usd > 0) && (
                        <div style={{ color: T.teal, fontSize: 12, marginTop: 4, fontWeight: 600 }}>
                          ${price.price_usd}/year · save ${price.savings_vs_monthly_usd}
                        </div>
                      )}
                      {billing === "monthly" && (
                        <div style={{ color: "#64748b", fontSize: 12, marginTop: 4 }}>
                          billed monthly
                        </div>
                      )}
                    </>
                  )}
                </div>

                {/* Credits highlight */}
                <div style={{
                  padding: "10px 14px", borderRadius: 10,
                  background: "rgba(255,255,255,0.04)",
                  border: `1px solid ${T.border}`, marginBottom: 18,
                }}>
                  <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 2 }}>
                    Credits
                  </div>
                  <div style={{ color: "#fff", fontWeight: 700, fontSize: 16, fontFamily: "Outfit, sans-serif" }}>
                    {(price.credits || 0).toLocaleString()}{billing === "annual" ? " / year" : " / month"}
                  </div>
                  {billing === "annual" && price.credit_bonus_months > 0 && (
                    <div style={{ fontSize: 10, color: T.teal, marginTop: 2 }}>
                      +{price.credit_bonus_months} bonus months
                    </div>
                  )}
                </div>

                {/* Feature list */}
                <ul style={{ listStyle: "none", padding: 0, margin: "0 0 24px", flex: 1 }}>
                  {(plan.features || []).slice(0, 5).map((f, i) => (
                    <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8, fontSize: 13, color: "#cbd5e1", lineHeight: 1.5 }}>
                      <Check style={{ width: 13, height: 13, color: T.teal, marginTop: 3, flexShrink: 0 }} />
                      <span>{f}</span>
                    </li>
                  ))}
                  {plan.max_agents > 0 && (
                    <li style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8, fontSize: 13, color: "#cbd5e1", lineHeight: 1.5 }}>
                      <Check style={{ width: 13, height: 13, color: T.teal, marginTop: 3, flexShrink: 0 }} />
                      <span>{plan.max_agents} AI agents</span>
                    </li>
                  )}
                  {plan.max_team_members > 1 && (
                    <li style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8, fontSize: 13, color: "#cbd5e1", lineHeight: 1.5 }}>
                      <Check style={{ width: 13, height: 13, color: T.teal, marginTop: 3, flexShrink: 0 }} />
                      <span>{plan.max_team_members} team seats</span>
                    </li>
                  )}
                </ul>

                {/* CTA */}
                <Link
                  to={`/register?plan=${plan.plan_id}&billing=${billing}`}
                  style={{
                    display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 6,
                    padding: "11px 20px", borderRadius: 10,
                    background: isPopular ? `linear-gradient(135deg, ${T.teal}, ${T.violet})` : "rgba(255,255,255,0.05)",
                    border: isPopular ? "none" : `1px solid ${T.border}`,
                    color: isPopular ? "#030712" : "#e2e8f0",
                    fontWeight: 700, fontSize: 13, textDecoration: "none",
                    boxShadow: isPopular ? `0 0 24px ${T.teal}35` : "none",
                    transition: "all 0.15s",
                  }}
                >
                  {isFree ? "Start free" : "Choose plan"} <ArrowRight style={{ width: 13, height: 13 }} />
                </Link>
              </div>
            );
          })}
        </div>

        {/* Under-grid trust strip */}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 10, fontSize: 12, color: "#64748b" }}>
          {[
            "Cancel anytime",
            "Credits never expire",
            "No long-term contract",
            "Stripe-secured payments",
            "GDPR & CAN-SPAM ready",
          ].map((item, i) => (
            <span key={i}>✓ {item}</span>
          ))}
        </div>

        {/* See-all-plans link */}
        <div style={{ textAlign: "center", marginTop: 24 }}>
          <Link to="/pricing" style={{
            color: "#94a3b8", fontSize: 13, textDecoration: "none",
            display: "inline-flex", alignItems: "center", gap: 6,
          }}>
            See the full pricing ladder + credit packages <ArrowRight style={{ width: 12, height: 12 }} />
          </Link>
        </div>
      </div>
    </section>
  );
};

export default LandingPricingSection;
