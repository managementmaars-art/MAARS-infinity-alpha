"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * Inbox Hooks
 * 
 * React Query hooks for inbox threads, messages, and email sending.
 */

// ===========================================
// Types
// ===========================================

interface InboxThread {
  id: string;
  teamId: string;
  creatorId: string | null;
  creatorEmail: string;
  isRead: boolean;
  isArchived: boolean;
  lastMessageAt: string;
  createdAt: string;
  creator?: {
    id: string;
    name: string | null;
    email: string | null;
  };
  _count?: {
    messages: number;
  };
}

interface InboxMessage {
  id: string;
  threadId: string;
  direction: "INBOUND" | "OUTBOUND";
  from: string;
  to: string;
  subject: string | null;
  textBody: string | null;
  htmlBody: string | null;
  deliveryStatus: string;
  sentAt: string | null;
  receivedAt: string | null;
  createdAt: string;
}

interface SendEmailInput {
  creatorId: string;
  toEmail?: string;
  subject: string;
  text: string;
  html: string;
  threadId?: string;
  cc?: string[];
  bcc?: string[];
}

interface InboxFilters {
  isRead?: boolean;
  isArchived?: boolean;
  search?: string;
}

// ===========================================
// Query Keys
// ===========================================

export const inboxKeys = {
  all: ["inbox"] as const,
  threads: (teamId: string, filters?: InboxFilters) =>
    [...inboxKeys.all, "threads", teamId, filters ?? {}] as const,
  thread: (teamId: string, threadId: string) =>
    [...inboxKeys.all, "thread", teamId, threadId] as const,
  messages: (teamId: string, threadId: string) =>
    [...inboxKeys.all, "messages", teamId, threadId] as const,
};

// ===========================================
// Fetch Functions
// ===========================================

async function fetchThreads(teamId: string, filters?: InboxFilters): Promise<InboxThread[]> {
  const params = new URLSearchParams();
  if (filters?.isRead !== undefined) params.set("isRead", String(filters.isRead));
  if (filters?.isArchived !== undefined) params.set("isArchived", String(filters.isArchived));
  if (filters?.search) params.set("search", filters.search);

  const res = await fetch(`/api/teams/${teamId}/inbox/threads?${params}`);
  if (!res.ok) throw new Error("Failed to fetch threads");
  return res.json();
}

async function fetchMessages(teamId: string, threadId: string): Promise<InboxMessage[]> {
  const res = await fetch(`/api/teams/${teamId}/inbox/threads/${threadId}/messages`);
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}

async function sendEmail(
  teamId: string,
  input: SendEmailInput
): Promise<{ success: boolean; messageId: string; threadId: string }> {
  const res = await fetch(`/api/teams/${teamId}/inbox/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to send email");
  }
  return res.json();
}

// ===========================================
// Query Hooks
// ===========================================

/**
 * Fetch inbox threads with optional filters
 */
export function useInboxThreads(teamId: string | undefined, filters?: InboxFilters) {
  return useQuery({
    queryKey: inboxKeys.threads(teamId!, filters),
    queryFn: () => fetchThreads(teamId!, filters),
    enabled: !!teamId,
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Fetch messages in a thread
 */
export function useInboxMessages(teamId: string, threadId: string | null) {
  return useQuery({
    queryKey: inboxKeys.messages(teamId, threadId!),
    queryFn: () => fetchMessages(teamId, threadId!),
    enabled: !!teamId && !!threadId,
  });
}

// ===========================================
// Mutation Hooks
// ===========================================

/**
 * Send a single email
 */
export function useSendEmail(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: SendEmailInput) => sendEmail(teamId, input),
    onSuccess: () => {
      // Invalidate all inbox queries to refresh
      queryClient.invalidateQueries({ queryKey: ["inbox", "threads", teamId] });
      queryClient.invalidateQueries({ queryKey: ["inbox", "messages", teamId] });
    },
  });
}

/**
 * Mark thread as read
 */
export function useMarkThreadRead(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (threadId: string) => {
      const res = await fetch(`/api/teams/${teamId}/inbox/threads/${threadId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isRead: true }),
      });
      if (!res.ok) throw new Error("Failed to mark as read");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inboxKeys.threads(teamId) });
    },
  });
}

/**
 * Archive thread
 */
export function useArchiveThread(teamId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (threadId: string) => {
      const res = await fetch(`/api/teams/${teamId}/inbox/threads/${threadId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isArchived: true }),
      });
      if (!res.ok) throw new Error("Failed to archive");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inboxKeys.threads(teamId) });
    },
  });
}

/**
 * Generate personalization previews
 */
export function useGeneratePreviews(teamId: string) {
  return useMutation({
    mutationFn: async (input: {
      subject: string;
      body: string;
      recipients: Array<{ creatorId: string; email: string }>;
    }) => {
      const res = await fetch(`/api/teams/${teamId}/inbox/personalization/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to generate previews");
      }
      return res.json() as Promise<{
        previews: Array<{
          creatorId: string;
          email: string;
          name: string | null;
          subject: string;
          message: string;
          explanation: string;
          error?: string;
        }>;
      }>;
    },
  });
}
