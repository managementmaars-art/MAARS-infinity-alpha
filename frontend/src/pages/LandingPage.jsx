import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Bot, Sparkles, Users, Zap, MessageSquare, BarChart3, ChevronRight, Menu, X } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const agents = [
    { name: "Commander Orion", role: "AI Commander", avatar: "https://static.prod-images.emergentagent.com/jobs/f339b0b8-5eaf-45b0-8c04-0efb16af4bdd/images/77f99f67e5b8cde95d04a3ea56cf1321f7f64cbc04dd85513e1028ca8f39742d.png", capabilities: ["Task Delegation", "Strategy", "Orchestration"], isCommander: true },
    { name: "Nadia Kessler", role: "Personal Secretary", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/43ae7e2a837703cb3a5da4fdd616bc12c825f9f0f15b7e9304e61a3dab0bd257.png", capabilities: ["Scheduling", "To-Do Lists", "Email Drafting"] },
    { name: "Zara Mitchell", role: "Marketing Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c4305af2c26cea8648db361e275c2f1ef2db69815efff20a57aa4e0807abfcce.png", capabilities: ["Social Media", "Ad Copy", "Campaigns"] },
    { name: "Victor Ashford", role: "Business Strategist", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/48310a3af62b331e8f13d73aa7ac03cdfd9565c00fc03fd7dade81f63edfe3a7.png", capabilities: ["Strategy", "Market Research", "Analysis"] },
    { name: "Luna Bergström", role: "Web Designer", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c608195e54230fb30922f73d04dd840a095e7d6ee759b4b9cfe368511284876d.png", capabilities: ["UI/UX", "Landing Pages", "Branding"] },
    { name: "Kai Nakamoto", role: "App Developer", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/2ceaf34f302e1bf7d622058c516b8e86782c142d9a32dee38b13da10b8f0514c.png", capabilities: ["Web Apps", "Mobile Apps", "Full-Stack"] },
    { name: "Scarlett Monroe", role: "Copywriter", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/364a8796cacf09680e368da7737c0d32f0d34938f50d178f486f16f83c2e1ce8.png", capabilities: ["Blog Posts", "Ad Copy", "Scripts"] },
    { name: "Derek Huang", role: "SEO Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/575d3fa6dfe02ec1dde1be4b46bc425f0647b8dc1f7959861024495b0c991eb2.png", capabilities: ["Keywords", "Technical SEO", "Analytics"] },
    { name: "Marcus Drake", role: "Sales Representative", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/c183841a001848d4235ef461c6c731daaf15852f71079333c626183e3cfaa67b.png", capabilities: ["Outreach", "Proposals", "CRM"] },
    { name: "Isla Fernandez", role: "Social Media Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/11308bd62064960ead4e2c6adb4934fcdf47ed8b1357075c86b86f1c974502db.png", capabilities: ["Content Strategy", "Engagement", "Analytics"] },
    { name: "Ethan Yates", role: "Data Analyst", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/41cc382a93f5b9105d6252da9c6b9754cc71e5f2438307cd4676a5df0feb077d.png", capabilities: ["Data Viz", "Reports", "SQL"] },
    { name: "Olivia Sinclair", role: "Content Writer", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/be456d87bf888f7ffc615e88032ea91c8816865cda575c8fdec6ada768e9a8b6.png", capabilities: ["Articles", "Stories", "Editing"] },
    { name: "Maya Thompson", role: "Customer Service Rep", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/601d2cc63be741316b3042b97fc364bb288b747f3490b760d142235111bbed8c.png", capabilities: ["Support", "FAQ", "Tickets"] },
    { name: "Nathan Cross", role: "Project Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/0419179a9ce4a57469625597d87d30675989fd8bbd9b2f017e6fb0622a28a325.png", capabilities: ["Agile", "Planning", "Timelines"] },
    { name: "Dr. Clara Voss", role: "Research Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/cf9a66c94564c9aa42c5847e1313438dc6d5effe45cb2e3d7b22adafef90cb9f.png", capabilities: ["Papers", "Analysis", "Citations"] },
    { name: "Benjamin Cole", role: "Financial Analyst", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/25cf7622e2dfbda1f6cd5969206619ac8c6a05480e705b84a5aac0046fe64cff.png", capabilities: ["Forecasting", "Budgets", "Reports"] },
    { name: "Amara Johnson", role: "HR Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/ba854821cc88befbefce7c5afd73b5ad0dc7299629c8c5cbc86710a4f7518cd3.png", capabilities: ["Recruiting", "Policies", "Onboarding"] },
    { name: "Felix Romano", role: "Graphic Designer", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/96d5c274e3657d527a5a8c4bf869dcfdb08530445029e0df555139dba990b2cc.png", capabilities: ["Logos", "Illustrations", "Branding"] },
    { name: "Alexandra Reid", role: "Legal Assistant", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/5173ff78c8d19fc7d2e4cea3f7068c8f31edb314bbb9211a14a7196dc3465f9a.png", capabilities: ["Contracts", "Compliance", "Legal Docs"] },
    { name: "Jasper Wells", role: "Email Marketing", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/4227fcd5613d5f75952dc16c7342647a701d8e9b29d70a0a99fd16932db94a85.png", capabilities: ["Campaigns", "Newsletters", "A/B Testing"] },
    { name: "Riley Chen", role: "Video Content", avatar: "https://static.prod-images.emergentagent.com/jobs/d5c3c70f-465d-437e-854c-b31caef3b9ee/images/0a2a672b36a390684ba6cf87b46621f3169e140edd6a7a8cff09df93200e921b.png", capabilities: ["Scripts", "Storyboards", "Editing"] }
  ];

  const features = [
    {
      icon: <Bot className="w-6 h-6" />,
      title: "Specialized AI Agents",
      description: "Pre-built expert agents for marketing, sales, development, and more."
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Custom Agent Builder",
      description: "Create personalized AI agents tailored to your specific workflow needs."
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Agent Collaboration",
      description: "Multiple agents working together to tackle complex tasks efficiently."
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Intelligent Chat",
      description: "Natural conversations with context-aware AI that remembers your history."
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Task Management",
      description: "Assign tasks to agents and track progress with detailed results."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Multiple LLM Support",
      description: "Powered by OpenAI, Claude, and Gemini for the best AI capabilities."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white font-['Outfit']">Martian AI</span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="#agents" className="text-zinc-400 hover:text-white transition-colors">Agents</a>
              <Link to="/pricing" className="text-zinc-400 hover:text-white transition-colors" data-testid="pricing-link">Pricing</Link>
              <Link to="/login" className="text-zinc-400 hover:text-white transition-colors" data-testid="login-link">Login</Link>
              <Button 
                onClick={() => navigate("/register")} 
                className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary"
                data-testid="get-started-btn"
              >
                Get Started
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-zinc-400 hover:text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden glass border-t border-white/10">
            <div className="px-4 py-4 space-y-4">
              <a href="#features" className="block text-zinc-400 hover:text-white">Features</a>
              <a href="#agents" className="block text-zinc-400 hover:text-white">Agents</a>
              <Link to="/pricing" className="block text-zinc-400 hover:text-white">Pricing</Link>
              <Link to="/login" className="block text-zinc-400 hover:text-white">Login</Link>
              <Button 
                onClick={() => navigate("/register")} 
                className="w-full bg-gradient-to-r from-indigo-500 to-violet-500"
              >
                Get Started
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1710957987034-cea509422852?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxhYnN0cmFjdCUyMGZ1dHVyaXN0aWMlMjBkaWdpdGFsJTIwbmV0d29yayUyMGNvbm5lY3Rpb24lMjBkYXJrJTIwYmx1ZSUyMHB1cnBsZXxlbnwwfHx8fDE3NzIwNjg5ODl8MA&ixlib=rb-4.1.0&q=85')",
            backgroundSize: "cover",
            backgroundPosition: "center"
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/50 via-background/80 to-background" />
        
        <div className="relative max-w-7xl mx-auto text-left">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 animate-fade-in">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-sm text-zinc-300">Powered by GPT-5.2, Claude & Gemini</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6 font-['Outfit'] animate-slide-up">
              Your AI Team,
              <span className="gradient-text"> Always Ready</span>
            </h1>
            
            <p className="text-lg text-zinc-400 mb-8 max-w-2xl animate-slide-up stagger-1" style={{ opacity: 0 }}>
              Build, customize, and deploy specialized AI agents that work together to accomplish your goals. From marketing to development, your AI team handles it all.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 animate-slide-up stagger-2" style={{ opacity: 0 }}>
              <Button 
                size="lg"
                onClick={() => navigate("/register")}
                className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary text-lg px-8"
                data-testid="hero-get-started-btn"
              >
                Start Building <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg"
                variant="outline"
                onClick={() => navigate("/login")}
                className="border-white/20 hover:bg-white/10 text-lg px-8"
                data-testid="hero-login-btn"
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
              Everything You Need
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl">
              A complete AI team platform with powerful features to supercharge your productivity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-6 rounded-xl glass glass-hover group cursor-default animate-slide-up"
                style={{ animationDelay: `${index * 0.1}s`, opacity: 0 }}
                data-testid={`feature-card-${index}`}
              >
                <div className="w-12 h-12 rounded-lg bg-indigo-500/20 flex items-center justify-center mb-4 text-indigo-400 group-hover:bg-indigo-500/30 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">{feature.title}</h3>
                <p className="text-zinc-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Agents Section */}
      <section id="agents" className="py-20 px-4 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
              Meet Your AI Team
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl">
              20 specialized AI employees ready to work for you - from secretaries to developers, marketers to analysts.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {agents.map((agent, index) => (
              <div
                key={index}
                className={`relative overflow-hidden rounded-xl glass glass-hover group animate-slide-up cursor-pointer ${agent.isCommander ? "ring-2 ring-amber-500/60 col-span-2 sm:col-span-1" : ""}`}
                style={{ animationDelay: `${(index % 10) * 0.05}s`, opacity: 0 }}
                data-testid={`agent-preview-${index}`}
                onClick={() => navigate("/register")}
              >
                {agent.isCommander && (
                  <div className="absolute top-2 right-2 z-10 px-2 py-0.5 text-[10px] font-bold bg-amber-500/90 text-black rounded-full">
                    COMMANDER
                  </div>
                )}
                <div className="aspect-square relative overflow-hidden">
                  <img
                    src={agent.avatar}
                    alt={agent.name}
                    className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/40 to-transparent" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-indigo-400 text-[10px] sm:text-xs">{agent.role}</p>
                  <h3 className="text-sm sm:text-base font-bold text-white font-['Outfit'] truncate">{agent.name}</h3>
                  <div className="hidden sm:flex flex-wrap gap-1 mt-1.5">
                    {agent.capabilities.slice(0, 2).map((cap, i) => (
                      <span key={i} className="px-1.5 py-0.5 text-[10px] rounded-full bg-white/10 text-zinc-300">
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Button
              size="lg"
              onClick={() => navigate("/register")}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary"
              data-testid="agents-cta-btn"
            >
              Access All Agents <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* AI Models Section */}
      <section id="models" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
              Powered by World-Class AI Models
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
              Every agent intelligently selects the best model for each task, or you can choose manually from 10 frontier models.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* OpenAI */}
            <div className="p-6 rounded-xl glass animate-slide-up" style={{ animationDelay: '0s', opacity: 0 }} data-testid="models-openai">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold text-white font-['Outfit']">OpenAI</h3>
              </div>
              <div className="space-y-3">
                {[
                  { name: "GPT-5.2", tag: "Flagship", desc: "Most capable model for coding, analysis & complex tasks", color: "emerald" },
                  { name: "GPT-4o", tag: "Fast", desc: "Balanced speed and quality for everyday tasks", color: "emerald" },
                  { name: "GPT-4o Mini", tag: "Economy", desc: "Cost-efficient for simple questions & quick answers", color: "zinc" },
                  { name: "O3", tag: "Reasoning", desc: "Advanced reasoning for math, logic & problem-solving", color: "amber" },
                  { name: "O3 Mini", tag: "Reasoning", desc: "Lightweight reasoning for everyday analytical tasks", color: "zinc" },
                ].map((m, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <div className="mt-0.5 w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium text-sm">{m.name}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full bg-${m.color}-500/20 text-${m.color}-400`}>{m.tag}</span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-0.5">{m.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Anthropic */}
            <div className="p-6 rounded-xl glass animate-slide-up" style={{ animationDelay: '0.1s', opacity: 0 }} data-testid="models-anthropic">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold text-white font-['Outfit']">Anthropic</h3>
              </div>
              <div className="space-y-3">
                {[
                  { name: "Claude Sonnet 4.5", tag: "Flagship", desc: "Best for creative writing, analysis & nuanced tasks", color: "orange" },
                  { name: "Claude Opus 4.5", tag: "Premium", desc: "Deep research, long-form content & complex analysis", color: "amber" },
                  { name: "Claude Haiku 4.5", tag: "Economy", desc: "Fast responses, summaries & lightweight tasks", color: "zinc" },
                ].map((m, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <div className="mt-0.5 w-2 h-2 rounded-full bg-orange-400 shrink-0" />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium text-sm">{m.name}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full bg-${m.color}-500/20 text-${m.color}-400`}>{m.tag}</span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-0.5">{m.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Google */}
            <div className="p-6 rounded-xl glass animate-slide-up" style={{ animationDelay: '0.2s', opacity: 0 }} data-testid="models-google">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white font-['Outfit']">Google</h3>
              </div>
              <div className="space-y-3">
                {[
                  { name: "Gemini 3 Flash", tag: "Fast", desc: "Lightning-fast responses for simple tasks & conversations", color: "blue" },
                  { name: "Gemini 3 Pro", tag: "Flagship", desc: "Multimodal capabilities for research & complex analysis", color: "blue" },
                ].map((m, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <div className="mt-0.5 w-2 h-2 rounded-full bg-blue-400 shrink-0" />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium text-sm">{m.name}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full bg-${m.color}-500/20 text-${m.color}-400`}>{m.tag}</span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-0.5">{m.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 rounded-lg bg-gradient-to-r from-indigo-500/10 to-violet-500/10 border border-indigo-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm font-semibold text-white">Smart Auto-Selection</span>
                </div>
                <p className="text-xs text-zinc-400">Each agent automatically picks the best model for the task — coding, creative writing, research, data analysis, and more.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
            Ready to Build Your AI Team?
          </h2>
          <p className="text-lg text-zinc-400 mb-8">
            Join thousands of professionals who are already leveraging AI to supercharge their workflow.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/register")}
              className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 glow-primary text-lg px-8"
              data-testid="cta-get-started-btn"
            >
              Get Started Free
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-white/10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <span className="text-zinc-400">Martian AI by MAARS Global Corporation © 2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-zinc-500">
            <a href="#models" className="hover:text-zinc-300 transition-colors">10 AI Models</a>
            <a href="#agents" className="hover:text-zinc-300 transition-colors">20 AI Agents</a>
            <Link to="/pricing" className="hover:text-zinc-300 transition-colors">Pricing</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
