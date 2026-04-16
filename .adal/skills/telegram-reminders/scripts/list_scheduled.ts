#!/usr/bin/env tsx

import { ConvexHttpClient } from "convex/browser";
import { readFileSync, existsSync } from "fs";
import { api } from "../convex/_generated/api.js";
import { Config, CONFIG_PATH, ScheduledMessage, getConvexUrl } from "./types.js";
import { setupProxy } from "./proxy-util.js";
import {
  logError,
  logInfo,
  log,
  logSeparator,
  logNotConfigured,
  logMessageEntry,
} from "./logger.js";

setupProxy();

async function listScheduled(): Promise<void> {
  // Load config
  if (!existsSync(CONFIG_PATH)) {
    logNotConfigured();
  }

  const config: Config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));

  // Get Convex URL
  const deploymentUrl = getConvexUrl(config.deployKey);
  const client = new ConvexHttpClient(deploymentUrl);

  logInfo("📋", "Fetching scheduled messages...\n");

  try {
    const messages = await client.query(api.messages.listScheduled, {}) as ScheduledMessage[];

    if (messages.length === 0) {
      log("No scheduled messages found.");
      return;
    }

    // Group by status
    const pending = messages.filter((m) => m.status === "pending");
    const sent = messages.filter((m) => m.status === "sent");
    const failed = messages.filter((m) => m.status === "failed");

    if (pending.length > 0) {
      log("⏰ PENDING MESSAGES:");
      logSeparator();
      pending.forEach((msg) => {
        const time = new Date(msg.scheduled_time).toLocaleString();
        const preview = msg.message_text
          ? msg.message_text.substring(0, 50) + "..."
          : undefined;

        logMessageEntry({
          id: msg._id,
          title: msg.title,
          time,
          recurring: msg.recurring,
          message: preview,
          fileName: msg.file_name,
        });
      });
      log("\n" + "─".repeat(60));
    }

    if (sent.length > 0) {
      log(`\n✅ SENT MESSAGES (${sent.length}):`);
      logSeparator();
      sent.slice(0, 5).forEach((msg) => {
        const time = new Date(msg.last_sent_at || msg.scheduled_time).toLocaleString();
        log(`\n${msg.title} - ${time}`);
      });
      if (sent.length > 5) {
        log(`\n... and ${sent.length - 5} more`);
      }
      log("\n" + "─".repeat(60));
    }

    if (failed.length > 0) {
      log(`\n❌ FAILED MESSAGES (${failed.length}):`);
      logSeparator();
      failed.forEach((msg) => {
        logMessageEntry({
          id: msg._id,
          title: msg.title,
          error: msg.error_message,
        });
      });
      log("\n" + "─".repeat(60));
    }

    log(`\nTotal: ${messages.length} messages`);
  } catch (error: any) {
    logError(`Failed to list messages: ${error.message}`);
    process.exit(1);
  }
}

listScheduled().catch((error: Error) => {
  logError(error.message);
  process.exit(1);
});
