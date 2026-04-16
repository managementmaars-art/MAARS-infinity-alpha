import { Command } from 'commander';
import { getClient, searchMessages, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatMessages } from '../formatters/plain.js';
import { formatMessagesMarkdown } from '../formatters/markdown.js';
import { getOutputFormat } from '../formatters/index.js';
import chalk from 'chalk';
import ora from 'ora';

export const searchCommand = new Command('search')
  .description('Search messages')
  .argument('<query>', 'Search query')
  .option('--chat <name>', 'Search within specific chat')
  .option('--all', 'Search all chats (global search)')
  .option('-n, --limit <number>', 'Maximum results', '50')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (query, options) => {
    const scope = options.chat ? `"${options.chat}"` : 'all chats';
    const spinner = ora(`Searching for "${query}" in ${scope}...`).start();

    try {
      const client = await getClient();

      const results = await searchMessages(client, query, {
        chat: options.chat,
        limit: parseInt(options.limit),
      });

      spinner.stop();

      const format = getOutputFormat(options);

      if (format === 'json') {
        console.log(formatJson(results));
      } else {
        for (const result of results) {
          if (result.messages.length === 0) {
            console.log(chalk.yellow('No results found.'));
            continue;
          }

          if (format === 'markdown') {
            console.log(formatMessagesMarkdown(result.messages, result.chatTitle));
          } else {
            console.log(formatMessages(result.messages, result.chatTitle));
          }
        }
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Search failed');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
