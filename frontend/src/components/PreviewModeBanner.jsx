/**
 * PreviewModeBanner — fixed top bar shown when admin is in client preview mode.
 * Lets the admin switch plans and exit preview.
 */
import { Eye, EyeOff, X } from "lucide-react";
import { usePreviewMode, PREVIEW_PLANS } from "./PreviewModeContext";

export default function PreviewModeBanner() {
  const { previewMode, previewPlan, switchPreviewPlan, exitPreview } = usePreviewMode();

  if (!previewMode) return null;

  const plan = PREVIEW_PLANS[previewPlan] || PREVIEW_PLANS.free;

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[9999] flex items-center gap-3 px-4 py-2 bg-amber-950/95 border-b border-amber-500/40 backdrop-blur-sm no-print"
      data-testid="preview-mode-banner"
    >
      {/* Icon + label */}
      <div className="flex items-center gap-2 shrink-0">
        <Eye className="w-4 h-4 text-amber-400" />
        <span className="text-amber-300 text-[12px] font-semibold">Client Preview</span>
        <span className="text-amber-500/60 text-[11px]">— viewing as a</span>
        <span className={`text-[11px] font-bold ${plan.color}`}>{plan.label} subscriber</span>
      </div>

      {/* Divider */}
      <div className="h-4 w-px bg-amber-500/30 shrink-0" />

      {/* Plan switcher */}
      <div className="flex items-center gap-1 flex-wrap">
        <span className="text-[10px] text-amber-500/60 mr-1">Switch plan:</span>
        {Object.entries(PREVIEW_PLANS).map(([key, p]) => (
          <button
            key={key}
            onClick={() => switchPreviewPlan(key)}
            className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold transition-all ${
              previewPlan === key
                ? `${p.bg} ${p.color} ring-1 ring-current/40`
                : "text-amber-600/70 hover:text-amber-400 hover:bg-amber-500/10"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Hint */}
      <span className="text-[10px] text-amber-600/50 hidden sm:block shrink-0">
        Admin nav &amp; features are hidden
      </span>

      {/* Exit button */}
      <button
        onClick={exitPreview}
        className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-[11px] font-semibold transition-colors shrink-0"
        data-testid="exit-preview-btn"
      >
        <X className="w-3.5 h-3.5" />
        Exit Preview
      </button>
    </div>
  );
}
