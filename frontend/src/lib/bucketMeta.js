/* Per-bucket display metadata — shared between WalletDashboard.jsx,
 * CreditsDisplay.jsx, and PricingPage.jsx so the 7 credit pools render
 * with the same icon, order, and hint text everywhere.
 *
 * Backend canonical order (services/billing/credit_buckets.py):
 *   chat → vibe → agent_sop → image → video → voice → stt → general
 */
import {
  MessageSquare,
  Code2,
  Users,
  Image as ImageIcon,
  Film,
  Mic,
  Headphones,
  Coins,
} from "lucide-react";

/**
 * Canonical bucket definitions — the order here is the render order.
 * Each entry: { key, label, icon, accent, hint }
 *   - accent is a string; WalletDashboard/PricingPage resolve it to
 *     the brand palette locally so we don't import color tokens.
 */
export const BUCKETS = [
  {
    key: "chat",
    label: "Chat",
    icon: MessageSquare,
    accent: "teal",
    hint: "Text generation through the universal gateway (GPT / Claude / Gemini / 22+ providers)",
  },
  {
    key: "vibe",
    label: "Vibe Coding",
    icon: Code2,
    accent: "violet",
    hint: "Full-stack app generation & iterative code edits (Claude / DeepSeek-Coder / Codestral / Qwen-Coder)",
  },
  {
    key: "agent_sop",
    label: "Agent Runs",
    icon: Users,
    accent: "blue",
    hint: "Full Office SOP runs (6-step pipelines: understand → research → plan → produce → verify → deliver)",
  },
  {
    key: "image",
    label: "Images",
    icon: ImageIcon,
    accent: "green",
    hint: "Image generation (Pollinations free → FLUX / DALL-E / Gemini / SDXL across 14 providers)",
  },
  {
    key: "video",
    label: "Videos",
    icon: Film,
    accent: "amber",
    hint: "Video generation (Fal LTX / CogVideoX / Hailuo / Kling / Veo / Sora across 13 providers)",
  },
  {
    key: "voice",
    label: "Voice",
    icon: Mic,
    accent: "red",
    hint: "Text-to-speech voice-over (Edge free → ElevenLabs multilingual — 29 languages)",
  },
  {
    key: "stt",
    label: "Transcription",
    icon: Headphones,
    accent: "mute",
    hint: "Speech-to-text (Groq Whisper v3-turbo / Deepgram Nova-2 / OpenAI Whisper)",
  },
  {
    key: "general",
    label: "General",
    icon: Coins,
    accent: "violet",
    hint: "Flexible fallback pool — covers any modality if your plan allows bucket spillover",
  },
];


/** Get a pool's {balance, reserved} from a wallet.buckets map; defaults to zero. */
export function getPool(buckets, key) {
  const p = (buckets || {})[key];
  if (!p) return { balance: 0, reserved: 0 };
  return {
    balance: Number(p.balance || 0),
    reserved: Number(p.reserved || 0),
  };
}


/** Format a credit number for display (thousands separator, falls through safely). */
export function fmtCredits(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "—";
  return v.toLocaleString();
}


/** Given the bucket_allowances map from /plans, return a sorted [[key, allowance], …]
 *  array in the canonical order, skipping zero-allowance buckets so the pricing
 *  card doesn't waste space on "0 STT" lines for plans that don't grant it. */
export function sortedAllowanceEntries(allowances, { dropZero = true } = {}) {
  const map = allowances || {};
  const out = [];
  for (const b of BUCKETS) {
    const v = Number(map[b.key] || 0);
    if (dropZero && v <= 0) continue;
    out.push([b.key, v]);
  }
  return out;
}
