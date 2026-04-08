import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../App";
import {
  Bot, MessageSquare, ListTodo, Users, Settings, LogOut, Menu, X,
  Shield, BarChart3, Package, Rocket, Brain, FileCheck, Cpu, LayoutDashboard,
  Activity, Gauge, Radio, Code, Palette, PenTool, Info,
  PanelLeftClose, PanelLeftOpen, Search, FileCode, Database,
  Network, GitBranch, Layers, Share2, Zap, Lock, CircuitBoard, DollarSign, Workflow,
  Globe, HardDrive, Megaphone, Plug, Building2, PieChart, Sparkles,
  CreditCard, Key, Mail, Paintbrush, BookOpen, ScrollText, TrendingUp,
  Diamond, Plus, Eye, Crown, UserPlus, Store, Satellite, FlaskConical,
  Lightbulb, Radar, Terminal
} from "lucide-react";
import { useState, useEffect, useCallback, Suspense, useRef } from "react";
import CommandPalette from "../CommandPalette";
import NeuralCommandCanvas from "../3d/NeuralCommandCanvas";
import PreviewModeBanner from "../PreviewModeBanner";
import { usePreviewMode, PREVIEW_PLANS } from "../PreviewModeContext";
import MessengerChat from "../MessengerChat";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── Palette tokens ──────────────────────────────────────────────────────── */
const T = {
  bg:       "#030712",
  sidebar:  "rgba(5,10,20,0.92)",
  teal:     "#4fd1c5",
  violet:   "#7c3aed",
  blue:     "#2563eb",
  border:   "rgba(255,255,255,0.07)",
  border2:  "rgba(255,255,255,0.12)",
};

/* ─── OrgSwitcher ─────────────────────────────────────────────────────────── */
function OrgSwitcher() {
  const { token } = useAuth();
  const [org, setOrg]         = useState(null);
  const [open, setOpen]       = useState(false);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/api/kernel/organizations/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null).then(d => { if (d) setOrg(d); }).catch(() => {});
  }, [token]);

  const createOrg = async () => {
    if (!newName.trim()) return;
    const res = await fetch(`${API}/api/kernel/organizations`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName.trim() }),
    });
    if (res.ok) { const data = await res.json(); setOrg(data); setCreating(false); setNewName(""); }
  };

  return (
    <div className="px-3 pt-1" data-testid="org-switcher">
      <button
        onClick={() => setOpen(!open)}
        style={{ background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, borderRadius: 8 }}
        className="w-full flex items-center gap-2 px-2.5 py-2 text-left transition-colors hover:border-white/10"
      >
        <div style={{ width: 22, height: 22, borderRadius: 6, background: "rgba(79,209,197,0.12)", border: `1px solid rgba(79,209,197,0.2)`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Building2 style={{ width: 11, height: 11, color: T.teal }} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-medium text-zinc-300 truncate">{org?.name || "Personal Workspace"}</p>
          <p className="text-[10px] text-zinc-600">{org ? `${org.members?.length || 1} members` : "No org yet"}</p>
        </div>
        <svg className={`w-3 h-3 text-zinc-600 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div style={{ background: "rgba(5,10,20,0.95)", border: `1px solid ${T.border}`, borderRadius: 8, marginTop: 4, padding: 8 }}>
          {org ? (
            <div className="space-y-1">
              <div style={{ padding: "4px 8px", borderRadius: 5, background: "rgba(79,209,197,0.08)", color: T.teal, fontSize: 11 }}>{org.name}</div>
              <div style={{ fontSize: 9, color: "#475569", padding: "0 8px" }}>ID: {org.org_id?.slice(0, 12)}…</div>
            </div>
          ) : creating ? (
            <div className="space-y-1.5">
              <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Organization name…"
                style={{ width: "100%", background: "rgba(255,255,255,0.05)", border: `1px solid ${T.border2}`, borderRadius: 6, padding: "4px 8px", fontSize: 12, color: "#e2e8f0", outline: "none" }}
                autoFocus onKeyDown={e => e.key === "Enter" && createOrg()} data-testid="org-name-input" />
              <div className="flex gap-1">
                <button onClick={createOrg} style={{ flex: 1, padding: "4px 0", borderRadius: 5, background: T.teal, color: "#030712", fontSize: 11, fontWeight: 700 }} data-testid="create-org-btn">Create</button>
                <button onClick={() => setCreating(false)} style={{ padding: "4px 10px", borderRadius: 5, background: "rgba(255,255,255,0.06)", color: "#94a3b8", fontSize: 11 }}>Cancel</button>
              </div>
            </div>
          ) : (
            <button onClick={() => setCreating(true)} style={{ width: "100%", padding: "6px 8px", borderRadius: 5, color: T.teal, fontSize: 11, textAlign: "left" }}
              className="hover:bg-white/5 transition-colors" data-testid="new-org-btn">
              + Create Organization
            </button>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── LiveSystemStatus ────────────────────────────────────────────────────── */
function LiveSystemStatus({ collapsed }) {
  const { token } = useAuth();
  const [agentCount, setAgentCount] = useState(null);

  useEffect(() => {
    if (!token) return;
    fetch(`${API}/api/agents`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d) setAgentCount(Array.isArray(d) ? d.length : (d.agents?.length ?? 0));
      }).catch(() => {});
  }, [token]);

  if (collapsed) return (
    <div style={{ display: "flex", justifyContent: "center", padding: "3px 0 6px" }}>
      <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", animation: "neural-pulse-green 2.2s ease-in-out infinite" }} />
    </div>
  );

  return (
    <div style={{ padding: "3px 14px 8px", display: "flex", alignItems: "center", gap: 7 }}>
      <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#10b981", flexShrink: 0, animation: "neural-pulse-green 2.2s ease-in-out infinite" }} />
      <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.12em", color: "rgba(16,185,129,0.7)", textTransform: "uppercase" }}>ONLINE</span>
      {agentCount !== null && (
        <span style={{ fontSize: 9, color: "#475569", marginLeft: "auto" }}>
          {agentCount} agent{agentCount !== 1 ? "s" : ""}
        </span>
      )}
      <div className="waveform" style={{ height: 14, marginLeft: agentCount !== null ? 0 : "auto" }}>
        <span /><span /><span /><span /><span />
      </div>
    </div>
  );
}

/* ─── SidebarCredits ──────────────────────────────────────────────────────── */
function SidebarCredits({ collapsed }) {
  const { token } = useAuth();
  const { previewMode, previewPlan } = usePreviewMode();
  const [credits, setCredits]   = useState(null);
  const [planName, setPlanName] = useState("Free");
  const [isOwner, setIsOwner]   = useState(false);
  const navigate = useNavigate();

  const fetchCredits = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/subscription`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const d = await res.json();
        setCredits(d.credits ?? 0);
        setPlanName(d.plan_info?.name ?? "Free");
        setIsOwner(!!d.is_owner);
      }
    } catch {}
  }, [token]);

  useEffect(() => { fetchCredits(); const iv = setInterval(fetchCredits, 30000); return () => clearInterval(iv); }, [fetchCredits]);

  const planInfo     = previewMode && PREVIEW_PLANS[previewPlan] ? PREVIEW_PLANS[previewPlan] : null;
  const showOwner    = isOwner && !previewMode;

  if (collapsed) {
    return (
      <div className="px-2 pt-2">
        <button onClick={() => navigate(showOwner ? "/admin/overview" : "/pricing")}
          title={showOwner ? "Owner — Unlimited" : credits !== null ? `${credits.toFixed(0)} credits` : "Credits"}
          style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", padding: "8px 0", borderRadius: 8, background: showOwner ? "rgba(167,139,250,0.1)" : "rgba(79,209,197,0.08)", border: `1px solid ${showOwner ? "rgba(167,139,250,0.2)" : "rgba(79,209,197,0.15)"}` }}
          data-testid="sidebar-credits-btn">
          {showOwner ? <Crown style={{ width: 16, height: 16, color: "#a78bfa" }} /> : <Diamond style={{ width: 16, height: 16, color: T.teal }} />}
        </button>
      </div>
    );
  }

  // Owner
  if (showOwner) return (
    <div className="px-3 pt-2" data-testid="sidebar-credits">
      <div style={{ borderRadius: 10, background: "rgba(167,139,250,0.07)", border: "1px solid rgba(167,139,250,0.18)", padding: "10px 12px" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5"><Crown style={{ width: 13, height: 13, color: "#a78bfa" }} /><span style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa" }}>Unlimited</span></div>
          <span style={{ fontSize: 9, fontWeight: 700, color: "#a78bfa", background: "rgba(167,139,250,0.15)", padding: "2px 6px", borderRadius: 20 }}>Owner</span>
        </div>
        <p style={{ fontSize: 10, color: "#475569", marginTop: 3 }}>No credit limits apply</p>
      </div>
    </div>
  );

  // Preview
  if (previewMode && planInfo) return (
    <div className="px-3 pt-2" data-testid="sidebar-credits">
      <div style={{ borderRadius: 10, background: "rgba(251,191,36,0.07)", border: "1px solid rgba(251,191,36,0.2)", padding: "10px 12px" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5"><Eye style={{ width: 13, height: 13, color: "#f59e0b" }} /><span style={{ fontSize: 12, fontWeight: 700, color: "#f59e0b" }}>{planInfo.credits.toLocaleString()}</span></div>
          <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded ${planInfo.bg} ${planInfo.color}`}>{planInfo.label}</span>
        </div>
        <p style={{ fontSize: 10, color: "#f59e0b", marginTop: 3 }}>Preview mode</p>
      </div>
    </div>
  );

  // Standard
  return (
    <div className="px-3 pt-2" data-testid="sidebar-credits">
      <div style={{ borderRadius: 10, background: "rgba(79,209,197,0.05)", border: "1px solid rgba(79,209,197,0.12)", padding: "10px 12px" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5"><Diamond style={{ width: 13, height: 13, color: T.teal }} /><span style={{ fontSize: 12, fontWeight: 700, color: T.teal, fontVariantNumeric: "tabular-nums" }}>{credits !== null ? credits.toFixed(2) : "…"}</span></div>
          <span style={{ fontSize: 9, color: "#a78bfa", background: "rgba(124,58,237,0.12)", padding: "2px 6px", borderRadius: 20, fontWeight: 600 }}>{planName}</span>
        </div>
        <button onClick={() => navigate("/pricing")}
          style={{ marginTop: 8, width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 5, padding: "5px 0", borderRadius: 7, background: "rgba(79,209,197,0.10)", color: T.teal, fontSize: 11, fontWeight: 600, border: "none", cursor: "pointer", transition: "background 0.2s" }}
          onMouseEnter={e => e.target.style.background = "rgba(79,209,197,0.18)"}
          onMouseLeave={e => e.target.style.background = "rgba(79,209,197,0.10)"}
          data-testid="sidebar-buy-credits-btn">
          <Plus style={{ width: 11, height: 11 }} /> Buy Credits
        </button>
      </div>
    </div>
  );
}

/* ─── Nav sections ────────────────────────────────────────────────────────── */
const navSections = [
  { label: null, items: [
    { icon: LayoutDashboard, label: "Dashboard", to: "/dashboard" },
  ]},
  { label: "Workspace", items: [
    { icon: Rocket,       label: "Projects",   to: "/projects"  },
    { icon: MessageSquare,label: "Chat",        to: "/chat"      },
    { icon: ListTodo,     label: "Tasks",       to: "/tasks"     },
    { icon: FileCheck,    label: "Approvals",   to: "/approvals" },
  ]},
  { label: "AI Tools", items: [
    { icon: Bot,       label: "Agents",             to: "/agents"               },
    { icon: UserPlus,  label: "Team Builder",        to: "/team-builder"         },
    { icon: Brain,     label: "Workspace Brain",     to: "/workspace"            },
    { icon: Cpu,       label: "Brain Profiles",      to: "/brain-profiles"       },
    { icon: Code,      label: "Vibe Coding",         to: "/vibe-coding"          },
    { icon: Lightbulb, label: "Reference Intel",     to: "/reference-intelligence"},
    { icon: PenTool,   label: "Content Generator",   to: "/content-generator"    },
  ]},
  { label: "Intelligence", items: [
    { icon: Layers,    label: "Kernel",           to: "/kernel"           },
    { icon: Network,   label: "Agent Networks",   to: "/networks"         },
    { icon: GitBranch, label: "Task Graphs",      to: "/task-graphs"      },
    { icon: Share2,    label: "Knowledge Graph",  to: "/knowledge-graph"  },
    { icon: Shield,    label: "Trust Scores",     to: "/trust-scores"     },
    { icon: Zap,       label: "Execution Gateway",to: "/execution-gateway"},
    { icon: Workflow,  label: "Workflow Builder", to: "/workflow-builder" },
    { icon: Megaphone, label: "Campaign Builder", to: "/campaigns"        },
    { icon: Plug,      label: "Integrations",     to: "/integrations"     },
    { icon: Satellite, label: "Social Media",     to: "/social"           },
    { icon: Key,       label: "Universal Key",    to: "/universal-key"    },
    { icon: PieChart,  label: "Analytics",        to: "/analytics"        },
    { icon: Sparkles,  label: "Agent Suggestions",to: "/agent-suggestions"},
    { icon: Globe,     label: "Environments",     to: "/environments"     },
    { icon: HardDrive, label: "Memory Hierarchy", to: "/memory-hierarchy" },
    { icon: Database,  label: "Memory",           to: "/memory"           },
    { icon: Activity,  label: "Collaborations",   to: "/collaborations"   },
    { icon: Gauge,     label: "KPI Dashboard",    to: "/kpi-dashboard"    },
    { icon: Radio,     label: "Activity Monitor", to: "/activity-monitor" },
    { icon: BarChart3, label: "My Insights",      to: "/insights"         },
  ]},
  { label: "MAARS Infinity", items: [
    { icon: Terminal,   label: "Developer API",     to: "/developer"         },
    { icon: Radar,      label: "Observability",     to: "/observability"     },
    { icon: FlaskConical,label:"Model Router",      to: "/model-router"      },
    { icon: Satellite,  label: "Commander Orion",   to: "/commander"         },
    { icon: TrendingUp, label: "Venture Portfolio", to: "/venture-portfolio" },
    { icon: Shield,     label: "Operator Panel",    to: "/operator"          },
    { icon: Store,      label: "Agent Catalog",     to: "/agent-catalog"     },
  ]},
  { label: "Manage", items: [
    { icon: Package,   label: "Products",     to: "/products"      },
    { icon: Users,     label: "Team",         to: "/team"          },
    { icon: Building2, label: "Organization", to: "/organization"  },
    { icon: Settings,  label: "Settings",     to: "/settings"      },
    { icon: Info,      label: "About",        to: "/about"         },
  ]},
];

/* ─── DashboardLayout ─────────────────────────────────────────────────────── */
const DashboardLayout = ({ children }) => {
  const navigate  = useNavigate();
  const location  = useLocation();
  const { user, logout } = useAuth();
  const { previewMode, isRouteVisibleToClient, enterPreview } = usePreviewMode();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [cmdOpen,    setCmdOpen]    = useState(false);
  const scrollY = useRef(0);
  const mainRef = useRef(null);
  const [collapsed, setCollapsed]   = useState(() => {
    try { return localStorage.getItem("maars_sidebar_collapsed") === "true"; } catch { return false; }
  });

  useEffect(() => {
    try { localStorage.setItem("maars_sidebar_collapsed", String(collapsed)); } catch {}
  }, [collapsed]);

  useEffect(() => {
    const handler = (e) => {
      const tag = e.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || e.target.isContentEditable) return;
      if (e.key === "/" && !e.metaKey && !e.ctrlKey) { e.preventDefault(); setCmdOpen(true); }
      if ((e.metaKey || e.ctrlKey) && e.key === "k")  { e.preventDefault(); setCmdOpen(true); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Global 3D tilt event delegation — handles ALL [data-3d] elements system-wide
  useEffect(() => {
    const onMove = (e) => {
      const card = e.target.closest("[data-3d]");
      if (!card) return;
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width  - 0.5) * 2;
      const y = ((e.clientY - rect.top)  / rect.height - 0.5) * 2;
      const s = parseFloat(card.getAttribute("data-3d-strength") || "10");
      const l = parseFloat(card.getAttribute("data-3d-lift") || "6");
      card.style.transform = `perspective(1200px) rotateX(${-y * s}deg) rotateY(${x * s}deg) translateZ(${l}px) scale(1.02)`;
      card.style.transition = "transform 0.06s ease-out";
      card.style.setProperty("--shimmer-x", `${(x + 1) / 2 * 100}%`);
      card.style.setProperty("--shimmer-y", `${(y + 1) / 2 * 100}%`);
      card.style.zIndex = "20";
    };
    const onOut = (e) => {
      const card = e.target.closest("[data-3d]");
      if (!card || card.contains(e.relatedTarget)) return;
      card.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px) scale(1)";
      card.style.transition = "transform 0.5s cubic-bezier(0.22,1,0.36,1)";
      card.style.zIndex = "";
    };
    const onScroll = (e) => { scrollY.current = e.target.scrollTop || window.scrollY; };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseout", onOut);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseout", onOut);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  const handleLogout = async () => { await logout(); navigate("/"); };

  const sidebarPx = collapsed ? 68 : 224;
  const isActive  = (to) => location.pathname === to || (to !== "/dashboard" && location.pathname.startsWith(to));

  /* ── NavItem ──────────────────────────────────────── */
  const NavItem = ({ icon: Icon, label, to, onClick }) => {
    const active = isActive(to);
    return (
      <button
        onClick={onClick || (() => navigate(to))}
        title={collapsed ? label : undefined}
        data-testid={`nav-${label.toLowerCase().replace(/\s+/g, "-")}`}
        style={{
          width: "100%", display: "flex", alignItems: "center",
          justifyContent: collapsed ? "center" : "flex-start",
          gap: 9, padding: collapsed ? "8px 0" : "7px 10px",
          borderRadius: 8, fontSize: 13, fontWeight: active ? 600 : 400,
          position: "relative", border: "none", cursor: "pointer",
          transition: "all 0.18s",
          background: active
            ? "linear-gradient(90deg, rgba(79,209,197,0.13) 0%, rgba(79,209,197,0.05) 100%)"
            : "transparent",
          color: active ? T.teal : "#64748b",
          boxShadow: active ? "inset 0 0 0 1px rgba(79,209,197,0.12)" : "none",
        }}
        onMouseEnter={e => { if (!active) { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.color = "#cbd5e1"; } }}
        onMouseLeave={e => { if (!active) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#64748b"; } }}
      >
        {active && (
          <span style={{
            position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)",
            width: 3, height: 22, borderRadius: "0 3px 3px 0",
            background: `linear-gradient(180deg, ${T.teal}, ${T.blue})`,
            boxShadow: `0 0 8px ${T.teal}88, 0 0 16px ${T.teal}44`,
          }} />
        )}
        <Icon style={{
          width: 15, height: 15, flexShrink: 0,
          color: active ? T.teal : "inherit",
          filter: active ? `drop-shadow(0 0 4px ${T.teal}88)` : "none",
        }} />
        {!collapsed && <span className="truncate">{label}</span>}
        {active && !collapsed && (
          <span style={{
            marginLeft: "auto", width: 4, height: 4, borderRadius: "50%",
            background: T.teal, flexShrink: 0,
            boxShadow: `0 0 6px ${T.teal}`,
          }} />
        )}
      </button>
    );
  };

  /* ── Section divider ──────────────────────────────── */
  const SectionDivider = ({ label }) => {
    if (collapsed) return <div style={{ height: 1, background: `linear-gradient(90deg, transparent, rgba(79,209,197,0.25), transparent)`, margin: "8px 6px" }} />;
    return (
      <div style={{ padding: "14px 10px 5px", display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ width: 16, height: 1, background: `linear-gradient(90deg, rgba(79,209,197,0.5), rgba(124,58,237,0.3))`, flexShrink: 0, animation: "border-teal-pulse 3s ease-in-out infinite" }} />
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: "rgba(79,209,197,0.55)", whiteSpace: "nowrap" }}>{label}</span>
        <span style={{ flex: 1, height: 1, background: `linear-gradient(90deg, rgba(79,209,197,0.1), transparent)` }} />
      </div>
    );
  };

  /* ── Render nav ───────────────────────────────────── */
  const renderNav = (closeMobile) => (
    <>
      {navSections.map((section, si) => {
        const visibleItems = (user?.is_admin && !previewMode)
          ? section.items
          : section.items.filter(item => isRouteVisibleToClient(item.to));
        if (visibleItems.length === 0 && section.label) return null;
        return (
          <div key={si}>
            {section.label && <SectionDivider label={section.label} />}
            {visibleItems.map(item => (
              <NavItem key={item.to} icon={item.icon} label={item.label} to={item.to}
                onClick={closeMobile ? () => { navigate(item.to); closeMobile(); } : undefined} />
            ))}
          </div>
        );
      })}

      {/* Admin section */}
      {user?.is_admin && !previewMode && (
        <>
          <SectionDivider label="Admin" />
          {[
            { icon: Activity,    label: "Overview",          to: "/admin/overview"        },
            { icon: BarChart3,   label: "Analytics",         to: "/admin/analytics"       },
            { icon: Globe,       label: "Universal Gateway", to: "/admin/gateway"         },
            { icon: Users,       label: "Users",             to: "/admin/users"           },
            { icon: Bot,         label: "Agents",            to: "/admin/agents"          },
            { icon: DollarSign,  label: "Transactions",      to: "/admin/transactions"    },
            { icon: TrendingUp,  label: "Pricing",           to: "/admin/pricing-manager" },
            { icon: Key,         label: "API Keys",          to: "/admin/api-keys"        },
            { icon: CreditCard,  label: "Payment Setup",     to: "/admin/payments"        },
            { icon: Mail,        label: "Email (SMTP)",      to: "/admin/smtp"            },
            { icon: Paintbrush,  label: "Branding",          to: "/admin/branding"        },
            { icon: BookOpen,    label: "Knowledge Base",    to: "/admin/knowledge"       },
            { icon: ScrollText,  label: "Audit Log",         to: "/admin/audit"           },
            { icon: FileCode,    label: "Code Explorer",     to: "/admin/code-explorer"   },
            { icon: Lock,        label: "Access Control",    to: "/rbac"                  },
            { icon: CircuitBoard,label: "Circuit Breakers",  to: "/circuit-breakers"      },
            { icon: Gauge,       label: "Cost Governance",   to: "/cost-governance"       },
          ].map(item => (
            <NavItem key={item.to} icon={item.icon} label={item.label} to={item.to}
              onClick={closeMobile ? () => { navigate(item.to); closeMobile(); } : undefined} />
          ))}

          {!collapsed && (
            <button onClick={() => enterPreview("free")}
              style={{ width: "100%", display: "flex", alignItems: "center", gap: 8, padding: "7px 10px", borderRadius: 8, fontSize: 12, color: "#f59e0b", border: "1px solid transparent", background: "transparent", cursor: "pointer", marginTop: 4, transition: "all 0.15s" }}
              onMouseEnter={e => { e.currentTarget.style.background = "rgba(245,158,11,0.08)"; e.currentTarget.style.borderColor = "rgba(245,158,11,0.2)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "transparent"; }}
              data-testid="preview-client-view-btn">
              <Eye style={{ width: 14, height: 14 }} />
              <span>Preview Client View</span>
            </button>
          )}
        </>
      )}
    </>
  );

  /* ── Sidebar inner content ───────────────────────── */
  const SidebarContent = ({ closeMobile }) => (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", position: "relative" }}>
      {/* Dot grid ambient texture */}
      <div className="dot-grid" style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.55 }} />

      {/* Animated ambient glow at top */}
      <div style={{ position: "absolute", top: -20, left: "50%", transform: "translateX(-50%)", width: 160, height: 100, background: `radial-gradient(ellipse, rgba(79,209,197,0.1) 0%, transparent 70%)`, pointerEvents: "none", animation: "holo 8s ease infinite", backgroundSize: "200% 200%" }} />

      {/* Animated right-edge glow border */}
      <div style={{ position: "absolute", top: "10%", right: 0, bottom: "10%", width: 1, background: `linear-gradient(180deg, transparent, rgba(79,209,197,0.4), rgba(124,58,237,0.3), rgba(79,209,197,0.2), transparent)`, backgroundSize: "100% 300%", animation: "holo 10s ease infinite", pointerEvents: "none", borderRadius: 1 }} />

      {/* Logo */}
      <div style={{ height: 56, display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", padding: collapsed ? "0" : "0 16px", gap: 10, borderBottom: `1px solid ${T.border}`, flexShrink: 0, position: "relative" }}>
        <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", minWidth: 0 }}>
          <img src="/branding/maars-logo.jpeg" alt="MAARS"
            style={{ width: collapsed ? 32 : 34, height: collapsed ? 32 : 34, borderRadius: 10, objectFit: "cover", flexShrink: 0, boxShadow: `0 0 18px rgba(79,209,197,0.3), 0 0 6px rgba(79,209,197,0.15)`, border: `1px solid rgba(79,209,197,0.25)`, animation: "neural-pulse 4s ease-in-out infinite" }} />
          {!collapsed && (
            <div style={{ minWidth: 0 }}>
              <h1 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: 13, fontFamily: "Outfit, sans-serif", lineHeight: 1.2, whiteSpace: "nowrap" }}>MAARS Command</h1>
              <p style={{ fontSize: 9, color: "#475569", lineHeight: 1, marginTop: 2 }}>by MAARS Global Corporation</p>
            </div>
          )}
        </Link>
      </div>

      {/* Live system status */}
      <LiveSystemStatus collapsed={collapsed} />

      {/* Credits */}
      <SidebarCredits collapsed={collapsed} />

      {/* Org switcher */}
      {!collapsed && <OrgSwitcher />}

      {/* Search */}
      <div style={{ padding: "8px 12px 4px" }}>
        <button onClick={() => setCmdOpen(true)}
          title={collapsed ? "Search (/)" : undefined}
          style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 8, padding: collapsed ? "8px 0" : "7px 10px", borderRadius: 8, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, color: "#475569", fontSize: 12, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; e.currentTarget.style.color = "#64748b"; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = "#475569"; }}
          data-testid="sidebar-search-btn">
          <Search style={{ width: 13, height: 13, flexShrink: 0 }} />
          {!collapsed && (
            <>
              <span style={{ flex: 1, textAlign: "left" }}>Search…</span>
              <kbd style={{ fontSize: 9, padding: "2px 5px", borderRadius: 4, background: "rgba(255,255,255,0.05)", border: `1px solid ${T.border}`, color: "#475569", fontFamily: "monospace" }}>/</kbd>
            </>
          )}
        </button>
      </div>

      {/* Nav scroll area */}
      <nav style={{ flex: 1, overflowY: "auto", overflowX: "hidden", padding: "4px 8px 8px" }}
        className="scrollbar-thin" data-testid="sidebar-nav">
        {renderNav(closeMobile || null)}
      </nav>

      {/* Collapse toggle */}
      <div style={{ padding: "8px 8px 4px", borderTop: `1px solid ${T.border}` }}>
        <button onClick={() => setCollapsed(c => !c)}
          style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "7px 0", borderRadius: 8, fontSize: 11, color: "#475569", background: "transparent", border: "none", cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.color = "#94a3b8"; }}
          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#475569"; }}
          data-testid="sidebar-collapse-btn">
          {collapsed ? <PanelLeftOpen style={{ width: 15, height: 15 }} /> : <><PanelLeftClose style={{ width: 15, height: 15 }} /><span>Collapse</span></>}
        </button>
      </div>

      {/* User + logout */}
      <div style={{ padding: "4px 8px 10px", borderTop: `1px solid ${T.border}`, position: "relative" }}>
        {/* Alive top-border glow line */}
        <div style={{ position: "absolute", top: -1, left: "10%", right: "10%", height: 1, background: "linear-gradient(90deg, transparent, rgba(79,209,197,0.35), rgba(124,58,237,0.25), rgba(79,209,197,0.35), transparent)", backgroundSize: "200% 100%", animation: "holo 6s ease infinite" }} />

        {!collapsed && (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px 6px" }}>
              {/* Avatar with alive ring */}
              <div style={{ position: "relative", flexShrink: 0 }}>
                <div style={{ width: 30, height: 30, borderRadius: "50%", background: `linear-gradient(135deg, ${T.teal}, ${T.violet})`, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden", border: "1.5px solid rgba(79,209,197,0.25)", boxShadow: "0 0 8px rgba(79,209,197,0.15)" }} className="maars-breathe">
                  {user?.picture
                    ? <img src={user.picture} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    : <span style={{ color: "#030712", fontSize: 12, fontWeight: 700 }}>{user?.name?.charAt(0) || "U"}</span>
                  }
                </div>
                {/* Online dot */}
                <div className="badge-online" style={{ position: "absolute", bottom: 0, right: 0, width: 8, height: 8, borderRadius: "50%", background: "#34d399", border: "1.5px solid rgba(5,10,20,0.9)" }} />
              </div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: "#cbd5e1", lineHeight: 1.2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user?.name}</p>
                <p style={{ fontSize: 10, color: "#475569", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user?.email}</p>
              </div>
            </div>
            {/* Version indicator */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "3px 10px 5px" }}>
              <span className="live-badge">LIVE</span>
              <span className="data-flow-text" style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.08em" }}>MAARS v2.0</span>
              <div style={{ display: "flex", gap: 3, alignItems: "center" }}>
                <span className="maars-typing-dot-1" style={{ width: 3, height: 3, borderRadius: "50%", background: "rgba(79,209,197,0.5)", display: "inline-block" }} />
                <span className="maars-typing-dot-2" style={{ width: 3, height: 3, borderRadius: "50%", background: "rgba(124,58,237,0.5)", display: "inline-block" }} />
                <span className="maars-typing-dot-3" style={{ width: 3, height: 3, borderRadius: "50%", background: "rgba(96,165,250,0.5)", display: "inline-block" }} />
              </div>
            </div>
          </>
        )}
        <button onClick={handleLogout} title={collapsed ? "Log Out" : undefined}
          style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 8, padding: collapsed ? "8px 0" : "7px 10px", borderRadius: 8, fontSize: 12, color: "#475569", background: "transparent", border: "none", cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.background = "rgba(239,68,68,0.08)"; e.currentTarget.style.color = "#f87171"; }}
          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#475569"; }}
          data-testid="nav-logout">
          <LogOut style={{ width: 15, height: 15, flexShrink: 0 }} />
          {!collapsed && <span>Log Out</span>}
        </button>
      </div>
    </div>
  );

  /* ── Render ───────────────────────────────────────── */
  return (
    <div style={{ minHeight: "100vh", background: T.bg }} className={previewMode ? "pt-9" : ""} data-testid="dashboard-layout">
      <style>{`
        /* ── Global 3D system ───────────────────────────────── */
        [data-3d] {
          position: relative;
          transform-style: preserve-3d;
          will-change: transform;
          cursor: default;
        }
        [data-3d]::after {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: inherit;
          background: radial-gradient(circle at var(--shimmer-x,50%) var(--shimmer-y,50%), rgba(255,255,255,0.05) 0%, transparent 55%);
          pointer-events: none;
          z-index: 1000;
          opacity: 0;
          transition: opacity 0.1s;
        }
        [data-3d]:hover::after { opacity: 1; }

        /* Depth shadow that intensifies on hover */
        [data-3d] { box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        [data-3d]:hover { box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(79,209,197,0.06); }

        /* 3D floating labels */
        .label-3d {
          transform: translateZ(12px);
          transform-style: preserve-3d;
        }

        /* Sidebar nav items get subtle 3D lift */
        .nav-item-3d { transition: transform 0.2s cubic-bezier(0.22,1,0.36,1); }
        .nav-item-3d:hover { transform: translateX(4px) perspective(400px) rotateY(-3deg); }

        /* 3D perspective container for main content */
        .scene-3d { perspective: 2400px; perspective-origin: 50% 40%; }

        /* Glowing depth rings */
        .depth-ring::before {
          content: '';
          position: absolute;
          inset: -1px;
          border-radius: inherit;
          background: linear-gradient(135deg, rgba(79,209,197,0.15), rgba(124,58,237,0.08), rgba(37,99,235,0.1));
          z-index: -1;
          opacity: 0;
          transition: opacity 0.3s;
        }
        .depth-ring:hover::before { opacity: 1; }

        /* Floating animation for depth elements */
        @keyframes depth-float {
          0%,100% { transform: translateZ(0px) translateY(0px); }
          50%      { transform: translateZ(8px) translateY(-3px); }
        }
        .depth-float { animation: depth-float 4s ease-in-out infinite; }

        /* Existing animations */
        @keyframes holo { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>

      {/* ── Three.js Neural Background — persistent across ALL pages ── */}
      <div style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none", opacity: 0.18 }}>
        <Suspense fallback={null}>
          <NeuralCommandCanvas scrollY={scrollY} />
        </Suspense>
      </div>

      {/* Ambient depth vignette */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 1, pointerEvents: "none",
        background: "radial-gradient(ellipse at 20% 50%, rgba(79,209,197,0.03) 0%, transparent 55%), radial-gradient(ellipse at 80% 30%, rgba(124,58,237,0.025) 0%, transparent 50%), radial-gradient(ellipse at 50% 100%, rgba(0,0,0,0.4) 0%, transparent 60%)",
      }} />

      <PreviewModeBanner />

      {/* Mobile header */}
      <div className={`flex lg:hidden fixed ${previewMode ? "top-9" : "top-0"} left-0 right-0 no-print items-center`}
        style={{ height: 56, background: "rgba(5,10,20,0.92)", backdropFilter: "blur(24px)", borderBottom: "1px solid rgba(79,209,197,0.1)", zIndex: 40, padding: "0 16px", gap: 12 }}>
        <button onClick={() => setMobileOpen(!mobileOpen)}
          style={{ padding: 8, borderRadius: 8, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#64748b", cursor: "pointer" }}
          data-testid="mobile-sidebar-toggle">
          {mobileOpen ? <X style={{ width: 18, height: 18 }} /> : <Menu style={{ width: 18, height: 18 }} />}
        </button>
        <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none" }}>
          <img src="/branding/maars-logo.jpeg" alt="MAARS" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover" }} />
          <span style={{ color: "#f1f5f9", fontWeight: 700, fontFamily: "Outfit, sans-serif", fontSize: 14 }}>MAARS Command</span>
        </Link>
        <button onClick={() => setCmdOpen(true)}
          style={{ marginLeft: "auto", padding: 8, borderRadius: 8, background: "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: "#64748b", cursor: "pointer" }}
          data-testid="mobile-search-btn">
          <Search style={{ width: 16, height: 16 }} />
        </button>
      </div>

      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex flex-col fixed no-print ${previewMode ? "top-9 bottom-0" : "inset-y-0"} left-0 neural-bg`}
        style={{ width: sidebarPx, background: T.sidebar, backdropFilter: "blur(32px)", borderRight: "1px solid rgba(79,209,197,0.1)", zIndex: 30, transition: "width 0.2s", overflow: "hidden" }}>
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      {mobileOpen && (
        <>
          <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", backdropFilter: "blur(6px)", zIndex: 40 }} className="lg:hidden" onClick={() => setMobileOpen(false)} />
          <aside style={{ position: "fixed", inset: "0 auto 0 0", width: 224, background: "rgba(5,10,20,0.98)", backdropFilter: "blur(24px)", borderRight: `1px solid ${T.border}`, zIndex: 50 }} className="lg:hidden">
            <SidebarContent closeMobile={() => setMobileOpen(false)} />
          </aside>
        </>
      )}

      {/* Main content — wrapped in 3D scene perspective */}
      <div
        ref={mainRef}
        className={`scene-3d ${collapsed ? "lg:ml-[68px]" : "lg:ml-56"} pt-14 lg:pt-0 transition-[margin-left] duration-200 min-h-screen`}
        style={{ position: "relative", zIndex: 2 }}
      >
        {location.pathname.startsWith("/chat") ? (
          children
        ) : (
          <div className="p-4 md:p-5 lg:p-6 xl:p-8 max-w-7xl mx-auto">
            {children}
          </div>
        )}
      </div>

      <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
      <MessengerChat />
    </div>
  );
};

export default DashboardLayout;
