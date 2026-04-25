/* Terms of Service — SaaS baseline ToS.
   Review with counsel before launch. Plain-English, defensive posture. */
import { Link } from "react-router-dom";

const TermsOfService = () => (
  <div style={{ minHeight: "100vh", background: "#030712", color: "#e5e7eb", padding: "48px 16px" }}>
    <div style={{ maxWidth: 780, margin: "0 auto" }}>
      <Link to="/" style={{ color: "#60a5fa", fontSize: 14, textDecoration: "none" }}>← Back to MAARS</Link>
      <h1 style={{ fontSize: 36, fontWeight: 800, color: "#fff", marginTop: 24, marginBottom: 8, fontFamily: "Outfit, sans-serif" }}>Terms of Service</h1>
      <p style={{ color: "#94a3b8", fontSize: 13 }}>Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</p>

      <section style={{ lineHeight: 1.7, fontSize: 15, marginTop: 32 }}>

        <p style={{ marginBottom: 24 }}>
          These Terms govern your access to and use of MAARS Command ("the Service"), operated
          by MAARS Global Corporation. By creating an account or using the Service you agree to
          these Terms. If you don't agree, don't use the Service.
        </p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>1. Account & eligibility</h2>
        <p>You must be at least 18 and legally able to contract in your jurisdiction. One person or legal entity per account. You're responsible for keeping your credentials secure.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>2. Subscription & billing</h2>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li>Plans are billed monthly or annually in advance.</li>
          <li>Credits consumed during a billing cycle are non-refundable after use.</li>
          <li>Unused credits roll over while your subscription is active.</li>
          <li>Cancel anytime. Cancellation takes effect at the end of your current billing period.</li>
          <li>We may change prices with 30 days' notice; existing paid periods honor the price at purchase.</li>
          <li>Failed charges result in a 7-day grace, then service pause, then data retention per our Privacy Policy.</li>
        </ul>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>3. Acceptable use</h2>
        <p>You agree NOT to use the Service to:</p>
        <ul style={{ marginTop: 8, paddingLeft: 20 }}>
          <li>Send unsolicited bulk email, SMS, or calls in violation of CAN-SPAM, CASL, GDPR, UK DMCC, Australian Spam Act, or equivalent laws.</li>
          <li>Impersonate real people, organizations, or government entities.</li>
          <li>Generate content that is illegal, defamatory, infringes IP, or constitutes harassment.</li>
          <li>Circumvent rate limits or reverse-engineer the Service.</li>
          <li>Reuse, resell, or mirror the Service or its outputs as a competing product without an explicit reseller agreement.</li>
          <li>Use the Service for surveillance, mass targeting of minors, or credential theft.</li>
        </ul>
        <p style={{ marginTop: 12 }}>Violations may result in immediate suspension without refund and reporting to law enforcement where required.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>4. Content ownership</h2>
        <p>You own the content you create using the Service. MAARS retains no rights in your outputs beyond what's necessary to provide the Service. We may process your content only to deliver, maintain, and improve the Service (and to meet legal obligations).</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>5. AI outputs</h2>
        <p>AI models produce probabilistic outputs and can be wrong, biased, or fabricate information. You are responsible for reviewing and verifying outputs before relying on them. Do not use the Service for medical, legal, or financial advice requiring a licensed professional.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>6. Third-party integrations</h2>
        <p>When you connect LinkedIn, Stripe, or other third-party services, you agree to those services' terms. MAARS is not responsible for third-party outages, policy changes, or account actions those services take against you.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>7. Warranty disclaimer</h2>
        <p>The Service is provided "as is" and "as available". To the fullest extent permitted by law, we disclaim all warranties, express or implied, including fitness for a particular purpose, non-infringement, and uninterrupted availability.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>8. Limitation of liability</h2>
        <p>To the extent permitted by law, MAARS's total liability for any claim arising from or related to the Service is limited to the fees you paid to MAARS in the 12 months preceding the claim. We are not liable for indirect, consequential, or incidental damages including lost profits or data.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>9. Indemnification</h2>
        <p>You agree to indemnify MAARS against claims arising from your use of the Service, your content, or your violation of these Terms or applicable law.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>10. Termination</h2>
        <p>Either party may terminate for any reason with notice. We may terminate immediately for material breach (e.g., prohibited use under Section 3). On termination, your account is handled per our Privacy Policy (30-day soft retention, then purge).</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>11. Governing law & disputes</h2>
        <p>These Terms are governed by the laws of MAARS's primary operating jurisdiction, without regard to conflict-of-law rules. Disputes go to binding arbitration on an individual basis; no class actions. EU/UK consumers retain their statutory rights.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>12. Changes</h2>
        <p>We may update these Terms. Material changes are notified at least 30 days in advance via email and in-app banner. Continued use after the effective date means you accept the new Terms.</p>

        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#fff", marginTop: 32, marginBottom: 12 }}>13. Contact</h2>
        <p>Legal: <strong>legal@marsgc.net</strong></p>
        <p>General: <strong>management.maars@marsgc.net</strong></p>
      </section>
    </div>
  </div>
);

export default TermsOfService;
