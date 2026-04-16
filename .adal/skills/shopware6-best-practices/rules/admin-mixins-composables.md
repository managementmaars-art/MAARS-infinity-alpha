---
title: Mixins, Directives & Composition
impact: MEDIUM
impactDescription: code reuse patterns for consistent admin functionality
tags: administration, vue, mixin, directive, composable
---

## Mixins, Directives & Composition

**Impact: MEDIUM (code reuse patterns for consistent admin functionality)**

Use Shopware's built-in mixins for common functionality. Create custom mixins for shared logic across components. Understand when to use mixins vs. composition.

**Incorrect (duplicating common logic):**

```javascript
// Bad: Duplicated notification logic in every component
Component.register('my-component-a', {
    methods: {
        showSuccess(message) {
            this.$store.dispatch('notification/createNotification', {
                variant: 'success',
                message: message
            });
        },
        showError(message) {
            this.$store.dispatch('notification/createNotification', {
                variant: 'error',
                message: message
            });
        }
    }
});

// Same code duplicated in another component
Component.register('my-component-b', {
    methods: {
        showSuccess(message) { /* same code */ },
        showError(message) { /* same code */ }
    }
});
```

**Correct (using built-in mixins):**

```javascript
const { Component, Mixin } = Shopware;

Component.register('my-plugin-list', {
    mixins: [
        // Good: Use built-in notification mixin
        Mixin.getByName('notification'),
        // Good: Use listing mixin for pagination
        Mixin.getByName('listing'),
        // Good: Use placeholder mixin for entity names
        Mixin.getByName('placeholder')
    ],

    methods: {
        async onSave() {
            try {
                await this.repository.save(this.entity);

                // Good: Methods from notification mixin
                this.createNotificationSuccess({
                    title: this.$tc('global.default.success'),
                    message: this.$tc('my-plugin.notification.saveSuccess')
                });
            } catch (error) {
                this.createNotificationError({
                    title: this.$tc('global.default.error'),
                    message: error.message
                });
            }
        }
    }
});
```

**Available built-in mixins:**

```javascript
// Notification mixin - adds notification methods
Mixin.getByName('notification')
// Methods: createNotificationSuccess, createNotificationError, createNotificationWarning, createNotificationInfo

// Listing mixin - adds pagination functionality
Mixin.getByName('listing')
// Properties: page, limit, total, sortBy, sortDirection
// Methods: onPageChange, onSearch, getList

// Validation mixin - form validation
Mixin.getByName('validation')
// Methods: validate

// Placeholder mixin - display placeholders for loading entities
Mixin.getByName('placeholder')
// Methods: placeholder(entity, property, fallback)

// Position mixin - sorting/positioning
Mixin.getByName('position')

// Salutation mixin - format names with salutation
Mixin.getByName('salutation')
// Methods: salutation
```

**Correct custom mixin creation:**

```javascript
// src/mixin/my-custom-mixin.js
const { Mixin } = Shopware;

Mixin.register('my-custom-mixin', {
    data() {
        return {
            customMixinData: null
        };
    },

    computed: {
        isCustomCondition() {
            return this.customMixinData !== null;
        }
    },

    methods: {
        initCustomMixin() {
            // Initialization logic
        },

        formatCustomValue(value) {
            // Shared formatting logic
            return `Formatted: ${value}`;
        },

        async loadCustomData(entityId) {
            // Shared data loading logic
            const repository = this.repositoryFactory.create('my_entity');
            this.customMixinData = await repository.get(entityId);
        }
    },

    created() {
        this.initCustomMixin();
    }
});
```

```javascript
// Usage in component
import '../../mixin/my-custom-mixin';

Component.register('my-component', {
    mixins: [
        Mixin.getByName('notification'),
        Mixin.getByName('my-custom-mixin')
    ],

    methods: {
        doSomething() {
            const formatted = this.formatCustomValue('test');
            console.log(formatted); // "Formatted: test"
        }
    }
});
```

**Correct use of directives:**

```javascript
// src/directive/my-custom-directive.js
const { Directive } = Shopware;

Directive.register('my-tooltip', {
    bind(el, binding) {
        el.setAttribute('title', binding.value);
        el.classList.add('has-tooltip');
    },

    update(el, binding) {
        if (binding.value !== binding.oldValue) {
            el.setAttribute('title', binding.value);
        }
    },

    unbind(el) {
        el.removeAttribute('title');
        el.classList.remove('has-tooltip');
    }
});
```

```twig
{# Usage in template #}
<span v-my-tooltip="item.description">
    {{ item.name }}
</span>
```

**Built-in directives:**

```twig
{# Tooltip directive #}
<sw-button v-tooltip="$tc('my.tooltip.text')">
    Hover me
</sw-button>

{# Tooltip with position #}
<sw-button v-tooltip.bottom="tooltipText">
    Bottom tooltip
</sw-button>

{# Popover directive #}
<sw-button v-popover="{ message: 'Popover content' }">
    With popover
</sw-button>

{# Drag and drop sorting #}
<div v-droppable="{ data: item, dragGroup: 'myGroup' }">
    <div v-draggable="{ data: item, dragGroup: 'myGroup' }">
        Draggable item
    </div>
</div>
```

**Composition with inject/provide:**

```javascript
// Parent component providing data
Component.register('my-parent-component', {
    provide() {
        return {
            mySharedService: this.sharedService,
            getParentEntity: () => this.entity
        };
    },

    data() {
        return {
            entity: null,
            sharedService: Shopware.Service('myService')
        };
    }
});

// Child component consuming provided data
Component.register('my-child-component', {
    inject: [
        'mySharedService',
        'getParentEntity'
    ],

    computed: {
        parentEntity() {
            return this.getParentEntity();
        }
    },

    methods: {
        doAction() {
            this.mySharedService.performAction(this.parentEntity);
        }
    }
});
```

**Common inject dependencies:**

```javascript
inject: [
    'repositoryFactory',     // Create entity repositories
    'acl',                   // Check permissions
    'context',               // API context (language, etc.)
    'feature',               // Feature flags
    'loginService',          // Authentication
    'userService',           // Current user info
    'systemConfigApiService' // System configuration
]
```

Reference: [Mixins](https://developer.shopware.com/docs/guides/plugins/plugins/administration/using-mixins.html)
