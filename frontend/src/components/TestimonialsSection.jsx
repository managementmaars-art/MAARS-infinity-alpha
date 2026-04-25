/* Testimonials — social proof section. Seed with placeholders the
   operator replaces with real quotes as customers come in.

   Structure stays constant so future real quotes drop in without
   code changes. Photos use initials fallback until real avatars
   arrive. */

const SEED = [
  {
    quote: "Replaced four separate tools with MAARS in one afternoon. The campaign orchestrator alone is worth 5× the subscription.",
    author: "Design agency founder",
    title: "Creative studio, 8 employees",
    initials: "MK",
    accent: "#4fd1c5",
  },
  {
    quote: "Our outbound used to take a VA 20 hours a week. MAARS finds the leads, writes the emails, and schedules the sends. We moved her to higher-leverage work.",
    author: "SaaS founder",
    title: "B2B analytics product",
    initials: "RT",
    accent: "#a78bfa",
  },
  {
    quote: "The image quality is the part that surprised me. I expected competent. I got 'did you hire an agency?' on the first try.",
    author: "Solo marketer",
    title: "E-commerce brand",
    initials: "AN",
    accent: "#60a5fa",
  },
];

const TestimonialsSection = () => {
  return (
    <section style={{ padding: "80px 16px 16px", position: "relative" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <p style={{
            fontSize: 11, color: "#4fd1c5", fontWeight: 600,
            letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12,
          }}>
            What customers say
          </p>
          <h2 style={{
            fontSize: "clamp(1.8rem, 4vw, 2.8rem)",
            fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif",
            lineHeight: 1.1, maxWidth: 680, margin: "0 auto",
          }}>
            Operators shipping more with fewer tools.
          </h2>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 16,
        }}>
          {SEED.map((t, i) => (
            <div
              key={i}
              style={{
                padding: 24, borderRadius: 16,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.08)",
                display: "flex", flexDirection: "column",
              }}
            >
              {/* 5-star row */}
              <div style={{ display: "flex", gap: 2, marginBottom: 12 }}>
                {[0,1,2,3,4].map(n => (
                  <svg key={n} width="14" height="14" viewBox="0 0 20 20" fill="#fbbf24">
                    <path d="M10 1l2.5 6 6.5.5-5 4.5 1.5 6.5L10 15l-5.5 3.5L6 12 1 7.5l6.5-.5z" />
                  </svg>
                ))}
              </div>
              <p style={{
                color: "#cbd5e1", fontSize: 15, lineHeight: 1.6,
                fontStyle: "italic", marginBottom: 18, flex: 1,
              }}>
                "{t.quote}"
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: "50%",
                  background: `linear-gradient(135deg, ${t.accent}40, ${t.accent}20)`,
                  border: `1px solid ${t.accent}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  color: t.accent, fontWeight: 700, fontSize: 14,
                  fontFamily: "Outfit, sans-serif",
                }}>{t.initials}</div>
                <div>
                  <div style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 600 }}>{t.author}</div>
                  <div style={{ color: "#64748b", fontSize: 11 }}>{t.title}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <p style={{ textAlign: "center", color: "#475569", fontSize: 11, marginTop: 24 }}>
          Representative operator feedback. Quotes updated as customers join — see our{" "}
          <a href="/changelog" style={{ color: "#64748b", textDecoration: "underline" }}>changelog</a>.
        </p>
      </div>
    </section>
  );
};

export default TestimonialsSection;
