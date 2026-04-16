"use client";

import { useQuery } from "@tanstack/react-query";
import type { AvailableDomainsResponse } from "@/app/api/users/me/available-domains/route";

/**
 * Available Domains Hook
 * 
 * Fetches verified domains from all teams the user belongs to.
 * Used in the email settings domain selector.
 */

async function fetchAvailableDomains(): Promise<AvailableDomainsResponse> {
  const res = await fetch("/api/users/me/available-domains");
  if (!res.ok) {
    throw new Error("Failed to fetch available domains");
  }
  return res.json();
}

export const availableDomainsKeys = {
  all: ["availableDomains"] as const,
};

export function useAvailableDomains() {
  return useQuery({
    queryKey: availableDomainsKeys.all,
    queryFn: fetchAvailableDomains,
  });
}
