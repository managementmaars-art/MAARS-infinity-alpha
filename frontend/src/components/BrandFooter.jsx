import { Bot } from "lucide-react";

export const BrandFooter = ({ className = "" }) => (
  <footer className={`py-4 px-4 border-t border-white/10 ${className}`} data-testid="brand-footer">
    <div className="flex items-center justify-center gap-2">
      <div className="w-5 h-5 rounded bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center flex-shrink-0">
        <Bot className="w-3 h-3 text-white" />
      </div>
      <span className="text-xs text-zinc-500">MAARS Command by MAARS Global Corporation &copy; 2026</span>
    </div>
  </footer>
);
