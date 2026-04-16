---
title: Command Lifecycle & Arguments
impact: MEDIUM
impactDescription: proper argument handling and command lifecycle
tags: cli, command, arguments, options, lifecycle
---

## Command Lifecycle & Arguments

**Impact: MEDIUM (proper argument handling and command lifecycle)**

Understanding the command lifecycle helps create robust CLI tools. Implement proper initialization, interaction, and execution phases.

**Incorrect (all logic in execute):**

```php
// Bad: Everything in execute, no separation of concerns
protected function execute(InputInterface $input, OutputInterface $output): int
{
    // Validation, initialization, and execution all mixed together
    if (!$input->getArgument('file')) {
        $output->writeln('File is required');
        return 1;
    }
    // ... hundreds of lines
}
```

**Correct command lifecycle:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

#[AsCommand(
    name: 'my-plugin:data:process',
    description: 'Process data from a source file'
)]
class DataProcessCommand extends Command
{
    private SymfonyStyle $io;
    private array $config = [];

    protected function configure(): void
    {
        $this
            // Required argument
            ->addArgument(
                'file',
                InputArgument::REQUIRED,
                'Path to the source file'
            )
            // Optional argument with default
            ->addArgument(
                'output-dir',
                InputArgument::OPTIONAL,
                'Output directory',
                './output'
            )
            // Array argument (must be last)
            ->addArgument(
                'filters',
                InputArgument::IS_ARRAY,
                'Filters to apply (space-separated)'
            )
            // Value option
            ->addOption(
                'format',
                'F',
                InputOption::VALUE_REQUIRED,
                'Output format',
                'json'
            )
            // Boolean option (flag)
            ->addOption(
                'verbose-output',
                null,
                InputOption::VALUE_NONE,
                'Enable verbose output'
            )
            // Option with optional value
            ->addOption(
                'config',
                'c',
                InputOption::VALUE_OPTIONAL,
                'Path to config file',
                null
            )
            // Option that can appear multiple times
            ->addOption(
                'exclude',
                'e',
                InputOption::VALUE_REQUIRED | InputOption::VALUE_IS_ARRAY,
                'Patterns to exclude'
            );
    }

    /**
     * Initialize: Called before interact() and execute()
     * Use for setting up resources needed by both methods
     */
    protected function initialize(InputInterface $input, OutputInterface $output): void
    {
        $this->io = new SymfonyStyle($input, $output);

        // Load configuration
        $configPath = $input->getOption('config');
        if ($configPath && file_exists($configPath)) {
            $this->config = json_decode(file_get_contents($configPath), true) ?? [];
            $this->io->note('Loaded configuration from: ' . $configPath);
        }

        // Validate file exists
        $file = $input->getArgument('file');
        if (!file_exists($file)) {
            throw new \InvalidArgumentException(sprintf('File not found: %s', $file));
        }
    }

    /**
     * Interact: Called after initialize, before execute
     * Use for asking interactive questions when arguments/options are missing
     */
    protected function interact(InputInterface $input, OutputInterface $output): void
    {
        // Only interact if running interactively
        if (!$input->isInteractive()) {
            return;
        }

        // Ask for format if not provided via option
        if (!$input->getOption('format')) {
            $format = $this->io->choice(
                'Select output format',
                ['json', 'csv', 'xml'],
                'json'
            );
            $input->setOption('format', $format);
        }

        // Confirm output directory
        $outputDir = $input->getArgument('output-dir');
        if (!is_dir($outputDir)) {
            if ($this->io->confirm(sprintf('Create output directory "%s"?', $outputDir), true)) {
                mkdir($outputDir, 0755, true);
            } else {
                throw new \RuntimeException('Output directory does not exist');
            }
        }
    }

    /**
     * Execute: Main command logic
     */
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $file = $input->getArgument('file');
        $outputDir = $input->getArgument('output-dir');
        $filters = $input->getArgument('filters');
        $format = $input->getOption('format');
        $excludePatterns = $input->getOption('exclude');
        $verboseOutput = $input->getOption('verbose-output');

        $this->io->title('Data Processing');

        // Show configuration summary
        if ($verboseOutput || $output->isVerbose()) {
            $this->io->section('Configuration');
            $this->io->listing([
                'Source: ' . $file,
                'Output: ' . $outputDir,
                'Format: ' . $format,
                'Filters: ' . (empty($filters) ? 'none' : implode(', ', $filters)),
                'Excludes: ' . (empty($excludePatterns) ? 'none' : implode(', ', $excludePatterns))
            ]);
        }

        try {
            // Load data
            $this->io->section('Loading data');
            $data = $this->loadData($file);
            $this->io->text(sprintf('Loaded %d records', count($data)));

            // Apply filters
            if (!empty($filters)) {
                $this->io->section('Applying filters');
                $data = $this->applyFilters($data, $filters);
                $this->io->text(sprintf('%d records after filtering', count($data)));
            }

            // Apply exclusions
            if (!empty($excludePatterns)) {
                $data = $this->applyExclusions($data, $excludePatterns);
                $this->io->text(sprintf('%d records after exclusions', count($data)));
            }

            // Process data
            $this->io->section('Processing');
            $this->io->progressStart(count($data));

            $results = [];
            foreach ($data as $item) {
                $results[] = $this->processItem($item);
                $this->io->progressAdvance();
            }

            $this->io->progressFinish();

            // Write output
            $this->io->section('Writing output');
            $outputFile = $this->writeOutput($results, $outputDir, $format);
            $this->io->text('Written to: ' . $outputFile);

            $this->io->success(sprintf('Processed %d records successfully.', count($results)));

            return Command::SUCCESS;

        } catch (\Exception $e) {
            $this->io->error('Processing failed: ' . $e->getMessage());

            if ($output->isVeryVerbose()) {
                $this->io->section('Stack Trace');
                $this->io->text($e->getTraceAsString());
            }

            return Command::FAILURE;
        }
    }

    private function loadData(string $file): array
    {
        $content = file_get_contents($file);
        return json_decode($content, true) ?? [];
    }

    private function applyFilters(array $data, array $filters): array
    {
        // Filter implementation
        return array_filter($data, function ($item) use ($filters) {
            foreach ($filters as $filter) {
                [$field, $value] = explode('=', $filter);
                if (($item[$field] ?? null) !== $value) {
                    return false;
                }
            }
            return true;
        });
    }

    private function applyExclusions(array $data, array $patterns): array
    {
        return array_filter($data, function ($item) use ($patterns) {
            foreach ($patterns as $pattern) {
                if (fnmatch($pattern, $item['name'] ?? '')) {
                    return false;
                }
            }
            return true;
        });
    }

    private function processItem(array $item): array
    {
        // Processing logic
        return $item;
    }

    private function writeOutput(array $data, string $dir, string $format): string
    {
        $filename = sprintf('%s/output_%s.%s', $dir, date('Y-m-d_His'), $format);

        $content = match ($format) {
            'json' => json_encode($data, JSON_PRETTY_PRINT),
            'csv' => $this->toCsv($data),
            'xml' => $this->toXml($data),
            default => throw new \InvalidArgumentException('Unsupported format: ' . $format)
        };

        file_put_contents($filename, $content);

        return $filename;
    }
}
```

**Argument and option types:**

| Type | Description | Example |
|------|-------------|---------|
| `REQUIRED` | Must be provided | `file` |
| `OPTIONAL` | Can be omitted | `output-dir` |
| `IS_ARRAY` | Multiple values | `filters` |
| `VALUE_NONE` | Boolean flag | `--force` |
| `VALUE_REQUIRED` | Must have value | `--format=json` |
| `VALUE_OPTIONAL` | Value is optional | `--config[=path]` |
| `VALUE_IS_ARRAY` | Can repeat | `--exclude=a --exclude=b` |

**Command lifecycle order:**

1. `configure()` - Define arguments and options
2. `initialize()` - Set up resources
3. `interact()` - Ask missing inputs
4. `execute()` - Run command logic

Reference: [Symfony Console](https://symfony.com/doc/current/console.html)
