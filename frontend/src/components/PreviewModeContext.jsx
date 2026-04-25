/**
 * PreviewModeContext — gives the admin the ability to:
 *   1. Toggle into "Client View" to see exactly what clients see
 *   2. Simulate any subscription plan (Free / Starter / Pro / Business)
 *   3. Control which nav pages are visible to clients
 */
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";

const PreviewModeContext = createContext(null);

// UNIFIED 5-tier plans — matches backend services/billing/plan_deliverables.py
// PLAN_CATALOG and what the public /api/plans plans_v2 returns. Keeping the
// credits/agent/commander defaults here as a synchronous fallback for the
// first render before PreviewModeProvider fetches plans from the backend.
// When you change a plan's credits here, update PLAN_CATALOG too.
export const PREVIEW_PLANS = {
  free:     { label: "Free",     color: "text-zinc-400",   bg: "bg-zinc-500/20",   credits: 10,    max_agents: 3,  includes_commander: false },
  creator:  { label: "Creator",  color: "text-teal-400",   bg: "bg-teal-500/20",   credits: 50,    max_agents: 12, includes_commander: false },
  studio:   { label: "Studio",   color: "text-violet-400", bg: "bg-violet-500/20", credits: 200,   max_agents: 25, includes_commander: true  },
  scale:    { label: "Scale",    color: "text-indigo-400", bg: "bg-indigo-500/20", credits: 750,   max_agents: 41, includes_commander: true  },
  infinity: { label: "Infinity", color: "text-amber-400",  bg: "bg-amber-500/20",  credits: 5000,  max_agents: -1, includes_commander: true  },
};

export function PreviewModeProvider({ children }) {
  const { user, token } = useAuth();

  const [previewMode, setPreviewMode] = useState(() => {
    try { return localStorage.getItem("maars_preview_mode") === "true"; } catch { return false; }
  });

  const [previewPlan, setPreviewPlan] = useState(() => {
    try { return localStorage.getItem("maars_preview_plan") || "free"; } catch { return "free"; }
  });

  // Live plans from /api/plans — keeps preview toolbar synced with whatever
  // the operator has published. Falls back to the static PREVIEW_PLANS
  // constants while the fetch is in flight.
  const [livePreviewPlans, setLivePreviewPlans] = useState(PREVIEW_PLANS);

  useEffect(() => {
    fetch(`${API}/plans`).then(r => r.ok ? r.json() : null).then(data => {
      if (!data) return;
      const v2 = Array.isArray(data.plans_v2) ? data.plans_v2 : [];
      if (!v2.length) return;
      // Merge v2 into the display map; preserve color/bg from static config.
      const merged = { ...PREVIEW_PLANS };
      for (const p of v2) {
        const fallback = merged[p.plan_id] || PREVIEW_PLANS.free;
        merged[p.plan_id] = {
          ...fallback,
          label:              p.name || fallback.label,
          credits:            p.credits ?? fallback.credits,
          max_agents:         p.max_agents ?? fallback.max_agents,
          includes_commander: p.includes_commander ?? fallback.includes_commander,
          price_usd:          p.price_usd,
          tagline:            p.tagline,
        };
      }
      setLivePreviewPlans(merged);
    }).catch(() => {});
  }, []);

  // Map of route path → visible (true = shown to clients, false = hidden)
  const [navVisibility, setNavVisibility] = useState({});
  const [visibilityLoaded, setVisibilityLoaded] = useState(false);

  const isAdmin = user?.is_admin;

  // Load visibility settings from backend
  const loadVisibility = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/admin/nav-visibility`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setNavVisibility(data.visibility || {});
      }
    } catch {}
    setVisibilityLoaded(true);
  }, [token]);

  useEffect(() => {
    if (isAdmin) loadVisibility();
    else {
      // Non-admins fetch the public endpoint
      fetch(`${API}/admin/nav-visibility/public`)
        .then(r => r.ok ? r.json() : { visibility: {} })
        .then(d => { setNavVisibility(d.visibility || {}); setVisibilityLoaded(true); })
        .catch(() => setVisibilityLoaded(true));
    }
  }, [isAdmin, loadVisibility]);

  const saveVisibility = useCallback(async (updated) => {
    if (!token) return;
    setNavVisibility(updated);
    try {
      await fetch(`${API}/admin/nav-visibility`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ visibility: updated }),
      });
    } catch {}
  }, [token]);

  const toggleNavItem = useCallback((route) => {
    setNavVisibility(prev => {
      const current = prev[route] !== false; // default true
      const updated = { ...prev, [route]: !current };
      saveVisibility(updated);
      return updated;
    });
  }, [saveVisibility]);

  const enterPreview = useCallback((plan = "free") => {
    setPreviewMode(true);
    setPreviewPlan(plan);
    try {
      localStorage.setItem("maars_preview_mode", "true");
      localStorage.setItem("maars_preview_plan", plan);
    } catch {}
  }, []);

  const exitPreview = useCallback(() => {
    setPreviewMode(false);
    try {
      localStorage.removeItem("maars_preview_mode");
    } catch {}
  }, []);

  const switchPreviewPlan = useCallback((plan) => {
    setPreviewPlan(plan);
    try { localStorage.setItem("maars_preview_plan", plan); } catch {}
  }, []);

  /**
   * isRouteVisibleToClient(route) — used by DashboardLayout to decide
   * whether a nav item should appear for clients.
   * If no entry exists → defaults to visible (true).
   */
  const isRouteVisibleToClient = useCallback((route) => {
    if (navVisibility[route] === false) return false;
    return true;
  }, [navVisibility]);

  return (
    <PreviewModeContext.Provider value={{
      previewMode: isAdmin ? previewMode : false,
      previewPlan,
      previewPlans: livePreviewPlans,   // live plans from /api/plans
      navVisibility,
      visibilityLoaded,
      isRouteVisibleToClient,
      toggleNavItem,
      enterPreview,
      exitPreview,
      switchPreviewPlan,
      loadVisibility,
    }}>
      {children}
    </PreviewModeContext.Provider>
  );
}

export function usePreviewMode() {
  const ctx = useContext(PreviewModeContext);
  if (!ctx) throw new Error("usePreviewMode must be inside PreviewModeProvider");
  return ctx;
}
