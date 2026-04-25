/* Cookie consent banner — GDPR / UK DMCC compliant.
   Shows on first visit to an EU/UK IP (best-effort geo via timezone).
   Persists choice in localStorage so it doesn't re-prompt. */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const STORAGE_KEY = "maars_cookie_consent_v1";

// Heuristic: if user's browser timezone is in EU/UK/EEA/Swiss, we show
// the strict banner. Non-EU users still get a banner (best practice)
// but with pre-accepted analytics that they can decline.
const EU_TIMEZONES = new Set([
  "Europe/London", "Europe/Dublin", "Europe/Paris", "Europe/Berlin",
  "Europe/Madrid", "Europe/Rome", "Europe/Amsterdam", "Europe/Brussels",
  "Europe/Vienna", "Europe/Warsaw", "Europe/Prague", "Europe/Budapest",
  "Europe/Stockholm", "Europe/Oslo", "Europe/Copenhagen", "Europe/Helsinki",
  "Europe/Athens", "Europe/Lisbon", "Europe/Zurich", "Europe/Luxembourg",
  "Europe/Bucharest", "Europe/Sofia", "Europe/Riga", "Europe/Tallinn",
  "Europe/Vilnius", "Europe/Bratislava", "Europe/Ljubljana", "Europe/Zagreb",
  "Europe/Malta", "Europe/Nicosia", "Atlantic/Reykjavik",
]);

function isEUuser() {
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    return EU_TIMEZONES.has(tz);
  } catch { return false; }
}

function loadConsent() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null"); }
  catch { return null; }
}

function saveConsent(obj) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      ...obj,
      savedAt: new Date().toISOString(),
      version: 1,
    }));
  } catch {}
}

const CookieConsent = () => {
  const [shown, setShown] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [pref, setPref] = useState({ essential: true, analytics: false, marketing: false });
  const isEU = isEUuser();

  useEffect(() => {
    const existing = loadConsent();
    if (!existing) setShown(true);
  }, []);

  const acceptAll = () => {
    saveConsent({ essential: true, analytics: true, marketing: true, mode: "accept_all" });
    setShown(false);
  };
  const rejectAll = () => {
    saveConsent({ essential: true, analytics: false, marketing: false, mode: "reject_all" });
    setShown(false);
  };
  const saveChoice = () => {
    saveConsent({ ...pref, mode: "custom" });
    setShown(false);
  };

  if (!shown) return null;

  return (
    <div
      role="dialog"
      aria-label="Cookie preferences"
      style={{
        position: "fixed", bottom: 16, left: 16, right: 16,
        zIndex: 1000, maxWidth: 720, margin: "0 auto",
        background: "rgba(5,10,20,0.97)", backdropFilter: "blur(12px)",
        border: "1px solid rgba(79,209,197,0.3)",
        borderRadius: 14, padding: 20,
        boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
        color: "#e5e7eb", fontSize: 14,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12, marginBottom: 12 }}>
        <div>
          <strong style={{ color: "#fff", fontSize: 15 }}>We value your privacy</strong>
          {isEU && <span style={{ marginLeft: 8, fontSize: 10, padding: "2px 6px", borderRadius: 999, background: "rgba(79,209,197,0.15)", color: "#4fd1c5" }}>GDPR</span>}
        </div>
      </div>

      <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.55, marginBottom: 14 }}>
        We use essential cookies to run MAARS. With your consent we also set analytics and marketing cookies to understand usage and improve the product. You can change your choice anytime. See our <Link to="/privacy" style={{ color: "#60a5fa" }}>Privacy Policy</Link>.
      </p>

      {expanded && (
        <div style={{ marginBottom: 14, padding: 12, background: "rgba(255,255,255,0.03)", borderRadius: 10, border: "1px solid rgba(255,255,255,0.06)" }}>
          {[
            { key: "essential", label: "Essential", desc: "Session, authentication, security. Required — can't disable.", disabled: true },
            { key: "analytics", label: "Analytics", desc: "Anonymized usage metrics to improve the product." },
            { key: "marketing", label: "Marketing", desc: "Personalized ads, retargeting, referral tracking." },
          ].map(({ key, label, desc, disabled }) => (
            <label key={key} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "8px 0", cursor: disabled ? "default" : "pointer" }}>
              <input
                type="checkbox"
                checked={pref[key]}
                disabled={disabled}
                onChange={(e) => setPref(p => ({ ...p, [key]: e.target.checked }))}
                style={{ marginTop: 2, accentColor: "#4fd1c5" }}
              />
              <div>
                <div style={{ color: disabled ? "#64748b" : "#e2e8f0", fontWeight: 600, fontSize: 13 }}>{label}</div>
                <div style={{ color: "#64748b", fontSize: 11 }}>{desc}</div>
              </div>
            </label>
          ))}
        </div>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        <button onClick={rejectAll} style={{
          padding: "8px 18px", borderRadius: 8, background: "transparent",
          border: "1px solid rgba(255,255,255,0.12)", color: "#94a3b8",
          fontSize: 12, fontWeight: 600, cursor: "pointer",
        }}>Reject non-essential</button>
        <button onClick={() => setExpanded(e => !e)} style={{
          padding: "8px 18px", borderRadius: 8, background: "transparent",
          border: "1px solid rgba(255,255,255,0.12)", color: "#94a3b8",
          fontSize: 12, fontWeight: 600, cursor: "pointer",
        }}>{expanded ? "Hide options" : "Customize"}</button>
        {expanded && (
          <button onClick={saveChoice} style={{
            padding: "8px 18px", borderRadius: 8, background: "rgba(124,58,237,0.4)",
            border: "1px solid rgba(124,58,237,0.6)", color: "#fff",
            fontSize: 12, fontWeight: 600, cursor: "pointer",
          }}>Save my choice</button>
        )}
        <button onClick={acceptAll} style={{
          padding: "8px 20px", borderRadius: 8,
          background: "linear-gradient(135deg, #4fd1c5, #7c3aed)",
          border: "none", color: "#030712",
          fontSize: 12, fontWeight: 700, cursor: "pointer",
          marginLeft: "auto",
        }}>Accept all</button>
      </div>
    </div>
  );
};

export default CookieConsent;
