/* Hub page at /alternatives — links to all competitor comparison pages.
   Primary purpose: internal linking for SEO + a landing spot for
   organic traffic that searches "[competitor] alternative". */
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";
import { ALL_ALTERNATIVES } from "./alternatives/configs";

const setSeoTags = () => {
  document.title = "AI Tool Alternatives — MAARS Command";
  const desc = "Compare MAARS Command against the other AI tools — Jasper, Copy.ai, Cursor, Lovable. Side-by-side pricing, features, and switch guides.";
  const setTag = (name, content) => {
    let el = document.querySelector(`meta[name="${name}"]`);
    if (!el) { el = document.createElement("meta"); el.setAttribute("name", name); document.head.appendChild(el); }
    el.setAttribute("content", content);
  };
  setTag("description", desc);
};

const AlternativesHub = () => {
  useEffect(() => { setSeoTags(); }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb" }}>
      <nav style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "14px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <img src="/branding/maars-logo.jpeg" alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover" }} />
            <span style={{ fontSize: 15, fontWeight: 700, color: "#fff" }}>MAARS Command</span>
          </Link>
          <div style={{ display: "flex", gap: 20, fontSize: 13, color: "#94a3b8" }}>
            <Link to="/pricing" style={{ color: "inherit", textDecoration: "none" }}>Pricing</Link>
            <Link to="/changelog" style={{ color: "inherit", textDecoration: "none" }}>Changelog</Link>
            <Link to="/login" style={{ color: "inherit", textDecoration: "none" }}>Login</Link>
          </div>
        </div>
      </nav>

      <section style={{ maxWidth: 1000, margin: "0 auto", padding: "72px 24px 40px", textAlign: "center" }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "6px 14px", borderRadius: 999,
          background: "rgba(79,209,197,0.15)", border: "1px solid rgba(79,209,197,0.3)",
          color: "#4fd1c5", fontSize: 11, fontWeight: 600, letterSpacing: "0.08em",
          textTransform: "uppercase", marginBottom: 20,
        }}>
          <Sparkles style={{ width: 12, height: 12 }} /> Comparisons
        </div>
        <h1 style={{
          fontSize: "clamp(2rem, 5vw, 3.2rem)", fontWeight: 800,
          color: "#fff", fontFamily: "Outfit, sans-serif",
          lineHeight: 1.1, marginBottom: 16,
        }}>
          MAARS vs. the alternatives
        </h1>
        <p style={{
          fontSize: "clamp(1rem, 1.3vw, 1.1rem)", color: "#94a3b8",
          lineHeight: 1.6, maxWidth: 620, margin: "0 auto",
        }}>
          Direct feature-by-feature comparisons. Honest claims. No inflated benchmarks.
        </p>
      </section>

      <section style={{ maxWidth: 1000, margin: "0 auto", padding: "8px 24px 80px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
          {ALL_ALTERNATIVES.map(({ slug, config, tagline }) => (
            <Link
              key={slug}
              to={`/alternatives/${slug}`}
              style={{
                padding: 24, borderRadius: 16,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.08)",
                textDecoration: "none", color: "inherit",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(79,209,197,0.3)"; e.currentTarget.style.background = "rgba(79,209,197,0.04)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"; e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                <span style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>
                  MAARS vs
                </span>
                <ArrowRight style={{ width: 14, height: 14, color: "#64748b" }} />
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", marginBottom: 10 }}>
                {config.competitorName}
              </h2>
              <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.55 }}>{tagline}</p>
            </Link>
          ))}
        </div>
      </section>

      <footer style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "20px 24px", color: "#475569", fontSize: 12, textAlign: "center" }}>
        <span>MAARS Command © 2026 · </span>
        <Link to="/privacy" style={{ color: "inherit" }}>Privacy</Link>
        <span> · </span>
        <Link to="/terms" style={{ color: "inherit" }}>Terms</Link>
      </footer>
    </div>
  );
};

export default AlternativesHub;
