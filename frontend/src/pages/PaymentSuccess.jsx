import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { CheckCircle, XCircle } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

const T = {
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { token } = useAuth();
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  const sessionId = searchParams.get("session_id");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const verifyPayment = async () => {
    try {
      const response = await fetch(`${API}/checkout/status/${sessionId}`, { headers });
      if (response.ok) {
        const data = await response.json();
        if (data.payment_status === "paid") {
          setStatus("success");
          setMessage(data.message || "Payment successful!");
          toast.success(data.message || "Payment successful!");
        } else {
          setStatus("pending");
          setMessage("Payment is being processed...");
        }
      } else {
        setStatus("error");
        setMessage("Failed to verify payment");
      }
    } catch {
      setStatus("error");
      setMessage("Error verifying payment");
    }
  };

  useEffect(() => {
    if (sessionId) verifyPayment();
    else { setStatus("error"); setMessage("No session ID found"); }
  }, [sessionId]);

  const Btn = ({ onClick, primary, children }) => (
    <button onClick={onClick}
      style={{ padding: "10px 24px", borderRadius: 10, border: primary ? "none" : `1px solid rgba(255,255,255,.12)`, background: primary ? `linear-gradient(135deg, ${T.violet}, ${T.indigo})` : "transparent", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
      {children}
    </button>
  );

  return (
    <div style={{ minHeight: "100vh", background: "#030712", display: "flex", flexDirection: "column" }}>
      <style>{STYLES}</style>
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <div style={{ maxWidth: 400, width: "100%", textAlign: "center", animation: "fadeUp .4s ease" }}>

          {status === "loading" && (
            <>
              <div style={{ width: 64, height: 64, border: `3px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .9s linear infinite", margin: "0 auto 20px" }} />
              <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", marginBottom: 8 }}>Verifying Payment…</h1>
              <p style={{ color: T.zinc, fontSize: 14 }}>Please wait while we confirm your payment.</p>
            </>
          )}

          {status === "success" && (
            <>
              <div style={{ width: 80, height: 80, borderRadius: "50%", background: "rgba(52,211,153,.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
                <CheckCircle size={40} style={{ color: T.green }} />
              </div>
              <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", marginBottom: 8 }}>Payment Successful!</h1>
              <p style={{ color: T.zinc, fontSize: 14, marginBottom: 28 }}>{message}</p>
              <Btn onClick={() => navigate("/dashboard")} primary>Go to Dashboard</Btn>
            </>
          )}

          {status === "pending" && (
            <>
              <div style={{ width: 64, height: 64, border: `3px solid ${T.amber}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .9s linear infinite", margin: "0 auto 20px" }} />
              <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", marginBottom: 8 }}>Processing Payment…</h1>
              <p style={{ color: T.zinc, fontSize: 14, marginBottom: 28 }}>{message}</p>
              <Btn onClick={() => verifyPayment()}>Check Again</Btn>
            </>
          )}

          {status === "error" && (
            <>
              <div style={{ width: 80, height: 80, borderRadius: "50%", background: "rgba(239,68,68,.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
                <XCircle size={40} style={{ color: T.red }} />
              </div>
              <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", marginBottom: 8 }}>Payment Issue</h1>
              <p style={{ color: T.zinc, fontSize: 14, marginBottom: 28 }}>{message}</p>
              <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
                <Btn onClick={() => navigate("/pricing")}>Try Again</Btn>
                <Btn onClick={() => navigate("/dashboard")} primary>Go to Dashboard</Btn>
              </div>
            </>
          )}
        </div>
      </div>
      <BrandFooter />
    </div>
  );
};

export default PaymentSuccess;
