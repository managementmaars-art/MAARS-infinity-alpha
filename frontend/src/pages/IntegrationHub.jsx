import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Link2, Unlink, Check, ExternalLink, Settings, ToggleLeft, ToggleRight, MessageCircle, ShoppingBag, Users, Cloud, Hash, Zap, Mail } from "lucide-react";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const ICONS = {
  "message-circle": MessageCircle, "shopping-bag": ShoppingBag,
  "users": Users, "cloud": Cloud, "hash": Hash, "zap": Zap, "mail": Mail,
};

export default function IntegrationHub() {
  const { token } = useAuth();
  const [data, setData] = useState({ available: [], connected: [], connected_ids: [] });
  const [loading, setLoading] = useState(true);
  const [configuring, setConfiguring] = useState(null); // integration_id being configured
  const [configValues, setConfigValues] = useState({});

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = async () => {
    try {
      const res = await fetch(`${API}/api/kernel/integrations/available`, { headers: h });
      if (res.ok) setData(await res.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [token]);

  const connect = async (integrationId) => {
    const res = await fetch(`${API}/api/kernel/integrations/connect`, {
      method: "POST", headers: h,
      body: JSON.stringify({ integration_id: integrationId, config: configValues }),
    });
    if (res.ok) {
      toast.success("Integration connected");
      setConfiguring(null);
      setConfigValues({});
      fetchData();
    }
  };

  const disconnect = async (integrationId) => {
    await fetch(`${API}/api/kernel/integrations/${integrationId}`, { method: "DELETE", headers: h });
    toast.success("Integration disconnected");
    fetchData();
  };

  const toggleEnabled = async (integrationId, enabled) => {
    await fetch(`${API}/api/kernel/integrations/${integrationId}/toggle`, {
      method: "PUT", headers: h,
      body: JSON.stringify({ enabled: !enabled }),
    });
    fetchData();
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  const connected = data.connected || [];
  const connectedIds = new Set(data.connected_ids || []);

  // Group by category
  const categories = {};
  (data.available || []).forEach(i => {
    if (!categories[i.category]) categories[i.category] = [];
    categories[i.category].push(i);
  });

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8" data-testid="integration-hub">
      <div>
        <h1 className="text-xl font-bold text-white">Integration Hub</h1>
        <p className="text-sm text-zinc-500">Connect external services to power your AI agents with real-world data and actions</p>
      </div>

      {/* Connected integrations */}
      {connected.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Active Connections</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="connected-integrations">
            {connected.map(c => {
              const template = (data.available || []).find(a => a.integration_id === c.integration_id);
              return (
                <div key={c.integration_id} className="rounded-xl border border-white/5 bg-zinc-900/30 p-4" data-testid={`connected-${c.integration_id}`}>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${c.color}20` }}>
                      <IntIcon name={template?.icon} color={c.color} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white">{c.name}</p>
                      <p className="text-[10px] text-zinc-500">{c.category}</p>
                    </div>
                    <button onClick={() => toggleEnabled(c.integration_id, c.enabled)}
                      className="text-zinc-500 hover:text-white transition-colors" data-testid={`toggle-${c.integration_id}`}>
                      {c.enabled ? <ToggleRight className="w-5 h-5 text-emerald-400" /> : <ToggleLeft className="w-5 h-5" />}
                    </button>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${c.enabled ? "bg-emerald-500/10 text-emerald-400" : "bg-zinc-800 text-zinc-500"}`}>
                      {c.enabled ? "Active" : "Paused"}
                    </span>
                    <span className="text-[9px] text-zinc-600">Connected {new Date(c.connected_at).toLocaleDateString()}</span>
                    <div className="flex-1" />
                    <button onClick={() => disconnect(c.integration_id)} className="text-[9px] text-zinc-600 hover:text-red-400 transition-colors"
                      data-testid={`disconnect-${c.integration_id}`}>
                      <Unlink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Available integrations by category */}
      {Object.entries(categories).map(([category, integrations]) => (
        <div key={category}>
          <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">{category}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {integrations.map(integ => {
              const isConnected = connectedIds.has(integ.integration_id);
              const isConfiguring = configuring === integ.integration_id;
              return (
                <div key={integ.integration_id}
                  className={`rounded-xl border p-4 transition-all ${isConnected ? "border-emerald-500/20 bg-emerald-500/[0.02]" : "border-white/5 bg-zinc-900/30 hover:border-white/10"}`}
                  data-testid={`integration-${integ.integration_id}`}>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${integ.color}15` }}>
                      <IntIcon name={integ.icon} color={integ.color} size={20} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <p className="text-sm font-semibold text-white">{integ.name}</p>
                        {isConnected && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                      </div>
                      <p className="text-[10px] text-zinc-500">{integ.category}</p>
                    </div>
                  </div>
                  <p className="text-xs text-zinc-400 mb-3 line-clamp-2">{integ.description}</p>

                  {/* Features */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {(integ.features || []).slice(0, 3).map(f => (
                      <span key={f} className="text-[8px] px-1.5 py-0.5 rounded bg-zinc-800/50 text-zinc-500">{f}</span>
                    ))}
                    {(integ.features || []).length > 3 && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded bg-zinc-800/50 text-zinc-500">+{integ.features.length - 3}</span>
                    )}
                  </div>

                  {/* Config form */}
                  {isConfiguring && (
                    <div className="space-y-2 mb-3 p-2 bg-zinc-800/30 rounded-lg" data-testid={`config-form-${integ.integration_id}`}>
                      {(integ.config_fields || []).map(field => (
                        <div key={field.key}>
                          <label className="text-[9px] text-zinc-400 font-medium">{field.label}{field.required && " *"}</label>
                          <input
                            type={field.type === "password" ? "password" : "text"}
                            placeholder={field.placeholder || ""}
                            value={configValues[field.key] || ""}
                            onChange={e => setConfigValues(prev => ({ ...prev, [field.key]: e.target.value }))}
                            className="w-full bg-zinc-900/50 border border-white/5 rounded px-2 py-1.5 text-[10px] text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30 mt-0.5"
                            data-testid={`config-${field.key}`}
                          />
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {isConnected ? (
                      <span className="text-[10px] text-emerald-400 flex items-center gap-1"><Check className="w-3 h-3" /> Connected</span>
                    ) : isConfiguring ? (
                      <>
                        <Button size="sm" className="h-7 text-[10px] bg-emerald-600 hover:bg-emerald-700" onClick={() => connect(integ.integration_id)}
                          data-testid={`connect-save-${integ.integration_id}`}>
                          <Link2 className="w-3 h-3 mr-1" /> Save & Connect
                        </Button>
                        <Button size="sm" variant="ghost" className="h-7 text-[10px] text-zinc-400" onClick={() => { setConfiguring(null); setConfigValues({}); }}>
                          Cancel
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" variant="outline" className="h-7 text-[10px] border-white/10" onClick={() => setConfiguring(integ.integration_id)}
                        data-testid={`connect-btn-${integ.integration_id}`}>
                        <Settings className="w-3 h-3 mr-1" /> Configure
                      </Button>
                    )}
                    <div className="flex-1" />
                    <a href={integ.docs_url} target="_blank" rel="noopener noreferrer" className="text-zinc-600 hover:text-zinc-400 transition-colors">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function IntIcon({ name, color, size = 16 }) {
  const Icon = ICONS[name] || Zap;
  return <Icon style={{ color, width: size, height: size }} />;
}
