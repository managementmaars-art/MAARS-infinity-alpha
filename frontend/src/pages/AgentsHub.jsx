/**
 * AgentsHub — consolidates the four agent surfaces that used to live
 * as separate top-level pages (/agents, /create-agent, /agent-suggestions,
 * /agent-catalog) into one sub-tabbed page at /agents.
 *
 * Commander Orion stays separate at /commander — he is the orchestrator
 * for the Infinity tier and deserves his own page.
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Bot, UserPlus, Sparkles, Store } from "lucide-react";

import Agents from "./Agents";
import CreateAgent from "./CreateAgent";
import AgentSuggestions from "./AgentSuggestions";
import AgentCatalog from "./AgentCatalog";

const VIEWS = [
  { id: "list",        label: "My Agents",   icon: Bot,       Component: Agents },
  { id: "create",      label: "Create",      icon: UserPlus,  Component: CreateAgent },
  { id: "suggestions", label: "Suggestions", icon: Sparkles,  Component: AgentSuggestions },
  { id: "catalog",     label: "Catalog",     icon: Store,     Component: AgentCatalog },
];

export default function AgentsHub() {
  const [params, setParams] = useSearchParams();
  const initial = params.get("view") || "list";
  const [view, setView] = useState(
    VIEWS.find(v => v.id === initial) ? initial : "list"
  );

  const set = (id) => {
    setView(id);
    const p = new URLSearchParams(params);
    p.set("view", id);
    setParams(p, { replace: true });
  };

  const Active = VIEWS.find(v => v.id === view)?.Component || Agents;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "0 24px" }}>
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
