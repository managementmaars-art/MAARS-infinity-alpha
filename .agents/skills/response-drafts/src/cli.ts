#!/usr/bin/env node

import { ResponseDraftsSkill, Ticket, ResponseTone, TicketPriority } from './index';

const args = process.argv.slice(2);
const command = args[0];

const skill = new ResponseDraftsSkill();

// Helper to print usage
function printUsage() {
  console.log(`
Response Drafts Skill - CLI

Usage: response-drafts <command> [options]

Commands:
  health                              Check system health
  
  generate <ticket-id>                Generate response drafts for a ticket
    --subject <text>                  Ticket subject (required)
    --description <text>              Ticket description (required)
    --priority <low|medium|high|urgent> Ticket priority (default: medium)
    --requester <name>                Requester name
    --tags <tag1,tag2>                Comma-separated tags
    --tone <tone>                     Force specific tone
    --count <n>                       Number of drafts (default: 3)
    --no-kb                           Disable KB article suggestions
    
  drafts <ticket-id>                  List drafts for a ticket
    --limit <n>                       Limit results (default: 10)
    
  all-drafts                          List all drafts
    --limit <n>                       Limit results (default: 50)
    
  templates                           List available templates
    --category <cat>                  Filter by category
    
  template <name>                     Show specific template
  
  use-template <name>                 Apply template with variables
    --vars '<json>'                   JSON object of variables
    
  add-template                        Add custom template
    --name <name>                     Template name (required)
    --category <cat>                  Category (required)
    --content <text>                  Template content (required)
    --tone <tone>                     Tone (default: professional)
    --tags <tag1,tag2>                Comma-separated tags
    
  kb                                  List KB articles
    --category <cat>                  Filter by category
    
  kb-add                              Add KB article
    --id <id>                         Article ID (required)
    --title <text>                    Title (required)
    --content <text>                  Content (required)
    --category <cat>                  Category
    --tags <tag1,tag2>                Comma-separated tags
    
  send <draft-id>                     Mark draft as sent
  
  stats                               Show usage statistics
  
  tones                               List available tones
  
  help                                Show this help

Examples:
  response-drafts health
  
  response-drafts generate TICKET-123 \\
    --subject "Can't login" \\
    --description "I'm getting an error when trying to login" \\
    --priority high \\
    --requester "John Doe"
    
  response-drafts templates --category resolution
  
  response-drafts use-template acknowledgment \\
    --vars '{"requesterName":"Jane","subject":"billing issue"}'
`);
}

// Parse arguments
function parseArgs(args: string[]): Record<string, string | boolean> {
  const options: Record<string, string | boolean> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        options[key] = args[i + 1];
        i++;
      } else {
        options[key] = true;
      }
    }
  }
  return options;
}

const options = parseArgs(args.slice(1));

async function main() {
  try {
    switch (command) {
      case 'health': {
        const health = await skill.healthCheck();
        console.log(`Status: ${health.status}`);
        console.log(`Message: ${health.message}`);
        break;
      }

      case 'generate': {
        const ticketId = args[1];
        if (!ticketId) {
          console.error('Error: ticket-id is required');
          process.exit(1);
        }

        const subject = options.subject as string;
        const description = options.description as string;
        
        if (!subject || !description) {
          console.error('Error: --subject and --description are required');
          process.exit(1);
        }

        const ticket: Ticket = {
          id: ticketId,
          subject,
          description,
          priority: (options.priority as TicketPriority) || 'medium',
          requesterName: options.requester as string,
          tags: options.tags ? (options.tags as string).split(',').map(t => t.trim()) : []
        };

        console.log(`Generating drafts for ticket ${ticketId}...`);
        console.log(`Subject: ${subject}`);
        console.log(`Priority: ${ticket.priority}`);
        console.log('');

        const drafts = await skill.generateDrafts(ticket, {
          tone: options.tone as ResponseTone,
          count: options.count ? parseInt(options.count as string) : 3,
          includeKBArticles: options['no-kb'] !== true
        });

        console.log(`Generated ${drafts.length} draft(s):\n`);
        
        for (let i = 0; i < drafts.length; i++) {
          const draft = drafts[i];
          console.log(`─`.repeat(60));
          console.log(`Draft ${i + 1} (ID: ${draft.id})`);
          console.log(`Tone: ${draft.tone} | Confidence: ${Math.round(draft.confidence * 100)}%`);
          if (draft.kbArticles && draft.kbArticles.length > 0) {
            console.log(`KB Articles: ${draft.kbArticles.map(a => a.title).join(', ')}`);
          }
          console.log('─'.repeat(60));
          console.log(draft.content);
          console.log('');
        }
        break;
      }

      case 'drafts': {
        const ticketId = args[1];
        if (!ticketId) {
          console.error('Error: ticket-id is required');
          process.exit(1);
        }

        const drafts = await skill.getDraftsForTicket(ticketId);
        
        if (drafts.length === 0) {
          console.log(`No drafts found for ticket ${ticketId}`);
          break;
        }

        console.log(`Drafts for ticket ${ticketId}:\n`);
        for (const draft of drafts) {
          const status = draft.wasSent ? '✓ Sent' : '○ Pending';
          console.log(`[${status}] ID: ${draft.id} | Tone: ${draft.tone} | ${draft.createdAt.toLocaleString()}`);
          console.log(`Confidence: ${Math.round(draft.confidence * 100)}%`);
          console.log(`Preview: ${draft.content.substring(0, 100)}...`);
          console.log('');
        }
        break;
      }

      case 'all-drafts': {
        const limit = options.limit ? parseInt(options.limit as string) : 50;
        const drafts = await skill.getAllDrafts(limit);
        
        if (drafts.length === 0) {
          console.log('No drafts found');
          break;
        }

        console.log(`All Drafts (last ${limit}):\n`);
        for (const draft of drafts) {
          const status = draft.wasSent ? '✓' : '○';
          console.log(`${status} [${draft.ticketId}] ID: ${draft.id} | ${draft.tone} | ${draft.createdAt.toLocaleDateString()}`);
        }
        break;
      }

      case 'templates': {
        const category = options.category as string;
        const templates = await skill.getTemplates(category);
        
        if (templates.length === 0) {
          console.log('No templates found');
          break;
        }

        console.log('Available Templates:\n');
        
        // Group by category
        const byCategory: Record<string, typeof templates> = {};
        for (const t of templates) {
          if (!byCategory[t.category]) byCategory[t.category] = [];
          byCategory[t.category].push(t);
        }

        for (const [cat, temps] of Object.entries(byCategory)) {
          console.log(`\n[${cat.toUpperCase()}]`);
          for (const t of temps) {
            console.log(`  • ${t.name} (${t.tone})`);
            const vars = t.variables?.join(', ') || 'none';
            console.log(`    Variables: ${vars}`);
          }
        }
        break;
      }

      case 'template': {
        const name = args[1];
        if (!name) {
          console.error('Error: template name is required');
          process.exit(1);
        }

        const template = await skill.getTemplate(name);
        if (!template) {
          console.error(`Template '${name}' not found`);
          process.exit(1);
        }

        console.log(`Template: ${template.name}`);
        console.log(`Category: ${template.category}`);
        console.log(`Tone: ${template.tone}`);
        console.log(`Tags: ${template.tags?.join(', ') || 'none'}`);
        console.log(`Variables: ${template.variables?.join(', ') || 'none'}`);
        console.log('');
        console.log('Content:');
        console.log('─'.repeat(60));
        console.log(template.content);
        break;
      }

      case 'use-template': {
        const name = args[1];
        if (!name) {
          console.error('Error: template name is required');
          process.exit(1);
        }

        const template = await skill.getTemplate(name);
        if (!template) {
          console.error(`Template '${name}' not found`);
          process.exit(1);
        }

        let vars: Record<string, string> = {};
        if (options.vars) {
          try {
            vars = JSON.parse(options.vars as string);
          } catch (e) {
            console.error('Error: --vars must be valid JSON');
            process.exit(1);
          }
        }

        const result = skill.applyTemplate(template, vars);
        console.log('Applied Template:\n');
        console.log(result);
        break;
      }

      case 'add-template': {
        const name = options.name as string;
        const category = options.category as string;
        const content = options.content as string;

        if (!name || !category || !content) {
          console.error('Error: --name, --category, and --content are required');
          process.exit(1);
        }

        const template = await skill.addTemplate({
          name,
          category,
          content,
          tone: (options.tone as ResponseTone) || 'professional',
          tags: options.tags ? (options.tags as string).split(',').map(t => t.trim()) : [],
          variables: content.match(/{{\s*(\w+)\s*}}/g)?.map(v => v.replace(/[{}\s]/g, '')) || []
        });

        console.log(`Template '${template.name}' added successfully (ID: ${template.id})`);
        break;
      }

      case 'kb': {
        const category = options.category as string;
        const articles = await skill.getKBArticles(category);
        
        if (articles.length === 0) {
          console.log('No KB articles found');
          break;
        }

        console.log('Knowledge Base Articles:\n');
        for (const article of articles) {
          console.log(`📖 ${article.title} [${article.id}]`);
          console.log(`   Category: ${article.category || 'uncategorized'}`);
          console.log(`   Tags: ${article.tags?.join(', ') || 'none'}`);
          console.log(`   ${article.content.substring(0, 100)}...`);
          console.log('');
        }
        break;
      }

      case 'kb-add': {
        const id = options.id as string;
        const title = options.title as string;
        const content = options.content as string;

        if (!id || !title || !content) {
          console.error('Error: --id, --title, and --content are required');
          process.exit(1);
        }

        await skill.addKBArticle({
          id,
          title,
          content,
          category: options.category as string,
          tags: options.tags ? (options.tags as string).split(',').map(t => t.trim()) : []
        });

        console.log(`KB Article '${title}' added successfully (ID: ${id})`);
        break;
      }

      case 'send': {
        const draftId = parseInt(args[1]);
        if (isNaN(draftId)) {
          console.error('Error: valid draft-id is required');
          process.exit(1);
        }

        await skill.markDraftAsSent(draftId);
        console.log(`Draft ${draftId} marked as sent`);
        break;
      }

      case 'stats': {
        const stats = await skill.getStats();
        
        console.log('Response Drafts Statistics\n');
        console.log(`Total Drafts: ${stats.totalDrafts}`);
        console.log(`Sent Drafts: ${stats.sentDrafts}`);
        console.log(`Success Rate: ${stats.totalDrafts > 0 ? Math.round((stats.sentDrafts / stats.totalDrafts) * 100) : 0}%`);
        console.log(`Average Confidence: ${Math.round(stats.averageConfidence * 100)}%`);
        console.log('\nDrafts by Tone:');
        for (const [tone, count] of Object.entries(stats.draftsByTone)) {
          console.log(`  ${tone}: ${count}`);
        }
        break;
      }

      case 'tones': {
        console.log('Available Tones:\n');
        const tones: ResponseTone[] = ['professional', 'empathetic', 'technical', 'casual', 'apologetic', 'confident'];
        for (const tone of tones) {
          const descriptions: Record<ResponseTone, string> = {
            professional: 'Clear, business-appropriate language',
            empathetic: 'Shows understanding and compassion',
            technical: 'Precise, detailed explanations',
            casual: 'Friendly, conversational style',
            apologetic: 'Acknowledges issues with regret',
            confident: 'Assures resolution capability'
          };
          console.log(`  • ${tone}: ${descriptions[tone]}`);
        }
        break;
      }

      case 'help':
      case '--help':
      case '-h':
      default:
        printUsage();
        break;
    }
  } catch (error) {
    console.error('Error:', (error as Error).message);
    process.exit(1);
  } finally {
    await skill.close();
  }
}

main();
