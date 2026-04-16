---
title: Progress Bars & Output Formatting
impact: MEDIUM
impactDescription: user-friendly CLI output for long-running tasks
tags: cli, progress, output, formatting, ux
---

## Progress Bars & Output Formatting

**Impact: MEDIUM (user-friendly CLI output for long-running tasks)**

Proper output formatting and progress indication makes CLI tools user-friendly. Use SymfonyStyle and progress bars for professional output.

**Incorrect (poor output formatting):**

```php
// Bad: Unformatted output, no progress indication
protected function execute(InputInterface $input, OutputInterface $output): int
{
    echo "Starting...\n";
    foreach ($items as $item) {
        echo "Processing " . $item->getId() . "\n";
        $this->process($item);
    }
    echo "Done\n";
    return 0;
}
```

**Correct output formatting:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

use Symfony\Component\Console\Helper\ProgressBar;
use Symfony\Component\Console\Helper\Table;
use Symfony\Component\Console\Helper\TableSeparator;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

#[AsCommand(name: 'my-plugin:demo:output')]
class OutputDemoCommand extends Command
{
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        // Title and section headers
        $io->title('Output Formatting Demo');
        $io->section('Basic Output');

        // Text output
        $io->text('This is regular text output.');
        $io->text([
            'Multiple lines can be passed',
            'as an array of strings.'
        ]);

        // Listings
        $io->section('Listings');
        $io->listing([
            'First item',
            'Second item',
            'Third item'
        ]);

        // Definition list
        $io->section('Definition List');
        $io->definitionList(
            ['Product' => 'Laptop Pro X'],
            ['Price' => '€1,299.00'],
            ['Stock' => '42 units'],
            new TableSeparator(),
            ['Status' => 'Active']
        );

        // Tables
        $io->section('Tables');
        $io->table(
            ['ID', 'Product', 'Price', 'Stock'],
            [
                ['P001', 'Laptop Pro X', '€1,299.00', 42],
                ['P002', 'Wireless Mouse', '€49.99', 156],
                ['P003', 'USB-C Hub', '€79.00', 88]
            ]
        );

        // Horizontal table
        $io->horizontalTable(
            ['ID', 'Name', 'Status'],
            [
                ['P001', 'Product A', 'Active'],
                ['P002', 'Product B', 'Inactive']
            ]
        );

        // Messages
        $io->section('Message Types');
        $io->success('Operation completed successfully!');
        $io->error('An error occurred during processing.');
        $io->warning('This action cannot be undone.');
        $io->note('Remember to backup your data first.');
        $io->info('Processing will take approximately 5 minutes.');
        $io->caution('High resource usage expected.');

        // Blocks
        $io->section('Blocks');
        $io->block(
            'This is a custom block with important information.',
            'IMPORTANT',
            'fg=white;bg=blue',
            ' ! ',
            true
        );

        return Command::SUCCESS;
    }
}
```

**Correct progress bar usage:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

#[AsCommand(name: 'my-plugin:process:batch')]
class BatchProcessCommand extends Command
{
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        // Simple progress with SymfonyStyle
        $io->title('Batch Processing');

        $items = $this->loadItems();
        $total = count($items);

        $io->progressStart($total);

        foreach ($items as $item) {
            $this->processItem($item);
            $io->progressAdvance();
        }

        $io->progressFinish();

        // Advanced progress bar with custom format
        $io->section('Advanced Progress');

        $progressBar = new ProgressBar($output, $total);
        $progressBar->setFormat('custom');
        ProgressBar::setFormatDefinition(
            'custom',
            ' %current%/%max% [%bar%] %percent:3s%% %elapsed:6s%/%estimated:-6s% %memory:6s%'
        );

        $progressBar->start();

        foreach ($items as $item) {
            $this->processItem($item);
            $progressBar->advance();
        }

        $progressBar->finish();
        $output->writeln('');

        // Progress with message
        $io->section('Progress with Messages');

        $progressBar = $io->createProgressBar($total);
        $progressBar->setFormat(
            "%current%/%max% [%bar%] %percent:3s%%\n%message%"
        );

        foreach ($items as $index => $item) {
            $progressBar->setMessage(sprintf('Processing: %s', $item->getName()));
            $progressBar->advance();
            $this->processItem($item);
        }

        $progressBar->setMessage('Complete!');
        $progressBar->finish();
        $output->writeln('');

        return Command::SUCCESS;
    }
}
```

**Correct multi-stage processing:**

```php
#[AsCommand(name: 'my-plugin:import:full')]
class FullImportCommand extends Command
{
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        $io->title('Full Data Import');

        // Stage 1: Download
        $io->section('Stage 1/4: Downloading data');
        $this->downloadWithProgress($io, $output);

        // Stage 2: Parse
        $io->section('Stage 2/4: Parsing files');
        $records = $this->parseWithProgress($io, $output);

        // Stage 3: Validate
        $io->section('Stage 3/4: Validating records');
        $validRecords = $this->validateWithProgress($io, $output, $records);

        // Stage 4: Import
        $io->section('Stage 4/4: Importing to database');
        $results = $this->importWithProgress($io, $output, $validRecords);

        // Final summary
        $io->section('Import Summary');

        $io->table(
            ['Metric', 'Count'],
            [
                ['Total Records', count($records)],
                ['Valid Records', count($validRecords)],
                ['Imported', $results['imported']],
                ['Updated', $results['updated']],
                ['Skipped', $results['skipped']],
                ['Errors', $results['errors']]
            ]
        );

        if ($results['errors'] > 0) {
            $io->warning(sprintf('%d records failed to import.', $results['errors']));
            $io->text('Check the log file for details: var/log/my_plugin_import.log');
            return Command::FAILURE;
        }

        $io->success('Import completed successfully!');

        return Command::SUCCESS;
    }

    private function downloadWithProgress(SymfonyStyle $io, OutputInterface $output): void
    {
        $progressBar = new ProgressBar($output);
        $progressBar->setFormat(' Downloading: [%bar%] %percent:3s%%');

        $progressBar->start(100);
        for ($i = 0; $i <= 100; $i += 10) {
            usleep(100000); // Simulate download
            $progressBar->setProgress($i);
        }
        $progressBar->finish();
        $output->writeln('');

        $io->text('Downloaded 3 files (2.4 MB)');
    }

    private function importWithProgress(SymfonyStyle $io, OutputInterface $output, array $records): array
    {
        $results = ['imported' => 0, 'updated' => 0, 'skipped' => 0, 'errors' => 0];

        $io->progressStart(count($records));

        foreach ($records as $record) {
            try {
                $result = $this->importRecord($record);
                $results[$result]++;
            } catch (\Exception $e) {
                $results['errors']++;
            }
            $io->progressAdvance();
        }

        $io->progressFinish();

        return $results;
    }
}
```

**Correct verbosity-aware output:**

```php
protected function execute(InputInterface $input, OutputInterface $output): int
{
    $io = new SymfonyStyle($input, $output);

    // Always shown
    $io->title('Data Processing');

    // Shown with -v
    if ($output->isVerbose()) {
        $io->section('Configuration');
        $io->listing([
            'Source: ' . $this->getSource(),
            'Target: ' . $this->getTarget()
        ]);
    }

    foreach ($items as $item) {
        // Shown with -vv
        if ($output->isVeryVerbose()) {
            $io->text(sprintf('Processing item: %s', $item->getId()));
        }

        // Shown with -vvv
        if ($output->isDebug()) {
            $io->text(sprintf('  Data: %s', json_encode($item->getData())));
        }

        $this->process($item);
    }

    $io->success('Done!');

    return Command::SUCCESS;
}
```

**Output verbosity levels:**

| Flag | Method | Use Case |
|------|--------|----------|
| (none) | `isQuiet()` | Essential output only |
| `-v` | `isVerbose()` | Additional info |
| `-vv` | `isVeryVerbose()` | Detailed progress |
| `-vvv` | `isDebug()` | Debug information |

Reference: [Console Output](https://symfony.com/doc/current/console/style.html)
