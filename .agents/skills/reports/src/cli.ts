#!/usr/bin/env node
/**
 * Reports Skill CLI
 * Command-line interface for generating financial reports
 */

import { ReportsSkill, PLReport, BalanceSheet, CashFlowReport } from './index';

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  const skill = new ReportsSkill();

  try {
    switch (command) {
      case 'status':
      case 'health': {
        const health = await skill.healthCheck();
        console.log('Reports Skill Health Check');
        console.log('==========================');
        console.log(`Overall Status: ${health.status.toUpperCase()}`);
        console.log(`\nQuickBooks:`);
        console.log(`  Connected: ${health.quickbooks.connected ? 'Yes' : 'No'}`);
        if (health.quickbooks.message) {
          console.log(`  Message: ${health.quickbooks.message}`);
        }
        console.log(`\nReceipts OCR:`);
        console.log(`  Connected: ${health.receiptsOcr.connected ? 'Yes' : 'No'}`);
        if (health.receiptsOcr.message) {
          console.log(`  Message: ${health.receiptsOcr.message}`);
        }
        break;
      }

      case 'pl': {
        const period = (args[1] as any) || 'monthly';
        const year = args[2] ? parseInt(args[2]) : undefined;
        const month = args[3] ? parseInt(args[3]) : undefined;
        
        console.log(`Generating P&L Report (${period})...`);
        const report = await skill.generatePLReport({ period, year, month });
        
        console.log('\n' + '='.repeat(60));
        console.log(`  ${report.name}`);
        console.log('='.repeat(60));
        console.log(`Period: ${report.period}`);
        console.log(`Date Range: ${report.dateRange.startDate} to ${report.dateRange.endDate}`);
        console.log(`Generated: ${new Date(report.generatedAt).toLocaleString()}`);
        console.log('\n--- REVENUE ---');
        console.log(`Total Revenue: ${report.revenue.total.toFixed(2)}`);
        report.revenue.byCategory.forEach(c => {
          console.log(`  ${c.category}: ${c.amount.toFixed(2)} (${c.percentage.toFixed(1)}%)`);
        });
        console.log('\n--- EXPENSES ---');
        console.log(`Total Expenses: ${report.expenses.total.toFixed(2)}`);
        report.expenses.byCategory.forEach(c => {
          console.log(`  ${c.category}: ${c.amount.toFixed(2)} (${c.percentage.toFixed(1)}%)`);
        });
        console.log('\n--- SUMMARY ---');
        console.log(`Gross Profit: ${report.grossProfit.toFixed(2)}`);
        console.log(`Net Income: ${report.netIncome.toFixed(2)}`);
        console.log(`Margin: ${report.margin.toFixed(1)}%`);
        console.log('\n' + report.summary);
        break;
      }

      case 'balance': {
        const asOfDate = args[1] || new Date().toISOString().split('T')[0];
        
        console.log(`Generating Balance Sheet...`);
        const report = await skill.generateBalanceSheet({ asOfDate });
        
        console.log('\n' + '='.repeat(60));
        console.log(`  ${report.name}`);
        console.log('='.repeat(60));
        console.log(`As Of: ${report.asOfDate}`);
        console.log(`Generated: ${new Date(report.generatedAt).toLocaleString()}`);
        console.log(`Status: ${report.balanced ? '✓ Balanced' : '✗ Unbalanced'}`);
        console.log('\n--- ASSETS ---');
        console.log(`Current Assets: ${report.assets.totalCurrent.toFixed(2)}`);
        report.assets.current.forEach(a => {
          console.log(`  ${a.name}: ${a.amount.toFixed(2)}`);
        });
        console.log(`Fixed Assets: ${report.assets.totalFixed.toFixed(2)}`);
        console.log(`Total Assets: ${report.assets.total.toFixed(2)}`);
        console.log('\n--- LIABILITIES ---');
        console.log(`Current Liabilities: ${report.liabilities.totalCurrent.toFixed(2)}`);
        report.liabilities.current.forEach(l => {
          console.log(`  ${l.name}: ${l.amount.toFixed(2)}`);
        });
        console.log(`Long-term Liabilities: ${report.liabilities.totalLongTerm.toFixed(2)}`);
        console.log(`Total Liabilities: ${report.liabilities.total.toFixed(2)}`);
        console.log('\n--- EQUITY ---');
        report.equity.items.forEach(e => {
          console.log(`  ${e.name}: ${e.amount.toFixed(2)}`);
        });
        console.log(`Total Equity: ${report.equity.total.toFixed(2)}`);
        console.log(`\nTotal Liabilities + Equity: ${report.totalLiabilitiesAndEquity.toFixed(2)}`);
        console.log('\n' + report.summary);
        break;
      }

      case 'cashflow': {
        const period = (args[1] as any) || 'monthly';
        const year = args[2] ? parseInt(args[2]) : undefined;
        const month = args[3] ? parseInt(args[3]) : undefined;
        
        console.log(`Generating Cash Flow Report (${period})...`);
        const report = await skill.generateCashFlowReport({ period, year, month });
        
        console.log('\n' + '='.repeat(60));
        console.log(`  ${report.name}`);
        console.log('='.repeat(60));
        console.log(`Period: ${report.period}`);
        console.log(`Date Range: ${report.dateRange.startDate} to ${report.dateRange.endDate}`);
        console.log(`Generated: ${new Date(report.generatedAt).toLocaleString()}`);
        console.log('\n--- OPERATING ACTIVITIES ---');
        console.log(`  Inflows: +${report.operating.inflows.toFixed(2)}`);
        console.log(`  Outflows: -${report.operating.outflows.toFixed(2)}`);
        console.log(`  Net: ${report.operating.net >= 0 ? '+' : ''}${report.operating.net.toFixed(2)}`);
        console.log('\n--- INVESTING ACTIVITIES ---');
        console.log(`  Inflows: +${report.investing.inflows.toFixed(2)}`);
        console.log(`  Outflows: -${report.investing.outflows.toFixed(2)}`);
        console.log(`  Net: ${report.investing.net >= 0 ? '+' : ''}${report.investing.net.toFixed(2)}`);
        console.log('\n--- FINANCING ACTIVITIES ---');
        console.log(`  Inflows: +${report.financing.inflows.toFixed(2)}`);
        console.log(`  Outflows: -${report.financing.outflows.toFixed(2)}`);
        console.log(`  Net: ${report.financing.net >= 0 ? '+' : ''}${report.financing.net.toFixed(2)}`);
        console.log('\n--- SUMMARY ---');
        console.log(`Beginning Cash: ${report.beginningCash.toFixed(2)}`);
        console.log(`Net Change: ${report.netChange >= 0 ? '+' : ''}${report.netChange.toFixed(2)}`);
        console.log(`Ending Cash: ${report.endingCash.toFixed(2)}`);
        console.log('\n' + report.summary);
        break;
      }

      case 'export': {
        const reportType = args[1];
        const outputPath = args[2];
        
        if (!reportType) {
          console.log('Usage: reports export <pl|balance|cashflow> [output-path]');
          console.log('Options:');
          console.log('  --period <monthly|quarterly|yearly>');
          console.log('  --year <year>');
          console.log('  --month <month>');
          process.exit(1);
        }

        const exportOptions: any = { period: 'monthly' };
        for (let i = 3; i < args.length; i += 2) {
          const key = args[i]?.replace('--', '');
          const value = args[i + 1];
          if (key && value) {
            exportOptions[key] = key === 'year' || key === 'month' ? parseInt(value) : value;
          }
        }

        let report: PLReport | BalanceSheet | CashFlowReport;
        
        switch (reportType) {
          case 'pl':
            report = await skill.generatePLReport(exportOptions);
            break;
          case 'balance':
            report = await skill.generateBalanceSheet(exportOptions.asOfDate ? { asOfDate: exportOptions.asOfDate } : {});
            break;
          case 'cashflow':
            report = await skill.generateCashFlowReport(exportOptions);
            break;
          default:
            console.error(`Unknown report type: ${reportType}`);
            process.exit(1);
        }

        const filePath = await skill.exportToHTML(report, outputPath);
        console.log(`Report exported to: ${filePath}`);
        break;
      }

      case 'history': {
        const reportType = args[1] as any;
        const limit = args[2] ? parseInt(args[2]) : 20;
        
        const history = await skill.getReportHistory(reportType, limit);
        
        console.log('Report History');
        console.log('==============');
        if (history.length === 0) {
          console.log('No reports generated yet.');
        } else {
          history.forEach(h => {
            console.log(`[${h.reportType.toUpperCase()}] ${h.reportName}`);
            console.log(`  Generated: ${new Date(h.generatedAt).toLocaleString()}`);
            console.log(`  Period: ${h.dateRange}`);
            if (h.filePath) {
              console.log(`  File: ${h.filePath}`);
            }
            console.log();
          });
        }
        break;
      }

      case 'schedule': {
        const action = args[1];
        
        if (action === 'create') {
          const name = args[2];
          const type = args[3] as any;
          const period = args[4] as any;
          const schedule = args[5] as any;
          
          if (!name || !type || !period || !schedule) {
            console.log('Usage: reports schedule create <name> <pl|balance|cashflow> <monthly|quarterly|yearly> <daily|weekly|monthly>');
            process.exit(1);
          }
          
          const scheduled = await skill.createScheduledReport({
            name,
            type,
            period,
            schedule,
            active: true,
          });
          
          console.log('Scheduled report created:');
          console.log(`  ID: ${scheduled.id}`);
          console.log(`  Name: ${scheduled.name}`);
          console.log(`  Type: ${scheduled.type}`);
          console.log(`  Period: ${scheduled.period}`);
          console.log(`  Schedule: ${scheduled.schedule}`);
        } else if (action === 'list') {
          const activeOnly = args.includes('--active');
          const schedules = await skill.getScheduledReports(activeOnly);
          
          console.log('Scheduled Reports');
          console.log('=================');
          if (schedules.length === 0) {
            console.log('No scheduled reports.');
          } else {
            schedules.forEach(s => {
              console.log(`[${s.id}] ${s.name} (${s.type.toUpperCase()})`);
              console.log(`  Period: ${s.period}, Schedule: ${s.schedule}`);
              console.log(`  Active: ${s.active ? 'Yes' : 'No'}`);
              if (s.lastRun) {
                console.log(`  Last Run: ${new Date(s.lastRun).toLocaleString()}`);
              }
              if (s.nextRun) {
                console.log(`  Next Run: ${new Date(s.nextRun).toLocaleString()}`);
              }
              console.log();
            });
          }
        } else if (action === 'delete') {
          const id = parseInt(args[2]);
          if (isNaN(id)) {
            console.log('Usage: reports schedule delete <id>');
            process.exit(1);
          }
          await skill.deleteScheduledReport(id);
          console.log(`Scheduled report ${id} deleted.`);
        } else {
          console.log('Usage: reports schedule <create|list|delete> [options]');
        }
        break;
      }

      case 'help':
      default: {
        console.log('Reports Skill - Financial Report Generation');
        console.log('==========================================\n');
        console.log('Commands:');
        console.log('  status                    Check health of dependencies');
        console.log('  pl [period] [year] [month]  Generate P&L report');
        console.log('  balance [date]            Generate Balance Sheet');
        console.log('  cashflow [period] [year] [month]  Generate Cash Flow report');
        console.log('  export <type> [path]      Export report to HTML');
        console.log('  history [type] [limit]    View report history');
        console.log('  schedule create <name> <type> <period> <schedule>  Schedule a report');
        console.log('  schedule list [--active]  List scheduled reports');
        console.log('  schedule delete <id>      Delete scheduled report');
        console.log('  help                      Show this help message');
        console.log('\nPeriods: monthly, quarterly, yearly');
        console.log('Report types: pl, balance, cashflow');
        console.log('\nExamples:');
        console.log('  reports pl monthly 2024 1      # January 2024 P&L');
        console.log('  reports balance 2024-01-31     # Balance sheet as of Jan 31');
        console.log('  reports export pl ./report.html --period quarterly --year 2024');
        break;
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
