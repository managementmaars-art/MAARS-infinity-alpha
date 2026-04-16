#!/usr/bin/env node
import { SlackSkill } from './index.js';

function printUsage() {
  console.log(`
Slack Skill CLI

Usage:
  node dist/cli.js <command> [options]

Commands:
  status                              Check connection status
  health                              Run health check
  channels                            List all channels
  users [options]                     List users (--include-bots to include bots)
  user <user-id>                      Get user info by ID
  find-user <email>                   Find user by email

  send <channel> <message>            Send a message to a channel
  dm <user-id> <message>              Send a direct message
  reply <channel> <thread-ts> <msg>   Reply in a thread

  upload <channel> <file> [title]     Upload a file to a channel

  create-channel <name> [options]     Create a new channel (--private for private)
  join <channel>                      Join bot to a channel
  leave <channel>                     Leave a channel

  templates                           List notification templates
  template <name>                     Show template details
  create-template <name> <channel> <file>  Create template from file
  delete-template <name>              Delete a template
  notify <template> [channel]         Send notification using template

  history [limit]                     Show sent message history

Options:
  --profile <name>    Use specific profile (default: default)
  --blocks            Parse message as JSON blocks
  --private           Create private channel
  --include-bots      Include bots in user list
  --var-<name>=<val>  Set template variable

Examples:
  node dist/cli.js status
  node dist/cli.js send #general "Hello everyone!"
  node dist/cli.js dm U123456 "Hey there!"
  node dist/cli.js upload #general ./report.pdf "Monthly Report"
  node dist/cli.js create-channel alerts --private
  node dist/cli.js notify welcome --var-name="John"
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    printUsage();
    process.exit(0);
  }

  const command = args[0];
  const profileIndex = args.indexOf('--profile');
  const profile = profileIndex > -1 ? args[profileIndex + 1] : 'default';
  
  // Remove --profile and its value from args
  if (profileIndex > -1) {
    args.splice(profileIndex, 2);
  }

  const skill = SlackSkill.forProfile(profile);

  try {
    switch (command) {
      case 'status': {
        const connected = await skill.isConnected();
        console.log(connected ? 'Connected to Slack' : 'Not connected');
        break;
      }

      case 'health': {
        const health = await skill.healthCheck();
        console.log(`Status: ${health.status}`);
        console.log(`Message: ${health.message}`);
        break;
      }

      case 'channels': {
        const channels = await skill.listChannels();
        console.log('Channels:');
        for (const c of channels) {
          const privacy = c.isPrivate ? 'private' : 'public';
          console.log(`  #${c.name} (${privacy}, ${c.numMembers} members)`);
        }
        break;
      }

      case 'users': {
        const includeBots = args.includes('--include-bots');
        const users = await skill.listUsers(includeBots);
        console.log('Users:');
        for (const u of users) {
          const admin = u.isAdmin ? ' [admin]' : '';
          const bot = u.isBot ? ' [bot]' : '';
          console.log(`  ${u.name} (${u.realName || 'no name'})${admin}${bot}`);
        }
        break;
      }

      case 'user': {
        const userId = args[1];
        if (!userId) {
          console.error('Usage: user <user-id>');
          process.exit(1);
        }
        const user = await skill.getUserInfo(userId);
        if (user) {
          console.log(`ID: ${user.id}`);
          console.log(`Name: ${user.name}`);
          console.log(`Real Name: ${user.realName || 'N/A'}`);
          console.log(`Email: ${user.email || 'N/A'}`);
          console.log(`Admin: ${user.isAdmin}`);
          console.log(`Bot: ${user.isBot}`);
        } else {
          console.error('User not found');
        }
        break;
      }

      case 'find-user': {
        const email = args[1];
        if (!email) {
          console.error('Usage: find-user <email>');
          process.exit(1);
        }
        const user = await skill.findUserByEmail(email);
        if (user) {
          console.log(`Found: ${user.name} (${user.id})`);
          console.log(`Email: ${user.email}`);
        } else {
          console.error('User not found');
        }
        break;
      }

      case 'send': {
        const channel = args[1];
        const message = args[2];
        if (!channel || !message) {
          console.error('Usage: send <channel> <message>');
          process.exit(1);
        }
        const result = await skill.sendMessage({
          channel,
          text: message
        });
        if (result.ok) {
          console.log(`Message sent: ${result.ts}`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'dm': {
        const userId = args[1];
        const message = args[2];
        if (!userId || !message) {
          console.error('Usage: dm <user-id> <message>');
          process.exit(1);
        }
        const result = await skill.sendDirectMessage(userId, message);
        if (result.ok) {
          console.log(`Message sent: ${result.ts}`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'reply': {
        const channel = args[1];
        const threadTs = args[2];
        const message = args[3];
        if (!channel || !threadTs || !message) {
          console.error('Usage: reply <channel> <thread-ts> <message>');
          process.exit(1);
        }
        const result = await skill.replyInThread(channel, threadTs, message);
        if (result.ok) {
          console.log(`Reply sent: ${result.ts}`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'upload': {
        const channel = args[1];
        const filePath = args[2];
        const title = args[3];
        if (!channel || !filePath) {
          console.error('Usage: upload <channel> <file-path> [title]');
          process.exit(1);
        }
        const result = await skill.uploadFile({
          channels: channel,
          file: filePath,
          title
        });
        if (result.ok) {
          console.log(`File uploaded`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'create-channel': {
        const name = args[1];
        const isPrivate = args.includes('--private');
        if (!name) {
          console.error('Usage: create-channel <name> [--private]');
          process.exit(1);
        }
        const result = await skill.createChannel({ name, isPrivate });
        if (result.ok) {
          const channel = (result as any).channel;
          console.log(`Channel created: #${channel.name} (${channel.id})`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'join': {
        const channel = args[1];
        if (!channel) {
          console.error('Usage: join <channel>');
          process.exit(1);
        }
        const result = await skill.joinChannel(channel);
        if (result.ok) {
          console.log(`Joined channel`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'leave': {
        const channel = args[1];
        if (!channel) {
          console.error('Usage: leave <channel>');
          process.exit(1);
        }
        const result = await skill.leaveChannel(channel);
        if (result.ok) {
          console.log(`Left channel`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'templates': {
        const templates = await skill.listTemplates();
        console.log('Templates:');
        for (const t of templates) {
          console.log(`  ${t.name} -> ${t.channel || 'no default channel'}`);
        }
        break;
      }

      case 'template': {
        const name = args[1];
        if (!name) {
          console.error('Usage: template <name>');
          process.exit(1);
        }
        const template = await skill.getTemplate(name);
        if (template) {
          console.log(`Name: ${template.name}`);
          console.log(`Channel: ${template.channel || 'N/A'}`);
          console.log(`Text: ${template.text}`);
          if (template.blocks) {
            console.log(`Blocks: ${JSON.stringify(template.blocks, null, 2)}`);
          }
        } else {
          console.error('Template not found');
        }
        break;
      }

      case 'create-template': {
        const name = args[1];
        const channel = args[2];
        const filePath = args[3];
        if (!name || !filePath) {
          console.error('Usage: create-template <name> <channel> <file>');
          process.exit(1);
        }
        
        const fs = await import('fs');
        const text = fs.readFileSync(filePath, 'utf-8');
        
        await skill.createTemplate({
          name,
          channel,
          text
        });
        console.log(`Template created: ${name}`);
        break;
      }

      case 'delete-template': {
        const name = args[1];
        if (!name) {
          console.error('Usage: delete-template <name>');
          process.exit(1);
        }
        await skill.deleteTemplate(name);
        console.log(`Template deleted: ${name}`);
        break;
      }

      case 'notify': {
        const templateName = args[1];
        const targetChannel = args[2];
        
        if (!templateName) {
          console.error('Usage: notify <template-name> [channel]');
          process.exit(1);
        }

        // Parse template variables (--var-name=value)
        const variables: Record<string, string> = {};
        for (const arg of args) {
          if (arg.startsWith('--var-')) {
            const match = arg.match(/^--var-(.+?)=(.+)$/);
            if (match) {
              variables[match[1]] = match[2];
            }
          }
        }

        const result = await skill.sendNotification(templateName, variables, targetChannel);
        if (result.ok) {
          console.log(`Notification sent: ${result.ts}`);
        } else {
          console.error(`Failed: ${result.error}`);
        }
        break;
      }

      case 'history': {
        const limit = parseInt(args[1] || '50');
        const history = await skill.getMessageHistory(limit);
        console.log('Message History:');
        for (const h of history) {
          console.log(`  [${h.created_at}] ${h.channel}: ${h.text?.substring(0, 50)}...`);
        }
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        printUsage();
        process.exit(1);
    }
  } catch (error: any) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await skill.close();
  }
}

main();
