---
title: JavaScript Plugin System
impact: HIGH
impactDescription: proper JS plugin architecture for interactive storefront components
tags: storefront, javascript, plugin, webpack, es6
---

## JavaScript Plugin System

**Impact: HIGH (proper JS plugin architecture for interactive storefront components)**

Shopware 6 uses a plugin-based JavaScript architecture. Extend the `Plugin` base class and register plugins properly to ensure correct initialization and lifecycle management.

**Incorrect (inline scripts or jQuery patterns):**

```html
<!-- Bad: Inline scripts without plugin system -->
<script>
    $(document).ready(function() {
        $('.my-button').click(function() {
            // jQuery spaghetti
        });
    });
</script>
```

```javascript
// Bad: Global functions without encapsulation
function doSomething() {
    document.querySelector('.element').classList.add('active');
}
```

**Correct (extending Plugin base class):**

```javascript
// Good: custom/plugins/MyPlugin/src/Resources/app/storefront/src/plugin/my-custom-plugin.plugin.js

import Plugin from 'src/plugin-system/plugin.class';
import DomAccess from 'src/helper/dom-access.helper';
import HttpClient from 'src/service/http-client.service';

export default class MyCustomPlugin extends Plugin {
    // Define default options
    static options = {
        buttonSelector: '.my-button',
        contentSelector: '.my-content',
        activeClass: 'is-active',
        apiEndpoint: '/my-plugin/api'
    };

    init() {
        // Get DOM elements using helper
        this.button = DomAccess.querySelector(this.el, this.options.buttonSelector);
        this.content = DomAccess.querySelector(this.el, this.options.contentSelector, false);

        // Initialize HTTP client for AJAX
        this._client = new HttpClient();

        // Register event listeners
        this._registerEvents();
    }

    _registerEvents() {
        this.button.addEventListener('click', this._onButtonClick.bind(this));
    }

    _onButtonClick(event) {
        event.preventDefault();

        this.el.classList.toggle(this.options.activeClass);

        if (this.content) {
            this._loadContent();
        }
    }

    _loadContent() {
        this._client.get(this.options.apiEndpoint, (response) => {
            this.content.innerHTML = response;

            // Publish event for other plugins
            this.$emitter.publish('contentLoaded', { content: response });
        });
    }

    // Cleanup on destroy
    destroy() {
        this.button.removeEventListener('click', this._onButtonClick.bind(this));
    }
}
```

**Correct plugin registration:**

```javascript
// Good: custom/plugins/MyPlugin/src/Resources/app/storefront/src/main.js

import MyCustomPlugin from './plugin/my-custom-plugin.plugin';
import AnotherPlugin from './plugin/another-plugin.plugin';

// Register plugin with selector
const PluginManager = window.PluginManager;

PluginManager.register('MyCustomPlugin', MyCustomPlugin, '[data-my-custom-plugin]');
PluginManager.register('AnotherPlugin', AnotherPlugin, '[data-another-plugin]');

// Register with custom options override
PluginManager.register('MyCustomPlugin', MyCustomPlugin, '[data-my-custom-plugin]', {
    buttonSelector: '.custom-button'
});
```

**Correct HTML data attribute usage:**

```twig
{# Initialize plugin with data attribute #}
<div data-my-custom-plugin="true">
    <button class="my-button">Click me</button>
    <div class="my-content"></div>
</div>

{# Pass options via data attributes #}
<div data-my-custom-plugin="true"
     data-my-custom-plugin-options='{ "apiEndpoint": "/custom/api", "activeClass": "custom-active" }'>
    <button class="my-button">Click me</button>
</div>
```

**Extending existing Shopware plugins:**

```javascript
// Good: Extend existing plugin instead of replacing
import AddToCartPlugin from 'src/plugin/add-to-cart/add-to-cart.plugin';

export default class ExtendedAddToCartPlugin extends AddToCartPlugin {
    init() {
        // Call parent init
        super.init();

        // Add custom initialization
        this._initCustomTracking();
    }

    _initCustomTracking() {
        this.$emitter.subscribe('beforeFormSubmit', this._trackAddToCart.bind(this));
    }

    _trackAddToCart(event) {
        // Custom tracking logic
        console.log('Product added:', event.detail);
    }
}
```

```javascript
// Register extended plugin to override original
PluginManager.override('AddToCart', ExtendedAddToCartPlugin, '[data-add-to-cart]');
```

**Using plugin events:**

```javascript
// Subscribe to plugin events
const element = document.querySelector('[data-my-custom-plugin]');
const pluginInstance = PluginManager.getPluginInstanceFromElement(element, 'MyCustomPlugin');

pluginInstance.$emitter.subscribe('contentLoaded', (event) => {
    console.log('Content was loaded:', event.detail.content);
});

// Publish custom events
this.$emitter.publish('myCustomEvent', {
    data: 'some data'
});
```

**Build configuration (if customizing webpack):**

```javascript
// custom/plugins/MyPlugin/src/Resources/app/storefront/build/webpack.config.js
module.exports = () => {
    return {
        resolve: {
            alias: {
                '@my-plugin': path.resolve(__dirname, '..', 'src'),
            },
        },
    };
};
```

**Important conventions:**

| Convention | Description |
|------------|-------------|
| File naming | `my-plugin-name.plugin.js` |
| Class naming | `MyPluginNamePlugin` |
| Data attribute | `data-my-plugin-name` |
| Options attribute | `data-my-plugin-name-options` |
| CSS class prefix | `my-plugin-` |

Reference: [JavaScript Plugins](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-custom-javascript.html)
