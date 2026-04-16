---
title: Follow Atomic Design for Components
impact: CRITICAL
impactDescription: ensures scalable and maintainable content architecture
tags: component, atomic-design, schema, structure
---

## Follow Atomic Design for Components

**Impact: CRITICAL (ensures scalable and maintainable content architecture)**

Components should follow atomic design principles: atoms (basic fields), molecules (combined blocks), organisms (complex sections), and content types (page templates). This creates reusable, composable structures.

**Incorrect (flat, monolithic components):**

```json
// Bad: One massive component with everything
{
  "name": "homepage",
  "schema": {
    "hero_title": { "type": "text" },
    "hero_subtitle": { "type": "text" },
    "hero_image": { "type": "asset" },
    "hero_cta_text": { "type": "text" },
    "hero_cta_link": { "type": "link" },
    "features_title": { "type": "text" },
    "feature_1_title": { "type": "text" },
    "feature_1_description": { "type": "textarea" },
    "feature_2_title": { "type": "text" },
    "feature_2_description": { "type": "textarea" },
    "testimonial_text": { "type": "textarea" },
    "testimonial_author": { "type": "text" }
    // ... continues with 50+ fields
  }
}
```

**Correct (atomic, composable components):**

```json
// Good: Atom - Button component
{
  "name": "button",
  "is_nestable": true,
  "schema": {
    "label": { "type": "text", "required": true },
    "link": { "type": "link" },
    "variant": {
      "type": "option",
      "options": [
        { "name": "Primary", "value": "primary" },
        { "name": "Secondary", "value": "secondary" }
      ]
    }
  }
}

// Good: Molecule - Hero component using atoms
{
  "name": "hero",
  "is_nestable": true,
  "schema": {
    "title": { "type": "text", "required": true },
    "subtitle": { "type": "text" },
    "image": { "type": "asset", "filetypes": ["images"] },
    "buttons": {
      "type": "bloks",
      "restrict_components": true,
      "component_whitelist": ["button"],
      "maximum": 2
    }
  }
}

// Good: Organism - Feature grid
{
  "name": "feature_grid",
  "is_nestable": true,
  "schema": {
    "headline": { "type": "text" },
    "features": {
      "type": "bloks",
      "restrict_components": true,
      "component_whitelist": ["feature_card"],
      "minimum": 1,
      "maximum": 6
    }
  }
}

// Good: Content type - Page template
{
  "name": "page",
  "is_root": true,
  "schema": {
    "body": {
      "type": "bloks",
      "restrict_components": true,
      "component_whitelist": ["hero", "feature_grid", "testimonials", "cta_section"]
    },
    "seo": { "type": "bloks", "component_whitelist": ["seo_meta"] }
  }
}
```

**Component hierarchy:**

| Level | Type | Purpose | Example |
|-------|------|---------|---------|
| Atom | Nestable | Single responsibility | Button, Image, Text |
| Molecule | Nestable | Combined atoms | Card, Hero, Form Field |
| Organism | Nestable | Page sections | Feature Grid, Testimonials |
| Template | Root | Page structure | Page, Article, Product |

Reference: [Content Modeling](https://www.storyblok.com/docs/concepts/content-modeling)
