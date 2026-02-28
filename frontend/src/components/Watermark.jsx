import { Sparkles } from "lucide-react";

export const Watermark = () => (
  <div className="fixed bottom-4 right-4 z-40 flex flex-col items-end gap-1.5 pointer-events-none select-none">
    <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-zinc-900/90 backdrop-blur-sm border border-white/5 shadow-lg">
      <Sparkles className="w-4 h-4 text-indigo-400" />
      <span className="text-[12px] text-zinc-300 font-medium tracking-wide">Powered by GPT-5.2, Claude, Gemini, Sora 2, DALL-E 3 & Whisper</span>
    </div>
    <span className="text-[11px] text-zinc-500 font-medium pr-1 tracking-wide">MAARS Global Corporation</span>
  </div>
);
