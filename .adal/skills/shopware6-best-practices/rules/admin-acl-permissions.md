---
title: ACL & Permission Checks
impact: HIGH
impactDescription: proper permission handling ensures secure admin interfaces
tags: administration, acl, permissions, security, roles
---

## ACL & Permission Checks

**Impact: HIGH (proper permission handling ensures secure admin interfaces)**

Always check ACL permissions in administration components before allowing actions. Use the `acl` service for checks and disable/hide UI elements based on permissions.

**Incorrect (no permission checks):**

```javascript
// Bad: No ACL checks on actions
Component.register('my-plugin-detail', {
    methods: {
        onSave() {
            // Bad: Anyone can save
            this.repository.save(this.entity);
        },

        onDelete() {
            // Bad: Anyone can delete
            this.repository.delete(this.entity.id);
        }
    }
});
```

```twig
{# Bad: Button always visible regardless of permissions #}
<sw-button @click="onDelete">
    Delete
</sw-button>
```

**Correct (with ACL checks):**

```javascript
// Good: Inject and use ACL service
Component.register('my-plugin-detail', {
    inject: [
        'repositoryFactory',
        'acl'  // Good: Inject ACL service
    ],

    computed: {
        // Good: Compute permission states
        canEdit() {
            return this.acl.can('my_plugin.editor');
        },

        canDelete() {
            return this.acl.can('my_plugin.deleter');
        },

        canCreate() {
            return this.acl.can('my_plugin.creator');
        }
    },

    methods: {
        async onSave() {
            // Good: Check permission before action
            if (!this.acl.can('my_plugin.editor')) {
                this.createNotificationError({
                    message: this.$tc('global.notification.noPermission')
                });
                return;
            }

            await this.repository.save(this.entity);
        },

        async onDelete() {
            // Good: Check permission before delete
            if (!this.acl.can('my_plugin.deleter')) {
                this.createNotificationError({
                    message: this.$tc('global.notification.noPermission')
                });
                return;
            }

            await this.repository.delete(this.entity.id);
        }
    }
});
```

**Correct template with permission checks:**

```twig
{% block my_plugin_detail_actions %}
    <template #smart-bar-actions>
        {# Good: Check permission for cancel (always visible) #}
        <sw-button @click="onCancel">
            {{ $tc('global.default.cancel') }}
        </sw-button>

        {# Good: Disable save button if no edit permission #}
        <sw-button-process
            :disabled="!acl.can('my_plugin.editor')"
            :isLoading="isLoading"
            variant="primary"
            @click="onSave"
        >
            {{ $tc('global.default.save') }}
        </sw-button-process>
    </template>
{% endblock %}

{% block my_plugin_detail_content %}
    <template #content>
        <sw-card :isLoading="isLoading">
            {# Good: Disable form fields if no edit permission #}
            <sw-text-field
                v-model="entity.name"
                :label="$tc('my-plugin.detail.labelName')"
                :disabled="!acl.can('my_plugin.editor')"
                required
            />

            <sw-switch-field
                v-model="entity.active"
                :label="$tc('my-plugin.detail.labelActive')"
                :disabled="!acl.can('my_plugin.editor')"
            />
        </sw-card>

        {# Good: Hide delete card entirely if no permission #}
        <sw-card
            v-if="acl.can('my_plugin.deleter') && !isCreateMode"
            :title="$tc('my-plugin.detail.dangerZone')"
        >
            <sw-button
                variant="danger"
                @click="onDelete"
            >
                {{ $tc('global.default.delete') }}
            </sw-button>
        </sw-card>
    </template>
{% endblock %}
```

**Correct list page with ACL:**

```twig
{% block my_plugin_list %}
    <sw-page class="my-plugin-list">
        {% block my_plugin_list_actions %}
            <template #smart-bar-actions>
                {# Good: Only show create button with permission #}
                <sw-button
                    v-if="acl.can('my_plugin.creator')"
                    :routerLink="{ name: 'my.plugin.module.create' }"
                    variant="primary"
                >
                    {{ $tc('my-plugin.list.buttonCreate') }}
                </sw-button>
            </template>
        {% endblock %}

        {% block my_plugin_list_content %}
            <template #content>
                <sw-entity-listing
                    :items="items"
                    :columns="columns"
                    :repository="repository"
                    :isLoading="isLoading"
                    :allowEdit="acl.can('my_plugin.editor')"
                    :allowDelete="acl.can('my_plugin.deleter')"
                    :allowInlineEdit="acl.can('my_plugin.editor')"
                    @inline-edit-save="onInlineEditSave"
                >
                    {# Good: Context menu with permission checks #}
                    <template #actions="{ item }">
                        <sw-context-menu-item
                            :routerLink="{ name: 'my.plugin.module.detail', params: { id: item.id } }"
                        >
                            {{ $tc('global.default.edit') }}
                        </sw-context-menu-item>

                        <sw-context-menu-item
                            v-if="acl.can('my_plugin.deleter')"
                            variant="danger"
                            @click="onDelete(item.id)"
                        >
                            {{ $tc('global.default.delete') }}
                        </sw-context-menu-item>
                    </template>
                </sw-entity-listing>
            </template>
        {% endblock %}
    </sw-page>
{% endblock %}
```

**Define ACL privileges in XML:**

```xml
<!-- src/Resources/config/acl.xml -->
<?xml version="1.0" ?>
<privileges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/Framework/Resources/config/acl.xsd">

    <acl>
        <!-- Viewer: read-only access -->
        <role name="my_plugin.viewer">
            <privilege>my_plugin_entity:read</privilege>
            <privilege>product:read</privilege>
        </role>

        <!-- Editor: can modify -->
        <role name="my_plugin.editor">
            <parent>my_plugin.viewer</parent>
            <privilege>my_plugin_entity:update</privilege>
        </role>

        <!-- Creator: can create new -->
        <role name="my_plugin.creator">
            <parent>my_plugin.editor</parent>
            <privilege>my_plugin_entity:create</privilege>
        </role>

        <!-- Deleter: can delete -->
        <role name="my_plugin.deleter">
            <parent>my_plugin.editor</parent>
            <privilege>my_plugin_entity:delete</privilege>
        </role>
    </acl>
</privileges>
```

**Route meta privileges:**

```javascript
// module/index.js
Module.register('my-plugin-module', {
    routes: {
        list: {
            component: 'my-plugin-list',
            path: 'list',
            meta: {
                privilege: 'my_plugin.viewer'  // Required to access route
            }
        },
        detail: {
            component: 'my-plugin-detail',
            path: 'detail/:id',
            meta: {
                privilege: 'my_plugin.viewer'
            }
        },
        create: {
            component: 'my-plugin-detail',
            path: 'create',
            meta: {
                privilege: 'my_plugin.creator'  // Stricter for create
            }
        }
    },

    navigation: [{
        id: 'my-plugin-module',
        path: 'my.plugin.module.list',
        privilege: 'my_plugin.viewer'  // Hide nav if no permission
    }]
});
```

**Common privilege patterns:**

| Role | Privileges | Use Case |
|------|------------|----------|
| `viewer` | `:read` | View-only users |
| `editor` | `:read`, `:update` | Can modify existing |
| `creator` | `:read`, `:update`, `:create` | Can create new |
| `deleter` | `:read`, `:update`, `:delete` | Can delete |
| `admin` | All of the above | Full access |

Reference: [ACL in Administration](https://developer.shopware.com/docs/guides/plugins/plugins/administration/add-acl-rules.html)
