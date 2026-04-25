/**
 * MemoryHub — consolidates the five memory surfaces that used to live
 * as separate top-level pages (/workspace, /brain-profiles, /memory,
 * /knowledge-graph, /memory-hierarchy) into one sub-tabbed page at
 * /memory. Each tab renders its original page component unchanged.
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Brain, Cpu, Shield, Share2, HardDrive } from "lucide-react";

import WorkspaceBrain from "./WorkspaceBrain";
import BrainProfiles from "./BrainProfiles";
import MemoryGovernance from "./MemoryGovernance";
import KnowledgeGraph from "./KnowledgeGraph";
import MemoryHierarchy from "./MemoryHierarchy";

const VIEWS = [
  { id: "workspace",  label: "Workspace Brain", icon: Brain,     Component: WorkspaceBrain },
  { id: "profiles",   label: "Brain Profiles",  icon: Cpu,       Component: BrainProfiles },
  { id: "governance", label: "Governance",      icon: Shield,    Component: MemoryGovernance },
  { id: "graph",      label: "Knowledge Graph", icon: Share2,    Component: KnowledgeGraph },
  { id: "hierarchy",  label: "Hierarchy",       icon: HardDrive, Component: MemoryHierarchy },
];

export default function MemoryHub() {
  const [params, setParams] = useSearchParams();
  const initial = params.get("view") || "workspace";
  const [view, setView] = useState(
    VIEWS.find(v => v.id === initial) ? initial : "workspace"
  );

  const set = (id) => {
    setView(id);
    const p = new URLSearchParams(params);
    p.set("view", id);
    setParams(p, { replace: true });
  };

  const Active = VIEWS.find(v => v.id === view)?.Component || WorkspaceBrain;

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
