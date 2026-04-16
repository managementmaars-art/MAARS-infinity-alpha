import { Command } from 'commander';
import { getClient, getMe, disconnectClient } from '../client.js';
import { formatJson } from '../formatters/json.js';
import { formatUser } from '../formatters/plain.js';
import ora from 'ora';

export const whoamiCommand = new Command('whoami')
  .description('Show logged-in account information')
  .option('--json', 'Output as JSON')
  .action(async (options) => {
    const spinner = ora('Fetching account info...').start();

    try {
      const client = await getClient();
      const me = await getMe(client);

      spinner.stop();

      if (options.json) {
        console.log(formatJson({
          id: me.id.toString(),
          firstName: me.firstName,
          lastName: me.lastName,
          username: me.username,
          phone: me.phone,
        }));
      } else {
        console.log(formatUser({
          firstName: me.firstName ?? undefined,
          lastName: me.lastName ?? undefined,
          username: me.username ?? undefined,
          phone: me.phone ?? undefined,
        }));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to get account info');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
