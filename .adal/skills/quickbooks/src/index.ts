/**
 * QuickBooks Skill
 * Sync with QuickBooks Online for accounting integration
 * Supports customers, invoices, and transactions with two-way sync
 */

import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';
import { QuickBooksAuthClient, QuickBooksAuthResult } from '@openclaw/quickbooks-auth';

/**
 * QuickBooks Customer
 */
export interface Customer {
  id?: number;
  qbId: string;
  displayName: string;
  givenName?: string;
  familyName?: string;
  companyName?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  postalCode?: string;
  balance?: number;
  active: boolean;
  createdAt?: string;
  updatedAt?: string;
  lastSyncedAt?: string;
  localModified?: boolean;
}

/**
 * Customer database record (snake_case columns)
 */
interface CustomerRecord {
  id?: number;
  qb_id: string;
  display_name: string;
  given_name?: string;
  family_name?: string;
  company_name?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  postal_code?: string;
  balance?: number;
  active: number;
  created_at?: string;
  updated_at?: string;
  last_synced_at?: string;
  local_modified?: number;
}

/**
 * QuickBooks Invoice Line Item
 */
export interface InvoiceLineItem {
  id?: number;
  lineId: string;
  description?: string;
  amount: number;
  quantity?: number;
  unitPrice?: number;
  itemName?: string;
}

/**
 * Invoice line item database record
 */
interface InvoiceLineItemRecord {
  id?: number;
  line_id: string;
  invoice_id: number;
  description?: string;
  amount: number;
  quantity?: number;
  unit_price?: number;
  item_name?: string;
}

/**
 * QuickBooks Invoice
 */
export interface Invoice {
  id?: number;
  qbId: string;
  customerId: string;
  customerName?: string;
  docNumber: string;
  txnDate: string;
  dueDate?: string;
  totalAmount: number;
  balance: number;
  status: string;
  privateNote?: string;
  lineItems: InvoiceLineItem[];
  createdAt?: string;
  updatedAt?: string;
  lastSyncedAt?: string;
  localModified?: boolean;
}

/**
 * Invoice database record (snake_case columns)
 */
interface InvoiceRecord {
  id?: number;
  qb_id: string;
  customer_id: string;
  customer_name?: string;
  doc_number: string;
  txn_date: string;
  due_date?: string;
  total_amount: number;
  balance: number;
  status: string;
  private_note?: string;
  created_at?: string;
  updated_at?: string;
  last_synced_at?: string;
  local_modified?: number;
}

/**
 * QuickBooks Transaction
 */
export interface Transaction {
  id?: number;
  qbId: string;
  txnType: string;
  txnDate: string;
  amount: number;
  entityName?: string;
  entityType?: string;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
  lastSyncedAt?: string;
}

/**
 * Transaction database record
 */
interface TransactionRecord {
  id?: number;
  qb_id: string;
  txn_type: string;
  txn_date: string;
  amount: number;
  entity_name?: string;
  entity_type?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  last_synced_at?: string;
}

/**
 * Sync conflict
 */
export interface SyncConflict {
  id?: number;
  entityType: string;
  entityId: string;
  localData: string;
  remoteData: string;
  localUpdatedAt: string;
  remoteUpdatedAt: string;
  createdAt?: string;
  resolved?: boolean;
  resolution?: string;
}

/**
 * Sync conflict database record
 */
interface SyncConflictRecord {
  id?: number;
  entity_type: string;
  entity_id: string;
  local_data: string;
  remote_data: string;
  local_updated_at: string;
  remote_updated_at: string;
  created_at?: string;
  resolved?: number;
  resolution?: string;
}

/**
 * Sync state
 */
export interface SyncState {
  id?: number;
  entityType: string;
  lastSyncTime: string;
  syncToken?: string;
  recordCount: number;
}

/**
 * Sync state database record
 */
interface SyncStateRecord {
  id?: number;
  entity_type: string;
  last_sync_time: string;
  sync_token?: string;
  record_count: number;
}

/**
 * Sync result
 */
export interface SyncResult {
  entityType: string;
  created: number;
  updated: number;
  deleted: number;
  conflicts: number;
  errors: string[];
}

/**
 * QuickBooks skill configuration
 */
export interface QuickBooksSkillConfig {
  dataDir?: string;
  profile?: string;
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
 * QuickBooks Skill for accounting sync
 */
export class QuickBooksSkill {
  private db: sqlite3.Database | null = null;
  private dataDir: string;
  private authClient: QuickBooksAuthClient;
  private initPromise: Promise<void> | null = null;

  constructor(config: QuickBooksSkillConfig = {}) {
    this.dataDir = config.dataDir || path.join(os.homedir(), '.openclaw', 'skills', 'quickbooks');
    this.authClient = new QuickBooksAuthClient(config.profile || 'default');
  }

  /**
   * Initialize the database
   */
  private async init(): Promise<void> {
    if (this.initPromise) return this.initPromise;
    if (this.db) return;

    this.initPromise = this.doInit();
    return this.initPromise;
  }

  private async doInit(): Promise<void> {
    // Ensure data directory exists
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }

    const dbPath = path.join(this.dataDir, 'quickbooks.db');
    
    this.db = new (sqlite3 as any).Database(dbPath);

    // Create tables
    await this.createTables();
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Customers table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qb_id TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        given_name TEXT,
        family_name TEXT,
        company_name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        postal_code TEXT,
        balance REAL DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_synced_at TEXT,
        local_modified INTEGER DEFAULT 0
      )
    `);

    // Invoices table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qb_id TEXT UNIQUE NOT NULL,
        customer_id TEXT NOT NULL,
        customer_name TEXT,
        doc_number TEXT NOT NULL,
        txn_date TEXT NOT NULL,
        due_date TEXT,
        total_amount REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        private_note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_synced_at TEXT,
        local_modified INTEGER DEFAULT 0
      )
    `);

    // Invoice line items table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS invoice_line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_id TEXT NOT NULL,
        invoice_id INTEGER NOT NULL,
        description TEXT,
        amount REAL DEFAULT 0,
        quantity REAL,
        unit_price REAL,
        item_name TEXT,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
      )
    `);

    // Transactions table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qb_id TEXT UNIQUE NOT NULL,
        txn_type TEXT NOT NULL,
        txn_date TEXT NOT NULL,
        amount REAL DEFAULT 0,
        entity_name TEXT,
        entity_type TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_synced_at TEXT
      )
    `);

    // Sync state table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS sync_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT UNIQUE NOT NULL,
        last_sync_time TEXT,
        sync_token TEXT,
        record_count INTEGER DEFAULT 0
      )
    `);

    // Conflicts table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS conflicts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        local_data TEXT NOT NULL,
        remote_data TEXT NOT NULL,
        local_updated_at TEXT NOT NULL,
        remote_updated_at TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        resolved INTEGER DEFAULT 0,
        resolution TEXT,
        UNIQUE(entity_type, entity_id)
      )
    `);
  }

  /**
   * Check if connected to QuickBooks
   */
  async isConnected(): Promise<boolean> {
    return this.authClient.isConnected();
  }

  /**
   * Get connection status
   */
  async getStatus(): Promise<{
    connected: boolean;
    profile: string;
    realmId: string | null;
    environment: string;
  }> {
    const connected = await this.authClient.isConnected();
    const realmId = await this.authClient.getRealmId();
    const environment = await this.authClient.getEnvironment();

    return {
      connected,
      profile: 'default',
      realmId,
      environment,
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    message?: string;
    realmId?: string;
  }> {
    const health = await this.authClient.healthCheck();
    return {
      status: health.status,
      message: health.message,
      realmId: health.realmId,
    };
  }

  /**
   * Fetch customers from QuickBooks
   */
  async fetchCustomers(limit: number = 100): Promise<any[]> {
    const response = await this.authClient.fetch(`/query?query=select * from Customer maxresults ${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch customers: ${response.statusText}`);
    }
    const data = await response.json() as { QueryResponse?: { Customer?: any[] } };
    return data.QueryResponse?.Customer || [];
  }

  /**
   * Sync customers from QuickBooks
   */
  async syncCustomers(): Promise<SyncResult> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const result: SyncResult = {
      entityType: 'customers',
      created: 0,
      updated: 0,
      deleted: 0,
      conflicts: 0,
      errors: [],
    };

    try {
      const customers = await this.fetchCustomers(1000);
      const now = new Date().toISOString();

      for (const qbCustomer of customers) {
        try {
          // Check if customer exists locally
          const existing = await get<CustomerRecord>(
            this.db,
            'SELECT * FROM customers WHERE qb_id = ?',
            [qbCustomer.Id]
          );

          const customerData = {
            qb_id: qbCustomer.Id,
            display_name: qbCustomer.DisplayName || '',
            given_name: qbCustomer.GivenName || null,
            family_name: qbCustomer.FamilyName || null,
            company_name: qbCustomer.CompanyName || null,
            email: qbCustomer.PrimaryEmailAddr?.Address || null,
            phone: qbCustomer.PrimaryPhone?.FreeFormNumber || null,
            address: qbCustomer.BillAddr?.Line1 || null,
            city: qbCustomer.BillAddr?.City || null,
            country: qbCustomer.BillAddr?.Country || null,
            postal_code: qbCustomer.BillAddr?.PostalCode || null,
            balance: qbCustomer.Balance || 0,
            active: qbCustomer.Active !== false ? 1 : 0,
            last_synced_at: now,
          };

          if (existing) {
            // Check for conflict - local modifications
            if (existing.local_modified) {
              // Record conflict
              await this.recordConflict('customer', qbCustomer.Id, existing, customerData);
              result.conflicts++;
              continue;
            }

            // Update existing
            await run(this.db, `
              UPDATE customers SET
                display_name = ?,
                given_name = ?,
                family_name = ?,
                company_name = ?,
                email = ?,
                phone = ?,
                address = ?,
                city = ?,
                country = ?,
                postal_code = ?,
                balance = ?,
                active = ?,
                last_synced_at = ?,
                updated_at = ?
              WHERE qb_id = ?
            `, [
              customerData.display_name,
              customerData.given_name,
              customerData.family_name,
              customerData.company_name,
              customerData.email,
              customerData.phone,
              customerData.address,
              customerData.city,
              customerData.country,
              customerData.postal_code,
              customerData.balance,
              customerData.active,
              customerData.last_synced_at,
              now,
              qbCustomer.Id,
            ]);
            result.updated++;
          } else {
            // Insert new
            await run(this.db, `
              INSERT INTO customers (
                qb_id, display_name, given_name, family_name, company_name,
                email, phone, address, city, country, postal_code,
                balance, active, last_synced_at
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `, [
              customerData.qb_id,
              customerData.display_name,
              customerData.given_name,
              customerData.family_name,
              customerData.company_name,
              customerData.email,
              customerData.phone,
              customerData.address,
              customerData.city,
              customerData.country,
              customerData.postal_code,
              customerData.balance,
              customerData.active,
              customerData.last_synced_at,
            ]);
            result.created++;
          }
        } catch (err) {
          result.errors.push(`Customer ${qbCustomer.Id}: ${err instanceof Error ? err.message : String(err)}`);
        }
      }

      // Update sync state
      await this.updateSyncState('customers', result.created + result.updated);

    } catch (err) {
      result.errors.push(`Sync failed: ${err instanceof Error ? err.message : String(err)}`);
    }

    return result;
  }

  /**
   * Get customers from local database
   */
  async getCustomers(limit: number = 100): Promise<Customer[]> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const records = await all<CustomerRecord>(
      this.db,
      'SELECT * FROM customers ORDER BY display_name LIMIT ?',
      [limit]
    );

    return records.map(this.recordToCustomer);
  }

  /**
   * Get a single customer
   */
  async getCustomer(id: string | number): Promise<Customer | null> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    let record: CustomerRecord | undefined;
    
    if (typeof id === 'number' || !isNaN(Number(id))) {
      record = await get<CustomerRecord>(
        this.db,
        'SELECT * FROM customers WHERE id = ?',
        [Number(id)]
      );
    } else {
      record = await get<CustomerRecord>(
        this.db,
        'SELECT * FROM customers WHERE qb_id = ?',
        [id]
      );
    }

    return record ? this.recordToCustomer(record) : null;
  }

  /**
   * Convert database record to Customer
   */
  private recordToCustomer(record: CustomerRecord): Customer {
    return {
      id: record.id,
      qbId: record.qb_id,
      displayName: record.display_name,
      givenName: record.given_name,
      familyName: record.family_name,
      companyName: record.company_name,
      email: record.email,
      phone: record.phone,
      address: record.address,
      city: record.city,
      country: record.country,
      postalCode: record.postal_code,
      balance: record.balance,
      active: record.active === 1,
      createdAt: record.created_at,
      updatedAt: record.updated_at,
      lastSyncedAt: record.last_synced_at,
      localModified: record.local_modified === 1,
    };
  }

  /**
   * Fetch invoices from QuickBooks
   */
  async fetchInvoices(limit: number = 100, since?: string): Promise<any[]> {
    let query = `select * from Invoice maxresults ${limit}`;
    if (since) {
      query = `select * from Invoice where MetaData.LastUpdatedTime >= '${since}' maxresults ${limit}`;
    }
    
    const response = await this.authClient.fetch(`/query?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch invoices: ${response.statusText}`);
    }
    const data = await response.json() as { QueryResponse?: { Invoice?: any[] } };
    return data.QueryResponse?.Invoice || [];
  }

  /**
   * Sync invoices from QuickBooks
   */
  async syncInvoices(since?: string): Promise<SyncResult> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const result: SyncResult = {
      entityType: 'invoices',
      created: 0,
      updated: 0,
      deleted: 0,
      conflicts: 0,
      errors: [],
    };

    try {
      const invoices = await this.fetchInvoices(1000, since);
      const now = new Date().toISOString();

      for (const qbInvoice of invoices) {
        try {
          // Check if invoice exists locally
          const existing = await get<InvoiceRecord>(
            this.db,
            'SELECT * FROM invoices WHERE qb_id = ?',
            [qbInvoice.Id]
          );

          const invoiceData = {
            qb_id: qbInvoice.Id,
            customer_id: qbInvoice.CustomerRef?.value || '',
            customer_name: qbInvoice.CustomerRef?.name || '',
            doc_number: qbInvoice.DocNumber || '',
            txn_date: qbInvoice.TxnDate || '',
            due_date: qbInvoice.DueDate || null,
            total_amount: qbInvoice.TotalAmt || 0,
            balance: qbInvoice.Balance || 0,
            status: this.getInvoiceStatus(qbInvoice),
            private_note: qbInvoice.PrivateNote || null,
            last_synced_at: now,
          };

          let invoiceId: number;

          if (existing) {
            // Check for conflict
            if (existing.local_modified) {
              await this.recordConflict('invoice', qbInvoice.Id, existing, invoiceData);
              result.conflicts++;
              continue;
            }

            // Update existing
            await run(this.db, `
              UPDATE invoices SET
                customer_id = ?,
                customer_name = ?,
                doc_number = ?,
                txn_date = ?,
                due_date = ?,
                total_amount = ?,
                balance = ?,
                status = ?,
                private_note = ?,
                last_synced_at = ?,
                updated_at = ?
              WHERE qb_id = ?
            `, [
              invoiceData.customer_id,
              invoiceData.customer_name,
              invoiceData.doc_number,
              invoiceData.txn_date,
              invoiceData.due_date,
              invoiceData.total_amount,
              invoiceData.balance,
              invoiceData.status,
              invoiceData.private_note,
              invoiceData.last_synced_at,
              now,
              qbInvoice.Id,
            ]);
            invoiceId = existing.id!;
            result.updated++;
          } else {
            // Insert new
            const insertResult = await runWithResult(this.db, `
              INSERT INTO invoices (
                qb_id, customer_id, customer_name, doc_number, txn_date,
                due_date, total_amount, balance, status, private_note, last_synced_at
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `, [
              invoiceData.qb_id,
              invoiceData.customer_id,
              invoiceData.customer_name,
              invoiceData.doc_number,
              invoiceData.txn_date,
              invoiceData.due_date,
              invoiceData.total_amount,
              invoiceData.balance,
              invoiceData.status,
              invoiceData.private_note,
              invoiceData.last_synced_at,
            ]);
            invoiceId = insertResult.lastID;
            result.created++;
          }

          // Sync line items
          await this.syncInvoiceLineItems(invoiceId, qbInvoice.Line || []);

        } catch (err) {
          result.errors.push(`Invoice ${qbInvoice.Id}: ${err instanceof Error ? err.message : String(err)}`);
        }
      }

      // Update sync state
      await this.updateSyncState('invoices', result.created + result.updated);

    } catch (err) {
      result.errors.push(`Sync failed: ${err instanceof Error ? err.message : String(err)}`);
    }

    return result;
  }

  /**
   * Get invoice status from QuickBooks data
   */
  private getInvoiceStatus(qbInvoice: any): string {
    if (qbInvoice.Balance === 0) return 'Paid';
    if (qbInvoice.Balance < qbInvoice.TotalAmt) return 'Partial';
    if (qbInvoice.DueDate && new Date(qbInvoice.DueDate) < new Date()) return 'Overdue';
    return 'Pending';
  }

  /**
   * Sync invoice line items
   */
  private async syncInvoiceLineItems(invoiceId: number, lines: any[]): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Delete existing line items
    await run(this.db, 'DELETE FROM invoice_line_items WHERE invoice_id = ?', [invoiceId]);

    // Insert new line items (skip subtotal lines)
    for (const line of lines) {
      if (line.DetailType === 'SubTotalLineDetail') continue;

      await run(this.db, `
        INSERT INTO invoice_line_items (line_id, invoice_id, description, amount, quantity, unit_price, item_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `, [
        line.Id || `line-${Date.now()}`,
        invoiceId,
        line.Description || '',
        line.Amount || 0,
        line.SalesItemLineDetail?.Qty || null,
        line.SalesItemLineDetail?.UnitPrice || null,
        line.SalesItemLineDetail?.ItemRef?.name || null,
      ]);
    }
  }

  /**
   * Get invoices from local database
   */
  async getInvoices(limit: number = 100, status?: string): Promise<Invoice[]> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM invoices';
    const params: any[] = [];

    if (status && status !== 'all') {
      sql += ' WHERE status = ?';
      params.push(status);
    }

    sql += ' ORDER BY txn_date DESC LIMIT ?';
    params.push(limit);

    const records = await all<InvoiceRecord>(this.db, sql, params);

    const invoices: Invoice[] = [];
    for (const record of records) {
      const invoice = this.recordToInvoice(record);
      invoice.lineItems = await this.getInvoiceLineItems(record.id!);
      invoices.push(invoice);
    }

    return invoices;
  }

  /**
   * Get invoice line items
   */
  private async getInvoiceLineItems(invoiceId: number): Promise<InvoiceLineItem[]> {
    if (!this.db) throw new Error('Database not initialized');

    const records = await all<InvoiceLineItemRecord>(
      this.db,
      'SELECT * FROM invoice_line_items WHERE invoice_id = ?',
      [invoiceId]
    );

    return records.map(this.recordToInvoiceLineItem);
  }

  /**
   * Get a single invoice
   */
  async getInvoice(id: string | number): Promise<Invoice | null> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    let record: InvoiceRecord | undefined;
    
    if (typeof id === 'number' || !isNaN(Number(id))) {
      record = await get<InvoiceRecord>(
        this.db,
        'SELECT * FROM invoices WHERE id = ?',
        [Number(id)]
      );
    } else {
      record = await get<InvoiceRecord>(
        this.db,
        'SELECT * FROM invoices WHERE qb_id = ?',
        [id]
      );
    }

    if (!record) return null;

    const invoice = this.recordToInvoice(record);
    invoice.lineItems = await this.getInvoiceLineItems(record.id!);
    return invoice;
  }

  /**
   * Convert database record to Invoice
   */
  private recordToInvoice(record: InvoiceRecord): Invoice {
    return {
      id: record.id,
      qbId: record.qb_id,
      customerId: record.customer_id,
      customerName: record.customer_name,
      docNumber: record.doc_number,
      txnDate: record.txn_date,
      dueDate: record.due_date,
      totalAmount: record.total_amount,
      balance: record.balance,
      status: record.status,
      privateNote: record.private_note,
      lineItems: [],
      createdAt: record.created_at,
      updatedAt: record.updated_at,
      lastSyncedAt: record.last_synced_at,
      localModified: record.local_modified === 1,
    };
  }

  /**
   * Convert database record to InvoiceLineItem
   */
  private recordToInvoiceLineItem(record: InvoiceLineItemRecord): InvoiceLineItem {
    return {
      id: record.id,
      lineId: record.line_id,
      description: record.description,
      amount: record.amount,
      quantity: record.quantity,
      unitPrice: record.unit_price,
      itemName: record.item_name,
    };
  }

  /**
   * Fetch transactions from QuickBooks
   */
  async fetchTransactions(limit: number = 100): Promise<any[]> {
    const query = `select * from Transaction maxresults ${limit}`;
    
    const response = await this.authClient.fetch(`/query?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch transactions: ${response.statusText}`);
    }
    const data = await response.json() as { QueryResponse?: { Transaction?: any[] } };
    return data.QueryResponse?.Transaction || [];
  }

  /**
   * Sync transactions from QuickBooks
   */
  async syncTransactions(): Promise<SyncResult> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const result: SyncResult = {
      entityType: 'transactions',
      created: 0,
      updated: 0,
      deleted: 0,
      conflicts: 0,
      errors: [],
    };

    try {
      const transactions = await this.fetchTransactions(1000);
      const now = new Date().toISOString();

      for (const qbTxn of transactions) {
        try {
          // Check if transaction exists locally
          const existing = await get<TransactionRecord>(
            this.db,
            'SELECT * FROM transactions WHERE qb_id = ?',
            [qbTxn.Id]
          );

          const txnData = {
            qb_id: qbTxn.Id,
            txn_type: qbTxn.TxnType || 'Unknown',
            txn_date: qbTxn.TxnDate || '',
            amount: qbTxn.Amount || 0,
            entity_name: qbTxn.EntityRef?.name || null,
            entity_type: qbTxn.EntityRef?.type || null,
            description: qbTxn.PrivateNote || null,
            last_synced_at: now,
          };

          if (existing) {
            // Update existing
            await run(this.db, `
              UPDATE transactions SET
                txn_type = ?,
                txn_date = ?,
                amount = ?,
                entity_name = ?,
                entity_type = ?,
                description = ?,
                last_synced_at = ?,
                updated_at = ?
              WHERE qb_id = ?
            `, [
              txnData.txn_type,
              txnData.txn_date,
              txnData.amount,
              txnData.entity_name,
              txnData.entity_type,
              txnData.description,
              txnData.last_synced_at,
              now,
              qbTxn.Id,
            ]);
            result.updated++;
          } else {
            // Insert new
            await run(this.db, `
              INSERT INTO transactions (qb_id, txn_type, txn_date, amount, entity_name, entity_type, description, last_synced_at)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            `, [
              txnData.qb_id,
              txnData.txn_type,
              txnData.txn_date,
              txnData.amount,
              txnData.entity_name,
              txnData.entity_type,
              txnData.description,
              txnData.last_synced_at,
            ]);
            result.created++;
          }
        } catch (err) {
          result.errors.push(`Transaction ${qbTxn.Id}: ${err instanceof Error ? err.message : String(err)}`);
        }
      }

      // Update sync state
      await this.updateSyncState('transactions', result.created + result.updated);

    } catch (err) {
      result.errors.push(`Sync failed: ${err instanceof Error ? err.message : String(err)}`);
    }

    return result;
  }

  /**
   * Get transactions from local database
   */
  async getTransactions(limit: number = 100, type?: string): Promise<Transaction[]> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM transactions';
    const params: any[] = [];

    if (type) {
      sql += ' WHERE txn_type = ?';
      params.push(type);
    }

    sql += ' ORDER BY txn_date DESC LIMIT ?';
    params.push(limit);

    const records = await all<TransactionRecord>(this.db, sql, params);

    return records.map(this.recordToTransaction);
  }

  /**
   * Convert database record to Transaction
   */
  private recordToTransaction(record: TransactionRecord): Transaction {
    return {
      id: record.id,
      qbId: record.qb_id,
      txnType: record.txn_type,
      txnDate: record.txn_date,
      amount: record.amount,
      entityName: record.entity_name,
      entityType: record.entity_type,
      description: record.description,
      createdAt: record.created_at,
      updatedAt: record.updated_at,
      lastSyncedAt: record.last_synced_at,
    };
  }

  /**
   * Record a sync conflict
   */
  private async recordConflict(entityType: string, entityId: string, localData: any, remoteData: any): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const now = new Date().toISOString();

    await runWithResult(this.db, `
      INSERT INTO conflicts (entity_type, entity_id, local_data, remote_data, local_updated_at, remote_updated_at)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(entity_type, entity_id) DO UPDATE SET
        local_data = excluded.local_data,
        remote_data = excluded.remote_data,
        local_updated_at = excluded.local_updated_at,
        remote_updated_at = excluded.remote_updated_at,
        created_at = ?,
        resolved = 0,
        resolution = NULL
    `, [
      entityType,
      entityId,
      JSON.stringify(localData),
      JSON.stringify(remoteData),
      localData.updated_at || now,
      now,
      now,
    ]);
  }

  /**
   * Get unresolved conflicts
   */
  async getConflicts(): Promise<SyncConflict[]> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const records = await all<SyncConflictRecord>(
      this.db,
      'SELECT * FROM conflicts WHERE resolved = 0 ORDER BY created_at DESC'
    );

    return records.map(this.recordToConflict);
  }

  /**
   * Convert database record to SyncConflict
   */
  private recordToConflict(record: SyncConflictRecord): SyncConflict {
    return {
      id: record.id,
      entityType: record.entity_type,
      entityId: record.entity_id,
      localData: record.local_data,
      remoteData: record.remote_data,
      localUpdatedAt: record.local_updated_at,
      remoteUpdatedAt: record.remote_updated_at,
      createdAt: record.created_at,
      resolved: record.resolved === 1,
      resolution: record.resolution,
    };
  }

  /**
   * Resolve a conflict
   */
  async resolveConflict(conflictId: number, resolution: 'local' | 'remote'): Promise<boolean> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const conflict = await get<SyncConflictRecord>(
      this.db,
      'SELECT * FROM conflicts WHERE id = ?',
      [conflictId]
    );

    if (!conflict) return false;

    // Mark conflict as resolved
    await run(this.db, `
      UPDATE conflicts SET resolved = 1, resolution = ? WHERE id = ?
    `, [resolution, conflictId]);

    if (resolution === 'local') {
      // Keep local version - mark as modified to push later
      if (conflict.entity_type === 'customer') {
        await run(this.db, 'UPDATE customers SET local_modified = 1 WHERE qb_id = ?', [conflict.entity_id]);
      } else if (conflict.entity_type === 'invoice') {
        await run(this.db, 'UPDATE invoices SET local_modified = 1 WHERE qb_id = ?', [conflict.entity_id]);
      }
    } else {
      // Keep remote version - re-sync from QuickBooks
      if (conflict.entity_type === 'customer') {
        // Clear local modified flag
        await run(this.db, 'UPDATE customers SET local_modified = 0 WHERE qb_id = ?', [conflict.entity_id]);
      } else if (conflict.entity_type === 'invoice') {
        await run(this.db, 'UPDATE invoices SET local_modified = 0 WHERE qb_id = ?', [conflict.entity_id]);
      }
    }

    return true;
  }

  /**
   * Update sync state
   */
  private async updateSyncState(entityType: string, recordCount: number): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const now = new Date().toISOString();

    await runWithResult(this.db, `
      INSERT INTO sync_state (entity_type, last_sync_time, record_count)
      VALUES (?, ?, ?)
      ON CONFLICT(entity_type) DO UPDATE SET
        last_sync_time = excluded.last_sync_time,
        record_count = excluded.record_count
    `, [entityType, now, recordCount]);
  }

  /**
   * Get sync state
   */
  async getSyncState(): Promise<SyncState[]> {
    await this.init();
    if (!this.db) throw new Error('Database not initialized');

    const records = await all<SyncStateRecord>(
      this.db,
      'SELECT * FROM sync_state ORDER BY entity_type'
    );

    return records.map(r => ({
      id: r.id,
      entityType: r.entity_type,
      lastSyncTime: r.last_sync_time,
      syncToken: r.sync_token,
      recordCount: r.record_count,
    }));
  }

  /**
   * Full sync of all entities
   */
  async fullSync(options: {
    customers?: boolean;
    invoices?: boolean;
    transactions?: boolean;
    since?: string;
  } = {}): Promise<SyncResult[]> {
    const results: SyncResult[] = [];

    if (options.customers !== false) {
      results.push(await this.syncCustomers());
    }

    if (options.invoices !== false) {
      results.push(await this.syncInvoices(options.since));
    }

    if (options.transactions !== false) {
      results.push(await this.syncTransactions());
    }

    return results;
  }

  /**
   * Close the database connection
   */
  async close(): Promise<void> {
    // Wait for init to complete before closing
    if (this.initPromise) {
      try {
        await this.initPromise;
      } catch (err) {
        // Ignore init errors during close
      }
    }

    if (this.db) {
      return new Promise((resolve, reject) => {
        this.db!.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
  }
}

export default QuickBooksSkill;
