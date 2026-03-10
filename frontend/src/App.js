import { useEffect, useRef, useState, createContext, useContext, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/Dashboard";
import AgentChat from "./pages/AgentChat";
import Agents from "./pages/Agents";
import CreateAgent from "./pages/CreateAgent";
import Tasks from "./pages/Tasks";
import Settings from "./pages/Settings";
import PricingPage from "./pages/PricingPage";
import PaymentSuccess from "./pages/PaymentSuccess";
import AdminDashboard from "./pages/AdminDashboard";
import Team from "./pages/Team";
import InsightsPage from "./pages/InsightsPage";
import ProductCatalog from "./pages/ProductCatalog";
import Projects from "./pages/Projects";
import WorkspaceBrain from "./pages/WorkspaceBrain";
import Approvals from "./pages/Approvals";
import BrainProfiles from "./pages/BrainProfiles";
import DashboardLayout from "./components/layout/DashboardLayout";
import KPIDashboard from "./pages/KPIDashboard";
import CollaborationEngine from "./pages/CollaborationEngine";
import ActivityMonitor from "./pages/ActivityMonitor";
import VibeCoding from "./pages/VibeCoding";
import ReferenceIntelligence from "./pages/ReferenceIntelligence";
import ContentGenerator from "./pages/ContentGenerator";
import AboutPage from "./pages/AboutPage";
import CodeExplorer from "./pages/CodeExplorer";
import MemoryGovernance from "./pages/MemoryGovernance";
import KernelDashboard from "./pages/KernelDashboard";
import AgentNetworks from "./pages/AgentNetworks";
import TaskGraphs from "./pages/TaskGraphs";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import TrustScores from "./pages/TrustScores";
import ExecutionGateway from "./pages/ExecutionGateway";
import RBAC from "./pages/RBAC";
import CircuitBreakers from "./pages/CircuitBreakers";
import CostGovernance from "./pages/CostGovernance";
import WorkflowBuilder from "./pages/WorkflowBuilder";
import Environments from "./pages/Environments";
import MemoryHierarchy from "./pages/MemoryHierarchy";
import CampaignBuilder from "./pages/CampaignBuilder";
import IntegrationHub from "./pages/IntegrationHub";
import Organization from "./pages/Organization";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import AgentSuggestions from "./pages/AgentSuggestions";
import {
  AdminOverviewPage, AdminAnalyticsPage, AdminUsersPage, AdminAgentsPage,
  AdminTransactionsPage, AdminPricingManagerPage, AdminApiKeysPage,
  AdminPaymentSetupPage, AdminSmtpPage, AdminBrandingPage,
  AdminKnowledgeBasePage, AdminAuditLogPage
} from "./pages/AdminPages";
import { Toaster } from "./components/ui/sonner";
import { Watermark } from "./components/Watermark";
import { BrandingProvider } from "./components/BrandingProvider";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem("token"));

  const checkAuth = useCallback(async (signal) => {
    // CRITICAL: Skip auth check if returning from OAuth callback
    if (window.location.hash?.includes('session_id=')) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API}/auth/me`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        signal,
      });

      if (signal?.aborted) return;

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
        localStorage.removeItem("token");
        setToken(null);
      }
    } catch (error) {
      if (error.name === 'AbortError') return;
      setUser(null);
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    const controller = new AbortController();
    checkAuth(controller.signal);
    return () => controller.abort();
  }, [checkAuth]);

  const login = (userData, authToken) => {
    setUser(userData);
    if (authToken) {
      localStorage.setItem("token", authToken);
      setToken(authToken);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API}/auth/logout`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
    } catch (error) {
      console.error("Logout error:", error);
    }
    setUser(null);
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, token, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

// Auth Callback Component
// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      const hash = location.hash;
      const sessionIdMatch = hash.match(/session_id=([^&]+)/);
      
      if (!sessionIdMatch) {
        navigate("/login");
        return;
      }

      const sessionId = sessionIdMatch[1];

      try {
        const response = await fetch(`${API}/auth/session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });

        if (response.ok) {
          const userData = await response.json();
          login(userData);
          navigate("/dashboard", { replace: true, state: { user: userData } });
        } else {
          navigate("/login");
        }
      } catch (error) {
        console.error("Auth callback error:", error);
        navigate("/login");
      }
    };

    processAuth();
  }, [location, navigate, login]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-muted-foreground">Authenticating...</p>
      </div>
    </div>
  );
};

// Protected Route
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user && !location.state?.user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Admin Protected Route
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Global floating credits display removed — credits are now in the sidebar

// App Router with session_id detection
const AppRouter = () => {
  const location = useLocation();
  
  // Check for session_id in URL fragment synchronously
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/payment/success" element={<ProtectedRoute><PaymentSuccess /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout><Dashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/chat/:agentId?" element={<ProtectedRoute><DashboardLayout><AgentChat /></DashboardLayout></ProtectedRoute>} />
      <Route path="/agents" element={<ProtectedRoute><DashboardLayout><Agents /></DashboardLayout></ProtectedRoute>} />
      <Route path="/agents/create" element={<ProtectedRoute><DashboardLayout><CreateAgent /></DashboardLayout></ProtectedRoute>} />
      <Route path="/products" element={<ProtectedRoute><DashboardLayout><ProductCatalog /></DashboardLayout></ProtectedRoute>} />
      <Route path="/projects/*" element={<ProtectedRoute><DashboardLayout><Projects /></DashboardLayout></ProtectedRoute>} />
      <Route path="/workspace" element={<ProtectedRoute><DashboardLayout><WorkspaceBrain /></DashboardLayout></ProtectedRoute>} />
      <Route path="/approvals" element={<ProtectedRoute><DashboardLayout><Approvals /></DashboardLayout></ProtectedRoute>} />
      <Route path="/brain-profiles" element={<ProtectedRoute><DashboardLayout><BrainProfiles /></DashboardLayout></ProtectedRoute>} />
      <Route path="/kpi-dashboard" element={<ProtectedRoute><DashboardLayout><KPIDashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/collaborations" element={<ProtectedRoute><DashboardLayout><CollaborationEngine /></DashboardLayout></ProtectedRoute>} />
      <Route path="/activity-monitor" element={<ProtectedRoute><DashboardLayout><ActivityMonitor /></DashboardLayout></ProtectedRoute>} />
      <Route path="/vibe-coding" element={<ProtectedRoute><DashboardLayout><VibeCoding /></DashboardLayout></ProtectedRoute>} />
      <Route path="/reference-intelligence" element={<ProtectedRoute><DashboardLayout><ReferenceIntelligence /></DashboardLayout></ProtectedRoute>} />
      <Route path="/content-generator" element={<ProtectedRoute><DashboardLayout><ContentGenerator /></DashboardLayout></ProtectedRoute>} />
      <Route path="/tasks" element={<ProtectedRoute><DashboardLayout><Tasks /></DashboardLayout></ProtectedRoute>} />
      <Route path="/team" element={<ProtectedRoute><DashboardLayout><Team /></DashboardLayout></ProtectedRoute>} />
      <Route path="/insights" element={<ProtectedRoute><DashboardLayout><InsightsPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><DashboardLayout><Settings /></DashboardLayout></ProtectedRoute>} />
      <Route path="/about" element={<ProtectedRoute><DashboardLayout><AboutPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/memory" element={<ProtectedRoute><DashboardLayout><MemoryGovernance /></DashboardLayout></ProtectedRoute>} />
      <Route path="/kernel" element={<ProtectedRoute><DashboardLayout><KernelDashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/networks" element={<ProtectedRoute><DashboardLayout><AgentNetworks /></DashboardLayout></ProtectedRoute>} />
      <Route path="/task-graphs" element={<ProtectedRoute><DashboardLayout><TaskGraphs /></DashboardLayout></ProtectedRoute>} />
      <Route path="/knowledge-graph" element={<ProtectedRoute><DashboardLayout><KnowledgeGraph /></DashboardLayout></ProtectedRoute>} />
      <Route path="/trust-scores" element={<ProtectedRoute><DashboardLayout><TrustScores /></DashboardLayout></ProtectedRoute>} />
      <Route path="/execution-gateway" element={<ProtectedRoute><DashboardLayout><ExecutionGateway /></DashboardLayout></ProtectedRoute>} />
      <Route path="/rbac" element={<ProtectedRoute><DashboardLayout><RBAC /></DashboardLayout></ProtectedRoute>} />
      <Route path="/circuit-breakers" element={<ProtectedRoute><DashboardLayout><CircuitBreakers /></DashboardLayout></ProtectedRoute>} />
      <Route path="/cost-governance" element={<ProtectedRoute><DashboardLayout><CostGovernance /></DashboardLayout></ProtectedRoute>} />
      <Route path="/workflow-builder" element={<ProtectedRoute><DashboardLayout><WorkflowBuilder /></DashboardLayout></ProtectedRoute>} />
      <Route path="/environments" element={<ProtectedRoute><DashboardLayout><Environments /></DashboardLayout></ProtectedRoute>} />
      <Route path="/memory-hierarchy" element={<ProtectedRoute><DashboardLayout><MemoryHierarchy /></DashboardLayout></ProtectedRoute>} />
      <Route path="/campaigns" element={<ProtectedRoute><DashboardLayout><CampaignBuilder /></DashboardLayout></ProtectedRoute>} />
      <Route path="/integrations" element={<ProtectedRoute><DashboardLayout><IntegrationHub /></DashboardLayout></ProtectedRoute>} />
      <Route path="/organization" element={<ProtectedRoute><DashboardLayout><Organization /></DashboardLayout></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><DashboardLayout><AnalyticsDashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/agent-suggestions" element={<ProtectedRoute><DashboardLayout><AgentSuggestions /></DashboardLayout></ProtectedRoute>} />
      <Route path="/admin" element={<AdminRoute><DashboardLayout><AdminOverviewPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/overview" element={<AdminRoute><DashboardLayout><AdminOverviewPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/analytics" element={<AdminRoute><DashboardLayout><AdminAnalyticsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/users" element={<AdminRoute><DashboardLayout><AdminUsersPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/agents" element={<AdminRoute><DashboardLayout><AdminAgentsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/transactions" element={<AdminRoute><DashboardLayout><AdminTransactionsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/pricing-manager" element={<AdminRoute><DashboardLayout><AdminPricingManagerPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/api-keys" element={<AdminRoute><DashboardLayout><AdminApiKeysPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/payments" element={<AdminRoute><DashboardLayout><AdminPaymentSetupPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/smtp" element={<AdminRoute><DashboardLayout><AdminSmtpPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/branding" element={<AdminRoute><DashboardLayout><AdminBrandingPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/knowledge" element={<AdminRoute><DashboardLayout><AdminKnowledgeBasePage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/audit" element={<AdminRoute><DashboardLayout><AdminAuditLogPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/code-explorer" element={<AdminRoute><DashboardLayout><CodeExplorer /></DashboardLayout></AdminRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BrandingProvider>
          <AppRouter />
          <Watermark />
          <Toaster position="top-right" richColors />
        </BrandingProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
