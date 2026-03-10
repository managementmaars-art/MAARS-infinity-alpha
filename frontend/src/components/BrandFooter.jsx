import { Bot } from "lucide-react";
import { useBranding } from "./BrandingProvider";

export const BrandFooter = ({ className = "" }) => {
  const branding = useBranding();
  const name = branding.platform_name || "MAARS ∞";
  const footer = branding.footer_text || "MAARS Global Corporation";

  return (
    <footer className={`py-4 px-4 border-t border-white/10 ${className}`} data-testid="brand-footer">
      <div className="flex items-center justify-center gap-2">
        {branding.logo_url ? (
          <img
            src={branding.logo_url.startsWith("/api") ? `${process.env.REACT_APP_BACKEND_URL}${branding.logo_url}` : branding.logo_url}
            alt={name}
            className="h-5 w-5 object-contain rounded"
            onError={(e) => { e.target.style.display = "none"; }}
          />
        ) : (
          <div className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${branding.primary_color}, ${branding.accent_color})` }}>
            <Bot className="w-3 h-3 text-white" />
          </div>
        )}
        <span className="text-xs text-zinc-500">{name} by {footer} &copy; {new Date().getFullYear()}</span>
      </div>
    </footer>
  );
};
