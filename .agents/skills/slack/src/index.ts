import { SlackAuthClient } from '@openclaw/slack-auth';
import * as sqlite3 from 'sqlite3';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Template types
export interface NotificationTemplate {
  id?: number;
  name: string;
  channel?: string;
  text: string;
  blocks?: object[];
  attachments?: object[];
  createdAt?: string;
  updatedAt?: string;
}

// Message options
export interface MessageOptions {
  channel: string;
  text: string;
  blocks?: object[];
  attachments?: object[];
  threadTs?: string;
  unfurlLinks?: boolean;
  unfurlMedia?: boolean;
  mrkdwn?: boolean;
}

// File upload options
export interface FileUploadOptions {
  channels: string;
  file?: string;
  content?: string;
  filename?: string;
  title?: string;
  initialComment?: string;
  threadTs?: string;
}

// Channel creation options
export interface CreateChannelOptions {
  name: string;
  isPrivate?: boolean;
  description?: string;
}

// Message response
export interface MessageResponse {
  ok: boolean;
  channel?: string;
  ts?: string;
  message?: object;
  error?: string;
  warning?: string;
}

// Channel info
export interface ChannelInfo {
  id: string;
  name: string;
  isPrivate: boolean;
  numMembers: number;
  topic?: string;
  purpose?: string;
  created: number;
  creator: string;
}

// User info
export interface UserInfo {
  id: string;
  name: string;
  realName?: string;
  email?: string;
  isAdmin: boolean;
  isBot: boolean;
  avatar?: string;
}

// Database run result
interface RunResult {
  lastID: number;
  changes: number;
}

export class SlackSkill {
  private auth: SlackAuthClient;
  private db: sqlite3.Database | null = null;
  private dbPath: string;
  private profile: string;
  private initPromise: Promise<void> | null = null;

  constructor(profile: string = 'default') {
    this.profile = profile;
    this.auth = SlackAuthClient.forProfile(profile);
    this.dbPath = path.join(os.homedir(), '.openclaw', 'skills', 'slack', `${profile}.db`);
  }

  /**
   * Create a skill instance for a specific profile
   */
  static forProfile(profile: string): SlackSkill {
    return new SlackSkill(profile);
  }

  /**
   * Initialize the database
   */
  private async initDb(): Promise<void> {
    if (this.db) return;
    if (this.initPromise) return this.initPromise;

    this.initPromise = this.doInitDb();
    return this.initPromise;
  }

  private async doInitDb(): Promise<void> {
    // Ensure directory exists
    const dir = path.dirname(this.dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
    }

    this.db = new (sqlite3 as any).Database(this.dbPath);

    // Initialize schema using serialize to ensure proper ordering
    await new Promise<void>((resolve, reject) => {
      this.db!.serialize(() => {
        this.db!.run(`
          CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            channel TEXT,
            text TEXT NOT NULL,
            blocks TEXT,
            attachments TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        this.db!.run(`
          CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL,
            text TEXT,
            ts TEXT,
            thread_ts TEXT,
            template_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        this.db!.run(`CREATE INDEX IF NOT EXISTS idx_templates_name ON templates(name)`);
        this.db!.run(`CREATE INDEX IF NOT EXISTS idx_messages_channel ON sent_messages(channel)`);
        this.db!.run(`CREATE INDEX IF NOT EXISTS idx_messages_ts ON sent_messages(ts)`, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    });
  }

  /**
   * Promisified db.run that returns lastID
   */
  private runWithResult(sql: string, params: any[] = []): Promise<RunResult> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      this.db.run(sql, params, function(this: any, err: Error | null) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  /**
   * Promisified db.get
   */
  private dbGet<T>(sql: string, params: any[] = []): Promise<T | undefined> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      this.db.get(sql, params, (err: Error | null, row: T) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  /**
   * Promisified db.all
   */
  private dbAll<T>(sql: string, params: any[] = []): Promise<T[]> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      this.db.all(sql, params, (err: Error | null, rows: T[]) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  /**
   * Get the auth client
   */
  getAuthClient(): SlackAuthClient {
    return this.auth;
  }

  /**
   * Check if connected to Slack
   */
  async isConnected(): Promise<boolean> {
    return await this.auth.isConnected();
  }

  /**
   * Send a message to a channel
   */
  async sendMessage(options: MessageOptions): Promise<MessageResponse> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }

    const response = await fetch('https://slack.com/api/chat.postMessage', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        channel: options.channel,
        text: options.text,
        blocks: options.blocks,
        attachments: options.attachments,
        thread_ts: options.threadTs,
        unfurl_links: options.unfurlLinks,
        unfurl_media: options.unfurlMedia,
        mrkdwn: options.mrkdwn ?? true
      })
    });

    const result = await response.json() as MessageResponse;

    // Log sent message
    if (result.ok) {
      await this.initDb();
      await this.runWithResult(
        'INSERT INTO sent_messages (channel, text, ts, thread_ts) VALUES (?, ?, ?, ?)',
        [options.channel, options.text.substring(0, 1000), result.ts, options.threadTs || null]
      );
    }

    return result;
  }

  /**
   * Send a direct message to a user
   */
  async sendDirectMessage(userId: string, text: string, options?: Partial<MessageOptions>): Promise<MessageResponse> {
    return this.sendMessage({
      channel: userId,
      text,
      ...options
    });
  }

  /**
   * Reply to a thread
   */
  async replyInThread(channel: string, threadTs: string, text: string): Promise<MessageResponse> {
    return this.sendMessage({
      channel,
      text,
      threadTs
    });
  }

  /**
   * Upload a file to Slack
   */
  async uploadFile(options: FileUploadOptions): Promise<MessageResponse> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }

    const formData = new FormData();
    formData.append('channels', options.channels);
    formData.append('filename', options.filename || 'file');
    if (options.title) formData.append('title', options.title);
    if (options.initialComment) formData.append('initial_comment', options.initialComment);
    if (options.threadTs) formData.append('thread_ts', options.threadTs);

    if (options.file && fs.existsSync(options.file)) {
      const fileContent = fs.readFileSync(options.file);
      const blob = new Blob([fileContent]);
      formData.append('file', blob, path.basename(options.file));
    } else if (options.content) {
      const blob = new Blob([options.content]);
      formData.append('file', blob, options.filename || 'file.txt');
    } else {
      return { ok: false, error: 'no_file_or_content' };
    }

    const response = await fetch('https://slack.com/api/files.upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    return await response.json() as MessageResponse;
  }

  /**
   * Create a new channel
   */
  async createChannel(options: CreateChannelOptions): Promise<MessageResponse> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }

    const endpoint = options.isPrivate 
      ? 'https://slack.com/api/conversations.create'
      : 'https://slack.com/api/channels.create';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: options.name.replace(/^#/, ''),
        is_private: options.isPrivate
      })
    });

    const result = await response.json() as MessageResponse;

    // Set description if provided
    if (result.ok && options.description) {
      const channelId = (result as any).channel?.id;
      if (channelId) {
        await fetch('https://slack.com/api/conversations.setPurpose', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            channel: channelId,
            purpose: options.description
          })
        });
      }
    }

    return result;
  }

  /**
   * Get or create a channel (creates if it doesn't exist)
   */
  async getOrCreateChannel(name: string, isPrivate: boolean = false): Promise<ChannelInfo | null> {
    // First try to find the channel
    const channels = await this.listChannels();
    const normalizedName = name.replace(/^#/, '').toLowerCase();
    const existing = channels.find(c => c.name.toLowerCase() === normalizedName);

    if (existing) {
      return existing;
    }

    // Create if not found
    const result = await this.createChannel({ name: normalizedName, isPrivate });
    if (result.ok && (result as any).channel) {
      const channel = (result as any).channel;
      return {
        id: channel.id,
        name: channel.name,
        isPrivate: channel.is_private ?? isPrivate,
        numMembers: channel.num_members ?? 0,
        topic: channel.topic?.value,
        purpose: channel.purpose?.value,
        created: channel.created,
        creator: channel.creator
      };
    }

    return null;
  }

  /**
   * List all channels
   */
  async listChannels(types: string = 'public_channel,private_channel'): Promise<ChannelInfo[]> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return [];
    }

    const response = await fetch(`https://slack.com/api/conversations.list?types=${types}&limit=1000`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const result = await response.json() as any;

    if (!result.ok) {
      return [];
    }

    return result.channels.map((c: any) => ({
      id: c.id,
      name: c.name,
      isPrivate: c.is_private,
      numMembers: c.num_members || 0,
      topic: c.topic?.value,
      purpose: c.purpose?.value,
      created: c.created,
      creator: c.creator
    }));
  }

  /**
   * Get user info
   */
  async getUserInfo(userId: string): Promise<UserInfo | null> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return null;
    }

    const response = await fetch(`https://slack.com/api/users.info?user=${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const result = await response.json() as any;

    if (!result.ok || !result.user) {
      return null;
    }

    const user = result.user;
    return {
      id: user.id,
      name: user.name,
      realName: user.real_name,
      email: user.profile?.email,
      isAdmin: user.is_admin || false,
      isBot: user.is_bot || false,
      avatar: user.profile?.image_48
    };
  }

  /**
   * Find user by email
   */
  async findUserByEmail(email: string): Promise<UserInfo | null> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return null;
    }

    const response = await fetch(`https://slack.com/api/users.lookupByEmail?email=${encodeURIComponent(email)}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const result = await response.json() as any;

    if (!result.ok || !result.user) {
      return null;
    }

    const user = result.user;
    return {
      id: user.id,
      name: user.name,
      realName: user.real_name,
      email: user.profile?.email,
      isAdmin: user.is_admin || false,
      isBot: user.is_bot || false,
      avatar: user.profile?.image_48
    };
  }

  /**
   * List users in workspace
   */
  async listUsers(includeBots: boolean = false): Promise<UserInfo[]> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return [];
    }

    const response = await fetch('https://slack.com/api/users.list?limit=1000', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const result = await response.json() as any;

    if (!result.ok || !result.members) {
      return [];
    }

    return result.members
      .filter((u: any) => includeBots || !u.is_bot)
      .filter((u: any) => !u.deleted)
      .map((u: any) => ({
        id: u.id,
        name: u.name,
        realName: u.real_name,
        email: u.profile?.email,
        isAdmin: u.is_admin || false,
        isBot: u.is_bot || false,
        avatar: u.profile?.image_48
      }));
  }

  /**
   * Invite bot to a channel
   */
  async joinChannel(channel: string): Promise<MessageResponse> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }

    const response = await fetch('https://slack.com/api/conversations.join', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ channel })
    });

    return await response.json() as MessageResponse;
  }

  /**
   * Leave a channel
   */
  async leaveChannel(channel: string): Promise<MessageResponse> {
    const token = await this.auth.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }

    const response = await fetch('https://slack.com/api/conversations.leave', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ channel })
    });

    return await response.json() as MessageResponse;
  }

  /**
   * Send a notification using a template
   */
  async sendNotification(templateName: string, variables?: Record<string, string>, targetChannel?: string): Promise<MessageResponse> {
    await this.initDb();

    const template = await this.dbGet<{
      id: number;
      name: string;
      channel: string | null;
      text: string;
      blocks: string | null;
      attachments: string | null;
    }>(
      'SELECT * FROM templates WHERE name = ?',
      [templateName]
    );

    if (!template) {
      return { ok: false, error: 'template_not_found' };
    }

    let text = template.text;
    let blocks: object[] | undefined = template.blocks ? JSON.parse(template.blocks) : undefined;

    // Replace variables
    if (variables) {
      for (const [key, value] of Object.entries(variables)) {
        const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
        text = text.replace(regex, value);
        if (blocks) {
          const blocksStr = JSON.stringify(blocks).replace(regex, value);
          blocks = JSON.parse(blocksStr);
        }
      }
    }

    const result = await this.sendMessage({
      channel: targetChannel || template.channel || '#general',
      text,
      blocks,
      attachments: template.attachments ? JSON.parse(template.attachments) : undefined
    });

    // Log template usage
    if (result.ok) {
      await this.runWithResult(
        'UPDATE templates SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [template.id]
      );
    }

    return result;
  }

  /**
   * Create a notification template
   */
  async createTemplate(template: NotificationTemplate): Promise<void> {
    await this.initDb();

    await this.runWithResult(
      `INSERT OR REPLACE INTO templates (name, channel, text, blocks, attachments, updated_at)
       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)`,
      [
        template.name,
        template.channel,
        template.text,
        template.blocks ? JSON.stringify(template.blocks) : null,
        template.attachments ? JSON.stringify(template.attachments) : null
      ]
    );
  }

  /**
   * Get a template by name
   */
  async getTemplate(name: string): Promise<NotificationTemplate | null> {
    await this.initDb();

    const template = await this.dbGet<{
      id: number;
      name: string;
      channel: string | null;
      text: string;
      blocks: string | null;
      attachments: string | null;
      created_at: string;
      updated_at: string;
    }>(
      'SELECT * FROM templates WHERE name = ?',
      [name]
    );

    if (template) {
      return {
        id: template.id,
        name: template.name,
        channel: template.channel || undefined,
        text: template.text,
        blocks: template.blocks ? JSON.parse(template.blocks) : undefined,
        attachments: template.attachments ? JSON.parse(template.attachments) : undefined,
        createdAt: template.created_at,
        updatedAt: template.updated_at
      };
    }

    return null;
  }

  /**
   * List all templates
   */
  async listTemplates(): Promise<NotificationTemplate[]> {
    await this.initDb();

    const templates = await this.dbAll<{
      id: number;
      name: string;
      channel: string | null;
      text: string;
      blocks: string | null;
      attachments: string | null;
      created_at: string;
      updated_at: string;
    }>('SELECT * FROM templates ORDER BY name');

    return templates.map(t => ({
      id: t.id,
      name: t.name,
      channel: t.channel || undefined,
      text: t.text,
      blocks: t.blocks ? JSON.parse(t.blocks) : undefined,
      attachments: t.attachments ? JSON.parse(t.attachments) : undefined,
      createdAt: t.created_at,
      updatedAt: t.updated_at
    }));
  }

  /**
   * Delete a template
   */
  async deleteTemplate(name: string): Promise<void> {
    await this.initDb();
    await this.runWithResult('DELETE FROM templates WHERE name = ?', [name]);
  }

  /**
   * Get message history
   */
  async getMessageHistory(limit: number = 50): Promise<any[]> {
    await this.initDb();

    return await this.dbAll(
      'SELECT * FROM sent_messages ORDER BY created_at DESC LIMIT ?',
      [limit]
    );
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; message: string }> {
    const connected = await this.isConnected();
    if (!connected) {
      return { status: 'unhealthy', message: 'Not authenticated' };
    }

    try {
      const channels = await this.listChannels('public_channel');
      return { 
        status: 'healthy', 
        message: `Connected. Can access ${channels.length} channels.` 
      };
    } catch (error: any) {
      return { status: 'unhealthy', message: error.message };
    }
  }

  /**
   * Close connections
   */
  async close(): Promise<void> {
    // Wait for init to complete before closing
    if (this.initPromise) {
      try {
        await this.initPromise;
      } catch (e) {
        // Ignore init errors during close
      }
    }
    if (this.db) {
      await new Promise<void>((resolve) => {
        this.db!.close(() => resolve());
      });
      this.db = null;
    }
  }
}

export default SlackSkill;
