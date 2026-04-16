---
title: Implement Database Migrations Correctly
impact: MEDIUM-HIGH
impactDescription: ensures safe and reversible schema changes
tags: database, migrations, schema, upgrade
---

## Implement Database Migrations Correctly

**Impact: MEDIUM-HIGH (ensures safe and reversible schema changes)**

Shopware uses migration classes for database schema changes. Proper migrations ensure upgrade safety and data integrity.

**Incorrect (problematic migrations):**

```php
// Bad: No timestamp in class name
namespace MyVendor\MyPlugin\Migration;

class CreateCustomTable extends MigrationStep
{
    // Will fail - missing timestamp!
}

// Bad: Destructive changes in update()
class Migration1705000000BadMigration extends MigrationStep
{
    public function update(Connection $connection): void
    {
        // Bad: Dropping columns in update() - data loss!
        $connection->executeStatement('ALTER TABLE product DROP COLUMN custom_field');

        // Bad: Truncating tables
        $connection->executeStatement('TRUNCATE TABLE custom_entity');
    }

    public function updateDestructive(Connection $connection): void
    {
        // Empty - should be here instead!
    }
}

// Bad: Not checking if migration already ran
class Migration1705000001BadCheck extends MigrationStep
{
    public function update(Connection $connection): void
    {
        // Bad: Will fail if table already exists
        $connection->executeStatement('
            CREATE TABLE custom_entity (
                id BINARY(16) NOT NULL PRIMARY KEY
            )
        ');
    }
}

// Bad: Raw SQL without schema builder
class Migration1705000002RawSql extends MigrationStep
{
    public function update(Connection $connection): void
    {
        // Bad: Platform-specific SQL, no proper escaping
        $connection->executeStatement("
            ALTER TABLE product
            ADD custom_field VARCHAR(255) DEFAULT 'value'
        ");
    }
}
```

**Correct (proper migration implementation):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Migration;

use Doctrine\DBAL\Connection;
use Doctrine\DBAL\Exception;
use Shopware\Core\Framework\Migration\MigrationStep;

// Good: Proper timestamp format (YYYYMMDDHHMMSS)
class Migration1705123456CreateCustomEntity extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1705123456;
    }

    public function update(Connection $connection): void
    {
        // Good: Check if table exists first
        $tableExists = $connection->executeQuery(
            "SHOW TABLES LIKE 'custom_entity'"
        )->rowCount() > 0;

        if ($tableExists) {
            return;
        }

        // Good: Complete table creation with proper types
        $connection->executeStatement('
            CREATE TABLE `custom_entity` (
                `id` BINARY(16) NOT NULL,
                `name` VARCHAR(255) NOT NULL,
                `description` LONGTEXT NULL,
                `active` TINYINT(1) NOT NULL DEFAULT 0,
                `priority` INT NOT NULL DEFAULT 0,
                `config` JSON NULL,
                `created_at` DATETIME(3) NOT NULL,
                `updated_at` DATETIME(3) NULL,
                PRIMARY KEY (`id`),
                INDEX `idx.custom_entity.name` (`name`),
                INDEX `idx.custom_entity.active` (`active`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ');
    }

    // Good: Destructive operations go here
    public function updateDestructive(Connection $connection): void
    {
        // Called only when explicitly running destructive migrations
        // bin/console database:migrate --all MyVendorMyPlugin
    }
}

// Good: Adding columns safely
class Migration1705123457AddProductCustomField extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1705123457;
    }

    public function update(Connection $connection): void
    {
        // Good: Check if column already exists
        if ($this->columnExists($connection, 'product', 'custom_rating')) {
            return;
        }

        $connection->executeStatement('
            ALTER TABLE `product`
            ADD COLUMN `custom_rating` DECIMAL(3,2) NULL AFTER `rating_average`
        ');
    }

    public function updateDestructive(Connection $connection): void
    {
    }

    private function columnExists(Connection $connection, string $table, string $column): bool
    {
        $sql = '
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table
            AND COLUMN_NAME = :column
        ';

        return (int) $connection->executeQuery($sql, [
            'table' => $table,
            'column' => $column,
        ])->fetchOne() > 0;
    }
}

// Good: Foreign key relationships
class Migration1705123458AddForeignKeys extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1705123458;
    }

    public function update(Connection $connection): void
    {
        // Good: Add FK with proper naming and cascade
        $this->addForeignKeyIfNotExists(
            $connection,
            'custom_entity',
            'fk.custom_entity.product_id',
            'product_id',
            'product',
            'id',
            'CASCADE',
            'CASCADE'
        );
    }

    public function updateDestructive(Connection $connection): void
    {
    }

    private function addForeignKeyIfNotExists(
        Connection $connection,
        string $table,
        string $constraintName,
        string $column,
        string $referenceTable,
        string $referenceColumn,
        string $onDelete,
        string $onUpdate
    ): void {
        $exists = $connection->executeQuery("
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
            AND TABLE_NAME = :table
            AND CONSTRAINT_NAME = :constraint
        ", ['table' => $table, 'constraint' => $constraintName])->fetchOne();

        if ($exists > 0) {
            return;
        }

        $connection->executeStatement(sprintf(
            'ALTER TABLE `%s` ADD CONSTRAINT `%s`
             FOREIGN KEY (`%s`) REFERENCES `%s` (`%s`)
             ON DELETE %s ON UPDATE %s',
            $table,
            $constraintName,
            $column,
            $referenceTable,
            $referenceColumn,
            $onDelete,
            $onUpdate
        ));
    }
}
```

**Migration naming convention:**

```
Migration{timestamp}{Description}.php
         │         │
         │         └── PascalCase description
         └── Unix timestamp or YYYYMMDDHHMMSS
```

**Migration method purposes:**

| Method | Purpose | When Run |
|--------|---------|----------|
| `update()` | Non-destructive changes | Always |
| `updateDestructive()` | Destructive changes | With `--all` flag |

Reference: [Database Migrations](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/database-migrations.html)
