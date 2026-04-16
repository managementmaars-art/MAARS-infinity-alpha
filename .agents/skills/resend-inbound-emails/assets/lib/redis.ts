import Redis from "ioredis";

/**
 * Redis Client for Pub/Sub
 * 
 * OPTIONAL: Only needed if using SSE for real-time updates instead of polling.
 * 
 * Usage:
 * - Publisher: Singleton client for publishing events
 * - Subscriber: New client per SSE connection (Redis pub/sub requirement)
 * 
 * Environment:
 * - REDIS_URL: Redis connection string (e.g., from Railway Redis)
 */

// Lazy-initialized publisher client (singleton)
let publisherClient: Redis | null = null;

export function getPublisherClient(): Redis {
  if (!publisherClient) {
    if (!process.env.REDIS_URL) {
      throw new Error("REDIS_URL environment variable is not set");
    }
    publisherClient = new Redis(process.env.REDIS_URL);
  }
  return publisherClient;
}

// Create new subscriber client (each SSE connection needs its own)
export function createSubscriberClient(): Redis {
  if (!process.env.REDIS_URL) {
    throw new Error("REDIS_URL environment variable is not set");
  }
  return new Redis(process.env.REDIS_URL);
}

// Channel prefix for inbox events
export const INBOX_CHANNEL_PREFIX = "inbox:events:";

/**
 * Publish an inbox event to Redis for real-time updates.
 * Call this from webhook handler when emails are received/status changes.
 */
export async function publishInboxEvent(
  teamId: string,
  event: { type: string; data: Record<string, unknown> }
): Promise<void> {
  const publisher = getPublisherClient();
  await publisher.publish(
    `${INBOX_CHANNEL_PREFIX}${teamId}`,
    JSON.stringify(event)
  );
}
