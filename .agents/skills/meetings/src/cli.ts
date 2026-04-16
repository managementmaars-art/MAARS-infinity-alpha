#!/usr/bin/env node
/**
 * Meetings Skill CLI
 * Command-line interface for meeting coordination
 */

import { MeetingsSkill, Meeting, MeetingTemplate } from './index';
import { TimeSlot } from '@openclaw/calendar';

const command = process.argv[2];
const args = process.argv.slice(3);

const profile = process.env.OPENCLAW_PROFILE || 'default';
const meetings = new MeetingsSkill({ profile });

async function main() {
  try {
    switch (command) {
      case 'status':
        await showStatus();
        break;
      case 'schedule':
        await scheduleMeeting();
        break;
      case 'quick':
        await quickSchedule();
        break;
      case 'template':
        await scheduleFromTemplate();
        break;
      case 'templates':
        await listTemplates();
        break;
      case 'list':
        await listMeetings();
        break;
      case 'get':
        await getMeeting();
        break;
      case 'cancel':
        await cancelMeeting();
        break;
      case 'delete':
        await deleteMeeting();
        break;
      case 'free':
        await findAvailability();
        break;
      case 'invite':
        await sendInvite();
        break;
      case 'prep':
        await sendPrep();
        break;
      case 'health':
        await healthCheck();
        break;
      default:
        showHelp();
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  } finally {
    await meetings.close();
  }
}

async function showStatus() {
  const status = await meetings.getStatus();
  
  if (status.connected) {
    console.log(`✓ Meetings skill connected`);
    console.log(`  Email: ${status.email}`);
    console.log(`  Calendar: ${status.calendarConnected ? '✓' : '✗'}`);
    console.log(`  Email: ${status.emailConnected ? '✓' : '✗'}`);
  } else {
    console.log(`✗ Meetings skill not connected`);
    if (!status.calendarConnected) {
      console.log(`  Calendar not connected`);
    }
    if (!status.emailConnected) {
      console.log(`  Email not connected`);
    }
    console.log(`\nRun authentication first:`);
    console.log(`  node ../google-oauth/dist/cli.js connect default calendar email`);
  }
}

async function scheduleMeeting() {
  const title = getArg('--title') || getArg('-t');
  const duration = parseInt(getArg('--duration') || getArg('-d') || '60');
  const attendeesArg = getArg('--attendees') || getArg('-a');
  const days = parseInt(getArg('--days') || '7');
  
  if (!title || !attendeesArg) {
    console.error('Usage: meetings schedule --title "Meeting Title" --attendees "email1@example.com,email2@example.com" [options]');
    console.log('\nOptions:');
    console.log('  --title, -t        Meeting title (required)');
    console.log('  --attendees, -a    Comma-separated email addresses (required)');
    console.log('  --duration, -d     Duration in minutes (default: 60)');
    console.log('  --description      Meeting description');
    console.log('  --location         Meeting location');
    console.log('  --days             Days ahead to search (default: 7)');
    console.log('  --no-invite        Do not send email invites');
    console.log('  --prep             Send prep email with agenda');
    process.exit(1);
  }
  
  const timeMin = new Date();
  const timeMax = new Date();
  timeMax.setDate(timeMin.getDate() + days);
  
  const attendees = attendeesArg.split(',').map(e => e.trim());
  
  // Build agenda if provided
  const agendaItems: Array<{ title: string; duration: number }> = [];
  let agendaIndex = 0;
  while (true) {
    const agendaTitle = getArg(`--agenda-${agendaIndex}`);
    if (!agendaTitle) break;
    const agendaDuration = parseInt(getArg(`--agenda-${agendaIndex}-duration`) || '10');
    agendaItems.push({ title: agendaTitle, duration: agendaDuration });
    agendaIndex++;
  }
  
  const result = await meetings.schedule({
    title,
    description: getArg('--description'),
    duration,
    attendees,
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
    location: getArg('--location'),
    agenda: agendaItems.length > 0 ? agendaItems : undefined,
    sendInvites: !hasFlag('--no-invite'),
    sendPrepEmail: hasFlag('--prep'),
  });
  
  if (result.success && result.meeting) {
    console.log('\n✓ Meeting scheduled successfully');
    printMeeting(result.meeting);
    
    if (result.suggestedSlots && result.suggestedSlots.length > 0) {
      console.log('\nAlternative times:');
      for (const slot of result.suggestedSlots.slice(0, 3)) {
        console.log(`  ${formatDateTime(slot.start)} - ${formatTime(slot.end)}`);
      }
    }
  } else {
    console.log('\n✗ Failed to schedule meeting');
    console.log(`  Error: ${result.error}`);
    
    if (result.suggestedSlots && result.suggestedSlots.length > 0) {
      console.log('\nSuggested time slots:');
      for (const slot of result.suggestedSlots.slice(0, 5)) {
        console.log(`  ${formatDateTime(slot.start)} - ${formatTime(slot.end)}`);
      }
    }
  }
}

async function quickSchedule() {
  const title = getArg('--title') || getArg('-t');
  const attendeesArg = getArg('--attendees') || getArg('-a');
  
  if (!title || !attendeesArg) {
    console.error('Usage: meetings quick --title "Meeting Title" --attendees "email1@example.com" [options]');
    console.log('\nOptions:');
    console.log('  --title, -t        Meeting title (required)');
    console.log('  --attendees, -a    Comma-separated email addresses (required)');
    console.log('  --duration         Duration in minutes (default: 30)');
    console.log('  --days             Days ahead to search (default: 3)');
    process.exit(1);
  }
  
  const duration = parseInt(getArg('--duration') || '30');
  const days = parseInt(getArg('--days') || '3');
  const timeMin = new Date();
  const timeMax = new Date();
  timeMax.setDate(timeMin.getDate() + days);
  
  const attendees = attendeesArg.split(',').map(e => e.trim());
  
  const result = await meetings.schedule({
    title,
    duration,
    attendees,
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
    sendInvites: true,
  });
  
  if (result.success && result.meeting) {
    console.log('\n✓ Meeting scheduled');
    console.log(`  ${result.meeting.title}`);
    console.log(`  ${formatDateTime(result.meeting.startTime)} - ${formatTime(result.meeting.endTime)}`);
    console.log(`  Attendees: ${result.meeting.attendees.map(a => a.email).join(', ')}`);
  } else {
    console.log('\n✗ Failed to schedule');
    console.log(`  ${result.error}`);
  }
}

async function scheduleFromTemplate() {
  const templateName = args[0];
  const title = getArg('--title') || getArg('-t');
  const attendeesArg = getArg('--attendees') || getArg('-a');
  
  if (!templateName || !attendeesArg) {
    console.error('Usage: meetings template <template-name> --attendees "email1@example.com" [options]');
    console.log('\nOptions:');
    console.log('  --title, -t        Override meeting title');
    console.log('  --attendees, -a    Comma-separated email addresses (required)');
    console.log('  --days             Days ahead to search (default: 7)');
    console.log('  --no-invite        Do not send email invites');
    console.log('\nAvailable templates:');
    const templates = await meetings.listTemplates();
    for (const t of templates) {
      console.log(`  ${t.name} - ${t.title} (${t.duration} min)`);
    }
    process.exit(1);
  }
  
  const days = parseInt(getArg('--days') || '7');
  const timeMin = new Date();
  const timeMax = new Date();
  timeMax.setDate(timeMin.getDate() + days);
  
  const attendees = attendeesArg.split(',').map(e => e.trim());
  
  const result = await meetings.scheduleFromTemplate(templateName, {
    title,
    attendees,
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
    sendInvites: !hasFlag('--no-invite'),
  });
  
  if (result.success && result.meeting) {
    console.log('\n✓ Meeting scheduled from template');
    printMeeting(result.meeting);
  } else {
    console.log('\n✗ Failed to schedule');
    console.log(`  ${result.error}`);
  }
}

async function listTemplates() {
  const templates = await meetings.listTemplates();
  
  console.log(`\nMeeting Templates (${templates.length}):`);
  console.log('-'.repeat(60));
  
  for (const t of templates) {
    console.log(`\n${t.name}`);
    console.log(`  Title: ${t.title}`);
    console.log(`  Duration: ${t.duration} min`);
    if (t.description) {
      console.log(`  Description: ${t.description}`);
    }
    if (t.agenda.length > 0) {
      console.log(`  Agenda: ${t.agenda.length} items`);
    }
  }
}

async function listMeetings() {
  const status = getArg('--status');
  const days = parseInt(getArg('--days') || '30');
  const limit = parseInt(getArg('--limit') || '20');
  
  const from = new Date();
  const to = new Date();
  to.setDate(from.getDate() + days);
  
  const meetingList = await meetings.listMeetings({
    status: status as Meeting['status'],
    from: from.toISOString(),
    to: to.toISOString(),
    limit,
  });
  
  console.log(`\nMeetings (${meetingList.length}):`);
  console.log('-'.repeat(60));
  
  for (const meeting of meetingList) {
    printMeetingSummary(meeting);
  }
}

async function getMeeting() {
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: meetings get <meeting-id>');
    process.exit(1);
  }
  
  const meeting = await meetings.getMeeting(meetingId);
  if (!meeting) {
    console.log(`Meeting not found: ${meetingId}`);
    process.exit(1);
  }
  
  console.log('\nMeeting Details:');
  console.log('='.repeat(60));
  printMeeting(meeting, true);
}

async function cancelMeeting() {
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: meetings cancel <meeting-id> [--no-notify]');
    process.exit(1);
  }
  
  const notify = !hasFlag('--no-notify');
  const success = await meetings.cancelMeeting(meetingId, notify);
  
  if (success) {
    console.log(`✓ Meeting cancelled${notify ? ' and attendees notified' : ''}`);
  } else {
    console.log('✗ Failed to cancel meeting');
  }
}

async function deleteMeeting() {
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: meetings delete <meeting-id>');
    process.exit(1);
  }
  
  const success = await meetings.deleteMeeting(meetingId);
  
  if (success) {
    console.log('✓ Meeting deleted');
  } else {
    console.log('✗ Failed to delete meeting');
  }
}

async function findAvailability() {
  const duration = parseInt(getArg('--duration') || getArg('-d') || '60');
  const days = parseInt(getArg('--days') || '7');
  
  const timeMin = new Date();
  const timeMax = new Date();
  timeMax.setDate(timeMin.getDate() + days);
  
  const slots = await meetings.findAvailability({
    attendees: [],
    duration,
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
  });
  
  console.log(`\nAvailable time slots (${slots.availableSlots.length}):`);
  console.log('-'.repeat(60));
  
  for (const slot of slots.availableSlots.slice(0, 10)) {
    console.log(`  ${formatDateTime(slot.start)} - ${formatTime(slot.end)}`);
  }
  
  if (slots.availableSlots.length > 10) {
    console.log(`\n  ... and ${slots.availableSlots.length - 10} more slots`);
  }
}

async function sendInvite() {
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: meetings invite <meeting-id>');
    process.exit(1);
  }
  
  const meeting = await meetings.getMeeting(meetingId);
  if (!meeting) {
    console.log(`Meeting not found: ${meetingId}`);
    process.exit(1);
  }
  
  await meetings.sendMeetingInvite(meeting);
  console.log('✓ Invites sent to all attendees');
}

async function sendPrep() {
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: meetings prep <meeting-id>');
    process.exit(1);
  }
  
  const meeting = await meetings.getMeeting(meetingId);
  if (!meeting) {
    console.log(`Meeting not found: ${meetingId}`);
    process.exit(1);
  }
  
  await meetings.sendPrepEmail(meeting);
  console.log('✓ Prep email sent to all attendees');
}

async function healthCheck() {
  const result = await meetings.healthCheck();
  
  console.log(`\nHealth Check: ${result.status.toUpperCase()}`);
  console.log('-'.repeat(40));
  
  if (result.email) {
    console.log(`Email: ${result.email}`);
  }
  if (result.message) {
    console.log(`Message: ${result.message}`);
  }
  
  process.exit(result.status === 'healthy' ? 0 : 1);
}

// Helper functions

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index !== -1 && index + 1 < args.length) {
    return args[index + 1];
  }
  return undefined;
}

function hasFlag(name: string): boolean {
  return args.includes(name);
}

function printMeeting(meeting: Meeting, detailed = false) {
  console.log(`\n${meeting.title}`);
  console.log(`  ID: ${meeting.id}`);
  console.log(`  Status: ${meeting.status}`);
  console.log(`  Time: ${formatDateTime(meeting.startTime)} - ${formatTime(meeting.endTime)}`);
  console.log(`  Timezone: ${meeting.timeZone}`);
  
  if (meeting.location) {
    console.log(`  Location: ${meeting.location}`);
  }
  
  if (meeting.videoLink) {
    console.log(`  Video: ${meeting.videoLink}`);
  }
  
  if (meeting.attendees.length > 0) {
    console.log(`  Attendees (${meeting.attendees.length}):`);
    for (const attendee of meeting.attendees) {
      const status = attendee.responseStatus ? ` (${attendee.responseStatus})` : '';
      const name = attendee.name || attendee.email;
      console.log(`    - ${name}${status}`);
    }
  }
  
  if (meeting.agenda.length > 0) {
    console.log(`  Agenda (${meeting.agenda.length} items):`);
    for (const item of meeting.agenda) {
      console.log(`    ${item.title} (${item.duration} min)`);
    }
  }
  
  if (detailed && meeting.description) {
    console.log(`  Description: ${meeting.description.substring(0, 200)}${meeting.description.length > 200 ? '...' : ''}`);
  }
  
  if (meeting.calendarEventId) {
    console.log(`  Calendar Event: ${meeting.calendarEventId}`);
  }
}

function printMeetingSummary(meeting: Meeting) {
  const start = new Date(meeting.startTime);
  const statusIcon = meeting.status === 'scheduled' ? '●' : '○';
  console.log(`\n${statusIcon} ${meeting.title}`);
  console.log(`  ${formatDateTime(meeting.startTime)} - ${formatTime(meeting.endTime)}`);
  console.log(`  ID: ${meeting.id}`);
  console.log(`  Status: ${meeting.status}`);
  if (meeting.attendees.length > 0) {
    console.log(`  Attendees: ${meeting.attendees.length}`);
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

function formatTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

function showHelp() {
  console.log(`
Meetings Skill CLI

Usage: meetings <command> [options]

Commands:
  status                      Show connection status
  schedule                    Schedule a new meeting [--title, --attendees, --duration, --days, --description, --location, --no-invite, --prep]
  quick                       Quick schedule with minimal options [--title, --attendees, --duration, --days]
  template <name>             Schedule from template [--title, --attendees, --days, --no-invite]
  templates                   List available templates
  list                        List scheduled meetings [--status, --days, --limit]
  get <id>                    Get meeting details
  cancel <id>                 Cancel a meeting [--no-notify]
  delete <id>                 Delete a meeting permanently
  free                        Find available time slots [--duration, --days]
  invite <id>                 Send invites for a meeting
  prep <id>                   Send prep email for a meeting
  health                      Run health check

Examples:
  meetings schedule --title "Team Standup" --attendees "alice@example.com,bob@example.com" --duration 30
  meetings template Standup --attendees "team@example.com"
  meetings list --days 7
  meetings cancel meeting_1234567890

Environment Variables:
  OPENCLAW_PROFILE    Profile to use (default: default)
`);
}

main();
