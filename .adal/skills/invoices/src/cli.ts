#!/usr/bin/env node
/**
 * Invoices Skill CLI
 * Command-line interface for invoice management
 */

import { InvoicesSkill, getInvoicesSkill, InvoiceStatus, LineItem } from './index';
import * as fs from 'fs';

const USAGE = `
Invoices Skill - Create, manage, and track professional invoices

Usage: invoices <command> [options]

Configuration Commands:
  config                    Show current business configuration
  config-set <key> <value>  Update business configuration
                            Keys: name, email, phone, address, taxId, 
                                  defaultTaxRate, defaultTerms, defaultDueDays,
                                  invoicePrefix

Client Commands:
  client-list               List all clients
  client-add <name>         Add a new client
    --email <email>         Client email
    --address <address>     Client address
    --phone <phone>         Client phone
    --tax-id <id>           Client tax ID
  client-get <id>           Get client details
  client-update <id>        Update client
    --name, --email, --address, --phone, --tax-id
  client-delete <id>        Delete client
  client-invoices <id>      List invoices for client

Invoice Commands:
  list [status]             List invoices (all, draft, sent, paid, overdue, cancelled)
  create <client-id>        Create new invoice
    --desc "Item 1, 2, 100" Add line item (can be used multiple times)
    --tax <rate>            Tax rate percentage (default: from config)
    --due <days>            Due in N days (default: from config)
    --notes <text>          Invoice notes
    --terms <text>          Payment terms
  get <id>                  Get invoice details
  get-number <number>       Get invoice by invoice number
  update <id>               Update invoice
    --status <status>       Update status
    --notes <text>          Update notes
    --terms <text>          Update terms
  delete <id>               Delete invoice
  send <id>                 Mark invoice as sent
  cancel <id>               Cancel invoice

Line Item Commands:
  items-update <invoice-id> Update line items
    --desc "Item 1, 2, 100" Replace all items (can be used multiple times)

Payment Commands:
  pay <invoice-id> <amount> Record payment
    --method <method>       Payment method
    --notes <text>          Payment notes
    --date <YYYY-MM-DD>     Payment date (default: today)
  payment-delete <id>       Delete a payment

PDF/Export Commands:
  pdf <id>                  Generate PDF for invoice
  export [status]           Export invoices to CSV

Report Commands:
  summary                   Show invoice summary report
  overdue                   List overdue invoices

Other Commands:
  status                    Check connection status
  health                    Run health check
  help                      Show this help message

Examples:
  invoices config-set name "Acme Corp"
  invoices config-set defaultTaxRate 10
  
  invoices client-add "John Doe" --email john@example.com
  
  invoices create 1 --desc "Consulting, 10, 150" --desc "Design, 5, 200" --tax 10
  invoices list sent
  invoices get 1
  invoices send 1
  invoices pay 1 1500 --method "Bank Transfer"
  invoices pdf 1
  invoices overdue
`;

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const skill = getInvoicesSkill();

  // Helper to parse options
  function getOption(name: string): string | undefined {
    const idx = args.indexOf(name);
    return idx !== -1 && args[idx + 1] ? args[idx + 1] : undefined;
  }

  function getOptions(name: string): string[] {
    const values: string[] = [];
    for (let i = 0; i < args.length; i++) {
      if (args[i] === name && args[i + 1]) {
        values.push(args[i + 1]);
      }
    }
    return values;
  }

  try {
    switch (command) {
      // Configuration commands
      case 'config': {
        const config = await skill.getConfig();
        console.log('\nBusiness Configuration:');
        console.log('─'.repeat(50));
        console.log(`Name:             ${config.name}`);
        console.log(`Email:            ${config.email || '(not set)'}`);
        console.log(`Phone:            ${config.phone || '(not set)'}`);
        console.log(`Address:          ${config.address ? config.address.replace(/\n/g, ' | ') : '(not set)'}`);
        console.log(`Tax ID:           ${config.taxId || '(not set)'}`);
        console.log(`Default Tax Rate: ${config.defaultTaxRate}%`);
        console.log(`Default Terms:    ${config.defaultTerms}`);
        console.log(`Default Due Days: ${config.defaultDueDays}`);
        console.log(`Invoice Prefix:   ${config.invoicePrefix}`);
        console.log(`Next Number:      ${config.nextInvoiceNumber}`);
        console.log('─'.repeat(50));
        break;
      }

      case 'config-set': {
        const key = args[1];
        const value = args[2];
        if (!key || value === undefined) {
          console.error('Error: Key and value required');
          console.error('Usage: invoices config-set <key> <value>');
          process.exit(1);
        }

        const updates: Record<string, any> = {};
        switch (key) {
          case 'name': updates.name = value; break;
          case 'email': updates.email = value; break;
          case 'phone': updates.phone = value; break;
          case 'address': updates.address = value; break;
          case 'taxId': updates.taxId = value; break;
          case 'defaultTaxRate': updates.defaultTaxRate = parseFloat(value); break;
          case 'defaultTerms': updates.defaultTerms = value; break;
          case 'defaultDueDays': updates.defaultDueDays = parseInt(value); break;
          case 'invoicePrefix': updates.invoicePrefix = value; break;
          default:
            console.error(`Error: Unknown config key: ${key}`);
            process.exit(1);
        }

        await skill.updateConfig(updates);
        console.log(`✓ Updated ${key} to: ${value}`);
        break;
      }

      // Client commands
      case 'client-list': {
        const clients = await skill.listClients();
        if (clients.length === 0) {
          console.log('No clients found. Use client-add to create one.');
        } else {
          console.log('\nClients:');
          console.log('─'.repeat(80));
          console.log(`${'ID'.padStart(4)} ${'Name'.padEnd(25)} ${'Email'.padEnd(25)} ${'Phone'.padEnd(15)}`);
          console.log('─'.repeat(80));
          for (const c of clients) {
            console.log(`${c.id!.toString().padStart(4)} ${c.name.padEnd(25)} ${(c.email || '').padEnd(25)} ${(c.phone || '').padEnd(15)}`);
          }
          console.log('─'.repeat(80));
        }
        break;
      }

      case 'client-add': {
        const name = args[1];
        if (!name) {
          console.error('Error: Client name required');
          console.error('Usage: invoices client-add <name> [--email ...] [--address ...]');
          process.exit(1);
        }

        const client = await skill.createClient({
          name,
          email: getOption('--email'),
          address: getOption('--address'),
          phone: getOption('--phone'),
          taxId: getOption('--tax-id'),
        });

        console.log(`✓ Created client: ${client.name} (ID: ${client.id})`);
        break;
      }

      case 'client-get': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid client ID required');
          process.exit(1);
        }

        const client = await skill.getClient(id);
        if (!client) {
          console.log('Client not found');
        } else {
          console.log('\nClient Details:');
          console.log('─'.repeat(50));
          console.log(`ID:      ${client.id}`);
          console.log(`Name:    ${client.name}`);
          console.log(`Email:   ${client.email || '(not set)'}`);
          console.log(`Phone:   ${client.phone || '(not set)'}`);
          console.log(`Address: ${client.address ? client.address.replace(/\n/g, ' | ') : '(not set)'}`);
          console.log(`Tax ID:  ${client.taxId || '(not set)'}`);
          console.log(`Notes:   ${client.notes || '(not set)'}`);
          console.log(`Created: ${client.createdAt}`);
          console.log('─'.repeat(50));
        }
        break;
      }

      case 'client-update': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid client ID required');
          process.exit(1);
        }

        const updates: any = {};
        if (getOption('--name')) updates.name = getOption('--name');
        if (getOption('--email')) updates.email = getOption('--email');
        if (getOption('--address')) updates.address = getOption('--address');
        if (getOption('--phone')) updates.phone = getOption('--phone');
        if (getOption('--tax-id')) updates.taxId = getOption('--tax-id');

        if (Object.keys(updates).length === 0) {
          console.error('Error: At least one field to update required');
          process.exit(1);
        }

        await skill.updateClient(id, updates);
        console.log('✓ Client updated');
        break;
      }

      case 'client-delete': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid client ID required');
          process.exit(1);
        }

        await skill.deleteClient(id);
        console.log('✓ Client deleted');
        break;
      }

      case 'client-invoices': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid client ID required');
          process.exit(1);
        }

        const invoices = await skill.getClientInvoices(id);
        if (invoices.length === 0) {
          console.log('No invoices found for this client.');
        } else {
          printInvoices(invoices);
        }
        break;
      }

      // Invoice commands
      case 'list': {
        const status = args[1] as InvoiceStatus | undefined;
        const validStatuses: InvoiceStatus[] = ['draft', 'sent', 'paid', 'overdue', 'cancelled'];
        
        if (status && !validStatuses.includes(status)) {
          console.error(`Error: Invalid status. Valid: ${validStatuses.join(', ')}`);
          process.exit(1);
        }

        const invoices = await skill.listInvoices(status ? { status } : {});
        printInvoices(invoices);
        break;
      }

      case 'create': {
        const clientId = parseInt(args[1]);
        if (isNaN(clientId)) {
          console.error('Error: Valid client ID required');
          console.error('Usage: invoices create <client-id> --desc "Item, qty, price"');
          process.exit(1);
        }

        const descOptions = getOptions('--desc');
        if (descOptions.length === 0) {
          console.error('Error: At least one line item required (--desc "Description, qty, price")');
          process.exit(1);
        }

        const lineItems: Omit<LineItem, 'id' | 'amount'>[] = descOptions.map(desc => {
          const parts = desc.split(',').map(s => s.trim());
          if (parts.length < 3) {
            throw new Error(`Invalid line item format: ${desc}. Use: "Description, qty, price"`);
          }
          return {
            description: parts[0],
            quantity: parseFloat(parts[1]),
            unitPrice: parseFloat(parts[2]),
          };
        });

        const invoice = await skill.createInvoice(clientId, lineItems, {
          taxRate: getOption('--tax') ? parseFloat(getOption('--tax')!) : undefined,
          dueDate: getOption('--due') ? addDays(parseInt(getOption('--due')!)) : undefined,
          notes: getOption('--notes'),
          terms: getOption('--terms'),
        });

        console.log(`✓ Created invoice: ${invoice.invoiceNumber}`);
        console.log(`  Total: $${invoice.total.toFixed(2)}`);
        console.log(`  Due: ${invoice.dueDate}`);
        break;
      }

      case 'get': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        const invoice = await skill.getInvoice(id);
        if (!invoice) {
          console.log('Invoice not found');
        } else {
          printInvoiceDetails(invoice);
        }
        break;
      }

      case 'get-number': {
        const number = args[1];
        if (!number) {
          console.error('Error: Invoice number required');
          process.exit(1);
        }

        const invoice = await skill.getInvoiceByNumber(number);
        if (!invoice) {
          console.log('Invoice not found');
        } else {
          printInvoiceDetails(invoice);
        }
        break;
      }

      case 'update': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        const updates: any = {};
        if (getOption('--status')) updates.status = getOption('--status');
        if (getOption('--notes')) updates.notes = getOption('--notes');
        if (getOption('--terms')) updates.terms = getOption('--terms');

        if (Object.keys(updates).length === 0) {
          console.error('Error: At least one field to update required');
          process.exit(1);
        }

        await skill.updateInvoice(id, updates);
        console.log('✓ Invoice updated');
        break;
      }

      case 'delete': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        await skill.deleteInvoice(id);
        console.log('✓ Invoice deleted');
        break;
      }

      case 'send': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        await skill.markAsSent(id);
        console.log('✓ Invoice marked as sent');
        break;
      }

      case 'cancel': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        await skill.updateInvoice(id, { status: 'cancelled' });
        console.log('✓ Invoice cancelled');
        break;
      }

      case 'items-update': {
        const invoiceId = parseInt(args[1]);
        if (isNaN(invoiceId)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        const descOptions = getOptions('--desc');
        if (descOptions.length === 0) {
          console.error('Error: At least one line item required (--desc "Description, qty, price")');
          process.exit(1);
        }

        const lineItems: Omit<LineItem, 'id' | 'amount'>[] = descOptions.map(desc => {
          const parts = desc.split(',').map(s => s.trim());
          if (parts.length < 3) {
            throw new Error(`Invalid line item format: ${desc}. Use: "Description, qty, price"`);
          }
          return {
            description: parts[0],
            quantity: parseFloat(parts[1]),
            unitPrice: parseFloat(parts[2]),
          };
        });

        await skill.updateLineItems(invoiceId, lineItems);
        console.log('✓ Line items updated');
        break;
      }

      // Payment commands
      case 'pay': {
        const invoiceId = parseInt(args[1]);
        const amount = parseFloat(args[2]);
        
        if (isNaN(invoiceId) || isNaN(amount)) {
          console.error('Error: Valid invoice ID and amount required');
          console.error('Usage: invoices pay <invoice-id> <amount> [--method ...]');
          process.exit(1);
        }

        const payment = await skill.recordPayment(invoiceId, amount, {
          method: getOption('--method'),
          notes: getOption('--notes'),
          date: getOption('--date'),
        });

        console.log(`✓ Recorded payment of $${amount.toFixed(2)}`);
        console.log(`  Payment ID: ${payment.id}`);
        break;
      }

      case 'payment-delete': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid payment ID required');
          process.exit(1);
        }

        await skill.deletePayment(id);
        console.log('✓ Payment deleted');
        break;
      }

      // PDF/Export commands
      case 'pdf': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Valid invoice ID required');
          process.exit(1);
        }

        const { htmlPath, pdfPath } = await skill.generatePDF(id);
        console.log(`✓ Generated invoice PDF`);
        console.log(`  HTML: ${htmlPath}`);
        console.log(`  PDF:  ${pdfPath}`);
        console.log('\nNote: Convert HTML to PDF using your preferred tool (e.g., puppeteer, wkhtmltopdf)');
        break;
      }

      case 'export': {
        const status = args[1] as InvoiceStatus | undefined;
        const result = await skill.exportToCSV(status ? { status } : {});
        
        const filePath = `/tmp/${result.filename}`;
        fs.writeFileSync(filePath, result.content);
        console.log(`✓ Exported to ${filePath}`);
        console.log('\nPreview:');
        console.log(result.content);
        break;
      }

      // Report commands
      case 'summary': {
        const summary = await skill.getSummary();
        console.log('\nInvoice Summary:');
        console.log('─'.repeat(50));
        console.log(`Total Invoices:   ${summary.totalInvoices}`);
        console.log(`Total Revenue:    $${summary.totalRevenue.toFixed(2)}`);
        console.log(`Total Paid:       $${summary.totalPaid.toFixed(2)}`);
        console.log(`Total Outstanding: $${summary.totalOutstanding.toFixed(2)}`);
        console.log(`Total Overdue:    $${summary.totalOverdue.toFixed(2)}`);
        console.log('─'.repeat(50));
        console.log('\nBy Status:');
        for (const [status, data] of Object.entries(summary.byStatus)) {
          if (data.count > 0) {
            console.log(`  ${status.padEnd(12)} ${data.count.toString().padStart(3)} invoices  $${data.amount.toFixed(2)}`);
          }
        }
        break;
      }

      case 'overdue': {
        const invoices = await skill.getOverdueInvoices();
        if (invoices.length === 0) {
          console.log('No overdue invoices.');
        } else {
          console.log('\n⚠️  Overdue Invoices:');
          printInvoices(invoices);
        }
        break;
      }

      // Other commands
      case 'status':
      case 'health': {
        const health = await skill.healthCheck();
        console.log(JSON.stringify(health, null, 2));
        break;
      }

      case 'help':
      case '--help':
      case '-h':
      default:
        console.log(USAGE);
        break;
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  } finally {
    await skill.close();
  }
}

// Helper functions
function printInvoices(invoices: any[]) {
  console.log('\nInvoices:');
  console.log('─'.repeat(100));
  console.log(`${'ID'.padStart(4)} ${'Number'.padEnd(15)} ${'Client'.padEnd(20)} ${'Date'.padEnd(12)} ${'Due'.padEnd(12)} ${'Status'.padEnd(10)} ${'Total'.padStart(10)} ${'Paid'.padStart(10)} ${'Balance'.padStart(10)}`);
  console.log('─'.repeat(100));
  for (const inv of invoices) {
    const statusIcon = getStatusIcon(inv.status);
    console.log(
      `${inv.id.toString().padStart(4)} ` +
      `${inv.invoiceNumber.padEnd(15)} ` +
      `${(inv.clientName || '').substring(0, 20).padEnd(20)} ` +
      `${inv.issueDate.padEnd(12)} ` +
      `${inv.dueDate.padEnd(12)} ` +
      `${statusIcon}${inv.status.padEnd(9)} ` +
      `${inv.total.toFixed(2).padStart(10)} ` +
      `${inv.amountPaid.toFixed(2).padStart(10)} ` +
      `${inv.balanceDue.toFixed(2).padStart(10)}`
    );
  }
  console.log('─'.repeat(100));
}

function printInvoiceDetails(invoice: any) {
  const statusIcon = getStatusIcon(invoice.status);
  console.log('\n' + '═'.repeat(60));
  console.log('  INVOICE DETAILS');
  console.log('═'.repeat(60));
  console.log(`  Invoice:     ${invoice.invoiceNumber}`);
  console.log(`  Status:      ${statusIcon}${invoice.status.toUpperCase()}`);
  console.log(`  Client:      ${invoice.clientName}`);
  console.log(`  Issue Date:  ${invoice.issueDate}`);
  console.log(`  Due Date:    ${invoice.dueDate}`);
  console.log('─'.repeat(60));
  
  if (invoice.lineItems && invoice.lineItems.length > 0) {
    console.log('\n  Line Items:');
    console.log(`  ${'Description'.padEnd(30)} ${'Qty'.padStart(8)} ${'Price'.padStart(12)} ${'Amount'.padStart(12)}`);
    console.log('  ' + '─'.repeat(66));
    for (const item of invoice.lineItems) {
      // Handle both snake_case and camelCase property names
      const quantity = item.quantity ?? (item as any).quantity;
      const unitPrice = item.unitPrice ?? (item as any).unit_price;
      const amount = item.amount ?? (item as any).amount;
      console.log(`  ${item.description.substring(0, 30).padEnd(30)} ${quantity.toString().padStart(8)} $${Number(unitPrice).toFixed(2).padStart(10)} $${Number(amount).toFixed(2).padStart(10)}`);
    }
  }
  
  console.log('  ' + '─'.repeat(66));
  console.log(`  ${''.padEnd(50)} Subtotal: $${invoice.subtotal.toFixed(2)}`);
  console.log(`  ${''.padEnd(50)} Tax (${invoice.taxRate}%): $${invoice.taxAmount.toFixed(2)}`);
  console.log(`  ${''.padEnd(50)} Total: $${invoice.total.toFixed(2)}`);
  
  if (invoice.amountPaid > 0) {
    console.log(`  ${''.padEnd(50)} Paid: $${invoice.amountPaid.toFixed(2)}`);
    console.log(`  ${''.padEnd(50)} Balance Due: $${invoice.balanceDue.toFixed(2)}`);
  }
  
  if (invoice.payments && invoice.payments.length > 0) {
    console.log('\n  Payment History:');
    for (const payment of invoice.payments) {
      console.log(`    ${payment.date}: $${payment.amount.toFixed(2)}${payment.method ? ` via ${payment.method}` : ''}`);
    }
  }
  
  if (invoice.notes) {
    console.log('\n  Notes:');
    console.log(`  ${invoice.notes}`);
  }
  
  if (invoice.terms) {
    console.log('\n  Terms:');
    console.log(`  ${invoice.terms}`);
  }
  
  console.log('═'.repeat(60));
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'draft': return '📝 ';
    case 'sent': return '📤 ';
    case 'paid': return '✅ ';
    case 'overdue': return '⚠️  ';
    case 'cancelled': return '❌ ';
    default: return '';
  }
}

function addDays(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().split('T')[0];
}

main();
