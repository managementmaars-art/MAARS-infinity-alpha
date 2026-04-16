---
name: quickbooks
description: "QuickBooks Online integration for accounting sync - sync customers, invoices, and transactions with two-way sync and conflict resolution"
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# QuickBooks Skill

Sync with QuickBooks Online for accounting integration. Supports customers, invoices, and transactions with two-way sync and conflict resolution.

## Capabilities

- `status` - Check connection status
  - Example: `quickbooks status`

- `health` - Health check for QuickBooks connection
  - Example: `quickbooks health`

- `customers` - List customers from QuickBooks
  - Options: `--sync` to sync from QuickBooks, `--limit <n>`
  - Example: `quickbooks customers --sync`

- `customer-get <id>` - Get customer details
  - Example: `quickbooks customer-get 123`

- `customer-sync` - Sync all customers from QuickBooks
  - Example: `quickbooks customer-sync`

- `invoices` - List invoices from QuickBooks
  - Options: `--sync` to sync, `--limit <n>`, `--status <status>`
  - Example: `quickbooks invoices --sync --limit 50`

- `invoice-get <id>` - Get invoice details
  - Example: `quickbooks invoice-get 456`

- `invoice-sync` - Sync all invoices from QuickBooks
  - Options: `--since <date>` to sync only recent invoices
  - Example: `quickbooks invoice-sync --since 2024-01-01`

- `transactions` - List transactions
  - Options: `--sync`, `--limit <n>`, `--type <type>`
  - Example: `quickbooks transactions --sync`

- `transaction-sync` - Sync all transactions
  - Example: `quickbooks transaction-sync`

- `sync` - Full sync (customers, invoices, transactions)
  - Options: `--customers`, `--invoices`, `--transactions` to sync only specific types
  - Example: `quickbooks sync`

- `conflicts` - List sync conflicts
  - Example: `quickbooks conflicts`

- `conflict-resolve <id>` - Resolve a conflict
  - Options: `--use <local|remote>` which version to keep
  - Example: `quickbooks conflict-resolve 1 --use remote`

- `push-customer <local-id>` - Push local customer to QuickBooks
  - Example: `quickbooks push-customer 5`

- `push-invoice <local-id>` - Push local invoice to QuickBooks
  - Example: `quickbooks push-invoice 10`

## Setup

```bash
# First, set up quickbooks-auth skill
node ../quickbooks-auth/dist/cli.js connect mycompany

# Build this skill
npm install
npm run build

# Check status
npm run cli -- status
```

## Storage

SQLite database at `~/.openclaw/skills/quickbooks/quickbooks.db`:
- `customers` - Synced customer data from QuickBooks
- `invoices` - Synced invoice data
- `transactions` - Synced transaction data
- `sync_state` - Last sync timestamps and sync tokens
- `conflicts` - Unresolved sync conflicts

## Sync Strategy

### Two-Way Sync
- Changes from QuickBooks are pulled to local database
- Local changes can be pushed to QuickBooks
- Conflict detection based on `last_updated` timestamps

### Conflict Resolution
When the same record is modified in both QuickBooks and locally:
1. Conflict is recorded in conflicts table
2. User must resolve with `conflict-resolve`
3. Options: keep local, keep remote, or merge

### Incremental Sync
- Uses `last_sync_time` to fetch only changes since last sync
- Reduces API calls and sync time

## API Limits

QuickBooks Online API has rate limits:
- 500 requests per minute per realm
- Sync operations batch requests to stay within limits
