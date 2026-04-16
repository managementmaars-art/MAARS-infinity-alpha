#!/usr/bin/env tsx

import { ConvexHttpClient } from "convex/browser";
import { readFileSync, existsSync } from "fs";
import { api } from "../convex/_generated/api.js";
import { Id } from "../convex/_generated/dataModel.js";
import { Config, CONFIG_PATH, getConvexUrl } from "./types.js";
import { logError, logSuccess, logInfo, logUsage, logNotConfigured } from "./logger.js";
import { setupProxy } from "./proxy-util.js";

setupProxy();

async function cancelMessage(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    logUsage("Usage: tsx cancel_message.ts <message_id>", [
      "Get message IDs with: npm run list",
    ]);
    process.exit(1);
  }

  const messageId = args[0] as Id<"scheduled_messages">;

  // Load config
  if (!existsSync(CONFIG_PATH)) {
    logNotConfigured();
  }

  const config: Config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));

  // Get Convex URL
  const deploymentUrl = getConvexUrl(config.deployKey);
  const client = new ConvexHttpClient(deploymentUrl);

  logInfo("🗑️", `Cancelling message ${messageId}...`);

  try {
    await client.mutation(api.messages.cancelMessage, {
      messageId,
    });

    logSuccess("Message cancelled successfully!");
  } catch (error: any) {
    logError(`Failed to cancel: ${error.message}`);
    process.exit(1);
  }
}

cancelMessage().catch((error: Error) => {
  logError(error.message);
  process.exit(1);
});
