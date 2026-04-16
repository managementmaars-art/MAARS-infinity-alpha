/**
 * Invoices Skill
 * Create, manage, and track professional invoices
 */

import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';

/**
 * Invoice status types
 */
export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';

/**
 * Line item for an invoice
 */
export interface LineItem {
  id?: number;
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
}

/**
 * Line item database record (snake_case columns)
 */
interface LineItemRecord {
  id?: number;
  invoice_id: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

/**
 * Client information
 */
export interface Client {
  id?: number;
  name: string;
  email?: string;
  address?: string;
  phone?: string;
  taxId?: string;
  notes?: string;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Payment record
 */
export interface Payment {
  id?: number;
  invoiceId: number;
  amount: number;
  method?: string;
  notes?: string;
  date: string;
}

/**
 * Invoice data
 */
export interface Invoice {
  id?: number;
  invoiceNumber: string;
  clientId: number;
  clientName?: string;
  issueDate: string;
  dueDate: string;
  status: InvoiceStatus;
  subtotal: number;
  taxRate: number;
  taxAmount: number;
  total: number;
  amountPaid: number;
  balanceDue: number;
  notes?: string;
  terms?: string;
  lineItems: LineItem[];
  payments?: Payment[];
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Invoice database record (snake_case columns)
 */
interface InvoiceRecord {
  id?: number;
  invoice_number: string;
  client_id: number;
  issue_date: string;
  due_date: string;
  status: InvoiceStatus;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;
  amount_paid: number;
  balance_due: number;
  notes?: string;
  terms?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Business configuration
 */
export interface BusinessConfig {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  taxId?: string;
  logoPath?: string;
  defaultTaxRate: number;
  defaultTerms: string;
  defaultDueDays: number;
  invoicePrefix: string;
  nextInvoiceNumber: number;
}

/**
 * Business config database record (snake_case columns)
 */
interface BusinessConfigRecord {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  logo_path?: string;
  default_tax_rate: number;
  default_terms: string;
  default_due_days: number;
  invoice_prefix: string;
  next_invoice_number: number;
}

/**
 * Invoice summary for reporting
 */
export interface InvoiceSummary {
  totalInvoices: number;
  totalRevenue: number;
  totalOutstanding: number;
  totalPaid: number;
  totalOverdue: number;
  byStatus: Record<InvoiceStatus, { count: number; amount: number }>;
}

/**
 * Invoices skill configuration
 */
export interface InvoicesSkillConfig {
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
 * Invoices Skill - Create and manage professional invoices
 */
export class InvoicesSkill {
  private dataDir: string;
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;

  constructor(config: InvoicesSkillConfig = {}) {
    this.dataDir = config.dataDir || path.join(os.homedir(), '.openclaw', 'skills', 'invoices');
    this.initPromise = this.initDatabase();
  }

  /**
   * Initialize database and directories
   */
  private async initDatabase(): Promise<void> {
    // Create directories
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true, mode: 0o700 });
    }
    const pdfDir = path.join(this.dataDir, 'pdfs');
    if (!fs.existsSync(pdfDir)) {
      fs.mkdirSync(pdfDir, { recursive: true, mode: 0o700 });
    }

    const dbPath = path.join(this.dataDir, 'invoices.db');
    
    this.db = await new Promise<sqlite3.Database>((resolve, reject) => {
      const db = new (sqlite3 as any).Database(dbPath, (err: Error | null) => {
        if (err) reject(err);
        else resolve(db);
      });
    });

    // Create tables
    await this.createTables();
  }

  /**
   * Create database tables
   */
  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Business config table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        name TEXT NOT NULL DEFAULT 'My Business',
        email TEXT,
        phone TEXT,
        address TEXT,
        tax_id TEXT,
        logo_path TEXT,
        default_tax_rate REAL DEFAULT 0,
        default_terms TEXT DEFAULT 'Net 30',
        default_due_days INTEGER DEFAULT 30,
        invoice_prefix TEXT DEFAULT 'INV-',
        next_invoice_number INTEGER DEFAULT 1
      )
    `);

    // Clients table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        address TEXT,
        phone TEXT,
        tax_id TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      )
    `);

    // Invoices table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL UNIQUE,
        client_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        subtotal REAL NOT NULL DEFAULT 0,
        tax_rate REAL NOT NULL DEFAULT 0,
        tax_amount REAL NOT NULL DEFAULT 0,
        total REAL NOT NULL DEFAULT 0,
        amount_paid REAL NOT NULL DEFAULT 0,
        balance_due REAL NOT NULL DEFAULT 0,
        notes TEXT,
        terms TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (client_id) REFERENCES clients(id)
      )
    `);

    // Line items table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 1,
        unit_price REAL NOT NULL DEFAULT 0,
        amount REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
      )
    `);

    // Payments table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        method TEXT,
        notes TEXT,
        date TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
      )
    `);

    // Create indexes
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_line_items_invoice ON line_items(invoice_id)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)`);

    // Insert default config if not exists
    await run(this.db, `
      INSERT OR IGNORE INTO config (id, name, default_tax_rate, default_terms, default_due_days, invoice_prefix, next_invoice_number)
      VALUES (1, 'My Business', 0, 'Net 30', 30, 'INV-', 1)
    `);
  }

  /**
   * Ensure database is initialized
   */
  private async ensureDatabase(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  /**
   * Get business configuration
   */
  async getConfig(): Promise<BusinessConfig> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const record = await get<BusinessConfigRecord>(this.db, 'SELECT * FROM config WHERE id = 1');
    if (!record) {
      throw new Error('Business configuration not found');
    }
    
    return {
      id: record.id,
      name: record.name,
      email: record.email,
      phone: record.phone,
      address: record.address,
      taxId: record.tax_id,
      logoPath: record.logo_path,
      defaultTaxRate: record.default_tax_rate,
      defaultTerms: record.default_terms,
      defaultDueDays: record.default_due_days,
      invoicePrefix: record.invoice_prefix,
      nextInvoiceNumber: record.next_invoice_number,
    };
  }

  /**
   * Update business configuration
   */
  async updateConfig(config: Partial<BusinessConfig>): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const values: any[] = [];

    if (config.name !== undefined) { fields.push('name = ?'); values.push(config.name); }
    if (config.email !== undefined) { fields.push('email = ?'); values.push(config.email); }
    if (config.phone !== undefined) { fields.push('phone = ?'); values.push(config.phone); }
    if (config.address !== undefined) { fields.push('address = ?'); values.push(config.address); }
    if (config.taxId !== undefined) { fields.push('tax_id = ?'); values.push(config.taxId); }
    if (config.logoPath !== undefined) { fields.push('logo_path = ?'); values.push(config.logoPath); }
    if (config.defaultTaxRate !== undefined) { fields.push('default_tax_rate = ?'); values.push(config.defaultTaxRate); }
    if (config.defaultTerms !== undefined) { fields.push('default_terms = ?'); values.push(config.defaultTerms); }
    if (config.defaultDueDays !== undefined) { fields.push('default_due_days = ?'); values.push(config.defaultDueDays); }
    if (config.invoicePrefix !== undefined) { fields.push('invoice_prefix = ?'); values.push(config.invoicePrefix); }
    if (config.nextInvoiceNumber !== undefined) { fields.push('next_invoice_number = ?'); values.push(config.nextInvoiceNumber); }

    if (fields.length > 0) {
      await run(this.db, `UPDATE config SET ${fields.join(', ')} WHERE id = 1`, values);
    }
  }

  /**
   * Create a new client
   */
  async createClient(client: Omit<Client, 'id' | 'createdAt' | 'updatedAt'>): Promise<Client> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const result = await runWithResult(this.db, `
      INSERT INTO clients (name, email, address, phone, tax_id, notes)
      VALUES (?, ?, ?, ?, ?, ?)
    `, [client.name, client.email || null, client.address || null, client.phone || null, client.taxId || null, client.notes || null]);

    const newClient = await get<Client>(this.db, 'SELECT * FROM clients WHERE id = ?', [result.lastID]);
    if (!newClient) throw new Error('Failed to create client');
    return newClient;
  }

  /**
   * Get client by ID
   */
  async getClient(id: number): Promise<Client | null> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const client = await get<Client>(this.db, 'SELECT * FROM clients WHERE id = ?', [id]);
    return client || null;
  }

  /**
   * Get client by name
   */
  async getClientByName(name: string): Promise<Client | null> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const client = await get<Client>(this.db, 'SELECT * FROM clients WHERE name = ?', [name]);
    return client || null;
  }

  /**
   * List all clients
   */
  async listClients(): Promise<Client[]> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    return await all<Client>(this.db, 'SELECT * FROM clients ORDER BY name');
  }

  /**
   * Update client
   */
  async updateClient(id: number, updates: Partial<Omit<Client, 'id' | 'createdAt' | 'updatedAt'>>): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const values: any[] = [];

    if (updates.name !== undefined) { fields.push('name = ?'); values.push(updates.name); }
    if (updates.email !== undefined) { fields.push('email = ?'); values.push(updates.email); }
    if (updates.address !== undefined) { fields.push('address = ?'); values.push(updates.address); }
    if (updates.phone !== undefined) { fields.push('phone = ?'); values.push(updates.phone); }
    if (updates.taxId !== undefined) { fields.push('tax_id = ?'); values.push(updates.taxId); }
    if (updates.notes !== undefined) { fields.push('notes = ?'); values.push(updates.notes); }

    if (fields.length > 0) {
      fields.push('updated_at = datetime("now")');
      values.push(id);
      await run(this.db, `UPDATE clients SET ${fields.join(', ')} WHERE id = ?`, values);
    }
  }

  /**
   * Delete client
   */
  async deleteClient(id: number): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await run(this.db, 'DELETE FROM clients WHERE id = ?', [id]);
  }

  /**
   * Generate next invoice number
   */
  private async generateInvoiceNumber(): Promise<string> {
    const config = await this.getConfig();
    const number = config.nextInvoiceNumber;
    const invoiceNumber = `${config.invoicePrefix}${number.toString().padStart(4, '0')}`;
    
    // Increment counter
    await this.updateConfig({ nextInvoiceNumber: number + 1 });
    
    return invoiceNumber;
  }

  /**
   * Calculate invoice totals from line items
   */
  private calculateTotals(lineItems: LineItem[], taxRate: number): { subtotal: number; taxAmount: number; total: number } {
    const subtotal = lineItems.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0);
    const taxAmount = subtotal * (taxRate / 100);
    const total = subtotal + taxAmount;
    return { subtotal, taxAmount, total };
  }

  /**
   * Create a new invoice
   */
  async createInvoice(
    clientId: number,
    lineItems: Omit<LineItem, 'id' | 'amount'>[],
    options: {
      issueDate?: string;
      dueDate?: string;
      taxRate?: number;
      notes?: string;
      terms?: string;
      status?: InvoiceStatus;
    } = {}
  ): Promise<Invoice> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const config = await this.getConfig();
    const client = await this.getClient(clientId);
    if (!client) throw new Error(`Client not found: ${clientId}`);

    // Calculate dates
    const issueDate = options.issueDate || new Date().toISOString().split('T')[0];
    const dueDate = options.dueDate || this.addDays(issueDate, config.defaultDueDays);
    const taxRate = options.taxRate !== undefined ? options.taxRate : config.defaultTaxRate;

    // Calculate line item amounts
    const calculatedLineItems: LineItem[] = lineItems.map(item => ({
      ...item,
      amount: item.quantity * item.unitPrice,
    }));

    // Calculate totals
    const { subtotal, taxAmount, total } = this.calculateTotals(calculatedLineItems, taxRate);

    // Generate invoice number
    const invoiceNumber = await this.generateInvoiceNumber();

    // Create invoice
    const result = await runWithResult(this.db, `
      INSERT INTO invoices (invoice_number, client_id, issue_date, due_date, status, 
        subtotal, tax_rate, tax_amount, total, amount_paid, balance_due, notes, terms)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    `, [
      invoiceNumber, clientId, issueDate, dueDate, options.status || 'draft',
      subtotal, taxRate, taxAmount, total, total,
      options.notes || null, options.terms || config.defaultTerms,
    ]);

    const invoiceId = result.lastID;

    // Create line items
    for (const item of calculatedLineItems) {
      await run(this.db, `
        INSERT INTO line_items (invoice_id, description, quantity, unit_price, amount)
        VALUES (?, ?, ?, ?, ?)
      `, [invoiceId, item.description, item.quantity, item.unitPrice, item.amount]);
    }

    return await this.getInvoice(invoiceId) as Invoice;
  }

  /**
   * Add days to a date string
   */
  private addDays(dateStr: string, days: number): string {
    const date = new Date(dateStr);
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  }

  /**
   * Get invoice by ID
   */
  async getInvoice(id: number): Promise<Invoice | null> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const record = await get<InvoiceRecord & { client_name: string }>(this.db, `
      SELECT i.*, c.name as client_name 
      FROM invoices i 
      JOIN clients c ON i.client_id = c.id 
      WHERE i.id = ?
    `, [id]);

    if (!record) return null;

    // Get line items
    const lineItemRecords = await all<LineItemRecord>(this.db, 
      'SELECT * FROM line_items WHERE invoice_id = ?', [id]
    );
    const lineItems: LineItem[] = lineItemRecords.map(r => ({
      id: r.id,
      description: r.description,
      quantity: r.quantity,
      unitPrice: r.unit_price,
      amount: r.amount,
    }));

    // Get payments
    const payments = await all<Payment>(this.db, 
      'SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC', [id]
    );

    return {
      id: record.id,
      invoiceNumber: record.invoice_number,
      clientId: record.client_id,
      clientName: record.client_name,
      issueDate: record.issue_date,
      dueDate: record.due_date,
      status: record.status,
      subtotal: record.subtotal,
      taxRate: record.tax_rate,
      taxAmount: record.tax_amount,
      total: record.total,
      amountPaid: record.amount_paid,
      balanceDue: record.balance_due,
      notes: record.notes,
      terms: record.terms,
      lineItems,
      payments,
      createdAt: record.created_at,
      updatedAt: record.updated_at,
    };
  }

  /**
   * Get invoice by number
   */
  async getInvoiceByNumber(invoiceNumber: string): Promise<Invoice | null> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const invoice = await get<{ id: number }>(this.db, 
      'SELECT id FROM invoices WHERE invoice_number = ?', [invoiceNumber]
    );

    if (!invoice) return null;
    return this.getInvoice(invoice.id);
  }

  /**
   * List invoices with optional filters
   */
  async listInvoices(options: {
    status?: InvoiceStatus;
    clientId?: number;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<Invoice[]> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    let sql = `
      SELECT i.*, c.name as client_name 
      FROM invoices i 
      JOIN clients c ON i.client_id = c.id 
      WHERE 1=1
    `;
    const params: any[] = [];

    if (options.status) {
      sql += ' AND i.status = ?';
      params.push(options.status);
    }
    if (options.clientId) {
      sql += ' AND i.client_id = ?';
      params.push(options.clientId);
    }
    if (options.startDate) {
      sql += ' AND i.issue_date >= ?';
      params.push(options.startDate);
    }
    if (options.endDate) {
      sql += ' AND i.issue_date <= ?';
      params.push(options.endDate);
    }

    sql += ' ORDER BY i.created_at DESC';

    const rows = await all<InvoiceRecord & { client_name: string }>(this.db, sql, params);

    // Get line items and payments for each invoice
    const invoices: Invoice[] = [];
    for (const row of rows) {
      const lineItemRecords = await all<LineItemRecord>(this.db, 
        'SELECT * FROM line_items WHERE invoice_id = ?', [row.id!]
      );
      const lineItems: LineItem[] = lineItemRecords.map(r => ({
        id: r.id,
        description: r.description,
        quantity: r.quantity,
        unitPrice: r.unit_price,
        amount: r.amount,
      }));
      const payments = await all<Payment>(this.db, 
        'SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC', [row.id!]
      );

      invoices.push({
        id: row.id,
        invoiceNumber: row.invoice_number,
        clientId: row.client_id,
        clientName: row.client_name,
        issueDate: row.issue_date,
        dueDate: row.due_date,
        status: row.status,
        subtotal: row.subtotal,
        taxRate: row.tax_rate,
        taxAmount: row.tax_amount,
        total: row.total,
        amountPaid: row.amount_paid,
        balanceDue: row.balance_due,
        notes: row.notes,
        terms: row.terms,
        lineItems,
        payments,
        createdAt: row.created_at,
        updatedAt: row.updated_at,
      });
    }

    return invoices;
  }

  /**
   * Update invoice
   */
  async updateInvoice(id: number, updates: Partial<Omit<Invoice, 'id' | 'createdAt' | 'updatedAt' | 'lineItems' | 'payments'>>): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const values: any[] = [];

    if (updates.issueDate !== undefined) { fields.push('issue_date = ?'); values.push(updates.issueDate); }
    if (updates.dueDate !== undefined) { fields.push('due_date = ?'); values.push(updates.dueDate); }
    if (updates.status !== undefined) { fields.push('status = ?'); values.push(updates.status); }
    if (updates.notes !== undefined) { fields.push('notes = ?'); values.push(updates.notes); }
    if (updates.terms !== undefined) { fields.push('terms = ?'); values.push(updates.terms); }

    if (fields.length > 0) {
      fields.push('updated_at = datetime("now")');
      values.push(id);
      await run(this.db, `UPDATE invoices SET ${fields.join(', ')} WHERE id = ?`, values);

      // Update status to overdue if past due date
      if (updates.dueDate || updates.status) {
        const today = new Date().toISOString().split('T')[0];
        await run(this.db, `
          UPDATE invoices 
          SET status = 'overdue' 
          WHERE id = ? AND due_date < ? AND status = 'sent'
        `, [id, today]);
      }
    }
  }

  /**
   * Update invoice line items
   */
  async updateLineItems(invoiceId: number, lineItems: Omit<LineItem, 'id' | 'amount'>[]): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    // Delete existing line items
    await run(this.db, 'DELETE FROM line_items WHERE invoice_id = ?', [invoiceId]);

    // Calculate new line items with amounts
    const calculatedLineItems: LineItem[] = lineItems.map(item => ({
      ...item,
      amount: item.quantity * item.unitPrice,
    }));

    // Insert new line items
    for (const item of calculatedLineItems) {
      await run(this.db, `
        INSERT INTO line_items (invoice_id, description, quantity, unit_price, amount)
        VALUES (?, ?, ?, ?, ?)
      `, [invoiceId, item.description, item.quantity, item.unitPrice, item.amount]);
    }

    // Get invoice to recalculate totals
    const invoice = await this.getInvoice(invoiceId);
    if (!invoice) throw new Error('Invoice not found');

    // Recalculate totals
    const { subtotal, taxAmount, total } = this.calculateTotals(calculatedLineItems, invoice.taxRate);
    const balanceDue = total - invoice.amountPaid;

    // Update invoice totals
    await run(this.db, `
      UPDATE invoices 
      SET subtotal = ?, tax_amount = ?, total = ?, balance_due = ?, updated_at = datetime('now')
      WHERE id = ?
    `, [subtotal, taxAmount, total, balanceDue, invoiceId]);
  }

  /**
   * Delete invoice
   */
  async deleteInvoice(id: number): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await run(this.db, 'DELETE FROM invoices WHERE id = ?', [id]);
  }

  /**
   * Mark invoice as sent
   */
  async markAsSent(id: number): Promise<void> {
    await this.updateInvoice(id, { status: 'sent' });
  }

  /**
   * Record a payment
   */
  async recordPayment(
    invoiceId: number,
    amount: number,
    options: { method?: string; notes?: string; date?: string } = {}
  ): Promise<Payment> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const invoice = await this.getInvoice(invoiceId);
    if (!invoice) throw new Error('Invoice not found');

    const paymentDate = options.date || new Date().toISOString().split('T')[0];

    // Create payment record
    const result = await runWithResult(this.db, `
      INSERT INTO payments (invoice_id, amount, method, notes, date)
      VALUES (?, ?, ?, ?, ?)
    `, [invoiceId, amount, options.method || null, options.notes || null, paymentDate]);

    // Update invoice amounts
    const newAmountPaid = invoice.amountPaid + amount;
    const newBalanceDue = invoice.total - newAmountPaid;
    const newStatus = newBalanceDue <= 0 ? 'paid' : invoice.status;

    await run(this.db, `
      UPDATE invoices 
      SET amount_paid = ?, balance_due = ?, status = ?, updated_at = datetime('now')
      WHERE id = ?
    `, [newAmountPaid, newBalanceDue, newStatus, invoiceId]);

    const payment = await get<Payment>(this.db, 'SELECT * FROM payments WHERE id = ?', [result.lastID]);
    if (!payment) throw new Error('Failed to create payment');
    return payment;
  }

  /**
   * Get payment by ID
   */
  async getPayment(id: number): Promise<Payment | null> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const payment = await get<Payment>(this.db, 'SELECT * FROM payments WHERE id = ?', [id]);
    return payment || null;
  }

  /**
   * Delete payment
   */
  async deletePayment(id: number): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const payment = await this.getPayment(id);
    if (!payment) throw new Error('Payment not found');

    const invoice = await this.getInvoice(payment.invoiceId);
    if (!invoice) throw new Error('Invoice not found');

    // Update invoice amounts
    const newAmountPaid = invoice.amountPaid - payment.amount;
    const newBalanceDue = invoice.total - newAmountPaid;

    await run(this.db, `
      UPDATE invoices 
      SET amount_paid = ?, balance_due = ?, status = CASE WHEN ? < ? THEN 'sent' ELSE status END,
          updated_at = datetime('now')
      WHERE id = ?
    `, [newAmountPaid, newBalanceDue, newAmountPaid, invoice.total, payment.invoiceId]);

    await run(this.db, 'DELETE FROM payments WHERE id = ?', [id]);
  }

  /**
   * Get invoice summary/report
   */
  async getSummary(options: {
    startDate?: string;
    endDate?: string;
  } = {}): Promise<InvoiceSummary> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    // Get totals by status
    let sql = 'SELECT status, COUNT(*) as count, SUM(total) as total, SUM(amount_paid) as paid FROM invoices WHERE 1=1';
    const params: any[] = [];

    if (options.startDate) {
      sql += ' AND issue_date >= ?';
      params.push(options.startDate);
    }
    if (options.endDate) {
      sql += ' AND issue_date <= ?';
      params.push(options.endDate);
    }

    sql += ' GROUP BY status';

    const rows = await all<{ status: InvoiceStatus; count: number; total: number; paid: number }>(this.db, sql, params);

    const byStatus: Record<InvoiceStatus, { count: number; amount: number }> = {
      draft: { count: 0, amount: 0 },
      sent: { count: 0, amount: 0 },
      paid: { count: 0, amount: 0 },
      overdue: { count: 0, amount: 0 },
      cancelled: { count: 0, amount: 0 },
    };

    let totalInvoices = 0;
    let totalRevenue = 0;
    let totalPaid = 0;
    let totalOutstanding = 0;
    let totalOverdue = 0;

    for (const row of rows) {
      byStatus[row.status] = { count: row.count, amount: row.total };
      totalInvoices += row.count;
      totalRevenue += row.total;
      totalPaid += row.paid || 0;

      if (row.status === 'sent' || row.status === 'overdue') {
        totalOutstanding += (row.total - (row.paid || 0));
        if (row.status === 'overdue') {
          totalOverdue += (row.total - (row.paid || 0));
        }
      }
    }

    return {
      totalInvoices,
      totalRevenue,
      totalOutstanding,
      totalPaid,
      totalOverdue,
      byStatus,
    };
  }

  /**
   * Get overdue invoices
   */
  async getOverdueInvoices(): Promise<Invoice[]> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const today = new Date().toISOString().split('T')[0];

    // First update any invoices that should be marked overdue
    await run(this.db, `
      UPDATE invoices 
      SET status = 'overdue' 
      WHERE due_date < ? AND status = 'sent'
    `, [today]);

    return this.listInvoices({ status: 'overdue' });
  }

  /**
   * Get client invoice history
   */
  async getClientInvoices(clientId: number): Promise<Invoice[]> {
    return this.listInvoices({ clientId });
  }

  /**
   * Generate HTML for PDF
   */
  private generateInvoiceHTML(invoice: Invoice, config: BusinessConfig): string {
    const formatCurrency = (amount: number) => `$${amount.toFixed(2)}`;
    const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString();

    const lineItemsHTML = invoice.lineItems.map(item => `
      <tr>
        <td>${item.description}</td>
        <td style="text-align: center;">${item.quantity}</td>
        <td style="text-align: right;">${formatCurrency(item.unitPrice)}</td>
        <td style="text-align: right;">${formatCurrency(item.amount)}</td>
      </tr>
    `).join('');

    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Invoice ${invoice.invoiceNumber}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    .header { display: flex; justify-content: space-between; margin-bottom: 40px; }
    .company-info { max-width: 300px; }
    .company-name { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .invoice-title { font-size: 32px; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }
    .invoice-details { background: #f8f9fa; padding: 20px; border-radius: 8px; }
    .detail-row { display: flex; justify-content: space-between; margin: 8px 0; }
    .detail-label { font-weight: bold; }
    .client-section { margin: 30px 0; }
    .section-title { font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 8px; }
    .client-name { font-size: 18px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin: 30px 0; }
    th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
    td { padding: 12px; border-bottom: 1px solid #ddd; }
    .totals { margin-top: 30px; text-align: right; }
    .total-row { margin: 8px 0; }
    .total-label { display: inline-block; width: 150px; font-weight: bold; }
    .total-value { display: inline-block; width: 100px; }
    .grand-total { font-size: 20px; font-weight: bold; margin-top: 15px; padding-top: 15px; border-top: 2px solid #2c3e50; }
    .status-badge { 
      display: inline-block; 
      padding: 6px 12px; 
      border-radius: 4px; 
      font-weight: bold; 
      text-transform: uppercase;
      font-size: 12px;
    }
    .status-draft { background: #95a5a6; color: white; }
    .status-sent { background: #3498db; color: white; }
    .status-paid { background: #27ae60; color: white; }
    .status-overdue { background: #e74c3c; color: white; }
    .status-cancelled { background: #7f8c8d; color: white; }
    .notes { margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
    .notes-title { font-weight: bold; margin-bottom: 10px; }
    .footer { margin-top: 60px; text-align: center; color: #666; font-size: 12px; }
  </style>
</head>
<body>
  <div class="header">
    <div class="company-info">
      <div class="company-name">${config.name}</div>
      ${config.address ? `<div>${config.address.replace(/\n/g, '<br>')}</div>` : ''}
      ${config.email ? `<div>${config.email}</div>` : ''}
      ${config.phone ? `<div>${config.phone}</div>` : ''}
      ${config.taxId ? `<div>Tax ID: ${config.taxId}</div>` : ''}
    </div>
    <div class="invoice-details">
      <div class="invoice-title">INVOICE</div>
      <div class="detail-row">
        <span class="detail-label">Invoice #:</span>
        <span>${invoice.invoiceNumber}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Issue Date:</span>
        <span>${formatDate(invoice.issueDate)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Due Date:</span>
        <span>${formatDate(invoice.dueDate)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Status:</span>
        <span class="status-badge status-${invoice.status}">${invoice.status}</span>
      </div>
    </div>
  </div>

  <div class="client-section">
    <div class="section-title">Bill To</div>
    <div class="client-name">${invoice.clientName}</div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Description</th>
        <th style="text-align: center;">Quantity</th>
        <th style="text-align: right;">Unit Price</th>
        <th style="text-align: right;">Amount</th>
      </tr>
    </thead>
    <tbody>
      ${lineItemsHTML}
    </tbody>
  </table>

  <div class="totals">
    <div class="total-row">
      <span class="total-label">Subtotal:</span>
      <span class="total-value">${formatCurrency(invoice.subtotal)}</span>
    </div>
    <div class="total-row">
      <span class="total-label">Tax (${invoice.taxRate}%):</span>
      <span class="total-value">${formatCurrency(invoice.taxAmount)}</span>
    </div>
    <div class="total-row grand-total">
      <span class="total-label">Total:</span>
      <span class="total-value">${formatCurrency(invoice.total)}</span>
    </div>
    ${invoice.amountPaid > 0 ? `
    <div class="total-row">
      <span class="total-label">Amount Paid:</span>
      <span class="total-value">${formatCurrency(invoice.amountPaid)}</span>
    </div>
    <div class="total-row grand-total">
      <span class="total-label">Balance Due:</span>
      <span class="total-value">${formatCurrency(invoice.balanceDue)}</span>
    </div>
    ` : ''}
  </div>

  ${invoice.notes ? `
  <div class="notes">
    <div class="notes-title">Notes</div>
    <div>${invoice.notes}</div>
  </div>
  ` : ''}

  ${invoice.terms ? `
  <div class="notes">
    <div class="notes-title">Terms & Conditions</div>
    <div>${invoice.terms}</div>
  </div>
  ` : ''}

  <div class="footer">
    Thank you for your business!
  </div>
</body>
</html>`;
  }

  /**
   * Generate PDF for invoice (returns HTML path, can be converted to PDF by user)
   */
  async generatePDF(invoiceId: number): Promise<{ htmlPath: string; pdfPath: string }> {
    await this.ensureDatabase();

    const invoice = await this.getInvoice(invoiceId);
    if (!invoice) throw new Error('Invoice not found');

    const config = await this.getConfig();
    const html = this.generateInvoiceHTML(invoice, config);

    const pdfDir = path.join(this.dataDir, 'pdfs');
    const baseFilename = `${invoice.invoiceNumber}`;
    const htmlPath = path.join(pdfDir, `${baseFilename}.html`);

    fs.writeFileSync(htmlPath, html, 'utf-8');

    // Return both HTML path and suggested PDF path
    // User can convert HTML to PDF using their preferred tool (puppeteer, wkhtmltopdf, etc.)
    return {
      htmlPath,
      pdfPath: path.join(pdfDir, `${baseFilename}.pdf`),
    };
  }

  /**
   * Export invoices to CSV
   */
  async exportToCSV(options: {
    status?: InvoiceStatus;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<{ filename: string; content: string }> {
    const invoices = await this.listInvoices(options);

    const lines: string[] = [
      'Invoice Number,Client,Issue Date,Due Date,Status,Subtotal,Tax,Total,Amount Paid,Balance Due',
    ];

    for (const inv of invoices) {
      lines.push([
        inv.invoiceNumber,
        `"${inv.clientName?.replace(/"/g, '""')}"`,
        inv.issueDate,
        inv.dueDate,
        inv.status,
        inv.subtotal,
        inv.taxAmount,
        inv.total,
        inv.amountPaid,
        inv.balanceDue,
      ].join(','));
    }

    const timestamp = new Date().toISOString().split('T')[0];
    return {
      filename: `invoices-${timestamp}.csv`,
      content: lines.join('\n'),
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; message: string }> {
    try {
      await this.ensureDatabase();
      if (!this.db) {
        return { status: 'unhealthy', message: 'Database not initialized' };
      }

      // Test database connection
      await get(this.db, 'SELECT 1');

      return { status: 'healthy', message: 'Invoices skill is ready' };
    } catch (error) {
      return { status: 'unhealthy', message: `Health check failed: ${error}` };
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
      await new Promise<void>((resolve) => {
        this.db!.close(() => resolve());
      });
      this.db = null;
    }
  }
}

/**
 * Factory function to get InvoicesSkill instance
 */
export function getInvoicesSkill(): InvoicesSkill {
  return new InvoicesSkill();
}

export default InvoicesSkill;
