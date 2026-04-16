"use client";

import { useEffect, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { inboxCreatorKeys } from "./use-inbox-creators";

/**
 * Inbox Polling Hook
 * 
 * Polls for new inbox messages and shows toast notifications.
 * Uses polling for reliability over SSE (works with serverless).
 */

type InboxUpdate = {
  id: string;
  creatorId: string | null;
  creatorName: string;
  subject: string | null;
  preview: string;
  receivedAt: string;
};

type InboxUpdatesResponse = {
  newMessages: InboxUpdate[];
  timestamp: string;
};

interface UseInboxPollingOptions {
  interval?: number;  // Default: 10000ms (10 seconds)
  enabled?: boolean;  // Default: true
}

export function useInboxPolling(
  teamId: string | undefined,
  options?: UseInboxPollingOptions
) {
  const { interval = 10000, enabled = true } = options ?? {};
  const queryClient = useQueryClient();
  const router = useRouter();
  const lastCheckRef = useRef<string | null>(null);
  const seenMessageIdsRef = useRef<Set<string>>(new Set());

  const checkForUpdates = useCallback(async () => {
    if (!teamId) return;

    const since = lastCheckRef.current || new Date(Date.now() - 15000).toISOString();
    
    const res = await fetch(
      `/api/teams/${teamId}/inbox/updates?since=${encodeURIComponent(since)}`
    );

    if (!res.ok) return;

    const data: InboxUpdatesResponse = await res.json();
    lastCheckRef.current = data.timestamp;

    // Filter out already seen messages
    const newMessages = data.newMessages.filter(
      (msg) => !seenMessageIdsRef.current.has(msg.id)
    );

    if (newMessages.length === 0) return;

    // Refetch inbox queries to update UI
    queryClient.refetchQueries({
      queryKey: inboxCreatorKeys.creators(teamId),
    });

    // Show toast for each new message (limit to 3 to prevent spam)
    const toastMessages = newMessages.slice(0, 3);
    for (const msg of toastMessages) {
      seenMessageIdsRef.current.add(msg.id);

      // Linear/Front style toast - minimal and clean
      toast(msg.creatorName, {
        description: msg.preview || msg.subject || "New message",
        action: msg.creatorId
          ? {
              label: "View",
              onClick: () => {
                router.push(`/teams/${teamId}/inbox?creator=${msg.creatorId}`);
              },
            }
          : undefined,
        duration: 5000,
      });
    }

    // If we have new messages beyond the toast limit, show a summary
    if (newMessages.length > 3) {
      const remaining = newMessages.length - 3;
      toast.info(`+${remaining} more new message${remaining > 1 ? "s" : ""}`);
    }
  }, [teamId, queryClient, router]);

  // Start polling
  useEffect(() => {
    if (!enabled || !teamId) return;

    checkForUpdates(); // Initial check

    const intervalId = setInterval(checkForUpdates, interval);
    return () => clearInterval(intervalId);
  }, [enabled, teamId, interval, checkForUpdates]);

  // Memory cleanup - keeps only last 100 message IDs
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      if (seenMessageIdsRef.current.size > 100) {
        const idsArray = Array.from(seenMessageIdsRef.current);
        seenMessageIdsRef.current = new Set(idsArray.slice(-100));
      }
    }, 60000);
    return () => clearInterval(cleanupInterval);
  }, []);
}

// Query keys for inbox creators (minimal definition for this hook)
export const inboxCreatorKeys = {
  creators: (teamId: string) => ["inbox", "creators", teamId] as const,
};
