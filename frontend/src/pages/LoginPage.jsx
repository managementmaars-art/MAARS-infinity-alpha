import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Mail, Lock, ArrowRight, Sparkles, Shield, Zap, Globe, Brain, Eye, EyeOff } from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL?.trim() || "http://localhost:8000";

const OAUTH_ERROR_MESSAGES = {
  oauth_cancelled:       "Google sign-in was cancelled.",
  not_configured:        "Google OAuth is not configured on this server.",
  token_exchange_failed: "Google authentication failed. Please try again.",
  user_info_failed:      "Could not retrieve your Google profile. Please try again.",
  oauth_failed:          "Google sign-in failed. Please try again.",
  no_email:              "Your Google account did not provide an email address.",
};

/* ── Immersive left panel ─────────────────────────────────── */
function AuthPanel() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf, w, h;
    const resize = () => { w = canvas.width = canvas.offsetWidth; h = canvas.height = canvas.offsetHeight; };
    resize();
    window.addEventListener("resize", resize);

    // Neural network nodes
    const nodes = Array.from({length: 32}, () => ({
      x: Math.random() * (w||600), y: Math.random() * (h||800),
      vx: (Math.random()-0.5)*0.35, vy: (Math.random()-0.5)*0.35,
      r: 1.5 + Math.random()*2.5,
      phase: Math.random()*Math.PI*2,
      color: Math.random() > 0.5 ? "79,209,197" : Math.random()>0.5 ? "124,58,237" : "37,99,235",
    }));

    // Floating orbs (large, atmospheric)
    const orbs = Array.from({length: 5}, (_, i) => ({
      x: Math.random()*(w||600), y: Math.random()*(h||800),
      r: 100 + Math.random()*160,
      vx: (Math.random()-0.5)*0.15, vy: (Math.random()-0.5)*0.15,
      hue: ["79,209,197","124,58,237","37,99,235"][i%3],
      phase: Math.random()*Math.PI*2,
    }));

    // Data particles
    const particles = Array.from({length:60}, ()=>({
      x: Math.random()*(w||600), y: Math.random()*(h||800),
      size: 0.5+Math.random(),
      speed: 0.2+Math.random()*0.5,
      alpha: 0.1+Math.random()*0.4,
      color: Math.random()>0.5?"79,209,197":"124,58,237",
    }));

    const draw = (t) => {
      ctx.clearRect(0,0,w,h);

      // Draw orbs
      orbs.forEach(o => {
        o.x+=o.vx; o.y+=o.vy;
        if(o.x<-o.r)o.x=w+o.r; if(o.x>w+o.r)o.x=-o.r;
        if(o.y<-o.r)o.y=h+o.r; if(o.y>h+o.r)o.y=-o.r;
        const pulse = 0.03+0.015*Math.sin(t*0.0008+o.phase);
        const g = ctx.createRadialGradient(o.x,o.y,0,o.x,o.y,o.r);
        g.addColorStop(0,`rgba(${o.hue},${pulse})`);
        g.addColorStop(1,`rgba(${o.hue},0)`);
        ctx.fillStyle=g; ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill();
      });

      // Draw grid
      ctx.strokeStyle="rgba(79,209,197,0.04)"; ctx.lineWidth=0.5;
      for(let x=0;x<w;x+=50){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
      for(let y=0;y<h;y+=50){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}

      // Draw neural connections
      nodes.forEach((a,i)=>nodes.slice(i+1).forEach(b=>{
        const dx=a.x-b.x,dy=a.y-b.y,dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<100){
          ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
          const alpha=(1-dist/100)*0.2;
          ctx.strokeStyle=`rgba(79,209,197,${alpha})`;
          ctx.lineWidth=0.8; ctx.stroke();
        }
      }));

      // Draw and animate nodes
      nodes.forEach(n => {
        n.x+=n.vx; n.y+=n.vy;
        if(n.x<0)n.x=w; if(n.x>w)n.x=0;
        if(n.y<0)n.y=h; if(n.y>h)n.y=0;
        const pulse = 0.6+0.4*Math.sin(t*0.002+n.phase);
        // Glow
        const glow = ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r*4);
        glow.addColorStop(0,`rgba(${n.color},${0.3*pulse})`);
        glow.addColorStop(1,`rgba(${n.color},0)`);
        ctx.fillStyle=glow; ctx.beginPath(); ctx.arc(n.x,n.y,n.r*4,0,Math.PI*2); ctx.fill();
        // Core
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r*(0.7+0.3*pulse),0,Math.PI*2);
        ctx.fillStyle=`rgba(${n.color},${0.6+0.4*pulse})`; ctx.fill();
      });

      // Particles (slow drift upward)
      particles.forEach(p => {
        p.y-=p.speed;
        if(p.y<0) p.y=h;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2);
        ctx.fillStyle=`rgba(${p.color},${p.alpha})`; ctx.fill();
      });

      raf=requestAnimationFrame(draw);
    };
    raf=requestAnimationFrame(draw);
    return ()=>{cancelAnimationFrame(raf);window.removeEventListener("resize",resize);};
  }, []);

  const features = [
    { icon: Brain,  text: "458+ specialized AI agents", sub:"Across 27 expert networks" },
    { icon: Globe,  text: "33 providers · 175,000+ models", sub:"All via one universal key" },
    { icon: Shield, text: "Enterprise governance & trust scoring", sub:"Every action audited & metered" },
    { icon: Zap,    text: "Real-time multi-agent orchestration", sub:"Parallel task execution at scale" },
  ];

  return (
    <div style={{position:"relative",width:"100%",height:"100%",overflow:"hidden",background:"#020810",display:"flex",flexDirection:"column",justifyContent:"center",alignItems:"flex-start",padding:"64px 60px"}}>
      <canvas ref={canvasRef} style={{position:"absolute",inset:0,width:"100%",height:"100%"}} />

      {/* Vignette edges */}
      <div style={{position:"absolute",inset:0,background:"radial-gradient(ellipse 75% 75% at 50% 50%, transparent 35%, rgba(2,8,16,0.85) 100%)",pointerEvents:"none"}} />

      {/* Content */}
      <div style={{position:"relative",zIndex:1,maxWidth:440}}>
        {/* Logo */}
        <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:52}}>
          <div style={{
            position:"relative",width:48,height:48,borderRadius:14,overflow:"hidden",
            boxShadow:"0 0 32px rgba(79,209,197,0.3), 0 0 64px rgba(79,209,197,0.1)",
          }}>
            <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{width:"100%",height:"100%",objectFit:"cover"}} />
            <div style={{position:"absolute",inset:0,border:"1px solid rgba(79,209,197,0.35)",borderRadius:14}} />
          </div>
          <div>
            <h2 style={{color:"#f1f5f9",fontWeight:800,fontSize:20,fontFamily:"Outfit, sans-serif",lineHeight:1.1,margin:0}}>MAARS Command</h2>
            <p style={{color:"#475569",fontSize:11,margin:0,letterSpacing:"0.08em"}}>AI WORKFORCE PLATFORM</p>
          </div>
        </div>

        {/* Headline */}
        <div style={{marginBottom:12}}>
          <div style={{
            display:"inline-flex",alignItems:"center",gap:6,
            padding:"4px 12px",borderRadius:20,marginBottom:16,
            background:"rgba(79,209,197,0.1)",border:"1px solid rgba(79,209,197,0.25)",
          }}>
            <span style={{width:6,height:6,borderRadius:"50%",background:"#34d399",display:"inline-block",animation:"lp_online_dot 2s ease infinite"}} />
            <span style={{fontSize:10,fontWeight:700,color:"#34d399",letterSpacing:"0.12em"}}>458 AGENTS ONLINE</span>
          </div>
          <h1 style={{fontSize:"clamp(2.2rem, 4vw, 3rem)",fontWeight:900,fontFamily:"Outfit, sans-serif",lineHeight:1.05,color:"#f1f5f9",margin:"0 0 14px"}}>
            Your AI workforce{" "}
            <span style={{
              background:"linear-gradient(135deg, #4fd1c5 0%, #a78bfa 60%, #60a5fa 100%)",
              WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent",
            }}>is waiting.</span>
          </h1>
          <p style={{fontSize:15,color:"#475569",lineHeight:1.65,margin:0}}>
            Command 458+ AI agents, route across 33 providers, and orchestrate enterprise-scale workflows — all from one dashboard.
          </p>
        </div>

        {/* Feature list */}
        <div style={{display:"flex",flexDirection:"column",gap:14,marginTop:36}}>
          {features.map((f,i)=>(
            <div key={i} style={{display:"flex",alignItems:"center",gap:14,animation:`lp_card_in 0.5s ease ${i*0.1}s both`}}>
              <div style={{
                width:36,height:36,borderRadius:10,flexShrink:0,
                background:"rgba(79,209,197,0.1)",border:"1px solid rgba(79,209,197,0.2)",
                display:"flex",alignItems:"center",justifyContent:"center",
              }}>
                <f.icon style={{width:16,height:16,color:"#4fd1c5"}} />
              </div>
              <div>
                <p style={{fontSize:13,color:"#cbd5e1",fontWeight:600,margin:0}}>{f.text}</p>
                <p style={{fontSize:11,color:"#475569",margin:0}}>{f.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Decorative animated ring */}
        <div style={{
          position:"absolute",bottom:-100,right:-60,
          width:280,height:280,borderRadius:"50%",
          border:"1px solid rgba(79,209,197,0.07)",
          animation:"db_ring_spin 20s linear infinite",
          pointerEvents:"none",
        }}>
          <div style={{
            position:"absolute",top:20,left:20,right:20,bottom:20,borderRadius:"50%",
            border:"1px dashed rgba(124,58,237,0.08)",
          }} />
        </div>
      </div>

      <style>{`
        @keyframes lp_online_dot { 0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,0.7)} 60%{box-shadow:0 0 0 5px rgba(52,211,153,0)} }
        @keyframes lp_card_in { from{opacity:0;transform:translateX(-12px)} to{opacity:1;transform:translateX(0)} }
        @keyframes db_ring_spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes spin_anim { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

/* ── LoginPage ────────────────────────────────────────────── */
const LoginPage = () => {
  const navigate  = useNavigate();
  const location  = useLocation();
  const { login } = useAuth();
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [loading,  setLoading]  = useState(false);
  const [showPw,   setShowPw]   = useState(false);
  const [focused,  setFocused]  = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const error  = params.get("error");
    if (error) toast.error(OAUTH_ERROR_MESSAGES[error] || "Sign-in failed.");
  }, [location.search]);

  const handleGoogleLogin = () => { window.location.href = `${BACKEND_URL}/api/auth/google`; };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/login`,{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email,password}),
      });
      const data = await res.json();
      if (res.ok) { login(data.user, data.token); toast.success("Welcome back!"); navigate("/dashboard"); }
      else toast.error(data.detail || "Invalid credentials");
    } catch { toast.error("Login failed. Please try again."); }
    finally { setLoading(false); }
  };

  const inputStyle = (field) => ({
    paddingLeft:44, height:50, borderRadius:12, fontSize:14,
    background:"rgba(255,255,255,0.04)",
    border:`1px solid ${focused===field?"rgba(79,209,197,0.5)":"rgba(255,255,255,0.09)"}`,
    boxShadow: focused===field?"0 0 0 3px rgba(79,209,197,0.08)":"none",
    transition:"all 0.2s", color:"#e2e8f0",
  });

  return (
    <div style={{minHeight:"100vh",background:"#020810",display:"flex",flexDirection:"column"}}>
      <div style={{flex:1,display:"flex"}}>

        {/* Left panel */}
        <div className="hidden lg:block" style={{width:"52%",position:"relative"}}>
          <AuthPanel />
        </div>

        {/* Right form panel */}
        <div style={{
          flex:1,display:"flex",flexDirection:"column",justifyContent:"center",
          padding:"40px 8vw",
          background:"rgba(4,8,20,0.6)",backdropFilter:"blur(32px)",
          borderLeft:"1px solid rgba(255,255,255,0.05)",
          position:"relative",overflow:"hidden",
        }}>
          {/* Ambient glow */}
          <div style={{position:"absolute",top:-80,right:-80,width:300,height:300,borderRadius:"50%",background:"radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%)",pointerEvents:"none"}} />
          <div style={{position:"absolute",bottom:-60,left:-60,width:240,height:240,borderRadius:"50%",background:"radial-gradient(circle, rgba(79,209,197,0.05) 0%, transparent 70%)",pointerEvents:"none"}} />

          {/* Back link */}
          <Link to="/" style={{
            display:"inline-flex",alignItems:"center",gap:7,fontSize:12,
            color:"#475569",textDecoration:"none",marginBottom:40,
            transition:"color 0.15s",width:"fit-content",letterSpacing:"0.03em",
          }}
          onMouseEnter={e=>e.currentTarget.style.color="#4fd1c5"}
          onMouseLeave={e=>e.currentTarget.style.color="#475569"}>
            ← Back to home
          </Link>

          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 mb-8">
            <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{width:36,height:36,borderRadius:10,objectFit:"cover",border:"1px solid rgba(79,209,197,0.2)"}} />
            <span style={{color:"#f1f5f9",fontWeight:800,fontFamily:"Outfit, sans-serif",fontSize:17}}>MAARS Command</span>
          </div>

          <div style={{maxWidth:380,width:"100%",position:"relative"}}>
            {/* Heading */}
            <div style={{marginBottom:32}}>
              <h1 style={{fontSize:28,fontWeight:900,color:"#f1f5f9",fontFamily:"Outfit, sans-serif",margin:"0 0 8px",letterSpacing:"-0.02em"}}>
                Welcome back
              </h1>
              <p style={{fontSize:14,color:"#475569",margin:0}}>
                Your AI team is online and ready.{" "}
                <span style={{color:"#34d399",fontWeight:600}}>●</span>
              </p>
            </div>

            {/* Google button */}
            <button
              type="button"
              onClick={handleGoogleLogin}
              data-testid="google-login-btn"
              style={{
                width:"100%",display:"flex",alignItems:"center",justifyContent:"center",gap:10,
                padding:"13px 0",borderRadius:13,marginBottom:24,
                background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.1)",
                color:"#e2e8f0",fontSize:14,fontWeight:600,cursor:"pointer",
                transition:"all 0.25s",
              }}
              onMouseEnter={e=>{e.currentTarget.style.background="rgba(255,255,255,0.08)";e.currentTarget.style.borderColor="rgba(255,255,255,0.18)";e.currentTarget.style.boxShadow="0 4px 20px rgba(0,0,0,0.3)";}}
              onMouseLeave={e=>{e.currentTarget.style.background="rgba(255,255,255,0.04)";e.currentTarget.style.borderColor="rgba(255,255,255,0.1)";e.currentTarget.style.boxShadow="none";}}
            >
              <svg style={{width:18,height:18,flexShrink:0}} viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            {/* Divider */}
            <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:24}}>
              <div style={{flex:1,height:1,background:"rgba(255,255,255,0.07)"}} />
              <span style={{fontSize:11,color:"#475569",letterSpacing:"0.05em"}}>or continue with email</span>
              <div style={{flex:1,height:1,background:"rgba(255,255,255,0.07)"}} />
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} style={{display:"flex",flexDirection:"column",gap:16}}>
              <div>
                <label htmlFor="email" style={{fontSize:11,fontWeight:700,color:"#64748b",display:"block",marginBottom:7,letterSpacing:"0.08em",textTransform:"uppercase"}}>Email</label>
                <div style={{position:"relative"}}>
                  <Mail style={{position:"absolute",left:14,top:"50%",transform:"translateY(-50%)",width:15,height:15,color:focused==="email"?"#4fd1c5":"#64748b",transition:"color 0.2s"}} />
                  <input id="email" type="email" placeholder="name@example.com"
                    value={email} onChange={e=>setEmail(e.target.value)}
                    style={inputStyle("email")}
                    onFocus={()=>setFocused("email")} onBlur={()=>setFocused(null)}
                    required data-testid="login-email-input" />
                </div>
              </div>

              <div>
                <label htmlFor="password" style={{fontSize:11,fontWeight:700,color:"#64748b",display:"block",marginBottom:7,letterSpacing:"0.08em",textTransform:"uppercase"}}>Password</label>
                <div style={{position:"relative"}}>
                  <Lock style={{position:"absolute",left:14,top:"50%",transform:"translateY(-50%)",width:15,height:15,color:focused==="password"?"#4fd1c5":"#64748b",transition:"color 0.2s"}} />
                  <input id="password" type={showPw?"text":"password"} placeholder="••••••••"
                    value={password} onChange={e=>setPassword(e.target.value)}
                    style={{...inputStyle("password"),paddingRight:44,outline:"none"}}
                    onFocus={()=>setFocused("password")} onBlur={()=>setFocused(null)}
                    required data-testid="login-password-input" />
                  <button type="button" onClick={()=>setShowPw(p=>!p)} style={{position:"absolute",right:14,top:"50%",transform:"translateY(-50%)",background:"none",border:"none",cursor:"pointer",color:"#64748b",padding:0}}>
                    {showPw ? <EyeOff style={{width:15,height:15}} /> : <Eye style={{width:15,height:15}} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                data-testid="login-submit-btn"
                style={{
                  width:"100%",display:"flex",alignItems:"center",justifyContent:"center",gap:8,
                  padding:"14px 0",borderRadius:13,marginTop:4,
                  background:loading?"rgba(79,209,197,0.35)":"linear-gradient(135deg, #4fd1c5 0%, #2563eb 100%)",
                  color:"#030712",fontSize:14,fontWeight:800,border:"none",
                  cursor:loading?"not-allowed":"pointer",
                  boxShadow:loading?"none":"0 0 40px rgba(79,209,197,0.35), 0 4px 16px rgba(79,209,197,0.15)",
                  transition:"all 0.25s",letterSpacing:"0.02em",
                }}
                onMouseEnter={e=>{if(!loading){e.currentTarget.style.boxShadow="0 0 60px rgba(79,209,197,0.55), 0 8px 24px rgba(79,209,197,0.2)";e.currentTarget.style.transform="translateY(-1px)";}}}
                onMouseLeave={e=>{if(!loading){e.currentTarget.style.boxShadow="0 0 40px rgba(79,209,197,0.35), 0 4px 16px rgba(79,209,197,0.15)";e.currentTarget.style.transform="translateY(0)";}}}
              >
                {loading ? (
                  <>
                    <div style={{width:16,height:16,borderRadius:"50%",border:"2px solid rgba(3,7,18,0.3)",borderTop:"2px solid #030712",animation:"spin_anim 0.7s linear infinite"}} />
                    Authenticating…
                  </>
                ) : (
                  <>Sign In <ArrowRight style={{width:16,height:16}} /></>
                )}
              </button>
            </form>

            {/* Sign up */}
            <p style={{marginTop:24,textAlign:"center",fontSize:13,color:"#475569"}}>
              No account yet?{" "}
              <Link to="/register" data-testid="register-link"
                style={{color:"#4fd1c5",textDecoration:"none",fontWeight:700,transition:"all 0.15s"}}
                onMouseEnter={e=>e.currentTarget.style.textShadow="0 0 12px rgba(79,209,197,0.5)"}
                onMouseLeave={e=>e.currentTarget.style.textShadow="none"}>
                Create your account →
              </Link>
            </p>

            {/* Trust badges */}
            <div style={{marginTop:32,display:"flex",alignItems:"center",justifyContent:"center",gap:16,flexWrap:"wrap"}}>
              {["SOC2 Ready","GDPR Compliant","256-bit AES","JWT Secured"].map((badge,i)=>(
                <div key={i} style={{display:"flex",alignItems:"center",gap:5,padding:"4px 10px",borderRadius:20,background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)"}}>
                  <Shield style={{width:9,height:9,color:"#475569"}} />
                  <span style={{fontSize:9,color:"#475569",fontWeight:600,letterSpacing:"0.06em"}}>{badge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <BrandFooter />
    </div>
  );
};

export default LoginPage;
