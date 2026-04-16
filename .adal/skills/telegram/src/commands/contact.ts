import { Command } from 'commander';
import { getClient, getContactInfo, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatContact } from '../formatters/plain.js';
import { formatContactMarkdown } from '../formatters/markdown.js';
import { getOutputFormat } from '../formatters/index.js';
import ora from 'ora';

export const contactCommand = new Command('contact')
  .description('Get contact information')
  .argument('<user>', 'Username (@user) or phone number')
  .option('--json', 'Output as JSON')
  .option('--markdown', 'Output as Markdown')
  .action(async (user, options) => {
    const spinner = ora(`Fetching contact info for "${user}"...`).start();

    try {
      const client = await getClient();
      const contact = await getContactInfo(client, user);

      spinner.stop();

      const format = getOutputFormat(options);

      switch (format) {
        case 'json':
          console.log(formatJson(contact));
          break;
        case 'markdown':
          console.log(formatContactMarkdown(contact));
          break;
        default:
          console.log(formatContact(contact));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to fetch contact info');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
