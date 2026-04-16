import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';

// Ticket types
export interface Ticket {
  id: string;
  subject: string;
  body: string;
  from: string;
  createdAt: Date;
  tags?: string[];
}

export type TicketCategory = 
  | 'bug' 
  | 'feature_request' 
  | 'question' 
  | 'complaint' 
  | 'billing' 
  | 'technical' 
  | 'account' 
  | 'other';

export type TicketPriority = 'critical' | 'high' | 'medium' | 'low';

export interface TicketClassification {
  id?: number;
  ticketId: string;
  category: TicketCategory;
  priority: TicketPriority;
  priorityScore: number;
  confidence: number;
  reasons: string[];
  assignedTo?: string;
  isSpam: boolean;
  spamScore: number;
  classifiedAt: Date;
  reviewed: boolean;
}

export interface TriageResult {
  ticket: Ticket;
  classification: TicketClassification;
}

export interface ClassificationStats {
  totalClassified: number;
  byCategory: Record<TicketCategory, number>;
  byPriority: Record<TicketPriority, number>;
  byAssignment: Record<string, number>;
  spamCount: number;
  unreviewed: number;
}

// Database record interfaces (snake_case)
interface ClassificationRecord {
  id?: number;
  ticket_id: string;
  category: string;
  priority: string;
  priority_score: number;
  confidence: number;
  reasons: string;
  assigned_to?: string;
  is_spam: number;
  spam_score: number;
  classified_at: string;
  reviewed: number;
}

interface ClassificationRuleRecord {
  id?: number;
  pattern: string;
  pattern_type: string;
  category: string;
  priority: string;
  assigned_to?: string;
  auto_spam: number;
  created_at: string;
}

interface AssignmentRuleRecord {
  id?: number;
  category: string;
  team: string;
  workload: number;
  active: number;
  created_at: string;
}

// Helper for SQLite run with result
function runWithResult(db: sqlite3.Database, sql: string, params: any[] = []): Promise<{ lastID: number; changes: number }> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(this: sqlite3.RunResult, err: Error | null) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

export class TicketTriageSkill {
  private db: sqlite3.Database | null = null;
  private dbPath: string;
  private profile: string;
  private initPromise: Promise<void> | null = null;

  constructor(profile: string = 'default') {
    this.profile = profile;
    const skillDir = path.join(os.homedir(), '.openclaw', 'skills', 'ticket-triage');
    if (!fs.existsSync(skillDir)) {
      fs.mkdirSync(skillDir, { recursive: true });
    }
    this.dbPath = path.join(skillDir, `${profile}.db`);
  }

  static forProfile(profile: string): TicketTriageSkill {
    return new TicketTriageSkill(profile);
  }

  private async initDatabase(): Promise<void> {
    if (this.db) return;
    if (this.initPromise) return this.initPromise;

    this.initPromise = new Promise((resolve, reject) => {
      this.db = new (sqlite3 as any).Database(this.dbPath, async (err: Error | null) => {
        if (err) {
          reject(err);
          return;
        }
        try {
          await this.createTables();
          await this.seedDefaultAssignmentRules();
          resolve();
        } catch (error) {
          reject(error);
        }
      });
    });

    return this.initPromise;
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const schema = `
      CREATE TABLE IF NOT EXISTS classifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        priority_score REAL NOT NULL,
        confidence REAL NOT NULL,
        reasons TEXT NOT NULL,
        assigned_to TEXT,
        is_spam INTEGER DEFAULT 0,
        spam_score REAL DEFAULT 0,
        classified_at TEXT NOT NULL,
        reviewed INTEGER DEFAULT 0
      );

      CREATE INDEX IF NOT EXISTS idx_classifications_category ON classifications(category);
      CREATE INDEX IF NOT EXISTS idx_classifications_priority ON classifications(priority);
      CREATE INDEX IF NOT EXISTS idx_classifications_assigned ON classifications(assigned_to);
      CREATE INDEX IF NOT EXISTS idx_classifications_spam ON classifications(is_spam);
      CREATE INDEX IF NOT EXISTS idx_classifications_reviewed ON classifications(reviewed);

      CREATE TABLE IF NOT EXISTS classification_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT NOT NULL,
        pattern_type TEXT DEFAULT 'keyword',
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        assigned_to TEXT,
        auto_spam INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
      );

      CREATE INDEX IF NOT EXISTS idx_rules_pattern ON classification_rules(pattern);

      CREATE TABLE IF NOT EXISTS assignment_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        team TEXT NOT NULL,
        workload INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
      );

      CREATE INDEX IF NOT EXISTS idx_assignment_category ON assignment_rules(category);

      CREATE TABLE IF NOT EXISTS classification_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT NOT NULL,
        action_type TEXT NOT NULL,
        previous_category TEXT,
        new_category TEXT,
        previous_priority TEXT,
        new_priority TEXT,
        performed_at TEXT NOT NULL
      );

      CREATE INDEX IF NOT EXISTS idx_history_ticket ON classification_history(ticket_id);
    `;

    await new Promise<void>((resolve, reject) => {
      this.db!.exec(schema, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  private async seedDefaultAssignmentRules(): Promise<void> {
    if (!this.db) return;

    const defaults = [
      { category: 'bug', team: 'engineering' },
      { category: 'technical', team: 'support-tier2' },
      { category: 'billing', team: 'billing-team' },
      { category: 'account', team: 'customer-success' },
      { category: 'feature_request', team: 'product-team' },
      { category: 'complaint', team: 'customer-success' },
      { category: 'question', team: 'support-tier1' },
      { category: 'other', team: 'support-tier1' }
    ];

    for (const rule of defaults) {
      await runWithResult(this.db, `
        INSERT OR IGNORE INTO assignment_rules (category, team, created_at)
        VALUES (?, ?, ?)
      `, [rule.category, rule.team, new Date().toISOString()]);
    }
  }

  // AI Classification algorithm
  private classifyTicket(ticket: Ticket): TicketClassification {
    const subjectLower = ticket.subject.toLowerCase();
    const bodyLower = ticket.body.toLowerCase();
    const fromLower = ticket.from.toLowerCase();
    const fullText = `${subjectLower} ${bodyLower}`;

    let category: TicketCategory = 'other';
    let priority: TicketPriority = 'medium';
    let score = 50;
    const reasons: string[] = [];
    let isSpam = false;
    let spamScore = 0;

    // Spam detection patterns
    const spamPatterns = [
      'viagra', 'cialis', 'lottery', 'winner', 'million dollars', 'prince',
      'inheritance', 'nigerian', 'bank transfer', 'click here', 'act now',
      'limited time', 'urgent!!!', 'congratulations you won', 'free money',
      'weight loss', 'work from home', 'make money fast', 'credit card debt'
    ];

    const spamMatches = spamPatterns.filter(p => fullText.includes(p));
    if (spamMatches.length > 0) {
      spamScore = Math.min(1.0, 0.3 + (spamMatches.length * 0.2));
      if (spamScore > 0.7) {
        isSpam = true;
        reasons.push(`Spam detected: ${spamMatches.length} spam indicators`);
      }
    }

    // Category detection patterns
    const categoryPatterns: Record<TicketCategory, string[]> = {
      bug: ['bug', 'error', 'crash', 'not working', 'broken', 'failed', 'exception', 'stack trace', 'bug report'],
      feature_request: ['feature', 'enhancement', 'suggestion', 'would be nice', 'add support', 'implement', 'request'],
      question: ['how do i', 'how to', 'what is', 'help with', 'question', 'confused', 'don\'t understand', 'clarification'],
      complaint: ['complaint', 'unhappy', 'disappointed', 'terrible', 'awful', 'worst', 'cancel subscription', 'refund', 'terrible service'],
      billing: ['bill', 'payment', 'charge', 'invoice', 'subscription', 'price', 'cost', 'refund', 'billing', 'credit card', 'charged'],
      technical: ['api', 'integration', 'endpoint', 'webhook', 'sdk', 'code', 'developer', 'technical', 'implementation'],
      account: ['login', 'password', 'reset', 'account', 'access', 'forgot', 'username', 'sign in', 'authentication', 'verify'],
      other: []
    };

    // Find best matching category
    let bestMatch: TicketCategory = 'other';
    let bestScore = 0;

    for (const [cat, patterns] of Object.entries(categoryPatterns)) {
      if (cat === 'other') continue;
      const matches = patterns.filter(p => fullText.includes(p));
      if (matches.length > bestScore) {
        bestScore = matches.length;
        bestMatch = cat as TicketCategory;
      }
    }

    if (bestScore > 0) {
      category = bestMatch;
      reasons.push(`Detected as ${category} (${bestScore} matching patterns)`);
    } else {
      reasons.push('No specific category detected, defaulting to other');
    }

    // Priority scoring
    const criticalPatterns = ['urgent', 'critical', 'down', 'outage', 'security', 'breach', 'hack', 'data loss', 'emergency'];
    const highPatterns = ['important', 'asap', 'soon', 'broken', 'not working', 'can\'t access', 'unable to'];
    const lowPatterns = ['suggestion', 'when you have time', 'nice to have', 'future', 'low priority'];

    const criticalMatches = criticalPatterns.filter(p => fullText.includes(p)).length;
    const highMatches = highPatterns.filter(p => fullText.includes(p)).length;
    const lowMatches = lowPatterns.filter(p => fullText.includes(p)).length;

    score += criticalMatches * 25;
    score += highMatches * 10;
    score -= lowMatches * 15;

    if (criticalMatches > 0) {
      priority = 'critical';
      reasons.push(`Critical keywords detected: ${criticalMatches}`);
    } else if (highMatches > 0 && score >= 60) {
      priority = 'high';
      reasons.push(`High priority keywords detected: ${highMatches}`);
    } else if (score <= 30 || lowMatches > 0) {
      priority = 'low';
      reasons.push('Low priority indicators present');
    } else {
      priority = 'medium';
      reasons.push('Standard priority');
    }

    // Adjust for subject indicators
    if (subjectLower.startsWith('re:') || subjectLower.startsWith('fw:')) {
      score += 5;
      reasons.push('Follow-up message');
    }

    // Check for exclamation marks indicating urgency
    const exclamationCount = (ticket.subject.match(/!/g) || []).length;
    if (exclamationCount > 2) {
      score += exclamationCount * 3;
      reasons.push('Urgency indicators in subject');
    }

    // Cap score
    score = Math.min(100, Math.max(0, score));

    // Get assignment based on category
    const assignedTo = this.getDefaultAssignment(category);

    // Calculate confidence
    const confidence = Math.min(0.95, 0.5 + (reasons.length * 0.1) + (bestScore * 0.05));

    return {
      ticketId: ticket.id,
      category,
      priority,
      priorityScore: score,
      confidence,
      reasons,
      assignedTo,
      isSpam,
      spamScore,
      classifiedAt: new Date(),
      reviewed: false
    };
  }

  private getDefaultAssignment(category: TicketCategory): string {
    const defaults: Record<TicketCategory, string> = {
      bug: 'engineering',
      technical: 'support-tier2',
      billing: 'billing-team',
      account: 'customer-success',
      feature_request: 'product-team',
      complaint: 'customer-success',
      question: 'support-tier1',
      other: 'support-tier1'
    };
    return defaults[category] || 'support-tier1';
  }

  async classify(ticket: Ticket): Promise<TicketClassification> {
    await this.initDatabase();

    // Check for existing classification
    const existing = await this.getClassification(ticket.id);
    if (existing && !existing.reviewed) {
      return existing;
    }

    // Check classification rules
    const ruleMatch = await this.findMatchingRule(ticket);
    let classification: TicketClassification;

    if (ruleMatch && !ruleMatch.autoSpam) {
      classification = {
        ticketId: ticket.id,
        category: ruleMatch.category,
        priority: ruleMatch.priority,
        priorityScore: ruleMatch.priority === 'critical' ? 90 : ruleMatch.priority === 'high' ? 70 : 50,
        confidence: 0.9,
        reasons: ['Matched classification rule'],
        assignedTo: ruleMatch.assignedTo || this.getDefaultAssignment(ruleMatch.category),
        isSpam: false,
        spamScore: 0,
        classifiedAt: new Date(),
        reviewed: false
      };
    } else if (ruleMatch && ruleMatch.autoSpam) {
      classification = {
        ticketId: ticket.id,
        category: 'other',
        priority: 'low',
        priorityScore: 10,
        confidence: 0.95,
        reasons: ['Matched spam rule'],
        assignedTo: undefined,
        isSpam: true,
        spamScore: 0.95,
        classifiedAt: new Date(),
        reviewed: false
      };
    } else {
      classification = this.classifyTicket(ticket);
    }

    await this.saveClassification(classification);
    return classification;
  }

  private async findMatchingRule(ticket: Ticket): Promise<{
    category: TicketCategory;
    priority: TicketPriority;
    assignedTo?: string;
    autoSpam: boolean;
  } | null> {
    await this.initDatabase();
    if (!this.db) return null;

    const fullText = `${ticket.subject} ${ticket.body}`.toLowerCase();

    return new Promise((resolve, reject) => {
      this.db!.all('SELECT * FROM classification_rules', [], (err, rows: ClassificationRuleRecord[]) => {
        if (err) {
          reject(err);
          return;
        }

        for (const row of rows) {
          const pattern = row.pattern.toLowerCase();
          const matches = row.pattern_type === 'regex' 
            ? new RegExp(pattern, 'i').test(fullText)
            : fullText.includes(pattern);

          if (matches) {
            resolve({
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              assignedTo: row.assigned_to || undefined,
              autoSpam: row.auto_spam === 1
            });
            return;
          }
        }
        resolve(null);
      });
    });
  }

  private async saveClassification(classification: TicketClassification): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = `
      INSERT OR REPLACE INTO classifications 
      (ticket_id, category, priority, priority_score, confidence, reasons, assigned_to, is_spam, spam_score, classified_at, reviewed)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    await runWithResult(this.db, sql, [
      classification.ticketId,
      classification.category,
      classification.priority,
      classification.priorityScore,
      classification.confidence,
      JSON.stringify(classification.reasons),
      classification.assignedTo || null,
      classification.isSpam ? 1 : 0,
      classification.spamScore,
      classification.classifiedAt.toISOString(),
      classification.reviewed ? 1 : 0
    ]);
  }

  async getClassification(ticketId: string): Promise<TicketClassification | null> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.get(
        'SELECT * FROM classifications WHERE ticket_id = ?',
        [ticketId],
        (err, row: ClassificationRecord | undefined) => {
          if (err) {
            reject(err);
          } else if (!row) {
            resolve(null);
          } else {
            resolve({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            });
          }
        }
      );
    });
  }

  async listByCategory(category: TicketCategory, limit: number = 50): Promise<TicketClassification[]> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classifications WHERE category = ? ORDER BY priority_score DESC LIMIT ?',
        [category, limit],
        (err, rows: ClassificationRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            })));
          }
        }
      );
    });
  }

  async listByPriority(priority: TicketPriority, limit: number = 50): Promise<TicketClassification[]> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classifications WHERE priority = ? AND is_spam = 0 ORDER BY priority_score DESC LIMIT ?',
        [priority, limit],
        (err, rows: ClassificationRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            })));
          }
        }
      );
    });
  }

  async listByAssignee(team: string, limit: number = 50): Promise<TicketClassification[]> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classifications WHERE assigned_to = ? AND is_spam = 0 ORDER BY priority_score DESC LIMIT ?',
        [team, limit],
        (err, rows: ClassificationRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            })));
          }
        }
      );
    });
  }

  async getSpamTickets(limit: number = 50): Promise<TicketClassification[]> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classifications WHERE is_spam = 1 ORDER BY spam_score DESC LIMIT ?',
        [limit],
        (err, rows: ClassificationRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            })));
          }
        }
      );
    });
  }

  async getUnreviewed(limit: number = 50): Promise<TicketClassification[]> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classifications WHERE reviewed = 0 AND is_spam = 0 ORDER BY priority_score DESC LIMIT ?',
        [limit],
        (err, rows: ClassificationRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id,
              ticketId: row.ticket_id,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              priorityScore: row.priority_score,
              confidence: row.confidence,
              reasons: JSON.parse(row.reasons),
              assignedTo: row.assigned_to || undefined,
              isSpam: row.is_spam === 1,
              spamScore: row.spam_score,
              classifiedAt: new Date(row.classified_at),
              reviewed: row.reviewed === 1
            })));
          }
        }
      );
    });
  }

  async review(ticketId: string, updates: Partial<Pick<TicketClassification, 'category' | 'priority' | 'assignedTo'>>): Promise<void> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const classification = await this.getClassification(ticketId);
    if (!classification) {
      throw new Error(`No classification found for ticket ${ticketId}`);
    }

    // Log the change
    await runWithResult(this.db, `
      INSERT INTO classification_history (ticket_id, action_type, previous_category, new_category, previous_priority, new_priority, performed_at)
      VALUES (?, 'review', ?, ?, ?, ?, ?)
    `, [
      ticketId,
      classification.category,
      updates.category || classification.category,
      classification.priority,
      updates.priority || classification.priority,
      new Date().toISOString()
    ]);

    const sql = `
      UPDATE classifications 
      SET category = COALESCE(?, category),
          priority = COALESCE(?, priority),
          assigned_to = COALESCE(?, assigned_to),
          reviewed = 1
      WHERE ticket_id = ?
    `;

    await runWithResult(this.db, sql, [
      updates.category || null,
      updates.priority || null,
      updates.assignedTo || null,
      ticketId
    ]);
  }

  // Classification rules management
  async addClassificationRule(
    pattern: string,
    patternType: 'keyword' | 'regex',
    category: TicketCategory,
    priority: TicketPriority,
    assignedTo?: string,
    autoSpam: boolean = false
  ): Promise<void> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await runWithResult(this.db, `
      INSERT INTO classification_rules (pattern, pattern_type, category, priority, assigned_to, auto_spam, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      pattern,
      patternType,
      category,
      priority,
      assignedTo || null,
      autoSpam ? 1 : 0,
      new Date().toISOString()
    ]);
  }

  async listClassificationRules(): Promise<Array<{
    id: number;
    pattern: string;
    patternType: string;
    category: TicketCategory;
    priority: TicketPriority;
    assignedTo?: string;
    autoSpam: boolean;
    createdAt: Date;
  }>> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM classification_rules ORDER BY created_at DESC',
        [],
        (err, rows: ClassificationRuleRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id!,
              pattern: row.pattern,
              patternType: row.pattern_type,
              category: row.category as TicketCategory,
              priority: row.priority as TicketPriority,
              assignedTo: row.assigned_to || undefined,
              autoSpam: row.auto_spam === 1,
              createdAt: new Date(row.created_at)
            })));
          }
        }
      );
    });
  }

  async deleteClassificationRule(id: number): Promise<void> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await runWithResult(this.db, 'DELETE FROM classification_rules WHERE id = ?', [id]);
  }

  // Assignment rules management
  async updateAssignmentRule(category: TicketCategory, team: string, active: boolean = true): Promise<void> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await runWithResult(this.db, `
      INSERT OR REPLACE INTO assignment_rules (category, team, active, created_at)
      VALUES (?, ?, ?, ?)
    `, [
      category,
      team,
      active ? 1 : 0,
      new Date().toISOString()
    ]);
  }

  async getAssignmentRules(): Promise<Array<{
    id: number;
    category: TicketCategory;
    team: string;
    workload: number;
    active: boolean;
  }>> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM assignment_rules ORDER BY category',
        [],
        (err, rows: AssignmentRuleRecord[]) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows.map(row => ({
              id: row.id!,
              category: row.category as TicketCategory,
              team: row.team,
              workload: row.workload,
              active: row.active === 1
            })));
          }
        }
      );
    });
  }

  // Statistics
  async getStats(): Promise<ClassificationStats> {
    await this.initDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const stats: ClassificationStats = {
      totalClassified: 0,
      byCategory: {
        bug: 0, feature_request: 0, question: 0, complaint: 0,
        billing: 0, technical: 0, account: 0, other: 0
      },
      byPriority: {
        critical: 0, high: 0, medium: 0, low: 0
      },
      byAssignment: {},
      spamCount: 0,
      unreviewed: 0
    };

    return new Promise((resolve, reject) => {
      this.db!.get('SELECT COUNT(*) as count FROM classifications', [], (err, row: { count: number }) => {
        if (err) {
          reject(err);
          return;
        }
        stats.totalClassified = row.count;

        this.db!.all('SELECT category, COUNT(*) as count FROM classifications GROUP BY category', [], (err, rows: Array<{ category: string; count: number }>) => {
          if (err) {
            reject(err);
            return;
          }
          for (const row of rows) {
            stats.byCategory[row.category as TicketCategory] = row.count;
          }

          this.db!.all('SELECT priority, COUNT(*) as count FROM classifications GROUP BY priority', [], (err, rows: Array<{ priority: string; count: number }>) => {
            if (err) {
              reject(err);
              return;
            }
            for (const row of rows) {
              stats.byPriority[row.priority as TicketPriority] = row.count;
            }

            this.db!.all('SELECT assigned_to, COUNT(*) as count FROM classifications WHERE assigned_to IS NOT NULL GROUP BY assigned_to', [], (err, rows: Array<{ assigned_to: string; count: number }>) => {
              if (err) {
                reject(err);
                return;
              }
              for (const row of rows) {
                stats.byAssignment[row.assigned_to] = row.count;
              }

              this.db!.get('SELECT COUNT(*) as count FROM classifications WHERE is_spam = 1', [], (err, row: { count: number }) => {
                if (err) {
                  reject(err);
                  return;
                }
                stats.spamCount = row.count;

                this.db!.get('SELECT COUNT(*) as count FROM classifications WHERE reviewed = 0', [], (err, row: { count: number }) => {
                  if (err) {
                    reject(err);
                    return;
                  }
                  stats.unreviewed = row.count;
                  resolve(stats);
                });
              });
            });
          });
        });
      });
    });
  }

  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; message?: string }> {
    try {
      await this.initDatabase();
      return { status: 'healthy', message: 'Ticket triage system operational' };
    } catch (error: any) {
      return { status: 'unhealthy', message: error.message };
    }
  }

  async close(): Promise<void> {
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

export default TicketTriageSkill;
