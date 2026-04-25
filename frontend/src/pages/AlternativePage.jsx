/* Generic competitor-comparison page — parameterized by a `config`
   prop so the 4 MAARS-vs-X pages share one template.

   Each config file ({jasper,copyai,cursor,lovable}) supplies:
     - meta: title, subtitle, description, keyword
     - hero: headline, sub
     - theyAre + weAre: 3-line positioning summary
     - comparison: rows of [feature, them, us, usWins] with usWins=true
     - whySwitch: 4-5 cards
     - faq: [{q,a}]
     - cta: primary + secondary label
*/
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Check, X, ArrowRight, Sparkles, Zap, Shield, Target, DollarSign } from "lucide-react";

const T = {
  teal:  "#4fd1c5",
  violet:"#7c3aed",
  emerald: "#10b981",
  border:"rgba(255,255,255,0.08)",
};

const setSeoTags = (meta) => {
  // Basic on-page SEO — React Router doesn't do <Helmet> out of the box
  // and we don't want a dep. Direct DOM manipulation keeps it free.
  if (!meta) return;
  document.title = meta.title;
  const setTag = (name, content, isProperty = false) => {
    const attr = isProperty ? "property" : "name";
    let el = document.querySelector(`meta[${attr}="${name}"]`);
    if (!el) {
      el = document.createElement("meta");
      el.setAttribute(attr, name);
      document.head.appendChild(el);
    }
    el.setAttribute("content", content);
  };
  setTag("description", meta.description);
  setTag("og:title", meta.title, true);
  setTag("og:description", meta.description, true);
  setTag("og:type", "website", true);
  setTag("twitter:card", "summary_large_image");
  setTag("twitter:title", meta.title);
  setTag("twitter:description", meta.description);
};

const AlternativePage = ({ config }) => {
  useEffect(() => {
    setSeoTags(config.meta);
    // Structured data — FAQPage JSON-LD so Google gets rich snippets
    if (config.faq?.length) {
      const ld = document.createElement("script");
      ld.type = "application/ld+json";
      ld.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: config.faq.map(({ q, a }) => ({
          "@type": "Question",
          name: q,
          acceptedAnswer: { "@type": "Answer", text: a },
        })),
      });
      document.head.appendChild(ld);
      return () => { document.head.removeChild(ld); };
    }
  }, [config]);

  return (
    <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb" }}>
      {/* Nav */}
      <nav style={{ borderBottom: `1px solid ${T.border}`, padding: "14px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <img src="/branding/maars-logo.jpeg" alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover" }} />
            <span style={{ fontSize: 15, fontWeight: 700, color: "#fff" }}>MAARS Command</span>
          </Link>
          <div style={{ display: "flex", gap: 20, fontSize: 13, color: "#94a3b8" }}>
            <Link to="/pricing" style={{ color: "inherit", textDecoration: "none" }}>Pricing</Link>
            <Link to="/alternatives" style={{ color: "inherit", textDecoration: "none" }}>Alternatives</Link>
            <Link to="/login" style={{ color: "inherit", textDecoration: "none" }}>Login</Link>
            <Link to="/register" style={{
              color: "#030712", background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`,
              padding: "6px 14px", borderRadius: 8, fontWeight: 700, textDecoration: "none",
            }}>Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 980, margin: "0 auto", padding: "72px 24px 48px", textAlign: "center" }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "6px 14px", borderRadius: 999,
          background: `${T.teal}15`, border: `1px solid ${T.teal}30`,
          color: T.teal, fontSize: 11, fontWeight: 600, letterSpacing: "0.05em",
          textTransform: "uppercase", marginBottom: 20,
        }}>
          <Sparkles style={{ width: 12, height: 12 }} /> MAARS vs {config.competitorName}
        </div>
        <h1 style={{
          fontSize: "clamp(2rem, 5.5vw, 3.5rem)", fontWeight: 800,
          color: "#fff", fontFamily: "Outfit, sans-serif",
          lineHeight: 1.08, marginBottom: 18,
        }}>
          {config.hero.headline}
        </h1>
        <p style={{
          fontSize: "clamp(1rem, 1.4vw, 1.15rem)", color: "#94a3b8",
          lineHeight: 1.6, maxWidth: 680, margin: "0 auto 32px",
        }}>{config.hero.sub}</p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <Link to="/register" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "13px 28px", borderRadius: 10,
            background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`,
            color: "#030712", fontWeight: 700, textDecoration: "none", fontSize: 14,
            boxShadow: `0 0 28px ${T.teal}40`,
          }}>{config.cta?.primary || "Try MAARS Free"} <ArrowRight style={{ width: 14, height: 14 }} /></Link>
          <Link to="/pricing" style={{
            padding: "13px 28px", borderRadius: 10,
            background: "transparent", color: "#e2e8f0",
            border: `1px solid ${T.border}`, fontWeight: 600, textDecoration: "none", fontSize: 14,
          }}>{config.cta?.secondary || "See pricing"}</Link>
        </div>
      </section>

      {/* Positioning: Them vs Us */}
      <section style={{ maxWidth: 980, margin: "0 auto", padding: "32px 24px 56px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16 }}>
          <div style={{
            padding: 24, borderRadius: 16,
            background: "rgba(255,255,255,0.02)",
            border: `1px solid ${T.border}`,
          }}>
            <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>
              {config.competitorName}
            </div>
            <h3 style={{ fontSize: 18, color: "#cbd5e1", fontWeight: 700, marginBottom: 12, fontFamily: "Outfit, sans-serif" }}>
              {config.theyAre.headline}
            </h3>
            <p style={{ fontSize: 14, color: "#94a3b8", lineHeight: 1.6 }}>{config.theyAre.body}</p>
          </div>
          <div style={{
            padding: 24, borderRadius: 16,
            background: `linear-gradient(135deg, ${T.teal}10, ${T.violet}10)`,
            border: `1px solid ${T.teal}40`,
          }}>
            <div style={{ fontSize: 11, color: T.teal, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8, fontWeight: 700 }}>
              MAARS
            </div>
            <h3 style={{ fontSize: 18, color: "#fff", fontWeight: 700, marginBottom: 12, fontFamily: "Outfit, sans-serif" }}>
              {config.weAre.headline}
            </h3>
            <p style={{ fontSize: 14, color: "#cbd5e1", lineHeight: 1.6 }}>{config.weAre.body}</p>
          </div>
        </div>
      </section>

      {/* Comparison table */}
      <section style={{ maxWidth: 980, margin: "0 auto", padding: "16px 24px 56px" }}>
        <h2 style={{
          fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800,
          color: "#fff", fontFamily: "Outfit, sans-serif",
          textAlign: "center", marginBottom: 24,
        }}>Feature-by-feature</h2>
        <div style={{
          border: `1px solid ${T.border}`, borderRadius: 16, overflow: "hidden",
          background: "rgba(255,255,255,0.02)",
        }}>
          <div style={{
            display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr",
            padding: "14px 20px", borderBottom: `1px solid ${T.border}`,
            background: "rgba(255,255,255,0.03)",
            fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600,
          }}>
            <div>Feature</div>
            <div style={{ textAlign: "center" }}>{config.competitorName}</div>
            <div style={{ textAlign: "center", color: T.teal }}>MAARS</div>
          </div>
          {config.comparison.map((row, i) => (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr",
              padding: "16px 20px",
              borderBottom: i < config.comparison.length - 1 ? `1px solid ${T.border}` : "none",
              alignItems: "center", fontSize: 14,
            }}>
              <div style={{ color: "#e2e8f0", fontWeight: 500 }}>{row[0]}</div>
              <div style={{ textAlign: "center", color: "#94a3b8" }}>
                {row[1] === true ? <Check style={{ width: 16, height: 16, color: "#94a3b8", display: "inline" }} /> :
                 row[1] === false ? <X style={{ width: 16, height: 16, color: "#ef4444", display: "inline" }} /> :
                 row[1]}
              </div>
              <div style={{ textAlign: "center", color: row[3] ? T.teal : "#94a3b8", fontWeight: row[3] ? 700 : 400 }}>
                {row[2] === true ? <Check style={{ width: 18, height: 18, color: T.teal, display: "inline" }} /> :
                 row[2] === false ? <X style={{ width: 16, height: 16, color: "#ef4444", display: "inline" }} /> :
                 row[2]}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Why switch */}
      <section style={{ maxWidth: 980, margin: "0 auto", padding: "32px 24px 56px" }}>
        <h2 style={{
          fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800, color: "#fff",
          fontFamily: "Outfit, sans-serif", textAlign: "center", marginBottom: 24,
        }}>Why switch to MAARS</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
          {config.whySwitch.map((item, i) => {
            const Icon = [Zap, DollarSign, Shield, Target, Sparkles][i % 5];
            return (
              <div key={i} style={{
                padding: 20, borderRadius: 14,
                background: "rgba(255,255,255,0.03)",
                border: `1px solid ${T.border}`,
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: `${T.teal}15`, border: `1px solid ${T.teal}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 12,
                }}>
                  <Icon style={{ width: 16, height: 16, color: T.teal }} />
                </div>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 6, fontFamily: "Outfit, sans-serif" }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.55 }}>{item.body}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* FAQ */}
      {config.faq?.length > 0 && (
        <section style={{ maxWidth: 760, margin: "0 auto", padding: "32px 24px 56px" }}>
          <h2 style={{
            fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800, color: "#fff",
            fontFamily: "Outfit, sans-serif", textAlign: "center", marginBottom: 24,
          }}>Questions people ask</h2>
          {config.faq.map((f, i) => (
            <div key={i} style={{
              padding: "18px 0",
              borderBottom: i < config.faq.length - 1 ? `1px solid ${T.border}` : "none",
            }}>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 6 }}>{f.q}</h3>
              <p style={{ fontSize: 14, color: "#94a3b8", lineHeight: 1.6 }}>{f.a}</p>
            </div>
          ))}
        </section>
      )}

      {/* CTA */}
      <section style={{ maxWidth: 760, margin: "0 auto", padding: "16px 24px 80px", textAlign: "center" }}>
        <div style={{
          padding: 40, borderRadius: 20,
          background: `linear-gradient(135deg, ${T.teal}12, ${T.violet}12)`,
          border: `1px solid ${T.teal}30`,
        }}>
          <h2 style={{
            fontSize: "clamp(1.4rem, 3vw, 2rem)", fontWeight: 800, color: "#fff",
            fontFamily: "Outfit, sans-serif", marginBottom: 10,
          }}>
            Leave {config.competitorName}. Keep what works.
          </h2>
          <p style={{ fontSize: 15, color: "#cbd5e1", marginBottom: 22 }}>
            Sign up in 60 seconds. Cancel anytime. Free tier included.
          </p>
          <Link to="/register" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "13px 32px", borderRadius: 10,
            background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`,
            color: "#030712", fontWeight: 700, textDecoration: "none", fontSize: 14,
            boxShadow: `0 0 30px ${T.teal}40`,
          }}>{config.cta?.primary || "Try MAARS Free"} <ArrowRight style={{ width: 14, height: 14 }} /></Link>
        </div>
      </section>

      <footer style={{ borderTop: `1px solid ${T.border}`, padding: "20px 24px", color: "#475569", fontSize: 12, textAlign: "center" }}>
        <span>MAARS Command © 2026 · </span>
        <Link to="/privacy" style={{ color: "inherit" }}>Privacy</Link>
        <span> · </span>
        <Link to="/terms" style={{ color: "inherit" }}>Terms</Link>
        <span> · </span>
        <Link to="/changelog" style={{ color: "inherit" }}>Changelog</Link>
      </footer>
    </div>
  );
};

export default AlternativePage;
