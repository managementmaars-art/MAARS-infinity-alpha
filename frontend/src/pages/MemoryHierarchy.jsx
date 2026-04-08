import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Database, Layers, Clock, HardDrive, Zap } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#7c3aed",
  cyan: "#22d3ee",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

export default function MemoryHierarchy() {
  const { token } = useAuth();
  const [layers, setLayers] = useState([]);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLayer, setSelectedLayer] = useState(null);

  useEffect(() => {
    const h = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch(`${API}/api/kernel/memory/layers`, { headers: h }).then(r => r.json()),
      fetch(`${API}/api/kernel/memory/stats`, { headers: h }).then(r => r.json()),
    ]).then(([l, s]) => {
      setLayers(Array.isArray(l) ? l : []);
      setStats(Array.isArray(s) ? s : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const getStatForLayer = (layerNum) => stats.find(s => s.layer === layerNum) || { items: 0, usage_kb: 0 };
  const totalUsage = stats.reduce((s, x) => s + x.usage_kb, 0);
  const totalItems = stats.reduce((s, x) => s + x.items, 0);

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.violet}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const selected = layers.find(l => l.layer === selectedLayer);
  const selectedStat = selectedLayer ? getStatForLayer(selectedLayer) : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="memory-hierarchy">
      <style>{STYLES}</style>

      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Memory Hierarchy</h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>7-layer memory architecture from L1 working memory to L7 archival storage</p>
      </div>

      {/* Summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }} data-testid="memory-summary">
        {[
          { icon: Layers, label: "Memory Layers", value: "7", accent: T.violet },
          { icon: Database, label: "Total Items", value: totalItems, accent: T.cyan },
          { icon: HardDrive, label: "Total Usage", value: totalUsage < 1024 ? `${totalUsage.toFixed(1)} KB` : `${(totalUsage / 1024).toFixed(1)} MB`, accent: T.green },
        ].map(s => (
          <div key={s.label} style={{ position: "relative", background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 18px", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: s.accent }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <s.icon size={14} style={{ color: s.accent }} />
              <span style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em" }}>{s.label}</span>
            </div>
            <div style={{ fontSize: 24, fontWeight: 700, color: "#fff" }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        {/* Pyramid */}
        <div style={{ flex: 1 }} data-testid="memory-pyramid">
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            {layers.map((layer, i) => {
              const stat = getStatForLayer(layer.layer);
              const widthPct = 30 + (i * 10);
              const isSelected = selectedLayer === layer.layer;
              return (
                <button
                  key={layer.layer}
                  onClick={() => setSelectedLayer(isSelected ? null : layer.layer)}
                  data-testid={`memory-layer-${layer.layer}`}
                  style={{
                    width: `${widthPct}%`, minWidth: 200,
                    borderRadius: 12, border: `1px solid ${isSelected ? "rgba(255,255,255,.2)" : "transparent"}`,
                    background: `${layer.color}15`, padding: "10px 14px",
                    cursor: "pointer", transition: "all .2s",
                    boxShadow: isSelected ? `0 0 0 1px ${layer.color}30` : "none",
                  }}
                  onMouseEnter={e => !isSelected && (e.currentTarget.style.borderColor = `${layer.color}40`)}
                  onMouseLeave={e => !isSelected && (e.currentTarget.style.borderColor = "transparent")}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{ width: 28, height: 28, borderRadius: 8, background: `${layer.color}25`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: layer.color }}>
                        {layer.code}
                      </div>
                      <div style={{ textAlign: "left" }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: "#fff" }}>{layer.name}</div>
                        <div style={{ fontSize: 9, color: T.zinc }}>TTL: {layer.ttl}</div>
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: layer.color }}>{stat.items} items</div>
                      <div style={{ fontSize: 9, color: T.zinc }}>{stat.usage_kb.toFixed(1)} KB</div>
                    </div>
                  </div>
                  <div style={{ height: 3, background: "rgba(255,255,255,.06)", borderRadius: 4, overflow: "hidden", marginTop: 8 }}>
                    <div style={{ height: "100%", borderRadius: 4, background: layer.color, opacity: .7, width: `${totalUsage > 0 ? Math.max((stat.usage_kb / totalUsage) * 100, 2) : 2}%` }} />
                  </div>
                </button>
              );
            })}
          </div>
          {/* Speed gradient */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 16, paddingLeft: "8%", paddingRight: "8%" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: T.red }}><Zap size={11} /> Fastest (L1)</div>
            <div style={{ flex: 1, height: 1, margin: "0 12px", background: "linear-gradient(to right, rgba(239,68,68,.4), rgba(245,158,11,.4), rgba(96,165,250,.4), rgba(124,58,237,.4))" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: "#818cf8" }}><Clock size={11} /> Largest (L7)</div>
          </div>
        </div>

        {/* Detail panel */}
        {selected && (
          <div style={{ width: 280, flexShrink: 0, background: T.glass, border: `1px solid ${T.border}`, borderRadius: 16, padding: "18px 20px" }} data-testid="memory-detail">
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: `${selected.color}20`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: selected.color }}>
                {selected.code}
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{selected.name}</div>
                <div style={{ fontSize: 10, color: T.zinc }}>Layer {selected.layer}</div>
              </div>
            </div>
            <p style={{ fontSize: 12, color: T.zinc, marginBottom: 16, lineHeight: 1.6 }}>{selected.description}</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                ["TTL", selected.ttl],
                ["Capacity", selected.capacity],
                ["Access Speed", selected.access_speed],
                ["Current Items", selectedStat.items],
                ["Current Usage", `${selectedStat.usage_kb.toFixed(1)} KB`],
              ].map(([label, val]) => (
                <div key={label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: 10, color: T.zinc }}>{label}</span>
                  <span style={{ fontSize: 11, fontWeight: 600, color: "#fff" }}>{val}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
