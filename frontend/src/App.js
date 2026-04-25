import { useEffect, useRef, useState, createContext, useContext, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import ChangelogPage from "./pages/ChangelogPage";
import AlternativesHub from "./pages/AlternativesHub";
import AlternativePage from "./pages/AlternativePage";
import { JASPER, COPY_AI, CURSOR, LOVABLE } from "./pages/alternatives/configs";
import SubprocessorsPage from "./pages/SubprocessorsPage";
import { BlogListPage, BlogPostPage } from "./pages/BlogPage";
import CookieConsent from "./components/CookieConsent";
import Analytics from "./components/Analytics";
import ExitIntentPopup from "./components/ExitIntentPopup";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardHub from "./pages/DashboardHub";
import AgentChat from "./pages/AgentChat";
import AgentsHub from "./pages/AgentsHub";
import Tasks from "./pages/Tasks";
import Settings from "./pages/Settings";
import PricingPage from "./pages/PricingPage";
import PaymentSuccess from "./pages/PaymentSuccess";
import WalletDashboard from "./pages/WalletDashboard";
import ApiKeysPage from "./pages/ApiKeysPage";
// /admin/metrics merged into /admin/gateway Financials tab (Audit 016)
import ProviderIntelligencePage from "./pages/ProviderIntelligencePage";
import SetupWizard from "./pages/SetupWizard";
// AdminPackagesPage retired — its features (operator splits, customer overrides,
// audit slice) folded into the existing AdminPricingManagerPage as part of the
// Option-B unification.
import Team from "./pages/Team";
import InsightsPage from "./pages/InsightsPage";
import ProductCatalog from "./pages/ProductCatalog";
import Projects from "./pages/Projects";
import MemoryHub from "./pages/MemoryHub";
import Approvals from "./pages/Approvals";
import DashboardLayout from "./components/layout/DashboardLayout";
import CollaborationEngine from "./pages/CollaborationEngine";
import VibeCoding from "./pages/VibeCoding";
import ReferenceIntelligence from "./pages/ReferenceIntelligence";
import ContentGenerator from "./pages/ContentGenerator";
import AboutPage from "./pages/AboutPage";
import CodeExplorer from "./pages/CodeExplorer";
import KernelDashboard from "./pages/KernelDashboard";
import AgentNetworks from "./pages/AgentNetworks";
import TaskGraphs from "./pages/TaskGraphs";
import ExecutionGateway from "./pages/ExecutionGateway";
import WorkflowBuilder from "./pages/WorkflowBuilder";
import Environments from "./pages/Environments";
import CampaignBuilder from "./pages/CampaignBuilder";
import IntegrationHub from "./pages/IntegrationHub";
import Organization from "./pages/Organization";
import TeamBuilder from "./pages/TeamBuilder";
import OutcomesOverview from "./pages/OutcomesOverview";
import VenturePortfolio from "./pages/VenturePortfolio";
import CommanderOrion from "./pages/CommanderOrion";
import DeveloperPortal from './pages/DeveloperPortal';
import UniversalKeyPage from './pages/UniversalKeyPage';
import BrowserPanel from './pages/BrowserPanel';
import AppDetail from './pages/AppDetail';
import {
  AdminOverviewPage, AdminAnalyticsPage, AdminUsersPage, AdminAgentsPage,
  AdminTransactionsPage, AdminPricingManagerPage, AdminApiKeysPage,
  AdminPaymentSetupPage, AdminSmtpPage, AdminBrandingPage,
  AdminKnowledgeBasePage, AdminAuditLogPage, AdminUniversalGatewayPage,
  AdminGovernancePage
} from "./pages/AdminPages";
import TreasuryAutoPilot from "./pages/TreasuryAutoPilot";
import { Toaster } from "./components/ui/sonner";
import { Watermark } from "./components/Watermark";
import { BrandingProvider } from "./components/BrandingProvider";
import { PreviewModeProvider } from "./components/PreviewModeContext";

// In development, CRA's dev server (setupProxy.js) forwards /api/* to the
// backend — so the browser can talk to the backend as same-origin and Chrome
// never has to deal with cross-origin preflight edge cases. In production,
// REACT_APP_BACKEND_URL is baked into the bundle and used directly.
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL?.trim() || "";
export const API = BACKEND_URL ? `${BACKEND_URL}/api` : "/api";

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

// Google OAuth Callback — reads token from query params set by the backend redirect
const GoogleAuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    const error = params.get("error");

    if (error || !token) {
      navigate("/login?error=" + (error || "oauth_failed"), { replace: true });
      return;
    }

    const userData = {
      user_id: params.get("user_id"),
      email: params.get("email"),
      name: params.get("name"),
      picture: params.get("picture") || null,
      is_admin: params.get("is_admin") === "true",
    };

    login(userData, token);
    navigate("/dashboard", { replace: true });
  }, [location, navigate, login]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-muted-foreground text-sm">Signing you in with Google...</p>
      </div>
    </div>
  );
};

// Legacy Auth Callback Component (Emergent session-based OAuth — kept for backwards compat)
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
      <Route path="/auth/google/callback" element={<GoogleAuthCallback />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/terms" element={<TermsOfService />} />
      <Route path="/changelog" element={<ChangelogPage />} />
      <Route path="/alternatives" element={<AlternativesHub />} />
      <Route path="/alternatives/jasper" element={<AlternativePage config={JASPER} />} />
      <Route path="/alternatives/copy-ai" element={<AlternativePage config={COPY_AI} />} />
      <Route path="/alternatives/cursor" element={<AlternativePage config={CURSOR} />} />
      <Route path="/alternatives/lovable" element={<AlternativePage config={LOVABLE} />} />
      <Route path="/subprocessors" element={<SubprocessorsPage />} />
      <Route path="/blog" element={<BlogListPage />} />
      <Route path="/blog/:slug" element={<BlogPostPage />} />
      <Route path="/payment/success" element={<ProtectedRoute><PaymentSuccess /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout><DashboardHub /></DashboardLayout></ProtectedRoute>} />
      <Route path="/wallet" element={<ProtectedRoute><DashboardLayout><WalletDashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/api-keys" element={<ProtectedRoute><DashboardLayout><ApiKeysPage /></DashboardLayout></ProtectedRoute>} />
      {/* /admin/metrics consolidated into /admin/gateway → Financials tab (Audit 016) */}
      <Route path="/admin/metrics" element={<Navigate to="/admin/gateway" replace />} />
      {/* /admin/packages-manager → redirect to pricing-manager (consolidated UI) */}
      <Route path="/admin/packages-manager" element={<Navigate to="/admin/pricing-manager" replace />} />
      <Route path="/setup" element={<SetupWizard />} />
      <Route path="/chat/:agentId?" element={<ProtectedRoute><DashboardLayout><AgentChat /></DashboardLayout></ProtectedRoute>} />
      <Route path="/agents" element={<ProtectedRoute><DashboardLayout><AgentsHub /></DashboardLayout></ProtectedRoute>} />
      <Route path="/agents/create" element={<Navigate to="/agents?view=create" replace />} />
      <Route path="/products" element={<ProtectedRoute><DashboardLayout><ProductCatalog /></DashboardLayout></ProtectedRoute>} />
      <Route path="/projects/*" element={<ProtectedRoute><DashboardLayout><Projects /></DashboardLayout></ProtectedRoute>} />
      <Route path="/workspace" element={<Navigate to="/memory?view=workspace" replace />} />
      <Route path="/approvals" element={<ProtectedRoute><DashboardLayout><Approvals /></DashboardLayout></ProtectedRoute>} />
      <Route path="/brain-profiles" element={<Navigate to="/memory?view=profiles" replace />} />
      <Route path="/kpi-dashboard" element={<Navigate to="/dashboard?view=kpi" replace />} />
      <Route path="/collaborations" element={<ProtectedRoute><DashboardLayout><CollaborationEngine /></DashboardLayout></ProtectedRoute>} />
      <Route path="/activity-monitor" element={<Navigate to="/admin/governance?view=activity" replace />} />
      <Route path="/vibe-coding" element={<ProtectedRoute><DashboardLayout><VibeCoding /></DashboardLayout></ProtectedRoute>} />
      <Route path="/reference-intelligence" element={<ProtectedRoute><DashboardLayout><ReferenceIntelligence /></DashboardLayout></ProtectedRoute>} />
      <Route path="/content-generator" element={<ProtectedRoute><DashboardLayout><ContentGenerator /></DashboardLayout></ProtectedRoute>} />
      <Route path="/tasks" element={<ProtectedRoute><DashboardLayout><Tasks /></DashboardLayout></ProtectedRoute>} />
      <Route path="/team" element={<ProtectedRoute><DashboardLayout><Team /></DashboardLayout></ProtectedRoute>} />
      <Route path="/insights" element={<ProtectedRoute><DashboardLayout><InsightsPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><DashboardLayout><Settings /></DashboardLayout></ProtectedRoute>} />
      <Route path="/about" element={<ProtectedRoute><DashboardLayout><AboutPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/memory" element={<ProtectedRoute><DashboardLayout><MemoryHub /></DashboardLayout></ProtectedRoute>} />
      <Route path="/kernel" element={<ProtectedRoute><DashboardLayout><KernelDashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/networks" element={<ProtectedRoute><DashboardLayout><AgentNetworks /></DashboardLayout></ProtectedRoute>} />
      <Route path="/task-graphs" element={<ProtectedRoute><DashboardLayout><TaskGraphs /></DashboardLayout></ProtectedRoute>} />
      <Route path="/knowledge-graph" element={<Navigate to="/memory?view=graph" replace />} />
      <Route path="/trust-scores" element={<Navigate to="/admin/governance?view=trust" replace />} />
      <Route path="/execution-gateway" element={<ProtectedRoute><DashboardLayout><ExecutionGateway /></DashboardLayout></ProtectedRoute>} />
      <Route path="/developer" element={<ProtectedRoute><DashboardLayout><DeveloperPortal /></DashboardLayout></ProtectedRoute>} />
      <Route path="/rbac" element={<Navigate to="/admin/governance?view=rbac" replace />} />
      <Route path="/circuit-breakers" element={<Navigate to="/admin/governance?view=circuit" replace />} />
      <Route path="/cost-governance" element={<Navigate to="/admin/governance?view=cost" replace />} />
      <Route path="/workflow-builder" element={<ProtectedRoute><DashboardLayout><WorkflowBuilder /></DashboardLayout></ProtectedRoute>} />
      <Route path="/environments" element={<ProtectedRoute><DashboardLayout><Environments /></DashboardLayout></ProtectedRoute>} />
      <Route path="/memory-hierarchy" element={<Navigate to="/memory?view=hierarchy" replace />} />
      <Route path="/campaigns" element={<ProtectedRoute><DashboardLayout><CampaignBuilder /></DashboardLayout></ProtectedRoute>} />
      <Route path="/integrations" element={<ProtectedRoute><DashboardLayout><IntegrationHub /></DashboardLayout></ProtectedRoute>} />
      <Route path="/integrations/:provider" element={<ProtectedRoute><DashboardLayout><AppDetail /></DashboardLayout></ProtectedRoute>} />
      <Route path="/apps" element={<Navigate to="/integrations" replace />} />
      <Route path="/apps/:provider" element={<RedirectToIntegration />} />
      <Route path="/browser" element={<ProtectedRoute><DashboardLayout><BrowserPanel /></DashboardLayout></ProtectedRoute>} />
      <Route path="/social" element={<Navigate to="/integrations" replace />} />
      <Route path="/universal-key" element={<ProtectedRoute><DashboardLayout><UniversalKeyPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/organization" element={<ProtectedRoute><DashboardLayout><Organization /></DashboardLayout></ProtectedRoute>} />
      <Route path="/analytics" element={<Navigate to="/dashboard?view=analytics" replace />} />
      <Route path="/agent-suggestions" element={<Navigate to="/agents?view=suggestions" replace />} />
      <Route path="/team-builder" element={<ProtectedRoute><DashboardLayout><TeamBuilder /></DashboardLayout></ProtectedRoute>} />
      <Route path="/observability" element={<Navigate to="/dashboard?view=observability" replace />} />
      <Route path="/outcomes" element={<ProtectedRoute><DashboardLayout><OutcomesOverview /></DashboardLayout></ProtectedRoute>} />
      <Route path="/venture-portfolio" element={<ProtectedRoute><DashboardLayout><VenturePortfolio /></DashboardLayout></ProtectedRoute>} />
      <Route path="/commander" element={<ProtectedRoute><DashboardLayout><CommanderOrion /></DashboardLayout></ProtectedRoute>} />
      <Route path="/operator" element={<Navigate to="/admin/governance?view=operator" replace />} />
      <Route path="/agent-catalog" element={<Navigate to="/agents?view=catalog" replace />} />
      <Route path="/admin" element={<AdminRoute><DashboardLayout><AdminOverviewPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/overview" element={<AdminRoute><DashboardLayout><AdminOverviewPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/analytics" element={<AdminRoute><DashboardLayout><AdminAnalyticsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/users" element={<AdminRoute><DashboardLayout><AdminUsersPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/agents" element={<AdminRoute><DashboardLayout><AdminAgentsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/transactions" element={<AdminRoute><DashboardLayout><AdminTransactionsPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/pricing-manager" element={<AdminRoute><DashboardLayout><AdminPricingManagerPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/treasury" element={<AdminRoute><DashboardLayout><TreasuryAutoPilot /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/api-keys" element={<AdminRoute><DashboardLayout><AdminApiKeysPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/payments" element={<AdminRoute><DashboardLayout><AdminPaymentSetupPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/smtp" element={<AdminRoute><DashboardLayout><AdminSmtpPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/branding" element={<AdminRoute><DashboardLayout><AdminBrandingPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/knowledge" element={<AdminRoute><DashboardLayout><AdminKnowledgeBasePage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/audit" element={<AdminRoute><DashboardLayout><AdminAuditLogPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/gateway" element={<AdminRoute><DashboardLayout><AdminUniversalGatewayPage /></DashboardLayout></AdminRoute>} />
      <Route path="/admin/governance" element={<AdminRoute><DashboardLayout><AdminGovernancePage /></DashboardLayout></AdminRoute>} />
      {/* Provider Intelligence is now a tab inside the Universal Gateway
          (see UniversalGatewayTab.jsx — "Intelligence" + "Package Advisor"
          sub-tabs). Old direct URL redirects so nothing bookmarks stale. */}
      <Route path="/admin/provider-intelligence" element={<Navigate to="/admin/gateway?tab=intelligence" replace />} />
      <Route path="/admin/code-explorer" element={<AdminRoute><DashboardLayout><CodeExplorer /></DashboardLayout></AdminRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function RedirectToIntegration() {
  const { pathname } = useLocation();
  const provider = pathname.split("/").pop();
  return <Navigate to={`/integrations/${provider}`} replace />;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BrandingProvider>
          <PreviewModeProvider>
            <AppRouter />
            <Watermark />
            <CookieConsent />
            <ExitIntentPopup />
            <Analytics />
            <Toaster position="top-right" richColors />
          </PreviewModeProvider>
        </BrandingProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
