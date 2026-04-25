/**
 * ClientVisibilityTab — lets the admin control which pages/sections
 * are visible to client users, and preview any subscription tier.
 */
import { useState } from "react";
import { Eye, EyeOff, Play, CheckCircle, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Badge } from "../../ui/badge";
import { usePreviewMode, PREVIEW_PLANS } from "../../PreviewModeContext";
import { toast } from "sonner";

// Mirror of the navSections in DashboardLayout — must stay in sync.
const ALL_NAV_SECTIONS = [
  {
    label: "Workspace",
    items: [
      { label: "Projects",  to: "/projects" },
      { label: "Chat",      to: "/chat" },
      { label: "Tasks",     to: "/tasks" },
      { label: "Approvals", to: "/approvals" },
    ],
  },
  {
    label: "AI Tools",
    items: [
      { label: "Agents",            to: "/agents" },
      { label: "Team Builder",      to: "/team-builder" },
      { label: "Workspace Brain",   to: "/workspace" },
      { label: "Brain Profiles",    to: "/brain-profiles" },
      { label: "Vibe Coding",       to: "/vibe-coding" },
      { label: "Reference Intel",   to: "/reference-intelligence" },
      { label: "Content Generator", to: "/content-generator" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { label: "Kernel",            to: "/kernel" },
      { label: "Agent Networks",    to: "/networks" },
      { label: "Task Graphs",       to: "/task-graphs" },
      { label: "Knowledge Graph",   to: "/knowledge-graph" },
      { label: "Trust Scores",      to: "/trust-scores" },
      { label: "Execution Gateway", to: "/execution-gateway" },
      { label: "Workflow Builder",  to: "/workflow-builder" },
      { label: "Campaign Builder",  to: "/campaigns" },
      { label: "Integrations",      to: "/integrations" },
      { label: "Analytics",         to: "/analytics" },
      { label: "Agent Suggestions", to: "/agent-suggestions" },
      { label: "Environments",      to: "/environments" },
      { label: "Memory Hierarchy",  to: "/memory-hierarchy" },
      { label: "Memory",            to: "/memory" },
      { label: "Collaborations",    to: "/collaborations" },
      { label: "KPI Dashboard",     to: "/kpi-dashboard" },
      { label: "Activity Monitor",  to: "/activity-monitor" },
      { label: "My Insights",       to: "/insights" },
    ],
  },
  {
    label: "MAARS Infinity",
    items: [
      { label: "Observability",      to: "/observability" },
      { label: "Commander Orion",    to: "/commander" },
      { label: "Venture Portfolio",  to: "/venture-portfolio" },
      { label: "Operator Panel",     to: "/operator" },
      { label: "Agent Catalog",      to: "/agent-catalog" },
    ],
  },
  {
    label: "Manage",
    items: [
      { label: "Products",      to: "/products" },
      { label: "Team",          to: "/team" },
      { label: "Organization",  to: "/organization" },
      { label: "Settings",      to: "/settings" },
      { label: "About",         to: "/about" },
    ],
  },
];

export function ClientVisibilityTab() {
  const {
    navVisibility,
    isRouteVisibleToClient,
    toggleNavItem,
    enterPreview,
    previewMode,
    previewPlan,
    exitPreview,
    switchPreviewPlan,
  } = usePreviewMode();

  const [saving, setSaving] = useState(false);

  const handleToggle = async (route) => {
    setSaving(true);
    toggleNavItem(route);
    setTimeout(() => setSaving(false), 400);
  };

  const hiddenCount = Object.values(navVisibility).filter(v => v === false).length;
  const totalItems = ALL_NAV_SECTIONS.reduce((sum, s) => sum + s.items.length, 0);

  return (
    <div className="space-y-6" data-testid="client-visibility-tab">

      {/* Header info */}
      <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/15 flex items-start gap-3">
        <Info className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-indigo-300 text-sm font-medium">Client Visibility Control</p>
          <p className="text-zinc-500 text-xs mt-0.5">
            Toggle which pages appear in the sidebar for regular subscribers. As Owner, you always see everything.
            Changes save instantly.
          </p>
          {hiddenCount > 0 && (
            <p className="text-amber-400 text-xs mt-1 font-medium">
              {hiddenCount} page{hiddenCount !== 1 ? "s" : ""} currently hidden from clients
            </p>
          )}
        </div>
      </div>

      {/* Preview mode launcher */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader className="pb-3">
          <CardTitle className="text-white font-['Outfit'] flex items-center gap-3 text-base">
            <div className="w-9 h-9 rounded-lg bg-amber-500/15 flex items-center justify-center">
              <Eye className="w-4 h-4 text-amber-400" />
            </div>
            Preview as Client
          </CardTitle>
          <p className="text-zinc-500 text-sm">
            Enter a read-only simulation of exactly what a subscriber sees — their sidebar, their plan limits.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {Object.entries(PREVIEW_PLANS).map(([key, plan]) => {
              const isActive = previewMode && previewPlan === key;
              return (
                <button
                  key={key}
                  onClick={() => previewMode ? switchPreviewPlan(key) : enterPreview(key)}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all ${
                    isActive
                      ? `border-amber-500/60 bg-amber-500/10`
                      : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                  }`}
                >
                  <span className={`text-[13px] font-bold ${plan.color}`}>{plan.label}</span>
                  <span className="text-[10px] text-zinc-600">{plan.credits.toLocaleString()} credits</span>
                  <span className="text-[10px] text-zinc-600">{plan.max_agents} agents</span>
                  {isActive && (
                    <Badge className="text-[9px] bg-amber-500/20 text-amber-400 mt-0.5">Active</Badge>
                  )}
                </button>
              );
            })}
          </div>

          {previewMode ? (
            <button
              onClick={exitPreview}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-400 text-sm font-semibold transition-colors border border-amber-500/20"
            >
              <EyeOff className="w-4 h-4" />
              Exit Preview Mode
            </button>
          ) : (
            <button
              onClick={() => enterPreview("free")}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white text-sm font-semibold transition-all"
            >
              <Play className="w-4 h-4" />
              Enter Client Preview
            </button>
          )}
        </CardContent>
      </Card>

      {/* Visibility toggles per section */}
      {ALL_NAV_SECTIONS.map((section) => {
        const allVisible = section.items.every(item => isRouteVisibleToClient(item.to));
        const allHidden = section.items.every(item => !isRouteVisibleToClient(item.to));

        return (
          <Card key={section.label} className="bg-zinc-900/50 border-white/10">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white font-['Outfit'] text-sm font-semibold">
                  {section.label}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600">
                    {section.items.filter(i => isRouteVisibleToClient(i.to)).length}/{section.items.length} visible
                  </span>
                  {/* Section-level bulk toggle */}
                  <button
                    onClick={() => {
                      section.items.forEach(item => {
                        if (allVisible ? true : !isRouteVisibleToClient(item.to)) {
                          // toggle all to hidden if all visible, else show all
                        }
                        const shouldHide = allVisible;
                        const current = isRouteVisibleToClient(item.to);
                        if (shouldHide && current) handleToggle(item.to);
                        else if (!shouldHide && !current) handleToggle(item.to);
                      });
                    }}
                    className="text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors px-2 py-0.5 rounded border border-white/10 hover:border-white/20"
                  >
                    {allVisible ? "Hide all" : allHidden ? "Show all" : "Toggle all"}
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {section.items.map((item) => {
                  const visible = isRouteVisibleToClient(item.to);
                  return (
                    <button
                      key={item.to}
                      onClick={() => handleToggle(item.to)}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg border transition-all text-left ${
                        visible
                          ? "border-white/[0.08] bg-white/[0.02] hover:border-white/[0.14]"
                          : "border-red-500/20 bg-red-500/[0.04] hover:border-red-500/30"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        {visible ? (
                          <Eye className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <EyeOff className="w-3.5 h-3.5 text-red-400 shrink-0" />
                        )}
                        <span className={`text-[12px] font-medium ${visible ? "text-zinc-300" : "text-zinc-500 line-through"}`}>
                          {item.label}
                        </span>
                      </div>
                      <span className={`text-[10px] shrink-0 ${visible ? "text-emerald-500" : "text-red-500"}`}>
                        {visible ? "Visible" : "Hidden"}
                      </span>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {saving && (
        <div className="fixed bottom-6 right-6 flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-sm">
          <CheckCircle className="w-3.5 h-3.5" />
          Saved
        </div>
      )}
    </div>
  );
}
