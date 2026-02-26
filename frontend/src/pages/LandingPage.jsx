import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Bot, Sparkles, Users, Zap, MessageSquare, BarChart3, ChevronRight, Menu, X } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const agents = [
    {
      name: "Victoria Sterling",
      role: "Chief Executive Officer",
      avatar: "https://images.unsplash.com/photo-1677212004257-103cfa6b59d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
      capabilities: ["Strategic Planning", "Leadership", "M&A Advisory"]
    },
    {
      name: "Marcus Chen",
      role: "Chief Financial Officer",
      avatar: "https://images.unsplash.com/photo-1535378917042-10a22c95931a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YWklMjByb2JvdHxlbnwwfHwwfHx8MA%3D%3D&ixlib=rb-4.1.0&q=85",
      capabilities: ["Financial Analysis", "Budgeting", "Investment Strategy"]
    },
    {
      name: "Dr. Aiden Nakamura",
      role: "Chief Technology Officer",
      avatar: "https://images.unsplash.com/photo-1760931969401-9bd6ee902798?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHwzZCUyMHJvYm90JTIwYXZhdGFyJTIwZnV0dXJpc3RpYyUyMGljb24lMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzIwNjg5OTF8MA&ixlib=rb-4.1.0&q=85",
      capabilities: ["Software Architecture", "AI/ML Strategy", "Cloud Infrastructure"]
    }
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
              <span className="text-xl font-bold text-white font-['Outfit']">MAARS Global Corporation</span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="#agents" className="text-zinc-400 hover:text-white transition-colors">Agents</a>
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
              Pre-built expert agents ready to tackle your tasks, or create your own custom agents.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <div
                key={index}
                className="relative overflow-hidden rounded-xl glass glass-hover group animate-slide-up"
                style={{ animationDelay: `${index * 0.15}s`, opacity: 0 }}
                data-testid={`agent-preview-${index}`}
              >
                <div className="aspect-square relative overflow-hidden">
                  <img
                    src={agent.avatar}
                    alt={agent.name}
                    className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/50 to-transparent" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <p className="text-indigo-400 text-sm mb-1">{agent.role}</p>
                  <h3 className="text-xl font-bold text-white mb-3 font-['Outfit']">{agent.name}</h3>
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.map((cap, i) => (
                      <span key={i} className="px-2 py-1 text-xs rounded-full bg-white/10 text-zinc-300">
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
            <span className="text-zinc-400">MAARS Global Corporation © 2024</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-zinc-500">
            <span>Powered by OpenAI, Anthropic & Google</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
