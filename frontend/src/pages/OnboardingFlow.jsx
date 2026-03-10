import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  Bot, ArrowRight, ArrowLeft, MessageSquare, CreditCard, Sparkles,
  Zap, Users, X, CheckCircle, Brain, Volume2, Image, FileText
} from "lucide-react";
import { Button } from "../components/ui/button";

const steps = [
  {
    id: "welcome",
    title: "Welcome to MAARS ∞",
    subtitle: "Your AI-powered team is ready",
  },
  {
    id: "agents",
    title: "Meet Your AI Team",
    subtitle: "21 specialists ready to work for you",
  },
  {
    id: "how-it-works",
    title: "How It Works",
    subtitle: "Three simple steps to get started",
  },
  {
    id: "features",
    title: "Powerful Capabilities",
    subtitle: "Everything your AI team can do",
  },
  {
    id: "ready",
    title: "You're All Set!",
    subtitle: "Start chatting with your AI team",
  },
];

const OnboardingFlow = ({ onComplete }) => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [agents, setAgents] = useState([]);
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    fetch(`${API}/agents/public`)
      .then(r => r.json())
      .then(data => setAgents(data.slice(0, 8)))
      .catch(() => {});
  }, []);

  const handleComplete = async () => {
    setExiting(true);
    try {
      await fetch(`${API}/auth/onboarding-complete`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }
      });
    } catch {}
    setTimeout(() => onComplete(), 300);
  };

  const handleSkip = async () => {
    setExiting(true);
    try {
      await fetch(`${API}/auth/onboarding-complete`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }
      });
    } catch {}
    setTimeout(() => onComplete(), 300);
  };

  const next = () => step < steps.length - 1 && setStep(s => s + 1);
  const prev = () => step > 0 && setStep(s => s - 1);
  const current = steps[step];

  return (
    <div className={`fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md transition-opacity duration-300 ${exiting ? "opacity-0" : "opacity-100"}`} data-testid="onboarding-overlay">
      <div className="relative w-full max-w-2xl mx-4">
        {/* Skip button */}
        <button
          onClick={handleSkip}
          className="absolute -top-12 right-0 text-zinc-500 hover:text-white text-sm flex items-center gap-1 transition-colors"
          data-testid="onboarding-skip"
        >
          Skip tour <X className="w-4 h-4" />
        </button>

        {/* Card */}
        <div className="bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          {/* Progress bar */}
          <div className="h-1 bg-white/5">
            <div
              className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-500"
              style={{ width: `${((step + 1) / steps.length) * 100}%` }}
            />
          </div>

          <div className="p-8 min-h-[420px] flex flex-col">
            {/* Step indicator */}
            <div className="flex items-center gap-2 mb-6">
              {steps.map((_, i) => (
                <div
                  key={i}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    i === step ? "w-8 bg-red-500" : i < step ? "w-4 bg-red-500/40" : "w-4 bg-white/10"
                  }`}
                />
              ))}
            </div>

            {/* Content */}
            <div className="flex-1">
              {current.id === "welcome" && (
                <div className="text-center space-y-6" data-testid="onboarding-step-welcome">
                  <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-white font-['Outfit']">Welcome to MAARS ∞</h2>
                    <p className="text-zinc-400 mt-2 text-lg">{user?.name ? `Hey ${user.name.split(" ")[0]}!` : "Hey!"} Your AI-powered team is ready to work.</p>
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-4">
                    {[
                      { icon: Bot, label: "458+ AI Agents", desc: "Specialized experts" },
                      { icon: Brain, label: "Smart AI", desc: "Asks questions first" },
                      { icon: Zap, label: "Instant Results", desc: "Files, images & more" },
                    ].map((item, i) => (
                      <div key={i} className="p-4 rounded-xl bg-white/5 text-center">
                        <item.icon className="w-6 h-6 text-red-400 mx-auto mb-2" />
                        <p className="text-sm text-white font-medium">{item.label}</p>
                        <p className="text-xs text-zinc-500">{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {current.id === "agents" && (
                <div className="space-y-5" data-testid="onboarding-step-agents">
                  <div>
                    <h2 className="text-2xl font-bold text-white font-['Outfit']">Meet Your AI Team</h2>
                    <p className="text-zinc-400 mt-1">Each agent is a specialist. Pick the right one for your task.</p>
                  </div>
                  <div className="grid grid-cols-4 gap-3">
                    {agents.map((agent) => (
                      <div key={agent.agent_id} className="p-3 rounded-xl bg-white/5 text-center hover:bg-white/10 transition-colors">
                        <img src={agent.avatar} alt="" className="w-12 h-12 rounded-lg mx-auto mb-2 object-cover" />
                        <p className="text-xs text-white font-medium truncate">{agent.name}</p>
                        <p className="text-[10px] text-zinc-500 truncate">{agent.role}</p>
                      </div>
                    ))}
                  </div>
                  <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <p className="text-amber-300 text-sm">
                      <strong>Commander Orion</strong> is your lead agent. Give it a complex goal and it delegates to the right specialists automatically.
                    </p>
                  </div>
                </div>
              )}

              {current.id === "how-it-works" && (
                <div className="space-y-5" data-testid="onboarding-step-how">
                  <div>
                    <h2 className="text-2xl font-bold text-white font-['Outfit']">How It Works</h2>
                    <p className="text-zinc-400 mt-1">Getting results is as easy as 1-2-3.</p>
                  </div>
                  <div className="space-y-4">
                    {[
                      { num: "1", title: "Pick an Agent", desc: "Choose the specialist that fits your task. Marketing? Finance? Design? We've got you covered.", icon: Users },
                      { num: "2", title: "Describe Your Task", desc: "Just type what you need in plain English. The AI will ask clarifying questions if needed.", icon: MessageSquare },
                      { num: "3", title: "Get Results", desc: "Receive expert-level output — text, PDFs, images, or even videos. Download and use instantly.", icon: CheckCircle },
                    ].map((item, i) => (
                      <div key={i} className="flex items-start gap-4 p-4 rounded-xl bg-white/5">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shrink-0">
                          <span className="text-white font-bold text-sm">{item.num}</span>
                        </div>
                        <div>
                          <p className="text-white font-medium flex items-center gap-2">
                            {item.title} <item.icon className="w-4 h-4 text-zinc-500" />
                          </p>
                          <p className="text-zinc-400 text-sm mt-0.5">{item.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {current.id === "features" && (
                <div className="space-y-5" data-testid="onboarding-step-features">
                  <div>
                    <h2 className="text-2xl font-bold text-white font-['Outfit']">Powerful Capabilities</h2>
                    <p className="text-zinc-400 mt-1">Everything your AI team can do for you.</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { icon: FileText, title: "Document Generation", desc: "PDF, Word documents instantly", color: "blue" },
                      { icon: Image, title: "Image Creation", desc: "AI-generated visuals on demand", color: "purple" },
                      { icon: Volume2, title: "Voice Mode", desc: "Listen to AI responses out loud", color: "emerald" },
                      { icon: Brain, title: "Smart Collaboration", desc: "Agents consult each other", color: "amber" },
                      { icon: CreditCard, title: "Flexible Pricing", desc: "Pay only for what you use", color: "rose" },
                      { icon: Users, title: "Team Access", desc: "Invite your team to collaborate", color: "cyan" },
                    ].map((item, i) => (
                      <div key={i} className={`p-4 rounded-xl bg-${item.color}-500/10 border border-${item.color}-500/20`}>
                        <item.icon className={`w-5 h-5 text-${item.color}-400 mb-2`} />
                        <p className="text-white text-sm font-medium">{item.title}</p>
                        <p className="text-zinc-500 text-xs mt-0.5">{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {current.id === "ready" && (
                <div className="text-center space-y-6" data-testid="onboarding-step-ready">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                    <CheckCircle className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-white font-['Outfit']">You're All Set!</h2>
                    <p className="text-zinc-400 mt-2 text-lg">Start by chatting with any agent. Try asking for something specific!</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/5 text-left max-w-sm mx-auto">
                    <p className="text-xs text-zinc-500 mb-2">Try saying:</p>
                    <p className="text-sm text-white italic">"Create a social media strategy for my coffee shop and give me a PDF"</p>
                  </div>
                </div>
              )}
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between pt-6 mt-auto">
              <Button
                onClick={prev}
                variant="ghost"
                className={`text-zinc-400 hover:text-white ${step === 0 ? "invisible" : ""}`}
                data-testid="onboarding-prev"
              >
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
              </Button>

              <span className="text-xs text-zinc-600">{step + 1} / {steps.length}</span>

              {step < steps.length - 1 ? (
                <Button
                  onClick={next}
                  className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600"
                  data-testid="onboarding-next"
                >
                  Next <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleComplete}
                  className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600"
                  data-testid="onboarding-complete"
                >
                  Start Chatting <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;
