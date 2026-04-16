---
title: Manage Block Nesting Carefully
impact: HIGH
impactDescription: prevents overly complex content structures
tags: blocks, nesting, components, restrictions
---

## Manage Block Nesting Carefully

**Impact: HIGH (prevents overly complex content structures)**

Block nesting enables flexible content composition but can lead to complexity. Use restrictions and limits to guide editors while maintaining flexibility.

**Incorrect (unrestricted nesting):**

```json
// Bad: Any component anywhere with no limits
{
  "name": "page",
  "schema": {
    "body": {
      "type": "bloks"
      // No restrictions - allows any nestable component
      // Can nest infinitely, leading to chaos
    }
  }
}

// Bad: Column that can contain itself
{
  "name": "column",
  "is_nestable": true,
  "schema": {
    "content": {
      "type": "bloks"
      // Allows column inside column inside column...
    }
  }
}
```

**Correct (controlled nesting):**

```json
// Good: Page with section-level components only
{
  "name": "page",
  "is_root": true,
  "schema": {
    "body": {
      "type": "bloks",
      "restrict_components": true,
      "component_whitelist": [
        "hero_section",
        "content_section",
        "feature_grid",
        "testimonials_section",
        "cta_section"
      ],
      "description": "Add page sections in order"
    }
  }
}

// Good: Grid with controlled items
{
  "name": "grid_section",
  "is_nestable": true,
  "schema": {
    "columns": {
      "type": "option",
      "options": [
        { "name": "2 Columns", "value": "2" },
        { "name": "3 Columns", "value": "3" },
        { "name": "4 Columns", "value": "4" }
      ],
      "default_value": "3"
    },
    "items": {
      "type": "bloks",
      "restrict_components": true,
      "component_whitelist": ["grid_item"],
      "minimum": 2,
      "maximum": 12
    }
  }
}

// Good: Grid item with atomic content only
{
  "name": "grid_item",
  "is_nestable": true,
  "schema": {
    "icon": { "type": "asset", "filetypes": ["images"] },
    "title": { "type": "text", "required": true },
    "description": { "type": "textarea" },
    "link": { "type": "link" }
    // No nested blocks - atomic level
  }
}

// Good: Use component groups for organized restrictions
{
  "name": "content_area",
  "schema": {
    "blocks": {
      "type": "bloks",
      "restrict_components": true,
      "component_group_whitelist": ["content-blocks-group-uuid"]
    }
  }
}
```

**Nesting strategies:**

| Strategy | Use Case | Implementation |
|----------|----------|----------------|
| Whitelist | Page sections | `component_whitelist` array |
| Groups | Organized categories | `component_group_whitelist` with UUIDs |
| Tags | Flexible categorization | `component_tag_whitelist` |
| Max depth | Prevent infinite nesting | Define terminal components |
| Min/Max | Content requirements | `minimum` and `maximum` values |

**Best practices:**

1. Define clear nesting levels (page → section → element → atom)
2. Create terminal components that don't accept nested blocks
3. Use component groups to organize related components
4. Set reasonable minimum/maximum limits
5. Document nesting rules for editors

Reference: [Blocks Field](https://www.storyblok.com/docs/api/management/components/possible-field-types#blocks)
