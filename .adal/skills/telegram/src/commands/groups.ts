import { Command } from 'commander';
import { getClient, getDialogs, getAdminGroups, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatChats } from '../formatters/plain.js';
import { formatChatsMarkdown } from '../formatters/markdown.js';
import { getOutputFormat } from '../formatters/index.js';
import ora from 'ora';

export const groupsCommand = new Command('groups')
  .description('List groups')
  .option('--admin', 'Only show groups where you are admin')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (options) => {
    const spinner = ora('Fetching groups...').start();

    try {
      const client = await getClient();

      let groups;

      if (options.admin) {
        groups = await getAdminGroups(client);
      } else {
        const allChats = await getDialogs(client, 500);
        groups = allChats.filter(c => c.type === 'group' || c.type === 'supergroup');
      }

      spinner.stop();

      const format = getOutputFormat(options);

      switch (format) {
        case 'json':
          console.log(formatJson(groups));
          break;
        case 'markdown':
          console.log(formatChatsMarkdown(groups));
          break;
        default:
          console.log(formatChats(groups));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to fetch groups');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
