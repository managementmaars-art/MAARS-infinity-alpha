"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * User Profile Hooks
 * 
 * React Query hooks for user profile management including
 * notification settings and sending domain preferences.
 */

// ===========================================
// Types
// ===========================================

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  theme: "light" | "dark" | "system";
  notifyInboundEmail: boolean;
  sendFromDomain: string | null;
  createdAt: string;
}

interface UpdateUserInput {
  name?: string;
  image?: string | null;
  theme?: "light" | "dark" | "system";
  notifyInboundEmail?: boolean;
  sendFromDomain?: string | null;
}

// ===========================================
// Query Keys
// ===========================================

export const userKeys = {
  all: ["user"] as const,
  profile: ["user", "profile"] as const,
};

// ===========================================
// Fetch Functions
// ===========================================

async function fetchUserProfile(): Promise<UserProfile> {
  const res = await fetch("/api/users/me");
  if (!res.ok) {
    throw new Error("Failed to fetch user profile");
  }
  return res.json();
}

async function updateUserProfile(input: UpdateUserInput): Promise<UserProfile> {
  const res = await fetch("/api/users/me", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to update profile");
  }
  return res.json();
}

// ===========================================
// Query Hooks
// ===========================================

/**
 * Fetch current user profile
 */
export function useUserProfile() {
  return useQuery({
    queryKey: userKeys.profile,
    queryFn: fetchUserProfile,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Update user profile (name, theme, notifications, domain)
 */
export function useUpdateUserProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateUserProfile,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(userKeys.profile, updatedUser);
      // Also invalidate to ensure all components refetch fresh data
      queryClient.invalidateQueries({ queryKey: userKeys.profile });
    },
  });
}
