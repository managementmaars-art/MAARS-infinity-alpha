---
title: SCSS Variables & Theming
impact: MEDIUM
impactDescription: consistent styling through proper variable usage
tags: storefront, scss, css, variables, bootstrap, theming
---

## SCSS Variables & Theming

**Impact: MEDIUM (consistent styling through proper variable usage)**

Use Shopware's SCSS variable system and Bootstrap variables correctly. Override variables in the proper order and use theme configuration for admin-editable values.

**Incorrect (hardcoding values instead of using variables):**

```scss
// Bad: Hardcoded colors
.my-component {
    background-color: #008490;
    color: #1d1d1d;
    font-size: 14px;
    padding: 16px;
}

// Bad: Duplicating Bootstrap variables
$my-primary: #008490; // Duplicate of $sw-color-brand-primary
```

**Correct (using Shopware and Bootstrap variables):**

```scss
// Good: Use existing variables
.my-component {
    background-color: $sw-color-brand-primary;
    color: $sw-text-color;
    font-size: $font-size-base;
    padding: $spacer;
}

// Good: Use spacing helpers
.my-container {
    margin-bottom: $spacer * 2;
    padding: $spacer-lg;
}
```

**Core Shopware SCSS variables to use:**

```scss
// Brand colors (override in theme.json)
$sw-color-brand-primary
$sw-color-brand-secondary
$sw-color-success
$sw-color-info
$sw-color-warning
$sw-color-danger

// Text colors
$sw-text-color
$sw-headline-color
$sw-text-muted

// Background colors
$sw-background-color
$sw-surface-color

// Border colors
$sw-border-color
$sw-border-color-light

// Spacing (Bootstrap-based)
$spacer          // 1rem = 16px
$spacer-xs       // 0.25rem
$spacer-sm       // 0.5rem
$spacer-md       // 1rem
$spacer-lg       // 1.5rem
$spacer-xl       // 3rem

// Typography
$font-family-base
$font-size-base
$font-size-sm
$font-size-lg
$line-height-base
$headings-font-family
$headings-font-weight

// Breakpoints (Bootstrap)
$grid-breakpoints: (
    xs: 0,
    sm: 576px,
    md: 768px,
    lg: 992px,
    xl: 1200px,
    xxl: 1400px
);

// Container widths
$container-max-widths
```

**Correct variable override order:**

```scss
// 1. First, define your variable overrides
// _variables.scss

// Override Shopware brand colors
$sw-color-brand-primary: #3498db !default;
$sw-color-brand-secondary: #2ecc71 !default;

// Override Bootstrap variables
$font-family-base: 'Roboto', sans-serif !default;
$border-radius: 0.5rem !default;
$border-radius-lg: 0.75rem !default;

// Define custom variables
$my-theme-card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !default;
$my-theme-header-height: 80px !default;
```

```scss
// 2. Then import in base.scss
// base.scss

// Variables first (before any imports that use them)
@import 'variables';

// Component overrides
@import 'components/header';
@import 'components/navigation';
@import 'components/product';
```

**Using CSS custom properties (CSS variables):**

```scss
// Good: Define CSS variables for runtime theming
:root {
    --my-theme-primary: #{$sw-color-brand-primary};
    --my-theme-spacing: #{$spacer};
    --my-theme-radius: #{$border-radius};
}

// Use CSS variables for dynamic values
.my-component {
    background-color: var(--my-theme-primary);
    padding: var(--my-theme-spacing);
    border-radius: var(--my-theme-radius);
}

// JavaScript can modify CSS variables at runtime
// document.documentElement.style.setProperty('--my-theme-primary', newColor);
```

**Responsive design with mixins:**

```scss
// Good: Use Bootstrap breakpoint mixins
.my-component {
    padding: $spacer;

    @include media-breakpoint-up(md) {
        padding: $spacer-lg;
        display: flex;
    }

    @include media-breakpoint-up(lg) {
        padding: $spacer-xl;
    }

    @include media-breakpoint-down(sm) {
        font-size: $font-size-sm;
    }
}

// Responsive grid
.my-grid {
    display: grid;
    gap: $spacer;
    grid-template-columns: 1fr;

    @include media-breakpoint-up(md) {
        grid-template-columns: repeat(2, 1fr);
    }

    @include media-breakpoint-up(lg) {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

**Admin-editable theme variables:**

```json
// theme.json - Make variables editable in admin
{
    "config": {
        "fields": {
            "my-theme-primary-color": {
                "label": { "en-GB": "Primary Color" },
                "type": "color",
                "value": "#008490",
                "editable": true,
                "block": "colors",
                "scss": true
            },
            "my-theme-border-radius": {
                "label": { "en-GB": "Border Radius" },
                "type": "text",
                "value": "8px",
                "editable": true,
                "block": "layout",
                "scss": true
            }
        }
    }
}
```

```scss
// Variables from theme.json are automatically available
// when scss: true is set

.my-component {
    // $my-theme-primary-color and $my-theme-border-radius
    // are injected from theme config
    background-color: $my-theme-primary-color;
    border-radius: $my-theme-border-radius;
}
```

**Common patterns:**

| Pattern | Variables to Use |
|---------|------------------|
| Primary button | `$sw-color-brand-primary`, `$btn-padding-y`, `$btn-padding-x` |
| Card component | `$sw-surface-color`, `$sw-border-color`, `$border-radius` |
| Form inputs | `$input-*` variables from Bootstrap |
| Typography | `$font-size-*`, `$headings-*`, `$line-height-*` |
| Spacing | `$spacer-*` variables |

Reference: [SCSS Styling](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-custom-styling.html)
