---
title: Repository & Data Handling
impact: HIGH
impactDescription: correct data operations ensure consistency and performance
tags: administration, vue, repository, data, criteria, api
---

## Repository & Data Handling

**Impact: HIGH (correct data operations ensure consistency and performance)**

Use Shopware's repository factory and Criteria API for all data operations in the administration. Never make direct API calls or manipulate data outside the repository pattern.

**Incorrect (direct API calls):**

```javascript
// Bad: Direct HTTP calls
async loadProducts() {
    const response = await fetch('/api/product');
    this.products = await response.json();
}

// Bad: Using axios or other HTTP clients directly
async saveEntity() {
    await axios.post('/api/my-entity', this.entity);
}
```

**Correct (using repository factory):**

```javascript
const { Component } = Shopware;
const { Criteria } = Shopware.Data;

Component.register('my-plugin-list', {
    inject: [
        'repositoryFactory',
        'context'
    ],

    data() {
        return {
            items: null,
            isLoading: false
        };
    },

    computed: {
        // Good: Create repository from factory
        repository() {
            return this.repositoryFactory.create('my_plugin_entity');
        },

        productRepository() {
            return this.repositoryFactory.create('product');
        }
    },

    created() {
        this.loadItems();
    },

    methods: {
        async loadItems() {
            this.isLoading = true;

            const criteria = new Criteria();
            criteria.setLimit(25);
            criteria.addSorting(Criteria.sort('createdAt', 'DESC'));

            // Good: Use repository.search() with criteria
            this.items = await this.repository.search(criteria);
            this.isLoading = false;
        }
    }
});
```

**Correct Criteria usage:**

```javascript
const { Criteria } = Shopware.Data;

// Basic criteria with pagination
const criteria = new Criteria(1, 25); // page 1, limit 25

// Adding filters
criteria.addFilter(Criteria.equals('active', true));
criteria.addFilter(Criteria.contains('name', searchTerm));
criteria.addFilter(Criteria.range('price', { gte: 100, lte: 500 }));

// Multiple filters with AND/OR
criteria.addFilter(Criteria.multi('OR', [
    Criteria.equals('status', 'open'),
    Criteria.equals('status', 'pending')
]));

criteria.addFilter(Criteria.multi('AND', [
    Criteria.equals('active', true),
    Criteria.not('OR', [
        Criteria.equals('stock', 0)
    ])
]));

// Adding associations
criteria.addAssociation('manufacturer');
criteria.addAssociation('categories');
criteria.addAssociation('cover.media');

// Nested association with filters
criteria.getAssociation('categories')
    .addFilter(Criteria.equals('active', true))
    .setLimit(10);

// Sorting
criteria.addSorting(Criteria.sort('name', 'ASC'));
criteria.addSorting(Criteria.sort('createdAt', 'DESC'));

// Aggregations
criteria.addAggregation(Criteria.sum('totalStock', 'stock'));
criteria.addAggregation(Criteria.avg('averagePrice', 'price.gross'));
criteria.addAggregation(Criteria.count('productCount', 'id'));

// Search term
criteria.setTerm('search query');

// Total count mode
criteria.setTotalCountMode(1); // exact count
```

**Correct entity creation and saving:**

```javascript
methods: {
    // Create new entity
    createEntity() {
        // Good: Use repository.create() for new entities
        this.entity = this.repository.create();

        // Set defaults
        this.entity.active = true;
        this.entity.priority = 1;
    },

    // Save entity (create or update)
    async saveEntity() {
        this.isLoading = true;

        try {
            // Good: Use repository.save() - handles create and update
            await this.repository.save(this.entity);

            this.createNotificationSuccess({
                message: this.$tc('global.notification.saveSuccess')
            });
        } catch (error) {
            this.createNotificationError({
                message: error.message
            });
        } finally {
            this.isLoading = false;
        }
    },

    // Load single entity by ID
    async loadEntity(id) {
        // Good: Use repository.get() for single entity
        this.entity = await this.repository.get(id);
    },

    // Delete entity
    async deleteEntity(id) {
        try {
            // Good: Use repository.delete()
            await this.repository.delete(id);

            this.createNotificationSuccess({
                message: this.$tc('global.notification.deleteSuccess')
            });
        } catch (error) {
            this.createNotificationError({
                message: error.message
            });
        }
    },

    // Clone entity
    async cloneEntity(id) {
        // Good: Use repository.clone()
        const clonedEntity = await this.repository.clone(id);
        return clonedEntity;
    }
}
```

**Correct handling of associations:**

```javascript
async loadProductWithAssociations(productId) {
    const criteria = new Criteria();
    criteria.setIds([productId]);

    // Load specific associations
    criteria.addAssociation('manufacturer');
    criteria.addAssociation('categories');
    criteria.addAssociation('media');
    criteria.addAssociation('cover.media');

    const products = await this.productRepository.search(criteria);
    this.product = products.first();
}

// Save entity with many-to-many associations
async saveProductCategories(product, categoryIds) {
    // Good: Set association as entity collection
    const criteria = new Criteria();
    criteria.setIds(categoryIds);

    const categories = await this.categoryRepository.search(criteria);
    product.categories = categories;

    await this.productRepository.save(product);
}

// Add single association
async addCategory(product, categoryId) {
    const category = await this.categoryRepository.get(categoryId);

    if (!product.categories) {
        product.categories = new EntityCollection(
            '/category',
            'category',
            Shopware.Context.api
        );
    }

    product.categories.add(category);
    await this.productRepository.save(product);
}
```

**Correct sync operations for bulk updates:**

```javascript
async bulkUpdate(items, changes) {
    // Good: Use syncService for bulk operations
    const syncService = Shopware.Service('syncService');

    const payload = items.map(item => ({
        ...changes,
        id: item.id
    }));

    await syncService.sync([
        {
            action: 'upsert',
            entity: 'my_plugin_entity',
            payload: payload
        }
    ], {}, { 'single-operation': true });
}

// Bulk delete
async bulkDelete(ids) {
    const payload = ids.map(id => ({ id }));

    await this.syncService.sync([
        {
            action: 'delete',
            entity: 'my_plugin_entity',
            payload: payload
        }
    ], {}, { 'single-operation': true });
}
```

**Using state management:**

```javascript
// Access and modify global state
const languageId = Shopware.State.get('context').api.languageId;

// Commit state changes
Shopware.State.commit('context/setApiLanguageId', newLanguageId);

// Watch state changes
Shopware.State.watch(
    (state) => state.context.api.languageId,
    (newValue) => {
        this.onLanguageChange(newValue);
    }
);
```

Reference: [Data Handling](https://developer.shopware.com/docs/guides/plugins/plugins/administration/using-data-handling.html)
