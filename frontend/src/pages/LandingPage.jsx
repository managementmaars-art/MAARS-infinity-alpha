import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Bot, Sparkles, Users, Zap, MessageSquare, BarChart3, ChevronRight, Menu, X } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const agents = [
    { name: "Commander Orion", role: "AI Commander", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/9a3eb3186a873a3337de51d37d80e0dac2da6db7ef21b2bef016307c59557b27.png", capabilities: ["Task Delegation", "Strategy", "Orchestration"], isCommander: true },
    { name: "Nadia Kessler", role: "Personal Secretary", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/4e2850c614aa1c3711c4417f5358bd28b1b5c24bfa75abb3a1361b1fed079c60.png", capabilities: ["Scheduling", "To-Do Lists", "Email Drafting"] },
    { name: "Zara Mitchell", role: "Marketing Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/fb16f517812221326ad131382b9b06c3965961e251319d278f27e132382cbe59.png", capabilities: ["Social Media", "Ad Copy", "Campaigns"] },
    { name: "Victor Ashford", role: "Business Strategist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/5f057725298a1552ecc39a3c3de30b2068e94d77888fa433b28a81c254d6f366.png", capabilities: ["Strategy", "Market Research", "Analysis"] },
    { name: "Luna Bergström", role: "Web Designer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/18df20edd8fea63dd3f42bf6aa110307b55e1a46e57426bf4930c29c635857bf.png", capabilities: ["UI/UX", "Landing Pages", "Branding"] },
    { name: "Kai Nakamoto", role: "App Developer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/d61615bbb8ef939f24f083d0a30a5df23a49ea6ec19c4bb3032a7f594661effb.png", capabilities: ["Web Apps", "Mobile Apps", "Full-Stack"] },
    { name: "Scarlett Monroe", role: "Copywriter", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/9ebf04f46ebf0f541e00c1afa6a6cf2f60e5ff38caafaf777131b1dbb5631a51.png", capabilities: ["Blog Posts", "Ad Copy", "Scripts"] },
    { name: "Derek Huang", role: "SEO Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/f1478028a00b7568b29d851ee148d74298c984c0c84412512fafe6acecb79e68.png", capabilities: ["Keywords", "Technical SEO", "Analytics"] },
    { name: "Marcus Drake", role: "Sales Representative", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/f58dec61c7d57ae195e889db7f107160c013b6ca4f61bee75266edc8139e6f65.png", capabilities: ["Outreach", "Proposals", "CRM"] },
    { name: "Isla Fernandez", role: "Social Media Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/798f2bed9ad1f212875416e9f21ba960580048aeb210cb9efbde8bbc365f0a00.png", capabilities: ["Content Strategy", "Engagement", "Analytics"] },
    { name: "Ethan Yates", role: "Data Analyst", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/334c45614287e640d642e44c8e4f0c8838e0813105f170db17a003c0ac47802f.png", capabilities: ["Data Viz", "Reports", "SQL"] },
    { name: "Olivia Sinclair", role: "Content Writer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/6514b7a797d37d1e04470bfd5ec62dda493f71bbf1187da2dfc669ac4dea8984.png", capabilities: ["Articles", "Stories", "Editing"] },
    { name: "Maya Thompson", role: "Customer Service Rep", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/f06e5db223fc3ae402cb2fa11a430f404a64bec41c6252e9da47814aed1a8997.png", capabilities: ["Support", "FAQ", "Tickets"] },
    { name: "Nathan Cross", role: "Project Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/54fe8dafe0ffded87354be24fafd0ff2bbbebd2699b7671751bf16b64cbcd39d.png", capabilities: ["Agile", "Planning", "Timelines"] },
    { name: "Dr. Clara Voss", role: "Research Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/cf71c32849d1c29539e9bcc6673d483b4db0eb98f4ed89f3f8000bc5d23da801.png", capabilities: ["Papers", "Analysis", "Citations"] },
    { name: "Benjamin Cole", role: "Financial Analyst", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/6e0f47d6af19122133c6cc631c515a0de5493bd5976d95aea6f02e408e755931.png", capabilities: ["Forecasting", "Budgets", "Reports"] },
    { name: "Amara Johnson", role: "HR Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/ee7890378b0a54d85529a56bda988190c24693d702ff2ef004584cb89e8fe4ce.png", capabilities: ["Recruiting", "Policies", "Onboarding"] },
    { name: "Felix Romano", role: "Graphic Designer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/87f5df94dac8449fe045a0c876b50224b7c9dec0cecc9ad5ca49b3991efcfba0.png", capabilities: ["Logos", "Illustrations", "Branding"] },
    { name: "Alexandra Reid", role: "Legal Assistant", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/605e790242497984c3777d551af763849dc85b7c107cf6ca42b8bc399ebd63d8.png", capabilities: ["Contracts", "Compliance", "Legal Docs"] },
    { name: "Jasper Wells", role: "Email Marketing", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/d4091ddd69e0491820ee6a99bd6f186b74645e03de5037599d7d836a5e465c18.png", capabilities: ["Campaigns", "Newsletters", "A/B Testing"] },
    { name: "Riley Chen", role: "Video Content", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/2aaa884e525d1bb1afb68a429016993c0a24b4764a3c455022690c05c151b070.png", capabilities: ["Scripts", "Storyboards", "Editing"] },
    { name: "Damien Voss", role: "Cybersecurity Officer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/7eb081231afdea773949d6946afd7a1bbae48d272b14f772a7627f7b90e83ba1.png", capabilities: ["Security Audits", "Threat Analysis", "Compliance"] },
    { name: "Serena Okafor", role: "Automation Engineer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/181e17ed139f7030802f0c3ae0801ea69b15f780828b07cc8329a77b03b42bea.png", capabilities: ["Workflows", "Integrations", "Automation"] },
    { name: "Axel Brennan", role: "Growth Hacker", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/9f40cce8b43dc4c59cb24cc91e4b666fefe90ce2e51ade93e45680337e63c643.png", capabilities: ["Growth Experiments", "A/B Testing", "Funnels"] },
    { name: "Victoria Harrington", role: "Compliance Officer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/23f2f01a9c55a73c9e199bce775bc74541dc0311694e5fd12987682886041616.png", capabilities: ["Regulatory", "Audits", "GDPR"] },
    { name: "Dr. Luca Bernstein", role: "AI Optimizer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/d888a9a6ab8bd8a3afe850ddbf31e706fc38e011b454a3e8acf4a8ebe0e9f165.png", capabilities: ["AI Tuning", "Cost Reduction", "Prompts"] },
    { name: "Diana Morales", role: "Operations Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/d974fde36e8b923670637ccaa3babac5b46cc28fade0c0033c96ba86b4d66091.png", capabilities: ["Process", "Supply Chain", "KPIs"] },
    { name: "Maximilian Wolfe", role: "Revenue Strategist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/707cf99fa483834d42b8825e48537bbd3351e4e3f465e88bdd0c577d54e6b92c.png", capabilities: ["Pricing", "Revenue Models", "Monetization"] },
    { name: "Cassandra Steele", role: "Chief Strategy Officer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/e5ef1d410dcd7e499baa4089564365be54806a20a1946170f4a53d7b43e976a4.png", capabilities: ["Corporate Strategy", "Market Expansion", "OKRs"] },
    { name: "Richard Ashworth", role: "Investor Relations", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/da0d3b9c51198fe0df21bc3c98f064839f81dea915c88e590cf7b8d9380dd8c2.png", capabilities: ["Pitch Decks", "Fundraising", "Valuations"] },
    { name: "Priya Kapoor", role: "Product Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/3de9f03d7891c8833bf377ba7f45efad1b78b195066710674ef4d8ea83a3bce1.png", capabilities: ["Roadmaps", "User Stories", "Sprints"] },
    { name: "Nikolai Volkov", role: "Data Engineer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/c565764f7f90fc78fc100d2f4b4ff43c8baf755ace694139c1c54ee96a0429e4.png", capabilities: ["Pipelines", "ETL", "Databases"] },
    { name: "Valentina Cruz", role: "Brand Architect", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/19d90fd5dc3ea2d4ce4d9916762a4ebead00fdfdad82397a879c59099a3d516f.png", capabilities: ["Brand Identity", "Guidelines", "Visual Systems"] },
    { name: "Yuki Tanaka", role: "UX Researcher", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/db0fa9edc51497eef8627fe55936a764657127f3627fff193b6a09571c8885bb.png", capabilities: ["User Research", "Usability", "Personas"] },
    { name: "Marco De Luca", role: "3D Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/8ec4b4a27946e20891cca2de789d559338c6ab2f18a63b0ecebfa6eaa013fd8a.png", capabilities: ["3D Rendering", "Motion Graphics", "AR/VR"] },
    { name: "Catherine Blake", role: "PR Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/706aaf93ddbb0793256c82bd6389048070877ee8dee4e69b64b4abb02d8420c8.png", capabilities: ["PR Strategy", "Crisis Mgmt", "Media"] },
    { name: "Arjun Mehta", role: "Procurement Manager", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/84eae30d456323c117055f6217e22dead13c792020daf9019af55c745f44a344.png", capabilities: ["Vendor Mgmt", "Contracts", "Supply Chain"] },
    { name: "Sofia Reyes", role: "CX Architect", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/c2715d85ace40876df7f859d06f00275e4a34ca06d90436090bfd9569e6c6b24.png", capabilities: ["Journey Maps", "Loyalty", "NPS"] },
    { name: "Prof. James Whitfield", role: "Ethics Officer", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/5ab58f9fabff5a03e86596e12c555d71e72d4821271702c03f48eddc4cbef804.png", capabilities: ["Ethics", "Risk", "Governance"] },
    { name: "Dr. Eleanor Shaw", role: "Knowledge Architect", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/ea78ac11ca9f7675017f9311b0f4dcc70a5fb2f4344f8701aceab4b9dc242718.png", capabilities: ["Knowledge Mgmt", "Documentation", "Taxonomies"] },
    { name: "Layla Mansouri", role: "Localization Specialist", avatar: "https://static.prod-images.emergentagent.com/jobs/e3072301-4a05-4a6d-b37b-ba078a6b936d/images/d4c51d4c86045d6d0d1d9dccec55d81792f448d8734452de56f90e029c602ed5.png", capabilities: ["Localization", "Translation", "Global Markets"] }
  ];

  const features = [
    {
      icon: <Bot className="w-6 h-6" />,
      title: "458+ Specialized AI Agents",
      description: "Pre-built expert agents across 27 networks — engineering, finance, legal, creative, and more."
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Knowledge Graph",
      description: "Visualize how agents, networks, products, and ventures interconnect in a living knowledge map."
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Agent Collaboration",
      description: "Multiple agents working together across 27 specialized networks to tackle complex goals."
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Chat with Any Agent",
      description: "Natural conversations with 458+ context-aware AI agents, each with unique expertise and tools."
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Trust Scores & Execution Gateway",
      description: "Every action is governed, metered, and audited. Agent trust scores built from execution history."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "30+ AI Models",
      description: "Powered by OpenAI, Claude, Gemini, Grok, DeepSeek, Mistral, and more with smart auto-routing."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
              <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-8 h-8 rounded-lg object-cover" />
              <span className="text-xl font-bold text-white font-['Outfit']">MAARS ∞</span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="#agents" className="text-zinc-400 hover:text-white transition-colors">Agents</a>
              <Link to="/pricing" className="text-zinc-400 hover:text-white transition-colors" data-testid="pricing-link">Pricing</Link>
              <Link to="/login" className="text-zinc-400 hover:text-white transition-colors" data-testid="login-link">Login</Link>
              <Button 
                onClick={() => navigate("/register")} 
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 glow-primary"
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
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600"
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
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-zinc-300">Powered by GPT-5.2, Claude, Gemini, Sora 2, DALL-E 3 & Whisper</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6 font-['Outfit'] animate-slide-up">
              Your AI Team,
              <span className="gradient-text"> Always Ready</span>
            </h1>
            
            <p className="text-lg text-zinc-400 mb-8 max-w-2xl animate-slide-up stagger-1" style={{ opacity: 0 }}>
              458+ specialized AI agents across 27 networks, powered by 30+ AI models. Build, orchestrate, and govern your autonomous AI workforce with enterprise-grade trust scoring and execution governance.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 animate-slide-up stagger-2" style={{ opacity: 0 }}>
              <Button 
                size="lg"
                onClick={() => navigate("/register")}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 glow-primary text-lg px-8"
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
                <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4 text-blue-400 group-hover:bg-blue-500/30 transition-colors">
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
              458+ specialized AI agents ready to work for you - from strategists to developers, marketers to analysts.
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
                  <p className="text-blue-400 text-[10px] sm:text-xs">{agent.role}</p>
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
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 glow-primary"
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
              Every agent intelligently selects from 45+ frontier models across 13 providers — or you can choose manually.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: "OpenAI", color: "emerald", icon: "emerald", models: [
                { name: "GPT-5.2", tag: "Flagship", desc: "Most capable for coding, analysis & complex tasks" },
                { name: "GPT-4o", tag: "Fast", desc: "Balanced speed and quality" },
                { name: "GPT-4o Mini", tag: "Economy", desc: "Cost-efficient for quick answers" },
                { name: "O3", tag: "Reasoning", desc: "Advanced reasoning for math & logic" },
                { name: "O3 Mini", tag: "Reasoning", desc: "Lightweight analytical tasks" },
              ]},
              { name: "Anthropic", color: "orange", models: [
                { name: "Claude Sonnet 4.5", tag: "Flagship", desc: "Creative writing, analysis & nuanced tasks" },
                { name: "Claude Opus 4.5", tag: "Premium", desc: "Deep research & complex analysis" },
                { name: "Claude Haiku 4.5", tag: "Economy", desc: "Fast responses & summaries" },
              ]},
              { name: "Google", color: "blue", models: [
                { name: "Gemini 3 Flash", tag: "Fast", desc: "Lightning-fast responses" },
                { name: "Gemini 3 Pro", tag: "Flagship", desc: "Multimodal research & analysis" },
              ]},
              { name: "xAI (Grok)", color: "zinc", models: [
                { name: "Grok 3", tag: "Flagship", desc: "1M context, reasoning & analysis" },
                { name: "Grok 3 Mini", tag: "Economy", desc: "Cost-efficient reasoning" },
                { name: "Grok 2", tag: "Fast", desc: "Competitive with GPT-4o" },
              ]},
              { name: "DeepSeek", color: "cyan", models: [
                { name: "DeepSeek Chat", tag: "Economy", desc: "128K context, ultra-affordable" },
                { name: "DeepSeek Reasoner", tag: "Reasoning", desc: "Deep math & logic reasoning" },
              ]},
              { name: "Mistral AI", color: "violet", models: [
                { name: "Mistral Large", tag: "Flagship", desc: "Complex reasoning, enterprise-grade" },
                { name: "Mistral Medium", tag: "Fast", desc: "Balanced performance" },
                { name: "Mistral Small", tag: "Economy", desc: "Ultra-fast, simple tasks" },
              ]},
              { name: "Perplexity", color: "teal", models: [
                { name: "Sonar", tag: "Search", desc: "Web-grounded real-time answers" },
                { name: "Sonar Pro", tag: "Research", desc: "Deep web research with citations" },
              ]},
              { name: "Cohere", color: "pink", models: [
                { name: "Command R+", tag: "Flagship", desc: "RAG & enterprise tasks" },
                { name: "Command R", tag: "Economy", desc: "Cost-efficient summaries" },
              ]},
              { name: "AI Generation + Voice", color: "rose", models: [
                { name: "Nano Banana 2", tag: "Image Gen", desc: "Gemini 3.1 Flash image generation" },
                { name: "GPT Image 1", tag: "Image Gen", desc: "Generate images from text" },
                { name: "DALL-E 3", tag: "Image Gen", desc: "Creative image generation" },
                { name: "Sora 2", tag: "Video Gen", desc: "AI video from text prompts" },
                { name: "ElevenLabs", tag: "Voice", desc: "Multilingual TTS (Bangla, English, etc.)" },
                { name: "Whisper", tag: "STT", desc: "Speech-to-text in 50+ languages" },
              ]},
            ].map((provider, pi) => (
              <div key={pi} className="p-5 rounded-xl glass animate-slide-up" style={{ animationDelay: `${pi * 0.05}s`, opacity: 0 }} data-testid={`models-${provider.name.toLowerCase().replace(/[^a-z]/g, '')}`}>
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-9 h-9 rounded-lg bg-${provider.color}-500/20 flex items-center justify-center`}>
                    <Sparkles className={`w-4 h-4 text-${provider.color}-400`} />
                  </div>
                  <h3 className="text-lg font-bold text-white font-['Outfit']">{provider.name}</h3>
                </div>
                <div className="space-y-2">
                  {provider.models.map((m, mi) => (
                    <div key={mi} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                      <div className={`mt-1 w-1.5 h-1.5 rounded-full bg-${provider.color}-400 shrink-0`} />
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-white font-medium text-sm">{m.name}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-full bg-${provider.color}-500/20 text-${provider.color}-400`}>{m.tag}</span>
                        </div>
                        <p className="text-[11px] text-zinc-500 mt-0.5">{m.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Smart Auto-Selection card */}
            <div className="p-5 rounded-xl glass animate-slide-up flex flex-col justify-center" style={{ animationDelay: '0.45s', opacity: 0 }}>
              <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold text-white">Smart Auto-Selection</span>
                </div>
                <p className="text-xs text-zinc-400">Each agent picks the best model for the task automatically — coding, writing, research, or analysis.</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-xs text-zinc-400 text-center">
                  Also generates <span className="text-white font-medium">PDF, Excel, Word, CSV</span> documents on demand
                </p>
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
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 glow-primary text-lg px-8"
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
            <img src="/branding/maars-logo.jpeg" alt="MAARS" className="w-6 h-6 rounded object-cover" />
            <span className="text-zinc-400">MAARS ∞ by MAARS Global Corporation © 2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-zinc-500">
            <a href="#models" className="hover:text-zinc-300 transition-colors">10 AI Models</a>
            <a href="#agents" className="hover:text-zinc-300 transition-colors">458+ AI Agents</a>
            <Link to="/pricing" className="hover:text-zinc-300 transition-colors">Pricing</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
