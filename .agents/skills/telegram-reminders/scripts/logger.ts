/**
 * Centralized logging utilities for CLI scripts
 */

import pino from "pino";

const transport = pino.transport({
  target: "pino-pretty",
  options: {
    colorize: true,
    ignore: "pid,hostname,level,time",
    messageFormat: "{msg}",
  },
});

export const logger = pino(
  {
    level: process.env.LOG_LEVEL || "info",
    base: null,
    timestamp: false,
  },
  transport
);

/**
 * Log an error message with [!] prefix
 */
export function logError(message: string): void {
  logger.error(`[!] ${message}`);
}

/**
 * Log a success message with [+] prefix
 */
export function logSuccess(message: string): void {
  logger.info(`[+] ${message}`);
}

/**
 * Log an info message with custom emoji prefix
 */
export function logInfo(emoji: string, message: string): void {
  logger.info(`${emoji} ${message}`);
}

/**
 * Log a message without prefix
 */
export function log(message: string): void {
  logger.info(message);
}

/**
 * Log a separator line
 */
export function logSeparator(length: number = 60): void {
  logger.info("-".repeat(length));
}

/**
 * Log an indented detail line
 */
export function logDetail(message: string, indent: string = "   "): void {
  logger.info(`${indent}${message}`);
}

/**
 * Log usage help for a script
 */
export function logUsage(usage: string, examples?: string[]): void {
  logger.error(usage);
  if (examples && examples.length > 0) {
    logger.error("");
    logger.error("Examples:");
    examples.forEach((example) => logger.error(`  ${example}`));
  }
}

/**
 * Log a section header with optional emoji
 */
export function logSection(emoji: string, title: string): void {
  logger.info(`\n${emoji} ${title}`);
  logSeparator();
}

/**
 * Log not configured error and exit
 */
export function logNotConfigured(): never {
  logError("Not configured. Run: npm run setup");
  process.exit(1);
}

/**
 * Log a structured message entry with details
 */
export function logMessageEntry(details: {
  id?: string;
  title: string;
  time?: string;
  recurring?: string;
  message?: string;
  fileName?: string;
  error?: string;
  status?: string;
  index?: number;
}): void {
  const prefix = details.index ? `${details.index}. ` : "";
  const statusEmoji =
    details.status === "sent" ? "[+]" : details.status === "failed" ? "[!]" : "";

  log(`\n${prefix}${statusEmoji ? statusEmoji + " " : ""}${details.title}`);

  if (details.id) logDetail(`ID: ${details.id}`);
  if (details.time) logDetail(`Time: ${details.time}`);
  if (details.recurring) logDetail(`Recurring: ${details.recurring}`);
  if (details.message) logDetail(`Message: ${details.message}`);
  if (details.fileName) logDetail(`File: ${details.fileName}`);
  if (details.error) logDetail(`Error: ${details.error}`);
}
