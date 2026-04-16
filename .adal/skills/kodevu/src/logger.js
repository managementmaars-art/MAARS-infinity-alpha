import fs from "node:fs";
import path from "node:path";
import { formatDate } from "./utils.js";

// Top-level helpers moved into Logger as private methods (#name).

class Logger {
  constructor () {
    this.config = null;
    this.logFile = null;
    this.sessionId = null;
    this.initialized = false;
  }

  #formatValue(value) {
    if (value == null) return "";

    if (typeof value === "string") return value.trim();

    if (typeof value === "number" || typeof value === "boolean") return String(value);

    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  #formatMeta(meta = {}) {
    const parts = [];

    for (const [key, rawValue] of Object.entries(meta || {})) {
      if (rawValue == null || rawValue === "") continue;

      const value = this.#formatValue(rawValue);
      if (!value) continue;

      if (typeof rawValue === "string") {
        parts.push(`${key}=${JSON.stringify(value)}`);
        continue;
      }

      if (typeof rawValue === "number" || typeof rawValue === "boolean") {
        parts.push(`${key}=${rawValue}`);
        continue;
      }

      parts.push(`${key}=${value}`);
    }

    return parts.join(" ");
  }

  #formatErrorDetails(error) {
    if (!error) return "";

    if (error instanceof Error) return error.stack ?? error.message ?? String(error);

    if (typeof error === "string") return error;

    try {
      return JSON.stringify(error, null, 2);
    } catch {
      return String(error);
    }
  }

  init(config) {
    if (this.initialized) return;
    this.config = config;
    this.sessionId = this.#createSessionId();
    
    if (config.logsDir) {
      try {
        if (!fs.existsSync(config.logsDir)) {
          fs.mkdirSync(config.logsDir, { recursive: true });
        }
        const date = formatDate(new Date()).split(" ")[0];
        this.logFile = path.join(config.logsDir, `run-${date}.log`);
        
        // Simple rotation: Keep the most recent 7 log files
        this.#cleanupOldLogs(config.logsDir);
        this.initialized = true;
      } catch (err) {
        console.error(`[logger] Failed to initialize log file: ${err.message}`);
      }
    }
  }

  info(message, meta) {
    this.#log("INFO", message, meta);
  }

  warn(message, meta) {
    this.#log("WARN", message, { ...meta, console: meta?.console ?? true });
  }

  error(message, error, meta) {
    this.#log("ERROR", message, {
      ...meta,
      console: meta?.console ?? true,
      error: this.#formatErrorDetails(error)
    });
  }

  debug(message, meta) {
    this.#log("DEBUG", message, meta);
  }

  #log(level, message, meta = {}) {
    const timestamp = formatDate(new Date());
    const { console: consoleMode, ...details } = meta;
    const fields = {
      session: this.sessionId || "uninitialized",
      ...details
    };
    const metaSuffix = this.#formatMeta(fields);
    const logLine = `[${timestamp}] [${level}] ${message}${metaSuffix ? ` | ${metaSuffix}` : ""}`;

    if (this.logFile) {
      try {
        fs.appendFileSync(this.logFile, logLine + "\n");
      } catch (err) {
        // Ignore file errors during logging to prevent crashes
      }
    }

    if (!this.#shouldWriteToConsole(level, consoleMode)) {
      return;
    }

    if (level === "ERROR" || level === "WARN") {
      console.error(logLine);
    } else {
      console.log(logLine);
    }
  }

  #shouldWriteToConsole(level, consoleMode) {
    if (consoleMode === false) return false;

    if (level === "ERROR" || level === "WARN") return true;

    if (level === "DEBUG") {
      if (consoleMode === true) return Boolean(this.config?.debug);
      return false;
    }

    if (consoleMode === true) return true;

    if (consoleMode === "debug") return Boolean(this.config?.debug);

    return false;
  }

  #createSessionId() {
    return [
      Date.now().toString(36),
      process.pid.toString(36),
      Math.random().toString(36).slice(2, 8)
    ].join("-");
  }

  #cleanupOldLogs(logsDir) {
    try {
      const files = fs.readdirSync(logsDir);

      const logFiles = files
        .filter((file) => file.startsWith("run-") && file.endsWith(".log"))
        .map((file) => {
          const filePath = path.join(logsDir, file);
          try {
            const stats = fs.statSync(filePath);
            return { file, path: filePath, mtime: stats.mtimeMs };
          } catch {
            return null;
          }
        })
        .filter(Boolean)
        .sort((a, b) => b.mtime - a.mtime);

      const KEEP_COUNT = 7;
      const toRemove = logFiles.slice(KEEP_COUNT);

      for (const entry of toRemove) {
        try {
          fs.unlinkSync(entry.path);
        } catch {
      // Ignore individual deletion errors
        }
      }
    } catch (err) {
      // Ignore cleanup errors
    }
  }
}

export const logger = new Logger();
