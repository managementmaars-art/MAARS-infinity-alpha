---
name: invoices
description: "Create, manage, and track professional invoices"
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# Invoices Skill

Create professional PDF invoices, track payments, and manage client billing.

## Capabilities

- `create <client-id>` - Create a new invoice with line items
  - Options:
    - `--desc "Description, qty, price"` - Add line item (can use multiple times)
    - `--tax <rate>` - Tax rate percentage
    - `--due <days>` - Due in N days
    - `--notes <text>` - Invoice notes
    - `--terms <text>` - Payment terms
  - Example: `invoices create 1 --desc "Consulting, 10, 150" --desc "Design, 5, 200" --tax 10`

- `list [status]` - List invoices with optional filter
  - Status: all, draft, sent, paid, overdue, cancelled
  - Example: `invoices list sent`

- `get <id>` - Show invoice details
  - Returns: Full invoice with line items and payments
  - Example: `invoices get 1`

- `get-number <number>` - Get invoice by invoice number
  - Example: `invoices get-number INV-0001`

- `send <id>` - Mark invoice as sent
  - Example: `invoices send 1`

- `pay <invoice-id> <amount>` - Record a payment
  - Options:
    - `--method <method>` - Payment method
    - `--notes <text>` - Payment notes
    - `--date <YYYY-MM-DD>` - Payment date
  - Example: `invoices pay 1 500 --method "Bank Transfer"`

- `pdf <id>` - Generate PDF for invoice
  - Returns: Path to HTML file (convert to PDF with your tool)
  - Example: `invoices pdf 1`

- `update <id>` - Update invoice
  - Options: `--status`, `--notes`, `--terms`
  - Example: `invoices update 1 --status sent`

- `items-update <invoice-id>` - Update line items
  - Options: `--desc "Description, qty, price"` (replaces all items)
  - Example: `invoices items-update 1 --desc "New Item 1, 2, 100"`

- `cancel <id>` - Cancel an invoice
  - Example: `invoices cancel 1`

- `delete <id>` - Delete an invoice
  - Example: `invoices delete 1`

- `export [status]` - Export invoices to CSV
  - Example: `invoices export paid`

- `summary` - Generate invoice summary report
  - Returns: Revenue, outstanding, paid amounts by status
  - Example: `invoices summary`

- `overdue` - List overdue invoices
  - Automatically updates status for past-due invoices
  - Example: `invoices overdue`

## Client Management

- `client-list` - List all clients
  - Example: `invoices client-list`

- `client-add <name>` - Add a new client
  - Options: `--email`, `--address`, `--phone`, `--tax-id`
  - Example: `invoices client-add "Acme Corp" --email billing@acme.com`

- `client-get <id>` - Show client details
  - Example: `invoices client-get 1`

- `client-update <id>` - Update client
  - Options: `--name`, `--email`, `--address`, `--phone`, `--tax-id`
  - Example: `invoices client-update 1 --email new@acme.com`

- `client-delete <id>` - Delete client
  - Example: `invoices client-delete 1`

- `client-invoices <id>` - List invoices for a client
  - Example: `invoices client-invoices 1`

## Configuration

- `config` - Show business configuration
  - Example: `invoices config`

- `config-set <key> <value>` - Update configuration
  - Keys: `name`, `email`, `phone`, `address`, `taxId`, `defaultTaxRate`, `defaultTerms`, `defaultDueDays`, `invoicePrefix`
  - Example: `invoices config-set name "My Company"`
  - Example: `invoices config-set defaultTaxRate 10`

## Setup

Configure your business details:
```bash
npm run cli -- config-set name "My Company"
npm run cli -- config-set email "billing@example.com"
npm run cli -- config-set defaultTaxRate 10
```

Add clients:
```bash
npm run cli -- client-add "Acme Corp" --email billing@acme.com
```

Create your first invoice:
```bash
npm run cli -- create 1 --desc "Consulting Services, 10, 150" --desc "Design Work, 5, 200"
```

## Storage

SQLite database at `~/.openclaw/skills/invoices/invoices.db`:
- `config` - Business settings (name, tax rate, terms, etc.)
- `clients` - Client information
- `invoices` - Invoice records with totals and status
- `line_items` - Individual line items per invoice
- `payments` - Payment records per invoice

PDF templates generated at `~/.openclaw/skills/invoices/pdfs/`:
- HTML files ready for PDF conversion
- Use puppeteer, wkhtmltopdf, or browser print to convert

## Invoice Status Flow

```
draft → sent → paid
           ↘ overdue (auto-detected)
           ↘ cancelled (manual)
```

Auto-detection: Invoices automatically become overdue when past their due date while in "sent" status.

## Payment Tracking

- Record partial or full payments
- Automatic balance calculation
- Payment history per invoice
- Status updates to "paid" when fully paid

## Features

- **Professional PDF Generation**: HTML templates with CSS styling
- **Tax Calculation**: Configurable tax rate per invoice
- **Multi-Currency Support**: Store amounts in any currency (display as $)
- **Client Database**: Track client information and history
- **Payment Tracking**: Record and manage partial payments
- **Overdue Detection**: Automatic status updates
- **CSV Export**: Export data for accounting software
- **Reporting**: Revenue and outstanding amounts summary
