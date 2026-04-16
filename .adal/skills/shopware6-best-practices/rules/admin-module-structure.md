---
title: Admin Module Structure & Registration
impact: CRITICAL
impactDescription: proper module registration ensures admin functionality works correctly
tags: administration, vue, module, structure, registration
---

## Admin Module Structure & Registration

**Impact: CRITICAL (proper module registration ensures admin functionality works correctly)**

Administration modules must follow a specific structure with proper index.js registration. Modules define navigation entries, routes, and component organization.

**Incorrect (flat structure without proper registration):**

```javascript
// Bad: Components without module structure
// src/Resources/app/administration/src/component/my-component.js
export default {
    template: '<div>My Component</div>'
};
// Missing module registration, won't be loaded
```

**Correct module structure:**

```
src/Resources/app/administration/
├── src/
│   ├── main.js                          # Entry point
│   └── module/
│       └── my-plugin-module/
│           ├── index.js                 # Module registration
│           ├── page/
│           │   ├── my-plugin-list/
│           │   │   ├── index.js
│           │   │   └── my-plugin-list.html.twig
│           │   └── my-plugin-detail/
│           │       ├── index.js
│           │       └── my-plugin-detail.html.twig
│           ├── component/
│           │   └── my-plugin-card/
│           │       ├── index.js
│           │       └── my-plugin-card.html.twig
│           └── snippet/
│               ├── de-DE.json
│               └── en-GB.json
```

**Correct main.js entry point:**

```javascript
// src/Resources/app/administration/src/main.js

import './module/my-plugin-module';

// Import component extensions
import './extension/sw-product-detail';

// Import global components
import './component/my-global-component';
```

**Correct module registration (index.js):**

```javascript
// src/Resources/app/administration/src/module/my-plugin-module/index.js

import './page/my-plugin-list';
import './page/my-plugin-detail';
import './component/my-plugin-card';

import deDE from './snippet/de-DE.json';
import enGB from './snippet/en-GB.json';

const { Module } = Shopware;

Module.register('my-plugin-module', {
    type: 'plugin',
    name: 'my-plugin-module',
    title: 'my-plugin-module.general.title',
    description: 'my-plugin-module.general.description',
    color: '#ff3d58',
    icon: 'default-shopping-paper-bag-product',

    snippets: {
        'de-DE': deDE,
        'en-GB': enGB
    },

    routes: {
        list: {
            component: 'my-plugin-list',
            path: 'list',
            meta: {
                parentPath: 'sw.settings.index',
                privilege: 'my_plugin.viewer'
            }
        },
        detail: {
            component: 'my-plugin-detail',
            path: 'detail/:id',
            props: {
                default: (route) => ({ entityId: route.params.id })
            },
            meta: {
                parentPath: 'my.plugin.module.list',
                privilege: 'my_plugin.viewer'
            }
        },
        create: {
            component: 'my-plugin-detail',
            path: 'create',
            meta: {
                parentPath: 'my.plugin.module.list',
                privilege: 'my_plugin.creator'
            }
        }
    },

    navigation: [{
        id: 'my-plugin-module',
        label: 'my-plugin-module.navigation.main',
        color: '#ff3d58',
        icon: 'default-shopping-paper-bag-product',
        path: 'my.plugin.module.list',
        parent: 'sw-settings',
        position: 100,
        privilege: 'my_plugin.viewer'
    }],

    settingsItem: [{
        group: 'plugins',
        to: 'my.plugin.module.list',
        icon: 'default-shopping-paper-bag-product',
        privilege: 'my_plugin.viewer'
    }]
});
```

**Correct page component:**

```javascript
// src/module/my-plugin-module/page/my-plugin-list/index.js

const { Component, Mixin } = Shopware;
const { Criteria } = Shopware.Data;

Component.register('my-plugin-list', {
    template,

    inject: [
        'repositoryFactory',
        'acl'
    ],

    mixins: [
        Mixin.getByName('notification'),
        Mixin.getByName('listing')
    ],

    data() {
        return {
            items: null,
            isLoading: false,
            sortBy: 'createdAt',
            sortDirection: 'DESC',
            total: 0
        };
    },

    metaInfo() {
        return {
            title: this.$createTitle()
        };
    },

    computed: {
        repository() {
            return this.repositoryFactory.create('my_plugin_entity');
        },

        columns() {
            return [
                {
                    property: 'name',
                    label: this.$tc('my-plugin-module.list.columnName'),
                    routerLink: 'my.plugin.module.detail',
                    allowResize: true,
                    primary: true
                },
                {
                    property: 'active',
                    label: this.$tc('my-plugin-module.list.columnActive'),
                    allowResize: true
                },
                {
                    property: 'createdAt',
                    label: this.$tc('my-plugin-module.list.columnCreatedAt'),
                    allowResize: true
                }
            ];
        },

        listCriteria() {
            const criteria = new Criteria(this.page, this.limit);
            criteria.addSorting(Criteria.sort(this.sortBy, this.sortDirection));

            if (this.term) {
                criteria.setTerm(this.term);
            }

            return criteria;
        }
    },

    created() {
        this.getList();
    },

    methods: {
        async getList() {
            this.isLoading = true;

            try {
                const result = await this.repository.search(this.listCriteria);
                this.items = result;
                this.total = result.total;
            } catch (error) {
                this.createNotificationError({
                    message: error.message
                });
            } finally {
                this.isLoading = false;
            }
        },

        onChangeLanguage(languageId) {
            Shopware.State.commit('context/setApiLanguageId', languageId);
            this.getList();
        }
    }
});
```

**Correct snippet files:**

```json
// src/module/my-plugin-module/snippet/en-GB.json
{
    "my-plugin-module": {
        "general": {
            "title": "My Plugin",
            "description": "Manage my plugin entities"
        },
        "navigation": {
            "main": "My Plugin"
        },
        "list": {
            "title": "My Plugin Entities",
            "columnName": "Name",
            "columnActive": "Active",
            "columnCreatedAt": "Created at",
            "buttonCreate": "Create entity"
        },
        "detail": {
            "title": "Entity Details",
            "titleNew": "New Entity",
            "labelName": "Name",
            "labelActive": "Active",
            "placeholderName": "Enter name..."
        }
    }
}
```

**ACL privileges in plugin class:**

```php
// src/Resources/config/acl.xml
<?xml version="1.0" ?>
<privileges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/Framework/Resources/config/acl.xsd">

    <acl>
        <role name="my_plugin.viewer">
            <privilege>my_plugin_entity:read</privilege>
        </role>
        <role name="my_plugin.editor">
            <parent>my_plugin.viewer</parent>
            <privilege>my_plugin_entity:update</privilege>
        </role>
        <role name="my_plugin.creator">
            <parent>my_plugin.editor</parent>
            <privilege>my_plugin_entity:create</privilege>
        </role>
        <role name="my_plugin.deleter">
            <parent>my_plugin.editor</parent>
            <privilege>my_plugin_entity:delete</privilege>
        </role>
    </acl>
</privileges>
```

Reference: [Admin Modules](https://developer.shopware.com/docs/guides/plugins/plugins/administration/add-custom-module.html)
