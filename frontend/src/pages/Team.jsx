import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Label } from "../components/ui/label";
import {
  Bot, Users, UserPlus, Crown, Shield, User, Mail, Trash2, LogOut,
  LayoutDashboard, MessageSquare, ListTodo, Settings, Menu, X, Plus,
  CheckCircle, XCircle, Loader2, Share2, ChevronRight, Package,
  Activity, BarChart3
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { BrandFooter } from "../components/BrandFooter";

const Team = () => {
  const navigate = useNavigate();
  const { user, logout, token } = useAuth();
  const [teams, setTeams] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      const [teamsRes, invitesRes] = await Promise.all([
        fetch(`${API}/teams`, { headers }).catch(() => null),
        fetch(`${API}/teams/invites/pending`, { headers }).catch(() => null)
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
    } catch { /* silent */ } finally { setLoading(false); }
  };

  const createTeam = async () => {
    if (!teamName.trim()) return toast.error("Enter a team name");
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams`, { method: "POST", headers, body: JSON.stringify({ name: teamName }) });
      if (res.ok) {
        toast.success("Team created!");
        setCreateOpen(false);
        setTeamName("");
        fetchAll();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to create team");
      }
    } catch { toast.error("Failed to create team"); } finally { setProcessing(false); }
  };

  const inviteMember = async () => {
    if (!inviteEmail.trim()) return toast.error("Enter an email");
    if (!teams[0]) return toast.error("Create a team first");
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams/${teams[0].team_id}/invite`, {
        method: "POST", headers,
        body: JSON.stringify({ email: inviteEmail, role: inviteRole })
      });
      if (res.ok) {
        toast.success(`Invite sent to ${inviteEmail}`);
        setInviteOpen(false);
        setInviteEmail("");
        fetchAll();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Failed to send invite");
      }
    } catch { toast.error("Failed to send invite"); } finally { setProcessing(false); }
  };

  const respondInvite = async (inviteId, action) => {
    setProcessing(true);
    try {
      const res = await fetch(`${API}/teams/invites/${inviteId}/${action}`, { method: "POST", headers });
      if (res.ok) {
        toast.success(action === "accept" ? "You joined the team!" : "Invite declined");
        fetchAll();
      } else { toast.error("Failed to respond"); }
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
      const res = await fetch(`${API}/teams/${teamId}/members/${userId}`, {
        method: "PUT", headers,
        body: JSON.stringify({ role: newRole })
      });
      if (res.ok) { toast.success("Role updated"); fetchAll(); }
      else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Failed"); }
    } catch { toast.error("Failed to update role"); }
  };

  const deleteTeam = async (teamId) => {
    if (!window.confirm("Delete this team? All members will be removed.")) return;
    try {
      const res = await fetch(`${API}/teams/${teamId}`, { method: "DELETE", headers });
      if (res.ok) { toast.success("Team deleted"); fetchAll(); }
      else { toast.error("Failed to delete team"); }
    } catch { toast.error("Failed"); }
  };

  const getRoleIcon = (role) => {
    if (role === "owner") return <Crown className="w-3.5 h-3.5 text-amber-400" />;
    if (role === "admin") return <Shield className="w-3.5 h-3.5 text-blue-400" />;
    return <User className="w-3.5 h-3.5 text-zinc-400" />;
  };

  const getRoleBadge = (role) => {
    const styles = { owner: "bg-amber-500/15 text-amber-400 border-amber-500/20", admin: "bg-blue-500/15 text-blue-400 border-blue-500/20", member: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20" };
    return <Badge className={`${styles[role] || styles.member} text-[10px] border`}>{role}</Badge>;
  };

  const myTeam = teams[0];
  const isOwner = myTeam?.owner_id === user?.user_id;
  const myRole = myTeam?.members?.find(m => m.user_id === user?.user_id)?.role;
  const canManage = myRole === "owner" || myRole === "admin";

  const NavItem = ({ icon: Icon, label, to, active }) => (
    <Link to={to} className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${active ? "bg-indigo-500/20 text-indigo-400" : "text-zinc-400 hover:bg-white/5 hover:text-white"}`} data-testid={`nav-${label.toLowerCase()}`}>
      <Icon className="w-5 h-5" /><span className="font-medium">{label}</span>
    </Link>
  );

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center"><Bot className="w-5 h-5 text-white" /></div>
          <div><span className="text-lg font-bold text-white font-['Outfit']">MAARS Command</span><p className="text-[9px] text-zinc-500 -mt-1">by MAARS Global Corp</p></div>
        </Link>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        <NavItem icon={LayoutDashboard} label="Dashboard" to="/dashboard" />
        <NavItem icon={MessageSquare} label="Chat" to="/chat" />
        <NavItem icon={Users} label="Agents" to="/agents" />
        <NavItem icon={Package} label="Products" to="/products" />
        <NavItem icon={ListTodo} label="Tasks" to="/tasks" />
        <NavItem icon={Users} label="Team" to="/team" active />
        <NavItem icon={Settings} label="Settings" to="/settings" />
      </nav>
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            {user?.picture ? <img src={user.picture} alt="" className="w-full h-full rounded-full object-cover" /> : <span className="text-white font-semibold">{user?.name?.charAt(0) || "U"}</span>}
          </div>
          <div className="flex-1 min-w-0"><p className="text-sm font-medium text-white truncate">{user?.name}</p><p className="text-xs text-zinc-500 truncate">{user?.email}</p></div>
        </div>
        <Button variant="ghost" className="w-full justify-start text-zinc-400 hover:text-white hover:bg-white/5 mt-2" onClick={async () => { await logout(); navigate("/"); }}>
          <LogOut className="w-5 h-5 mr-3" />Sign Out
        </Button>
      </div>
    </div>
  );

  if (loading) return <div className="min-h-screen bg-background flex items-center justify-center"><div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="min-h-screen bg-background" data-testid="team-page">
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="flex items-center justify-between h-16 px-4">
          <Link to="/dashboard" className="flex items-center gap-2"><div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center"><Bot className="w-5 h-5 text-white" /></div><span className="text-lg font-bold text-white font-['Outfit']">MAARS Command</span></Link>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-zinc-400">{sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}</button>
        </div>
      </div>
      {sidebarOpen && <div className="lg:hidden fixed inset-0 z-40"><div className="absolute inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} /><div className="absolute left-0 top-0 bottom-0 w-64 bg-zinc-900 border-r border-white/10"><Sidebar /></div></div>}
      <div className="hidden lg:block fixed left-0 top-0 bottom-0 w-64 bg-zinc-900/50 border-r border-white/10"><Sidebar /></div>

      <div className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1 font-['Outfit']">Team</h1>
              <p className="text-zinc-400 text-sm">Collaborate with your team members</p>
            </div>
            {!myTeam && (
              <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="create-team-btn"><Plus className="w-4 h-4 mr-2" />Create Team</Button>
                </DialogTrigger>
                <DialogContent className="bg-zinc-900 border-white/10">
                  <DialogHeader><DialogTitle className="text-white font-['Outfit']">Create a Team</DialogTitle></DialogHeader>
                  <div className="space-y-4 mt-2">
                    <div className="space-y-2"><Label className="text-zinc-300">Team Name</Label><Input value={teamName} onChange={e => setTeamName(e.target.value)} placeholder="e.g. MAARS Global Team" className="bg-zinc-800/50 border-white/10" data-testid="team-name-input" /></div>
                    <Button onClick={createTeam} disabled={processing} className="w-full bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="confirm-create-team">{processing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}Create Team</Button>
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>

          {/* Pending Invites */}
          {pendingInvites.length > 0 && (
            <Card className="bg-indigo-500/5 border-indigo-500/20">
              <CardHeader className="pb-3"><CardTitle className="text-white text-base font-['Outfit'] flex items-center gap-2"><Mail className="w-4 h-4 text-indigo-400" />Pending Invitations ({pendingInvites.length})</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {pendingInvites.map(inv => (
                  <div key={inv.invite_id} className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/50" data-testid={`invite-${inv.invite_id}`}>
                    <div>
                      <p className="text-white text-sm font-medium">{inv.team_name}</p>
                      <p className="text-zinc-500 text-xs">Invited by {inv.invited_by_name} as {inv.role}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => respondInvite(inv.invite_id, "accept")} disabled={processing} className="bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 h-8" data-testid={`accept-invite-${inv.invite_id}`}><CheckCircle className="w-3.5 h-3.5 mr-1" />Accept</Button>
                      <Button size="sm" variant="ghost" onClick={() => respondInvite(inv.invite_id, "decline")} disabled={processing} className="text-red-400 hover:bg-red-500/10 h-8" data-testid={`decline-invite-${inv.invite_id}`}><XCircle className="w-3.5 h-3.5 mr-1" />Decline</Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Team Card */}
          {myTeam ? (
            <>
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white text-lg font-['Outfit'] flex items-center gap-2"><Users className="w-5 h-5 text-indigo-400" />{myTeam.name}</CardTitle>
                    <div className="flex gap-2">
                      {canManage && (
                        <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
                          <DialogTrigger asChild><Button size="sm" className="bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 h-8" data-testid="invite-member-btn"><UserPlus className="w-3.5 h-3.5 mr-1" />Invite</Button></DialogTrigger>
                          <DialogContent className="bg-zinc-900 border-white/10">
                            <DialogHeader><DialogTitle className="text-white font-['Outfit']">Invite Team Member</DialogTitle></DialogHeader>
                            <div className="space-y-4 mt-2">
                              <div className="space-y-2"><Label className="text-zinc-300">Email Address</Label><Input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="colleague@company.com" type="email" className="bg-zinc-800/50 border-white/10" data-testid="invite-email-input" /></div>
                              <div className="space-y-2">
                                <Label className="text-zinc-300">Role</Label>
                                <div className="flex gap-2">
                                  {["member", "admin"].map(r => (
                                    <button key={r} onClick={() => setInviteRole(r)} className={`flex-1 p-3 rounded-lg border text-sm transition-colors ${inviteRole === r ? "bg-indigo-500/15 border-indigo-500/30 text-indigo-400" : "bg-zinc-800/50 border-white/5 text-zinc-400 hover:border-white/10"}`} data-testid={`invite-role-${r}`}>
                                      <div className="flex items-center gap-2 justify-center">{r === "admin" ? <Shield className="w-4 h-4" /> : <User className="w-4 h-4" />}<span className="capitalize font-medium">{r}</span></div>
                                      <p className="text-[10px] text-zinc-500 mt-1">{r === "admin" ? "Manage agents & members" : "Chat & create tasks"}</p>
                                    </button>
                                  ))}
                                </div>
                              </div>
                              <Button onClick={inviteMember} disabled={processing} className="w-full bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="send-invite-btn">{processing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Mail className="w-4 h-4 mr-2" />}Send Invite</Button>
                            </div>
                          </DialogContent>
                        </Dialog>
                      )}
                      {isOwner && <Button size="sm" variant="ghost" onClick={() => deleteTeam(myTeam.team_id)} className="text-red-400 hover:bg-red-500/10 h-8" data-testid="delete-team-btn"><Trash2 className="w-3.5 h-3.5" /></Button>}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {myTeam.members.map(member => (
                      <div key={member.user_id} className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/50 transition-colors" data-testid={`team-member-${member.user_id}`}>
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0">
                          <span className="text-white font-semibold text-sm">{member.name?.charAt(0) || "?"}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-white truncate">{member.name}</p>
                            {getRoleBadge(member.role)}
                          </div>
                          <p className="text-xs text-zinc-500 truncate">{member.email}</p>
                        </div>
                        {isOwner && member.user_id !== user?.user_id && (
                          <div className="flex items-center gap-1 shrink-0">
                            <select
                              value={member.role}
                              onChange={e => updateRole(myTeam.team_id, member.user_id, e.target.value)}
                              className="h-7 px-2 text-xs rounded bg-zinc-800 border border-white/10 text-zinc-300"
                              data-testid={`role-select-${member.user_id}`}
                            >
                              <option value="member">Member</option>
                              <option value="admin">Admin</option>
                            </select>
                            <Button size="sm" variant="ghost" onClick={() => removeMember(myTeam.team_id, member.user_id, member.name)} className="text-red-400 hover:bg-red-500/10 h-7 w-7 p-0" data-testid={`remove-member-${member.user_id}`}>
                              <Trash2 className="w-3.5 h-3.5" />
                            </Button>
                          </div>
                        )}
                        {!isOwner && member.user_id === user?.user_id && member.role !== "owner" && (
                          <Button size="sm" variant="ghost" onClick={() => removeMember(myTeam.team_id, member.user_id, "yourself")} className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10 h-7 text-xs" data-testid="leave-team-btn">
                            <LogOut className="w-3.5 h-3.5 mr-1" />Leave
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Shared Chats */}
              <Card className="bg-zinc-900/50 border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-white text-base font-['Outfit'] flex items-center gap-2"><Share2 className="w-4 h-4 text-emerald-400" />Shared Chats ({sharedChats.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  {sharedChats.length === 0 ? (
                    <p className="text-zinc-500 text-sm text-center py-4">No shared chats yet. Share a chat from the Chat page to make it visible to your team.</p>
                  ) : (
                    <div className="space-y-2">
                      {sharedChats.map(chat => (
                        <button key={chat.chat_id} onClick={() => navigate(`/chat/${chat.agent_id}`)} className="w-full flex items-center gap-3 p-3 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/50 transition-colors text-left" data-testid={`shared-chat-${chat.chat_id}`}>
                          <MessageSquare className="w-4 h-4 text-indigo-400 shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{chat.title || "Untitled chat"}</p>
                            <p className="text-xs text-zinc-500">by {chat.owner_name}</p>
                          </div>
                          <ChevronRight className="w-4 h-4 text-zinc-600" />
                        </button>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Team Stats */}
              {teamStats && (
                <Card className="bg-zinc-900/50 border-white/10" data-testid="team-stats-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white text-base font-['Outfit'] flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-amber-400" />Team Stats
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-3 mb-4">
                      <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-center">
                        <p className="text-lg font-bold text-white">{teamStats.member_count}</p>
                        <p className="text-[10px] text-indigo-400">Members</p>
                      </div>
                      <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
                        <p className="text-lg font-bold text-white">{teamStats.total_chats}</p>
                        <p className="text-[10px] text-emerald-400">Total Chats</p>
                      </div>
                      <div className="p-3 rounded-lg bg-violet-500/10 border border-violet-500/20 text-center">
                        <p className="text-lg font-bold text-white">{teamStats.shared_chats}</p>
                        <p className="text-[10px] text-violet-400">Shared</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      {teamStats.members?.map(m => (
                        <div key={m.user_id} className="flex items-center justify-between p-2 rounded-lg bg-white/5" data-testid={`stat-member-${m.user_id}`}>
                          <div className="flex items-center gap-2 min-w-0">
                            {getRoleIcon(m.role)}
                            <span className="text-sm text-white truncate">{m.name}</span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <span className="text-xs text-zinc-400">{m.chats} chats</span>
                            {getRoleBadge(m.role)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Team Activity Feed */}
              {teamActivity.length > 0 && (
                <Card className="bg-zinc-900/50 border-white/10" data-testid="team-activity-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white text-base font-['Outfit'] flex items-center gap-2">
                      <Activity className="w-4 h-4 text-cyan-400" />Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-[400px] overflow-y-auto">
                      {teamActivity.map((item, i) => (
                        <button
                          key={`${item.chat_id}-${i}`}
                          onClick={() => item.agent_id && navigate(`/chat/${item.agent_id}?chat=${item.chat_id}`)}
                          className="w-full flex items-start gap-3 p-3 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/50 transition-colors text-left"
                          data-testid={`activity-item-${i}`}
                        >
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
                            item.type === "shared_chat" ? "bg-emerald-500/15" : "bg-indigo-500/15"
                          }`}>
                            {item.type === "shared_chat" ? (
                              <Share2 className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{item.title}</p>
                            <p className="text-xs text-zinc-500">{item.user_name} {item.timestamp ? `- ${new Date(item.timestamp).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}` : ""}</p>
                          </div>
                          <ChevronRight className="w-4 h-4 text-zinc-600 shrink-0 mt-1" />
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : pendingInvites.length === 0 ? (
            <div className="p-12 rounded-xl border border-dashed border-white/10 text-center">
              <Users className="w-14 h-14 text-zinc-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2 font-['Outfit']">No Team Yet</h3>
              <p className="text-zinc-400 mb-6 max-w-md mx-auto">Create a team to invite colleagues, share chats, and collaborate with your AI agents together.</p>
              <Button onClick={() => setCreateOpen(true)} className="bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="empty-create-team-btn"><Plus className="w-4 h-4 mr-2" />Create Your Team</Button>
            </div>
          ) : null}
        </div>
      </div>
      <div className="lg:ml-64"><BrandFooter /></div>
    </div>
  );
};

export default Team;
