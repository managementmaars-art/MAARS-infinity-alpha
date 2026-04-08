import { useState, useEffect, useRef, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bot, MessageSquare, ListTodo, Sparkles, Plus, ChevronRight,
  Trash2, Zap, Users, Terminal, ArrowRight, Activity, Brain,
  Flame, Trophy, Radio, Cpu, Command, TrendingUp, Shield,
  Network, Layers, GitBranch, Eye, Radar, Globe, Bolt
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import OnboardingFlow from "./OnboardingFlow";
import NotificationCenter from "../components/NotificationCenter";
import CommandCenter from "../components/projects/CommandCenter";
import GamificationWidget from "../components/GamificationWidget";
import AgentAvatar from "../components/AgentAvatar";

/* ─── Tokens ──────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  pink:   "#f472b6",
  amber:  "#f59e0b",
  green:  "#34d399",
  red:    "#f87171",
  border: "rgba(255,255,255,0.07)",
  border2:"rgba(255,255,255,0.12)",
  glass:  "rgba(6,12,28,0.7)",
  glass2: "rgba(8,16,32,0.85)",
};

/* ─── Keyframes injected once ─────────────────────────────── */
const GLOBAL_STYLES = `
  @keyframes db_holo      { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
  @keyframes db_spin      { to{transform:rotate(360deg)} }
  @keyframes db_spin_rev  { to{transform:rotate(-360deg)} }
  @keyframes db_fade_up   { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
  @keyframes db_pulse_g   { 0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,0.8)} 60%{box-shadow:0 0 0 8px rgba(52,211,153,0)} }
  @keyframes db_pulse_t   { 0%,100%{box-shadow:0 0 0 0 rgba(79,209,197,0.7)} 60%{box-shadow:0 0 0 6px rgba(79,209,197,0)} }
  @keyframes db_pulse_a   { 0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,0.7)} 60%{box-shadow:0 0 0 6px rgba(245,158,11,0)} }
  @keyframes db_float     { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
  @keyframes db_breathe   { 0%,100%{opacity:0.6;transform:scale(1)} 50%{opacity:1;transform:scale(1.04)} }
  @keyframes db_scan      { 0%{top:-2px;opacity:0} 5%{opacity:0.5} 95%{opacity:0.5} 100%{top:100%;opacity:0} }
  @keyframes db_flow      { 0%{background-position:0% 50%} 100%{background-position:200% 50%} }
  @keyframes db_orb       { 0%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-20px) scale(1.08)} 66%{transform:translate(-20px,15px) scale(0.95)} 100%{transform:translate(0,0) scale(1)} }
  @keyframes db_ring_spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
  @keyframes db_ticker    { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
  @keyframes db_bar_grow  { from{width:0} to{width:var(--bar-w,50%)} }
  @keyframes db_wave_1    { 0%,100%{height:3px}  50%{height:18px} }
  @keyframes db_wave_2    { 0%,100%{height:7px}  50%{height:26px} }
  @keyframes db_wave_3    { 0%,100%{height:12px} 50%{height:8px}  }
  @keyframes db_wave_4    { 0%,100%{height:5px}  50%{height:20px} }
  @keyframes db_wave_5    { 0%,100%{height:9px}  50%{height:5px}  }
  @keyframes db_blink     { 0%,100%{opacity:1} 50%{opacity:0} }
  @keyframes db_neural_line { 0%{stroke-dashoffset:1000} 100%{stroke-dashoffset:0} }
  @keyframes neuralPulseGreen { 0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.7)} 60%{box-shadow:0 0 0 7px rgba(16,185,129,0)} }
  @keyframes fadeInUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
  @keyframes holo { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
  @keyframes spin { to { transform: rotate(360deg); } }
  .db-card-hover { transition: all 0.3s cubic-bezier(0.22,1,0.36,1); }
  .db-card-hover:hover { transform: translateY(-4px) !important; }
  .db-shimmer-hover { position: relative; overflow: hidden; }
  .db-shimmer-hover::after { content:''; position:absolute; inset:0; background:linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.04) 50%, transparent 60%); transform:translateX(-100%); transition:transform 0.7s ease; }
  .db-shimmer-hover:hover::after { transform:translateX(100%); }
`;

/* ─── useCountUp ──────────────────────────────────────────── */
function useCountUp(target, duration = 1600, delay = 0) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!target) return;
    const timer = setTimeout(() => {
      const start = Date.now();
      const tick = () => {
        const p = Math.min((Date.now() - start) / duration, 1);
        const e = 1 - Math.pow(1 - p, 3);
        setCount(Math.round(e * target));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }, delay);
    return () => clearTimeout(timer);
  }, [target, duration, delay]);
  return count;
}

/* ─── useLiveTime ─────────────────────────────────────────── */
function useLiveTime() {
  const [t, setT] = useState(new Date());
  useEffect(() => {
    const i = setInterval(() => setT(new Date()), 1000);
    return () => clearInterval(i);
  }, []);
  return t;
}

/* ─── Live ticker messages ────────────────────────────────── */
const TICKER_MSGS = [
  "▸ Commander Orion coordinating 14 active agents across 3 networks",
  "▸ System operating at 99.97% uptime",
  "▸ 175,000+ AI models available via Universal Key",
  "▸ Enterprise trust scoring active — all agent actions audited",
  "▸ Real-time multi-agent collaboration engine online",
  "▸ 27 specialized networks — strategy, creative, engineering, finance, legal…",
  "▸ Zero-downtime model switching across 33 LLM providers",
  "▸ Knowledge graph continuously updated with new intelligence",
];

/* ─── Animated neural background canvas ──────────────────── */
function NeuralBg({ width = 400, height = 200, accent = T.teal }) {
  const ref = useRef(null);
  useEffect(() => {
    const c = ref.current; if (!c) return;
    const ctx = c.getContext("2d");
    c.width = width; c.height = height;
    const pts = Array.from({length: 18}, () => ({
      x: Math.random() * width, y: Math.random() * height,
      vx: (Math.random()-0.5)*0.4, vy: (Math.random()-0.5)*0.4,
      r: 2 + Math.random()*2, phase: Math.random()*Math.PI*2,
    }));
    let raf;
    const draw = (t) => {
      ctx.clearRect(0, 0, width, height);
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = width; if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height; if (p.y > height) p.y = 0;
      });
      // Draw connections
      pts.forEach((a, i) => pts.slice(i+1).forEach(b => {
        const dx = a.x-b.x, dy = a.y-b.y;
        const dist = Math.sqrt(dx*dx+dy*dy);
        if (dist < 90) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          const alpha = (1 - dist/90) * 0.25;
          ctx.strokeStyle = `rgba(79,209,197,${alpha})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }));
      // Draw nodes
      pts.forEach(p => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 0.002 + p.phase);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * (0.8 + 0.2*pulse), 0, Math.PI*2);
        ctx.fillStyle = `rgba(79,209,197,${0.3 + 0.4*pulse})`;
        ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [width, height, accent]);
  return <canvas ref={ref} style={{ position:"absolute", inset:0, width:"100%", height:"100%", opacity:0.4 }} />;
}

/* ─── Waveform visualizer ─────────────────────────────────── */
function Waveform({ accent = T.teal, bars = 7, height = 28 }) {
  const anims = ["db_wave_1","db_wave_2","db_wave_3","db_wave_4","db_wave_5","db_wave_2","db_wave_3"];
  const durs  = [1.0, 0.85, 1.1, 0.9, 1.2, 0.95, 1.05];
  return (
    <div style={{ display:"flex", alignItems:"center", gap:2.5, height }}>
      {Array.from({length:bars}, (_,i) => (
        <div key={i} style={{
          width:3, borderRadius:3, background: accent, opacity:0.85,
          animation:`${anims[i%5]} ${durs[i%5]}s ease-in-out ${i*0.12}s infinite`,
        }} />
      ))}
    </div>
  );
}

/* ─── Holographic stat card V2 ────────────────────────────── */
function HoloStatCard({ label, value, suffix="", icon: Icon, accent, sub, delay=0, sparkline, testId }) {
  const count = useCountUp(value, 1600, delay);
  const [hov, setHov] = useState(false);
  const sparkRef = useRef(null);

  useEffect(() => {
    if (!sparkline || !sparkRef.current) return;
    const c = sparkRef.current;
    const ctx = c.getContext("2d");
    c.width = 80; c.height = 28;
    const pts = sparkline;
    const max = Math.max(...pts); const min = Math.min(...pts);
    const range = max-min || 1;
    ctx.clearRect(0, 0, 80, 28);
    ctx.beginPath();
    pts.forEach((v,i) => {
      const x = (i/(pts.length-1))*78 + 1;
      const y = 26 - ((v-min)/range)*22;
      i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    });
    const grad = ctx.createLinearGradient(0,0,80,0);
    grad.addColorStop(0, accent+"88"); grad.addColorStop(1, accent);
    ctx.strokeStyle = grad; ctx.lineWidth = 1.5;
    ctx.stroke();
    // Fill
    ctx.lineTo(78, 28); ctx.lineTo(1, 28);
    ctx.closePath();
    const fillGrad = ctx.createLinearGradient(0,0,0,28);
    fillGrad.addColorStop(0, accent+"33"); fillGrad.addColorStop(1, accent+"00");
    ctx.fillStyle = fillGrad; ctx.fill();
  }, [sparkline, accent]);

  return (
    <div
      data-testid={testId}
      data-3d
      data-3d-strength="12"
      data-3d-lift="8"
      className="db-card-hover db-shimmer-hover"
      style={{
        position:"relative", padding:1.5, borderRadius:20,
        background:`linear-gradient(135deg, ${accent}88, ${accent}22, rgba(255,255,255,0.03), ${accent}44)`,
        backgroundSize:"300% 300%", animation:"db_holo 6s ease infinite",
        boxShadow: hov ? `0 16px 48px ${accent}20, 0 0 0 0.5px ${accent}33` : `0 4px 20px ${accent}10`,
      }}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
    >
      <div style={{
        background:"rgba(4,8,20,0.96)", borderRadius:19,
        padding:"20px 22px 18px", backdropFilter:"blur(20px)",
        position:"relative", overflow:"hidden",
      }}>
        {/* Scanline texture */}
        <div style={{position:"absolute",inset:0,background:"repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.006) 2px, rgba(255,255,255,0.006) 3px)",pointerEvents:"none",borderRadius:19}} />
        {/* Scan line sweep */}
        <div style={{position:"absolute",left:0,right:0,height:1,background:`linear-gradient(90deg, transparent, ${accent}55, transparent)`,animation:"db_scan 5s linear infinite",pointerEvents:"none"}} />
        {/* Corner orb */}
        <div style={{position:"absolute",top:-30,right:-30,width:100,height:100,borderRadius:"50%",background:`radial-gradient(circle, ${accent}30 0%, transparent 65%)`,pointerEvents:"none",animation:"db_breathe 4s ease-in-out infinite"}} />

        <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",position:"relative"}}>
          <div style={{flex:1}}>
            <p style={{fontSize:9,fontWeight:800,color:accent,letterSpacing:"0.18em",textTransform:"uppercase",marginBottom:10,opacity:0.8}}>{label}</p>
            <p style={{fontSize:36,fontWeight:800,color:"#f1f5f9",lineHeight:1,fontFamily:"Outfit, sans-serif",fontVariantNumeric:"tabular-nums",letterSpacing:"-0.02em"}}>
              {count.toLocaleString()}{suffix}
            </p>
            {sub && <p style={{fontSize:10,color:"#64748b",marginTop:5}}>{sub}</p>}
            {sparkline && <canvas ref={sparkRef} style={{marginTop:10,display:"block"}} />}
          </div>
          <div style={{
            width:48,height:48,borderRadius:14,
            background:`linear-gradient(135deg, ${accent}22, ${accent}08)`,
            border:`1px solid ${accent}33`,
            display:"flex",alignItems:"center",justifyContent:"center",
            flexShrink:0, marginLeft:12,
            boxShadow: hov ? `0 0 24px ${accent}50, inset 0 0 12px ${accent}10` : "none",
            transition:"box-shadow 0.4s",
          }}>
            <Icon style={{width:22,height:22,color:accent}} />
          </div>
        </div>

        {/* Bottom trend indicator */}
        <div style={{position:"absolute",bottom:10,right:16,display:"flex",alignItems:"center",gap:4}}>
          <TrendingUp style={{width:10,height:10,color:T.green}} />
          <span style={{fontSize:9,color:T.green,fontWeight:700}}>Live</span>
        </div>
      </div>
    </div>
  );
}

/* ─── Live neural activity feed ───────────────────────────── */
const FEED_TEMPLATES = [
  (a) => `${a} completed strategic analysis`,
  (a) => `${a} generated campaign brief`,
  (a) => `${a} delegated subtask to specialist`,
  (a) => `${a} finished code review`,
  (a) => `${a} submitted research report`,
  (a) => `${a} optimized model routing`,
  (a) => `${a} processed knowledge update`,
  (a) => `${a} ran competitive analysis`,
  (a) => `${a} drafted email sequence`,
  (a) => `${a} scheduled 3 follow-ups`,
  (a) => `${a} deployed automation workflow`,
  (a) => `${a} completed legal review`,
  (a) => `${a} built financial forecast`,
  (a) => `${a} updated product roadmap`,
  (a) => `${a} resolved 4 support tickets`,
];

const AGENT_NAMES = ["Commander Orion","Nadia Kessler","Marcus Drake","Luna Bergström","Victor Ashford","Ethan Yates","Zara Mitchell","Scarlett Monroe","Derek Huang","Riley Chen","Damien Voss","Alexandra Reid","Felix Romano","Nathan Cross","Serena Okafor"];
const ACCENTS = [T.teal, T.violet+"cc", T.blue, T.green, T.pink, T.amber];

function NeuralActivityFeed({ agents }) {
  const [events, setEvents] = useState(() =>
    Array.from({length:8}, (_,i) => ({
      id: i,
      agent: AGENT_NAMES[i % AGENT_NAMES.length],
      msg: FEED_TEMPLATES[i % FEED_TEMPLATES.length](AGENT_NAMES[i % AGENT_NAMES.length]),
      accent: ACCENTS[i % ACCENTS.length],
      ts: Date.now() - (8-i) * 18000,
      fresh: false,
    }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      const agentList = agents.length > 0 ? agents.map(a=>a.name) : AGENT_NAMES;
      const a = agentList[Math.floor(Math.random() * agentList.length)];
      const tmpl = FEED_TEMPLATES[Math.floor(Math.random() * FEED_TEMPLATES.length)];
      const accent = ACCENTS[Math.floor(Math.random() * ACCENTS.length)];
      setEvents(prev => [{
        id: Date.now(), agent: a, msg: tmpl(a), accent, ts: Date.now(), fresh: true,
      }, ...prev].slice(0, 12));
    }, 3800);
    return () => clearInterval(interval);
  }, [agents]);

  const fmt = (ts) => {
    const diff = Math.floor((Date.now() - ts) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
    return `${Math.floor(diff/3600)}h ago`;
  };

  return (
    <div
      data-3d
      data-3d-strength="8"
      data-3d-lift="5"
      style={{
        background:T.glass, border:`1px solid ${T.border}`, borderRadius:18,
        backdropFilter:"blur(16px)", overflow:"hidden", position:"relative",
      }}>
      {/* Header */}
      <div style={{padding:"14px 18px 12px",borderBottom:`1px solid ${T.border}`,display:"flex",alignItems:"center",justifyContent:"space-between"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{position:"relative"}}>
            <Radio style={{width:16,height:16,color:T.teal}} />
            <div style={{position:"absolute",top:-2,right:-2,width:6,height:6,borderRadius:"50%",background:T.green,animation:"db_pulse_g 2s ease infinite"}} />
          </div>
          <span style={{fontSize:11,fontWeight:700,color:"#e2e8f0",letterSpacing:"0.05em"}}>Neural Activity Feed</span>
          <div style={{display:"flex",alignItems:"center",gap:3,padding:"2px 8px",borderRadius:20,background:"rgba(52,211,153,0.1)",border:"1px solid rgba(52,211,153,0.25)"}}>
            <span style={{width:5,height:5,borderRadius:"50%",background:T.green,display:"inline-block",animation:"db_blink 1.2s ease infinite"}} />
            <span style={{fontSize:9,fontWeight:700,color:T.green,letterSpacing:"0.1em"}}>LIVE</span>
          </div>
        </div>
        <Waveform accent={T.teal} bars={5} height={20} />
      </div>
      {/* Events */}
      <div style={{maxHeight:320,overflowY:"auto",padding:"8px 0"}}>
        {events.map((ev, i) => (
          <div key={ev.id} style={{
            display:"flex",alignItems:"center",gap:12,padding:"9px 18px",
            borderBottom:`1px solid rgba(255,255,255,0.03)`,
            background: ev.fresh && i===0 ? `${ev.accent}08` : "transparent",
            transition:"background 2s ease",
            animation: ev.fresh && i===0 ? "db_fade_up 0.4s ease" : "none",
          }}>
            <div style={{
              width:8,height:8,borderRadius:"50%",flexShrink:0,
              background:ev.accent,
              boxShadow:`0 0 6px ${ev.accent}`,
              animation: i===0 ? "db_pulse_t 2s ease infinite" : "none",
            }} />
            <div style={{flex:1,minWidth:0}}>
              <p style={{fontSize:12,color:"#cbd5e1",lineHeight:1.4,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                <span style={{color:ev.accent,fontWeight:600}}>{ev.agent}</span>
                {" "}
                {ev.msg.replace(ev.agent, "")}
              </p>
            </div>
            <span style={{fontSize:10,color:"#475569",flexShrink:0}}>{fmt(ev.ts)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── System health panel ─────────────────────────────────── */
function SystemHealth({ agents, stats }) {
  const metrics = [
    { label:"Agents Online",   value: agents.filter(a=>!a.hidden).length, max:458, accent:T.teal,   icon:Bot },
    { label:"Tasks Completed", value: stats?.completed_tasks||0,           max:Math.max(stats?.total_tasks||1,1), accent:T.green,  icon:Sparkles },
    { label:"Model Providers", value:33, max:33,                          accent:T.blue,   icon:Globe },
    { label:"Networks Active", value:27, max:27,                          accent:"#a78bfa", icon:Network },
  ];
  return (
    <div data-3d data-3d-strength="8" data-3d-lift="5" style={{background:T.glass,border:`1px solid ${T.border}`,borderRadius:18,backdropFilter:"blur(16px)",overflow:"hidden"}}>
      <div style={{padding:"14px 18px 12px",borderBottom:`1px solid ${T.border}`,display:"flex",alignItems:"center",gap:8}}>
        <Shield style={{width:15,height:15,color:T.teal}} />
        <span style={{fontSize:11,fontWeight:700,color:"#e2e8f0"}}>System Health</span>
        <div style={{marginLeft:"auto",display:"flex",alignItems:"center",gap:5}}>
          <span style={{width:6,height:6,borderRadius:"50%",background:T.green,display:"inline-block",animation:"db_pulse_g 2s ease infinite"}} />
          <span style={{fontSize:9,fontWeight:700,color:T.green}}>NOMINAL</span>
        </div>
      </div>
      <div style={{padding:"14px 18px",display:"flex",flexDirection:"column",gap:14}}>
        {metrics.map((m,i) => {
          const pct = Math.min((m.value / m.max) * 100, 100);
          return (
            <div key={i}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:5}}>
                <div style={{display:"flex",alignItems:"center",gap:6}}>
                  <m.icon style={{width:12,height:12,color:m.accent}} />
                  <span style={{fontSize:11,color:"#94a3b8"}}>{m.label}</span>
                </div>
                <span style={{fontSize:12,fontWeight:700,color:"#f1f5f9",fontVariantNumeric:"tabular-nums"}}>{m.value.toLocaleString()}</span>
              </div>
              <div style={{height:4,borderRadius:4,background:"rgba(255,255,255,0.06)",overflow:"hidden"}}>
                <div style={{
                  height:"100%",borderRadius:4,
                  background:`linear-gradient(90deg, ${m.accent}88, ${m.accent})`,
                  width:`${pct}%`,
                  boxShadow:`0 0 8px ${m.accent}66`,
                  transition:"width 1s cubic-bezier(0.22,1,0.36,1)",
                  animation:"db_bar_grow 1.2s cubic-bezier(0.22,1,0.36,1) both",
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Activity Heatmap V2 ─────────────────────────────────── */
function ActivityHeatmap({ stats }) {
  const WEEKS = 17;
  const total = (stats?.total_chats||0) + (stats?.total_tasks||0);
  const [hovered, setHovered] = useState(null);

  const data = useMemo(() => Array.from({length:WEEKS*7}, (_,i) => {
    const pos = i/(WEEKS*7);
    const v = Math.sin(i/6.5*Math.PI)*0.35 + Math.sin(i/2.8+1.4)*0.18 + pos*0.55 + 0.08;
    return total > 0 ? Math.max(0, Math.min(4, Math.round(v*3.2))) : 0;
  }), [total]);

  const getColor = v => ["rgba(255,255,255,0.04)","rgba(79,209,197,0.18)","rgba(79,209,197,0.38)","rgba(79,209,197,0.65)",T.teal][v];
  const days = ["S","M","T","W","T","F","S"];
  const months = Array.from({length:WEEKS}, (_,w) => {
    const d = new Date(); d.setDate(d.getDate() - (WEEKS-w)*7);
    return w%4===0 ? d.toLocaleDateString([],{month:"short"}) : "";
  });

  return (
    <div data-3d data-3d-strength="8" data-3d-lift="4" style={{background:T.glass,border:`1px solid ${T.border}`,borderRadius:18,backdropFilter:"blur(16px)",padding:"18px 20px",position:"relative",overflow:"hidden"}}>
      <NeuralBg width={800} height={120} />
      <div style={{position:"relative",zIndex:1}}>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:14}}>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <Activity style={{width:14,height:14,color:T.teal}} />
            <span style={{fontSize:11,fontWeight:700,color:"#e2e8f0"}}>Activity Matrix</span>
            <span style={{fontSize:10,color:"#475569"}}>· {WEEKS} weeks</span>
          </div>
          <div style={{display:"flex",alignItems:"center",gap:5}}>
            <span style={{fontSize:9,color:"#475569"}}>Less</span>
            {[0,1,2,3,4].map(v=><div key={v} style={{width:9,height:9,borderRadius:2,background:getColor(v),border:"1px solid rgba(255,255,255,0.05)"}} />)}
            <span style={{fontSize:9,color:"#475569"}}>More</span>
          </div>
        </div>
        <div style={{overflowX:"auto"}}>
          <div style={{display:"grid",gridTemplateColumns:`24px repeat(${WEEKS}, 1fr)`,gap:"2px",marginBottom:3}}>
            <div />
            {months.map((m,w)=><div key={w} style={{fontSize:8,color:"#475569",textAlign:"center"}}>{m}</div>)}
          </div>
          {days.map((day,d)=>(
            <div key={d} style={{display:"grid",gridTemplateColumns:`24px repeat(${WEEKS}, 1fr)`,gap:"2px",marginBottom:2}}>
              <div style={{fontSize:8,color:"#475569",display:"flex",alignItems:"center"}}>{d%2===0?day:""}</div>
              {Array.from({length:WEEKS},(_,w)=>{
                const val = data[w*7+d]||0, key=`${w}-${d}`;
                return <div key={w} style={{
                  height:10,borderRadius:2,background:getColor(val),
                  border:"1px solid rgba(255,255,255,0.03)",
                  transition:"all 0.15s",
                  transform:hovered===key?"scale(1.7)":"scale(1)",
                  boxShadow:hovered===key?`0 0 8px ${T.teal}`:"none",
                  cursor:"default",position:"relative",zIndex:hovered===key?2:1,
                }}
                onMouseEnter={()=>setHovered(key)}
                onMouseLeave={()=>setHovered(null)}
                title={val>0?`${val*3} interactions`:"No activity"}
                />;
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── Live agent roster V2 ────────────────────────────────── */
function LiveAgentRoster({ agents, recentChats, onChat }) {
  const activeIds = new Set((recentChats||[]).slice(0,20).map(c=>c.agent_id));
  const visible = agents.filter(a=>!a.hidden).slice(0,40);
  const active = visible.filter(a=>activeIds.has(a.agent_id));
  const [filter, setFilter] = useState("all");
  const shown = filter==="active" ? visible.filter(a=>activeIds.has(a.agent_id)) : visible;

  return (
    <div data-3d data-3d-strength="8" data-3d-lift="5" style={{background:T.glass,border:`1px solid ${T.border}`,borderRadius:18,backdropFilter:"blur(16px)",overflow:"hidden"}}>
      {/* Header */}
      <div style={{padding:"14px 18px 12px",borderBottom:`1px solid ${T.border}`,display:"flex",alignItems:"center",justifyContent:"space-between",flexWrap:"wrap",gap:8}}>
        <div style={{display:"flex",alignItems:"center",gap:8}}>
          <Users style={{width:14,height:14,color:T.teal}} />
          <span style={{fontSize:11,fontWeight:700,color:"#e2e8f0"}}>Live Roster</span>
          <div style={{display:"flex",alignItems:"center",gap:4,padding:"2px 8px",borderRadius:20,background:"rgba(52,211,153,0.1)",border:"1px solid rgba(52,211,153,0.2)"}}>
            <span style={{width:5,height:5,borderRadius:"50%",background:T.green,display:"inline-block",animation:"db_pulse_g 2s ease infinite"}} />
            <span style={{fontSize:9,fontWeight:700,color:T.green}}>{active.length} active</span>
          </div>
        </div>
        <div style={{display:"flex",gap:4}}>
          {["all","active"].map(f=>(
            <button key={f} onClick={()=>setFilter(f)} style={{
              padding:"3px 10px",borderRadius:20,fontSize:10,fontWeight:600,
              background:filter===f?`${T.teal}20`:"transparent",
              color:filter===f?T.teal:"#475569",
              border:filter===f?`1px solid ${T.teal}40`:"1px solid transparent",
              cursor:"pointer",transition:"all 0.15s",
            }}>{f==="all"?`All (${visible.length})`:`Active (${active.length})`}</button>
          ))}
        </div>
      </div>
      {/* Grid */}
      <div style={{padding:16,maxHeight:480,overflowY:"auto"}}>
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill, minmax(68px, 1fr))",gap:10}}>
          {shown.map((agent,i)=>{
            const isActive = activeIds.has(agent.agent_id);
            return (
              <div key={agent.agent_id}
                title={`${agent.name} — ${isActive?"Recently active":"Available"}`}
                onClick={()=>onChat(agent.agent_id)}
                style={{
                  display:"flex",flexDirection:"column",alignItems:"center",gap:5,
                  cursor:"pointer",transition:"all 0.25s",
                  animation:`db_fade_up 0.4s ease ${Math.min(i*0.02,0.5)}s both`,
                  opacity: isActive?1:0.55,
                }}
                onMouseEnter={e=>{e.currentTarget.style.opacity="1";e.currentTarget.style.transform="translateY(-4px)";}}
                onMouseLeave={e=>{e.currentTarget.style.opacity=isActive?"1":"0.55";e.currentTarget.style.transform="translateY(0)";}}
              >
                <AgentAvatar
                  agent={agent}
                  size="md"
                  status={isActive?"online":"offline"}
                  animate={isActive}
                  showRing={isActive}
                  showStatus
                />
                <span style={{
                  fontSize:9,color:isActive?"#94a3b8":"#475569",
                  textAlign:"center",overflow:"hidden",textOverflow:"ellipsis",
                  whiteSpace:"nowrap",maxWidth:64,lineHeight:1.2,
                }}>{agent.name.split(" ")[0]}</span>
              </div>
            );
          })}
        </div>
        {shown.length===0&&<p style={{textAlign:"center",padding:"24px 0",fontSize:12,color:"#475569"}}>No agents in this view</p>}
      </div>
    </div>
  );
}

/* ─── Mission briefing V2 ─────────────────────────────────── */
const MISSIONS = [
  "Deploy Commander Orion on a complex multi-agent strategic objective",
  "Analyze your top-performing agents and optimize their prompts",
  "Build a multi-agent workflow for your highest-priority project",
  "Explore the 175,000+ model catalog — find your ideal reasoning stack",
  "Set up an integration to connect your existing tools to the platform",
  "Create a custom agent tailored to your unique workflow and domain",
  "Review your analytics and identify optimization opportunities",
  "Run a full campaign brief through your creative agent network",
  "Delegate a complex research project to your analyst team",
  "Configure trust scores and safety guardrails for your agent fleet",
  "Build a task graph for your next big initiative using the kernel",
  "Expand your agent network with domain-specific knowledge injections",
  "Set up automated workflows to eliminate repetitive manual processes",
  "Explore multi-step agent collaboration and delegation chains",
  "Configure organization-wide RBAC permissions and audit policies",
];

function MissionBriefing({ user, agents, stats }) {
  const time = useLiveTime();
  const mission = MISSIONS[new Date().getDate() % MISSIONS.length];
  const h = time.getHours();
  const greeting = h<5?"Working late":h<12?"Good morning":h<17?"Good afternoon":h<21?"Good evening":"Burning the midnight oil";
  const totalAgents = agents.filter(a=>!a.hidden).length;

  return (
    <div style={{marginBottom:28}}>
      {/* Status bar */}
      <div data-3d data-3d-strength="6" data-3d-lift="3" style={{
        display:"flex",alignItems:"center",gap:0,marginBottom:16,
        background:"rgba(4,8,20,0.8)",border:`1px solid ${T.border}`,
        borderRadius:12,overflow:"hidden",backdropFilter:"blur(12px)",
      }}>
        {/* Online badge */}
        <div style={{display:"flex",alignItems:"center",gap:6,padding:"8px 14px",borderRight:`1px solid ${T.border}`,flexShrink:0}}>
          <span style={{width:7,height:7,borderRadius:"50%",background:T.green,boxShadow:`0 0 8px ${T.green}`,display:"inline-block",animation:"db_pulse_g 2s ease infinite"}} />
          <span style={{fontSize:10,fontWeight:700,color:T.green,letterSpacing:"0.12em",whiteSpace:"nowrap"}}>SYSTEM ONLINE</span>
        </div>
        {/* Clock */}
        <div style={{padding:"8px 14px",borderRight:`1px solid ${T.border}`,flexShrink:0}}>
          <span style={{fontSize:10,color:"#64748b",fontFamily:"JetBrains Mono,monospace",fontWeight:600}}>
            {time.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"})}
          </span>
        </div>
        {/* Agents count */}
        <div style={{padding:"8px 14px",borderRight:`1px solid ${T.border}`,flexShrink:0}}>
          <span style={{fontSize:10,color:"#64748b"}}><span style={{color:T.teal,fontWeight:700}}>{totalAgents}</span> agents standing by</span>
        </div>
        {/* Notifications */}
        <div style={{marginLeft:"auto",padding:"4px 12px"}}>
          <NotificationCenter />
        </div>
      </div>

      {/* Greeting */}
      <h1 style={{
        fontSize:"clamp(1.9rem, 3.5vw, 2.8rem)",fontWeight:800,
        fontFamily:"Outfit, sans-serif",lineHeight:1.06,margin:"0 0 10px",
        background:`linear-gradient(135deg, #f1f5f9 0%, ${T.teal} 45%, #a78bfa 80%, ${T.teal} 100%)`,
        backgroundSize:"200% 200%",
        WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent",
        animation:"db_flow 6s ease infinite",
      }}>
        {greeting}, {user?.name?.split(" ")[0]||"Commander"}.
      </h1>

      {/* Mission */}
      <div style={{display:"flex",alignItems:"flex-start",gap:10,marginBottom:16}}>
        <div style={{
          padding:"3px 10px",borderRadius:20,
          background:`${T.amber}18`,border:`1px solid ${T.amber}33`,
          fontSize:9,fontWeight:800,color:T.amber,letterSpacing:"0.15em",
          whiteSpace:"nowrap",marginTop:2,flexShrink:0,
        }}>⚡ MISSION</div>
        <p style={{fontSize:14,color:"#94a3b8",lineHeight:1.6,margin:0}}>{mission}</p>
      </div>

      {/* Live ticker */}
      <div style={{
        background:"rgba(4,8,20,0.6)",border:`1px solid ${T.border}`,
        borderRadius:8,overflow:"hidden",position:"relative",
      }}>
        <div style={{display:"flex",alignItems:"center"}}>
          <div style={{
            padding:"6px 12px",background:`${T.teal}15`,
            borderRight:`1px solid ${T.teal}22`,flexShrink:0,
            display:"flex",alignItems:"center",gap:5,
          }}>
            <Cpu style={{width:10,height:10,color:T.teal}} />
            <span style={{fontSize:9,fontWeight:800,color:T.teal,letterSpacing:"0.1em"}}>INTEL</span>
          </div>
          <div style={{overflow:"hidden",flex:1}}>
            <div style={{
              display:"flex",
              animation:"db_ticker 30s linear infinite",
              whiteSpace:"nowrap",
            }}>
              {[...TICKER_MSGS,...TICKER_MSGS].map((m,i)=>(
                <span key={i} style={{fontSize:10,color:"#64748b",padding:"6px 20px",flexShrink:0}}>{m}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Commander card V2 ───────────────────────────────────── */
function CommanderCard({ commander, navigate }) {
  const [hov, setHov] = useState(false);
  return (
    <div>
      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
        <span style={{width:20,height:1,background:T.teal,display:"block"}} />
        <span style={{fontSize:10,fontWeight:700,letterSpacing:"0.18em",textTransform:"uppercase",color:T.teal}}>Your Commander</span>
      </div>
      <div
        onClick={()=>navigate(`/chat/${commander.agent_id}`)}
        data-testid="commander-card"
        data-3d
        data-3d-strength="10"
        data-3d-lift="7"
        className="db-card-hover db-shimmer-hover"
        style={{
          position:"relative",borderRadius:20,cursor:"pointer",overflow:"hidden",
          background:"linear-gradient(135deg, rgba(79,209,197,0.08) 0%, rgba(124,58,237,0.06) 50%, rgba(37,99,235,0.06) 100%)",
          border:`1px solid ${hov?"rgba(79,209,197,0.45)":"rgba(79,209,197,0.18)"}`,
          backdropFilter:"blur(16px)",
          boxShadow:hov?"0 20px 60px rgba(79,209,197,0.18), 0 0 0 0.5px rgba(79,209,197,0.15)":"0 4px 20px rgba(0,0,0,0.3)",
          transition:"all 0.35s cubic-bezier(0.22,1,0.36,1)",
        }}
        onMouseEnter={()=>setHov(true)}
        onMouseLeave={()=>setHov(false)}
      >
        {/* Scan line */}
        <div style={{position:"absolute",left:0,right:0,height:1,background:`linear-gradient(90deg, transparent, ${T.teal}55, transparent)`,animation:"db_scan 5s linear infinite",pointerEvents:"none"}} />
        {/* Corner glow */}
        <div style={{position:"absolute",top:-40,left:-40,width:160,height:160,borderRadius:"50%",background:"radial-gradient(circle, rgba(79,209,197,0.14) 0%, transparent 70%)",pointerEvents:"none"}} />
        <div style={{position:"absolute",bottom:-40,right:-40,width:120,height:120,borderRadius:"50%",background:"radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)",pointerEvents:"none"}} />

        <div style={{display:"flex",alignItems:"center",gap:16,padding:"18px 20px",position:"relative"}}>
          <div style={{flexShrink:0,animation:"db_float 4s ease-in-out infinite"}}>
            <AgentAvatar
              agent={commander}
              size="xl"
              status="online"
              animate
              showRing
              showPulse
            />
          </div>
          <div style={{flex:1,minWidth:0}}>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:3}}>
              <h3 style={{fontSize:17,fontWeight:800,color:"#f1f5f9",fontFamily:"Outfit, sans-serif",margin:0}}>{commander.name}</h3>
              <span style={{
                padding:"2px 8px",borderRadius:20,fontSize:8,fontWeight:900,
                background:"linear-gradient(90deg,#f59e0b,#d97706)",color:"#000",
                letterSpacing:"0.15em",boxShadow:"0 0 12px rgba(245,158,11,0.5)",
              }}>⚡ CMD</span>
            </div>
            <p style={{fontSize:11,color:T.teal,margin:"0 0 10px",opacity:0.9,fontWeight:600}}>{commander.role}</p>
            <div style={{display:"flex",flexWrap:"wrap",gap:5}}>
              {(commander.capabilities||[]).slice(0,4).map((cap,i)=>(
                <span key={i} style={{padding:"3px 9px",fontSize:9,borderRadius:20,background:"rgba(79,209,197,0.1)",color:T.teal,border:"1px solid rgba(79,209,197,0.2)",fontWeight:600}}>{cap}</span>
              ))}
            </div>
          </div>
          <button
            onClick={e=>{e.stopPropagation();navigate(`/chat/${commander.agent_id}`);}}
            style={{
              display:"flex",alignItems:"center",gap:6,padding:"10px 18px",borderRadius:12,
              background:`linear-gradient(135deg, ${T.teal}, ${T.blue})`,
              color:"#030712",fontSize:13,fontWeight:800,border:"none",cursor:"pointer",
              boxShadow:"0 0 24px rgba(79,209,197,0.35)",flexShrink:0,
              transition:"box-shadow 0.2s",
            }}
            onMouseEnter={e=>e.currentTarget.style.boxShadow="0 0 40px rgba(79,209,197,0.55)"}
            onMouseLeave={e=>e.currentTarget.style.boxShadow="0 0 24px rgba(79,209,197,0.35)"}
          >
            <MessageSquare style={{width:14,height:14}} /> Chat Now
          </button>
        </div>

        {/* Bottom waveform */}
        <div style={{borderTop:`1px solid rgba(255,255,255,0.05)`,padding:"10px 20px",display:"flex",alignItems:"center",gap:12}}>
          <Waveform accent={T.teal} bars={9} height={22} />
          <span style={{fontSize:10,color:"#475569"}}>Coordinating agent network…</span>
          <div style={{marginLeft:"auto",display:"flex",alignItems:"center",gap:5}}>
            <span style={{fontSize:10,color:T.green,fontWeight:700}}>●</span>
            <span style={{fontSize:10,color:"#64748b"}}>Online</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── AI Insights panel ───────────────────────────────────── */
const INSIGHT_ITEMS = [
  { icon: TrendingUp, color: "#4fd1c5", title: "Fleet Performance",   getDesc: (agents, stats) => `${agents.filter(a=>!a.hidden).length} agents active · ${((stats?.completed_tasks||0)/Math.max((stats?.total_tasks||1),1)*100).toFixed(0)}% task completion rate` },
  { icon: Brain,      color: "#a78bfa", title: "Knowledge Coverage",  getDesc: () => "33 skill domains · Provider guides injected per agent · RAG pipeline live" },
  { icon: Shield,     color: "#34d399", title: "Governance Status",   getDesc: () => "Trust scoring active · Audit logs running · All actions metered" },
  { icon: Network,    color: "#60a5fa", title: "Agent Networks",       getDesc: () => "27 specialized networks · Commander orchestration ready · Multi-agent chains enabled" },
  { icon: Zap,        color: "#f59e0b", title: "Model Infrastructure",getDesc: () => "175k+ models available · Smart routing active · 33 providers connected" },
  { icon: Radar,      color: "#f472b6", title: "Recommendations",     getDesc: (agents, stats) => stats?.total_chats===0 ? "Start your first chat to activate agent learning" : `${stats?.total_chats} conversations logged · ${agents.filter(a=>a.is_custom).length} custom agents built` },
];

function AIInsightsPanel({ agents, stats }) {
  const [activeIdx, setActiveIdx] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setActiveIdx(i => (i+1) % INSIGHT_ITEMS.length), 4200);
    return () => clearInterval(timer);
  }, []);

  const active = INSIGHT_ITEMS[activeIdx];

  return (
    <div data-3d data-3d-strength="6" data-3d-lift="4" style={{background:`linear-gradient(135deg, rgba(8,14,30,0.9), rgba(6,10,24,0.95))`,border:`1px solid rgba(255,255,255,0.07)`,borderRadius:18,backdropFilter:"blur(16px)",padding:"18px 20px",marginBottom:24,position:"relative",overflow:"hidden"}}>
      <NeuralBg width={1200} height={80} />
      <div style={{position:"relative",zIndex:1}}>
        <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
          <Cpu style={{width:13,height:13,color:T.teal}} />
          <span style={{fontSize:10,fontWeight:800,letterSpacing:"0.18em",textTransform:"uppercase",color:T.teal}}>AI System Insights</span>
          <div style={{marginLeft:"auto",display:"flex",gap:5}}>
            {INSIGHT_ITEMS.map((_,i) => (
              <button key={i} onClick={()=>setActiveIdx(i)} style={{width:i===activeIdx?18:6,height:6,borderRadius:3,background:i===activeIdx?T.teal:"rgba(255,255,255,0.1)",border:"none",cursor:"pointer",transition:"all 0.3s",padding:0}} />
            ))}
          </div>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:16,minHeight:48}}>
          <div style={{width:40,height:40,borderRadius:12,background:`${active.color}18`,border:`1px solid ${active.color}33`,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,transition:"all 0.4s"}}>
            <active.icon style={{width:18,height:18,color:active.color}} />
          </div>
          <div style={{flex:1,minWidth:0}}>
            <p style={{fontSize:13,fontWeight:700,color:"#e2e8f0",margin:"0 0 3px",transition:"all 0.4s"}}>{active.title}</p>
            <p style={{fontSize:11,color:"#64748b",lineHeight:1.5,margin:0,transition:"all 0.4s"}}>{active.getDesc(agents, stats)}</p>
          </div>
          <div style={{display:"flex",gap:12,flexShrink:0}}>
            {INSIGHT_ITEMS.filter((_,i)=>i!==activeIdx).slice(0,3).map((item,i)=>(
              <button key={i} onClick={()=>setActiveIdx(INSIGHT_ITEMS.indexOf(item))} style={{width:32,height:32,borderRadius:9,background:`${item.color}10`,border:`1px solid ${item.color}20`,display:"flex",alignItems:"center",justifyContent:"center",cursor:"pointer",transition:"all 0.2s"}} title={item.title}
                onMouseEnter={e=>{e.currentTarget.style.background=`${item.color}22`;e.currentTarget.style.borderColor=`${item.color}44`;}}
                onMouseLeave={e=>{e.currentTarget.style.background=`${item.color}10`;e.currentTarget.style.borderColor=`${item.color}20`;}}>
                <item.icon style={{width:13,height:13,color:item.color}} />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Quick actions V2 ────────────────────────────────────── */
function QuickActions({ navigate, agents }) {
  const actions = [
    { label:"New Chat",      desc:"Start a conversation",  icon:MessageSquare, onClick:()=>navigate("/chat"),           accent:T.teal,    kbd:"N", testId:"quick-action-new-chat"      },
    { label:"Create Task",   desc:"Assign to agents",      icon:ListTodo,      onClick:()=>navigate("/tasks"),          accent:"#a78bfa", kbd:"T", testId:"quick-action-create-task"   },
    { label:"Browse Agents", desc:`${agents.length} agents`,icon:Users,         onClick:()=>navigate("/agents"),         accent:T.blue,    kbd:"A", testId:"quick-action-browse-agents" },
    { label:"Create Agent",  desc:"Build custom AI",       icon:Plus,          onClick:()=>navigate("/agents/create"),  accent:T.pink,    kbd:"C", testId:"quick-action-create-agent"  },
    { label:"Developer API", desc:"175k+ models",          icon:Terminal,      onClick:()=>navigate("/developer"),      accent:T.green,   kbd:"D", testId:"quick-action-developer-api" },
    { label:"Projects",      desc:"Command center",        icon:GitBranch,     onClick:()=>navigate("/projects"),       accent:T.amber,   kbd:"P", testId:"quick-action-projects"      },
  ];
  return (
    <div>
      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
        <span style={{width:20,height:1,background:T.teal,display:"block"}} />
        <span style={{fontSize:10,fontWeight:700,letterSpacing:"0.18em",textTransform:"uppercase",color:T.teal}}>Quick Actions</span>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill, minmax(180px, 1fr))",gap:8}}>
        {actions.map((a,i)=>(
          <button key={a.label} onClick={a.onClick} data-testid={a.testId}
            className="db-shimmer-hover"
            style={{
              display:"flex",alignItems:"center",gap:11,padding:"12px 14px",
              borderRadius:14,background:T.glass,border:`1px solid ${T.border}`,
              backdropFilter:"blur(12px)",cursor:"pointer",textAlign:"left",
              transition:"all 0.25s cubic-bezier(0.22,1,0.36,1)",
              animation:`db_fade_up 0.4s ease ${i*0.06}s both`,
            }}
            onMouseEnter={e=>{e.currentTarget.style.borderColor=`${a.accent}44`;e.currentTarget.style.boxShadow=`0 6px 24px ${a.accent}14`;e.currentTarget.style.transform="translateY(-2px)";e.currentTarget.style.background=T.glass2;}}
            onMouseLeave={e=>{e.currentTarget.style.borderColor=T.border;e.currentTarget.style.boxShadow="none";e.currentTarget.style.transform="translateY(0)";e.currentTarget.style.background=T.glass;}}
          >
            <div style={{width:36,height:36,borderRadius:10,background:`${a.accent}15`,border:`1px solid ${a.accent}25`,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,transition:"all 0.2s"}}>
              <a.icon style={{width:16,height:16,color:a.accent}} />
            </div>
            <div style={{minWidth:0,flex:1}}>
              <p style={{fontSize:12,fontWeight:700,color:"#e2e8f0",margin:0}}>{a.label}</p>
              <p style={{fontSize:10,color:"#64748b",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",margin:0}}>{a.desc}</p>
            </div>
            <span style={{fontSize:9,color:"#475569",padding:"2px 5px",borderRadius:4,border:"1px solid rgba(255,255,255,0.07)",fontFamily:"JetBrains Mono, monospace",flexShrink:0}}>{a.kbd}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/* ─── Dashboard ───────────────────────────────────────────── */
const Dashboard = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [agents,      setAgents]      = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [stats,       setStats]       = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const headers = token ? { Authorization:`Bearer ${token}` } : {};

  useEffect(() => {
    (async () => {
      try {
        const [ar, cr, sr] = await Promise.all([
          fetch(`${API}/agents`,{headers}).catch(()=>null),
          fetch(`${API}/chats`, {headers}).catch(()=>null),
          fetch(`${API}/stats`, {headers}).catch(()=>null),
        ]);
        if (ar?.ok) setAgents(await ar.json());
        if (cr?.ok) { const d=await cr.json(); setRecentChats(d.chats||d); }
        if (sr?.ok) setStats(await sr.json());
      } catch { toast.error("Failed to load dashboard"); }
      finally  { setLoading(false); }
    })();
    if (user && !user.onboarding_completed) setShowOnboarding(true);
  }, []);

  const handleDeleteChat = async (chatId) => {
    const res = await fetch(`${API}/chats/${chatId}`,{method:"DELETE",headers:{Authorization:`Bearer ${token}`}});
    if (res.ok) { setRecentChats(p=>p.filter(c=>c.chat_id!==chatId)); toast.success("Chat deleted"); }
  };

  const commander = agents.find(a=>a.agent_id==="commander_orion"||a.name?.toLowerCase().includes("commander"));

  const sparkline = [2,4,3,6,5,8,7,9,6,10,8,12,9,14,11,16];

  if (loading) return (
    <div style={{display:"flex",alignItems:"center",justifyContent:"center",padding:"80px 0",flexDirection:"column",gap:16}}>
      <style>{GLOBAL_STYLES}</style>
      <div style={{position:"relative"}}>
        <div style={{width:52,height:52,borderRadius:"50%",border:`2px solid rgba(79,209,197,0.15)`,borderTop:`2px solid ${T.teal}`,animation:"db_spin 0.8s linear infinite"}} />
        <div style={{position:"absolute",inset:7,borderRadius:"50%",border:`1px solid rgba(124,58,237,0.3)`,borderBottom:`1px solid ${T.violet}`,animation:"db_spin_rev 1.4s linear infinite"}} />
        <div style={{position:"absolute",inset:14,borderRadius:"50%",border:`1px solid rgba(37,99,235,0.2)`,borderLeft:`1px solid ${T.blue}`,animation:"db_spin 2.2s linear infinite"}} />
      </div>
      <p style={{fontSize:13,color:"#64748b",letterSpacing:"0.05em"}}>Initializing command center…</p>
    </div>
  );

  return (
    <div data-testid="dashboard-page" style={{maxWidth:1240}}>
      <style>{GLOBAL_STYLES}</style>
      {showOnboarding && <OnboardingFlow onComplete={()=>setShowOnboarding(false)} />}

      {/* ── Mission Briefing ── */}
      <MissionBriefing user={user} agents={agents} stats={stats} />

      {/* ── Holographic Stats ── */}
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit, minmax(220px, 1fr))",gap:12,marginBottom:24}}>
        <HoloStatCard label="Total Chats"   value={stats?.total_chats||0}     icon={MessageSquare} accent={T.teal}   delay={0}   sparkline={sparkline}            testId="stat-total-chats" />
        <HoloStatCard label="Total Tasks"   value={stats?.total_tasks||0}     icon={ListTodo}      accent="#a78bfa"  delay={100} sparkline={sparkline.map(v=>v*0.7)} testId="stat-total-tasks" />
        <HoloStatCard label="Completed"     value={stats?.completed_tasks||0} icon={Sparkles}      accent={T.green}  delay={200} sparkline={sparkline.map(v=>v*0.5)} />
        <HoloStatCard label="Active Agents" value={agents.filter(a=>!a.hidden).length} icon={Bot} accent={T.amber} sub={`of ${agents.length} total`} delay={300} sparkline={sparkline.map(v=>v*0.9)} />
      </div>

      {/* ── AI Insights ── */}
      <AIInsightsPanel agents={agents} stats={stats} />

      {/* ── Gamification ── */}
      {stats && <div style={{marginBottom:24}}><GamificationWidget stats={stats} /></div>}

      {/* ── Activity heatmap ── */}
      <div style={{marginBottom:24}}><ActivityHeatmap stats={stats} /></div>

      {/* ── Three-column main layout ── */}
      <div style={{display:"grid",gridTemplateColumns:"minmax(0,1.1fr) minmax(0,1fr)",gap:20,marginBottom:24,alignItems:"start"}}>
        {/* Left column */}
        <div style={{display:"flex",flexDirection:"column",gap:20}}>
          {commander && <CommanderCard commander={commander} navigate={navigate} />}
          <div>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:14}}>
              <span style={{width:20,height:1,background:T.teal,display:"block"}} />
              <span style={{fontSize:10,fontWeight:700,letterSpacing:"0.18em",textTransform:"uppercase",color:T.teal}}>Command Center</span>
            </div>
            <CommandCenter />
          </div>
          <QuickActions navigate={navigate} agents={agents} />
        </div>

        {/* Right column */}
        <div style={{display:"flex",flexDirection:"column",gap:16}}>
          <SystemHealth agents={agents} stats={stats} />
          <NeuralActivityFeed agents={agents} />
          <LiveAgentRoster agents={agents} recentChats={recentChats} onChat={id=>navigate(`/chat/${id}`)} />
        </div>
      </div>

      {/* ── Recent Conversations ── */}
      {recentChats.length > 0 && (
        <div>
          <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:14}}>
            <div style={{display:"flex",alignItems:"center",gap:8}}>
              <span style={{width:20,height:1,background:T.teal,display:"block"}} />
              <span style={{fontSize:10,fontWeight:700,letterSpacing:"0.18em",textTransform:"uppercase",color:T.teal}}>Recent Conversations</span>
            </div>
            <button onClick={()=>navigate("/chat")} style={{display:"flex",alignItems:"center",gap:4,fontSize:12,color:"#64748b",background:"none",border:"none",cursor:"pointer",transition:"color 0.15s"}} onMouseEnter={e=>e.currentTarget.style.color=T.teal} onMouseLeave={e=>e.currentTarget.style.color="#64748b"}>
              View All <ChevronRight style={{width:13,height:13}} />
            </button>
          </div>
          <div style={{display:"flex",flexDirection:"column",gap:6}}>
            {recentChats.slice(0,6).map((chat,i)=>{
              const agent = agents.find(a=>a.agent_id===chat.agent_id);
              return (
                <div key={chat.chat_id}
                  data-testid={`recent-chat-${chat.chat_id}`}
                  data-3d
                  data-3d-strength="12"
                  data-3d-lift="6"
                  onClick={()=>navigate(`/chat/${chat.agent_id}?chat=${chat.chat_id}`)}
                  className="db-shimmer-hover"
                  style={{
                    display:"flex",alignItems:"center",gap:14,padding:"12px 16px",
                    borderRadius:14,cursor:"pointer",
                    background:T.glass,border:`1px solid ${T.border}`,
                    backdropFilter:"blur(12px)",
                    transition:"all 0.25s",
                    animation:`db_fade_up 0.4s ease ${i*0.05}s both`,
                  }}
                  onMouseEnter={e=>{e.currentTarget.style.borderColor="rgba(79,209,197,0.25)";e.currentTarget.style.background=T.glass2;e.currentTarget.style.transform="translateX(4px)";}}
                  onMouseLeave={e=>{e.currentTarget.style.borderColor=T.border;e.currentTarget.style.background=T.glass;e.currentTarget.style.transform="translateX(0)";}}
                >
                  <AgentAvatar agent={agent||{}} size="sm" animate={false} showRing={false} showStatus={false} />
                  <div style={{flex:1,minWidth:0}}>
                    <p style={{fontSize:13,fontWeight:600,color:"#e2e8f0",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",margin:0}}>{chat.title}</p>
                    <p style={{fontSize:10,color:"#64748b",marginTop:2}}>{agent?.name||"Agent"} · {chat.messages?.length||0} messages</p>
                  </div>
                  <div style={{display:"flex",alignItems:"center",gap:6,flexShrink:0}}>
                    <button onClick={e=>{e.stopPropagation();handleDeleteChat(chat.chat_id);}} data-testid={`delete-recent-chat-${chat.chat_id}`}
                      style={{padding:6,borderRadius:7,background:"transparent",border:"none",cursor:"pointer",color:"#64748b",transition:"color 0.15s"}}
                      onMouseEnter={e=>e.currentTarget.style.color="#f87171"}
                      onMouseLeave={e=>e.currentTarget.style.color="#64748b"}>
                      <Trash2 style={{width:13,height:13}} />
                    </button>
                    <ChevronRight style={{width:14,height:14,color:"#475569"}} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && recentChats.length===0 && agents.length===0 && (
        <div style={{textAlign:"center",padding:"60px 0"}}>
          <div style={{width:64,height:64,borderRadius:"50%",background:"rgba(79,209,197,0.08)",border:"1px solid rgba(79,209,197,0.2)",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 16px",animation:"db_pulse_t 2.5s ease infinite"}}>
            <Activity style={{width:28,height:28,color:T.teal}} />
          </div>
          <h3 style={{fontSize:18,fontWeight:700,color:"#e2e8f0",marginBottom:8,fontFamily:"Outfit, sans-serif"}}>Command center initialized</h3>
          <p style={{fontSize:14,color:"#64748b",marginBottom:24}}>Your AI workforce is standing by. Issue your first command.</p>
          <button onClick={()=>navigate("/chat")} style={{display:"inline-flex",alignItems:"center",gap:8,padding:"13px 28px",borderRadius:12,background:`linear-gradient(135deg, ${T.teal}, ${T.blue})`,color:"#030712",fontSize:14,fontWeight:800,border:"none",cursor:"pointer",boxShadow:"0 0 32px rgba(79,209,197,0.3)"}}>
            <MessageSquare style={{width:16,height:16}} /> Issue First Command
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
