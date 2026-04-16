#!/usr/bin/env node
/**
 * Maintenance Scheduler CLI
 * Command-line interface for scheduling home maintenance tasks
 */

import { MaintenanceSchedulerSkill, HomeType, TaskCategory, maintenanceTemplates } from './index';

const args = process.argv.slice(2);

function printHelp(): void {
  console.log(`
Maintenance Scheduler - Schedule recurring home maintenance tasks

Usage: maintenance-scheduler <command> [options]

Commands:
  apply-template <type>              Apply a seasonal template (house|apartment|condo)
  preview-template <type>            Preview tasks in a template
  templates                          List available templates

  create <name> <frequency>          Create a custom maintenance task
    --days <n>                       Frequency in days (required)
    --notice-days <n>                Days of advance notice (default: 3)
    --category <cat>                 Category: indoor, outdoor, hvac, plumbing, electrical, appliance, safety, cleaning, other
    --description <text>             Task description

  list                               List all tasks
    --category <cat>                 Filter by category

  get <id>                           Get task details
  update <id>                        Update a task
    --name <name>                    New name
    --days <n>                       New frequency
    --notice-days <n>                New notice period
    --category <cat>                 New category
    --description <text>             New description
  delete <id>                        Delete a task

  complete <id>                      Mark a task complete (auto-schedules next)
    --notes <text>                   Completion notes

  upcoming [days]                    Show upcoming tasks (default: 365 days)
  due                                Show tasks due now (including notice period)
  history                            Show completion history
    --limit <n>                      Number of entries (default: 20)

  stats                              Show statistics
  health                             Check system health

Examples:
  maintenance-scheduler apply-template house
  maintenance-scheduler create "Water plants" --days 7 --category indoor
  maintenance-scheduler create "Clean gutters" --days 90 --notice-days 7 --category outdoor
  maintenance-scheduler upcoming 30
  maintenance-scheduler complete 1 --notes "Changed all filters"
`);
}

async function main(): Promise<void> {
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    printHelp();
    process.exit(0);
  }

  const scheduler = new MaintenanceSchedulerSkill();

  try {
    switch (command) {
      case 'apply-template': {
        const homeType = args[1] as HomeType;
        if (!homeType || !['house', 'apartment', 'condo'].includes(homeType)) {
          console.error('Error: Please specify a valid template type: house, apartment, or condo');
          process.exit(1);
        }

        console.log(`Applying ${homeType} maintenance template...`);
        const result = await scheduler.applyTemplate(homeType);
        console.log(`✓ Created ${result.created} maintenance tasks`);
        console.log('\nTasks created:');
        for (const task of result.tasks) {
          const category = task.category.charAt(0).toUpperCase() + task.category.slice(1);
          console.log(`  • ${task.name} (${category}) - Every ${task.frequencyDays} days`);
        }
        break;
      }

      case 'preview-template': {
        const homeType = args[1] as HomeType;
        if (!homeType || !['house', 'apartment', 'condo'].includes(homeType)) {
          console.error('Error: Please specify a valid template type: house, apartment, or condo');
          process.exit(1);
        }

        const tasks = scheduler.previewTemplate(homeType);
        console.log(`\n${homeType.charAt(0).toUpperCase() + homeType.slice(1)} Maintenance Template`);
        console.log(`${tasks.length} tasks:\n`);

        // Group by frequency
        const byFrequency: Record<number, typeof tasks> = {};
        for (const task of tasks) {
          if (!byFrequency[task.frequencyDays]) {
            byFrequency[task.frequencyDays] = [];
          }
          byFrequency[task.frequencyDays].push(task);
        }

        const frequencies = Object.keys(byFrequency).map(Number).sort((a, b) => a - b);
        for (const freq of frequencies) {
          let freqLabel: string;
          if (freq === 30) freqLabel = 'Monthly';
          else if (freq === 90) freqLabel = 'Quarterly';
          else if (freq === 180) freqLabel = 'Bi-Annual';
          else if (freq === 365) freqLabel = 'Annual';
          else freqLabel = `Every ${freq} days`;

          console.log(`${freqLabel}:`);
          for (const task of byFrequency[freq]) {
            console.log(`  • ${task.name}`);
            if (task.description) {
              console.log(`    ${task.description}`);
            }
          }
          console.log();
        }
        break;
      }

      case 'templates': {
        const templates = scheduler.getAvailableTemplates();
        console.log('\nAvailable Templates:');
        for (const tmpl of templates) {
          console.log(`  ${tmpl.type.padEnd(12)} - ${tmpl.name} (${tmpl.taskCount} tasks)`);
        }
        break;
      }

      case 'create': {
        const name = args[1];
        if (!name) {
          console.error('Error: Please specify a task name');
          process.exit(1);
        }

        const daysIndex = args.indexOf('--days');
        const days = daysIndex >= 0 ? parseInt(args[daysIndex + 1]) : NaN;
        if (isNaN(days) || days <= 0) {
          console.error('Error: Please specify a valid frequency with --days <n>');
          process.exit(1);
        }

        const noticeIndex = args.indexOf('--notice-days');
        const noticeDays = noticeIndex >= 0 ? parseInt(args[noticeIndex + 1]) : 3;

        const categoryIndex = args.indexOf('--category');
        const category = (categoryIndex >= 0 ? args[categoryIndex + 1] : 'other') as TaskCategory;

        const descIndex = args.indexOf('--description');
        const description = descIndex >= 0 ? args[descIndex + 1] : undefined;

        const task = await scheduler.createTask({
          name,
          description,
          frequencyDays: days,
          advanceNoticeDays: noticeDays,
          category,
        });

        console.log(`✓ Created task: ${task.name}`);
        console.log(`  ID: ${task.id}`);
        console.log(`  Frequency: Every ${task.frequencyDays} days`);
        console.log(`  Next due: ${new Date(task.nextDue).toLocaleDateString()}`);
        console.log(`  Category: ${task.category}`);
        break;
      }

      case 'list': {
        const categoryIndex = args.indexOf('--category');
        const category = categoryIndex >= 0 ? args[categoryIndex + 1] as TaskCategory : undefined;

        const tasks = await scheduler.listTasks(category);
        
        if (tasks.length === 0) {
          console.log('No tasks found. Create one with: maintenance-scheduler create <name> --days <n>');
          break;
        }

        console.log(`\n${tasks.length} maintenance tasks:\n`);
        
        // Group by category
        const byCategory: Record<string, typeof tasks> = {};
        for (const task of tasks) {
          if (!byCategory[task.category]) {
            byCategory[task.category] = [];
          }
          byCategory[task.category].push(task);
        }

        for (const [cat, catTasks] of Object.entries(byCategory)) {
          console.log(`${cat.charAt(0).toUpperCase() + cat.slice(1)}:`);
          for (const task of catTasks) {
            const due = new Date(task.nextDue);
            const daysUntil = Math.ceil((due.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
            const dueStr = daysUntil < 0 ? `(${Math.abs(daysUntil)} days overdue)` : 
                          daysUntil === 0 ? '(Due today)' : 
                          `(Due in ${daysUntil} days)`;
            console.log(`  [${task.id}] ${task.name} - Every ${task.frequencyDays} days ${dueStr}`);
          }
          console.log();
        }
        break;
      }

      case 'get': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Please specify a valid task ID');
          process.exit(1);
        }

        const task = await scheduler.getTask(id);
        if (!task) {
          console.error(`Task ${id} not found`);
          process.exit(1);
        }

        console.log(`\nTask: ${task.name}`);
        console.log(`ID: ${task.id}`);
        console.log(`Description: ${task.description || 'None'}`);
        console.log(`Frequency: Every ${task.frequencyDays} days`);
        console.log(`Advance notice: ${task.advanceNoticeDays} days`);
        console.log(`Category: ${task.category}`);
        console.log(`Next due: ${new Date(task.nextDue).toLocaleString()}`);
        console.log(`Created: ${new Date(task.createdAt).toLocaleDateString()}`);
        break;
      }

      case 'update': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Please specify a valid task ID');
          process.exit(1);
        }

        const nameIndex = args.indexOf('--name');
        const daysIndex = args.indexOf('--days');
        const noticeIndex = args.indexOf('--notice-days');
        const categoryIndex = args.indexOf('--category');
        const descIndex = args.indexOf('--description');

        const updates: {
          name?: string;
          frequencyDays?: number;
          advanceNoticeDays?: number;
          category?: TaskCategory;
          description?: string;
        } = {};

        if (nameIndex >= 0) updates.name = args[nameIndex + 1];
        if (daysIndex >= 0) updates.frequencyDays = parseInt(args[daysIndex + 1]);
        if (noticeIndex >= 0) updates.advanceNoticeDays = parseInt(args[noticeIndex + 1]);
        if (categoryIndex >= 0) updates.category = args[categoryIndex + 1] as TaskCategory;
        if (descIndex >= 0) updates.description = args[descIndex + 1];

        const task = await scheduler.updateTask(id, updates);
        if (!task) {
          console.error(`Task ${id} not found`);
          process.exit(1);
        }

        console.log(`✓ Updated task: ${task.name}`);
        break;
      }

      case 'delete': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Please specify a valid task ID');
          process.exit(1);
        }

        const task = await scheduler.getTask(id);
        if (!task) {
          console.error(`Task ${id} not found`);
          process.exit(1);
        }

        const success = await scheduler.deleteTask(id);
        if (success) {
          console.log(`✓ Deleted task: ${task.name}`);
        } else {
          console.error('Failed to delete task');
          process.exit(1);
        }
        break;
      }

      case 'complete': {
        const id = parseInt(args[1]);
        if (isNaN(id)) {
          console.error('Error: Please specify a valid task ID');
          process.exit(1);
        }

        const notesIndex = args.indexOf('--notes');
        const notes = notesIndex >= 0 ? args[notesIndex + 1] : undefined;

        const task = await scheduler.getTask(id);
        if (!task) {
          console.error(`Task ${id} not found`);
          process.exit(1);
        }

        const result = await scheduler.completeTask(id, notes);
        if (result.success) {
          console.log(`✓ Completed: ${task.name}`);
          if (result.nextDue) {
            console.log(`  Next due: ${result.nextDue.toLocaleDateString()}`);
          }
        } else {
          console.error('Failed to complete task');
          process.exit(1);
        }
        break;
      }

      case 'upcoming': {
        const days = args[1] ? parseInt(args[1]) : 365;
        const tasks = await scheduler.getUpcomingTasks(days);

        if (tasks.length === 0) {
          console.log('No upcoming tasks in the specified period.');
          break;
        }

        console.log(`\nUpcoming maintenance tasks (next ${days} days):\n`);
        
        for (const item of tasks) {
          const dueStr = item.daysUntil < 0 ? `${Math.abs(item.daysUntil)} days overdue` :
                        item.daysUntil === 0 ? 'Due today' :
                        item.daysUntil === 1 ? 'Due tomorrow' :
                        `Due in ${item.daysUntil} days`;
          
          const noticeStr = item.isNoticePeriod ? ' [Notice period]' : '';
          
          console.log(`[${item.task.id}] ${item.task.name}`);
          console.log(`    ${dueStr}${noticeStr}`);
          console.log(`    Category: ${item.task.category} | Frequency: Every ${item.task.frequencyDays} days`);
          console.log();
        }
        break;
      }

      case 'due': {
        const due = await scheduler.getDueTasks();

        if (due.length === 0) {
          console.log('No tasks due currently. Great job keeping up with maintenance!');
          break;
        }

        console.log(`\nTasks due (including notice period):\n`);
        
        for (const item of due) {
          const dueStr = item.daysUntil < 0 ? `OVERDUE: ${Math.abs(item.daysUntil)} days` :
                        item.daysUntil === 0 ? 'DUE TODAY' :
                        `Due in ${item.daysUntil} days`;
          
          console.log(`[${item.task.id}] ${item.task.name} - ${dueStr}`);
          console.log(`    Category: ${item.task.category}`);
          if (item.task.description) {
            console.log(`    ${item.task.description}`);
          }
          console.log();
        }
        break;
      }

      case 'history': {
        const limitIndex = args.indexOf('--limit');
        const limit = limitIndex >= 0 ? parseInt(args[limitIndex + 1]) : 20;

        const history = await scheduler.getCompletionHistory(limit);

        if (history.length === 0) {
          console.log('No completion history yet. Complete some tasks to see them here!');
          break;
        }

        console.log(`\nCompletion History (last ${history.length} entries):\n`);
        
        for (const entry of history) {
          const date = new Date(entry.completedAt);
          console.log(`${date.toLocaleDateString()} - ${entry.taskName}`);
          if (entry.notes) {
            console.log(`  Notes: ${entry.notes}`);
          }
        }
        break;
      }

      case 'stats': {
        const stats = await scheduler.getStats();
        
        console.log('\nMaintenance Statistics');
        console.log('=====================\n');
        console.log(`Total tasks: ${stats.totalTasks}`);
        console.log(`Completed this month: ${stats.completedThisMonth}`);
        console.log(`Completed this year: ${stats.completedThisYear}`);
        console.log(`Overdue tasks: ${stats.overdueTasks}`);
        console.log(`Upcoming (30 days): ${stats.upcomingTasks}`);
        console.log('\nBy Category:');
        for (const [cat, count] of Object.entries(stats.byCategory)) {
          if (count > 0) {
            console.log(`  ${cat}: ${count}`);
          }
        }
        break;
      }

      case 'health': {
        const health = await scheduler.healthCheck();
        
        console.log('\nHealth Check');
        console.log('===========\n');
        console.log(`Status: ${health.status === 'healthy' ? '✓ Healthy' : '✗ Unhealthy'}`);
        console.log(`Database: ${health.database}`);
        console.log(`Total tasks: ${health.tasks}`);
        console.log(`Completions this year: ${health.completions}`);
        console.log(`Upcoming (30 days): ${health.upcoming}`);
        console.log(`Overdue: ${health.overdue}`);
        
        if (health.error) {
          console.log(`\nError: ${health.error}`);
        }
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        printHelp();
        process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  } finally {
    await scheduler.close();
  }
}

main();
