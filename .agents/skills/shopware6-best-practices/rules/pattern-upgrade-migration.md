---
title: Version Upgrade Patterns
impact: HIGH
impactDescription: smooth upgrades between Shopware versions
tags: upgrade, migration, compatibility, version, update
---

## Version Upgrade Patterns

**Impact: HIGH (smooth upgrades between Shopware versions)**

Follow upgrade patterns to ensure plugins work across Shopware versions. Handle deprecations, breaking changes, and version-specific code correctly.

**Correct version-aware code:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Shopware\Core\Framework\Plugin;

class VersionAwareSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly string $shopwareVersion
    ) {}

    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded'
        ];
    }

    public function onProductLoaded(EntityLoadedEvent $event): void
    {
        // Version-specific behavior
        if (version_compare($this->shopwareVersion, '6.6.0.0', '>=')) {
            $this->handleNewVersion($event);
        } else {
            $this->handleLegacyVersion($event);
        }
    }

    private function handleNewVersion(EntityLoadedEvent $event): void
    {
        // New API in 6.6+
        foreach ($event->getEntities() as $product) {
            $product->addExtension('myData', $this->loadDataNew($product));
        }
    }

    private function handleLegacyVersion(EntityLoadedEvent $event): void
    {
        // Legacy API for 6.5
        foreach ($event->getEntities() as $product) {
            $product->addExtension('myData', $this->loadDataLegacy($product));
        }
    }
}
```

**Correct update migration:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Migration;

use Doctrine\DBAL\Connection;
use Shopware\Core\Framework\Migration\MigrationStep;

class Migration1700000002UpdateSchema extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1700000002;
    }

    public function update(Connection $connection): void
    {
        // Check if update is needed
        $columns = $connection->fetchAllAssociative(
            'SHOW COLUMNS FROM `my_plugin_entity`'
        );

        $columnNames = array_column($columns, 'Field');

        // Add new column if not exists
        if (!in_array('new_field', $columnNames, true)) {
            $connection->executeStatement('
                ALTER TABLE `my_plugin_entity`
                ADD COLUMN `new_field` VARCHAR(255) NULL AFTER `name`
            ');
        }

        // Migrate data from old field to new
        if (in_array('old_field', $columnNames, true)) {
            $connection->executeStatement('
                UPDATE `my_plugin_entity`
                SET `new_field` = `old_field`
                WHERE `new_field` IS NULL AND `old_field` IS NOT NULL
            ');
        }

        // Add index for performance
        $indexes = $connection->fetchAllAssociative(
            'SHOW INDEX FROM `my_plugin_entity` WHERE Key_name = ?',
            ['idx.my_plugin_entity.new_field']
        );

        if (empty($indexes)) {
            $connection->executeStatement('
                CREATE INDEX `idx.my_plugin_entity.new_field`
                ON `my_plugin_entity` (`new_field`)
            ');
        }
    }

    public function updateDestructive(Connection $connection): void
    {
        // Remove old column (only after confirming data migrated)
        $columns = $connection->fetchAllAssociative(
            'SHOW COLUMNS FROM `my_plugin_entity`'
        );

        $columnNames = array_column($columns, 'Field');

        if (in_array('old_field', $columnNames, true)) {
            $connection->executeStatement('
                ALTER TABLE `my_plugin_entity`
                DROP COLUMN `old_field`
            ');
        }
    }
}
```

**Correct deprecation handling:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Framework\Feature;

class CompatibilityService
{
    public function processData(array $data): array
    {
        // Check if feature flag is active (new behavior)
        if (Feature::isActive('FEATURE_NEXT_12345')) {
            return $this->processNewWay($data);
        }

        // Fallback to old behavior
        return $this->processOldWay($data);
    }

    /**
     * @deprecated tag:v7.0.0 - Use processNewWay instead
     */
    private function processOldWay(array $data): array
    {
        Feature::triggerDeprecationOrThrow(
            'v7.0.0',
            'Method processOldWay is deprecated, use processNewWay instead'
        );

        // Old implementation
        return $data;
    }

    private function processNewWay(array $data): array
    {
        // New implementation
        return array_map(fn($item) => $this->transformItem($item), $data);
    }
}
```

**Correct plugin update lifecycle:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin;

use Shopware\Core\Framework\Plugin;
use Shopware\Core\Framework\Plugin\Context\UpdateContext;

class MyPlugin extends Plugin
{
    public function update(UpdateContext $updateContext): void
    {
        parent::update($updateContext);

        $currentVersion = $updateContext->getCurrentPluginVersion();
        $updateVersion = $updateContext->getUpdatePluginVersion();

        // Run version-specific updates
        if (version_compare($currentVersion, '2.0.0', '<') &&
            version_compare($updateVersion, '2.0.0', '>=')) {
            $this->updateTo2_0_0($updateContext);
        }

        if (version_compare($currentVersion, '3.0.0', '<') &&
            version_compare($updateVersion, '3.0.0', '>=')) {
            $this->updateTo3_0_0($updateContext);
        }
    }

    private function updateTo2_0_0(UpdateContext $context): void
    {
        // Migrate data structures
        $connection = $this->container->get(Connection::class);

        // Update custom fields schema
        $this->updateCustomFields($context->getContext());

        // Migrate existing data
        $connection->executeStatement('
            UPDATE product
            SET custom_fields = JSON_SET(
                COALESCE(custom_fields, "{}"),
                "$.my_plugin_new_field",
                JSON_EXTRACT(custom_fields, "$.my_plugin_old_field")
            )
            WHERE JSON_EXTRACT(custom_fields, "$.my_plugin_old_field") IS NOT NULL
        ');
    }

    private function updateTo3_0_0(UpdateContext $context): void
    {
        // Clear caches for new features
        $this->container->get('cache.object')->clear();

        // Register new scheduled tasks
        $this->registerScheduledTasks($context->getContext());

        // Update configuration defaults
        $configService = $this->container->get(SystemConfigService::class);
        $configService->set('MyPlugin.config.newFeature', true);
    }
}
```

**Correct composer.json version constraints:**

```json
{
    "name": "my-vendor/my-plugin",
    "version": "2.0.0",
    "require": {
        "shopware/core": "~6.6.0 || ~6.7.0",
        "shopware/administration": "~6.6.0 || ~6.7.0",
        "shopware/storefront": "~6.6.0 || ~6.7.0"
    },
    "extra": {
        "shopware-plugin-class": "MyVendor\\MyPlugin\\MyPlugin",
        "label": {
            "de-DE": "Mein Plugin",
            "en-GB": "My Plugin"
        },
        "description": {
            "de-DE": "Plugin Beschreibung",
            "en-GB": "Plugin description"
        }
    }
}
```

**Upgrade checklist:**

| Step | Action |
|------|--------|
| 1 | Check changelog for breaking changes |
| 2 | Update composer.json constraints |
| 3 | Run deprecation checks (`bin/console debug:deprecation`) |
| 4 | Update deprecated API calls |
| 5 | Test with new Shopware version |
| 6 | Create update migrations if needed |
| 7 | Update documentation |
| 8 | Test upgrade path from old version |

**Common breaking change patterns:**

```php
// Service ID changes
// Old: Shopware\Core\...\SomeService
// New: Check container for new ID

// Method signature changes
// Check return types and parameters

// Event changes
// Some events renamed or removed

// Removed features
// Check Feature::isActive() before using
```

Reference: [Plugin Updates](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/plugin-lifecycle.html)
