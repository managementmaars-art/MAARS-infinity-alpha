import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  Bell, CheckCheck, Trash2, MessageSquare, CreditCard,
  UserPlus, Sparkles, AlertTriangle, CheckCircle
} from "lucide-react";

/* ─── Type config ─────────────────────────────────────────────────────────── */
const TYPE_CONFIG = {
  welcome:          { Icon: Sparkles,     color: "#4fd1c5", bg: "rgba(79,209,197,0.12)"  },
  credits_low:      { Icon: AlertTriangle,color: "#f59e0b", bg: "rgba(245,158,11,0.12)"  },
  team_join:        { Icon: UserPlus,     color: "#34d399", bg: "rgba(52,211,153,0.12)"  },
  team_invite:      { Icon: UserPlus,     color: "#4fd1c5", bg: "rgba(79,209,197,0.12)"  },
  team_share:       { Icon: MessageSquare,color: "#a78bfa", bg: "rgba(167,139,250,0.12)" },
  project_complete: { Icon: CheckCircle,  color: "#34d399", bg: "rgba(52,211,153,0.12)"  },
  report_ready:     { Icon: MessageSquare,color: "#a78bfa", bg: "rgba(167,139,250,0.12)" },
  subscription:     { Icon: CreditCard,   color: "#f472b6", bg: "rgba(244,114,182,0.12)" },
  default:          { Icon: Bell,         color: "#475569", bg: "rgba(71,85,105,0.12)"   },
};

const getConfig = (type) => TYPE_CONFIG[type] || TYPE_CONFIG.default;

const getTimeAgo = (ts) => {
  if (!ts) return "";
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60)    return "just now";
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

/* ─── Component ───────────────────────────────────────────────────────────── */
const NotificationCenter = () => {
  const { token } = useAuth();
  const navigate  = useNavigate();
  const [open,          setOpen]          = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unread,        setUnread]        = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API}/notifications`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setUnread(data.unread_count || 0);
      }
    } catch {}
  };

  const markRead = async (id) => {
    setNotifications(prev => prev.map(n => n.notification_id === id ? { ...n, read: true } : n));
    setUnread(prev => Math.max(0, prev - 1));
    try {
      await fetch(`${API}/notifications/${id}/read`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` },
      });
    } catch {}
  };

  const markAllRead = async () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnread(0);
    try {
      await fetch(`${API}/notifications/read-all`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` },
      });
    } catch {}
  };

  const clearRead = async () => {
    setNotifications(prev => prev.filter(n => !n.read));
    try {
      await fetch(`${API}/notifications/clear`, {
        method: "DELETE", headers: { Authorization: `Bearer ${token}` },
      });
    } catch {}
  };

  const handleClick = (notif) => {
    if (!notif.read) markRead(notif.notification_id);
    if (notif.link) { navigate(notif.link); setOpen(false); }
  };

  return (
    <div ref={ref} style={{ position: "relative" }} data-testid="notification-center">
      {/* ── Bell trigger ─────────────────────────── */}
      <button
        onClick={() => setOpen(o => !o)}
        data-testid="notification-bell"
        style={{
          position: "relative", display: "flex", alignItems: "center", justifyContent: "center",
          width: 40, height: 40, borderRadius: 11,
          background: open ? "rgba(79,209,197,0.1)" : "rgba(255,255,255,0.04)",
          border: `1px solid ${open ? "rgba(79,209,197,0.25)" : "rgba(255,255,255,0.08)"}`,
          color: open ? "#4fd1c5" : "#64748b",
          cursor: "pointer", transition: "all 0.2s",
        }}
        onMouseEnter={e => { if (!open) { e.currentTarget.style.background = "rgba(255,255,255,0.07)"; e.currentTarget.style.color = "#e2e8f0"; } }}
        onMouseLeave={e => { if (!open) { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.color = "#64748b"; } }}
      >
        <Bell style={{ width: 17, height: 17 }} />
        {unread > 0 && (
          <span
            data-testid="notification-badge"
            style={{
              position: "absolute", top: -4, right: -4,
              minWidth: 18, height: 18, borderRadius: 9,
              background: "linear-gradient(135deg, #f87171, #ef4444)",
              color: "#fff", fontSize: 10, fontWeight: 700,
              display: "flex", alignItems: "center", justifyContent: "center",
              padding: "0 4px", border: "2px solid #030712",
              boxShadow: "0 0 8px rgba(239,68,68,0.5)",
            }}>
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {/* ── Dropdown ─────────────────────────────── */}
      {open && (
        <div
          data-testid="notification-dropdown"
          style={{
            position: "absolute", right: 0, top: "calc(100% + 10px)",
            width: 340, maxHeight: 480,
            background: "rgba(5,10,20,0.97)", border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 18, boxShadow: "0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(79,209,197,0.06)",
            backdropFilter: "blur(24px)", zIndex: 100, overflow: "hidden",
            animation: "dropIn 0.18s cubic-bezier(0.34,1.56,0.64,1)",
          }}
        >
          <style>{`@keyframes dropIn { from { opacity: 0; transform: translateY(-8px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }`}</style>

          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px 14px", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: unread > 0 ? "#4fd1c5" : "#64748b", boxShadow: unread > 0 ? "0 0 6px #4fd1c5" : "none", transition: "all 0.3s" }} />
              <h3 style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>Notifications</h3>
              {unread > 0 && (
                <span style={{ padding: "1px 7px", borderRadius: 20, background: "rgba(79,209,197,0.12)", border: "1px solid rgba(79,209,197,0.2)", color: "#4fd1c5", fontSize: 10, fontWeight: 700 }}>{unread} new</span>
              )}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              {unread > 0 && (
                <button onClick={markAllRead}
                  data-testid="mark-all-read"
                  style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 8px", borderRadius: 7, background: "transparent", border: "none", color: "#475569", fontSize: 11, cursor: "pointer", transition: "color 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.color = "#4fd1c5"}
                  onMouseLeave={e => e.currentTarget.style.color = "#475569"}>
                  <CheckCheck style={{ width: 12, height: 12 }} /> All read
                </button>
              )}
              {notifications.some(n => n.read) && (
                <button onClick={clearRead}
                  data-testid="clear-read"
                  style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 8px", borderRadius: 7, background: "transparent", border: "none", color: "#475569", fontSize: 11, cursor: "pointer", transition: "color 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.color = "#f87171"}
                  onMouseLeave={e => e.currentTarget.style.color = "#475569"}>
                  <Trash2 style={{ width: 11, height: 11 }} /> Clear
                </button>
              )}
            </div>
          </div>

          {/* Notification list */}
          <div style={{ maxHeight: 380, overflowY: "auto" }}>
            {notifications.length > 0 ? notifications.map((notif, i) => {
              const { Icon, color, bg } = getConfig(notif.type);
              return (
                <button
                  key={notif.notification_id}
                  onClick={() => handleClick(notif)}
                  data-testid={`notification-item-${i}`}
                  style={{
                    width: "100%", display: "flex", alignItems: "flex-start", gap: 12,
                    padding: "13px 18px", textAlign: "left", background: notif.read ? "transparent" : "rgba(79,209,197,0.03)",
                    border: "none", borderBottom: "1px solid rgba(255,255,255,0.05)",
                    cursor: "pointer", transition: "background 0.15s",
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.04)"}
                  onMouseLeave={e => e.currentTarget.style.background = notif.read ? "transparent" : "rgba(79,209,197,0.03)"}
                >
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: bg, border: `1px solid ${color}22`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>
                    <Icon style={{ width: 16, height: 16, color }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                      <p style={{ fontSize: 13, fontWeight: notif.read ? 400 : 600, color: notif.read ? "#64748b" : "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>{notif.title}</p>
                      {!notif.read && <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#4fd1c5", boxShadow: "0 0 4px #4fd1c5", flexShrink: 0 }} />}
                    </div>
                    <p style={{ fontSize: 11, color: "#475569", lineHeight: 1.45, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{notif.message}</p>
                    <p style={{ fontSize: 10, color: "#475569", marginTop: 4 }}>{getTimeAgo(notif.created_at)}</p>
                  </div>
                </button>
              );
            }) : (
              <div style={{ padding: "48px 18px", textAlign: "center" }}>
                <div style={{ width: 48, height: 48, borderRadius: "50%", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 14px" }}>
                  <Bell style={{ width: 20, height: 20, color: "#475569" }} />
                </div>
                <p style={{ fontSize: 13, color: "#475569" }}>No notifications yet</p>
                <p style={{ fontSize: 11, color: "#475569", marginTop: 4 }}>We'll let you know when something happens.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
