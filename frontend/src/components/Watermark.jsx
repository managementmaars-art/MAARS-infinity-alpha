export const Watermark = () => (
  <div className="fixed bottom-4 right-4 z-40 pointer-events-none select-none">
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-900/80 backdrop-blur-sm border border-white/[0.06]">
      <span className="text-[12px] text-zinc-400 font-medium tracking-wide">MAARS Global Corporation</span>
    </div>
  </div>
);
