"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from "next-themes";
import { getQueryClient } from "@/lib/query-client";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

/**
 * App Providers
 * 
 * File: src/components/providers.tsx
 * 
 * Wraps the entire application with required providers.
 * Order matters - outer providers are available to inner ones.
 * 
 * Stack (outside to inside):
 * 1. ThemeProvider - Light/dark/system mode
 * 2. SessionProvider - NextAuth session
 * 3. QueryClientProvider - React Query
 * 4. TooltipProvider - Global tooltip config (0 delay)
 * 5. Toaster - Toast notifications (sonner)
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient();

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <SessionProvider>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider delayDuration={0}>
            {children}
            <Toaster />
          </TooltipProvider>
        </QueryClientProvider>
      </SessionProvider>
    </ThemeProvider>
  );
}
