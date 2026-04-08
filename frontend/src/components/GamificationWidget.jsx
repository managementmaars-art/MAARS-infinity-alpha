/**
 * GamificationWidget — Streaks, XP, Levels, Milestones
 * Self-contained: persists to localStorage, reads stats from props.
 * No backend changes required.
 */
import { useState, useEffect, useRef } from "react";
import { Flame, Zap, Trophy, Star, ChevronRight, X } from "lucide-react";

/* ─── Level table ────────────────────────────────────────────────────────── */
const LEVELS = [
  { level: 1,  xp: 0,    title: "Recruit"    },
  { level: 2,  xp: 100,  title: "Apprentice" },
  { level: 3,  xp: 300,  title: "Operative"  },
  { level: 4,  xp: 600,  title: "Specialist" },
  { level: 5,  xp: 1000, title: "Expert"     },
  { level: 6,  xp: 1500, title: "Commander"  },
  { level: 7,  xp: 2200, title: "Architect"  },
  { level: 8,  xp: 3000, title: "Director"   },
  { level: 9,  xp: 4000, title: "Strategist" },
  { level: 10, xp: 5500, title: "Visionary"  },
];

const getLevelInfo = (xp) => {
  let current = LEVELS[0];
  let next    = LEVELS[1];
  for (let i = 0; i < LEVELS.length - 1; i++) {
    if (xp >= LEVELS[i].xp && xp < LEVELS[i + 1].xp) {
      current = LEVELS[i];
      next    = LEVELS[i + 1];
      break;
    }
    if (xp >= LEVELS[LEVELS.length - 1].xp) {
      current = LEVELS[LEVELS.length - 1];
      next    = null;
    }
  }
  const progress = next
    ? Math.min(100, ((xp - current.xp) / (next.xp - current.xp)) * 100)
    : 100;
  return { current, next, progress };
};

/* ─── Milestone definitions ──────────────────────────────────────────────── */
const MILESTONES = [
  { id: "first_chat",    label: "First Contact",    desc: "Start your first chat",        xpReward: 50,  threshold: (s) => s.total_chats >= 1   },
  { id: "chat_10",       label: "Conversationalist", desc: "Complete 10 chats",           xpReward: 75,  threshold: (s) => s.total_chats >= 10  },
  { id: "chat_50",       label: "Power Chatter",    desc: "Complete 50 chats",            xpReward: 150, threshold: (s) => s.total_chats >= 50  },
  { id: "first_task",    label: "Task Master",      desc: "Create your first task",       xpReward: 50,  threshold: (s) => s.total_tasks >= 1   },
  { id: "tasks_5",       label: "Doer",             desc: "Complete 5 tasks",             xpReward: 100, threshold: (s) => s.completed_tasks >= 5},
  { id: "tasks_20",      label: "Executor",         desc: "Complete 20 tasks",            xpReward: 200, threshold: (s) => s.completed_tasks >= 20},
  { id: "streak_3",      label: "Consistent",       desc: "3-day streak",                 xpReward: 75,  threshold: (_, streak) => streak >= 3  },
  { id: "streak_7",      label: "Dedicated",        desc: "7-day streak",                 xpReward: 150, threshold: (_, streak) => streak >= 7  },
  { id: "streak_30",     label: "Unstoppable",      desc: "30-day streak",                xpReward: 500, threshold: (_, streak) => streak >= 30 },
];

const MILESTONE_ICONS = {
  first_chat: "💬", chat_10: "🗨️", chat_50: "🔥",
  first_task: "✅", tasks_5: "⚡", tasks_20: "🎯",
  streak_3: "🌟", streak_7: "💎", streak_30: "👑",
};

/* ─── Streak logic ───────────────────────────────────────────────────────── */
function computeStreak(lastActiveDate) {
  const today     = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();
  if (!lastActiveDate) return 1;
  if (lastActiveDate === today) return null; // no change, already counted
  if (lastActiveDate === yesterday) return null; // will increment on load
  return 1; // gap > 1 day, reset
}

function useGamification(stats) {
  const [state, setState] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("maars_gamification") || "{}");
      return {
        xp:            saved.xp            ?? 0,
        streak:        saved.streak        ?? 1,
        lastActive:    saved.lastActive    ?? null,
        unlockedBadges:saved.unlockedBadges ?? [],
        lastDailyXP:   saved.lastDailyXP   ?? null,
      };
    } catch { return { xp: 0, streak: 1, lastActive: null, unlockedBadges: [], lastDailyXP: null }; }
  });

  const [newBadge, setNewBadge] = useState(null);

  // Persist to localStorage
  useEffect(() => {
    try { localStorage.setItem("maars_gamification", JSON.stringify(state)); } catch {}
  }, [state]);

  // Daily XP + streak management
  useEffect(() => {
    const today = new Date().toDateString();
    setState(prev => {
      let { xp, streak, lastActive, lastDailyXP } = prev;
      let changed = false;

      // Daily login XP (once per day)
      if (lastDailyXP !== today) {
        xp += 10;
        lastDailyXP = today;
        changed = true;
      }

      // Streak logic
      const yesterday = new Date(Date.now() - 86400000).toDateString();
      if (lastActive !== today) {
        if (lastActive === yesterday) {
          streak = streak + 1;
        } else if (lastActive !== today) {
          streak = 1;
        }
        lastActive = today;
        changed = true;
      }

      return changed ? { ...prev, xp, streak, lastActive, lastDailyXP } : prev;
    });
  }, []);

  // XP from stats
  useEffect(() => {
    if (!stats) return;
    const statsKey = `maars_stats_xp_${JSON.stringify({ c: stats.total_chats, t: stats.completed_tasks })}`;
    if (localStorage.getItem(statsKey)) return;
    localStorage.setItem(statsKey, "1");

    const xpGain = (stats.total_chats || 0) * 5 + (stats.completed_tasks || 0) * 10;
    setState(prev => ({ ...prev, xp: Math.max(prev.xp, xpGain) }));
  }, [stats?.total_chats, stats?.completed_tasks]);

  // Milestone checks
  useEffect(() => {
    if (!stats) return;
    setState(prev => {
      let { xp, unlockedBadges } = prev;
      let newBadgeFound = null;
      let changed = false;

      MILESTONES.forEach(m => {
        if (!unlockedBadges.includes(m.id) && m.threshold(stats, prev.streak)) {
          xp += m.xpReward;
          unlockedBadges = [...unlockedBadges, m.id];
          newBadgeFound = m;
          changed = true;
        }
      });

      if (changed) {
        if (newBadgeFound) setNewBadge(newBadgeFound);
        return { ...prev, xp, unlockedBadges };
      }
      return prev;
    });
  }, [stats?.total_chats, stats?.completed_tasks, state.streak]);

  return { state, newBadge, clearNewBadge: () => setNewBadge(null) };
}

/* ─── Badge Toast ────────────────────────────────────────────────────────── */
function BadgeToast({ badge, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 4000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div
      style={{
        position: "fixed", bottom: 24, right: 24, zIndex: 9999,
        background: "rgba(5,10,20,0.96)", border: "1px solid rgba(79,209,197,0.35)",
        borderRadius: 14, padding: "14px 18px", display: "flex", alignItems: "center", gap: 14,
        boxShadow: "0 8px 40px rgba(79,209,197,0.2)",
        animation: "slideUp 0.4s cubic-bezier(0.34,1.56,0.64,1)",
        backdropFilter: "blur(20px)", maxWidth: 320,
      }}
    >
      <div style={{ fontSize: 28 }}>{MILESTONE_ICONS[badge.id] || "🏆"}</div>
      <div>
        <p style={{ fontSize: 11, color: "#4fd1c5", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 2 }}>Achievement Unlocked!</p>
        <p style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", fontFamily: "Outfit, sans-serif" }}>{badge.label}</p>
        <p style={{ fontSize: 12, color: "#64748b" }}>+{badge.xpReward} XP · {badge.desc}</p>
      </div>
      <button onClick={onDismiss} style={{ position: "absolute", top: 8, right: 8, color: "#475569", background: "none", border: "none", cursor: "pointer", padding: 4 }}>
        <X style={{ width: 12, height: 12 }} />
      </button>
      <style>{`@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }`}</style>
    </div>
  );
}

/* ─── GamificationWidget ─────────────────────────────────────────────────── */
export default function GamificationWidget({ stats }) {
  const { state, newBadge, clearNewBadge } = useGamification(stats);
  const { xp, streak, unlockedBadges }     = state;
  const { current, next, progress }        = getLevelInfo(xp);
  const [expanded, setExpanded]            = useState(false);

  const recentBadges = MILESTONES.filter(m => unlockedBadges.includes(m.id)).slice(-3);

  return (
    <>
      {newBadge && <BadgeToast badge={newBadge} onDismiss={clearNewBadge} />}

      <div
        style={{
          background: "rgba(8,15,28,0.6)", border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 16, padding: "16px 18px", backdropFilter: "blur(12px)",
          transition: "all 0.25s", cursor: "pointer",
        }}
        onClick={() => setExpanded(e => !e)}
        onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(79,209,197,0.2)"; e.currentTarget.style.boxShadow = "0 4px 24px rgba(79,209,197,0.08)"; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)"; e.currentTarget.style.boxShadow = "none"; }}
      >
        {/* Top row */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: expanded ? 16 : 0 }}>
          {/* Streak */}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 32, height: 32, borderRadius: 9, background: streak >= 3 ? "rgba(249,115,22,0.15)" : "rgba(255,255,255,0.05)", border: `1px solid ${streak >= 3 ? "rgba(249,115,22,0.3)" : "rgba(255,255,255,0.08)"}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Flame style={{ width: 15, height: 15, color: streak >= 3 ? "#f97316" : "#475569" }} />
            </div>
            <div>
              <p style={{ fontSize: 16, fontWeight: 800, color: streak >= 3 ? "#f97316" : "#e2e8f0", lineHeight: 1, fontFamily: "Outfit, sans-serif" }}>{streak}</p>
              <p style={{ fontSize: 9, color: "#475569", lineHeight: 1, textTransform: "uppercase", letterSpacing: "0.1em" }}>day streak</p>
            </div>
          </div>

          {/* Divider */}
          <div style={{ width: 1, height: 32, background: "rgba(255,255,255,0.07)" }} />

          {/* Level + XP */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 18, height: 18, borderRadius: 5, background: "rgba(79,209,197,0.15)", border: "1px solid rgba(79,209,197,0.3)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Zap style={{ width: 10, height: 10, color: "#4fd1c5" }} />
                </div>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#4fd1c5" }}>Lv.{current.level} · {current.title}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <Star style={{ width: 11, height: 11, color: "#f59e0b" }} />
                <span style={{ fontSize: 11, color: "#f59e0b", fontWeight: 700 }}>{xp.toLocaleString()} XP</span>
                <ChevronRight style={{ width: 12, height: 12, color: "#475569", transform: expanded ? "rotate(90deg)" : "rotate(0)", transition: "transform 0.2s" }} />
              </div>
            </div>

            {/* XP progress bar */}
            <div style={{ height: 4, borderRadius: 3, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
              <div style={{
                height: "100%", borderRadius: 3,
                background: "linear-gradient(90deg, #4fd1c5, #2563eb)",
                width: `${progress}%`, transition: "width 0.8s ease",
                boxShadow: "0 0 8px rgba(79,209,197,0.5)",
              }} />
            </div>
            {next && (
              <p style={{ fontSize: 9, color: "#475569", marginTop: 3, textAlign: "right" }}>
                {(next.xp - xp).toLocaleString()} XP to {next.title}
              </p>
            )}
          </div>
        </div>

        {/* Expanded: badges */}
        {expanded && (
          <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 14 }}>
            <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "#475569", marginBottom: 10 }}>
              Achievements · {unlockedBadges.length}/{MILESTONES.length}
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {MILESTONES.map(m => {
                const unlocked = unlockedBadges.includes(m.id);
                return (
                  <div key={m.id} title={`${m.label}: ${m.desc} (+${m.xpReward} XP)`}
                    style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 10px", borderRadius: 20, background: unlocked ? "rgba(79,209,197,0.08)" : "rgba(255,255,255,0.03)", border: `1px solid ${unlocked ? "rgba(79,209,197,0.2)" : "rgba(255,255,255,0.06)"}`, opacity: unlocked ? 1 : 0.45, transition: "all 0.2s" }}>
                    <span style={{ fontSize: 14 }}>{MILESTONE_ICONS[m.id]}</span>
                    <span style={{ fontSize: 11, color: unlocked ? "#e2e8f0" : "#475569", fontWeight: unlocked ? 600 : 400 }}>{m.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
