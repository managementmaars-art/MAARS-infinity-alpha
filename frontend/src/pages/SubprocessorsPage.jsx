/* Subprocessor list — GDPR transparency requirement.
   Every business that processes personal data on our behalf is listed
   here. Customers (especially EU B2B) check this before signing. */
import { Link } from "react-router-dom";

const SUBPROCESSORS = [
  { name: "Stripe, Inc.",       purpose: "Payment processing",        location: "USA", data_types: ["Payment info", "billing address"] },
  { name: "MongoDB Atlas",      purpose: "Database hosting",          location: "USA / EU", data_types: ["All platform data"] },
  { name: "Amazon Web Services", purpose: "Infrastructure hosting",   location: "Global", data_types: ["All platform data"] },
  { name: "SendGrid (Twilio)",  purpose: "Transactional + outbound email delivery", location: "USA", data_types: ["Email addresses", "message content"] },
  { name: "Resend",             purpose: "Transactional email delivery (alt)",   location: "USA", data_types: ["Email addresses", "message content"] },
  { name: "Twilio",             purpose: "SMS + voice delivery (optional)",      location: "USA", data_types: ["Phone numbers", "call transcripts"] },
  { name: "OpenAI",             purpose: "AI inference",              location: "USA", data_types: ["Prompt content", "generated output"] },
  { name: "Anthropic",          purpose: "AI inference",              location: "USA", data_types: ["Prompt content", "generated output"] },
  { name: "Google (Gemini)",    purpose: "AI inference",              location: "Global", data_types: ["Prompt content", "generated output"] },
  { name: "Microsoft",          purpose: "Text-to-speech (Edge TTS)", location: "Global", data_types: ["Text for speech synthesis"] },
  { name: "Deepgram",           purpose: "Speech-to-text",            location: "USA", data_types: ["Audio files"] },
  { name: "Apollo.io",          purpose: "Lead research (optional)",  location: "USA", data_types: ["Search queries"] },
  { name: "Hunter.io",          purpose: "Lead research fallback",    location: "USA", data_types: ["Domain queries"] },
  { name: "LinkedIn",           purpose: "OAuth-connected posting",   location: "USA", data_types: ["Post content"] },
  { name: "Sentry",             purpose: "Error monitoring (PII-scrubbed)", location: "USA / EU", data_types: ["Stack traces", "request metadata"] },
  { name: "Frankfurter (ECB)",  purpose: "FX rate lookup",            location: "EU",  data_types: ["None — public rates only"] },
];

const SubprocessorsPage = () => (
  <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb", padding: "48px 16px" }}>
    <div style={{ maxWidth: 860, margin: "0 auto" }}>
      <Link to="/privacy" style={{ color: "#60a5fa", fontSize: 14, textDecoration: "none" }}>← Back to Privacy Policy</Link>
      <h1 style={{ fontSize: 36, fontWeight: 800, color: "#fff", marginTop: 24, marginBottom: 10, fontFamily: "Outfit, sans-serif" }}>
        Subprocessors
      </h1>
      <p style={{ color: "#94a3b8", fontSize: 14, marginBottom: 32, lineHeight: 1.6 }}>
        The third parties MAARS engages to process personal data on your behalf. We notify customers at least 30 days before adding or replacing a subprocessor. Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}.
      </p>

      <div style={{
        overflow: "auto", border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14, background: "rgba(255,255,255,0.02)",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "rgba(255,255,255,0.03)", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
              <th style={{ padding: "12px 16px", textAlign: "left", color: "#94a3b8", fontWeight: 600 }}>Subprocessor</th>
              <th style={{ padding: "12px 16px", textAlign: "left", color: "#94a3b8", fontWeight: 600 }}>Purpose</th>
              <th style={{ padding: "12px 16px", textAlign: "left", color: "#94a3b8", fontWeight: 600 }}>Location</th>
              <th style={{ padding: "12px 16px", textAlign: "left", color: "#94a3b8", fontWeight: 600 }}>Data types</th>
            </tr>
          </thead>
          <tbody>
            {SUBPROCESSORS.map((s, i) => (
              <tr key={s.name} style={{ borderBottom: i < SUBPROCESSORS.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none" }}>
                <td style={{ padding: "12px 16px", color: "#e2e8f0", fontWeight: 600 }}>{s.name}</td>
                <td style={{ padding: "12px 16px", color: "#cbd5e1" }}>{s.purpose}</td>
                <td style={{ padding: "12px 16px", color: "#94a3b8" }}>{s.location}</td>
                <td style={{ padding: "12px 16px", color: "#94a3b8", fontSize: 12 }}>
                  {s.data_types.join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 style={{ fontSize: 20, fontWeight: 700, color: "#fff", marginTop: 40, marginBottom: 12 }}>
        Data Processing Agreement (DPA)
      </h2>
      <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.65 }}>
        MAARS offers a standard DPA for customers processing personal data under GDPR, UK GDPR, or comparable regulations. Our DPA incorporates the EU Standard Contractual Clauses (2021/914) and the UK International Data Transfer Addendum.
      </p>
      <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.65, marginTop: 12 }}>
        To request a countersigned DPA, email <strong style={{ color: "#e2e8f0" }}>privacy@marsgc.net</strong> from your registered account email with "DPA Request" in the subject.
      </p>

      <p style={{ color: "#475569", fontSize: 11, marginTop: 40, textAlign: "center" }}>
        <Link to="/privacy" style={{ color: "inherit" }}>Privacy</Link> · <Link to="/terms" style={{ color: "inherit" }}>Terms</Link>
      </p>
    </div>
  </div>
);

export default SubprocessorsPage;
