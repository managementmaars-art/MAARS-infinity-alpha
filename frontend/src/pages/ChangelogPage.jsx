/* Changelog — trust signal + retention + SEO.
   Fetches from /api/changelog (public). Markdown-light (double-newline
   paragraph split, no full parser to avoid deps). */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { API } from "../App";

const TAG_STYLES = {
  feature:     { bg: "rgba(79,209,197,0.12)",  fg: "#4fd1c5", label: "Feature" },
  improvement: { bg: "rgba(124,58,237,0.12)",  fg: "#a78bfa", label: "Improvement" },
  fix:         { bg: "rgba(245,158,11,0.12)",  fg: "#fbbf24", label: "Fix" },
  compliance:  { bg: "rgba(96,165,250,0.12)",  fg: "#60a5fa", label: "Compliance" },
};

const formatDate = (iso) => {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric",
    });
  } catch { return ""; }
};

const ChangelogPage = () => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/changelog?limit=50`)
      .then((r) => (r.ok ? r.json() : { data: [] }))
      .then((d) => { setEntries(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb" }}>
      {/* Header */}
      <nav style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "16px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <img src="/branding/maars-logo.jpeg" alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover" }} />
            <span style={{ fontSize: 15, fontWeight: 700, color: "#fff" }}>MAARS Command</span>
          </Link>
          <div style={{ display: "flex", gap: 20, fontSize: 13, color: "#94a3b8" }}>
            <Link to="/pricing" style={{ color: "inherit", textDecoration: "none" }}>Pricing</Link>
            <Link to="/changelog" style={{ color: "#fff", textDecoration: "none" }}>Changelog</Link>
            <Link to="/login" style={{ color: "inherit", textDecoration: "none" }}>Login</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 760, margin: "0 auto", padding: "56px 24px 32px" }}>
        <p style={{ fontSize: 12, color: "#4fd1c5", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12 }}>
          Changelog
        </p>
        <h1 style={{ fontSize: 40, fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif", marginBottom: 12, lineHeight: 1.1 }}>
          What we ship
        </h1>
        <p style={{ fontSize: 16, color: "#94a3b8", lineHeight: 1.6 }}>
          We publish every meaningful change. Subscribe to the <a href="/api/changelog" style={{ color: "#60a5fa" }}>JSON feed</a> for your own tracking.
        </p>
      </section>

      {/* Entries */}
      <section style={{ maxWidth: 760, margin: "0 auto", padding: "0 24px 80px" }}>
        {loading && (
          <div style={{ color: "#64748b", fontSize: 14 }}>Loading…</div>
        )}
        {!loading && entries.length === 0 && (
          <div style={{ padding: 40, textAlign: "center", color: "#64748b", border: "1px dashed rgba(255,255,255,0.08)", borderRadius: 14 }}>
            No changelog entries yet.
          </div>
        )}
        {entries.map((e, idx) => {
          const tag = TAG_STYLES[e.tag] || TAG_STYLES.feature;
          return (
            <article
              key={e.slug || idx}
              id={e.slug}
              style={{
                position: "relative",
                paddingLeft: 24,
                paddingBottom: 40,
                borderLeft: "2px solid rgba(255,255,255,0.06)",
              }}
            >
              <div
                style={{
                  position: "absolute", left: -7, top: 6,
                  width: 12, height: 12, borderRadius: "50%",
                  background: tag.fg, boxShadow: `0 0 10px ${tag.fg}60`,
                }}
              />
              <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <span style={{
                  fontSize: 10, fontWeight: 700, letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  padding: "3px 10px", borderRadius: 999,
                  background: tag.bg, color: tag.fg,
                  border: `1px solid ${tag.fg}30`,
                }}>{tag.label}</span>
                <span style={{ color: "#475569", fontSize: 12 }}>{formatDate(e.published_at)}</span>
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", marginBottom: 8 }}>
                {e.title}
              </h2>
              {e.summary && (
                <p style={{ color: "#cbd5e1", fontSize: 15, lineHeight: 1.6, marginBottom: 12 }}>{e.summary}</p>
              )}
              {e.body && (
                <div style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.7 }}>
                  {e.body.split("\n\n").map((p, i) => (
                    <p key={i} style={{ marginBottom: 10 }}>{p}</p>
                  ))}
                </div>
              )}
            </article>
          );
        })}
      </section>

      {/* Footer strip */}
      <footer style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "20px 24px", color: "#475569", fontSize: 12, textAlign: "center" }}>
        <span>MAARS Command © 2026 · </span>
        <Link to="/privacy" style={{ color: "inherit" }}>Privacy</Link>
        <span> · </span>
        <Link to="/terms" style={{ color: "inherit" }}>Terms</Link>
        <span> · </span>
        <a href="/api/status" style={{ color: "inherit" }}>Status</a>
      </footer>
    </div>
  );
};

export default ChangelogPage;
