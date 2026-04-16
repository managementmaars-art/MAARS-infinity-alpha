import { NextRequest } from "next/server";
import { createSubscriberClient, INBOX_CHANNEL_PREFIX } from "@/lib/redis";

/**
 * SSE Endpoint for Real-time Inbox Updates
 * 
 * File: src/app/api/teams/[teamId]/inbox/events/route.ts
 * 
 * OPTIONAL: Alternative to polling for real-time updates. Requires Redis.
 * 
 * Usage:
 * ```typescript
 * const eventSource = new EventSource(`/api/teams/${teamId}/inbox/events`);
 * eventSource.onmessage = (e) => {
 *   const event = JSON.parse(e.data);
 *   // Handle: new_message, inbox_update, message_status
 * };
 * ```
 */

// Event types sent via SSE
type InboxEventType = "new_message" | "inbox_update" | "message_status";

type RouteParams = {
  params: Promise<{ teamId: string }>;
};

export async function GET(req: NextRequest, { params }: RouteParams) {
  const { teamId } = await params;

  // Check if Redis is configured
  if (!process.env.REDIS_URL) {
    return new Response("SSE not available (Redis not configured)", { status: 503 });
  }

  const channel = `${INBOX_CHANNEL_PREFIX}${teamId}`;
  let subscriber: ReturnType<typeof createSubscriberClient> | null = null;
  let isCleanedUp = false;

  // Create a readable stream for SSE
  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      controller.enqueue(formatSSE({ type: "connected", teamId }));

      // Create Redis subscriber
      subscriber = createSubscriberClient();

      // Handle incoming messages
      subscriber.on("message", (_channel: string, message: string) => {
        if (isCleanedUp) return;
        
        const event = JSON.parse(message);
        controller.enqueue(formatSSE(event));
      });

      // Subscribe to team's inbox channel
      await subscriber.subscribe(channel);

      // Send keepalive ping every 30 seconds
      const pingInterval = setInterval(() => {
        if (isCleanedUp) {
          clearInterval(pingInterval);
          return;
        }
        controller.enqueue(formatSSE({ type: "ping" }));
      }, 30000);

      // Handle connection close
      req.signal.addEventListener("abort", async () => {
        isCleanedUp = true;
        clearInterval(pingInterval);
        
        if (subscriber) {
          await subscriber.unsubscribe(channel);
          subscriber.disconnect();
        }
        
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}

function formatSSE(data: object): Uint8Array {
  const encoder = new TextEncoder();
  return encoder.encode(`data: ${JSON.stringify(data)}\n\n`);
}
