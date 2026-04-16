import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';

// Types
export type ResponseTone = 'professional' | 'empathetic' | 'technical' | 'casual' | 'apologetic' | 'confident';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TicketStatus = 'open' | 'pending' | 'solved' | 'closed';

export interface Ticket {
  id: string;
  subject: string;
  description: string;
  priority?: TicketPriority;
  status?: TicketStatus;
  requesterName?: string;
  tags?: string[];
  createdAt?: Date;
}

export interface KnowledgeBaseArticle {
  id: string;
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  url?: string;
}

export interface DraftOptions {
  tone?: ResponseTone;
  count?: number;
  includeKBArticles?: boolean;
  maxLength?: number;
  ticketHistory?: string[];
}

export interface ResponseDraft {
  id?: number;
  ticketId: string;
  content: string;
  tone: ResponseTone;
  kbArticles?: KnowledgeBaseArticle[];
  confidence: number;
  createdAt: Date;
  wasSent: boolean;
}

export interface ResponseTemplate {
  id?: number;
  name: string;
  category: string;
  content: string;
  tone: ResponseTone;
  tags?: string[];
  variables?: string[];
}

export interface DraftStats {
  totalDrafts: number;
  sentDrafts: number;
  draftsByTone: Record<ResponseTone, number>;
  averageConfidence: number;
}

// Utility functions
function runWithResult(db: sqlite3.Database, sql: string, params: any[] = []): Promise<{ lastID: number; changes: number }> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(this: sqlite3.RunResult, err: Error | null) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function getDbPath(): string {
  const homeDir = os.homedir();
  const baseDir = path.join(homeDir, '.openclaw', 'skills', 'response-drafts');
  
  if (!fs.existsSync(baseDir)) {
    fs.mkdirSync(baseDir, { recursive: true });
  }
  
  return path.join(baseDir, 'drafts.db');
}

// Default templates
const DEFAULT_TEMPLATES: Omit<ResponseTemplate, 'id'>[] = [
  {
    name: 'acknowledgment',
    category: 'general',
    content: 'Hi {{requesterName}},\n\nThank you for reaching out to us. I understand your concern about {{subject}}.\n\nI\'m looking into this for you and will get back to you shortly.\n\nBest regards,\n{{agentName}}',
    tone: 'professional',
    tags: ['acknowledgment', 'initial-response'],
    variables: ['requesterName', 'subject', 'agentName']
  },
  {
    name: 'solution-provided',
    category: 'resolution',
    content: 'Hi {{requesterName}},\n\nGreat news! I\'ve resolved the issue with {{subject}}.\n\n{{solution}}\n\nPlease let me know if you need any further assistance.\n\nBest regards,\n{{agentName}}',
    tone: 'confident',
    tags: ['solution', 'resolution'],
    variables: ['requesterName', 'subject', 'solution', 'agentName']
  },
  {
    name: 'escalation',
    category: 'escalation',
    content: 'Hi {{requesterName}},\n\nThank you for your patience regarding {{subject}}.\n\nI\'ve escalated this to our specialized team who will be better equipped to help. You can expect to hear from them within {{timeframe}}.\n\nReference: {{ticketId}}\n\nBest regards,\n{{agentName}}',
    tone: 'empathetic',
    tags: ['escalation', 'specialist'],
    variables: ['requesterName', 'subject', 'timeframe', 'ticketId', 'agentName']
  },
  {
    name: 'need-more-info',
    category: 'follow-up',
    content: 'Hi {{requesterName}},\n\nTo help you better with {{subject}}, could you please provide:\n\n{{questions}}\n\nOnce I have this information, I\'ll be able to assist you further.\n\nBest regards,\n{{agentName}}',
    tone: 'professional',
    tags: ['follow-up', 'information-request'],
    variables: ['requesterName', 'subject', 'questions', 'agentName']
  },
  {
    name: 'apology',
    category: 'general',
    content: 'Hi {{requesterName}},\n\nI sincerely apologize for the inconvenience you\'ve experienced with {{subject}}.\n\n{{resolution}}\n\nWe appreciate your patience and understanding.\n\nBest regards,\n{{agentName}}',
    tone: 'apologetic',
    tags: ['apology', 'service-recovery'],
    variables: ['requesterName', 'subject', 'resolution', 'agentName']
  }
];

// Default KB articles
const DEFAULT_KB_ARTICLES: KnowledgeBaseArticle[] = [
  {
    id: 'kb-001',
    title: 'Account Password Reset',
    content: 'To reset your password, go to Settings > Security > Change Password.',
    category: 'account',
    tags: ['password', 'reset', 'account', 'login']
  },
  {
    id: 'kb-002',
    title: 'Payment Failed Troubleshooting',
    content: 'Check your card details, expiration date, and ensure sufficient funds.',
    category: 'billing',
    tags: ['payment', 'billing', 'failed', 'card']
  },
  {
    id: 'kb-003',
    title: 'Feature Not Working',
    content: 'Try clearing your browser cache, disabling extensions, or using incognito mode.',
    category: 'technical',
    tags: ['bug', 'feature', 'not-working', 'troubleshooting']
  }
];

export class ResponseDraftsSkill {
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;
  private dataDir: string;

  constructor() {
    this.dataDir = path.join(os.homedir(), '.openclaw', 'skills', 'response-drafts');
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
    this.initPromise = this.initialize();
  }

  private async initialize(): Promise<void> {
    const dbPath = getDbPath();
    
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(dbPath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        this.createTables().then(() => resolve()).catch(reject);
      });
    });
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const tables = [
      `CREATE TABLE IF NOT EXISTS response_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT NOT NULL,
        content TEXT NOT NULL,
        tone TEXT NOT NULL,
        kb_articles TEXT,
        confidence REAL DEFAULT 0.8,
        created_at TEXT NOT NULL,
        was_sent INTEGER DEFAULT 0
      )`,
      `CREATE TABLE IF NOT EXISTS response_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        tone TEXT NOT NULL,
        tags TEXT,
        variables TEXT
      )`,
      `CREATE TABLE IF NOT EXISTS kb_articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        url TEXT
      )`,
      `CREATE TABLE IF NOT EXISTS kb_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        article_id TEXT NOT NULL,
        relevance_score REAL DEFAULT 1.0,
        FOREIGN KEY (article_id) REFERENCES kb_articles(id) ON DELETE CASCADE
      )`,
      `CREATE INDEX IF NOT EXISTS idx_drafts_ticket ON response_drafts(ticket_id)`,
      `CREATE INDEX IF NOT EXISTS idx_templates_category ON response_templates(category)`,
      `CREATE INDEX IF NOT EXISTS idx_kb_tags ON kb_articles(category)`
    ];

    for (const sql of tables) {
      await new Promise<void>((resolve, reject) => {
        this.db!.run(sql, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }

    // Seed default data
    await this.seedDefaultData();
  }

  private async seedDefaultData(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Check if templates exist
    const count = await new Promise<number>((resolve, reject) => {
      this.db!.get('SELECT COUNT(*) as count FROM response_templates', (err, row: any) => {
        if (err) reject(err);
        else resolve(row.count);
      });
    });

    if (count === 0) {
      // Seed templates
      for (const template of DEFAULT_TEMPLATES) {
        await runWithResult(this.db,
          `INSERT INTO response_templates (name, category, content, tone, tags, variables)
           VALUES (?, ?, ?, ?, ?, ?)`,
          [
            template.name,
            template.category,
            template.content,
            template.tone,
            JSON.stringify(template.tags),
            JSON.stringify(template.variables)
          ]
        );
      }

      // Seed KB articles
      for (const article of DEFAULT_KB_ARTICLES) {
        await runWithResult(this.db,
          `INSERT OR IGNORE INTO kb_articles (id, title, content, category, tags, url)
           VALUES (?, ?, ?, ?, ?, ?)`,
          [
            article.id,
            article.title,
            article.content,
            article.category,
            JSON.stringify(article.tags),
            article.url || null
          ]
        );

        // Create mappings from tags
        if (article.tags) {
          for (const tag of article.tags) {
            await runWithResult(this.db,
              `INSERT OR IGNORE INTO kb_mappings (keyword, article_id, relevance_score)
               VALUES (?, ?, ?)`,
              [tag.toLowerCase(), article.id, 1.0]
            );
          }
        }
      }
    }
  }

  private async ensureInitialized(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
      this.initPromise = null;
    }
  }

  // Generate response drafts for a ticket
  async generateDrafts(ticket: Ticket, options: DraftOptions = {}): Promise<ResponseDraft[]> {
    await this.ensureInitialized();
    
    const tone = options.tone || this.detectTone(ticket);
    const count = options.count || 3;
    const includeKB = options.includeKBArticles !== false;

    // Find relevant KB articles
    let kbArticles: KnowledgeBaseArticle[] = [];
    if (includeKB) {
      kbArticles = await this.findRelevantKBArticles(ticket);
    }

    // Generate different types of drafts
    const drafts: ResponseDraft[] = [];
    const templates = await this.getTemplatesForTone(tone);

    // Draft 1: Template-based
    if (templates.length > 0) {
      const template = templates[0];
      const content = this.generateFromTemplate(template, ticket, kbArticles);
      drafts.push({
        ticketId: ticket.id,
        content,
        tone,
        kbArticles: kbArticles.slice(0, 2),
        confidence: kbArticles.length > 0 ? 0.85 : 0.7,
        createdAt: new Date(),
        wasSent: false
      });
    }

    // Draft 2: AI-style response (simulated)
    drafts.push({
      ticketId: ticket.id,
      content: this.generateAIResponse(ticket, tone, kbArticles),
      tone,
      kbArticles: kbArticles.slice(0, 2),
      confidence: 0.75,
      createdAt: new Date(),
      wasSent: false
    });

    // Draft 3: Alternative tone or shorter version
    if (count > 2) {
      const altTone = this.getAlternativeTone(tone);
      drafts.push({
        ticketId: ticket.id,
        content: this.generateAIResponse(ticket, altTone, kbArticles, true),
        tone: altTone,
        kbArticles: kbArticles.slice(0, 1),
        confidence: 0.7,
        createdAt: new Date(),
        wasSent: false
      });
    }

    // Save drafts to database
    for (const draft of drafts) {
      const result = await runWithResult(this.db!,
        `INSERT INTO response_drafts (ticket_id, content, tone, kb_articles, confidence, created_at, was_sent)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          draft.ticketId,
          draft.content,
          draft.tone,
          JSON.stringify(draft.kbArticles || []),
          draft.confidence,
          draft.createdAt.toISOString(),
          0
        ]
      );
      draft.id = result.lastID;
    }

    return drafts;
  }

  // Detect appropriate tone based on ticket content
  private detectTone(ticket: Ticket): ResponseTone {
    const text = (ticket.subject + ' ' + ticket.description).toLowerCase();
    const priority = ticket.priority || 'medium';

    if (priority === 'urgent' || text.includes('urgent') || text.includes('critical') || text.includes('down')) {
      return 'empathetic';
    }
    if (text.includes('error') || text.includes('bug') || text.includes('not working')) {
      return 'technical';
    }
    if (text.includes('frustrated') || text.includes('disappointed') || text.includes('unacceptable')) {
      return 'apologetic';
    }
    if (text.includes('thank') || text.includes('great') || text.includes('love')) {
      return 'casual';
    }
    return 'professional';
  }

  // Get alternative tone
  private getAlternativeTone(currentTone: ResponseTone): ResponseTone {
    const alternatives: Record<ResponseTone, ResponseTone> = {
      'professional': 'casual',
      'casual': 'professional',
      'empathetic': 'apologetic',
      'apologetic': 'empathetic',
      'technical': 'professional',
      'confident': 'professional'
    };
    return alternatives[currentTone] || 'professional';
  }

  // Find relevant KB articles for a ticket
  private async findRelevantKBArticles(ticket: Ticket): Promise<KnowledgeBaseArticle[]> {
    await this.ensureInitialized();
    
    const text = (ticket.subject + ' ' + ticket.description).toLowerCase();
    const keywords = text.split(/\s+/).filter(w => w.length > 3);
    
    if (keywords.length === 0) return [];

    const placeholders = keywords.map(() => '?').join(',');
    
    interface ArticleRow {
      id: string;
      title: string;
      content: string;
      category: string | null;
      tags: string | null;
      url: string | null;
      relevance: number;
    }

    const rows = await new Promise<ArticleRow[]>((resolve, reject) => {
      this.db!.all<ArticleRow>(
        `SELECT a.*, AVG(m.relevance_score) as relevance
         FROM kb_articles a
         JOIN kb_mappings m ON a.id = m.article_id
         WHERE m.keyword IN (${placeholders})
         GROUP BY a.id
         ORDER BY relevance DESC
         LIMIT 3`,
        keywords,
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows || []);
        }
      );
    });

    return rows.map(row => ({
      id: row.id,
      title: row.title,
      content: row.content,
      category: row.category || undefined,
      tags: row.tags ? JSON.parse(row.tags) : [],
      url: row.url || undefined
    }));
  }

  // Get templates for a specific tone
  private async getTemplatesForTone(tone: ResponseTone): Promise<ResponseTemplate[]> {
    await this.ensureInitialized();

    interface TemplateRow {
      id: number;
      name: string;
      category: string;
      content: string;
      tone: string;
      tags: string | null;
      variables: string | null;
    }

    const rows = await new Promise<TemplateRow[]>((resolve, reject) => {
      this.db!.all<TemplateRow>(
        `SELECT * FROM response_templates 
         WHERE tone = ? OR tone = 'professional'
         ORDER BY CASE WHEN tone = ? THEN 0 ELSE 1 END
         LIMIT 5`,
        [tone, tone],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows || []);
        }
      );
    });

    return rows.map(row => ({
      id: row.id,
      name: row.name,
      category: row.category,
      content: row.content,
      tone: row.tone as ResponseTone,
      tags: row.tags ? JSON.parse(row.tags) : [],
      variables: row.variables ? JSON.parse(row.variables) : []
    }));
  }

  // Generate content from template
  private generateFromTemplate(template: ResponseTemplate, ticket: Ticket, kbArticles: KnowledgeBaseArticle[]): string {
    let content = template.content;
    
    // Replace basic variables
    content = content.replace(/{{requesterName}}/g, ticket.requesterName || 'there');
    content = content.replace(/{{subject}}/g, ticket.subject);
    content = content.replace(/{{ticketId}}/g, ticket.id);
    content = content.replace(/{{agentName}}/g, 'Support Team');

    // Add KB article content if relevant
    if (kbArticles.length > 0 && content.includes('{{solution}}')) {
      const solution = `Here's what you can do:\n\n${kbArticles[0].title}\n${kbArticles[0].content}`;
      content = content.replace(/{{solution}}/g, solution);
    } else {
      content = content.replace(/{{solution}}/g, 'We\'re working on a solution for you.');
    }

    if (content.includes('{{questions}}')) {
      content = content.replace(/{{questions}}/g, '1. When did this issue first occur?\n2. Have you tried any troubleshooting steps?\n3. What browser/device are you using?');
    }

    if (content.includes('{{timeframe}}')) {
      content = content.replace(/{{timeframe}}/g, '24 hours');
    }

    return content;
  }

  // Generate AI-style response (simulated)
  private generateAIResponse(ticket: Ticket, tone: ResponseTone, kbArticles: KnowledgeBaseArticle[], isShort: boolean = false): string {
    const toneModifiers: Record<ResponseTone, string> = {
      'professional': 'Thank you for contacting support.',
      'empathetic': 'I understand how frustrating this must be for you.',
      'technical': 'I\'ve analyzed the technical details of your issue.',
      'casual': 'Hey! Thanks for reaching out.',
      'apologetic': 'I sincerely apologize for the inconvenience this has caused.',
      'confident': 'I can definitely help you resolve this issue.'
    };

    let response = `${toneModifiers[tone]}\n\n`;
    
    if (isShort) {
      response += `Regarding "${ticket.subject}", `;
      if (kbArticles.length > 0) {
        response += `please refer to our guide: "${kbArticles[0].title}". `;
      }
      response += `Let me know if you need anything else!`;
    } else {
      response += `I've reviewed your inquiry about "${ticket.subject}".\n\n`;
      
      if (kbArticles.length > 0) {
        response += `Based on your description, this article may help:\n`;
        response += `📖 ${kbArticles[0].title}\n`;
        response += `${kbArticles[0].content}\n\n`;
      }

      response += `If this doesn't resolve your issue, please reply with:\n`;
      response += `- Any error messages you're seeing\n`;
      response += `- Steps you've already tried\n`;
      response += `- Your account email (if different)\n\n`;
      response += `We're here to help!`;
    }

    return response;
  }

  // Get all templates
  async getTemplates(category?: string): Promise<ResponseTemplate[]> {
    await this.ensureInitialized();

    let sql = 'SELECT * FROM response_templates';
    const params: any[] = [];
    
    if (category) {
      sql += ' WHERE category = ?';
      params.push(category);
    }
    
    sql += ' ORDER BY category, name';

    interface TemplateRow {
      id: number;
      name: string;
      category: string;
      content: string;
      tone: string;
      tags: string | null;
      variables: string | null;
    }

    const rows = await new Promise<TemplateRow[]>((resolve, reject) => {
      this.db!.all<TemplateRow>(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows || []);
      });
    });

    return rows.map(row => ({
      id: row.id,
      name: row.name,
      category: row.category,
      content: row.content,
      tone: row.tone as ResponseTone,
      tags: row.tags ? JSON.parse(row.tags) : [],
      variables: row.variables ? JSON.parse(row.variables) : []
    }));
  }

  // Get a specific template
  async getTemplate(name: string): Promise<ResponseTemplate | null> {
    await this.ensureInitialized();

    interface TemplateRow {
      id: number;
      name: string;
      category: string;
      content: string;
      tone: string;
      tags: string | null;
      variables: string | null;
    }

    const row = await new Promise<TemplateRow | undefined>((resolve, reject) => {
      this.db!.get<TemplateRow>(
        'SELECT * FROM response_templates WHERE name = ?',
        [name],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });

    if (!row) return null;

    return {
      id: row.id,
      name: row.name,
      category: row.category,
      content: row.content,
      tone: row.tone as ResponseTone,
      tags: row.tags ? JSON.parse(row.tags) : [],
      variables: row.variables ? JSON.parse(row.variables) : []
    };
  }

  // Add custom template
  async addTemplate(template: Omit<ResponseTemplate, 'id'>): Promise<ResponseTemplate> {
    await this.ensureInitialized();

    const result = await runWithResult(this.db!,
      `INSERT INTO response_templates (name, category, content, tone, tags, variables)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [
        template.name,
        template.category,
        template.content,
        template.tone,
        JSON.stringify(template.tags || []),
        JSON.stringify(template.variables || [])
      ]
    );

    return {
      id: result.lastID,
      ...template
    };
  }

  // Apply template with variables
  applyTemplate(template: ResponseTemplate, variables: Record<string, string>): string {
    let content = template.content;
    
    for (const [key, value] of Object.entries(variables)) {
      const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
      content = content.replace(regex, value);
    }

    return content;
  }

  // Get drafts for a ticket
  async getDraftsForTicket(ticketId: string): Promise<ResponseDraft[]> {
    await this.ensureInitialized();

    interface DraftRow {
      id: number;
      ticket_id: string;
      content: string;
      tone: string;
      kb_articles: string | null;
      confidence: number;
      created_at: string;
      was_sent: number;
    }

    const rows = await new Promise<DraftRow[]>((resolve, reject) => {
      this.db!.all<DraftRow>(
        'SELECT * FROM response_drafts WHERE ticket_id = ? ORDER BY created_at DESC',
        [ticketId],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows || []);
        }
      );
    });

    return rows.map(row => ({
      id: row.id,
      ticketId: row.ticket_id,
      content: row.content,
      tone: row.tone as ResponseTone,
      kbArticles: row.kb_articles ? JSON.parse(row.kb_articles) : [],
      confidence: row.confidence,
      createdAt: new Date(row.created_at),
      wasSent: row.was_sent === 1
    }));
  }

  // Get all drafts
  async getAllDrafts(limit: number = 50): Promise<ResponseDraft[]> {
    await this.ensureInitialized();

    interface DraftRow {
      id: number;
      ticket_id: string;
      content: string;
      tone: string;
      kb_articles: string | null;
      confidence: number;
      created_at: string;
      was_sent: number;
    }

    const rows = await new Promise<DraftRow[]>((resolve, reject) => {
      this.db!.all<DraftRow>(
        'SELECT * FROM response_drafts ORDER BY created_at DESC LIMIT ?',
        [limit],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows || []);
        }
      );
    });

    return rows.map(row => ({
      id: row.id,
      ticketId: row.ticket_id,
      content: row.content,
      tone: row.tone as ResponseTone,
      kbArticles: row.kb_articles ? JSON.parse(row.kb_articles) : [],
      confidence: row.confidence,
      createdAt: new Date(row.created_at),
      wasSent: row.was_sent === 1
    }));
  }

  // Mark draft as sent
  async markDraftAsSent(draftId: number): Promise<void> {
    await this.ensureInitialized();

    await new Promise<void>((resolve, reject) => {
      this.db!.run(
        'UPDATE response_drafts SET was_sent = 1 WHERE id = ?',
        [draftId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  // Get statistics
  async getStats(): Promise<DraftStats> {
    await this.ensureInitialized();

    interface CountRow {
      total: number;
      sent: number;
    }

    const counts = await new Promise<CountRow>((resolve, reject) => {
      this.db!.get<CountRow>(
        `SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN was_sent = 1 THEN 1 ELSE 0 END) as sent
         FROM response_drafts`,
        (err, row: any) => {
          if (err) reject(err);
          else resolve(row || { total: 0, sent: 0 });
        }
      );
    });

    interface ToneRow {
      tone: string;
      count: number;
    }

    const toneRows = await new Promise<ToneRow[]>((resolve, reject) => {
      this.db!.all<ToneRow>(
        `SELECT tone, COUNT(*) as count 
         FROM response_drafts 
         GROUP BY tone`,
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows || []);
        }
      );
    });

    const draftsByTone: Record<ResponseTone, number> = {
      professional: 0,
      empathetic: 0,
      technical: 0,
      casual: 0,
      apologetic: 0,
      confident: 0
    };

    for (const row of toneRows) {
      if (row.tone in draftsByTone) {
        draftsByTone[row.tone as ResponseTone] = row.count;
      }
    }

    const avgConf = await new Promise<{ avg: number }>((resolve, reject) => {
      this.db!.get(
        'SELECT AVG(confidence) as avg FROM response_drafts',
        (err, row: any) => {
          if (err) reject(err);
          else resolve(row || { avg: 0 });
        }
      );
    });

    return {
      totalDrafts: counts.total,
      sentDrafts: counts.sent,
      draftsByTone,
      averageConfidence: avgConf.avg || 0
    };
  }

  // Add KB article
  async addKBArticle(article: KnowledgeBaseArticle): Promise<void> {
    await this.ensureInitialized();

    await runWithResult(this.db!,
      `INSERT OR REPLACE INTO kb_articles (id, title, content, category, tags, url)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [
        article.id,
        article.title,
        article.content,
        article.category || null,
        JSON.stringify(article.tags || []),
        article.url || null
      ]
    );

    // Add mappings
    if (article.tags) {
      for (const tag of article.tags) {
        await runWithResult(this.db!,
          `INSERT OR IGNORE INTO kb_mappings (keyword, article_id, relevance_score)
           VALUES (?, ?, ?)`,
          [tag.toLowerCase(), article.id, 1.0]
        );
      }
    }

    // Add title words as mappings
    const titleWords = article.title.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    for (const word of titleWords) {
      await runWithResult(this.db!,
        `INSERT OR IGNORE INTO kb_mappings (keyword, article_id, relevance_score)
         VALUES (?, ?, ?)`,
        [word, article.id, 0.8]
      );
    }
  }

  // Get all KB articles
  async getKBArticles(category?: string): Promise<KnowledgeBaseArticle[]> {
    await this.ensureInitialized();

    let sql = 'SELECT * FROM kb_articles';
    const params: any[] = [];
    
    if (category) {
      sql += ' WHERE category = ?';
      params.push(category);
    }
    
    sql += ' ORDER BY title';

    interface ArticleRow {
      id: string;
      title: string;
      content: string;
      category: string | null;
      tags: string | null;
      url: string | null;
    }

    const rows = await new Promise<ArticleRow[]>((resolve, reject) => {
      this.db!.all<ArticleRow>(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows || []);
      });
    });

    return rows.map(row => ({
      id: row.id,
      title: row.title,
      content: row.content,
      category: row.category || undefined,
      tags: row.tags ? JSON.parse(row.tags) : [],
      url: row.url || undefined
    }));
  }

  // Health check
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; message: string }> {
    try {
      await this.ensureInitialized();
      
      const templateCount = await new Promise<number>((resolve, reject) => {
        this.db!.get('SELECT COUNT(*) as count FROM response_templates', (err, row: any) => {
          if (err) reject(err);
          else resolve(row.count);
        });
      });

      const kbCount = await new Promise<number>((resolve, reject) => {
        this.db!.get('SELECT COUNT(*) as count FROM kb_articles', (err, row: any) => {
          if (err) reject(err);
          else resolve(row.count);
        });
      });

      return {
        status: 'healthy',
        message: `Ready - ${templateCount} templates, ${kbCount} KB articles`
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: `Error: ${(error as Error).message}`
      };
    }
  }

  // Close database connection
  async close(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise.catch(() => {});
    }

    if (this.db) {
      await new Promise<void>((resolve, reject) => {
        this.db!.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      });
      this.db = null;
    }
  }
}

export default ResponseDraftsSkill;
