import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { token } = useAuth();
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  
  const sessionId = searchParams.get("session_id");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    if (sessionId) {
      verifyPayment();
    } else {
      setStatus("error");
      setMessage("No session ID found");
    }
  }, [sessionId]);

  const verifyPayment = async () => {
    try {
      const response = await fetch(`${API}/checkout/status/${sessionId}`, {
        credentials: "include",
        headers
      });

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
    } catch (error) {
      setStatus("error");
      setMessage("Error verifying payment");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {status === "loading" && (
          <>
            <Loader2 className="w-16 h-16 text-indigo-400 mx-auto mb-4 animate-spin" />
            <h1 className="text-2xl font-bold text-white mb-2 font-['Outfit']">
              Verifying Payment...
            </h1>
            <p className="text-zinc-400">Please wait while we confirm your payment.</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-emerald-400" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2 font-['Outfit']">
              Payment Successful!
            </h1>
            <p className="text-zinc-400 mb-6">{message}</p>
            <Button
              onClick={() => navigate("/dashboard")}
              className="bg-gradient-to-r from-indigo-500 to-violet-500"
            >
              Go to Dashboard
            </Button>
          </>
        )}

        {status === "pending" && (
          <>
            <Loader2 className="w-16 h-16 text-amber-400 mx-auto mb-4 animate-spin" />
            <h1 className="text-2xl font-bold text-white mb-2 font-['Outfit']">
              Processing Payment...
            </h1>
            <p className="text-zinc-400 mb-6">{message}</p>
            <Button
              onClick={() => verifyPayment()}
              variant="outline"
              className="border-white/10"
            >
              Check Again
            </Button>
          </>
        )}

        {status === "error" && (
          <>
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2 font-['Outfit']">
              Payment Issue
            </h1>
            <p className="text-zinc-400 mb-6">{message}</p>
            <div className="flex gap-3 justify-center">
              <Button
                onClick={() => navigate("/pricing")}
                variant="outline"
                className="border-white/10"
              >
                Try Again
              </Button>
              <Button
                onClick={() => navigate("/dashboard")}
                className="bg-gradient-to-r from-indigo-500 to-violet-500"
              >
                Go to Dashboard
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PaymentSuccess;
