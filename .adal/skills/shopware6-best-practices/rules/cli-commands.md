---
title: Custom Console Commands
impact: HIGH
impactDescription: developer productivity for maintenance and automation tasks
tags: cli, command, console, symfony, automation
---

## Custom Console Commands

**Impact: HIGH (developer productivity for maintenance and automation tasks)**

Console commands enable automation, maintenance tasks, and developer tools. Use Symfony's console component correctly with proper arguments, options, and error handling.

**Incorrect (minimal command without proper structure):**

```php
// Bad: No input validation, no progress indication, no error handling
class ImportCommand extends Command
{
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $products = file_get_contents('/path/to/products.csv');
        // Process without feedback...
        return 0;
    }
}
```

**Correct command implementation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

use Shopware\Core\Framework\Context;
use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

#[AsCommand(
    name: 'my-plugin:product:sync',
    description: 'Synchronize products with external system',
    aliases: ['my:sync']
)]
class ProductSyncCommand extends Command
{
    public function __construct(
        private readonly ProductSyncService $syncService,
        private readonly EntityRepository $productRepository,
        private readonly LoggerInterface $logger
    ) {
        parent::__construct();
    }

    protected function configure(): void
    {
        $this
            ->addArgument(
                'product-ids',
                InputArgument::OPTIONAL | InputArgument::IS_ARRAY,
                'Specific product IDs to sync (space-separated)'
            )
            ->addOption(
                'limit',
                'l',
                InputOption::VALUE_REQUIRED,
                'Maximum number of products to sync',
                '100'
            )
            ->addOption(
                'force',
                'f',
                InputOption::VALUE_NONE,
                'Force sync even if already synced'
            )
            ->addOption(
                'dry-run',
                null,
                InputOption::VALUE_NONE,
                'Show what would be synced without making changes'
            )
            ->addOption(
                'since',
                's',
                InputOption::VALUE_REQUIRED,
                'Only sync products updated since this date (Y-m-d format)'
            )
            ->setHelp(<<<'HELP'
The <info>%command.name%</info> command synchronizes products with the external system.

Sync all products:
    <info>php %command.full_name%</info>

Sync specific products:
    <info>php %command.full_name% abc123 def456</info>

Sync with limit:
    <info>php %command.full_name% --limit=50</info>

Dry run (preview without changes):
    <info>php %command.full_name% --dry-run</info>

Sync products updated since date:
    <info>php %command.full_name% --since=2024-01-01</info>
HELP
            );
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $context = Context::createDefaultContext();

        $productIds = $input->getArgument('product-ids');
        $limit = (int) $input->getOption('limit');
        $force = $input->getOption('force');
        $dryRun = $input->getOption('dry-run');
        $since = $input->getOption('since');

        // Validate date option
        if ($since !== null) {
            try {
                $sinceDate = new \DateTime($since);
            } catch (\Exception $e) {
                $io->error('Invalid date format. Use Y-m-d (e.g., 2024-01-01)');
                return Command::FAILURE;
            }
        }

        $io->title('Product Synchronization');

        if ($dryRun) {
            $io->warning('DRY RUN MODE - No changes will be made');
        }

        // Build criteria
        $criteria = $this->buildCriteria($productIds, $limit, $force, $sinceDate ?? null);

        // Get products to sync
        $products = $this->productRepository->search($criteria, $context);

        if ($products->count() === 0) {
            $io->success('No products to sync.');
            return Command::SUCCESS;
        }

        $io->info(sprintf('Found %d products to sync', $products->count()));

        // Confirm if many products
        if ($products->count() > 50 && !$dryRun) {
            if (!$io->confirm('This will sync many products. Continue?', false)) {
                $io->warning('Aborted.');
                return Command::SUCCESS;
            }
        }

        // Process with progress bar
        $io->progressStart($products->count());

        $successCount = 0;
        $errorCount = 0;
        $errors = [];

        foreach ($products as $product) {
            try {
                if (!$dryRun) {
                    $this->syncService->syncProduct($product->getId(), $context);
                }
                $successCount++;

            } catch (\Exception $e) {
                $errorCount++;
                $errors[] = [
                    'product' => $product->getProductNumber(),
                    'error' => $e->getMessage()
                ];

                $this->logger->error('Product sync failed', [
                    'productId' => $product->getId(),
                    'error' => $e->getMessage()
                ]);
            }

            $io->progressAdvance();
        }

        $io->progressFinish();

        // Summary
        $io->newLine(2);
        $io->section('Sync Summary');

        $io->definitionList(
            ['Total Products' => $products->count()],
            ['Successful' => $successCount],
            ['Failed' => $errorCount]
        );

        // Show errors if any
        if (!empty($errors)) {
            $io->section('Errors');
            $io->table(
                ['Product', 'Error'],
                array_map(fn($e) => [$e['product'], $e['error']], $errors)
            );
        }

        if ($errorCount > 0) {
            $io->warning(sprintf('%d products failed to sync. Check logs for details.', $errorCount));
            return Command::FAILURE;
        }

        $io->success(sprintf('Successfully synced %d products.', $successCount));
        return Command::SUCCESS;
    }

    private function buildCriteria(
        array $productIds,
        int $limit,
        bool $force,
        ?\DateTime $since
    ): Criteria {
        if (!empty($productIds)) {
            $criteria = new Criteria($productIds);
        } else {
            $criteria = new Criteria();
            $criteria->setLimit($limit);
            $criteria->addSorting(new FieldSorting('updatedAt', FieldSorting::DESCENDING));
        }

        $criteria->addFilter(new EqualsFilter('active', true));

        // Only products not yet synced (unless force)
        if (!$force) {
            $criteria->addFilter(new MultiFilter(MultiFilter::CONNECTION_OR, [
                new EqualsFilter('customFields.my_plugin_sync_status', null),
                new EqualsFilter('customFields.my_plugin_sync_status', 'pending'),
                new EqualsFilter('customFields.my_plugin_sync_status', 'error')
            ]));
        }

        // Filter by update date
        if ($since) {
            $criteria->addFilter(new RangeFilter('updatedAt', [
                RangeFilter::GTE => $since->format('Y-m-d H:i:s')
            ]));
        }

        return $criteria;
    }
}
```

**Service registration:**

```xml
<service id="MyVendor\MyPlugin\Command\ProductSyncCommand">
    <argument type="service" id="MyVendor\MyPlugin\Service\ProductSyncService"/>
    <argument type="service" id="product.repository"/>
    <argument type="service" id="logger"/>
    <tag name="console.command"/>
</service>
```

**Interactive command example:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

#[AsCommand(
    name: 'my-plugin:config:setup',
    description: 'Interactive setup wizard for plugin configuration'
)]
class SetupWizardCommand extends Command
{
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        $io->title('My Plugin Setup Wizard');
        $io->text('This wizard will help you configure the plugin.');
        $io->newLine();

        // API Configuration
        $io->section('API Configuration');

        $apiUrl = $io->ask(
            'Enter the API base URL',
            'https://api.example.com',
            function ($value) {
                if (!filter_var($value, FILTER_VALIDATE_URL)) {
                    throw new \RuntimeException('Invalid URL format');
                }
                return $value;
            }
        );

        $clientId = $io->ask('Enter your Client ID');

        $clientSecret = $io->askHidden('Enter your Client Secret (hidden)');

        // Connection test
        $io->section('Testing Connection');

        try {
            $io->text('Connecting to API...');
            $this->testConnection($apiUrl, $clientId, $clientSecret);
            $io->success('Connection successful!');

        } catch (\Exception $e) {
            $io->error('Connection failed: ' . $e->getMessage());

            if (!$io->confirm('Save configuration anyway?', false)) {
                return Command::FAILURE;
            }
        }

        // Feature selection
        $io->section('Features');

        $features = $io->choice(
            'Select features to enable',
            ['Product Sync', 'Order Export', 'Customer Import', 'All'],
            'All',
            true // Multiple selection
        );

        // Sync options
        $syncInterval = $io->choice(
            'How often should products sync?',
            ['Every hour', 'Every 6 hours', 'Once daily', 'Manual only'],
            'Every 6 hours'
        );

        // Confirmation
        $io->section('Configuration Summary');

        $io->table(
            ['Setting', 'Value'],
            [
                ['API URL', $apiUrl],
                ['Client ID', $clientId],
                ['Features', implode(', ', $features)],
                ['Sync Interval', $syncInterval]
            ]
        );

        if (!$io->confirm('Save this configuration?', true)) {
            $io->warning('Setup cancelled.');
            return Command::SUCCESS;
        }

        // Save configuration
        $this->saveConfiguration([
            'apiUrl' => $apiUrl,
            'clientId' => $clientId,
            'clientSecret' => $clientSecret,
            'features' => $features,
            'syncInterval' => $syncInterval
        ]);

        $io->success('Configuration saved successfully!');

        $io->note([
            'Next steps:',
            '1. Run "bin/console my-plugin:product:sync" to start syncing',
            '2. Check the documentation for advanced configuration'
        ]);

        return Command::SUCCESS;
    }
}
```

**Common command patterns:**

| Pattern | Use Case |
|---------|----------|
| `--dry-run` | Preview changes without executing |
| `--force` | Override safety checks |
| `--limit` | Process subset of data |
| `--since` | Filter by date |
| `-v/-vv/-vvv` | Verbosity levels (built-in) |
| `--no-interaction` | Non-interactive mode |

Reference: [Console Commands](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-custom-commands.html)
