import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, User, ArrowLeft, ArrowRight, Eye, EyeOff, Zap, Bot, Shield, Globe } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL?.trim() || "http://localhost:8000";

/* ── Canvas ambient panel (3-layer: orbs + neural + particles) ──────────── */
function AuthPanel() {
  const orbRef   = useRef(null);
  const netRef   = useRef(null);
  const partRef  = useRef(null);

  /* Layer 1 — atmospheric orbs */
  useEffect(() => {
    const canvas = orbRef.current; if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const W = canvas.width, H = canvas.height;
    const orbs = Array.from({ length: 5 }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: 80 + Math.random() * 140,
      vx: (Math.random() - 0.5) * 0.18, vy: (Math.random() - 0.5) * 0.18,
      hue: Math.random() < 0.5 ? 173 : 265,
      alpha: 0.04 + Math.random() * 0.05,
    }));
    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      orbs.forEach(o => {
        o.x += o.vx; o.y += o.vy;
        if (o.x < -o.r) o.x = W + o.r; if (o.x > W + o.r) o.x = -o.r;
        if (o.y < -o.r) o.y = H + o.r; if (o.y > H + o.r) o.y = -o.r;
        const g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
        g.addColorStop(0, `hsla(${o.hue},80%,65%,${o.alpha})`);
        g.addColorStop(1, "transparent");
        ctx.beginPath(); ctx.arc(o.x, o.y, o.r, 0, Math.PI * 2);
        ctx.fillStyle = g; ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  /* Layer 2 — neural network */
  useEffect(() => {
    const canvas = netRef.current; if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const W = canvas.width, H = canvas.height;
    const nodes = Array.from({ length: 32 }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.22, vy: (Math.random() - 0.5) * 0.22,
      r: 1.5 + Math.random() * 2, pulse: Math.random() * Math.PI * 2,
    }));
    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      nodes.forEach(n => {
        n.x += n.vx; n.y += n.vy; n.pulse += 0.025;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;
      });
      nodes.forEach((a, i) => nodes.slice(i + 1).forEach(b => {
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 110) {
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(79,209,197,${(1 - d / 110) * 0.12})`;
          ctx.lineWidth = 0.6; ctx.stroke();
        }
      }));
      nodes.forEach(n => {
        const glow = 0.5 + 0.5 * Math.sin(n.pulse);
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(79,209,197,${0.2 + glow * 0.3})`; ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  /* Layer 3 — rising data particles */
  useEffect(() => {
    const canvas = partRef.current; if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const W = canvas.width, H = canvas.height;
    const chars = "01アイウエオΨΩ∞∇λφ";
    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * W, y: H + Math.random() * H,
      speed: 0.3 + Math.random() * 0.5,
      char: chars[Math.floor(Math.random() * chars.length)],
      opacity: Math.random() * 0.18,
      size: 8 + Math.random() * 6,
    }));
    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      ctx.font = `${particles[0]?.size || 10}px monospace`;
      particles.forEach(p => {
        p.y -= p.speed;
        if (p.y < -20) { p.y = H + 20; p.x = Math.random() * W; p.char = chars[Math.floor(Math.random() * chars.length)]; }
        ctx.font = `${p.size}px monospace`;
        ctx.fillStyle = `rgba(79,209,197,${p.opacity})`;
        ctx.fillText(p.char, p.x, p.y);
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  const perks = [
    { icon: Bot,    title: "458+ AI Agents",       sub: "Specialized for every role" },
    { icon: Globe,  title: "175,000+ Models",       sub: "33 providers connected" },
    { icon: Zap,    title: "Smart Auto-Routing",    sub: "Task & credit aware" },
    { icon: Shield, title: "Enterprise Governance", sub: "Trust scoring built-in" },
  ];

  return (
    <div style={{ position: "relative", width: "52%", minHeight: "100vh", background: "#020810", overflow: "hidden", flexShrink: 0 }}>
      <canvas ref={orbRef}  style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }} />
      <canvas ref={netRef}  style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }} />
      <canvas ref={partRef} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }} />

      {/* Grid overlay */}
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(79,209,197,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(79,209,197,0.03) 1px, transparent 1px)", backgroundSize: "48px 48px", pointerEvents: "none" }} />

      <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", justifyContent: "center", height: "100%", padding: "60px 56px" }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 56 }}>
          <div style={{ position: "relative" }}>
            <img src="/branding/maars-logo.jpeg" alt="MAARS"
              style={{ width: 46, height: 46, borderRadius: 13, objectFit: "cover", border: "1.5px solid rgba(79,209,197,0.35)", boxShadow: "0 0 28px rgba(79,209,197,0.3), 0 0 60px rgba(79,209,197,0.1)" }} />
            <div style={{ position: "absolute", inset: -4, borderRadius: 17, border: "1px solid rgba(79,209,197,0.15)", animation: "rp_ring 3s linear infinite", pointerEvents: "none" }} />
          </div>
          <div>
            <h2 style={{ color: "#f1f5f9", fontWeight: 800, fontSize: 19, fontFamily: "Outfit, sans-serif", lineHeight: 1.1, margin: 0 }}>MAARS Command</h2>
            <p style={{ color: "#4fd1c5", fontSize: 10, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", margin: 0 }}>AI Command Center</p>
          </div>
        </div>

        {/* Headline */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#4fd1c5", animation: "rp_dot 1.8s ease-in-out infinite" }} />
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.2em", textTransform: "uppercase", color: "#4fd1c5" }}>Join 12,000+ Teams</span>
          </div>
          <h1 style={{ fontSize: "clamp(1.9rem, 3vw, 2.8rem)", fontWeight: 800, fontFamily: "Outfit, sans-serif", lineHeight: 1.1, color: "#f1f5f9", margin: "0 0 14px" }}>
            Build your{" "}
            <span style={{ background: "linear-gradient(135deg, #4fd1c5, #a78bfa, #60a5fa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundSize: "200% 200%", animation: "rp_grad 4s ease infinite" }}>AI team</span>
            <br />in minutes.
          </h1>
          <p style={{ fontSize: 15, color: "#4a5568", lineHeight: 1.7, maxWidth: 380 }}>
            Free to start. Instant access to 458+ specialized agents, enterprise governance, and 175,000+ models.
          </p>
        </div>

        {/* Perk rows */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {perks.map(({ icon: Icon, title, sub }, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 16px", borderRadius: 14, background: "rgba(79,209,197,0.04)", border: "1px solid rgba(79,209,197,0.08)", backdropFilter: "blur(8px)", transition: "all 0.2s" }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(79,209,197,0.1)", border: "1px solid rgba(79,209,197,0.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon style={{ width: 16, height: 16, color: "#4fd1c5" }} />
              </div>
              <div>
                <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", margin: 0, lineHeight: 1.2 }}>{title}</p>
                <p style={{ fontSize: 11, color: "#475569", margin: 0 }}>{sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Live agents badge */}
        <div style={{ marginTop: 36, display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 12px", borderRadius: 20, background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.2)" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", animation: "rp_dot 1.4s ease-in-out infinite" }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: "#34d399", letterSpacing: "0.06em" }}>458 AGENTS ONLINE</span>
          </div>
          <span style={{ fontSize: 11, color: "#334155" }}>Free tier available</span>
        </div>
      </div>

      <style>{`
        @keyframes rp_ring { to { transform: rotate(360deg); } }
        @keyframes rp_dot  { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(1.4); } }
        @keyframes rp_grad { 0%,100% { background-position:0% 50%; } 50% { background-position:100% 50%; } }
      `}</style>
    </div>
  );
}

/* ── Register page ─────────────────────────────────────────────────────────── */
const RegisterPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [name,     setName]      = useState("");
  const [email,    setEmail]     = useState("");
  const [password, setPassword]  = useState("");
  const [showPass, setShowPass]  = useState(false);
  const [loading,  setLoading]   = useState(false);
  const [focused,  setFocused]   = useState(null);

  const handleGoogleSignup = () => { window.location.href = `${BACKEND_URL}/api/auth/google`; };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        login(data.user, data.token);
        toast.success("Account created successfully!");
        navigate("/dashboard");
      } else {
        toast.error(data.detail || "Registration failed");
      }
    } catch { toast.error("Registration failed. Please try again."); }
    finally  { setLoading(false); }
  };

  const inputStyle = (field) => ({
    paddingLeft: 38, height: 46, borderRadius: 11, fontSize: 14,
    background: "rgba(8,15,28,0.7)",
    border: `1px solid ${focused === field ? "rgba(79,209,197,0.5)" : "rgba(255,255,255,0.08)"}`,
    boxShadow: focused === field ? "0 0 0 3px rgba(79,209,197,0.08), 0 0 16px rgba(79,209,197,0.12)" : "none",
    color: "#e2e8f0",
    outline: "none",
    transition: "all 0.2s",
  });

  return (
    <div style={{ minHeight: "100vh", background: "#030712", display: "flex", flexDirection: "column" }}>
      <div style={{ flex: 1, display: "flex" }}>

        {/* Left animated panel */}
        <div className="hidden lg:block" style={{ flexShrink: 0, width: "52%" }}>
          <AuthPanel />
        </div>

        {/* Right form panel */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "40px 8vw", background: "rgba(4,8,18,0.85)", backdropFilter: "blur(24px)", borderLeft: "1px solid rgba(255,255,255,0.05)", position: "relative", overflow: "hidden" }}>
          {/* Ambient glow blobs */}
          <div style={{ position: "absolute", top: "10%", right: "5%", width: 200, height: 200, borderRadius: "50%", background: "radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", bottom: "15%", left: "5%",  width: 160, height: 160, borderRadius: "50%", background: "radial-gradient(circle, rgba(79,209,197,0.05) 0%, transparent 70%)", pointerEvents: "none" }} />

          <Link to="/"
            data-testid="back-to-home"
            style={{ position: "relative", zIndex: 1, display: "inline-flex", alignItems: "center", gap: 7, fontSize: 13, color: "#475569", textDecoration: "none", marginBottom: 40, transition: "color 0.15s", width: "fit-content" }}
            onMouseEnter={e => e.currentTarget.style.color = "#4fd1c5"}
            onMouseLeave={e => e.currentTarget.style.color = "#475569"}>
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back to home
          </Link>

          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2 mb-8" style={{ position: "relative", zIndex: 1 }}>
            <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{ width: 32, height: 32, borderRadius: 8, objectFit: "cover" }} />
            <span style={{ color: "#f1f5f9", fontWeight: 700, fontFamily: "Outfit, sans-serif", fontSize: 16 }}>MAARS Command</span>
          </div>

          <div style={{ maxWidth: 360, width: "100%", position: "relative", zIndex: 1 }}>
            <div style={{ marginBottom: 30 }}>
              <h1 style={{ fontSize: 26, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: "0 0 6px" }}>Create your account</h1>
              <p style={{ fontSize: 14, color: "#475569" }}>Free to start · No credit card required</p>
            </div>

            {/* Google */}
            <button type="button" onClick={handleGoogleSignup}
              data-testid="google-register-btn"
              style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 10, padding: "13px 0", borderRadius: 11, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)", color: "#e2e8f0", fontSize: 14, fontWeight: 600, cursor: "pointer", transition: "all 0.2s", marginBottom: 22, position: "relative", overflow: "hidden" }}
              onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.07)"; e.currentTarget.style.borderColor = "rgba(79,209,197,0.25)"; e.currentTarget.style.boxShadow = "0 0 20px rgba(79,209,197,0.08)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; e.currentTarget.style.boxShadow = "none"; }}>
              <svg style={{ width: 18, height: 18, flexShrink: 0 }} viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            {/* Divider */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 22 }}>
              <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.07)" }} />
              <span style={{ fontSize: 12, color: "#334155" }}>or register with email</span>
              <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.07)" }} />
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label htmlFor="name" style={{ fontSize: 11, fontWeight: 700, color: "#475569", display: "block", marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>Full Name</label>
                <div style={{ position: "relative" }}>
                  <User style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", width: 15, height: 15, color: focused === "name" ? "#4fd1c5" : "#475569", transition: "color 0.2s", pointerEvents: "none" }} />
                  <input id="name" type="text" placeholder="Your full name"
                    value={name} onChange={e => setName(e.target.value)}
                    onFocus={() => setFocused("name")} onBlur={() => setFocused(null)}
                    style={{ ...inputStyle("name"), outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }}
                    required data-testid="register-name-input" />
                </div>
              </div>

              <div>
                <label htmlFor="email" style={{ fontSize: 11, fontWeight: 700, color: "#475569", display: "block", marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>Email Address</label>
                <div style={{ position: "relative" }}>
                  <Mail style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", width: 15, height: 15, color: focused === "email" ? "#4fd1c5" : "#475569", transition: "color 0.2s", pointerEvents: "none" }} />
                  <input id="email" type="email" placeholder="name@example.com"
                    value={email} onChange={e => setEmail(e.target.value)}
                    onFocus={() => setFocused("email")} onBlur={() => setFocused(null)}
                    style={{ ...inputStyle("email"), outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }}
                    required data-testid="register-email-input" />
                </div>
              </div>

              <div>
                <label htmlFor="password" style={{ fontSize: 11, fontWeight: 700, color: "#475569", display: "block", marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>Password</label>
                <div style={{ position: "relative" }}>
                  <Lock style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", width: 15, height: 15, color: focused === "password" ? "#4fd1c5" : "#475569", transition: "color 0.2s", pointerEvents: "none" }} />
                  <input id="password" type={showPass ? "text" : "password"} placeholder="Min. 6 characters"
                    value={password} onChange={e => setPassword(e.target.value)}
                    onFocus={() => setFocused("password")} onBlur={() => setFocused(null)}
                    style={{ ...inputStyle("password"), paddingRight: 44, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box" }}
                    minLength={6} required data-testid="register-password-input" />
                  <button type="button" onClick={() => setShowPass(v => !v)}
                    style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "#475569", padding: 0, display: "flex" }}>
                    {showPass
                      ? <EyeOff style={{ width: 15, height: 15 }} />
                      : <Eye    style={{ width: 15, height: 15 }} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={loading}
                data-testid="register-submit-btn"
                style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "14px 0", borderRadius: 11, marginTop: 6, background: loading ? "rgba(79,209,197,0.35)" : "linear-gradient(135deg, #4fd1c5, #2563eb)", color: "#030712", fontSize: 14, fontWeight: 800, border: "none", cursor: loading ? "not-allowed" : "pointer", boxShadow: loading ? "none" : "0 0 32px rgba(79,209,197,0.28), 0 4px 20px rgba(79,209,197,0.15)", transition: "all 0.2s", letterSpacing: "0.02em" }}
                onMouseEnter={e => { if (!loading) e.currentTarget.style.boxShadow = "0 0 52px rgba(79,209,197,0.52), 0 4px 28px rgba(79,209,197,0.25)"; }}
                onMouseLeave={e => { if (!loading) e.currentTarget.style.boxShadow = "0 0 32px rgba(79,209,197,0.28), 0 4px 20px rgba(79,209,197,0.15)"; }}>
                {loading ? (
                  <><div style={{ width: 16, height: 16, borderRadius: "50%", border: "2px solid rgba(3,7,18,0.3)", borderTop: "2px solid #030712", animation: "rp_spin 0.7s linear infinite" }} />Creating account…</>
                ) : (
                  <>Create Account <ArrowRight style={{ width: 16, height: 16 }} /></>
                )}
              </button>
            </form>

            {/* Trust badges */}
            <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 24, marginBottom: 4 }}>
              {["SOC 2", "GDPR", "AES-256", "JWT"].map(b => (
                <div key={b} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#334155" }} />
                  <span style={{ fontSize: 10, color: "#334155", fontWeight: 600 }}>{b}</span>
                </div>
              ))}
            </div>

            <p style={{ marginTop: 20, textAlign: "center", fontSize: 13, color: "#475569" }}>
              Already have an account?{" "}
              <Link to="/login"
                data-testid="login-link"
                style={{ color: "#4fd1c5", textDecoration: "none", fontWeight: 700 }}
                onMouseEnter={e => e.currentTarget.style.opacity = "0.7"}
                onMouseLeave={e => e.currentTarget.style.opacity = "1"}>
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>

      <BrandFooter />
      <style>{`@keyframes rp_spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default RegisterPage;
