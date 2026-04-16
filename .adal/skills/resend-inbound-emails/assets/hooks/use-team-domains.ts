"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * Team Domain Management Hooks
 * 
 * React Query hooks for managing custom sending domains via Resend API.
 */

// ===========================================
// Types
// ===========================================

interface DnsRecord {
  type: string;
  name: string;
  value: string;
  priority?: number;
  status?: string;
}

interface TeamDomain {
  id: string;
  teamId: string;
  resendDomainId: string;
  domain: string;
  status: "not_started" | "pending" | "verified" | "invalid";
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  records?: DnsRecord[];
}

interface DomainWithRecords extends TeamDomain {
  records: DnsRecord[];
}

// ===========================================
// Query Keys
// ===========================================

export const teamDomainKeys = {
  all: (teamId: string) => ["teamDomains", teamId] as const,
  detail: (teamId: string, domainId: string) => ["teamDomains", teamId, domainId] as const,
};

// ===========================================
// Fetch Functions
// ===========================================

async function fetchDomains(teamId: string): Promise<DomainWithRecords[]> {
  const res = await fetch(`/api/teams/${teamId}/domains`);
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to fetch domains");
  }
  return res.json();
}

async function fetchDomainDetails(
  teamId: string,
  domainId: string
): Promise<DomainWithRecords> {
  const res = await fetch(`/api/teams/${teamId}/domains/${domainId}`);
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to fetch domain");
  }
  return res.json();
}

// ===========================================
// Query Hooks
// ===========================================

/**
 * Fetch all domains for a team
 */
export function useTeamDomains(teamId: string | undefined) {
  return useQuery({
    queryKey: teamDomainKeys.all(teamId!),
    queryFn: () => fetchDomains(teamId!),
    enabled: !!teamId,
  });
}

/**
 * Fetch domain details with DNS records
 */
export function useDomainDetails(teamId: string, domainId: string | null) {
  return useQuery({
    queryKey: teamDomainKeys.detail(teamId, domainId!),
    queryFn: () => fetchDomainDetails(teamId, domainId!),
    enabled: !!teamId && !!domainId,
  });
}

// ===========================================
// Mutation Hooks
// ===========================================

/**
 * Add a new domain
 */
export function useAddDomain(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (domain: string) => {
      const res = await fetch(`/api/teams/${teamId}/domains`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to add domain");
      }
      return res.json() as Promise<{ domain: TeamDomain; records: DnsRecord[] }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.all(teamId) });
    },
  });
}

/**
 * Verify domain DNS records
 */
export function useVerifyDomain(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (domainId: string) => {
      const res = await fetch(`/api/teams/${teamId}/domains/${domainId}/verify`, {
        method: "POST",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Verification failed");
      }
      return res.json() as Promise<{ domain: TeamDomain; records: DnsRecord[]; message: string }>;
    },
    onSuccess: (_, domainId) => {
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.all(teamId) });
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.detail(teamId, domainId) });
    },
  });
}

/**
 * Activate domain (makes it the active sending domain)
 */
export function useActivateDomain(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (domainId: string) => {
      const res = await fetch(`/api/teams/${teamId}/domains/${domainId}/activate`, {
        method: "PUT",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Activation failed");
      }
      return res.json() as Promise<{ domain: TeamDomain }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.all(teamId) });
    },
  });
}

/**
 * Deactivate domain
 */
export function useDeactivateDomain(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (domainId: string) => {
      const res = await fetch(`/api/teams/${teamId}/domains/${domainId}/activate`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Deactivation failed");
      }
      return res.json() as Promise<{ domain: TeamDomain }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.all(teamId) });
    },
  });
}

/**
 * Delete domain
 */
export function useDeleteDomain(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (domainId: string) => {
      const res = await fetch(`/api/teams/${teamId}/domains/${domainId}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Delete failed");
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamDomainKeys.all(teamId) });
    },
  });
}
