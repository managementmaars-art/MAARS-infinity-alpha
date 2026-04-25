import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  Bot, ArrowRight, ArrowLeft, MessageSquare, CreditCard, Sparkles,
  Zap, Users, X, CheckCircle, Brain, Volume2, Image, FileText, Trophy,
  Target, Rocket, Mail, Linkedin
} from "lucide-react";

/* ─── Design tokens ───────────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.6)",
};

const STEPS = [
  { id: "welcome",      title: "Welcome to MAARS",      subtitle: "Your AI workforce awaits" },
  { id: "agents",       title: "Meet Your AI Team",      subtitle: "Specialists for every task" },
  { id: "how-it-works", title: "How It Works",           subtitle: "Three steps to results" },
  { id: "features",     title: "Powerful Capabilities",  subtitle: "What your team can do" },
  { id: "activate",     title: "Launch Your First Win",  subtitle: "Pick a starter goal — one click" },
  { id: "ready",        title: "You're All Set!",        subtitle: "+50 XP for getting started" },
];

const OnboardingFlow = ({ onComplete }) => {
  const { token, user } = useAuth();
  const navigate  = useNavigate();
  const [step,    setStep]    = useState(0);
  const [agents,  setAgents]  = useState([]);
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    fetch(`${API}/agents/public`)
      .then(r => r.json())
      .then(data => setAgents(data.slice(0, 8)))
      .catch(() => {});
  }, []);

  const complete = async () => {
    setExiting(true);
    try {
      await fetch(`${API}/auth/onboarding-complete`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` },
      });
    } catch {}
    setTimeout(() => onComplete(), 300);
  };

  const next = () => step < STEPS.length - 1 && setStep(s => s + 1);
  const prev = () => step > 0 && setStep(s => s - 1);
  const current = STEPS[step];
  const progress = ((step + 1) / STEPS.length) * 100;

  return (
    <div
      data-testid="onboarding-overlay"
      style={{
        position: "fixed", inset: 0, zIndex: 200,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "rgba(3,7,18,0.88)", backdropFilter: "blur(20px)",
        transition: "opacity 0.3s", opacity: exiting ? 0 : 1,
      }}
    >
      <div style={{ position: "relative", width: "100%", maxWidth: 620, margin: "0 16px" }}>
        {/* Skip */}
        <button
          onClick={complete}
          data-testid="onboarding-skip"
          style={{ position: "absolute", top: -48, right: 0, display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "#475569", background: "none", border: "none", cursor: "pointer", transition: "color 0.15s" }}
          onMouseEnter={e => e.currentTarget.style.color = "#e2e8f0"}
          onMouseLeave={e => e.currentTarget.style.color = "#475569"}>
          Skip tour <X style={{ width: 14, height: 14 }} />
        </button>

        {/* Card */}
        <div style={{
          background: "rgba(5,10,20,0.97)", border: `1px solid ${T.border}`,
          borderRadius: 24, overflow: "hidden",
          boxShadow: "0 32px 80px rgba(0,0,0,0.7), 0 0 0 1px rgba(79,209,197,0.06)",
        }}>
          {/* Progress bar */}
          <div style={{ height: 3, background: "rgba(255,255,255,0.05)" }}>
            <div style={{ height: "100%", background: `linear-gradient(90deg, ${T.teal}, ${T.violet})`, width: `${progress}%`, transition: "width 0.5s ease", boxShadow: `0 0 12px rgba(79,209,197,0.4)` }} />
          </div>

          <div style={{ padding: "36px 40px", minHeight: 460, display: "flex", flexDirection: "column" }}>
            {/* Step dots */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 32 }}>
              {STEPS.map((_, i) => (
                <div key={i} style={{ height: 4, borderRadius: 2, transition: "all 0.3s", background: i <= step ? T.teal : "rgba(255,255,255,0.08)", width: i === step ? 28 : 14 }} />
              ))}
              <span style={{ marginLeft: "auto", fontSize: 11, color: "#64748b", fontVariantNumeric: "tabular-nums" }}>{step + 1} / {STEPS.length}</span>
            </div>

            {/* Content */}
            <div style={{ flex: 1 }}>

              {/* ── Welcome ──────────────────────────────── */}
              {current.id === "welcome" && (
                <div data-testid="onboarding-step-welcome" style={{ textAlign: "center" }}>
                  <div style={{ width: 80, height: 80, borderRadius: 24, background: `linear-gradient(135deg, rgba(79,209,197,0.2), rgba(124,58,237,0.2))`, border: "1px solid rgba(79,209,197,0.3)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px", boxShadow: "0 0 40px rgba(79,209,197,0.15)" }}>
                    <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{ width: 56, height: 56, borderRadius: 16, objectFit: "cover" }} />
                  </div>
                  <h2 style={{ fontSize: 28, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 10 }}>
                    Welcome to{" "}
                    <span style={{ background: `linear-gradient(135deg, ${T.teal}, #a78bfa)`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>MAARS Command</span>
                  </h2>
                  <p style={{ fontSize: 15, color: "#64748b", marginBottom: 32, lineHeight: 1.6 }}>
                    {user?.name ? `Hey ${user.name.split(" ")[0]}! ` : ""}Your AI-powered team of 458+ specialists is ready to work for you.
                  </p>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
                    {[
                      { icon: Bot,    color: T.teal,   label: "458+ AI Agents",     desc: "Specialized experts" },
                      { icon: Brain,  color: "#a78bfa", label: "Smart Routing",      desc: "Right agent, every time" },
                      { icon: Zap,    color: T.violet, label: "Instant Results",     desc: "Files, images & more" },
                    ].map((item, i) => (
                      <div key={i} style={{ padding: "18px 14px", borderRadius: 16, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textAlign: "center" }}>
                        <div style={{ width: 40, height: 40, borderRadius: 11, background: `${item.color}18`, border: `1px solid ${item.color}28`, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 10px" }}>
                          <item.icon style={{ width: 18, height: 18, color: item.color }} />
                        </div>
                        <p style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", marginBottom: 4, fontFamily: "Outfit, sans-serif" }}>{item.label}</p>
                        <p style={{ fontSize: 11, color: "#475569" }}>{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Agents ───────────────────────────────── */}
              {current.id === "agents" && (
                <div data-testid="onboarding-step-agents">
                  <h2 style={{ fontSize: 24, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>Meet Your AI Team</h2>
                  <p style={{ fontSize: 13, color: "#64748b", marginBottom: 20 }}>Each agent is a specialist. Pick the right one for your task.</p>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 20 }}>
                    {agents.map(agent => (
                      <div key={agent.agent_id} style={{ padding: "12px 10px", borderRadius: 14, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textAlign: "center", transition: "border-color 0.2s", cursor: "default" }}
                        onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(79,209,197,0.25)"}
                        onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                        <img src={agent.avatar} alt="" style={{ width: 44, height: 44, borderRadius: 12, objectFit: "cover", margin: "0 auto 8px", display: "block" }} />
                        <p style={{ fontSize: 11, fontWeight: 700, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.name}</p>
                        <p style={{ fontSize: 10, color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{agent.role}</p>
                      </div>
                    ))}
                  </div>
                  <div style={{ padding: "14px 16px", borderRadius: 14, background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)" }}>
                    <p style={{ fontSize: 13, color: "#fbbf24", lineHeight: 1.5 }}>
                      <strong>Commander Orion</strong> is your lead strategist. Give it a complex goal and it automatically delegates to the right specialists.
                    </p>
                  </div>
                </div>
              )}

              {/* ── How It Works ─────────────────────────── */}
              {current.id === "how-it-works" && (
                <div data-testid="onboarding-step-how">
                  <h2 style={{ fontSize: 24, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>How It Works</h2>
                  <p style={{ fontSize: 13, color: "#64748b", marginBottom: 24 }}>Getting results is as easy as 1-2-3.</p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {[
                      { num: "1", accent: T.teal,   title: "Pick an Agent",    desc: "Choose the specialist that fits your task — marketing, finance, code, design, and 450+ more.", icon: Users },
                      { num: "2", accent: T.violet, title: "Describe Your Task",desc: "Just type in plain English. The AI asks clarifying questions when needed to ensure perfect output.", icon: MessageSquare },
                      { num: "3", accent: T.blue,   title: "Get Results",      desc: "Receive expert output — text, PDFs, images, or videos. Download and use in seconds.", icon: CheckCircle },
                    ].map((item, i) => (
                      <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 16, padding: "16px 18px", borderRadius: 16, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}` }}>
                        <div style={{ width: 36, height: 36, borderRadius: 10, background: `${item.accent}18`, border: `1px solid ${item.accent}28`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <span style={{ fontSize: 16, fontWeight: 800, color: item.accent, fontFamily: "Outfit, sans-serif" }}>{item.num}</span>
                        </div>
                        <div style={{ minWidth: 0 }}>
                          <p style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 4, display: "flex", alignItems: "center", gap: 6 }}>
                            {item.title} <item.icon style={{ width: 13, height: 13, color: "#64748b" }} />
                          </p>
                          <p style={{ fontSize: 12, color: "#64748b", lineHeight: 1.55 }}>{item.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Features ─────────────────────────────── */}
              {current.id === "features" && (
                <div data-testid="onboarding-step-features">
                  <h2 style={{ fontSize: 24, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>Powerful Capabilities</h2>
                  <p style={{ fontSize: 13, color: "#64748b", marginBottom: 24 }}>Everything your AI team can do.</p>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
                    {[
                      { icon: FileText,    color: "#60a5fa", bg: "rgba(96,165,250,0.1)",  border: "rgba(96,165,250,0.2)",  title: "Document Generation", desc: "PDF, Word, Excel instantly" },
                      { icon: Image,       color: "#c084fc", bg: "rgba(192,132,252,0.1)", border: "rgba(192,132,252,0.2)", title: "Image Creation",       desc: "AI visuals on demand" },
                      { icon: Volume2,     color: T.teal,   bg: "rgba(79,209,197,0.1)",  border: "rgba(79,209,197,0.2)",  title: "Voice Mode",           desc: "Listen to AI responses" },
                      { icon: Brain,       color: "#fbbf24", bg: "rgba(251,191,36,0.1)",  border: "rgba(251,191,36,0.2)",  title: "Multi-Agent Collab",   desc: "Agents consult each other" },
                      { icon: CreditCard,  color: "#f472b6", bg: "rgba(244,114,182,0.1)", border: "rgba(244,114,182,0.2)", title: "Flexible Credits",     desc: "Pay only for what you use" },
                      { icon: Users,       color: T.violet, bg: "rgba(124,58,237,0.1)",  border: "rgba(124,58,237,0.2)",  title: "Team Access",          desc: "Invite your whole team" },
                    ].map((item, i) => (
                      <div key={i} style={{ padding: "14px 16px", borderRadius: 14, background: item.bg, border: `1px solid ${item.border}` }}>
                        <item.icon style={{ width: 18, height: 18, color: item.color, marginBottom: 8 }} />
                        <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 3 }}>{item.title}</p>
                        <p style={{ fontSize: 11, color: "#64748b" }}>{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Activate: first real action ─────────────
                  The biggest retention lever in any SaaS: get the user
                  to experience a single win during onboarding. Each
                  card here launches a real task in the dashboard and
                  hands the user something they can show a peer. */}
              {current.id === "activate" && (
                <div data-testid="onboarding-step-activate">
                  <h2 style={{ fontSize: 24, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 6 }}>
                    Launch Your First Win
                  </h2>
                  <p style={{ fontSize: 13, color: "#64748b", marginBottom: 18 }}>
                    Pick any of these — we'll pre-load it so you can publish in under 60 seconds.
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {[
                      {
                        icon: Mail,
                        color: T.teal,
                        title: "Run a cold-email campaign",
                        desc: "Find prospects, draft personalized messages, schedule over 5 days",
                        route: "/dashboard?launch=campaign",
                      },
                      {
                        icon: Image,
                        color: "#c084fc",
                        title: "Generate a premium image",
                        desc: "We'll enhance your prompt into a production-grade creative brief",
                        route: "/dashboard?launch=image",
                      },
                      {
                        icon: Linkedin,
                        color: "#60a5fa",
                        title: "Schedule your first LinkedIn post",
                        desc: "Queue a post for the next 9am-11am window (highest engagement)",
                        route: "/dashboard?launch=linkedin",
                      },
                      {
                        icon: Target,
                        color: "#fbbf24",
                        title: "Give Commander a goal",
                        desc: "One sentence, Commander delegates to the right specialists",
                        route: "/dashboard?launch=commander",
                      },
                    ].map((item, i) => (
                      <button
                        key={i}
                        onClick={async () => {
                          await complete();  // mark onboarding done
                          setTimeout(() => navigate(item.route), 350);
                        }}
                        style={{
                          display: "flex", alignItems: "center", gap: 14,
                          padding: "14px 16px", borderRadius: 14,
                          background: "rgba(255,255,255,0.03)",
                          border: `1px solid ${T.border}`,
                          cursor: "pointer", textAlign: "left",
                          transition: "all 0.15s",
                        }}
                        onMouseEnter={e => {
                          e.currentTarget.style.background = "rgba(79,209,197,0.05)";
                          e.currentTarget.style.borderColor = "rgba(79,209,197,0.3)";
                        }}
                        onMouseLeave={e => {
                          e.currentTarget.style.background = "rgba(255,255,255,0.03)";
                          e.currentTarget.style.borderColor = T.border;
                        }}
                      >
                        <div style={{ width: 40, height: 40, borderRadius: 10, background: `${item.color}18`, border: `1px solid ${item.color}28`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <item.icon style={{ width: 18, height: 18, color: item.color }} />
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 3, fontFamily: "Outfit, sans-serif" }}>
                            {item.title}
                          </p>
                          <p style={{ fontSize: 12, color: "#64748b", lineHeight: 1.45 }}>{item.desc}</p>
                        </div>
                        <ArrowRight style={{ width: 16, height: 16, color: "#475569", flexShrink: 0 }} />
                      </button>
                    ))}
                  </div>
                  <p style={{ fontSize: 11, color: "#475569", marginTop: 14, textAlign: "center" }}>
                    Or skip — you can launch anything from the dashboard anytime.
                  </p>
                </div>
              )}

              {/* ── Ready ────────────────────────────────── */}
              {current.id === "ready" && (
                <div data-testid="onboarding-step-ready" style={{ textAlign: "center" }}>
                  <div style={{ width: 80, height: 80, borderRadius: "50%", background: "linear-gradient(135deg, rgba(79,209,197,0.2), rgba(52,211,153,0.2))", border: "1px solid rgba(79,209,197,0.35)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px", boxShadow: "0 0 40px rgba(79,209,197,0.2)" }}>
                    <CheckCircle style={{ width: 36, height: 36, color: T.teal }} />
                  </div>
                  <h2 style={{ fontSize: 28, fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", marginBottom: 10 }}>You're All Set!</h2>
                  <p style={{ fontSize: 15, color: "#64748b", marginBottom: 28, lineHeight: 1.6 }}>Start chatting with any agent. Try something specific!</p>

                  {/* XP reward */}
                  <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "10px 20px", borderRadius: 24, background: "rgba(79,209,197,0.08)", border: "1px solid rgba(79,209,197,0.2)", marginBottom: 24 }}>
                    <Trophy style={{ width: 16, height: 16, color: "#f59e0b" }} />
                    <span style={{ fontSize: 13, fontWeight: 700, color: T.teal }}>+50 XP earned for completing onboarding!</span>
                  </div>

                  <div style={{ padding: "16px 20px", borderRadius: 14, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, textAlign: "left", maxWidth: 400, margin: "0 auto" }}>
                    <p style={{ fontSize: 10, color: "#64748b", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.1em" }}>Try saying:</p>
                    <p style={{ fontSize: 13, color: "#94a3b8", fontStyle: "italic", lineHeight: 1.5 }}>
                      "Create a social media strategy for my coffee shop and give me a PDF report"
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Navigation */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 28, marginTop: "auto" }}>
              <button
                onClick={prev}
                data-testid="onboarding-prev"
                style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 16px", borderRadius: 10, background: "transparent", border: `1px solid ${T.border}`, color: "#475569", fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.15s", visibility: step === 0 ? "hidden" : "visible" }}
                onMouseEnter={e => { e.currentTarget.style.color = "#e2e8f0"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.15)"; }}
                onMouseLeave={e => { e.currentTarget.style.color = "#475569"; e.currentTarget.style.borderColor = T.border; }}>
                <ArrowLeft style={{ width: 14, height: 14 }} /> Back
              </button>

              {step < STEPS.length - 1 ? (
                <button onClick={next}
                  data-testid="onboarding-next"
                  style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 22px", borderRadius: 11, background: `linear-gradient(135deg, ${T.teal}, ${T.blue})`, color: "#030712", fontSize: 13, fontWeight: 700, border: "none", cursor: "pointer", boxShadow: "0 0 24px rgba(79,209,197,0.3)", transition: "box-shadow 0.2s" }}
                  onMouseEnter={e => e.currentTarget.style.boxShadow = "0 0 40px rgba(79,209,197,0.5)"}
                  onMouseLeave={e => e.currentTarget.style.boxShadow = "0 0 24px rgba(79,209,197,0.3)"}>
                  Next <ArrowRight style={{ width: 15, height: 15 }} />
                </button>
              ) : (
                <button onClick={complete}
                  data-testid="onboarding-complete"
                  style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 22px", borderRadius: 11, background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`, color: "#030712", fontSize: 13, fontWeight: 700, border: "none", cursor: "pointer", boxShadow: "0 0 28px rgba(79,209,197,0.35)", transition: "box-shadow 0.2s" }}
                  onMouseEnter={e => e.currentTarget.style.boxShadow = "0 0 48px rgba(79,209,197,0.55)"}
                  onMouseLeave={e => e.currentTarget.style.boxShadow = "0 0 28px rgba(79,209,197,0.35)"}>
                  Start Chatting <ArrowRight style={{ width: 15, height: 15 }} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;
