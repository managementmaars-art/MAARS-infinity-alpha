import { useState, useEffect } from "react";
import { useAuth } from "../App";
import { Building2, Users, Crown, Shield, UserPlus, Trash2, Mail } from "lucide-react";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

export default function Organization() {
  const { token } = useAuth();
  const [orgData, setOrgData] = useState({ org: null, members: [] });
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [orgName, setOrgName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchOrg = async () => {
    try {
      const res = await fetch(`${API}/api/kernel/organizations/me`, { headers: h });
      if (res.ok) setOrgData(await res.json());
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchOrg(); }, [token]);

  const createOrg = async () => {
    if (!orgName.trim()) return;
    const res = await fetch(`${API}/api/kernel/organizations`, {
      method: "POST", headers: h,
      body: JSON.stringify({ name: orgName, slug: orgName.toLowerCase().replace(/\s+/g, "-") }),
    });
    if (res.ok) {
      toast.success("Organization created");
      setCreating(false);
      setOrgName("");
      fetchOrg();
    }
  };

  const inviteMember = async () => {
    if (!inviteEmail.trim() || !orgData.org) return;
    const res = await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/invite`, {
      method: "POST", headers: h,
      body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
    });
    if (res.ok) {
      toast.success(`Invite sent to ${inviteEmail}`);
      setInviteEmail("");
    }
  };

  const removeMember = async (targetUserId) => {
    if (!orgData.org) return;
    await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/members/${targetUserId}`, {
      method: "DELETE", headers: h,
    });
    toast.success("Member removed");
    fetchOrg();
  };

  const updateRole = async (targetUserId, newRole) => {
    if (!orgData.org) return;
    await fetch(`${API}/api/kernel/organizations/${orgData.org.org_id}/members/${targetUserId}/role`, {
      method: "PUT", headers: h,
      body: JSON.stringify({ role: newRole }),
    });
    toast.success("Role updated");
    fetchOrg();
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" /></div>;

  const org = orgData.org;
  const members = orgData.members || [];

  const roleIcons = { owner: Crown, admin: Shield, member: Users };
  const roleColors = { owner: "text-amber-400", admin: "text-indigo-400", member: "text-zinc-400" };

  // No org yet
  if (!org) {
    return (
      <div className="max-w-2xl mx-auto p-6 space-y-6" data-testid="org-create">
        <div className="text-center py-12">
          <Building2 className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Create Your Organization</h2>
          <p className="text-sm text-zinc-500 mb-6">Set up a workspace to share agents, campaigns, and integrations with your team.</p>
          {!creating ? (
            <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={() => setCreating(true)} data-testid="create-org-start">
              <Building2 className="w-4 h-4 mr-2" /> Create Organization
            </Button>
          ) : (
            <div className="max-w-sm mx-auto space-y-3">
              <input value={orgName} onChange={e => setOrgName(e.target.value)} placeholder="Organization name..."
                className="w-full bg-zinc-900/50 border border-white/5 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30"
                data-testid="org-name-input" />
              <div className="flex gap-2">
                <Button className="flex-1 bg-indigo-600 hover:bg-indigo-700" onClick={createOrg} data-testid="create-org-confirm">Create</Button>
                <Button variant="ghost" className="text-zinc-400" onClick={() => setCreating(false)}>Cancel</Button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6" data-testid="org-dashboard">
      {/* Org Header */}
      <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <Building2 className="w-7 h-7 text-indigo-400" />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-white">{org.name}</h1>
            <p className="text-xs text-zinc-500">{members.length} member{members.length !== 1 ? "s" : ""} &middot; Created {new Date(org.created_at).toLocaleDateString()}</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Shared Resources</p>
            <p className="text-xs text-zinc-400">Agents, Campaigns, Integrations</p>
          </div>
        </div>
      </div>

      {/* Invite Member */}
      <div className="bg-zinc-900/50 border border-white/5 rounded-xl p-4">
        <p className="text-xs font-semibold text-zinc-400 mb-3">Invite Team Member</p>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Mail className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="Email address..."
              className="w-full pl-8 pr-3 py-2 bg-zinc-800/50 border border-white/5 rounded-lg text-xs text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/30"
              data-testid="invite-email-input" />
          </div>
          <select value={inviteRole} onChange={e => setInviteRole(e.target.value)}
            className="bg-zinc-800/50 border border-white/5 rounded-lg px-3 text-xs text-zinc-300" data-testid="invite-role-select">
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
          <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 h-9 text-xs" onClick={inviteMember} data-testid="invite-btn">
            <UserPlus className="w-3.5 h-3.5 mr-1" /> Invite
          </Button>
        </div>
      </div>

      {/* Members List */}
      <div>
        <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Team Members</p>
        <div className="space-y-2" data-testid="members-list">
          {members.map((m, i) => {
            const RoleIcon = roleIcons[m.role] || Users;
            return (
              <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/5 bg-zinc-900/30" data-testid={`member-${m.user_id}`}>
                <div className="w-9 h-9 rounded-lg bg-zinc-800 flex items-center justify-center">
                  <RoleIcon className={`w-4 h-4 ${roleColors[m.role] || "text-zinc-400"}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white">{m.name}</p>
                  <p className="text-[10px] text-zinc-500">{m.email} &middot; Joined {new Date(m.joined_at).toLocaleDateString()}</p>
                </div>
                <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${m.role === "owner" ? "bg-amber-500/10 text-amber-400" : m.role === "admin" ? "bg-indigo-500/10 text-indigo-400" : "bg-zinc-800 text-zinc-400"}`}>
                  {m.role}
                </span>
                {m.role !== "owner" && (
                  <div className="flex gap-1">
                    <select value={m.role} onChange={e => updateRole(m.user_id, e.target.value)}
                      className="bg-zinc-800/50 border border-white/5 rounded px-1.5 py-0.5 text-[10px] text-zinc-400">
                      <option value="member">Member</option>
                      <option value="admin">Admin</option>
                    </select>
                    <button onClick={() => removeMember(m.user_id)} className="text-zinc-600 hover:text-red-400 transition-colors" data-testid={`remove-member-${m.user_id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
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
