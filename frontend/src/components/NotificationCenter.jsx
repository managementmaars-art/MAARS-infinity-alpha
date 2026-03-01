import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import {
  Bell, Check, CheckCheck, Trash2, X, MessageSquare, CreditCard,
  UserPlus, Sparkles, AlertTriangle, Gift
} from "lucide-react";

const iconMap = {
  welcome: Sparkles,
  credits_low: AlertTriangle,
  team_join: UserPlus,
  team_invite: UserPlus,
  report_ready: MessageSquare,
  subscription: CreditCard,
  default: Bell,
};

const colorMap = {
  welcome: "indigo",
  credits_low: "amber",
  team_join: "emerald",
  team_invite: "cyan",
  report_ready: "violet",
  subscription: "rose",
  default: "zinc",
};

const getTimeAgo = (ts) => {
  if (!ts) return "";
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
};

const NotificationCenter = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unread, setUnread] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API}/notifications`, { headers: { Authorization: `Bearer ${token}` }
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
        method: "POST", headers: { Authorization: `Bearer ${token}` }
      });
    } catch {}
  };

  const markAllRead = async () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnread(0);
    try {
      await fetch(`${API}/notifications/read-all`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }
      });
    } catch {}
  };

  const clearRead = async () => {
    setNotifications(prev => prev.filter(n => !n.read));
    try {
      await fetch(`${API}/notifications/clear`, {
        method: "DELETE", headers: { Authorization: `Bearer ${token}` }
      });
    } catch {}
  };

  const handleClick = (notif) => {
    if (!notif.read) markRead(notif.notification_id);
    if (notif.link) {
      navigate(notif.link);
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={ref} data-testid="notification-center">
      {/* Bell Button */}
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors"
        data-testid="notification-bell"
      >
        <Bell className="w-5 h-5" />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-bold px-1" data-testid="notification-badge">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-zinc-900 border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden" data-testid="notification-dropdown">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
            <h3 className="text-sm font-semibold text-white">Notifications</h3>
            <div className="flex items-center gap-1">
              {unread > 0 && (
                <button onClick={markAllRead} className="text-xs text-zinc-500 hover:text-indigo-400 transition-colors flex items-center gap-1 px-2 py-1 rounded" data-testid="mark-all-read">
                  <CheckCheck className="w-3 h-3" /> Read all
                </button>
              )}
              {notifications.some(n => n.read) && (
                <button onClick={clearRead} className="text-xs text-zinc-500 hover:text-red-400 transition-colors flex items-center gap-1 px-2 py-1 rounded" data-testid="clear-read">
                  <Trash2 className="w-3 h-3" /> Clear
                </button>
              )}
            </div>
          </div>

          {/* Notification List */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length > 0 ? notifications.map((notif, i) => {
              const Icon = iconMap[notif.type] || iconMap.default;
              const color = colorMap[notif.type] || colorMap.default;
              return (
                <button
                  key={notif.notification_id}
                  onClick={() => handleClick(notif)}
                  className={`w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-white/5 transition-colors border-b border-white/5 ${!notif.read ? "bg-white/[0.03]" : ""}`}
                  data-testid={`notification-item-${i}`}
                >
                  <div className={`w-8 h-8 rounded-full bg-${color}-500/15 flex items-center justify-center shrink-0 mt-0.5`}>
                    <Icon className={`w-4 h-4 text-${color}-400`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm truncate ${!notif.read ? "text-white font-medium" : "text-zinc-400"}`}>{notif.title}</p>
                      {!notif.read && <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />}
                    </div>
                    <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">{notif.message}</p>
                    <p className="text-[10px] text-zinc-600 mt-1">{getTimeAgo(notif.created_at)}</p>
                  </div>
                </button>
              );
            }) : (
              <div className="px-4 py-10 text-center">
                <Bell className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
                <p className="text-zinc-500 text-sm">No notifications yet</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
