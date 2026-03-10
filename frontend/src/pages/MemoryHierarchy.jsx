import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Database, Layers, Clock, HardDrive, Zap, Info } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

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

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="memory-hierarchy">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Memory Hierarchy</h1>
        <p className="text-sm text-zinc-400 mt-1">7-layer memory architecture from L1 working memory to L7 archival storage</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3" data-testid="memory-summary">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Layers className="w-4 h-4 text-violet-400" /><span className="text-xs text-zinc-500">Memory Layers</span></div>
          <p className="text-2xl font-bold text-white">7</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><Database className="w-4 h-4 text-cyan-400" /><span className="text-xs text-zinc-500">Total Items</span></div>
          <p className="text-2xl font-bold text-white">{totalItems}</p>
        </div>
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2"><HardDrive className="w-4 h-4 text-emerald-400" /><span className="text-xs text-zinc-500">Total Usage</span></div>
          <p className="text-2xl font-bold text-white">{totalUsage < 1024 ? `${totalUsage.toFixed(1)} KB` : `${(totalUsage / 1024).toFixed(1)} MB`}</p>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Pyramid Visualization */}
        <div className="flex-1" data-testid="memory-pyramid">
          <div className="flex flex-col items-center gap-1">
            {layers.map((layer, i) => {
              const stat = getStatForLayer(layer.layer);
              const widthPercent = 30 + (i * 10);
              const isSelected = selectedLayer === layer.layer;
              return (
                <button
                  key={layer.layer}
                  onClick={() => setSelectedLayer(isSelected ? null : layer.layer)}
                  className={`relative transition-all rounded-lg border ${isSelected ? "border-white/20 shadow-lg" : "border-transparent hover:border-white/10"}`}
                  style={{ width: `${widthPercent}%`, minWidth: "200px" }}
                  data-testid={`memory-layer-${layer.layer}`}
                >
                  <div className="px-4 py-3 rounded-lg" style={{ backgroundColor: `${layer.color}15` }}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold" style={{ backgroundColor: `${layer.color}25`, color: layer.color }}>
                          {layer.code}
                        </div>
                        <div className="text-left">
                          <p className="text-xs font-medium text-white">{layer.name}</p>
                          <p className="text-[9px] text-zinc-500">TTL: {layer.ttl}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs font-bold" style={{ color: layer.color }}>{stat.items} items</p>
                        <p className="text-[9px] text-zinc-500">{stat.usage_kb.toFixed(1)} KB</p>
                      </div>
                    </div>
                    {/* Usage bar */}
                    <div className="mt-2 h-1 bg-zinc-800/50 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{
                        backgroundColor: layer.color,
                        width: `${totalUsage > 0 ? Math.max((stat.usage_kb / totalUsage) * 100, 2) : 2}%`,
                        opacity: 0.7,
                      }} />
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Speed Indicators */}
          <div className="flex items-center justify-between mt-4 px-8">
            <div className="flex items-center gap-1.5 text-[10px] text-red-400"><Zap className="w-3 h-3" /> Fastest (L1)</div>
            <div className="flex-1 h-px bg-gradient-to-r from-red-500/30 via-amber-500/30 via-blue-500/30 to-violet-500/30 mx-3" />
            <div className="flex items-center gap-1.5 text-[10px] text-indigo-400"><Clock className="w-3 h-3" /> Largest (L7)</div>
          </div>
        </div>

        {/* Detail Panel */}
        {selectedLayer && (() => {
          const layer = layers.find(l => l.layer === selectedLayer);
          const stat = getStatForLayer(selectedLayer);
          if (!layer) return null;
          return (
            <div className="w-72 bg-zinc-900/40 border border-white/5 rounded-xl p-4 shrink-0" data-testid="memory-detail">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold" style={{ backgroundColor: `${layer.color}20`, color: layer.color }}>
                  {layer.code}
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{layer.name}</p>
                  <p className="text-[10px] text-zinc-500">Layer {layer.layer}</p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 mb-4">{layer.description}</p>
              <div className="space-y-3">
                {[
                  { label: "TTL", value: layer.ttl },
                  { label: "Capacity", value: layer.capacity },
                  { label: "Access Speed", value: layer.access_speed },
                  { label: "Current Items", value: stat.items },
                  { label: "Current Usage", value: `${stat.usage_kb.toFixed(1)} KB` },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-[10px] text-zinc-500">{item.label}</span>
                    <span className="text-xs text-white font-medium">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}
