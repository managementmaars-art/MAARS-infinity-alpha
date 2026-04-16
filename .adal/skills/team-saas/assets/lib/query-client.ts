"use client";

import { QueryClient } from "@tanstack/react-query";

/**
 * React Query client configuration
 * 
 * Features:
 * - 30s stale time (data considered fresh)
 * - Refetch on window focus
 * - Singleton pattern for browser
 */

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Data is considered fresh for 30 seconds
        staleTime: 30 * 1000,
        // Refetch when user switches back to the tab
        refetchOnWindowFocus: true,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

export function getQueryClient() {
  // Server: always make a new query client
  if (typeof window === "undefined") {
    return makeQueryClient();
  }
  
  // Browser: make a new query client if we don't already have one
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient();
  }
  return browserQueryClient;
}
