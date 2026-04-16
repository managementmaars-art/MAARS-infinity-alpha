---
title: Vue Component Patterns
impact: HIGH
impactDescription: consistent component architecture for maintainable admin code
tags: administration, vue, component, template, pattern
---

## Vue Component Patterns

**Impact: HIGH (consistent component architecture for maintainable admin code)**

Administration components must follow Shopware's component patterns using `Component.register()`, proper template separation, and injection for services. Never use Vue's global registration directly.

**Incorrect (Vue global registration):**

```javascript
// Bad: Direct Vue component registration
Vue.component('my-component', {
    template: '<div>{{ message }}</div>',
    data() {
        return { message: 'Hello' };
    }
});
```

```javascript
// Bad: Inline template string
Component.register('my-component', {
    template: `
        <div class="my-component">
            <h1>{{ title }}</h1>
            <p>{{ description }}</p>
        </div>
    `
});
```

**Correct component registration:**

```javascript
// src/module/my-plugin/component/my-plugin-card/index.js

import template from './my-plugin-card.html.twig';
import './my-plugin-card.scss';

const { Component } = Shopware;

Component.register('my-plugin-card', {
    template,

    props: {
        item: {
            type: Object,
            required: true
        },
        isLoading: {
            type: Boolean,
            required: false,
            default: false
        }
    },

    computed: {
        formattedDate() {
            if (!this.item.createdAt) {
                return '';
            }
            return this.item.createdAt.toLocaleString();
        }
    },

    methods: {
        onCardClick() {
            this.$emit('card-click', this.item);
        }
    }
});
```

**Correct Twig template:**

```twig
{# src/module/my-plugin/component/my-plugin-card/my-plugin-card.html.twig #}

{% block my_plugin_card %}
    <sw-card
        class="my-plugin-card"
        :isLoading="isLoading"
        @click="onCardClick"
    >
        {% block my_plugin_card_header %}
            <template #header>
                <sw-card-header>
                    {{ item.name }}
                </sw-card-header>
            </template>
        {% endblock %}

        {% block my_plugin_card_content %}
            <div class="my-plugin-card__content">
                {% block my_plugin_card_status %}
                    <sw-label
                        :variant="item.active ? 'success' : 'neutral'"
                        size="small"
                    >
                        {{ item.active ? $tc('global.default.active') : $tc('global.default.inactive') }}
                    </sw-label>
                {% endblock %}

                {% block my_plugin_card_description %}
                    <p class="my-plugin-card__description">
                        {{ item.description }}
                    </p>
                {% endblock %}

                {% block my_plugin_card_meta %}
                    <div class="my-plugin-card__meta">
                        {{ $tc('my-plugin.card.createdAt') }}: {{ formattedDate }}
                    </div>
                {% endblock %}
            </div>
        {% endblock %}
    </sw-card>
{% endblock %}
```

**Correct detail page component:**

```javascript
// src/module/my-plugin/page/my-plugin-detail/index.js

import template from './my-plugin-detail.html.twig';

const { Component, Mixin } = Shopware;
const { mapPropertyErrors } = Shopware.Component.getComponentHelper();

Component.register('my-plugin-detail', {
    template,

    inject: [
        'repositoryFactory',
        'acl'
    ],

    mixins: [
        Mixin.getByName('notification'),
        Mixin.getByName('placeholder')
    ],

    props: {
        entityId: {
            type: String,
            required: false,
            default: null
        }
    },

    data() {
        return {
            entity: null,
            isLoading: false,
            isSaveSuccessful: false
        };
    },

    metaInfo() {
        return {
            title: this.$createTitle(this.identifier)
        };
    },

    computed: {
        repository() {
            return this.repositoryFactory.create('my_plugin_entity');
        },

        isCreateMode() {
            return this.entityId === null;
        },

        identifier() {
            return this.entity?.name || '';
        },

        ...mapPropertyErrors('entity', ['name'])
    },

    watch: {
        entityId() {
            this.loadEntity();
        }
    },

    created() {
        this.loadEntity();
    },

    methods: {
        async loadEntity() {
            this.isLoading = true;

            if (this.isCreateMode) {
                this.entity = this.repository.create();
                this.entity.active = true;
                this.isLoading = false;
                return;
            }

            try {
                this.entity = await this.repository.get(this.entityId);
            } catch (error) {
                this.createNotificationError({
                    message: error.message
                });
            } finally {
                this.isLoading = false;
            }
        },

        async onSave() {
            this.isLoading = true;
            this.isSaveSuccessful = false;

            try {
                await this.repository.save(this.entity);

                this.isSaveSuccessful = true;

                if (this.isCreateMode) {
                    this.$router.push({
                        name: 'my.plugin.module.detail',
                        params: { id: this.entity.id }
                    });
                }

                this.createNotificationSuccess({
                    message: this.$tc('my-plugin.detail.saveSuccess')
                });
            } catch (error) {
                this.createNotificationError({
                    message: error.message
                });
            } finally {
                this.isLoading = false;
            }
        },

        onCancel() {
            this.$router.push({ name: 'my.plugin.module.list' });
        }
    }
});
```

**Correct detail template with form:**

```twig
{# src/module/my-plugin/page/my-plugin-detail/my-plugin-detail.html.twig #}

{% block my_plugin_detail %}
    <sw-page class="my-plugin-detail">
        {% block my_plugin_detail_header %}
            <template #smart-bar-header>
                <h2 v-if="isCreateMode">
                    {{ $tc('my-plugin.detail.titleNew') }}
                </h2>
                <h2 v-else>
                    {{ placeholder(entity, 'name', $tc('my-plugin.detail.title')) }}
                </h2>
            </template>
        {% endblock %}

        {% block my_plugin_detail_actions %}
            <template #smart-bar-actions>
                <sw-button
                    v-tooltip.bottom="$tc('global.default.cancel')"
                    @click="onCancel"
                >
                    {{ $tc('global.default.cancel') }}
                </sw-button>

                <sw-button-process
                    v-tooltip.bottom="$tc('global.default.save')"
                    class="my-plugin-detail__save-action"
                    :isLoading="isLoading"
                    :processSuccess="isSaveSuccessful"
                    :disabled="!acl.can('my_plugin.editor')"
                    variant="primary"
                    @process-finish="isSaveSuccessful = false"
                    @click="onSave"
                >
                    {{ $tc('global.default.save') }}
                </sw-button-process>
            </template>
        {% endblock %}

        {% block my_plugin_detail_content %}
            <template #content>
                <sw-card-view>
                    <sw-card
                        :title="$tc('my-plugin.detail.cardTitle')"
                        :isLoading="isLoading"
                    >
                        {% block my_plugin_detail_form %}
                            <sw-container columns="1fr 1fr" gap="0 32px">
                                {% block my_plugin_detail_name %}
                                    <sw-text-field
                                        v-model="entity.name"
                                        :label="$tc('my-plugin.detail.labelName')"
                                        :placeholder="$tc('my-plugin.detail.placeholderName')"
                                        :error="entityNameError"
                                        :disabled="!acl.can('my_plugin.editor')"
                                        required
                                    />
                                {% endblock %}

                                {% block my_plugin_detail_active %}
                                    <sw-switch-field
                                        v-model="entity.active"
                                        :label="$tc('my-plugin.detail.labelActive')"
                                        :disabled="!acl.can('my_plugin.editor')"
                                    />
                                {% endblock %}
                            </sw-container>
                        {% endblock %}
                    </sw-card>
                </sw-card-view>
            </template>
        {% endblock %}
    </sw-page>
{% endblock %}
```

**Common Shopware admin components:**

| Component | Purpose |
|-----------|---------|
| `sw-page` | Page layout wrapper |
| `sw-card` | Content card container |
| `sw-card-view` | Card grid layout |
| `sw-button` | Standard button |
| `sw-button-process` | Button with loading state |
| `sw-text-field` | Text input |
| `sw-switch-field` | Toggle switch |
| `sw-select-field` | Dropdown select |
| `sw-entity-single-select` | Entity picker |
| `sw-data-grid` | Data table |
| `sw-container` | Grid layout |

Reference: [Admin Components](https://developer.shopware.com/docs/guides/plugins/plugins/administration/add-custom-component.html)
