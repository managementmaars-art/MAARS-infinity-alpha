---
name: maintenance-scheduler
description: "Schedule recurring home maintenance tasks with seasonal templates"
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# Maintenance Scheduler Skill

Schedule recurring home maintenance tasks with seasonal templates. Track completion and get notifications when tasks are due.

## Features

- **Seasonal templates**: Pre-built maintenance schedules for different seasons
- **Custom schedules**: Create your own maintenance tasks with flexible recurrence
- **Completion tracking**: Mark tasks complete and view history
- **Notification timing**: Configurable advance notice for upcoming tasks
- **Home type support**: Templates for houses, apartments, and condos

## Usage

### Apply a seasonal template

Apply pre-built maintenance schedules for your home type:

```bash
# Apply house maintenance template
npx maintenance-scheduler apply-template house

# Apply apartment maintenance template
npx maintenance-scheduler apply-template apartment

# Apply condo maintenance template
npx maintenance-scheduler apply-template condo
```

### Create a custom maintenance task

```bash
# Create a weekly task
npx maintenance-scheduler create "Water plants" weekly --days 7

# Create a monthly task with advance notice
npx maintenance-scheduler create "Check smoke detectors" monthly --days 30 --notice-days 3

# Create a quarterly task
npx maintenance-scheduler create "Service HVAC" custom --days 90 --notice-days 7

# Create an annual task
npx maintenance-scheduler create "Clean gutters" custom --days 365 --notice-days 14
```

### List upcoming tasks

```bash
# Show all upcoming tasks
npx maintenance-scheduler upcoming

# Show tasks due in next 30 days
npx maintenance-scheduler upcoming 30

# Show tasks due today
npx maintenance-scheduler due
```

### Complete a task

```bash
npx maintenance-scheduler complete 123
```

When you complete a recurring task, the next occurrence is automatically scheduled.

### View completion history

```bash
# View recent completions
npx maintenance-scheduler history

# View more entries
npx maintenance-scheduler history --limit 50
```

### Manage tasks

```bash
# List all tasks
npx maintenance-scheduler list

# Get task details
npx maintenance-scheduler get 123

# Update a task
npx maintenance-scheduler update 123 --name "New name" --days 14

# Delete a task
npx maintenance-scheduler delete 123
```

### Templates

```bash
# List available templates
npx maintenance-scheduler templates

# Preview what tasks a template will create
npx maintenance-scheduler preview-template house
```

### Statistics

```bash
# View completion statistics
npx maintenance-scheduler stats

# Check system health
npx maintenance-scheduler health
```

## Seasonal Templates

### House Template

**Monthly tasks:**
- Check HVAC filters
- Test smoke and CO detectors
- Inspect plumbing for leaks

**Quarterly tasks:**
- Clean gutters
- Inspect roof
- Service garage door

**Bi-annual tasks:**
- Deep clean carpets
- Service major appliances
- Inspect exterior paint

**Annual tasks:**
- Professional HVAC service
- Chimney inspection
- Septic system check

### Apartment Template

**Monthly tasks:**
- Check smoke detectors
- Clean AC filters
- Inspect faucets for leaks

**Quarterly tasks:**
- Deep clean appliances
- Check weather stripping

**Annual tasks:**
- Deep clean carpets
- Professional AC service
- Safety inspection

### Condo Template

**Monthly tasks:**
- Check detectors and filters
- Inspect for moisture

**Quarterly tasks:**
- Clean balcony/terrace
- Service appliances

**Annual tasks:**
- Deep cleaning
- Maintenance inspection

## API Usage

```typescript
import { MaintenanceSchedulerSkill } from '@openclaw/maintenance-scheduler';

const scheduler = new MaintenanceSchedulerSkill();

// Apply a template
await scheduler.applyTemplate('house');

// Create a custom task
const task = await scheduler.createTask({
  name: 'Water plants',
  frequencyDays: 7,
  advanceNoticeDays: 1,
  category: 'indoor'
});

// Get upcoming tasks
const upcoming = await scheduler.getUpcomingTasks(30);
for (const item of upcoming) {
  console.log(`${item.task.name} due in ${item.daysUntil} days`);
}

// Complete a task (auto-schedules next occurrence)
await scheduler.completeTask(task.id);

// View completion history
const history = await scheduler.getCompletionHistory(20);

// Close connection
await scheduler.close();
```

## Storage

SQLite database at `~/.openclaw/skills/maintenance-scheduler/maintenance.db`:

- `tasks` - Maintenance tasks with schedule configuration
- `completion_history` - Record of completed tasks

## Integration with Reminders Skill

This skill depends on the reminders skill to create notification reminders. When a task is created or completed, a reminder is automatically scheduled based on the advance notice configuration.
