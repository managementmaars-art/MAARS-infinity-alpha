/**
 * Background Job Worker
 * 
 * This script runs alongside the Next.js server to process background jobs.
 * It uses pg-boss for PostgreSQL-backed job queues.
 * 
 * Usage:
 *   Development: bun run scripts/worker.ts
 *   Production: Runs automatically via Dockerfile
 */

import { getBoss, QUEUES, DEFAULT_JOB_OPTIONS } from "@/lib/jobs/boss";

// Import your job handlers
// import { handleSendEmail } from "./handlers/send-email";
// import { handleBulkSendEmail } from "./handlers/bulk-send-email";

async function startWorker() {
  console.log("[Worker] Starting pg-boss worker...");
  
  const boss = getBoss();
  await boss.start();
  
  console.log("[Worker] pg-boss started successfully");

  // ===========================================
  // Register job handlers
  // ===========================================

  // Example: Single email handler
  // boss.work(QUEUES.SEND_EMAIL, { batchSize: 2 }, async (job) => {
  //   console.log(`[Worker] Processing ${QUEUES.SEND_EMAIL}:`, job.id);
  //   await handleSendEmail(job.data);
  // });

  // Example: Bulk email handler  
  // boss.work(QUEUES.BULK_SEND_EMAIL, { batchSize: 1 }, async (job) => {
  //   console.log(`[Worker] Processing ${QUEUES.BULK_SEND_EMAIL}:`, job.id);
  //   await handleBulkSendEmail(job.data);
  // });

  // ===========================================
  // Schedule recurring jobs
  // ===========================================

  // Example: Daily cleanup at 6 AM UTC
  // await boss.schedule(QUEUES.DAILY_CLEANUP, "0 6 * * *", {}, {
  //   ...DEFAULT_JOB_OPTIONS,
  //   tz: "UTC",
  // });

  // Example: Weekly report every Sunday at 9 AM UTC
  // await boss.schedule(QUEUES.WEEKLY_REPORT, "0 9 * * 0", {}, {
  //   ...DEFAULT_JOB_OPTIONS,
  //   tz: "UTC",
  // });

  console.log("[Worker] All handlers registered");
  console.log("[Worker] Listening for jobs...");

  // Handle graceful shutdown
  const shutdown = async () => {
    console.log("[Worker] Shutting down...");
    await boss.stop({ graceful: true, timeout: 30000 });
    console.log("[Worker] Stopped");
    process.exit(0);
  };

  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
}

// Start the worker
startWorker().catch((error) => {
  console.error("[Worker] Failed to start:", error);
  process.exit(1);
});
