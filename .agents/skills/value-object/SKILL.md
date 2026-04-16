---
name: value-object
description: |
  Generate or refactor TypeScript value objects. Use when asked to: create a value object, make an immutable domain type, wrap a primitive with validation, add raw DTO conversion, implement toRaw/fromRaw helpers, generate mapper files for persistence or transport. Triggers on: "value object", "immutable wrapper", "scalar wrapper", "domain primitive", "money type", "email type", "toRaw", "fromRaw", IFoo/FooRaw naming patterns, mapper files, "add validation to", "retrofit create factory".
argument-hint: 'Name and fields of the value object (e.g. "EmailAddress wrapping a string", "Money with amount and currency")'
---

# Value Object Skill

Generates or refactors **immutable TypeScript value objects** — domain primitives that encapsulate validation, normalization, and conversion logic.

## Decision: what to generate

| Request | Output |
|---|---|
| Single primitive (email, UUID, phone, color…) | Interface + scalar wrapper class |
| Composite (address, money, date range…) | Interface + composite class accepting `IFoo` raw shape |
| Mentions persistence or transport layer | Also generate `mapper/FooMapper.ts` |
| Improving/retrofitting existing code | Add missing factory + `toRaw`/`toJSON` without renaming |

## File layout

```
<package>/
├── value_object/
│   ├── IFoo.ts          # Interface / raw shape
│   └── impl/
│       └── Foo.ts       # Immutable implementation
└── mapper/
    └── FooMapper.ts     # Only when persistence / transport is involved
```

Use relative imports. Never use project-specific import aliases (`@alias/`, `~pkg/`).

## Core rules — always apply

- `private constructor` — creation only via factory
- `public static create(raw): T` — validate, normalize, throw `new Error("…")` on invalid
- `public readonly` on every field — no mutation after construction
- `toRaw()` — returns the primitive or a plain object; inverse of `create()`
- `toJSON()` / `toDto()` — returns the interface shape for serialization

See [./references/value-object-templates.md](./references/value-object-templates.md) for concrete implementations.

## Scalar wrapper

- Constructor accepts a single primitive (`string`, `number`)
- `toRaw()` returns that primitive directly
- Interface has a single named field: `{ value: string }`

## Composite value object

- Constructor accepts the full `IFoo` shape
- `create(raw: IFoo)` validates required fields; normalizes strings with `.trim()`
- `toRaw()` returns a plain object matching `IFoo`

## Mapper (persistence / transport only)

- Separate class: `FooMapper.fromRaw(raw) → Foo`, `FooMapper.toRaw(foo) → RawType`
- Do **not** put database or transport concerns inside the value object itself

## Validation

- `null` / `undefined` input → throw, do not silently produce a broken object
- Normalize in the factory (`.trim()`, `.toLowerCase()`) before storing
- Throw `new Error("descriptive message")` — keep it simple, no custom error classes unless asked

## Special cases

| Case | Key notes |
|---|---|
| Email | Validate `@` presence; normalize to lowercase; `toRaw()` returns string |
| Phone | Decide in factory: strip non-digits or keep formatted |
| UUID | Validate format with regex; do not generate inside the value object |
| Password hash | Store hash only; no plain-text field; `toRaw()` must not accidentally expose the hash |
| Money / Currency | `amount` as integer cents + `currency` as ISO string; never use floats |
| Date range | Validate `start < end`; expose computed helpers (`duration()`, `contains(d)`) if useful |
| Color | Validate hex or RGB; normalize to one canonical format |
| Nullable wrapping | Accept `null` in `fromRaw()`; return `null` from `toRaw()` if value is absent |

## If improving existing code

1. Keep existing names (`IEmailAddress`, `EmailAddress`, `EmailAddressRaw`, etc.)
2. Add missing `create()` / `fromRaw()` factory with validation
3. Make constructor `private` if it is not already
4. Add `toRaw()` / `toJSON()` if absent
5. Do not restructure unrelated logic or rename symbols

## Output style

- Modern TypeScript; `.ts` file extensions in imports
- `export default` for the implementation class
- Keep generated code short and readable — one responsibility per file
