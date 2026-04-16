"use client";

import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

/**
 * Theme Toggle Component
 * 
 * A three-option segmented control for switching between light, dark, and system themes.
 * Uses icon-only buttons with tooltips for a clean, minimal appearance.
 * 
 * Design: Linear-style with subtle backgrounds and smooth transitions.
 * 
 * Features:
 * - Icon-only buttons (Sun, Moon, Monitor)
 * - Tooltips on hover
 * - Active state with background highlight
 * - Optional: Persist to database via user profile hook
 */

const themes = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
] as const;

type ThemeValue = "light" | "dark" | "system";

interface ThemeToggleProps {
  /** Optional callback when theme changes (e.g., to persist to database) */
  onThemeChange?: (theme: ThemeValue) => void;
}

export function ThemeToggle({ onThemeChange }: ThemeToggleProps = {}) {
  const { theme, setTheme } = useTheme();

  function handleThemeChange(newTheme: ThemeValue) {
    setTheme(newTheme);
    onThemeChange?.(newTheme);
  }

  return (
    <div className="flex items-center gap-0.5 p-1 rounded-lg bg-secondary/50 border border-border">
      {themes.map(({ value, icon: Icon, label }) => (
        <Tooltip key={value}>
          <TooltipTrigger asChild>
            <button
              onClick={() => handleThemeChange(value)}
              className={cn(
                "flex items-center justify-center w-7 h-7 rounded-md transition-all duration-200 cursor-pointer",
                theme === value
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-background/50"
              )}
              aria-label={`Switch to ${label} theme`}
            >
              <Icon className="h-3.5 w-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" sideOffset={8}>
            {label}
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  );
}

/**
 * Example with database persistence:
 * 
 * import { useUpdateUserProfile } from "@/hooks/use-user";
 * 
 * export function ThemeToggleWithPersistence() {
 *   const { mutate: updateProfile } = useUpdateUserProfile();
 *   
 *   return (
 *     <ThemeToggle 
 *       onThemeChange={(theme) => updateProfile({ theme })} 
 *     />
 *   );
 * }
 */
