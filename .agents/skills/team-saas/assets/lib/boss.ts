import { PgBoss } from "pg-boss";

/**
 * pg-boss job queue configuration
 * 
 * pg-boss is a PostgreSQL-backed job queue that's perfect for SaaS because:
 * - Uses the same database (no extra infrastructure)
 * - Supports scheduled/recurring jobs
 * - Built-in retry with backoff
 * - Job deduplication
 * 
 * Usage:
 *   // Create job
 *   const boss = getBoss();
 *   await boss.send(QUEUES.SEND_EMAIL, { to, subject, body }, DEFAULT_JOB_OPTIONS);
 *   
 *   // Worker handles job
 *   boss.work(QUEUES.SEND_EMAIL, async (job) => {
 *     await handleSendEmail(job.data);
 *   });
 */

let boss: PgBoss | null = null;

export function getBoss(): PgBoss {
  if (!boss) {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL is not configured");
    }
    
    boss = new PgBoss({
      connectionString,
      // Use pgboss schema
      schema: "pgboss",
      // Auto-create schema if it doesn't exist
      createSchema: true,
      // Run database migrations on start
      migrate: true,
    });
  }
  return boss;
}

// Default job options with retry settings
export const DEFAULT_JOB_OPTIONS = {
  retryLimit: 3,
  retryDelay: 30, // seconds
  retryBackoff: true, // exponential backoff
  // Keep completed jobs for 7 days (for debugging)
  retentionSeconds: 60 * 60 * 24 * 7,
};

// Queue names - add your queues here
export const QUEUES = {
  // Email
  SEND_EMAIL: "send-email",
  BULK_SEND_EMAIL: "bulk-send-email",
  
  // Scheduled tasks
  DAILY_CLEANUP: "daily-cleanup",
  WEEKLY_REPORT: "weekly-report",
  
  // Add more queues as needed
} as const;

export type QueueName = typeof QUEUES[keyof typeof QUEUES];
