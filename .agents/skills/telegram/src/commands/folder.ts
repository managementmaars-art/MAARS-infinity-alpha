import { Command } from 'commander';
import { getClient, getFolder, disconnectClient } from '../client.js';
import { formatFolder } from '../formatters/plain.js';
import ora from 'ora';

export const folderCommand = new Command('folder')
  .description('Show chats in a specific folder')
  .argument('<name>', 'Folder name')
  .option('--json', 'Output as JSON')
  .action(async (name, options) => {
    const spinner = ora(`Loading folder "${name}"...`).start();

    try {
      const client = await getClient();
      const folder = await getFolder(client, name);

      spinner.stop();

      if (!folder) {
        console.error(`Folder not found: ${name}`);
        process.exit(1);
      }

      if (options.json) {
        console.log(JSON.stringify(folder, null, 2));
      } else {
        console.log(formatFolder(folder));
      }

      await disconnectClient();
    } catch (error) {
      spinner.fail('Failed to load folder');
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });
