/**
 * MAARS Design Tokens — single source of truth for the admin + client visual language.
 *
 * Every admin page (PricingManager, CustomPackages, Revenue-by-Category,
 * Quality Gate Dashboard, etc.) used to hardcode Tailwind classes like
 * `text-emerald-400 bg-emerald-500/10`. That meant renaming the "chat"
 * color meant sweeping 15+ files. These tokens collapse the palette +
 * category-track mappings into one place so:
 *
 *   - A category's color changes in ONE file
 *   - Every admin tab, client page, 3D scene, and email template stays in sync
 *   - New pages pick up the current look by importing these tokens, not
 *     by eyeballing another page's Tailwind classes
 *
 * Both Tailwind-class strings (for JSX) AND raw hex values (for inline
 * styles / 3D scene uniforms / CSS-in-JS) are exposed so every render
 * target can consume the same source.
 */

// ── Per-category tracks ─────────────────────────────────────────────
// The 8 dedicated workload tracks + "general" untagged pool. Order is
// stable — used by the top strip in Pricing Manager, the Revenue by
// Category panel, the Media Budget Calculator mix sliders, and the
// per-plan Deliverables editor.
export const TRACKS = [
  { key: "chat",      label: "Chat",         color: "emerald", hex: "#4fd1c5",
    routing: "Free-first · escalates to Claude/GPT-4 on complex reasoning" },
  { key: "code",      label: "Code / Vibe",  color: "violet",  hex: "#a78bfa",
    routing: "DeepSeek Coder · Qwen Coder · escalates to Claude Opus on architecture" },
  { key: "image_std", label: "Image Std",    color: "rose",    hex: "#fda4af",
    routing: "Pollinations (free) · escalates to Flux on finer detail" },
  { key: "image_hd",  label: "Image HD",     color: "fuchsia", hex: "#e879f9",
    routing: "Flux HD primary · premium-tier default" },
  { key: "video",     label: "Video",        color: "amber",   hex: "#fbbf24",
    routing: "Fal LTX · escalates to Sora/Runway for cinematic tier" },
  { key: "voiceover", label: "Voiceover",    color: "sky",     hex: "#38bdf8",
    routing: "ElevenLabs premium voices · studio-quality default" },
  { key: "tts",       label: "TTS",          color: "cyan",    hex: "#22d3ee",
    routing: "Edge TTS (free) · escalates to ElevenLabs if client flags quality" },
  { key: "stt",       label: "STT",          color: "teal",    hex: "#2dd4bf",
    routing: "Groq Whisper (free) · Whisper Large V3 · near-premium accuracy" },
];

// Lookups
export const TRACK_BY_KEY = Object.fromEntries(TRACKS.map(t => [t.key, t]));
export const trackColor   = (key) => (TRACK_BY_KEY[key] || TRACKS[0]).color;
export const trackHex     = (key) => (TRACK_BY_KEY[key] || TRACKS[0]).hex;
export const trackLabel   = (key) => (TRACK_BY_KEY[key] || TRACKS[0]).label;
export const trackRouting = (key) => (TRACK_BY_KEY[key] || TRACKS[0]).routing;

// Tailwind class fragments — used when rendering dynamic per-track
// styles. Tailwind's JIT needs the full class names to appear in the
// source at build time, so we enumerate all 8 tracks explicitly.
export const TRACK_TINT_CLASSES = {
  chat:      "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  code:      "text-violet-400  bg-violet-500/10  border-violet-500/30",
  image_std: "text-rose-400    bg-rose-500/10    border-rose-500/30",
  image_hd:  "text-fuchsia-400 bg-fuchsia-500/10 border-fuchsia-500/30",
  video:     "text-amber-400   bg-amber-500/10   border-amber-500/30",
  voiceover: "text-sky-400     bg-sky-500/10     border-sky-500/30",
  tts:       "text-cyan-400    bg-cyan-500/10    border-cyan-500/30",
  stt:       "text-teal-400    bg-teal-500/10    border-teal-500/30",
  general:   "text-zinc-400    bg-zinc-500/10    border-white/10",
};
export const TRACK_TEXT_CLASSES = {
  chat:      "text-emerald-400",
  code:      "text-violet-400",
  image_std: "text-rose-300",
  image_hd:  "text-fuchsia-400",
  video:     "text-amber-400",
  voiceover: "text-sky-400",
  tts:       "text-cyan-400",
  stt:       "text-teal-400",
  general:   "text-zinc-400",
};

// ── Semantic palette ────────────────────────────────────────────────
// Status semantics — margin health, quality-gate verdicts, cost drift.
export const STATUS = {
  success:  { hex: "#34d399", tw: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" },
  warning:  { hex: "#fbbf24", tw: "text-amber-400   bg-amber-500/10   border-amber-500/30"   },
  danger:   { hex: "#f87171", tw: "text-rose-400    bg-rose-500/10    border-rose-500/30"    },
  info:     { hex: "#60a5fa", tw: "text-blue-400    bg-blue-500/10    border-blue-500/30"    },
  muted:    { hex: "#71717a", tw: "text-zinc-400    bg-zinc-500/10    border-white/10"       },
};

// Margin thresholds for the status color mapping. Kept here so every
// surface that renders a margin percentage picks the same cutoffs.
export const MARGIN_THRESHOLDS = {
  excellent: 90,   // >= 90% → green
  acceptable: 50,  // >= 50% → amber
  // < 50% → rose (loss zone)
};
export const marginStatus = (pct) => {
  if (pct == null) return STATUS.muted;
  if (pct >= MARGIN_THRESHOLDS.excellent) return STATUS.success;
  if (pct >= MARGIN_THRESHOLDS.acceptable) return STATUS.warning;
  return STATUS.danger;
};

// ── Brand palette ───────────────────────────────────────────────────
// Hero/landing 3D scene colors. Match these if you build new 3D assets
// so the composited look stays unified.
export const BRAND = {
  bg:      "#030712",   // deep void
  teal:    "#4fd1c5",   // primary accent
  violet:  "#7c3aed",   // secondary accent
  blue:    "#2563eb",   // tertiary accent
  glass:   "rgba(255,255,255,0.04)",
  border:  "rgba(255,255,255,0.08)",
};

// ── Spacing / typography ────────────────────────────────────────────
// Keep shared size tokens explicit so cards/panels/tables stay visually
// aligned across the admin and client surfaces. Tailwind arbitrary
// values (`p-[12px]`) drift; these anchor the system.
export const SPACING = {
  cardPadding:   "p-4",
  cardPaddingLg: "p-6",
  stripGap:      "gap-2",
  stripGapLg:    "gap-3",
  sectionGap:    "space-y-4",
  sectionGapLg:  "space-y-6",
};
export const TYPE = {
  pageTitle:  "text-2xl font-bold text-white font-['Outfit']",
  cardTitle:  "text-white font-['Outfit'] font-semibold",
  sectionTitle: "text-[10px] text-zinc-400 font-semibold uppercase tracking-wide",
  label:      "text-zinc-400 text-xs",
  hint:       "text-[9px] text-zinc-600",
  valueBig:   "text-2xl font-bold text-white font-mono",
  valueMd:    "text-lg font-bold font-mono",
  valueSm:    "text-sm font-bold font-mono",
};

// ── Category helper for admin dropdowns ─────────────────────────────
// Used by CustomPackagesTab + client PricingPage tabs so the dropdown
// options stay canonical across both.
export const CATEGORY_OPTIONS = [
  { value: "general",   label: "General (any track)" },
  ...TRACKS.map(t => ({ value: t.key, label: t.label })),
];
