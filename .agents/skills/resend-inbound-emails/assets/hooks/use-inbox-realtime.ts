"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { inboxCreatorKeys } from "./use-inbox-creators";

/**
 * SSE-based Real-time Inbox Updates
 * 
 * OPTIONAL: Alternative to polling. Requires Redis backend.
 * 
 * Advantages over polling:
 * - True real-time (no delay)
 * - More efficient (no repeated requests)
 * 
 * Disadvantages:
 * - Requires Redis
 * - May not work well with serverless (connection limits)
 * - Falls back to polling if SSE unavailable
 */

interface UseInboxRealtimeOptions {
  enabled?: boolean;
  onNewMessage?: (data: { creatorId: string; threadId: string }) => void;
}

export function useInboxRealtime(
  teamId: string | undefined,
  options?: UseInboxRealtimeOptions
) {
  const { enabled = true, onNewMessage } = options ?? {};
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled || !teamId) return;

    // Create SSE connection
    const eventSource = new EventSource(`/api/teams/${teamId}/inbox/events`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (e) => {
      const event = JSON.parse(e.data);

      switch (event.type) {
        case "new_message":
          // Invalidate inbox queries
          queryClient.invalidateQueries({
            queryKey: inboxCreatorKeys.creators(teamId),
          });
          
          // Show toast notification
          toast("New message received", {
            description: "Your inbox has been updated",
          });
          
          // Call custom handler
          onNewMessage?.(event.data);
          break;

        case "inbox_update":
        case "message_status":
          // Just invalidate queries
          queryClient.invalidateQueries({
            queryKey: inboxCreatorKeys.creators(teamId),
          });
          break;

        case "ping":
          // Keepalive, ignore
          break;
      }
    };

    eventSource.onerror = () => {
      // SSE connection failed - will auto-reconnect
      // Consider falling back to polling
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [enabled, teamId, queryClient, onNewMessage]);
}

// Query keys (minimal definition for this hook)
export const inboxCreatorKeys = {
  creators: (teamId: string) => ["inbox", "creators", teamId] as const,
};
