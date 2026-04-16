---
title: Follow Proper Plugin Structure
impact: CRITICAL
impactDescription: ensures plugin discovery and correct initialization
tags: plugin, structure, composer, bootstrap
---

## Follow Proper Plugin Structure

**Impact: CRITICAL (ensures plugin discovery and correct initialization)**

Shopware 6 plugins must follow a specific directory structure and composer configuration to be properly discovered and loaded by the platform.

**Incorrect (broken plugin structure):**

```
custom/plugins/MyPlugin/
├── MyPlugin.php              # Wrong location - must be in src/
├── composer.json             # Missing shopware-plugin-class
└── Services/
    └── MyService.php
```

```json
// Bad: Missing required composer.json fields
{
    "name": "my-vendor/my-plugin",
    "type": "library",
    "autoload": {
        "psr-4": {
            "MyVendor\\MyPlugin\\": ""
        }
    }
}
```

```php
// Bad: Plugin class in wrong namespace or location
namespace MyPlugin;

class MyPlugin extends Plugin
{
    // Will not be discovered!
}
```

**Correct (proper plugin structure):**

```
custom/plugins/MyPlugin/
├── composer.json
└── src/
    ├── MyPlugin.php                    # Main plugin class
    ├── Resources/
    │   ├── config/
    │   │   ├── services.xml            # Service definitions
    │   │   ├── routes.xml              # Route registration (optional)
    │   │   └── config.xml              # Plugin configuration (optional)
    │   ├── views/                      # Twig templates
    │   └── app/
    │       └── administration/         # Admin module (optional)
    ├── Controller/
    ├── Subscriber/
    ├── Service/
    ├── Core/                           # Core extensions
    ├── Migration/                      # Database migrations
    └── Entity/                         # Custom entities
```

```json
// Good: Correct composer.json configuration
{
    "name": "my-vendor/my-plugin",
    "description": "My Shopware 6 Plugin",
    "version": "1.0.0",
    "type": "shopware-platform-plugin",
    "license": "MIT",
    "authors": [
        {
            "name": "My Company"
        }
    ],
    "require": {
        "shopware/core": "~6.6.0"
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
    },
    "autoload": {
        "psr-4": {
            "MyVendor\\MyPlugin\\": "src/"
        }
    }
}
```

```php
// Good: Proper plugin class
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin;

use Shopware\Core\Framework\Plugin;
use Shopware\Core\Framework\Plugin\Context\InstallContext;
use Shopware\Core\Framework\Plugin\Context\UninstallContext;
use Shopware\Core\Framework\Plugin\Context\UpdateContext;
use Shopware\Core\Framework\Plugin\Context\ActivateContext;
use Shopware\Core\Framework\Plugin\Context\DeactivateContext;

class MyPlugin extends Plugin
{
    public function install(InstallContext $installContext): void
    {
        parent::install($installContext);
        // Custom install logic
    }

    public function uninstall(UninstallContext $uninstallContext): void
    {
        parent::uninstall($uninstallContext);

        if ($uninstallContext->keepUserData()) {
            return;
        }

        // Clean up custom data only if user opts out of keeping data
        $this->cleanupCustomData();
    }

    public function update(UpdateContext $updateContext): void
    {
        parent::update($updateContext);
        // Handle version-specific updates
    }

    public function activate(ActivateContext $activateContext): void
    {
        parent::activate($activateContext);
    }

    public function deactivate(DeactivateContext $deactivateContext): void
    {
        parent::deactivate($deactivateContext);
    }
}
```

**Plugin lifecycle hooks:**

| Method | When Called | Use Case |
|--------|-------------|----------|
| `install()` | First installation | Create custom tables, initial data |
| `update()` | Version upgrade | Data migrations, schema updates |
| `activate()` | Plugin enabled | Enable features, cache warmup |
| `deactivate()` | Plugin disabled | Disable features gracefully |
| `uninstall()` | Plugin removed | Cleanup data (respect keepUserData) |

Reference: [Plugin Base Guide](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-base-guide.html)
