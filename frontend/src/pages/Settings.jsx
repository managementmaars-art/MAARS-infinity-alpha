import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { 
  Bot, User, Mail, Shield, LogOut, CreditCard, Sparkles, Crown, Zap,
  LayoutDashboard, Users, MessageSquare, ListTodo, Settings, Menu, X
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [subscription, setSubscription] = useState(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const response = await fetch(`${API}/subscription`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        setSubscription(await response.json());
      }
    } catch (error) {
      console.error("Failed to fetch subscription");
    }
  };

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out successfully");
    navigate("/");
  };

  const getPlanIcon = (plan) => {
    switch (plan) {
      case "business": return <Crown className="w-5 h-5" />;
      case "pro": return <Sparkles className="w-5 h-5" />;
      case "starter": return <Zap className="w-5 h-5" />;
      default: return <CreditCard className="w-5 h-5" />;
    }
  };

  const getPlanColor = (plan) => {
    switch (plan) {
      case "business": return "text-amber-400 bg-amber-500/20";
      case "pro": return "text-violet-400 bg-violet-500/20";
      case "starter": return "text-indigo-400 bg-indigo-500/20";
      default: return "text-zinc-400 bg-zinc-500/20";
    }
  };

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active 
          ? "bg-indigo-500/20 text-indigo-400" 
          : "text-zinc-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </Link>
  );

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white font-['Outfit']">MAARS Global Corporation</span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <NavItem icon={LayoutDashboard} label="Dashboard" to="/dashboard" />
        <NavItem icon={MessageSquare} label="Chat" to="/chat" />
        <NavItem icon={Users} label="Agents" to="/agents" />
        <NavItem icon={ListTodo} label="Tasks" to="/tasks" />
        <NavItem icon={Settings} label="Settings" to="/settings" active />
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            {user?.picture ? (
              <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" />
            ) : (
              <span className="text-white font-semibold">{user?.name?.charAt(0) || "U"}</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.name}</p>
            <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start text-zinc-400 hover:text-white hover:bg-white/5 mt-2"
          onClick={handleLogout}
          data-testid="sidebar-logout-btn"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background" data-testid="settings-page">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white font-['Outfit']">MAARS Global Corporation</span>
          </Link>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-zinc-400">
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-zinc-900 border-r border-white/10">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 bottom-0 w-64 bg-zinc-900/50 border-r border-white/10">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-6 lg:p-8 max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2 font-['Outfit']">
              Settings
            </h1>
            <p className="text-zinc-400">Manage your account and preferences</p>
          </div>

          {/* Profile Section */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <User className="w-5 h-5 text-indigo-400" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center overflow-hidden">
                  {user?.picture ? (
                    <img src={user.picture} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-2xl text-white font-semibold">
                      {user?.name?.charAt(0) || "U"}
                    </span>
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{user?.name}</h3>
                  <p className="text-zinc-400">{user?.email}</p>
                </div>
              </div>

              <Separator className="bg-white/10" />

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-zinc-300">Full Name</Label>
                  <Input
                    value={user?.name || ""}
                    disabled
                    className="bg-zinc-800/50 border-white/10"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-zinc-300">Email</Label>
                  <Input
                    value={user?.email || ""}
                    disabled
                    className="bg-zinc-800/50 border-white/10"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Section */}
          <Card className="bg-zinc-900/50 border-white/10 mb-6">
            <CardHeader>
              <CardTitle className="text-white font-['Outfit'] flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-400" />
                Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-800/30">
                <div>
                  <p className="font-medium text-white">User ID</p>
                  <p className="text-sm text-zinc-400 font-mono">{user?.user_id}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-800/30">
                <div>
                  <p className="font-medium text-white">AI Providers</p>
                  <p className="text-sm text-zinc-400">OpenAI, Anthropic, Google Gemini</p>
                </div>
                <span className="px-3 py-1 text-xs rounded-full bg-emerald-500/20 text-emerald-400">
                  Connected
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="bg-zinc-900/50 border-red-500/20">
            <CardHeader>
              <CardTitle className="text-red-400 font-['Outfit']">Danger Zone</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Sign Out</p>
                  <p className="text-sm text-zinc-400">Sign out from your account</p>
                </div>
                <Button
                  variant="outline"
                  className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  onClick={handleLogout}
                  data-testid="logout-btn"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
