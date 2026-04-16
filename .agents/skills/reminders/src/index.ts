/**
 * Reminders Skill
 * Local reminder system with scheduling and notifications
 * No external APIs required - all data stored locally in SQLite
 */

import * as sqlite3 from 'sqlite3';
import path from 'path';
import os from 'os';
import fs from 'fs';

/**
 * Reminder type - one-time or recurring
 */
export type ReminderType = 'once' | 'daily' | 'weekly' | 'monthly';

/**
 * Reminder record from database
 */
export interface Reminder {
  id: number;
  message: string;
  scheduledAt: string;
  reminderType: ReminderType;
  createdAt: string;
  completedAt: string | null;
  snoozeUntil: string | null;
}

/**
 * Completed reminder record (history)
 */
export interface ReminderHistory {
  id: number;
  message: string;
  scheduledAt: string;
  completedAt: string;
}

/**
 * Options for creating a one-time reminder
 */
export interface CreateReminderOptions {
  message: string;
  scheduledAt: Date | string;
}

/**
 * Options for creating a recurring reminder
 */
export interface CreateRecurringReminderOptions {
  message: string;
  type: Exclude<ReminderType, 'once'>;
  /** Starting date for the first occurrence (defaults to now) */
  startAt?: Date | string;
}

/**
 * Options for listing reminders
 */
export interface ListRemindersOptions {
  includeCompleted?: boolean;
  limit?: number;
  offset?: number;
}

/**
 * Options for finding due reminders
 */
export interface DueRemindersOptions {
  before?: Date | string;
}

/**
 * Health check result
 */
export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  pendingReminders: number;
  completedReminders: number;
  database: string;
  error?: string;
}

// Promisify database operations
function run(db: sqlite3.Database, sql: string, params: any[] = []): Promise<void> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
      if (err) reject(err);
      else resolve();
    });
  });
}

// Run with result (for INSERT to get lastID)
function runWithResult(db: sqlite3.Database, sql: string, params: any[] = []): Promise<{ lastID: number; changes: number }> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(this: sqlite3.RunResult, err: Error | null) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function get<T>(db: sqlite3.Database, sql: string, params: any[] = []): Promise<T | undefined> {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row as T);
    });
  });
}

function all<T>(db: sqlite3.Database, sql: string, params: any[] = []): Promise<T[]> {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows as T[]);
    });
  });
}

/**
 * Reminders Skill - Local reminder management with SQLite
 */
export class RemindersSkill {
  private dbPath: string;
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;

  constructor(dbPath?: string) {
    this.dbPath = dbPath || path.join(os.homedir(), '.openclaw', 'skills', 'reminders', 'reminders.db');
    this.initPromise = this.initDatabase();
  }

  /**
   * Initialize the database
   */
  private async initDatabase(): Promise<void> {
    const dir = path.dirname(this.dbPath);
    
    // Ensure directory exists
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
    }

    // Open database
    this.db = await new Promise<sqlite3.Database>((resolve, reject) => {
      const db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) reject(err);
        else resolve(db);
      });
    });

    // Create tables
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        scheduled_at TEXT NOT NULL,
        reminder_type TEXT NOT NULL DEFAULT 'once',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        snooze_until TEXT
      )
    `);

    await run(this.db, `
      CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_at)
    `);

    await run(this.db, `
      CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(completed_at)
    `);

    await run(this.db, `
      CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        message TEXT,
        scheduled_at TEXT,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  /**
   * Ensure database is initialized
   */
  private async ensureInitialized(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  /**
   * Parse natural language datetime
   * Supports formats like:
   * - "2026-02-15 14:00"
   * - "tomorrow"
   * - "in 2 hours"
   * - "in 30 minutes"
   * - "in 3 days"
   */
  parseNaturalDateTime(input: string): Date {
    const now = new Date();
    const inputLower = input.toLowerCase().trim();

    // Handle special keywords
    if (inputLower === 'now') {
      return now;
    }

    if (inputLower === 'today') {
      return now;
    }

    if (inputLower === 'tomorrow') {
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      return tomorrow;
    }

    // Handle "in X unit" format
    const inMatch = inputLower.match(/^in\s+(\d+)\s+(hour|hours|minute|minutes|min|mins|day|days|week|weeks)$/);
    if (inMatch) {
      const num = parseInt(inMatch[1], 10);
      const unit = inMatch[2];
      const result = new Date(now);

      if (unit.startsWith('hour')) {
        result.setHours(result.getHours() + num);
      } else if (unit.startsWith('min')) {
        result.setMinutes(result.getMinutes() + num);
      } else if (unit.startsWith('day')) {
        result.setDate(result.getDate() + num);
      } else if (unit.startsWith('week')) {
        result.setDate(result.getDate() + num * 7);
      }
      return result;
    }

    // Handle "in an hour" / "in a minute" / "in a day"
    const inAMatch = inputLower.match(/^in\s+(a|an)\s+(hour|minute|min|day|week)$/);
    if (inAMatch) {
      const unit = inAMatch[2];
      const result = new Date(now);

      if (unit.startsWith('hour')) {
        result.setHours(result.getHours() + 1);
      } else if (unit.startsWith('min')) {
        result.setMinutes(result.getMinutes() + 1);
      } else if (unit.startsWith('day')) {
        result.setDate(result.getDate() + 1);
      } else if (unit.startsWith('week')) {
        result.setDate(result.getDate() + 7);
      }
      return result;
    }

    // Try parsing as ISO date
    const isoDate = new Date(input);
    if (!isNaN(isoDate.getTime())) {
      return isoDate;
    }

    // Try parsing "YYYY-MM-DD HH:MM"
    const dateTimeMatch = input.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})$/);
    if (dateTimeMatch) {
      const [_, year, month, day, hour, minute] = dateTimeMatch;
      const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hour), parseInt(minute));
      if (!isNaN(date.getTime())) {
        return date;
      }
    }

    // Try parsing "HH:MM" (today at specific time, or tomorrow if passed)
    const timeMatch = input.match(/^(\d{2}):(\d{2})$/);
    if (timeMatch) {
      const [_, hour, minute] = timeMatch;
      const date = new Date(now);
      date.setHours(parseInt(hour), parseInt(minute), 0, 0);
      
      // If time has already passed today, use tomorrow
      if (date < now) {
        date.setDate(date.getDate() + 1);
      }
      return date;
    }

    throw new Error(`Unable to parse datetime: "${input}". Try formats like "2026-02-15 14:00", "tomorrow", "in 2 hours", or "in 30 minutes"`);
  }

  /**
   * Create a one-time reminder
   */
  async addReminder(options: CreateReminderOptions): Promise<Reminder> {
    await this.ensureInitialized();

    const scheduledAt = options.scheduledAt instanceof Date 
      ? options.scheduledAt.toISOString() 
      : options.scheduledAt;

    const result = await runWithResult(this.db!,
      `INSERT INTO reminders (message, scheduled_at, reminder_type) VALUES (?, ?, ?)`,
      [options.message, scheduledAt, 'once']
    );

    return {
      id: result.lastID,
      message: options.message,
      scheduledAt,
      reminderType: 'once',
      createdAt: new Date().toISOString(),
      completedAt: null,
      snoozeUntil: null,
    };
  }

  /**
   * Create a recurring reminder
   */
  async addRecurringReminder(options: CreateRecurringReminderOptions): Promise<Reminder> {
    await this.ensureInitialized();

    const startAt = options.startAt 
      ? (options.startAt instanceof Date ? options.startAt : new Date(options.startAt))
      : new Date();

    const scheduledAt = startAt.toISOString();

    const result = await runWithResult(this.db!,
      `INSERT INTO reminders (message, scheduled_at, reminder_type) VALUES (?, ?, ?)`,
      [options.message, scheduledAt, options.type]
    );

    return {
      id: result.lastID,
      message: options.message,
      scheduledAt,
      reminderType: options.type,
      createdAt: new Date().toISOString(),
      completedAt: null,
      snoozeUntil: null,
    };
  }

  /**
   * List all reminders
   */
  async listReminders(options: ListRemindersOptions = {}): Promise<Reminder[]> {
    await this.ensureInitialized();

    let sql = `
      SELECT 
        id,
        message,
        scheduled_at as scheduledAt,
        reminder_type as reminderType,
        created_at as createdAt,
        completed_at as completedAt,
        snooze_until as snoozeUntil
      FROM reminders
      WHERE 1=1
    `;

    const params: any[] = [];

    if (!options.includeCompleted) {
      sql += ` AND completed_at IS NULL`;
    }

    sql += ` ORDER BY scheduled_at ASC`;

    if (options.limit) {
      sql += ` LIMIT ?`;
      params.push(options.limit);
    }

    if (options.offset) {
      sql += ` OFFSET ?`;
      params.push(options.offset);
    }

    const rows = await all<{
      id: number;
      message: string;
      scheduledAt: string;
      reminderType: ReminderType;
      createdAt: string;
      completedAt: string | null;
      snoozeUntil: string | null;
    }>(this.db!, sql, params);

    return rows;
  }

  /**
   * Get reminders that are due (scheduled time <= now and not snoozed)
   */
  async getDueReminders(options: DueRemindersOptions = {}): Promise<Reminder[]> {
    await this.ensureInitialized();

    const before = options.before ? new Date(options.before) : new Date();
    const beforeStr = before.toISOString();

    const rows = await all<{
      id: number;
      message: string;
      scheduledAt: string;
      reminderType: ReminderType;
      createdAt: string;
      completedAt: string | null;
      snoozeUntil: string | null;
    }>(this.db!, `
      SELECT 
        id,
        message,
        scheduled_at as scheduledAt,
        reminder_type as reminderType,
        created_at as createdAt,
        completed_at as completedAt,
        snooze_until as snoozeUntil
      FROM reminders
      WHERE completed_at IS NULL
        AND scheduled_at <= ?
        AND (snooze_until IS NULL OR snooze_until <= ?)
      ORDER BY scheduled_at ASC
    `, [beforeStr, beforeStr]);

    return rows;
  }

  /**
   * Get a single reminder by ID
   */
  async getReminder(id: number): Promise<Reminder | undefined> {
    await this.ensureInitialized();

    const row = await get<{
      id: number;
      message: string;
      scheduledAt: string;
      reminderType: ReminderType;
      createdAt: string;
      completedAt: string | null;
      snoozeUntil: string | null;
    }>(this.db!, `
      SELECT 
        id,
        message,
        scheduled_at as scheduledAt,
        reminder_type as reminderType,
        created_at as createdAt,
        completed_at as completedAt,
        snooze_until as snoozeUntil
      FROM reminders
      WHERE id = ?
    `, [id]);

    return row;
  }

  /**
   * Mark a reminder as complete
   * For recurring reminders, schedules the next occurrence
   */
  async completeReminder(id: number): Promise<{ 
    success: boolean; 
    nextOccurrence?: Date;
    movedToHistory?: boolean;
  }> {
    await this.ensureInitialized();

    const reminder = await this.getReminder(id);
    if (!reminder) {
      throw new Error(`Reminder ${id} not found`);
    }

    if (reminder.reminderType === 'once') {
      // Move to history
      await run(this.db!, `
        INSERT INTO history (id, message, scheduled_at, completed_at)
        VALUES (?, ?, ?, ?)
      `, [reminder.id, reminder.message, reminder.scheduledAt, new Date().toISOString()]);

      // Delete from reminders
      await run(this.db!, `DELETE FROM reminders WHERE id = ?`, [id]);

      return { success: true, movedToHistory: true };
    } else {
      // Recurring - calculate next occurrence
      const currentScheduled = new Date(reminder.scheduledAt);
      let nextScheduled: Date;

      switch (reminder.reminderType) {
        case 'daily':
          nextScheduled = new Date(currentScheduled);
          nextScheduled.setDate(nextScheduled.getDate() + 1);
          break;
        case 'weekly':
          nextScheduled = new Date(currentScheduled);
          nextScheduled.setDate(nextScheduled.getDate() + 7);
          break;
        case 'monthly':
          nextScheduled = new Date(currentScheduled);
          nextScheduled.setMonth(nextScheduled.getMonth() + 1);
          break;
        default:
          throw new Error(`Unknown reminder type: ${reminder.reminderType}`);
      }

      // Update with next occurrence
      await run(this.db!, `
        UPDATE reminders 
        SET scheduled_at = ?, snooze_until = NULL 
        WHERE id = ?
      `, [nextScheduled.toISOString(), id]);

      return { success: true, nextOccurrence: nextScheduled };
    }
  }

  /**
   * Snooze a reminder for a specified number of minutes
   */
  async snoozeReminder(id: number, minutes: number): Promise<Reminder> {
    await this.ensureInitialized();

    const snoozeUntil = new Date();
    snoozeUntil.setMinutes(snoozeUntil.getMinutes() + minutes);
    const snoozeUntilStr = snoozeUntil.toISOString();

    await run(this.db!, `
      UPDATE reminders 
      SET snooze_until = ? 
      WHERE id = ? AND completed_at IS NULL
    `, [snoozeUntilStr, id]);

    const reminder = await this.getReminder(id);
    if (!reminder) {
      throw new Error(`Reminder ${id} not found or already completed`);
    }

    return reminder;
  }

  /**
   * Delete a reminder
   */
  async deleteReminder(id: number): Promise<boolean> {
    await this.ensureInitialized();

    const result = await runWithResult(this.db!, `DELETE FROM reminders WHERE id = ?`, [id]);
    return result.changes > 0;
  }

  /**
   * Get reminder history (completed reminders)
   */
  async getHistory(limit: number = 50): Promise<ReminderHistory[]> {
    await this.ensureInitialized();

    const rows = await all<{
      id: number;
      message: string;
      scheduledAt: string;
      completedAt: string;
    }>(this.db!, `
      SELECT 
        id,
        message,
        scheduled_at as scheduledAt,
        completed_at as completedAt
      FROM history
      ORDER BY completed_at DESC
      LIMIT ?
    `, [limit]);

    return rows;
  }

  /**
   * Get statistics about reminders
   */
  async getStats(): Promise<{
    pending: number;
    completed: number;
    overdue: number;
  }> {
    await this.ensureInitialized();

    const now = new Date().toISOString();

    const pendingResult = await get<{ count: number }>(this.db!, `
      SELECT COUNT(*) as count FROM reminders WHERE completed_at IS NULL
    `);

    const completedResult = await get<{ count: number }>(this.db!, `
      SELECT COUNT(*) as count FROM history
    `);

    const overdueResult = await get<{ count: number }>(this.db!, `
      SELECT COUNT(*) as count FROM reminders 
      WHERE completed_at IS NULL AND scheduled_at < ?
    `, [now]);

    return {
      pending: pendingResult?.count || 0,
      completed: completedResult?.count || 0,
      overdue: overdueResult?.count || 0,
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthCheckResult> {
    try {
      await this.ensureInitialized();

      const stats = await this.getStats();

      return {
        status: 'healthy',
        pendingReminders: stats.pending,
        completedReminders: stats.completed,
        database: this.dbPath,
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        pendingReminders: 0,
        completedReminders: 0,
        database: this.dbPath,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Run daemon check - returns due reminders for notification
   */
  async daemonCheck(): Promise<{
    notifications: Reminder[];
    count: number;
    timestamp: string;
  }> {
    const due = await this.getDueReminders();
    return {
      notifications: due,
      count: due.length,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Close database connection
   */
  async close(): Promise<void> {
    if (this.initPromise) {
      try {
        await this.initPromise;
      } catch (e) {
        // Ignore init errors
      }
    }
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

// Default export
export default RemindersSkill;
