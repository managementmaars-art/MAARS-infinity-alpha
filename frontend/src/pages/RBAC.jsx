import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Shield, Users, Check, X, ChevronRight, Lock } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  cyan: "#22d3ee",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const ROLE_COLORS = {
  admin: { color: T.red, bg: "rgba(239,68,68,.1)" },
  manager: { color: T.indigo, bg: "rgba(129,140,248,.1)" },
  operator: { color: T.cyan, bg: "rgba(34,211,238,.1)" },
  viewer: { color: T.zinc, bg: "rgba(113,113,122,.1)" },
  analyst: { color: T.cyan, bg: "rgba(34,211,238,.1)" },
};

const ROLE_META = {
  admin: { label: "Admin", description: "Full system access with all permissions" },
  manager: { label: "Manager", description: "Manage agents, workflows, and campaigns" },
  operator: { label: "Operator", description: "Execute workflows and campaigns" },
  viewer: { label: "Viewer", description: "Read-only access across the platform" },
  analyst: { label: "Analyst", description: "View analytics and reporting data" },
};

export default function RBAC() {
  const { token } = useAuth();
  const [config, setConfig] = useState({ roles: [], permissions: {} });
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState("admin");
  const [expandedUser, setExpandedUser] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/kernel/rbac/config`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : { roles: [], permissions: {} }),
      fetch(`${API}/api/kernel/rbac/users`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : []),
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
    if (res.ok) setUsers(prev => prev.map(u => u.user_id === userId ? { ...u, role } : u));
  };

  const roleNames = Array.isArray(config.roles) ? config.roles : Object.keys(config.roles || {});
  const permissionsMap = config.permissions || {};

  const roles = {};
  roleNames.forEach(name => {
    roles[name] = {
      label: ROLE_META[name]?.label || name.charAt(0).toUpperCase() + name.slice(1),
      description: ROLE_META[name]?.description || `${name} role`,
      permissions: permissionsMap[name] || [],
    };
  });

  const resourceSet = new Set();
  const actionSet = new Set();
  Object.values(permissionsMap).forEach(perms => {
    (perms || []).forEach(p => {
      if (p === "*") return;
      const [resource, action] = p.split(":");
      if (resource) resourceSet.add(resource);
      if (action && action !== "*") actionSet.add(action);
    });
  });
  const resources = Array.from(resourceSet);
  const actions = Array.from(actionSet).length > 0 ? Array.from(actionSet) : ["read", "write", "execute"];

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.red}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="rbac-page">
      <style>{STYLES}</style>

      <div>
        <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>Access Control (RBAC)</h1>
        <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Manage roles, permissions, and user access across the MAARS Command system</p>
      </div>

      {/* Role cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }} data-testid="role-cards">
        {Object.entries(roles).map(([key, role]) => {
          const rc = ROLE_COLORS[key] || ROLE_COLORS.viewer;
          const isSelected = selectedRole === key;
          const userCount = users.filter(u => u.role === key).length;
          return (
            <button key={key} onClick={() => setSelectedRole(key)} data-testid={`role-card-${key}`}
              style={{ textAlign: "left", padding: "14px 16px", borderRadius: 12, border: `1px solid ${isSelected ? "rgba(255,255,255,.15)" : T.border}`, background: isSelected ? rc.bg : T.glass, cursor: "pointer", transition: "all .2s" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                <div style={{ width: 10, height: 10, borderRadius: "50%", background: rc.color }} />
                <span style={{ fontSize: 13, fontWeight: 700, color: rc.color }}>{role.label}</span>
              </div>
              <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8 }}>{role.description}</p>
              <div style={{ display: "flex", gap: 10, fontSize: 10, color: "rgba(113,113,122,.7)" }}>
                <span>{(role.permissions || []).length === 1 && (role.permissions || [])[0] === "*" ? "All" : (role.permissions || []).length} perms</span>
                <span>{userCount} users</span>
              </div>
            </button>
          );
        })}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {/* Permission matrix */}
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }} data-testid="permission-matrix">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Lock size={13} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>Permission Matrix — {roles[selectedRole]?.label}</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {resources.map(resource => {
              const perms = roles[selectedRole]?.permissions || [];
              const hasWild = perms.includes("*");
              return (
                <div key={resource} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 8px", borderRadius: 7 }}>
                  <span style={{ fontSize: 11, color: "#d4d4d8", width: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flexShrink: 0 }}>{resource.replace(/_/g, " ")}</span>
                  <div style={{ display: "flex", gap: 4 }}>
                    {actions.map(action => {
                      const has = hasWild || perms.includes(`${resource}:${action}`);
                      return (
                        <div key={action} title={`${resource}:${action}`}
                          style={{ width: 40, height: 22, borderRadius: 5, display: "flex", alignItems: "center", justifyContent: "center", background: has ? "rgba(52,211,153,.12)" : "rgba(255,255,255,.04)", color: has ? T.green : T.zinc }}>
                          {has ? <Check size={11} /> : <X size={11} />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            <div style={{ display: "flex", alignItems: "center", gap: 8, paddingTop: 6 }}>
              <div style={{ width: 120 }} />
              {actions.map(a => <span key={a} style={{ width: 40, textAlign: "center", fontSize: 9, color: T.zinc }}>{a}</span>)}
            </div>
          </div>
        </div>

        {/* User assignments */}
        <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px" }} data-testid="user-assignments">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Users size={13} style={{ color: T.zinc }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>User Assignments</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {users.length === 0 ? (
              <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "16px 0" }}>No users found</p>
            ) : users.map(user => {
              const rc = ROLE_COLORS[user.role] || ROLE_COLORS.viewer;
              const isExpanded = expandedUser === user.user_id;
              const initials = user.name?.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase() || "??";
              return (
                <div key={user.user_id} data-testid={`user-${user.user_id}`}
                  style={{ background: "rgba(255,255,255,.025)", border: `1px solid ${T.border}`, borderRadius: 10, overflow: "hidden" }}>
                  <button onClick={() => setExpandedUser(isExpanded ? null : user.user_id)}
                    style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", background: "none", border: "none", cursor: "pointer", transition: "background .2s" }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,.02)"}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                    <div style={{ width: 28, height: 28, borderRadius: 8, background: "rgba(255,255,255,.08)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: "#d4d4d8" }}>
                      {initials}
                    </div>
                    <div style={{ flex: 1, textAlign: "left", minWidth: 0 }}>
                      <p style={{ fontSize: 12, color: "#fff", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.name}</p>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.email}</p>
                    </div>
                    <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: rc.bg, color: rc.color }}>{user.role}</span>
                    <ChevronRight size={12} style={{ color: T.zinc, transform: isExpanded ? "rotate(90deg)" : "none", transition: "transform .2s" }} />
                  </button>
                  {isExpanded && (
                    <div style={{ padding: "8px 14px 12px", borderTop: `1px solid ${T.border}` }}>
                      <p style={{ fontSize: 10, color: T.zinc, marginBottom: 7 }}>Change role:</p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {Object.entries(roles).map(([key, role]) => {
                          const c = ROLE_COLORS[key] || ROLE_COLORS.viewer;
                          const active = user.role === key;
                          return (
                            <button key={key} onClick={() => changeRole(user.user_id, key)} data-testid={`set-role-${key}-${user.user_id}`}
                              style={{ padding: "4px 10px", borderRadius: 7, border: `1px solid ${active ? c.color : T.border}`, background: active ? c.bg : "transparent", color: active ? c.color : T.zinc, fontSize: 10, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}>
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
          </div>
        </div>
      </div>
    </div>
  );
}
