/**
 * Governance Tab — consolidates the six governance surfaces that used
 * to live as top-level pages (/rbac, /circuit-breakers, /cost-governance,
 * /trust-scores, /operator, /activity-monitor). They're now admin-only
 * because they expose control/audit surfaces that shouldn't be client-
 * facing. The underlying page components are self-contained so we just
 * render them inside a sub-tab switcher here.
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Shield, Activity, DollarSign, Zap, Command, Gauge } from "lucide-react";

import RBAC from "../../../pages/RBAC";
import CircuitBreakers from "../../../pages/CircuitBreakers";
import CostGovernance from "../../../pages/CostGovernance";
import TrustScores from "../../../pages/TrustScores";
import OperatorControlPanel from "../../../pages/OperatorControlPanel";
import ActivityMonitor from "../../../pages/ActivityMonitor";

const VIEWS = [
  { id: "rbac",           label: "RBAC",            icon: Shield,    Component: RBAC },
  { id: "circuit",        label: "Circuit Breakers", icon: Zap,      Component: CircuitBreakers },
  { id: "cost",           label: "Cost Governance",  icon: DollarSign, Component: CostGovernance },
  { id: "trust",          label: "Trust Scores",     icon: Gauge,    Component: TrustScores },
  { id: "operator",       label: "Operator Panel",   icon: Command,  Component: OperatorControlPanel },
  { id: "activity",       label: "Activity Monitor", icon: Activity, Component: ActivityMonitor },
];

export default function GovernanceTab() {
  const [params, setParams] = useSearchParams();
  const initial = params.get("view") || "rbac";
  const [view, setView] = useState(
    VIEWS.find(v => v.id === initial) ? initial : "rbac"
  );

  const set = (id) => {
    setView(id);
    const p = new URLSearchParams(params);
    p.set("view", id);
    setParams(p, { replace: true });
  };

  const Active = VIEWS.find(v => v.id === view)?.Component || RBAC;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid rgba(255,255,255,0.08)", paddingBottom: 2 }}>
        {VIEWS.map(v => {
          const active = v.id === view;
          const Icon = v.icon;
          return (
            <button
              key={v.id}
              onClick={() => set(v.id)}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "8px 14px", fontSize: 12, fontWeight: 500,
                background: "transparent",
                border: "none",
                borderBottom: active ? "2px solid #a78bfa" : "2px solid transparent",
                color: active ? "#c4b5fd" : "#71717a",
                cursor: "pointer", marginBottom: -1,
              }}
            >
              <Icon size={13} /> {v.label}
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
