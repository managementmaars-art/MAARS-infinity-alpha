import { Id } from "../convex/_generated/dataModel.js";

/**
 * Configuration stored in /mnt/user-data/outputs/telegram_config.json
 */
export interface Config {
  botToken: string;
  userId: string;
  deployKey: string;
  setupDate: string;
}

/**
 * Scheduled message record from database
 */
export interface ScheduledMessage {
  _id: Id<"scheduled_messages">;
  title: string;
  message_text?: string;
  storage_id?: Id<"_storage">;
  file_name?: string;
  scheduled_time: number;
  recurring?: string;
  status: string;
  created_at: number;
  last_sent_at?: number;
  error_message?: string;
}

/**
 * Message history record from database
 */
export interface MessageHistory {
  _id: Id<"message_history">;
  title: string;
  message_text?: string;
  sent_at: number;
  status: string;
  error_message?: string;
  scheduled_message_id?: Id<"scheduled_messages">;
}

/**
 * Telegram bot info from getMe API
 */
export interface BotInfo {
  username: string;
}

/**
 * Parsed time result from natural language processing
 */
export interface ParsedTime {
  scheduledTime: number;
  recurring?: string;
}

/**
 * Configuration file path
 */
export const CONFIG_PATH = "/mnt/user-data/outputs/telegram_config.json";

/**
 * Extract Convex deployment URL from deploy key
 * @param deployKey - Convex deploy key in format "prod:deployment-name|key"
 * @returns Convex deployment URL
 */
export function getConvexUrl(deployKey: string): string {
  const parts = deployKey.split("|")[0].split(":");
  if (parts.length < 2) {
    throw new Error("Invalid deploy key format");
  }
  const deploymentName = parts[1];
  return `https://${deploymentName}.convex.cloud`;
}
