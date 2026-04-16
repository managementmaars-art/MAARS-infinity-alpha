---
title: Use Consistent Naming Conventions
impact: HIGH
impactDescription: improves maintainability and developer experience
tags: naming, conventions, schema, organization
---

## Use Consistent Naming Conventions

**Impact: HIGH (improves maintainability and developer experience)**

Consistent naming across components, fields, and folders makes the codebase predictable and easier to maintain. Use snake_case for technical names and human-readable display names.

**Incorrect (inconsistent naming):**

```json
// Bad: Mixed conventions and unclear names
{
  "components": [
    { "name": "HeroSection" },      // PascalCase
    { "name": "feature-card" },     // kebab-case
    { "name": "ctaButton" },        // camelCase
    { "name": "TESTIMONIAL" }       // SCREAMING_CASE
  ]
}

// Bad: Unclear field names
{
  "name": "card",
  "schema": {
    "t": { "type": "text" },        // Abbreviated
    "desc": { "type": "textarea" }, // Abbreviated
    "img1": { "type": "asset" },    // Numbered
    "TheLink": { "type": "link" }   // PascalCase
  }
}
```

**Correct (consistent naming):**

```json
// Good: Consistent snake_case for component names
{
  "components": [
    { "name": "hero_section", "display_name": "Hero Section" },
    { "name": "feature_card", "display_name": "Feature Card" },
    { "name": "cta_button", "display_name": "CTA Button" },
    { "name": "testimonial_card", "display_name": "Testimonial Card" }
  ]
}

// Good: Clear, descriptive field names
{
  "name": "product_card",
  "display_name": "Product Card",
  "schema": {
    "title": {
      "type": "text",
      "display_name": "Product Title"
    },
    "description": {
      "type": "textarea",
      "display_name": "Product Description"
    },
    "featured_image": {
      "type": "asset",
      "display_name": "Featured Image"
    },
    "product_link": {
      "type": "link",
      "display_name": "Product Link"
    },
    "price_amount": {
      "type": "number",
      "display_name": "Price"
    },
    "is_featured": {
      "type": "boolean",
      "display_name": "Featured Product"
    }
  }
}
```

**Naming conventions table:**

| Element | Convention | Example |
|---------|------------|---------|
| Component name | snake_case | `hero_section` |
| Component display_name | Title Case | `Hero Section` |
| Field name | snake_case | `featured_image` |
| Field display_name | Title Case | `Featured Image` |
| Datasource slug | kebab-case | `product-categories` |
| Folder slug | kebab-case | `blog-posts` |
| Story slug | kebab-case | `about-us` |

**Prefixes for organization:**

```json
// Group related components with prefixes
{
  "components": [
    // Layout components
    { "name": "layout_header" },
    { "name": "layout_footer" },
    { "name": "layout_sidebar" },

    // Card variants
    { "name": "card_product" },
    { "name": "card_article" },
    { "name": "card_team_member" },

    // Form elements
    { "name": "form_input" },
    { "name": "form_select" },
    { "name": "form_textarea" },

    // SEO/Meta
    { "name": "seo_meta" },
    { "name": "seo_open_graph" }
  ]
}
```

Reference: [Component Schema](https://www.storyblok.com/docs/api/management/components/the-component-schema-field-object)
