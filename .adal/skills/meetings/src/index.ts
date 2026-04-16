/**
 * Meetings Skill
 * Coordinate meetings using calendar and email integration
 * Built on top of calendar and email skills
 */

import { CalendarSkill, CalendarEvent, TimeSlot } from '@openclaw/calendar';
import { EmailSkill } from '@openclaw/email';
import * as sqlite3 from 'sqlite3';
import path from 'path';
import os from 'os';
import fs from 'fs';

/**
 * Meeting attendee
 */
export interface MeetingAttendee {
  email: string;
  name?: string;
  optional?: boolean;
  responseStatus?: 'needsAction' | 'declined' | 'tentative' | 'accepted';
}

/**
 * Agenda item
 */
export interface AgendaItem {
  id: string;
  title: string;
  duration: number; // in minutes
  presenter?: string;
  description?: string;
}

/**
 * Meeting prep document
 */
export interface PrepDocument {
  id: string;
  name: string;
  url?: string;
  content?: string;
  type: 'link' | 'file' | 'note';
  required: boolean;
}

/**
 * Meeting record
 */
export interface Meeting {
  id: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
  timeZone: string;
  location?: string;
  videoLink?: string;
  attendees: MeetingAttendee[];
  agenda: AgendaItem[];
  prepDocuments: PrepDocument[];
  calendarEventId?: string;
  status: 'draft' | 'scheduled' | 'cancelled' | 'completed';
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Meeting request for scheduling
 */
export interface MeetingRequest {
  title: string;
  description?: string;
  duration: number; // in minutes
  attendees: string[]; // email addresses
  timeRange: {
    start: string; // ISO date
    end: string; // ISO date
  };
  preferredTimes?: string[]; // preferred ISO datetimes
  timeZone?: string;
  location?: string;
  agenda?: Array<{
    title: string;
    duration: number;
    presenter?: string;
    description?: string;
  }>;
  prepDocuments?: Array<{
    name: string;
    url?: string;
    type: 'link' | 'file' | 'note';
    required?: boolean;
  }>;
}

/**
 * Scheduling options
 */
export interface ScheduleOptions {
  title: string;
  description?: string;
  duration: number;
  attendees: string[];
  timeMin: string;
  timeMax: string;
  timeZone?: string;
  location?: string;
  agenda?: Array<{
    title: string;
    duration: number;
    presenter?: string;
    description?: string;
  }>;
  sendInvites?: boolean;
  sendPrepEmail?: boolean;
}

/**
 * Scheduling result
 */
export interface ScheduleResult {
  success: boolean;
  meeting?: Meeting;
  error?: string;
  suggestedSlots?: TimeSlot[];
  conflicts?: string[];
}

/**
 * Meeting template
 */
export interface MeetingTemplate {
  id: string;
  name: string;
  title: string;
  description?: string;
  duration: number;
  agenda: AgendaItem[];
  prepDocuments: PrepDocument[];
}

/**
 * Meetings skill configuration
 */
export interface MeetingsSkillConfig {
  profile?: string;
  dataDir?: string;
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

function runWithResult(db: sqlite3.Database, sql: string, params: any[] = []): Promise<{ lastID: number; changes: number }> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(this: sqlite3.RunResult, err: Error | null) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

/**
 * Meetings Skill - Coordinate meetings using calendar and email
 */
export class MeetingsSkill {
  private calendar: CalendarSkill;
  private email: EmailSkill;
  private profile: string;
  private dataDir: string;
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;

  constructor(config: MeetingsSkillConfig = {}) {
    this.profile = config.profile || 'default';
    this.dataDir = config.dataDir || path.join(os.homedir(), '.openclaw', 'skills', 'meetings');
    this.calendar = new CalendarSkill({ profile: this.profile });
    this.email = new EmailSkill({ profile: this.profile });
    this.initPromise = this.initStorage();
  }

  /**
   * Create MeetingsSkill for a specific profile
   */
  static forProfile(profile: string = 'default'): MeetingsSkill {
    return new MeetingsSkill({ profile });
  }

  /**
   * Initialize storage directory and database
   */
  private async initStorage(): Promise<void> {
    try {
      if (!fs.existsSync(this.dataDir)) {
        fs.mkdirSync(this.dataDir, { recursive: true, mode: 0o700 });
      }

      const dbPath = path.join(this.dataDir, 'meetings.db');
      
      this.db = await new Promise<sqlite3.Database>((resolve, reject) => {
        const db = new sqlite3.Database(dbPath, (err) => {
          if (err) reject(err);
          else resolve(db);
        });
      });

      // Create meetings table
      await run(this.db, `
        CREATE TABLE IF NOT EXISTS meetings (
          id TEXT PRIMARY KEY,
          profile TEXT NOT NULL,
          title TEXT NOT NULL,
          description TEXT,
          start_time TEXT NOT NULL,
          end_time TEXT NOT NULL,
          time_zone TEXT NOT NULL,
          location TEXT,
          video_link TEXT,
          attendees TEXT NOT NULL,
          agenda TEXT,
          prep_documents TEXT,
          calendar_event_id TEXT,
          status TEXT DEFAULT 'draft',
          notes TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
      `);

      await run(this.db, `
        CREATE INDEX IF NOT EXISTS idx_meetings_profile ON meetings(profile)
      `);
      await run(this.db, `
        CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)
      `);
      await run(this.db, `
        CREATE INDEX IF NOT EXISTS idx_meetings_time ON meetings(start_time, end_time)
      `);

      // Create templates table
      await run(this.db, `
        CREATE TABLE IF NOT EXISTS templates (
          id TEXT PRIMARY KEY,
          profile TEXT NOT NULL,
          name TEXT NOT NULL,
          title TEXT NOT NULL,
          description TEXT,
          duration INTEGER NOT NULL,
          agenda TEXT,
          prep_documents TEXT,
          created_at TEXT NOT NULL
        )
      `);

      await run(this.db, `
        CREATE INDEX IF NOT EXISTS idx_templates_profile ON templates(profile)
      `);

      // Insert default templates
      await this.insertDefaultTemplates();
    } catch (error) {
      console.error('Failed to initialize storage:', error);
      this.db = null;
    }
  }

  /**
   * Insert default meeting templates
   */
  private async insertDefaultTemplates(): Promise<void> {
    if (!this.db) return;

    const defaults: Omit<MeetingTemplate, 'id'>[] = [
      {
        name: 'Standup',
        title: 'Daily Standup',
        description: 'Daily team sync to discuss progress and blockers',
        duration: 15,
        agenda: [
          { id: '1', title: 'What did you do yesterday?', duration: 5 },
          { id: '2', title: 'What will you do today?', duration: 5 },
          { id: '3', title: 'Any blockers?', duration: 5 },
        ],
        prepDocuments: [],
      },
      {
        name: 'Sprint Planning',
        title: 'Sprint Planning',
        description: 'Plan work for the upcoming sprint',
        duration: 120,
        agenda: [
          { id: '1', title: 'Review previous sprint', duration: 20 },
          { id: '2', title: 'Sprint goal discussion', duration: 15 },
          { id: '3', title: 'Story estimation', duration: 60 },
          { id: '4', title: 'Sprint commitment', duration: 15 },
          { id: '5', title: 'Action items', duration: 10 },
        ],
        prepDocuments: [
          { id: '1', name: 'Backlog', type: 'link', required: true },
          { id: '2', name: 'Velocity Chart', type: 'link', required: true },
        ],
      },
      {
        name: '1-on-1',
        title: '1-on-1 with {attendee}',
        description: 'Regular check-in',
        duration: 30,
        agenda: [
          { id: '1', title: 'Updates from last time', duration: 5 },
          { id: '2', title: 'Current priorities', duration: 10 },
          { id: '3', title: 'Challenges and blockers', duration: 10 },
          { id: '4', title: 'Career development', duration: 5 },
        ],
        prepDocuments: [],
      },
      {
        name: 'Retrospective',
        title: 'Sprint Retrospective',
        description: 'Reflect on the sprint and identify improvements',
        duration: 60,
        agenda: [
          { id: '1', title: 'What went well?', duration: 15 },
          { id: '2', title: 'What could be improved?', duration: 15 },
          { id: '3', title: 'Action items', duration: 20 },
          { id: '4', title: 'Closing', duration: 10 },
        ],
        prepDocuments: [],
      },
      {
        name: 'Review',
        title: 'Project Review',
        description: 'Review project progress and deliverables',
        duration: 60,
        agenda: [
          { id: '1', title: 'Project status overview', duration: 15 },
          { id: '2', title: 'Demo/Review deliverables', duration: 30 },
          { id: '3', title: 'Feedback and discussion', duration: 15 },
        ],
        prepDocuments: [
          { id: '1', name: 'Project Status Report', type: 'link', required: true },
        ],
      },
    ];

    for (const template of defaults) {
      const existing = await get<{ count: number }>(
        this.db,
        'SELECT COUNT(*) as count FROM templates WHERE profile = ? AND name = ?',
        [this.profile, template.name]
      );
      
      if (existing && existing.count === 0) {
        const id = `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        await run(this.db, `
          INSERT INTO templates (id, profile, name, title, description, duration, agenda, prep_documents, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [
          id,
          this.profile,
          template.name,
          template.title,
          template.description || null,
          template.duration,
          JSON.stringify(template.agenda),
          JSON.stringify(template.prepDocuments),
          new Date().toISOString(),
        ]);
      }
    }
  }

  /**
   * Ensure storage is initialized
   */
  private async ensureStorage(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  /**
   * Check if required services are connected
   */
  async getStatus(): Promise<{
    connected: boolean;
    calendarConnected: boolean;
    emailConnected: boolean;
    email?: string;
  }> {
    const calendarStatus = await this.calendar.getStatus();
    const emailStatus = await this.email.getStatus();

    return {
      connected: calendarStatus.connected && emailStatus.connected,
      calendarConnected: calendarStatus.connected,
      emailConnected: emailStatus.connected,
      email: calendarStatus.email || emailStatus.email,
    };
  }

  /**
   * Find mutual availability for a meeting
   */
  async findAvailability(options: {
    attendees: string[];
    duration: number;
    timeMin: string;
    timeMax: string;
    timeZone?: string;
  }): Promise<{
    availableSlots: TimeSlot[];
    conflicts: Array<{
      email: string;
      busySlots: TimeSlot[];
    }>;
  }> {
    // Get available slots from calendar
    const availableSlots = await this.calendar.findFreeTime({
      timeMin: options.timeMin,
      timeMax: options.timeMax,
      duration: options.duration,
      timeZone: options.timeZone,
    });

    // For external attendees without calendar access, we can't check their availability
    // Return the slots for manual coordination
    return {
      availableSlots,
      conflicts: [],
    };
  }

  /**
   * Schedule a new meeting
   */
  async schedule(options: ScheduleOptions): Promise<ScheduleResult> {
    try {
      const status = await this.getStatus();
      if (!status.connected) {
        return {
          success: false,
          error: 'Calendar and email must be connected. Please authenticate first.',
        };
      }

      // Find available slots
      const availability = await this.findAvailability({
        attendees: options.attendees,
        duration: options.duration,
        timeMin: options.timeMin,
        timeMax: options.timeMax,
        timeZone: options.timeZone,
      });

      if (availability.availableSlots.length === 0) {
        return {
          success: false,
          error: 'No available time slots found in the specified range',
          suggestedSlots: [],
        };
      }

      // Use the first available slot
      const slot = availability.availableSlots[0];
      const startTime = new Date(slot.start);
      const endTime = new Date(startTime.getTime() + options.duration * 60 * 1000);
      const timeZone = options.timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone;

      // Build agenda
      const agenda: AgendaItem[] = options.agenda?.map((item, idx) => ({
        id: `item_${idx}`,
        title: item.title,
        duration: item.duration,
        presenter: item.presenter,
        description: item.description,
      })) || [];

      // Create calendar event
      const calendarEvent = await this.calendar.createEvent({
        summary: options.title,
        description: this.buildAgendaText(options.title, agenda, options.description),
        location: options.location,
        start: {
          dateTime: startTime.toISOString(),
          timeZone,
        },
        end: {
          dateTime: endTime.toISOString(),
          timeZone,
        },
        attendees: options.attendees.map(email => ({ email })),
      });

      // Create meeting record
      const meeting: Meeting = {
        id: `meeting_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: options.title,
        description: options.description,
        startTime: startTime.toISOString(),
        endTime: endTime.toISOString(),
        timeZone,
        location: options.location,
        attendees: options.attendees.map(email => ({
          email,
          responseStatus: 'needsAction',
        })),
        agenda,
        prepDocuments: [],
        calendarEventId: calendarEvent.id,
        status: 'scheduled',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // Save to database
      await this.saveMeeting(meeting);

      // Send invites via email if requested
      if (options.sendInvites) {
        await this.sendMeetingInvite(meeting);
      }

      // Send prep email if requested
      if (options.sendPrepEmail && agenda.length > 0) {
        await this.sendPrepEmail(meeting);
      }

      return {
        success: true,
        meeting,
        suggestedSlots: availability.availableSlots.slice(1, 4),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Create a meeting from a template
   */
  async scheduleFromTemplate(
    templateName: string,
    options: {
      title?: string;
      attendees: string[];
      timeMin: string;
      timeMax: string;
      timeZone?: string;
      location?: string;
      sendInvites?: boolean;
    }
  ): Promise<ScheduleResult> {
    const template = await this.getTemplate(templateName);
    
    if (!template) {
      return {
        success: false,
        error: `Template '${templateName}' not found`,
      };
    }

    const title = options.title || template.title;

    return this.schedule({
      title,
      description: template.description,
      duration: template.duration,
      attendees: options.attendees,
      timeMin: options.timeMin,
      timeMax: options.timeMax,
      timeZone: options.timeZone,
      location: options.location,
      agenda: template.agenda.map(item => ({
        title: item.title,
        duration: item.duration,
        presenter: item.presenter,
        description: item.description,
      })),
      sendInvites: options.sendInvites,
    });
  }

  /**
   * Send meeting invite email
   */
  async sendMeetingInvite(meeting: Meeting): Promise<void> {
    const subject = `Meeting Invite: ${meeting.title}`;
    
    const bodyText = this.buildInviteEmail(meeting);
    const bodyHtml = this.buildInviteEmailHtml(meeting);

    for (const attendee of meeting.attendees) {
      await this.email.send({
        to: attendee.email,
        subject,
        bodyText,
        bodyHtml,
      });
    }
  }

  /**
   * Send prep materials email
   */
  async sendPrepEmail(meeting: Meeting): Promise<void> {
    if (meeting.agenda.length === 0 && meeting.prepDocuments.length === 0) {
      return;
    }

    const subject = `Prep for: ${meeting.title}`;
    const bodyText = this.buildPrepEmail(meeting);
    const bodyHtml = this.buildPrepEmailHtml(meeting);

    for (const attendee of meeting.attendees) {
      await this.email.send({
        to: attendee.email,
        subject,
        bodyText,
        bodyHtml,
      });
    }
  }

  /**
   * Get a meeting by ID
   */
  async getMeeting(id: string): Promise<Meeting | null> {
    await this.ensureStorage();
    if (!this.db) return null;

    const row = await get<{
      id: string;
      title: string;
      description: string | null;
      start_time: string;
      end_time: string;
      time_zone: string;
      location: string | null;
      video_link: string | null;
      attendees: string;
      agenda: string | null;
      prep_documents: string | null;
      calendar_event_id: string | null;
      status: string;
      notes: string | null;
      created_at: string;
      updated_at: string;
    }>(this.db, 'SELECT * FROM meetings WHERE id = ? AND profile = ?', [id, this.profile]);

    if (!row) return null;

    return this.rowToMeeting(row);
  }

  /**
   * List meetings
   */
  async listMeetings(options: {
    status?: Meeting['status'];
    from?: string;
    to?: string;
    limit?: number;
  } = {}): Promise<Meeting[]> {
    await this.ensureStorage();
    if (!this.db) return [];

    let sql = 'SELECT * FROM meetings WHERE profile = ?';
    const params: any[] = [this.profile];

    if (options.status) {
      sql += ' AND status = ?';
      params.push(options.status);
    }

    if (options.from) {
      sql += ' AND start_time >= ?';
      params.push(options.from);
    }

    if (options.to) {
      sql += ' AND start_time <= ?';
      params.push(options.to);
    }

    sql += ' ORDER BY start_time DESC';

    if (options.limit) {
      sql += ' LIMIT ?';
      params.push(options.limit);
    }

    const rows = await all<{
      id: string;
      title: string;
      description: string | null;
      start_time: string;
      end_time: string;
      time_zone: string;
      location: string | null;
      video_link: string | null;
      attendees: string;
      agenda: string | null;
      prep_documents: string | null;
      calendar_event_id: string | null;
      status: string;
      notes: string | null;
      created_at: string;
      updated_at: string;
    }>(this.db, sql, params);

    return rows.map(row => this.rowToMeeting(row));
  }

  /**
   * Update a meeting
   */
  async updateMeeting(
    id: string,
    updates: Partial<Omit<Meeting, 'id' | 'createdAt'>>
  ): Promise<Meeting | null> {
    await this.ensureStorage();
    if (!this.db) return null;

    const existing = await this.getMeeting(id);
    if (!existing) return null;

    // Update calendar event if times change
    if (updates.startTime || updates.endTime || updates.title || updates.description) {
      if (existing.calendarEventId) {
        await this.calendar.updateEvent(existing.calendarEventId, {
          summary: updates.title || existing.title,
          description: updates.description !== undefined ? updates.description : existing.description,
          start: updates.startTime ? { dateTime: updates.startTime } : undefined,
          end: updates.endTime ? { dateTime: updates.endTime } : undefined,
          location: updates.location,
        });
      }
    }

    const updated: Meeting = {
      ...existing,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    await run(this.db, `
      UPDATE meetings SET
        title = ?,
        description = ?,
        start_time = ?,
        end_time = ?,
        time_zone = ?,
        location = ?,
        video_link = ?,
        attendees = ?,
        agenda = ?,
        prep_documents = ?,
        calendar_event_id = ?,
        status = ?,
        notes = ?,
        updated_at = ?
      WHERE id = ? AND profile = ?
    `, [
      updated.title,
      updated.description || null,
      updated.startTime,
      updated.endTime,
      updated.timeZone,
      updated.location || null,
      updated.videoLink || null,
      JSON.stringify(updated.attendees),
      updated.agenda.length > 0 ? JSON.stringify(updated.agenda) : null,
      updated.prepDocuments.length > 0 ? JSON.stringify(updated.prepDocuments) : null,
      updated.calendarEventId || null,
      updated.status,
      updated.notes || null,
      updated.updatedAt,
      id,
      this.profile,
    ]);

    return updated;
  }

  /**
   * Cancel a meeting
   */
  async cancelMeeting(id: string, notifyAttendees: boolean = true): Promise<boolean> {
    const meeting = await this.getMeeting(id);
    if (!meeting) return false;

    // Cancel calendar event
    if (meeting.calendarEventId) {
      try {
        await this.calendar.updateEvent(meeting.calendarEventId, {
          status: 'cancelled',
        });
      } catch (e) {
        // Event might already be deleted
      }
    }

    // Update database
    await this.updateMeeting(id, { status: 'cancelled' });

    // Send cancellation email
    if (notifyAttendees) {
      await this.sendCancellationEmail(meeting);
    }

    return true;
  }

  /**
   * Delete a meeting
   */
  async deleteMeeting(id: string): Promise<boolean> {
    await this.ensureStorage();
    if (!this.db) return false;

    const meeting = await this.getMeeting(id);
    if (!meeting) return false;

    // Delete calendar event
    if (meeting.calendarEventId) {
      try {
        await this.calendar.deleteEvent(meeting.calendarEventId);
      } catch (e) {
        // Event might already be deleted
      }
    }

    // Delete from database
    await run(this.db, 'DELETE FROM meetings WHERE id = ? AND profile = ?', [id, this.profile]);

    return true;
  }

  /**
   * Get meeting templates
   */
  async getTemplate(name: string): Promise<MeetingTemplate | null> {
    await this.ensureStorage();
    if (!this.db) return null;

    const row = await get<{
      id: string;
      name: string;
      title: string;
      description: string | null;
      duration: number;
      agenda: string | null;
      prep_documents: string | null;
    }>(this.db, 'SELECT * FROM templates WHERE profile = ? AND name = ?', [this.profile, name]);

    if (!row) return null;

    return {
      id: row.id,
      name: row.name,
      title: row.title,
      description: row.description || undefined,
      duration: row.duration,
      agenda: row.agenda ? JSON.parse(row.agenda) : [],
      prepDocuments: row.prep_documents ? JSON.parse(row.prep_documents) : [],
    };
  }

  /**
   * List all templates
   */
  async listTemplates(): Promise<MeetingTemplate[]> {
    await this.ensureStorage();
    if (!this.db) return [];

    const rows = await all<{
      id: string;
      name: string;
      title: string;
      description: string | null;
      duration: number;
      agenda: string | null;
      prep_documents: string | null;
    }>(this.db, 'SELECT * FROM templates WHERE profile = ? ORDER BY name', [this.profile]);

    return rows.map(row => ({
      id: row.id,
      name: row.name,
      title: row.title,
      description: row.description || undefined,
      duration: row.duration,
      agenda: row.agenda ? JSON.parse(row.agenda) : [],
      prepDocuments: row.prep_documents ? JSON.parse(row.prep_documents) : [],
    }));
  }

  /**
   * Create a custom template
   */
  async createTemplate(template: Omit<MeetingTemplate, 'id'>): Promise<MeetingTemplate> {
    await this.ensureStorage();
    if (!this.db) throw new Error('Storage not initialized');

    const id = `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    await run(this.db, `
      INSERT INTO templates (id, profile, name, title, description, duration, agenda, prep_documents, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      id,
      this.profile,
      template.name,
      template.title,
      template.description || null,
      template.duration,
      JSON.stringify(template.agenda),
      JSON.stringify(template.prepDocuments),
      new Date().toISOString(),
    ]);

    return { ...template, id };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    message?: string;
    email?: string;
  }> {
    const status = await this.getStatus();

    if (!status.connected) {
      if (!status.calendarConnected) {
        return { status: 'unhealthy', message: 'Calendar not connected' };
      }
      if (!status.emailConnected) {
        return { status: 'unhealthy', message: 'Email not connected' };
      }
    }

    // Check calendar health
    const calendarHealth = await this.calendar.healthCheck();
    if (calendarHealth.status !== 'healthy') {
      return { status: 'unhealthy', message: `Calendar: ${calendarHealth.message}`, email: status.email };
    }

    // Check email health
    const emailHealth = await this.email.healthCheck();
    if (emailHealth.status !== 'healthy') {
      return { status: 'unhealthy', message: `Email: ${emailHealth.message}`, email: status.email };
    }

    return { status: 'healthy', message: 'Meetings skill operational', email: status.email };
  }

  // Private helper methods

  private async saveMeeting(meeting: Meeting): Promise<void> {
    await this.ensureStorage();
    if (!this.db) throw new Error('Storage not initialized');

    await run(this.db, `
      INSERT INTO meetings (
        id, profile, title, description, start_time, end_time, time_zone,
        location, video_link, attendees, agenda, prep_documents,
        calendar_event_id, status, notes, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      meeting.id,
      this.profile,
      meeting.title,
      meeting.description || null,
      meeting.startTime,
      meeting.endTime,
      meeting.timeZone,
      meeting.location || null,
      meeting.videoLink || null,
      JSON.stringify(meeting.attendees),
      meeting.agenda.length > 0 ? JSON.stringify(meeting.agenda) : null,
      meeting.prepDocuments.length > 0 ? JSON.stringify(meeting.prepDocuments) : null,
      meeting.calendarEventId || null,
      meeting.status,
      meeting.notes || null,
      meeting.createdAt,
      meeting.updatedAt,
    ]);
  }

  private rowToMeeting(row: {
    id: string;
    title: string;
    description: string | null;
    start_time: string;
    end_time: string;
    time_zone: string;
    location: string | null;
    video_link: string | null;
    attendees: string;
    agenda: string | null;
    prep_documents: string | null;
    calendar_event_id: string | null;
    status: string;
    notes: string | null;
    created_at: string;
    updated_at: string;
  }): Meeting {
    return {
      id: row.id,
      title: row.title,
      description: row.description || undefined,
      startTime: row.start_time,
      endTime: row.end_time,
      timeZone: row.time_zone,
      location: row.location || undefined,
      videoLink: row.video_link || undefined,
      attendees: JSON.parse(row.attendees),
      agenda: row.agenda ? JSON.parse(row.agenda) : [],
      prepDocuments: row.prep_documents ? JSON.parse(row.prep_documents) : [],
      calendarEventId: row.calendar_event_id || undefined,
      status: row.status as Meeting['status'],
      notes: row.notes || undefined,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }

  private buildAgendaText(title: string, agenda: AgendaItem[], description?: string): string {
    const lines: string[] = [];
    
    if (description) {
      lines.push(description);
      lines.push('');
    }
    
    if (agenda.length > 0) {
      lines.push('AGENDA');
      lines.push('');
      
      let totalMinutes = 0;
      for (const item of agenda) {
        lines.push(`${item.title} (${item.duration} min)`);
        if (item.presenter) {
          lines.push(`  Presenter: ${item.presenter}`);
        }
        if (item.description) {
          lines.push(`  ${item.description}`);
        }
        totalMinutes += item.duration;
        lines.push('');
      }
      
      lines.push(`Total Duration: ${totalMinutes} minutes`);
    }
    
    return lines.join('\n');
  }

  private buildInviteEmail(meeting: Meeting): string {
    const lines: string[] = [
      `Meeting: ${meeting.title}`,
      '',
      `Time: ${new Date(meeting.startTime).toLocaleString()} - ${new Date(meeting.endTime).toLocaleTimeString()}`,
    ];

    if (meeting.location) {
      lines.push(`Location: ${meeting.location}`);
    }

    if (meeting.videoLink) {
      lines.push(`Video Link: ${meeting.videoLink}`);
    }

    if (meeting.description) {
      lines.push('');
      lines.push(meeting.description);
    }

    if (meeting.agenda.length > 0) {
      lines.push('');
      lines.push('AGENDA:');
      for (const item of meeting.agenda) {
        lines.push(`  • ${item.title} (${item.duration} min)`);
      }
    }

    return lines.join('\n');
  }

  private buildInviteEmailHtml(meeting: Meeting): string {
    let html = `
      <h2>${meeting.title}</h2>
      <p><strong>Time:</strong> ${new Date(meeting.startTime).toLocaleString()} - ${new Date(meeting.endTime).toLocaleTimeString()}</p>
    `;

    if (meeting.location) {
      html += `<p><strong>Location:</strong> ${meeting.location}</p>`;
    }

    if (meeting.videoLink) {
      html += `<p><strong>Video Link:</strong> <a href="${meeting.videoLink}">${meeting.videoLink}</a></p>`;
    }

    if (meeting.description) {
      html += `<p>${meeting.description.replace(/\n/g, '<br>')}</p>`;
    }

    if (meeting.agenda.length > 0) {
      html += '<h3>Agenda</h3><ul>';
      for (const item of meeting.agenda) {
        html += `<li>${item.title} (${item.duration} min)</li>`;
      }
      html += '</ul>';
    }

    return html;
  }

  private buildPrepEmail(meeting: Meeting): string {
    const lines: string[] = [
      `Meeting: ${meeting.title}`,
      `Time: ${new Date(meeting.startTime).toLocaleString()}`,
      '',
      'Please review the following before the meeting:',
      '',
    ];

    if (meeting.agenda.length > 0) {
      lines.push('AGENDA:');
      for (const item of meeting.agenda) {
        lines.push(`  • ${item.title} (${item.duration} min)`);
        if (item.description) {
          lines.push(`    ${item.description}`);
        }
      }
      lines.push('');
    }

    if (meeting.prepDocuments.length > 0) {
      lines.push('PREP MATERIALS:');
      for (const doc of meeting.prepDocuments) {
        const required = doc.required ? '[REQUIRED]' : '[Optional]';
        lines.push(`  ${required} ${doc.name}`);
        if (doc.url) {
          lines.push(`    ${doc.url}`);
        }
      }
    }

    return lines.join('\n');
  }

  private buildPrepEmailHtml(meeting: Meeting): string {
    let html = `
      <h2>Meeting Prep: ${meeting.title}</h2>
      <p><strong>Time:</strong> ${new Date(meeting.startTime).toLocaleString()}</p>
      <p>Please review the following before the meeting:</p>
    `;

    if (meeting.agenda.length > 0) {
      html += '<h3>Agenda</h3><ul>';
      for (const item of meeting.agenda) {
        html += `<li><strong>${item.title}</strong> (${item.duration} min)`;
        if (item.description) {
          html += `<br><small>${item.description}</small>`;
        }
        html += '</li>';
      }
      html += '</ul>';
    }

    if (meeting.prepDocuments.length > 0) {
      html += '<h3>Prep Materials</h3><ul>';
      for (const doc of meeting.prepDocuments) {
        const required = doc.required ? '<span style="color:red">[REQUIRED]</span>' : '[Optional]';
        html += `<li>${required} `;
        if (doc.url) {
          html += `<a href="${doc.url}">${doc.name}</a>`;
        } else {
          html += doc.name;
        }
        html += '</li>';
      }
      html += '</ul>';
    }

    return html;
  }

  private async sendCancellationEmail(meeting: Meeting): Promise<void> {
    const subject = `CANCELLED: ${meeting.title}`;
    const bodyText = `
This meeting has been cancelled.

Meeting: ${meeting.title}
Original Time: ${new Date(meeting.startTime).toLocaleString()}

Please disregard the previous invitation.
`.trim();

    const bodyHtml = `
<h2>Meeting Cancelled</h2>
<p>This meeting has been cancelled.</p>
<p><strong>Meeting:</strong> ${meeting.title}<br>
<strong>Original Time:</strong> ${new Date(meeting.startTime).toLocaleString()}</p>
<p>Please disregard the previous invitation.</p>
`;

    for (const attendee of meeting.attendees) {
      await this.email.send({
        to: attendee.email,
        subject,
        bodyText,
        bodyHtml,
      });
    }
  }

  /**
   * Close connections
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
    
    await this.calendar.close();
    await this.email.close();
  }
}

// Factory function
export function getMeetingsSkill(profile?: string): MeetingsSkill {
  return new MeetingsSkill({ profile });
}

export default MeetingsSkill;
