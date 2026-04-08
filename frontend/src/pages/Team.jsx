import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Users, UserPlus, Crown, Shield, User, Mail, Trash2, LogOut,
  MessageSquare, Plus, CheckCircle, XCircle, Share2, ChevronRight,
  Activity, BarChart3, X
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  amber: "#f59e0b",
  green: "#34d399",
  cyan: "#22d3ee",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
`;

const ROLE_META = {
  owner: { icon: Crown, color: T.amber, bg: "rgba(245,158,11,.12)" },
  admin: { icon: Shield, color: "#60a5fa", bg: "rgba(96,165,250,.12)" },
  member: { icon: User, color: T.zinc, bg: "rgba(113,113,122,.1)" },
};

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const Modal = ({ title, children, onClose }) => (
  <div style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center" }}>
    <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,.6)", backdropFilter: "blur(4px)" }} onClick={onClose} />
    <div style={{ position: "relative", background: "#0f0f1a", border: `1px solid ${T.border}`, borderRadius: 16, padding: "24px", width: "100%", maxWidth: 440, margin: "0 16px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
        <h3 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 17, fontWeight: 700, color: "#fff", margin: 0 }}>{title}</h3>
        <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4 }}><X size={16} /></button>
      </div>
      {children}
    </div>
  </div>
);

const RoleBadge = ({ role }) => {
  const rm = ROLE_META[role] || ROLE_META.member;
  return <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20, background: rm.bg, color: rm.color }}>{role}</span>;
};

const Team = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [teams, setTeams] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [teamName, setTeamName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");
  const [processing, setProcessing] = useState(false);
  const [sharedChats, setSharedChats] = useState([]);
  const [teamActivity, setTeamActivity] = useState([]);
  const [teamStats, setTeamStats] = useState(null);

  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : {};

  const fetchAll = async () => {
    try {
      const [teamsRes, invitesRes] = await Promise.all([
        fetch(`${API}/teams`, { headers }).catch(() => null),
        fetch(`${API}/teams/invites/pending`, { headers }).catch(() => null),
      ]);
      if (teamsRes?.ok) {
        const t = await teamsRes.json();
        setTeams(t);
        if (t.length > 0) {
          const [sharedRes, activityRes, statsRes] = await Promise.all([
            fetch(`${API}/teams/${t[0].team_id}/shared-chats`, { headers }).catch(() => null),
            fetch(`${API}/teams/${t[0].team_id}/activity?limit=20`, { headers }).catch(() => null),
            fetch(`${API}/teams/${t[0].team_id}/stats`, { headers }).catch(() => null),
          ]);
          if (sharedRes?.ok) setSharedChats(await sharedRes.json());
          if (activityRes?.ok) setTeamActivity(await activityRes.json());
          if (statsRes?.ok) setTeamStats(await statsRes.json());
        }
      }
      if (invitesRes?.ok) setPendingInvites(await invitesRes.json());
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const createTeam = async () => {
    if (!teamName.trim()) return toast.error("Enter a team name");
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams`, { method: "POST", headers, body: JSON.stringify({ name: teamName }) });
      if (res.ok) { toast.success("Team created!"); setCreateOpen(false); setTeamName(""); fetchAll(); }
      else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Failed to create team"); }
    } catch { toast.error("Failed to create team"); } finally { setProcessing(false); }
  };

  const inviteMember = async () => {
    if (!inviteEmail.trim()) return toast.error("Enter an email");
    if (!teams[0]) return toast.error("Create a team first");
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams/${teams[0].team_id}/invite`, { method: "POST", headers, body: JSON.stringify({ email: inviteEmail, role: inviteRole }) });
      if (res.ok) { toast.success(`Invite sent to ${inviteEmail}`); setInviteOpen(false); setInviteEmail(""); fetchAll(); }
      else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Failed to send invite"); }
    } catch { toast.error("Failed to send invite"); } finally { setProcessing(false); }
  };

  const respondInvite = async (inviteId, action) => {
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams/invites/${inviteId}/${action}`, { method: "POST", headers });
      if (res.ok) { toast.success(action === "accept" ? "You joined the team!" : "Invite declined"); fetchAll(); }
      else toast.error("Failed to respond");
    } catch { toast.error("Failed to respond"); } finally { setProcessing(false); }
  };

  const removeMember = async (teamId, userId, name) => {
    if (!window.confirm(`Remove ${name} from the team?`)) return;
    try {
      const res = await fetch(`${API}/teams/${teamId}/members/${userId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Member removed"); fetchAll(); }
      else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Failed"); }
    } catch { toast.error("Failed to remove member"); }
  };

  const updateRole = async (teamId, userId, newRole) => {
    try {
      const res = await fetch(`${API}/teams/${teamId}/members/${userId}`, { method: "PUT", headers, body: JSON.stringify({ role: newRole }) });
      if (res.ok) { toast.success("Role updated"); fetchAll(); }
    } catch { toast.error("Failed to update role"); }
  };

  const deleteTeam = async (teamId) => {
    if (!window.confirm("Delete this team? All members will be removed.")) return;
    try {
      const res = await fetch(`${API}/teams/${teamId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Team deleted"); fetchAll(); }
      else toast.error("Failed to delete team");
    } catch { toast.error("Failed"); }
  };

  const myTeam = teams[0];
  const isOwner = myTeam?.owner_id === user?.user_id;
  const myRole = myTeam?.members?.find(m => m.user_id === user?.user_id)?.role;
  const canManage = myRole === "owner" || myRole === "admin";

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.indigo}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const glassCard = { background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "16px 20px" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, animation: "fadeUp .4s ease" }} data-testid="team-page">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }}>Team</h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Collaborate with your team members</p>
        </div>
        {!myTeam && (
          <button onClick={() => setCreateOpen(true)} data-testid="create-team-btn"
            style={{ display: "flex", alignItems: "center", gap: 6, padding: "9px 18px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
            <Plus size={14} /> Create Team
          </button>
        )}
      </div>

      {/* Pending invites */}
      {pendingInvites.length > 0 && (
        <div style={{ ...glassCard, borderColor: "rgba(129,140,248,.2)", background: "rgba(129,140,248,.04)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <Mail size={14} style={{ color: T.indigo }} />
            <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Pending Invitations ({pendingInvites.length})</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {pendingInvites.map(inv => (
              <div key={inv.invite_id} data-testid={`invite-${inv.invite_id}`}
                style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.03)" }}>
                <div>
                  <p style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0, marginBottom: 2 }}>{inv.team_name}</p>
                  <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>Invited by {inv.invited_by_name} as {inv.role}</p>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => respondInvite(inv.invite_id, "accept")} disabled={processing} data-testid={`accept-invite-${inv.invite_id}`}
                    style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: "rgba(52,211,153,.12)", border: `1px solid rgba(52,211,153,.25)`, color: T.green, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                    <CheckCircle size={12} /> Accept
                  </button>
                  <button onClick={() => respondInvite(inv.invite_id, "decline")} disabled={processing} data-testid={`decline-invite-${inv.invite_id}`}
                    style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: "transparent", border: `1px solid ${T.border}`, color: T.red, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                    <XCircle size={12} /> Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Team card */}
      {myTeam ? (
        <>
          <div style={glassCard}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Users size={18} style={{ color: T.indigo }} />
                <span style={{ fontSize: 17, fontWeight: 700, color: "#fff" }}>{myTeam.name}</span>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {canManage && (
                  <button onClick={() => setInviteOpen(true)} data-testid="invite-member-btn"
                    style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 8, background: "rgba(129,140,248,.1)", border: `1px solid rgba(129,140,248,.2)`, color: T.indigo, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                    <UserPlus size={12} /> Invite
                  </button>
                )}
                {isOwner && (
                  <button onClick={() => deleteTeam(myTeam.team_id)} data-testid="delete-team-btn"
                    style={{ padding: "5px 10px", borderRadius: 8, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 11, cursor: "pointer", display: "flex", alignItems: "center" }}
                    onMouseEnter={e => e.currentTarget.style.color = T.red}
                    onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {myTeam.members?.map(member => {
                const rm = ROLE_META[member.role] || ROLE_META.member;
                return (
                  <div key={member.user_id} data-testid={`team-member-${member.user_id}`}
                    style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.025)", transition: "background .2s" }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,.04)"}
                    onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,.025)"}>
                    <div style={{ width: 34, height: 34, borderRadius: "50%", background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>{member.name?.charAt(0) || "?"}</span>
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{member.name}</span>
                        <RoleBadge role={member.role} />
                      </div>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{member.email}</p>
                    </div>
                    {isOwner && member.user_id !== user?.user_id && (
                      <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
                        <select value={member.role} onChange={e => updateRole(myTeam.team_id, member.user_id, e.target.value)}
                          data-testid={`role-select-${member.user_id}`}
                          style={{ background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`, borderRadius: 6, padding: "3px 8px", fontSize: 10, color: "#a1a1aa", outline: "none", fontFamily: "inherit", cursor: "pointer" }}>
                          <option value="member" style={{ background: "#0f0f1a" }}>Member</option>
                          <option value="admin" style={{ background: "#0f0f1a" }}>Admin</option>
                        </select>
                        <button onClick={() => removeMember(myTeam.team_id, member.user_id, member.name)} data-testid={`remove-member-${member.user_id}`}
                          style={{ background: "none", border: "none", cursor: "pointer", color: T.zinc, padding: 4 }}
                          onMouseEnter={e => e.currentTarget.style.color = T.red}
                          onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                          <Trash2 size={13} />
                        </button>
                      </div>
                    )}
                    {!isOwner && member.user_id === user?.user_id && member.role !== "owner" && (
                      <button onClick={() => removeMember(myTeam.team_id, member.user_id, "yourself")} data-testid="leave-team-btn"
                        style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 7, background: "transparent", border: `1px solid ${T.border}`, color: T.zinc, fontSize: 11, cursor: "pointer" }}>
                        <LogOut size={11} /> Leave
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Shared Chats */}
          <div style={glassCard}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Share2 size={14} style={{ color: T.green }} />
              <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Shared Chats ({sharedChats.length})</span>
            </div>
            {sharedChats.length === 0 ? (
              <p style={{ fontSize: 12, color: T.zinc, textAlign: "center", padding: "16px 0" }}>No shared chats yet. Share a chat from the Chat page to make it visible to your team.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {sharedChats.map(chat => (
                  <button key={chat.chat_id} onClick={() => navigate(`/chat/${chat.agent_id}`)} data-testid={`shared-chat-${chat.chat_id}`}
                    style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.025)", border: "none", cursor: "pointer", textAlign: "left", transition: "background .2s" }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,.04)"}
                    onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,.025)"}>
                    <MessageSquare size={14} style={{ color: T.indigo, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontSize: 13, color: "#fff", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{chat.title || "Untitled chat"}</p>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>by {chat.owner_name}</p>
                    </div>
                    <ChevronRight size={13} style={{ color: T.zinc }} />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Stats */}
          {teamStats && (
            <div style={glassCard} data-testid="team-stats-card">
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <BarChart3 size={14} style={{ color: T.amber }} />
                <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Team Stats</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginBottom: 14 }}>
                {[
                  { label: "Members", value: teamStats.member_count, color: T.indigo, bg: "rgba(129,140,248,.1)" },
                  { label: "Total Chats", value: teamStats.total_chats, color: T.green, bg: "rgba(52,211,153,.1)" },
                  { label: "Shared", value: teamStats.shared_chats, color: "#a78bfa", bg: "rgba(167,139,250,.1)" },
                ].map(s => (
                  <div key={s.label} style={{ padding: "12px 14px", borderRadius: 10, background: s.bg, textAlign: "center" }}>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#fff" }}>{s.value}</div>
                    <div style={{ fontSize: 10, color: s.color }}>{s.label}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                {teamStats.members?.map(m => {
                  const rm = ROLE_META[m.role] || ROLE_META.member;
                  const RoleIcon = rm.icon;
                  return (
                    <div key={m.user_id} data-testid={`stat-member-${m.user_id}`}
                      style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "7px 10px", borderRadius: 8, background: "rgba(255,255,255,.025)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 7, minWidth: 0 }}>
                        <RoleIcon size={12} style={{ color: rm.color }} />
                        <span style={{ fontSize: 12, color: "#fff", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{m.name}</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                        <span style={{ fontSize: 11, color: T.zinc }}>{m.chats} chats</span>
                        <RoleBadge role={m.role} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Activity */}
          {teamActivity.length > 0 && (
            <div style={glassCard} data-testid="team-activity-card">
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <Activity size={14} style={{ color: T.cyan }} />
                <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Recent Activity</span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 5, maxHeight: 360, overflowY: "auto" }}>
                {teamActivity.map((item, i) => (
                  <button key={`${item.chat_id}-${i}`} onClick={() => item.agent_id && navigate(`/chat/${item.agent_id}?chat=${item.chat_id}`)}
                    data-testid={`activity-item-${i}`}
                    style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 12px", borderRadius: 10, background: "rgba(255,255,255,.025)", border: "none", cursor: "pointer", textAlign: "left" }}
                    onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,.04)"}
                    onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,.025)"}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", background: item.type === "shared_chat" ? "rgba(52,211,153,.12)" : "rgba(129,140,248,.12)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      {item.type === "shared_chat" ? <Share2 size={12} style={{ color: T.green }} /> : <MessageSquare size={12} style={{ color: T.indigo }} />}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontSize: 12, color: "#fff", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.title}</p>
                      <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{item.user_name}{item.timestamp ? ` · ${new Date(item.timestamp).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}` : ""}</p>
                    </div>
                    <ChevronRight size={12} style={{ color: T.zinc, flexShrink: 0, marginTop: 2 }} />
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      ) : pendingInvites.length === 0 ? (
        <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
          <Users size={52} style={{ color: "rgba(255,255,255,.06)", marginBottom: 16 }} />
          <h3 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 20, fontWeight: 700, color: "#fff", marginBottom: 8 }}>No Team Yet</h3>
          <p style={{ fontSize: 13, color: T.zinc, marginBottom: 24, maxWidth: 380, margin: "0 auto 24px" }}>Create a team to invite colleagues, share chats, and collaborate with your AI agents together.</p>
          <button onClick={() => setCreateOpen(true)} data-testid="empty-create-team-btn"
            style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "10px 22px", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
            <Plus size={14} /> Create Your Team
          </button>
        </div>
      ) : null}

      {/* Create team modal */}
      {createOpen && (
        <Modal title="Create a Team" onClose={() => setCreateOpen(false)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Team Name</label>
              <input value={teamName} onChange={e => setTeamName(e.target.value)} placeholder="e.g. MAARS Global Team" style={formInput}
                data-testid="team-name-input"
                onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
                onBlur={e => e.target.style.borderColor = T.border} />
            </div>
            <button onClick={createTeam} disabled={processing} data-testid="confirm-create-team"
              style={{ width: "100%", padding: "10px 0", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: processing ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 7 }}>
              {processing ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : null}
              Create Team
            </button>
          </div>
        </Modal>
      )}

      {/* Invite modal */}
      {inviteOpen && (
        <Modal title="Invite Team Member" onClose={() => setInviteOpen(false)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 5, textTransform: "uppercase", letterSpacing: ".05em" }}>Email Address</label>
              <input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="colleague@company.com" type="email" style={formInput}
                data-testid="invite-email-input"
                onFocus={e => e.target.style.borderColor = "rgba(129,140,248,.5)"}
                onBlur={e => e.target.style.borderColor = T.border} />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".05em" }}>Role</label>
              <div style={{ display: "flex", gap: 8 }}>
                {["member", "admin"].map(r => (
                  <button key={r} onClick={() => setInviteRole(r)} data-testid={`invite-role-${r}`}
                    style={{ flex: 1, padding: "10px 14px", borderRadius: 10, border: `1px solid ${inviteRole === r ? "rgba(129,140,248,.3)" : T.border}`, background: inviteRole === r ? "rgba(129,140,248,.08)" : T.glass, cursor: "pointer", textAlign: "center" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 4 }}>
                      {r === "admin" ? <Shield size={13} style={{ color: T.indigo }} /> : <User size={13} style={{ color: T.zinc }} />}
                      <span style={{ fontSize: 12, fontWeight: 600, color: inviteRole === r ? T.indigo : "#a1a1aa", textTransform: "capitalize" }}>{r}</span>
                    </div>
                    <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{r === "admin" ? "Manage agents & members" : "Chat & create tasks"}</p>
                  </button>
                ))}
              </div>
            </div>
            <button onClick={inviteMember} disabled={processing} data-testid="send-invite-btn"
              style={{ width: "100%", padding: "10px 0", borderRadius: 10, background: `linear-gradient(135deg, ${T.violet}, ${T.indigo})`, border: "none", color: "#fff", fontSize: 13, fontWeight: 700, cursor: processing ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 7 }}>
              {processing ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> : <Mail size={13} />}
              Send Invite
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Team;
