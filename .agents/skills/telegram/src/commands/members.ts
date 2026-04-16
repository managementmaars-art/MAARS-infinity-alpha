import { Command } from 'commander';
import { getClient, getChatMembers, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatMembers } from '../formatters/plain.js';
import { formatMembersMarkdown } from '../formatters/markdown.js';
import { getOutputFormat } from '../formatters/index.js';
import ora from 'ora';

export const membersCommand = new Command('members')
  .description('List group members')
  .argument('<group>', 'Group name or username')
  .option('-n, --limit <number>', 'Maximum members to fetch', '200')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (group, options) => {
    const spinner = ora(`Fetching members of "${group}"...`).start();

    try {
      const client = await getClient();
      const members = await getChatMembers(client, group, {
        limit: parseInt(options.limit),
      });

      spinner.stop();

      const format = getOutputFormat(options);

      switch (format) {
        case 'json':
          console.log(formatJson(members));
          break;
        case 'markdown':
          console.log(formatMembersMarkdown(members));
          break;
        default:
          console.log(formatMembers(members));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to fetch members');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

export const adminsCommand = new Command('admins')
  .description('List group admins')
  .argument('<group>', 'Group name or username')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (group, options) => {
    const spinner = ora(`Fetching admins of "${group}"...`).start();

    try {
      const client = await getClient();
      const members = await getChatMembers(client, group, {
        adminsOnly: true,
      });

      spinner.stop();

      const format = getOutputFormat(options);

      switch (format) {
        case 'json':
          console.log(formatJson(members));
          break;
        case 'markdown':
          console.log(formatMembersMarkdown(members));
          break;
        default:
          console.log(formatMembers(members));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to fetch admins');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
