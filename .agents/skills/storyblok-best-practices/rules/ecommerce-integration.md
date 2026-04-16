---
title: Integrate E-commerce Platforms
impact: HIGH
impactDescription: enables headless commerce with content management
tags: ecommerce, shopify, commercetools, shopware, products
---

## Integrate E-commerce Platforms

**Impact: HIGH (enables headless commerce with content management)**

Storyblok excels as the content layer for headless commerce. Store product references in Storyblok and fetch product data from your e-commerce platform at runtime.

**Incorrect (storing product data in Storyblok):**

```json
// Bad: Duplicating e-commerce data in Storyblok
{
  "name": "product",
  "schema": {
    "product_name": { "type": "text" },
    "price": { "type": "number" },
    "sku": { "type": "text" },
    "inventory": { "type": "number" },
    "variants": { "type": "bloks" }
    // This data gets stale immediately!
  }
}
```

```jsx
// Bad: Fetching all product data from Storyblok
const ProductPage = async ({ slug }) => {
  const { data } = await storyblokApi.get(`cdn/stories/products/${slug}`);
  const product = data.story.content;

  return (
    <div>
      <h1>{product.product_name}</h1>
      <span>${product.price}</span> {/* Stale price! */}
      <span>In stock: {product.inventory}</span> {/* Stale inventory! */}
    </div>
  );
};
```

**Correct (reference-based integration):**

```json
// Good: Store only reference and CMS content
{
  "name": "product_page",
  "schema": {
    "product_id": {
      "type": "text",
      "display_name": "Product ID/SKU",
      "description": "Enter the product ID from your e-commerce platform"
    },
    "hero_content": {
      "type": "bloks",
      "display_name": "Hero Content",
      "restrict_components": true,
      "component_whitelist": ["hero", "product_gallery"]
    },
    "description": {
      "type": "richtext",
      "display_name": "Marketing Description",
      "translatable": true
    },
    "features": {
      "type": "bloks",
      "component_whitelist": ["feature_list", "comparison_table"]
    },
    "related_content": {
      "type": "bloks",
      "component_whitelist": ["article_grid", "testimonials"]
    }
  }
}
```

```jsx
// Good: Two-step fetching pattern
// app/products/[slug]/page.jsx
import { getStoryblokApi } from '@/lib/storyblok';
import { getProduct } from '@/lib/commerce';

export default async function ProductPage({ params }) {
  // Step 1: Fetch CMS content (marketing, layout)
  const storyblokApi = getStoryblokApi();
  const { data: storyData } = await storyblokApi.get(
    `cdn/stories/products/${params.slug}`,
    { version: 'published' }
  );

  const cmsContent = storyData.story.content;
  const productId = cmsContent.product_id;

  // Step 2: Fetch real-time product data from commerce platform
  const product = await getProduct(productId);

  return (
    <main>
      {/* CMS-controlled hero/marketing content */}
      <StoryblokComponent blok={cmsContent.hero_content} />

      {/* Real-time product data */}
      <ProductDetails product={product} />

      {/* CMS-controlled description */}
      <RichText content={cmsContent.description} />

      {/* Real-time pricing and inventory */}
      <AddToCart
        productId={product.id}
        price={product.price}
        available={product.inventory > 0}
      />

      {/* CMS-controlled features and content */}
      <StoryblokComponent blok={cmsContent.features} />
    </main>
  );
}
```

```javascript
// Good: Shopify integration
// lib/shopify.js
import { createStorefrontClient } from '@shopify/hydrogen-react';

const client = createStorefrontClient({
  storeDomain: process.env.SHOPIFY_STORE_DOMAIN,
  publicStorefrontToken: process.env.SHOPIFY_STOREFRONT_TOKEN
});

export async function getProduct(handle) {
  const { data } = await client.query({
    query: `
      query GetProduct($handle: String!) {
        product(handle: $handle) {
          id
          title
          handle
          priceRange {
            minVariantPrice {
              amount
              currencyCode
            }
          }
          variants(first: 10) {
            nodes {
              id
              title
              availableForSale
              price {
                amount
                currencyCode
              }
            }
          }
          images(first: 5) {
            nodes {
              url
              altText
            }
          }
        }
      }
    `,
    variables: { handle }
  });

  return data.product;
}
```

```javascript
// Good: commercetools integration
// lib/commercetools.js
import { createApiBuilderFromCtpClient } from '@commercetools/platform-sdk';
import { ClientBuilder } from '@commercetools/sdk-client-v2';

const ctpClient = new ClientBuilder()
  .withProjectKey(process.env.CTP_PROJECT_KEY)
  .withClientCredentialsFlow({
    host: process.env.CTP_AUTH_URL,
    projectKey: process.env.CTP_PROJECT_KEY,
    credentials: {
      clientId: process.env.CTP_CLIENT_ID,
      clientSecret: process.env.CTP_CLIENT_SECRET
    }
  })
  .withHttpMiddleware({ host: process.env.CTP_API_URL })
  .build();

const apiRoot = createApiBuilderFromCtpClient(ctpClient)
  .withProjectKey({ projectKey: process.env.CTP_PROJECT_KEY });

export async function getProduct(productId) {
  const response = await apiRoot
    .products()
    .withId({ ID: productId })
    .get()
    .execute();

  return response.body;
}
```

```jsx
// Good: Product selector field plugin for editors
// Storyblok field plugin that searches e-commerce API
import { useFieldPlugin } from '@storyblok/field-plugin/react';

const ProductSelector = () => {
  const { data, actions } = useFieldPlugin();
  const [search, setSearch] = useState('');
  const [results, setResults] = useState([]);

  const searchProducts = async (query) => {
    const response = await fetch(`/api/products/search?q=${query}`);
    const products = await response.json();
    setResults(products);
  };

  const selectProduct = (product) => {
    actions.setContent({
      id: product.id,
      name: product.title,
      image: product.images[0]?.url
    });
  };

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyUp={() => searchProducts(search)}
        placeholder="Search products..."
      />
      <ul>
        {results.map(product => (
          <li key={product.id} onClick={() => selectProduct(product)}>
            <img src={product.image} alt="" />
            {product.title} - ${product.price}
          </li>
        ))}
      </ul>
      {data.content && (
        <div>Selected: {data.content.name}</div>
      )}
    </div>
  );
};
```

**Integration patterns by platform:**

| Platform | Connection | Product Reference |
|----------|------------|-------------------|
| Shopify | Storefront API | Handle or ID |
| commercetools | Platform SDK | Product ID |
| Shopware | Store API | Product ID |
| BigCommerce | GraphQL API | Product ID |
| Medusa | REST/JS SDK | Product ID |

**Data ownership:**

| Data Type | Source | Reason |
|-----------|--------|--------|
| Price, inventory | E-commerce | Real-time accuracy |
| Variants, SKUs | E-commerce | Single source of truth |
| Marketing copy | Storyblok | Editorial control |
| Hero images | Storyblok | Design flexibility |
| SEO content | Storyblok | Multi-language support |
| Related content | Storyblok | Cross-sell flexibility |

Reference: [E-commerce Integration](https://www.storyblok.com/tp/headless-ecommerce-guide)
