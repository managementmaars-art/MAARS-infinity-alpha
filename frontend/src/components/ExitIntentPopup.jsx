/* Exit-intent popup — shows once, when the cursor leaves the top of
   the viewport (classic "about to close tab" signal). Desktop only —
   mobile has no cursor.

   Single offer: 200 bonus credits if you sign up now. Dismissed state
   persists in sessionStorage so refresh doesn't re-trigger. */
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { X, Sparkles, ArrowRight } from "lucide-react";

const STORAGE_KEY = "maars_exit_intent_shown_v1";

// Only fire on these marketing paths — not inside the app
const MARKETING_PATHS = new Set([
  "/", "/pricing", "/changelog",
  "/alternatives", "/alternatives/jasper", "/alternatives/copy-ai",
  "/alternatives/cursor", "/alternatives/lovable",
  "/blog",
]);

const ExitIntentPopup = () => {
  const [shown, setShown] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (sessionStorage.getItem(STORAGE_KEY) === "1") return;
    if (!MARKETING_PATHS.has(location.pathname)) return;
    // Don't show to logged-in users
    try { if (localStorage.getItem("token")) return; } catch {}

    const handler = (e) => {
      // Cursor leaving the top of the viewport = likely reaching for
      // the close tab / back button.
      if (e.clientY < 0 && !shown) {
        setShown(true);
        sessionStorage.setItem(STORAGE_KEY, "1");
      }
    };
    document.addEventListener("mouseleave", handler);
    return () => document.removeEventListener("mouseleave", handler);
  }, [shown, location.pathname]);

  if (!shown) return null;

  return (
    <div
      role="dialog"
      style={{
        position: "fixed", inset: 0, zIndex: 500,
        background: "rgba(3,7,18,0.8)", backdropFilter: "blur(12px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: 20, animation: "fadeIn 0.3s ease",
      }}
      onClick={() => setShown(false)}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: 460, width: "100%",
          background: "rgba(5,10,20,0.98)",
          border: "1px solid rgba(79,209,197,0.3)",
          borderRadius: 16, padding: 32,
          boxShadow: "0 30px 80px rgba(0,0,0,0.6)",
          position: "relative",
          color: "#e5e7eb",
        }}
      >
        <button
          onClick={() => setShown(false)}
          aria-label="Close"
          style={{
            position: "absolute", top: 14, right: 14,
            background: "none", border: "none", color: "#64748b",
            cursor: "pointer", padding: 4,
          }}
        >
          <X style={{ width: 18, height: 18 }} />
        </button>

        <div style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "5px 12px", borderRadius: 999,
          background: "rgba(79,209,197,0.15)",
          border: "1px solid rgba(79,209,197,0.3)",
          color: "#4fd1c5", fontSize: 10, fontWeight: 700,
          letterSpacing: "0.1em", textTransform: "uppercase",
          marginBottom: 16,
        }}>
          <Sparkles style={{ width: 11, height: 11 }} /> Wait — before you go
        </div>

        <h2 style={{
          fontSize: 26, fontWeight: 800, color: "#fff",
          fontFamily: "Outfit, sans-serif",
          lineHeight: 1.15, marginBottom: 12,
        }}>
          200 bonus credits on us.
        </h2>
        <p style={{ fontSize: 15, color: "#94a3b8", lineHeight: 1.55, marginBottom: 24 }}>
          Sign up today and we'll add <strong style={{ color: "#4fd1c5" }}>200 extra credits</strong> to your starter balance — enough to run a full cold-email campaign or generate ~10 premium images. No card required.
        </p>

        <button
          onClick={() => { setShown(false); navigate("/register?promo=exit200"); }}
          style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "13px 28px", borderRadius: 10,
            background: "linear-gradient(135deg, #4fd1c5, #7c3aed)",
            color: "#030712", fontSize: 14, fontWeight: 700,
            border: "none", cursor: "pointer",
            boxShadow: "0 0 30px rgba(79,209,197,0.35)",
          }}
        >
          Claim 200 bonus credits <ArrowRight style={{ width: 14, height: 14 }} />
        </button>

        <p style={{ fontSize: 11, color: "#475569", marginTop: 14 }}>
          One-time offer. No credit card. Cancel anytime.
        </p>
      </div>
    </div>
  );
};

export default ExitIntentPopup;
