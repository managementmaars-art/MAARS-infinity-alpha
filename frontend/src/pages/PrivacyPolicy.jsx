/* Privacy Policy — generic but jurisdiction-aware template covering
   GDPR / UK DPA / CCPA / PIPEDA / Australian Privacy Act.

   IMPORTANT: Before shipping, have counsel review this file. This is
   a functional baseline that satisfies 90% of SaaS requirements but
   is NOT legal advice. Update the [BRACKETS] placeholders with your
   actual business details. */
import { Link } from "react-router-dom";

const SECTIONS = [
  { id: "what", title: "1. What we collect" },
  { id: "why",  title: "2. Why we collect it" },
  { id: "share",title: "3. Who we share with" },
  { id: "store",title: "4. How long we keep it" },
  { id: "rights",title: "5. Your rights" },
  { id: "intl", title: "6. International transfers" },
  { id: "cookies", title: "7. Cookies" },
  { id: "contact", title: "8. Contact" },
];

const PrivacyPolicy = () => (
  <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb", padding: "48px 16px" }}>
    <div style={{ maxWidth: 780, margin: "0 auto" }}>
      <Link to="/" style={{ color: "#60a5fa", fontSize: 14, textDecoration: "none" }}>← Back to MAARS</Link>
      <h1 style={{ fontSize: 36, fontWeight: 800, color: "#fff", marginTop: 24, marginBottom: 8, fontFamily: "Outfit, sans-serif" }}>Privacy Policy</h1>
      <p style={{ color: "#94a3b8", fontSize: 13 }}>Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</p>

      <nav style={{ marginTop: 32, marginBottom: 40, padding: 16, background: "rgba(255,255,255,0.03)", borderRadius: 12, border: "1px solid rgba(255,255,255,0.08)" }}>
        <p style={{ fontSize: 11, color: "#64748b", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.1em" }}>Contents</p>
        {SECTIONS.map(s => (
          <a key={s.id} href={`#${s.id}`} style={{ display: "block", padding: "4px 0", color: "#a78bfa", fontSize: 13, textDecoration: "none" }}>{s.title}</a>
        ))}
      </nav>

      <section style={{ lineHeight: 1.7, fontSize: 15 }}>
        <p style={{ marginBottom: 24 }}>
          MAARS Global Corporation ("MAARS", "we", "us") operates the MAARS Command platform
          at maarscommand.com. This Privacy Policy explains what personal data we collect, how
          we use it, and the rights you have over it. We comply with the General Data Protection
          Regulation (EU/UK GDPR), the California Consumer Privacy Act (CCPA), Canada's PIPEDA,
          and similar laws in other jurisdictions where we offer the service.
        </p>

        <h2 id="what" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>1. What we collect</h2>
        <p>We collect only what's required to operate the service:</p>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li><strong>Account data</strong>: name, email, hashed password, organization name.</li>
          <li><strong>Usage data</strong>: which agents you invoked, credits consumed, timestamps, IP address, user agent.</li>
          <li><strong>Content</strong>: the prompts, messages, and files you submit to the platform. Stored to provide history; not used to train public models.</li>
          <li><strong>Payment data</strong>: processed by Stripe. MAARS never sees your card number; we store only the Stripe customer ID + last-four digits for your receipts.</li>
          <li><strong>Third-party integrations</strong>: if you connect LinkedIn / Google / Apollo / etc., we store the OAuth tokens required to make calls on your behalf.</li>
        </ul>

        <h2 id="why" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>2. Why we collect it</h2>
        <p>Legal bases under GDPR Art. 6:</p>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li><strong>Contract (Art. 6(1)(b))</strong>: to provide the service you signed up for.</li>
          <li><strong>Legitimate interest (Art. 6(1)(f))</strong>: fraud prevention, security monitoring, service improvement.</li>
          <li><strong>Consent (Art. 6(1)(a))</strong>: analytics beyond essential, marketing emails — you opt in; you can withdraw anytime.</li>
          <li><strong>Legal obligation (Art. 6(1)(c))</strong>: tax records, law-enforcement requests.</li>
        </ul>

        <h2 id="share" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>3. Who we share with</h2>
        <p>We do not sell personal data. We share only with:</p>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li>Infrastructure subprocessors (cloud hosting, CDN, monitoring).</li>
          <li>Payment processors (Stripe).</li>
          <li>AI inference providers we route your requests through — only the request payload, never your identity, is sent.</li>
          <li>Email delivery providers for transactional email.</li>
          <li>Law enforcement, when legally compelled.</li>
        </ul>
        <p style={{ marginTop: 12 }}>A full subprocessor list is available upon request — email privacy@marsgc.net.</p>

        <h2 id="store" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>4. How long we keep it</h2>
        <p>Active account data for as long as your account is active. After you delete your account, we soft-retain data for 30 days (reversible), then permanently purge. Backups are rotated out within 90 days. Tax records retained up to 7 years where legally required.</p>

        <h2 id="rights" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>5. Your rights</h2>
        <p>You have the right to:</p>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li>Access your data — <Link to="/settings/privacy" style={{ color: "#60a5fa" }}>request export</Link> (GDPR Art. 15, CCPA §1798.110).</li>
          <li>Correct inaccurate data — edit in your settings or email privacy@marsgc.net.</li>
          <li>Delete your data — <Link to="/settings/privacy" style={{ color: "#60a5fa" }}>request deletion</Link> (GDPR Art. 17, CCPA §1798.105).</li>
          <li>Object to processing for marketing / profiling — opt out in your email preferences.</li>
          <li>Data portability — exports are JSON (machine-readable).</li>
          <li>Lodge a complaint with your local supervisory authority (e.g., the UK ICO, Irish DPC).</li>
        </ul>

        <h2 id="intl" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>6. International data transfers</h2>
        <p>MAARS infrastructure is operated globally. When data moves between jurisdictions we rely on the EU Standard Contractual Clauses (2021/914) and equivalent safeguards. If you're in the UK we additionally apply the UK International Data Transfer Addendum.</p>

        <h2 id="cookies" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>7. Cookies</h2>
        <p>We use only essential cookies for session management and security. Analytics and marketing cookies require your consent via our cookie banner. You can change consent anytime at <Link to="/cookies" style={{ color: "#60a5fa" }}>/cookies</Link>.</p>

        <h2 id="contact" style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>8. Contact</h2>
        <p>Data Protection inquiries: <strong>privacy@marsgc.net</strong></p>
        <p>General inquiries: <strong>management.maars@marsgc.net</strong></p>
        <p style={{ marginTop: 24, padding: 16, background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.2)", borderRadius: 10, fontSize: 13, color: "#fbbf24" }}>
          EU/UK residents: we do not currently have an appointed EU Representative under Art. 27 GDPR. If you're established in the EEA/UK and would like to exercise your rights, use the contact above or file a complaint with your local authority.
        </p>
      </section>
    </div>
  </div>
);

export default PrivacyPolicy;
