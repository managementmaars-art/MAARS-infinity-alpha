---
title: PHPStan & Code Quality
impact: MEDIUM
impactDescription: automated code quality checks
tags: devops, phpstan, static-analysis, quality, linting
---

## PHPStan & Code Quality

**Impact: MEDIUM (automated code quality checks)**

Use PHPStan and other static analysis tools to catch errors before runtime. Configure proper rule sets for Shopware-specific patterns.

**Correct phpstan.neon configuration:**

```neon
# phpstan.neon

includes:
    - vendor/phpstan/phpstan/conf/bleedingEdge.neon
    - vendor/shopware/core/DevOps/StaticAnalyze/PHPStan/extension.neon
    - vendor/shopware/core/DevOps/StaticAnalyze/PHPStan/rules.neon

parameters:
    level: 8

    paths:
        - src
        - tests

    excludePaths:
        - src/Resources
        - src/Migration

    bootstrapFiles:
        - vendor/shopware/core/DevOps/StaticAnalyze/PHPStan/phpstan-bootstrap.php

    # Shopware specific settings
    shopware:
        checkClassHierarchy: true

    # Type coverage
    reportUnmatchedIgnoredErrors: true
    treatPhpDocTypesAsCertain: false

    # Ignore patterns
    ignoreErrors:
        # Ignore deprecation notices for now
        - '#Method .* is deprecated#'

        # Ignore dynamic property access in entities
        - '#Access to an undefined property Shopware\\Core\\.*Entity::\$#'

        # Ignore test mock returns
        -
            message: '#Method .* should return .* but returns MockObject#'
            path: tests/*

    # Symfony container settings
    symfony:
        container_xml_path: var/cache/phpstan_dev/Shopware_Core_DevOps_StaticAnalyze_StaticAnalyzeKernelPhpstan_devDebugContainer.xml
```

**Correct composer.json for development tools:**

```json
{
    "require-dev": {
        "phpstan/phpstan": "^1.10",
        "phpstan/phpstan-symfony": "^1.3",
        "phpstan/phpstan-phpunit": "^1.3",
        "phpstan/phpstan-deprecation-rules": "^1.1",
        "phpstan/phpstan-strict-rules": "^1.5",
        "phpunit/phpunit": "^10.5",
        "squizlabs/php_codesniffer": "^3.8",
        "friendsofphp/php-cs-fixer": "^3.45",
        "rector/rector": "^0.19"
    },
    "scripts": {
        "phpstan": "phpstan analyse --memory-limit=2G",
        "phpcs": "phpcs --standard=PSR12 src/",
        "phpcs-fix": "phpcbf --standard=PSR12 src/",
        "cs-fix": "php-cs-fixer fix --config=.php-cs-fixer.php",
        "test": "phpunit --configuration phpunit.xml.dist",
        "test-coverage": "phpunit --configuration phpunit.xml.dist --coverage-html coverage/",
        "quality": [
            "@phpstan",
            "@phpcs",
            "@test"
        ]
    }
}
```

**Correct PHP-CS-Fixer configuration:**

```php
<?php
// .php-cs-fixer.php

$finder = PhpCsFixer\Finder::create()
    ->in(__DIR__ . '/src')
    ->in(__DIR__ . '/tests')
    ->exclude('Resources')
    ->exclude('Migration');

return (new PhpCsFixer\Config())
    ->setRiskyAllowed(true)
    ->setRules([
        '@PSR12' => true,
        '@Symfony' => true,
        '@PHP82Migration' => true,

        // Strict rules
        'declare_strict_types' => true,
        'strict_param' => true,
        'strict_comparison' => true,

        // Array notation
        'array_syntax' => ['syntax' => 'short'],
        'no_trailing_comma_in_singleline_array' => true,
        'trailing_comma_in_multiline' => ['elements' => ['arrays', 'arguments', 'parameters']],

        // Imports
        'ordered_imports' => ['sort_algorithm' => 'alpha'],
        'no_unused_imports' => true,
        'global_namespace_import' => [
            'import_classes' => true,
            'import_constants' => false,
            'import_functions' => false,
        ],

        // PHPDoc
        'phpdoc_align' => ['align' => 'left'],
        'phpdoc_order' => true,
        'phpdoc_separation' => true,
        'no_superfluous_phpdoc_tags' => ['allow_mixed' => true],

        // Spacing
        'concat_space' => ['spacing' => 'one'],
        'binary_operator_spaces' => ['default' => 'single_space'],
        'method_argument_space' => ['on_multiline' => 'ensure_fully_multiline'],

        // Other
        'yoda_style' => false,
        'single_line_throw' => false,
        'void_return' => true,
    ])
    ->setFinder($finder);
```

**Correct Rector configuration for upgrades:**

```php
<?php
// rector.php

use Rector\Config\RectorConfig;
use Rector\Set\ValueObject\LevelSetList;
use Rector\Symfony\Set\SymfonySetList;

return static function (RectorConfig $rectorConfig): void {
    $rectorConfig->paths([
        __DIR__ . '/src',
    ]);

    $rectorConfig->skip([
        __DIR__ . '/src/Resources',
        __DIR__ . '/src/Migration',
    ]);

    // PHP 8.2 compatibility
    $rectorConfig->sets([
        LevelSetList::UP_TO_PHP_82,
    ]);

    // Symfony upgrades
    $rectorConfig->sets([
        SymfonySetList::SYMFONY_64,
    ]);

    // Custom rules
    $rectorConfig->rules([
        // Add specific rules
    ]);
};
```

**Correct pre-commit hook (.husky/pre-commit):**

```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Run PHP-CS-Fixer on staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.php$')

if [ -n "$STAGED_FILES" ]; then
    echo "Checking PHP code style..."
    vendor/bin/php-cs-fixer fix --config=.php-cs-fixer.php --dry-run --diff $STAGED_FILES

    if [ $? -ne 0 ]; then
        echo "Code style issues found. Run 'composer cs-fix' to fix."
        exit 1
    fi

    echo "Running PHPStan..."
    vendor/bin/phpstan analyse $STAGED_FILES --memory-limit=512M

    if [ $? -ne 0 ]; then
        echo "Static analysis errors found."
        exit 1
    fi
fi

# Run JS/TS linting for admin changes
STAGED_JS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|ts|vue)$')

if [ -n "$STAGED_JS" ]; then
    echo "Checking JavaScript/TypeScript..."
    cd src/Resources/app/administration
    npm run lint

    if [ $? -ne 0 ]; then
        echo "JavaScript linting errors found."
        exit 1
    fi
    cd -
fi

echo "Pre-commit checks passed!"
```

**CI quality gates:**

```yaml
# .github/workflows/quality.yml

name: Code Quality

on:
  pull_request:
  push:
    branches: [main]

jobs:
  phpstan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
          coverage: none
      - run: composer install --no-progress
      - run: vendor/bin/phpstan analyse --error-format=github

  phpcs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
      - run: composer install --no-progress
      - run: vendor/bin/phpcs --standard=PSR12 --report=checkstyle src/ | cs2pr

  tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: shopware_test
          MYSQL_ROOT_PASSWORD: root
        ports:
          - 3306:3306
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
          coverage: xdebug
      - run: composer install --no-progress
      - run: vendor/bin/phpunit --coverage-clover=coverage.xml
      - uses: codecov/codecov-action@v3
```

Reference: [PHPStan](https://phpstan.org/user-guide/getting-started)
