---
name: wordpress-development
description: WordPress block development, REST API, theme development with block themes, WP-CLI usage, and plugin architecture.
---

# WordPress Development

## Overview

Modern WordPress development centers on the Block Editor (Gutenberg), block themes (FSE), the REST API, and WP-CLI. PHP 8.2+ and Node.js are required for contemporary workflows.

## Block Development Setup

```bash
# Create a new block plugin
npx @wordpress/create-block@latest my-block
cd my-block
npm start

# Create block inside existing plugin
npx @wordpress/create-block@latest --no-plugin my-block

# Or use the interactivity API template
npx @wordpress/create-block@latest my-block --template @wordpress/create-block-interactive-template
```

## Custom Block (JavaScript)

```javascript
// src/my-block/index.js
import { registerBlockType } from "@wordpress/blocks";
import { useBlockProps, RichText, InspectorControls, MediaUpload, MediaUploadCheck } from "@wordpress/block-editor";
import { PanelBody, TextControl, ToggleControl, RangeControl, Button } from "@wordpress/components";
import { __ } from "@wordpress/i18n";
import metadata from "./block.json";
import "./style.scss";
import "./editor.scss";

registerBlockType(metadata.name, {
  edit({ attributes, setAttributes }) {
    const { title, content, imageId, imageUrl, showBorder, columns } = attributes;
    const blockProps = useBlockProps({ className: "my-custom-block" });

    return (
      <>
        <InspectorControls>
          <PanelBody title={__("Settings", "my-plugin")}>
            <ToggleControl
              label={__("Show Border", "my-plugin")}
              checked={showBorder}
              onChange={(value) => setAttributes({ showBorder: value })}
            />
            <RangeControl
              label={__("Columns", "my-plugin")}
              value={columns}
              onChange={(value) => setAttributes({ columns: value })}
              min={1}
              max={4}
            />
          </PanelBody>
        </InspectorControls>

        <div {...blockProps}>
          <MediaUploadCheck>
            <MediaUpload
              onSelect={(media) => setAttributes({ imageId: media.id, imageUrl: media.url })}
              allowedTypes={["image"]}
              value={imageId}
              render={({ open }) => (
                <Button onClick={open} variant="secondary">
                  {imageUrl ? __("Replace Image") : __("Select Image")}
                </Button>
              )}
            />
          </MediaUploadCheck>
          {imageUrl && <img src={imageUrl} alt="" />}
          <RichText
            tagName="h2"
            value={title}
            onChange={(value) => setAttributes({ title: value })}
            placeholder={__("Enter title...", "my-plugin")}
          />
          <RichText
            tagName="p"
            value={content}
            onChange={(value) => setAttributes({ content: value })}
            placeholder={__("Enter content...", "my-plugin")}
          />
        </div>
      </>
    );
  },

  save({ attributes }) {
    const { title, content, imageUrl, showBorder, columns } = attributes;
    const blockProps = useBlockProps.save({
      className: `my-custom-block columns-${columns} ${showBorder ? "has-border" : ""}`,
    });

    return (
      <div {...blockProps}>
        {imageUrl && <img src={imageUrl} alt="" />}
        <RichText.Content tagName="h2" value={title} />
        <RichText.Content tagName="p" value={content} />
      </div>
    );
  },
});
```

```json
// src/my-block/block.json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "my-plugin/my-block",
  "version": "1.0.0",
  "title": "My Custom Block",
  "category": "content",
  "icon": "layout",
  "description": "A custom block with image and text.",
  "keywords": ["custom", "layout"],
  "supports": {
    "html": false,
    "align": ["wide", "full"],
    "spacing": { "margin": true, "padding": true },
    "color": { "background": true, "text": true },
    "typography": { "fontSize": true, "lineHeight": true }
  },
  "attributes": {
    "title": { "type": "string", "default": "" },
    "content": { "type": "string", "default": "" },
    "imageId": { "type": "number" },
    "imageUrl": { "type": "string" },
    "showBorder": { "type": "boolean", "default": false },
    "columns": { "type": "number", "default": 2 }
  },
  "textdomain": "my-plugin",
  "editorScript": "file:./index.js",
  "editorStyle": "file:./editor.css",
  "style": "file:./style-index.css",
  "viewScript": "file:./view.js"
}
```

## Plugin Architecture (PHP)

```php
<?php
/**
 * Plugin Name: My Plugin
 * Description: Custom WordPress plugin.
 * Version: 1.0.0
 * Requires at least: 6.4
 * Requires PHP: 8.1
 * Text Domain: my-plugin
 */

declare(strict_types=1);

if (!defined('ABSPATH')) exit;

define('MY_PLUGIN_VERSION', '1.0.0');
define('MY_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('MY_PLUGIN_URL', plugin_dir_url(__FILE__));

// Autoload
require_once MY_PLUGIN_DIR . 'vendor/autoload.php';

// Register block
add_action('init', function(): void {
    register_block_type(MY_PLUGIN_DIR . 'build/my-block');
});

// Custom post type
add_action('init', function(): void {
    register_post_type('product', [
        'labels' => [
            'name'          => __('Products', 'my-plugin'),
            'singular_name' => __('Product', 'my-plugin'),
        ],
        'public'       => true,
        'show_in_rest' => true,    // Required for Gutenberg & REST API
        'supports'     => ['title', 'editor', 'thumbnail', 'custom-fields'],
        'has_archive'  => true,
        'rewrite'      => ['slug' => 'products'],
        'menu_icon'    => 'dashicons-cart',
    ]);
});

// Custom REST API endpoint
add_action('rest_api_init', function(): void {
    register_rest_route('my-plugin/v1', '/products', [
        'methods'             => WP_REST_Server::READABLE,
        'callback'            => 'my_plugin_get_products',
        'permission_callback' => '__return_true',
        'args'                => [
            'page'     => ['type' => 'integer', 'default' => 1, 'sanitize_callback' => 'absint'],
            'per_page' => ['type' => 'integer', 'default' => 10, 'sanitize_callback' => 'absint'],
            'category' => ['type' => 'string', 'sanitize_callback' => 'sanitize_text_field'],
        ],
    ]);

    register_rest_route('my-plugin/v1', '/products/(?P<id>\d+)', [
        'methods'             => WP_REST_Server::READABLE,
        'callback'            => 'my_plugin_get_product',
        'permission_callback' => '__return_true',
        'args'                => [
            'id' => ['type' => 'integer', 'required' => true],
        ],
    ]);
});

function my_plugin_get_products(WP_REST_Request $request): WP_REST_Response {
    $query = new WP_Query([
        'post_type'      => 'product',
        'posts_per_page' => $request->get_param('per_page'),
        'paged'          => $request->get_param('page'),
        'post_status'    => 'publish',
    ]);

    $products = array_map(function(WP_Post $post): array {
        return [
            'id'        => $post->ID,
            'title'     => get_the_title($post),
            'content'   => apply_filters('the_content', $post->post_content),
            'thumbnail' => get_the_post_thumbnail_url($post, 'full'),
            'meta'      => get_post_meta($post->ID),
            'link'      => get_permalink($post),
        ];
    }, $query->posts);

    $response = new WP_REST_Response($products, 200);
    $response->header('X-WP-Total', $query->found_posts);
    $response->header('X-WP-TotalPages', $query->max_num_pages);
    return $response;
}
```

## Block Theme Development (FSE)

```
my-theme/
├── style.css              # Theme header
├── functions.php
├── theme.json             # Design system
├── templates/
│   ├── index.html
│   ├── single.html
│   ├── archive.html
│   └── 404.html
└── parts/
    ├── header.html
    └── footer.html
```

```json
// theme.json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "color": {
      "palette": [
        { "name": "Primary", "slug": "primary", "color": "#0073aa" },
        { "name": "Secondary", "slug": "secondary", "color": "#f0f0f0" },
        { "name": "Dark", "slug": "dark", "color": "#1d2327" }
      ]
    },
    "typography": {
      "fluid": true,
      "fontFamilies": [
        {
          "name": "Inter",
          "slug": "inter",
          "fontFamily": "Inter, sans-serif",
          "fontFace": [
            {
              "src": ["file:./assets/fonts/inter-regular.woff2"],
              "fontWeight": "400",
              "fontStyle": "normal"
            }
          ]
        }
      ],
      "fontSizes": [
        { "name": "Small", "slug": "small", "size": "0.875rem" },
        { "name": "Medium", "slug": "medium", "size": "1rem" },
        { "name": "Large", "slug": "large", "size": "1.5rem" },
        { "name": "X-Large", "slug": "x-large", "size": "clamp(1.75rem, 3vw, 2.25rem)" }
      ]
    },
    "layout": {
      "contentSize": "860px",
      "wideSize": "1200px"
    },
    "spacing": {
      "spacingScale": { "steps": 7, "mediumStep": 1.5, "unit": "rem", "operator": "*", "increment": 1.5 }
    }
  },
  "styles": {
    "color": { "background": "var(--wp--preset--color--white)", "text": "var(--wp--preset--color--dark)" },
    "typography": { "fontFamily": "var(--wp--preset--font-family--inter)", "fontSize": "var(--wp--preset--font-size--medium)" },
    "elements": {
      "link": { "color": { "text": "var(--wp--preset--color--primary)" } },
      "h1": { "typography": { "fontSize": "var(--wp--preset--font-size--x-large)", "fontWeight": "700" } }
    }
  }
}
```

## WP-CLI

```bash
# Core management
wp core download --version=6.5
wp core install --url=localhost --title="My Site" --admin_user=admin --admin_password=secret --admin_email=admin@example.com
wp core update

# Plugin management
wp plugin install woocommerce --activate
wp plugin list
wp plugin deactivate --all
wp plugin update --all

# Database operations
wp db export backup.sql
wp db import backup.sql
wp db optimize
wp search-replace 'http://old-domain.com' 'https://new-domain.com' --all-tables

# Post operations
wp post create --post_title="Test" --post_status=publish --post_type=post
wp post list --post_type=product --format=table
wp post delete $(wp post list --post_type=revision --format=ids)

# User management
wp user create john john@example.com --role=editor --user_pass=password
wp user list --role=administrator

# Cache
wp cache flush
wp rewrite flush

# Custom WP-CLI command
WP_CLI::add_command('my-plugin sync', function($args, $assoc_args) {
    $dry_run = WP_CLI\Utils\get_flag_value($assoc_args, 'dry-run', false);
    WP_CLI::log("Starting sync...");
    // ... sync logic
    WP_CLI::success("Sync complete!");
});
# Usage: wp my-plugin sync --dry-run
```

## Key Patterns

- **`show_in_rest: true`** is required for Gutenberg to interact with custom post types
- **`block.json`** is the source of truth — use it for block registration in both PHP and JS
- **Block supports** in `block.json` enable built-in editor controls (spacing, color, typography)
- **Theme.json** replaces hardcoded CSS — keeps design tokens in sync between editor and frontend
- **`apply_filters('the_content', ...)`** processes blocks, shortcodes, and embeds in REST responses
- **WP-CLI scripts** in CI/CD for database migrations and search-replace on deployments

## Models to Use

- **claude-opus-4-5**: Complex plugin architecture, custom Gutenberg components, WooCommerce extensions
- **claude-sonnet-4-5**: Block development, REST API endpoints, theme.json configuration
- **claude-haiku-3-5**: Simple shortcodes, WP-CLI commands, hook additions
