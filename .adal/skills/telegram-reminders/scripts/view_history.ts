#!/usr/bin/env tsx

import { ConvexHttpClient } from "convex/browser";
import { readFileSync, existsSync } from "fs";
import { api } from "../convex/_generated/api.js";
import { Config, CONFIG_PATH, MessageHistory, getConvexUrl } from "./types.js";
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

async function viewHistory(): Promise<void> {
  const args = process.argv.slice(2);
  const limit = args[0] ? parseInt(args[0]) : 50;

  // Load config
  if (!existsSync(CONFIG_PATH)) {
    logNotConfigured();
  }

  const config: Config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));

  // Get Convex URL
  const deploymentUrl = getConvexUrl(config.deployKey);
  const client = new ConvexHttpClient(deploymentUrl);

  logInfo("📜", `Fetching last ${limit} messages...\n`);

  try {
    const history = await client.query(api.messages.viewHistory, { limit }) as MessageHistory[];

    if (history.length === 0) {
      log("No message history found.");
      return;
    }

    log("MESSAGE HISTORY:");
    logSeparator();

    history.forEach((msg, index) => {
      const time = new Date(msg.sent_at).toLocaleString();
      const preview = msg.message_text
        ? msg.message_text.substring(0, 50) + (msg.message_text.length > 50 ? "..." : "")
        : undefined;

      logMessageEntry({
        index: index + 1,
        status: msg.status,
        title: msg.title,
        time,
        message: preview,
        error: msg.status === "failed" ? msg.error_message : undefined,
      });
    });

    log("\n" + "─".repeat(60));
    log(`Total: ${history.length} messages`);
  } catch (error: any) {
    logError(`Failed to view history: ${error.message}`);
    process.exit(1);
  }
}

viewHistory().catch((error: Error) => {
  logError(error.message);
  process.exit(1);
});
