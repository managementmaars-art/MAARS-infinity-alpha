#!/usr/bin/env node
/**
 * Reminders Skill CLI
 * Command-line interface for reminder management
 */

import { RemindersSkill, Reminder, ReminderType } from './index';

const command = process.argv[2];
const args = process.argv.slice(3);

const reminders = new RemindersSkill();

async function main() {
  try {
    switch (command) {
      case 'add':
        await addReminder();
        break;
      case 'recurring':
        await addRecurring();
        break;
      case 'list':
        await listReminders();
        break;
      case 'due':
        await listDue();
        break;
      case 'get':
        await getReminder();
        break;
      case 'complete':
        await completeReminder();
        break;
      case 'snooze':
        await snoozeReminder();
        break;
      case 'delete':
        await deleteReminder();
        break;
      case 'history':
        await showHistory();
        break;
      case 'stats':
        await showStats();
        break;
      case 'daemon':
        await runDaemon();
        break;
      case 'health':
        await healthCheck();
        break;
      case 'parse':
        await testParse();
        break;
      default:
        showHelp();
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  } finally {
    await reminders.close();
  }
}

async function addReminder() {
  if (args.length < 2) {
    console.error('Usage: reminders add <datetime> <message>');
    console.log('\nDatetime formats:');
    console.log('  "2026-02-15 14:00"  - Specific date and time');
    console.log('  "tomorrow"           - Tomorrow at current time');
    console.log('  "in 2 hours"         - Relative time');
    console.log('  "in 30 minutes"      - Relative time');
    console.log('  "14:30"              - Today at 14:30 (or tomorrow if passed)');
    console.log('\nExample: reminders add "in 30 minutes" "Call mom"');
    process.exit(1);
  }

  const datetime = args[0];
  const message = args.slice(1).join(' ');

  const scheduledAt = reminders.parseNaturalDateTime(datetime);
  const reminder = await reminders.addReminder({ message, scheduledAt });

  console.log('\n✓ Reminder created');
  console.log(`  ID: ${reminder.id}`);
  console.log(`  Message: ${reminder.message}`);
  console.log(`  Scheduled: ${formatDateTime(reminder.scheduledAt)}`);
}

async function addRecurring() {
  if (args.length < 3) {
    console.error('Usage: reminders recurring <type> <datetime> <message>');
    console.log('\nTypes: daily, weekly, monthly');
    console.log('\nExample: reminders recurring daily "09:00" "Take vitamins"');
    process.exit(1);
  }

  const type = args[0] as 'daily' | 'weekly' | 'monthly';
  if (!['daily', 'weekly', 'monthly'].includes(type)) {
    console.error('Error: Type must be daily, weekly, or monthly');
    process.exit(1);
  }

  const datetime = args[1];
  const message = args.slice(2).join(' ');

  const startAt = reminders.parseNaturalDateTime(datetime);
  const reminder = await reminders.addRecurringReminder({ message, type, startAt });

  console.log('\n✓ Recurring reminder created');
  console.log(`  ID: ${reminder.id}`);
  console.log(`  Message: ${reminder.message}`);
  console.log(`  Type: ${reminder.reminderType}`);
  console.log(`  First occurrence: ${formatDateTime(reminder.scheduledAt)}`);
}

async function listReminders() {
  const includeCompleted = args.includes('--all');
  const limit = parseInt(getArg('--limit') || '50');

  const list = await reminders.listReminders({ includeCompleted, limit });

  console.log(`\nReminders (${list.length}):`);
  console.log('-'.repeat(60));

  if (list.length === 0) {
    console.log('No reminders found.');
    return;
  }

  for (const reminder of list) {
    printReminder(reminder);
  }
}

async function listDue() {
  const due = await reminders.getDueReminders();

  console.log(`\nDue Reminders (${due.length}):`);
  console.log('-'.repeat(60));

  if (due.length === 0) {
    console.log('No reminders are currently due.');
    return;
  }

  for (const reminder of due) {
    printReminder(reminder, true);
  }
}

async function getReminder() {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: reminders get <id>');
    process.exit(1);
  }

  const reminder = await reminders.getReminder(id);
  if (!reminder) {
    console.error(`Reminder ${id} not found`);
    process.exit(1);
  }

  console.log('\nReminder Details:');
  console.log('='.repeat(60));
  printReminder(reminder, true);
}

async function completeReminder() {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: reminders complete <id>');
    process.exit(1);
  }

  const result = await reminders.completeReminder(id);
  
  if (result.movedToHistory) {
    console.log(`✓ Reminder ${id} completed and moved to history`);
  } else if (result.nextOccurrence) {
    console.log(`✓ Reminder ${id} completed`);
    console.log(`  Next occurrence: ${formatDateTime(result.nextOccurrence.toISOString())}`);
  }
}

async function snoozeReminder() {
  if (args.length < 2) {
    console.error('Usage: reminders snooze <id> <minutes>');
    console.log('\nExample: reminders snooze 123 30');
    process.exit(1);
  }

  const id = parseInt(args[0]);
  const minutes = parseInt(args[1]);

  if (isNaN(id) || isNaN(minutes)) {
    console.error('Error: ID and minutes must be numbers');
    process.exit(1);
  }

  const reminder = await reminders.snoozeReminder(id, minutes);
  console.log(`✓ Reminder ${id} snoozed for ${minutes} minutes`);
  console.log(`  Will notify again at: ${formatDateTime(reminder.snoozeUntil!)}`);
}

async function deleteReminder() {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: reminders delete <id>');
    process.exit(1);
  }

  const deleted = await reminders.deleteReminder(id);
  if (deleted) {
    console.log(`✓ Reminder ${id} deleted`);
  } else {
    console.error(`Reminder ${id} not found`);
    process.exit(1);
  }
}

async function showHistory() {
  const limit = parseInt(getArg('--limit') || '20');
  const history = await reminders.getHistory(limit);

  console.log(`\nReminder History (${history.length}):`);
  console.log('-'.repeat(60));

  if (history.length === 0) {
    console.log('No completed reminders.');
    return;
  }

  for (const item of history) {
    console.log(`\n#${item.id}: ${item.message}`);
    console.log(`  Scheduled: ${formatDateTime(item.scheduledAt)}`);
    console.log(`  Completed: ${formatDateTime(item.completedAt)}`);
  }
}

async function showStats() {
  const stats = await reminders.getStats();

  console.log('\nReminder Statistics:');
  console.log('-'.repeat(40));
  console.log(`  Pending reminders: ${stats.pending}`);
  console.log(`  Completed reminders: ${stats.completed}`);
  console.log(`  Overdue reminders: ${stats.overdue}`);
}

async function runDaemon() {
  const result = await reminders.daemonCheck();

  if (result.count === 0) {
    console.log(JSON.stringify({ notifications: [], count: 0 }));
    return;
  }

  // Output as JSON for programmatic use
  console.log(JSON.stringify({
    notifications: result.notifications.map(r => ({
      id: r.id,
      message: r.message,
      scheduledAt: r.scheduledAt,
      type: r.reminderType,
    })),
    count: result.count,
    timestamp: result.timestamp,
  }, null, 2));
}

async function healthCheck() {
  const result = await reminders.healthCheck();

  console.log(`\nHealth Check: ${result.status.toUpperCase()}`);
  console.log('-'.repeat(40));
  console.log(`Database: ${result.database}`);
  console.log(`Pending reminders: ${result.pendingReminders}`);
  console.log(`Completed reminders: ${result.completedReminders}`);
  
  if (result.error) {
    console.log(`Error: ${result.error}`);
  }

  process.exit(result.status === 'healthy' ? 0 : 1);
}

async function testParse() {
  if (args.length === 0) {
    console.error('Usage: reminders parse <datetime-string>');
    console.log('\nTest natural language datetime parsing');
    process.exit(1);
  }

  const input = args.join(' ');
  try {
    const result = reminders.parseNaturalDateTime(input);
    console.log(`\nInput: "${input}"`);
    console.log(`Parsed: ${formatDateTime(result.toISOString())}`);
    console.log(`ISO: ${result.toISOString()}`);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

// Helper functions

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index !== -1 && index + 1 < args.length) {
    return args[index + 1];
  }
  return undefined;
}

function printReminder(reminder: Reminder, detailed = false) {
  const isOverdue = new Date(reminder.scheduledAt) < new Date() && !reminder.completedAt;
  const overdueMark = isOverdue ? ' [OVERDUE]' : '';
  const typeLabel = reminder.reminderType !== 'once' ? ` (${reminder.reminderType})` : '';

  console.log(`\n#${reminder.id}: ${reminder.message}${typeLabel}${overdueMark}`);
  console.log(`  Scheduled: ${formatDateTime(reminder.scheduledAt)}`);
  
  if (reminder.snoozeUntil) {
    console.log(`  Snoozed until: ${formatDateTime(reminder.snoozeUntil)}`);
  }

  if (detailed) {
    console.log(`  Created: ${formatDateTime(reminder.createdAt)}`);
    if (reminder.completedAt) {
      console.log(`  Completed: ${formatDateTime(reminder.completedAt)}`);
    }
  }
}

function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function showHelp() {
  console.log(`
Reminders Skill CLI

Usage: reminders <command> [options]

Commands:
  add <datetime> <message>         Create a one-time reminder
                                   Datetime: "2026-02-15 14:00", "tomorrow", "in 2 hours"
  
  recurring <type> <time> <msg>    Create a recurring reminder
                                   Type: daily, weekly, monthly
  
  list                             List all pending reminders [--all, --limit N]
  due                              List reminders that are due now
  get <id>                         Get details of a specific reminder
  complete <id>                    Mark a reminder as complete
  snooze <id> <minutes>            Snooze a reminder
  delete <id>                      Delete a reminder
  history                          Show completed reminders [--limit N]
  stats                            Show reminder statistics
  daemon                           Check for due reminders (JSON output)
  health                           Run health check
  parse <datetime>                 Test natural language parsing

Examples:
  reminders add "in 30 minutes" "Call dentist"
  reminders add "2026-02-15 09:00" "Meeting with team"
  reminders recurring daily "09:00" "Take vitamins"
  reminders recurring weekly "Monday 10:00" "Weekly review"
`);
}

main();
