import { useState, useEffect, useCallback, useMemo } from "react";
import { useAuth } from "../App";
import { Building2, Users, Crown, Shield, UserPlus, Trash2, Mail } from "lucide-react";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL?.trim() || "";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 9, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const ROLE_META = {
  owner: { icon: Crown, color: T.amber, bg: "rgba(245,158,11,.12)" },
  admin: { icon: Shield, color: T.indigo, bg: "rgba(129,140,248,.12)" },
  member: { icon: Users, color: T.zinc, bg: "rgba(113,113,122,.1)" },
};

export default function Organization() {
  const { token } = useAuth();
  const [orgData, setOrgData] = useState({ org: null, members: [] });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [orgName, setOrgName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");

  const h = useMemo(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);

  const fetchOrg = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/kernel/organizations/me`, { headers: h });
      if (res.ok) setOrgData(await res.json());
    } catch {} finally { setLoading(false); }
  }, [h]);

  useEffect(() => { fetchOrg(); }, [fetchOrg]);

  const createOrg = async () => {
    if (!orgName.trim()) return;
    const res = await fetch(`${API}/api/kernel/organizations`, {
      method: "POST", headers: h,
      body: JSON.stringify({ name: orgName, slug: orgName.toLowerCase().replace(/\s+/g, "-") }),
    });
    if (res.ok) { toast.success("Organization created"); setCreating(false); setOrgName(""); fetchOrg(); }
  };

  const inviteMember = async () => {
    if (!inviteEmail.trim() || !orgData.org) return;
    const res = await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/invite`, {
      method: "POST", headers: h,
      body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
    });
    if (res.ok) { toast.success(`Invite sent to ${inviteEmail}`); setInviteEmail(""); }
  };

  const removeMember = async (targetUserId) => {
    if (!orgData.org) return;
    await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/members/${targetUserId}`, { method: "DELETE", headers: h });
    toast.success("Member removed"); fetchOrg();
  };

  const updateRole = async (targetUserId, newRole) => {
    if (!orgData.org) return;
    await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/members/${targetUserId}/role`, {
      method: "PUT", headers: h, body: JSON.stringify({ role: newRole }),
    });
    toast.success("Role updated"); fetchOrg();
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const org = orgData.org;
  const members = orgData.members || [];

  if (!org) {
    return (
      <div style={{ maxWidth: 480, margin: "0 auto", padding: "32px 24px", animation: "fadeUp .4s ease" }} data-testid="org-create">
        <style>{STYLES}</style>
        <div style={{ textAlign: "center", padding: "40px 20px" }}>
          <Building2 size={48} style={{ color: "rgba(255,255,255,.08)", marginBottom: 16 }} />
          <h2 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 22, fontWeight: 700, color: "#fff", marginBottom: 8 }}>Create Your Organization</h2>
          <p style={{ fontSize: 13, color: T.zinc, marginBottom: 28 }}>Set up a workspace to share agents, campaigns, and integrations with your team.</p>
          {!creating ? (
            <button onClick={() => setCreating(true)} data-testid="create-org-start"
              style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "10px 22px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
              <Building2 size={15} /> Create Organization
            </button>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <input value={orgName} onChange={e => setOrgName(e.target.value)} placeholder="Organization name…" style={formInput}
                data-testid="org-name-input"
                onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
                onBlur={e => e.target.style.borderColor = T.border} />
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={createOrg} data-testid="create-org-confirm"
                  style={{ flex: 1, padding: "9px 0", borderRadius: 9, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                  Create
                </button>
                <button onClick={() => setCreating(false)}
                  style={{ padding: "9px 16px", borderRadius: 9, background: T.glass, border: `1px solid ${T.border}`, color: T.zinc, fontSize: 13, cursor: "pointer" }}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="org-dashboard">
      <style>{STYLES}</style>

      {/* Org header */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 16, padding: "20px 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ width: 52, height: 52, borderRadius: 14, background: "rgba(129,140,248,.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Building2 size={26} style={{ color: T.indigo }} />
          </div>
          <div style={{ flex: 1 }}>
            <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 22, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 4 }}>{org.name}</h1>
            <p style={{ fontSize: 12, color: T.zinc, margin: 0 }}>{members.length} member{members.length !== 1 ? "s" : ""} · Created {new Date(org.created_at).toLocaleDateString()}</p>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", marginBottom: 3 }}>Shared Resources</p>
            <p style={{ fontSize: 12, color: "#a1a1aa" }}>Agents, Campaigns, Integrations</p>
          </div>
        </div>
      </div>

      {/* Invite */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 18px" }}>
        <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600, marginBottom: 10 }}>Invite Team Member</p>
        <div style={{ display: "flex", gap: 8 }}>
          <div style={{ position: "relative", flex: 1 }}>
            <Mail size={12} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
            <input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="Email address…"
              style={{ ...formInput, paddingLeft: 30 }} data-testid="invite-email-input"
              onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
              onBlur={e => e.target.style.borderColor = T.border} />
          </div>
          <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} data-testid="invite-role-select"
            style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 9, padding: "8px 12px", color: "#a1a1aa", fontSize: 12, outline: "none", fontFamily: "inherit", cursor: "pointer" }}>
            <option value="member" style={{ background: "#0f0f1a" }}>Member</option>
            <option value="admin" style={{ background: "#0f0f1a" }}>Admin</option>
          </select>
          <button onClick={inviteMember} data-testid="invite-btn"
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "8px 14px", borderRadius: 9, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: "pointer", flexShrink: 0 }}>
            <UserPlus size={13} /> Invite
          </button>
        </div>
      </div>

      {/* Members list */}
      <div>
        <p style={{ fontSize: 10, color: T.zinc, textTransform: "uppercase", letterSpacing: ".07em", fontWeight: 600, marginBottom: 10 }}>Team Members</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }} data-testid="members-list">
          {members.map((m, i) => {
            const rm = ROLE_META[m.role] || ROLE_META.member;
            const RoleIcon = rm.icon;
            return (
              <div key={i} data-testid={`member-${m.user_id}`}
                style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", borderRadius: 12, border: `1px solid ${T.border}`, background: T.glass }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: rm.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <RoleIcon size={16} style={{ color: rm.color }} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0, marginBottom: 2 }}>{m.name}</p>
                  <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{m.email} · Joined {new Date(m.joined_at).toLocaleDateString()}</p>
                </div>
                <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 20, background: rm.bg, color: rm.color }}>{m.role}</span>
                {m.role !== "owner" && (
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <select value={m.role} onChange={e => updateRole(m.user_id, e.target.value)}
                      style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 6, padding: "3px 8px", fontSize: 10, color: "#a1a1aa", outline: "none", fontFamily: "inherit", cursor: "pointer" }}>
                      <option value="member" style={{ background: "#0f0f1a" }}>Member</option>
                      <option value="admin" style={{ background: "#0f0f1a" }}>Admin</option>
                    </select>
                    <button onClick={() => removeMember(m.user_id)} data-testid={`remove-member-${m.user_id}`}
                      style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4, transition: "color .2s" }}
                      onMouseEnter={e => e.currentTarget.style.color = T.red}
                      onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
