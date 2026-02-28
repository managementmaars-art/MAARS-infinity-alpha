import { Sparkles } from "lucide-react";

export const Watermark = () => (
  <div className="fixed bottom-4 right-4 z-40 flex flex-col items-end gap-1.5 pointer-events-none select-none">
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900/80 backdrop-blur-sm border border-white/5">
      <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
      <span className="text-[11px] text-zinc-400 font-medium">Powered by GPT-5.2, Claude & Gemini</span>
    </div>
    <span className="text-[10px] text-zinc-600 pr-1">MAARS Global Corporation</span>
  </div>
);
