---
title: Theme Development & Inheritance
impact: HIGH
impactDescription: proper theme structure ensures maintainability and upgrade safety
tags: storefront, theme, inheritance, scss, assets
---

## Theme Development & Inheritance

**Impact: HIGH (proper theme structure ensures maintainability and upgrade safety)**

Themes must extend the Storefront theme or another theme, use proper inheritance, and follow the correct directory structure. Never create standalone themes without proper parent inheritance.

**Incorrect (theme without proper inheritance):**

```php
// Bad: Plugin class trying to act as theme without proper setup
class MyTheme extends Plugin
{
    // Missing theme configuration
}
```

```json
// Bad: theme.json without proper views inheritance
{
    "name": "MyTheme",
    "author": "MyVendor"
}
```

**Correct theme structure:**

```
custom/plugins/MyTheme/
├── composer.json
└── src/
    ├── MyTheme.php
    └── Resources/
        ├── theme.json
        ├── views/
        │   └── storefront/
        │       └── ... (template overrides)
        ├── app/
        │   └── storefront/
        │       ├── src/
        │       │   ├── main.js
        │       │   ├── scss/
        │       │   │   ├── base.scss
        │       │   │   ├── _variables.scss
        │       │   │   └── _overrides.scss
        │       │   └── plugin/
        │       └── dist/
        │           └── storefront/
        │               └── js/
        └── public/
            └── ... (static assets)
```

**Correct theme.json configuration:**

```json
{
    "name": "MyTheme",
    "author": "MyVendor",
    "description": {
        "en-GB": "Custom theme for client project",
        "de-DE": "Individuelles Theme für Kundenprojekt"
    },
    "views": [
        "@Storefront",
        "@Plugins",
        "@MyTheme"
    ],
    "style": [
        "@Storefront",
        "app/storefront/src/scss/base.scss"
    ],
    "script": [
        "@Storefront",
        "app/storefront/dist/storefront/js/my-theme.js"
    ],
    "asset": [
        "@Storefront"
    ],
    "previewMedia": "preview.png",
    "config": {
        "blocks": {
            "colors": {
                "label": {
                    "en-GB": "Colors",
                    "de-DE": "Farben"
                }
            },
            "typography": {
                "label": {
                    "en-GB": "Typography",
                    "de-DE": "Typografie"
                }
            }
        },
        "fields": {
            "sw-color-brand-primary": {
                "label": {
                    "en-GB": "Primary color",
                    "de-DE": "Primärfarbe"
                },
                "type": "color",
                "value": "#008490",
                "editable": true,
                "block": "colors"
            },
            "my-theme-header-bg": {
                "label": {
                    "en-GB": "Header background",
                    "de-DE": "Header-Hintergrund"
                },
                "type": "color",
                "value": "#ffffff",
                "editable": true,
                "block": "colors",
                "scss": true
            },
            "my-theme-font-family": {
                "label": {
                    "en-GB": "Font family",
                    "de-DE": "Schriftart"
                },
                "type": "fontFamily",
                "value": "'Inter', sans-serif",
                "editable": true,
                "block": "typography"
            },
            "my-theme-logo": {
                "label": {
                    "en-GB": "Theme logo",
                    "de-DE": "Theme-Logo"
                },
                "type": "media",
                "value": "app/storefront/dist/assets/logo.png",
                "editable": true
            }
        }
    }
}
```

**Correct theme plugin class:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyTheme;

use Shopware\Core\Framework\Plugin;
use Shopware\Storefront\Framework\ThemeInterface;

class MyTheme extends Plugin implements ThemeInterface
{
    // ThemeInterface marks this plugin as a theme
    // No additional code required for basic themes

    public function getThemeConfigPath(): string
    {
        return 'theme.json';
    }
}
```

**Correct SCSS structure:**

```scss
// base.scss - Main entry point
@import 'variables';
@import 'overrides';
@import 'components/header';
@import 'components/footer';
@import 'components/product-card';

// Custom styles
.my-theme {
    &-header {
        background-color: $my-theme-header-bg;
    }
}
```

```scss
// _variables.scss - Override Shopware variables
// These must be defined BEFORE importing Storefront

// Override primary color (from theme.json)
// $sw-color-brand-primary is set via theme.json config

// Custom theme variables (with scss: true in theme.json)
// $my-theme-header-bg is automatically available

// Additional custom variables
$my-theme-border-radius: 8px;
$my-theme-box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
```

```scss
// _overrides.scss - Override Storefront component styles
.header-main {
    background-color: $my-theme-header-bg;
    box-shadow: $my-theme-box-shadow;
}

.product-box {
    border-radius: $my-theme-border-radius;

    .product-name {
        font-family: $my-theme-font-family;
    }
}

// Override Bootstrap variables
.btn-primary {
    border-radius: $my-theme-border-radius;
}
```

**Theme inheritance (child themes):**

```json
{
    "name": "MyChildTheme",
    "author": "MyVendor",
    "views": [
        "@Storefront",
        "@MyParentTheme",
        "@MyChildTheme"
    ],
    "style": [
        "@MyParentTheme",
        "app/storefront/src/scss/child-overrides.scss"
    ],
    "script": [
        "@MyParentTheme",
        "app/storefront/dist/storefront/js/child-theme.js"
    ],
    "configInheritance": [
        "@MyParentTheme"
    ]
}
```

**Theme compilation commands:**

```bash
# Compile theme for development
bin/console theme:compile

# Compile with hot reload (development)
bin/console theme:compile --keep-assets

# Dump theme configuration
bin/console theme:dump

# Refresh theme assignment
bin/console theme:refresh

# Change theme for sales channel
bin/console theme:change --sales-channel="storefront" MyTheme
```

Reference: [Theme Development](https://developer.shopware.com/docs/guides/plugins/themes/theme-base-guide.html)
