/**
 * AgentAvatar — Animated agent avatar with photorealistic or styled initials fallback.
 *
 * Priority:
 *  1. agent.avatar CDN/local URL  → <img>
 *  2. agent.avatar SVG data URI   → <img> (browsers support data: URIs natively)
 *  3. Broken img / empty avatar   → styled initials div (deterministic color per role)
 *
 * Alive effects:
 *  • Breathing (subtle scale pulse on the photo)
 *  • Rotating dual-tone gradient ring
 *  • Outward heartbeat pulse rings (sonar effect)
 *  • Glowing status dot
 *  • Ambient glow halo that pulses with the breathing
 *
 * Sizes: xs(24) sm(32) md(48) lg(64) xl(96) 2xl(128)
 */

import { useMemo, useId, useState } from "react";

/* ── Role → accent colour ─────────────────────────────────────────────────── */
const roleAccent = (role = "", network = "", isCommander = false) => {
  if (isCommander) return { ring: "#f59e0b", glow: "rgba(245,158,11,0.5)",  bg: "#1a1000", g1: "#f59e0b", g2: "#fbbf24" };
  const r = (role + " " + network).toLowerCase();
  if (/analyst|data|research|insight|intelligence/i.test(r))      return { ring: "#4fd1c5", glow: "rgba(79,209,197,0.45)",  bg: "#021210", g1: "#0d9488", g2: "#4fd1c5" };
  if (/creative|writer|content|copy|design|brand/i.test(r))       return { ring: "#a78bfa", glow: "rgba(167,139,250,0.45)", bg: "#0d0618", g1: "#7c3aed", g2: "#a78bfa" };
  if (/developer|engineer|technical|code|architect/i.test(r))     return { ring: "#60a5fa", glow: "rgba(96,165,250,0.45)",  bg: "#020b1a", g1: "#1d4ed8", g2: "#60a5fa" };
  if (/market|growth|seo|social|pr|campaign|sales|revenue/i.test(r)) return { ring: "#f472b6", glow: "rgba(244,114,182,0.45)", bg: "#180512", g1: "#be185d", g2: "#f472b6" };
  if (/finance|capital|investor|financial|budget/i.test(r))       return { ring: "#fbbf24", glow: "rgba(251,191,36,0.45)",  bg: "#120c00", g1: "#d97706", g2: "#fbbf24" };
  if (/legal|compliance|governance|ethic|audit/i.test(r))         return { ring: "#94a3b8", glow: "rgba(148,163,184,0.4)",  bg: "#080b10", g1: "#475569", g2: "#94a3b8" };
  if (/hr|recruit|operat|manag|project|execut/i.test(r))          return { ring: "#34d399", glow: "rgba(52,211,153,0.45)",  bg: "#011008", g1: "#047857", g2: "#34d399" };
  if (/security|cyber|threat|protect/i.test(r))                   return { ring: "#f87171", glow: "rgba(248,113,113,0.45)", bg: "#140202", g1: "#dc2626", g2: "#f87171" };
  if (/strateg|executive|vision|leadership/i.test(r))             return { ring: "#c084fc", glow: "rgba(192,132,252,0.45)", bg: "#120818", g1: "#9333ea", g2: "#c084fc" };
  if (/product|venture|innovat|startup/i.test(r))                 return { ring: "#38bdf8", glow: "rgba(56,189,248,0.45)",  bg: "#011520", g1: "#0284c7", g2: "#38bdf8" };
  return                                                                { ring: "#4fd1c5", glow: "rgba(79,209,197,0.45)",  bg: "#021210", g1: "#0d9488", g2: "#4fd1c5" };
};

const STATUS_COLOR = {
  online:  "#34d399",
  busy:    "#f59e0b",
  offline: "#475569",
  typing:  "#60a5fa",
};

const SIZES = {
  xs:  { outer: 24,  pad: 2,   dot: 6,  fontSize: 9  },
  sm:  { outer: 32,  pad: 2.5, dot: 8,  fontSize: 11 },
  md:  { outer: 48,  pad: 3,   dot: 10, fontSize: 14 },
  lg:  { outer: 64,  pad: 3.5, dot: 12, fontSize: 18 },
  xl:  { outer: 96,  pad: 4,   dot: 14, fontSize: 26 },
  "2xl":{ outer: 128, pad: 5,  dot: 16, fontSize: 34 },
};

/* ── Deterministic initials from name ───────────────────────────────────────── */
const getInitials = (name = "", agentId = "") => {
  const src = name || agentId;
  if (!src) return "?";
  const parts = src.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return src.slice(0, 2).toUpperCase();
};

export default function AgentAvatar({
  agent       = {},
  size        = "md",
  status      = "online",
  animate     = true,
  showRing    = true,
  showStatus  = true,
  showPulse   = false,
  className   = "",
  style       = {},
  onClick,
}) {
  const uid   = useId().replace(/:/g, "_");
  const s     = SIZES[size] || SIZES.md;
  const ac    = roleAccent(agent.role || "", agent.network || "", agent.isCommander);
  const inner = s.outer - s.pad * 2;
  const [imgError, setImgError] = useState(false);

  const av = agent.avatar || "";
  // Valid avatar: non-empty, not an old dicebear cartoon, not a broken randomuser fallback
  const hasAvatar = !imgError && av
    && !av.includes("dicebear.com/7.x/personas")
    && !av.includes("dicebear.com/9.x/adventurer");

  const initials = useMemo(() => getInitials(agent.name, agent.agent_id), [agent.name, agent.agent_id]);
  const animBase = `av_${uid}`;

  return (
    <div
      className={className}
      onClick={onClick}
      style={{
        position: "relative",
        width:  s.outer,
        height: s.outer,
        flexShrink: 0,
        cursor: onClick ? "pointer" : "default",
        ...style,
      }}
    >
      {/* Injected keyframes */}
      {animate && (
        <style>{`
          @keyframes ${animBase}_ring {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes ${animBase}_ring2 {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(-360deg); }
          }
          @keyframes ${animBase}_breathe {
            0%,100% { transform: scale(1);     box-shadow: 0 0 ${s.outer*0.3}px ${ac.glow}; }
            50%     { transform: scale(1.045); box-shadow: 0 0 ${s.outer*0.55}px ${ac.glow}; }
          }
          @keyframes ${animBase}_pulse1 {
            0%   { transform: scale(1);   opacity: 0.6; }
            100% { transform: scale(2.2); opacity: 0; }
          }
          @keyframes ${animBase}_pulse2 {
            0%   { transform: scale(1);   opacity: 0.4; }
            100% { transform: scale(3.0); opacity: 0; }
          }
          @keyframes ${animBase}_dot {
            0%,100% { opacity: 1;   transform: scale(1); }
            50%     { opacity: 0.6; transform: scale(1.35); }
          }
        `}</style>
      )}

      {/* Sonar heartbeat rings (landing/featured cards) */}
      {animate && showPulse && (
        <>
          <div style={{
            position: "absolute", inset: 0, borderRadius: "50%",
            border: `1.5px solid ${ac.ring}`,
            animation: `${animBase}_pulse1 2.4s ease-out infinite`,
            pointerEvents: "none",
          }} />
          <div style={{
            position: "absolute", inset: 0, borderRadius: "50%",
            border: `1px solid ${ac.ring}`,
            animation: `${animBase}_pulse2 2.4s ease-out 0.8s infinite`,
            pointerEvents: "none",
          }} />
        </>
      )}

      {/* Outer counter-rotating ring */}
      {showRing && animate && (
        <div style={{
          position: "absolute", inset: 0, borderRadius: "50%",
          background: `conic-gradient(from 0deg, transparent 0%, ${ac.ring}99 30%, transparent 55%, ${ac.ring}55 80%, transparent 100%)`,
          animation: `${animBase}_ring2 6s linear infinite`,
          pointerEvents: "none",
        }} />
      )}

      {/* Main rotating ring */}
      {showRing && (
        <div style={{
          position: "absolute", inset: 0, borderRadius: "50%",
          background: animate
            ? `conic-gradient(from 0deg, ${ac.ring} 0%, ${ac.ring}cc 15%, transparent 45%, ${ac.ring}66 75%, ${ac.ring} 100%)`
            : `none`,
          border: animate ? "none" : `2px solid ${ac.ring}44`,
          animation: animate ? `${animBase}_ring 3s linear infinite` : "none",
          pointerEvents: "none",
        }} />
      )}

      {/* Inner container — breathing */}
      <div style={{
        position: "absolute",
        top:    s.pad,
        left:   s.pad,
        width:  inner,
        height: inner,
        borderRadius: "50%",
        overflow: "hidden",
        background: ac.bg,
        animation: animate ? `${animBase}_breathe 3.8s ease-in-out infinite` : "none",
        zIndex: 1,
      }}>
        {hasAvatar ? (
          <img
            src={av}
            alt={agent.name || "Agent"}
            loading="lazy"
            draggable={false}
            style={{ width: "100%", height: "100%", objectFit: "cover", display: "block", borderRadius: "50%" }}
            onError={() => setImgError(true)}
          />
        ) : (
          /* Styled initials fallback — deterministic, role-colored, looks intentional */
          <div style={{
            width: "100%", height: "100%",
            borderRadius: "50%",
            background: `radial-gradient(circle at 35% 35%, ${ac.g1}cc, ${ac.g2}55 50%, ${ac.bg} 100%)`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: s.fontSize * 0.7,
            fontWeight: 800,
            color: ac.ring,
            letterSpacing: "-0.02em",
            fontFamily: "Outfit, system-ui, sans-serif",
            textShadow: `0 0 ${s.fontSize}px ${ac.glow}`,
            userSelect: "none",
          }}>
            {initials}
          </div>
        )}
      </div>

      {/* Status indicator */}
      {showStatus && status && (
        <div style={{
          position: "absolute",
          bottom: s.pad - 1,
          right:  s.pad - 1,
          width:  s.dot,
          height: s.dot,
          borderRadius: "50%",
          background: STATUS_COLOR[status] || STATUS_COLOR.offline,
          border: `${Math.max(1.5, s.pad * 0.5)}px solid #030712`,
          boxShadow: `0 0 ${s.dot}px ${STATUS_COLOR[status] || STATUS_COLOR.offline}`,
          animation: animate ? `${animBase}_dot 2s ease-in-out infinite` : "none",
          zIndex: 10,
        }} />
      )}
    </div>
  );
}

/* ── Stacked avatar group ─────────────────────────────────────────────────── */
export function AgentAvatarGroup({ agents = [], size = "sm", max = 5, className = "" }) {
  const visible  = agents.slice(0, max);
  const overflow = agents.length - max;
  const s = SIZES[size] || SIZES.sm;
  return (
    <div className={`flex items-center ${className}`}>
      {visible.map((agent, i) => (
        <AgentAvatar
          key={agent.agent_id || i}
          agent={agent}
          size={size}
          showStatus={false}
          showRing={false}
          animate={false}
          style={{ marginLeft: i === 0 ? 0 : -(s.outer / 4), zIndex: visible.length - i }}
        />
      ))}
      {overflow > 0 && (
        <div style={{
          marginLeft: -(s.outer / 4),
          width: s.outer, height: s.outer, borderRadius: "50%",
          background: "rgba(255,255,255,0.08)",
          border: "2px solid rgba(255,255,255,0.12)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: s.fontSize * 0.7, color: "#94a3b8", fontWeight: 700,
        }}>+{overflow}</div>
      )}
    </div>
  );
}
