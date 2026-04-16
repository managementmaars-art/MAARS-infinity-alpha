import { Command } from 'commander';
import { getClient, getDialogs, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatInbox } from '../formatters/plain.js';
import { formatInboxMarkdown } from '../formatters/markdown.js';
import { getOutputFormat } from '../formatters/index.js';
import ora from 'ora';

export const inboxCommand = new Command('inbox')
  .description('Show unread messages summary')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (options) => {
    const spinner = ora('Fetching inbox...').start();

    try {
      const client = await getClient();
      const chats = await getDialogs(client, 500);
      const unreadChats = chats.filter(c => c.unreadCount > 0);

      spinner.stop();

      const format = getOutputFormat(options);

      switch (format) {
        case 'json':
          console.log(formatJson({
            totalUnread: unreadChats.reduce((sum, c) => sum + c.unreadCount, 0),
            chatsWithUnread: unreadChats.length,
            chats: unreadChats,
          }));
          break;
        case 'markdown':
          console.log(formatInboxMarkdown(chats));
          break;
        default:
          console.log(formatInbox(chats));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to fetch inbox');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
