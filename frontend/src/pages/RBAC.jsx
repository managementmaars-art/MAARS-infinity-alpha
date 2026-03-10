import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Shield, Users, Check, X, ChevronDown, ChevronRight, Lock, Unlock, Info } from "lucide-react";
import { Button } from "../components/ui/button";

const API = process.env.REACT_APP_BACKEND_URL;

const ROLE_COLORS = {
  admin: { bg: "bg-red-500/10", text: "text-red-400", badge: "bg-red-500" },
  manager: { bg: "bg-indigo-500/10", text: "text-indigo-400", badge: "bg-indigo-500" },
  analyst: { bg: "bg-cyan-500/10", text: "text-cyan-400", badge: "bg-cyan-500" },
  viewer: { bg: "bg-zinc-500/10", text: "text-zinc-400", badge: "bg-zinc-500" },
};

export default function RBAC() {
  const { token } = useAuth();
  const [config, setConfig] = useState({ roles: {}, resources: [], actions: [] });
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState("admin");
  const [expandedUser, setExpandedUser] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/rbac/config`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/kernel/rbac/users`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ]).then(([cfg, usrs]) => {
      setConfig(cfg);
      setUsers(Array.isArray(usrs) ? usrs : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const changeRole = async (userId, role) => {
    const res = await fetch(`${API}/api/kernel/rbac/users/${userId}/role`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });
    if (res.ok) {
      setUsers(prev => prev.map(u => u.user_id === userId ? { ...u, role } : u));
    }
  };

  const roles = config.roles || {};
  const resources = config.resources || [];
  const actions = config.actions || [];

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-red-500 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="rbac-page">
      <div>
        <h1 className="text-2xl font-bold text-white font-['Outfit']">Access Control (RBAC)</h1>
        <p className="text-sm text-zinc-400 mt-1">Manage roles, permissions, and user access across the MAARS ∞ system</p>
      </div>

      {/* Role Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="role-cards">
        {Object.entries(roles).map(([key, role]) => {
          const rc = ROLE_COLORS[key] || ROLE_COLORS.viewer;
          const isSelected = selectedRole === key;
          const userCount = users.filter(u => u.role === key).length;
          return (
            <button key={key} onClick={() => setSelectedRole(key)}
              className={`text-left p-4 rounded-xl border transition-all ${isSelected ? `${rc.bg} border-white/10` : "bg-zinc-900/40 border-white/5 hover:border-white/10"}`}
              data-testid={`role-card-${key}`}>
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-2.5 h-2.5 rounded-full ${rc.badge}`} />
                <span className={`text-sm font-semibold ${rc.text}`}>{role.label}</span>
              </div>
              <p className="text-[11px] text-zinc-500 mb-2">{role.description}</p>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-zinc-600">{role.permissions.length === 1 && role.permissions[0] === "*" ? "All" : role.permissions.length} permissions</span>
                <span className="text-[10px] text-zinc-600">{userCount} users</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Permission Matrix */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4" data-testid="permission-matrix">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Lock className="w-4 h-4 text-zinc-500" /> Permission Matrix — {roles[selectedRole]?.label}</h3>
          <div className="space-y-1">
            {resources.map(resource => {
              const perms = roles[selectedRole]?.permissions || [];
              const hasWild = perms.includes("*");
              return (
                <div key={resource} className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-white/[0.02]">
                  <span className="text-xs text-zinc-300 w-32 truncate">{resource.replace(/_/g, " ")}</span>
                  <div className="flex gap-1">
                    {actions.map(action => {
                      const perm = `${resource}:${action}`;
                      const has = hasWild || perms.includes(perm);
                      return (
                        <div key={action} className={`w-12 h-6 rounded flex items-center justify-center text-[9px] font-medium ${has ? "bg-emerald-500/15 text-emerald-400" : "bg-zinc-800/50 text-zinc-600"}`}
                          title={`${resource}:${action}`}>
                          {has ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            <div className="flex items-center gap-2 pt-2 text-[9px] text-zinc-600">
              {actions.map(a => <span key={a} className="w-12 text-center">{a}</span>)}
            </div>
          </div>
        </div>

        {/* User Assignments */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4" data-testid="user-assignments">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><Users className="w-4 h-4 text-zinc-500" /> User Assignments</h3>
          <div className="space-y-1.5">
            {users.map(user => {
              const rc = ROLE_COLORS[user.role] || ROLE_COLORS.viewer;
              const isExpanded = expandedUser === user.user_id;
              return (
                <div key={user.user_id} className="bg-zinc-800/30 border border-white/[0.03] rounded-lg overflow-hidden" data-testid={`user-${user.user_id}`}>
                  <button onClick={() => setExpandedUser(isExpanded ? null : user.user_id)}
                    className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-white/[0.02] transition-colors">
                    <div className="w-7 h-7 rounded-lg bg-zinc-700/50 flex items-center justify-center text-[10px] font-bold text-zinc-300">
                      {user.name?.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase() || "??"}
                    </div>
                    <div className="flex-1 text-left min-w-0">
                      <p className="text-xs text-white truncate">{user.name}</p>
                      <p className="text-[10px] text-zinc-500 truncate">{user.email}</p>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${rc.bg} ${rc.text}`}>{user.role}</span>
                    <ChevronRight className={`w-3 h-3 text-zinc-600 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
                  </button>
                  {isExpanded && (
                    <div className="px-3 pb-3 pt-1 border-t border-white/[0.03]">
                      <p className="text-[10px] text-zinc-500 mb-2">Change role:</p>
                      <div className="flex gap-1.5">
                        {Object.entries(roles).map(([key, role]) => {
                          const c = ROLE_COLORS[key] || ROLE_COLORS.viewer;
                          return (
                            <button key={key} onClick={() => changeRole(user.user_id, key)}
                              className={`px-2.5 py-1 rounded text-[10px] font-medium transition-colors ${user.role === key ? `${c.bg} ${c.text} ring-1 ring-current/30` : "bg-zinc-800 text-zinc-500 hover:text-zinc-300"}`}
                              data-testid={`set-role-${key}-${user.user_id}`}>
                              {role.label}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            {users.length === 0 && <p className="text-xs text-zinc-600 text-center py-4">No users found</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
