#!/usr/bin/env node

import { TicketTriageSkill, Ticket, TicketCategory, TicketPriority } from './index';

const args = process.argv.slice(2);
const command = args[0];

function printHelp() {
  console.log(`
Ticket Triage CLI - AI-powered support ticket classification

Usage: ticket-triage <command> [options]

Commands:
  classify                    Classify a ticket interactively
  classify --subject "..."    Classify with subject
  classify --body "..."       Classify with body
  category <name>             List tickets by category
  priority <level>            List tickets by priority
  assignee <team>             List tickets by assignee
  spam                        List spam tickets
  unreviewed                  List unreviewed tickets
  review <ticketId>           Review and update classification
  add-rule                    Add classification rule
  list-rules                  List classification rules
  delete-rule <id>            Delete a classification rule
  assignment-rules            List assignment rules
  update-assignment           Update assignment rule
  stats                       Show classification statistics
  health                      Check system health

Examples:
  ticket-triage classify --subject "Login error" --body "Cannot access my account"
  ticket-triage category bug
  ticket-triage priority critical
  ticket-triage add-rule --pattern "urgent" --category bug --priority critical
`);
}

function parseArgs() {
  const options: Record<string, string> = {};
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : 'true';
      options[key] = value;
      if (value !== 'true') i++;
    }
  }
  return options;
}

async function classifyCommand() {
  const options = parseArgs();
  const triage = new TicketTriageSkill();

  try {
    let ticket: Ticket;
    
    if (options.subject && options.body) {
      ticket = {
        id: options.id || `TICKET-${Date.now()}`,
        subject: options.subject,
        body: options.body,
        from: options.from || 'unknown@example.com',
        createdAt: new Date(),
        tags: options.tags ? options.tags.split(',') : undefined
      };
    } else {
      console.log('Interactive mode not supported in CLI. Use --subject and --body options.');
      console.log('Example: ticket-triage classify --subject "Login error" --body "Cannot access"');
      process.exit(1);
    }

    const classification = await triage.classify(ticket);

    console.log('\n🎫 Ticket Classification Result\n');
    console.log(`Ticket ID:     ${ticket.id}`);
    console.log(`Subject:       ${ticket.subject}`);
    console.log(`\n📊 Classification:`);
    console.log(`  Category:    ${classification.category}`);
    console.log(`  Priority:    ${classification.priority.toUpperCase()}`);
    console.log(`  Score:       ${classification.priorityScore}/100`);
    console.log(`  Confidence:  ${(classification.confidence * 100).toFixed(1)}%`);
    console.log(`  Assigned To: ${classification.assignedTo || 'Unassigned'}`);
    
    if (classification.isSpam) {
      console.log(`\n🚫 SPAM DETECTED (Score: ${(classification.spamScore * 100).toFixed(1)}%)`);
    }

    console.log(`\n📝 Reasons:`);
    classification.reasons.forEach(reason => {
      console.log(`  • ${reason}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function categoryCommand() {
  const category = args[1] as TicketCategory;
  if (!category) {
    console.log('Usage: ticket-triage category <bug|feature_request|question|complaint|billing|technical|account|other>');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    const classifications = await triage.listByCategory(category, 50);
    
    console.log(`\n📁 Tickets in category: ${category}\n`);
    
    if (classifications.length === 0) {
      console.log('No tickets found in this category.');
      return;
    }

    console.log(`Found ${classifications.length} tickets:\n`);
    console.log('ID                    Priority  Score  Confidence  Assigned To');
    console.log('-'.repeat(75));

    classifications.forEach(c => {
      const id = c.ticketId.padEnd(20);
      const priority = c.priority.padEnd(9);
      const score = c.priorityScore.toString().padStart(5);
      const conf = `${(c.confidence * 100).toFixed(0)}%`.padStart(10);
      const assigned = c.assignedTo || '-';
      console.log(`${id} ${priority} ${score} ${conf}  ${assigned}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function priorityCommand() {
  const priority = args[1] as TicketPriority;
  if (!priority) {
    console.log('Usage: ticket-triage priority <critical|high|medium|low>');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    const classifications = await triage.listByPriority(priority, 50);
    
    console.log(`\n🔔 Tickets with priority: ${priority.toUpperCase()}\n`);
    
    if (classifications.length === 0) {
      console.log('No tickets found with this priority.');
      return;
    }

    console.log(`Found ${classifications.length} tickets:\n`);
    console.log('ID                    Category      Score  Confidence  Assigned To');
    console.log('-'.repeat(75));

    classifications.forEach(c => {
      const id = c.ticketId.padEnd(20);
      const cat = c.category.padEnd(13);
      const score = c.priorityScore.toString().padStart(5);
      const conf = `${(c.confidence * 100).toFixed(0)}%`.padStart(10);
      const assigned = c.assignedTo || '-';
      console.log(`${id} ${cat} ${score} ${conf}  ${assigned}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function assigneeCommand() {
  const team = args[1];
  if (!team) {
    console.log('Usage: ticket-triage assignee <team-name>');
    console.log('Example: ticket-triage assignee engineering');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    const classifications = await triage.listByAssignee(team, 50);
    
    console.log(`\n👤 Tickets assigned to: ${team}\n`);
    
    if (classifications.length === 0) {
      console.log('No tickets assigned to this team.');
      return;
    }

    console.log(`Found ${classifications.length} tickets:\n`);
    console.log('ID                    Category      Priority  Score');
    console.log('-'.repeat(60));

    classifications.forEach(c => {
      const id = c.ticketId.padEnd(20);
      const cat = c.category.padEnd(13);
      const priority = c.priority.padEnd(9);
      const score = c.priorityScore.toString().padStart(5);
      console.log(`${id} ${cat} ${priority} ${score}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function spamCommand() {
  const triage = new TicketTriageSkill();

  try {
    const classifications = await triage.getSpamTickets(50);
    
    console.log(`\n🚫 Spam Tickets\n`);
    
    if (classifications.length === 0) {
      console.log('No spam tickets found.');
      return;
    }

    console.log(`Found ${classifications.length} spam tickets:\n`);
    console.log('ID                    Spam Score  Classified At');
    console.log('-'.repeat(60));

    classifications.forEach(c => {
      const id = c.ticketId.padEnd(20);
      const score = `${(c.spamScore * 100).toFixed(1)}%`.padStart(10);
      const date = c.classifiedAt.toISOString().split('T')[0];
      console.log(`${id} ${score}  ${date}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function unreviewedCommand() {
  const triage = new TicketTriageSkill();

  try {
    const classifications = await triage.getUnreviewed(50);
    
    console.log(`\n👀 Unreviewed Tickets\n`);
    
    if (classifications.length === 0) {
      console.log('No unreviewed tickets found.');
      return;
    }

    console.log(`Found ${classifications.length} unreviewed tickets:\n`);
    console.log('ID                    Category      Priority  Score  Assigned To');
    console.log('-'.repeat(75));

    classifications.forEach(c => {
      const id = c.ticketId.padEnd(20);
      const cat = c.category.padEnd(13);
      const priority = c.priority.padEnd(9);
      const score = c.priorityScore.toString().padStart(5);
      const assigned = c.assignedTo || '-';
      console.log(`${id} ${cat} ${priority} ${score}  ${assigned}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function reviewCommand() {
  const ticketId = args[1];
  if (!ticketId) {
    console.log('Usage: ticket-triage review <ticketId> [--category <cat>] [--priority <pri>] [--assignee <team>]');
    process.exit(1);
  }

  const options = parseArgs();
  const triage = new TicketTriageSkill();

  try {
    const updates: any = {};
    if (options.category) updates.category = options.category as TicketCategory;
    if (options.priority) updates.priority = options.priority as TicketPriority;
    if (options.assignee) updates.assignedTo = options.assignee;

    await triage.review(ticketId, updates);

    console.log(`\n✅ Ticket ${ticketId} reviewed and updated.`);
    
    const classification = await triage.getClassification(ticketId);
    if (classification) {
      console.log(`\nUpdated classification:`);
      console.log(`  Category:    ${classification.category}`);
      console.log(`  Priority:    ${classification.priority}`);
      console.log(`  Assigned To: ${classification.assignedTo || 'Unassigned'}`);
    }

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function addRuleCommand() {
  const options = parseArgs();
  
  if (!options.pattern || !options.category || !options.priority) {
    console.log('Usage: ticket-triage add-rule --pattern <text> --category <cat> --priority <pri> [--assignee <team>] [--spam]');
    console.log('Example: ticket-triage add-rule --pattern "billing" --category billing --priority high');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    await triage.addClassificationRule(
      options.pattern,
      (options.type as 'keyword' | 'regex') || 'keyword',
      options.category as TicketCategory,
      options.priority as TicketPriority,
      options.assignee,
      options.spam === 'true'
    );

    console.log(`\n✅ Classification rule added:`);
    console.log(`  Pattern:  ${options.pattern}`);
    console.log(`  Category: ${options.category}`);
    console.log(`  Priority: ${options.priority}`);
    if (options.assignee) console.log(`  Assignee: ${options.assignee}`);
    if (options.spam === 'true') console.log(`  Auto-spam: Yes`);

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function listRulesCommand() {
  const triage = new TicketTriageSkill();

  try {
    const rules = await triage.listClassificationRules();
    
    console.log(`\n📋 Classification Rules\n`);
    
    if (rules.length === 0) {
      console.log('No classification rules defined.');
      return;
    }

    console.log(`Found ${rules.length} rules:\n`);
    console.log('ID  Type     Pattern              Category        Priority  Assignee');
    console.log('-'.repeat(80));

    rules.forEach(r => {
      const id = r.id.toString().padStart(2);
      const type = r.patternType.padEnd(8);
      const pattern = r.pattern.slice(0, 18).padEnd(20);
      const cat = r.category.padEnd(15);
      const pri = r.priority.padEnd(9);
      const assign = r.assignedTo || '-';
      const spam = r.autoSpam ? ' [SPAM]' : '';
      console.log(`${id}  ${type} ${pattern} ${cat} ${pri} ${assign}${spam}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function deleteRuleCommand() {
  const id = parseInt(args[1]);
  if (isNaN(id)) {
    console.log('Usage: ticket-triage delete-rule <id>');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    await triage.deleteClassificationRule(id);
    console.log(`\n✅ Rule ${id} deleted.`);
  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function assignmentRulesCommand() {
  const triage = new TicketTriageSkill();

  try {
    const rules = await triage.getAssignmentRules();
    
    console.log(`\n👥 Assignment Rules\n`);
    
    if (rules.length === 0) {
      console.log('No assignment rules defined.');
      return;
    }

    console.log(`Found ${rules.length} rules:\n`);
    console.log('Category          Team              Active');
    console.log('-'.repeat(50));

    rules.forEach(r => {
      const cat = r.category.padEnd(17);
      const team = r.team.padEnd(17);
      const active = r.active ? 'Yes' : 'No';
      console.log(`${cat} ${team} ${active}`);
    });

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function updateAssignmentCommand() {
  const options = parseArgs();
  
  if (!options.category || !options.team) {
    console.log('Usage: ticket-triage update-assignment --category <cat> --team <name> [--active true|false]');
    console.log('Example: ticket-triage update-assignment --category bug --team engineering');
    process.exit(1);
  }

  const triage = new TicketTriageSkill();

  try {
    await triage.updateAssignmentRule(
      options.category as TicketCategory,
      options.team,
      options.active !== 'false'
    );

    console.log(`\n✅ Assignment rule updated:`);
    console.log(`  Category: ${options.category}`);
    console.log(`  Team:     ${options.team}`);
    console.log(`  Active:   ${options.active !== 'false'}`);

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function statsCommand() {
  const triage = new TicketTriageSkill();

  try {
    const stats = await triage.getStats();
    
    console.log(`\n📊 Ticket Triage Statistics\n`);
    console.log(`Total Classified: ${stats.totalClassified}`);
    console.log(`Spam Detected:    ${stats.spamCount}`);
    console.log(`Unreviewed:       ${stats.unreviewed}\n`);

    console.log('By Category:');
    Object.entries(stats.byCategory).forEach(([cat, count]) => {
      if (count > 0) {
        console.log(`  ${cat.padEnd(17)} ${count.toString().padStart(4)}`);
      }
    });

    console.log('\nBy Priority:');
    Object.entries(stats.byPriority).forEach(([pri, count]) => {
      console.log(`  ${pri.padEnd(10)} ${count.toString().padStart(4)}`);
    });

    if (Object.keys(stats.byAssignment).length > 0) {
      console.log('\nBy Assignment:');
      Object.entries(stats.byAssignment).forEach(([team, count]) => {
        console.log(`  ${team.padEnd(20)} ${count.toString().padStart(4)}`);
      });
    }

  } catch (error: any) {
    console.error('Error:', error.message);
  } finally {
    await triage.close();
  }
}

async function healthCommand() {
  const triage = new TicketTriageSkill();

  try {
    const health = await triage.healthCheck();
    
    if (health.status === 'healthy') {
      console.log(`✅ ${health.message}`);
      process.exit(0);
    } else {
      console.log(`❌ ${health.message}`);
      process.exit(1);
    }
  } catch (error: any) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await triage.close();
  }
}

async function main() {
  if (!command || command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    process.exit(0);
  }

  switch (command) {
    case 'classify':
      await classifyCommand();
      break;
    case 'category':
      await categoryCommand();
      break;
    case 'priority':
      await priorityCommand();
      break;
    case 'assignee':
      await assigneeCommand();
      break;
    case 'spam':
      await spamCommand();
      break;
    case 'unreviewed':
      await unreviewedCommand();
      break;
    case 'review':
      await reviewCommand();
      break;
    case 'add-rule':
      await addRuleCommand();
      break;
    case 'list-rules':
      await listRulesCommand();
      break;
    case 'delete-rule':
      await deleteRuleCommand();
      break;
    case 'assignment-rules':
      await assignmentRulesCommand();
      break;
    case 'update-assignment':
      await updateAssignmentCommand();
      break;
    case 'stats':
      await statsCommand();
      break;
    case 'health':
      await healthCommand();
      break;
    default:
      console.log(`Unknown command: ${command}`);
      printHelp();
      process.exit(1);
  }
}

main().catch(console.error);
