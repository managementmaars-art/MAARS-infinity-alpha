/**
 * DashboardHub — consolidates the four dashboard views that used to
 * live as separate top-level pages (/dashboard, /kpi-dashboard,
 * /analytics, /observability) into one sub-tabbed page at /dashboard.
 *
 * Each tab renders its original page component unchanged so none of
 * the existing data/UX is lost — just unified under a single URL.
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { LayoutDashboard, Gauge, PieChart, Radar } from "lucide-react";

import Dashboard from "./Dashboard";
import KPIDashboard from "./KPIDashboard";
import AnalyticsDashboard from "./AnalyticsDashboard";
import ObservabilityDashboard from "./ObservabilityDashboard";

const VIEWS = [
  { id: "overview",      label: "Overview",       icon: LayoutDashboard, Component: Dashboard },
  { id: "kpi",           label: "KPIs",           icon: Gauge,           Component: KPIDashboard },
  { id: "analytics",     label: "Analytics",      icon: PieChart,        Component: AnalyticsDashboard },
  { id: "observability", label: "Observability",  icon: Radar,           Component: ObservabilityDashboard },
];

export default function DashboardHub() {
  const [params, setParams] = useSearchParams();
  const initial = params.get("view") || "overview";
  const [view, setView] = useState(
    VIEWS.find(v => v.id === initial) ? initial : "overview"
  );

  const set = (id) => {
    setView(id);
    const p = new URLSearchParams(params);
    p.set("view", id);
    setParams(p, { replace: true });
  };

  const Active = VIEWS.find(v => v.id === view)?.Component || Dashboard;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid rgba(255,255,255,0.08)", paddingBottom: 2, padding: "0 24px" }}>
        {VIEWS.map(v => {
          const active = v.id === view;
          const Icon = v.icon;
          return (
            <button
              key={v.id}
              onClick={() => set(v.id)}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "10px 16px", fontSize: 13, fontWeight: 500,
                background: "transparent",
                border: "none",
                borderBottom: active ? "2px solid #a78bfa" : "2px solid transparent",
                color: active ? "#c4b5fd" : "#9ca3af",
                cursor: "pointer", marginBottom: -1,
              }}
            >
              <Icon size={14} /> {v.label}
            </button>
          );
        })}
      </div>
      <div>
        <Active />
      </div>
    </div>
  );
}
