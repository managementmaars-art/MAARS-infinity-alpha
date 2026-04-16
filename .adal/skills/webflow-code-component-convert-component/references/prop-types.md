# Webflow Prop Types Quick Reference

Quick reference for all 11 Webflow code component prop types via `props.<Type>()` from `@webflow/data-types`.

## Quick Reference Table

| Type       | Alias    | Return Type | Has defaultValue | Unique Params                    |
|------------|----------|-------------|------------------|----------------------------------|
| Text       | String   | `string`    | Yes              | —                                |
| RichText   | —        | `ReactNode` | Yes              | —                                |
| TextNode   | —        | `ReactNode` | Yes              | `multiline`                      |
| Link       | —        | `object`    | No               | —                                |
| Image      | —        | `object`    | No               | —                                |
| Number     | —        | `number`    | Yes              | `min`, `max`, `decimals`         |
| Boolean    | —        | `boolean`   | Yes              | `trueLabel`, `falseLabel`        |
| Variant    | —        | `string`    | Yes              | `options` (required)             |
| Visibility | —        | `boolean`   | Yes              | —                                |
| Slot       | Children | `ReactNode` | No               | —                                |
| ID         | —        | `string`    | No               | —                                |

## Type Signatures

### Text (alias: String)

```tsx
props.Text({ name, group?, tooltip?, defaultValue?: string })
// Returns: string
```

### RichText

```tsx
props.RichText({ name, group?, tooltip?, defaultValue?: string })
// Returns: ReactNode
```

### TextNode

```tsx
props.TextNode({ name, group?, tooltip?, defaultValue?: string, multiline?: boolean })
// Returns: ReactNode
```

- Editable directly on the Webflow canvas

### Link

```tsx
props.Link({ name, group?, tooltip? })
// Returns: { href: string, target?: "_self" | "_blank" | string, preload?: "prerender" | "prefetch" | "none" | string }
```

- No `defaultValue` param
- Returns an object — may need a wrapper if component expects `href` and `target` separately

### Image

```tsx
props.Image({ name, group?, tooltip? })
// Returns: { src: string, alt?: string }
```

- No `defaultValue` param
- Returns an object — may need a wrapper if component expects `src` and `alt` separately

### Number

```tsx
props.Number({ name, group?, tooltip?, defaultValue?: number, min?: number, max?: number, decimals?: number })
// Returns: number
```

### Boolean

```tsx
props.Boolean({ name, group?, tooltip?, defaultValue?: boolean, trueLabel?: string, falseLabel?: string })
// Returns: boolean
```

### Variant

```tsx
props.Variant({ name, options: string[], group?, tooltip?, defaultValue?: string })
// Returns: string
```

- `options` is **required**
- `defaultValue` must match one of the options

### Visibility

```tsx
props.Visibility({ name, group?, tooltip?, defaultValue?: boolean })
// Returns: boolean
```

### Slot (alias: Children)

```tsx
props.Slot({ name, group?, tooltip? })
// Returns: ReactNode
```

- No `defaultValue` param
- Allows designers to insert child components

### ID

```tsx
props.Id({ name, group?, tooltip? })
// Returns: string
```

- No `defaultValue` param
- Used for HTML element IDs (CSS targeting, form labels, JS interactions)

## Common Params

All types share: `name` (required), `group` (optional), `tooltip` (optional)
