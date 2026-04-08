/**
 * PreviewModeContext — gives the admin the ability to:
 *   1. Toggle into "Client View" to see exactly what clients see
 *   2. Simulate any subscription plan (Free / Starter / Pro / Business)
 *   3. Control which nav pages are visible to clients
 */
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";

const PreviewModeContext = createContext(null);

export const PREVIEW_PLANS = {
  free:     { label: "Free",     color: "text-zinc-400",   bg: "bg-zinc-500/20",   credits: 50,    max_agents: 3,  includes_commander: false },
  starter:  { label: "Starter",  color: "text-blue-400",   bg: "bg-blue-500/20",   credits: 500,   max_agents: 10, includes_commander: false },
  pro:      { label: "Pro",      color: "text-violet-400", bg: "bg-violet-500/20", credits: 2000,  max_agents: 25, includes_commander: true  },
  business: { label: "Business", color: "text-amber-400",  bg: "bg-amber-500/20",  credits: 6000,  max_agents: 41, includes_commander: true  },
};

export function PreviewModeProvider({ children }) {
  const { user, token } = useAuth();

  const [previewMode, setPreviewMode] = useState(() => {
    try { return localStorage.getItem("maars_preview_mode") === "true"; } catch { return false; }
  });

  const [previewPlan, setPreviewPlan] = useState(() => {
    try { return localStorage.getItem("maars_preview_plan") || "free"; } catch { return "free"; }
  });

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
