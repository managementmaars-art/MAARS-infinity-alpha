import { useBranding } from "./BrandingProvider";

export const Watermark = () => {
  const branding = useBranding();
  const footer = branding.footer_text || "MAARS Global Corporation";
  
  return (
    <div className="fixed bottom-0 left-0 right-0 z-30 pointer-events-none select-none flex justify-center pb-2">
      <div className="px-3 py-1 rounded-full bg-zinc-900/60 backdrop-blur-sm border border-white/[0.04]">
        <span className="text-[10px] text-zinc-600 font-medium tracking-wide">{footer}</span>
      </div>
    </div>
  );
};
