"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * Teams Hooks Template
 * 
 * React Query hooks for team management.
 * 
 * Pattern: Simple invalidation on success (no optimistic updates).
 * This is the pattern used in the actual codebase - simpler and more reliable.
 */

// ===========================================
// Types
// ===========================================

interface Team {
  id: string;
  name: string;
  slug: string;
  logo: string | null;
  role: "ADMIN" | "MEMBER";
  memberCount: number;
  createdAt: string;
}

interface CreateTeamInput {
  name: string;
  logo?: string;
}

interface UpdateTeamInput {
  name?: string;
  logo?: string;
}

// ===========================================
// Query Keys (Factory Pattern)
// ===========================================

export const teamKeys = {
  all: ["teams"] as const,
  lists: () => [...teamKeys.all, "list"] as const,
  details: () => [...teamKeys.all, "detail"] as const,
  detail: (id: string) => [...teamKeys.details(), id] as const,
  members: (id: string) => [...teamKeys.detail(id), "members"] as const,
};

export const invitationKeys = {
  all: (teamId: string) => [...teamKeys.detail(teamId), "invitations"] as const,
};

// ===========================================
// Fetch Functions
// ===========================================

async function fetchTeams(): Promise<Team[]> {
  const res = await fetch("/api/teams");
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to fetch teams");
  }
  return res.json();
}

async function fetchTeam(teamId: string): Promise<Team> {
  const res = await fetch(`/api/teams/${teamId}`);
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to fetch team");
  }
  return res.json();
}

async function createTeam(input: CreateTeamInput): Promise<Team> {
  const res = await fetch("/api/teams", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to create team");
  }
  return res.json();
}

async function updateTeam(teamId: string, input: UpdateTeamInput): Promise<Team> {
  const res = await fetch(`/api/teams/${teamId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to update team");
  }
  return res.json();
}

async function deleteTeam(teamId: string): Promise<void> {
  const res = await fetch(`/api/teams/${teamId}`, { method: "DELETE" });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to delete team");
  }
}

// ===========================================
// Query Hooks
// ===========================================

/**
 * Fetch all teams for the current user
 */
export function useTeams() {
  return useQuery({
    queryKey: teamKeys.lists(),
    queryFn: fetchTeams,
  });
}

/**
 * Fetch a single team by ID
 */
export function useTeam(teamId: string | null) {
  return useQuery({
    queryKey: teamKeys.detail(teamId!),
    queryFn: () => fetchTeam(teamId!),
    enabled: !!teamId,
  });
}

// ===========================================
// Mutation Hooks
// ===========================================

/**
 * Create a new team
 */
export function useCreateTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTeam,
    onSuccess: (newTeam) => {
      // Invalidate teams list to refetch
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() });
      // Pre-populate detail cache
      queryClient.setQueryData(teamKeys.detail(newTeam.id), newTeam);
    },
  });
}

/**
 * Update a team
 */
export function useUpdateTeam(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: UpdateTeamInput) => updateTeam(teamId, input),
    onSuccess: (updatedTeam) => {
      // Invalidate all team queries
      queryClient.invalidateQueries({ 
        queryKey: teamKeys.all,
        refetchType: "all",
      });
      // Update detail cache
      queryClient.setQueryData(teamKeys.detail(teamId), updatedTeam);
    },
  });
}

/**
 * Delete a team
 */
export function useDeleteTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteTeam,
    onSuccess: (_data, teamId) => {
      // Invalidate teams list
      queryClient.invalidateQueries({ queryKey: teamKeys.lists() });
      // Remove detail cache
      queryClient.removeQueries({ queryKey: teamKeys.detail(teamId) });
    },
  });
}

// ===========================================
// Invitation Hooks
// ===========================================

interface Invitation {
  id: string;
  email: string;
  role: "ADMIN" | "MEMBER";
  token: string;
  expiresAt: string;
  createdAt: string;
  inviter: {
    name: string | null;
    email: string;
  };
}

async function fetchInvitations(teamId: string): Promise<Invitation[]> {
  const res = await fetch(`/api/teams/${teamId}/invitations`);
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to fetch invitations");
  }
  return res.json();
}

/**
 * Fetch team invitations
 */
export function useInvitations(teamId: string | undefined) {
  return useQuery({
    queryKey: invitationKeys.all(teamId!),
    queryFn: () => fetchInvitations(teamId!),
    enabled: !!teamId,
    staleTime: 0, // Always refetch
    refetchOnWindowFocus: true,
  });
}

/**
 * Returns a function to invalidate invitations
 */
export function useInvalidateInvitations(teamId: string) {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.invalidateQueries({ queryKey: invitationKeys.all(teamId) });
  };
}
