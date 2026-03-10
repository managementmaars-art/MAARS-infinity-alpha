import { useBranding } from "./BrandingProvider";

export const Watermark = () => {
  const branding = useBranding();
  
  return (
    <div className="fixed bottom-0 left-0 right-0 z-30 pointer-events-none select-none flex justify-center pb-2">
      <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#070721]/70 backdrop-blur-sm border border-blue-500/[0.06]">
        <img 
          src="/branding/maars-logo.jpeg" 
          alt="MAARS GC" 
          className="w-4 h-4 rounded-full object-cover"
        />
        <span className="text-[10px] text-blue-300/50 font-medium tracking-wider font-['Outfit']">
          MAARS GLOBAL CORPORATION
        </span>
      </div>
    </div>
  );
};
