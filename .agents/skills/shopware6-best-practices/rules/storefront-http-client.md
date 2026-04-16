---
title: AJAX & HttpClient Usage
impact: MEDIUM
impactDescription: proper asynchronous communication with Store API
tags: storefront, javascript, ajax, http, api, fetch
---

## AJAX & HttpClient Usage

**Impact: MEDIUM (proper asynchronous communication with Store API)**

Use Shopware's HttpClient service for AJAX requests. It handles CSRF tokens, content types, and error handling automatically. Never use raw fetch/XMLHttpRequest without proper headers.

**Incorrect (raw fetch without proper headers):**

```javascript
// Bad: Raw fetch without CSRF token
fetch('/store-api/product', {
    method: 'POST',
    body: JSON.stringify({ ids: productIds })
})
.then(response => response.json())
.then(data => console.log(data));

// Bad: Missing content type and SW headers
$.ajax({
    url: '/my-plugin/action',
    method: 'POST',
    data: formData
});
```

**Correct (using HttpClient service):**

```javascript
import HttpClient from 'src/service/http-client.service';

export default class MyPlugin extends Plugin {
    init() {
        this._client = new HttpClient();
    }

    loadProducts() {
        // Good: GET request
        this._client.get('/store-api/product', (response) => {
            const data = JSON.parse(response);
            this._renderProducts(data.elements);
        });
    }

    submitForm(formData) {
        // Good: POST request with data
        this._client.post('/store-api/checkout/cart/line-item', formData, (response) => {
            const result = JSON.parse(response);
            this._onSuccess(result);
        });
    }

    updateWithJson(data) {
        // Good: POST with JSON content type
        const jsonData = JSON.stringify(data);

        this._client.post(
            '/store-api/my-plugin/update',
            jsonData,
            (response) => {
                this._handleResponse(JSON.parse(response));
            },
            'application/json'
        );
    }
}
```

**Correct Store API requests with includes:**

```javascript
// Good: Request specific fields only (reduces response size)
loadProductWithIncludes() {
    const payload = JSON.stringify({
        includes: {
            product: ['id', 'name', 'calculatedPrice', 'cover'],
            product_media: ['media'],
            media: ['url', 'alt']
        },
        associations: {
            cover: {
                associations: {
                    media: {}
                }
            }
        }
    });

    this._client.post('/store-api/product', payload, (response) => {
        const data = JSON.parse(response);
        this._renderProducts(data.elements);
    }, 'application/json');
}
```

**Correct error handling:**

```javascript
import HttpClient from 'src/service/http-client.service';

export default class MyPlugin extends Plugin {
    init() {
        this._client = new HttpClient();
    }

    async fetchData() {
        const url = '/store-api/my-plugin/data';

        this._client.get(url, (response) => {
            try {
                const data = JSON.parse(response);

                if (data.errors && data.errors.length > 0) {
                    this._handleApiErrors(data.errors);
                    return;
                }

                this._onSuccess(data);
            } catch (e) {
                this._handleParseError(e);
            }
        }, (error) => {
            // Error callback
            this._handleNetworkError(error);
        });
    }

    _handleApiErrors(errors) {
        errors.forEach(error => {
            console.error(`API Error: ${error.detail}`);
            this._showNotification(error.detail, 'error');
        });
    }

    _handleNetworkError(error) {
        console.error('Network error:', error);
        this._showNotification('Network error. Please try again.', 'error');
    }
}
```

**Correct form submission with FormData:**

```javascript
import HttpClient from 'src/service/http-client.service';
import FormSerializeUtil from 'src/utility/form/form-serialize.util';

export default class MyFormPlugin extends Plugin {
    init() {
        this._client = new HttpClient();
        this._form = this.el.querySelector('form');
        this._registerEvents();
    }

    _registerEvents() {
        this._form.addEventListener('submit', this._onSubmit.bind(this));
    }

    _onSubmit(event) {
        event.preventDefault();

        // Serialize form data
        const formData = FormSerializeUtil.serialize(this._form);

        // Add CSRF token if needed
        const csrfInput = this._form.querySelector('input[name="_csrf_token"]');
        if (csrfInput) {
            formData.append('_csrf_token', csrfInput.value);
        }

        this._client.post(
            this._form.action,
            formData,
            this._onSuccess.bind(this),
            this._getContentType()
        );
    }

    _getContentType() {
        // Let browser set content type for FormData (multipart)
        return false;
    }

    _onSuccess(response) {
        const data = JSON.parse(response);
        window.location.reload();
    }
}
```

**Using the PageLoading indicator:**

```javascript
import HttpClient from 'src/service/http-client.service';

export default class MyPlugin extends Plugin {
    init() {
        this._client = new HttpClient();
    }

    loadData() {
        // Show loading indicator
        this.$emitter.publish('beforeLoad');

        // Create page loading indicator
        const indicator = document.createElement('div');
        indicator.classList.add('loader');
        this.el.appendChild(indicator);

        this._client.get('/store-api/my-data', (response) => {
            // Hide loading indicator
            indicator.remove();

            this.$emitter.publish('afterLoad');
            this._processResponse(response);
        });
    }
}
```

**Correct AJAX pagination pattern:**

```javascript
export default class InfiniteScrollPlugin extends Plugin {
    static options = {
        loadMoreSelector: '.load-more-btn',
        containerSelector: '.product-list',
        apiUrl: '/store-api/product'
    };

    init() {
        this._client = new HttpClient();
        this._page = 1;
        this._limit = 24;
        this._isLoading = false;

        this._registerEvents();
    }

    _registerEvents() {
        const loadMoreBtn = this.el.querySelector(this.options.loadMoreSelector);
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', this._loadMore.bind(this));
        }
    }

    _loadMore(event) {
        event.preventDefault();

        if (this._isLoading) return;
        this._isLoading = true;

        this._page++;

        const payload = JSON.stringify({
            page: this._page,
            limit: this._limit,
            includes: {
                product: ['id', 'name', 'calculatedPrice', 'cover']
            }
        });

        this._client.post(this.options.apiUrl, payload, (response) => {
            const data = JSON.parse(response);
            this._appendProducts(data.elements);
            this._isLoading = false;

            // Hide button if no more products
            if (data.elements.length < this._limit) {
                this._hideLoadMoreButton();
            }
        }, 'application/json');
    }

    _appendProducts(products) {
        const container = this.el.querySelector(this.options.containerSelector);
        products.forEach(product => {
            container.insertAdjacentHTML('beforeend', this._renderProduct(product));
        });
    }
}
```

Reference: [JavaScript & AJAX](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-custom-javascript.html)
