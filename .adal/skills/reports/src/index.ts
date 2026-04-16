/**
 * Reports Skill
 * Generate financial reports (P&L, Balance Sheet, Cash Flow)
 * Depends on quickbooks and receipts-ocr for data
 */

import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';
import { QuickBooksSkill } from '@openclaw/quickbooks';
import { ReceiptsOCRSkill } from '@openclaw/receipts-ocr';

/**
 * Report period (monthly, quarterly, yearly)
 */
export type ReportPeriod = 'monthly' | 'quarterly' | 'yearly' | 'custom';

/**
 * Date range for reports
 */
export interface DateRange {
  startDate: string;
  endDate: string;
}

/**
 * P&L Report data
 */
export interface PLReport {
  id?: number;
  name: string;
  period: ReportPeriod;
  dateRange: DateRange;
  generatedAt: string;
  revenue: {
    total: number;
    byCategory: Array<{ category: string; amount: number; percentage: number }>;
  };
  expenses: {
    total: number;
    byCategory: Array<{ category: string; amount: number; percentage: number }>;
  };
  grossProfit: number;
  netIncome: number;
  margin: number;
  summary: string;
}

/**
 * Balance Sheet data
 */
export interface BalanceSheet {
  id?: number;
  name: string;
  asOfDate: string;
  generatedAt: string;
  assets: {
    current: Array<{ name: string; amount: number }>;
    fixed: Array<{ name: string; amount: number }>;
    totalCurrent: number;
    totalFixed: number;
    total: number;
  };
  liabilities: {
    current: Array<{ name: string; amount: number }>;
    longTerm: Array<{ name: string; amount: number }>;
    totalCurrent: number;
    totalLongTerm: number;
    total: number;
  };
  equity: {
    items: Array<{ name: string; amount: number }>;
    total: number;
  };
  totalLiabilitiesAndEquity: number;
  balanced: boolean;
  summary: string;
}

/**
 * Cash Flow Report data
 */
export interface CashFlowReport {
  id?: number;
  name: string;
  period: ReportPeriod;
  dateRange: DateRange;
  generatedAt: string;
  operating: {
    inflows: number;
    outflows: number;
    net: number;
  };
  investing: {
    inflows: number;
    outflows: number;
    net: number;
  };
  financing: {
    inflows: number;
    outflows: number;
    net: number;
  };
  beginningCash: number;
  endingCash: number;
  netChange: number;
  summary: string;
}

/**
 * Scheduled report configuration
 */
export interface ScheduledReport {
  id?: number;
  name: string;
  type: 'pl' | 'balance' | 'cashflow';
  period: ReportPeriod;
  schedule: 'daily' | 'weekly' | 'monthly';
  emailRecipients?: string;
  active: boolean;
  lastRun?: string;
  nextRun?: string;
  createdAt?: string;
}

/**
 * Database record for scheduled report
 */
interface ScheduledReportRecord {
  id?: number;
  name: string;
  type: 'pl' | 'balance' | 'cashflow';
  period: ReportPeriod;
  schedule: 'daily' | 'weekly' | 'monthly';
  email_recipients?: string;
  active: number;
  last_run?: string;
  next_run?: string;
  created_at?: string;
}

/**
 * Report history entry
 */
export interface ReportHistory {
  id?: number;
  reportType: 'pl' | 'balance' | 'cashflow';
  reportName: string;
  generatedAt: string;
  dateRange: string;
  filePath?: string;
}

/**
 * Reports skill configuration
 */
export interface ReportsSkillConfig {
  dataDir?: string;
  quickbooksProfile?: string;
  receiptsProfile?: string;
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
 * Reports Skill - Generate financial reports
 */
export class ReportsSkill {
  private dataDir: string;
  private reportsDir: string;
  private db: sqlite3.Database | null = null;
  private initPromise: Promise<void> | null = null;
  private quickbooks: QuickBooksSkill | null = null;
  private receiptsOcr: ReceiptsOCRSkill | null = null;
  private quickbooksProfile: string;
  private receiptsProfile: string;

  constructor(config: ReportsSkillConfig = {}) {
    this.dataDir = config.dataDir || path.join(os.homedir(), '.openclaw', 'skills', 'reports');
    this.reportsDir = path.join(this.dataDir, 'reports');
    this.quickbooksProfile = config.quickbooksProfile || 'default';
    this.receiptsProfile = config.receiptsProfile || 'default';
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
    if (!fs.existsSync(this.reportsDir)) {
      fs.mkdirSync(this.reportsDir, { recursive: true, mode: 0o700 });
    }

    const dbPath = path.join(this.dataDir, 'reports.db');
    
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

    // Scheduled reports table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS scheduled_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('pl', 'balance', 'cashflow')),
        period TEXT NOT NULL CHECK(period IN ('monthly', 'quarterly', 'yearly', 'custom')),
        schedule TEXT NOT NULL CHECK(schedule IN ('daily', 'weekly', 'monthly')),
        email_recipients TEXT,
        active INTEGER DEFAULT 1,
        last_run TEXT,
        next_run TEXT,
        created_at TEXT DEFAULT (datetime('now'))
      )
    `);

    // Report history table
    await run(this.db, `
      CREATE TABLE IF NOT EXISTS report_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        report_name TEXT NOT NULL,
        generated_at TEXT DEFAULT (datetime('now')),
        date_range TEXT,
        file_path TEXT
      )
    `);

    // Create indexes
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_scheduled_active ON scheduled_reports(active)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_history_type ON report_history(report_type)`);
    await run(this.db, `CREATE INDEX IF NOT EXISTS idx_history_date ON report_history(generated_at)`);
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
   * Get or create QuickBooks skill instance
   */
  private async getQuickBooks(): Promise<QuickBooksSkill> {
    if (!this.quickbooks) {
      this.quickbooks = new QuickBooksSkill({ profile: this.quickbooksProfile });
    }
    return this.quickbooks;
  }

  /**
   * Get or create Receipts OCR skill instance
   */
  private async getReceiptsOcr(): Promise<ReceiptsOCRSkill> {
    if (!this.receiptsOcr) {
      this.receiptsOcr = new ReceiptsOCRSkill({ profile: this.receiptsProfile });
    }
    return this.receiptsOcr;
  }

  /**
   * Check health of dependencies
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    quickbooks: { connected: boolean; message?: string };
    receiptsOcr: { connected: boolean; message?: string };
  }> {
    let quickbooksStatus = { connected: false, message: 'Not checked' };
    let receiptsOcrStatus = { connected: false, message: 'Not checked' };

    try {
      const qb = await this.getQuickBooks();
      const qbConnected = await qb.isConnected();
      if (qbConnected) {
        const health = await qb.healthCheck();
        quickbooksStatus = { connected: true, message: health.message || 'Connected' };
      } else {
        quickbooksStatus = { connected: false, message: 'Not connected' };
      }
    } catch (err) {
      quickbooksStatus = { connected: false, message: String(err) };
    }

    try {
      const receipts = await this.getReceiptsOcr();
      const receiptsStatus = await receipts.getStatus();
      receiptsOcrStatus = { connected: receiptsStatus.connected, message: receiptsStatus.connected ? 'Connected' : 'Not connected' };
    } catch (err) {
      receiptsOcrStatus = { connected: false, message: String(err) };
    }

    const status = quickbooksStatus.connected || receiptsOcrStatus.connected
      ? (quickbooksStatus.connected && receiptsOcrStatus.connected ? 'healthy' : 'degraded')
      : 'unhealthy';

    return {
      status,
      quickbooks: quickbooksStatus,
      receiptsOcr: receiptsOcrStatus,
    };
  }

  /**
   * Get date range for a period
   */
  getDateRange(period: ReportPeriod, year?: number, month?: number): DateRange {
    const now = new Date();
    const targetYear = year || now.getFullYear();
    
    switch (period) {
      case 'monthly':
        const targetMonth = month !== undefined ? month : now.getMonth();
        const startDate = new Date(targetYear, targetMonth, 1);
        const endDate = new Date(targetYear, targetMonth + 1, 0);
        return {
          startDate: startDate.toISOString().split('T')[0],
          endDate: endDate.toISOString().split('T')[0],
        };
      
      case 'quarterly':
        const quarter = month !== undefined ? Math.floor(month / 3) : Math.floor(now.getMonth() / 3);
        const qStart = new Date(targetYear, quarter * 3, 1);
        const qEnd = new Date(targetYear, quarter * 3 + 3, 0);
        return {
          startDate: qStart.toISOString().split('T')[0],
          endDate: qEnd.toISOString().split('T')[0],
        };
      
      case 'yearly':
        return {
          startDate: `${targetYear}-01-01`,
          endDate: `${targetYear}-12-31`,
        };
      
      default:
        return {
          startDate: now.toISOString().split('T')[0],
          endDate: now.toISOString().split('T')[0],
        };
    }
  }

  /**
   * Generate P&L Report
   */
  async generatePLReport(options: {
    name?: string;
    period?: ReportPeriod;
    dateRange?: DateRange;
    year?: number;
    month?: number;
  } = {}): Promise<PLReport> {
    await this.ensureDatabase();

    const period = options.period || 'monthly';
    const dateRange = options.dateRange || this.getDateRange(period, options.year, options.month);
    const name = options.name || `P&L Report - ${period} ${dateRange.startDate}`;

    // Get data from QuickBooks and receipts
    const quickbooks = await this.getQuickBooks();
    const receiptsOcr = await this.getReceiptsOcr();

    // Get invoices (revenue) from QuickBooks
    const invoices = await quickbooks.getInvoices(1000);
    const periodInvoices = invoices.filter(inv => {
      return inv.txnDate >= dateRange.startDate && inv.txnDate <= dateRange.endDate;
    });

    // Calculate revenue by category
    const revenueByCustomer: Record<string, number> = {};
    let totalRevenue = 0;
    for (const inv of periodInvoices) {
      if (inv.status === 'Paid' || inv.status === 'Partial' || inv.status === 'Pending') {
        const amount = inv.totalAmount;
        totalRevenue += amount;
        const category = inv.customerName || 'Other';
        revenueByCustomer[category] = (revenueByCustomer[category] || 0) + amount;
      }
    }

    // Get expenses from receipts
    const receipts = await receiptsOcr.listReceipts({
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      status: 'confirmed',
    });

    // Calculate expenses by category
    const expensesByCategory: Record<string, number> = {};
    let totalExpenses = 0;
    for (const receipt of receipts) {
      if (receipt.totalAmount) {
        totalExpenses += receipt.totalAmount;
        const category = receipt.category || 'Uncategorized';
        expensesByCategory[category] = (expensesByCategory[category] || 0) + receipt.totalAmount;
      }
    }

    // Sort and format revenue categories
    const revenueCategories = Object.entries(revenueByCustomer)
      .map(([category, amount]) => ({
        category,
        amount,
        percentage: totalRevenue > 0 ? (amount / totalRevenue) * 100 : 0,
      }))
      .sort((a, b) => b.amount - a.amount);

    // Sort and format expense categories
    const expenseCategories = Object.entries(expensesByCategory)
      .map(([category, amount]) => ({
        category,
        amount,
        percentage: totalExpenses > 0 ? (amount / totalExpenses) * 100 : 0,
      }))
      .sort((a, b) => b.amount - a.amount);

    const grossProfit = totalRevenue - totalExpenses;
    const netIncome = grossProfit;
    const margin = totalRevenue > 0 ? (netIncome / totalRevenue) * 100 : 0;

    const report: PLReport = {
      name,
      period,
      dateRange,
      generatedAt: new Date().toISOString(),
      revenue: {
        total: totalRevenue,
        byCategory: revenueCategories,
      },
      expenses: {
        total: totalExpenses,
        byCategory: expenseCategories,
      },
      grossProfit,
      netIncome,
      margin,
      summary: `Generated ${totalRevenue.toFixed(2)} in revenue with ${totalExpenses.toFixed(2)} in expenses. Net income: ${netIncome.toFixed(2)} (${margin.toFixed(1)}% margin).`,
    };

    // Save to history
    await this.saveReportHistory('pl', name, dateRange);

    return report;
  }

  /**
   * Generate Balance Sheet
   */
  async generateBalanceSheet(options: {
    name?: string;
    asOfDate?: string;
  } = {}): Promise<BalanceSheet> {
    await this.ensureDatabase();

    const asOfDate = options.asOfDate || new Date().toISOString().split('T')[0];
    const name = options.name || `Balance Sheet - ${asOfDate}`;

    // Get data from QuickBooks
    const quickbooks = await this.getQuickBooks();
    
    // Get all customers with balances (accounts receivable)
    const customers = await quickbooks.getCustomers(1000);
    const accountsReceivable = customers
      .filter(c => c.balance && c.balance > 0)
      .reduce((sum, c) => sum + (c.balance || 0), 0);

    // Get all invoices
    const invoices = await quickbooks.getInvoices(1000);
    const pendingInvoices = invoices.filter(inv => inv.status === 'Pending' || inv.status === 'Partial');
    const totalPending = pendingInvoices.reduce((sum, inv) => sum + inv.balance, 0);

    // Get paid invoices (cash equivalent)
    const paidInvoices = invoices.filter(inv => inv.status === 'Paid');
    const totalCash = paidInvoices.reduce((sum, inv) => sum + inv.totalAmount, 0);

    // Current assets
    const currentAssets = [
      { name: 'Cash and Equivalents', amount: totalCash },
      { name: 'Accounts Receivable', amount: accountsReceivable + totalPending },
    ].filter(a => a.amount > 0);

    const totalCurrentAssets = currentAssets.reduce((sum, a) => sum + a.amount, 0);

    // Fixed assets (placeholder - would come from asset tracking)
    const fixedAssets: Array<{ name: string; amount: number }> = [];
    const totalFixedAssets = 0;

    const totalAssets = totalCurrentAssets + totalFixedAssets;

    // Liabilities
    const currentLiabilities: Array<{ name: string; amount: number }> = [];
    const longTermLiabilities: Array<{ name: string; amount: number }> = [];

    // Get transactions for expense accruals
    const transactions = await quickbooks.getTransactions(1000);
    const outstandingPayables = transactions
      .filter(t => t.txnType === 'Bill' && new Date(t.txnDate) <= new Date(asOfDate))
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    if (outstandingPayables > 0) {
      currentLiabilities.push({ name: 'Accounts Payable', amount: outstandingPayables });
    }

    const totalCurrentLiabilities = currentLiabilities.reduce((sum, l) => sum + l.amount, 0);
    const totalLongTermLiabilities = longTermLiabilities.reduce((sum, l) => sum + l.amount, 0);
    const totalLiabilities = totalCurrentLiabilities + totalLongTermLiabilities;

    // Equity
    const retainedEarnings = totalAssets - totalLiabilities;
    const equity = {
      items: [
        { name: 'Owner\'s Equity', amount: retainedEarnings > 0 ? retainedEarnings : 0 },
        { name: 'Retained Earnings', amount: 0 },
      ].filter(e => e.amount > 0),
      total: retainedEarnings > 0 ? retainedEarnings : 0,
    };

    const totalLiabilitiesAndEquity = totalLiabilities + equity.total;
    const balanced = Math.abs(totalAssets - totalLiabilitiesAndEquity) < 0.01;

    const report: BalanceSheet = {
      name,
      asOfDate,
      generatedAt: new Date().toISOString(),
      assets: {
        current: currentAssets,
        fixed: fixedAssets,
        totalCurrent: totalCurrentAssets,
        totalFixed: totalFixedAssets,
        total: totalAssets,
      },
      liabilities: {
        current: currentLiabilities,
        longTerm: longTermLiabilities,
        totalCurrent: totalCurrentLiabilities,
        totalLongTerm: totalLongTermLiabilities,
        total: totalLiabilities,
      },
      equity,
      totalLiabilitiesAndEquity,
      balanced,
      summary: `Total assets: ${totalAssets.toFixed(2)}. Total liabilities: ${totalLiabilities.toFixed(2)}. Equity: ${equity.total.toFixed(2)}. ${balanced ? 'Balanced' : 'Unbalanced'}.`,
    };

    // Save to history
    await this.saveReportHistory('balance', name, { startDate: asOfDate, endDate: asOfDate });

    return report;
  }

  /**
   * Generate Cash Flow Report
   */
  async generateCashFlowReport(options: {
    name?: string;
    period?: ReportPeriod;
    dateRange?: DateRange;
    year?: number;
    month?: number;
  } = {}): Promise<CashFlowReport> {
    await this.ensureDatabase();

    const period = options.period || 'monthly';
    const dateRange = options.dateRange || this.getDateRange(period, options.year, options.month);
    const name = options.name || `Cash Flow Report - ${period} ${dateRange.startDate}`;

    // Get data from QuickBooks
    const quickbooks = await this.getQuickBooks();
    const transactions = await quickbooks.getTransactions(1000);

    // Filter transactions by date
    const periodTransactions = transactions.filter(t => {
      return t.txnDate >= dateRange.startDate && t.txnDate <= dateRange.endDate;
    });

    // Categorize transactions
    let operatingInflows = 0;
    let operatingOutflows = 0;
    let investingInflows = 0;
    let investingOutflows = 0;
    let financingInflows = 0;
    let financingOutflows = 0;

    for (const txn of periodTransactions) {
      const amount = Math.abs(txn.amount);
      
      // Simple categorization based on transaction type
      switch (txn.txnType) {
        case 'Invoice':
        case 'Payment':
        case 'SalesReceipt':
          operatingInflows += amount;
          break;
        case 'Bill':
        case 'Expense':
          operatingOutflows += amount;
          break;
        case 'Deposit':
          if (amount > 1000) {
            financingInflows += amount;
          } else {
            operatingInflows += amount;
          }
          break;
        case 'Transfer':
          if (txn.amount < 0) {
            financingOutflows += Math.abs(txn.amount);
          } else {
            financingInflows += txn.amount;
          }
          break;
        default:
          if (txn.amount > 0) {
            operatingInflows += txn.amount;
          } else {
            operatingOutflows += Math.abs(txn.amount);
          }
      }
    }

    // Get receipts as operating expenses
    const receiptsOcr = await this.getReceiptsOcr();
    const receipts = await receiptsOcr.listReceipts({
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      status: 'confirmed',
    });
    const receiptTotal = receipts.reduce((sum, r) => sum + (r.totalAmount || 0), 0);
    operatingOutflows += receiptTotal;

    const operatingNet = operatingInflows - operatingOutflows;
    const investingNet = investingInflows - investingOutflows;
    const financingNet = financingInflows - financingOutflows;
    const netChange = operatingNet + investingNet + financingNet;

    // Estimate beginning cash (simplified)
    const beginningCash = Math.max(0, operatingInflows * 0.8);
    const endingCash = beginningCash + netChange;

    const report: CashFlowReport = {
      name,
      period,
      dateRange,
      generatedAt: new Date().toISOString(),
      operating: {
        inflows: operatingInflows,
        outflows: operatingOutflows,
        net: operatingNet,
      },
      investing: {
        inflows: investingInflows,
        outflows: investingOutflows,
        net: investingNet,
      },
      financing: {
        inflows: financingInflows,
        outflows: financingOutflows,
        net: financingNet,
      },
      beginningCash,
      endingCash,
      netChange,
      summary: `Operating: ${operatingNet >= 0 ? '+' : ''}${operatingNet.toFixed(2)}, Investing: ${investingNet >= 0 ? '+' : ''}${investingNet.toFixed(2)}, Financing: ${financingNet >= 0 ? '+' : ''}${financingNet.toFixed(2)}. Net change: ${netChange >= 0 ? '+' : ''}${netChange.toFixed(2)}.`,
    };

    // Save to history
    await this.saveReportHistory('cashflow', name, dateRange);

    return report;
  }

  /**
   * Save report to history
   */
  private async saveReportHistory(reportType: 'pl' | 'balance' | 'cashflow', reportName: string, dateRange: DateRange): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) return;

    await run(this.db, `
      INSERT INTO report_history (report_type, report_name, date_range)
      VALUES (?, ?, ?)
    `, [reportType, reportName, `${dateRange.startDate} to ${dateRange.endDate}`]);
  }

  /**
   * Get report history
   */
  async getReportHistory(reportType?: 'pl' | 'balance' | 'cashflow', limit: number = 50): Promise<ReportHistory[]> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM report_history';
    const params: any[] = [];

    if (reportType) {
      sql += ' WHERE report_type = ?';
      params.push(reportType);
    }

    sql += ' ORDER BY generated_at DESC LIMIT ?';
    params.push(limit);

    const records = await all<{
      id?: number;
      report_type: string;
      report_name: string;
      generated_at: string;
      date_range: string;
      file_path?: string;
    }>(this.db, sql, params);

    return records.map(r => ({
      id: r.id,
      reportType: r.report_type as 'pl' | 'balance' | 'cashflow',
      reportName: r.report_name,
      generatedAt: r.generated_at,
      dateRange: r.date_range,
      filePath: r.file_path,
    }));
  }

  /**
   * Generate HTML report for PDF export
   */
  generateHTMLReport(report: PLReport | BalanceSheet | CashFlowReport): string {
    const now = new Date().toLocaleString();

    if ('revenue' in report) {
      // P&L Report
      return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${report.name}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    h1 { color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }
    h2 { color: #2c5282; margin-top: 30px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { background: #edf2f7; font-weight: 600; }
    .total { font-weight: bold; background: #f7fafc; }
    .positive { color: #38a169; }
    .negative { color: #e53e3e; }
    .summary { background: #ebf8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
    .footer { margin-top: 40px; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 20px; }
  </style>
</head>
<body>
  <h1>${report.name}</h1>
  <p><strong>Period:</strong> ${report.period} (${report.dateRange.startDate} to ${report.dateRange.endDate})</p>
  <p><strong>Generated:</strong> ${now}</p>

  <div class="summary">
    <h2>Summary</h2>
    <p>${report.summary}</p>
    <p><strong>Net Income:</strong> <span class="${report.netIncome >= 0 ? 'positive' : 'negative'}">${report.netIncome.toFixed(2)} (${report.margin.toFixed(1)}%)</span></p>
  </div>

  <h2>Revenue</h2>
  <table>
    <thead>
      <tr><th>Category</th><th>Amount</th><th>%</th></tr>
    </thead>
    <tbody>
      ${report.revenue.byCategory.map(c => `
        <tr><td>${c.category}</td><td>${c.amount.toFixed(2)}</td><td>${c.percentage.toFixed(1)}%</td></tr>
      `).join('')}
      <tr class="total"><td>Total Revenue</td><td>${report.revenue.total.toFixed(2)}</td><td>100%</td></tr>
    </tbody>
  </table>

  <h2>Expenses</h2>
  <table>
    <thead>
      <tr><th>Category</th><th>Amount</th><th>%</th></tr>
    </thead>
    <tbody>
      ${report.expenses.byCategory.map(c => `
        <tr><td>${c.category}</td><td>${c.amount.toFixed(2)}</td><td>${c.percentage.toFixed(1)}%</td></tr>
      `).join('')}
      <tr class="total"><td>Total Expenses</td><td>${report.expenses.total.toFixed(2)}</td><td>100%</td></tr>
    </tbody>
  </table>

  <div class="footer">
    Generated by OpenClaw Reports Skill
  </div>
</body>
</html>`;
    } else if ('assets' in report) {
      // Balance Sheet
      return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${report.name}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    h1 { color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }
    h2 { color: #2c5282; margin-top: 30px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { background: #edf2f7; font-weight: 600; }
    .total { font-weight: bold; background: #f7fafc; }
    .summary { background: #ebf8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
    .balanced { color: #38a169; }
    .unbalanced { color: #e53e3e; }
    .footer { margin-top: 40px; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 20px; }
  </style>
</head>
<body>
  <h1>${report.name}</h1>
  <p><strong>As of:</strong> ${report.asOfDate}</p>
  <p><strong>Generated:</strong> ${now}</p>

  <div class="summary">
    <h2>Summary</h2>
    <p>${report.summary}</p>
    <p class="${report.balanced ? 'balanced' : 'unbalanced'}">${report.balanced ? '✓ Balanced' : '✗ Unbalanced'}</p>
  </div>

  <h2>Assets</h2>
  <table>
    <thead>
      <tr><th>Item</th><th>Amount</th></tr>
    </thead>
    <tbody>
      ${report.assets.current.map(a => `
        <tr><td>${a.name} (Current)</td><td>${a.amount.toFixed(2)}</td></tr>
      `).join('')}
      ${report.assets.fixed.map(a => `
        <tr><td>${a.name} (Fixed)</td><td>${a.amount.toFixed(2)}</td></tr>
      `).join('')}
      <tr class="total"><td>Total Assets</td><td>${report.assets.total.toFixed(2)}</td></tr>
    </tbody>
  </table>

  <h2>Liabilities</h2>
  <table>
    <thead>
      <tr><th>Item</th><th>Amount</th></tr>
    </thead>
    <tbody>
      ${report.liabilities.current.map(l => `
        <tr><td>${l.name} (Current)</td><td>${l.amount.toFixed(2)}</td></tr>
      `).join('')}
      ${report.liabilities.longTerm.map(l => `
        <tr><td>${l.name} (Long-term)</td><td>${l.amount.toFixed(2)}</td></tr>
      `).join('')}
      <tr class="total"><td>Total Liabilities</td><td>${report.liabilities.total.toFixed(2)}</td></tr>
    </tbody>
  </table>

  <h2>Equity</h2>
  <table>
    <thead>
      <tr><th>Item</th><th>Amount</th></tr>
    </thead>
    <tbody>
      ${report.equity.items.map(e => `
        <tr><td>${e.name}</td><td>${e.amount.toFixed(2)}</td></tr>
      `).join('')}
      <tr class="total"><td>Total Equity</td><td>${report.equity.total.toFixed(2)}</td></tr>
    </tbody>
  </table>

  <table>
    <tr class="total"><td>Total Liabilities + Equity</td><td>${report.totalLiabilitiesAndEquity.toFixed(2)}</td></tr>
  </table>

  <div class="footer">
    Generated by OpenClaw Reports Skill
  </div>
</body>
</html>`;
    } else {
      // Cash Flow Report
      return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${report.name}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    h1 { color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }
    h2 { color: #2c5282; margin-top: 30px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { background: #edf2f7; font-weight: 600; }
    .total { font-weight: bold; background: #f7fafc; }
    .positive { color: #38a169; }
    .negative { color: #e53e3e; }
    .summary { background: #ebf8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
    .footer { margin-top: 40px; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 20px; }
  </style>
</head>
<body>
  <h1>${report.name}</h1>
  <p><strong>Period:</strong> ${report.period} (${report.dateRange.startDate} to ${report.dateRange.endDate})</p>
  <p><strong>Generated:</strong> ${now}</p>

  <div class="summary">
    <h2>Summary</h2>
    <p>${report.summary}</p>
  </div>

  <h2>Operating Activities</h2>
  <table>
    <tr><td>Cash Inflows</td><td class="positive">+${report.operating.inflows.toFixed(2)}</td></tr>
    <tr><td>Cash Outflows</td><td class="negative">-${report.operating.outflows.toFixed(2)}</td></tr>
    <tr class="total"><td>Net Operating Cash</td><td class="${report.operating.net >= 0 ? 'positive' : 'negative'}">${report.operating.net >= 0 ? '+' : ''}${report.operating.net.toFixed(2)}</td></tr>
  </table>

  <h2>Investing Activities</h2>
  <table>
    <tr><td>Cash Inflows</td><td class="positive">+${report.investing.inflows.toFixed(2)}</td></tr>
    <tr><td>Cash Outflows</td><td class="negative">-${report.investing.outflows.toFixed(2)}</td></tr>
    <tr class="total"><td>Net Investing Cash</td><td class="${report.investing.net >= 0 ? 'positive' : 'negative'}">${report.investing.net >= 0 ? '+' : ''}${report.investing.net.toFixed(2)}</td></tr>
  </table>

  <h2>Financing Activities</h2>
  <table>
    <tr><td>Cash Inflows</td><td class="positive">+${report.financing.inflows.toFixed(2)}</td></tr>
    <tr><td>Cash Outflows</td><td class="negative">-${report.financing.outflows.toFixed(2)}</td></tr>
    <tr class="total"><td>Net Financing Cash</td><td class="${report.financing.net >= 0 ? 'positive' : 'negative'}">${report.financing.net >= 0 ? '+' : ''}${report.financing.net.toFixed(2)}</td></tr>
  </table>

  <table>
    <tr class="total"><td>Beginning Cash</td><td>${report.beginningCash.toFixed(2)}</td></tr>
    <tr class="total"><td>Net Change</td><td class="${report.netChange >= 0 ? 'positive' : 'negative'}">${report.netChange >= 0 ? '+' : ''}${report.netChange.toFixed(2)}</td></tr>
    <tr class="total"><td>Ending Cash</td><td>${report.endingCash.toFixed(2)}</td></tr>
  </table>

  <div class="footer">
    Generated by OpenClaw Reports Skill
  </div>
</body>
</html>`;
    }
  }

  /**
   * Export report to HTML file
   */
  async exportToHTML(report: PLReport | BalanceSheet | CashFlowReport, filePath?: string): Promise<string> {
    const html = this.generateHTMLReport(report);
    const outputPath = filePath || path.join(this.reportsDir, `${report.name.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}.html`);
    fs.writeFileSync(outputPath, html, 'utf-8');
    return outputPath;
  }

  /**
   * Create a scheduled report
   */
  async createScheduledReport(config: Omit<ScheduledReport, 'id' | 'createdAt'>): Promise<ScheduledReport> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    const result = await runWithResult(this.db, `
      INSERT INTO scheduled_reports (name, type, period, schedule, email_recipients, active, next_run)
      VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+1 day'))
    `, [config.name, config.type, config.period, config.schedule, config.emailRecipients, config.active ? 1 : 0]);

    return {
      id: result.lastID,
      ...config,
      createdAt: new Date().toISOString(),
    };
  }

  /**
   * Get scheduled reports
   */
  async getScheduledReports(activeOnly: boolean = false): Promise<ScheduledReport[]> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM scheduled_reports';
    const params: any[] = [];

    if (activeOnly) {
      sql += ' WHERE active = 1';
    }

    sql += ' ORDER BY created_at DESC';

    const records = await all<ScheduledReportRecord>(this.db, sql, params);

    return records.map(r => ({
      id: r.id,
      name: r.name,
      type: r.type,
      period: r.period,
      schedule: r.schedule,
      emailRecipients: r.email_recipients,
      active: r.active === 1,
      lastRun: r.last_run,
      nextRun: r.next_run,
      createdAt: r.created_at,
    }));
  }

  /**
   * Delete scheduled report
   */
  async deleteScheduledReport(id: number): Promise<void> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    await run(this.db, 'DELETE FROM scheduled_reports WHERE id = ?', [id]);
  }

  /**
   * Clear report history
   */
  async clearHistory(olderThan?: string): Promise<number> {
    await this.ensureDatabase();
    if (!this.db) throw new Error('Database not initialized');

    if (olderThan) {
      const result = await runWithResult(this.db, 'DELETE FROM report_history WHERE generated_at < ?', [olderThan]);
      return result.changes;
    } else {
      const result = await runWithResult(this.db, 'DELETE FROM report_history');
      return result.changes;
    }
  }

  /**
   * Close database connection and dependencies
   */
  async close(): Promise<void> {
    await this.ensureDatabase();
    
    if (this.db) {
      await new Promise<void>((resolve, reject) => {
        this.db!.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      });
      this.db = null;
    }

    if (this.quickbooks) {
      await this.quickbooks.close();
      this.quickbooks = null;
    }

    if (this.receiptsOcr) {
      await this.receiptsOcr.close();
      this.receiptsOcr = null;
    }
  }
}

export default ReportsSkill;
