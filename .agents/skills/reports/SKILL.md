---
name: reports
description: Generate financial reports (P&L, Balance Sheet, Cash Flow)
version: 1.0.0
author: OpenClaw
dependencies:
  - quickbooks
  - receipts-ocr
---

# Reports Skill

Generate comprehensive financial reports including Profit & Loss statements, Balance Sheets, and Cash Flow reports.

## Overview

This skill aggregates data from QuickBooks (invoices, customers, transactions) and Receipts OCR (expense tracking) to generate professional financial reports suitable for business analysis, tax preparation, and investor presentations.

## Capabilities

- **P&L Reports**: Track revenue, expenses, and profitability over time
- **Balance Sheets**: Snapshot of assets, liabilities, and equity
- **Cash Flow Reports**: Monitor cash movement across operating, investing, and financing activities
- **PDF Export**: Generate HTML reports ready for PDF conversion
- **Scheduled Reports**: Automate report generation

## Installation

```bash
cd skills/reports
npm install
npm run build
```

## Usage

### CLI

```bash
# Check dependencies health
npm run cli -- status

# Generate P&L Report
npm run cli -- pl monthly 2024 1    # January 2024
npm run cli -- pl quarterly 2024    # Q1 2024

# Generate Balance Sheet
npm run cli -- balance              # As of today
npm run cli -- balance 2024-01-31   # As of specific date

# Generate Cash Flow Report
npm run cli -- cashflow monthly 2024 1

# Export to HTML
npm run cli -- export pl ./my-report.html --period yearly --year 2024

# View report history
npm run cli -- history pl 10

# Schedule reports
npm run cli -- schedule create "Monthly P&L" pl monthly monthly
npm run cli -- schedule list
```

### Library

```typescript
import { ReportsSkill } from '@openclaw/reports';

const reports = new ReportsSkill();

// Generate P&L Report
const plReport = await reports.generatePLReport({
  period: 'monthly',
  year: 2024,
  month: 0,  // January
});

console.log(`Revenue: ${plReport.revenue.total}`);
console.log(`Expenses: ${plReport.expenses.total}`);
console.log(`Net Income: ${plReport.netIncome}`);

// Generate Balance Sheet
const balanceSheet = await reports.generateBalanceSheet({
  asOfDate: '2024-01-31',
});

console.log(`Total Assets: ${balanceSheet.assets.total}`);
console.log(`Total Liabilities: ${balanceSheet.liabilities.total}`);
console.log(`Equity: ${balanceSheet.equity.total}`);

// Generate Cash Flow Report
const cashFlow = await reports.generateCashFlowReport({
  period: 'quarterly',
  year: 2024,
});

console.log(`Operating Cash Flow: ${cashFlow.operating.net}`);
console.log(`Free Cash Flow: ${cashFlow.operating.net + cashFlow.investing.net}`);

// Export to HTML
const htmlPath = await reports.exportToHTML(plReport, './pl-report.html');

// Close connections
await reports.close();
```

## Data Sources

### QuickBooks Integration
- **Invoices**: Revenue data with customer breakdown
- **Customers**: Accounts receivable tracking
- **Transactions**: Cash flow categorization

### Receipts OCR Integration
- **Confirmed Receipts**: Expense categorization
- **Merchant Data**: Expense vendor breakdown
- **Categories**: Automated expense classification

## Report Formats

### P&L Report Structure
```typescript
{
  name: string;
  period: 'monthly' | 'quarterly' | 'yearly';
  dateRange: { startDate: string; endDate: string };
  revenue: {
    total: number;
    byCategory: [{ category: string; amount: number; percentage: number }];
  };
  expenses: {
    total: number;
    byCategory: [{ category: string; amount: number; percentage: number }];
  };
  grossProfit: number;
  netIncome: number;
  margin: number;
}
```

### Balance Sheet Structure
```typescript
{
  name: string;
  asOfDate: string;
  assets: {
    current: [{ name: string; amount: number }];
    fixed: [{ name: string; amount: number }];
    totalCurrent: number;
    totalFixed: number;
    total: number;
  };
  liabilities: {
    current: [{ name: string; amount: number }];
    longTerm: [{ name: string; amount: number }];
    totalCurrent: number;
    totalLongTerm: number;
    total: number;
  };
  equity: {
    items: [{ name: string; amount: number }];
    total: number;
  };
  balanced: boolean;  // Assets = Liabilities + Equity
}
```

### Cash Flow Structure
```typescript
{
  name: string;
  period: 'monthly' | 'quarterly' | 'yearly';
  operating: { inflows: number; outflows: number; net: number };
  investing: { inflows: number; outflows: number; net: number };
  financing: { inflows: number; outflows: number; net: number };
  beginningCash: number;
  endingCash: number;
  netChange: number;
}
```

## Scheduled Reports

Automate report generation on a recurring schedule:

```typescript
// Create a scheduled report
const scheduled = await reports.createScheduledReport({
  name: 'Monthly P&L',
  type: 'pl',
  period: 'monthly',
  schedule: 'monthly',  // daily, weekly, monthly
  active: true,
});

// List scheduled reports
const schedules = await reports.getScheduledReports(true);  // active only

// Delete scheduled report
await reports.deleteScheduledReport(scheduledId);
```

## Report History

Track all generated reports:

```typescript
// Get recent P&L reports
const history = await reports.getReportHistory('pl', 10);

// Clear old history
const deleted = await reports.clearHistory('2024-01-01');
```

## HTML Export

Reports are exported as professionally styled HTML files ready for PDF conversion:

```typescript
const html = reports.generateHTMLReport(plReport);
const filePath = await reports.exportToHTML(plReport, './report.html');
```

HTML features:
- Professional styling with CSS
- Responsive design
- Color-coded positive/negative values
- Summary sections with key metrics
- Detailed breakdown tables

## Configuration

Store data in custom location:

```typescript
const reports = new ReportsSkill({
  dataDir: '/custom/path/to/reports',
  quickbooksProfile: 'business',  // QuickBooks profile to use
  receiptsProfile: 'default',     // Receipts OCR profile to use
});
```

## Dependencies

- `@openclaw/quickbooks`: For invoice and transaction data
- `@openclaw/receipts-ocr`: For expense tracking
- `sqlite3`: Local storage for report history and scheduled reports

## Limitations

- Requires QuickBooks connection for invoice/revenue data
- Requires Receipts OCR for comprehensive expense categorization
- Fixed assets must be tracked externally (not in QuickBooks integration)
- Cash flow beginning balance is estimated based on historical data

## File Locations

- Data: `~/.openclaw/skills/reports/`
- Reports: `~/.openclaw/skills/reports/reports/`
- Database: `~/.openclaw/skills/reports/reports.db`
