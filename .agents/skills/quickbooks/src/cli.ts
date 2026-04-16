#!/usr/bin/env node
/**
 * QuickBooks Skill CLI
 */

import { QuickBooksSkill, SyncResult } from './index';

const args = process.argv.slice(2);
const command = args[0];

function formatSyncResult(result: SyncResult): string {
  const lines = [
    `${result.entityType}:`,
    `  Created: ${result.created}`,
    `  Updated: ${result.updated}`,
    `  Conflicts: ${result.conflicts}`,
  ];
  if (result.errors.length > 0) {
    lines.push(`  Errors: ${result.errors.length}`);
    result.errors.slice(0, 3).forEach(e => lines.push(`    - ${e}`));
    if (result.errors.length > 3) {
      lines.push(`    ... and ${result.errors.length - 3} more`);
    }
  }
  return lines.join('\n');
}

async function main() {
  const skill = new QuickBooksSkill();

  try {
    switch (command) {
      case 'status': {
        const status = await skill.getStatus();
        console.log('QuickBooks Connection Status');
        console.log('============================');
        console.log(`Connected: ${status.connected ? 'Yes' : 'No'}`);
        console.log(`Profile: ${status.profile}`);
        console.log(`Realm ID: ${status.realmId || 'Not connected'}`);
        console.log(`Environment: ${status.environment}`);
        break;
      }

      case 'health': {
        const health = await skill.healthCheck();
        console.log('QuickBooks Health Check');
        console.log('=======================');
        console.log(`Status: ${health.status}`);
        if (health.realmId) console.log(`Realm ID: ${health.realmId}`);
        if (health.message) console.log(`Message: ${health.message}`);
        process.exit(health.status === 'healthy' ? 0 : 1);
      }

      case 'customers': {
        const shouldSync = args.includes('--sync');
        const limitIndex = args.indexOf('--limit');
        const limit = limitIndex >= 0 ? parseInt(args[limitIndex + 1]) || 50 : 50;

        if (shouldSync) {
          console.log('Syncing customers from QuickBooks...');
          const result = await skill.syncCustomers();
          console.log(formatSyncResult(result));
        }

        const customers = await skill.getCustomers(limit);
        console.log(`\nCustomers (${customers.length}):`);
        console.log('='.repeat(80));
        console.log(`${'ID'.padEnd(6)} ${'QB ID'.padEnd(15)} ${'Name'.padEnd(30)} ${'Email'.padEnd(25)} ${'Balance'.padEnd(10)}`);
        console.log('-'.repeat(80));
        customers.forEach(c => {
          console.log(
            `${String(c.id).padEnd(6)} ${c.qbId.padEnd(15)} ${c.displayName.slice(0, 30).padEnd(30)} ` +
            `${(c.email || '').slice(0, 25).padEnd(25)} ${String(c.balance || 0).padEnd(10)}`
          );
        });
        break;
      }

      case 'customer-get': {
        const id = args[1];
        if (!id) {
          console.error('Usage: quickbooks customer-get <id>');
          process.exit(1);
        }

        const customer = await skill.getCustomer(id);
        if (!customer) {
          console.error(`Customer not found: ${id}`);
          process.exit(1);
        }

        console.log('Customer Details');
        console.log('================');
        console.log(`ID: ${customer.id}`);
        console.log(`QB ID: ${customer.qbId}`);
        console.log(`Display Name: ${customer.displayName}`);
        console.log(`Given Name: ${customer.givenName || 'N/A'}`);
        console.log(`Family Name: ${customer.familyName || 'N/A'}`);
        console.log(`Company: ${customer.companyName || 'N/A'}`);
        console.log(`Email: ${customer.email || 'N/A'}`);
        console.log(`Phone: ${customer.phone || 'N/A'}`);
        console.log(`Address: ${customer.address || ''} ${customer.city || ''} ${customer.country || ''}`);
        console.log(`Balance: ${customer.balance || 0}`);
        console.log(`Active: ${customer.active ? 'Yes' : 'No'}`);
        console.log(`Last Synced: ${customer.lastSyncedAt || 'Never'}`);
        break;
      }

      case 'customer-sync': {
        console.log('Syncing customers from QuickBooks...');
        const result = await skill.syncCustomers();
        console.log(formatSyncResult(result));
        break;
      }

      case 'invoices': {
        const shouldSync = args.includes('--sync');
        const limitIndex = args.indexOf('--limit');
        const limit = limitIndex >= 0 ? parseInt(args[limitIndex + 1]) || 50 : 50;
        const statusIndex = args.indexOf('--status');
        const status = statusIndex >= 0 ? args[statusIndex + 1] : undefined;

        if (shouldSync) {
          console.log('Syncing invoices from QuickBooks...');
          const result = await skill.syncInvoices();
          console.log(formatSyncResult(result));
        }

        const invoices = await skill.getInvoices(limit, status);
        console.log(`\nInvoices (${invoices.length}):`);
        console.log('='.repeat(100));
        console.log(`${'ID'.padEnd(6)} ${'Doc #'.padEnd(12)} ${'Date'.padEnd(12)} ${'Customer'.padEnd(25)} ${'Status'.padEnd(10)} ${'Total'.padEnd(12)} ${'Balance'.padEnd(12)}`);
        console.log('-'.repeat(100));
        invoices.forEach(i => {
          console.log(
            `${String(i.id).padEnd(6)} ${i.docNumber.padEnd(12)} ${i.txnDate.padEnd(12)} ` +
            `${(i.customerName || 'Unknown').slice(0, 25).padEnd(25)} ${i.status.padEnd(10)} ` +
            `${String(i.totalAmount).padEnd(12)} ${String(i.balance).padEnd(12)}`
          );
        });
        break;
      }

      case 'invoice-get': {
        const id = args[1];
        if (!id) {
          console.error('Usage: quickbooks invoice-get <id>');
          process.exit(1);
        }

        const invoice = await skill.getInvoice(id);
        if (!invoice) {
          console.error(`Invoice not found: ${id}`);
          process.exit(1);
        }

        console.log('Invoice Details');
        console.log('===============');
        console.log(`ID: ${invoice.id}`);
        console.log(`QB ID: ${invoice.qbId}`);
        console.log(`Document Number: ${invoice.docNumber}`);
        console.log(`Transaction Date: ${invoice.txnDate}`);
        console.log(`Due Date: ${invoice.dueDate || 'N/A'}`);
        console.log(`Customer: ${invoice.customerName || 'Unknown'} (ID: ${invoice.customerId})`);
        console.log(`Status: ${invoice.status}`);
        console.log(`Total Amount: ${invoice.totalAmount}`);
        console.log(`Balance: ${invoice.balance}`);
        console.log(`Private Note: ${invoice.privateNote || 'N/A'}`);
        console.log(`Last Synced: ${invoice.lastSyncedAt || 'Never'}`);

        if (invoice.lineItems.length > 0) {
          console.log('\nLine Items:');
          console.log('-'.repeat(80));
          console.log(`${'Description'.padEnd(40)} ${'Qty'.padEnd(10)} ${'Price'.padEnd(12)} ${'Amount'.padEnd(12)}`);
          console.log('-'.repeat(80));
          invoice.lineItems.forEach(line => {
            console.log(
              `${(line.description || '').slice(0, 40).padEnd(40)} ` +
              `${String(line.quantity || '').padEnd(10)} ` +
              `${String(line.unitPrice || '').padEnd(12)} ` +
              `${String(line.amount).padEnd(12)}`
            );
          });
        }
        break;
      }

      case 'invoice-sync': {
        const sinceIndex = args.indexOf('--since');
        const since = sinceIndex >= 0 ? args[sinceIndex + 1] : undefined;

        console.log('Syncing invoices from QuickBooks...');
        if (since) console.log(`Since: ${since}`);
        const result = await skill.syncInvoices(since);
        console.log(formatSyncResult(result));
        break;
      }

      case 'transactions': {
        const shouldSync = args.includes('--sync');
        const limitIndex = args.indexOf('--limit');
        const limit = limitIndex >= 0 ? parseInt(args[limitIndex + 1]) || 50 : 50;
        const typeIndex = args.indexOf('--type');
        const type = typeIndex >= 0 ? args[typeIndex + 1] : undefined;

        if (shouldSync) {
          console.log('Syncing transactions from QuickBooks...');
          const result = await skill.syncTransactions();
          console.log(formatSyncResult(result));
        }

        const transactions = await skill.getTransactions(limit, type);
        console.log(`\nTransactions (${transactions.length}):`);
        console.log('='.repeat(90));
        console.log(`${'ID'.padEnd(6)} ${'Type'.padEnd(15)} ${'Date'.padEnd(12)} ${'Entity'.padEnd(25)} ${'Amount'.padEnd(15)}`);
        console.log('-'.repeat(90));
        transactions.forEach(t => {
          console.log(
            `${String(t.id).padEnd(6)} ${t.txnType.padEnd(15)} ${t.txnDate.padEnd(12)} ` +
            `${(t.entityName || 'N/A').slice(0, 25).padEnd(25)} ${String(t.amount).padEnd(15)}`
          );
        });
        break;
      }

      case 'transaction-sync': {
        console.log('Syncing transactions from QuickBooks...');
        const result = await skill.syncTransactions();
        console.log(formatSyncResult(result));
        break;
      }

      case 'sync': {
        const customersOnly = args.includes('--customers');
        const invoicesOnly = args.includes('--invoices');
        const transactionsOnly = args.includes('--transactions');

        const options: any = {};
        if (customersOnly || invoicesOnly || transactionsOnly) {
          options.customers = customersOnly;
          options.invoices = invoicesOnly;
          options.transactions = transactionsOnly;
        }

        console.log('Running full sync with QuickBooks...');
        console.log('====================================\n');

        const results = await skill.fullSync(options);
        results.forEach(result => {
          console.log(formatSyncResult(result));
          console.log();
        });

        const totalCreated = results.reduce((sum, r) => sum + r.created, 0);
        const totalUpdated = results.reduce((sum, r) => sum + r.updated, 0);
        const totalConflicts = results.reduce((sum, r) => sum + r.conflicts, 0);

        console.log('Sync Summary');
        console.log('============');
        console.log(`Total Created: ${totalCreated}`);
        console.log(`Total Updated: ${totalUpdated}`);
        console.log(`Total Conflicts: ${totalConflicts}`);
        break;
      }

      case 'conflicts': {
        const conflicts = await skill.getConflicts();
        if (conflicts.length === 0) {
          console.log('No unresolved conflicts.');
          break;
        }

        console.log(`Unresolved Conflicts (${conflicts.length}):`);
        console.log('='.repeat(100));
        console.log(`${'ID'.padEnd(6)} ${'Type'.padEnd(15)} ${'Entity ID'.padEnd(20)} ${'Created At'.padEnd(25)}`);
        console.log('-'.repeat(100));
        conflicts.forEach(c => {
          console.log(
            `${String(c.id).padEnd(6)} ${c.entityType.padEnd(15)} ${c.entityId.padEnd(20)} ${(c.createdAt || '').padEnd(25)}`
          );
        });
        console.log('\nTo resolve: quickbooks conflict-resolve <id> --use <local|remote>');
        break;
      }

      case 'conflict-resolve': {
        const conflictId = parseInt(args[1]);
        const useIndex = args.indexOf('--use');
        const resolution = useIndex >= 0 ? args[useIndex + 1] : undefined;

        if (!conflictId || !resolution || (resolution !== 'local' && resolution !== 'remote')) {
          console.error('Usage: quickbooks conflict-resolve <id> --use <local|remote>');
          process.exit(1);
        }

        const success = await skill.resolveConflict(conflictId, resolution);
        if (success) {
          console.log(`Conflict ${conflictId} resolved. Keeping ${resolution} version.`);
        } else {
          console.error(`Failed to resolve conflict ${conflictId}`);
          process.exit(1);
        }
        break;
      }

      case 'sync-state': {
        const states = await skill.getSyncState();
        if (states.length === 0) {
          console.log('No sync state recorded yet. Run a sync first.');
          break;
        }

        console.log('Sync State');
        console.log('==========');
        console.log(`${'Entity Type'.padEnd(20)} ${'Last Sync'.padEnd(25)} ${'Records'.padEnd(10)}`);
        console.log('-'.repeat(60));
        states.forEach(s => {
          console.log(
            `${s.entityType.padEnd(20)} ${s.lastSyncTime.padEnd(25)} ${String(s.recordCount).padEnd(10)}`
          );
        });
        break;
      }

      case 'help':
      default: {
        console.log('QuickBooks Skill CLI');
        console.log('====================');
        console.log();
        console.log('Connection Commands:');
        console.log('  status                    Check connection status');
        console.log('  health                    Health check for QuickBooks connection');
        console.log();
        console.log('Customer Commands:');
        console.log('  customers [--sync]        List customers');
        console.log('  customer-get <id>         Get customer details');
        console.log('  customer-sync             Sync customers from QuickBooks');
        console.log();
        console.log('Invoice Commands:');
        console.log('  invoices [--sync]         List invoices');
        console.log('  invoice-get <id>          Get invoice details');
        console.log('  invoice-sync [--since <date>]  Sync invoices from QuickBooks');
        console.log();
        console.log('Transaction Commands:');
        console.log('  transactions [--sync]     List transactions');
        console.log('  transaction-sync          Sync transactions from QuickBooks');
        console.log();
        console.log('Sync Commands:');
        console.log('  sync [--customers] [--invoices] [--transactions]  Full sync');
        console.log('  conflicts                 List unresolved conflicts');
        console.log('  conflict-resolve <id> --use <local|remote>  Resolve conflict');
        console.log('  sync-state                Show last sync times');
        console.log();
        console.log('Options:');
        console.log('  --sync                    Sync from QuickBooks before listing');
        console.log('  --limit <n>               Limit results (default: 50)');
        console.log('  --status <status>         Filter by status');
        console.log('  --since <YYYY-MM-DD>      Sync only records since date');
      }
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  } finally {
    await skill.close();
  }
}

main();
