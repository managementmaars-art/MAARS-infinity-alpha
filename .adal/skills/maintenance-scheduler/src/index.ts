/**
 * Maintenance Scheduler Skill
 * Schedule recurring home maintenance tasks with seasonal templates
 * Depends on reminders skill for notification scheduling
 */

import * as sqlite3 from 'sqlite3';
import path from 'path';
import os from 'os';
import fs from 'fs';
import { RemindersSkill } from '@openclaw/reminders';

/**
 * Home type for templates
 */
export type HomeType = 'house' | 'apartment' | 'condo';

/**
 * Task category
 */
export type TaskCategory = 'indoor' | 'outdoor' | 'hvac' | 'plumbing' | 'electrical' | 'appliance' | 'safety' | 'cleaning' | 'other';

/**
 * Maintenance task interface
 */
export interface MaintenanceTask {
  id: number;
  name: string;
  description?: string;
  frequencyDays: number;
  advanceNoticeDays: number;
  category: TaskCategory;
  homeType?: HomeType;
  reminderId?: number;
  nextDue: string;
  createdAt: string;
}

/**
 * Task record from database (snake_case)
 */
interface TaskRecord {
  id: number;
  name: string;
  description?: string;
  frequency_days: number;
  advance_notice_days: number;
  category: TaskCategory;
  home_type?: HomeType;
  reminder_id?: number;
  next_due: string;
  created_at: string;
}

/**
 * Completion history entry
 */
export interface CompletionHistory {
  id: number;
  taskId: number;
  taskName: string;
  completedAt: string;
  notes?: string;
}

/**
 * Completion record from database (snake_case)
 */
interface CompletionRecord {
  id: number;
  task_id: number;
  task_name: string;
  completed_at: string;
  notes?: string;
}

/**
 * Upcoming task with calculated dates
 */
export interface UpcomingTask {
  task: MaintenanceTask;
  daysUntil: number;
  isNoticePeriod: boolean;
  noticeInDays: number;
}

/**
 * Template task for applying seasonal templates
 */
export interface TemplateTask {
  name: string;
  description?: string;
  frequencyDays: number;
  advanceNoticeDays: number;
  category: TaskCategory;
}

/**
 * Create task options
 */
export interface CreateTaskOptions {
  name: string;
  description?: string;
  frequencyDays: number;
  advanceNoticeDays?: number;
  category?: TaskCategory;
  homeType?: HomeType;
  startDate?: Date;
}

/**
 * Update task options
 */
export interface UpdateTaskOptions {
  name?: string;
  description?: string;
  frequencyDays?: number;
  advanceNoticeDays?: number;
  category?: TaskCategory;
}

/**
 * Completion stats
 */
export interface CompletionStats {
  totalTasks: number;
  completedThisMonth: number;
  completedThisYear: number;
  overdueTasks: number;
  upcomingTasks: number;
  byCategory: Record<TaskCategory, number>;
}

/**
 * Health check result
 */
export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  tasks: number;
  completions: number;
  upcoming: number;
  overdue: number;
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
 * Seasonal maintenance templates
 */
export const maintenanceTemplates: Record<HomeType, TemplateTask[]> = {
  house: [
    // Monthly
    { name: 'Check HVAC filters', description: 'Inspect and replace if dirty', frequencyDays: 30, advanceNoticeDays: 3, category: 'hvac' },
    { name: 'Test smoke detectors', description: 'Test all smoke and CO detectors', frequencyDays: 30, advanceNoticeDays: 2, category: 'safety' },
    { name: 'Inspect plumbing', description: 'Check under sinks and around toilets for leaks', frequencyDays: 30, advanceNoticeDays: 3, category: 'plumbing' },
    { name: 'Clean garbage disposal', description: 'Clean and deodorize', frequencyDays: 30, advanceNoticeDays: 2, category: 'appliance' },
    // Quarterly
    { name: 'Clean gutters', description: 'Remove leaves and debris', frequencyDays: 90, advanceNoticeDays: 7, category: 'outdoor' },
    { name: 'Inspect roof', description: 'Check for damaged shingles or leaks', frequencyDays: 90, advanceNoticeDays: 7, category: 'outdoor' },
    { name: 'Service garage door', description: 'Lubricate moving parts', frequencyDays: 90, advanceNoticeDays: 5, category: 'other' },
    { name: 'Clean dryer vent', description: 'Remove lint buildup', frequencyDays: 90, advanceNoticeDays: 5, category: 'appliance' },
    // Bi-annual
    { name: 'Deep clean carpets', description: 'Professional or rental cleaning', frequencyDays: 180, advanceNoticeDays: 7, category: 'cleaning' },
    { name: 'Service major appliances', description: 'Check dishwasher, washer, dryer', frequencyDays: 180, advanceNoticeDays: 7, category: 'appliance' },
    { name: 'Inspect exterior paint', description: 'Check for peeling or damage', frequencyDays: 180, advanceNoticeDays: 14, category: 'outdoor' },
    { name: 'Clean windows', description: 'Interior and exterior', frequencyDays: 180, advanceNoticeDays: 7, category: 'cleaning' },
    // Annual
    { name: 'Professional HVAC service', description: 'Annual inspection and tune-up', frequencyDays: 365, advanceNoticeDays: 14, category: 'hvac' },
    { name: 'Chimney inspection', description: 'Professional cleaning if needed', frequencyDays: 365, advanceNoticeDays: 14, category: 'safety' },
    { name: 'Septic system check', description: 'Inspection and pumping if needed', frequencyDays: 365, advanceNoticeDays: 21, category: 'plumbing' },
    { name: 'Water heater flush', description: 'Drain and remove sediment', frequencyDays: 365, advanceNoticeDays: 7, category: 'plumbing' },
  ],
  apartment: [
    // Monthly
    { name: 'Check smoke detectors', description: 'Test all detectors', frequencyDays: 30, advanceNoticeDays: 2, category: 'safety' },
    { name: 'Clean AC filters', description: 'Wash or replace filters', frequencyDays: 30, advanceNoticeDays: 3, category: 'hvac' },
    { name: 'Inspect faucets', description: 'Check for drips and leaks', frequencyDays: 30, advanceNoticeDays: 3, category: 'plumbing' },
    { name: 'Clean drains', description: 'Use drain cleaner or baking soda/vinegar', frequencyDays: 30, advanceNoticeDays: 2, category: 'plumbing' },
    // Quarterly
    { name: 'Deep clean appliances', description: 'Clean fridge, oven, microwave', frequencyDays: 90, advanceNoticeDays: 5, category: 'appliance' },
    { name: 'Check weather stripping', description: 'Inspect door and window seals', frequencyDays: 90, advanceNoticeDays: 5, category: 'other' },
    { name: 'Clean range hood filter', description: 'Degrease filter', frequencyDays: 90, advanceNoticeDays: 3, category: 'appliance' },
    // Annual
    { name: 'Deep clean carpets', description: 'Professional or rental cleaning', frequencyDays: 365, advanceNoticeDays: 7, category: 'cleaning' },
    { name: 'Professional AC service', description: 'Annual inspection', frequencyDays: 365, advanceNoticeDays: 14, category: 'hvac' },
    { name: 'Safety inspection', description: 'Check all safety equipment', frequencyDays: 365, advanceNoticeDays: 7, category: 'safety' },
    { name: 'Paint touch-ups', description: 'Fix scuffs and marks', frequencyDays: 365, advanceNoticeDays: 14, category: 'indoor' },
  ],
  condo: [
    // Monthly
    { name: 'Check detectors and filters', description: 'Smoke, CO, and HVAC filters', frequencyDays: 30, advanceNoticeDays: 3, category: 'safety' },
    { name: 'Inspect for moisture', description: 'Check windows and bathroom for condensation', frequencyDays: 30, advanceNoticeDays: 3, category: 'plumbing' },
    { name: 'Clean appliance filters', description: 'Dishwasher, range hood, dryer', frequencyDays: 30, advanceNoticeDays: 2, category: 'appliance' },
    // Quarterly
    { name: 'Clean balcony/terrace', description: 'Sweep and wash outdoor space', frequencyDays: 90, advanceNoticeDays: 5, category: 'outdoor' },
    { name: 'Service appliances', description: 'Deep clean and inspect all appliances', frequencyDays: 90, advanceNoticeDays: 5, category: 'appliance' },
    { name: 'Check caulking', description: 'Inspect bathroom and kitchen caulking', frequencyDays: 90, advanceNoticeDays: 5, category: 'plumbing' },
    // Annual
    { name: 'Deep cleaning', description: 'Professional or thorough DIY cleaning', frequencyDays: 365, advanceNoticeDays: 7, category: 'cleaning' },
    { name: 'Maintenance inspection', description: 'Review all systems with building management', frequencyDays: 365, advanceNoticeDays: 14, category: 'other' },
    { name: 'Window washing', description: 'Interior and accessible exterior', frequencyDays: 365, advanceNoticeDays: 7, category: 'cleaning' },
    { name: 'Closet organization', description: 'Purge and reorganize storage', frequencyDays: 365, advanceNoticeDays: 7, category: 'indoor' },
  ],
};

/**
 * Maintenance Scheduler Skill - Schedule home maintenance tasks
 */
export class MaintenanceSchedulerSkill {
  private dbPath: string;
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;
  private remindersSkill: RemindersSkill;

  constructor(dbPath?: string) {
    this.dbPath = dbPath || path.join(os.homedir(), '.openclaw', 'skills', 'maintenance-scheduler', 'maintenance.db');
    this.remindersSkill = new RemindersSkill();
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

    // Create tasks table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        frequency_days INTEGER NOT NULL,
        advance_notice_days INTEGER DEFAULT 3,
        category TEXT DEFAULT 'other',
        home_type TEXT,
        reminder_id INTEGER,
        next_due TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create completion_history table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS completion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
      )
    `);

    // Create indexes
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_tasks_next_due ON tasks(next_due)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_history_task ON completion_history(task_id)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_history_completed ON completion_history(completed_at)`);
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
   * Calculate next due date
   */
  private calculateNextDue(frequencyDays: number, fromDate?: Date): Date {
    const base = fromDate ? new Date(fromDate) : new Date();
    const next = new Date(base);
    next.setDate(next.getDate() + frequencyDays);
    return next;
  }

  /**
   * Calculate days until a date
   */
  private daysUntil(target: Date): number {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const targetCopy = new Date(target);
    targetCopy.setHours(0, 0, 0, 0);
    
    const diffMs = targetCopy.getTime() - now.getTime();
    return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  }

  /**
   * Create a reminder for a task
   */
  private async createTaskReminder(task: MaintenanceTask): Promise<number | undefined> {
    const reminderDate = new Date(task.nextDue);
    reminderDate.setDate(reminderDate.getDate() - task.advanceNoticeDays);
    
    // If reminder date is in the past, set it for tomorrow
    if (reminderDate < new Date()) {
      reminderDate.setDate(new Date().getDate() + 1);
    }

    try {
      const reminder = await this.remindersSkill.addReminder({
        message: `Maintenance due: ${task.name}`,
        scheduledAt: reminderDate,
      });
      return reminder.id;
    } catch (e) {
      console.warn('Failed to create reminder:', e instanceof Error ? e.message : String(e));
      return undefined;
    }
  }

  /**
   * Create a new maintenance task
   */
  async createTask(options: CreateTaskOptions): Promise<MaintenanceTask> {
    await this.ensureInitialized();

    const frequencyDays = options.frequencyDays;
    const advanceNoticeDays = options.advanceNoticeDays ?? 3;
    const category = options.category ?? 'other';
    const startDate = options.startDate || new Date();
    const nextDue = this.calculateNextDue(frequencyDays, startDate);

    const result = await runWithResult(this.db!,
      `INSERT INTO tasks (name, description, frequency_days, advance_notice_days, category, home_type, next_due) 
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        options.name,
        options.description || null,
        frequencyDays,
        advanceNoticeDays,
        category,
        options.homeType || null,
        nextDue.toISOString(),
      ]
    );

    const task: MaintenanceTask = {
      id: result.lastID,
      name: options.name,
      description: options.description,
      frequencyDays,
      advanceNoticeDays,
      category,
      homeType: options.homeType,
      nextDue: nextDue.toISOString(),
      createdAt: new Date().toISOString(),
    };

    // Create reminder
    const reminderId = await this.createTaskReminder(task);
    if (reminderId) {
      task.reminderId = reminderId;
      await run(this.db!, `UPDATE tasks SET reminder_id = ? WHERE id = ?`, [reminderId, task.id]);
    }

    return task;
  }

  /**
   * Get a task by ID
   */
  async getTask(id: number): Promise<MaintenanceTask | undefined> {
    await this.ensureInitialized();

    const record = await get<TaskRecord>(this.db!, `
      SELECT id, name, description, frequency_days, advance_notice_days, 
             category, home_type, reminder_id, next_due, created_at
      FROM tasks WHERE id = ?
    `, [id]);

    if (!record) return undefined;

    return this.mapTaskRecord(record);
  }

  /**
   * List all tasks
   */
  async listTasks(category?: TaskCategory): Promise<MaintenanceTask[]> {
    await this.ensureInitialized();

    let sql = `
      SELECT id, name, description, frequency_days, advance_notice_days,
             category, home_type, reminder_id, next_due, created_at
      FROM tasks
    `;
    const params: any[] = [];

    if (category) {
      sql += ` WHERE category = ?`;
      params.push(category);
    }

    sql += ` ORDER BY next_due ASC`;

    const records = await all<TaskRecord>(this.db!, sql, params);

    return records.map(record => this.mapTaskRecord(record));
  }

  /**
   * Update a task
   */
  async updateTask(id: number, updates: UpdateTaskOptions): Promise<MaintenanceTask | undefined> {
    await this.ensureInitialized();

    const task = await this.getTask(id);
    if (!task) return undefined;

    const sets: string[] = [];
    const params: any[] = [];

    if (updates.name !== undefined) { sets.push('name = ?'); params.push(updates.name); }
    if (updates.description !== undefined) { sets.push('description = ?'); params.push(updates.description); }
    if (updates.frequencyDays !== undefined) { sets.push('frequency_days = ?'); params.push(updates.frequencyDays); }
    if (updates.advanceNoticeDays !== undefined) { sets.push('advance_notice_days = ?'); params.push(updates.advanceNoticeDays); }
    if (updates.category !== undefined) { sets.push('category = ?'); params.push(updates.category); }

    if (sets.length === 0) {
      return task;
    }

    params.push(id);
    await run(this.db!, `UPDATE tasks SET ${sets.join(', ')} WHERE id = ?`, params);

    // Update reminder if notice period changed
    if (updates.advanceNoticeDays !== undefined && task.reminderId) {
      await this.remindersSkill.deleteReminder(task.reminderId);
      const updated = await this.getTask(id);
      if (updated) {
        const newReminderId = await this.createTaskReminder(updated);
        if (newReminderId) {
          await run(this.db!, `UPDATE tasks SET reminder_id = ? WHERE id = ?`, [newReminderId, id]);
        }
      }
    }

    return this.getTask(id);
  }

  /**
   * Delete a task
   */
  async deleteTask(id: number): Promise<boolean> {
    await this.ensureInitialized();

    const task = await this.getTask(id);
    if (task?.reminderId) {
      await this.remindersSkill.deleteReminder(task.reminderId);
    }

    const result = await runWithResult(this.db!, `DELETE FROM tasks WHERE id = ?`, [id]);
    return result.changes > 0;
  }

  /**
   * Complete a task and schedule next occurrence
   */
  async completeTask(id: number, notes?: string): Promise<{
    success: boolean;
    nextDue?: Date;
    historyId?: number;
  }> {
    await this.ensureInitialized();

    const task = await this.getTask(id);
    if (!task) {
      throw new Error(`Task ${id} not found`);
    }

    // Record completion
    const historyResult = await runWithResult(this.db!,
      `INSERT INTO completion_history (task_id, task_name, notes) VALUES (?, ?, ?)`,
      [id, task.name, notes || null]
    );

    // Calculate next due date
    const nextDue = this.calculateNextDue(task.frequencyDays);

    // Delete old reminder
    if (task.reminderId) {
      await this.remindersSkill.deleteReminder(task.reminderId);
    }

    // Create new reminder for next occurrence
    const updatedTask: MaintenanceTask = {
      ...task,
      nextDue: nextDue.toISOString(),
    };
    const newReminderId = await this.createTaskReminder(updatedTask);

    // Update task with next due date
    await run(this.db!, 
      `UPDATE tasks SET next_due = ?, reminder_id = ? WHERE id = ?`,
      [nextDue.toISOString(), newReminderId || null, id]
    );

    return {
      success: true,
      nextDue,
      historyId: historyResult.lastID,
    };
  }

  /**
   * Get upcoming tasks
   */
  async getUpcomingTasks(daysAhead: number = 365): Promise<UpcomingTask[]> {
    await this.ensureInitialized();

    const records = await all<TaskRecord>(this.db!, `
      SELECT id, name, description, frequency_days, advance_notice_days,
             category, home_type, reminder_id, next_due, created_at
      FROM tasks
      ORDER BY next_due ASC
    `);

    const upcoming: UpcomingTask[] = [];

    for (const record of records) {
      const nextDue = new Date(record.next_due);
      const daysUntil = this.daysUntil(nextDue);

      if (daysUntil <= daysAhead) {
        const noticeInDays = daysUntil - record.advance_notice_days;
        const isNoticePeriod = daysUntil <= record.advance_notice_days;

        upcoming.push({
          task: this.mapTaskRecord(record),
          daysUntil,
          isNoticePeriod,
          noticeInDays: Math.max(0, noticeInDays),
        });
      }
    }

    // Sort by days until (closest first)
    return upcoming.sort((a, b) => a.daysUntil - b.daysUntil);
  }

  /**
   * Get due tasks (including notice period)
   */
  async getDueTasks(): Promise<UpcomingTask[]> {
    await this.ensureInitialized();

    const records = await all<TaskRecord>(this.db!, `
      SELECT id, name, description, frequency_days, advance_notice_days,
             category, home_type, reminder_id, next_due, created_at
      FROM tasks
      ORDER BY next_due ASC
    `);

    const due: UpcomingTask[] = [];
    const now = new Date();

    for (const record of records) {
      const nextDue = new Date(record.next_due);
      const daysUntil = this.daysUntil(nextDue);
      
      // Task is due if it's past due or within notice period
      const noticeDate = new Date(nextDue);
      noticeDate.setDate(noticeDate.getDate() - record.advance_notice_days);

      if (now >= noticeDate) {
        due.push({
          task: this.mapTaskRecord(record),
          daysUntil,
          isNoticePeriod: daysUntil > 0,
          noticeInDays: Math.max(0, daysUntil),
        });
      }
    }

    return due;
  }

  /**
   * Get completion history
   */
  async getCompletionHistory(limit: number = 50): Promise<CompletionHistory[]> {
    await this.ensureInitialized();

    const records = await all<CompletionRecord>(this.db!, `
      SELECT id, task_id, task_name, completed_at, notes
      FROM completion_history
      ORDER BY completed_at DESC
      LIMIT ?
    `, [limit]);

    return records.map(record => ({
      id: record.id,
      taskId: record.task_id,
      taskName: record.task_name,
      completedAt: record.completed_at,
      notes: record.notes,
    }));
  }

  /**
   * Get tasks by category
   */
  async getTasksByCategory(category: TaskCategory): Promise<MaintenanceTask[]> {
    return this.listTasks(category);
  }

  /**
   * Apply a seasonal template
   */
  async applyTemplate(homeType: HomeType): Promise<{
    created: number;
    tasks: MaintenanceTask[];
  }> {
    await this.ensureInitialized();

    const template = maintenanceTemplates[homeType];
    if (!template) {
      throw new Error(`Unknown template: ${homeType}`);
    }

    const created: MaintenanceTask[] = [];

    for (const templateTask of template) {
      const task = await this.createTask({
        name: templateTask.name,
        description: templateTask.description,
        frequencyDays: templateTask.frequencyDays,
        advanceNoticeDays: templateTask.advanceNoticeDays,
        category: templateTask.category,
        homeType,
      });
      created.push(task);
    }

    return {
      created: created.length,
      tasks: created,
    };
  }

  /**
   * Preview a template (without creating)
   */
  previewTemplate(homeType: HomeType): TemplateTask[] {
    return maintenanceTemplates[homeType] || [];
  }

  /**
   * Get available templates
   */
  getAvailableTemplates(): { type: HomeType; name: string; taskCount: number }[] {
    return [
      { type: 'house', name: 'House Maintenance', taskCount: maintenanceTemplates.house.length },
      { type: 'apartment', name: 'Apartment Maintenance', taskCount: maintenanceTemplates.apartment.length },
      { type: 'condo', name: 'Condo Maintenance', taskCount: maintenanceTemplates.condo.length },
    ];
  }

  /**
   * Get completion statistics
   */
  async getStats(): Promise<CompletionStats> {
    await this.ensureInitialized();

    const totalTasksResult = await get<{ count: number }>(this.db!, `SELECT COUNT(*) as count FROM tasks`);
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const startOfYear = new Date(now.getFullYear(), 0, 1);

    const thisMonthResult = await get<{ count: number }>(this.db!, 
      `SELECT COUNT(*) as count FROM completion_history WHERE completed_at >= ?`,
      [startOfMonth.toISOString()]
    );

    const thisYearResult = await get<{ count: number }>(this.db!,
      `SELECT COUNT(*) as count FROM completion_history WHERE completed_at >= ?`,
      [startOfYear.toISOString()]
    );

    const overdueResult = await get<{ count: number }>(this.db!,
      `SELECT COUNT(*) as count FROM tasks WHERE next_due < ?`,
      [now.toISOString()]
    );

    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
    const upcomingResult = await get<{ count: number }>(this.db!,
      `SELECT COUNT(*) as count FROM tasks WHERE next_due <= ?`,
      [thirtyDaysFromNow.toISOString()]
    );

    // Get counts by category
    const categoryResults = await all<{ category: TaskCategory; count: number }>(this.db!,
      `SELECT category, COUNT(*) as count FROM tasks GROUP BY category`
    );

    const byCategory: Record<TaskCategory, number> = {
      indoor: 0, outdoor: 0, hvac: 0, plumbing: 0, electrical: 0,
      appliance: 0, safety: 0, cleaning: 0, other: 0,
    };

    for (const row of categoryResults) {
      byCategory[row.category] = row.count;
    }

    return {
      totalTasks: totalTasksResult?.count || 0,
      completedThisMonth: thisMonthResult?.count || 0,
      completedThisYear: thisYearResult?.count || 0,
      overdueTasks: overdueResult?.count || 0,
      upcomingTasks: upcomingResult?.count || 0,
      byCategory,
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthCheckResult> {
    try {
      await this.ensureInitialized();

      const stats = await this.getStats();
      const upcoming = await this.getUpcomingTasks(30);
      const due = await this.getDueTasks();

      return {
        status: 'healthy',
        tasks: stats.totalTasks,
        completions: stats.completedThisYear,
        upcoming: upcoming.length,
        overdue: due.filter(t => t.daysUntil < 0).length,
        database: this.dbPath,
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        tasks: 0,
        completions: 0,
        upcoming: 0,
        overdue: 0,
        database: this.dbPath,
        error: error instanceof Error ? error.message : String(error),
      };
    }
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
    await this.remindersSkill.close();
  }

  /**
   * Map database record to MaintenanceTask interface
   */
  private mapTaskRecord(record: TaskRecord): MaintenanceTask {
    return {
      id: record.id,
      name: record.name,
      description: record.description,
      frequencyDays: record.frequency_days,
      advanceNoticeDays: record.advance_notice_days,
      category: record.category,
      homeType: record.home_type,
      reminderId: record.reminder_id,
      nextDue: record.next_due,
      createdAt: record.created_at,
    };
  }
}

// Default export
export default MaintenanceSchedulerSkill;
