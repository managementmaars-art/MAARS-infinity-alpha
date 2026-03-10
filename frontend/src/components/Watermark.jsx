import { useBranding } from "./BrandingProvider";

export const Watermark = () => {
  const branding = useBranding();
  
  return (
    <div className="fixed bottom-3 right-4 z-30 pointer-events-none select-none">
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-950/70 backdrop-blur-sm border border-white/[0.04]">
        <img src="/branding/maars-logo.jpeg" alt="MAARS GC" className="w-5 h-5 rounded object-cover" />
        <div className="flex flex-col">
          <span className="text-[9px] text-zinc-500 font-semibold tracking-wider font-['Outfit'] leading-tight">MAARS COMMAND</span>
          <span className="text-[7px] text-zinc-600 tracking-wide leading-tight">by MAARS Global Corporation</span>
        </div>
      </div>
    </div>
  );
};
